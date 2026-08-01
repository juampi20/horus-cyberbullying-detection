FROM python:3.9-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

RUN mkdir /src_streamlit

COPY requirements.txt /src_streamlit

WORKDIR /src_streamlit

RUN uv pip install --system -r requirements.txt

COPY . /src_streamlit

EXPOSE 8501

CMD ["streamlit", "run", "ui.py"]