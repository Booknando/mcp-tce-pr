"""Consulta real opcional: não imprime dados individuais dos registros."""

import asyncio
import json

from mcp_tce_pr.tools import consultar_base_pr, listar_bases_pr


async def main():
    sources = await listar_bases_pr()
    print(json.dumps({"bases_publicadas": len(sources)}, ensure_ascii=False))
    for base in (
        "licitacoes",
        "obras",
        "acordaos",
        "acompanhamentos",
        "responsaveis_tecnicos",
        "bens_patrimoniais",
    ):
        years = [s["ano"] for s in sources if s["base"] == base and s["ano"]]
        result = await consultar_base_pr(base, max(years) if years else None, limite=1)
        assert result["registros"], base
        print(
            json.dumps(
                {
                    "base": base,
                    "total": result["total_encontrado"],
                    "campos": result["campos"],
                    "linhas_invalidas": result["linhas_invalidas_ignoradas"],
                    "fonte": result["fonte"],
                    "ultima_modificacao_http": result["ultima_modificacao_http"],
                    "obtido_em": result["obtido_em"],
                },
                ensure_ascii=False,
            )
        )


asyncio.run(main())
