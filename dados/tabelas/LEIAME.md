# Tabelas da frente `dados`: como foram feitas

Registro exigido pela DA-D3 (`specs/dados/discussao.md`). Data: 24/10/2026.

## Lista dos 20 remédios (DA-D1)

losartana, hidroclorotiazida, anlodipino, enalapril, atenolol, furosemida, espironolactona, metformina, glibenclamida, sinvastatina, atorvastatina, varfarina, ácido acetilsalicílico, clopidogrel, omeprazol, clonazepam, diazepam, diclofenaco, ibuprofeno, levotiroxina. Extra: a associação losartana + hidroclorotiazida. A constante `PRINCIPIOS` fica em `dados/etl/cmed.py`.

## `remedios.csv` e `sinonimos.csv` (não são feitos por LLM)

- Fonte: lista de preços CMED publicada em 09/10/2026 (`lista_pmc__20261009...xlsx`, baixada de gov.br/anvisa, aba "Lista PMC"). O arquivo fica em `dados/brutos/` (fora do Git); `python -m dados.etl.cmed` regenera as duas tabelas.
- Checagem de risco (item 2): a coluna `SUBSTÂNCIA` traz o princípio ativo (associações separadas por `;`), então o ETL é automático. Os 20 princípios têm apresentações na lista.
- Entram só apresentações orais (comprimido, cápsula, líquido). Injetáveis, tópicos e aerossóis são descartados. Marcas que saíram do mercado (ex.: Zocor) não aparecem.
- Sinônimos: nomes de sal da CMED ("cloridrato de metformina") mais apelidos fixos (AAS, Aspirina, Glifage, Glucophage, simvastatina).

## Tabelas clínicas feitas com LLM (`interacoes`, `classes`, `cbmpi`, `sinais_alarme`, `regras_gravidade`)

- **Geração:** Claude Sonnet 5.5, no Claude Code, restrita aos 20 princípios. As referências da coluna `fonte` são as que o gerador indicou. **Não foram abertas nem conferidas pelo gerador.**
- **Conferência:** 3 subagentes Claude Sonnet 5.5, em sessão limpa, sem ver o prompt de geração, só leitura, com a instrução "procure erros linha a linha". Um conferiu `interacoes.csv`, outro `classes.csv` e `cbmpi.csv`, outro `sinais_alarme.csv` e `regras_gravidade.csv`. Os relatórios foram aplicados em 24/10/2026.
- Tudo está com `conferencia = llm`. Nada foi revisado por profissional.

### Mudanças feitas depois da conferência

- `interacoes.csv`: 6 linhas ajustadas e 6 pares novos sugeridos pelo revisor (34 → 40 linhas). Depois, um subagente **Opus** abriu fontes reais (bulas da FDA e SmPC do Reino Unido, mais 2 espelhos de bulas brasileiras) para os 4 pares da demo e os 6 novos; os trechos ficam em `dados/brutos/bulas/` (fora do Git) e a coluna `fonte` cita só o que foi aberto. As outras 30 linhas terminam com "(fonte não conferida)". **A bula oficial da Anvisa não foi conferida** (o bulário bloqueia robôs).
- `classes.csv`: nome da classe da espironolactona; a fonte agora separa a classe (ATC) da decisão `duplicidade_relevante` (critério editorial do projeto).
- `cbmpi.csv`: critérios reescritos conforme o texto do consenso (Quadro 1: benzodiazepínicos, critério 5; glibenclamida, 26; AINE não seletivo em uso prolongado, 34), conferido pelo revisor contra o PDF do artigo.
- `sinais_alarme.csv`: as 4 regexes originais pegaram só 73 de 120 frases do revisor. Foram reescritas duas vezes olhando falhas de frases cegas geradas por Sonnet. Entraram 3 sinais novos (`alarme_avc`, `alarme_desmaio`, `alarme_sangramento_grave`), além dos 4 da visão §2.3. **Em frases novas nunca vistas (rodada 3) o recall é de cerca de 56%**; o ajuste não melhorou a generalização (detalhes em `specs/dados/revisao-humana.md`).
- `regras_gravidade.csv`: regras novas (queda sem conseguir levantar, suor frio com palpitação, sonolência excessiva, engasgo) e sinônimos nos termos.
- **As regexes e regras reescritas não foram revisadas de novo.** Elas foram ajustadas para passar nas frases do próprio revisor, então o desempenho em frases novas pode ser pior que o dos testes.

## Limitações conhecidas

- **Fontes clínicas não abertas.** O revisor não conseguiu abrir o DDInter nem as bulas da Anvisa. **Antes da demo, abra a bula de cada um dos 4 pares e cite só o que viu:** varfarina + AAS, varfarina + diclofenaco, losartana + espironolactona, sinvastatina + anlodipino. A bula do Marevan não foi confirmada para o diclofenaco, a do Aldactone para a losartana, nem a do Zocor brasileiro para o anlodipino.
- **Mesma família de modelo** gerou e conferiu: o erro correlacionado não some.
- **Dependência do extrator.** `s:` nas regras de gravidade casa por substring nos `sintomas` e na `descricao`. Se `harness.diario.estruturar` não devolver termos canônicos ("queda", "vomito"), casos como "ela caiu" só são pegos pelas regexes de alarme. Combinar o vocabulário com Caio.
- **Negação não é tratada** (DA-D2, conservador): "não teve dor no peito" mostra o cartão 192. Vale também para "sem febre", "sem tontura" nas regras de gravidade.
- **Não cobre ainda:** o "triplo golpe" (IECA/BRA + diurético + anti-inflamatório), interações entre três remédios, CBMPI condicional a dose/duração (AAS e omeprazol ficaram de fora porque o fluxo não captura dose e duração), e diclofenaco tópico junto de AINE oral.
- `duplicidade_principio` (mesmo princípio em 2 itens) vem de regra fixa, sem tabela clínica. O contrato só permite `llm` ou `profissional` na `conferencia`, e usei `llm`.
