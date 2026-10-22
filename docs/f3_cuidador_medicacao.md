# F3 — Cuidador familiar e a medicação do idoso

> Projeto escolhido para o desenvolvimento e a participação no AKCIT Camp 2026.
> Este documento **só reorganiza** o que já está em [`avaliacao_final.md`](avaliacao_final.md) sobre o F3 (avaliação feita em 27/09/2026). Nada foi acrescentado nem removido do escopo.

---

## 1. Resumo

| | |
|---|---|
| **Problema** | Cuidador familiar gerenciando muitos remédios de um idoso, receitados por vários médicos, sem apoio para entender sintomas e interações. |
| **Solução** | Agente que lê a foto da receita, monta o cronograma, lembra por voz, registra sintomas num diário por voz, checa interações conhecidas e escala para a ESF. |
| **Nota regional** | **3,48** (3º lugar entre os candidatos) |
| **Nota final (projeção)** | **3,25** |
| **Leitura da avaliação** | **O curinga:** é o mais fácil de validar e tem o pitch mais emocional, mas pagador e risco regulatório pesam contra ele na final. |

---

## 2. Desenrolar

- **Hoje:** a filha cuida da mãe, que toma 9 remédios receitados por 3 médicos. Ela usa uma tabela no papel na geladeira. Não sabe se a tontura de hoje é interação, e o posto só atende na semana que vem.
- **Com o agente:** ela manda a foto da receita e recebe o cronograma. O agente lembra por voz. Ela diz "ela está tonta", e o agente registra, checa interações conhecidas e avisa: "isso pode ter relação com X + Y; já mandei o resumo para a enfermeira da ESF."
- **Métrica de sucesso:**
  - doses tomadas no horário;
  - alertas relevantes escalados;
  - carga percebida pelo cuidador.

---

## 3. Estrutura da solução (escopo)

### 3.1 Fluxo

```
Foto da receita → [Leitor, LLM com visão] → itens estruturados → confirmação do cuidador (obrigatória)
     → [Normalizador] nome comercial → princípio ativo (lista CMED/Anvisa, determinístico)
     → [Checador] base de interações (determinística) → alertas
     → [Diário, voz] sintomas → [Escalonador] regras de gravidade → resumo para a ESF
```

### 3.2 Componentes

| Componente | O que faz | Tipo |
|---|---|---|
| **Leitor** | Lê a foto da receita e gera itens estruturados | LLM com visão |
| *Confirmação do cuidador* | Valida a leitura antes de virar cronograma | Humano (obrigatória) |
| **Normalizador** | Nome comercial → princípio ativo (lista CMED/Anvisa) | Determinístico |
| **Checador** | Cruza com a base de interações e gera alertas | Determinístico |
| **Diário (voz)** | Registra sintomas relatados pelo cuidador | Voz |
| **Escalonador** | Aplica regras de gravidade e gera o resumo para a ESF | Regras |

### 3.3 Dados

| Fonte | Situação |
|---|---|
| **Lista CMED** (princípio ativo por produto) | Pública |
| **Base de interações** | **Gargalo.** DDInter é gratuita para uso acadêmico — **checar a licença comercial** |
| **Dados da ESF** | Não há dado real; a demo simula |

### 3.4 Guardrails

- **Nunca sugerir dose nem suspensão.**
- Todo alerta termina em "fale com o profissional".
- A leitura da receita exige **confirmação humana** antes de virar cronograma.

### 3.5 Avaliação

- Acurácia da leitura em receitas reais anonimizadas (**as manuscritas são o maior risco técnico**).
- Recall de interações sobre pares conhecidos.

### 3.6 Teste de remoção (edital, 9.4)

Sem o agente sobra um app de lembrete (Medisafe). O valor novo é **ler a receita, conversar sobre sintomas e escalar**. IA central, mas o núcleo de segurança é determinístico, como deve ser.

---

## 4. Entregas

| Marco | Escopo |
|---|---|
| **MVP — 24/10** | foto → cronograma → lembrete → diário por voz → alerta de interação |
| **Evolução — 28/11** | painel da ESF e piloto com famílias reais |

> Sobre prazos: o edital permite desenvolver logo após a inscrição, e a solução é a mesma do início ao fim. O prazo real de construção é **~4 semanas até 24/10** (ou 31/10 no online), mais 4 semanas até a final. O dia do hackathon é para refinar e apresentar.

---

## 5. Notas da banca

### 5.1 Regional (decide quem chega à final)

| Critério | Peso | Nota F3 |
|---|---|---|
| Problema e Validação | 20% | 4 |
| Solução e Uso de IA | 30% | 3,5 |
| Diferencial e Viabilidade | 20% | 2,5 |
| Equipe | 15% | 3 |
| Pitch | 15% | 4,5 |
| **Nota regional** | | **3,48** |

### 5.2 Final (projeção para 28/11)

| Critério | Peso | Nota F3 |
|---|---|---|
| IA e Maturidade Técnica (ativo próprio pesa muito) | 25% | 3,5 |
| **Potencial de Investimento** | 30% | 2,5 |
| Equipe e Execução | 20% | 3 (fixo) |
| Evolução (espaço para evoluir) | 10% | 3,5 |
| Pitch | 15% | 4,5 |
| **Nota final** | | **3,25** |

> Escala do edital: 1 = frágil, 3 = genérico, 5 = forte e evidenciado. Diferenças abaixo de ~0,3 são ruído; a validação com pessoas reais decide o resto. A Equipe fica em 3 para todos os candidatos (depende de quem entra no time, não do problema).

---

## 6. Pontos medidos

### Fortes
- ✅ **O mais fácil de validar:** todo mundo conhece um cuidador. Cinco conversas até 04/10 é realista.
- ✅ É o **pitch mais emocional e universal**.

### Fracos / riscos
- ❌ **Pagador fraco.** A família paga pouco. A tese B2B2C via **operadoras de saúde** (menos internação de idoso) existe, mas não está provada.
- ❌ **Risco regulatório:** software que apoia decisão clínica pode ser dispositivo médico na Anvisa (RDC 657/2022). A banca de investidores vai perguntar.
- ⚠️ **Risco técnico:** leitura de receitas manuscritas.
- ⚠️ **Dados:** licença comercial da base de interações (DDInter) a checar; sem dado real da ESF (demo simulada). A avaliação geral nota que, fora F6 e F1, os candidatos dependem de dado simulado ou de parceiro.

### Critério para abandonar
Se os cuidadores disserem que o problema real não é a medicação (e sim cansaço, dinheiro ou revezamento).

---

## 7. Posição na recomendação original

Na avaliação de 27/09, a recomendação era levar F6 e F1 como finalistas, com o **F3 como Plano B**: "Se as duas validações falharem até ~11/10, o F3 é o único que dá para validar rápido o bastante para recuperar o prazo de 24/10."

---

## 8. Pendências que já constam no escopo

- [ ] Checar a licença comercial da DDInter (ou alternativa de base de interações).
- [ ] Conseguir receitas reais anonimizadas (incluindo manuscritas) para medir a acurácia da leitura.
- [ ] Montar conjunto de pares de interação conhecidos para medir recall.
- [ ] Conversas com cuidadores para validar a dor (e checar o critério de abandono).
- [ ] Preparar resposta para a banca sobre pagador (tese B2B2C via operadoras) e enquadramento na RDC 657/2022.
