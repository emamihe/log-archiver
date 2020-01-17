FROM python:2.7-alpine
MAINTAINER Hamid Emamian, emami.he@gmail.com
COPY . /app
WORKDIR /app
RUN apk add gcc && \
    apk add libc-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    mkdir /var/log/log-archiver && \
    mkdir /var/lib/log-archiver
CMD ["python", "/app/archiver.py", "--config", "config.json"]
