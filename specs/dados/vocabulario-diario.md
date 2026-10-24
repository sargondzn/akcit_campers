# Vocabulário do diário: `dados` ↔ `harness`

> Gerado por `python -m dados.vocabulario` a partir de `dados/tabelas/regras_gravidade.csv`. Não edite à mão.

O `harness.diario.estruturar` (B) devolve um `SintomaEstruturado`; `avaliar_gravidade` (C) decide a conduta
olhando estes termos. Se o extrator devolver outra palavra (por exemplo "caiu no banheiro" em vez de `queda`),
a regra de 24 horas correspondente **não casa**. As regexes de alarme (192) rodam sobre o texto todo e não
dependem deste vocabulário.

## Como o casamento funciona

- `sintomas`: cada termo é procurado, com `_` valendo espaço, no início de uma palavra da `descricao` ou dos `sintomas`.
  Por isso um termo curto vale como prefixo: `desmai` casa `desmaio`, `desmaiou` e `desmaiada`.
- `sinais`: precisa ser a chave exata, com valor verdadeiro (`{"fala_enrolada": True}`).
- `intensidade`: `leve`, `moderada` ou `forte`; a regra pede "igual ou maior".
- Negação não é tratada (DA-D2): "sem febre" ainda casa `febre`.

## `sintomas`

- `apagou`
- `boca_torta`
- `caiu`
- `cansaco`
- `coco_preto`
- `convuls`
- `desmai`
- `diarreia`
- `dificil_de_acordar`
- `dor`
- `dor_de_cabeca`
- `engasg`
- `enjoo`
- `escorreg`
- `falta_de_apetite`
- `febre`
- `fezes_escuras`
- `fezes_pretas`
- `ficou_mole`
- `fraqueza`
- `glicemia_baixa`
- `inchaco`
- `melena`
- `muito_sonolent`
- `nao_consegue_levantar`
- `nao_esta_urinando`
- `palpitacao`
- `perda_de_consciencia`
- `pior_dor_de_cabeca`
- `quadril`
- `queda`
- `recusa_liquidos`
- `sangramento`
- `sangue_nas_fezes`
- `sonolencia_excessiva`
- `suor_frio`
- `tombo`
- `tontura`
- `tosse_com_sangue`
- `tremor`
- `tropec`
- `urina_com_sangue`
- `vomito`
- `vomito_com_sangue`
- `vomitou_sangue`

## `sinais` (chave exata, valor verdadeiro)

- `desequilibrio_subito`
- `dormencia_subita`
- `fala_enrolada`
- `fraqueza_de_um_lado`
- `perda_de_visao`
- `rosto_torto`

## `intensidade`

- `leve`
- `moderada`
- `forte`

## Pendente de validação (DA-D4)

Falta conferir se o que o extrator de B realmente devolve bate com esta lista. Depois que B integrar, rodar o
conjunto `relatos` pelo caminho completo (`harness.diario.estruturar` → `avaliar_gravidade`) e comparar com o
resultado de `avaliar_gravidade` sobre `SintomaEstruturado` montado à mão.
