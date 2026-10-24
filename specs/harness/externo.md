# Tarefas externas — harness

> **Dono:** Pessoa B (Caio) · escrito em 24/10/2026; atualizado no mesmo dia para o harness multiagente em **Agno**, os **modelos da API da OpenAI** e as funcionalidades **E1, E2, E4 e E8** (spec §1–§3).
> Tudo o que precisa ser feito **fora do código**, por uma pessoa: criar a chave da OpenAI, instalar programas, juntar arquivos de teste, combinar com o time e preparar a máquina da demo. O código não consegue fazer nada disso sozinho.
> Spec: [`spec.md`](spec.md) · Checklist: [`checklist.md`](checklist.md).

**Chave de API: uma, a da OpenAI** (§2). A voz continua local (sem chave). O Agno não tem conta nem chave.

Ordem sugerida: §2 (chave) → §1 e §3 (instalação) → §5 (arquivos) → §4 (bancada, destrava a HA-D2) → §6 e §7 em paralelo → §8 → §9 no dia.

---

## 1. Programas na sua máquina de desenvolvimento

| Programa | Para quê | Como instalar (Windows, PowerShell) | Como conferir |
|---|---|---|---|
| Python 3.12 | Projeto Python único (00-projeto §2). Já instalado em 24/10 | `winget install Python.Python.3.12` | `py -3.12 --version` |
| Git | Já instalado | — | `git --version` |
| ffmpeg | Converter WebM/Opus e MP4/AAC para WAV e gerar o MP3 da fala (spec §8 e §14) | `winget install Gyan.FFmpeg` e reabrir o terminal | `ffmpeg -version` |
| Docker Desktop | Rodar o Docker Compose de A (D8) | `winget install Docker.DockerDesktop` (pede WSL 2 e reinício) | `docker compose version` |
| Dependências Python do harness | Agno, cliente da OpenAI, PDF, Whisper, Piper, testes | `harness/requirements.txt`, num `venv/` (§3) | §3, item 3 |

O **Ollama não é mais necessário** (os modelos rodam na OpenAI desde 24/10). Se você já instalou, pode desinstalar.

Espaço em disco: reserve **~3 GB** (modelo do Whisper, voz do Piper e imagens Docker).

---

## 2. Chave da API da OpenAI

1. Entre em https://platform.openai.com com a conta que vai pagar (sua ou do time) e crie, se ainda não houver, uma **organização** para o time.
2. **Crie um projeto só para a Seriema** (menu de projetos → *Create project*, nome `seriema`). Assim o gasto e as chaves ficam separados de outros usos.
3. **Billing:** cadastre um cartão ou compre créditos. Veja se o AKCIT Camp ou algum parceiro oferece créditos.
4. **Limite de gasto:** em *Limits* do projeto, defina um **orçamento mensal** e um alerta por e-mail (sugestão: alerta em 50% e 80%). É isso que impede uma conta surpresa se algo entrar em laço.
5. **Crie a chave:** *API keys* do projeto → *Create new secret key*, nome `seriema-<sua máquina>`. Se a tela oferecer permissões restritas, deixe só o necessário para *Responses* e *Models*.
6. **Copie a chave na hora.** Ela não aparece de novo.
7. Guarde a chave **só** num arquivo `.env` na raiz do repositório (o `.gitignore` já cobre `.env`):
   ```
   OPENAI_API_KEY=sk-...
   LLM_MODELO_VISAO=gpt-6-luna
   LLM_MODELO_CONVERSA=gpt-6-luna
   AGNO_TELEMETRY=false
   ```
   **Nunca** coloque a chave no código, no Git, no `.env.exemplo`, em print de tela ou numa conversa (inclusive comigo). Se ela vazar, revogue em *API keys* e crie outra.
8. **Uma chave por máquina** (a sua e a de produção), para poder revogar uma sem derrubar a outra.
9. **Privacidade:** leia a página de uso de dados da API da OpenAI (procure "API data usage" ou "Your data" na documentação) e anote três coisas para Beatriz pôr no termo de consentimento (FE-D3): se os dados da API são usados para treino, por quanto tempo ficam guardados e em que país são processados. Até 24/10, a regra conhecida era: **não são usados para treino por padrão** e podem ficar guardados por um tempo limitado para monitoramento de abuso. **Confira na página atual**, porque isso muda.
10. Conferir os modelos: em https://developers.openai.com/api/docs/models, confirme que `gpt-6-luna` e `gpt-6.1-sol` (pontos de partida da spec §3.2) aparecem e anote os preços por milhão de tokens. Os preços entram na conta de custo da avaliação.

---

## 3. Ambiente Python (`venv/`) e Agno

1. Na raiz do repositório, crie o ambiente virtual em `venv/` (já está no `.gitignore`) e instale as dependências:
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\python.exe -m pip install --upgrade pip
   .\venv\Scripts\python.exe -m pip install -r harness\requirements.txt
   ```
   Em 24/10, essa instalação foi testada num ambiente limpo com Python 3.12 no Windows e funcionou.
2. Para não digitar o caminho toda vez, ative o ambiente: `.\venv\Scripts\Activate.ps1`. Se o PowerShell bloquear, rode antes `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
3. Conferir: `python -c "import agno, openai, faster_whisper, piper, pypdf, pypdfium2; print('ok')"`.
4. **Teste mínimo** de um agente com a OpenAI: saída tipada, ferramenta e imagem. Salve como `teste_agno.py` **fora do repositório** (ex.: na Área de Trabalho), troque o caminho da foto por uma das imagens do §5 e rode com o ambiente ativado (`python teste_agno.py`):
   ```python
   from dotenv import load_dotenv
   load_dotenv(r"C:\dev\akcit_camp\.env")

   from pydantic import BaseModel
   from agno.agent import Agent
   from agno.media import Image
   from agno.models.openai.responses import OpenAIResponses

   class Remedio(BaseModel):
       nome: str
       concentracao: str | None

   def consultar_lista() -> str:
       """Devolve a lista atual de remédios do idoso."""
       return "losartana 50 mg; metformina 850 mg"

   modelo = OpenAIResponses(id="gpt-6-luna")

   extrator = Agent(model=modelo, output_schema=Remedio, telemetry=False)
   print(extrator.run("Receita: Losartana potássica 50mg, 1 cp de 12/12h").content)

   rotina = Agent(model=modelo, tools=[consultar_lista], tool_call_limit=5, telemetry=False)
   rotina.print_response("Quais remédios ela toma hoje?")

   leitor = Agent(model=modelo, telemetry=False)
   leitor.print_response("Transcreva os remédios e a posologia desta receita, sem interpretar.",
                         images=[Image(filepath=r"C:\caminho\da\receita_impressa.jpg")])
   ```
   Deu certo se: o primeiro `print` mostra um `Remedio` preenchido; a segunda resposta cita os dois remédios (a ferramenta foi chamada); a terceira transcreve a receita.
5. Erros comuns: `401` = chave errada ou revogada; `429` = sem crédito ou limite de uso atingido (§2, itens 3 e 4); `404 model` = nome do modelo mudou (§2, item 10).
6. Anote a versão instalada (`pip show agno`). Ela já está fixada em `harness/requirements.txt`; avise A quando o `pyproject.toml` existir.

> Os nomes das classes e parâmetros acima (`Agent`, `Team`, `Workflow`, `output_schema`, `tool_call_limit`, `telemetry`, `agno.media.Image`, `agno.models.openai.responses.OpenAIResponses`) foram conferidos no Agno 3.1.10 em 24/10/2026. Se uma versão nova mudar algum nome, avise B para ajustar a spec.

---

## 4. Teste de bancada dos modelos (destrava a HA-D2)

Com a OpenAI, o teste **não depende mais da máquina de produção**: pode ser feito na sua.

1. Use as imagens do §5. Para cada modelo candidato (`gpt-6-luna` nos dois papéis; `gpt-6.1-sol` como Leitor, se o `luna` errar a receita à mão), anote:
   - acertou princípio ativo e concentração da receita impressa, da receita à mão e da caixa? (sim/não por item);
   - leu o médico, a data da receita e a quantidade da caixa? (E1, E4);
   - a saída tipada veio válida e a ferramenta foi chamada? (teste do §3, item 4; depois, o script de bancada que vou deixar em `harness/`);
   - tempo por foto **somando os dois subagentes** (Leitor + Intérprete) e por mensagem de conversa (coordenadora + subagente);
   - **custo**: tokens de entrada e saída (o Agno mostra nas métricas da execução; a página *Usage* da OpenAI também) × preço do §2, item 10;
   - português da resposta.
2. Preencher a **HA-D2** na [`discussao.md`](discussao.md) com: modelo de visão, modelo de conversa, acertos, tempo médio e custo médio por foto e por mensagem.

---

## 5. Arquivos de teste da bancada (fora do Git)

| Arquivo | Quantidade | Para quê |
|---|---|---|
| Foto de receita **impressa** | 1 | Leitura |
| Foto de receita **à mão** | 1 | Leitura (o maior risco) |
| Foto de **caixa** de remédio (frente, com nome, concentração e quantidade legíveis) | 1 | Leitura e estoque (E4) |
| PDF de receita digital (com texto) | 1 | Leitura |
| PDF escaneado (só imagem) | 1 | Leitura |
| **Par de receitas do mesmo médico**, uma antiga e uma nova, com pelo menos um remédio que mudou de dose e um que saiu | 1 par | Conciliação (E1) |
| Uma receita de **outro médico** | 1 | Escopo da conciliação (E1) |

Regras (D14, avaliação §2):

1. **Anonimize antes de salvar:** cubra nome do paciente, endereço, telefone e CRM (editor de imagem simples, retângulo preto). **Deixe visível a especialidade** (ou o nome curto do médico) e a **data**: a conciliação (E1) e a validade da receita (E4) precisam deles.
2. Lembre que essas fotos agora **vão para a OpenAI** no teste. Use só receitas anonimizadas e de quem autorizou.
3. Tire a foto como a cuidadora tiraria: celular, luz de casa, sem scanner.
4. Guarde em `harness/testes/dados_privados/`. **Antes**, confira se o `.gitignore` já cobre `**/dados_privados/` (tarefa de A no esqueleto, 00-projeto §4). Em 24/10 o `.gitignore` só tinha `docs/`, `venv/`, `.venv/` e `.env`: até A acrescentar, deixe os arquivos fora do repositório.
5. Se puder, aproveite as mesmas fotos para os conjuntos da avaliação de Roberto (`caixas`, `receitas_impressas`, `receitas_manuscritas`, `conciliacao`).

---

## 6. Voz local: Escuta (STT) e Fala (TTS)

A voz continua na máquina (decisão de 24/10): o áudio da cuidadora não vai para a OpenAI.

### 6.1 faster-whisper (Escuta)

O modelo é baixado sozinho do Hugging Face na primeira transcrição (`small`, ~500 MB). Não precisa de conta nem de chave.

1. Rodar uma transcrição na **máquina de produção** antes do dia da demo, para o download não acontecer na frente da banca.
2. Combinar com A que a pasta de cache do modelo (`~/.cache/huggingface`) fique num **volume do Docker**.

### 6.2 Piper (Fala)

1. Ouvir as vozes pt-BR em https://rhasspy.github.io/piper-samples (escolher **Português (Brasil)**) e escolher uma voz acolhedora (persona da Seri, spec §16).
2. Baixar os **dois arquivos** da voz escolhida em https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR, por exemplo `pt_BR-faber-medium.onnx` **e** `pt_BR-faber-medium.onnx.json`.
3. Guardar os dois juntos, fora do Git, e combinar com A o caminho dentro do contêiner.
4. Definir `TTS_VOZ` com o nome da voz (ex.: `pt_BR-faber-medium`).

### 6.3 Áudios de teste

Gravar frases curtas em cada aparelho: uma comum, uma de sintoma não urgente, uma de alarme ("ela caiu e bateu a cabeça"), uma de consulta ("tenho consulta com o cardiologista dia 30 às duas da tarde") e um relato de consulta ("o médico disse para voltar em três meses e pediu exame de sangue").

- **Android (Chrome):** gera WebM/Opus. Use a gravação da PWA de A quando estiver pronta.
- **iPhone (Safari):** gera MP4/AAC. O gravador de voz do iPhone (`.m4a`) já serve para um primeiro teste.

Guardar junto com as imagens do §5, fora do Git.

---

## 7. Combinar com o time

### Com Beatriz (A — plataforma)

- [ ] **BE-D3:** qual é a máquina de produção e quem cuida dela no dia. Com a OpenAI, ela precisa de **internet estável**, e a exigência de RAM cai.
- [ ] **Integração do C1 (HA-D7):** a API que já está em `plataforma/api` usa caminhos `/api/...`, a ação `confirmar_lista`, responde na hora e ainda não tem `contratos/` nem o `Repositorio` (C6). Combinar qual versão vale antes de plugar o harness.
- [ ] **Contratos novos de 24/10** (00-projeto/spec §5): campos novos do `ItemLido`, `Mudanca`, `InfoRemedio`, as ações `definir_escopo`, `decidir_item` e `contar_estoque`, os tipos `consulta_preparada` e `aviso_estoque`, `EventoAgendado` + `processar_evento`, os campos novos do `Resumo` e os métodos novos do `Repositorio`. Precisam do acordo dos três (00-projeto §7.4).
- [ ] **Agendador de eventos** (verificação diária, véspera e pós-consulta) e `/demo/evento` para a demo (backend §8.1).
- [ ] **PDF "Para levar à consulta"** (backend §9).
- [ ] **Termo de consentimento** citando o processamento pela OpenAI, com o que você anotou no §2, item 9.
- [ ] Variáveis no `.env.exemplo` **sem valores reais**: `OPENAI_API_KEY=`, `LLM_MODELO_VISAO`, `LLM_MODELO_CONVERSA`, `STT_MODELO`, `TTS_VOZ`, `AGNO_TELEMETRY=false`. Tirar `LLM_URL_BASE` e o serviço `ollama` do Compose.
- [ ] Dependências de `harness/requirements.txt` no `pyproject.toml` quando ele existir.
- [ ] ffmpeg na imagem da API e volumes para o cache do Whisper e para a voz do Piper.
- [ ] `.gitignore` cobrindo `**/dados_privados/` (§5).

### Com Roberto (C — dados e avaliação)

- [ ] Formato de saída de `normalizar`, `checar_lista`, `detectar_alarme` e `avaliar_gravidade` conforme C2–C4.
- [ ] **C8 `info_remedio`** e as tabelas novas (dados §4 e §7a): `indicacoes.csv` (para que serve, E8), `farmacia_popular.csv` (E4) e `tipos_receita.csv` (validade, E4). A lista do Farmácia Popular sai da **página oficial do programa no gov.br**, com a data da consulta.
- [ ] Os 20 casos do conjunto de guardrail (5 deles sobre conciliação e "para que serve"), para ampliar as frases proibidas do Auditor (spec §13.3).
- [ ] Os 4 sinais de alarme, para o teste "chega a `ligue_192` sem chamar nenhum agente" (spec §18).
- [ ] Custo por caso no relatório da avaliação (avaliação §5) e no BMC (custo por chamada).
- [ ] Avisar quando o C7 estiver exposto, com `conciliacao`.

---

## 8. Preparar a máquina de produção

Na máquina da BE-D3, com A:

1. `.env` com a **chave de produção** (§2, item 8), os modelos da HA-D2 e `AGNO_TELEMETRY=false`.
2. Modelo do Whisper e voz do Piper já presentes (§6).
3. **Desligar a suspensão** do Windows: Configurações → Sistema → Energia → "Quando conectado, colocar em suspensão após" = **Nunca**. Deixar na tomada.
4. Desativar atualizações automáticas no dia (Windows Update → Pausar atualizações).
5. Internet por cabo, se possível, e um roteador de celular de reserva.
6. Rodar o roteiro inteiro uma vez pelo celular, pela URL da Netlify (00-projeto/spec §8): foto → lista → para que serve → receita nova com conciliação → áudio de alarme → 192 → consulta marcada → preparo → aviso de estoque.

---

## 9. No dia da demo

1. Ligar a máquina **cedo** e subir o Docker Compose.
2. Conferir na OpenAI: **crédito disponível**, limite de gasto não atingido e a página de status (https://status.openai.com) sem incidente.
3. Conferir `GET /saude` (API, banco e chave da OpenAI).
4. Deixar uma consulta marcada e um estoque baixo cadastrado na conta da demo, para disparar o preparo e o aviso com `/demo/evento`.
5. Se o túnel for rápido (BE-D2), conferir com A se a `VITE_API_URL` foi atualizada e o frontend republicado.
6. Ter o **vídeo de backup** à mão (frente `negocio`): sem internet ou sem OpenAI, a demo ao vivo não funciona.
