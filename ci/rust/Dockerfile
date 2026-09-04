# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS cargo-tools

ARG CARGO_AUDIT_VERSION

RUN cargo install cargo-audit \
  --version "${CARGO_AUDIT_VERSION}" \
  --locked \
  --features fix \
  --root /opt/cargo-tools

FROM ${BASE_IMAGE}

ARG CARGO_AUDIT_VERSION
ARG RUST_VERSION

RUN test "$(rustc --version | cut -d ' ' -f 2)" = "${RUST_VERSION}" \
  && rustup component add --toolchain "${RUST_VERSION}" rustfmt clippy

COPY --from=cargo-tools /opt/cargo-tools/bin/cargo-audit /usr/local/bin/

RUN test "$(cargo-audit --version)" = "cargo-audit ${CARGO_AUDIT_VERSION}"

WORKDIR /workspace
