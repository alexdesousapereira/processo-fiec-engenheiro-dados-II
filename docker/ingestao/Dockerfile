# API e extração. Os testes vão na imagem porque tudo no projeto roda em contêiner.
FROM python:3.12.13-slim-bookworm

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# O arquivo .lock trava também as dependências indiretas, para cada build instalar as mesmas versões.
COPY requirements/ /tmp/requirements/
RUN pip install --no-cache-dir -r /tmp/requirements/testes.txt -c /tmp/requirements/ingestao.lock

COPY src /app/src
COPY tests /app/tests

# O volume nomeado herda o dono desta pasta na primeira vez em que é criado.
RUN useradd --uid 1000 --create-home ingestao \
    && mkdir -p /app/data \
    && chown -R ingestao /app
USER ingestao

# Um só worker: a extração roda em segundo plano neste processo.
CMD ["uvicorn", "pim_pf.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
