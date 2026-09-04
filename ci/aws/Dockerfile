# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG AWS_CLI_VERSION

RUN --mount=type=bind,source=install.sh,target=/tmp/install-aws-cli,ro \
  /bin/bash /tmp/install-aws-cli "${AWS_CLI_VERSION}"

ENV AWS_PAGER=""

WORKDIR /workspace
