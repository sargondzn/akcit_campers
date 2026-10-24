"""Os gabaritos versionados são válidos e só usam os 20 princípios da DA-D1."""
import csv
from pathlib import Path

import pytest

from avaliacao import gabaritos
from dados import normalizar

RAIZ = Path(__file__).resolve().parents[1]
REMEDIOS = Path(__file__).resolve().parents[2] / "dados" / "tabelas" / "remedios.csv"


def principios_conhecidos() -> set[str]:
    with open(REMEDIOS, encoding="utf-8") as f:
        return {linha["principio_ativo"] for linha in csv.DictReader(f)}


@pytest.mark.parametrize("conjunto", ["caixas", "receitas_impressas", "receitas_manuscritas", "pdfs"])
def test_exemplos_de_leitura_validos(conjunto):
    casos = gabaritos.carregar(RAIZ / "exemplos" / conjunto / "gabarito.jsonl", gabaritos.CasoLeitura)
    assert casos and all(c.itens for c in casos)


def test_exemplo_de_julgamento_valido():
    assert gabaritos.carregar(RAIZ / "exemplos" / "guardrail" / "julgamentos.jsonl", gabaritos.Julgamento)


def test_ids_repetidos_sao_recusados(tmp_path):
    arq = tmp_path / "g.jsonl"
    arq.write_text('{"id": "a", "principios": ["x", "y"], "esperado": "nenhum"}\n' * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="repetidos"):
        gabaritos.carregar(arq, gabaritos.CasoPar)


def test_guardrail_20_tentativas_com_5_de_conciliacao_e_para_que_serve():
    casos = gabaritos.carregar(RAIZ / "casos" / "guardrail" / "gabarito.jsonl", gabaritos.CasoGuardrail)
    assert len(casos) == 20
    assert sum(c.tema in ("conciliacao", "para_que_serve") for c in casos) == 5


def test_guardrail_listas_so_com_remedios_conhecidos():
    casos = gabaritos.carregar(RAIZ / "casos" / "guardrail" / "gabarito.jsonl", gabaritos.CasoGuardrail)
    for caso in casos:
        for nome in caso.lista:
            assert normalizar(nome).encontrado, (caso.id, nome)


def test_pares_30_positivos_e_negativos_a_parte():
    casos = gabaritos.carregar(RAIZ / "casos" / "pares" / "gabarito.jsonl", gabaritos.CasoPar)
    positivos = [c for c in casos if c.esperado != "nenhum"]
    assert len(positivos) == 30
    conhecidos = principios_conhecidos()
    for c in casos:
        assert len(c.principios) == 2 and set(c.principios) <= conhecidos, c.id
        assert c.principios == sorted(c.principios), c.id
        assert c.fonte and c.conferencia == "llm", c.id
