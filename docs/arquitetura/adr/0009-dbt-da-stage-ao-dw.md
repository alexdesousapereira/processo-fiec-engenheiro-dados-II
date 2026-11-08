# ADR 0009: dbt para carregar o DW, com Python na extração e no tratamento

**Status:** aceita, 2026-11-07. O local de execução do dbt foi substituído pelo [ADR 0012](0012-dbt-em-conteiner-e-socket-docker.md), e os nomes, pelo [ADR 0013](0013-nomes-do-warehouse.md). A escolha do dbt e da estratégia `merge` continua valendo.

## Contexto

O DW precisa de upsert, chaves, view analítica e testes de dados. A prova exige extração em Python (I1) e
tratamento em Python e/ou PySpark (T1). O dbt não atende a nenhum requisito diretamente: é uma escolha do projeto,
e esta é a justificativa escrita que a constituição exige.

O dbt só transforma dados que já estão no banco. Ele não chama APIs, então não pode fazer a extração.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| dbt da Stage ao DW; Python até a Stage | Atende a I1 e T1; SQL versionado, ordem de carga, contratos e testes prontos | Mais uma ferramenta, em ambiente Python separado |
| dbt em todo o tratamento | Mais SQL e menos Python | Tratamento fora de Python contraria o T1 ao pé da letra |
| SQL escrito à mão, chamado pelo Airflow | Nenhuma dependência nova | Ordem, testes e criação de tabelas ficam por conta do projeto |

## Decisão

Python extrai, pandas trata e recarrega a Stage. O dbt carrega o DW com modelos incrementais `merge`, cria a view e
executa os testes de dados. O Airflow chama o dbt pela linha de comando, nas tarefas `carregar_dw` e `testar_dados`.

## Consequências

- O dbt fica em um ambiente virtual próprio na imagem, para não conflitar com as dependências do Airflow.
- A estratégia é `merge`, e não `delete+insert`: apagar uma linha de dimensão referenciada violaria a chave estrangeira.
- Cada tabela é carregada na sua própria transação, com as dimensões antes do fato. Se o fato falhar, ele continua
  como estava, os meses seguem pendentes e a próxima execução refaz a carga.
- `dbt run --full-refresh` não deve ser usado: a Stage só tem os meses alterados, e o DW perderia os demais. Para
  refazer o DW, use o modo `reprocessar` da DAG.
- Regras de domínio ficam em dois lugares: linhas inválidas são barradas no pandas, e os testes do dbt verificam o
  resultado final.
