#!/bin/bash

export DOCKER_FILE=Dockerfile

export DOCKER_IMAGE_REFERENCE=shallowview/prprocess:3.21.0-alpine
export DOCKER_CONTAINER_NAME=sv-preprocess

export DOCKER_OUTPUT_VOLUME_NAME=$DOCKER_CONTAINER_NAME-outputs