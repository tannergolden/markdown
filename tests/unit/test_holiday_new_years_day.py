# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The New Year's Day set: the year it draws is the year of the New Year's Day it is handed, in the balloons
and in the lamps on the tower's roof, so December 31 already shows the year about to begin; any year, this
century and after, is set as large as its room allows; and fireworks are for midnight, so no day file has
one."""
from __future__ import annotations

import datetime as dt
import unittest
from unittest import mock

from tests import support

from domain import holidays as H
from domain.banners.content import Header
from domain.banners.designs import DESIGNS, check, render
from domain.canvas import DARK, DAY
from domain.holidays.new_years_day import SAMPLE_YEAR, SET, YEAR_ROOM
from domain.holidays.new_years_day import art as A
from domain.holidays.pixel import Pix

support.install()
KEY = "new-years-day"
HEADER = Header(tone="standard", holiday=KEY)


def drawn_balloons(held) -> dict:
    """The year's balloons as a moving H1 draws them: the pixels of the layer they ride the air on."""
    return held.h1(HEADER, False, True).layers["bob0"]


def balloons_for(year: str, drawn: dict) -> dict:
    """`year` in balloons on its own, in the face the H1 gives it and where it set the `drawn` ones (their
    seam is a pixel outside the figures)."""
    x, y = min(x for x, _ in drawn) + 1, min(y for _, y in drawn) + 1
    q = Pix(415, y + 40)
    A.year_balloons(q, x, y, False, strings=0, face=A.year_face(year, YEAR_ROOM[1] - YEAR_ROOM[0]), year=year)
    return q.layers["base"]


class TheYear(unittest.TestCase):
    def test_the_year_drawn_is_the_year_of_the_day_the_set_is_handed(self):
        a, b = SET.on(dt.date(2031, 1, 1)), SET.on(dt.date(2032, 1, 1))
        self.assertEqual((a.year, b.year), ("2031", "2032"))
        drawn = drawn_balloons(a)
        self.assertEqual(drawn, balloons_for("2031", drawn))
        self.assertNotEqual(drawn, balloons_for("2032", drawn))
        drawn = drawn_balloons(b)
        self.assertEqual(drawn, balloons_for("2032", drawn))
        self.assertNotEqual(drawn, balloons_for("2033", drawn))
        for code in ("H1", "H2"):
            for theme in (DAY, DARK):
                self.assertNotEqual(a.header(code, HEADER, theme, True, True),
                                    b.header(code, HEADER, theme, True, True), (code, theme["name"]))

    def test_the_tower_lights_the_year_it_is_handed(self):
        with mock.patch.object(A, "ball_drop", wraps=A.ball_drop) as drop:
            for night in (False, True):
                SET.on(dt.date(2468, 1, 1)).h2(HEADER, night, True)
        self.assertEqual({c.kwargs["year"] for c in drop.call_args_list}, {"2468"})

    def test_with_no_day_the_set_draws_its_sample_year(self):
        self.assertIsNone(SET.day)
        self.assertEqual(SET.year, str(SAMPLE_YEAR))
        self.assertEqual(H.drawn_by(KEY).year, "2027")
        drawn = drawn_balloons(SET)
        self.assertEqual(drawn, balloons_for("2027", drawn))

    def test_december_31_celebrates_the_year_about_to_begin(self):
        for year in (2026, 2099, 2399):
            for day in (dt.date(year, 12, 31), dt.date(year + 1, 1, 1), dt.date(year + 1, 1, 2)):
                w = H.active(day)
                self.assertEqual((w.key, w.day), (KEY, dt.date(year + 1, 1, 1)), day)
                held = H.drawn_by(f"{w.key}:{w.day.isoformat()}")
                self.assertEqual(held.year, str(year + 1), day)
            drawn = drawn_balloons(held)
            self.assertEqual(drawn, balloons_for(str(year + 1), drawn))
            self.assertNotEqual(drawn, balloons_for(str(year), drawn))

    def test_any_year_takes_the_largest_face_that_fits_and_its_files_hold(self):
        room = YEAR_ROOM[1] - YEAR_ROOM[0]
        for year in (2027, 2100, 2111, 2468, 2999, 9999):
            self.assertEqual(A.year_face(str(year), room), A.YEAR_FACES[0], year)
            h = Header(tone="standard", holiday=f"{KEY}:{year}-01-01")
            for code in ("H1", "H2"):
                files = render(DESIGNS[code], h)
                self.assertEqual(check(DESIGNS[code], files, SET.tokens), {}, (year, code))
                for name, svg in files.items():
                    self.assertIn(f" {KEY} {code} ", svg.split("-->")[0], (year, name))
            p = SET.on(dt.date(year, 1, 1)).h1(HEADER, False, True)
            xs, ys = [x for x, _ in p.layers["bob0"]], [y for _, y in p.layers["bob0"]]
            self.assertGreaterEqual(min(xs), YEAR_ROOM[0], year)
            self.assertLessEqual(max(xs), YEAR_ROOM[1] + 1, year)
            # Clear of every word, as high as they bob.
            self.assertTrue(p.clear_of_words(min(xs), min(ys) - 2, max(xs) + 1, max(ys) + 1), year)
        # A year of more figures than its room takes takes the next face down, and the smallest when none fits.
        self.assertEqual(A.year_face("12345", room), A.YEAR_FACES[1])
        self.assertEqual(A.year_face("1234567890123", room), A.YEAR_FACES[-1])


class Midnight(unittest.TestCase):
    NIGHT_ONLY = ("firework", "flash", "sparkler", "marquee_chase")

    def drawn(self, theme) -> dict:
        """How often each night-only drawing is drawn in every header and footer of `theme`."""
        spies = {n: mock.patch.object(A, n, wraps=getattr(A, n)) for n in self.NIGHT_ONLY}
        mocks = {n: s.start() for n, s in spies.items()}
        try:
            held = SET.on(dt.date(2027, 1, 1))
            for code in ("H1", "H2", "H3"):
                for wide, motion in ((True, True), (True, False), (False, False)):
                    held.header(code, HEADER, theme, wide, motion)
        finally:
            for s in spies.values():
                s.stop()
        return {n: m.call_count for n, m in mocks.items()}

    def test_fireworks_are_for_midnight_so_no_day_file_has_one(self):
        self.assertEqual(self.drawn(DAY), {n: 0 for n in self.NIGHT_ONLY})
        by_night = self.drawn(DARK)
        self.assertTrue(all(by_night.values()), by_night)


if __name__ == "__main__":
    unittest.main()
