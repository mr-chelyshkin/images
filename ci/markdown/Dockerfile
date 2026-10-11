# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS image

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION
ARG MDFORMAT_VERSION
ARG MDFORMAT_GFM_VERSION

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt,ro \
  test "$(python --version)" = "Python ${PYTHON_VERSION}" \
  && python -m pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
  && python -m pip check \
  && python -c 'from importlib.metadata import version; import sys; assert version("mdformat") == sys.argv[1]; assert version("mdformat-gfm") == sys.argv[2]' \
    "${MDFORMAT_VERSION}" "${MDFORMAT_GFM_VERSION}"

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/markdown; \
    kv PYTHON "$(python -c 'import platform; print(platform.python_version())')"; \
    python -m pip list --format=freeze --exclude pip \
      | awk -F '==' '{ k = toupper($1); gsub(/[-.]/, "_", k); printf "%s=\"%s\"\n", k, $2 }'; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/markdown; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
