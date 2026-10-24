"""Conciliação (E1, spec §7): compara a receita nova com a lista, sem modelo.

`conciliar` é o C7 da avaliação. A Seri nunca decide tirar ou manter: só mostra e pergunta.
"""

from __future__ import annotations

from typing import Literal

from harness import dados_ponte as dados
from harness.contratos import ItemLido, Mudanca

Escopo = Literal["toda_lista", "medico", "acrescimo"]


def _chave(item: ItemLido) -> frozenset[str]:
    return frozenset(item.principio_ativo) if item.principio_ativo else frozenset({dados.texto_normalizado(item.nome_lido)})


def _mesmo_medico(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    a, b = dados.texto_normalizado(a), dados.texto_normalizado(b)
    return a == b or a in b or b in a


def _conc(c: str | None) -> str:
    return dados.texto_normalizado(c or "").replace(" ", "")


def no_escopo(lista_atual: list[ItemLido], escopo: Escopo, prescritor: str | None) -> list[ItemLido]:
    ativos = [i for i in lista_atual if i.status not in ("retirado", "ilegivel")]
    if escopo == "toda_lista":
        return ativos
    if escopo == "medico":
        return [i for i in ativos if _mesmo_medico(i.prescritor, prescritor)]
    return []


def conciliar(lista_atual: list[ItemLido], itens_novos: list[ItemLido], escopo: Escopo,
              prescritor: str | None = None) -> list[Mudanca]:
    comparar = no_escopo(lista_atual, escopo, prescritor)
    # no acréscimo, o mesmo remédio que já existe ainda é comparado (não vira duplicado silencioso)
    if escopo == "acrescimo":
        chaves_novas = {_chave(n) for n in itens_novos}
        comparar = [i for i in lista_atual if i.status not in ("retirado", "ilegivel") and _chave(i) in chaves_novas]

    anteriores = {_chave(i): i for i in comparar}
    mudancas: list[Mudanca] = []
    vistos: set[frozenset[str]] = set()
    for novo in itens_novos:
        chave = _chave(novo)
        antigo = anteriores.get(chave)
        if antigo is None:
            mudancas.append(Mudanca(tipo="novo", item_novo_id=novo.item_id))
            continue
        vistos.add(chave)
        mudou = []
        if _conc(novo.concentracao) and _conc(novo.concentracao) != _conc(antigo.concentracao):
            mudou.append("concentracao")
        if novo.unidades_por_dose is not None and novo.unidades_por_dose != antigo.unidades_por_dose:
            mudou.append("unidades_por_dose")
        if novo.horarios and sorted(novo.horarios) != sorted(antigo.horarios):
            mudou.append("horarios")
        nome_dif = dados.texto_normalizado(novo.nome_lido).split(" ")[0] != dados.texto_normalizado(antigo.nome_lido).split(" ")[0]
        mudancas.append(Mudanca(tipo="alterado" if mudou else "mantido", item_novo_id=novo.item_id,
                                item_anterior_id=antigo.item_id, o_que_mudou=mudou, nome_diferente=nome_dif))
    if escopo != "acrescimo":
        for chave, antigo in anteriores.items():
            if chave not in vistos:
                mudancas.append(Mudanca(tipo="ausente", item_anterior_id=antigo.item_id))
    return mudancas


def lista_resultante(lista_atual: list[ItemLido], itens_novos: list[ItemLido],
                     mudancas: list[Mudanca]) -> list[ItemLido]:
    """Lista proposta: a atual com as trocas aplicadas. Ausente continua até a decisão."""
    novos = {i.item_id: i for i in itens_novos}
    substituidos = {m.item_anterior_id: m.item_novo_id for m in mudancas if m.tipo in ("alterado", "mantido")}
    resultado: list[ItemLido] = []
    for item in lista_atual:
        if item.status == "retirado":
            continue
        if item.item_id in substituidos:
            novo = novos[substituidos[item.item_id]]
            # o item novo herda o id do antigo, para manter o histórico e o estoque
            resultado.append(novo.model_copy(update={"item_id": item.item_id}))
        else:
            resultado.append(item.model_copy())
    for m in mudancas:
        if m.tipo == "novo":
            resultado.append(novos[m.item_novo_id].model_copy())
    return resultado


def aplicar_decisoes(itens: list[ItemLido], mudancas: list[Mudanca]) -> tuple[list[ItemLido], list[str]]:
    """Na confirmação: 'o médico tirou' → retirado; sem decisão = 'não sei' (spec §7.4)."""
    retirar = {m.item_anterior_id for m in mudancas if m.tipo == "ausente" and m.decisao == "medico_tirou"}
    nao_sei = {m.item_anterior_id for m in mudancas if m.tipo == "ausente" and m.decisao in (None, "nao_sei")}
    finais: list[ItemLido] = []
    pontos: list[str] = []
    for item in itens:
        if item.item_id in retirar:
            finais.append(item.model_copy(update={"status": "retirado"}))
            continue
        status = item.status
        if status in ("proposto", "confirmado"):
            status = "confirmado"
        finais.append(item.model_copy(update={"status": status}))
        if item.item_id in nao_sei:
            pontos.append(f"{item.nome_lido} não veio na receita nova: confirmar se continua")
    return finais, pontos
