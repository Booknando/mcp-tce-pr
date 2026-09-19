from .constants import ACORDAOS, CATALOG, LICITACOES
from .portal import AREAS


def fontes_pr() -> dict:
    return {
        "catalogo": CATALOG,
        "licitacoes_historico": LICITACOES,
        "acordaos": ACORDAOS,
        "areas_portal": AREAS,
        "limitacoes": "CSV, portal público e PIT; sem consulta processual autenticada. Cache CSV de 1 hora. "
        "Valores originais em texto. Não presume atualização diária efetiva.",
    }
