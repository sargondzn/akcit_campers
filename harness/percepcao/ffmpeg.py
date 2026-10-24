"""Localiza e chama o ffmpeg (conversão de áudio da Escuta e da Fala)."""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
from functools import lru_cache


@lru_cache(maxsize=1)
def caminho() -> str:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    achado = shutil.which("ffmpeg")
    if achado:
        return achado
    # instalado pelo winget e ainda fora do PATH deste processo
    padrao = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages",
                          "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe")
    candidatos = glob.glob(padrao)
    if candidatos:
        return candidatos[0]
    raise FileNotFoundError("ffmpeg não encontrado. Instale (externo.md §1) ou defina FFMPEG no .env.")


def converter(entrada: str, saida: str, *args: str) -> None:
    subprocess.run([caminho(), "-y", "-loglevel", "error", "-i", entrada, *args, saida], check=True)
