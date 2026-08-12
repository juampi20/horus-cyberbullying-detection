FROM python:3.9-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

RUN mkdir /app

COPY requirements.txt /app

WORKDIR /app

RUN uv pip install --system -r requirements.txt

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
