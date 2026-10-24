"""Subagentes do harness (spec §2.2), construídos com o Agno.

O núcleo e os fluxos falam com `Agentes` (esta interface). A implementação real usa Agno + OpenAI;
os testes usam uma implementação falsa, sem rede (spec §18).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Protocol, TypeVar

from pydantic import BaseModel

from harness.agentes.esquemas import (
    ItensInterpretados, LeituraBruta, PerguntasConsulta, RelatoConsulta, SaidaDiario,
)
from harness.estado import EstadoMensagem

PASTA_PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
T = TypeVar("T", bound=BaseModel)


@lru_cache(maxsize=None)
def prompt(nome: str) -> str:
    return (PASTA_PROMPTS / f"{nome}.md").read_text(encoding="utf-8")


@dataclass
class ResultadoConversa:
    texto: str
    membro: str | None
    diario: SaidaDiario | None = None


class Agentes(Protocol):
    def ler(self, imagens: list[str], estado: EstadoMensagem) -> LeituraBruta: ...
    def interpretar(self, texto: str, estado: EstadoMensagem) -> ItensInterpretados: ...
    def conversar(self, texto: str, contexto: str, ctx, estado: EstadoMensagem) -> ResultadoConversa: ...
    def estruturar_sintoma(self, texto: str, contexto: str, estado: EstadoMensagem) -> SaidaDiario: ...
    def preparar_perguntas(self, fatos: str, candidatas: list[dict], estado: EstadoMensagem) -> PerguntasConsulta: ...
    def estruturar_relato(self, texto: str, estado: EstadoMensagem) -> RelatoConsulta: ...


def _tokens(metricas) -> tuple[int | None, int | None]:
    if metricas is None:
        return None, None
    if isinstance(metricas, dict):
        ent, sai = metricas.get("input_tokens"), metricas.get("output_tokens")
    else:
        ent, sai = getattr(metricas, "input_tokens", None), getattr(metricas, "output_tokens", None)
    if isinstance(ent, list):
        ent = sum(ent)
    if isinstance(sai, list):
        sai = sum(sai)
    return ent, sai


def _como(esquema: type[T], conteudo) -> T:
    if isinstance(conteudo, esquema):
        return conteudo
    if isinstance(conteudo, BaseModel):
        return esquema.model_validate(conteudo.model_dump())
    if isinstance(conteudo, dict):
        return esquema.model_validate(conteudo)
    return esquema.model_validate_json(str(conteudo))


class AgentesAgno:
    """Implementação real: um `Agent` do Agno por subagente e a equipe da Seri (`Team`, modo route)."""

    def _rodar(self, agente, entrada, estado: EstadoMensagem, nome: str, **kwargs):
        inicio = time.monotonic()
        saida = agente.run(entrada, **kwargs)
        ent, sai = _tokens(getattr(saida, "metrics", None))
        modelo = getattr(getattr(agente, "model", None), "id", None)
        estado.passo("agente", str(getattr(saida, "content", ""))[:200], agente=nome,
                     duracao_ms=int((time.monotonic() - inicio) * 1000), modelo=modelo,
                     tokens_entrada=ent, tokens_saida=sai)
        return saida

    def _estruturado(self, nome: str, papel: str, esquema: type[T], entrada, estado: EstadoMensagem,
                     instrucoes: str, **kwargs) -> T:
        from agno.agent import Agent
        from harness.agentes.modelos import modelo

        agente = Agent(name=nome, model=modelo(papel), instructions=instrucoes, output_schema=esquema,
                       telemetry=False)
        saida = self._rodar(agente, entrada, estado, nome, **kwargs)
        try:
            return _como(esquema, saida.content)
        except Exception as erro:  # 1 nova tentativa com o erro (spec §3.2)
            saida = self._rodar(agente, f"{entrada}\n\nSua resposta anterior era inválida ({erro}). Responda de novo no formato pedido.",
                                estado, nome, **kwargs)
            return _como(esquema, saida.content)

    def ler(self, imagens: list[str], estado: EstadoMensagem) -> LeituraBruta:
        from agno.media import Image

        return self._estruturado("leitor", "visao", LeituraBruta, "Transcreva esta imagem.", estado,
                                 prompt("leitor"), images=[Image(filepath=c) for c in imagens])

    def interpretar(self, texto: str, estado: EstadoMensagem) -> ItensInterpretados:
        return self._estruturado("interprete", "conversa", ItensInterpretados, texto, estado, prompt("interprete"))

    def estruturar_sintoma(self, texto: str, contexto: str, estado: EstadoMensagem) -> SaidaDiario:
        return self._estruturado("diario", "conversa", SaidaDiario, f"{contexto}\n\nRelato da cuidadora: {texto}",
                                 estado, prompt("diario"))

    def preparar_perguntas(self, fatos: str, candidatas: list[dict], estado: EstadoMensagem) -> PerguntasConsulta:
        entrada = f"Fatos:\n{fatos}\n\nPerguntas candidatas:\n{json.dumps(candidatas, ensure_ascii=False)}"
        return self._estruturado("preparador", "conversa", PerguntasConsulta, entrada, estado, prompt("preparador"))

    def estruturar_relato(self, texto: str, estado: EstadoMensagem) -> RelatoConsulta:
        return self._estruturado("agenda", "conversa", RelatoConsulta, texto, estado, prompt("agenda_relato"))

    def conversar(self, texto: str, contexto: str, ctx, estado: EstadoMensagem) -> ResultadoConversa:
        from agno.agent import Agent
        from agno.team import Team
        from harness.agentes.modelos import modelo
        from harness.ferramentas.registro import FERRAMENTAS_POR_AGENTE, construir, gancho_limite

        ferramentas = construir(ctx)
        gancho = gancho_limite(estado)
        persona = prompt("persona")

        def membro(nome: str, rotulo: str, papel: str):
            return Agent(
                name=rotulo, role=papel, model=modelo("conversa"),
                instructions=[persona, prompt(nome)], additional_context=contexto,
                tools=[ferramentas[f] for f in FERRAMENTAS_POR_AGENTE[nome]],
                tool_hooks=[gancho], tool_call_limit=5, telemetry=False,
            )

        diario = Agent(name="Diario", role="Organiza relatos de sintoma", model=modelo("conversa"),
                       instructions=prompt("diario"), additional_context=contexto, output_schema=SaidaDiario,
                       telemetry=False)
        equipe = Team(
            name="Seri", mode="route", model=modelo("conversa"),
            members=[
                membro("rotina", "Rotina", "Horários, lista do dia e doses dadas"),
                membro("explicador", "Explicador", "Lista, alertas, para que serve cada remédio e cumprimentos"),
                diario,
                membro("agenda", "Agenda", "Consultas: marcar e consultar"),
                membro("farmacia", "Farmacia", "Estoque, remédio acabando, receita vencendo e Farmácia Popular"),
            ],
            instructions=prompt("coordenadora"), additional_context=contexto, telemetry=False,
        )
        saida = self._rodar(equipe, texto, estado, "coordenadora")
        respostas = getattr(saida, "member_responses", None) or []
        nome_membro = getattr(respostas[-1], "agent_name", None) if respostas else None
        conteudo = saida.content
        if nome_membro == "Diario" or isinstance(conteudo, SaidaDiario):
            try:
                bruto = respostas[-1].content if respostas else conteudo
                return ResultadoConversa(texto="", membro="diario", diario=_como(SaidaDiario, bruto))
            except Exception:
                return ResultadoConversa(texto="", membro="diario", diario=None)
        return ResultadoConversa(texto=str(conteudo or "").strip(), membro=(nome_membro or "").lower() or None)
