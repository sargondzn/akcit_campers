import pytest

from dados.etl.cmed import PRINCIPIOS
from dados.normalizador import normalizar

# Um nome comercial conhecido por princípio (todos existem na CMED 2026-10-09).
COMERCIAL = {
    "losartana": "cozaar", "hidroclorotiazida": "clorana", "anlodipino": "norvasc",
    "enalapril": "renitec", "atenolol": "atenopress", "furosemida": "lasix",
    "espironolactona": "aldactone", "metformina": "glifage", "glibenclamida": "daonil",
    "sinvastatina": "vaslip", "atorvastatina": "lipitor", "varfarina": "marevan",
    "acido acetilsalicilico": "aspirina", "clopidogrel": "plaq", "omeprazol": "losec",
    "clonazepam": "rivotril", "diazepam": "valium", "diclofenaco": "voltaren",
    "ibuprofeno": "alivium", "levotiroxina": "euthyrox",
}


def test_lista_cobre_os_vinte():
    assert set(COMERCIAL) == set(PRINCIPIOS)


@pytest.mark.parametrize("principio,comercial", COMERCIAL.items())
def test_por_nome_comercial(principio, comercial):
    r = normalizar(comercial)
    assert r.encontrado, comercial
    assert principio in r.principio_ativo
    assert r.nome_comercial == comercial
    assert r.fonte.startswith("CMED ")


@pytest.mark.parametrize("principio", PRINCIPIOS)
def test_por_principio(principio):
    r = normalizar(principio)
    assert r.encontrado
    assert r.principio_ativo == [principio]


@pytest.mark.parametrize("principio", PRINCIPIOS)
def test_com_erro_de_digitacao_leve(principio):
    # troca duas letras do meio: "losartana" -> "losatrana"
    meio = len(principio) // 2
    errado = principio[: meio - 1] + principio[meio] + principio[meio - 1] + principio[meio + 1:]
    r = normalizar(errado)
    assert r.encontrado, errado
    assert r.principio_ativo == [principio]


def test_acento_e_maiuscula_nao_importam():
    assert normalizar("ÁCIDO ACETILSALICÍLICO").principio_ativo == ["acido acetilsalicilico"]


def test_mesmo_principio_nomes_diferentes():
    assert normalizar("Glifage").principio_ativo == normalizar("Glucophage").principio_ativo == ["metformina"]
    assert normalizar("AAS").principio_ativo == normalizar("Aspirina").principio_ativo == ["acido acetilsalicilico"]


@pytest.mark.parametrize("texto,conc", [
    ("Glifage 850mg", "850 mg"),
    ("Rivotril 2 mg", "2 mg"),
    ("clonazepam 2,5 mg/ml", "2,5 mg/ml"),
    ("levotiroxina 25 mcg", "25 mcg"),
    ("caixa com 30 comprimidos de atenolol 50 mg", "50 mg"),
])
def test_extrai_concentracao(texto, conc):
    r = normalizar(texto)
    assert r.encontrado
    assert r.concentracao == conc


def test_sem_concentracao():
    assert normalizar("losartana").concentracao is None


def test_palavras_de_forma_sao_ignoradas():
    r = normalizar("Losartana Potássica 50 mg comprimidos revestidos")
    assert r.principio_ativo == ["losartana"] and r.concentracao == "50 mg"


@pytest.mark.parametrize("texto", [
    "losartana + hidroclorotiazida",
    "losartana e hidroclorotiazida",
    "losartana hidroclorotiazida 50 mg",
    "Hyzaar 50 + 12,5 mg",
])
def test_associacao_devolve_os_dois_principios(texto):
    assert normalizar(texto).principio_ativo == ["hidroclorotiazida", "losartana"]


def test_associacao_nao_descarta_remedio():
    assert normalizar("varfarina aas").principio_ativo == ["acido acetilsalicilico", "varfarina"]


@pytest.mark.parametrize("texto", ["paracetamol", "xyz", "", "30 comprimidos", "esomeprazol"])
def test_desconhecido_nao_e_encontrado(texto):
    # esomeprazol parece omeprazol, mas são remédios diferentes: não pode virar um pelo outro.
    r = normalizar(texto)
    assert not r.encontrado
    assert r.principio_ativo == []
