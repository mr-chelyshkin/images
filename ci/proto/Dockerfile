# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG BUF_VERSION
ARG CLANG_FORMAT_VERSION
ARG TARGETARCH

RUN --mount=type=bind,source=install.sh,target=/tmp/install-proto-tools,ro \
  /bin/sh /tmp/install-proto-tools \
    "${BUF_VERSION}" \
    "${CLANG_FORMAT_VERSION}" \
    "${TARGETARCH}"

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/proto; \
    kv BUF "$(buf --version)"; \
    kv CLANG_FORMAT "$(clang-format --version | sed -n 's/.*clang-format version \([^ ]*\).*/\1/p')"; \
    kv GIT "$(git --version | awk '{ print $3 }')"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/proto; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
