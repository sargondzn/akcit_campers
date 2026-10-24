# Spec — 00-projeto

> **Status:** 🟡 escrita em 23/10/2026 a partir das respostas da [`discussao.md`](discussao.md) (D0–D22); atualizada em 24/10/2026 a pedido do usuário: harness multiagente em Agno (D5), **modelos da OpenAI** no lugar dos locais (D3) e as funcionalidades **E1, E2, E4 e E8** (D23), com os contratos novos ou ampliados marcados com **(24/10)**. Aguarda a aprovação dos três (A, B e C).
> **Vale para todas as frentes.** Em caso de conflito, esta spec prevalece sobre a spec de uma frente. Os contratos (§5) só mudam com o acordo dos três; o escopo só muda com pedido do usuário (registrado em [`visao.md`](visao.md) §5).

---

## 1. Produto

| Item | Decisão | Fonte |
|---|---|---|
| Nome do produto | **Seriema** (disponibilidade do nome a checar, frente `negocio`) | D15.1 |
| Nome do agente na interface | **Seri** | D15.1 |
| Fonte do escopo | O plano (`docs/f3_plano_startup_v1.md`) prevalece sobre o escopo original, respeitadas as mudanças da visão §5 | D0 |
| Corte regional × final | [`escopo-por-fase.md`](escopo-por-fase.md) | D16 |
| Trilha | **Goiânia**, regional em **24/10/2026**; final em **28/11/2026** | D11 |
| Contas | Uma conta = uma cuidadora = **um idoso** no MVP; login por **e-mail + senha** | D17 |
| Interface | **Conversa como tela principal** + telas de apoio (remédios, rotina, diário) | D17 |
| Alerta clínico | A Seri **menciona a possível interação** à cuidadora, sempre com fonte e terminando em "leve ao farmacêutico ou médico" | D15.2 |
| Destino do resumo | PDF para a cuidadora **+ link de acesso sem conta** para o profissional | D9 |
| Primeiro pagador (tese) | Operadora | D15.3 |
| Conferência clínica | **No regional, feita com LLM** (tabela curada, pares, relatos, para que serve e Farmácia Popular). Na final, por profissional, se necessário | D7.2, D15.4 |
| Funcionalidades além da rotina (24/10) | **E8** para que serve cada remédio · **E1** conciliação a cada receita nova · **E2** preparo da consulta e registro do que o médico disse · **E4** estoque, validade da receita e Farmácia Popular. Todas no regional | D23 |

---

## 2. Stack

| Camada | Decisão | Fonte |
|---|---|---|
| Plataforma | **PWA instalável já no regional**, mobile-first. React + Vite + `vite-plugin-pwa`, Tailwind + shadcn/ui | D1, D16.1, D18, D20 |
| API | **Python 3.12 + FastAPI** + Pydantic | D2 |
| Banco e arquivos | **SQLite** (via SQLAlchemy, para migrar para PostgreSQL na final) + arquivos em disco + **APScheduler** | D6 |
| Harness agêntico | **Sistema multiagente com o framework Agno** (Python): uma coordenadora (a Seri) encaminha a subagentes especializados (Leitor, Intérprete, Rotina, Explicador, Diário, Agenda, Preparador, Farmácia), e as tarefas de sequência conhecida rodam como fluxos fixos. Substitui o loop próprio e a migração para LangGraph | D5 (atualizada em 24/10) |
| Modelos de linguagem e visão | **API da OpenAI**, com a chave do time (`OPENAI_API_KEY`). Os modelos exatos saem do teste de bancada da frente `harness` (ponto de partida: `gpt-6-luna`). Substitui os modelos open-source locais | D3 (atualizada em 24/10) |
| Voz | **Local:** faster-whisper (STT) e Piper (TTS), com ffmpeg para converter os formatos de áudio | D4 |
| Notificação | Web Push com chaves VAPID geradas por nós (P1) | D1 |
| Ambiente local | **Docker Compose** | D8 |
| Produção | **Frontend na Netlify**; API + harness + dados + voz + banco **numa máquina do time**, em Docker, exposta por **Cloudflare Tunnel** (HTTPS). Os modelos de linguagem rodam na OpenAI | D8, D22 |
| Idioma | **Português** no código, nos comentários e nos nomes | D12.4 |

Versões: Python 3.12; as demais bibliotecas na versão estável do dia em que forem instaladas, **fixadas no arquivo de dependências** (`pyproject.toml`/lockfile e `package-lock.json`).

Na final, conforme as respostas: PostgreSQL + armazenamento de objetos + fila (D6). A criação dos modelos fica isolada no harness (`harness/agentes/modelos.py`): trocar de modelo ou de provedor é mudar só ali.

---

## 3. Arquitetura e implantação

```
 Celular da cuidadora (Android / iPhone)
        │  HTTPS
        ▼
 Netlify ── PWA (React) ──────────────┐
                                      │ HTTPS + token Bearer
                                      ▼
 Máquina do time ── Cloudflare Tunnel ── Docker Compose
                                      ├─ api       (FastAPI + harness em Agno + dados, um processo Python)
                                      │    ├─ SQLite + arquivos  (volume)
                                      │    ├─ faster-whisper, Piper, ffmpeg (voz local)
                                      │    ├─ fila de mensagens  (um item por vez)
                                      │    └─ agendador (lembretes, verificação diária, consultas)
                                      └─ tunel     (cloudflared)

 api ── HTTPS + OPENAI_API_KEY ──► API da OpenAI (modelos de visão e de conversa)
```

Consequências que todas as frentes precisam respeitar:

1. **A máquina de produção fica ligada** durante a avaliação da banca e a demo. Qual máquina e quem cuida dela: BE-D3 em [`backend/discussao.md`](../backend/discussao.md).
2. **Processamento assíncrono.** O túnel da Cloudflare corta requisições que passam de ~100 s, e uma foto passa por vários subagentes (e pela transcrição local, no caso do áudio). Por isso, nenhuma requisição espera o harness: a API recebe a mensagem, responde na hora com `202` e o frontend consulta a resposta (§6).
3. **Domínios diferentes** (Netlify × túnel): autenticação por **token Bearer no cabeçalho**, não por cookie (o Safari bloqueia cookie entre sites). A API libera CORS só para o domínio da Netlify e para `localhost`.
4. **URL da API no frontend** vem da variável `VITE_API_URL`. Se o túnel tiver URL aleatória, a variável é atualizada e o frontend republicado antes da apresentação (BE-D2).
5. **Depende de internet e da OpenAI:** a imagem é reduzida no celular (menos tempo e menos custo), a conversa mostra "a Seri está lendo a receita…", a conta da OpenAI tem crédito e limite de gasto conferidos antes da demo, e o **vídeo de backup da demo** é obrigatório.
6. **Privacidade (24/10):** foto, texto da receita, transcrição do áudio e o contexto da conversa **vão para a OpenAI**. O áudio em si fica na máquina (a voz é local). O termo de consentimento diz isso, o contexto leva só o apelido do idoso, e a política de uso e retenção de dados da API da OpenAI é conferida e citada no termo (§7.3).

---

## 4. Estrutura do repositório

```
plataforma/frontend/   ← A  (React, PWA, configuração da Netlify)
plataforma/api/        ← A  (FastAPI, banco, arquivos, agendador, PDF, implementação do C6)
harness/               ← B  (harness agêntico)
dados/                 ← C  (ferramentas de dados e tabelas)
avaliacao/             ← C  (executor, formatos de gabarito, relatórios agregados)
negocio/               ← C  (BMC, pitch, relatórios quinzenais, síntese das entrevistas)
contratos/             ← todos, só com acordo (tipos e interfaces do §5)
infra/                 ← A  (Docker Compose, Dockerfile, túnel, .env.exemplo)
pyproject.toml         ← A cria; cada dono acrescenta as próprias dependências
```

Regras:

- **Ninguém edita a pasta do outro.** Precisa de algo? Pede ao dono ou propõe mudança de contrato.
- Todo o código Python (`plataforma/api`, `harness`, `dados`, `avaliacao`, `contratos`) é **um só projeto Python**, importado no mesmo processo. Assim, os contratos são chamadas de função, não HTTP.
- **Fora do Git** (D14): fotos, receitas, áudios, PDFs reais, banco, `.env` e entrevistas brutas. O `.gitignore` precisa cobrir pelo menos `.env`, `*.sqlite*`, `armazenamento/`, `**/dados_privados/` e `dados/brutos/` (tarefa de A no esqueleto).
- A documentação de apoio em `docs/` está fora do repositório (D13); quem precisar pede ao administrador do repositório.

---

## 5. Contratos

Os tipos ficam em `contratos/` (Pydantic). A notação abaixo é a referência; os nomes finais no código seguem esta spec. Datas e horas em ISO 8601; horários do cronograma no fuso **America/Sao_Paulo**.

### 5.1 Tipos compartilhados

```python
class Anexo:
    caminho: str            # caminho no armazenamento da API; o harness só lê
    mime: str               # image/jpeg, image/png, application/pdf, audio/webm, audio/mp4, audio/mpeg, audio/wav
    tamanho_bytes: int

class ItemLido:             # um remédio lido ou proposto
    item_id: str
    nome_lido: str                      # como está escrito na receita ou na caixa
    principio_ativo: list[str]          # após normalizar; vazio se não encontrado; mais de um = associação
    concentracao: str | None            # "50 mg"
    forma: str | None                   # "comprimido"
    posologia_texto: str | None         # como está escrito ("1 cp de 12/12h")
    horarios: list[str]                 # ["08:00", "20:00"]; vazio se não der para inferir
    origem: Literal["receita_foto", "caixa_foto", "receita_pdf", "digitado", "falado"]
    confianca: float                    # 0 a 1
    status: Literal["proposto", "nao_confirmado", "ilegivel", "confirmado", "retirado"]   # retirado (24/10): "o médico tirou" na conciliação
    # (24/10) campos para E1, E4 e E8; todos opcionais
    prescritor: str | None              # especialidade ou nome curto do médico, como na receita
    data_receita: date | None
    indicacao_na_receita: str | None    # só se estiver escrita ("para pressão")
    unidades_por_dose: float | None     # "1 cp" → 1; "meio comprimido" → 0.5
    quantidade_embalagem: int | None    # caixa: "30 comprimidos" → 30

class Mudanca:                          # (24/10) E1 — resultado da conciliação
    tipo: Literal["novo", "mantido", "alterado", "ausente"]
    item_novo_id: str | None
    item_anterior_id: str | None
    o_que_mudou: list[str]              # em alterado: ["concentracao", "horarios", "unidades_por_dose"]
    nome_diferente: bool                # mesmo princípio com outro nome comercial
    decisao: Literal["continua", "medico_tirou", "nao_sei"] | None   # só em ausente

class InfoRemedio:                      # (24/10) E8 e E4 — vem do C8
    principio_ativo: str
    para_que_serve: str                 # frase simples de uso comum: "controlar a pressão alta"
    farmacia_popular: bool
    farmacia_popular_detalhe: str | None        # indicação do programa, se houver
    documentos_farmacia_popular: list[str]      # ["a receita", "um documento com foto", "o CPF"]
    tipo_receita: Literal["simples", "controle_especial", "antimicrobiano"] | None
    validade_receita_dias: int | None
    fonte: str
    conferencia: Literal["llm", "profissional"]

class Alerta:
    tipo: Literal["interacao", "duplicidade_principio", "duplicidade_classe", "cbmpi"]
    item_ids: list[str]
    principios: list[str]
    gravidade: Literal["alta", "moderada", "baixa"] | None
    descricao: str                      # frase simples, em português
    fonte: str                          # referência indicada na tabela
    conferencia: Literal["llm", "profissional"]

class SintomaEstruturado:
    descricao: str                      # o que a cuidadora disse (transcrição)
    sintomas: list[str]                 # termos normalizados: "queda", "tontura"...
    inicio: str | None                  # "hoje de manhã", "há 3 dias"
    intensidade: Literal["leve", "moderada", "forte"] | None
    sinais: dict[str, bool]             # ex.: {"bateu_a_cabeca": True}

class Conduta:
    nivel: Literal["ligue_192", "atendimento_24h", "observar"]
    regra_id: str
    motivo: str
    fonte: str
```

### C1 — Plataforma → harness (A chama, B implementa)

```python
class Acao:
    tipo: Literal["confirmar_pendencia", "recusar_pendencia", "corrigir_item",
                  "definir_escopo", "decidir_item", "contar_estoque"]       # os 3 últimos: (24/10)
    pendencia_id: str
    dados: dict                         # corrigir_item: {"item_id", "texto"}
                                        # definir_escopo: {"escopo": "toda_lista" | "medico" | "acrescimo"}
                                        # decidir_item: {"item_anterior_id", "decisao": "continua" | "medico_tirou" | "nao_sei"}
                                        # contar_estoque: {"item_id", "quantidade"}

class MensagemEntrada:
    mensagem_id: str                    # UUID gerado no celular (idempotência)
    conta_id: str
    idoso_id: str
    tipo: Literal["texto", "foto", "pdf", "audio", "acao"]
    texto: str | None
    anexo: Anexo | None                 # áudio em WebM/Opus (Chrome) ou MP4/AAC (Safari): os dois são aceitos
    acao: Acao | None
    recebida_em: datetime

class Botao:
    rotulo: str                         # "Confirmo a lista"
    acao: Acao | None                   # None = botão do próprio app (ex.: abrir câmera)
    abre: Literal["camera", "galeria", "pdf", "gravar", "teclado", "tel:192"] | None

class MensagemSaida:
    tipo: Literal["texto", "lista_para_confirmar", "alertas", "pedido_de_foto", "ligue_192", "resumo",
                  "consulta_preparada", "aviso_estoque"]                    # os 2 últimos: (24/10)
    texto: str                          # sempre presente; é o que o Auditor verifica
    audio: Anexo | None                 # fala da Seri, quando houver
    itens: list[ItemLido] | None        # em lista_para_confirmar
    mudancas: list[Mudanca] | None      # (24/10) em lista_para_confirmar, quando houve conciliação (E1)
    info: list[InfoRemedio] | None      # (24/10) "para que serve" de cada item (E8)
    alertas: list[Alerta] | None        # em alertas e lista_para_confirmar
    resumo_id: str | None               # em resumo e consulta_preparada
    botoes: list[Botao]

class EventoAgendado:                   # (24/10) disparado pelo agendador de A (E2, E4)
    tipo: Literal["verificacao_diaria", "vespera_consulta", "pos_consulta"]
    conta_id: str
    idoso_id: str
    consulta_id: str | None             # nos eventos de consulta
    disparado_em: datetime

class RespostaHarness:
    mensagens: list[MensagemSaida]
    estado: Literal["ok", "aguardando_confirmacao", "erro"]

def processar_mensagem(entrada: MensagemEntrada, repo: Repositorio) -> RespostaHarness: ...
def processar_evento(evento: EventoAgendado, repo: Repositorio) -> RespostaHarness: ...   # (24/10)
def falar(texto: str) -> Anexo: ...     # TTS do lembrete; áudio em MP3 (toca no Android e no iPhone)
```

### C2 — Harness → dados: normalização (B chama, C implementa)

```python
class ResultadoNormalizacao:
    entrada: str
    encontrado: bool
    principio_ativo: list[str]          # minúsculo, sem acento; mais de um = associação
    concentracao: str | None
    nome_comercial: str | None
    candidatos: list[str]               # quando há ambiguidade
    fonte: str                          # "CMED <data do arquivo>"

def normalizar(nome: str) -> ResultadoNormalizacao: ...
```

### C3 — Harness → dados: checagem da lista (B chama, C implementa)

```python
class ItemParaChecar:
    item_id: str
    principio_ativo: list[str]

def checar_lista(itens: list[ItemParaChecar]) -> list[Alerta]: ...   # ordenado por gravidade
```

### C4 — Harness → dados: alarme e gravidade (B chama, C implementa)

```python
def detectar_alarme(texto: str) -> Conduta | None: ...   # regra fixa, roda ANTES do modelo
def avaliar_gravidade(sintoma: SintomaEstruturado) -> Conduta: ...
```

### C5 — Harness → plataforma: resumo (B monta, A gera o PDF e o link)

```python
class Resumo:
    resumo_id: str
    tipo: Literal["escalonamento", "preparo_consulta"]   # (24/10) preparo_consulta = E2
    idoso_apelido: str
    periodo_inicio: date
    periodo_fim: date
    motivo: str                         # por que foi gerado (a conduta)
    lista_atual: list[ItemLido]
    doses_perdidas: list[dict]          # {"item_id", "nome", "horario_previsto"}
    sintomas: list[dict]                # SintomaEstruturado + "registrado_em" + conduta
    alertas: list[Alerta]
    perguntas_para_profissional: list[str]
    info: list[InfoRemedio]             # (24/10) para que serve cada remédio da lista (E8)
    consulta: dict | None               # (24/10) em preparo_consulta: {"data_hora", "profissional", "local"}
    mudancas_recentes: list[dict]       # (24/10) mudanças na lista no período: {"data", "nome", "tipo", "o_que_mudou"}
    pontos_para_conferir: list[str]     # (24/10) itens "não sei", não confirmados, receitas vencendo, estoque baixo
    aviso: str                          # texto fixo: "Gerado a partir dos relatos da cuidadora. Não é diagnóstico."
    gerado_em: datetime
```

### C6 — Plataforma → harness: memória e ações (A implementa, B usa)

```python
class Repositorio(Protocol):
    # leitura (Contexto)
    def obter_idoso(self, idoso_id) -> dict: ...                     # apelido
    def obter_lista_atual(self, idoso_id) -> ListaVersao: ...        # versao, confirmada_em, itens: list[ItemLido], pontos_para_conferir (24/10)
    def obter_cronograma(self, idoso_id) -> list[Horario]: ...       # item_id, horario, ativo
    def obter_doses(self, idoso_id, desde) -> list[Dose]: ...        # horario_id, previsto, status: tomada|nao_tomada|sem_resposta
    def obter_diario(self, idoso_id, desde) -> list[RegistroDiario]: ...
    def obter_historico(self, conta_id, limite=20) -> list[MensagemDaConversa]: ...
    def obter_pendencias(self, conta_id) -> list[Pendencia]: ...     # pendencia_id, tipo, dados, criada_em
    def obter_versoes_lista(self, idoso_id, desde) -> list[ListaVersao]: ...   # (24/10) E1 e E2
    def obter_consultas(self, idoso_id, desde) -> list[Consulta]: ...         # (24/10) consulta_id, data_hora, profissional, local, relato
    def obter_estoque(self, idoso_id) -> list[RegistroEstoque]: ...           # (24/10) último registro por item: item_id, quantidade, registrado_em

    # escrita (ferramentas)
    def criar_pendencia(self, conta_id, tipo, dados) -> str: ...     # tipos: lista_para_confirmar, mudanca_cronograma, diario_aberto, leitura_baixa_confianca
                                                                     # (24/10) escopo_receita, consulta_para_confirmar, relato_consulta, quantidade_por_dose
    def atualizar_pendencia(self, pendencia_id, dados) -> None: ...  # (24/10) definir_escopo e decidir_item mudam a proposta guardada
    def resolver_pendencia(self, pendencia_id, resultado) -> None: ...
    def salvar_lista_confirmada(self, idoso_id, itens, pontos_para_conferir=None) -> int: ...   # cria nova versão e o cronograma; devolve a versão
                                                                     # (24/10) pontos_para_conferir: itens "não sei" da conciliação; voltam em ListaVersao
    def alterar_cronograma(self, idoso_id, mudancas) -> None: ...
    def registrar_dose(self, horario_id, status, quando) -> None: ...
    def registrar_sintoma(self, idoso_id, sintoma, conduta) -> str: ...
    def salvar_resumo(self, resumo: Resumo) -> dict: ...             # {"resumo_id", "url_pdf", "url_publica"}; o PDF muda pelo tipo
    def salvar_consulta(self, idoso_id, data_hora, profissional, local) -> str: ...   # (24/10) agenda os eventos da consulta
    def registrar_relato_consulta(self, consulta_id, relato: dict) -> None: ...       # (24/10)
    def registrar_estoque(self, item_id, quantidade, quando, origem) -> None: ...     # (24/10) origem: falado | caixa_foto
    def registrar_passo(self, passo: dict) -> None: ...              # registro de passos (P1)
```

B não mexe no schema do banco. Para trabalhar sem a API, B mantém um `RepositorioEmMemoria` que segue este protocolo (também usado pela avaliação).

### C7 — Avaliação → harness (C chama, B expõe)

```python
harness.processar_mensagem(entrada, repo)                         # o harness inteiro
harness.leitor.ler(anexo) -> list[ItemLido]                       # leitura isolada
harness.auditor.verificar(texto, contexto) -> ResultadoAuditor    # aprovado: bool, motivos: list[str], texto_final: str
harness.diario.estruturar(texto) -> SintomaEstruturado
harness.conciliacao.conciliar(lista_atual, itens_novos, escopo) -> list[Mudanca]   # (24/10) E1
```

### C8 — Harness e plataforma → dados: informação do remédio (B e A chamam, C implementa) (24/10)

```python
def info_remedio(principio_ativo: str) -> InfoRemedio | None: ...   # None = sem informação na tabela
```

Usado pelo harness (E8, E4, preparo da consulta) e pela API de A (tela Remédios). Determinístico, só tabela com fonte.

---

## 6. Fluxo de uma mensagem

1. O celular gera o `mensagem_id` (UUID) e envia `POST /mensagens`. A API grava a mensagem e o anexo e responde **`202`** com `{"mensagem_id", "status": "processando"}`. Se o mesmo `mensagem_id` chegar de novo (reenvio), a API devolve o estado atual sem duplicar.
2. A **fila** da API (um item por vez, em ordem de chegada) chama `processar_mensagem`.
3. As `MensagemSaida` viram mensagens da conversa no banco, e a mensagem de entrada fica `respondida` (ou `erro`).
4. Enquanto houver mensagem `processando`, o frontend consulta `GET /conversa?depois=<cursor>` a cada **2 s** e mostra "a Seri está…".
5. Se o harness passar de **5 min** ou falhar, a API grava a resposta fixa "Não consegui processar agora. Tente de novo em instantes." com estado `erro`.

---

## 7. Regras transversais

### 7.1 Guardrails (visão §2.3) — onde cada um mora

| Guardrail | Implementação | Dono |
|---|---|---|
| Nunca sugerir dose, troca ou suspensão | Auditor em toda `MensagemSaida` + instrução do sistema | B |
| Nada vira cronograma sem confirmação | Ferramentas com `exige_confirmacao` só criam pendência; só a ação `confirmar_pendencia` da cuidadora executa | B (fluxo) + A (botões) |
| Fato clínico só de ferramenta, com fonte | `Alerta`, `Conduta` e `InfoRemedio` sempre vêm de C2–C4 e C8; o Auditor bloqueia fato clínico (inclusive "para que serve") sem objeto de origem | B + C |
| Nunca sugerir tirar ou manter remédio na conciliação (E1) | Comparação determinística; a decisão "o médico tirou" é da cuidadora; "não sei" mantém o item e vira pergunta para a consulta | B |
| Sinal de alarme não passa pelo LLM | `detectar_alarme` antes do modelo → mensagem fixa `ligue_192` | C (regra) + B (posição no fluxo) |
| Na dúvida, chamar um humano | Fluxo de confiança baixa (D19) e "confirme com o farmacêutico" | B |
| LGPD | Consentimento antes de qualquer envio; dados mínimos; nada para a operadora | A |

### 7.2 Regras do harness (D21)

- Até **5 chamadas de ferramenta por mensagem**. No limite, o harness para e responde com o que tem.
- **Exigem confirmação da cuidadora:** `salvar_lista_confirmada`, qualquer mudança no cronograma e `registrar_consulta` (24/10). **Diretas:** `registrar_dose`, `registrar_sintoma` e `registrar_estoque` (24/10).
- **O modelo nunca decide sozinho:** o sinal de alarme (regra fixa → 192), os fatos clínicos (só vêm das ferramentas de C) e a liberação da saída (sempre passa pelo Auditor).
- **Registro de passos** (P1): cada observação, ferramenta chamada, resultado e bloqueio do Auditor fica guardado **só no servidor**.

### 7.3 LGPD e dados

- A tela de consentimento é a única forma de consentimento no regional (D14.3). Sem consentimento aceito, a API recusa os envios.
- (24/10) O termo informa que foto, texto da receita e transcrição do áudio são processados pela **OpenAI** (fora do Brasil), conforme a política de dados da API, e que o áudio fica na máquina do time.
- Perfil do idoso mínimo: **apelido**.
- Logs não guardam conteúdo de mensagem, receita ou sintoma, só ids, tempos e erros. O registro de passos (P1) é a exceção, fica no banco e nunca sai do servidor.
- O link público do resumo usa um token aleatório e expira (BE-D1).

### 7.4 Convenções

- Português em código, comentários e nomes (D12.4). Termos técnicos consagrados podem ficar em inglês (`token`, `endpoint`).
- Versionamento é do time: as mensagens seguem o padrão já usado no repositório (`tipo: descrição`).
- Cada contrato tem um **stub** com respostas fixas, para ninguém esperar ninguém: A mantém o stub do harness (C1), e B mantém os stubs das ferramentas de dados (C2–C4) e o `RepositorioEmMemoria` (C6).
- Mudou um contrato? Atualize esta spec **antes** do código, com o acordo dos três.

---

## 8. Definição de pronto do regional

A demo funciona **na URL da Netlify, em um Android e em um iPhone reais**, com o app instalado na tela inicial, seguindo o roteiro do plano:

1. Criar conta → aceitar o consentimento → informar o apelido do idoso.
2. **Foto da receita física** → a Seri propõe a lista, marcando o que precisa ser conferido.
3. A lista vem com **alerta de interação ou duplicidade**, com fonte e "leve ao farmacêutico ou médico".
4. A cuidadora **confirma** → o cronograma aparece em Remédios/Rotina.
5. **Lembrete disparado na hora**, com texto e áudio → "Tomei".
6. **Áudio** de sintoma → sinal de alarme vira o cartão "Ligue 192"; sintoma não urgente vira **resumo em PDF + link** para o profissional.
7. Uma tentativa de pedir dose é recusada pelo Auditor.
8. (24/10) **"Para que serve a losartana?"** → a Seri responde com a frase da tabela e a fonte (E8).
9. (24/10) **Foto de uma receita nova** → a Seri mostra o que entrou, o que mudou e o que não veio, e pergunta sobre o que não veio (E1).
10. (24/10) **Consulta marcada** → na véspera (disparada na hora pelo modo demo), chega a página "Para levar à consulta" com as perguntas (E2).
11. (24/10) **Aviso de estoque** ("a losartana deve acabar por volta de…") com a informação do Farmácia Popular (E4).

Mais o relatório da avaliação (frente `avaliacao`), o pitch e o vídeo de backup (frente `negocio`).
