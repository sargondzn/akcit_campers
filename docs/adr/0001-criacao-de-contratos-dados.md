# ADR 0001: criação de `contratos/dados.py` (tipos dos contratos C2, C3 e C4)

- **Status:** proposto. Aguarda o aceite de A (Beatriz) e B (Caio), conforme `specs/00-projeto/spec.md` §7.4.
- **Data:** 24/10/2026
- **Autor:** Roberto (Pessoa C, frente `dados`), com apoio do Claude Code.

## Contexto

A spec do projeto (`specs/00-projeto/spec.md` §2 e §5) prevê uma pasta `contratos/` com os tipos Pydantic de todos os contratos entre as frentes, e diz que ela só muda com o acordo dos três. Na data desta decisão a pasta não existia: o repositório só tinha specs, e nenhuma das três frentes tinha escrito código.

A frente `dados` (C) implementa as funções que o harness (B) chama:

| Contrato | Função | Tipos usados |
|---|---|---|
| C2 | `normalizar(nome)` | `ResultadoNormalizacao` |
| C3 | `checar_lista(itens)` | `ItemParaChecar`, `Alerta` |
| C4 | `detectar_alarme(texto)`, `avaliar_gravidade(sintoma)` | `Conduta`, `SintomaEstruturado` |

Sem esses tipos, o código de `dados/` não roda nem pode ser testado, e a frente `dados` é a que mais bloqueia as outras (caminho crítico do `atividades_roberto.md`). A spec §7.4 também diz que cada dono mantém stubs dos seus contratos para ninguém esperar ninguém.

O aceite da spec e dos contratos C1 a C7 por C foi registrado em 23/10/2026; os aceites de A e B continuam pendentes.

## Decisão

Criar `contratos/__init__.py` e `contratos/dados.py` com **somente** os cinco tipos que a frente `dados` usa, copiados da notação do §5 da spec, sem alterar nomes, campos nem tipos de campo:

- `ResultadoNormalizacao`
- `ItemParaChecar`
- `Alerta`
- `SintomaEstruturado`
- `Conduta`

Os demais tipos do §5 (`Anexo`, `ItemLido`, `MensagemEntrada`, `MensagemSaida`, `Resumo` e outros) **não foram criados**. Eles pertencem aos contratos de A e B, e criá-los sem os donos seria decidir por eles.

Escolhas de implementação, que não mudam o contrato:

- `BaseModel` do Pydantic v2, como a spec indica.
- Campos de lista ou dicionário têm valor padrão vazio (`principio_ativo=[]`, `candidatos=[]`, `sintomas=[]`, `sinais={}`) e `ResultadoNormalizacao.fonte` tem padrão `""`. Isso só facilita construir o objeto; quem preenche tudo continua válido.
- `Literal` para `tipo`, `gravidade`, `nivel`, `intensidade` e `conferencia`, com os mesmos valores da spec.

## Consequências

**Positivas**

- A frente `dados` pode ser desenvolvida e testada sozinha (238 testes passando em 24/10/2026), e B pode trocar os stubs por funções reais sem mudar assinatura.
- Os tipos ficam num lugar só e validados; B e A importam de `contratos` em vez de cada um redefinir.

**Riscos e pontos em aberto**

- A pasta `contratos/` foi criada por C antes do aceite de A e B. Se eles já tiverem uma versão própria, será preciso unificar e manter a versão da spec como referência.
- `Alerta.conferencia` só aceita `llm` ou `profissional`. O alerta `duplicidade_principio` vem de uma regra fixa, sem linha de tabela clínica, e hoje usa `llm`. Se o time achar enganoso, o contrato precisa de um terceiro valor (por exemplo `regra_fixa`), o que exige acordo dos três.
- `SintomaEstruturado` é produzido pelo harness (`harness.diario.estruturar`). As regras de gravidade dependem de os termos em `sintomas` e as chaves de `sinais` virem no vocabulário combinado em `dados/tabelas/regras_gravidade.csv`. Esse vocabulário não faz parte do tipo e precisa ser combinado com B.

## Como usar

```python
from contratos.dados import Alerta, Conduta, ItemParaChecar, ResultadoNormalizacao, SintomaEstruturado
# ou, equivalente:
from contratos import Alerta, Conduta
```

Quem usa hoje: `dados/normalizador.py` (`ResultadoNormalizacao`), `dados/farmacovigilante.py` (`ItemParaChecar`, `Alerta`), `dados/gravidade.py` (`Conduta`, `SintomaEstruturado`) e os testes em `dados/testes/`.

Regras de manutenção:

1. Para mudar um tipo, atualizar primeiro `specs/00-projeto/spec.md` §5, com o acordo dos três, e só depois `contratos/dados.py`.
2. Novos contratos de A e B entram em arquivos próprios dentro de `contratos/` (por exemplo `contratos/harness.py`), sem editar este.
3. O comando `python -m pytest dados/testes` deve continuar passando depois de qualquer mudança.

## Alternativas consideradas

- **Esperar B ou A criarem `contratos/`:** bloquearia a frente `dados`, que está no caminho crítico, e o regional é no mesmo dia.
- **Definir os tipos dentro de `dados/`:** B teria que importar de `dados` e os tipos divergiriam dos de A e B, o que a spec quis evitar ao criar a pasta compartilhada.
- **Criar todos os tipos do §5 de uma vez:** seria decidir pelos donos de A e B e arriscaria conflito com o que eles já escreveram.
