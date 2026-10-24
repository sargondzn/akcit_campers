"""Conversa com a Seri no terminal, com a OpenAI de verdade e o RepositorioEmMemoria.

Serve para testar o harness inteiro antes de a API de A estar plugada. Nada é gravado em banco.

    .\\venv\\Scripts\\python.exe -m harness.demo            # começa vazio
    .\\venv\\Scripts\\python.exe -m harness.demo --exemplo  # lista, consulta amanhã e estoque já cadastrados

Comandos: texto livre · /foto <caminho> · /pdf <caminho> · /audio <caminho> · /b <n> (aperta o botão n)
          /corrigir <n> <texto> · /evento diario|vespera|pos · /lista · /passos · /sair
"""

from __future__ import annotations

import shlex
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

from harness.config import CONFIG
from harness.contratos import Acao, Anexo, EventoAgendado, ItemLido, MensagemEntrada, RespostaHarness
from harness.nucleo import processar_evento, processar_mensagem
from harness.testes.repositorio_memoria import RepositorioEmMemoria

CONTA, IDOSO = "conta-demo", "idoso-demo"
MIMES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".pdf": "application/pdf",
         ".webm": "audio/webm", ".m4a": "audio/mp4", ".mp4": "audio/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav"}


def exemplo(repo: RepositorioEmMemoria) -> None:
    itens = [
        ItemLido(item_id="los", nome_lido="Losartana 50 mg", principio_ativo=["losartana"], concentracao="50 mg",
                 posologia_texto="1 cp de 12/12h", horarios=["08:00", "20:00"], status="confirmado", confianca=1,
                 prescritor="cardiologista", data_receita=date.today() - timedelta(days=173), unidades_por_dose=1),
        ItemLido(item_id="sin", nome_lido="Sinvastatina 20 mg", principio_ativo=["sinvastatina"], concentracao="20 mg",
                 posologia_texto="1 cp à noite", horarios=["21:00"], status="confirmado", prescritor="cardiologista", confianca=1,
                 unidades_por_dose=1),
        ItemLido(item_id="met", nome_lido="Glifage 850 mg", principio_ativo=["metformina"], concentracao="850 mg",
                 posologia_texto="1 cp no almoço", horarios=["12:00"], status="confirmado", confianca=1,
                 prescritor="endocrinologista", unidades_por_dose=1),
    ]
    repo.salvar_lista_confirmada(IDOSO, itens)
    agora = datetime.now()
    repo.registrar_estoque("los", 14, agora, "falado")        # 7 dias de losartana: dispara o aviso
    repo.salvar_consulta(IDOSO, (agora + timedelta(days=1)).replace(hour=14, minute=0), "cardiologista", None)
    repo.registrar_mensagem("seri", "Oi! Eu sou a Seri.")


class Demo:
    def __init__(self, repo: RepositorioEmMemoria):
        self.repo = repo
        self.botoes = []
        self.ultima_lista = []

    def mostrar(self, resposta: RespostaHarness) -> None:
        # os botões continuam numerados entre as respostas, como os cartões que ficam na conversa
        for m in resposta.mensagens:
            print(f"\n  Seri [{m.tipo}]: {m.texto}")
            self.repo.registrar_mensagem("seri", m.texto)
            if m.itens:
                self.ultima_lista = m.itens
                mud = {x.item_anterior_id or x.item_novo_id: x for x in (m.mudancas or [])}
                usos = {i.principio_ativo: i.para_que_serve for i in (m.info or [])}
                for n, i in enumerate(m.itens, 1):
                    tag = mud.get(i.item_id)
                    tag = f" [{tag.tipo}{' ' + ','.join(tag.o_que_mudou) if tag and tag.o_que_mudou else ''}]" if tag else ""
                    uso = next((u for p, u in usos.items() if p in i.principio_ativo), "")
                    print(f"     {n}. {i.nome_lido} — {i.concentracao or '?'} — {i.posologia_texto or ''} "
                          f"{i.horarios} conf. {i.confianca:.2f} {i.status}{tag}" + (f"\n        para: {uso}" if uso else ""))
            if m.audio:
                print(f"     ♪ áudio: {m.audio.caminho}")
            if m.resumo_id:
                arquivo = CONFIG.caminho_armazenamento / "resumos_demo" / f"{m.resumo_id}.json"
                print(f"     📄 resumo: {arquivo}")
            for b in m.botoes:
                self.botoes.append(b)
                print(f"     [{len(self.botoes)}] {b.rotulo}" + (f"  (abre {b.abre})" if b.abre and not b.acao else ""))
        print(f"  (estado: {resposta.estado})")

    def enviar(self, **kw) -> None:
        entrada = MensagemEntrada(mensagem_id=uuid.uuid4().hex, conta_id=CONTA, idoso_id=IDOSO,
                                  recebida_em=datetime.now(), **kw)
        if entrada.texto:
            self.repo.registrar_mensagem("cuidadora", entrada.texto)
        print("  …a Seri está pensando")
        self.mostrar(processar_mensagem(entrada, self.repo))

    def anexo(self, caminho: str) -> Anexo:
        p = Path(caminho.strip('"'))
        if not p.exists():
            raise FileNotFoundError(p)
        return Anexo(caminho=str(p), mime=MIMES.get(p.suffix.lower(), "application/octet-stream"),
                     tamanho_bytes=p.stat().st_size)

    def comando(self, linha: str) -> bool:
        if not linha.startswith("/"):
            self.enviar(tipo="texto", texto=linha)
            return True
        partes = shlex.split(linha, posix=False)
        cmd, args = partes[0], partes[1:]
        if cmd == "/sair":
            return False
        if cmd in ("/foto", "/pdf", "/audio"):
            self.enviar(tipo=cmd[1:], anexo=self.anexo(" ".join(args)))
        elif cmd == "/b":
            botao = self.botoes[int(args[0]) - 1]
            if not botao.acao:
                print(f"  (este botão abre {botao.abre} no app; use /foto, /audio ou digite)")
            else:
                self.enviar(tipo="acao", acao=botao.acao)
        elif cmd == "/corrigir":
            item = self.ultima_lista[int(args[0]) - 1]
            pend = next(p for p in self.repo.obter_pendencias(CONTA) if p.tipo == "lista_para_confirmar")
            self.enviar(tipo="acao", acao=Acao(tipo="corrigir_item", pendencia_id=pend.pendencia_id,
                                               dados={"item_id": item.item_id, "texto": " ".join(args[1:])}))
        elif cmd == "/evento":
            tipo = {"diario": "verificacao_diaria", "vespera": "vespera_consulta", "pos": "pos_consulta"}[args[0]]
            consulta = next(iter(self.repo.obter_consultas(IDOSO, datetime.now() - timedelta(days=2))), None)
            evento = EventoAgendado(tipo=tipo, conta_id=CONTA, idoso_id=IDOSO, disparado_em=datetime.now(),
                                    consulta_id=consulta.consulta_id if consulta else None)
            resposta = processar_evento(evento, self.repo)
            self.mostrar(resposta) if resposta.mensagens else print("  (nenhuma mensagem para este evento)")
        elif cmd == "/lista":
            lista = self.repo.obter_lista_atual(IDOSO)
            print(f"  versão {lista.versao if lista else '-'}: " + ", ".join(
                f"{i.nome_lido} ({i.status})" for i in (lista.itens if lista else [])))
        elif cmd == "/passos":
            for p in self.repo.passos[-15:]:
                print(f"  {p['tipo']:<16} {p['agente'] or '':<14} {p['duracao_ms'] or '':>6} {p['conteudo'][:90]}")
        else:
            print(__doc__)
        return True


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    repo = RepositorioEmMemoria(pasta_resumos=CONFIG.caminho_armazenamento / "resumos_demo")
    if "--exemplo" in sys.argv:
        exemplo(repo)
        print("Exemplo carregado: 3 remédios, consulta amanhã às 14h e estoque de 7 dias de losartana.")
    print(__doc__)
    demo = Demo(repo)
    while True:
        try:
            linha = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not linha:
            continue
        try:
            if not demo.comando(linha):
                break
        except Exception as erro:
            print(f"  (erro: {type(erro).__name__}: {erro})")


if __name__ == "__main__":
    main()
