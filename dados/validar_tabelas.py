"""Confere colunas, valores e referências entre as tabelas. Roda junto com os testes.

Uso: python -m dados.validar_tabelas   (sai com código 1 se houver erro)
"""
import csv
import re
import sys
from pathlib import Path

from dados.gravidade import interpretar_condicao
from dados.texto import normalizar_texto

TABELAS = Path(__file__).resolve().parent / "tabelas"
COLUNAS = {
    "remedios.csv": ["principio_ativo", "nome_comercial", "concentracao", "forma", "registro_anvisa", "fonte"],
    "sinonimos.csv": ["termo", "principio_ativo"],
    "interacoes.csv": ["principio_a", "principio_b", "gravidade", "descricao", "fonte", "conferencia"],
    "classes.csv": ["principio_ativo", "classe", "duplicidade_relevante", "fonte", "conferencia"],
    "cbmpi.csv": ["principio_ativo", "criterio", "motivo", "fonte", "conferencia"],
    "sinais_alarme.csv": ["regra_id", "padrao", "descricao", "fonte", "conferencia"],
    "regras_gravidade.csv": ["regra_id", "ordem", "condicao", "nivel", "motivo", "fonte", "conferencia"],
}
CONFERENCIA = {"llm", "profissional"}


def _ler(nome, erros):
    caminho = TABELAS / nome
    if not caminho.exists():
        erros.append(f"{nome}: arquivo não existe")
        return []
    with open(caminho, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        if leitor.fieldnames != COLUNAS[nome]:
            erros.append(f"{nome}: colunas {leitor.fieldnames} diferem de {COLUNAS[nome]}")
            return []
        return list(leitor)


def validar() -> list[str]:
    erros: list[str] = []
    t = {nome: _ler(nome, erros) for nome in COLUNAS}

    # princípios conhecidos: os isolados de remedios.csv (associações valem pelos componentes)
    conhecidos = {p for l in t["remedios.csv"] for p in l["principio_ativo"].split(";")}

    def princ(nome, valor, ctx):
        if valor != normalizar_texto(valor):
            erros.append(f"{nome}: {ctx} {valor!r} não está em minúsculo e sem acento")
        if valor not in conhecidos:
            erros.append(f"{nome}: {ctx} {valor!r} não existe em remedios.csv")

    for l in t["sinonimos.csv"]:
        for p in l["principio_ativo"].split(";"):
            princ("sinonimos.csv", p, "principio_ativo")

    vistos = set()
    for l in t["interacoes.csv"]:
        a, b = l["principio_a"], l["principio_b"]
        princ("interacoes.csv", a, "principio_a"); princ("interacoes.csv", b, "principio_b")
        if not a < b:
            erros.append(f"interacoes.csv: par fora de ordem alfabética ou igual: {a}, {b}")
        if (a, b) in vistos:
            erros.append(f"interacoes.csv: par repetido: {a}, {b}")
        vistos.add((a, b))
        if l["gravidade"] not in ("alta", "moderada", "baixa"):
            erros.append(f"interacoes.csv: gravidade inválida em {a}+{b}: {l['gravidade']!r}")

    classes = set()
    for l in t["classes.csv"]:
        princ("classes.csv", l["principio_ativo"], "principio_ativo")
        classes.add(l["principio_ativo"])
        if l["duplicidade_relevante"] not in ("sim", "nao"):
            erros.append(f"classes.csv: duplicidade_relevante inválida em {l['principio_ativo']}")
    for p in sorted(conhecidos - classes):
        erros.append(f"classes.csv: {p!r} está em remedios.csv e não tem classe")

    for l in t["cbmpi.csv"]:
        princ("cbmpi.csv", l["principio_ativo"], "principio_ativo")

    ids = set()
    for l in t["sinais_alarme.csv"]:
        try:
            re.compile(l["padrao"])
        except re.error as e:
            erros.append(f"sinais_alarme.csv: regex inválida em {l['regra_id']}: {e}")
        if l["regra_id"] in ids:
            erros.append(f"sinais_alarme.csv: regra_id repetido: {l['regra_id']}")
        ids.add(l["regra_id"])

    ordens = set()
    for l in t["regras_gravidade.csv"]:
        if l["nivel"] not in ("ligue_192", "atendimento_24h", "observar"):
            erros.append(f"regras_gravidade.csv: nivel inválido em {l['regra_id']}: {l['nivel']!r}")
        if not l["ordem"].isdigit() or l["ordem"] in ordens:
            erros.append(f"regras_gravidade.csv: ordem inválida ou repetida em {l['regra_id']}: {l['ordem']!r}")
        ordens.add(l["ordem"])
        try:
            interpretar_condicao(l["condicao"])
        except ValueError as e:
            erros.append(f"regras_gravidade.csv: condicao de {l['regra_id']}: {e}")
        if l["regra_id"] in ids:
            erros.append(f"regras_gravidade.csv: regra_id repetido: {l['regra_id']}")
        ids.add(l["regra_id"])

    # fonte e conferencia preenchidas em toda linha clínica
    for nome in ("interacoes.csv", "classes.csv", "cbmpi.csv", "sinais_alarme.csv", "regras_gravidade.csv"):
        for i, l in enumerate(t[nome], start=2):
            if not l["fonte"].strip():
                erros.append(f"{nome} linha {i}: fonte vazia")
            if l["conferencia"] not in CONFERENCIA:
                erros.append(f"{nome} linha {i}: conferencia {l['conferencia']!r} (esperado llm ou profissional)")
    return erros


if __name__ == "__main__":
    problemas = validar()
    print("\n".join(problemas) if problemas else "tabelas ok")
    sys.exit(1 if problemas else 0)
