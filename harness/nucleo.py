"""processar_mensagem e processar_evento (C1): a ordem fixa do spec §5.

1. Percepção → 2. Regras fixas → 3. Contexto → 4. Rota → 5. Auditor → 6. Fala → registro de passos
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from harness import fala as tts
from harness.agentes import Agentes
from harness.contratos import (
    Botao, EventoAgendado, MensagemEntrada, MensagemSaida, RespostaHarness,
)
from harness.estado import EstadoMensagem
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos import diario as fluxo_diario
from harness.fluxos import leitura as fluxo_leitura
from harness.fluxos import relato_consulta as fluxo_relato
from harness.guardrails import auditor, confirmacao, frases, regras_fixas
from harness.percepcao import contexto as percepcao_contexto

logging.getLogger("agno").setLevel(logging.WARNING)
log = logging.getLogger("harness")

FRASE_MOTIVO_E8 = "O motivo exato para ela, só o médico que receitou pode dizer."


def _agentes_padrao() -> Agentes:
    from harness.agentes import AgentesAgno

    return AgentesAgno()


def _erros_de_servico() -> tuple[type[BaseException], ...]:
    from harness.agentes.modelos import ChaveAusente

    try:
        import openai

        return (ChaveAusente, openai.APIError, openai.APIConnectionError, TimeoutError)
    except ImportError:  # pragma: no cover
        return (ChaveAusente, TimeoutError)


# ---------------- passo 5: Auditor ----------------

def _contexto_auditor(ctx: ContextoExecucao) -> auditor.ContextoAuditor:
    est = ctx.estado
    itens = list(ctx.itens_atuais()) + list(est.itens_proposta)
    for versao in ctx.repo.obter_versoes_lista(ctx.idoso_id, ctx.agora - timedelta(days=3650)):
        itens += versao.itens
    return auditor.ContextoAuditor(
        itens=itens, quantidades_estoque=[r.quantidade for r in ctx.repo.obter_estoque(ctx.idoso_id)],
        tem_alerta=bool(est.alertas), tem_conduta=bool(est.condutas), tem_info=bool(est.infos),
    )


def auditar(mensagens: list[MensagemSaida], ctx: ContextoExecucao) -> list[MensagemSaida]:
    contexto = _contexto_auditor(ctx)
    saida = []
    for m in mensagens:
        resultado = auditor.verificar(m.texto, contexto)
        if resultado.aprovado:
            saida.append(m)
            continue
        ctx.estado.passo("bloqueio_auditor", f"{resultado.motivos} | {m.texto}")
        saida.append(MensagemSaida(tipo="texto", texto=resultado.texto_final))
    return saida


# ---------------- passo 6: Fala ----------------

def _com_fala(mensagens: list[MensagemSaida], ctx: ContextoExecucao) -> None:
    for m in mensagens:
        if m.tipo == "lista_para_confirmar" or len(m.texto) > tts.LIMITE_CARACTERES:
            continue
        try:
            m.audio = tts.falar(m.texto)
        except Exception as erro:  # sem voz, a resposta sai só em texto
            ctx.estado.passo("resultado", f"fala indisponível: {erro}")
        return


def _finalizar(mensagens: list[MensagemSaida], ctx: ContextoExecucao, falar: bool, erro: bool = False) -> RespostaHarness:
    if not erro:
        mensagens = auditar(mensagens, ctx)
    if falar:
        _com_fala(mensagens, ctx)
    for m in mensagens:
        ctx.estado.passo("resposta", m.texto, agente=m.tipo)
    for passo in ctx.estado.passos:
        try:
            ctx.repo.registrar_passo(passo)
        except Exception:  # registro de passos é P1: nunca derruba a resposta
            break
    estado = "erro" if erro else ("aguardando_confirmacao" if ctx.estado.pendencia_criada else "ok")
    return RespostaHarness(mensagens=mensagens, estado=estado)


# ---------------- passos 1 a 4 ----------------

def _rota_texto(texto: str, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    pendencias = ctx.repo.obter_pendencias(ctx.conta_id)
    contexto = percepcao_contexto.montar(ctx)
    ctx.estado.passo("contexto", contexto[:300])
    aberta = {p.tipo: p for p in pendencias}
    if "diario_aberto" in aberta:
        return fluxo_diario.executar_diario(texto, ctx, agentes, contexto, pendencia=aberta["diario_aberto"])
    if "relato_consulta" in aberta:
        return fluxo_relato.executar_relato(texto, aberta["relato_consulta"], ctx, agentes)

    resultado = agentes.conversar(texto, contexto, ctx, ctx.estado)
    if resultado.membro == "diario":
        return fluxo_diario.executar_diario(texto, ctx, agentes, contexto, saida=resultado.diario)
    resposta = resultado.texto or frases.NAO_ENTENDI
    if ctx.estado.chamadas_ferramenta > 5 and not resultado.texto:
        resposta = frases.LIMITE
    if ctx.estado.infos and "médico que receitou" not in resposta:   # E8: a frase fixa vai inteira
        resposta = f"{resposta.rstrip()} {FRASE_MOTIVO_E8}"
    mensagens = [MensagemSaida(tipo="texto", texto=resposta, botoes=list(ctx.estado.botoes_extra))]
    if ctx.estado.pediu_foto:
        mensagens.append(MensagemSaida(
            tipo="pedido_de_foto", texto=f"Pode mandar a foto da {ctx.estado.pediu_foto}.",
            botoes=[Botao(rotulo="Tirar foto", abre="camera"), Botao(rotulo="Escolher da galeria", abre="galeria")]))
    return mensagens


def processar_mensagem(entrada: MensagemEntrada, repo, agentes: Agentes | None = None) -> RespostaHarness:
    estado = EstadoMensagem(entrada.mensagem_id, entrada.conta_id, entrada.idoso_id)
    ctx = ContextoExecucao(repo, entrada.conta_id, entrada.idoso_id, estado, datetime.now())
    try:
        agentes = agentes or _agentes_padrao()
        # 1. Percepção
        if entrada.tipo == "acao" and entrada.acao:
            estado.passo("percepcao", f"acao {entrada.acao.tipo}")
            return _finalizar(confirmacao.tratar(entrada.acao, ctx, agentes), ctx, falar=True)
        texto = (entrada.texto or "").strip()
        if entrada.tipo == "audio" and entrada.anexo:
            from harness.percepcao import escuta

            texto = escuta.transcrever(entrada.anexo.caminho)
            estado.passo("percepcao", f"transcrição: {texto}")
            if not texto:
                return _finalizar([MensagemSaida(tipo="texto", texto=frases.NAO_OUVI,
                                                 botoes=[Botao(rotulo="Gravar de novo", abre="gravar")])], ctx, falar=True)
        # 2. Regras fixas (antes de qualquer agente)
        if texto and (conduta := regras_fixas.checar(texto)):
            estado.passo("regra_fixa", conduta.regra_id)
            estado.condutas.append(conduta)
            return _finalizar([regras_fixas.tratar_alarme(texto, conduta, repo, entrada.idoso_id)], ctx, falar=True)
        # 3 e 4. Contexto e rota
        if entrada.tipo in ("foto", "pdf") and entrada.anexo:
            mensagens = fluxo_leitura.executar_leitura(entrada, ctx, agentes)
        elif texto:
            mensagens = _rota_texto(texto, ctx, agentes)
        else:
            mensagens = [MensagemSaida(tipo="texto", texto=frases.NAO_ENTENDI)]
        return _finalizar(mensagens, ctx, falar=True)
    except _erros_de_servico() as erro:
        log.warning("serviço indisponível: %s", type(erro).__name__)
        estado.passo("resultado", f"erro de serviço: {type(erro).__name__}")
        return _finalizar([MensagemSaida(tipo="texto", texto=frases.INDISPONIVEL)], ctx, falar=False, erro=True)


def processar_evento(evento: EventoAgendado, repo, agentes: Agentes | None = None) -> RespostaHarness:
    from harness import eventos

    estado = EstadoMensagem(f"evento:{evento.tipo}", evento.conta_id, evento.idoso_id)
    ctx = ContextoExecucao(repo, evento.conta_id, evento.idoso_id, estado, evento.disparado_em)
    try:
        agentes = agentes or _agentes_padrao()
        return _finalizar(eventos.tratar(evento, ctx, agentes), ctx, falar=True)
    except _erros_de_servico() as erro:
        log.warning("serviço indisponível no evento: %s", type(erro).__name__)
        return _finalizar([], ctx, falar=False, erro=True)
