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

## AV-D4 — Meta de 100% dos alarmes → 192 com texto livre 🔴 (aberta; aprofundar)

**Contexto:** o conjunto `relatos` (spec §2) tem como meta que 100% dos relatos com alarme virem `ligue_192`. Medimos o detector de alarme (`dados/gravidade.py::detectar_alarme`, só regexes) com frases de cuidadora geradas por LLM que ele nunca viu (rodada 3, `avaliacao/exemplos/relatos_cegos/`):

- **59 de 105 frases de emergência disparam o 192 (56%).** Os outros 46 alarmes passam em silêncio.
- **3 de 20 frases normais (sem emergência) disparam o 192 por engano (15%).** Os "20" são só as frases que não são alarme.
- Dois ciclos de ajuste das regexes levaram a 100% nas frases usadas no ajuste, mas **não melhoraram** as frases novas (59% antes, 56% depois).
- Ressalva: as frases são inventadas por LLM, não fala real, e a rodada 3 foi pedida de propósito mais difícil. O número com relatos reais pode ser melhor ou pior.

**Duas decisões em uma (não confundir):**

| | Para quê | Quando |
|---|---|---|
| Decisão 1: o que dizer no pitch | Não afirmar "100% dos alarmes viram 192" com texto livre. Mostrar o número honesto e os 7 sinais cobertos. | Regional |
| Decisão 2: arquitetura do projeto | Como detectar alarme de verdade, em fala livre. | Final e depois |

**Opções para a decisão 2 (e o pitch):**
- (a) **Só regras fixas, número honesto no pitch.** Regional. Simples, testável, sem alucinação. Recall baixo com fala livre.
- (b) **Camada com LLM que só eleva a conduta.** O LLM lê o relato; se ele achar alarme, o cartão 192 aparece mesmo que a regex não tenha achado. Ele **nunca** pode tirar um alarme que a regra fixa achou ("se qualquer um achar, alerta"). Muda a regra da visão §2.3 ("sinal de alarme não passa pelo LLM"), precisa do acordo dos três. Custos: mais falsos alarmes, latência, o custo e a latência de uma chamada à OpenAI (o harness passou a usar a API em 24/10) e a privacidade (o relato sai da máquina); precisa ser medido com a mesma metodologia cega.
- (c) **Usar fala real das cuidadoras (entrevistas) para melhorar e para medir.** Não substitui o (b): complementa. Dois usos: (1) alimentar a lista de jeitos de falar que as regras e o prompt do LLM precisam cobrir; (2) formar um conjunto de teste de fala real, **separado** do que foi usado no ajuste, que dá um número que vale. Exemplo: da entrevista sai "ela ficou toda mole e a boca entortou"; essa frase entra no teste, e uma parte fica guardada sem ninguém mexer, só para medir. Hoje só há 1 entrevista (meta: 5 a 10).

**Recomendação:** (a) no regional, com o número honesto; (b) mais (c) na final.

**Perguntas para aprofundar:**
1. O (b) roda no `diario.estruturar` que já existe (sem custo de chamada extra) ou é uma chamada separada?
2. Qual modelo da OpenAI (a spec do harness trocou o modelo local pela API em 24/10, HA-D2 ainda aberta) detecta alarme bem, e a que custo, latência e privacidade (o relato da cuidadora vai para a OpenAI, o que o termo de consentimento já precisa cobrir)? Medir com as rodadas cegas e depois com falas reais. O Diário (que já existe e já lê o relato) poderia fazer isso na mesma chamada?
3. Qual taxa de falso alarme a cuidadora tolera antes de ignorar o cartão (efeito "lobo")?
4. Como pedir a mudança da regra da visão §2.3 aos três (A, B e C)?
5. O que medir e mostrar no pitch do regional, enquanto o (b) não existe?

**Resposta:**
