# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG NODE_VERSION

RUN test "$(node --version)" = "v${NODE_VERSION}"

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/node; \
    kv NODE "$(node --version | sed 's/^v//')"; \
    kv NPM "$(npm --version)"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/node; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
