"""Harness agêntico da Seriema (Pessoa B). Spec: specs/harness/spec.md.

C1 (para A): processar_mensagem, processar_evento, falar.
C7 (para a avaliação): leitor.ler, auditor.verificar, diario.estruturar, conciliacao.conciliar.
"""

from harness import conciliacao
from harness.fala import falar
from harness.guardrails import auditor
from harness.nucleo import processar_mensagem, processar_evento
from harness import c7 as _c7

leitor = _c7.leitor
diario = _c7.diario

__all__ = ["processar_mensagem", "processar_evento", "falar", "leitor", "auditor", "diario", "conciliacao"]
