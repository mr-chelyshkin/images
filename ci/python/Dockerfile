# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
ARG UV_IMAGE
FROM ${UV_IMAGE} AS uv

FROM ${BASE_IMAGE} AS image

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION
ARG UV_VERSION

COPY --from=uv /uv /uvx /usr/local/bin/

RUN test "$(python --version)" = "Python ${PYTHON_VERSION}" \
  && test "$(uv --version | cut -d ' ' -f 2)" = "${UV_VERSION}"

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/python; \
    kv PYTHON "$(python -c 'import platform; print(platform.python_version())')"; \
    kv UV "$(uv --version | awk '{ print $2 }')"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/python; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
