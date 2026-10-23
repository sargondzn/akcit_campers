# Discussão — dados

> **Dono:** Pessoa C (Roberto). As decisões de projeto já tomadas estão na [`00-projeto/discussao.md`](../00-projeto/discussao.md) (D7, D15.2, D15.4, D16).
> As perguntas abaixo **não bloqueiam o início**: a [`spec.md`](spec.md) já usa a recomendação como padrão.

---

## DA-D1 — Lista dos ~20 remédios

**Contexto:** a D16 reduziu o Normalizador para cerca de 20 remédios, e a D7.1 deixou a escolha com o dono da frente. A demo e os conjuntos de avaliação (caixas, receitas, pares) usam remédios desta lista.

**Sugestão de critério:** remédios muito comuns em idosos (pressão, diabetes, colesterol, anticoagulação, estômago, sono), incluindo pelo menos um par com interação conhecida e um caso de mesmo princípio ativo em nomes diferentes, para a demo mostrar os alertas.

**Resposta (lista final):**

---

## DA-D2 — Negação nos sinais de alarme

**Contexto:** "não teve dor no peito" contém "dor no peito". Tratar negação reduz falso alarme, mas pode deixar passar um alarme verdadeiro ("não sei se é dor no peito, mas está apertando").

**Opções:** (a) conservador: qualquer menção dispara o 192; (b) ignorar a menção quando houver negação logo antes.

**Recomendação:** (a) no regional.

**Resposta:**

---

## DA-D3 — Qual LLM gera as tabelas clínicas

**Contexto:** a D7.2 decidiu gerar as tabelas com LLM. O modelo local pequeno do harness (D3) sabe pouco de farmacologia. Usar um assistente de chat disponível ao time (sem API) só para gerar as tabelas não envia dado de paciente nenhum.

**Recomendação:** o melhor assistente disponível ao time, registrando qual foi em `dados/tabelas/LEIAME.md`.

**Resposta:**
