"""Tipos dos contratos C2, C3 e C4 (spec 00-projeto, §5).

Versão mínima criada por C para destravar a frente `dados`. Os nomes e campos
seguem a spec; mudanças só com o acordo dos três.
"""
from typing import Literal

from pydantic import BaseModel


class ResultadoNormalizacao(BaseModel):
    entrada: str
    encontrado: bool
    principio_ativo: list[str] = []
    concentracao: str | None = None
    nome_comercial: str | None = None
    candidatos: list[str] = []
    fonte: str = ""


class ItemParaChecar(BaseModel):
    item_id: str
    principio_ativo: list[str]


class Alerta(BaseModel):
    tipo: Literal["interacao", "duplicidade_principio", "duplicidade_classe", "cbmpi"]
    item_ids: list[str]
    principios: list[str]
    gravidade: Literal["alta", "moderada", "baixa"] | None
    descricao: str
    fonte: str
    conferencia: Literal["llm", "profissional"]


class SintomaEstruturado(BaseModel):
    descricao: str
    sintomas: list[str] = []
    inicio: str | None = None
    intensidade: Literal["leve", "moderada", "forte"] | None = None
    sinais: dict[str, bool] = {}


class Conduta(BaseModel):
    nivel: Literal["ligue_192", "atendimento_24h", "observar"]
    regra_id: str
    motivo: str
    fonte: str
