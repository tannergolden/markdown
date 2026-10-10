# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the shared checks cannot know about the Juneteenth set: its titles are painted like the flag, every band
of the paint reading on the night sky and the day's edge drawing exactly the engine's outline; fireworks,
fireflies and string lights come out only at night; a phone's sheet leaves the flag the pole it was drawn on; and
a written colour finds the family the set has for it."""
from __future__ import annotations

import math
import re
import unittest
from unittest import mock

from tests import support

from domain.banners.content import Header
from domain.holidays import drawn_by
from domain.holidays.designs.badges import STYLES, inside, nearest
from domain.holidays.juneteenth import art as A
from domain.holidays.juneteenth.palette import C, NIGHT_SKY, RAMP
from domain.holidays.pixel import FONTS, Pix, contrast
from domain.palette import PALETTE

support.install()
SET = drawn_by("juneteenth")
SAMPLE = Header(title="BANNERS", tagline="Blueprint headers and footers a README draws for itself.",
                motto="Drafted, never fetched.", notes=(), description="",
                figures=(("PROJECT", "tannergolden/banners"), ("RELEASE", "v1.8.0")), tone="juneteenth")


def path_cells(d: str) -> set:
    """The pixels a mono symbol's path covers: the canvas writes runs a pixel thick, along a row (`h`) through its
    middle or down a column (`v`), each move after the first relative to where the last run ended."""
    cells, x, y, op = set(), 0.0, 0.0, None
    nums = []
    for tok in re.findall(r"[Mmhv]|-?\d*\.?\d+", d):
        if tok in "Mmhv":
            op, nums = tok, []
            continue
        nums.append(float(tok))
        if op in "Mm" and len(nums) == 2:
            x, y = (nums[0], nums[1]) if op == "M" else (x + nums[0], y + nums[1])
        elif op == "h":
            cells |= {(math.floor(x) + i, math.floor(y)) for i in range(int(nums[0]))}
            x += nums[0]
        elif op == "v":
            cells |= {(math.floor(x), math.floor(y) + i) for i in range(int(nums[0]))}
            y += nums[0]
    return cells


def stroked(p: Pix, stroke: str) -> set:
    """Every pixel the uses stroked in `stroke` cover on the drawing's base layer."""
    keys = {sid: key for key, sid in p.syms.items() if isinstance(sid, str)}
    paths = dict(re.findall(r'<path id="(q\d+)" d="([^"]+)"/>', "".join(p.defs)))
    out = set()
    for colour, sid, x, y, scale in p.uses["base"]:
        if colour != stroke:
            continue
        key = keys[sid]
        if key[0] == "glyph":
            rows = FONTS[key[1]][0][key[2]][1]
            out |= {(x + col * scale + i, y + r * scale + j) for r, cols in enumerate(rows) for col in cols
                    for i in range(scale) for j in range(scale)}
        else:
            out |= {(x + cx, y + cy) for cx, cy in path_cells(paths[sid])}
    return out


class Title(unittest.TestCase):
    def test_every_band_of_the_flags_paint_reads_on_every_row_of_the_night_sky(self):
        for scale in (1, 2, 3, 4):
            for arc in (2, 3):
                for r in range(7 * scale):
                    band = A.foil_fill(r, 0, scale, True, arc)
                    for sky in NIGHT_SKY:
                        self.assertGreaterEqual(contrast(band, sky), 4.5, (scale, arc, r, band, sky))

    def test_by_day_the_white_arc_needs_the_deep_blue_edge_and_has_it(self):
        self.assertLess(contrast(A.foil_fill(3, 0, 1, False), C["paper"]), 1.5)
        self.assertGreaterEqual(contrast(RAMP["blue"][0], C["paper"]), 4.5)
        for night in (False, True):
            p = Pix(120, 40)
            SET.title_text(p, 4, 6, "JUNE", night, 3)
            strokes = {stroke for stroke, *_ in p.uses["base"]}
            self.assertEqual(RAMP["blue"][0] in strokes, not night, night)
            self.assertEqual(RAMP["gold"][4] in strokes, not night, night)

    def test_the_day_edge_draws_exactly_what_the_engines_outline_would(self):
        edge = RAMP["blue"][0]
        for scale in (1, 2, 3, 4):
            ours, engines = Pix(260, 60), Pix(260, 60)
            A.title_edge(ours, 5, 5, "JUNE 19, 1865", scale, edge, RAMP["gold"][4])
            engines.text(5, 5, "JUNE 19, 1865", RAMP["blue"][2], "57", scale, outline=edge)
            self.assertEqual(stroked(ours, edge), stroked(engines, edge), scale)
            self.assertEqual(len(ours.words), 0, "the shadow is drawing, not words")


class Night(unittest.TestCase):
    def test_fireworks_fireflies_and_string_lights_come_out_only_at_night(self):
        for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
            for night in (False, True):
                p = draw(SAMPLE, night, True)
                fireworks = [L for L in p.layers if L.startswith("fw") and (p.layers[L] or p.uses[L])]
                lights = [L for L in p.layers if L.startswith("bl") and (p.layers[L] or p.uses[L])]
                self.assertEqual(bool(fireworks), night, (code, night))
                if code != "H2":
                    self.assertEqual(bool(lights), night, (code, night, "fireflies"))

    def test_the_frames_stars_light_up_in_turn_only_along_a_wide_header_by_night(self):
        star = RAMP["gold"][6]
        for night in (False, True):
            for p, chases in ((SET.h2(SAMPLE, night, True), night), (SET.h2_narrow(SAMPLE, night), False)):
                lit = any(p.layers[L].get((6, 0)) == star for L in p.layers if L.startswith("tw"))
                self.assertEqual(lit, chases, (p.w, night))


class Phone(unittest.TestCase):
    def test_a_phone_sheet_leaves_the_flag_its_pole_beside_the_motto(self):
        for night in (False, True):
            _, rule = SET._h1n(None, SAMPLE, night)
            p = SET.h1_narrow(SAMPLE, night)
            self.assertTrue(p.clear_of_words(6, rule - 47, 38, rule - 23), night)
            pole = RAMP["silver"][4 if night else 5]
            self.assertTrue(all(p.get(8, y) in (pole, RAMP["silver"][6]) for y in range(rule - 40, rule - 13)), night)
            motto = [b for b in p.words if b[1] < rule - 23 and b[3] > rule - 46 and b[0] > 41]
            self.assertTrue(motto, "the motto stands beside the flag, above the cookout")


class Badges(unittest.TestCase):
    def test_a_written_colour_finds_the_family_the_set_has_for_it(self):
        swatches = SET.badge_swatches()
        wanted = {"red": "red", "crimson": "red", "orange": "ember", "yellow": "gold", "amber": "gold",
                  "green": "green", "forest": "green", "blue": "blue", "cobalt": "blue", "purple": "violet",
                  "plum": "violet", "amethyst": "violet", "white": "linen", "ivory": "linen", "black": "starlight",
                  "gray": "slate", "slate": "slate", "brown": "oak"}
        for written, family in wanted.items():
            self.assertEqual(nearest(PALETTE[written], swatches), family, written)

    def test_the_confetti_lies_only_along_the_top_two_rows_inside_the_shape(self):
        for style, s in STYLES.items():
            args = (style, "Build", "Passing", "pulse", SET.badge_label(), SET.badge_swatches()["green"][:2])
            trimmed = SET.classic_badge(*args)
            with mock.patch.object(type(SET), "badge_top", lambda *a: None):
                bare = SET.classic_badge(*args)
            changed = {q for q in set(trimmed.layers["base"]) | set(bare.layers["base"])
                       if trimmed.get(*q) != bare.get(*q)}
            self.assertTrue(changed, style)
            self.assertTrue(all(y < 2 and inside(x, y, trimmed.w, s["h"], s["corner"]) for x, y in changed), style)


if __name__ == "__main__":
    unittest.main()
