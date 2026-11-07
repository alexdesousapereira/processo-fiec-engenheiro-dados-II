# ADR 0006: Camada Landing antes da Bronze

**Status:** adiada para a [proposta futura](../proposta-futura/PROPOSTA-FUTURA.md), conforme o ADR 0007. Na arquitetura atual, os arquivos brutos cumprem o papel de preservar o original.

## Contexto

Até aqui, a Bronze guardava o JSON da API e também era a primeira camada lida pelo tratamento. Esse papel
único misturava duas responsabilidades: preservar o que a fonte enviou e deixar os dados consultáveis.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Só Bronze, em JSON | Menos etapas e menos armazenamento | Comparar versões exige abrir e interpretar arquivos JSON |
| Só Bronze, em Parquet | Consultável desde o início | Perde o arquivo original da fonte |
| Landing em JSON e Bronze em Parquet | Preserva o original e permite consultá-lo | Uma camada e uma tarefa a mais; dados duplicados entre as camadas |

## Decisão

A Landing guarda o JSON gzip como a fonte entregou, de forma imutável e versionada. A Bronze lê esses
arquivos com PySpark e os grava em Parquet com colunas como texto, colunas técnicas e todas as versões,
sem nenhuma regra de negócio. As regras de tratamento continuam começando na Silver.

## Consequências

- A DAG passa a ter 8 tarefas, com `carregar_bronze` entre `validar_landing` e `transformar_silver`.
- A Bronze pode ser apagada e reconstruída a partir da Landing a qualquer momento.
- Comparar versões de um mês vira uma consulta simples, útil para medir revisões do IBGE.
- O volume atual não exige essa separação. A justificativa é organização e rastreabilidade, não desempenho.
