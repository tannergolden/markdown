# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Heaven & Hell's own rules, which the checks every set shares cannot know: every header stands on heaven's
cloud by day and on hell's river of lava by night, never on the other's; the ground, the herald's call across the
H3 and the sky's blended bands keep two units clear of every word; and its boards and podium are heaven's and
hell's own stuffs."""
from __future__ import annotations

import math
import re
import unittest

from tests import support
from tests.unit.test_holiday_sets import contents

from domain import pixelthemes
from domain.canvas import DARK, DAY
from domain.holidays.pixel import Pix
from domain.pixelthemes.heaven_and_hell import flyers as FL
from domain.pixelthemes.heaven_and_hell import scenes as SC
from domain.pixelthemes.heaven_and_hell import sheet as S
from domain.pixelthemes.heaven_and_hell.palette import DAY_SKY, NIGHT_SKY, RAMP

support.install()
KEY = "heaven-and-hell"
SET = pixelthemes.drawn_by(KEY)


def near(p: Pix, x: float, y: float, margin: int = 2) -> bool:
    """Whether the point (x, y) comes within `margin` units of any word on `p`."""
    x, y = int(x), int(y)
    return not p.clear_of_words(x - margin, y - margin, x + 1 + margin, y + 1 + margin)


class TheTwins(unittest.TestCase):
    def test_every_header_stands_on_cloud_by_day_and_on_lava_by_night_never_on_the_others(self):
        cloud, lava = RAMP["cloud"][2].upper(), RAMP["lava"][5].upper()
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for wide in (True, False):
                    day = SET.header(code, h, DAY, wide, False).upper()
                    dark = SET.header(code, h, DARK, wide, False).upper()
                    self.assertTrue(cloud in day and lava not in day, (name, code, wide, "day"))
                    self.assertTrue(lava in dark and cloud not in dark, (name, code, wide, "dark"))

    def test_by_day_the_sky_is_heavens_and_by_night_hells_each_band_laid_into_the_next(self):
        for night, sky in ((False, DAY_SKY), (True, NIGHT_SKY)):
            p = Pix(415, 132)
            S.paper(p, night)
            fills = re.findall(r'<rect y="\d+" width="415" height="\d+" fill="(#[0-9A-F]{6})"/>', "".join(p.under))
            self.assertEqual(fills, list(sky), night)
            checkers = [d for d in p.defs if d.startswith("<pattern")]
            self.assertEqual(len(checkers), len(sky) - 1, night)
            for i, d in enumerate(checkers, 1):
                self.assertIn(f'fill="{sky[i]}"', d)
                self.assertIn(f'fill="{sky[i - 1]}"', d)


class ClearOfWords(unittest.TestCase):
    def test_the_ground_never_comes_within_two_units_of_a_word(self):
        for night in (False, True):
            p = Pix(415, 132)
            p.text(150, 84, "A WORD LOW OVER THE FOOT", "#000000", "35")
            SC.band(p, 5, 410, 100, 14, night, 3, False, ends=((5, 64), (340, 410)))
            cells = [q for name, layer in p.layers.items() for q in layer]
            self.assertTrue(cells, night)
            self.assertFalse([q for q in cells if near(p, *q)], night)

    def test_the_heralds_call_never_comes_within_two_units_of_a_word(self):
        for night in (False, True):
            p = Pix(415, 104)
            p.text(200, 34, "IN THE WAY", "#000000", "35")
            FL.call(p, 360, 30, 1.0, night, False, box=(8, 9, 407, 73))
            polygons = [re.findall(r'(-?[\d.]+),(-?[\d.]+)', g) for g in re.findall(
                r'<polygon points="([^"]+)"', "".join(s for shapes in p.shapes.values() for s in shapes))]
            cells = [q for name, layer in p.layers.items() for q in layer]
            self.assertTrue(polygons or cells, night)
            for poly in polygons:
                (ox, oy), *ends = [(float(x), float(y)) for x, y in poly]
                for ex, ey in ends:
                    for t in range(1, 41):
                        self.assertFalse(near(p, ox + (ex - ox) * t / 40, oy + (ey - oy) * t / 40), (night, poly))
            self.assertFalse([q for q in cells if near(p, *q)], night)

    def test_the_heralds_call_by_day_is_light_and_by_night_fire(self):
        for night in (False, True):
            p = Pix(415, 104)
            FL.call(p, 360, 30, 1.0, night, False, box=(8, 9, 407, 73))
            shapes = "".join(s for shapes in p.shapes.values() for s in shapes)
            colours = {c for layer in p.layers.values() for c in layer.values()}
            if night:
                self.assertIn(RAMP["fire"][6], colours)
                self.assertIn(RAMP["smoke"][4], shapes)
            else:
                self.assertGreaterEqual(shapes.count("<polygon"), 4)
                self.assertNotIn(RAMP["fire"][6], colours)


class TheGames(unittest.TestCase):
    def test_its_boards_and_podium_are_heavens_by_day_and_hells_by_night(self):
        day, dark = SET.game_board(False), SET.game_board(True)
        self.assertEqual((day["light_stuff"].grain, day["dark_stuff"].grain, day["style"]), ("veins", "metal", "gilt"))
        self.assertEqual((dark["light_stuff"].grain, dark["dark_stuff"].grain, dark["style"]),
                         ("stone", "slate", "iron"))
        self.assertEqual(SET.game_podium(False).style, "garland")
        self.assertEqual(SET.game_podium(True).style, "crenels")
        # A board's light squares are lighter than its dark ones, by day and by night.
        for b in (day, dark):
            light, deep = (sum(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (b["light"], b["dark"]))
            self.assertGreater(light, deep)
        self.assertTrue(math.isfinite(len(SET.game_tokens)))


if __name__ == "__main__":
    unittest.main()
