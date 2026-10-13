# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Nothing on a pixel set's schematic touches a word: every card's own touch keeps two units clear of every word on
the sheet, and a label too long for its wire is lettered over the cards rather than left out.

@tannergolden's profile once had Halloween's pumpkin and Valentine's Day's heart sitting on the label of the group
under its first row, and its two shortest wires drawn without their labels. Every holiday's set and every collection's
design is drawn wide and on a phone, by day and by night, over every layout the wires test draws and a group set under
a row as the profile's is, and every card's touch outside the card is inked again where it was drawn.
"""
from __future__ import annotations

import unittest
from unittest import mock

from tests import support
from tests.unit.test_schematic_border import _box, layouts

from domain import collections, holidays as H, pixelsets
from domain.elements import data as ED
from domain.elements import draw as E
from domain.holidays.pixel import Pix

support.install()


class Inked(Pix):
    """A scratch canvas that keeps every solid cell drawn on it, a placed symbol's among them."""

    def __init__(self, w: int, h: int):
        super().__init__(w, h)
        self.cells_of: dict = {}
        self.placed: set = set()

    def symbol(self, key, cells=None, shapes="", mono=False):
        sid = super().symbol(key, cells, shapes, mono)
        if sid not in self.cells_of:
            pairs = cells.items() if isinstance(cells, dict) else ((xy, "") for xy in cells or ())
            self.cells_of[sid] = [xy for xy, c in pairs if ":" not in str(c)]
        return sid

    def use(self, key, x, y, L="base", stroke=None, scale=1):
        super().use(key, x, y, L, stroke, scale)
        for cx, cy in self.cells_of.get(self.syms[key], ()):
            self.placed |= {(x + cx * scale + i, y + cy * scale + j) for i in range(scale) for j in range(scale)}

    def solid(self) -> set:
        return self.placed | {xy for cells in self.layers.values() for xy, c in cells.items() if ":" not in c}


def under_a_row() -> dict:
    """A group of four cards in one column under a row of three, with a label as long as the profile's."""
    keys = ("standards", "path", "repos", "markdown", "header", "badges", "drawings", "trophies")
    boxes = {k: _box(k.upper()) for k in keys}
    for k in keys[4:]:
        boxes[k]["in"] = "page"
    spec = {"kind": "schematic", "title": "Under a row", "desc": "A group in one column under a row of three.",
            "boxes": boxes, "groups": {"page": "THIS README  ·  DRAWN, NEVER FETCHED"},
            "wires": [["standards", "path", "BY LINK"], ["path", "repos", "TEMPLATE"], ["repos", "markdown", "ONE STUB"],
                      ["markdown", "header"], ["markdown", "badges"], ["markdown", "drawings"],
                      ["markdown", "trophies", "DRAWS"]]}
    merged = ED.merged(ED.check({"s": spec}), {}, subject="octo/octo", today="2026-10-07")
    return E.describe("schematic", merged["s"])


class Touch(unittest.TestCase):
    def test_no_cards_touch_comes_within_two_units_of_a_word(self):
        # Every holiday's set, and every collection's design drawn so far.
        designs = [k for c in collections.COLLECTIONS.values() for k in c.keys if collections.is_drawn(k)]
        sheets = {**layouts(), "a group under a row": under_a_row()}
        for key in [*H.SETS, *designs]:
            held = pixelsets.drawn_by(key)
            cls = type(held)
            real = cls.node_deco
            for name, d in sheets.items():
                for variant in ("wide", "narrow"):
                    for night in (False, True):
                        cards = []

                        def deco(self, p, night_, x, y, w, h, seed, lid):
                            cards.append((p, x, y, w, h, seed, lid))
                            return real(self, p, night_, x, y, w, h, seed, lid)
                        with self.subTest(set=key, layout=name, variant=variant, night=night):
                            with mock.patch.object(cls, "node_deco", deco):
                                p = held.draw_element("schematic", d, night, variant, None)
                            # Only the sheet's own cards: the set also draws touches on scratch canvases.
                            cards = [c[1:] for c in cards if c[0] is p]
                            self.assertTrue(cards)
                            for x, y, w, h, seed, lid in cards:
                                q = Inked(p.w, p.h)
                                real(held, q, night, x, y, w, h, seed, lid)
                                touch = {(cx, cy) for cx, cy in q.solid()
                                         if not (x <= cx < x + w and y <= cy < y + h)}
                                for x0, y0, x1, y1 in p.words:
                                    # A word's box is a pixel round its letters; one more keeps two clear.
                                    near = [c for c in touch if x0 - 1 <= c[0] < x1 + 1 and y0 - 1 <= c[1] < y1 + 1]
                                    self.assertFalse(near, f"{key} {name} {variant}: the card at ({x}, {y}) "
                                                           f"inks {sorted(near)[:3]} by the word at {(x0, y0, x1, y1)}")


    def test_a_label_too_long_for_its_wire_is_lettered_over_the_cards(self):
        # Two cards side by side are joined by a wire shorter than BY LINK and TEMPLATE: each is set over
        # the gap, clear of both cards and their touch, in every set.
        designs = [k for c in collections.COLLECTIONS.values() for k in c.keys if collections.is_drawn(k)]
        d = under_a_row()
        for key in [*H.SETS, *designs]:
            held = pixelsets.drawn_by(key)
            for night in (False, True):
                lettered = []
                real = Pix.text

                def text(self, x, y, s, c, *a, **k):
                    lettered.append(s)
                    return real(self, x, y, s, c, *a, **k)
                with self.subTest(set=key, night=night), mock.patch.object(Pix, "text", text):
                    held.draw_element("schematic", d, night, "wide", None)
                    for label in ("BY LINK", "TEMPLATE", "ONE STUB", "DRAWS"):
                        self.assertIn(label, lettered, f"{key}: {label}")


if __name__ == "__main__":
    unittest.main()
