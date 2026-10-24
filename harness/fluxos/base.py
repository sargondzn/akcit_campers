"""Fluxos fixos como `Workflow` do Agno (spec §2.4, HA-D1).

Cada passo é uma função Python que lê e escreve um dicionário de contexto. Um passo pode
parar o fluxo com `ctx["_parar"] = True` (ex.: a leitura precisa perguntar o escopo).
"""

from __future__ import annotations

from typing import Callable

from agno.workflow import Step, Workflow
from agno.workflow.types import StepInput, StepOutput

Passo = Callable[[dict], None]


def executar(nome: str, passos: list[Passo], ctx: dict) -> dict:
    erros: list[BaseException] = []

    def envolver(funcao: Passo):
        def executor(_entrada: StepInput) -> StepOutput:
            if ctx.get("_parar") or erros:
                return StepOutput(content="pulado", stop=True)
            try:
                funcao(ctx)
            except BaseException as erro:  # o erro sai do fluxo inteiro, não fica escondido no Agno
                erros.append(erro)
                return StepOutput(content=f"erro: {erro}", stop=True, success=False)
            return StepOutput(content=funcao.__name__, stop=bool(ctx.get("_parar")))
        executor.__name__ = funcao.__name__
        return executor

    fluxo = Workflow(name=nome, steps=[Step(name=p.__name__, executor=envolver(p), max_retries=0) for p in passos],
                     telemetry=False)
    fluxo.run(input=nome)
    if erros:
        raise erros[0]
    return ctx
