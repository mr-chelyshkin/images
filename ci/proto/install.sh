#!/bin/sh

set -eu

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <buf-version> <clang-format-major-version> <target-architecture>" >&2
  exit 2
fi

buf_version="$1"
clang_format_version="$2"
target_arch="$3"

case "${target_arch}" in
  amd64)
    buf_arch="x86_64"
    ;;
  arm64)
    buf_arch="aarch64"
    ;;
  *)
    echo "unsupported architecture: ${target_arch}" >&2
    exit 1
    ;;
esac

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
  ca-certificates \
  "clang-format-${clang_format_version}" \
  curl \
  git

buf_binary="buf-Linux-${buf_arch}"
curl -fsSL \
  "https://github.com/bufbuild/buf/releases/download/v${buf_version}/${buf_binary}" \
  -o "/tmp/${buf_binary}"
install -m 0755 "/tmp/${buf_binary}" /usr/local/bin/buf
ln -sf "/usr/bin/clang-format-${clang_format_version}" /usr/local/bin/clang-format

installed_buf_version="$(buf --version)"
if [ "${installed_buf_version}" != "${buf_version}" ]; then
  echo "unexpected Buf version: ${installed_buf_version}" >&2
  exit 1
fi

installed_clang_format_version="$(clang-format --version)"
case "${installed_clang_format_version}" in
  *"clang-format version ${clang_format_version}."*)
    ;;
  *)
    echo "unexpected clang-format version: ${installed_clang_format_version}" >&2
    exit 1
    ;;
esac

apt-get purge --yes --auto-remove curl
rm -f "/tmp/${buf_binary}"
rm -rf /var/lib/apt/lists/*
