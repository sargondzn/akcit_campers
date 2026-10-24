# Checklist — dados

> **Dono:** Pessoa C (Roberto). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md).

- [x] **P0** — Definir a lista dos ~20 remédios (DA-D1)
- [x] **P0** — Checar o campo de princípio ativo no dicionário de dados da Anvisa/CMED
- [x] **P0** — ETL da CMED → `remedios.csv` + `sinonimos.csv` (§3, §4)
- [x] **P0** — `normalizar` (C2) + testes (§5)
- [x] **P0** — Gerar com LLM e conferir com LLM: `interacoes.csv`, `classes.csv`, `cbmpi.csv` (§2, DA-D3)
- [x] **P0** — `checar_lista` (C3) + testes (§6)
- [x] **P0** — `sinais_alarme.csv` + `detectar_alarme` (C4) + testes (§7.1)
- [x] **P0** — `regras_gravidade.csv` + `avaliar_gravidade` (C4) + testes (§7.2)
- [x] **P0** — `validar_tabelas.py` e `tabelas/LEIAME.md` (como as tabelas foram feitas)
- [x] **P0** — Entregar para B: funções reais no lugar dos stubs (`from dados import normalizar, checar_lista, detectar_alarme, avaliar_gravidade`; troca dos stubs é de B)
- [x] **P0** — Vocabulário do Diário como dado (`vocabulario.csv`), validado e testado; o documento prevalece (DA-D4)
- [x] **P0** — Testes E2E de relatos: texto cru e oráculo (`test_relatos_e2e.py`, `avaliacao/relatos.py`)
- [ ] **P0** — Validar com B o Diário real × vocabulário (DA-D4): colar o bloco em `harness/prompts/diario.md` e rodar `test_relatos_e2e.py` com `OPENAI_API_KEY`
- [ ] **P1** — Revisão humana póstuma das tabelas e fontes (`revisao-humana.md`)

## Funcionalidades de 24/10 (E4, E8)

- [x] **P0** — `indicacoes.csv` para os ~20 remédios, gerada e conferida com LLM, com fonte (E8)
- [x] **P0** — `farmacia_popular.csv` a partir da página oficial do programa, com a data (E4): elenco de 31/08/2026
- [x] **P1** — `tipos_receita.csv` e a coluna `tipo_receita` em `remedios.csv` (E4): tipo derivado da tarja da CMED; validades conferidas em fonte oficial por subagente (simples 180 = Farmácia Popular, não prazo legal; ver `revisao-humana.md` §8)
- [x] **P0** — `info_remedio` (C8) + testes
- [ ] **P1** — Revisão humana das validades de receita: abrir a RDC 1.000/2025 e a portaria 12.091/2026 republicada no Diário Oficial
- [ ] **P0** — B liga `texto_normalizado` e `nomes_conhecidos` de `dados` na ponte do harness (hoje ainda são stubs) e ajusta o artigo da frase "para que serve"
