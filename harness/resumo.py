"""Monta o `Resumo` (C5) do escalonamento e do preparo da consulta. A gera o PDF e o link."""

from __future__ import annotations

import uuid
from datetime import datetime

from harness import dados_ponte as dados
from harness.contratos import Alerta, ItemParaChecar, Resumo
from harness.ferramentas.registro import ContextoExecucao


def doses_perdidas(ctx: ContextoExecucao, desde: datetime) -> list[dict]:
    nomes = {i.item_id: i.nome_lido for i in ctx.itens_atuais()}
    horarios = {h.horario_id: h for h in ctx.repo.obter_cronograma(ctx.idoso_id)}
    saida = []
    for d in ctx.repo.obter_doses(ctx.idoso_id, desde):
        if d.status != "tomada" and (h := horarios.get(d.horario_id)):
            saida.append({"item_id": h.item_id, "nome": nomes.get(h.item_id, "?"), "horario_previsto": d.previsto.isoformat()})
    return saida


def sintomas(ctx: ContextoExecucao, desde: datetime) -> list[dict]:
    return [{**r.sintoma.model_dump(), "registrado_em": r.registrado_em.isoformat(), "conduta": r.conduta.nivel}
            for r in ctx.repo.obter_diario(ctx.idoso_id, desde)]


def alertas_da_lista(ctx: ContextoExecucao) -> list[Alerta]:
    return dados.checar_lista([ItemParaChecar(item_id=i.item_id, principio_ativo=i.principio_ativo)
                               for i in ctx.itens_atuais()])


def montar(ctx: ContextoExecucao, tipo: str, motivo: str, desde: datetime, **extras) -> Resumo:
    itens = ctx.itens_atuais()
    infos = [info for i in itens for p in i.principio_ativo if (info := dados.info_remedio(p))]
    alertas = alertas_da_lista(ctx)
    ctx.estado.alertas += alertas
    ctx.estado.infos += infos
    return Resumo(
        resumo_id=uuid.uuid4().hex[:12], tipo=tipo,
        idoso_apelido=ctx.repo.obter_idoso(ctx.idoso_id).get("apelido", ""),
        periodo_inicio=desde.date(), periodo_fim=ctx.agora.date(), motivo=motivo, lista_atual=itens,
        doses_perdidas=doses_perdidas(ctx, desde), sintomas=sintomas(ctx, desde), alertas=alertas, info=infos,
        gerado_em=ctx.agora, **extras,
    )
