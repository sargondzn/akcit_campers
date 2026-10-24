"""info_remedio (C8): para que serve, Farmácia Popular, tipo e validade da receita. Só tabela com fonte."""
import csv

import pytest

from contratos.dados import InfoRemedio
from dados.etl.cmed import PRINCIPIOS
from dados.info_remedio import info_remedio
from dados.validar_tabelas import TABELAS, _validar_info_remedio

# Elenco oficial do Programa Farmácia Popular (Ministério da Saúde, atualizado em 31/08/2026) ∩ os 20 remédios.
NO_PROGRAMA = {"anlodipino", "atenolol", "enalapril", "espironolactona", "furosemida", "glibenclamida",
               "hidroclorotiazida", "losartana", "metformina", "sinvastatina"}


@pytest.mark.parametrize("principio", PRINCIPIOS)
def test_todo_remedio_tem_para_que_serve_e_fonte(principio):
    info = info_remedio(principio)
    assert isinstance(info, InfoRemedio)
    assert info.principio_ativo == principio
    assert info.para_que_serve.strip() and info.fonte.strip()
    assert info.conferencia == "llm"


@pytest.mark.parametrize("principio", sorted(NO_PROGRAMA))
def test_remedios_do_programa(principio):
    info = info_remedio(principio)
    assert info.farmacia_popular is True
    assert info.farmacia_popular_detalhe
    assert "a receita" in info.documentos_farmacia_popular
    assert any("CPF" in d for d in info.documentos_farmacia_popular)
    assert "Farmácia Popular" in info.fonte


@pytest.mark.parametrize("principio", sorted(set(PRINCIPIOS) - NO_PROGRAMA))
def test_remedios_fora_do_programa(principio):
    info = info_remedio(principio)
    assert info.farmacia_popular is False
    assert info.farmacia_popular_detalhe is None
    assert info.documentos_farmacia_popular == []


def test_indicacao_do_programa():
    assert info_remedio("losartana").farmacia_popular_detalhe == "hipertensão"
    assert info_remedio("metformina").farmacia_popular_detalhe == "diabetes"
    assert info_remedio("sinvastatina").farmacia_popular_detalhe.startswith("dislipidemia")


def test_para_que_serve_de_exemplos():
    assert info_remedio("losartana").para_que_serve == "controlar a pressão alta"
    assert info_remedio("sinvastatina").para_que_serve.startswith("baixar o colesterol")


def test_frase_do_harness_fica_natural():
    # harness/frases: "A <nome> costuma ser usada para <para_que_serve>."
    info = info_remedio("metformina")
    frase = f"A metformina costuma ser usada para {info.para_que_serve}."
    assert frase == "A metformina costuma ser usada para controlar o açúcar no sangue no diabetes tipo 2."


@pytest.mark.parametrize("principio,tipo", [("clonazepam", "controle_especial"), ("diazepam", "controle_especial"),
                                            ("losartana", "simples"), ("varfarina", "simples")])
def test_tipo_de_receita(principio, tipo):
    assert info_remedio(principio).tipo_receita == tipo


def test_validade_acompanha_o_tipo():
    controle, simples = info_remedio("clonazepam"), info_remedio("losartana")
    assert controle.validade_receita_dias == 30
    assert simples.validade_receita_dias is None or simples.validade_receita_dias > 0
    assert controle.validade_receita_dias is not None


@pytest.mark.parametrize("nome", ["paracetamol", "", "xyz", "hidroclorotiazida;losartana", "dipirona"])
def test_desconhecido_devolve_none(nome):
    assert info_remedio(nome) is None


def test_aceita_maiuscula_e_acento():
    assert info_remedio("LOSARTANA").principio_ativo == "losartana"
    assert info_remedio("Ácido Acetilsalicílico").principio_ativo == "acido acetilsalicilico"


def test_resultado_e_serializavel():
    assert info_remedio("losartana").model_dump()["farmacia_popular"] is True


def test_nenhuma_frase_cita_dose():
    import re
    for p in PRINCIPIOS:
        assert not re.search(r"\d+\s*(mg|mcg|ml|g)\b|\bdose", info_remedio(p).para_que_serve.lower()), p


# --- o validador pega tabela ruim -----------------------------------------------------------------

def _tabelas(**mudancas):
    def ler(nome):
        with open(TABELAS / nome, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    t = {n: ler(n) for n in ("remedios.csv", "indicacoes.csv", "farmacia_popular.csv", "tipos_receita.csv")}
    t.update(mudancas)
    return t, {p for l in t["remedios.csv"] for p in l["principio_ativo"].split(";")}


def test_validador_aceita_as_tabelas_atuais():
    t, conhecidos = _tabelas()
    assert _validar_info_remedio(t, conhecidos) == []


@pytest.mark.parametrize("campo,valor,trecho", [
    ("indicacoes.csv|para_que_serve|losartana", "controle a pressão", "infinitivo"),
    ("indicacoes.csv|para_que_serve|losartana", "controlar a pressão com 50 mg", "dose"),
    ("indicacoes.csv|principio_ativo|losartana", "paracetamol", "não existe em remedios.csv"),
    ("farmacia_popular.csv|gratuito|losartana", "talvez", "gratuito inválido"),
    ("farmacia_popular.csv|documentos|losartana", "", "documentos"),
    ("tipos_receita.csv|validade_dias|controle_especial", "-3", "validade_dias inválida"),
])
def test_validador_pega_tabela_ruim(campo, valor, trecho):
    arquivo, coluna, chave = campo.split("|")
    t, conhecidos = _tabelas()
    alvo = next(l for l in t[arquivo] if chave in (l.get("principio_ativo"), l.get("tipo_receita")))
    alvo[coluna] = valor
    erros = _validar_info_remedio(t, conhecidos)
    assert any(trecho in e for e in erros), erros


def test_validador_exige_indicacao_para_todo_remedio():
    t, conhecidos = _tabelas()
    t["indicacoes.csv"] = [l for l in t["indicacoes.csv"] if l["principio_ativo"] != "varfarina"]
    assert any("varfarina" in e and "para que serve" in e for e in _validar_info_remedio(t, conhecidos))


def test_validador_exige_linha_para_cada_tipo_usado():
    t, conhecidos = _tabelas()
    t["tipos_receita.csv"] = [l for l in t["tipos_receita.csv"] if l["tipo_receita"] != "controle_especial"]
    assert any("controle_especial" in e for e in _validar_info_remedio(t, conhecidos))
