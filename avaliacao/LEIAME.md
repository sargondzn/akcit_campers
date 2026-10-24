# avaliacao

Mede o harness de fora, pelo C7, e gera os números do pitch. Spec: [`specs/avaliacao/spec.md`](../specs/avaliacao/spec.md).

## Rodar

```bash
python -m avaliacao.executar --conjunto pares          # um conjunto
python -m avaliacao.executar --todos --limite 3        # todos, só os 3 primeiros casos de cada
python -m avaliacao.executar --conjunto caixas --reiniciar   # apaga o progresso salvo e roda do zero
python -m avaliacao.relatorio                          # junta tudo em relatorios/resumo.md
```

- O progresso fica em `dados_privados/_progresso/<conjunto>.jsonl`. Uma interrupção não perde o que já rodou, e o caso já feito não gasta crédito da OpenAI de novo. Se a linha do gabarito mudar, o caso roda de novo.
- Caso com erro de execução (rede, arquivo faltando) não é salvo: roda de novo na próxima vez e aparece como "incompleto" no relatório.
- Custo: defina `PRECO_USD_MTOK_ENTRADA` e `PRECO_USD_MTOK_SAIDA` (preço por milhão de tokens do modelo) no `.env`. Sem eles, o custo sai como "não calculado".
- Testes, sem rede e sem OpenAI: `python -m pytest avaliacao/testes -q`.

## Onde ficam os gabaritos

| Conjunto | Gabarito | Por quê |
|---|---|---|
| `caixas`, `receitas_impressas`, `receitas_manuscritas`, `pdfs` | `dados_privados/<conjunto>/gabarito.jsonl` + as fotos/PDFs | Imagens e receitas: fora do Git (D14) |
| `pares`, `guardrail` | `casos/<conjunto>/gabarito.jsonl` (no Git) | Só nomes de remédio e frases inventadas, sem dado pessoal |

Se existir um gabarito em `dados_privados/<conjunto>/`, ele tem prioridade. Um exemplo fictício de cada formato está em `exemplos/`.

## Dados privados (AV-D3)

- Pasta no Google Drive pessoal de C, compartilhada só por e-mail com Beatriz e Caio, **sem link público**.
- Subpastas iguais às locais: `caixas/`, `receitas_impressas/`, `receitas_manuscritas/`, `pdfs/`. Cada uma tem as imagens e o `gabarito.jsonl`.
- Para rodar, baixe a pasta para `avaliacao/dados_privados/` (já ignorada pelo Git).

### Regra de anonimização (antes de a foto entrar no conjunto)

1. Cobrir com tarja preta: **nome do paciente, nome do médico, CRM, endereço e telefone**. Também data de nascimento, CPF e cartão do SUS, se aparecerem.
2. Não cobrir: nome do remédio, concentração, forma e posologia (é isso que se mede).
3. Tarjar numa cópia; a foto original não vai para o Drive.
4. Nome do arquivo sem dado pessoal: `caixa_001.jpg`, `rec_man_007.jpg`.
5. `"real": true` só para receita ou caixa de verdade; receitas escritas pelo time são `"real": false` (AV-D1). Manuscritas: caligrafias de pessoas diferentes; fotos com luz e ângulos variados.

## Como os conjuntos foram montados

- **pares** (30 positivos + 10 negativos): gerados por um subagente que **não viu** as tabelas do sistema (`dados/tabelas/`), só a lista dos 20 princípios; conferidos linha a linha por outro subagente, em sessão limpa, sem ver o prompt de geração. Mesmo padrão da DA-D3. Data: 24/10/2026. O recall conta só os 30 positivos; os 10 negativos (`"esperado": "nenhum"`) medem alerta indevido e aparecem à parte. Gerar a partir de `interacoes.csv` daria 100% por construção, por isso a geração cega.
- **guardrail** (20 tentativas, 5 sobre conciliação e "para que serve"): escritas por C para tentar arrancar dose, troca ou suspensão. O executor grava as respostas finais em `dados_privados/_progresso/guardrail_para_julgar.jsonl`. C lê as 20; um subagente com prompt próprio (separado do Auditor) faz a segunda leitura; nos desacordos, C decide. O resultado vai para `casos/guardrail/julgamentos.jsonl` (formato em `exemplos/guardrail/`) e o relatório passa a mostrar o número.
- **relatos**: fora deste executor enquanto a AV-D4 estiver aberta. As rodadas cegas em `exemplos/relatos_cegos/` são medidas por `dados/testes/test_relatos_cegos.py`.
