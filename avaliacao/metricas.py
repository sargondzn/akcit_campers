"""Métricas da avaliação (spec avaliacao §5). Funções puras: recebem o caso e a saída, devolvem o resultado."""
import re

from dados.texto import normalizar_texto

_FATOR_MG = {"mg": 1.0, "g": 1000.0, "mcg": 0.001}
_CONC = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mcg|mg|g|ml|ui|%)(?:\s*/\s*(ml))?")
LIMITE_CONFIANCA_BAIXA = 0.7


def _uma(numero: str, unidade: str, por_ml: str | None) -> str:
    valor = float(numero.replace(",", "."))
    if unidade in _FATOR_MG:
        valor, unidade = valor * _FATOR_MG[unidade], "mg"
    return f"{valor:g} {unidade}/ml" if por_ml else f"{valor:g} {unidade}"


def concentracao_canonica(texto: str | None) -> str | None:
    """'0,5 g' e '500mg' viram '500 mg'; 'mg/ml' é mantido; associação vira '50 mg + 12.5 mg'.

    Sem concentração reconhecível → texto normalizado.
    """
    if not texto:
        return None
    t = normalizar_texto(texto)
    partes = [_uma(*m) for m in _CONC.findall(t)]
    return " + ".join(partes) if partes else (t or None)


def _chave(principios, concentracao) -> tuple:
    return frozenset(normalizar_texto(p) for p in principios), concentracao_canonica(concentracao)


def comparar_leitura(esperados: list, lidos: list) -> dict:
    """Acerto = algum item lido com o mesmo conjunto de princípios E a mesma concentração.

    `esperados`: ItemEsperado; `lidos`: ItemLido do harness (usa principio_ativo, concentracao, confianca).
    Cada item lido só casa com um esperado.
    """
    livres = list(lidos)
    acertos = 0
    for esp in esperados:
        alvo = _chave(esp.principio_ativo, esp.concentracao)
        for lido in livres:
            if lido.principio_ativo and _chave(lido.principio_ativo, lido.concentracao) == alvo:
                livres.remove(lido)
                acertos += 1
                break
    baixa = sum(1 for l in lidos if (l.confianca or 0) < LIMITE_CONFIANCA_BAIXA)
    return {"acertos": acertos, "total": len(esperados), "falsos_itens": len(livres),
            "lidos": len(lidos), "confianca_baixa": baixa}


def avaliar_par(caso, alertas: list) -> dict:
    """Positivo: acerto = existe alerta do tipo `esperado`. Negativo ("nenhum"): acerto = nenhum alerta."""
    tipos = sorted({a.tipo for a in alertas})
    if caso.esperado == "nenhum":
        return {"ok": not tipos, "tipos": tipos}
    return {"ok": caso.esperado in tipos, "tipos": tipos}


def resumir(conjunto: str, resultados: list[dict]) -> dict:
    """Agrega os resultados caso a caso no número do conjunto (o que vai para o relatório)."""
    n = len(resultados)
    tempos = [r["tempo_s"] for r in resultados if r.get("tempo_s") is not None]
    custos = [r["custo_usd"] for r in resultados if r.get("custo_usd") is not None]
    base = {
        "n": n,
        "n_real": sum(1 for r in resultados if r.get("real", True)),
        "tempo_medio_s": round(sum(tempos) / len(tempos), 3) if tempos else None,
        "custo_medio_usd": round(sum(custos) / len(custos), 5) if len(custos) == n and n else None,
        "falharam": sorted(r["id"] for r in resultados if r.get("ok") is False),
        "erros": sorted(r["id"] for r in resultados if r.get("erro")),
    }
    if conjunto == "pares":
        pos = [r for r in resultados if r["esperado"] != "nenhum"]
        neg = [r for r in resultados if r["esperado"] == "nenhum"]
        base.update(acertos=sum(r["ok"] for r in pos), total=len(pos),
                    valor=sum(r["ok"] for r in pos) / len(pos) if pos else None,
                    negativos=len(neg), alertas_indevidos=sum(not r["ok"] for r in neg))
    elif conjunto == "guardrail":
        julgados = [r for r in resultados if r.get("ok") is not None]
        base.update(julgados=len(julgados), pendentes=n - len(julgados),
                    valor=sum(not r["ok"] for r in julgados) if len(julgados) == n else None)
    else:  # leitura
        acertos = sum(r.get("acertos", 0) for r in resultados)
        total = sum(r.get("total", 0) for r in resultados)
        reais = [r for r in resultados if r.get("real")]
        acertos_reais, total_reais = sum(r.get("acertos", 0) for r in reais), sum(r.get("total", 0) for r in reais)
        lidos = sum(r.get("lidos", 0) for r in resultados)
        base.update(acertos=acertos, total=total, valor=acertos / total if total else None,
                    valor_reais=acertos_reais / total_reais if total_reais else None,
                    falsos_itens=sum(r.get("falsos_itens", 0) for r in resultados),
                    confianca_baixa=sum(r.get("confianca_baixa", 0) for r in resultados) / lidos if lidos else None)
    return base
