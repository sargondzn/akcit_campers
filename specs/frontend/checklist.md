# Checklist — frontend

> **Dona:** Pessoa A (Beatriz). **P0** = a demo não acontece sem ela; **P1** = se der tempo (o que sobrar vai para a final).
> Spec: [`spec.md`](spec.md).

## Base

- [ ] **P0** — Projeto React + Vite + Tailwind + shadcn/ui em `plataforma/frontend/` (§2)
- [ ] **P0** — Layout mobile-first: coluna única, largura máxima 480 px, barra inferior, áreas seguras, `100dvh`, fonte ≥ 16 px, toque ≥ 48 px (§5)
- [ ] **P0** — Cliente da API com `VITE_API_URL`, token Bearer e tratamento de 401/403 (§6)
- [ ] **P0** — Dados falsos locais para trabalhar antes da API (§6)

## Telas

- [ ] **P0** — Entrar / Criar conta
- [ ] **P0** — Consentimento (texto conforme FE-D3)
- [ ] **P0** — Idoso (apelido)
- [ ] **P0** — Conversa: balões e todos os tipos de `MensagemSaida` (§3.1)
- [ ] **P0** — Conversa: indicador "a Seri está…" e consulta a cada 2 s (§6)
- [ ] **P0** — Remédios: lista confirmada + itens não confirmados
- [ ] **P0** — Rotina simples: horários de hoje com Tomei / Não tomei
- [ ] **P0** — Lembrete na tela com áudio (§3.2)
- [ ] **P0** — Resumo: abrir PDF e compartilhar o link (Web Share / copiar)
- [ ] **P1** — Rotina completa
- [ ] **P1** — Diário

## Envio

- [ ] **P0** — Foto: câmera traseira + galeria, orientação, redução para 1600 px (§4.1)
- [ ] **P0** — PDF até 10 MB (§4.2)
- [ ] **P0** — Áudio: tocar para gravar/parar, limite de 2 min, WebM/Opus ou MP4 (§4.3)
- [ ] **P0** — Fila local no IndexedDB com reenvio e `mensagem_id` (§4.4)

## PWA e entrega

- [ ] **P0** — Manifesto, ícones e service worker sem cache da API (§7)
- [ ] **P0** — Tela "Instalar o app" (Android e iPhone)
- [ ] **P0** — Deploy na Netlify com redirecionamento de SPA e `VITE_API_URL`
- [ ] **P0** — Roteiro da demo testado em Android e iPhone reais, com o app instalado (00-projeto/spec §8)
- [ ] **P1** — Push: permissão, inscrição VAPID, recebimento com o app fechado
