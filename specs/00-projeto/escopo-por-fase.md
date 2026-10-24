# Escopo por fase — regional × final

> **Para que serve:** deixar claro **o que precisa estar pronto no regional** e **o que fica conscientemente para a final**. Se não está na seção 2, não é trabalho do regional.
> **Fontes:** [`visao.md`](visao.md) §2.2 e §5, as respostas da [`discussao.md`](discussao.md) e a Parte 7 do plano (`docs/f3_plano_startup_v1.md`, fora do repositório).
> **Atualizado em:** 24/10/2026 (modelos da OpenAI; E1, E2, E4 e E8 no regional).

---

## 1. Regras de corte

1. **Regional P0:** sem isso a demo não acontece. É obrigatório.
2. **Regional P1:** entra se der tempo.
3. **Final:** só começa depois da entrega do regional, salvo decisão em contrário.
4. **Item P1 que não ficar pronto no regional passa automaticamente para a final** (D16).

Datas: regional em **24/10, Goiânia** (D11). Final em **28/11**, no Cubo Itaú, com entrega até 17h30.

---

## 2. Regional — o que precisamos concluir

Donos: **A** (Beatriz), **B** (Caio), **C** (Roberto). As tarefas detalhadas estão no `checklist.md` de cada frente.

### 2.1 Funcionalidades

| Área | O que entrega | Dono | Prioridade |
|---|---|---|---|
| **Plataforma** | **Mobile-first** (visão §2.5): login, consentimento, conversa (câmera direta, PDF, gravar e tocar áudio, botões de confirmar), lista de remédios, rotina simples, envio resiliente, **PWA instalável**, testada em Android e iPhone | A | P0 |
| | Telas completas de rotina e diário; push agendado | A | P1 |
| **API e infraestrutura** | Contas, banco (perfil, lista versionada, doses, diário), arquivos, fila de mensagens, PDF + link público do resumo, Docker local, produção (Netlify + máquina do time + túnel) | A | P0 |
| **Entrada e leitura** | Foto da receita física (impressa e à mão), foto de caixa e PDF → lista com confiança; confirmação obrigatória; fluxo de confiança baixa (D19) | B | P0 |
| **Normalização** | Nome comercial → princípio ativo e concentração para **~20 remédios** (Anvisa/CMED) (D16) | C | P0 |
| **Farmacovigilância mínima** | Mesmo princípio ativo em nomes diferentes + tabela curada (interações, duplicidade de classe, CBMPI), **gerada e conferida com LLM**, com fonte (D7, D15.4) | C | P0 |
| **Rotina** | Cronograma; lembrete com texto e áudio disparado na hora (demo); confirmação de dose | A + B (voz) | P0 |
| **Diário e escalonamento** | Áudio → sintoma estruturado → regras de gravidade → "ligue 192" ou resumo em PDF + link | B + C (regras) | P0 |
| **Auditor e guardrails** | Bloqueio de frases proibidas, de dose, de remédio fora da lista e de fato clínico sem fonte | B | P0 |
| **Harness agêntico** | Sistema multiagente em **Agno**: coordenadora + subagentes (Leitor, Intérprete, Rotina, Explicador, Diário, Agenda, Preparador, Farmácia) e fluxos fixos; até 5 ferramentas por mensagem, registro de ferramentas, contexto a cada decisão, **modelos da API da OpenAI** | B | P0 |
| **E8 — Para que serve** | Frase de uso comum de cada remédio, com fonte, na conversa, na proposta, na tela Remédios e no preparo | B + C (tabela) + A (tela) | P0 |
| **E1 — Conciliação** | Receita nova × lista: escopo da receita, novo/mantido/alterado/ausente, decisão da cuidadora sobre o ausente | B + A (cartão) | P0 |
| **E2 — Preparo da consulta** | Registrar consulta; página "Para levar à consulta" na véspera; registro do que o médico disse | B + A (agenda, PDF, eventos) | P0 |
| **E4 — Remédio nunca falta** | Estoque e aviso de 7 e 2 dias; Farmácia Popular | B + A (estoque, eventos) + C (tabela) | P0 |
| | Validade da receita e aviso de vencimento | B + C (tabela) | P1 |
| | Registro de passos (D21) | B | P1 |

### 2.2 Avaliação

| Conjunto | Dono | Prioridade |
|---|---|---|
| Executor + relatório de métricas | C | P0 |
| 20 fotos de caixas | C (fotos: todos) | P0 |
| 10 fotos de receitas impressas e 20 de manuscritas (D19) | C (receitas: todos) | P0 |
| 30 pares de interação e duplicidade, conferidos com LLM | C | P0 |
| 20 tentativas de arrancar dose (guardrail), incluindo 5 de E1 e E8 ("posso tirar o remédio que não veio?") | C | P0 |
| 10 casos de conciliação (lista antes + receita nova → mudanças esperadas) | C | P1 |
| 10 PDFs de receita digital | C | P1 |
| 20 relatos de sintoma, conferidos com LLM | C | P1 |

### 2.3 Entregáveis e validação

| O que | Dono | Prioridade |
|---|---|---|
| GitHub com protótipo, BMC, pitch e documentação do fluxo | Todos (negócio: C) | P0 |
| Pitch de 3 min com demo ao vivo (foto → lista → alerta → para que serve → receita nova com conciliação → áudio → escalonamento → preparo da consulta → aviso de estoque), ensaiado | Todos | P0 |
| Vídeo de backup da demo | Todos | P0 |
| Entrevistas (1 feita; meta 5 a 10); checar o critério de giro | C | P0 |
| Revisão de todos os materiais de negócio (D12.3) | A e B | P0 |
| Checar o nome (INPI, registro.br, Instagram, lojas) | C | P1 |
| Checar o campo de princípio ativo no dicionário de dados da Anvisa | C | P0 |

---

## 3. Final — o que fica para depois do regional

Os donos são sugeridos pela frente de cada um e serão confirmados depois do regional.

### 3.1 Produto e tecnologia

| Funcionalidade | Dono sugerido | Origem |
|---|---|---|
| **Painel do farmacêutico ou da enfermeira**, com fila de casos, desenhado primeiro para o computador | A | Plano §4.7 |
| **Código de barras da caixa** como entrada | B | Plano §4.7 |
| **Tendências no diário** ("3 dias de tontura") | B | Plano §4.7 |
| **Efeito adverso × sintoma relatado** | B + C | Plano §4.7 |
| **Base de interações completa e licenciada** | C | Mudança de 22/10 |
| **Conversão de nomes PT → internacional em escala** | C | Mudança de 22/10 |
| **CBMPI completo + critérios de Beers** | C | Mudança de 22/10 |
| **RAG em bulas** (Bulário Eletrônico da Anvisa) | C | Mudança de 22/10 |
| **Normalizador ampliado** (de ~20 para mais remédios) | C | D16 |
| **Tabelas clínicas mais completas e revisadas por profissional** | C | D7.2, D15.4 |
| **Conjunto de caixas de 20 para 50 fotos**; receitas reais em quantidade satisfatória | C (fotos: todos) | Mudança de 22/10; D19.4 |
| **Equipe da Seri em modo `coordinate`** | B | D5 atualizada, HA-D8 |
| **E3, E5, E6 e E7** (rede de cuidado, cuidar de quem cuida, dúvidas de administração, padrões no tempo), se aprovadas depois | Todos | D23 |
| **PostgreSQL + armazenamento de objetos + fila** | A | D6 |
| Correções apontadas pela banca e pelos mentores do regional (v1.1) | Todos | Plano, Parte 7 |
| Itens P1 do regional que não ficarem prontos | Dono original | Regra 4 |

### 3.2 Validação e negócio

| Tarefa | Quando (plano) | Dono |
|---|---|---|
| Recrutar 5 a 10 famílias e assinar termo de consentimento (LGPD) | 25/10–31/10 | C |
| **Piloto de 2 semanas**: medir uso diário, doses confirmadas, alertas e o que as cuidadoras dizem | 02/11–15/11 | Todos |
| Conversas com 2–3 farmácias regionais e 1–2 operadoras/autogestões; **buscar carta de intenção** | 02/11–15/11 | C |
| **Unit economics** com números reais | 09/11–15/11 | C |
| Levantar quanto das internações de idosos vem de erro de medicação em casa | até a final | C |
| **Análise regulatória** (RDC 657/2022 e 751/2022), com parecer de especialista se possível | 09/11–15/11 | C |
| **Revisão profissional** das tabelas, pares e relatos, se necessário | até a final | C |
| **Licença comercial** da base de interações | até a final | C |
| Resposta para a banca sobre o pagador (operadora como primeira tese, D15.3) | até a final | C |
| Nova frase de posicionamento no lugar de "pelo WhatsApp" | até a final | C |

Todas as tarefas de negócio passam pela revisão de A e B (D12.3).

### 3.3 Entregáveis da final

| O que | Quando (plano) |
|---|---|
| 3º relatório quinzenal | 01/11 |
| 4º relatório quinzenal | 15/11 |
| Pitch de 5 min para investidores: problema → tração do piloto → modelo B2B2C → unit economics → mercado → time → pedido | 16/11–22/11 |
| Mentoria dos finalistas (levar as 3 perguntas mais difíceis esperadas) | semana de 23/11 |
| Ensaio com banca simulada (Anvisa, quem paga, por que a operadora não faz sozinha) | 24/11–27/11 |
| **Entrega e pitch na final** | 28/11, até 17h30 |
