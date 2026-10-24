"""Gabaritos cegos de relatos (frases de cuidadora geradas por um subagente Sonnet que não viu as regexes).

- rodada 1: usada para AJUSTAR as regexes (1º ciclo). Teste de regressão, não prova de qualidade.
- rodada 2: usada para AJUSTAR as regexes (2º ciclo). Idem.
- rodada 3: frases novas, medidas DEPOIS dos dois ciclos e SEM ajuste posterior. É a estimativa honesta.
  Resultado em 24/10/2026: 59 de 105 alarmes (56%; os 4 sinais originais: 58%) e 3 falsos positivos em 20.
  Antes de qualquer ajuste, a rodada 1 tinha dado 59%: dois ciclos de ajuste NÃO melhoraram o recall em frases
  novas. Os pisos abaixo só impedem piora; não suba o número ajustando regex para a rodada 3.
"""
import json
from pathlib import Path

import pytest

from dados.gravidade import detectar_alarme

PASTA = Path(__file__).resolve().parents[2] / "avaliacao" / "exemplos" / "relatos_cegos"


def carregar(nome):
    with open(PASTA / nome, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def medir(casos):
    alarmes = [c for c in casos if c["alarme"]]
    outros = [c for c in casos if not c["alarme"]]
    acertos = sum(1 for c in alarmes if detectar_alarme(c["texto"]))
    falsos = sum(1 for c in outros if detectar_alarme(c["texto"]))
    return acertos, len(alarmes), falsos, len(outros)


def test_rodada1_todo_alarme_dispara():
    acertos, n, falsos, m = medir(carregar("rodada1.jsonl"))
    assert acertos == n == 175
    assert falsos <= 1 and m == 31  # "discussão bem confusa" é falso positivo conhecido


def test_rodada2_usada_no_ajuste():
    acertos, n, falsos, m = medir(carregar("rodada2.jsonl"))
    assert acertos == n == 84 and m == 15
    assert falsos == 0


def test_rodada3_estimativa_honesta_nao_piora():
    acertos, n, falsos, m = medir(carregar("rodada3.jsonl"))
    assert n == 105 and m == 20
    assert acertos >= 59  # 56%: ver docstring
    assert falsos <= 3


@pytest.mark.parametrize("arquivo", ["rodada1.jsonl", "rodada2.jsonl", "rodada3.jsonl"])
def test_formato_do_gabarito(arquivo):
    for c in carregar(arquivo):
        assert {"id", "texto", "nivel_esperado", "alarme", "real"} <= set(c)
        assert c["real"] is False
        assert (c["nivel_esperado"] == "ligue_192") == c["alarme"]
