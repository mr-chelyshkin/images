"""mdformat support for named, nestable VitePress containers."""

from html import escape
import re

from markdown_it import MarkdownIt
from mdit_py_plugins.container import container_plugin
from mdformat.renderer import RenderContext, RenderTreeNode


_CONTAINER_NAME = re.compile(r"[a-z0-9_-]+(?:[ \t]|$)")
_CONTAINER_LINE = re.compile(r"^(\s*)(:{3,})[ \t]*([a-z0-9_-]+)(?:[ \t]|$)")


def update_mdit(mdit: MarkdownIt) -> None:
    mdit.use(
        container_plugin,
        "vitepress",
        validate=lambda info, _marker: bool(_CONTAINER_NAME.match(info.lstrip())),
        render=_render_html,
    )


def _render_html(_renderer, tokens, index, _options, _env) -> str:
    token = tokens[index]
    if token.nesting == 1:
        # Keep the container name/title in mdformat's semantic validation.
        info = escape(token.info.strip(), quote=True)
        return f'<div data-vitepress-container="{info}">\n'
    return "</div>\n"


def _render_container(node: RenderTreeNode, context: RenderContext) -> str:
    body = "\n\n".join(filter(None, (child.render(context) for child in node.children)))
    opening = f"{node.markup} {node.info.strip()}"
    if not body:
        return f"{opening}\n{node.markup}"
    return f"{opening}\n\n{body}\n\n{node.markup}"


def _escape_paragraph(text: str, _node: RenderTreeNode, _context: RenderContext) -> str:
    # Escaped literal markers must not become containers after formatting/wrapping.
    lines = []
    for line in text.split("\n"):
        marker = _CONTAINER_LINE.match(line)
        if marker:
            indentation = marker[1]
            line = f"{indentation}\\{line[len(indentation):]}"
        lines.append(line)
    return "\n".join(lines)


RENDERERS = {"container_vitepress": _render_container}
POSTPROCESSORS = {"paragraph": _escape_paragraph}
