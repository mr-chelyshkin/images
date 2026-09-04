# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG NODE_VERSION

RUN test "$(node --version)" = "v${NODE_VERSION}"

WORKDIR /workspace
