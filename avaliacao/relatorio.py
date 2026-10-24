"""Relatório para o pitch (spec avaliacao §7): junta o relatório mais recente de cada conjunto em resumo.md.

Uso:
    python -m avaliacao.relatorio
"""
import json
import sys
from pathlib import Path

from avaliacao.conjuntos import CONJUNTOS
from avaliacao.executar import RELATORIOS, _formatar_valor


def mais_recentes(pasta: Path) -> dict[str, dict]:
    por_conjunto = {}
    for caminho in sorted(pasta.glob("*_*.json")):   # nome começa pela data: o último vence
        rel = json.loads(caminho.read_text(encoding="utf-8"))
        if rel.get("conjunto") in CONJUNTOS:
            por_conjunto[rel["conjunto"]] = rel
    return por_conjunto


def montar(rels: dict[str, dict]) -> str:
    linhas = [
        "# Avaliação — resumo para o pitch",
        "",
        "| Conjunto | Prioridade | n (reais) | Meta | Resultado | Status | Data |",
        "|---|---|---|---|---|---|---|",
    ]
    for nome, conjunto in CONJUNTOS.items():
        rel = rels.get(nome)
        if rel is None:
            linhas.append(f"| `{nome}` | {conjunto.prioridade} | — | {conjunto.meta_texto} | não rodado | — | — |")
            continue
        linhas.append(f"| `{nome}` | {rel['prioridade']} | {rel['n']} ({rel['n_real']}) | {rel['meta']} | "
                      f"{_formatar_valor(rel)} | {rel['status']} | {rel['data'][:10]} |")

    modelos = sorted({f"{k}={v}" for r in rels.values() for k, v in r["modelos"].items() if k.startswith("LLM_")})
    custos = {n: r["custo_medio_usd"] for n, r in rels.items() if r.get("custo_medio_usd")}
    total = sum(r["n"] for r in rels.values())
    reais = sum(r["n_real"] for r in rels.values())
    linhas += [
        "",
        "## Observações obrigatórias",
        "",
        f"- Modelos da API da OpenAI: {', '.join(modelos) or 'nenhum conjunto com modelo rodado ainda'}.",
        "- Custo médio por caso: " + (", ".join(f"{n} US$ {c:.4f}" for n, c in custos.items())
                                      or "não calculado (defina PRECO_USD_MTOK_ENTRADA e _SAIDA)") + ".",
        "- Tabelas clínicas, pares e relatos foram gerados e conferidos com LLM no regional, sem revisão de "
        "profissional. Os pares foram gerados às cegas (o gerador não viu as tabelas do sistema).",
        f"- Casos reais: {reais} de {total}; os demais foram feitos pelo time (AV-D1) e são separados nos relatórios.",
        "- O guardrail é julgado por leitura humana de C com segunda leitura de um subagente (AV-D2), não pelo "
        "próprio Auditor.",
        "- O conjunto `relatos` não entra aqui enquanto a AV-D4 estiver aberta (ver specs/avaliacao/discussao.md).",
    ]
    return "\n".join(linhas) + "\n"


def main() -> int:
    rels = mais_recentes(RELATORIOS)
    (RELATORIOS / "resumo.md").write_text(montar(rels), encoding="utf-8")
    print(f"resumo.md com {len(rels)} conjunto(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
