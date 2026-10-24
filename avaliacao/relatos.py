"""Avaliação de relatos de ponta a ponta: texto da cuidadora -> conduta (192, 24h ou observar).

Reproduz o fluxo do harness (spec harness §9): regras fixas de alarme sobre o texto; senão o Diário
estrutura o relato em um `SintomaEstruturado` e `avaliar_gravidade` decide. O Diário é plugável:

- `texto_cru`: não estrutura nada (`descricao = texto`); mede o que `dados` entrega sozinho.
- `oraculo(casos)`: devolve a ficha esperada do gabarito; mede só regras e vocabulário.
- `harness.diario.estruturar`: o Diário real (precisa de OPENAI_API_KEY); mede os dois lados juntos.

Uso:  medir(casos, texto_cru)
"""
import json
from collections import Counter
from pathlib import Path
from typing import Callable

from contratos.dados import Conduta, SintomaEstruturado
from dados.gravidade import avaliar_gravidade, detectar_alarme

GABARITO = Path(__file__).resolve().parent / "exemplos" / "relatos_e2e" / "gabarito.jsonl"
NIVEIS = ["observar", "atendimento_24h", "ligue_192"]  # do menos ao mais grave
GRAVIDADE = {n: i for i, n in enumerate(NIVEIS)}

Estruturador = Callable[[str], SintomaEstruturado]


def carregar(caminho: Path = GABARITO) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def texto_cru(texto: str) -> SintomaEstruturado:
    return SintomaEstruturado(descricao=texto)


def oraculo(casos: list[dict]) -> Estruturador:
    por_texto = {c["texto"]: c for c in casos}

    def estruturar(texto: str) -> SintomaEstruturado:
        c = por_texto[texto]
        return SintomaEstruturado(descricao=texto, sintomas=list(c["sintomas"]), intensidade=c["intensidade"],
                                  sinais={k: True for k in c["sinais"]})
    return estruturar


def pipeline(texto: str, estruturar: Estruturador) -> Conduta:
    """Alarme sobre o texto; senão estrutura e avalia (o `avaliar_gravidade` reaplica o alarme)."""
    return detectar_alarme(texto) or avaliar_gravidade(estruturar(texto))


def medir(casos: list[dict], estruturar: Estruturador) -> dict:
    """Acertos, matriz esperado->obtido e os ids de subtriagem (obtido menos grave que o esperado)
    e supertriagem (mais grave). Subtriagem é o erro perigoso."""
    matriz: Counter = Counter()
    sub, super_, certos = [], [], 0
    for c in casos:
        obtido = pipeline(c["texto"], estruturar).nivel
        esperado = c["nivel_esperado"]
        matriz[(esperado, obtido)] += 1
        if obtido == esperado:
            certos += 1
        elif GRAVIDADE[obtido] < GRAVIDADE[esperado]:
            sub.append(c["id"])
        else:
            super_.append(c["id"])
    return {"n": len(casos), "certos": certos, "subtriagem": sub, "supertriagem": super_,
            "matriz": {f"{e}->{o}": n for (e, o), n in sorted(matriz.items())}}


def resumo(nome: str, r: dict) -> str:
    return (f"{nome}: {r['certos']}/{r['n']} certos ({r['certos'] / r['n']:.0%}); "
            f"subtriagem {len(r['subtriagem'])}; supertriagem {len(r['supertriagem'])}")
