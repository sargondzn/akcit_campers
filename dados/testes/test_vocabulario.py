from dados.gravidade import INTENSIDADES
from dados.vocabulario import DOCUMENTO, documento, vocabulario


def test_documento_do_vocabulario_esta_atualizado():
    # se falhar: python -m dados.vocabulario > specs/dados/vocabulario-diario.md
    assert DOCUMENTO.read_text(encoding="utf-8") == documento()


def test_vocabulario_tem_o_essencial():
    v = vocabulario()
    assert {"queda", "sangramento", "febre", "tontura"} <= set(v["sintomas"])
    assert {"fala_enrolada", "rosto_torto"} <= set(v["sinais"])
    assert v["intensidades"] == list(INTENSIDADES)
