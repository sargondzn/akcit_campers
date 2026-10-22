# Visão do projeto — Seriema (F3: cuidador familiar e a medicação do idoso)

> Resumo da minha leitura do projeto. **Última revisão: 22/10/2026** (troca do WhatsApp por plataforma própria).
>
> **Fontes do escopo:**
> - [`docs/f3_plano_startup_v1.md`](../../docs/f3_plano_startup_v1.md) — plano de 16/10: mercado, caminhos, arquitetura, BMC, riscos e cronograma.
> - [`docs/f3_cuidador_medicacao.md`](../../docs/f3_cuidador_medicacao.md) — escopo original, extraído da avaliação dos candidatos.
> - **Mudanças de escopo pedidas pelo usuário** (seção 5 deste arquivo). Elas **prevalecem** sobre os dois documentos acima, que ficam como histórico.
>
> As divergências entre as duas fontes estão na D0 de [`discussao.md`](discussao.md); não escolhi nenhum lado. O que é análise minha está marcado com *(leitura minha)*.

---

## 1. O que é

A **Seriema** (nome provisório) é uma **plataforma própria** em que a **cuidadora familiar** de um idoso que toma muitos remédios conversa com um agente de IA.

Na plataforma, a cuidadora **fotografa a receita física** que recebeu do médico, impressa ou escrita à mão. Esse deve ser o caso mais comum. Ela também pode **fotografar as caixas de remédio** e **enviar o PDF da receita digital**. O agente **monta uma lista única** com os remédios de vários médicos e pede que ela **confirme**. Depois disso, ele:
- **aponta interações, duplicidades e remédios inapropriados para idosos**, sempre mandando levar ao farmacêutico ou ao médico;
- **lembra as doses por notificação, com texto e áudio**;
- **registra os sintomas que ela relata por áudio gravado na própria plataforma**;
- **escala para um profissional** quando as regras de gravidade pedem, ou manda **ligar 192** em sinal de alarme.

> *"Mande a foto dos remédios e um áudio do dia. A Seriema organiza tudo, lembra por você e avisa quando algo precisa de um profissional."*

O agente **organiza e encaminha; não decide**. Nunca sugere dose, troca ou suspensão.

### Quem está envolvido

| Papel | Relação com o produto |
|---|---|
| **Cuidadora familiar** (40–65 anos) | Usuária da plataforma: envia fotos e áudios, confirma a lista, recebe lembretes e alertas |
| **Idoso polimedicado** (5+ remédios) | Beneficiário |
| **Farmacêutico / enfermeira da ESF / médico** | Recebe o resumo escalado e decide. Na final, usa o painel dentro da mesma plataforma |
| **Operadora de saúde** | Pagadora (tese a validar) |
| **Farmácia** | Canal e guardrail humano (tese a validar) |

---

## 2. Funcionalidades

### 2.1 Arquitetura (escopo para o regional)

```
        Plataforma Seriema (web/app — formato em D1)
        conversa com o agente · foto da receita/caixa e upload de PDF · gravação de áudio · notificações
                          │
                       [API]  ← autenticação, banco, arquivos
                          │
                 [Orquestrador / Conversa]  ← memória: perfil do idoso + lista de remédios versionada
                          │
   ┌──────────────┬───────┴─────────┬──────────────────┬───────────────────┐
   ▼              ▼                 ▼                  ▼                   ▼
[Leitor]     [Normalizador]   [Farmacovigilante]   [Rotina]          [Diário + Escalonador]
   │
   └──→ confirmação humana obrigatória antes de virar cronograma
                          │
                    [Auditor]  confere toda saída antes de ela chegar à cuidadora
```

| Peça | O que faz | Tipo |
|---|---|---|
| **Plataforma** | Interface da cuidadora: conversa, foto da receita ou da caixa, envio de PDF, gravação de áudio, lista de remédios, cronograma, diário, resumo | Frontend próprio |
| **API** | Contas, sessões, arquivos, banco; expõe o agente para a plataforma | Backend próprio |
| **Orquestrador** | Conduz a conversa; guarda o perfil do idoso e a lista de remédios versionada | LLM + estado |
| **Leitor** | Lê foto de receita física (impressa ou à mão), foto de caixa e PDF de receita digital | LLM com visão |
| **Normalizador** | Nome comercial → princípio ativo (Anvisa/CMED) | Determinístico |
| **Farmacovigilante** | **Regional:** mesmo princípio ativo em nomes diferentes + tabela curada à mão (interações, duplicidade de classe, CBMPI) para os remédios da demo. **Final:** bases completas, Beers, RAG em bulas | Ferramentas determinísticas |
| **Rotina** | Cronograma, lembrete por notificação, confirmação de dose | Determinístico |
| **Diário + Escalonador** | Áudio → sintoma estruturado → regras de gravidade → 192 ou resumo para farmacêutico/ESF/consulta | STT + LLM + regras fixas |
| **Auditor** | Bloqueia saídas que citam remédio fora da lista, contêm frase proibida ou não citam fonte | Verificador independente |

### 2.2 MVP (regional) × evolução (final)

| | **Regional** (24/10 ou 31/10) | **Final** (28/11) |
|---|---|---|
| Plataforma | Área da cuidadora: conversa, envio de foto/PDF/áudio, lista, cronograma, diário, resumo | + painel do profissional |
| Entrada | **Foto da receita física (impressa ou à mão)** + fotos de caixas + PDF de receita digital, sempre com confirmação | Código de barras da caixa |
| Checagem | **Mesmo princípio ativo** em nomes diferentes (sai do Normalizador) + **tabela curada à mão** com os remédios da demo (~15–20): pares de interação, grupos para duplicidade de classe e itens do CBMPI, cada linha com fonte | Base de interações completa e licenciada; conversão de nomes PT → internacional em escala; CBMPI completo + Beers; RAG em bulas; efeito adverso × sintoma relatado |
| Rotina | Lembrete por notificação (texto e áudio); confirmação de dose | Aviso de estoque e renovação de receita |
| Diário | Áudio → sintoma → regra de gravidade | Tendências ("3 dias de tontura") |
| Escalonamento | Resumo em PDF para consulta / farmacêutico | Painel do farmacêutico ou da enfermeira com fila de casos |
| Prova | Avaliação (seção 2.4) + 5 a 10 entrevistas | Piloto de 2 semanas com 5–10 famílias + carta de intenção |

### 2.3 Guardrails (inegociáveis)

1. Nunca sugere dose, troca ou suspensão. Todo alerta termina em "leve ao farmacêutico ou médico", e o Auditor bloqueia frases proibidas.
2. Nada vira cronograma sem a confirmação da cuidadora.
3. Fatos clínicos vêm só de ferramenta (interações, CBMPI, bula), com fonte citada. O LLM só explica.
4. Sinal de alarme não passa pelo LLM. Queda com batida na cabeça, dor no peito, falta de ar ou confusão súbita → regra fixa "ligue 192".
5. Na dúvida, chama um humano: se a leitura vier com confiança baixa, o agente pede outra foto ou encaminha ao farmacêutico.
6. LGPD: consentimento específico (registrado na própria plataforma), dados mínimos, nada compartilhado com a operadora para fins de preço.

### 2.4 Como medimos (harness)

| O que | Conjunto | Meta (regional) |
|---|---|---|
| Leitura de caixas | 50 fotos reais | ≥ 95% (princípio ativo + concentração) |
| Leitura de receita digital | 10 PDFs anonimizados | ≥ 95% |
| Leitura de manuscrita | 10 fotos | Medir e mostrar o número |
| Leitura de receita impressa (foto) | a definir (D19) | a definir (D19) |
| Interações e duplicidades | 30 pares conferidos por farmacêutico, dentro dos remédios da tabela curada (ver D7) | Recall ≥ 90% |
| Escalonamento | 20 relatos com conduta certa | 100% dos alarmes → 192 |
| Guardrail | 20 tentativas de arrancar dose | 0 respostas com dose |

---

## 3. Viabilidade

| Eixo | Situação | Comentário |
|---|---|---|
| **Prazo** | 🔴 **Crítico** | *(leitura minha)* O repositório ainda não tem código. Na trilha **Goiânia (24/10)** sobram cerca de 2 dias; na **Online (31/10)**, cerca de 9. A plataforma própria acrescenta uma frente de frontend ao MVP. Ver D11 e D16. |
| **Plataforma própria** | 🟢 Viável | *(leitura minha)* Sem cadastro na Meta, sem templates e sem número de teste. Navegadores modernos já fazem tudo de que precisamos: câmera e upload de arquivo, gravação de áudio e notificações push. O Web Push usa chaves que nós mesmos geramos, sem conta em terceiros. **A chave do LLM continua necessária** (D3). |
| **Notificação de lembrete** | 🟡 | *(leitura minha)* No iPhone, o push web só funciona se a plataforma for instalada na tela inicial (iOS 16.4+). No Android funciona direto no navegador. Na demo, o lembrete pode ser disparado na hora. |
| **Leitura** | 🟡 / 🔴 | Foto de receita impressa, caixa e PDF digital trazem texto impresso, e o modelo deve ler bem. *(leitura minha)* **A receita à mão agora está no caminho principal**, e é a entrada que os modelos leem pior (F1 ≈ 7,6% num estudo de 2024, sem ajuste fino). A confirmação obrigatória e o pedido de nova foto (ou da caixa) quando a confiança for baixa viram peças centrais da segurança. Ver D19. |
| **Normalização** | 🟢 Viável | Base da Anvisa e CMED são públicas. Falta checar o campo de princípio ativo no dicionário de dados. |
| **Farmacovigilância** | 🟢 Regional / 🟡 Final | **Regional:** viável. A checagem de mesmo princípio ativo sai do Normalizador, e a tabela curada à mão é pequena (~15–20 remédios). **Final:** é aqui que ficam as partes trabalhosas. DDInter e DrugBank só valem para uso não comercial, então é preciso licença. Bulas da Anvisa não têm API. O CBMPI precisa ser transcrito por completo. É preciso converter os nomes dos princípios ativos do português para o nome internacional, porque as bases de interação estão em inglês. |
| **Voz** | 🟢 Viável | STT do áudio gravado na plataforma; TTS do lembrete tocado na plataforma. |
| **Regulatório** | 🔴 Risco na final | Possível SaMD (RDC 657/2022 e 751/2022, provável classe II). O agente organiza e encaminha; o farmacêutico decide. Buscar parecer de especialista. |
| **LGPD** | 🟡 | Dado de saúde é sensível. *(leitura minha)* Com plataforma própria, a guarda dos dados é nossa: login, controle de acesso e armazenamento passam a ser responsabilidade do projeto. |
| **Adoção** | 🟡 Novo risco | *(leitura minha)* O plano apoiava o engajamento no "sem app para baixar, tudo no WhatsApp". Com plataforma própria, a cuidadora precisa abrir e, idealmente, instalar mais uma ferramenta. Vale perguntar isso nas entrevistas. |
| **Negócio** | 🟡 | O plano propõe a operadora como pagadora (PMPM) e a farmácia como canal. Ainda falta evidência. |

**Resumo *(leitura minha)*:** a plataforma própria tira a burocracia da Meta e nos dá controle da interface. Também deixa o painel do profissional da final mais natural, porque é a mesma plataforma com outro perfil. Em troca, ela soma uma frente de frontend a um prazo que já era crítico e cria o risco de adoção. Isso reforça a necessidade de combinar o caminho P0/P1 da demo (D16).

---

## 4. Possíveis saídas

### 4.1 Caminhos de negócio (do plano)

| Caminho | Quem paga | Papel no plano |
|---|---|---|
| A. Família (B2C) | Cuidadora, ~R$ 20–30/mês | Porta de entrada e prova de uso |
| **B. Operadoras (B2B2C)** ⭐ | Operadora, PMPM R$ 8–15 | **Pagador principal** |
| **C. Farmácias (B2B)** ⭐ | Farmácia, R$ 300–500/loja/mês | **Canal e trava regulatória** |
| D. SUS / ESF (B2G) | Prefeitura, edital | Piloto de impacto |
| E. Empresas (benefício) | RH | Expansão de longo prazo |
| F. Agências, home care, ILPIs | B2B SaaS | Canal e receita intermediária |

**Recomendação do plano:** a cuidadora familiar é a persona da história, a operadora é a pagadora e o farmacêutico é o canal e a trava regulatória.

### 4.2 Argumento para a banca

- **Teste de remoção:** sem o agente sobra um app de lembrete com digitação manual, que o MyTherapy já faz de graça. O valor que só o agente entrega é **ler, juntar, conversar e escalar**.
- **Contexto favorável:** Política Nacional de Cuidados (Lei 15.069/2024), Diretrizes do Cuidado Farmacêutico (2026) e receita digital.
- **Unit economics:** a PMPM de R$ 10 empata ao evitar ~5 internações por 1.000 idosos por ano (números ilustrativos).
- *(leitura minha)* A frase do plano "a Hippocratic AI para o cuidador brasileiro, **pelo WhatsApp**" precisa de nova redação.

### 4.3 Se a validação falhar (critérios de giro do plano)

- **A cuidadora diz que o remédio não é a dor:** girar para coordenação do cuidado entre familiares, com a mesma persona.
- **Farmacêutico e enfermeira dizem que não agiriam com base no resumo:** cortar o escalonamento e focar na cuidadora.

---

## 5. Registro de mudanças de escopo

| Data | Mudança (pedida pelo usuário) | Motivo | Partes do plano afetadas |
|---|---|---|---|
| 22/10/2026 | **Farmacovigilância reduzida no regional.** Fica a checagem de mesmo princípio ativo e uma tabela curada à mão (interações, duplicidade de classe, CBMPI) para os remédios da demo. Base licenciada, conversão de nomes em escala, CBMPI completo + Beers, RAG em bulas e efeito adverso × sintoma vão para a final. | Tirar do MVP a complexidade de dados (licença, conversão de nomes, bulas) sem perder o alerta da demo | §4.3 e §4.7 do plano (checagem), §4.5 (avaliação de pares), Parte 7 (dados de 18/10). Detalhes em [`escopo-por-fase.md`](escopo-por-fase.md). |
| 22/10/2026 | **Foto da receita física (impressa ou escrita à mão) vira entrada principal**, ao lado das fotos de caixa e do PDF da receita digital. A manuscrita deixa de ser bônus. | É o que a cuidadora mais tem em mãos: o médico costuma entregar a receita em papel | §4.2 e §4.7 do plano (entrada), §4.5 (avaliação), Parte 2.5 item 3 ("tirar a letra de médico do caminho principal"). Retoma a entrada do escopo original da avaliação. |
| 22/10/2026 | **WhatsApp substituído por plataforma própria.** Foto, PDF, áudio, conversa, lembretes e resumo passam a acontecer na plataforma da Seriema. | Evitar chaves e integrações trabalhosas, como as da Meta | Arquitetura (canal), §4.3 dados/canal, BMC (canais, relacionamento, custos "WhatsApp por conversa", parceria Meta), divisão do time ("WhatsApp, voz e PDF"), frases do pitch ("sem app para baixar", "pelo WhatsApp"). Os documentos em `docs/` **não foram editados**. |
