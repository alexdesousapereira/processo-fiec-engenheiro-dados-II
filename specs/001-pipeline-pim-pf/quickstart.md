# Quickstart: validação do pipeline

Roteiro para provar, de ponta a ponta, que a feature funciona depois da implementação. Contratos: [API](contracts/api-ingestao.md),
[DAG](contracts/dag-airflow.md), [painel](contracts/painel.md). Modelo: [data-model.md](data-model.md).

## Pré-requisitos

- Docker Desktop em execução e acesso à internet para as APIs do IBGE.
- Power BI Desktop, só para o cenário 7.
- Portas 5432, 8000 e 8080 livres, ou outras definidas no `.env`.

## 1. Subir do zero (SC-001)

```powershell
Copy-Item .env.example .env
docker compose down -v      # apaga os dados do ambiente; só em um ambiente que possa ser refeito
docker compose up -d --build
docker compose ps
```

**Esperado**: `postgres`, `ingestao` e `airflow-apiserver` saudáveis; `airflow-init` e `dbt` encerrados com código 0.

## 2. Testes automatizados

```powershell
docker compose run --rm ingestao pytest
docker compose exec airflow-scheduler airflow dags list-import-errors
```

**Esperado**: todos os testes aprovados, sem erros de importação.

## 3. Carga completa pelo Airflow (US1, US3, US4, SC-002)

Em `http://localhost:8080`, dispare `pim_pf_8888`.

```powershell
docker compose exec postgres psql -U pim -d pim -c "SELECT count(*) FROM warehouse.fat_producao_fisica"
docker compose exec postgres psql -U pim -d pim -c "SELECT count(*) FROM warehouse.fato_producao_fisica_industrial_2025"
docker compose exec postgres psql -U pim -d pim -c "SELECT count(*) FROM warehouse.vw_top3_transformacao_2025"
```

**Esperado**: as 18 tarefas verdes (com o Cosmos, cada modelo e teste do dbt é uma tarefa) e, na medição de referência, 914.166, 2.004 e 612 linhas. Revisões da fonte podem mudar o total: o
fato deve ter 3.078 linhas por mês.

## 4. Resultado analítico (SC-005)

```powershell
docker compose exec postgres psql -U pim -d pim -f /sql/top3_por_uf_mes.sql
```

**Esperado**: no Ceará, em 202501, média 101,58012 e top 3 com 3.13 (145,03), 3.24 (136,56) e 3.11 (120,05).

## 5. API (US2, SC-007)

```powershell
curl.exe -i http://localhost:8000/health
curl.exe -i -X POST http://localhost:8000/extracoes/producao-fisica -H "Content-Type: application/json" -d '{\"inicio\":\"2025-03\",\"fim\":\"2025-01\"}'
curl.exe -i -X POST http://localhost:8000/extracoes/variaveis -H "Content-Type: application/json" -d '{}'
curl.exe http://localhost:8000/execucoes/<execucao_id>
```

**Esperado**: `200`; `422`; `202` em menos de 5 s; e `sucesso` no status, com 6 linhas em `variaveis`. Um segundo pedido durante
uma execução deve receber `409`.

## 6. Idempotência e reprocessamento (SC-003, SC-006, SC-008)

| Ação | Esperado |
|---|---|
| Disparar a DAG de novo, sem novidade | Encerra em `verificar_novidades`, sem alterar dados |
| Disparar com `modo=reprocessar`, `inicio=fim=2025-01` | Fato com o mesmo total, nenhuma pasta nova em `raw/` |
| Disparar com `modo=reprocessar` e rede bloqueada na `ingestao` | Termina com sucesso, sem acessar a fonte |
| Forçar falha em `dbt run` | Mês segue pendente, e o warehouse continua com os dados anteriores |
| Forçar um lote inválido na Stage, como um código de território duplicado | `validar_lote` falha, o warehouse não muda, e o mês segue pendente |
| Forçar um teste reprovado no resultado, como um ano incompleto em `dim_calendario` | `testar_dados` falha, e a execução fica como falha |

## 7. Painel (US5, SC-010)

1. Abra `powerbi/` no Power BI Desktop e atualize, informando o usuário `pim_leitura`.
2. Confira que há só as telas de capa e análise.
3. Filtre Ceará e janeiro de 2025 e compare com o cenário 4.
