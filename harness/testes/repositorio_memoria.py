"""RepositorioEmMemoria: segue o protocolo C6 sem banco (00-projeto/spec §5, C6).

Usado pelos testes, pela avaliação (C7) e pela demo no terminal. Os PDFs dos resumos
não são gerados aqui (isso é de A): `salvar_resumo` guarda o JSON e devolve URLs falsas.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from harness.contratos import (
    Conduta, Consulta, Dose, Horario, ItemLido, ListaVersao, MensagemDaConversa, Pendencia,
    RegistroDiario, RegistroEstoque, Resumo, SintomaEstruturado,
)


def _id() -> str:
    return uuid.uuid4().hex[:10]


class RepositorioEmMemoria:
    def __init__(self, apelido: str = "Dona Maria", pasta_resumos: Path | None = None):
        self.apelido = apelido
        self.versoes: list[ListaVersao] = []
        self.horarios: list[Horario] = []
        self.doses: list[Dose] = []
        self.diario: list[RegistroDiario] = []
        self.mensagens: list[MensagemDaConversa] = []
        self.pendencias: dict[str, Pendencia] = {}
        self.consultas: dict[str, Consulta] = {}
        self.estoque: list[RegistroEstoque] = []
        self.resumos: dict[str, Resumo] = {}
        self.passos: list[dict] = []
        self.pasta_resumos = pasta_resumos

    # ----- leitura -----
    def obter_idoso(self, idoso_id: str) -> dict:
        return {"idoso_id": idoso_id, "apelido": self.apelido}

    def obter_lista_atual(self, idoso_id: str) -> ListaVersao | None:
        return self.versoes[-1] if self.versoes else None

    def obter_cronograma(self, idoso_id: str) -> list[Horario]:
        return [h for h in self.horarios if h.ativo]

    def obter_doses(self, idoso_id: str, desde: datetime) -> list[Dose]:
        return [d for d in self.doses if d.previsto >= desde]

    def obter_diario(self, idoso_id: str, desde: datetime) -> list[RegistroDiario]:
        return [r for r in self.diario if r.registrado_em >= desde]

    def obter_historico(self, conta_id: str, limite: int = 20) -> list[MensagemDaConversa]:
        return self.mensagens[-limite:]

    def obter_pendencias(self, conta_id: str) -> list[Pendencia]:
        return [p for p in self.pendencias.values() if p.status == "aberta"]

    def obter_versoes_lista(self, idoso_id: str, desde: datetime) -> list[ListaVersao]:
        return [v for v in self.versoes if v.confirmada_em and v.confirmada_em >= desde]

    def obter_consultas(self, idoso_id: str, desde: datetime) -> list[Consulta]:
        return sorted((c for c in self.consultas.values() if c.data_hora >= desde), key=lambda c: c.data_hora)

    def obter_estoque(self, idoso_id: str) -> list[RegistroEstoque]:
        ultimo: dict[str, RegistroEstoque] = {}
        for r in self.estoque:
            ultimo[r.item_id] = r
        return list(ultimo.values())

    # ----- escrita -----
    def criar_pendencia(self, conta_id: str, tipo: str, dados: dict) -> str:
        pid = _id()
        self.pendencias[pid] = Pendencia(pendencia_id=pid, tipo=tipo, dados=dados, criada_em=datetime.now())
        return pid

    def atualizar_pendencia(self, pendencia_id: str, dados: dict) -> None:
        self.pendencias[pendencia_id].dados = dados

    def resolver_pendencia(self, pendencia_id: str, resultado: str) -> None:
        p = self.pendencias.get(pendencia_id)
        if p:
            p.status = resultado if resultado in ("confirmada", "recusada") else "resolvida"

    def salvar_lista_confirmada(self, idoso_id: str, itens: list[ItemLido],
                                pontos_para_conferir: list[str] | None = None) -> int:
        versao = len(self.versoes) + 1
        agora = datetime.now()
        self.versoes.append(ListaVersao(versao=versao, confirmada_em=agora, itens=[i.model_copy() for i in itens],
                                        pontos_para_conferir=pontos_para_conferir or []))
        self.horarios = [
            Horario(horario_id=_id(), item_id=i.item_id, horario=h)
            for i in itens if i.status == "confirmado" for h in i.horarios
        ]
        return versao

    def alterar_cronograma(self, idoso_id: str, mudancas: list[dict]) -> None:
        for m in mudancas:
            if m["acao"] == "remover":
                for h in self.horarios:
                    if h.item_id == m["item_id"] and h.horario == m["horario"]:
                        h.ativo = False
            elif m["acao"] == "incluir":
                self.horarios.append(Horario(horario_id=_id(), item_id=m["item_id"], horario=m["horario"]))
            elif m["acao"] == "mudar":
                for h in self.horarios:
                    if h.item_id == m["item_id"] and h.horario == m["horario"]:
                        h.horario = m["novo_horario"]

    def registrar_dose(self, horario_id: str, status: str, quando: datetime) -> None:
        self.doses.append(Dose(horario_id=horario_id, previsto=quando, status=status))

    def registrar_sintoma(self, idoso_id: str, sintoma: SintomaEstruturado, conduta: Conduta) -> str:
        self.diario.append(RegistroDiario(sintoma=sintoma, conduta=conduta, registrado_em=datetime.now()))
        return _id()

    def salvar_resumo(self, resumo: Resumo) -> dict:
        self.resumos[resumo.resumo_id] = resumo
        if self.pasta_resumos:
            self.pasta_resumos.mkdir(parents=True, exist_ok=True)
            (self.pasta_resumos / f"{resumo.resumo_id}.json").write_text(
                json.dumps(resumo.model_dump(mode="json"), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"resumo_id": resumo.resumo_id, "url_pdf": f"memoria://resumos/{resumo.resumo_id}.pdf",
                "url_publica": f"memoria://r/{resumo.resumo_id}"}

    def salvar_consulta(self, idoso_id: str, data_hora: datetime, profissional: str, local: str | None) -> str:
        cid = _id()
        self.consultas[cid] = Consulta(consulta_id=cid, data_hora=data_hora, profissional=profissional, local=local)
        return cid

    def registrar_relato_consulta(self, consulta_id: str, relato: dict) -> None:
        self.consultas[consulta_id].relato = relato

    def registrar_estoque(self, item_id: str, quantidade: float, quando: datetime, origem: str) -> None:
        self.estoque.append(RegistroEstoque(item_id=item_id, quantidade=quantidade, registrado_em=quando, origem=origem))

    def registrar_passo(self, passo: dict) -> None:
        self.passos.append(passo)

    # ----- só da memória (a API de A grava as mensagens por conta própria) -----
    def registrar_mensagem(self, autor: str, texto: str) -> None:
        self.mensagens.append(MensagemDaConversa(autor=autor, texto=texto, criada_em=datetime.now()))
