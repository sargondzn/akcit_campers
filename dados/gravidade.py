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
#   s:<sintoma>   o termo do vocabulário (ou um sinônimo) aparece nos `sintomas` ou na `descricao`
#   sinal:<chave> `sinais[chave]` é verdadeiro, ou um sinônimo do vocabulário aparece na `descricao`
#   int:<nivel>   intensidade igual ou maior (leve < moderada < forte); sem `intensidade`, usa pistas da fala
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


# Negação só vale para o texto livre (`descricao`): "sem febre" não conta como febre. O que o Diário
# lista em `sintomas` é confiado como está. Os sinais de alarme (192) NÃO usam isto (DA-D2).
NEGACAO = re.compile(r"\b(sem|nao teve|nao tem|nao tinha|nao esta com|nao esta sentindo|nao apresentou|nunca teve)\s+(?:\w+\s+){0,2}$")


def _padrao(alternativas: list[str]) -> re.Pattern:
    """Alternativas do vocabulário -> regex. `*` no fim vale "começa com"; sem `*`, palavra inteira.
    ` % ` no meio vale "até 5 palavras quaisquer aqui" ("fezes % pretas" casa "fezes dele estão pretas")."""
    partes = []
    for alt in alternativas:
        alt = alt.strip()
        if not alt:
            continue
        prefixo = alt.endswith("*")
        miolo = r"(?:\s+\w+){0,5}\s+".join(re.escape(x) for x in alt.rstrip("*").split(" % "))
        partes.append(miolo + ("" if prefixo else r"(?![a-z])"))
    return re.compile(r"(?<![a-z])(?:" + "|".join(partes) + ")")


@lru_cache(maxsize=1)
def _vocabulario_motor() -> dict[tuple[str, str], dict]:
    """(tipo, termo) -> {'padrao', 'exclusoes'}, de vocabulario.csv."""
    saida = {}
    with open(TABELAS / "vocabulario.csv", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            alternativas = [linha["termo"].replace("_", " "), *linha["sinonimos"].split("|")]
            exclusoes = [e for e in linha["exclusoes"].split("|") if e.strip()]
            saida[(linha["tipo"], linha["termo"])] = {
                "padrao": _padrao(alternativas),
                "exclusoes": _padrao(exclusoes) if exclusoes else None,
            }
    return saida


def _aparece(tipo: str, termo: str, descricao: str, sintomas: list[str]) -> bool:
    """O termo (ou um sinônimo) aparece nos sintomas listados ou, sem negação, na descrição."""
    entrada = _vocabulario_motor().get((tipo, termo))
    if entrada is None:  # termo fora do vocabulário (o validador não deixa chegar aqui)
        entrada = {"padrao": _padrao([termo.replace("_", " ")]), "exclusoes": None}

    def limpar(texto: str) -> str:
        return entrada["exclusoes"].sub(" ", texto) if entrada["exclusoes"] else texto

    if any(entrada["padrao"].search(limpar(item)) for item in sintomas):
        return True
    texto = limpar(descricao)
    return any(not NEGACAO.search(texto[max(0, m.start() - 30):m.start()]) for m in entrada["padrao"].finditer(texto))


def _intensidade(sintoma: SintomaEstruturado, descricao: str) -> str | None:
    """A intensidade do Diário vence; sem ela, procura pistas de fala (forte antes de moderada)."""
    if sintoma.intensidade is not None:
        return sintoma.intensidade
    for nivel in ("forte", "moderada", "leve"):
        entrada = _vocabulario_motor().get(("intensidade", nivel))
        if entrada is None:
            continue
        texto = entrada["exclusoes"].sub(" ", descricao) if entrada["exclusoes"] else descricao
        if entrada["padrao"].search(texto):
            return nivel
    return None


def _termo_casa(tipo: str, valor: str, ctx: dict) -> bool:
    if tipo == "s":
        return _aparece("sintoma", valor, ctx["descricao"], ctx["sintomas"])
    if tipo == "sinal":
        return ctx["sinais"].get(valor) is True or _aparece("sinal", valor, ctx["descricao"], [])
    if ctx["intensidade"] is None:
        return False
    return INTENSIDADES[ctx["intensidade"]] >= INTENSIDADES[valor]


@lru_cache(maxsize=1)
def _regras() -> list[dict]:
    with open(TABELAS / "regras_gravidade.csv", encoding="utf-8") as f:
        regras = [{**l, "ordem": int(l["ordem"]), "alternativas": interpretar_condicao(l["condicao"])}
                  for l in csv.DictReader(f)]
    return sorted(regras, key=lambda r: r["ordem"])


def avaliar_gravidade(sintoma: SintomaEstruturado) -> Conduta:
    chaves = " ".join(k.replace("_", " ") for k, v in sintoma.sinais.items() if v is True)
    itens = [normalizar_texto(x) for x in sintoma.sintomas]
    alarme = detectar_alarme(" ".join([sintoma.descricao, *sintoma.sintomas, chaves]))
    if alarme:
        return alarme
    descricao = normalizar_texto(f"{sintoma.descricao} {chaves}")
    ctx = {"descricao": descricao, "sintomas": itens, "sinais": sintoma.sinais,
           "intensidade": _intensidade(sintoma, descricao)}
    for regra in _regras():
        if any(all(_termo_casa(t, v, ctx) for t, v in alt) for alt in regra["alternativas"]):
            return Conduta(nivel=regra["nivel"], regra_id=regra["regra_id"],
                           motivo=regra["motivo"], fonte=regra["fonte"])
    return PADRAO_OBSERVAR
