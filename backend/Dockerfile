FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./foodgram .
RUN cd foodgram/ && gunicorn --bind 0.0.0.0:8000 foodgram.wsgi
