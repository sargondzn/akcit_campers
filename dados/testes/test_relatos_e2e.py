"""Relatos de ponta a ponta: texto da cuidadora -> conduta (192, 24h, observar). DA-D4.

O gabarito (`avaliacao/exemplos/relatos_e2e/gabarito.jsonl`) foi escrito e rotulado por um Sonnet 5.5 que viu
só o vocabulário e a definição dos três níveis (não as regras nem as regexes): `nivel_esperado` é o julgamento
dele, não de um clínico (`conferencia = llm`).

Três caminhos, do mais simples ao completo:
1. texto cru     : sem Diário; mede o que `dados` entrega sozinho.
2. oráculo       : o Diário "perfeito" (ficha esperada); mede só regras e vocabulário.
3. Diário real   : `harness.diario.estruturar` (de B); precisa de OPENAI_API_KEY. Pula se não houver.

Os números abaixo foram medidos em 24/10/2026. ATENÇÃO: depois da 1ª medição (texto cru 42/54 = 78% com 8
subtriagens; oráculo 48/54 = 89% com 1 subtriagem) as regras e o vocabulário foram corrigidos olhando
estes mesmos casos, então os números atuais são OTIMISTAS: o gabarito virou conjunto de desenvolvimento.
"""
import os

import pytest

from avaliacao.relatos import GRAVIDADE, carregar, medir, oraculo, pipeline, resumo, texto_cru
from dados.vocabulario import vocabulario

CASOS = carregar()

# Divergências de julgamento entre o rotulador e as regras (todas de supertriagem): documentadas no gabarito.
DIVERGENCIAS = {"e2e_034": "ligue_192", "e2e_035": "ligue_192", "e2e_036": "ligue_192", "e2e_046": "atendimento_24h"}
# Limites do texto cru: dependem de número que só o Diário transforma em termo do vocabulário.
LIMITES_TEXTO_CRU = {"e2e_029", "e2e_033"}


def test_gabarito_bem_formado():
    assert len(CASOS) == 54
    por_nivel = {n: sum(1 for c in CASOS if c["nivel_esperado"] == n) for n in GRAVIDADE}
    assert por_nivel == {"observar": 18, "atendimento_24h": 18, "ligue_192": 18}
    ids = [c["id"] for c in CASOS]
    assert len(set(ids)) == len(ids)
    for c in CASOS:
        assert c["real"] is False and c["conferencia"] == "llm"
        assert c["alarme"] == (c["nivel_esperado"] == "ligue_192")
        assert c["intensidade"] in (None, "leve", "moderada", "forte")


def test_ficha_do_gabarito_usa_so_termos_do_vocabulario():
    v = vocabulario()
    for c in CASOS:
        assert set(c["sintomas"]) <= set(v["sintomas"]), c["id"]
        assert set(c["sinais"]) <= set(v["sinais"]), c["id"]


def test_oraculo_acerta_tudo_menos_as_divergencias_documentadas():
    r = medir(CASOS, oraculo(CASOS))
    print(resumo("oráculo", r))
    assert r["subtriagem"] == []  # nunca fica abaixo do esperado
    obtidos = {c["id"]: pipeline(c["texto"], oraculo(CASOS)).nivel for c in CASOS}
    for c in CASOS:
        if c["id"] in DIVERGENCIAS:
            assert obtidos[c["id"]] == DIVERGENCIAS[c["id"]], c["id"]
            assert "observacao" in c, c["id"]
        else:
            assert obtidos[c["id"]] == c["nivel_esperado"], (c["id"], c["texto"])


def test_texto_cru_nunca_deixa_passar_emergencia():
    # invariante de segurança: relato que o rotulador deu como 192 vira 192 mesmo sem Diário
    r = medir(CASOS, texto_cru)
    print(resumo("texto cru", r))
    esperados_192 = {c["id"] for c in CASOS if c["nivel_esperado"] == "ligue_192"}
    assert not (set(r["subtriagem"]) & esperados_192), set(r["subtriagem"]) & esperados_192


def test_texto_cru_nao_piora():
    r = medir(CASOS, texto_cru)
    assert r["certos"] >= 49  # 91% (otimista: conjunto de desenvolvimento)
    assert set(r["subtriagem"]) <= LIMITES_TEXTO_CRU
    assert len(r["supertriagem"]) <= 3


def test_texto_cru_nao_escala_o_que_nao_e_sintoma():
    sem_nada = [c for c in CASOS if c["nivel_esperado"] == "observar" and not c["sintomas"]]
    assert len(sem_nada) == 8
    for c in sem_nada:
        assert pipeline(c["texto"], texto_cru).nivel == "observar", c["texto"]


def test_diario_real_do_harness():
    """Quando o Diário de B estiver ligado à OpenAI: os dois lados batem? Pula sem a chave."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("sem OPENAI_API_KEY: o Diário real não pode ser chamado")
    harness = pytest.importorskip("harness")
    v = vocabulario()

    def estruturar(texto):
        return harness.diario.estruturar(texto)

    r = medir(CASOS, estruturar)
    print(resumo("Diário real", r))
    fora = sorted({t for c in CASOS for t in estruturar(c["texto"]).sintomas if t not in v["sintomas"]})
    print("termos devolvidos fora do vocabulário:", fora)
    esperados_192 = {c["id"] for c in CASOS if c["nivel_esperado"] == "ligue_192"}
    assert not (set(r["subtriagem"]) & esperados_192)  # emergência nunca pode ficar abaixo de 192
