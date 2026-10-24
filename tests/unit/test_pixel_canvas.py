# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the pixel canvas writes when a set asks it to write a drawing as lightly as it can: `blocks` fills exactly
the pixels it is given with rectangles, a run merged down the rows it repeats on; and `compact` writes each solid
colour of each layer in the cheaper of the canvas's strokes and those rectangles, the same drawing unit for unit,
leaving faint pixels, the layers it is told to keep, and every colour the strokes carry more cheaply as drawn."""
from __future__ import annotations

import re
import unittest

from tests import support  # noqa: F401  (puts src/ on the path)

from domain.holidays.pixel import Pix

BLOCK = re.compile(r"([Mm])(-?\d+) ?(-?\d+)h(\d+)v(\d+)h-(\d+)z")


def filled(d: str) -> set:
    """The units the rectangles of path data `d`, as `blocks` writes it, fill: each placed relative to the last."""
    cells, at = set(), (0, 0)
    for move, x, y, w, h, back in BLOCK.findall(d):
        x, y = int(x) + (at[0] if move == "m" else 0), int(y) + (at[1] if move == "m" else 0)
        assert w == back, d
        cells |= {(x + i, y + j) for i in range(int(w)) for j in range(int(h))}
        at = (x, y)
    assert "".join("".join(m) for m in BLOCK.findall(d)) or not d
    return cells


def drawing() -> Pix:
    """A drawing with a tall flat band, a speckle, a faint wash and a mark of its own."""
    p = Pix(60, 50)
    p.rect(4, 3, 12, 40, "#224466")                                  # the band
    for i in range(30):
        p.px((i * 7) % 59, (i * 11) % 49, "#AA3322")                 # the speckle
    p.rect(30, 10, 10, 10, "#FFFFFF:0.25")                           # the wash, faint
    p.rect(40, 2, 9, 9, "#224466", p.layer("mark"))                  # the mark's own
    return p


class Blocks(unittest.TestCase):
    def test_it_fills_exactly_the_cells_it_is_given(self):
        shapes = [{(x, y) for x in range(3, 9) for y in range(2, 20)},
                  {(0, 0), (2, 0), (0, 1), (1, 1), (2, 1), (5, 7)},
                  {(x, y) for x in range(10) for y in range(10) if (x + y) % 3},
                  {(7, 7)}]
        for cells in shapes:
            self.assertEqual(filled(Pix.blocks(cells)), cells)

    def test_a_tall_band_is_one_rectangle(self):
        self.assertEqual(Pix.blocks({(x, y) for x in range(4, 16) for y in range(3, 43)}), "M4 3h12v40h-12z")


class Compact(unittest.TestCase):
    def test_it_writes_the_same_drawing_unit_for_unit_and_lighter(self):
        p, before = drawing(), drawing()
        p.compact(keep=("mark",))
        self.assertLess(len(p.svg("t", "d")), len(before.svg("t", "d")))
        band = {xy for xy, c in before.layers["base"].items() if c == "#224466"}
        (rect,) = p.shapes["base"]
        self.assertEqual(rect, f'<path fill="#224466" d="{Pix.blocks(band)}"/>')
        self.assertEqual(filled(Pix.blocks(band)), band)
        self.assertFalse(band & set(p.layers["base"]), "the band's pixels leave the layer")

    def test_faint_pixels_kept_layers_and_cheaper_strokes_stay_as_drawn(self):
        p, before = drawing(), drawing()
        p.compact(keep=("mark",))
        for colour in ("#FFFFFF:0.25", "#AA3322"):
            self.assertEqual({xy for xy, c in p.layers["base"].items() if c == colour},
                             {xy for xy, c in before.layers["base"].items() if c == colour}, colour)
        self.assertEqual(p.layers["mark"], before.layers["mark"])
        self.assertEqual(p.shapes["mark"], [])

    def test_with_nothing_kept_every_layer_is_written_lightly(self):
        p = drawing()
        p.compact()
        self.assertTrue(p.shapes["mark"])


if __name__ == "__main__":
    unittest.main()
