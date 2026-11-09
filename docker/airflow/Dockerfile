# Etapa 1: gera o manifest.json do projeto dbt. O Cosmos lê esse arquivo para desenhar uma tarefa por modelo e
# por teste, sem instalar o dbt na imagem do Airflow. O dbt parse não conecta ao banco: as variáveis abaixo só
# existem para o profiles.yml ser lido.
FROM python:3.12.13-slim-bookworm AS manifesto
COPY requirements/dbt.txt requirements/dbt.lock /tmp/requirements/
RUN pip install --no-cache-dir -r /tmp/requirements/dbt.txt -c /tmp/requirements/dbt.lock
COPY dbt /app/dbt
WORKDIR /app/dbt
RUN PIM_DB_HOST=parse PIM_DB_PORTA=5432 PIM_DB_NOME=parse PIM_DB_USUARIO=parse PIM_DB_SENHA=parse \
    dbt parse --profiles-dir /app/dbt --target-path /app/target

# Etapa 2: a imagem oficial já traz os providers docker e standard e o requests. Só o Cosmos é acrescentado:
# a extração roda na API, e o dbt, no próprio contêiner.
FROM apache/airflow:3.4.0-python3.12

COPY requirements/airflow.txt requirements/airflow.lock /tmp/requirements/
# apache-airflow fixo na versão da imagem, para o pip não trocar o Airflow ao instalar o Cosmos.
RUN pip install --no-cache-dir "apache-airflow==3.4.0" -r /tmp/requirements/airflow.txt -c /tmp/requirements/airflow.lock

COPY --chown=airflow:root --from=manifesto /app/target/manifest.json /opt/airflow/dbt/manifest.json
COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root src/pim_pf/__init__.py src/pim_pf/cliente_api.py /opt/airflow/src/pim_pf/

ENV PYTHONPATH=/opt/airflow/src
