"""Normalização de texto compartilhada pelo ETL e pelas ferramentas de dados."""
import re
import unicodedata


def sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def normalizar_texto(texto: str) -> str:
    """Minúsculo, sem acento e sem pontuação extra.

    Mantém dígitos, letras e os símbolos que importam para concentração
    (`,` `.` `/` `%` `+`); o resto vira espaço.
    """
    texto = sem_acento(texto.lower())
    texto = re.sub(r"[^a-z0-9,./%+]+", " ", texto)
    # pontuação solta (fim de frase) não é parte de número nem de nome
    texto = re.sub(r"(?<![0-9])[,.]|[,.](?![0-9])", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()
