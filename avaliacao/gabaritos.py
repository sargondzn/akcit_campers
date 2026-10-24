"""Formato dos gabaritos (spec avaliacao §4): um `gabarito.jsonl` por conjunto, uma linha por caso."""
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

TipoAlerta = Literal["interacao", "duplicidade_principio", "duplicidade_classe", "cbmpi"]


class ItemEsperado(BaseModel):
    principio_ativo: list[str]
    concentracao: str | None = None


class CasoLeitura(BaseModel):
    """caixas, receitas_impressas, receitas_manuscritas, pdfs."""
    id: str
    arquivo: str
    itens: list[ItemEsperado]
    real: bool


class CasoPar(BaseModel):
    """pares: `esperado = "nenhum"` é caso negativo (mede alerta falso, fora do recall)."""
    id: str
    principios: list[str]
    esperado: TipoAlerta | Literal["nenhum"]
    tambem: list[TipoAlerta] = []
    justificativa: str = ""
    fonte: str = ""
    conferencia: Literal["llm", "profissional"] = "llm"


class CasoGuardrail(BaseModel):
    id: str
    mensagem: str
    lista: list[str]
    tema: Literal["dose", "troca", "suspensao", "conciliacao", "para_que_serve"] = "dose"


class Julgamento(BaseModel):
    """Leitura da resposta final do guardrail (AV-D2): C decide, o subagente é a segunda leitura."""
    id: str
    contem_orientacao: bool          # decisão final de C
    segunda_leitura: bool | None = None
    observacao: str = ""


MODELOS = {"leitura": CasoLeitura, "pares": CasoPar, "guardrail": CasoGuardrail}


def carregar(caminho: Path, modelo: type[BaseModel]) -> list:
    with open(caminho, encoding="utf-8") as f:
        casos = [modelo.model_validate(json.loads(linha)) for linha in f if linha.strip()]
    ids = [c.id for c in casos]
    repetidos = {i for i in ids if ids.count(i) > 1}
    if repetidos:
        raise ValueError(f"{caminho}: ids repetidos {sorted(repetidos)}")
    return casos
