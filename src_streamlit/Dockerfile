FROM python:3.9-slim

RUN mkdir /src_streamlit

COPY requirements.txt /src_streamlit

WORKDIR /src_streamlit

RUN pip install -r requirements.txt

COPY . /src_streamlit

EXPOSE 8501

CMD ["streamlit", "run", "ui.py"]