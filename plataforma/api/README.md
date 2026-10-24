# Seriema — API

API da plataforma Seriema (Pessoa A). Contas, consentimento, arquivos, lista versionada, lembrete e o PDF do resumo. A leitura da foto, a transcrição, a voz e a checagem de interações ficam fora: enquanto isso, `app/stub.py` responde no formato do contrato C1.

A interface está no repositório `akcit-campers-front`. Esta API fica aqui, em `plataforma/api`.

## Rodar

No PowerShell, a partir desta pasta:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Conta pronta para a demo: `demo@seriema.local` / `seriema`.

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
| PUT | `/api/lista/itens` | Ajusta os remédios (nome, concentração, horário opcional, foto opcional) |
| POST | `/api/arquivos` | Sobe foto da caixa ou do blister para um item da lista |
| POST | `/api/doses` | Registra que o horário do lembrete foi visto |
| GET | `/api/resumo.pdf` | PDF só com a sessão da cuidadora |
| GET | `/api/arquivos/{id}` | Foto, PDF ou áudio da própria conta |

Foto ou PDF devolvem a lista fixa da demonstração e um alerta. Texto com queda, batida na cabeça, dor no peito, falta de ar ou confusão devolve "ligue 192" sem passar por outro fluxo. Áudio devolve o resumo. A transcrição ainda não existe.

## O que falta

Anotado em 23/10/2026.

### Desta API, para a demo

- [ ] Publicar em **HTTPS**, no mesmo endereço em que a interface for publicada. Câmera e microfone no celular de outra pessoa dependem disso.
- [ ] Trocar o stub de `app/stub.py` pela chamada real do harness quando o contrato C1 estiver ligado. Até lá, a lista é fixa e o áudio não é transcrito.
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
