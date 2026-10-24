"""Estoque e validade da receita (E4, spec §12): contas determinísticas, sem modelo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from harness import dados_ponte as dados
from harness.contratos import Dose, Horario, ItemLido, RegistroEstoque

AVISOS_DIAS = (7, 2)          # HA-D11
AVISO_RECEITA_DIAS = 7        # HA-D11


@dataclass
class EstadoEstoque:
    item_id: str
    nome: str
    estoque_estimado: float
    consumo_diario: float
    dias_restantes: float | None
    acaba_em: date | None


def calcular(itens: list[ItemLido], cronograma: list[Horario], doses: list[Dose],
             registros: list[RegistroEstoque], agora: datetime) -> list[EstadoEstoque]:
    por_item_horarios: dict[str, list[Horario]] = {}
    for h in cronograma:
        if h.ativo:
            por_item_horarios.setdefault(h.item_id, []).append(h)
    nao_tomadas = {(d.horario_id, d.previsto.date()) for d in doses if d.status == "nao_tomada"}
    ultimo = {r.item_id: r for r in registros}
    estados: list[EstadoEstoque] = []
    for item in itens:
        if item.status != "confirmado" or item.item_id not in ultimo:
            continue
        reg = ultimo[item.item_id]
        horarios = por_item_horarios.get(item.item_id, [])
        por_dose = item.unidades_por_dose or 0
        consumo = por_dose * len(horarios)
        gasto = 0.0
        if por_dose and horarios:
            dia = reg.registrado_em.date()
            while dia <= agora.date():
                for h in horarios:
                    hh, mm = (int(x) for x in h.horario.split(":"))
                    momento = datetime.combine(dia, datetime.min.time()).replace(hour=hh, minute=mm)
                    if reg.registrado_em < momento <= agora and (h.horario_id, dia) not in nao_tomadas:
                        gasto += por_dose
                dia += timedelta(days=1)
        restante = max(reg.quantidade - gasto, 0)
        dias = restante / consumo if consumo else None
        acaba = (agora + timedelta(days=dias)).date() if dias is not None else None
        estados.append(EstadoEstoque(item.item_id, item.nome_lido, restante, consumo, dias, acaba))
    return estados


def avisos_de_estoque(estados: list[EstadoEstoque]) -> list[EstadoEstoque]:
    """Avisa no dia em que faltam 7 e no dia em que faltam 2 dias (sem guardar memória)."""
    return [e for e in estados if e.dias_restantes is not None and int(e.dias_restantes) in AVISOS_DIAS]


def validade(item: ItemLido) -> date | None:
    if not item.data_receita or not item.principio_ativo:
        return None
    info = dados.info_remedio(item.principio_ativo[0])
    if not info or not info.validade_receita_dias:
        return None
    return item.data_receita + timedelta(days=info.validade_receita_dias)


def receitas_vencendo(itens: list[ItemLido], hoje: date, dias: int = AVISO_RECEITA_DIAS,
                      exato: bool = True) -> list[tuple[ItemLido, date]]:
    saida = []
    for item in itens:
        if item.status != "confirmado":
            continue
        vence = validade(item)
        if vence is None:
            continue
        falta = (vence - hoje).days
        if (falta == dias) if exato else (0 <= falta <= dias):
            saida.append((item, vence))
    return saida
