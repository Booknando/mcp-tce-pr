from typing import Literal

from pydantic import BaseModel, Field

Dataset = Literal[
    "licitacoes",
    "acordaos",
    "obras",
    "acompanhamentos",
    "responsaveis_tecnicos",
    "bens_patrimoniais",
]


class Consulta(BaseModel):
    base: Dataset
    ano: int | None = Field(default=None, ge=1900, le=2100)
    texto: str = Field(default="", max_length=200)
    filtros: dict[str, str] = Field(default_factory=dict, max_length=20)
    limite: int = Field(default=20, ge=1, le=100)
    deslocamento: int = Field(default=0, ge=0, le=100000)


class Fonte(BaseModel):
    base: Dataset
    ano: int | None
    url: str
    catalogo: str
