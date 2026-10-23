# Discussão — harness

> **Dono:** Pessoa B (Caio). As decisões de projeto já tomadas estão na [`00-projeto/discussao.md`](../00-projeto/discussao.md) (D3, D4, D5, D15, D19, D21, D22).
> As perguntas abaixo **não bloqueiam o início**: a [`spec.md`](spec.md) já usa a recomendação como padrão.

---

## HA-D1 — Leitura como fluxo fixo ou decidida pelo Orquestrador

**Contexto:** com foto ou PDF, a sequência é sempre a mesma (Leitor → normalizar → checar_lista → proposta). Deixar o modelo decidir cada passo custa uma chamada a mais por etapa e, em CPU, cada chamada pode levar dezenas de segundos. Modelos pequenos também erram mais a ordem.

**Opções:** (a) fluxo fixo em código, com o Orquestrador cuidando da conversa, das dúvidas e do diário; (b) tudo decidido pelo Orquestrador.

**Recomendação:** (a) no regional. Na final, com LangGraph (D5) e talvez um modelo maior, o fluxo vira um subgrafo.

**Resposta:**

---

## HA-D2 — Modelos escolhidos no teste de bancada

**Contexto:** a escolha depende de testar na máquina de produção (D22, BE-D3).

**Para preencher depois do teste:** modelo de visão, modelo de conversa, tempo médio por foto, se o tool use nativo funcionou ou se foi preciso o plano B (spec §3).

**Resposta:**

---

## HA-D3 — Limiar de confiança da leitura

**Contexto:** abaixo do limiar, o item entra no fluxo de confiança baixa (D19). Modelos pequenos não calibram bem a própria confiança, por isso a spec também usa o resultado do `normalizar`.

**Recomendação:** 0,7, revisado depois do primeiro relatório da avaliação.

**Resposta:**

---

## HA-D4 — Auditor só com regras ou também com modelo

**Contexto:** um Auditor determinístico (palavras e números) é rápido, previsível e independente do modelo que gera a resposta. Um segundo modelo verificando pega casos sutis, mas dobra o tempo em CPU.

**Recomendação:** só regras no regional; avaliar um verificador com modelo na final.

**Resposta:**
