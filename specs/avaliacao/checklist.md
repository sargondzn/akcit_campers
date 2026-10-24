# Checklist — avaliacao

> **Dono:** Pessoa C (Roberto). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md).

- [~] **P0** — Pasta compartilhada dos dados privados (AV-D3) e regra de anonimização (§3) — regra em `avaliacao/LEIAME.md`; falta criar a pasta no Drive
- [x] **P0** — Formato dos gabaritos + exemplos fictícios no Git (§4) — `avaliacao/gabaritos.py`, `avaliacao/exemplos/`
- [x] **P0** — Executor com progresso salvo e relatório por conjunto (§6) — `python -m avaliacao.executar`
- [ ] **P0** — Conjunto `caixas`: 20 fotos (fotos: todos) — métrica pronta; faltam as fotos
- [ ] **P0** — Conjunto `receitas_impressas`: 10 fotos (receitas: todos; AV-D1) — métrica pronta; faltam as fotos
- [ ] **P0** — Conjunto `receitas_manuscritas`: 20 fotos (receitas: todos; AV-D1) — métrica pronta; faltam as fotos
- [x] **P0** — Conjunto `pares`: 30 pares, conferidos com LLM — gerados às cegas; recall 100% (30/30), 0 alertas indevidos em 10 negativos (24/10)
- [~] **P0** — Conjunto `guardrail`: 20 tentativas + julgamento (AV-D2) — tentativas prontas; falta rodar com a OpenAI e julgar
- [~] **P0** — `relatorios/resumo.md` para o pitch (§7) — gerador pronto (`python -m avaliacao.relatorio`); faltam os números dos outros conjuntos
- [ ] **P1** — Conjunto `pdfs`: 10 PDFs
- [ ] **P1** — Conjunto `relatos`: 20 relatos, conferidos com LLM

## Funcionalidades de 24/10

- [x] **P0** — 5 casos de guardrail sobre conciliação e "para que serve"
- [ ] **P1** — Conjunto `conciliacao` (10 casos) e métrica
- [x] **P0** — Custo médio por caso no relatório (tokens do registro de passos × `PRECO_USD_MTOK_ENTRADA`/`_SAIDA`)
