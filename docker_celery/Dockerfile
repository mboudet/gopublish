FROM alpine:3.13

MAINTAINER "Mateo Boudet <mateo.boudet@inrae.fr>"

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0

COPY . /gopublish
WORKDIR /gopublish

RUN apk add --no-cache \
    python3 \
    bash \
    nano \
    py-psutil \
    postgresql-libs && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    apk add --no-cache --virtual .build-deps gcc g++ musl-dev python3-dev postgresql-dev && \
    pip3 install -r /gopublish/requirements_celery.txt && \
    apk --purge del .build-deps && \
    rm -r /root/.cache

ENTRYPOINT celery -A gopublish.tasks.celery worker --concurrency=10 --loglevel=info
