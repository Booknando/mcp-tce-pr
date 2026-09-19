"""Fontes verificadas em 19/09/2026; URLs de arquivos descobertas no catálogo."""

CATALOG = "https://servicos.tce.pr.gov.br/servicos/srv_dados_abertos.aspx"
LICITACOES = "https://servicos.tce.pr.gov.br/servicos/arquivos/dadosabertos/muraldelicitacoes/"
ACORDAOS = "https://viajuris.tce.pr.gov.br/DadosAbertos/DadosAbertos/BaseDados"
ALLOWED_HOSTS = {"servicos.tce.pr.gov.br", "viajuris.tce.pr.gov.br"}
MAX_BYTES = 128 * 1024 * 1024
MAX_CACHE_BYTES = 192 * 1024 * 1024
CACHE_SECONDS = 3600
MAX_CACHE_ENTRIES = 4
OBRAS_FILES = {
    "obras_municipais_base_de_dados.csv": "obras",
    "acompanhamentos_base_de_dados.csv": "acompanhamentos",
    "responsaveis_tecnicos_base_de_dados.csv": "responsaveis_tecnicos",
    "bens_patrimoniais_base_de_dados.csv": "bens_patrimoniais",
}
