# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Exit set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is a city street's wall in the March rain, overcast grey-blue concrete by day and navy-black and wet by
night, its panels streaked where the rain runs down them, held in the riveted iron of the elevated railway: a column
of painted iron down each side, a granite kerb along the foot, and across a header's top a lattice girder of the El,
studded with rivets weeping rust, parting either side of the month's mark. Titles are neon signs on a dark board:
glass tubes bent to the letters, unlit and pale by day, and by night burning the hand's phosphor, white-hot at their
cores, their light haloed on the board and blooming in three steps round the sign, one letter guttering. Headers
open on the street in the rain: at the left a phone booth of steel and glass under a bishop's-crook streetlamp with
a street sign spelt in the code, its payphone ringing and its handset off the hook, swinging on its cord, a pillar
of the El braced to the girder on curved knee braces with a poster of a white rabbit peeling off it, a traffic
signal hung from the girder showing green, and a figure in a long dark coat striding to the booth through the rain;
at the right the brick front of a tenement with its fire escape zigzagging down it, its windows lit green by night
and someone watching from one, and a vertical neon sign, HOTEL, its light pooled on the brick; and on the street
under the words a manhole breathing steam and a hydrant at the kerb. Along the foot the wet street holds every light
in shimmering streaks of ripples, the lamp's, the booth's, the signal's and the sign's, and by night the title's
neon as one long sheen under it. The rain falls slanting across the whole sky behind the title and down the street,
lit green where it passes through the lamp's light. A section's header has the booth close up and answered, someone
in a long coat inside with the handset to an ear, under the streetlamp, an Agent striding toward it and a pillar of
the El rising from the girder; a strip's has the hotel's corner rising its full height. The marks beside the titles
are an EXIT sign and a ringing payphone, and a rule where no scene stands is a riveted strap with puddles of the
rain on it. Footers stand on the El's girder with the booth on it, and the elements are built of neon tubes, the
El's iron, rivets and lanterns. Everything is shaded from the one light in the upper left on the set's own ramps,
and every light is the hand's phosphor."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, LZ, Pix, fold, measure, num, tube
from .palette import C, NIGHT_SKY, RAMP, X

WALL, STREET, IRON, RUST = RAMP["wall"], RAMP["street"], RAMP["iron"], RAMP["rust"]
BRICK, MORTAR, STEEL, GLASS = RAMP["brick"], RAMP["mortar"], RAMP["steel"], RAMP["glass"]
TUBE, BOARD, GRANITE, COAT = RAMP["tube"], RAMP["board"], RAMP["granite"], RAMP["coat"]
HAIR, FLAME, ENAMEL = RAMP["hair"], RAMP["flame"], RAMP["enamel"]
SKIN = RAMP["skin1"]
EDGE = 4          # the iron column's width down each side, and the kerb's along the foot
GIRDER = 13       # the rows the El's girder takes across a header's top


def area(cells) -> str:
    """Path data that fills exactly the pixels `cells` with rectangles: each row's runs, merged down the rows while a
    run repeats under itself, every move after the first relative to where the last rectangle began."""
    rows: dict = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
    rects, open_ = [], {}
    for y in sorted(rows):
        xs, runs = sorted(rows[y]), []
        for x in xs:
            if runs and x == runs[-1][1] + 1:
                runs[-1][1] = x
            else:
                runs.append([x, x])
        here = {tuple(r) for r in runs}
        for run in list(open_):
            y0, h = open_[run]
            if run not in here or y0 + h != y:
                rects.append((y0, run[0], run[1] - run[0] + 1, h))
                del open_[run]
        for run in here:
            y0, h = open_.get(run, (y, 0))
            open_[run] = (y0, h + 1)
    rects += [(y0, run[0], run[1] - run[0] + 1, h) for run, (y0, h) in open_.items()]
    out, at = [], None
    for y, x, w, h in sorted(rects):
        out.append((f"M{x} {y}" if at is None else f"m{x - at[0]} {y - at[1]}") + f"h{w}v{h}h-{w}z")
        at = (x, y)
    return "".join(out)


def fills(cells: dict) -> str:
    """Filled paths for {(x, y): colour}, rectangles a colour (see `area`): the shapes a pattern's tile is drawn in,
    since a browser paints thin strokes inside a pattern poorly when the file asks for crisp edges."""
    by: dict = {}
    for xy, c in cells.items():
        by.setdefault(c, set()).add(xy)
    return "".join(f'<path fill="{c}" d="{area(cs)}"/>' for c, cs in sorted(by.items()))


def light(nx: float, ny: float, nz: float) -> float:
    """How much of the one lamp a surface facing (nx, ny, nz) takes, 0 to 1."""
    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return max(0.0, (nx * LX + ny * LY + nz * LZ) / n)


def ellipse(cx, cy, rx, ry) -> set:
    """The cells inside an ellipse centred on (cx, cy)."""
    out = set()
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                out.add((x, y))
    return out


def sprite(p: Pix, x, y, art, pal, L="base", flip=False):
    """Pixel art from rows of characters, each looked up in `pal`; a character it does not name is left clear."""
    for j, row in enumerate(art):
        for i, ch in enumerate(row[::-1] if flip else row):
            c = pal.get(ch)
            if c:
                p.px(x + i, y + j, c, L)


# --------------------------------------------------------------------------- the wall
TILE_W, TILE_H = 48, 32     # a panel of the street wall's concrete


def _panels(uid: str, night: bool, streaks: int = 9) -> str:
    """The street wall as a pattern tile, a panel of concrete TILE_W by TILE_H: the joint along its top and down its
    side, its upper edge catching the light under the joint, and `streaks` where the rain has run down it from the
    joint, longer and shorter, a tone darker than the concrete."""
    joint, lip, streak = (STREET[2], STREET[4], STREET[2]) if night else (WALL[4], WALL[6], WALL[4])
    rnd = random.Random(8)
    cells = {}
    for x in range(TILE_W):
        cells[(x, 0)] = joint
        cells[(x, 1)] = lip
    for y in range(TILE_H):
        cells[(0, y)] = joint
    for _ in range(streaks):
        x = rnd.randrange(3, TILE_W - 2)
        n = rnd.randint(4, 18)
        for y in range(2, 2 + n):
            if rnd.random() < 0.85:
                cells[(x, y)] = streak
    return (f'<pattern id="{uid}w" width="{TILE_W}" height="{TILE_H}" patternUnits="userSpaceOnUse">'
            f'{fills(cells)}</pattern>')


def band_edges(h: int) -> list:
    """The rows the night's bands change at, down a sheet `h` tall."""
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the street wall's concrete panels, overcast grey-blue by day and navy-black by
    night, streaked by the rain; a drawing made lighter to fit its budget keeps the panels and fewer of the streaks,
    texture no one misses at 1x. The drawing keeps which sheet it is and whether it is night."""
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
    p.defs.append(_panels(uid, night, streaks=3 if p.lite else 9))
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}w)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the wall's concrete, or the night's band of it there."""
    if not night:
        return C["paper"]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


# --------------------------------------------------------------------------- the frame: the El's iron
def _rivets(uid: str, along: bool, night: bool, gap: int = 6) -> str:
    """A line of rivets on painted iron, one every `gap` units, as a pattern: each head lit at its upper left with
    its shadow at its lower right."""
    k = -1 if night else 0
    w, h = (gap, 2) if along else (2, gap)
    cells = {(0, 0): IRON[6 + k], (1, 0): IRON[4 + k], (0, 1): IRON[3 + k], (1, 1): IRON[0]}
    return f'<pattern id="{uid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{fills(cells)}</pattern>'


def frame(p: Pix, night: bool, top: int = 0):
    """The border: a column of the El's painted iron down each side, lit on the face it turns to the light and in
    shade on its far side, riveted down its middle, and a kerb of granite along the foot, its upper edge lit and its
    joints cut at intervals; the shadow the iron casts on the wall inside it."""
    w, h = p.w, p.h
    k = -1 if night else 0
    sh = p.shapes["base"]
    for i, c in enumerate((IRON[0], IRON[5 + k], IRON[3 + k], IRON[1])):
        sh.append(f'<rect x="{i}" y="{top}" width="1" height="{h - top}" fill="{c}"/>')
    for i, c in enumerate((IRON[4 + k], IRON[3 + k], IRON[1], IRON[0])):
        sh.append(f'<rect x="{w - EDGE + i}" y="{top}" width="1" height="{h - top}" fill="{c}"/>')
    for i, c in enumerate((GRANITE[5 + k], GRANITE[4 + k], GRANITE[2 + k], GRANITE[0])):
        sh.append(f'<rect x="{EDGE}" y="{h - EDGE + i}" width="{w - 2 * EDGE}" height="1" fill="{c}"/>')
    uid = getattr(p, "sheet", "p")
    p.defs.append(_rivets(f"{uid}rv", False, night))
    sh.append(f'<rect x="1" y="{top + 2}" width="2" height="{h - top - EDGE - 2}" fill="url(#{uid}rv)"/>')
    sh.append(f'<rect x="{w - 3}" y="{top + 2}" width="2" height="{h - top - EDGE - 2}" fill="url(#{uid}rv)"/>')
    sh.append(f'<rect x="{EDGE}" y="{top}" width="1" height="{h - top - EDGE}" fill="{X["shade"]}" '
              f'fill-opacity="{".25" if not night else ".45"}"/>')
    for x in range(EDGE + 31, w - EDGE, 37):
        p.px(x, h - EDGE, GRANITE[2 + k])
        p.px(x, h - EDGE + 1, GRANITE[1])
        p.px(x, h - EDGE + 2, GRANITE[0])


def _lattice(uid: str, night: bool) -> str:
    """The girder's web as a pattern tile 12 by 6: a stiffener of flat iron at each end and a cross of flat bars
    between, the wall showing through the lattice; the bars lit on their upper faces."""
    k = -1 if night else 0
    cells = {}
    for y in range(6):
        cells[(0, y)] = IRON[4 + k]
        cells[(1, y)] = IRON[2 + k]
    for i in range(6):
        cells[(2 + round(i * 9 / 5), i)] = IRON[3 + k]
        cells[(3 + round(i * 9 / 5), i)] = IRON[1]
        cells[(10 - round(i * 9 / 5), i)] = IRON[4 + k]
        cells[(11 - round(i * 9 / 5), i)] = IRON[2 + k]
    return (f'<pattern id="{uid}" x="0" y="4" width="12" height="6" patternUnits="userSpaceOnUse">'
            f'{fills(cells)}</pattern>')


def girder(p: Pix, night: bool, gap=None):
    """The El's lattice girder across a header's top: its top flange lit along its upper face and riveted, its web
    an open lattice of flat bars between stiffeners, its bottom flange riveted, rust weeping from a rivet here and
    there, and its shadow on the wall under it. `gap` is the span (x0, x1) it parts either side of, the month's
    mark, each end closed with a plate; None runs it unbroken from side to side."""
    w = p.w
    k = -1 if night else 0
    uid = getattr(p, "sheet", "p")
    p.defs.append(_lattice(f"{uid}gl", night))
    p.defs.append(_rivets(f"{uid}gr", True, night, gap=5))
    runs = [(0, w)] if gap is None else [(0, gap[0]), (gap[1], w)]
    L = p.layer("girder", z=-1)
    sh = p.shapes[L]
    rows = [(0, IRON[0]), (1, IRON[5 + k]), (2, IRON[4 + k]), (3, IRON[1]), (10, IRON[4 + k]), (11, IRON[2 + k]),
            (12, IRON[0])]
    rnd = random.Random(2)
    for a, b in runs:
        n = b - a
        sh.append(f'<rect x="{a}" y="4" width="{n}" height="6" fill="url(#{uid}gl)"/>')
        for y, c in rows:
            sh.append(f'<rect x="{a}" y="{y}" width="{n}" height="1" fill="{c}"/>')
        sh.append(f'<rect x="{a + 2}" y="1" width="{n - 4}" height="2" fill="url(#{uid}gr)"/>')
        sh.append(f'<rect x="{a + 2}" y="10" width="{n - 4}" height="2" fill="url(#{uid}gr)"/>')
        sh.append(f'<rect x="{a}" y="13" width="{n}" height="1" fill="{X["shade"]}" '
                  f'fill-opacity="{".22" if not night else ".4"}"/>')
        for _ in range(max(1, n // 40)):
            rx = rnd.randrange(a + 4, b - 4) // 5 * 5 + 2
            for i, y in enumerate(range(12, 12 + rnd.randint(2, 4))):
                p.px(rx, y, RUST[max(0, 3 + k - i // 2)], L)
        for end in ((a,) if a > 0 else ()) + ((b - 3,) if b < w else ()):
            for y in range(0, 13):
                p.px(end, y, IRON[0], L)
                p.px(end + 1, y, IRON[4 + k], L)
                p.px(end + 2, y, IRON[1] if end != a else IRON[2 + k], L)
            for y in (3, 6, 9):
                p.px(end + 1, y, IRON[6 + k], L)


# --------------------------------------------------------------------------- the title: a neon sign
def _tube_cells(ch: str, scale: int) -> dict:
    """The neon tube a letter is bent from, {(x, y): 0 or 1}: a tube two units wide down the middle of every stroke
    of the face's letter at the larger sizes and one unit at the smaller, joined where its strokes meet, corner to
    corner where a stroke runs on the slant; 1 marks the tube's upper or left half, its hot core."""
    g = FONTS["57"][0][ch]
    ink = {(c, r) for r, cols in enumerate(g[1]) for c in cols}
    tw = 2 if scale >= 4 else 1
    off = (scale - tw) // 2
    cells = set()

    def core(c, r):
        return c * scale + off, r * scale + off
    for (c, r) in ink:
        x, y = core(c, r)
        cells.update((x + i, y + j) for i in range(tw) for j in range(tw))
        for dc, dr in ((1, 0), (0, 1), (1, 1), (-1, 1)):
            if (c + dc, r + dr) not in ink:
                continue
            if dc and dr and ((c + dc, r) in ink or (c, r + dr) in ink):
                continue
            x1, y1 = core(c + dc, r + dr)
            steps = scale * 2
            for s in range(steps + 1):
                t = s / steps
                px_, py_ = round(x + (x1 - x) * t), round(y + (y1 - y) * t)
                cells.update((px_ + i, py_ + j) for i in range(tw) for j in range(tw))
    return {(x, y): int((x, y - 1) not in cells or (x - 1, y) not in cells) for (x, y) in cells}


def _board(p: Pix, bx0, by0, bx1, by1, night):
    """A sign's board of dark enamel in a steel rim, bolted at its corners, its shadow on the wall under it."""
    k = -1 if night else 0
    B = p.layer("board", z=-2)
    sh = p.shapes[B]
    sh.append(f'<rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" fill="{BOARD[0]}"/>'
              f'<rect x="{bx0 + 1}" y="{by0 + 1}" width="{bx1 - bx0 - 2}" height="{by1 - by0 - 2}" '
              f'fill="{BOARD[3 + k]}"/><rect x="{bx0 + 2}" y="{by0 + 2}" width="{bx1 - bx0 - 4}" '
              f'height="{by1 - by0 - 4}" fill="{BOARD[1] if night else BOARD[2]}"/>'
              f'<rect x="{bx0 + 1}" y="{by0 + 1}" width="{bx1 - bx0 - 2}" height="1" fill="{STEEL[5 + k]}"/>'
              f'<rect x="{bx0 + 1}" y="{by1 - 2}" width="{bx1 - bx0 - 2}" height="1" fill="{STEEL[1]}"/>')
    for bx, by in ((bx0 + 2, by0 + 2), (bx1 - 3, by0 + 2), (bx0 + 2, by1 - 3), (bx1 - 3, by1 - 3)):
        p.px(bx, by, STEEL[5 + k], B)
    sh.append(f'<rect x="{bx0 + 2}" y="{by1}" width="{bx1 - bx0 - 2}" height="1" fill="{X["shade"]}" '
              f'fill-opacity="{".3" if not night else ".5"}"/>')


def neon_title(p: Pix, x, y, s, night, scale, L="base", board=True) -> int:
    """A title as a neon sign: its board of dark enamel in a steel rim, bolted to the wall at its corners, and on it
    every letter a glass tube bent to the face's letter (see `_tube_cells`), each tube drawn once a file and placed.
    By day the tubes are unlit, pale glass catching the light along their upper edges; by night they burn the hand's
    phosphor, white-hot at their cores, their light glowing round them on the board (the bloom round the whole sign
    is the sky's, see `neon_bloom`), and one letter gutters on a flicker. The board reaches as far over the letters as
    under them, so a title set at the top of a header keeps the month's mark clear. Without its `board` the tubes are
    bent alone, none guttering, as a move on a game's sheet is lettered by night. Returns its width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    cx, placed = x, []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    rows = max((len(glyphs[ch][1]) for ch in s if ch != " "), default=0)
    th = rows * scale
    pad = 2 + scale
    bx0, by0, bx1, by1 = x - pad, y - scale + 1, x + w + pad, y + th + scale - 1
    if board:
        _board(p, bx0, by0, bx1, by1, night)
    flick = len(placed) - 2 if (board and len(placed) > 2) else -1
    for i, (ch, lx) in enumerate(placed):
        key = ("tube", ch, scale, night)
        if key not in p.syms:
            hot, glass = (FLAME[6], FLAME[5]) if night else (TUBE[6], TUBE[3])
            p.symbol(key, {xy: (hot if v else glass) for xy, v in _tube_cells(ch, scale).items()})
        TL = p.flicker(2) if (night and i == flick) else L
        if night:
            gkey = ("glyph", "57", ch)
            if gkey not in p.syms:
                p.symbol(gkey, {(c, r): 1 for r, cols in enumerate(glyphs[ch][1]) for c in cols}, mono=True)
            GL = p.flicker(2, back=True) if TL != L else p.layer("neonglow", z=-1.5)
            p.use(gkey, lx, y, GL, stroke=f"{FLAME[3]}:.55", scale=scale)
        p.use(key, lx, y, TL)
    p.words.append((bx0 - 1, by0 - 1, bx1 + 1, by1 + 1) if board else (x - 1, y - 1, x + w + 1, y + th + 1))
    return w


# --------------------------------------------------------------------------- the rain and the night's light
def _rain_tile(p: Pix, night: bool, lit: bool = False) -> str:
    """The rain's pattern, drawn once a file: streaks a unit wide in a tile 48 by 48, in the rain's grey, or in the
    lamp's phosphor where it falls through the lamp's light (`lit`). Returns the pattern's id."""
    key = ("rain", night, lit)
    if key in p.syms:
        return p.syms[key]
    uid = f"{getattr(p, 'sheet', 'p')}r"
    if ("rain-streaks",) not in p.syms:
        rnd = random.Random(21)
        cells = set()
        for _ in range(20):
            x, y = rnd.randrange(48), rnd.randrange(48)
            for i in range(rnd.choice((3, 4, 4, 5))):
                cells.add(((x - i // 3) % 48, (y + i) % 48))
        p.defs.append(f'<path id="{uid}s" d="{area(cells)}"/>')
        p.syms[("rain-streaks",)] = f"{uid}s"
    pid = f"{uid}{'l' if lit else ''}{'n' if night else 'd'}"
    tone = FLAME[4] if lit else X["rain_night"] if night else X["rain_day"]
    p.defs.append(f'<pattern id="{pid}" width="48" height="48" patternUnits="userSpaceOnUse">'
                  f'<use href="#{uid}s" fill="{tone}"/></pattern>')
    p.syms[key] = pid
    return pid


def _area(box) -> str:
    a, b, c, d = box
    return f"M{a} {b}h{c - a}v{d - b}h{a - c}z"


def _cut(box, holes) -> str:
    """Path data for the box with the boxes `holes` cut out of it, even-odd: each hole trimmed to the box first, so a
    hole reaching outside it is never filled in there instead."""
    x0, y0, x1, y1 = box
    out = _area(box)
    for a, b, c, d in holes:
        a, b, c, d = max(a, x0), max(b, y0), min(c, x1), min(d, y1)
        if a < c and b < d:
            out += _area((a, b, c, d))
    return out


def _falling(p: Pix, pid: str, clip: str, bbox, z: float, alpha: str):
    """Rain from pattern `pid` falling inside the clip path `clip` (path data, even-odd, so a box inside a box is
    left dry), which lies inside the box `bbox`, stepped down and to the left six rows and two columns every twentieth
    of a second, so the loop closes after a tile's width and three tiles' height; held where it begins in the still
    twin."""
    p.rains = getattr(p, "rains", 0) + 1
    cid = f"{pid}c{p.rains}"
    p.defs.append(f'<clipPath id="{cid}"><path clip-rule="evenodd" d="{clip}"/></clipPath>')
    x0, y0, x1, y1 = bbox
    rect = (f'<rect x="{num(x0)}" y="{num(y0 - 144)}" width="{num(x1 - x0 + 48)}" height="{num(y1 - y0 + 144)}" '
            f'fill="url(#{pid})" fill-opacity="{alpha}"/>')
    values = ";".join(f"{-2 * i} {6 * i}" for i in range(24))
    anim = (f'<animateTransform attributeName="transform" type="translate" values="{values}" dur="1.2s" '
            f'repeatCount="indefinite" calcMode="discrete"/>')
    p.raw(z, f'<g clip-path="url(#{cid})"><g>{rect}{anim}</g></g>', f'<g clip-path="url(#{cid})">{rect}</g>')


def rain(p: Pix, boxes, night, lit=None, keep=()):
    """The rain falling slant down the street in front of the scenes, in the boxes `boxes` the words leave it,
    keeping out of the boxes `keep` inside them, as a booth's glass it would hide; and by night shining green where it
    passes through the lamp's light, `lit`, a polygon of points."""
    bbox = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    _falling(p, _rain_tile(p, night), "".join(_area(b) for b in boxes) + "".join(_area(b) for b in keep), bbox, 1.5,
             ".55" if not night else ".7")
    if lit and night:
        pts = "".join(("M" if i == 0 else "L") + f"{num(a)} {num(b)}" for i, (a, b) in enumerate(lit)) + "z"
        xs, ys = [a for a, _ in lit], [b for _, b in lit]
        _falling(p, _rain_tile(p, night, lit=True), pts, (min(xs), min(ys), max(xs), max(ys)), 1.6, ".8")


def sky_rain(p: Pix, box, night, holes=()):
    """The rain across the whole sky behind the title, from the girder down to the foot of the box `box`, never in
    the boxes `holes` (the month's mark): finer and fainter than the rain in the street, hidden behind the sign's
    board, the city's weather over everything."""
    _falling(p, _rain_tile(p, night), _cut(box, holes), box, -2.5,
             ".35" if not night else ".5")


def neon_bloom(p: Pix, title, box, holes=()):
    """The neon's bloom by night: its green light in three steps round the title, the nearer brighter, laid over the
    sign's board and out over the wall and through the girder, spreading wide to either side and fading out at the
    foot of the box `box`, and never in the boxes `holes` (the month's mark)."""
    bx0, by0, bx1, by1 = title
    cx, cy, rx = (bx0 + bx1) / 2, (by0 + by1) / 2, (bx1 - bx0) / 2
    reach = box[3] - cy
    cid = f"{getattr(p, 'sheet', 'p')}nb"
    p.defs.append(f'<clipPath id="{cid}"><path clip-rule="evenodd" d="{_cut(box, holes)}"/></clipPath>')
    rings = "".join(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx + dx)}" ry="{num(reach + dy)}" '
                    f'fill="{FLAME[3]}" fill-opacity="{a}"/>' for dx, dy, a in ((46, 4, ".05"), (26, 2, ".06"),
                                                                                  (10, 0, ".08")))
    p.raw(-1.9, f'<g clip-path="url(#{cid})">{rings}</g>', f'<g clip-path="url(#{cid})">{rings}</g>')


STREET_ROWS = (10, 8, 6, 4)   # the depths of wet street tried in front of the kerb, deepest first


def street(p: Pix, x0, x1, gs, g, night):
    """The wet street along the foot from column x0 to x1: the kerb's edge at row gs, which everything stands on,
    and the asphalt from there down to row g, black and shining with rain, a line of sheen across it."""
    L = p.layer("street", z=-0.95)
    edge, tar, sheen = (STREET[4], STREET[1], STREET[2]) if night else (WALL[4], WALL[2], WALL[3])
    w = x1 - x0
    p.shapes[L].append(f'<rect x="{x0}" y="{gs}" width="{w}" height="1" fill="{edge}"/>'
                       f'<rect x="{x0}" y="{gs + 1}" width="{w}" height="{g - gs}" fill="{tar}"/>'
                       f'<rect x="{x0}" y="{gs + 2}" width="{w}" height="1" fill="{sheen}"/>')


def _ripples_of(p: Pix, hw, bright, dim, depth) -> str:
    """A light's streak of ripples in the wet, `hw` either side of its column and `depth` rows down (and two over the
    kerb, for its step), a row dark between them here and there, its middle bright down the half of it nearer the
    kerb and only the dim left below; drawn once a file for each light of its kind as a group of paths, a tone each,
    every move after the first relative. Returns its id."""
    key = ("ripples", hw, bright, dim, depth)
    if key in p.syms:
        return p.syms[key]
    rnd = random.Random(hw * 31 + depth)
    rows: dict = {}
    for r in range(-2, depth):
        if r > 0 and rnd.random() < 0.3:
            continue
        h = max(0, hw + rnd.choice((-1, 0, 0, 1)))
        core = (h // 2 if r < depth // 2 else -1) if bright else -1
        if h > core:
            rows.setdefault(dim, []).extend(((-h, r, h - core), (core + 1, r, h - core)))
        if core >= 0:
            rows.setdefault(bright, []).append((-core, r, 2 * core + 1))
    out = []
    for tone, items in rows.items():
        d, at = [], None
        for x, y, w in sorted(items, key=lambda t: (t[1], t[0])):
            d.append(f"M{x} {y + 0.5:g}h{w}" if at is None else f"m{x - at[0]} {y - at[1]}h{w}")
            at = (x + w, y)
        out.append(f'<path stroke="{tone}" d="{"".join(d)}"/>')
    sid = f"{getattr(p, 'sheet', 'p')}rp{sum(1 for k in p.syms if isinstance(k, tuple) and k[0] == 'ripples')}"
    p.defs.append(f'<g id="{sid}">{"".join(out)}</g>')
    p.syms[key] = sid
    return sid


def reflections(p: Pix, sources, x0, x1, gs, g, pools=()):
    """The lights lying in the wet street between columns x0 and x1, the noir's puddle shine: under each of `sources`,
    (x, half width, bright, dim), its light down the asphalt from the kerb toward us as a streak of ripples, each a
    row of light about as wide as the light, its middle in the `bright` tone (none when None) and its ends in the
    `dim`, fading down it (see `_ripples_of`); and under the brightest lights, `pools`
    ((x, half width, tone) each), a pool of their light on the wet, in two steps. In a moving header the ripples step
    every eighth of a second, a row down and a column aside, so the light shimmers; the still twin holds them where
    they begin. Lights of a kind share one drawing of their ripples."""
    depth = g - gs
    uses = "".join(f'<use href="#{_ripples_of(p, hw, bright, dim, depth)}" x="{x}" y="{gs + 1}"/>'
                   for x, hw, bright, dim in sources)
    if not uses and not pools:
        return
    p.wets = getattr(p, "wets", 0) + 1
    cid = f"{getattr(p, 'sheet', 'p')}wet{p.wets}"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{gs + 1}" width="{x1 - x0}" height="{depth}"/></clipPath>')
    under = "".join(f'<ellipse cx="{num(x + 0.5)}" cy="{gs + 1}" rx="{num(hw * f)}" ry="{num(3.5 * f)}" fill="{tone}" '
                    f'fill-opacity="{a}"/>' for x, hw, tone in pools for f, a in ((1, ".14"), (0.55, ".2")))
    p.raw(-0.9, f'<g clip-path="url(#{cid})">{under}<g>{uses}<animateTransform attributeName="transform" '
                f'type="translate" values="0 0;1 1;0 2;-1 1" dur=".5s" repeatCount="indefinite" calcMode="discrete"/>'
                f'</g></g>', f'<g clip-path="url(#{cid})">{under}{uses}</g>')


def ripples(p: Pix, x0, x1, gs, g, motion, night, n=4, seed=13):
    """Raindrops striking the wet street from column x0 to x1: a ring of splash here and there that comes and goes."""
    rnd = random.Random(seed)
    tone = STREET[5] if night else WALL[6]
    for i in range(n):
        x, y = rnd.randrange(x0 + 2, x1 - 2), rnd.randrange(gs + 2, g + 1)
        L = p.twinkle(i) if motion else "base"
        p.px(x - 1, y, tone, L)
        p.px(x + 1, y, tone, L)


# --------------------------------------------------------------------------- the streetlamp
def streetlamp(p: Pix, x, g, top, night, motion, reach=13):
    """A bishop's-crook streetlamp of cast iron standing on the pavement at row g, its post at column x rising to
    row `top`, where it curls over to the right and hangs its lantern `reach` units out: a stepped plinth and a fluted
    base, the post three units thick, lit down its left side and ringed with collars, the crook with a scroll under
    it, and the lantern's glass under its cap and finial, which by night burns the hand's phosphor, flickering a
    little, and throws a cone of light down onto the street. Returns the lantern's centre and the cone's polygon."""
    k = -1 if night else 0
    I = lambda t: IRON[max(0, min(6, t + k))]
    # The plinth and the fluted base.
    for y, (a, b) in zip(range(g - 9, g + 1), ((-1, 3), (-1, 3), (-2, 4), (-2, 4), (-2, 4), (-2, 4), (-3, 5),
                                               (-3, 5), (-4, 6), (-4, 6))):
        for dx in range(a, b + 1):
            t = 5 if dx == a else 1 if dx == b else 3 if (dx - a) % 2 else 4
            p.px(x + dx, y, I(t))
    p.hline(x - 4, x + 7, g - 2, I(5))
    # The post and its collars.
    for y in range(top + 3, g - 9):
        p.px(x, y, I(5))
        p.px(x + 1, y, I(3))
        p.px(x + 2, y, I(1))
    for cy in (g - 22, g - 40, top + 12):
        p.hline(x - 1, x + 4, cy, I(5))
        p.hline(x - 1, x + 4, cy + 1, I(2))
    # The crook curling over to the right, and the scroll under it.
    arc = [(0, 4), (0, 3), (1, 2), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 1), (9, 1), (10, 2),
           (11, 2), (12, 3)]
    for dx, dy in arc:
        p.px(x + dx, top + dy, I(5))
        p.px(x + dx + (1 if dy < 2 else 0), top + dy + 1, I(2))
    for dx, dy in ((3, 3), (4, 3), (5, 4), (4, 5), (3, 5), (3, 4)):
        p.px(x + dx, top + dy, I(4) if dy < 5 else I(2))
    # The lantern: its cap and finial, the glass, and the bottom rim.
    lx, ly = x + reach - 1, top + 4
    p.px(lx, ly - 1, I(5))
    p.hline(lx - 2, lx + 3, ly, I(5))
    p.hline(lx - 3, lx + 4, ly + 1, I(3))
    p.hline(lx - 4, lx + 5, ly + 2, I(1))
    G = p.flicker(0) if night else "base"
    for j in range(7):
        w = 3 if j < 5 else 2
        for dx in range(-w, w + 1):
            if night:
                c = FLAME[6] if (dx < 1 and 0 < j < 5) else FLAME[5] if dx < 2 else FLAME[4]
            else:
                c = GLASS[6] if dx == -w else GLASS[5] if dx < 0 else GLASS[4] if dx < 2 else GLASS[3]
            p.px(lx + dx, ly + 3 + j, c, G)
        p.px(lx - w - 1, ly + 3 + j, I(4))
        p.px(lx + w + 1, ly + 3 + j, I(1))
    for dx in (-1, 1):
        for j in range(5):
            p.px(lx + dx * 2, ly + 3 + j, I(2) if not night else FLAME[3], G)
    p.hline(lx - 3, lx + 4, ly + 10, I(3))
    p.px(lx, ly + 11, I(2))
    cone = [(lx - 2, ly + 10), (lx + 3, ly + 10), (lx + 16, g + 1), (lx - 15, g + 1)]
    if night:
        p.halo(lx + 0.5, ly + 6.5, 16, 14, FLAME[3], (0.08, 0.16, 0.26),
               L=p.flicker(0, back=True) if motion else "haze")
        sh = p.shapes[p.layer("cone", z=-0.8)]
        for i in range(3):
            f = (3 - i) / 3
            pts = [(lx + 0.5 - 2.5 * f, ly + 10), (lx + 0.5 + 2.5 * f, ly + 10), (lx + 0.5 + 15.5 * f, g + 1),
                   (lx + 0.5 - 15.5 * f, g + 1)]
            sh.append(f'<polygon points="{" ".join(f"{num(a)},{num(b)}" for a, b in pts)}" fill="{FLAME[3]}" '
                      f'fill-opacity="{(".06", ".07", ".09")[i]}"/>')
    return (lx, ly + 6), cone


# --------------------------------------------------------------------------- the booth
HANDSET = [".hhh.", "h...h", "h...h", "h...h", "hh.hh"]   # the handset hanging, its ear and mouth cups below
SIGN = [".#######.", "##.....##", "#.......#"]               # a handset's mark, lit on the booth's sign


def booth(p: Pix, x0, g, night, motion, w=22, h=44, answered=False):
    """A phone booth of steel and glass standing on the pavement at row g from column x0, `w` wide and `h` tall: its
    roof and a sign lit with a handset's mark, its folding glass door catching a glint of the street's light, and
    inside on its back wall the payphone, ringing, its handset off the hook and swinging on its coiled cord; or, when
    `answered`, someone in a long coat inside with the handset to an ear, its cord looped from the phone; by night its
    light burns green inside the glass and glows round it, the brightest thing on its side of the street. Returns its
    span."""
    k = -1 if night else 0
    top = g - h + 1
    back = FLAME[0] if night else STEEL[2]
    p.rect(x0 + 2, top + 8, w - 4, h - 11, back)
    p.rect(x0 + 2, top + 8, w - 4, 2, FLAME[1] if night else STEEL[1])
    if night:
        p.halo(x0 + w / 2, top + h / 2, w / 2 + 7, h / 2 + 5, FLAME[3], (0.05, 0.1, 0.15))
    px0, py0 = (x0 + w - 12, top + 16) if answered else (x0 + w // 2 - 4, top + 14)
    # The payphone: its steel case, its coin slot, its dial of buttons, the hook and the coin return.
    p.rect(px0, py0, 8, 13, STEEL[3 + k])
    p.hline(px0, px0 + 8, py0, STEEL[6 + k])
    p.vline(px0, py0, py0 + 13, STEEL[5 + k])
    p.vline(px0 + 7, py0 + 1, py0 + 13, STEEL[1])
    p.hline(px0 + 1, px0 + 8, py0 + 12, STEEL[1])
    p.hline(px0 + 2, px0 + 6, py0 + 2, STEEL[0])
    key = FLAME[4] if night else STEEL[6]
    for j in range(3):
        for i in range(3):
            p.px(px0 + 2 + i * 1 + (i > 0) * 0, py0 + 5 + j * 2, key if (i + j) % 2 == 0 else STEEL[5 + k])
    p.rect(px0 + 5, py0 + 9, 2, 2, STEEL[1])
    p.vline(px0 - 1, py0 + 1, py0 + 6, STEEL[4 + k])
    p.px(px0 - 2, py0 + 1, STEEL[5 + k])
    cord = STEEL[1] if not night else STEEL[0]
    hand = STEEL[0] if not night else STEEL[1]
    if answered:
        # The caller at the left of the booth with the handset to an ear, its cord sagging across to the phone.
        cx = x0 + 3
        caller(p, cx, g - 3, night)
        hy = g - 3 - len(CALLER) + 7
        for i in range(px0 - cx - 2):
            p.px(cx + 3 + i, hy + round(4 * math.sin(math.pi * i / max(1, px0 - cx - 3))), cord)
        p.px(px0 - 1, py0 + 2, STEEL[4 + k])
        swings = ()
    else:
        swings = (-3, -1, 2, -1)
    # The handset swinging on its coiled cord, a frame for each swing.
    for n, dx in enumerate(swings):
        if motion:
            L = p.seq(f"swing{n}", n / 4, (n + 1) / 4, 1.6, keep=(n == 1), z=0.6)
        elif n == 1:
            L = "base"
        else:
            continue
        for i in range(8):
            p.px(px0 + 3 + round(dx * i / 8) + (i % 2), py0 + 13 + i, cord, L)
        sprite(p, px0 + 1 + dx, py0 + 21, HANDSET, {"h": hand}, L)
        p.px(px0 + 2 + dx, py0 + 21, STEEL[4 + k], L)
    # The ringing, a pair of marks either side that come and go, until it is answered.
    ring = FLAME[5] if night else COAT[3]
    for n, (t0, t1) in enumerate(() if answered else ((0.0, 0.2), (0.25, 0.45))):
        if motion:
            L = p.seq(f"ring{n}", t0, t1, 1.0, keep=True, z=0.7)
        else:
            L = "base"
        for side in (-1, 1):
            bx = px0 + (9 if side > 0 else -2) + (n + 1) * side
            for dy in (-2, -1, 0, 1, 2):
                if abs(dy) < 2 or n == 1:
                    p.px(bx + (0 if abs(dy) < 2 else -side), py0 + 2 + dy, ring, L)
    # The glass: a glint of the street's light on the door's panes.
    G = p.layer("boothglass", z=0.8)
    glint = GLASS[6] if not night else GLASS[3]
    for y in range(top + 9, g - 3):
        for x in range(x0 + 2, x0 + w - 2):
            if 1 <= ((x - x0) - (y - top) * 0.5) % 19 < 2:
                p.px(x, y, glint + ":0.45", G)
    # The steel: roof, sign, posts, the door's frame and its bars, and the kick plate.
    p.hline(x0 - 1, x0 + w + 1, top, STEEL[0])
    p.hline(x0 - 1, x0 + w + 1, top + 1, STEEL[6 + k])
    p.hline(x0 - 1, x0 + w + 1, top + 2, STEEL[4 + k])
    p.hline(x0 - 1, x0 + w + 1, top + 3, STEEL[1])
    sign = BOARD[1] if night else STEEL[1]
    p.rect(x0 + 1, top + 4, w - 2, 4, sign)
    mark = FLAME[6] if night else STEEL[6]
    sprite(p, x0 + w // 2 - 4, top + 4, SIGN, {"#": mark})
    if night:
        p.halo(x0 + w / 2, top + 6, w / 2 + 4, 5, FLAME[3], (0.08, 0.16))
    for y in range(top + 4, g + 1):
        for x, t in ((x0, 0), (x0 + 1, 5 + k), (x0 + w - 2, 2 + k), (x0 + w - 1, 0)):
            p.px(x, y, STEEL[max(0, t)])
    for yy in (top + 8, g - 3):
        p.hline(x0 + 2, x0 + w - 2, yy, STEEL[4 + k])
        p.hline(x0 + 2, x0 + w - 2, yy + 1, STEEL[1])
    p.hline(x0 + 1, x0 + w - 1, g - 2, STEEL[2 + k])
    p.hline(x0 + 1, x0 + w - 1, g - 1, STEEL[3 + k])
    p.hline(x0, x0 + w, g, STEEL[0])
    return (x0 - 1, x0 + w + 1)


# --------------------------------------------------------------------------- the figure
# A figure in a long dark coat striding to the left, 15 wide and 26 tall: his dark hair (h, lit H), his face in
# profile (f, shaded F) behind dark glasses (g), his coat (c, lit C, its edge e) flaring behind him as he strides, his
# hand (f) swinging, his trousers (t) and shoes (s).
FIGURE = [
    ".....hhhh......",
    "....hHHHhh.....",
    "....hHhhhh.....",
    "...fgghhhh.....",
    "..ffFFfhh......",
    "...ffFf........",
    "....fF.........",
    "....eCCe.......",
    "...eCCCce......",
    "..eCCcccce.....",
    ".eCCcccccce....",
    ".eCcCcccccce...",
    "eCc.eCccccce...",
    "ff..eCcccccce..",
    "....eCccccccce.",
    "....eCcccccccce",
    "...eCCccccccce.",
    "...eCccccccce..",
    "..eCcccc.ccce..",
    "..eCccc...cce..",
    "...ttt....tt...",
    "...tt......tt..",
    "..tt.......tt..",
    "..tt........t..",
    ".sss........ss.",
    ".ss..........ss",
]


def figure(p: Pix, x0, g, night, motion):
    """The figure in a long dark coat and dark glasses striding through the rain toward the booth, at row g from
    column x0, 26 units from crown to sole; his coat's tails flare out behind him and fall again on a loop of six
    seconds. By night his face keeps its tone and takes the lamp's green. Returns his span."""
    k = -1 if night else 0
    pal = {"h": HAIR[1], "H": HAIR[3 + k], "f": SKIN[4], "F": SKIN[2], "g": COAT[0],
           "c": COAT[2], "C": COAT[4 + k], "e": COAT[0], "t": COAT[1], "s": COAT[0]}
    top = g - len(FIGURE) + 1
    sprite(p, x0, top, FIGURE, pal)
    if motion:
        L = p.seq("coat", 0.5, 0.75, 6.0, z=0.4)
        for dy, dx in ((15, 15), (16, 15), (17, 14), (18, 14), (19, 13)):
            p.px(x0 + dx, top + dy, COAT[0], L)
            p.px(x0 + dx - 1, top + dy, pal["c"], L)
    if night:
        p.halo(x0 + 5, top + 4, 4, 3, FLAME[3], (0.12, 0.22), L="base", only={SKIN[4], SKIN[2]})
        # The lamp behind him to the left catches the edge of his coat.
        for j, row in enumerate(FIGURE):
            i = next((i for i, ch in enumerate(row) if ch in "eC"), None)
            if i is not None and 7 <= j <= 19:
                p.px(x0 + i, top + j, FLAME[1])
    return (x0, x0 + 15)


# Someone in a long dark coat and dark glasses standing in a booth and answering its phone, 12 wide and 28 tall, facing
# us with the handset held to an ear: dark hair (h, lit H), the face (f, shaded F) behind dark glasses (g), the
# handset (k), the coat (c, lit C, its edge e), trousers (t) and shoes (s).
CALLER = [
    "....hhhh....",
    "...hHHhhh...",
    "..khHhhhhh..",
    "..khffffhh..",
    "..kfggggfh..",
    "..kffffffh..",
    "..fkfFFff...",
    "..cc.fFf....",
    ".cccCcccc...",
    ".cCCcccccc..",
    "ccCcccccccc.",
    "cCccccccccc.",
    "cCcccccccccc",
    "cCcccccccccc",
    ".Cccccccccc.",
    ".Ccccccccce.",
    ".Cccccccccce",
    ".Ccccccccccc",
    ".Cccccccccce",
    ".Ccccccccccc",
    ".Cccccccccce",
    ".Cccccccccc.",
    ".Ccccc.cccc.",
    ".Cccc..cccc.",
    "..tt....tt..",
    "..tt....tt..",
    "..tt....tt..",
    ".sss....sss.",
]


def caller(p: Pix, x0, g, night, L="base"):
    """Someone answering the booth's phone, standing at row g from column x0 (see `CALLER`): by night lit green from
    the booth's light along the edge of the coat and on the face, as the walker in the street is."""
    k = -1 if night else 0
    pal = {"h": HAIR[1], "H": HAIR[3 + k], "f": SKIN[4], "F": SKIN[2], "g": COAT[0], "k": STEEL[1],
           "c": COAT[2], "C": COAT[4 + k] if not night else FLAME[1], "e": COAT[0], "t": COAT[1], "s": COAT[0]}
    sprite(p, x0, g - len(CALLER) + 1, CALLER, pal, L)
    if night:
        p.halo(x0 + 6, g - len(CALLER) + 5, 4, 3, FLAME[3], (0.12, 0.22), L="base", only={SKIN[4], SKIN[2]})


# An Agent in a dark suit striding to the left, 15 wide and 26 tall: his neat dark hair (h, lit H), his face (f, shaded
# F) behind dark glasses (g), the coiled wire of his earpiece (e), his white shirt (w, shaded W) and dark tie (k), his
# suit (c, lit C, its edge e), his trousers (t) and shoes (s).
AGENT = [
    ".....hhhh......",
    "....hHHhhh.....",
    "....hhhhhh.....",
    "...fgggfhh.....",
    "...ffFFfhe.....",
    "...ffFff.e.....",
    "....fFf..e.....",
    "....wWke.......",
    "...ecwkcce.....",
    "..eCcwkccce....",
    "..eCcwkcccce...",
    ".eCcCwkccccce..",
    ".eCcCcccccccce.",
    ".eCc.Cccccccce.",
    ".ff..Ccccccce..",
    ".....Cccccccce.",
    ".....eCccccce..",
    "....eCccc.cce..",
    "....tttt..ttt..",
    "...ttt.....tt..",
    "...tt......tt..",
    "..tt........tt.",
    "..tt........tt.",
    ".tt.........tt.",
    ".sss.........ss",
    "sss..........ss",
]


def agent(p: Pix, x0, g, night):
    """An Agent striding toward the booth along the kerb at row g from column x0 (see `AGENT`); by night the booth's
    green catches his face and the edge of his suit."""
    k = -1 if night else 0
    pal = {"h": HAIR[1], "H": HAIR[3 + k], "f": SKIN[4], "F": SKIN[2], "g": COAT[0], "w": TUBE[6] if not night
           else TUBE[4], "W": TUBE[4] if not night else TUBE[2], "k": COAT[0], "c": COAT[3], "C": COAT[5 + k],
           "e": COAT[0], "t": COAT[2], "s": COAT[0]}
    top = g - len(AGENT) + 1
    sprite(p, x0, top, AGENT, pal)
    if night:
        p.halo(x0 + 5, top + 4, 4, 3, FLAME[3], (0.12, 0.22), L="base", only={SKIN[4], SKIN[2]})
        for j, row in enumerate(AGENT[7:17], start=7):
            i = next((i for i, ch in enumerate(row) if ch in "eC"), None)
            if i is not None:
                p.px(x0 + i, top + j, FLAME[1])


# A white rabbit leaping, 11 by 9, as a poster's print shows it: r its white, e its eye.
RABBIT = [
    "........rr.",
    ".......rr..",
    "......rrrr.",
    ".....rrrerr",
    "..rrrrrrrr.",
    ".rrrrrrrr..",
    "rrrrrrrrr..",
    ".rr...rr...",
    "rr.....rr..",
]


def poster(p: Pix, x, y, night):
    """A poster pasted on the street wall at (x, y), 15 wide and 19 tall, sodden with rain: a white rabbit leaping on
    its dark ground over a line of the code, its lower corner torn and peeling, its paper darker where the rain has
    run down it."""
    k = -2 if night else 0
    paper_, ground = (STREET[5], STREET[2]) if night else (WALL[6], COAT[3])
    for yy in range(y, y + 19):
        for xx in range(x, x + 15):
            if xx - x + (y + 19 - yy) < 4 and xx - x < 4:
                continue
            edge = xx in (x, x + 14) or yy in (y, y + 18)
            p.px(xx, yy, paper_ if edge else ground)
    sprite(p, x + 2, y + 3, RABBIT, {"r": TUBE[6 + k] if not night else STEEL[4], "e": BRICK[4]})
    rnd = random.Random(5)
    for i in range(3):
        gx = x + 2 + i * 4
        for (ux, uy) in ((0, 0), (1, 0), (2, 0), (1, 1), (0, 2), (2, 2)):
            if rnd.random() < 0.8:
                p.px(gx + ux, y + 14 + uy, paper_)
    for dx, dy in ((1, 15), (2, 16), (3, 17), (1, 16), (2, 17)):
        p.px(x + dx, y + dy, paper_ if (dx + dy) % 2 else (WALL[4] if not night else STREET[3]))
    for xx in (x + 5, x + 11):
        for yy in range(y + 1, y + 12):
            if (yy - y) % 3:
                p.px(xx, yy, (WALL[4] if not night else STREET[1]) + ":0.5")


def street_sign(p: Pix, x, y, night):
    """A street's name sign of green enamel bolted to the lamppost at (x, y), 13 wide and 9 tall, the street's name
    in the code's glyphs, as the simulation spells it."""
    from .. import rain as code
    face, rim, ink = (FLAME[0], STEEL[2], TUBE[4]) if night else (FLAME[1], STEEL[5], TUBE[6])
    p.rect(x, y, 13, 9, rim)
    p.rect(x + 1, y + 1, 11, 7, face)
    for i, name in enumerate(("ka", "7")):
        for (ux, uy) in code.cells(name):
            if uy < 7:
                p.px(x + 1 + i * 6 + ux, y + 1 + uy, ink)


def steam(p: Pix, cx, g, night, motion):
    """A manhole in the street at row g, centred on column cx, its iron lid lit along its rim, and steam breathing up
    out of it, a puff rising and thinning through three frames, two seconds round; the still twin holds one puff."""
    k = -1 if night else 0
    for x in range(cx - 6, cx + 7):
        p.px(x, g, IRON[max(0, 2 + k)] if (x - cx) % 3 else IRON[max(0, 4 + k)])
    p.hline(cx - 5, cx + 6, g - 1, IRON[max(0, 5 + k)])
    puff = STREET[6] if night else C["white"]
    rnd = random.Random(6)
    for n in range(3):
        if motion:
            L = p.seq(f"steam{n}", n / 3, (n + 1) / 3, 2.4, keep=(n == 1), z=1.7)
        else:
            L = "base" if n == 1 else None
        if L is None:
            continue
        for _ in range(8 + n * 2):
            dx = rnd.gauss(0, 2 + n * 1.2)
            dy = rnd.uniform(1, 3 + n * 1.8)
            a = max(0.12, 0.42 - n * 0.08)
            p.apx(cx + dx, g - 1 - dy, puff, a, L)


def hydrant(p: Pix, x, g, night):
    """A fire hydrant at the kerb at row g from column x, 7 wide and 8 tall: its dome and cap, its body lit down its
    left side, the nozzles either side and its flanged foot."""
    k = -2 if night else 0
    R = BRICK
    rows = [(2, 4, 4), (1, 5, 5), (0, 6, 5), (1, 5, 4), (1, 5, 4), (1, 5, 4), (0, 6, 3), (0, 6, 2)]
    for j, (a, b, t) in enumerate(rows):
        for xx in range(x + a, x + b + 1):
            tone = t + (1 if xx == x + a else -1 if xx == x + b else 0)
            p.px(xx, g - 7 + j, R[max(0, min(6, tone + k))])
    p.px(x + 3, g - 8, R[max(0, 5 + k)])
    p.px(x - 1, g - 4, R[max(0, 3 + k)])
    p.px(x + 7, g - 4, R[max(0, 2 + k)])


def columns(runs) -> str:
    """Paths for upright runs of colour, [(colour, x, y, height)]: each colour's runs as strokes down the middle of
    their columns, one path a colour, every move after the first relative to where the last run ended."""
    by: dict = {}
    for c, x, y, h in runs:
        if h > 0:
            by.setdefault(c, []).append((x, y, h))
    out = []
    for c, items in by.items():
        d, at = [], None
        for x, y, h in sorted(items):
            d.append(f"M{x + 0.5:g} {y}v{h}" if at is None else f"m{x + 0.5 - at[0]:g} {y - at[1]}v{h}")
            at = (x + 0.5, y + h)
        out.append(f'<path stroke="{c}" d="{"".join(d)}"/>')
    return "".join(out)


def brace(p: Pix, x, top, R, side, night, L):
    """A curved knee brace of the El's iron where a pillar meets the girder, its corner at column x under row `top`,
    reaching R units out along the girder and down the pillar to the `side` (1 right, -1 left): a flange of plate
    bent on a quarter circle, lit on its outer edge and in shade on its inner, riveted along it, and between it and
    the corner a web of plate pierced in a lattice the wall shows through."""
    k = -1 if night else 0
    I = lambda t: IRON[max(0, min(6, t + k))]
    for v in range(R):
        for u in range(R):
            d = math.hypot(R - u - 0.5, R - v - 0.5)
            if d < R - 3:
                continue
            if d >= R:
                if u > 1 and v > 1 and (u + v) % 4 == 0 and d > R + 1.2:
                    continue
                c = I(2) if (u + v) % 4 != 1 else I(3)
            else:
                c = I(5) if d >= R - 1 else I(3) if d >= R - 2 else I(1)
                if R - 2 <= d < R - 1 and (u + v) % 4 == 0:
                    c = I(6)
            p.px(x + side * u, top + v, c, L)


def pillar(p: Pix, x0, top, g, night, w=11, braces=(0, 0)):
    """A pillar of the El from the girder at row `top` down to the kerb at row g from column x0, `w` wide: riveted
    plate lit down its left face and in shade down its right, a cap where it meets the girder, a flared foot, and a
    curved knee brace up to the girder from either side of it as far out as `braces` (left, right; 0 for none). Its
    plate is drawn as upright strokes, a path a tone."""
    k = -1 if night else 0
    I = lambda t: IRON[max(0, min(6, t + k))]
    L = p.layer("pillar", z=-0.5)
    runs = []
    for x in range(x0, x0 + w):
        u = (x - x0) / w
        t = 0 if x in (x0, x0 + w - 1) else 5 if u < 0.2 else 4 if u < 0.5 else 2
        runs.append((I(t), x, top, g + 1 - top))
    runs += [(I(0), x0 - 1, g - 3, 4), (I(0), x0 + w, g - 3, 4)]
    p.shapes[L].append(columns(runs))
    for y in range(top + 3, g - 4, 4):
        p.px(x0 + 2, y, I(6), L)
        p.px(x0 + w - 3, y, I(4), L)
    for y in (top + 1, g - 4):
        p.hline(x0 - 1, x0 + w + 1, y, I(4), L)
    p.hline(x0 - 1, x0 + w + 1, top, I(0), L)
    if braces[0]:
        brace(p, x0 - 1, top, braces[0], -1, night, L)
    if braces[1]:
        brace(p, x0 + w, top, braces[1], 1, night, L)


def signal(p: Pix, x, top, night, motion):
    """A traffic signal hung from the El's girder at column x on a rod from row `top`: its housing of black iron with
    a hood over each of its three lamps, the red and the amber dark and the green lit the hand's phosphor, glowing
    round it by night, the whole thing swaying a unit in the wind on a slow beat. Returns its box."""
    k = -1 if night else 0
    I = lambda t: IRON[max(0, min(6, t + k))]
    p.vline(x, top, top + 3, I(4))
    p.vline(x + 1, top, top + 3, I(1))
    hx, hy = x - 3, top + 3
    for yy in range(hy, hy + 20):
        for xx in range(hx, hx + 8):
            edge = xx in (hx, hx + 7) or yy in (hy, hy + 19)
            p.px(xx, yy, I(0) if edge else I(1) if xx > hx + 4 else I(2))
    for n, (dark, lit) in enumerate(((BRICK[1], None), (RUST[1], None), (FLAME[1], True))):
        cy = hy + 3 + n * 6
        for dy in range(-2, 3):
            for dx in range(-2, 2):
                if abs(dy) == 2 and dx in (-2, 1):
                    continue
                if lit:
                    c = (FLAME[6] if dx < 0 and dy < 1 else FLAME[5]) if night else \
                        (FLAME[5] if dx < 0 and dy < 1 else FLAME[4])
                else:
                    c = dark
                p.px(x + dx, cy + dy, c)
        p.hline(x - 3, x + 3, cy - 3, I(4))
        p.px(x - 3, cy - 2, I(3))
        p.px(x + 2, cy - 2, I(1))
    if night:
        p.halo(x, hy + 15, 9, 8, FLAME[3], (0.06, 0.12, 0.2))
    return hx - 1, top, hx + 9, hy + 20


def corner(p: Pix, x0, g, night, motion, walker=True, posted=True, braces=(0, 0)) -> tuple:
    """The left of the street, standing on the kerb at row g from column x0: the streetlamp, its lantern hung over the
    phone booth, the booth with its payphone ringing, and when `walker` the figure striding to it, when `posted` a
    pillar of the El behind him with a poster pasted on it, braced to the girder as far out as `braces`. Returns its
    span, the lamp's cone of light, the booth's box, which the rain keeps out of, and the columns of the lamp's and
    the booth's light and of the pillar (None without it), which lie in the wet street."""
    reach = 52 if walker else 36
    if posted:
        pillar(p, x0 + 31, GIRDER, g, night, w=13, braces=braces)
        poster(p, x0 + 30, g - 58, night)
    (lx, ly), cone = streetlamp(p, x0 + 1, g, 19, night, motion, reach=13)
    street_sign(p, x0 + 3, g - 55, night)
    booth(p, x0 + 7, g, night, motion)
    if walker:
        figure(p, x0 + 36, g, night, motion)
    return (x0 - 1, x0 + reach), cone, (x0 + 6, g - 43, x0 + 30, g - 2), (lx, x0 + 18, x0 + 37 if posted else None)


# --------------------------------------------------------------------------- the tenement
def _bricks(uid: str, night: bool) -> str:
    """The tenement's brick as a pattern tile 8 by 6: courses of bricks in stretcher bond, each lit along its top,
    in mortar a tone off the brick."""
    k = -3 if night else 0
    cells = {}
    for y in range(6):
        for x in range(8):
            course = y // 3
            u = (x + (4 if course else 0)) % 8
            v = y % 3
            if v == 2 or u == 7:
                c = MORTAR[max(0, 2 + k)]
            elif v == 0:
                c = BRICK[max(0, 4 + k)]
            else:
                c = BRICK[max(0, 3 + k)] if (u + course) % 5 else BRICK[max(0, 2 + k)]
            cells[(x, y)] = c
    return f'<pattern id="{uid}" width="8" height="6" patternUnits="userSpaceOnUse">{fills(cells)}</pattern>'


def window(p: Pix, x, y, night, lit, motion, phase=0, shade=0, watcher=False):
    """A tenement window, 9 wide and 12 tall, its top-left at (x, y): a lintel and a sill of stone, its sash in two
    panes, dark by day with the sky's grey in its glass, and by night dark or lit green from inside, its blind drawn
    `shade` rows down, and at a `watcher`'s window someone standing in it, looking down on the street."""
    k = -2 if night else 0
    p.hline(x - 1, x + 10, y - 1, MORTAR[max(0, 5 + k)])
    p.hline(x - 1, x + 10, y, MORTAR[max(0, 3 + k)])
    for yy in range(y + 1, y + 12):
        for xx in range(x, x + 9):
            if xx in (x, x + 8) or yy in (y + 1, y + 6):
                c = MORTAR[max(0, 4 + k)] if xx == x or yy == y + 1 else MORTAR[max(0, 2 + k)]
            elif night and lit:
                c = BOARD[2] if yy < y + 2 + shade else FLAME[2] if yy > y + 6 else FLAME[1]
            elif night:
                c = STREET[1] if (xx - x) + (yy - y) > 6 else STREET[3]
            else:
                c = GLASS[3] if (xx - x) + (yy - y) < 7 else GLASS[1]
            p.px(xx, yy, c)
    if night and lit:
        p.halo(x + 4.5, y + 7, 8, 7, FLAME[2], (0.06, 0.12), L=p.layer("brickglow", z=-0.85))
        if watcher:
            for dx, dy in ((4, 6), (5, 6), (4, 7), (5, 7), (4, 8), (5, 8), (3, 9), (6, 9), (2, 10), (7, 10)):
                p.px(x + dx, y + dy, BOARD[1])
            for xx in range(x + 3, x + 7):
                p.px(xx, y + 9, BOARD[1])
                p.px(xx, y + 10, BOARD[1])
    p.hline(x - 1, x + 10, y + 12, MORTAR[max(0, 5 + k)])
    p.hline(x - 1, x + 10, y + 13, MORTAR[max(0, 2 + k)])


def fire_escape(p: Pix, x0, x1, floors, g, night):
    """The fire escape down the tenement's front from column x0 to x1: a landing of iron at each of `floors`, its
    railing of bars, the stairs zigzagging down between them, and the drop ladder hanging over the street."""
    k = -1 if night else 0
    rail, bar, dark = IRON[max(0, 4 + k)], IRON[max(0, 2 + k)], IRON[0]
    for i, fy in enumerate(floors):
        p.hline(x0, x1, fy, rail)
        p.hline(x0, x1, fy + 1, dark)
        p.hline(x0, x1, fy - 5, rail)
        for x in range(x0, x1, 2):
            p.vline(x, fy - 4, fy, bar)
        if i + 1 < len(floors):
            ny = floors[i + 1]
            a, b = (x0 + 2, x1 - 4) if i % 2 == 0 else (x1 - 4, x0 + 2)
            n = ny - fy
            for s in range(n):
                xx = round(a + (b - a) * s / n)
                p.px(xx, fy + 2 + s, rail)
                p.px(xx + 1, fy + 2 + s, dark)
                if s % 2 == 0:
                    p.px(xx + (1 if b > a else -1), fy + 1 + s, bar)
    last = floors[-1]
    lx = x0 + 4
    for y in range(last + 2, min(g - 6, last + 14)):
        p.px(lx, y, rail)
        p.px(lx + 3, y, rail)
        if (y - last) % 3 == 0:
            p.hline(lx, lx + 4, y, bar)


def hotel_sign(p: Pix, x, y, night, motion):
    """The hotel's vertical neon sign, 9 wide, hung off the brick at (x, y) on two iron brackets: a dark box in a steel
    rim, and down it HOTEL in glass tubes, unlit by day, burning the hand's phosphor by night with its glow round it,
    the E guttering. Returns its foot."""
    k = -1 if night else 0
    letters = "HOTEL"
    h = len(letters) * 9 + 3
    p.rect(x, y, 9, h, BOARD[0])
    p.rect(x + 1, y + 1, 7, h - 2, BOARD[2] if not night else BOARD[1])
    p.vline(x + 1, y + 1, y + h - 1, STEEL[4 + k])
    for by in (y + 4, y + h - 6):
        p.hline(x + 9, x + 13, by, IRON[max(0, 3 + k)])
        p.px(x + 13, by + 1, IRON[max(0, 1 + k)])
    glyphs = FONTS["57"][0]
    for i, ch in enumerate(letters):
        gw, rows = glyphs[ch]
        lx, ly = x + 2 + (5 - gw) // 2, y + 2 + i * 9
        L = p.flicker(1) if (night and motion and ch == "E") else "base"
        for r, cols in enumerate(rows):
            for col in cols:
                if night:
                    p.px(lx + col, ly + r, FLAME[6] if r % 6 == 0 or col == min(cols) else FLAME[5], L)
                else:
                    p.px(lx + col, ly + r, TUBE[5] if r == 0 or col == min(cols) else TUBE[3], L)
    if night:
        p.halo(x + 4.5, y + h / 2, 17, h / 2 + 9, FLAME[3], (0.12, 0.25, 0.42), L=p.layer("brickglow", z=-0.85))
    return y + h


def tenement(p: Pix, x0, x1, g, night, motion) -> tuple:
    """The right of the street, standing on the pavement at row g from column x0 to x1: the brick front of a tenement
    rising out of the sheet, its windows in two columns over three floors, some lit green by night, or one column
    where the words leave it less room, its fire escape zigzagging down it, the vertical neon sign HOTEL hung off its
    corner. Returns its span and the column of the sign's light, which lies in the wet street."""
    k = -2 if night else 0
    top = GIRDER + 2
    uid = f"{getattr(p, 'sheet', 'p')}bk"
    p.defs.append(_bricks(uid, night))
    p.shapes[p.layer("brick", z=-0.9)].append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{g - top + 1}" '
                                               f'fill="url(#{uid})"/>')
    for y in range(top, g + 1):
        p.px(x0, y, MORTAR[max(0, 5 + k)] if (y // 3) % 2 else MORTAR[max(0, 3 + k)])
        p.px(x0 + 1, y, MORTAR[max(0, 3 + k)] if (y // 3) % 2 else MORTAR[max(0, 2 + k)])
    rnd = random.Random(4)
    floors = []
    wide = x1 - x0 >= 50
    cols = (x0 + 6, x0 + 20) if wide else (x0 + 6,)
    for i, wy in enumerate(range(top + 6, g - 20, 22)):
        for j, wx in enumerate(cols):
            lit = rnd.random() < 0.45 or (i, j) == (1, 0)
            window(p, wx, wy, night, lit, motion, shade=rnd.choice((1, 3, 4)) if (i, j) != (1, 0) else 1,
                   watcher=(i, j) == (1, 0))
        floors.append(wy + 16)
    fire_escape(p, x0 + 3, x0 + (32 if wide else 18), floors, g, night)
    sx = x1 - 13
    hotel_sign(p, sx, top + 8, night, motion)
    # The doorway at the foot, and the wet pavement holding the light.
    dx = x0 + (34 if wide else 19)
    p.rect(dx, g - 14, 8, 15, STREET[0] if night else WALL[0])
    p.hline(dx - 1, dx + 9, g - 15, MORTAR[max(0, 5 + k)])
    p.vline(dx - 1, g - 14, g + 1, MORTAR[max(0, 4 + k)])
    p.vline(dx + 8, g - 14, g + 1, MORTAR[max(0, 2 + k)])
    return (x0 - 1, x1 + 1), sx + 4


# --------------------------------------------------------------------------- a section's and a strip's heroes
CALLBOX_W, CALLBOX_H = 32, 70     # the booth a section's header stands close up, wide and tall


def callbox(p: Pix, x0, x1, g, night, motion, room, top=GIRDER) -> tuple:
    """A section's hero, the booth answered, standing on the kerb at row g between columns x0 and x1 with `room` rows
    free over it: the wet street along the foot; the streetlamp at the left with its lantern hung over the booth; the
    booth close up and tall, someone in a long coat inside with the handset to an ear (see `booth`); where the words
    leave the width, an Agent striding toward it, a pillar of the El at the right braced to the girder with a poster
    of the white rabbit on it, and a hydrant at the kerb; the light of the booth and the lamp lying in the wet street,
    and the rain slanting down through it all. The pillar rises from row `top`, the girder's foot on a wide header and
    the top of the room under a phone's words. Returns its span."""
    w = x1 - x0
    depth = min(8, max(0, room - CALLBOX_H - 4))
    gs = g - depth
    if depth:
        street(p, x0, x1, gs, g, night)
    h = min(CALLBOX_H, room - depth - 2)
    bw = CALLBOX_W if w >= CALLBOX_W + 24 else CALLBOX_W - 6
    lamp = w >= bw + 20
    bx = x0 + 18 if lamp else x0 + max(1, (w - bw) // 2)
    keep = (bx + 1, gs - h + 9, bx + bw - 1, gs - 2)
    lights = []
    if w >= bw + 62:
        pillar(p, x1 - 24, top, gs, night, w=11, braces=(9, 0) if top == GIRDER else (0, 0))
        poster(p, x1 - 26, max(top + 4, gs - 58), night)
    if w >= bw + 32:
        hydrant(p, x1 - 9, gs, night)
        lights.append((x1 - 6, 2, None, BRICK[1]) if night else (x1 - 6, 2, BRICK[4], BRICK[3]))
    if w >= bw + 54 and lamp:
        agent(p, x0 + 18 + bw + 5, gs, night)
    cone = None
    if lamp:
        (lx, _), cone = streetlamp(p, x0 + 3, gs, max(top + 4, gs - h - 14), night, motion, reach=17)
        lights.append((lx, 2, FLAME[5], FLAME[3]) if night else (lx, 2, WALL[6], WALL[5]))
    booth(p, bx, gs, night, motion, w=bw, h=h, answered=True)
    lights.append((bx + bw // 2, 5, FLAME[4], FLAME[2]) if night else (bx + bw // 2, 5, WALL[6], WALL[5]))
    if depth:
        pools = [(bx + bw // 2, bw // 2 + 6, FLAME[3])] if night else []
        reflections(p, lights, x0, x1, gs, g, pools)
        ripples(p, x0, x1, gs, g, motion, night, n=2, seed=x0)
    rain(p, [(x0, top + 1, x1, g + 1)], night, lit=cone, keep=[keep])
    return (x0 - 1, x1 + 1)


def hotel(p: Pix, x0, x1, g, night, motion, room) -> tuple:
    """A strip's hero, the hotel's corner, rising the strip's full height at the right on the kerb at row g between
    columns x0 and x1 with `room` rows free over it: its brick front from the girder down to the street, its windows
    in columns as many as its width holds, some lit green by night and someone watching from one, the fire escape
    zigzagging down where there are two columns or more, its doorway at the foot under a canopy, and hung off its corner
    on iron brackets the vertical neon sign HOTEL, unlit by day and by night burning the hand's phosphor, its light
    pooled on the brick; a hydrant at the kerb, the wet street holding the sign's light, and the rain falling past.
    Returns its span."""
    k = -2 if night else 0
    depth = min(6, max(0, room - 52))
    gs = g - depth
    top = gs - room + depth + 1
    if depth:
        street(p, x0, x1, gs, g, night)
    wall = x0 + 14
    uid = f"{getattr(p, 'sheet', 'p')}bk"
    if ("bricks", night) not in p.syms:
        p.defs.append(_bricks(uid, night))
        p.syms[("bricks", night)] = uid
    p.shapes[p.layer("brick", z=-0.9)].append(f'<rect x="{wall}" y="{top}" width="{x1 - wall}" height="{gs - top + 1}" '
                                               f'fill="url(#{uid})"/>')
    for y in range(top, gs + 1):
        p.px(wall, y, MORTAR[max(0, 5 + k)] if (y // 3) % 2 else MORTAR[max(0, 3 + k)])
        p.px(wall + 1, y, MORTAR[max(0, 3 + k)] if (y // 3) % 2 else MORTAR[max(0, 2 + k)])
    cols = list(range(wall + 8, x1 - 11, 16))
    floors = []
    for i, wy in enumerate(range(top + 4, gs - 24, 16)):
        for j, wx in enumerate(cols):
            window(p, wx, wy, night, (i + j) % 3 != 1, motion, shade=(1, 3, 2)[(i + j) % 3], watcher=(i, j) == (0, 0))
        floors.append(wy + 14)
    if len(cols) > 1 and len(floors) > 1:
        fire_escape(p, wall + 6, wall + 36, floors, gs, night)
    # The doorway under its canopy, a lamp over it.
    dx = cols[1] + 1 if len(cols) > 1 else wall + 9
    p.rect(dx, gs - 14, 9, 15, STREET[0] if night else WALL[0])
    p.vline(dx - 1, gs - 14, gs + 1, MORTAR[max(0, 4 + k)])
    p.vline(dx + 9, gs - 14, gs + 1, MORTAR[max(0, 2 + k)])
    for i in range(14):
        p.px(dx - 3 + i, gs - 17, BRICK[max(0, 5 + k)] if i % 2 else BRICK[max(0, 3 + k)])
        p.px(dx - 3 + i, gs - 16, BRICK[max(0, 2 + k)])
    p.px(dx + 4, gs - 15, FLAME[5] if night else GLASS[5])
    sy = top + max(2, (gs - top - 48) // 2 - 2)
    hotel_sign(p, x0 + 1, sy, night, motion)
    hydrant(p, x1 - 9, gs, night)
    if depth:
        lights = [(x0 + 5, 2, FLAME[5], FLAME[3]) if night else (x0 + 5, 2, BOARD[3], WALL[1]),
                  (x1 - 6, 2, None, BRICK[1]) if night else (x1 - 6, 2, BRICK[4], BRICK[3])]
        reflections(p, lights, x0, x1, gs, g)
    rain(p, [(x0, top, x1, g + 1)], night)
    return (x0 - 1, x1 + 1)


def phone_street(p: Pix, g, night, room) -> tuple:
    """A phone's H1, the whole street across the phone under its words, on the kerb at row g with `room` rows free
    over it: the streetlamp and the booth with its payphone ringing at the left, the figure in the long coat striding
    to it, the hotel's corner at the right with its sign, a hydrant at its kerb, the wet street along the foot
    holding every light, and the rain over it all. Returns its span."""
    x0, x1 = EDGE + 1, p.w - EDGE - 1
    depth = 6 if room >= 50 else 0
    gs = g - depth
    top = g - room + 1
    if depth:
        street(p, x0, x1, gs, g, night)
    h = min(40, room - depth - 4)
    (lx, _), cone = streetlamp(p, x0 + 1, gs, max(top + 2, gs - h - 12), night, False, reach=12)
    booth(p, x0 + 8, gs, night, False, w=18, h=h)
    figure(p, x0 + 34, gs, night, False)
    hx = x1 - 52
    hotel(p, hx, x1, g, night, False, room)
    if depth:
        lights = [(lx, 2, FLAME[5], FLAME[3]) if night else (lx, 2, WALL[6], WALL[5]),
                  (x0 + 17, 3, FLAME[4], FLAME[2]) if night else (x0 + 17, 3, WALL[6], WALL[5])]
        reflections(p, lights, x0, hx - 1, gs, g, [(x0 + 17, 12, FLAME[3])] if night else [])
    rain(p, [(x0, top, hx, g + 1)], night, lit=cone, keep=[(x0 + 9, gs - h + 9, x0 + 25, gs - 2)])
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the footers
FOOT_RISE = 5     # the rows the girder along a footer's foot deepens by where the cells leave it room
FOOT_RUN = 18     # the fewest columns it deepens along
FOOT_LEAST = 12   # the fewest columns any stretch of it runs along between words


def booth_mark(p: Pix, x, y, night, L="base"):
    """A phone booth, 13 wide and 24 tall, its top-left at (x, y): the emblem a footer carries after its last cell.
    Its steel frame and roof, the sign on the roof with a handset's mark, its glass and the payphone on the back wall;
    by night its light burns green inside the glass, flickering a little, and its sign glows."""
    k = -1 if night else 0
    F = p.flicker(2) if night else L
    p.rect(x + 1, y + 6, 11, 16, FLAME[1] if night else STEEL[2], F)
    p.rect(x + 7, y + 9, 3, 5, STEEL[4 + k])
    p.px(x + 6, y + 10, STEEL[1])
    for yy in range(y + 7, y + 21):
        if (yy - y) % 5 == 0:
            p.hline(x + 1, x + 12, yy, STEEL[4 + k], L)
    p.hline(x, x + 13, y, STEEL[0], L)
    p.hline(x, x + 13, y + 1, STEEL[5 + k], L)
    p.rect(x + 1, y + 2, 11, 4, BOARD[1] if night else STEEL[1], L)
    for (dx, dy) in ((3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (3, 4), (9, 4)):
        p.px(x + dx, y + dy, FLAME[6] if night else STEEL[6], F if night else L)
    for yy in range(y + 2, y + 24):
        p.px(x, yy, STEEL[0], L)
        p.px(x + 12, yy, STEEL[0], L)
    p.hline(x, x + 13, y + 22, STEEL[3 + k], L)
    p.hline(x, x + 13, y + 23, STEEL[0], L)
    if night:
        p.halo(x + 6.5, y + 12, 11, 14, FLAME[3], (0.06, 0.12), L=p.flicker(2, back=True))


def lamp_mark(p: Pix, x, y, night):
    """A streetlamp's lantern on its bracket, 9 wide and 11 tall, its top-left at (x, y): the ornament in the corner of
    a title block's notes; by night its glass burns the hand's phosphor, flickering, and glows round it."""
    k = -1 if night else 0
    p.hline(x, x + 6, y, IRON[4 + k])
    p.px(x + 6, y + 1, IRON[4 + k])
    p.px(x, y + 1, IRON[2 + k])
    p.hline(x + 4, x + 9, y + 2, IRON[5 + k])
    p.hline(x + 3, x + 10, y + 3, IRON[2 + k])
    G = p.flicker(0) if night else "base"
    for j in range(5):
        for dx in range(4, 9):
            c = (FLAME[6] if dx < 6 else FLAME[5]) if night else (GLASS[6] if dx == 4 else GLASS[4] if dx < 7 else
                                                                  GLASS[3])
            p.px(x + dx, y + 4 + j, c, G)
        p.px(x + 3, y + 4 + j, IRON[4 + k])
        p.px(x + 9, y + 4 + j, IRON[1])
    p.hline(x + 3, x + 10, y + 9, IRON[3 + k])
    p.px(x + 6, y + 10, IRON[2 + k])
    if night:
        p.halo(x + 6.5, y + 6.5, 7, 6, FLAME[3], (0.08, 0.16), L=p.flicker(0, back=True))


def footing(p: Pix, night: bool, after=0):
    """A footer once its words are set: the El's riveted girder along its foot on the kerb the frame lays there, its
    flanges lit along their tops and its lattice of flat bars between them, as deep as keeps a row clear of the words
    over each column (and none under a word that comes down to the kerb), and a course deeper wherever the cells leave
    it room along FOOT_RUN columns or more; and at the rightmost place from column `after` on where the cells leave
    the wall free, the phone booth standing on the girder, lit by night (see `booth_mark`)."""
    w, h = p.w, p.h
    k = -1 if night else 0
    foot = h - EDGE
    ledge = foot - 6
    base = p.layers["base"]

    def lowest(x):
        """The row under the lowest word over column x and the columns beside it, a row of margin under it."""
        return max((b[3] + 1 for b in p.words if b[0] - 1 <= x < b[2] + 1), default=0)

    def free(x0, y0, x1, y1):
        return 5 <= x0 and x1 <= w - 5 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0 - 1, x1 + 1) for y in range(y0, y1))
    mark = next((x for x in range(w - 6 - 13, max(EDGE + 1, after) - 1, -1) if free(x, ledge - 25, x + 13, ledge)),
                None)
    taken = (mark - 2, mark + 15) if mark is not None else (0, 0)
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
    uid = f"{getattr(p, 'sheet', 'p')}gl"
    if ("lattice", night) not in p.syms:
        p.defs.append(_lattice(uid, night))
        p.syms[("lattice", night)] = uid
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
    web = p.shapes[p.layer("lattice", z=0.05)]
    for a, b, t in runs:
        n = b - a
        p.hline(a, b, t, IRON[5 + k])
        if t + 1 < foot - 1:
            p.hline(a, b, t + 1, IRON[3 + k])
        if foot - 1 - (t + 2) > 0:
            for yy in range(t + 2, foot - 1):
                p.hline(a, b, yy, IRON[1])
            web.append(f'<rect x="{a}" y="{t + 2}" width="{n}" height="{foot - 1 - (t + 2)}" fill="url(#{uid})"/>')
        p.hline(a, b, foot - 1, IRON[0])
        for xx in range(a + 2, b - 1, 6):
            p.px(xx, t, IRON[6 + k])
            if t < ledge:
                p.px(xx, t + 2, IRON[6 + k])
    for x in range(EDGE + 1, w - EDGE):
        a, b = tops[x - 1], tops[x]
        if a != b and min(a, b) <= foot - 2:
            for y in range(min(a, b), min(foot, max(a, b))):
                p.px(x if b < a else x - 1, y, IRON[4 + k] if b < a else IRON[1])
    if mark is not None:
        booth_mark(p, mark, ledge - 24, night)


# ------------------------------------------------------------------------ the marks beside the titles, and the rule's
# An EXIT sign, 17 wide and 9 tall: its plate (b) in a rim (o), lit along its top (t) and shaded along its foot and
# right side (d), and its four letters (e). The small one, 7 tall, is the same plate without the rows over and under
# the letters.
EXIT_SIGN = [
    ".ooooooooooooooo.",
    "otttttttttttttttd",
    "obeeebebebebeeebd",
    "obebbbebebebbebbd",
    "obeebbbebbebbebbd",
    "obebbbebebebbebbd",
    "obeeebebebebbebbd",
    "obbbbbbbbbbbbbbbd",
    ".ddddddddddddddd.",
]
EXIT_SMALL = ["o" * 17, *EXIT_SIGN[2:7], "d" * 17]


def exit_sign(p: Pix, x, y, night, small=False, L="base"):
    """An EXIT sign, its top-left at (x, y): by day a plate of street-sign green enamel lettered white; by night a dark
    box whose letters burn the hand's phosphor, glowing round it and guttering now and then, the way out of the
    street."""
    art = EXIT_SMALL if small else EXIT_SIGN
    if night:
        pal = {"o": STEEL[1], "t": STEEL[3], "b": BOARD[1], "d": STEEL[0], "e": FLAME[6]}
    else:
        pal = {"o": ENAMEL[0], "t": ENAMEL[5], "b": ENAMEL[3], "d": ENAMEL[1], "e": TUBE[6]}
    lit = {ch: c for ch, c in pal.items() if ch != "e"}
    sprite(p, x, y, art, lit, L)
    F = p.flicker(1) if night else L
    sprite(p, x, y, art, {"e": pal["e"]}, F)
    if night:
        h = len(art)
        p.halo(x + 8.5, y + h / 2, 12, h / 2 + 3, FLAME[3], (0.06, 0.12), L=p.flicker(1, back=True))


# A payphone on a wall, 19 wide and 19 tall, ringing: its steel case (s, lit S down its left, shaded d down its right,
# rimmed o) with its little window (g, its line of light L), its keys (k) and its coin return (x, X); the handset (h,
# lit H) in its cradle (c) on the case's left, its cord (w) coiled down from it into the case; and the ringing, a mark
# either side (r).
PAYPHONE = [
    "........ooooooo....",
    ".r.....oSSSSSSdo.r.",
    "r......oSgggggdo..r",
    "r......oSgLLLgdo..r",
    ".r.....oSgggggdo.r.",
    "...hhhcoSsssssdo...",
    "...hHhcoSkskskdo...",
    "....h.coSsssssdo...",
    "....h.coSkskskdo...",
    "....h.coSsssssdo...",
    "....h.coSkskskdo...",
    "....h.coSsssssdo...",
    "....h.coSkskskdo...",
    "...hhhcoSsssssdo...",
    "...hHhcoSsxxxsdo...",
    "....w..oSsxXxsdo...",
    "...w...oSsssssdo...",
    "....w..oddddddo....",
    ".....ww.ooooooo....",
]


def payphone(p: Pix, x, y, night, L="base"):
    """A payphone on the wall, its top-left at (x, y), ringing: its steel case, its window, its keys and its handset in
    the cradle on its coiled cord, a mark of its ringing either side; by night its window and keys burn the hand's
    phosphor and the ringing with them."""
    k = -1 if night else 0
    pal = {"o": STEEL[0], "S": STEEL[5 + k], "s": STEEL[3 + k], "d": STEEL[1], "x": STEEL[1], "X": STEEL[0],
           "c": STEEL[1] if not night else STEEL[3]}
    if night:
        pal.update({"g": BOARD[1], "L": FLAME[6], "k": FLAME[4], "h": STEEL[3], "H": STEEL[5], "w": STEEL[3],
                    "r": FLAME[5]})
    else:
        pal.update({"g": GLASS[1], "L": GLASS[4], "k": STEEL[6], "h": COAT[1], "H": COAT[4], "w": COAT[2],
                    "r": COAT[3]})
    sprite(p, x, y, PAYPHONE, pal, L)
    if night:
        p.halo(x + 11.5, y + 3.5, 5, 3, FLAME[3], (0.08, 0.16), L=p.flicker(0, back=True))


def rule_bits(p: Pix, x0, x1, y, seed, night):
    """What lies on a header's rule where no scene stands: the iron strap it is, riveted at intervals, and here and
    there a puddle of the rain lying on it, its sheen catching the light (by night the neon's green), and in a moving
    header the rain's drops falling into it in turn, each ringing out across its water (the still file keeps one
    ring); each only where it keeps two units clear of the words."""
    rnd = random.Random(seed)
    if night:
        water, deep, sheen, ring = STREET[5], STREET[4], FLAME[2], FLAME[4]
        head, lit, shadow = STEEL[4], STEEL[2], STEEL[0]
    else:
        water, deep, sheen, ring = GLASS[3], GLASS[2], GLASS[6], GLASS[6]
        head, lit, shadow = STEEL[6], STEEL[4], IRON[1]
    x = x0 + 6 + rnd.randrange(0, 12)
    n = 0
    while x + 12 < x1:
        if n % 3 == 1 and p.clear_of_words(x - 3, y - 6, x + 16, y + 3):
            w = rnd.choice((11, 13))
            cx = x + w // 2
            p.hline(x, x + w, y, deep)
            p.hline(x + 2, x + w - 2, y - 1, water)
            p.hline(x + 3, x + 5, y - 1, sheen)
            p.px(x + w - 4, y - 1, sheen)
            phase = (n // 3) % 2
            for f, cells in enumerate((((0, -4),), ((0, -3),), ((0, -1),), ((-1, -1), (1, -1)),
                                       ((-2, 0), (2, 0), (-3, 0), (3, 0)))):
                t0 = (f / 5 + phase / 2) % 1
                L = p.seq(f"drip{phase}{f}", t0, t0 + 0.2, 1.8, keep=(f == 3), z=0.5)
                for dx, dy in cells:
                    p.px(cx + dx, y + dy, ring if dy > -2 else (X["rain_night"] if night else GLASS[4]), L)
            x += w + 16 + rnd.randrange(0, 10)
        elif p.clear_of_words(x - 2, y - 3, x + 4, y + 3):
            p.px(x, y - 1, head)
            p.px(x + 1, y - 1, lit)
            p.px(x, y, lit)
            p.px(x + 1, y, shadow)
            x += 22 + rnd.randrange(0, 12)
        else:
            x += 8
        n += 1


# --------------------------------------------------------------------------- the footers', links' and badges' sprites
# The link buttons' icons, seven by seven, things of the street: the payphone's handset, the white rabbit, the
# streetlamp, the hydrant, the traffic signal and the phone booth. Each letter is looked up in `icon_pal`.
ICONS = {
    "handset": [".......", ".hhhhh.", "hH...Hh", "hh...hh", ".......", ".......", "......."],
    "rabbit": ["....ww.", "...ww..", "..wwww.", ".wwwwew", "wwwwww.", "ww..ww.", "w....w."],
    "lamp": [".ppp...", "p..p...", "p.LLL..", "p.LlL..", "p......", "p......", "ppp...."],
    "hydrant": ["..rr...", ".rRrr..", "rrRrrr.", ".rRrr..", ".rRrr..", ".rRrr..", "rrrrrr."],
    "signal": [".iiii..", ".iRDi..", ".iYDi..", ".iGgi..", ".iiii..", "..ii...", "..ii..."],
    "booth": ["sssssss", "sGGGGGs", "sg...gs", "sg.h.gs", "sg...gs", "sg...gs", "sssssss"],
}
LINK_ICONS = ("handset", "rabbit", "lamp", "hydrant", "signal", "booth")


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones: the handset's black, the rabbit's white, the El's iron for the lamp's post and the signal's
    housing, the hydrant's red, the booth's steel and glass; the lamp's lantern, the signal's green lamp and the
    booth's sign burn the hand's phosphor, brighter by night."""
    k = -1 if night else 0
    return {"h": COAT[1] if not night else STEEL[5], "H": COAT[4] if not night else STEEL[6],
            "w": TUBE[6] if not night else TUBE[5], "e": BRICK[4], "p": IRON[3 + k] if not night else IRON[5],
            "L": FLAME[5] if night else FLAME[4], "l": FLAME[6] if night else FLAME[5], "r": BRICK[4 + k],
            "R": BRICK[6 + k], "i": IRON[1] if not night else IRON[4], "D": BRICK[1], "Y": RUST[1],
            "G": FLAME[5] if night else FLAME[4], "g": FLAME[3], "s": STEEL[3 + k] if not night else STEEL[5],
            "#": ink}


def heart(p: Pix, x, y, L="base"):
    """A heart bent from a neon tube, seven by six, burning the hand's phosphor, white-hot along its upper lobes."""
    art = [".65.65.", "6544456", "5444445", ".54445.", "..545..", "...5..."]
    p.sprite(x, y, art, {str(i): FLAME[i] for i in range(7)}, 1, L)


# --------------------------------------------------------------------------- the elements' pieces
def rivet(p: Pix, x, y, night, L="base"):
    """A rivet's domed head in the El's iron, two pixels square at (x, y), lit on its upper left."""
    k = -1 if night else 0
    p.px(x, y, IRON[6 + k], L)
    p.px(x + 1, y, IRON[4 + k], L)
    p.px(x, y + 1, IRON[4 + k], L)
    p.px(x + 1, y + 1, IRON[1], L)


def bolt(p: Pix, cx, cy, night):
    """A hex bolt's head of steel, five pixels across, centred on (cx, cy)."""
    k = -1 if night else 0
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if abs(dx) == 2 and abs(dy) == 2:
                continue
            t = 6 if dx + dy < -1 else 4 if dx + dy < 2 else 2
            p.px(cx + dx, cy + dy, STEEL[t + k])
    p.px(cx, cy, STEEL[1])


def iron_ring(p: Pix, path, rad, night, rivets=()):
    """A band of the El's painted iron along `path`, lit where it turns to the light, outlined dark, a rivet at each
    point of `rivets`."""
    k = -1 if night else 0

    def colour(s_, o, lam, x, y):
        return IRON[max(1, min(6, round(1.4 + 4.6 * lam) + k))]
    tube(p, path, rad, colour, outline=IRON[0])
    for (x, y) in rivets:
        rivet(p, round(x) - 1, round(y) - 1, night)


def neon_bar(p: Pix, bx, base, bw, v, night):
    """A week's commits as a neon tube stood up on its board from the base line: the dark board, and down its middle
    the tube, pale unlit glass by day, burning the hand's phosphor by night, white-hot at its core."""
    if v <= 0:
        return
    p.rect(bx, base - v, bw, v, BOARD[1] if night else BOARD[3])
    p.hline(bx, bx + bw, base - v, STEEL[4] if not night else STEEL[2])
    cx = bx + bw // 2
    if v > 3 and bw > 3:
        hot, glass = (FLAME[6], FLAME[4]) if night else (TUBE[6], TUBE[3])
        p.vline(cx - 1, base - v + 2, base - 1, glass)
        p.vline(cx, base - v + 2, base - 1, hot)
        if bw > 6:
            p.vline(cx + 1, base - v + 2, base - 1, glass)
        if night and v > 6:
            for yy in range(base - v + 2, base - 1, 2):
                p.apx(cx - 2, yy, FLAME[3], 0.35)
                p.apx(cx + (2 if bw > 6 else 1), yy, FLAME[3], 0.35)


def lantern(p: Pix, x, y, night, big=False, lit=True):
    """A streetlamp's lantern hung by its finial from the girder at (x, y): its iron cap, its glass, burning the hand's
    phosphor by night when `lit`, pale by day, and its iron foot; a `big` one wider, an unlit one only its frame."""
    k = -1 if night else 0
    w = 3 if big else 2
    p.vline(x, y, y + 1, IRON[3 + k])
    p.hline(x - w, x + w + 1, y + 2, IRON[5 + k])
    for j in range(3 + w):
        for dx in range(-w + 1, w):
            if not lit:
                c = None
            elif night:
                c = FLAME[6] if dx < 0 else FLAME[5]
            else:
                c = GLASS[6] if dx < 0 else GLASS[4]
            if c:
                p.px(x + dx, y + 3 + j, c)
        p.px(x - w, y + 3 + j, IRON[4 + k])
        p.px(x + w, y + 3 + j, IRON[1])
    p.hline(x - w, x + w + 1, y + 6 + w, IRON[2 + k])


SENTINEL = [".kkkkk.", "kkRkRkk", "kkkkkkk", ".k.k.k.", "k..k..k", "k..k..k"]


def face(p: Pix, cx, cy, i, person, night):
    """A contributor in the street's people's manner, a portrait fifteen units square centred on (cx, cy): a lit
    window behind them, their hair and their face on one of the hand's skins, dark glasses over their eyes, a dark
    coat at their shoulders and their initials on its collar; a bot is one of the machines, its red eyes burning."""
    k = -1 if night else 0
    x0, y0 = cx - 7, cy - 7
    p.rect(x0, y0, 15, 15, FLAME[1] if night else GLASS[4])
    p.box(x0 - 1, y0 - 1, 17, 17, IRON[1] if not night else STEEL[2])
    if not person.get("initials"):
        sprite(p, x0 + 4, y0 + 4, SENTINEL, {"k": COAT[1], "R": BRICK[5]})
        for j in range(3):
            p.px(x0 + 4 + j * 3, y0 + 11, COAT[1])
        return
    skin = RAMP[("skin0", "skin1", "skin2")[i % 3]]
    hair = (HAIR[1], HAIR[3], RUST[2], HAIR[0])[i % 4]
    for yy in range(y0 + 1, y0 + 9):
        for xx in range(x0 + 4, x0 + 11):
            dx, dy = xx - (x0 + 7), yy - (y0 + 5)
            if dx * dx / 10 + dy * dy / 14 > 1:
                continue
            c = skin[4] if dx < 1 else skin[3]
            if yy <= y0 + 2 or (yy <= y0 + 5 and abs(dx) == 3):
                c = hair
            p.px(xx, yy, c)
    p.hline(x0 + 5, x0 + 10, y0 + 5, COAT[0])
    p.px(x0 + 7, y0 + 5, COAT[2])
    for yy in range(y0 + 9, y0 + 15):
        for xx in range(x0 + max(1, 4 - (yy - y0 - 9)), x0 + min(14, 11 + (yy - y0 - 9))):
            p.px(xx, yy, COAT[2] if xx > x0 + 7 else COAT[4 + k])
    ini = str(person["initials"])[:2]
    p.text(cx - measure(ini, "35") // 2, y0 + 10, ini, TUBE[6], "35")


def neon_fill(p: Pix, x, y, w, fill, night):
    """A contributor's share as a neon tube in its rim: the tube lit along `fill` of its length, burning the hand's
    phosphor by night and pale glass by day, dark glass for the rest."""
    p.box(x, y, w + 2, 4, IRON[1] if not night else STEEL[2])
    hot, glass, dark = (FLAME[6], FLAME[4], BOARD[2]) if night else (BOARD[3], BOARD[2], TUBE[3])
    for xx in range(w):
        lit = xx < fill
        p.px(x + 1 + xx, y + 1, hot if lit else dark)
        p.px(x + 1 + xx, y + 2, glass if lit else dark)


def girder_line(p: Pix, x0, x1, y, night):
    """The El's girder the releases hang from, up to today: three rows of iron, lit along the top, riveted."""
    k = -1 if night else 0
    p.hline(x0, x1, y - 1, IRON[5 + k])
    p.hline(x0, x1, y, IRON[3 + k])
    p.hline(x0, x1, y + 1, IRON[1])
    for xx in range(x0 + 2, x1 - 1, 7):
        p.px(xx, y, IRON[6 + k])


def signal_small(p: Pix, x, y, night):
    """A small traffic signal, five wide and six tall, its top-left at (x, y): its housing of the El's iron on a short
    post below it, its red and amber lamps dark and its green lit, burning the hand's phosphor by night."""
    k = -1 if night else 0
    p.rect(x + 1, y, 3, 5, IRON[1])
    p.vline(x + 1, y, y + 5, IRON[3 + k])
    p.px(x + 2, y + 1, BRICK[1])
    p.px(x + 2, y + 2, RUST[1])
    p.px(x + 2, y + 3, FLAME[6] if night else FLAME[4])
    p.px(x + 2, y + 5, IRON[3 + k])
    if night:
        p.halo(x + 2.5, y + 3.5, 3, 3, FLAME[3], (0.1, 0.2))


def signal_mark(p: Pix, x, y, night):
    """A traffic signal's housing, five wide and eleven tall, its top-left at (x, y), its green lamp lit."""
    k = -1 if night else 0
    p.rect(x, y, 5, 11, IRON[1])
    p.box(x, y, 5, 11, IRON[0])
    p.rect(x + 1, y + 1, 3, 2, BRICK[1])
    p.rect(x + 1, y + 4, 3, 2, RUST[1])
    p.rect(x + 1, y + 7, 3, 2, FLAME[5] if night else FLAME[3])
    p.px(x + 1, y + 7, FLAME[6] if night else FLAME[4])
    p.vline(x + 2, y - 2, y, IRON[3 + k])

