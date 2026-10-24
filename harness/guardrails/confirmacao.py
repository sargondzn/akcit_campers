"""Confirmação humana e decisões (spec §13.2): tudo em código, sem agente."""

from __future__ import annotations

from datetime import datetime, timedelta

from harness import conciliacao
from harness import estoque as calc_estoque
from harness.agentes import Agentes
from harness.contratos import Acao, ItemLido, MensagemSaida, Mudanca, Pendencia
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos import leitura
from harness.guardrails import frases


def _pendencia(ctx: ContextoExecucao, pid: str) -> Pendencia | None:
    return next((p for p in ctx.repo.obter_pendencias(ctx.conta_id) if p.pendencia_id == pid), None)


def _proposta(p: Pendencia) -> tuple[list[ItemLido], list[Mudanca]]:
    return ([ItemLido.model_validate(i) for i in p.dados.get("itens", [])],
            [Mudanca.model_validate(m) for m in p.dados.get("mudancas", [])])


def tratar(acao: Acao, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    if acao.tipo == "contar_estoque":
        return _contar_estoque(acao, ctx)
    p = _pendencia(ctx, acao.pendencia_id)
    if p is None:   # já resolvida (clique duplo) ou inexistente
        return [MensagemSaida(tipo="texto", texto=frases.JA_RESOLVIDO)]
    if acao.tipo == "recusar_pendencia":
        ctx.repo.resolver_pendencia(p.pendencia_id, "recusada")
        return [MensagemSaida(tipo="texto", texto=frases.RECUSADO)]
    if acao.tipo == "confirmar_pendencia":
        return _confirmar(p, ctx)
    if acao.tipo == "definir_escopo":
        return _definir_escopo(p, acao, ctx)
    if acao.tipo == "decidir_item":
        return _decidir_item(p, acao, ctx)
    if acao.tipo == "corrigir_item":
        return _corrigir_item(p, acao, ctx, agentes)
    return [MensagemSaida(tipo="texto", texto=frases.NAO_ENTENDI)]


def _confirmar(p: Pendencia, ctx: ContextoExecucao) -> list[MensagemSaida]:
    if p.tipo == "lista_para_confirmar":
        primeira = ctx.repo.obter_lista_atual(ctx.idoso_id) is None
        itens, mudancas = _proposta(p)
        finais, pontos = conciliacao.aplicar_decisoes(itens, mudancas)
        anteriores = ctx.repo.obter_lista_atual(ctx.idoso_id)
        if anteriores:
            pontos = list(dict.fromkeys(anteriores.pontos_para_conferir + pontos))
        ctx.repo.salvar_lista_confirmada(ctx.idoso_id, finais, pontos)
        ctx.repo.resolver_pendencia(p.pendencia_id, "confirmada")
        for outra in ctx.repo.obter_pendencias(ctx.conta_id):
            if outra.tipo == "leitura_baixa_confianca":
                ctx.repo.resolver_pendencia(outra.pendencia_id, "resolvida")
        texto = frases.LISTA_SALVA + (" " + frases.OFERTA_ESTOQUE if primeira else "")
        return [MensagemSaida(tipo="texto", texto=texto)]
    if p.tipo == "mudanca_cronograma":
        ctx.repo.alterar_cronograma(ctx.idoso_id, p.dados["mudancas"])
        ctx.repo.resolver_pendencia(p.pendencia_id, "confirmada")
        return [MensagemSaida(tipo="texto", texto="Pronto, o horário foi atualizado na Rotina.")]
    if p.tipo == "consulta_para_confirmar":
        ctx.repo.salvar_consulta(ctx.idoso_id, datetime.fromisoformat(p.dados["data_hora"]),
                                 p.dados["profissional"], p.dados.get("local"))
        ctx.repo.resolver_pendencia(p.pendencia_id, "confirmada")
        return [MensagemSaida(tipo="texto", texto=frases.CONSULTA_SALVA)]
    return [MensagemSaida(tipo="texto", texto=frases.JA_RESOLVIDO)]


def _definir_escopo(p: Pendencia, acao: Acao, ctx: ContextoExecucao) -> list[MensagemSaida]:
    if p.tipo != "escopo_receita":
        return [MensagemSaida(tipo="texto", texto=frases.JA_RESOLVIDO)]
    novos = [ItemLido.model_validate(i) for i in p.dados["itens"]]
    ctx.repo.resolver_pendencia(p.pendencia_id, "resolvida")
    return leitura.propor(ctx, novos, acao.dados.get("escopo", "toda_lista"), p.dados.get("prescritor"))


def _decidir_item(p: Pendencia, acao: Acao, ctx: ContextoExecucao) -> list[MensagemSaida]:
    itens, mudancas = _proposta(p)
    alvo = acao.dados.get("item_anterior_id")
    decisao = acao.dados.get("decisao")
    for m in mudancas:
        if m.tipo == "ausente" and m.item_anterior_id == alvo:
            m.decisao = decisao
    ctx.repo.atualizar_pendencia(p.pendencia_id, {**p.dados, "mudancas": [m.model_dump(mode="json") for m in mudancas]})
    ctx.estado.itens_proposta = itens
    nome = next((i.nome_lido for i in itens if i.item_id == alvo), "O remédio")
    return [MensagemSaida(tipo="texto", texto=f"Anotado: {nome} {frases.DECISAO.get(decisao, '')}.")]


def _corrigir_item(p: Pendencia, acao: Acao, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    itens, mudancas = _proposta(p)
    alvo = acao.dados.get("item_id")
    interpretado = agentes.interpretar(acao.dados.get("texto", ""), ctx.estado)
    corrigidos = leitura.pos_processar(interpretado, "digitado")
    if not corrigidos:
        return [MensagemSaida(tipo="texto", texto=frases.LIMITE)]
    novo = corrigidos[0]
    atualizados = [novo.model_copy(update={"item_id": i.item_id, "origem": "digitado",
                                           "prescritor": i.prescritor, "data_receita": i.data_receita})
                   if i.item_id == alvo else i for i in itens]
    ctx.repo.resolver_pendencia(p.pendencia_id, "resolvida")
    anteriores = ctx.itens_atuais()
    return leitura.emitir_proposta(ctx, atualizados, mudancas, anteriores)


def _contar_estoque(acao: Acao, ctx: ContextoExecucao) -> list[MensagemSaida]:
    item_id, quantidade = acao.dados.get("item_id"), float(acao.dados.get("quantidade", 0))
    item = next((i for i in ctx.itens_atuais() if i.item_id == item_id), None)
    if not item or quantidade <= 0:
        return [MensagemSaida(tipo="texto", texto=frases.JA_RESOLVIDO)]
    atuais = {r.item_id: r.quantidade for r in ctx.repo.obter_estoque(ctx.idoso_id)}
    restante = 0.0
    if item_id in atuais:
        for e in calc_estoque.calcular([item], ctx.repo.obter_cronograma(ctx.idoso_id),
                                       ctx.repo.obter_doses(ctx.idoso_id, ctx.agora - timedelta(days=90)),
                                       ctx.repo.obter_estoque(ctx.idoso_id), ctx.agora):
            restante = e.estoque_estimado
    total = restante + quantidade
    ctx.repo.registrar_estoque(item_id, total, ctx.agora, "caixa_foto")
    ctx.estado.itens_proposta = [item]
    return [MensagemSaida(tipo="texto", texto=frases.ESTOQUE_REGISTRADO.format(quantidade=f"{total:g} unidades",
                                                                               nome=item.nome_lido))]
