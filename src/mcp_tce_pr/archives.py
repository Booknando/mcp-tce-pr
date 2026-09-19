"""ZIP remoto seekable: central directory e membros por HTTP Range, sem extração em disco."""

import asyncio
import csv
import io
import re
import zipfile
from urllib.parse import urlsplit

import httpx

from .client import SourceError, normalize
from .portal import AREAS, provenance, public_url, read_page


class RemoteZip(io.RawIOBase):
    def __init__(self, url: str):
        self.url = public_url(url)
        self.http = httpx.Client(timeout=30, follow_redirects=False)
        self.pos = 0
        self.downloaded = 0
        try:
            r = self.http.head(self.url)
            r.raise_for_status()
            self.size = int(r.headers.get("content-length", 0))
            self.etag = r.headers.get("etag")
            self.headers = dict(r.headers)
            if not 0 < self.size <= 10 * 1024**3:
                raise SourceError("ZIP sem tamanho conhecido ou acima de 10 GiB.")
        except Exception:
            self.http.close()
            raise

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        if not 0 <= pos <= self.size:
            raise SourceError("Posição inválida no ZIP.")
        self.pos = pos
        return pos

    def read(self, size=-1):
        size = min(self.size - self.pos, self.size if size < 0 else size)
        if not size:
            return b""
        if size > 16 * 1024**2 or self.downloaded + size > 64 * 1024**2:
            raise SourceError("Leitura ZIP excede orçamento: 16 MiB por faixa, 64 MiB por chamada.")
        end = self.pos + size - 1
        headers = {"Range": f"bytes={self.pos}-{end}", "Accept-Encoding": "identity"}
        if self.etag:
            headers["If-Match"] = self.etag
        with self.http.stream("GET", self.url, headers=headers) as r:
            expected = f"bytes {self.pos}-{end}/{self.size}"
            if r.status_code != 206 or r.headers.get("content-range") != expected:
                raise SourceError(
                    "A fonte não honrou HTTP Range ou o ZIP mudou; download integral recusado."
                )
            if self.etag and r.headers.get("etag") not in (None, self.etag):
                raise SourceError("ZIP alterado durante a consulta.")
            parts, received = [], 0
            for chunk in r.iter_bytes():
                received += len(chunk)
                if received > size:
                    raise SourceError("Resposta Range maior que a faixa solicitada.")
                parts.append(chunk)
            if received != size:
                raise SourceError("Resposta Range incompleta.")
        self.pos += size
        self.downloaded += size
        return b"".join(parts)

    def close(self):
        self.http.close()
        super().close()


def list_zip(url, offset, limit):
    with RemoteZip(url) as remote, zipfile.ZipFile(remote) as archive:
        members = archive.infolist()
        return {
            "arquivos": [
                {
                    "nome": i.filename,
                    "bytes": i.file_size,
                    "bytes_comprimidos": i.compress_size,
                    "pasta": i.is_dir(),
                }
                for i in members[offset : offset + limit]
            ],
            "total_arquivos": len(members),
            "bytes_zip": remote.size,
            "bytes_baixados": remote.downloaded,
            "proximo_deslocamento": offset + limit if offset + limit < len(members) else None,
            **provenance(url, remote.headers),
        }


def query_zip(url, member, filters, offset, limit, encoding):
    with RemoteZip(url) as remote, zipfile.ZipFile(remote) as archive:
        try:
            info = archive.getinfo(member)
        except KeyError as e:
            raise SourceError("Membro não encontrado; liste os arquivos do ZIP.") from e
        if not member.lower().endswith((".csv", ".txt")) or info.flag_bits & 1:
            raise SourceError("Somente CSV/TXT não criptografado.")
        if info.file_size > 4 * 1024**3:
            raise SourceError("Membro excede 4 GiB.")
        with (
            archive.open(info) as raw,
            io.TextIOWrapper(raw, encoding=encoding, newline="") as stream,
        ):
            first = stream.readline()
            sep = max((";", "\t", "|", ","), key=first.count)
            fields = next(csv.reader([first], delimiter=sep))
            if len(fields) < 2 or len(set(fields)) != len(fields) or set(filters) - set(fields):
                raise SourceError(f"Cabeçalho/filtros inválidos. Campos: {fields}")
            reader = csv.DictReader(stream, fieldnames=fields, delimiter=sep)
            rows, scanned, bad, decoded_size, complete = [], 0, 0, len(first), True
            # Cursor é a posição de registros examinados, não o número de correspondências.
            for row in reader:
                scanned += 1
                decoded_size += sum(len(str(v)) for v in row.values())
                if scanned > offset:
                    if None in row or any(v is None for v in row.values()):
                        bad += 1
                    elif all(normalize(v) in normalize(row[k]) for k, v in filters.items()):
                        rows.append(row)
                if len(rows) >= limit or decoded_size > 32 * 1024**2 or scanned >= offset + 100000:
                    if scanned <= offset:
                        raise SourceError(
                            "Cursor além do orçamento de leitura; use o arquivo original."
                        )
                    complete = False
                    break
        return {
            "registros": rows,
            "campos": fields,
            "registros_examinados": scanned,
            "linhas_invalidas": bad,
            "fim_do_arquivo": complete,
            "proximo_cursor": None if complete else scanned,
            "bytes_baixados": remote.downloaded,
            "membro": member,
            "limites": "Sem total global. Até 100 mil registros novos / 32 MiB de texto por chamada; "
            "cursor exige releitura desde o início. Para análise integral, baixe a fonte externamente.",
            **provenance(url, remote.headers),
        }


async def listar_downloads_pit_pr(ano: int | None = None) -> dict:
    """Descobre ZIPs anuais consolidados do PIT pelos links publicados; não baixa os pacotes."""
    page = await read_page(AREAS["pit_consolidado"])
    links = [l for l in page["links"] if urlsplit(l["url"]).path.lower().endswith(".zip")]
    if ano is not None:
        links = [l for l in links if re.search(rf"(?:^|/)({ano})_", urlsplit(l["url"]).path)]
    return {
        "arquivos": links,
        **provenance(AREAS["pit_consolidado"]),
        "proximo_passo": "Use listar_arquivos_zip_pr e consultar_dados_pit_pr para os ZIPs/XMLs municipais.",
    }


async def listar_arquivos_zip_pr(url: str, deslocamento: int = 0, limite: int = 100) -> dict:
    """Lista membros de ZIP público remoto com HTTP Range, sem baixar o pacote inteiro."""
    if deslocamento < 0 or not 1 <= limite <= 200:
        raise SourceError("Paginação inválida.")
    return await asyncio.to_thread(list_zip, url, deslocamento, limite)


async def consultar_csv_zip_pr(
    url: str,
    arquivo: str,
    filtros: dict[str, str] | None = None,
    cursor: int = 0,
    limite: int = 20,
    encoding: str = "utf-8-sig",
) -> dict:
    """Consulta um CSV/TXT diretamente dentro de ZIP por faixas HTTP.

    Primeiro liste os membros e consulte sem filtros para descobrir campos. Filtros são
    substrings sem acentos, combinados por E. cursor é o número de registros já examinados.
    Encoding pode ser utf-8-sig, cp1252 ou latin-1. Não extrai arquivos no disco.
    Para o PIT consolidado, que contém ZIPs/XMLs aninhados, use consultar_dados_pit_pr.
    """
    if (
        cursor < 0
        or cursor > 1000000
        or not 1 <= limite <= 100
        or encoding not in ("utf-8-sig", "cp1252", "latin-1")
    ):
        raise SourceError("Parâmetros inválidos.")
    return await asyncio.to_thread(query_zip, url, arquivo, filtros or {}, cursor, limite, encoding)
