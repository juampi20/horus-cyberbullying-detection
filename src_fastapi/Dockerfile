FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt \
    && rm -rf /root/.cache/pip

RUN python -m spacy download en_core_web_sm

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
