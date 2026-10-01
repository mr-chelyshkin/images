# Container images

[![License: Apache-2.0](https://img.shields.io/github/license/mr-chelyshkin/images?label=license)](LICENSE)

<p align="center">
  <img src=".github/assets/readme-header.png"
       alt="github.com/mr-chelyshkin/images"
       width="800">
</p>

### Container images for my local Taskfile commands and CI workflows.

The publishing target prefix is `ghcr.io/mr-chelyshkin/`. 

## Images

| Context                        | Tag       | Included tools                                                                |
|--------------------------------|-----------|-------------------------------------------------------------------------------|
| [`ci/aws`](ci/aws)             | `2.36.24` | AWS CLI v2 `2.36.24`                                                          |
| [`ci/golang`](ci/golang)       | `1.26.4`  | Go `1.26.4`, gofumpt `v0.7.0`, golangci-lint `v2.9.0`, govulncheck `v1.7.0`   |
| [`ci/golang`](ci/golang)       | `1.27.1`  | Go `1.27.1`, gofumpt `v0.7.0`, golangci-lint `v2.13.2`, govulncheck `v1.7.0`  |
| [`ci/markdown`](ci/markdown)   | `1.0.0`   | mdformat `1.0.0`, mdformat-gfm `1.0.0`, Python `3.14.7`                       |
| [`ci/nix`](ci/nix)             | `2.35.2`  | Nix `2.35.2`, nixfmt `1.4.0`, statix `0-unstable-2026-05-14`, deadnix `1.3.2` |
| [`ci/node`](ci/node)           | `22.23.1` | Node.js `22.23.1`; npm from the base image, not pinned separately             |
| [`ci/proto`](ci/proto)         | `1.50.0`  | Buf `1.50.0`, clang-format `14.x` from Debian bookworm                        |
| [`ci/python`](ci/python)       | `3.14.7`  | Python `3.14.7`, uv `0.12.9`                                                  |
| [`ci/rust`](ci/rust)           | `1.90.0`  | Rust `1.90.0`, rustfmt, Clippy, cargo-audit `0.22.0`                          |
| [`ci/terraform`](ci/terraform) | `1.15.9`  | Terraform `1.15.9`, Bash, Git, curl, unzip                                    |

The workflow builds all current images for `linux/amd64` and `linux/arm64`. 

## Use an image directly

Mount the current repository and run a command from `/workspace`:

```sh
docker run --rm --init \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --env GOPATH=/tmp/go \
  --volume "$PWD:/workspace" \
  --workdir /workspace \
  ghcr.io/mr-chelyshkin/ci/golang:1.27.1 \
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

### Nix commands

The Nix image enables `nix-command` and flakes. Its `NIXPKGS_REV` build argument pins
the formatter and linters; project dependencies remain controlled by the project's
own lock file.

Run Nix commands as the image's default user (`root` inside the container) to allow
writes to `/nix`. Nix uses a single-user store without its own build sandbox; Docker
provides the container boundary. No privileged container or extra capabilities are required:

```sh
docker run --rm --init \
  --security-opt no-new-privileges --cap-drop ALL \
  --volume "$PWD:/workspace:ro" \
  --workdir /workspace \
  ghcr.io/mr-chelyshkin/ci/nix:2.35.2 \
  nix flake check --no-build --no-write-lock-file
```

The standalone `nixfmt`, `statix`, and `deadnix` commands also support running with
`--user "$(id -u):$(id -g)"`. Use that mode for formatting files in a writable bind mount.

Prefer the native image architecture. In local AMD64-on-ARM64 testing, Nix builds
failed with `unable to load seccomp BPF program`. For that emulated run,
`--option filter-syscalls false` disables Nix's syscall filter for the command;
Docker's security restrictions remain in place. The image keeps Nix's runtime
filter enabled by default.

## Taskfile consumers

These images can be used with the companion [Taskfiles repository](https://github.com/mr-chelyshkin/tasks), which provides
reusable tasks for local development and CI.

> See the [Taskfiles documentation](https://github.com/mr-chelyshkin/tasks#quick-start) for setup, configuration, and usage.

## Add an image or variant

Each image context has this shape:

```text
ci/<name>/
├── Dockerfile
├── variants.yaml
└── ...             # optional build helpers and configuration
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

> Every Sunday, a scheduled run rebuilds and publishes the complete matrix.
> This picks up available system package updates and security fixes without requiring source changes.

For each variant, the workflow publishes:

- `<version>`;
- `<version>-sha-<full-commit-sha>`.

> It does not publish `latest`. 
 
The workflow writes OCI source, revision, version, creation time, title, author, and description metadata, 
including description on the root multi-platform index.
