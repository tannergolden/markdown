# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The page's birthday: the day it falls on, whose it is and how old the page turns, the set that draws it, and the
page it takes for the day from whatever else would draw it."""
from __future__ import annotations

import datetime as dt
import unittest

from tests import support

from app import page as P
from domain import birthday as B
from domain import pixelsets, settings
from domain.birthday import art as A
from domain.birthday.party import SAMPLE_AGE
from domain.holidays.pixel import Pix

D = dt.date
support.install()


def cfg(**given) -> dict:
    return settings.validate(given, catalogue=support.install())


class Calendar(unittest.TestCase):
    def test_a_leap_day_birthday_is_kept_on_february_28_in_a_common_year(self):
        self.assertEqual(B.falls(2, 29, 2027), D(2027, 2, 28))
        self.assertEqual(B.falls(2, 29, 2028), D(2028, 2, 29))
        self.assertEqual(B.falls(3, 14, 2027), D(2027, 3, 14))

    def test_a_person_without_a_year_has_a_birthday_every_year_and_no_age(self):
        self.assertEqual(B.on(D(2026, 3, 14), given="03-14"), B.Party(D(2026, 3, 14)))
        self.assertIsNone(B.on(D(2026, 3, 13), given="03-14"))
        self.assertIsNone(B.on(D(2026, 3, 15), given="03-14"))
        self.assertEqual(B.on(D(2027, 2, 28), given="02-29"), B.Party(D(2027, 2, 28)))

    def test_a_person_with_a_year_turns_a_year_older_from_the_first_anniversary(self):
        self.assertEqual(B.on(D(2026, 3, 14), given="1990-03-14"), B.Party(D(2026, 3, 14), 36))
        self.assertEqual(B.on(D(2027, 3, 14), given="1990-03-14").age, 37)
        self.assertIsNone(B.on(D(1990, 3, 14), given="1990-03-14"))
        self.assertIsNone(B.on(D(2026, 3, 14), given="2030-03-14"))
        self.assertEqual(B.on(D(2027, 2, 28), given="2004-02-29"), B.Party(D(2027, 2, 28), 23))

    def test_a_cake_holds_every_age_up_to_999_and_no_older(self):
        self.assertEqual(B.on(D(2026, 3, 14), given="1027-03-14").age, 999)
        self.assertEqual(B.on(D(2026, 3, 14), given="1926-03-14").age, 100)
        self.assertIsNone(B.on(D(2026, 3, 13), given="1027-03-14"))
        for when in (D(2026, 3, 14), D(2026, 7, 1)):
            with self.assertRaises(B.BirthdayError) as caught:
                B.on(when, given="1026-03-14")
            self.assertIn("up to 999, so a whole date's year is 1027 or later", str(caught.exception))
            self.assertNotIn("1026", str(caught.exception))

    def test_a_repository_turns_a_year_older_from_the_first_anniversary(self):
        self.assertIsNone(B.on(D(2026, 10, 10), born=D(2026, 10, 10)))
        self.assertEqual(B.on(D(2027, 10, 10), born=D(2026, 10, 10)), B.Party(D(2027, 10, 10), 1))
        self.assertEqual(B.on(D(2039, 3, 14), born=D(2019, 3, 14)).age, 20)
        self.assertIsNone(B.on(D(2039, 3, 15), born=D(2019, 3, 14)))
        self.assertIsNone(B.on(D(2039, 3, 14)))

    def test_the_key_carries_the_day_and_an_age_when_one_is_known(self):
        self.assertEqual(B.Party(D(2026, 3, 14)).held, "birthday:2026-03-14")
        self.assertEqual(B.Party(D(2026, 3, 14), 7).held, "birthday:2026-03-14:7")

    def test_ordinals(self):
        self.assertEqual([B.ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22, 23, 101, 111)],
                         ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "23rd", "101st",
                          "111th"])


class TheSet(unittest.TestCase):
    def test_the_key_hands_out_the_set_told_its_day_and_age(self):
        sample = B.drawn_by("birthday")
        self.assertEqual((sample.key, sample.name, sample.day), ("birthday", "Birthday", None))
        person = B.drawn_by("birthday:2026-03-14")
        self.assertEqual((person.day, person.age), (D(2026, 3, 14), None))
        repo = B.drawn_by("birthday:2026-03-14:7")
        self.assertEqual((repo.day, repo.age), (D(2026, 3, 14), 7))
        self.assertIsNone(sample.day, "handing out a set told its day leaves the shared one alone")
        for other in ("", None, "halloween", "birthdays"):
            self.assertIsNone(B.drawn_by(other), other)

    def test_the_kit_finds_it_by_its_key(self):
        self.assertEqual(pixelsets.drawn_by("birthday:2026-03-14:7").age, 7)
        self.assertEqual(pixelsets.name("birthday:2026-03-14"), "the Birthday set")

    def test_the_cake_carries_the_age_in_number_candles_and_a_person_without_one_five(self):
        for age, wicks in ((None, 5), (3, 1), (12, 2), (101, 3), (999, 3)):
            p = Pix(120, 80)
            self.assertEqual(len(A.candle_row(p, 60, 60, False, age)), wicks, age)

    def test_three_figures_stand_on_the_top_tier_with_their_flames_apart(self):
        for age in (100, 888, 999):
            p = Pix(415, 140)
            wicks = A.cake(p, 200, 130, False, False, age)
            tier = [x for (x, y), c in p.layers["base"].items() if y == wicks[0][1] + 12]
            figures = [x for (x, y), c in p.layers["base"].items() if wicks[0][1] + 2 <= y <= wicks[0][1] + 11]
            self.assertGreaterEqual(min(figures), min(tier), age)
            self.assertLessEqual(max(figures), max(tier), age)
            gaps = [b[0] - a[0] for a, b in zip(wicks, wicks[1:])]
            self.assertTrue(all(g >= 6 for g in gaps), (age, gaps))
        self.assertEqual(B.drawn_by("birthday")._age(), SAMPLE_AGE)
        self.assertIsNone(B.drawn_by("birthday:2026-03-14")._age())

    def test_every_figure_is_cast_and_ten_rows_tall(self):
        for figure, rows in A.FIGURES.items():
            self.assertEqual(len(rows), 10, figure)
            self.assertTrue(all(len(row) == 7 for row in rows), figure)

    def test_every_wide_header_and_phone_spells_the_greeting_in_its_bunting(self):
        for w in (415, 180):
            p = Pix(w, 40)
            A.bunting(p, 5, w - 5, 5, False, span=41 if w > 180 else 34)
            inked = [(x, y) for (x, y), c in p.layers["base"].items() if c == A.C["ink"]]
            self.assertGreater(len(inked), 60, w)
            self.assertTrue(all(5 <= y <= 20 for _, y in inked), w)

    def test_a_counters_digit_is_never_covered_by_its_gift_box(self):
        for night in (False, True):
            q = Pix(40, 40)
            B.drawn_by("birthday").counter_cell(q, 10, 10, night)
            digit = {(x, y) for x in range(13, 18) for y in range(15, 22)}   # where `counters` letters it
            self.assertFalse(digit & set(q.layers["base"]), night)
            self.assertTrue(digit <= set(q.layers["far"]), night)

    def test_the_candles_blow_out_once_a_loop_in_a_moving_file_and_stay_lit_in_a_still_one(self):
        held = B.drawn_by("birthday:2026-03-14:7")
        from domain.banners import sample
        from domain.banners.compose import compose
        from domain.banners.designs import DESIGNS, render
        from domain.banners.settings import check
        h, _, _ = compose(sample.SAMPLES["repository"], check({}) | {"theme": "standard", "holiday": held.key + ":2026-03-14:7"})
        files = render(DESIGNS["H2"], h)
        moving, still = files["header-day.svg"], files["header-still-day.svg"]
        self.assertIn(f'keyTimes="0;{A.num(A.BLOW_OUT)};{A.num(A.BLOW_ON)}"', moving)
        self.assertIn("birthday H2 day", moving)
        self.assertNotIn("<animate", still)


class ThePage(unittest.TestCase):
    def settle(self, today, mode="profile", born=None, **given):
        return P.settle(".", cfg(**given), mode=mode, subject="octo-dev", here="octo-dev/octo-dev", today=today,
                        lk={"drawn": None, "parts": {}}, born=born)

    def test_a_person_names_their_birthday_and_it_takes_the_page_for_the_day(self):
        page = self.settle(D(2026, 3, 14), birthday="03-14")
        self.assertEqual((page.held, page.drawn_in), ("birthday", "birthday:2026-03-14"))
        self.assertEqual(self.settle(D(2026, 3, 15), birthday="03-14").held, "")
        self.assertEqual(self.settle(D(2026, 3, 14)).held, "", "GitHub keeps no birthday for a person")

    def test_a_person_with_a_year_turns_their_age(self):
        page = self.settle(D(2026, 3, 14), birthday="1990-03-14")
        self.assertEqual(page.drawn_in, "birthday:2026-03-14:36")
        self.assertEqual(self.settle(D(2026, 3, 14), birthday="1027-03-14").drawn_in, "birthday:2026-03-14:999")

    def test_a_year_that_would_make_the_page_older_than_its_cake_holds_fails_the_settings(self):
        with self.assertRaises(settings.SettingsError) as caught:
            self.settle(D(2026, 5, 1), birthday="1026-03-14")
        self.assertIn("up to 999", str(caught.exception))

    def test_the_birthday_wins_over_a_holiday_and_a_collection_and_hands_them_back(self):
        page = self.settle(D(2026, 12, 25), birthday="12-25")
        self.assertEqual(page.held, "birthday")
        self.assertIsNone(page.holiday)
        self.assertEqual(self.settle(D(2026, 12, 26), birthday="12-25").held, "christmas")
        page = self.settle(D(2026, 11, 3), birthday="11-03", theme="medieval")
        self.assertEqual(page.drawn_in, "birthday:2026-11-03")
        self.assertTrue(self.settle(D(2026, 11, 4), birthday="11-03", theme="medieval").drawn_in.startswith("medieval"))

    def test_the_two_switches_are_apart(self):
        self.assertEqual(self.settle(D(2026, 12, 25), birthday="12-25", holidays=False).held, "birthday")
        self.assertEqual(self.settle(D(2026, 12, 25), birthday=False).held, "christmas")

    def test_a_repository_takes_the_day_github_created_it_and_no_other(self):
        page = self.settle(D(2027, 10, 10), mode="repository", born=D(2026, 10, 10))
        self.assertEqual((page.drawn_in, page.born), ("birthday:2027-10-10:1", D(2026, 10, 10)))
        self.assertEqual(self.settle(D(2027, 10, 10), mode="repository", born=D(2026, 10, 10), birthday=False).held,
                         "")
        with self.assertRaises(settings.SettingsError) as caught:
            self.settle(D(2027, 10, 10), mode="repository", born=D(2026, 10, 10), birthday="10-10")
        self.assertIn("the day GitHub created it", str(caught.exception))

    def test_a_repository_is_born_on_its_day_in_the_pages_zone(self):
        class GitHub:
            def __init__(self, stamp):
                self.stamp = stamp

            def rest(self, path, missing=None, **params):
                return {"created_at": self.stamp} if self.stamp else None

        west = dt.timezone(dt.timedelta(hours=-5))
        self.assertEqual(P.born_on(GitHub("2019-03-15T02:30:00Z"), "o/r", west), D(2019, 3, 14))
        self.assertEqual(P.born_on(GitHub("2019-03-15T02:30:00Z"), "o/r", dt.timezone.utc), D(2019, 3, 15))
        self.assertIsNone(P.born_on(GitHub(""), "o/r", west))


if __name__ == "__main__":
    unittest.main()
