# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Thanksgiving set's own rules, which the checks every set shares cannot know: the fallen leaves along a
badge's top stay in its top two rows and inside its shape; a title's paint reads on the evening sky and its
dark edge on the paper; a falling leaf or a skein of geese never crosses a word; a deep red written colour
takes the plaid; and a counter's digit is written over its place card."""
from __future__ import annotations

import unittest

from tests import support

from domain.holidays import drawn_by
from domain.holidays.designs.badges import STYLES, TOP, inside, nearest
from domain.holidays.pixel import Pix, contrast
from domain.holidays.thanksgiving import art as A
from domain.holidays.thanksgiving.palette import C, NIGHT_SKY, RAMP
from domain.palette import PALETTE

support.install()
SET = drawn_by("thanksgiving")


class Badges(unittest.TestCase):
    def test_the_fallen_leaves_stay_in_the_top_two_rows_and_inside_each_styles_shape(self):
        for style, s in STYLES.items():
            for w in range(8, 64):
                for seed in range(12):
                    for night in (False, True):
                        p = Pix(w, s["h"])
                        SET.badge_top(p, w, s, seed, night)
                        cells = p.layers["base"]
                        self.assertTrue(cells, (style, w, seed))
                        for (x, y) in cells:
                            self.assertLess(y, TOP, (style, w, seed, x, y))
                            self.assertTrue(0 <= x < w and inside(x, y, w, s["h"], s["corner"]), (style, w, seed, x, y))

    def test_a_deep_red_takes_the_plaid_and_a_bright_one_plain_cranberry(self):
        swatches = SET.badge_swatches()
        self.assertEqual(nearest(PALETTE["maroon"], swatches), "plaid")
        self.assertEqual(nearest(PALETTE["red"], swatches), "cranberry")
        svg = SET.badge(style="flat", label="Tone", message="maroon", icon=None, label_hex=PALETTE["black"],
                        message_hex=PALETTE["maroon"], live=False, state=None, reserve=(), rels=["static/x.svg"],
                        stamp="x")["static/x.svg"]
        for col in (RAMP["cranberry"][3], RAMP["cranberry"][2]):     # the cloth and its checks
            self.assertIn(col, svg)


class Titles(unittest.TestCase):
    def test_the_paint_reads_on_the_sky_and_the_dark_edge_on_the_paper(self):
        # A title stands in the upper part of its sky, never in its lowest band, where the deepest red is
        # nearest the sky's own colour; every band of the paint holds 4.5:1 on each band above it.
        for scale in (1, 2, 3, 4):
            for r in range(7 * scale):
                ink = A.autumn_fill(r, 0, scale, True)
                for sky in NIGHT_SKY[:-1]:
                    self.assertGreaterEqual(contrast(ink, sky), 4.5, (scale, r, ink, sky))
        # By day the letters' gold crown is too pale for the paper; the dark edge round each one carries them.
        self.assertGreaterEqual(contrast(RAMP["bark"][1], C["paper"]), 4.5)

    def test_a_day_title_takes_two_uses_a_letter_and_a_night_one_one(self):
        for night, each in ((False, 2), (True, 1)):
            p = Pix(415, 60, lite=True)      # lighter: no leaf comes to rest on the letters
            SET.title_text(p, 10, 10, "BANNERS", night, 4)
            self.assertEqual(len(p.uses["base"]), each * 7, night)


class Motion(unittest.TestCase):
    FALL = (52, 16, 100, "squash", -22, 7.0, 0.0)

    def test_a_falling_leaf_never_crosses_a_word(self):
        for motion in (True, False):
            p = Pix(415, 120)
            A.falling_leaves(p, [self.FALL], False, motion)
            self.assertEqual(len(p.raws) + len(p.uses.get("near", ())), 1, motion)
            x, y = A.fall_path(52, 16, 100, -22, 0.0)[10]
            q = Pix(415, 120)
            q.text(x - 4, y + 2, "IN THE WAY", "#000000", "35")
            A.falling_leaves(q, [self.FALL], False, motion)
            self.assertEqual(len(q.raws) + len(q.uses.get("near", ())), 0, motion)

    def test_a_skein_of_geese_never_crosses_a_word(self):
        for motion in (True, False):
            p = Pix(415, 120)
            A.geese(p, (430, 66), (378, 36), (318, -30), False, motion)
            self.assertEqual(len(p.raws) + len(p.uses.get("near", ())), 1, motion)
            q = Pix(415, 120)
            q.text(340, 10, "IN THE WAY", "#000000", "35")
            A.geese(q, (430, 66), (378, 36), (318, -30), False, motion)
            self.assertEqual(len(q.raws) + len(q.uses.get("near", ())), 0, motion)


class Elements(unittest.TestCase):
    def test_a_counters_digit_is_written_over_its_place_card(self):
        for night in (False, True):
            q = Pix(48, 48)
            SET.counter_cell(q, 24, 24, night)
            self.assertFalse(q.layers["base"])
            self.assertTrue(q.layers["card"])
            self.assertLess(q.meta["card"][0], q.meta["base"][0])


if __name__ == "__main__":
    unittest.main()
