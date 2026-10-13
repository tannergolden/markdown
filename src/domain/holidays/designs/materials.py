# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What a set's boards and its Hall's podium are made of: the grain of a square, a cell, a bar, a frame and a block,
cut from the set's own tones.

A `Stuff` is a material as a set names it: a ramp of its tones, darkest first, the tone it stands at, its grain and,
for a grain that is flecked or leaded, a second colour. Every tone a grain lays down is the stuff's own or a step
either side of it on its ramp, so a board keeps to its set's closed palette, and a grain stays within a step or two of
its tone, so a piece standing on it reads as clearly as on the bare colour.

A grain is drawn once for each size and variant a file asks for (`surface`), and the board lays it where it is needed
as a symbol, so a board of sixty-four squares costs a few of them. The grains:

  flat      the bare tone
  wood      long grain lines, wavering, now and then a knot; `turned` runs them down instead of across, as
            parquet lays its dark squares
  stone     a dressed block: speckled, lit along its top and left, shaded along its foot, a crack or a pit here
            and there
  slate     stone split along its bed: fine lines across it at a slant
  tile      tesserae: little tiles in a bed of grout, each a shade of its own, every other course set over
  weave     a plain weave of cloth, the threads crossing
  stitch    laid and couched embroidery: the wool laid in slanting rows, a couching thread across them
  ivory     polished bone: a faint grain down it, a gleam at its corner
  glass     stained glass in its lead: a sheen across it, a seed of a bubble, the came round it in the second colour;
            a patch too big for one pane leaded in several, each a tone of its own
  vellum    skin prepared for writing: mottled, a follicle here and there
  wave      a sea as a chart draws it: rows of little crests
  sand      fine speckle
  snow      a drift's sparkle
  needles   pine needles, every way
  flecks    a stone flecked with the second colour, as lapis is with gold
  scales    overlapping scales, a dragon's or a heap of coins
  velvet    a pile catching the light along one side
  lace      a ground of eyelets
  veins     banded, as malachite is
  satin     a sheen running across it
  metal     a brushed plate with a rivet at each corner
  cells     cloisonne: garnets cut to a lattice of cells walled in the second colour, each catching the light
  laid      laid and couched work: long threads across, held down at intervals by a stitch catching the light

A frame (`frame`) is drawn round a board in a stuff of its own: wood with mitred corners, gilt with a row of beads,
stone in courses of ashlar, iron with rivets, a chart's neatline of alternate bars, stripes, stars, slanting bars as
the Bayeux Tapestry parts its borders, tesserae, a strip of cloisonne cells, or plain.

A `Podium` is what a Hall's podium is cut from, how it is worked and what it is trimmed in (`PODIUMS`): plainly;
crenellated, its blocks a castle's; tied with a ribbon, as a present is; hung with bunting in the board's colours,
with a ship's shields along its rail, with banners, or with a garland of leaves; edged in lace; or cobwebbed.
"""
from __future__ import annotations

import math
import random
from typing import NamedTuple

GRAINS = ("flat", "wood", "stone", "slate", "tile", "weave", "stitch", "ivory", "glass", "vellum", "wave", "sand",
          "snow", "needles", "flecks", "scales", "velvet", "lace", "veins", "satin", "metal", "cells", "laid")
FRAMES = ("plain", "wood", "gilt", "stone", "iron", "ink", "stripes", "stars", "bars", "tesserae", "cells")
# How a Hall's podium may be worked beyond its stuff: plainly; crenellated, its blocks a castle's; tied in a ribbon, as
# a present is; hung with bunting, with a ship's shields along its top, with banners, or with a garland of leaves;
# edged in lace; or cobwebbed in its corners.
PODIUMS = ("plain", "crenels", "ribbon", "bunting", "shields", "banners", "garland", "lace", "cobwebs")


class Stuff(NamedTuple):
    """A material: its ramp of tones, darkest first; the tone it stands at; its grain; and the second colour a
    flecked or leaded grain, or a striped frame, is laid with."""
    ramp: tuple
    at: int
    grain: str = "flat"
    fleck: str | None = None

    @property
    def base(self) -> str:
        return self.ramp[self.at]

    def tone(self, d: int) -> str:
        """The tone `d` steps up (lighter) or down (darker) the ramp from the stuff's own, held at its ends."""
        return self.ramp[max(0, min(len(self.ramp) - 1, self.at + d))]

    @property
    def key(self) -> tuple:
        """What tells one stuff from another, for keeping each of its drawings once: its ramp may be a list."""
        return tuple(self.ramp), self.at, self.grain, self.fleck

    @property
    def tokens(self) -> frozenset:
        return frozenset(c.upper() for c in (*self.ramp, *((self.fleck,) if self.fleck else ())))


class Podium(NamedTuple):
    """What a Hall's podium is cut from (`stuff`), how it is worked (`style`, one of `PODIUMS`), and what it is
    trimmed in (`trim`): its ribbon, its banners, its lace or the shields along it. Bunting is hung in the board's
    own two colours, and banners and shields alternate the trim with them."""
    stuff: Stuff
    style: str = "plain"
    trim: Stuff | None = None


def plain(colour: str) -> Stuff:
    """A colour as a stuff with no grain: a ramp of one tone."""
    return Stuff((colour,), 0)


# --------------------------------------------------------------------------- the grains
def _bevel(cells: dict, s: Stuff, w: int, h: int, lit: int = 1, shade: int = -1) -> None:
    for x in range(w):
        cells[(x, 0)] = s.tone(lit)
        cells[(x, h - 1)] = s.tone(shade)
    for y in range(1, h - 1):
        cells[(0, y)] = s.tone(lit)
        cells[(w - 1, y)] = s.tone(shade)


def _wood(s, w, h, rnd, turned):
    cells = {}
    phase = rnd.random() * 6.3
    gap = 3 + rnd.randint(0, 1)
    u, v = (h, w) if turned else (w, h)          # u runs along the grain, v across it
    for j in range(v):
        for i in range(u):
            wave = round(math.sin(i / (5.5 + gap) + phase + j * .35) * 1.2)
            k = (j + wave + int(phase * 3)) % (gap + 2)
            c = s.base
            if k == 0 and rnd.random() < .82:
                c = s.tone(-1)
            elif k == gap and rnd.random() < .22:
                c = s.tone(1)
            cells[(j, i) if turned else (i, j)] = c
    if rnd.random() < .35 and min(w, h) >= 12:
        kx, ky = rnd.randint(3, w - 4), rnd.randint(3, h - 4)
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                if (dx, dy) in ((-2, -1), (2, -1), (-2, 1), (2, 1)):
                    continue
                cells[(kx + dx, ky + dy) if not turned else (kx + dy, ky + dx)] = s.tone(-1)
        cells[(kx, ky)] = s.tone(-2)
    return cells


def _stone(s, w, h, rnd, variant, quiet=False):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for (x, y) in list(cells):
        r = rnd.random()
        if r < .07:
            cells[(x, y)] = s.tone(-1)
        elif r < .11:
            cells[(x, y)] = s.tone(1)
    if variant % 3 == 1 and min(w, h) >= 10 and not quiet:
        x, y = rnd.randint(2, w // 2), rnd.randint(2, h // 2)
        for _ in range(rnd.randint(4, 8)):
            cells[(x, y)] = s.tone(-2)
            x, y = x + rnd.choice((0, 1, 1)), y + rnd.choice((0, 1))
            if not (1 <= x < w - 1 and 1 <= y < h - 1):
                break
    elif variant % 3 == 2 and min(w, h) >= 6 and not quiet:
        for _ in range(2):
            x, y = rnd.randint(2, w - 3), rnd.randint(2, h - 3)
            cells[(x, y)] = s.tone(-2)
            cells[(x + 1, y)] = s.tone(-1)
    _bevel(cells, s, w, h)
    return cells


def _slate(s, w, h, rnd, variant):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    step = 5
    off = rnd.randint(0, step - 1)
    for y in range(h):
        for x in range(w):
            k = (x + 2 * y + off) % (step * 2)
            if k == 0 and rnd.random() < .7:
                cells[(x, y)] = s.tone(-1)
            elif k == 1 and rnd.random() < .25:
                cells[(x, y)] = s.tone(1)
    _bevel(cells, s, w, h)
    return cells


def _tile(s, w, h, rnd, variant):
    t = 4 if min(w, h) >= 16 else 3
    grout = s.fleck or s.tone(-2)
    cells = {(x, y): grout for y in range(h) for x in range(w)}
    pitch = t + 1
    for row in range(-1, h // pitch + 2):
        off = (pitch // 2) * (row % 2) + variant
        for col in range(-1, w // pitch + 2):
            r = rnd.random()
            c = s.tone(1) if r < .22 else s.tone(-1) if r < .36 else s.base
            x0, y0 = col * pitch - off + 1, row * pitch + 1
            for y in range(y0, y0 + t):
                for x in range(x0, x0 + t):
                    if 0 <= x < w and 0 <= y < h:
                        cells[(x, y)] = c
                        if (x, y) == (x0, y0) and r > .7:
                            cells[(x, y)] = s.tone(1)
    return cells


def _weave(s, w, h, rnd, variant):
    """A plain weave: the weft's threads passing over two warps and under two, every other row set over, so the
    cloth reads in little ridges; a thread lit here and there."""
    cells = {}
    for y in range(h):
        for x in range(w):
            c = s.base
            if y % 2 == 0 and (x + (y // 2) % 2 * 2 + variant) % 4 < 2:
                c = s.tone(-1)
            elif y % 4 == 3 and (x + variant) % 9 == 0:
                c = s.tone(1)
            cells[(x, y)] = c
    return cells


def _stitch(s, w, h, rnd, variant):
    cells = {}
    for y in range(h):
        for x in range(w):
            k = (x + 2 * y + variant) % 4
            c = s.tone(-1) if k == 0 else s.tone(1) if k == 2 and (x + y) % 3 == 0 else s.base
            cells[(x, y)] = c
    for y in range(2 + variant % 3, h, 6):
        for x in range(w):
            if (x + y) % 3 != 2:
                cells[(x, y)] = s.tone(-2) if x % 3 == 0 else s.tone(-1)
    return cells


def _ivory(s, w, h, rnd, variant, quiet=False):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for x in range(1, w - 1):
        if rnd.random() < .16 and not quiet:
            c = s.tone(1) if (x + variant) % 3 else s.tone(-1)
            y0 = rnd.randint(0, h // 2)
            for y in range(y0, min(h - 1, y0 + rnd.randint(h // 3, h))):
                if rnd.random() < .7:
                    cells[(x, y)] = c
    for i in range(3):
        for j in range(3 - i):
            cells[(1 + i, 1 + j)] = s.tone(2)
    for x in range(w):
        cells[(x, h - 1)] = s.tone(-1)
    for y in range(h):
        cells[(w - 1, y)] = s.tone(-1)
    return cells


def _glass(s, w, h, rnd, variant):
    """Glass in its lead: a pane lit along a band across it, or a patch too big for one pane leaded in several, each
    a tone of its own as the panes of a window are."""
    came = s.fleck or s.tone(-3)
    if max(w, h) <= 30:
        return _pane(s, w, h, rnd, variant, came)
    cols, rows = max(1, round(w / 15)), max(1, round(h / 15))
    xs = [round(i * (w - 1) / cols) for i in range(cols + 1)]
    ys = [round(j * (h - 1) / rows) for j in range(rows + 1)]
    cells = {}
    for j in range(rows):
        for i in range(cols):
            tone = (0, 1, 0, -1, 1, 0)[(i * 5 + j * 3 + variant) % 6]
            pane = Stuff(s.ramp, max(1, min(len(s.ramp) - 3, s.at + tone)), s.grain, s.fleck)
            for (x, y), c in _pane(pane, xs[i + 1] - xs[i] + 1, ys[j + 1] - ys[j] + 1, rnd, i + j, came).items():
                cells[(xs[i] + x, ys[j] + y)] = c
    return cells


def _pane(s, w, h, rnd, variant, came):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    band = w // 3 + variant % 3
    for y in range(h):
        for x in range(w):
            d = x - y
            if band <= d <= band + 1:
                cells[(x, y)] = s.tone(1)
            elif d == band + 3 and (x + y) % 2 == 0:
                cells[(x, y)] = s.tone(2)
            elif x + y > w + h - 8:
                cells[(x, y)] = s.tone(-1)
    for _ in range(2 if min(w, h) >= 6 else 0):
        bx, by = rnd.randint(2, w - 3), rnd.randint(2, h - 3)
        cells[(bx, by)] = s.tone(2)
    for x in range(w):
        cells[(x, 0)] = came
        cells[(x, h - 1)] = came
    for y in range(h):
        cells[(0, y)] = came
        cells[(w - 1, y)] = came
    return cells


def _vellum(s, w, h, rnd, variant, quiet=False):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for _ in range(max(2, w * h // 160) if not quiet else 0):
        cx, cy, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(2.5, 5)
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if (x, y) in cells and math.hypot(x - cx, y - cy) < r and rnd.random() < .3:
                    cells[(x, y)] = s.tone(-1)
    for (x, y) in list(cells):
        if rnd.random() < .012:
            cells[(x, y)] = s.tone(-2)
    return cells


def _wave(s, w, h, rnd, variant):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for i, y0 in enumerate(range(1 + variant % 2, h - 1, 4)):
        off = (i * 3 + variant) % 6
        for x in range(w):
            k = (x + off) % 6
            if k in (1, 2):
                cells[(x, y0)] = s.tone(1)
            elif k in (0, 3) and y0 + 1 < h:
                cells[(x, y0 + 1)] = s.tone(1)
    return cells


def _sand(s, w, h, rnd, variant):
    cells = {}
    for y in range(h):
        for x in range(w):
            r = rnd.random()
            cells[(x, y)] = s.tone(-1) if r < .12 else s.tone(1) if r < .2 else s.base
    return cells


def _snow(s, w, h, rnd, variant, quiet=False):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for _ in range(w * h // 40):
        cells[(rnd.randint(0, w - 1), rnd.randint(0, h - 1))] = s.tone(-1)
    for _ in range((1 + variant % 2 + (w * h) // 300) if min(w, h) >= 8 and not quiet else 0):
        x, y = rnd.randint(2, w - 3), rnd.randint(2, h - 5)
        cells[(x, y)] = s.fleck or s.tone(2)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cells[(x + dx, y + dy)] = s.tone(1)
    return cells


def _needles(s, w, h, rnd, variant):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for _ in range(w * h // 11):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        dx = rnd.choice((-1, 1))
        c = s.tone(-1) if rnd.random() < .6 else s.tone(1)
        for i in range(3):
            if 0 <= x + i * dx < w and 0 <= y + i < h:
                cells[(x + i * dx, y + i)] = c
    return cells


def _flecks(s, w, h, rnd, variant):
    cells = {}
    for y in range(h):
        for x in range(w):
            r = rnd.random()
            cells[(x, y)] = (s.fleck or s.tone(2)) if r < .028 else s.tone(1) if r < .07 else \
                s.tone(-1) if r < .13 else s.base
    return cells


def _scales(s, w, h, rnd, variant):
    """Rows of scales, each a cup open to the top, every row set half a scale over and overlapping the row above:
    its rim in the shade, a gleam on its upper left."""
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    sw, sh = 6, 4
    cup = [(-3, 0), (-3, 1), (-2, 2), (-1, 3), (0, 3), (1, 3), (2, 2), (2, 1)]
    for row in range(-2, h // sh + 2):
        off = (sw // 2) * (row % 2) + variant
        for col in range(-1, w // sw + 2):
            cx, top = col * sw - off + 3, row * sh
            for (dx, dy) in cup:
                x, y = cx + dx, top + dy
                if 0 <= x < w and 0 <= y < h:
                    cells[(x, y)] = s.tone(-1)
            for (dx, dy) in ((-1, 1), (-2, 1)):
                x, y = cx + dx, top + dy
                if 0 <= x < w and 0 <= y < h:
                    cells[(x, y)] = s.tone(1)
    return cells


def _velvet(s, w, h, rnd, variant):
    """Pile catching the light along its upper left and falling into shade at its lower right, a few tufts lit."""
    cells = {}
    for y in range(h):
        for x in range(w):
            d = x + y
            c = s.base
            if d < 3 or (d < 6 and (x + y) % 2 == 0 and x % 2 == 0):
                c = s.tone(1)
            elif d > w + h - 5 or (d > w + h - 9 and x % 2 == 0 and y % 2 == 1):
                c = s.tone(-1)
            elif rnd.random() < .03:
                c = s.tone(1)
            cells[(x, y)] = c
    return cells


def _lace(s, w, h, rnd, variant, quiet=False):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for cy in range(2 + variant % 2, h, 6) if not quiet else ():
        for cx in range(2 + (cy // 6 % 2) * 3, w, 6):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= cx + dx < w and 0 <= cy + dy < h:
                    cells[(cx + dx, cy + dy)] = s.tone(-1)
            if cx + 3 < w and cy + 3 < h:
                cells[(cx + 3, cy + 3)] = s.tone(-1)
    return cells


def _veins(s, w, h, rnd, variant):
    cells = {}
    phase = rnd.random() * 6.3
    for y in range(h):
        for x in range(w):
            band = (y + math.sin(x / max(w, 1) * math.pi * 1.4 + phase) * 3.5 + variant) % 5
            c = s.base
            if band < 1:
                c = s.tone(-1)
            elif 2.4 < band < 3 and (x + y) % 2 == 0:
                c = s.tone(1)
            cells[(x, y)] = c
    return cells


def _satin(s, w, h, rnd, variant):
    cells = {}
    for y in range(h):
        for x in range(w):
            t = (x + y) / (w + h)
            c = s.base
            if .55 < t < .7 or (.5 < t <= .55 and (x + y) % 2 == 0):
                c = s.tone(1)
            elif t < .12 and (x + y) % 2 == 0:
                c = s.tone(-1)
            cells[(x, y)] = c
    return cells


def _metal(s, w, h, rnd, variant):
    cells = {(x, y): s.base for y in range(h) for x in range(w)}
    for y in range(1, h - 1):
        if rnd.random() < .5:
            x0 = rnd.randint(0, w // 2)
            c = s.tone(1) if rnd.random() < .5 else s.tone(-1)
            for x in range(x0, min(w - 1, x0 + rnd.randint(w // 3, w))):
                cells[(x, y)] = c
    _bevel(cells, s, w, h)
    if min(w, h) >= 12:
        for (rx, ry) in ((2, 2), (w - 4, 2), (2, h - 4), (w - 4, h - 4)):
            cells[(rx, ry)] = s.tone(2)
            cells[(rx + 1, ry)] = s.tone(1)
            cells[(rx, ry + 1)] = s.tone(1)
            cells[(rx + 1, ry + 1)] = s.tone(-2)
    return cells


def _laid(s, w, h, rnd, variant):
    """Laid and couched work, as an embroidery fills a ground: long threads laid across it, every third row in the
    shadow between two, held down at intervals by a stitch across them that catches the light."""
    cells = {}
    for y in range(h):
        for x in range(w):
            c = s.base
            if y % 3 == 2:
                c = s.tone(1) if (x + (y // 3) * 5 + variant) % 10 == 0 else s.tone(-1)
            cells[(x, y)] = c
    return cells


def _cells(s, w, h, rnd, variant):
    """Cloisonne: garnets cut to fit a lattice of cells walled in gold (the fleck), not laid in courses as tiles are,
    every other one a shade deeper, each lit at its top-left where the foil behind it catches the light."""
    wall = s.fleck or s.tone(-2)
    cells = {(x, y): wall for y in range(h) for x in range(w)}
    pitch = 5 if min(w, h) >= 16 else 4
    for row, y0 in enumerate(range(1, h, pitch)):
        for col, x0 in enumerate(range(1, w, pitch)):
            deep = (row + col + variant) % 2
            for y in range(y0, min(h, y0 + pitch - 1)):
                for x in range(x0, min(w, x0 + pitch - 1)):
                    edge = x == x0 + pitch - 2 or y == y0 + pitch - 2
                    cells[(x, y)] = s.tone(-1 - deep) if edge else s.tone(-deep)
            cells[(x0, y0)] = s.tone(2)
            if x0 + 1 < w:
                cells[(x0 + 1, y0)] = s.tone(1)
    return cells


# The grains whose figures, in a patch too small for them, read as marks rather than as grain: stone's cracks and
# pits, ivory's streaks, vellum's mottles, snow's sparkles and lace's eyelets. A quiet patch leaves them out.
QUIETED = frozenset({"stone", "ivory", "vellum", "snow", "lace"})


def surface(s: Stuff, w: int, h: int, variant: int = 0, turned: bool = False, quiet: bool = False) -> dict:
    """A patch of the stuff `w` by `h`, {(x, y): colour} with its top-left at (0, 0), in one of a few variants so
    neighbouring squares are not the same; the same for the same arguments every time. A `quiet` patch keeps its
    grain's speckle, bevel and gleam and leaves out the figures that would read as marks at its size."""
    rnd = random.Random(f"{s.grain}/{s.base}/{w}x{h}/{variant}/{turned}")
    g = s.grain
    if g == "flat" or len(s.ramp) < 2:
        return {(x, y): s.base for y in range(h) for x in range(w)}
    if g == "wood":
        return _wood(s, w, h, rnd, turned)
    if g in ("stone", "slate", "tile", "weave", "stitch", "ivory", "glass", "vellum", "wave", "sand", "snow",
             "needles", "flecks", "scales", "velvet", "lace", "veins", "satin", "metal", "cells", "laid"):
        grain = globals()[f"_{g}"]
        return grain(s, w, h, rnd, variant, quiet=True) if quiet and g in QUIETED else grain(s, w, h, rnd, variant)
    raise ValueError(f"no such grain: {g}")


def lay(p, s: Stuff, x: int, y: int, w: int, h: int, variant: int = 0, turned: bool = False, L: str = "squares",
        z: float = -1, quiet: bool = False) -> None:
    """The stuff laid as a patch with its top-left at (x, y), drawn once in the file and placed wherever it is
    needed: on its own layer under everything a board carries, unless `L` names another; `quiet` as `surface`."""
    key = ("stuff", s.key, w, h, variant, turned, quiet)
    if key not in p.syms:
        p.symbol(key, surface(s, w, h, variant, turned, quiet))
    if L not in p.layers:
        p.layer(L, z=z)
    p.use(key, x, y, L)


# --------------------------------------------------------------------------- the frames
def frame(p, s: Stuff, style: str, x0: int, y0: int, w: int, h: int, t: int, night: bool, L: str = "base") -> None:
    """A frame `t` wide round the area from (x0, y0), `w` by `h`, in the stuff `s` and the style `style`: its
    shadow cast down and to the right, its body, the light along its top and left edges and the shade along its
    foot and right, and its outline."""
    ox0, oy0, ox1, oy1 = x0 - t, y0 - t, x0 + w + t, y0 + h + t
    shade = s.tone(-3)
    for y in range(oy0 + 2, oy1 + 3):
        for x in range(ox0 + 2, ox1 + 3):
            if x >= ox1 or y >= oy1:
                p.px(x, y, f"{shade}:{'0.5' if night else '0.3'}", L)

    def side(x, y) -> str:
        """Which side of the frame (x, y) is on: top, left, foot or right, a corner split on its diagonal."""
        dt, dl, db, dr = y - oy0, x - ox0, oy1 - 1 - y, ox1 - 1 - x
        m = min(dt, dl, db, dr)
        return "top" if m == dt else "left" if m == dl else "foot" if m == db else "right"

    rnd = random.Random(f"frame/{style}/{s.base}/{w}x{h}/{t}")
    for y in range(oy0, oy1):
        for x in range(ox0, ox1):
            if x0 <= x < x0 + w and y0 <= y < y0 + h:
                continue
            sd = side(x, y)
            across = {"top": y - oy0, "left": x - ox0, "foot": oy1 - 1 - y, "right": ox1 - 1 - x}[sd]
            along = x - ox0 if sd in ("top", "foot") else y - oy0
            lit = sd in ("top", "left")
            c = s.base
            if style == "wood":
                c = s.tone(-1) if (along // 2 + across * 3 + (along * 7) % 5) % 6 == 0 else s.base
                if across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            elif style == "gilt":
                mid = t // 2
                if across == mid:
                    c = s.tone(2) if along % 3 == 0 else s.tone(-1) if along % 3 == 2 else s.base
                elif across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
                elif across == t - 1:
                    c = s.tone(-2)
            elif style == "stone":
                joint = (along + (6 if across * 2 >= t else 0)) % 12 == 0
                r = rnd.random()
                c = s.tone(-2) if joint else s.tone(-1) if r < .1 else s.tone(1) if r < .14 else s.base
                if across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            elif style == "iron":
                if across == t // 2 and along % 10 == 5:
                    c = s.tone(2)
                elif across == t // 2 + 1 and along % 10 == 5:
                    c = s.tone(-2)
                elif across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            elif style == "ink":
                ink, ground = s.base, s.fleck or s.tone(5)
                if across in (0, t - 1):
                    c = ink
                elif across == t // 2 or (t > 3 and across == t // 2 - 1):
                    c = ink if (along // 6) % 2 == 0 else ground
                else:
                    c = ground
            elif style == "stripes":
                c = s.base if ((x + y) // 3) % 2 == 0 else (s.fleck or s.tone(3))
                if across == 0:
                    c = s.tone(-2)
            elif style == "stars":
                if across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            elif style == "bars":
                # slanting bars across the band in the second colour, as the Bayeux Tapestry parts its borders
                c = (s.fleck or s.tone(3)) if (along - across) % 9 in (0, 1) else s.base
                if across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            elif style == "tesserae":
                # little tiles in two colours turn about in a bed of grout, as a mosaic's border is laid
                if across == 0 or across == t - 1 or along % 3 == 2:
                    c = s.tone(-2) if across or not lit else s.tone(1)
                else:
                    c = (s.fleck or s.tone(2)) if (along // 3) % 2 else s.base
                    if along % 3 == 0 and across == 1:
                        c = s.tone(1) if c == s.base else c
            elif style == "cells":
                # gold walls round a row of garnets down the band's middle, each catching the light at its top left,
                # as a cloisonne strip is set
                if 0 < across < t - 1 and along % 4 != 3:
                    c = s.fleck or s.tone(-2)
                    if across == 1 and along % 4 == 0:
                        c = s.tone(3)
                elif across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            else:
                if across == 0:
                    c = s.tone(1) if lit else s.tone(-2)
            if across == t - 1 and style not in ("ink", "gilt"):
                c = s.tone(-2)
            p.px(x, y, c, L)
    if style == "wood":
        for (cx, cy, dx, dy) in ((ox0, oy0, 1, 1), (ox1 - 1, oy0, -1, 1), (ox0, oy1 - 1, 1, -1),
                                 (ox1 - 1, oy1 - 1, -1, -1)):
            for i in range(t):
                p.px(cx + dx * i, cy + dy * i, s.tone(-2), L)
    if style == "stars":
        # a star every few pixels down the middle of each side, in the second colour, as a flag's canton carries them
        star = s.fleck or s.tone(4)
        mid = t // 2
        spots = [(x, oy0 + mid) for x in range(ox0 + mid + 4, ox1 - mid - 3, 9)]
        spots += [(x, oy1 - 1 - mid) for x in range(ox0 + mid + 4, ox1 - mid - 3, 9)]
        spots += [(ox0 + mid, y) for y in range(oy0 + mid + 9, oy1 - mid - 8, 9)]
        spots += [(ox1 - 1 - mid, y) for y in range(oy0 + mid + 9, oy1 - mid - 8, 9)]
        for (sx, sy) in spots:
            p.px(sx, sy, star, L)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(sx + dx, sy + dy, star, L)
    p.box(ox0 - 1, oy0 - 1, ox1 - ox0 + 2, oy1 - oy0 + 2, shade, L)
