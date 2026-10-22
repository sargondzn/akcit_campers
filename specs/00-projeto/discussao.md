# Discussão — 00-projeto (escopo, stack, frentes e prazos)

> **Revisada em 22/10/2026:** o WhatsApp saiu e entrou a plataforma própria (ver [`visao.md`](visao.md) §5).
> Responda no campo **Resposta** de cada item. A `spec.md` só será escrita depois das respostas.
> Cada decisão traz contexto, opções e uma recomendação minha; a decisão é sua.

**Ordem sugerida:** D11 (prazo) → D0 (fonte do escopo) → D1 e D17 (plataforma) → D15 → D16. As outras dependem dessas.

---

## D11 — Prazo, trilha e situação atual 🔴

**Contexto:** o repositório ainda não tem código.

**Perguntas:**
1. A inscrição foi feita? Em qual trilha: **Goiânia (24/10)** ou **Online (31/10)**?
2. A entrega é a do plano (GitHub com protótipo, BMC, pitch e documentação do fluxo; pitch de 3 min com demo ao vivo)? Algo muda na trilha Online?
3. O que já foi feito fora do repositório: entrevistas, fotos de caixas, dados baixados, acesso ao DDInter/DrugBank?
4. As entrevistas confirmaram que o remédio é a dor, ou houve giro?

**Resposta:**

---

## D0 — Fonte do escopo e divergências

**Contexto:** as duas referências em `docs/` divergem em alguns pontos. O canal já está resolvido pela mudança de 22/10 (plataforma própria).

| Tema | `f3_cuidador_medicacao.md` (avaliação) | `f3_plano_startup_v1.md` (plano) |
|---|---|---|
| Entrada principal | Foto da receita | Fotos de caixas + PDF de receita digital; manuscrita como bônus |
| Componentes | Leitor, Normalizador, Checador, Diário, Escalonador | + Orquestrador, Farmacovigilante (duplicidade, CBMPI, bulas), Rotina, **Auditor** |
| Destino do escalonamento | Enfermeira da ESF | Farmacêutico / ESF / consulta, via **resumo em PDF** |
| Sinal de alarme | Não mencionado | Regra fixa → "ligue 192" |
| Evolução (28/11) | Painel da ESF + piloto | Painel do farmacêutico **ou** enfermeira + piloto + manuscrita, código de barras, estoque, tendências |
| Avaliação | Acurácia da leitura + recall de interações | 6 conjuntos com metas (visão §2.4) |

**Pergunta:** o **plano prevalece** sobre o escopo original nessas divergências, respeitadas as mudanças de escopo da visão §5? (Recomendação: sim.)

**Resposta:**

---

## D1 — Formato da plataforma

**Contexto:** a plataforma precisa de câmera ou upload (foto e PDF), gravação de áudio, reprodução de áudio, notificações de lembrete e, na final, um painel do profissional.

| Opção | Prós | Contras |
|---|---|---|
| **A. Web app responsivo instalável (PWA)** | Um código só para celular e computador; sem loja de apps; câmera, áudio e push pelo navegador; o painel da final sai da mesma base | Push no iPhone só com o app instalado na tela inicial |
| **B. App nativo (React Native/Expo ou Flutter)** | Notificações mais confiáveis; experiência de app | Exige conta e chaves de push (Firebase/Apple), que é justamente o tipo de configuração que queremos evitar; build e instalação na demo; o painel continua precisando de web |
| **C. Web simples, sem PWA** | O mais rápido de fazer | Sem push: o lembrete só aparece com a página aberta |

**Recomendação:** A. Na demo, o lembrete pode ser disparado na hora, então a limitação do iPhone não atrapalha.

**Resposta:**

---

## D17 — Como a cuidadora usa a plataforma

**Contexto:** o plano descreve uma **conversa** (o Orquestrador conduz; a história da Ana é um diálogo). Sem o WhatsApp, temos que desenhar essa interface.

| Opção | Comentário |
|---|---|
| **A. Conversa como tela principal + telas de apoio** | Chat com o agente (foto, PDF, áudio, botões de confirmar); telas para lista de remédios, cronograma, diário e resumos. Mantém a experiência do plano e deixa o agente no centro (teste de remoção) |
| **B. Telas guiadas, sem chat** | Fluxo em passos (enviar foto → confirmar → ver alertas). Mais simples, mas o agente "some", o que é ruim para o critério de IA da banca |
| **C. Só conversa** | Tudo no chat; consultar a lista ou o cronograma fica difícil |

**Perguntas:**
1. Qual opção?
2. **Contas:** como a cuidadora entra? Sugestões: e-mail + senha, link mágico por e-mail ou, na demo, contas pré-criadas. Uma cuidadora pode cuidar de mais de um idoso?

**Recomendação:** A; login por e-mail + senha; um idoso por conta no MVP.

**Resposta:**

---

## D15 — Decisões abertas do próprio plano (Parte 6)

1. **Nome:** Seriema, Cuidário ou outro? O nome do agente é "Seri", "Clara" ou outro? (Aparece na interface.)
2. **Até onde vai o alerta clínico?** O MVP mostra "possível interação, leve ao farmacêutico", ou **só organiza e escala**, sem mencionar interação? *Isso define se o Farmacovigilante fala com a cuidadora ou só alimenta o resumo.*
3. **Primeiro pagador:** operadora ou farmácia? (Afeta para quem o resumo é escrito.)
4. **Alguém de saúde** (Farmácia/Enfermagem) entrou no time ou como mentor? Quem confere os 30 pares de interação e os 20 relatos de sintoma?

**Resposta:**

---

## D16 — O que entra no caminho da demo

**Contexto *(leitura minha)*:** o escopo do regional tem a plataforma, 7 agentes, 4 bases e 6 conjuntos de avaliação. Não proponho cortar nada; proponho **ordenar**. A spec marcaria cada item como **P0 (a demo não acontece sem ele)** ou **P1 (se der tempo até a entrega)**.

Proposta, seguindo o roteiro da demo do plano (foto → lista → alerta → áudio → escalonamento):

| P0 | P1 |
|---|---|
| Plataforma: login, conversa, envio de foto/PDF, gravação de áudio, lista de remédios | Instalação como PWA; telas de cronograma e diário completas |
| Leitor (caixa + PDF) + confirmação | Manuscrita |
| Normalizador para os ~50 remédios | RAG em bulas |
| Farmacovigilante: interação + duplicidade + CBMPI | Conjuntos de avaliação completos (P0 = caixas, pares e guardrail) |
| Diário → regras de gravidade → 192 / resumo PDF | Lembrete agendado com push de verdade (P0 = disparado na hora, na tela) |
| Auditor (frases proibidas + remédio fora da lista) | |

Também há uma divergência interna no plano: o **aviso de estoque** aparece na arquitetura do regional (Rotina), mas a tabela MVP × final o coloca na final.

**Perguntas:**
1. Concorda com a ideia de P0/P1? Ajusta a tabela?
2. Aviso de estoque: regional ou final?

**Resposta:**

---

## D12 — Equipe

**Contexto:** o plano sugeria 4 papéis. Com a plataforma própria, eu os ajustaria para: (1) agentes e LLM, (2) dados e farmacovigilância, (3) **plataforma (frontend + API)**, voz e PDF, (4) entrevistas, BMC e pitch.

**Perguntas:**
1. Quem é quem, e com que experiência (Python, JS/TS, React, infra)?
2. Idioma do código e dos comentários: português ou inglês?

**Resposta:**

---

## D2 — Backend

| Opção | Comentário |
|---|---|
| **A. Python + FastAPI** | Melhor ecossistema para LLM, visão, PDF, ETL (Anvisa/CMED) e avaliação. Frontend separado |
| **B. TypeScript de ponta a ponta (ex.: Next.js)** | Uma linguagem só para frontend e backend; ETL e avaliação ficam menos cômodos |

**Recomendação:** A.

**Resposta:**

---

## D18 — Frontend

| Opção | Comentário |
|---|---|
| **A. React + Vite (+ plugin PWA), com Tailwind** | Leve, rápido de montar, PWA simples; consome a API FastAPI |
| **B. Next.js** | Mais recursos (SSR, rotas de API), que não precisamos com um backend separado |
| **C. HTML + HTMX servido pelo FastAPI** | Menos peças; mais limitado para gravação de áudio e chat em tempo real |

**Recomendação:** A, se o time conhecer React; senão, conversamos.

**Resposta:**

---

## D3 — Provedor do LLM (Leitor, Orquestrador, Diário, resumos)

**Contexto:** o LLM continua precisando de chave de API, a menos que usemos um modelo local. O plano cita **AWS Bedrock, "que casa com os créditos do prêmio"**.

| Opção | Comentário |
|---|---|
| **A. Claude via AWS Bedrock** | Alinha com o plano e com créditos AWS; exige conta AWS com acesso ao modelo liberado |
| **B. Claude via API Anthropic direta** | Setup mais rápido (só a chave); dá para migrar para o Bedrock depois |
| **C. Modelo aberto local** | Sem chave e sem dado saindo da máquina; pior em visão e mais infra |

Modelos sugeridos: `claude-sonnet-5-5` para visão e extração; `claude-haiku-5-5` para conversa e resumos leves.

**Perguntas:**
1. Já existem créditos AWS ou chave de API disponíveis **agora**?
2. Se não houver créditos AWS até a entrega, aceita começar pela opção B?

**Recomendação:** B para começar, com o cliente do LLM isolado para a troca ser trivial.

**Resposta:**

---

## D4 — Voz (STT do diário, TTS do lembrete)

**Contexto:** o áudio é gravado e tocado na própria plataforma.

| Opção | Comentário |
|---|---|
| **A. Nuvem** (ex.: OpenAI Whisper API, Amazon Transcribe/Polly, Google, ElevenLabs) | Rápido de integrar, bom pt-BR; mais uma chave de API |
| **B. Local** (faster-whisper + Piper) | Sem chave nem custo por uso; mais CPU e latência |
| **C. Voz do navegador** (Web Speech API) | Grátis e sem chave; qualidade e suporte em pt-BR variam por navegador; o STT do Chrome envia o áudio ao Google |

**Recomendação:** B para STT se a máquina da demo aguentar; senão A. TTS: A ou Piper.

**Resposta:**

---

## D5 — Orquestração dos agentes

| Opção | Comentário |
|---|---|
| **A. Pipeline em código** | Cada agente é um módulo com contrato de entrada e saída tipado; o LLM usa tool use onde precisa. Menos dependências, mais fácil de testar |
| **B. LangGraph (ou similar)** | Grafo explícito, bom para mostrar na banca; mais curva no prazo atual |

**Recomendação:** A.

**Resposta:**

---

## D6 — Banco de dados, arquivos e agendamento

**Contexto:** precisamos guardar contas, perfil do idoso, lista de remédios **versionada**, doses confirmadas, diário, fotos, PDFs e áudios. Com plataforma própria, a guarda dos dados sensíveis é nossa.

| Opção | Comentário |
|---|---|
| **A. SQLite + arquivos em disco + APScheduler** | Zero infra; suficiente para demo e piloto pequeno |
| **B. PostgreSQL + armazenamento de objetos (S3 ou similar) + fila** | Pronto para escala; mais infra |

**Recomendação:** A, com camada de acesso que permita migrar no piloto.

**Resposta:**

---

## D7 — Bases de farmacovigilância

**Contexto (plano):** interações via DDInter ou DrugBank acadêmico (openFDA como apoio); CBMPI e Beers; bulas da Anvisa (~50, sem API); sinais de alarme de protocolos do Ministério da Saúde.

**Perguntas:**
1. Qual base de interações usamos no hackathon: DDInter, DrugBank acadêmico ou as duas?
2. Quem define a lista dos **~50 remédios mais comuns em idosos**? O farmacêutico, se houver; senão, partimos do CBMPI e da literatura.
3. *(leitura minha)* Podemos montar a tabela de conversão dos nomes (português → internacional) **só para os ~50 remédios**, revisada à mão?

**Resposta:**

---

## D8 — Hospedagem

**Contexto:** sem o webhook do WhatsApp, não precisamos de URL pública para desenvolver. Para a demo, câmera, microfone e push só funcionam em **HTTPS** (ou localhost).

| Opção | Comentário |
|---|---|
| **A. Tudo local na máquina da demo** | Mais simples; o celular só acessa via túnel HTTPS (ngrok/Cloudflare Tunnel) |
| **B. PaaS (Render, Railway, Fly.io; Vercel/Netlify para o frontend)** | URL HTTPS estável; dá para abrir no celular de qualquer pessoa da banca |
| **C. AWS** (casa com o Bedrock) | Coerente com os créditos; mais configuração |

**Recomendação:** A para desenvolver; B para a entrega.

**Resposta:**

---

## D9 — Destino do resumo no MVP

**Contexto:** no MVP, o escalonamento é um "resumo em PDF para consulta / farmacêutico". O painel do profissional fica para a final.

**Pergunta:** no MVP, o PDF fica **só disponível para a cuidadora** (baixar ou compartilhar pelo celular), ou também gera um **link de acesso** para o profissional abrir sem conta?

**Resposta:**

---

## D10 — Frentes (uma pasta cada em `specs/`)

| Frente | Conteúdo | Quando |
|---|---|---|
| `backend` | API, contas, banco, arquivos, Rotina (agendador), voz, geração de PDF | Regional |
| `agentes` | Orquestrador, Leitor, Diário/Escalonador, Auditor; cliente do LLM | Regional |
| `dados` | Normalizador (Anvisa/CMED), Farmacovigilante (interações, duplicidade, CBMPI, bulas), sinais de alarme | Regional |
| `frontend` | Plataforma da cuidadora; na final, painel do profissional | Regional + final |
| `harness` | Os 6 conjuntos de avaliação e o relatório de métricas | Regional |
| `negocio` *(opcional)* | Entrevistas, BMC, pitch, relatórios quinzenais | Contínuo |

**Perguntas:**
1. Concorda com as frentes e os nomes? (`agentes` e `dados` poderiam ficar dentro de `backend`.)
2. Quer a frente `negocio` em `specs/`, ou só as técnicas?

**Resposta:**

---

## D13 — Pasta `docs/`

**Contexto:** você pediu que `specs/` concentre a documentação. Hoje `docs/` tem 3 arquivos. O plano aponta para `../avaliação_problemas/avaliacao_final.md`, que não existe (o arquivo está em `docs/avaliacao_final.md`).

**Perguntas:**
1. Movo `docs/` para `specs/referencia/` e ajusto os links, ou deixo onde está?
2. Corrijo o link quebrado no plano?
3. Os documentos de referência devem ganhar uma nota sobre a troca do WhatsApp, ou o registro na `visao.md` §5 basta?

**Resposta:**

---

## D14 — Dados de teste e LGPD

**Contexto:** o harness precisa de 50 fotos de caixas, 10 PDFs, 10 manuscritas, 30 pares, 20 relatos e 20 tentativas (plano).

**Perguntas:**
1. O que já existe desses conjuntos?
2. Fotos e receitas reais ficam **fora do Git** (pasta ignorada ou drive)? Recomendo que sim: são dados sensíveis.
3. Nos testes com cuidadoras, a tela de consentimento da plataforma já basta, ou usamos também um termo à parte?

**Resposta:**
