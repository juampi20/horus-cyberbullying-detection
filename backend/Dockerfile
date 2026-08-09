FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt

RUN uv pip install --system -r /app/requirements.txt

# Versión explícita del modelo: spacy 3.7.2 arma una URL rota (404) con
# `download en_core_web_sm` genérico; pinneando la versión 3.7.1 (compatible)
# el download resuelve determinísticamente.
RUN python -m spacy download en_core_web_sm-3.7.1

# notificación: los modelos se montan por volumen (docker-compose), build context=./backend
# El contexto de build es ./backend, así que la raíz models/ (con los .pkl) NO se copia aquí:
# los .pkl viven en el host en <repo-root>/models/ y el código los carga desde MODELS_DIR
# (app/core/config.py, parents[3] / "models"). Para que el container encuentre los modelos,
# docker-compose monta por volumen <repo-root>/models/ en el path que MODELS_DIR resuelve
# dentro de la imagen (con COPY . /app/ y parents[3], ese path es /models). Ver docker-compose.yml.
COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
