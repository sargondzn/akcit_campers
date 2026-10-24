"""Frente `dados` (C): as ferramentas determinísticas que o harness chama (C2, C3, C4 e C8) e dois auxiliares.

`texto_normalizado` e `nomes_conhecidos` não são contratos: o harness os usa para comparar nomes de remédio
e para o Auditor achar remédio citado fora da lista.
"""
from dados.farmacovigilante import checar_lista
from dados.gravidade import avaliar_gravidade, detectar_alarme
from dados.info_remedio import info_remedio
from dados.normalizador import nomes_conhecidos, normalizar
from dados.texto import normalizar_texto as texto_normalizado

__all__ = ["normalizar", "checar_lista", "detectar_alarme", "avaliar_gravidade", "info_remedio",
           "texto_normalizado", "nomes_conhecidos"]
