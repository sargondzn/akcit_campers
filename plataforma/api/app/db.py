import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def pasta_dados() -> Path:
    pasta = Path(os.environ.get("SERIEMA_DADOS", RAIZ / "dados"))
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "arquivos").mkdir(exist_ok=True)
    return pasta


def caminho_banco() -> Path:
    return pasta_dados() / "seriema.db"


@contextmanager
def banco():
    conn = sqlite3.connect(caminho_banco())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def iniciar_banco() -> None:
    with banco() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                criada_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessoes (
                token TEXT PRIMARY KEY,
                conta_id INTEGER NOT NULL REFERENCES contas(id),
                criada_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS consentimentos (
                conta_id INTEGER PRIMARY KEY REFERENCES contas(id),
                nome_idoso TEXT NOT NULL,
                texto_versao TEXT NOT NULL,
                aceito_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS arquivos (
                id INTEGER PRIMARY KEY,
                conta_id INTEGER NOT NULL REFERENCES contas(id),
                tipo TEXT NOT NULL,
                nome TEXT NOT NULL,
                caminho TEXT NOT NULL,
                criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY,
                conta_id INTEGER NOT NULL REFERENCES contas(id),
                papel TEXT NOT NULL,
                tipo TEXT NOT NULL,
                texto TEXT NOT NULL,
                arquivo_id INTEGER,
                extra_json TEXT NOT NULL DEFAULT '{}',
                criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS listas (
                id INTEGER PRIMARY KEY,
                conta_id INTEGER NOT NULL REFERENCES contas(id),
                versao INTEGER NOT NULL,
                confirmada INTEGER NOT NULL DEFAULT 0,
                criada_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY,
                lista_id INTEGER NOT NULL REFERENCES listas(id),
                nome TEXT NOT NULL,
                concentracao TEXT NOT NULL,
                horario TEXT,
                arquivo_id INTEGER REFERENCES arquivos(id)
            );
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY,
                lista_id INTEGER NOT NULL REFERENCES listas(id),
                texto TEXT NOT NULL,
                fonte TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS lembretes (
                id INTEGER PRIMARY KEY,
                conta_id INTEGER NOT NULL REFERENCES contas(id),
                texto TEXT NOT NULL,
                visto INTEGER NOT NULL DEFAULT 0,
                criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS doses (
                id INTEGER PRIMARY KEY,
                conta_id INTEGER NOT NULL REFERENCES contas(id),
                lembrete_id INTEGER NOT NULL,
                registrado_em TEXT NOT NULL
            );
            """
        )
        _migrar_itens(conn)


def _migrar_itens(conn: sqlite3.Connection) -> None:
    colunas = {linha[1] for linha in conn.execute("PRAGMA table_info(itens)")}
    if "horario" not in colunas:
        conn.execute("ALTER TABLE itens ADD COLUMN horario TEXT")
    if "arquivo_id" not in colunas:
        conn.execute("ALTER TABLE itens ADD COLUMN arquivo_id INTEGER REFERENCES arquivos(id)")


def gerar_hash(senha: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${digest}"


def confere_senha(senha: str, guardado: str) -> bool:
    salt, digest = guardado.split("$", 1)
    novo = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 200_000).hex()
    return secrets.compare_digest(novo, digest)


def semear_demo() -> None:
    with banco() as conn:
        existe = conn.execute(
            "SELECT id FROM contas WHERE email = ?",
            ("demo@seriema.local",),
        ).fetchone()
        if existe is None:
            conn.execute(
                "INSERT INTO contas (email, senha_hash, criada_em) VALUES (?, ?, ?)",
                ("demo@seriema.local", gerar_hash("seriema"), agora()),
            )


def buscar_email(email: str):
    with banco() as conn:
        return conn.execute("SELECT * FROM contas WHERE email = ?", (email,)).fetchone()


def criar_conta(email: str, senha: str) -> int:
    with banco() as conn:
        cur = conn.execute(
            "INSERT INTO contas (email, senha_hash, criada_em) VALUES (?, ?, ?)",
            (email, gerar_hash(senha), agora()),
        )
        return int(cur.lastrowid)


def criar_sessao(conta_id: int) -> str:
    token = secrets.token_urlsafe(32)
    with banco() as conn:
        conn.execute(
            "INSERT INTO sessoes (token, conta_id, criada_em) VALUES (?, ?, ?)",
            (token, conta_id, agora()),
        )
    return token


def conta_do_token(token: str) -> int | None:
    with banco() as conn:
        row = conn.execute(
            """
            SELECT contas.id AS id, contas.email AS email
            FROM sessoes JOIN contas ON contas.id = sessoes.conta_id
            WHERE sessoes.token = ?
            """,
            (token,),
        ).fetchone()
        if row is None:
            return None
        return int(row["id"])


def dados_sessao(conta_id: int) -> dict:
    with banco() as conn:
        conta = conn.execute("SELECT email FROM contas WHERE id = ?", (conta_id,)).fetchone()
        aceite = conn.execute(
            "SELECT nome_idoso FROM consentimentos WHERE conta_id = ?",
            (conta_id,),
        ).fetchone()
        return {
            "email": conta["email"],
            "consentimento_ok": aceite is not None,
            "nome_idoso": aceite["nome_idoso"] if aceite else "",
        }


def registrar_consentimento(conta_id: int, nome_idoso: str) -> None:
    nome = nome_idoso.strip() or "Pessoa cuidada"
    with banco() as conn:
        conn.execute(
            """
            INSERT INTO consentimentos (conta_id, nome_idoso, texto_versao, aceito_em)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(conta_id) DO UPDATE SET
                nome_idoso = excluded.nome_idoso,
                texto_versao = excluded.texto_versao,
                aceito_em = excluded.aceito_em
            """,
            (conta_id, nome[:80], "2026-10-23", agora()),
        )


def consentimento_ok(conta_id: int) -> bool:
    return dados_sessao(conta_id)["consentimento_ok"]


def nome_idoso(conta_id: int) -> str:
    return dados_sessao(conta_id)["nome_idoso"] or "Pessoa cuidada"


def salvar_arquivo(conta_id: int, tipo: str, nome: str, conteudo: bytes) -> int:
    with banco() as conn:
        cur = conn.execute(
            "INSERT INTO arquivos (conta_id, tipo, nome, caminho, criado_em) VALUES (?, ?, ?, ?, ?)",
            (conta_id, tipo, nome, "", agora()),
        )
        arquivo_id = int(cur.lastrowid)
        destino = pasta_dados() / "arquivos" / f"{arquivo_id}.bin"
        destino.write_bytes(conteudo)
        conn.execute("UPDATE arquivos SET caminho = ? WHERE id = ?", (str(destino), arquivo_id))
        return arquivo_id


def ler_arquivo(conta_id: int, arquivo_id: int) -> tuple[bytes, str, str] | None:
    with banco() as conn:
        row = conn.execute(
            "SELECT caminho, tipo, nome FROM arquivos WHERE id = ? AND conta_id = ?",
            (arquivo_id, conta_id),
        ).fetchone()
        if row is None:
            return None
        return Path(row["caminho"]).read_bytes(), row["tipo"], row["nome"]


def adicionar_mensagem(
    conta_id: int,
    papel: str,
    tipo: str,
    texto: str,
    arquivo_id: int | None = None,
    extra: dict | None = None,
) -> int:
    with banco() as conn:
        cur = conn.execute(
            """
            INSERT INTO mensagens (conta_id, papel, tipo, texto, arquivo_id, extra_json, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conta_id,
                papel,
                tipo,
                texto,
                arquivo_id,
                json.dumps(extra or {}, ensure_ascii=False),
                agora(),
            ),
        )
        return int(cur.lastrowid)


def listar_mensagens(conta_id: int) -> list[dict]:
    with banco() as conn:
        rows = conn.execute(
            """
            SELECT id, papel, tipo, texto, arquivo_id, extra_json, criado_em
            FROM mensagens WHERE conta_id = ? ORDER BY id
            """,
            (conta_id,),
        ).fetchall()
    saida = []
    for row in rows:
        extra = json.loads(row["extra_json"] or "{}")
        saida.append(
            {
                "id": row["id"],
                "papel": row["papel"],
                "tipo": row["tipo"],
                "texto": row["texto"],
                "arquivo_id": row["arquivo_id"],
                "criado_em": row["criado_em"],
                "itens": extra.get("itens", []),
                "alertas": extra.get("alertas", []),
                "acoes": extra.get("acoes", []),
            }
        )
    return saida


def criar_lista_demo(conta_id: int) -> dict:
    itens = [
        ("Losartana potássica", "50 mg"),
        ("Hidroclorotiazida", "25 mg"),
        ("Metformina", "850 mg"),
        ("Sinvastatina", "20 mg"),
    ]
    alerta = (
        "Losartana e hidroclorotiazida aparecem juntas. Leve a lista ao farmacêutico ou ao médico. A Seriema não sugere troca, dose nem suspensão.",
        "Material de demonstração. Confira com o farmacêutico ou o médico.",
    )
    with banco() as conn:
        versao_row = conn.execute(
            "SELECT COALESCE(MAX(versao), 0) AS versao FROM listas WHERE conta_id = ?",
            (conta_id,),
        ).fetchone()
        versao = int(versao_row["versao"]) + 1
        cur = conn.execute(
            "INSERT INTO listas (conta_id, versao, confirmada, criada_em) VALUES (?, ?, 0, ?)",
            (conta_id, versao, agora()),
        )
        lista_id = int(cur.lastrowid)
        for nome, concentracao in itens:
            conn.execute(
                "INSERT INTO itens (lista_id, nome, concentracao) VALUES (?, ?, ?)",
                (lista_id, nome, concentracao),
            )
        conn.execute(
            "INSERT INTO alertas (lista_id, texto, fonte) VALUES (?, ?, ?)",
            (lista_id, alerta[0], alerta[1]),
        )
    return lista_atual(conta_id)


def lista_atual(conta_id: int) -> dict | None:
    with banco() as conn:
        lista = conn.execute(
            """
            SELECT id, versao, confirmada FROM listas
            WHERE conta_id = ? ORDER BY versao DESC LIMIT 1
            """,
            (conta_id,),
        ).fetchone()
        if lista is None:
            return None
        itens = conn.execute(
            "SELECT nome, concentracao, horario, arquivo_id FROM itens WHERE lista_id = ? ORDER BY id",
            (lista["id"],),
        ).fetchall()
        alertas = conn.execute(
            "SELECT texto, fonte FROM alertas WHERE lista_id = ? ORDER BY id",
            (lista["id"],),
        ).fetchall()
        return {
            "versao": lista["versao"],
            "confirmada": bool(lista["confirmada"]),
            "itens": [
                {
                    "nome": i["nome"],
                    "concentracao": i["concentracao"],
                    "horario": i["horario"],
                    "arquivo_id": i["arquivo_id"],
                }
                for i in itens
            ],
            "alertas": [{"texto": a["texto"], "fonte": a["fonte"]} for a in alertas],
        }


def _proxima_versao_lista(conn, conta_id: int) -> int:
    versao_row = conn.execute(
        "SELECT COALESCE(MAX(versao), 0) AS versao FROM listas WHERE conta_id = ?",
        (conta_id,),
    ).fetchone()
    return int(versao_row["versao"]) + 1


def _gravar_itens(conn, lista_id: int, itens: list[dict]) -> None:
    conn.execute("DELETE FROM itens WHERE lista_id = ?", (lista_id,))
    for item in itens:
        conn.execute(
            """
            INSERT INTO itens (lista_id, nome, concentracao, horario, arquivo_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                lista_id,
                item["nome"],
                item["concentracao"],
                item.get("horario"),
                item.get("arquivo_id"),
            ),
        )


_ALERTA_LISTA_MANUAL = (
    "Lista montada ou ajustada na mão. Confira nome e concentração com a receita, a caixa ou o farmacêutico.",
    "Entrada manual na plataforma.",
)


def atualizar_itens_lista_pendente(conta_id: int, itens: list[dict[str, str]]) -> dict:
    with banco() as conn:
        lista = conn.execute(
            """
            SELECT id, confirmada FROM listas
            WHERE conta_id = ? ORDER BY versao DESC LIMIT 1
            """,
            (conta_id,),
        ).fetchone()
        if lista is None:
            versao = _proxima_versao_lista(conn, conta_id)
            cur = conn.execute(
                "INSERT INTO listas (conta_id, versao, confirmada, criada_em) VALUES (?, ?, 0, ?)",
                (conta_id, versao, agora()),
            )
            lista_id = int(cur.lastrowid)
            _gravar_itens(conn, lista_id, itens)
            conn.execute(
                "INSERT INTO alertas (lista_id, texto, fonte) VALUES (?, ?, ?)",
                (lista_id, _ALERTA_LISTA_MANUAL[0], _ALERTA_LISTA_MANUAL[1]),
            )
        elif lista["confirmada"]:
            versao = _proxima_versao_lista(conn, conta_id)
            cur = conn.execute(
                "INSERT INTO listas (conta_id, versao, confirmada, criada_em) VALUES (?, ?, 0, ?)",
                (conta_id, versao, agora()),
            )
            lista_id = int(cur.lastrowid)
            _gravar_itens(conn, lista_id, itens)
            conn.execute(
                "INSERT INTO alertas (lista_id, texto, fonte) VALUES (?, ?, ?)",
                (lista_id, _ALERTA_LISTA_MANUAL[0], _ALERTA_LISTA_MANUAL[1]),
            )
        else:
            lista_id = int(lista["id"])
            _gravar_itens(conn, lista_id, itens)
    return lista_atual(conta_id) or {}


def confirmar_lista_atual(conta_id: int) -> bool:
    with banco() as conn:
        lista = conn.execute(
            """
            SELECT id, confirmada FROM listas
            WHERE conta_id = ? ORDER BY versao DESC LIMIT 1
            """,
            (conta_id,),
        ).fetchone()
        if lista is None or lista["confirmada"]:
            return False
        conn.execute("UPDATE listas SET confirmada = 1 WHERE id = ?", (lista["id"],))
        return True


def criar_lembrete(conta_id: int, texto: str) -> dict:
    with banco() as conn:
        conn.execute("UPDATE lembretes SET visto = 1 WHERE conta_id = ? AND visto = 0", (conta_id,))
        cur = conn.execute(
            "INSERT INTO lembretes (conta_id, texto, visto, criado_em) VALUES (?, ?, 0, ?)",
            (conta_id, texto, agora()),
        )
        return {"id": int(cur.lastrowid), "texto": texto, "visto": False}


def lembrete_aberto(conta_id: int) -> dict | None:
    with banco() as conn:
        row = conn.execute(
            """
            SELECT id, texto FROM lembretes
            WHERE conta_id = ? AND visto = 0 ORDER BY id DESC LIMIT 1
            """,
            (conta_id,),
        ).fetchone()
        if row is None:
            return None
        return {"id": row["id"], "texto": row["texto"], "visto": False}


def marcar_lembrete_visto(conta_id: int, lembrete_id: int) -> None:
    with banco() as conn:
        conn.execute(
            "UPDATE lembretes SET visto = 1 WHERE id = ? AND conta_id = ?",
            (lembrete_id, conta_id),
        )


def registrar_dose(conta_id: int, lembrete_id: int) -> str | None:
    with banco() as conn:
        row = conn.execute(
            "SELECT id FROM lembretes WHERE id = ? AND conta_id = ?",
            (lembrete_id, conta_id),
        ).fetchone()
        if row is None:
            return None
        momento = agora()
        conn.execute(
            "INSERT INTO doses (conta_id, lembrete_id, registrado_em) VALUES (?, ?, ?)",
            (conta_id, lembrete_id, momento),
        )
        conn.execute(
            "UPDATE lembretes SET visto = 1 WHERE id = ? AND conta_id = ?",
            (lembrete_id, conta_id),
        )
        return momento


def ultima_dose(conta_id: int) -> str | None:
    with banco() as conn:
        row = conn.execute(
            "SELECT registrado_em FROM doses WHERE conta_id = ? ORDER BY id DESC LIMIT 1",
            (conta_id,),
        ).fetchone()
        return row["registrado_em"] if row else None


def garantir_boas_vindas(conta_id: int) -> None:
    with banco() as conn:
        row = conn.execute(
            "SELECT id FROM mensagens WHERE conta_id = ? LIMIT 1",
            (conta_id,),
        ).fetchone()
        if row is not None:
            return
    adicionar_mensagem(
        conta_id,
        "agente",
        "texto",
        "Mande a foto da receita, da caixa ou o PDF. Eu monto a lista e você confirma. Não sugiro dose, troca nem suspensão.",
    )
