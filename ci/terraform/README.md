# ci/terraform

Terraform CLI for CI workflows.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

- Terraform is downloaded from `releases.hashicorp.com` and verified with
  HashiCorp's GPG signature and SHA-256 checksums.
