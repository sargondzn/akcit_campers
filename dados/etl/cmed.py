"""ETL da CMED: extrai os ~20 remédios da lista de preços e gera remedios.csv e sinonimos.csv.

Uso:
    python -m dados.etl.cmed [caminho/lista_pmc.xlsx]

Sem argumento, usa o arquivo mais recente de dados/brutos/ (baixado de
https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos).
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl

from dados.texto import normalizar_texto

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "brutos"
TABELAS = RAIZ / "tabelas"

# Lista final da DA-D1 (24/10/2026). Sem acento, minúsculo.
PRINCIPIOS = [
    "losartana", "hidroclorotiazida", "anlodipino", "enalapril", "atenolol",
    "furosemida", "espironolactona",
    "metformina", "glibenclamida",
    "sinvastatina", "atorvastatina",
    "varfarina", "acido acetilsalicilico", "clopidogrel",
    "omeprazol",
    "clonazepam", "diazepam",
    "diclofenaco", "ibuprofeno",
    "levotiroxina",
]

# Associações aceitas além dos princípios isolados (DA-D1: entrada extra).
ASSOCIACOES = [frozenset({"losartana", "hidroclorotiazida"})]

# Apelidos que a cuidadora usa e que não aparecem como SUBSTÂNCIA na CMED.
SINONIMOS_FIXOS = {
    "aas": "acido acetilsalicilico",
    "aspirina": "acido acetilsalicilico",
    "acido acetil salicilico": "acido acetilsalicilico",
    "glucophage": "metformina",
    "glifage": "metformina",
    "simvastatina": "sinvastatina",
}

# Primeira palavra da forma farmacêutica na APRESENTAÇÃO ("50 MG COM REV CT BL ...").
FORMA_TOKEN = re.compile(r"\b(COM|CM|CAP|CAPS|SOL|GTS|XPE|SUS|INJ|AER|GEL|POM|CREME|EMU|SPR|LOC|SUPOS|ENEMA|OFT|COL|ADES|PO|LIOF)\b")
FORMAS = {"COM": "comprimido", "CM": "comprimido", "CAP": "capsula", "CAPS": "capsula",
          "SOL": "liquido", "GTS": "liquido", "XPE": "liquido", "SUS": "liquido"}
# Apresentação que não serve para a rotina da cuidadora (injetáveis, tópicos, aerossol...) é descartada.
EXCLUIR_SE = re.compile(r"\b(INJ|AER|SPR|OFT|COL|LIOF)\b")
UNIDADE = re.compile(r"(MG|MCG|G|ML|UI|%)(?:\s*/\s*(?:\d+\s*)?(?:ML|G|MG|DOSE))?", re.I)


def _apresentacao(texto: str) -> tuple[str, str] | None:
    """Devolve (concentracao, forma) ou None se a apresentação não entra na lista."""
    texto = texto.replace("\xa0", " ").upper().strip()
    achado = FORMA_TOKEN.search(texto)
    if not achado or EXCLUIR_SE.search(texto):
        return None
    forma = FORMAS.get(achado.group(1))
    if forma is None:  # gel, pomada, creme, pó...
        return None
    cabeca = texto[: achado.start()]
    numeros = re.findall(r"\d+(?:[.,]\d+)?", cabeca)
    unidades = UNIDADE.findall(cabeca)
    if not numeros:
        return "", forma
    numeros = [re.sub(r",0$", "", n.replace(".", ",")) for n in numeros]
    sufixo = re.search(r"/\s*(\d+\s*)?(ML|G|MG|DOSE)", cabeca)
    unidade = unidades[-1].lower() if unidades else ""
    if sufixo:
        unidade += "/" + (sufixo.group(1) or "").strip() + sufixo.group(2).lower()
    return " + ".join(numeros) + " " + unidade, forma


def _componentes(substancia: str) -> list[str | None]:
    """Cada componente da SUBSTÂNCIA vira um princípio da lista, ou None se for de fora."""
    saida = []
    for parte in substancia.split(";"):
        texto = normalizar_texto(parte)
        achado = None
        for principio in PRINCIPIOS:
            # palavra inteira: "esomeprazol" não casa com "omeprazol"
            if re.search(rf"(?<![a-z]){re.escape(principio)}(?![a-z])", texto):
                achado = principio
                break
        saida.append(achado)
    return saida


def _principios_da_linha(substancia: str) -> list[str] | None:
    comps = _componentes(substancia)
    if None in comps:
        return None
    unicos = sorted(set(comps))
    if len(unicos) == 1:
        return unicos
    return unicos if frozenset(unicos) in ASSOCIACOES else None


def _arquivo_mais_recente() -> Path:
    arquivos = sorted(BRUTOS.glob("lista_pmc_*.xlsx"))
    if not arquivos:
        sys.exit(f"Nenhum lista_pmc_*.xlsx em {BRUTOS}. Baixe a lista PMC da CMED (ver docstring).")
    return arquivos[-1]


def _data_do_arquivo(caminho: Path) -> str:
    achado = re.search(r"(\d{4})(\d{2})(\d{2})", caminho.stem)
    return "-".join(achado.groups()) if achado else "data desconhecida"


def extrair(caminho: Path):
    wb = openpyxl.load_workbook(caminho, read_only=True)
    ws = wb["Lista PMC"]
    linhas = ws.iter_rows(values_only=True)
    cabecalho = next(l for l in linhas if l and str(l[0] or "").strip().upper().startswith("SUBST"))
    col = {str(nome).strip().upper(): i for i, nome in enumerate(cabecalho) if nome}
    i_sub, i_reg, i_prod, i_apr = col["SUBSTÂNCIA"], col["REGISTRO"], col["PRODUTO"], col["APRESENTAÇÃO"]

    remedios: dict[tuple, dict] = {}
    substancias: dict[str, str] = {}  # texto normalizado da SUBSTÂNCIA -> princípio (só isoladas)
    for linha in linhas:
        if not linha or not linha[i_sub]:
            continue
        principios = _principios_da_linha(str(linha[i_sub]))
        if not principios:
            continue
        apresentacao = _apresentacao(str(linha[i_apr]))
        if apresentacao is None:
            continue
        concentracao, forma = apresentacao
        principio = ";".join(principios)
        if len(principios) == 1:
            substancias[normalizar_texto(str(linha[i_sub]))] = principio
        chave = (principio, normalizar_texto(str(linha[i_prod])), concentracao, forma)
        remedios.setdefault(chave, {"registro_anvisa": str(linha[i_reg] or "").strip()})
    return remedios, substancias


def gravar(remedios, substancias, fonte: str) -> None:
    TABELAS.mkdir(exist_ok=True)
    with open(TABELAS / "remedios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["principio_ativo", "nome_comercial", "concentracao", "forma", "registro_anvisa", "fonte"])
        for (principio, nome, conc, forma), extra in sorted(remedios.items()):
            w.writerow([principio, nome, conc, forma, extra["registro_anvisa"], fonte])

    sinonimos = dict(SINONIMOS_FIXOS)
    for texto, principio in substancias.items():  # nomes de sal: "cloridrato de metformina" -> metformina
        if texto != principio:
            sinonimos.setdefault(texto, principio)
    with open(TABELAS / "sinonimos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["termo", "principio_ativo"])
        for termo, principio in sorted(sinonimos.items()):
            w.writerow([termo, principio])


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else _arquivo_mais_recente()
    fonte = f"CMED {_data_do_arquivo(caminho)}"
    remedios, substancias = extrair(caminho)
    gravar(remedios, substancias, fonte)
    cobertos = {p for (p, *_ ) in remedios if ";" not in p}
    faltando = sorted(set(PRINCIPIOS) - cobertos)
    print(f"{len(remedios)} apresentações; princípios cobertos: {len(cobertos)}/{len(PRINCIPIOS)}")
    if faltando:
        sys.exit(f"Princípios sem nenhuma apresentação na CMED: {faltando}")


if __name__ == "__main__":
    main()
