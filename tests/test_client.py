import json

import httpx
import pytest
import respx
from fastmcp import Client
from pydantic import ValidationError

from mcp_tce_pr.client import SourceError, TCEClient, discover, parse_csv, validate_url
from mcp_tce_pr.constants import ACORDAOS, CATALOG
from mcp_tce_pr.schemas import Consulta
from mcp_tce_pr.server import mcp

CSV = (
    "nmMunicipio;dsObjeto;valor\r\r\n"
    "-----------;--------;-----\r\r\n"
    '"Curitiba";"Saúde; escola\nsegunda linha";"1.25"\r\r\n'
    '"CURITIBA";"Saúde pública";"2.50"\r\r\n'
    '"Londrina";"Estrada";"3.00"\r\r\n'
).encode("utf-8-sig")


def test_csv_accents_pagination_multiline_and_separator():
    result = parse_csv(
        CSV, Consulta(base="obras", texto="saude", limite=1, filtros={"nmMunicipio": "curitiba"})
    )
    assert result["total_encontrado"] == 2
    assert result["proximo_deslocamento"] == 1
    assert result["registros"][0]["dsObjeto"] == "Saúde; escola\nsegunda linha"
    assert result["registros"][0]["valor"] == "1.25"
    second = parse_csv(CSV, Consulta(base="obras", texto="saude", limite=1, deslocamento=1))
    assert second["registros"][0]["valor"] == "2.50"
    assert second["proximo_deslocamento"] is None


def test_cp1252_and_bad_rows():
    data = "nome;valor\nSão José;1\nquebrado\nextra;1;2\n".encode("cp1252")
    result = parse_csv(data, Consulta(base="obras", texto="sao jose"))
    assert result["total_encontrado"] == 1
    assert result["linhas_invalidas_ignoradas"] == 2


def test_invalid_schema_and_filter():
    with pytest.raises(SourceError):
        parse_csv(b"<html>error</html>", Consulta(base="obras"))
    with pytest.raises(SourceError, match="Campos desconhecidos"):
        parse_csv(CSV, Consulta(base="obras", filtros={"wrong": "x"}))
    with pytest.raises(ValidationError):
        Consulta(base="obras", limite=101)


@pytest.mark.parametrize(
    "url",
    [
        "http://viajuris.tce.pr.gov.br/a",
        "https://evil.com/",
        "https://viajuris.tce.pr.gov.br.evil.com/",
        "https://user@viajuris.tce.pr.gov.br/",
        "https://viajuris.tce.pr.gov.br:123/a",
    ],
)
def test_url_restrictions(url):
    with pytest.raises(SourceError):
        validate_url(url)


def test_discovery():
    html = b'<a href="/DadosAbertos/DadosAbertos/DownloadArquivo?nomeArquivo=2026_acordaos_base_de_dados.csv">CSV</a><a href="https://evil.com/2025_acordaos_base_de_dados.csv">bad</a>'
    sources = discover(html, ACORDAOS)
    assert len(sources) == 1
    assert sources[0].ano == 2026
    assert sources[0].url.startswith("https://viajuris.tce.pr.gov.br/")
    with pytest.raises(SourceError):
        discover(b"<html>changed</html>", CATALOG)


@respx.mock
async def test_http_cache_and_error():
    route = respx.get(CATALOG).mock(return_value=httpx.Response(200, content=b"test"))
    client = TCEClient()
    _, first = await client.fetch(CATALOG)
    _, second = await client.fetch(CATALOG)
    assert not first["cache"] and second["cache"]
    assert route.call_count == 1
    respx.get(ACORDAOS).mock(return_value=httpx.Response(503))
    with pytest.raises(SourceError, match="HTTPStatusError"):
        await client.fetch(ACORDAOS)


@respx.mock
async def test_cache_budget_and_expiration(monkeypatch):
    monkeypatch.setattr("mcp_tce_pr.client.MAX_CACHE_BYTES", 5)
    first_route = respx.get(CATALOG).mock(return_value=httpx.Response(200, content=b"123"))
    respx.get(ACORDAOS).mock(return_value=httpx.Response(200, content=b"456"))
    client = TCEClient()
    await client.fetch(CATALOG)
    await client.fetch(ACORDAOS)
    assert CATALOG not in client.cache
    await client.fetch(CATALOG)
    assert first_route.call_count == 2
    client.cache_seconds = 0
    await client.fetch(CATALOG)
    assert first_route.call_count == 3


@respx.mock
async def test_redirect_blocked_and_size_limit(monkeypatch):
    respx.get(CATALOG).mock(
        return_value=httpx.Response(302, headers={"location": "https://evil.com"})
    )
    with pytest.raises(SourceError, match="permitidas"):
        await TCEClient().fetch(CATALOG)
    monkeypatch.setattr("mcp_tce_pr.client.MAX_BYTES", 3)
    respx.get(CATALOG).mock(return_value=httpx.Response(200, content=b"1234"))
    with pytest.raises(SourceError, match="128 MiB"):
        await TCEClient().fetch(CATALOG)


@respx.mock
async def test_query_and_mcp_protocol(monkeypatch):
    client = TCEClient()
    monkeypatch.setattr("mcp_tce_pr.tools.client", client)
    csv_url = "https://servicos.tce.pr.gov.br/obras_municipais_base_de_dados.csv"
    respx.get(CATALOG).mock(return_value=httpx.Response(200, text=f'<a href="{csv_url}">Obras</a>'))
    respx.get(csv_url).mock(return_value=httpx.Response(200, content=CSV))
    async with Client(mcp) as session:
        assert len(await session.list_tools()) == 19
        assert len(await session.list_resources()) == 1
        assert len(await session.list_prompts()) == 1
        result = await session.call_tool(
            "consultar_obras_pr", {"municipio": "curitiba", "limite": 1}
        )
        data = json.loads(result.content[0].text)
        assert data["total_encontrado"] == 2
        assert data["fonte"]["url"] == csv_url
        assert data["obtido_em"]
    with pytest.raises(SourceError, match="não são anuais"):
        await client.query(Consulta(base="obras", ano=2026))
