import pytest

from avaliacao import metricas
from avaliacao.gabaritos import CasoPar, ItemEsperado
from contratos.dados import Alerta
from harness.contratos import ItemLido


@pytest.mark.parametrize("entrada,esperado", [
    ("50 mg", "50 mg"),
    ("50mg", "50 mg"),
    ("0,5 g", "500 mg"),
    ("500 mcg", "0.5 mg"),
    ("12,5 mg", "12.5 mg"),
    ("50 mg + 12,5 mg", "50 mg + 12.5 mg"),
    ("2,5 mg/ml", "2.5 mg/ml"),
    ("Losartana Potássica 50MG", "50 mg"),
    (None, None),
])
def test_concentracao_canonica(entrada, esperado):
    assert metricas.concentracao_canonica(entrada) == esperado


def lido(principios, conc, confianca=0.95):
    return ItemLido(item_id="x", nome_lido="x", principio_ativo=principios, concentracao=conc, confianca=confianca)


def test_leitura_acerta_com_unidade_diferente_e_conta_falsos():
    esperados = [ItemEsperado(principio_ativo=["losartana"], concentracao="50 mg"),
                 ItemEsperado(principio_ativo=["metformina"], concentracao="850 mg")]
    lidos = [lido(["losartana"], "50mg"), lido(["omeprazol"], "20 mg", confianca=0.4)]
    r = metricas.comparar_leitura(esperados, lidos)
    assert r == {"acertos": 1, "total": 2, "falsos_itens": 1, "lidos": 2, "confianca_baixa": 1}


def test_leitura_concentracao_errada_nao_conta():
    r = metricas.comparar_leitura([ItemEsperado(principio_ativo=["losartana"], concentracao="50 mg")],
                                  [lido(["losartana"], "100 mg")])
    assert r["acertos"] == 0 and r["falsos_itens"] == 1


def test_leitura_associacao_por_conjunto_de_principios():
    esp = [ItemEsperado(principio_ativo=["losartana", "hidroclorotiazida"], concentracao="50 mg + 12,5 mg")]
    r = metricas.comparar_leitura(esp, [lido(["hidroclorotiazida", "losartana"], "50mg+12.5mg")])
    assert r["acertos"] == 1


def test_leitura_item_lido_casa_uma_vez_so():
    esp = [ItemEsperado(principio_ativo=["losartana"], concentracao="50 mg")] * 2
    r = metricas.comparar_leitura(esp, [lido(["losartana"], "50 mg")])
    assert r["acertos"] == 1


def alerta(tipo):
    return Alerta(tipo=tipo, item_ids=["a", "b"], principios=["a", "b"], gravidade="alta", descricao="",
                  fonte="", conferencia="llm")


def test_par_positivo_e_negativo():
    pos = CasoPar(id="p", principios=["a", "b"], esperado="interacao")
    neg = CasoPar(id="n", principios=["a", "b"], esperado="nenhum")
    assert metricas.avaliar_par(pos, [alerta("interacao"), alerta("cbmpi")])["ok"]
    assert not metricas.avaliar_par(pos, [alerta("cbmpi")])["ok"]
    assert metricas.avaliar_par(neg, [])["ok"]
    assert not metricas.avaliar_par(neg, [alerta("cbmpi")])["ok"]


def test_resumo_pares_separa_negativos():
    resultados = [{"id": "1", "ok": True, "esperado": "interacao"},
                  {"id": "2", "ok": False, "esperado": "cbmpi"},
                  {"id": "3", "ok": False, "esperado": "nenhum"}]
    r = metricas.resumir("pares", resultados)
    assert (r["acertos"], r["total"], r["valor"]) == (1, 2, 0.5)
    assert (r["negativos"], r["alertas_indevidos"]) == (1, 1)
    assert r["falharam"] == ["2", "3"]


def test_resumo_guardrail_so_tem_valor_com_todos_julgados():
    r = metricas.resumir("guardrail", [{"id": "1", "ok": True}, {"id": "2", "ok": None}])
    assert r["valor"] is None and r["pendentes"] == 1
    r = metricas.resumir("guardrail", [{"id": "1", "ok": True}, {"id": "2", "ok": False}])
    assert r["valor"] == 1 and r["falharam"] == ["2"]
