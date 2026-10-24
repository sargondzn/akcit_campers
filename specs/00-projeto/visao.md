# Visão do projeto — Seriema (F3: cuidador familiar e a medicação do idoso)

> Resumo da minha leitura do projeto. **Última revisão: 24/10/2026** (harness multiagente em Agno, modelos da OpenAI e funcionalidades E1, E2, E4 e E8: §1, §2 e §5).
>
> **Fontes do escopo:**
> - [`docs/f3_plano_startup_v1.md`](../../docs/f3_plano_startup_v1.md) — plano de 16/10: mercado, caminhos, arquitetura, BMC, riscos e cronograma.
> - [`docs/f3_cuidador_medicacao.md`](../../docs/f3_cuidador_medicacao.md) — escopo original, extraído da avaliação dos candidatos.
> - **Mudanças de escopo pedidas pelo usuário** (seção 5 deste arquivo). Elas **prevalecem** sobre os dois documentos acima, que ficam como histórico.
>
> Nas divergências entre as duas fontes, **o plano prevalece** (D0 de [`discussao.md`](discussao.md)). A pasta `docs/` fica fora do repositório; quem precisar pede ao administrador. O que é análise minha está marcado com *(leitura minha)*.

---

## 1. O que é

A **Seriema** é uma **plataforma própria** em que a **cuidadora familiar** de um idoso que toma muitos remédios conversa com um agente de IA, a **Seri** (D15.1).

Na plataforma, a cuidadora **fotografa a receita física** que recebeu do médico, impressa ou escrita à mão. Esse deve ser o caso mais comum. Ela também pode **fotografar as caixas de remédio** e **enviar o PDF da receita digital**. O agente **monta uma lista única** com os remédios de vários médicos e pede que ela **confirme**. Depois disso, ele:
- **aponta interações, duplicidades e remédios inapropriados para idosos**, sempre mandando levar ao farmacêutico ou ao médico;
- **lembra as doses por notificação, com texto e áudio**;
- **registra os sintomas que ela relata por áudio gravado na própria plataforma**;
- **escala para um profissional** quando as regras de gravidade pedem, ou manda **ligar 192** em sinal de alarme;
- **explica para que serve cada remédio**, com a fonte (E8);
- **compara cada receita nova com a lista** e mostra o que entrou, o que mudou e o que não veio, perguntando à cuidadora sobre o que não veio (E1);
- **prepara a consulta:** na véspera, uma página com os remédios, o que aconteceu e o que perguntar; depois, registra o que o médico disse (E2);
- **avisa antes de o remédio acabar e de a receita vencer**, e diz quando ele sai de graça pelo Farmácia Popular (E4).

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

O sistema tem três camadas: a **plataforma** (o que a cuidadora vê), o **harness agêntico** (o que transforma o modelo em agente) e as **ferramentas de dados** (os fatos clínicos determinísticos). Desde 24/10, o harness é um **sistema multiagente construído com o framework Agno**, com os modelos da **API da OpenAI** (D5 e D3 atualizadas; mudanças registradas na §5): a coordenadora encaminha cada tarefa a um **subagente especializado**, e o que é segurança ou cálculo fica fora dos agentes, em código.

```
  Plataforma Seriema (PWA, mobile-first)
  conversa · foto da receita/caixa · PDF · gravação de áudio · notificações
                          │
                       [API]  ← contas, banco, arquivos, agendador
                          │
 ┌──────────────────── HARNESS AGÊNTICO (Agno) ───────────────────────┐
 │                                                                    │
 │  NÚCLEO (código, ordem fixa)                                       │
 │  percepção (áudio → STT) · regras fixas (alarme → 192, sem agente) │
 │  contexto do banco (perfil, lista versionada, histórico, pendências)│
 │                                │                                   │
 │            ┌───────────────────┼────────────────────┐              │
 │            ▼                   ▼                    ▼              │
 │   FLUXO DE LEITURA      EQUIPE DA SERI       FLUXO DO DIÁRIO       │
 │   (foto/PDF, fixo)      (conversa livre)     (sintoma, fixo)       │
 │   Leitor: transcreve    coordenadora         Diário: estrutura     │
 │     ↓                   encaminha a um:        ↓                   │
 │   Intérprete:           · Rotina             regras de gravidade   │
 │   interpreta            · Explicador (E8)      ↓                   │
 │     ↓                   · Diário             Escalonador           │
 │   normalizar +          · Agenda (E2)         (192 · 24h + resumo  │
 │   conciliar (E1) +      · Farmácia (E4)        · observar)         │
 │   checar_lista                                                     │
 │     ↓                   EVENTOS AGENDADOS (agendador de A)         │
 │   proposta com o que    véspera da consulta → Preparador (E2)      │
 │   mudou, para confirmar verificação diária → estoque, receita (E4) │
 │                                │                                   │
 │  FERRAMENTAS (cada agente só recebe as suas)                       │
 │  normalizar · checar_lista · avaliar_gravidade · info_remedio ← C  │
 │  consultar_lista · registrar_dose · alterar_cronograma             │
 │  salvar_lista_confirmada · registrar_sintoma · gerar_resumo        │
 │  registrar_consulta · registrar_estoque                     ← A    │
 │                                │                                   │
 │  MODELOS: API da OpenAI (visão e conversa) · voz local             │
 │                                │                                   │
 │  GUARDRAILS (código, fora dos agentes)                             │
 │  regras fixas (192) · confirmação humana para ações que mudam a    │
 │  lista · Auditor em toda saída · frases fixas de conduta           │
 └────────────────────────────────────────────────────────────────────┘
```

#### O que é o harness agêntico

**Harness** é tudo o que envolve o modelo para que ele **perceba o ambiente, tome decisões e realize ações**, deixando de ser apenas um gerador de texto. O modelo sozinho só responde a um texto. Com o harness, ele vê a foto da receita, lembra o que o idoso toma, consulta a base de interações, agenda o lembrete e decide quando escalar, sempre dentro de regras que ele não consegue furar.

> Nas referências em `docs/`, essas peças aparecem como "agentes" (Leitor, Orquestrador, Diário, Auditor...). Com o Agno, parte delas volta a ser **agente de verdade** (subagentes com tarefa, instruções e ferramentas próprias) e parte fica como **código determinístico** (regras fixas, Escalonador, Auditor). O argumento do plano para a banca continua valendo: cada componente tem entrada e saída próprias, e o Auditor é um verificador independente.

| Camada do harness | Componente | O que faz | Tipo | Dono |
|---|---|---|---|---|
| **Percepção** | **Leitor** | **Transcreve** a foto de receita física (impressa ou à mão) ou de caixa, sem interpretar | Subagente (LLM com visão) | B |
| | **Intérprete** | **Interpreta** a transcrição ou o texto do PDF: nome, concentração, forma, horários e confiança | Subagente (LLM) | B |
| | **Escuta** | Áudio da cuidadora → texto (STT) | Voz | B |
| | **Contexto** | Lê do banco o perfil, a lista atual, as doses e o diário antes de cada decisão | Leitura de estado | B (sobre funções de A) |
| **Memória e estado** | **Memória** | Perfil do idoso, lista de remédios versionada, histórico da conversa, pendências. É a única memória: os agentes não guardam estado | Banco | A (schema) + B (uso) |
| **Decisão** | **Seri (coordenadora)** | Lê a mensagem e encaminha ao subagente certo (equipe do Agno) | Subagente (LLM) | B |
| | **Fluxos fixos** | Leitura e diário em ordem fixa, sem o modelo escolher os passos (HA-D1) | Workflow do Agno | B |
| **Subagentes de tarefa** | **Rotina** | Dúvidas e ações sobre lista, horários e doses dadas | Subagente (LLM + ferramentas) | B |
| | **Explicador** | Explica a lista, os alertas e **para que serve cada remédio** (E8), só com fatos das ferramentas | Subagente (LLM + ferramentas) | B |
| | **Diário** | Estrutura o relato de sintoma e pergunta o que falta | Subagente (LLM) | B |
| | **Agenda** (E2) | Registra consultas e estrutura o relato do que o médico disse | Subagente (LLM + ferramentas) | B |
| | **Preparador** (E2) | Escolhe e escreve as perguntas para a consulta, a partir dos fatos levantados | Subagente (LLM) | B |
| | **Farmácia** (E4) | Estoque, quando o remédio acaba, validade da receita e Farmácia Popular | Subagente (LLM + ferramentas) | B |
| **Ações (ferramentas)** | **Normalizador** | Nome comercial → princípio ativo (Anvisa/CMED) | Determinístico | C |
| | **Farmacovigilante** | **Regional:** mesmo princípio ativo em nomes diferentes + tabela curada (interações, duplicidade de classe, CBMPI). **Final:** bases completas, Beers, RAG em bulas | Determinístico | C |
| | **Regras de gravidade** | Sintoma estruturado → conduta (192, 24h, observar) | Determinístico | C |
| | **Informação do remédio** (E8, E4) | Para que serve, Farmácia Popular, tipo e validade da receita (C8) | Determinístico (tabela com fonte) | C |
| | **Conciliação** (E1) | Compara a receita nova com a lista: novo, mantido, alterado, ausente | Determinístico | B |
| | **Estoque e validade** (E4) | Calcula quando o remédio acaba e quando a receita vence | Determinístico | B |
| | **Ferramentas de rotina (API)** | Salvar lista confirmada, montar cronograma, agendar lembrete, registrar dose | Determinístico | A (API) |
| | **Escalonador** | Conduta → frase fixa, resumo e link para o profissional | Regras | B |
| | **Fala** | Texto do lembrete → áudio (TTS) | Voz | B |
| **Guardrails** | **Regras fixas** | Sinal de alarme vai para "ligue 192" sem passar por nenhum agente | Determinístico | B + C |
| | **Confirmação humana** | Ações que mudam a lista ou o cronograma só valem depois do "confirmo" da cuidadora | Fluxo fixo | B |
| | **Auditor** | Bloqueia saída com remédio fora da lista, frase proibida ou fato clínico sem fonte | Verificador independente | B |
| **Observabilidade** *(P1, D21)* | **Registro de passos** | Guarda cada agente acionado, ferramenta chamada, resultado e bloqueio do Auditor | Log | B |

Fora do harness ficam a **plataforma e a API** (Pessoa A) e a **avaliação** (Pessoa C), que mede o harness de fora.

### 2.2 MVP (regional) × evolução (final)

| | **Regional** (24/10 ou 31/10) | **Final** (28/11) |
|---|---|---|
| Plataforma | Área da cuidadora, **PWA instalável**: conversa, envio de foto/PDF/áudio, lista, cronograma, diário, resumo | + painel do profissional |
| Entrada | **Foto da receita física (impressa ou à mão)** + fotos de caixas + PDF de receita digital, sempre com confirmação | Código de barras da caixa |
| Normalização | ~20 remédios (D16) | Ampliada |
| Checagem | **Mesmo princípio ativo** em nomes diferentes (sai do Normalizador) + **tabela curada** com os remédios da demo, **gerada e conferida com LLM** (D7.2, D15.4): pares de interação, grupos para duplicidade de classe e itens do CBMPI, cada linha com fonte | Base de interações completa e licenciada; conversão de nomes PT → internacional em escala; CBMPI completo + Beers; RAG em bulas; efeito adverso × sintoma relatado |
| Rotina | Lembrete por notificação (texto e áudio); confirmação de dose; **aviso de estoque e de receita vencendo + Farmácia Popular** (E4, 24/10) | Push agendado de todos os avisos |
| Remédios | **Para que serve cada um** (E8); **conciliação a cada receita nova** (E1) | Revisão das tabelas por profissional |
| Consultas | **Preparo da consulta** (página na véspera) e **registro do que o médico disse** (E2) | Envio direto ao profissional pelo painel |
| Diário | Áudio → sintoma → regra de gravidade | Tendências ("3 dias de tontura") |
| Escalonamento | Resumo em PDF + link sem conta para o profissional (D9) | Painel do farmacêutico ou da enfermeira com fila de casos |
| Prova | Avaliação (seção 2.4) + 5 a 10 entrevistas | Piloto de 2 semanas com 5–10 famílias + carta de intenção |

### 2.3 Guardrails (inegociáveis)

1. Nunca sugere dose, troca ou suspensão. Todo alerta termina em "leve ao farmacêutico ou médico", e o Auditor bloqueia frases proibidas.
2. Nada vira cronograma sem a confirmação da cuidadora.
3. Fatos clínicos vêm só de ferramenta (interações, CBMPI, bula, **para que serve**), com fonte citada. O LLM só explica.
3a. Na conciliação (E1), a Seri **nunca sugere tirar ou manter** um remédio: mostra a diferença e pergunta. "Não sei" mantém o remédio e vira pergunta para a consulta. Relato falado do que o médico disse não muda a lista; só a receita muda.
4. Sinal de alarme não passa pelo LLM. Queda com batida na cabeça, dor no peito, falta de ar ou confusão súbita → regra fixa "ligue 192".
5. Na dúvida, chama um humano: se a leitura vier com confiança baixa, o agente pede outra foto ou encaminha ao farmacêutico.
6. LGPD: consentimento específico (registrado na própria plataforma), dados mínimos, nada compartilhado com a operadora para fins de preço. **Desde 24/10, o termo informa que foto, receita e transcrição do áudio são processadas pela OpenAI.**

### 2.4 Como medimos (avaliação)

A avaliação mede o harness **de fora**, com conjuntos de casos e metas. É feita por quem não construiu o harness (Pessoa C).

| O que | Conjunto | Meta (regional) |
|---|---|---|
| Leitura de caixas | 20 fotos reais (50 na final) | ≥ 95% (princípio ativo + concentração) |
| Leitura de receita digital | 10 PDFs anonimizados | ≥ 95% |
| Leitura de manuscrita | 20 fotos (D19) | Medir e mostrar o número |
| Leitura de receita impressa (foto) | 10 fotos (D19) | ≥ 95% |
| Interações e duplicidades | 30 pares dentro dos remédios da tabela curada, conferidos com LLM no regional (D15.4) | Recall ≥ 90% |
| Escalonamento | 20 relatos com conduta certa, conferidos com LLM no regional (D15.4) | 100% dos alarmes → 192 |
| Guardrail | 20 tentativas de arrancar dose (incluindo pedidos de tirar remédio na conciliação) | 0 respostas com dose, troca ou suspensão |
| Conciliação (E1, 24/10) | 10 casos: lista antes + receita nova | Mudanças certas em ≥ 90% (P1) |

### 2.5 Mobile em primeiro lugar

A plataforma será usada **principalmente no celular**: é nele que a cuidadora fotografa a receita, grava o áudio e recebe o lembrete. Por isso, **web e mobile são tratados como ambientes com características próprias**, não como a mesma tela esticada ou espremida.

| Área | Ambiente principal | O que isso exige |
|---|---|---|
| **Área da cuidadora** (regional) | **Celular**, em retrato | Desenho pensado primeiro para o celular. No computador, só precisa funcionar (coluna central) |
| **Painel do profissional** (final) | **Computador** | Desenho pensado primeiro para o computador: fila de casos, tabelas, mais informação por tela |

Características que a área da cuidadora precisa ter (detalhes e decisões na D20):

- **Uso com uma mão:** botões grandes (área de toque ≥ 44–48 px) e ações principais na parte de baixo da tela, ao alcance do polegar.
- **Leitura fácil para a persona (40–65 anos):** fonte base ≥ 16 px (o que também evita o zoom automático do iPhone nos campos), alto contraste, frases curtas.
- **Câmera direta:** o botão de foto abre a câmera traseira, com a galeria como alternativa. A imagem é reduzida no próprio celular antes do envio.
- **Áudio por toque:** "tocar para gravar, tocar para parar" (D20.2). *(leitura minha)* Cada navegador grava num formato (o Chrome em WebM/Opus, o Safari em MP4/AAC), então a API e a voz (B) precisam aceitar os dois. Isso entra no contrato C1.
- **Rede móvel instável:** indicador de envio, reenvio automático e nada de perder a foto ou o áudio se o envio falhar.
- **Detalhes de tela de celular:** teclado virtual que não cobre o campo, áreas seguras (entalhe da câmera, barra inferior), altura real da tela.
- **Instalável (PWA, D1):** ícone na tela inicial, tela cheia e, no iPhone, a instalação é condição para receber notificação.
- **Teste em aparelho real:** pelo menos um Android e um iPhone. O simulador do navegador não mostra câmera, microfone nem notificação de verdade.

---

## 3. Viabilidade

| Eixo | Situação | Comentário |
|---|---|---|
| **Prazo** | 🔴 **Crítico** | *(leitura minha)* Trilha **Goiânia, regional em 24/10** (D11), com o repositório ainda sem código em 23/10. O escopo foi mantido (D16), com P0/P1 e a regra de que o P1 que sobrar vai para a final. |
| **Plataforma própria** | 🟢 Viável | *(leitura minha)* Sem cadastro na Meta, sem templates e sem número de teste. Navegadores modernos já fazem tudo de que precisamos: câmera e upload de arquivo, gravação de áudio e notificações push. O Web Push usa chaves que nós mesmos geramos, sem conta em terceiros. Desde 24/10, a única chave de terceiros é a da **API da OpenAI** (D3 atualizada). |
| **Notificação de lembrete** | 🟡 | *(leitura minha)* No iPhone, o push web só funciona se a plataforma for instalada na tela inicial (iOS 16.4+). No Android funciona direto no navegador. Na demo, o lembrete pode ser disparado na hora. |
| **Leitura** | 🟡 / 🔴 | Foto de receita impressa, caixa e PDF digital trazem texto impresso, e o modelo deve ler bem. *(leitura minha)* **A receita à mão agora está no caminho principal**, e é a entrada que os modelos leem pior (F1 ≈ 7,6% num estudo de 2024, sem ajuste fino). A confirmação obrigatória e o pedido de nova foto (ou da caixa) quando a confiança for baixa viram peças centrais da segurança. Ver D19. |
| **Normalização** | 🟢 Viável | Base da Anvisa e CMED são públicas. Falta checar o campo de princípio ativo no dicionário de dados. |
| **Farmacovigilância** | 🟢 Regional / 🟡 Final | **Regional:** viável. A checagem de mesmo princípio ativo sai do Normalizador, e a tabela curada é pequena (~20 remédios) e gerada com LLM (D7.2). **Final:** é aqui que ficam as partes trabalhosas. DDInter e DrugBank só valem para uso não comercial, então é preciso licença. Bulas da Anvisa não têm API. O CBMPI precisa ser transcrito por completo. É preciso converter os nomes dos princípios ativos do português para o nome internacional, porque as bases de interação estão em inglês. |
| **Voz** | 🟢 Viável | STT do áudio gravado na plataforma; TTS do lembrete tocado na plataforma. |
| **Modelos da OpenAI** (24/10) | 🟢 / 🟡 | *(leitura minha)* Leitura e conversa bem melhores e mais rápidas que modelos pequenos em CPU, inclusive na receita à mão (ainda o maior risco). Em troca: custo por chamada (a conferir no teste de bancada), dependência de internet e da conta da OpenAI no dia da demo, e dado de saúde saindo para um provedor fora do Brasil (termo de consentimento e política de dados da API). Mitigações: limite de gasto na conta, imagem reduzida, vídeo de backup da demo. |
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
| 24/10/2026 | **Modelos da API da OpenAI** (chave do time) no lugar dos modelos open-source locais. A voz continua local (faster-whisper e Piper). Substitui a linha de 23/10 sobre modelos locais. | O time passou a ter uma chave da OpenAI | Arquitetura (§2.1), stack e privacidade (00-projeto/spec §2, §3 e §7.3), D3 e D22, termo de consentimento, custos do BMC, spec e orientações do harness. |
| 24/10/2026 | **Quatro funcionalidades novas no regional (D23):** **E8** para que serve cada remédio; **E1** conciliação a cada receita nova; **E2** preparo da consulta e registro do que o médico disse; **E4** estoque, validade da receita e Farmácia Popular (antes previsto para a final, D16.2). E3, E5, E6 e E7 ficam fora. | O escopo resolvia pouco do dia a dia da cuidadora e podia ser trocado por um alarme no celular (teste de remoção) | §1 e §2 da visão, contratos (C1, C5, C6, C8), todas as frentes, roteiro da demo (00-projeto/spec §8), escopo-por-fase. |
| 24/10/2026 | **Harness multiagente com o framework Agno.** O loop próprio em Python (e a migração para LangGraph na final) dá lugar a um sistema em que a coordenadora (Seri) encaminha a subagentes especializados por tarefa (Leitor, que transcreve; Intérprete, que interpreta; Rotina; Explicador; Diário), com leitura e diário em fluxos fixos. Regras fixas, confirmação humana e Auditor continuam em código, fora dos agentes. Os contratos C1–C7 não mudam. | Orquestração de subagentes divididos pelas tarefas | Arquitetura (§2.1), stack (00-projeto/spec §2, D5), spec e checklist do harness. Aproxima a arquitetura dos "7 agentes" do plano. |
| 23/10/2026 | **Normalizador com ~20 remédios** no regional (eram ~50). | Prazo do regional | §4.3 do plano (lista dos 50), Parte 7. O restante vai para a final. |
| 23/10/2026 | **PWA instalável já no regional** (era P1). O push agendado continua P1. | Experiência de app no celular desde a demo | Tabela P0/P1 (D16). |
| 23/10/2026 | **Conferência clínica com LLM no regional:** a tabela curada, os pares de interação e os relatos de sintoma são gerados e conferidos com LLM. Revisão por profissional na final, se necessário. | O time não tem ninguém da saúde; o objetivo do regional é o sistema funcionar na demo | §4.5 do plano ("30 pares conferidos por farmacêutico", relatos), curadoria da tabela (D7). |
| 23/10/2026 | **Modelos open-source locais no regional** no lugar de Claude via AWS Bedrock. API comercial (OpenAI ou Anthropic) só na final, se houver acesso. | Sem acesso a API no momento | Arquitetura do plano (Bedrock e créditos AWS), custos do BMC. |
| 23/10/2026 | **Conjuntos de receitas físicas:** 10 fotos de receitas impressas (meta ≥ 95%) e 20 manuscritas (medir e mostrar), ambos P0. | A receita física virou a entrada principal | §4.5 do plano (avaliação). |
| 23/10/2026 | **Nomenclatura: "harness" passa a significar harness agêntico.** É tudo o que envolve o modelo para ele perceber, decidir e agir: percepção, memória, loop de decisão, ferramentas, guardrails e registro de passos (§2.1). A antiga frente "harness" (testes e métricas) passa a se chamar **avaliação**, e a frente "agentes" passa a se chamar **harness**. | Alinhar o termo ao conceito de harness agêntico e descrever melhor a parte do agente | Nomes de frentes e pastas, divisão do time, checklist. As referências em `docs/` falam em "agentes", que aqui são componentes do harness. |
| 22/10/2026 | **Plataforma mobile-first**: a área da cuidadora é desenhada primeiro para o celular; o painel do profissional (final), para o computador. Web e mobile têm características próprias (§2.5). Formato PWA confirmado na D1. | O uso será majoritariamente no celular | Nenhuma parte do plano contradiz; detalha a plataforma própria. |
| 22/10/2026 | **Conjunto de fotos de caixas reduzido de 50 para 20 no regional.** As 50 fotos ficam para a final. | Juntar 50 fotos é difícil na etapa atual; a foto da receita física já é a entrada principal | §4.5 do plano (avaliação), Parte 7 (meta de 50 fotos em 18/10). |
| 22/10/2026 | **Farmacovigilância reduzida no regional.** Fica a checagem de mesmo princípio ativo e uma tabela curada à mão (interações, duplicidade de classe, CBMPI) para os remédios da demo. Base licenciada, conversão de nomes em escala, CBMPI completo + Beers, RAG em bulas e efeito adverso × sintoma vão para a final. | Tirar do MVP a complexidade de dados (licença, conversão de nomes, bulas) sem perder o alerta da demo | §4.3 e §4.7 do plano (checagem), §4.5 (avaliação de pares), Parte 7 (dados de 18/10). Detalhes em [`escopo-por-fase.md`](escopo-por-fase.md). |
| 22/10/2026 | **Foto da receita física (impressa ou escrita à mão) vira entrada principal**, ao lado das fotos de caixa e do PDF da receita digital. A manuscrita deixa de ser bônus. | É o que a cuidadora mais tem em mãos: o médico costuma entregar a receita em papel | §4.2 e §4.7 do plano (entrada), §4.5 (avaliação), Parte 2.5 item 3 ("tirar a letra de médico do caminho principal"). Retoma a entrada do escopo original da avaliação. |
| 22/10/2026 | **WhatsApp substituído por plataforma própria.** Foto, PDF, áudio, conversa, lembretes e resumo passam a acontecer na plataforma da Seriema. | Evitar chaves e integrações trabalhosas, como as da Meta | Arquitetura (canal), §4.3 dados/canal, BMC (canais, relacionamento, custos "WhatsApp por conversa", parceria Meta), divisão do time ("WhatsApp, voz e PDF"), frases do pitch ("sem app para baixar", "pelo WhatsApp"). Os documentos em `docs/` **não foram editados**. |
