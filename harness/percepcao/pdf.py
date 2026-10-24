"""PDF da receita (spec §6.1): texto, se houver; senão, páginas como imagem."""

from __future__ import annotations

from pathlib import Path

from harness.config import CONFIG


def extrair_texto(caminho: str) -> str:
    from pypdf import PdfReader

    leitor = PdfReader(caminho)
    return "\n".join((pagina.extract_text() or "") for pagina in leitor.pages[: CONFIG.max_paginas_pdf]).strip()


def paginas_como_imagem(caminho: str, pasta_saida: Path) -> list[str]:
    import pypdfium2 as pdfium

    pasta_saida.mkdir(parents=True, exist_ok=True)
    documento = pdfium.PdfDocument(caminho)
    caminhos = []
    for indice in range(min(len(documento), CONFIG.max_paginas_pdf)):   # HA-D5: no máximo 3 páginas
        imagem = documento[indice].render(scale=2).to_pil()
        destino = pasta_saida / f"{Path(caminho).stem}_p{indice + 1}.png"
        imagem.save(destino)
        caminhos.append(str(destino))
    return caminhos
