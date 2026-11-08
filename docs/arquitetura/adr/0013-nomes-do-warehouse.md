# ADR 0013: schema warehouse, com prefixos dim_ e fat_

**Status:** aceita, 2026-11-07. Substitui os nomes do [ADR 0010](0010-dw-em-fato-e-dimensao.md). O restante daquela decisão continua valendo.

## Contexto

O ADR 0010 usava o schema `dw` e os prefixos `d` e `f`. O candidato definiu novos nomes ao revisar o desenho da solução.

## Decisão

| Antes | Agora |
|---|---|
| Schema `dw` | Schema `warehouse` |
| `dterritorio` | `dim_territorio` |
| `dvariavel` | `dim_variaveis` |
| `dcategoria` | `dim_categorias` |
| `dcalendario` | `dim_calendario` |
| `fproducao_fisica` | `fat_producao_fisica` |
| `stage.variavel` | `stage.variaveis` |

Toda tabela da Stage e do warehouse passa a ter `path_origem` e `data_carga`. Elas substituem `origem_arquivo` e `ingestao_em` do fato; a data de ingestão continua no manifesto e em `controle.carga_periodo`.

`data_carga` é definida na carga da Stage e propagada sem mudança, o que liga as duas camadas pelo mesmo instante. Em `dim_calendario`, que não vem da fonte, `path_origem` é `gerado:dbt`, e `data_carga` é o momento da execução.

Além dos dois schemas pedidos, `controle` continua existindo. O hash de cada mês e as execuções precisam sobreviver às recargas da Stage, e o usuário do Power BI não deve enxergá-los.

## Consequências

- Os novos prefixos deixam a função de cada tabela evidente a quem não conhece o projeto.
- Mudar os nomes exigiu recriar os volumes e refazer a carga, o que leva cerca de 4 minutos.
- Um reprocessamento manual atualiza `data_carga`. Isso é esperado: a comparação de idempotência considera os dados de negócio.
