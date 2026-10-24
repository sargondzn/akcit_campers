"""Fala (spec §14): texto → MP3, local, com Piper. Cache por texto."""

from __future__ import annotations

import hashlib
import os
import tempfile
import wave
from functools import lru_cache

from harness.config import CONFIG
from harness.contratos import Anexo
from harness.percepcao import ffmpeg

LIMITE_CARACTERES = 400


class FalaIndisponivel(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _voz():
    from piper import PiperVoice

    caminho = CONFIG.caminho_vozes / f"{CONFIG.tts_voz}.onnx"
    if not caminho.exists():
        raise FalaIndisponivel(f"Voz do Piper não encontrada em {caminho} (externo.md §6.2)")
    return PiperVoice.load(str(caminho))


def falar(texto: str) -> Anexo:
    pasta = CONFIG.caminho_armazenamento / "seri_audio"
    pasta.mkdir(parents=True, exist_ok=True)
    nome = hashlib.sha1(f"{CONFIG.tts_voz}|{texto}".encode()).hexdigest()[:16]
    mp3 = pasta / f"{nome}.mp3"
    if not mp3.exists():
        voz = _voz()
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "fala.wav")
            with wave.open(wav, "wb") as arquivo:
                voz.synthesize_wav(texto, arquivo)
            ffmpeg.converter(wav, str(mp3), "-codec:a", "libmp3lame", "-q:a", "4")
    return Anexo(caminho=str(mp3), mime="audio/mpeg", tamanho_bytes=mp3.stat().st_size)
