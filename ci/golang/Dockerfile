# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS tools

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG GOFUMPT_VERSION
ARG GOLANGCI_LINT_VERSION
ARG GOVULNCHECK_VERSION

ENV GOBIN=/usr/local/bin

RUN go install mvdan.cc/gofumpt@"${GOFUMPT_VERSION}" \
    && go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@"${GOLANGCI_LINT_VERSION}" \
    && go install golang.org/x/vuln/cmd/govulncheck@"${GOVULNCHECK_VERSION}"

FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

COPY --from=tools \
  /usr/local/bin/gofumpt \
  /usr/local/bin/golangci-lint \
  /usr/local/bin/govulncheck \
  /usr/local/bin/

WORKDIR /workspace
