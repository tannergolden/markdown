# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Architect set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is a wall of the white room where the year is reviewed: warm white by day, laid in large panels with fine
joints between them, and grey-black by night, lit only by its screens. Its frame is a stack of small televisions in
pale grey plastic, a column of them down each side and a row along the foot, their tubes glowing, and along a
header's top a row of larger sets, as wide as the screens of the wall under them, switched off but for a dim test card
in every third, parting either side of the month's mark, which sits among them as one more screen. Across a header's
sky, behind the title, the room's far wall is a wall of screens (`sky_wall`), warm grey glass by day and dark by night,
a light sweeping slowly across it and a few of its screens left on showing pictures of the year (`lit_screens`).
Titles are a video wall: every unit of a letter a little television, its case casting a shadow on the wall by day, and
by night its screen's light blooming round it.

A header opens on the year in review (see `screens`). At its left three big sets in charcoal plastic rise the height of
the wall, showing the code falling, the two pills held out and the white rabbit, with smaller sets above them where a
tall header leaves room. At its right four more show the train, the hovercraft, the pods and the chateau's chandelier,
over the console, a vision mixer with its monitor showing the room itself, its meters, rows of keys and a pen lying on
its ledge, and before it the Architect, seated in his tall white wingback; cables wiring the sets together lie along
the floor between them. Every screen burns on the hand's phosphor; by night their light falls on the plastic, the
leather, the steel and the Architect near them and pools on the floor, and in a moving header the pictures flicker, the
code runs down January's tube, the console's keys blink and a ripple of snow passes through the year's sets in turn.

Under the row of sets along the top a cable is slung between grey ties, a tally light under each (`cable_garland`),
parting round the month's mark. The section header stands the Architect before a tower of sets three across at its
right (`audience`), his pen held up to the screens and the tower's cables rising from it to the ceiling, and the strip
stands his white wingback empty before a column of sets (`vigil`), his pen on its seat, the column's cables rising
over it so that it stands the strip's full height. On a phone the whole room stands under the words (`phone_room`),
the Architect stands before his tower with his chair waiting behind him (`phone_audience`), and his empty chair keeps
its vigil by its column with a big set showing the code at the left (`phone_vigil`). Everything is shaded from the one
light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Paint, Pix, num
from ..hand import MATRIX
from . import screens as S
from .palette import C, NIGHT_SKY, RAMP, ramp_for, step

WALL, DUSK, PLASTIC, GLASS, SHELL = RAMP["wall"], RAMP["dusk"], RAMP["plastic"], RAMP["glass"], RAMP["shell"]
SUIT = RAMP["suit"]
LEATHER, STEEL, BRASS, FLAME = RAMP["leather"], RAMP["steel"], RAMP["brass"], RAMP["flame"]
EDGE = 4          # the frame's width down a sheet's sides and along its foot
TOP = 13          # the depth of the row of televisions along a header's top
PANEL_W, PANEL_H = 52, 30     # the wall's panels


# --------------------------------------------------------------------------- the room
def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the room's wall, warm white by day and by night grey-black, palest across its
    middle where the screens' light falls, laid in large panels with a fine joint between them, drawn once a file as a
    pattern."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
        joint = DUSK[4]
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
        joint = WALL[4]
    p.defs.append(f'<pattern id="{uid}w" x="{(w % PANEL_W) // 2}" y="1" width="{PANEL_W}" height="{PANEL_H}" '
                  f'patternUnits="userSpaceOnUse"><path stroke="{joint}" d="M0 .5h{PANEL_W}M.5 1v{PANEL_H - 1}"/>'
                  f'</pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}w)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the band of the dark room by night, the warm white wall by day."""
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        return next(NIGHT_SKY[i] for i in range(n) if y < edges[i + 1] or i == n - 1)
    return C["paper"]


# --------------------------------------------------------------------------- the wall of screens across the sky
CELL_W, CELL_H = 22, 14       # a screen of the wall: its tube twenty units by twelve in a bezel a unit wide
SWEEP = 32.0                  # seconds the light takes to run across the wall's screens and rest: a slow sweep


def axis(p: Pix) -> int:
    """The column the wall's grid is laid from, so that one of its screens' slots stands under the month's mark."""
    return p.w // 2 - CELL_W // 2


def _cell(night: bool, lit: bool = False) -> dict:
    """One screen of the wall across the sky, as {(x, y): colour}: its bezel lit along its top and left and shaded along
    its right and foot, the shadow of its lip along the top and left of the glass, the glass the room's own warm grey by
    day, so the wall sits in the white room rather than cooling it, and dark by night, with a glare across its upper
    left, or with `lit` catching the light that sweeps across the wall."""
    if night:
        lit_edge, shade, recess = DUSK[5], DUSK[0], DUSK[0]
        glass, glare = (GLASS[3], GLASS[5]) if lit else (DUSK[1], DUSK[4])
    else:
        lit_edge, shade, recess = WALL[6], WALL[2], WALL[2]
        glass, glare = (WALL[4] if lit else WALL[3]), C["white"]
    out = {}
    for y in range(CELL_H):
        for x in range(CELL_W):
            if x == 0 or y == 0 or (x == 1 and y == 1):
                c = lit_edge
            elif x == CELL_W - 1 or y == CELL_H - 1 or (x in (1, CELL_W - 2) and y in (1, CELL_H - 2)):
                c = shade
            elif x == 1 or y == 1:
                c = recess
            else:
                c = glass
            out[(x, y)] = c
    for xy in ((4, 2), (3, 3), (2, 4)):
        out[xy] = glare
    return out


def wall_rects(p: Pix, end: int) -> list:
    """The boxes the wall across the sky fills, from under the frame's row to row `end`, as (x0, y0, x1, y1): whole rows
    of screens, the slot under the month's mark left empty in the first, for the mark is the screen that hangs there."""
    rows = (end - TOP) // CELL_H
    if rows < 1:
        return []
    y1, a = TOP + rows * CELL_H, axis(p)
    out = [(EDGE, TOP, a, TOP + CELL_H), (a + CELL_W, TOP, p.w - EDGE, TOP + CELL_H)]
    if rows > 1:
        out.append((EDGE, TOP + CELL_H, p.w - EDGE, y1))
    return out


def sky_wall(p: Pix, night: bool, motion: bool, avoid) -> list:
    """The room's far wall across the sky, behind the title, a wall of screens switched off: rows of tubes in
    their bezels from under the frame's row down to a ledge above the words under the title (the second box of
    `avoid`), their glass a warm grey by day and dark by night. In a moving header the light sweeps slowly across it,
    a column of screens catching it at a time, once every `SWEEP` seconds. Drawn as patterns, once a file. Returns the
    boxes it fills."""
    if p.w < 300 or len(avoid) < 2:
        return []
    rects = wall_rects(p, avoid[1][1] - 2)
    if not rects:
        return []
    a = axis(p)
    tile = _pattern(p, "vw", CELL_W, CELL_H, _cell(night), x0=a, y0=TOP)
    for (x0, y0, x1, y1) in rects:
        p.under.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{tile})"/>')
    foot = rects[-1][3]
    p.under.append(f'<path stroke="{WALL[2] if not night else DUSK[5]}" d="M{EDGE} {foot}.5h{p.w - 2 * EDGE}"/>')
    if motion:
        lit = _pattern(p, "vl", CELL_W, CELL_H, _cell(night, lit=True), x0=a, y0=TOP)
        first = a - ((a - EDGE) // CELL_W + 2) * CELL_W
        steps = (p.w - first) // CELL_W + 1
        xs = [first + i * CELL_W for i in range(steps)]
        xs += [xs[-1]] * (len(xs) // 2)
        cid = f"vs{len(p.raws)}"
        boxes = "".join(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{lit})"/>'
                        for (x0, y0, x1, y1) in rects)
        p.raw(-19, f'<clipPath id="{cid}"><rect x="{xs[0]}" y="{TOP}" width="{2 * CELL_W}" height="{foot - TOP}">'
                   f'<animate attributeName="x" values="{";".join(str(x) for x in xs)}" dur="{num(SWEEP)}s" '
                   f'repeatCount="indefinite" calcMode="discrete"/></rect></clipPath><g clip-path="url(#{cid})">'
                   f'{boxes}</g>', "")
    return rects


def lit_screens(p: Pix, night: bool, motion: bool, rects: list, avoid, months) -> int:
    """A few of the wall's screens left on, wherever the title and the scenes at the sides leave a whole screen clear,
    never past the right end of the words under the title, where an H2's or H3's hero stands, the farthest from the
    title first, two by day and more by night: each showing one of `months`' pictures dimly in the phosphor, flickering
    on its own in a moving header, its tube joining those the ripple of snow passes through. Returns how many it lit."""
    if not rects:
        return 0
    a = axis(p)
    title = avoid[0]
    slots = []
    for (x0, y0, x1, y1) in rects:
        for y in range(y0, y1, CELL_H):
            k = -((a - x0) // CELL_W)
            x = a + k * CELL_W
            while x + CELL_W <= x1:
                clear = 58 <= x and x + CELL_W <= min(p.w - 58, avoid[1][2])
                clear = clear and not (x < title[2] + 2 and title[0] - 2 < x + CELL_W and y < title[3] + 2
                                       and title[1] - 2 < y + CELL_H)
                if clear and x >= x0:
                    slots.append((x, y))
                x += CELL_W
    slots.sort(key=lambda q: (abs(q[0] + CELL_W / 2 - p.w / 2) * -1, q[1]))
    dim = {1: FLAME[0], 2: FLAME[0], 3: FLAME[1], 4: FLAME[1], 5: FLAME[2], 6: FLAME[3]}
    n = 0
    for (x, y), name in zip(slots, months[:6 if night else 2]):
        tubes(p)[S.ORDER.index(name)] = (x + 1, y + 1, S.W, S.H)
        p.shapes[p.layer("base")].append(f'<rect x="{x + 1}" y="{y + 1}" width="{S.W}" height="{S.H}" '
                                         f'fill="{GLASS[2]}"/>')
        L = p.flicker(n) if motion else "base"
        for (i, j), t in S.cells(name).items():
            p.px(x + 1 + i, y + 1 + j, dim[t], L)
        n += 1
    return n


# --------------------------------------------------------------------------- the frame: a stack of televisions
def _case(night: bool, shell: bool = False) -> dict:
    """The tones of a television's case: its outline, its face, its lit and its shaded edges, in charcoal plastic, or
    with `shell` in the frame's pale grey by day; both dim by night."""
    if night:
        return {"o": PLASTIC[0], "c": PLASTIC[1], "L": PLASTIC[3], "s": PLASTIC[0]}
    if shell:
        return {"o": SHELL[0], "c": SHELL[4], "L": SHELL[6], "s": SHELL[2]}
    return {"o": PLASTIC[0], "c": PLASTIC[3], "L": PLASTIC[5], "s": PLASTIC[1]}


def _pattern(p: Pix, pid: str, w: int, h: int, cells: dict, x0=0, y0=0) -> str:
    """A pattern tile `w` by `h` from (x0, y0) of {(x, y): colour}, defined once a file. Returns its id."""
    key = ("pattern", pid)
    if key not in p.syms:
        rows: dict = {}
        for (x, y), c in cells.items():
            rows.setdefault(c, {}).setdefault(y, []).append(x)
        body = "".join(f'<path stroke="{c}" d="{Pix._d(r)}"/>' for c, r in rows.items())
        p.defs.append(f'<pattern id="{pid}" x="{x0}" y="{y0}" width="{w}" height="{h}" '
                      f'patternUnits="userSpaceOnUse">{body}</pattern>')
        p.syms[key] = pid
    return pid


def _lay(p: Pix, pid: str, x, y, w, h, L="base"):
    """A band laid in pattern `pid`."""
    if w > 0 and h > 0:
        L = p.layer(L)
        p.shapes[L].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')


def _tiny(night: bool, across: bool) -> dict:
    """One of the tiny sets the frame's sides and foot are stacked of: a case four units deep round a tube two units
    square, a glowing unit at its upper left; down the sides five units tall, along the foot six wide."""
    k = _case(night, shell=True)
    tube = (GLASS[2], GLASS[3])
    glow = FLAME[3] if night else FLAME[2]
    if across:
        rows = ["oLLLLo", "ogGgso", "ogggso", "ssssss"]
    else:
        rows = ["oLLs", "oGgs", "oggs", "ocss", "ssss"]
    pal = {"o": k["o"], "L": k["L"], "s": k["s"], "c": k["c"], "g": tube[0], "G": glow}
    return {(x, y): pal[ch] for y, row in enumerate(rows) for x, ch in enumerate(row)}


SET_W, SET_H = 12, 11         # a set in the row along a header's top


def _set_tile(night: bool, shell: bool = False) -> dict:
    """Three sets side by side, thirty-six units by eleven, as they stand along a header's top in the frame's pale
    grey (`shell`) and over the walls of sets in charcoal: one showing snow, one a test card of bars stepped down the
    phosphor, one the code falling, all of them dim beside the pictures of the year."""
    k = _case(night, shell)
    rnd = random.Random(7)
    cells = {}
    for n in range(3):
        x0 = n * SET_W
        for y in range(SET_H):
            for x in range(SET_W):
                if x in (0, SET_W - 1) or y in (0, SET_H - 1):
                    c = k["o"]
                elif y == 1 or x == 1:
                    c = k["L"]
                elif y == SET_H - 2 or x == SET_W - 2:
                    c = k["s"]
                else:
                    c = k["c"]
                cells[(x0 + x, y)] = c
        for y in range(2, SET_H - 3):
            for x in range(2, SET_W - 2):
                if (x in (2, SET_W - 3)) and y in (2, SET_H - 4):
                    continue
                if n == 0:
                    c = FLAME[rnd.choice((0, 0, 1, 1, 2))]
                elif n == 1:
                    c = FLAME[max(0, 4 - (x - 2) * 5 // (SET_W - 4))] if y < SET_H - 5 else GLASS[3]
                else:
                    c = FLAME[4] if (x * 7 + y * 3) % 11 == 0 else FLAME[1] if (x % 3 == 1 and y % 2) else GLASS[2]
                cells[(x0 + x, y)] = c
        cells[(x0 + SET_W - 4, SET_H - 3)] = k["s"]
        cells[(x0 + SET_W - 3, SET_H - 3)] = FLAME[4]
    return cells


def _band_tile(night: bool) -> dict:
    """Three of the sets along a header's top, side by side, each as wide as a screen of the wall under them, sixty-six
    units by eleven, in the frame's pale grey: their tubes switched off with a gleam across them, the middle one
    showing a dim test card, a power light at the foot of the first two."""
    k = _case(night, shell=True)
    dark, gleam = (GLASS[1], GLASS[4]) if night else (SHELL[1], SHELL[3])
    cells = {}
    for n in range(3):
        x0 = n * CELL_W
        for y in range(SET_H):
            for x in range(CELL_W):
                if x in (0, CELL_W - 1) or y in (0, SET_H - 1):
                    c = k["o"]
                elif y == 1 or x == 1:
                    c = k["L"]
                elif y == SET_H - 2 or x == CELL_W - 2:
                    c = k["s"]
                else:
                    c = k["c"]
                cells[(x0 + x, y)] = c
        for y in range(2, SET_H - 3):
            for x in range(3, CELL_W - 3):
                if x in (3, CELL_W - 4) and y in (2, SET_H - 4):
                    continue
                if n == 1:
                    c = FLAME[max(0, 3 - (x - 3) * 4 // (CELL_W - 6))] if y < SET_H - 5 else GLASS[3]
                else:
                    c = gleam if (x - y) in (2, 3) or (x - y) == 9 else dark
                cells[(x0 + x, y)] = c
        if n < 2:
            cells[(x0 + CELL_W - 4, SET_H - 3)] = FLAME[3]
    return cells


def frame(p: Pix, night: bool, header: bool = False, gap=None):
    """The frame: a stack of small televisions, a column of them down each side and a row along the foot, every tube
    glowing; along a header's top a row of larger sets, as wide as the screens of the wall under them and switched
    off, parting either side of `gap`, the columns the month's mark keeps clear, where it sits among them as one more
    screen."""
    w, h = p.w, p.h
    side = _pattern(p, "fs", 4, 5, _tiny(night, False))
    foot = _pattern(p, "ff", 6, 4, _tiny(night, True), x0=0, y0=h - 4)
    top = TOP if header else 4
    _lay(p, side, 0, top, 4, h - top - 4)
    _lay(p, side, w - 4, top, 4, h - top - 4)
    _lay(p, foot, 0, h - 4, w, 4)
    if not header:
        _lay(p, _pattern(p, "ft", 6, 4, _tiny(night, True)), 0, 0, w, 4)
        return
    k = _case(night, shell=True)
    a = axis(p)
    p.hline(0, w, 0, k["o"])
    tile = _pattern(p, "fr", 3 * CELL_W, SET_H, _band_tile(night), x0=a, y0=1)
    spans = [(0, w)] if gap is None else [(0, a), (a + CELL_W, w)]
    for x0, x1 in spans:
        _lay(p, tile, max(1, x0), 1, min(w - 1, x1) - max(1, x0), SET_H)
        p.hline(x0, x1, TOP - 1, k["o"])


# --------------------------------------------------------------------------- the titles: a video wall
def _screen_unit(r, c, scale, night):
    """The colour at row `r` and column `c` of a title's letter, in canvas units from its top-left: every unit of the
    face a little television. By day its charcoal case makes the letters, dark on the white room, lit along its top
    and left and shaded along its right and foot, with its screen glowing in the middle; by night the screens make
    them, burning in the dark, each in its case's thin dark line along its right and foot, white at its heart, and in
    letters two units to a font pixel, too small for that line, only a dark corner left between the screens."""
    i, j = c % scale, r % scale
    if night:
        if scale == 2:
            return PLASTIC[0] if i == j == 1 else FLAME[6] if i == j == 0 else FLAME[4]
        if scale > 2 and (i == scale - 1 or j == scale - 1):
            return PLASTIC[0]
        if scale < 2:
            return FLAME[6]
        mid = (scale - 1) / 2 - 0.5
        d = abs(i - mid) + abs(j - mid)
        return FLAME[6] if d < 0.6 else FLAME[5] if d < 1.6 else FLAME[4]
    if scale <= 2:
        return PLASTIC[2] if (scale == 2 and (i == 1 or j == 1)) else FLAME[3]
    if i == 0 or j == 0:
        return PLASTIC[4]
    if i == scale - 1 or j == scale - 1:
        return PLASTIC[1]
    return FLAME[4] if (i == 1 and j == 1) else FLAME[3]


SCREENS = Paint("tv", _screen_unit, period=4)
SCREENS3 = Paint("tv", _screen_unit, period=3)
SCREENS2 = Paint("tv", _screen_unit, period=2)


def video_title(p: Pix, x, y, s: str, scale: int, night: bool) -> int:
    """A title set as a video wall: every unit of its letters a little screen with a bright centre in a dark bezel
    (see `_screen_unit`), the letters outlined in the bezels' plastic and casting their shadow down and to the right
    on the wall behind them, and by night the screens' light blooming round them. A drawing made lighter to fit its
    budget leaves out the outline, four strokes a letter, for the screens' own bezels still edge every letter, and by
    night the shadow too, black on the dark wall. Returns its width."""
    casing = PLASTIC[0] if night else PLASTIC[1]
    paint = {4: SCREENS, 3: SCREENS3}.get(scale, SCREENS2)
    kw = dict(paint=paint, night=night)
    if not (p.lite and night):
        kw["shadow"] = DUSK[0] if night else SHELL[2]
    if not p.lite:
        kw["outline"] = casing
    if night:
        kw["glow"] = (FLAME[3], (0.05, 0.1, 0.17) if scale >= 3 else (0.14,))
    return p.text(x, y, s, casing, "57", scale, **kw)


def title_flicker(p: Pix, x, y, s: str, scale: int, night: bool, seed: int = 0):
    """In a moving header, a few of a title's screens flicker on their own, as the sets of a video wall do."""
    from ...holidays.pixel import FONTS, fold
    glyphs, _, space = FONTS["57"]
    units, cx = [], x
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        for r, cols in enumerate(glyphs[ch][1]):
            for col in cols:
                units.append((cx + col * scale, y + r * scale))
        cx += (glyphs[ch][0] + 1) * scale
    rnd = random.Random(seed + len(s))
    for n, (ux, uy) in enumerate(rnd.sample(units, min(7, len(units)))):
        L = p.flicker(n)
        for dy in range(scale - 1):
            for dx in range(scale - 1):
                p.px(ux + dx, uy + dy, FLAME[6] if (dx + dy) % 2 == 0 else FLAME[5], L)


# --------------------------------------------------------------------------- the screens' light
LIT = {c for name in ("plastic", "leather", "steel", "brass", "suit") for c in RAMP[name]}
PALE = set(LEATHER)


def lamp(p: Pix, cx, cy, r):
    """A screen at (cx, cy) whose light reaches `r` units: by night `screenlight` lays it on what stands near it."""
    p.lamps.append((cx, cy, r))


def _lit(c: str, d: float) -> str:
    """A colour `d` from a screen, 0 at it and 1 at the edge of its reach, in its light: pale plastic and leather near
    it take the phosphor's own green, and everything else is lit two tones lighter on its own ramp near it and one
    further off."""
    if c in PALE and d < 0.38:
        return FLAME[2] if ramp_for(c).index(c) < 4 else FLAME[3]
    return step(c, 2 if d < 0.55 else 1)


def screenlight(p: Pix, night: bool):
    """The finishing pass, by night only: every screen's light laid into the colours of what stands near it, the
    nearest screen's for each pixel, on the plastic of the sets, the chair's leather and the console's steel, and on a
    footer's console. The words take none of it."""
    if not night or not p.lamps:
        return
    for name in ("base", "foot"):
        cells = p.layers.get(name, {})
        for (x, y), c in list(cells.items()):
            if c not in LIT:
                continue
            best = None
            for (cx, cy, r) in p.lamps:
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.2) / r
                if d < 1 and (best is None or d < best):
                    best = d
            if best is not None:
                cells[(x, y)] = _lit(c, best)


# --------------------------------------------------------------------------- the televisions
TV_W, TV_H = 24, 18           # a set on the wall: its case round a tube twenty units by twelve
TUBE = (2, 2)                 # where the tube is in the set


def _tv_case(q: Pix, ox, oy, night: bool):
    """A set's case, drawn on `q` with its top-left at (ox, oy): white plastic lit along its top and left and shaded
    along its foot and right, the dark glass of its tube with a gleam at the tube's upper left, its knobs and its
    power light."""
    k = _case(night)
    for y in range(TV_H):
        for x in range(TV_W):
            if x in (0, TV_W - 1) and y in (0, TV_H - 1):
                continue
            if x in (0, TV_W - 1) or y in (0, TV_H - 1):
                c = k["o"]
            elif y == 1 or x == 1:
                c = k["L"]
            elif y == TV_H - 2 or x == TV_W - 2:
                c = k["s"]
            else:
                c = k["c"]
            q.px(ox + x, oy + y, c)
    tx, ty = TUBE
    for y in range(S.H):
        for x in range(S.W):
            if x in (0, S.W - 1) and y in (0, S.H - 1):
                continue
            q.px(ox + tx + x, oy + ty + y, GLASS[2])
    for (x, y) in ((1, 0), (0, 1), (2, 0), (0, 2)):
        q.px(ox + tx + x, oy + ty + y, GLASS[5])
    if night:
        for x in range(1, S.W - 1):
            q.px(ox + tx + x, oy + ty - 1, FLAME[1])
            q.px(ox + tx + x, oy + ty + S.H, FLAME[0])
        for y in range(1, S.H - 1):
            q.px(ox + tx - 1, oy + ty + y, FLAME[1])
            q.px(ox + tx + S.W, oy + ty + y, FLAME[0])
    for x in (TV_W - 8, TV_W - 6):
        q.px(ox + x, oy + TV_H - 3, k["s"])
    q.px(ox + TV_W - 4, oy + TV_H - 3, FLAME[4])


def tubes(p: Pix) -> dict:
    """The tubes of the sets showing the year on drawing `p`, by the index of the month each shows: where the ripple of
    snow passes (see `snow`)."""
    if not hasattr(p, "tubes"):
        p.tubes = {}
    return p.tubes


def tv(p: Pix, x, y, name: str, night: bool, motion: bool, phase=None):
    """A set on the wall with its top-left at (x, y), showing month `name`'s picture (see `screens`): its case drawn
    once a file and placed, its picture in the phosphor, flickering in a moving header when given a `phase`. Its tube
    joins those the ripple of snow passes through (see `snow`)."""
    p.stamp(("tv", night), lambda q, ox, oy: _tv_case(q, ox, oy, night), x, y, pad=24)
    lamp(p, x + TV_W / 2, y + TV_H / 2, 15)
    tx, ty = TUBE
    tubes(p)[S.ORDER.index(name)] = (x + tx, y + ty, S.W, S.H)
    L = p.flicker(phase) if (motion and phase is not None) else p.layer("tube", z=0.4)
    for (i, j), t in S.cells(name).items():
        p.px(x + tx + i, y + ty + j, FLAME[t], L)


BIG_W, BIG_H = 46, 29         # a big set: its case round a tube forty units by twenty-four
BIG_TUBE = (3, 2)             # where the tube is in a big set


def _big_case(q: Pix, ox, oy, night: bool):
    """A big set's case drawn on `q` with its top-left at (ox, oy): charcoal plastic lit along its top and left and
    shaded along its foot and right, the dark glass of its tube with a gleam at its upper left, by night the tube's
    light on the bezel round it, and along its foot a speaker's grille, its knobs and its power light."""
    k = _case(night)
    for y in range(BIG_H):
        for x in range(BIG_W):
            if x in (0, BIG_W - 1) and y in (0, BIG_H - 1):
                continue
            if x in (0, BIG_W - 1) or y in (0, BIG_H - 1):
                c = k["o"]
            elif y == 1 or x == 1:
                c = k["L"]
            elif y == BIG_H - 2 or x == BIG_W - 2:
                c = k["s"]
            else:
                c = k["c"]
            q.px(ox + x, oy + y, c)
    tx, ty = BIG_TUBE
    for y in range(S.BH):
        for x in range(S.BW):
            if not (x in (0, S.BW - 1) and y in (0, S.BH - 1)):
                q.px(ox + tx + x, oy + ty + y, GLASS[2])
    for (x, y) in ((1, 1), (2, 1), (3, 1), (1, 2), (1, 3), (2, 2)):
        q.px(ox + tx + x, oy + ty + y, GLASS[5])
    if night:
        for x in range(1, S.BW - 1):
            q.px(ox + tx + x, oy + ty - 1, FLAME[1])
            q.px(ox + tx + x, oy + ty + S.BH, FLAME[0])
        for y in range(1, S.BH - 1):
            q.px(ox + tx - 1, oy + ty + y, FLAME[1])
            q.px(ox + tx + S.BW, oy + ty + y, FLAME[0])
    for x in range(4, 20, 2):
        q.px(ox + x, oy + BIG_H - 3, k["s"])
    for x in (BIG_W - 11, BIG_W - 8):
        q.px(ox + x, oy + BIG_H - 3, k["s"])
        q.px(ox + x, oy + BIG_H - 4, k["L"])
    q.px(ox + BIG_W - 5, oy + BIG_H - 3, FLAME[4])


def big_tv(p: Pix, x, y, name: str, night: bool, motion: bool, phase=None):
    """A big set with its top-left at (x, y), showing month `name`'s big picture (see `screens.big`): January's the
    code running down its tube, the others still, flickering in a moving header when given a `phase`. Its tube joins
    those the ripple of snow passes through."""
    p.stamp(("big", night), lambda q, ox, oy: _big_case(q, ox, oy, night), x, y, pad=48)
    lamp(p, x + BIG_W / 2, y + BIG_H / 2, 26)
    tx, ty = BIG_TUBE
    tubes(p)[S.ORDER.index(name)] = (x + tx, y + ty, S.BW, S.BH)
    if name == "rain":
        code_tube(p, x + tx, y + ty, S.BW, S.BH, S.big_cells(name), motion)
        return
    L = p.flicker(phase) if (motion and phase is not None) else p.layer("tube", z=0.4)
    for (i, j), t in S.big_cells(name).items():
        p.px(x + tx + i, y + ty + j, FLAME[t], L)


def code_tube(p: Pix, ox, oy, w, h, cells: dict, motion: bool):
    """The code running down a tube `w` units by `h` with its top-left at (ox, oy), its streams `cells` {(x, y): tone}
    wrapping from the tube's foot to its top: stepping down a unit every eighth of a second, drawn once a file and laid
    twice, one tube's height apart, so the loop never shows its seam; the still twin holds it where it starts."""
    gid = f"ct{len(p.raws)}"
    p.defs.append(f'<g id="{gid}">{p.markup({q: FLAME[t] for q, t in cells.items()})}</g>')
    p.defs.append(f'<clipPath id="{gid}c"><path d="M{ox + 1} {oy}h{w - 2}v{h}h-{w - 2}zM{ox} {oy + 1}h{w}v{h - 2}'
                  f'h-{w}z"/></clipPath>')
    still = f'<g clip-path="url(#{gid}c)"><use href="#{gid}" x="{ox}" y="{oy}"/></g>'
    if not motion:
        p.raw(0.6, still, still)
        return
    values = ";".join(f"{ox} {oy + i}" for i in range(h))
    p.raw(0.6, f'<g clip-path="url(#{gid}c)"><g><use href="#{gid}"/><use href="#{gid}" y="-{h}"/>'
               f'<animateTransform attributeName="transform" type="translate" values="{values}" '
               f'dur="{num(h * 0.12)}s" repeatCount="indefinite" calcMode="discrete"/></g></g>', still)


SNOW = (8, 5)                 # the snow's tile, in units
RIPPLE = (0.6, 0.025)         # when in the hand's period the snow reaches January's set, and how long each set holds it


def snow(p: Pix, tubes: dict, motion: bool):
    """In a moving header, the sets losing their pictures to snow once in the hand's period, each for a moment in its
    turn by the month it shows, so that a ripple of snow runs through the year from January's set to December's, which
    holds it longest. `tubes` maps each month's index to its set's tube, (x, y, width, height). The snow is a pattern
    drawn once a file, laid on one tube's worth of glass that moves from set to set; the still twin has none."""
    if not motion or not tubes:
        return
    w, h = SNOW
    rnd = random.Random(12)
    tile = _pattern(p, "sn", w, h, {(i, j): FLAME[rnd.choice((0, 1, 3))] for i in range(w) for j in range(h)
                                    if rnd.random() < 0.7})
    order = sorted(tubes)
    start, hold = RIPPLE
    times = [start + i * hold for i in range(len(order))]
    end = times[-1] + 2 * hold
    keys = "0;" + ";".join(num(t) for t in times[1:])
    dur = num(MATRIX.glint)
    moves = ""
    for k, attr in enumerate(("x", "y", "width", "height")):
        values = [str(tubes[m][k]) for m in order]
        if len(set(values)) > 1:
            moves += (f'<animate attributeName="{attr}" values="{";".join(values)}" keyTimes="{keys}" dur="{dur}s" '
                      f'repeatCount="indefinite" calcMode="discrete"/>')
    x0, y0, w0, h0 = tubes[order[0]]
    p.raw(0.6, f'<g opacity="0"><rect x="{x0}" y="{y0}" width="{w0}" height="{h0}" fill="url(#{tile})">{moves}</rect>'
               f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{num(start)};{num(end)}" dur="{dur}s" '
               f'repeatCount="indefinite" calcMode="discrete"/></g>', "")


def small_sets(p: Pix, x0, x1, top, night: bool):
    """A row of the frame's larger sets (see `_set_tile`) from column x0 to x1, its top on row `top`: snow, the test
    card and the code."""
    tile = _pattern(p, f"fr{x0}", 3 * SET_W, SET_H, _set_tile(night), x0=x0, y0=top)
    _lay(p, tile, x0, top, x1 - x0, SET_H)
    lamp(p, (x0 + x1) / 2, top + SET_H / 2, 14)


def floor_pool(p: Pix, cx, g, rx, night: bool):
    """By night the screens' green light pooled on the floor at row g round column cx, `rx` units each way."""
    if night:
        p.halo(cx, g - 1.5, rx, 3, FLAME[3], (0.12, 0.2, 0.3), L="pool", shape=True)


def big_wall(p: Pix, x0, g, months, night: bool, motion: bool) -> tuple:
    """The big sets stacked at the left, standing on the floor at row g from column x0, as many as the wall leaves room
    for, `months`' first ones, each showing its month's big picture, the earliest at the top; over them, where the wall
    rises higher, rows of smaller sets up to the frame's row. By day they throw a shadow on the wall; by night their
    light blooms round them and pools on the floor at their foot. Returns the span of the floor it covers."""
    n = max(1, min(len(months), (g - TOP) // BIG_H))
    top = g - n * BIG_H + 1
    for i, name in enumerate(months[:n]):
        big_tv(p, x0, top + i * BIG_H, name, night, motion, phase=None if name == "rain" else (i + 1) % 3)
    high = top
    while high - SET_H > TOP:
        high -= SET_H
        small_sets(p, x0 + (BIG_W - 3 * SET_W) // 2, x0 + (BIG_W + 3 * SET_W) // 2, high, night)
    if not night:
        p.vline(x0 + BIG_W, top + 1, g + 1, WALL[3])
    else:
        p.halo(x0 + BIG_W / 2, (top + g) / 2, BIG_W / 2 + 2, (g - top) / 2, FLAME[3], (0.06, 0.12, 0.2))
        floor_pool(p, x0 + BIG_W + 4, g, 20, night)
    return (x0 - 1, x0 + BIG_W + 1)


# --------------------------------------------------------------------------- the console and the chair
def console(p: Pix, x0, x1, g, night: bool, motion: bool, monitor: str):
    """The Architect's console from column x0 to x1, standing on the floor at row g: a vision mixer's desk in charcoal
    plastic, its sloped top set with rows of keys, a few of them lit and blinking in a moving header, a fountain pen
    lying on its ledge, its barrel brass and its cap black, its body on a plinth of steel; on it a row of meters and a
    monitor showing month `monitor`'s picture."""
    k = _case(night)
    top = g - 13                       # the desk's ledge
    tv(p, x0 + (x1 - x0 - TV_W) // 2, top - 6 - TV_H, monitor, night, motion)
    for y in range(top - 6, top - 3):
        for x in range(x0 + 2, x1 - 2):
            p.px(x, y, k["o"] if y == top - 6 or x in (x0 + 2, x1 - 3) else k["c"])
    for j, x in enumerate(range(x0 + 4, x1 - 4)):
        p.px(x, top - 5, FLAME[3 + (j % 3 == 0)] if (j * 5) % 7 < 4 else GLASS[3])
    for j in range(3):
        y = top - 1 - j
        for x in range(x0 + j, x1 - j):
            p.px(x, y, k["L"] if j == 2 else k["c"])
        p.px(x0 + j, y, k["L"])
        p.px(x1 - j - 1, y, k["s"])
    rnd = random.Random(x0 * 3)
    for j in (0, 2):
        y = top - 1 - j
        for i, x in enumerate(range(x0 + 2 + j, x1 - 2 - j, 2)):
            r = rnd.random()
            if r < 0.25:
                p.px(x, y, FLAME[4], p.blink(i) if (motion and r < 0.1) else "base")
            else:
                p.px(x, y, PLASTIC[0] if night else PLASTIC[2])
    p.hline(x0, x1, top, k["L"])
    p.hline(x0, x1, top + 1, k["s"])
    p.hline(x0 + 3, x0 + 12, top - 1, BRASS[5])
    p.hline(x0 + 3, x0 + 12, top, BRASS[3])
    p.hline(x0 + 9, x0 + 12, top - 1, STEEL[2])
    p.hline(x0 + 9, x0 + 12, top, STEEL[0])
    p.px(x0 + 2, top, BRASS[6])
    for y in range(top + 2, g - 1):
        for x in range(x0 + 1, x1 - 1):
            p.px(x, y, k["L"] if x == x0 + 1 else k["s"] if x == x1 - 2 else k["c"])
        p.px(x0, y, k["o"])
        p.px(x1 - 1, y, k["o"])
    for x in range(x0 + 4, x1 - 4, 6):
        p.vline(x, top + 4, g - 3, k["s"])
    p.hline(x0, x1, g - 1, STEEL[3])
    p.hline(x0, x1, g, STEEL[1])


# The white wingback, 26 units wide and 47 tall, seen from its side facing left toward the screens: its tall back
# buttoned in white leather with a wing at its head, its seat and cushion, and its legs of steel. o is its outline,
# L l s S its leather light to deep, b a button and m its legs.
CHAIR = [
    "...............ooooooo....",
    ".............ooLLLLLLLo...",
    "............oLLlllllllso..",
    "...........oLllllllllllso.",
    "...........oLlblllllblllso",
    "...........oLlllllllllllso",
    "............oLllbllllbllso",
    ".............oLllllllllllo",
    "..............oLlllbllllso",
    "..............oLllllllllso",
    "..............oLllblllllso",
    "..............oLllllllllso",
    "..............oLlllllbllso",
    "..............oLllllllllso",
    "..............oLlbllllllso",
    "..............oLllllllllso",
    "..............oLlllllbllso",
    "..............oLllllllllso",
    "..............oLllllllllso",
    "..............oLlblllllso.",
    "..............oLlllbllllso",
    "..............oLllllllllso",
    "..............oLllblllllso",
    "..............oLllllllllso",
    "..............oLlllllbllso",
    "..............oLllllllllso",
    "..............oLlbllllllso",
    "..............oLllllllllso",
    "..............oLlllllbllso",
    "..............oLllllllllso",
    "..............oLllllllllso",
    "..............oLlblllllso.",
    "..............oLllllllllso",
    "..............oLllllllllso",
    "..............oLlllllbllso",
    "...ooooooooooooLllllllllso",
    "..oLLLLLLLLLLLLllllllllSso",
    "..oLlllllllllllllllllllSso",
    "..oslllllllllllllllllllSso",
    "..ossssssssssssssssssssSSo",
    "..oSSSSSSSSSSSSSSSSSSSSSSo",
    "...ooooooooooooooooooooooo",
    "...m...................m..",
    "...m...................m..",
    "...m...................m..",
    "...m...................m..",
    "..mm..................mm..",
]
# The Architect seated in it, facing his console, drawn to the hand's canon: an old man with his white hair swept
# back and a short white beard, a single dark unit for his eye, in a pale grey suit with a dark tie, holding a pen up
# before him. h H his hair, K k his skin, e his eye, w his beard, x his collar and y his tie, u U S his suit, p the pen
# and b its brass, d his shoes. Laid over the chair, with his back to its back.
ARCHITECT = [
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    ".........hhhh.............",
    "........hHHHHhh...........",
    "........KeKkHHhh..........",
    ".......KKKKkkhh...........",
    "........wwKkkh............",
    "........wwwwk.............",
    ".........wwxy.............",
    "........uuxyxuu...........",
    ".......UuuxyxuuU..........",
    "......UUuuxyuuuuu.........",
    "......UuuuyuuuuUu.........",
    ".....p.Uuuuuuuu.Uu........",
    ".....p.KUuuuuuu.Uu........",
    ".....pKkUUuuuuuuUu........",
    ".....bkUUuuuuuuuuu........",
    "...uuUUUUUUUuuuuuuu.......",
    "..UUUUUUUUUUuuuuuuu.......",
    "..UuuuuuuuuuuuuuuS........",
    "..UuS.....................",
    "..UuS.....................",
    "..UuS.....................",
    "..UuS.....................",
    "..UuS.....................",
    "..UuS.....................",
    "..UuS.....................",
    ".ddddS....................",
    "ddddd.....................",
]


def architect(p: Pix, x, g, night: bool, light=None):
    """The Architect in his white wingback (see `CHAIR` and `ARCHITECT`), standing on the floor at row g with the
    chair's left at column x, and he outlined against the chair and the room, each stretch of the line in the darkest
    tone of the part of him it rims, all but his pen. His skin keeps its tone by night, as the hand's canon has it; by
    night he, his suit and his chair take the green light of the screen before him, at `light` (cx, cy)."""
    if night:
        chair = {"o": LEATHER[0], "L": LEATHER[3], "l": LEATHER[2], "s": LEATHER[1], "S": LEATHER[0],
                 "b": LEATHER[0], "m": STEEL[2]}
    else:
        chair = {"o": LEATHER[1], "L": LEATHER[6], "l": LEATHER[5], "s": LEATHER[3], "S": LEATHER[2],
                 "b": LEATHER[2], "m": STEEL[5]}
    skin = RAMP["skin0"]
    j = -2 if night else 0
    man = {"h": SHELL[3], "H": SHELL[5], "K": skin[4], "k": skin[3], "e": STEEL[0], "w": SHELL[5], "x": SUIT[6],
           "y": SUIT[1], "u": SUIT[4 + j], "U": SUIT[5 + j], "S": SUIT[2 + j], "p": STEEL[0], "b": BRASS[5],
           "d": SUIT[1]}
    top = g - len(CHAIR) + 1
    key = ("architect", night)
    if key not in p.syms:
        cells = {(i, j): chair[ch] for j, row in enumerate(CHAIR) for i, ch in enumerate(row) if ch in chair}
        him = {(i, j): ch for j, row in enumerate(ARCHITECT) for i, ch in enumerate(row) if ch in man}
        for (i, j), ch in him.items():
            for q in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if q not in him and ch not in "pb" and 0 <= q[0] < len(CHAIR[0]) and q[1] < len(CHAIR):
                    cells[q] = ramp_for(man[ch])[0]
        cells.update({xy: man[ch] for xy, ch in him.items()})
        p.symbol(key, cells)
    p.use(key, x, top, p.layer("hero", z=0.2))
    if night and light:
        lit = {(x + i, top + j): c for j, row in enumerate(CHAIR) for i, ch in enumerate(row)
               if (c := man.get(ARCHITECT[j][i]) or chair.get(ch))}
        hero = p.layer("hero~", z=0.25)
        for (hx, hy), c in lit.items():
            d = math.hypot((hx + 0.5 - light[0] - 4) / 32, (hy + 0.5 - light[1] - 6) / 26)
            if d < 1:
                p.apx(hx, hy, FLAME[4], (0.14, 0.24, 0.34)[min(2, int((1 - d) * 3))], hero)


def study(p: Pix, x0, x1, g, months, night: bool, motion: bool) -> tuple:
    """The right of the room from column x0 to x1, standing on the floor at row g: a stack of sets two across at the
    top of the wall, two high where the wall leaves room, showing `months`' first pictures, and before the wall of
    screens the Architect in his tall white wingback, facing his console, where a monitor shows the last, the room
    itself. By night the screens' light falls on him, his chair and the floor. Returns the span of the floor it
    covers."""
    rows = max(1, min(2, (g - 13 - 6 - TV_H - TOP - 2) // TV_H))
    for n, name in enumerate(months[:2 * rows]):
        tv(p, x0 + 1 + (n % 2) * TV_W, TOP + 1 + (n // 2) * TV_H, name, night, motion, phase=(n + 1) % 3)
    console(p, x0, x0 + 25, g, night, motion, months[-1])
    monitor = (x0 + 12.5, g - 13 - 6 - TV_H / 2)
    architect(p, x1 - len(CHAIR[0]) + 1, g, night, light=monitor)
    if night:
        p.halo(x0 + 12.5, monitor[1], 16, 14, FLAME[3], (0.06, 0.12, 0.2))
        floor_pool(p, (x0 + x1) / 2, g, 26, night)
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the floor
def _clear_runs(p: Pix, x0, x1, y0, y1, least: int = 6) -> list:
    """The runs of columns from x0 to x1 whose rows y0 to y1 lie two units clear of every word, `least` columns long
    at the least, as (start, end) with the end excluded."""
    runs, start = [], None
    for x in range(x0, x1 + 1):
        ok = x < x1 and p.clear_of_words(x - 2, y0 - 2, x + 3, y1 + 2)
        if ok and start is None:
            start = x
        elif not ok and start is not None:
            if x - start >= least:
                runs.append((start, x))
            start = None
    return runs


def cables(p: Pix, x0, x1, y, night: bool):
    """The cables that wire the sets together, lying along the floor from column x0 to x1 over the rule on row y
    wherever no word lies near: two of them, black, crossing and parting in slow waves, lit along their tops, with a
    green connector's light here and there."""
    for a, b in _clear_runs(p, x0, x1, y - 3, y - 1):
        for n, (amp, period, phase) in enumerate(((0.9, 23, 0.0), (0.9, 31, 2.1))):
            for x in range(a, b):
                yy = y - 2 + round(amp * math.sin(2 * math.pi * x / period + phase))
                p.px(x, yy, PLASTIC[2 + n] if night else PLASTIC[0 + n])
        for x in range(a + 9, b - 4, 37):
            p.px(x, y - 2, FLAME[4])
            p.px(x + 1, y - 2, PLASTIC[0])


# --------------------------------------------------------------------------- the Architect standing; his empty chair
# The Architect standing, 13 units wide and 34 tall, facing right toward his screens, drawn to the hand's canon: his
# white hair swept back and his short white beard, a single dark unit for his eye, his pale grey suit and dark tie, and
# his pen held up before him in his right hand. Letters as in `ARCHITECT`.
STANDING = [
    "....hhhh.....",
    "...hHHHHhh...",
    "...hHHHHHh...",
    "...hHHKKKk...",
    "...hHKeKKk...",
    "....hKKKKK...",
    "....hwwKk....",
    ".....wwwk....",
    ".....wwxy....",
    "...uUUxyxu...",
    "..uUUUuyuuu..",
    "..UUUuuyuuuu.",
    "..UUuuuyuuuu.",
    "..UUuuuuuuKkp",
    "..UUuuuuuuuSb",
    "..UUuuuuuuu..",
    "..UUuuuuuuS..",
    "..UUuuuuuuS..",
    "..Uuuuuuuuu..",
    "...uuuuuuuS..",
    "...uuuuuuuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...uuuS.uuS..",
    "...ddd..ddd..",
    "...dddd.dddd.",
]


def _man(night: bool) -> dict:
    """The Architect's tones by day and by night: his hair and beard, his skin, which keeps its tone by night as the
    hand's canon has it, his collar, tie and suit, the suit two tones deeper by night, his pen and its brass."""
    skin = RAMP["skin0"]
    j = -2 if night else 0
    return {"h": SHELL[3], "H": SHELL[5], "K": skin[4], "k": skin[3], "e": STEEL[0], "w": SHELL[5], "x": SUIT[6],
            "y": SUIT[1], "u": SUIT[4 + j], "U": SUIT[5 + j], "S": SUIT[2 + j], "p": STEEL[0], "b": BRASS[5],
            "d": SUIT[1]}


def _outlined(rows: list, pal: dict, width: int, under: dict | None = None) -> dict:
    """A figure's cells {(x, y): colour} from `rows` in `pal`, outlined against what lies `under` it and the room, each
    stretch of the line in the darkest tone of the part it rims, all but a pen, and none under the soles he stands
    on."""
    cells = dict(under or {})
    him = {(i, j): ch for j, row in enumerate(rows) for i, ch in enumerate(row) if ch in pal}
    for (i, j), ch in him.items():
        for q in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if q not in him and ch not in "pb" and 0 <= q[0] < width and q[1] < len(rows):
                cells[q] = ramp_for(pal[ch])[0]
    cells.update({xy: pal[ch] for xy, ch in him.items()})
    return cells


def standing(p: Pix, x, g, night: bool, light=None):
    """The Architect standing on the floor at row g, his left at column x, facing right toward his screens, his pen
    held up before him (see `STANDING`), outlined against the room. By night the green light of the screen at `light`
    (cx, cy) falls on him."""
    man = _man(night)
    top = g - len(STANDING) + 1
    key = ("standing", night)
    if key not in p.syms:
        p.symbol(key, _outlined(STANDING, man, len(STANDING[0]) + 1))
    p.use(key, x, top, p.layer("hero", z=0.2))
    if night and light:
        hero = p.layer("hero~", z=0.25)
        for j, row in enumerate(STANDING):
            for i, ch in enumerate(row):
                if ch in man and ch not in "pb":
                    d = math.hypot((x + i + 0.5 - light[0]) / 30, (top + j + 0.5 - light[1]) / 30)
                    if d < 1:
                        p.apx(x + i, top + j, FLAME[4], (0.12, 0.2, 0.3)[min(2, int((1 - d) * 3))], hero)


# The near arm of the wingback, which only the empty chair shows (the Architect sits in front of it): a padded arm
# rolled at its front, lying along the seat from the back, as the chair's rows from row ARM[0] on.
ARM = (30, ["..oooooooooooooLllllllllso", ".oLLLLLLLLLLLLlLlblllllso.", ".oLllllllllllllLllllllllso",
            ".oslllllllllllSLllllllllso", "..osssssssssssSLlllllbllso"])


def empty_chair(p: Pix, x, g, night: bool, light=None):
    """The white wingback alone on the floor at row g, its left at column x, turned to face right toward the screens,
    its near arm rolled along its seat (see `ARM`) and the Architect's pen lying on the seat. By night the screens'
    green light at `light` falls on it."""
    if night:
        pal = {"o": LEATHER[0], "L": LEATHER[3], "l": LEATHER[2], "s": LEATHER[1], "S": LEATHER[0],
               "b": LEATHER[0], "m": STEEL[2]}
    else:
        pal = {"o": LEATHER[1], "L": LEATHER[6], "l": LEATHER[5], "s": LEATHER[3], "S": LEATHER[2],
               "b": LEATHER[2], "m": STEEL[5]}
    w = len(CHAIR[0])
    top = g - len(CHAIR) + 1
    key = ("empty chair", night)
    if key not in p.syms:
        rows = CHAIR[:ARM[0]] + ARM[1] + CHAIR[ARM[0] + len(ARM[1]):]
        cells = {(w - 1 - i, j): pal[ch] for j, row in enumerate(rows) for i, ch in enumerate(row) if ch in pal}
        seat = len(CHAIR) - 12
        for i in range(8, 16):
            cells[(i, seat)] = BRASS[5] if i < 12 else STEEL[0]
        p.symbol(key, cells)
    p.use(key, x, top, p.layer("hero", z=0.2))
    if night and light:
        hero = p.layer("hero~", z=0.25)
        for j, row in enumerate(CHAIR):
            for i, ch in enumerate(row):
                if ch in pal and ch != "m":
                    hx = x + w - 1 - i
                    d = math.hypot((hx + 0.5 - light[0]) / 34, (top + j + 0.5 - light[1]) / 34)
                    if d < 1:
                        p.apx(hx, top + j, FLAME[4], (0.1, 0.18, 0.28)[min(2, int((1 - d) * 3))], hero)


# --------------------------------------------------------------------------- a tower of sets (H2, H3)
STAND = 3         # the rows of the steel stand a tower of sets stands on


def tower(p: Pix, x, g, cols: int, rows: int, months, night: bool, motion: bool, reach=None) -> tuple:
    """A tower of sets `cols` across and `rows` high on a stand of steel, its left at column x and standing on the
    floor at row g, each set showing one of `months`' pictures, the first at the top left, flickering in a moving
    header, and its cables rising from its top to row `reach`, where they are slung from the ceiling. By day the tower
    throws a shadow on the wall; by night its light blooms round it and pools on the floor at its foot. Returns the
    span of the floor it covers and the middle of its screens."""
    w = cols * TV_W
    for y in (g - 2, g - 1, g):
        for xx in range(x, x + w):
            p.px(xx, y, STEEL[5 if y == g - 2 else 3 if y == g - 1 else 1])
    for xx in (x + 2, x + w - 3):
        p.vline(xx, g - 1, g + 1, STEEL[0])
    top = g - STAND - rows * TV_H + 1
    if reach is not None and top - reach >= 3:
        loom(p, x + 3, x + w - 3, reach, top, night)
    for n, name in enumerate(list(months)[:cols * rows]):
        tv(p, x + (n % cols) * TV_W, top + (n // cols) * TV_H, name, night, motion, phase=(n + 2) % 3)
    if not night:
        p.vline(x + w, top + 1, g - 2, WALL[3])
    else:
        p.halo(x + w / 2, (top + g) / 2, w / 2 + 3, (g - top) / 2 + 1, FLAME[3], (0.05, 0.1, 0.17))
        floor_pool(p, x + w / 2, g, w // 2 + 10, night)
    return (x - 1, x + w + 1), (x + w / 2, top + rows * TV_H / 2)


def loom(p: Pix, x0, x1, top, foot, night: bool):
    """The cables a tower's sets are wired with, rising from its top on row `foot` to the ceiling on row `top`, three
    of them every so often across it from column x0 to x1, each swaying a unit as it climbs, its sheath lit down its
    left, a grey tie binding each bundle where it leaves the sets."""
    for i, cx in enumerate(range(x0 + 2, x1 - 1, 10)):
        for j in range(3):
            for y in range(top, foot):
                sway = round(math.sin((y + i * 7 + j * 3) / 6.0))
                xx = cx + j + sway
                p.px(xx, y, PLASTIC[3] if j == 0 else PLASTIC[1] if j == 1 else PLASTIC[2])
        p.hline(cx - 1, cx + 4, foot - 2, SHELL[4] if not night else SHELL[2])
        p.hline(cx - 1, cx + 4, top, PLASTIC[0])


TOWER_MONTHS = ("choice", "exit", "dojo", "rooftop", "oracle", "harvest", "subway", "hovercraft", "chateau",
                "rain", "rabbit", "architect")


def audience(p: Pix, x0, x1, g, night: bool, motion: bool, room: int) -> tuple:
    """The H2's hero, from column x0 to x1 on the floor at row g: a tower of sets three across and as high as the `room`
    rows over the floor leave it, four at the most, its cables rising to the ceiling over it, at the right, and the
    Architect standing before it, his pen held up to the screens. Returns the span of the floor it covers."""
    rows = max(1, min(4, (room - STAND - 2) // TV_H))
    (a, b), light = tower(p, x1 - 3 * TV_W + 1, g, 3, rows, TOWER_MONTHS, night, motion, reach=g - room + 1)
    standing(p, a - 17, g, night, light=light)
    return (a - 19, b)


def vigil(p: Pix, x0, x1, g, night: bool, motion: bool, room: int) -> tuple:
    """The H3's hero, from column x0 to x1 on the floor at row g: a column of sets as high as the `room` rows over the
    floor leave it, four at the most, its cables rising to the ceiling over it so that it stands their full height, at
    the right, and the Architect's white wingback standing empty before it, turned to the screens, his pen on its seat.
    Returns the span of the floor it covers."""
    rows = max(1, min(4, (room - STAND - 1) // TV_H))
    shown = ("rain", "choice", "rabbit", "architect")[4 - rows:]
    (a, b), light = tower(p, x1 - TV_W + 1, g, 1, rows, shown, night, motion, reach=g - room + 1)
    if room >= len(CHAIR) + 2:
        empty_chair(p, a - len(CHAIR[0]) - 1, g, night, light=light)
        return (a - len(CHAIR[0]) - 2, b)
    return (a, b)


def section_mark(p: Pix, x, y, night: bool):
    """A little set beside SECTION A-A, its tube glowing, from a row over the words to one under them."""
    k = -1 if night else 0
    rows = ["ccccccc", "cGgggSc", "cgggggc", "ccccccc", "..CCC.."]
    p.sprite(x, y - 1, rows, {"c": SHELL[5 + k], "C": SHELL[3 + k], "g": FLAME[2], "G": FLAME[4], "S": FLAME[1]})


def strip_mark(p: Pix, x, y, night: bool):
    """A little set beside a strip's title, the code running down its tube, eleven units wide and ten tall, raised so
    that its stand stays two rows clear of the tagline under the title."""
    k = -1 if night else 0
    rows = ["ccccccccccc", "cgGgggggGgc", "cGgggGgggGc", "cgggGgggggc", "cggGggggGgc", "cGggggGgggc",
            "cgggGggggSc", "ccccccccccc", "....CCC....", "...CCCCC..."]
    p.sprite(x, y - 6, rows, {"c": SHELL[5 + k], "C": SHELL[3 + k], "g": GLASS[3], "G": FLAME[3], "S": FLAME[5]})


# --------------------------------------------------------------------------- on a phone
PHONE_SCENE = 62      # the rows a phone's H1 gives its room under its words
PHONE_LEAST = 48      # the fewest rows the room is drawn in
# The rows a phone's H2 and H3 ask for under their words, whatever the words: room for a tower of sets three high with
# the Architect standing before it, and for a column of sets three high with his chair before it.
UNDER = {"H2": 64, "H3": 62}


def phone_room(p: Pix, g, night: bool, room: int) -> tuple:
    """The whole room across a phone under its words, standing on the floor at row g in the `room` rows free over it:
    the big sets stacked at the left, as many as the rows leave room for, the console with its monitor, the Architect
    in his white wingback facing it, and a tower of sets two across at the right. Returns the span of the floor it
    covers."""
    n = max(1, min(2, room // BIG_H))
    top = g - n * BIG_H + 1
    for i, name in enumerate(("rain", "choice")[:n]):
        big_tv(p, 5, top + i * BIG_H, name, False, False)
    console(p, 56, 81, g, night, False, "architect")
    architect(p, 82, g, night, light=(68.5, g - 13 - 6 - TV_H / 2))
    rows = max(1, min(3, (room - STAND - 1) // TV_H))
    tower(p, 122, g, 2, rows, TOWER_MONTHS[2:], night, False)
    if night:
        floor_pool(p, 30, g, 26, night)
        floor_pool(p, 96, g, 24, night)
    return (4, p.w - 4)


def phone_audience(p: Pix, g, night: bool, room: int) -> tuple:
    """A phone's H2 under its words: a tower of sets three across at the right, as high as the `room` rows leave it,
    the Architect standing before it with his pen held up, and his white wingback waiting empty behind him."""
    rows = max(1, min(3, (room - STAND - 2) // TV_H))
    (a, b), light = tower(p, p.w - 5 - 3 * TV_W, g, 3, rows, TOWER_MONTHS, night, False)
    standing(p, a - 20, g, night, light=light)
    if room >= len(CHAIR) + 2:
        empty_chair(p, 8, g, night)
    return (4, p.w - 4)


def phone_vigil(p: Pix, g, night: bool, room: int) -> tuple:
    """A phone's H3 under its words: the column of sets with the Architect's empty chair turned to it at the right, as
    high as the `room` rows leave them, and at the left a big set with the code running down it."""
    span = vigil(p, p.w - 60, p.w - 5, g, night, False, room)
    if room >= BIG_H + 2:
        big_tv(p, 8, g - BIG_H + 1, "rain", False, False)
    return (4, p.w - 4) if span else span


# --------------------------------------------------------------------------- the cable under the band (the garland)
SAG = 4           # the rows the cable sags between two clips


def cable_garland(p: Pix, x0, x1, night: bool, gap=None, span: int = 3 * CELL_W):
    """A cable slung under the row of sets along a header's top, sagging SAG rows between clips every `span` units,
    each clip a grey tie with a tally light under it, green when it is on; parting either side of `gap`, the columns
    the month's mark keeps clear. Each stretch is drawn once a file and placed as often as it hangs."""
    spans = [(x0, x1)] if gap is None else [(x0, gap[0]), (gap[1], x1)]
    key = ("cable", span, night)
    if key not in p.syms:
        cells = {}
        for x in range(span + 1):
            t = x / span
            y = round(SAG * 4 * t * (1 - t))
            cells[(x, y)] = PLASTIC[1]
            cells[(x, y + 1)] = PLASTIC[0] if not night else DUSK[0]
            if x % 9 == 4:
                cells[(x, y)] = PLASTIC[3]
        p.symbol(key, cells)
        p.symbol(("clip", night), {(0, 0): SHELL[4 if not night else 2], (1, 0): SHELL[2 if not night else 1],
                                   (0, 1): SHELL[3 if not night else 1], (1, 1): SHELL[1 if not night else 0],
                                   (0, 2): FLAME[3], (1, 2): FLAME[1]})
    for a, b in spans:
        n = (b - a) // span
        if n < 1:
            continue
        start = a + ((b - a) - n * span) // 2
        for i in range(n):
            p.use(key, start + i * span, TOP + 1)
        for i in range(n + 1):
            p.use(("clip", night), start + i * span - 1, TOP)
