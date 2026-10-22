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

| Context | Purpose |
| -- | -- |
| [`ci/aws`](ci/aws) | AWS CLI v2. |
| [`ci/golang`](ci/golang) | Go with gofumpt, golangci-lint, and govulncheck. |
| [`ci/markdown`](ci/markdown) | mdformat with GitHub Flavored Markdown support. |
| [`ci/nix`](ci/nix) | Nix with nixfmt, statix, and deadnix. |
| [`ci/node`](ci/node) | Node.js and npm. |
| [`ci/proto`](ci/proto) | Buf and clang-format. |
| [`ci/python`](ci/python) | Python and uv. |
| [`ci/rust`](ci/rust) | Rust with rustfmt, Clippy, and cargo-audit. |
| [`ci/terraform`](ci/terraform) | Terraform CLI. |

Each context has a README with the image specifics. Tags and pinned versions
live in its `variants.yaml`. The workflow builds all images for `linux/amd64`
and `linux/arm64`.

## What is inside an image

Every image describes itself in `/etc/ci-image`:

```sh
docker run --rm ghcr.io/mr-chelyshkin/ci/golang:1.27.3 cat /etc/ci-image
```

## Taskfile consumers

These images can be used with the companion
[Taskfiles repository](https://github.com/mr-chelyshkin/tasks), which provides
reusable tasks for local development and CI.

> See the
> [Taskfiles documentation](https://github.com/mr-chelyshkin/tasks#quick-start)
> for setup, configuration, and usage.

## Publishing and tags

> Every Sunday, a scheduled run rebuilds and publishes the complete matrix. This
> picks up available system package updates and security fixes without requiring
> source changes.

For each variant, the workflow publishes one tag: `<version>`.

> It does not publish `latest`.

The tag moves with the weekly rebuild. The source commit of a build is in the
`org.opencontainers.image.revision` label.
