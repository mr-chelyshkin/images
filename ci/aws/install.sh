#!/usr/bin/env bash

set -euo pipefail

if (( $# != 1 )); then
  echo "usage: $0 <aws-cli-version>" >&2
  exit 2
fi

readonly aws_cli_version="$1"

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
  ca-certificates \
  curl \
  gnupg \
  unzip

curl -fsSL "https://awscli.amazonaws.com/v2/install.sh" |
  bash -s -- \
    --version "${aws_cli_version}" \
    --system \
    --quiet

installed_version="$(aws --version 2>&1)"

if [[ "${installed_version}" != "aws-cli/${aws_cli_version} "* ]]; then
  echo "unexpected AWS CLI version: ${installed_version}" >&2
  exit 1
fi

apt-get purge --yes --auto-remove curl gnupg unzip
rm -rf /var/lib/apt/lists/*
