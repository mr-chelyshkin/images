# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION
ARG MDFORMAT_VERSION
ARG MDFORMAT_GFM_VERSION

RUN test "$(python --version)" = "Python ${PYTHON_VERSION}" \
  && python -m pip install --no-cache-dir \
    "mdformat==${MDFORMAT_VERSION}" \
    "mdformat-gfm==${MDFORMAT_GFM_VERSION}" \
  && python -c 'from importlib.metadata import version; import sys; assert version("mdformat") == sys.argv[1]; assert version("mdformat-gfm") == sys.argv[2]' \
    "${MDFORMAT_VERSION}" "${MDFORMAT_GFM_VERSION}"

WORKDIR /workspace
