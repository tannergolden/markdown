# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Localizing: reading a shields.io link, naming its file, and rewriting the documents that show it."""
from __future__ import annotations

import unittest

from tests import support

from app.parts import badges as parts
from domain.badges import classic as C
from domain.badges import localize as L

support.install()
FTB = "?style=for-the-badge"
BASE = "https://raw.githubusercontent.com/octo/site/main/assets/markdown/badges/localized/"


def shields(label: str, message: str, colour: str, query: str = FTB) -> str:
    return f"https://img.shields.io/badge/{label}-{message}-{colour}{query}"


class Parse(unittest.TestCase):
    def test_the_fields_and_the_house_icon(self):
        self.assertEqual(L.parse(shields("Status", "Active", "2EA043")),
                         {"label": "Status", "message": "Active", "label_color": "black", "message_color": "green",
                          "icon": "pulse", "style": "for-the-badge"})

    def test_escaped_dashes_and_underscores(self):
        spec = L.parse(shields("Code__Style", "Semi--Formal", "blue"))
        self.assertEqual((spec["label"], spec["message"]), ("Code_Style", "Semi-Formal"))
        self.assertEqual(L.parse(shields("Last_Commit", "Today", "green"))["label"], "Last Commit")
        self.assertEqual(L.parse(shields("A", "50%25", "green"))["message"], "50%")

    def test_colours_are_tokens_where_they_can_be(self):
        self.assertEqual(L.parse(shields("A", "B", "123456"))["message_color"], "#123456")
        self.assertEqual(L.parse(shields("A", "B", "abc"))["message_color"], "#ABC")
        for raw, tok in (("brightgreen", "green"), ("critical", "red"), ("informational", "blue"),
                         ("lightgrey", "slate"), ("mauve", "slate")):
            self.assertEqual(L.parse(shields("A", "B", raw))["message_color"], tok, raw)
        self.assertEqual(L.parse(shields("A", "B", "green", FTB + "&labelColor=C0A062"))["label_color"], "gold")

    def test_styles(self):
        for raw, style in (("plastic", "plastic"), ("social", "flat"), ("flat-square", "flat-square")):
            self.assertEqual(L.parse(shields("A", "B", "blue", f"?style={raw}"))["style"], style, raw)
        self.assertEqual(L.parse(shields("A", "B", "blue", ""))["style"], "flat")

    def test_a_badge_that_is_not_static_is_left_alone(self):
        self.assertIsNone(L.parse("https://img.shields.io/github/stars/o/r"))
        self.assertIsNone(L.parse("https://img.shields.io/badge/onlyone"))

    def test_every_parsed_badge_draws(self):
        spec = L.parse(shields("License", "MIT", "F1E05A", "?style=plastic"))
        self.assertEqual(L.draw(spec), C.render("License", "MIT", "black", "yellow", "scale", "plastic") + "\n")


class Names(unittest.TestCase):
    def test_a_name_is_its_label_and_message(self):
        spec = L.parse(shields("Code Style", "Semi Formal!", "blue"))
        self.assertEqual(L.base_name(spec), "code-style-semi-formal")

    def test_two_badges_that_would_share_a_name_each_get_a_hash(self):
        a, b = L.parse(shields("A", "B", "green")), L.parse(shields("A", "B", "red"))
        names = L.names([a, b, a])
        self.assertEqual(len(names), 2)
        self.assertTrue(all(n.startswith("a-b-") and len(n) == len("a-b-123456.svg") for n in names.values()))

    def test_a_new_badge_never_takes_the_name_of_one_drawn_before(self):
        drawn, new = L.parse(shields("A", "B", "green")), L.parse(shields("A", "B", "red"))
        names = L.names([new, drawn], taken={"a-b.svg": drawn})
        self.assertEqual(names[L.signature(drawn)], "a-b.svg", "the one drawn before keeps its file")
        self.assertNotEqual(names[L.signature(new)], "a-b.svg")

    def test_every_way_a_document_points_at_a_file_is_found(self):
        pattern = L.references("assets/markdown/badges/localized")
        for ref in ("assets/markdown/badges/localized/a-b.svg", "../../assets/markdown/badges/localized/a-b.svg",
                    "/assets/markdown/badges/localized/a-b.svg", "./assets/markdown/badges/localized/a-b.svg",
                    "https://raw.githubusercontent.com/o/r/feature/x/assets/markdown/badges/localized/a-b.svg"):
            self.assertEqual(pattern.fullmatch(ref).group(1), "a-b.svg", ref)
        self.assertIsNone(pattern.search("assets/markdown/badges/static/a-b.svg"))


class Rewrite(unittest.TestCase):
    def test_whole_urls_only(self):
        short, long = shields("A", "B", "green", ""), shields("A", "B", "green", "?style=plastic")
        text = f"![a]({short}) ![b]({long})"
        new = L.rewrite(text, {short: "a-b.svg"}, BASE, L.references("x"), keep=False)
        self.assertEqual(new, f"![a]({BASE}a-b.svg) ![b]({long})")


class Plan(unittest.TestCase):
    """The app's plan for a repository's Markdown, from the settings and the lock's record."""

    def plan(self, docs, record=None, on=True, here="octo/site"):
        return parts.localize(docs, record or {}, on=on, here=here, branch="main", out="assets/markdown",
                              readme="README.md")

    def test_identical_badges_share_one_file_and_every_link_is_absolute(self):
        url = shields("Status", "Active", "2EA043")
        p = self.plan({"docs/a.md": f"![Status]({url})\n", "docs/b.md": f"[![Status]({url})](./)\n"})
        self.assertEqual(list(p["files"]), ["assets/markdown/badges/localized/status-active.svg"])
        self.assertEqual(p["texts"], {"docs/a.md": f"![Status]({BASE}status-active.svg)\n",
                                      "docs/b.md": f"[![Status]({BASE}status-active.svg)](./)\n"})
        self.assertEqual(p["record"], {"status-active.svg": L.parse(url)})

    def test_the_readme_keeps_its_relative_links_and_the_rest_are_made_absolute(self):
        rel = "assets/markdown/badges/localized/a-b.svg"
        record = {"a-b.svg": L.parse(shields("A", "B", "green"))}
        p = self.plan({"README.md": f"![x]({rel})\n", "docs/a.md": f"![x](../{rel})\n"}, record)
        self.assertEqual(p["texts"], {"docs/a.md": f"![x]({BASE}a-b.svg)\n"})
        self.assertEqual(p["record"], record, "a badge still shown is kept")

    def test_a_badge_no_document_shows_is_dropped_and_one_nobody_recorded_is_kept_as_it_is(self):
        record = {"a-b.svg": L.parse(shields("A", "B", "green"))}
        p = self.plan({"docs/a.md": "![x](assets/markdown/badges/localized/c-d.svg)\n"}, record)
        self.assertEqual((p["files"], p["record"]), ({}, {}))
        self.assertEqual(p["keep"], ["assets/markdown/badges/localized/c-d.svg"])
        self.assertIn("no record of drawing it", p["notes"][0])

    def test_off_it_rewrites_nothing_new_but_keeps_what_it_drew(self):
        url = shields("A", "B", "green")
        record = {"a-b.svg": L.parse(url)}
        docs = {"docs/a.md": f"![x]({BASE}a-b.svg) ![y]({shields('C', 'D', 'red')})\n"}
        p = self.plan(docs, record, on=False)
        self.assertEqual((p["texts"], list(p["files"])), ({}, ["assets/markdown/badges/localized/a-b.svg"]))

    def test_a_second_pass_changes_nothing(self):
        url = shields("Status", "Active", "2EA043")
        first = self.plan({"docs/a.md": f"![s]({url})\n"})
        again = self.plan(first["texts"], first["record"])
        self.assertEqual((again["texts"], again["files"], again["record"]),
                         ({}, first["files"], first["record"]))

    def test_an_endpoint_it_cannot_draw_is_named(self):
        p = self.plan({"docs/a.md": "![s](https://img.shields.io/badge/onlyone)\n"})
        self.assertIn("docs/a.md: left https://img.shields.io/badge/onlyone as it is", p["notes"][0])

    def test_without_knowing_the_repository_it_rewrites_nothing(self):
        p = self.plan({"docs/a.md": f"![s]({shields('A', 'B', 'green')})\n"}, here="")
        self.assertEqual((p["texts"], p["files"]), ({}, {}))
        self.assertIn("cannot tell which repository", p["notes"][0])


if __name__ == "__main__":
    unittest.main()
