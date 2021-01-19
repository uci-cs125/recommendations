FROM python:3.7

## Setup base OS
RUN pip3 install --upgrade pip
RUN apt-get update && apt-get install -y build-essential libffi-dev

## Set up environment with Flask App
WORKDIR /var/www/app

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]
