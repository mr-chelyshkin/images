# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG NIXPKGS_REV

COPY nix.conf /etc/nix/nix.conf

ENV PATH=/opt/ci-tools/bin:/nix/var/nix/profiles/default/bin:/nix/var/nix/profiles/default/sbin

RUN mkdir -p /opt \
  && nix-env --option filter-syscalls false --profile /opt/ci-tools \
    --file "https://github.com/NixOS/nixpkgs/archive/${NIXPKGS_REV}.tar.gz" \
    --install --attr nixfmt statix deadnix \
  && nix-store --gc \
  && nixfmt --version \
  && statix --help \
  && deadnix --version

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/nix; \
    nix_version=$(nix --version); kv NIX "${nix_version##* }"; \
    nix-env --profile /opt/ci-tools --query --installed | while read -r entry; do \
      name=${entry%%-[0-9]*}; \
      kv "$(printf '%s' "$name" | tr '[:lower:]' '[:upper:]' | tr - _)" "${entry#"$name"-}"; \
    done; \
    kv NIXPKGS "${NIXPKGS_REV}"; \
    kv BASE "${BASE_IMAGE}"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/nix; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
