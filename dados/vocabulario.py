"""Vocabulário que o extrator (harness.diario.estruturar) deve usar em SintomaEstruturado.

Fonte única: as condições de regras_gravidade.csv. O documento specs/dados/vocabulario-diario.md
é gerado daqui:

    python -m dados.vocabulario > specs/dados/vocabulario-diario.md
"""
import csv
from pathlib import Path

from dados.gravidade import INTENSIDADES, interpretar_condicao

RAIZ = Path(__file__).resolve().parent
TABELAS = RAIZ / "tabelas"
DOCUMENTO = RAIZ.parent / "specs" / "dados" / "vocabulario-diario.md"


def vocabulario() -> dict[str, list[str]]:
    """{'sintomas': [...], 'sinais': [...], 'intensidades': [...]}, ordenados e sem repetição."""
    sintomas, sinais = set(), set()
    with open(TABELAS / "regras_gravidade.csv", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            for alternativa in interpretar_condicao(linha["condicao"]):
                for tipo, valor in alternativa:
                    if tipo == "s":
                        sintomas.add(valor)
                    elif tipo == "sinal":
                        sinais.add(valor)
    return {"sintomas": sorted(sintomas), "sinais": sorted(sinais), "intensidades": list(INTENSIDADES)}


def documento() -> str:
    v = vocabulario()
    linhas = [
        "# Vocabulário do diário: `dados` ↔ `harness`",
        "",
        "> Gerado por `python -m dados.vocabulario` a partir de `dados/tabelas/regras_gravidade.csv`. Não edite à mão.",
        "",
        "O `harness.diario.estruturar` (B) devolve um `SintomaEstruturado`; `avaliar_gravidade` (C) decide a conduta",
        "olhando estes termos. Se o extrator devolver outra palavra (por exemplo \"caiu no banheiro\" em vez de `queda`),",
        "a regra de 24 horas correspondente **não casa**. As regexes de alarme (192) rodam sobre o texto todo e não",
        "dependem deste vocabulário.",
        "",
        "## Como o casamento funciona",
        "",
        "- `sintomas`: cada termo é procurado, com `_` valendo espaço, no início de uma palavra da `descricao` ou dos `sintomas`.",
        "  Por isso um termo curto vale como prefixo: `desmai` casa `desmaio`, `desmaiou` e `desmaiada`.",
        "- `sinais`: precisa ser a chave exata, com valor verdadeiro (`{\"fala_enrolada\": True}`).",
        "- `intensidade`: `leve`, `moderada` ou `forte`; a regra pede \"igual ou maior\".",
        "- Negação não é tratada (DA-D2): \"sem febre\" ainda casa `febre`.",
        "",
        "## `sintomas`",
        "",
        *[f"- `{t}`" for t in v["sintomas"]],
        "",
        "## `sinais` (chave exata, valor verdadeiro)",
        "",
        *[f"- `{t}`" for t in v["sinais"]],
        "",
        "## `intensidade`",
        "",
        *[f"- `{t}`" for t in v["intensidades"]],
        "",
        "## Pendente de validação (DA-D4)",
        "",
        "Falta conferir se o que o extrator de B realmente devolve bate com esta lista. Depois que B integrar, rodar o",
        "conjunto `relatos` pelo caminho completo (`harness.diario.estruturar` → `avaliar_gravidade`) e comparar com o",
        "resultado de `avaliar_gravidade` sobre `SintomaEstruturado` montado à mão.",
        "",
    ]
    return "\n".join(linhas)


if __name__ == "__main__":
    print(documento(), end="")
