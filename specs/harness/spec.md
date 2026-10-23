# Spec — harness

> **Dono:** Pessoa B (Caio) · **Status:** 🟡 escrita em 23/10/2026 a partir de D3, D4, D5, D15, D19, D21 e D22. Os padrões marcados com **(HA-Dn)** valem até resposta em contrário na [`discussao.md`](discussao.md).
> Regras gerais, contratos (C1–C7) e arquitetura: [`00-projeto/spec.md`](../00-projeto/spec.md). O que é o harness: [`visao.md` §2.1](../00-projeto/visao.md).

---

## 1. Escopo

O **harness agêntico** é tudo o que envolve o modelo para ele perceber, decidir e agir. Esta frente entrega:

| Camada | Componente | Regional |
|---|---|---|
| Percepção | Leitor (foto de receita física impressa e à mão, foto de caixa, PDF) · Escuta (STT) · Contexto (C6) | P0 |
| Memória | Uso do `Repositorio` (C6): perfil, lista versionada, histórico, pendências | P0 |
| Decisão | Orquestrador: loop com tool use | P0 |
| Ações | Registro de ferramentas · Diário + Escalonador · Fala (TTS) | P0 |
| Guardrails | Regras fixas (192) · Confirmação humana · Auditor | P0 |
| Observabilidade | Registro de passos | P1 |

**Final:** migração do loop para LangGraph (D5), código de barras, tendências no diário, efeito adverso × sintoma.

## 2. Estrutura de `harness/`

```
harness/
├── __init__.py            ← expõe processar_mensagem, falar, leitor, auditor, diario (C1, C7)
├── config.py              ← lê as variáveis LLM_*, STT_*, TTS_*
├── cliente_llm.py         ← único ponto que fala com o modelo
├── nucleo.py              ← processar_mensagem: a ordem do §4
├── percepcao/  leitor.py · escuta.py · contexto.py
├── orquestrador.py        ← o loop (§7)
├── ferramentas/  registro.py · <uma por ferramenta>.py
├── diario.py · escalonador.py · fala.py
├── guardrails/  regras_fixas.py · confirmacao.py · auditor.py · frases.py
├── prompts/               ← textos de sistema em .md, em português
├── registro_passos.py     ← P1
├── stubs/                 ← stubs de C2–C4 (até C entregar)
└── testes/                ← RepositorioEmMemoria (C6), LLM falso, testes
```

Cada etapa do §4 é uma **função pura sobre um estado** (entrada → estado → saída). Isso facilita os testes e a migração para os nós do LangGraph na final.

## 3. Cliente do LLM e modelos

- **Ollama local, em CPU** (D3, D22), pela API compatível com a da OpenAI (`LLM_URL_BASE`). Trocar por API comercial na final = mudar só `cliente_llm.py` e as variáveis.
- Dois papéis: `LLM_MODELO_VISAO` (Leitor) e `LLM_MODELO_CONVERSA` (Orquestrador, Diário). Pode ser o mesmo modelo, se ele fizer as duas coisas bem.
- **Escolha dos modelos por teste de bancada** (primeira tarefa do checklist), na máquina de produção: modelos open-source de 2–4 B parâmetros, com visão e com tool use no Ollama (ponto de partida: família Qwen-VL para visão e Qwen3 para conversa). Critérios, em ordem: lê receita impressa e caixa; chama ferramenta no formato certo; tempo por foto; português. O resultado vai para a HA-D2.
- Extração com temperatura 0 e **saída em JSON validada com Pydantic**. JSON inválido → 1 nova tentativa com o erro na mensagem → falha controlada.
- Tempo máximo por chamada: 180 s (ajustável depois do teste de bancada). Ollama fora do ar → mensagem fixa de indisponibilidade.
- **Plano B do tool use:** se o modelo pequeno não chamar ferramentas de forma confiável pelo mecanismo nativo, o loop pede um JSON `{"ferramenta": ..., "argumentos": {...}}` ou `{"responder": "..."}` e o valida com o mesmo registro. O resto do harness não muda.

## 4. `processar_mensagem` — ordem fixa

```
entrada ─► 1. Percepção ─► 2. Regras fixas ─► 3. Contexto ─► 4. Rota ─► 5. Auditor ─► 6. Fala? ─► RespostaHarness
                               │ alarme                                       ▲
                               └──────────► ligue_192 (fixo) ─────────────────┘
```

1. **Percepção:** `texto` segue como está; `audio` → Escuta → texto; `foto`/`pdf` → Leitor → itens; `acao` → Confirmação (§9.2).
2. **Regras fixas:** para todo texto (digitado ou transcrito), `detectar_alarme` (C4). Se houver alarme: `registrar_sintoma`, mensagem fixa `ligue_192` e **fim** — o modelo não participa.
3. **Contexto:** carrega pelo `Repositorio` o idoso, a lista atual, as pendências abertas, as doses e o diário dos últimos 7 dias e as últimas 20 mensagens. Vira um bloco de contexto compacto para o modelo.
4. **Rota:**
   - `foto`/`pdf` → **fluxo de leitura** (§5), fluxo fixo **(HA-D1)**.
   - Pendência `diario_aberto` ou relato de sintoma → **Diário** (§8).
   - Demais textos → **Orquestrador** (§7).
5. **Auditor** em todo texto de saída (§9.3).
6. **Fala:** a primeira mensagem de texto de cada resposta ganha áudio pelo TTS (§10).
7. **Registro de passos** em cada etapa (P1, §11).

## 5. Leitor e fluxo de leitura

### 5.1 Entrada

- **Foto** (já reduzida pelo celular): vai direto ao modelo de visão.
- **PDF:** primeiro extrai o texto (pypdf). Se houver texto, o modelo de conversa estrutura os itens a partir dele. Se não houver (PDF escaneado), cada página vira imagem (pypdfium2) e segue como foto.

### 5.2 Saída do modelo

O prompt pede, para cada remédio: `nome_lido`, `concentracao`, `forma`, `posologia_texto`, `horarios` sugeridos a partir da posologia e `confianca_modelo` (0–1). Também pede que nada seja inventado: o que não se lê fica nulo.

### 5.3 Pós-processamento (determinístico)

1. `normalizar(nome_lido)` (C2) preenche `principio_ativo` e, se faltar, `concentracao`.
2. **Confiança final** = `confianca_modelo`, limitada a **0,5** quando `normalizar` não encontra o remédio ou quando faltam nome ou concentração.
3. Confiança final < **0,7 (HA-D3)** = leitura baixa.
4. `checar_lista` (C3) com a **lista atual + itens novos** gera os alertas.

### 5.4 Fluxo de confiança baixa (D19)

1. **1ª tentativa:** `pedido_de_foto` — "Não consegui ler bem <nome ou 'um dos remédios'>. Pode tirar outra foto, com mais luz e sem dobras?" (pendência `leitura_baixa_confianca`).
2. **Ainda baixa:** botões "Foto da caixa deste remédio" e "Digitar ou falar o nome".
3. **Até a cuidadora confirmar**, o item fica `nao_confirmado` e **não entra no cronograma**.
4. **Se nada resolver:** o item fica `ilegivel`, fora da lista ativa, com o aviso "Confirme este remédio com o farmacêutico".

### 5.5 Proposta e confirmação

- A Seri responde com `lista_para_confirmar` (lista atual + novos itens, cada um com status e confiança) e os `alertas`, e cria a pendência `lista_para_confirmar` com a proposta.
- Botões: **"Confirmo a lista"** (`confirmar_pendencia`) e **"Corrigir um item"** (abre o teclado ou a gravação; a correção chega como `corrigir_item`, o item é refeito pelo `normalizar` e uma nova proposta substitui a anterior).
- Só `confirmar_pendencia` executa `salvar_lista_confirmada` (§9.2).

## 6. Escuta (STT)

- faster-whisper, idioma `pt`, modelo em `STT_MODELO` (padrão `small`, `int8` em CPU; trocar por `base` se ficar lento), com filtro de voz (VAD).
- ffmpeg converte WebM/Opus e MP4/AAC para WAV 16 kHz mono antes da transcrição.
- Transcrição vazia → "Não consegui ouvir. Pode gravar de novo, mais perto do celular?"

## 7. Orquestrador

- Mensagem de sistema (`prompts/sistema.md`): persona da Seri (§12), regras do §9 em linguagem direta, o bloco de contexto e a lista de ferramentas do registro.
- **Loop:** o modelo responde **ou** pede uma ferramenta → o harness valida os argumentos (Pydantic) → executa (ou cria pendência, se `exige_confirmacao`) → devolve o resultado como observação → repete.
- **No máximo 5 chamadas de ferramenta por mensagem** (D21). Argumento inválido ou ferramenta desconhecida conta como chamada e volta como erro de observação. No limite, o harness pede ao modelo a resposta final sem ferramentas; se ainda falhar, responde "Vou precisar de um pouco mais de informação. Pode me contar de outro jeito?".

### 7.1 Registro de ferramentas

| Ferramenta | O que faz | Implementação | Exige confirmação |
|---|---|---|---|
| `consultar_lista` | Lista atual, cronograma e pendências | C6 (A) | Não |
| `consultar_doses` | Doses do período (tomadas, perdidas) | C6 (A) | Não |
| `normalizar` | Nome → princípio ativo | C2 (C) | Não |
| `checar_lista` | Alertas da lista atual | C3 (C) | Não |
| `avaliar_gravidade` | Sintoma → conduta | C4 (C) | Não |
| `pedir_foto` | Pede foto de receita ou de caixa | B | Não |
| `registrar_dose` | "Ela já tomou o das 8h" | C6 (A) | **Não** (D21) |
| `registrar_sintoma` | Guarda sintoma + conduta | C6 (A) | **Não** (D21) |
| `gerar_resumo` | Monta o `Resumo` (C5) e chama `salvar_resumo` | B + A | Não |
| `escalar` | Mensagem com a conduta + resumo e link | B | Não |
| `salvar_lista_confirmada` | Grava a nova versão da lista | C6 (A) | **Sim** |
| `alterar_cronograma` | Muda, inclui ou remove horários | C6 (A) | **Sim** |

Cada entrada do registro tem: `nome`, `descricao` (em português, para o modelo), `entrada` e `saida` (modelos Pydantic), `exige_confirmacao` e `funcao`. Ferramenta fora do registro não existe para o modelo.

## 8. Diário e Escalonador

1. Texto (transcrito ou digitado) → `diario.estruturar` → `SintomaEstruturado` (modelo de conversa, JSON).
2. **Faltou o essencial** (o que, desde quando, intensidade)? Até **2 perguntas**, uma por vez, com pendência `diario_aberto`. A resposta seguinte da cuidadora completa o sintoma.
3. `detectar_alarme` de novo sobre o sintoma estruturado (segurança dupla) → `avaliar_gravidade` (C4) → `registrar_sintoma`.
4. Por conduta:
   - `ligue_192` → mensagem fixa `ligue_192`.
   - `atendimento_24h` → "Isso precisa ser visto por um profissional em até 24 horas." + `gerar_resumo` + mensagem `resumo` com o link.
   - `observar` → "Anotei. Se piorar ou aparecer <sinais da regra>, me conte na hora."
5. A frase de conduta é **fixa por nível** (`guardrails/frases.py`). O modelo não escreve conduta.

## 9. Guardrails

### 9.1 Regras fixas

- `detectar_alarme` (C4) roda antes do modelo (§4, passo 2) e de novo no Diário (§8).
- Mensagem fixa: **"Isso pode ser um sinal de alarme. Ligue agora para o SAMU: 192."** + botão `tel:192`.

### 9.2 Confirmação humana

- Ferramenta com `exige_confirmacao` **não executa**: cria pendência com os argumentos e responde com a proposta e os botões.
- `confirmar_pendencia` executa exatamente os argumentos guardados; `recusar_pendencia` descarta. Pendência já resolvida é ignorada (clique duplo).

### 9.3 Auditor (determinístico no regional, HA-D4)

Verifica todo `texto` de saída antes de liberar:

1. **Frases proibidas:** orientação de dose, troca ou suspensão (ex.: "tome", "pode tomar", "aumente", "diminua", "dobre", "suspenda", "pare de tomar", "troque", "substitua"), com variações. A lista fica em `guardrails/frases.py` e é ampliada com os casos do conjunto de guardrail da avaliação.
2. **Números de dose:** quantidade + unidade (mg, ml, gotas, comprimidos) só passa se corresponder a um item da lista atual ou da proposta.
3. **Remédio fora da lista:** nome de remédio conhecido pelo Normalizador que não está na lista nem na proposta.
4. **Fato clínico sem fonte:** menção a interação, efeito, contraindicação ou duplicidade sem um `Alerta` ou `Conduta` gerado nesta resposta.

Bloqueio → o texto é trocado por **"Não posso orientar sobre doses ou troca de remédios. Leve essa dúvida ao farmacêutico ou médico."** (ou pela frase fixa do caso) e o motivo vai para o registro de passos. Mensagens fixas desta spec passam pelo Auditor como as outras.

### 9.4 Alertas para a cuidadora (D15.2)

O texto do alerta é montado a partir do `Alerta`: "<descrição>. Fonte: <fonte>. **Leve ao farmacêutico ou médico antes de mudar qualquer coisa.**" O modelo pode explicar em palavras simples, sem acrescentar fato.

## 10. Fala (TTS)

- Piper, voz pt-BR em `TTS_VOZ`; ffmpeg converte para **MP3**.
- `falar(texto) -> Anexo` (C1) atende a API (lembretes) e o próprio harness (§4, passo 6).
- Textos longos (> 400 caracteres) não ganham áudio, para não atrasar a resposta.

## 11. Registro de passos (P1, D21)

`repo.registrar_passo` com `mensagem_id`, ordem, tipo (`percepcao`, `regra_fixa`, `contexto`, `modelo`, `ferramenta`, `resultado`, `bloqueio_auditor`, `resposta`), conteúdo resumido, duração (ms) e modelo usado. Fica **só no servidor** e serve para depurar, para a avaliação e para mostrar o harness funcionando na banca.

## 12. Persona da Seri

- Português do Brasil, "você", frases curtas, no máximo 3 frases por mensagem, sem jargão (diz "remédio", não "fármaco").
- Acolhedora, sem prometer resultado e sem se apresentar como profissional de saúde.
- Sempre que não souber: diz que não sabe e encaminha a um humano.

## 13. Testes

- Auditor: casos positivos e negativos (incluindo os 20 do conjunto de guardrail).
- Regras fixas: os 4 sinais do guardrail chegam a `ligue_192` sem o modelo ser chamado.
- Loop: LLM falso que pede ferramentas em sequência; limite de 5; ferramenta com confirmação vira pendência.
- Leitor: 3 imagens de exemplo de bancada (fora do Git) para checagem rápida.
