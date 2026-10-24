"""Eventos agendados (spec §5.1): verificação diária (E4), véspera e pós-consulta (E2)."""

from __future__ import annotations

from datetime import timedelta

from harness import dados_ponte as dados
from harness import estoque as calc_estoque
from harness.agentes import Agentes
from harness.contratos import Botao, EventoAgendado, MensagemSaida
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos import preparo
from harness.guardrails import frases


def _farmacia_popular(nome: str, principios: list[str], ctx: ContextoExecucao) -> str:
    for p in principios:
        info = dados.info_remedio(p)
        if info and info.farmacia_popular:
            ctx.estado.infos.append(info)
            texto = frases.FARMACIA_POPULAR.format(nome=nome, documentos=frases.juntar(info.documentos_farmacia_popular))
            if dados.texto_normalizado(p) not in dados.texto_normalizado(nome):   # nome de marca
                texto += " " + frases.OUTRA_MARCA
            return " " + texto
    return ""


def verificacao_diaria(ctx: ContextoExecucao) -> list[MensagemSaida]:
    itens = ctx.itens_atuais()
    ctx.estado.itens_proposta = itens
    saidas = []
    estados = calc_estoque.calcular(itens, ctx.repo.obter_cronograma(ctx.idoso_id),
                                    ctx.repo.obter_doses(ctx.idoso_id, ctx.agora - timedelta(days=90)),
                                    ctx.repo.obter_estoque(ctx.idoso_id), ctx.agora)
    por_id = {i.item_id: i for i in itens}
    for e in calc_estoque.avisos_de_estoque(estados):
        item = por_id[e.item_id]
        texto = frases.ESTOQUE_ACABANDO.format(nome=item.nome_lido, dia=f"{e.acaba_em:%d/%m}")
        texto += _farmacia_popular(item.nome_lido, item.principio_ativo, ctx)
        saidas.append(MensagemSaida(tipo="aviso_estoque", texto=texto,
                                    botoes=[Botao(rotulo="Comprei mais", abre="teclado")]))
    for item, vence in calc_estoque.receitas_vencendo(itens, ctx.agora.date()):   # P1
        saidas.append(MensagemSaida(tipo="aviso_estoque",
                                    texto=frases.RECEITA_VENCENDO.format(nome=item.nome_lido, dia=f"{vence:%d/%m}")))
    return saidas


def tratar(evento: EventoAgendado, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    if evento.tipo == "verificacao_diaria":
        return verificacao_diaria(ctx)
    if evento.tipo == "vespera_consulta":
        ctx.estado.itens_proposta = ctx.itens_atuais()
        return preparo.executar_preparo(evento.consulta_id, ctx, agentes)
    if evento.tipo == "pos_consulta":
        return preparo.perguntar_pos_consulta(evento.consulta_id, ctx)
    return []
