FROM python:3.7-alpine

RUN apk add git

COPY . /app
WORKDIR /app
RUN source env/bin/activate
RUN pip install -r requirements.txt
