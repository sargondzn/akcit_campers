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
- [x] Documentar a plataforma mobile-first (visão §2.5, D20) (22/10)
- [ ] **Todos** — Responder a discussão (D0–D20) e definir quem é A, B e C (D12)
- [ ] **Todos** — Aprovar `spec.md` do 00-projeto, com os contratos C1–C7
- [ ] Criar as pastas das frentes (D10), cada uma com `discussao.md`, `spec.md` e `checklist.md`
- [ ] Resolver D13 (destino da pasta `docs/` e link quebrado no plano)

## Fase 1 — Regional: construção em paralelo (proposta)

> Este checklist cobre só o **regional**. O que fica para a final está em [`escopo-por-fase.md`](escopo-por-fase.md).

### Pessoa A — Plataforma

- [ ] **A · P0** — Esqueleto do repositório (pastas por dono, `contratos/`, instruções de setup)
- [ ] **A · P0** — Stub do agente seguindo o contrato C1
- [ ] **A · P0** — API: contas e login
- [ ] **A · P0** — Banco: perfil do idoso, lista de remédios versionada, doses, diário; funções de acesso (C6)
- [ ] **A · P0** — Upload e armazenamento de foto, PDF e áudio
- [ ] **A · P0** — Base mobile-first do frontend: layout de uma coluna em retrato, botões grandes, ações ao alcance do polegar, fonte ≥ 16 px, áreas seguras e teclado virtual (visão §2.5, D20)
- [ ] **A · P0** — Frontend: login e tela de consentimento (LGPD)
- [ ] **A · P0** — Frontend: tela de conversa (enviar foto/PDF, gravar áudio, tocar áudio, botões de confirmar)
- [ ] **A · P0** — Câmera direta (traseira, com galeria como alternativa) e redução da imagem antes do envio
- [ ] **A · P0** — Envio resiliente em rede móvel: indicador, reenvio, sem perder foto ou áudio
- [ ] **A · P0** — Testar o fluxo da demo em aparelho real (Android e iPhone)
- [ ] **A · P0** — Frontend: tela da lista de remédios
- [ ] **A · P0** — Lembrete disparado na hora, na tela (demo)
- [ ] **A · P0** — Geração do PDF a partir do `Resumo` (C5)
- [ ] **A · P0** — Deploy com HTTPS para a demo
- [ ] **A · P1** — PWA instalável + notificação push com agendamento
- [ ] **A · P1** — Telas completas de cronograma e diário

### Pessoa B — Agentes

- [ ] **B · P0** — Cliente do LLM isolado (troca de provedor trivial)
- [ ] **B · P0** — Stubs das funções de dados (C2–C4)
- [ ] **B · P0** — Leitor: foto de receita física (impressa e à mão) + foto de caixa + PDF → itens estruturados com confiança
- [ ] **B · P0** — Fluxo de confiança baixa (nova foto, foto da caixa, item "não confirmado") — conforme D19
- [ ] **B · P0** — Fluxo de confirmação (proposta de lista → confirmação da cuidadora)
- [ ] **B · P0** — Orquestrador: estado da conversa e roteamento para os agentes (C1)
- [ ] **B · P0** — Voz: STT do áudio da cuidadora (aceitando WebM/Opus e MP4/AAC) e TTS do lembrete
- [ ] **B · P0** — Diário: transcrição → sintoma estruturado (com perguntas de acompanhamento)
- [ ] **B · P0** — Escalonador: aplica `avaliar_gravidade` → 192 ou `Resumo` (C5)
- [ ] **B · P0** — Auditor: frases proibidas, remédio fora da lista, fonte citada

### Pessoa C — Dados e avaliação

- [ ] **C · P0** — Definir a lista dos ~50 remédios mais comuns em idosos
- [ ] **C · P0** — ETL Anvisa/CMED → `normalizar` (C2)
- [ ] **C · P0** — Checagem de mesmo princípio ativo em nomes diferentes (a partir do `normalizar`)
- [ ] **C · P0** — Tabela curada à mão para os ~15–20 remédios da demo: pares de interação, grupos de classe e itens do CBMPI, com fonte em cada linha → `checar_lista` (C3)
- [ ] **C · P0** — Sinais de alarme e regras de gravidade → `avaliar_gravidade` (C4)
- [ ] **C · P0** — Harness: executor + relatório de métricas
- [ ] **C · P0** — Conjuntos P0: 20 fotos de caixas (rótulos), 30 pares, 20 tentativas de guardrail
- [ ] **C · P0** — Conjuntos de receitas físicas: fotos impressas e manuscritas (quantidade e metas em D19)
- [ ] **C · P1** — Conjuntos restantes: 10 PDFs, 20 relatos

### Todos

- [ ] **Todos · P0** — Fotografar caixas de remédio (meta: 20)
- [ ] **Todos · P0** — Juntar receitas físicas reais, impressas e à mão, anonimizadas (D19)
- [ ] **Todos · P0** — Integração: dados → agentes → plataforma
- [ ] **Todos · P0** — Rodar o harness, congelar o código, gravar vídeo de backup da demo
- [ ] **Todos · P0** — Ensaiar o pitch
- [ ] **(dono em aberto)** — Entrevistas, BMC, pitch, relatórios quinzenais

## Pendências do regional que já constam nas referências

- [ ] Checar o campo de princípio ativo no dicionário de dados da Anvisa
- [ ] Entrevistas: 8–10 cuidadoras, 2 farmacêuticos, 1–2 enfermeiras de ESF; checar o critério de giro
- [ ] Checar disponibilidade do nome (INPI classes 9 e 44, registro.br, Instagram, lojas)

As pendências de licença, unit economics, regulatório e pagador foram para a final ([`escopo-por-fase.md`](escopo-por-fase.md) §3).
