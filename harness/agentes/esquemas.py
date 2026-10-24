"""Saídas tipadas dos subagentes (spec §2.2, §6, §9, §11). Sem valores padrão: a saída
estruturada da OpenAI exige todos os campos, e o que o modelo não souber volta como null."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class RemedioBruto(BaseModel):
    texto_remedio: str
    texto_posologia: str | None
    texto_embalagem: str | None
    legivel: Literal["sim", "parcial", "nao"]


class LeituraBruta(BaseModel):
    tipo_documento: Literal["receita_impressa", "receita_mao", "receita_alta", "caixa", "outro"]
    texto_cabecalho: str | None
    remedios: list[RemedioBruto]


class ItemInterpretado(BaseModel):
    nome_lido: str
    concentracao: str | None
    forma: str | None
    posologia_texto: str | None
    horarios: list[str]
    unidades_por_dose: float | None
    quantidade_embalagem: int | None
    indicacao_na_receita: str | None
    legivel: Literal["sim", "parcial", "nao"]
    confianca_modelo: float


class ItensInterpretados(BaseModel):
    tipo_documento: Literal["receita_impressa", "receita_mao", "receita_alta", "caixa", "receita_pdf", "outro"]
    prescritor: str | None
    data_receita: str | None          # AAAA-MM-DD
    itens: list[ItemInterpretado]


class SaidaDiario(BaseModel):
    descricao: str
    sintomas: list[str]
    inicio: str | None
    intensidade: Literal["leve", "moderada", "forte"] | None
    sinais: list[str]                  # sinais presentes, ex.: ["bateu_a_cabeca"]
    pergunta: str | None               # a próxima pergunta, se faltar o essencial


class PerguntaConsulta(BaseModel):
    texto: str
    origem_id: str


class PerguntasConsulta(BaseModel):
    perguntas: list[PerguntaConsulta]


class RelatoConsulta(BaseModel):
    orientacoes: list[str]
    exames_pedidos: list[str]
    retorno_em: str | None             # AAAA-MM-DD ou texto ("em 3 meses")
    mudancas_citadas: list[str]
