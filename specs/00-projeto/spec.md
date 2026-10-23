# Spec — 00-projeto

> **Status:** 🟡 escrita em 23/10/2026 a partir das respostas da [`discussao.md`](discussao.md) (D0–D22). Aguarda a aprovação dos três (A, B e C).
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
| Conferência clínica | **No regional, feita com LLM** (tabela curada, pares e relatos). Na final, por profissional, se necessário | D7.2, D15.4 |

---

## 2. Stack

| Camada | Decisão | Fonte |
|---|---|---|
| Plataforma | **PWA instalável já no regional**, mobile-first. React + Vite + `vite-plugin-pwa`, Tailwind + shadcn/ui | D1, D16.1, D18, D20 |
| API | **Python 3.12 + FastAPI** + Pydantic | D2 |
| Banco e arquivos | **SQLite** (via SQLAlchemy, para migrar para PostgreSQL na final) + arquivos em disco + **APScheduler** | D6 |
| Loop do harness | **Loop próprio em Python com tool use** no regional; migração para **LangGraph** na final | D5 |
| Modelos de linguagem e visão | **Open-source, locais**, servidos pelo **Ollama** (API compatível com a da OpenAI), **rodando em CPU**. Os modelos exatos saem do teste de bancada da frente `harness` | D3, D22 |
| Voz | **Local:** faster-whisper (STT) e Piper (TTS), com ffmpeg para converter os formatos de áudio | D4 |
| Notificação | Web Push com chaves VAPID geradas por nós (P1) | D1 |
| Ambiente local | **Docker Compose** | D8 |
| Produção | **Frontend na Netlify**; API + harness + dados + modelos + banco **numa máquina do time**, em Docker, exposta por **Cloudflare Tunnel** (HTTPS) | D8, D22 |
| Idioma | **Português** no código, nos comentários e nos nomes | D12.4 |

Versões: Python 3.12; as demais bibliotecas na versão estável do dia em que forem instaladas, **fixadas no arquivo de dependências** (`pyproject.toml`/lockfile e `package-lock.json`).

Na final, conforme as respostas: LangGraph (D5), PostgreSQL + armazenamento de objetos + fila (D6) e, se o time conseguir acesso, API da OpenAI ou da Anthropic (observação da D3). O cliente do LLM fica isolado para essa troca ser trivial.

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
                                      ├─ api       (FastAPI + harness + dados, um processo Python)
                                      │    ├─ SQLite + arquivos  (volume)
                                      │    ├─ faster-whisper, Piper, ffmpeg
                                      │    └─ fila de mensagens  (um item por vez)
                                      └─ ollama    (modelos de visão e de conversa, CPU)
```

Consequências que todas as frentes precisam respeitar:

1. **A máquina de produção fica ligada** durante a avaliação da banca e a demo. Qual máquina e quem cuida dela: BE-D3 em [`backend/discussao.md`](../backend/discussao.md).
2. **Processamento assíncrono.** O túnel da Cloudflare corta requisições que passam de ~100 s, e o modelo em CPU pode demorar mais que isso numa foto. Por isso, nenhuma requisição espera o harness: a API recebe a mensagem, responde na hora com `202` e o frontend consulta a resposta (§6).
3. **Domínios diferentes** (Netlify × túnel): autenticação por **token Bearer no cabeçalho**, não por cookie (o Safari bloqueia cookie entre sites). A API libera CORS só para o domínio da Netlify e para `localhost`.
4. **URL da API no frontend** vem da variável `VITE_API_URL`. Se o túnel tiver URL aleatória, a variável é atualizada e o frontend republicado antes da apresentação (BE-D2).
5. **CPU é lento:** a imagem é reduzida no celular, a fila processa uma mensagem por vez, a conversa mostra "a Seri está lendo a receita…" e o **vídeo de backup da demo** é obrigatório.
6. **Privacidade:** o modelo é local, então foto, áudio e receita **não saem da máquina do time** para nenhum provedor de IA.

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
    status: Literal["proposto", "nao_confirmado", "ilegivel", "confirmado"]

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
    tipo: Literal["confirmar_pendencia", "recusar_pendencia", "corrigir_item"]
    pendencia_id: str
    dados: dict                         # em corrigir_item: {"item_id": ..., "texto": "o nome certo é ..."}

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
    tipo: Literal["texto", "lista_para_confirmar", "alertas", "pedido_de_foto", "ligue_192", "resumo"]
    texto: str                          # sempre presente; é o que o Auditor verifica
    audio: Anexo | None                 # fala da Seri, quando houver
    itens: list[ItemLido] | None        # em lista_para_confirmar
    alertas: list[Alerta] | None        # em alertas e lista_para_confirmar
    resumo_id: str | None               # em resumo
    botoes: list[Botao]

class RespostaHarness:
    mensagens: list[MensagemSaida]
    estado: Literal["ok", "aguardando_confirmacao", "erro"]

def processar_mensagem(entrada: MensagemEntrada, repo: Repositorio) -> RespostaHarness: ...
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
    idoso_apelido: str
    periodo_inicio: date
    periodo_fim: date
    motivo: str                         # por que foi gerado (a conduta)
    lista_atual: list[ItemLido]
    doses_perdidas: list[dict]          # {"item_id", "nome", "horario_previsto"}
    sintomas: list[dict]                # SintomaEstruturado + "registrado_em" + conduta
    alertas: list[Alerta]
    perguntas_para_profissional: list[str]
    aviso: str                          # texto fixo: "Gerado a partir dos relatos da cuidadora. Não é diagnóstico."
    gerado_em: datetime
```

### C6 — Plataforma → harness: memória e ações (A implementa, B usa)

```python
class Repositorio(Protocol):
    # leitura (Contexto)
    def obter_idoso(self, idoso_id) -> dict: ...                     # apelido
    def obter_lista_atual(self, idoso_id) -> ListaVersao: ...        # versao, confirmada_em, itens: list[ItemLido]
    def obter_cronograma(self, idoso_id) -> list[Horario]: ...       # item_id, horario, ativo
    def obter_doses(self, idoso_id, desde) -> list[Dose]: ...        # horario_id, previsto, status: tomada|nao_tomada|sem_resposta
    def obter_diario(self, idoso_id, desde) -> list[RegistroDiario]: ...
    def obter_historico(self, conta_id, limite=20) -> list[MensagemDaConversa]: ...
    def obter_pendencias(self, conta_id) -> list[Pendencia]: ...     # pendencia_id, tipo, dados, criada_em

    # escrita (ferramentas)
    def criar_pendencia(self, conta_id, tipo, dados) -> str: ...     # tipos: lista_para_confirmar, mudanca_cronograma, diario_aberto, leitura_baixa_confianca
    def resolver_pendencia(self, pendencia_id, resultado) -> None: ...
    def salvar_lista_confirmada(self, idoso_id, itens) -> int: ...   # cria nova versão e o cronograma; devolve a versão
    def alterar_cronograma(self, idoso_id, mudancas) -> None: ...
    def registrar_dose(self, horario_id, status, quando) -> None: ...
    def registrar_sintoma(self, idoso_id, sintoma, conduta) -> str: ...
    def salvar_resumo(self, resumo: Resumo) -> dict: ...             # {"resumo_id", "url_pdf", "url_publica"}
    def registrar_passo(self, passo: dict) -> None: ...              # registro de passos (P1)
```

B não mexe no schema do banco. Para trabalhar sem a API, B mantém um `RepositorioEmMemoria` que segue este protocolo (também usado pela avaliação).

### C7 — Avaliação → harness (C chama, B expõe)

```python
harness.processar_mensagem(entrada, repo)                         # o harness inteiro
harness.leitor.ler(anexo) -> list[ItemLido]                       # leitura isolada
harness.auditor.verificar(texto, contexto) -> ResultadoAuditor    # aprovado: bool, motivos: list[str], texto_final: str
harness.diario.estruturar(texto) -> SintomaEstruturado
```

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
| Fato clínico só de ferramenta, com fonte | `Alerta` e `Conduta` sempre vêm de C2–C4; o Auditor bloqueia fato clínico sem objeto de origem | B + C |
| Sinal de alarme não passa pelo LLM | `detectar_alarme` antes do modelo → mensagem fixa `ligue_192` | C (regra) + B (posição no fluxo) |
| Na dúvida, chamar um humano | Fluxo de confiança baixa (D19) e "confirme com o farmacêutico" | B |
| LGPD | Consentimento antes de qualquer envio; dados mínimos; nada para a operadora | A |

### 7.2 Regras do harness (D21)

- Até **5 chamadas de ferramenta por mensagem**. No limite, o harness para e responde com o que tem.
- **Exigem confirmação da cuidadora:** `salvar_lista_confirmada` e qualquer mudança no cronograma. **Diretas:** `registrar_dose` e `registrar_sintoma`.
- **O modelo nunca decide sozinho:** o sinal de alarme (regra fixa → 192), os fatos clínicos (só vêm das ferramentas de C) e a liberação da saída (sempre passa pelo Auditor).
- **Registro de passos** (P1): cada observação, ferramenta chamada, resultado e bloqueio do Auditor fica guardado **só no servidor**.

### 7.3 LGPD e dados

- A tela de consentimento é a única forma de consentimento no regional (D14.3). Sem consentimento aceito, a API recusa os envios.
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

Mais o relatório da avaliação (frente `avaliacao`), o pitch e o vídeo de backup (frente `negocio`).
