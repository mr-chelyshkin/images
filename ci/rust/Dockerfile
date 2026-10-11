# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS cargo-tools

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG CARGO_AUDIT_VERSION

RUN cargo install cargo-audit \
  --version "${CARGO_AUDIT_VERSION}" \
  --locked \
  --features fix \
  --root /opt/cargo-tools

FROM ${BASE_IMAGE}

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
  && rm -rf /var/lib/apt/lists/*

ARG CARGO_AUDIT_VERSION
ARG RUST_VERSION

RUN test "$(rustc --version | cut -d ' ' -f 2)" = "${RUST_VERSION}" \
  && rustup component add --toolchain "${RUST_VERSION}" rustfmt clippy \
  && rustup target add --toolchain "${RUST_VERSION}" aarch64-unknown-linux-musl x86_64-unknown-linux-musl

COPY --from=cargo-tools /opt/cargo-tools/bin/cargo-audit /usr/local/bin/

RUN test "$(cargo-audit --version)" = "cargo-audit ${CARGO_AUDIT_VERSION}"

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/rust; \
    kv RUST "$(rustc --version | awk '{ print $2 }')"; \
    kv CARGO "$(cargo --version | awk '{ print $2 }')"; \
    kv RUSTFMT "$(rustfmt --version | awk '{ print $2 }')"; \
    kv CLIPPY "$(cargo clippy --version | awk '{ print $2 }')"; \
    kv CARGO_AUDIT "$(cargo-audit --version | awk '{ print $2 }')"; \
    kv TARGETS "$(rustup target list --installed | tr '\n' ' ' | sed 's/ $//')"; \
    kv BASE "${BASE_IMAGE}"; \
    kv OS "$(. /etc/os-release && echo "$PRETTY_NAME")"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/rust; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
