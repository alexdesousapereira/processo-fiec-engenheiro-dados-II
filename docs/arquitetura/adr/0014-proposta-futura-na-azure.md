# ADR 0014: proposta futura na Azure, com Databricks, Data Factory e ADLS

**Status:** proposta, 2026-11-07. Substitui a parte do [ADR 0007](0007-modelo-relacional-e-proposta-futura.md) que previa MinIO, Airflow e Docker Compose na proposta futura. A escolha por um banco relacional agora continua valendo.

## Contexto

A proposta futura previa um lakehouse em camadas com MinIO, PySpark local, Airflow e Docker Compose. O candidato decidiu que a evolução
seria na Azure: Databricks para processar, Azure Data Factory para orquestrar e o Azure Data Lake Storage Gen2 para guardar cada camada.

## Decisão

| Tema | Escolha | Alternativas consideradas |
|---|---|---|
| Consumo da Gold | Tabelas Delta no ADLS, consultadas pelo SQL Warehouse do Databricks | Copiar a Gold para PostgreSQL, Azure SQL ou Synapse: um banco e uma cópia a mais para manter |
| Extração | O código Python atual, em um job do Databricks | Atividade de cópia do Data Factory: exigiria refazer o hash por mês e a validação em outra etapa |
| API de ingestão | Sai: o Data Factory aciona o job direto | Manter a API no Azure Container Apps: mais um serviço para hospedar e proteger, sem função nova |
| Acesso | Unity Catalog, grupos do Entra ID e identidades gerenciadas | Chaves ou tokens SAS no Key Vault: segredos para guardar e trocar |

## Consequências

- O mesmo código de domínio (fonte, hash, símbolos e validações) segue em Python, e os testes atuais servem de aceite na migração.
- O Power BI só troca a fonte de dados: os nomes das tabelas e das colunas da Gold são os de hoje.
- O status de cada carga passa a ser visto no monitoramento do Data Factory e do Databricks, e não em uma tabela própria.
- O custo é o principal risco para o volume atual, e precisa ser medido antes de migrar. Os critérios de quando migrar estão na proposta.
- Esta decisão não muda nada na entrega da prova: ela registra a evolução prevista.
