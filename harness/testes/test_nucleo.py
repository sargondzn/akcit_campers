from datetime import datetime, timedelta
from pathlib import Path

import pytest

from harness import nucleo
from harness.agentes import ResultadoConversa
from harness.agentes.esquemas import ItensInterpretados, RelatoConsulta, SaidaDiario
from harness.contratos import Acao, Anexo, EventoAgendado, MensagemEntrada
from harness.guardrails import frases
from harness.testes.agentes_falsos import AgentesFalsos, item
from harness.testes.repositorio_memoria import RepositorioEmMemoria


@pytest.fixture(autouse=True)
def sem_fala(monkeypatch):
    monkeypatch.setattr(nucleo.tts, "falar", lambda texto: (_ for _ in ()).throw(RuntimeError("sem voz no teste")))


def msg(tipo="texto", texto=None, **kw):
    return MensagemEntrada(mensagem_id="m", conta_id="c", idoso_id="i", tipo=tipo, texto=texto,
                           recebida_em=datetime.now(), **kw)


def acao(tipo, pid, **dados):
    return msg("acao", acao=Acao(tipo=tipo, pendencia_id=pid, dados=dados))


def foto(tmp_path: Path) -> Anexo:
    caminho = tmp_path / "receita.jpg"
    caminho.write_bytes(b"x")
    return Anexo(caminho=str(caminho), mime="image/jpeg")


def receita(*itens, prescritor="cardiologista", tipo="receita_impressa"):
    return ItensInterpretados(tipo_documento=tipo, prescritor=prescritor, data_receita="2026-10-20", itens=list(itens))


@pytest.mark.parametrize("texto", ["ela caiu e bateu a cabeça", "está com dor no peito", "falta de ar forte",
                                   "ficou confusa de repente"])
def test_alarme_vai_ao_192_sem_nenhum_agente(texto):
    repo, ag = RepositorioEmMemoria(), AgentesFalsos()
    r = nucleo.processar_mensagem(msg(texto=texto), repo, ag)
    assert r.mensagens[0].tipo == "ligue_192" and ag.chamadas == [] and len(repo.diario) == 1


def test_fluxo_completo_leitura_conciliacao_e_confirmacao(tmp_path):
    repo = RepositorioEmMemoria()
    ag = AgentesFalsos(interpretacoes=[
        receita(item("Losartana", "50 mg"), item("Sinvastatina", "20 mg", horarios=("21:00",))),
        receita(item("Losartana", "100 mg"), item("Anlodipino", "5 mg")),
    ])
    # 1ª receita: sem lista, vai direto à proposta
    r = nucleo.processar_mensagem(msg("foto", anexo=foto(tmp_path)), repo, ag)
    proposta = r.mensagens[0]
    assert proposta.tipo == "lista_para_confirmar" and r.estado == "aguardando_confirmacao"
    assert proposta.info and "pressão" in proposta.info[0].para_que_serve       # E8
    pid = proposta.botoes[0].acao.pendencia_id
    r = nucleo.processar_mensagem(acao("confirmar_pendencia", pid), repo, ag)
    assert repo.versoes[-1].versao == 1 and len(repo.horarios) == 3

    # 2ª receita: pergunta o escopo, depois concilia
    r = nucleo.processar_mensagem(msg("foto", anexo=foto(tmp_path)), repo, ag)
    escopo = r.mensagens[0]
    assert [b.acao.dados["escopo"] for b in escopo.botoes][0] == "medico"
    r = nucleo.processar_mensagem(acao("definir_escopo", escopo.botoes[1].acao.pendencia_id, escopo="toda_lista"), repo, ag)
    tipos = {m.tipo for m in r.mensagens[0].mudancas}
    assert tipos == {"alterado", "novo", "ausente"}
    ausente = next(m for m in r.mensagens if m.botoes and m.botoes[0].acao and m.botoes[0].acao.tipo == "decidir_item")
    nucleo.processar_mensagem(msg("acao", acao=ausente.botoes[2].acao), repo, ag)           # "Não sei"
    nucleo.processar_mensagem(acao("confirmar_pendencia", r.mensagens[0].botoes[0].acao.pendencia_id), repo, ag)
    v2 = repo.versoes[-1]
    assert v2.versao == 2 and v2.pontos_para_conferir and "Sinvastatina" in v2.pontos_para_conferir[0]
    assert next(i for i in v2.itens if i.principio_ativo == ["losartana"]).concentracao == "100 mg"

    # clique duplo: pendência já resolvida
    r = nucleo.processar_mensagem(acao("confirmar_pendencia", pid), repo, ag)
    assert r.mensagens[0].texto == frases.JA_RESOLVIDO


def test_confianca_baixa_pede_nova_foto(tmp_path):
    repo = RepositorioEmMemoria()
    ag = AgentesFalsos(interpretacoes=[receita(item("Remedio estranho", None, confianca=0.9))])
    r = nucleo.processar_mensagem(msg("foto", anexo=foto(tmp_path)), repo, ag)
    assert r.mensagens[-1].tipo == "pedido_de_foto"
    assert r.mensagens[0].itens[0].status == "nao_confirmado"


def test_diario_pergunta_e_escala(tmp_path):
    repo = RepositorioEmMemoria()
    ag = AgentesFalsos(
        conversa=ResultadoConversa(texto="", membro="diario",
                                   diario=SaidaDiario(descricao="Tontura", sintomas=["tontura"], inicio=None,
                                                      intensidade=None, sinais=[], pergunta="Desde quando?")),
        diario=[SaidaDiario(descricao="Tontura e febre desde ontem", sintomas=["tontura", "febre"], inicio="ontem",
                            intensidade="moderada", sinais=[], pergunta=None)])
    r = nucleo.processar_mensagem(msg(texto="ela está tonta"), repo, ag)
    assert r.mensagens[0].texto == "Desde quando?"
    r = nucleo.processar_mensagem(msg(texto="desde ontem, e com febre"), repo, ag)
    assert r.mensagens[0].texto == frases.CONDUTA_24H and r.mensagens[1].tipo == "resumo"


def test_consulta_preparo_e_relato():
    repo = RepositorioEmMemoria()
    ag = AgentesFalsos(relato=RelatoConsulta(orientacoes=["voltar em 3 meses"], exames_pedidos=["hemograma"],
                                             retorno_em="em 3 meses", mudancas_citadas=["losartana"]))
    from harness.contratos import ItemLido
    repo.salvar_lista_confirmada("i", [ItemLido(item_id="a", nome_lido="Losartana 50 mg", principio_ativo=["losartana"],
                                                concentracao="50 mg", horarios=["08:00"], status="confirmado")],
                                 ["Sinvastatina 20 mg não veio na receita nova: confirmar se continua"])
    amanha = datetime.now() + timedelta(days=1)
    cid = repo.salvar_consulta("i", amanha, "cardiologista", None)
    evento = EventoAgendado(tipo="vespera_consulta", conta_id="c", idoso_id="i", consulta_id=cid, disparado_em=datetime.now())
    r = nucleo.processar_evento(evento, repo, ag)
    assert r.mensagens[0].tipo == "consulta_preparada"
    resumo = repo.resumos[r.mensagens[0].resumo_id]
    assert resumo.tipo == "preparo_consulta" and "Pergunta inventada" not in resumo.perguntas_para_profissional
    assert any("Sinvastatina" in p for p in resumo.perguntas_para_profissional)

    pos = EventoAgendado(tipo="pos_consulta", conta_id="c", idoso_id="i", consulta_id=cid, disparado_em=datetime.now())
    nucleo.processar_evento(pos, repo, ag)
    r = nucleo.processar_mensagem(msg(texto="o médico pediu hemograma e mudou a losartana"), repo, ag)
    assert frases.RELATO_RECEITA in [m.texto for m in r.mensagens] and repo.consultas[cid].relato
    assert len(repo.versoes) == 1       # relato falado não muda a lista


def test_auditor_bloqueia_resposta_da_equipe():
    repo = RepositorioEmMemoria()
    ag = AgentesFalsos(conversa=ResultadoConversa(texto="Pode dar dois comprimidos hoje.", membro="rotina"))
    r = nucleo.processar_mensagem(msg(texto="posso dar dois?"), repo, ag)
    assert r.mensagens[0].texto == frases.BLOQUEIO
