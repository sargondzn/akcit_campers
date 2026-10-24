"""Único lugar que cria modelos (spec §3.2). Trocar de modelo ou provedor = mudar só aqui."""

from __future__ import annotations

from typing import Literal

from agno.models.openai.responses import OpenAIResponses

from harness.config import CONFIG


class ChaveAusente(RuntimeError):
    pass


def modelo(papel: Literal["visao", "conversa"]) -> OpenAIResponses:
    if not CONFIG.openai_api_key:
        raise ChaveAusente("OPENAI_API_KEY não definida no .env")
    return OpenAIResponses(
        id=CONFIG.modelo_visao if papel == "visao" else CONFIG.modelo_conversa,
        api_key=CONFIG.openai_api_key,
        timeout=CONFIG.tempo_max_chamada_s,
        max_retries=CONFIG.novas_tentativas,
    )
