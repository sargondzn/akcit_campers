import os
import tempfile

os.environ["SERIEMA_DADOS"] = tempfile.mkdtemp(prefix="seriema-teste-")
os.environ["HARNESS_STUB"] = "1"

from fastapi.testclient import TestClient

from app.main import app


def test_fluxo_da_demo():
    with TestClient(app) as client:
        entrar = client.post(
            "/api/entrar",
            json={"email": "demo@seriema.local", "senha": "seriema"},
        )
        assert entrar.status_code == 200
        token = entrar.json()["token"]
        assert entrar.json()["consentimento_ok"] is False
        cabecalho = {"Authorization": f"Bearer {token}"}

        bloqueado = client.get("/api/conversa", headers=cabecalho)
        assert bloqueado.status_code == 403

        aceite = client.post(
            "/api/consentimento",
            headers=cabecalho,
            json={"nome_idoso": "Dona Ana"},
        )
        assert aceite.status_code == 200
        assert aceite.json()["nome_idoso"] == "Dona Ana"

        manual = client.put(
            "/api/lista/itens",
            headers=cabecalho,
            json={"itens": [{"nome": "Losartana", "concentracao": "30 mg"}]},
        )
        assert manual.status_code == 200
        assert manual.json()["pode_confirmar"] is True
        assert manual.json()["itens"][0]["nome"] == "Losartana"

        foto = client.post(
            "/api/mensagens",
            headers=cabecalho,
            data={"texto": ""},
            files={"arquivo": ("receita.jpg", b"\xff\xd8\xff foto", "image/jpeg")},
        )
        assert foto.status_code == 200
        corpo = foto.json()
        assert corpo["pode_confirmar"] is True
        lista = next(m for m in corpo["mensagens"] if m["tipo"] == "lista")
        assert len(lista["itens"]) == 4
        assert lista["alertas"]

        editada = client.put(
            "/api/lista/itens",
            headers=cabecalho,
            json={
                "itens": [
                    {"nome": "Losartana potássica", "concentracao": "50 mg"},
                    {"nome": "Dipirona", "concentracao": "500 mg"},
                ]
            },
        )
        assert editada.status_code == 200
        assert len(editada.json()["itens"]) == 2
        assert editada.json()["itens"][1]["nome"] == "Dipirona"

        confirmada = client.post(
            "/api/acoes",
            headers=cabecalho,
            json={"id": "confirmar_lista"},
        )
        assert confirmada.status_code == 200
        assert confirmada.json()["pode_confirmar"] is False
        assert confirmada.json()["lembrete"]["texto"]

        audio = client.post(
            "/api/mensagens",
            headers=cabecalho,
            files={"arquivo": ("relato.webm", b"audio", "audio/webm")},
        )
        assert any(
            acao["id"] == "baixar_resumo"
            for mensagem in audio.json()["mensagens"]
            for acao in mensagem["acoes"]
        )

        alarme = client.post(
            "/api/mensagens",
            headers=cabecalho,
            data={"texto": "queda com batida na cabeça"},
        )
        assert any(m["tipo"] == "alarme" for m in alarme.json()["mensagens"])

        pdf = client.get("/api/resumo.pdf", headers=cabecalho)
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")
        assert "Seriema".encode("cp1252") in pdf.content

        senha = client.post(
            "/api/entrar",
            json={"email": "demo@seriema.local", "senha": "errada"},
        )
        assert senha.status_code == 401
