# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Independence Day set's own rules: nothing the night brings, a firework above all, is drawn in a day
file; every badge wears the flag's trim along its top two rows; and every title is painted with the flag."""
from __future__ import annotations

import unittest
from unittest import mock

from tests import support

from domain.banners import sample as BS
from domain.banners.compose import compose
from domain.banners.settings import check as banners_check
from domain.canvas import DARK, DAY
from domain.elements import data as ED
from domain.elements import draw as E
from domain.holidays import drawn_by
from domain.holidays.designs.badges import STYLES, inside
from domain.holidays.independence_day import art as A
from domain.holidays.independence_day.palette import RAMP
from infra.yaml_reader import loads

support.install()
KEY = "independence-day"
SET = drawn_by(KEY)
SPECIMEN = loads((support.ROOT / "tests" / "fixtures" / "driftmark" / ".github" / "markdown.yaml")
                 .read_text(encoding="utf-8"))
ELEMENTS = ED.merged(ED.check(SPECIMEN["elements"]), {}, subject="driftmark/driftmark", today="2026-09-25")
SAMPLES = [compose(m, banners_check({}) | {"theme": "standard", "holiday": KEY})[:2] for m in BS.SAMPLES.values()]
N, R, W = RAMP["navy"], RAMP["red"], RAMP["cloth"]


def every_file(theme: dict):
    """Every file the set draws in a theme: each sample's headers (moving, still and a phone's), its footers
    and links, and every element in every variant."""
    for h, f in SAMPLES:
        for code in ("H1", "H2", "H3"):
            for wide, motion in ((True, True), (True, False), (False, False)):
                yield SET.header(code, h, theme, wide, motion)
        for code in ("F1", "F2"):
            for wide in (True, False):
                yield SET.footer(code, f, theme, wide, False)
        for i, (label, _) in enumerate(f.links):
            yield SET.link(label, theme, i)
    for d in ELEMENTS.values():
        kind = d["kind"]
        d = E.describe(kind, d)
        for variant in E.variants(kind, d):
            yield SET.element(kind, d, theme, variant)


class NightOnly(unittest.TestCase):
    def test_no_day_file_carries_a_firework(self):
        with mock.patch.object(A, "firework", wraps=A.firework) as firework:
            for _ in every_file(DAY):
                pass
            self.assertEqual(firework.call_count, 0, "a firework in a day file")
            for _ in every_file(DARK):
                pass
            self.assertGreater(firework.call_count, 0, "the night's fireworks are drawn after dark")

    def test_a_day_drawing_has_no_firework_and_no_firefly_however_it_moves(self):
        """A firework's frames lie on its own layers (fw...), a firefly's flash on a blinking one (bl...)."""
        for h, _ in SAMPLES:
            for draw in (SET.h1, SET.h2, SET.h3):
                for motion in (True, False):
                    layers = draw(h, False, motion).layers
                    self.assertEqual([n for n in layers if n.startswith(("fw", "bl"))], [], (draw.__name__, motion))
            night = SET.h1(h, True, True).layers
            self.assertTrue(any(n.startswith("fw") for n in night) and any(n.startswith("bl") for n in night))


class Badges(unittest.TestCase):
    def test_every_badge_wears_the_flags_trim(self):
        """A row of the union's blue with a white star every four pixels, over a row of red and white stripes
        two pixels long, inside the badge's own shape, on a classic badge, a plate by day and night and a
        live plate."""
        for style, s in STYLES.items():
            drawings = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                          SET.badge_swatches()["navy"][:2])]
            drawings += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            drawings.append(SET.plate_badge(style, "CI", "Failing", "pulse", "live", "red"))
            for p in drawings:
                stars = []
                for x in range(p.w):
                    if inside(x, 0, p.w, p.h, s["corner"]):
                        self.assertIn(p.get(x, 0), (N[2], W[6]), (style, x))
                        if p.get(x, 0) == W[6]:
                            stars.append(x)
                    if inside(x, 1, p.w, p.h, s["corner"]):
                        self.assertEqual(p.get(x, 1), R[3] if (x // 2) % 2 == 0 else W[5], (style, x))
                self.assertTrue(stars, style)
                self.assertTrue(all(b - a == 4 for a, b in zip(stars, stars[1:])), (style, stars))


class Titles(unittest.TestCase):
    def test_every_title_is_painted_with_the_flag_and_edged_by_day(self):
        for h, _ in SAMPLES:
            for code in ("H1", "H2", "H3"):
                day, dark = (SET.header(code, h, theme, True, False) for theme in (DAY, DARK))
                self.assertIn('stroke="url(#paflg', day, code)
                self.assertIn('stroke="url(#paflg', dark, code)
                self.assertIn(f'<g stroke="{N[0]}">', day, "a day title's dark edge")


if __name__ == "__main__":
    unittest.main()
