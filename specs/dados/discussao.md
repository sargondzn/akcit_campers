# Discussão — dados

> **Dono:** Pessoa C (Roberto). As decisões de projeto já tomadas estão na [`00-projeto/discussao.md`](../00-projeto/discussao.md) (D7, D15.2, D15.4, D16).
> As perguntas abaixo **não bloqueiam o início**: a [`spec.md`](spec.md) já usa a recomendação como padrão.

---

## DA-D1 — Lista dos ~20 remédios

**Contexto:** a D16 reduziu o Normalizador para cerca de 20 remédios, e a D7.1 deixou a escolha com o dono da frente. A demo e os conjuntos de avaliação (caixas, receitas, pares) usam remédios desta lista.

**Sugestão de critério:** remédios muito comuns em idosos (pressão, diabetes, colesterol, anticoagulação, estômago, sono), incluindo pelo menos um par com interação conhecida e um caso de mesmo princípio ativo em nomes diferentes, para a demo mostrar os alertas.

**Resposta (lista final):** aprovada em 24/10/2026. 20 princípios ativos:

| Grupo | Princípios ativos |
|---|---|
| Pressão e coração | losartana, hidroclorotiazida, anlodipino, enalapril, atenolol, furosemida, espironolactona |
| Diabetes | metformina, glibenclamida |
| Colesterol | sinvastatina, atorvastatina |
| Anticoagulação e antiagregação | varfarina, ácido acetilsalicílico, clopidogrel |
| Estômago | omeprazol |
| Sono e ansiedade | clonazepam, diazepam |
| Dor e inflamação | diclofenaco, ibuprofeno |
| Tireoide | levotiroxina |

- Pares da demo: varfarina + AAS e varfarina + diclofenaco (grave); losartana + espironolactona (potássio alto); sinvastatina + anlodipino (moderada).
- Duplicidades: clonazepam + diazepam (mesma classe, também CBMPI); diclofenaco + ibuprofeno.
- Mesmo princípio, nomes diferentes: Glifage e Glucophage (metformina); AAS e Aspirina (ácido acetilsalicílico).
- Entrada extra: associação losartana + hidroclorotiazida.
- Cada nome precisa existir na CMED e as caixas precisam ser fáceis de fotografar.

---

## DA-D2 — Negação nos sinais de alarme

**Contexto:** "não teve dor no peito" contém "dor no peito". Tratar negação reduz falso alarme, mas pode deixar passar um alarme verdadeiro ("não sei se é dor no peito, mas está apertando").

**Opções:** (a) conservador: qualquer menção dispara o 192; (b) ignorar a menção quando houver negação logo antes.

**Recomendação:** (a) no regional.

**Resposta:** (a) conservador, aprovada em 24/10/2026. Qualquer menção a um dos 4 sinais dispara o cartão `ligue_192`, inclusive com negação. O sistema não liga sozinho: mostra o cartão vermelho com o botão `tel:192` e a cuidadora decide. Os testes incluem frases com negação esperando o disparo. Nível de precaução configurável (fraco/médio) fica como roadmap da final; chamada automática está fora do escopo.

---

## DA-D3 — Qual LLM gera as tabelas clínicas

**Contexto:** a D7.2 decidiu gerar as tabelas com LLM. O modelo local pequeno do harness (D3) sabe pouco de farmacologia. Usar um assistente de chat disponível ao time (sem API) só para gerar as tabelas não envia dado de paciente nenhum.

**Recomendação:** o melhor assistente disponível ao time, registrando qual foi em `dados/tabelas/LEIAME.md`.

**Resposta:** aprovada em 24/10/2026. Geração com Claude Sonnet 5.5; conferência por subagentes Sonnet 5.5 em sessão limpa, sem ver o prompt de geração, procurando erros linha a linha. Divergências são removidas ou marcadas. Os pares da demo são conferidos também contra a bula (Anvisa). Modelos, data e prompts ficam em `dados/tabelas/LEIAME.md`.

---

## DA-D4 — Vocabulário do Diário (dados ↔ harness) 🟡

**Contexto:** `avaliar_gravidade` (C) decide a conduta olhando os termos de `SintomaEstruturado.sintomas` e as chaves de `sinais`, mas quem preenche esses campos é o **Diário** (`harness.diario.estruturar`, de B), um subagente já decidido na spec do harness (§2.2 e §9) que organiza o relato da cuidadora; ele **não** decide alarme nem conduta. Se o Diário devolver "caiu no banheiro" em vez de `queda`, a regra de 24 horas poderia não casar. As regexes de alarme (192) rodam sobre o texto todo e não dependem disso. (Não confundir com a AV-D4, que trata de uma camada de LLM para detectar alarme e ainda não foi decidida.)

**Resposta (24/10/2026):** o vocabulário de [`vocabulario-diario.md`](vocabulario-diario.md) **prevalece enquanto o Diário real não existe ou não o segue**; B adapta o Diário a ele.
- A fonte agora é `dados/tabelas/vocabulario.csv` (nome canônico, definição, sinônimos, exclusões, exemplo e tratamento de cada termo); o documento é gerado dele por `python -m dados.vocabulario`, e `--json` gera a lista fechada para o prompt.
- As regras de gravidade só podem usar termos do vocabulário (`validar_tabelas.py` confere, e há testes de alcance de cada regra).
- Mesmo que o Diário não use o nome canônico, a regra casa os **sinônimos** na `descricao` (com exclusões e negação), então o vocabulário também protege contra um Diário que escreve livre.
- O que fica **aberto**: ligar o Diário real. O prompt atual (`harness/prompts/diario.md`) ainda tem exemplos próprios ("tontura", "queda", "febre_alta") e não cita este vocabulário; o bloco para colar nele está no documento. Quando B ligar o Diário à OpenAI, rodar `pytest dados/testes/test_relatos_e2e.py` com `OPENAI_API_KEY`: ele compara a conduta de ponta a ponta e lista os termos fora do vocabulário.
