"""Repositorio (C6) sobre o banco da API, para o harness (specs/backend/spec.md §7).

Uma instância por conta: cada conta cuida de um idoso, e `idoso_id` é o id da conta em texto.
A lista de remédios fica em `listas`/`itens`, as mesmas tabelas que a interface lê.
O resto (pendências, horários, doses, diário, consultas, estoque, resumos e passos) fica em
`harness_registros`, um JSON por registro.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from app import db
from harness.contratos import (
    Conduta, Consulta, Dose, Horario, ItemLido, ListaVersao, MensagemDaConversa, Pendencia,
    RegistroDiario, RegistroEstoque, Resumo, SintomaEstruturado,
)


def _id() -> str:
    return uuid.uuid4().hex[:10]


def linha_item(item: ItemLido) -> dict:
    """ItemLido → linha de `itens` (o que a interface mostra, mais o ItemLido inteiro em `dados`)."""
    return {
        "nome": item.nome_lido,
        "concentracao": item.concentracao or "",
        "horario": ", ".join(item.horarios) or None,
        "dados": item.model_dump(mode="json"),
    }


def _desde(registros: list, campo: str, desde: datetime) -> list:
    return [r for r in registros if getattr(r, campo) >= desde]


class RepositorioApi:
    def __init__(self, conta_id: int):
        self.conta_id = conta_id
        self.lista_salva = False

    def _todos(self, colecao: str) -> list[dict]:
        return db.listar_registros(self.conta_id, colecao)

    def _salvar(self, colecao: str, registro_id: str, dados: dict) -> None:
        db.salvar_registro(self.conta_id, colecao, registro_id, dados)

    # ----- leitura -----
    def obter_idoso(self, idoso_id: str) -> dict:
        return {"idoso_id": idoso_id, "apelido": db.nome_idoso(self.conta_id)}

    def _versoes(self) -> list[ListaVersao]:
        return [
            ListaVersao(
                versao=v["versao"],
                confirmada_em=datetime.fromisoformat(v["confirmada_em"]) if v["confirmada_em"] else None,
                itens=[ItemLido.model_validate(i) for i in v["itens"] if i],
                pontos_para_conferir=v["pontos"],
            )
            for v in db.listas_confirmadas(self.conta_id)
        ]

    def obter_lista_atual(self, idoso_id: str) -> ListaVersao | None:
        versoes = self._versoes()
        return versoes[-1] if versoes else None

    def obter_cronograma(self, idoso_id: str) -> list[Horario]:
        horarios = [Horario.model_validate(h) for h in self._todos("horario")]
        return [h for h in horarios if h.ativo]

    def obter_doses(self, idoso_id: str, desde: datetime) -> list[Dose]:
        return _desde([Dose.model_validate(d) for d in self._todos("dose")], "previsto", desde)

    def obter_diario(self, idoso_id: str, desde: datetime) -> list[RegistroDiario]:
        return _desde([RegistroDiario.model_validate(r) for r in self._todos("diario")], "registrado_em", desde)

    def obter_historico(self, conta_id: str, limite: int = 20) -> list[MensagemDaConversa]:
        mensagens = db.listar_mensagens(self.conta_id)[-limite:]
        return [
            MensagemDaConversa(
                autor="cuidadora" if m["papel"] == "cuidadora" else "seri",
                texto=m["texto"],
                criada_em=datetime.fromisoformat(m["criado_em"]).astimezone().replace(tzinfo=None),
            )
            for m in mensagens
        ]

    def obter_pendencias(self, conta_id: str) -> list[Pendencia]:
        pendencias = [Pendencia.model_validate(p) for p in self._todos("pendencia")]
        return [p for p in pendencias if p.status == "aberta"]

    def obter_versoes_lista(self, idoso_id: str, desde: datetime) -> list[ListaVersao]:
        return [v for v in self._versoes() if v.confirmada_em and v.confirmada_em >= desde]

    def obter_consultas(self, idoso_id: str, desde: datetime) -> list[Consulta]:
        consultas = _desde([Consulta.model_validate(c) for c in self._todos("consulta")], "data_hora", desde)
        return sorted(consultas, key=lambda c: c.data_hora)

    def obter_estoque(self, idoso_id: str) -> list[RegistroEstoque]:
        ultimo: dict[str, RegistroEstoque] = {}
        for r in self._todos("estoque"):
            registro = RegistroEstoque.model_validate(r)
            ultimo[registro.item_id] = registro
        return list(ultimo.values())

    # ----- escrita -----
    def criar_pendencia(self, conta_id: str, tipo: str, dados: dict) -> str:
        pid = _id()
        pendencia = Pendencia(pendencia_id=pid, tipo=tipo, dados=dados, criada_em=datetime.now())
        self._salvar("pendencia", pid, pendencia.model_dump(mode="json"))
        return pid

    def _pendencia(self, pendencia_id: str) -> Pendencia | None:
        dados = db.ler_registro(self.conta_id, pendencia_id)
        return Pendencia.model_validate(dados) if dados else None

    def atualizar_pendencia(self, pendencia_id: str, dados: dict) -> None:
        if (p := self._pendencia(pendencia_id)):
            p.dados = dados
            self._salvar("pendencia", pendencia_id, p.model_dump(mode="json"))

    def resolver_pendencia(self, pendencia_id: str, resultado: str) -> None:
        if (p := self._pendencia(pendencia_id)):
            p.status = resultado if resultado in ("confirmada", "recusada") else "resolvida"
            self._salvar("pendencia", pendencia_id, p.model_dump(mode="json"))

    def salvar_lista_confirmada(self, idoso_id: str, itens: list[ItemLido],
                                pontos_para_conferir: list[str] | None = None) -> int:
        versao = db.confirmar_lista(
            self.conta_id,
            [linha_item(i) for i in itens],
            pontos_para_conferir or [],
            datetime.now().isoformat(),
        )
        for h in self._todos("horario"):
            if h["ativo"]:
                self._salvar("horario", h["horario_id"], {**h, "ativo": False})
        for i in itens:
            if i.status == "confirmado":
                for horario in i.horarios:
                    novo = Horario(horario_id=_id(), item_id=i.item_id, horario=horario)
                    self._salvar("horario", novo.horario_id, novo.model_dump(mode="json"))
        self.lista_salva = True
        return versao

    def alterar_cronograma(self, idoso_id: str, mudancas: list[dict]) -> None:
        horarios = [Horario.model_validate(h) for h in self._todos("horario")]
        for m in mudancas:
            if m["acao"] == "incluir":
                horarios.append(Horario(horario_id=_id(), item_id=m["item_id"], horario=m["horario"]))
                continue
            for h in horarios:
                if h.ativo and h.item_id == m["item_id"] and h.horario == m["horario"]:
                    if m["acao"] == "remover":
                        h.ativo = False
                    elif m["acao"] == "mudar":
                        h.horario = m["novo_horario"]
        for h in horarios:
            self._salvar("horario", h.horario_id, h.model_dump(mode="json"))

    def registrar_dose(self, horario_id: str, status: str, quando: datetime) -> None:
        dose = Dose(horario_id=horario_id, previsto=quando, status=status)
        self._salvar("dose", _id(), dose.model_dump(mode="json"))

    def registrar_sintoma(self, idoso_id: str, sintoma: SintomaEstruturado, conduta: Conduta) -> str:
        rid = _id()
        registro = RegistroDiario(sintoma=sintoma, conduta=conduta, registrado_em=datetime.now())
        self._salvar("diario", rid, registro.model_dump(mode="json"))
        return rid

    def salvar_resumo(self, resumo: Resumo) -> dict:
        self._salvar("resumo", resumo.resumo_id, resumo.model_dump(mode="json"))
        return {"resumo_id": resumo.resumo_id, "url_pdf": "/api/resumo.pdf", "url_publica": "/api/resumo.pdf"}

    def salvar_consulta(self, idoso_id: str, data_hora: datetime, profissional: str, local: str | None) -> str:
        cid = _id()
        consulta = Consulta(consulta_id=cid, data_hora=data_hora, profissional=profissional, local=local)
        self._salvar("consulta", cid, consulta.model_dump(mode="json"))
        return cid

    def registrar_relato_consulta(self, consulta_id: str, relato: dict) -> None:
        if (dados := db.ler_registro(self.conta_id, consulta_id)):
            self._salvar("consulta", consulta_id, {**dados, "relato": relato})

    def registrar_estoque(self, item_id: str, quantidade: float, quando: datetime, origem: str) -> None:
        registro = RegistroEstoque(item_id=item_id, quantidade=quantidade, registrado_em=quando, origem=origem)
        self._salvar("estoque", _id(), registro.model_dump(mode="json"))

    def registrar_passo(self, passo: dict) -> None:
        self._salvar("passo", _id(), passo)
