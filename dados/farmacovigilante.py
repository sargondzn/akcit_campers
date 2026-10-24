"""checar_lista (C3): alertas sobre a lista de remédios, a partir das tabelas curadas."""
import csv
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from contratos.dados import Alerta, ItemParaChecar

TABELAS = Path(__file__).resolve().parent / "tabelas"
ORDEM_GRAVIDADE = {"alta": 0, "moderada": 1, "baixa": 2, None: 3}
ORDEM_TIPO = {"duplicidade_principio": 0, "interacao": 1, "duplicidade_classe": 2, "cbmpi": 3}


def _ler(nome: str) -> list[dict]:
    with open(TABELAS / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def _tabelas():
    interacoes = {(l["principio_a"], l["principio_b"]): l for l in _ler("interacoes.csv")}
    classes = {l["principio_ativo"]: l for l in _ler("classes.csv")}
    cbmpi = {l["principio_ativo"]: l for l in _ler("cbmpi.csv")}
    return interacoes, classes, cbmpi


def checar_lista(itens: list[ItemParaChecar]) -> list[Alerta]:
    interacoes, classes, cbmpi = _tabelas()
    alertas: dict[tuple, Alerta] = {}

    def adicionar(chave, alerta):
        alertas.setdefault(chave, alerta)  # sem repetição

    # item_ids por princípio (um item pode ser uma associação com 2 princípios)
    donos: dict[str, list[str]] = {}
    for item in itens:
        for principio in dict.fromkeys(item.principio_ativo):
            donos.setdefault(principio, []).append(item.item_id)

    # 1. Mesmo princípio em 2 ou mais itens (nomes comerciais diferentes, por exemplo)
    for principio, ids in donos.items():
        if len(set(ids)) > 1:
            adicionar(("dup", principio), Alerta(
                tipo="duplicidade_principio", item_ids=sorted(set(ids)), principios=[principio],
                gravidade="alta",
                descricao=f"Há mais de um item com o mesmo remédio ({principio}), talvez com nomes diferentes. "
                          "Tomar os dois pode causar overdose. Converse com o médico ou o farmacêutico.",
                fonte="regra fixa: mesmo princípio ativo em mais de um item (CMED); sem tabela clínica", conferencia="llm"))

    presentes = sorted(donos)
    # 2. Interações
    for a, b in combinations(presentes, 2):
        linha = interacoes.get((a, b))
        if linha:
            adicionar(("int", a, b), Alerta(
                tipo="interacao", item_ids=sorted(set(donos[a]) | set(donos[b])), principios=[a, b],
                gravidade=linha["gravidade"], descricao=linha["descricao"],
                fonte=linha["fonte"], conferencia=linha["conferencia"]))

    # 3. Duplicidade de classe (princípios diferentes, mesma classe, duplicidade relevante)
    por_classe: dict[str, list[str]] = {}
    for principio in presentes:
        linha = classes.get(principio)
        if linha and linha["duplicidade_relevante"] == "sim":
            por_classe.setdefault(linha["classe"], []).append(principio)
    for classe, principios in por_classe.items():
        if len(principios) > 1:
            ids = sorted({i for p in principios for i in donos[p]})
            adicionar(("cls", classe), Alerta(
                tipo="duplicidade_classe", item_ids=ids, principios=principios, gravidade="moderada",
                descricao=f"Estes remédios são da mesma classe ({classe}). Tomar mais de um pode somar os efeitos. "
                          "Converse com o médico ou o farmacêutico.",
                fonte=classes[principios[0]]["fonte"], conferencia=classes[principios[0]]["conferencia"]))

    # 4. CBMPI (inapropriados para idosos)
    for principio in presentes:
        linha = cbmpi.get(principio)
        if linha:
            adicionar(("cbmpi", principio), Alerta(
                tipo="cbmpi", item_ids=sorted(set(donos[principio])), principios=[principio],
                gravidade=None, descricao=linha["motivo"],
                fonte=linha["fonte"], conferencia=linha["conferencia"]))

    return sorted(alertas.values(), key=lambda a: (ORDEM_GRAVIDADE[a.gravidade], ORDEM_TIPO[a.tipo], a.principios))
