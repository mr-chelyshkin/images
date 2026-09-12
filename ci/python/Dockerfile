# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
ARG UV_IMAGE
FROM ${UV_IMAGE} AS uv

FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION
ARG UV_VERSION

COPY --from=uv /uv /uvx /usr/local/bin/

RUN test "$(python --version)" = "Python ${PYTHON_VERSION}" \
  && test "$(uv --version | cut -d ' ' -f 2)" = "${UV_VERSION}"

WORKDIR /workspace
