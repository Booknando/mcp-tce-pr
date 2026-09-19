import io
import json
import zipfile

import httpx
import pytest
import respx
from fastmcp import Client
from openpyxl import Workbook
from pypdf import PdfWriter

from mcp_tce_pr.archives import list_zip, query_zip
from mcp_tce_pr.client import SourceError
from mcp_tce_pr.documents import extract
from mcp_tce_pr.portal import AREAS, parse_page, public_url, query_form, request, search, window
from mcp_tce_pr.server import mcp


@pytest.mark.parametrize(
    "url",
    [
        "http://www.tce.pr.gov.br/",
        "https://tce.pr.gov.br.evil.test/",
        "https://127.0.0.1/",
        "https://intranet.tce.pr.gov.br/",
        "https://www.tce.pr.gov.br/login/",
        "file:///etc/passwd",
        "https://app.powerbi.com/login",
        "https://user@www.tce.pr.gov.br/",
    ],
)
def test_public_url_rejects(url):
    with pytest.raises(SourceError):
        public_url(url)


def test_parse_navigation_forms_and_pagination():
    data = b"""<title>Test</title><script>ignore</script><a href="/a.pdf">PDF</a>
    <iframe src="https://pit.tce.pr.gov.br/Dados/"></iframe>
    <a href="https://example.com">External</a><form method="post">
    <input type="hidden" name="token" value="secret"><input name="q">
    <select name="year"><option value="2026">2026</option></select></form>"""
    page = parse_page(data, AREAS["inicio"])
    assert page["links"][0]["tipo"] == "arquivo"
    assert page["iframes"][0]["url"].startswith("https://pit.")
    assert not page["links"][2]["leitura_permitida"]
    assert "secret" not in json.dumps(page)
    assert "ignore" not in page["texto"]
    page["texto"] = "a" * 201
    assert window(page, limit=100)["proximo_deslocamento"] == 100
    assert parse_page('<a href="">Vazio</a>', AREAS["inicio"])["links"] == []


async def test_new_mural_selects_published_export(monkeypatch):
    from mcp_tce_pr.portal_tools import consultar_novo_mural_pr

    url = "https://pit.tce.pr.gov.br/arquivos/ie_exp/licitacao_municipal/licitacao_municipal_2026_csv.zip"

    async def page(*args, **kwargs):
        return {"links": [{"url": url}]}

    async def listing(*args, **kwargs):
        return {"arquivos": [{"nome": "licitacao_municipal_2026.csv"}]}

    async def query(given_url, member, filters, cursor, limit):
        assert given_url == url and member.endswith(".csv")
        assert filters == {"municipio": "Curitiba"}
        return {"registros": [{"municipio": "Curitiba"}], "fonte": url}

    monkeypatch.setattr("mcp_tce_pr.portal_tools.ler_novo_mural_pr", page)
    monkeypatch.setattr("mcp_tce_pr.archives.listar_arquivos_zip_pr", listing)
    monkeypatch.setattr("mcp_tce_pr.archives.consultar_csv_zip_pr", query)
    result = await consultar_novo_mural_pr(2026, filtros={"municipio": "Curitiba"})
    assert result["registros"][0]["municipio"] == "Curitiba"
    with pytest.raises(SourceError, match="não encontrada"):
        await consultar_novo_mural_pr(2027)


@respx.mock
async def test_redirect_boundaries_and_size():
    respx.get(AREAS["inicio"]).mock(
        return_value=httpx.Response(302, headers={"location": "https://evil.test"})
    )
    with pytest.raises(SourceError):
        await request(AREAS["inicio"])
    respx.get(AREAS["inicio"]).mock(return_value=httpx.Response(200, content=b"12345"))
    with pytest.raises(SourceError, match="excede"):
        await request(AREAS["inicio"], limit=4)


@respx.mock
async def test_form_preserves_state_but_rejects_hidden_override():
    url = AREAS["processos"]
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            text='<form method="post"><input type="hidden" name="__VIEWSTATE" value="a"><input name="query"><input name="button" type="submit" value="OK"></form>',
        )
    )
    route = respx.post(url).mock(return_value=httpx.Response(200, text="<p>Resultado</p>"))
    result = await query_form(url, {"query": "123/26", "button": "OK"}, 0)
    assert "Resultado" in result["texto"]
    assert b"__VIEWSTATE=a" in route.calls[0].request.content
    with pytest.raises(SourceError):
        await query_form(url, {"__VIEWSTATE": "bad"}, 0)
    with pytest.raises(SourceError):
        await query_form(AREAS["inicio"], {}, 0)


@respx.mock
async def test_search_reports_actual_scope():
    respx.get(AREAS["inicio"]).mock(
        return_value=httpx.Response(
            200,
            text='<html>saude<a href="/next">Próxima</a></html>',
            headers={"content-type": "text/html"},
        )
    )
    result = await search("saúde", "inicio", 1)
    assert len(result["resultados"]) == 1
    assert result["limite_atingido"]
    assert len(result["paginas_visitadas"]) == 1


def test_pdf_and_xlsx():
    out = io.BytesIO()
    pdf = PdfWriter()
    pdf.add_blank_page(width=72, height=72)
    pdf.add_blank_page(width=72, height=72)
    pdf.write(out)
    result = extract(out.getvalue(), "application/pdf", 1, 1)
    assert result["proxima_pagina"] == 2
    out = io.BytesIO()
    wb = Workbook()
    wb.active.append(["Nome", "Valor"])
    wb.active.append(["São José", 2])
    wb.save(out)
    result = extract(out.getvalue(), "application/octet-stream", 1, 1)
    assert "São José" in result["texto"]


def make_zip():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("dados.csv", "nome;valor\nSão José;1\nCuritiba;2\nCuritiba;3\n")
    return out.getvalue()


@respx.mock
def test_remote_zip_ranges_and_cursor():
    blob = make_zip()
    url = "https://pit.tce.pr.gov.br/Arquivos/test.zip"
    respx.head(url).mock(
        return_value=httpx.Response(200, headers={"content-length": str(len(blob)), "etag": '"x"'})
    )

    def range_response(req):
        start, end = map(int, req.headers["range"].split("=")[1].split("-"))
        return httpx.Response(
            206,
            content=blob[start : end + 1],
            headers={"content-range": f"bytes {start}-{end}/{len(blob)}", "etag": '"x"'},
        )

    respx.get(url).mock(side_effect=range_response)
    result = list_zip(url, 0, 10)
    assert result["arquivos"][0]["nome"] == "dados.csv"
    result = query_zip(url, "dados.csv", {"nome": "curitiba"}, 0, 1, "utf-8-sig")
    assert result["registros"][0]["valor"] == "2"
    assert result["proximo_cursor"] == 2
    result = query_zip(url, "dados.csv", {}, 2, 1, "utf-8-sig")
    assert result["registros"][0]["valor"] == "3"


@respx.mock
def test_remote_zip_refuses_full_download():
    blob = make_zip()
    url = "https://pit.tce.pr.gov.br/Arquivos/test.zip"
    respx.head(url).mock(
        return_value=httpx.Response(200, headers={"content-length": str(len(blob))})
    )
    respx.get(url).mock(return_value=httpx.Response(200, content=blob))
    with pytest.raises((SourceError, zipfile.BadZipFile)):
        list_zip(url, 0, 10)


async def test_new_tools_through_mcp():
    async with Client(mcp) as session:
        tools = {t.name for t in await session.list_tools()}
        assert {"ler_pagina_portal_pr", "consultar_processo_pr", "consultar_csv_zip_pr"} <= tools
        result = await session.call_tool("listar_areas_portal_pr", {})
        assert "diario" in json.loads(result.content[0].text)["areas"]
