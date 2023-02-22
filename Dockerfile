FROM python:3.11

LABEL cryptohuntbackend image

WORKDIR /

COPY "requirements.txt" "requirements.txt"

RUN ["pip3", "install", "-r","requirements.txt"]

RUN ["pip3", "install", "gunicorn", "boto3"]

WORKDIR /crypto-hunt-backend

COPY . .

CMD gunicorn --bind 0.0.0.0:80 --workers 10 wsgi:app
