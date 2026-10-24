"""normalizar (C2): nome comercial, princípio ou apelido -> princípio ativo e concentração."""
import csv
import re
from functools import lru_cache
from pathlib import Path

from rapidfuzz import fuzz, process

from contratos.dados import ResultadoNormalizacao
from dados.texto import normalizar_texto

TABELAS = Path(__file__).resolve().parent / "tabelas"

NOTA_MINIMA = 85
DIFERENCA_AMBIGUA = 5

# Número (ou soma "50 + 12,5") seguido de unidade, com "/ml" opcional.
CONCENTRACAO = re.compile(
    r"\d+(?:[.,]\d+)?(?:\s*\+\s*\d+(?:[.,]\d+)?)*\s*(?:mg|mcg|g|ml|ui|%)(?:\s*/\s*\d*\s*(?:ml|g|mg|dose))?(?![a-z])"
)
# Palavras de forma e embalagem que não ajudam a achar o remédio.
PALAVRAS_IGNORADAS = {
    "comprimido", "comprimidos", "comp", "cp", "cps", "cpr", "capsula", "capsulas", "cap",
    "caixa", "cx", "com", "revestido", "revestidos", "rev", "de", "c", "generico", "similar",
    "mg", "mcg", "ml", "g", "gotas", "gts", "unidades", "unid",
}


@lru_cache(maxsize=1)
def _tabelas():
    sinonimos: dict[str, str] = {}
    comerciais: dict[str, set[str]] = {}
    principios: set[str] = set()
    fonte = ""
    with open(TABELAS / "remedios.csv", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            fonte = linha["fonte"]
            principios.update(linha["principio_ativo"].split(";"))
            comerciais.setdefault(normalizar_texto(linha["nome_comercial"]), set()).add(linha["principio_ativo"])
    with open(TABELAS / "sinonimos.csv", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            sinonimos[normalizar_texto(linha["termo"])] = linha["principio_ativo"]
    return sinonimos, comerciais, principios, fonte


def _formatar_concentracao(bruto: str) -> str:
    bruto = re.sub(r"\s*\+\s*", " + ", bruto.strip())
    bruto = re.sub(r"(\d),0(?!\d)", r"\1", bruto.replace(".", ","))
    return re.sub(r"(\d)\s*(?=[a-z%])", r"\1 ", bruto)


def _limpar(texto: str) -> tuple[str, str | None]:
    """Devolve (nome sem concentração e sem palavras de forma, concentração formatada)."""
    achado = CONCENTRACAO.search(texto)
    concentracao = _formatar_concentracao(achado.group(0)) if achado else None
    if achado:
        texto = texto[: achado.start()] + " " + texto[achado.end():]
    tokens = [t for t in texto.split() if t not in PALAVRAS_IGNORADAS and not re.fullmatch(r"[\d.,/%]+", t)]
    return " ".join(tokens), concentracao


def _grupos(chaves: dict[str, set[str]]) -> dict[str, list[str]]:
    return {k: sorted(v) for k, v in chaves.items()}


def _montar(entrada, principios, concentracao, nome_comercial, fonte) -> ResultadoNormalizacao:
    # cada elemento é um princípio ("losartana"), uma associação ("hidroclorotiazida;losartana") ou um conjunto deles
    itens = [x for conjunto in principios for x in ([conjunto] if isinstance(conjunto, str) else conjunto)]
    lista = sorted({p for item in itens for p in item.split(";")})
    return ResultadoNormalizacao(
        entrada=entrada, encontrado=True, principio_ativo=lista,
        concentracao=concentracao, nome_comercial=nome_comercial, fonte=fonte,
    )


def _ambiguo(entrada, candidatos, concentracao, fonte) -> ResultadoNormalizacao:
    return ResultadoNormalizacao(
        entrada=entrada, encontrado=False, concentracao=concentracao,
        candidatos=sorted(candidatos), fonte=fonte,
    )


def _busca_exata(nome, sinonimos, comerciais, principios):
    """Ordem da spec: sinônimo, nome comercial, princípio. Devolve conjunto de princípios ou None."""
    if nome in sinonimos:
        return {sinonimos[nome]}
    if nome in comerciais:
        return comerciais[nome]
    if nome in principios:
        return {nome}
    return None


def normalizar(nome: str) -> ResultadoNormalizacao:
    sinonimos, comerciais, principios, fonte = _tabelas()
    limpo, concentracao = _limpar(normalizar_texto(nome))
    comercial = lambda n: n if n in comerciais else None  # noqa: E731

    if not limpo:
        return ResultadoNormalizacao(entrada=nome, encontrado=False, concentracao=concentracao, fonte=fonte)

    # 1. Associação escrita pela cuidadora: "losartana + hidroclorotiazida" (ou "losartana e hidroclorotiazida").
    partes = [p.strip() for p in re.split(r"\s*(?:\+|\be\b)\s*", limpo) if p.strip()]
    if len(partes) > 1:
        achados = [_busca_exata(p, sinonimos, comerciais, principios) for p in partes]
        if all(a and len(a) == 1 for a in achados):
            return _montar(nome, [next(iter(a)) for a in achados], concentracao, None, fonte)

    # 2. Exata, com o nome inteiro e depois com prefixos ("losartana potassica generico").
    palavras = limpo.split()
    for n in range(len(palavras), 0, -1):
        trecho = " ".join(palavras[:n])
        achados = _busca_exata(trecho, sinonimos, comerciais, principios)
        if achados:
            if len(achados) > 1:
                return _ambiguo(nome, achados, concentracao, fonte)
            sobra = palavras[n:]
            # Palavra que sobrou e é outro remédio ("losartana hidroclorotiazida"): não pode ser descartada.
            outros = [_busca_exata(w, sinonimos, comerciais, principios) for w in sobra]
            reconhecidos = [o for o in outros if o]
            if reconhecidos:
                if all(len(o) == 1 for o in reconhecidos):
                    return _montar(nome, [achados, *reconhecidos], concentracao, None, fonte)
                return _ambiguo(nome, {p for o in [achados, *reconhecidos] for p in o}, concentracao, fonte)
            return _montar(nome, achados, concentracao, comercial(trecho), fonte)

    # 3. Aproximada. Exige mesma letra inicial e tamanho parecido: "esomeprazol" não vira "omeprazol".
    chaves: dict[str, set[str]] = {}
    for k, v in sinonimos.items():
        chaves.setdefault(k, set()).add(v)
    for k, v in comerciais.items():
        chaves.setdefault(k, set()).update(v)
    for p in principios:
        chaves.setdefault(p, set()).add(p)
    candidatas = [k for k in chaves if k[:1] == limpo[:1] and abs(len(k) - len(limpo)) <= 1]
    melhores: dict[frozenset, tuple[float, str]] = {}
    for chave, nota, _ in process.extract(limpo, candidatas, scorer=fuzz.ratio, limit=10, score_cutoff=NOTA_MINIMA):
        grupo = frozenset(chaves[chave])
        if grupo not in melhores or nota > melhores[grupo][0]:
            melhores[grupo] = (nota, chave)
    if not melhores:
        return ResultadoNormalizacao(entrada=nome, encontrado=False, concentracao=concentracao, fonte=fonte)
    ordenados = sorted(melhores.items(), key=lambda kv: -kv[1][0])
    if len(ordenados) > 1 and ordenados[0][1][0] - ordenados[1][1][0] < DIFERENCA_AMBIGUA:
        return _ambiguo(nome, {p for g, _ in ordenados for p in g}, concentracao, fonte)
    grupo, (_, chave) = ordenados[0]
    if len(grupo) > 1:
        return _ambiguo(nome, grupo, concentracao, fonte)
    return _montar(nome, grupo, concentracao, comercial(chave), fonte)
