"""Verificação pública por área; saída apenas de metadados, sem dados pessoais."""

import asyncio
import json

from mcp_tce_pr.archives import listar_arquivos_zip_pr, listar_downloads_pit_pr
from mcp_tce_pr.portal import AREAS, read_page
from mcp_tce_pr.portal_tools import consultar_processo_pr


async def main():
    sem = asyncio.Semaphore(3)

    async def check(name, url):
        async with sem:
            try:
                page = await read_page(url)
                result = {
                    "area": name,
                    "url": url,
                    "status": page["status"],
                    "caracteres": len(page["texto"]),
                    "links": len(page["links"]),
                    "formularios": len(page["formularios"]),
                }
            except (ValueError, OSError) as e:
                result = {"area": name, "erro": str(e)}
            print(json.dumps(result, ensure_ascii=False), flush=True)

    await asyncio.gather(*(check(k, v) for k, v in AREAS.items()))
    downloads = await listar_downloads_pit_pr(2026)
    print(json.dumps(downloads, ensure_ascii=False), flush=True)
    if downloads["arquivos"]:
        print(
            json.dumps(
                await listar_arquivos_zip_pr(downloads["arquivos"][0]["url"]), ensure_ascii=False
            ),
            flush=True,
        )
    result = await consultar_processo_pr("196886/26")
    print(
        json.dumps(
            {
                "processo": "196886/26",
                "fonte": result["fonte"],
                "caracteres": result["total_caracteres"],
                "links": result["total_links"],
                "numero_presente": "196886" in result["texto"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


asyncio.run(main())
