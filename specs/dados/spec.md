# Spec — dados

> **Dono:** Pessoa C (Roberto) · **Status:** 🟡 escrita em 23/10/2026 a partir de D7, D15.2, D15.4 e D16. Os padrões marcados com **(DA-Dn)** valem até resposta em contrário na [`discussao.md`](discussao.md).
> Regras gerais e contratos (C2, C3, C4, C8): [`00-projeto/spec.md`](../00-projeto/spec.md). Corte regional × final: [`escopo-por-fase.md`](../00-projeto/escopo-por-fase.md).
> **Atualização de 24/10/2026** (pedido do usuário, escrita por B): modelos da OpenAI no lugar dos locais (D3) e funcionalidades E1, E2, E4 e E8 (D23). As partes novas estão marcadas com **(24/10)**. **C revisa** e ajusta os detalhes de implementação.

---

## 1. Escopo

**Regional:** as ferramentas de dados que o harness chama, todas **determinísticas** (sem modelo em tempo de execução):

| Ferramenta | Contrato | O que faz |
|---|---|---|
| `normalizar` | C2 | Nome comercial → princípio ativo e concentração, para **~20 remédios** (D16) |
| `checar_lista` | C3 | Mesmo princípio ativo em nomes diferentes + tabela curada (interações, duplicidade de classe, CBMPI) |
| `detectar_alarme` | C4 | Sinal de alarme no texto → `ligue_192` |
| `avaliar_gravidade` | C4 | Sintoma estruturado → conduta (192, 24h, observar) |
| `info_remedio` **(24/10)** | C8 | Princípio ativo → para que serve (E8), Farmácia Popular (E4), tipo e validade da receita (E4) |

**Final:** base de interações completa e licenciada, conversão de nomes PT → internacional em escala, CBMPI completo + Beers, RAG em bulas, efeito adverso × sintoma, revisão por profissional.

## 2. Como as tabelas são feitas no regional

- **Lista de remédios:** ~20 remédios comuns em idosos, escolhidos por C (D7.1). A lista final fica registrada na DA-D1. Os remédios da demo saem dela.
- **Tabelas clínicas** (interações, classes, CBMPI, sinais de alarme, regras de gravidade): **geradas com ajuda de um LLM e conferidas com LLM** (D7.2, D15.4). O objetivo do regional é o sistema funcionar corretamente na demo, sem aprofundar a curadoria.
- Para não esconder isso, toda linha clínica tem as colunas `fonte` (a referência indicada na geração, ex.: bula, DDInter, CBMPI) e `conferencia` = `llm`. Na final, a conferência por profissional muda a coluna para `profissional`.
- O registro de como foi feito (qual LLM, data, prompt usado) fica em `dados/tabelas/LEIAME.md`.

## 3. Estrutura de `dados/`

```
dados/
├── brutos/                  ← download da CMED (fora do Git; baixado pelo script)
├── etl/cmed.py              ← extrai os ~20 remédios da tabela da CMED
├── tabelas/                 ← CSV versionados (UTF-8, separador vírgula)
│   ├── remedios.csv
│   ├── sinonimos.csv
│   ├── interacoes.csv
│   ├── classes.csv
│   ├── cbmpi.csv
│   ├── sinais_alarme.csv
│   ├── regras_gravidade.csv
│   ├── indicacoes.csv           ← (24/10) para que serve
│   ├── farmacia_popular.csv     ← (24/10)
│   ├── tipos_receita.csv        ← (24/10) validade por tipo de receita
│   └── LEIAME.md
├── texto.py                 ← normalização de texto (minúsculo, sem acento, sem pontuação extra)
├── normalizador.py          ← normalizar (C2)
├── farmacovigilante.py      ← checar_lista (C3)
├── gravidade.py             ← detectar_alarme e avaliar_gravidade (C4)
├── info_remedio.py          ← info_remedio (C8, 24/10)
├── validar_tabelas.py       ← confere colunas, valores e referências entre tabelas
└── testes/
```

## 4. Tabelas

| Arquivo | Colunas |
|---|---|
| `remedios.csv` | `principio_ativo`, `nome_comercial`, `concentracao`, `forma`, `registro_anvisa`, `fonte` (CMED + data do arquivo) |
| `sinonimos.csv` | `termo` (ex.: "aas", "glifage"), `principio_ativo` |
| `interacoes.csv` | `principio_a`, `principio_b`, `gravidade` (alta/moderada/baixa), `descricao` (frase simples em português), `fonte`, `conferencia` |
| `classes.csv` | `principio_ativo`, `classe`, `duplicidade_relevante` (sim/não), `fonte`, `conferencia` |
| `cbmpi.csv` | `principio_ativo`, `criterio`, `motivo` (frase simples), `fonte`, `conferencia` |
| `sinais_alarme.csv` | `regra_id`, `padrao` (expressão regular sobre o texto normalizado), `descricao`, `fonte`, `conferencia` |
| `regras_gravidade.csv` | `regra_id`, `ordem`, `condicao` (sintomas e sinais), `nivel` (ligue_192/atendimento_24h/observar), `motivo`, `fonte`, `conferencia` |
| `indicacoes.csv` **(24/10)** | `principio_ativo`, `para_que_serve` (frase simples de uso comum, sem verbo no imperativo: "controlar a pressão alta"), `fonte` (bula), `conferencia` |
| `farmacia_popular.csv` **(24/10)** | `principio_ativo`, `concentracao`, `indicacao_programa`, `gratuito` (sim/não), `documentos` (separados por `;`), `fonte` (página oficial do programa + data da consulta), `conferencia` |
| `tipos_receita.csv` **(24/10)** | `tipo_receita` (simples/controle_especial/antimicrobiano), `validade_dias`, `fonte`, `conferencia`; e `remedios.csv` ganha a coluna `tipo_receita` |

Regras: todo `principio_ativo` citado nas tabelas clínicas existe em `remedios.csv`; princípios em minúsculo e sem acento; pares de `interacoes.csv` em ordem alfabética, sem repetição. `validar_tabelas.py` falha se alguma regra for quebrada.

## 5. `normalizar` (C2)

1. Normaliza o texto de entrada e extrai a **concentração** por expressão regular (`\d+([.,]\d+)?\s*(mg|mcg|g|ml|ui|%)`, incluindo "mg/ml").
2. Remove palavras de forma e embalagem ("comprimido", "cp", "caixa com", "revestido"…).
3. Procura, nesta ordem: `sinonimos.termo` exato → `nome_comercial` exato → `principio_ativo` exato → **aproximado** (rapidfuzz, nota ≥ 85).
4. Uma correspondência → `encontrado = True`. Várias com nota próxima (diferença < 5) → `encontrado = False` e `candidatos` preenchidos. Nenhuma → `encontrado = False`.
5. Associações (ex.: losartana + hidroclorotiazida) devolvem os dois princípios.

## 6. `checar_lista` (C3)

Para a lista recebida (itens com `item_id` e `principio_ativo`):

1. **Duplicidade de princípio:** o mesmo princípio em 2+ itens → `duplicidade_principio`, gravidade alta.
2. **Interações:** cada par de princípios da lista consultado em `interacoes.csv` → `interacao`.
3. **Duplicidade de classe:** 2+ princípios diferentes da mesma `classe` com `duplicidade_relevante = sim` → `duplicidade_classe`.
4. **CBMPI:** cada princípio presente em `cbmpi.csv` → `cbmpi`.
5. Saída ordenada por gravidade (alta → baixa → sem gravidade), sem alertas repetidos. Cada `Alerta` leva `fonte` e `conferencia` da linha de origem.

## 7. `detectar_alarme` e `avaliar_gravidade` (C4)

### 7.1 Sinais de alarme (regra fixa, visão §2.3 item 4)

No mínimo, os quatro sinais do guardrail, com as variações de fala mais comuns:

| `regra_id` | Sinal | Exemplos de variação |
|---|---|---|
| `alarme_queda_cabeca` | Queda com batida na cabeça | "caiu e bateu a cabeça", "bateu com a cabeça", "levou um tombo e bateu a cabeça" |
| `alarme_dor_peito` | Dor no peito | "dor no peito", "aperto no peito", "dor forte no peito" |
| `alarme_falta_ar` | Falta de ar | "falta de ar", "não consegue respirar", "respirando com dificuldade", "sem ar" |
| `alarme_confusao` | Confusão súbita | "ficou confuso de repente", "não reconhece ninguém", "falando coisa sem sentido" |

C pode acrescentar sinais, sempre com `fonte` e `conferencia`.

- Busca sobre o texto normalizado. **Negação** ("não teve dor no peito"): tratamento conforme **DA-D2** (padrão: **conservador**, ou seja, na dúvida dispara o 192; o falso alarme é aceito em troca de não perder um alarme verdadeiro).
- Retorna a `Conduta` com `nivel = "ligue_192"`, o `regra_id` e o motivo, ou `None`.

### 7.2 Regras de gravidade

- Entrada: `SintomaEstruturado`. Primeiro reaplica os sinais de alarme sobre `descricao` e `sinais`.
- Depois percorre `regras_gravidade.csv` pela `ordem`; a primeira regra que casa define a conduta.
- Nenhuma regra casou → `observar` com `regra_id = "padrao_observar"`.

## 7a. `info_remedio` (C8, 24/10)

1. Busca o `principio_ativo` em `indicacoes.csv`, `farmacia_popular.csv` e, pelo `tipo_receita` de `remedios.csv`, em `tipos_receita.csv`.
2. Monta o `InfoRemedio` (00-projeto/spec §5.1). Sem linha em `indicacoes.csv` → devolve `None` (o harness diz "ainda não tenho essa informação").
3. `farmacia_popular = True` só se houver linha com `gratuito = sim` para o princípio (e a concentração, se a tabela tiver).
4. A lista do Farmácia Popular e as regras de receita mudam com o tempo: a data da consulta à fonte oficial vai na coluna `fonte` e em `LEIAME.md`.

## 8. Testes

- `normalizar`: cada um dos ~20 remédios por nome comercial, por princípio, com erro de digitação leve e com concentração; nome desconhecido.
- `checar_lista`: pelo menos um caso de cada tipo de alerta e uma lista sem alertas.
- `detectar_alarme`: todas as variações da tabela do §7.1 e frases sem alarme.
- `info_remedio`: os ~20 remédios têm `para_que_serve`; um com e um sem Farmácia Popular; princípio desconhecido → `None`.
- `validar_tabelas.py` roda junto com os testes (inclusive as tabelas novas).
