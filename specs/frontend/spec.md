# Spec — frontend

> **Dona:** Pessoa A (Beatriz) · **Status:** 🟡 escrita em 23/10/2026 a partir de D1, D9, D16, D17, D18, D20 e D22. Os padrões marcados com **(FE-Dn)** valem até resposta em contrário na [`discussao.md`](discussao.md).
> Regras gerais, contratos e arquitetura: [`00-projeto/spec.md`](../00-projeto/spec.md). Requisitos mobile: [`visao.md` §2.5](../00-projeto/visao.md).
> **Atualização de 24/10/2026** (pedido do usuário, escrita por B): modelos da OpenAI no lugar dos locais (D3) e funcionalidades E1, E2, E4 e E8 (D23). As partes novas estão marcadas com **(24/10)**. **A revisa** e ajusta os detalhes de implementação.

---

## 1. Escopo

**Regional:** a área da cuidadora, **mobile-first** e **instalável como PWA**: conta, consentimento, conversa com a Seri (foto, PDF, áudio, texto, botões), lista de remédios, rotina do dia, lembrete na tela, resumo com link.
**Final:** painel do profissional, desenhado primeiro para o computador ([`escopo-por-fase.md`](../00-projeto/escopo-por-fase.md) §3).

## 2. Stack

- React + Vite + `vite-plugin-pwa`; Tailwind + shadcn/ui (D18, D20.5).
- Linguagem: TypeScript **(FE-D1)**.
- Rotas: React Router. Chamadas à API: `fetch` com um cliente único em `src/api/` (biblioteca de cache a critério de A).
- Hospedagem: **Netlify** (D8). Build `npm run build`, pasta publicada `dist`, redirecionamento de SPA `/* /index.html 200`, variável `VITE_API_URL`.

## 3. Telas e navegação

Barra inferior fixa com as abas **Conversa · Remédios · Rotina**. A aba **Diário** só aparece quando a tela estiver pronta (P1, **FE-D2**). Ordem de entrada: Entrar → Consentimento → Idoso → Conversa.

| Tela | Conteúdo | Prioridade |
|---|---|---|
| **Entrar / Criar conta** | E-mail + senha (mínimo 8 caracteres). Erros em frase simples | P0 |
| **Consentimento** | Texto do termo (**FE-D3**), caixa "Li e concordo" e botão "Continuar". Sem aceite, nada mais abre. Envia a versão do termo aceita. **(24/10)** O termo diz que foto, receita e transcrição do áudio são processadas pela OpenAI e que o áudio fica na nossa máquina | P0 |
| **Idoso** | Um campo: apelido do idoso ("Como você chama a pessoa que você cuida?") | P0 |
| **Conversa** (início) | Mensagens da Seri e da cuidadora; barra de envio (§4); indicador "a Seri está lendo a receita…" enquanto houver mensagem `processando` | P0 |
| **Remédios** | Lista confirmada atual (versão e data); itens "não confirmados" em seção separada, com aviso "confirme com o farmacêutico". **(24/10)** Em cada item: **"Para que serve"** (frase do C8 + "o motivo exato, só o médico que receitou pode dizer"); selo **"Grátis no Farmácia Popular"** quando houver; **"Dura até <dia>"** (estoque) e **"Receita vence em <dia>"** quando houver; botão "Comprei mais" (abre a conversa com o teclado) | P0 |
| **Rotina** | Horários de hoje com "Tomei" / "Não tomei" | P0 (versão simples) |
| **Consultas** **(24/10)** | Dentro da aba Rotina: próximas consultas (data, hora, profissional) e as anteriores, com "Abrir a página da consulta" quando houver preparo. Marcar consulta é pela conversa ("Tenho consulta…") | P0 |
| **Rotina completa** | Semana, histórico de doses | P1 |
| **Diário** | Sintomas registrados e a conduta de cada um | P1 |
| **Instalar o app** | Android: botão que usa o `beforeinstallprompt`. iPhone: passo a passo ilustrado ("Compartilhar → Adicionar à Tela de Início"). Aparece na primeira entrada e no menu; some quando o app já está instalado (`display-mode: standalone`) | P0 |

### 3.1 Como cada `MensagemSaida` aparece (C1)

| `tipo` | Visual |
|---|---|
| `texto` | Balão da Seri. Se tiver `audio`, botão "▶ Ouvir" |
| `lista_para_confirmar` | Cartão com um item por linha: nome, princípio ativo, concentração, horários e **"para que serve"** (`info`, 24/10). Item com `confianca` baixa ganha a etiqueta "conferir"; `nao_confirmado`/`ilegivel` em cinza com o aviso. Alertas embutidos no fim do cartão. Botões vindos de `botoes` (ex.: "Confirmo a lista", "Corrigir um item"). **(24/10) Com `mudancas` (E1):** itens agrupados em **Novos**, **Mudou** ("Antes: … · Agora: …"), **Não veio nesta receita** (com os 3 botões "Continua", "O médico tirou", "Não sei" em cada item, que enviam `decidir_item`) e **Sem mudança** (recolhido) |
| `alertas` | Cartão amarelo: descrição, fonte e a frase fixa "Leve ao farmacêutico ou médico antes de mudar qualquer coisa" |
| `pedido_de_foto` | Balão + botões de `botoes` (`abre: camera/galeria/teclado/gravar`) |
| `ligue_192` | Cartão **vermelho**, ocupando a largura, com botão grande "Ligar 192" (`tel:192`) |
| `resumo` | Cartão com "Abrir PDF" e "Enviar para o profissional" (Web Share API com a `url_publica`; sem suporte, botão "Copiar link") |
| `consulta_preparada` **(24/10)** | Cartão da consulta (data, hora, profissional) com "Abrir a página" e "Enviar para o profissional", como o `resumo` |
| `aviso_estoque` **(24/10)** | Cartão laranja: remédio, "deve acabar por volta de <dia>" ou "receita vence em <dia>", texto do Farmácia Popular quando houver, botão "Comprei mais" |

Botões com `acao` enviam uma `MensagemEntrada` do tipo `acao`. Depois de usados, ficam desabilitados.

### 3.2 Lembrete na tela (P0)

- Com o app aberto, o frontend consulta `GET /lembretes/pendentes` a cada 30 s.
- Lembrete pendente abre um **painel inferior** com o texto ("Hora do remédio: Losartana 50 mg, 1 comprimido"), o botão "▶ Ouvir" (o navegador pode bloquear o som automático, então tocar sempre exige um toque) e "Tomei" / "Não tomei".
- Push com o app fechado é P1 (§7).

## 4. Barra de envio da conversa

Fixa na parte de baixo, ao alcance do polegar: **[📷 Foto] [📄 PDF] [🎤 Áudio]** + campo de texto + enviar.

### 4.1 Foto

- "Foto" abre a câmera traseira (`<input type="file" accept="image/*" capture="environment">`) e oferece "Escolher da galeria" (o mesmo input sem `capture`).
- Antes do envio: corrigir a orientação (EXIF), reduzir o maior lado para **1600 px** e salvar em JPEG com qualidade 0,8.
- Mostrar uma miniatura e "Enviar" / "Tirar outra".

### 4.2 PDF

- `accept="application/pdf"`, limite de **10 MB**.

### 4.3 Áudio

- **Tocar para gravar, tocar para parar** (D20.2). Durante a gravação: botão grande vermelho, cronômetro e "Cancelar".
- Limite de **2 min** (para sozinho).
- `MediaRecorder` com o primeiro formato suportado entre `audio/webm;codecs=opus` e `audio/mp4`.
- Permissão de microfone negada → mensagem explicando como liberar no Android e no iPhone.

### 4.4 Envio resiliente

- Toda mensagem ganha um `mensagem_id` (UUID) no celular e entra numa **fila local no IndexedDB**, com o arquivo.
- Estados visíveis em cada balão: *enviando* · *enviado* · *falhou — tentando de novo*.
- Reenvio automático com espera crescente (2 s, 5 s, 15 s, 30 s…) e botão "Tentar agora". A fila sobrevive a recarregar a página e a fechar o app.
- O reenvio usa o mesmo `mensagem_id`; a API não duplica.

## 5. Requisitos mobile (visão §2.5, D20)

- Uma coluna em retrato; no computador, coluna central com **largura máxima de 480 px** (D20.4: basta funcionar).
- Área de toque ≥ **48 px**; ações principais na metade de baixo.
- Fonte base ≥ **16 px** (evita o zoom automático do iPhone); contraste mínimo WCAG AA; frases curtas.
- Altura com `100dvh`; respeitar `env(safe-area-inset-*)`; `viewport-fit=cover`.
- Teclado virtual: o campo em foco não pode ficar coberto (rolar até ele).
- Referência de desempenho: Android de entrada em 4G fraco (D20.3) — bundle inicial enxuto, imagens reduzidas, nada pesado na primeira tela.
- Teste obrigatório em **Android (Chrome)** e **iPhone (Safari, instalado na tela inicial)** (D20.1).

## 6. Integração com a API

- Base: `VITE_API_URL`. Token no `localStorage` e enviado em `Authorization: Bearer`. Resposta `401` → volta para Entrar; `403` por falta de consentimento → tela de Consentimento.
- Conversa: `GET /conversa?depois=<cursor>` a cada **2 s** enquanto houver mensagem `processando`; fora disso, ao abrir a tela e ao voltar o foco para o app.
- Endpoints usados: ver [`backend/spec.md`](../backend/spec.md) §5.
- Enquanto a API não existir, A usa **dados falsos locais** no frontend; enquanto o harness não existir, a API usa o stub do C1.

## 7. PWA

- **Manifesto:** `name` "Seriema", `short_name` "Seriema", `lang` "pt-BR", `display` "standalone", `start_url` "/", cores do tema, ícones 192 px e 512 px + versão `maskable`, ícone da Apple (180 px).
- **Service worker** (`vite-plugin-pwa`): guarda só os arquivos do app (HTML, JS, CSS, ícones). **Nunca guarda respostas da API** (dados de saúde).
- Atualização: quando houver versão nova, aviso "Nova versão disponível — Atualizar".
- **Push (P1):** depois da instalação, pedir permissão com uma explicação antes; inscrever com a chave pública VAPID de `GET /push/chave`; enviar a inscrição para `POST /push/inscricao`. No iPhone, só oferecer quando o app estiver instalado.

## 8. Textos e acessibilidade

- Português, tom da Seri: acolhedor, direto, "você".
- Todo botão de ícone tem rótulo acessível (`aria-label`).
- Nenhuma tela do frontend escreve orientação clínica própria: textos clínicos vêm do harness (já auditados) ou são as frases fixas desta spec.

## 9. Fora do regional

Painel do profissional (computador), telas completas de rotina e diário (P1), push agendado (P1).
