# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Christmas set's own rules, which the checks every set shares cannot know: snow lies along a badge's top
two rows, in the night's colours on a night plate, with the letters under it; a title wears a cap of snow;
snow falls only across a wide moving header, its still twin keeps the far flakes where they lie, a lighter
drawing keeps only those, and a phone's header has none; the moon is out only by night, and only where it
has room; and a counter's digits keep an ink of their own, so they are set over the doors they are cut into."""
from __future__ import annotations

import unittest
from unittest import mock

from tests import support

from domain.banners.content import Header
from domain.canvas import BUDGET, DARK, DAY
from domain.elements import data as ED
from domain.elements import draw as E
from domain.holidays.christmas import SET
from domain.holidays.christmas.palette import C, SNOW, X
from domain.holidays.designs.badges import STYLES, TOP
from domain.holidays.pixel import contrast
from infra.yaml_reader import loads

support.install()
HEADER = Header(tone="standard", holiday="christmas")
LONG = HEADER.with_(title="an-organisation-with-a-long-name/and-a-long-repository")


def rows(p, *ys) -> set:
    """The colours a drawing's pixels take in rows `ys`."""
    return {c for (x, y), c in p.layers["base"].items() if y in ys}


class Badges(unittest.TestCase):
    def test_snow_lies_on_every_badges_top_rows_in_the_nights_colours_on_a_night_plate(self):
        for style in STYLES:
            plates = {night: SET.plate_badge(style, "License", "MIT", "scale", "night" if night else "day")
                      for night in (False, True)}
            for night, p in plates.items():
                snow, other = SNOW[night], SNOW[not night]
                self.assertIn(snow["top"], rows(p, 0), (style, night))
                self.assertTrue(rows(p, 1) & {snow["shade"], snow["deep"]}, (style, night))
                self.assertFalse(rows(p, 0, 1) & {other["shade"], other["deep"]}, (style, night))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the snow")
            classic = SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                        SET.badge_states()["green"])
            self.assertTrue(rows(classic, 1) & {SNOW[False]["shade"], SNOW[False]["deep"]}, style)


class Headers(unittest.TestCase):
    def test_a_title_wears_a_cap_of_snow_shaded_at_each_drifts_end(self):
        for night in (False, True):
            caps = set(SET.h2(HEADER, night, True).layers["base~"].values())
            self.assertIn(C["white"], caps, night)
            self.assertIn(SNOW[night]["shade"], caps, night)

    def test_snow_falls_only_across_a_wide_moving_header(self):
        for theme in (DAY, DARK):
            moving = SET.header("H1", HEADER, theme, True, True)
            still = SET.header("H1", HEADER, theme, True, False)
            phone = SET.header("H1", HEADER, theme, False, False)
            for depth in ("far", "near"):
                self.assertIn(f'href="#snow{depth}g"', moving, theme["name"])
            self.assertIn('clip-path="url(#snowfarc)"', still, "the still twin keeps the far flakes where they lie")
            self.assertNotIn("snownear", still, "and leaves the near ones, which would sit on its letters, out")
            self.assertNotIn("snowfar", phone)

    def test_a_lighter_drawing_keeps_its_snow_falling_behind_it_and_none_in_front(self):
        full = SET.header("H2", HEADER, DARK, True, True)
        with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
            lighter = SET.header("H2", HEADER, DARK, True, True)
        self.assertIn('href="#snowfarg"', lighter)
        self.assertNotIn("snownear", lighter)

    def test_the_moon_is_out_only_by_night_and_only_where_it_has_room(self):
        self.assertIn(X["earthshine"], SET.header("H1", HEADER, DARK, True, True))
        self.assertNotIn(X["earthshine"], SET.header("H1", HEADER, DAY, True, True))
        self.assertNotIn(X["earthshine"], SET.header("H1", LONG, DARK, True, True), "a long title leaves it no room")


class Elements(unittest.TestCase):
    def test_a_counters_digits_have_an_ink_of_their_own_and_are_set_over_their_doors(self):
        settings = loads((support.ROOT / "tests" / "fixtures" / "driftmark" / ".github" / "markdown.yaml")
                         .read_text(encoding="utf-8"))
        vitals = ED.merged(ED.check(settings["elements"]), {}, subject="driftmark/driftmark",
                           today="2026-09-25")["vitals"]
        for night in (False, True):
            k = SET.ink(night)
            words = {k[role] for role in ("title", "shadow", "body", "muted", "rule", "accent", "tag_ink")}
            p = SET.draw_element("instruments", E.describe("instruments", vitals), night, "wide")
            svg = p.svg("t", "d", still=True)
            door = svg.index(f'href="#{p.syms[(("stamp", ("cell", night)), "base")]}"')
            for dim in (False, True):
                ink = SET.counter_ink(night, dim)
                self.assertNotIn(ink, words, (night, dim))
                self.assertGreaterEqual(contrast(ink, k["fill"]), 4.5, (night, dim))
                self.assertLess(door, svg.index(f'<g stroke="{ink}">'), (night, dim))


if __name__ == "__main__":
    unittest.main()
