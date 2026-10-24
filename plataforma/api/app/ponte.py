"""Chamada ao harness (C1) no lugar do stub (specs/backend/spec.md §6).

Monta a `MensagemEntrada`, chama `harness.processar_mensagem` com o `RepositorioApi` e grava
cada `MensagemSaida` como mensagem da Seriema, no formato que a interface já lê
(`tipo`, `texto`, `itens`, `alertas`, `acoes`). Uma chamada por vez, para manter a ordem da conversa.
"""

from __future__ import annotations

import logging
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[3]
if str(RAIZ_REPO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPO))

from app import db, stub  # noqa: E402
from app.repositorio import RepositorioApi  # noqa: E402
from harness import processar_mensagem  # noqa: E402
from harness.contratos import Acao, Anexo, MensagemEntrada, MensagemSaida  # noqa: E402
from harness.guardrails import frases  # noqa: E402

log = logging.getLogger("seriema.ponte")

TRAVA = threading.Lock()
AGENTES = None  # os testes trocam por agentes falsos; None = agentes de verdade (OpenAI)

MIME = {"foto": "image/jpeg", "pdf": "application/pdf", "audio": "audio/webm"}
TIPO_NA_INTERFACE = {
    "lista_para_confirmar": "lista",
    "ligue_192": "alarme",
    "resumo": "resumo",
}
SEM_LISTA = "Ainda não há lista nova para confirmar. Mande a foto da receita, da caixa ou o PDF."


def tratar(conta_id: int, texto: str, arquivo: dict | None) -> dict:
    db.garantir_boas_vindas(conta_id)
    texto = texto.strip()
    tipo = arquivo["tipo"] if arquivo else "texto"
    legenda = texto or {"foto": "Enviei uma foto.", "pdf": "Enviei um PDF.", "audio": "Enviei um áudio."}.get(tipo, "")
    db.adicionar_mensagem(conta_id, "cuidadora", tipo, legenda, arquivo["id"] if arquivo else None)

    anexo = None
    if arquivo:
        caminho = db.caminho_arquivo(conta_id, arquivo["id"])
        anexo = Anexo(caminho=caminho, mime=MIME[tipo], tamanho_bytes=Path(caminho).stat().st_size)
    entrada = _entrada(conta_id, tipo, texto=texto or None, anexo=anexo)
    if texto.lower() in {"confirmo", "confirmo a lista"} and (acao := _acao_confirmar(conta_id)):
        entrada = _entrada(conta_id, "acao", acao=acao)
    return _rodar(conta_id, entrada)


def confirmar(conta_id: int) -> dict:
    db.garantir_boas_vindas(conta_id)
    db.adicionar_mensagem(conta_id, "cuidadora", "texto", "Confirmo a lista.")
    acao = _acao_confirmar(conta_id)
    if acao is None:
        db.adicionar_mensagem(conta_id, "agente", "texto", SEM_LISTA)
        return stub.estado(conta_id)
    return _rodar(conta_id, _entrada(conta_id, "acao", acao=acao))


def acionar_botao(conta_id: int, mensagem_id: int, indice: int) -> dict | None:
    """Botões do harness com ação (escopo da receita, decisão sobre item ausente, estoque)."""
    extra = db.mensagem_extra(conta_id, mensagem_id)
    botoes = (extra or {}).get("botoes", [])
    if not 0 <= indice < len(botoes):
        return None
    botao = botoes[indice]
    db.adicionar_mensagem(conta_id, "cuidadora", "texto", botao["rotulo"])
    return _rodar(conta_id, _entrada(conta_id, "acao", acao=Acao.model_validate(botao["acao"])))


def _entrada(conta_id: int, tipo: str, **campos) -> MensagemEntrada:
    return MensagemEntrada(
        mensagem_id=uuid.uuid4().hex, conta_id=str(conta_id), idoso_id=str(conta_id),
        tipo=tipo, recebida_em=datetime.now(), **campos,
    )


def _acao_confirmar(conta_id: int) -> Acao | None:
    repo = RepositorioApi(conta_id)
    abertas = [p for p in repo.obter_pendencias(str(conta_id)) if p.tipo == "lista_para_confirmar"]
    if not abertas:
        return None
    return Acao(tipo="confirmar_pendencia", pendencia_id=abertas[-1].pendencia_id)


def _rodar(conta_id: int, entrada: MensagemEntrada) -> dict:
    repo = RepositorioApi(conta_id)
    with TRAVA:
        try:
            resposta = processar_mensagem(entrada, repo, AGENTES)
            mensagens = resposta.mensagens
        except Exception:  # erro fora dos serviços já tratados pelo harness: resposta fixa (00-projeto/spec §6)
            log.exception("harness falhou")
            mensagens = [MensagemSaida(tipo="texto", texto=frases.INDISPONIVEL)]
    _gravar(conta_id, mensagens)
    if repo.lista_salva:
        db.criar_lembrete(conta_id, stub.TEXTO_LEMBRETE)
    return stub.estado(conta_id)


def _gravar(conta_id: int, mensagens: list[MensagemSaida]) -> None:
    alertas_na_lista = any(m.tipo == "lista_para_confirmar" and m.alertas for m in mensagens)
    for m in mensagens:
        if m.tipo == "alertas" and alertas_na_lista:
            continue  # os mesmos alertas já vão no cartão da lista
        alertas = [_alerta(a) for a in m.alertas or []]
        itens = [_item(i) for i in m.itens or []]
        if m.tipo == "lista_para_confirmar":
            db.propor_lista(
                conta_id,
                [{"nome": i.nome_lido, "concentracao": i.concentracao or "", "dados": i.model_dump(mode="json")}
                 for i in m.itens or []],
                [{"texto": a["descricao"] or a.get("texto", ""), "fonte": a.get("fonte", "")} for a in alertas],
            )
        acoes, botoes = _acoes(m)
        extra = {"itens": itens, "alertas": alertas, "acoes": acoes, "botoes": botoes}
        mensagem_id = db.adicionar_mensagem(
            conta_id, "agente", TIPO_NA_INTERFACE.get(m.tipo, "texto"), m.texto, _audio(conta_id, m), extra=extra,
        )
        if botoes:
            extra["acoes"] = acoes + [
                {"id": f"botao:{mensagem_id}:{n}", "rotulo": b["rotulo"]} for n, b in enumerate(botoes)
            ]
            db.definir_extra(conta_id, mensagem_id, extra)


def _item(item) -> dict:
    nome = item.nome_lido
    if item.status in ("nao_confirmado", "ilegivel"):
        nome = f"{nome} (confira)"
    return {"nome": nome, "concentracao": item.concentracao or ""}


def _alerta(alerta) -> dict:
    dados = alerta.model_dump(mode="json")
    dados.setdefault("descricao", "")
    return dados


def _acoes(m: MensagemSaida) -> tuple[list[dict], list[dict]]:
    """`acoes` para a interface; `botoes` guarda as ações do harness para `/api/acoes` (`botao:<mensagem>:<n>`)."""
    if m.tipo == "ligue_192":
        return [{"id": "ligar_192", "rotulo": "Ligar 192"}], []
    if m.tipo == "resumo":
        return [{"id": "baixar_resumo", "rotulo": "Baixar resumo em PDF"}], []
    botoes = [
        {"rotulo": b.rotulo, "acao": b.acao.model_dump(mode="json")}
        for b in m.botoes
        if b.acao and b.acao.tipo != "confirmar_pendencia"  # a interface já tem o botão Confirmar lista
    ]
    return [], botoes


def _audio(conta_id: int, m: MensagemSaida) -> int | None:
    if m.audio is None:
        return None
    try:
        caminho = Path(m.audio.caminho)
        return db.salvar_arquivo(conta_id, "audio", caminho.name, caminho.read_bytes())
    except OSError:
        return None
