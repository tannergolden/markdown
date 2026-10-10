# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The medieval hand's month mark: the month's sign of the zodiac, in gold, on a roundel of lapis ringed in gold.

Medieval calendars marked each month with its sign, so every header of a page
on the medieval collection's calendar carries one, the same in all twelve
designs: a band of gold leaf round a field of lapis lazuli, and the month's
sign laid on the field in gold. It is shaded on the engine's ramps by the
engine's one light, up and to the left: the band is raised, so the light
finds its outer upper left and its inner lower right, the field is sunk in
the band's shadow along its upper left, and the sign stands proud of the
field and casts its shadow down and to the right. Its outline is the darkest
gold, never black.

The signs are drawn as glyphs in a medieval hand rather than as the figures
some calendars painted, the water bearer, the fish, the ram and the rest.
Both were tried at the size a reader sees them, two pixels a unit, where the
field is eleven units across. As figures the ram, the bull, the crab and the
scales could just be made out, but the water bearer, the twins, the maiden,
the archer, the goat-fish and the fish could not, and the twelve must be in
one style. As glyphs every sign reads.

It is the same by day and by night. In a moving header its gold catches one
faint glint, on the engine's twinkle cadence; a still file has none. It is
drawn in layers of its own over the scene, so a scene's lights and garlands
stay behind it, and what it covers is left out of the file. Each of its
discs is drawn whole, so every row of each is a single stroke: it takes 790
to 900 bytes of a file, by its sign, and its glint some 50 more where the
scene twinkles already, or some 220 where the glint brings the twinkling.
"""
from __future__ import annotations

import math

from ..holidays.pixel import LX, LY, LZ, make_ramp

GOLD = make_ramp("#D4A13A")      # gold leaf, dark to light
LAPIS = make_ramp("#2F4DA6")     # lapis lazuli, dark to light
TOKENS = frozenset(GOLD + LAPIS)
SIZE = 17                        # the roundel's width and height, in units
Z = 9.5                          # the depth it is drawn at: over the scene, just under the twinkling its glint joins
RING, FIELD = 7.5, 5.5           # the radii of the gold band's outer edge and of the lapis field inside it

# The signs, January's first: Aquarius in January to Capricorn in December, as the medieval calendar sets them.
SIGNS = ("Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn")

# Each sign as a glyph, `#` for gold, at most nine units square, its corners left clear so it lies on the field.
GLYPHS = {
    "Aquarius": [       # two waves
        "..#...#..",
        ".#.#.#.#.",
        "#...#...#",
        ".........",
        "..#...#..",
        ".#.#.#.#.",
        "#...#...#",
    ],
    "Pisces": [         # two fish back to back, tied
        "#.......#",
        ".#.....#.",
        "..#...#..",
        "..#####..",
        "..#...#..",
        ".#.....#.",
        "#.......#",
    ],
    "Aries": [          # the ram's horns
        ".##...##.",
        "#..#.#..#",
        "#..#.#..#",
        "....#....",
        "....#....",
        "....#....",
        "....#....",
    ],
    "Taurus": [         # the bull's head and horns
        "#.......#",
        ".#.....#.",
        "..#####..",
        ".#.....#.",
        ".#.....#.",
        ".#.....#.",
        "..#####..",
    ],
    "Gemini": [         # the twins, two pillars
        ".#######.",
        "..#...#..",
        "..#...#..",
        "..#...#..",
        "..#...#..",
        "..#...#..",
        ".#######.",
    ],
    "Cancer": [         # the crab's claws
        "...#####.",
        ".##.....#",
        "#..#.....",
        ".##......",
        "......##.",
        ".....#..#",
        "#.....##.",
        ".#####...",
    ],
    "Leo": [            # the lion's mane and tail
        "...###...",
        "..#...#..",
        "..#...#..",
        "..#...#..",
        ".###..#..",
        "#..#..#..",
        "#..#..#.#",
        ".##....#.",
    ],
    "Virgo": [          # the maiden's m, looped
        ".##.##...",
        "#..#..#..",
        "#..#..#..",
        "#..#..#..",
        "#..#..###",
        "#..#..#.#",
        "......##.",
        "......#..",
    ],
    "Libra": [          # the scales
        "...###...",
        "..#...#..",
        "..#...#..",
        "###...###",
        ".........",
        "#########",
    ],
    "Scorpio": [        # the scorpion's m and its sting
        ".##.##...",
        "#..#..#..",
        "#..#..#..",
        "#..#..#..",
        "#..#..#.#",
        "#..#...##",
        ".......##",
    ],
    "Sagittarius": [    # the archer's arrow
        "....####.",
        "......##.",
        ".....#.#.",
        ".#..#..#.",
        "..##.....",
        "..##.....",
        ".#..#....",
        "#........",
    ],
    "Capricorn": [      # the goat-fish
        ".#.#.....",
        "#..#.....",
        ".##.#....",
        "....#.##.",
        "....##..#",
        "....#...#",
        "...#.###.",
        "..#......",
    ],
}


def sign(month: int) -> str:
    """The sign a month is marked with: Aquarius for January, month 1."""
    return SIGNS[month - 1]


def _disc(r: float) -> set:
    """The units within `r` of the roundel's middle unit, as offsets from it."""
    n = SIZE // 2
    return {(dx, dy) for dy in range(-n, n + 1) for dx in range(-n, n + 1) if math.hypot(dx, dy) <= r}


def _light() -> dict:
    """How much of the engine's light falls on each unit of the gold band, 0 to 1. The band is a raised ring, so
    across it the surface turns from facing in to facing out, and the lamp up and to the left finds its outer
    upper left and its inner lower right."""
    mid, half = (RING + FIELD) / 2, (RING - FIELD) / 2
    out = {}
    for dx, dy in _disc(RING) - _disc(FIELD):
        d = math.hypot(dx, dy)
        o = max(-1.0, min(1.0, (d - mid) / half))
        nz = math.sqrt(max(0.0, 1 - o * o))
        out[(dx, dy)] = max(0.0, dx / d * o * LX + dy / d * o * LY + nz * LZ)
    return out


LIGHT = _light()
# Where the glint catches: the brightest unit on the band's outer upper left, where the eye looks for the shine.
GLINT = max((xy for xy in LIGHT if xy[0] + xy[1] < 0), key=LIGHT.get)


def _glyph(month: int) -> set:
    """The units of a month's glyph, as offsets from the roundel's middle."""
    art = GLYPHS[sign(month)]
    ox, oy = -(max(len(r) for r in art) // 2), -(len(art) // 2)
    return {(ox + i, oy + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch == "#"}


def layers(month: int) -> list:
    """Month `month`'s roundel as layers drawn low to high, each a map of offsets from its middle to colours.

    The outline, the gold band and the lapis field are each a whole disc, laid
    one over another, so every row of each is one stroke. Over them lie the
    light on the band, the band's shadow on the field's upper left, the sign
    in gold, and the sign's shadow, one unit down and to the right of it."""
    field = _disc(FIELD)
    glyph = _glyph(month)
    top = {xy: GOLD[5] if lam > 0.88 else GOLD[4] for xy, lam in LIGHT.items() if lam > 0.62}
    for dx, dy in field:
        d = math.hypot(dx, dy)
        if d > FIELD - 1.6 and (dx * LX + dy * LY) / d > 0.35:
            top[(dx, dy)] = LAPIS[2]
    for x, y in glyph:
        if (x + 1, y + 1) in field and (x + 1, y + 1) not in glyph:
            top[(x + 1, y + 1)] = LAPIS[2]
    top.update({xy: GOLD[4] for xy in glyph})
    return [{xy: GOLD[0] for xy in _disc(SIZE / 2)}, {xy: GOLD[3] for xy in _disc(RING)},
            {xy: LAPIS[3] for xy in field}, top]


class Roundel:
    """The medieval hand's month mark, `size` units square, painting only its `tokens`."""

    size = SIZE
    tokens = TOKENS

    def __call__(self, p, cx: int, cy: int, month: int, night: bool = False, motion: bool = False):
        """Draw month `month`'s roundel on `p` centred on the unit (cx, cy), the same by day and by night, and in a
        moving header the glint its gold catches.

        Every pixel the drawing holds under the roundel, on any layer, is taken
        out first: it would be hidden, or it would be laid over the roundel. The
        glint is laid on the twinkling layer the scene already uses, when it uses
        one, so it costs the file a stroke rather than a layer of its own."""
        drawn = layers(month)
        covered = {(cx + dx, cy + dy) for dx, dy in drawn[0]}
        for cells in p.layers.values():
            for xy in covered & cells.keys():
                del cells[xy]
        for i, cells in enumerate(drawn):
            name = p.layer("mark" + (str(i) if i else ""), z=Z + i / 10)
            for (dx, dy), c in cells.items():
                p.px(cx + dx, cy + dy, c, name)
        if motion:
            glint = p.twinkle(next((i for i in range(3) if p.layers.get(f"tw{i}")), 0))
            gx, gy = cx + GLINT[0], cy + GLINT[1]
            for x, y in ((gx, gy - 1), (gx - 1, gy), (gx, gy), (gx + 1, gy), (gx, gy + 1)):
                p.apx(x, y, GOLD[6], 0.6, glint)


ROUNDEL = Roundel()
