FROM python:2.7-alpine
MAINTAINER Hamid Emamian, emami.he@gmail.com
COPY . /app
WORKDIR /app
RUN apk add gcc && \
    apk add libc-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
VOLUME ["/var/lib/log-archiver", "/var/log/log-archiver"]
CMD ["python", "/app/archiver.py", "--config", "config.json"]
