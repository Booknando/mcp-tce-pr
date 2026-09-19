"""Navegador isolado para leitura de conteúdo público gerado por JavaScript."""

import asyncio
import ipaddress
import os
import re
from urllib.parse import urlsplit

from .client import SourceError
from .portal import parse_page, provenance, public_url

_render_lock = asyncio.Lock()


async def render_page(url: str, section: str | None = None) -> dict:
    try:
        from playwright.async_api import Error as BrowserError
        from playwright.async_api import TimeoutError as BrowserTimeout
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise SourceError(
            "Instale o extra navegador: uv sync --extra navegador; uv run playwright install chromium"
        ) from e
    public_url(url)
    async with _render_lock, async_playwright() as pw:
        browser = None
        for channel in [os.environ.get("MCP_TCE_BROWSER_CHANNEL") or None, "msedge", "chrome"]:
            try:
                browser = await pw.chromium.launch(headless=True, channel=channel)
                break
            except BrowserError:
                continue
        if browser is None:
            raise SourceError(
                "Navegador não disponível. Execute uv run playwright install chromium."
            )
        try:
            context = await browser.new_context(accept_downloads=False, service_workers="block")
            # Perfil novo: sem credenciais, cookies do usuário, extensões ou arquivos locais.
            page = await context.new_page()

            async def guard(route):
                req = route.request
                host = urlsplit(req.url).hostname or ""
                private = host in ("localhost", "localhost.localdomain")
                try:
                    private = private or not ipaddress.ip_address(host).is_global
                except ValueError:
                    private = private or host.endswith((".localhost", ".local"))
                if private:
                    await route.abort()
                    return
                if req.is_navigation_request():
                    try:
                        public_url(req.url)
                    except (SourceError, ValueError):
                        await route.abort()
                        return
                if req.url.startswith(("file:", "ftp:")):
                    await route.abort()
                    return
                await route.continue_()

            await context.route("**/*", guard)
            async with asyncio.timeout(75):
                response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                warnings = []
                try:
                    await page.wait_for_load_state("networkidle", timeout=12000)
                except BrowserTimeout:
                    warnings.append(
                        "A página continuou carregando recursos; conteúdo pode estar parcial."
                    )
                public_url(page.url)
                if section is not None:
                    if urlsplit(page.url).hostname != "app.powerbi.com" or section not in (
                        "Visão geral",
                        "Detalhamento de licitação",
                        "Itens de licitação",
                        "Dados abertos",
                    ):
                        raise SourceError("Seção não permitida no painel público do novo Mural.")
                    await (
                        page.get_by_text(re.compile("^" + re.escape(section) + "$", re.IGNORECASE))
                        .filter(visible=True)
                        .first.click(timeout=15000)
                    )
                    try:
                        await page.wait_for_load_state("networkidle", timeout=12000)
                    except BrowserTimeout:
                        warnings.append("Painel ainda carregando; seção pode estar parcial.")
                    if section == "Dados abertos":
                        try:
                            await page.locator(
                                'a[href*="/arquivos/ie_exp/licitacao_municipal/"]'
                            ).first.wait_for(timeout=15000)
                        except BrowserTimeout:
                            warnings.append("Links de download ainda não apareceram no painel.")
                result = parse_page(await page.content(), page.url)
                frames = []
                for frame in page.frames[1:11]:
                    try:
                        public_url(frame.url)
                        parsed = parse_page(await frame.content(), frame.url)
                        frames.append({"url": frame.url, "texto": parsed["texto"][:20000]})
                        result["links"].extend(parsed["links"])
                    except (SourceError, ValueError, BrowserError):
                        warnings.append(f"Frame não lido: {frame.url}")
                result["texto"] += "\n" + "\n".join(f["texto"] for f in frames)
                return {
                    **result,
                    **provenance(page.url),
                    "renderizado": True,
                    "secao": section,
                    "status_http": response.status if response else None,
                    "frames_lidos": [f["url"] for f in frames],
                    "avisos_renderizacao": warnings,
                    "limite_renderizacao": "Texto/links visíveis; não extrai automaticamente todo o modelo Power BI. "
                    "Máximo 10 frames, 20000 caracteres por frame; sem login ou operações de envio.",
                }
        except TimeoutError as e:
            raise SourceError("Tempo de renderização esgotado.") from e
        finally:
            await browser.close()
