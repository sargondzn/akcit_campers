from dados.validar_tabelas import validar


def test_tabelas_validas():
    assert validar() == []
