"""info_remedio (C8, 24/10): princípio ativo -> para que serve, Farmácia Popular, tipo e validade da receita.

Determinístico: só tabelas com fonte (indicacoes.csv, farmacia_popular.csv, remedios.csv, tipos_receita.csv).
Sem linha em indicacoes.csv devolve None, e o harness diz "ainda não tenho essa informação".
"""
import csv
from functools import lru_cache
from pathlib import Path

from contratos.dados import InfoRemedio
from dados.texto import normalizar_texto

TABELAS = Path(__file__).resolve().parent / "tabelas"
RESTRICAO = {"simples": 0, "antimicrobiano": 1, "controle_especial": 2}


def _ler(nome: str) -> list[dict]:
    with open(TABELAS / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def _tabelas():
    indicacoes = {l["principio_ativo"]: l for l in _ler("indicacoes.csv")}
    programa: dict[str, list[dict]] = {}
    for l in _ler("farmacia_popular.csv"):
        programa.setdefault(l["principio_ativo"], []).append(l)
    tipos_por_principio: dict[str, str] = {}
    for l in _ler("remedios.csv"):
        if ";" in l["principio_ativo"]:
            continue  # associação: o tipo vale para os componentes isolados
        atual = tipos_por_principio.get(l["principio_ativo"], "simples")
        if RESTRICAO[l["tipo_receita"]] >= RESTRICAO[atual]:
            tipos_por_principio[l["principio_ativo"]] = l["tipo_receita"]
    validades = {l["tipo_receita"]: l for l in _ler("tipos_receita.csv")}
    return indicacoes, programa, tipos_por_principio, validades


def info_remedio(principio_ativo: str) -> InfoRemedio | None:
    indicacoes, programa, tipos_por_principio, validades = _tabelas()
    principio = normalizar_texto(principio_ativo)
    indicacao = indicacoes.get(principio)
    if indicacao is None:
        return None

    fontes = [indicacao["fonte"]]
    conferencias = [indicacao["conferencia"]]

    linhas = [l for l in programa.get(principio, []) if l["gratuito"] == "sim"]
    detalhe, documentos = None, []
    if linhas:
        detalhe = linhas[0]["indicacao_programa"]
        documentos = [d.strip() for d in linhas[0]["documentos"].split(";") if d.strip()]
        fontes.append(linhas[0]["fonte"])
        conferencias += [l["conferencia"] for l in linhas]

    tipo = tipos_por_principio.get(principio)
    validade = None
    if tipo is not None and tipo in validades:
        v = validades[tipo]
        validade = int(v["validade_dias"]) if v["validade_dias"].strip() else None
        fontes.append(v["fonte"])
        conferencias.append(v["conferencia"])

    return InfoRemedio(
        principio_ativo=principio,
        para_que_serve=indicacao["para_que_serve"],
        farmacia_popular=bool(linhas),
        farmacia_popular_detalhe=detalhe,
        documentos_farmacia_popular=documentos,
        tipo_receita=tipo,
        validade_receita_dias=validade,
        fonte="; ".join(dict.fromkeys(fontes)),
        conferencia="profissional" if all(c == "profissional" for c in conferencias) else "llm",
    )
