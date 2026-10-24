"""Frente `dados` (C): as quatro ferramentas determinísticas que o harness chama (C2, C3, C4)."""
from dados.farmacovigilante import checar_lista
from dados.gravidade import avaliar_gravidade, detectar_alarme
from dados.normalizador import normalizar

__all__ = ["normalizar", "checar_lista", "detectar_alarme", "avaliar_gravidade"]
