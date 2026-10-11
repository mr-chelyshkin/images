# ci/rust

Rust toolchain with rustfmt, Clippy, and cargo-audit.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions and targets: `cat /etc/ci-image` inside the image.

## Notes

- cargo-audit is built with the `fix` feature and supports `cargo audit fix`.
- The `aarch64-unknown-linux-musl` and `x86_64-unknown-linux-musl` targets are
  installed. Linking them needs `rust-lld`, for example in the project's
  `.cargo/config.toml`:

```toml
[target.aarch64-unknown-linux-musl]
linker = "rust-lld"

[target.x86_64-unknown-linux-musl]
linker = "rust-lld"
```
