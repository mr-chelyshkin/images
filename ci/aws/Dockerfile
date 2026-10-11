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

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/aws; \
    kv AWS_CLI "$(aws --version 2>&1 | sed -n 's|^aws-cli/\([^ ]*\) .*|\1|p')"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/aws; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
