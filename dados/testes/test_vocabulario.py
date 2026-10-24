"""O vocabulário (dados/tabelas/vocabulario.csv) é a fonte; regras e Diário se adaptam a ele (DA-D4)."""
import json

import pytest

from contratos.dados import SintomaEstruturado
from dados.gravidade import INTENSIDADES, _regras, avaliar_gravidade
from dados.validar_tabelas import _validar_vocabulario
from dados.vocabulario import DOCUMENTO, como_json, documento, linhas, vocabulario


def entrada(descricao="", sintomas=(), sinais=(), intensidade=None):
    return SintomaEstruturado(descricao=descricao, sintomas=list(sintomas), intensidade=intensidade,
                              sinais={k: True for k in sinais})


# --- documento e formato ------------------------------------------------------------------

def test_documento_do_vocabulario_esta_atualizado():
    # se falhar: python -m dados.vocabulario > specs/dados/vocabulario-diario.md
    assert DOCUMENTO.read_text(encoding="utf-8") == documento()


def test_documento_diz_que_o_vocabulario_prevalece():
    assert "prevalece" in documento()


def test_json_bate_com_a_tabela_e_e_serializavel():
    j = como_json()
    json.dumps(j, ensure_ascii=False)
    v = vocabulario()
    assert sorted(x["termo"] for x in j["sintomas"]) == v["sintomas"]
    assert sorted(x["termo"] for x in j["sinais"]) == v["sinais"]
    assert [x["termo"] for x in j["intensidades"]] == list(INTENSIDADES)
    assert all(x["definicao"] and x["exemplo"] for k in ("sintomas", "sinais") for x in j[k])


def test_vocabulario_tem_o_essencial():
    v = vocabulario()
    assert {"queda", "sangramento", "febre", "tontura", "desmaio", "fezes_pretas", "dor_no_peito"} <= set(v["sintomas"])
    assert {"fala_enrolada", "rosto_torto", "bateu_a_cabeca", "inicio_subito"} <= set(v["sinais"])
    assert v["intensidades"] == ["leve", "moderada", "forte"]


# --- invariantes entre vocabulário e regras (as mesmas que validar_tabelas.py cobra) -------

def test_validador_aceita_o_vocabulario_atual():
    import csv
    from dados.validar_tabelas import TABELAS
    with open(TABELAS / "regras_gravidade.csv", encoding="utf-8") as f:
        regras = list(csv.DictReader(f))
    assert _validar_vocabulario(linhas(), regras) == []


def _linha(**kw):
    base = {"tipo": "sintoma", "termo": "febre", "definicao": "x", "sinonimos": "febril", "exclusoes": "",
            "exemplo": "teve febre", "tratamento": "regra", "fonte": "f", "conferencia": "llm"}
    return {**base, **kw}


def _regra(cond):
    return {"regra_id": "r1", "ordem": "1", "condicao": cond, "nivel": "observar", "motivo": "m", "fonte": "f", "conferencia": "llm"}


@pytest.mark.parametrize("vocab,regras,trecho", [
    ([_linha(), _linha(termo="calor", sinonimos="febril", exemplo="muito calor febril")], [_regra("s:febre | s:calor")], "ambígua"),
    ([_linha()], [_regra("s:febre | s:tontura")], "não está no vocabulário"),
    ([_linha(), _linha(termo="tontura", exemplo="tontura", sinonimos="")], [_regra("s:febre")], "nenhuma regra o usa"),
    ([_linha(tratamento="sem_regra")], [_regra("s:febre")], "mas uma regra o usa"),
    ([_linha(exemplo="está bem")], [_regra("s:febre")], "não contém o termo"),
    ([_linha(sinonimos="Febril")], [_regra("s:febre")], "fora do formato normalizado"),
    ([_linha(), _linha()], [_regra("s:febre")], "termo repetido"),
    ([_linha(tratamento="talvez")], [_regra("s:febre")], "tratamento inválido"),
    ([_linha(termo="Febre Alta", exemplo="febre alta")], [_regra("s:febre_alta")], "minúsculo"),
])
def test_validador_pega_vocabulario_ruim(vocab, regras, trecho):
    erros = _validar_vocabulario(vocab, regras)
    assert any(trecho in e for e in erros), erros


def test_todo_termo_das_regras_esta_no_vocabulario():
    from dados.gravidade import interpretar_condicao
    conhecidos = {(l["tipo"], l["termo"]) for l in linhas()}
    for regra in _regras():
        for alt in regra["alternativas"]:
            for tipo, valor in alt:
                if tipo != "int":
                    assert ("sintoma" if tipo == "s" else "sinal", valor) in conhecidos, (regra["regra_id"], tipo, valor)


# --- cada regra é alcançável só com termos canônicos ------------------------------------------

def _monta(alternativa):
    sintomas = [v for t, v in alternativa if t == "s"]
    sinais = [v for t, v in alternativa if t == "sinal"]
    ints = [v for t, v in alternativa if t == "int"]
    return entrada(sintomas=sintomas, sinais=sinais, intensidade=ints[0] if ints else None)


def _casos_de_alcance():
    return [pytest.param(r, alt, id=f"{r['regra_id']}#{i}") for r in _regras() for i, alt in enumerate(r["alternativas"])]


@pytest.mark.parametrize("regra,alternativa", _casos_de_alcance())
def test_cada_alternativa_de_regra_e_alcancavel(regra, alternativa):
    c = avaliar_gravidade(_monta(alternativa))
    ordem_obtida = next((r["ordem"] for r in _regras() if r["regra_id"] == c.regra_id), -1)
    # vence a própria regra, uma regra anterior (mais grave) ou um alarme de 192
    assert c.regra_id == regra["regra_id"] or c.regra_id.startswith("alarme_") or ordem_obtida < regra["ordem"], c


# --- termos de alarme realmente disparam o 192 --------------------------------------------------

def _termos_de_alarme():
    return [pytest.param(l, id=f"{l['tipo']}:{l['termo']}") for l in linhas() if "alarme" in l["tratamento"]]


@pytest.mark.parametrize("linha", _termos_de_alarme())
def test_termo_de_alarme_dispara_192_sozinho(linha):
    e = entrada(sintomas=[linha["termo"]]) if linha["tipo"] == "sintoma" else entrada(sinais=[linha["termo"]])
    c = avaliar_gravidade(e)
    assert c.nivel == "ligue_192", (linha["termo"], c)


# --- o exemplo de cada termo, só como texto, produz a conduta da própria linha ------------------

def _exemplos_de_sintoma():
    return [pytest.param(l, id=l["termo"]) for l in linhas() if l["tipo"] == "sintoma"]


def _tem_regra_solo(termo):
    return any(len(alt) == 1 and alt[0] == ("s", termo) for r in _regras() for alt in r["alternativas"])


@pytest.mark.parametrize("linha", _exemplos_de_sintoma())
def test_exemplo_em_texto_cru_tem_a_conduta_da_linha(linha):
    c = avaliar_gravidade(entrada(descricao=linha["exemplo"]))
    if "alarme" in linha["tratamento"]:
        assert c.nivel == "ligue_192", (linha["exemplo"], c)
    elif linha["tratamento"] == "sem_regra":
        assert c.nivel == "observar", (linha["exemplo"], c)  # só registro: nunca escala
    elif _tem_regra_solo(linha["termo"]):
        assert c.regra_id != "padrao_observar", (linha["exemplo"], c)
    # termo que só entra em combinações (suor_frio com palpitacao etc.) não escala sozinho


# --- sinônimos, exclusões, negação e intensidade ------------------------------------------------

@pytest.mark.parametrize("texto,regra", [
    ("levou um tombo e dói o quadril", "grav_queda_sem_levantar"),
    ("a vó escorregou no banheiro", "grav_queda"),
    ("tropeçou no tapete", "grav_queda"),
    ("foi ao chão na cozinha", "grav_queda"),
    ("o coco dele tá preto", "grav_sangramento"),
    ("as fezes estão escuras desde ontem", "grav_sangramento"),
    ("a urina saiu vermelha", "grav_sangramento"),
    ("ele está febril", "grav_febre"),
    ("está dormindo o dia todo", "grav_sonolencia_excessiva"),
    ("ficou engasgada com a comida", "grav_engasgo"),
    ("perna esquerda inchada", "grav_inchaco"),
    ("não está urinando", "grav_vomito_diarreia"),
    ("não quer beber água", "grav_vomito_diarreia"),
    ("está com a glicemia baixa", "grav_acucar_baixo"),
])
def test_sinonimos_em_texto_cru(texto, regra):
    assert avaliar_gravidade(entrada(descricao=texto)).regra_id == regra


@pytest.mark.parametrize("texto", [
    "caiu a energia no bairro", "a pressão caiu um pouco hoje", "caiu a internet", "queda de cabelo",
    "fez exame de sangue de rotina", "foi doar sangue", "vai afinar o sangue com o médico",
    "caiu o preço do remédio",
])
def test_exclusoes_nao_viram_sintoma(texto):
    assert avaliar_gravidade(entrada(descricao=texto)).regra_id in ("padrao_observar", "obs_sintomas_leves")
    assert avaliar_gravidade(entrada(descricao=texto)).nivel == "observar"


@pytest.mark.parametrize("texto", ["sem febre hoje", "não teve vômito", "não está com tontura", "sem tontura"])
def test_negacao_so_na_descricao(texto):
    assert avaliar_gravidade(entrada(descricao=texto)).nivel == "observar"
    assert avaliar_gravidade(entrada(descricao=texto)).regra_id != "grav_febre"


def test_sintoma_listado_pelo_diario_e_aceito_como_esta():
    # o Diário listou "febre": confiamos, mesmo que a descrição diga "sem"
    assert avaliar_gravidade(entrada(descricao="sem febre ontem, mas hoje piorou", sintomas=["febre"])).regra_id == "grav_febre"


def test_alarme_continua_sem_tratar_negacao():
    assert avaliar_gravidade(entrada(descricao="não teve dor no peito")).nivel == "ligue_192"


@pytest.mark.parametrize("texto,nivel", [
    ("dor insuportável na perna", "atendimento_24h"),
    ("uma dor fortíssima nas costas", "atendimento_24h"),
    ("dorzinha leve na perna", "observar"),
    ("dor leve", "observar"),
    ("tontura forte ao levantar", "atendimento_24h"),
    ("tontura levinha", "observar"),
])
def test_intensidade_inferida_da_fala(texto, nivel):
    assert avaliar_gravidade(entrada(descricao=texto)).nivel == nivel


def test_intensidade_do_diario_vence_a_pista():
    assert avaliar_gravidade(entrada(descricao="dor insuportável", sintomas=["dor"], intensidade="leve")).nivel == "observar"
    assert avaliar_gravidade(entrada(descricao="dorzinha", sintomas=["dor"], intensidade="forte")).nivel == "atendimento_24h"


def test_dor_de_cabeca_subita_e_forte_e_192():
    c = avaliar_gravidade(entrada(descricao="começou do nada, dor de cabeça fortíssima", sintomas=["dor_de_cabeca"]))
    assert c.nivel == "ligue_192"
    assert avaliar_gravidade(entrada(descricao="dor de cabeça leve", sintomas=["dor_de_cabeca"])).nivel == "observar"


def test_dor_nao_casa_dentro_de_outra_palavra():
    # "dor" não pode casar "dormiu" nem "dormente"
    assert avaliar_gravidade(entrada(descricao="dormiu bem, forte e saudável")).regra_id == "padrao_observar"
