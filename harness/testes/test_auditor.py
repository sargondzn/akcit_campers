from harness.contratos import ItemLido
from harness.guardrails import auditor, frases

LISTA = [ItemLido(item_id="a", nome_lido="Losartana 50 mg", principio_ativo=["losartana"], concentracao="50 mg",
                  posologia_texto="1 cp de 12/12h", status="confirmado")]


def ctx(**kw):
    return auditor.ContextoAuditor(itens=LISTA, **kw)


def test_bloqueia_orientacao_de_dose():
    for texto in ["Pode tomar dois comprimidos hoje.", "Dobre a dose da losartana.", "Suspenda o remédio.",
                  "Pode tirar a losartana.", "Troque pela marca mais barata.", "Pare de dar esse remédio."]:
        r = auditor.verificar(texto, ctx())
        assert not r.aprovado, texto
        assert r.texto_final == frases.BLOQUEIO


def test_aprova_frases_fixas_e_texto_normal():
    for texto in [frases.LIGUE_192, frases.AUSENTE.format(nome="Losartana 50 mg"), frases.CONSULTA_SALVA,
                  frases.RECEITA_VENCENDO.format(nome="Losartana", dia="30/10"), "Anotei que ela já tomou a das 8h.",
                  frases.LEITURA_BAIXA_1.format(nome="um dos remédios"), frases.ESCOPO.format(de_quem="do cardiologista")]:
        assert auditor.verificar(texto, ctx()).aprovado, texto


def test_de_um_como_preposicao_nao_bloqueia():
    for texto in [frases.ESCOPO.format(de_quem="de um médico"), frases.LIMITE, frases.NAO_ENTENDI,
                  "Mande a foto de uma caixa de cada vez."]:
        assert auditor.verificar(texto, ctx()).aprovado, texto


def test_de_um_antes_de_dose_bloqueia():
    for texto in ["Dê um comprimido a mais.", "dê uma gota", "Pode de um comprimido a mais hoje.",
                  "Melhor de meio comprimido."]:
        assert not auditor.verificar(texto, ctx()).aprovado, texto


def test_dose_fora_da_lista():
    assert auditor.verificar("A losartana 50 mg está na lista.", ctx()).aprovado
    assert not auditor.verificar("A losartana 100 mg está na lista.", ctx()).aprovado
    assert not auditor.verificar("Não posso recomendar dois comprimidos de losartana.", ctx()).aprovado
    assert auditor.verificar("A receita diz um comprimido de losartana.", ctx()).aprovado


def test_remedio_fora_da_lista():
    assert not auditor.verificar("Você também pode conversar sobre o diazepam.", ctx()).aprovado


def test_fato_clinico_precisa_de_fonte():
    texto = frases.PARA_QUE_SERVE.format(nome="Losartana", uso="controlar a pressão alta")
    assert not auditor.verificar(texto, ctx()).aprovado
    assert auditor.verificar(texto, ctx(tem_info=True)).aprovado
