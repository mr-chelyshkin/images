# ci/nix

Nix with nixfmt, statix, and deadnix.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

The image enables `nix-command` and flakes. Its `NIXPKGS_REV` build argument
pins the formatter and linters; project dependencies remain controlled by the
project's own lock file.

Run Nix commands as the image's default user (`root` inside the container) to
allow writes to `/nix`.

The standalone `nixfmt`, `statix`, and `deadnix` commands also support running
with `--user "$(id -u):$(id -g)"`. Use that mode for formatting files in a
writable bind mount.

```sh
docker run --rm --init \
  --security-opt no-new-privileges --cap-drop ALL \
  --volume "$PWD:/workspace:ro" \
  --workdir /workspace \
  ghcr.io/mr-chelyshkin/ci/nix:2.35.2 \
  nix flake check --no-build --no-write-lock-file
```
