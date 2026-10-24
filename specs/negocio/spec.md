# Spec — negocio

> **Dono:** Pessoa C (Roberto), com **revisão obrigatória de A e B** (D12.3) · **Status:** 🟡 escrita em 23/10/2026 a partir de D10, D11, D12 e D15.
> Não é necessária para o sistema funcionar, mas é **fundamental no dia do AKCIT Camp** (D10.1). Contexto de negócio: [`visao.md` §1, §3 e §4](../00-projeto/visao.md).

---

## 1. Regra de revisão

Nenhum material de negócio é entregue ou apresentado sem que **os três** tenham revisado. Cada entregável tem, no checklist, uma linha de revisão por A e outra por B.

## 2. Entregáveis do regional

| Entregável | Conteúdo | Onde fica |
|---|---|---|
| **BMC** | O canvas do plano atualizado com as decisões das specs: plataforma própria no lugar do WhatsApp (canais, relacionamento, custos e parcerias), **operadora como primeiro pagador** (D15.3), farmácia como canal e trava regulatória, modelos da API da OpenAI desde 24/10 (custo por chamada, medido pela avaliação, mais a máquina do time para API e voz) | `negocio/bmc.md` (+ imagem ou PDF) |
| **Pitch de 3 min com demo ao vivo** | Roteiro da demo (00-projeto/spec §8): foto → lista → alerta → para que serve → receita nova com conciliação → áudio → escalonamento → preparo da consulta → aviso de estoque. Argumentos da visão §4.2 (teste de remoção, contexto favorável, unit economics ilustrativos). Números do relatório da avaliação | `negocio/pitch/` (slides em PDF + roteiro falado) |
| **Vídeo de backup da demo** | O mesmo roteiro gravado em celular real, para o caso de a rede ou a máquina falhar | Fora do Git (pasta compartilhada); link em `negocio/pitch/` |
| **Documentação do fluxo** | Ponteiro para `specs/` (visão, divisão, specs das frentes) + um diagrama do fluxo da cuidadora | `negocio/fluxo.md` |
| **Entrevistas** | Meta do plano: 5 a 10 (cuidadoras, farmacêuticos, enfermeiras de ESF). **1 feita** (D11.3). Checar o critério de giro (visão §4.3) | Síntese em `negocio/entrevistas.md`; anotações brutas fora do Git |
| **Relatórios quinzenais** | Conforme o calendário do plano | `negocio/relatorios/` |
| **Checagem do nome** (P1) | Seriema: INPI (classes 9 e 44), registro.br, Instagram, lojas | `negocio/nome.md` |

## 3. O que o pitch pode e não pode afirmar

Para não prometer o que o protótipo não faz:

- **Pode:** "lê a receita física, junta a lista, alerta, lembra, escuta e escala"; "nunca sugere dose — é bloqueado por um Auditor independente"; "o modelo roda localmente, e a foto não sai para um provedor de IA"; os números do `avaliacao/relatorios/resumo.md`, com o n real.
- **Não pode:** dizer que as interações foram validadas por farmacêutico (no regional, foram geradas e conferidas com LLM, D7.2/D15.4); citar números de avaliação que não estejam no relatório; dizer "sem app para baixar" ou "pelo WhatsApp" (frases do plano que deixaram de valer, visão §4.2).

## 4. Entrevistas

- Roteiro e públicos do plano. Registro anonimizado: só papel e cidade, nunca nome.
- A síntese registra, para cada entrevista: confirma ou não que o remédio é a dor; reação à plataforma própria (instalaria? usaria no dia a dia? — risco de adoção da visão §3); quem pagaria.

## 5. Final

Itens de validação e negócio da final (piloto, carta de intenção, unit economics reais, análise regulatória, licença de base, nova frase de posicionamento, pitch de 5 min): [`escopo-por-fase.md` §3.2 e §3.3](../00-projeto/escopo-por-fase.md).
