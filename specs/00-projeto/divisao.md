# Divisão do time — 3 pessoas

> **Status:** 🟡 proposta. Os nomes e o encaixe de cada pessoa dependem da D12 em [`discussao.md`](discussao.md). As tarefas com dono estão em [`checklist.md`](checklist.md).

---

## 1. Princípio

Cada pessoa é **dona de um pedaço do sistema**, com pastas próprias no código e uma frente própria em `specs/`. As partes só se tocam por **contratos** combinados antes de começar (seção 3). Enquanto a parte do outro não fica pronta, cada um trabalha com um **stub**, uma versão falsa que respeita o contrato. Assim ninguém espera ninguém, e ninguém edita a pasta do outro.

---

## 2. Quem faz o quê

| | **Pessoa A — Plataforma** | **Pessoa B — Agentes** | **Pessoa C — Dados e avaliação** |
|---|---|---|---|
| **Frentes em `specs/`** | `frontend`, `backend` | `agentes` | `dados`, `harness` |
| **É dona de** | Interface da cuidadora, API, contas, banco, arquivos, agendador de lembretes, geração do PDF, deploy | Orquestrador, Leitor, Diário + Escalonador, Auditor, cliente do LLM, voz (STT/TTS) | Normalizador, Farmacovigilante (interações, duplicidade, CBMPI, bulas), regras de gravidade e sinais de alarme, harness de avaliação |
| **Perfil ideal** | JS/TS + React, um pouco de Python | Python + LLM | Python + dados (planilhas, ETL); gosto por curadoria |
| **Entrega para os outros** | Schema do banco e funções de acesso (para B); endpoint que chama o agente | `processar_mensagem` (para A); conteúdo do resumo (para A); Leitor e Auditor chamáveis (para C) | `normalizar`, `checar_lista`, `avaliar_gravidade` (para B); relatório de métricas (para o pitch) |
| **Trabalha com stub de** | Agente (respostas falsas) | Funções de dados (respostas falsas); banco em memória | Nenhum: suas funções são puras e testáveis sozinhas |

**Por que a avaliação fica com C:** quem mede não é quem construiu o Leitor e o Auditor. Isso é o verificador independente que a banca valoriza.

**Por que a voz fica com B:** a voz é ferramenta do agente (o Diário transcreve, a Rotina fala). A plataforma só grava e toca o áudio. Isso também alivia a Pessoa A, que tem a frente mais larga.

### Tarefas compartilhadas (todos)

- Fechar a discussão e aprovar os contratos **antes de codar**.
- Fotografar caixas de remédio para o conjunto de avaliação (meta: 50 fotos).
- Integração final e ensaio da demo.
- Negócio (entrevistas, BMC, pitch, relatórios quinzenais): **dono em aberto**, ver D12.

---

## 3. Contratos (pontos de encontro)

Ficam em `contratos/` no código e são detalhados em `00-projeto/spec.md`. **Mudança de contrato só com acordo dos três.**

| # | Entre | Contrato | Exemplo do que passa |
|---|---|---|---|
| C1 | A → B | `processar_mensagem(conta, mensagem) → resposta` | Entrada: texto, foto, PDF ou áudio. Saída: texto, áudio, lista para confirmar, alertas, ação "ligue 192" |
| C2 | B → C | `normalizar(nome_comercial) → princípio ativo + concentração` | "Losartana Potássica 50mg" → losartana, 50 mg |
| C3 | B → C | `checar_lista(princípios) → alertas com fonte` | Interação, duplicidade, CBMPI |
| C4 | B → C | `avaliar_gravidade(sintoma) → conduta` | "queda + batida na cabeça" → 192 |
| C5 | B → A | `Resumo` (estrutura de dados) → PDF | Remédios, doses perdidas, sintomas, perguntas para o médico |
| C6 | A → B | Acesso ao banco (perfil, lista versionada, doses, diário) | Funções de leitura e escrita; B não mexe no schema |
| C7 | C → B | Harness chama o Leitor, o Auditor e o Escalonador | Mesmas funções usadas pela plataforma |

---

## 4. Organização do código (proposta)

```
plataforma/frontend/   ← A
plataforma/api/        ← A
agentes/               ← B
dados/                 ← C
harness/               ← C
contratos/             ← todos (só com acordo)
```

A estrutura final depende de D2, D10 e D18.

---

## 5. Ordem de trabalho

1. **Juntos:** responder a discussão → aprovar a spec do 00-projeto e os contratos.
2. **Em paralelo, cada um com stub:**
   - A: login → conversa → upload → lista.
   - B: Leitor → confirmação → Orquestrador → Diário/Escalonador → Auditor.
   - C: lista dos ~50 → Normalizador → Farmacovigilante → regras de gravidade → harness.
3. **Integração:** trocar os stubs pelas peças reais, uma de cada vez: C → B, depois B → A.
4. **Juntos:** rodar o harness, congelar o código, ensaiar a demo.
