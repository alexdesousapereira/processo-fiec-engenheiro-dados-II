# ADR 0002: Banco da camada analítica

**Status:** proposta, 2026-11-06

## Contexto

A prova pede um formato consultável via SQL e cita banco relacional como exemplo. O Airflow também
precisa de um banco para seus metadados.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| PostgreSQL | Um contêiner atende o Airflow e o modelo relacional; leve; imagem multiplataforma | Pode não ser o banco final de produção |
| SQL Server | Comum em data warehouses corporativos | Pede mais memória, um segundo banco para o Airflow e aceite de licença; imagem sem suporte oficial a ARM |
| DuckDB | Nenhum serviço a mais | Fraco para acesso concorrente; menos parecido com um banco servidor |

## Decisão

PostgreSQL, com bancos separados para Airflow e dados.

## Consequências

- Menos contêineres, menos memória e menos falhas para quem avalia.
- Migrar exige trocar o driver JDBC e ajustar o DDL. A consulta do top 3 muda pouco; na view, a cláusula
  `WINDOW` teria de ser reescrita em bancos sem suporte a ela.
- Um único serviço concentra metadados e dados, o que seria separado em produção.
