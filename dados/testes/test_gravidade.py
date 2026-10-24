import pytest

from contratos.dados import SintomaEstruturado
from dados.gravidade import avaliar_gravidade, interpretar_condicao


def sintoma(descricao="", sintomas=(), intensidade=None, **sinais):
    return SintomaEstruturado(descricao=descricao, sintomas=list(sintomas), intensidade=intensidade, sinais=sinais)


@pytest.mark.parametrize("s,regras", [
    # o alarme roda primeiro; se a fala já tem o sinal, ele vence, e a regra de gravidade é a rede de segurança
    (sintoma("ela desmaiou na cozinha", ["desmaio"]), {"alarme_desmaio"}),
    (sintoma("teve uma convulsão", ["convulsao"]), {"alarme_desmaio"}),
    (sintoma("a fala ficou enrolada", [], fala_enrolada=True), {"alarme_avc"}),
    (sintoma("rosto torto de repente", [], rosto_torto=True), {"alarme_avc"}),
    (sintoma("sentiu a perna dormente", [], dormencia_subita=True), {"grav_sinais_avc"}),
    (sintoma("o olho esquerdo parou de funcionar", [], perda_de_visao=True), {"grav_sinais_avc"}),
    (sintoma("vomitou sangue", ["vomito_com_sangue"]), {"alarme_sangramento_grave"}),
    (sintoma("sangrando muito", ["sangramento"], "forte"), {"alarme_sangramento_grave"}),
    (sintoma("o nariz não para", ["sangramento"], "forte"), {"grav_sangramento_forte"}),
    (sintoma("tosse com secreção", ["tosse_com_sangue"]), {"alarme_sangramento_grave"}),
    (sintoma("fezes pretas e tontura", ["fezes_pretas", "tontura"]), {"alarme_sangramento_grave"}),
    (sintoma("caiu e dói o quadril", ["queda", "quadril"]), {"grav_queda_sem_levantar"}),
    (sintoma("suando frio com palpitação", ["suor_frio", "palpitacao"]), {"grav_suor_frio_mal_estar"}),
])
def test_192_pelas_regras_de_gravidade(s, regras):
    c = avaliar_gravidade(s)
    assert c.nivel == "ligue_192" and c.regra_id in regras


@pytest.mark.parametrize("s,regra", [
    (sintoma("escorregou no tapete e se apoiou na parede", ["queda"]), "grav_queda"),
    (sintoma("sangrou um pouco o nariz", ["sangramento"], "leve"), "grav_sangramento"),
    (sintoma("fezes pretas hoje", ["fezes_pretas"]), "grav_sangramento"),
    (sintoma("está com febre", ["febre"]), "grav_febre"),
    (sintoma("ela caiu ontem", ["caiu"]), "grav_queda"),
    (sintoma("fezes escuras há dois dias", ["fezes_escuras"]), "grav_sangramento"),
    (sintoma("não está urinando desde ontem", ["nao_esta_urinando"]), "grav_vomito_diarreia"),
    (sintoma("diarreia há três dias", ["diarreia"], "moderada"), "grav_vomito_diarreia"),
    (sintoma("perna esquerda inchada e vermelha", ["inchaco"]), "grav_inchaco"),
    (sintoma("muito sonolenta, difícil de acordar", ["dificil_de_acordar"]), "grav_sonolencia_excessiva"),
    (sintoma("engasgou com a comida", ["engasgo"]), "grav_engasgo"),
    (sintoma("muito enjoo", ["vomito"], "moderada"), "grav_vomito_diarreia"),
    (sintoma("tontura forte", ["tontura"], "forte"), "grav_tontura_forte"),
    (sintoma("dor forte na perna", ["dor"], "forte"), "grav_dor_forte"),
    (sintoma("pernas inchadas", ["inchaco_nas_pernas"]), "grav_inchaco"),
    (sintoma("suando frio e tremendo", ["suor_frio", "tremor"]), "grav_acucar_baixo"),
])
def test_atendimento_24h(s, regra):
    c = avaliar_gravidade(s)
    assert c.nivel == "atendimento_24h" and c.regra_id == regra


@pytest.mark.parametrize("s", [
    sintoma("um pouco de tontura", ["tontura"], "leve"),
    sintoma("dor de cabeça leve", ["dor_de_cabeca"], "leve"),
    sintoma("está sem apetite", ["falta_de_apetite"]),
])
def test_observar(s):
    c = avaliar_gravidade(s)
    assert c.nivel == "observar" and c.regra_id == "obs_sintomas_leves"


def test_padrao_quando_nenhuma_regra_casa():
    c = avaliar_gravidade(sintoma("hoje acordou animada", ["bem_disposta"]))
    assert c.nivel == "observar" and c.regra_id == "padrao_observar"


def test_alarme_tem_prioridade_sobre_as_regras():
    # "queda" casaria atendimento_24h, mas bater a cabeça é sinal de alarme (192)
    c = avaliar_gravidade(sintoma("caiu e bateu a cabeça", ["queda"]))
    assert c.nivel == "ligue_192" and c.regra_id == "alarme_queda_cabeca"


def test_alarme_pelos_sinais_estruturados():
    c = avaliar_gravidade(sintoma("caiu no banheiro", ["queda"], bateu_a_cabeca=True))
    assert c.regra_id == "alarme_queda_cabeca"


def test_sinal_falso_nao_conta():
    c = avaliar_gravidade(sintoma("tropeçou", ["queda"], bateu_a_cabeca=False))
    assert c.regra_id == "grav_queda"


def test_intensidade_ausente_nao_casa_regra_com_intensidade():
    assert avaliar_gravidade(sintoma("dor na perna", ["dor"])).nivel == "observar"


def test_interpretar_condicao_e_validacao():
    assert interpretar_condicao("s:a & int:forte | sinal:b") == [[("s", "a"), ("int", "forte")], [("sinal", "b")]]
    for ruim in ["x:abc", "s:", "int:altissima", ""]:
        with pytest.raises(ValueError):
            interpretar_condicao(ruim)
