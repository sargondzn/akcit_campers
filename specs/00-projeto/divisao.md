# Divisão do time — 3 pessoas

> **Status:** 🟡 proposta. Os nomes e o encaixe de cada pessoa dependem da D12 em [`discussao.md`](discussao.md). As tarefas com dono estão em [`checklist.md`](checklist.md).

---

## 1. Princípio

Cada pessoa é **dona de um pedaço do sistema**, com pastas próprias no código e uma frente própria em `specs/`. As partes só se tocam por **contratos** combinados antes de começar (seção 3). Enquanto a parte do outro não fica pronta, cada um trabalha com um **stub**, uma versão falsa que respeita o contrato. Assim ninguém espera ninguém, e ninguém edita a pasta do outro.

---

## 2. Quem faz o quê

| | **Pessoa A — Plataforma** | **Pessoa B — Harness agêntico** | **Pessoa C — Dados e avaliação** |
|---|---|---|---|
| **Frentes em `specs/`** | `frontend`, `backend` | `harness` | `dados`, `avaliacao` |
| **É dona de** | Interface da cuidadora, API, contas, banco, arquivos, agendador de lembretes, geração do PDF, deploy | Tudo o que transforma o modelo em agente ([`visao.md` §2.1](visao.md)): percepção (Leitor, STT), memória em uso, loop de decisão (Orquestrador), registro das ferramentas, Diário + Escalonador, guardrails (regras fixas, confirmação humana, Auditor), cliente do LLM, voz (TTS), registro de passos | Ferramentas de dados que o harness chama (Normalizador, Farmacovigilante, regras de gravidade e sinais de alarme) e a **avaliação** do harness |
| **Perfil ideal** | JS/TS + React, um pouco de Python; **noção de desenvolvimento mobile** (ver abaixo) | Python + LLM (tool use, saída estruturada, prompts) | Python + dados (planilhas, ETL); gosto por curadoria e testes |
| **Entrega para os outros** | Schema do banco, funções de acesso e ações da API usadas como ferramentas (para B); endpoint que chama o harness | `processar_mensagem` (para A); conteúdo do resumo (para A); componentes chamáveis para a avaliação (para C) | `normalizar`, `checar_lista`, `avaliar_gravidade` (para B); relatório de métricas (para o pitch) |
| **Trabalha com stub de** | Harness (respostas falsas) | Ferramentas de dados (respostas falsas); banco em memória | Nenhum: suas funções são puras e testáveis sozinhas |

**O que é o harness agêntico (Pessoa B):** é tudo o que envolve o modelo para ele **perceber o ambiente, decidir e agir**, deixando de ser só um gerador de texto. A Pessoa B não escreve "um prompt": ela constrói o loop, define quais ferramentas o modelo pode chamar e com quais permissões, cuida da memória que ele enxerga e coloca os guardrails que ele não consegue furar. As ferramentas de dados (C) e as ações da API (A) são **plugadas** no harness pelos contratos.

**O que a Pessoa A precisa ter em mente:** a plataforma será usada principalmente no **celular**. A área da cuidadora é desenhada primeiro para o celular, e o painel do profissional (final) primeiro para o computador. Web e mobile têm características próprias: toque com uma mão, câmera, gravação de áudio, rede instável, teclado virtual, instalação como PWA e teste em aparelho real. A lista completa está em [`visao.md` §2.5](visao.md), e as decisões na D20.

**Por que a avaliação fica com C:** quem mede o harness não é quem o construiu. Isso é o verificador independente que a banca valoriza.

**Por que a voz fica com B:** a voz faz parte do harness: o STT é percepção (o Diário escuta) e o TTS é ação (o lembrete fala). A plataforma só grava e toca o áudio. Isso também alivia a Pessoa A, que tem a frente mais larga.

### Tarefas compartilhadas (todos)

- Fechar a discussão e aprovar os contratos **antes de codar**.
- Fotografar caixas de remédio para o conjunto de avaliação (meta: 20 fotos no regional; 50 na final).
- Integração final e ensaio da demo.
- Negócio (entrevistas, BMC, pitch, relatórios quinzenais): **dono em aberto**, ver D12.

---

## 3. Contratos (pontos de encontro)

Ficam em `contratos/` no código e são detalhados em `00-projeto/spec.md`. **Mudança de contrato só com acordo dos três.**

| # | Entre | Contrato | Exemplo do que passa |
|---|---|---|---|
| C1 | A → B | `processar_mensagem(conta, mensagem) → resposta` | Entrada: texto, foto, PDF ou áudio (**WebM/Opus ou MP4/AAC**, conforme o navegador). Saída: texto, áudio, lista para confirmar, alertas, ação "ligue 192" |
| C2 | B → C | `normalizar(nome_comercial) → princípio ativo + concentração` | "Losartana Potássica 50mg" → losartana, 50 mg |
| C3 | B → C | `checar_lista(princípios) → alertas com fonte` | Interação, duplicidade, CBMPI |
| C4 | B → C | `avaliar_gravidade(sintoma) → conduta` | "queda + batida na cabeça" → 192 |
| C5 | B → A | `Resumo` (estrutura de dados) → PDF | Remédios, doses perdidas, sintomas, perguntas para o médico |
| C6 | A → B | Acesso ao banco e ações da API usadas como ferramentas | Leitura do perfil, lista, doses e diário; `salvar_lista_confirmada`, `agendar_lembrete`, `registrar_dose`. B não mexe no schema |
| C7 | C → B | A avaliação chama o Leitor, o Auditor, o Escalonador e o harness inteiro | Mesmas funções usadas pela plataforma |

---

## 4. Organização do código (proposta)

```
plataforma/frontend/   ← A
plataforma/api/        ← A
harness/               ← B (harness agêntico)
dados/                 ← C
avaliacao/             ← C
contratos/             ← todos (só com acordo)
```

A estrutura final depende de D2, D10 e D18.

---

## 5. Ordem de trabalho

1. **Juntos:** responder a discussão → aprovar a spec do 00-projeto e os contratos.
2. **Em paralelo, cada um com stub:**
   - A: login → conversa → upload → lista.
   - B: loop do Orquestrador com ferramentas falsas → Leitor → confirmação → Diário/Escalonador → Auditor.
   - C: lista dos ~50 → Normalizador → Farmacovigilante → regras de gravidade → avaliação.
3. **Integração:** trocar os stubs pelas peças reais, uma de cada vez: C → B, depois B → A.
4. **Juntos:** rodar a avaliação, congelar o código, ensaiar a demo.
