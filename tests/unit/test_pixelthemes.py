# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The pixel themes: one world drawn as pixel art, a theme a page names and keeps all year. The settings take one
by its key; the page is drawn in its set every day, with no day, month's mark or sign handed to it; a holiday's set
and the Birthday set still take their days and hand the page back; and the commit says so once, by its name."""
from __future__ import annotations

import datetime as dt
import unittest
from pathlib import Path
from unittest import mock

from tests import support

from app import run as R
from app.page import settle
from domain import birthday as B
from domain import collections as C
from domain import holidays as H
from domain import pixelsets, pixelthemes as P, settings as S
from domain.holidays.designs import Holiday

KEY = "heaven-and-hell"


class TheRegistry(unittest.TestCase):
    def test_every_pixel_theme_is_drawn_by_the_set_its_key_names(self):
        self.assertTrue(P.THEMES)
        for key, theme in P.THEMES.items():
            with self.subTest(key):
                self.assertEqual(theme.key, key)
                self.assertTrue(theme.summary.endswith("."))
                self.assertTrue(P.is_drawn(key))
                held = P.drawn_by(key)
                self.assertIsInstance(held, Holiday)
                self.assertEqual((held.key, held.name), (key, theme.name))
                self.assertTrue(held.tokens)
                self.assertEqual(P.package(key), key.replace("-", "_"))
        self.assertEqual(P.themes(), list(P.THEMES))

    def test_a_pixel_theme_is_no_holiday_no_collection_and_no_print(self):
        catalogue = support.install()
        for key in P.THEMES:
            self.assertNotEqual(key, B.KEY)
            self.assertNotIn(key, H.SETS)
            self.assertIsNone(C.owner(key))
            self.assertNotIn(key, C.COLLECTIONS)
            self.assertNotIn(key, catalogue)

    def test_its_set_is_the_same_whatever_comes_after_a_colon(self):
        # A pixel theme has no calendar to be told its day by, and no hand to take a sign from.
        held = P.drawn_by(KEY)
        for after in (f"{KEY}:2026-11-01", f"{KEY}:leo", f"{KEY}:2026-11-01:leo"):
            self.assertIs(P.drawn_by(after), held, after)
        self.assertIsNone(held.day)

    def test_nothing_else_is_a_pixel_theme(self):
        for key in ("", None, "heaven", "standard", "blueprint", "medieval", "medieval-forge", "halloween", B.KEY):
            self.assertIsNone(P.drawn_by(key), key)
            self.assertFalse(P.is_drawn(key), key)
            self.assertEqual(P.name_of(key), "", key)
        self.assertFalse(P.is_theme(f"{KEY}:leo"))

    def test_a_listed_theme_whose_package_is_not_here_cannot_be_picked(self):
        with mock.patch.dict(P.THEMES, {"limbo": P.Theme("limbo", "Limbo", "Neither one nor the other.")}):
            self.assertFalse(P.is_drawn("limbo"))
            self.assertIsNone(P.drawn_by("limbo"))
            self.assertNotIn("limbo", P.themes())
            with self.assertRaises(S.SettingsError):
                S.validate({"theme": "limbo"}, None, catalogue=support.install())

    def test_it_is_named_in_words(self):
        self.assertEqual(P.name_of(KEY), "Heaven & Hell")
        self.assertEqual(P.described(KEY), "the Heaven & Hell theme")
        self.assertEqual(pixelsets.name(KEY), "the Heaven & Hell theme")
        self.assertEqual(pixelsets.drawn_by(KEY).key, KEY)


class TheSettings(unittest.TestCase):
    def test_the_settings_and_the_stub_take_a_pixel_theme_by_its_key(self):
        catalogue = support.install()
        self.assertEqual(S.validate({"theme": KEY}, None, catalogue=catalogue)["theme"], KEY)
        self.assertEqual(S.validate(None, {"theme": KEY}, catalogue=catalogue)["theme"], KEY)

    def test_an_unknown_theme_is_told_the_pixel_themes_among_the_rest(self):
        with self.assertRaises(S.SettingsError) as caught:
            S.validate({"theme": "plaid"}, None, catalogue=support.install())
        said = str(caught.exception)
        for name in ("standard", "blueprint", "rainbowprint", KEY):
            self.assertIn(name, said)


class ThePage(unittest.TestCase):
    def page(self, today: dt.date, holidays: bool = True, sign: str = "", born: dt.date | None = None,
             theme: str = KEY):
        cfg = S.validate({"theme": theme, "holidays": holidays, "sign": sign}, None, catalogue=support.install())
        return settle(Path("."), cfg, mode="repository", subject="o/r", here="o/r", today=today, lk={}, born=born)

    def test_the_page_is_drawn_in_its_set_every_day_and_in_standard_for_what_it_cannot_draw(self):
        for month in range(1, 13):
            page = self.page(dt.date(2027, month, 9), holidays=False)
            self.assertEqual((page.design, page.drawn_in, page.theme, page.rainbow, page.held),
                             (KEY, KEY, "standard", None, ""), month)
            self.assertTrue(page.pinned)
            self.assertEqual(pixelsets.drawn_by(page.drawn_in).key, KEY)

    def test_it_carries_no_sign_and_no_day(self):
        page = self.page(dt.date(2027, 3, 9), sign="leo")
        self.assertEqual(page.drawn_in, KEY)
        self.assertIsNone(pixelsets.drawn_by(page.drawn_in).day)

    def test_a_holidays_set_takes_its_days_and_hands_the_page_back(self):
        up = self.page(dt.date(2027, 10, 31))
        self.assertEqual((up.held, up.design), ("halloween", KEY))
        self.assertEqual(up.drawn_in, "halloween:2027-10-31")
        after = self.page(dt.date(2027, 11, 3))
        self.assertEqual((after.held, after.drawn_in), ("", KEY))
        kept = self.page(dt.date(2027, 10, 31), holidays=False)
        self.assertEqual((kept.held, kept.drawn_in), ("", KEY))

    def test_the_birthday_set_takes_its_day(self):
        page = self.page(dt.date(2027, 5, 9), born=dt.date(2020, 5, 9))
        self.assertEqual(page.held, B.KEY)
        self.assertTrue(page.drawn_in.startswith(f"{B.KEY}:"))
        self.assertEqual(self.page(dt.date(2027, 5, 10), born=dt.date(2020, 5, 9)).drawn_in, KEY)


class TheCommit(unittest.TestCase):
    page = ThePage.page

    def test_the_commit_says_once_that_the_page_is_drawn_in_it_all_year(self):
        page = self.page(dt.date(2027, 2, 3))
        subject, para = R._set_news(page, "", "")
        self.assertEqual(subject, "draw the page in Heaven & Hell")
        self.assertEqual(para, "The page is drawn in the Heaven & Hell theme: the banners, the badges, the elements "
                               "and the trophy case, all year.")
        self.assertEqual(R._set_news(page, "", KEY), ("", ""))
        self.assertEqual(R._set_news(self.page(dt.date(2027, 3, 1)), "", KEY), ("", ""))

    def test_the_commit_says_where_the_page_goes_when_a_holiday_comes_and_goes(self):
        up = self.page(dt.date(2027, 10, 30))
        subject, para = R._set_news(up, "", KEY)
        self.assertEqual(subject, "put up the Halloween set")
        self.assertIn("the page goes back to the Heaven & Hell theme after.", para)
        down = self.page(dt.date(2027, 11, 2))
        self.assertEqual(R._set_news(down, "halloween", KEY),
                         ("take down the Halloween set",
                          "The Halloween set is down, and the page is drawn in the Heaven & Hell theme."))

    def test_the_birthday_says_the_page_goes_back_to_it_tomorrow(self):
        page = self.page(dt.date(2027, 5, 9), born=dt.date(2020, 5, 9))
        _, para = R._set_news(page, "", KEY)
        self.assertIn("tomorrow the page is drawn in the Heaven & Hell theme again.", para)


if __name__ == "__main__":
    unittest.main()
