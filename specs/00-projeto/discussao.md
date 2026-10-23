# Discussão — 00-projeto (escopo, stack, frentes e prazos)

> **Revisada em 22/10/2026:** o WhatsApp saiu e entrou a plataforma própria (ver [`visao.md`](visao.md) §5).
> **Respondida em 23/10/2026.** As respostas viraram a [`spec.md`](spec.md) do projeto e as specs das frentes. A D22 foi aberta e respondida em 23/10, ao escrever as specs.
> Novas perguntas que surgirem ficam na `discussao.md` da frente correspondente.
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
1. A inscrição já foi feita e estamos na trilha de Goiânia (24/10). 
2. Não sei se muda na trilha online, mas a entrega é de acordo com o plano.
3. Nada foi feito ainda fora do repositório além de uma entrevista.
4. As entrevistas mostraram que a nossa solução é viável e resolve uma dor cotidiana de cuidadores de idosos.

---

## D0 — Fonte do escopo e divergências

**Contexto:** as duas referências em `docs/` divergem em alguns pontos. O canal já está resolvido pela mudança de 22/10 (plataforma própria).

| Tema | `f3_cuidador_medicacao.md` (avaliação) | `f3_plano_startup_v1.md` (plano) |
|---|---|---|
| ~~Entrada principal~~ | ~~Foto da receita~~ | ~~Fotos de caixas + PDF; manuscrita como bônus~~ — **resolvido** pela mudança de 22/10 (visão §5): foto da receita física + caixas + PDF |
| Componentes | Leitor, Normalizador, Checador, Diário, Escalonador | + Orquestrador, Farmacovigilante (duplicidade, CBMPI, bulas), Rotina, **Auditor** |
| Destino do escalonamento | Enfermeira da ESF | Farmacêutico / ESF / consulta, via **resumo em PDF** |
| Sinal de alarme | Não mencionado | Regra fixa → "ligue 192" |
| Evolução (28/11) | Painel da ESF + piloto | Painel do farmacêutico **ou** enfermeira + piloto + manuscrita, código de barras, estoque, tendências |
| Avaliação | Acurácia da leitura + recall de interações | 6 conjuntos com metas (visão §2.4) |

**Pergunta:** o **plano prevalece** sobre o escopo original nessas divergências, respeitadas as mudanças de escopo da visão §5? (Recomendação: sim.)

**Resposta:** Sim.

---

## D1 — Formato da plataforma

**Contexto:** a plataforma precisa de câmera ou upload (foto e PDF), gravação de áudio, reprodução de áudio, notificações de lembrete e, na final, um painel do profissional.

| Opção | Prós | Contras |
|---|---|---|
| **A. Web app responsivo instalável (PWA)** | Um código só para celular e computador; sem loja de apps; câmera, áudio e push pelo navegador; o painel da final sai da mesma base | Push no iPhone só com o app instalado na tela inicial |
| **B. App nativo (React Native/Expo ou Flutter)** | Notificações mais confiáveis; experiência de app | Exige conta e chaves de push (Firebase/Apple), que é justamente o tipo de configuração que queremos evitar; build e instalação na demo; o painel continua precisando de web |
| **C. Web simples, sem PWA** | O mais rápido de fazer | Sem push: o lembrete só aparece com a página aberta |

**Recomendação:** A. Na demo, o lembrete pode ser disparado na hora, então a limitação do iPhone não atrapalha.

**Resposta:** Faremos de acordo com a sugestão A.

---

## D20 — Experiência mobile

**Contexto:** o uso será majoritariamente no celular (visão §2.5). A área da cuidadora é desenhada primeiro para o celular; o painel do profissional (final), primeiro para o computador.

**Perguntas:**
1. **Aparelhos-alvo:** testamos em quais celulares reais? Há pelo menos um Android e um iPhone no time?
2. **Gravação de áudio:** "segurar para falar" (estilo WhatsApp) ou "tocar para gravar, tocar para parar"? O segundo é mais fácil para quem tem pouca firmeza na mão.
3. **Celular de entrada:** consideramos aparelhos Android mais simples (pouca memória, tela pequena, rede 4G fraca) como referência de desempenho?
4. **Computador na área da cuidadora:** basta "funcionar" (coluna central), ou ela precisa de um layout próprio no computador já no regional?
5. **Biblioteca de componentes:** algo pronto e pensado para toque (ex.: shadcn/ui ou Radix + Tailwind), ou componentes próprios?

**Recomendação:** 1 — um Android e um iPhone. 2 — tocar para gravar e tocar para parar. 3 — sim. 4 — basta funcionar. 5 — shadcn/ui com Tailwind, se a D18 for React.

**Resposta:**
1. Sim, temos iphone e android no time, podemos preparar para os dois os.
2. Tocar para gravar e tocar para parar.
3. Sim.
4. Basta funcionar.
5. Shadcn/ui com Tailwind, se a D18 for React.

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

**Resposta:** A; login por e-mail + senha; um idoso por conta no MVP.

---

## D15 — Decisões abertas do próprio plano (Parte 6)

1. **Nome:** Seriema, Cuidário ou outro? O nome do agente é "Seri", "Clara" ou outro? (Aparece na interface.)
2. **Até onde vai o alerta clínico?** O MVP mostra "possível interação, leve ao farmacêutico", ou **só organiza e escala**, sem mencionar interação? *Isso define se o Farmacovigilante fala com a cuidadora ou só alimenta o resumo.*
3. **Primeiro pagador:** operadora ou farmácia? (Afeta para quem o resumo é escrito.)
4. **Alguém de saúde** (Farmácia/Enfermagem) entrou no time ou como mentor? Quem confere os 30 pares de interação e os 20 relatos de sintoma?

**Resposta:**
1. Nome será Seriema. O agente pode ser chamar Seri.
2. Queremos que haja essa menção a interação.
3. Operadora.
4. Não temos ninguém da saúde no time. Iremos usar llms para fazer a conferência na etapa regional. Na etapa final, se necessário, iremos passar esses dados para análise por parte de um profissional.

---

## D16 — O que entra no caminho da demo

**Contexto *(leitura minha)*:** o escopo do regional tem a plataforma, o harness agêntico com vários componentes, 4 bases e 6 conjuntos de avaliação. Não proponho cortar nada; proponho **ordenar**. A spec marcaria cada item como **P0 (a demo não acontece sem ele)** ou **P1 (se der tempo até a entrega)**.

Proposta, seguindo o roteiro da demo do plano (foto → lista → alerta → áudio → escalonamento):

| P0 | P1 |
|---|---|
| Plataforma: login, conversa, envio de foto/PDF, gravação de áudio, lista de remédios | Instalação como PWA; telas de cronograma e diário completas |
| Leitor (foto de receita impressa e à mão + caixa + PDF) + confirmação | |
| Normalizador para os ~50 remédios | |
| Farmacovigilante mínimo: mesmo princípio ativo + tabela curada | Conjuntos de avaliação completos (P0 = caixas, pares e guardrail) |
| Diário → regras de gravidade → 192 / resumo PDF | Lembrete agendado com push de verdade (P0 = disparado na hora, na tela) |
| Auditor (frases proibidas + remédio fora da lista) | |

Também há uma divergência interna no plano: o **aviso de estoque** aparece na arquitetura do regional (Rotina), mas a tabela MVP × final o coloca na final.

**Perguntas:**
1. Concorda com a ideia de P0/P1? Ajusta a tabela?
2. Aviso de estoque: regional ou final?

**Resposta:**
1. Quero que o PWA seja intalável já na etapa regional. No normalizador, iremos usar cerca de 20 remédios. De resto, concordo com a ideia de separação entre p0 e p1.
2. O registro de estoque fica apenas para a final.


---

## D19 — Foto da receita física como entrada principal

**Contexto:** a foto da receita física, impressa ou à mão, passou a ser a entrada principal (visão §5). Com isso, a receita à mão sai do papel de bônus e entra no caminho principal. É a entrada que os modelos leem pior.

**Perguntas:**
1. **Avaliação:** adicionamos um conjunto de **fotos de receitas impressas** (sugestão: 10, meta ≥ 95%, igual ao PDF)? E as **manuscritas** sobem para P0, com mais exemplos (sugestão: 20) e meta "medir e mostrar"?
2. **Quando a confiança da leitura for baixa**, o que o agente faz? Sugestões, combináveis: (a) pede outra foto; (b) pede a foto da caixa daquele remédio para confirmar; (c) pede que a cuidadora digite ou fale o nome; (d) marca o item como "não confirmado", e ele não entra no cronograma.
3. **Itens ilegíveis:** se nada resolver, o item fica fora da lista com o aviso "confirme com o farmacêutico"?
4. **Fonte das receitas:** dá para conseguir receitas reais (anonimizadas) das famílias da equipe e dos entrevistados até a entrega?

**Recomendação:** 1 — sim, para as duas. 2 — (a), depois (b) ou (c), e (d) até que a cuidadora confirme. 3 — sim.

**Resposta:**
1. Sim para as duas.
2. (a), depois (b) ou (c), e (d) até que a cuidadora confirme.
3. Sim.
4. Provavelmente não uma quantidade satisfatória até a entrega local, mas podemos providenciar uma quantidade satisfatória caso cheguemos até a final.


---

## D12 — Equipe (3 pessoas)

**Contexto:** proposta de divisão em [`divisao.md`](divisao.md): **A — Plataforma** (frontend + API), **B — Harness agêntico** (modelo, percepção, loop, ferramentas, guardrails, voz), **C — Dados e avaliação** (ferramentas de dados + avaliação). O plano sugeria 4 papéis; o quarto (entrevistas, BMC, pitch) ficou sem dono.

**Perguntas:**
1. Quem é A, B e C? Qual a experiência de cada um (Python, JS/TS, React, infra)?
2. Concorda com a divisão e com os contratos C1–C7?
3. Quem cuida do negócio (entrevistas, BMC, pitch, relatórios)? Opções: (a) uma pessoa como dona, provavelmente C, cuja frente fica mais leve depois que os dados estão prontos; (b) dividido por tema (entrevistas: C; BMC: B; pitch: A).
4. Idioma do código e dos comentários: português ou inglês?

**Resposta:**
1. A é a Beatriz, B é o Caio e C é o Roberto. A experiência aqui é irrelevante, cada um irá dar o seu próprio jeito de resolver os problemas.
2. Sim, concordo.
3. Podemos deixar a pessoa C com isso, mas essa parte de negócio deve passar por uma revisão por parte de todos os outros membros do grupo.
4. Iremos deixar em português.

---

## D2 — Backend

| Opção | Comentário |
|---|---|
| **A. Python + FastAPI** | Melhor ecossistema para LLM, visão, PDF, ETL (Anvisa/CMED) e avaliação. Frontend separado |
| **B. TypeScript de ponta a ponta (ex.: Next.js)** | Uma linguagem só para frontend e backend; ETL e avaliação ficam menos cômodos |

**Recomendação:** A.

**Resposta:** Faremos de acordo com a opção A.

---

## D18 — Frontend

| Opção | Comentário |
|---|---|
| **A. React + Vite (+ plugin PWA), com Tailwind** | Leve, rápido de montar, PWA simples; consome a API FastAPI |
| **B. Next.js** | Mais recursos (SSR, rotas de API), que não precisamos com um backend separado |
| **C. HTML + HTMX servido pelo FastAPI** | Menos peças; mais limitado para gravação de áudio e chat em tempo real |

**Recomendação:** A, se o time conhecer React; senão, conversamos.

**Resposta:** Seguiremos a opção A.

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

**Resposta:** Seguiremos a recomendação C.

Observação para o grupo: se algum de vocês conseguir ter acesso à API da OpenAI ou da Anthropic, podemos usar caso cheguemos na final, mas para a etapa regional, acho que faz mais sentido usarmos um modelo open-source.

---

## D4 — Voz (STT do diário, TTS do lembrete)

**Contexto:** o áudio é gravado e tocado na própria plataforma.

| Opção | Comentário |
|---|---|
| **A. Nuvem** (ex.: OpenAI Whisper API, Amazon Transcribe/Polly, Google, ElevenLabs) | Rápido de integrar, bom pt-BR; mais uma chave de API |
| **B. Local** (faster-whisper + Piper) | Sem chave nem custo por uso; mais CPU e latência |
| **C. Voz do navegador** (Web Speech API) | Grátis e sem chave; qualidade e suporte em pt-BR variam por navegador; o STT do Chrome envia o áudio ao Google |

**Recomendação:** B para STT se a máquina da demo aguentar; senão A. TTS: A ou Piper.

**Resposta:** Faremos conforme a recomendação B.

---

## D5 — Como construir o loop do harness

**Contexto:** o Orquestrador é o loop de decisão do harness (visão §2.1): recebe as observações, escolhe a ferramenta, observa o resultado e responde.

| Opção | Comentário |
|---|---|
| **A. Loop próprio em Python com tool use do LLM** | O modelo recebe o contexto e a lista de ferramentas e decide qual chamar. Fluxos críticos (confirmação, 192, Auditor) ficam fixos em código, fora da escolha do modelo. Poucas dependências, fácil de entender e testar |
| **B. LangGraph (ou similar)** | Grafo explícito, bom para mostrar na banca; mais curva de aprendizado no prazo atual |
| **C. SDK de agentes do provedor** (ex.: Claude Agent SDK) | Loop e ferramentas prontos; menos controle sobre os guardrails fixos e mais acoplamento ao provedor |

**Recomendação:** A. Cada componente do harness vira um módulo com contrato tipado, e o diagrama da visão §2.1 cumpre o papel visual na banca.

**Resposta:** Usaremos para a etapa regional a opção A. Mas iremos desenvolver para a opção B, caso a gente chegue na final.

---

## D21 — Regras do harness agêntico

**Contexto:** o harness define o que o modelo pode perceber, decidir e fazer (visão §2.1). Estas regras entram na spec da frente `harness`.

**Perguntas:**
1. **Limite de passos:** quantas ferramentas o modelo pode chamar por mensagem antes de parar e responder? (Evita loop infinito e custo alto.)
2. **Ações que exigem confirmação da cuidadora:** sugestão — `salvar_lista_confirmada` e qualquer mudança no cronograma. `registrar_dose` e `registrar_sintoma` podem ser diretas.
3. **O que o modelo nunca decide sozinho:** sugestão — sinal de alarme (regra fixa → 192), fatos clínicos (só vêm das ferramentas de C) e a liberação da saída (passa sempre pelo Auditor).
4. **Registro de passos:** guardamos cada observação, ferramenta chamada, resultado e bloqueio do Auditor? Ajuda a depurar, alimenta a avaliação e mostra o harness funcionando na banca. Contém dado sensível, então fica só no servidor.

**Recomendação:** 1 — até 5 chamadas por mensagem. 2 e 3 — como sugerido. 4 — sim, como P1.

**Resposta:**
1. Até 5 chamadas por mensagem.
2. Faça como sugerido.
3. Faça conforme o sugerido.
4. Sim, faremos conforme o sugerido.

---

## D6 — Banco de dados, arquivos e agendamento

**Contexto:** precisamos guardar contas, perfil do idoso, lista de remédios **versionada**, doses confirmadas, diário, fotos, PDFs e áudios. Com plataforma própria, a guarda dos dados sensíveis é nossa.

| Opção | Comentário |
|---|---|
| **A. SQLite + arquivos em disco + APScheduler** | Zero infra; suficiente para demo e piloto pequeno |
| **B. PostgreSQL + armazenamento de objetos (S3 ou similar) + fila** | Pronto para escala; mais infra |

**Recomendação:** A, com camada de acesso que permita migrar no piloto.

**Resposta:** Vamos usar a A para a demo. Talvez migremos para a B, caso passemos para a final.

---

## D7 — Tabela curada de farmacovigilância (regional)

**Contexto:** no regional, a farmacovigilância é a checagem de mesmo princípio ativo mais uma **tabela curada à mão** para os remédios da demo (visão §5). Base licenciada, conversão de nomes em escala, CBMPI completo, Beers e bulas ficam para a final ([`escopo-por-fase.md`](escopo-por-fase.md)).

**Perguntas:**
1. Quem define a lista dos **~50 remédios** do Normalizador e os **~15–20 da demo**? O farmacêutico, se houver; senão, partimos do CBMPI e da literatura.
2. De onde vem cada linha da tabela curada? Sugestão: consulta manual a DDInter/DrugBank, bula e CBMPI, registrando a fonte em cada linha.
3. *(leitura minha)* **Evitar a avaliação circular:** se os 30 pares da avaliação vierem da mesma fonte que a tabela, o recall dá 100% sem provar nada. Sugestão: quem monta os pares de teste (o farmacêutico ou outra pessoa) não é quem montou a tabela, e os pares incluem casos negativos e casos fora da tabela.

**Resposta:**
1. Acho que essa parte de fotos para o normalizador pode ser apenas para termos uma noção de como o sistema está respondendo, identificando acurácia e outros fatores para melhora do sistema. Podemos deixar o próprio responsável pela frente para selecionar as fotos dentro desse contexto.
2. Não temos uma referência fixa, podemos usar uma llm para gerar essa tabela para a gente, é algo que não queremos detalhar muito antes da final. Podemos pensar em aumentar a complexidade depois da etapa regional. Por enquanto, queremos apenas que o sistema funcione corretamente durante a demo.
3. Não acho que precisamos ter muito trabalho nessa parte, além de que já temos uma equipe reduzida, então não pretendo seguir essa sugestão.

---

## D8 — Hospedagem

**Contexto:** sem o webhook do WhatsApp, não precisamos de URL pública para desenvolver. Para a demo, câmera, microfone e push só funcionam em **HTTPS** (ou localhost).

| Opção | Comentário |
|---|---|
| **A. Tudo local na máquina da demo** | Mais simples; o celular só acessa via túnel HTTPS (ngrok/Cloudflare Tunnel) |
| **B. PaaS (Render, Railway, Fly.io; Vercel/Netlify para o frontend)** | URL HTTPS estável; dá para abrir no celular de qualquer pessoa da banca |
| **C. AWS** (casa com o Bedrock) | Coerente com os créditos; mais configuração |

**Recomendação:** A para desenvolver; B para a entrega.

**Resposta:** Quero que seja possível testar localmente usando o Docker de suporte e vamos usar a Netlify para a hospedagem, deixando o sistema em produção e disponível para o acesso por parte da banca.

---

## D9 — Destino do resumo no MVP

**Contexto:** no MVP, o escalonamento é um "resumo em PDF para consulta / farmacêutico". O painel do profissional fica para a final.

**Pergunta:** no MVP, o PDF fica **só disponível para a cuidadora** (baixar ou compartilhar pelo celular), ou também gera um **link de acesso** para o profissional abrir sem conta?

**Resposta:** Acho interessante abrir um link de acesso sme necessidade de criação de conta.

---

## D10 — Frentes (uma pasta cada em `specs/`)

| Frente | Conteúdo | Dono | Quando |
|---|---|---|---|
| `frontend` | Plataforma da cuidadora; na final, painel do profissional | A | Regional + final |
| `backend` | API, contas, banco, arquivos, agendador de lembretes, geração de PDF | A | Regional |
| `harness` | Harness agêntico: percepção (Leitor, STT), memória em uso, loop do Orquestrador, registro de ferramentas, Diário/Escalonador, guardrails (regras fixas, confirmação, Auditor), cliente do LLM, TTS | B | Regional |
| `dados` | Ferramentas de dados: Normalizador (Anvisa/CMED), Farmacovigilante (no regional: mesmo princípio ativo + tabela curada), regras de gravidade e sinais de alarme | C | Regional |
| `avaliacao` | Os conjuntos de avaliação e o relatório de métricas | C | Regional |
| `negocio` *(opcional)* | Entrevistas, BMC, pitch, relatórios quinzenais | em aberto (D12) | Contínuo |

**Perguntas:**
1. Concorda com as frentes e os nomes? (`harness` e `dados` poderiam ficar dentro de `backend`.)
2. Quer a frente `negocio` em `specs/`, ou só as técnicas?

**Resposta:**
1. Vamos deixar as frentes conforme o que você sugeriu (frontend, backend, harness, dados, avaliacao e negocio). A parte de negócio não é obrigatória para o desenvolvimento do sistema, mas deve estar ali, pois ela é fundamental para o dia do akcit camp.
2. Quero ela em specs, sim.

---

## D13 — Pasta `docs/`

**Contexto:** você pediu que `specs/` concentre a documentação. Hoje `docs/` tem 3 arquivos. O plano aponta para `../avaliação_problemas/avaliacao_final.md`, que não existe (o arquivo está em `docs/avaliacao_final.md`).

**Perguntas:**
1. Movo `docs/` para `specs/referencia/` e ajusto os links, ou deixo onde está?
2. Corrijo o link quebrado no plano?
3. Os documentos de referência devem ganhar uma nota sobre a troca do WhatsApp, ou o registro na `visao.md` §5 basta?

**Resposta:**
1. Não, você deve deixar o que já temos.
2. Não precisa corrigir o link quebrado. Só adicionar uma observação de que essa documentação auxiliar está de fora do repositório, mas pode ser requisitada para o admin.
3. Não precisa, só a pasta de `specs/` que precisa ter em algum lugar sobre a mudança do whatsapp.

---

## D14 — Dados de teste e LGPD

**Contexto:** no regional, a avaliação precisa de 20 fotos de caixas (50 na final), fotos de receitas físicas (D19), 10 PDFs, 30 pares, 20 relatos e 20 tentativas.

**Perguntas:**
1. O que já existe desses conjuntos?
2. Fotos e receitas reais ficam **fora do Git** (pasta ignorada ou drive)? Recomendo que sim: são dados sensíveis.
3. Nos testes com cuidadoras, a tela de consentimento da plataforma já basta, ou usamos também um termo à parte?

**Resposta:**
1. Não existe nada desse conjunto ainda.
2. Sim, ficam de fora do Git.
3. Podemos fazer só a tela de consentimento para a etapa regional.
Acho importante dizer aqui que talvez não consigamos trazer tudo que a etapa de harness pede, já que estamos muito próximos da data do evento.

> *Nota (23/10):* nesta resposta, "harness" está no sentido antigo, de **avaliação**. Pela nova nomenclatura (visão §5), a frase se refere aos conjuntos de avaliação. Isso conversa com a D16, que define o que é P0 e o que é P1 na avaliação.

---

## D22 — Onde rodam a API e o modelo em produção

**Contexto:** a Netlify (D8) hospeda só o frontend (páginas estáticas e funções curtas). A API em FastAPI, o SQLite, o agendador, o faster-whisper e o modelo open-source local (D3) precisam de outro lugar. O modelo de visão precisa de GPU para responder em segundos; só com CPU, cada foto leva bem mais tempo.

**Perguntas (feitas em 23/10, ao escrever as specs):**
1. Onde rodam a API e o modelo na versão de produção que a banca vai acessar?
2. Alguém do time tem máquina com GPU NVIDIA de 8 GB ou mais?

**Resposta:**
1. Máquina do time + túnel: frontend na Netlify; API, harness, modelos e banco num computador do time, em Docker, exposto por Cloudflare Tunnel (HTTPS).
2. Não / não sei. Os modelos rodam em CPU (modelos pequenos), salvo se aparecer uma GPU.
