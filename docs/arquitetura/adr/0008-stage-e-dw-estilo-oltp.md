# ADR 0008: Stage e DW estilo OLTP no PostgreSQL

**Status:** proposta, 2026-11-06. A divisão em Stage e DW continua valendo; a modelagem normalizada do DW foi
substituída por fato e dimensão no [ADR 0010](0010-dw-em-fato-e-dimensao.md).

## Contexto

O modelo relacional já previa tabelas temporárias de carga, mas sem uma camada definida. A arquitetura precisa
deixar claro onde os dados entram e onde ficam prontos para consulta.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Stage e DW normalizado (estilo OLTP) | Separa carga e publicação; integridade por chaves; DW intacto se a carga falhar | Uma cópia a mais dos dados alterados |
| Stage e DW em star schema | Modelo dimensional clássico | Mais tabelas e transformação sem ganho para uma fonte e uma pergunta analítica |
| pandas gravando direto nas tabelas finais | Menos tabelas | Falha no meio da carga é mais difícil de isolar e investigar |

## Decisão

Dividir o banco em dois schemas. O pandas recarrega o schema `stage` com `COPY`, em tabelas sem chaves. O dbt faz o
upsert no schema `dw`, normalizado, com chaves primárias e estrangeiras e a view analítica
([ADR 0009](0009-dbt-da-stage-ao-dw.md)).

## Consequências

- Os consumidores não veem o resultado de um tratamento que falhou.
- A Stage guarda a última carga até a próxima, o que ajuda a investigar falhas.
- O controle de carga fica no schema `controle`, pois precisa sobreviver entre as cargas.
- "Estilo OLTP" descreve a modelagem e as garantias transacionais. A carga de trabalho continua em lote e
  analítica, e isso precisa ficar claro na entrevista.
- O star schema continua na [proposta futura](../proposta-futura/PROPOSTA-FUTURA.md).
