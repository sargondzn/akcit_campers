"""Fluxo do diário (spec §9): Diário → regras de gravidade → Escalonador."""

from __future__ import annotations

from harness import dados_ponte as dados
from harness import escalonador
from harness.agentes import Agentes
from harness.agentes.esquemas import SaidaDiario
from harness.contratos import MensagemSaida, Pendencia, SintomaEstruturado
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos.base import executar

MAX_PERGUNTAS = 2


def executar_diario(texto: str, ctx: ContextoExecucao, agentes: Agentes, contexto: str,
                    pendencia: Pendencia | None = None, saida: SaidaDiario | None = None) -> list[MensagemSaida]:
    saidas: list[MensagemSaida] = []
    acumulado = f"{pendencia.dados.get('texto', '')} {texto}".strip() if pendencia else texto
    perguntas = pendencia.dados.get("perguntas", 0) if pendencia else 0
    c: dict = {"saida": saida if not pendencia else None}

    def estruturar(c):
        if c["saida"] is None:
            c["saida"] = agentes.estruturar_sintoma(acumulado, contexto, ctx.estado)

    def perguntar(c):
        s: SaidaDiario = c["saida"]
        if s.pergunta and perguntas < MAX_PERGUNTAS:
            dados_p = {"texto": acumulado, "perguntas": perguntas + 1}
            if pendencia:
                ctx.repo.atualizar_pendencia(pendencia.pendencia_id, dados_p)
            else:
                ctx.repo.criar_pendencia(ctx.conta_id, "diario_aberto", dados_p)
            saidas.append(MensagemSaida(tipo="texto", texto=s.pergunta))
            c["_parar"] = True
        elif pendencia:
            ctx.repo.resolver_pendencia(pendencia.pendencia_id, "resolvida")

    def avaliar(c):
        s: SaidaDiario = c["saida"]
        sintoma = SintomaEstruturado(descricao=s.descricao or acumulado, sintomas=s.sintomas, inicio=s.inicio,
                                     intensidade=s.intensidade, sinais={sinal: True for sinal in s.sinais})
        texto_alarme = " ".join([acumulado, sintoma.descricao, *s.sinais]).replace("_", " ")
        conduta = dados.detectar_alarme(texto_alarme) or dados.avaliar_gravidade(sintoma)   # segurança dupla
        ctx.repo.registrar_sintoma(ctx.idoso_id, sintoma, conduta)
        c["conduta"] = conduta

    def escalar(c):
        saidas.extend(escalonador.escalar(c["conduta"], ctx))

    executar("diario", [estruturar, perguntar, avaliar, escalar], c)
    return saidas
