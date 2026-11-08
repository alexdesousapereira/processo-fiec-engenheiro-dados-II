# dbt e o projeto na imagem: o DockerOperator não depende de caminhos da máquina host.
FROM python:3.12.13-slim-bookworm

# O arquivo .lock trava também as dependências indiretas, para cada build instalar as mesmas versões.
COPY requirements/dbt.txt requirements/dbt.lock /tmp/requirements/
RUN pip install --no-cache-dir -r /tmp/requirements/dbt.txt -c /tmp/requirements/dbt.lock

COPY dbt /app/dbt
WORKDIR /app/dbt

# target e logs ficam fora do projeto, em uma pasta que o usuário sem privilégios pode gravar.
ENV DBT_PROFILES_DIR=/app/dbt
ENV DBT_PROJECT_DIR=/app/dbt
ENV DBT_TARGET_PATH=/tmp/dbt/target
ENV DBT_LOG_PATH=/tmp/dbt/logs

RUN useradd --uid 1000 --create-home dbt
USER dbt
