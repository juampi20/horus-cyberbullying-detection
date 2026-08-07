FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt

RUN uv pip install --system -r /app/requirements.txt

RUN python -m spacy download en_core_web_sm

# notificación: los modelos se montan por volumen (docker-compose) — build context=./backend
# El contexto de build es ./backend, así que la raíz models/ (con los .pkl) NO se copia aquí:
# los .pkl viven en el host en <repo-root>/models/ y el código los carga desde MODELS_PATH
# (backend/app/api/constants.py). Para que el container encuentre los modelos, docker-compose
# debe montar por volumen <repo-root>/models/ en el path que MODELS_PATH resuelve dentro de la
# imagen (con COPY . /app/ y parents[3], ese path es /models). Ver docker-compose.yml.
COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
