# Checklist — dados

> **Dono:** Pessoa C (Roberto). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md).

- [ ] **P0** — Definir a lista dos ~20 remédios (DA-D1)
- [ ] **P0** — Checar o campo de princípio ativo no dicionário de dados da Anvisa/CMED
- [ ] **P0** — ETL da CMED → `remedios.csv` + `sinonimos.csv` (§3, §4)
- [ ] **P0** — `normalizar` (C2) + testes (§5)
- [ ] **P0** — Gerar com LLM e conferir com LLM: `interacoes.csv`, `classes.csv`, `cbmpi.csv` (§2, DA-D3)
- [ ] **P0** — `checar_lista` (C3) + testes (§6)
- [ ] **P0** — `sinais_alarme.csv` + `detectar_alarme` (C4) + testes (§7.1)
- [ ] **P0** — `regras_gravidade.csv` + `avaliar_gravidade` (C4) + testes (§7.2)
- [ ] **P0** — `validar_tabelas.py` e `tabelas/LEIAME.md` (como as tabelas foram feitas)
- [ ] **P0** — Entregar para B: funções reais no lugar dos stubs
