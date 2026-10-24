"""Configuração do harness: lê o `.env` da raiz e as variáveis LLM_*, STT_*, TTS_* (spec §3)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")
os.environ.setdefault("AGNO_TELEMETRY", "false")


@dataclass(frozen=True)
class Config:
    openai_api_key: str
    modelo_visao: str
    modelo_conversa: str
    stt_modelo: str
    tts_voz: str
    caminho_vozes: Path
    caminho_armazenamento: Path
    tempo_max_chamada_s: int = 60
    novas_tentativas: int = 2
    orcamento_mensagem_s: int = 240     # HA-D5
    max_paginas_pdf: int = 3            # HA-D5
    limite_ferramentas: int = 5         # D21


def carregar() -> Config:
    armazenamento = Path(os.environ.get("CAMINHO_ARMAZENAMENTO", RAIZ / "armazenamento"))
    return Config(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        modelo_visao=os.environ.get("LLM_MODELO_VISAO", "gpt-6-luna"),
        modelo_conversa=os.environ.get("LLM_MODELO_CONVERSA", "gpt-6-luna"),
        stt_modelo=os.environ.get("STT_MODELO", "small"),
        tts_voz=os.environ.get("TTS_VOZ", "pt_BR-faber-medium"),
        caminho_vozes=Path(os.environ.get("CAMINHO_VOZES", armazenamento / "vozes")),
        caminho_armazenamento=armazenamento,
    )


CONFIG = carregar()
