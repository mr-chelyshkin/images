# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
ARG TERRAFORM_VERSION

RUN --mount=type=bind,source=install.sh,target=/tmp/install-terraform,ro \
  /bin/sh /tmp/install-terraform "${TERRAFORM_VERSION}" "${TARGETARCH}"

WORKDIR /workspace
