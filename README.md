# Container images

[![License: Apache-2.0](https://img.shields.io/github/license/mr-chelyshkin/images?label=license)](LICENSE)

Container images for my local Taskfile commands and CI workflows.

The publish target prefix is `ghcr.io/mr-chelyshkin/`. 
A reference becomes usable only after its workflow run succeeds.

## Images

| Context                        | Tag       | Included tools                                                              |
|--------------------------------|-----------|-----------------------------------------------------------------------------|
| [`ci/aws`](ci/aws)             | `2.36.24` | AWS CLI v2 `2.36.24`                                                        |
| [`ci/golang`](ci/golang)       | `1.26.4`  | Go `1.26.4`, gofumpt `v0.7.0`, golangci-lint `v2.9.0`, govulncheck `v1.7.0` |
| [`ci/node`](ci/node)           | `22.23.1` | Node.js `22.23.1`; npm from the base image, not pinned separately           |
| [`ci/proto`](ci/proto)         | `1.50.0`  | Buf `1.50.0`, clang-format `14.x` from Debian bookworm                      |
| [`ci/rust`](ci/rust)           | `1.90.0`  | Rust `1.90.0`, rustfmt, Clippy, cargo-audit `0.22.0`                        |
| [`ci/terraform`](ci/terraform) | `1.15.9`  | Terraform `1.15.9`, Bash, Git, curl, unzip                                  |

The workflow builds all current images for `linux/amd64` and `linux/arm64`. 
Each image uses `/workspace`; pass the complete command after the image reference.

## Use an image directly

Mount the current repository and run a command from `/workspace`:

```sh
docker run --rm --init \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --env GOPATH=/tmp/go \
  --volume "$PWD:/workspace" \
  --workdir /workspace \
  ghcr.io/mr-chelyshkin/ci/golang:1.26.4 \
  go test ./...
```

Open a shell in the same layout:

```sh
docker run --rm --interactive --tty \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --volume "$PWD:/workspace" \
  --workdir /workspace \
  ghcr.io/mr-chelyshkin/ci/terraform:1.15.9 \
  /bin/bash
```

## Taskfile consumers

These images can be used with the companion [Taskfiles repository](https://github.com/mr-chelyshkin/tasks), which provides 
reusable tasks for local development and CI. See its documentation for setup, configuration, and usage.

## Add an image or variant

Each image context has this shape:

```text
ci/<name>/
├── Dockerfile
├── variants.yaml
└── *.sh            # optional build helpers
```

Use lowercase letters, digits, and internal hyphens for `<name>`. 
A minimal manifest is:

```yaml
schema: 1
description: "Short single-line image description."

variants:
  - tag: "1.2.3"
    build_args:
      BASE_IMAGE: "debian:bookworm-slim"
      TOOL_VERSION: "1.2.3"
```

## Publishing and tags

- A push to `main` publishes changed image contexts. 
- A manual workflow dispatch publishes the complete matrix. 
- Changes to the shared workflow or matrix scripts also publish the complete matrix.

For each variant, the workflow publishes:

- `<version>`;
- `<version>-sha-<full-commit-sha>`.

> It does not publish `latest`. 
 
The workflow writes OCI source, revision, version, creation time, title, author,
and description metadata, including description on the root multi-platform index.
