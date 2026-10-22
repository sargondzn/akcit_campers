# specs/ — Documentação do projeto

Projeto **Seriema** (nome provisório) — F3: Cuidador familiar e a medicação do idoso · AKCIT Camp 2026.

Toda a documentação do projeto fica nesta pasta. O desenvolvimento segue **spec-driven development**: nada é implementado sem estar em uma spec aprovada.

---

## Regras de trabalho (absolutas)

1. **Instruções do usuário e das specs são absolutas.** Na dúvida, perguntar antes de fazer.
2. **Escopo da ideia não muda** sem pedido explícito do usuário. Fontes do escopo:
   - [`docs/f3_plano_startup_v1.md`](../docs/f3_plano_startup_v1.md) — plano detalhado (16/10)
   - [`docs/f3_cuidador_medicacao.md`](../docs/f3_cuidador_medicacao.md) — escopo original da avaliação
   - **Mudanças de escopo pedidas pelo usuário** ficam registradas em [`00-projeto/visao.md` §5](00-projeto/visao.md) e prevalecem sobre os documentos acima.
   - Qual dos dois documentos prevalece nas divergências entre eles: pendente (D0 em `00-projeto/discussao.md`).
3. **Nada fora do escopo, das specs ou destas regras.**
4. **Versionamento é do usuário:** nenhum commit, push ou PR sem pedido explícito.
5. **Fluxo de cada frente:** `discussao.md` → `spec.md` → `checklist.md`.
   - **discussao.md** — perguntas abertas. O usuário responde antes de a spec ser escrita.
   - **spec.md** — regras e contratos da frente, descritos minuciosamente. Só é escrita/alterada a partir de respostas da discussão.
   - **checklist.md** — atividades a executar, marcadas conforme o andamento.

---

## Estrutura

```
specs/
├── README.md               ← este arquivo (regras + índice)
├── 00-projeto/             ← visão geral e decisões transversais (stack, frentes, prazos)
│   ├── visao.md
│   ├── divisao.md      ← quem faz o quê (3 pessoas) e contratos entre as partes
│   ├── escopo-por-fase.md ← o que entra no regional e o que fica para a final
│   ├── discussao.md
│   ├── spec.md
│   └── checklist.md
└── <frente>/               ← uma pasta por frente, criada após a decisão D10
    ├── discussao.md
    ├── spec.md
    └── checklist.md
```

---

## Índice e status

| Pasta | O que é | Discussão | Spec | Checklist |
|---|---|---|---|---|
| [`00-projeto`](00-projeto/) | Visão, stack, frentes, prazos | 🟡 aguardando respostas | ⚪ não iniciada | 🟡 em andamento |

Visão resumida do projeto: [`00-projeto/visao.md`](00-projeto/visao.md).
O que entra no regional e o que fica para a final: [`00-projeto/escopo-por-fase.md`](00-projeto/escopo-por-fase.md).
Divisão do time e tarefas por pessoa: [`00-projeto/divisao.md`](00-projeto/divisao.md) e [`00-projeto/checklist.md`](00-projeto/checklist.md).

Legenda: ⚪ não iniciada · 🟡 em andamento · 🟢 aprovada/concluída
