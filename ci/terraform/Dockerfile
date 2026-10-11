# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS image

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
ARG TERRAFORM_VERSION

RUN --mount=type=bind,source=install.sh,target=/tmp/install-terraform,ro \
  /bin/sh /tmp/install-terraform "${TERRAFORM_VERSION}" "${TARGETARCH}"

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/terraform; \
    kv TERRAFORM "$(CHECKPOINT_DISABLE=1 terraform version | sed -n '1s/^Terraform v//p')"; \
    kv GIT "$(git --version | awk '{ print $3 }')"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/terraform; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
