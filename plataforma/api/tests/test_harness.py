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


def entrar(client, email="harness@seriema.local") -> dict:
    token = client.post("/api/entrar", json={"email": email, "senha": "seriema"}).json()["token"]
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


def test_edicao_na_tela_vale_na_confirmacao(monkeypatch):
    monkeypatch.delenv("HARNESS_STUB", raising=False)
    monkeypatch.setattr(ponte, "AGENTES", AgentesFalsos(interpretacoes=[
        receita(item("Losartana", "50 mg"), item("Metfromina", "850 mg", horarios=("07:00",), confianca=0.4)),
    ]))
    with TestClient(app) as client:
        cabecalho = entrar(client, "edicao@seriema.local")
        foto(client, cabecalho)
        foto_caixa = client.post("/api/arquivos", headers=cabecalho,
                                 files={"arquivo": ("caixa.jpg", b"\xff\xd8\xff caixa", "image/jpeg")}).json()["id"]

        editada = client.put("/api/lista/itens", headers=cabecalho, json={"itens": [
            {"nome": "Losartana", "concentracao": "100 mg", "horario": None, "arquivo_id": foto_caixa},
            {"nome": "Metformina", "concentracao": "850 mg", "horario": "07:30"},   # nome corrigido na tela
            {"nome": "Sinvastatina", "concentracao": "20 mg", "horario": None},     # item novo
        ]})
        assert editada.status_code == 200
        assert editada.json()["pode_confirmar"] is True

        confirmada = client.post("/api/acoes", headers=cabecalho, json={"id": "confirmar_lista"}).json()
        assert confirmada["pode_confirmar"] is False
        atual = client.get("/api/lista", headers=cabecalho).json()
        assert atual["confirmada"] is True
        assert [(i["nome"], i["concentracao"], i["horario"]) for i in atual["itens"]] == [
            ("Losartana", "100 mg", "08:00, 20:00"),   # horários lidos da receita ficam
            ("Metformina", "850 mg", "07:30"),
            ("Sinvastatina", "20 mg", None),
        ]
        assert atual["itens"][0]["arquivo_id"] == foto_caixa
        confirmados = ponte.RepositorioApi(int(atual_conta(client, cabecalho))).obter_lista_atual("")
        metformina = next(i for i in confirmados.itens if i.nome_lido == "Metformina")
        assert metformina.status == "confirmado" and metformina.origem == "receita_foto"   # é o item lido, corrigido


def atual_conta(client, cabecalho) -> int:
    from app import db

    return db.conta_do_token(cabecalho["Authorization"].split(" ", 1)[1])


def test_texto_de_alarme_passa_pelas_regras_fixas(monkeypatch):
    monkeypatch.delenv("HARNESS_STUB", raising=False)
    monkeypatch.setattr(ponte, "AGENTES", AgentesFalsos())
    with TestClient(app) as client:
        cabecalho = entrar(client)
        corpo = client.post("/api/mensagens", headers=cabecalho, data={"texto": "ela teve uma queda e bateu a cabeça"})
        alarme = next(m for m in corpo.json()["mensagens"] if m["tipo"] == "alarme")
        assert any(a["id"] == "ligar_192" for a in alarme["acoes"])
