# ci/markdown

mdformat with GitHub Flavored Markdown support.

| Variant | Additional support | Dependency lock |
| -- | -- | -- |
| `1.0.0` | GFM | `requirements.txt` |
| `1.1.0` | GFM, YAML frontmatter, VitePress containers | `requirements-vitepress.txt` |

- Versions and build arguments: [`variants.yaml`](variants.yaml).
- Installed versions: `cat /etc/ci-image` inside the image.
- All external packages are locked with hashes. Weekly rebuilds keep their
  versions.

## VitePress support

`1.1.0` installs `mdformat-frontmatter` and the local
[`mdformat-vitepress`](vitepress/) plugin. The CLI loads both automatically. The
plugin formats named `:::` containers, including nested `::::` containers,
custom titles, and `code-group`. Fenced code examples remain literal; include
comments and Vue/HTML blocks are preserved.

Both variants keep mdformat and GFM at the same versions. The original lock is
unchanged; the extra packages and local plugin are installed only in `1.1.0`.
The plugin wheel is built in a separate stage with `requirements-build.txt`; the
build backend is not installed in the final image. The build checks package
versions and runs the plugin tests for `1.1.0`.

## Updating dependencies

Run from `ci/markdown/` after editing the corresponding `.in` file:

```sh
uv pip compile requirements.in --universal --python-version 3.14 --generate-hashes -o requirements.txt
uv pip compile requirements-vitepress.in --universal --python-version 3.14 --generate-hashes -o requirements-vitepress.txt
uv pip compile requirements-build.in --universal --python-version 3.14 --generate-hashes -o requirements-build.txt
```

Keep the variant build arguments and the local plugin version in
`vitepress/pyproject.toml` in sync with the locks. Plugin behavior tests live in
`vitepress/tests/`.
