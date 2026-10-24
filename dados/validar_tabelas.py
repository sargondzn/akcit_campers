"""Confere colunas, valores e referências entre as tabelas. Roda junto com os testes.

Uso: python -m dados.validar_tabelas   (sai com código 1 se houver erro)
"""
import csv
import re
import sys
from pathlib import Path

from dados.gravidade import _padrao, interpretar_condicao
from dados.texto import normalizar_texto

TABELAS = Path(__file__).resolve().parent / "tabelas"
COLUNAS = {
    "remedios.csv": ["principio_ativo", "nome_comercial", "concentracao", "forma", "registro_anvisa", "tipo_receita", "fonte"],
    "sinonimos.csv": ["termo", "principio_ativo"],
    "interacoes.csv": ["principio_a", "principio_b", "gravidade", "descricao", "fonte", "conferencia"],
    "classes.csv": ["principio_ativo", "classe", "duplicidade_relevante", "fonte", "conferencia"],
    "cbmpi.csv": ["principio_ativo", "criterio", "motivo", "fonte", "conferencia"],
    "sinais_alarme.csv": ["regra_id", "padrao", "descricao", "fonte", "conferencia"],
    "regras_gravidade.csv": ["regra_id", "ordem", "condicao", "nivel", "motivo", "fonte", "conferencia"],
    "indicacoes.csv": ["principio_ativo", "para_que_serve", "fonte", "conferencia"],
    "farmacia_popular.csv": ["principio_ativo", "concentracao", "indicacao_programa", "gratuito", "documentos", "fonte", "conferencia"],
    "tipos_receita.csv": ["tipo_receita", "validade_dias", "fonte", "conferencia"],
    "vocabulario.csv": ["tipo", "termo", "definicao", "sinonimos", "exclusoes", "exemplo", "tratamento", "fonte", "conferencia"],
}
TIPOS_VOCABULARIO = {"sintoma", "sinal", "intensidade"}
TRATAMENTOS = {"regra", "alarme", "regra+alarme", "sem_regra"}
TIPOS_RECEITA = {"simples", "controle_especial", "antimicrobiano"}
CONFERENCIA = {"llm", "profissional"}


def _ler(nome, erros):
    caminho = TABELAS / nome
    if not caminho.exists():
        erros.append(f"{nome}: arquivo não existe")
        return []
    with open(caminho, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        if leitor.fieldnames != COLUNAS[nome]:
            erros.append(f"{nome}: colunas {leitor.fieldnames} diferem de {COLUNAS[nome]}")
            return []
        return list(leitor)


def validar() -> list[str]:
    erros: list[str] = []
    t = {nome: _ler(nome, erros) for nome in COLUNAS}

    # princípios conhecidos: os isolados de remedios.csv (associações valem pelos componentes)
    conhecidos = {p for l in t["remedios.csv"] for p in l["principio_ativo"].split(";")}

    def princ(nome, valor, ctx):
        if valor != normalizar_texto(valor):
            erros.append(f"{nome}: {ctx} {valor!r} não está em minúsculo e sem acento")
        if valor not in conhecidos:
            erros.append(f"{nome}: {ctx} {valor!r} não existe em remedios.csv")

    for l in t["sinonimos.csv"]:
        for p in l["principio_ativo"].split(";"):
            princ("sinonimos.csv", p, "principio_ativo")

    vistos = set()
    for l in t["interacoes.csv"]:
        a, b = l["principio_a"], l["principio_b"]
        princ("interacoes.csv", a, "principio_a"); princ("interacoes.csv", b, "principio_b")
        if not a < b:
            erros.append(f"interacoes.csv: par fora de ordem alfabética ou igual: {a}, {b}")
        if (a, b) in vistos:
            erros.append(f"interacoes.csv: par repetido: {a}, {b}")
        vistos.add((a, b))
        if l["gravidade"] not in ("alta", "moderada", "baixa"):
            erros.append(f"interacoes.csv: gravidade inválida em {a}+{b}: {l['gravidade']!r}")

    classes = set()
    for l in t["classes.csv"]:
        princ("classes.csv", l["principio_ativo"], "principio_ativo")
        classes.add(l["principio_ativo"])
        if l["duplicidade_relevante"] not in ("sim", "nao"):
            erros.append(f"classes.csv: duplicidade_relevante inválida em {l['principio_ativo']}")
    for p in sorted(conhecidos - classes):
        erros.append(f"classes.csv: {p!r} está em remedios.csv e não tem classe")

    for l in t["cbmpi.csv"]:
        princ("cbmpi.csv", l["principio_ativo"], "principio_ativo")

    ids = set()
    for l in t["sinais_alarme.csv"]:
        try:
            re.compile(l["padrao"])
        except re.error as e:
            erros.append(f"sinais_alarme.csv: regex inválida em {l['regra_id']}: {e}")
        if l["regra_id"] in ids:
            erros.append(f"sinais_alarme.csv: regra_id repetido: {l['regra_id']}")
        ids.add(l["regra_id"])

    ordens = set()
    for l in t["regras_gravidade.csv"]:
        if l["nivel"] not in ("ligue_192", "atendimento_24h", "observar"):
            erros.append(f"regras_gravidade.csv: nivel inválido em {l['regra_id']}: {l['nivel']!r}")
        if not l["ordem"].isdigit() or l["ordem"] in ordens:
            erros.append(f"regras_gravidade.csv: ordem inválida ou repetida em {l['regra_id']}: {l['ordem']!r}")
        ordens.add(l["ordem"])
        try:
            interpretar_condicao(l["condicao"])
        except ValueError as e:
            erros.append(f"regras_gravidade.csv: condicao de {l['regra_id']}: {e}")
        if l["regra_id"] in ids:
            erros.append(f"regras_gravidade.csv: regra_id repetido: {l['regra_id']}")
        ids.add(l["regra_id"])

    erros += _validar_vocabulario(t["vocabulario.csv"], t["regras_gravidade.csv"])
    erros += _validar_info_remedio(t, conhecidos)

    # fonte e conferencia preenchidas em toda linha clínica
    for nome in ("interacoes.csv", "classes.csv", "cbmpi.csv", "sinais_alarme.csv", "regras_gravidade.csv", "vocabulario.csv", "indicacoes.csv", "farmacia_popular.csv", "tipos_receita.csv"):
        for i, l in enumerate(t[nome], start=2):
            if not l["fonte"].strip():
                erros.append(f"{nome} linha {i}: fonte vazia")
            if l["conferencia"] not in CONFERENCIA:
                erros.append(f"{nome} linha {i}: conferencia {l['conferencia']!r} (esperado llm ou profissional)")
    return erros


def _validar_vocabulario(vocab, regras) -> list[str]:
    """O vocabulário é a fonte; as regras só podem usar termos dele (DA-D4)."""
    erros: list[str] = []
    chaves = set()
    dono: dict[tuple[str, str], str] = {}  # (tipo, forma de falar) -> termo
    for l in vocab:
        ctx = f"vocabulario.csv: {l['tipo']} {l['termo']!r}"
        if l["tipo"] not in TIPOS_VOCABULARIO:
            erros.append(f"{ctx}: tipo inválido")
        if l["tratamento"] not in TRATAMENTOS:
            erros.append(f"{ctx}: tratamento inválido {l['tratamento']!r}")
        if not re.fullmatch(r"[a-z0-9_]+", l["termo"]):
            erros.append(f"{ctx}: termo deve ser minúsculo, sem acento, com _ no lugar de espaço")
        if (l["tipo"], l["termo"]) in chaves:
            erros.append(f"{ctx}: termo repetido")
        chaves.add((l["tipo"], l["termo"]))
        for campo in ("definicao", "exemplo"):
            if not l[campo].strip():
                erros.append(f"{ctx}: {campo} vazio")
        formas = [l["termo"].replace("_", " ")] + [x for x in l["sinonimos"].split("|") if x]
        for forma in formas:
            base = forma.rstrip("*")
            if any(parte != normalizar_texto(parte) for parte in base.split(" % ")):
                erros.append(f"{ctx}: forma {forma!r} fora do formato normalizado (minúsculo, sem acento nem pontuação)")
            outro = dono.get((l["tipo"], base))  # forma exata repetida em dois termos
            if outro is not None and outro != l["termo"]:
                erros.append(f"{ctx}: a forma {forma!r} também é de {outro!r} (ambígua)")
            dono[(l["tipo"], base)] = l["termo"]
        for exc in [x for x in l["exclusoes"].split("|") if x]:
            if exc.rstrip("*") != normalizar_texto(exc.rstrip("*")):
                erros.append(f"{ctx}: exclusão {exc!r} fora do formato normalizado")
        if not _padrao(formas).search(normalizar_texto(l["exemplo"])):
            erros.append(f"{ctx}: o exemplo {l['exemplo']!r} não contém o termo nem um sinônimo")

    usos: dict[tuple[str, str], int] = {}
    for r in regras:
        try:
            alternativas = interpretar_condicao(r["condicao"])
        except ValueError:
            continue  # já reportado em regras_gravidade.csv
        for alt in alternativas:
            for tipo, valor in alt:
                if tipo == "int":
                    if ("intensidade", valor) not in chaves:
                        erros.append(f"regras_gravidade.csv: {r['regra_id']} usa int:{valor}, que não está no vocabulário")
                    continue
                chave = ("sintoma" if tipo == "s" else "sinal", valor)
                if chave not in chaves:
                    erros.append(f"regras_gravidade.csv: {r['regra_id']} usa {tipo}:{valor}, que não está no vocabulário")
                usos[chave] = usos.get(chave, 0) + 1
    for l in vocab:
        if l["tipo"] == "intensidade":
            continue
        chave = (l["tipo"], l["termo"])
        com_regra = l["tratamento"] in ("regra", "regra+alarme")
        if com_regra and chave not in usos:
            erros.append(f"vocabulario.csv: {l['tipo']} {l['termo']!r} está marcado '{l['tratamento']}' e nenhuma regra o usa")
        if not com_regra and chave in usos:
            erros.append(f"vocabulario.csv: {l['tipo']} {l['termo']!r} está marcado '{l['tratamento']}' mas uma regra o usa")
    return erros


def _validar_info_remedio(t, conhecidos) -> list[str]:
    """Tabelas do C8: indicacoes.csv, farmacia_popular.csv, tipos_receita.csv e a coluna tipo_receita."""
    erros: list[str] = []
    isolados = {p for p in conhecidos}  # princípios isolados de remedios.csv
    usados = {l["tipo_receita"] for l in t["remedios.csv"]}
    for l in t["remedios.csv"]:
        if l["tipo_receita"] not in TIPOS_RECEITA:
            erros.append(f"remedios.csv: tipo_receita inválido em {l['nome_comercial']!r}: {l['tipo_receita']!r}")

    com_indicacao = set()
    for l in t["indicacoes.csv"]:
        p = l["principio_ativo"]
        if p != normalizar_texto(p) or p not in conhecidos:
            erros.append(f"indicacoes.csv: principio_ativo {p!r} não existe em remedios.csv ou não está normalizado")
        if p in com_indicacao:
            erros.append(f"indicacoes.csv: princípio repetido: {p}")
        com_indicacao.add(p)
        frase = l["para_que_serve"].strip()
        if not frase or not frase.split()[0].rstrip(",;.").endswith("r"):
            erros.append(f"indicacoes.csv: {p}: a frase deve começar com verbo no infinitivo (ex.: 'controlar a pressão alta')")
        if re.search(r"\d+\s*(mg|mcg|ml|g)\b|\bdoses?\b|\bcomprimidos?\b", frase.lower()):
            erros.append(f"indicacoes.csv: {p}: a frase não pode citar dose, mg nem comprimido")
    for p in sorted(isolados - com_indicacao):
        erros.append(f"indicacoes.csv: {p!r} está em remedios.csv e não tem 'para que serve'")

    for l in t["farmacia_popular.csv"]:
        p = l["principio_ativo"]
        if p not in conhecidos:
            erros.append(f"farmacia_popular.csv: princípio {p!r} não existe em remedios.csv")
        if l["gratuito"] not in ("sim", "nao"):
            erros.append(f"farmacia_popular.csv: gratuito inválido em {p}: {l['gratuito']!r}")
        if not l["concentracao"].strip() or not l["indicacao_programa"].strip():
            erros.append(f"farmacia_popular.csv: {p}: concentracao e indicacao_programa são obrigatórias")
        if l["gratuito"] == "sim" and not [d for d in l["documentos"].split(";") if d.strip()]:
            erros.append(f"farmacia_popular.csv: {p}: remédio gratuito precisa listar os documentos")

    tipos = set()
    for l in t["tipos_receita.csv"]:
        if l["tipo_receita"] not in TIPOS_RECEITA:
            erros.append(f"tipos_receita.csv: tipo inválido: {l['tipo_receita']!r}")
        if l["tipo_receita"] in tipos:
            erros.append(f"tipos_receita.csv: tipo repetido: {l['tipo_receita']}")
        tipos.add(l["tipo_receita"])
        v = l["validade_dias"].strip()
        if v and not (v.isdigit() and int(v) > 0):
            erros.append(f"tipos_receita.csv: validade_dias inválida em {l['tipo_receita']}: {v!r}")
    for tipo in sorted(usados - tipos):
        erros.append(f"tipos_receita.csv: o tipo {tipo!r} é usado em remedios.csv e não tem linha")
    return erros


if __name__ == "__main__":
    problemas = validar()
    print("\n".join(problemas) if problemas else "tabelas ok")
    sys.exit(1 if problemas else 0)
