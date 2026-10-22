# Checklist — 00-projeto

> Dono de cada tarefa: **A** (Plataforma), **B** (Agentes), **C** (Dados e avaliação), **Todos**. Ver [`divisao.md`](divisao.md).
> Prioridade: **P0** = a demo não acontece sem ela; **P1** = se der tempo até a entrega. A proposta P0/P1 depende da D16.
> Quando as frentes forem criadas (D10), as tarefas de construção migram para o `checklist.md` de cada frente.

## Fase 0 — Organização e decisões (Todos)

- [x] Criar `specs/` com regras e índice (`README.md`)
- [x] Escrever a visão do projeto (`visao.md`)
- [x] Levantar estudo de stack e perguntas (`discussao.md`)
- [x] Revisar visão e discussão com `docs/f3_plano_startup_v1.md` (22/10)
- [x] Trocar WhatsApp por plataforma própria na visão e na discussão (22/10)
- [x] Propor divisão do time em 3 pessoas (`divisao.md`)
- [x] Incluir foto da receita física como entrada principal (22/10)
- [ ] **Todos** — Responder a discussão (D0–D19) e definir quem é A, B e C (D12)
- [ ] **Todos** — Aprovar `spec.md` do 00-projeto, com os contratos C1–C7
- [ ] Criar as pastas das frentes (D10), cada uma com `discussao.md`, `spec.md` e `checklist.md`
- [ ] Resolver D13 (destino da pasta `docs/` e link quebrado no plano)

## Fase 1 — Construção em paralelo (proposta)

### Pessoa A — Plataforma

- [ ] **A · P0** — Esqueleto do repositório (pastas por dono, `contratos/`, instruções de setup)
- [ ] **A · P0** — Stub do agente seguindo o contrato C1
- [ ] **A · P0** — API: contas e login
- [ ] **A · P0** — Banco: perfil do idoso, lista de remédios versionada, doses, diário; funções de acesso (C6)
- [ ] **A · P0** — Upload e armazenamento de foto, PDF e áudio
- [ ] **A · P0** — Frontend: login e tela de consentimento (LGPD)
- [ ] **A · P0** — Frontend: tela de conversa (enviar foto/PDF, gravar áudio, tocar áudio, botões de confirmar)
- [ ] **A · P0** — Frontend: tela da lista de remédios
- [ ] **A · P0** — Lembrete disparado na hora, na tela (demo)
- [ ] **A · P0** — Geração do PDF a partir do `Resumo` (C5)
- [ ] **A · P0** — Deploy com HTTPS para a demo
- [ ] **A · P1** — PWA instalável + notificação push com agendamento
- [ ] **A · P1** — Telas completas de cronograma e diário
- [ ] **A · Final** — Painel do profissional

### Pessoa B — Agentes

- [ ] **B · P0** — Cliente do LLM isolado (troca de provedor trivial)
- [ ] **B · P0** — Stubs das funções de dados (C2–C4)
- [ ] **B · P0** — Leitor: foto de receita física (impressa e à mão) + foto de caixa + PDF → itens estruturados com confiança
- [ ] **B · P0** — Fluxo de confiança baixa (nova foto, foto da caixa, item "não confirmado") — conforme D19
- [ ] **B · P0** — Fluxo de confirmação (proposta de lista → confirmação da cuidadora)
- [ ] **B · P0** — Orquestrador: estado da conversa e roteamento para os agentes (C1)
- [ ] **B · P0** — Voz: STT do áudio da cuidadora e TTS do lembrete
- [ ] **B · P0** — Diário: transcrição → sintoma estruturado (com perguntas de acompanhamento)
- [ ] **B · P0** — Escalonador: aplica `avaliar_gravidade` → 192 ou `Resumo` (C5)
- [ ] **B · P0** — Auditor: frases proibidas, remédio fora da lista, fonte citada
- [ ] **B · Final** — Tendências no diário ("3 dias de tontura")

### Pessoa C — Dados e avaliação

- [ ] **C · P0** — Definir a lista dos ~50 remédios mais comuns em idosos
- [ ] **C · P0** — ETL Anvisa/CMED → `normalizar` (C2)
- [ ] **C · P0** — Tabela de conversão de nomes PT → internacional para os ~50
- [ ] **C · P0** — Base de interações filtrada para os ~50 (DDInter/DrugBank)
- [ ] **C · P0** — Duplicidade de classe e CBMPI transcrito → `checar_lista` (C3)
- [ ] **C · P0** — Sinais de alarme e regras de gravidade → `avaliar_gravidade` (C4)
- [ ] **C · P0** — Harness: executor + relatório de métricas
- [ ] **C · P0** — Conjuntos P0: 50 fotos de caixas (rótulos), 30 pares, 20 tentativas de guardrail
- [ ] **C · P0** — Conjuntos de receitas físicas: fotos impressas e manuscritas (quantidade e metas em D19)
- [ ] **C · P1** — RAG em bulas (~50)
- [ ] **C · P1** — Conjuntos restantes: 10 PDFs, 20 relatos

### Todos

- [ ] **Todos · P0** — Fotografar caixas de remédio (meta: 50)
- [ ] **Todos · P0** — Juntar receitas físicas reais, impressas e à mão, anonimizadas (D19)
- [ ] **Todos · P0** — Integração: dados → agentes → plataforma
- [ ] **Todos · P0** — Rodar o harness, congelar o código, gravar vídeo de backup da demo
- [ ] **Todos · P0** — Ensaiar o pitch
- [ ] **(dono em aberto)** — Entrevistas, BMC, pitch, relatórios quinzenais

## Pendências que já constam nas referências

- [ ] Checar a licença comercial do DDInter (e o uso acadêmico do DrugBank)
- [ ] Checar o campo de princípio ativo no dicionário de dados da Anvisa
- [ ] Entrevistas: 8–10 cuidadoras, 2 farmacêuticos, 1–2 enfermeiras de ESF; checar o critério de giro
- [ ] Checar disponibilidade do nome (INPI classes 9 e 44, registro.br, Instagram, lojas)
- [ ] Levantar o custo médio de internação de idoso na saúde suplementar (unit economics)
- [ ] Levantar quanto das internações de idosos vem de erro de medicação em casa
- [ ] Parecer sobre o enquadramento na RDC 657/2022 e 751/2022
- [ ] Preparar a resposta para a banca sobre o pagador (operadora/farmácia)
