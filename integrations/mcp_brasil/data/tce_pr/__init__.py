"""Adaptador opcional; requer mcp-tce-pr instalado no ambiente do MCP Brasil."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="tce_pr",
    description="TCE-PR: portal público, documentos, processos, PIT e bases CSV",
    version="0.3.0",
    api_base="https://servicos.tce.pr.gov.br",
    requires_auth=False,
    tags=["tce", "pr", "licitacoes", "obras", "jurisprudencia"],
)
