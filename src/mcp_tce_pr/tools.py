"""Ferramentas sem HTTP direto; consultas delegadas ao cliente."""

from .client import client
from .schemas import Consulta, Dataset


async def atualizar_dados_pr(base: Dataset, ano: int | None = None) -> dict:
    """Busca novamente catálogo e CSV tradicional, ignorando o cache local.

    Informe ano para licitacoes/acordaos. Retorna amostra, origem e horário real
    de obtenção. Não altera o TCE-PR nem garante que a fonte tenha dados novos.
    PIT, novo Mural, páginas e documentos já são buscados a cada consulta.
    """
    return await client.query(Consulta(base=base, ano=ano, limite=1), force=True)


async def listar_bases_pr(base: Dataset | None = None) -> list[dict]:
    """Descobre arquivos e anos efetivamente publicados nos catálogos oficiais do TCE-PR."""
    return [s.model_dump() for s in await client.sources(base)]


async def descrever_base_pr(base: Dataset, ano: int | None = None) -> dict:
    """Retorna nomes originais dos campos e um registro de exemplo para montar filtros."""
    return await client.query(Consulta(base=base, ano=ano, limite=1))


async def consultar_base_pr(
    base: Dataset,
    ano: int | None = None,
    texto: str = "",
    filtros: dict[str, str] | None = None,
    limite: int = 20,
    deslocamento: int = 0,
) -> dict:
    """Consulta CSV oficial. Filtros são substrings combinadas por E, sem distinguir acentos/caixa.

    Use descrever_base_pr para nomes exatos das colunas. texto procura uma expressão em
    qualquer coluna. ano seleciona o arquivo publicado, não filtra datas dos registros.
    limite: 1 a 100. deslocamento pagina os resultados; sem ordenação adicional.
    Inclui fonte, data de obtenção, total e próximo deslocamento. Cache padrão de uma hora.
    """
    return await client.query(
        Consulta(
            base=base,
            ano=ano,
            texto=texto,
            filtros=filtros or {},
            limite=limite,
            deslocamento=deslocamento,
        )
    )


async def consultar_licitacoes_pr(
    ano: int,
    municipio: str = "",
    objeto: str = "",
    limite: int = 20,
    deslocamento: int = 0,
) -> dict:
    """Pesquisa o Mural de Licitações por ano da base, município e trecho do objeto."""
    return await consultar_base_pr(
        "licitacoes",
        ano,
        filtros={
            "nmMunicipio": municipio,
            "dsObjeto": objeto,
        },
        limite=limite,
        deslocamento=deslocamento,
    )


async def consultar_obras_pr(
    municipio: str = "",
    objeto: str = "",
    limite: int = 20,
    deslocamento: int = 0,
) -> dict:
    """Pesquisa obras municipais; confira a última modificação HTTP para avaliar atualidade."""
    return await consultar_base_pr(
        "obras",
        filtros={"nmMunicipio": municipio, "dsObjeto": objeto},
        limite=limite,
        deslocamento=deslocamento,
    )


async def consultar_acordaos_pr(
    ano: int,
    texto: str = "",
    relator: str = "",
    entidade: str = "",
    limite: int = 20,
    deslocamento: int = 0,
) -> dict:
    """Pesquisa acórdãos do ViaJuris; retorna ementas e links PDF quando publicados no CSV."""
    return await consultar_base_pr(
        "acordaos",
        ano,
        texto,
        {
            "NmRelator": relator,
            "DsEntidade": entidade,
        },
        limite,
        deslocamento,
    )
