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
- **Dependência do Diário.** As regras de gravidade usam o vocabulário (`vocabulario.csv`): casam o termo canônico ou um sinônimo nos `sintomas` e na `descricao`. Mesmo assim, termos que o Diário (`harness.diario.estruturar`) invente fora do vocabulário podem não casar. Ver DA-D4.
- **Negação não é tratada** (DA-D2, conservador): "não teve dor no peito" mostra o cartão 192. Vale também para "sem febre", "sem tontura" nas regras de gravidade.
- **Não cobre ainda:** o "triplo golpe" (IECA/BRA + diurético + anti-inflamatório), interações entre três remédios, CBMPI condicional a dose/duração (AAS e omeprazol ficaram de fora porque o fluxo não captura dose e duração), e diclofenaco tópico junto de AINE oral.
- `duplicidade_principio` (mesmo princípio em 2 itens) vem de regra fixa, sem tabela clínica. O contrato só permite `llm` ou `profissional` na `conferencia`, e usei `llm`.

## `vocabulario.csv` (feito com apoio de LLM)

Fonte do vocabulário que o Diário deve usar (DA-D4): 51 linhas (41 sintomas, 8 sinais, 3 intensidades), cada uma com definição, sinônimos, exclusões, exemplo e tratamento. Gerado por Claude Sonnet 5.5 a partir dos termos das regras, **sem segunda leitura de LLM nem de profissional**; as regras de gravidade foram reescritas para usar só nomes canônicos dele, e entrou a regra `grav_dor_cabeca_subita` (192) e `grav_pressao_baixa` (24h), ambas sugeridas por revisões de LLM e pendentes de revisão clínica. Os sinônimos usam `*` (começo de palavra) e `%` (até 5 palavras no meio).

## Tabelas do C8 (`info_remedio`), 24/10/2026

- **`indicacoes.csv`** ("para que serve" dos 20 remédios): gerada por Claude Sonnet 5.5 e conferida por um subagente Sonnet em sessão limpa, que abriu rótulos da FDA (DailyMed) e algumas bulas brasileiras; 12 de 20 frases foram ajustadas. A coluna `fonte` cita só links que o revisor abriu. **A bula oficial da Anvisa não foi conferida** (o bulário bloqueia robôs). As frases são de uso comum em bula; usos fora de bula (por exemplo clonazepam e diazepam para insônia) ficaram de fora de propósito.
- **`farmacia_popular.csv`**: transcrito do PDF oficial "Elenco de Medicamentos e Insumos" do Ministério da Saúde, **atualizado em 31/08/2026** (baixado em 24/10/2026 para `dados/brutos/farmacia_popular/`, fora do Git). Dos 20 remédios, 10 estão no programa (14 linhas, por concentração). Os documentos vêm da página oficial do programa: documento oficial com foto e CPF, e receita dentro da validade. Transcrição feita por LLM, sem segunda leitura humana; a lista muda com o tempo, então a data da consulta fica na coluna `fonte`.
- **`tipos_receita.csv`** e a coluna **`tipo_receita`** de `remedios.csv`: o tipo vem da tarja da CMED (tarja preta = controle especial; classe J1 = antimicrobiano), usando o mais restritivo entre as apresentações do princípio. Entre os 20, só clonazepam e diazepam são controle especial. **As validades (controle especial 30 dias, antimicrobiano 10) foram escritas de memória e não conferidas**; a de receita simples ficou vazia porque não há prazo legal confirmado (o harness então não avisa vencimento).
- Os auxiliares do harness `texto_normalizado` e `nomes_conhecidos` não são contratos; vêm de `dados/texto.py` e das tabelas de remédios.
