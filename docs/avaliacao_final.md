# AKCIT Camp 2026 — Avaliação Final dos 8 Candidatos

> Feita em 27/09/2026 sobre `problemas_candidatos_finais.md` (F1–F8).
> Método: para cada candidato, imaginei o **desenrolar** (a dor hoje → onde o agente entra → como medir o resultado) e planejei o **escopo da estrutura da solução**. Não é a solução pronta. Com isso, dei notas nos critérios da banca.
> As notas são julgamento meu, na escala do edital (1 = frágil, 3 = genérico, 5 = forte e evidenciado). **Diferenças abaixo de ~0,3 são ruído.** A validação com pessoas reais decide o resto.

---

## 0. O que mudou desde o doc dos 8 (pesquisa de hoje)

| # | Fato novo | Efeito |
|---|---|---|
| F2 | O **Governo de Goiás (mar/2026)**, a **SMS de Goiânia (fev/2026)** e **Aparecida** já confirmam consultas pelo WhatsApp. **Fortaleza** (set/2026) já realoca a vaga com IA. | O "lado SUS pouco atendido" não vale em GO. Diferencial cai muito. |
| F6 | Existe o **+Convênios (QIATech)**: IA para mapear oportunidades, gerar propostas e monitorar prazos, integrando Transferegov, SIMEC e FNS. A Dynadok faz prestação de contas com IA. | Concorrência sobe de "média" para "média-alta". |
| F6 | O Transferegov tem **API pública** de Transferências Especiais (plano de ação, relatório de gestão). | Viabilidade técnica sobe: dá para fazer demo com **dado real**. |
| F7 | A **Hand Talk lançou reconhecimento de sinais com IA**. **CESAR + Lenovo** gastaram 5 anos e ~R$ 10 mi em tradução Libras ↔ português. | O sentido difícil (Libras → texto) já tem dono com muito dinheiro. |
| F5 | Já há ferramentas de IA que classificam cClassTrib/CST "em segundos" (ex.: ClassTrib). **Simples Nacional e MEI estão dispensados** dos campos IBS/CBS em 2026; só entram em 2027. | Mercado mais cheio, e a dor de 2026 é menor que parecia para "pequenas empresas". |
| F8 | A lei federal (**Lei 15.224/2025**, PNCPDA) **incentiva** a doação (Selo Doador, segurança jurídica). Ela **não obriga**. | Não é "demanda forçada por lei". |
| F4 | O monitoramento estadual já **envia alertas geolocalizados** para brigadas, Defesa Civil e Bombeiros. O PSA Brigadas formou **172 brigadistas**, todos no Nordeste Goiano. A emergência ambiental vai de 01/07 a **31/10/2026**. | Mercado pequeno, alerta já existe, e a janela de validação fecha em 1 mês. |
| F1 | Na revisão de simplificação da EUDR (maio/2026), o alívio para micro e pequenos (declaração única, endereço no lugar do polígono) vale **só para países de risco baixo**. **O Brasil é "risco padrão"**. | A exigência de polígono + due diligence completa **continua** para o Brasil. A dor se mantém. |

### Uma correção de enquadramento
O doc dos 8 usa **"Demo em 1 dia"** como critério. O edital diz que a equipe **pode começar a desenvolver logo após a inscrição** e que a solução é a mesma do início ao fim. O prazo real de construção é **~4 semanas até 24/10** (ou 31/10 no online), mais 4 semanas até a final. O dia do hackathon é para refinar e apresentar. Isso ajuda candidatos com engenharia mais pesada (F1) e não salva o F7.

---

## 1. Placar

### 1.1 Regional (o que decide se você chega à final)

Equipe fica em **3 para todos**: depende de quem entra no time, não do problema. Ela entra na conta, mas não diferencia.

| | Problema e Validação (20%) | Solução e Uso de IA (30%) | Diferencial e Viabilidade (20%) | Equipe (15%) | Pitch (15%) | **Nota regional** |
|---|---|---|---|---|---|---|
| **F6** Município × emendas | 4 | **4,5** | 3 | 3 | 4 | **3,80** |
| **F1** EUDR | 4 | 3,5 | 3,5 | 3 | 4 | **3,60** |
| **F3** Cuidador | 4 | 3,5 | 2,5 | 3 | 4,5 | **3,48** |
| **F5** Reforma tributária | 4 | 4 | 2,5 | 3 | 3 | **3,40** |
| **F8** Desperdício | 4 | 3 | 2,5 | 3 | 3,5 | **3,18** |
| **F7** Libras | 4 | 2,5 | 2 | 3 | 4,5 | **3,08** |
| **F4** Brigadas | 3 | 3 | 2,5 | 3 | 4 | **3,05** |
| **F2** Faltas SUS | 4 | 2,5 | 2 | 3 | 3,5 | **2,93** |
| **F9** Lexicity *(adicionado em 11/10)* | 3,5* | 4* | 2,5 | 3 | 4 | **3,45** |

\* Condicionado: Problema e Validação só chega a 3,5 com 8–10 conversas com quem estuda inglês (hoje n = 2); Solução e IA só chega a 4 se o tutor conduzir a experiência. Se o Diferencial subir para 3,5, o regional passa de 3,6.

### 1.2 Final (projeção para 28/11)

Pesos da final: IA e Maturidade Técnica 25% (ativo próprio pesa muito), **Potencial de Investimento 30%**, Equipe e Execução 20% (fixo em 3), Evolução 10%, Pitch 15%.

| | IA + ativo próprio | **Potencial de Investimento** | Espaço para evoluir | Pitch | **Nota final** |
|---|---|---|---|---|---|
| **F1** EUDR | 4 | **4** | 4 | 4 | **3,80** |
| **F6** Município × emendas | 4,5 | 3 | 4 | 4 | **3,63** |
| **F5** Reforma tributária | 3,5 | 3,5 | 3,5 | 3 | **3,33** |
| **F3** Cuidador | 3,5 | 2,5 | 3,5 | 4,5 | **3,25** |
| **F8** Desperdício | 3 | 3 | 3 | 3,5 | **3,08** |
| **F4** Brigadas | 3 | 2 | 3 | 4 | **2,85** |
| **F7** Libras | 2,5 | 2 | 3 | 4,5 | **2,80** |
| **F2** Faltas SUS | 2,5 | 2 | 3 | 3,5 | **2,65** |
| **F9** Lexicity *(11/10)* | 4 | 2,5 | 3,5 | 4 | **3,30** |

### 1.3 Leitura rápida
- **F6 ganha no regional, F1 ganha na final.** Os dois estão no topo nas duas tabelas.
- **F3 é o curinga:** é o mais fácil de validar e tem o pitch mais emocional, mas pagador e risco regulatório pesam contra ele na final.
- **F5** tem boa engenharia de IA, mas mercado lotado e domínio novo.
- **F2, F4 e F7 caem** por causa dos fatos novos da seção 0.

---

## 2. Os 8, um a um

Formato de cada bloco:
- **Desenrolar:** a dor hoje → onde o agente entra → como saber que funcionou
- **Estrutura (escopo):** fluxo, dados, ferramentas, guardrails e avaliação
- **Teste de remoção** (edital, 9.4): se tirar o agente, a solução ainda entrega o valor principal?
- **MVP até 24/10 × evolução até 28/11**
- **Pontos medidos**

---

### F6 — Município pequeno perdendo emendas e convênios · regional 3,80 · final 3,63

**Desenrolar**
- **Hoje:** o secretário de planejamento de uma cidade de 8 mil habitantes cuida de 30 instrumentos em 5 portais. Ele descobre a pendência quando o recurso já está bloqueado. A saída é pagar consultoria por percentual captado, ou perder o recurso.
- **Com o agente:** todo dia de manhã chega uma mensagem no WhatsApp: "2 planos de ação da Emenda Pix X vencem em 12 dias. Rascunhei os dois com base em 14 planos aprovados de municípios parecidos. Revise aqui."
- **Métrica de sucesso:** pendências resolvidas antes do prazo, dias até regularizar e R$ desbloqueados.

**Estrutura (escopo)**
```
[Monitor] ─diário→ API Transferegov + CAUC ──→ lista de pendências e prazos (estado em banco)
     │
[Diagnóstico] ── RAG sobre Decreto 11.531/23, Portaria Conjunta 33/23 e manuais ──→ "o que falta, por quê, até quando" (com citação)
     │
[Redator] ── modelos + planos APROVADOS de municípios parecidos (API) ──→ rascunho do plano / relatório de gestão
     │
[Auditor] ── checagens determinísticas (campos obrigatórios, valores, datas, CNPJ) ──→ aprova ou devolve ao Redator
     │
Secretário revisa e aprova → exporta o texto pronto para colar no portal
```
- **Dados:** a API pública de Transferências Especiais e o Portal da Transparência são **reais e abertos**. O CAUC é consulta pública da STN (provavelmente via scraping; confirmar).
- **Multiagente se justifica?** Sim. Monitor, Diagnóstico, Redator e Auditor têm entradas e saídas diferentes, e o Auditor como verificador separado é exatamente o que a banca pede.
- **Guardrails:** o agente **nunca submete nada ao portal** (sem login gov.br). Toda afirmação normativa sai com citação. Valores e datas vêm só de ferramenta, nunca do LLM.
- **Avaliação:** separar planos aprovados como gold set e medir se o rascunho cobre os campos obrigatórios. Medir a precisão do diagnóstico contra pendências reais conhecidas e a taxa de citação correta no RAG.
- **Ativo próprio:** um corpus de planos aprovados e reprovados, mais o histórico de pendências por tipo de município. Isso cresce com o uso.

**Teste de remoção:** sem agente sobra um painel de prazos, e o +Convênios já faz isso. O valor que só o agente entrega é **diagnosticar e rascunhar** a partir de norma e de casos parecidos. **IA central.**

**MVP 24/10:** Monitor + Diagnóstico + Redator para **Emendas Pix**, rodando ao vivo sobre 3 municípios goianos reais (idealmente um dos 43 impedidos).
**Evolução 28/11:** convênios discricionários, prestação de contas lendo notas por foto, Auditor completo e métricas de avaliação no painel.

**Demo de 3 min:** "Este é o município X. Ele está impedido de receber R$ Y. Olhem o agente achar o porquê na API, agora, e rascunhar a correção."

**Pontos medidos**
- ✅ Dado real e público permite **gerar evidência sem entrevista** (quantos municípios de GO têm pendência hoje), além das conversas.
- ✅ Venda B2G de ticket pequeno pode ser feita por **dispensa de licitação** (limite anual na casa de R$ 60 mil, atualizado por decreto; confirmar). Há canal via AGM, CNM e consórcios.
- ⚠️ O +Convênios é concorrente direto. O diferencial precisa sair do nicho (**Emendas Pix + regularização**, e não captação) e do ativo.
- ⚠️ Pouco "imersivo". A voz no WhatsApp cobre o mínimo.
- **Critério para abandonar:** se secretários disserem que a pendência é política (falta decisão, não braço técnico), ou que já usam consultoria ou +Convênios e estão satisfeitos.

---

### F1 — EUDR para pequeno produtor e cooperativa · regional 3,60 · final 3,80

**Desenrolar**
- **Hoje:** a trading avisa a cooperativa: "a partir de dezembro, sem polígono e prova de não desmatamento, não compro". O técnico da cooperativa precisa juntar CAR, mapa e comprovantes de 300 cooperados, um por um, pelo WhatsApp e por planilha. **Uma parcela irregular contamina o lote inteiro.**
- **Com o agente:** o agente conversa com cada cooperado, pega o número do CAR ou a localização, cruza com desmatamento pós-2020 e embargos, e devolve ao técnico: "287 ok, 9 faltando documento (já cobrei), 4 com risco. Separe estes do lote."
- **Métrica de sucesso:** % de cooperados com dossiê completo, horas de técnico por cooperado e lotes bloqueados.

**Estrutura (escopo)**
```
[Coletor, WhatsApp] ── conversa com o produtor (texto, voz, foto do recibo do CAR) ──→ nº do CAR / ponto GPS
     │
[Geo, ferramentas determinísticas] ── polígono do SICAR ∩ PRODES Cerrado ∩ MapBiomas Alerta ∩ embargos Ibama ──→ achados com área e data
     │
[Analista] ── RAG sobre EUDR + Código Florestal ──→ o achado é risco real ou exceção legal (ex.: supressão autorizada)?
     │
[Montador] ──→ dossiê por produtor e por lote + segregação das parcelas de risco
     │
Técnico da cooperativa aprova
```
- **Dados:** CAR/SICAR (download público por município), PRODES Cerrado (TerraBrasilis), MapBiomas Alerta (API gratuita com cadastro) e embargos Ibama (público com geometria). **Todos reais.**
- **Guardrails:** o veredito "livre de desmatamento" vem **só da interseção geográfica**, nunca do LLM. O LLM explica e classifica exceções, sempre citando a norma. Na dúvida, o caso vai para o técnico.
- **Avaliação:** um conjunto de propriedades com resultado conhecido (limpas e com alerta) para medir falsos negativos, que é o erro caro. Medir também a taxa de conclusão da coleta por conversa.
- **Ativo próprio:** a base consolidada de cooperados com polígonos validados, e a integração que ninguém quer construir (conversa com o produtor + geo + dossiê).

**Teste de remoção:** ⚠️ **ponto fraco.** O núcleo (polígono ∩ desmatamento) é um script de GIS. Se a banca enxergar só isso, a IA vira acessório. O valor que só o agente entrega é **coletar dados de centenas de produtores pouco digitais** e **raciocinar sobre exceções legais**. O pitch tem que colocar isso na frente.

**MVP 24/10:** Coletor + Geo + dossiê para 1 município goiano, com CARs públicos reais e um mapa na demo.
**Evolução 28/11:** Analista de exceções, visão por lote e cooperativa, legalidade (trabalho escravo, embargos) e exportação no formato do sistema da UE.

**Demo de 3 min:** "Seu João manda o número do CAR por áudio → o mapa acende → 3,2 ha desmatados em 2022 → o lote é separado → o dossiê sai pronto."

**Pontos medidos**
- ✅ Prazo externo duro (30/12/2026 para as tradings; 30/06/2027 para os pequenos) e o Brasil sem alívio. A pressão sobre o fornecedor começa **agora**, bem no meio do camp.
- ✅ É o **melhor candidato em Potencial de Investimento**: B2B, pagador identificável (cooperativa ou trading), mercado global.
- ✅ O mapa dá um visual "imersivo" razoável.
- ⚠️ **Hipótese a checar já:** quanto da soja e da carne **de Goiás** vai para a UE? A soja em grão vai principalmente para a China. Ver no **Comex Stat**. Se o volume for pequeno, o recorte vira café (MG) ou soja em farelo, e você perde o apelo regional.
- ⚠️ A EUDR já foi adiada 2 vezes. Um terceiro adiamento enfraquece a urgência.
- ⚠️ Domínio novo e engenharia geo pesada. Cabe em 4 semanas, mas não em 1 dia.
- **Critério para abandonar:** se as cooperativas disserem que a trading já fornece a ferramenta de coleta aos fornecedores, ou que a AB+S resolve.

---

### F3 — Cuidador familiar e a medicação do idoso · regional 3,48 · final 3,25

**Desenrolar**
- **Hoje:** a filha cuida da mãe, que toma 9 remédios receitados por 3 médicos. Ela usa uma tabela no papel na geladeira. Não sabe se a tontura de hoje é interação, e o posto só atende na semana que vem.
- **Com o agente:** ela manda a foto da receita e recebe o cronograma. O agente lembra por voz. Ela diz "ela está tonta", e o agente registra, checa interações conhecidas e avisa: "isso pode ter relação com X + Y; já mandei o resumo para a enfermeira da ESF."
- **Métrica de sucesso:** doses tomadas no horário, alertas relevantes escalados e carga percebida pelo cuidador.

**Estrutura (escopo)**
```
Foto da receita → [Leitor, LLM com visão] → itens estruturados → confirmação do cuidador (obrigatória)
     → [Normalizador] nome comercial → princípio ativo (lista CMED/Anvisa, determinístico)
     → [Checador] base de interações (determinística) → alertas
     → [Diário, voz] sintomas → [Escalonador] regras de gravidade → resumo para a ESF
```
- **Dados:** a lista CMED (princípio ativo por produto) é pública. A base de interações é o gargalo: DDInter é gratuita para uso acadêmico (**checar a licença comercial**). Não há dado real da ESF, então a demo simula.
- **Guardrails:** **nunca sugerir dose nem suspensão**. Todo alerta termina em "fale com o profissional". A leitura da receita exige confirmação humana antes de virar cronograma.
- **Avaliação:** acurácia da leitura em receitas reais anonimizadas (**as manuscritas são o maior risco técnico**) e recall de interações sobre pares conhecidos.

**Teste de remoção:** sem o agente sobra um app de lembrete (Medisafe). O valor novo é **ler a receita, conversar sobre sintomas e escalar**. IA central, mas o núcleo de segurança é determinístico, como deve ser.

**MVP 24/10:** foto → cronograma → lembrete → diário por voz → alerta de interação.
**Evolução 28/11:** painel da ESF e piloto com famílias reais.

**Pontos medidos**
- ✅ **O mais fácil de validar:** todo mundo conhece um cuidador. Cinco conversas até 04/10 é realista.
- ✅ É o pitch mais emocional e universal.
- ❌ **Pagador fraco.** A família paga pouco. A tese B2B2C via **operadoras de saúde** (menos internação de idoso) existe, mas não está provada.
- ❌ **Risco regulatório:** software que apoia decisão clínica pode ser dispositivo médico na Anvisa (RDC 657/2022). A banca de investidores vai perguntar.
- **Critério para abandonar:** se os cuidadores disserem que o problema real não é a medicação (e sim cansaço, dinheiro ou revezamento).

---

### F5 — Contador e pequena empresa na Reforma Tributária · regional 3,40 · final 3,33

**Desenrolar**
- **Hoje:** o escritório atende 60 empresas do regime regular. Cada cadastro de produto precisa de CST + cClassTrib novos, e o contador revisa item por item. A nota sai com erro e a rejeição volta dias depois.
- **Com o agente:** o contador sobe o cadastro e os XMLs do mês e recebe: "1.240 itens classificados, 37 com dúvida (com justificativa e artigo da LC 214), 12 notas com divergência."
- **Métrica de sucesso:** % de itens classificados sem revisão, erros pegos antes da emissão e horas economizadas por cliente.

**Estrutura (escopo)**
```
Cadastro (CSV) + XMLs NF-e → [Classificador] RAG sobre LC 214/2025 + tabelas cClassTrib/CST/NCM
   → [Validador determinístico] o código existe? é compatível com o NCM/CST?
   → [Auditor de notas] compara o emitido com o esperado → divergências
   → [Redator] correção + justificativa com citação → contador aprova
```
- **Dados:** as tabelas oficiais são públicas (Portal NF-e). **XMLs reais precisam vir de um contador parceiro.**
- **Guardrails:** sem citação não há classificação. Na dúvida, o item vai para humano. Cálculo só em ferramenta.
- **Avaliação:** um gold set de itens classificados por um contador. **Sem um contador no time ou parceiro, você não consegue montar essa avaliação.**

**Teste de remoção:** a classificação com raciocínio jurídico é o núcleo, e é tarefa natural de LLM. **IA central.**

**Pontos medidos**
- ✅ Demanda forçada por lei, pagador claro (escritório contábil) e ótima história de engenharia (RAG + validador).
- ❌ Mercado lotado: ERPs grandes, ferramentas de classificação com IA já no ar e Contabilizei. A banca vai perguntar "por que não o ERP?".
- ❌ Simples e MEI só entram em 2027, então a dor de 2026 é menor que o doc dos 8 sugere.
- ❌ Domínio novo e sem contador por perto.
- ❌ O pitch é seco.

---

### F8 — Supermercado que joga fora o que dava para vender ou doar · regional 3,18 · final 3,08

**Desenrolar**
- **Hoje:** o gerente do hortifrúti descobre o que venceu na hora de jogar fora. A doação depende de alguém lembrar de ligar para a ONG, e a nota fiscal de doação dá trabalho.
- **Com o agente:** toda manhã chega uma lista: "remarque estes 14 itens em 30%; estes 8 vencem amanhã, e o Banco de Alimentos busca às 15h. A nota de doação está rascunhada."

**Estrutura (escopo):** exportação de estoque (CSV do ERP) → previsão de vencimento (determinística + ML simples) → regras de remarcação → [Agente de doação] casa o excedente com ONGs próximas e negocia a coleta → rascunho da documentação (termo + NF de doação; **o ICMS da doação em GO precisa ser verificado**) → o gerente aprova.

**Teste de remoção:** ⚠️ um relatório de "itens a vencer" já entrega boa parte do valor. A IA entra na coordenação da doação e nos documentos. **IA média.**

**Pontos medidos**
- ✅ Fácil de validar (mercados de bairro) e o ROI é mensurável.
- ❌ Concorrência forte (Connecting Food, Food To Save, módulos de ERP).
- ❌ A lei incentiva, mas não obriga.
- ❌ Depende de integração com o caixa ou ERP.

---

### F7 — Pessoa surda sem intérprete no atendimento de saúde · regional 3,08 · final 2,80

**Desenrolar:** a pessoa surda chega à UBS, ninguém sinaliza, e a consulta vira bilhetinho ou filho interpretando.

**Estrutura (escopo) do que é viável:**
- Profissional → surdo: fala → texto → **português simplificado** (LLM; o português costuma ser a 2ª língua do surdo) → avatar do VLibras (código aberto do governo).
- Surdo → profissional: **triagem prévia visual** (pictogramas + vídeo curto) e reconhecimento de um vocabulário fechado de ~50 sinais de saúde (MediaPipe + classificador). Isso funciona em demo, mas **não é robusto**.

**Teste de remoção:** ❌ o avatar é do VLibras, não seu. O que é realmente seu (simplificação + triagem) é fino, e o sentido difícil já tem Hand Talk e CESAR/Lenovo.

**Pontos medidos**
- ✅ Impacto social muito alto e o maior alinhamento com "tecnologias imersivas", que é a vocação do AKCIT. A banca vai gostar do tema.
- ❌ Diferencial técnico fraco contra concorrentes com muito dinheiro.
- ❌ Precisa de alguém fluente em Libras no time para validar (o curso de Letras: Libras da UFG ajuda).

---

### F4 — Brigadista comunitário do Cerrado · regional 3,05 · final 2,85

**Desenrolar:** o brigadista em Cavalcante recebe o alerta de foco, decide sozinho se vai, combate, e depois preenche o relatório do turno para receber os R$ 267,24.

**Estrutura (escopo):** focos (BDQueimadas, público) + tempo (INMET/Open-Meteo) → índice de risco (determinístico) → [Triagem] prioriza e sugere o deslocamento → [Relator] o brigadista fala por áudio ou manda foto → relatório do PSA pronto → coordenação aprova. **Conectividade ruim na Chapada** exige modo offline.

**Teste de remoção:** ⚠️ o alerta já existe (monitoramento estadual). O que sobra para o agente é triagem e **relatório por voz**. IA média.

**Pontos medidos**
- ✅ Apelo regional forte para a banca de Goiânia, e há acesso ao CEMPA-Cerrado na UFG.
- ❌ Mercado pequeno (172 brigadistas, um só pagador, a Semad).
- ❌ A temporada acaba em 31/10, então dá para validar agora e depois só na próxima seca.
- ❌ Potencial de investimento baixo. Escalaria para Prevfogo e ICMBio, mas também é B2G.

---

### F2 — Consultas e exames perdidos por falta no SUS · regional 2,93 · final 2,65

**Desenrolar:** o paciente falta, a vaga some e quem estava na fila não fica sabendo.

**Estrutura (escopo):** confirmação pelo WhatsApp → motivo da falta → libera a vaga → chama o próximo da fila (regras de prioridade da regulação, determinísticas) → modelo de risco de falta → overbooking controlado → o regulador aprova. **Integração com SISREG ou sistema municipal é fechada**, então a demo seria toda simulada.

**Teste de remoção:** ❌ confirmação é template, previsão é ML clássico e realocação é regra. Um bot sem LLM entrega quase tudo.

**Pontos medidos**
- ❌ **Goiás, Goiânia e Aparecida já confirmam pelo WhatsApp**, e Fortaleza já realoca com IA. As secretarias com quem você validaria já compraram a solução básica.
- Sobra uma pergunta de validação interessante ("depois do WhatsApp, a falta caiu? O que acontece com a vaga liberada na véspera?"), mas é um nicho dentro de um produto que já existe.

---

### F9 — Lexicity (aprender vocabulário por lugar, com tutor e conteúdo validado) · regional ~3,45 · final ~3,30

*Adicionado em 11/10/2026, a partir do projeto `~/dev/lexicity` e de uma busca de concorrência.*

**Desenrolar**
- **Hoje:** o aluno de inglês aprende palavras soltas ou em conversa. Apps com LLM geram conteúdo que ninguém verifica, e quem estuda para prova ou cursinho não vê a estrutura do léxico (sinônimos, antônimos, nível CEFR por sentido). A dor vem do Roberto e da Bea, e precisa ser confirmada.
- **Com o agente:** o aprendiz clica num lugar da cidade e vê as palavras do contexto. O tutor decide o que ensinar a seguir com base no que ele errou, gera exercícios, corrige e agenda a revisão. Toda tradução, sinônimo e regra mostrada foi checada contra o grafo.
- **Métrica de sucesso:** taxa de erro do conteúdo gerado (medida e publicada), retenção de palavras na revisão e sessões por semana.

**Estrutura (escopo, produto completo até 24/10)**
```
Grafo lexical (Neo4j): WordNet + CEFRLex + palavras, sentidos e cenas
     │
[Gerador] LLM (Claude ou modelo aberto) pré-gera cenas, frases e notas de gramática, com cache
     │
[Validador] checa tradução, sinônimo, antônimo e nível contra o grafo ──→ aceita ou rejeita (taxa de erro em eval/)
     │
[Tutor, LangGraph] modelo do aprendiz + ferramentas (consulta ao grafo, agendador de revisão, gerador de exercício, corretor)
     │
Interface: cidade 2D clicável → opcional WebXR com fotos 360° (mesmo JSON de cena)
```
- **Dados:** WordNet, CEFRLex e WordNet anotado com CEFR, todos abertos. **Licenças ainda não checadas.** O histórico de erros dos aprendizes é o ativo que cresce com o uso.
- **Guardrails:** conteúdo e regras de gramática só entram se passarem pelo validador. O chat do tutor responde com base no grafo e cita a fonte.
- **Avaliação:** taxa de alucinação do conteúdo gerado (Claude × modelo aberto), e um pequeno comparativo de recuperação por grafo × vetorial nas perguntas de gramática.

**Teste de remoção:** se o tutor for o caminho principal (decide, gera, corrige, agenda), sem ele o app vira um navegador de grafo, e o valor principal some. **IA central, condicionada ao desenho.** Se o tutor for só um chat ao lado da cidade, cai para 3.

**Concorrência (busca de 11/10; só páginas de loja e não testei os apps)**
- **LingoLooper** (mundo 3D com lugares, mais de 1.000 personagens de IA, ~26 idiomas, US$ 14,99/mês) é o mais próximo e já ocupa "cidade + tutor de IA".
- Noun Town, Mondly VR e ImmerseMe ocupam o espaço de cenas em VR, e o CapWords o de vocabulário a partir de fotos.
- Fluentika, Speak On, Hablo e EnglishBay cobrem tutor de IA para brasileiros.
- Não achei nenhum com exploração por lugar + grafo lexical + conteúdo validado com erro publicado. É ausência nas buscas, não prova.

**Pontos medidos**
- ✅ O tutor por agente casa com o que o curso lista como uso esperado ("tutores adaptativos"), e a validação com taxa medida é a "profundidade de engenharia" que a banca pede.
- ✅ Custo marginal baixo (conteúdo pré-gerado e em cache) ajuda o argumento de unit economics da final.
- ✅ Visão de óculos VR natural: WebXR com fotos 360° evita modelar a cidade 3D.
- ⚠️ **Diferencial é o ponto fraco.** "Cidade + IA" não diferencia. Só valem a confiança no conteúdo e a navegação pela estrutura do léxico, e ambas dependem de as entrevistas confirmarem a dor.
- ⚠️ Problema e Validação sem evidência ainda. O pagador é freemium (CAC alto); cursinho e escola de idiomas é canal opcional a validar com a Bea.
- ⚠️ Nenhum critério dos placares mede "imersivo", então VR é bônus de narrativa.
- ⚠️ O transformer de flexão verbal (Fase 3) só conta se entrar no produto. O idioma-alvo continua inglês, e a ideia de reenquadrar para "Português para migrantes" foi descartada.
- **Critério para abandonar:** as conversas mostrarem que ninguém sente o erro de conteúdo nem a falta de contexto, ou que os alunos não pagariam.

---

## 3. Padrões que a avaliação revelou

1. **O teste de remoção separa os candidatos.** Onde o núcleo é regra ou ML clássico (F2, F8, F4), a nota de IA não passa de 3. Onde o núcleo é ler norma, raciocinar e rascunhar (F6, F5), passa de 4. O F1 fica no meio e depende de como você enquadra.
2. **Dado real e aberto vale ouro na demo.** F6 e F1 podem rodar ao vivo sobre dado público de verdade. Os outros dependem de dado simulado ou de parceiro.
3. **O regional e a final puxam para lados diferentes.** O regional premia a IA (30%) e a final premia o investimento (30%). F6 e F1 são os únicos bons nos dois.
4. **"Imersivo" não decide.** Só F7 é forte nisso, e perde em todo o resto. Voz + mapa (F1) ou voz no WhatsApp (F6) bastam como multimodal.

---

## 4. Recomendação

**Levar F6 e F1 como finalistas** e usar a semana até 04/10 para validar os dois em paralelo. Na segunda semana, fique com um só.

| | F6 — Emendas | F1 — EUDR |
|---|---|---|
| **Por que** | Melhor nota de IA; demo ao vivo com dado real; vence o regional | Melhor potencial de investimento; prazo externo duro; vence a final |
| **5 conversas até 04/10 com** | secretários de planejamento de cidades pequenas de GO (a AGM, em Goiânia, é o atalho) | técnicos de cooperativa (ex.: Comigo, em Rio Verde), agrônomos da EA/UFG, exportadores |
| **Checagem de mesa desta semana** | Listar pela API quantos municípios de GO têm pendência hoje | Ver no Comex Stat quanto de GO vai para a UE |
| **Critério para abandonar** | Pendência é política, não técnica; ou já têm consultoria/+Convênios e estão satisfeitos | A trading já dá a ferramenta ao fornecedor; ou GO exporta pouco para a UE |

**Plano B:** **F3.** Se as duas validações falharem até ~11/10, o F3 é o único que dá para validar rápido o bastante para recuperar o prazo de 24/10.

**Descartar agora:** F2 (a solução básica já existe exatamente onde você validaria) e F7 (sem diferencial técnico possível no prazo).

---

## Fontes (pesquisa de 27/09/2026)

- EUDR, simplificação e risco do Brasil: [Dcycle](https://dcycle.io/blog/eudr-simplification-review-2026/) · [EUDR.live — revisão de 04/05/2026](https://www.eudr.live/en/simplification-review-may-2026) · [Coolset — declaração simplificada](https://www.coolset.com/academy/eudr-simplified-declaration-for-micro-and-small-operators-compliance-made-easy-for-primary-producers) · [Tracextech — classificação de risco](https://tracextech.com/eudr-country-risk-classifications/) · [Access2Markets (Comissão Europeia)](https://trade.ec.europa.eu/access-to-markets/en/news/delay-until-december-2026-and-other-developments-implementation-eudr-regulation) · [Embrapa — rastreabilidade](https://www.embrapa.br/en/busca-de-noticias/-/noticia/105296287/brasil-avanca-na-rastreabilidade-do-agro-mas-dificuldades-ainda-existem)
- Transferegov e concorrentes do F6: [API de Transferências Especiais](https://www.gov.br/transferegov/pt-br/ferramentas-gestao/dados-abertos/apis/transferencias-especiais) · [APIs Transferegov](https://api-publica.transferegov.gestao.gov.br/) · [CGU — transparência das Emendas Pix (05/2026)](https://www.gov.br/cgu/pt-br/assuntos/noticias/2026/05/portal-da-transparencia-amplia-acesso-a-dados-sobre-emendas-individuais-feitas-por-transferencias-especiais) · [+Convênios (QIATech)](https://www.qiatech.com.br/) · [Dynadok](https://blog.dynadok.com/governo/como-automatizar-a-analise-documental-na-prestacao-de-contas-de-convenios-publicos/)
- SUS e WhatsApp: [Governo de Goiás (03/2026)](https://goias.gov.br/governo-lanca-canal-de-confirmacao-de-consultas-e-exames-pelo-whatsapp/) · [Mais Goiás — 26% de faltas](https://www.maisgoias.com.br/cidades/26-dos-pacientes-nao-comparecem-a-consultas-e-exames-agendados-em-goias-diz-governo/) · [Tribuna do Planalto — Goiânia](https://tribunadoplanalto.com.br/saude-de-goiania-vai-confirmar-consultas-e-exames-pelo-whatsapp/) · [Aparecida](https://aparecida.go.gov.br/saude-de-aparecida-confirma-consultas-especializadas-pelo-whatsapp) · [O Povo — Fortaleza (09/2026)](https://www.opovo.com.br/noticias/fortaleza/2026/09/22/aplicativo-permite-confirmacao-por-whatsapp-de-consultas-em-fortaleza.html)
- Reforma tributária: [Meu Contador Online — cClassTrib](https://www.meucontadoronline.com.br/blog/guia-completo-cst-ibs-cbs-cclasstrib/) · [ClassTrib](https://classtrib.com/novo/) · [Tecnospeed — tabelas](https://blog.tecnospeed.com.br/tabela-cclasstrib/)
- Desperdício: [Embrapa — Lei 15.224/2025](https://www.embrapa.br/en/busca-de-noticias/-/noticia/53848860/governo-sanciona-lei-de-combate-a-perdas-e-desperdicios-de-alimentos) · [Câmara — lei em vigor](https://www.camara.leg.br/noticias/1206356-entra-em-vigor-lei-de-incentivo-a-doacao-e-de-combate-ao-desperdicio-de-alimentos/) · [ANR — Lei SP 18.420/2026](https://anrbrasil.org.br/lei-estadual-no-18-420-2026-combate-ao-desperdicio-de-alimentos-e-doacao-de-excedentes-de-refeicoes-prontas/)
- Brigadas: [Semad — PSA Brigadas e Cerrado Vivo](https://goias.gov.br/meioambiente/com-psa-brigadas-semad-reforca-operacao-cerrado-vivo-no-combate-aos-incendios-florestais-em-goias/) · [Semad — 172 formados](https://goias.gov.br/meioambiente/psa-brigadas-forma-quase-180-moradores-do-nordeste-goiano-para-atuar-na-prevencao-e-combate-a-incendios-florestais/) · [Portal 6 (23/09/2026)](https://portal6.com.br/2026/09/23/goias-alia-planejamento-estrategico-e-engajamento-comunitario-para-proteger-o-cerrado-2/)
- Libras: [AIoT Brasil — Hand Talk reconhece sinais](https://aiotbrasil.com.br/noticias/hand-talk-lanca-tecnologia-de-reconhecimento-de-sinais-com-ia) · [Jornal Digital — CESAR e Lenovo](https://jornaldigital.recife.br/2025/02/13/cesar-e-lenovo-desenvolvem-ia-que-faz-traducao-simultanea-de-libras-para-o-portugues/)
