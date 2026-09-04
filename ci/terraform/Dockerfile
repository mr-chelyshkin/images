# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG TARGETARCH
ARG TERRAFORM_VERSION

RUN --mount=type=bind,source=install.sh,target=/tmp/install-terraform,ro \
  /bin/sh /tmp/install-terraform "${TERRAFORM_VERSION}" "${TARGETARCH}"

WORKDIR /workspace
