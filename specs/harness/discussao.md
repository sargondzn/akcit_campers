# Discussão — harness

> **Dono:** Pessoa B (Caio). As decisões de projeto já tomadas estão na [`00-projeto/discussao.md`](../00-projeto/discussao.md) (D3, D4, D5, D15, D19, D21, D22).
> As perguntas abaixo **não bloqueiam o início**: a [`spec.md`](spec.md) já usa a recomendação como padrão.

---

## HA-D1 — Leitura como fluxo fixo ou decidida pelo Orquestrador

**Contexto:** com foto ou PDF, a sequência é sempre a mesma (Leitor → normalizar → checar_lista → proposta). Deixar o modelo decidir cada passo custa uma chamada a mais por etapa e, em CPU, cada chamada pode levar dezenas de segundos. Modelos pequenos também erram mais a ordem.

**Opções:** (a) fluxo fixo em código, com o Orquestrador cuidando da conversa, das dúvidas e do diário; (b) tudo decidido pelo Orquestrador.

**Recomendação:** (a) no regional. Na final, com LangGraph (D5) e talvez um modelo maior, o fluxo vira um subgrafo.

**Resposta:** Faremos conforme recomendado.

> *Nota (24/10):* com a troca para o Agno (D5 atualizada), o fluxo fixo vira um `Workflow` do Agno com os subagentes Leitor e Intérprete (spec §2.4). A decisão continua valendo: o modelo não escolhe os passos da leitura.

---

## HA-D2 — Modelos escolhidos no teste de bancada

**Contexto:** a escolha depende de testar na máquina de produção (D22, BE-D3).

**Para preencher depois do teste:** modelo de visão, modelo de conversa, tempo médio por foto, se o tool use nativo funcionou ou se foi preciso o plano B (spec §3).

**Resposta:** Faremos conforme recomendação.

> *Atualização (24/10):* com a troca para a API da OpenAI (D3 atualizada), o teste de bancada deixa de depender da máquina de produção e compara modelos da OpenAI (ponto de partida: `gpt-6-luna`; `gpt-6.1-sol` para o Leitor se a receita à mão falhar). **Para preencher depois do teste:** modelo de visão, modelo de conversa, acerto nas imagens de bancada, tempo médio por foto e por mensagem, **custo médio por foto e por mensagem**. Passo a passo: [`externo.md`](externo.md) §4.

---

## HA-D3 — Limiar de confiança da leitura

**Contexto:** abaixo do limiar, o item entra no fluxo de confiança baixa (D19). Modelos pequenos não calibram bem a própria confiança, por isso a spec também usa o resultado do `normalizar`.

**Recomendação:** 0,7, revisado depois do primeiro relatório da avaliação.

**Resposta:** Faremos conforme a recomendação.

---

## HA-D4 — Auditor só com regras ou também com modelo

**Contexto:** um Auditor determinístico (palavras e números) é rápido, previsível e independente do modelo que gera a resposta. Um segundo modelo verificando pega casos sutis, mas dobra o tempo em CPU.

**Recomendação:** só regras no regional; avaliar um verificador com modelo na final.

**Resposta:** Faremos conforme recomendado.

---

> **Perguntas abertas em 24/10/2026**, na revisão da spec contra o projeto. Também não bloqueiam: até a resposta, vale a recomendação.

## HA-D5 — Tempo total da leitura × limite de 5 min da API

**Contexto:** a API desiste da mensagem depois de **5 min** (00-projeto §6). *Atualizado em 24/10:* com a OpenAI, cada chamada tem até **60 s** e até 2 novas tentativas (spec §3.2), e uma foto passa por Leitor + Intérprete. Um PDF escaneado de várias páginas faz uma chamada do Leitor por página e também aumenta o custo.

**Opções:** (a) orçamento de tempo por mensagem no harness (**240 s**), que corta as novas tentativas e as páginas restantes quando o tempo acaba, e no máximo **3 páginas** por PDF escaneado; (b) aumentar o limite da API (muda a spec de A); (c) deixar como está.

**Recomendação:** (a). Os números são revistos depois do teste de bancada (HA-D2).

**Resposta:**

---

## HA-D6 — Um modelo só ou dois · ⚪ superada em 24/10

> Com a API da OpenAI não há modelo carregado na memória da máquina, então o problema de troca de modelo não existe mais. A escolha de um ou dois modelos virou critério de custo e acerto na HA-D2.

**Contexto:** a spec permite o mesmo modelo para visão e conversa (§3). Com dois modelos em CPU, o Ollama pode precisar trocar o modelo na memória a cada foto seguida de conversa, e essa troca custa segundos a mais. Já existem modelos pequenos com visão **e** tool use (ex.: `qwen3-vl:4b`).

**Recomendação:** no teste de bancada, testar primeiro um modelo só para os dois papéis. Só usar dois se o único falhar em leitura ou em tool use. Em qualquer caso, pedir a A `OLLAMA_KEEP_ALIVE=-1` no Compose ([`externo.md`](externo.md) §6).

**Resposta:**

---

## HA-D7 — Qual C1 vale na integração com a API atual

**Contexto:** o código que já está em `plataforma/api` (A) é diferente da spec do projeto: caminhos `/api/...`, ação `confirmar_lista` (o C1 tem `confirmar_pendencia`, `recusar_pendencia` e `corrigir_item`), resposta na hora (a spec pede `202` + fila, 00-projeto §6), banco próprio sem `contratos/` nem `Repositorio` (C6). O README dela também cita a interface num repositório separado (`akcit-campers-front`) e "HTTPS no mesmo endereço da interface", enquanto a spec diz Netlify + túnel.

**Recomendação:** o harness segue o C1 e o C6 da spec do projeto (que prevalece sobre as frentes). Combinar com Beatriz se a API será ajustada ao contrato ou se o contrato muda, com acordo dos três (00-projeto §7.4). Não é decisão só de B.

**Resposta:**

---

## HA-D8 — Modo da equipe da Seri no Agno

**Contexto:** o `Team` do Agno tem modos. Em `route`, a coordenadora escolhe **um** subagente e a resposta dele vai direto para a cuidadora: 2 chamadas ao modelo no caso comum. Em `coordinate`, a coordenadora divide a tarefa, delega e junta as respostas: no mínimo 3 chamadas, e mais se ela delegar a vários. *Atualizado em 24/10:* com a OpenAI, a lentidão de CPU sai do caminho, mas cada chamada a mais custa tempo e dinheiro, e com 5 membros (Rotina, Explicador, Diário, Agenda, Farmácia) o `coordinate` tende a delegar a mais de um.

**Opções:** (a) `route` no regional; (b) `coordinate` desde já.

**Recomendação:** (a). Reavaliar `coordinate` depois do teste de bancada, se aparecerem pedidos que juntam dois membros com frequência (ex.: "para que serve e quando acaba a losartana?").

**Resposta:**

---

## HA-D9 — Confirmação humana: pendência no C6 ou pausa do Agno

**Contexto:** o Agno tem uma pausa própria para confirmação humana: a ferramenta marcada para confirmar pausa a execução, que depois continua com `continue_run`. Para continuar em outra requisição, ele precisa guardar a execução num banco do Agno. No nosso fluxo, o "Confirmo a lista" chega em outra mensagem, às vezes muito depois, e a pendência já fica no `Repositorio` (C6).

**Opções:** (a) manter a pendência no C6 e executar a confirmação em código, sem agente (spec §10.2); (b) usar a pausa do Agno com um banco próprio dele.

**Recomendação:** (a). Uma fonte de verdade só (o banco de A), e a confirmação não depende do modelo.

**Resposta:**

---

> **Perguntas abertas em 24/10/2026**, com as funcionalidades E1, E2, E4 e E8 (D23). Não bloqueiam: até a resposta, vale a recomendação.

## HA-D10 — Conciliação quando a lista não tem o médico de cada remédio

**Contexto:** a conciliação (spec §7.2) compara a receita nova só com os remédios do mesmo médico, para não marcar como "sumido" o remédio receitado por outro. Mas listas montadas antes de 24/10, ou a partir de caixas, não têm o `prescritor`.

**Opções:** (a) se nenhum item tiver médico, perguntar "Algum remédio da lista é de outro médico?" antes de marcar os ausentes; (b) tratar como "toda a lista" sem perguntar; (c) nunca marcar ausente sem médico conhecido.

**Recomendação:** (a). Uma pergunta a mais evita que a cuidadora ache que a Seri mandou tirar um remédio.

**Resposta:**

---

## HA-D11 — Quando avisar que o remédio vai acabar

**Contexto:** o aviso de estoque (spec §12.1) usa o estoque estimado. Cedo demais vira ruído; tarde demais não dá tempo de comprar ou de pegar no Farmácia Popular, nem de conseguir receita nova.

**Recomendação:** dois avisos por remédio: com **7 dias** e com **2 dias** restantes. Validade da receita: um aviso com **7 dias** para vencer.

**Resposta:**

---

## HA-D12 — Horários dos eventos agendados

**Contexto:** os eventos (spec §5.1) chegam como mensagens da Seri. Horário ruim incomoda e é ignorado.

**Recomendação:** verificação diária às **09:00**; véspera da consulta às **18:00** do dia anterior; pós-consulta às **10:00** do dia seguinte. Na demo, todos são disparados na hora (`/demo/evento`, backend §5).

**Resposta:**

---

> **Pergunta aberta em 24/10/2026**, a partir da avaliação com os relatos cegos da rodada 3 (DA-D4, AV-D4). Até a resposta, a spec §9 continua valendo como está.

## HA-D13 — Avaliar a gravidade antes de o Diário perguntar o que falta

**Contexto:** pela spec §9, o Diário primeiro completa o relato (até 2 perguntas: o quê, desde quando, intensidade) e só depois roda `avaliar_gravidade`. Medição em 24/10/2026, com os 125 relatos da rodada 3 (frases que as regras nunca viram), pelo harness completo, com o `dados/` real e o `gpt-6-luna`:

| | Hoje (pergunta antes) | Gravidade antes da pergunta |
|---|---|---|
| Alarmes → 192 | **64 de 105 (61%)**: 59 pela regra fixa + 5 pelo Diário | **97 de 105 (92%)** |
| Frases normais → 192 por engano | 3 de 20 | 4 de 20 |

Dos 41 alarmes perdidos hoje, **40 viraram uma pergunta do Diário** ("desde quando?") em vez do 192. Exemplos: "ficou com a boca torta e a fala enrolada", "parece que tem um saco plástico no rosto dela", "ela não reconhece a filha". Os 8 que continuariam perdidos têm relatos em que o Diário não usou um termo do vocabulário de C (ex.: "dormência" sem o sinal `dormencia_subita`).

**Opções:** (a) avaliar a gravidade sobre o relato parcial **antes** de perguntar: se der 192, manda o 192 na hora; se der 24 h ou observar, segue perguntando e reavalia no fim; (b) manter como está.

**Recomendação:** (a). É a mesma lógica da regra fixa (sinal de alarme não espera), custa uma chamada a mais só quando o relato está incompleto e troca 33 alarmes perdidos por 1 alarme falso a mais.

**Resposta:**
