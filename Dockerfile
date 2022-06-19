FROM python:3.9-alpine

WORKDIR /url-scraper

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app2.py

CMD ["flask", "run", "--host=0.0.0.0"]