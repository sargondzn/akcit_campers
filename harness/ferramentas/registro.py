"""Registro de ferramentas (spec §17.1). Funções Python puras, presas ao contexto da mensagem.

Cada agente só recebe as ferramentas da sua coluna "Usada por". As que exigem confirmação
não executam: criam pendência e devolvem "aguardando confirmação" (spec §13.2).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Literal

from harness import dados_ponte as dados
from harness import estoque as calc_estoque
from harness.config import CONFIG
from harness.contratos import Acao, Botao, ItemLido, ItemParaChecar
from harness.estado import EstadoMensagem
from harness.guardrails import frases


@dataclass
class ContextoExecucao:
    repo: object
    conta_id: str
    idoso_id: str
    estado: EstadoMensagem
    agora: datetime

    # atalhos usados por ferramentas, fluxos e núcleo
    def itens_atuais(self) -> list[ItemLido]:
        lista = self.repo.obter_lista_atual(self.idoso_id)
        return [i for i in lista.itens if i.status != "retirado"] if lista else []

    def achar_item(self, nome: str) -> ItemLido | None:
        alvo = dados.texto_normalizado(nome)
        principio = dados.normalizar(nome).principio_ativo
        for item in self.itens_atuais():
            nome_item = dados.texto_normalizado(item.nome_lido)
            if alvo and (alvo in nome_item or nome_item.split(" ")[0] in alvo):
                return item
            if principio and set(principio) == set(item.principio_ativo):
                return item
        return None


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def construir(ctx: ContextoExecucao) -> dict[str, Callable]:
    repo, est = ctx.repo, ctx.estado

    def consultar_lista() -> str:
        """Mostra a lista atual de remédios, os horários de cada um e as pendências abertas."""
        horarios = repo.obter_cronograma(ctx.idoso_id)
        itens = []
        for i in ctx.itens_atuais():
            itens.append({"nome": i.nome_lido, "principio_ativo": i.principio_ativo, "concentracao": i.concentracao,
                          "posologia": i.posologia_texto, "status": i.status,
                          "horarios": [h.horario for h in horarios if h.item_id == i.item_id]})
        pend = [p.tipo for p in repo.obter_pendencias(ctx.conta_id)]
        return _json({"remedios": itens, "pendencias": pend})

    def consultar_doses(dias: int = 7) -> str:
        """Mostra as doses dos últimos dias: tomadas, não tomadas e sem resposta."""
        nomes = {i.item_id: i.nome_lido for i in ctx.itens_atuais()}
        por_horario = {h.horario_id: h for h in repo.obter_cronograma(ctx.idoso_id)}
        saida = []
        for d in repo.obter_doses(ctx.idoso_id, ctx.agora - timedelta(days=dias)):
            h = por_horario.get(d.horario_id)
            saida.append({"remedio": nomes.get(h.item_id) if h else None, "previsto": d.previsto, "status": d.status})
        return _json(saida)

    def registrar_dose(remedio: str, horario: str, status: Literal["tomada", "nao_tomada"]) -> str:
        """Registra que a dose de um remédio num horário (HH:MM) foi dada (tomada) ou não (nao_tomada)."""
        item = ctx.achar_item(remedio)
        if not item:
            return "Remédio não encontrado na lista."
        for h in repo.obter_cronograma(ctx.idoso_id):
            if h.item_id == item.item_id and h.horario == horario:
                hh, mm = (int(x) for x in horario.split(":"))
                repo.registrar_dose(h.horario_id, status, ctx.agora.replace(hour=hh, minute=mm, second=0, microsecond=0))
                return f"Registrado: {item.nome_lido} das {horario} — {status}."
        return "Esse horário não está no cronograma desse remédio."

    def alterar_cronograma(remedio: str, acao: Literal["incluir", "remover", "mudar"], horario: str,
                           novo_horario: str | None = None) -> str:
        """Propõe incluir, remover ou mudar um horário (HH:MM) de um remédio. Só vale depois da confirmação da cuidadora."""
        item = ctx.achar_item(remedio)
        if not item:
            return "Remédio não encontrado na lista."
        mudanca = {"item_id": item.item_id, "acao": acao, "horario": horario, "novo_horario": novo_horario}
        pid = repo.criar_pendencia(ctx.conta_id, "mudanca_cronograma", {"mudancas": [mudanca], "nome": item.nome_lido})
        est.pendencia_criada = True
        est.botoes_extra += [
            Botao(rotulo="Confirmo", acao=Acao(tipo="confirmar_pendencia", pendencia_id=pid)),
            Botao(rotulo="Cancelar", acao=Acao(tipo="recusar_pendencia", pendencia_id=pid)),
        ]
        return "Aguardando a confirmação da cuidadora no botão."

    def pedir_foto(tipo: Literal["receita", "caixa"]) -> str:
        """Pede à cuidadora uma foto da receita ou da caixa do remédio."""
        est.pediu_foto = tipo
        return "Os botões de foto vão aparecer para ela."

    def normalizar(nome: str) -> str:
        """Descobre o princípio ativo de um remédio a partir do nome."""
        return dados.normalizar(nome).model_dump_json()

    def checar_lista() -> str:
        """Verifica alertas (interações, duplicidades, remédios que pedem cuidado em idosos) na lista atual."""
        itens = ctx.itens_atuais()
        alertas = dados.checar_lista([ItemParaChecar(item_id=i.item_id, principio_ativo=i.principio_ativo) for i in itens])
        est.alertas += alertas
        if not alertas:
            return "Nenhum alerta na lista atual."
        return _json([frases.ALERTA.format(descricao=a.descricao, fonte=a.fonte) for a in alertas])

    def info_remedio(nome: str) -> str:
        """Para que serve um remédio, se ele sai de graça no Farmácia Popular e a validade da receita."""
        item = ctx.achar_item(nome)
        principios = item.principio_ativo if item else dados.normalizar(nome).principio_ativo
        if not principios:
            return frases.SEM_INFO
        textos = []
        for p in principios:
            info = dados.info_remedio(p)
            if not info:
                textos.append(frases.SEM_INFO)
                continue
            est.infos.append(info)
            nome_exibido = item.nome_lido if item and len(principios) == 1 else p
            t = frases.PARA_QUE_SERVE.format(nome=nome_exibido, uso=info.para_que_serve)
            if item and item.indicacao_na_receita:
                t += " " + frases.NA_RECEITA.format(indicacao=item.indicacao_na_receita)
            if info.farmacia_popular:
                t += " " + frases.FARMACIA_POPULAR.format(nome=nome_exibido, documentos=frases.juntar(info.documentos_farmacia_popular))
            textos.append(t)
        return " ".join(textos)

    def consultar_consultas() -> str:
        """Mostra as próximas consultas e as que já passaram (últimos 60 dias)."""
        consultas = repo.obter_consultas(ctx.idoso_id, ctx.agora - timedelta(days=60))
        return _json([{"quando": c.data_hora, "profissional": c.profissional, "local": c.local,
                       "ja_passou": c.data_hora < ctx.agora} for c in consultas]) if consultas else "Nenhuma consulta marcada."

    def registrar_consulta(data_hora: str, profissional: str, local: str | None = None) -> str:
        """Marca uma consulta (data_hora no formato AAAA-MM-DDTHH:MM). Só vale depois da confirmação da cuidadora."""
        try:
            quando = datetime.fromisoformat(data_hora)
        except ValueError:
            return "Data inválida. Pergunte a data e a hora de novo."
        if quando < ctx.agora:
            return "Essa data já passou. Pergunte a data de novo."
        pid = repo.criar_pendencia(ctx.conta_id, "consulta_para_confirmar",
                                   {"data_hora": quando.isoformat(), "profissional": profissional, "local": local})
        est.pendencia_criada = True
        est.botoes_extra += [
            Botao(rotulo="Está certo", acao=Acao(tipo="confirmar_pendencia", pendencia_id=pid)),
            Botao(rotulo="Corrigir", acao=Acao(tipo="recusar_pendencia", pendencia_id=pid), abre="teclado"),
        ]
        quando_txt = quando.strftime("%d/%m às %H:%M")
        return f"Aguardando confirmação. Diga exatamente: '{frases.CONSULTA_CONFIRMAR.format(profissional=profissional, quando=quando_txt)}'"

    def consultar_estoque() -> str:
        """Mostra quanto ainda tem de cada remédio e quando deve acabar."""
        estados = calc_estoque.calcular(ctx.itens_atuais(), repo.obter_cronograma(ctx.idoso_id),
                                        repo.obter_doses(ctx.idoso_id, ctx.agora - timedelta(days=90)),
                                        repo.obter_estoque(ctx.idoso_id), ctx.agora)
        if not estados:
            return "Nenhum estoque registrado ainda."
        return _json([{"remedio": e.nome, "restante": round(e.estoque_estimado, 1),
                       "dias_restantes": None if e.dias_restantes is None else int(e.dias_restantes),
                       "acaba_em": e.acaba_em} for e in estados])

    def registrar_estoque(remedio: str, quantidade: float, modo: Literal["somar", "substituir"] = "somar") -> str:
        """Registra a quantidade (em comprimidos ou unidades) de um remédio: somar = comprou mais; substituir = tem exatamente isso."""
        item = ctx.achar_item(remedio)
        if not item:
            return "Remédio não encontrado na lista."
        atual = 0.0
        if modo == "somar":
            for e in calc_estoque.calcular([item], repo.obter_cronograma(ctx.idoso_id),
                                           repo.obter_doses(ctx.idoso_id, ctx.agora - timedelta(days=90)),
                                           repo.obter_estoque(ctx.idoso_id), ctx.agora):
                atual = e.estoque_estimado
        repo.registrar_estoque(item.item_id, atual + quantidade, ctx.agora, "falado")
        texto = frases.ESTOQUE_REGISTRADO.format(quantidade=f"{atual + quantidade:g} unidades", nome=item.nome_lido)
        if not item.unidades_por_dose:
            texto += " Ainda não sei quantos comprimidos ela toma de cada vez: pergunte, conforme a receita."
        return texto

    return {f.__name__: f for f in [
        consultar_lista, consultar_doses, registrar_dose, alterar_cronograma, pedir_foto, normalizar,
        checar_lista, info_remedio, consultar_consultas, registrar_consulta, consultar_estoque, registrar_estoque,
    ]}


FERRAMENTAS_POR_AGENTE = {
    "rotina": ["consultar_lista", "consultar_doses", "registrar_dose", "alterar_cronograma", "pedir_foto"],
    "explicador": ["consultar_lista", "checar_lista", "normalizar", "info_remedio"],
    "agenda": ["consultar_consultas", "registrar_consulta"],
    "farmacia": ["consultar_lista", "consultar_estoque", "registrar_estoque", "info_remedio"],
}


def gancho_limite(estado: EstadoMensagem):
    """Hook de ferramenta do Agno: conta as chamadas somando todos os agentes (D21)."""
    def gancho(function_name: str, function_call: Callable, arguments: dict):
        estado.chamadas_ferramenta += 1
        if estado.chamadas_ferramenta > CONFIG.limite_ferramentas:
            estado.passo("ferramenta", f"limite atingido: {function_name}")
            return "Limite de ferramentas atingido. Responda agora, sem ferramentas."
        try:
            resultado = function_call(**arguments)
        except Exception as erro:  # argumento inválido conta como chamada e volta como erro
            resultado = f"Erro na ferramenta: {erro}"
        estado.passo("ferramenta", f"{function_name}({arguments}) -> {str(resultado)[:120]}")
        return resultado
    return gancho
