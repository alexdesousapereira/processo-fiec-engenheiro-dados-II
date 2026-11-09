"""DAG do pipeline da PIM-PF (requisito O1). Aqui só a ordem; a lógica está na API e no dbt.

Dois grupos de tarefas semelhantes:
- ingestao: as três tarefas que conversam com a API.
- dbt: valida o lote na Stage e, pelo Cosmos, roda cada modelo do warehouse seguido dos seus testes.
O dbt roda sempre no contêiner pim-pf-dbt (ADR 0012); o Cosmos só desenha as tarefas a partir do manifest.json.
"""
import os
from datetime import datetime, timedelta

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.standard.sensors.python import PythonSensor
from airflow.sdk import DAG, Param, TaskGroup
from cosmos import DbtTaskGroup, ExecutionConfig, ExecutionMode, LoadMode, ProjectConfig, RenderConfig, TestBehavior

from pim_pf import cliente_api

# Igual para todo contêiner do dbt, seja do DockerOperator, seja do Cosmos.
DOCKER_DBT = {
    "image": "pim-pf-dbt:1.0",
    "docker_url": "unix://var/run/docker.sock",
    "network_mode": "pim_pf_rede",
    # A pasta temporária padrão usa um caminho do host, que varia no Docker Desktop.
    "mount_tmp_dir": False,
    "auto_remove": "success",
    "environment": {
        "PIM_DB_HOST": os.environ["PIM_DB_HOST"],
        "PIM_DB_PORTA": os.environ["PIM_DB_PORTA"],
        "PIM_DB_NOME": os.environ["PIM_DB_NOME"],
        "PIM_DB_USUARIO": os.environ["PIM_DB_USUARIO"],
    },
    # Fora dos logs e da interface do Airflow.
    "private_environment": {"PIM_DB_SENHA": os.environ["PIM_DB_SENHA"]},
}


def _verificar(params: dict) -> bool:
    """Outros modos são pedidos manuais: seguem mesmo sem novidade na fonte."""
    return params["modo"] != "auto" or cliente_api.ha_novidade()


def _solicitar(params: dict) -> str:
    return cliente_api.solicitar(params["modo"], params["inicio"], params["fim"])


with DAG(
    dag_id="pim_pf_8888",
    description="PIM-PF: da API do IBGE ao warehouse no PostgreSQL",
    # Diário porque a verificação é barata e a data de publicação da fonte pode variar.
    schedule="@daily",
    start_date=datetime(2026, 11, 1),
    # A fonte não é consultada por data de execução, então não há o que recuperar.
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
        "retry_exponential_backoff": True,
    },
    params={
        "modo": Param(
            "auto",
            enum=["auto", "completa", "reprocessar"],
            description="auto: só o que mudou. completa: baixa tudo de novo. reprocessar: refaz sem chamar a fonte.",
        ),
        "inicio": Param("", type="string", description="Primeiro mês, como 2025-01. Vazio: a regra do modo."),
        "fim": Param("", type="string", description="Último mês, como 2025-03. Vazio: a regra do modo."),
    },
    tags=["pim-pf", "ibge"],
) as dag:
    with TaskGroup("ingestao", tooltip="Conversa com a API: verifica, pede e acompanha a extração") as ingestao:
        verificar_novidades = ShortCircuitOperator(task_id="verificar_novidades", python_callable=_verificar)
        solicitar_extracao = PythonOperator(task_id="solicitar_extracao", python_callable=_solicitar)
        # Sem novas tentativas: quando a extração falha, o erro já é definitivo. Os meses seguem
        # pendentes, e a próxima execução os retoma. O modo reschedule não ocupa vaga durante a espera.
        aguardar_extracao = PythonSensor(
            task_id="aguardar_extracao",
            python_callable=cliente_api.execucao_concluida,
            op_kwargs={"execucao_id": "{{ ti.xcom_pull(task_ids='ingestao.solicitar_extracao') }}"},
            mode="reschedule",
            poke_interval=30,
            timeout=3600,
            retries=0,
        )
        verificar_novidades >> solicitar_extracao >> aguardar_extracao

    with TaskGroup("dbt", tooltip="Valida o lote na Stage e publica o warehouse, modelo a modelo") as dbt:
        # Antes de publicar: se o lote reprovar, o warehouse não muda e os meses seguem pendentes.
        # Repetir não adianta: uma reprovação aponta um problema nos dados.
        validar_lote = DockerOperator(
            task_id="validar_lote", command="dbt test --select source:stage", retries=0, **DOCKER_DBT
        )
        # Uma tarefa por modelo, seguida dos testes dele. A ordem vem das dependências do manifest:
        # dimensões antes do fato, e o fato antes da tabela analítica e das views.
        warehouse = DbtTaskGroup(
            group_id="warehouse",
            project_config=ProjectConfig(manifest_path="/opt/airflow/dbt/manifest.json", project_name="pim_pf"),
            render_config=RenderConfig(
                load_method=LoadMode.DBT_MANIFEST,
                select=["path:models/warehouse"],
                # O Airflow mostra só as tabelas: um run e um test por modelo. Os testes de chave estrangeira
                # não viram tarefas próprias; rodam dentro do test do fato, que vem depois das dimensões.
                test_behavior=TestBehavior.AFTER_EACH,
            ),
            execution_config=ExecutionConfig(execution_mode=ExecutionMode.DOCKER, dbt_project_path="/app/dbt"),
            # Depois de publicar, um teste reprovado deixa a execução como falha, para corrigir e reprocessar.
            operator_args=dict(DOCKER_DBT),
            default_args={"retries": 0},
        )
        validar_lote >> warehouse

    ingestao >> dbt
