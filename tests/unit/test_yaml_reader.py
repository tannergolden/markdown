# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support  # noqa: F401

from infra.yaml_reader import YamlError, loads


class YamlReaderTest(unittest.TestCase):
    def test_an_empty_file_is_none(self):
        self.assertIsNone(loads(""))
        self.assertIsNone(loads("# only a comment\n\n"))

    def test_scalars_resolve_to_the_yaml_1_2_core_schema(self):
        doc = loads("a: true\nb: False\nc: null\nd: ~\ne: 42\nf: -3\ng: 1.5\nh: on\ni: no\nj: 2026-09-28\nk: 007\nl:\n")
        self.assertEqual(doc, {"a": True, "b": False, "c": None, "d": None, "e": 42, "f": -3, "g": 1.5, "h": "on",
                               "i": "no", "j": "2026-09-28", "k": "007", "l": None})

    def test_quotes_and_escapes(self):
        doc = loads("""a: 'it''s'\nb: "tab\\there \\u00e9 \\U0001F389"\nc: "a # not a comment"\nd: plain # a comment\n""")
        self.assertEqual(doc, {"a": "it's", "b": "tab\there \u00e9 \U0001F389", "c": "a # not a comment", "d": "plain"})

    def test_a_url_is_one_value(self):
        self.assertEqual(loads("site: https://example.com/a:b?c=d#frag")["site"], "https://example.com/a:b?c=d#frag")

    def test_nested_maps_and_both_list_styles(self):
        doc = loads("top:\n  inner:\n    deep: 1\n  list:\n  - a\n  - b\n  other:\n    - c\n")
        self.assertEqual(doc, {"top": {"inner": {"deep": 1}, "list": ["a", "b"], "other": ["c"]}})

    def test_a_list_of_maps(self):
        doc = loads("badges:\n  - name: a\n    label: A\n  -   name: b\n      label: B\n  -\n    name: c\n")
        self.assertEqual(doc, {"badges": [{"name": "a", "label": "A"}, {"name": "b", "label": "B"}, {"name": "c"}]})

    def test_inline_collections_nest_and_cross_lines(self):
        doc = loads("a: [1, [2, 3], {x: y, z: [4]}]\nb: {k: 'v, w', m: \"n]\"}\nc: [one,\n    two]\n")
        self.assertEqual(doc, {"a": [1, [2, 3], {"x": "y", "z": [4]}], "b": {"k": "v, w", "m": "n]"}, "c": ["one", "two"]})

    def test_blocks_of_text(self):
        doc = loads("lit: |\n  one\n    two\n\n  three\nfold: >-\n  a\n  b\n\n  c\nkeep: |+\n  x\n\nnext: 1\n")
        self.assertEqual(doc["lit"], "one\n  two\n\nthree\n")
        self.assertEqual(doc["fold"], "a b\nc")
        self.assertEqual(doc["keep"], "x\n\n")
        self.assertEqual(doc["next"], 1)

    def test_a_block_of_text_in_a_list(self):
        self.assertEqual(loads("notes:\n  - |\n    first\n  - second\n"), {"notes": ["first\n", "second"]})

    def test_quoted_text_that_runs_over_lines_is_folded(self):
        doc = loads("a: 'the page''s\n  one theme\n\n  and more' # note\nb: \"join\\\n  ed # kept\"\nc:\n  - 'x\n    y'\n")
        self.assertEqual(doc, {"a": "the page's one theme\nand more", "b": "joined # kept", "c": ["x y"]})

    def test_a_leading_document_marker_is_allowed(self):
        self.assertEqual(loads("---\na: 1\n"), {"a": 1})

    def test_crlf_line_endings(self):
        self.assertEqual(loads("a: 1\r\nb:\r\n  - x\r\n"), {"a": 1, "b": ["x"]})

    def refuses(self, text: str, words: str, line: int | None = None):
        with self.assertRaises(YamlError) as caught:
            loads(text)
        self.assertIn(words, str(caught.exception))
        if line is not None:
            self.assertEqual(caught.exception.line, line)

    def test_refuses_what_it_does_not_read_naming_the_line(self):
        self.refuses("a: 1\na: 2\n", "'a' is given twice", 2)
        self.refuses("a: &x 1\n", "anchors and aliases", 1)
        self.refuses("a: *x\n", "anchors and aliases", 1)
        self.refuses("a: !!str 1\n", "tags", 1)
        self.refuses("a:\n\t- b\n", "tab in the indentation", 2)
        self.refuses("a: 1\n---\nb: 2\n", "second document", 2)
        self.refuses("a: [1, 2\n", "never closed", 1)
        self.refuses("a: 'open\n", "never closed", 1)
        self.refuses("a: b\n  c\n", "runs on", 2)
        self.refuses("- a\nb: c\n", "cannot place", 2)
        self.refuses('a: "\\q"\n', "not an escape", 1)
        self.refuses("? complex\n", "`?` keys", 1)


if __name__ == "__main__":
    unittest.main()
