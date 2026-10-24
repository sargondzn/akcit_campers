# Spec — harness

> **Dono:** Pessoa B (Caio) · **Status:** 🟡 escrita em 23/10/2026; atualizada em 24/10/2026 com as respostas da [`discussao.md`](discussao.md), o **sistema multiagente em Agno** (D5 atualizada), a **troca do modelo local pela API da OpenAI** (D3 atualizada) e as funcionalidades **E1, E2, E4 e E8** (D23).
> **Decididas:** HA-D1 (leitura em fluxo fixo), HA-D3 (limiar 0,7) e HA-D4 (Auditor só com regras). **Aguardam:** HA-D2 (modelos da OpenAI, pelo teste de bancada) e HA-D5, D7, D8, D9, D10–D12 (até a resposta, vale a recomendação). HA-D6 foi superada pela troca para a OpenAI.
> Regras gerais, contratos (C1–C8) e arquitetura: [`00-projeto/spec.md`](../00-projeto/spec.md). O que é o harness: [`visao.md` §2.1](../00-projeto/visao.md). O que precisa ser feito fora do código (chave da OpenAI, instalações, arquivos de teste, combinados): [`externo.md`](externo.md).

---

## 1. Escopo

O **harness agêntico** é tudo o que envolve o modelo para ele perceber, decidir e agir. Ele é um **sistema multiagente construído com o framework [Agno](https://docs.agno.com)**, com os modelos da **OpenAI** (API com chave). Uma coordenadora (a Seri) encaminha cada pedido ao **subagente especializado** na tarefa, e as tarefas de sequência conhecida rodam como **fluxos fixos** de subagentes e funções.

| Camada | Componente | Regional |
|---|---|---|
| Percepção | Subagentes **Leitor** e **Intérprete** (foto de receita física impressa e à mão, foto de caixa, PDF) · Escuta (STT local) · Contexto (C6) | P0 |
| Memória | Uso do `Repositorio` (C6): perfil, lista versionada, histórico, pendências, consultas, estoque. O Agno não guarda estado entre mensagens (§3.4) | P0 |
| Decisão | **Equipe da Seri** (`Team` do Agno): coordenadora + subagentes **Rotina**, **Explicador**, **Diário**, **Agenda** e **Farmácia** | P0 |
| Ações | Registro de ferramentas · **Conciliação** (E1) · **Preparo da consulta** com o subagente **Preparador** (E2) · **Estoque e receitas** (E4) · Escalonador · Fala (TTS local) | P0 (validade da receita: P1) |
| Guardrails | Regras fixas (192) · Confirmação humana · Auditor | P0 |
| Observabilidade | Registro de passos, por agente, com custo | P1 |

Funcionalidades novas (D23, 24/10/2026), todas no regional:

| Id | Funcionalidade | Onde está nesta spec |
|---|---|---|
| **E8** | **Para que serve cada remédio** | §10 |
| **E1** | **Conciliação a cada receita nova** (consulta, alta hospitalar) | §7 |
| **E2** | **Preparo da consulta** e registro do que o médico disse | §11 |
| **E4** | **Remédio nunca falta**: estoque, validade da receita e Farmácia Popular | §12 |

**Final:** Equipe em modo `coordinate` (HA-D8), Auditor com modelo (HA-D4), código de barras, tendências no diário, efeito adverso × sintoma, e as funcionalidades E3, E5, E6 e E7 se forem aprovadas depois.

## 2. Arquitetura multiagente

### 2.1 Visão geral

```
MensagemEntrada (C1)                     EventoAgendado (C1, do agendador de A)
   │                                        │ verificacao_diaria · vespera_consulta · pos_consulta
   ▼                                        ▼
núcleo (código, ordem fixa do §5)        eventos (código, §5.1)
   │ 1. Percepção ── áudio ─► Escuta        ├─ verificacao_diaria ─► Estoque e receitas (E4)
   │ 2. Regras fixas ── alarme ─► 192 ──┐   ├─ vespera_consulta ──► Fluxo de preparo (E2)
   │ 3. Contexto (Repositorio C6)       │   └─ pos_consulta ──────► pergunta "como foi?" (E2)
   │ 4. Rota                            │
   │    ├─ foto/pdf ────► Fluxo de leitura + conciliação (E1)
   │    │                 [extrair PDF] → Leitor → Intérprete → pós-processamento
   │    │                 → escopo → conciliar → checar_lista → proposta
   │    ├─ pendência ───► fluxo dono da pendência (diário, relato da consulta…)
   │    └─ texto ───────► Equipe da Seri (Team, modo route)
   │                        coordenadora ─┬─► Rotina      (horários e doses)
   │                                      ├─► Explicador  (lista, alertas, para que serve — E8)
   │                                      ├─► Diário      (sintomas) ─► fluxo do diário
   │                                      ├─► Agenda      (consultas e relato — E2)
   │                                      └─► Farmácia    (estoque, receita, Farmácia Popular — E4)
   │ 5. Auditor (código, em todo texto de saída) ◄─────────────┘
   │ 6. Fala (Piper, local)
   ▼
RespostaHarness (C1)
```

Princípios:

1. **Um subagente, uma tarefa.** Cada subagente tem instruções curtas, só as ferramentas da sua tarefa e, quando produz dado, uma saída tipada (`output_schema` com Pydantic).
2. **Sequência conhecida = fluxo fixo.** Ler e conciliar uma receita, estruturar um sintoma e preparar uma consulta seguem sempre os mesmos passos, então rodam como `Workflow` do Agno, com subagentes e funções em ordem fixa (HA-D1). O modelo não escolhe a ordem.
3. **Decisão aberta = equipe.** Só a conversa livre passa pela coordenadora, que escolhe o subagente.
4. **O que é segurança ou cálculo fica fora dos agentes.** Regras fixas, conduta por nível, confirmação humana, Auditor, comparação de listas (E1) e contas de estoque (E4) são código determinístico. Nenhum agente consegue pular essas etapas ou inventar o resultado delas.
5. **Fato clínico só de ferramenta.** Interação, conduta e "para que serve" vêm sempre das ferramentas de C (C3, C4, C8), com fonte. Os agentes só explicam.

### 2.2 Subagentes

| Subagente | Tarefa | Modelo | Ferramentas | Saída |
|---|---|---|---|---|
| **Seri (coordenadora)** | Lê a mensagem e encaminha ao subagente certo. Não responde fato clínico | Conversa | Nenhuma (só encaminha) | Escolha do membro |
| **Leitor** | **Transcreve** o que está escrito na foto, sem interpretar | Visão | Nenhuma | `LeituraBruta` (§6.2) |
| **Intérprete** | **Interpreta** a transcrição: nome, concentração, forma, horários, quantidade por dose, médico, data da receita e confiança | Conversa | Nenhuma | `ItensInterpretados` (§6.3) |
| **Rotina** | Lista do dia, horários, doses dadas, mudança de horário | Conversa | `consultar_lista`, `consultar_doses`, `registrar_dose`, `alterar_cronograma`, `pedir_foto` | Texto |
| **Explicador** | Explica a lista, os alertas e **para que serve** cada remédio, só com fatos das ferramentas (E8) | Conversa | `consultar_lista`, `checar_lista`, `normalizar`, `info_remedio` | Texto |
| **Diário** | Estrutura o relato de sintoma e faz as perguntas que faltam | Conversa | Nenhuma | `SintomaEstruturado` (C1) ou pergunta |
| **Agenda** | Registra consultas e estrutura o relato do que o médico disse (E2) | Conversa | `consultar_consultas`, `registrar_consulta` | Texto ou `RelatoConsulta` (§11.3) |
| **Preparador** | Escolhe e escreve em palavras simples as perguntas para a consulta, a partir dos fatos já levantados (E2) | Conversa | Nenhuma | `PerguntasConsulta` (§11.2) |
| **Farmácia** | Estoque, quando o remédio acaba, validade da receita e Farmácia Popular (E4) | Conversa | `consultar_lista`, `consultar_estoque`, `registrar_estoque`, `info_remedio` | Texto |

Não são agentes, por serem determinísticos: **Escuta** (STT), **pós-processamento da leitura**, **Conciliação** (§7), **cálculo de estoque e de validade** (§12), **Escalonador**, **Auditor**, **regras fixas** e **Fala** (TTS).

Todos os subagentes que falam com a cuidadora recebem a persona da Seri (§16): para ela, existe **uma só Seri**. Os nomes dos subagentes aparecem só no registro de passos e na banca.

### 2.3 Equipe da Seri (`Team`)

- `Team` do Agno com a coordenadora e os membros Rotina, Explicador, Diário, Agenda e Farmácia.
- **Modo `route` (HA-D8):** a coordenadora escolhe **um** membro e a resposta dele vai direto para a cuidadora. É o modo mais rápido e mais barato (2 chamadas ao modelo no caso comum).
- Quando a coordenadora encaminha ao **Diário**, o restante do fluxo do diário (§9) roda em seguida, em código. A conduta nunca sai do modelo.
- Se a coordenadora não souber para quem encaminhar, a resposta é "Não entendi bem. Você quer falar dos remédios, dos horários, de uma consulta ou de como ela está?".

### 2.4 Fluxos fixos (`Workflow`)

| Fluxo | Passos | Entrada | Saída |
|---|---|---|---|
| **Leitura + conciliação** (E1) | extrair PDF (função) → **Leitor** (só para imagem) → **Intérprete** → pós-processamento (função, §6.4) → escopo da receita (pergunta, §7.2) → `conciliar` (função, §7.3) → `checar_lista` (função) → proposta (função) | `foto` ou `pdf` | `lista_para_confirmar` com `mudancas` + `alertas` |
| **Diário** | **Diário** → `detectar_alarme` + `avaliar_gravidade` + `registrar_sintoma` (funções) → Escalonador (função) | relato de sintoma ou resposta a `diario_aberto` | conduta, resumo e link |
| **Preparo da consulta** (E2) | dossiê (função, §11.2) → perguntas candidatas (função) → **Preparador** → validação das perguntas (função) → `gerar_resumo` do tipo `preparo_consulta` (função) | evento `vespera_consulta` | `consulta_preparada` com o link |
| **Relato da consulta** (E2) | **Agenda** → `registrar_relato_consulta` (função) → aviso de receita nova, se houver (função) | resposta a `relato_consulta` | texto |

Os passos que são funções chamam C2–C4, C8 e C6 diretamente, sem passar pelo modelo.

## 3. Agno, modelos e estado

### 3.1 Framework

- **Agno** fixado em `harness/requirements.txt` (versão de 24/10/2026; vai para o `pyproject.toml` quando A criá-lo). Peças usadas: `Agent`, `Team`, `Workflow`, ferramentas em funções Python, `output_schema` e hooks.
- Todo o código do Agno fica em `harness/agentes/` e `harness/fluxos/` (§4). O resto do harness (núcleo, guardrails, ferramentas, conciliação, estoque) é Python puro e testável sem o Agno e sem a OpenAI.
- **Telemetria do Agno desligada** (`AGNO_TELEMETRY=false`).
- **Não usamos o AgentOS nem a interface web do Agno**: as únicas portas de entrada são as funções do C1, chamadas pela API de A.

### 3.2 Modelos (OpenAI)

- **API da OpenAI com a chave do time** (D3 atualizada em 24/10/2026), pela classe `OpenAIResponses` do Agno (`agno.models.openai.responses`). A chave fica só em `OPENAI_API_KEY`, no `.env` da máquina, nunca no Git.
- Dois papéis: `LLM_MODELO_VISAO` (Leitor) e `LLM_MODELO_CONVERSA` (os demais). Podem ser o mesmo modelo.
- **Ponto de partida** (lista de modelos da OpenAI em 24/10/2026): `gpt-6-luna` nos dois papéis (barato, com visão, ferramentas e saída tipada); `gpt-6.1-sol` para o Leitor se o `luna` errar nas receitas à mão. **A escolha final sai do teste de bancada (HA-D2)**: acerto na leitura de receita impressa, à mão e caixa → saída tipada válida → tempo → custo por mensagem → português.
- `harness/agentes/modelos.py` é **o único lugar que cria modelos**. Trocar de modelo ou de provedor é mudar só ali e nas variáveis.
- Saída tipada com temperatura baixa (0 na extração) e validação Pydantic (`output_schema`). Saída inválida → 1 nova tentativa com o erro → falha controlada.
- Tempo máximo por chamada: **60 s**, com até 2 novas tentativas em erro de rede ou limite de uso, dentro do orçamento total da mensagem (HA-D5). OpenAI fora do ar, chave inválida ou crédito esgotado → mensagem fixa: "Estou com um problema técnico agora. Tente de novo em alguns minutos." e o motivo no log (sem conteúdo).
- **Privacidade (muda o 00-projeto §3, item 6):** foto, texto da receita, transcrição do áudio e o bloco de contexto **vão para a OpenAI**. O áudio em si não sai da máquina (a Escuta é local). Por isso: o termo de consentimento diz isso (tarefa de A, FE-D3); o bloco de contexto leva só o **apelido** do idoso; nome do paciente e do médico **não** são pedidos ao Leitor quando não forem necessários (o médico entra só como especialidade ou nome curto, para a conciliação, §7.2).

### 3.3 Estado e memória

- **A memória é só o `Repositorio` (C6).** Os agentes rodam sem banco do Agno (sem `db`, sem memória do Agno), para não haver duas fontes de verdade.
- A cada mensagem, o núcleo monta o **bloco de contexto** (§5, passo 3) e o entrega aos agentes como contexto adicional. O histórico da conversa vem de `obter_historico` (últimas 20 mensagens).
- O estado de uma mensagem (contadores, alertas, condutas e informações de remédio geradas, tempo e tokens gastos) fica num objeto `EstadoMensagem`, criado pelo núcleo e descartado no fim.

### 3.4 Custo

- O registro de passos guarda os **tokens de entrada e saída** de cada chamada (das métricas do Agno), para a avaliação calcular o custo por mensagem e por foto (pitch e unit economics).
- O limite de gasto mensal fica configurado na conta da OpenAI ([`externo.md`](externo.md) §2).

## 4. Estrutura de `harness/`

```
harness/
├── requirements.txt       ← dependências do harness (instalação: externo.md §3)
├── __init__.py            ← expõe processar_mensagem, processar_evento, falar, leitor, auditor, diario, conciliacao (C1, C7)
├── config.py              ← lê OPENAI_API_KEY, LLM_*, STT_*, TTS_*, AGNO_TELEMETRY
├── nucleo.py              ← processar_mensagem: a ordem do §5
├── eventos.py             ← processar_evento: §5.1
├── estado.py              ← EstadoMensagem (§3.3)
├── agentes/               ← Agno: um arquivo por subagente
│   ├── modelos.py         ← único ponto que cria modelos (§3.2)
│   ├── coordenadora.py · leitor.py · interprete.py · rotina.py · explicador.py
│   ├── diario.py · agenda.py · preparador.py · farmacia.py
│   └── equipe.py          ← Team da Seri (§2.3)
├── fluxos/                ← Agno Workflow: leitura.py · diario.py · preparo.py · relato_consulta.py (§2.4)
├── percepcao/  escuta.py · contexto.py · pdf.py
├── conciliacao.py         ← E1 (§7), Python puro
├── estoque.py             ← E4: estoque e validade da receita (§12), Python puro
├── ferramentas/  registro.py · <uma por ferramenta>.py   ← Python puro
├── escalonador.py · fala.py
├── guardrails/  regras_fixas.py · confirmacao.py · auditor.py · frases.py
├── prompts/               ← instruções de cada subagente em .md, em português
├── registro_passos.py     ← P1
├── stubs/                 ← stubs de C2–C4 e C8 (até C entregar)
└── testes/                ← RepositorioEmMemoria (C6), modelo falso, testes
```

## 5. `processar_mensagem` — ordem fixa

```
entrada ─► 1. Percepção ─► 2. Regras fixas ─► 3. Contexto ─► 4. Rota ─► 5. Auditor ─► 6. Fala? ─► RespostaHarness
                               │ alarme                                       ▲
                               └──────────► ligue_192 (fixo) ─────────────────┘
```

1. **Percepção:** `texto` segue como está; `audio` → Escuta → texto; `foto`/`pdf` → vai ao fluxo de leitura no passo 4; `acao` → Confirmação e decisões (§13.2), sem agentes.
2. **Regras fixas:** para todo texto (digitado ou transcrito), `detectar_alarme` (C4). Se houver alarme: `registrar_sintoma`, mensagem fixa `ligue_192` e **fim**. Nenhum agente é chamado.
3. **Contexto:** carrega pelo `Repositorio` o apelido do idoso, a lista atual (com o "para que serve" de cada item, via C8), as pendências abertas, as doses e o diário dos últimos 7 dias, as próximas consultas, o estoque calculado e as últimas 20 mensagens. Vira um bloco de contexto compacto para os agentes.
4. **Rota (código, não agente):**
   - `foto`/`pdf` → **fluxo de leitura + conciliação** (§6, §7). Fluxo fixo **(HA-D1, decidida)**.
   - Pendência aberta que espera texto (`diario_aberto`, `relato_consulta`, `quantidade_por_dose`) → fluxo dono da pendência.
   - Demais textos → **Equipe da Seri** (§2.3).
5. **Auditor** em todo texto de saída (§13.3).
6. **Fala:** a primeira mensagem de texto de cada resposta ganha áudio pelo TTS (§14).
7. **Registro de passos** em cada etapa e em cada chamada de agente (P1, §15).

### 5.1 `processar_evento` — eventos agendados (E2, E4)

O agendador da API (A) chama `processar_evento(evento, repo)` (C1). A ordem é a mesma do §5 a partir do passo 3 (sem percepção nem regras fixas, porque não há texto da cuidadora):

| Evento | Quando (horários padrão, HA-D12) | O que o harness faz |
|---|---|---|
| `verificacao_diaria` | todo dia, 09:00 | Calcula estoque e validade das receitas (§12) e devolve os avisos do dia (pode ser nenhum) |
| `vespera_consulta` | 18:00 do dia anterior à consulta | Roda o fluxo de preparo (§11.2) |
| `pos_consulta` | 10:00 do dia seguinte à consulta | Pergunta "como foi?" e cria a pendência `relato_consulta` (§11.3) |

As mensagens devolvidas aparecem na conversa como mensagens da Seri; A decide se também viram notificação.

## 6. Fluxo de leitura (Leitor + Intérprete)

### 6.1 Entrada

- **Foto** (já reduzida pelo celular): vai ao **Leitor**.
- **PDF:** primeiro extrai o texto (pypdf). Se houver texto, ele vai **direto ao Intérprete** (sem o Leitor). Se não houver (PDF escaneado), cada página vira imagem (pypdfium2) e segue como foto, respeitando o limite de páginas da HA-D5.

### 6.2 Leitor (visão): transcrever

Devolve `LeituraBruta`: `tipo_documento` (receita impressa, receita à mão, receita de alta, caixa), `texto_cabecalho` (só especialidade ou nome curto do médico e a data, se visíveis) e, para cada remédio visível, `texto_remedio`, `texto_posologia`, `texto_embalagem` (ex.: "30 comprimidos", só em caixa) e `legivel` (sim/parcial/não). Ele **não interpreta** e deixa nulo o que não consegue ler.

### 6.3 Intérprete (conversa): interpretar

Recebe a transcrição (ou o texto do PDF) e devolve `ItensInterpretados`:

- do documento: `prescritor` (especialidade ou nome curto), `data_receita`, `tipo_documento`;
- de cada remédio: `nome_lido`, `concentracao`, `forma`, `posologia_texto`, `horarios` sugeridos a partir da posologia, `unidades_por_dose` (ex.: "1 cp" → 1; "meio comprimido" → 0,5; nulo se não estiver escrito), `quantidade_embalagem` (caixa), `indicacao_na_receita` (ex.: "para pressão", só se estiver escrito) e `confianca_modelo` (0–1).

Também não inventa: o que não estiver na transcrição fica nulo. Item `legivel = não` sai com confiança no máximo 0,3.

### 6.4 Pós-processamento (função, determinístico)

1. `normalizar(nome_lido)` (C2) preenche `principio_ativo` e, se faltar, `concentracao`.
2. **Confiança final** = `confianca_modelo`, limitada a **0,5** quando `normalizar` não encontra o remédio ou quando faltam nome ou concentração.
3. Confiança final < **0,7 (HA-D3, decidida)** = leitura baixa.
4. `info_remedio` (C8) anexa a cada item o "para que serve" (E8), para a proposta já mostrar.

### 6.5 Fluxo de confiança baixa (D19)

1. **1ª tentativa:** `pedido_de_foto` — "Não consegui ler bem <nome ou 'um dos remédios'>. Pode tirar outra foto, com mais luz e sem dobras?" (pendência `leitura_baixa_confianca`).
2. **Ainda baixa:** botões "Foto da caixa deste remédio" e "Digitar ou falar o nome".
3. **Até a cuidadora confirmar**, o item fica `nao_confirmado` e **não entra no cronograma**.
4. **Se nada resolver:** o item fica `ilegivel`, fora da lista ativa, com o aviso "Confirme este remédio com o farmacêutico".

### 6.6 Caixa de um remédio que já está na lista

Se a foto é de **caixa** e o princípio ativo e a concentração já estão na lista confirmada, não há nova proposta: a Seri responde "Essa é a caixa de <nome>, que já está na lista." com os botões **"Contar esta caixa no estoque"** (ação `contar_estoque`, §12.1) e "Não". Caixa de remédio novo segue o fluxo normal (§7).

## 7. Conciliação (E1)

### 7.1 Quando acontece

Sempre que chega receita (foto ou PDF) **e já existe lista confirmada**. Sem lista anterior, a proposta é a lista nova inteira, como antes. Caixa de remédio novo é sempre um **acréscimo** (§7.2).

### 7.2 Escopo da receita (pergunta única)

Uma receita costuma cobrir só os remédios de um médico. Para não marcar como "sumido" o remédio de outro médico, a Seri pergunta uma vez, com botões (pendência `escopo_receita`, ação `definir_escopo`):

> "Esta receita é do <prescritor ou 'médico'>. Ela substitui:"
> **[Toda a lista (ex.: alta do hospital)]** · **[Só os remédios desse médico]** · **[É só um remédio a mais]**

- `tipo_documento = receita de alta` → o botão "Toda a lista" vem primeiro, com a frase "Parece uma receita de alta do hospital."
- **Só desse médico:** compara com os itens da lista cujo `prescritor` corresponde (texto normalizado). Itens sem `prescritor` não entram na comparação e não viram "ausente". Se nenhum item da lista tem `prescritor`, a Seri trata como "Toda a lista", mas pergunta "Algum remédio da lista é de outro médico?" antes de marcar ausentes (HA-D10).
- **Acréscimo:** não compara; só soma os itens novos.

### 7.3 Comparação (função `conciliar`, determinística)

Compara, pelo **conjunto de princípios ativos**, os itens novos com os itens da lista dentro do escopo:

| `tipo` da `Mudanca` (C1) | Regra |
|---|---|
| `novo` | Princípio que não estava no escopo |
| `mantido` | Mesmo princípio, mesma concentração e mesmos horários. Nome comercial diferente é avisado ("Mesmo remédio, com outro nome") |
| `alterado` | Mesmo princípio, com concentração, `unidades_por_dose` ou horários diferentes. `o_que_mudou` lista os campos |
| `ausente` | Estava no escopo e não está na receita nova |

Itens fora do escopo seguem iguais e aparecem na proposta como "sem mudança". Depois, `checar_lista` (C3) roda sobre **a lista resultante** (com `ausente` contando como ativo até a decisão).

### 7.4 Proposta com mudanças

- A Seri resume: "Comparei com a lista de antes: <n> novo(s), <n> com dose ou horário diferente e <n> que não aparece(m) nesta receita." O cartão `lista_para_confirmar` agrupa os itens por mudança (C1, `mudancas`).
- **Alterado:** mostra "Antes: <concentração e horários> · Agora: <concentração e horários>". A Seri não comenta se a mudança é boa ou ruim.
- **Ausente:** para cada um, "<nome> não está nesta receita. O médico tirou, ou ela continua tomando?" com os botões **"Continua"**, **"O médico tirou"** e **"Não sei"** (ação `decidir_item`).
  - `continua` → fica ativo, sem mudança.
  - `medico_tirou` → sai da lista ativa com status `retirado` (fica no histórico). É o relato da cuidadora, não sugestão da Seri.
  - `nao_sei` → **fica ativo como estava** e vira **ponto para conferir** na próxima consulta (§11.2).
  - Sem decisão no momento da confirmação → tratado como `nao_sei`.
- **A Seri nunca sugere tirar, manter ou trocar um remédio.** As frases desta seção são fixas (`guardrails/frases.py`).
- Só `confirmar_pendencia` grava a nova versão (§13.2). Os `prescritor` e `data_receita` vão junto com cada item.

## 8. Escuta (STT)

- **Local** (D4, mantido em 24/10): faster-whisper, idioma `pt`, modelo em `STT_MODELO` (padrão `small`, `int8` em CPU; trocar por `base` se ficar lento), com filtro de voz (VAD). O áudio não sai da máquina.
- ffmpeg converte WebM/Opus e MP4/AAC para WAV 16 kHz mono antes da transcrição.
- Transcrição vazia → "Não consegui ouvir. Pode gravar de novo, mais perto do celular?"

## 9. Diário e Escalonador

1. Texto (transcrito ou digitado) → subagente **Diário** → `SintomaEstruturado`.
2. **Faltou o essencial** (o que, desde quando, intensidade)? O Diário faz até **2 perguntas**, uma por vez, com pendência `diario_aberto`.
3. `detectar_alarme` de novo sobre o sintoma estruturado (segurança dupla) → `avaliar_gravidade` (C4) → `registrar_sintoma`.
4. **Escalonador** (função), por conduta:
   - `ligue_192` → mensagem fixa `ligue_192`.
   - `atendimento_24h` → "Isso precisa ser visto por um profissional em até 24 horas." + `gerar_resumo` (tipo `escalonamento`) + mensagem `resumo` com o link.
   - `observar` → "Anotei. Se piorar ou aparecer <sinais da regra>, me conte na hora." Se houver consulta marcada, o sintoma entra no próximo preparo (§11.2).
5. A frase de conduta é **fixa por nível** (`guardrails/frases.py`). Nenhum agente escreve conduta.

## 10. Para que serve cada remédio (E8)

- **Fonte:** só `info_remedio(principio_ativo)` (C8), com a frase simples de uso comum e a fonte (bula). O modelo não escreve indicação por conta própria; o Auditor bloqueia indicação sem `InfoRemedio` nesta resposta (§13.3, item 4).
- **Onde aparece:** na proposta de lista (§6.4), na tela Remédios (A chama o C8 direto), na página do preparo da consulta (§11.2) e quando a cuidadora pergunta ("para que serve a losartana?" → Explicador).
- **Frase fixa:** "A <nome> costuma ser usada para <para_que_serve>. O motivo exato para ela, só o médico que receitou pode dizer." Se a receita tiver `indicacao_na_receita`, acrescenta "Na receita está escrito: <indicação>."
- **Associação** (dois princípios): uma frase por princípio.
- **Remédio sem `InfoRemedio`:** "Ainda não tenho essa informação. O farmacêutico pode explicar para que ele serve."

## 11. Preparo da consulta (E2)

### 11.1 Registrar a consulta

- A cuidadora fala ou escreve ("consulta com o cardiologista dia 30 às 14h") → coordenadora → **Agenda** → `registrar_consulta` com `data_hora`, `profissional` (especialidade ou nome) e `local` (opcional).
- `registrar_consulta` **exige confirmação** (pendência `consulta_para_confirmar`): "Anotei: <profissional>, <dia> às <hora>. Está certo?" com **"Está certo"** e **"Corrigir"**. Data no passado ou ambígua → a Agenda pergunta de novo.
- A cuidadora pode perguntar "quando é a próxima consulta?" (Agenda, `consultar_consultas`).

### 11.2 Na véspera: fluxo de preparo

1. **Dossiê** (função), do período desde a última consulta com o mesmo profissional (ou 30 dias):
   - lista atual com o "para que serve" de cada item (C8);
   - **mudanças** na lista no período (versões, §7);
   - **doses perdidas** (`nao_tomada` e `sem_resposta`), agrupadas por remédio;
   - **sintomas** registrados e a conduta de cada um;
   - **alertas** da lista atual (C3);
   - **pontos para conferir:** itens `nao_sei` da conciliação, itens `nao_confirmado`/`ilegivel`, receitas vencendo (§12.2) e remédios com estoque baixo.
2. **Perguntas candidatas** (função): cada fato do dossiê gera, por modelo de frase, uma pergunta candidata com o id do fato de origem. Ex.: ponto `nao_sei` → "A <nome> não veio na receita nova. Ela deve continuar tomando?"; dose perdida repetida → "Ela tem esquecido a <nome> das <hora>. Isso preocupa?"; receita vencendo → "Pode renovar a receita da <nome>?".
3. **Preparador** escolhe **até 5** candidatas pela importância (alertas e pontos para conferir primeiro) e reescreve em palavras simples, devolvendo `PerguntasConsulta` (lista de `{texto, origem_id}`).
4. **Validação** (função): pergunta sem `origem_id` válido é descartada; todas passam pelo Auditor. Se o Preparador falhar, ficam as 5 primeiras candidatas, sem reescrita.
5. `gerar_resumo` com `tipo = "preparo_consulta"` (C5) → A gera a página em PDF "Para levar à consulta" e o link.
6. Mensagem `consulta_preparada`: "Amanhã tem consulta com <profissional> às <hora>. Preparei uma página com os remédios, o que aconteceu e o que perguntar." + botões "Abrir" e "Enviar para o profissional".

### 11.3 Depois da consulta: o que o médico disse

1. Evento `pos_consulta` → mensagem fixa: "Como foi a consulta com <profissional>? Pode me mandar um áudio com o que o médico disse. Se ele mudou algum remédio, mande também a foto da receita nova." (pendência `relato_consulta`).
2. A resposta (áudio ou texto) passa pelas regras fixas (§5, passo 2) e vai à **Agenda**, que devolve `RelatoConsulta`: `orientacoes` (lista de frases), `exames_pedidos`, `retorno_em`, `mudancas_citadas` (remédios que a cuidadora disse que mudaram).
3. `registrar_relato_consulta` guarda o relato na consulta. Se `retorno_em` tiver data, a Agenda oferece registrar a próxima consulta (§11.1).
4. **Relato falado não muda a lista.** Se houver `mudancas_citadas`: "Para eu atualizar a lista, mande a foto da receita nova. Até lá, a lista continua como está." Só a receita, pelo fluxo da §7, muda a lista.

## 12. Remédio nunca falta (E4)

### 12.1 Estoque

- **Registro** (`registrar_estoque`, direto, como `registrar_dose`): a cuidadora diz "comprei 2 caixas de losartana" (Farmácia, que pergunta quantos comprimidos vêm na caixa se não souber), ou toca em "Contar esta caixa no estoque" (§6.6, usa `quantidade_embalagem` lida). O registro guarda a **quantidade total na mão** naquele momento (soma ao que já havia, ou substitui se a cuidadora disser "tenho 20 comprimidos").
- **Quantidade por dose:** vem de `unidades_por_dose` (§6.3). Se estiver nula, a Farmácia pergunta uma vez: "Quantos comprimidos de <nome> ela toma de cada vez, conforme a receita?" (pendência `quantidade_por_dose`). A Seri só registra o que a cuidadora disser; não sugere número.
- **Cálculo** (`estoque.calcular`, determinístico): estoque estimado = último registro − (unidades por dose × doses previstas desde o registro), sem descontar as doses marcadas `nao_tomada`. Dias restantes = estoque ÷ consumo diário pelo cronograma.
- **Avisos** na `verificacao_diaria` **(HA-D11)**: com **7 dias** restantes e de novo com **2 dias**, uma mensagem `aviso_estoque` por remédio: "A <nome> deve acabar por volta de <dia>." + o texto da Farmácia Popular (§12.3), se couber, + botão **"Comprei mais"** (abre o teclado ou a gravação). Remédio sem registro de estoque não gera aviso; a Farmácia oferece cadastrar quando a lista é confirmada pela primeira vez.

### 12.2 Validade da receita (P1)

- Validade = `data_receita` + `validade_receita_dias` do C8 (pelo tipo de receita do princípio). Sem `data_receita` ou sem validade na tabela → não calcula.
- Com **7 dias** para vencer: "A receita da <nome> vence em <dia>. Se ela for continuar, peça uma receita nova ao médico." A receita vencendo também entra nos pontos para conferir do preparo (§11.2).

### 12.3 Farmácia Popular

- Item da lista com `farmacia_popular = True` no C8 ganha, na tela Remédios e nos avisos, a frase fixa: "Pelo programa Farmácia Popular, a <nome> sai de graça nas farmácias credenciadas. Leve <documentos do C8>."
- Se o remédio da lista for de marca e o programa entregar pelo princípio ativo, a frase acrescenta: "A farmácia pode entregar outra marca do mesmo remédio. Confirme com o farmacêutico." A Seri não sugere trocar a marca.
- A Farmácia responde "onde pego de graça?" e "esse remédio tem no Farmácia Popular?" só com o C8.

## 13. Guardrails

### 13.1 Regras fixas

- `detectar_alarme` (C4) roda antes de qualquer agente (§5, passo 2) e de novo no fluxo do diário (§9). Vale também para o relato da consulta (§11.3).
- Mensagem fixa: **"Isso pode ser um sinal de alarme. Ligue agora para o SAMU: 192."** + botão `tel:192`.

### 13.2 Confirmação humana e decisões (HA-D9)

- Ferramenta com `exige_confirmacao` **não executa**: a função cria uma pendência no `Repositorio` com os argumentos e devolve ao agente "aguardando confirmação da cuidadora".
- Ações (C1), todas **em código, sem agente**:
  - `confirmar_pendencia` executa exatamente os argumentos guardados; `recusar_pendencia` descarta. Pendência já resolvida é ignorada (clique duplo).
  - `definir_escopo` (§7.2) e `decidir_item` (§7.4) atualizam a proposta guardada na pendência e devolvem a proposta atualizada.
  - `contar_estoque` (§6.6) registra a caixa no estoque.
- A pausa de execução do próprio Agno (*human-in-the-loop*) não é usada: a confirmação chega em outra requisição, e a pendência no C6 já guarda tudo.

### 13.3 Auditor (determinístico, HA-D4 decidida)

Roda **no núcleo**, depois de qualquer agente ou fluxo e antes de liberar a resposta, sobre todo `texto` de saída (inclusive as perguntas do preparo):

1. **Frases proibidas:** orientação de dose, troca ou suspensão (ex.: "tome", "pode tomar", "aumente", "diminua", "dobre", "suspenda", "pare de tomar", "troque", "substitua", "pode tirar"), com variações. A lista fica em `guardrails/frases.py` e é ampliada com os casos do conjunto de guardrail da avaliação.
2. **Números de dose:** quantidade + unidade (mg, ml, gotas, comprimidos) só passa se corresponder a um item da lista atual, da proposta ou do estoque registrado.
3. **Remédio fora da lista:** nome de remédio conhecido pelo Normalizador que não está na lista, na proposta nem no histórico de versões.
4. **Fato clínico sem fonte:** menção a interação, efeito, contraindicação, duplicidade ou **indicação ("serve para", "é para")** sem um `Alerta`, `Conduta` ou `InfoRemedio` gerado nesta resposta (registrado no `EstadoMensagem`).

Bloqueio → o texto é trocado por **"Não posso orientar sobre doses ou troca de remédios. Leve essa dúvida ao farmacêutico ou médico."** (ou pela frase fixa do caso) e o motivo vai para o registro de passos. As frases fixas desta spec passam pelo Auditor como as outras e são escritas para não dispará-lo.

### 13.4 Alertas para a cuidadora (D15.2)

O texto do alerta é montado a partir do `Alerta`: "<descrição>. Fonte: <fonte>. **Leve ao farmacêutico ou médico antes de mudar qualquer coisa.**" O Explicador pode explicar em palavras simples, sem acrescentar fato.

## 14. Fala (TTS)

- **Local** (D4, mantido): Piper, voz pt-BR em `TTS_VOZ`; ffmpeg converte para **MP3**.
- `falar(texto) -> Anexo` (C1) atende a API (lembretes) e o próprio harness (§5, passo 6).
- Textos longos (> 400 caracteres) não ganham áudio, para não atrasar a resposta.

## 15. Registro de passos (P1, D21)

`repo.registrar_passo` com `mensagem_id` (ou id do evento), ordem, tipo (`percepcao`, `regra_fixa`, `contexto`, `agente`, `ferramenta`, `resultado`, `bloqueio_auditor`, `resposta`), **agente** (coordenadora, leitor, intérprete…), conteúdo resumido, duração (ms), modelo e **tokens de entrada e saída**. Fica **só no servidor** e serve para depurar, para a avaliação (tempo e custo) e para mostrar na banca a divisão de tarefas entre os subagentes.

## 16. Persona da Seri

- Português do Brasil, "você", frases curtas, no máximo 3 frases por mensagem, sem jargão (diz "remédio", não "fármaco").
- Acolhedora, sem prometer resultado e sem se apresentar como profissional de saúde.
- Sempre que não souber: diz que não sabe e encaminha a um humano.
- Vale para todos os subagentes que falam com a cuidadora (§2.2).

## 17. Ferramentas e limites

- Instruções de cada subagente em `prompts/<subagente>.md`: persona da Seri (§16), as regras do §13 que valem para ele, em linguagem direta, e o bloco de contexto.
- **No máximo 5 chamadas de ferramenta por mensagem, somando todos os agentes** (D21). O `EstadoMensagem` conta as chamadas por um hook de ferramenta do Agno (`tool_hooks`), e cada agente também recebe `tool_call_limit`. Argumento inválido ou ferramenta desconhecida conta como chamada e volta ao agente como erro. No limite, o agente responde sem ferramentas; se ainda falhar: "Vou precisar de um pouco mais de informação. Pode me contar de outro jeito?".

### 17.1 Registro de ferramentas

| Ferramenta | O que faz | Implementação | Usada por | Exige confirmação |
|---|---|---|---|---|
| `consultar_lista` | Lista atual, cronograma e pendências | C6 (A) | Rotina, Explicador, Farmácia | Não |
| `consultar_doses` | Doses do período (tomadas, perdidas) | C6 (A) | Rotina | Não |
| `normalizar` | Nome → princípio ativo | C2 (C) | Explicador; pós-processamento | Não |
| `checar_lista` | Alertas da lista | C3 (C) | Explicador; fluxo de leitura; preparo | Não |
| `info_remedio` | Para que serve, Farmácia Popular, tipo e validade da receita | **C8 (C)** | Explicador, Farmácia; pós-processamento; preparo; estoque | Não |
| `avaliar_gravidade` | Sintoma → conduta | C4 (C) | Fluxo do diário | Não |
| `pedir_foto` | Pede foto de receita ou de caixa | B | Rotina | Não |
| `registrar_dose` | "Ela já tomou o das 8h" | C6 (A) | Rotina | **Não** (D21) |
| `registrar_sintoma` | Guarda sintoma + conduta | C6 (A) | Fluxo do diário; regras fixas | **Não** (D21) |
| `consultar_consultas` | Próximas consultas e as anteriores | C6 (A) | Agenda | Não |
| `registrar_consulta` | Marca uma consulta | C6 (A) | Agenda | **Sim** |
| `registrar_relato_consulta` | Guarda o que o médico disse | C6 (A) | Fluxo do relato | Não |
| `consultar_estoque` | Estoque estimado e dias restantes | B (`estoque.py`) sobre C6 | Farmácia | Não |
| `registrar_estoque` | Guarda a quantidade na mão | C6 (A) | Farmácia; ação `contar_estoque` | Não |
| `gerar_resumo` | Monta o `Resumo` (C5) e chama `salvar_resumo` | B + A | Escalonador; preparo | Não |
| `escalar` | Mensagem com a conduta + resumo e link | B | Escalonador | Não |
| `salvar_lista_confirmada` | Grava a nova versão da lista | C6 (A) | Confirmação (§13.2) | **Sim** |
| `alterar_cronograma` | Muda, inclui ou remove horários | C6 (A) | Rotina | **Sim** |

Cada entrada do registro tem: `nome`, `descricao` (em português, para o modelo), `entrada` e `saida` (modelos Pydantic), `exige_confirmacao` e `funcao`. As ferramentas são funções Python puras; um adaptador as entrega ao Agno. **Cada agente só recebe as ferramentas da coluna "Usada por"**: ferramenta fora da lista do agente não existe para ele.

## 18. Testes

Nenhum teste automático chama a OpenAI: os agentes usam um **modelo falso** compatível com a classe de modelo do Agno. A chamada real fica no teste de bancada e na avaliação.

- Auditor: casos positivos e negativos (incluindo os 20 do conjunto de guardrail, indicação sem fonte e "pode tirar").
- Regras fixas: os 4 sinais do guardrail chegam a `ligue_192` **sem nenhum agente ser chamado**, inclusive no relato da consulta.
- Equipe: encaminhamento a cada membro; limite de 5 chamadas somando os agentes; ferramenta com confirmação vira pendência; agente não enxerga ferramenta fora da sua lista.
- Leitura: Leitor e Intérprete falsos, inclusive PDF com texto (pula o Leitor) e caixa de remédio já na lista (§6.6).
- **Conciliação** (`conciliar`, sem agente): os 4 tipos de mudança; os 3 escopos; item sem `prescritor`; mesmo princípio com outro nome; decisão ausente tratada como `nao_sei`.
- **Estoque** (`estoque.calcular`, sem agente): consumo com meio comprimido, dose `nao_tomada`, avisos de 7 e 2 dias, remédio sem registro.
- **Preparo:** dossiê completo; pergunta sem origem descartada; Preparador com falha usa as candidatas.
- Diário com as 3 condutas.
- Leitor e Intérprete reais: imagens de bancada (fora do Git), rodadas à mão no teste de bancada ([`externo.md`](externo.md) §4).
