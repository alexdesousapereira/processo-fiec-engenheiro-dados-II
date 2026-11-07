# A imagem oficial já traz os providers docker e standard e o requests. Nada é instalado:
# a extração roda na API, e o dbt, no próprio contêiner.
FROM apache/airflow:3.4.0-python3.12

COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root src/pim_pf/__init__.py src/pim_pf/cliente_api.py /opt/airflow/src/pim_pf/

ENV PYTHONPATH=/opt/airflow/src
