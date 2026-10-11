# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS tools

ARG GOFUMPT_VERSION
ARG GOLANGCI_LINT_VERSION
ARG GOVULNCHECK_VERSION

ENV GOBIN=/usr/local/bin

RUN go install mvdan.cc/gofumpt@"${GOFUMPT_VERSION}" \
    && go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@"${GOLANGCI_LINT_VERSION}" \
    && go install golang.org/x/vuln/cmd/govulncheck@"${GOVULNCHECK_VERSION}" \
    && go clean -cache -modcache

FROM ${BASE_IMAGE} AS image

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

COPY --from=tools \
  /usr/local/bin/gofumpt \
  /usr/local/bin/golangci-lint \
  /usr/local/bin/govulncheck \
  /usr/local/bin/

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/golang; \
    kv GO "$(go env GOVERSION | sed 's/^go//')"; \
    kv GOFUMPT "$(go version -m /usr/local/bin/gofumpt | awk '$1 == "mod" { print $3 }')"; \
    kv GOLANGCI_LINT "$(go version -m /usr/local/bin/golangci-lint | awk '$1 == "mod" { print $3 }')"; \
    kv GOVULNCHECK "$(go version -m /usr/local/bin/govulncheck | awk '$1 == "mod" { print $3 }')"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/golang; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
