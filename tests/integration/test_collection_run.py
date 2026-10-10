# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A page in a collection, run by run: drawn in the month's design, the next design taking over on the first
of the month and named in its commit, a holiday's set still taking over and handing back to the month's
design, a named design kept all year, and a collection still being drawn refused. A page on the collection's
calendar carries the month's mark in every header, and a page that keeps one design all year carries none,
unless the page chose a sign, which it carries either way."""
from __future__ import annotations

import unittest

from tests.integration import test_banners_run as B
from tests.unit import test_collection_hand as TH
from tests.unit import test_collections as T

from domain.banners import sample


class Collection(B.Folder):
    settings = "theme: standin\n"
    drawn = 12

    def setUp(self):
        for p in T.stand_in(self.drawn):
            p.start()
            self.addCleanup(p.stop)
        super().setUp()

    def day(self, when: str) -> tuple[int, str]:
        self.msg.unlink(missing_ok=True)
        return B.run(["run", "--root", str(self.root), "--today", when, "--commit-file", str(self.msg)],
                     sample.REPOSITORY)

    def drawn_in(self, design: str) -> bool:
        """Whether the header is drawn by the package the stand-in's design borrows."""
        key = T.borrowed(design).replace("_", "-")
        return f"<!--markdown-kit v1 {key} H2 day-->" in self.svg("header-day.svg")

    def message(self) -> str:
        return self.msg.read_text(encoding="utf-8")


class AMonthTurns(Collection):
    def test_the_months_design_draws_the_page_and_the_next_takes_over_on_the_first(self):
        code, out = self.day("2026-03-31")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in("standin-march"))
        drawn = self.lock()["drawn"]
        self.assertEqual((drawn["theme"], drawn["design"], drawn["holiday"]), ("standin", "standin-march", None))
        self.assertIn("in Design 3, from the standin collection", out)
        self.assertIn("It is March, so the page is drawn in Design 3", self.message().replace("\n", " "))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)

        code, out = self.day("2026-04-01")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in("standin-april"))
        self.assertEqual(self.lock()["drawn"]["design"], "standin-april")
        msg = self.message()
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 draw April's standin design, Design 4")
        self.assertIn("On May 1 the next design takes over.", msg.replace("\n", " "))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)

        code, out = self.day("2026-04-02")
        self.assertIn("nothing changed", out)
        self.assertFalse(self.msg.exists())

    def test_a_holidays_set_still_takes_over_and_hands_back_to_the_months_design(self):
        self.day("2026-10-29")
        self.assertTrue(self.drawn_in("standin-october"))

        code, out = self.day("2026-10-30")
        self.assertEqual(code, 0, out)
        self.assertIn("<!--markdown-kit v1 halloween H2 day-->", self.svg("header-day.svg"))
        self.assertEqual(self.lock()["drawn"]["holiday"], "halloween")
        msg = self.message()
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 put up the Halloween set")
        self.assertIn("goes back to Design 10, the standin collection's October design after",
                      msg.replace("\n", " "))

        code, out = self.day("2026-11-02")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in("standin-november"))
        msg = self.message()
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 take down the Halloween set")
        self.assertIn("drawn in Design 11, the standin collection's November design.", msg.replace("\n", " "))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)


class ANamedDesign(Collection):
    settings = "theme: standin-march\n"

    def test_a_page_that_names_a_design_keeps_it_all_year(self):
        code, out = self.day("2026-03-15")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in("standin-march"))
        self.assertIn("The page is drawn in Design 3, from the standin collection", self.message().replace("\n", " "))
        header = self.svg("header-day.svg")
        code, out = self.day("2026-09-15")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.svg("header-day.svg"), header)
        self.assertEqual(self.lock()["drawn"]["design"], "standin-march")


class StillBeingDrawn(Collection):
    drawn = 5

    def test_a_collection_still_being_drawn_is_refused_with_the_reason(self):
        code, out = self.day("2026-03-15")
        self.assertEqual(code, 2, out)
        self.assertIn("theme: standin is a collection still being drawn, with 5 of its 12 designs done", out)


class TheMonthsMark(B.Folder):
    """The medieval collection in November, in the hand: the month's design is Forge."""
    settings = "theme: medieval\n"
    HEADERS = ("header-day.svg", "header-dark.svg", "header-still-day.svg", "header-still-dark.svg",
               "header-narrow-day.svg", "header-narrow-dark.svg")

    def run_on(self, when: str) -> tuple[int, str]:
        return B.run(["run", "--root", str(self.root), "--today", when, "--commit-file", str(self.msg)],
                     sample.REPOSITORY)

    def marked(self, name: str) -> bool:
        """Whether a header file carries the November mark, whole, at its top centre."""
        svg = self.svg(name)
        return all(part in svg for part in TH.markup(180 if "narrow" in name else 415, 11))

    def test_a_page_on_the_calendar_carries_the_mark_in_every_header_and_check_agrees(self):
        code, out = self.run_on("2026-11-10")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.lock()["drawn"]["design"], "medieval-forge")
        for name in self.HEADERS:
            self.assertIn("<!--markdown-kit v1 medieval-forge H2 ", self.svg(name), name)
            self.assertTrue(self.marked(name), name)
        self.assertFalse(any(part in self.svg("footer-day.svg") for part in TH.markup(415, 11)))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)
        code, out = self.run_on("2026-11-11")
        self.assertIn("nothing changed", out)

    def test_a_page_that_chose_a_sign_carries_it_kept_all_year_and_on_the_calendar_and_check_agrees(self):
        for settings in ("theme: medieval-forge\nsign: leo\n", "theme: medieval\nsign: Leo\n"):
            self.set(settings)
            code, out = self.run_on("2026-11-10")
            self.assertEqual(code, 0, out)
            for name in self.HEADERS:
                svg, width = self.svg(name), 180 if "narrow" in name else 415
                self.assertIn("<!--markdown-kit v1 medieval-forge H2 ", svg, (settings, name))
                self.assertTrue(all(part in svg for part in TH.markup(width, 7)), (settings, name, "Leo's"))
                self.assertFalse(all(part in svg for part in TH.markup(width, 11)), (settings, name, "not November's"))
            self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0, settings)

    def test_a_page_that_keeps_one_design_all_year_carries_none_and_check_agrees(self):
        self.set("theme: medieval-forge\n")
        code, out = self.run_on("2026-11-10")
        self.assertEqual(code, 0, out)
        for name in self.HEADERS:
            self.assertIn("<!--markdown-kit v1 medieval-forge H2 ", self.svg(name), name)
            self.assertFalse(any(part in self.svg(name) for part in TH.markup(180 if "narrow" in name else 415, 11)),
                             name)
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)


if __name__ == "__main__":
    unittest.main()
