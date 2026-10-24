# Checklist — 00-projeto

> Dono de cada tarefa: **A** (Beatriz — Plataforma), **B** (Caio — Harness agêntico), **C** (Roberto — Dados, avaliação e negócio), **Todos**. Ver [`divisao.md`](divisao.md).
> As tarefas de construção ficam no `checklist.md` de cada frente. Aqui ficam só as tarefas do projeto e as que envolvem os três.

## Fase 0 — Organização e decisões (Todos)

- [x] Criar `specs/` com regras e índice (`README.md`)
- [x] Escrever a visão do projeto (`visao.md`)
- [x] Levantar estudo de stack e perguntas (`discussao.md`)
- [x] Revisar visão e discussão com `docs/f3_plano_startup_v1.md` (22/10)
- [x] Trocar WhatsApp por plataforma própria na visão e na discussão (22/10)
- [x] Propor divisão do time em 3 pessoas (`divisao.md`)
- [x] Incluir foto da receita física como entrada principal (22/10)
- [x] Documentar a plataforma mobile-first (visão §2.5, D20) (22/10)
- [x] Adotar a nomenclatura "harness agêntico" e renomear a antiga frente de testes para "avaliação" (23/10)
- [x] Responder a discussão (D0–D22) e definir quem é A, B e C (23/10)
- [x] Escrever a `spec.md` do 00-projeto, com os contratos C1–C7 (23/10)
- [x] Criar as frentes `frontend`, `backend`, `harness`, `dados`, `avaliacao` e `negocio` com discussão, spec e checklist (23/10)
- [x] Resolver D13: `docs/` fica onde está, fora do repositório, com observação no `README.md` (23/10)
- [ ] **Todos** — Aprovar a `spec.md` do 00-projeto e os contratos C1–C7 (C ✔ 23/10; A e B pendentes)
- [ ] **Todos** — Ler a spec da própria frente e responder as perguntas da `discussao.md` dela (as que não bloqueiam já têm padrão)

## Fase 1 — Regional (24/10): o que envolve os três

- [ ] **A** — Esqueleto do repositório, `contratos/` e Docker Compose primeiro: destrava B e C ([`backend/checklist.md`](../backend/checklist.md))
- [ ] **Todos** — Definir a máquina de produção e o responsável (BE-D3)
- [ ] **Todos · P0** — Fotografar caixas de remédio (meta: 20)
- [ ] **Todos · P0** — Juntar receitas físicas, impressas e à mão, anonimizadas (D19, AV-D1)
- [ ] **Todos · P0** — Integração: dados → harness → plataforma (trocar os stubs, um por vez)
- [ ] **Todos · P0** — Roteiro da demo funcionando na Netlify, em Android e iPhone (00-projeto/spec §8)
- [ ] **Todos · P0** — Rodar a avaliação, congelar o código, gravar o vídeo de backup
- [ ] **Todos · P0** — Revisar os materiais de negócio e ensaiar o pitch

## Checklists das frentes

| Frente | Dono | Checklist |
|---|---|---|
| frontend | A | [`frontend/checklist.md`](../frontend/checklist.md) |
| backend | A | [`backend/checklist.md`](../backend/checklist.md) |
| harness | B | [`harness/checklist.md`](../harness/checklist.md) |
| dados | C | [`dados/checklist.md`](../dados/checklist.md) |
| avaliacao | C | [`avaliacao/checklist.md`](../avaliacao/checklist.md) |
| negocio | C (revisão de todos) | [`negocio/checklist.md`](../negocio/checklist.md) |

O que fica para a final: [`escopo-por-fase.md`](escopo-por-fase.md) §3.
