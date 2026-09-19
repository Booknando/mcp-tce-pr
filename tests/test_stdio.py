import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def test_stdio_subprocess():
    transport = StdioTransport(command=sys.executable, args=["-m", "mcp_tce_pr.server"])
    async with Client(transport) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools} >= {
            "listar_bases_pr",
            "descrever_base_pr",
            "consultar_base_pr",
            "consultar_licitacoes_pr",
            "consultar_obras_pr",
            "consultar_acordaos_pr",
        }
        resources = await client.read_resource("tce-pr://fontes")
        assert "viajuris.tce.pr.gov.br" in resources[0].text
