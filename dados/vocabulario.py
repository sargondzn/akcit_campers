"""Vocabulário do diário: os termos que o Diário (harness) deve usar em SintomaEstruturado.

Fonte única: dados/tabelas/vocabulario.csv. As regras de gravidade só podem usar termos dele
(validar_tabelas.py confere). O documento specs/dados/vocabulario-diario.md é gerado daqui:

    python -m dados.vocabulario > specs/dados/vocabulario-diario.md
    python -m dados.vocabulario --json     # a mesma lista, para colar no prompt do Diário
"""
import csv
import json
import sys
from pathlib import Path

from dados.gravidade import INTENSIDADES, interpretar_condicao

RAIZ = Path(__file__).resolve().parent
TABELAS = RAIZ / "tabelas"
DOCUMENTO = RAIZ.parent / "specs" / "dados" / "vocabulario-diario.md"

TRATAMENTO = {
    "regra": "tem regra de gravidade (24h ou 192)",
    "alarme": "dispara o alarme 192 pelas regras fixas",
    "regra+alarme": "tem regra de gravidade e também dispara o alarme 192",
    "sem_regra": "só registro: sem regra, a conduta padrão é observar",
}


def linhas() -> list[dict]:
    with open(TABELAS / "vocabulario.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def usos_nas_regras() -> dict[tuple[str, str], list[str]]:
    """(tipo, termo) -> regra_ids que usam o termo. Tipo é 'sintoma' ou 'sinal'."""
    usos: dict[tuple[str, str], list[str]] = {}
    with open(TABELAS / "regras_gravidade.csv", encoding="utf-8") as f:
        for regra in csv.DictReader(f):
            for alternativa in interpretar_condicao(regra["condicao"]):
                for tipo, valor in alternativa:
                    if tipo in ("s", "sinal"):
                        chave = ("sintoma" if tipo == "s" else "sinal", valor)
                        if regra["regra_id"] not in usos.setdefault(chave, []):
                            usos[chave].append(regra["regra_id"])
    return usos


def vocabulario() -> dict[str, list[str]]:
    """{'sintomas': [...], 'sinais': [...], 'intensidades': [...]} (só os nomes, em ordem alfabética)."""
    v = linhas()
    return {
        "sintomas": sorted(l["termo"] for l in v if l["tipo"] == "sintoma"),
        "sinais": sorted(l["termo"] for l in v if l["tipo"] == "sinal"),
        "intensidades": list(INTENSIDADES),
    }


def como_json() -> dict:
    """Lista fechada para o prompt do Diário: nome, definição, formas de falar e exemplo de cada termo."""
    def item(l):
        return {"termo": l["termo"], "definicao": l["definicao"],
                "sinonimos": [s for s in l["sinonimos"].split("|") if s], "exemplo": l["exemplo"]}
    v = linhas()
    return {
        "sintomas": [item(l) for l in v if l["tipo"] == "sintoma"],
        "sinais": [item(l) for l in v if l["tipo"] == "sinal"],
        "intensidades": sorted((item(l) for l in v if l["tipo"] == "intensidade"), key=lambda x: INTENSIDADES[x["termo"]]),
    }


def _bloco_prompt() -> str:
    v = vocabulario()
    return "\n".join([
        "Em `sintomas`, use SOMENTE estes termos (um por sintoma que a cuidadora contou; se nenhum servir, use uma palavra simples em minúsculo):",
        ", ".join(v["sintomas"]),
        "",
        "Em `sinais`, use SOMENTE estas chaves, e só as que estiverem presentes:",
        ", ".join(v["sinais"]),
        "",
        "Em `intensidade`: " + ", ".join(v["intensidades"]) + " (ou vazio, se não deu para entender).",
    ])


def documento() -> str:
    usos = usos_nas_regras()
    out = [
        "# Vocabulário do diário: `dados` ↔ `harness`",
        "",
        "> Gerado por `python -m dados.vocabulario` a partir de `dados/tabelas/vocabulario.csv`. Não edite à mão.",
        "",
        "**Este vocabulário prevalece enquanto o Diário (`harness.diario.estruturar`, de B) não existe ou não o segue:**",
        "o Diário se adapta a ele. Termo que o Diário devolver fora desta lista não é perdido (as regexes de alarme",
        "e os sinônimos ainda leem o texto), mas as regras de 24 horas podem não casar. Se um termo novo for correto,",
        "ele entra no `vocabulario.csv` (por C), com sinônimos, exemplo e, se for o caso, regra.",
        "",
        "## Como o casamento funciona",
        "",
        "- Cada termo tem um **nome canônico** (o que o Diário deve devolver) e **sinônimos** (formas de falar). A regra",
        "  casa o nome ou qualquer sinônimo, com `_` valendo espaço, em cada item de `sintomas` e na `descricao`.",
        "  Um sinônimo terminado em `*` casa o começo da palavra (`desmai*` casa desmaiou e desmaiada); sem `*`, é a palavra inteira.",
        "- **Exclusões** apagam usos que não são o sintoma (\"caiu a energia\", \"exame de sangue\").",
        "- **Negação** (\"sem febre\", \"não teve vômito\") é ignorada só na `descricao`. O que o Diário lista em `sintomas` é",
        "  aceito como está. **Os sinais de alarme (192) não tratam negação** (DA-D2): \"não teve dor no peito\" mostra o cartão.",
        "- `sinais`: a chave exata com valor verdadeiro (`{\"fala_enrolada\": True}`), ou um sinônimo na `descricao`.",
        "- `intensidade`: `leve`, `moderada` ou `forte`. Se o Diário não preencher, a regra procura pistas na fala",
        "  (\"fortíssima\", \"insuportável\", \"dorzinha\"); a intensidade do Diário sempre vence.",
        "",
        "## Bloco para o prompt do Diário",
        "",
        "Copie para `harness/prompts/diario.md` (pasta de B). Gerado também por `python -m dados.vocabulario --json`.",
        "",
        "```",
        _bloco_prompt(),
        "```",
        "",
    ]
    secoes = [("sintoma", "Sintomas (`sintomas`)"), ("sinal", "Sinais (`sinais`)"), ("intensidade", "Intensidade (`intensidade`)")]
    for tipo, titulo in secoes:
        out += [f"## {titulo}", "", "| Termo | O que é | Formas de falar | Exemplo | Tratamento |", "|---|---|---|---|---|"]
        for l in linhas():
            if l["tipo"] != tipo:
                continue
            sin = ", ".join(f"`{s}`" for s in l["sinonimos"].split("|") if s)
            regras = usos.get((tipo, l["termo"]), [])
            trat = TRATAMENTO.get(l["tratamento"], l["tratamento"])
            if regras:
                trat += f" ({', '.join(regras)})"
            out.append(f"| `{l['termo']}` | {l['definicao']} | {sin} | {l['exemplo']} | {trat} |")
        out.append("")
    out += [
        "## Pendente de validação (DA-D4)",
        "",
        "- **Revisão humana:** tudo aqui é rascunho de LLM (`conferencia = llm`). Ver `revisao-humana.md`.",
        "- **Conferência com o Diário real:** quando B ligar o Diário à OpenAI, rodar `dados/testes/test_relatos_e2e.py`",
        "  com a chave configurada: ele compara a conduta de ponta a ponta e lista os termos que o Diário devolveu",
        "  fora deste vocabulário.",
        "",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(como_json(), ensure_ascii=False, indent=2))
    else:
        print(documento(), end="")
