"""Behavior tests without installing or modifying the development environment."""

import unittest
from unittest.mock import patch

import mdformat
from mdformat import plugins

import mdformat_vitepress


class ContainerFormattingTests(unittest.TestCase):
    def format(self, text, wrap=80):
        with patch.dict(plugins.PARSER_EXTENSIONS, vitepress=mdformat_vitepress):
            return mdformat.text(text, extensions={"gfm", "vitepress"}, options={"wrap": wrap})

    def assert_stable(self, source):
        formatted = self.format(source)
        self.assertEqual(self.format(formatted), formatted)
        return formatted

    def test_container_without_blank_lines_keeps_name_title_and_content(self):
        formatted = self.assert_stable("::: warning Read this\nA warning.\n:::\n")
        self.assertEqual(formatted, "::: warning Read this\n\nA warning.\n\n:::\n")

    def test_nested_container_markers_remain_distinct(self):
        source = ":::: info Requirements\n::: code-group\n```sh [Mac]\necho yes\n```\n:::\n::::\n"
        formatted = self.assert_stable(source)
        self.assertTrue(formatted.startswith(":::: info Requirements\n"))
        self.assertIn("::: code-group\n", formatted)
        self.assertIn("```sh [Mac]\necho yes\n```", formatted)
        self.assertTrue(formatted.endswith(":::\n\n::::\n"))

    def test_unknown_custom_name_does_not_need_a_formatter_allowlist(self):
        formatted = self.assert_stable("::: custom-panel A title\nCustom content.\n:::\n")
        self.assertTrue(formatted.startswith("::: custom-panel A title\n"))
        self.assertIn("Custom content.", formatted)

    def test_container_body_is_formatted(self):
        formatted = self.format("::: tip\n" + "word " * 25 + "\n:::\n", wrap=40)
        body = formatted.split("\n\n")[1]
        self.assertTrue(all(len(line) <= 40 for line in body.splitlines()))
        self.assertIn("\n", body)

    def test_literal_containers_inside_fences_stay_literal(self):
        source = "````markdown\n::: warning\n```sh\necho yes\n```\n:::\n````\n"
        self.assertEqual(self.assert_stable(source), source)

    def test_escaped_container_marker_stays_literal(self):
        formatted = self.assert_stable("\\::: warning This is literal.\n")
        self.assertTrue(formatted.startswith("\\::: warning"))

    def test_include_and_vue_components_pass_through(self):
        source = "::: details Example\n<!-- @include: ../.reference/cli.md#usage -->\n\n<ThemeGallery />\n\n<div class=\"sample\">\n  <CustomComponent :active=\"true\" />\n</div>\n:::\n"
        formatted = self.assert_stable(source)
        self.assertIn("<!-- @include: ../.reference/cli.md#usage -->", formatted)
        self.assertIn("<ThemeGallery />", formatted)
        self.assertIn('<CustomComponent :active="true" />', formatted)

    def test_container_can_be_nested_in_list_and_blockquote(self):
        for source in [
            "- Item\n\n  ::: tip\n  Body.\n  :::\n",
            "> ::: info\n> Body.\n> :::\n",
        ]:
            with self.subTest(source=source):
                self.assertIn("Body.", self.assert_stable(source))


if __name__ == "__main__":
    unittest.main()
