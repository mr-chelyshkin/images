# ci/aws

AWS CLI v2 for CI workflows.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

- The CLI is installed with the official AWS installer, which verifies the
  archive's GPG signature.
- Commands never wait for a pager: `AWS_PAGER` is empty.
- Credentials and region come from the environment, for example
  `AWS_ACCESS_KEY_ID` and `AWS_REGION`.
