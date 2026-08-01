FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt

RUN uv pip install --system -r /app/requirements.txt

RUN python -m spacy download en_core_web_sm

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
