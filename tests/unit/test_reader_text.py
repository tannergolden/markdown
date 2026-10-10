# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What a file says to a reader is text, and the lint reads it as text.

A file's title, description and labels often come from the page itself: a placard's description is a
GitHub issue's title, a badge says what its settings say. The lint once read that text as markup, so a
good first issue numbered #681 read as a colour off the palette and failed the run that drew it, as did a
dash or a sentence that mentions javascript:. Markup is still held to every rule; the text is not, and a
dash in it is set as a hyphen, since no file the kit draws carries one.
"""
from __future__ import annotations

import unittest

from tests import support

from domain import collections, holidays as H
from domain.badges import data as BD
from domain.canvas import BUDGET, Canvas, c, lint, prose
from domain.elements import data as ED

support.install()

# The dashes by code point, so this file never carries one.
EN, EM = "–", "—"
SAYS = {
    "an issue number that reads as a colour": "#681: [Proposal]: normalize the links",
    "a six-figure issue number": "#123456: crash on start",
    "a word that reads as a colour": "#BAD request on save",
    "an em dash": f"Fix the build {EM} again",
    "an en dash": f"Pages 1{EN}2 render blank",
    "a scheme a script would use": "Links that start javascript: are blocked",
    "a reference outside the file": 'Load url(https://example.com/a.png) or src="x"',
    "words a paint reads like": "Set fill: red; color: blue on the card",
}


def placard(desc: str) -> dict:
    return ED.merged(ED.check({"pick": {"kind": "placard", "owner": "octo", "name": "repo", "icon": "flag",
                                        "link": "https://github.com/octo/repo/issues/681", "desc": desc,
                                        "cells": [["Stars", "1K"], ["Language", "PYTHON"], ["Opened", "3 OCT"]]}}),
                     {}, subject="octo/octo", today="2026-10-07")


class TheLint(unittest.TestCase):
    def file(self, title: str, desc: str) -> str:
        cv = Canvas(200, 40, title=title, desc=desc, stamp="test")
        cv.add(f'<rect width="200" height="40" fill="{c("navy")}"/>')
        return cv.svg()

    def test_reads_a_title_and_description_as_text(self):
        for what, text in SAYS.items():
            with self.subTest(what):
                self.assertEqual(lint(self.file(text, text), budget=BUDGET["header"]), [])

    def test_still_refuses_the_same_things_in_markup(self):
        base = self.file("A title", "A description.")
        for body, words in (('<rect fill="#681"/>', "#681 is not a palette token"), ("<script>x()</script>", "<script"),
                            ('<image href="https://x.y/a.png"/>', "outside the file"), (f"<g>{EM}</g>", "dash")):
            with self.subTest(body):
                problems = lint(base.replace("</svg>", body + "</svg>"), budget=BUDGET["header"])
                self.assertTrue(any(words in p for p in problems), problems)

    def test_sets_a_dash_in_what_it_says_as_a_hyphen(self):
        svg = self.file(f"Fast {EM} and small", f"Pages 1{EN}2.")
        self.assertIn("Fast - and small", svg)
        self.assertIn("Pages 1-2.", svg)
        self.assertNotIn(EM, svg)
        self.assertEqual(prose(f"a{EN}b{EM}c"), "a-b-c")


class TheDrawings(unittest.TestCase):
    def test_a_placard_draws_whatever_its_issue_says(self):
        for what, text in SAYS.items():
            for tone in ("standard", "blueprint"):
                with self.subTest(what, tone=tone):
                    files = ED.render(placard(text), tone)
                    self.assertTrue(files)
                    self.assertFalse(any(EM in svg or EN in svg for svg in files.values()))

    def test_every_pixel_set_draws_it_too(self):
        # Every holiday's set, and every collection's design drawn so far.
        designs = [k for c in collections.COLLECTIONS.values() for k in c.keys if collections.is_drawn(k)]
        for key in [*H.SETS, *designs]:
            for what in ("an issue number that reads as a colour", "an em dash", "a scheme a script would use"):
                with self.subTest(key, what=what):
                    files = ED.render(placard(SAYS[what]), "standard", key)
                    self.assertTrue(files)
                    self.assertFalse(any(EM in svg for svg in files.values()))

    def test_a_badge_says_it_too(self):
        # A plate letters its message, and its lettering has no dash: a message typed with one is refused
        # with a sentence saying so before anything is drawn, so a plate is held only to the colour words.
        for theme, says in (("standard", ("an issue number that reads as a colour", "an em dash",
                                          "a word that reads as a colour")),
                            ("blueprint", ("an issue number that reads as a colour", "a word that reads as a colour"))):
            for what in says:
                with self.subTest(theme, what=what):
                    b = {"name": "note", "label": "Note", "message": SAYS[what], "icon": "info"}
                    files = BD.draw(b, {}, theme=theme, shade=None, seed="2026W40")
                    self.assertTrue(files)
                    self.assertFalse(any(EM in svg for svg in files.values()))


if __name__ == "__main__":
    unittest.main()
