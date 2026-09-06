# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG AWS_CLI_VERSION

RUN --mount=type=bind,source=install.sh,target=/tmp/install-aws-cli,ro \
  /bin/bash /tmp/install-aws-cli "${AWS_CLI_VERSION}"

ENV AWS_PAGER=""

WORKDIR /workspace
