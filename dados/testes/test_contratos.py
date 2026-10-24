"""As quatro funções entregues a B têm a assinatura exata dos contratos C2 a C4 (spec 00-projeto §5)."""
import inspect

import dados
from contratos.dados import Alerta, Conduta, InfoRemedio, ItemParaChecar, ResultadoNormalizacao, SintomaEstruturado


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


def test_info_remedio_c8():
    params, retorno = assinatura(dados.info_remedio)
    assert params == [("principio_ativo", str)] and retorno == (InfoRemedio | None)


def test_auxiliares_do_harness():
    assert dados.texto_normalizado("  Ácido  ACETILSALICÍLICO! ") == "acido acetilsalicilico"
    nomes = dados.nomes_conhecidos()
    assert {"losartana", "glifage", "aspirina", "marevan", "acido acetilsalicilico"} <= nomes
    assert all(n == dados.texto_normalizado(n) for n in nomes)


def test_exporta_os_contratos_e_os_auxiliares():
    assert sorted(dados.__all__) == ["avaliar_gravidade", "checar_lista", "detectar_alarme", "info_remedio",
                                     "nomes_conhecidos", "normalizar", "texto_normalizado"]
