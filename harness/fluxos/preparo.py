"""Preparo da consulta (E2, spec §11.2) e pergunta pós-consulta (§11.3)."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta

from harness import conciliacao
from harness import estoque as calc_estoque
from harness import resumo as montar_resumo
from harness.agentes import Agentes
from harness.contratos import Botao, Consulta, ItemLido, MensagemSaida
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos.base import executar
from harness.guardrails import auditor, frases

MAX_PERGUNTAS = 5


def _consulta(ctx: ContextoExecucao, consulta_id: str | None) -> Consulta | None:
    consultas = ctx.repo.obter_consultas(ctx.idoso_id, ctx.agora - timedelta(days=60))
    if consulta_id:
        return next((c for c in consultas if c.consulta_id == consulta_id), None)
    futuras = [c for c in consultas if c.data_hora >= ctx.agora]
    return futuras[0] if futuras else None


def _desde(ctx: ContextoExecucao, consulta: Consulta):
    anteriores = [c for c in ctx.repo.obter_consultas(ctx.idoso_id, ctx.agora - timedelta(days=365))
                  if c.data_hora < ctx.agora and c.profissional == consulta.profissional and c.consulta_id != consulta.consulta_id]
    return anteriores[-1].data_hora if anteriores else ctx.agora - timedelta(days=30)


def _mudancas_recentes(ctx: ContextoExecucao, desde) -> list[dict]:
    versoes = ctx.repo.obter_versoes_lista(ctx.idoso_id, desde - timedelta(days=3650))
    saida = []
    for anterior, atual in zip(versoes, versoes[1:]):
        if not atual.confirmada_em or atual.confirmada_em < desde:
            continue
        novos = [i for i in atual.itens if i.status != "retirado"]
        for m in conciliacao.conciliar(anterior.itens, novos, "toda_lista"):
            if m.tipo == "mantido":
                continue
            ref = next((i for i in atual.itens + anterior.itens if i.item_id in (m.item_novo_id, m.item_anterior_id)), None)
            retirado = any(i.item_id == m.item_anterior_id and i.status == "retirado" for i in atual.itens)
            saida.append({"data": atual.confirmada_em.date().isoformat(), "nome": ref.nome_lido if ref else "?",
                          "tipo": "retirado" if retirado else m.tipo, "o_que_mudou": m.o_que_mudou})
    return saida


def executar_preparo(consulta_id: str | None, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    saidas: list[MensagemSaida] = []
    c: dict = {}

    def dossie(c):
        consulta = _consulta(ctx, consulta_id)
        if not consulta:
            c["_parar"] = True
            return
        desde = _desde(ctx, consulta)
        itens = ctx.itens_atuais()
        lista = ctx.repo.obter_lista_atual(ctx.idoso_id)
        pontos = list(lista.pontos_para_conferir) if lista else []
        pontos += [f"{i.nome_lido} ainda não foi confirmado" for i in itens if i.status in ("nao_confirmado", "ilegivel")]
        for item, vence in calc_estoque.receitas_vencendo(itens, ctx.agora.date(), dias=30, exato=False):
            pontos.append(f"A receita da {item.nome_lido} vence em {vence:%d/%m}")
        horarios = ctx.repo.obter_cronograma(ctx.idoso_id)
        doses = ctx.repo.obter_doses(ctx.idoso_id, ctx.agora - timedelta(days=90))
        for e in calc_estoque.calcular(itens, horarios, doses, ctx.repo.obter_estoque(ctx.idoso_id), ctx.agora):
            if e.dias_restantes is not None and e.dias_restantes <= 7:
                pontos.append(f"A {e.nome} está acabando")
        c.update(consulta=consulta, desde=desde, pontos=pontos, mudancas=_mudancas_recentes(ctx, desde),
                 perdidas=montar_resumo.doses_perdidas(ctx, desde), sintomas=montar_resumo.sintomas(ctx, desde),
                 alertas=montar_resumo.alertas_da_lista(ctx))

    def candidatas(c):
        cand = []
        for n, a in enumerate(c["alertas"]):
            cand.append({"id": f"alerta_{n}", "texto": f"Sobre este aviso: {a.descricao}. Isso preocupa no caso dela?"})
        for n, p in enumerate(c["pontos"]):
            if "não veio na receita nova" in p:
                nome = p.split(" não veio")[0]
                texto = f"A {nome} não veio na receita nova. Ela deve continuar tomando?"
            elif "vence" in p:
                texto = f"{p}. Pode renovar?"
            elif "acabando" in p:
                texto = f"{p}. Precisa de receita nova?"
            else:
                texto = f"{p}. Pode conferir comigo?"
            cand.append({"id": f"ponto_{n}", "texto": texto})
        for n, (nome, qtd) in enumerate(Counter(d["nome"] for d in c["perdidas"]).most_common()):
            if qtd >= 2:
                cand.append({"id": f"dose_{n}", "texto": f"Ela deixou de tomar a {nome} {qtd} vezes. Isso preocupa?"})
        for n, s in enumerate(c["sintomas"]):
            quando = f" ({s['inicio']})" if s.get("inicio") else ""
            cand.append({"id": f"sintoma_{n}", "texto": f"Ela teve {s['descricao'].rstrip('.').lower()}{quando}. Pode ter relação com algum remédio?"})
        for n, m in enumerate(c["mudancas"]):
            if m["tipo"] == "alterado":
                cand.append({"id": f"mudanca_{n}", "texto": f"A {m['nome']} mudou em {m['data']}. Está tudo certo com a mudança?"})
        c["candidatas"] = cand

    def perguntas(c):
        cand = {x["id"]: x["texto"] for x in c["candidatas"]}
        escolhidas: list[str] = []
        if cand:
            fatos = (f"Consulta: {c['consulta'].profissional}. Pontos: {c['pontos']}. Mudanças: {c['mudancas']}. "
                     f"Sintomas: {[s['descricao'] for s in c['sintomas']]}.")
            try:
                saida = agentes.preparar_perguntas(fatos, c["candidatas"], ctx.estado)
                escolhidas = [p.texto for p in saida.perguntas if p.origem_id in cand][:MAX_PERGUNTAS]
            except Exception as erro:  # sem reescrita, ficam as candidatas (spec §11.2, passo 4)
                ctx.estado.passo("resultado", f"preparador falhou: {erro}")
            if not escolhidas:
                escolhidas = list(cand.values())[:MAX_PERGUNTAS]
        historico = [i for v in ctx.repo.obter_versoes_lista(ctx.idoso_id, ctx.agora - timedelta(days=3650)) for i in v.itens]
        nomes_pontos = [ItemLido(item_id=f"ponto_{n}", nome_lido=p.split(" não veio")[0]) for n, p in enumerate(c["pontos"])]
        contexto_aud = auditor.ContextoAuditor(itens=ctx.itens_atuais() + historico + nomes_pontos,
                                               tem_alerta=bool(c["alertas"]), tem_info=True)
        c["perguntas"] = [p for p in escolhidas if auditor.verificar(p, contexto_aud).aprovado]

    def pagina(c):
        consulta = c["consulta"]
        resumo = montar_resumo.montar(
            ctx, "preparo_consulta", f"Consulta com {consulta.profissional}", c["desde"],
            perguntas_para_profissional=c["perguntas"], pontos_para_conferir=c["pontos"],
            mudancas_recentes=c["mudancas"],
            consulta={"data_hora": consulta.data_hora.isoformat(), "profissional": consulta.profissional,
                      "local": consulta.local},
        )
        ctx.repo.salvar_resumo(resumo)
        saidas.append(MensagemSaida(
            tipo="consulta_preparada", resumo_id=resumo.resumo_id,
            texto=frases.CONSULTA_PREPARADA.format(profissional=consulta.profissional, hora=f"{consulta.data_hora:%H:%M}"),
        ))

    executar("preparo_consulta", [dossie, candidatas, perguntas, pagina], c)
    return saidas


def perguntar_pos_consulta(consulta_id: str | None, ctx: ContextoExecucao) -> list[MensagemSaida]:
    consulta = _consulta(ctx, consulta_id)
    if not consulta:
        return []
    ctx.repo.criar_pendencia(ctx.conta_id, "relato_consulta", {"consulta_id": consulta.consulta_id})
    ctx.estado.pendencia_criada = True
    return [MensagemSaida(tipo="texto", texto=frases.POS_CONSULTA.format(profissional=consulta.profissional),
                          botoes=[Botao(rotulo="Gravar áudio", abre="gravar"), Botao(rotulo="Escrever", abre="teclado"),
                                  Botao(rotulo="Foto da receita nova", abre="camera")])]
