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

WORKDIR /workspace
