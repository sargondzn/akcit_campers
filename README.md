# Seriema

**F3 — Cuidador familiar e a medicação do idoso** · AKCIT Camp 2026

A Seriema é uma plataforma em que a **cuidadora familiar** de um idoso que toma muitos remédios conversa com um agente de IA, a **Seri**. Ela fotografa a receita (impressa ou escrita à mão), a caixa do remédio ou envia o PDF da receita digital. A Seri monta uma lista única com os remédios de vários médicos e pede que ela confirme.

> *"Mande a foto dos remédios e um áudio do dia. A Seriema organiza tudo, lembra por você e avisa quando algo precisa de um profissional."*

A Seri **organiza e encaminha; não decide**. Nunca sugere dose, troca ou suspensão.

---

## O que a Seri faz

| | Funcionalidade |
|---|---|
| 📷 | **Lê a receita** (foto impressa ou à mão, caixa, PDF) e propõe a lista para a cuidadora conferir, corrigir e confirmar |
| ⚠️ | **Aponta interações, duplicidades e remédios inapropriados para idosos**, sempre mandando levar ao farmacêutico ou ao médico |
| ⏰ | **Lembra as doses** com texto e áudio, e registra se a dose foi dada |
| 🎙️ | **Registra sintomas** que a cuidadora relata por áudio e aplica as regras de gravidade |
| 🚨 | **Manda ligar 192** em sinal de alarme (queda com batida na cabeça, dor no peito, falta de ar, confusão súbita), sem passar por nenhum modelo |
| 💊 | **Explica para que serve cada remédio**, com a fonte (E8) |
| 🔁 | **Compara cada receita nova com a lista** e mostra o que entrou, o que mudou e o que não veio (E1) |
| 🩺 | **Prepara a consulta** na véspera e registra o que o médico disse (E2) |
| 📦 | **Avisa antes de o remédio acabar e de a receita vencer**, e diz quando ele sai de graça pelo Farmácia Popular (E4) |

### Guardrails (inegociáveis)

1. Nunca sugere dose, troca ou suspensão. Um **Auditor** em código confere toda resposta antes de ela sair.
2. Nada vira lista ou cronograma sem o **"confirmo"** da cuidadora.
3. Fatos clínicos (interações, para que serve, Farmácia Popular) vêm de **tabelas com fonte**. O modelo só explica.
4. Sinal de alarme vai direto para **"ligue 192"**, por regra fixa.
5. Leitura com confiança baixa: a Seri pede outra foto ou encaminha a um profissional.
6. LGPD: consentimento registrado na plataforma, dados mínimos. O termo informa que foto, receita e transcrição do áudio são processadas pela OpenAI.

---

## Como funciona

```
  Interface (PWA, celular primeiro)            repositório akcit-campers-front
  conversa · foto · PDF · áudio · lista · lembrete
                     │  HTTP
                     ▼
  API (FastAPI + SQLite)                       plataforma/api
  contas · consentimento · arquivos · lista versionada · lembretes · PDF do resumo
  app/ponte.py ── chama o harness (C1) · app/repositorio.py ── memória do harness (C6)
                     │
                     ▼
  HARNESS AGÊNTICO (Agno + API da OpenAI)      harness/
  1. percepção: Leitor (visão) · Intérprete · Escuta (Whisper local)
  2. regras fixas: alarme → 192, sem agente
  3. contexto: lista, doses, diário e pendências lidos do banco
  4. rota: fluxo de leitura · fluxo do diário · equipe da Seri
           (Rotina, Explicador, Diário, Agenda, Preparador, Farmácia)
  5. Auditor em toda saída  →  6. Fala (Piper local)
                     │
                     ▼
  FERRAMENTAS DE DADOS (determinísticas)       dados/
  normalizador · farmacovigilante · gravidade · info_remedio
```

**Harness** aqui quer dizer **harness agêntico**: tudo o que envolve o modelo para ele perceber o ambiente, decidir e agir. São as ferramentas, a memória, os fluxos e os guardrails. Testes e métricas são a **avaliação** (`avaliacao/`), que mede o harness de fora.

O que é segurança ou cálculo fica **fora dos agentes**, em código: regras fixas, confirmação humana, Auditor, conciliação, estoque e Escalonador.

---

## Time

| Pessoa | Frente | Pastas |
|---|---|---|
| **A — Beatriz** | Plataforma: interface e API | `plataforma/api`, repositório `akcit-campers-front` |
| **B — Caio** | Harness agêntico | `harness/` |
| **C — Roberto** | Dados, avaliação e negócio | `dados/`, `avaliacao/` |
| Todos | Contratos entre as partes (só mudam com acordo dos três) | `contratos/` |

As partes se tocam só pelos contratos C1–C8, descritos em [`specs/00-projeto/spec.md`](specs/00-projeto/spec.md) §5.

---

## Estrutura do repositório

```
akcit_camp/
├── plataforma/api/   ← API da plataforma (FastAPI). Chama o harness pela app/ponte.py
├── harness/          ← harness agêntico: núcleo, agentes, fluxos, guardrails, percepção, fala
├── dados/            ← ferramentas de dados: normalizador, farmacovigilante, gravidade, info_remedio
│   └── tabelas/      ← tabelas curadas, cada linha com fonte
├── contratos/        ← tipos compartilhados (C2–C4, C8)
├── avaliacao/        ← conjuntos de casos, métricas e relatório
├── specs/            ← toda a documentação (spec-driven)
├── armazenamento/    ← voz do Piper, áudios gerados, temporários (fora do Git)
└── .env              ← chave da OpenAI e configurações (fora do Git)
```

A interface fica em outro repositório: [`akcit-campers-front`](https://github.com/BiaTrixie/akcit-campers-front).

---

## Como rodar (Git Bash, Windows)

### Pré-requisitos

| O quê | Para quê | Como |
|---|---|---|
| Python 3.12 | API, harness, dados e avaliação | [python.org](https://www.python.org/downloads/) |
| Node.js | Interface | [nodejs.org](https://nodejs.org/) |
| ffmpeg | Transcrever o áudio e gerar a voz da Seri | `winget install Gyan.FFmpeg` e reabrir o terminal |
| Chave da OpenAI | Leitura da receita e conversa | No `.env` da raiz (abaixo) |
| Voz do Piper | Áudio das respostas (opcional; sem ela, sai só texto) | `pt_BR-faber-medium.onnx` e `.onnx.json` em `armazenamento/vozes/` ([`specs/harness/externo.md`](specs/harness/externo.md) §6.2) |

### 1. Configurar o `.env` (raiz do repositório)

```bash
OPENAI_API_KEY=sk-...
LLM_MODELO_VISAO=...        # opcional
LLM_MODELO_CONVERSA=...     # opcional
AGNO_TELEMETRY=false
```

### 2. Subir a API (terminal 1)

```bash
cd /c/dev/akcit_camp/plataforma/api
py -3 -m venv .venv                                          # só na primeira vez
./.venv/Scripts/python.exe -m pip install -r requirements.txt   # instala também o harness
./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Para conferir, abra `http://127.0.0.1:8000/docs`.

Para rodar **sem a OpenAI**, com as respostas fixas do stub:

```bash
HARNESS_STUB=1 ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Subir a interface (terminal 2)

```bash
cd /c/dev/akcit-campers-front
npm install      # só na primeira vez
npm run dev
```

Abra `http://127.0.0.1:5173` e entre com a conta da demo: `demo@seriema.local` / `seriema`.

Uma foto de receita leva de 10 a 30 segundos para virar lista.

### 4. Conversar com a Seri só no terminal (opcional)

Sem API e sem interface, com um repositório em memória:

```bash
cd /c/dev/akcit_camp
./venv/Scripts/python.exe -m harness.demo --exemplo
```

O `venv/` da raiz se cria com `py -3.12 -m venv venv` e `./venv/Scripts/python.exe -m pip install -r harness/requirements.txt`. Comandos e detalhes em [`harness/README.md`](harness/README.md).

---

## Testes

Todos rodam **sem rede e sem a OpenAI** (agentes falsos e stubs).

```bash
cd /c/dev/akcit_camp
./venv/Scripts/python.exe -m pytest harness/testes -q        # harness
./venv/Scripts/python.exe -m pytest dados/testes -q          # ferramentas de dados
./venv/Scripts/python.exe -m pytest avaliacao/testes -q      # avaliação

cd plataforma/api
./.venv/Scripts/python.exe -m pytest -q                      # API, com e sem o harness
```

A avaliação de verdade (leitura de receitas, pares de interação, guardrail) usa a OpenAI e conjuntos privados. Veja [`avaliacao/LEIAME.md`](avaliacao/LEIAME.md).

---

## Documentação

O projeto segue **spec-driven development**: nada é implementado sem estar numa spec. Cada frente tem `discussao.md` → `spec.md` → `checklist.md`.

| Comece por | O que tem |
|---|---|
| [`specs/README.md`](specs/README.md) | Regras de trabalho e índice das frentes |
| [`specs/00-projeto/visao.md`](specs/00-projeto/visao.md) | O que é, funcionalidades, viabilidade e o registro de mudanças de escopo |
| [`specs/00-projeto/spec.md`](specs/00-projeto/spec.md) | Stack, arquitetura e contratos C1–C8 |
| [`specs/00-projeto/divisao.md`](specs/00-projeto/divisao.md) | Quem faz o quê |
| [`specs/00-projeto/escopo-por-fase.md`](specs/00-projeto/escopo-por-fase.md) | O que entra no regional e o que fica para a final |
| `specs/<frente>/` | `frontend`, `backend`, `harness`, `dados`, `avaliacao`, `negocio` |

READMEs das partes: [`plataforma/api`](plataforma/api/README.md) · [`harness`](harness/README.md) · [`avaliacao`](avaliacao/LEIAME.md).

A pasta `docs/` (plano de startup e escopo original) não é versionada. Quem precisar pede ao administrador do repositório.

---

## Prazos

| Etapa | Data |
|---|---|
| Regional (trilha Goiânia) | 24/10/2026 |
| Final | 28/11/2026 |

Na final entram o painel do profissional, as bases de interação completas e licenciadas e o piloto com famílias. O corte está em [`escopo-por-fase.md`](specs/00-projeto/escopo-por-fase.md).
