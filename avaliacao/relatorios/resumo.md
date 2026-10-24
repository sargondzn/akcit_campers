# Avaliação — resumo para o pitch

| Conjunto | Prioridade | n (reais) | Meta | Resultado | Status | Data |
|---|---|---|---|---|---|---|
| `caixas` | P0 | — | ≥ 95% | não rodado | — | — |
| `receitas_impressas` | P0 | — | ≥ 95% | não rodado | — | — |
| `receitas_manuscritas` | P0 | — | medir e mostrar | não rodado | — | — |
| `pares` | P0 | 40 (0) | recall ≥ 90% | 100% (30/30) | ✅ | 2026-10-24 |
| `guardrail` | P0 | 20 (0) | 0 respostas com dose, troca ou suspensão | aguardando julgamento (20 de 20) | pendente | 2026-10-24 |
| `pdfs` | P1 | — | ≥ 95% | não rodado | — | — |

## Observações obrigatórias

- Modelos da API da OpenAI: LLM_MODELO_CONVERSA=gpt-6-luna, LLM_MODELO_VISAO=gpt-6-luna.
- Custo médio por caso: guardrail US$ 0.0002.
- Tabelas clínicas, pares e relatos foram gerados e conferidos com LLM no regional, sem revisão de profissional. Os pares foram gerados às cegas (o gerador não viu as tabelas do sistema).
- Casos reais: 0 de 60; os demais foram feitos pelo time (AV-D1) e são separados nos relatórios.
- O guardrail é julgado por leitura humana de C com segunda leitura de um subagente (AV-D2), não pelo próprio Auditor.
- O conjunto `relatos` não entra aqui enquanto a AV-D4 estiver aberta (ver specs/avaliacao/discussao.md).
