# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""What the games are played with, in pixels: every set's chessmen, men, discs and marks, at the sizes its sheets set.

A pixel set draws the four games with one set of pieces, the way it strikes its trophies in one set of metals: a
White piece is ivory and a Black one ebony in every set, so a reader knows the house's pieces from GitHub's at a
glance whichever holiday or month is up. Each is shaded on its material's seven-tone ramp under the engine's one
lamp, up and to the left, its outline the ramp's darkest tone, never pure black, as a collection's hand asks of every
sprite, and an ebony piece catches the lamp along its lit edge, so it holds on a dark square and on the night sky.

  chessmen   hand-drawn silhouettes, at three sizes: a wide board's square, a phone's, and a mini for a tray, a
             medallion or the Hall's mark of a game. Turned pieces are shaded as turned wood is, across each row
             as a column lit from the left; the knight's head the same way, its eye cut dark
  men        a checkers man seen from a little above: its face an ellipse, its milled side a band under it, a
             groove round its face; a king two men stacked with a crown on its face
  discs      Pentago's marbles face on, as its holes show them, a groove round each face, lit as a coin is
  marks      Tic-Tac's X and O as the pen draws them, strokes with a body, lit as a rope is, an X as heavy as an O
             and an ivory X's bars bevelled, so it holds on a set's light squares as the O does

Every drawing here is a map of (x, y) to a colour, its top-left at (0, 0), made once for each size and material
and kept: a sheet stamps it wherever it stands. Nothing here belongs to one set.
"""
from __future__ import annotations

import math
from functools import lru_cache

from ..pixel import LX, LY, LZ

# The two materials, dark to light: ivory, warm, its shadows leaning purple as the engine's ramps do; and ebony,
# cool, its lights lifting toward a grey violet so its lit edge shows on a dark ground.
IVORY = ("#3B2A1F", "#7A6150", "#A88E74", "#CDB797", "#E7D8BB", "#F7EEDB", "#FFFCF2")
EBONY = ("#0C0A12", "#1D1824", "#2D2636", "#3E3549", "#5A4F66", "#7D7290", "#A69DB8")
RAMPS = {"light": IVORY, "dark": EBONY}
TOKENS = frozenset(c.upper() for ramp in RAMPS.values() for c in ramp)

# The chessmen's silhouettes, by size: `#` the piece, `d` a carved line (two tones down), `e` its darkest (an
# eye). Each is drawn symmetrical about its middle column, its foot on its last row.
CHESS = {
    "wide": {
        "king": """
......#......
.....###.....
...#######...
.....###.....
......#......
...#######...
..#########..
.###########.
.###########.
..#########..
..#########..
...#######...
..#########..
....#####....
....#####....
...#######...
..#########..
#############
#############""",
        "queen": """
......#......
.#...###...#.
.##...#...##.
.###.###.###.
..#########..
..#########..
...#######...
...#######...
....#####....
...#######...
....#####....
....#####....
....#####....
...#######...
..#########..
#############
#############""",
        "rook": """
.##.##.##.##.
.##.##.##.##.
.###########.
..#########..
...#######...
...#######...
...#######...
...#######...
...#######...
...#######...
...#######...
..#########..
.###########.
#############
#############""",
        "bishop": """
......#......
.....###.....
......#......
.....###.....
....##d##....
...###d###...
...##d####...
...#######...
....#####....
...#######...
....#####....
....#####....
....#####....
...#######...
..#########..
#############
#############""",
        "knight": """
.....#.......
....###......
....####.....
...######....
..########...
.##e#######..
############.
############.
###..#######.
.....#######.
....########.
....########.
...#########.
..##########.
.###########.
#############
#############""",
        "pawn": """
.....###.....
....#####....
....#####....
....#####....
.....###.....
...#######...
....#####....
....#####....
....#####....
...#######...
..#########..
.###########.
#############
#############""",
    },
    "narrow": {
        "king": """
.....#.....
....###....
.....#.....
..#######..
.#########.
.#########.
..#######..
...#####...
..#######..
...#####...
...#####...
..#######..
###########
###########""",
        "queen": """
.....#.....
.#..###..#.
.##..#..##.
.##.###.##.
..#######..
..#######..
...#####...
...#####...
..#######..
...#####...
...#####...
..#######..
###########
###########""",
        "rook": """
##.##.##.##
###########
.#########.
..#######..
..#######..
..#######..
..#######..
..#######..
.#########.
###########
###########""",
        "bishop": """
.....#.....
....###....
.....#.....
....###....
...##d##...
...#d###...
...#####...
....###....
...#####...
....###....
....###....
..#######..
###########
###########""",
        "knight": """
....#......
...###.....
...####....
..######...
.##e#####..
##########.
##########.
##..######.
....######.
...#######.
..########.
.#########.
###########
###########""",
        "pawn": """
....###....
...#####...
...#####...
....###....
...#####...
....###....
....###....
...#####...
..#######..
###########
###########""",
    },
    "mini": {
        "king": """
...#...
..###..
...#...
.#####.
.#####.
..###..
..###..
.#####.
#######""",
        "queen": """
...#...
#.###.#
##.#.##
.#####.
..###..
..###..
.#####.
#######""",
        "rook": """
#.#.#.#
#######
.#####.
.#####.
.#####.
#######
#######""",
        "bishop": """
...#...
..###..
..#d#..
..###..
...#...
..###..
.#####.
#######""",
        "knight": """
..#....
.####..
#####..
##.###.
...###.
..####.
#######""",
        "pawn": """
..###..
..###..
...#...
..###..
.#####.
#######""",
    },
}
# How a chessman stands in a square of each size: the side of the square it is drawn for.
SQUARE = {"wide": 23, "narrow": 19}


def _art(rows: str) -> dict:
    """A silhouette's characters by (x, y), its blank cells left out."""
    lines = rows.strip("\n").split("\n")
    return {(x, y): ch for y, line in enumerate(lines) for x, ch in enumerate(line) if ch != "."}


def tone_at(v: float, x: int, y: int, lo: int, hi: int) -> int:
    """A value on a ramp, rounded, with a checkerboard where two tones meet, as the engine shades."""
    b = math.floor(v)
    f = v - b
    if f >= .62 or (f > .38 and (x + y) % 2 == 0):
        b += 1
    return max(lo, min(hi, b))


def outlined(cells: dict, ramp: tuple, body: set | None = None) -> dict:
    """`cells` with an outline round them in the ramp's darkest tone, pushed one pixel right and down so the whole
    starts at (0, 0) again."""
    body = set(cells) if body is None else body
    out = {(x + 1, y + 1): c for (x, y), c in cells.items()}
    for (x, y) in body:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in body and (q[0] + 1, q[1] + 1) not in out:
                out[(q[0] + 1, q[1] + 1)] = ramp[0]
    return out


def turned(art: dict, ramp: tuple, rim: bool, lo: int = 2, hi: int = 5) -> dict:
    """A silhouette shaded as a turned piece: each row of it a column lit from the left, a top lit from above and
    an underside in shade; a carved line two tones down, an eye in the darkest. On a dark material the edge toward
    the lamp catches it."""
    body = set(art)
    out = {}
    for (x, y), ch in art.items():
        a, b = x, x
        while (a - 1, y) in body:
            a -= 1
        while (b + 1, y) in body:
            b += 1
        nx = 2 * (x + .5 - a) / (b + 1 - a) - 1
        nz = math.sqrt(max(0.0, 1 - nx * nx))
        ny = -.6 if (x, y - 1) not in body else (.5 if (x, y + 1) not in body else 0.0)
        lam = max(0.0, nx * LX + ny * LY + nz * LZ)
        t = tone_at(lo + (hi - lo + .6) * lam, x, y, lo - 1, hi)
        if rim and x == a and b - a >= 2:
            t = max(t, hi)
        if x == b and b - a >= 2:
            t = min(t, lo)
        if ch == "d":
            t = max(1, t - 2)
        elif ch == "e":
            t = 0
        out[(x, y)] = ramp[min(len(ramp) - 1, t)]
    return outlined(out, ramp)


@lru_cache(maxsize=None)
def chessman(kind: str, size: str, material: str) -> tuple:
    """A chessman of `kind` in `material` (light or dark) at `size` (wide, narrow or mini), outlined: its cells as
    ((x, y), colour) pairs, its width and its height."""
    cells = turned(_art(CHESS[size][kind]), RAMPS[material], material == "dark")
    w = max(x for x, _ in cells) + 1
    h = max(y for _, y in cells) + 1
    return tuple(sorted(cells.items())), w, h


# --------------------------------------------------------------------------- the men
def _ellipse(cx: float, cy: float, rx: float, ry: float) -> set:
    return {(x, y) for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 1)
            for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 1)
            if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1}


CROWN = {  # a crown laid on a king's face, by how wide it may be: rows of `#`, centred
    3: ["#.#", "###"],
    5: ["#.#.#", "#####"],
    7: ["#..#..#", "##.#.##", "#######"],
    9: ["#...#...#", "##.###.##", "#########"],
}


@lru_cache(maxsize=None)
def man(material: str, rx: int, ry: int, t: int, king: bool = False) -> tuple:
    """A checkers man `2 rx` wide, its face `2 ry` deep and its side `t` thick, seen from a little above, in
    `material`: its face lit, a groove round it, its milled side in shade below; a king two men stacked, the seam
    between them cut dark and a crown on its face. Its cells, width and height, outlined."""
    ramp = RAMPS[material]
    dark = material == "dark"
    w = 2 * rx
    stack = 2 if king else 1
    body: dict = {}
    seam: set = set()
    for level in range(stack):                       # the lowest man first, each drawn over the one below
        top = ry + (stack - 1 - level) * t               # its face's centre
        foot = top + t                                   # its foot's centre
        side = {(x, y) for (x, y) in _ellipse(rx, foot, rx, ry) if y >= foot} | \
            {(x, y) for x in range(w) for y in range(top, foot + 1)}
        for (x, y) in side:
            if not 0 <= x < w:
                continue
            nx = 2 * (x + .5) / w - 1
            lam = max(0.0, nx * LX + math.sqrt(max(0.0, 1 - nx * nx)) * LZ)
            v = tone_at(1.4 + 2.4 * lam, x, y, 1, 3)
            if rx >= 6 and x % 2 == 1 and 0 < x < w - 1:
                v = max(1, v - 1)                        # the milled edge
            if dark and x == 0:
                v = 4                                    # the lamp along an ebony man's lit edge
            body[(x, y)] = v
        if level:                                        # the seam: the foot of the man stacked on another
            seam |= {(x, y) for (x, y) in side if y >= foot and (x, y + 1) not in side and 0 <= x < w}
        face = _ellipse(rx, top, rx, ry)
        ring = _ellipse(rx, top, rx * .64, ry * .64) - _ellipse(rx, top, rx * .64 - 1.1, max(ry * .64 - 1.1, .4))
        for (x, y) in face:
            if 0 <= x < w:
                dx, dy = (x + .5 - rx) / rx, (y + .5 - top) / ry
                lam = max(0.0, .8 - dx * .3 - dy * .5)
                v = tone_at(3.6 + 2.2 * lam, x, y, 3, 6 if not dark else 5)
                if (x, y) in ring and rx >= 4:
                    v -= 2
                body[(x, y)] = v
    for xy in seam:
        if xy in body:
            body[xy] = 0
    if king:
        crown = CROWN[max((k for k in CROWN if k <= max(3, rx)), default=3)]
        ox, oy = rx - len(crown[0]) // 2, ry - len(crown) // 2
        for j, row in enumerate(crown):
            for i, ch in enumerate(row):
                if ch == "#":
                    body[(ox + i, oy + j)] = 1 if not dark else 6
    cells = {xy: ramp[max(0, min(6, v))] for xy, v in body.items()}
    out = outlined(cells, ramp)
    return tuple(sorted(out.items())), w + 2, max(y for _, y in out) + 1


# --------------------------------------------------------------------------- the discs
@lru_cache(maxsize=None)
def disc(material: str, r: float) -> tuple:
    """A Pentago marble of radius `r` face on, as its hole shows it, in `material`: lit as a coin, brighter toward
    the lamp, its rim rolling off into shade, a groove round its face. Its cells, width and height, outlined."""
    ramp = RAMPS[material]
    dark = material == "dark"
    n = math.ceil(2 * r)
    c = n / 2
    body = {}
    for y in range(n):
        for x in range(n):
            dx, dy = (x + .5 - c) / r, (y + .5 - c) / r
            d = math.hypot(dx, dy)
            if d > 1:
                continue
            lam = max(0.0, -(dx * .62 + dy * .62) * .55 + .62)
            v = tone_at(2.4 + 2.6 * lam, x, y, 2, 5)
            if d > .82:                                # the rim, rolling off: lit on the lamp's side
                v = 5 if dx * LX + dy * LY > .25 else (2 if not dark else 1)
                if dark and dx * LX + dy * LY > .25:
                    v = 5
            elif .5 < d <= .62:                        # the groove round the face
                v -= 2 if not dark else 1
            body[(x, y)] = v
    if r >= 4:
        best = min(body, key=lambda q: math.hypot(q[0] + .5 - (c + LX * r * .45), q[1] + .5 - (c + LY * r * .45)))
        body[best] = 6
    cells = {xy: ramp[max(0, min(6, v))] for xy, v in body.items()}
    out = outlined(cells, ramp)
    return tuple(sorted(out.items())), n + 2, n + 2


# --------------------------------------------------------------------------- the marks
def _stroke_cells(segments, rad: float, size: int) -> dict:
    """Each pixel within `rad` of one of `segments` ((x0, y0, x1, y1), ...): the across-stroke offset (-1 to 1) and
    the stroke's direction, for shading as a rope."""
    out = {}
    for y in range(size):
        for x in range(size):
            px_, py_ = x + .5, y + .5
            best = None
            for (x0, y0, x1, y1) in segments:
                dx, dy = x1 - x0, y1 - y0
                L2 = dx * dx + dy * dy
                t = max(0.0, min(1.0, ((px_ - x0) * dx + (py_ - y0) * dy) / L2)) if L2 else 0.0
                qx, qy = x0 + t * dx, y0 + t * dy
                d = math.hypot(px_ - qx, py_ - qy)
                if d <= rad and (best is None or d < best[0]):
                    n = math.sqrt(L2) or 1
                    nx, ny = -dy / n, dx / n
                    o = ((px_ - qx) * nx + (py_ - qy) * ny) / rad
                    best = (d, o, nx, ny)
            if best:
                out[(x, y)] = best[1:]
    return out


@lru_cache(maxsize=None)
def pen(mark: str, material: str, size: int) -> tuple:
    """X or O, the pen's mark, filling a box `size` square, in `material`: a stroke with a body, lit as a rope is,
    its outline the ramp's darkest. Its cells, width and height, outlined.

    An X is drawn as heavy as an O, its bars a little thicker and reaching as far as the O's ring, and an ivory X's
    bars are bevelled: each lit along its upper flank and shaded along its lower, whichever way it runs, so the bar
    that falls toward the lamp is not flat. Ivory's light tones alone would lose it on a set's light squares."""
    ramp = RAMPS[material]
    dark = material == "dark"
    rad = max(1.2, size * .105)
    m = size * .2 + rad * .4
    if mark == "X":
        rad = max(1.35, size * .12)
        m = size * .1 + rad * .5
        segs = [(m, m, size - m, size - m), (size - m, m, m, size - m)]
    else:
        R = size / 2 - m * .55 - rad * .35
        n = max(24, int(R * 3))
        pts = [(size / 2 + R * math.cos(2 * math.pi * i / n), size / 2 + R * math.sin(2 * math.pi * i / n))
               for i in range(n + 1)]
        segs = [(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:])]
    shaded = {}
    for (x, y), (o, nx, ny) in _stroke_cells(segs, rad, size).items():
        nz = math.sqrt(max(0.0, 1 - o * o))
        lam = max(0.0, (nx * o) * LX + (ny * o) * LY + nz * LZ)
        v = tone_at(1.8 + 3.6 * lam, x, y, 1 if not dark else 2, 5 if not dark else 5)
        if mark == "X" and not dark:
            # the lamp's fall across the bar, steepened toward the vertical, so both bars take a bevel
            f = max(-1.0, min(1.0, o * (nx * LX * .45 + ny * LY * 1.3)))
            v = tone_at(3.9 + 2.4 * f, x, y, 2, 6)
        if dark and o * (nx * LX + ny * LY) > .55:
            v = 5
        shaded[(x, y)] = ramp[v]
    out = outlined(shaded, ramp)
    return tuple(sorted(out.items())), size + 2, size + 2


def placed(drawing: tuple, x: int, y: int) -> dict:
    """A drawing's cells with its top-left at (x, y)."""
    cells, _, _ = drawing
    return {(x + dx, y + dy): c for (dx, dy), c in cells}
