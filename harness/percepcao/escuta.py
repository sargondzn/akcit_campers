"""Escuta (spec §8): áudio → texto, local, com faster-whisper. O áudio não sai da máquina."""

from __future__ import annotations

import os
import tempfile
import wave
from functools import lru_cache

from harness.config import CONFIG
from harness.percepcao import ffmpeg


@lru_cache(maxsize=1)
def _modelo():
    from faster_whisper import WhisperModel

    return WhisperModel(CONFIG.stt_modelo, device="cpu", compute_type="int8")


def _amostras(wav: str):
    """WAV 16 kHz mono 16 bits → float32. Evita o decodificador `av` do faster-whisper,
    incompatível com o av 19 instalado junto (o ffmpeg já fez a conversão)."""
    import numpy as np

    with wave.open(wav, "rb") as arquivo:
        bruto = arquivo.readframes(arquivo.getnframes())
    return np.frombuffer(bruto, dtype=np.int16).astype(np.float32) / 32768.0


def transcrever(caminho_audio: str) -> str:
    with tempfile.TemporaryDirectory() as pasta:
        wav = os.path.join(pasta, "audio.wav")
        ffmpeg.converter(caminho_audio, wav, "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le")
        segmentos, _info = _modelo().transcribe(_amostras(wav), language="pt", vad_filter=True)
        return " ".join(s.text.strip() for s in segmentos).strip()
