# Checklist — harness

> **Dono:** Pessoa B (Caio). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md) · Tarefas fora do código: [`externo.md`](externo.md). Atualizado em 24/10/2026 (OpenAI; E1, E2, E4 e E8).
> **24/10 — implementação:** harness funcionando de ponta a ponta com a OpenAI pela demo no terminal (`python -m harness.demo --exemplo`) e 19 testes sem rede. Desvios e pendências no fim deste arquivo.

## Fora do código ([`externo.md`](externo.md))

- [x] **P0** — Chave da OpenAI criada e guardada no `.env` (§2) — conferir o limite de gasto na conta
- [x] **P0** — Programas instalados e `venv/` com `harness/requirements.txt` (§1, §3) — 24/10: Python 3.12.10, ffmpeg 9.0.2, Docker 29.8 (já havia), `AGNO_TELEMETRY=false` no usuário
- [x] **P0** — Teste mínimo do Agno com a OpenAI (§3)
- [ ] **P0** — Arquivos de bancada anonimizados, fora do Git, incluindo o par de receitas para a conciliação (§5)
- [ ] **P0** — Teste de bancada dos modelos da OpenAI; registrar na HA-D2 (§4)
- [ ] **P0** — Voz do Piper escolhida e baixada; modelo do Whisper baixado na máquina de produção (§6) — 24/10: `pt_BR-faber-medium` e Whisper `small` baixados na máquina de desenvolvimento; falta a de produção
- [ ] **P0** — Combinados com A e C (§7), incluindo BE-D3, HA-D7 e o C8
- [ ] **P0** — Máquina de produção preparada (§8)

## Base

- [x] **P0** — Agno e dependências fixados em `requirements.txt`, telemetria desligada (§3.1)
- [x] **P0** — `agentes/modelos.py`: modelos da OpenAI pelo Agno, saída tipada validada, tempo máximo e novas tentativas (§3.2)
- [x] **P0** — Stubs de `normalizar`, `checar_lista`, `detectar_alarme`, `avaliar_gravidade` e `info_remedio` (C2–C4, C8)
- [x] **P0** — `RepositorioEmMemoria` (C6, com os métodos de 24/10) e modelo falso compatível com o Agno para testes
- [x] **P0** — `processar_mensagem` com a ordem fixa do §5
- [x] **P0** — `processar_evento` para os 3 eventos agendados (§5.1)

## Percepção

- [x] **P0** — Subagente Leitor: foto → `LeituraBruta` (§6.2)
- [x] **P0** — Subagente Intérprete: transcrição ou texto do PDF → `ItensInterpretados`, com médico, data, quantidade por dose e embalagem (§6.3)
- [x] **P0** — Workflow de leitura com pós-processamento e "para que serve" (§2.4, §6.1, §6.4)
- [x] **P0** — Fluxo de confiança baixa (§6.5)
- [x] **P0** — Caixa de remédio que já está na lista (§6.6)
- [x] **P0** — Escuta local: WebM/Opus e MP4/AAC → texto (§8)
- [x] **P0** — Contexto a cada mensagem (§3.3, §5 passo 3)

## Conciliação (E1)

- [x] **P0** — Pergunta de escopo da receita e ação `definir_escopo` (§7.2)
- [x] **P0** — `conciliar`: novo, mantido, alterado, ausente (§7.3)
- [x] **P0** — Proposta com mudanças, ação `decidir_item` e frases fixas (§7.4)

## Decisão e ações

- [x] **P0** — Registro de ferramentas, com a lista de ferramentas de cada agente (§17.1)
- [x] **P0** — Subagentes Rotina e Explicador, com "para que serve" (§2.2, §10)
- [x] **P0** — Subagente Agenda: registrar consulta com confirmação (§11.1)
- [x] **P0** — Subagente Farmácia: estoque e Farmácia Popular (§12)
- [x] **P0** — Equipe da Seri: coordenadora em modo `route` com os 5 membros (§2.3, HA-D8)
- [x] **P0** — Limite de 5 chamadas de ferramenta somando todos os agentes (§17)
- [x] **P0** — Subagente Diário + Workflow do diário (§9)
- [x] **P0** — Escalonador: conduta → 192, resumo + link, ou observar (§9)
- [x] **P0** — `gerar_resumo` → `Resumo` (C5), nos dois tipos

## Preparo da consulta (E2)

- [x] **P0** — Dossiê e perguntas candidatas (§11.2)
- [x] **P0** — Subagente Preparador + validação das perguntas (§11.2)
- [x] **P0** — Workflow do preparo e mensagem `consulta_preparada` (§11.2)
- [x] **P0** — Pós-consulta: pergunta, relato pela Agenda e aviso de receita nova (§11.3)

## Remédio nunca falta (E4)

- [x] **P0** — `estoque.calcular` e `registrar_estoque` (§12.1)
- [x] **P0** — Avisos de 7 e 2 dias na verificação diária (§12.1, HA-D11)
- [x] **P0** — Frases do Farmácia Popular (§12.3)
- [x] **P1** — Validade da receita e aviso (§12.2)

## Guardrails

- [x] **P0** — Regras fixas antes de qualquer agente, inclusive no relato da consulta (§13.1)
- [x] **P0** — Confirmação humana por pendência e as ações de 24/10, sem agente (§13.2)
- [x] **P0** — Auditor com as 4 verificações, incluindo indicação sem fonte (§13.3)
- [x] **P0** — Textos fixos de alerta, conduta, conciliação, para que serve, estoque e bloqueio (`frases.py`)
- [x] **P0** — Instruções de cada subagente com a persona da Seri (§16, §17)
- [x] **P0** — Fala: `falar(texto)` em MP3 (§14)

## Integração e prova

- [ ] **P0** — Trocar os stubs pelas funções reais de C (inclusive C8)
- [ ] **P0** — Plugar na API de A (sem stub), com `processar_evento`
- [x] **P0** — Expor o C7 para a avaliação (com `conciliacao`)
- [x] **P0** — Testes do §18
- [x] **P1** — Registro de passos por agente, com tokens (§15)

## Desvios e pendências da implementação (24/10)

- **Contratos:** os tipos estão em `harness/contratos.py` até A criar `contratos/`. Acrescentei `pontos_para_conferir` em `ListaVersao` e em `salvar_lista_confirmada` (C6), para o "não sei" da conciliação (E1) chegar ao preparo (E2). Atualizado na 00-projeto/spec §5.
- **Testes:** o falso fica na camada `Agentes` (`testes/agentes_falsos.py`), não na classe de modelo do Agno. O efeito é o mesmo (nenhuma chamada à OpenAI nos testes) e é mais simples de manter.
- **HA-D10:** quando nenhum remédio da lista tem médico, a opção "Só os remédios desse médico" não marca nenhum ausente (lado seguro), mas a pergunta extra da recomendação ainda não foi feita.
- **E4:** a pendência `quantidade_por_dose` não foi implementada: a quantidade por dose vem da leitura da receita ("1 cp"). Sem ela, o remédio não gera aviso de estoque.
- **Faster-whisper 1.2.1 × av 19:** a Escuta passa as amostras do WAV direto ao Whisper, sem o decodificador `av` (incompatível).
- **Pendente de fora:** plugar na API de A (HA-D7), trocar os stubs pelos dados de C, teste de bancada com receitas reais (HA-D2).
