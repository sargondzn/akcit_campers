# Spec — backend

> **Dona:** Pessoa A (Beatriz) · **Status:** 🟡 escrita em 23/10/2026 a partir de D2, D6, D8, D9, D14, D17 e D22. Os padrões marcados com **(BE-Dn)** valem até resposta em contrário na [`discussao.md`](discussao.md).
> Regras gerais, contratos (C1, C5, C6) e arquitetura: [`00-projeto/spec.md`](../00-projeto/spec.md).

---

## 1. Escopo

**Regional:** API, contas, consentimento, banco, arquivos, fila de mensagens que chama o harness, implementação do `Repositorio` (C6), cronograma e lembretes, PDF e link público do resumo (C5), infraestrutura local (Docker) e de produção (túnel).
**Final:** PostgreSQL + armazenamento de objetos + fila (D6), API do painel do profissional, aviso de estoque.

## 2. Stack

- Python 3.12, FastAPI, Pydantic, Uvicorn.
- SQLAlchemy sobre **SQLite** (modo WAL). No regional, as tabelas são criadas por código; migrações (Alembic) ficam para a final.
- APScheduler para os lembretes. Fuso **America/Sao_Paulo**.
- Senhas com hash Argon2 (ou bcrypt); token JWT.
- PDF: biblioteca a critério de A **(BE-D4)**.
- Web Push (P1): `pywebpush` com chaves VAPID geradas por nós.
- ffmpeg instalado na imagem (usado pela voz do harness).

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
| `item_lista` | id, lista_versao_id, item (JSON de `ItemLido`), status |
| `horario` | id, idoso_id, item_id, hora ("08:00"), ativo |
| `dose` | id, horario_id, previsto_para, status (tomada/nao_tomada/sem_resposta), registrado_em |
| `lembrete` | id, horario_id, dose_id, disparado_em, texto, audio_arquivo_id, visto_em |
| `sintoma` | id, idoso_id, sintoma (JSON), conduta (JSON), registrado_em |
| `resumo` | id, idoso_id, conteudo (JSON de `Resumo`), pdf_arquivo_id, token_publico, expira_em, revogado |
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
| GET | `/saude` | Verifica se a API, o banco e o Ollama respondem (sem token) |
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
| GET | `/resumos/{id}` | Dados do resumo e as URLs |
| GET | `/r/{token}` | **Link público** do resumo (sem conta): devolve o PDF; `404` se expirado ou revogado; cabeçalho `X-Robots-Tag: noindex` |
| POST | `/resumos/{id}/revogar` | Desativa o link público |
| POST | `/demo/lembrete` | Dispara agora o próximo lembrete da conta. **Só existe com `MODO_DEMO=1`** |
| GET | `/push/chave` | Chave pública VAPID (P1) |
| POST | `/push/inscricao` | Guarda a inscrição de push (P1) |

## 6. Fila de mensagens e chamada ao harness

- `POST /mensagens` grava a mensagem (`processando`) e o anexo e coloca na fila. **Uma única thread de trabalho** consome a fila em ordem de chegada (o modelo em CPU não aguenta paralelismo).
- A thread monta a `MensagemEntrada` (C1) e chama `harness.processar_mensagem(entrada, repo)` com o `Repositorio` da API.
- Ações de pendência (`tipo = "acao"`) também passam pela fila, para manter a ordem da conversa.
- Cada `MensagemSaida` vira uma `mensagem` da Seri. Áudios da Seri ficam em `arquivo` (`audio_seri`).
- Tempo máximo de **5 min** por mensagem. Erro ou tempo esgotado: status `erro` + resposta fixa (00-projeto/spec §6).
- Ao reiniciar, mensagens que ficaram `processando` voltam para a fila.
- Com `HARNESS_STUB=1`, a API usa o **stub do C1** (respostas fixas para cada tipo), mantido por A.

## 7. Repositório (C6)

`plataforma/api/repositorio.py` implementa o protocolo `Repositorio` de `contratos/` sobre o banco. Funções e regras: 00-projeto/spec §5 (C6) e §3 desta spec. `salvar_resumo` chama a geração do PDF (§9) e cria o link público.

## 8. Cronograma e lembretes

- A cada minuto, o APScheduler procura `horario` ativos que venceram e ainda não têm lembrete no dia; para cada um, cria a `dose` (`sem_resposta`) e o `lembrete`.
- Texto do lembrete: `"Hora do remédio: <nome> <concentração>. <posologia_texto>"`. Áudio: `harness.falar(texto)` (C1), com **cache por texto** para não sintetizar o mesmo áudio de novo.
- O frontend vê o lembrete por `GET /lembretes/pendentes` (P0). Com push (P1), o agendador também envia a notificação.
- `/demo/lembrete` usa o mesmo caminho, só que na hora.

## 9. Resumo, PDF e link público (C5, D9)

- O PDF tem: cabeçalho "Seriema — Resumo para o profissional de saúde", apelido do idoso, período, motivo, remédios atuais, doses perdidas, sintomas com conduta, alertas com fonte, perguntas para o profissional, o aviso fixo do `Resumo` e a data de geração.
- O link público usa um token aleatório de 32 bytes (`secrets.token_urlsafe`), válido por **7 dias (BE-D1)** e revogável.
- O link mostra só o PDF; não dá acesso à conta nem a outros dados.

## 10. Infraestrutura

### 10.1 Docker Compose (`infra/`)

| Serviço | Imagem | Detalhes |
|---|---|---|
| `api` | Python 3.12-slim + ffmpeg | Volume `armazenamento/` e banco; porta 8000 |
| `ollama` | `ollama/ollama` | Volume para os modelos; o `api` acessa por `http://ollama:11434` |
| `tunel` | `cloudflare/cloudflared` | Só no perfil `producao` (BE-D2) |

O frontend roda fora do Compose em desenvolvimento (`npm run dev`) e na Netlify em produção.

### 10.2 Variáveis (`.env.exemplo`, sem segredos reais)

`SEGREDO_JWT`, `ORIGENS_PERMITIDAS`, `CAMINHO_BANCO`, `CAMINHO_ARMAZENAMENTO`, `MODO_DEMO`, `HARNESS_STUB`, `LLM_URL_BASE`, `LLM_MODELO_VISAO`, `LLM_MODELO_CONVERSA`, `STT_MODELO`, `TTS_VOZ`, `VAPID_PUBLICA`, `VAPID_PRIVADA` (P1), `TUNEL_TOKEN` (se túnel nomeado).

As variáveis `LLM_*`, `STT_*` e `TTS_*` são definidas por B; A só as repassa ao contêiner.

### 10.3 Produção (D22)

- Frontend na Netlify; o restante na máquina do time (BE-D3), com `docker compose --profile producao up`.
- Antes da apresentação: `/saude` verde, modelos já baixados e aquecidos, `VITE_API_URL` apontando para o túnel, roteiro testado nos dois celulares.

## 11. Fora do regional

PostgreSQL + objetos + fila (D6), migrações, painel do profissional, aviso de estoque e renovação de receita, exclusão de conta pela interface.
