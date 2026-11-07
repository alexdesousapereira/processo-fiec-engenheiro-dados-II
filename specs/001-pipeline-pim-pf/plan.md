# Implementation Plan: Pipeline da PIM-PF, da extração ao painel analítico

**Branch**: `docs/constituicao-1.1.0` (branch atual; o script sugere `001-pipeline-pim-pf`, que não foi criada) | **Date**: 2026-11-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-pipeline-pim-pf/spec.md`

## Summary

O pipeline atual roda inteiro dentro da imagem do Airflow. Este plano o reorganiza no desenho do candidato: a ingestão passa
para um contêiner próprio, atrás de uma API FastAPI; o dbt passa para outro contêiner, acionado por `DockerOperator`; o modelo
muda para o schema `warehouse`, com `dim_*` e `fat_*`; e um painel em PBIP consome esse modelo.

O código de extração, tratamento e modelagem é reaproveitado. As novidades são a API, o registro de execuções, a extração por
tabela, a janela de períodos, o novo Compose e o painel. Os motivos estão em [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12 nos três contêineres; SQL no dbt e no PostgreSQL 16.10

**Primary Dependencies**:

| Contêiner | Base | Dependências |
|---|---|---|
| `ingestao` | `python:3.12.13-slim-bookworm` | FastAPI 0.162.2, Uvicorn 0.54.0, Pydantic 2.14.3, requests 2.34.2, pandas 3.1.0, psycopg2-binary 2.9.13; testes: pytest 9.2.0, httpx 0.28.1 |
| `dbt` | `python:3.12.13-slim-bookworm` | dbt-core 1.11.17, dbt-postgres 1.11.0 |
| Airflow | `apache/airflow:3.4.0-python3.12` | Já traz os providers `docker` 4.6.1 e `standard` 1.21.0, e `requests` 2.34.2 (medido) |

**Storage**: PostgreSQL (schemas `stage`, `warehouse` e `controle`) e arquivos brutos JSON gzip em volume nomeado

**Testing**: pytest nos contêineres, com a fonte simulada; `TestClient` na API; testes do dbt nos dados; validação manual do painel

**Target Platform**: Docker Compose, testado no Docker Desktop 27.3.1 com Windows 11; painel no Power BI Desktop para Windows

**Project Type**: pipeline de dados com serviço web de ingestão e painel analítico

**Performance Goals**: confirmação do pedido em até 5 s (SC-007); carga completa de 297 meses em cerca de 3 min (medido)

**Constraints**: pico de memória do pandas de cerca de 343 MB (medido); um mês por requisição, para permitir o hash por mês

**Scale/Scope**: 914.166 linhas, com 3.078 novas por mês; 4 endpoints de extração; 5 tabelas e 2 views analíticas; 2 telas

Não há itens em aberto: Q1 e Q2 da spec foram respondidas, e as dúvidas técnicas foram medidas em [research.md](research.md).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Regra | Avaliação | Como é atendida |
|---|---|---|
| I. Prova como fonte | Passa, com justificativa | Requisitos citam IDs. API e painel não têm requisito direto; a spec os justifica, e a API terá o ADR 0011 |
| II. Decisão defensável | Passa | [research.md](research.md) traz alternativas; ADRs 0011 a 0013 entram nas tarefas |
| III. Dados medidos | Passa | Novas medições registradas em `docs/fonte-sidra-8888.md` |
| IV. Cargas idempotentes | Passa | Hash por mês, `merge`, arquivos brutos imutáveis e uma execução por vez |
| V. Ambiente reproduzível | Passa | Tudo em contêineres, com versões fixas; validação em clone limpo |
| Python, pandas e requests | Passa | Lógica em `src/`; regras explícitas de símbolos; `timeout`, novas tentativas e validação. Falta anotar o retorno em `banco.py` |
| FastAPI | Passa | Pydantic, `202`, `409`, `/health`, rotas finas e `TestClient`. Não há listas, então não há paginação |
| Docker | Exceção documentada | Socket só no `airflow-scheduler`, com ADR 0012 (ver Complexity Tracking) |
| Airflow | Passa | DAG só com ordem e parâmetros; XCom só com o identificador da execução |
| SQL e PostgreSQL | Passa | Parâmetros, `COPY`, chaves no banco, usuário somente leitura; `EXPLAIN` da view entra nas tarefas |

**Resultado**: aprovado antes da pesquisa e reavaliado após o design, sem novas violações.

## Project Structure

### Documentation (this feature)

```text
specs/001-pipeline-pim-pf/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api-ingestao.md
│   ├── dag-airflow.md
│   └── painel.md
├── checklists/requirements.md
└── tasks.md             # gerado por /speckit-tasks
```

### Source Code (repository root)

```text
docker/
├── ingestao/Dockerfile      # novo: API e extração
├── dbt/Dockerfile           # novo: dbt e o projeto
└── airflow/Dockerfile       # substitui o Dockerfile da raiz
requirements/
├── ingestao.txt             # novo: versões exatas
└── testes.txt               # novo
docker-compose.yml           # refeito: serviços ingestao e dbt, porta 8000, rede nomeada
.env.example                 # novas variáveis
src/pim_pf/
├── fonte.py                 # ganha metadados e localidades
├── extracao.py              # janela de períodos e extração por tabela
├── tratamento.py            # tratamento das três dimensões
├── carga.py                 # Stage por tabela; sai a chamada ao dbt
├── banco.py                 # anotação de retorno
├── execucoes.py             # novo: registro e situação das execuções
├── api.py                   # novo: rotas e modelos Pydantic
└── cliente_api.py           # novo: chamadas da DAG à API, testáveis sem Airflow
dags/pim_pf_8888.py          # refeita: 6 tarefas
dbt/
├── models/warehouse/        # substitui models/dw: dim_*, fat_* e views
├── models/stage/sources.yml
└── tests/                   # testes atualizados, mais o top 3
sql/init/01-estrutura.sh     # schemas, Stage com metadados e execuções
sql/top3_por_uf_mes.sql      # passa a ler o warehouse
tests/
├── test_extracao.py, test_tratamento.py   # ampliados
├── test_janela_periodos.py  # novo
├── test_api.py              # novo
└── test_cliente_api.py      # novo
powerbi/                     # novo: PBIP, tema versionado e fundos SVG
docs/arquitetura/            # ADRs 0011 a 0013, ARQUITETURA.md e diagrama
```

**Structure Decision**: mantém um único projeto Python em `src/pim_pf`, para reaproveitar o código e os testes. Cada contêiner recebe
só o que usa: a imagem do Airflow leva a DAG e `cliente_api.py`, sem pandas nem dbt.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Socket do Docker montado no `airflow-scheduler` | O candidato definiu dbt em contêiner próprio, acionado por `DockerOperator` | dbt na imagem do Airflow é mais simples e seguro, mas contraria essa decisão. Fica registrado como alternativa no ADR 0012 |
| API sem exigência na prova | Decisão do candidato: ponto único para acionar a ingestão e ver o status | Chamar a extração direto na DAG exigiria pandas na imagem do Airflow e dispensaria o contrato pedido |
| Schema `controle`, além dos dois pedidos | O hash por mês e as execuções precisam sobreviver às recargas da Stage, e o Power BI não deve enxergá-los | Guardar na `stage` misturaria tabelas descartáveis e permanentes |
