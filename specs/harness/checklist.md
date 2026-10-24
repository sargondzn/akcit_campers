# Checklist — harness

> **Dono:** Pessoa B (Caio). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md) · Tarefas fora do código: [`externo.md`](externo.md). Atualizado em 24/10/2026 (OpenAI; E1, E2, E4 e E8).

## Fora do código ([`externo.md`](externo.md))

- [ ] **P0** — Chave da OpenAI criada, com limite de gasto, guardada no `.env` (§2)
- [ ] **P0** — Programas instalados e `venv/` com `harness/requirements.txt` (§1, §3)
- [ ] **P0** — Teste mínimo do Agno com a OpenAI (§3)
- [ ] **P0** — Arquivos de bancada anonimizados, fora do Git, incluindo o par de receitas para a conciliação (§5)
- [ ] **P0** — Teste de bancada dos modelos da OpenAI; registrar na HA-D2 (§4)
- [ ] **P0** — Voz do Piper escolhida e baixada; modelo do Whisper baixado na máquina de produção (§6)
- [ ] **P0** — Combinados com A e C (§7), incluindo BE-D3, HA-D7 e o C8
- [ ] **P0** — Máquina de produção preparada (§8)

## Base

- [ ] **P0** — Agno e dependências fixados em `requirements.txt`, telemetria desligada (§3.1)
- [ ] **P0** — `agentes/modelos.py`: modelos da OpenAI pelo Agno, saída tipada validada, tempo máximo e novas tentativas (§3.2)
- [ ] **P0** — Stubs de `normalizar`, `checar_lista`, `detectar_alarme`, `avaliar_gravidade` e `info_remedio` (C2–C4, C8)
- [ ] **P0** — `RepositorioEmMemoria` (C6, com os métodos de 24/10) e modelo falso compatível com o Agno para testes
- [ ] **P0** — `processar_mensagem` com a ordem fixa do §5
- [ ] **P0** — `processar_evento` para os 3 eventos agendados (§5.1)

## Percepção

- [ ] **P0** — Subagente Leitor: foto → `LeituraBruta` (§6.2)
- [ ] **P0** — Subagente Intérprete: transcrição ou texto do PDF → `ItensInterpretados`, com médico, data, quantidade por dose e embalagem (§6.3)
- [ ] **P0** — Workflow de leitura com pós-processamento e "para que serve" (§2.4, §6.1, §6.4)
- [ ] **P0** — Fluxo de confiança baixa (§6.5)
- [ ] **P0** — Caixa de remédio que já está na lista (§6.6)
- [ ] **P0** — Escuta local: WebM/Opus e MP4/AAC → texto (§8)
- [ ] **P0** — Contexto a cada mensagem (§3.3, §5 passo 3)

## Conciliação (E1)

- [ ] **P0** — Pergunta de escopo da receita e ação `definir_escopo` (§7.2)
- [ ] **P0** — `conciliar`: novo, mantido, alterado, ausente (§7.3)
- [ ] **P0** — Proposta com mudanças, ação `decidir_item` e frases fixas (§7.4)

## Decisão e ações

- [ ] **P0** — Registro de ferramentas, com a lista de ferramentas de cada agente (§17.1)
- [ ] **P0** — Subagentes Rotina e Explicador, com "para que serve" (§2.2, §10)
- [ ] **P0** — Subagente Agenda: registrar consulta com confirmação (§11.1)
- [ ] **P0** — Subagente Farmácia: estoque e Farmácia Popular (§12)
- [ ] **P0** — Equipe da Seri: coordenadora em modo `route` com os 5 membros (§2.3, HA-D8)
- [ ] **P0** — Limite de 5 chamadas de ferramenta somando todos os agentes (§17)
- [ ] **P0** — Subagente Diário + Workflow do diário (§9)
- [ ] **P0** — Escalonador: conduta → 192, resumo + link, ou observar (§9)
- [ ] **P0** — `gerar_resumo` → `Resumo` (C5), nos dois tipos

## Preparo da consulta (E2)

- [ ] **P0** — Dossiê e perguntas candidatas (§11.2)
- [ ] **P0** — Subagente Preparador + validação das perguntas (§11.2)
- [ ] **P0** — Workflow do preparo e mensagem `consulta_preparada` (§11.2)
- [ ] **P0** — Pós-consulta: pergunta, relato pela Agenda e aviso de receita nova (§11.3)

## Remédio nunca falta (E4)

- [ ] **P0** — `estoque.calcular` e `registrar_estoque` (§12.1)
- [ ] **P0** — Avisos de 7 e 2 dias na verificação diária (§12.1, HA-D11)
- [ ] **P0** — Frases do Farmácia Popular (§12.3)
- [ ] **P1** — Validade da receita e aviso (§12.2)

## Guardrails

- [ ] **P0** — Regras fixas antes de qualquer agente, inclusive no relato da consulta (§13.1)
- [ ] **P0** — Confirmação humana por pendência e as ações de 24/10, sem agente (§13.2)
- [ ] **P0** — Auditor com as 4 verificações, incluindo indicação sem fonte (§13.3)
- [ ] **P0** — Textos fixos de alerta, conduta, conciliação, para que serve, estoque e bloqueio (`frases.py`)
- [ ] **P0** — Instruções de cada subagente com a persona da Seri (§16, §17)
- [ ] **P0** — Fala: `falar(texto)` em MP3 (§14)

## Integração e prova

- [ ] **P0** — Trocar os stubs pelas funções reais de C (inclusive C8)
- [ ] **P0** — Plugar na API de A (sem stub), com `processar_evento`
- [ ] **P0** — Expor o C7 para a avaliação (com `conciliacao`)
- [ ] **P0** — Testes do §18
- [ ] **P1** — Registro de passos por agente, com tokens (§15)
