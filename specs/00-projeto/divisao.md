# Divisão do time — 3 pessoas

> **Status:** 🟢 aprovada na D12 (23/10/2026). As tarefas com dono estão no `checklist.md` de cada frente.

---

## 1. Princípio

Cada pessoa é **dona de um pedaço do sistema**, com pastas próprias no código e frentes próprias em `specs/`. As partes só se tocam por **contratos** combinados antes de começar (seção 3). Enquanto a parte do outro não fica pronta, cada um trabalha com um **stub**, uma versão falsa que respeita o contrato. Assim ninguém espera ninguém, e ninguém edita a pasta do outro.

---

## 2. Quem faz o quê

| | **A — Beatriz (Plataforma)** | **B — Caio (Harness agêntico)** | **C — Roberto (Dados, avaliação e negócio)** |
|---|---|---|---|
| **Frentes em `specs/`** | [`frontend`](../frontend/spec.md), [`backend`](../backend/spec.md) | [`harness`](../harness/spec.md) | [`dados`](../dados/spec.md), [`avaliacao`](../avaliacao/spec.md), [`negocio`](../negocio/spec.md) |
| **É dona(o) de** | Interface da cuidadora (PWA mobile-first), API, contas, banco, arquivos, fila de mensagens, agendador de lembretes, PDF e link do resumo, Docker, túnel e deploy | Tudo o que transforma o modelo em agente ([`visao.md` §2.1](visao.md)): percepção (Leitor, STT), uso da memória, loop do Orquestrador, registro de ferramentas, Diário + Escalonador, guardrails (regras fixas, confirmação humana, Auditor), cliente do LLM, voz (TTS), registro de passos | Ferramentas de dados que o harness chama (Normalizador, Farmacovigilante, sinais de alarme, regras de gravidade), a **avaliação** do harness e os materiais de **negócio** |
| **Entrega para os outros** | `contratos/`, esqueleto do repositório e Docker (para todos); `Repositorio` do C6 (para B); endpoint que chama o harness | `processar_mensagem` e `falar` (para A); `Resumo` (para A); C7 (para C) | `normalizar`, `checar_lista`, `detectar_alarme`, `avaliar_gravidade` (para B); relatório de métricas e pitch (para todos) |
| **Trabalha com stub de** | Harness (respostas fixas) | Ferramentas de dados; `RepositorioEmMemoria` | Nenhum: as funções são puras e testáveis sozinhas |

A experiência de cada um não define a divisão: cada pessoa resolve os problemas da própria frente do seu jeito (D12.1).

**O que é o harness agêntico (B):** é tudo o que envolve o modelo para ele **perceber o ambiente, decidir e agir**, deixando de ser só um gerador de texto. O trabalho não é "escrever um prompt": é construir o loop, definir quais ferramentas o modelo pode chamar e com quais permissões, cuidar da memória que ele enxerga e colocar os guardrails que ele não consegue furar. As ferramentas de dados (C) e as ações da API (A) são **plugadas** no harness pelos contratos.

**O que a frente de A precisa ter em mente:** a plataforma será usada principalmente no **celular**. A área da cuidadora é desenhada primeiro para o celular; o painel do profissional (final), primeiro para o computador. Detalhes em [`visao.md` §2.5](visao.md) e na [`frontend/spec.md`](../frontend/spec.md).

**Por que a avaliação fica com C:** quem mede o harness não é quem o construiu.

**Por que a voz fica com B:** o STT é percepção (o Diário escuta) e o TTS é ação (o lembrete fala). A plataforma só grava e toca o áudio.

**Negócio com C, revisado por todos (D12.3):** a frente de C fica mais leve depois que os dados estão prontos; nenhum material de negócio sai sem a revisão de A e B.

### Tarefas compartilhadas (todos)

- Aprovar os contratos **antes de codar**.
- Fotografar caixas (20 no regional; 50 na final) e juntar receitas físicas.
- Integração, avaliação, vídeo de backup e ensaio da demo.
- Revisar os materiais de negócio.

---

## 3. Contratos (pontos de encontro)

Ficam em `contratos/` no código e estão detalhados em [`spec.md`](spec.md) §5. **Mudança de contrato só com acordo dos três.**

| # | Entre | Contrato |
|---|---|---|
| C1 | A → B | `processar_mensagem(entrada, repo) → RespostaHarness` e `falar(texto) → Anexo`. Áudio de entrada em WebM/Opus ou MP4/AAC |
| C2 | B → C | `normalizar(nome) → ResultadoNormalizacao` |
| C3 | B → C | `checar_lista(itens) → list[Alerta]` |
| C4 | B → C | `detectar_alarme(texto) → Conduta | None` e `avaliar_gravidade(sintoma) → Conduta` |
| C5 | B → A | `Resumo` → PDF + link público |
| C6 | A → B | `Repositorio`: leitura do contexto e ações usadas como ferramentas |
| C7 | C → B | A avaliação chama o harness inteiro e os componentes (`leitor`, `auditor`, `diario`) |

---

## 4. Organização do código

```
plataforma/frontend/   ← A
plataforma/api/        ← A
infra/                 ← A
harness/               ← B
dados/                 ← C
avaliacao/             ← C
negocio/               ← C
contratos/             ← todos (só com acordo)
```

Em 23/10/2026 a interface foi para o repositório `akcit-campers-front`. A API ficou neste repositório, em `plataforma/api`.

---

## 5. Ordem de trabalho

1. **A primeiro:** esqueleto, `contratos/` e Docker, para destravar os outros.
2. **Em paralelo, cada um com stub:**
   - A: login → consentimento → conversa → upload → lista → lembrete → PDF → deploy.
   - B: teste de bancada dos modelos → loop com ferramentas falsas → Leitor → confirmação → Diário/Escalonador → Auditor.
   - C: lista dos ~20 → Normalizador → tabelas e Farmacovigilante → alarme e gravidade → avaliação; negócio em paralelo.
3. **Integração:** trocar os stubs pelas peças reais, uma de cada vez: C → B, depois B → A.
4. **Juntos:** rodar a avaliação, congelar o código, gravar o vídeo, ensaiar a demo.
