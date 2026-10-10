# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The collections: twelve designs to a collection, one for each month, picked by the page's own day; a
collection still being drawn cannot be picked; a holiday's set still takes over; the trophies stay standard;
and the commit says when a month's design takes over."""
from __future__ import annotations

import datetime as dt
import unittest
from pathlib import Path
from unittest import mock

from tests import support

from app import run as R
from app.page import settle
from domain import collections as C, pixelsets, settings as S
from domain.holidays.designs import Holiday

# The designs drawn so far, which a stand-in collection borrows twelve times over: a collection is complete
# only with twelve, so the stand-in is how these tests draw one before any real collection is finished.
DRAWN = [k for c in C.COLLECTIONS.values() for k in c.keys if C.is_drawn(k)]
STAND_IN = C.Collection("standin", "Stand-in", tuple((f"standin-{m.lower()}", f"Design {i + 1}")
                                                     for i, m in enumerate(C.MONTHS)))


PACKAGE = C.package


def borrowed(design: str) -> str:
    """The package a stand-in design is drawn by: the drawn designs, by turns, January's first."""
    if design in STAND_IN.keys:
        return PACKAGE(DRAWN[STAND_IN.keys.index(design) % len(DRAWN)])
    return PACKAGE(design)


def stand_in(drawn: int = 12):
    """Patches that make `standin` a collection with its first `drawn` designs drawn."""
    designs = STAND_IN.designs[:drawn] + tuple((f"{k}-unmade", n) for k, n in STAND_IN.designs[drawn:])
    real = C.Collection("standin", "Stand-in", designs)
    return [mock.patch.object(C, "COLLECTIONS", {"standin": real}), mock.patch.object(C, "package", borrowed)]


class Patched(unittest.TestCase):
    drawn = 12

    def setUp(self):
        for p in stand_in(self.drawn):
            p.start()
            self.addCleanup(p.stop)


class TheRegistry(unittest.TestCase):
    def test_every_collection_has_twelve_designs_one_for_each_month(self):
        self.assertEqual(len(C.MONTHS), 12)
        for c in C.COLLECTIONS.values():
            with self.subTest(c.key):
                self.assertEqual(len(c.designs), 12)
                self.assertEqual(len(set(c.keys)), 12)
                self.assertEqual(len({n for _, n in c.designs}), 12)
                for key in c.keys:
                    self.assertTrue(key.startswith(f"{c.key}-"), key)
                    self.assertEqual(c.month_of(key), c.keys.index(key) + 1)

    def test_every_drawn_design_is_the_set_its_key_names(self):
        self.assertTrue(DRAWN)
        for key in DRAWN:
            with self.subTest(key):
                held = C.drawn_by(key)
                self.assertIsInstance(held, Holiday)
                self.assertEqual((held.key, held.name), (key, C.name_of(key)))
                self.assertEqual(pixelsets.drawn_by(key), held)
                # What the collection's page says about it.
                self.assertTrue(held.tagline and held.about, key)
                self.assertFalse(any(dash in held.tagline + held.about for dash in "\u2013\u2014"), key)

    def test_a_design_is_drawn_as_the_months_with_a_day_and_kept_all_year_without_one(self):
        key = DRAWN[0]
        kept = C.drawn_by(key)
        self.assertIsNone(kept.day)
        month = C.drawn_by(f"{key}:2026-11-01")
        self.assertEqual((month.key, month.day), (key, dt.date(2026, 11, 1)))
        self.assertIsNone(kept.day, "handing a design a day leaves the design itself alone")
        # Every function that takes a design's key takes it with a day too.
        dated = f"{key}:2026-11-01"
        self.assertEqual((C.bare(dated), C.package(dated), C.owner(dated), C.is_drawn(dated)),
                         (key, C.package(key), C.owner(key), True))
        self.assertEqual((C.name_of(dated), C.described(dated), C.described(dated, month=True)),
                         (C.name_of(key), C.described(key), C.described(key, month=True)))
        self.assertEqual(C.owner(key).month_of(dated), C.owner(key).month_of(key))
        self.assertIsNone(C.drawn_by("medieval-nonesuch:2026-11-01"))
        # And with the sign a page chose, last, after the day of a page on the calendar.
        for signed in (f"{key}:leo", f"{key}:2026-11-01:leo"):
            self.assertEqual((C.bare(signed), C.package(signed), C.owner(signed), C.is_drawn(signed)),
                             (key, C.package(key), C.owner(key), True))
        held = C.drawn_by(f"{key}:2026-11-01:leo")
        self.assertEqual((held.key, held.day, held.sign), (key, dt.date(2026, 11, 1), "leo"))
        self.assertEqual((C.drawn_by(f"{key}:leo").day, C.drawn_by(f"{key}:leo").sign), (None, "leo"))
        self.assertEqual(kept.sign, "", "handing a design a sign leaves the design itself alone")

    def test_nothing_else_is_a_design(self):
        for key in ("", None, "standard", "blueprint", "halloween", "medieval", "medieval-nonesuch"):
            self.assertIsNone(C.drawn_by(key), key)
            self.assertFalse(C.is_drawn(key or ""), key)
        self.assertEqual(C.design_for("blueprint", dt.date(2026, 5, 1)), "")

    def test_a_collection_is_picked_only_once_all_twelve_are_drawn(self):
        for c in C.COLLECTIONS.values():
            self.assertEqual(C.is_theme(c.key), C.drawn(c.key) == 12)
            self.assertEqual(c.key in C.themes(), C.drawn(c.key) == 12)


class StillBeingDrawn(Patched):
    drawn = 7

    def test_neither_it_nor_any_of_its_designs_can_be_picked(self):
        self.assertFalse(C.complete("standin"))
        self.assertEqual(C.drawn("standin"), 7)
        self.assertEqual(C.themes(), [])
        for theme in ("standin", "standin-january", "standin-december-unmade"):
            self.assertFalse(C.is_theme(theme), theme)
            self.assertEqual(C.design_for(theme, dt.date(2026, 1, 15)), "")
        self.assertEqual(C.unfinished("standin"), "standin is a collection still being drawn, with 7 of its 12 "
                                                   "designs done")
        self.assertEqual(C.unfinished("standin-march"), C.unfinished("standin"))
        self.assertEqual(C.unfinished("blueprint"), "")

    def test_the_settings_say_so(self):
        with self.assertRaises(S.SettingsError) as caught:
            S.validate({"theme": "standin"}, None, catalogue=support.install())
        self.assertIn("theme: standin is a collection still being drawn, with 7 of its 12 designs done",
                      str(caught.exception))


class Complete(Patched):
    def test_each_month_is_drawn_in_its_design_from_its_first_day_to_its_last(self):
        self.assertTrue(C.complete("standin"))
        self.assertEqual(C.themes(), ["standin"])
        for month in range(1, 13):
            first = dt.date(2027, month, 1)
            last = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
            for day in (first, first.replace(day=15), last):
                self.assertEqual(C.design_for("standin", day), STAND_IN.keys[month - 1], day)
        self.assertEqual(C.design_for("standin", dt.date(2027, 1, 31)), "standin-january")
        self.assertEqual(C.design_for("standin", dt.date(2027, 2, 1)), "standin-february")
        self.assertEqual(C.design_for("standin", dt.date(2027, 12, 31)), "standin-december")
        self.assertEqual(C.design_for("standin", dt.date(2028, 1, 1)), "standin-january")

    def test_a_page_that_names_a_design_keeps_it_all_year(self):
        for month in range(1, 13):
            self.assertEqual(C.design_for("standin-march", dt.date(2027, month, 9)), "standin-march")

    def test_the_settings_take_the_collection_or_one_of_its_designs(self):
        catalogue = support.install()
        self.assertEqual(S.validate({"theme": "standin"}, None, catalogue=catalogue)["theme"], "standin")
        self.assertEqual(S.validate(None, {"theme": "standin-june"}, catalogue=catalogue)["theme"], "standin-june")
        with self.assertRaises(S.SettingsError) as caught:
            S.validate({"theme": "plaid"}, None, catalogue=catalogue)
        self.assertIn("standin", str(caught.exception))

    def page(self, theme: str, today: dt.date, holidays: bool = True, sign: str = ""):
        cfg = S.validate({"theme": theme, "holidays": holidays, "sign": sign}, None, catalogue=support.install())
        return settle(Path("."), cfg, mode="repository", subject="o/r", here="o/r", today=today, lk={})

    def test_the_page_is_drawn_in_the_months_design_with_the_trophies_standard(self):
        page = self.page("standin", dt.date(2027, 3, 9))
        self.assertEqual((page.design, page.drawn_in, page.theme, page.rainbow),
                         ("standin-march", "standin-march:2027-03-09", "standard", None))
        self.assertFalse(page.pinned)
        self.assertTrue(self.page("standin-march", dt.date(2027, 8, 9)).pinned)
        held = pixelsets.drawn_by(page.drawn_in)
        self.assertEqual((held.key, held.day), (DRAWN[2 % len(DRAWN)], dt.date(2027, 3, 9)))

    def test_a_page_on_the_calendar_hands_its_design_the_day_and_a_page_that_keeps_one_does_not(self):
        # The day tells the design it is drawn as the month's, which gives its headers the month's mark.
        on = self.page("standin", dt.date(2027, 3, 9))
        self.assertEqual(on.drawn_in, "standin-march:2027-03-09")
        self.assertEqual(pixelsets.drawn_by(on.drawn_in).day, dt.date(2027, 3, 9))
        kept = self.page("standin-march", dt.date(2027, 8, 9))
        self.assertEqual((kept.design, kept.drawn_in), ("standin-march", "standin-march"))
        self.assertIsNone(pixelsets.drawn_by(kept.drawn_in).day)
        # A holiday's set is told its own day, as it always was.
        held = self.page("standin", dt.date(2027, 10, 31))
        self.assertEqual(held.drawn_in, "halloween:2027-10-31")
        self.assertEqual(pixelsets.drawn_by(held.drawn_in).day, dt.date(2027, 10, 31))

    def test_a_page_that_chose_a_sign_hands_it_to_its_design_whichever_way_it_is_drawn(self):
        # The sign comes last, after the day of a page on the calendar, and the design carries it in place of the
        # month's.
        on = self.page("standin", dt.date(2027, 3, 9), sign="Leo")
        self.assertEqual(on.drawn_in, "standin-march:2027-03-09:leo")
        held = pixelsets.drawn_by(on.drawn_in)
        self.assertEqual((held.day, held.sign, held.mark_month), (dt.date(2027, 3, 9), "leo", 7))
        kept = self.page("standin-march", dt.date(2027, 8, 9), sign="leo")
        self.assertEqual(kept.drawn_in, "standin-march:leo")
        held = pixelsets.drawn_by(kept.drawn_in)
        self.assertEqual((held.day, held.sign, held.mark_month), (None, "leo", 7))
        # A holiday's set carries no sign, and a page in another theme has no design to hand one to.
        self.assertEqual(self.page("standin", dt.date(2027, 10, 31), sign="leo").drawn_in, "halloween:2027-10-31")
        self.assertEqual(self.page("blueprint", dt.date(2027, 3, 9), sign="leo").drawn_in, "")

    def test_a_holidays_set_still_takes_over_and_the_months_design_is_kept_for_after(self):
        page = self.page("standin", dt.date(2027, 10, 31))
        self.assertEqual((page.held, page.design), ("halloween", "standin-october"))
        self.assertTrue(page.drawn_in.startswith("halloween:"))
        page = self.page("standin", dt.date(2027, 10, 31), holidays=False)
        self.assertEqual((page.held, page.drawn_in), ("", "standin-october:2027-10-31"))

    def test_the_commit_says_when_a_months_design_takes_over(self):
        page = self.page("standin", dt.date(2027, 4, 1))
        subject, para = R._set_news(page, "", "standin-march")
        self.assertEqual(subject, "draw April's standin design, Design 4")
        self.assertIn("It is April, so the page is drawn in Design 4, the standin collection's design for the month",
                      para)
        self.assertIn("with the trophies in the standard look. On May 1 the next design takes over.", para)
        self.assertEqual(R._set_news(page, "", "standin-april"), ("", ""))
        december = self.page("standin", dt.date(2027, 12, 1))
        self.assertIn("On January 1 the next design takes over.", R._set_news(december, "", "")[1])

    def test_the_commit_says_where_the_page_goes_when_a_holiday_comes_and_goes(self):
        up = self.page("standin", dt.date(2027, 10, 30))
        subject, para = R._set_news(up, "", "standin-october")
        self.assertEqual(subject, "put up the Halloween set")
        self.assertIn("the page goes back to Design 10, the standin collection's October design after.", para)
        down = self.page("standin", dt.date(2027, 11, 2))
        subject, para = R._set_news(down, "halloween", "standin-november")
        self.assertEqual(subject, "take down the Halloween set")
        self.assertEqual(para, "The Halloween set is down, and the page is drawn in Design 11, the standin "
                               "collection's November design.")

    def test_a_named_design_is_announced_once(self):
        page = self.page("standin-june", dt.date(2027, 2, 3))
        subject, para = R._set_news(page, "", "")
        self.assertEqual(subject, "draw the page in Design 6")
        self.assertIn("The page is drawn in Design 6, from the standin collection", para)
        self.assertEqual(R._set_news(page, "", "standin-june"), ("", ""))


class PixelSets(unittest.TestCase):
    def test_a_holiday_and_a_design_are_found_the_same_way(self):
        self.assertEqual(pixelsets.drawn_by("halloween:2026-10-31").key, "halloween")
        self.assertEqual(pixelsets.name("halloween:2026-10-31"), "the Halloween set")
        key = DRAWN[0]
        self.assertEqual(pixelsets.drawn_by(key).key, key)
        self.assertEqual(pixelsets.name(key), f"{C.name_of(key)}, from the {C.owner(key).key} collection")
        self.assertIsNone(pixelsets.drawn_by("no-such-set"))


if __name__ == "__main__":
    unittest.main()
