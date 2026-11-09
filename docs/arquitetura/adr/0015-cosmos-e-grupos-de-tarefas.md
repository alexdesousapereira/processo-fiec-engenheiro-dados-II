# ADR 0015: Cosmos para ver cada etapa do dbt no Airflow, e grupos de tarefas na DAG

**Status:** aceita, 2026-11-08. Complementa o [ADR 0012](0012-dbt-em-conteiner-e-socket-docker.md), que continua valendo.

## Contexto

O candidato pediu para ver cada etapa do dbt dentro do Airflow e para agrupar as tarefas semelhantes da DAG. Antes, o dbt
rodava em duas tarefas únicas (`carregar_warehouse`, com `dbt run`, e `testar_dados`, com `dbt test`). Quando algo falhava,
era preciso abrir o log para saber qual modelo ou teste tinha falhado, e reexecutar significava rodar tudo de novo.

O [Cosmos](https://github.com/astronomer/astronomer-cosmos) lê o projeto dbt e cria uma tarefa por modelo e por teste,
com as dependências do próprio projeto.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Cosmos em modo Docker, lendo o `manifest.json` | Mantém o dbt no contêiner próprio (ADR 0012); a imagem do Airflow ganha só 3 pacotes | O `manifest.json` precisa ser gerado no build da imagem do Airflow; um contêiner por tarefa deixa a carga mais lenta |
| Cosmos em modo virtualenv, com o dbt na imagem do Airflow | Mais simples e sem o socket do Docker | Substituiria o ADR 0012 e misturaria as dependências do dbt com as do Airflow |
| Manter `dbt run` e `dbt test` em duas tarefas | Nada muda | Não mostra cada etapa, que foi o pedido |

## Decisão

Escolhida pelo candidato: **Cosmos em modo Docker**.

- `DbtTaskGroup` com `ExecutionMode.DOCKER`: cada tarefa é um contêiner `pim-pf-dbt:1.0`, com a mesma rede, as mesmas
  variáveis e a senha em `private_environment`.
- `LoadMode.DBT_MANIFEST`: a imagem do Airflow tem uma etapa de build que roda `dbt parse` e copia só o `manifest.json`.
  O dbt não é instalado na imagem final do Airflow.
- `TestBehavior.AFTER_EACH`: cada modelo tem uma tarefa `run` e, em seguida, uma `test`. Um modelo com teste reprovado
  não deixa os modelos seguintes rodarem.
- O grupo mostra só as tabelas, a pedido do candidato. Os testes de chave estrangeira do fato não viram tarefas
  próprias: rodam dentro da tarefa `test` dos modelos que eles leem, e a do fato vem depois das dimensões.
- `validar_lote` continua como uma tarefa só, porque os testes da Stage precisam rodar antes de qualquer modelo.
- Grupos de tarefas: `ingestao` (as três tarefas que falam com a API) e `dbt` (`validar_lote` e o grupo `warehouse`).
- Versão 1.15.1, de 04/08/2026. A 1.16.0 saiu em 03/11/2026, há poucos dias, e foi descartada por isso.

## Consequências

- A interface do Airflow mostra cada modelo e cada teste, e é possível reexecutar só a tarefa que falhou.
- A carga no warehouse ficou mais lenta: cerca de 15 contêineres, um por tarefa, em vez de dois. Medido: cerca de 1,5 min
  no grupo `dbt` para reprocessar um mês.
- O grupo `dbt` não repete tarefas que falharam. Antes, só `carregar_warehouse` repetia; agora um erro de modelo exige
  reexecutar a tarefa pela interface.
- Mudou o projeto dbt: o build da imagem do Airflow precisa ser refeito para o `manifest.json` acompanhar.
- O teste "soma das diferenças é zero" passou a ler a tabela analítica. Assim ela ganha a sua tarefa de teste, que roda
  também o teste de unidade da média; sem nenhum teste de dados, o Cosmos não criaria essa tarefa.
- O socket do Docker continua só no scheduler, como no ADR 0012.
