# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS image

ARG NIXPKGS_REV

COPY nix.conf /etc/nix/nix.conf

ENV PATH=/opt/ci-tools/bin:/nix/var/nix/profiles/default/bin:/nix/var/nix/profiles/default/sbin

RUN mkdir -p /opt \
  && nixpkgs="https://github.com/NixOS/nixpkgs/archive/${NIXPKGS_REV}.tar.gz" \
  && nix-env --profile /opt/ci-tools --file "$nixpkgs" \
    --install --attr nixfmt statix deadnix ruff \
  && nix-env --profile /opt/ci-tools --file "$nixpkgs" \
    --install --from-expression 'nixpkgs: (nixpkgs { }).python3.withPackages (ps: [ ps.mypy ps.pytest ])' \
  && nix-store --gc \
  && nixfmt --version \
  && statix --help \
  && deadnix --version \
  && ruff --version \
  && python3 --version \
  && mypy --version \
  && pytest --version

ARG BASE_IMAGE

RUN kv() { printf '%s="%s"\n' "$1" "$2"; } \
  && { \
    kv IMAGE ci/nix; \
    nix_version=$(nix --version); kv NIX "${nix_version##* }"; \
    nix-env --profile /opt/ci-tools --query --installed | while read -r entry; do \
      name=${entry%%-[0-9]*}; version=${entry#"$name"-}; \
      kv "$(printf '%s' "$name" | tr '[:lower:]' '[:upper:]' | tr - _)" "${version%-env}"; \
    done; \
    kv MYPY "$(mypy --version | cut -d ' ' -f 2)"; \
    kv PYTEST "$(pytest --version | cut -d ' ' -f 2)"; \
    kv NIXPKGS "${NIXPKGS_REV}"; \
    kv BASE "${BASE_IMAGE}"; \
    kv DOCS https://github.com/mr-chelyshkin/images/tree/main/ci/nix; \
  } > /etc/ci-image \
  && ! grep -q '=""$' /etc/ci-image \
  && cat /etc/ci-image

WORKDIR /workspace
