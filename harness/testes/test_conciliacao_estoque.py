from datetime import date, datetime, timedelta

from harness import conciliacao, estoque
from harness.contratos import Dose, Horario, ItemLido, RegistroEstoque


def it(item_id, nome, principio, conc, horarios=("08:00",), prescritor="cardiologista", **kw):
    return ItemLido(item_id=item_id, nome_lido=nome, principio_ativo=[principio], concentracao=conc,
                    horarios=list(horarios), status="confirmado", prescritor=prescritor, **kw)


ATUAL = [
    it("a", "Losartana 50 mg", "losartana", "50 mg"),
    it("b", "Sinvastatina 20 mg", "sinvastatina", "20 mg", ("21:00",)),
    it("c", "Metformina 850 mg", "metformina", "850 mg", prescritor="endocrinologista"),
]


def test_quatro_tipos_de_mudanca_toda_lista():
    novos = [it("n1", "Losartana 100 mg", "losartana", "100 mg"), it("n2", "Anlodipino 5 mg", "anlodipino", "5 mg"),
             it("n3", "Zocor 20mg", "sinvastatina", "20 mg", ("21:00",))]
    tipos = {(m.tipo, m.item_anterior_id or m.item_novo_id) for m in conciliacao.conciliar(ATUAL, novos, "toda_lista")}
    assert ("alterado", "a") in tipos and ("novo", "n2") in tipos and ("mantido", "b") in tipos and ("ausente", "c") in tipos
    mantido = next(m for m in conciliacao.conciliar(ATUAL, novos, "toda_lista") if m.tipo == "mantido")
    assert mantido.nome_diferente


def test_escopo_do_medico_nao_marca_remedio_de_outro_medico():
    novos = [it("n1", "Losartana 50 mg", "losartana", "50 mg")]
    mudancas = conciliacao.conciliar(ATUAL, novos, "medico", prescritor="Cardiologista")
    ausentes = {m.item_anterior_id for m in mudancas if m.tipo == "ausente"}
    assert ausentes == {"b"}        # a metformina é do endocrinologista


def test_acrescimo_nao_marca_ausente_e_sem_decisao_vira_nao_sei():
    novos = [it("n1", "Anlodipino 5 mg", "anlodipino", "5 mg")]
    assert all(m.tipo != "ausente" for m in conciliacao.conciliar(ATUAL, novos, "acrescimo"))
    mudancas = conciliacao.conciliar(ATUAL, [], "toda_lista")
    mudancas[0].decisao = "medico_tirou"
    finais, pontos = conciliacao.aplicar_decisoes(conciliacao.lista_resultante(ATUAL, [], mudancas), mudancas)
    assert next(i for i in finais if i.item_id == mudancas[0].item_anterior_id).status == "retirado"
    assert len(pontos) == 2     # os outros dois, sem decisão, viram pergunta para a consulta


def test_estoque_com_meio_comprimido_e_dose_nao_tomada():
    agora = datetime(2026, 10, 24, 12, 0)
    item = it("a", "Losartana 50 mg", "losartana", "50 mg", ("08:00", "20:00"), unidades_por_dose=0.5)
    horarios = [Horario(horario_id="h1", item_id="a", horario="08:00"), Horario(horario_id="h2", item_id="a", horario="20:00")]
    registro = RegistroEstoque(item_id="a", quantidade=10, registrado_em=agora - timedelta(days=2))
    doses = [Dose(horario_id="h1", previsto=agora.replace(hour=8), status="nao_tomada")]
    (e,) = estoque.calcular([item], horarios, doses, [registro], agora)
    # 2 dias atrás 12h → 4 doses de 0,5 até agora, menos a das 08h de hoje (não tomada) = 1,5
    assert e.estoque_estimado == 8.5 and e.consumo_diario == 1.0 and int(e.dias_restantes) == 8


def test_avisos_7_e_2_dias_e_receita_vencendo():
    estados = [estoque.EstadoEstoque("a", "A", 7.2, 1, 7.2, None), estoque.EstadoEstoque("b", "B", 5, 1, 5, None),
               estoque.EstadoEstoque("c", "C", 2.9, 1, 2.9, None)]
    assert {e.item_id for e in estoque.avisos_de_estoque(estados)} == {"a", "c"}
    item = it("a", "Losartana 50 mg", "losartana", "50 mg", data_receita=date(2026, 5, 4))   # simples = 180 dias no stub
    assert estoque.receitas_vencendo([item], date(2026, 10, 24))
