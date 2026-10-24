def _quebrar(texto: str, limite: int = 78) -> list[str]:
    palavras = texto.split()
    linhas: list[str] = []
    atual = ""
    for palavra in palavras:
        candidato = palavra if not atual else f"{atual} {palavra}"
        if len(candidato) <= limite:
            atual = candidato
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas or [""]


def _escapar(texto: str) -> bytes:
    bruto = texto.encode("cp1252", errors="replace")
    return bruto.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def gerar_pdf(linhas: list[str]) -> bytes:
    prontas: list[str] = []
    for linha in linhas:
        prontas.extend(_quebrar(linha))
    prontas = prontas[:42]

    partes = [b"BT", b"/F1 12 Tf", b"48 800 Td", b"16 TL"]
    for indice, linha in enumerate(prontas):
        if indice:
            partes.append(b"T*")
        partes.append(b"(" + _escapar(linha) + b") Tj")
    partes.append(b"ET")
    fluxo = b"\n".join(partes)

    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length "
        + str(len(fluxo)).encode()
        + b" >>\nstream\n"
        + fluxo
        + b"\nendstream",
    ]

    saida = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for numero, objeto in enumerate(objetos, start=1):
        offsets.append(len(saida))
        saida.extend(f"{numero} 0 obj\n".encode())
        saida.extend(objeto)
        saida.extend(b"\nendobj\n")
    xref = len(saida)
    saida.extend(f"xref\n0 {len(objetos) + 1}\n".encode())
    saida.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        saida.extend(f"{offset:010d} 00000 n \n".encode())
    saida.extend(
        f"trailer<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(saida)
