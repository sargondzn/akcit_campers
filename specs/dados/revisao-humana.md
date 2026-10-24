# Revisão humana póstuma: o que foi feito por LLM e precisa de olho humano

> Criado em 24/10/2026. No regional, as tabelas, as fontes, os gabaritos e as regexes de `dados` foram feitos e conferidos **só por LLM** (Claude Sonnet 5.5 e Opus), por falta de tempo. Tudo abaixo continua com `conferencia = llm`. Quando uma pessoa revisar uma linha, mude a coluna para `profissional` e escreva quem revisou e quando.

## 1. Fontes dos pares da demo (prioridade alta)

**Quem:** Roberto, e de preferência um farmacêutico ou o professor da área.
**Por quê:** a gravidade e a descrição dos 4 pares foram sustentadas por bulas **da FDA e do Reino Unido** abertas pelo Opus (trechos literais em `dados/brutos/bulas/`, fora do Git). **A bula oficial da Anvisa não foi conferida**: o bulário (`consultas.anvisa.gov.br`) bloqueia robôs com erro 403, e eu não contornei o bloqueio. Opus e Sonnet são da mesma família que gerou a tabela, então a concordância deles não é validação independente.

| Par | Gravidade | Fonte aberta pelo Opus | Abrir na Anvisa |
|---|---|---|---|
| varfarina + AAS | alta | Jantoven (FDA), seção 7.3 | bulário, "Marevan" |
| varfarina + diclofenaco | alta | Diclofenaco (FDA), Drug Interactions; Jantoven, Tabela 3 | bulário, "Marevan" e "Voltaren" |
| losartana + espironolactona | alta | Aldactone (FDA), seções 5.1 e 7.1 | bulário, "Aldactone" e "Cozaar" |
| sinvastatina + anlodipino | moderada | Zocor (FDA), seções 2.5 e 7 | bulário, "Zocor" |

**Como:** abra `https://consultas.anvisa.gov.br/#/bulario/`, busque o nome comercial, baixe a bula do profissional, procure "Interações medicamentosas", copie o trecho e a seção para a coluna `fonte` de `dados/tabelas/interacoes.csv`. A bula brasileira do Marevan que o espelho `bulas.med.br` mostra cita "salicilatos" e AINEs em geral, **não o diclofenaco pelo nome**; a bula do Daonil no espelho é de 2016, talvez desatualizada.

## 2. Pares e fontes que ninguém abriu

- **30 pares antigos** de `interacoes.csv`: a coluna `fonte` termina com "(fonte não conferida)". Citam "DDInter" e bulas que **nenhum modelo nem humano abriu**.
- **6 pares novos** (atenolol com glibenclamida, diclofenaco e ibuprofeno; diclofenaco com glibenclamida; glibenclamida com ibuprofeno; furosemida com hidroclorotiazida): o Opus abriu fontes, mas as **gravidades são julgamento dele**, sobretudo `atenolol+diclofenaco`, `atenolol+ibuprofeno`, `diclofenaco+glibenclamida` (já baixada para baixa, relatos isolados) e `glibenclamida+ibuprofeno` (mantida moderada, relatos raros, pelo perfil do idoso).
- **Texto em português simples** de todas as linhas: um farmacêutico deve ler. A frase "o betabloqueador não esconde o suor da hipoglicemia" foi sugerida de memória e **não entrou** na tabela.

## 3. Classes e CBMPI

- `classes.csv`: a coluna `duplicidade_relevante` (sim ou nao) é **decisão editorial** do projeto, não da ATC. Revisar com farmacêutico. O AAS e o clopidogrel ficaram com `nao` porque a combinação costuma ser intencional (o alerta vem da interação).
- `cbmpi.csv`: os critérios foram conferidos pelo subagente contra o PDF do consenso (Oliveira et al., 2016). Ficaram de fora, por dependerem de dose, duração ou doença: AAS (dose acima de 150 mg), omeprazol (mais de 8 semanas), furosemida e espironolactona. O texto de diclofenaco e ibuprofeno diz "usado por muito tempo", mas o sistema **não captura a duração**: o alerta aparece para qualquer uso.

## 4. Alarmes e gravidade

- `sinais_alarme.csv` tem **7 sinais**. Os 4 primeiros vêm da visão §2.3. **AVC, desmaio ou convulsão e sangramento grave foram acrescentados por C** (com apoio de LLM) e **precisam de aceite de Beatriz, Caio e, de preferência, de um profissional de saúde**.
- **Qualidade medida em frases cegas** (geradas por Sonnet que não viu as regexes; arquivos em `avaliacao/exemplos/relatos_cegos/`):

| Rodada | Situação das regexes | Alarmes que disparam | Falsos positivos |
|---|---|---|---|
| Revisão inicial | originais, frases do revisor | 73 de 120 (61%) | n/d |
| Rodada 1 | originais, 175 frases novas | 103 de 175 (59%); 4 sinais originais: 69% | 2 de 31 |
| Rodada 1 depois do 1º ajuste | ajustadas **olhando estas frases** | 175 de 175 (100%) | 1 de 31 |
| Rodada 2 | depois do 1º ajuste, frases novas | 63 de 84 (75%) | 2 de 15 |
| Rodada 2 depois do 2º ajuste | ajustadas **olhando estas frases** | 84 de 84 (100%) | 0 de 15 |
| **Rodada 3** | **depois dos 2 ajustes, frases novas, sem novo ajuste** | **59 de 105 (56%); 4 sinais originais: 58%** | **3 de 20** |

  **A rodada 3 é a estimativa honesta: cerca de 56%.** Por sinal: confusão 3/15, AVC 6/15, sangramento 6/15, falta de ar 9/15, dor no peito 10/15, desmaio 12/15, queda com batida 13/15.
  **Conclusão: ajustar regex olhando frases não generalizou.** O recall em frases novas ficou igual ao de antes de qualquer ajuste (59%), porque a fala livre tem variedade demais para regras fixas. Parei de ajustar de propósito: continuar só faria os números de ajuste chegarem a 100% sem melhorar o mundo real.
  **Consequência para o pitch e para a meta:** a meta "100% dos alarmes viram 192" (`visao.md` §2.4, conjunto `relatos`) **não é atingida pelas regexes sozinhas** com texto livre; ela só dá 100% em conjuntos usados para ajustá-las. Não afirmar essa meta com números de relatos que as regexes já viram. Decisão pendente do time (AV-D4, em `specs/avaliacao/discussao.md`): permitir uma camada com LLM que **só eleva** a conduta (nunca rebaixa), o que muda a regra "sinal de alarme não passa pelo LLM" da visão §2.3.
- **Falsos positivos conhecidos** (por escolha conservadora, DA-D2): "ficou sem ar num quarto fechado", "desmaio de personagem da novela", "dor no coração de saudade" (as exceções em `gravidade.py::EXCECOES` cobrem pneu, desmaio de décadas atrás e discussão confusa, mas só esses casos). Negação nunca é tratada ("não teve dor no peito" dispara).
- `regras_gravidade.csv`: nível de cada regra (24 horas, 192, observar) é julgamento de LLM; um clínico deve revisar, principalmente as regras de 192 acrescentadas (queda sem conseguir levantar, suor frio com palpitação ou enjoo).
- Os gabaritos cegos (`avaliacao/exemplos/relatos_cegos/`) são frases **fictícias geradas por LLM**, não relatos de cuidadoras. Substituir ou complementar com as entrevistas reais (item 18 da avaliação).

## 5. Contrato

- `Alerta.conferencia` só aceita `llm` ou `profissional`. O alerta `duplicidade_principio` vem de regra fixa e usa `llm`. Se o time achar enganoso, propor um terceiro valor (ver ADR 0001).
- `contratos/dados.py` foi criado por C antes do aceite de A e B (ver ADR 0001).

## 6. Vocabulário com o harness (DA-D4)

Conferir se o que `harness.diario.estruturar` (Caio) devolve bate com `specs/dados/vocabulario-diario.md`. Depois que o Caio integrar: rodar os relatos pelo caminho completo e comparar com `avaliar_gravidade` sobre `SintomaEstruturado` montado à mão.

## Como marcar como feito

Para cada linha revisada: troque `conferencia` para `profissional`, ajuste `fonte` se mudou, e acrescente aqui `Revisado por <nome>, <data>`.

## 7. Vocabulário do Diário e E2E de relatos (DA-D4, 24/10/2026)

- **`vocabulario.csv`** (51 linhas) e **sinônimos, exclusões e pistas de intensidade** são rascunho de LLM. Revisar com quem conhece a fala das cuidadoras: sinônimos largos demais viram supertriagem ("caiu" aparece em "caiu a energia", tratado por exclusões); estreitos demais viram subtriagem.
- **Regras novas** (sugestões de LLM, sem revisão clínica): `grav_dor_cabeca_subita` (dor de cabeça fortíssima de repente → 192) e `grav_pressao_baixa` (pressão baixa com tontura ou fraqueza → 24h).
- **Alarmes ampliados depois do E2E:** vômito com sangue com palavras no meio ("vomitou um tanto de sangue") e engasgo com obstrução ("não entra nem sai ar") passaram a disparar o 192.
- **Gabarito `avaliacao/exemplos/relatos_e2e/gabarito.jsonl`:** 54 relatos escritos e rotulados por um Sonnet que viu só o vocabulário e os níveis (`nivel_esperado` é julgamento dele). Quatro divergências ficaram documentadas no próprio arquivo (campo `observacao`): `e2e_034` (queda com dor no quadril que ainda anda: nossa regra é 192), `e2e_035` (confusão há um dia: o alarme conservador dispara), `e2e_036` (sangue vivo nas fezes: regex larga) e `e2e_046` (inchaço leve de sempre: toda queixa de inchaço é 24h). **Um clínico deve decidir quem está certo.**

### Números do E2E (54 relatos)

| Medição | Texto cru (sem Diário) | Oráculo (Diário perfeito) |
|---|---|---|
| **1ª, antes de qualquer correção** | 42/54 (78%), 8 subtriagens, 4 supertriagens | 48/54 (89%), 1 subtriagem, 5 supertriagens |
| Depois das correções | 49/54 (91%), 2 subtriagens, 3 supertriagens | 50/54 (93%), 0 subtriagens, 4 supertriagens |

A 1ª medição é a honesta. **A segunda é otimista**: as correções foram feitas olhando estes mesmos 54 casos, então o gabarito virou conjunto de desenvolvimento. Subtriagens que restam no texto cru: `e2e_029` (açúcar "58") e `e2e_033` (pressão "80 por 50"), que dependem de número que só o Diário transforma em termo. Em texto cru, **todos os 18 relatos de emergência do gabarito viram 192**, mas isso também foi ajustado olhando o gabarito.
- **Diário real:** `test_diario_real_do_harness` não pôde rodar (sem `OPENAI_API_KEY` neste ambiente). É a medição que falta.
- Para uma estimativa honesta do E2E, gerar uma nova rodada cega (como as de `relatos_cegos`) e medir sem ajustar.

## 8. C8 `info_remedio` e tabelas novas (24/10/2026)

- **`indicacoes.csv`:** rascunho de LLM, conferido por outro LLM (Sonnet, sessão limpa) em rótulos da FDA e algumas bulas brasileiras. **Um farmacêutico ou médico deve validar as 20 frases.** Pontos de decisão que o revisor levantou e ficaram para humano: (a) o AAS ficou só com uso cardiovascular (a bula de 100 mg diz que não é para dor); (b) usos comuns em idoso fora de bula (clonazepam e diazepam para insônia, omeprazol como proteção do estômago) não aparecem; (c) termos difíceis para leigo ("insuficiência cardíaca", "angina") têm explicação entre parênteses só em parte das frases.
- **`farmacia_popular.csv`:** fonte oficial boa (PDF de 31/08/2026), mas **transcrita por LLM**; conferir contra o PDF em `dados/brutos/farmacia_popular/` (ou o site) e refazer quando o programa atualizar a lista. A concentração só vale para as listadas (ex.: losartana 50 mg); `info_remedio` não olha concentração.
- **`tipos_receita.csv` (prioridade média):** **validades não conferidas.** Controle especial = 30 dias e antimicrobiano = 10 dias estão de memória do gerador (Portaria SVS/MS 344/1998 e RDC 471/2021); a receita simples ficou sem prazo (vazio). Confirmar nas normas e, se houver prazo, preencher. Uma pesquisa com outro modelo estava em andamento quando o PR foi aberto; se terminar, entra como commit seguinte.
- **Atenção para o harness:** o stub do Caio assumia 180 dias para receita simples; aqui ela é vazia, então os avisos de "receita vencendo" só valem para controle especial e antimicrobiano até alguém confirmar o prazo.
- **Fontes de bula:** a bula oficial da Anvisa não foi aberta para nenhuma das tabelas (o bulário bloqueia robôs). Para as bulas brasileiras, o revisor usou espelhos de fabricantes e farmácias.
- **Conferência de stubs:** `info_remedio` agora é real (a ponte `harness/dados_ponte.py` para de usar o stub). Continuam stubs do lado do harness `texto_normalizado` e `nomes_conhecidos`, que a ponte ainda não liga a `dados`. O Auditor usa `nomes_conhecidos` para achar remédio citado fora da lista da cuidadora; com os nomes reais (225) ele passa a bloquear marcas que o stub não conhecia.
