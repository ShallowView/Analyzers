FROM python:3.13-alpine3.21 AS base

ARG DOCKER_FILES_ROOT=bin/docker

ENV PYROOT=/usr/src/preprocess

RUN apk add postgresql-dev

COPY ./ $PYROOT
WORKDIR $PYROOT

RUN pip install -r requirements.txt --verbose

FROM base AS preprocess

ENV DOCKERFILE_FOLDER=$PYROOT/$DOCKER_FILES_ROOT

ENTRYPOINT ["sh", "bin/analysis/preProcess.sh"]