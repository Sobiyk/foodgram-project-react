FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./foodgram .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]