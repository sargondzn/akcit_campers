"""Fluxo de leitura + conciliação (spec §2.4, §6, §7). Ordem fixa (HA-D1).

extrair → Leitor → Intérprete → pós-processamento → confiança baixa → caixa já na lista
→ escopo da receita → conciliar → checar_lista → proposta
"""

from __future__ import annotations

import json
import uuid
from datetime import date

from harness import conciliacao
from harness import dados_ponte as dados
from harness.agentes import Agentes
from harness.agentes.esquemas import ItemInterpretado, ItensInterpretados, LeituraBruta
from harness.config import CONFIG
from harness.contratos import Acao, Botao, ItemLido, ItemParaChecar, MensagemEntrada, MensagemSaida, Mudanca
from harness.ferramentas.registro import ContextoExecucao
from harness.fluxos.base import executar
from harness.guardrails import frases
from harness.percepcao import pdf

LIMIAR_CONFIANCA = 0.7          # HA-D3
TETO_SEM_NORMALIZAR = 0.5       # spec §6.4
ORIGEM = {"caixa": "caixa_foto", "receita_pdf": "receita_pdf"}


def _data(texto: str | None) -> date | None:
    try:
        return date.fromisoformat(texto) if texto else None
    except ValueError:
        return None


def pos_processar(interpretado: ItensInterpretados, origem_padrao: str) -> list[ItemLido]:
    """Spec §6.4: normalizar, confiança final e o vínculo com o documento."""
    itens = []
    origem = ORIGEM.get(interpretado.tipo_documento, origem_padrao)
    for bruto in interpretado.itens:
        itens.append(item_de(bruto, interpretado, origem))
    return itens


def item_de(bruto: ItemInterpretado, doc: ItensInterpretados, origem: str) -> ItemLido:
    norm = dados.normalizar(" ".join(filter(None, [bruto.nome_lido, bruto.concentracao])))
    confianca = max(0.0, min(1.0, bruto.confianca_modelo))
    if bruto.legivel == "nao":
        confianca = min(confianca, 0.3)
    concentracao = bruto.concentracao or norm.concentracao
    if not norm.encontrado or not bruto.nome_lido or not concentracao:
        confianca = min(confianca, TETO_SEM_NORMALIZAR)
    return ItemLido(
        item_id=uuid.uuid4().hex[:10], nome_lido=bruto.nome_lido, principio_ativo=norm.principio_ativo,
        concentracao=concentracao, forma=bruto.forma, posologia_texto=bruto.posologia_texto,
        horarios=[h for h in bruto.horarios if len(h) == 5 and h[2] == ":"], origem=origem, confianca=round(confianca, 2),
        status="proposto" if confianca >= LIMIAR_CONFIANCA else "nao_confirmado",
        prescritor=doc.prescritor, data_receita=_data(doc.data_receita),
        indicacao_na_receita=bruto.indicacao_na_receita, unidades_por_dose=bruto.unidades_por_dose,
        quantidade_embalagem=bruto.quantidade_embalagem,
    )


def _infos(ctx: ContextoExecucao, itens: list[ItemLido]):
    infos = [info for i in itens for p in i.principio_ativo if (info := dados.info_remedio(p))]
    ctx.estado.infos += infos
    return infos


def _resumo_mudanca(m: Mudanca, por_id: dict[str, ItemLido], anteriores: dict[str, ItemLido]) -> str | None:
    if m.tipo != "alterado":
        return None
    novo = por_id.get(m.item_anterior_id) or por_id.get(m.item_novo_id)
    antigo = anteriores.get(m.item_anterior_id)
    if not novo or not antigo:
        return None
    fmt = lambda i: f"{i.concentracao or '?'}, {', '.join(i.horarios) or 'sem horário'}"
    return f"{novo.nome_lido} mudou. Antes: {fmt(antigo)} · Agora: {fmt(novo)}."


def emitir_proposta(ctx: ContextoExecucao, itens: list[ItemLido], mudancas: list[Mudanca],
                    anteriores: list[ItemLido]) -> list[MensagemSaida]:
    """Cria a pendência `lista_para_confirmar` e as mensagens da proposta (spec §6.6, §7.4)."""
    ativos = [i for i in itens if i.status not in ("ilegivel", "retirado")]
    alertas = dados.checar_lista([ItemParaChecar(item_id=i.item_id, principio_ativo=i.principio_ativo) for i in ativos])
    ctx.estado.alertas += alertas
    ctx.estado.itens_proposta = itens
    infos = _infos(ctx, itens)
    pid = ctx.repo.criar_pendencia(ctx.conta_id, "lista_para_confirmar", {
        "itens": [i.model_dump(mode="json") for i in itens],
        "mudancas": [m.model_dump(mode="json") for m in mudancas],
    })
    ctx.estado.pendencia_criada = True

    if mudancas:
        conta = lambda t: sum(1 for m in mudancas if m.tipo == t)
        texto = frases.RESUMO_CONCILIACAO.format(novos=conta("novo"), alterados=conta("alterado"), ausentes=conta("ausente"))
    else:
        texto = frases.PROPOSTA
    msgs = [MensagemSaida(
        tipo="lista_para_confirmar", texto=texto, itens=itens, mudancas=mudancas or None, info=infos or None,
        alertas=alertas or None,
        botoes=[Botao(rotulo="Confirmo a lista", acao=Acao(tipo="confirmar_pendencia", pendencia_id=pid)),
                Botao(rotulo="Corrigir um item", abre="teclado")],
    )]
    por_id = {i.item_id: i for i in itens}
    antes = {i.item_id: i for i in anteriores}
    for m in mudancas:
        if (linha := _resumo_mudanca(m, por_id, antes)):
            msgs.append(MensagemSaida(tipo="texto", texto=linha))
        if m.tipo == "mantido" and m.nome_diferente and (i := por_id.get(m.item_anterior_id)):
            msgs.append(MensagemSaida(tipo="texto", texto=f"{i.nome_lido}: {frases.MESMO_REMEDIO}"))
    if alertas:
        msgs.append(MensagemSaida(tipo="alertas", alertas=alertas,
                                  texto="\n".join(frases.ALERTA.format(descricao=a.descricao, fonte=a.fonte) for a in alertas)))
    for m in mudancas:
        if m.tipo == "ausente" and (antigo := antes.get(m.item_anterior_id)):
            msgs.append(MensagemSaida(tipo="texto", texto=frases.AUSENTE.format(nome=antigo.nome_lido), botoes=[
                Botao(rotulo=rotulo, acao=Acao(tipo="decidir_item", pendencia_id=pid,
                                               dados={"item_anterior_id": antigo.item_id, "decisao": decisao}))
                for rotulo, decisao in (("Continua", "continua"), ("O médico tirou", "medico_tirou"), ("Não sei", "nao_sei"))
            ]))
    return msgs


def propor(ctx: ContextoExecucao, novos: list[ItemLido], escopo: str, prescritor: str | None) -> list[MensagemSaida]:
    atual = ctx.itens_atuais()
    if not atual:
        return emitir_proposta(ctx, novos, [], [])
    mudancas = conciliacao.conciliar(atual, novos, escopo, prescritor)
    resultante = conciliacao.lista_resultante(atual, novos, mudancas)
    return emitir_proposta(ctx, resultante, mudancas, atual)


def perguntar_escopo(ctx: ContextoExecucao, novos: list[ItemLido], prescritor: str | None,
                     tipo_documento: str) -> list[MensagemSaida]:
    pid = ctx.repo.criar_pendencia(ctx.conta_id, "escopo_receita", {
        "itens": [i.model_dump(mode="json") for i in novos], "prescritor": prescritor,
    })
    ctx.estado.pendencia_criada = True
    ctx.estado.itens_proposta = novos
    de_quem = f"do {prescritor}" if prescritor else "de um médico"
    texto = frases.ESCOPO_ALTA if tipo_documento == "receita_alta" else frases.ESCOPO.format(de_quem=de_quem)
    opcoes = [("Toda a lista", "toda_lista"), ("Só os remédios desse médico", "medico"), ("É só um remédio a mais", "acrescimo")]
    if tipo_documento != "receita_alta":
        opcoes = [opcoes[1], opcoes[0], opcoes[2]] if prescritor else opcoes
    return [MensagemSaida(tipo="texto", texto=texto, botoes=[
        Botao(rotulo=r, acao=Acao(tipo="definir_escopo", pendencia_id=pid, dados={"escopo": e})) for r, e in opcoes
    ])]


def executar_leitura(entrada: MensagemEntrada, ctx: ContextoExecucao, agentes: Agentes) -> list[MensagemSaida]:
    saidas: list[MensagemSaida] = []
    c: dict = {}

    def extrair(c):
        caminho = entrada.anexo.caminho
        if entrada.tipo == "pdf":
            texto = pdf.extrair_texto(caminho)
            if len(texto) > 30:
                c["texto"], c["origem"] = texto, "receita_pdf"
                return
            c["imagens"] = pdf.paginas_como_imagem(caminho, CONFIG.caminho_armazenamento / "tmp_pdf")
            c["origem"] = "receita_pdf"
        else:
            c["imagens"], c["origem"] = [caminho], "receita_foto"

    def ler(c):
        if "imagens" not in c:
            return
        leituras: list[LeituraBruta] = [agentes.ler([img], ctx.estado) for img in c["imagens"]]
        remedios = [r for l in leituras for r in l.remedios]
        if not remedios:
            saidas.append(MensagemSaida(tipo="pedido_de_foto", texto=frases.NADA_LIDO, botoes=_botoes_foto()))
            c["_parar"] = True
            return
        c["tipo_documento"] = leituras[0].tipo_documento
        c["texto"] = json.dumps({"tipo_documento": leituras[0].tipo_documento,
                                 "cabecalho": " | ".join(filter(None, (l.texto_cabecalho for l in leituras))),
                                 "remedios": [r.model_dump() for r in remedios]}, ensure_ascii=False)

    def interpretar(c):
        c["interpretado"] = agentes.interpretar(c["texto"], ctx.estado)
        if "tipo_documento" not in c:
            c["tipo_documento"] = c["interpretado"].tipo_documento

    def pos_processamento(c):
        c["itens"] = pos_processar(c["interpretado"], c["origem"])
        if not c["itens"]:
            saidas.append(MensagemSaida(tipo="pedido_de_foto", texto=frases.NADA_LIDO, botoes=_botoes_foto()))
            c["_parar"] = True

    def confianca_baixa(c):
        baixos = [i for i in c["itens"] if i.status == "nao_confirmado"]
        abertas = [p for p in ctx.repo.obter_pendencias(ctx.conta_id) if p.tipo == "leitura_baixa_confianca"]
        if not baixos:
            for p in abertas:
                ctx.repo.resolver_pendencia(p.pendencia_id, "resolvida")
            return
        nome = baixos[0].nome_lido if len(baixos) == 1 and baixos[0].nome_lido else "um dos remédios"
        if not abertas:
            ctx.repo.criar_pendencia(ctx.conta_id, "leitura_baixa_confianca", {"nomes": [b.nome_lido for b in baixos]})
            saidas.append(MensagemSaida(tipo="pedido_de_foto", texto=frases.LEITURA_BAIXA_1.format(nome=nome),
                                        botoes=_botoes_foto()))
        else:
            saidas.append(MensagemSaida(tipo="pedido_de_foto", texto=frases.LEITURA_BAIXA_2.format(nome=nome), botoes=[
                Botao(rotulo="Foto da caixa deste remédio", abre="camera"),
                Botao(rotulo="Digitar ou falar o nome", abre="teclado")]))

    def caixa_ja_na_lista(c):
        if c["tipo_documento"] != "caixa" or len(c["itens"]) != 1:
            return
        novo = c["itens"][0]
        for atual in ctx.itens_atuais():
            if set(atual.principio_ativo) == set(novo.principio_ativo) and novo.principio_ativo and \
                    conciliacao._conc(atual.concentracao) == conciliacao._conc(novo.concentracao):
                botoes = [Botao(rotulo="Não", abre=None)]
                if novo.quantidade_embalagem:
                    botoes.insert(0, Botao(rotulo="Contar esta caixa no estoque", acao=Acao(
                        tipo="contar_estoque", pendencia_id="",
                        dados={"item_id": atual.item_id, "quantidade": novo.quantidade_embalagem})))
                saidas.append(MensagemSaida(tipo="texto", texto=frases.CAIXA_JA_NA_LISTA.format(nome=atual.nome_lido),
                                            botoes=botoes))
                ctx.estado.itens_proposta = [novo]
                c["_parar"] = True
                return

    def escopo(c):
        if not ctx.itens_atuais():
            c["escopo"] = "toda_lista"
        elif c["tipo_documento"] == "caixa":
            c["escopo"] = "acrescimo"
        else:
            saidas.extend(perguntar_escopo(ctx, c["itens"], c["interpretado"].prescritor, c["tipo_documento"]))
            c["_parar"] = True

    def proposta(c):
        saidas.extend(propor(ctx, c["itens"], c["escopo"], c["interpretado"].prescritor))

    executar("leitura", [extrair, ler, interpretar, pos_processamento, confianca_baixa, caixa_ja_na_lista,
                         escopo, proposta], c)
    # o pedido de nova foto vem depois da proposta, para a cuidadora ver o que já foi lido
    return sorted(saidas, key=lambda m: m.tipo == "pedido_de_foto")


def _botoes_foto() -> list[Botao]:
    return [Botao(rotulo="Tirar foto", abre="camera"), Botao(rotulo="Escolher da galeria", abre="galeria")]
