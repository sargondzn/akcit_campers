"""Regras fixas (spec §13.1): sinal de alarme vira 192 antes de qualquer agente."""

from __future__ import annotations

from harness import dados_ponte as dados
from harness.contratos import Botao, Conduta, MensagemSaida, SintomaEstruturado
from harness.guardrails import frases


def checar(texto: str) -> Conduta | None:
    return dados.detectar_alarme(texto)


def mensagem_192() -> MensagemSaida:
    return MensagemSaida(tipo="ligue_192", texto=frases.LIGUE_192,
                         botoes=[Botao(rotulo="Ligar 192", abre="tel:192")])


def tratar_alarme(texto: str, conduta: Conduta, repo, idoso_id: str) -> MensagemSaida:
    sintoma = SintomaEstruturado(descricao=texto, sintomas=[conduta.motivo.lower()])
    repo.registrar_sintoma(idoso_id, sintoma, conduta)
    return mensagem_192()
