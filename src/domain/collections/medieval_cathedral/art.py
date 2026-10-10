# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Cathedral set's scenery and sprites, drawn on the shared pixel canvas.

The leaded window the sheet is glazed with, the stone of its frame and the string course its sill and its rules are
carved as, the frieze of glazed quatrefoils across a header's top and the gargoyles on its corners, the rose window, the
lancets with their saints on their sills, the great window that holds three of them under one arch, the altar and its
candles, the shaft of sun of the day and the owl and the candlelit glass of the night, letters glazed in coloured glass
and leaded in black with the gleam that crosses them, the marks a footer ends in, and the glass, stone and lead every
element and badge is made of. Its candles burn on the collection's hand's flame. Everything is shaded from the one light
in the upper left on the set's own ramps, and drawn in the fewest bytes that draw it exactly (see "drawing in few
bytes"), so the longest page keeps its whole scene and its motion within the budget: a drawing made lighter to fit thins
only texture, the glints on a rose's petals, the faintest ring of each pool of light and the window's faintest cast."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, Pix, fold, num
from .palette import C, GLAZES, HAND, NIGHT_SKY, RAMP, STONE, X

D = 12            # a quarry's width and height: the lattice's diagonals meet every twelve pixels
ARCH = 10         # the pitch of the arcade along a sheet's top edge
TOP, FOOT = 5, 5  # the rows the arcade and the sill take


def stone_ramp(night: bool) -> list:
    """The tracery's tones: pale limestone by day, the same stone by candlelight at night."""
    return RAMP["dusk" if night else "stone"]


def glaze_tones(glaze: str, night: bool) -> tuple:
    """A glass's tones (against the lead, its body, where it runs thin) by day, with the sun behind it, and by
    night, lit from inside: amber is glazed deeper by day so a letter of it still reads on the pale panes."""
    R = RAMP[glaze]
    if night:
        body = 5 if glaze in ("ruby", "cobalt") else 4
    else:
        body = 2 if glaze == "amber" else 3
    return R[max(0, body - 2)], R[body], R[min(6, body + 2)]


# --------------------------------------------------------------------------- drawing in few bytes
# A header's art is pixels, and a pixel costs bytes: a run of one colour along a row is a few, a lone pixel of a
# thin line (a lead spoke, a lattice's diagonal) nearly as many. So the set lays the colour of a sprite's thin lines
# as one ground under the whole of it and draws its pieces over that, lays a texture that repeats as a pattern,
# and writes every ground the shorter way, along its rows or down its columns. Every one of these is exact: the
# picture is the one the pixels would have made.
def _paths(cols: dict) -> str:
    """Paths for {colour or colour:alpha: {y: [x, ...]}}."""
    out = []
    for c, rows in cols.items():
        if not rows:
            continue
        if ":" in c:
            col, a = c.split(":")
            out.append(f'<path stroke="{col}" stroke-opacity="{a}" d="{Pix._d(rows)}"/>')
        else:
            out.append(f'<path stroke="{c}" d="{Pix._d(rows)}"/>')
    return "".join(out)


def _rows(cells) -> dict:
    """`cells` as {y: [x, ...]}, the rows `Pix._d` writes."""
    rows: dict = {}
    for (x, y) in cells:
        rows.setdefault(y, []).append(x)
    return rows


def _d(cells) -> str:
    """Path data for `cells`, as runs along the rows (the way `Pix._d` writes a layer's pixels) or as runs down the
    columns, whichever is the shorter: a tall, narrow shape like a lancet's glass is a few strokes down."""
    cols: dict = {}
    for (x, y) in cells:
        cols.setdefault(x, []).append(y)
    across = Pix._d(_rows(cells))
    out, at = [], None
    for x in sorted(cols):
        ys = sorted(cols[x])
        start = ys[0]
        for i, y in enumerate(ys):
            if i + 1 < len(ys) and ys[i + 1] == y + 1:
                continue
            sx, sy, n = x + 0.5, start, y - start + 1
            out.append(f"M{num(sx)} {num(sy)}v{n}" if at is None else f"m{num(sx - at[0])} {num(sy - at[1])}v{n}")
            at = (sx, sy + n)
            if i + 1 < len(ys):
                start = ys[i + 1]
    down = "".join(out).replace(" -", "-")
    return down if len(down) < len(across) else across


def _shape(paint: str, cells) -> str:
    """A ground as markup: a rectangle when its cells fill one, else a path of runs (see `_d`)."""
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if len(set(cells)) == (x1 - x0 + 1) * (y1 - y0 + 1):
        at = (f' x="{x0}"' if x0 else "") + (f' y="{y0}"' if y0 else "")
        return f'<rect{at} width="{x1 - x0 + 1}" height="{y1 - y0 + 1}" fill="{paint}"/>'
    return f'<path stroke="{paint}" d="{_d(cells)}"/>'


def _cost(cells: dict, ground=False) -> int:
    """The bytes `cells`, {(x, y): colour}, take as the pixels of a layer, a path a colour, or laid as grounds."""
    by: dict = {}
    for xy, c in cells.items():
        by.setdefault(c, []).append(xy)
    if ground:
        return sum(len(_shape(c, xys)) for c, xys in by.items())
    return sum(len(Pix._d(_rows(xys))) + 22 for xys in by.values())


def _plan(colours: dict, plans) -> tuple:
    """The cheapest way to draw `colours` of the `plans` offered and every cell a pixel (see `paint`): its grounds,
    (paint, cells), and the cells left to draw as pixels."""
    best = (_cost(colours), [], colours)
    for plan in plans:
        shown, grounds = {}, []
        for what, cells in plan:
            paint_, tone = what if isinstance(what, tuple) else (what, None)
            cells = [xy for xy in cells if xy in colours]
            if not cells:
                continue
            grounds.append((paint_, cells))
            shown.update({xy: tone(xy) for xy in cells} if tone else dict.fromkeys(cells, paint_))
        rest = {xy: c for xy, c in colours.items() if shown.get(xy) != c}
        cost = _cost(rest) + sum(_cost(dict.fromkeys(cells, col), ground=True) for col, cells in grounds)
        if cost < best[0]:
            best = (cost, grounds, rest)
    return best[1], best[2]


def _markup(cells: dict, plans=None) -> str:
    """`cells`, {(x, y): colour}, as the markup of a symbol or a pattern tile, in the fewest bytes of the `plans`
    offered (see `paint`), or with no plans given of each solid colour tried as a ground under the whole."""
    if plans is None:
        plans = [[(c, list(cells))] for c in sorted(set(cells.values())) if ":" not in c]
    grounds, rest = _plan(cells, plans)
    by: dict = {}
    for (x, y), c in rest.items():
        by.setdefault(c, {}).setdefault(y, []).append(x)
    return "".join(_shape(paint_, xys) for paint_, xys in grounds) + _paths(by)


def _ground(p: Pix, cells, paint: str, L="base"):
    """Lay `paint` (a colour, or a pattern's url) on `cells` in place of whatever pixels lay there, as one shape
    (see `_shape`) under the layer's pixels, so what is drawn over the cells later still lies over them. The canvas
    keeps what each cell was laid with (`ground_at`)."""
    p.layer(L)
    if not hasattr(p, "grounds"):
        p.grounds = {}
    if not cells:
        return
    for xy in cells:
        p.layers[L].pop(xy, None)
        p.grounds[xy] = paint
    p.shapes[L].append(_shape(paint, cells))


def ground_at(p: Pix, x, y):
    """The colour a cell of the drawing shows on the base layer: its pixel, or what it was laid with."""
    return p.get(x, y) or getattr(p, "grounds", {}).get((x, y))


def paint(p: Pix, colours: dict, plans=(), L="base"):
    """Paint a sprite, {(x, y): colour}, in the fewest bytes of the ways offered. A plan is a list of grounds,
    (paint, cells), each laid in turn as one shape under the layer's pixels (see `_ground`), a paint being a colour
    or a pattern's url with the colour it shows at each cell, (url, tone); a pixel then goes only where the grounds
    leave a colour other than the one wanted. Painting every cell as a pixel is always offered. Whichever way wins,
    what shows is the sprite: a ground is the colour of the thin lines a sprite is drawn in, its lead or its
    outline, laid under the whole of it, so those lines cost nothing and the sprite's pieces are drawn over it
    whole."""
    grounds, rest = _plan(colours, plans)
    p.layer(L)
    for xy in colours:
        p.layers[L].pop(xy, None)
    for paint_, cells in grounds:
        _ground(p, cells, paint_, L)
    for (x, y), c in rest.items():
        p.px(x, y, c, L)


def _tile(p: Pix, key, n, x, y, tone) -> str:
    """A pattern `n` pixels square repeating from (x, y), whose pixel `i` across and `j` down is `tone(i, j)`,
    made once a file. Returns its id."""
    if key not in p.syms:
        pid = f"w{len(p.syms)}"
        p.defs.append(f'<pattern id="{pid}" x="{x % n}" y="{y % n}" width="{n}" height="{n}" '
                      f'patternUnits="userSpaceOnUse">'
                      f'{_markup({(i, j): tone(i, j) for j in range(n) for i in range(n)})}</pattern>')
        p.syms[key] = pid
    return p.syms[key]


# --------------------------------------------------------------------------- the paper
def _quarries(uid: str, night: bool, lite: bool = False) -> str:
    """The leaded window as two pattern tiles: diamond quarries in a lattice of cames, a streak along each pane's
    upper left where the glass runs thin, the same in every quarry and so a tile 12 by 12 (`{uid}q`); and each pane
    cast a little differently from its neighbours, with a seed in the odd one, a tile 24 by 24 (`{uid}c`). No pixel
    lies in both. By day the panes are grisaille with the daylight behind them; by night the cames are black and
    the panes take the candlelight, but for the faintest cast, which a drawing made lighter (`lite`) leaves out."""
    T = 2 * D
    lattice: dict = {}
    panes: dict = {}

    def put(tile, c, x, y):
        tile.setdefault(c, {}).setdefault(y, []).append(x)
    came = C["came_n"] if night else C["came"]
    for y in range(T):
        for x in range(T):
            u, v = (x + y) % D, (x - y) % D
            if u == 0 or v == 0:
                if x < D and y < D:
                    put(lattice, came, x, y)
                continue
            pane = ((x + y) // D + 2 * ((x - y + T) // D)) % 4
            if u == 2 and 3 <= v <= 7:
                if x < D and y < D:
                    put(lattice, f"{RAMP['candle'][5]}:.16" if night else C["white"], x, y)
            elif u == 6 and v == 7 and pane in (1, 3):
                put(panes, f"{X['pane_dim']}:.5" if night else RAMP["grisaille"][3], x, y)
            elif night:
                if pane == 1 and not lite:
                    put(panes, f"{RAMP['candle'][4]}:.05", x, y)
                elif pane == 3:
                    put(panes, f"{X['pane_dim']}:.3", x, y)
            elif pane:
                put(panes, (X["tint_sky"], X["tint_warm"], X["tint_cool"])[pane - 1], x, y)
    return (f'<pattern id="{uid}q" width="{D}" height="{D}" patternUnits="userSpaceOnUse">{_paths(lattice)}</pattern>'
            f'<pattern id="{uid}c" width="{T}" height="{T}" patternUnits="userSpaceOnUse">{_paths(panes)}</pattern>')


def band_edges(y: int, h: int) -> list:
    n = len(NIGHT_SKY)
    return [y + round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, x=0, y=None, w=None, h=None, uid="p"):
    """The ground a drawing sits on: the leaded window between the arcade along the top and the sill along the
    foot, grisaille quarries with the daylight behind them by day, and by night the same window lit from
    inside by candles, dim toward the top where the light does not reach and warmer toward the foot."""
    y = TOP if y is None else y
    w = p.w if w is None else w
    h = p.h - y - FOOT if h is None else h
    p.night = night          # what a hook told no theme (the scale's bar) reads to know which glass it is
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
    else:
        edges = band_edges(y, h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" '
                               f'fill="{col}"/>')
    p.defs.append(_quarries(uid, night, p.lite))
    for tile in "cq":
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}{tile})"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`."""
    if not night:
        return C["paper"]
    edges = band_edges(TOP, p.h - TOP - FOOT)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


# --------------------------------------------------------------------------- the night sky
def sparkle(p: Pix, x, y, L="base"):
    """A four-point star: a white heart, pale arms."""
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, X["star"], L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """The stars that show through the clear quarries by night: pinpricks, a few brighter, and now and then
    one with points. None inside a box in `avoid`."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.55 or faint:
            p.px(x, y, X["star_dim"], "haze")
        elif k < 0.9:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.5) else "haze"
            p.px(x, y, X["star"] if rnd.random() < 0.7 else RAMP["sky"][5], L)
        else:
            sparkle(p, x, y, L=p.twinkle(i, back=True) if twinkling else "haze")


# --------------------------------------------------------------------------- the frame
def _arcade(uid: str, S: list) -> str:
    """A pattern tile of the arcade along a sheet's top, 10 by 5: a dark edge, a lit coping with its joints, and
    a row of pointed arches cut dark into the stone under it."""
    cells: dict = {}
    for x in range(ARCH):
        cells[(x, 0)] = S[1]
        cells[(x, 1)] = S[6] if x % 5 else S[4]
        k = abs(x - 4)
        for y, reach in ((2, 0), (3, 1), (4, 2)):
            cells[(x, y)] = S[0] if k <= reach else S[3] if x == 9 else S[5] if k == reach + 1 and x < 4 else S[4]
    return (f'<pattern id="{uid}a" width="{ARCH}" height="{TOP}" patternUnits="userSpaceOnUse">{_markup(cells)}'
            f'</pattern>')


def _mullion(uid: str, S: list, night: bool) -> str:
    """A pattern tile of a stone mullion four pixels across: a dark edge, a lit roll, the shaft's face and its
    shaded side, with a joint every twelve rows."""
    cells: dict = {}
    tones = (0, 6, 4, 2)
    for y in range(12):
        for k, t in enumerate(tones):
            if y == 11 and k in (1, 2):
                t -= 1
            cells[(k, y)] = S[max(0, t)]
    return f'<pattern id="{uid}m" width="4" height="12" patternUnits="userSpaceOnUse">{_markup(cells)}</pattern>'


# The string course, the band of stone a sill and every rule is carved as, a tile 6 by 3: a moulding lit along
# its top and shaded under it, with a small quatrefoil cut into its face in every tile, its upper left in the
# shadow of the cut and its lower right catching the light, round a boss lit at its middle. Its digits are the
# stone's tones.
COURSE = ["661666", "416144", "220222"]


def _course(p: Pix, y: int, night: bool, uid: str = "sc") -> str:
    """The pattern a string course whose top is row `y` is cut from, made once a row and a file. Returns its
    id."""
    key = ("course", uid, y, night)
    if key not in p.syms:
        S = stone_ramp(night)
        cells = {(i, j): S[int(ch)] for j, row in enumerate(COURSE) for i, ch in enumerate(row)}
        pid = f"{uid}{y}"
        p.defs.append(f'<pattern id="{pid}" y="{y}" width="{len(COURSE[0])}" height="{len(COURSE)}" '
                      f'patternUnits="userSpaceOnUse">{_markup(cells)}</pattern>')
        p.syms[key] = pid
    return p.syms[key]


def string_course(p: Pix, x0, x1, y, night):
    """A string course of stone carved along the rule at row `y` from x0 to x1, standing on the rule (its foot is
    row `y`): a moulding lit along its top with a small quatrefoil cut into its face every six columns. It is
    three rows deep, and two under a word that comes within two units of its top; it leaves out what a word
    lies too near and the columns a scene stands on, whose foot it would otherwise cut."""
    pid = _course(p, y - 2, night)
    L = p.layer("course", z=0.4)
    runs: list = []
    for x in range(x0, x1):
        if any(ground_at(p, x, yy) for yy in (y - 3, y - 2, y - 1)):
            h = 0
        elif p.clear_of_words(x - 2, y - 4, x + 3, y + 3):
            h = 3
        elif p.clear_of_words(x - 2, y - 3, x + 3, y + 3):
            h = 2
        else:
            h = 0
        if runs and runs[-1][2] == h and runs[-1][1] == x:
            runs[-1][1] = x + 1
        else:
            runs.append([x, x + 1, h])
    for a, b, h in runs:
        if h:
            p.shapes[L].append(f'<rect x="{a}" y="{y + 1 - h}" width="{b - a}" height="{h}" fill="url(#{pid})"/>')


# A gargoyle crouched over a header's top left corner, 30 by 23, facing in: a bat's wing raised over its back
# with its bones lit, a horned head thrust out over the glass with its jaws open on a red throat and its fangs
# bared, a chest and a foreleg braced on a corbel of stone, its haunch tucked under and its tail hanging over the
# corbel's face to a barbed tip. `O` is the dark line round
# it, `h`, `l`, `m`, `d` and `D` its stone from lit to shaded, `w` the wing's skin and `b` its bones, `r` the throat,
# `t` a fang or a claw, `e` the eye, which glows by candlelight, and `C`, `c`, `s` the corbel. By day it stands
# dark against the pale glass. It keeps above row 14 wherever it reaches past column 12, and the corbel, its feet
# and its tail stay inside that column below, so no title, dimension or note a layout sets near a corner comes
# within two units of it, on either corner.
GARGOYLE = [
    ".......O...O........O..O......",
    ".O....OwO.ObO.......OhOOhO....",
    ".OO..OwwwOObO.......OlOOlO....",
    ".OwOOwwwwwwbO......OllllllO...",
    "..OwwwwwwwwbO.....OlhhllelOO..",
    "..OwwwwwwwbhO....OlhllmmmmlhdO",
    "...OwwwwwbhlOOOOOlhlmmmmmmmmmO",
    "...OwwwwbhllhhhhhlmmmmmmmmdddO",
    "..OOOwwbhllmmmmmmmmmmmmdOOOOOO",
    ".OhhhOOOlmmmmmmmmmmmmdOkrrrkO.",
    ".OhllhmmmmmmmmmmmmmmddOrrrrO..",
    ".OhlmhhmmmmmmmmmmmdddddOkrkO..",
    ".OlmhlmmmmODlmmmdddOOdddddO...",
    ".OlmlmmmmmODlmmdO....OOOOO....",
    ".OlmmmmmDOlmO.................",
    ".OlmmmmDDOlmO.................",
    ".OlmmmDDOOlmO.................",
    ".OlmmDDO.OlmO.................",
    ".OldDDO..OlmO.................",
    "..OkOkO..OkOk.................",
    "CCOlCCCCCCCCC.................",
    "cOlllOcccccc..................",
    "ssOlOsssss....................",
]
GW = len(GARGOYLE[0])
EYE = next((i, j) for j, row in enumerate(GARGOYLE) for i, ch in enumerate(row) if ch == "e")


def _gargoyle(p: Pix, night: bool):
    """The gargoyle drawn once a file, and its twin facing the other way, which reuses it mirrored."""
    key = ("gargoyle", night)
    if key not in p.syms:
        S, Ld = stone_ramp(night), RAMP["lead"]
        if night:
            pal = {"O": Ld[0], "D": Ld[0], "w": Ld[0], "b": S[5], "d": Ld[0], "m": Ld[1], "l": S[4], "h": S[6],
                   "k": S[6], "e": RAMP["candle"][5], "r": RAMP["ruby"][1], "C": S[6], "c": S[4], "s": S[2]}
        else:
            pal = {"O": Ld[1], "D": S[0], "w": S[0], "b": S[3], "d": S[0], "m": S[1], "l": S[2], "h": S[3],
                   "k": S[6], "e": S[6], "r": RAMP["ruby"][1], "C": S[6], "c": S[4], "s": S[2]}
        sid = p.symbol(key, {}, shapes=_markup({(i, j): pal[ch] for j, row in enumerate(GARGOYLE)
                                                for i, ch in enumerate(row) if ch != "."}))
        p.symbol(("gargoyle-twin", night), {}, shapes=f'<use href="#{sid}" transform="matrix(-1 0 0 1 {GW} 0)"/>')
    return key, ("gargoyle-twin", night)


def gargoyles(p: Pix, night: bool):
    """A gargoyle on each top corner of a header, the one on the right its twin facing the other way, and by
    night their eyes glowing with the candlelight, flickering in a moving file."""
    left, right = _gargoyle(p, night)
    p.use(left, 0, 0)
    p.use(right, p.w - GW, 0)
    if night:
        F = RAMP["candle"]
        for i, x in enumerate((EYE[0], p.w - 1 - EYE[0])):
            L = p.flicker(i)
            p.px(x, EYE[1], F[6], L)
            p.halo(x + 0.5, EYE[1] + 0.5, 2.6, 2.2, F[4], (0.14, 0.3), L=L)


def frame(p: Pix, night: bool, gargoyles: bool = False, x=0, y=0, w=None, h=None, uid="fr"):
    """The sheet's border in gothic stone: an arcade of pointed arches along the top, a mullion down each side
    and a sill along the foot with a band of quatrefoils cut into it; a footer, the one short sheet, stands on
    a step over the sill. A header's gargoyles are set on its corners by `frieze`, over the band."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    S = stone_ramp(night)
    p.defs.append(_mullion(uid, S, night))
    for bx in (x, x + w - 4):
        p.shapes["base"].append(f'<rect x="{bx}" y="{y + TOP}" width="4" height="{h - TOP - FOOT}" '
                                f'fill="url(#{uid}m)"/>')
    p.defs.append(_arcade(uid, S))
    p.shapes["base"].append(f'<rect x="{x}" y="{y}" width="{w}" height="{TOP}" fill="url(#{uid}a)"/>')
    for xx in range(x + 4, x + w - 4):
        p.apx(xx, y + TOP, X["shade_ink"], 0.2, "base")
    ledge = y + h - FOOT
    p.hline(x, x + w, ledge, S[6])
    sill = _course(p, ledge + 1, night, uid=f"{uid}s")
    p.shapes["base"].append(f'<rect x="{x}" y="{ledge + 1}" width="{w}" height="3" fill="url(#{sill})"/>')
    p.hline(x, x + w, y + h - 1, S[1])
    if h < 60:
        # A footer stands on a step: a course of stone proud of the window over the sill, its shadow above it.
        for xx in range(x, x + w):
            p.px(xx, ledge - 1, S[3] if (xx - x) % 12 == 7 else S[5])
        for xx in range(x + 4, x + w - 4):
            p.apx(xx, ledge - 2, X["shade_ink"], 0.18, "base")
    else:
        for xx in range(x + 4, x + w - 4):
            p.apx(xx, ledge - 1, X["shade_ink"], 0.14, "base")


# --------------------------------------------------------------------------- the frieze
# One bay of the frieze across a header's top, 14 by 12 from the row under the coping: a panel of stone in the
# coping's shadow along its top and lit along its foot, a quatrefoil pierced through it whose four lobes are
# glazed in cobalt set straight into the stone, a roundel of ruby leaded in at its middle, and a rib to the next
# bay. `1`-`6` are stone, dark where the light cannot reach an arris and lit where it can; `g`, `G` and `q` the
# cobalt's body, its streak where it runs thin and its dark edge; `L` the lead; `r` the ruby and `*` the spot on
# it where a glint twinkles.
FRIEZE = [
    "22222222222221",
    "444441Gq344443",
    "44441Gggq64443",
    "44411Gggq31443",
    "441GGgLLgGq343",
    "41GggL*rLggq63",
    "41qggLrrLggq63",
    "443qqgLLgqq643",
    "44463Gggq66443",
    "44441qggq64443",
    "444443qq644443",
    "55555555555555",
]
BAY = len(FRIEZE[0])
GLINT = next((i, j) for j, row in enumerate(FRIEZE) for i, ch in enumerate(row) if ch == "*")
FRIEZE_TOP = 2    # the frieze hangs from the coping, over the arcade's own arches


def _frieze_bays(p: Pix, night: bool, x0: int) -> str:
    """The bay as a pattern that repeats along the frieze from column `x0`, made once a file. Returns its id."""
    key = ("frieze", night, x0)
    if key not in p.syms:
        S = stone_ramp(night)
        dark, body, thin = glaze_tones("cobalt", night)
        pal = {str(k): S[k] for k in range(7)}
        pal.update({"g": body, "G": thin, "q": dark, "L": RAMP["lead"][0 if night else 1],
                    "r": glaze_tones("ruby", night)[1], "*": glaze_tones("ruby", night)[2]})
        pid = f"fz{'n' if night else 'd'}"
        p.defs.append(f'<pattern id="{pid}" x="{x0}" y="{FRIEZE_TOP}" width="{BAY}" height="{len(FRIEZE)}" '
                      f'patternUnits="userSpaceOnUse">'
                      f'{_markup({(i, j): pal[ch] for j, row in enumerate(FRIEZE) for i, ch in enumerate(row)})}'
                      f'</pattern>')
        p.syms[key] = pid
    return p.syms[key]


def bay_layout(w: int) -> tuple:
    """Where the frieze's bays lie across a header `w` wide: the first one's column and how many there are. They
    are laid out from the top centre, a whole bay under the month's mark and as many whole bays to either side as
    the gargoyles leave room for, so the mark covers the middle bay's quatrefoil whole and cuts none."""
    mid = w // 2 - BAY // 2
    k = (mid - GW) // BAY
    return mid - k * BAY, 2 * k + 1


def frieze(p: Pix, night, seed=0):
    """The tracery across a header's top, between the gargoyles crouched on its corners: a band of stone hung
    from the coping, pierced with a quatrefoil in every bay, each glazed in cobalt round a roundel of ruby, and
    a glint on each roundel that twinkles in a moving header. The bays are laid out from the top centre (see
    `bay_layout`); the band's ends, where whole bays leave a few columns over, are plain stone."""
    x0, n = bay_layout(p.w)
    S = stone_ramp(night)
    for xx in list(range(GW, x0)) + list(range(x0 + n * BAY, p.w - GW)):
        edge = xx in (GW, p.w - GW - 1)
        for j in range(len(FRIEZE)):
            c = S[2] if j == 0 else S[5] if j == len(FRIEZE) - 1 else S[1] if edge else S[4]
            p.px(xx, FRIEZE_TOP + j, c)
    bays = _frieze_bays(p, night, x0)
    p.shapes[p.layer("frieze", z=0.05)].append(f'<rect x="{x0}" y="{FRIEZE_TOP}" width="{n * BAY}" '
                                               f'height="{len(FRIEZE)}" fill="url(#{bays})"/>')
    for i in range(n):
        p.px(x0 + i * BAY + GLINT[0], FRIEZE_TOP + GLINT[1], C["white"], p.twinkle(i + seed))
    gargoyles(p, night)


# --------------------------------------------------------------------------- the glazed title
def _glass_finish(dark: str, thin: str, scale: int):
    """The finish over a letter of glass: a dark rim where the glass meets its lead (all round at the largest
    size, along the shaded edges at the next, none where a stroke is two pixels wide) and a streak where the
    glass runs thin, from the lower left up to the right."""
    def finish(p: Pix, cells, s, L, rnd, y0):
        x0 = min(x for x, _ in cells)
        streak = 5 * scale
        for (gx, gy) in cells:
            rim = False
            if scale >= 4:
                rim = any((gx + dx, gy + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            elif scale == 3:
                rim = (gx + 1, gy) not in cells or (gx, gy + 1) not in cells
            if rim:
                p.px(gx, gy, dark, L)
            elif (gx - x0) + (gy - y0) in range(streak, streak + max(1, scale // 2)):
                p.px(gx, gy, thin, L)
    return finish


def _came_symbol(p: Pix, ch: str):
    """The came round a letter, drawn once a glyph: the glyph grown a pixel every way, as one path the lead
    is stroked in, placed under the letter's own path."""
    key = ("came", "57", ch)
    if key not in p.syms:
        g = FONTS["57"][0][ch]
        ink = {(col, r) for r, cols in enumerate(g[1]) for col in cols}
        grown = set(ink)
        for (col, r) in ink:
            grown.update(((col + 1, r), (col - 1, r), (col, r + 1), (col, r - 1)))
        p.symbol(key, {q: 1 for q in grown}, mono=True)
    return key


def _regroup(p: Pix, L: str, start: int, z: float):
    """The symbols placed on layer `L` since its `start`-th use, written again more briefly on a layer of their own
    at depth `z`, just over `L`: the uses set at one height and size share one translate and scale, each placed by
    its x alone in the symbol's own units, and the uses of each colour share one group, in the order they were laid.
    Drawn the same, at about half the bytes of a translate and a scale on every use."""
    uses = p.uses[L][start:]
    if not uses:
        return
    del p.uses[L][start:]
    rows: dict = {}
    for stroke, sid, x, y, scale in uses:
        rows.setdefault((y, scale), {}).setdefault(stroke, []).append((x, sid))
    out = []
    for (y, scale), strokes in rows.items():
        x0 = min(x for placed in strokes.values() for x, _ in placed)
        size = f" scale({scale})" if scale != 1 else ""
        out.append(f'<g transform="translate({num(x0)} {num(y)}){size}">')
        for stroke, placed in strokes.items():
            inner = "".join(f'<use href="#{sid}"' + (f' x="{num((x - x0) / scale)}"' if x != x0 else "") + "/>"
                            for x, sid in placed)
            col, _, a = (stroke or "").partition(":")
            attrs = f' stroke="{col}"' + (f' stroke-opacity="{num(float(a))}"' if a else "") if stroke else ""
            out.append(f"<g{attrs}>{inner}</g>")
        out.append("</g>")
    p.shapes[p.layer(f"{L}=", z=z)].append("".join(out))


def glass_title(p: Pix, x, y, s, night, scale, L="base") -> int:
    """A title whose every letter is a pane of coloured glass, ruby, cobalt, emerald and amber by turns, leaded
    in black: a came a pixel wide round each letter, a dark rim where the glass meets it, a streak where the
    glass runs thin, and by night the candlelight behind the glass, which glows. A drawing made lighter to fit its
    budget keeps all of it: the glass is the title's treatment, not its texture. Returns the width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    came = RAMP["lead"][1 if night else 0]
    p.layer(L)
    marks = {name: len(p.uses[name]) for name in (L, "haze")}
    lite, p.lite = p.lite, False
    cx, i, letters = x, 0, []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        dark, body, thin = glaze_tones(GLAZES[i % len(GLAZES)], night)
        p.use(_came_symbol(p, ch), cx, y, L, stroke=came, scale=scale)
        kw = dict(finish=_glass_finish(dark, thin, scale))
        if night and scale >= 2:
            kw["glow"] = (thin, (0.1, 0.22) if scale >= 3 else (0.16,))
        p.text(cx, y, ch, body, "57", scale, L, **kw)
        letters.append((ch, cx, body))
        cx += (g[0] + 1) * scale
        i += 1
    p.lite = lite
    # A letter that comes three times or more on the line is placed as its came and its glass at once: one symbol
    # with the came stroked in lead inside it and the glass taking the colour of the group it is placed in.
    del p.uses[L][marks[L]:]
    often = {ch for ch, _, _ in letters if sum(c == ch for c, _, _ in letters) >= 3}
    for ch, lx, _ in letters:
        if ch not in often:
            p.use(_came_symbol(p, ch), lx, y, L, stroke=came, scale=scale)
    for ch, lx, body in letters:
        came_key, glyph_key = _came_symbol(p, ch), ("glyph", "57", ch)
        if ch in often:
            both = ("glass", ch, came)
            if both not in p.syms:
                p.symbol(both, {}, shapes=f'<use href="#{p.syms[came_key]}" stroke="{came}"/>'
                                          f'<use href="#{p.syms[glyph_key]}"/>')
            glyph_key = both
        p.use(glyph_key, lx, y, L, stroke=body, scale=scale)
    _regroup(p, L, marks[L], p.meta[L][0] + 0.1)
    _regroup(p, "haze", marks["haze"], p.meta["haze"][0] + 0.1)
    return cx - x - scale


def title_glint(p: Pix, x, y, s, scale, w, n):
    """In a moving header a gleam of light crosses a title's glass on the hand's period, once every `HAND.glint`
    seconds: a slanted band of white, laid on the letters' glass alone through a mask of their glyphs, sweeps across
    the line from left to right in the first two fifths of the period and rests beyond it for the rest. The still
    twin has none."""
    glyphs, _, space = FONTS["57"]
    uses, cx = [], 0
    for ch in fold(s, "57"):
        if ch == " ":
            cx += space + 1
            continue
        uses.append(f'<use href="#{p.syms[("glyph", "57", ch)]}"' + (f' x="{cx}"' if cx else "") + "/>")
        cx += glyphs[ch][0] + 1
    tall = 7 * scale
    mid = f"tg{n}"
    p.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x - 1}" y="{y - 1}" width="{w + 2}" '
                  f'height="{tall + 2}"><g stroke="{C["white"]}" transform="translate({x} {y}) scale({scale})">'
                  f'{"".join(uses)}</g></mask>')
    reach = w + tall + 2 * scale
    band = f"M{x - tall - 2 * scale} {y}h{2 * scale}l{tall} {tall}h-{2 * scale}z"
    p.raw(0.5, f'<g mask="url(#{mid})"><path fill="{C["white"]}" fill-opacity=".55" d="{band}"><animateTransform '
               f'attributeName="transform" type="translate" values="0;{reach};{reach}" keyTimes="0;.4;1" '
               f'dur="{num(HAND.glint)}s" repeatCount="indefinite"/></path></g>', "")


# --------------------------------------------------------------------------- glass and lead
def disc(p: Pix, cx, cy, r, glaze, night, L="base", rim=True, lead=True):
    """A roundel of glass centred on (cx, cy): its body, a streak where it runs thin, a dark rim where it meets
    the lead, and the came round it."""
    dark, body, thin = glaze_tones(glaze, night)
    Ld = RAMP["lead"]
    cells = set()
    for yy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for xx in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            if math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) <= r:
                cells.add((xx, yy))
    for (xx, yy) in cells:
        edge = any((xx + dx, yy + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
        c = body
        if rim and edge and r >= 2.5:
            c = dark
        elif dx * LX + dy * LY > r * 0.45:
            c = thin
        p.px(xx, yy, c, L)
    if lead:
        for (xx, yy) in list(cells):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (xx + dx, yy + dy)
                if q not in cells:
                    p.px(q[0], q[1], Ld[1], L)
    return cells


# A trefoil of tracery, 13 by 10: three lobes glazed in cobalt set into a frame of stone with a cusp between each
# pair, and a roundel of ruby leaded in where they meet, the small kin of the frieze's quatrefoils. Its letters
# are the frieze's.
TREFOIL = [
    "....41114....",
    "...41GGq44...",
    "...1Ggggq6...",
    "..41Ggggq44..",
    ".41GgLrLgq44.",
    ".1GggLrLggq6.",
    ".1GggLLLggq6.",
    ".1qgggqgggq6.",
    ".44qqq4qqq64.",
    "..466646664..",
]


def trefoil(p: Pix, x, y, night, L="base"):
    """A trefoil of stone tracery glazed in cobalt round a roundel of ruby, 13 by 10 from (x - 1, y - 1)."""
    key = ("trefoil", night)
    if key not in p.syms:
        S = stone_ramp(night)
        dark, body, thin = glaze_tones("cobalt", night)
        pal = {str(k): S[k] for k in range(7)}
        pal.update({"g": body, "G": thin, "q": dark, "L": RAMP["lead"][0 if night else 1],
                    "r": glaze_tones("ruby", night)[2 if night else 1]})
        p.symbol(key, {}, shapes=_markup({(i, j): pal[ch] for j, row in enumerate(TREFOIL) for i, ch in enumerate(row)
                                          if ch != "."}))
    p.use(key, x - 1, y - 1, L)


FLEUR = ["..#..", ".###.", "#.#.#", "#####", "..#..", ".#.#."]


def fleur(p: Pix, x, y, night, L="base", s=1):
    """A fleur-de-lis in gold glass, 5 by 6 at `s` 1, lit along its upper edges."""
    G = RAMP["gold"]
    ink = {(i, j) for j, row in enumerate(FLEUR) for i, ch in enumerate(row) if ch == "#"}
    for (i, j) in ink:
        c = G[5] if (i, j - 1) not in ink else G[3]
        p.rect(x + i * s, y + j * s, s, s, c, L)


def fleur_roundel(p: Pix, cx, cy, night, L="base"):
    """A roundel of cobalt glass, 13 across, with a fleur-de-lis of gold glass leaded into it."""
    disc(p, cx, cy, 6, "cobalt", night, L)
    fleur(p, cx - 3, cy - 3, night, L)


# --------------------------------------------------------------------------- candles and their light
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `candlelight` lays its warm light on the stone
    within `r` of it, flickering with the flame. `own` are the candle's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def pool(p: Pix, rx, ry, alphas) -> tuple:
    """A pool of light's radii and rings, (rx, ry, alphas), for `Pix.halo`: in a drawing made lighter to fit its
    budget its outermost, faintest ring is left out. Each ring of a halo shows the same however many lie outside
    it, so what is left is the pool as it was, a ring smaller."""
    n = len(alphas)
    if p.lite and n > 1:
        return rx * (n - 1) / n, ry * (n - 1) / n, alphas[1:]
    return rx, ry, alphas


def glow_at(p: Pix, cx, cy, rx, ry, col, alphas, L="haze"):
    """A big stepped glow, the rings `Pix.halo` lays as ellipses, drawn once a file for its size and placed where
    it shines on layer `L`: the same glow, a few bytes each time it is placed again. A drawing made lighter leaves
    out its outermost ring (see `pool`)."""
    rx, ry, alphas = pool(p, rx, ry, alphas)
    key = ("halo", num(rx), num(ry), col, alphas)
    if key not in p.syms:
        n, prev, rings = len(alphas), 0.0, []
        for k, a in enumerate(alphas):
            f = (n - k) / n
            o = 1 - (1 - a) / (1 - prev)
            prev = a
            rings.append(f'<ellipse rx="{num(rx * f)}" ry="{num(ry * f)}" fill="{col}" fill-opacity="{num(o)}"/>')
        p.symbol(key, {}, shapes="".join(rings))
    p.layer(L)
    p.shapes[L].append(f'<use href="#{p.syms[key]}" x="{num(cx)}" y="{num(cy)}"/>')


def glass_glow(p: Pix, cx, cy, rx, ry, phase=0, motion=True):
    """By night, the light of the candles near a window reaching its glass: a warm glow laid over the glass in
    front of them, strongest nearest the flames, flickering with them in a moving file."""
    rx, ry, alphas = pool(p, rx, ry, (0.05, 0.1, 0.17))
    p.halo(cx, cy, rx, ry, RAMP["candle"][4], alphas, L=p.flicker(phase) if motion else "pool", shape=True)


def candlelight(p: Pix):
    """The finishing pass by night: each candle's light on the stone near it, strongest nearest the flame. The
    sky and the words take none, and the glass takes only the glow its own scene lays on it (`glass_glow`). In a
    drawing made lighter, which has no finishing pass, the scene lays it (see `Cathedral.scene`), its outer ring
    left out."""
    col = RAMP["candle"][4]
    alphas = (0.12, 0.26)
    n = len(alphas)
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = ground_at(p, x, y)
                if c is None or (x, y) in own or c not in STONE:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.2) / r
                ring = min(n - 1, int((1 - d) * n))
                if d < 1 and not (p.lite and ring == 0):
                    p.apx(x, y, col, alphas[ring], L)


FLAME = ((0, 0, 6), (0, -1, 6), (-1, -1, 4), (1, -1, 4), (0, -2, 5), (-1, -2, 3), (1, -2, 3), (0, -3, 4), (0, -4, 2))


def flame(p: Pix, x, y, phase=0, reach=7, halo=True, flicker=True, L="base"):
    """A candle flame whose foot is (x, y): a teardrop that flickers with its glow in a moving file, and warm
    light on the stone round it (see `candlelight`). Night only."""
    F = RAMP["candle"]
    Lf = p.flicker(phase) if flicker else L
    for (dx, dy, t) in FLAME:
        p.px(x + dx, y + dy, F[t], Lf)
    if halo:
        glow_at(p, x + 0.5, y - 1.5, 7, 6.5, F[3], (0.06, 0.12, 0.2),
                L=p.flicker(phase, back=True) if flicker else "haze")
    own = {(x + dx, y + dy) for dx, dy, _ in FLAME}
    lamp(p, x + 0.5, y - 1, reach, phase, own)


def candle(p: Pix, x, y, h, night, phase=0, L="base", reach=7, flicker=True, halo=True):
    """A wax candle two wide and `h` tall with its foot at row `y`, its wick dark by day and burning by night, with
    a glow round its flame unless `halo` is False."""
    Gr = RAMP["grisaille"]
    for yy in range(y - h, y):
        p.px(x, yy, Gr[6 if not night else 5], L)
        p.px(x + 1, yy, RAMP["lead"][5] if not night else Gr[2], L)
    p.px(x, y - h - 1, RAMP["lead"][2], L)
    if night:
        flame(p, x, y - h - 1, phase, reach=reach, halo=halo, flicker=flicker, L=L)


def candlestick(p: Pix, cx, y, night, stem=4, h=7, phase=0, L="base", reach=8, flicker=True):
    """A brass candlestick standing on row `y`: a stepped foot, a stem with a knop, a drip pan, and the candle."""
    G = RAMP["gold"]
    k = -1 if night else 0
    for i, xx in enumerate(range(cx - 2, cx + 3)):
        p.px(xx, y - 1, G[(5, 4, 4, 3, 2)[i] + k], L)
    p.px(cx - 1, y - 2, G[4 + k], L)
    p.px(cx, y - 2, G[3 + k], L)
    p.px(cx + 1, y - 2, G[2 + k], L)
    top = y - 2 - stem
    for yy in range(top, y - 2):
        p.px(cx, yy, G[3 + k], L)
    p.px(cx, y - 3 - stem // 2, G[5 + k], L)
    for i, xx in enumerate(range(cx - 1, cx + 2)):
        p.px(xx, top - 1, G[(5, 4, 2)[i] + k], L)
    candle(p, cx, top - 1, h, night, phase, L, reach=reach, flicker=flicker)


def votive(p: Pix, x, y, night, phase=0, flicker=True):
    """A votive candle standing on a sill at row `y`: a stub of wax in a little cup of gold, its wick dark by day
    and burning by night, its light on the sill round it (the glass above it takes the glow its window lays)."""
    G = RAMP["gold"]
    k = -1 if night else 0
    for i, t in enumerate((5, 4, 3, 2)):
        p.px(x - 1 + i, y - 1, G[t + k])
    candle(p, x, y - 1, 3, night, phase, reach=4, flicker=flicker, halo=False)


SCONCE = ["...I...", "...I...", "..IiI..", ".IIIII.", "...I...", "...I...", "..rIr..", ".IIIII.", "..rrr.."]


def sconce(p: Pix, x, y, night, phase=0, L="base"):
    """A candle in an iron sconce, 7 by 9 from (x, y): a bracket fixed to the stone by a riveted plate, the
    drip pan it carries and the candle on it, unlit by day and burning by night with its light on the stone."""
    I = RAMP["lead"]
    k = 1 if night else 0
    pal = {"I": I[3 + k], "i": I[1 + k], "r": I[5 + k]}
    p.sprite(x, y + 4, SCONCE[4:], pal, 1, L)
    for i, xx in enumerate(range(x + 1, x + 6)):
        p.px(xx, y + 3, I[(4, 3, 3, 2, 1)[i] + k], L)
    candle(p, x + 2, y + 3, 4, night, phase, L, reach=9)
    p.vline(x + 4, y - 1, y + 3, I[2 + k], L)
    p.vline(x + 1, y, y + 3, I[2 + k], L)


def footer_mark(p: Pix, x, y, night, wide=True):
    """What stands at the corner of a footer's closing notes, from (x, y): a small lancet window of the church
    glazed in ruby, and beside it a candle in its iron sconce, burning by night with its light reaching the
    window's glass. On a phone the window is narrower, and both stand further right, clear of a closing line
    as long as the phone lets one run."""
    lx, w, sx = (x + 1, 7, x + 10) if wide else (x + 6, 5, x + 13)
    foot = y + 10
    lancet(p, lx, foot, w, foot - TOP - 3, night, glaze="ruby", motion=False, glow=False)
    sconce(p, sx, y + 1, night, phase=1)
    if night:
        glass_glow(p, sx + 2.5, y + 2, 10, 9, phase=1, motion=False)


def step_light(p: Pix, x, w, foot, glaze):
    """By day, the colour of a light of `glaze` glass `w` wide from column x laid on the footer's step under it at
    row `foot` and the sill's lit edge under that, a column further right a row down as the sun comes from the
    upper left."""
    _, body, _ = glaze_tones(glaze, False)
    for j in (0, 1):
        for i in range(w):
            p.apx(x + i + j, foot + j, body, 0.55 if 0 < i < w - 1 else 0.3, "pool")


def footer_east(p: Pix, x, foot, night, r=9) -> tuple:
    """The design's mark at the right end of a footer, from column x and standing on the step at row `foot`, 57
    wide with its rose's radius `r` 9: a rose window set in the wall between two lancets, one of ruby glass and
    one of cobalt, and a candle in a brass candlestick at each end. By day the lancets lay their colours on the
    step; by night the candles burn and the glass glows with their light. Returns the columns it stands on."""
    lh = foot - TOP - 3
    cx = x + 19 + r + 0.5
    for lx, glaze in ((x + 7, "ruby"), (x + 23 + 2 * r, "cobalt")):
        lancet(p, lx, foot, 9, lh, night, glaze=glaze, motion=False, glow=False, lattice=lh > 18)
        if not night:
            step_light(p, lx + 2, 5, foot, glaze)
    rose_window(p, cx, foot - 3 - r, r, night, motion=False, petals=8)
    for i, sx in enumerate((x + 2, x + 36 + 2 * r)):
        candlestick(p, sx, foot, night, stem=4, h=7, phase=i, flicker=False)
    if night:
        glass_glow(p, cx, foot - lh / 2, 2 * r + 8, lh / 2 + 4, phase=1, motion=False)
    return (x, x + 38 + 2 * r)


def footer_rose(p: Pix, cx, foot, night, r=9) -> tuple:
    """The design's mark between a phone's scale and its way back up, standing on the rule at row `foot` with its
    middle on column cx: a rose window of radius `r` set in the wall, and a candle in a brass candlestick to
    each side of it, burning by night with the rose glowing in their light. Returns the columns it stands on."""
    rose_window(p, cx + 0.5, foot - 3 - r, r, night, motion=False, petals=8)
    for i, sx in enumerate((cx - r - 4, cx + r + 5)):
        candlestick(p, sx, foot, night, stem=4, h=7, phase=i, flicker=False)
    return (cx - r - 6, cx + r + 7)


def footer_knight(p: Pix, x, foot, night) -> tuple:
    """The design's mark in the corner of a footer's scale, 13 wide from column x and standing on the step at row
    `foot`: the knight in his lancet of ruby, rising to the arcade. By day he lays his ruby on the step; by night
    the candlelight behind the glass makes it glow. Returns the columns it stands on."""
    lancet(p, x, foot, 13, foot - TOP - 3, night, glaze="ruby", figure="knight", motion=False, lattice=False)
    if not night:
        step_light(p, x + 2, 9, foot, "ruby")
    return (x - 1, x + 14)


# --------------------------------------------------------------------------- the rose window
def rose_window(p: Pix, cx, cy, r, night, motion=True, L="base", petals=12, glow=True):
    """A rose window of radius `r` centred on (cx, cy): a ring of stone, and inside its lead a wheel of petals
    of ruby and cobalt glass between lead spokes, an inner wheel of emerald and amber, and a gold heart with a
    ruby eye; every pane dark against its lead and lit where it runs thin. By night the candlelight behind it
    makes it glow. A drawing made lighter to fit its budget leaves out the glints where the petals run thin, a
    texture no one misses at 1x, and the outer ring of its glow."""
    lite = p.lite
    S, Ld, G = stone_ramp(night), RAMP["lead"], RAMP["gold"]
    k = 1 if night else 0
    kind = {}
    r_lead = r - 2
    r_inner = r * 0.44
    r_heart = r * 0.2
    for yy in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for xx in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if rho > r + 0.5:
                continue
            th = math.atan2(dy, dx)
            if rho > r_lead + 0.5:
                kind[(xx, yy)] = ("stone", dx * LX + dy * LY > r * 0.3, rho > r - 0.5)
                if rho > r - 0.4:
                    kind[(xx, yy)] = ("edge",)
            elif rho > r_lead - 0.5:
                kind[(xx, yy)] = ("lead",)
            elif rho > r_inner + 0.5:
                seg = (th + math.pi) / (2 * math.pi) * petals
                near = abs(seg - round(seg)) * (2 * math.pi / petals) * rho
                kind[(xx, yy)] = ("lead",) if near < 0.55 else ("glass", ("ruby", "cobalt")[int(seg) % 2])
            elif rho > r_inner - 0.5:
                kind[(xx, yy)] = ("lead",)
            elif rho > r_heart + 0.5:
                seg = (th + math.pi) / (2 * math.pi) * 8 + 0.5
                near = abs(seg - round(seg)) * (2 * math.pi / 8) * rho
                kind[(xx, yy)] = ("lead",) if near < 0.55 else ("glass", ("emerald", "amber")[int(seg) % 2])
            elif rho > r_heart - 0.5:
                kind[(xx, yy)] = ("lead",)
            else:
                kind[(xx, yy)] = ("heart", rho < r_heart * 0.45)
    colours = {}
    for (xx, yy), what in kind.items():
        if what[0] == "edge":
            c = S[1]
        elif what[0] == "stone":
            c = S[max(0, (5 if what[1] else 3) - (1 if what[2] else 0))]
        elif what[0] == "lead":
            c = Ld[0 if night else 1]
        elif what[0] == "heart":
            c = RAMP["ruby"][4] if what[1] else G[4 + k if k else 4]
        else:
            dark, body, thin = glaze_tones(what[1], night)
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            # A small rose's pieces are mostly edge: only their lower right falls dark against the lead, so they
            # keep their colour.
            edge = any(kind.get((xx + ex, yy + ey), ("lead",))[0] in ("lead", "edge")
                       for ex, ey in (((1, 0), (0, 1)) if r < 12 else ((1, 0), (-1, 0), (0, 1), (0, -1))))
            c = dark if edge else thin if (not lite and (xx - yy) % 7 == 0 and dx * LX + dy * LY > -r * 0.2) else body
        colours[(xx, yy)] = c
    # The lead under the whole wheel, so its rings and spokes cost nothing, and under each glass its dark, so a
    # pane is a run of its body between its edges.
    lead = [(Ld[0 if night else 1], list(kind))]
    panes = [(glaze_tones(g, night)[0], [xy for xy, what in kind.items() if what[0] == "glass" and what[1] == g])
             for g in ("ruby", "cobalt", "emerald", "amber")]
    paint(p, colours, (lead, lead + panes), L)
    if night and glow:
        F = RAMP["candle"]
        rx, ry, alphas = pool(p, r * 1.55, r * 1.55, (0.05, 0.1, 0.16))
        p.halo(cx, cy, rx, ry, F[3], alphas, L="haze")
        if motion:
            rx, ry, alphas = pool(p, r * 1.2, r * 1.2, (0.05, 0.08))
            p.halo(cx, cy, rx, ry, F[4], alphas, L=p.flicker(1, back=True))


# --------------------------------------------------------------------------- the saints in glass
# Figures in glass, 9 wide, drawn as a glazier draws: bold pieces of colour, each letter a piece. The lead
# between them is drawn round the whole figure. `H` halo gold and `h` its rim, `F` flesh and `f` its shade, `E`
# an eye, `W` white glass, `w` its shade, `G` gold, `g` deep gold, `R r` ruby, `B b` cobalt, `V v` violet,
# `A a` steel, `U` umber, `Y` amber, `M` emerald.
KING = [
    "..hhhhh..", ".hHHHHHh.", "hHG.G.GHh", "hHGGGGGHh", "hHFFFFFHh", ".hFEFEFh.", "..FFfFF..", "..UFFFU..",
    "..WWWWW..", ".RRWwWRRG", ".RRRWRRRg", "RRRRWRRRG", "RRRRWRRRg", "RRRRWRRRG", "RRRRWRRRg", ".RRRRRRRG",
    ".rrrrrrr.", ".rrrrrrr.", "..UUUUU..",
]
BISHOP = [
    "....W....", "...WWW...", "..hWgWh..", ".hHWWWHh.", "hHHFFFHHh", "hHFEFEFHh", ".hFFfFFh.", "..FFFFF.G",
    ".VVVgVVVG", "VVVVgVVVG", "VVVVgVVVG", "VVVVgVVVG", "VVVVgVVVG", "VVVVgVVVG", ".VVVgVVVG", ".VVVgVVVG",
    ".vvvvvvvG", ".vvvvvvvG", "..UUUUU..",
]
KNIGHT = [
    "..hhhhh..", ".hHHHHHh.", "hHAAAAAHh", "hHAaaaAHh", "hHA...AHh", ".hAAAAAh.", "W.AAAAA..", "W.BBBBB..",
    "WBBBWBBB.", "WBWWWWWB.", "WBBBWBBB.", "GBBBWBBB.", "WBBBWBBB.", "WBBBBBBB.", ".BBBBBBB.", ".bbbbbbb.",
    ".bbbbbbb.", ".AAAAAAA.", "..aaaaa..",
]
ANGEL = [
    "..hhhhh..", ".hHHHHHh.", "hHYYYYYHh", "hHYFFFYHh", "hHFEFEFHh", ".hYFFFYh.", "G.FFFFF.G", "GGWWWWWGG",
    "GGWWWWWGG", "GGWWwWWGG", "GGWWWWWGG", "GgWWWWWgG", "GgWWWWWgG", "GgWWWWWgG", ".gWWWWWg.", ".gWWWWWg.",
    "..wwwww..", "..wwwww..", "..FF.FF..",
]
SAINTS = {"king": KING, "bishop": BISHOP, "knight": KNIGHT, "angel": ANGEL}


def saint_pal(night: bool) -> dict:
    """The pieces' tones, a step brighter by night with the candlelight behind them."""
    k = 1 if night else 0
    G, F, Gr, R, B, V, A, U, Y, M = (RAMP[n] for n in ("gold", "flesh", "grisaille", "ruby", "cobalt", "violet",
                                                        "lead", "umber", "amber", "emerald"))
    return {"H": G[4 + k], "h": G[2 + k], "F": F[4], "f": F[2], "E": RAMP["lead"][1], "W": Gr[6], "w": Gr[4],
            "G": G[4 + k], "g": G[2 + k], "R": R[3 + k], "r": R[1 + k], "B": B[3 + k], "b": B[1 + k],
            "V": V[3 + k], "v": V[1 + k], "A": A[5 + k], "a": A[3 + k], "U": U[2 + k], "Y": Y[3 + k], "M": M[3 + k]}


def figure_in_lead(p: Pix, x, y, art, pal, night, L="base"):
    """A figure in glass, rows of `art` looked up in `pal` with its top-left at (x, y), and the lead drawn round
    the whole of it, a pixel wide. The lead is laid under the figure as one ground when that is the lighter way to
    draw it (see `paint`)."""
    Ld = RAMP["lead"][0 if night else 1]
    colours = {}
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch != "." and pal.get(ch):
                colours[(x + i, y + j)] = pal[ch]
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                jj, ii = j + dy, i + dx
                if not (0 <= jj < len(art) and 0 <= ii < len(row) and art[jj][ii] != "."):
                    colours[(x + ii, y + jj)] = Ld
    paint(p, colours, ([(Ld, list(colours))],), L)


def saint(p: Pix, x, y, who: str, night, L="base"):
    """One of the saints in glass, top-left at (x, y), the lead drawn round every piece of the figure."""
    figure_in_lead(p, x, y, SAINTS[who], saint_pal(night), night, L)


# A knight in glass for a section's lancet, 13 wide and 27 tall: a great helm under his halo, a cobalt surcoat
# with a white cross, a sword raised on his right and a shield on his left.
KNIGHT_TALL = [
    "....hhhhh....", "...hHHHHHh...", "..hHAAAAAHh..", "..hHAAAAAHh..", "..hHAaaaAHh..", "..hHA...AHh..",
    "...hAAAAAh...", "W...AAAAA....", "W...AAAAA....", "W..BBBBBBB...", "W.BBBBWBBBB..", "WBBBBBWBBBBB.",
    "WBBWWWWWWWBB.", "WBBBBBWBBBBB.", "GBBBBBWBBBBRR", "WBBBBBWBBBRRR", "W.BBBBWBBBRWR", "W.BBBBWBBBRRR",
    "..BBBBBBBBRRR", "..BBBBBBBB.RR", "..BBBBBBBB...", "..bbbbbbbb...", "..bbbbbbbb...", "..bbbbbbbb...",
    "..AAAAAAAA...", "..AAA..AAA...", "..aaa..aaa...",
]


def knight_tall(p: Pix, x, y, night, L="base"):
    figure_in_lead(p, x, y, KNIGHT_TALL, saint_pal(night), night, L)


# --------------------------------------------------------------------------- the lancets
def _arch_rows(w: int, h: int) -> list:
    """The inside of a lancet `w` wide and `h` tall as (row, x0, x1) from the apex down: an equilateral pointed
    head over straight jambs."""
    out = []
    R = w - 1
    rise = int(R * 0.866)
    for j in range(h):
        t = rise - j
        if t > 0:
            half = math.sqrt(max(0.0, R * R - t * t)) - R / 2
            if half < 0.5:
                continue
            x0, x1 = math.ceil(w / 2 - half - 0.01), math.floor(w / 2 + half - 0.99)
            if x1 < x0:
                continue
            out.append((j, x0, x1))
        else:
            out.append((j, 0, w - 1))
    return out


def lancet(p: Pix, x, foot, w, h, night, glaze="cobalt", figure=None, L="base", motion=True, glow=True,
           lattice=True):
    """A lancet window `w` wide whose sill is row `foot` and whose apex stands `h` rows above it: a stone frame
    round a pointed opening, the lead inside it, and the glass: a ground of `glaze` under a lattice of lead
    quarries, a figure in glass standing on a band of emerald at the foot when one is given, and a canopy of
    amber over its head. By night the candlelight behind the window makes it glow."""
    S, Ld = stone_ramp(night), RAMP["lead"]
    k = -1 if night else 0
    rows = _arch_rows(w, h)
    inside = {}
    for (j, x0, x1) in rows:
        for xx in range(x0, x1 + 1):
            inside[(x + xx, foot - h + j)] = True
    frame_cells = {}
    for (xx, yy) in inside:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, -1)):
            q = (xx + dx, yy + dy)
            if q not in inside:
                frame_cells[q] = True
    for (xx, yy) in frame_cells:
        lit = ((xx - 1, yy) not in inside and (xx + 1, yy) in inside
               or (xx, yy - 1) not in inside and (xx, yy + 1) in inside)
        p.px(xx, yy, S[6 + k] if lit else S[3 + k], L)
    for (xx, yy) in frame_cells:
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            q = (xx + dx, yy + dy)
            if q not in inside and q not in frame_cells and q[1] < foot:
                p.px(q[0], q[1], S[2 + k], L)
    lead_cells = {q for q in inside
                  if any((q[0] + dx, q[1] + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    dark, body, thin = glaze_tones(glaze, night)
    top = foot - h
    colours, glass, canopy_glass = {}, [], []
    for (xx, yy) in inside:
        u, v = (xx - x), (yy - top)
        canopy = figure and yy < foot - 1 - len(SAINTS[figure]) - 1 and yy >= foot - 1 - len(SAINTS[figure]) - 6
        if (xx, yy) in lead_cells:
            c = Ld[0 if night else 1]
        elif figure and yy >= foot - 2:
            c = RAMP["emerald"][3 + (1 if night else 0)]
        elif canopy:
            c = _canopy_tone(u, v, night)
            canopy_glass.append((xx, yy))
        elif lattice and ((u + v) % 6 == 0 or (u - v) % 6 == 0):
            c = Ld[2 if night else 3]
            glass.append((xx, yy))
        else:
            near = any((xx + dx, yy + dy) in lead_cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            c = dark if near else thin if (u - v) % 6 == 2 and (u + v) % 6 != 0 else body
            glass.append((xx, yy))
        colours[(xx, yy)] = c
    # The glass laid with its pattern of lattice and streaks, the canopy with its own, and the lead under all of
    # it when that is lighter; only the dark edge against the lead and the band at the foot are pixels.
    quarries = (f"url(#{_lattice(p, glaze, night, lattice, x, top)})",
                lambda xy: _quarry_tone(xy[0] - x, xy[1] - top, glaze, night, lattice))
    over = []
    if canopy_glass:
        over.append(((f"url(#{_canopy(p, night, x, top)})", lambda xy: _canopy_tone(xy[0] - x, xy[1] - top, night)),
                     canopy_glass))
    lead = (Ld[0 if night else 1], list(inside))
    paint(p, colours, ([(quarries, glass)] + over, [(quarries, list(inside))] + over,
                       [lead, (quarries, glass)] + over, [lead, (quarries, glass + canopy_glass)] + over), L)
    if figure:
        art = SAINTS[figure]
        saint(p, x + (w - 9) // 2, foot - 2 - len(art), figure, night, L)
    if night and glow:
        F = RAMP["candle"]
        glow_at(p, x + w / 2, foot - h / 2, w * 0.9, h * 0.62, F[3], (0.05, 0.1), L=p.layer("haze-", z=-20.1))
    return inside


def _quarry_tone(u, v, glaze, night, lattice) -> str:
    """The colour of a lancet's glass `u` across and `v` down from its top-left, where nothing else lies on it: the
    lattice of lead, the streak where the glass runs thin, and the glass."""
    _, body, thin = glaze_tones(glaze, night)
    if lattice and ((u + v) % 6 == 0 or (u - v) % 6 == 0):
        return RAMP["lead"][2 if night else 3]
    return thin if (u - v) % 6 == 2 and (u + v) % 6 != 0 else body


def _canopy_tone(u, v, night) -> str:
    """The colour of a canopy of amber over a saint's head, `u` across and `v` down from its window's top-left."""
    Y = RAMP["amber"]
    return Y[4 if night else 3] if (u + v) % 3 else Y[2 if night else 1]


def _lattice(p: Pix, glaze, night, lattice, x, y) -> str:
    """The glass of a lancet whose top-left is (x, y) as a pattern: its lattice of lead, its streaks and its glass,
    six pixels square, shared by every lancet of the glass that stands in step with it."""
    return _tile(p, ("quarries", glaze, night, lattice, x % 6, y % 6), 6, x, y,
                 lambda u, v: _quarry_tone(u, v, glaze, night, lattice))


def _canopy(p: Pix, night, x, y) -> str:
    """The amber of a canopy as a pattern three pixels square, for the lancet whose top-left is (x, y)."""
    return _tile(p, ("canopy", night, x % 3, y % 3), 3, x, y, lambda u, v: _canopy_tone(u, v, night))


SILL = 5   # the rows of a window's sill over the floor


def sill(p: Pix, x0, x1, g, night, lights=()) -> int:
    """The stone sill a window stands on, from x0 to x1 over the floor at row g: a ledge five rows deep, its lit
    edge the window's foot, its top face three rows deep and its front in shade. By day each of `lights`, (x, w,
    glaze), lays the colour of the glass above it on the ledge: a patch of that glass's colour the width of its
    light, falling a column to the right a row as the sun comes from the upper left. Returns the row the window
    stands on."""
    S = stone_ramp(night)
    k = -1 if night else 0
    for j, t in enumerate((6, 5, 5, 4, 2)):
        p.hline(x0, x1, g - SILL + j, S[t + k])
    if not night:
        for (x, w, glaze) in lights:
            _, body, _ = glaze_tones(glaze, False)
            for j in (1, 2, 3):
                for i in range(w):
                    p.apx(x + i + j - 1, g - SILL + j, body, 0.66 if 0 < i < w - 1 else 0.4, "pool")
    return g - SILL


# --------------------------------------------------------------------------- the altar
def altar(p: Pix, cx, g, night, w=26, candles=(-8, 0, 8), phase=0, cross=True, L="base", flicker=True):
    """An altar of stone standing on row `g`, `w` wide about cx: a slab lit along its top over a frontal of
    white cloth with a band of violet silk, candles in brass candlesticks on the slab, and a gold cross. By
    night the candles burn and their light lies on the stone."""
    S, Gr, V, G = stone_ramp(night), RAMP["grisaille"], RAMP["violet"], RAMP["gold"]
    k = -1 if night else 0
    x0 = cx - w // 2
    top = g - 7
    p.hline(x0 - 1, x0 + w + 1, top, S[6 + k])
    p.hline(x0 - 1, x0 + w + 1, top + 1, S[4 + k])
    p.px(x0 + w, top + 1, S[2 + k])
    for yy in range(top + 2, g):
        for xx in range(x0, x0 + w):
            t = 2 if yy == g - 1 else (yy - top - 2) % 2 == 0 and 6 or 5
            c = Gr[max(0, t + k)]
            if yy == top + 4:
                c = V[3 + k] if xx % 4 else V[1 + k]
            elif xx in (x0, x0 + w - 1):
                c = Gr[3 + k]
            p.px(xx, yy, c, L)
    p.rect(x0 - 2, top + 2, 2, g - top - 2, S[3 + k], L)
    p.rect(x0 + w, top + 2, 2, g - top - 2, S[1 + k], L)
    if cross:
        for yy in range(top - 7, top):
            p.px(cx, yy, G[4 + k], L)
        for xx in range(cx - 2, cx + 3):
            p.px(xx, top - 5, G[4 + k], L)
        p.px(cx, top - 7, G[5 + k], L)
        p.px(cx - 2, top - 5, G[5 + k], L)
        p.px(cx - 1, top - 1, G[3 + k], L)
        p.px(cx + 1, top - 1, G[3 + k], L)
    for i, dx in enumerate(candles):
        candlestick(p, cx + dx, top, night, stem=4, h=7 if i % 2 == 0 else 6, phase=phase + i, L=L, flicker=flicker)


# --------------------------------------------------------------------------- the sunbeam and its motes
MOTE_STEP = 1.4   # the seconds a mote takes to drift a column across the shaft of sun


def sunbeam(p: Pix, top, foot, x0, x1, w0, w1, seed=1, motion=True, small=False, name="bm"):
    """A shaft of sunlight slanting down from the upper left by day, `w0` wide at (x0, top) and spreading to `w1`
    at (x1, foot): a wash of gold over the scene with a pale core and two brighter rays down it, and motes of dust
    caught in it that drift slowly across it in a moving header, a column every second and a half, so they cross
    the shaft in half a minute, as slow as the hand's ambient sweeps. A `small` shaft, a phone's, has no rays and
    fewer motes."""
    def quad(a, b):
        """The shaft from a fraction `a` of its width to `b`, as a polygon's points."""
        return (f"{num(x0 + w0 * a)} {top} {num(x0 + w0 * b)} {top} {num(x1 + w1 * b)} {foot} "
                f"{num(x1 + w1 * a)} {foot}")
    L = p.layer("beam", z=4)
    p.shapes[L].append(f'<polygon points="{quad(0, 1)}" fill="{RAMP["gold"][4]}" fill-opacity=".28"/>')
    p.shapes[L].append(f'<polygon points="{quad(.22, .78)}" fill="{X["sun"]}" fill-opacity=".5"/>')
    if not small:
        for a in (.36, .62):
            p.shapes[L].append(f'<path d="M{num(x0 + w0 * a)} {top}L{num(x1 + w1 * a)} {foot}" stroke="{C["white"]}" '
                               f'stroke-opacity=".55" stroke-width=".6"/>')
    cid = f"{name}c"
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{quad(0, 1)}"/></clipPath>')
    lo, hi = min(x0, x1), max(x0 + w0, x1 + w1)
    period = round(w1)
    anim = ("drift", lo, top, hi, foot, period, cid, MOTE_STEP) if motion else None
    Lm = p.layer("motes", anim, z=6)
    rnd = random.Random(seed)
    for i in range(14 if small else 26):
        y = rnd.randrange(top + 2, foot - 1)
        t = (y - top) / max(1, foot - top)
        x = round(x0 + (x1 - x0) * t + rnd.uniform(0.1, 0.9) * (w0 + (w1 - w0) * t))
        if lo <= x < hi:
            p.px(x, y, C["white"] if i % 3 == 0 else RAMP["gold"][5] if i % 3 == 1 else RAMP["gold"][3], Lm)


# --------------------------------------------------------------------------- the owl
OWL = [
    ["#...........#", "##.........##", ".##.......##.", "..###...###..", "...#######...", "...#wwewe#...",
     "...##www##...", "....#####....", ".....#.#....."],
    [".............", ".............", ".............", "....#####....", "...#######...", "..##wwewe##..",
     ".##.#www#.##.", "##..#####..##", ".....#.#....."],
]


def _owl_symbol(p: Pix, frame: int):
    key = ("owl", frame)
    if key not in p.syms:
        U, Gr, Y = RAMP["umber"], RAMP["grisaille"], RAMP["amber"]
        art = OWL[frame]
        ink = {(i, j): ch for j, r in enumerate(art) for i, ch in enumerate(r) if ch != "."}
        cells = {}
        for (i, j), ch in ink.items():
            if ch == "w":
                cells[(i, j)] = Gr[5]
            elif ch == "e":
                cells[(i, j)] = Y[5]
            else:
                cells[(i, j)] = U[4] if (i, j - 1) not in ink else U[2]
        p.symbol(key, {}, shapes=_markup(cells))
    return key


def glide(p: Pix, frames, path, dur, z, clip, flap=0.4):
    """Something that flies through a window of the sky: like `Pix.fly`, but clipped to `clip` (x0, y0, x1, y1),
    so it can enter from beyond the frame. The still file shows the first frame at the path's first point."""
    ids = [p.syms[f] for f in frames]
    steps = ";".join(f"{x} {y}" for x, y in path)
    n = len(ids)
    uses = []
    for i, sid in enumerate(ids):
        vals = ";".join("1" if j == i else "0" for j in range(n))
        hidden = ' opacity="0"' if i else ""
        uses.append(f'<use href="#{sid}"{hidden}><animate attributeName="opacity" values="{vals}" '
                    f'dur="{num(flap * n)}s" repeatCount="indefinite" calcMode="discrete"/></use>')
    cid = f"gl{len(p.raws)}"
    x0, y0, x1, y1 = clip
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    moving = (f'<g clip-path="url(#{cid})"><g>{"".join(uses)}<animateTransform attributeName="transform" '
              f'type="translate" values="{steps}" dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/>'
              f'</g></g>')
    sx, sy = path[0]
    p.raw(z, moving, f'<use href="#{ids[0]}" x="{sx}" y="{sy}"/>')


def owl(p: Pix, start, perch, clip, motion=True, hold=14, step=2):
    """An owl crossing by night: it comes in from beyond the frame on the right, glides down to perch on the
    rose window, waits, and flies off beyond the frame on the left. `start` is where the still file shows it,
    mid-flight."""
    frames = [_owl_symbol(p, 0), _owl_symbol(p, 1)]
    if not motion:
        p.use(frames[0], start[0], start[1], "near")
        return
    x0, y0, x1, y1 = clip
    sx, sy = start
    px_, py_ = perch
    path = []
    n = max(1, round(abs(px_ - sx) / step))
    for i in range(n):
        t = i / n
        path.append((round(sx + (px_ - sx) * t), round(sy + (py_ - sy) * t * t)))
    path += [perch] * hold
    far = x0 - 14
    m = max(1, round(abs(px_ - far) / step))
    for i in range(m):
        t = i / m
        path.append((round(px_ + (far - px_) * t), round(py_ - 8 * math.sin(math.pi * t) - 2 * t)))
    back = x1 + 4
    q = max(1, round(abs(back - sx) / step))
    for i in range(q):
        t = i / q
        path.append((round(back + (sx - back) * t), round(y0 + 1 + (sy - y0 - 1) * t)))
    glide(p, frames, path, len(path) * 0.1, 16, clip)


# --------------------------------------------------------------------------- the scenes
def east_end(p: Pix, x0, g, night, motion=True, phase=0, room=76, reach=53):
    """The altar end of the nave on the left of a header, from x0 over 52 pixels, the floor at row g: the altar
    with its cross and three candles, and above it the great rose window; by day a sunbeam slants down across
    the rose onto the altar with motes drifting in it and lays the rose's colours on the altar's cloth; by night
    the candles burn, their light reaching the lower half of the rose, the rose glows and an owl comes to perch
    on it. Built to the `room` of rows free of words above the floor: with 70 rows or more the
    rose is at its full size, with fewer it is smaller, under 30 rows there is no rose, and under 20 nothing.
    Beside a title that runs nearly to it, `reach` keeps the owl's flight within that many columns of x0, short
    of the 53 it may take, and its still file shows it nearer the rose."""
    if room < 20:
        return None
    cx = x0 + 26
    altar(p, cx, g, night, phase=phase, flicker=motion)
    r = min(20, (room - 27) // 2)
    rose = room >= 30 and r >= 8
    if rose:
        cy = g - 27 - r
        rose_window(p, cx, cy, r, night, motion=motion)
        if night and room >= 50:
            owl(p, (x0 + reach - 13, cy - r - 2), (cx - 4, cy - r - 7), (x0 - 1, g - room, x0 + reach, g - 1),
                motion=motion)
    if night:
        glass_glow(p, cx + 0.5, g - 25, 18, 22, phase=phase, motion=motion)
    else:
        top = max(23, g - room + 1)
        sunbeam(p, top, g - 8, x0 + 4, cx - 9, 9, 20, seed=phase + 3, motion=motion)
        if rose:
            altar_light(p, cx, g, (("ruby", -7), ("cobalt", -1), ("ruby", 5)))
    return (x0 - 1, x0 + 53)


def altar_light(p: Pix, cx, g, patches, w=26):
    """The colours of the rose the sun has come through, laid on the white cloth of the altar under it by day:
    for each of `patches`, (glaze, offset from cx), a patch of that glass's colour four columns wide on the
    frontal, falling a column to the right a row."""
    top = g - 7
    for glaze, dx in patches:
        _, body, _ = glaze_tones(glaze, False)
        for j, yy in enumerate(range(top + 2, top + 5)):
            for i in range(4):
                x = cx + dx + i + j
                if cx - w // 2 < x < cx + w // 2 - 1 and yy != top + 4:
                    p.apx(x, yy, body, 0.42 if 0 < i < 3 else 0.26, "pool")


# The glass each saint of the east window stands on: the king's ruby robe on cobalt, the bishop's violet on
# amber, the knight's cobalt surcoat on ruby and the angel's white on emerald, so each lays its own colour on the
# sill by day.
GROUNDS = {"king": "cobalt", "bishop": "amber", "knight": "ruby", "angel": "emerald"}


def east_window(p: Pix, x0, g, night, motion=True, phase=0, room=76,
                figures=("king", "bishop", "knight", "angel"), w=13):
    """The lancets of the east window on the right of a header, from x0 over 50 pixels, standing on a sill over
    the floor at row g: a saint in glass in each on a ground of its own glass, and over them, when the words
    leave room, a small rose in the tracery; votive candles stand on the sill between them, burning by night with
    their light on the saints' glass, and by day each lancet lays its colour on the sill, ruby, cobalt, emerald
    and amber side by side. Built to the `room` of rows free of words: with 38 rows or more the saints
    stand in their lancets, with fewer the lancets are glazed plain and shorter, and under 18 nothing stands."""
    if room < 18:
        return None
    n = len(figures)
    span = n * w - (n - 1)
    with_figures = room >= 38
    h = min(44, room - 10) if with_figures else min(24, room - 7)
    foot = sill(p, x0 - 2, x0 + span + 2, g, night,
                [(x0 + i * (w - 1) + 2, w - 4, GROUNDS[who]) for i, who in enumerate(figures)])
    for i, who in enumerate(figures):
        lancet(p, x0 + i * (w - 1), foot, w, h, night, glaze=GROUNDS[who], figure=who if with_figures else None,
               motion=motion, lattice=not with_figures or h > 40)
    for i in range(1, n):
        votive(p, x0 + i * (w - 1) - 1, g - 1, night, phase=phase + i, flicker=motion)
    if night:
        glass_glow(p, x0 + span / 2, foot - 5, span / 2 + 4, 14, phase=phase + 1, motion=motion)
    if room >= h + 32:
        rose_window(p, x0 + span / 2, foot - h - 13, 9, night, motion=motion, petals=8, glow=False)
    return (x0 - 2, x0 + span + 2)


def section_window(p: Pix, cx, g, night, motion=True, phase=0, room=70):
    """The lancet beside a section's title, centred on cx and standing on a sill over row g: a knight in glass
    under a canopy, a candle in a brass candlestick on the sill to each side, whose light reaches his glass by
    night, and by day the window's ruby laid on the sill. Built to the `room` of rows free of words: with 48 rows
    or more the knight stands in his window, with fewer the window is glazed plain and shorter, and under 22
    nothing stands."""
    if room < 22:
        return None
    Ld = RAMP["lead"]
    w = 19
    x = cx - w // 2
    foot = sill(p, x - 14, x + w + 14, g, night, [(x + 2, w - 4, "ruby")])
    tall = room >= 48
    h = min(56, room - 10) if tall else min(28, room - 7)
    inside = lancet(p, x, foot, w, h, night, glaze="ruby", motion=motion, lattice=not tall)
    if tall:
        top = foot - h
        Y = RAMP["amber"]
        for (xx, yy) in inside:
            u, v = xx - x, yy - top
            if foot - 30 > yy >= foot - 36:
                c = Y[4 + (1 if night else 0)] if (u + v) % 3 else Y[2 + (1 if night else 0)]
                if any(q not in inside for q in ((xx + 1, yy), (xx - 1, yy))):
                    c = Ld[0 if night else 1]
                p.px(xx, yy, c)
        knight_tall(p, x + 3, foot - 29, night)
    if room >= 26:
        candlestick(p, x - 6, foot, night, stem=5, h=8, phase=phase, flicker=motion)
        candlestick(p, x + w + 6, foot, night, stem=5, h=8, phase=phase + 1, flicker=motion)
        if night:
            glass_glow(p, cx + 0.5, foot - 13, 19, 15, phase=phase, motion=motion)
    return (x - 14, x + w + 14)


def arch_frame(p: Pix, x, foot, w, h, night, depth=3, L="base") -> dict:
    """The moulded stone round a pointed opening `w` wide whose sill is row `foot` and whose apex stands `h` rows
    above it: a moulding `depth` deep, lit where it faces the light up and to the left and in shade where it
    turns away, its outer edge dark against the glass; and the opening itself filled with plain stone, the plate
    the window's lights and its rose are set into. Returns the opening's cells."""
    S = stone_ramp(night)
    k = -1 if night else 0
    inside = {(x + xx, foot - h + j) for (j, x0, x1) in _arch_rows(w, h) for xx in range(x0, x1 + 1)}
    outer = {(x - depth + xx, foot - h - depth + j) for (j, x0, x1) in _arch_rows(w + 2 * depth, h + depth)
             for xx in range(x0, x1 + 1)}
    cx = x + w / 2
    colours = {}
    for (xx, yy) in outer - inside:
        if yy >= foot:
            continue
        reveal = any((xx + dx, yy + dy) in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        edge = any((xx + dx, yy + dy) not in outer for dx, dy in ((1, 0), (-1, 0), (0, -1)))
        left = xx < cx
        if edge:
            c = S[1 + k]                                   # the moulding's outer edge, dark against the glass
        elif reveal:
            c = S[2 + k] if left else S[6 + k]             # the reveal, turned from the light on the left
        else:
            c = S[5 + k] if left else S[4 + k]             # the moulding's face
        colours[(xx, yy)] = c
    for (xx, yy) in inside:                                # the plate of stone the lights are set into
        colours[(xx, yy)] = S[4 + k]
    paint(p, colours, ([(S[4 + k], list(inside))],), L)
    return {q: True for q in inside}


def quatrefoil_light(p: Pix, cx, cy, glaze, night, L="base"):
    """A little quatrefoil of glass pierced through a window's plate, seven across centred on (cx, cy): four lobes
    of `glaze` round a gold bead, leaded round."""
    dark, body, thin = glaze_tones(glaze, night)
    Ld = RAMP["lead"][0 if night else 1]
    art = ["..lll..", ".lgGgl.", "lgglggl", "lGlolGl", "lgglggl", ".lgggl.", "..lll.."]
    p.sprite(cx - 3, cy - 3, art, {"l": Ld, "g": body, "G": thin, "o": RAMP["gold"][5]}, 1, L)


# The great window's three lights, left to right: the saint in each and the glass he stands on.
TRIPLET = (("angel", "emerald"), ("knight", "ruby"), ("king", "cobalt"))


def great_window(p: Pix, cx, g, night, motion=True, phase=0, room=90, lw=19):
    """The great window beside a section's title, centred on cx over the floor at row g: under one pointed arch
    of moulded stone, three lancets stepped up to the middle one, the angel on her emerald, the knight on his
    ruby and the king on his cobalt, each under his canopy of amber; and in the arch's head a rose of ruby and
    cobalt round a heart of gold over the middle light, a little quatrefoil of glass over each of the others.
    It stands on a sill with a candle in a brass candlestick at each end. By day it lays its three colours on the
    sill; by night the candles burn, their light reaches the glass, and the glass glows. Built to the `room` of
    rows the words leave free above the floor: the arch rises as high as the room lets it, to 84 rows. A phone's
    is the same window drawn smaller, its lights `lw` 13 wide in place of 19, its rose smaller and nothing over
    the outer lights, whose heads come too near the arch. Returns the span of the floor it stands on."""
    small = lw < 19
    gap, lower = (2, 4) if small else (3, 9)
    w = 3 * lw + 2 * gap + 6
    x = cx - w // 2
    xs = [x + 3 + i * (lw + gap) for i in range(3)]
    foot = sill(p, x - 10, x + w + 10, g, night, [(lx + 2, lw - 4, glaze) for lx, (_, glaze) in zip(xs, TRIPLET)])
    h = min(84, room - SILL - 3)
    arch_frame(p, x, foot, w, h, night)
    lh = min(30, h - 22) if small else round(h * 0.62)
    for i, (lx, (who, glaze)) in enumerate(zip(xs, TRIPLET)):
        tall = lh - (lower if i != 1 else 0)
        lancet(p, lx, foot, lw, tall, night, glaze=glaze, figure=who, motion=motion, lattice=tall > 40)
    r = min(8, (h - lh) // 2 - 3) if small else min(12, (h - lh) // 2 - 2)
    cy = foot - lh - 3 - r
    rose_window(p, cx + 0.5, cy, r, night, motion=motion, glow=False, petals=8 if small else 12)
    if not small:
        for i, lx in enumerate(xs):
            if i != 1:
                quatrefoil_light(p, lx + lw // 2, foot - lh + lower - 6, "amber", night)
    candlestick(p, x - 6, foot, night, stem=7, h=10, phase=phase, flicker=motion)
    candlestick(p, x + w + 5, foot, night, stem=7, h=10, phase=phase + 1, flicker=motion)
    if night:
        glass_glow(p, cx + 0.5, foot - lh // 2, w // 2 + 6, lh // 2 + 8, phase=phase, motion=motion)
        glow_at(p, cx + 0.5, cy, r * 1.7, r * 1.7, RAMP["candle"][3], (0.05, 0.1), L=p.layer("haze-", z=-20.1))
    return (x - 10, x + w + 10)


def register(p: Pix, inside, x, w, base, top, who, night):
    """A second register in a tall lancet `w` wide from column x whose glass is `inside` and whose apex is row
    `top`: over row `base` a band of emerald for the saint `who` to stand on, the saint, and a canopy of amber over
    the saint's head, laid on the lancet's glass and kept inside its lead."""
    Ld, M = RAMP["lead"][0 if night else 1], RAMP["emerald"][3 + (1 if night else 0)]
    art = SAINTS[who]
    feet = base - 2
    for (xx, yy) in inside:
        if not (feet - len(art) - 6 <= yy < base) or feet - len(art) - 1 <= yy < feet:
            continue
        edge = any(q not in inside for q in ((xx + 1, yy), (xx - 1, yy)))
        c = M if yy >= feet else _canopy_tone(xx - x, yy - top, night)
        p.px(xx, yy, Ld if edge else c)
    saint(p, x + (w - 9) // 2, feet - len(art), who, night)


def strip_scene(p: Pix, cx, g, night, motion=True, phase=0, room=60):
    """What stands at the right of a strip, its hero: a tall lancet of emerald glass, the bishop standing in it
    under his canopy of amber and a little quatrefoil of ruby in its head, between a pair of candles in brass
    candlesticks on a sill, as tall as the words leave room for, to 66 rows; by day it lays its green on the sill,
    by night it takes the candles' light. A lancet 62 rows tall or more is glazed in two registers, as the tall
    lights of a cathedral are, the angel standing over the bishop under a canopy of her own. Where the words
    leave fewer than 38 rows, a small lancet of emerald glass with a roundel of amber in its head stands between
    the candles instead, and under 32 the candles alone."""
    if room < 18:
        return None
    if room >= 38:
        h = min(66, room - SILL - 2)
        foot = sill(p, cx - 20, cx + 20, g, night, [(cx - 6, 13, "emerald")])
        inside = lancet(p, cx - 8, foot, 17, h, night, glaze="emerald", figure="bishop", motion=motion,
                        lattice=h > 40)
        if h >= 62:
            register(p, inside, cx - 8, 17, foot - 2 - len(BISHOP) - 6, foot - h, "angel", night)
        quatrefoil_light(p, cx, foot - h + (7 if h >= 62 else 9), "ruby", night)
        candlestick(p, cx - 14, foot, night, stem=6, h=9, phase=phase, flicker=motion)
        candlestick(p, cx + 14, foot, night, stem=6, h=9, phase=phase + 1, flicker=motion)
        if night:
            glass_glow(p, cx + 0.5, foot - h // 3, 18, h // 3 + 6, phase=phase, motion=motion)
        return (cx - 20, cx + 20)
    glazed = room >= 32
    foot = sill(p, cx - 18, cx + 18, g, night, [(cx - 4, 9, "emerald")] if glazed else ())
    if glazed:
        h = min(32, room - 8)
        lancet(p, cx - 6, foot, 13, h, night, glaze="emerald", motion=motion)
        disc(p, cx + 0.5, foot - h + 7, 2.6, "amber", night)
    candlestick(p, cx - 12, foot, night, stem=4, h=7, phase=phase, flicker=motion)
    candlestick(p, cx + 12, foot, night, stem=4, h=7, phase=phase + 1, flicker=motion)
    if night:
        glass_glow(p, cx + 0.5, foot - 12, 16, 12, phase=phase, motion=motion)
    return (cx - 18, cx + 18)


def chapel(p: Pix, x0, g, night, room=40, phase=0):
    """A phone's altar end, 30 wide from x0: the altar with two candles and its cross, and over it a rose window
    when the words leave room; by day a shaft of sun comes down from the upper left through the rose onto the
    altar and lays the rose's colours on its cloth. Built to the `room` of rows free of words above the floor:
    with 62 rows or more the rose is at its full size, wider than the altar end, with fewer it is smaller, under
    30 there is no rose, and under 18 nothing stands."""
    if room < 18:
        return None
    cx = x0 + 15
    altar(p, cx, g, night, w=20, candles=(-6, 6), phase=phase, cross=True, flicker=False)
    r = min(18, (room - 26) // 2)
    rose = room >= 30 and r >= 6
    if rose:
        rose_window(p, cx, g - 26 - r, r, night, motion=False, petals=12 if r >= 12 else 8)
    if night:
        glass_glow(p, cx + 0.5, g - 24, max(13, r + 3), max(15, r + 6), motion=False)
    if not night and room >= 34:
        sunbeam(p, max(23, g - room + 1), g - 8, x0 + 1, cx - 7, 6, 13, seed=phase + 5, motion=False,
                small=True, name="bn")
        if rose:
            altar_light(p, cx, g, (("ruby", -5), ("cobalt", 1)), w=20)
    return (x0 - 1, x0 + 31)


def phone_nave(p: Pix, g, night, room=52):
    """A phone's east end, the full width of the sheet under its words, its floor at row g: in the middle the
    altar under its rose (see `chapel`), a tall candle on its stand to either side of it, and beyond them two
    saints in their lancets at each side, the angel and the king on the left and the bishop and the knight on
    the right, each on the glass of his light in the east window. Built to the `room` of rows the words leave
    free above the floor. Returns the span of the floor it stands on."""
    chapel(p, 75, g, night, room=room)
    for x, phase in ((56, 1), (124, 2)):
        if room >= 36:
            candlestick(p, x, g, night, stem=min(26, room - 20), h=10, phase=phase, flicker=False)
    phone_lancets(p, 10, g, night, figures=("angel", "king"), room=room)
    phone_lancets(p, 146, g, night, figures=("bishop", "knight"), room=room)
    return (6, 174)


def phone_lancets(p: Pix, x0, g, night, figures=("angel", "king"), room=40, w=13):
    """A phone's lancets, standing on a sill over row g, each saint on the ground of glass it has in the east
    window, which it lays on the sill by day; built to the `room` the words leave: saints in their windows with
    36 rows or more, plain glass with fewer, nothing under 18."""
    if room < 18:
        return None
    n = len(figures)
    span = n * w - (n - 1)
    with_figures = room >= 36
    h = min(46, room - 8) if with_figures else min(22, room - 6)
    foot = sill(p, x0 - 2, x0 + span + 2, g, night,
                [(x0 + i * (w - 1) + 2, w - 4, GROUNDS[who]) for i, who in enumerate(figures)])
    for i, who in enumerate(figures):
        lancet(p, x0 + i * (w - 1), foot, w, h, night, glaze=GROUNDS[who], figure=who if with_figures else None,
               motion=False, lattice=not with_figures or h > 40)
    return (x0 - 2, x0 + span + 2)


# --------------------------------------------------------------------------- small pieces for the elements
def pane_cell(q: Pix, ox, oy, night):
    """A pane 11 by 15 a numeral is leaded into: the came round it, the glass within, a streak where it runs
    thin and a dark rim where it meets the lead."""
    Ld, Gr, Du = RAMP["lead"], RAMP["grisaille"], RAMP["dusk"]
    face, thin, rim = (Du[2], Du[3], Du[1]) if night else (Gr[5], Gr[6], Gr[3])
    for yy in range(15):
        for xx in range(11):
            if xx in (0, 10) or yy in (0, 14):
                c = Ld[0 if night else 1]
            elif xx in (1, 9) or yy in (1, 13):
                c = rim
            elif (xx + yy) in (5, 6):
                c = thin
            else:
                c = face
            q.px(ox + xx, oy + yy, c)


def lancet_bar(p: Pix, bx, base, bw, v, night, glaze):
    """A week's commits as a lancet window of coloured glass standing on the base line, `bw` wide and `v` tall."""
    if v <= 2 or bw < 3:
        _, body, _ = glaze_tones(glaze, night)
        p.rect(bx, base - v, bw, v, body)
        return
    lancet(p, bx, base, bw, v, night, glaze=glaze, motion=False, glow=False, lattice=bw >= 8)


def came(p: Pix, x0, x1, y, night, L="base"):
    """A lead came along a row, lit along its top and dark along its foot."""
    Ld = RAMP["lead"]
    k = 1 if night else 0
    p.hline(x0, x1, y, Ld[4 + k], L)
    p.hline(x0, x1, y + 1, Ld[1 + k], L)


def came_tones(night: bool) -> tuple:
    """A came's face and the shaded side under it: dark grey lead by day, lit a little by night so it shows on the
    dark glass."""
    Ld = RAMP["lead"]
    return (Ld[5], Ld[3]) if night else (Ld[3], Ld[1])


def solder(p: Pix, x, y, night, L="base"):
    """A blob of solder where cames meet, a cross of five pixels centred on (x, y), its tin lit on its upper
    left."""
    Ld = RAMP["lead"]
    body, lit = (Ld[5], Ld[6]) if night else (Ld[4], Ld[6])
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, body, L)
    p.px(x - 1, y, lit, L)
    p.px(x, y - 1, lit, L)


def came_wire(p: Pix, cells, night):
    """A schematic's wire as a lead came: the wire the layout draws is its face, and this lays its shaded side
    along it (under a run that goes across, beside one that goes down) and a blob of solder where it leaves its
    card and at every bend."""
    _, shade = came_tones(night)
    kinds: dict = {}
    for (x, y, d) in cells:
        kinds.setdefault((x, y), set()).add(d)
        if d == "h":
            p.px(x, y + 1, shade)
        else:
            p.px(x + 1, y, shade)
    if cells:
        solder(p, cells[0][0], cells[0][1], night)
    for (x, y), ds in kinds.items():
        if len(ds) == 2:
            solder(p, x, y, night)


def leaded_card(p: Pix, x, y, w, h, night, seed, ink):
    """A schematic's card as a leaded panel: a came of lead round it, its icon's cell glazed as a pane of coloured
    glass with the icon leaded into it in white glass, a diamond quarry of gold glass leaded into the pane's
    corners above and below the icon, a came between the pane and the card's pale glass, and solder where the
    cames meet. `ink` is the colour the layout drew the icon in, which this takes up and leads in again."""
    Ld, Gr = RAMP["lead"], RAMP["grisaille"]
    face, _ = came_tones(night)
    outer = Ld[0 if night else 1]
    icon_y = y + (h - 7) // 2
    icon = {(xx, yy) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9) if p.get(xx, yy) == ink}
    glaze = ("cobalt", "ruby", "emerald", "amber", "violet")[seed % 5]
    dark, body, thin = glaze_tones(glaze, night)
    gd, gb, gt = glaze_tones("gold" if glaze != "amber" else "cobalt", night)
    x0, x1, y0, y1 = x + 2, x + 10, y + 2, y + h - 3
    quarries = [(x + 6, y0 + 3), (x + 6, y1 - 3)] if icon_y - y0 >= 7 else []
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            qx, qy = min(quarries, key=lambda q: abs(xx - q[0]) + abs(yy - q[1])) if quarries else (-99, -99)
            d = abs(xx - qx) + abs(yy - qy)
            if (xx, yy) in icon:
                c = Gr[6 if not night else 5]
            elif any((xx + dx, yy + dy) in icon for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c = outer
            elif d == 3:
                c = outer
            elif d < 3:
                c = gt if d == 2 and xx <= qx and yy <= qy else gb
            elif xx == x1 or yy == y1:
                c = dark
            else:
                c = thin if (xx - x0) + (yy - y0) in (3, 4) else body
            p.px(xx, yy, c)
    p.box(x, y, w, h, outer)
    p.vline(x + 11, y + 1, y + h - 1, outer)
    p.vline(x + 12, y + 2, y + h - 2, face)
    for sx, sy in ((x + 11, y + 1), (x + 11, y + h - 2)):
        solder(p, sx, sy, night)


def bead(p: Pix, x, y, glaze, night, L="base"):
    """A bead of glass 3 by 3 centred on (x, y), with its glint."""
    dark, body, thin = glaze_tones(glaze, night)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        p.px(x + dx, y + dy, body, L)
    p.px(x, y, body, L)
    p.px(x - 1, y - 1, thin, L)
    p.px(x + 1, y + 1, dark, L)


def glass_release(p: Pix, x, gy, kind, glaze, night, L="base"):
    """A release on the timeline's came, threaded on it so it keeps under what the release brought, which the
    sheet sets from six rows over the came: a roundel of glass leaded in, a bigger one with a gold cross for a
    big release, a bead on a short stem for a patch, an empty ring of lead for one still to come, and a small
    lancet of stone for the repository's founding."""
    Ld, G = RAMP["lead"], RAMP["gold"]
    k = 1 if night else 0
    if kind == "made":
        S = stone_ramp(night)
        for yy in range(gy - 4, gy + 1):
            for xx in range(x - 2, x + 3):
                p.px(xx, yy, S[(6 if xx == x - 2 else 4 if xx < x + 2 else 2) - k], L)
        p.hline(x - 1, x + 2, gy - 5, S[5 - k], L)
        for yy in range(gy - 3, gy):
            p.px(x, yy, RAMP["ruby"][3 + k], L)
        return
    if kind == "minor":
        p.vline(x, gy - 2, gy + 1, Ld[3 + k], L)
        bead(p, x, gy - 3, glaze, night, L)
        return
    if kind == "next":
        for yy in range(gy - 3, gy + 5):
            for xx in range(x - 3, x + 4):
                d = math.hypot(xx + 0.5 - x - 0.5, yy + 0.5 - (gy + 1))
                if 2.2 <= d <= 3.5:
                    p.px(xx, yy, Ld[3 + k], L)
        return
    r = 4.2 if kind == "big" else 3.4
    disc(p, x + 0.5, gy + 1, r, glaze, night, L)
    if kind == "big":
        for d in range(-2, 3):
            p.px(x + d, gy + 1, G[4 + k], L)
            p.px(x, gy + 1 + d, G[4 + k], L)


def today_candle(p: Pix, x, y, night, L="base"):
    """A candle standing on the timeline's came at today, burning by night: three rows of wax and a full flame
    where the rows over it are free, and where a release's note sits over today a stub of wax with a small flame
    that keeps a row under the note."""
    Gr, Ld = RAMP["grisaille"], RAMP["lead"]
    tall = p.clear_of_words(x - 3, y - 10, x + 4, y)
    h = 3 if tall else 2
    for yy in range(y - h, y):
        p.px(x - 1, yy, Gr[6 if not night else 5], L)
        p.px(x, yy, Gr[6 if not night else 5], L)
        p.px(x + 1, yy, Gr[4 if not night else 3], L)
    p.px(x, y - h - 1, Ld[2], L)
    if night and tall:
        flame(p, x, y - h - 1, flicker=False, reach=6, halo=False, L=L)
    elif night:
        F = RAMP["candle"]
        for dx, dy, t in ((0, 0, 6), (-1, -1, 4), (0, -1, 5), (1, -1, 4), (0, -2, 3)):
            p.px(x + dx, y - h - 1 + dy, F[t], L)
        lamp(p, x + 0.5, y - h - 2, 5, 0, {(x, y - h - 1)})


def halo_head(p: Pix, cx, cy, i, night, bot=False, L="base"):
    """A contributor as a saint's head in glass: a face under hair in its own colour, on a ground of coloured
    glass by turns, with a gold halo behind it and the lead round every piece. A bot is a hooded brother in
    grey glass with no halo."""
    G, F, Ld, Gr, U = RAMP["gold"], RAMP["flesh"], RAMP["lead"], RAMP["grisaille"], RAMP["umber"]
    k = 1 if night else 0
    grounds = ("cobalt", "ruby", "emerald", "violet")
    hair = (U[3], RAMP["amber"][4], U[1], RAMP["ruby"][2])
    glaze = "lead" if bot else grounds[i % 4]
    dark, body, thin = (Ld[2], Ld[3], Ld[5]) if bot else glaze_tones(glaze, night)
    for yy in range(cy - 8, cy + 8):
        for xx in range(cx - 7, cx + 8):
            edge = yy in (cy - 8, cy + 7) or xx in (cx - 7, cx + 7)
            p.px(xx, yy, Ld[1] if edge else dark if (yy == cy - 7 or xx == cx - 6 or xx == cx + 6 or yy == cy + 6)
                 else thin if (xx - yy) % 7 == 0 else body, L)
    if not bot:
        for yy in range(cy - 8, cy + 4):
            for xx in range(cx - 6, cx + 7):
                d = math.hypot(xx + 0.5 - cx - 0.5, yy + 0.5 - (cy - 2.5))
                if d <= 5.4:
                    p.px(xx, yy, G[2 + k] if d > 4.5 else G[4 + k] if (xx + yy) % 3 else G[5 + k], L)
    face = [".HHHHH.", "HHHHHHH", "HFFFFFH", "FFEFEFF", ".FFfFF.", ".FFFFF.", "..FFF..", ".NNNNN.", ".NNNNN."]
    pal = {"H": Gr[4] if bot else hair[i % 4], "F": F[4], "f": F[2], "E": Ld[1],
           "N": Gr[3] if bot else (RAMP["ruby"], RAMP["cobalt"], RAMP["amber"], RAMP["emerald"])[(i + 1) % 4][3 + k]}
    if bot:
        face = ["..HHH..", ".HHHHH.", "HHHHHHH", "HHFFFHH", "HFEFEFH", "HFFfFFH", "HHFFFHH", "HHHHHHH", ".HHHHH."]
    x0, y0 = cx - 3, cy - 6
    for j, row in enumerate(face):
        for ii, ch in enumerate(row):
            if ch != ".":
                p.px(x0 + ii, y0 + j, pal[ch], L)
    for j, row in enumerate(face):
        for ii, ch in enumerate(row):
            if ch == ".":
                continue
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                jj, i2 = j + dy, ii + dx
                if not (0 <= jj < len(face) and 0 <= i2 < len(row) and face[jj][i2] != "."):
                    p.px(x0 + i2, y0 + jj, Ld[0 if night else 1], L)


MITRE = ["...#...", "..#.#..", ".#...#.", "#.....#", "#######", ".#####.", ".#...#."]


def mitre(p: Pix, x, y, night, L="base"):
    """A bishop's mitre, 7 by 7, of white glass with a band of gold and a ruby at its peak."""
    Gr, G, R, Ld = RAMP["grisaille"], RAMP["gold"], RAMP["ruby"], RAMP["lead"]
    k = 1 if night else 0
    for j in range(6):
        for i in range(7):
            d = abs(i - 3)
            if j == 0 and d == 0 or j == 1 and d <= 1 or j == 2 and d <= 2 or j >= 3:
                c = Gr[6] if (i < 3 or j < 2) else Gr[4]
                if j == 4:
                    c = G[4 + k]
                if i in (1, 5) and j in (2, 3):
                    c = G[3 + k]
                p.px(x + i, y + j, c, L)
    p.px(x + 3, y, R[4], L)
    p.px(x + 2, y + 6, G[3 + k], L)
    p.px(x + 4, y + 6, G[3 + k], L)
    for j in range(7):
        for i in range(7):
            d = abs(i - 3)
            inside = j == 0 and d == 0 or j == 1 and d <= 1 or j == 2 and d <= 2 or 3 <= j <= 5
            if not inside:
                continue
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                jj, ii = j + dy, i + dx
                dd = abs(ii - 3)
                ins = 0 <= jj and (jj == 0 and dd == 0 or jj == 1 and dd <= 1 or jj == 2 and dd <= 2 or 3 <= jj <= 5)
                if not ins and jj <= 6:
                    p.px(x + ii, y + jj, Ld[1], L)


def tracery_ring(p: Pix, cx, cy, r0, r1, n, night, L="base"):
    """The tracery round a seal: a ring of stone pierced with petals of ruby and cobalt glass between spokes of
    lead, from r0 to r1."""
    S, Ld = stone_ramp(night), RAMP["lead"]
    k = -1 if night else 0
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 1):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not (r0 - 0.5 <= rho <= r1 + 0.5):
                continue
            th = math.atan2(dy, dx)
            seg = (th + math.pi) / (2 * math.pi) * n
            near = abs(seg - round(seg)) * (2 * math.pi / n) * rho
            if rho > r1 - 1.5 or rho < r0 + 0.5:
                facing = dx * LX + dy * LY > 0.3 * rho
                c = S[(5 if facing else 3) + k] if rho > r1 - 1.5 else Ld[1]
            elif near < 0.6:
                c = Ld[1]
            else:
                glaze = ("ruby", "cobalt")[int(seg) % 2]
                dark, body, thin = glaze_tones(glaze, night)
                c = thin if (xx - yy) % 5 == 0 else body
                if rho > r1 - 2.5 or rho < r0 + 1.5 or near < 1.2:
                    c = dark
            p.px(xx, yy, c, L)


def silk_tails(p: Pix, x, y, w, h, night, tail=4, L="base"):
    """The ends of a ribbon of violet silk either side of its block from x to x + w: each falls a row as it
    leaves the block and is cut square, lit along its top and shaded along its foot."""
    V = RAMP["violet"]
    for j in range(h):
        drop = 1 if j else 0
        for i in range(tail):
            c = V[1] if i == 0 else V[4] if j == 0 else V[0] if j == h - 1 else V[2]
            p.px(x - 1 - i, y + j + (drop if i >= 2 else 0), c, L)
            p.px(x + w + i, y + j + (drop if i >= 2 else 0), c, L)


def window_frame(p: Pix, night: bool):
    """A placard as a lancet in its stone frame: the arcade, the mullions and the sill of the set's border, and
    inside them a border of small panes of coloured glass leaded round the window."""
    frame(p, night, uid="pl")
    Ld = RAMP["lead"]
    k = 1 if night else 0
    w, h = p.w, p.h
    glazes = ("ruby", "cobalt", "amber", "emerald")
    for yy in range(TOP + 1, h - FOOT):
        i = (yy - TOP - 1) // 4
        _, body, thin = glaze_tones(glazes[i % 4], night)
        for xx in (4, w - 6):
            p.px(xx, yy, Ld[1 + k] if (yy - TOP - 1) % 4 == 0 else body)
            p.px(xx + 1, yy, Ld[1 + k] if (yy - TOP - 1) % 4 == 0 else thin if xx == 4 else body)
    p.vline(6, TOP + 1, h - FOOT, Ld[1 + k])
    p.vline(w - 7, TOP + 1, h - FOOT, Ld[1 + k])
    for xx in range(7, w - 7):
        i = (xx - 7) // 4
        _, body, thin = glaze_tones(glazes[(i + 2) % 4], night)
        p.px(xx, TOP + 1, Ld[1 + k] if (xx - 7) % 4 == 0 else thin)
        p.px(xx, TOP + 2, Ld[1 + k] if (xx - 7) % 4 == 0 else body)
        p.px(xx, TOP + 3, Ld[1 + k])


# --------------------------------------------------------------------------- icons
# Icons for the link buttons, 9 by 7, bold enough to read at the kit's size: a rose window, a fleur-de-lis, a
# mitre and a chalice. Tones: `#` the button's letters, `g G` gold, `r` ruby, `b` cobalt, `w` white glass,
# `l` lead.
ICONS = {
    "rose": [".ll###ll.", "l#rbrbr#l", "l#b###b#l", "##r#G#r##", "l#b###b#l", "l#rbrbr#l", ".ll###ll."],
    "fleur": ["....G....", "...GGG...", ".G.GGG.G.", "GGG.G.GGG", ".GGGGGGG.", "...GgG...", "..Gg.gG.."],
    "mitre": ["....w....", "...www...", "..wwwww..", ".wwwwwww.", "wwGGGGGww", ".wwwwwww.", ".ww...ww."],
    "chalice": ["GGGGGGGGG", ".GrGGGrG.", "..GGGGG..", "...GGG...", "....G....", "...gGg...", ".GGGGGGG."],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a button by day or by night."""
    G, R, B, Gr, Ld = RAMP["gold"], RAMP["ruby"], RAMP["cobalt"], RAMP["grisaille"], RAMP["lead"]
    k = -1 if night else 0
    return {"#": ink, "G": G[4 + k], "g": G[2 + k], "r": R[4 + k], "b": B[5 + k], "w": Gr[6 + k], "l": Ld[1]}


# --------------------------------------------------------------------------- small pieces for the banners
HEART = [".bbb.bbb.", "bbtbbbbbb", "bbbbbbbbb", ".bbbbbbb.", "..bbbbb..", "...bbb...", "....d...."]


def heart(p: Pix, x, y, L="base"):
    """A heart of ruby glass, 7 by 6, leaded round, lit on its upper-left lobe."""
    dark, body, thin = glaze_tones("ruby", False)
    art = [".bb.bb.", "btbbbbb", "bbbbbbd", ".bbbbd.", "..bbd..", "...d..."]
    p.sprite(x, y, art, {"b": body, "t": thin, "d": dark}, 1, L)


def glass_bar(p: Pix, x0, y0, w, h, period=5, night=False, L="base"):
    """A graphic scale as a rule of lead and glass: panes of ruby and cobalt by turns, a came between each pair,
    each pane lit along its top where the glass runs thin and dark along its foot, and lit from inside by
    night."""
    Ld = RAMP["lead"]
    for xx in range(x0, x0 + w):
        i = (xx - x0) // period
        if (xx - x0) % period == 0 and xx > x0:
            p.vline(xx, y0, y0 + h, Ld[0 if night else 1], L)
            continue
        dark, body, thin = glaze_tones(("ruby", "cobalt")[i % 2], night)
        for yy in range(y0, y0 + h):
            p.px(xx, yy, thin if yy == y0 else dark if yy == y0 + h - 1 else body, L)


def gold_star(p: Pix, cx, cy, night, L="base"):
    """A star of gold glass, 5 by 5, for the busiest week."""
    G = RAMP["gold"]
    k = 1 if night else 0
    for d in range(-2, 3):
        p.px(cx + d, cy, G[4 + k] if d else G[6], L)
        p.px(cx, cy + d, G[4 + k] if d else G[6], L)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        p.px(cx + dx, cy + dy, G[2 + k], L)
