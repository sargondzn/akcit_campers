# Seriema — API

API da plataforma Seriema (Pessoa A). Contas, consentimento, arquivos, lista versionada, lembrete e o PDF do resumo. A conversa passa pelo harness (`harness.processar_mensagem`, contrato C1): `app/ponte.py` faz a chamada e `app/repositorio.py` é o `Repositorio` (C6) sobre o banco. Com `HARNESS_STUB=1`, `app/stub.py` responde no lugar do harness, com respostas fixas.

A interface está no repositório `akcit-campers-front`. Esta API fica aqui, em `plataforma/api`.

## Rodar

No PowerShell, a partir desta pasta:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Conta pronta para a demo: `demo@seriema.local` / `seriema`.

O `requirements.txt` já instala as dependências do harness (`harness/requirements.txt`). O `.env` da raiz do repositório precisa de `OPENAI_API_KEY`: sem ela, a leitura da foto responde que o serviço está indisponível. Uma foto leva de 10 a 30 segundos.

Para rodar sem OpenAI, com as respostas fixas (Git Bash):

```bash
HARNESS_STUB=1 ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Os arquivos e o banco ficam em `dados/` e não entram no Git.

## O que a interface chama

| Método | Caminho | Uso |
|---|---|---|
| POST | `/api/entrar` | E-mail e senha. E-mail novo cria a conta |
| GET | `/api/sessao` | Diz se o consentimento já foi aceito |
| POST | `/api/consentimento` | Aceite e nome da pessoa cuidada |
| GET | `/api/conversa` | Histórico, lembrete e se a lista pode ser confirmada |
| POST | `/api/mensagens` | Texto, foto, PDF ou áudio |
| POST | `/api/acoes` | `confirmar_lista` |
| GET | `/api/lista` | Versão mais recente |
| POST | `/api/doses` | Registra que o horário do lembrete foi visto |
| GET | `/api/resumo.pdf` | PDF só com a sessão da cuidadora |
| GET | `/api/arquivos/{id}` | Foto, PDF ou áudio da própria conta |

Foto ou PDF passam pelo Leitor e pelo Intérprete do harness e viram uma lista para confirmar (`listas` sem confirmação). "Confirmar lista" resolve a pendência `lista_para_confirmar` no harness, que grava a versão confirmada. Botões do harness com ação (escopo da receita, item ausente, estoque) chegam em `acoes` com id `botao:<mensagem>:<n>` e voltam por `POST /api/acoes`. Texto de alarme cai nas regras fixas do harness e devolve "ligue 192".

Com `HARNESS_STUB=1`: foto ou PDF devolvem a lista fixa da demonstração, áudio devolve o resumo sem transcrição.

## O que falta

Anotado em 23/10/2026.

### Desta API, para a demo

- [ ] Publicar em **HTTPS**, no mesmo endereço em que a interface for publicada. Câmera e microfone no celular de outra pessoa dependem disso.
- [x] Trocar o stub de `app/stub.py` pela chamada real do harness (24/10/2026, `app/ponte.py`).
- [ ] Fila com status `processando` e retomada ao reiniciar (spec §6). Hoje a chamada roda numa thread, uma por vez, e a requisição espera a resposta.
- [ ] Interface: mostrar as ações `botao:...` como botões. Hoje ela só desenha `ligar_192` e `baixar_resumo`.
- [ ] Lembrete por horário marcado. Hoje ele aparece na hora em que a lista é confirmada.
- [ ] Confirmar o reenvio de arquivo quando a rede cai. A interface já guarda a foto para tentar de novo; a API em si não tem fila.

### De outras frentes

- [ ] Leitura da foto e do PDF, transcrição, voz do lembrete e Auditor (harness).
- [ ] Normalização, interações e gravidade com fonte real (dados).
- [ ] Avaliação e conjuntos de teste.

O PDF, o 192 e o alerta que saem hoje são da demonstração. Não são leitura nem checagem clínica.

## Teste

```powershell
.\.venv\Scripts\python.exe -m pytest
```
