# ADR 0010: DW em fato e dimensão, com dcalendario

**Status:** aceita, 2026-11-07. Substitui a parte do [ADR 0008](0008-stage-e-dw-estilo-oltp.md) que definia o DW como
normalizado, estilo OLTP. Os nomes de schema e tabelas foram substituídos pelo [ADR 0013](0013-nomes-do-warehouse.md); o modelo em fato e dimensão continua valendo.

## Contexto

O DW tinha o formato de um modelo normalizado, sem uma dimensão de tempo: o mês era só o código `periodo`, e o filtro de
2025 dependia de uma faixa de códigos. Os dados serão consumidos por analistas, inclusive no Power BI, em que fato e
dimensão é o formato mais natural.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Fato e dimensões, com chaves da fonte | Modelo fácil de consultar; chaves já estáveis; poucas mudanças na carga | Só preserva o valor atual dos nomes, sem histórico de mudanças |
| Fato e dimensões, com chaves substitutas | Permite guardar o histórico de cada dimensão | Mais uma etapa na carga, sem necessidade medida |
| Manter o modelo anterior, sem calendário | Nenhuma mudança | Ano, trimestre e nome do mês precisariam ser recalculados em cada consulta |

## Decisão

Publicar no schema `dw` as dimensões `dterritorio`, `dvariavel`, `dcategoria` e `dcalendario`, e o fato
`fproducao_fisica`. O prefixo `d` indica dimensão, e o `f`, fato. As chaves continuam sendo os códigos do IBGE.

`dcalendario` tem uma linha por mês, porque esse é o grão da fonte. Sua chave é `periodo` (AAAAMM), o mesmo código do
fato, com chave estrangeira entre os dois. O dbt gera a tabela a partir do primeiro e do último ano da Stage, sempre
com anos completos, e o `merge` acumula os anos entre as cargas.

A view usa o calendário para filtrar 2025 (`ano = 2025`), mantendo as mesmas colunas de antes. A Stage não mudou: ela é
a área de carga, e seus nomes não fazem parte do modelo de consumo.

## Consequências

- O fato continua com todas as variáveis e territórios (I2), e cada linha traz a medida de uma variável. Quem consulta
  o fato precisa filtrar a variável, como a view já faz.
- O calendário tem meses ainda sem dados, como 202612, para manter os anos completos.
- Um calendário mensal não atende às funções de data do Power BI que exigem uma tabela com todos os dias. Se forem
  necessárias, será preciso criar uma tabela diária no próprio Power BI, ligada pelo código do mês.
- As dimensões guardam só o valor mais recente de cada código. Hoje a fonte não exige histórico.
