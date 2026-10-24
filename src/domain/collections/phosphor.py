# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Matrix hand's month mark: the month's numeral in the code's own script, glowing on a phosphor screen.

A Japanese calendar numbers its months, 一月 for January to 十二月 for
December, and the code the collection is written in falls in the same script,
so every header of a page on the Matrix collection's calendar carries the
month's numeral, the same in all twelve designs: a small screen of dark glass
in a gunmetal bezel, its numeral lit on the glass in phosphor. It is shaded on
the engine's ramps by the engine's one light, up and to the left: the bezel's
upper and left edges catch the light and its lower and right ones fall into
shade, the glass shows a gleam where its curve meets the light at its upper
left, and the numeral, lit from inside, burns white at its upper and left edges
and leaves a dim ghost of itself down and to the right on the glass, as
phosphor does. Its outline is the darkest steel, never black.

The numerals are drawn as a terminal's bitmap face draws kanji, a unit to a
stroke, at most nine units square. 十一 and 十二 set the ten and the one or
two side by side, smaller, as the face would.

It is the same by day and by night. In a moving header the numeral is decoded
once every `GLINT` seconds, the hand's period: for a fifth of a second each,
two of the code's glyphs flicker on the glass in its place before it resolves.
A still file shows the numeral alone. It is drawn in layers of its own over
the scene, so a scene's lights stay behind it, and what it covers is left out
of the file. Its names are the numerals' readings in a month's name, `ichi`
for January to `juuni` for December, the long vowel of the last three written
twice as a keyboard writes it, which a page names to carry one all year:
`sign: shichi`.
"""
from __future__ import annotations

import random

from ..holidays.pixel import make_ramp
from . import rain

STEEL = make_ramp("#55606B")     # the bezel's gunmetal, dark to light
GLASS = make_ramp("#0F2A1F")     # the screen's dark glass, dark to light
PHOSPHOR = make_ramp("#2BD46A")  # the numeral's light: the hand's flame (see `hand.MATRIX`)
TOKENS = frozenset(STEEL + GLASS + PHOSPHOR)
SIZE = 17                        # the screen's width and height, in units
Z = 9.5                          # the depth it is drawn at: over the scene, just under the twinkling
OUTER, BEZEL, FIELD = 8, 7, 5    # the half-widths of the outline, the bezel and the glass
GLINT = 10.0                     # how often the numeral is decoded, in seconds: the hand's glint
DECODE = 0.02                    # the share of the loop each of the two glyphs shows for, a fifth of a second

# The numerals' readings as a month is named, January's first: ichigatsu, nigatsu, and so to juunigatsu.
SIGNS = ("Ichi", "Ni", "San", "Shi", "Go", "Roku", "Shichi", "Hachi", "Ku", "Juu", "Juuichi", "Juuni")

# Each month's numeral as a terminal's bitmap face draws it, `#` for a lit unit, at most nine units square.
NUMERALS = {
    "Ichi": [            # 一
        "#########",
    ],
    "Ni": [              # 二
        ".#######.",
        ".........",
        ".........",
        ".........",
        "#########",
    ],
    "San": [             # 三
        ".#######.",
        ".........",
        ".........",
        "..#####..",
        ".........",
        ".........",
        "#########",
    ],
    "Shi": [             # 四
        "#########",
        "#..#.#..#",
        "#..#.#..#",
        "#..#.#..#",
        "#.#...#.#",
        "##.....##",
        "#.......#",
        "#########",
    ],
    "Go": [              # 五
        "#########",
        "...#.....",
        "...#.....",
        ".#######.",
        "...#...#.",
        "..#....#.",
        "..#....#.",
        "#########",
    ],
    "Roku": [            # 六
        "....#....",
        ".....#...",
        "#########",
        ".........",
        "..#...#..",
        ".#.....#.",
        "#.......#",
    ],
    "Shichi": [          # 七
        "...#.....",
        "...#.....",
        "...#..###",
        "######...",
        "...#.....",
        "...#.....",
        "...#....#",
        "....#####",
    ],
    "Hachi": [           # 八
        "...#.#...",
        "...#.#...",
        "...#.#...",
        "..#...#..",
        "..#...#..",
        ".#.....#.",
        "#.......#",
    ],
    "Ku": [              # 九
        "..#......",
        "..#......",
        "######...",
        "..#..#...",
        "..#..#...",
        ".#...#..#",
        "#....####",
    ],
    "Juu": [             # 十
        "....#....",
        "....#....",
        "....#....",
        "#########",
        "....#....",
        "....#....",
        "....#....",
        "....#....",
    ],
    "Juuichi": [         # 十一
        "..#......",
        "..#......",
        "..#......",
        "#####.###",
        "..#......",
        "..#......",
        "..#......",
    ],
    "Juuni": [           # 十二
        "..#......",
        "..#...##.",
        "..#......",
        "#####....",
        "..#......",
        "..#..####",
        "..#......",
    ],
}


def sign(month: int) -> str:
    """The numeral a month is marked with: Ichi for January, month 1."""
    return SIGNS[month - 1]


def _square(half: float, r: float) -> set:
    """The units of a square `half` units each side of the middle unit, its corners rounded to radius `r`."""
    n = SIZE // 2
    out = set()
    for dy in range(-n, n + 1):
        for dx in range(-n, n + 1):
            ax, ay = abs(dx), abs(dy)
            if ax > half or ay > half:
                continue
            ex, ey = ax - (half - r), ay - (half - r)
            if ex > 0 and ey > 0 and ex * ex + ey * ey > r * r + 0.3:
                continue
            out.add((dx, dy))
    return out


def _glyph(art: list) -> set:
    """The units of a glyph drawn in rows, as offsets from the middle unit."""
    ox, oy = -(max(len(r) for r in art) // 2), -(len(art) // 2)
    return {(ox + i, oy + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch == "#"}


def _numeral(month: int) -> set:
    return _glyph(NUMERALS[sign(month)])


def _lit(units: set, field: set) -> dict:
    """A glyph lit on the glass: its strokes in phosphor, white at every upper and left edge, and its ghost one
    unit down and to the right on the glass where no stroke lies."""
    out = {}
    for x, y in units:
        if (x + 1, y + 1) in field and (x + 1, y + 1) not in units:
            out[(x + 1, y + 1)] = PHOSPHOR[1]
    for x, y in units:
        edge = (x, y - 1) not in units or (x - 1, y) not in units
        out[(x, y)] = PHOSPHOR[5] if edge else PHOSPHOR[4]
    return out


def layers(month: int) -> list:
    """Month `month`'s screen as layers drawn low to high, each a map of offsets from its middle to colours.

    The outline, the bezel and the glass are each a whole square, laid one over
    another, so every row of each is one stroke. Over them lie the light and
    shade on the bezel, the glass's scanlines and its gleam, and last the
    numeral with its ghost."""
    outline, bezel, field = _square(OUTER, 3), _square(BEZEL, 2.5), _square(FIELD, 1.5)
    edges = {}
    for dx, dy in bezel - field:
        if dy <= -(BEZEL - 1) or dx <= -(BEZEL - 1):
            edges[(dx, dy)] = STEEL[4] if (dx <= -(BEZEL - 1) and dy <= -(BEZEL - 1)) else STEEL[3]
        elif dy >= BEZEL - 1 or dx >= BEZEL - 1:
            edges[(dx, dy)] = STEEL[1]
    for dx, dy in field:
        if dy % 2 == 0 and (dx, dy) not in edges:
            edges[(dx, dy)] = GLASS[0]
    for xy in ((-4, -5), (-3, -5), (-5, -4), (-5, -3)):
        if xy in field:
            edges[xy] = GLASS[3]
    return [{xy: STEEL[0] for xy in outline}, {xy: STEEL[2] for xy in bezel}, {xy: GLASS[1] for xy in field},
            edges, _lit(_numeral(month), field)]


def decoding(month: int) -> list:
    """The two glyphs of the code that flicker in the numeral's place as it is decoded, lit as it is: each a
    glyph of the rain, the same for a month every time."""
    rnd = random.Random(month * 31 + 7)
    field = _square(FIELD, 1.5)
    out = []
    for name in rnd.sample(rain.NAMES, 2):
        out.append(_lit(_glyph(rain.glyph(name)), field))
    return out


class Screen:
    """The Matrix hand's month mark, `size` units square, painting only its `tokens`."""

    size = SIZE
    tokens = TOKENS

    def __call__(self, p, cx: int, cy: int, month: int, night: bool = False, motion: bool = False):
        """Draw month `month`'s screen on `p` centred on the unit (cx, cy), the same by day and by night, and in a
        moving header the decoding that resolves into its numeral every `GLINT` seconds.

        Every pixel the drawing holds under the screen, on any layer, is taken
        out first: it would be hidden, or it would be laid over the screen."""
        drawn = layers(month)
        covered = {(cx + dx, cy + dy) for dx, dy in drawn[0]}
        for cells in p.layers.values():
            for xy in covered & cells.keys():
                del cells[xy]
        for i, cells in enumerate(drawn):
            name = "mark" + (str(i) if i else "")
            if motion and i == len(drawn) - 1:
                name = p.seq(name, 2 * DECODE, 1, GLINT, keep=True, z=Z + i / 10)
            else:
                name = p.layer(name, z=Z + i / 10)
            for (dx, dy), c in cells.items():
                p.px(cx + dx, cy + dy, c, name)
        if motion:
            for k, cells in enumerate(decoding(month)):
                name = p.seq(f"mark{len(drawn) + k}", k * DECODE, (k + 1) * DECODE, GLINT, z=Z + (len(drawn) + k) / 10)
                for (dx, dy), c in cells.items():
                    p.px(cx + dx, cy + dy, c, name)


SCREEN = Screen()
