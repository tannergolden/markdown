# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Valentine's Day set's own rules, which the checks every set shares cannot know: a title lacquered by day
reads by the wine edge round its letters and lit as neon by night reads by every band of it; a flip clock's
digits read on their tiles; what the set shows only at night (its sky lanterns, its ribbon's hearts lighting up
in turn) never shows by day; the petals along a badge's top stay in its top two rows and inside its shape; and
a written colour lands on the swatch of its own family."""
from __future__ import annotations

import unittest
from unittest import mock

from tests import support

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.holidays import drawn_by
from domain.holidays.designs.badges import STYLES, TOP, inside, nearest
from domain.holidays.pixel import Pix, contrast
from domain.holidays.valentines_day import art as A
from domain.holidays.valentines_day.palette import C, NIGHT_SKY, RAMP
from domain.palette import PALETTE

support.install()
SET = drawn_by("valentines-day")
HEADER = Header(holiday="valentines-day")


class Title(unittest.TestCase):
    def test_by_day_the_lacquer_reads_by_its_wine_edge_and_by_night_every_band_of_the_neon_reads(self):
        edge = SET.lit(False)["outline"]
        for ground in (C["paper"], C["grid"]):
            self.assertGreaterEqual(contrast(edge, ground), 4.5, ground)
        for scale in (1, 2, 3, 4):
            for row in range(7 * scale):
                band = A.foil_fill(row, 0, scale, True)
                for ground in NIGHT_SKY:
                    self.assertGreaterEqual(contrast(band, ground), 4.5, (scale, row, ground))

    def test_the_edge_is_drawn_round_every_title_even_when_a_file_is_drawn_lighter(self):
        edge = f'<g stroke="{SET.lit(False)["outline"]}">'
        self.assertIn(edge, SET.header("H2", HEADER, DAY, True, True))
        SET._lite = True
        try:
            self.assertIn(edge, SET.header("H2", HEADER, DAY, True, True))
        finally:
            SET._lite = False
        self.assertIn('stroke="url(#pafoil4n)"', SET.header("H2", HEADER, DARK, True, True))


class Elements(unittest.TestCase):
    def test_a_counters_digits_read_on_their_flip_tile(self):
        tile = Pix(11, 15)
        A.flip_tile(tile, 0, 0)
        faces = {c for (x, y), c in tile.layers["base"].items() if 1 <= y <= 13 and y != 7 and x < 10}
        for night in (False, True):
            for face in faces:
                self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, (night, face))


class NightOnly(unittest.TestCase):
    def test_sky_lanterns_and_the_ribbons_lit_hearts_are_drawn_only_by_night(self):
        with mock.patch.object(A, "sky_lanterns") as lanterns, mock.patch.object(A, "heart_chase") as chase:
            for code in ("H1", "H2", "H3"):
                for wide in (True, False):
                    for motion in (True, False):
                        SET.header(code, HEADER, DAY, wide, motion)
            self.assertFalse(lanterns.called)
            self.assertFalse(chase.called)
            SET.header("H1", HEADER, DARK, True, False)
            self.assertTrue(lanterns.called)
            self.assertFalse(chase.called, "the hearts light up in turn only in a moving file")
            SET.header("H1", HEADER, DARK, True, True)
            self.assertTrue(chase.called)


class Badges(unittest.TestCase):
    def test_the_petals_lie_in_a_badges_top_two_rows_and_inside_its_shape(self):
        for style, s in STYLES.items():
            for w in (9, 23, 60):
                for seed in range(6):
                    p = Pix(w, s["h"])
                    SET.badge_top(p, w, s, seed, False)
                    self.assertTrue(p.layers["base"], (style, w, seed))
                    for (x, y) in p.layers["base"]:
                        self.assertLess(y, TOP, (style, w, seed, x, y))
                        self.assertTrue(inside(x, y, w, s["h"], s["corner"]), (style, w, seed, x, y))

    def test_a_written_colour_lands_on_the_swatch_of_its_own_family(self):
        swatches = SET.badge_swatches()
        family = {"red": "rose", "orange": "amber", "yellow": "gold", "green": "leaf", "purple": "lilac",
                  "white": "lace", "black": "starlight", "gray": "silver", "brown": "cocoa", "magenta": "sprinkles"}
        for written, swatch in family.items():
            self.assertEqual(nearest(PALETTE[written], swatches), swatch, written)
        self.assertEqual(swatches["rose"][0], RAMP["rose"][3])


if __name__ == "__main__":
    unittest.main()
