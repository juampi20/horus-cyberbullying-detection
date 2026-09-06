FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt

RUN uv pip install --system -r /app/requirements.txt

# Version explicita del modelo: spacy 3.7.2 arma una URL rota (404) con
# `download en_core_web_sm` generico; pinneando la version 3.7.1 (compatible)
# el download resuelve deterministicamente.
RUN python -m spacy download en_core_web_sm-3.7.1

# Los artefactos del modelo (.pkl entrenados por notebooks/03_train.ipynb) y la tabla de
# metricas models_results.csv viven en el arbol del repo bajo backend/app/api/models/.
# Como el contexto de build es ./backend, COPY . /app/ los reproduce dentro de la imagen
# en /app/app/api/models/ — el mismo path que resuelven MODELS_DIR y METRICS_PATH
# (app/core/config.py). No se montan volumenes del host para los modelos.
COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
