"""Consulta aos XMLs municipais publicados dentro do ZIP consolidado PIT."""

import asyncio
import io
import re
import zipfile

from defusedxml.ElementTree import iterparse

from .archives import RemoteZip, listar_downloads_pit_pr
from .client import SourceError, normalize
from .portal import provenance

TEMAS = (
    "Combustivel",
    "Contrato",
    "Convenio",
    "Despesa",
    "Diarias",
    "Licitacao",
    "Obra",
    "Receita",
    "Relacionamentos",
)


def query_xml(data: bytes, filters: dict, offset: int, limit: int) -> dict:
    rows, fields, matches, count = [], set(), 0, 0
    # PIT publica registros como atributos dos elementos filhos de root.
    for _, element in iterparse(
        io.BytesIO(data), events=("end",), forbid_dtd=True, forbid_entities=True
    ):
        if element.attrib:
            row = dict(element.attrib)
            fields.update(row)
            count += 1
            if all(normalize(v) in normalize(row.get(k, "")) for k, v in filters.items()):
                if offset <= matches < offset + limit:
                    rows.append(row)
                matches += 1
        element.clear()
    if set(filters) - fields and count:
        raise SourceError(
            f"Filtros desconhecidos: {sorted(set(filters) - fields)}. Campos: {sorted(fields)}"
        )
    return {
        "registros": rows,
        "campos": sorted(fields),
        "total_registros": count,
        "total_encontrado": matches,
        "proximo_deslocamento": offset + limit if offset + limit < matches else None,
    }


def query_pit(url, year, municipality, theme, filename, filters, offset, limit):
    with RemoteZip(url) as remote, zipfile.ZipFile(remote) as outer:
        wanted = f"{year}_{municipality}_{theme}.zip"
        try:
            member = outer.getinfo(wanted)
        except KeyError as e:
            raise SourceError(
                "Município/tema não publicado. Use listar_arquivos_zip_pr para descobrir os códigos."
            ) from e
        if member.file_size > 32 * 1024**2:
            raise SourceError(
                "Pacote municipal acima de 32 MiB; use o download original para análise integral."
            )
        with zipfile.ZipFile(io.BytesIO(outer.read(member))) as inner:
            names = [{"nome": i.filename, "bytes": i.file_size} for i in inner.infolist()]
            if filename is None:
                return {
                    "arquivos": names,
                    "pacote_municipal": wanted,
                    "bytes_baixados": remote.downloaded,
                    **provenance(url, remote.headers),
                }
            try:
                item = inner.getinfo(filename)
            except KeyError as e:
                raise SourceError(
                    "XML não encontrado; chame sem arquivo para listar as opções."
                ) from e
            if (
                not filename.lower().endswith(".xml")
                or item.file_size > 64 * 1024**2
                or item.flag_bits & 1
            ):
                raise SourceError("Somente XML não criptografado de até 64 MiB.")
            result = query_xml(inner.read(item), filters, offset, limit)
            return {
                **result,
                "pacote_municipal": wanted,
                "arquivo": filename,
                "bytes_baixados": remote.downloaded,
                **provenance(url, remote.headers),
                "atualizacao": "PIT: remessas fechadas, publicação semanal declarada; confira dtEnvio/nrMesProcessamento e Last-Modified.",
            }


async def consultar_dados_pit_pr(
    ano: int,
    codigo_municipio: str,
    tema: str,
    arquivo: str | None = None,
    filtros: dict[str, str] | None = None,
    deslocamento: int = 0,
    limite: int = 20,
) -> dict:
    """Consulta receitas, despesas, contratos, convênios, licitações, obras, diárias e combustível do PIT.

    Descubra codigo_municipio nos nomes de listar_arquivos_zip_pr (ex. 410010).
    Temas: Combustivel, Contrato, Convenio, Despesa, Diarias, Licitacao, Obra, Receita,
    Relacionamentos. Primeiro omita arquivo para listar os XMLs internos; depois forneça
    seu nome exato. Filtros: nomes de atributos XML, substrings sem acentos combinadas por E.
    Não baixa o ZIP anual inteiro. Pagina registros encontrados; retorna total e procedência.
    """
    if (
        not 1900 <= ano <= 2100
        or not re.fullmatch(r"\d{6,7}", codigo_municipio)
        or tema not in TEMAS
    ):
        raise SourceError(f"Ano/código/tema inválido. Temas: {TEMAS}")
    if deslocamento < 0 or not 1 <= limite <= 100:
        raise SourceError("Paginação inválida.")
    sources = await listar_downloads_pit_pr(ano)
    if not sources["arquivos"]:
        raise SourceError("Ano não publicado no PIT consolidado.")
    return await asyncio.to_thread(
        query_pit,
        sources["arquivos"][0]["url"],
        ano,
        codigo_municipio,
        tema,
        arquivo,
        filtros or {},
        deslocamento,
        limite,
    )
