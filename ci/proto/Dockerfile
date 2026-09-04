# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG BUF_VERSION
ARG CLANG_FORMAT_VERSION
ARG TARGETARCH

RUN --mount=type=bind,source=install.sh,target=/tmp/install-proto-tools,ro \
  /bin/sh /tmp/install-proto-tools \
    "${BUF_VERSION}" \
    "${CLANG_FORMAT_VERSION}" \
    "${TARGETARCH}"

WORKDIR /workspace
