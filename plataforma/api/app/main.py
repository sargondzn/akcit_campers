from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, Header, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from app import db, stub
from app.pdf import gerar_pdf

MAX_ARQUIVO = 8 * 1024 * 1024


class ErroApi(Exception):
    def __init__(self, status: int, erro: str):
        self.status = status
        self.erro = erro


class EntrarIn(BaseModel):
    email: str
    senha: str


class ConsentimentoIn(BaseModel):
    nome_idoso: str = ""


class AcaoIn(BaseModel):
    id: str


class DoseIn(BaseModel):
    lembrete_id: int = Field(gt=0)


class ItemListaIn(BaseModel):
    nome: str
    concentracao: str
    horario: str | None = None
    arquivo_id: int | None = None


class ItensListaIn(BaseModel):
    itens: list[ItemListaIn]


@asynccontextmanager
async def vida(_: FastAPI):
    db.iniciar_banco()
    db.semear_demo()
    yield


app = FastAPI(title="Seriema API", lifespan=vida)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErroApi)
def tratar_erro(_: object, exc: ErroApi) -> JSONResponse:
    return JSONResponse({"erro": exc.erro}, status_code=exc.status)


def conta_atual(authorization: str | None = None) -> int:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise ErroApi(401, "Entre de novo para continuar.")
    token = authorization.split(" ", 1)[1].strip()
    conta_id = db.conta_do_token(token)
    if conta_id is None:
        raise ErroApi(401, "Entre de novo para continuar.")
    return conta_id


def exigir_conta(authorization: str | None = Header(default=None)) -> int:
    return conta_atual(authorization)


def exigir_uso(conta_id: int = Depends(exigir_conta)) -> int:
    if not db.consentimento_ok(conta_id):
        raise ErroApi(403, "Antes, aceite o uso dos dados de saúde.")
    return conta_id


def tipo_de_midia(tipo: str, nome: str) -> str:
    nome = (nome or "").lower()
    if tipo == "foto":
        if nome.endswith(".png"):
            return "image/png"
        if nome.endswith(".webp"):
            return "image/webp"
        return "image/jpeg"
    if tipo == "pdf":
        return "application/pdf"
    if nome.endswith((".mp4", ".m4a", ".aac")):
        return "audio/mp4"
    if nome.endswith(".mp3"):
        return "audio/mpeg"
    if nome.endswith(".wav"):
        return "audio/wav"
    if nome.endswith(".ogg"):
        return "audio/ogg"
    return "audio/webm"


def classificar(content_type: str, nome: str) -> str:
    tipo = (content_type or "").split(";", 1)[0].lower()
    nome = (nome or "").lower()
    if tipo.startswith("image/") or nome.endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")):
        return "foto"
    if tipo == "application/pdf" or nome.endswith(".pdf"):
        return "pdf"
    if tipo.startswith("audio/") or tipo in {"video/mp4", "video/webm"} or nome.endswith(
        (".webm", ".mp4", ".m4a", ".aac", ".mp3", ".wav", ".ogg")
    ):
        return "audio"
    raise ErroApi(400, "Envie uma foto, um PDF ou um áudio.")


@app.get("/api/saude")
def saude() -> dict:
    return {"ok": True}


@app.post("/api/entrar")
def entrar(corpo: EntrarIn) -> dict:
    email = corpo.email.strip().lower()
    if "@" not in email or len(email) > 200 or len(corpo.senha) < 4:
        raise ErroApi(400, "Use um e-mail e uma senha de pelo menos 4 caracteres.")
    conta = db.buscar_email(email)
    if conta is None:
        conta_id = db.criar_conta(email, corpo.senha)
    elif not db.confere_senha(corpo.senha, conta["senha_hash"]):
        raise ErroApi(401, "Senha não confere.")
    else:
        conta_id = int(conta["id"])
    return {"token": db.criar_sessao(conta_id), **db.dados_sessao(conta_id)}


@app.get("/api/sessao")
def sessao(conta_id: int = Depends(exigir_conta)) -> dict:
    return db.dados_sessao(conta_id)


@app.post("/api/consentimento")
def consentimento(corpo: ConsentimentoIn, conta_id: int = Depends(exigir_conta)) -> dict:
    db.registrar_consentimento(conta_id, corpo.nome_idoso)
    return db.dados_sessao(conta_id)


@app.get("/api/conversa")
def conversa(conta_id: int = Depends(exigir_uso)) -> dict:
    db.garantir_boas_vindas(conta_id)
    return stub.estado(conta_id)


@app.post("/api/mensagens")
async def mensagens(
    conta_id: int = Depends(exigir_uso),
    texto: str = Form(""),
    arquivo: UploadFile | None = File(None),
) -> dict:
    guardado = None
    if arquivo is not None and arquivo.filename:
        conteudo = await arquivo.read()
        if not conteudo:
            raise ErroApi(400, "O arquivo chegou vazio.")
        if len(conteudo) > MAX_ARQUIVO:
            raise ErroApi(413, "O arquivo passa de 8 MB. Tire outra foto, mais de perto.")
        tipo = classificar(arquivo.content_type or "", arquivo.filename)
        arquivo_id = db.salvar_arquivo(conta_id, tipo, arquivo.filename, conteudo)
        guardado = {"id": arquivo_id, "tipo": tipo}
    if not texto.strip() and guardado is None:
        raise ErroApi(400, "Escreva uma mensagem ou envie uma foto, um PDF ou um áudio.")
    return stub.tratar(conta_id, texto, guardado)


@app.post("/api/acoes")
def acoes(corpo: AcaoIn, conta_id: int = Depends(exigir_uso)) -> dict:
    if corpo.id != "confirmar_lista":
        raise ErroApi(400, "Ação desconhecida.")
    return stub.confirmar(conta_id)


def resposta_lista(conta_id: int, atual: dict | None) -> dict:
    if atual is None:
        return {
            "versao": None,
            "confirmada": False,
            "itens": [],
            "alertas": [],
            "pode_confirmar": False,
            "ultima_dose": db.ultima_dose(conta_id),
            "lembrete": db.lembrete_aberto(conta_id),
        }
    return {
        **atual,
        "pode_confirmar": not atual["confirmada"],
        "ultima_dose": db.ultima_dose(conta_id),
        "lembrete": db.lembrete_aberto(conta_id),
    }


@app.get("/api/lista")
def lista(conta_id: int = Depends(exigir_uso)) -> dict:
    return resposta_lista(conta_id, db.lista_atual(conta_id))


def _normalizar_horario(valor: str | None) -> str | None:
    if not valor or not valor.strip():
        return None
    limpo = valor.strip()
    if len(limpo) > 20:
        raise ErroApi(400, "Horário longo demais.")
    return limpo


@app.put("/api/lista/itens")
def atualizar_itens(corpo: ItensListaIn, conta_id: int = Depends(exigir_uso)) -> dict:
    itens: list[dict] = []
    for item in corpo.itens:
        nome = item.nome.strip()
        concentracao = item.concentracao.strip()
        if not nome or not concentracao:
            raise ErroApi(400, "Cada remédio precisa de nome e concentração.")
        if len(nome) > 200 or len(concentracao) > 80:
            raise ErroApi(400, "Nome ou concentração longos demais.")
        arquivo_id = item.arquivo_id
        if arquivo_id is not None and db.ler_arquivo(conta_id, arquivo_id) is None:
            raise ErroApi(400, "Não encontrei a foto desse remédio.")
        itens.append(
            {
                "nome": nome,
                "concentracao": concentracao,
                "horario": _normalizar_horario(item.horario),
                "arquivo_id": arquivo_id,
            }
        )
    atualizado = db.atualizar_itens_lista_pendente(conta_id, itens)
    return resposta_lista(conta_id, atualizado)


@app.post("/api/arquivos")
async def enviar_arquivo(
    conta_id: int = Depends(exigir_uso),
    arquivo: UploadFile = File(...),
) -> dict:
    if not arquivo.filename:
        raise ErroApi(400, "Escolha uma foto.")
    conteudo = await arquivo.read()
    if not conteudo:
        raise ErroApi(400, "A foto chegou vazia.")
    if len(conteudo) > MAX_ARQUIVO:
        raise ErroApi(413, "A foto passa de 8 MB. Tire outra, mais de perto.")
    tipo = classificar(arquivo.content_type or "", arquivo.filename)
    if tipo != "foto":
        raise ErroApi(400, "Envie uma foto (JPEG, PNG ou WebP).")
    arquivo_id = db.salvar_arquivo(conta_id, tipo, arquivo.filename, conteudo)
    return {"id": arquivo_id}


@app.post("/api/lembretes/{lembrete_id}/visto")
def ver_lembrete(lembrete_id: int, conta_id: int = Depends(exigir_uso)) -> dict:
    db.marcar_lembrete_visto(conta_id, lembrete_id)
    return stub.estado(conta_id)


@app.post("/api/doses")
def doses(corpo: DoseIn, conta_id: int = Depends(exigir_uso)) -> dict:
    if db.registrar_dose(conta_id, corpo.lembrete_id) is None:
        raise ErroApi(404, "Não encontrei esse lembrete.")
    return stub.estado(conta_id)


@app.get("/api/resumo.pdf")
def resumo(conta_id: int = Depends(exigir_uso)) -> Response:
    linhas = ["Seriema", "Resumo para a consulta", f"Pessoa cuidada: {db.nome_idoso(conta_id)}", ""]
    atual = db.lista_atual(conta_id)
    if atual is None:
        linhas.append("Ainda não há lista de remédios.")
    else:
        estado = "confirmada" if atual["confirmada"] else "ainda sem confirmação"
        linhas.append(f"Lista versão {atual['versao']}, {estado}.")
        for item in atual["itens"]:
            linhas.append(f"- {item['nome']} {item['concentracao']}")
        linhas.append("")
        for alerta in atual["alertas"]:
            linhas.append(alerta["texto"])
            linhas.append(f"Fonte: {alerta['fonte']}")
    linhas.append("")
    linhas.append("Este resumo organiza. Quem decide é o profissional.")
    linhas.append("A Seriema não indica dose, troca ou suspensão.")
    return Response(content=gerar_pdf(linhas), media_type="application/pdf")


@app.get("/api/arquivos/{arquivo_id}")
def arquivos(arquivo_id: int, conta_id: int = Depends(exigir_uso)) -> Response:
    achado = db.ler_arquivo(conta_id, arquivo_id)
    if achado is None:
        raise ErroApi(404, "Não encontrei esse arquivo.")
    conteudo, tipo, nome = achado
    return Response(content=conteudo, media_type=tipo_de_midia(tipo, nome))
