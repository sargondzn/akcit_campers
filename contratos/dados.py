"""Tipos dos contratos C2, C3, C4 e C8 (spec 00-projeto, §5).

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


class InfoRemedio(BaseModel):
    """C8 (24/10): o que se sabe de um remédio, só de tabela com fonte."""
    principio_ativo: str
    para_que_serve: str                      # frase simples de uso comum: "controlar a pressão alta"
    farmacia_popular: bool = False
    farmacia_popular_detalhe: str | None = None      # indicação do programa, se houver
    documentos_farmacia_popular: list[str] = []      # ["a receita", "um documento oficial com foto e CPF"]
    tipo_receita: Literal["simples", "controle_especial", "antimicrobiano"] | None = None
    validade_receita_dias: int | None = None
    fonte: str
    conferencia: Literal["llm", "profissional"]
