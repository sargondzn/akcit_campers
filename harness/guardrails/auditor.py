"""Auditor determinístico (spec §13.3, HA-D4): roda no núcleo sobre todo texto de saída."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from harness import dados_ponte as dados
from harness.contratos import ItemLido
from harness.guardrails import frases

FRASES_PROIBIDAS = re.compile(
    r"\b("
    r"tome|tomem|tomar mais|tomar menos|pode tomar|pode dar (o|a|os|as|mais|menos|metade|dois|duas|um|uma|\d)"
    r"|d[eê] mais|d[eê] metade|dê (dois|duas|um|uma|meio|meia) "
    # "de um" sem acento é preposição ("de um médico", "de uma consulta"): só conta antes de unidade de dose
    r"|de (dois|duas|um|uma|meio|meia) (comprimidos?|cps?|c[aá]psulas?|gotas?|doses?|colher(es)?|ampolas?)"
    r"|aument[ae]|aumentar a dose|diminu[ai]|reduz(a|ir) a dose|dobr[ae]|suspend[ae]|suspender|pare de (tomar|dar|usar)"
    r"|parar de (tomar|dar|usar)|interromp[ae]|troqu?e|trocar (por|pelo|pela)|substitua|substituir (por|pelo|pela)|pode tirar (o|a|os|as|esse|essa)|tire (o|a|esse|essa)"
    r"|deixe de (tomar|dar)|pule (a|o) dose"
    r")\b",
    re.IGNORECASE,
)
RE_DOSE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mg|mcg|ml|gotas?|comprimidos?|cps?|c[aá]psulas?)\b", re.IGNORECASE)
RE_FATO = re.compile(
    r"intera[cç][aã]o|interage|efeito colateral|efeitos colaterais|contraindica|duplicidade|"
    r"serve para|usad[ao] para|indicad[ao] para|é para (a|o|tratar|controlar)",
    re.IGNORECASE,
)

UNIDADES = {"mg": "mg", "mcg": "mcg", "ml": "ml", "gota": "gota", "gotas": "gota", "comprimido": "un",
            "comprimidos": "un", "cp": "un", "cps": "un", "capsula": "un", "capsulas": "un", "cápsula": "un",
            "cápsulas": "un"}


@dataclass
class ContextoAuditor:
    itens: list[ItemLido] = field(default_factory=list)          # lista atual + proposta + histórico
    quantidades_estoque: list[float] = field(default_factory=list)
    tem_alerta: bool = False
    tem_conduta: bool = False
    tem_info: bool = False


@dataclass
class ResultadoAuditor:
    aprovado: bool
    motivos: list[str]
    texto_final: str


EXTENSO = {"meio": "0.5", "meia": "0.5", "um": "1", "uma": "1", "dois": "2", "duas": "2", "tres": "3", "três": "3",
           "quatro": "4", "cinco": "5", "seis": "6", "dez": "10", "vinte": "20", "trinta": "30"}
RE_EXTENSO = re.compile(r"\b(" + "|".join(EXTENSO) + r")\s+(?=(mg|ml|gotas?|comprimidos?|c[aá]psulas?)\b)", re.IGNORECASE)


def _com_digitos(texto: str) -> str:
    """'dois comprimidos' → '2 comprimidos', para a regra de dose valer também por extenso."""
    return RE_EXTENSO.sub(lambda m: EXTENSO[m.group(1).lower()] + " ", texto)


def _numero(valor: str) -> float:
    return float(valor.replace(",", "."))


def _doses_permitidas(ctx: ContextoAuditor) -> set[tuple[float, str]]:
    permitidas: set[tuple[float, str]] = set()
    for item in ctx.itens:
        for texto in (item.concentracao or "", item.posologia_texto or "", item.nome_lido or ""):
            for valor, unidade in RE_DOSE.findall(_com_digitos(texto)):
                permitidas.add((_numero(valor), UNIDADES.get(unidade.lower(), unidade.lower())))
        if item.quantidade_embalagem:
            permitidas.add((float(item.quantidade_embalagem), "un"))
        if item.unidades_por_dose:
            permitidas.add((float(item.unidades_por_dose), "un"))
    for q in ctx.quantidades_estoque:
        permitidas.add((float(q), "un"))
    return permitidas


def _nomes_da_lista(ctx: ContextoAuditor) -> set[str]:
    nomes: set[str] = set()
    for item in ctx.itens:
        nomes.update(dados.texto_normalizado(p) for p in item.principio_ativo)
        nomes.add(dados.texto_normalizado(item.nome_lido))
    return nomes


def verificar(texto: str, contexto: ContextoAuditor | None = None) -> ResultadoAuditor:
    ctx = contexto or ContextoAuditor()
    motivos: list[str] = []

    if FRASES_PROIBIDAS.search(texto):
        motivos.append("frase_proibida")

    permitidas = _doses_permitidas(ctx)
    for valor, unidade in RE_DOSE.findall(_com_digitos(texto)):
        if (_numero(valor), UNIDADES.get(unidade.lower(), unidade.lower())) not in permitidas:
            motivos.append(f"dose_fora_da_lista:{valor} {unidade}")
            break

    normalizado = dados.texto_normalizado(texto)
    nomes_lista = _nomes_da_lista(ctx)
    for nome in dados.nomes_conhecidos():
        if len(nome) >= 4 and re.search(rf"\b{re.escape(nome)}\b", normalizado):
            principio = dados.normalizar(nome).principio_ativo
            if not (nome in nomes_lista or any(p in nomes_lista for p in principio)
                    or any(nome in n for n in nomes_lista)):
                motivos.append(f"remedio_fora_da_lista:{nome}")
                break

    if RE_FATO.search(texto) and not (ctx.tem_alerta or ctx.tem_conduta or ctx.tem_info):
        motivos.append("fato_clinico_sem_fonte")

    if motivos:
        return ResultadoAuditor(aprovado=False, motivos=motivos, texto_final=frases.BLOQUEIO)
    return ResultadoAuditor(aprovado=True, motivos=[], texto_final=texto)
