"""Stubs de C2, C3, C4 e C8 (00-projeto/spec §7.4): B mantém até C entregar `dados/`.

Os dados abaixo são só para o harness funcionar e para a demo. Toda linha clínica diz
"STUB" na fonte: nada aqui foi conferido. A tabela real e conferida é a da frente `dados`.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from itertools import combinations

from harness.contratos import (
    Alerta, Conduta, InfoRemedio, ItemParaChecar, ResultadoNormalizacao, SintomaEstruturado,
)

FONTE_STUB = "STUB de B (exemplo, não conferido) — substituir pela tabela de C"
FONTE_CMED = "STUB de B (exemplo a partir da CMED) — substituir pelo Normalizador de C"


def texto_normalizado(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-z0-9.,/ ]+", " ", texto.lower())
    return re.sub(r"\s+", " ", texto).strip()


# principio -> (nomes comerciais, concentração comum, classe)
REMEDIOS: dict[str, tuple[list[str], str, str]] = {
    "losartana": (["cozaar", "losartana potassica", "aradois"], "50 mg", "bra"),
    "enalapril": (["renitec", "maleato de enalapril"], "10 mg", "ieca"),
    "captopril": (["capoten"], "25 mg", "ieca"),
    "hidroclorotiazida": (["clorana", "hctz"], "25 mg", "diuretico_tiazidico"),
    "anlodipino": (["norvasc", "besilato de anlodipino"], "5 mg", "bcc"),
    "metformina": (["glifage", "cloridrato de metformina"], "850 mg", "biguanida"),
    "glibenclamida": (["daonil"], "5 mg", "sulfonilureia"),
    "sinvastatina": (["zocor"], "20 mg", "estatina"),
    "atorvastatina": (["lipitor", "citalor"], "20 mg", "estatina"),
    "omeprazol": (["losec"], "20 mg", "ibp"),
    "acido acetilsalicilico": (["aas", "aspirina"], "100 mg", "antiagregante"),
    "levotiroxina": (["puran t4", "synthroid", "euthyrox"], "50 mcg", "hormonio_tireoide"),
    "diazepam": (["valium"], "5 mg", "benzodiazepinico"),
    "clonazepam": (["rivotril"], "2 mg", "benzodiazepinico"),
    "varfarina": (["marevan", "coumadin"], "5 mg", "anticoagulante"),
    "furosemida": (["lasix"], "40 mg", "diuretico_alca"),
}

CLASSES_DUPLICIDADE = {"ieca", "bra", "estatina", "benzodiazepinico", "ibp"}

INTERACOES: dict[tuple[str, str], tuple[str, str]] = {
    ("enalapril", "losartana"): ("alta", "Os dois agem no mesmo sistema da pressão. Juntos, podem baixar demais a pressão e afetar os rins"),
    ("acido acetilsalicilico", "varfarina"): ("alta", "Juntos, aumentam o risco de sangramento"),
    ("captopril", "losartana"): ("alta", "Os dois agem no mesmo sistema da pressão. Juntos, podem baixar demais a pressão e afetar os rins"),
    ("clonazepam", "diazepam"): ("alta", "Dois calmantes do mesmo tipo aumentam a sonolência e o risco de queda"),
}

CBMPI = {
    "diazepam": "Calmante de efeito longo: em idosos, aumenta o risco de sonolência e queda",
    "clonazepam": "Calmante: em idosos, aumenta o risco de sonolência e queda",
    "glibenclamida": "Em idosos, aumenta o risco de açúcar baixo no sangue",
}

PARA_QUE_SERVE = {
    "losartana": "controlar a pressão alta",
    "enalapril": "controlar a pressão alta e ajudar o coração",
    "captopril": "controlar a pressão alta",
    "hidroclorotiazida": "controlar a pressão alta e diminuir o inchaço",
    "anlodipino": "controlar a pressão alta",
    "metformina": "controlar o açúcar no sangue (diabetes tipo 2)",
    "glibenclamida": "controlar o açúcar no sangue (diabetes tipo 2)",
    "sinvastatina": "baixar o colesterol",
    "atorvastatina": "baixar o colesterol",
    "omeprazol": "diminuir a acidez do estômago",
    "acido acetilsalicilico": "ajudar a prevenir infarto e derrame",
    "levotiroxina": "repor o hormônio da tireoide",
    "diazepam": "acalmar e ajudar a dormir",
    "clonazepam": "acalmar e ajudar a dormir",
    "varfarina": "evitar a formação de coágulos no sangue",
    "furosemida": "diminuir o inchaço e ajudar o coração",
}

FARMACIA_POPULAR = {
    "losartana": "hipertensão", "enalapril": "hipertensão", "captopril": "hipertensão",
    "hidroclorotiazida": "hipertensão", "metformina": "diabetes", "glibenclamida": "diabetes",
    "sinvastatina": "colesterol alto",
}
DOCUMENTOS_FP = ["a receita", "um documento com foto", "o CPF"]

TIPO_RECEITA = {"diazepam": "controle_especial", "clonazepam": "controle_especial"}
VALIDADE_DIAS = {"simples": 180, "controle_especial": 30, "antimicrobiano": 10}

PALAVRAS_FORMA = r"\b(comprimidos?|comp|cps?|capsulas?|caps|revestidos?|caixa com|cx|frasco|gotas|solucao|oral|de liberacao prolongada)\b"
RE_CONCENTRACAO = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mg/ml|mcg|mg|g|ml|ui|%)")


def _nomes_por_principio() -> dict[str, str]:
    indice = {}
    for principio, (comerciais, _c, _k) in REMEDIOS.items():
        indice[principio] = principio
        for nome in comerciais:
            indice[texto_normalizado(nome)] = principio
    return indice


INDICE = _nomes_por_principio()


def nomes_conhecidos() -> set[str]:
    return set(INDICE)


# ---------- C2 ----------

def normalizar(nome: str) -> ResultadoNormalizacao:
    texto = texto_normalizado(nome)
    conc = RE_CONCENTRACAO.search(texto)
    concentracao = f"{conc.group(1).replace(',', '.')} {conc.group(2)}" if conc else None
    limpo = RE_CONCENTRACAO.sub(" ", texto)
    limpo = re.sub(PALAVRAS_FORMA, " ", limpo)
    limpo = re.sub(r"\s+", " ", limpo).strip()

    achados: list[str] = []
    if limpo in INDICE:
        achados = [INDICE[limpo]]
    else:
        # todos os nomes conhecidos no texto; mais de um princípio = associação ("losartana + hidroclorotiazida")
        for termo, principio in sorted(INDICE.items(), key=lambda t: -len(t[0])):
            if re.search(rf"\b{re.escape(termo)}\b", limpo) and principio not in achados:
                achados.append(principio)
    if not achados and limpo:
        notas = sorted(((SequenceMatcher(None, limpo, t).ratio(), p) for t, p in INDICE.items()), reverse=True)
        if notas and notas[0][0] >= 0.85:
            if len(notas) > 1 and notas[1][1] != notas[0][1] and notas[0][0] - notas[1][0] < 0.05:
                return ResultadoNormalizacao(entrada=nome, encontrado=False,
                                             candidatos=[notas[0][1], notas[1][1]], fonte=FONTE_CMED)
            achados = [notas[0][1]]
    if not achados:
        return ResultadoNormalizacao(entrada=nome, encontrado=False, concentracao=concentracao, fonte=FONTE_CMED)
    achados = list(dict.fromkeys(achados))
    return ResultadoNormalizacao(entrada=nome, encontrado=True, principio_ativo=achados,
                                 concentracao=concentracao, nome_comercial=None, fonte=FONTE_CMED)


# ---------- C3 ----------

def checar_lista(itens: list[ItemParaChecar]) -> list[Alerta]:
    alertas: list[Alerta] = []
    por_principio: dict[str, list[str]] = {}
    for item in itens:
        for p in item.principio_ativo:
            por_principio.setdefault(p, []).append(item.item_id)
    for p, ids in por_principio.items():
        if len(ids) > 1:
            alertas.append(Alerta(tipo="duplicidade_principio", item_ids=ids, principios=[p], gravidade="alta",
                                  descricao=f"O mesmo remédio ({p}) aparece mais de uma vez na lista, com nomes diferentes",
                                  fonte=FONTE_STUB))
    principios = sorted(por_principio)
    for a, b in combinations(principios, 2):
        par = tuple(sorted((a, b)))
        if par in INTERACOES:
            grav, desc = INTERACOES[par]
            alertas.append(Alerta(tipo="interacao", item_ids=por_principio[a] + por_principio[b], principios=list(par),
                                  gravidade=grav, descricao=desc, fonte=FONTE_STUB))
    por_classe: dict[str, list[str]] = {}
    for p in principios:
        if p in REMEDIOS:
            por_classe.setdefault(REMEDIOS[p][2], []).append(p)
    for classe, ps in por_classe.items():
        if len(ps) > 1 and classe in CLASSES_DUPLICIDADE:
            ja = any(set(al.principios) == set(ps) for al in alertas)
            if not ja:
                ids = [i for p in ps for i in por_principio[p]]
                alertas.append(Alerta(tipo="duplicidade_classe", item_ids=ids, principios=ps, gravidade="moderada",
                                      descricao="Dois remédios do mesmo grupo, possivelmente de médicos diferentes",
                                      fonte=FONTE_STUB))
    for p in principios:
        if p in CBMPI:
            alertas.append(Alerta(tipo="cbmpi", item_ids=por_principio[p], principios=[p], gravidade=None,
                                  descricao=CBMPI[p], fonte=FONTE_STUB))
    ordem = {"alta": 0, "moderada": 1, "baixa": 2, None: 3}
    return sorted(alertas, key=lambda a: ordem[a.gravidade])


# ---------- C4 ----------

SINAIS_ALARME = [
    ("alarme_queda_cabeca", r"(caiu|queda|tombo|caindo).{0,40}(bateu|batida).{0,15}cabeca|bateu (a|com a) cabeca",
     "Queda com batida na cabeça"),
    ("alarme_dor_peito", r"(dor|aperto|pressao|queimacao) (forte )?no peito", "Dor no peito"),
    ("alarme_falta_ar", r"falta de ar|nao consegue respirar|respirando com dificuldade|sem ar\b|sufocad", "Falta de ar"),
    ("alarme_confusao", r"confus[ao]|nao reconhece|falando coisa sem sentido|desorientad", "Confusão súbita"),
]


def detectar_alarme(texto: str) -> Conduta | None:
    t = texto_normalizado(texto)
    for regra_id, padrao, descricao in SINAIS_ALARME:
        if re.search(padrao, t):
            return Conduta(nivel="ligue_192", regra_id=regra_id, motivo=descricao, fonte=FONTE_STUB)
    return None


REGRAS_24H = [
    ("g24_desmaio", r"desmai", "Desmaio"),
    ("g24_sangramento", r"sangr", "Sangramento"),
    ("g24_febre", r"febre", "Febre"),
    ("g24_queda", r"caiu|queda|tombo", "Queda"),
    ("g24_vomito", r"vomit", "Vômitos"),
]


def avaliar_gravidade(sintoma: SintomaEstruturado) -> Conduta:
    texto = " ".join([sintoma.descricao, *sintoma.sintomas, *[k for k, v in sintoma.sinais.items() if v]])
    alarme = detectar_alarme(texto.replace("_", " "))
    if alarme:
        return alarme
    t = texto_normalizado(texto)
    for regra_id, padrao, motivo in REGRAS_24H:
        if re.search(padrao, t):
            return Conduta(nivel="atendimento_24h", regra_id=regra_id, motivo=motivo, fonte=FONTE_STUB)
    if sintoma.intensidade == "forte":
        return Conduta(nivel="atendimento_24h", regra_id="g24_forte", motivo="Sintoma forte", fonte=FONTE_STUB)
    return Conduta(nivel="observar", regra_id="padrao_observar", motivo="Sem sinal de gravidade", fonte=FONTE_STUB)


# ---------- C8 ----------

def info_remedio(principio_ativo: str) -> InfoRemedio | None:
    p = texto_normalizado(principio_ativo)
    if p not in PARA_QUE_SERVE:
        return None
    tipo = TIPO_RECEITA.get(p, "simples")
    fp = p in FARMACIA_POPULAR
    return InfoRemedio(
        principio_ativo=p, para_que_serve=PARA_QUE_SERVE[p], farmacia_popular=fp,
        farmacia_popular_detalhe=FARMACIA_POPULAR.get(p), documentos_farmacia_popular=DOCUMENTOS_FP if fp else [],
        tipo_receita=tipo, validade_receita_dias=VALIDADE_DIAS[tipo], fonte=FONTE_STUB,
    )
