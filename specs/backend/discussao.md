# Discussão — backend

> **Dona:** Pessoa A (Beatriz). As decisões de projeto já tomadas estão na [`00-projeto/discussao.md`](../00-projeto/discussao.md) (D2, D6, D8, D9, D14, D17, D22).
> As perguntas abaixo **não bloqueiam o início**: a [`spec.md`](spec.md) já usa a recomendação como padrão. A BE-D3 precisa de resposta **antes da demo**.

---

## BE-D1 — Validade do link público do resumo

**Contexto:** o profissional abre o PDF sem conta (D9). Um link sem prazo fica circulando com dado de saúde.

**Recomendação:** 7 dias, com opção de revogar.

**Resposta:**

---

## BE-D2 — Túnel rápido ou nomeado

**Contexto:** o túnel rápido da Cloudflare não pede conta, mas gera uma URL nova a cada vez que sobe; aí é preciso atualizar `VITE_API_URL` e republicar o frontend. O túnel nomeado mantém a URL fixa, mas exige conta na Cloudflare e um domínio gerenciado por ela.

**Perguntas:** alguém do time tem domínio? Aceitamos o túnel rápido no regional?

**Recomendação:** túnel rápido no regional, com um passo do checklist para atualizar a URL antes da apresentação; nomeado se houver domínio.

**Resposta:**

---

## BE-D3 — Máquina de produção

**Contexto:** a API, os modelos e o banco rodam num computador do time (D22), que precisa ficar ligado e conectado durante a avaliação e a demo. Em CPU, uma máquina com mais núcleos e memória deixa a leitura mais rápida (sugestão: 16 GB de RAM ou mais).

**Perguntas:** qual computador? Quem fica responsável por ele no dia?

**Resposta:**

---

## BE-D4 — Biblioteca de PDF

**Contexto:** WeasyPrint gera o PDF a partir de HTML/CSS (fácil de deixar bonito, depende de bibliotecas do sistema, resolvido no Docker). ReportLab é Python puro, porém mais trabalhoso de diagramar.

**Recomendação:** WeasyPrint. A decide.

**Resposta:**
