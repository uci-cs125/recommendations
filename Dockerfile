FROM python:3.8-alpine
RUN pip3 install --upgrade pip

WORKDIR /var/www/app

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

COPY . /var/www/app
RUN pip3 install -r requirements.txt

ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]
