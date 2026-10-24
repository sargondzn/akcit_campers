"""Escalonador (spec §9, passo 4): conduta → frase fixa, resumo e link. Sem modelo."""

from __future__ import annotations

from datetime import timedelta

from harness import resumo as montar_resumo
from harness.contratos import Conduta, MensagemSaida
from harness.ferramentas.registro import ContextoExecucao
from harness.guardrails import frases, regras_fixas


def escalar(conduta: Conduta, ctx: ContextoExecucao) -> list[MensagemSaida]:
    ctx.estado.condutas.append(conduta)
    if conduta.nivel == "ligue_192":
        return [regras_fixas.mensagem_192()]
    if conduta.nivel == "atendimento_24h":
        resumo = montar_resumo.montar(ctx, "escalonamento", conduta.motivo, ctx.agora - timedelta(days=7),
                                      perguntas_para_profissional=[f"{conduta.motivo}: o que fazer agora?"])
        ctx.repo.salvar_resumo(resumo)
        return [MensagemSaida(tipo="texto", texto=frases.CONDUTA_24H),
                MensagemSaida(tipo="resumo", texto="Preparei um resumo para você mostrar ao profissional.",
                              resumo_id=resumo.resumo_id)]
    texto = frases.CONDUTA_OBSERVAR
    if ctx.repo.obter_consultas(ctx.idoso_id, ctx.agora):
        texto += " Vou incluir isso na página da próxima consulta."
    return [MensagemSaida(tipo="texto", texto=texto)]
