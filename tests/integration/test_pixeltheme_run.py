# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A page in a pixel theme, run by run: drawn in its set every day of the year and said so once in its commit,
a holiday's set still taking over and handing the page back, the lock remembering it, and `check` agreeing with
what was drawn; a sign the settings name carries nowhere, for a pixel theme has no month to mark."""
from __future__ import annotations

import unittest

from tests.integration import test_banners_run as B
from tests.unit import test_collection_hand as TH

from domain.banners import sample

KEY = "heaven-and-hell"


class PixelTheme(B.Folder):
    settings = f"theme: {KEY}\n"
    HEADERS = ("header-day.svg", "header-dark.svg", "header-still-day.svg", "header-still-dark.svg",
               "header-narrow-day.svg", "header-narrow-dark.svg")

    def day(self, when: str) -> tuple[int, str]:
        self.msg.unlink(missing_ok=True)
        return B.run(["run", "--root", str(self.root), "--today", when, "--commit-file", str(self.msg)],
                     sample.REPOSITORY)

    def drawn_in(self, key: str) -> bool:
        return f"<!--markdown-kit v1 {key} H2 day-->" in self.svg("header-day.svg")

    def message(self) -> str:
        return self.msg.read_text(encoding="utf-8")

    def test_the_page_is_drawn_in_it_all_year_and_the_commit_says_so_once(self):
        code, out = self.day("2026-03-15")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in(KEY))
        drawn = self.lock()["drawn"]
        self.assertEqual((drawn["theme"], drawn["design"], drawn["holiday"]), (KEY, KEY, None))
        msg = self.message().replace("\n", " ")
        self.assertIn("The page is drawn in the Heaven & Hell theme: the banners, the badges and the elements, all "
                      "year.", msg)
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)
        header = self.svg("header-day.svg")
        code, out = self.day("2026-09-15")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.svg("header-day.svg"), header)
        self.assertNotIn("Heaven & Hell", self.message() if self.msg.exists() else "")

    def test_a_holidays_set_still_takes_over_and_hands_the_page_back(self):
        self.day("2026-10-29")
        self.assertTrue(self.drawn_in(KEY))
        code, out = self.day("2026-10-30")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in("halloween"))
        self.assertEqual(self.lock()["drawn"]["holiday"], "halloween")
        msg = self.message().replace("\n", " ")
        self.assertIn("put up the Halloween set", msg)
        self.assertIn("the page goes back to the Heaven & Hell theme after.", msg)
        code, out = self.day("2026-11-02")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.drawn_in(KEY))
        self.assertIn("The Halloween set is down, and the page is drawn in the Heaven & Hell theme.",
                      self.message().replace("\n", " "))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)

    def test_a_sign_is_carried_nowhere_and_check_agrees(self):
        self.set(f"theme: {KEY}\nsign: leo\n")
        code, out = self.day("2026-11-10")
        self.assertEqual(code, 0, out)
        for name in self.HEADERS:
            svg, width = self.svg(name), 180 if "narrow" in name else 415
            self.assertIn(f"<!--markdown-kit v1 {KEY} H2 ", svg, name)
            for month in (7, 11):
                self.assertFalse(all(part in svg for part in TH.markup(width, month)), (name, month))
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)


if __name__ == "__main__":
    unittest.main()
