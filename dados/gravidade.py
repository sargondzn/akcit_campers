"""detectar_alarme e avaliar_gravidade (C4).

Tudo determinístico: nenhuma chamada de modelo. `detectar_alarme` roda ANTES do modelo
(harness/spec.md §62) e não trata negação (DA-D2, conservador): qualquer menção a um
sinal dispara o cartão `ligue_192`. O falso alarme é aceito para não perder um verdadeiro.
"""
import csv
import re
from functools import lru_cache
from pathlib import Path

from contratos.dados import Conduta, SintomaEstruturado
from dados.texto import normalizar_texto

TABELAS = Path(__file__).resolve().parent / "tabelas"


@lru_cache(maxsize=1)
def _sinais() -> list[dict]:
    with open(TABELAS / "sinais_alarme.csv", encoding="utf-8") as f:
        return [{**linha, "regex": re.compile(linha["padrao"])} for linha in csv.DictReader(f)]


# Contextos em que as palavras de alarme aparecem sem ser emergência. O trecho é apagado antes
# de procurar o alarme, então só vale para estes casos conhecidos (objeto sem ar, fato de décadas
# atrás, assunto de TV). Negação NÃO entra aqui (DA-D2): "não teve dor no peito" continua disparando.
EXCECOES = [re.compile(p) for p in (
    r"\b(pneu|bola|bexiga|colchao|boia)\b.{0,40}\bsem ar\b",
    r"\b(desmai\w*|convuls\w*)\b.{0,50}\b(quando (era|eu era|ele era|ela era)|anos atras|ha \d+ anos|faz \d+ anos|na juventude|antigamente)\b",
    r"\b(discussao|programa|filme|novela|historia|trama|musica|reuniao)\b.{0,25}\bconfus[ao]s?\b",
)]


def detectar_alarme(texto: str) -> Conduta | None:
    normalizado = normalizar_texto(texto)
    for excecao in EXCECOES:
        normalizado = excecao.sub(" ", normalizado)
    for sinal in _sinais():
        if sinal["regex"].search(normalizado):
            return Conduta(
                nivel="ligue_192",
                regra_id=sinal["regra_id"],
                motivo=f"Possível sinal de alarme: {sinal['descricao'].lower()}.",
                fonte=sinal["fonte"],
            )
    return None


# ---------------------------------------------------------------------------
# avaliar_gravidade
#
# `condicao` em regras_gravidade.csv: termos ligados por `&` (todos) e `|` (qualquer);
# o `&` pesa mais que o `|`. Termos:
#   s:<sintoma>   o sintoma aparece nos `sintomas` ou na `descricao` ("_" vale espaço)
#   sinal:<chave> `sinais[chave]` é verdadeiro
#   int:<nivel>   intensidade igual ou maior (leve < moderada < forte)
# ---------------------------------------------------------------------------
INTENSIDADES = {"leve": 1, "moderada": 2, "forte": 3}
PADRAO_OBSERVAR = Conduta(
    nivel="observar",
    regra_id="padrao_observar",
    motivo="Nenhuma regra de atenção se aplica. Anote e acompanhe; se piorar, procure atendimento.",
    fonte="regra do projeto (dados/spec.md §7.2)",
)


def interpretar_condicao(condicao: str) -> list[list[tuple[str, str]]]:
    """Condição em texto -> lista de alternativas, cada uma uma lista de termos (tipo, valor).

    Levanta ValueError se algum termo for inválido (usado por validar_tabelas.py).
    """
    alternativas = []
    for alternativa in condicao.split("|"):
        termos = []
        for termo in alternativa.split("&"):
            tipo, _, valor = termo.strip().partition(":")
            if tipo not in ("s", "sinal", "int") or not valor:
                raise ValueError(f"termo inválido: {termo.strip()!r}")
            if tipo == "int" and valor not in INTENSIDADES:
                raise ValueError(f"intensidade inválida: {valor!r}")
            termos.append((tipo, valor))
        alternativas.append(termos)
    return alternativas


def _termo_casa(tipo: str, valor: str, texto: str, sintoma) -> bool:
    if tipo == "s":
        return re.search(rf"(?<![a-z]){re.escape(valor.replace('_', ' '))}", texto) is not None
    if tipo == "sinal":
        return sintoma.sinais.get(valor) is True
    if sintoma.intensidade is None:
        return False
    return INTENSIDADES[sintoma.intensidade] >= INTENSIDADES[valor]


@lru_cache(maxsize=1)
def _regras() -> list[dict]:
    with open(TABELAS / "regras_gravidade.csv", encoding="utf-8") as f:
        regras = [{**l, "ordem": int(l["ordem"]), "alternativas": interpretar_condicao(l["condicao"])}
                  for l in csv.DictReader(f)]
    return sorted(regras, key=lambda r: r["ordem"])


def avaliar_gravidade(sintoma: SintomaEstruturado) -> Conduta:
    chaves = " ".join(k.replace("_", " ") for k, v in sintoma.sinais.items() if v is True)
    texto = normalizar_texto(" ".join([sintoma.descricao, *sintoma.sintomas, chaves]))
    alarme = detectar_alarme(texto)
    if alarme:
        return alarme
    for regra in _regras():
        if any(all(_termo_casa(t, v, texto, sintoma) for t, v in alt) for alt in regra["alternativas"]):
            return Conduta(nivel=regra["nivel"], regra_id=regra["regra_id"],
                           motivo=regra["motivo"], fonte=regra["fonte"])
    return PADRAO_OBSERVAR
