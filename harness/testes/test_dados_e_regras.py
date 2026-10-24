"""Stubs de C2–C4 e C8, regra de 192 em todas as variações e o limite de ferramentas (spec §13.1, §17, §18)."""

import pytest

from harness import dados_ponte as dados
from harness.contratos import ItemParaChecar, SintomaEstruturado
from harness.estado import EstadoMensagem
from harness.ferramentas.registro import gancho_limite


@pytest.mark.parametrize("texto", [
    "caiu e bateu a cabeça", "bateu com a cabeça no batente", "levou um tombo e bateu a cabeça",
    "dor no peito", "aperto no peito", "dor forte no peito",
    "falta de ar", "não consegue respirar", "respirando com dificuldade", "estou sem ar",
    "ficou confuso de repente", "não reconhece ninguém", "falando coisa sem sentido",
])
def test_sinais_de_alarme_com_variacoes(texto):
    conduta = dados.detectar_alarme(texto)
    assert conduta is not None and conduta.nivel == "ligue_192", texto


@pytest.mark.parametrize("texto", [
    "ela está bem hoje", "tomou o remédio da manhã", "comprei losartana", "tontura leve desde ontem",
])
def test_sem_alarme_em_frases_normais(texto):
    assert dados.detectar_alarme(texto) is None, texto


@pytest.mark.parametrize("entrada, principio", [
    ("Losartana 50 mg", "losartana"),
    ("LOSARTANA POTÁSSICA 50MG", "losartana"),
    ("Cozaar 50 mg", "losartana"),
    ("glifage 850", "metformina"),
    ("aas 100 mg", "acido acetilsalicilico"),
])
def test_normalizar_nomes_comerciais_e_caixa_alta(entrada, principio):
    r = dados.normalizar(entrada)
    assert r.encontrado and principio in r.principio_ativo, entrada


def test_normalizar_associacao_devolve_dois_principios():
    r = dados.normalizar("losartana + hidroclorotiazida")
    assert r.encontrado and set(r.principio_ativo) == {"losartana", "hidroclorotiazida"}


def test_normalizar_desconhecido_nao_inventa():
    r = dados.normalizar("remedio inexistente xyz")
    assert not r.encontrado and r.principio_ativo == []


def test_checar_lista_duplicidade_interacao_e_cbmpi():
    itens = [
        ItemParaChecar(item_id="1", principio_ativo=["enalapril"]),
        ItemParaChecar(item_id="2", principio_ativo=["losartana"]),
        ItemParaChecar(item_id="3", principio_ativo=["diazepam"]),
        ItemParaChecar(item_id="4", principio_ativo=["diazepam"]),
    ]
    tipos = [a.tipo for a in dados.checar_lista(itens)]
    assert "duplicidade_principio" in tipos
    assert "interacao" in tipos
    assert "cbmpi" in tipos


def test_checar_lista_sem_alertas_quando_nao_ha_risco():
    assert dados.checar_lista([ItemParaChecar(item_id="1", principio_ativo=["metformina"])]) == []


def test_avaliar_gravidade_niveis():
    assert dados.avaliar_gravidade(SintomaEstruturado(descricao="ela desmaiou", sintomas=["desmaio"])).nivel == "atendimento_24h"
    assert dados.avaliar_gravidade(SintomaEstruturado(descricao="tontura leve", sintomas=["tontura"])).nivel == "observar"
    assert dados.avaliar_gravidade(SintomaEstruturado(descricao="caiu e bateu a cabeça", sintomas=["queda"])).nivel == "ligue_192"


def test_info_remedio_com_e_sem_farmacia_popular():
    assert dados.info_remedio("losartana").farmacia_popular is True
    assert dados.info_remedio("diazepam").farmacia_popular is False
    assert dados.info_remedio("diazepam").tipo_receita == "controle_especial"
    assert dados.info_remedio("principio que nao existe") is None


def test_limite_de_ferramentas_conta_e_bloqueia():
    estado = EstadoMensagem("m", "c", "i")
    gancho = gancho_limite(estado)
    chamada = lambda: "ok"
    respostas = [gancho("f", chamada, {}) for _ in range(7)]
    assert respostas[:5] == ["ok"] * 5
    assert "Limite de ferramentas" in respostas[5]
    assert estado.chamadas_ferramenta == 7


def test_ferramenta_com_argumento_invalido_volta_como_erro():
    estado = EstadoMensagem("m", "c", "i")

    def falha(**kw):
        raise TypeError("argumento errado")

    assert gancho_limite(estado)("f", falha, {"x": 1}).startswith("Erro na ferramenta")
