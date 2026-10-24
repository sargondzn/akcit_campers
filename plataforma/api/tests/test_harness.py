"""A API chamando o harness de verdade (ponte C1 + RepositorioApi), com agentes falsos: sem rede e sem OpenAI."""

import os
import tempfile

os.environ.setdefault("SERIEMA_DADOS", tempfile.mkdtemp(prefix="seriema-teste-"))
os.environ.setdefault("HARNESS_DADOS_STUB", "1")

from fastapi.testclient import TestClient

from app import ponte
from app.main import app
from harness.agentes.esquemas import ItensInterpretados
from harness.testes.agentes_falsos import AgentesFalsos, item


def receita(*itens, prescritor="Dr. Silva"):
    return ItensInterpretados(tipo_documento="receita_impressa", prescritor=prescritor,
                              data_receita="2026-10-20", itens=list(itens))


def entrar(client) -> dict:
    token = client.post("/api/entrar", json={"email": "harness@seriema.local", "senha": "seriema"}).json()["token"]
    cabecalho = {"Authorization": f"Bearer {token}"}
    client.post("/api/consentimento", headers=cabecalho, json={"nome_idoso": "Dona Ana"})
    return cabecalho


def foto(client, cabecalho) -> dict:
    resposta = client.post("/api/mensagens", headers=cabecalho, data={"texto": ""},
                           files={"arquivo": ("receita.jpg", b"\xff\xd8\xff foto", "image/jpeg")})
    assert resposta.status_code == 200
    return resposta.json()


def test_foto_vira_lista_e_confirmacao_passa_pelo_harness(monkeypatch):
    monkeypatch.delenv("HARNESS_STUB", raising=False)
    monkeypatch.setattr(ponte, "AGENTES", AgentesFalsos(interpretacoes=[
        receita(item("Losartana", "50 mg"), item("Metformina", "850 mg", horarios=("08:00",))),
        receita(item("Losartana", "100 mg")),
    ]))
    with TestClient(app) as client:
        cabecalho = entrar(client)

        corpo = foto(client, cabecalho)
        lista = next(m for m in corpo["mensagens"] if m["tipo"] == "lista")
        assert [i["nome"] for i in lista["itens"]] == ["Losartana", "Metformina"]
        assert corpo["pode_confirmar"] is True
        assert client.get("/api/lista", headers=cabecalho).json()["confirmada"] is False

        confirmada = client.post("/api/acoes", headers=cabecalho, json={"id": "confirmar_lista"}).json()
        assert confirmada["pode_confirmar"] is False
        assert confirmada["lembrete"]["texto"]
        atual = client.get("/api/lista", headers=cabecalho).json()
        assert atual["confirmada"] is True
        assert [i["concentracao"] for i in atual["itens"]] == ["50 mg", "850 mg"]

        # segunda receita com lista já confirmada: o harness pergunta o escopo por botões
        corpo = foto(client, cabecalho)
        botoes = [a for m in corpo["mensagens"] for a in m["acoes"] if a["id"].startswith("botao:")]
        assert botoes
        toda = next(b for b in botoes if b["rotulo"] == "Toda a lista")
        corpo = client.post("/api/acoes", headers=cabecalho, json={"id": toda["id"]}).json()
        assert corpo["pode_confirmar"] is True
        assert any(m["tipo"] == "lista" for m in corpo["mensagens"])


def test_texto_de_alarme_passa_pelas_regras_fixas(monkeypatch):
    monkeypatch.delenv("HARNESS_STUB", raising=False)
    monkeypatch.setattr(ponte, "AGENTES", AgentesFalsos())
    with TestClient(app) as client:
        cabecalho = entrar(client)
        corpo = client.post("/api/mensagens", headers=cabecalho, data={"texto": "ela teve uma queda e bateu a cabeça"})
        alarme = next(m for m in corpo.json()["mensagens"] if m["tipo"] == "alarme")
        assert any(a["id"] == "ligar_192" for a in alarme["acoes"])
