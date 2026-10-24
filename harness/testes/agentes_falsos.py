"""Subagentes falsos para os testes: respostas fixas, sem rede e sem OpenAI (spec §18)."""

from __future__ import annotations

from dataclasses import dataclass, field

from harness.agentes import ResultadoConversa
from harness.agentes.esquemas import (
    ItemInterpretado, ItensInterpretados, LeituraBruta, PerguntaConsulta, PerguntasConsulta, RelatoConsulta,
    RemedioBruto, SaidaDiario,
)


def item(nome: str, conc: str | None, posologia: str = "1 cp de 12/12h", horarios=("08:00", "20:00"),
         confianca: float = 0.95, **extra) -> ItemInterpretado:
    base = dict(nome_lido=nome, concentracao=conc, forma="comprimido", posologia_texto=posologia,
                horarios=list(horarios), unidades_por_dose=1, quantidade_embalagem=None, indicacao_na_receita=None,
                legivel="sim", confianca_modelo=confianca)
    base.update(extra)
    return ItemInterpretado(**base)


@dataclass
class AgentesFalsos:
    interpretacoes: list[ItensInterpretados] = field(default_factory=list)
    conversa: ResultadoConversa | None = None
    diario: list[SaidaDiario] = field(default_factory=list)
    relato: RelatoConsulta | None = None
    chamadas: list[str] = field(default_factory=list)

    def ler(self, imagens, estado) -> LeituraBruta:
        self.chamadas.append("leitor")
        return LeituraBruta(tipo_documento="receita_impressa", texto_cabecalho=None,
                            remedios=[RemedioBruto(texto_remedio="x", texto_posologia=None, texto_embalagem=None, legivel="sim")])

    def interpretar(self, texto, estado) -> ItensInterpretados:
        self.chamadas.append("interprete")
        return self.interpretacoes.pop(0)

    def conversar(self, texto, contexto, ctx, estado) -> ResultadoConversa:
        self.chamadas.append("equipe")
        return self.conversa or ResultadoConversa(texto="Oi! Como posso ajudar?", membro="explicador")

    def estruturar_sintoma(self, texto, contexto, estado) -> SaidaDiario:
        self.chamadas.append("diario")
        return self.diario.pop(0)

    def preparar_perguntas(self, fatos, candidatas, estado) -> PerguntasConsulta:
        self.chamadas.append("preparador")
        return PerguntasConsulta(perguntas=[PerguntaConsulta(texto=c["texto"], origem_id=c["id"]) for c in candidatas[:5]]
                                 + [PerguntaConsulta(texto="Pergunta inventada", origem_id="nao_existe")])

    def estruturar_relato(self, texto, estado) -> RelatoConsulta:
        self.chamadas.append("agenda")
        return self.relato
