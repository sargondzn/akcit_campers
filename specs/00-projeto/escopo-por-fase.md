# Escopo por fase — regional × final

> **Para que serve:** deixar claro **o que precisa estar pronto no regional** e **o que fica conscientemente para a final**. Se não está na seção 2, não é trabalho do regional.
> **Fontes:** [`visao.md`](visao.md) §2.2 e §5, [`checklist.md`](checklist.md) e a Parte 7 do plano ([`docs/f3_plano_startup_v1.md`](../../docs/f3_plano_startup_v1.md)).
> **Atualizado em:** 22/10/2026.

---

## 1. Regras de corte

1. **Regional P0:** sem isso a demo não acontece. É obrigatório.
2. **Regional P1:** entra se der tempo.
3. **Final:** só começa depois da entrega do regional, salvo decisão em contrário.
4. *(proposta, a confirmar na D16)* **Item P1 que não ficar pronto no regional passa automaticamente para a final.**

Datas: regional em **24/10 (Goiânia)** ou **31/10 (Online)**, conforme a D11. Final em **28/11**, no Cubo Itaú, com entrega até 17h30.

---

## 2. Regional — o que precisamos concluir

Donos: **A** (Plataforma), **B** (Agentes), **C** (Dados e avaliação). As tarefas detalhadas estão no [`checklist.md`](checklist.md).

### 2.1 Funcionalidades

| Área | O que entrega | Dono | Prioridade |
|---|---|---|---|
| **Plataforma** | Login, consentimento (LGPD), tela de conversa (foto, PDF, gravar e tocar áudio, botões de confirmar), lista de remédios | A | P0 |
| | Telas completas de cronograma e diário; PWA instalável com push agendado | A | P1 |
| **API e dados do app** | Contas, banco (perfil do idoso, lista versionada, doses, diário), arquivos, geração do PDF do resumo, deploy com HTTPS | A | P0 |
| **Entrada e leitura** | Foto da receita física (impressa e à mão), foto de caixa e PDF → lista estruturada com confiança; confirmação obrigatória; fluxo de confiança baixa (D19) | B | P0 |
| **Normalização** | Nome comercial → princípio ativo e concentração para os ~50 remédios (Anvisa/CMED) | C | P0 |
| **Farmacovigilância mínima** | Mesmo princípio ativo em nomes diferentes + tabela curada à mão para ~15–20 remédios da demo (interações, duplicidade de classe, CBMPI), com fonte | C | P0 |
| **Rotina** | Cronograma; lembrete com texto e áudio disparado na hora (demo); confirmação de dose | A + B (voz) | P0 |
| **Diário e escalonamento** | Áudio → sintoma estruturado → regras de gravidade → "ligue 192" ou resumo em PDF para consulta / farmacêutico | B + C (regras) | P0 |
| **Auditor e guardrails** | Bloqueio de frases proibidas, de remédio fora da lista e de fato clínico sem fonte | B | P0 |
| **Conversa** | Orquestrador com estado e roteamento entre os agentes | B | P0 |

### 2.2 Avaliação (harness)

| Conjunto | Dono | Prioridade |
|---|---|---|
| Executor + relatório de métricas | C | P0 |
| 50 fotos de caixas | C (fotos: todos) | P0 |
| Fotos de receitas físicas, impressas e à mão (quantidade e metas na D19) | C (receitas: todos) | P0 |
| 30 pares de interação e duplicidade, dentro dos remédios da tabela curada | C | P0 |
| 20 tentativas de arrancar dose (guardrail) | C | P0 |
| 10 PDFs de receita digital | C | P1 |
| 20 relatos de sintoma com a conduta certa | C | P1 |

### 2.3 Entregáveis e validação

| O que | Dono | Prioridade |
|---|---|---|
| GitHub com protótipo, BMC, pitch e documentação do fluxo | Todos | P0 |
| Pitch de 3 min com demo ao vivo (foto → lista → alerta → áudio → escalonamento), ensaiado | Todos | P0 |
| Vídeo de backup da demo | Todos | P0 |
| 5 a 10 entrevistas (cuidadoras, farmacêuticos, enfermeiras de ESF); checar o critério de giro | em aberto (D12) | P0 |
| Checar o nome (INPI, registro.br, Instagram, lojas) | em aberto (D12) | P1 |
| Checar o campo de princípio ativo no dicionário de dados da Anvisa | C | P0 |

---

## 3. Final — o que fica para depois do regional

Os donos são sugeridos pela frente de cada um e serão confirmados depois do regional.

### 3.1 Produto

| Funcionalidade | Dono sugerido | Origem |
|---|---|---|
| **Painel do farmacêutico ou da enfermeira**, com fila de casos | A | Plano §4.7 |
| **Código de barras da caixa** como entrada | B | Plano §4.7 |
| **Aviso de estoque e renovação de receita** | A + B | Plano §4.7 (ver D16.2: pode subir para o regional) |
| **Tendências no diário** ("3 dias de tontura") | B | Plano §4.7 |
| **Efeito adverso × sintoma relatado** ("pode ter relação com X") | B + C | Plano §4.7 |
| **Base de interações completa e licenciada** (DDInter, DrugBank ou base própria curada por farmacêutico) | C | Mudança de escopo de 22/10 |
| **Conversão de nomes PT → internacional em escala** | C | Mudança de escopo de 22/10 |
| **CBMPI completo + critérios de Beers** | C | Mudança de escopo de 22/10 |
| **RAG em bulas** (Bulário Eletrônico da Anvisa) | C | Mudança de escopo de 22/10 |
| Correções apontadas pela banca e pelos mentores do regional (v1.1) | Todos | Plano, Parte 7 |
| Itens P1 do regional que não ficarem prontos | Dono original | Regra 4 (D16) |

### 3.2 Validação e negócio

| Tarefa | Quando (plano) | Dono |
|---|---|---|
| Recrutar 5 a 10 famílias e assinar termo de consentimento (LGPD) | 25/10–31/10 | em aberto |
| **Piloto de 2 semanas**: medir uso diário, doses confirmadas, alertas e o que as cuidadoras dizem | 02/11–15/11 | Todos |
| Conversas com 2–3 farmácias regionais e 1–2 operadoras/autogestões; **buscar carta de intenção** | 02/11–15/11 | em aberto |
| **Unit economics** com números reais: custo médio de internação de idoso na saúde suplementar; custo por idoso medido no piloto | 09/11–15/11 | em aberto |
| Levantar quanto das internações de idosos vem de erro de medicação em casa | até a final | em aberto |
| **Análise regulatória** (RDC 657/2022 e 751/2022), com parecer de especialista se possível | 09/11–15/11 | em aberto |
| **Licença comercial** da base de interações (DDInter / DrugBank) | até a final | C |
| Resposta para a banca sobre o pagador (operadora / farmácia) | até a final | em aberto |
| Nova frase de posicionamento no lugar de "pelo WhatsApp" (visão §4.2) | até a final | em aberto |

### 3.3 Entregáveis da final

| O que | Quando (plano) |
|---|---|
| 3º relatório quinzenal | 01/11 |
| 4º relatório quinzenal | 15/11 |
| Pitch de 5 min para investidores: problema → tração do piloto → modelo B2B2C → unit economics → mercado → time → pedido | 16/11–22/11 |
| Mentoria dos finalistas (levar as 3 perguntas mais difíceis esperadas) | semana de 23/11 |
| Ensaio com banca simulada (Anvisa, quem paga, por que a operadora não faz sozinha) | 24/11–27/11 |
| **Entrega e pitch na final** | 28/11, até 17h30 |

---

## 4. Decisões pendentes que podem mexer neste corte

| Decisão | Efeito possível |
|---|---|
| **D11** — trilha (24/10 ou 31/10) | Se for 24/10, mais itens P0 podem virar P1, ou ir para a final |
| **D16** — tabela P0/P1 e regra 4 | Define o que entra se der tempo e o que acontece com o que sobrar |
| **D16.2** — aviso de estoque | Regional ou final |
| **D15.2** — até onde vai o alerta clínico | Se o MVP só organizar e escalar, a farmacovigilância mínima também vai para a final |
| **D19** — receitas físicas | Tamanho e metas dos conjuntos de avaliação de receitas |
