# harness — Seriema (Pessoa B)

Sistema multiagente em Agno com os modelos da OpenAI. Spec: [`specs/harness/spec.md`](../specs/harness/spec.md).

## Instalar

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r harness\requirements.txt
```

O `.env` da raiz precisa de `OPENAI_API_KEY` (e, se quiser, `LLM_MODELO_VISAO`, `LLM_MODELO_CONVERSA`). A voz do Piper fica em `armazenamento/vozes/` (fora do Git); sem ela, as respostas saem só em texto.

## Conversar com a Seri no terminal

```powershell
.\venv\Scripts\python.exe -m harness.demo --exemplo
```

`--exemplo` já cadastra 3 remédios, uma consulta amanhã e um estoque de 7 dias. Comandos: texto livre, `/foto <caminho>`, `/pdf <caminho>`, `/audio <caminho>`, `/b <n>` (aperta o botão n), `/corrigir <n> <texto>`, `/evento diario|vespera|pos`, `/lista`, `/passos`, `/sair`. Usa a OpenAI de verdade e um repositório em memória (nada é gravado em banco).

## Testes (sem rede e sem OpenAI)

```powershell
.\venv\Scripts\python.exe -m pytest harness\testes -q
```

## Para A (plataforma) — C1

```python
from harness import processar_mensagem, processar_evento, falar
resposta = processar_mensagem(entrada, repo)      # MensagemEntrada + Repositorio (C6)
resposta = processar_evento(evento, repo)         # EventoAgendado: verificacao_diaria, vespera_consulta, pos_consulta
```

Os tipos estão em `harness/contratos.py` até a pasta `contratos/` existir. `harness/testes/repositorio_memoria.py` é a referência do protocolo `Repositorio`.

## Para C (dados e avaliação)

- Enquanto `dados/` não existir, o harness usa `harness/stubs/dados.py` (dados de exemplo, marcados como STUB, não conferidos). Quando `dados.normalizador`, `dados.farmacovigilante`, `dados.gravidade` e `dados.info_remedio` existirem, `harness/dados_ponte.py` passa a usá-los sozinho.
- C7: `harness.leitor.ler(anexo)`, `harness.auditor.verificar(texto, contexto)`, `harness.diario.estruturar(texto)`, `harness.conciliacao.conciliar(...)`.
