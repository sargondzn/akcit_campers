"""Ponte para as ferramentas de dados (C2–C4, C8).

Usa as funções reais de `dados/` quando C as entregar; até lá, os stubs de B.
Com HARNESS_DADOS_STUB=1, força os stubs (testes e demo).
"""

from __future__ import annotations

import os

from harness.stubs import dados as _stub

normalizar = _stub.normalizar
checar_lista = _stub.checar_lista
detectar_alarme = _stub.detectar_alarme
avaliar_gravidade = _stub.avaliar_gravidade
info_remedio = _stub.info_remedio
nomes_conhecidos = _stub.nomes_conhecidos
texto_normalizado = _stub.texto_normalizado
USANDO_STUB = True

if os.environ.get("HARNESS_DADOS_STUB") != "1":
    try:  # pragma: no cover - depende da entrega de C
        from dados.normalizador import normalizar  # type: ignore  # noqa: F811
        from dados.farmacovigilante import checar_lista  # type: ignore  # noqa: F811
        from dados.gravidade import detectar_alarme, avaliar_gravidade  # type: ignore  # noqa: F811
        from dados.info_remedio import info_remedio  # type: ignore  # noqa: F811
        USANDO_STUB = False
    except ImportError:
        pass
