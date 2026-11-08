# ADR 0007: Modelo relacional agora, lakehouse como proposta futura

**Status:** proposta, 2026-11-06. O modelo do DW passou a ser fato e dimensão no
[ADR 0010](0010-dw-em-fato-e-dimensao.md); a escolha por um banco relacional agora e pelo lakehouse depois continua valendo.
A tecnologia da proposta futura (MinIO, Airflow e Docker Compose) foi substituída por Databricks, Data Factory e ADLS no
[ADR 0014](0014-proposta-futura-na-azure.md).

## Contexto

O cenário atual tem uma fonte e cerca de 914 mil linhas. A versão anterior da arquitetura usava MinIO e quatro
camadas (Landing, Bronze, Silver e Gold), o que é mais do que esse cenário pede.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Modelo relacional normalizado com view | Integridade por chaves, upsert simples, menos serviços | Menos preparado para muitas fontes; avaliador pode esperar modelo dimensional |
| Lakehouse em camadas com star schema | Separação clara e preparo para crescer | Mais serviços, tarefas e código para defender, sem necessidade atual |
| Só o banco, sem guardar arquivos | Mínimo possível | Reprocessar exige a API; menos resposta aos itens de formato e particionamento da prova |

## Decisão

Usar um modelo relacional normalizado no PostgreSQL, com a estrutura analítica em uma view, e manter os arquivos
brutos em volume local. O lakehouse fica documentado em [proposta-futura](../proposta-futura/PROPOSTA-FUTURA.md),
com os critérios para migrar. A divisão do banco em Stage e DW está no
[ADR 0008](0008-stage-e-dw-estilo-oltp.md).

## Consequências

- Menos componentes para rodar e para explicar.
- A view recalcula a média a cada consulta, o que é aceitável com 2.004 linhas em 2025.
- "OLTP" descreve a modelagem normalizada e as garantias transacionais. A carga de trabalho continua sendo em
  lote e analítica, e é preciso deixar isso claro na entrevista.
- A migração é facilitada porque os arquivos brutos já estão organizados por mês e versão.
