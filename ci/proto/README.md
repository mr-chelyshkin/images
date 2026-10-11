# ci/proto

Buf and clang-format for Protobuf schemas.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

- Buf is downloaded from its GitHub releases for the target architecture.
- clang-format comes from Debian packages; `CLANG_FORMAT_VERSION` pins its major
  version.
