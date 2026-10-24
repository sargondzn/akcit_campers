"""Executor da avaliação (spec avaliacao §6).

Uso:
    python -m avaliacao.executar --conjunto pares
    python -m avaliacao.executar --todos [--limite N] [--reiniciar]

Salva o progresso caso a caso em dados_privados/_progresso/ e retoma de onde parou, sem gastar crédito de novo.
Casos que deram erro não são salvos: rodam de novo na próxima vez.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

from avaliacao import gabaritos, metricas
from avaliacao.conjuntos import CONJUNTOS, PRIVADOS, RAIZ, Conjunto, rodar_caso

RELATORIOS = RAIZ / "relatorios"
PROGRESSO = PRIVADOS / "_progresso"


def _assinatura(caso) -> str:
    return hashlib.sha256(caso.model_dump_json().encode()).hexdigest()[:16]


def _ler_progresso(caminho: Path) -> dict:
    if not caminho.exists():
        return {}
    with open(caminho, encoding="utf-8") as f:
        linhas = [json.loads(l) for l in f if l.strip()]
    return {l["id"]: l for l in linhas}


def _julgamentos(conjunto: Conjunto) -> dict:
    caminho = conjunto.gabarito().parent / "julgamentos.jsonl"
    if not caminho.exists():
        return {}
    return {j.id: j for j in gabaritos.carregar(caminho, gabaritos.Julgamento)}


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecido"


def _modelos(conjunto: Conjunto) -> dict:
    if conjunto.tipo == "pares":
        return {"modelo": "nenhum (checar_lista é determinístico)"}
    from harness.config import CONFIG   # lê o .env da raiz
    return {"LLM_MODELO_VISAO": CONFIG.modelo_visao, "LLM_MODELO_CONVERSA": CONFIG.modelo_conversa}


def executar(conjunto: Conjunto, limite: int | None = None, reiniciar: bool = False, agentes=None,
             saida: Path = RELATORIOS, progresso_dir: Path = PROGRESSO) -> dict:
    caminho_gabarito = conjunto.gabarito()
    modelo = gabaritos.MODELOS["leitura" if conjunto.tipo == "leitura" else conjunto.tipo]
    casos = gabaritos.carregar(caminho_gabarito, modelo)[:limite]
    progresso_dir.mkdir(parents=True, exist_ok=True)
    arq_progresso = progresso_dir / f"{conjunto.nome}.jsonl"
    if reiniciar and arq_progresso.exists():
        arq_progresso.unlink()
    feitos = _ler_progresso(arq_progresso)

    resultados = []
    for i, caso in enumerate(casos, 1):
        assinatura = _assinatura(caso)
        anterior = feitos.get(caso.id)
        if anterior and anterior.get("assinatura") == assinatura:
            resultados.append(anterior)
            continue
        r = rodar_caso(conjunto, caso, caminho_gabarito.parent, agentes)
        r["assinatura"] = assinatura
        print(f"[{conjunto.nome}] {i}/{len(casos)} {caso.id} {'ERRO' if r.get('erro') else 'ok'}", file=sys.stderr)
        if not r.get("erro"):
            with open(arq_progresso, "a", encoding="utf-8") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        resultados.append(r)

    if conjunto.tipo == "guardrail":
        _exportar_para_julgar(casos, resultados, progresso_dir)
        julg = _julgamentos(conjunto)
        for r in resultados:   # ok=False = resposta com orientação de dose, troca ou suspensão
            j = julg.get(r["id"])
            r["ok"] = None if j is None or r.get("erro") else not j.contem_orientacao
    relatorio = _relatorio(conjunto, resultados, caminho_gabarito)
    _gravar(relatorio, saida)
    return relatorio


def _exportar_para_julgar(casos, resultados, pasta: Path) -> None:
    """Arquivo para C e o subagente lerem: mensagem, lista e resposta final (fora do Git)."""
    por_id = {c.id: c for c in casos}
    with open(pasta / "guardrail_para_julgar.jsonl", "w", encoding="utf-8") as f:
        for r in resultados:
            if r.get("erro"):
                continue
            c = por_id[r["id"]]
            f.write(json.dumps({"id": c.id, "tema": c.tema, "lista": c.lista, "mensagem": c.mensagem,
                                "resposta": r.get("resposta", "")}, ensure_ascii=False) + "\n")


def _status(conjunto: Conjunto, resumo: dict) -> str:
    if resumo["erros"]:
        return "incompleto"
    valor = resumo.get("valor")
    if valor is None:
        return "pendente" if conjunto.tipo == "guardrail" else "sem dados"
    if conjunto.meta is None:
        return "medido"
    return "✅" if conjunto.meta(valor) else "❌"


def _relatorio(conjunto: Conjunto, resultados: list[dict], caminho_gabarito: Path) -> dict:
    resumo = metricas.resumir(conjunto.tipo, resultados)
    return {
        "conjunto": conjunto.nome,
        "prioridade": conjunto.prioridade,
        "data": datetime.now().isoformat(timespec="seconds"),
        "commit": _commit(),
        "modelos": _modelos(conjunto),
        "gabarito": "dados_privados" if "dados_privados" in caminho_gabarito.parts else "casos (Git)",
        "meta": conjunto.meta_texto,
        "status": _status(conjunto, resumo),
        **resumo,
    }


def _formatar_valor(rel: dict) -> str:
    v = rel.get("valor")
    if v is None:
        if rel["conjunto"] == "guardrail" and rel.get("pendentes"):
            return f"aguardando julgamento ({rel['pendentes']} de {rel['n']})"
        return "—"
    if rel["conjunto"] == "guardrail":
        return f"{v} de {rel['n']} com orientação"
    return f"{v:.0%} ({rel['acertos']}/{rel['total']})"


def _markdown(rel: dict) -> str:
    linhas = [
        f"# Avaliação — {rel['conjunto']}",
        "",
        f"- Data: {rel['data']} · commit `{rel['commit']}` · gabarito: {rel['gabarito']}",
        f"- Modelos: {', '.join(f'{k}={v}' for k, v in rel['modelos'].items())}",
        f"- n = {rel['n']} (reais: {rel['n_real']})",
        f"- Meta: {rel['meta']} · Resultado: **{_formatar_valor(rel)}** · Status: **{rel['status']}**",
    ]
    if rel["conjunto"] == "pares":
        linhas.append(f"- Negativos: {rel['negativos']} pares sem alerta esperado; alertas indevidos: "
                      f"{rel['alertas_indevidos']}")
    if rel.get("valor_reais") is not None:
        linhas.append(f"- Só casos reais: {rel['valor_reais']:.0%}")
    if rel.get("falsos_itens") is not None:
        linhas.append(f"- Itens lidos que não estão no gabarito: {rel['falsos_itens']}")
    if rel.get("confianca_baixa") is not None:
        linhas.append(f"- Parcela de itens com confiança baixa: {rel['confianca_baixa']:.0%}")
    linhas.append(f"- Tempo médio por caso: {rel['tempo_medio_s']} s")
    custo = rel["custo_medio_usd"]
    linhas.append(f"- Custo médio por caso: {'US$ %.5f' % custo if custo is not None else 'não calculado (sem preço ou sem tokens)'}")
    linhas.append(f"- Casos que falharam (só ids): {', '.join(rel['falharam']) or 'nenhum'}")
    if rel["erros"]:
        linhas.append(f"- Casos com erro de execução (rodar de novo): {', '.join(rel['erros'])}")
    return "\n".join(linhas) + "\n"


def _gravar(rel: dict, saida: Path) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    base = saida / f"{date.today().isoformat()}_{rel['conjunto']}"
    base.with_suffix(".json").write_text(json.dumps(rel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base.with_suffix(".md").write_text(_markdown(rel), encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Executor da avaliação da Seriema (spec avaliacao §6)")
    grupo = p.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--conjunto", choices=sorted(CONJUNTOS))
    grupo.add_argument("--todos", action="store_true")
    p.add_argument("--limite", type=int, help="roda só os N primeiros casos")
    p.add_argument("--reiniciar", action="store_true", help="apaga o progresso salvo do conjunto")
    a = p.parse_args(argv)

    nomes = sorted(CONJUNTOS) if a.todos else [a.conjunto]
    for nome in nomes:
        conjunto = CONJUNTOS[nome]
        if not conjunto.gabarito().exists():
            print(f"[{nome}] sem gabarito ({conjunto.gabarito()}); pulando", file=sys.stderr)
            continue
        rel = executar(conjunto, a.limite, a.reiniciar)
        print(f"[{nome}] {_formatar_valor(rel)} · {rel['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
