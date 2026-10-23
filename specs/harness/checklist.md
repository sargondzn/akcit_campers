# Checklist — harness

> **Dono:** Pessoa B (Caio). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md).

## Base

- [ ] **P0** — Teste de bancada dos modelos na máquina de produção; registrar na HA-D2 (§3)
- [ ] **P0** — `cliente_llm.py` isolado, com saída JSON validada e plano B do tool use (§3)
- [ ] **P0** — Stubs de `normalizar`, `checar_lista`, `detectar_alarme` e `avaliar_gravidade` (C2–C4)
- [ ] **P0** — `RepositorioEmMemoria` (C6) e LLM falso para testes
- [ ] **P0** — `processar_mensagem` com a ordem fixa do §4

## Percepção

- [ ] **P0** — Leitor: foto de receita (impressa e à mão), foto de caixa e PDF → `ItemLido` (§5.1–5.3)
- [ ] **P0** — Fluxo de confiança baixa (§5.4)
- [ ] **P0** — Proposta, correção e confirmação da lista (§5.5)
- [ ] **P0** — Escuta: WebM/Opus e MP4/AAC → texto (§6)
- [ ] **P0** — Contexto a cada mensagem (§4, passo 3)

## Decisão e ações

- [ ] **P0** — Registro de ferramentas (§7.1)
- [ ] **P0** — Loop do Orquestrador com limite de 5 chamadas (§7)
- [ ] **P0** — Diário: estruturar sintoma + até 2 perguntas (§8)
- [ ] **P0** — Escalonador: conduta → 192, resumo + link, ou observar (§8)
- [ ] **P0** — `gerar_resumo` → `Resumo` (C5)
- [ ] **P0** — Fala: `falar(texto)` em MP3 (§10)

## Guardrails

- [ ] **P0** — Regras fixas antes do modelo (§9.1)
- [ ] **P0** — Confirmação humana por pendência (§9.2)
- [ ] **P0** — Auditor com as 4 verificações (§9.3)
- [ ] **P0** — Textos fixos de alerta, conduta e bloqueio (§9.4, `frases.py`)
- [ ] **P0** — Prompt de sistema com a persona da Seri (§12)

## Integração e prova

- [ ] **P0** — Trocar os stubs pelas funções reais de C
- [ ] **P0** — Plugar na API de A (sem stub)
- [ ] **P0** — Expor o C7 para a avaliação
- [ ] **P0** — Testes do §13
- [ ] **P1** — Registro de passos (§11)
