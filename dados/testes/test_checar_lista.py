from contratos.dados import ItemParaChecar
from dados.farmacovigilante import checar_lista


def lista(*pares):
    return [ItemParaChecar(item_id=i, principio_ativo=p if isinstance(p, list) else [p]) for i, p in pares]


def tipos(alertas):
    return [(a.tipo, tuple(a.principios)) for a in alertas]


def test_lista_sem_alertas():
    assert checar_lista(lista(("1", "losartana"), ("2", "metformina"), ("3", "levotiroxina"))) == []


def test_lista_vazia():
    assert checar_lista([]) == []


def test_interacao_varfarina_aas_e_grave():
    alertas = checar_lista(lista(("1", "varfarina"), ("2", "acido acetilsalicilico")))
    assert len(alertas) == 1
    a = alertas[0]
    assert a.tipo == "interacao" and a.gravidade == "alta"
    assert a.item_ids == ["1", "2"]
    assert a.fonte and a.conferencia == "llm"
    assert "farmacêutico" in a.descricao


def test_demo_varfarina_diclofenaco():
    alertas = checar_lista(lista(("1", "varfarina"), ("2", "diclofenaco")))
    assert alertas[0].tipo == "interacao" and alertas[0].gravidade == "alta"


def test_demo_losartana_espironolactona():
    alertas = checar_lista(lista(("1", "losartana"), ("2", "espironolactona")))
    assert tipos(alertas) == [("interacao", ("espironolactona", "losartana"))]
    assert "potássio" in alertas[0].descricao


def test_demo_sinvastatina_anlodipino_moderada():
    alertas = checar_lista(lista(("1", "sinvastatina"), ("2", "anlodipino")))
    assert alertas[0].gravidade == "moderada"


def test_ordem_do_par_nao_importa():
    a = checar_lista(lista(("1", "varfarina"), ("2", "acido acetilsalicilico")))
    b = checar_lista(lista(("2", "acido acetilsalicilico"), ("1", "varfarina")))
    assert tipos(a) == tipos(b)


def test_duplicidade_de_principio_nomes_diferentes():
    # Glifage e Glucophage normalizam para metformina: dois itens, mesmo princípio
    alertas = checar_lista(lista(("1", "metformina"), ("2", "metformina")))
    assert [(a.tipo, a.gravidade) for a in alertas] == [("duplicidade_principio", "alta")]
    assert alertas[0].item_ids == ["1", "2"]


def test_duplicidade_de_classe_benzodiazepinicos():
    alertas = checar_lista(lista(("1", "clonazepam"), ("2", "diazepam")))
    assert "duplicidade_classe" in {a.tipo for a in alertas}


def test_duplicidade_de_classe_anti_inflamatorios():
    alertas = checar_lista(lista(("1", "diclofenaco"), ("2", "ibuprofeno")))
    assert {"interacao", "duplicidade_classe"} <= {a.tipo for a in alertas}


def test_aas_com_clopidogrel_nao_vira_duplicidade_de_classe():
    # combinação muitas vezes intencional; quem alerta é a interação
    alertas = checar_lista(lista(("1", "acido acetilsalicilico"), ("2", "clopidogrel")))
    assert "duplicidade_classe" not in {a.tipo for a in alertas}


def test_cbmpi_para_um_unico_remedio():
    alertas = checar_lista(lista(("1", "diazepam")))
    assert [(a.tipo, a.principios) for a in alertas] == [("cbmpi", ["diazepam"])]
    assert alertas[0].gravidade is None and alertas[0].fonte.startswith("CBMPI")


def test_associacao_conta_os_dois_principios():
    # losartana+hidroclorotiazida num item só, mais espironolactona em outro
    alertas = checar_lista(lista(("1", ["hidroclorotiazida", "losartana"]), ("2", "espironolactona")))
    assert ("interacao", ("espironolactona", "losartana")) in tipos(alertas)
    assert alertas[0].item_ids == ["1", "2"]


def test_ordenado_por_gravidade_e_sem_repeticao():
    alertas = checar_lista(lista(("1", "varfarina"), ("2", "diclofenaco"), ("3", "ibuprofeno"), ("4", "clonazepam")))
    ordem = {"alta": 0, "moderada": 1, "baixa": 2, None: 3}
    graus = [ordem[a.gravidade] for a in alertas]
    assert graus == sorted(graus)
    assert len(set(tipos(alertas))) == len(alertas)
    assert alertas[0].gravidade == "alta"


def test_principio_desconhecido_e_ignorado():
    assert checar_lista(lista(("1", "paracetamol"), ("2", "losartana"))) == []
