# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A schematic's wires and their labels stay inside its border, in every renderer that draws one.

A wire that has to pass a box in its own column runs down a channel beside the column, and beside the
last column that channel is outside the boxes; on a phone, every wire that skips a row takes a channel of
its own at the right. This README's own schematic once ran its KEEPS wire down the margin outside the
sheet's border. Each layout here is drawn by the prints, the standard theme and every holiday set, wide
and on a phone, and every point of every wire, and every label turned to run along one, has to land
inside the border.
"""
from __future__ import annotations

import re
import unittest
from unittest import mock

from tests import support

from domain import collections, holidays as H, pixelsets
from domain.canvas import DAY
from domain.elements import data as ED
from domain.elements import draw as E
from domain.holidays.pixel import Pix
from domain.standard import elements as SE
from infra.yaml_reader import loads

support.install()


def _section(path) -> dict:
    return loads(path.read_text(encoding="utf-8"))["elements"]


def _box(title: str, icon: str = "grid", note=None) -> dict:
    out = {"title": title, "path": f"{title.lower().replace(' ', '/')}.yml", "icon": icon}
    if note:
        out["note"] = note
    return out


def _spec(boxes: list[str], wires: list[tuple], groups: dict | None = None, ins: dict | None = None) -> dict:
    spec = {"kind": "schematic", "title": "Stress", "desc": "A layout built to push wires toward the border.",
            "boxes": {k: _box(k.upper()) for k in boxes}, "wires": [list(w) for w in wires]}
    if groups:
        spec["groups"] = groups
        for k, g in (ins or {}).items():
            spec["boxes"][k]["in"] = g
    return spec


# Layouts that send wires toward the edges: round the last column, many channels on a phone, stacked
# layers bypassed in every column, a cycle, and groups that lift the first row.
STRESS = {
    "round the last column": _spec(
        ["stub", "settings", "kit", "measure", "draw", "lock", "commit"],
        [("stub", "kit", "CALLS"), ("settings", "kit", "READ"), ("kit", "measure", "MEASURES"),
         ("measure", "draw", "DRAWS"), ("measure", "lock", "KEEPS"), ("draw", "commit", "WRITES")]),
    "every wire skips": _spec(
        ["a", "b", "c", "d", "e", "f", "g"],
        [("a", "b", "NEXT"), ("b", "c", "NEXT"), ("c", "d", "NEXT"), ("d", "e", "NEXT"), ("e", "f", "NEXT"),
         ("f", "g", "NEXT"), ("a", "c", "SKIPS"), ("a", "d", "SKIPS"), ("a", "e", "SKIPS"), ("a", "f", "SKIPS"),
         ("a", "g", "SKIPS"), ("b", "d", "SKIPS"), ("b", "e", "SKIPS"), ("b", "f", "SKIPS"), ("c", "e", "SKIPS"),
         ("c", "g", "SKIPS"), ("d", "f", "SKIPS"), ("d", "g", "SKIPS")]),
    "stacked in every column": _spec(
        ["s1", "s2", "s3", "m1", "m2", "m3", "e1", "e2", "e3"],
        [("s1", "m1", "A"), ("s2", "m2", "B"), ("s3", "m3", "C"), ("s1", "m3", "AROUND"), ("m1", "e1", "D"),
         ("m2", "e2", "E"), ("m3", "e3", "F"), ("m1", "e3", "AROUND"), ("s2", "e2", "LONG")]),
    "a cycle": _spec(["one", "two", "three", "four"],
                     [("one", "two", "GO"), ("two", "three", "GO"), ("three", "one", "BACK"), ("three", "four", "OUT")]),
    "groups": _spec(
        ["in", "parse", "check", "draw", "out"],
        [("in", "parse", "READS"), ("parse", "check", "CHECKS"), ("check", "draw", "DRAWS"), ("parse", "draw", "SKIPS"),
         ("draw", "out", "WRITES")],
        groups={"kit": "THE KIT"}, ins={"parse": "kit", "check": "kit", "draw": "kit"}),
}


def layouts() -> dict:
    """Every schematic the test draws: this README's own, the specimen's, and the stress layouts."""
    found = {"this README": _section(support.ROOT / ".github" / "markdown.yaml")["how-it-runs"],
             "the driftmark specimen": _section(support.ROOT / "tests" / "fixtures" / "driftmark" / ".github"
                                                / "markdown.yaml")["how-it-runs"]}
    found.update(STRESS)
    out = {}
    for name, spec in found.items():
        merged = ED.merged(ED.check({"s": spec}), {}, subject="octo/octo", today="2026-10-07")
        out[name] = E.describe("schematic", merged["s"])
    return out


def _turned(svg: str) -> list[float]:
    """The x of every label turned to run along a wire."""
    return [float(m.group(1)) for m in re.finditer(r"rotate\(-90 ([\d.]+) [\d.]+\)", svg)]


class Inside(unittest.TestCase):
    def assertInside(self, what: str, xs, lo: float, hi: float) -> None:
        xs = list(xs)
        self.assertTrue(xs, f"{what}: nothing drawn")
        out = [x for x in xs if not lo <= x <= hi]
        self.assertFalse(out, f"{what}: x {sorted(set(out))} outside {lo}..{hi}")

    def test_the_prints_keep_every_wire_inside_the_border(self):
        for name, d in layouts().items():
            for variant in ("wide", "narrow"):
                g = E.geometry(variant)
                seen = []
                real = E._wire

                def spy(cv, col, pts, *a, **k):
                    seen.append(list(pts))
                    return real(cv, col, pts, *a, **k)
                with self.subTest(layout=name, variant=variant), mock.patch.object(E, "_wire", spy):
                    svg = E.schematic(d, "blueprint", DAY, variant)
                    lo, hi = g["B"] + 6, g["W"] - g["B"] - 6
                    self.assertInside(f"{name} {variant} wires", (x for pts in seen for x, _ in pts), lo, hi)
                    turned = _turned(svg)
                    if turned:
                        self.assertInside(f"{name} {variant} labels", turned, lo, hi)

    def test_the_standard_theme_keeps_every_wire_inside_its_margin(self):
        for name, d in layouts().items():
            for variant in ("wide", "narrow"):
                W = SE.NARROW if variant == "narrow" else SE.WIDE
                seen = []
                real = SE._wire

                def spy(cv, std, width, pts, *a, **k):
                    seen.append(list(pts))
                    return real(cv, std, width, pts, *a, **k)
                with self.subTest(layout=name, variant=variant), mock.patch.object(SE, "_wire", spy):
                    svg = SE.schematic(d, DAY, variant)
                    lo, hi = SE.PAD, W - SE.PAD - 4
                    self.assertInside(f"{name} {variant} wires", (x for pts in seen for x, _ in pts), lo, hi)
                    turned = _turned(svg)
                    if turned:
                        self.assertInside(f"{name} {variant} labels", turned, lo, hi)

    def test_every_pixel_set_keeps_every_wire_inside_its_frame(self):
        # Every holiday's set, and every collection's design drawn so far.
        designs = [k for c in collections.COLLECTIONS.values() for k in c.keys if collections.is_drawn(k)]
        for key in [*H.SETS, *designs]:
            held = pixelsets.drawn_by(key)
            cls = type(held)
            for name, d in layouts().items():
                for variant, W in (("wide", 415), ("narrow", 180)):
                    seen, upright = [], []
                    real_wire, real_vtext = cls.wire, Pix.vtext

                    def wire(self, p, night, pts, *a, **k):
                        seen.append(list(pts))
                        return real_wire(self, p, night, pts, *a, **k)

                    def vtext(self, x, y, s, c, *a, **k):
                        upright.append(x)
                        return real_vtext(self, x, y, s, c, *a, **k)
                    with self.subTest(set=key, layout=name, variant=variant), \
                            mock.patch.object(cls, "wire", wire), mock.patch.object(Pix, "vtext", vtext):
                        held.draw_element("schematic", d, False, variant, None)
                        # The frame is 4 px; a wire keeps 2 more, and an upright label's backing is 7 wide.
                        self.assertInside(f"{key} {name} {variant} wires", (x for pts in seen for x, _ in pts), 6, W - 6)
                        if upright:
                            self.assertInside(f"{key} {name} {variant} labels", (x - 1 for x in upright), 4, W - 4 - 7)

    def test_this_readmes_keeps_wire_runs_inside_the_blueprint_border(self):
        # The case that was reported: KEEPS, round the last column, wide, in the blueprint.
        d = layouts()["this README"]
        seen = []
        real = E._wire

        def spy(cv, col, pts, label, *a, **k):
            seen.append((label, list(pts)))
            return real(cv, col, pts, label, *a, **k)
        with mock.patch.object(E, "_wire", spy):
            E.schematic(d, "blueprint", DAY, "wide")
        keeps = [pts for label, pts in seen if label == "KEEPS"]
        self.assertEqual(len(keeps), 1)
        g = E.geometry("wide")
        self.assertLessEqual(max(x for x, _ in keeps[0]), g["W"] - g["B"] - E.ROOM)


if __name__ == "__main__":
    unittest.main()
