# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The badges' drawings: the badges kit's own, byte for byte, in every style, plate, print and state."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
import xml.dom.minidom as minidom

from tests import support

from domain.badges import classic as C
from domain.badges import data as BD
from domain.badges import plates as P
from domain.palette import PALETTE
from domain.prints import PRINTS

support.install()
GOLDEN = json.loads((support.ROOT / "tests" / "fixtures" / "badges" / "golden.json").read_text(encoding="utf-8"))


def drawn(kw: dict) -> str:
    """One fixture badge, drawn by the renderer its style names."""
    style = kw.get("style", C.DEFAULT_STYLE)
    if style in P.BLUEPRINT_STYLES:
        if kw.get("state"):
            return P.render_live(kw.get("label", ""), kw.get("message", ""), kw.get("icon"), style, kw["state"],
                                 tuple(kw.get("reserve", ())))
        return P.render_blueprint(kw.get("label", ""), kw.get("message", ""), kw.get("icon"), style,
                                  kw.get("print", P.DEFAULT_PRINT), kw.get("dark", False),
                                  tuple(kw.get("reserve", ())))
    return C.render(kw.get("label", ""), kw.get("message", ""), kw.get("label_color", "black"),
                    kw.get("message_color", "blue"), kw.get("icon"), style)


class TheBadgesKitsOwn(unittest.TestCase):
    def test_every_badge_is_drawn_byte_for_byte_as_the_badges_kit_drew_it(self):
        self.assertGreater(len(GOLDEN["badges"]), 250)
        for case in GOLDEN["badges"]:
            svg = drawn(case["badge"])
            self.assertEqual(hashlib.sha256(svg.encode()).hexdigest(), case["sha256"], case["badge"])

    def test_every_badge_is_well_formed_deterministic_stamped_and_passes_the_lint(self):
        for case in GOLDEN["badges"]:
            svg = drawn(case["badge"])
            minidom.parseString(svg)
            self.assertEqual(svg, drawn(case["badge"]))
            self.assertEqual(svg.count(BD.STAMP), 1)
            self.assertEqual(BD.lint(svg), [], case["badge"])


class Styles(unittest.TestCase):
    def test_every_style_declares_every_geometry_key(self):
        keys = set(C.STYLES[C.DEFAULT_STYLE])
        for name, g in C.STYLES.items():
            self.assertEqual(set(g), keys, name)

    def test_corner_radius_never_exceeds_half_the_height(self):
        for name, g in C.STYLES.items():
            self.assertLessEqual(g["rx"], g["h"] / 2 + 1e-9, name)

    def test_every_sheen_is_a_real_gradient(self):
        for name, g in C.STYLES.items():
            if g["sheen"] is not None:
                self.assertIn(g["sheen"], C.SHEENS, name)

    def test_every_style_is_grouped_once_and_the_default_leads(self):
        seen = [s for _, _, group in C.STYLE_GROUPS for s in group]
        self.assertEqual(sorted(seen), sorted(C.STYLES))
        self.assertEqual(next(iter(C.STYLES)), C.DEFAULT_STYLE)
        self.assertEqual(C.STYLE_GROUPS[0][2][0], C.DEFAULT_STYLE)

    def test_a_scaled_style_measures_proportionally(self):
        norm = C._text_width("Passing", C._W_NORM11, 9.0, 0.0)
        small = C.STYLES["compact"]
        scaled = C._text_width("Passing", small["table"], small["fallback"], 0.0) * small["mscale"]
        self.assertAlmostEqual(scaled, norm * (9 / 11), places=6)

    def test_an_unknown_colour_or_style_is_refused(self):
        with self.assertRaises(C.BadgeError):
            C.render("A", "B", "black", "chartreuse")
        with self.assertRaises(C.BadgeError):
            C.render("A", "B", style="3d")

    def test_the_rotation_pool_holds_no_state_slot_or_label_colour(self):
        pool = set(C.STATIC_RANDOM_POOL)
        for tok in C.HEALTH_COLORS | C.HEALTH_NEUTRAL | {"black", "gold", "white", "pink", "purple"}:
            self.assertNotIn(tok, pool)
        self.assertEqual(C.STATIC_RANDOM_POOL, sorted(C.STATIC_RANDOM_POOL))


class Plates(unittest.TestCase):
    def test_every_style_has_a_twin_with_its_geometry(self):
        for key, g in C.STYLES.items():
            twin = P.BLUEPRINT_STYLES[P.BLUEPRINT + key]
            for field in ("h", "pad", "icon", "gap", "rx", "sheen", "caps"):
                self.assertEqual(twin[field], g[field], f"{key}.{field}")
        self.assertEqual(len(P.BLUEPRINT_STYLES), len(C.STYLES))

    def test_every_colour_is_a_palette_token(self):
        tokens = {v.upper() for v in PALETTE.values()}
        svgs = [P.render_blueprint("A", "B", "pulse", s, t, d)
                for s in P.BLUEPRINT_STYLES for t in PRINTS for d in (False, True)]
        svgs += [P.render_live("A", "B", "pulse", s, st) for s in P.BLUEPRINT_STYLES for st in P.STATE_PRINT]
        for svg in svgs:
            for hexc in re.findall(r"#[0-9A-Fa-f]{6}\b", svg):
                self.assertIn(hexc.upper(), tokens)

    def test_yellow_is_not_drawn_in_the_gold_family(self):
        svg = P.render_live("Coverage", "78%", None, state="yellow")
        self.assertIn(PALETTE["tangerine"], svg)
        self.assertNotIn(PALETTE["mustard"], svg)

    def test_reserve_holds_the_width(self):
        width = lambda svg: int(re.search(r'width="(\d+)"', svg).group(1))
        values = ("Passing", "Failing", "Pending")
        widths = {width(P.render_live("Build", v, "check", state="green", reserve=values)) for v in values}
        self.assertEqual(len(widths), 1)

    def test_the_lettering_is_paths_never_text(self):
        svg = P.render_blueprint("Build Status", "Passing", "check")
        self.assertNotIn("<text", svg)
        self.assertIn("<title>Build Status: Passing</title>", svg)

    def test_two_plates_can_share_a_page(self):
        ids = lambda svg: set(re.findall(r'\bid="([^"]+)"', svg))
        a = P.render_blueprint("Build", "Passing", None, "blueprint-flat")
        b = P.render_blueprint("Build", "Passing", None, "blueprint-flat", "redprint")
        self.assertFalse(ids(a) & ids(b))

    def test_an_unknown_print_names_where_a_repository_adds_its_own(self):
        with self.assertRaisesRegex(C.BadgeError, "under prints in its settings"):
            P.render_blueprint("A", "B", tone="goldprint")


if __name__ == "__main__":
    unittest.main()
