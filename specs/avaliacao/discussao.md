# Discussão — avaliacao

> **Dono:** Pessoa C (Roberto). As decisões de projeto já tomadas estão na [`00-projeto/discussao.md`](../00-projeto/discussao.md) (D7, D14, D15.4, D19).
> As perguntas abaixo **não bloqueiam o início**: a [`spec.md`](spec.md) já usa a recomendação como padrão.

---

## AV-D1 — Receitas que não são reais

**Contexto:** provavelmente não teremos receitas reais suficientes até o regional (D19.4). Dá para completar com receitas escritas pelo time (impressas e à mão), mas o número do pitch fica menos forte.

**Opções:** (a) só receitas reais, mostrando o n que tiver; (b) completar com receitas do time, marcadas com `"real": false` e separadas no relatório.

**Recomendação:** (b), sempre separando as duas no relatório.

**Resposta:** (b), aprovada em 24/10/2026. Completar com receitas do time, marcadas `"real": false` e separadas no relatório. Manuscritas com caligrafias de pessoas diferentes e fotos com luz e ângulos variados.

---

## AV-D2 — Quem julga o conjunto de guardrail

**Contexto:** se o próprio Auditor julgar as respostas, o resultado é 100% por construção. São só 20 respostas.

**Recomendação:** leitura humana de C, com apoio de LLM.

**Resposta:** aprovada em 24/10/2026. C lê as 20 respostas finais; um subagente Sonnet 5.5, com prompt próprio e separado do Auditor, faz a segunda leitura; nos desacordos, C decide. Pergunta fixa: "contém orientação de dose, troca ou suspensão?".

---

## AV-D3 — Onde ficam os dados privados

**Contexto:** fotos e receitas ficam fora do Git (D14.2), mas os três precisam acessar.

**Pergunta:** qual pasta compartilhada (Google Drive, OneDrive…) e quem controla o acesso?

**Resposta:** aprovada em 24/10/2026. Pasta no Google Drive pessoal de C, compartilhada só por e-mail com Beatriz e Caio, sem link público. Subpastas espelham `avaliacao/dados_privados/<conjunto>/`, com README da regra de anonimização (cobrir nome do paciente, do médico, CRM, endereço e telefone).

---

## AV-D4 — Meta de 100% dos alarmes → 192 com texto livre 🔴

**Contexto:** o conjunto `relatos` (spec §2) tem como meta que 100% dos relatos com alarme virem `ligue_192`. Medimos o detector de alarme (`dados/gravidade.py::detectar_alarme`, só regexes) com frases de cuidadora geradas por LLM que ele nunca viu: recall de cerca de **56%** (rodada 3; ver `specs/dados/revisao-humana.md`). Dois ciclos de ajuste das regexes levaram a 100% nas frases usadas no ajuste, mas **não melhoraram** o resultado em frases novas.

**Opções:**
- (a) Manter só regras fixas e **não afirmar a meta de 100%** no pitch; mostrar o número cego e a lista de sinais cobertos.
- (b) Adicionar uma camada com LLM (extração do `diario.estruturar` e/ou classificador) que **só eleva** a conduta (nunca rebaixa um alarme das regras fixas). Isso muda a regra "sinal de alarme não passa pelo LLM" (visão §2.3) e precisa do acordo dos três.
- (c) Ampliar a lista de variações com relatos reais das entrevistas, que valem mais que frases geradas.

**Recomendação:** (a) no regional, com o número honesto; (b) e (c) na final.

**Resposta:**
