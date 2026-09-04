#!/bin/sh

set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <terraform-version> <target-architecture>" >&2
  exit 2
fi

terraform_version="$1"
target_arch="$2"

case "${target_arch}" in
  amd64|arm64)
    terraform_arch="${target_arch}"
    ;;
  *)
    echo "unsupported architecture: ${target_arch}" >&2
    exit 1
    ;;
esac

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
  bash \
  ca-certificates \
  curl \
  git \
  gpg \
  unzip

terraform_base_url="https://releases.hashicorp.com/terraform/${terraform_version}"
terraform_archive="terraform_${terraform_version}_linux_${terraform_arch}.zip"
terraform_checksums="terraform_${terraform_version}_SHA256SUMS"
terraform_signature="${terraform_checksums}.sig"

download_dir="$(mktemp -d)"
trap 'rm -rf "${download_dir}"' EXIT

curl -fsSL \
  "${terraform_base_url}/${terraform_archive}" \
  -o "${download_dir}/${terraform_archive}"
curl -fsSL \
  "${terraform_base_url}/${terraform_checksums}" \
  -o "${download_dir}/${terraform_checksums}"
curl -fsSL \
  "${terraform_base_url}/${terraform_signature}" \
  -o "${download_dir}/${terraform_signature}"
curl -fsSL \
  "https://www.hashicorp.com/.well-known/pgp-key.txt" \
  -o "${download_dir}/hashicorp-release-key.asc"

gpg --batch --dearmor \
  --output "${download_dir}/hashicorp-release-keyring.gpg" \
  "${download_dir}/hashicorp-release-key.asc"
gpgv --keyring "${download_dir}/hashicorp-release-keyring.gpg" \
  "${download_dir}/${terraform_signature}" \
  "${download_dir}/${terraform_checksums}"

awk -v archive="${terraform_archive}" '
  $2 == archive { matches++; checksum = $0 }
  END {
    if (matches != 1) exit 1
    print checksum
  }
' "${download_dir}/${terraform_checksums}" > "${download_dir}/terraform.sha256"

(
  cd "${download_dir}"
  sha256sum -c terraform.sha256
)

unzip -q "${download_dir}/${terraform_archive}" terraform -d /usr/local/bin
chmod 0755 /usr/local/bin/terraform

installed_version="$(CHECKPOINT_DISABLE=1 terraform version | sed -n '1s/^Terraform v//p')"
if [ "${installed_version}" != "${terraform_version}" ]; then
  echo "unexpected Terraform version: ${installed_version}" >&2
  exit 1
fi

apt-get purge --yes --auto-remove gpg
rm -rf /var/lib/apt/lists/*
