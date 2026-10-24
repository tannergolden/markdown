# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Choice set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is the damask wallpaper of an old hotel room on a stormy night, dusty rose by day and wine-black by
night, its medallions woven in a sheen a tone off the ground, held in a frame of oxblood chesterfield leather: a
padded roll down each side and along the foot, close-studded with brass nails, and across a header's top a deep-
buttoned panel of tufted leather that parts either side of the month's mark. Titles are glossy gel capsules of candy
red, a white streak of light along each stroke's upper left and a darker underside, casting their shadow on the
paper; by night the streak is the green of the room's one lamp. Headers open on the room: a red leather wingback
chair studded with brass on a Persian runner under a cracked mirror, whose glass the code falls through by night, a
round table beside it with a glass of water and a banker's lamp whose green glass burns by night and rims the chair;
across the room a tall window streaming with rain under a velvet pelmet between curtains of green velvet, the storm
grey outside it by day and by night the city's lit towers under a sky that lightning splits, each stroke lighting the
whole room above the words for its instant, and before it a little table with an open box and the two pills, one red
and one blue; and on the floor under the words a suitcase and an umbrella dripping in its stand. A section's header
has the fireside: a carved mahogany fireplace whose fire burns green by night, its candles lit on the mantel, a pier
mirror over it showing the window across the room, and a club chair either side facing the other across a low table
with the glass of water and the pills. A strip's has the cheval glass, the red chair facing it and caught in it, its
face going to liquid in rings. The marks beside the titles are the two pills and round dark glasses with the pills
caught in them, and the Persian runner lies along a rule. Footers stand on a mahogany skirting with the box of pills
and the banker's lamp on it, and the elements are built of nailed leather, brass, the title's gel, mahogany and
velvet tassels on a brass rod. Everything is shaded from the one light in the upper left on the set's own ramps, and
every light is the hand's phosphor."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, LZ, Pix, fold, measure, num, sphere, tube
from .. import rain
from .palette import C, NIGHT_SKY, RAMP, X

ROSE, WINE, OX, BRASS = RAMP["rose"], RAMP["wine"], RAMP["oxblood"], RAMP["brass"]
CANDY, BLUE, WOOD, GLASS = RAMP["candy"], RAMP["blue"], RAMP["mahogany"], RAMP["glass"]
STORM, NIGHT, VELVET, SATIN, FLAME = RAMP["storm"], RAMP["night"], RAMP["velvet"], RAMP["satin"], RAMP["flame"]
EDGE = 4          # the leather roll's width down each side and along the foot
BAND = 14         # the rows the tufted panel takes across a header's top, its studs and its edges


def fills(cells: dict) -> str:
    """Filled paths for {(x, y): colour}, a row's run at a time: the shapes a pattern's tile is drawn in, since a
    browser paints thin strokes inside a pattern poorly when the file asks for crisp edges."""
    by: dict = {}
    for xy, c in cells.items():
        by.setdefault(c, set()).add(xy)
    return "".join(f'<path fill="{c}" d="{Pix.area(cs)}"/>' for c, cs in sorted(by.items()))


def light(nx: float, ny: float, nz: float) -> float:
    """How much of the one lamp a surface facing (nx, ny, nz) takes, 0 to 1."""
    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return max(0.0, (nx * LX + ny * LY + nz * LZ) / n)


def pillow(p: Pix, cells, ramp, lo=1, hi=5, r=2.5, L="base", outline=True):
    """A padded shape shaded as a cushion lit from the upper left: each cell's slope read from how near it lies to
    the shape's edge on each side, its tone stepped down the ramp from `hi` where it faces the light to `lo` where
    it turns away, and an outline round it in the ramp's darkest tone."""
    cells = set(cells)

    def reach(x, y, dx, dy):
        n = 0
        while n <= r and (x + dx * (n + 1), y + dy * (n + 1)) in cells:
            n += 1
        return n
    for (x, y) in cells:
        dl, dr, du, dd = reach(x, y, -1, 0), reach(x, y, 1, 0), reach(x, y, 0, -1), reach(x, y, 0, 1)
        nx = -(r - dl) / r if dl < r and dl <= dr else (r - dr) / r if dr < r else 0.0
        ny = -(r - du) / r if du < r and du <= dd else (r - dd) / r if dd < r else 0.0
        nz = math.sqrt(max(0.08, 1 - min(1.0, nx * nx + ny * ny)))
        t = round(lo + (hi - lo) * min(1.0, light(nx, ny, nz) / 0.85))
        p.px(x, y, ramp[max(lo, min(hi, t))], L)
    if outline:
        for (x, y) in cells:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in cells:
                    p.px(x + dx, y + dy, ramp[0], L)


def ellipse(cx, cy, rx, ry) -> set:
    """The cells inside an ellipse centred on (cx, cy)."""
    out = set()
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                out.add((x, y))
    return out


def rounded(x0, y0, x1, y1, r=1.5, top=True, bottom=True) -> set:
    """The cells of a box from (x0, y0) to (x1, y1), ends excluded, its top and foot corners rounded to `r`."""
    out = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            ex = max(x0 + r - (x + 0.5), (x + 0.5) - (x1 - r), 0)
            ey = max((y0 + r - (y + 0.5)) if top else 0, ((y + 0.5) - (y1 - r)) if bottom else 0, 0)
            if ex > 0 and ey > 0 and ex * ex + ey * ey > r * r:
                continue
            out.add((x, y))
    return out


# --------------------------------------------------------------------------- the wallpaper
# A medallion of the damask, 21 by 28, woven in the paper's sheen: a bud over a palmette in its ogee of scrolls, and
# a vase of leaves under it, mirrored about its middle column.
DAMASK = [
    "..........#..........",
    ".........###.........",
    "..........#..........",
    "........#.#.#........",
    ".......##.#.##.......",
    "......#..###..#......",
    ".....#..#####..#.....",
    "..##...#.###.#...##..",
    ".#..#..#..#..#..#..#.",
    ".#...#.#.###.#.#...#.",
    "..#...##.###.##...#..",
    "...##..#######..##...",
    ".....#..#####..#.....",
    "....#.#..###..#.#....",
    "...#..##..#..##..#...",
    "..#..#..#.#.#..#..#..",
    "..#.#..#.###.#..#.#..",
    "...#..#.#####.#..#...",
    "......#.#####.#......",
    ".....#...###...#.....",
    "....#..#..#..#..#....",
    "...#..#...#...#..#...",
    "...#.#...###...#.#...",
    "....#...#####...#....",
    ".........###.........",
    "......#...#...#......",
    ".......###.###.......",
    "..........#..........",
]
TILE_W, TILE_H = 34, 44     # the damask's repeat, a medallion at its middle and a quarter at each corner


def _damask(uid: str, night: bool, lite: bool = False) -> str:
    """The wallpaper's patterns: a medallion and the small sprigs beside it drawn once, woven in a sheen a tone
    lighter than the ground, and laid in two patterns TILE_W by TILE_H, the second dropped half a tile across and
    half a tile down, so the medallions stand in half-drop as a damask's do. A drawing made lighter weaves only the
    medallion's heart, a lozenge, among the sprigs."""
    sheen = WINE[3] if night else ROSE[6]
    cells = {}
    mw, mh = len(DAMASK[0]), len(DAMASK)
    for j, row in enumerate(DAMASK):
        for i, ch in enumerate(row):
            if ch == "#" and (not lite or abs(i - mw // 2) + abs(j - 12) <= 3):
                cells[(i - mw // 2 + TILE_W // 2, j - mh // 2 + TILE_H // 2)] = sheen
    for dx, dy in ((0, -2), (0, -1), (-1, 0), (1, 0), (0, 0), (0, 1), (-2, 0), (2, 0)):
        cells[(dx, TILE_H // 2 + dy)] = sheen
        cells[(TILE_W + dx, TILE_H // 2 + dy)] = sheen
    body = f'<path id="{uid}m" fill="{sheen}" d="{Pix.area(set(cells))}"/>'
    return (f'<pattern id="{uid}d" width="{TILE_W}" height="{TILE_H}" patternUnits="userSpaceOnUse">{body}</pattern>'
            f'<pattern id="{uid}e" x="{TILE_W // 2}" y="{TILE_H // 2}" width="{TILE_W}" height="{TILE_H}" '
            f'patternUnits="userSpaceOnUse"><use href="#{uid}m"/></pattern>')


def band_edges(h: int) -> list:
    """The rows the night's bands change at, down a sheet `h` tall."""
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the hotel room's damask wallpaper, dusty rose by day and wine-black by night,
    darkest under the ceiling and along the floor, its medallions thinned to their hearts on a drawing made lighter.
    The drawing keeps which sheet it is and whether it is night."""
    p.sheet, p.night = uid, night
    w, h = p.w, p.h
    if night:
        edges = band_edges(h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                at = f' y="{edges[i]}"' if edges[i] else ""
                p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
    p.defs.append(_damask(uid, night, p.lite))
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}d)"/><rect width="{w}" height="{h}" '
                   f'fill="url(#{uid}e)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the wallpaper's ground, or the night's band of it there."""
    if not night:
        return C["paper"]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


# --------------------------------------------------------------------------- the frame: the chesterfield
def _studs(uid: str, along: bool, night: bool) -> str:
    """A run of brass nails, a nail every four units, as a pattern: each nail's head lit at its upper left and
    shaded at its lower right, on the leather between them."""
    k = -1 if night else 0
    face = OX[3 + k]
    cells = {}
    w, h = (4, 2) if along else (2, 4)
    for y in range(h):
        for x in range(w):
            cells[(x, y)] = face
    head = {(0, 0): BRASS[6 + k], (1, 0): BRASS[4 + k], (0, 1): BRASS[3 + k], (1, 1): BRASS[1]}
    cells.update(head)
    return f'<pattern id="{uid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{fills(cells)}</pattern>'


def frame(p: Pix, night: bool, top: int = 0):
    """The border: a padded roll of oxblood leather down each side and along the foot, its face to the room lit
    and its far side in shade, close-studded with brass nails along its middle, and the shadow it casts on the
    wallpaper inside it. The sides start at row `top`, under the tufted panel of a header (see `band`)."""
    w, h = p.w, p.h
    k = -1 if night else 0
    sh = p.shapes["base"]
    cols_left = (OX[0], OX[5 + k], OX[3 + k], OX[1])
    cols_right = (OX[4 + k], OX[3 + k], OX[1], OX[0])
    rows_foot = (OX[4 + k], OX[3 + k], OX[1], OX[0])
    for i, c in enumerate(cols_left):
        sh.append(f'<rect x="{i}" y="{top}" width="1" height="{h - top}" fill="{c}"/>')
    for i, c in enumerate(cols_right):
        sh.append(f'<rect x="{w - EDGE + i}" y="{top}" width="1" height="{h - top}" fill="{c}"/>')
    for i, c in enumerate(rows_foot):
        sh.append(f'<rect x="{EDGE}" y="{h - EDGE + i}" width="{w - 2 * EDGE}" height="1" fill="{c}"/>')
    uid = getattr(p, "sheet", "p")
    p.defs.append(_studs(f"{uid}sv", False, night))
    p.defs.append(_studs(f"{uid}sh", True, night))
    sh.append(f'<rect x="1" y="{top + 1}" width="2" height="{h - top - EDGE - 1}" fill="url(#{uid}sv)"/>')
    sh.append(f'<rect x="{w - 3}" y="{top + 1}" width="2" height="{h - top - EDGE - 1}" fill="url(#{uid}sv)"/>')
    sh.append(f'<rect x="{EDGE + 1}" y="{h - 3}" width="{w - 2 * EDGE - 2}" height="2" fill="url(#{uid}sh)"/>')
    # The roll's shadow on the wallpaper inside it, and a brass cap on each lower corner.
    sh.append(f'<rect x="{EDGE}" y="{top}" width="1" height="{h - top - EDGE}" fill="{X["shade"]}" '
              f'fill-opacity="{".35" if not night else ".5"}"/>')
    for cx in (1, w - 3):
        p.rect(cx - 1, h - EDGE, 4, EDGE, OX[0])
        p.rect(cx, h - 3, 2, 2, BRASS[4 + k])
        p.px(cx, h - 3, BRASS[6 + k])
        p.px(cx + 1, h - 2, BRASS[1])


def _tufts(uid: str, night: bool) -> str:
    """The tufted leather as a pattern tile 12 by 8: diamond puffs of leather between buttons set on a diamond
    lattice, each puff shaded as a pillow lit from the upper left, deep folds along its four edges, and each button
    a dimple of dark leather under a brass cap that catches the light."""
    k = -1 if night else 0
    W, H = 12, 8
    hw, hh = W / 2, H / 2
    cells = {}
    for y in range(H):
        for x in range(W):
            px_, py_ = x + 0.5, y + 0.5
            d, cx, cy = min((abs(px_ - cx) / hw + abs(py_ - cy) / hh, cx, cy)
                            for cx, cy in ((hw, 0), (hw, H), (0, hh), (W, hh)))
            u, v = (px_ - cx) / hw, (py_ - cy) / hh
            z = max(0.0, 1 - d) ** 0.6
            t = 1 + round(4.6 * light(u * 1.4, v * 1.4, 1.0) * (0.55 + 0.45 * z))
            if d > 0.86:
                t = 1 if d < 0.97 else 0
            cells[(x, y)] = OX[max(0, min(6, t + k))]
    for bx, by in ((0, 0), (W // 2, H // 2)):
        cells[(bx % W, by % H)] = OX[0]
        cells[((bx - 1) % W, by % H)] = OX[1]
        cells[(bx % W, (by - 1) % H)] = OX[1]
        cells[((bx - 1) % W, (by - 1) % H)] = BRASS[5 + k]
    return f'<pattern id="{uid}" y="-2" width="{W}" height="{H}" patternUnits="userSpaceOnUse">{fills(cells)}</pattern>'


def band(p: Pix, night: bool, gap=None):
    """The deep-buttoned panel of oxblood leather across a header's top: a roll along its upper edge, a row of
    tufted puffs between their buttons, a welt and a line of brass nails along its foot, and its shadow on the
    wallpaper under it. `gap` is the span (x0, x1) it parts either side of, the month's mark, each end finished with
    a stitched welt; None runs it unbroken from side to side."""
    w = p.w
    k = -1 if night else 0
    uid = getattr(p, "sheet", "p")
    p.defs.append(_tufts(f"{uid}t", night))
    runs = [(0, w)] if gap is None else [(0, gap[0]), (gap[1], w)]
    L = p.layer("band", z=-1)
    sh = p.shapes[L]
    for a, b in runs:
        n = b - a
        rows = [(0, OX[0]), (1, OX[6 + k]), (10, OX[1]), (11, OX[2 + k]), (12, OX[2 + k]), (13, OX[0])]
        sh.append(f'<rect x="{a}" y="2" width="{n}" height="8" fill="url(#{uid}t)"/>')
        for y, c in rows:
            sh.append(f'<rect x="{a}" y="{y}" width="{n}" height="1" fill="{c}"/>')
        sh.append(f'<rect x="{a}" y="11" width="{n}" height="2" fill="url(#{uid}sh)"/>')
        sh.append(f'<rect x="{a}" y="14" width="{n}" height="1" fill="{X["shade"]}" '
                  f'fill-opacity="{".3" if not night else ".5"}"/>')
        for end in ((a,) if a > 0 else ()) + ((b - 1,) if b < w else ()):
            for y in range(0, 14):
                p.px(end, y, OX[0], L)
            inner = end + 1 if end == a else end - 1
            for y in range(1, 13):
                p.px(inner, y, OX[4 + k] if end == a else OX[1], L)


# --------------------------------------------------------------------------- the title: gel capsules
def capsule_title(p: Pix, x, y, s, night, scale, L="base") -> int:
    """A title in glossy gel capsules of candy red, built from the face's own letters, each drawn once a file as one
    path and laid again and again: its shadow cast down and to the right on the paper, a rim of the gel's darkest
    tone round it, and inside the letters, through a mask of them, the gel itself, laid four times a unit apart down
    and to the right, so every stroke runs from its lit upper left edge through a white streak of light and the candy
    body to its dark underside, wherever it turns. At the smaller sizes the streak and then the body go, as the
    stroke narrows. By night the streak is the pale green of the lamp it catches, and the underside a tone lighter,
    so the stroke keeps its width against the dark. The line of letters is drawn once and every pass places it whole,
    so a long title costs little more than a short one. Returns its width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    placed, cx = [], x
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(c, r): 1 for r, cols in enumerate(glyphs[ch][1]) for c in cols}, mono=True)
        placed.append((p.syms[key], (cx - x) / scale))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    rows = max((len(glyphs[ch][1]) for ch in s if ch != " "), default=0)

    def uses(dx=0.0, dy=0.0) -> str:
        return "".join(f'<use href="#{sid}"' + (f' x="{num(gx + dx)}"' if gx + dx else "")
                       + (f' y="{num(dy)}"' if dy else "") + "/>" for sid, gx in placed)
    u = 1 / scale
    n = getattr(p, "capsules", 0)
    p.capsules = n + 1
    mid = f"{getattr(p, 'sheet', 'p')}c{n}"
    t = f'transform="translate({x} {y}) scale({scale})"'
    # The line of letters is kept once and every pass of the capsule places the whole line, so a long title costs
    # little more than a short one.
    p.defs.append(f'<g id="{mid}l">{uses()}</g>')

    def line(dx=0.0, dy=0.0) -> str:
        return f'<use href="#{mid}l"' + (f' x="{num(dx)}"' if dx else "") + (f' y="{num(dy)}"' if dy else "") + "/>"
    p.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x - 1}" y="{y - 1}" width="{w + 2}" '
                  f'height="{rows * scale + 2}"><g stroke="{C["white"]}" {t}>{line()}</g></mask>')
    under = CANDY[2] if night else CANDY[1]
    streak = FLAME[6] if night else C["white"]
    steps = ((CANDY[4], streak, CANDY[3], under) if scale >= 4 else
             (CANDY[6] if not night else FLAME[5], CANDY[3], under) if scale == 3 else (CANDY[4], under))
    off = 2 * u if scale > 2 else u
    shade = f'<g stroke="{X["shade"]}" stroke-opacity="{".22" if not night else ".6"}" {t}>{line(off, off)}</g>'
    ring = (f'<g stroke="{CANDY[0]}" {t}>' + "".join(line(dx, dy) for dx, dy in ((-u, 0), (u, 0), (0, -u), (0, u)))
            + "</g>")
    gel = "".join(f'<g stroke="{c}">{line(k * u, k * u)}</g>' for k, c in enumerate(steps))
    p.shapes[p.layer(L)].append(f'{shade}{ring}<g mask="url(#{mid})"><g {t}>{gel}</g></g>')
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    return w


# --------------------------------------------------------------------------- the chair
def wingback(p: Pix, x0, g, night):
    """A wingback armchair of red leather seen from the front, standing on the floor at row g from column x0, 34
    wide and 40 tall: its tall back deep-buttoned on a diamond lattice, folds running between the buttons, its wings
    flaring out from its shoulders and curving down onto the arms, the arms rolled into scrolls at their fronts and
    studded with brass, a fat cushion on the seat, an apron close-nailed along its foot, and four short turned legs of
    mahogany. By day the room's light falls on it from the upper left; by night it stands in the dark, the lamp's
    green on the side that faces it. Returns its span."""
    top = g - 39
    lo, hi = (0, 3) if night else (1, 5)
    back = rounded(x0 + 9, top, x0 + 25, top + 25, r=5.5, bottom=False)
    pillow(p, back, OX, lo=lo, hi=hi, r=4)
    flare = (2, 4, 5, 6, 6, 6, 6, 6, 6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3)
    for side in (0, 1):
        wing = set()
        for j, ext in enumerate(flare):
            y = top + 3 + j
            if side == 0:
                wing.update((x, y) for x in range(x0 + 9 - ext, x0 + 11))
            else:
                wing.update((x, y) for x in range(x0 + 23, x0 + 25 + ext))
        pillow(p, wing, OX, lo=lo, hi=hi - side, r=2.5)
    for j, yy in enumerate(range(top + 5, top + 22, 4)):
        for xx in range(x0 + 13 + (2 if j % 2 else 0), x0 + 22, 4):
            p.px(xx, yy, OX[0])
            p.px(xx - 1, yy - 1, OX[min(6, hi + 1)])
            if j < 4:
                p.px(xx + 1, yy + 2, OX[max(0, lo + 1)])
                p.px(xx - 1, yy + 2, OX[max(0, lo + 1)])
    for side, (ax0, ax1) in enumerate(((x0 + 1, x0 + 10), (x0 + 24, x0 + 33))):
        arm = rounded(ax0, top + 21, ax1, top + 33, r=3.5, bottom=False)
        pillow(p, arm, OX, lo=lo, hi=hi - side, r=3)
        cx = (ax0 + ax1) / 2
        sphere(p, cx, top + 24.5, 3.6, OX, lo=max(1, lo), hi=hi + 1 - side, spec=not night)
        p.px(round(cx - 0.5), top + 24, OX[0])
        p.px(round(cx - 0.5) + 1, top + 25, OX[max(0, lo + 1)])
        for yy in range(top + 29, top + 34, 2):
            p.px(round(cx - 0.5), yy, BRASS[4 if night else 5])
    cushion = rounded(x0 + 10, top + 24, x0 + 24, top + 31, r=2.5)
    pillow(p, cushion, OX, lo=lo, hi=hi + (0 if night else 1), r=2.5)
    apron = rounded(x0 + 1, top + 31, x0 + 33, top + 36, r=1)
    pillow(p, apron, OX, lo=lo, hi=hi, r=2)
    for xx in range(x0 + 2, x0 + 32, 2):
        p.px(xx, top + 35, BRASS[(3 if night else 5) - (1 if xx > x0 + 20 else 0)])
    for lx in (x0 + 3, x0 + 29):
        for y in range(top + 37, g + 1):
            fat = y == top + 38
            p.px(lx, y, WOOD[(2 if night else 4) + (1 if fat else 0)])
            p.px(lx + 1, y, WOOD[1 if night else 2])
        p.px(lx, g, BRASS[3 if night else 4])
        p.px(lx + 1, g, BRASS[1])
    return (x0, x0 + 34)


# --------------------------------------------------------------------------- the table, the lamp and the glass
def side_table(p: Pix, x0, g, night, w=18, h=19):
    """A round pedestal table of mahogany at row g from column x0: its top an oval slab lit along its rim, its
    turned stem and three splayed feet. Returns the row its top is at."""
    k = -2 if night else 0
    top = g - h
    cx = x0 + w / 2
    for (x, y) in ellipse(cx, top + 1.5, w / 2, 2.2):
        far = (x + 0.5 - cx) / (w / 2)
        t = 5 if y <= top + 1 else 3
        if far > 0.5:
            t -= 1
        p.px(x, y, WOOD[max(0, t + k)])
    p.hline(x0 + 1, x0 + w - 1, top + 3, WOOD[max(0, 2 + k)])
    p.hline(x0 + 2, x0 + w - 2, top + 4, WOOD[0])
    sx = round(cx) - 1
    for y in range(top + 5, g - 2):
        bulge = 1 if top + 8 <= y <= top + 10 else 0
        p.px(sx - bulge, y, WOOD[max(0, 5 + k)])
        p.px(sx + 1, y, WOOD[max(0, 3 + k)])
        p.px(sx + 2 + bulge, y, WOOD[1 if not night else 0])
    for dx, c in ((-5, 4), (-4, 4), (-3, 4), (-2, 3), (3, 2), (4, 2), (5, 1), (6, 1)):
        p.px(sx + dx, g - 1 if abs(dx) < 4 else g, WOOD[max(0, c + k)])
    p.hline(sx - 2, sx + 4, g - 2, WOOD[max(0, 3 + k)])
    p.px(sx - 6, g, WOOD[max(0, 3 + k)])
    p.px(sx + 7, g, WOOD[0])
    return top


def bankers_lamp(p: Pix, x, y, night, motion, clip=None):
    """A banker's lamp standing on the surface at row y from column x, 11 wide: its brass foot and stem, its pull
    chain, and its shade of green glass, which by night burns the hand's phosphor and throws its light down on the
    table, out over the wallpaper and onto the chair beside it, as far as the box `clip` (x0, y0, x1, y1) when given,
    the corner of the room the words leave it."""
    k = -2 if night else 0
    p.hline(x + 1, x + 9, y - 1, BRASS[max(0, 4 + k)])
    p.hline(x, x + 10, y, BRASS[max(0, 2 + k)])
    p.px(x, y - 1, BRASS[0])
    p.px(x + 9, y - 1, BRASS[1])
    p.vline(x + 5, y - 5, y - 1, BRASS[max(0, 5 + k)])
    p.vline(x + 6, y - 5, y - 1, BRASS[max(0, 2 + k)])
    sy = y - 6
    rows = ((sy - 3, x + 2, x + 9), (sy - 2, x + 1, x + 10), (sy - 1, x, x + 11), (sy, x, x + 11))
    if night:
        L = p.flicker(1) if motion else "base"
        tone = (FLAME[6], FLAME[5], FLAME[4], FLAME[3])
    else:
        L = "base"
        tone = (FLAME[3], FLAME[2], FLAME[2], FLAME[1])
    for i, (yy, a, b) in enumerate(rows):
        for xx in range(a, b):
            far = (xx - x) > 7
            p.px(xx, yy, tone[min(3, i + (1 if far else 0))], L)
    p.hline(x + 2, x + 9, sy - 4, FLAME[0] if not night else FLAME[2])
    p.hline(x, x + 11, sy + 1, BRASS[max(0, 4 + k)] if not night else FLAME[2], L if night else "base")
    p.px(x + 8, sy + 2, BRASS[max(0, 5 + k)])
    p.px(x + 8, sy + 3, BRASS[max(0, 3 + k)])
    if night:
        rings = "".join(f'<ellipse cx="{num(x + 5.5)}" cy="{sy + 4}" rx="{num(30 * f)}" ry="{num(22 * f)}" '
                        f'fill="{FLAME[3]}" fill-opacity="{a}"/>'
                        for f, a in ((1, ".05"), (0.67, ".05"), (0.33, ".07")))
        if clip:
            cid = f"{getattr(p, 'sheet', 'p')}lg"
            a, b, c, d = clip
            p.defs.append(f'<clipPath id="{cid}"><rect x="{a}" y="{b}" width="{c - a}" height="{d - b}"/></clipPath>')
            rings = f'<g clip-path="url(#{cid})">{rings}</g>'
        p.raw(-19, rings, rings)
        p.halo(x + 5.5, y, 9, 2.5, FLAME[4], (0.14, 0.26), L=p.flicker(1, back=True) if motion else "haze")


def water_glass(p: Pix, x, y, night):
    """A tumbler of water standing on the surface at row y from column x, 4 wide and 6 tall: clear glass lit down
    its left side, the water inside it a tone deeper with its meniscus catching the light; by night it catches the
    lamp's green."""
    if night:
        edge, lit, water, deep, rim = GLASS[3], FLAME[4], GLASS[1], GLASS[0], FLAME[5]
    else:
        edge, lit, water, deep, rim = GLASS[2], GLASS[6], GLASS[4], GLASS[3], GLASS[6]
    for yy in range(y - 6, y):
        p.px(x, yy, lit)
        p.px(x + 3, yy, edge)
        for xx in (x + 1, x + 2):
            p.px(xx, yy, (water if xx == x + 1 else deep) if yy >= y - 4 else GLASS[5 if not night else 2])
    p.hline(x + 1, x + 3, y - 4, rim)
    p.hline(x, x + 4, y - 1, edge)


# --------------------------------------------------------------------------- the mirror
def mirror_code(p: Pix, cx, cy, rx, ry, motion, seed=7):
    """The code falling through the mirror's glass by night: streams of the rain's glyphs, each led by a white-hot
    glyph with its trail fading up behind it, stepping down a glyph every 0.12 seconds, laid behind the crack and
    clipped to the glass's oval; held where its loop begins in the still twin. A drawing made lighter shortens every
    trail by two glyphs."""
    rnd = random.Random(seed)
    tones = (FLAME[6], FLAME[5], FLAME[4], FLAME[3], FLAME[3], FLAME[2], FLAME[2], FLAME[1])
    by: dict = {}
    loop = (round(2 * ry) // rain.PITCH + 4) * rain.PITCH
    x0, y0 = round(cx - rx), round(cy - ry)
    for i, gx in enumerate(range(x0 + 1, round(cx + rx) - rain.W + 1, rain.COLUMN)):
        head = rnd.randrange(loop // rain.PITCH) * rain.PITCH
        for j in range(rnd.randint(4, 6) - (2 if p.lite else 0)):     # shorter trails on a drawing made lighter
            c = tones[min(j, len(tones) - 1)]
            gy = y0 + (head - j * rain.PITCH) % loop
            sid = p.syms[rain.symbol(p, rnd.choice(rain.NAMES))]
            by.setdefault(c, []).append(f'<use href="#{sid}" x="{gx}" y="{gy}"/>')
    inner = "".join(f'<g stroke="{c}">{"".join(us)}</g>' for c, us in by.items())
    cid = "mc"
    p.defs.append(f'<clipPath id="{cid}"><ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}"/>'
                  f'</clipPath><g id="{cid}g">{inner}</g>')
    copies = f'<use href="#{cid}g"/><use href="#{cid}g" y="-{loop}"/>'
    steps = loop // rain.PITCH
    values = ";".join(f"0 {i * rain.PITCH}" for i in range(steps))
    p.raw(-0.6, f'<g clip-path="url(#{cid})"><g>{copies}<animateTransform attributeName="transform" '
                f'type="translate" values="{values}" dur="{num(steps * 0.12)}s" repeatCount="indefinite" '
                f'calcMode="discrete"/></g></g>' if motion else "", f'<g clip-path="url(#{cid})">{copies}</g>')


def mirror(p: Pix, cx, cy, night, motion, rx=14, ry=19):
    """An oval mirror in a gilt frame hung on the wallpaper by a cord from a brass hook, centred on (cx, cy),
    cracked across from a blow at its upper right; its glass catches a pale sheen by day, and by night the code
    falls through it (see `mirror_code`), as though the room were only its reflection."""
    k = -2 if night else 0
    outer, inner = ellipse(cx, cy, rx, ry), ellipse(cx, cy, rx - 2, ry - 2)
    for (x, y) in outer - inner:
        dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        t = 2 + round(4 * light(dx, dy, 0.35))
        p.px(x, y, BRASS[max(1, min(6, t + k))])
    for (x, y) in outer:
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ddx, y + ddy) not in outer:
                p.px(x + ddx, y + ddy, BRASS[0])
    glass = NIGHT if night else GLASS
    G = p.layer("mirror", z=-1)
    for (x, y) in inner:
        dx, dy = (x + 0.5 - cx) / (rx - 2), (y + 0.5 - cy) / (ry - 2)
        t = 1 if night else 4
        band_ = dx + dy * 0.6
        if -0.95 < band_ < -0.55 or -0.25 < band_ < -0.1:
            t += 1
        p.px(x, y, glass[t], G)
    if night:
        mirror_code(p, cx, cy, rx - 2, ry - 2, motion)
    hit = (round(cx + rx * 0.3), round(cy - ry * 0.35))
    rnd = random.Random(3)
    for dx, dy in ((-1, 1), (-1, 0), (0, 1), (1, 1), (-1, -1), (1, 0)):
        x, y = hit
        for _ in range(rnd.randint(5, 11)):
            x += dx if rnd.random() < 0.8 else 0
            y += dy if rnd.random() < 0.8 else 0
            if (x, y) in inner:
                p.px(x, y, C["white"] if not night else GLASS[4])
                if (x + 1, y + 1) in inner and (x + 1, y + 1) != hit:
                    p.px(x + 1, y + 1, glass[1 if not night else 0])
    p.px(*hit, C["white"])
    top = round(cy - ry)
    for i in range(1, 5):
        p.px(round(cx) - 1 - i, top - i, BRASS[max(0, 2 + k)])
        p.px(round(cx) + i, top - i, BRASS[max(0, 2 + k)])
    p.px(round(cx) - 1, top - 5, BRASS[max(0, 5 + k)])
    p.px(round(cx), top - 5, BRASS[max(0, 4 + k)])


def rug(p: Pix, x0, x1, g, night):
    """A Persian runner on the floor at row g from column x0 to x1, seen almost edge on: a band of madder red with a
    row of small gold and indigo medallions along it, its edge dark, and a fringe at each end."""
    k = -2 if night else 0
    for x in range(x0, x1):
        m = (x - x0) % 6
        p.px(x, g - 1, (BRASS[max(0, 4 + k)] if m == 2 else BLUE[max(0, 1 + k // 2)] if m == 5 else OX[max(0, 3 + k)]))
        p.px(x, g, OX[max(0, 1 + k // 2)])
    for x in (x0 - 1, x0 - 2, x1, x1 + 1):
        p.px(x, g, SATIN[max(0, 4 + k)] if x % 2 else SATIN[max(0, 2 + k)])


def suitcase(p: Pix, x0, g, night):
    """An old leather suitcase standing on its end on the floor at row g from column x0, 17 wide and 13 tall: its
    tan hide lit along its top and left, two straps buckled round it, brass corners and clasps, its handle on top,
    and a hotel's label pasted on its side."""
    k = -2 if night else 0
    W = WOOD
    top = g - 12
    case = rounded(x0, top, x0 + 17, g + 1, r=1.5)
    pillow(p, case, W, lo=max(1, 2 + k), hi=max(2, 6 + k), r=2.5)
    for sx in (x0 + 4, x0 + 12):
        for y in range(top, g + 1):
            p.px(sx, y, W[max(0, 1 + k)])
        p.px(sx, top + 5, BRASS[max(0, 5 + k)])
        p.px(sx, top + 6, BRASS[max(0, 3 + k)])
    for cx, cy in ((x0, top), (x0 + 16, top), (x0, g), (x0 + 16, g)):
        p.px(cx, cy, BRASS[max(0, 4 + k)])
    p.hline(x0 + 6, x0 + 11, top - 2, W[max(0, 4 + k)])
    p.px(x0 + 5, top - 1, W[max(0, 3 + k)])
    p.px(x0 + 11, top - 1, W[max(0, 2 + k)])
    label = (SATIN[max(0, 5 + k)], CANDY[max(0, 3 + k)])
    p.rect(x0 + 6, top + 3, 5, 4, label[0])
    p.hline(x0 + 6, x0 + 11, top + 3, label[1])
    p.hline(x0 + 7, x0 + 10, top + 5, SATIN[max(0, 2 + k)])


def umbrella(p: Pix, x0, g, night, motion):
    """A black umbrella furled in a brass stand on the floor at row g from column x0, 17 tall, still wet from the
    storm: its crook handle over the stand's rim, rain gathering at its tip and dripping into the puddle at its foot,
    a drop every few seconds in a moving header."""
    k = -2 if night else 0
    top = g - 7
    for y in range(top, g + 1):
        p.px(x0, y, BRASS[max(0, 5 + k)])
        for x in range(x0 + 1, x0 + 6):
            p.px(x, y, BRASS[max(0, (4 if x < x0 + 3 else 2) + k)])
        p.px(x0 + 6, y, BRASS[0])
    p.hline(x0, x0 + 7, top, BRASS[max(0, 6 + k)])
    p.hline(x0, x0 + 7, top + 3, BRASS[max(0, 3 + k)])
    cloth = (STORM[1], STORM[0]) if not night else (NIGHT[4], NIGHT[2])
    for y in range(top - 7, top):
        p.px(x0 + 2, y, cloth[0])
        p.px(x0 + 3, y, cloth[1])
        if y > top - 4:
            p.px(x0 + 4, y, cloth[1])
    for dx, dy in ((2, -8), (2, -9), (3, -10), (4, -10), (5, -9), (5, -8)):
        p.px(x0 + dx, top + dy, WOOD[max(0, 4 + k)] if dx < 4 else WOOD[max(0, 2 + k)])
    puddle = GLASS[4] if not night else NIGHT[4]
    p.hline(x0 - 3, x0 + 10, g, puddle)
    p.hline(x0 - 1, x0 + 7, g, GLASS[5] if not night else NIGHT[5])
    drop = GLASS[6] if not night else GLASS[3]
    p.px(x0 + 7, top + 1, drop)
    if motion:
        p.px(x0 + 7, top + 4, drop, p.seq("drip0", 0.0, 0.08, 3.6, z=1.6))
        L = p.seq("drip1", 0.08, 0.16, 3.6, z=1.6)
        p.px(x0 + 6, g - 1, drop, L)
        p.px(x0 + 8, g - 1, drop, L)


def rim(p: Pix, x0, x1, y0, y1, ramp, left=False):
    """The lamp's green caught by night along the right of what stands in the box (x0, y0, x1, y1) drawn in `ramp`
    (along its left, with `left`), the side that faces the light beside it: on each row the outermost cell inside the
    outline takes a rim of phosphor, brighter where the silhouette steps out."""
    base = p.layers["base"]
    own = set(ramp)
    last = None
    cols = range(x0 + 1, x1 + 1) if left else range(x1, x0, -1)
    for y in range(y0, y1):
        x = next((x for x in cols if base.get((x, y)) in own and base.get((x, y)) != ramp[0]), None)
        if x is not None:
            out = last is None or (x < last if left else x > last)
            p.px(x, y, FLAME[2] if out else FLAME[1])
        last = x


def room(p: Pix, x0, g, night, motion, mirrored=True, compact=False) -> tuple:
    """The left of the room, standing on the floor at row g from column x0: the wingback chair on a Persian runner,
    the cracked mirror over it when `mirrored`, and beside it the round table with the banker's lamp and the glass of
    water, which by night is all the light the room has, and rims the chair. A `compact` room, for less room beside
    the words, has a smaller table and the lamp alone on it. Returns its span."""
    if mirrored:
        mirror(p, x0 + 17, g - 61, night, motion)
    rug(p, x0 + 1, x0 + (46 if compact else 52), g, night)
    wingback(p, x0, g, night)
    if night:
        rim(p, x0, x0 + 34, g - 40, g, OX)
    top = side_table(p, x0 + 35, g, night, w=12 if compact else 18)
    bankers_lamp(p, x0 + 35, top - 1, night, motion, clip=(EDGE, g - 40, x0 + (47 if compact else 53), g + 1))
    if not compact:
        water_glass(p, x0 + 47, top - 1, night)
    return (x0 - 1, x0 + (48 if compact else 54))


# --------------------------------------------------------------------------- the window
def _storm(p: Pix, x0, y0, x1, y1, night, motion):
    """What the window shows: the storm. By day a grey sky heavy with rolling cloud over the grey towers of the
    city; by night a dark sky over towers whose windows burn green, a light blinking on the tallest's mast, and the
    sky glowing faintly green over the city; everything kept inside the box, however small the window. A drawing made
    lighter rolls half the clouds."""
    S = NIGHT if night else STORM
    h = y1 - y0
    sh = p.shapes["base"]
    bands = (1, 1, 2, 2, 3) if night else (3, 3, 4, 4, 5)
    for i, t in enumerate(bands):
        a, b = y0 + i * h // len(bands), y0 + (i + 1) * h // len(bands)
        sh.append(f'<rect x="{x0}" y="{a}" width="{x1 - x0}" height="{b - a}" fill="{S[t]}"/>')
    if night:
        sh.append(f'<rect x="{x0}" y="{y1 - 22}" width="{x1 - x0}" height="22" fill="{FLAME[1]}" fill-opacity=".12"/>')
    clouds = ((x0 + 4, y0 + 3, 10, 4), (x0 + 20, y0 + 5, 13, 4.6), (x0 + 31, y0 + 2, 8, 3.4),
              (x0 + 9, y0 + 12, 11, 3.6), (x0 + 27, y0 + 15, 10, 3.2), (x0 + 3, y0 + 20, 8, 2.6))
    if p.lite:              # a drawing made lighter keeps the clouds' bands and the towers, not their billows
        clouds = clouds[1::2]
    for i, (cx, cy, rx, ry) in enumerate(clouds):
        blob = ellipse(cx, cy, rx, ry)
        base = bands[0] + (1 if i % 2 else 2)
        for (x, y) in blob:
            if x0 <= x < x1 and y0 <= y < y1:
                edge = (x, y - 1) not in blob
                under = (x, y + 1) not in blob
                p.px(x, y, S[min(6, base + 1)] if edge else S[max(0, base - 1)] if under else S[base])
    rnd = random.Random(5)
    towers = ((0, 8, 18), (7, 7, 27), (13, 9, 14), (21, 6, 23), (26, 8, 16))
    for dx, tw, th in towers:
        tx = x0 + dx
        if tx >= x1:
            continue
        for y in range(max(y0, y1 - th), y1):
            for x in range(tx, min(x1, tx + tw)):
                p.px(x, y, S[0] if night else S[2])
            p.px(tx, y, S[1] if night else S[3])
        for wy in range(y1 - th + 2, y1 - 1, 3):
            for wx in range(tx + 2, min(x1, tx + tw) - 1, 2):
                if rnd.random() < (0.5 if night else 0.35):
                    lit = FLAME[rnd.choice((1, 2, 2, 3, 4))] if night else S[4]
                    L = p.twinkle(wx + wy) if (night and motion and rnd.random() < 0.15) else "base"
                    if wy >= y0:
                        p.px(wx, wy, lit, L)
    mx = x0 + 7 + 3
    top = y1 - 27
    if top - 6 >= y0:
        p.vline(mx, top - 5, top, S[1] if night else S[2])
        if night:
            p.px(mx, top - 6, FLAME[5], p.blink(2) if motion else "base")


STRIKE = 9.0                                             # the seconds between one stroke of lightning and the next
STROKES = ((0.6, 0.615, True), (0.64, 0.67, False))      # its two flashes in quick succession, as parts of that loop


def room_flash(p: Pix, box, window, holes=()):
    """The lightning lighting the whole room for its instant by night: a pale wash of its phosphor over the wallpaper
    in the box (x0, y0, x1, y1), in two steps, fading over its last rows, brightest round the box `window` it comes in
    by and fainter the second time, behind everything that stands in the room, and never in the boxes `holes` (the
    month's mark). Only a moving header has it; it shows with the bolt (see `lightning`)."""
    x0, y0, x1, y1 = box
    if y1 - y0 < 8:
        return
    cid = f"atm{getattr(p, 'sheet', 'p')}rf"
    cut = [(max(a, x0), max(b, y0), min(c, x1), min(d, y1)) for a, b, c, d in holes]
    p.defs.append(f'<clipPath id="{cid}"><path clip-rule="evenodd" d="M{x0} {y0}h{x1 - x0}v{y1 - y0}h{x0 - x1}z'
                  + "".join(f"M{a} {b}h{c - a}v{d - b}h{a - c}z" for a, b, c, d in cut if a < c and b < d)
                  + '"/></clipPath>')
    wx0, wy0, wx1, wy1 = window
    for n, (t0, t1, _) in enumerate(STROKES):
        a = (".06", ".04")[n]
        p.raw(-1.2, f'<g clip-path="url(#{cid})" fill="{FLAME[5]}" fill-opacity="{a}" opacity="0"><rect x="{x0}" '
                    f'y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/><rect x="{x0}" y="{y0}" width="{x1 - x0}" '
                    f'height="{y1 - y0 - 5}"/><ellipse cx="{num((wx0 + wx1) / 2)}" cy="{num((wy0 + wy1) / 2)}" '
                    f'rx="{num((wx1 - wx0) * 1.6)}" ry="{num(wy1 - wy0)}"/><animate attributeName="opacity" '
                    f'values="0;1;0" keyTimes="0;{num(t0)};{num(t1)}" dur="{num(STRIKE)}s" repeatCount="indefinite" '
                    f'calcMode="discrete"/></g>', "")


def lightning(p: Pix, x0, y0, x1, y1, motion, dur=STRIKE):
    """The lightning by night: a forked bolt of phosphor down the window's sky, which a still file holds, and in a
    moving header its flash, a wash of green over the window's sky, twice in quick succession once every `dur`
    seconds, the bolt showing with it; the room lights up with it (see `room_flash`)."""
    rnd = random.Random(4)
    x = x0 + (x1 - x0) * 3 // 5
    pts = []
    for y in range(y0, y1 - 14):
        if rnd.random() < 0.4:
            x += rnd.choice((-1, 1, 1))
        pts.append((min(x1 - 2, max(x0 + 1, x)), y))
    fx, fy = pts[len(pts) // 3]
    for i in range(12):
        fx -= 1 if i % 3 else 0
        fy += 1
        pts.append((fx, fy))
    shots = STROKES if motion else ((0, 1, True),)
    bolt = {}
    for (bx, by) in pts:
        bolt[(bx - 1, by)] = FLAME[2]
        bolt[(bx + 1, by)] = FLAME[4]
    for (bx, by) in pts:
        bolt[(bx, by)] = FLAME[6]
    p.symbol(("bolt", x0, y0), bolt)
    for n, (t0, t1, keep) in enumerate(shots):
        L = p.seq(f"bolt{n}", t0, t1, dur, keep=keep, z=1.5)
        p.use(("bolt", x0, y0), 0, 0, L)
        if motion:
            F = p.seq(f"flash{n}", t0, t1, dur, z=1.4)
            p.shapes[F].append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{FLAME[3]}" '
                               f'fill-opacity=".2"/>')


def trickle(p: Pix, box, night, n=0, seed=9):
    """The rain running down the window's glass: drops a unit wide, each a bright bead with a short trail, stepping
    down the panes a unit every tenth of a second, drawn once and laid twice so the loop never shows its seam; held
    in the still twin where it begins. A drawing made lighter keeps half the drops."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    bead = GLASS[6] if not night else GLASS[2]
    trail = GLASS[5] if not night else NIGHT[5]
    loop = y1 - y0 + 6
    cells = {}
    for x in range(x0, x1):
        for n_ in range(2):
            if rnd.random() < 0.55 or (p.lite and n_):     # a drawing made lighter keeps half the drops
                continue
            head = rnd.randrange(loop)
            for i in range(rnd.randint(2, 4)):
                cells[(x, y0 + (head - i) % loop)] = bead if i == 0 else trail
    cid = f"tr{n}"
    gid = f"{cid}g"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    p.defs.append(f'<g id="{gid}">{p.markup(cells)}</g>')
    values = ";".join(f"0 {i}" for i in range(loop))
    p.raw(1.2, f'<g clip-path="url(#{cid})"><g><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/>'
               f'<animateTransform attributeName="transform" type="translate" values="{values}" '
               f'dur="{num(loop * 0.1)}s" repeatCount="indefinite" calcMode="discrete"/></g></g>',
          f'<g clip-path="url(#{cid})"><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/></g>')


def window(p: Pix, x0, y0, x1, sill, night, motion):
    """A tall sash window in a mahogany frame from (x0, y0) to its sill at row `sill`, its panes in two columns and
    two rows a sash, the storm outside them (see `_storm`), the rain running down the glass, and by night the
    lightning (see `lightning`)."""
    k = -2 if night else 0
    gx0, gy0, gx1, gy1 = x0 + 3, y0 + 3, x1 - 3, sill - 2
    _storm(p, gx0, gy0, gx1, gy1, night, motion)
    if night:
        lightning(p, gx0, gy0, gx1, gy1, motion)
    trickle(p, (gx0, gy0, gx1, gy1), night)
    for y in range(y0, sill):
        for x in range(x0, x1):
            if gx0 <= x < gx1 and gy0 <= y < gy1:
                continue
            if x in (x0, x1 - 1) or y == y0:
                t = 0
            elif x == x0 + 1 or y == y0 + 1:
                t = 5
            elif x >= gx1 or y >= gy1:
                t = 2
            else:
                t = 3
            p.px(x, y, WOOD[max(0, t + k)])
    mid = (gy0 + gy1) // 2
    cx = (gx0 + gx1) // 2
    for (a, b) in ((gy0, mid), (mid + 3, gy1)):
        q = (a + b) // 2
        p.hline(gx0, gx1, q, WOOD[max(0, 4 + k)])
        p.hline(gx0, gx1, q + 1, WOOD[1])
        p.vline(cx, a, b, WOOD[max(0, 4 + k)])
        p.vline(cx + 1, a, b, WOOD[1])
    p.hline(gx0, gx1, mid, WOOD[max(0, 5 + k)])
    p.hline(gx0, gx1, mid + 1, WOOD[max(0, 3 + k)])
    p.hline(gx0, gx1, mid + 2, WOOD[0])
    p.hline(x0 - 2, x1 + 2, sill, WOOD[max(0, 5 + k)])
    p.hline(x0 - 2, x1 + 2, sill + 1, WOOD[max(0, 3 + k)])
    p.hline(x0 - 1, x1 + 1, sill + 2, WOOD[0])


def curtain(p: Pix, x0, x1, y0, g, tie, night, right=False):
    """A curtain of green velvet hung from the rod at row y0 down to the floor at row g, hanging in deep upright
    folds, each lit along its crest and falling into shadow in its trough, its inner edge sweeping in to where a
    brass cord ties it back at row `tie`, a tassel hanging from the cord, and spreading out again below it to pool
    on the floor."""
    lo, hi = (0, 3) if night else (1, 6)
    fold = (hi, hi - 1, (hi + lo) // 2, lo + 1, lo) if not night else (hi, hi - 1, lo + 1, lo)
    w = x1 - x0
    narrow = 4
    for y in range(y0, g + 1):
        if y <= tie:
            f = (y - y0) / max(1, tie - y0)
            span = narrow + (w - narrow) * math.cos(f * math.pi / 2) ** 0.8
        else:
            f = (y - tie) / max(1, g - tie)
            span = narrow + (w - 2 - narrow) * math.sin(f * math.pi / 2) ** 0.9
        span = max(narrow, round(span))
        a, b = (x1 - span, x1) if right else (x0, x0 + span)
        for x in range(a, b):
            i = (x - x0) if not right else (x1 - 1 - x)
            t = fold[i % len(fold)]
            if x == (a if right else b - 1):
                t = lo
            p.px(x, y, VELVET[t])
    k = -2 if night else 0
    a, b = (x0, x0 + narrow) if not right else (x1 - narrow, x1)
    for x in range(a, b):
        p.px(x, tie, BRASS[max(0, 5 + k)])
        p.px(x, tie + 1, BRASS[max(0, 2 + k)])
    tx = a if not right else b - 1
    for i, c in enumerate((4, 3)):
        p.px(tx, tie + 2 + i, BRASS[max(0, c + k)])
    for dy, (u, v) in enumerate(((-1, 1), (-1, 1), (-1, 1))):
        for dx in range(u, v + 1):
            p.px(tx + dx, tie + 4 + dy, BRASS[max(0, (5 if dx < 0 else 3 if dx == 0 else 1) + k)])


def valance(p: Pix, x0, x1, y, night):
    """The pelmet over the window: swags of green velvet hung from the rod at row y, lit along their tops and deeper
    in their folds, scalloped along their foot and edged with a brass fringe."""
    lo, hi = (0, 3) if night else (1, 6)
    k = -2 if night else 0
    w = x1 - x0
    for x in range(x0, x1):
        u = ((x - x0) / w) * 3 % 1.0
        depth = 4 + round(3 * math.sin(math.pi * u))
        for dy in range(depth):
            t = hi if dy == 0 else hi - 2 if dy < depth - 1 else lo + 1
            if u < 0.12 or u > 0.88:
                t = max(lo, t - 1)
            p.px(x, y + dy, VELVET[t])
        p.px(x, y + depth, BRASS[max(0, (5 if x % 2 else 3) + k)])
        if x % 2 == 0:
            p.px(x, y + depth + 1, BRASS[max(0, 2 + k)])


def pill(p: Pix, x, y, ramp, motion, phase):
    """A pill lying on its side, 9 wide and 5 tall with its rim: a glossy capsule lit along its top, a white glint
    at its upper left that catches the light, its underside dark, ringed in its darkest tone."""
    art = [".ooooooo.", "oWllllmmo", "ollmmmmdo", "odddddddo", ".ooooooo."]
    pal = {"o": ramp[0], "l": ramp[4], "m": ramp[3], "d": ramp[1]}
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch in pal:
                p.px(x + i, y + j, pal[ch])
    p.px(x + 1, y + 1, ramp[6])
    p.px(x + 2, y + 1, ramp[5])
    p.px(x + 1, y + 1, C["white"], p.twinkle(phase) if motion else "base")


def pill_box(p: Pix, x0, y, night, motion):
    """The small box on the table at row y from column x0, 21 wide: its lid of oxblood leather open behind it, lined
    in quilted satin, and in its satin bed the two pills side by side, the red and the blue."""
    k = -2 if night else 0
    sat = [SATIN[max(0, i + k)] for i in range(7)]
    for yy in range(y - 11, y - 6):
        for xx in range(x0 + 1, x0 + 20):
            edge = xx in (x0 + 1, x0 + 19) or yy == y - 11
            quilt = (xx - x0 + yy) % 4 == 0 or (xx - x0 - yy) % 4 == 0
            p.px(xx, yy, OX[max(0, 3 + k)] if edge else sat[4] if quilt else sat[5])
    p.hline(x0 + 1, x0 + 20, y - 12, OX[0])
    p.vline(x0, y - 11, y - 4, OX[0])
    p.vline(x0 + 20, y - 11, y - 4, OX[0])
    for yy in range(y - 6, y - 2):
        p.hline(x0 + 1, x0 + 20, yy, sat[3] if yy > y - 6 else sat[2])
    pill(p, x0 + 1, y - 7, CANDY, motion, 0)
    pill(p, x0 + 11, y - 7, BLUE, motion, 2)
    p.hline(x0, x0 + 21, y - 2, BRASS[max(0, 5 + k)])
    p.hline(x0, x0 + 21, y - 1, OX[max(0, 3 + k)])
    p.hline(x0, x0 + 21, y, OX[1])
    p.vline(x0, y - 4, y + 1, OX[0])
    p.vline(x0 + 20, y - 4, y + 1, OX[0])
    p.hline(x0, x0 + 21, y + 1, OX[0])


def stand(p: Pix, cx, top, g, night):
    """A little round table of mahogany, its top at row `top` over the floor at row g, centred on column cx: a lace
    doily over its lipped top, a slender turned stem and three feet."""
    k = -2 if night else 0
    p.hline(cx - 10, cx + 11, top, WOOD[max(0, 5 + k)])
    p.hline(cx - 10, cx + 11, top + 1, WOOD[max(0, 3 + k)])
    for x in range(cx - 8, cx + 9):
        p.px(x, top + 2, SATIN[max(0, 6 + k)] if x % 3 else SATIN[max(0, 4 + k)])
        if x % 3 == 1:
            p.px(x, top + 3, SATIN[max(0, 5 + k)])
    p.hline(cx - 9, cx - 8, top + 2, WOOD[0])
    p.hline(cx + 9, cx + 10, top + 2, WOOD[0])
    for y in range(top + 3, g - 1):
        fat = (y - top) in (6, 7)
        p.px(cx - 1 - (1 if fat else 0), y, WOOD[max(0, 5 + k)])
        p.px(cx, y, WOOD[max(0, 3 + k)])
        p.px(cx + 1 + (1 if fat else 0), y, WOOD[1])
    for dx in range(-6, 8):
        p.px(cx + dx, g - (1 if abs(dx) < 3 else 0), WOOD[max(0, (4 if dx < 0 else 1) + k)])


def storm_window(p: Pix, x0, x1, g, night, motion, top=None) -> tuple:
    """The right of the room, standing on the floor at row g from column x0 to x1: the tall window streaming with
    rain under a velvet pelmet on its brass rod at row `top` (under the tufted panel when not given), a curtain of
    green velvet tied back each side, and before it the little table with the open box and the two pills. Given less
    room than its widest, the curtains draw in, and the window with them. Returns its span."""
    k = -2 if night else 0
    y0 = BAND + 2 if top is None else top
    w = x1 - x0
    cw = 13 - (54 - w + 1) // 2
    mid = x0 + w // 2
    window(p, x0 + cw - 4, y0 + 4, x1 - cw + 5, g - 14, night, motion)
    tie = max(y0 + 10, g - 42)
    curtain(p, x0 + 1, x0 + cw + 1, y0 + 2, g, tie, night)
    curtain(p, x1 - cw - 1, x1 - 1, y0 + 2, g, tie, night, right=True)
    valance(p, x0 + 1, x1 - 1, y0 + 2, night)
    p.hline(x0, x1, y0, BRASS[max(0, 5 + k)])
    p.hline(x0, x1, y0 + 1, BRASS[max(0, 2 + k)])
    for fx in (x0 - 1, x1 - 1):
        p.rect(fx, y0 - 1, 2, 4, BRASS[max(0, 4 + k)])
        p.px(fx, y0 - 1, BRASS[max(0, 6 + k)])
    stand(p, mid, g - 19, g, night)
    pill_box(p, mid - 10, g - 21, night, motion)
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the fireside
def club_chair(p: Pix, x0, g, night, right=True, fire=False, big=False):
    """A club chair of red leather seen in profile, standing on the floor at row g from column x0, 24 wide and 30
    tall (29 and 36 when `big`), facing right (or left): its high back padded and rounded over, its arm rolled into a
    fat scroll at the front and nailed with brass down its face, its apron close-nailed along the foot and its short
    legs of mahogany; by night, when it stands by the `fire`, the green of the fire along the side that faces it.
    Returns its span."""
    f = 1.2 if big else 1.0
    w, h = round(24 * f), round(30 * f)
    top = g - h + 1
    lo, hi = (0, 3) if night else (1, 5)

    def X(lx):
        return x0 + lx if right else x0 + w - 1 - lx

    def Y(v):
        return top + round(v * f)

    def box(lx0, y0, lx1, y1, r):
        return {(X(lx), y) for (lx, y) in rounded(lx0, y0, lx1, y1, r=r)}
    pillow(p, box(0, top, round(8 * f), Y(24), 3.2 * f), OX, lo=lo, hi=hi, r=3)
    pillow(p, box(2, Y(11), w - 2, Y(24), 2.5 * f), OX, lo=lo, hi=hi - 1, r=3)
    pillow(p, box(2, Y(10), w - 3, Y(14), 2 * f), OX, lo=lo + 1, hi=hi, r=2, outline=False)
    sphere(p, X(w - 5) + 0.5, Y(13), 3.3 * f, OX, lo=max(1, lo), hi=hi + 1, spec=not night)
    p.px(X(w - 5), Y(13), OX[0])
    for y in range(Y(17), Y(24), 2):
        p.px(X(w - 4), y, BRASS[4 if night else 5])
    pillow(p, box(1, Y(23), w - 1, Y(27), 1), OX, lo=lo, hi=hi, r=2)
    for lx in range(2, w - 2, 2):
        p.px(X(lx), Y(26), BRASS[(3 if night else 5) - (1 if lx > w * 0.6 else 0)])
    for lx in (3, w - 5):
        for y in range(Y(28), g + 1):
            p.px(X(lx), y, WOOD[(2 if night else 4) + (1 if y == Y(28) else 0)])
            p.px(X(lx + 1), y, WOOD[1 if night else 2])
    if night and fire:
        rim(p, x0 - 1, x0 + w, top - 1, Y(28), OX, left=not right)
    return (x0 - 1, x0 + w + 1)


def _reflected_window(p: Pix, x0, y0, x1, y1, night, motion):
    """The window across the room as a mirror shows it, from (x0, y0) to (x1, y1): the storm outside its panes (see
    `_storm`), its glazing bars, and by night the lightning, which the mirror flashes with."""
    _storm(p, x0, y0, x1, y1, night, motion)
    if night and y1 - y0 >= 20:
        lightning(p, x0, y0, x1, y1, motion)
    k = -2 if night else 0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    p.vline(cx, y0, y1, WOOD[max(0, 4 + k)])
    p.vline(cx + 1, y0, y1, WOOD[1])
    p.hline(x0, x1, cy, WOOD[max(0, 4 + k)])
    p.hline(x0, x1, cy + 1, WOOD[1])


def fireplace(p: Pix, x0, g, night, motion, top=None, w=36, h=40):
    """A fireplace of carved mahogany, `w` wide and `h` tall over its hearth at row g from column x0: fluted pilasters
    with brass capitals, a frieze with a carved panel, its shelf lit along its edge with a brass clock on it between
    two candlesticks, an arched opening backed with cast iron, a grate of logs, a brass fender on a hearthstone of
    pale marble; cold by day, and by night a fire burning in it in the hand's phosphor, flickering, its light on the
    hearth and the candles lit on the shelf. Over it from row `top`, when there is room, a tall pier mirror in a gilt
    frame that shows the window across the room and the storm through it (see `_reflected_window`). Returns its
    span."""
    k = -2 if night else 0
    my = g - h + 1

    def W(t):
        return WOOD[max(0, min(6, t + k))]
    p.hline(x0 - 3, x0 + w + 3, g - 2, SATIN[max(0, 5 + k)])
    p.hline(x0 - 3, x0 + w + 3, g - 1, SATIN[max(0, 3 + k)])
    p.hline(x0 - 3, x0 + w + 3, g, SATIN[max(0, 1 + k)])
    fx0, fx1, fy0, fy1 = x0 + 7, x0 + w - 7, my + 11, g - 2
    back = NIGHT if night else STORM
    for (x, y) in rounded(fx0, fy0, fx1, fy1, r=5, bottom=False):
        p.px(x, y, back[2] if (x - fx0) % 4 == 0 and y < fy1 - 6 and not night else back[0 if night else 1])
    gy = fy1 - 5
    iron, lit_iron = (NIGHT[3], NIGHT[4]) if night else (STORM[1], STORM[2])
    p.hline(fx0 + 3, fx1 - 3, gy + 3, iron)
    p.hline(fx0 + 3, fx1 - 3, gy + 1, lit_iron)
    for x in range(fx0 + 3, fx1 - 3, 3):
        p.px(x, gy + 2, iron)
    for x in (fx0 + 4, fx1 - 5):
        p.vline(x, gy + 1, fy1, lit_iron)
    for (lx0, lx1, ly) in ((fx0 + 4, fx1 - 6, gy), (fx0 + 7, fx1 - 3, gy - 1), (fx0 + 6, fx1 - 7, gy - 2)):
        p.hline(lx0, lx1, ly, W(3))
        p.px(lx0, ly, W(5))
        p.px(lx1 - 1, ly, W(1))
    if night:
        for x in range(fx0 + 5, fx1 - 5, 2):
            p.px(x, gy - 1, FLAME[3])
        rnd = random.Random(5)
        span = fx1 - fx0 - 8
        for ph in (range(3) if motion else (0,)):
            L = p.flicker(ph) if motion else "base"
            for x in range(fx0 + 4, fx1 - 4):
                tall = 4 + round(5 * math.sin(math.pi * (x - fx0 - 4 + 0.5) / span) ** 0.8) + rnd.randint(-1, 2)
                for j in range(tall):
                    if (x + j + ph) % 5 == 0 and j > tall // 2:
                        continue
                    t = 6 if j < tall * 0.35 else 5 if j < tall * 0.6 else 4 if j < tall * 0.85 else 3
                    p.px(x, gy - 2 - j, FLAME[t], L)
        p.halo(x0 + w / 2, gy - 3, 15, 10, FLAME[3], (0.05, 0.09, 0.14),
               L=p.flicker(1, back=True) if motion else "haze")
    else:
        for x in range(fx0 + 5, fx1 - 5, 3):
            p.px(x, gy - 3, STORM[4])
    for side in (0, 1):
        px0 = x0 if side == 0 else x0 + w - 6
        tones = (4, 5, 2, 4, 2, 1) if side == 0 else (4, 2, 4, 1, 3, 1)
        for i, t in enumerate(tones):
            p.vline(px0 + i, my + 3, g - 2, W(t))
        p.hline(px0 - 1, px0 + 7, my + 9, BRASS[max(0, 4 + k)])
        p.hline(px0 - 1, px0 + 7, my + 10, BRASS[max(0, 2 + k)])
        p.hline(px0 - 1, px0 + 7, g - 4, W(5))
        p.hline(px0 - 1, px0 + 7, g - 3, W(2))
    p.rect(x0 + 6, my + 3, w - 12, 8, W(3))
    p.hline(x0 + 6, x0 + w - 6, my + 3, W(2))
    p.hline(x0 + 9, x0 + w - 9, my + 5, W(1))
    p.hline(x0 + 9, x0 + w - 9, my + 8, W(5))
    p.vline(x0 + 9, my + 5, my + 9, W(1))
    p.vline(x0 + w - 10, my + 5, my + 9, W(5))
    cx = x0 + w // 2
    for (dx, dy), t in (((-1, 6), 5), ((0, 6), 4), ((-1, 7), 3), ((0, 7), 2)):
        p.px(cx + dx, my + dy, BRASS[max(0, t + k)])
    p.hline(x0 + 5, x0 + w - 5, g - 4, BRASS[max(0, 5 + k)])
    p.hline(x0 + 5, x0 + w - 5, g - 3, BRASS[max(0, 3 + k)])
    p.px(x0 + 5, g - 2, BRASS[max(0, 2 + k)])
    p.px(x0 + w - 6, g - 2, BRASS[max(0, 2 + k)])
    p.hline(x0 - 2, x0 + w + 2, my, W(5))
    p.hline(x0 - 2, x0 + w + 2, my + 1, W(4))
    p.hline(x0 - 1, x0 + w + 1, my + 2, W(1))
    # The clock on the shelf and a candlestick at each end, their candles lit by night.
    p.rect(cx - 2, my - 6, 4, 6, BRASS[max(0, 3 + k)])
    p.hline(cx - 2, cx + 2, my - 6, BRASS[max(0, 5 + k)])
    p.rect(cx - 1, my - 5, 2, 2, SATIN[max(0, 6 + k)])
    for sx in (x0 + 1, x0 + w - 2):
        p.vline(sx, my - 5, my, BRASS[max(0, 4 + k)])
        p.px(sx - 1, my - 1, BRASS[max(0, 3 + k)])
        p.px(sx + 1, my - 1, BRASS[max(0, 2 + k)])
        p.vline(sx, my - 8, my - 5, SATIN[max(0, 6 + k)])
        if night:
            L = p.flicker(sx % 3) if motion else "base"
            p.px(sx, my - 9, FLAME[6], L)
            p.px(sx, my - 10, FLAME[4], L)
            p.halo(sx + 0.5, my - 9, 3, 3, FLAME[3], (0.1, 0.2), L=p.flicker(sx % 3, back=True) if motion else "haze")
    if top is not None and my - 6 - top >= 16:
        mx0, mx1, my0, my1 = x0 + 6, x0 + w - 6, top, my - 8
        for y in range(my0, my1):
            for x in (mx0, mx1 - 1):
                p.px(x, y, BRASS[max(0, 1 + k // 2)])
            p.px(mx0 + 1, y, BRASS[max(0, 5 + k)])
            p.px(mx1 - 2, y, BRASS[max(0, 3 + k)])
        for y, t in ((my0, None), (my0 + 1, 5), (my1 - 2, 3), (my1 - 1, None)):
            p.hline(mx0 + (0 if t is None else 1), mx1 - (0 if t is None else 1), y,
                    BRASS[max(0, 1 + k // 2)] if t is None else BRASS[max(0, t + k)])
        _reflected_window(p, mx0 + 2, my0 + 2, mx1 - 2, my1 - 2, night, motion)
        for i in range(-3, 4):
            p.px(cx + i, my0 - 1, BRASS[max(0, 4 + k)])
        p.px(cx - 1, my0 - 2, BRASS[max(0, 5 + k)])
        p.px(cx, my0 - 2, BRASS[max(0, 3 + k)])
    return (x0 - 3, x0 + w + 3)


def tea_table(p: Pix, cx, g, night):
    """A low pedestal table of mahogany centred on column cx on the floor at row g, 14 wide and 12 tall, and on it the
    glass of water and the two pills, the red and the blue."""
    k = -2 if night else 0
    top = g - 12
    p.hline(cx - 7, cx + 7, top, WOOD[max(0, 5 + k)])
    p.hline(cx - 7, cx + 7, top + 1, WOOD[max(0, 3 + k)])
    p.hline(cx - 6, cx + 6, top + 2, WOOD[max(0, 1 + k // 2)])
    for y in range(top + 3, g - 1):
        p.px(cx - 1, y, WOOD[max(0, 5 + k)])
        p.px(cx, y, WOOD[max(0, 2 + k)])
    for dx in range(-4, 5):
        p.px(cx + dx, g - (1 if abs(dx) < 2 else 0), WOOD[max(0, (4 if dx < 0 else 1) + k)])
    water_glass(p, cx - 6, top, night)
    for x, ramp in ((cx - 1, CANDY), (cx + 3, BLUE)):
        p.hline(x, x + 3, top - 1, ramp[3])
        p.px(x, top - 1, ramp[6])
        p.px(x + 2, top - 1, ramp[1])


def fireside(p: Pix, x0, x1, g, night, motion, room) -> tuple:
    """The fireside, standing on the floor at row g between columns x0 and x1 in the `room` rows free over it: the
    fireplace in the middle with its pier mirror over it as high as the room goes, a club chair at each side facing
    the other across the hearth, and between them the low table with the glass of water and the two pills; by night
    the fire's green on the chairs. Given a hundred columns and seventy rows the fireplace and the chairs stand a size
    larger. Returns its span."""
    big = x1 - x0 >= 100 and room >= 70
    fw, fh, cw = (40, 48, 29) if big else (36, 40, 24)
    cx = (x0 + x1) // 2
    fireplace(p, cx - fw // 2, g, night, motion, top=g - room + 2, w=fw, h=fh)
    tea_table(p, cx, g, night)
    club_chair(p, x0, g, night, right=True, fire=True, big=big)
    club_chair(p, x1 - cw, g, night, right=False, fire=True, big=big)
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the cheval glass
# The club chair as the cheval glass shows it, turned to face the room, 12 wide and 9 tall: its back (b), the scroll of
# its arm (s), its arm (a), its rim (o) and its nails (n).
SEEN = [
    "........oo..",
    ".......obbo.",
    ".......obbo.",
    "..oo...obbo.",
    ".ossoooobbo.",
    ".ossaaaaabo.",
    "..oaaaaaabo.",
    "..onanananno"[:12],
    "..o......o..",
]


def cheval(p: Pix, x0, g, night, motion, top, chair=True):
    """A cheval glass, 26 wide, swung between two turned mahogany uprights with finials on splayed feet, from row
    `top` to the floor at row g from column x0: the tall glass in its frame on brass pivots, silver and catching the
    light by day and by night grey in the dark, the red chair that faces it caught in its foot when there is a
    `chair`; and in a moving header its face gone to liquid where a hand touched it, rings spreading out across it
    one after another (the still file keeps the first). By night its silver holds what little light the room has,
    pale against the dark paper. Returns its span."""
    k = -2 if night else 0
    w = 26

    def W(t):
        return WOOD[max(0, min(6, t + k))]
    for side in (0, 1):
        ux = x0 + (1 if side == 0 else w - 3)
        p.vline(ux, top + 2, g - 1, W(5 if side == 0 else 4))
        p.vline(ux + 1, top + 2, g - 1, W(2))
        sphere(p, ux + 1, top + 1, 1.6, WOOD, lo=max(0, 1 + k), hi=max(1, 5 + k), spec=False)
        for dx in range(-3, 4):
            p.px(ux + dx + side, g - (0 if abs(dx) > 1 else 1), W(4 if dx < 0 else 2))
    p.hline(x0 + 1, x0 + w - 1, g - 4, W(3))
    p.hline(x0 + 1, x0 + w - 1, g - 3, W(1))
    gx0, gx1, gy0, gy1 = x0 + 4, x0 + w - 4, top + 3, g - 7
    cx, cy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    rx, ry = (gx1 - gx0) / 2, (gy1 - gy0) / 2
    outer = rounded(gx0, gy0, gx1, gy1, r=6)
    inner = rounded(gx0 + 2, gy0 + 2, gx1 - 2, gy1 - 2, r=4.5)
    for (x, y) in outer - inner:
        p.px(x, y, W(5 if (x < cx and y < cy) else 3 if (x < cx or y < cy) else 2))
    for (x, y) in outer:
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ddx, y + ddy) not in outer:
                p.px(x + ddx, y + ddy, WOOD[0])
    for side in (gx0 - 1, gx1):
        p.px(side, round(cy), BRASS[max(0, 5 + k)])
        p.px(side, round(cy) + 1, BRASS[max(0, 3 + k)])
    G = p.layer("cheval", z=-1)
    for (x, y) in inner:
        u = (x + 0.5 - cx) / rx + (y + 0.5 - cy) / ry * 0.6
        if night:
            c = GLASS[5] if -0.9 < u < -0.5 else GLASS[4] if -0.2 < u < -0.05 else GLASS[3]
        else:
            c = GLASS[6] if -0.9 < u < -0.55 or -0.2 < u < -0.05 else GLASS[5]
        p.px(x, y, c, G)
    if chair:
        # The chair in the glass, turned the other way, smaller and darker than in the room.
        sx, sy = gx1 - 3 - len(SEEN[0]), gy1 - 3 - len(SEEN)
        pal = ({"o": OX[0], "b": OX[2], "s": OX[3], "a": OX[1], "n": BRASS[2]} if night else
               {"o": OX[1], "b": OX[3], "s": OX[4], "a": OX[2], "n": BRASS[4]})
        for j, row in enumerate(SEEN):
            for i, ch in enumerate(row):
                if ch in pal and (sx + i, sy + j) in inner:
                    p.px(sx + i, sy + j, pal[ch], G)
    hx, hy = round(cx), round(cy + ry * 0.15)
    ring = GLASS[6] if night else C["white"]
    for n in range(4):
        if not motion and n:
            break
        rr = 1.5 + n * 2.2
        cells = {(round(hx + rr * math.cos(math.radians(a))), round(hy + rr * 1.3 * math.sin(math.radians(a))))
                 for a in range(0, 360, 6)}
        L = p.seq(f"liquid{n}", n / 5, (n + 1) / 5, 2.5, keep=(n == 0), z=-0.5) if motion else G
        for xy in cells & inner:
            p.px(*xy, ring, L)
    return (x0 - 3, x0 + w + 3)


def mirror_corner(p: Pix, x0, x1, g, night, motion, room, lamp=False) -> tuple:
    """The corner of the room with the cheval glass, standing on the floor at row g between columns x0 and x1 in the
    `room` rows free over it: the glass rising the whole height at the right, and the club chair facing it where
    the words leave it room; with `lamp`, the round table between them with the banker's lamp burning on it by night.
    Returns its span."""
    seated = x1 - x0 >= 52
    cheval(p, x1 - 26, g, night, motion, g - room + 2, chair=seated)
    if seated:
        club_chair(p, x0, g, night, right=True)
    if lamp:
        top = side_table(p, x0 + 28, g, night, w=14)
        bankers_lamp(p, x0 + 29, top - 1, night, motion, clip=(x0, g - 40, x1 - 26, g + 1))
    return (x0 - 1 if seated else x1 - 29, x1 + 1)


# --------------------------------------------------------------------------- the room on a phone
def phone_room(p: Pix, x0, x1, g, night, rows) -> tuple:
    """A phone's H1: the whole room across the phone, standing on the floor at row g between columns x0 and x1 in the
    `rows` free over it: the wingback chair with its table, its lamp and its glass at the left, the tall window in the
    storm with the two pills before it at the right, and between them the cracked mirror on the wallpaper over the
    suitcase and the umbrella dripping in its stand."""
    spans = [room(p, x0 + 1, g, night, False, mirrored=False)]
    spans.append(storm_window(p, x1 - 54, x1 - 1, g, night, False, top=g - rows + 3))
    mid = (spans[0][1] + spans[1][0]) // 2
    if rows >= 46:
        mirror(p, mid, g - 30, night, False, rx=8, ry=11)
    suitcase(p, mid - 16, g, night)
    umbrella(p, mid + 6, g, night, False)
    return (x0, x1)


def phone_fireside(p: Pix, x0, x1, g, night, room) -> tuple:
    """A phone's H2: the fireside across the phone (see `fireside`), and beside the chairs the round table with the
    banker's lamp burning on it by night at the left, and the suitcase and the umbrella in its stand at the right."""
    cx = (x0 + x1) // 2
    fireside(p, cx - 50, cx + 50, g, night, False, room)
    top = side_table(p, x0 + 2, g, night, w=14)
    bankers_lamp(p, x0 + 3, top - 1, night, False, clip=(x0, g - 40, cx - 50, g + 1))
    suitcase(p, x1 - 32, g, night)
    umbrella(p, x1 - 10, g, night, False)
    return (x0, x1)


def phone_mirror(p: Pix, x0, x1, g, night, room) -> tuple:
    """A phone's H3: the corner with the cheval glass across the phone (see `mirror_corner`), the banker's lamp on its
    table by the chair, and at the left the suitcase and the umbrella in its stand."""
    mirror_corner(p, x1 - 74, x1, g, night, False, room, lamp=True)
    suitcase(p, x0 + 4, g, night)
    umbrella(p, x0 + 28, g, night, False)
    return (x0, x1)


# ------------------------------------------------------------------------ the marks beside the titles, and the rule's
PILL = [".ooooooo.", "oWllllmmo", "ollmmmmdo", "odddddddo", ".ooooooo."]   # a pill, as `pill` draws it
PILLS_W, PILLS_H = 20, 5


def pills_mark(p: Pix, x, y, night):
    """The two pills side by side, the red and the blue, 20 wide and 5 tall from (x, y): glossy capsules lit along
    their tops, a white glint at the upper left of each, ringed in their darkest tone."""
    for i, ramp in enumerate((CANDY, BLUE)):
        p.sprite(x + 11 * i, y, PILL, {"o": ramp[0], "W": C["white"], "l": ramp[4], "m": ramp[3], "d": ramp[1]})


# Round dark glasses with no arms, 19 wide and 8 tall: their rims (o) and the bridge between, the dark lenses (L) with
# a glint at the upper left of each (G), and caught in them the two pills, the red (R, its underside r) in one and the
# blue (B, b) in the other.
SPECTACLES = [
    "..oooo.......oooo..",
    ".oLLLLo.....oLLLLo.",
    "oLGLLLLo...oLGLLLLo",
    "oLLLLLLooooLLLLLLLo",
    "oLLRrLLo...oLLBbLLo",
    "oLLLLLLo...oLLLLLLo",
    ".oLLLLo.....oLLLLo.",
    "..oooo.......oooo..",
]
SPECS_W, SPECS_H = 19, 8


def spectacles(p: Pix, x, y, night):
    """Round dark glasses, their top-left at (x, y), the red pill caught in one lens and the blue in the other, as the
    offer is seen reflected; their rims black by day and by night catching the lamp in brass."""
    rim_, lens = (BRASS[2], NIGHT[2]) if night else (NIGHT[1], NIGHT[3])
    p.sprite(x, y, SPECTACLES, {"o": rim_, "L": lens, "G": C["white"], "R": CANDY[4], "r": CANDY[2], "B": BLUE[4],
                                "b": BLUE[2]})


def _runner_tiles(p: Pix, night: bool, y: int) -> tuple:
    """The runner's patterns, drawn once a file: a tile six units wide of its madder red set with a medallion of gold
    and one of indigo, over its dark edge in the deep one (aligned to begin at row y - 2) and alone in the shallow
    one. Returns their ids."""
    key = ("runner", night, y)
    if key not in p.syms:
        k = -2 if night else 0
        uid = f"{getattr(p, 'sheet', 'p')}ru{len([q for q in p.syms if q[0] == 'runner'])}"
        row = {(m, 0): BRASS[max(0, 4 + k)] if m == 2 else BLUE[max(0, 2 + k // 2)] if m == 5 else OX[max(0, 3 + k)]
               for m in range(6)}
        edge = {(m, 1): OX[max(0, 1 + k // 2)] for m in range(6)}
        p.defs.append(f'<pattern id="{uid}d" y="{y - 2}" width="6" height="2" patternUnits="userSpaceOnUse">'
                      f'{fills({**row, **edge})}</pattern><pattern id="{uid}s" y="{y - 1}" width="6" height="1" '
                      f'patternUnits="userSpaceOnUse">{fills(row)}</pattern>')
        p.syms[key] = (f"{uid}d", f"{uid}s")
    return p.syms[key]


def runner(p: Pix, x0, x1, y, night):
    """The Persian runner laid along the floor on a rule at row y between columns x0 and x1, as the room's runner is
    laid under its chair: a band of madder red set with small medallions of gold and indigo by turns over its dark
    edge, a fringe at each end; a row deep where the words over it come down near the rule, and each stretch two
    units clear of every word."""
    k = -2 if night else 0
    ok = [p.clear_of_words(x - 2, y - 3, x + 3, y + 3) for x in range(x0, x1)]
    x = x0
    while x < x1:
        if not ok[x - x0]:
            x += 1
            continue
        b = next((i for i in range(x, x1) if not ok[i - x0]), x1)
        if b - x >= 14:
            deep = p.clear_of_words(x - 2, y - 4, b + 2, y + 3)
            tiles = _runner_tiles(p, night, y)
            p.shapes["base"].append(f'<rect x="{x + 2}" y="{y - 2 if deep else y - 1}" width="{b - x - 4}" '
                                    f'height="{2 if deep else 1}" fill="url(#{tiles[0] if deep else tiles[1]})"/>')
            for xx in (x, x + 1, b - 2, b - 1):
                p.px(xx, y - 1, SATIN[max(0, (5 if xx % 2 else 3) + k)])
        x = b


# --------------------------------------------------------------------------- the footers
FOOT_RISE = 5     # the rows the skirting along a footer's foot rises by where the cells leave it room
FOOT_RUN = 18     # the fewest columns it rises along
FOOT_LEAST = 12   # the fewest columns any stretch of it runs along between words


def lamp_mark(p: Pix, x, y, night, L="base"):
    """A banker's lamp, 11 wide and 10 tall, its top-left at (x, y): the ornament in the corner of a title block's
    notes. Its brass foot and stem and its shade of green glass, which by night burns the hand's phosphor, flickering,
    and glows round it."""
    k = -2 if night else 0
    F = p.flicker(1) if night else L
    tone = (FLAME[6], FLAME[5], FLAME[4], FLAME[3]) if night else (FLAME[3], FLAME[2], FLAME[2], FLAME[1])
    for i, (dy, a, b) in enumerate(((0, 2, 9), (1, 1, 10), (2, 0, 11), (3, 0, 11))):
        for xx in range(a, b):
            p.px(x + xx, y + dy, tone[min(3, i + (1 if xx > 7 else 0))], F)
    p.hline(x, x + 11, y + 4, BRASS[max(0, 4 + k)])
    p.vline(x + 5, y + 5, y + 9, BRASS[max(0, 5 + k)])
    p.vline(x + 6, y + 5, y + 9, BRASS[max(0, 2 + k)])
    p.px(x + 8, y + 5, BRASS[max(0, 5 + k)])
    p.px(x + 8, y + 6, BRASS[max(0, 3 + k)])
    p.hline(x + 1, x + 10, y + 9, BRASS[max(0, 3 + k)])
    p.px(x, y + 9, BRASS[1])
    if night:
        p.halo(x + 5.5, y + 4, 8, 4, FLAME[3], (0.08, 0.16), L=p.flicker(1, back=True))


def footing(p: Pix, night: bool, after=0):
    """A footer once its words are set: a skirting board of carved mahogany along its foot on the chesterfield roll
    the frame lays there, its moulding lit along its top over a shadowed groove, its face panelled, as tall as keeps a
    row clear of the words over each column (and none under a word that comes down to the roll), and a course taller
    wherever the cells leave it room along FOOT_RUN columns or more; and at the rightmost place from column `after` on
    where the cells leave the wall free, the open box with the two pills standing on it (see `pill_box`), the banker's
    lamp beside it where there is room, its green glass lit by night (see `lamp_mark`)."""
    w, h = p.w, p.h
    k = -2 if night else 0
    foot = h - EDGE
    ledge = foot - 6
    base = p.layers["base"]

    def lowest(x):
        return max((b[3] + 1 for b in p.words if b[0] - 1 <= x < b[2] + 1), default=0)

    def free(x0, y0, x1, y1):
        return 5 <= x0 and x1 <= w - 5 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0 - 1, x1 + 1) for y in range(y0, y1))
    mark, lamp = None, False
    for mw, lit in ((34, True), (21, False)):
        mark = next((x for x in range(w - 6 - mw, max(EDGE + 1, after) - 1, -1) if free(x, ledge - 15, x + mw, ledge)),
                    None)
        if mark is not None:
            lamp = lit
            break
    taken = (mark - 2, mark + (36 if lamp else 23)) if mark is not None else (0, 0)
    tops = [max(ledge, lowest(x) + 1) for x in range(w)]
    rise = [x not in range(*taken) and tops[x] == ledge and free(x, ledge - FOOT_RISE - 1, x + 1, ledge)
            for x in range(w)]
    x = EDGE
    while x < w - EDGE:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - EDGE) if not rise[i]), w - EDGE)
        if b - x >= FOOT_RUN:
            tops[x:b] = [ledge - FOOT_RISE] * (b - x)
        x = b
    x = EDGE
    while x < w - EDGE:             # no stub narrower than FOOT_LEAST between words that come down to the foot
        if tops[x] > foot - 2:
            x += 1
            continue
        b = next((i for i in range(x, w - EDGE) if tops[i] > foot - 2), w - EDGE)
        if b - x < FOOT_LEAST:
            tops[x:b] = [foot] * (b - x)
        x = b
    runs, x = [], EDGE
    while x < w - EDGE:
        t = tops[x]
        b = next((i for i in range(x, w - EDGE) if tops[i] != t), w - EDGE)
        if t <= foot - 2:
            runs.append((x, b, t))
        x = b

    def W(t):
        return WOOD[max(0, min(6, t + k))]
    for a, b, t in runs:
        p.hline(a, b, t, W(5))
        if t + 1 < foot - 1:
            p.hline(a, b, t + 1, W(3))
        if t + 2 < foot - 1:
            p.hline(a, b, t + 2, W(1))
        if foot - 1 - (t + 3) > 0:
            for yy in range(t + 3, foot - 1):
                p.hline(a, b, yy, W(3))
            for xx in range(a + 9 - a % 9, b, 37):
                p.vline(xx, t + 3, foot - 1, W(1))
                p.vline(xx + 1, t + 3, foot - 1, W(4))
        p.hline(a, b, foot - 1, W(1))
    for x in range(EDGE + 1, w - EDGE):
        a, b = tops[x - 1], tops[x]
        if a != b and min(a, b) <= foot - 2:
            for y in range(min(a, b), min(foot, max(a, b))):
                p.px(x if b < a else x - 1, y, W(4) if b < a else W(1))
    if mark is not None:
        if lamp:
            lamp_mark(p, mark, ledge - 10, night)
        pill_box(p, mark + (13 if lamp else 0), ledge - 2, night, False)


# --------------------------------------------------------------------------- the elements' pieces
LAMP_SMALL = [".LLLLL.", "LLLLLLl", "lllllll", "...b...", "...b...", ".bbbbb."]   # a banker's lamp, seven by six


def lamp_small(p: Pix, x, y, night):
    """A small banker's lamp, seven by six, its top-left at (x, y): its brass stem and foot and its shade of green
    glass, burning the hand's phosphor by night, flickering."""
    k = -2 if night else 0
    glass = {"L": FLAME[6] if night else FLAME[3], "l": FLAME[4] if night else FLAME[1]}
    p.sprite(x, y, LAMP_SMALL[:3], glass, 1, p.flicker(1) if night else "base")
    p.sprite(x, y, LAMP_SMALL, {"b": BRASS[max(0, 4 + k)]})


def nail(p: Pix, x, y, night, L="base"):
    """An upholsterer's brass nail, two pixels square at (x, y), its domed head lit on its upper left."""
    k = -1 if night else 0
    p.px(x, y, BRASS[6 + k], L)
    p.px(x + 1, y, BRASS[4 + k], L)
    p.px(x, y + 1, BRASS[4 + k], L)
    p.px(x + 1, y + 1, BRASS[1], L)


def boss(p: Pix, cx, cy, night):
    """A domed brass boss centred on (cx, cy), the hub a dial's hand turns on."""
    sphere(p, cx + 0.5, cy + 0.5, 2.6, BRASS, lo=1 if night else 2, hi=5 if night else 6, spec=True)


def brass_ring(p: Pix, path, rad, night, nails=()):
    """A band of polished brass along `path`, lit where it turns to the light, outlined dark, a nail at each point of
    `nails`."""
    k = -1 if night else 0

    def colour(s_, o, lam, x, y):
        return BRASS[max(1, min(6, round(1.2 + 4.8 * lam) + k))]
    tube(p, path, rad, colour, outline=BRASS[0])
    for (x, y) in nails:
        nail(p, round(x) - 1, round(y) - 1, night)


def leather_ring(p: Pix, path, rad, night, nails=()):
    """A roll of oxblood leather along `path`, padded and lit where it turns to the light, close-nailed in brass at
    each point of `nails`."""
    k = -1 if night else 0

    def colour(s_, o, lam, x, y):
        return OX[max(1, min(6, round(1.3 + 4.4 * lam) + k))]
    tube(p, path, rad, colour, outline=OX[0])
    for (x, y) in nails:
        nail(p, round(x) - 1, round(y) - 1, night)


def gel_bar(p: Pix, bx, base, bw, v, night):
    """A week's commits as a stick of the title's candy-red gel stood up on the base line: its rounded top, its lit
    left edge and the streak of light down it (by night the lamp's green), its dark underside down its right."""
    if v <= 0:
        return
    streak = FLAME[6] if night else C["white"]
    for xx in range(bw):
        t = 4 if xx == 0 else 3 if xx < bw - 1 else 1
        c = CANDY[t]
        if bw > 3 and xx == 1:
            c = streak
        top = base - v + (1 if (xx in (0, bw - 1) and v > 2 and bw > 2) else 0)
        p.vline(bx + xx, top, base, c)
    p.hline(bx, bx + bw, base - 1, CANDY[1])


def pill_drop(p: Pix, x, y, night, ramp=None):
    """A small pill, five by three, its top-left at (x, y): the red one, unless `ramp` names the blue's."""
    r = ramp or CANDY
    p.hline(x + 1, x + 4, y, r[4])
    p.px(x + 1, y, C["white"])
    p.hline(x, x + 5, y + 1, r[3])
    p.hline(x + 1, x + 4, y + 2, r[1])


def tassel(p: Pix, x, y, night, big=False, ramp=None):
    """A tassel hung from a curtain ring at (x, y): the brass ring, the knotted head and the fringe, in the curtains'
    velvet or the red of `ramp`, longer when `big`."""
    k = -1 if night else 0
    r = ramp or VELVET
    p.px(x - 1, y, BRASS[5 + k])
    p.px(x + 1, y, BRASS[3 + k])
    p.px(x, y + 1, BRASS[4 + k])
    p.hline(x - 1, x + 2, y + 2, r[4 + k])
    n = 5 if big else 3
    for j in range(n):
        p.px(x - 1, y + 3 + j, r[5 + k] if j % 2 == 0 else r[3 + k])
        p.px(x, y + 3 + j, r[4 + k])
        p.px(x + 1, y + 3 + j, r[2 + k])
    if big:
        p.px(x - 2, y + 3 + n - 1, r[3 + k])
        p.px(x + 2, y + 3 + n - 1, r[1 + k])


def curtain_rod(p: Pix, x0, x1, y, night):
    """A brass curtain rod the releases hang from, up to today: three rows of brass, lit along its top, a finial at
    its start."""
    k = -1 if night else 0
    p.hline(x0, x1, y - 1, BRASS[6 + k])
    p.hline(x0, x1, y, BRASS[4 + k])
    p.hline(x0, x1, y + 1, BRASS[1])
    sphere(p, x0 - 1, y + 0.5, 1.8, BRASS, lo=1, hi=5 if night else 6, spec=False)


# A Sentinel, the machine that hunts the ships, seven by six, for a bot: its dark carapace (k), its red eyes (R).
SENTINEL = [".kkkkk.", "kkRkRkk", "kkkkkkk", ".k.k.k.", "k..k..k", "k..k..k"]


def face(p: Pix, cx, cy, i, person, night):
    """A contributor in the room's manner, a portrait fifteen units square centred on (cx, cy): the damask behind
    them, their hair and their face on one of the hand's skins, round dark glasses over their eyes, a long dark coat at
    their shoulders and their initials on it; a bot is one of the machines, its red eyes burning."""
    k = -1 if night else 0
    x0, y0 = cx - 7, cy - 7
    p.rect(x0, y0, 15, 15, WINE[4] if night else ROSE[3])
    for (dx, dy) in ((3, 3), (11, 3), (7, 7), (3, 11), (11, 11)):
        p.px(x0 + dx, y0 + dy, WINE[6] if night else ROSE[5])
    p.box(x0 - 1, y0 - 1, 17, 17, BRASS[3 + k])
    if not person.get("initials"):
        p.sprite(x0 + 4, y0 + 4, SENTINEL, {"k": NIGHT[1], "R": CANDY[4]})
        return
    skin = RAMP[("skin0", "skin1", "skin2")[i % 3]]
    hair = (WOOD[0], WOOD[2], NIGHT[1], WOOD[4])[i % 4]
    for yy in range(y0 + 1, y0 + 9):
        for xx in range(x0 + 4, x0 + 11):
            dx, dy = xx - (x0 + 7), yy - (y0 + 5)
            if dx * dx / 10 + dy * dy / 14 > 1:
                continue
            c = skin[4] if dx < 1 else skin[3]
            if yy <= y0 + 2 or (yy <= y0 + 5 and abs(dx) == 3):
                c = hair
            p.px(xx, yy, c)
    for ex in (x0 + 5, x0 + 8):
        p.hline(ex, ex + 2, y0 + 5, NIGHT[1])
    p.px(x0 + 7, y0 + 5, NIGHT[2])
    for yy in range(y0 + 9, y0 + 15):
        for xx in range(x0 + max(1, 4 - (yy - y0 - 9)), x0 + min(14, 11 + (yy - y0 - 9))):
            p.px(xx, yy, NIGHT[2] if xx > x0 + 7 else NIGHT[4 + k])
    ini = str(person["initials"])[:2]
    p.text(cx - measure(ini, "35") // 2, y0 + 10, ini, SATIN[6], "35")


def gel_fill(p: Pix, x, y, w, fill, night):
    """A contributor's share as a capsule of the candy-red gel in a brass rim: filled along `fill` of its length, lit
    along its top (by night the lamp's green), the rest of the rim empty and dark."""
    p.box(x, y, w + 2, 4, BRASS[3] if not night else BRASS[2])
    lit = FLAME[5] if night else CANDY[5]
    for xx in range(w):
        full = xx < fill
        p.px(x + 1 + xx, y + 1, lit if full else (WINE[2] if night else ROSE[3]))
        p.px(x + 1 + xx, y + 2, CANDY[3] if full else (WINE[1] if night else ROSE[2]))


# --------------------------------------------------------------------------- the footers', links' and badges' sprites
# The link buttons' icons, seven by seven, things of the room: the red pill and the blue, the cracked mirror, the
# banker's lamp, the glass of water and the umbrella. Each letter is looked up in `icon_pal`.
ICONS = {
    "red pill": ["....oo.", "...oHRo", "..oHRRo", ".oRRRo.", "oRRRo..", "oRRo...", ".oo...."],
    "blue pill": ["....oo.", "...oHBo", "..oHBBo", ".oBBBo.", "oBBBo..", "oBBo...", ".oo...."],
    "mirror": ["..ggg..", ".gsssg.", ".gsCsg.", ".gssCg.", ".gsssg.", "..ggg..", "...g..."],
    "lamp": ["..LLL..", ".LLLLL.", "lLLLLLl", "...b...", "...b...", "..bbb..", ".bbbbb."],
    "glass": [".s...s.", ".swwws.", ".swwws.", ".swwws.", "..sws..", "..sss..", "......."],
    "umbrella": ["..UUU..", ".UUUUU.", "UUUUUUU", "...h...", "...h...", ".h.h...", "..h...."],
}
LINK_ICONS = ("red pill", "blue pill", "mirror", "lamp", "glass", "umbrella")


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones: the pills' gel, the mirror's gilt and glass, the lamp's green glass on its brass, the glass
    and its water and the umbrella's black silk, a step deeper by night, when the lamp's shade burns the hand's
    phosphor."""
    k = -1 if night else 0
    return {"o": CANDY[0] if not night else OX[0], "H": CANDY[6], "R": CANDY[3], "B": BLUE[3 + k],
            "g": BRASS[4 + k], "s": GLASS[4 + k], "C": C["white"], "L": FLAME[4] if night else VELVET[4],
            "l": FLAME[2] if night else VELVET[2], "b": BRASS[4 + k], "w": GLASS[5 + k], "U": NIGHT[3],
            "h": WOOD[4 + k], "#": ink}


def heart(p: Pix, x, y, L="base"):
    """A heart of the candy-red gel the title is made of, seven by six, a streak of light across its upper-left
    lobe."""
    art = [".53.43.", "5644432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): CANDY[i] for i in range(7)}, 1, L)

