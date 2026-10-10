# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Alchemist set's scenery and sprites, drawn on the shared pixel canvas.

The limewashed wall every sheet is, with its cracks and the old stains where something boiled over, the
oak shelves and uprights of its frame on their brass brackets, the row of glass vessels on the top shelf,
titles that turn from lead to gold, the laboratory its headers open on (the alchemist at his bench, the
alembic distilling, the retort over its spirit lamp, the bubbling flask, the armillary sphere, the hourglass,
the skull and the book of symbols, the crocodile hung from the ceiling, the round window, the furnace, the
table of the seven metals, the lantern and the herbs), the shaft of sun with its dust by day; by night the
room lit by its own lights alone, each laying a pool of its colour on the wall round it and its light into
the colours of what stands near it, the moon's cold shaft through the window, the sparks and the stars; the
footer's bottom shelf with the crucible and the goods stood along it wherever its words leave room; and the
brass and glass every element and badge is made of. Everything is shaded from the one light in the upper left
on the set's own ramps; the big quiet things (the wall, the shelves, the row of vessels) are pattern tiles of
whole pixels, so the files stay light enough to carry the rest. It is drawn in the medieval collection's hand:
every flame burns the hand's flame, the moon through the window is the hand's, the people are on the hand's
skin, and the row of vessels stands either side of the top centre a header keeps for the month's mark."""
from __future__ import annotations

import math
import random
import zlib

from ...holidays.pixel import FONTS, Paint, Pix, fold, num, sphere
from ..hand import MEDIEVAL
from .palette import C, ELIXIRS, NIGHT_SKY, RAMP, X, ramp_for, step

LIME, DUSK, OAK, BRASS = RAMP["lime"], RAMP["dusk"], RAMP["oak"], RAMP["brass"]
LEAD, GOLD, GLASS, IRON = RAMP["lead"], RAMP["gold"], RAMP["glass"], RAMP["iron"]
GREEN, VIOLET, RED, BLUE, AMBER, FIRE = (RAMP[n] for n in ("green", "violet", "red", "blue", "amber", "fire"))
BONE, SKIN, ASH, CROC, CLAY, SKY = (RAMP[n] for n in ("bone", "skin", "ash", "croc", "clay", "sky"))
MOON = MEDIEVAL.ramp("moon")      # the hand's moon, which shows through the round window by night


# The laboratory's motion: every bubble, drop, grain of sand and spark steps through the same four frames of one
# cycle, so a moving header carries four groups of frames however much moves in it.
FRAMES, BEAT = 4, 1.6


def tick(p: Pix, f: int) -> str:
    """The layer of frame `f` of the laboratory's cycle, shown for its quarter of the beat; the still file
    keeps the first."""
    f %= FRAMES
    return p.seq(f"t{f}", f / FRAMES, (f + 1) / FRAMES, BEAT, keep=f == 0, z=1)


def wall(night: bool) -> list:
    """The wall's tones: limewash by day, the same wall in the dark by night."""
    return DUSK if night else LIME


def seed_of(s: str) -> int:
    """A number drawn from a string that is the same on every run, for features a name decides."""
    return zlib.crc32(str(s).encode("utf-8"))


def _paths(cells: dict) -> str:
    """Paths for {(x, y): colour or colour:alpha}, one a colour."""
    by: dict = {}
    for (x, y), c in cells.items():
        by.setdefault(c, {}).setdefault(y, []).append(x)
    out = []
    for c, rows in sorted(by.items()):
        if ":" in c:
            col, a = c.split(":")
            out.append(f'<path stroke="{col}" stroke-opacity="{a}" d="{Pix._d(rows)}"/>')
        else:
            out.append(f'<path stroke="{c}" d="{Pix._d(rows)}"/>')
    return "".join(out)


def _art(rows: list, pal: dict, x=0, y=0) -> dict:
    """Character art as cells {(x, y): colour}, each character looked up in `pal` (absent or None is left out)."""
    return {(x + i, y + j): pal[ch] for j, row in enumerate(rows) for i, ch in enumerate(row) if pal.get(ch)}


def sprite(p: Pix, x, y, rows, pal, L="base", flip=False):
    """Character art placed with its top-left at (x, y), `flip` turning it to face the other way."""
    for (i, j), c in _art([r[::-1] for r in rows] if flip else rows, pal).items():
        p.px(x + i, y + j, c, L)


# --------------------------------------------------------------------------- the wall
TILE_W, TILE_H = 132, 90


def _wash(uid: str, night: bool, clouds: bool = True) -> str:
    """A pattern tile of the limewashed wall, 132 by 90: the lime laid on with a brush in soft clouds a shade
    lighter and a shade darker, a few flecks of grit, and fine cracks wandering through the plaster with a
    branch or two. The clouds and the cracks wrap, so the tile joins without a seam. Without its `clouds` and
    their grit the wall keeps its cracks just where they were."""
    rnd = random.Random(29)
    T = wall(night)
    light, dark, grit, crack = (T[2], T[0], T[3], T[0]) if night else (T[6], T[4], T[3], T[4])
    # The clouds the brush left: patches of a fine grain of lighter lime, and fewer of darker, each patch a few
    # overlapping ovals filled with the grain, so its edge is ragged rather than round.
    dither = (f'<pattern id="{uid}l" width="4" height="4" patternUnits="userSpaceOnUse">'
              f'<path stroke="{light}" d="M0 .5h1m1 2h1"/></pattern>'
              f'<pattern id="{uid}k" width="6" height="4" patternUnits="userSpaceOnUse">'
              f'<path stroke="{dark}" d="M1 .5h1m2 2h1"/></pattern>')
    shapes = []
    for i in range(6):
        cx, cy = rnd.uniform(0, TILE_W), rnd.uniform(0, TILE_H)
        fill = f"url(#{uid}{'l' if i % 3 else 'k'})"
        for _ in range(2):
            ox, oy = cx + rnd.uniform(-10, 10), cy + rnd.uniform(-4, 4)
            rx, ry = rnd.uniform(7, 16), rnd.uniform(3, 7)
            for dx in (-TILE_W, 0, TILE_W):
                for dy in (-TILE_H, 0, TILE_H):
                    if clouds and -rx < ox + dx < TILE_W + rx and -ry < oy + dy < TILE_H + ry:
                        shapes.append(f'<ellipse cx="{num(ox + dx)}" cy="{num(oy + dy)}" rx="{num(rx)}" '
                                      f'ry="{num(ry)}" fill="{fill}"/>')
    cells = {}
    for _ in range(26):
        c = grit if rnd.random() < 0.6 else dark      # drawn in the order the tile always drew it
        q = (rnd.randrange(TILE_W), rnd.randrange(TILE_H))
        if clouds:
            cells[q] = c
    for start, n in (((18, 8), 26), ((92, 48), 20)):
        x, y = start
        dx = rnd.choice((-1, 1))
        for i in range(n):
            cells[(x % TILE_W, y % TILE_H)] = crack
            y += 1
            if rnd.random() < 0.55:
                x += dx
            if rnd.random() < 0.18:
                dx = -dx
            if i == n // 2:
                bx, by = x, y
                for _ in range(7):
                    bx -= dx
                    by += rnd.choice((0, 1))
                    cells[(bx % TILE_W, by % TILE_H)] = crack
    return (f'{dither if clouds else ""}<pattern id="{uid}w" width="{TILE_W}" height="{TILE_H}" '
            f'patternUnits="userSpaceOnUse">{"".join(shapes)}{_paths(cells)}</pattern>')


def band_edges(h: int) -> list:
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p"):
    """The ground a drawing sits on: the limewashed wall of the laboratory, warm off-white by day; by night the
    same wall in the dark, warming a little toward the foot. The drawing keeps which sheet it is (`uid`) and
    whether it is night, for the hooks the layout calls without saying. Drawn lighter, the brush's faint clouds
    and the grit on the wall go and its cracks stay."""
    p.sheet, p.night = uid, night
    if not night:
        p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="{C["paper"]}"/>')
    else:
        edges = band_edges(p.h)
        for i, col in enumerate(NIGHT_SKY):
            p.under.append(f'<rect y="{edges[i]}" width="{p.w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    p.defs.append(_wash(uid, night, clouds=not p.lite))
    p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="url(#{uid}w)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`."""
    if not night:
        return C["paper"]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


def glow(p: Pix, cx, cy, rx, ry, col, alphas=(0.05, 0.09, 0.14), L="haze"):
    """A pool of coloured light on the wall by night, stepped in rings, strongest toward the middle."""
    p.halo(cx, cy, rx, ry, col, alphas, L=L, shape=True)


def night_glows(p: Pix):
    """By night on a sheet that is not a header, the flasks' light in its corners: a pool of green low at its
    left and of violet high at its right, the wall dark between them."""
    glow(p, 0, p.h, 130, 64, GREEN[5], (0.04, 0.07, 0.1))
    glow(p, p.w, 0, 130, 54, VIOLET[5], (0.04, 0.07, 0.1))


def stain(p: Pix, x, y, w, col, seed=0, L="haze"):
    """An old stain on the wall, seen by day, where something boiled over on the bench below and spat: a faint
    blotch `w` wide whose foot is row y, darker at its dried edge, the spatter thrown up and out round it, and a
    short run or two falling from it. A wall drawn lighter is left clean of them."""
    if getattr(p, "night", False) or p.lite:
        return
    rnd = random.Random(seed)
    cells = {}
    cx, h = x + w / 2, max(3, w // 3)
    for yy in range(y - h, y + 1):
        for xx in range(x, x + w):
            d = math.hypot((xx + 0.5 - cx) / (w / 2), (yy + 0.5 - y) / h) + rnd.uniform(-0.15, 0.15)
            if d < 1:
                cells[(xx, yy)] = 0.24 if d > 0.72 else 0.1
    for _ in range(w):
        a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
        r = rnd.uniform(0.6, 1.5)
        cells[(round(cx + math.cos(a) * r * w / 2), round(y + math.sin(a) * r * h * 1.6))] = 0.3
    for _ in range(2):
        rx, n = x + rnd.randint(2, w - 3), rnd.randint(2, 5)
        for j in range(n):
            cells[(rx, y + 1 + j)] = round(0.22 * (1 - j / n) + 0.06, 2)
    for (xx, yy), a in cells.items():
        p.apx(xx, yy, col, a, L)


# --------------------------------------------------------------------------- the frame
POST = 5          # the oak uprights' width down each side
SHELF = 10        # the row a header's top shelf stands at: the vessels stand on it, the dimension keeps under it
BOARD = 4         # the shelf board's depth
FOOT = 5          # the foot shelf's depth


def _post(uid: str, night: bool, grain: bool = True) -> str:
    """A pattern tile of an oak upright, 5 by 24: a dark arris, a lit edge, the face with its grain running
    down it in long streaks, and the shaded edge; without its `grain`, the face plain."""
    W = OAK
    k = -1 if night else 0
    cells = {}
    for y in range(24):
        cells[(0, y)] = W[0]
        cells[(1, y)] = W[5 + k]
        cells[(2, y)] = W[2 + k] if grain and (3 <= y <= 8 or 16 <= y <= 18) else W[4 + k]
        cells[(3, y)] = W[4 + k] if grain and 10 <= y <= 14 else W[3 + k]
        cells[(4, y)] = W[1]
    return f'<pattern id="{uid}" width="5" height="24" patternUnits="userSpaceOnUse">{_paths(cells)}</pattern>'


def _board(uid: str, rows: int, night: bool, y: int, grain: bool = True) -> str:
    """A pattern tile of an oak board along a shelf, 40 wide and `rows` deep from row y: its upper face lit,
    its front with the grain running along it in long streaks and a knot, and its lower edge dark; without
    its `grain`, the front plain."""
    W = OAK
    k = -1 if night else 0
    streaks = ((0, 26, 4), (26, 40, 3), (8, 19, 2), (31, 36, 2)) if grain else ()
    cells = {}
    for x in range(40):
        for j in range(rows):
            if j == 0:
                c = W[5 + k]
            elif j == rows - 1:
                c = W[0]
            else:
                c = W[3 + k]
                for (a, b, t) in streaks[(j - 1) * 2:(j - 1) * 2 + 2] if j < 3 else ():
                    if a <= x < b:
                        c = W[t + k]
            cells[(x, j)] = c
    if rows > 3 and grain:
        cells[(14, 2)] = W[1]
        cells[(15, 2)] = W[1]
    return (f'<pattern id="{uid}" y="{y}" width="40" height="{rows}" patternUnits="userSpaceOnUse">'
            f'{_paths(cells)}</pattern>')


# A brass bracket under a shelf's end, 8 by 8, its upright arm screwed to the oak upright and its arm under the
# shelf, a gusset between them pierced in a scroll. `H` is the brass lit, `m` its face, `d` its shade, `s` a screw.
BRACKET = [
    "HHHHHHHd",
    "Hsmmmsd.",
    "Hm.mmd..",
    "Hmm.d...",
    "Hsmd....",
    "Hmd.....",
    "Hd......",
    "d.......",
]
# A brass cap on an upright's top, 5 by 3.
FINIAL = [".HHm.", "HHmmd", ".mdd."]


def _brass(night: bool) -> dict:
    k = -1 if night else 0
    return {"H": BRASS[5 + k], "m": BRASS[3 + k], "d": BRASS[1], "s": BRASS[0], "h": BRASS[6 + k]}


def frame(p: Pix, night: bool, header: bool = False, footer: bool = False, uid="fr"):
    """The sheet's border in dark oak: an upright down each side, and across the top a shelf. On a header the
    shelf stands lower, at row SHELF, for the vessels to stand on, carried on brass brackets at its ends, with
    a brass cap on each upright above it; on any other sheet it is a board along the top edge, its ends
    capped in brass. Along the foot another shelf; a footer's waits for its words (see `stock`), so it can
    be as deep as they leave for its books and jars to stand on. Each piece is one tile placed along it."""
    w, h = p.w, p.h
    k = -1 if night else 0
    p.defs.append(_post(uid + "p", night, grain=not p.lite))
    for bx in (0, w - POST):
        p.shapes["base"].append(f'<rect x="{bx}" width="{POST}" height="{h}" fill="url(#{uid}p)"/>')
    foot = FOOT
    top = SHELF if header else 0
    p.defs.append(_board(uid + "t", BOARD + (0 if header else 1), night, top, grain=not p.lite))
    if header:
        p.shapes["base"].append(f'<rect x="{POST}" y="{top}" width="{w - 2 * POST}" height="{BOARD}" '
                                f'fill="url(#{uid}t)"/>')
        for xx in range(POST, w - POST):
            p.apx(xx, top + BOARD, X["shade_ink"], 0.26, "base")
            p.apx(xx, top + BOARD + 1, X["shade_ink"], 0.1, "base")
        pal = _brass(night)
        for (bx, flip) in ((POST, False), (w - POST - len(BRACKET[0]), True)):
            sprite(p, bx, top + BOARD, BRACKET, pal, flip=flip)
        for bx in (0, w - POST):
            sprite(p, bx, 0, FINIAL, pal)
    else:
        p.shapes["base"].append(f'<rect y="0" width="{w}" height="{BOARD + 1}" fill="url(#{uid}t)"/>')
        for xx in range(POST, w - POST):
            p.apx(xx, BOARD + 1, X["shade_ink"], 0.22, "base")
        for bx in (1, w - 5):
            p.hline(bx, bx + 4, 1, BRASS[5 + k])
            p.hline(bx, bx + 4, 2, BRASS[3 + k])
            p.hline(bx, bx + 4, 3, BRASS[1])
            p.px(bx + 1, 2, BRASS[0])
    if footer:
        return
    p.defs.append(_board(uid + "f", foot, night, h - foot, grain=not p.lite))
    p.shapes["base"].append(f'<rect y="{h - foot}" width="{w}" height="{foot}" fill="url(#{uid}f)"/>')
    for xx in range(POST, w - POST):
        p.apx(xx, h - foot - 1, X["shade_ink"], 0.2, "base")
    for bx in (1, w - 5):
        p.hline(bx, bx + 4, h - foot + 1, BRASS[5 + k])
        p.hline(bx, bx + 4, h - foot + 2, BRASS[3 + k])
        p.px(bx + 1, h - foot + 2, BRASS[0])
        p.hline(bx, bx + 4, h - foot + 3, BRASS[1])


# --------------------------------------------------------------------------- the vessels on the top shelf
# The glass on the top shelf, each vessel standing on row 9, the row above the shelf: a round flask stoppered
# with cork, a tall jar, a retort with its neck bent down, a phial, an alembic with its beak, a glazed jar with
# its lid, a pear-shaped flask, a brass mortar with its pestle, and a square bottle with a glass stopper. In the
# art `o` is the glass's lit edge and `O` its shaded edge, `e` empty glass with the wall behind it, `w` a glint,
# `l` `L` `d` the elixir lit, its body and its shade, `k` `K` cork, and the jar's glaze and the mortar's brass
# their own letters. Each vessel is (rows, its elixir, where its bubbles rise: (x, the rows they rise
# through)).
VESSELS = {
    "flask": (["....kk.....", "....kK.....", "....oO.....", "...ooOO....", "..oweeeO...", ".oweeeeeO..",
               "olllLLLLdO.", "oLLLLLLddO.", ".OLLLLddO..", "..OOOOOO..."], (4, (6, 8))),
    "jar": ([".kkkk..", ".kKKK..", "oooooOO", "oweeeeO", "oweeeeO", "olllLLO", "oLLLLdO", "oLLLLdO", "oLLLddO",
             "OOOOOOO"], (3, (5, 8))),
    "retort": ([".......oooo....", "......oeeeeoo..", ".....oeOOOOOeo.", "....oeO.....OOo", "..ooweO........",
                ".oweeeeO.......", "olllLLLdO......", "oLLLLLLdO......", ".OLLLLddO......", "..OOOOOO......."],
               (3, (6, 8))),
    "phial": [".kk..", ".kK..", ".oO..", "ooOOO", "oweeO", "oweeO", "olLLO", "oLLLO", "oLLdO", "OOOOO"],
    "alembic": (["...oooO.....", "..oweeeOo...", "..oeeeeOOoo.", "...oOOO...oo", "..ooooOO...o", ".oweeeeeO...",
                 "olllLLLLdO..", "oLLLLLLLdO..", ".OLLLLLddO..", "..OOOOOOO..."], (4, (6, 8))),
    "albarello": (["..........", "...aaA....", "..aaaaA...", ".bbbbbbbB.", "..bbbbbB..", ".bWWWWWWB.",
                   ".bbwbbbbB.", ".bbbbbbbB.", "..bbbbbB..", ".BBBBBBBB."], None),
    "pear": (["...kk...", "...kK...", "...oO...", "...oO...", "..oweO..", ".oweeeO.", "olllLLdO", "oLLLLLdO",
              "oLLLLddO", ".OOOOOO."], (3, (6, 8))),
    "mortar": ([".......", ".......", ".......", "......p", ".....p.", "....p..", "MMMMMMm", ".MmmmmD", "..MmmD.",
                ".MMMDD."], None),
    "bottle": (["..ww...", "..oO...", ".oOOOO.", "ooooooO", "oweeeeO", "olllLLO", "oLLLLdO", "oLLLLdO", "oLLLddO",
                "OOOOOOO"], (3, (5, 8))),
}
VESSELS["phial"] = (VESSELS["phial"], (2, (6, 8)))
# The vessels in a tile of the shelf, left to right, each with its gap after it and its elixir.
SHELF_ROW = (("flask", 2, "green"), ("jar", 2, "violet"), ("retort", 1, "amber"), ("phial", 2, "red"),
             ("alembic", 1, "blue"), ("albarello", 1, None), ("pear", 2, "violet"), ("mortar", 2, None),
             ("bottle", 2, "green"), ("phial", 2, "amber"), ("flask", 2, "red"), ("jar", 2, "blue"))


def _vessel_pal(elixir, night: bool) -> dict:
    """The tones of a vessel on the shelf by day, and by night its elixir lit from within, the glass round it
    catching its light."""
    E = RAMP[elixir] if elixir else GREEN
    if night:
        return {"o": E[4], "O": GLASS[1], "e": E[1], "w": E[6], "l": E[6], "L": E[5], "d": E[4],
                "k": OAK[4], "K": OAK[2], "a": BLUE[3], "A": BLUE[1], "b": BLUE[2], "B": BLUE[0], "W": BONE[3],
                "M": BRASS[3], "m": BRASS[2], "D": BRASS[1], "p": BRASS[4]}
    return {"o": GLASS[2], "O": GLASS[1], "e": GLASS[5], "w": C["white"], "l": E[5], "L": E[4], "d": E[3],
            "k": AMBER[3], "K": AMBER[1], "a": BLUE[4], "A": BLUE[2], "b": BLUE[3], "B": BLUE[1], "W": BONE[6],
            "M": BRASS[4], "m": BRASS[3], "D": BRASS[1], "p": BRASS[5]}


# The vessels a tile drawn lighter keeps: the first three, a flask, a jar and a retort, each of another elixir.
LITE_TILE = 3


def _shelf_tile(n=len(SHELF_ROW)):
    """Where each of the first `n` vessels of a tile of the shelf stands, (name, x, elixir), and the tile's
    width."""
    out, x = [], 0
    for name, gap, elixir in SHELF_ROW[:n]:
        out.append((name, x, elixir))
        x += len(VESSELS[name][0][0]) + gap
    return out, x


def top_centre(w: int) -> tuple:
    """The columns (x0, x1), ends excluded, that a header `w` units wide keeps clear at its top centre for the
    hand's month's mark: the box the mark is drawn in and two units either side of it (see
    `Holiday.month_mark`). A header keeps them clear whether the mark is drawn or not."""
    n = MEDIEVAL.mark_size
    x0 = w // 2 - n // 2
    return x0 - 2, x0 + n + 2


def shelf_runs(x0, x1, keep, n=len(SHELF_ROW)) -> tuple:
    """Where a tile of the first `n` vessels starts along the shelf from x0 to x1, and the runs of whole vessels
    it is laid in there, one either side of the `keep` columns: (the tile's first column, [(a, b), ...], ends
    excluded). Each run begins and ends at a gap between two vessels, so no vessel stands cut, and the tile starts
    where the two runs stand evenly about the kept columns, fill as much of the shelf as they can and leave its
    two ends alike."""
    placed, tw = _shelf_tile(n)
    widths = [(vx, len(VESSELS[name][0][0])) for name, vx, _ in placed]
    best = None
    for start in range(x0, x0 + tw):
        sides = ([], [])
        for m in range(-1, (x1 - x0) // tw + 2):
            for vx, w in widths:
                a = start + m * tw + vx
                if x0 <= a and a + w <= x1 and (a + w <= keep[0] or a >= keep[1]):
                    sides[a >= keep[1]].append((a, a + w))
        if not all(sides):
            continue
        runs = [(min(a for a, _ in side), max(b for _, b in side)) for side in sides]
        (la, lb), (ra, rb) = runs
        inner, outer = (keep[0] - lb, ra - keep[1]), (la - x0, x1 - rb)
        score = ((lb - la) + (rb - ra) - 4 * abs(inner[0] - inner[1]) - 2 * abs(outer[0] - outer[1])
                 - 3 * max(0, 2 - min(inner)))
        if best is None or score > best[0]:
            best = (score, start, runs)
    return (best[1], best[2]) if best else (x0, [])


def vessels(p: Pix, x0, x1, night, top=0, uid="vs"):
    """The row of glass vessels standing on the top shelf from x0 to x1, their feet on the row over the shelf
    at row `top` + 9: a tile of a dozen vessels repeated along the shelf in two runs, one either side of the top
    centre the header keeps for the month's mark (see `top_centre`), each beginning and ending at a gap between
    two vessels so no vessel stands cut, the shelf running on bare behind the mark (see `shelf_runs`). By day the
    glass shows the wall through it, and glints on the glass twinkle in a moving header. By night each elixir
    glows in its glass and lights the wall behind it, and bubbles rise through it, frame by frame. Drawn lighter,
    the tile is its first three vessels, repeated the more often, and everything else as it was."""
    placed, tw = _shelf_tile(LITE_TILE if p.lite else len(SHELF_ROW))
    sx, runs = shelf_runs(x0, x1, top_centre(p.w), len(placed))
    if not runs:
        return
    base, glints, glows = {}, [{}, {}, {}], []
    bubbles = [{} for _ in range(FRAMES)]
    for i, (name, vx, elixir) in enumerate(placed):
        rows, rise = VESSELS[name]
        pal = _vessel_pal(elixir, night)
        cells = _art(rows, pal, vx, 0)
        base.update(cells)
        if night and elixir:
            E = RAMP[elixir]
            cx = vx + len(rows[0]) / 2
            for dx in (-tw, 0, tw):
                if -10 < cx + dx < tw + 10:
                    glows.append(f'<ellipse cx="{num(cx + dx)}" cy="7" rx="{num(len(rows[0]) / 2 + 4)}" ry="6" '
                                 f'fill="{E[5]}"/>')
            if rise:
                bx, (lo, hi) = rise
                for f in range(FRAMES):
                    for j, yy in enumerate(range(hi, lo - 1, -1)):
                        if (j + f) % FRAMES == 0:
                            bubbles[f][(vx + bx + (j % 2), yy)] = E[6] if yy > lo else C["white"]
        elif not night:
            for (gx, gy), c in cells.items():
                if c == C["white"]:
                    glints[(i + gx) % 3][(gx, gy)] = X["glint"]
    # every layer of the row is one tile laid along both runs at once
    d = "".join(f"M{a} {top}h{b - a}v10h{a - b}z" for a, b in runs)
    glow = f'<g fill-opacity=".3">{"".join(glows)}</g>' if glows else ""
    p.defs.append(f'<pattern id="{uid}" x="{sx}" y="{top}" width="{tw}" height="10" '
                  f'patternUnits="userSpaceOnUse">{glow}{_paths(base)}</pattern>')
    p.shapes["base"].append(f'<path d="{d}" fill="url(#{uid})"/>')
    if not night:
        for f, cells in enumerate(glints):
            if cells:
                p.defs.append(f'<pattern id="{uid}g{f}" x="{sx}" y="{top}" width="{tw}" height="10" '
                              f'patternUnits="userSpaceOnUse">{_paths(cells)}</pattern>')
                p.shapes[p.twinkle(f)].append(f'<path d="{d}" fill="url(#{uid}g{f})"/>')
        return
    for f, cells in enumerate(bubbles):
        p.defs.append(f'<pattern id="{uid}b{f}" x="{sx}" y="{top}" width="{tw}" height="10" '
                      f'patternUnits="userSpaceOnUse">{_paths(cells)}</pattern>')
        p.shapes[tick(p, f)].append(f'<path d="{d}" fill="url(#{uid}b{f})"/>')


# --------------------------------------------------------------------------- the title: lead into gold
# Where along a line the lead begins to turn and where it has all turned to gold, as shares of the line.
FRONT = (0.3, 0.68)
# The order a font pixel turns in as the change passes through it: a 4 by 4 ordered dither, so the gold spreads
# through the lead in a fine grain rather than along a straight edge.
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def goldness(t: float) -> float:
    """How far the change has gone at `t` along a line, 0 (lead) to 1 (gold), eased at both ends."""
    a, b = FRONT
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)


def _metal(level: int, fr: int, fc: int) -> bool:
    """Whether the font pixel at row fr and column fc of a letter has turned to gold, `level` (0 to 4) being
    how far the change has gone in the letter: the gold creeps in from its foot first, as if it rose."""
    if level <= 0 or level >= 4:
        return level >= 4
    lean = (fr - 3) // 2
    return 4 * level + lean > BAYER[fr % 4][fc % 4]


def _metal_fill(level: int):
    """A letter's paint, `level` quarters of the way from lead to gold: its font pixels turned to gold or still
    lead, the lead dull and grey with a pit here and there, the gold bright with a sheen across its upper left,
    both lit along their tops and shaded along their feet. Night lifts the gold a step, and the lead two, as the
    flasks' light falls on it."""
    def fill(r, c, scale, night):
        fr, fc = r // scale, c // scale
        top = r == 0 and scale >= 3
        if _metal(level, fr, fc):
            band = (5, 5, 4, 4, 3, 3, 2)[min(6, fr)] + (1 if night else 0)
            if top or fr + fc == 2:
                band = 6
            return GOLD[min(6, band)]
        band = (5, 5, 4, 4, 3, 3, 2)[min(6, fr)] + (2 if night else 0)
        if top:
            band += 1
        elif (fr * 3 + fc * 5) % 7 == 0 and fr not in (0, 6):
            band -= 1
        return LEAD[max(0, min(6, band))]
    return fill


PAINTS = [Paint(f"tm{level}", _metal_fill(level), period=6) for level in range(5)]


def transmuted_title(p: Pix, x, y, s, night, scale) -> int:
    """A title that turns from lead to gold along its line: its first letters dull grey lead and its last
    bright gold, and between them the gold spreading through the lead letter by letter in a fine grain. By
    day each letter sits in a dark rim along its upper left and stands proud of the wall along its lower
    right; by night the gold glows. In a wide moving header a glint of light sweeps across the letters now
    and then. Returns the width.

    The line's letters are kept once, a group for each step of the change, and the rim, the paint, the glow
    and the glint each place those groups whole: a long title costs a few bytes a letter, not a few for each
    of its five layers."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    w = p.measure(s, "57", scale)
    cx = x
    steps: dict = {}
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(g[1]) for col in cols}, mono=True)
        level = round(4 * goldness((cx + g[0] * scale / 2 - x) / max(1, w)))
        steps.setdefault(level, []).append((key, (cx - x) // scale))
        # each letter's box, a pixel all round, as a line of text keeps its own
        p.words.append((cx - 1, y - 1, cx + g[0] * scale + 1, y + len(g[1]) * scale + 1))
        cx += (g[0] + 1) * scale
    if not steps:
        return w
    p.lines = getattr(p, "lines", 0) + 1
    tag = f"t{p.lines}l"
    move = f' transform="translate({x} {y}) scale({scale})"'
    for level, letters in sorted(steps.items()):
        p.defs.append(f'<g id="{tag}{level}"{move}>{_placed(p, letters)}</g>')
    body = []
    if not night:
        # the dark rim: the letter a pixel to its left and a pixel up, and its depth along its lower right
        off = max(1, scale // 2)
        for rim, levels in ((LEAD[0], (0, 1, 2)), (OAK[0], (3, 4))):
            uses = "".join(f'<use href="#{tag}{level}" x="-1"/><use href="#{tag}{level}" y="-1"/>'
                           f'<use href="#{tag}{level}" x="{off}" y="{off}"/>' for level in levels if level in steps)
            if uses:
                body.append(f'<g stroke="{rim}">{uses}</g>')
    elif scale >= 2 and any(level > 2 for level in steps):
        # the gold's glow: rings round each gold letter, a pixel a ring, the outermost faintest
        alphas = (0.1, 0.2) if scale >= 3 else (0.18,)
        gold = [letter for level in (3, 4) for letter in steps.get(level, ())]
        rings = []
        for i, a in enumerate(alphas):
            k = len(alphas) - i
            placed = "".join(f'<use href="#{_ring(p, key, scale, k)}"' + (f' x="{lx}"' if lx else "") + "/>"
                             for key, lx in gold)
            rings.append(f'<g stroke="{GOLD[4]}" stroke-opacity="{num(a)}"{move}>{placed}</g>')
        p.raw(-20, "".join(rings), "".join(rings))
    for level in sorted(steps):
        body.append(f'<use href="#{tag}{level}" stroke="url(#{p._pattern(PAINTS[level], scale, night)})"/>')
    p.raw(0, "".join(body), "".join(body))
    _glint(p, [f"{tag}{level}" for level in sorted(steps)], x, y, w, scale)
    return w


def _placed(p: Pix, letters) -> str:
    """The uses of a line's letters, each at its column in the face's units."""
    return "".join(f'<use href="#{p.syms[key]}"' + (f' x="{lx}"' if lx else "") + "/>" for key, lx in letters)


def _ring(p: Pix, key, scale, k) -> str:
    """The symbol of the `k`-th ring of glow round a letter, counted out from it: the letter's rows as strokes
    `k` canvas pixels longer at each end and wider, drawn once a file and placed under every gold letter."""
    gkey = ("glow", key, scale, k)
    if gkey not in p.syms:
        d = k / scale
        parts, at = [], None
        for r, cols in enumerate(FONTS[key[1]][0][key[2]][1]):
            for (rx, rw) in _runs_of(sorted(cols)):
                sx, sy = rx - d, r + 0.5
                parts.append(f"M{num(sx)} {num(sy)}h{num(rw + 2 * d)}" if at is None
                             else f"m{num(sx - at[0])} {num(sy - at[1])}h{num(rw + 2 * d)}")
                at = (sx + rw + 2 * d, sy)
        sid = f"q{len(p.syms)}"
        p.defs.append(f'<path id="{sid}" stroke-width="{num(1 + 2 * d)}" d="{"".join(parts)}"/>')
        p.syms[gkey] = sid
    return p.syms[gkey]


def _runs_of(cols) -> list:
    """The runs of neighbouring columns in a sorted row, as (start, length)."""
    runs = []
    for c in cols:
        if runs and c == runs[-1][0] + runs[-1][1]:
            runs[-1] = (runs[-1][0], runs[-1][1] + 1)
        else:
            runs.append((c, 1))
    return runs


def _glint(p: Pix, groups, x, y, w, scale):
    """A glint of light that sweeps across a title's letters every few seconds: a bright slanted streak with a
    softer one either side, seen only on the letters (the line's own groups of letters are its mask), its edges
    crisp as it moves. A title of several lines has one glint, its streak drawn at the first line and placed
    again at each line under it, all crossing at once. The still file has none."""
    h = 7 * scale + 2
    lean = h // 2
    glint = getattr(p, "glint", None)
    if glint is None:
        glint = p.glint = {"at": len(p.raws), "mask": f"tg{len(p.raws)}", "groups": [], "bands": [], "end": 0,
                           "first": (x, y, scale)}
        p.raw(9, "", "")
    x0, y0, s0 = glint["first"]
    if not glint["bands"]:
        glint["bands"].append(
            f'<g id="{glint["mask"]}b"><path d="M{x - 6} {y - 1}h2l-{lean} {h}h-2z" fill="{X["glint"]}" '
            f'fill-opacity=".35"/><path d="M{x - 4} {y - 1}h2l-{lean} {h}h-2z" fill="{C["white"]}" '
            f'fill-opacity=".85"/><path d="M{x - 2} {y - 1}h2l-{lean} {h}h-2z" fill="{X["glint"]}" '
            f'fill-opacity=".35"/></g>')
    elif scale == s0:
        glint["bands"].append(f'<use href="#{glint["mask"]}b" x="{x - x0}" y="{y - y0}"/>')
    else:
        glint["bands"].append(
            f'<path d="M{x - 6} {y - 1}h2l-{lean} {h}h-2z" fill="{X["glint"]}" fill-opacity=".35"/>'
            f'<path d="M{x - 4} {y - 1}h2l-{lean} {h}h-2z" fill="{C["white"]}" fill-opacity=".85"/>'
            f'<path d="M{x - 2} {y - 1}h2l-{lean} {h}h-2z" fill="{X["glint"]}" fill-opacity=".35"/>')
    glint["groups"] += groups
    glint["end"] = max(glint["end"], w + lean + 10)
    letters = "".join(f'<use href="#{g}"/>' for g in glint["groups"])
    moving = (f'<mask id="{glint["mask"]}" maskUnits="userSpaceOnUse" x="0" y="0" width="{p.w}" height="{p.h}">'
              f'<g stroke="{C["white"]}">{letters}</g></mask><g mask="url(#{glint["mask"]})"><g>'
              f'{"".join(glint["bands"])}<animateTransform attributeName="transform" type="translate" '
              f'values="0 0;{glint["end"]} 0;{glint["end"]} 0" keyTimes="0;.3;1" dur="{num(MEDIEVAL.glint)}s" '
              f'repeatCount="indefinite"/>'
              f'</g></g>')
    z, order, _, _ = p.raws[glint["at"]]
    p.raws[glint["at"]] = (z, order, moving, "")


# --------------------------------------------------------------------------- the bench along a rule
def _bench_tile(p: Pix, y: int, night: bool) -> str:
    """The pattern the bench's front is cut from along a rule whose top row is `y`, made once a row and a file:
    its top lit, a streak of grain along it, and its front edge catching the light; drawn lighter, plain."""
    key = ("bench", y, night)
    if key not in p.syms:
        k = -1 if night else 0
        grain = not p.lite
        cells = {}
        for x in range(26):
            cells[(x, 0)] = OAK[3 + k] if grain and x % 13 in (4, 5, 6) else OAK[4 + k]
            cells[(x, 1)] = OAK[5 + k] if grain and x % 13 in (9, 10) else OAK[6 + k]
        pid = f"bn{y}{'n' if night else 'd'}"
        p.defs.append(f'<pattern id="{pid}" y="{y}" width="26" height="2" patternUnits="userSpaceOnUse">'
                      f'{_paths(cells)}</pattern>')
        p.syms[key] = pid
    return p.syms[key]


def bench_edge(p: Pix, x0, x1, y, night, L="base"):
    """The front of the oak bench along a rule from x0 to x1: its top lit, its edge, and the rule its dark
    foot; it leaves out the columns a word lies within two units of."""
    pid = _bench_tile(p, y - 2, night)
    runs, start = [], None
    for x in range(x0, x1 + 1):
        free = x < x1 and p.clear_of_words(x - 2, y - 4, x + 3, y + 1)
        if free and start is None:
            start = x
        elif not free and start is not None:
            runs.append((start, x))
            start = None
    for a_, b_ in runs:
        p.shapes[L].append(f'<rect x="{a_}" y="{y - 2}" width="{b_ - a_}" height="2" fill="url(#{pid})"/>')


# --------------------------------------------------------------------------- light by night
def lamp(p: Pix, cx, cy, r, col, own=(), tint=1):
    """Register a light at (cx, cy): once its scene is drawn, `lights` lays its colour into the oak, the brass,
    the cloth, the bone and the clay within `r` of it, strongest nearest it. `own` are the light's own pixels,
    which it leaves as they are; `tint` is how many tones lighter than their own the pale things near it take
    its colour, 0 for a strong light held close, like molten gold or a fire, and None for a light that only
    lightens them like everything else. What a drawing keeps in `p.unlit` no light changes: a broad flat thing,
    like the parchment of the table of metals, takes its light as a wash laid over it instead."""
    p.lamps.append((cx, cy, r, col, set(own), tint))


# What a light falls on: everything the laboratory is made of but the wall, the glass and the words.
LIT = (set(OAK) | set(BRASS) | set(BONE) | set(CLAY) | set(IRON) | set(RED) | set(BLUE) | set(ASH) | set(SKIN)
       | set(CROC) | set(LEAD) | set(GOLD))
# The pale things, which take a light's own colour where it falls strongest.
PALE = set(ASH) | set(BONE) | set(LEAD) | set(IRON)


def lights(p: Pix):
    """By night each light on what stands near it, laid into the colours themselves rather than over them:
    within a light's reach what it falls on is a tone lighter on its own ramp, and in the near half of its reach
    two tones; the pale things (a beard, bone, lead, iron) take the light's own colour instead, a tone lighter
    beyond the near half than in it, so the light warms or greens them as it falls off (see `lamp`). A light's
    own pixels are left as they are. Drawn lighter, each light keeps its near half and lets the faint step
    beyond it go."""
    base = p.layers["base"]
    unlit = getattr(p, "unlit", ())
    for (cx, cy, r, col, own, tint) in p.lamps:
        hue = ramp_for(col)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y))
                if c is None or (x, y) in own or (x, y) in unlit or c not in LIT:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1) / r
                if d >= (0.5 if p.lite else 1):
                    continue
                if c in PALE and tint is not None:
                    base[(x, y)] = hue[min(6, ramp_for(c).index(c) + tint + (0 if d < 0.5 else 1))]
                else:
                    base[(x, y)] = step(c, 2 if d < 0.5 else 1)
    p.lamps = []


def pool(p: Pix, cx, cy, rx, ry, col, alphas=(0.1, 0.2, 0.3, 0.42)):
    """By night a pool of a light's colour on the wall round it, in steps, strongest at its heart: kept with the
    drawing until its scene lays it on the wall (see `lay_pools`). A light drawn outside a scene lays a fainter
    glow of its own."""
    if getattr(p, "pools", None) is None:
        p.halo(cx, cy, rx * 0.6, ry * 0.6, col, tuple(a * 0.5 for a in alphas[:3]), L="haze", shape=True)
        return
    p.pools.append((cx, cy, rx, ry, col, alphas))


def shine(p: Pix, cx, cy, r, col, alphas=(0.12, 0.24)):
    """By night the glow of a bright light laid over what stands nearest it, in front of it: two small rings, so
    the light itself shines and its glass and the hand or the stand round it are washed in its colour. Drawn
    lighter, the inner ring alone."""
    if p.lite and len(alphas) > 1:
        r, alphas = r / len(alphas), alphas[-1:]
    L = p.layer("pool")
    prev, n = 0.0, len(alphas)
    for k, a in enumerate(alphas):
        f = (n - k) / n
        p.shapes[L].append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(r * f)}" ry="{num(r * f)}" fill="{col}" '
                           f'fill-opacity="{num(1 - (1 - a) / (1 - prev))}"/>')
        prev = a


def open_pools(p: Pix):
    """Begin a scene's pools of light: every light drawn until `lay_pools` keeps its pool for the scene."""
    p.pools = []


def grain(p: Pix):
    """Drawn lighter, the grain goes from what stands in the base layer: a lone pixel a tone off the colour on
    either side of it along its row, on the same ramp, takes that colour, so the row is one run. Outlines,
    eyes, glints and every edge between two things stay, being off their neighbours by more than a tone or
    another colour altogether."""
    if not p.lite:
        return
    base = p.layers["base"]
    for (x, y), c in list(base.items()):
        a = base.get((x - 1, y))
        if a is None or a != base.get((x + 1, y)) or a == c or c not in TONE or a not in TONE:
            continue
        if TONE[a][0] == TONE[c][0] and abs(TONE[a][1] - TONE[c][1]) == 1:
            base[(x, y)] = a


# Each colour of a ramp, with its ramp's name and its place on it.
TONE = {}
for _name, _ramp in RAMP.items():
    for _i, _c in enumerate(_ramp):
        TONE.setdefault(_c, (_name, _i))


def lay_pools(p: Pix, x0, y0, x1, y1):
    """Lay the pools of light kept since `open_pools` on the wall behind the scene, and the scene's lights into
    what stands near them (see `lights`): the pools inside the box (x0, y0) to (x1, y1), the room the scene
    stands in, so no light falls past it on a word; between them the wall keeps its dark."""
    pools, p.pools = getattr(p, "pools", None) or [], None
    grain(p)
    lights(p)
    if not pools:
        return
    placed: dict = {}
    for (cx, cy, rx, ry, col, alphas) in pools:
        alphas = alphas[::2] if p.lite else alphas      # drawn lighter, a pool keeps its reach in fewer steps
        placed.setdefault(col, []).append(f'<use href="#{_pool_rings(p, alphas)}" '
                                          f'transform="translate({num(cx)} {num(cy)}) scale({num(rx)} {num(ry)})"/>')
    cid = f"lp{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    group = (f'<g clip-path="url(#{cid})">'
             + "".join(f'<g fill="{col}">{"".join(r)}</g>' for col, r in placed.items()) + '</g>')
    p.raw(-19, group, group)


def _pool_rings(p: Pix, alphas) -> str:
    """The rings of a pool of light of `alphas`, kept once a file as a symbol a unit round and placed scaled to
    each pool: a circle a step, each smaller than the last, the strongest at the heart, so where they lie over
    one another the light builds to each step's own strength."""
    key = ("pool", alphas)
    if key not in p.syms:
        sid = f"q{len(p.syms)}"
        prev, n, rings = 0.0, len(alphas), []
        for k, a in enumerate(alphas):
            rings.append(f'<circle r="{num((n - k) / n)}" fill-opacity="{num(1 - (1 - a) / (1 - prev))}"/>')
            prev = a
        p.defs.append(f'<g id="{sid}">{"".join(rings)}</g>')
        p.syms[key] = sid
    return p.syms[key]


# --------------------------------------------------------------------------- the alchemist
# The alchemist at his workbench, 48 by 46, facing left, the bench before him hiding him below his chest: a tall
# cap of crimson felt with a star and a band of gold, white hair falling to his shoulders, a bushy brow over his
# eye, a long nose and a long white beard in strands, a robe of blue trimmed with gold, a collar of fur and a gold
# chain with a medal of the sun on it; and his near arm raised in its wide sleeve, his hand round the neck of a
# round flask of the gold he has made, holding it up to the light. `k c C T p` are the cap's felt, `Y y z` its
# gold and the medal's, `h H` his hair, `f F n m e` his face and his eye, `b B x` his beard, `r R S q` the robe,
# `g` its trim, `u U` the fur, `a A` his hand, and the flask is glass (`o O i W`) round its elixir (`l L d`)
# under a cork (`K j`).
ALCHEMIST = [
    ".....................................kk.........",
    "...................................kCcck........",
    "..................................kCTcck........",
    ".................................kCTcccck.......",
    "................................kCTcccccpk......",
    "...............................kCTccccccpk......",
    ".........jj..................kCTccccYcccppk.....",
    "........KjjK................kCTccccYYYcccpk.....",
    "........KKKK...............kCTccccccYccccppk....",
    "........oiiO..............kCTcccccccccccccppk...",
    "........naaa.............kCTccccccccccccccppk...",
    ".......naaaaA..........zYYYYYYYYYYYYYYYYYYYYYzz.",
    ".......aaaaaaA.........zyyyyyyyyyyyyyyyyyyyyyzz.",
    ".......AaaaaaAAgg........FFFFFFFFFHHHHHHHHHHHx..",
    "........AAaaAAgggR......nnffffffffhhhhHhhhhhHx..",
    "........oiiOggRRRR....BbbbbbbfffFfhhhhHhhhhhHx..",
    "........oiiORRRRRSR....nfFenfffFFfhhhhHhhhhhHx..",
    ".......ooiiOORRRRSRr..nffFFfffFaFfHhhhhHhhhhHx..",
    ".....oiiiiiiOORRRSRrrnfffffffFaaFhHhhhhHhhhHx...",
    "....oiWiiiiiiiORRRSRnfffffffffFaFhHhhhhHhhhHx...",
    "...oiWWiiiiiiiiORRRnffFffffffffFhhHhhhhhHhhHx...",
    "..oiWiiiiiiiiiiiORRFFmbbbbbbbbbbbFHhhhhhHhhHx...",
    "..oiiiiiiiiiiiiiORRbbbbbbbbbbbbbBxxHhhhhHhhHx...",
    "..oLLLLLLLLllllllORbbbbbbbbBbbbbbBxHhhhhhHhhxu..",
    "..oLLLLLLLLlllllldObbbbbBbBbbbbbbbBxHhhhhHhxuuu.",
    "..olLLLLLLlllllllddbbbbbBbBbbbbBbbBxxHhhxuuuuuu.",
    "..olLLLLLllllllldddbbbbbBbbBbbbBbbbBxuuuuuuuuuu.",
    "..olllLlllllllldddOrbbbbBbbBbbbBbbbBxUuuuuuuuuuU",
    "...olllllllllldddOrrbbbbBbbbBbBbbbbBxgUuuuuuuUUU",
    "....OllllllllddddOrrbbbbBbbbBbBbbbbBxgRRRRRRRRRq",
    ".....OdllllllddddOrrrbbbBbbbBbBbbbBxYgRRRSRRRRRq",
    ".......OOddddddOOqrrrbbbbBbbBbBbbbBxrgRRRSRRRRrq",
    ".........OOOOOqqrrrrrRbbbBbBbbBbbbBxrYgRRSRRRrrq",
    ".............qqrrrrrrRbbbbBBbbBbbBxrrrgRRSRRRrrq",
    "..............qrrrrrrrRbbbBBbbbBbBxrrYgRRSRRrrrq",
    "..............qqrrrrrrrbbbBBbbBbBxrYYYgRRRSRrrrq",
    "...............qqrrrrrrrbBbbBbBbBxYyyyYgRRRRrrq.",
    "...............qqqrrrrrrbBbbBBbBxrYyzyYgRRRrrrq.",
    "................qqqrrrrrrBbbBBbBxrYyyyYgRRRrrrq.",
    "................qqqqrrrrrbBbBBBxrrrYYYrgRRRrrrq.",
    ".................qqqqrrrrrbBBBBxrrrrrrrgRRrrrrq.",
    ".................qqqqqrrrrrBBBxxrrrrrrrgRRrrrrq.",
    ".................qqqqqrrrrrbBxRRRRRrrrrgRRrrrrq.",
    ".................qqqqqqrrrrrBxrRRRRrrrrgRRrrrrq.",
    ".................qqqqqqrrrrrrrrrRRRRRRRRrrrrrgRR",
    ".................qqqqqqqrrrrrrrrrrRRRRRRrrrrrgRr",
]
# Where the flask he holds up glows by night, from his sprite's top-left.
HELD_FLASK = (9, 24)


def alchemist(p: Pix, x, y, night, robe="blue", L="base", bench=None):
    """The alchemist behind his workbench, top-left at (x, y), holding up his flask of gold to the light: by day
    it catches the sun from the window, by night it glows and lights his face, his beard and his sleeve. His
    face and his hand are on the hand's lightest skin, and by night fall a tone into the dark with the rest of
    the room until his flask's light lifts them again (see `lights`). Behind a bench whose top is at row
    `bench`, only so much of him is drawn as shows over it and its top."""
    k = -1 if night else 0
    Rb, Cp = RAMP[robe], RED
    pal = {"k": Cp[1 + k], "K": AMBER[2], "j": AMBER[3 + k], "c": Cp[2 + k], "C": Cp[4 + k], "T": Cp[5 + k],
           "p": Cp[1], "m": SKIN[1], "S": Rb[5 + k], "Y": GOLD[5 + k],
           "y": GOLD[3 + k], "z": GOLD[1], "h": ASH[5 + k], "H": ASH[3 + k], "f": SKIN[3 + k], "F": SKIN[2 + k],
           "n": SKIN[4 + k], "e": OAK[0], "b": ASH[6 + k], "B": ASH[4 + k], "x": ASH[2 + k], "r": Rb[2 + k],
           "R": Rb[4 + k], "q": Rb[1 + k], "g": GOLD[4 + k], "u": BONE[5 + k], "U": BONE[3 + k], "a": SKIN[3 + k],
           "A": SKIN[2 + k], "o": GLASS[3], "O": GLASS[1], "i": GOLD[1] if night else GLASS[5],
           "W": C["white"], "l": GOLD[5 if night else 4], "L": GOLD[6 if night else 5], "d": GOLD[3 if night else 2]}
    sprite(p, x, y, ALCHEMIST[:None if bench is None else max(0, bench + 4 - y)], pal, L)
    if night:
        fx, fy = x + HELD_FLASK[0], y + HELD_FLASK[1]
        pool(p, fx, fy, 36, 32, GOLD[4], (0.08, 0.16, 0.26, 0.38))
        shine(p, fx, fy, 11, GOLD[5])
        own = {(x + i, y + j) for j, row in enumerate(ALCHEMIST) for i, ch in enumerate(row) if ch in "lLdioOWK"}
        lamp(p, fx + 2, fy - 2, 26, GOLD[4], own=own, tint=0)


# --------------------------------------------------------------------------- the workbench and its goods
# A brass mortar, 11 by 9, its wooden pestle leaning in it: `O o` the pestle, `B b M d m` the brass from lit to
# dark, `m` the hollow of the bowl.
MORTAR = [
    "........Oo.",
    ".......Oo..",
    "......Oo...",
    ".BBBBBBoBb.",
    "BbmmmmmmmdM",
    ".bBbbbbbbM.",
    "..bBbbbbM..",
    "...BbbbM...",
    "..dMMMMMMd.",
]
# A carboy in its wicker basket, 13 by 15: a round bottle of green glass, stoppered, the basket woven round its
# belly. `o O` the glass, `g G` the elixir in it, `w W` the wicker, `K` the stopper.
CARBOY = [
    ".....KK......",
    ".....oO......",
    ".....oO......",
    "....ooOO.....",
    "..ooggggOO...",
    ".oggGggggOO..",
    "oggGgggggggO.",
    "wWwWwWwWwWwWw",
    "WwWwWwWwWwWwW",
    "wWwWwWwWwWwWw",
    "WwWwWwWwWwWwW",
    "wWwWwWwWwWwWw",
    "WwWwWwWwWwWwW",
    ".wWwWwWwWwWw.",
    "..wwwwwwwww..",
]


def mortar(p: Pix, x, foot, night, L="base"):
    """The brass mortar with its pestle, standing on the row above `foot` from x."""
    k = -1 if night else 0
    sprite(p, x, foot - len(MORTAR), MORTAR, {"O": OAK[5 + k], "o": OAK[3 + k], "B": BRASS[5 + k],
                                              "b": BRASS[4 + k], "m": BRASS[1], "M": BRASS[2 + k], "d": BRASS[1]}, L)


def carboy(p: Pix, x, foot, night, L="base"):
    """The carboy of green elixir in its wicker basket, standing on the row above `foot` from x."""
    k = -1 if night else 0
    sprite(p, x, foot - len(CARBOY), CARBOY, {"K": AMBER[2], "o": GLASS[3], "O": GLASS[1], "g": GREEN[3 + k],
                                              "G": GREEN[5 + k], "w": AMBER[3 + k], "W": AMBER[2 + k]}, L)


def workbench(p: Pix, x0, x1, top, foot, night, L="base"):
    """The alchemist's workbench of oak from x0 to x1 (not included), its top at row `top` and its legs down to
    the row above `foot`: the top lit along its edge with a streak of grain, plain when drawn lighter, an apron
    of two drawers with brass pulls under it (as much of it as a short bench has room for), a leg at each end,
    and the wall behind in its shadow under it."""
    k = -1 if night else 0
    mid = (x0 + x1) // 2
    for xx in range(x0, x1):
        p.px(xx, top, OAK[6 + k], L)
        p.px(xx, top + 1, OAK[5 + k], L)
        p.px(xx, top + 2, OAK[3 + k] if (xx - x0) % 13 == 6 and not p.lite else OAK[4 + k], L)
        p.px(xx, top + 3, OAK[1], L)
    low = min(top + 10, foot - 1)
    for yy in range(top + 4, low + 1):
        for xx in range(x0 + 2, x1 - 2):
            c = OAK[2 + k] if yy == top + 4 else OAK[3 + k]
            if xx in (x0 + 4, mid, x1 - 5) or yy in (top + 5, low):
                c = OAK[1]
            elif yy == top + 6:
                c = OAK[4 + k]
            p.px(xx, yy, c, L)
    for cx in ((x0 + 4 + mid) // 2, (mid + x1 - 5) // 2) if low >= top + 9 else ():
        p.px(cx, top + 7, BRASS[5 + k], L)
        p.px(cx + 1, top + 7, BRASS[3 + k], L)
        p.px(cx, top + 8, BRASS[2 + k], L)
        p.px(cx + 1, top + 8, BRASS[1], L)
    for lx in (x0 + 1, x1 - 5):
        for yy in range(top + 4, foot):
            for i, t in enumerate((4, 3, 3, 1)):
                p.px(lx + i, yy, OAK[t + k], L)
    if top + 11 < foot:
        p.shapes[L].append(f'<rect x="{x0 + 5}" y="{top + 11}" width="{x1 - x0 - 10}" height="{foot - top - 11}" '
                           f'fill="{X["shade_ink"]}" fill-opacity=".16"/>')


# --------------------------------------------------------------------------- the crocodile
# The stuffed crocodile hung from the ceiling, 46 by 12, facing left: its long snout with the teeth along its
# jaw and its red gape, a gold eye under its brow, the ridges of scutes along its back and its tail, its hide
# lit along its back and dark along its flank, a pale belly, and its four legs splayed with their claws.
CROCODILE = [
    "................s.s.s.s.s.s.s.s...............",
    "............kkkkSkSkSkSkSkSkSkSkk.s.s.s.s.....",
    "..........kkHHHHHhHhHhHhHhHhHhHHHkkSkSkSkSkk..",
    "...kkkkkkkHHHeghhmhhmhhmhhmhhmhhmhhhhhhhhhhkkS",
    "..kHHHHHHHHhhkkhhhmhhmhhmhhmhhmhhmhhhmhhhhhkkS",
    ".kHhhhhhhhhhhhhmhhmhhmhhmhhmhhmhhmhhhmhhhhkk..",
    "kHhhhhhhhhhmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmkk...",
    "kWtWtWtWtWtkmmbbbbbbbbbbbbbbbbbbbbbbbmmkkk....",
    "kqqqqqqqqqqkkbbbbbbbbbbbbbbbbbbbbbbbbkkk......",
    ".kmmmmmmmmkk.kmmk..........kmmk...............",
    "..kkkkkkkkk.kmmk..........kmmk................",
    "...........kwkwk.........kwkwk................",
]
CROC_ROPES = (14, 36)   # the columns the ropes come down to, at its neck and its tail's root


def crocodile(p: Pix, x, y, ceiling, night, L="base"):
    """The stuffed crocodile, top-left at (x, y), hung on two ropes from the shelf over it at row `ceiling`."""
    k = -1 if night else 0
    pal = {"k": CROC[0], "H": CROC[5 + k], "h": CROC[4 + k], "m": CROC[2 + k], "S": CROC[6 + k],
           "s": CROC[3 + k], "e": GOLD[4], "g": OAK[0], "W": BONE[6 + k], "t": BONE[3 + k], "q": RED[2 + k],
           "b": BONE[3 + k], "w": BONE[5 + k]}
    for cx in CROC_ROPES:
        for yy in range(ceiling, y + 2):
            p.px(x + cx, yy, AMBER[3 + k] if (yy + cx) % 3 else AMBER[1], L)
    sprite(p, x, y, CROCODILE, pal, L)


# --------------------------------------------------------------------------- the round window
def window(p: Pix, cx, cy, r, night, motion=True, L="base"):
    """A round window set deep in the wall, centred on (cx, cy): its reveal in the plaster, shaded on its upper
    left and lit on its lower right where the light falls into it, a came of lead round the glass and a cross
    of lead across it. By day the panes are bright with the sky and the sun's glare on the upper one; by night
    they are dark, and stars show through them, twinkling in a moving header, with a sliver of the hand's moon."""
    W = wall(night)
    cells = {}
    reveal = 2.2 if r >= 9 else 1.2
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 2):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            if rho > r + 0.4:
                continue
            toward = (dx * -0.6 + dy * -0.8) / max(0.5, rho)      # the side of the ring toward the light
            if rho > r - 0.6:
                cells[(x, y)] = W[0] if toward < -0.2 else W[1] if not night else W[2]
            elif rho > r - reveal:
                cells[(x, y)] = (W[2] if toward > 0.25 else W[4] if toward > -0.35 else W[6]) if not night else \
                    (W[2] if toward > 0.25 else W[3] if toward > -0.35 else W[4])
            elif rho > r - reveal - (0.9 if r >= 9 else 0.7) or abs(dx) < 0.6 or abs(dy) < 0.6:
                cells[(x, y)] = LEAD[1 + (0 if night else 1)]
            elif night:
                cells[(x, y)] = SKY[1]
            else:
                glare = dx < 0 and dy < 0 and math.hypot(dx + r * 0.4, dy + r * 0.4) < r * 0.28
                cells[(x, y)] = C["white"] if glare else GLASS[6] if -2 <= dx + dy <= 0 else BLUE[6]
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    if night:
        for i, (fx, fy) in enumerate(((-0.45, -0.5), (0.35, -0.3), (-0.3, 0.42), (0.5, 0.55), (0.2, -0.62))):
            sx, sy = round(cx + fx * r), round(cy + fy * r)
            if cells.get((sx, sy)) == SKY[1]:
                p.px(sx, sy, X["star"] if i % 2 else C["white"], p.twinkle(i) if motion else L)
        mx, my = round(cx + r * 0.42), round(cy - r * 0.48)
        for (dx, dy) in ((0, 0), (1, 1), (1, 2), (0, 3)):
            if cells.get((mx + dx, my + dy)) == SKY[1]:
                p.px(mx + dx, my + dy, MOON[4 if dx else 3], L)
    return cells


def _shaft(top, foot, x0, w0, x1, w1, a=0.0, b=1.0, t0=None):
    """The points of the band of a shaft from `a` to `b` of the way across it, from row `t0` (its top if not
    given) to its foot."""
    t0 = top if t0 is None else t0
    u = (t0 - top) / max(1, foot - top)
    xa, wa = x0 + (x1 - x0) * u, w0 + (w1 - w0) * u
    return (f"{num(xa + wa * a)} {num(t0)} {num(xa + wa * b)} {num(t0)} {num(x1 + w1 * b)} {num(foot)} "
            f"{num(x1 + w1 * a)} {num(foot)}")


# How long the dust takes to drift down the shaft of sun, in seconds: a slow ambient sweep of the hand's.
DRIFT = 24


def sunbeam(p: Pix, top, foot, x0, w0, x1, w1, seed=1, motion=True, lite=False):
    """The shaft of sun from the round window by day, `w0` wide at (x0, top) and spreading to `w1` at (x1,
    foot): a band of warm light with a brighter core, a patch of sun where it lands, and dust drifting slowly
    down through it in a moving header (see `DRIFT`), resting where it is in a still one; drawn lighter, fewer
    motes."""
    L = p.layer("beam", z=4)
    for (a, b, c, o) in ((0, 1, X["sun"], ".34"), (.22, .78, AMBER[6], ".34")):
        p.shapes[L].append(f'<polygon points="{_shaft(top, foot, x0, w0, x1, w1, a, b)}" fill="{c}" '
                           f'fill-opacity="{o}"/>')
    p.shapes[L].append(f'<polygon points="{_shaft(top, foot, x0, w0, x1, w1, 0, 1, foot - 3)}" '
                       f'fill="{X["glint"]}" fill-opacity=".45"/>')
    rnd = random.Random(seed)
    drift = (round((x1 - x0) * 0.25), round((foot - top) * 0.25))
    motes = {}
    for i in range(9 if lite else 16):
        t = rnd.uniform(-0.25, 0.95)
        y = top + (foot - top) * t
        x = x0 + (x1 - x0) * t + rnd.uniform(0.15, 0.85) * (w0 + (w1 - w0) * max(0.0, t))
        motes[(round(x), round(y))] = C["white"] if i % 3 else GOLD[6]
    resting = {(x, y): c for (x, y), c in motes.items() if y >= top}
    still = _paths(resting)
    cid = f"sb{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{_shaft(top, foot, x0, w0, x1, w1)}"/></clipPath>')
    if motion:
        moving = (f'<g clip-path="url(#{cid})"><g>{_paths(motes)}<animateTransform attributeName="transform" '
                  f'type="translate" values="0 0;{drift[0]} {drift[1]}" dur="{num(DRIFT)}s" repeatCount="indefinite"/>'
                  f'</g></g>')
    else:
        moving = f'<g clip-path="url(#{cid})">{still}</g>'
    p.raw(5, moving, f'<g clip-path="url(#{cid})">{still}</g>')


def moonbeam(p: Pix, top, foot, x0, w0, x1, w1):
    """By night a cold shaft of moonlight from the round window, as `sunbeam` lays the sun's but fainter, with
    a paler core and no dust in it, and a cold patch where it lands."""
    L = p.layer("beam", z=4)
    for (a, b, c, o) in ((0, 1, SKY[6], ".18"), (.25, .75, GLASS[6], ".16")):
        p.shapes[L].append(f'<polygon points="{_shaft(top, foot, x0, w0, x1, w1, a, b)}" fill="{c}" '
                           f'fill-opacity="{o}"/>')
    p.shapes[L].append(f'<polygon points="{_shaft(top, foot, x0, w0, x1, w1, 0, 1, foot - 3)}" '
                       f'fill="{GLASS[6]}" fill-opacity=".24"/>')


# --------------------------------------------------------------------------- the bench's things
SKULL = ["..wwwW..", ".wwWWWwS", "wwWWWwwS", "wkkwkkwS", "wkkwkkSS", ".wwkwwS.", "..twtwS.", "..SSSS.."]
BOOK = ["..pppppp.pppppp...", ".ppqpqpPpPpqpqpp..", ".pqqqppPpPpppqqp..", "pppqppPPpPPpqpppp.",
        "ppppppPPpPPppppppL", "LLLLLLLLLLLLLLLLLL", ".llllllllllllllll."]
# The hourglass, 9 by 14, between its oak plates on two turned posts: the sand in the upper bulb, its stream
# through the neck and its heap in the lower bulb.
HOURGLASS = ["BBBBBBBBB", "bbbbbbbbb", "B.ommmo.B", "B.ogggo.B", "B..ogo..B", "B...g...B", "B...s...B",
             "B..oso..B", "B.o.s.o.B", "B.o...o.B", "B.ogggo.B", "B.ggggg.B", "BBBBBBBBB", "bbbbbbbbb"]


def skull(p: Pix, x, foot, night, L="base"):
    """A skull on the bench, its jaw on the row above `foot`."""
    k = -1 if night else 0
    sprite(p, x, foot - len(SKULL), SKULL, {"w": BONE[5 + k], "W": BONE[6 + k], "S": BONE[2 + k], "k": OAK[0],
                                            "t": BONE[4 + k]}, L)


def book(p: Pix, x, foot, night, L="base"):
    """An open book of symbols lying on the bench, its covers of red leather, the signs inked on its pages."""
    k = -1 if night else 0
    sprite(p, x, foot - len(BOOK), BOOK, {"p": BONE[5 + k], "P": BONE[3 + k], "q": RED[2 + k], "L": RED[2 + k],
                                          "l": RED[1]}, L)


def hourglass(p: Pix, x, foot, night, motion=True, L="base"):
    """The hourglass, its foot on the row above `foot`, its sand running in a moving header: a stream of grains
    falling from the upper bulb to the heap in the lower one, a grain a frame."""
    k = -1 if night else 0
    y = foot - len(HOURGLASS)
    sprite(p, x, y, HOURGLASS, {"B": OAK[4 + k], "b": OAK[2 + k], "m": GLASS[3], "g": AMBER[4 + k],
                                "o": GLASS[4 + k], "s": AMBER[4 + k]}, L)
    if motion:
        for f in range(FRAMES):
            p.px(x + 4, y + 6 + f, AMBER[5], tick(p, f))


# --------------------------------------------------------------------------- glass on the bench
def flask_cells(cx, foot, r, neck, elixir, night, level=0.55):
    """A round flask standing on the row above `foot`, its bulb of radius `r` round (cx, foot - 1 - r), a neck
    `neck` rows tall with its lip, filled to `level` of its bulb: the glass's edge lit on the left and dark on
    the right, empty glass showing the wall, the elixir lit at its surface and dark at its foot, and a glint."""
    E = RAMP[elixir]
    cy = foot - 1 - r
    cells = {}
    surface = cy + r - 2 * r * level
    for y in range(math.floor(cy - r) - 1, foot):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy * 1.05)
            if rho > r + 0.3:
                continue
            if rho > r - 0.8:
                cells[(x, y)] = GLASS[3] if dx < 0 or dy < -r * 0.5 else GLASS[1]
            elif y + 0.5 >= surface:
                cells[(x, y)] = E[6 if night else 5] if y + 0.5 < surface + 1 else \
                    E[(4 if night else 3) if dx > r * 0.3 or dy > r * 0.6 else (5 if night else 4)]
            else:
                cells[(x, y)] = (E[1] if night else GLASS[5])
    gx, gy = round(cx - r * 0.45), round(cy - r * 0.45)
    cells[(gx, gy)] = C["white"]
    nx = round(cx - 1)
    for y in range(round(cy - r) - neck, round(cy - r) + 1):
        cells[(nx - 1, y)] = GLASS[3]
        cells[(nx, y)] = E[1] if night else GLASS[5]
        cells[(nx + 1, y)] = GLASS[1]
    top = round(cy - r) - neck
    for xx in range(nx - 2, nx + 3):
        cells[(xx, top - 1)] = GLASS[3] if xx < nx + 1 else GLASS[1]
    return cells


def bubbles(p: Pix, x, y0, y1, col, spread=2):
    """Bubbles rising through an elixir from row y0 up to row y1 round column x, frame by frame in a moving
    header, each frame a bubble or two a step higher than the last."""
    for f in range(FRAMES):
        Ls = tick(p, f)
        for j, yy in enumerate(range(y0, y1 - 1, -1)):
            if (j + f) % FRAMES == 0:
                p.px(x + (j % spread) - spread // 2, yy, col, Ls)


def green_flask(p: Pix, cx, foot, night, motion=True, r=5, neck=4, L="base"):
    """The round flask of green elixir bubbling on the bench, glowing by night and lighting what stands near
    it, its bubbles rising in a moving header and a wisp of vapour at its lip."""
    cells = flask_cells(cx, foot, r, neck, "green", night, level=0.6)
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    cy = foot - 1 - r
    if motion:
        bubbles(p, round(cx), foot - 2, round(cy - r * 0.1), GREEN[6])
        top = round(cy - r) - neck - 2
        for f in range(FRAMES):
            Ls = tick(p, f)
            for j in range(3):
                p.px(round(cx - 1) + ((f + j) % 2), top - j - f, (GREEN[5] if night else GLASS[4]) + ":0.6", Ls)
    if night:
        pool(p, cx, cy, r * 3 + 20, r * 3 + 16, GREEN[5])
        shine(p, cx, cy, r + 4, GREEN[5])
        lamp(p, cx, cy, r + 15, GREEN[5], own=set(cells))


# --------------------------------------------------------------------------- the armillary sphere
def armillary(p: Pix, cx, cy, r, night, L="base", stand=True):
    """A brass armillary sphere of radius `r` on (cx, cy): the meridian ring, the equator and the two tropics
    across it, the broad band of the zodiac crossing it aslant with its degrees marked, and the axis through the
    poles, each ring lit along its upper left and dark along its lower right; and, `stand`, the pillar and foot
    it turns on."""
    k = -1 if night else 0
    B = BRASS
    cells = {}

    def ring(points, band=False, shade=0):
        for i, (x, y) in enumerate(points):
            xi, yi = math.floor(x), math.floor(y)
            facing = ((x - cx) * -0.6 + (y - cy) * -0.8) / max(1.0, r)
            t = 5 if facing > 0.35 else 4 if facing > -0.15 else 2
            cells[(xi, yi)] = B[max(0, t - shade + k)]
            if band:
                cells[(xi, yi + 1)] = B[max(0, t - (2 if i % 3 == 0 else 1) + k)]
    n = int(8 * r)

    def ellipse(rx, ry, dy=0.0, turn=0.0):
        out = []
        for i in range(n):
            t = 2 * math.pi * i / n
            ex, ey = rx * math.cos(t), ry * math.sin(t)
            out.append((cx + ex * math.cos(turn) - ey * math.sin(turn), cy + dy + ex * math.sin(turn)
                        + ey * math.cos(turn)))
        return out
    if r >= 13:         # a great sphere's meridian is a broad ring, its inner edge a tone in shade
        ring(ellipse(r - 1, r - 1), shade=1)
    ring(ellipse(r, r))
    ring(ellipse(r, r * 0.3))
    if r >= 8:
        for side in (-1, 1):
            q = 0.5 * side
            ring(ellipse(r * math.sqrt(1 - q * q), r * 0.3 * math.sqrt(1 - q * q), dy=q * r))
    ring(ellipse(r, r * 0.38, turn=math.radians(-30)), band=True)
    for yy in range(round(cy - r) - 2, round(cy + r) + 2):
        cells[(round(cx), yy)] = B[3 + k] if yy % 2 else B[5 + k]
    cells[(round(cx), round(cy - r) - 2)] = B[6 + k]
    cells[(round(cx), round(cy))] = B[6 + k]
    if stand:
        base = round(cy + r) + 2
        for yy in range(base, base + 3):
            cells[(round(cx), yy)] = B[4 + k]
            cells[(round(cx) - 1, yy)] = B[5 + k]
        for j, half in enumerate((2, 3, 4)):
            for xx in range(round(cx) - half, round(cx) + half):
                cells[(xx, base + 3 + j)] = B[(5 if xx < cx - 1 else 3 if xx < cx + 1 else 2) + k]
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    return cells


# The turned brass stand of the great armillary sphere, its half-widths from the cup under the sphere down: the cup
# that holds the axis, a neck, the ball of its knop, the stem (as long as the stand is tall), a collar, and its
# foot spreading in four steps to the bench.
STAND = ((2, 2, 1, 1), (2, 3, 3, 2), (2, 3, 4, 5))   # its cup and neck, its knop, and its foot


def great_armillary(p: Pix, cx, top, foot, r, night, L="base"):
    """The great armillary sphere of a strip, radius `r`, on its turned stand of brass: the sphere's axis tipped at
    row `top` over column cx and the stand's foot on the row above `foot`, the stem as long as the rows between
    leave it (see `armillary`). The stand is shaded as a turned column lit from the upper left. Returns the columns
    it covers."""
    cy = top + r + 2
    armillary(p, cx, cy, r, night, L, stand=False)
    k = -1 if night else 0
    y0 = cy + r + 2
    cup, knop, base = STAND
    stem = max(2, foot - y0 - len(cup) - len(knop) - len(base) - 2)
    halves = [*cup, *knop, *([1] * stem), 2, 1, *base]
    for j, half in enumerate(halves[:foot - y0]):
        widened = j == 0 or half > halves[j - 1]
        for x in range(cx - half, cx + half + 1):
            u = (x - cx) / max(1, half)
            t = 5 if u < -0.5 else 4 if u < 0 else 3 if u < 0.5 else 2
            if x == cx + half:
                t = 1
            elif widened and u < 0:
                t = 6
            p.px(x, y0 + j, BRASS[max(0, t + k)], L)
    return (cx - r - 1, cx + r + 2)


# --------------------------------------------------------------------------- the athanor and the alembic
def athanor(p: Pix, x, foot, w, h, night, phase=0, L="base"):
    """The athanor, the alchemist's furnace: a tower of plastered clay `w` wide at its foot and `h` tall, its
    foot on the row above `foot`, tapering as it rises to a dome with an iron ring at its crown that the
    cucurbit sits in, a tall one bound with two hoops of iron; standing on a plinth of stone, lit on its left
    and shaded on its right, a crack or two in
    its plaster and soot above its door. The fire door is an arch of iron near its foot: the coals glow in it
    by day, and by night the fire burns there, flickering, glowing and lighting the bench and the wall, and
    shows at the peephole above. Returns the row of the ring's top and the door's middle."""
    k = -1 if night else 0
    top = foot - h
    cx = x + w / 2
    hb, ht = w / 2, w / 2 - 2
    cells = {}

    def half(j):
        if j < 4:
            return (ht - 4, ht - 2, ht - 1, ht)[j]
        if j >= h - 2:
            return hb + 1
        return ht + (hb - ht) * (j - 4) / max(1, h - 7)
    for j in range(h):
        hw = half(j)
        yy = top + j
        for xx in range(math.floor(cx - hw), math.ceil(cx + hw)):
            u = (xx + 0.5 - cx) / hw
            if j >= h - 2:
                cells[(xx, yy)] = ASH[(4 if u < -0.3 else 3 if u < 0.5 else 2) - (1 if j == h - 1 else 0) + k]
                continue
            t = 5 if u < -0.45 else 4 if u < 0.1 else 3 if u < 0.55 else 2
            if j < 4:
                t += 1
            if u > 0.86:
                t = 0
            elif u < -0.9:
                t = 1
            cells[(xx, yy)] = CLAY[max(0, min(6, t + 2 * k))]
    # a tall athanor is bound with two hoops of iron
    if h >= 40:
        for yy in (top + h // 3, top + 2 * h // 3):
            for xx in range(math.floor(cx - hb) - 1, math.ceil(cx + hb) + 1):
                if (xx, yy) in cells:
                    cells[(xx, yy)] = IRON[(5 if xx < cx else 3) + k]
                    cells[(xx, yy + 1)] = IRON[1]
    # the iron ring at the crown
    rw = round(ht - 3)
    for xx in range(round(cx - rw), round(cx + rw)):
        cells[(xx, top)] = IRON[(5 if xx < cx else 3) + k]
        cells[(xx, top + 1)] = IRON[1]
    # the fire door: an arch of iron round the fire
    dw, dh = 7, 8
    dx0, dy0 = round(cx - dw / 2), foot - 2 - dh
    door = {}
    for j in range(dh):
        for i in range(dw):
            if j == 0 and i in (0, 1, dw - 2, dw - 1) or j == 1 and i in (0, dw - 1):
                continue
            edge = i in (0, dw - 1) or j == dh - 1 or (j == 0) or (j == 1 and i in (1, dw - 2))
            door[(dx0 + i, dy0 + j)] = "e" if edge else "f"
    # soot above the door, and a crack or two in the plaster: texture a furnace drawn lighter goes without
    for j in range(1, 7) if not p.lite else ():
        for i in range(2, dw - 2):
            q = (dx0 + i, dy0 - j)
            if q in cells and (i + j) % 3 != 0 and j < 7 - abs(i - dw // 2):
                cells[q] = CLAY[1 + (1 if j > 3 else 0) + k] if night else CLAY[2 if j > 3 else 1]
    for (cx_, cy_), n in (((round(cx) + 3, top + 7), 4), ((round(cx) - 4, top + 12), 3)) if not p.lite else ():
        for i in range(n):
            q = (cx_ + (i % 2), cy_ + i)
            if q in cells:
                cells[q] = CLAY[1]
    for (xx, yy), c in cells.items():
        p.px(xx, yy, c, L)
    for (xx, yy), what in door.items():
        if what == "e":
            c = IRON[(5 if xx == dx0 or yy <= dy0 + 1 else 1) + k]
        elif night:
            c = FIRE[5] if yy >= dy0 + dh - 3 else FIRE[3] if (xx * 3 + yy) % 4 else FIRE[4]
        else:
            c = FIRE[3] if yy >= dy0 + dh - 2 and (xx + yy) % 2 else FIRE[1] if yy >= dy0 + dh - 3 else IRON[1]
        p.px(xx, yy, c, L)
    peep = (round(cx) + 3, top + 9)
    p.px(*peep, FIRE[4] if night else IRON[1], L)
    if night:
        Lf = p.flicker(phase)
        for xx in range(dx0 + 1, dx0 + dw - 1):
            p.px(xx, dy0 + dh - 2, FIRE[6], Lf)
            if (xx + phase) % 2:
                p.px(xx, dy0 + dh - 3, FIRE[5], Lf)
            if (xx + phase) % 3 == 0:
                p.px(xx, dy0 + dh - 4, FIRE[4], Lf)
        p.px(*peep, FIRE[6], Lf)
        if p.lite:      # drawn lighter, the halo's inner ring alone
            p.halo(dx0 + dw / 2, dy0 + dh / 2 + 1, (dw + 3) / 2, (dh + 2) / 2, FIRE[5], (0.2,),
                   L=p.flicker(phase, back=True), shape=True)
        else:
            p.halo(dx0 + dw / 2, dy0 + dh / 2 + 1, dw + 3, dh + 2, FIRE[5], (0.1, 0.2), L=p.flicker(phase, back=True))
        pool(p, dx0 + dw / 2, foot - 2, w + 34, 24, FIRE[4], (0.08, 0.16, 0.26, 0.38))
        lamp(p, dx0 + dw / 2, dy0 + dh, max(16, h * 0.7), FIRE[4], own=set(door), tint=None)
        # the fire's light thrown up the furnace's front and along the floor before it, kept above the floor;
        # drawn lighter, without its faint outermost step
        wash = "".join(f'<ellipse cx="{num(dx0 + dw / 2)}" cy="{num(dy0 + dh)}" rx="{num(rx)}" ry="{num(ry)}" '
                       f'fill-opacity="{o}"/>'
                       for (rx, ry, o) in ((w / 2 + 3, h * 0.55, ".1"), (w / 2, h * 0.38, ".12"),
                                           (dw + 2, h * 0.22, ".16"))[1 if p.lite else 0:])
        wash += "".join(f'<rect x="{num(dx0 + dw / 2 - half)}" y="{foot}" width="{num(2 * half)}" height="2" '
                        f'fill-opacity="{o}"/>' for (half, o) in ((w * 0.9 + 6, ".2"), (w * 0.5 + 3, ".3")))
        cid = f"fw{len(p.defs)}"
        p.defs.append(f'<clipPath id="{cid}"><rect x="{num(x - w)}" y="{top}" width="{3 * w}" '
                      f'height="{foot + 2 - top}"/></clipPath>')
        group = f'<g clip-path="url(#{cid})" fill="{FIRE[4]}">{wash}</g>'
        p.raw(3.5, group, group)
    return top, dy0 + dh // 2


def alembic(p: Pix, cx, base, night, motion=True, size=1, phase=0, run=None, right=False, L="base"):
    """The alembic on its furnace, distilling: the cucurbit's gourd sunk in the furnace's ring with the violet
    matter boiling in it and the vapour over it, its neck rising into the helm, a smaller dome of glass with the
    rim channel round its foot, and the helm's long beak running down to the left. A drop gathers at the beak's
    tip and falls, frame by frame in a moving header. By night the violet glows through the glass and lights the
    furnace and the bench. `base` is the row of the furnace's ring, `size` 0 to 4 how big it is, `run`, when
    given, how many columns the beak runs, and `right` turns the beak to run down to the right; returns the tip of
    the beak."""
    V = VIOLET
    r = (3, 6, 8, 10, 12)[size]
    cells = {}
    # the cucurbit's shoulder above the ring, the violet boiling in it and the vapour over it
    sh = (2, 5, 7, 9, 11)[size]
    full = max(1, round(sh * 0.45))
    for j in range(sh):
        yy = base - j
        t = j / max(1, sh - 1)
        hw = 2 + (r - 2) * (1 - t * t)
        for xx in range(math.floor(cx - hw), math.ceil(cx + hw)):
            u = (xx + 0.5 - cx) / hw
            if abs(u) > 1 - 1.2 / hw:
                c = GLASS[3] if u < 0 else GLASS[1]
            elif j < full:
                c = V[(5 if night else 4) if u < 0.2 else (4 if night else 3)]
                if j == full - 1:
                    c = V[6 if night else 5]
            else:
                c = (V[1] if j == full else V[0]) if night else (GLASS[4] if j == full else GLASS[5])
            cells[(xx, yy)] = c
    if size:
        cells[(round(cx - r * 0.55), base - full - 1)] = C["white"]
    # its neck, up into the helm
    neck = (1, 2, 3, 3, 3)[size]
    ny = base - sh
    for yy in range(ny - neck + 1, ny + 1):
        cells[(cx - 2, yy)] = GLASS[3]
        cells[(cx - 1, yy)] = V[1] if night else GLASS[5]
        cells[(cx, yy)] = V[1] if night else GLASS[5]
        cells[(cx + 1, yy)] = GLASS[1]
    # the helm: a bulb of glass over the neck, the rim channel round it where the beak leaves
    hr = (3, 5, 6, 7, 8)[size]
    ry = hr * 0.88
    hcy = ny - neck - ry + 1.5
    rim = round(hcy + ry * 0.42)
    for yy in range(math.floor(hcy - ry) - 1, ny - neck + 1):
        for xx in range(math.floor(cx - hr) - 1, math.ceil(cx + hr) + 1):
            dx, dy = (xx + 0.5 - cx) / hr, (yy + 0.5 - hcy) / ry
            rho = math.hypot(dx, dy)
            if rho > 1.04:
                continue
            if rho > 1 - 1.1 / hr:
                c = GLASS[3] if dx - dy * 0.6 < 0.25 else GLASS[1]
            elif night:
                c = V[1] if dy > 0.1 else V[0]
            else:
                c = GLASS[6] if dx + dy < -0.7 else GLASS[5] if dy < 0.35 else GLASS[4]
            cells[(xx, yy)] = c
    for xx in range(math.floor(cx - hr) - 1, math.ceil(cx + hr) + 1):
        cells[(xx, rim)] = GLASS[2] if xx < cx else GLASS[1]
    cells[(math.floor(cx - hr) - 1, rim)] = GLASS[3]
    gx = round(cx - hr * 0.45)
    cells[(gx, round(hcy - ry * 0.5))] = C["white"]
    if size:
        cells[(gx - 1, round(hcy - ry * 0.5) + 1)] = GLASS[6]
    top = math.floor(hcy - ry)
    for xx in range(cx - 1, cx + 1):
        cells[(xx, top - 1)] = GLASS[3]
    cells[(cx, top - 1)] = GLASS[2]
    # the beak: a tube of glass from the rim channel down to one side, the distillate running in it
    run = run or (6, 12, 20, 24, 26)[size]
    d = 1 if right else -1
    bx, by = (math.ceil(cx + hr) + 1 if right else math.floor(cx - hr) - 2), rim - 1
    tip = (bx + d * run, by + run * 2 // 3 + 1)
    for i in range(run + 1):
        xx = bx + d * i
        yy = by + round(i * 2 / 3)
        cells[(xx, yy)] = GLASS[3]
        cells[(xx, yy + 1)] = (V[5] if night else V[4]) if i % 4 == 1 else (V[2] if night else GLASS[4])
        cells[(xx, yy + 2)] = GLASS[1]
    for (xx, yy), c in cells.items():
        p.px(xx, yy, c, L)
    tx, ty = tip
    frames = FRAMES if motion else 1
    for f in range(frames):
        Ls = tick(p, f) if frames > 1 else L
        dy = (0, 1, 3, 5)[f]
        p.px(tx, ty + 1 + dy, V[5 if night else 4], Ls)
        if f == 0:
            p.px(tx, ty + 2, V[3 if night else 2], Ls)
    if motion:
        bubbles(p, cx, base, base - full + 1, V[6], spread=6)
    if night:
        pool(p, cx, base - sh // 2, r * 2 + 22, r * 2 + 18, V[5])
        shine(p, cx, base - full // 2, r + 3, V[5])
        lamp(p, cx, base - 3, r + 14, V[5], own=set(cells))
    return tip


def receiver(p: Pix, cx, foot, night, r=5, neck=3, L="base"):
    """The receiving flask the alembic's beak drips into, the violet distillate gathering in it."""
    cells = flask_cells(cx, foot, r, neck, "violet", night, level=0.35)
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    if night:
        pool(p, cx, foot - r, r * 2 + 8, r * 2 + 6, VIOLET[4], (0.06, 0.12, 0.2))
    return round(cx - 1), round(foot - 1 - 2 * r) - neck - 1


# --------------------------------------------------------------------------- the retort over its spirit lamp
# A retort of glass, 18 by 13, its round bulb at the left resting on the tripod's ring and its neck rising from it
# and bending over and down to the right; `o O` glass, `e` empty glass, `l L d` its red matter, `w` a glint.
RETORT = [
    ".........ooooo....",
    "........oeeeeeoo..",
    ".......oeeOOOOeeo.",
    "......oeeO....OOeo",
    ".....oeeO......OOo",
    "...ooweeO.........",
    "..oweeeeeO........",
    ".oweeeeeeeO.......",
    "olllllLLLLdO......",
    "oLLLLLLLLLdO......",
    "oLLLLLLLLddO......",
    ".OLLLLLLddO.......",
    "..OOOOOOOO........",
]
# The tripod and the spirit lamp under it, 13 by 12: a ring of iron on three legs splayed wide, and the brass
# lamp between them, its wick (`h`) where the flame stands.
TRIPOD = [
    "..IIIIIIIII..",
    ".iIiiiiiiiIi.",
    ".i.........i.",
    ".i.........i.",
    "..i.......i..",
    "..i.......i..",
    "..i..hhh..i..",
    "...i.hHh.i...",
    "...ihHHHhi...",
    "..iHHHHHHHi..",
    "..i.bbbbb.i..",
    ".ii.......ii.",
]


# The spirit lamp's small flame, (dx, dy, its tone on the hand's flame) from its heart: by day its heart a tone
# short of the brightest, as the furnace's coals are dimmer by day than its fire by night, and by night white-hot.
SPIRIT = ((0, 0, 5), (0, -1, 5), (-1, 0, 4), (1, 0, 4), (0, -2, 4), (-1, -1, 3), (1, -1, 3), (0, -3, 3))


def retort(p: Pix, x, foot, night, motion=True, phase=1, headroom=99, L="base"):
    """A retort on its tripod over a spirit lamp's small flame, from x with its feet on the row above `foot`: the
    flame, on the hand's flame (see `SPIRIT`), burns by day and by night, flickering in a moving header, and by
    night glows and lights what stands near it, sparks rise from the retort, as far as the `headroom` of rows
    free over it, and its red matter glows. It stands 22 rows tall. Returns the columns it covers."""
    k = -1 if night else 0
    ty = foot - len(TRIPOD)
    sprite(p, x, ty, TRIPOD, {"I": IRON[4 + k], "i": IRON[2 + k], "h": GLASS[3], "H": BRASS[4 + k],
                              "b": BRASS[2 + k]}, L)
    ry = ty - len(RETORT) + 3
    sprite(p, x - 1, ry, RETORT, {"o": GLASS[3], "O": GLASS[1], "e": RED[1] if night else GLASS[5],
                                  "w": C["white"], "l": RED[5 if night else 4], "L": RED[4 if night else 3],
                                  "d": RED[2]}, L)
    fx, fy = x + 6, ty + 5
    Lf = p.flicker(phase) if motion else L
    for (dx, dy, t) in SPIRIT:
        p.px(fx + dx, fy + dy, FIRE[6 if night and t == 5 else t], Lf)
    if night:
        if p.lite:      # drawn lighter, the halo's inner ring alone
            p.halo(fx + 0.5, fy, 2.5, 2, FIRE[5], (0.24,), L=p.flicker(phase, back=True) if motion else "haze",
                   shape=True)
        else:
            p.halo(fx + 0.5, fy, 5, 4, FIRE[5], (0.12, 0.24), L=p.flicker(phase, back=True) if motion else "haze")
        pool(p, fx + 0.5, fy - 2, 16, 13, FIRE[4], (0.08, 0.16, 0.26))
        pool(p, x + 4, ry + 7, 14, 11, RED[4], (0.06, 0.12, 0.2))
        lamp(p, fx + 0.5, fy, 12, FIRE[4])
        if motion:
            for f in range(FRAMES):
                Ls = tick(p, f)
                for j, (sx, sy) in enumerate(((3, -2), (6, -5), (2, -8), (7, -11), (4, -14))):
                    if (j + f) % 2 == 0 and f - sy <= headroom:
                        p.px(x + sx + (f % 2), ry + sy - f, (GOLD[6], VIOLET[6], GREEN[6], X["glint"])[(j + f) % 4],
                             Ls)
        else:
            for (sx, sy) in ((2, -3), (5, -7), (3, -11)):
                if -sy <= headroom:
                    p.px(x + sx, ry + sy, GOLD[6], L)
    return (x - 1, x + 17)


# --------------------------------------------------------------------------- the scenes
def bench(p: Pix, x0, x1, rule, night, L="base"):
    """The bench's top along the rule from x0 to x1, under a scene: its top lit and its front edge."""
    pid = _bench_tile(p, rule - 2, night)
    p.shapes[L].append(f'<rect x="{x0}" y="{rule - 2}" width="{x1 - x0}" height="2" fill="url(#{pid})"/>')


def wall_shelf(p: Pix, x0, x1, y, night, L="base"):
    """A short oak shelf on the wall, its top at row y, on a brass bracket at each end."""
    k = -1 if night else 0
    p.hline(x0, x1, y, OAK[5 + k], L)
    p.hline(x0, x1, y + 1, OAK[3 + k], L)
    p.hline(x0, x1, y + 2, OAK[0], L)
    for xx in range(x0 + 1, x1 - 1):
        p.apx(xx, y + 3, X["shade_ink"], 0.22, L)
    for bx in (x0 + 2, x1 - 4):
        p.px(bx, y + 3, BRASS[4 + k], L)
        p.px(bx + 1, y + 3, BRASS[3 + k], L)
        p.px(bx, y + 4, BRASS[3 + k], L)
        p.px(bx + 1, y + 4, BRASS[1], L)
        p.px(bx, y + 5, BRASS[1], L)


def lab_left(p: Pix, x0, rule, night, motion=True, lite=False, room=80):
    """The left of a wide header's laboratory, from x0 over 49 columns, standing on the bench along the rule: the
    alchemist behind his workbench holding his flask of gold up to the light, the bench filling the lower part of
    the room with the brass mortar, the open book of symbols and the green flask bubbling on it and the carboy
    and a skull on its books under it; the round window over him with, by day, the sun coming down through it
    onto the bench with the dust in its light, and by night the stars in its panes; and the stuffed crocodile hung
    from the ceiling over it all. Built to the `room` of rows free of words over the bench: the crocodile hangs
    where it leaves the bench 18 rows, the window wants 62, under 50 the alchemist and his bench give way to his
    things on the bench along the rule with an old green stain on the wall over them, and under 16 nothing
    stands. Drawn lighter it keeps all of it, the window's sun drifting with fewer motes. Returns the span of the
    rule it covers."""
    if room < 16:
        return None
    foot = rule - 2
    bench(p, x0 - 1, x0 + 49, rule, night)
    if room < 50:
        stain(p, x0, foot - 12, 11, GREEN[2], seed=2)
        skull(p, x0 + 1, foot, night)
        if room >= 22:
            book(p, x0 + 29, foot, night)
        green_flask(p, x0 + 15, foot, night, motion)
        return (x0 - 1, x0 + 49)
    above = len(ALCHEMIST) - 4             # the rows of him the bench leaves showing
    top = foot - max(24, round(room * 0.4))
    croc_foot = CROC_TOP + len(CROCODILE)
    croc = foot - (croc_foot + 1 + above) >= 18 and croc_foot + 1 >= foot - room
    sy = max(top - above, croc_foot + 1 if croc else foot - room)
    top = sy + above
    if room >= 62:
        r = 12 if room >= 80 else 10
        ceiling = croc_foot + 2 if croc else foot - room
        cy = ceiling + r if sy + 6 - ceiling >= 2 * r + 1 else sy + 9
        window(p, x0 + 11, cy, r, night, motion)
        if not night:
            sunbeam(p, cy + 2, foot - 1, x0 + 2, 12, x0 + 14, 26, seed=3, motion=motion, lite=lite)
        else:
            moonbeam(p, cy + 2, foot - 1, x0 + 2, 12, x0 + 14, 26)
    if croc:
        crocodile(p, x0 + 1, CROC_TOP, A_SHELF, night)
    alchemist(p, x0 + 1, sy, night)
    workbench(p, x0 - 1, x0 + 50, top, foot, night)
    book(p, x0 + 17, top, night)
    green_flask(p, x0 + 42, top, night, motion, r=4, neck=3)
    mortar(p, x0 + 3, top, night)
    under = foot - top - 11
    if under >= len(CARBOY):
        carboy(p, x0 + 8, foot, night)
    if under >= len(BOOKS) + len(SKULL):
        books(p, x0 + 28, foot, night)
        skull(p, x0 + 31, foot - len(BOOKS), night)
    elif under >= len(BOOKS):
        books(p, x0 + 28, foot, night)
    return (x0 - 1, x0 + 49)


CROC_TOP = 16   # the row the crocodile's back is hung at, its ropes coming down from the top shelf


def lab_right(p: Pix, x0, rule, night, motion=True, lite=False, room=80):
    """The right of a wide header's laboratory, from x0 over 48 columns, standing on the bench: the athanor at
    the right with the alembic on it distilling, its beak dripping into the receiving flask; the retort on its
    tripod over the spirit lamp at the left, throwing sparks by night; and over them a shelf on the wall with
    the armillary sphere and the hourglass. Built to the `room` of rows free of words: under 78 rows the shelf
    goes, under 52 the alembic gives way to the retort and the receiver alone, and under 26 nothing stands.
    Returns the span of the rule it covers."""
    if room < 26:
        return None
    foot = rule - 2
    bench(p, x0 - 1, x0 + 48, rule, night)
    if room >= 52:
        top, _ = athanor(p, x0 + 27, foot, 20, 26, night, phase=2)
        tip = alembic(p, x0 + 37, top, night, motion, size=1, phase=0)
        receiver(p, tip[0] + 1, foot, night, r=5, neck=3)
    else:
        receiver(p, x0 + 34, foot, night, r=5, neck=3)
    stain(p, x0 + 6, foot - 27, 12, BLUE[2], seed=3)
    retort(p, x0 + 2, foot, night, motion, phase=1, headroom=room - 23)
    if room >= 78:
        sy = max(foot - 64, foot - room + 30)
        wall_shelf(p, x0 + 1, x0 + 31, sy, night)
        armillary(p, x0 + 11, sy - 18, 10, night)
        hourglass(p, x0 + 22, sy, night, motion)
    return (x0 - 1, x0 + 48)


A_SHELF = SHELF + BOARD


# --------------------------------------------------------------------------- more of the laboratory
# The alchemist for a phone, 22 by 22, his flask of gold held up: the big one drawn small, in the same letters.
ALCHEMIST_SMALL = [
    "...............kk.....",
    "..............kCk.....",
    "......K......kCcpk....",
    ".....aoa....kCcYcpk...",
    "....oiiiO..kCccccpk...",
    "...oiWiiiO.zYYyyyyyz..",
    "...olLLllOnfbffhhhhH..",
    "...oLLLLdOffeFfhhhhH..",
    "....OdddOnfffFfhhhH...",
    ".....OOOrrmffbbbhH....",
    "......gRrbbbbbbbbBuu..",
    ".....gqRrbbbbbbbbBUuuu",
    ".....gqqrbbbbbbbbxrRRr",
    "......gqqrbbbbbbBxrRRq",
    ".......gqrbbbbbBxrRRrq",
    "........ggrbbbBxrgRrrq",
    ".........rrxbBxrrgRrrq",
    ".........rrrxxrrrgRrqq",
    "........qrrrrrrrrgrrqq",
    "........qqrrrrrrrgrrqq",
    "........qqrrrrrrrgrqqq",
    ".......qqqrrrrrrrgrqqq",
]
# A bundle of herbs hung up to dry on its string, 7 by 11: the tie of red thread and the leaves, olive and gold.
HERBS = ["...s...", "...s...", "...s...", "..bbb..", ".gGgGg.", "gGgaaGg", "gGgGgGg", ".gaGgg.", ".g.G.g.",
         "..g.g..", "...g..."]
# Three books lying one on another, 14 by 7: red, blue and green leather, their pages' edges pale.
BOOKS = ["..rrrrrrrrrr..", "..rppppppppRr.", ".bbbbbbbbbbbb.", ".bppppppppppB.", "gggggggggggggg",
         "gppppppppppppG", "GGGGGGGGGGGGGG"]
# A three-legged stool, 12 by 5.
STOOL = ["OOOOOOOOOOOO", "oooooooooooo", ".o...o....o.", ".o...o....o.", "o....o.....o"]


def small_alchemist(p: Pix, x, y, night, L="base"):
    """The alchemist for a phone, top-left at (x, y), holding up his flask of gold, glowing by night."""
    k = -1 if night else 0
    Rb, Cp = BLUE, RED
    pal = {"k": Cp[1 + k], "K": AMBER[2], "c": Cp[2 + k], "C": Cp[4 + k], "p": Cp[1], "Y": GOLD[5 + k],
           "y": GOLD[3 + k], "z": GOLD[1], "h": ASH[5 + k], "H": ASH[3 + k], "f": SKIN[3 + k], "F": SKIN[2 + k],
           "n": SKIN[4 + k], "m": SKIN[1], "e": OAK[0], "b": ASH[6 + k], "B": ASH[4 + k], "x": ASH[2 + k],
           "r": Rb[2 + k], "R": Rb[4 + k], "q": Rb[1 + k], "g": GOLD[4 + k], "u": BONE[5 + k], "U": BONE[3 + k],
           "a": SKIN[3 + k], "o": GLASS[3], "O": GLASS[1], "i": GOLD[1] if night else GLASS[5], "W": C["white"],
           "l": GOLD[5 if night else 4], "L": GOLD[6 if night else 5], "d": GOLD[3 if night else 2]}
    sprite(p, x, y, ALCHEMIST_SMALL, pal, L)
    if night:
        pool(p, x + 6, y + 7, 16, 14, GOLD[4], (0.08, 0.16, 0.26, 0.36))
        lamp(p, x + 6, y + 7, 14, GOLD[4], tint=0)


def herbs(p: Pix, x, ceiling, drop, night, kind=0, L="base"):
    """A bundle of herbs hung to dry from the shelf at row `ceiling` on a string `drop` rows long, top-left at
    x; `kind` turns its leaves another way."""
    k = -1 if night else 0
    art = [r[::-1] for r in HERBS] if kind % 2 else HERBS
    for yy in range(ceiling, ceiling + drop):
        p.px(x + 3, yy, AMBER[2 + k], L)
    sprite(p, x, ceiling + drop, art, {"s": AMBER[2 + k], "b": RED[2 + k], "g": CROC[3 + k], "G": CROC[5 + k],
                                       "a": AMBER[4 + k]}, L)


def books(p: Pix, x, foot, night, L="base"):
    """Three books lying one on another, their foot on the row above `foot`."""
    k = -1 if night else 0
    sprite(p, x, foot - len(BOOKS), BOOKS, {"r": RED[3 + k], "R": RED[1], "b": BLUE[3 + k], "B": BLUE[1],
                                            "g": GREEN[3 + k], "G": GREEN[1], "p": BONE[5 + k]}, L)


def candle(p: Pix, x, foot, night, phase=0, motion=True, h=4, L="base"):
    """A stub of candle standing on the row above `foot` at x, its wick dark by day and by night burning, its
    flame flickering in a moving header and its light on what stands near it."""
    k = -1 if night else 0
    for yy in range(foot - h, foot):
        p.px(x, yy, BONE[6 + k], L)
        p.px(x + 1, yy, BONE[4 + k], L)
    p.px(x, foot - h - 1, OAK[0], L)
    if not night:
        return
    Lf = p.flicker(phase) if motion else L
    for (dx, dy, c) in ((0, -1, FIRE[6]), (0, -2, FIRE[5]), (0, -3, FIRE[4]), (1, -1, FIRE[4]), (-1, -1, FIRE[3])):
        p.px(x + dx, foot - h - 1 + dy, c, Lf)
    if motion:
        p.halo(x + 0.5, foot - h - 2.5, 4, 4, FIRE[5], (0.12, 0.24), L=p.flicker(phase, back=True))
    else:
        shine(p, x + 0.5, foot - h - 2.5, 4, FIRE[5])
    pool(p, x + 0.5, foot - h - 2, 18, 15, FIRE[4], (0.06, 0.12, 0.2, 0.3))
    lamp(p, x + 0.5, foot - h - 2, 13, FIRE[4], own={(x + i, yy) for i in (0, 1) for yy in range(foot - h, foot)})


def stool(p: Pix, x, foot, night, L="base"):
    """A three-legged stool of oak, its legs on the row above `foot`. Returns the row of its seat."""
    k = -1 if night else 0
    sprite(p, x, foot - len(STOOL), STOOL, {"O": OAK[5 + k], "o": OAK[2 + k]}, L)
    return foot - len(STOOL)


def jars(p: Pix, x, foot, night, names=("jar", "albarello", "bottle"), elixirs=("green", None, "violet"), L="base"):
    """A few of the shelf's vessels standing side by side on the row above `foot`, from x."""
    for name, elixir in zip(names, elixirs):
        rows = VESSELS[name][0]
        for (i, j), c in _art(rows, _vessel_pal(elixir, night), x, foot - len(rows)).items():
            p.px(i, j, c, L)
        x += len(rows[0]) + 1
    return x


# The signs of the seven metals, as the table on the wall draws them, each as tall as a line of its writing:
# gold's circle with its point, silver's crescent, quicksilver's horns, copper's mirror, iron's arrow, tin's four
# and lead's sickle.
METALS = {
    "gold": ["...###...", ".##...##.", ".#.....#.", "#.......#", "#...#...#", "#.......#", ".#.....#.", ".##...##.",
             "...###..."],
    "silver": ["..##.", ".#...", "#....", "#....", "#....", "#....", "#....", ".#...", "..##."],
    "quicksilver": ["#.....#", ".#...#.", "..###..", ".#...#.", "#.....#", "#.....#", ".#...#.", "..###..", "...#...",
                    ".#####.", "...#..."],
    "copper": ["..###..", ".#...#.", "#.....#", "#.....#", ".#...#.", "..###..", "...#...", ".#####.", "...#...",
               "...#..."],
    "iron": ["....####", "......##", ".....#.#", "..###..#", ".#...#..", "#.....#.", "#.....#.", ".#...#..",
             "..###..."],
    "tin": [".##..#.", "#..#.#.", "...#.#.", "..#..#.", ".#...#.", "#######", ".....#.", ".....#.", ".....#."],
    "lead": [".#.....", ".#.....", "####...", ".#.....", ".#.##..", ".##..#.", ".#...#.", ".....#.", "....#.."],
}
CHART_W, CHART_H = 39, 38


def chart(p: Pix, x, y, night, L="base"):
    """The table of the seven metals pinned to the wall, 39 by 38 from (x, y): a sheet of parchment on two brass
    nails, its lower right corner curling over, a rubric of red at its head and a line of writing under it, the
    signs of the seven metals inked large in two rows below, gold's in gold, and a line of writing at its foot,
    its edges shading it off the wall. By night it hangs in the dark but where a light falls on it."""
    k = -3 if night else 0
    w, h = CHART_W, CHART_H
    cells = {}
    for j in range(h):
        for i in range(w):
            a, b = w - 1 - i, h - 1 - j
            if a + b < 5 or (i, j) in ((0, 0), (w - 1, 0), (0, h - 1)):
                continue
            if a <= 5 and b <= 5:
                cells[(x + i, y + j)] = BONE[(6 if a + b > 6 else 5) + k] if a + b > 5 else BONE[max(0, 3 + k)]
                continue
            edge = i == 0 or j == 0 or a == 0 or b == 0
            lit = i < 2 or j < 2
            t = 2 if a == 0 or b == 0 else 5 if lit and not edge else 3 if edge else 4
            if t == 4 and (i * 7 + j * 13) % 23 == 0:
                t = 3
            cells[(x + i, y + j)] = BONE[max(0, t + k)]
    ink, rubric = OAK[0 if night else 1], RED[2 if night else 3]
    rnd = random.Random(7)
    for row, col, x0, x1 in ((3, rubric, 4, w - 5), (5, ink, 4, w - 11), (h - 5, ink, 4, w - 10)):
        xx = x + x0
        while xx < x + x1:
            n = rnd.randint(2, 5)
            for i in range(min(n, x + x1 - xx)):
                cells[(xx + i, y + row)] = col
            xx += n + 1
    for names, top, gap in ((("gold", "silver", "quicksilver", "copper"), 8, 2), (("iron", "tin", "lead"), 22, 4)):
        widths = [len(METALS[n][0]) for n in names]
        xx = x + (w - sum(widths) - gap * (len(names) - 1)) // 2
        for name, gw in zip(names, widths):
            col = GOLD[4 if night else 3] if name == "gold" else ink
            for (i, j), _ in _art(METALS[name], {"#": col}, xx, y + top).items():
                cells[(i, j)] = col
            xx += gw + gap
    for (xx, yy), c in cells.items():
        p.px(xx, yy, c, L)
    p.unlit = set(getattr(p, "unlit", ())) | set(cells)
    for nx in (x + 2, x + w - 3):
        p.px(nx, y + 1, BRASS[4 if night else 5], L)
        p.px(nx + 1, y + 1, BRASS[2], L)
        p.px(nx, y + 2, BRASS[2], L)
    for i in range(1, w - 4):
        p.apx(x + i + 1, y + h, X["shade_ink"], 0.18, L)
    for j in range(1, h - 5):
        p.apx(x + w, y + j + 1, X["shade_ink"], 0.18, L)


# A brass lantern hung on its chain, 9 by 13: its cap and its ring, four panes of glass round a candle, and its
# base with a drip under it. `B b d` the brass, lit to dark, `o O` the panes' edges, `g` the glass, `f` the flame.
LANTERN = [
    "....b....",
    "...BbB...",
    "..BBbbd..",
    ".BbbbbbD.",
    ".o.ggg.O.",
    ".o.gfg.O.",
    ".o.gfg.O.",
    ".o.ggg.O.",
    ".BbbbbbD.",
    "..BbbbD..",
    "...bbd...",
    "....d....",
    "....d....",
]


def lantern(p: Pix, x, ceiling, drop, night, phase=0, motion=True, L="base"):
    """A brass lantern hung on a chain `drop` rows long from the shelf at row `ceiling`, top-left at x: its panes
    bright with the day by day, and by night its candle burning, flickering in a moving header, its light
    falling all round it. Returns the row of its foot."""
    k = -1 if night else 0
    for yy in range(ceiling, ceiling + drop):
        p.px(x + 4, yy, IRON[3 + k] if yy % 2 else IRON[5 + k], L)
    y = ceiling + drop
    pal = {"B": BRASS[5 + k], "b": BRASS[4 + k], "d": BRASS[2 + k], "D": BRASS[1], "o": GLASS[3], "O": GLASS[1],
           "g": GOLD[3] if night else GLASS[5], "f": FIRE[4] if night else GLASS[5]}
    sprite(p, x, y, LANTERN, pal, L)
    if night:
        Lf = p.flicker(phase) if motion else L
        for (dx, dy, c) in ((4, 5, FIRE[5]), (4, 6, FIRE[6]), (3, 6, FIRE[4]), (5, 6, FIRE[4]), (4, 4, FIRE[4])):
            p.px(x + dx, y + dy, c, Lf)
        pool(p, x + 4.5, y + 6, 30, 26, FIRE[4], (0.06, 0.12, 0.2, 0.3))
        shine(p, x + 4.5, y + 6, 14, GOLD[5], (0.06, 0.12, 0.2))
        lamp(p, x + 4.5, y + 6, 20, FIRE[4], own={(x + i, y + j) for j, row in enumerate(LANTERN)
                                                    for i, ch in enumerate(row) if ch != "."})
    return y + len(LANTERN)


# A row of books standing on a shelf, 15 by 10, their spines in leather of red, blue, green and oak, gold bands
# on them: `r R b B g G o O` the spines lit and shaded, `y` the bands.
SPINES = [
    "..........oo...",
    ".rr.......oO...",
    ".rR.bb....oO.gg",
    ".yy.bB.gg.yy.gG",
    ".rR.yy.gG.oO.gG",
    ".rR.bB.yy.oO.yy",
    ".rR.bB.gG.oO.gG",
    ".yy.bB.gG.yy.gG",
    ".rR.yy.gG.oO.gG",
    ".rR.bB.gG.oO.gG",
]


def spines(p: Pix, x, foot, night, L="base"):
    """A row of books standing on the row above `foot` from x, their spines banded in gold."""
    k = -1 if night else 0
    sprite(p, x, foot - len(SPINES), SPINES, {"r": RED[3 + k], "R": RED[1], "b": BLUE[3 + k], "B": BLUE[1],
                                              "g": GREEN[3 + k], "G": GREEN[1], "o": OAK[4 + k], "O": OAK[2 + k],
                                              "y": GOLD[4 + k]}, L)
    return x + len(SPINES[0])


def lab_section(p: Pix, x0, rule, night, motion=True, lite=False, room=80):
    """The scene beside a section's title, from x0 over 99 columns, standing on the bench and as tall as its
    room: the great alembic on its tall athanor distilling, its long beak running down to the right to the
    receiving flask on a bracket and a drop falling into it; the table of the seven metals pinned to the wall at
    the left with bundles of herbs hung to dry over it, and under it the retort over its spirit lamp and the
    green flask; a brass lantern hung from the shelf between them, its candle burning by night; a shelf of books
    and jars on the wall at the right, and three books under a skull with a candle stub on it on the bench.
    Built to the `room` of rows free of words over the bench: under 86 rows the smaller still of the old
    corner stands, under 52 a smaller one again, and under 30 nothing. Returns the span of the rule it covers."""
    if room < 30:
        return None
    foot = rule - 2
    bench(p, x0 - 1, x0 + 99, rule, night)
    if room < 86:
        size = 2 if room >= 52 else 1
        w, h = ((20, 24), (26, 32))[size - 1]
        fx = x0 + 42
        stain(p, x0 + 2, foot - 10, 14, BLUE[2], seed=4)
        top, _ = athanor(p, fx, foot, w, h, night, phase=2)
        tip = alembic(p, fx + w // 2, top, night, motion, size=size, phase=0)
        seat = stool(p, tip[0] - 5, foot, night)
        receiver(p, tip[0] + 1, seat, night, r=(5, 6)[size - 1], neck=3)
        books(p, x0 + 77, foot, night)
        skull(p, x0 + 80, foot - len(BOOKS), night)
        candle(p, x0 + 86, foot - len(BOOKS) - 7, night, phase=1, motion=motion)
        if room >= 70:
            sy = foot - min(room - 22, 46)
            wall_shelf(p, x0 + 74, x0 + 98, sy, night)
            jars(p, x0 + 76, sy, night, ("jar", "phial", "bottle"), ("green", "amber", "violet"))
        return (x0 - 1, x0 + 99)
    ceiling = foot - room
    # the great still: the athanor as tall as the room leaves under the alembic
    h = min(60, room - 38)
    top, _ = athanor(p, x0 + 44, foot, 32, h, night, phase=2)
    tip = alembic(p, x0 + 60, top, night, motion, size=4, phase=0, run=20, right=True)
    rack = tip[1] + 18
    wall_shelf(p, x0 + 80, x0 + 99, rack, night)
    receiver(p, tip[0] + 1, rack, night, r=6, neck=3)
    # the books and jars on their shelf over it, clear of the beak
    sy = max(ceiling + 13, A_SHELF + 14)
    if tip[1] - 14 > sy + 4:
        wall_shelf(p, x0 + 78, x0 + 99, sy, night)
        x = spines(p, x0 + 80, sy, night)
        jars(p, x + 1, sy, night, ("phial",), ("amber",))
    # under the bracket, on the bench: a skull on three books with its candle
    books(p, x0 + 82, foot, night)
    skull(p, x0 + 85, foot - len(BOOKS), night)
    candle(p, x0 + 91, foot - len(BOOKS) - 7, night, phase=1, motion=motion)
    # the table of the seven metals at the left, the herbs hung to dry over it and the lantern beside it
    cy = max(ceiling + 16, A_SHELF + 16)
    chart(p, x0 + 1, cy, night)
    for i, (hx, drop) in enumerate(((x0 + 6, 2), (x0 + 18, 4), (x0 + 30, 1))):
        herbs(p, hx, A_SHELF, drop, night, kind=i)
    lantern(p, x0 + 40, A_SHELF, max(6, cy - A_SHELF + 4), night, phase=2, motion=motion)
    # under the table: the retort over its spirit lamp, and the green flask
    under = foot - (cy + CHART_H + 2)
    if under >= 23:
        retort(p, x0 + 5, foot, night, motion, phase=1, headroom=under - 23)
    if under >= 15:
        green_flask(p, x0 + 31, foot, night, motion, r=5, neck=3)
    stain(p, x0 + 21, foot - 18, 10, BLUE[2], seed=4)
    return (x0 - 1, x0 + 99)


# The great hourglass, 13 by 18, between its oak plates on two turned posts: the sand heaped in the lower bulb and
# running down from the upper, its stream through the neck. `B b` the posts and plates, lit and shaded, `o O` the
# glass, `e` the glass with the wall behind it, `S s` the sand, lit and shaded.
GREAT_GLASS = [
    "BBBBBBBBBBBBB",
    "bbbbbbbbbbbbb",
    ".B.ooooooO.b.",
    ".B.oSSSSsO.b.",
    ".B.oeSSSsO.b.",
    ".B..oeSsO..b.",
    ".B...oeO...b.",
    ".B....o....b.",
    ".B....s....b.",
    ".B...oeO...b.",
    ".B..oe.eO..b.",
    ".B.oe.s.eO.b.",
    ".B.oe.s.eO.b.",
    ".B.oeSSSeO.b.",
    ".B.oSSSSsO.b.",
    ".B.ooooooO.b.",
    "bbbbbbbbbbbbb",
    "BBBBBBBBBBBBB",
]


def great_glass(p: Pix, x, foot, night, motion=True, L="base"):
    """The great hourglass standing on the row above `foot` from x, its sand running grain by grain in a moving
    header."""
    k = -1 if night else 0
    y = foot - len(GREAT_GLASS)
    sprite(p, x, y, GREAT_GLASS, {"B": OAK[5 + k], "b": OAK[2 + k], "o": GLASS[3], "O": GLASS[1],
                                  "e": GLASS[5] if not night else DUSK[3], "S": AMBER[4 + k], "s": AMBER[2 + k]}, L)
    if motion:
        for f in range(FRAMES):
            p.px(x + 6, y + 9 + f % 3, AMBER[5 + k], tick(p, f))


def candlestick(p: Pix, x, foot, night, phase=0, motion=True, L="base"):
    """A tall candle in a brass candlestick standing on the row above `foot` from x, 5 wide: its base, its stem
    and its drip pan of brass, the candle on it, its wick dark by day and by night its flame burning,
    flickering in a moving header and its light falling all round it."""
    k = -1 if night else 0
    for i, c in enumerate((BRASS[5 + k], BRASS[4 + k], BRASS[4 + k], BRASS[3 + k], BRASS[1])):
        p.px(x + i, foot - 1, c, L)
    for yy in range(foot - 5, foot - 1):
        p.px(x + 2, yy, BRASS[4 + k] if yy % 2 else BRASS[3 + k], L)
    for i, c in enumerate((BRASS[5 + k], BRASS[4 + k], BRASS[4 + k], BRASS[2 + k], BRASS[1])):
        p.px(x + i, foot - 6, c, L)
    candle(p, x + 1, foot - 6, night, phase=phase, motion=motion, h=7)


GREAT_R, GREAT_MOST = 15, 60    # the great armillary sphere's radius, and the most rows it rises with its stand


def lab_strip(p: Pix, x0, rule, night, motion=True, lite=False, room=60):
    """What stands beside a strip's title, from x0 over 50 columns: the great armillary sphere at the right on its
    turned stand of brass, rising from the bench the strip's full height, GREAT_MOST rows at the most; at the left
    the great hourglass with its sand running on a pile of books, and a tall candle in its brass candlestick,
    burning by night; and under the sphere the green flask bubbling and a jar of the violet elixir, their light on
    the wall by night. Built to the `room` of rows free of words: under 46 rows the smaller sphere and a smaller
    hourglass stand on the bench with books and a phial, and under 22 nothing stands. Returns the span of the rule
    it covers."""
    if room < 22:
        return None
    foot = rule - 2
    bench(p, x0 - 1, x0 + 50, rule, night)
    if room < 46:
        r = max(6, min(12, (room - 10) // 2))
        armillary(p, x0 + 15, foot - 8 - r, r, night)
        books(p, x0 + 31, foot, night)
        if room >= 28:
            hourglass(p, x0 + 33, foot - len(BOOKS), night, motion)
        green_flask(p, x0 + 46, foot, night, motion, r=3, neck=3)
        return (x0 - 1, x0 + 50)
    cx = x0 + 45 - GREAT_R
    great_armillary(p, cx, foot - min(room, GREAT_MOST), foot, GREAT_R, night)
    books(p, x0, foot, night)
    great_glass(p, x0, foot - len(BOOKS), night, motion)
    candlestick(p, x0 + 15, foot, night, phase=1, motion=motion)
    green_flask(p, cx + 9, foot, night, motion, r=3, neck=3)
    jars(p, cx + 13, foot, night, ("jar",), ("violet",))
    if night:
        pool(p, cx + 16.5, foot - 5, 20, 16, VIOLET[5], (0.06, 0.12, 0.2, 0.28))
        lamp(p, cx + 16.5, foot - 5, 12, VIOLET[5])
    return (x0 - 1, x0 + 50)


# --------------------------------------------------------------------------- a phone's scenes
def phone_left(p: Pix, x0, rule, night, room=40):
    """The left of a phone's laboratory, 30 columns from x0 on the bench along the rule: the alchemist holding up
    his flask of gold behind it and a skull at its end, and over him the round window, the sun coming down through
    it by day and the stars in it by night, built to the `room` the words leave: with fewer than 44 rows the
    window goes, with fewer than 26 the skull and the green flask stand alone, and under 12 nothing."""
    if room < 12:
        return None
    foot = rule - 2
    bench(p, x0 - 1, x0 + 31, rule, night)
    if room >= 44:
        cy = foot - 34
        window(p, x0 + 9.5, cy + 0.5, 6.5, night, motion=False)
        if not night:
            sunbeam(p, cy + 3, foot - 1, x0 + 6, 7, x0 + 12, 14, seed=2, motion=False, lite=True)
        else:
            moonbeam(p, cy + 3, foot - 1, x0 + 6, 7, x0 + 12, 14)
    if room >= 26:
        small_alchemist(p, x0 + 8, foot - len(ALCHEMIST_SMALL), night)
        skull(p, x0, foot, night)
    else:
        skull(p, x0 + 2, foot, night)
        green_flask(p, x0 + 16, foot, night, motion=False, r=3, neck=2)
    return (x0 - 1, x0 + 31)


def phone_still(p: Pix, x1, rule, night, room=40):
    """A phone's still on the bench, ending at column x1 and 25 columns wide: the alembic on its athanor, its beak
    running down to the receiving flask, built to the `room` the words leave: from 41 rows the alembic of a
    wide header's still on a taller athanor, then a smaller one, with a bundle of herbs hung over it from the top
    shelf where the room reaches it; under 30 rows the retort over its spirit lamp stands alone, under 23 a flask
    of green elixir, and under 16 nothing."""
    if room < 16:
        return None
    foot = rule - 2
    bench(p, x1 - 25, x1, rule, night)
    if room >= 41:
        top, _ = athanor(p, x1 - 17, foot, 16, 22, night, phase=2)
        tip = alembic(p, x1 - 9, top, night, motion=False, size=1, phase=0, run=6)
        receiver(p, tip[0] + 1, foot, night, r=3, neck=2)
    elif room >= 30:
        if room >= 44 and foot - room <= A_SHELF + 2:
            herbs(p, x1 - 16, A_SHELF, 2, night, kind=1)
        top, _ = athanor(p, x1 - 15, foot, 14, 16, night, phase=2)
        tip = alembic(p, x1 - 8, top, night, motion=False, size=0, phase=0)
        receiver(p, tip[0] + 1, foot, night, r=3, neck=2)
    elif room >= 23:
        retort(p, x1 - 19, foot, night, motion=False, headroom=room - 23)
    else:
        green_flask(p, x1 - 10, foot, night, motion=False, r=4, neck=3)
    return (x1 - 25, x1)


def phone_lab(p: Pix, x0, rule, night, room=40):
    """The left of a phone's laboratory from x0, where a phone's header leaves the room: the alchemist of a wide
    header behind his workbench, holding up his flask of gold in front of the round window, the sun coming down
    through it by day and the stars in it by night, the open book and the green flask on the bench and the brass
    mortar too where he shows enough of himself over it. From 47 rows down to 38 the laboratory closes in round
    him at the same size: the bench stands lower and hides more of him, the window is smaller, and the book
    goes so his flask stays clear. With fewer than 38 rows the smaller corner of `phone_left` stands instead."""
    if room < 38:
        return phone_left(p, x0 + 1, rule, night, room)
    foot = rule - 2
    bench(p, x0 - 1, x0 + 51, rule, night)
    top = foot - (max(9, min(16, room - 39)) if room >= 47 else 7)
    sy = max(top - (len(ALCHEMIST) - 4), foot - room + 1)
    r = 10 if room >= 52 else 8 if room >= 47 else 7
    cy = sy + min(9, r + 1)
    window(p, x0 + 11, cy, r, night, motion=False)
    if not night:
        sunbeam(p, cy + 2, top - 1, x0 + 3, 10, x0 + 17, 22, seed=2, motion=False, lite=True)
    else:
        moonbeam(p, cy + 2, top - 1, x0 + 3, 10, x0 + 17, 22)
    alchemist(p, x0 + 1, sy, night, bench=top)
    workbench(p, x0 - 1, x0 + 50, top, foot, night)
    if top - sy >= 41:
        mortar(p, x0 + 3, top, night)
    if room >= 47:
        book(p, x0 + 17, top, night)
    green_flask(p, x0 + 42, top, night, motion=False, r=4, neck=3)
    return (x0 - 1, x0 + 51)


def phone_middle(p: Pix, x0, x1, rule, night, room=40):
    """The middle of a phone's laboratory from x0 to x1 on the bench, where a phone's header leaves the room: the
    retort over its spirit lamp, a skull on three books and the green flask bubbling, and over them a shelf on the
    wall with jars; under 38 rows the shelf goes, and under 24 nothing stands."""
    if room < 24:
        return None
    foot = rule - 2
    bench(p, x0 - 1, x1 + 1, rule, night)
    retort(p, x0 + 2, foot, night, motion=False, headroom=room - 23)
    books(p, x0 + 26, foot, night)
    skull(p, x0 + 29, foot - len(BOOKS), night)
    green_flask(p, x0 + 50, foot, night, motion=False, r=5, neck=3)
    if room >= 38:
        sy = foot - min(room - 12, 34)
        wall_shelf(p, x0 + 26, x0 + 56, sy, night)
        jars(p, x0 + 29, sy, night, ("jar", "phial", "bottle"), ("violet", "amber", "green"))
    return (x0 - 1, x1 + 1)


# The rows a phone's section and strip headers ask for under their words, whatever the words: the still beside the
# table of the seven metals, and the great armillary sphere on its stand, each at its full height.
UNDER = {"H2": 58, "H3": 56}
STILL_LEAST = 44      # the fewest rows over the bench a phone's still or sphere stands in, the hand's least for a hero
PHONE_R = 17          # the great armillary sphere's radius on a phone, which has the room for it


def phone_section(p: Pix, x0, x1, rule, night, room=58):
    """A section's laboratory under a phone's words, on the bench along the rule from x0 to x1 and as tall as its
    `room` of rows over the bench: at the left the table of the seven metals pinned to the wall, the green flask
    bubbling under it; in the middle the still, the alembic on a tall athanor rising the room's height, its beak
    running down to the receiving flask on a stool; at the right the retort over its spirit lamp and a skull on
    three books with a candle on it, and over them a shelf of books and jars. By night the furnace's fire, the
    spirit lamp, the candle and the elixirs light the room. Under STILL_LEAST rows the still stands smaller with
    the retort and the skull beside it. Returns the span of the rule it covers."""
    foot = rule - 2
    bench(p, x0 - 1, x1 + 1, rule, night)
    ceiling = foot - room
    if room < STILL_LEAST:
        top, _ = athanor(p, x0 + 44, foot, 20, max(12, room - 20), night, phase=2)
        tip = alembic(p, x0 + 54, top, night, motion=False, size=1, phase=0, run=10, right=True)
        receiver(p, tip[0] + 1, stool(p, tip[0] - 5, foot, night), night, r=5, neck=3)
        retort(p, x0 + 90, foot, night, motion=False, headroom=room - 23)
        books(p, x0 + 112, foot, night)
        skull(p, x0 + 115, foot - len(BOOKS), night)
        return (x0 - 1, x1 + 1)
    # the table of the seven metals, pinned high on the wall, and the green flask on the bench under it
    chart(p, x0 + 2, ceiling + 2, night)
    green_flask(p, x0 + 21, foot, night, motion=False, r=5, neck=3)
    # the still: the athanor as tall as the room leaves under the alembic
    size = 3
    h = room - 27
    top, _ = athanor(p, x0 + 46, foot, 26, h, night, phase=2)
    tip = alembic(p, x0 + 59, top, night, motion=False, size=size, phase=0, run=14, right=True)
    receiver(p, tip[0] + 1, stool(p, tip[0] - 5, foot, night), night, r=6, neck=3)
    # the retort and the skull on its books with its candle, and the shelf of books and jars over them
    x = x0 + 101
    retort(p, x, foot, night, motion=False, headroom=room - 23)
    books(p, x + 21, foot, night)
    skull(p, x + 24, foot - len(BOOKS), night)
    candle(p, x + 30, foot - len(BOOKS) - 7, night, phase=1, motion=False)
    sy = foot - 32
    wall_shelf(p, x + 2, x1 - 1, sy, night)
    xx = spines(p, x + 5, sy, night)
    jars(p, xx + 2, sy, night, ("jar", "phial", "bottle"), ("violet", "amber", "green"))
    if night:
        pool(p, xx + 5.5, sy - 5, 20, 16, VIOLET[5], (0.06, 0.12, 0.2))
    return (x0 - 1, x1 + 1)


def phone_strip_under(p: Pix, x0, x1, rule, night, room=56):
    """A strip's laboratory under a phone's words, on the bench along the rule from x0 to x1: in the middle the great
    armillary sphere on its turned stand of brass, rising the `room` of rows over the bench, GREAT_MOST at the
    most; at its left the great hourglass on a pile of books and a tall candle in its brass candlestick, burning by
    night; at its right the green flask bubbling, a skull and a jar of the violet elixir, its light on the wall by
    night. Under STILL_LEAST rows the smaller sphere stands on its own foot. Returns the span of the rule it
    covers."""
    foot = rule - 2
    bench(p, x0 - 1, x1 + 1, rule, night)
    mid = (x0 + x1) // 2
    r = PHONE_R
    if room < STILL_LEAST:
        r = max(6, min(12, (room - 10) // 2))
        armillary(p, mid, foot - 8 - r, r, night)
    else:
        great_armillary(p, mid, foot - min(room, GREAT_MOST), foot, r, night)
    left = mid - r - 4
    candlestick(p, left - 5, foot, night, phase=1, motion=False)
    books(p, left - 22, foot, night)
    great_glass(p, left - 22, foot - len(BOOKS), night, motion=False)
    sy = foot - 40
    wall_shelf(p, x0 + 1, left - 2, sy, night)
    jars(p, x0 + 4, sy, night, ("pear", "jar", "flask"), ("red", None, "amber"))
    for i, hx in enumerate((x0 + 7, x0 + 19, x0 + 31)):
        herbs(p, hx, sy + 3, 1 + i % 2, night, kind=i)
    right = mid + r + 4
    green_flask(p, right + 5, foot, night, motion=False, r=5, neck=3)
    skull(p, right + 13, foot, night)
    jars(p, right + 23, foot, night, ("jar", "albarello"), ("violet", None))
    sy = foot - 30
    wall_shelf(p, right + 2, x1 - 1, sy, night)
    xx = spines(p, right + 5, sy, night)
    jars(p, xx + 2, sy, night, ("bottle", "phial"), ("amber", "red"))
    if night:
        pool(p, right + 26.5, foot - 5, 22, 18, VIOLET[5], (0.06, 0.12, 0.2, 0.28))
        lamp(p, right + 26.5, foot - 5, 12, VIOLET[5])
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- marks
# The sign for gold, 9 by 9: a ring with a point at its middle, in gold, lit along its upper left.
SUN = ["..GGGgg..", ".Gg...gd.", "Gg.....gd", "G.......d", "G...H...d", "g.......d", "gg.....dd", ".gd...dd.",
       "..ddddd.."]


def sun_sign(p: Pix, x, y, night, L="base"):
    """The sign for gold, a circle with a point at its centre, 9 by 9 from (x, y), its ring of gold lit along its
    upper left and shaded along its lower right; by night it glows."""
    k = 0 if night else -1
    sprite(p, x, y, SUN, {"G": GOLD[6 + k], "g": GOLD[4 + k], "d": GOLD[2 + k], "H": GOLD[6]}, L)
    if night:
        p.halo(x + 4.5, y + 4.5, 7, 7, GOLD[4], (0.06, 0.12), L="haze")


# A phial of green elixir, 7 by 11, stoppered with cork.
PHIAL = ["..kk...", "..kK...", "..oO...", ".ooOO..", "oweeeO.", "oweeeO.", "olllLO.", "oLLLLO.", "oLLLdO.",
         "oLLddO.", ".OOOO.."]


def phial(p: Pix, x, y, night, elixir="green", L="base"):
    """A phial stoppered with cork, 7 by 11 from (x, y), its elixir glowing by night."""
    E = RAMP[elixir]
    sprite(p, x, y, PHIAL, {"k": AMBER[3], "K": AMBER[1], "o": GLASS[3], "O": GLASS[1],
                            "e": E[1] if night else GLASS[5], "w": C["white"], "l": E[6 if night else 5],
                            "L": E[5 if night else 4], "d": E[4 if night else 3]}, L)
    if night:
        p.halo(x + 3, y + 7, 7, 7, E[5], (0.06, 0.12, 0.2), L="haze")


# --------------------------------------------------------------------------- the footer's shelf
# The crucible on its tripod over a spirit lamp, 18 by 19: the crucible of clay (`C c K`) tapering to its foot,
# the metal in its mouth (`w M m`), held in the tripod's ring of iron (`I i`), the brass lamp (`H b`) standing
# between the tripod's legs with its wick (`h`), and the flame (`F f`), there only by night, licking up round the
# crucible's foot.
CRUCIBLE = [
    "..CCCCCCCCCCCCCC..",
    "..CwwMMMMMMMMMmK..",
    "..cmmmmmmmmmmmmK..",
    "...cCcccccccccK...",
    "IIIIcCcccccccKIIII",
    "iiiiicCcccccKiiiii",
    ".Ii..cCcccccK..iI.",
    ".Ii...cCcccK...iI.",
    ".Ii...FcccKF...iI.",
    ".Ii...FFffFF...iI.",
    ".Ii....FffF....iI.",
    ".Ii....FffF....iI.",
    "Ii......hh......iI",
    "Ii.....bHHb.....iI",
    "Ii...bHHHHHHb...iI",
    "Ii..bHHwHHHHHb..iI",
    "Ii..bbHHHHHHbb..iI",
    "Ii...bbbbbbbb...iI",
    "II..............II",
]
# The same for a phone, 13 by 14.
CRUCIBLE_SMALL = [
    ".CCCCCCCCCCc.",
    ".CwMMMMMMMmK.",
    ".cmmmmmmmmmK.",
    "..cCcccccccK.",
    "IIIcCcccccKII",
    "iiiicCcccKiii",
    "Ii...cccK...I",
    "Ii..FFffFF..I",
    "Ii...FffF...I",
    "Ii....hh....I",
    "Ii..bHHHHb..I",
    "Ii.bHwHHHHb.I",
    "Ii..bbbbbb..I",
    "II.........II",
]


def crucible(p: Pix, x, foot, night, small=False, L="base"):
    """The crucible on its tripod over a spirit lamp, its feet on the row above `foot` from x: by day the lamp
    is out and the metal in the crucible is a cold grey cake of lead; by night the flame burns under it, licking
    up round its foot, and the metal is molten gold, glowing, its light on the wall and on what stands near."""
    k = -1 if night else 0
    art = CRUCIBLE_SMALL if small else CRUCIBLE
    y = foot - len(art)
    pal = {"C": CLAY[4 + k], "c": CLAY[2 + k], "K": CLAY[0], "I": IRON[4 + k], "i": IRON[2 + k], "h": ASH[5],
           "H": BRASS[4 + k], "b": BRASS[2 + k]}
    if night:
        pal.update({"m": GOLD[4], "M": GOLD[5], "w": GOLD[6], "F": FIRE[4], "f": FIRE[6]})
    else:
        pal.update({"m": LEAD[3], "M": LEAD[4], "w": LEAD[6]})
    sprite(p, x, y, art, pal, L)
    if not night:
        return
    cx = x + len(art[0]) / 2
    own = {(x + i, y + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch in "wMmFf"}
    shine(p, cx, y + 1.5, len(art[0]) / 2 - 2, GOLD[5])
    fy = y + (8 if small else 10)
    pool(p, cx, fy, 26, 20, FIRE[4], (0.08, 0.15, 0.24, 0.34))
    pool(p, cx, y + 1, 16, 10, GOLD[4], (0.06, 0.12, 0.2))
    lamp(p, cx, fy, 24, FIRE[4], own=own, tint=0)


# The low things on the shelf under a footer's words, where only a few rows are left: two books lying one on
# another, a book lying alone, ingots of lead stacked, a rolled scroll, a little glazed pot tied over with paper
# and a brass bowl of yellow sulphur. `b B r R g G` a book's leather and its shade and `p` its pages; `m M d` the
# lead; `s S` the parchment and `r` its cord; `q Q` the paper; `y Y` the sulphur and `h H` the brass.
TOMES = ["..bbbbbbbbbb.", "..bppppppppB.", "rrrrrrrrrrrr.", "rppppppppppRr", "RRRRRRRRRRRRR"]
TOME = [".gggggggggg.", "gppppppppppG", "GGGGGGGGGGGG"]
INGOTS = ["...mmmm..", "..MMMMMd.", ".mmmMmmmd", "MMMMdMMMd"]
SCROLL = [".sSssssssS.", "sSsrsssssSs", ".SSSrSSSSS."]
POT = [".qqqq.", "qQQQQq", ".bbbB.", "bbbbbB", ".BBBB."]
BOWL = ["..yYy..", "hhhhhhH", ".HHHHH."]
LOW = {"tomes": TOMES, "tome": TOME, "ingots": INGOTS, "scroll": SCROLL, "pot": POT, "bowl": BOWL}


def low_good(p: Pix, name, x, foot, night, L="base"):
    """One of the low things, its foot on the row above `foot` from x."""
    k = -1 if night else 0
    art = LOW[name]
    pal = {"b": BLUE[3 + k], "B": BLUE[1], "r": RED[3 + k], "R": RED[1], "g": GREEN[3 + k], "G": GREEN[1],
           "p": BONE[5 + k], "m": LEAD[5 + k], "M": LEAD[3 + k], "d": LEAD[1], "s": BONE[5 + k], "S": BONE[3 + k],
           "q": BONE[6 + k], "Q": BONE[4 + k], "y": AMBER[5 + k], "Y": GOLD[6 + k], "h": BRASS[5 + k],
           "H": BRASS[2 + k]}
    if name == "scroll":
        pal["r"] = RED[2 + k]
    sprite(p, x, foot - len(art), art, pal, L)


# What stands along a footer's shelves, by turns: books standing and lying, the vessels with their elixirs, the
# skull, the carboy, a candle in its candlestick, the hourglass, the mortar and the low things.
STOCK = ("spines", "jar", "skull", "albarello", "carboy", "pear", "books", "candle", "bottle", "hourglass", "flask",
         "mortar", "phial", "tomes", "ingots", "pot", "scroll", "bowl", "tome")


def _size(name):
    """How wide and how tall one of the goods stands; a candle with the room its flame takes by night."""
    if name in LOW:
        return len(LOW[name][0]), len(LOW[name])
    if name in VESSELS:
        return len(VESSELS[name][0][0]), 10
    if name == "candle":
        return 5, 17
    art = {"spines": SPINES, "skull": SKULL, "books": BOOKS, "carboy": CARBOY, "hourglass": HOURGLASS,
           "mortar": MORTAR}[name]
    return len(art[0]), len(art)


def _good(p: Pix, name, x, foot, night, i):
    """Draw one of the goods, the `i`-th along its shelf, on the row above `foot` from x; by night a vessel's
    elixir lights the wall round it and a candle burns."""
    if name in LOW:
        low_good(p, name, x, foot, night)
    elif name in VESSELS:
        elixir = ELIXIRS[i % len(ELIXIRS)]
        jars(p, x, foot, night, names=(name,), elixirs=(elixir,))
        if night:
            w = len(VESSELS[name][0][0])
            pool(p, x + w / 2, foot - 5, w + 8, 10, RAMP[elixir][5], (0.05, 0.1, 0.16))
    elif name == "candle":
        candlestick(p, x, foot, night, phase=i, motion=False)
    elif name == "hourglass":
        hourglass(p, x, foot, night, motion=False)
    else:
        {"spines": spines, "skull": skull, "books": books, "carboy": carboy, "mortar": mortar}[name](p, x, foot, night)


def _runs(room, x0, x1):
    """The stretches of a shelf over which much the same height is free, as (start, end, height), the end
    excluded."""
    runs, x = [], x0
    while x < x1:
        if room[x] <= 0:
            x += 1
            continue
        a, lo, hi = x, room[x], room[x]
        while x < x1 and room[x] > 0 and max(hi, room[x]) - min(lo, room[x]) <= 3:
            lo, hi = min(lo, room[x]), max(hi, room[x])
            x += 1
        runs.append((a, x, lo))
    return runs


def foot_shelf(p: Pix, night, depth, uid="fr"):
    """A footer's bottom shelf, `depth` rows deep along its foot, its ends capped in brass where it is deep
    enough, and its shadow on the wall over it."""
    w, h = p.w, p.h
    k = -1 if night else 0
    p.defs.append(_board(uid + "f", depth, night, h - depth, grain=not p.lite))
    p.shapes["base"].append(f'<rect y="{h - depth}" width="{w}" height="{depth}" fill="url(#{uid}f)"/>')
    for xx in range(POST, w - POST):
        p.apx(xx, h - depth - 1, X["shade_ink"], 0.2, "base")
    caps = (BRASS[5 + k], BRASS[3 + k], BRASS[1]) if depth >= 5 else (BRASS[4 + k],)
    for bx in (1, w - 5):
        for j, c in enumerate(caps):
            p.hline(bx, bx + 4, h - depth + 1 + j, c)
        if depth >= 5:
            p.px(bx + 1, h - depth + 2, BRASS[0])


def stock(p: Pix, night, rule, mark=None):
    """A footer's last pass, once every word in it is set: its bottom shelf, four rows deep, or three where
    the words come down to it, and on it and on every rule its cells stand on, wherever they leave room, the
    crucible and the laboratory's goods, books and jars, the skull and the rest, each standing two units clear
    of every word and clear of the rules. The crucible stands nearest `mark`, the corner the layout keeps for
    the footer's mark, or else at the far end of the roomiest shelf; if it fits nowhere at its size it stands
    smaller. By night the crucible's flame, the candles and the elixirs light the wall and what stands near
    them."""
    w, h = p.w, p.h
    low = max((b[3] for b in p.words), default=0)
    depth = max(3, min(FOOT - 1, h - low))
    foot_shelf(p, night, depth)
    floor = h - depth
    open_pools(p)
    base = p.layers["base"]
    x0, x1 = POST + 1, w - POST - 1
    blocked = {xy for xy, c in base.items() if ":" not in c}
    for (a, b, c, d) in p.words:
        blocked.update((xx, yy) for xx in range(a - 2, c + 2) for yy in range(b - 2, d + 2))
    rules = [y for y in range(BOARD + 2, floor) if all(base.get((x, y)) == rule for x in range(x0, x1))]
    shelves = []
    top = BOARD + 2
    for f in rules + [floor]:
        room = {}
        for x in range(x0, x1):
            n = 0
            while f - 1 - n >= top and (x, f - 1 - n) not in blocked:
                n += 1
            room[x] = n
        shelves.append((f, room))
        top = f + 1

    def fits(room, x, wd, ht):
        """Whether a thing `wd` by `ht` stands at x with a free column on either side of it."""
        return (x - 1 >= x0 and x + wd < x1 and room[x - 1] > 0 and room[x + wd] > 0
                and all(room[xx] >= ht for xx in range(x, x + wd)))

    def take(room, x, wd):
        for xx in range(x - 1, x + wd + 1):
            if xx in room:
                room[xx] = 0

    placed = None
    for small in (False, True):
        art = CRUCIBLE_SMALL if small else CRUCIBLE
        wd, ht = len(art[0]), len(art)
        spots = []
        for (f, room) in shelves:
            for x in range(x0, x1 - wd + 1):
                if fits(room, x, wd, ht + 1):
                    near = abs(x + wd // 2 - mark[0]) + 2 * abs(f - mark[1] - ht) if mark else -x - f
                    spots.append((near, x, f, room))
        if spots:
            _, x, f, room = min(spots, key=lambda s: s[:3])
            crucible(p, x, f, night, small=small)
            take(room, x, wd)
            placed = x
            break
    i = 0
    for (f, room) in shelves:
        for (a, b, ht) in _runs(room, x0, x1):
            # a tall stretch takes tall things side by side, set in its middle with a free column at either end;
            # a stretch too low for a jar takes a low thing or two spaced out along it, never a row of them
            least = 8 if ht >= 12 else 0
            row, x = [], a + 1
            while True:
                for j in range(len(STOCK)):
                    name = STOCK[(i + j) % len(STOCK)]
                    wd, gh = _size(name)
                    if least <= gh < ht and x + wd < b:
                        row.append((name, x, i + j))
                        i += j + 1
                        x += wd + 2
                        break
                else:
                    break
            if not row:
                continue
            if ht < 8:
                row = [(n, gx, k) for (n, gx, k) in row if n in LOW][:max(1, (b - a) // 30)]
                gap = (b - a) / len(row)
                for m, (name, _, k) in enumerate(row):
                    _good(p, name, round(a + gap * (m + 0.5) - _size(name)[0] / 2), f, night, k)
                continue
            end = max(gx + _size(n)[0] for (n, gx, _) in row)
            shift = (b - 1 - end) // 2
            for (name, gx, n) in row:
                _good(p, name, gx + shift, f, night, n)
    hang_up(p, night, blocked, floor)
    lay_pools(p, POST, BOARD + 1, w - POST, floor)
    return placed


def hang_up(p: Pix, night, blocked, floor):
    """What hangs from a footer's top shelf over a stretch of wall its words and its goods leave empty, at
    least 30 columns wide and 15 rows deep: the stuffed crocodile on its ropes where there is room for it, and
    on either side of it bundles of herbs drying and, by turns, a brass lantern, lit by night."""
    w = p.w
    ceiling = BOARD + 1
    x0, x1 = POST + 1, w - POST - 1
    blocked = blocked | {xy for xy, c in p.layers["base"].items() if ":" not in c}
    room = {}
    for x in range(x0, x1):
        n = 0
        while ceiling + n < floor and (x, ceiling + n) not in blocked:
            n += 1
        room[x] = n
    for (a, b, ht) in _runs(room, x0, x1):
        if b - a < 30 or ht < 15:
            continue
        spans = [(a + 2, b - 2)]
        if b - a >= 60 and ht >= 16:
            cx = (a + b - len(CROCODILE[0])) // 2
            crocodile(p, cx, ceiling + min(4, ht - 14), ceiling, night)
            spans = [(a + 2, cx - 4), (cx + len(CROCODILE[0]) + 4, b - 2)]
        n = 0
        for (s0, s1) in spans:
            count = (s1 - s0 + 6) // 26
            for j in range(count):
                x = round(s0 + (s1 - s0) * (j + 0.5) / count) - 4 + (2, -3, 0, 3, -2)[n % 5]
                x = max(s0, min(s1 - len(LANTERN[0]), x))
                drop = (1, 4, 2, 5, 3)[n % 5]
                if n % 3 == 1 and drop + len(LANTERN) < ht - 1:
                    lantern(p, x, ceiling, drop, night, phase=n, motion=False)
                elif drop + len(HERBS) < ht - 1:
                    herbs(p, x + 1, ceiling, drop, night, kind=n)
                n += 1


# --------------------------------------------------------------------------- links
# Icons for the link buttons, 9 by 7, bold enough to read at the kit's size: a round flask, an hourglass, the
# sign for gold and a book. `#` is the button's ink, `e` the phial's elixir, `g` gold.
ICONS = {
    "flask": ["...###...", "...#.#...", "..#...#..", ".#eeeee#.", "#eeeeeee#", "#eeeeeee#", ".#######."],
    "hourglass": ["#########", ".#.....#.", "..#ggg#..", "...#g#...", "..#.g.#..", ".#ggggg#.", "#########"],
    "sun": ["..#####..", ".#.....#.", "#...g...#", "#..ggg..#", "#...g...#", ".#.....#.", "..#####.."],
    "book": ["###...###", "#..#.#..#", "#.e#.#e.#", "#..#.#..#", "#.e#.#e.#", "#..#.#..#", "####.####"],
}
LINK_ICONS = ("flask", "hourglass", "sun", "book")


def phial_link(p: Pix, x0, x1, y, seed, night):
    """A link button finished as a phial lying on its side: the button's left end narrowed to the phial's neck
    and stoppered with a cork, its right end rounded off with the elixir showing through the glass there, the
    glass lit along its top with a glint, the elixir lying along its foot, and the paper label it is lettered
    on between. `seed` (the layout's, from the label) picks its elixir."""
    E = RAMP[("green", "violet", "amber", "red")[seed % 4]]
    k = -1 if night else 0
    w = p.w
    base = p.layers["base"]
    edge = GLASS[2]
    # the neck and its cork at the left, and the rounded foot at the right
    for (xx, yy) in ((0, y), (1, y), (2, y), (0, y + 1), (1, y + 1), (0, y + 2), (0, y + 8), (0, y + 9), (1, y + 9),
                     (0, y + 10), (1, y + 10), (2, y + 10), (w - 1, y), (w - 2, y), (w - 1, y + 1),
                     (w - 1, y + 9), (w - 1, y + 10), (w - 2, y + 10)):
        base.pop((xx, yy), None)
    for (xx, yy) in ((2, y + 1), (3, y), (1, y + 2), (2, y + 9), (3, y + 10), (1, y + 8), (w - 3, y),
                     (w - 2, y + 1), (w - 3, y + 10), (w - 2, y + 9)):
        p.px(xx, yy, edge)
    for yy in range(y + 3, y + 8):
        p.px(0, yy, AMBER[4 + k] if yy == y + 3 else AMBER[2 + k])
        p.px(1, yy, AMBER[5 + k] if yy == y + 3 else AMBER[3 + k])
    p.px(2, y + 2, GLASS[4 + k])
    p.px(2, y + 8, GLASS[1])
    for yy in range(y + 2, y + 9):
        p.px(3, yy, GLASS[3] if yy < y + 5 else GLASS[2])
    for xx in range(4, w - 2):
        p.px(xx, y + 1, GLASS[5 + k] if (xx - 5) % 19 else C["white"])
    p.hline(4, w - 2, y + 9, E[4 + k])
    for xx in range(w - 5, w - 1):
        for yy in range(y + 2, y + 9):
            if (xx, yy) in base:
                p.px(xx, yy, E[(5 if yy < y + 4 else 4 if yy < y + 7 else 3) + k] if xx < w - 2 else edge)


# --------------------------------------------------------------------------- the elements: brass and glass
def brass_card(p: Pix, x, y, w, h, night, ink, seed=0, L="base"):
    """A schematic's card as an apothecary's label in a frame of brass: the frame lit along its top and left and
    dark along its foot and right, a rivet at each corner; at the left a panel of dark oak with the icon engraved
    in a round medallion of brass; then a strip of brass, and the label of parchment the words are written on,
    shaded under the frame, pale by day and dark by night so the words keep their contrast. `ink` is the colour
    the layout drew the icon in, which this takes up and engraves again in the medallion."""
    k = -1 if night else 0
    icon_y = y + (h - 7) // 2
    icon = {(xx - x - 2, yy - icon_y) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9)
            if p.get(xx, yy) == ink}
    paper, shade = (BONE[0], OAK[2]) if night else (BONE[5], BONE[4])
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + w - 3):
            if xx < x + 14:
                c = OAK[2 + k] if xx > x + 2 else OAK[3 + k]
            elif xx == x + 14:
                c = BRASS[3 + k]
            else:
                c = shade if yy == y + 2 or xx == x + 15 else paper
            p.px(xx, yy, c, L)
    for xx in range(x, x + w):
        p.px(xx, y, BRASS[5 + k], L)
        p.px(xx, y + 1, BRASS[3 + k], L)
        p.px(xx, y + h - 2, BRASS[2 + k], L)
        p.px(xx, y + h - 1, BRASS[1], L)
    for yy in range(y + 1, y + h - 1):
        p.px(x, yy, BRASS[5 + k], L)
        p.px(x + 1, yy, BRASS[3 + k], L)
        p.px(x + w - 3, yy, BRASS[3 + k], L)
        p.px(x + w - 2, yy, BRASS[2 + k], L)
        p.px(x + w - 1, yy, BRASS[1], L)
    for rx, ry in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
        for (dx, dy), c in (((0, 0), BRASS[6 + k]), ((1, 0), BRASS[4 + k]), ((0, 1), BRASS[4 + k]),
                            ((1, 1), BRASS[1])):
            p.px(rx + dx, ry + dy, c, L)
    # the medallion: a disc of brass, lit on its upper left, the icon engraved at its heart
    cx, cy, r = x + 7.5, y + h / 2, 5.3
    for yy in range(math.floor(cy - r), math.ceil(cy + r)):
        for xx in range(math.floor(cx - r), math.ceil(cx + r)):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if rho > r:
                continue
            lit = dx + dy < 0
            if rho > r - 1:
                c = BRASS[6 + k] if lit else BRASS[1]
            else:
                c = BRASS[5 + k] if dx + dy < -r * 0.9 else BRASS[4 + k] if lit else BRASS[3 + k]
            p.px(xx, yy, c, L)
    ox, oy = round(cx - 3.5), round(cy - 3.5)
    for (i, j) in icon:
        p.px(ox + i, oy + j, OAK[0], L)


def tube_over(p: Pix, cells, night, elixir="green", L="base"):
    """A wire redrawn as tubing of clear glass with an elixir running in it along its `cells` (x, y, direction):
    the tube two units wide inside its walls, the near wall lit and the far one dark, a line of light along the
    glass over the elixir, and a collar of brass where the tube leaves its card and at each bend."""
    E = RAMP[elixir]
    k = -1 if night else 0
    lit, dark = GLASS[5 + k], GLASS[1]
    shine, flow = (E[6], E[5]) if night else (GLASS[6], E[4])
    seen: dict = {}
    for (x, y, d) in cells:
        seen.setdefault((x, y), set()).add(d)
    for (x, y), ds in seen.items():
        if "h" in ds:
            for dy, c in ((-1, lit), (0, shine), (1, flow), (2, dark)):
                if "v" not in ds or dy in (-1, 2):
                    p.px(x, y + dy, c, L)
        if "v" in ds:
            for dx, c in ((-1, lit), (0, shine), (1, flow), (2, dark)):
                if "h" not in ds or dx in (-1, 2):
                    p.px(x + dx, y, c, L)
    collars = [(x, y) for (x, y), ds in seen.items() if len(ds) == 2]
    if cells:
        collars.append(cells[0][:2])
    for (x, y) in collars:
        for dy in range(-2, 4):
            for dx in range(-2, 4):
                edge = dx in (-2, 3) or dy in (-2, 3)
                c = BRASS[(5 if dx + dy < 1 else 3) + k] if not edge else BRASS[(6 if dx + dy < 1 else 1) + k]
                p.px(x + dx, y + dy, c, L)


def cylinder_bar(p: Pix, bx, base, bw, v, night, elixir, L="base"):
    """A week's commits as a graduated cylinder of clear glass standing on the base line, `v` rows tall to the top
    of its lip: its flared lip, its walls lit along the left and dark along the right, a line of light running
    down the inside of the near wall, a little clear glass under the lip and the elixir filling the rest with its
    meniscus curving up at the walls, the graduation etched on the glass every third row and longer every
    twelfth, and a foot a pixel wider each side. By night the elixir is lit from within, glows on the wall round
    it and has bubbles caught in it."""
    E = RAMP[elixir]
    k = 1 if night else 0
    top, x1 = base - v, bx + bw - 1
    room = 2 if v >= 14 else 1 if v >= 8 else 0
    surf = top + 1 + room
    clear = GLASS[0] if night else GLASS[6]
    for yy in range(top, base):
        for xx in range(bx, bx + bw):
            if xx == bx:
                c = GLASS[3]
            elif xx == x1:
                c = GLASS[1]
            elif yy < surf:
                c = C["white"] if xx == bx + 1 and not night else clear
            elif yy == surf:
                c = E[5 + k] if xx in (bx + 1, x1 - 1) else E[6] if xx < x1 - 1 else E[4 + k]
            elif xx == bx + 1:
                c = E[6]
            elif xx == x1 - 1:
                c = E[2 + k]
            else:
                c = E[(4 if xx - bx < bw * 0.55 else 3) + k]
            p.px(xx, yy, c, L)
    if surf > top + 1 and bw > 4:
        p.px(bx + 1, surf - 1, E[5 + k], L)
        p.px(x1 - 1, surf - 1, E[5 + k], L)
    for i, yy in enumerate(range(base - 3, surf, -3)):
        etch = GLASS[6] if yy > surf else GLASS[3]
        for xx in range(x1 - (3 if i % 4 == 3 else 2), x1):
            if xx > bx + 1:
                p.px(xx, yy, etch, L)
    for xx in range(bx - 1, bx + bw + 1):
        p.px(xx, top, GLASS[5] if xx < bx + bw // 2 else GLASS[2], L)
        p.px(xx, base - 1, GLASS[3] if xx < bx + bw // 2 else GLASS[1], L)
    if night and bw > 4:
        for j, yy in enumerate(range(base - 5, surf + 2, -5)):
            p.px(bx + 2 + (j % 2) * max(1, bw - 6), yy, C["white"] if j % 2 else E[6], L)
        p.halo(bx + bw / 2, (surf + base) / 2, bw * 0.9 + 3, (base - surf) / 2 + 4, E[5], (0.05, 0.1), L="haze",
               shape=True)


def stopper(p: Pix, bx, base, bw, v, night, L="base"):
    """The cork stoppering the busiest week's cylinder, standing in its mouth no higher than the lip, and by night
    a glow of gold round the cylinder for the gold the week's work has made."""
    top, k = base - v, -1 if night else 0
    for yy in range(top, min(top + 3, base - 2)):
        for xx in range(bx, bx + bw):
            c = AMBER[(4 if xx < bx + bw // 2 else 3) + k]
            if yy == top + 2 or xx in (bx, bx + bw - 1):
                c = AMBER[1 + (1 if yy == top else 0)]
            elif yy == top:
                c = AMBER[5 + k]
            p.px(xx, yy, c, L)
    if night:
        p.halo(bx + bw / 2, base - v / 2, bw + 6, v / 2 + 5, GOLD[4], (0.05, 0.1, 0.15), L="haze", shape=True)


def balance(p: Pix, cx, cy, r, night):
    """The balance on an instruments sheet's dial, laid over it once its words are set: a level beam of brass
    through the pivot, a post at each end with a pan on it, lead weights in the one and a nugget of gold in the
    other, and the hand the layout drew restyled as the balance's pointer, a needle of brass with a dark tip;
    each piece only where no word comes near it."""
    k = -1 if night else 0
    hand = [(x, y) for (x, y), c in p.layers["base"].items()
            if c == p.hand_ink and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= (r - 10) ** 2]
    x0, y0 = round(cx), round(cy)
    reach = max(8, min(14, round(r * 0.36)))
    for x in range(x0 - reach, x0 + reach + 1):
        if p.clear_of_words(x - 1, y0 - 1, x + 2, y0 + 5):
            p.px(x, y0 + 1, BRASS[5 + k])
            p.px(x, y0 + 2, BRASS[2 + k])
    for side, load in ((-1, "lead"), (1, "gold")):
        px_ = x0 + side * (reach - 2)
        if not p.clear_of_words(px_ - 5, y0 - 8, px_ + 6, y0 + 3):
            continue
        p.px(px_, y0, BRASS[3 + k])
        p.px(px_, y0 - 1, BRASS[3 + k])
        p.hline(px_ - 3, px_ + 4, y0 - 2, BRASS[4 + k])
        p.px(px_ - 3, y0 - 3, BRASS[6 + k])
        p.px(px_ + 3, y0 - 3, BRASS[3 + k])
        if load == "lead":
            for (dx, dy, c) in ((-2, -3, LEAD[4]), (-1, -3, LEAD[3]), (1, -3, LEAD[4]), (2, -3, LEAD[2]),
                                (-1, -4, LEAD[5]), (1, -4, LEAD[3])):
                p.px(px_ + dx, y0 + dy, c)
        else:
            for (dx, dy, c) in ((-1, -3, GOLD[4]), (0, -3, GOLD[3]), (1, -3, GOLD[2]), (-1, -4, GOLD[6]),
                                (0, -4, GOLD[5]), (0, -5, GOLD[5])):
                p.px(px_ + dx, y0 + dy, c)
    if hand:
        far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
        for (x, y) in hand:
            p.px(x, y, BRASS[(5 if (x + y) % 2 else 4) + k])
        p.px(far[0], far[1], OAK[0])
    sphere_hub(p, cx, cy, night)


def sphere_hub(p: Pix, cx, cy, night):
    """The balance's pivot, a knob of brass, drawn again over the beam."""
    sphere(p, cx + 0.5, cy - 0.5, 3.2, BRASS, lo=1, hi=6)


# The alchemical matters a file type's share is made of, by turns.
MATTERS = ("gold", "quicksilver", "cinnabar", "verdigris", "azure", "sulphur", "salt", "lead")


def matter(i: int, xx, yy, y0, y1, lift, night) -> str:
    """The colour at (xx, yy) of the `i`-th matter's share of the ribbon: gold with its sheen, quicksilver
    running bright and dark, cinnabar's red crystals, verdigris, azure, sulphur's yellow grains, white salt and
    dull lead; `lift` lights its top row and shades its foot."""
    kind = MATTERS[i % len(MATTERS)]
    u = yy - y0
    if kind == "gold":
        c = GOLD[6] if (xx - u) % 9 == 0 else GOLD[4]
    elif kind == "quicksilver":
        c = ASH[6] if (xx + u * 3) % 13 < 2 else ASH[4] if (xx // 4 + u) % 3 else ASH[3]
    elif kind == "cinnabar":
        c = RED[4] if (xx * 5 + u * 7) % 11 < 3 else RED[3]
    elif kind == "verdigris":
        c = GREEN[5] if (xx * 3 + u * 5) % 7 == 0 else GREEN[4]
    elif kind == "azure":
        c = BLUE[5] if (xx * 7 + u) % 9 == 0 else BLUE[4]
    elif kind == "sulphur":
        c = AMBER[5] if (xx + u) % 4 == 0 else GOLD[4] if (xx * 3 + u) % 5 else AMBER[4]
    elif kind == "salt":
        c = BONE[6] if (xx + u * 2) % 5 else BONE[4]
    else:
        c = LEAD[4] if (xx * 3 + u * 5) % 9 else LEAD[3]
    return step(c, lift)


def jar_cell(q: Pix, ox, oy, night):
    """An apothecary jar 11 by 15 a counter's digit is written on: a glazed jar with its lid and knob, and a
    paper label pasted on its front, framed in a printed rule, for the numeral."""
    k = -1 if night else 0
    J = BLUE
    for yy in range(15):
        for xx in range(11):
            if yy == 0:
                c = J[4 + k] if 3 <= xx <= 7 else None
            elif yy == 1:
                c = J[2 + k] if 1 <= xx <= 9 else None
            elif yy == 2:
                c = J[5 + k] if xx < 6 else J[3 + k]
            elif yy == 14:
                c = J[1] if 1 <= xx <= 9 else None
            elif 4 <= yy <= 12 and 2 <= xx <= 8:
                edge = yy in (4, 12) or xx in (2, 8)
                c = BONE[3 + k] if edge else BONE[6 + k]
            else:
                c = J[(5 if xx == 0 else 1 if xx == 10 else 4 if xx < 5 else 3) + k]
            if c:
                q.px(ox + xx, oy + yy, c)
    q.px(ox + 5, oy, J[6 + k])


def glass_tube(p: Pix, x0, x1, y, night, elixir="violet", L="base"):
    """The glass distillation tube the releases hang from, from x0 to x1 along row y + 1: its lit edge, the
    elixir running in it, its dark edge, and a collar of brass every so often."""
    E = RAMP[elixir]
    k = -1 if night else 0
    for x in range(x0, x1):
        p.px(x, y, GLASS[4 + k], L)
        p.px(x, y + 1, E[(5 if (x - x0) % 9 == 3 else 4) + (1 if night else 0)], L)
        p.px(x, y + 2, GLASS[1], L)
    for x in range(x0 + 20, x1 - 6, 44):
        for dy in range(-1, 4):
            p.px(x, y + dy, BRASS[5 + k] if dy < 1 else BRASS[3 + k], L)
            p.px(x + 1, y + dy, BRASS[2 + k], L)


def hanging_flask(p: Pix, x, gy, kind, night, i=0, L="base"):
    """A flask hung from the distillation tube at x for a release: a round flask of an elixir, bigger and of gold
    for a big release, a small phial for a patch, an empty flask of bare glass for one still to come, and for
    the repository's founding a cucurbit on its little stand."""
    k = -1 if night else 0
    if kind == "made":
        for yy in range(gy + 3, gy + 9):
            hw = 1 if yy < gy + 5 else 2
            for xx in range(x - hw, x + hw + 1):
                p.px(xx, yy, CLAY[(4 if xx < x else 2) + k], L)
        p.hline(x - 3, x + 4, gy + 9, IRON[4 + k], L)
        p.px(x - 3, gy + 10, IRON[2 + k], L)
        p.px(x + 3, gy + 10, IRON[2 + k], L)
        return
    p.px(x, gy + 3, GLASS[3], L)
    if kind == "minor":
        cells = flask_cells(x + 0.5, gy + 9, 2, 1, ELIXIRS[i % len(ELIXIRS)], night, level=0.6)
    elif kind == "next":
        cells = flask_cells(x + 0.5, gy + 11, 3, 1, "violet", night, level=0.0)
        cells = {q: c for q, c in cells.items() if c in (GLASS[3], GLASS[1])}
    elif kind == "big":
        cells = flask_cells(x + 0.5, gy + 13, 4, 1, "amber", night, level=0.65)
        cells = {q: (GOLD[5] if c in AMBER[4:] else GOLD[4] if c in AMBER else c) for q, c in cells.items()}
    else:
        cells = flask_cells(x + 0.5, gy + 11, 3, 1, ELIXIRS[i % len(ELIXIRS)], night, level=0.55)
    for (xx, yy), c in cells.items():
        p.px(xx, yy, c, L)


# The squat flask bubbling on the tube at today, 7 by 5, low enough to keep under the names above the tube: `o O`
# its glass, `l L d` its green elixir, `b` the bubbles in it.
TODAY = ["..oOO..", "..obO..", ".olblO.", "oLLbLdO", ".oLLdO."]


def today_flask(p: Pix, x, gy, night, L="base"):
    """The flask bubbling at today's end of the tube, sitting on it at column x with its foot on the row above
    the tube's row gy: green elixir with its bubbles, glowing by night."""
    k = 1 if night else 0
    sprite(p, x - 3, gy - len(TODAY), TODAY, {"o": GLASS[3], "O": GLASS[1], "l": GREEN[5 + k], "L": GREEN[4 + k],
                                               "d": GREEN[2 + k], "b": GREEN[6] if night else C["white"]}, L)
    if night:
        p.halo(x + 0.5, gy - 3, 7, 6, GREEN[5], (0.08, 0.16), L="haze", shape=True)


# --------------------------------------------------------------------------- the alchemists of the roster
# Their caps, each 17 wide and drawn down to the brow: a tall cone with a gold sign on it, a soft beret with its
# button, a coif, and a turban with its jewel; and a hood, which falls about the face to the shoulders and is
# drawn behind it. `k c C` the cloth, dark to lit, `g` a band of gold and `Y` a sign or a jewel.
CAPS = {
    "cone": ["........k........", ".......kCk.......", "......kCck.......", ".....kCccck......", "....kCcYcck......",
             "...kCccccccck....", ".ggggggggggggggg.", "................."],
    "beret": [".................", ".................", "........Y........", "...kkkkkkkkkkk...", ".kCCCccccccccck..",
              "kCcccccccccccccck", ".kkkkkkkkkkkkkkk.", "................."],
    "coif": [".................", ".................", ".................", ".....kkkkkkk.....", "....kCcccccck....",
             "...kCcccccccck...", "...kccccccccck...", "................."],
    "turban": [".................", ".................", "......kkkkk......", "....kCcYcccck....", "...kCcccccccck...",
               "..kCcCcccCccccck.", "..kkkkkkkkkkkkkk.", "................."],
}
HOOD = [".................", "......kkkkk......", "....kCCcccckk....", "...kCcccccccck...", "..kCc.......cck..",
        "..kC.........ck..", "..kC.........ck..", "..kC.........ck..", "..kC.........ck..", "..kC.........ck..",
        "..kc.........ck..", ".kCc.........cck.", ".kCc.........cck.", ".kcc.........cck.", "kCcc.........ccck",
        "kCcc.........ccck"]
# The face, front on: `h` hair at its sides, `b` the brows, `e` the eyes, `w` their lights, `n` the nose's shade.
FACE = [".....hfffffh.....", "....hfffffffh....", "....fbbfffbbf....", "....fewfffwef....", "....ffffnffff....",
        "....ffffffff.....", ".....fffffff.....", "......fffff......"]
# The beards from the moustache down: long and pointed, forked, short and clean-shaven but for a moustache.
BEARDS = {
    "long": ["....bbbfffbbb....", "....bbbbbbbbb....", "....bbbbbbbbb....", ".....bbbbbbb.....", ".....bbbbbbb.....",
             "......bbbbb......", ".......bbb.......", "........b........"],
    "forked": ["....bbbfffbbb....", "....bbbbbbbbb....", ".....bbbbbbb.....", ".....bbb.bbb.....", "......bb.bb......",
               "......b...b......"],
    "short": ["....bbbfffbbb....", "....bbbbbbbbb....", ".....bbbbbbb.....", "......bbbbb......"],
    "none": [".....bbbbbbb....."],
}
# The robe's shoulders under the beard, its collar of fur and the gold trim down its front.
ROBE = [".....uuuuuuu.....", "..rruuUUUUUuurr..", ".rRRrrrrgrrrrrqq.", "rRRrrrrrgrrrrrrqq", "rRrrrrrrgrrrrrrqq"]
ROBES = ("red", "blue", "green", "violet", "amber")
HAIRS = (("ash", 6), ("ash", 4), ("oak", 4), ("oak", 1), ("red", 2), ("ash", 2))
SHAPES = ("cone", "beret", "hood", "coif", "turban")
# The skins of the roster's alchemists, the hand's three: the darkest, the middle and the lightest. A face keeps
# its skin's own tones by day and by night, as no light of the laboratory falls on a roster to lift it again.
SKINS = ("skin2", "skin1", "skin")


def alchemist_head(p: Pix, cx, cy, person: dict, i: int, night, L="base"):
    """A contributor as an alchemist seen head and shoulders, 17 by 21 round (cx, cy), in robe and cap: the cap's
    shape and its cloth, the robe's colour, the beard's cut, the hair's colour, his skin (one of the hand's three,
    see `SKINS`) and whether he wears spectacles all drawn from his name, so each keeps his own looks from one page
    to the next and none is lettered."""
    k = -1 if night else 0
    n = seed_of(person.get("name", "") or str(i)) + i * 7
    cap = SHAPES[n % len(SHAPES)]
    robe = RAMP[ROBES[(n // 5) % len(ROBES)]]
    cloth = RAMP[ROBES[(n // 25 + 2) % len(ROBES)]]
    beard = tuple(BEARDS)[(n // 125) % len(BEARDS)]
    hr, ht = HAIRS[(n // 500) % len(HAIRS)]
    skin = RAMP[SKINS[(n // 3000) % len(SKINS)]]
    specs = (n // 9000) % 3 == 0
    H = RAMP[hr]
    hair = H[min(6, max(0, ht + k))]
    pal = {"k": cloth[1 + k], "c": cloth[3 + k], "C": cloth[5 + k], "Y": GOLD[5 + k], "g": GOLD[4 + k],
           "f": skin[3], "n": skin[2], "e": OAK[0], "w": BONE[6 + k], "h": hair, "b": hair,
           "r": robe[3 + k], "R": robe[5 + k], "q": robe[1 + k], "u": BONE[5 + k], "U": BONE[3 + k]}
    x0, y0 = cx - 8, cy - 10
    sprite(p, x0, y0 + 16, ROBE, pal, L)
    if cap == "hood":
        sprite(p, x0, y0, HOOD, pal, L)
    sprite(p, x0, y0 + 6, FACE, pal, L)
    sprite(p, x0, y0 + 11, BEARDS[beard], pal, L)
    if cap != "hood":
        sprite(p, x0, y0, CAPS[cap], pal, L)
    if specs:
        for dx in (3, 5, 6, 7, 8, 9, 11):
            if dx not in (5, 9):
                p.px(x0 + dx + 0, y0 + 9, BRASS[4 + k], L)
        p.px(x0 + 7, y0 + 8, BRASS[3 + k], L)


# The homunculus, 7 by 9: a little man curled in his flask, his head, his eye, his arms about his knees.
HOMUNCULUS = ["..fff..", ".fefff.", ".fffff.", "..fff..", ".fFfFf.", "fFfffFf", "ffFfFff", ".ff.ff.", ".F...F."]


def homunculus(p: Pix, cx, cy, night, L="base"):
    """A bot of the roster as a homunculus in its flask: a little man on the hand's lightest skin, curled in a
    round flask of green elixir, stoppered with cork, glowing by night."""
    cells = flask_cells(cx + 0.5, cy + 10, 7, 3, "green", night, level=0.9)
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    k = -1 if night else 0
    p.hline(cx - 2, cx + 3, cy - 8, AMBER[3 + k], L)
    p.hline(cx - 1, cx + 2, cy - 7, AMBER[2 + k], L)
    sprite(p, cx - 3, cy - 1, HOMUNCULUS, {"f": SKIN[3], "F": SKIN[2], "e": OAK[0]}, L)
    if night:
        p.halo(cx + 0.5, cy + 3, 9, 9, GREEN[5], (0.06, 0.12), L="haze")


# --------------------------------------------------------------------------- the seal: the ouroboros
# The ouroboros's head, 12 by 9, facing right at the top of its ring: its brow and gold eye, its upper jaw with its
# teeth, its gape with its own tail's tip in it, and its lower jaw. `r R` its wax, `q` the dark of its mouth.
SERPENT_HEAD = ["...rrrr.....", "..rRRRRrr...", ".rRRReRRrr..", "rRRRRRRRRrrr", "rRRRRRRqwqwq", "rrRRRRRq....",
                "rrrRRRRqwqwq", ".rrrrrrrrrr.", "..rrrrrrr..."]


def ouroboros(p: Pix, cx, cy, r0, r1, night):
    """The ouroboros round the certificate's seal, from r0 to r1, pressed in red wax: the wax spread round it in
    an uneven rim, darker, and the serpent coiled in a ring standing out of it, scaled in a fine diamond, lit
    along its upper left and dark along its lower right, thickening from its tail to its neck, and its head
    at the top of the ring with its gold eye and its jaws closed on its own tail's tip."""
    k = -1 if night else 0
    mid = (r0 + r1) / 2
    rnd = random.Random(5)
    lumps = [rnd.uniform(-0.8, 0.8) for _ in range(24)]
    for yy in range(math.floor(cy - r1) - 3, math.ceil(cy + r1) + 4):
        for xx in range(math.floor(cx - r1) - 3, math.ceil(cx + r1) + 4):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            a = math.degrees(math.atan2(dy, dx)) % 360
            edge = r1 + 1.6 + lumps[int(a / 15)]
            if rho > edge or rho < r0 - 0.6:
                continue
            facing = (dx * -0.6 + dy * -0.8) / max(0.5, rho)
            t = ((a - 280) % 360) / 360
            half = 1.4 + 2.4 * t
            if abs(rho - mid) <= half:
                off = (rho - mid) / half
                tone = 4 if off < -0.4 else 3 if off < 0.45 else 2
                tone += 1 if facing > 0.4 else -1 if facing < -0.5 else 0
                if (round(a / 7) + round((rho - mid) * 1.4)) % 2 and abs(off) < 0.7:
                    tone -= 1
            else:
                tone = 1 if facing < 0.3 else 2
            p.px(xx, yy, RED[max(0, min(6, tone + k))])
    hx = round(cx + mid * math.cos(math.radians(264))) - 6
    hy = round(cy + mid * math.sin(math.radians(264))) - 4
    sprite(p, hx, hy, SERPENT_HEAD, {"r": RED[3 + k], "R": RED[5 + k], "q": RED[0], "e": GOLD[5],
                                     "w": BONE[6 + k]})


def door(p: Pix, night):
    """A placard as a cabinet door over the whole card: a frame of dark oak round a panel of limed oak with its
    grain running down it, bound in brass at its corners, hung on two brass hinges at its left and fitted with a
    brass escutcheon at its right."""
    w, h = p.w, p.h
    k = -1 if night else 0
    W = wall(night)
    p.under.append(f'<rect width="{w}" height="{h}" fill="{W[5] if not night else W[1]}"/>')
    grain = {}
    for x in range(6, w - 6):
        for y in range(6, h - 6):
            if (x * 7) % 23 == 0 and (y + x) % 13 < 9 or (x * 11) % 31 == 0 and (y * 3 + x) % 17 < 12:
                grain[(x, y)] = W[4] if not night else W[2]
    for (x, y), c in grain.items():
        p.px(x, y, c)
    for x in range(w):
        for y in list(range(5)) + list(range(h - 5, h)):
            j = y if y < 5 else y - (h - 5)
            p.px(x, y, OAK[(5 if j == 0 else 0 if j == 4 else 3 if (x * 3) % 17 < 12 else 2) + k])
    for y in range(5, h - 5):
        for x in list(range(5)) + list(range(w - 5, w)):
            j = x if x < 5 else x - (w - 5)
            p.px(x, y, OAK[(5 if j == 0 else 0 if j == 4 else 3 if (y * 5) % 19 < 13 else 2) + k])
    for x in range(5, w - 5):
        p.apx(x, 5, X["shade_ink"], 0.3)
    for y in range(6, h - 5):
        p.apx(5, y, X["shade_ink"], 0.22)
    B = BRASS
    for (cx_, cy_, fx, fy) in ((1, 1, 1, 1), (w - 2, 1, -1, 1), (1, h - 2, 1, -1), (w - 2, h - 2, -1, -1)):
        for i in range(6):
            p.px(cx_ + fx * i, cy_, B[(5 if i < 3 else 4) + k])
            p.px(cx_, cy_ + fy * i, B[(5 if i < 3 else 4) + k])
        p.px(cx_ + fx, cy_ + fy, B[1])
    for hy in (14, h - 18):
        for i in range(9):
            p.px(i, hy, B[5 + k])
            p.px(i, hy + 1, B[3 + k])
            p.px(i, hy + 2, B[1])
        p.px(2, hy + 1, B[0])
        p.px(6, hy + 1, B[0])
    ex, ey = w - 4, h // 2 - 4
    for j in range(8):
        p.px(ex - 1, ey + j, B[5 + k])
        p.px(ex, ey + j, B[4 + k] if j not in (3, 4, 5) else OAK[0])
        p.px(ex + 1, ey + j, B[2 + k])


# --------------------------------------------------------------------------- small pieces
def silk(p: Pix, x, y, w, h, night, L="base"):
    """The ribbon under the seal: green silk, lit along its top and shaded along its foot, its ends falling a row
    either side of the block and cut in a fork, as long as its column leaves them room."""
    G = GREEN
    p.rect(x, y, w, h, G[5], L)
    p.hline(x, x + w, y, G[6], L)
    p.hline(x, x + w, y + h - 1, G[3], L)
    tail = min(4, x - 6, (100 if p.w == 415 else 88) - 2 - (x + w))
    for i in range(max(0, tail)):
        drop = 1 if i >= 2 else 0
        for j in range(h):
            if i == tail - 1 and j == h // 2:
                continue
            c = G[3] if i == 0 else G[6] if j == 0 else G[3] if j == h - 1 else G[4]
            p.px(x - 1 - i, y + j + drop, c, L)
            p.px(x + w + i, y + j + drop, c, L)


def shelf_lip(p: Pix, x0, x1, y, night, L="base"):
    """The lip of a shelf along a sheet's rule under its tag: a row of oak lit along its top, left out where a
    word comes near."""
    k = -1 if night else 0
    for x in range(x0, x1):
        if p.clear_of_words(x - 1, y - 2, x + 2, y + 1):
            p.px(x, y - 1, OAK[5 + k] if (x % 13) not in (4, 5) else OAK[4 + k], L)


def heart(p: Pix, x, y, L="base"):
    """A heart of red glass, 7 by 6, a glint on its upper-left lobe and its glass dark along its lower right."""
    art = [".rr.rr.", "rwrrrrR", "rrrrrRR", ".rrrRR.", "..rRR..", "...R..."]
    sprite(p, x, y, art, {"r": RED[4], "R": RED[2], "w": RED[6]}, L)


def scale_bar(p: Pix, x0, y0, w, h, period=5, night=False, L="base"):
    """A graphic scale's bar in lead and gold by turns, as if the work had begun on it: the lead dull grey with
    its top a shade lighter, the gold bright with its top lit and its foot dark."""
    for xx in range(x0, x0 + w):
        gold = ((xx - x0) // period) % 2 == 1
        for yy in range(y0, y0 + h):
            j = yy - y0
            if gold:
                c = GOLD[6] if j == 0 else GOLD[2] if j == h - 1 else GOLD[4]
            else:
                c = LEAD[5] if j == 0 else LEAD[1] if j == h - 1 else LEAD[3]
            p.px(xx, yy, c, L)


def link_icon(index, night, ink):
    """The icon of the `index`-th link and its palette: a round flask, an hourglass, the sign for gold and a book,
    in the button's ink with their elixir and their gold."""
    k = -1 if night else 0
    art = ICONS[LINK_ICONS[index % len(LINK_ICONS)]]
    return art, {"#": ink, "e": GREEN[3 + k], "g": GOLD[3 + k]}


def glint_mark(p: Pix, x, y, night, L="base"):
    """A four-pointed glint of gold, 5 by 5, its heart white."""
    for (dx, dy, c) in ((2, 2, C["white"]), (1, 2, GOLD[5]), (3, 2, GOLD[5]), (2, 1, GOLD[5]), (2, 3, GOLD[5]),
                        (0, 2, GOLD[3]), (4, 2, GOLD[3]), (2, 0, GOLD[3]), (2, 4, GOLD[3])):
        p.px(x + dx, y + dy, c, L)
