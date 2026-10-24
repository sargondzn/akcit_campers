# Spec — backend

> **Dona:** Pessoa A (Beatriz) · **Status:** 🟡 escrita em 23/10/2026 a partir de D2, D6, D8, D9, D14, D17 e D22. Os padrões marcados com **(BE-Dn)** valem até resposta em contrário na [`discussao.md`](discussao.md).
> Regras gerais, contratos (C1, C5, C6, C8) e arquitetura: [`00-projeto/spec.md`](../00-projeto/spec.md).
> **Atualização de 24/10/2026** (pedido do usuário, escrita por B): modelos da OpenAI no lugar dos locais (D3) e funcionalidades E1, E2, E4 e E8 (D23). As partes novas estão marcadas com **(24/10)**. **A revisa** e ajusta os detalhes de implementação.

---

## 1. Escopo

**Regional:** API, contas, consentimento, banco, arquivos, fila de mensagens que chama o harness, implementação do `Repositorio` (C6), cronograma e lembretes, PDF e link público do resumo (C5), infraestrutura local (Docker) e de produção (túnel).
**(24/10)** Também no regional: consultas e seus eventos (E2), estoque (E4), PDF do preparo da consulta (E2), "para que serve" na lista (E8, via C8) e as ações da conciliação (E1).
**Final:** PostgreSQL + armazenamento de objetos + fila (D6), API do painel do profissional.

## 2. Stack

- Python 3.12, FastAPI, Pydantic, Uvicorn.
- SQLAlchemy sobre **SQLite** (modo WAL). No regional, as tabelas são criadas por código; migrações (Alembic) ficam para a final.
- APScheduler para os lembretes. Fuso **America/Sao_Paulo**.
- Senhas com hash Argon2 (ou bcrypt); token JWT.
- PDF: biblioteca a critério de A **(BE-D4)**.
- Web Push (P1): `pywebpush` com chaves VAPID geradas por nós.
- ffmpeg instalado na imagem (usado pela voz do harness).
- **(24/10)** A API sai para a internet (API da OpenAI, chamada pelo harness). A chave fica só em `OPENAI_API_KEY`.

## 3. Modelo de dados

| Tabela | Colunas principais |
|---|---|
| `conta` | id, email (único), senha_hash, criada_em |
| `consentimento` | id, conta_id, versao_termo, aceito_em |
| `idoso` | id, conta_id (único: um idoso por conta), apelido |
| `arquivo` | id, conta_id, tipo (foto/pdf/audio/audio_seri/resumo_pdf), mime, caminho, tamanho, criado_em |
| `mensagem` | id (= `mensagem_id` do celular, ou gerado para as da Seri), conta_id, autor (cuidadora/seri), tipo, conteudo (JSON: texto, itens, alertas, botões…), arquivo_id, status (processando/respondida/erro — só nas da cuidadora), em_resposta_a, criada_em |
| `pendencia` | id, conta_id, tipo, dados (JSON), status (aberta/confirmada/recusada), criada_em, resolvida_em |
| `lista_versao` | id, idoso_id, versao, confirmada_em |
| `item_lista` | id, lista_versao_id, item (JSON de `ItemLido`, com os campos novos de 24/10: prescritor, data_receita, unidades_por_dose…), status (inclui `retirado`) |
| `horario` | id, idoso_id, item_id, hora ("08:00"), ativo |
| `dose` | id, horario_id, previsto_para, status (tomada/nao_tomada/sem_resposta), registrado_em |
| `lembrete` | id, horario_id, dose_id, disparado_em, texto, audio_arquivo_id, visto_em |
| `sintoma` | id, idoso_id, sintoma (JSON), conduta (JSON), registrado_em |
| `resumo` | id, idoso_id, tipo (escalonamento/preparo_consulta, 24/10), conteudo (JSON de `Resumo`), pdf_arquivo_id, token_publico, expira_em, revogado |
| `consulta` **(24/10)** | id, idoso_id, data_hora, profissional, local, relato (JSON de `RelatoConsulta`), criada_em |
| `estoque` **(24/10)** | id, idoso_id, item_id, principio_ativo, quantidade, origem (falado/caixa_foto), registrado_em |
| `evento` **(24/10)** | id, tipo (verificacao_diaria/vespera_consulta/pos_consulta), idoso_id, consulta_id, agendado_para, disparado_em |
| `inscricao_push` | id, conta_id, dados (JSON) — P1 |
| `passo_harness` | id, mensagem_id, ordem, tipo, conteudo (JSON), duracao_ms, criado_em — P1 |

Regras:

- `salvar_lista_confirmada` cria **uma nova `lista_versao`** (versões antigas nunca são apagadas) e recria os `horario` a partir dos `horarios` de cada item confirmado. Item sem horário entra na lista, mas não no cronograma.
- Itens `nao_confirmado`/`ilegivel` ficam guardados na versão com o status, **fora do cronograma**.

## 4. Autenticação, consentimento e segurança

- `POST /auth/cadastro` e `POST /auth/login` devolvem um JWT com validade de 7 dias, enviado em `Authorization: Bearer`.
- Todo endpoint de dados exige token **e** consentimento aceito (sem ele: `403` com `{"motivo": "consentimento"}`).
- CORS liberado só para o domínio da Netlify e `http://localhost:*`.
- Arquivos guardados em `armazenamento/<conta_id>/<uuid>.<ext>`, fora de qualquer pasta pública; só são servidos por endpoint autenticado que confere o dono.
- Tipos aceitos: `image/jpeg`, `image/png`, `image/heic` (convertido para JPEG), `application/pdf`, `audio/webm`, `audio/mp4`, `audio/mpeg`. Limite de **10 MB** por arquivo.
- Logs só com ids, tempos e erros (00-projeto/spec §7.3).

## 5. Endpoints

| Método | Caminho | O que faz |
|---|---|---|
| GET | `/saude` | Verifica se a API e o banco respondem e se a chave da OpenAI é aceita (sem token; não expõe a chave) |
| POST | `/auth/cadastro` | Cria a conta |
| POST | `/auth/login` | Devolve o token |
| GET | `/consentimento/termo` | Texto e versão atuais do termo |
| POST | `/consentimento` | Registra o aceite (`versao_termo`) |
| GET / PUT | `/idoso` | Lê ou define o apelido |
| POST | `/mensagens` | `multipart`: `mensagem_id`, `tipo`, `texto?`, `arquivo?`, `acao?` (JSON). Responde **`202`** `{"mensagem_id", "status"}`. Idempotente pelo `mensagem_id` |
| GET | `/conversa?depois=<cursor>&limite=50` | Mensagens novas (da cuidadora e da Seri), com status, e o próximo cursor |
| GET | `/arquivos/{id}` | Baixa um arquivo da própria conta (foto, áudio da Seri, PDF) |
| GET | `/lista` | Versão atual da lista com os itens |
| GET | `/lista/versoes` | Histórico de versões |
| GET | `/rotina?dia=AAAA-MM-DD` | Horários do dia com o status da dose |
| POST | `/doses` | `{"horario_id", "previsto_para", "status"}` — "Tomei" / "Não tomei" |
| GET | `/lembretes/pendentes` | Lembretes disparados e ainda não vistos |
| POST | `/lembretes/{id}/visto` | Marca como visto |
| GET | `/diario` | Sintomas e condutas (P1 na tela, mas o endpoint é simples) |
| GET | `/consultas` **(24/10)** | Próximas consultas e as anteriores, com o link do preparo, se houver |
| GET | `/estoque` **(24/10)** | Estoque estimado e dias restantes por remédio (calculado pelo harness, `estoque.calcular`) |
| GET | `/resumos/{id}` | Dados do resumo e as URLs |
| GET | `/r/{token}` | **Link público** do resumo (sem conta): devolve o PDF; `404` se expirado ou revogado; cabeçalho `X-Robots-Tag: noindex` |
| POST | `/resumos/{id}/revogar` | Desativa o link público |
| POST | `/demo/lembrete` | Dispara agora o próximo lembrete da conta. **Só existe com `MODO_DEMO=1`** |
| POST | `/demo/evento` **(24/10)** | `{"tipo", "consulta_id?"}`: dispara agora um evento agendado (véspera, pós-consulta, verificação diária). **Só com `MODO_DEMO=1`** |
| GET | `/push/chave` | Chave pública VAPID (P1) |
| POST | `/push/inscricao` | Guarda a inscrição de push (P1) |

## 6. Fila de mensagens e chamada ao harness

- `POST /mensagens` grava a mensagem (`processando`) e o anexo e coloca na fila. **Uma única thread de trabalho** consome a fila em ordem de chegada (mantém a ordem da conversa e a transcrição local em CPU).
- A thread monta a `MensagemEntrada` (C1) e chama `harness.processar_mensagem(entrada, repo)` com o `Repositorio` da API.
- Ações de pendência (`tipo = "acao"`) também passam pela fila, para manter a ordem da conversa.
- Cada `MensagemSaida` vira uma `mensagem` da Seri. Áudios da Seri ficam em `arquivo` (`audio_seri`).
- Tempo máximo de **5 min** por mensagem. Erro ou tempo esgotado: status `erro` + resposta fixa (00-projeto/spec §6).
- Ao reiniciar, mensagens que ficaram `processando` voltam para a fila.
- Com `HARNESS_STUB=1`, a API usa o **stub do C1** (respostas fixas para cada tipo), mantido por A.
- **(24/10)** Eventos agendados (§8.1) entram na **mesma fila**, como itens do tipo evento, e chamam `harness.processar_evento(evento, repo)`.

## 7. Repositório (C6)

`plataforma/api/repositorio.py` implementa o protocolo `Repositorio` de `contratos/` sobre o banco. Funções e regras: 00-projeto/spec §5 (C6) e §3 desta spec. `salvar_resumo` chama a geração do PDF (§9) e cria o link público.

## 8. Cronograma e lembretes

- A cada minuto, o APScheduler procura `horario` ativos que venceram e ainda não têm lembrete no dia; para cada um, cria a `dose` (`sem_resposta`) e o `lembrete`.
- Texto do lembrete: `"Hora do remédio: <nome> <concentração>. <posologia_texto>"`. Áudio: `harness.falar(texto)` (C1), com **cache por texto** para não sintetizar o mesmo áudio de novo.
- O frontend vê o lembrete por `GET /lembretes/pendentes` (P0). Com push (P1), o agendador também envia a notificação.
- `/demo/lembrete` usa o mesmo caminho, só que na hora.

### 8.1 Eventos agendados (24/10, E2 e E4)

- `verificacao_diaria`: todo dia às 09:00, para cada idoso com lista confirmada.
- `vespera_consulta`: às 18:00 do dia anterior a cada consulta. `pos_consulta`: às 10:00 do dia seguinte. Os dois são criados por `salvar_consulta` e recriados se a consulta mudar.
- O agendador grava o `evento` e coloca na fila (§6). As mensagens devolvidas viram mensagens da Seri; com push (P1), também viram notificação.
- `/demo/evento` usa o mesmo caminho, só que na hora.
- Horários padrão definidos na HA-D12 (harness).

## 9. Resumo, PDF e link público (C5, D9)

- O PDF tem: cabeçalho "Seriema — Resumo para o profissional de saúde", apelido do idoso, período, motivo, remédios atuais, doses perdidas, sintomas com conduta, alertas com fonte, perguntas para o profissional, o aviso fixo do `Resumo` e a data de geração.
- **(24/10)** `tipo = preparo_consulta` (E2): cabeçalho "Seriema — Para levar à consulta", data, hora e profissional; remédios atuais **com o "para que serve"** (E8); mudanças recentes na lista (E1); doses perdidas; sintomas; alertas; **pontos para conferir**; perguntas. Uma página sempre que possível.
- O link público usa um token aleatório de 32 bytes (`secrets.token_urlsafe`), válido por **7 dias (BE-D1)** e revogável.
- O link mostra só o PDF; não dá acesso à conta nem a outros dados.

## 10. Infraestrutura

### 10.1 Docker Compose (`infra/`)

| Serviço | Imagem | Detalhes |
|---|---|---|
| `api` | Python 3.12-slim + ffmpeg | Volume `armazenamento/` e banco; porta 8000 |
| `tunel` | `cloudflare/cloudflared` | Só no perfil `producao` (BE-D2) |

O frontend roda fora do Compose em desenvolvimento (`npm run dev`) e na Netlify em produção.

### 10.2 Variáveis (`.env.exemplo`, sem segredos reais)

`SEGREDO_JWT`, `ORIGENS_PERMITIDAS`, `CAMINHO_BANCO`, `CAMINHO_ARMAZENAMENTO`, `MODO_DEMO`, `HARNESS_STUB`, `OPENAI_API_KEY` (24/10), `LLM_MODELO_VISAO`, `LLM_MODELO_CONVERSA`, `STT_MODELO`, `TTS_VOZ`, `AGNO_TELEMETRY` (24/10), `VAPID_PUBLICA`, `VAPID_PRIVADA` (P1), `TUNEL_TOKEN` (se túnel nomeado). `LLM_URL_BASE` saiu (24/10).

As variáveis `OPENAI_API_KEY`, `LLM_*`, `STT_*`, `TTS_*` e `AGNO_TELEMETRY` são definidas por B; A só as repassa ao contêiner. `OPENAI_API_KEY` **nunca** vai para o `.env.exemplo`, para o Git ou para log.

### 10.3 Produção (D22)

- Frontend na Netlify; o restante na máquina do time (BE-D3), com `docker compose --profile producao up`.
- Antes da apresentação: `/saude` verde (inclui a chave da OpenAI), crédito e limite de gasto da conta conferidos, internet estável, voz do Piper e modelo do Whisper já baixados, `VITE_API_URL` apontando para o túnel, roteiro testado nos dois celulares.

## 11. Fora do regional

PostgreSQL + objetos + fila (D6), migrações, painel do profissional, exclusão de conta pela interface.
