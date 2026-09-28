# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A page through a holiday's window, run by run: its set goes up at the window's first midnight, holds on a
quiet day, checks, and comes down after, each change named in its commit; with holidays off it never goes
up, and a rainbowprint holds its colour while the set is up."""
from __future__ import annotations

import copy
import unittest

from tests.integration import test_banners_run as B

from domain.banners import sample


class Window(B.Folder):
    """Halloween at the default three days: October 30 to November 1."""

    def day(self, when: str, measurement: dict = sample.REPOSITORY) -> tuple[int, str]:
        self.msg.unlink(missing_ok=True)
        return B.run(["run", "--root", str(self.root), "--today", when, "--commit-file", str(self.msg)], measurement)

    def drawn_in_the_set(self) -> bool:
        return "<!--markdown-kit v1 halloween H2 day-->" in self.svg("header-day.svg")

    def test_the_set_goes_up_holds_checks_and_comes_down(self):
        code, out = self.day("2026-10-29")
        self.assertEqual(code, 0, out)
        self.assertFalse(self.drawn_in_the_set())
        self.assertIsNone(self.lock()["drawn"]["holiday"])

        code, out = self.day("2026-10-30")
        self.assertEqual(code, 0, out)
        self.assertIn("in the Halloween set", out)
        self.assertTrue(self.drawn_in_the_set())
        self.assertIn("<!--markdown-kit v1 halloween F1 day-->", self.svg("footer-day.svg"))
        self.assertEqual(self.lock()["drawn"]["holiday"], "halloween")
        msg = self.msg.read_text(encoding="utf-8")
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 put up the Halloween set")
        self.assertIn("The Halloween set is up from October 30 to November 1", msg.replace("\n", " "))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)

        code, out = self.day("2026-10-31")
        self.assertIn("nothing changed", out)
        self.assertFalse(self.msg.exists())

        code, out = self.day("2026-11-02")
        self.assertEqual(code, 0, out)
        self.assertFalse(self.drawn_in_the_set())
        self.assertIsNone(self.lock()["drawn"]["holiday"])
        msg = self.msg.read_text(encoding="utf-8")
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 take down the Halloween set")
        self.assertIn("drawn in blueprint again", msg.replace("\n", " "))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)

    def test_a_first_run_in_the_window_draws_the_set_and_says_so(self):
        code, out = self.day("2026-10-31")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in_the_set())
        msg = self.msg.read_text(encoding="utf-8")
        self.assertTrue(msg.startswith("chore(markdown): \U0001FAA7 draw the banners for"), msg)
        self.assertIn("The Halloween set is up", msg.replace("\n", " "))

    def test_with_holidays_off_the_set_never_goes_up(self):
        self.set("theme: blueprint\nholidays: false\n")
        self.day("2026-10-31")
        self.assertFalse(self.drawn_in_the_set())
        self.assertIsNone(self.lock()["drawn"]["holiday"])

    def test_a_longer_window_goes_up_sooner(self):
        self.set("theme: blueprint\nholiday-days: 7\n")
        self.day("2026-10-28")
        self.assertTrue(self.drawn_in_the_set())


class RainbowHolds(B.Folder):
    settings = "theme: rainbowprint\n"

    def update(self, when: str, stars: int) -> str:
        m = copy.deepcopy(sample.REPOSITORY)
        m["repository"]["stars"] = stars
        B.run(["run", "--root", str(self.root), "--today", when], m)
        return self.lock()["drawn"]["rainbow"]

    def test_the_rainbow_holds_its_colour_while_the_set_is_up_and_picks_up_after(self):
        self.assertEqual(self.update("2026-10-28", 10), "redprint")
        self.assertEqual(self.update("2026-10-30", 11), "redprint")
        self.assertEqual(self.update("2026-10-31", 12), "redprint")
        self.assertEqual(self.update("2026-11-02", 12), "redprint")
        self.assertIn(B.PALETTE[B.prints.PRINTS["redprint"]["line"]], self.svg("header-day.svg"))
        self.assertEqual(self.update("2026-11-03", 13), "orangeprint")


if __name__ == "__main__":
    unittest.main()
