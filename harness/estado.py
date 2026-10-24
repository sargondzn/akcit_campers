"""EstadoMensagem (spec §3.3): o que uma mensagem gerou, descartado no fim."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from harness.contratos import Alerta, Botao, Conduta, InfoRemedio, ItemLido


@dataclass
class EstadoMensagem:
    mensagem_id: str
    conta_id: str
    idoso_id: str
    inicio: float = field(default_factory=time.monotonic)
    chamadas_ferramenta: int = 0
    alertas: list[Alerta] = field(default_factory=list)
    condutas: list[Conduta] = field(default_factory=list)
    infos: list[InfoRemedio] = field(default_factory=list)
    itens_proposta: list[ItemLido] = field(default_factory=list)
    botoes_extra: list[Botao] = field(default_factory=list)   # pendências criadas por ferramentas
    pediu_foto: str | None = None
    pendencia_criada: bool = False
    passos: list[dict] = field(default_factory=list)

    def passo(self, tipo: str, conteudo: str, agente: str | None = None, duracao_ms: int | None = None,
              modelo: str | None = None, tokens_entrada: int | None = None, tokens_saida: int | None = None) -> None:
        self.passos.append({
            "mensagem_id": self.mensagem_id, "ordem": len(self.passos) + 1, "tipo": tipo, "agente": agente,
            "conteudo": conteudo[:300], "duracao_ms": duracao_ms, "modelo": modelo,
            "tokens_entrada": tokens_entrada, "tokens_saida": tokens_saida,
        })

    def tempo_restante(self, orcamento_s: int) -> float:
        return orcamento_s - (time.monotonic() - self.inicio)
