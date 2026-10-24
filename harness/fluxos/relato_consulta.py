"""Relato da consulta (E2, spec §11.3). Relato falado não muda a lista."""

from __future__ import annotations

from harness.agentes import Agentes
from harness.contratos import MensagemSaida, Pendencia
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos.base import executar
from harness.guardrails import frases


def executar_relato(texto: str, pendencia: Pendencia, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    saidas: list[MensagemSaida] = []
    c: dict = {}

    def estruturar(c):
        c["relato"] = agentes.estruturar_relato(texto, ctx.estado)

    def registrar(c):
        ctx.repo.registrar_relato_consulta(pendencia.dados["consulta_id"], c["relato"].model_dump())
        ctx.repo.resolver_pendencia(pendencia.pendencia_id, "resolvida")
        texto_saida = frases.RELATO_SALVO
        if c["relato"].exames_pedidos:
            texto_saida += " Exames pedidos: " + frases.juntar(c["relato"].exames_pedidos) + "."
        if c["relato"].retorno_em:
            texto_saida += f" Retorno: {c['relato'].retorno_em}. Quando souber a data e a hora, me conte que eu anoto."
        saidas.append(MensagemSaida(tipo="texto", texto=texto_saida))

    def receita_nova(c):
        if c["relato"].mudancas_citadas:
            saidas.append(MensagemSaida(tipo="texto", texto=frases.RELATO_RECEITA))

    executar("relato_consulta", [estruturar, registrar, receita_nova], c)
    return saidas
