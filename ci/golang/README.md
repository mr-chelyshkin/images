# ci/golang

Go toolchain with gofumpt, golangci-lint, and govulncheck.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

- Every Go variant carries its own builds of the tools, compiled with that Go
  version.
- The base is the official `golang` image; its operating system is reported as
  `OS` in `/etc/ci-image`.
