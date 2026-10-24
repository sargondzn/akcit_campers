"""Ponte para as ferramentas de dados (C2–C4, C8).

Usa cada função real de `dados/` que existir; o que ainda não existe continua no stub de B
(hoje, só `info_remedio`, C8). Com HARNESS_DADOS_STUB=1, força os stubs (testes e demo).
"""

from __future__ import annotations

import csv
import os
from functools import lru_cache
from pathlib import Path

from harness.stubs import dados as _stub

normalizar = _stub.normalizar
checar_lista = _stub.checar_lista
detectar_alarme = _stub.detectar_alarme
avaliar_gravidade = _stub.avaliar_gravidade
info_remedio = _stub.info_remedio
texto_normalizado = _stub.texto_normalizado
REAIS: list[str] = []          # funções que vieram de `dados/`

if os.environ.get("HARNESS_DADOS_STUB") != "1":
    try:
        from dados.normalizador import normalizar  # noqa: F811
        REAIS.append("normalizar")
    except ImportError:
        pass
    try:
        from dados.farmacovigilante import checar_lista  # noqa: F811
        REAIS.append("checar_lista")
    except ImportError:
        pass
    try:
        from dados.gravidade import avaliar_gravidade, detectar_alarme  # noqa: F811
        REAIS += ["detectar_alarme", "avaliar_gravidade"]
    except ImportError:
        pass
    try:
        from dados.info_remedio import info_remedio  # type: ignore  # noqa: F811
        REAIS.append("info_remedio")
    except ImportError:
        pass

USANDO_STUB = len(REAIS) < 5


@lru_cache(maxsize=1)
def nomes_conhecidos() -> frozenset[str]:
    """Nomes de remédio que o Auditor reconhece: os do stub e, se existirem, os das tabelas de C."""
    nomes = set(_stub.nomes_conhecidos())
    if "normalizar" in REAIS:
        tabelas = Path(__file__).resolve().parent.parent / "dados" / "tabelas"
        for arquivo, colunas in (("remedios.csv", ("principio_ativo", "nome_comercial")), ("sinonimos.csv", ("termo",))):
            caminho = tabelas / arquivo
            if caminho.exists():
                with open(caminho, encoding="utf-8") as f:
                    for linha in csv.DictReader(f):
                        nomes.update(texto_normalizado(linha[c]) for c in colunas if linha.get(c))
    return frozenset(n for n in nomes if n)


@lru_cache(maxsize=1)
def vocabulario_diario() -> dict[str, list[str]] | None:
    """Termos que `avaliar_gravidade` de C reconhece (specs/dados/vocabulario-diario.md)."""
    if "avaliar_gravidade" not in REAIS:
        return None
    try:
        from dados.vocabulario import vocabulario
    except ImportError:
        return None
    return vocabulario()
