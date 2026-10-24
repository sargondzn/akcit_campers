"""C7 — funções isoladas para a avaliação (00-projeto/spec §5, C7)."""

from __future__ import annotations

from types import SimpleNamespace

from harness.contratos import Anexo, ItemLido, SintomaEstruturado
from harness.estado import EstadoMensagem


def _agentes():
    from harness.agentes import AgentesAgno

    return AgentesAgno()


def ler(anexo: Anexo, agentes=None) -> list[ItemLido]:
    """Leitura isolada: Leitor (ou texto do PDF) → Intérprete → pós-processamento, sem conciliação."""
    from harness.config import CONFIG
    from harness.fluxos.leitura import pos_processar
    from harness.percepcao import pdf

    agentes = agentes or _agentes()
    estado = EstadoMensagem("c7", "c7", "c7")
    origem = "receita_foto"
    if anexo.mime == "application/pdf":
        origem = "receita_pdf"
        texto = pdf.extrair_texto(anexo.caminho)
        imagens = [] if len(texto) > 30 else pdf.paginas_como_imagem(anexo.caminho, CONFIG.caminho_armazenamento / "tmp_pdf")
    else:
        texto, imagens = "", [anexo.caminho]
    if imagens:
        leituras = [agentes.ler([img], estado) for img in imagens]
        texto = "\n".join(l.model_dump_json() for l in leituras)
    return pos_processar(agentes.interpretar(texto, estado), origem)


def estruturar(texto: str, agentes=None) -> SintomaEstruturado:
    agentes = agentes or _agentes()
    s = agentes.estruturar_sintoma(texto, "", EstadoMensagem("c7", "c7", "c7"))
    return SintomaEstruturado(descricao=s.descricao, sintomas=s.sintomas, inicio=s.inicio,
                              intensidade=s.intensidade, sinais={x: True for x in s.sinais})


leitor = SimpleNamespace(ler=ler)
diario = SimpleNamespace(estruturar=estruturar)
