# ci/python

Python with uv for locked project environments and package builds.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

- Python comes from the official `python` base image.
- uv is copied from the official uv image; the build checks both versions
  against `variants.yaml`.
