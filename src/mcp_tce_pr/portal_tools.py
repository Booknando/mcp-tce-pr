"""Ferramentas gerais: todas as áreas públicas podem ser navegadas por URL."""

import re
from typing import Literal

from .client import SourceError
from .portal import AREAS, query_form, read_page, search, window


def listar_areas_portal_pr() -> dict:
    """Lista pontos de entrada de todo o portal; siga links para descobrir outras áreas e sistemas."""
    return {
        "areas": AREAS,
        "modo": "Leitura pública por URL, documentos e navegação dinâmica opcional.",
        "limites": "Sem acesso autenticado, envio de petições ou garantia de extração integral de painéis.",
    }


async def ler_pagina_portal_pr(
    url: str,
    renderizar: bool = False,
    deslocamento: int = 0,
    limite: int = 20000,
    inicio_links: int = 0,
) -> dict:
    """Lê qualquer página pública TCE-PR: texto, links, iframes e campos de formulários.

    renderizar=True usa Chromium isolado para JavaScript/Power BI (extra navegador).
    Paginação textual por deslocamento; links por inicio_links, lotes de 100.
    Siga links de tipo iframe para sistemas incorporados. Documentos usam ler_documento_pr.
    """
    return window(await read_page(url, renderizar), deslocamento, limite, inicio_links)


async def buscar_no_portal_pr(texto: str, area: str = "inicio", max_paginas: int = 10) -> dict:
    """Busca texto navegando até 30 páginas de uma área. Expõe páginas visitadas e falhas; não é busca exaustiva."""
    return await search(texto, area, max_paginas)


async def consultar_formulario_pr(url: str, campos: dict[str, str], indice: int = 0) -> dict:
    """Consulta formulários públicos cadastrados de processos/sanções/inadimplentes.

    Primeiro leia a página para obter nomes reais dos campos, valores de opções e botão
    de pesquisa. Preserva cookies e campos ocultos ASP.NET; não aceita campos ocultos do agente.
    Não serve para login, requerimentos, peticionamento ou envio de dados de fiscalizados.
    """
    return window(await query_form(url, campos, indice))


async def consultar_processo_pr(numero: str) -> dict:
    """Consulta pública por número de protocolo, ex. 196886/26. Retorna a página de resposta e links."""
    if not re.fullmatch(r"\d{1,9}/(?:\d{2}|\d{4})", numero):
        raise SourceError("Use número/ano: 196886/26.")
    page = await read_page(AREAS["processos"])
    for form in page["formularios"]:
        inputs = form["campos"]
        number = next((c["nome"] for c in inputs if c["nome"].endswith("$tbnrProcesso")), None)
        button = next((c["nome"] for c in inputs if c["nome"].endswith("$btnProtocolo")), None)
        if number and button:
            return window(
                await query_form(AREAS["processos"], {number: numero, button: "OK"}, form["indice"])
            )
    raise SourceError("Formulário processual mudou; consulte a página original.")


async def ler_novo_mural_pr(
    secao: Literal[
        "Visão geral", "Detalhamento de licitação", "Itens de licitação", "Dados abertos"
    ] = "Visão geral",
    deslocamento: int = 0,
    inicio_links: int = 0,
) -> dict:
    """Lê o novo Mural de editais a partir de 01/05/2026, descobrindo o link no portal.

    Navega às seções públicas do Power BI com navegador isolado. Retorna texto e links
    da seção, não todos os registros do modelo. 'Dados abertos' procura fontes exportáveis.
    """
    from .render import render_page

    home = await read_page(AREAS["inicio"])
    url = next(
        (
            l["url"]
            for l in home["links"]
            if "01/05/2026" in l["titulo"] and "app.powerbi.com/" in l["url"]
        ),
        None,
    )
    if url is None:
        raise SourceError("Link do novo Mural não encontrado no portal; a navegação mudou.")
    return window(await render_page(url, secao), deslocamento, link_offset=inicio_links)


async def consultar_novo_mural_pr(
    ano: int,
    tipo: Literal["licitacoes", "itens"] = "licitacoes",
    filtros: dict[str, str] | None = None,
    cursor: int = 0,
    limite: int = 20,
) -> dict:
    """Consulta CSV oficial do NOVO Mural, editais a partir de 01/05/2026.

    Descobre o ZIP na seção Dados abertos do Power BI e lê os registros por HTTP Range.
    tipo='itens' consulta mapa de itens; tipo='licitacoes' consulta os certames.
    Primeiro consulte sem filtros para descobrir os campos. Filtros são substrings sem
    acentos combinadas por E. cursor é o número de registros já examinados, não página.
    Requer extra navegador para descobrir a fonte. Não mescla o CSV tradicional.
    """
    from urllib.parse import urlsplit

    from .archives import consultar_csv_zip_pr, listar_arquivos_zip_pr

    if not 2026 <= ano <= 2100:
        raise SourceError("Ano inválido para o novo Mural.")
    page = await ler_novo_mural_pr("Dados abertos")
    prefix = "licitacao_municipal_mapa_item" if tipo == "itens" else "licitacao_municipal"
    wanted = f"{prefix}_{ano}_csv.zip"
    url = next(
        (l["url"] for l in page["links"] if urlsplit(l["url"]).path.endswith("/" + wanted)), None
    )
    if url is None:
        raise SourceError("Exportação anual não encontrada na seção publicada de dados abertos.")
    index = await listar_arquivos_zip_pr(url)
    member = next((i["nome"] for i in index["arquivos"] if i["nome"].endswith(".csv")), None)
    if not member:
        raise SourceError("CSV não encontrado no ZIP publicado.")
    result = await consultar_csv_zip_pr(url, member, filtros, cursor, limite)
    return {
        **result,
        "cobertura": "Novo módulo do Mural: editais a partir de 01/05/2026; dados exportados até o dia anterior, conforme painel.",
    }
