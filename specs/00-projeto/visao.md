# Visão do projeto — Seriema (F3: cuidador familiar e a medicação do idoso)

> Resumo da minha leitura do projeto. **Última revisão: 23/10/2026** (respostas da discussão incorporadas).
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

O sistema tem três camadas: a **plataforma** (o que a cuidadora vê), o **harness agêntico** (o que transforma o modelo em agente) e as **ferramentas de dados** (os fatos clínicos determinísticos).

```
  Plataforma Seriema (PWA, mobile-first)
  conversa · foto da receita/caixa · PDF · gravação de áudio · notificações
                          │
                       [API]  ← contas, banco, arquivos, agendador
                          │
 ┌──────────────────────── HARNESS AGÊNTICO ─────────────────────────┐
 │                                                                    │
 │  PERCEPÇÃO            MEMÓRIA E ESTADO            MODELO (LLM)     │
 │  foto/PDF → Leitor    perfil do idoso             raciocina e      │
 │  áudio → STT          lista de remédios versionada  escolhe a      │
 │  estado do banco      histórico da conversa         próxima ação   │
 │  eventos (lembrete)   pendências (itens não confirmados)           │
 │                                │                                   │
 │                    LOOP DE DECISÃO (Orquestrador)                  │
 │          observa → decide → chama ferramenta → observa → responde  │
 │                                │                                   │
 │  FERRAMENTAS (ações)                                               │
 │  normalizar · checar_lista · avaliar_gravidade   ← dados (C)       │
 │  salvar_lista_confirmada · agendar_lembrete · registrar_dose       │
 │  registrar_sintoma · gerar_resumo · escalar      ← API (A)         │
 │                                │                                   │
 │  GUARDRAILS                                                        │
 │  regras fixas antes do modelo (192) · confirmação humana para      │
 │  ações que mudam a lista · Auditor em toda saída                   │
 └────────────────────────────────────────────────────────────────────┘
```

#### O que é o harness agêntico

**Harness** é tudo o que envolve o modelo para que ele **perceba o ambiente, tome decisões e realize ações**, deixando de ser apenas um gerador de texto. O modelo sozinho só responde a um texto. Com o harness, ele vê a foto da receita, lembra o que o idoso toma, consulta a base de interações, agenda o lembrete e decide quando escalar, sempre dentro de regras que ele não consegue furar.

> Nas referências em `docs/`, essas peças aparecem como "agentes" (Leitor, Orquestrador, Diário, Auditor...). Aqui elas são **componentes de um único harness**. O argumento do plano para a banca continua valendo: cada componente tem entrada e saída próprias, e o Auditor é um verificador independente.

| Camada do harness | Componente | O que faz | Tipo | Dono |
|---|---|---|---|---|
| **Percepção** | **Leitor** | Foto de receita física (impressa ou à mão), foto de caixa e PDF → itens estruturados com confiança | LLM com visão | B |
| | **Escuta** | Áudio da cuidadora → texto (STT) | Voz | B |
| | **Contexto** | Lê do banco o perfil, a lista atual, as doses e o diário antes de cada decisão | Leitura de estado | B (sobre funções de A) |
| **Memória e estado** | **Memória** | Perfil do idoso, lista de remédios versionada, histórico da conversa, pendências | Banco | A (schema) + B (uso) |
| **Decisão** | **Orquestrador** | Loop: recebe as observações, decide a próxima ação, chama ferramentas, observa o resultado e responde | LLM + tool use | B |
| **Ações (ferramentas)** | **Normalizador** | Nome comercial → princípio ativo (Anvisa/CMED) | Determinístico | C |
| | **Farmacovigilante** | **Regional:** mesmo princípio ativo em nomes diferentes + tabela curada (interações, duplicidade de classe, CBMPI). **Final:** bases completas, Beers, RAG em bulas | Determinístico | C |
| | **Regras de gravidade** | Sintoma estruturado → conduta (192, 24h, observar) | Determinístico | C |
| | **Rotina** | Salvar lista confirmada, montar cronograma, agendar lembrete, registrar dose | Determinístico | A (API) |
| | **Diário + Escalonador** | Registrar sintoma, perguntar o que falta, gerar o resumo e escalar | LLM + regras | B |
| | **Fala** | Texto do lembrete → áudio (TTS) | Voz | B |
| **Guardrails** | **Regras fixas** | Sinal de alarme vai para "ligue 192" sem passar pelo modelo | Determinístico | B + C |
| | **Confirmação humana** | Ações que mudam a lista ou o cronograma só valem depois do "confirmo" da cuidadora | Fluxo fixo | B |
| | **Auditor** | Bloqueia saída com remédio fora da lista, frase proibida ou fato clínico sem fonte | Verificador independente | B |
| **Observabilidade** *(P1, D21)* | **Registro de passos** | Guarda cada observação, ferramenta chamada, resultado e bloqueio do Auditor | Log | B |

Fora do harness ficam a **plataforma e a API** (Pessoa A) e a **avaliação** (Pessoa C), que mede o harness de fora.

### 2.2 MVP (regional) × evolução (final)

| | **Regional** (24/10 ou 31/10) | **Final** (28/11) |
|---|---|---|
| Plataforma | Área da cuidadora, **PWA instalável**: conversa, envio de foto/PDF/áudio, lista, cronograma, diário, resumo | + painel do profissional |
| Entrada | **Foto da receita física (impressa ou à mão)** + fotos de caixas + PDF de receita digital, sempre com confirmação | Código de barras da caixa |
| Normalização | ~20 remédios (D16) | Ampliada |
| Checagem | **Mesmo princípio ativo** em nomes diferentes (sai do Normalizador) + **tabela curada** com os remédios da demo, **gerada e conferida com LLM** (D7.2, D15.4): pares de interação, grupos para duplicidade de classe e itens do CBMPI, cada linha com fonte | Base de interações completa e licenciada; conversão de nomes PT → internacional em escala; CBMPI completo + Beers; RAG em bulas; efeito adverso × sintoma relatado |
| Rotina | Lembrete por notificação (texto e áudio); confirmação de dose | Aviso de estoque e renovação de receita |
| Diário | Áudio → sintoma → regra de gravidade | Tendências ("3 dias de tontura") |
| Escalonamento | Resumo em PDF + link sem conta para o profissional (D9) | Painel do farmacêutico ou da enfermeira com fila de casos |
| Prova | Avaliação (seção 2.4) + 5 a 10 entrevistas | Piloto de 2 semanas com 5–10 famílias + carta de intenção |

### 2.3 Guardrails (inegociáveis)

1. Nunca sugere dose, troca ou suspensão. Todo alerta termina em "leve ao farmacêutico ou médico", e o Auditor bloqueia frases proibidas.
2. Nada vira cronograma sem a confirmação da cuidadora.
3. Fatos clínicos vêm só de ferramenta (interações, CBMPI, bula), com fonte citada. O LLM só explica.
4. Sinal de alarme não passa pelo LLM. Queda com batida na cabeça, dor no peito, falta de ar ou confusão súbita → regra fixa "ligue 192".
5. Na dúvida, chama um humano: se a leitura vier com confiança baixa, o agente pede outra foto ou encaminha ao farmacêutico.
6. LGPD: consentimento específico (registrado na própria plataforma), dados mínimos, nada compartilhado com a operadora para fins de preço.

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
| Guardrail | 20 tentativas de arrancar dose | 0 respostas com dose |

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
| **Plataforma própria** | 🟢 Viável | *(leitura minha)* Sem cadastro na Meta, sem templates e sem número de teste. Navegadores modernos já fazem tudo de que precisamos: câmera e upload de arquivo, gravação de áudio e notificações push. O Web Push usa chaves que nós mesmos geramos, sem conta em terceiros. Com o modelo open-source local (D3), **nenhuma chave de API** é necessária no regional. |
| **Notificação de lembrete** | 🟡 | *(leitura minha)* No iPhone, o push web só funciona se a plataforma for instalada na tela inicial (iOS 16.4+). No Android funciona direto no navegador. Na demo, o lembrete pode ser disparado na hora. |
| **Leitura** | 🟡 / 🔴 | Foto de receita impressa, caixa e PDF digital trazem texto impresso, e o modelo deve ler bem. *(leitura minha)* **A receita à mão agora está no caminho principal**, e é a entrada que os modelos leem pior (F1 ≈ 7,6% num estudo de 2024, sem ajuste fino). A confirmação obrigatória e o pedido de nova foto (ou da caixa) quando a confiança for baixa viram peças centrais da segurança. Ver D19. |
| **Normalização** | 🟢 Viável | Base da Anvisa e CMED são públicas. Falta checar o campo de princípio ativo no dicionário de dados. |
| **Farmacovigilância** | 🟢 Regional / 🟡 Final | **Regional:** viável. A checagem de mesmo princípio ativo sai do Normalizador, e a tabela curada é pequena (~20 remédios) e gerada com LLM (D7.2). **Final:** é aqui que ficam as partes trabalhosas. DDInter e DrugBank só valem para uso não comercial, então é preciso licença. Bulas da Anvisa não têm API. O CBMPI precisa ser transcrito por completo. É preciso converter os nomes dos princípios ativos do português para o nome internacional, porque as bases de interação estão em inglês. |
| **Voz** | 🟢 Viável | STT do áudio gravado na plataforma; TTS do lembrete tocado na plataforma. |
| **Modelo local em CPU** | 🟡 / 🔴 | *(leitura minha)* Modelos open-source locais (D3) em máquina sem GPU (D22): sem chave e sem dado saindo para um provedor de IA, mas modelos pequenos leem pior (sobretudo a receita à mão) e cada foto pode levar bem mais que alguns segundos. Mitigações na `spec.md` §3: processamento assíncrono, imagem reduzida, teste de bancada dos modelos e vídeo de backup da demo. |
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
