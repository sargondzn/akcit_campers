# Checklist — backend

> **Dona:** Pessoa A (Beatriz). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md).

## Esqueleto (primeiro, porque destrava B e C)

- [ ] **P0** — Estrutura do repositório e `pyproject.toml` (00-projeto/spec §4)
- [ ] **P0** — `.gitignore` com `.env`, `*.sqlite*`, `armazenamento/`, `**/dados_privados/`, `dados/brutos/`
- [ ] **P0** — `contratos/` com os tipos do 00-projeto/spec §5 (acordo dos três)
- [ ] **P0** — Stub do harness (C1) com resposta fixa para cada tipo de mensagem (§6)
- [ ] **P0** — Docker Compose com `api` (sem `ollama` desde 24/10); `.env.exemplo` com as variáveis novas, sem a chave; instruções de setup (§10)

## API e banco

- [ ] **P0** — Tabelas do §3
- [ ] **P0** — Cadastro, login e token (§4)
- [ ] **P0** — Consentimento e bloqueio `403` sem aceite
- [ ] **P0** — Idoso (apelido)
- [ ] **P0** — Upload e armazenamento de foto, PDF e áudio, com limites e tipos (§4)
- [ ] **P0** — `POST /mensagens` idempotente + fila de uma thread + `GET /conversa` (§5, §6)
- [ ] **P0** — `Repositorio` (C6) sobre o banco, incluindo versões da lista (§7)
- [ ] **P0** — Lista, rotina e registro de dose
- [ ] **P0** — Agendador de lembretes + `GET /lembretes/pendentes` + áudio via `falar` com cache (§8)
- [ ] **P0** — `/demo/lembrete` com `MODO_DEMO=1`
- [ ] **P0** — PDF do resumo + link público com validade e revogação (§9)
- [ ] **P0** — `/saude`
- [ ] **P1** — `/diario`
- [ ] **P1** — Push: chaves VAPID, inscrição e envio pelo agendador
- [ ] **P1** — Tabela e gravação do registro de passos (para B)

## Produção

- [ ] **P0** — Definir a máquina e o responsável (BE-D3)
- [ ] **P0** — Túnel da Cloudflare no perfil `producao` (BE-D2)
- [ ] **P0** — CORS para o domínio da Netlify
- [ ] **P0** — Antes da apresentação: `/saude` verde, modelos aquecidos, `VITE_API_URL` atualizada (§10.3)

## Funcionalidades de 24/10 (E1, E2, E4, E8)

- [ ] **P0** — Campos novos de `ItemLido` e status `retirado` no `item_lista` (§3)
- [ ] **P0** — Ações `definir_escopo`, `decidir_item` e `contar_estoque` e `atualizar_pendencia` no `Repositorio` (C1, C6)
- [ ] **P0** — Tabelas `consulta`, `estoque` e `evento`; métodos novos do C6 (§3, §7)
- [ ] **P0** — Agendador de eventos e `/demo/evento` (§8.1)
- [ ] **P0** — PDF do preparo da consulta (§9)
- [ ] **P0** — `GET /consultas` e `GET /estoque`; "para que serve" na `GET /lista` (C8)
- [ ] **P0** — `/saude` checando a chave da OpenAI, sem expô-la
