# ci/markdown

mdformat with GitHub Flavored Markdown support.

- Variants: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.

## Notes

- `requirements.txt` locks mdformat and all its dependencies with hashes. The
  weekly rebuild keeps formatting unchanged.
- To change the formatter, edit `requirements.in`, regenerate the lock, and add
  a variant whose `MDFORMAT_VERSION` and `MDFORMAT_GFM_VERSION` match it; the
  build fails otherwise:

```sh
uv pip compile requirements.in --universal --python-version 3.14 --generate-hashes -o requirements.txt
```
