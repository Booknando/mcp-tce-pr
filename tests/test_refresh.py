import pytest
import respx
from fastmcp import Client

from mcp_tce_pr.client import SourceError, TCEClient
from mcp_tce_pr.constants import CATALOG
from mcp_tce_pr.server import mcp


@respx.mock
async def test_forced_refresh_through_mcp(monkeypatch):
    client = TCEClient()
    monkeypatch.setattr("mcp_tce_pr.tools.client", client)
    url = "https://servicos.tce.pr.gov.br/obras_municipais_base_de_dados.csv"
    catalog = respx.get(CATALOG).respond(200, text=f'<a href="{url}">Obras</a>')
    download = respx.get(url).respond(200, content=b"nome;valor\nantigo;1\n")
    async with Client(mcp) as session:
        await session.call_tool("descrever_base_pr", {"base": "obras"})
        download.respond(200, content=b"nome;valor\nnovo;2\n")
        cached = await session.call_tool("descrever_base_pr", {"base": "obras"})
        assert cached.data["registros"][0]["nome"] == "antigo"
        fresh = await session.call_tool("atualizar_dados_pr", {"base": "obras"})
        assert fresh.data["registros"][0]["nome"] == "novo"
        assert fresh.data["cache"] is False
        assert catalog.call_count == download.call_count == 2
        after = await session.call_tool("descrever_base_pr", {"base": "obras"})
        assert after.data["cache"] is True
        assert after.data["registros"][0]["nome"] == "novo"


@respx.mock
async def test_refresh_failure_is_not_stale_success():
    client = TCEClient()
    route = respx.get(CATALOG).respond(200, content=b"old")
    await client.fetch(CATALOG)
    route.respond(503)
    with pytest.raises(SourceError):
        await client.fetch(CATALOG, force=True)


@respx.mock
async def test_ttl_and_disabled_cache(monkeypatch):
    monkeypatch.setenv("MCP_TCE_CACHE_SECONDS", "10")
    client = TCEClient()
    route = respx.get(CATALOG).respond(200, content=b"a")
    await client.fetch(CATALOG)
    timestamp, body, metadata = client.cache[CATALOG]
    client.cache[CATALOG] = (timestamp - 11, body, metadata)
    await client.fetch(CATALOG)
    assert route.call_count == 2
    monkeypatch.setenv("MCP_TCE_CACHE_SECONDS", "0")
    client = TCEClient()
    await client.fetch(CATALOG)
    await client.fetch(CATALOG)
    assert route.call_count == 4


@pytest.mark.parametrize("value", ["-1", "86401", "abc", "1.5"])
def test_invalid_cache_configuration(monkeypatch, value):
    monkeypatch.setenv("MCP_TCE_CACHE_SECONDS", value)
    with pytest.raises(ValueError, match="MCP_TCE_CACHE_SECONDS"):
        TCEClient()
