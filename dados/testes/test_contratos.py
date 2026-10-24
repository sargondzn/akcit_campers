"""As quatro funções entregues a B têm a assinatura exata dos contratos C2 a C4 (spec 00-projeto §5)."""
import inspect

import dados
from contratos.dados import Conduta, ItemParaChecar, ResultadoNormalizacao, SintomaEstruturado, Alerta


def assinatura(funcao):
    sig = inspect.signature(funcao)
    return [(nome, p.annotation) for nome, p in sig.parameters.items()], sig.return_annotation


def test_normalizar_c2():
    params, retorno = assinatura(dados.normalizar)
    assert params == [("nome", str)] and retorno is ResultadoNormalizacao


def test_checar_lista_c3():
    params, retorno = assinatura(dados.checar_lista)
    assert params == [("itens", list[ItemParaChecar])] and retorno == list[Alerta]


def test_detectar_alarme_c4():
    params, retorno = assinatura(dados.detectar_alarme)
    assert params == [("texto", str)] and retorno == (Conduta | None)


def test_avaliar_gravidade_c4():
    params, retorno = assinatura(dados.avaliar_gravidade)
    assert retorno is Conduta
    assert [n for n, _ in params] == ["sintoma"]


def test_exporta_so_as_quatro():
    assert sorted(dados.__all__) == ["avaliar_gravidade", "checar_lista", "detectar_alarme", "normalizar"]
