# specs/ — Documentação do projeto

Projeto **Seriema** (agente: **Seri**) — F3: Cuidador familiar e a medicação do idoso · AKCIT Camp 2026.

Toda a documentação do projeto fica nesta pasta. O desenvolvimento segue **spec-driven development**: nada é implementado sem estar em uma spec.

---

## Regras de trabalho (absolutas)

1. **Instruções do usuário e das specs são absolutas.** Na dúvida, perguntar antes de fazer.
2. **Escopo da ideia não muda** sem pedido explícito do usuário. Fontes do escopo:
   - `docs/f3_plano_startup_v1.md` — plano detalhado (16/10). **Prevalece** nas divergências com o escopo original (D0).
   - `docs/f3_cuidador_medicacao.md` — escopo original da avaliação.
   - **Mudanças de escopo pedidas pelo usuário** ficam registradas em [`00-projeto/visao.md` §5](00-projeto/visao.md) e prevalecem sobre os documentos acima. É lá que está, por exemplo, a troca do WhatsApp pela plataforma própria.
3. **Nada fora do escopo, das specs ou destas regras.**
4. **Versionamento é do usuário:** nenhum commit, push ou PR sem pedido explícito.
5. **Fluxo de cada frente:** `discussao.md` → `spec.md` → `checklist.md`.
   - **discussao.md** — perguntas abertas, respondidas pelo time.
   - **spec.md** — regras e contratos da frente, descritos minuciosamente. Só muda a partir de respostas da discussão.
   - **checklist.md** — atividades a executar, marcadas conforme o andamento.

> **Documentação de apoio fora do repositório:** a pasta `docs/` (plano de startup, escopo original e avaliação dos candidatos) **não é versionada**. Os links para ela só funcionam na máquina de quem tem a pasta. Quem precisar dos arquivos pode pedi-los ao administrador do repositório.

---

## Estrutura

```
specs/
├── README.md              ← este arquivo (regras + índice)
├── 00-projeto/            ← visão geral e decisões transversais
│   ├── visao.md           ← o que é, funcionalidades, viabilidade, saídas, mudanças de escopo
│   ├── divisao.md         ← quem faz o quê e contratos entre as partes
│   ├── escopo-por-fase.md ← o que entra no regional e o que fica para a final
│   ├── discussao.md       ← decisões D0–D22
│   ├── spec.md            ← stack, arquitetura, contratos C1–C7, regras transversais
│   └── checklist.md
├── frontend/   ← A
├── backend/    ← A
├── harness/    ← B
├── dados/      ← C
├── avaliacao/  ← C
└── negocio/    ← C (revisão de todos)
    (cada frente: discussao.md · spec.md · checklist.md)
```

---

## Índice e status

| Pasta | O que é | Dono | Discussão | Spec | Checklist |
|---|---|---|---|---|---|
| [`00-projeto`](00-projeto/) | Visão, stack, contratos, prazos | Todos | 🟢 respondida | 🟡 aguardando aprovação | 🟡 em andamento |
| [`frontend`](frontend/) | PWA mobile-first da cuidadora | A — Beatriz | 🟡 perguntas não bloqueantes | 🟡 escrita | ⚪ não iniciado |
| [`backend`](backend/) | API, banco, fila, lembretes, PDF, infraestrutura | A — Beatriz | 🟡 perguntas não bloqueantes | 🟡 escrita | ⚪ não iniciado |
| [`harness`](harness/) | Harness agêntico | B — Caio | 🟡 perguntas não bloqueantes | 🟡 escrita | ⚪ não iniciado |
| [`dados`](dados/) | Normalizador, Farmacovigilante, alarme e gravidade | C — Roberto | 🟡 perguntas não bloqueantes | 🟡 escrita | ⚪ não iniciado |
| [`avaliacao`](avaliacao/) | Conjuntos de casos, métricas e relatório | C — Roberto | 🟡 perguntas não bloqueantes | 🟡 escrita | ⚪ não iniciado |
| [`negocio`](negocio/) | BMC, pitch, entrevistas, relatórios | C — Roberto | 🟡 perguntas não bloqueantes | 🟡 escrita | ⚪ não iniciado |

Por onde começar: [`00-projeto/visao.md`](00-projeto/visao.md) → [`00-projeto/spec.md`](00-projeto/spec.md) → a spec da sua frente.

Legenda: ⚪ não iniciada · 🟡 em andamento · 🟢 aprovada/concluída
