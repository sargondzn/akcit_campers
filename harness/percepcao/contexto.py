"""Contexto (spec §5, passo 3): bloco compacto com o estado do banco para os agentes.

Leva só o apelido do idoso (spec §3.2, privacidade).
"""

from __future__ import annotations

from datetime import timedelta

from harness import dados_ponte as dados
from harness import estoque as calc_estoque
from harness.ferramentas.registro import ContextoExecucao

DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def montar(ctx: ContextoExecucao) -> str:
    repo, agora = ctx.repo, ctx.agora
    linhas = [
        f"Hoje: {agora:%Y-%m-%d} ({DIAS_SEMANA[agora.weekday()]}), {agora:%H:%M}.",
        f"Pessoa cuidada: {repo.obter_idoso(ctx.idoso_id).get('apelido', 'a pessoa idosa')}.",
    ]
    itens = ctx.itens_atuais()
    horarios = repo.obter_cronograma(ctx.idoso_id)
    if itens:
        linhas.append("Lista de remédios:")
        for i in itens:
            hs = ", ".join(h.horario for h in horarios if h.item_id == i.item_id) or "sem horário"
            uso = ""
            if i.principio_ativo and (info := dados.info_remedio(i.principio_ativo[0])):
                uso = f"; usado para {info.para_que_serve}"
            linhas.append(f"- {i.nome_lido} ({i.concentracao or '?'}), {i.posologia_texto or ''} [{hs}]{uso}"
                          + ("" if i.status == "confirmado" else f" — {i.status}"))
    else:
        linhas.append("Ainda não há lista de remédios confirmada.")

    pendencias = repo.obter_pendencias(ctx.conta_id)
    if pendencias:
        linhas.append("Pendências abertas: " + ", ".join(p.tipo for p in pendencias))

    doses = repo.obter_doses(ctx.idoso_id, agora - timedelta(days=7))
    if doses:
        perdidas = sum(1 for d in doses if d.status != "tomada")
        linhas.append(f"Doses dos últimos 7 dias: {len(doses)} registradas, {perdidas} não tomadas ou sem resposta.")

    diario = repo.obter_diario(ctx.idoso_id, agora - timedelta(days=7))
    for r in diario[-3:]:
        linhas.append(f"Sintoma em {r.registrado_em:%d/%m}: {r.sintoma.descricao} (conduta: {r.conduta.nivel}).")

    for c in repo.obter_consultas(ctx.idoso_id, agora)[:3]:
        linhas.append(f"Consulta marcada: {c.profissional}, {c.data_hora:%d/%m às %H:%M}.")

    for e in calc_estoque.calcular(itens, horarios, doses, repo.obter_estoque(ctx.idoso_id), agora):
        if e.dias_restantes is not None:
            linhas.append(f"Estoque de {e.nome}: cerca de {int(e.dias_restantes)} dias.")

    historico = repo.obter_historico(ctx.conta_id, limite=20)
    if historico:
        linhas.append("Conversa recente:")
        linhas += [f"{m.autor}: {m.texto[:200]}" for m in historico]
    return "\n".join(linhas)
