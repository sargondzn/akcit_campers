"""Tipos dos contratos C1–C8 (00-projeto/spec §5), do jeito que o harness usa.

Os tipos de C2–C4 já vêm de `contratos/dados.py` (ADR 0001). Os de C1, C5–C8 ficam aqui até
irem para `contratos/` com o acordo dos três. Mudança aqui só com mudança na spec.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Protocol

from pydantic import BaseModel, Field


# ---------- 5.1 Tipos compartilhados ----------

class Anexo(BaseModel):
    caminho: str
    mime: str
    tamanho_bytes: int = 0


StatusItem = Literal["proposto", "nao_confirmado", "ilegivel", "confirmado", "retirado"]


class ItemLido(BaseModel):
    item_id: str
    nome_lido: str
    principio_ativo: list[str] = Field(default_factory=list)
    concentracao: str | None = None
    forma: str | None = None
    posologia_texto: str | None = None
    horarios: list[str] = Field(default_factory=list)
    origem: Literal["receita_foto", "caixa_foto", "receita_pdf", "digitado", "falado"] = "receita_foto"
    confianca: float = 0.0
    status: StatusItem = "proposto"
    prescritor: str | None = None
    data_receita: date | None = None
    indicacao_na_receita: str | None = None
    unidades_por_dose: float | None = None
    quantidade_embalagem: int | None = None


class Mudanca(BaseModel):
    tipo: Literal["novo", "mantido", "alterado", "ausente"]
    item_novo_id: str | None = None
    item_anterior_id: str | None = None
    o_que_mudou: list[str] = Field(default_factory=list)
    nome_diferente: bool = False
    decisao: Literal["continua", "medico_tirou", "nao_sei"] | None = None


# Alerta, SintomaEstruturado, Conduta, ResultadoNormalizacao, ItemParaChecar (C2–C4) e InfoRemedio (C8)
# vêm de `contratos/dados.py` (ADR 0001), para o harness e `dados/` usarem as mesmas classes.
from contratos.dados import (  # noqa: E402
    Alerta, Conduta, InfoRemedio, ItemParaChecar, ResultadoNormalizacao, SintomaEstruturado,
)


# ---------- C1 — Plataforma → harness ----------

TipoAcao = Literal[
    "confirmar_pendencia", "recusar_pendencia", "corrigir_item",
    "definir_escopo", "decidir_item", "contar_estoque",
]


class Acao(BaseModel):
    tipo: TipoAcao
    pendencia_id: str
    dados: dict = Field(default_factory=dict)


class MensagemEntrada(BaseModel):
    mensagem_id: str
    conta_id: str
    idoso_id: str
    tipo: Literal["texto", "foto", "pdf", "audio", "acao"]
    texto: str | None = None
    anexo: Anexo | None = None
    acao: Acao | None = None
    recebida_em: datetime


class Botao(BaseModel):
    rotulo: str
    acao: Acao | None = None
    abre: Literal["camera", "galeria", "pdf", "gravar", "teclado", "tel:192"] | None = None


TipoMensagemSaida = Literal[
    "texto", "lista_para_confirmar", "alertas", "pedido_de_foto", "ligue_192", "resumo",
    "consulta_preparada", "aviso_estoque",
]


class MensagemSaida(BaseModel):
    tipo: TipoMensagemSaida
    texto: str
    audio: Anexo | None = None
    itens: list[ItemLido] | None = None
    mudancas: list[Mudanca] | None = None
    info: list[InfoRemedio] | None = None
    alertas: list[Alerta] | None = None
    resumo_id: str | None = None
    botoes: list[Botao] = Field(default_factory=list)


class EventoAgendado(BaseModel):
    tipo: Literal["verificacao_diaria", "vespera_consulta", "pos_consulta"]
    conta_id: str
    idoso_id: str
    consulta_id: str | None = None
    disparado_em: datetime


class RespostaHarness(BaseModel):
    mensagens: list[MensagemSaida]
    estado: Literal["ok", "aguardando_confirmacao", "erro"] = "ok"


# ---------- C5 — Resumo ----------

class Resumo(BaseModel):
    resumo_id: str
    tipo: Literal["escalonamento", "preparo_consulta"]
    idoso_apelido: str
    periodo_inicio: date
    periodo_fim: date
    motivo: str
    lista_atual: list[ItemLido]
    doses_perdidas: list[dict] = Field(default_factory=list)
    sintomas: list[dict] = Field(default_factory=list)
    alertas: list[Alerta] = Field(default_factory=list)
    perguntas_para_profissional: list[str] = Field(default_factory=list)
    info: list[InfoRemedio] = Field(default_factory=list)
    consulta: dict | None = None
    mudancas_recentes: list[dict] = Field(default_factory=list)
    pontos_para_conferir: list[str] = Field(default_factory=list)
    aviso: str = "Gerado a partir dos relatos da cuidadora. Não é diagnóstico."
    gerado_em: datetime


# ---------- C6 — Repositorio ----------

class ListaVersao(BaseModel):
    versao: int
    confirmada_em: datetime | None = None
    itens: list[ItemLido] = Field(default_factory=list)
    pontos_para_conferir: list[str] = Field(default_factory=list)   # itens "não sei" da conciliação (E1 → E2)


class Horario(BaseModel):
    horario_id: str
    item_id: str
    horario: str
    ativo: bool = True


class Dose(BaseModel):
    horario_id: str
    previsto: datetime
    status: Literal["tomada", "nao_tomada", "sem_resposta"]


class RegistroDiario(BaseModel):
    sintoma: SintomaEstruturado
    conduta: Conduta
    registrado_em: datetime


class MensagemDaConversa(BaseModel):
    autor: Literal["cuidadora", "seri"]
    texto: str
    criada_em: datetime


TipoPendencia = Literal[
    "lista_para_confirmar", "mudanca_cronograma", "diario_aberto", "leitura_baixa_confianca",
    "escopo_receita", "consulta_para_confirmar", "relato_consulta", "quantidade_por_dose",
]


class Pendencia(BaseModel):
    pendencia_id: str
    tipo: TipoPendencia
    dados: dict = Field(default_factory=dict)
    criada_em: datetime
    status: Literal["aberta", "confirmada", "recusada", "resolvida"] = "aberta"


class Consulta(BaseModel):
    consulta_id: str
    data_hora: datetime
    profissional: str
    local: str | None = None
    relato: dict | None = None


class RegistroEstoque(BaseModel):
    item_id: str
    quantidade: float
    registrado_em: datetime
    origem: Literal["falado", "caixa_foto"] = "falado"


class Repositorio(Protocol):
    # leitura (Contexto)
    def obter_idoso(self, idoso_id: str) -> dict: ...
    def obter_lista_atual(self, idoso_id: str) -> ListaVersao | None: ...
    def obter_cronograma(self, idoso_id: str) -> list[Horario]: ...
    def obter_doses(self, idoso_id: str, desde: datetime) -> list[Dose]: ...
    def obter_diario(self, idoso_id: str, desde: datetime) -> list[RegistroDiario]: ...
    def obter_historico(self, conta_id: str, limite: int = 20) -> list[MensagemDaConversa]: ...
    def obter_pendencias(self, conta_id: str) -> list[Pendencia]: ...
    def obter_versoes_lista(self, idoso_id: str, desde: datetime) -> list[ListaVersao]: ...
    def obter_consultas(self, idoso_id: str, desde: datetime) -> list[Consulta]: ...
    def obter_estoque(self, idoso_id: str) -> list[RegistroEstoque]: ...

    # escrita (ferramentas)
    def criar_pendencia(self, conta_id: str, tipo: str, dados: dict) -> str: ...
    def atualizar_pendencia(self, pendencia_id: str, dados: dict) -> None: ...
    def resolver_pendencia(self, pendencia_id: str, resultado: str) -> None: ...
    def salvar_lista_confirmada(self, idoso_id: str, itens: list[ItemLido],
                                pontos_para_conferir: list[str] | None = None) -> int: ...
    def alterar_cronograma(self, idoso_id: str, mudancas: list[dict]) -> None: ...
    def registrar_dose(self, horario_id: str, status: str, quando: datetime) -> None: ...
    def registrar_sintoma(self, idoso_id: str, sintoma: SintomaEstruturado, conduta: Conduta) -> str: ...
    def salvar_resumo(self, resumo: Resumo) -> dict: ...
    def salvar_consulta(self, idoso_id: str, data_hora: datetime, profissional: str, local: str | None) -> str: ...
    def registrar_relato_consulta(self, consulta_id: str, relato: dict) -> None: ...
    def registrar_estoque(self, item_id: str, quantidade: float, quando: datetime, origem: str) -> None: ...
    def registrar_passo(self, passo: dict) -> None: ...
