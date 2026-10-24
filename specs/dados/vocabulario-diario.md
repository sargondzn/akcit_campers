# Vocabulário do diário: `dados` ↔ `harness`

> Gerado por `python -m dados.vocabulario` a partir de `dados/tabelas/vocabulario.csv`. Não edite à mão.

**Este vocabulário prevalece enquanto o Diário (`harness.diario.estruturar`, de B) não existe ou não o segue:**
o Diário se adapta a ele. Termo que o Diário devolver fora desta lista não é perdido (as regexes de alarme
e os sinônimos ainda leem o texto), mas as regras de 24 horas podem não casar. Se um termo novo for correto,
ele entra no `vocabulario.csv` (por C), com sinônimos, exemplo e, se for o caso, regra.

## Como o casamento funciona

- Cada termo tem um **nome canônico** (o que o Diário deve devolver) e **sinônimos** (formas de falar). A regra
  casa o nome ou qualquer sinônimo, com `_` valendo espaço, em cada item de `sintomas` e na `descricao`.
  Um sinônimo terminado em `*` casa o começo da palavra (`desmai*` casa desmaiou e desmaiada); sem `*`, é a palavra inteira.
- **Exclusões** apagam usos que não são o sintoma ("caiu a energia", "exame de sangue").
- **Negação** ("sem febre", "não teve vômito") é ignorada só na `descricao`. O que o Diário lista em `sintomas` é
  aceito como está. **Os sinais de alarme (192) não tratam negação** (DA-D2): "não teve dor no peito" mostra o cartão.
- `sinais`: a chave exata com valor verdadeiro (`{"fala_enrolada": True}`), ou um sinônimo na `descricao`.
- `intensidade`: `leve`, `moderada` ou `forte`. Se o Diário não preencher, a regra procura pistas na fala
  ("fortíssima", "insuportável", "dorzinha"); a intensidade do Diário sempre vence.

## Bloco para o prompt do Diário

Copie para `harness/prompts/diario.md` (pasta de B). Gerado também por `python -m dados.vocabulario --json`.

```
Em `sintomas`, use SOMENTE estes termos (um por sintoma que a cuidadora contou; se nenhum servir, use uma palavra simples em minúsculo):
boca_torta, cansaco, confusao_mental, constipacao, convulsao, desmaio, diarreia, dor, dor_abdominal, dor_de_cabeca, dor_nas_costas, dor_no_peito, engasgo, enjoo, falta_de_apetite, falta_de_ar, febre, fezes_pretas, fraqueza, glicemia_baixa, inchaco, nao_consegue_levantar, nao_esta_urinando, palpitacao, pior_dor_de_cabeca, quadril, queda, queda_de_pressao, recusa_liquidos, sangramento, sangue_nas_fezes, sonolencia_excessiva, suor_frio, tontura, tosse, tosse_com_sangue, tremor, urina_com_sangue, vomito, vomito_com_sangue

Em `sinais`, use SOMENTE estas chaves, e só as que estiverem presentes:
bateu_a_cabeca, desequilibrio_subito, dormencia_subita, fala_enrolada, fraqueza_de_um_lado, inicio_subito, perda_de_visao, rosto_torto

Em `intensidade`: leve, moderada, forte (ou vazio, se não deu para entender).
```

## Sintomas (`sintomas`)

| Termo | O que é | Formas de falar | Exemplo | Tratamento |
|---|---|---|---|---|
| `queda` | O idoso caiu ou escorregou, com ou sem machucado. | `queda`, `quedas`, `tombo`, `escorreg*`, `tropec*`, `caiu`, `caiu no`, `caiu na`, `caiu da`, `caiu de`, `caiu e`, `caiu pra`, `caiu sentad*`, `foi ao chao`, `foi pro chao`, `foi parar no chao`, `despencou` | ontem a vó escorregou no banheiro | tem regra de gravidade (24h ou 192) (grav_queda_sem_levantar, grav_queda) |
| `quadril` | Dor ou pancada no quadril depois de uma queda. | `quadril`, `anca` | caiu e está com dor no quadril | tem regra de gravidade (24h ou 192) (grav_queda_sem_levantar) |
| `nao_consegue_levantar` | Depois de cair, não consegue levantar ou apoiar a perna. | `nao consegue levantar`, `nao consegue se levantar`, `nao conseguiu levantar`, `nao consegue ficar de pe`, `nao consegue andar`, `nao consegue firmar a perna`, `nao consegue apoiar` | caiu e não consegue levantar | tem regra de gravidade (24h ou 192) (grav_queda_sem_levantar) |
| `desmaio` | Perdeu os sentidos ou a consciência, mesmo por pouco tempo. | `desmai*`, `apagou`, `apagao`, `ficou mole`, `perdeu a consciencia`, `perdeu os sentidos`, `desacordad*`, `inconscient*`, `sincope`, `piripaque`, `desfalec*` | a vó desmaiou na cozinha | tem regra de gravidade e também dispara o alarme 192 (grav_perda_consciencia) |
| `convulsao` | Crise com tremores no corpo todo, olhos virados, baba ou rigidez. | `convuls*`, `crise convulsiva`, `tremores fortes`, `espuma na boca`, `olhos virados`, `mordeu a lingua` | ele teve uma convulsão | tem regra de gravidade e também dispara o alarme 192 (grav_perda_consciencia) |
| `sangramento` | Sangue saindo do corpo: nariz, corte, boca ou qualquer lugar. | `sangramento*`, `sangrando`, `sangrou`, `sangra`, `hemorragia`, `sangue nao para`, `jorrando sangue`, `sangue jorrando`, `sangue escorrendo` | o nariz do vô está sangrando | tem regra de gravidade (24h ou 192) (grav_sangramento_forte, grav_sangramento) |
| `vomito_com_sangue` | Vômito com sangue vivo ou escuro, parecido com borra de café. | `vomitou sangue`, `vomito com sangue`, `vomitando sangue`, `vomitar sangue`, `borra de cafe`, `hematemese`, `vomitou % sangue`, `vomitando % sangue`, `vomito % sangue` | ela vomitou sangue de manhã | tem regra de gravidade e também dispara o alarme 192 (grav_sangramento_forte) |
| `tosse_com_sangue` | Tosse que traz sangue. | `tosse com sangue`, `tossindo sangue`, `tossiu sangue`, `escarrando sangue`, `cuspindo sangue`, `sangue na tosse` | tossiu sangue ontem à noite | tem regra de gravidade e também dispara o alarme 192 (grav_sangramento_forte) |
| `fezes_pretas` | Fezes pretas, escuras ou com cheiro forte de piche (possível sangramento). | `fezes % pretas`, `fezes % preta`, `fezes % escuras`, `coco % preto`, `coco % escuro`, `melena`, `piche` | as fezes dele estão pretas | tem regra de gravidade (24h ou 192) (grav_sangramento_forte, grav_sangramento) |
| `sangue_nas_fezes` | Sangue vivo nas fezes ou na privada. | `sangue nas fezes`, `sangue no coco`, `fezes com sangue`, `sangue na privada`, `sangue vivo nas fezes` | tinha sangue nas fezes hoje | tem regra de gravidade (24h ou 192) (grav_sangramento) |
| `urina_com_sangue` | Urina vermelha ou com sangue. | `urina com sangue`, `urina % vermelha`, `xixi com sangue`, `sangue na urina`, `xixi % vermelho` | a urina saiu vermelha | tem regra de gravidade (24h ou 192) (grav_sangramento) |
| `tontura` | Sensação de cabeça rodando ou de que vai cair. | `tontura*`, `tonto`, `tonta`, `tonteou`, `tonteira`, `zonzo`, `zonza`, `cabeca rodando` | ela ficou tonta ao levantar | tem regra de gravidade (24h ou 192) (grav_sangramento_forte, grav_tontura_forte, grav_pressao_baixa, obs_sintomas_leves) |
| `fraqueza` | Fraqueza ou falta de força no corpo todo. | `fraqueza`, `fraco`, `fraca`, `sem forca*` | ele está muito fraco hoje | tem regra de gravidade (24h ou 192) (grav_sangramento_forte, grav_pressao_baixa) |
| `suor_frio` | Suor frio, pele gelada e molhada. | `suor frio`, `suando frio`, `gelado e suado`, `gelada e suada` | ficou com suor frio | tem regra de gravidade (24h ou 192) (grav_suor_frio_mal_estar, grav_acucar_baixo) |
| `palpitacao` | Coração disparado ou batendo forte. | `palpitac*`, `coracao disparado`, `coracao acelerado`, `taquicardia` | reclamou de palpitação | tem regra de gravidade (24h ou 192) (grav_suor_frio_mal_estar) |
| `enjoo` | Enjoo ou náusea, com ou sem vômito. | `enjoo`, `enjoad*`, `nausea*`, `ansia` | está enjoada desde cedo | tem regra de gravidade (24h ou 192) (grav_suor_frio_mal_estar, obs_sintomas_leves) |
| `tremor` | Tremor nas mãos ou no corpo. | `tremor*`, `tremendo`, `tremedeira` | as mãos estão com tremor | tem regra de gravidade (24h ou 192) (grav_acucar_baixo) |
| `glicemia_baixa` | Açúcar baixo no sangue (medido ou com sinais claros). | `glicemia % baixa`, `acucar % baixo`, `hipoglicemia`, `acucar caiu` | a glicemia estava baixa | tem regra de gravidade (24h ou 192) (grav_acucar_baixo) |
| `febre` | Febre ou sensação de febre alta. | `febre`, `febril`, `temperatura alta`, `calafrio*` | começou com febre à tarde | tem regra de gravidade (24h ou 192) (grav_febre) |
| `vomito` | Vômito. | `vomito`, `vomitou`, `vomitando`, `vomitar`, `botou pra fora`, `colocou pra fora` | vomitou duas vezes hoje | tem regra de gravidade (24h ou 192) (grav_vomito_diarreia, obs_sintomas_leves) |
| `diarreia` | Fezes líquidas ou muito soltas. | `diarreia*`, `fezes soltas`, `intestino solto`, `caganeira` | está com diarreia há 3 dias | tem regra de gravidade (24h ou 192) (grav_vomito_diarreia, obs_sintomas_leves) |
| `nao_esta_urinando` | Está urinando muito pouco ou nada. | `nao esta urinando`, `nao urina`, `nao fez xixi`, `sem urinar` | não está urinando desde ontem | tem regra de gravidade (24h ou 192) (grav_vomito_diarreia) |
| `recusa_liquidos` | Não quer beber água ou líquidos. | `nao quer beber agua`, `recusa liquidos`, `nao esta bebendo`, `nao aceita agua`, `nao quer tomar agua` | não quer beber água | tem regra de gravidade (24h ou 192) (grav_vomito_diarreia) |
| `dor` | Dor em qualquer parte do corpo (a intensidade vai em `intensidade`). | `dor`, `dores`, `doendo`, `doi`, `dorzinha`, `dolorido`, `dolorida` | reclama de dor na perna | tem regra de gravidade (24h ou 192) (grav_dor_forte, obs_sintomas_leves) |
| `dor_de_cabeca` | Dor de cabeça comum. | `dor de cabeca`, `dor na cabeca`, `cabeca doendo`, `cefaleia`, `enxaqueca` | dor de cabeça desde cedo | tem regra de gravidade (24h ou 192) (grav_dor_cabeca_subita, obs_sintomas_leves) |
| `pior_dor_de_cabeca` | A pior dor de cabeça da vida, súbita e fortíssima. | `pior dor de cabeca`, `a pior dor`, `dor de cabeca fortissima`, `nunca sentiu igual`, `dor de cabeca mais forte`, `martelada` | disse que é a pior dor de cabeça da vida | tem regra de gravidade e também dispara o alarme 192 (grav_sinais_avc) |
| `boca_torta` | Boca ou rosto torto ou caído de um lado. | `boca % torta`, `boca % entortou`, `rosto % torto`, `rosto % caido`, `boca % caida`, `boca caiu`, `cara % torta`, `face assimetrica` | a boca dela entortou | tem regra de gravidade e também dispara o alarme 192 (grav_sinais_avc) |
| `inchaco` | Inchaço, principalmente nas pernas (uma só, com dor ou vermelhidão, é mais grave). | `inchaco*`, `inchada`, `inchado`, `inchou`, `edema` | a perna está inchada | tem regra de gravidade (24h ou 192) (grav_inchaco) |
| `cansaco` | Cansaço ou falta de energia. | `cansaco`, `cansad*`, `canseira`, `fadiga` | está muito cansada | tem regra de gravidade (24h ou 192) (obs_sintomas_leves) |
| `falta_de_apetite` | Sem vontade de comer. | `falta de apetite`, `sem apetite`, `nao quer comer`, `nao esta comendo`, `inapetencia`, `sem fome` | está sem apetite | tem regra de gravidade (24h ou 192) (obs_sintomas_leves) |
| `sonolencia_excessiva` | Muito sonolento, dorme o dia todo ou é difícil de acordar. | `sonolencia excessiva`, `muito sonolent*`, `dormindo o dia todo`, `dificil de acordar`, `nao acorda direito`, `dormindo o dia inteiro`, `dorme o dia todo`, `dorme o dia inteiro`, `dificil acordar`, `muito dificil acordar` | está difícil de acordar | tem regra de gravidade (24h ou 192) (grav_sonolencia_excessiva) |
| `engasgo` | Engasgo com comida ou líquido. | `engasg*` | engasgou com a comida | tem regra de gravidade (24h ou 192) (grav_engasgo) |
| `dor_no_peito` | Dor, aperto, peso ou queimação no peito ou no coração. | `dor no peito`, `aperto no peito`, `peito apertado`, `peso no peito`, `dor no coracao`, `dor toracica` | reclama de dor no peito | dispara o alarme 192 pelas regras fixas |
| `falta_de_ar` | Falta de ar, respiração difícil ou sufocamento. | `falta de ar`, `sem ar`, `respiracao dificil`, `dificuldade para respirar`, `ofegante`, `sem folego` | está com falta de ar | dispara o alarme 192 pelas regras fixas |
| `confusao_mental` | Confusão súbita: não sabe onde está, não reconhece pessoas, fala coisas sem sentido, delira. | `confus*`, `desorientad*`, `delirando`, `nao reconhece ninguem`, `fala sem sentido`, `nao sabe onde esta` | ficou confusa de repente | dispara o alarme 192 pelas regras fixas |
| `tosse` | Tosse seca ou com catarro (com sangue é outro termo). | `tosse*`, `tossindo` | está com tosse leve | só registro: sem regra, a conduta padrão é observar |
| `dor_abdominal` | Dor de barriga ou cólica. | `dor de barriga`, `dor na barriga`, `barriga doendo`, `dor abdominal`, `colica` | dor de barriga depois do almoço | só registro: sem regra, a conduta padrão é observar |
| `constipacao` | Intestino preso, sem evacuar há dias. | `constipac*`, `intestino preso`, `prisao de ventre`, `sem evacuar` | está com o intestino preso | só registro: sem regra, a conduta padrão é observar |
| `queda_de_pressao` | Pressão baixa ou que caiu. | `queda de pressao`, `pressao caiu`, `pressao baixa`, `pressao baixou`, `hipotensao` | a pressão baixou hoje | tem regra de gravidade (24h ou 192) (grav_pressao_baixa) |
| `dor_nas_costas` | Dor nas costas ou na lombar. | `dor nas costas`, `costas doendo`, `lombar` | dor nas costas há dois dias | só registro: sem regra, a conduta padrão é observar |

## Sinais (`sinais`)

| Termo | O que é | Formas de falar | Exemplo | Tratamento |
|---|---|---|---|---|
| `bateu_a_cabeca` | Bateu a cabeça (em queda ou pancada). | `bateu a cabeca`, `bateu a nuca`, `bateu a testa`, `pancada na cabeca` | caiu e bateu a cabeça | dispara o alarme 192 pelas regras fixas |
| `fala_enrolada` | Fala enrolada, arrastada ou que ninguém entende. | `fala % enrolada`, `fala % arrastada`, `fala % embolada`, `falando enrolado` | a fala ficou enrolada | tem regra de gravidade e também dispara o alarme 192 (grav_sinais_avc) |
| `rosto_torto` | Rosto ou boca torta ou caída de um lado. | `rosto % torto`, `boca % torta`, `rosto % caido`, `boca % entortou` | o rosto ficou torto | tem regra de gravidade e também dispara o alarme 192 (grav_sinais_avc) |
| `fraqueza_de_um_lado` | Fraqueza ou braço/perna sem força de um lado só. | `fraqueza de um lado`, `lado % sem forca`, `braco % caido`, `braco % mole` | o lado direito está sem força | tem regra de gravidade e também dispara o alarme 192 (grav_sinais_avc) |
| `dormencia_subita` | Dormência ou formigamento de repente, em um lado do corpo. | `dormencia subita`, `dormente de repente`, `formigamento no braco`, `lado dormente` | o braço ficou dormente de repente | tem regra de gravidade (24h ou 192) (grav_sinais_avc) |
| `perda_de_visao` | Perdeu a visão de um olho, ficou escuro ou dobrado de repente. | `perda de visao`, `perdeu a visao`, `perdeu a vista`, `vista escureceu`, `enxergando dobrado`, `visao dupla` | perdeu a visão de um olho | tem regra de gravidade (24h ou 192) (grav_sinais_avc) |
| `desequilibrio_subito` | Perdeu o equilíbrio de repente, cambaleando, não para em pé. | `desequilibrio subito`, `cambaleando`, `nao para em pe`, `perdeu o equilibrio` | perdeu o equilíbrio de repente | tem regra de gravidade (24h ou 192) (grav_sinais_avc) |
| `inicio_subito` | Começou de repente, do nada. | `de repente`, `do nada`, `subitamente`, `de uma hora pra outra` | começou do nada | tem regra de gravidade (24h ou 192) (grav_dor_cabeca_subita) |

## Intensidade (`intensidade`)

| Termo | O que é | Formas de falar | Exemplo | Tratamento |
|---|---|---|---|---|
| `forte` | Intensidade forte. | `forte`, `fortissim*`, `insuportavel`, `intensa`, `intenso`, `muita dor`, `demais`, `nunca sentiu igual`, `de gritar`, `jorrando` | a dor está muito forte | tem regra de gravidade (24h ou 192) |
| `moderada` | Intensidade moderada. | `moderad*`, `meio forte`, `incomoda bastante`, `varias vezes`, `muitas vezes`, `toda hora`, `nao para de`, `sem parar`, `perdi a conta`, `nao segura nem agua`, `nao consegue segurar` | a dor é moderada | tem regra de gravidade (24h ou 192) |
| `leve` | Intensidade leve. | `leve`, `levinha`, `levinho`, `dorzinha`, `um pouco`, `pouquinho`, `fraquinha` | uma dor leve | tem regra de gravidade (24h ou 192) |

## Pendente de validação (DA-D4)

- **Revisão humana:** tudo aqui é rascunho de LLM (`conferencia = llm`). Ver `revisao-humana.md`.
- **Conferência com o Diário real:** quando B ligar o Diário à OpenAI, rodar `dados/testes/test_relatos_e2e.py`
  com a chave configurada: ele compara a conduta de ponta a ponta e lista os termos que o Diário devolveu
  fora deste vocabulário.
