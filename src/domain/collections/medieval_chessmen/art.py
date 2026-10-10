# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chessmen set's scenery and sprites, drawn on the shared pixel canvas.

The polished walrus ivory every footer, element and badge is, with its grain, the craquelure of old ivory and its
honey patina, and the board's edge that frames it, squares of ivory and of bone stained red between carved corner
blocks; the Norse hall every header is, its wall of upright oak planks, its crossbeam and posts, and the woven
hanging behind its words; the band of the board's notation cut along a header's top; titles cut deep and by day
inked dark in the cut; the chessmen themselves, after the pieces of the twelfth century found on the Isle of Lewis
(the king with his sword across his knees, the queen with her hand to her cheek, the bishop with his crozier, the
knight on his stocky pony, the berserker biting his shield and the pawns), in ivory shaded in its honey patina and
in bone stained red, at the board's size, at the size they stand on an H1's table and as the showpieces of a
section and a strip; the game in perspective on its trestle table, its whole board or its near corner, a knight
lifting and making his move and a soapstone lamp at its corner; the hearth of the hall with its fire, the post
carved with a dragon's head and the drinking horn hung from it by its strap, a round shield on the wall, a bench and
the gaming purse of tablemen; by day the shaft of winter light from the smoke hole and its motes, by night the
hearth and the lamp the hall's two lights, which throw the pieces' long shadows across the board and light their
faces from the side; the footer's board edge, its rank with the pieces taken standing on it and the toppled king of
checkmate; and the ivory every element and badge is made of. Everything is shaded from the one light in the upper
left on the set's own ramps by day, and from the hearth and the lamp by night."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import BLINKS, FONTS, Paint, Pix, fold, num
from ..hand import MEDIEVAL
from .palette import C, NIGHT_SKY, RAMP, X, step

IV, HO, RD, OAK = RAMP["ivory"], RAMP["honey"], RAMP["stain"], RAMP["oak"]
HALL, FIRE, SMOKE, STONE = RAMP["hall"], RAMP["fire"], RAMP["smoke"], RAMP["stone"]
IRON, LEATHER, GILT = RAMP["iron"], RAMP["leather"], RAMP["gilt"]


def flip(rows: list) -> list:
    """Pixel art turned to face the other way."""
    return [r[::-1] for r in rows]


def stamp(p: Pix, x, y, rows, pal, L="base", below=None):
    """Pixel art from rows of characters with its top-left at (x, y), each looked up in `pal`; a character the
    palette lacks is left clear, and rows from `below` down are left out."""
    for j, row in enumerate(rows):
        if below is not None and y + j >= below:
            break
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                p.px(x + i, y + j, c, L)


def keep(p: Pix, cells):
    """Remember cells a shape fills without setting them pixel by pixel, so a check that gathers what a scene draws
    finds them as it finds pixels set one by one."""
    if not hasattr(p, "filled"):
        p.filled = set()
    p.filled.update(cells)


def _blocks(rows: dict) -> str:
    """Path data filling the cells {y: [x, ...]} as blocks: each row's runs, a run lying the same in the rows under
    it one block with them, every move after the first relative to the last block's corner."""
    blocks, last = [], {}
    for y in sorted(rows):
        xs = sorted(set(rows[y]))
        runs, start = [], xs[0]
        for a, b in zip(xs, xs[1:] + [None]):
            if b != a + 1:
                runs.append((start, a - start + 1))
                start = b
        now = {}
        for run in runs:
            block = last.get(run)
            if block is not None and block[1] + block[3] == y:
                block[3] += 1
            else:
                block = [run[0], y, run[1], 1]
                blocks.append(block)
            now[run] = block
        last = now
    out, at = [], None
    for x, y, w, h in sorted(blocks, key=lambda b: (b[1], b[0])):
        out.append((f"M{x} {y}" if at is None else f"m{x - at[0]} {y - at[1]}") + f"h{w}v{h}h-{w}z")
        at = (x, y)
    return "".join(out).replace(" -", "-")


def paths(cells: dict) -> str:
    """Paths for {(x, y): colour or colour:alpha}: each colour's cells as strokes along their rows, or as filled
    blocks where its rows repeat enough to make that shorter."""
    by: dict = {}
    for (x, y), c in cells.items():
        by.setdefault(c, {}).setdefault(y, []).append(x)
    out = []
    for c, rows in sorted(by.items()):
        col, a = c.split(":") if ":" in c else (c, None)
        strokes, blocks = Pix._d(rows), _blocks(rows)
        if len(blocks) + 2 < len(strokes):
            out.append(f'<path fill="{col}"' + (f' fill-opacity="{a}"' if a else "") + f' d="{blocks}"/>')
        else:
            out.append(f'<path stroke="{col}"' + (f' stroke-opacity="{a}"' if a else "") + f' d="{strokes}"/>')
    return "".join(out)


def fill(p: Pix, pid: str, x, y, w, h, L="base"):
    """A block laid in a pattern, its cells kept as a sprite's."""
    if w <= 0 or h <= 0:
        return
    p.shapes[L].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')
    keep(p, {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)})


# --------------------------------------------------------------------------- the paper
TILE_W, TILE_H = 168, 96


def _ivory(uid: str, night: bool, lite: bool) -> str:
    """A pattern tile of polished walrus ivory, 168 by 96: the long grain of the tusk in fine streaks a shade under
    and a shade over the polish, wavering a little as they run; the craquelure of old ivory, hairline cracks along
    the grain that branch here and there; and by day a little honey patina in soft clouds where the ivory has
    yellowed. By night the same grain in the dark. Drawn lighter, the patina and half the grain go, the cracks stay."""
    rnd = random.Random(61)
    cells = {}
    dark, light, crack = (HALL[3], HALL[0], HALL[4]) if night else (X["grain"], X["sheen"], X["crack"])
    for i in range(22):
        y, x, n = rnd.randrange(TILE_H), rnd.randrange(TILE_W), rnd.randint(24, 110)
        if lite and (i % 2 or night):
            continue
        c = dark if i % 3 else light
        for k in range(n):
            if rnd.random() < 0.03:
                y += rnd.choice((-1, 1))
            if rnd.random() < 0.9:
                cells[((x + k) % TILE_W, y % TILE_H)] = c
    for _ in range(5):
        x, y, n = rnd.randrange(TILE_W), rnd.randrange(TILE_H), rnd.randint(10, 26)
        for k in range(n):
            cells[((x + k) % TILE_W, y % TILE_H)] = crack
            if rnd.random() < 0.18:
                y += rnd.choice((-1, 1))
            if rnd.random() < 0.08:
                bx, by = x + k, y
                for _ in range(rnd.randint(2, 4)):
                    by += 1
                    bx += rnd.choice((0, 1))
                    cells[(bx % TILE_W, by % TILE_H)] = crack
    shapes = []
    if not night and not lite:
        for _ in range(4):
            cx, cy = rnd.uniform(0, TILE_W), rnd.uniform(0, TILE_H)
            rx, ry = rnd.uniform(18, 34), rnd.uniform(7, 13)
            for dx in (-TILE_W, 0, TILE_W):
                for dy in (-TILE_H, 0, TILE_H):
                    if -rx < cx + dx < TILE_W + rx and -ry < cy + dy < TILE_H + ry:
                        shapes.append(f'<ellipse cx="{num(cx + dx)}" cy="{num(cy + dy)}" rx="{num(rx)}" '
                                      f'ry="{num(ry)}" fill="url(#{uid}h)"/>')
    honey = (f'<pattern id="{uid}h" width="3" height="3" patternUnits="userSpaceOnUse">'
             f'<path stroke="{HO[6]}" stroke-opacity=".5" d="M0 .5h2m-1 1h2m-3 1h1"/></pattern>') if shapes else ""
    return (f'{honey}<pattern id="{uid}w" width="{TILE_W}" height="{TILE_H}" patternUnits="userSpaceOnUse">'
            f'{"".join(shapes)}{paths(cells)}</pattern>')


def band_edges(h: int) -> list:
    """The rows the night's bands of the hall change at, down a sheet `h` tall."""
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p", hall=False):
    """The ground a drawing sits on: a panel of polished walrus ivory, warm cream by day with its grain, its
    craquelure and a little honey patina; by night the same ivory in a dark hall, warmed from the side the hearth
    burns on and falling to deep brown-black at the far side (see `hearthlight`). Under a header's `hall` the ivory
    is plain, the figures' floor, the wall of planks laid over the rest (see `hall_wall`). The drawing keeps which
    sheet it is (`uid`) and whether it is night, for the hooks the layout calls without saying."""
    p.sheet, p.night = uid, night
    if hall:
        p.hall = p.h
    if not night:
        p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="{C["paper"]}"/>')
    elif hall:
        p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="{NIGHT_SKY[-1]}"/>')
    else:
        edges = band_edges(p.h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                p.under.append(f'<rect y="{edges[i]}" width="{p.w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    if not hall:
        p.defs.append(_ivory(uid, night, p.lite))
        p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="url(#{uid}w)"/>')
    if night:
        hearthlight(p)


# --------------------------------------------------------------------------- the hall's timber
WALL, WOOL = RAMP["wall"], RAMP["wool"]
PLANKS = (14, 13, 15, 14, 13, 15)       # the widths of the planks across a tile of the wall
WALL_W, WALL_H = sum(PLANKS), 96
BEAM = 13           # the crossbeam's top row, just under the band


def _planks(uid: str, night: bool, lite: bool) -> str:
    """A tile of the hall's wall, WALL_W by WALL_H: upright planks of oak side by side, each lit along its left edge
    and dark in the seam at its right, a butt joint across each at its own height, and the grain running up it in
    streaks a tone under its face. By day the oak is weathered pale; by night it lies in the dark of the hall.
    Drawn lighter, the grain goes; the planks and their seams stay."""
    rnd = random.Random(23)
    tones = OAK if night else WALL
    faces = (1, 2, 1, 2, 2, 1) if night else (4, 5, 4, 3, 5, 4)
    rects, cells = [], {}
    x = 0
    for i, w in enumerate(PLANKS):
        f = faces[i]
        rects.append(f'<rect x="{x}" width="{w}" height="{WALL_H}" fill="{tones[f]}"/>')
        hi, lo = tones[min(6, f + 1)], tones[max(0, f - 2)]
        for y in range(WALL_H):
            cells[(x, y)] = hi
            cells[(x + w - 1, y)] = lo
        j = rnd.randrange(10, WALL_H - 10)
        for xx in range(x + 1, x + w - 1):
            cells[(xx, j)] = lo
            cells[(xx, j + 1)] = hi
        for _ in range(3):
            gx, y0, n = rnd.randrange(x + 2, x + w - 2), rnd.randrange(WALL_H), rnd.randint(20, 60)
            for k in range(n):
                if rnd.random() < 0.08:
                    gx = min(x + w - 3, max(x + 2, gx + rnd.choice((-1, 1))))
                if not lite:
                    cells.setdefault((gx, (y0 + k) % WALL_H), tones[max(0, f - 1)])
        x += w
    return (f'<pattern id="{uid}k" width="{WALL_W}" height="{WALL_H}" patternUnits="userSpaceOnUse">'
            f'{"".join(rects)}{paths(cells)}</pattern>')


def hall_wall(p: Pix, night: bool, floor: int, uid="p"):
    """A header's ground: the hall's wall of planks from the band down to the floor at row `floor`, over the ivory
    that stays under the figures; the drawing keeps the floor's row, for the hanging and the colour behind a row."""
    p.defs.append(_planks(uid, night, p.lite))
    p.under.append(f'<rect width="{p.w}" height="{floor + 1}" fill="url(#{uid}k)"/>')
    p.hall = floor


def crossbeam(p: Pix, night: bool):
    """The hall's crossbeam of oak along the wall just under the band, lit along its top, pegged, and its shadow
    falling on the planks under it; a drawing made lighter leaves out its pegs and the shadow's faint outer row."""
    k = -1 if night else 0
    y = BEAM
    for x in range(EDGE, p.w - EDGE):
        for j, c in enumerate((OAK[0], OAK[6 + k], OAK[5 + k], OAK[3 + k], OAK[0])):
            p.px(x, y + j, c)
        p.apx(x, y + 5, X["shade_ink"], 0.35)
        if not p.lite:
            p.apx(x, y + 6, X["shade_ink"], 0.15)
    if not p.lite:
        for x in range(20, p.w - 20, 46):
            p.px(x, y + 2, OAK[1])
            p.px(x + 1, y + 2, OAK[6 + k])


HANG = BEAM + 5     # the row the hanging hangs from
HANG_W = 150        # the narrowest a hanging is woven, however few its words


def _weave(uid: str, night: bool, lite: bool = False) -> str:
    """The patterns a hanging is woven in: its field a diamond twill of the natural wool, two tones a step apart
    (plain on a drawing made lighter), and its border a tablet-woven band of madder red with lozenges of woad blue
    and weld yellow, along (b) and down (v). By night the wool is the dark of the hall and the dyes a step or two
    into it."""
    W = HALL if night else WOOL
    lo, hi = (W[3], W[4]) if night else (W[4], W[5])
    k = -2 if night else 0
    red, red2, blue, yellow = RD[max(0, 2 + k)], RD[max(0, 3 + k)], RAMP["woad"][max(0, 3 + k)], RAMP["weld"][5 + k]
    twill = {(x, y): lo for y in range(6) for x in range(6) if ((x + y) % 6 == 0 or (x - y) % 6 == 0) and not lite}
    along, down = {}, {}
    for j in range(5):
        for i in range(8):
            m = (i + j) % 8
            c = red if j in (0, 4) else blue if m in (0, 4) else yellow if m in (2, 6) else red2
            along[(i, j)] = c
            down[(j, i)] = c
    return (f'<pattern id="{uid}t" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" '
            f'fill="{hi}"/>{paths(twill)}</pattern>'
            f'<pattern id="{uid}b" width="8" height="5" patternUnits="userSpaceOnUse">{paths(along)}</pattern>'
            f'<pattern id="{uid}v" width="5" height="8" patternUnits="userSpaceOnUse">{paths(down)}</pattern>')


def hanging(p: Pix, night: bool):
    """The woven hanging behind a header's words, hung from the crossbeam: wide and deep enough to lie behind every
    word over the floor with a little to spare, its field a calm twill of natural wool for the words to sit on, its
    border a tablet-woven band along its top and down its sides, its foot hemmed in red with a fringe of loose
    threads. It hangs on the wall behind everything, the scenes standing before it."""
    floor = getattr(p, "hall", None)
    words = [b for b in p.words if b[1] > BAND_FOOT and floor is not None and b[3] < floor]
    if not words:
        return
    x0 = max(EDGE + 1, min(b[0] for b in words) - 6)
    x1 = min(p.w - EDGE - 1, max(b[2] for b in words) + 6)
    y1 = min(floor, max(max(b[3] for b in words) + 3, HANG + 44))
    if x1 - x0 < HANG_W:
        mid = (x0 + x1) // 2
        x0 = max(EDGE + 1, min(mid - HANG_W // 2, p.w - EDGE - 1 - HANG_W))
        x1 = x0 + HANG_W
    uid = "hw"
    p.defs.append(_weave(uid, night, p.lite))
    L = p.layer("hang", z=-22)
    sh = p.shapes[L]
    sh.append(f'<rect x="{x0}" y="{HANG}" width="{x1 - x0}" height="{y1 - HANG}" fill="url(#{uid}t)"/>')
    sh.append(f'<rect x="{x0}" y="{HANG}" width="{x1 - x0}" height="5" fill="url(#{uid}b)"/>')
    for x in (x0, x1 - 5):
        if p.clear_of_words(x - 1, HANG + 5, x + 6, y1):
            sh.append(f'<rect x="{x}" y="{HANG + 5}" width="5" height="{y1 - HANG - 5}" fill="url(#{uid}v)"/>')
    k = -2 if night else 0
    W = HALL if night else WOOL
    sh.append(f'<rect x="{x0}" y="{y1}" width="{x1 - x0}" height="1" fill="{RD[max(0, 2 + k)]}"/>')
    sh.append(f'<rect x="{x0 + 1}" y="{y1 + 1}" width="{x1 - x0 - 2}" height="2" fill="url(#{uid}f)"/>')
    p.defs.append(f'<pattern id="{uid}f" width="2" height="2" patternUnits="userSpaceOnUse"><rect width="1" '
                  f'height="2" fill="{W[4] if night else W[2]}"/></pattern>')
    p.hanging = (x0, HANG, x1, y1)


def wall_posts(p: Pix, night: bool):
    """The hall's posts at a header's two ends, carrying the crossbeam down to the floor behind everything drawn
    before them, each from the first row clear of the words beside it (on a phone the words may run to its edges)."""
    floor = getattr(p, "hall", None)
    if floor is None:
        return
    base = p.layers["base"]
    for x in (EDGE + 2, p.w - EDGE - 8):
        if (x + 2, floor - 12) in base and (x + 3, floor - 30) in base:
            continue
        y0 = HANG
        while y0 < floor - 20 and not p.clear_of_words(x - 2, y0 - 2, x + 8, floor):
            y0 += 1
        if y0 < floor - 20:
            post(p, x, y0, floor + 1, night, L=p.layer("far"))


# The hearth's warmth on the ivory by night, ring by ring to its heart, from the sheet's left edge: with the
# darkest band of the night under it, it leaves every word its contrast.
HEARTH_WASH = (0.04, 0.08, 0.13)


def glow(p: Pix, cx, cy, rx, ry, col, alphas, L="haze"):
    """A stepped glow of `col` about (cx, cy), its rings `alphas` from the outermost in; on a drawing made lighter
    its outer ring is left off, the inner rings as they were."""
    if p.lite and len(alphas) > 2:
        n = len(alphas)
        rx, ry, alphas = rx * (n - 1) / n, ry * (n - 1) / n, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, L=L, shape=True)


def hearthlight(p: Pix):
    """By night the hearth's warmth on the ivory from the side it burns on, the left: a broad glow strongest at the
    left edge low down, falling away across the sheet to the dark at its far side."""
    w, h = p.w, p.h
    glow(p, -w * 0.08, h * 0.72, w * (0.55 if getattr(p, "hall", None) is not None else 0.78), max(h * 1.25, 60),
         FIRE[2], HEARTH_WASH)


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: on a header, where the hanging hangs, the tone of its twill the words keep the
    least contrast with; else the ivory, or the night's band of the hall there."""
    hang = getattr(p, "hanging", None)
    if hang and hang[1] <= y <= hang[3]:
        return HALL[4] if night else WOOL[4]
    if not night:
        return C["paper"]
    if getattr(p, "hall", None) is not None:
        return NIGHT_SKY[-1]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


# --------------------------------------------------------------------------- the frame: the board's edge
EDGE = 4            # the border's width: one square of the board's edge
BLOCK = 8           # a carved corner block's side


def _chequer(pid: str, night: bool) -> str:
    """The board's edge as a pattern tile two squares each way: squares of ivory and of bone stained red by turns,
    each a small inlay lit along its top and left and shaded along its foot and right."""
    k = -1 if night else 0
    cells = {}
    for y in range(8):
        for x in range(8):
            red = ((x // EDGE) + (y // EDGE)) % 2 == 1
            u, v = x % EDGE, y % EDGE
            R, t = (RD, (5, 3, 1)) if red else (IV, (6, 5, 3))
            tone = t[0] if (u == 0 or v == 0) else t[2] if (u == EDGE - 1 or v == EDGE - 1) else t[1]
            cells[(x, y)] = R[max(0, tone + k)]
    return f'<pattern id="{pid}" width="8" height="8" patternUnits="userSpaceOnUse">{paths(cells)}</pattern>'


# A carved corner block, 8 by 8: its edge lit and shaded, and a ring and dot cut in it, the mark the Norse carvers
# cut in bone and ivory. K the cut, 6 5 4 3 2 the ivory light to dark.
CORNER = [
    "KKKKKKKK",
    "K666665K",
    "K65KK43K",
    "K6K54K3K",
    "K6K4KK3K",
    "K54KK32K",
    "K543322K",
    "KKKKKKKK",
]
# The ends of a header's notation band, 8 by 13: the same block run down the band's height, a ring and dot over a
# lozenge cut under it.
BAND_END = [
    "KKKKKKKK",
    "K666665K",
    "K65KK43K",
    "K6K54K3K",
    "K6K4KK3K",
    "K54KK32K",
    "K654433K",
    "K65K443K",
    "K6K5K43K",
    "K65K432K",
    "K543322K",
    "K433222K",
    "KKKKKKKK",
]


def block(p: Pix, x, y, rows, night: bool, L="base"):
    """A carved block of ivory with its top-left at (x, y), drawn once a file and placed."""
    k = -1 if night else 0
    key = ("block", tuple(rows), night)
    if key not in p.syms:
        pal = {"K": IV[0], **{str(t): IV[max(0, t + k)] for t in range(1, 7)}}
        p.symbol(key, {(i, j): pal[ch] for j, r in enumerate(rows) for i, ch in enumerate(r) if ch in pal})
    p.use(key, x, y, L)
    keep(p, {(x + i, y + j) for j, r in enumerate(rows) for i, _ in enumerate(r)})


def frame(p: Pix, night: bool, header: bool = False, footer: bool = False, uid="fr"):
    """The sheet's border: the board's edge, squares of ivory and of bone stained red by turns down each side and
    along the foot (and along the top of any sheet but a header, whose notation band runs there), with a carved
    block at each corner, and the edge's shadow on the ivory inside it. Each run of squares is one pattern."""
    w, h = p.w, p.h
    p.defs.append(_chequer(uid + "c", night))
    top = 0 if not header else 12
    rects = [(0, top, EDGE, h - top), (w - EDGE, top, EDGE, h - top)]
    if not footer:
        rects.append((EDGE, h - EDGE, w - 2 * EDGE, EDGE))
    if not header:
        rects.append((EDGE, 0, w - 2 * EDGE, EDGE))
    for (x, y, rw, rh) in rects:
        p.shapes["base"].append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="url(#{uid}c)"/>')
        keep(p, {(xx, yy) for xx in range(x, x + rw) for yy in range(y, y + rh)})
    for y in range(top + (0 if header else EDGE), h - EDGE):
        p.apx(EDGE, y, X["shade_ink"], 0.18, "base")
    if not header:
        for x in range(EDGE + 1, w - EDGE):
            p.apx(x, EDGE, X["shade_ink"], 0.18, "base")
    corners = [(0, h - BLOCK), (w - BLOCK, h - BLOCK)] + ([] if header else [(0, 0), (w - BLOCK, 0)])
    for (x, y) in corners:
        block(p, x, y, CORNER, night)


# --------------------------------------------------------------------------- the notation band
BAND_FOOT = 12      # the band's last row: a title's carving keeps two clear of it
PAIRS = ("a1", "b2", "c3", "d4", "e5", "f6", "g7", "h8")


def _carve(p: Pix, s: str, x, y, colour: str, font="57"):
    """`s` raised at (x, y) in `colour`, each letter the font's glyph drawn once a file and placed, as a carving
    rather than words: nothing here is registered as text."""
    glyphs, _, space = FONTS[font]
    cx = x
    for ch in fold(s, font):
        if ch == " ":
            cx += space + 1
            continue
        g = glyphs[ch]
        key = ("glyph", font, ch)
        if key not in p.syms:
            p.symbol(key, {(c, r): 1 for r, cols in enumerate(g[1]) for c in cols}, mono=True)
        p.use(key, cx, y, "base", stroke=colour)
        keep(p, {(cx + c, y + r) for r, cols in enumerate(g[1]) for c in cols})
        cx += g[0] + 1


def runs(x0, x1, w) -> list:
    """The runs the squares' names are carved in along a band from column x0 to x1 of a header `w` wide, each
    (from, to, names): one run from end to end where every name keeps two units clear of the box the hand's month
    mark takes at the top centre, as on a wide header; else, as on a phone, where the band is short, two runs of four
    as long as each other, a1 to d4 and e5 to h8, parting either side of that box and two units clear of it, so the
    mark never cuts a name, whether it is drawn or not."""
    n = MEDIEVAL.mark_size
    m0 = w // 2 - n // 2 - 2
    m1 = m0 + n + 4
    whole = (x0 + BLOCK, x1 - BLOCK, PAIRS)
    if all(b <= m0 or a >= m1 for a, b in carved(*whole)[0]):
        return [whole]
    half, run = len(PAIRS) // 2, min(m0 - x0 - BLOCK, x1 - BLOCK - m1)
    return [(m0 - run, m0, PAIRS[:half]), (m1, m1 + run, PAIRS[half:])]


def carved(a, b, names) -> tuple:
    """Where the names `names` are carved from column a to b: the span (from, to) of each one's cartouche, and the
    first column of each groove cut between them, a groove being a cut and the lit edge right of it. The names stand
    evenly spaced with two grooves at each boundary between them where that leaves them room; where it does not, they
    stand packed four columns apart, centred between a and b, one groove in each gap."""
    cell = (b - a) / len(names)
    even, grooves = [], []
    for i, s in enumerate(names):
        sw = Pix.measure(s)
        cx = round(a + cell * (i + 0.5))
        even.append((cx - sw // 2 - 2, cx - sw // 2 + sw + 2))
    if all(s0 - e >= 7 for (_, e), (s0, _) in zip(even, even[1:])):
        for i in range(len(names) - 1):
            lx = round(a + cell * (i + 1))
            grooves += [lx - 2, lx + 1]
        return even, grooves
    widths = [Pix.measure(s) + 4 for s in names]
    x = a + (b - a - sum(widths) - 4 * (len(names) - 1)) // 2
    packed = []
    for i, wd in enumerate(widths):
        packed.append((x, x + wd))
        if i < len(widths) - 1:
            grooves.append(x + wd + 1)
        x += wd + 4
    return packed, grooves


def notation(p: Pix, x0, x1, night: bool, motion: bool = False):
    """The band along a header's top: a moulding of ivory lit along its upper edge and shaded along its lower, cut
    with the board's long diagonal in its notation, a1 to h8, each square's name raised in a sunken cartouche whose
    hollow has yellowed with age, two grooves cut across the band between each two, or one where the names stand
    close (see `carved`); a carved block at each end. On a phone the names run in two halves either side of the top
    centre, which is kept for the hand's month mark (see `runs`). In a wide moving header a glint of light runs slowly
    along the carving and rests, passing on the hand's period."""
    k = -1 if night else 0
    w = p.w
    top, foot = 0, BAND_FOOT - 1
    rows = [(top, 1, IV[0]), (top + 1, 1, IV[6 + k]), (top + 2, foot - top - 3, IV[5 + k]), (foot - 1, 1, IV[3 + k]),
            (foot, 1, IV[1])]
    band = p.layer("band", z=-0.5)
    p.shapes[band].append("".join(f'<rect y="{y}" width="{w}" height="{n}" fill="{c}"/>' for y, n, c in rows)
                          + f'<rect y="{foot + 1}" width="{w}" height="1" fill="{X["shade_ink"]}" fill-opacity=".22"/>')
    keep(p, {(x, y) for x in range(w) for y in range(top, foot + 2)})
    hollow, deep, lit = (HO[3 + k], HO[2 + k], IV[6 + k]) if not night else (OAK[2], OAK[1], IV[4])
    for a, b, names in runs(x0, x1, w):
        boxes, grooves = carved(a, b, names)
        for (bx0, bx1), s in zip(boxes, names):
            for y in range(top + 2, foot - 1):
                for x in range(bx0, bx1):
                    corner = (x in (bx0, bx1 - 1)) and (y in (top + 2, foot - 2))
                    if corner:
                        continue
                    p.px(x, y, deep if (x == bx0 or y == top + 2) else hollow)
            _carve(p, s, bx0 + 2, top + 3, lit)
        for gx in grooves:
            for y in range(top + 3, foot - 2):
                p.px(gx, y, IV[1])
                p.px(gx + 1, y, IV[6 + k])
    block(p, 0, top, BAND_END, night)
    block(p, w - BLOCK, top, BAND_END, night)
    if motion:
        glint(p, top + 1, foot, night)


def glint(p: Pix, y0, y1, night: bool):
    """A glint of light running slowly along the carved band: a slanted window that sweeps from end to end, rests
    and comes round, through which the band shows lit."""
    h = y1 - y0
    cid = f"bg{len(p.raws)}"
    w = p.w
    band = 7
    poly = f"0 {y1} {band} {y1} {band + h} {y0} {h} {y0}"
    sheen = X["glint"] if not night else FIRE[5]
    moving = (f'<clipPath id="{cid}"><polygon points="{poly}"><animateTransform attributeName="transform" '
              f'type="translate" values="{-band - h} 0;{w} 0;{w} 0" keyTimes="0;.55;1" dur="{num(MEDIEVAL.glint)}s" '
              f'repeatCount="indefinite"/></polygon></clipPath><g clip-path="url(#{cid})"><rect y="{y0}" '
              f'width="{w}" height="{h}" fill="{sheen}" fill-opacity="{".45" if not night else ".3"}"/></g>')
    p.raw(0.4, moving, "")


# --------------------------------------------------------------------------- the carved title
def _face_fill(r, c, scale, night):
    """A carved letter's face. By day the cut filled with a dark stain, as an inscription incised in ivory is inked:
    the honey brown of the stain toward its top, deepening to the dark of old oak at its foot. By night the letter's
    face of polished ivory dim in the dark hall, a little warmer toward its foot."""
    band = min(6, r // scale)
    if night:
        return (IV[5], IV[4], IV[4], IV[4], IV[3], IV[3], IV[3])[band]
    return (HO[1], HO[1], HO[0], HO[0], OAK[1], OAK[1], OAK[1])[band]


FACE = Paint("ivory", _face_fill)
AROUND = tuple((dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy)


def _shifted(tid: str, offsets) -> str:
    """The group `tid` placed again at each of `offsets`."""
    return "".join(f'<use href="#{tid}"' + (f' x="{dx}"' if dx else "") + (f' y="{dy}"' if dy else "") + "/>"
                   for dx, dy in offsets)


def carved_title(p: Pix, x, y, s, night: bool, scale: int) -> int:
    """A title cut deep in the ivory. By day each letter is an incision filled with a dark stain, as the carvers
    inked an inscription in ivory and bone, heavy and solid: a thin hollow yellowed with age round it, and along its
    lower right edge the ivory's polished lip catching the light. By night the letters stand raised with faces of
    polished cream dim in the dark hall, the ivory cut away round them into a dark hollow, their cut walls falling in
    shadow below and to the right of every stroke, and the hearth, on the left, lighting the left edge of every
    stroke orange, which a drawing made lighter leaves out. The line's letters are set once as a group, and the
    hollow, the walls, the face and the lit edges each place that group again, so a long title costs little more
    than its letters; the hollow's outer ring is placed only where the cut is deep enough to show it. Returns the
    width."""
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
    if not placed:
        return max(0, w)
    letters = []
    for ch, gx in placed:
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        letters.append(f'<use href="#{p.syms[key]}" x="{num((gx - x) / scale)}"/>')
    tid = f"ct{len(p.defs)}"
    p.defs.append(f'<g id="{tid}" transform="translate({x} {y}) scale({scale})">{"".join(letters)}</g>')
    deep = 2 if scale >= 3 else 1
    wall = max(1, scale // 2)
    if not night:
        body = [f'<g stroke="{HO[5]}">{_shifted(tid, AROUND)}</g>'] if scale >= 2 else []
        body.append(f'<g stroke="{X["glint"]}">{_shifted(tid, [(1, 1), (1, 0), (0, 1)])}</g>')
    else:
        # The hollow's outer ring, where the cut is deep enough to show one beyond the ring AROUND the letters.
        rings = [(dx, dy) for dy in range(-deep, deep + 1) for dx in range(-deep, deep + 1)
                 if max(abs(dx), abs(dy)) == deep and (dx, dy) != (-deep, -deep)] if deep > 1 else []
        walls = [(d, d) for d in range(1, wall + 1)] + [(wall, 0), (0, wall)]
        body = [f'<g stroke="{OAK[2]}">{_shifted(tid, rings)}</g>'] if rings else []
        body += [f'<g stroke="{OAK[1]}">{_shifted(tid, AROUND)}</g>',
                 f'<g stroke="{HALL[0]}">{_shifted(tid, walls)}</g>']
        if not p.lite:
            body.append(f'<use href="#{tid}" x="-1" stroke="{X["ember"]}"/>')
    body.append(f'<use href="#{tid}" stroke="url(#{p._pattern(FACE, scale, night)})"/>')
    group = "".join(body)
    p.raw(0.1, group, group)
    rows = max(len(glyphs[ch][1]) for ch, _ in placed)
    p.words.append((x - deep - 1, y - deep - 1, x + w + deep + wall + 1, y + rows * scale + deep + wall + 1))
    return w


# --------------------------------------------------------------------------- the chessmen
# The pieces at the size they stand on the board, after the Lewis chessmen, facing us: K the deep cut round and
# through them, 1 to 6 the ivory (or the red bone) from its darkest hollow to its brightest polish, e an eye.
# The king seated on his throne, its back framing him with the dark of its recess, crowned, his hair to his
# shoulders, a beard, and his sword across his knees, its hilt in his right hand.
KING = [
    ".....K.K.K.....",
    "....K6K6K5K....",
    "....K66654K....",
    "..KKK5K5K4KKK..",
    ".K51244433213K.",
    "K51125e6e42113K",
    "K5112554542113K",
    "K5112422232113K",
    "K5113565542113K",
    "K5112K554K2113K",
    "K5555K454K3323K",
    "K55544KKK43323K",
    "K55K5444433K23K",
    "K65666666666K3K",
    "K33422222222K3K",
    "K4K544443332K2K",
    "K4K545444332K2K",
    "K3K454434322K2K",
    "K3K454334322K2K",
    "K3KK54KK43KKK1K",
    "K6555544443332K",
    "K4333332222211K",
    ".KKKKKKKKKKKKK.",
]
# The queen on her throne, crowned over her veil, her right hand raised to her cheek and her left across her body.
QUEEN = [
    ".....K.K.K.....",
    "....K6K6K5K....",
    "....K66654K....",
    "..KKK44443KKK..",
    ".K1K56555443K1K",
    "K51K55e5e432K3K",
    "K5K6K55554432K3",
    "K5K66K54443K2K3",
    "K5K66K5333K32K3",
    "K5K56KK544K322K",
    "K5K456K4443K32K",
    "K5K456K44433K3K",
    "K5K4456K4433K3K",
    "K5K45666664K33K",
    "K4K5KKKKKKK332K",
    "K4K545443433K2K",
    "K3K545343432K2K",
    "K3K454343432K2K",
    "K3K454343322K2K",
    "K3KK54KK43KKK1K",
    "K6555544443332K",
    "K4333332222211K",
    ".KKKKKKKKKKKKK.",
]
# A bishop standing in his mitre and chasuble, his right hand raised in blessing, his crozier in his left.
BISHOP = [
    ".....K....KKKK.",
    "....K6K..K6554K",
    "...K665K.K5KK4K",
    "...K6K54K.K.K5K",
    "..K65K543K..K4K",
    "..K5K5K43K..K4K",
    "..KKKKKKKK..K4K",
    "..K5e5e43K..K4K",
    "..K555443K..K4K",
    "...K5443KK.KK4K",
    "..K65K43K5KK54K",
    ".K665K43K54K4K.",
    ".K6K55K3K544K..",
    ".K5K545K43K4K..",
    "K55K5443K43K4K.",
    "K54554443432K..",
    "K54554443332K..",
    "K45544433322K..",
    "K45544433222K..",
    "K44444333222K..",
    ".KK5K4KK3KKK...",
    "K66555444433K..",
    ".KKKKKKKKKKK...",
]
# A knight on his stocky pony riding right: his conical helm with its nasal, his kite shield on his left side
# toward us, his spear upright behind it, the pony's head with its eye, its short legs.
KNIGHT = [
    "......K....K......",
    ".....K6K...6......",
    "....K665K..6......",
    "....K6554K.5......",
    "...KKKKKKKK5......",
    "....Ke6e4K.5.KK...",
    "....K554K..4K55K..",
    "..K6666665KK4K5e4K",
    "..K655554K5K55443K",
    "..K655444K4K54433K",
    "..K654443K55443K2K",
    "..K544433K544332K.",
    ".KKK54433K4433KK..",
    "K554K543K44332K...",
    "K4544K4K443322K...",
    "K44334K4333222K...",
    "K3332222222211K...",
    ".KK4KK2K..K2KK4K..",
    "..K4KK2K..K2KK4K..",
    "..K5KK3K..K3KK5K..",
    "K665555544443332K.",
    ".KKKKKKKKKKKKKKK..",
]
# A berserker, a warder of the board, in his conical helm with his eyes starting, biting the rim of the kite shield
# held up before him, his sword upright in his right hand.
BERSERKER = [
    "K.....KK.....",
    "6K...K65K....",
    "5K..K6554K...",
    "5K..K5544K...",
    "5K.KKKKKKKK..",
    "5K.K6eK6eK3K.",
    "5K.K55543432K",
    "5KK6K66666K3K",
    "5K5K6K6K6K6K.",
    "5K5K66655443K",
    "KKK5K6555443K",
    "K66K5K555433K",
    ".KK5K6544433K",
    "..K5K6554433K",
    "..K5KK654433K",
    "..K4K.K54332K",
    "..K4K..K433K.",
    "..K4K...K3K..",
    "..K4K....K...",
    "..KK5KK.K3K..",
    "..K54K..K43K.",
    "K66555544433K",
    ".KKKKKKKKKKK.",
]
# A pawn: a small stele with a rounded head and a cut band, on its plinth.
PAWN = [
    "..KKKKK..",
    ".K66654K.",
    "K6655543K",
    "K6554433K",
    "KKKKKKKKK",
    ".K65433K.",
    ".K65433K.",
    ".K65432K.",
    ".K54432K.",
    ".K54332K.",
    "K6554432K",
    "K5444332K",
    ".KKKKKKK.",
]
# The pieces at their full size, for a section's header and a strip's. The king on his throne, its back cut in a
# lattice and its sides in arches, crowned, his eyes staring, his beard falling in strands, his hands on the hilt and
# the blade of the sword across his knees, his robe falling in folds to his feet.
KING_L = [
    ".............K...K...K............",
    "............K6K.K6K.K5K...........",
    "...........K665K665K554K..........",
    "..........K6666666555543K.........",
    "..........K6K66K55K54K43K.........",
    "..........KKKKKKKKKKKKKKK.........",
    "..........K45666666654K...........",
    "...KKKKKKK4K5666666654K3KKKKKKK...",
    "..K55555554K4322663324K33333333K..",
    ".K5555555543K5KK66KK4K3233333333K.",
    ".K55K2222243K56e66e64K3222222K22K.",
    ".K55K2444443K5666555K43222222K22K.",
    ".K55K4244443K56665555K3212221K22K.",
    ".K55K4424243K5K55554K43221212K22K.",
    ".K55K4442443K5532233K43222122K22K.",
    ".K55K442424K6656555654K321212K22K.",
    ".K55K4244443K56565654K3212221K22K.",
    ".K55K2444443K65656565K3222222K22K.",
    ".K5KKKK4KKK3K56565654K2KKKKKKK22K.",
    ".K5K665K6653KK656565KK23K4433K22K.",
    ".K5K6654K553K5K5656K4K23K44332K2K.",
    ".K5K6654K55K555K55K44K33K44332K2K.",
    ".K5K6654K5555554KK444333K44332K2K.",
    ".K5K6654K5555544K44443333K4332K2K.",
    ".K55K654K555554K444443332K4332K2K.",
    ".K55K654K555554K444433332K4332K2K.",
    "KKKKK654K55554K4444433332K4432KKKK",
    "K54KK654K55554K4444333332K4432K32K",
    "K54K66654K554K4444433332K44433K32K",
    "K54K665554K54K4444333332K5544KK32K",
    "K5KK6K5K4KKKKKKKKKKKKKKKK4K4KK332K",
    "K5KK66554K66666666666666KK55K5K32K",
    "K5K5KKKKK5555555555555555KKK4KK32K",
    "K54KKKKK5KKKKKKKKKKKKKKKKKKKK3K32K",
    "K54K44KKK54444K44333K333322K33K32K",
    "K54K44KK554444K44333K333222K33K32K",
    "K54K44KK55444K544333K332222K33K32K",
    "K54K44KK55444K544333K332222K33K32K",
    "K54K44KK5544K5444333K322222K33K32K",
    "K54K44KK5544K5444333K322222K33K32K",
    "K54K44KKK544K54443332KK222KK33K32K",
    "K54444K4K5544KK4433KK2K22K2K33332K",
    "K54444K4K5544K4K433K22K22K2K33332K",
    "KKKKKKK2KKKKKK4KKKKK21KKKK2KKKKKKK",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
    "K66666666666666666666655555555555K",
    "K44444444444444444444444443333333K",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
]
# The queen on her throne, crowned over her veil, her right hand cupped to her cheek and her left arm across her
# body under its elbow, her robe pleated.
QUEEN_L = [
    "...........K...K...K..........",
    "..........K6K.K6K.K5K.........",
    ".........K665K665K554K........",
    "........K6666666555543K.......",
    "........K66K665K554K43K.......",
    "........KKKKKKKKKKKKKKK.......",
    ".......K666K55555KK44K........",
    "...KKKKK665K5555554K43KKKKK...",
    "..K5555K665K5K55K54K43K3333K..",
    ".K55555K66K55e55e54K32K33333K.",
    ".K55K22K6KKK5555554K32K22K22K.",
    ".K55K24KK666K555544K32K12K22K.",
    ".K55K42KK6K66K4444K432K21K22K.",
    ".K55K44KK6K65K334K4432K22K22K.",
    ".K55K44KK66654K44K44332K2K22K.",
    ".K55K44K6K6654K4KK43322K2K22K.",
    ".K55K42K66K654KKK443322K1K22K.",
    ".K55K24444K654K2212222212K22K.",
    ".K55K42KKKK654KKKKKKKKK21K22K.",
    ".K55K4K665K654K444433332KK22K.",
    ".K55KK6655K654K4444333322K22K.",
    ".K55KK655KK654K4444K33222K22K.",
    ".K55KK655K6654K4443K33222K22K.",
    ".K55KK655K6554K4443K32221K22K.",
    "KKKKKK655KKKKKKKKKKK32221KKKKK",
    "K5444K65KK66655544433K211K332K",
    "K5444K65KK6555544433322K1K332K",
    "K5KKKK65K5KKKKKKKKKKKKK11KKK2K",
    "K54K4K65K55K44443K3322111KK32K",
    "K54K4K65K55K44443K3222111KK32K",
    "K54K44K5544444443333332K33K32K",
    "K54K44K554K4444K33333K2K33K32K",
    "K54K44K554K4444K33333K2K33K32K",
    "K54K44K55K44444K3333K22K33K32K",
    "K54K44K55K44444K3333K22K33K32K",
    "K54K44K55K4444K33333K22K33K32K",
    "K54K44KK5K4444K3333K22KK33K32K",
    "K54K44KK5544KK4433KK22KK33K32K",
    "K54444KK5544K4K433K2K2KK33332K",
    "KKKKKKKKKKKKK2KKKKK1KKKKKKKKKK",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
    "K6666666666666666666555555555K",
    "K4444444444444444444443333333K",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
]
# A berserker standing in his conical helm, his eyes starting, his teeth set in the rim of the kite shield held up
# before him, a cross and a boss cut in it, his sword raised in his right hand. w his teeth.
BERSERKER_L = [
    "............KK............",
    "...........K66K...........",
    "..K.......K6654K..........",
    ".K6K.....K665543K.........",
    ".K6K....K66555433K........",
    ".K65K..KKKKKKKKKKKK.......",
    ".K65K..K6664444333K.......",
    ".K65K.K65KKK44KKK32K......",
    ".K65K.K6KweK4KweK32K......",
    ".K65K.K6KKKK4KKKK32K......",
    ".K65K.KK5K5KKK4K4K2K......",
    ".K65K.KwKwKwKwKwKwK.......",
    ".K65KKKKKKKKKKKKKKKKKK....",
    ".K65K6666665555554443K....",
    ".K65K6555555444444432K....",
    ".K65K65K5555K44444K32K....",
    "KKKKK65K5555K44444K32K....",
    "K665K65KKKKKKKKKKKK32K....",
    "KKKKK65K555K6K444K432K....",
    ".K54K65K55K665K44K432K....",
    ".K54K65K555K5K444K432K....",
    "KK54K65KKKKKKKKKKKK32K....",
    "K655K65K5555K4444K432K....",
    ".KKKKK65K555K4444K32K.....",
    ".....K65K555K444K432K.....",
    "......K65K55K444K32K......",
    "......K655K5K44K432K......",
    ".......K65KKKKKK32K.......",
    ".......K6555444432K.......",
    "........K65544432K........",
    ".........K65443K..........",
    "..........K654K...........",
    "...........KKK............",
    "..........................",
    "........K5K...K3K.........",
    "........K5K...K3K.........",
    "........K54K.K43K.........",
    ".......KK54K.K43KK........",
    "......K6554K.K4332K.......",
    "......KKKKKK.KKKKKK.......",
    ".KKKKKKKKKKKKKKKKKKKKKKKK.",
    ".K66555555555554444444443.",
    ".K55444444444443333333332.",
    ".KKKKKKKKKKKKKKKKKKKKKKKK.",
]
# The pawn smaller, for the mark beside SECTION A-A where the title's carving leaves less room under it.
PAWN_S = [
    ".KKKKK.",
    "K66654K",
    "K65543K",
    "KKKKKKK",
    ".K654K.",
    ".K654K.",
    ".K543K.",
    "K65432K",
    "KKKKKKK",
]
PAWN_XS = [
    ".KKK.",
    "K654K",
    "KKKKK",
    ".K5K.",
    ".K4K.",
    "K543K",
    "KKKKK",
]
# The pieces as they stand on the board at the right of an H1, larger, the Lewis features cut deep enough to read
# at a glance: K the cut, 1 to 6 the ivory (or the red bone) from its darkest hollow to its polish, e an eye's
# pupil and w its white. The king on his throne, its posts knobbed and its back cut in a lattice behind him,
# crowned, his eyes staring under his brows, bearded, his sword across his knees, his robe falling in folds.
KING_M = [
    ".......K.K.K.K.......",
    "......K6K6K6K5K......",
    ".K....K6666554K....K.",
    "K6K...KKKKKKKKK...K3K",
    "K6KKKKK4666553KKKKK3K",
    "K65555K4KK6KK3K4432K.",
    "K5KKKKK4we6ew3KKKKK2K",
    "K5K111K4556543K111K2K",
    "K5K111K45KKK43K111K2K",
    "K5K11KK4566543KK11K2K",
    "K5K1K66K56543K43K1K2K",
    "K5K1K665K543K443K1K2K",
    "K5K3K6654KKK4433K3K2K",
    "K5K1K66554444333K1K2K",
    "K5KKK6655444433K3KK2K",
    "KKK65KKKKKKKKKKKKKKKK",
    "K5K66K666666666666554",
    "KKKKKKKKKKKKKKKKKKKKK",
    "K5K3K6K5544443K332K2K",
    "K5K1K6K554443K3332K2K",
    "K5K1K5K55443K33322K2K",
    "K5K1K5K5443K333222K2K",
    "K5K1K5K5443K332222K2K",
    "K5K1K6K5443K3322KKK2K",
    "K6555555544444433332K",
    "K4333333333222222221K",
    "K6655555555444443333K",
    "KKKKKKKKKKKKKKKKKKKKK",
]
# The queen on her throne, crowned over her veil, her right hand cupped to her cheek, her left arm across her body.
QUEEN_M = [
    ".......K.K.K.K.......",
    "......K6K6K6K5K......",
    ".K....K6666554K....K.",
    "K6K..KKKKKKKKKKK..K3K",
    "K6KKKK5K666553K3KKK3K",
    "K6555K6KKK6KKK3K432K.",
    "K5KKKK6Kwe6ew3K3KKK2K",
    "K5K1K66K556543K33KK2K",
    "K5K1K6K6K5K54K2K3KK2K",
    "K5KK66K66K554K32K3K2K",
    "K5KK6K665K44K432K3K2K",
    "K5KK6K6654KK4433K3K2K",
    "K5KK6KK66554443K33K2K",
    "K5KK65KK666654KK33K2K",
    "K5KK654KKKKKKKK433K2K",
    "K5KK6544444433333KK2K",
    "K5KK6544444333332KK2K",
    "K5KK654K4443K33322K2K",
    "K5KK654K4443K33322K2K",
    "K5KK65K44443K33222K2K",
    "K5KK65K4443K333222K2K",
    "K5KK65K4443K332222K2K",
    "K5KK65K443K3322222K2K",
    "K5KKK5K443K332222KK2K",
    "K6555555544444433332K",
    "K4333333333222222221K",
    "K6655555555444443333K",
    "KKKKKKKKKKKKKKKKKKKKK",
]
# The bishop standing in his mitre and chasuble, his right hand raised in blessing, his crozier in his left.
BISHOP_M = [
    ".......K.......KKK.",
    "......K6K.....K665K",
    ".....K665K...K5KK4K",
    ".....K6K54K..K5K.K3",
    "....K65K543K.K4K.K3",
    "....K6K5K443K.KK.K3",
    "....KKKKKKKKK....K3",
    "....K5we6ew3K...KK3",
    "....K5556543K...K3K",
    "....K55KKK43K...K3K",
    "...KK555543KKK..K3K",
    "..K66KK5543K44KKK3K",
    ".K66K6KK543K444K43K",
    ".K6K66K6K33K4444K3K",
    ".K6KK6K6KK3K44443K.",
    "K665K6K55K3K4443K3K",
    "K65K66555K3K44332K.",
    "K65K6655544K44332K.",
    "K654K655444K43322K.",
    "K654K6554443K3322K.",
    "K654K6554443K3222K.",
    "K654K655444K33222K.",
    "K654K65544K333222K.",
    "K654K65544K33222K3K",
    ".KK54K6544K33222K.K",
    ".K66555544444333K..",
    ".K44333332222211K..",
    "..KKKKKKKKKKKKKKK..",
]
# The knight on his stocky pony riding right: conical helm and nasal, his kite shield toward us, his spear upright,
# the pony's maned neck and long head.
KNIGHT_M = [
    "........K.....K.........",
    ".......K6K....6.........",
    "......K665K...6.........",
    "......K6654K..5.........",
    ".....K665543K.5.........",
    ".....KKKKKKKK.5.........",
    ".....K5w6w4K..5.........",
    ".....K56K54K..4...KK....",
    "...KKK5554KK..4..K55K...",
    "..K665KKKKK4K.4.K6554K..",
    "..K6665K5K444KK4K65554K.",
    "..K6655K55K44K4K655e43K.",
    ".KK6654K555K4K4K655443K.",
    "K55K654K5554KK4K6544332K",
    "K6K6554K5544K4K65443K32K",
    "K5K6554K554K44K6543K.KK.",
    "K5K6654K54K444K5443K....",
    "K5K6654K5K4444K4433K....",
    ".K5K654KK44444443332K...",
    ".K5KK65K444444433322K...",
    "..KK.KK5443333332221K...",
    ".....K5KK4KKKKKK3KK2K...",
    ".....K5K.K4K..K3K.K2K...",
    ".....K5K.K4K..K3K.K2K...",
    "...KK6555544444443332KK.",
    "...K44433333322222211K..",
    "....KKKKKKKKKKKKKKKKKK..",
]
# The berserker, a warder of the board: his conical helm, his eyes starting, his teeth in the rim of his kite
# shield, his sword upright in his right hand.
BERSERKER_M = [
    "K.......KK.......",
    "6K.....K66K......",
    "6K....K6654K.....",
    "6K...K665543K....",
    "5K..KKKKKKKKKK...",
    "5K..K6we4ew43K...",
    "5K..K5KK4KK43K...",
    "5K..K5554443K....",
    "5K.KwKwKwKwKwK...",
    "5KKK666655544KK..",
    "KKK6555555444432K",
    "K6K65K55K444K432K",
    "KKK65K55K444K432K",
    ".KK65KKKKKKKK432K",
    ".KK655K5K444K432K",
    ".K5K65K5K44K432K.",
    ".K5K655K5K4K432K.",
    "..K5K655K5K4432K.",
    "..K5K65555444432K",
    "...KK6555544432K.",
    "....K65544443K...",
    ".....K654432K....",
    "......K6543K.....",
    "......K5KK3K.....",
    ".....KK5K.K3KK...",
    "...KK6555444332K.",
    "...K44433332221K.",
    "....KKKKKKKKKKK..",
]
# The pawn: a stele with a rounded head and a cut band, on its plinth.
PAWN_M = [
    "...KKKKK...",
    "..K66654K..",
    ".K6655543K.",
    ".K6554433K.",
    ".KKKKKKKKK.",
    ".K665543K..",
    "..K65543K..",
    "..K65543K..",
    "..K65443K..",
    "..K65433K..",
    "..K55433K..",
    "..K54432K..",
    "..K54332K..",
    ".K6554432K.",
    ".K5444332K.",
    "K665544433K",
    "K444333221K",
    ".KKKKKKKKK.",
]
# The great pieces at their full size, the showpieces of a section's header and a strip's, as tall as the floor
# under the crossbeam lets them stand: K the deep cut, 1 to 6 the ivory (or the red bone) from the honey of its
# deepest patina to its polish, e an eye's pupil and w its white. The king on his throne, its knobbed posts ringed,
# its back's panels carved in plaited interlace and its seat's front in round arches; crowned, his hair to his
# shoulders, his eyes wide and staring under heavy brows, his long beard in strands, his mantle clasped, his right
# hand on the hilt and his left on the blade of the sword across his knees, his robe falling in folds to his feet.
KING_XL = [
    "............................................................",
    "......................K......K......K.......................",
    ".....................K5K....K5K....K5K...K..................",
    ".....KKK............K655K..K655K..K655KKKK..........KKK.....",
    "....K544K...........K655K..K655K..K6554K4K.........K544K....",
    "...K65443K..........K655K..K655K..K6554K4K........K65443K...",
    "...K65443K.........K66554KK66554KK66554K4K........K65443K...",
    "...K65443K.........KKKKKKKKKKKKKKKKKKKKKKK........K65443K...",
    "...K65443K.........K55e55555e55555e55555K.........K65443K...",
    "...K65443K.........K55555555555555555555K.........K65443K...",
    ".KKKKKKKK4KKKKKKKKKK44444444444444444444KKKKKKKKKK4KKKKKKKK.",
    ".K65544K44444444444KKKKKKKKKKKKKKKKKKKKKK44444444444K43333K.",
    ".K65544K4444444444K3436666655555444444434K4444444444K43333K.",
    ".K65544K4444444444K343KKKKKK5555KKKKKK434K4444444444K43333K.",
    ".K65544K4444444444K3436K6666K55K6665K4434K4444444444K43333K.",
    ".K65544K4KKKKKKKKKK3436KwwwwK6654KwwwwK34KKKKKKKKKK4K43333K.",
    ".KKKKKKK4K11K1K111K3436KweewK6554KweewK34K11K1K111K4KKKKKKK.",
    ".KKKKKKK4K1K4KK5K1K3436KweewK6554KweewK34K1K4KK5K1K4KKKKKKK.",
    ".K65544K4KK4K11K5KK34366KKKK564544KKKK434KK4K11K5KK4K43333K.",
    ".K65544K4KK4K11K5K434366666556454444444343K4K11K5KK4K43333K.",
    ".K65544K4K1K4KK5KK434366666556454444444343KK4KK5K1K4K43333K.",
    ".K65544K4K11K1K11K43436666655K53K444444343K1K1K111K4K43333K.",
    ".K65544K4K1K4KK5KK4343435KKKK3KKKK43544343KK4KK5K1K4K43333K.",
    ".K65544K4KK4K11K5K4343435435KKK43543544343K4K11K5KK4K43333K.",
    ".K65544K4KK4K11K5K43434354354K543543544343K4K11K5KK4K43333K.",
    ".KKKKKKK4K1K4KK5KK434343543543543543544343KK4KK5K1K4KKKKKKK.",
    ".KKKKKKK4K11K1K11K434343543543543543544343K1K1K111K4KKKKKKK.",
    ".K65544K4K1K4KK5KK434343543543543543544343KK4KK5K1K4K43333K.",
    ".K65544K4KK4K11K5K434343543543543543544343K4K11K5KK4K43333K.",
    ".K65544K4KK4K11K5K434343543543543543534343K4K11K5KK4K43333K.",
    ".K65544K4K1K4KK5KK434343543543543543534343KK4KK5K1K4K43333K.",
    ".K65544K4K11K5KKK34343435435435435435343434KK1K111K4K43333K.",
    ".K65544K4K1K4KK5K34343435435435435435343434K4KK5K1K4K43333K.",
    ".K65544K4KK4K11KK34343435435435435435343434KK11K5KK4K43333K.",
    ".KKKKKKK4KK4K11KK34343435435435435435343434KK11K5KK4KKKKKKK.",
    ".KKKKKKK4K1K4KK5K34343435435435435435343434K4KK5K1K4KKKKKKK.",
    ".K65544K4K11KK4KKKKKKKKK543543543543KKKKKKKKK1K111K4K43333K.",
    ".K65544K4K1K4KK5KK6655K5K4354354354K33K3322K4KK5K1K4K43333K.",
    ".K65544K4KK4K11KK66655K5K4354354354K33K33222K11K5KK4K43333K.",
    ".K65544K4KK4K11K666655K55K35435435K333K332222K1K5KK4K43333K.",
    ".K65544K4K1K4KKKKKKK55K55K35435435K333K33KKKKKKKK1K4K43333K.",
    ".K65544K4K11KK55544K55K555K543543K3333K33K33322K11K4K43333K.",
    ".K65544K4K1K4K55544K55K555KKK66KKK3333K33K33322KK1K4K43333K.",
    ".KKKKKKK4KK4K555544K55K55554K54K443333K33K333222KKK4KKKKKKK.",
    ".KKKKKKK4KK4K5555444K5K555544444443333K3K3333222KKK4KKKKKKK.",
    ".K65544K4K1KK5555444K5K555544444443333K3K3333222K1K4K43333K.",
    ".K65544K4K11K5555444K5K555544444443333K3K3333222K1K4K43333K.",
    ".K65544K4K1KK5555444K5K555544444443333K3K3333222K1K4K43333K.",
    ".K65544K4KKK65555KKKK5K555544444443333K3K33332222KK4K43333K.",
    ".K65544K4KKK6KKK5K4KK5K555544444443333K3K3KKKK222KK4K43333K.",
    ".K65544K4K1KK655K54K4KK555544444443333KK4K4444K22KK4K43333K.",
    ".K65544KK21K66554K4K4KK555544444443333KK4K4444K2K1K4K43333K.",
    ".KKKKKK55KK6665544KKKKKKKKKKKKKKKKKKKKKKK544443KKKKKKKKKKKK.",
    ".KKKKK6553K6665544KK66666666666666666666K544443K66666666K2K.",
    ".K655K6553K6665544KK55555555555555555555K544443K555555555KK.",
    ".K655K6553K6665544KK44444444444444444444K544443K44444444K3K.",
    ".K6554K55K1K66554K4KKKKKKKKKKKKKKKKKKKKKKK4444KKKKKKKKKK33K.",
    ".K65544KK21KK655K54KKKKKKKKKKKKKKKKKKKKKKK4444KKK1K4K43333K.",
    ".K65544K4KK4KKKK6K4K5553555434444343333333KKKK1K5KK4K43333K.",
    ".K65544K4K22222K6K4K5553555434444343333333332K2222K4K43333K.",
    ".K655444KKKKKKKK6KKK5553555434444343333333332KKKKKKK443333K.",
    ".KKKKKKKK33333K6663555535554344443433333333322K3333KKKKKKKK.",
    ".KKKKKKKK33333K6663555535554344443433333333322K3333KKKKKKKK.",
    ".K655444K333K3K6663555535554344443433333333322KK333K443333K.",
    ".K655444K33K1KK6663555535554344443433333333322K1K33K443333K.",
    ".K655444K33K11K6663555535554344443433333333322K1K33K443333K.",
    ".K655444K3K111K6663555535554344443433333333322K11K3K443333K.",
    ".K655444K3K111K6663555535554344443433333333322K11K3K443333K.",
    ".K655444K3K111K6663555535554344443433333333322K11K3K443333K.",
    ".K655444K3K11K666635555355543444434333333333222K1K3K443333K.",
    ".KKKKKKKK3K11K666635555355543444434333333333222K1K3KKKKKKKK.",
    ".KKKKKKKK3K11K66663KKKKKKK54344443KKKKKKK333222K1K3KKKKKKKK.",
    ".K655444K3K11KKKKKKK55555KKKKKKKKKK44444KKKKKKKK1K3K443333K.",
    "KKKKKKKKKKKKK555555KKKKKKK55555555KKKKKKK5555555KKKKKKKKKKKK",
    "K6666666666666666666666666666666666666666666666666666666666K",
    "K5555555555555555555555555555555555555555555555555555555555K",
    "K4444444444444444444444444444444444444444444444444444444444K",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
]
# The berserker standing in his conical helm with its nasal, his eyes starting under his brows, his teeth set in
# the rim of the kite shield held up before him, its boss and its cross cut in it, his sword raised in his right hand.
BERSERKER_XL = [
    ".................K................",
    "...K............K4K...............",
    "...K............K4K...............",
    "..K6K..........K544K..............",
    "..K6K.........K55444K.............",
    "..K6K.........K55444K.............",
    "..K6K........K5554443K............",
    "..K6K.......K555544433K...........",
    "..K6K......K65555444333K..........",
    "..K6K......K65555444333K..........",
    "..K6K.....K6655554443333K.........",
    "..K6K....K666555544433332K........",
    "..K6K..KKKKKKKKKKKKKKKKKKKKK......",
    "..K6K..K6655555544444433333K......",
    "..K6K..KKKKKKKKKKKKKKKKKKKKK......",
    "..K6K....KKKKKK5KKKKKKK44K........",
    "..K6K....KKwwwK5K5K5KwwwKK........",
    "..K6K....KKweeK5K5K5KeewKK........",
    "..K6K....KKweeK5K5K5KeewKK........",
    "..K6K....K666665K5K554444K........",
    "..K6K....K666665KKK554444K........",
    "..K6K....KKwKwKwKwKwKwKwKK........",
    "..K6KKKKKKKKKKKKKKKKKKKKKKKKKKK...",
    "..K6KK6666666666666666666666K2K...",
    "..K6K6655555544444433333322222K...",
    "..K6K6655555544443433333322222K...",
    "..K6K6655555544443433333322222K...",
    "..KK666555555444434333333222222K..",
    "..KK666555555444434333333222222K..",
    "..KK666555555444434333333222222K..",
    "KKKK666555555444KKK333333222222K..",
    "KK5K66655555544K544K33333222222K..",
    "..KK6665555554K65442K3333222222K..",
    "..K3K665555554K65442K333322222K...",
    "..KKKK65555554K65442K333322222K...",
    ".K5544K55555544K544K3333322222K...",
    "K655444K55555444KKK33333322222K...",
    "K655444K333333333333333333333K....",
    "K655444K555554444343333332222K....",
    "K655444K555554444343333332222K....",
    ".K5544K5555554444343333332222K....",
    "..KKKK65555554444343333332222K....",
    "......K555555444434333333222K.....",
    "......K555555444434333333222K.....",
    "......K555555444434333333222K.....",
    ".......K5555544443433333322K......",
    ".......K5555544443433333322K......",
    "........K55554444343333332K.......",
    "........K55554444343333332K.......",
    ".........K555444434333333K........",
    ".........KK5544443433333KK........",
    ".........KK5544443433333KK........",
    ".........K5K54444343333K3K........",
    "........K555K444434333K332K.......",
    "........K555K444434333K332K.......",
    "........K5555K4443433K3332K.......",
    "........K5555K4443433K3332K.......",
    "........K55554K44343K33332K.......",
    "........K555544K444K333332K.......",
    ".......K5555544K444K3333322K......",
    ".......K555KKKK3K4K4KKK3322K......",
    ".......KKKKK5543K4K433KKKKKK......",
    "...........K554K.K4433K...........",
    "...........K554K..K433K...........",
    "...........K554K..K433K...........",
    "...........K554K..K433K...........",
    "...........K554K..K433K...........",
    "...........K554K..K433K...........",
    ".........KKKKKKK..KKKKKKK.........",
    ".........K65555K..K44433K.........",
    ".KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK.",
    ".K666666666666666666666666666666K.",
    ".K555555555555555555555555555555K.",
    ".K555555555555555555555555555555K.",
    ".K444444444444444444444444444444K.",
    ".KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK.",
]
# The queen on her throne, crowned over the veil falling to her shoulders, her eyes wide, her right hand raised to
# her cheek and her left arm across her body under its elbow, her robe falling in folds.
QUEEN_XL = [
    "...............K....K....K................",
    "...KK..........KK...KK...KK..........KK...",
    "..K54K........K65K.K65K.K65K........K54K..",
    ".K6543K.......K65K.K65K.K65K.......K6543K.",
    ".K6543K......K6654K6654K6654K......K6543K.",
    ".K6543K......KKKKKKKKKKKKKKKK......K6543K.",
    ".KKKKK4KKKKKKK55555555555555KKKKKKK4KKKKK.",
    ".K654K444444KKKKKKKKKKKKKKKKKKK44444K433K.",
    ".K654K444444K65555554444443333K44444K433K.",
    ".K654K444444K65666655554444433K44444K433K.",
    ".K654K4KKKKKK6566KKKK55KKKK433KKKKK4K433K.",
    ".KKKKK4K1141K6566KwwK55KwwK433K1K1K4KKKKK.",
    ".KKKKK4KK4KK66566KeeK65KeeK4333K5KK4KKKKK.",
    ".K654K4KK4KK66KKK6KK5644KK44333K5KK4K433K.",
    ".K654K4KK4KK6K655K6556444444333K5KK4K433K.",
    ".K654K4K115KK66555K55K4K4444333KK1K4K433K.",
    ".K654K4KK4KKK66555K555544444333K5KK4K433K.",
    ".K654K4KK4KKK66555K555544444333K5KK4K433K.",
    ".KKKKK4KK4KKK66555KKKKK44443333K5KK4KKKKK.",
    ".KKKKK4K114KKK655K65555444K3333KK1K4KKKKK.",
    ".K654K4KK4KKK5KKK66555544K2K333K5KK4K433K.",
    ".K654K4KK4KK6554KKKKKKKKKKKK333K5KK4K433K.",
    ".K654K4KK4K66554K5554444433K3333KKK4K433K.",
    ".K654K4K11K6655K55554444433K3333K1K4K433K.",
    ".K654K4KKK66655K55554444433K3333KKK4K433K.",
    ".KKKKK4KKK66655K55554444433K3333KKK4KKKKK.",
    ".KKKKK4KKK66655K55554444433KKKKKKKK4KKKKK.",
    ".K654K4K1K66655K5555444443333332K1K4K433K.",
    ".K654K4KK4K6655K5555444443333332KKK4K433K.",
    ".K654K4KK4K665K555554444433333K2KKK4K433K.",
    ".K654K4KK4K665K555554KKKKKKKKKK2KKK4K433K.",
    ".K654K4K1KKKKKKKKKKKK554444443K22KK4K433K.",
    ".KKKKK4KKK66K666665555544444433K2KK4KKKKK.",
    ".KKKKK4KKK666K666655555KKKKKKKKK2KK4KKKKK.",
    ".K654K4KKK666KKKKKKKKKK4433333322KK4K433K.",
    ".K654K4K1K666K6555554444433333322KK4K433K.",
    ".K654K4KKKKKKKKKKKKKKKKKKKKKKKKKKKK4K433K.",
    ".K6544KKK3K663555354434443333332K3KK4433K.",
    ".K6544K33KK663555354434443333332KK3K4433K.",
    ".KKKKKK33KK663555354434443333332K1KKKKKKK.",
    ".KKKKKK3K1K663555354434443333332K11KKKKKK.",
    ".K6544K3KK66635553544344433333322K1K4433K.",
    ".K6544K3KK66635553544344433333322K1K4433K.",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
    "K6666666666666666666666666666666666666666K",
    "K5555555555555555555555555555555555555555K",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",
]
PIECES = {"king": KING, "queen": QUEEN, "bishop": BISHOP, "knight": KNIGHT, "berserker": BERSERKER, "pawn": PAWN,
          "pawn_s": PAWN_S, "pawn_xs": PAWN_XS, "king_l": KING_L, "queen_l": QUEEN_L, "berserker_l": BERSERKER_L,
          "king_m": KING_M, "queen_m": QUEEN_M, "bishop_m": BISHOP_M, "knight_m": KNIGHT_M, "berserker_m": BERSERKER_M,
          "pawn_m": PAWN_M, "king_xl": KING_XL, "queen_xl": QUEEN_XL, "berserker_xl": BERSERKER_XL}
SIDES = {"ivory": IV, "red": RD}


def piece_pal(side: str, night: bool, lit: bool = False) -> dict:
    """A piece's tones: by day its own ivory, its hollows yellowed in the honey of its patina, or its bone stained
    red; by night the same two steps into the dark, or one where a lamp stands by it."""
    R = SIDES[side]
    k = (-1 if lit else -2) if night else 0
    pal = {"K": R[0], "e": HALL[0], "w": R[6]}
    for t in range(1, 7):
        pal[str(t)] = R[max(1, t + k)]
    if side == "ivory":
        pal["1"], pal["2"] = HO[max(0, 2 + k)], HO[max(0, 3 + k)]
    return pal


def piece_cells(rows: list, side: str, night: bool, face: int = 1, lit: bool = False, thin: bool = False) -> dict:
    """A piece as cells {(x, y): colour}, facing right (1) or left (-1). By night the hearth on the left lights
    the edge of the piece toward it: the cut along that edge glows dull and the ivory just inside it bright, and
    the rest of the piece falls into the dark; a piece `lit` by the lamp beside it falls only a step into the dark,
    its face and its carving still showing. `thin`, for a drawing made lighter, leaves out the light's outermost
    reach into the ivory."""
    rows = rows if face > 0 else flip(rows)
    pal = piece_pal(side, night, lit)
    cells = {(i, j): pal[ch] for j, row in enumerate(rows) for i, ch in enumerate(row) if ch in pal}
    if night:
        hot, warm = (FIRE[5], IV[5]) if side == "ivory" else (FIRE[4], RD[5])
        for j, row in enumerate(rows):
            run = False
            for i, ch in enumerate(row):
                if ch == ".":
                    run = False
                    continue
                if not run:
                    run = True
                    cells[(i, j)] = FIRE[2]
                    if i + 1 < len(row) and row[i + 1] not in ".Ke":
                        cells[(i + 1, j)] = hot
                        if i + 2 < len(row) and row[i + 2] not in ".Ke" and not thin:
                            cells[(i + 2, j)] = warm
    return cells


def piece(p: Pix, kind: str, side: str, cx, foot, night: bool, face: int = 1, L="base", reuse=False, lit=False):
    """A piece standing with its plinth's foot on the row above `foot`, centred on column cx. `reuse` keeps it as a
    symbol drawn once a file, for a piece placed again and again; `lit`, a piece a lamp lights by night. Returns
    its box (x0, y0, x1, y1)."""
    rows = PIECES[kind]
    w, h = len(rows[0]), len(rows)
    x, y = round(cx - w / 2), foot - h
    cells = piece_cells(rows, side, night, face, lit, thin=p.lite)
    if reuse:
        key = ("piece", kind, side, night, face, lit)
        if key not in p.syms:
            p.symbol(key, cells)
        p.use(key, x, y, L)
        keep(p, {(x + i, y + j) for (i, j) in cells})
    else:
        for (i, j), c in cells.items():
            p.px(x + i, y + j, c, L)
    return (x, y, x + w, foot)


# --------------------------------------------------------------------------- the board in perspective
class Board:
    """The board seen from a player's seat: its near edge from column x0 at row gy, a square `sq` wide there, its
    eight ranks running back `depth` rows to its far edge, each a little narrower and shallower than the one before
    (the far edge `shrink` of the near one). Board places are (u, v): files 0 to `files` (eight on a whole board,
    more on the long stretch a court stands on) from the left, ranks 0 to 8 from the near edge."""

    def __init__(self, x0, gy, sq, depth, shrink=0.74, files=8):
        self.x0, self.gy, self.sq, self.depth, self.shrink, self.files = x0, gy, sq, depth, shrink, files
        self.a = (1 / shrink - 1) / 8
        self.cx = x0 + files / 2 * sq
        self.s8 = self.s(8)

    def __repr__(self):
        return f"Board({self.x0}, {self.gy}, {self.sq}, {self.depth}, {self.shrink}, {self.files})"

    def s(self, v):
        """How much narrower rank v is than the near edge."""
        return 1 / (1 + self.a * v)

    def y(self, v):
        """The row rank v lies at."""
        return self.gy - self.depth * (1 - self.s(v)) / (1 - self.s8)

    def x(self, u, v):
        """The column of file u at rank v."""
        return self.cx + (u - self.files / 2) * self.sq * self.s(v)

    def v_at(self, y):
        """The rank at row y."""
        t = (self.gy - y) / self.depth * (1 - self.s8)
        return (1 / max(1e-6, 1 - t) - 1) / self.a

    def u_at(self, x, v):
        """The file at column x on rank v."""
        return (x - self.cx) / (self.sq * self.s(v)) + self.files / 2

    def at(self, f, r):
        """The foot of a piece standing on file f, rank r (from 0): the middle of its square, a little forward."""
        v = r + 0.42
        return self.x(f + 0.5, v), round(self.y(v))


def shadow_cells(b: Board, f, r, night: bool, lift=0) -> set:
    """The cells of a piece's shadow on the board: by day a short one, down and to its right from the light above;
    by night a long one thrown away from the hearth on the left, across the squares along its rank. A piece lifted
    `lift` rows off the board throws it shorter by day and longer by night."""
    if night:
        length, width = 2.4 + lift * 0.06, 0.3
    else:
        length, width = 0.7 - lift * 0.03, 0.36
    u0, v0 = f + 0.5, r + 0.42
    cells = set()
    top, bot = b.y(v0 + width), b.y(v0 - width * 0.7)
    for y in range(math.floor(top), math.ceil(bot) + 1):
        v = b.v_at(y + 0.5)
        if not (v0 - width * 0.7 <= v <= v0 + width):
            continue
        xs = b.x(u0 - 0.1, v)
        taper = 1 - abs(v - v0) / (width * 1.6)
        xe = b.x(u0 + length * taper, v)
        cells |= {(x, y) for x in range(math.floor(xs), math.ceil(xe))}
    return cells


def board_squares(p: Pix, b: Board, night: bool, x1, shade=frozenset(), L="base", ranks=8):
    """The board's squares between its edges, cut off at column x1 where the sheet's edge stands over it: squares of
    ivory inlay and of dark oak by turns, the far ranks a shade deeper; by night the ivory squares warm on the
    hearth's side and dark toward the other. Where a piece's shadow lies (`shade`) each square is laid in its own
    darker tones. Along its left and far edges an ivory rim, and down its near edge the board's face, squares of
    ivory and of red bone by turns, over its foot's shadow. Only its first `ranks` ranks are laid where a stretch
    of the board is all that shows."""
    top = math.ceil(b.y(ranks))
    for y in range(top, b.gy):
        v = b.v_at(y + 0.5)
        xl, xr = math.ceil(b.x(0, v) - 0.5), min(x1, math.floor(b.x(b.files, v) - 0.5) + 1)
        far = v > 5.2 and ranks == 8
        for x in range(xl, xr):
            u = b.u_at(x + 0.5, v)
            light = (int(u) + int(v)) % 2 == 1
            if night:
                warm = u < 2.6 and not p.lite
                t = (3 if warm else 2) if light else (2 if warm else 1)
            else:
                far_ = far and not p.lite
                t = (4 if far_ else 5) if light else (3 if far_ else 4)
            if (x, y) in shade:
                t -= 2 if light else 1
            p.px(x, y, (IV if light else OAK)[max(0, t)], L)
        if xl - 1 < x1:
            p.px(xl - 1, y, IV[2 if night else 5], L)
            p.px(xl - 2, y, IV[0], L)
    xa, xb = math.ceil(b.x(0, ranks) - 0.5) - 2, min(x1, math.floor(b.x(b.files, ranks) - 0.5) + 1)
    p.hline(xa, xb, top - 1, IV[2 if night else 5], L)
    p.hline(xa, xb, top - 2, IV[0], L)
    k = -2 if night else 0
    xl, xr = math.ceil(b.x(0, 0) - 0.5) - 2, min(x1, math.floor(b.x(b.files, 0) - 0.5) + 1)
    for x in range(xl, xr):
        red = ((x - xl) // 4) % 2 == 1
        R, t = (RD, (5, 3, 2, 1)) if red else (IV, (6, 5, 4, 3))
        for j in range(4):
            p.px(x, b.gy + j, R[max(1, t[j] + k)], L)
        p.px(x, b.gy + 4, IV[0], L)


def knight_move(p: Pix, b: Board, start, end, night: bool, motion: bool, side="ivory", face=1, kind="knight",
                lit=False):
    """The knight lifting off his square, leaping in an arc and setting down on the square his move takes him to,
    resting there, then lifting back to where he stood, round and round; each place he passes through a frame of
    the loop, the knight drawn once and placed, and his shadow, drawn once, on the board under him, the two together
    in the frame. A still drawing keeps him on his first square. `kind` is the knight's size, `lit` whether a
    lamp by the board lights him by night."""
    rows = PIECES[kind]
    key = ("piece", kind, side, night, face, lit)
    if key not in p.syms:
        p.symbol(key, piece_cells(rows, side, night, face, lit, thin=p.lite))
    w, h = len(rows[0]), len(rows)
    (f0, r0), (f1, r1) = start, end
    sx, sy = b.at(f0, r0)
    skey = ("knight shadow", night, round(sx), sy)
    if skey not in p.syms:
        p.symbol(skey, {(x - round(sx), y - sy): f"{X['shade_ink']}:{'.55' if night else '.32'}"
                        for (x, y) in shadow_cells(b, f0, r0, night)})
    fm, rm = (f0 + f1) / 2, (r0 + r1) / 2
    frames = ((f0, r0, 0, 0.0, 0.42), (f0, r0, 4, 0.42, 0.47), (fm, rm, 10, 0.47, 0.52), (f1, r1, 4, 0.52, 0.57),
              (f1, r1, 0, 0.57, 0.9), (fm, rm, 7, 0.9, 0.95), (f0, r0, 3, 0.95, 1.0))
    if not motion:
        frames = frames[:1]
    for i, (f, r, lift, t0, t1) in enumerate(frames):
        L = p.seq(f"kn{i}", t0, t1, 7.0, keep=i == 0, z=0.6) if motion else "base"
        x, y = b.at(f, r)
        p.use(skey, round(x), y, L)
        p.use(key, round(x - w / 2), y - h - lift, L)
        keep(p, {(round(x - w / 2) + i, y - h - lift + j) for i in range(w) for j in range(h)})


# --------------------------------------------------------------------------- the game
# The game staged on its table at the right of an H1, as the room the words leave it allows: the whole board,
# wide and shallow, where the room runs wide; its near corner, running off under the frame at the right, where it
# runs narrow; and the whole board again on a phone. Each staging is the square's width at the near edge, the
# board's depth, how much narrower its far edge is, the pieces as (kind, side, file, rank, facing) in square
# coordinates from the ivory's near left corner, and the knight's square and the square his leap takes him to.
# The pieces stand at the size where each Lewis piece reads at a glance, red and ivory by turns, those behind
# between those in front so every head and crown shows.
STAGES = {
    "wide": dict(sq=16.0, depth=44, shrink=0.8, knight=((3.3, 0.2), (4.05, 1.8)), pieces=(
        ("queen_m", "ivory", 0.5, 0.45, 1), ("bishop_m", "red", 6.6, 0.6, -1), ("berserker_m", "red", 2.0, 3.5, 1),
        ("pawn_m", "red", 0.45, 6.4, 1), ("king_m", "ivory", 5.15, 3.9, -1))),
    "corner": dict(sq=16.0, depth=40, shrink=0.88, knight=((1.75, 0.2), (2.3, 1.75)), pieces=(
        ("queen_m", "red", 0.3, 0.45, 1), ("king_m", "ivory", 1.05, 3.3, 1))),
    "phone": dict(sq=12.0, depth=36, shrink=0.8, knight=((0.55, 0.3), (2.35, 0.1)), pieces=(
        ("berserker_m", "red", 2.25, 3.9, 1), ("queen_m", "red", 4.3, 0.45, -1), ("king_m", "ivory", 6.15, 4.0, -1),
        ("pawn_m", "ivory", 7.05, 0.1, -1))),
}
TABLE = 12          # the rows from the floor to the top of the table the board stands on
CEIL = BEAM + 6     # the highest row a scene's top reaches, clear of the crossbeam


def gaming_table(p: Pix, x0, x1, top, g, night: bool):
    """A low trestle table of oak from column x0 to x1, its top slab from row `top`, lit along its upper edge, and
    its two trestles standing on the floor at row g, a stretcher between them low down. A table running off under
    the frame at the right has its far trestle there, under the frame."""
    k = -1 if night else 0
    for x in range(x0, x1):
        end = x in (x0, x1 - 1)
        for j, t in enumerate((6, 4, 2)):
            p.px(x, top + j, OAK[0] if end else OAK[t + k])
        p.px(x, top + 3, OAK[0])
    for lx in (x0 + 3, x1 - 7):
        for y in range(top + 4, g):
            for dx, c in ((0, OAK[0]), (1, OAK[5 + k]), (2, OAK[3 + k]), (3, OAK[0])):
                p.px(lx + dx, y, c)
        for dx, c in ((-1, OAK[0]), (0, OAK[4 + k]), (1, OAK[4 + k]), (2, OAK[3 + k]), (3, OAK[2 + k]), (4, OAK[0])):
            p.px(lx + dx, g - 1, c)
    for x in range(x0 + 7, x1 - 7):
        p.px(x, g - 5, OAK[3 + k])
        p.px(x, g - 4, OAK[1])


def stage_board(s: dict, x0, g) -> Board:
    """The board a staging stands on its table on the floor at row g, its near left corner at column x0, laid as
    deep as STAGES says or, where the header is too low for that under the crossbeam, as much shallower as keeps
    every piece's crown below CEIL."""
    top = g - TABLE
    for depth in range(s["depth"], 20, -1):
        b = Board(x0, top - 4, s["sq"], depth, shrink=s["shrink"])
        if min(b.at(f, r)[1] - len(PIECES[kind]) for kind, _, f, r, _ in s["pieces"]) >= CEIL:
            return b
    return b


# A soapstone oil lamp: a shallow bowl of grey stone on its foot, the wick lying in its lip. K its cut, S s the
# stone lit and shaded, w the wick; the flame burns over the wick.
LAMP = [
    "....w....",
    "KKKKwKKKK",
    "KSSSSSSsK",
    ".KSSSSsK.",
    "..KsssK..",
    "...KKK...",
]
FLAMES = (
    {(4, -4): 4, (3, -3): 3, (4, -3): 6, (5, -3): 4, (3, -2): 4, (4, -2): 6, (5, -2): 3, (3, -1): 2, (4, -1): 5,
     (5, -1): 2},
    {(4, -5): 3, (4, -4): 5, (3, -3): 4, (4, -3): 6, (5, -3): 3, (3, -2): 3, (4, -2): 6, (5, -2): 4, (4, -1): 5,
     (3, -1): 2},
    {(5, -4): 3, (4, -4): 4, (3, -3): 3, (4, -3): 6, (5, -3): 5, (3, -2): 4, (4, -2): 5, (5, -2): 3, (4, -1): 4,
     (5, -1): 2},
)


def oil_lamp(p: Pix, x, foot, night: bool, motion: bool):
    """The soapstone lamp standing with its foot on the row above `foot`, its left at x, its flame burning over the
    wick (in a moving header its tongues leaping in time with the hearth's, frame by frame), and by night the pool
    of its light over the board and the pieces beside it, the second light of the hall, the dark between it and
    the hearth."""
    pal = {"K": STONE[0], "S": STONE[4 if night else 5], "s": STONE[2 if night else 3], "w": OAK[0]}
    y = foot - len(LAMP)
    cells = {(x + i, y + j): pal[ch] for j, row in enumerate(LAMP) for i, ch in enumerate(row) if ch in pal}
    for (cx, cy), c in cells.items():
        p.px(cx, cy, c)
    frames = FLAMES if motion else FLAMES[:1]
    for phase, flame in enumerate(frames):
        L = p.seq(f"fire{phase}", phase / 3, (phase + 1) / 3, BURN, keep=phase == 0, z=0.7) if motion else "base"
        for (i, j), t in flame.items():
            p.px(x + i, y + j, FIRE[t], L)
    keep(p, set(cells) | {(x + i, y + j) for f in frames for (i, j) in f})
    if night:
        glow(p, x + 4, y - 2, 62, 48, FIRE[2], (0.07, 0.13, 0.2))
        glow(p, x + 4, y - 2, 7, 6, FIRE[4], (0.12, 0.22), L=p.flicker(0, back=True) if motion else "haze")
        lamp(p, x + 4, y - 2, 18, set(cells))


MOTES = 24.0        # seconds the motes take to drift down their stretch of the shaft: a slow ambient sweep


def daylight(p: Pix, sx, tx, ty, motion: bool):
    """By day a shaft of winter light from the smoke hole in the roof slanting down onto the game: from under the
    crossbeam about column sx to the board about (tx, ty), pale, brightest at its heart; in a moving header motes of
    dust drift slowly down it (see MOTES)."""
    top = HANG
    L = p.layer("shaft", z=-19)
    for w, a in ((20, 0.18), (11, 0.24)):
        pts = f"{sx - w // 2},{top} {sx + w // 2},{top} {tx + w},{ty} {tx - w},{ty}"
        p.shapes[L].append(f'<polygon points="{pts}" fill="{X["glint"]}" fill-opacity="{a}"/>')
    if not motion:
        return
    rnd = random.Random(5)
    dx, dy = tx - sx, ty - top
    motes = []
    for _ in range(7):
        t = rnd.uniform(0.05, 0.75)
        motes.append((round(sx + dx * t + rnd.uniform(-4, 4)), round(top + dy * t)))
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for x, y in motes)
    n = 12
    steps = ";".join(f"{num(dx * i / n / 4)} {num(dy * i / n / 4)}" for i in range(n))
    p.raw(-18, f'<g fill="{X["glint"]}" fill-opacity=".8">{rects}<animateTransform attributeName="transform" '
               f'type="translate" values="{steps}" dur="{num(MOTES)}s" repeatCount="indefinite" calcMode="discrete"/>'
               f'</g>',
          f'<g fill="{X["glint"]}" fill-opacity=".8">{rects}</g>')


def sunlit(p: Pix, cx, cy, rx, ry):
    """The pool of the shaft's light where it falls on the board about (cx, cy): the squares a tone brighter on
    their own ramp within it."""
    base = p.layers["base"]
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            c = base.get((x, y))
            if c in IV or c in OAK:
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 < 1:
                    base[(x, y)] = step(c, 1)


def staged_game(p: Pix, x1, g, night: bool, motion: bool, layout: str, x0=None, reach=0):
    """The game on its table on the floor at row g, staged as STAGES says, ending at column x1 or, for its near
    corner, from its near left corner at column x0 off under the frame at the right: the trestle table, the board
    in perspective with its edge of ivory and red bone, every piece on its square throwing its shadow on the board,
    and the knight lifting off his square and leaping to the next. By night the soapstone lamp on the table at the
    board's left lights the pieces' faces and throws their shadows long across the board; by day the shaft of light
    from the smoke hole falls on the game. Each piece is drawn once and placed, the farthest first. Returns the span
    of the rule it covers."""
    s = STAGES[layout]
    sq = s["sq"]
    w = round(8 * sq)
    if x0 is None:
        x0 = x1 - w - 2
    edge = p.w - EDGE
    b = stage_board(s, x0, g)
    top = g - TABLE
    gaming_table(p, x0 - 4 - reach, min(edge + 1, x0 + w + 3), top, g, night)
    k = -1 if night else 0
    for i, dx in enumerate(range(6, reach - 10 if not p.lite else 0, 11)):
        R = IV if i % 2 == 0 else RD
        stamp(p, x0 - reach + dx, top - 4 + (i % 2), TABLEMAN, {"K": R[0], "6": R[6 + k], "5": R[5 + k],
                                                                  "4": R[4 + k]})
    placed = sorted(s["pieces"], key=lambda q: -q[3])
    shade = set()
    for kind, side, f, r, face in placed:
        shade |= shadow_cells(b, f, r, night)
    board_squares(p, b, night, min(edge, x0 + w + 2), shade)
    if not night:
        sunlit(p, b.x(1.6, 2.0), b.y(2.0), 2.2 * sq, 1.1 * sq)
    for kind, side, f, r, face in placed:
        x, y = b.at(f, r)
        piece(p, kind, side, x, y, night, face=face, reuse=True, lit=night)
    knight_move(p, b, s["knight"][0], s["knight"][1], night, motion, kind="knight_m", lit=night)
    oil_lamp(p, x0 - 6, top, night, motion)
    if not night:
        tx, ty = b.x(1.6, 2.0), b.y(2.0)
        daylight(p, tx - (ty - HANG) * 0.55, tx, ty, motion)
    return (x0 - 7 - reach, min(x1 + 2, edge))


# --------------------------------------------------------------------------- the hearth and its light
def lamp(p: Pix, cx, cy, r, own=()):
    """Register the fire's light at (cx, cy): once the drawing is done, `firelight` lays it into what stands within
    `r` of it. `own` are the fire's own pixels, which it leaves as they are."""
    p.lamps.append((cx, cy, r, 0, set(own)))


# What the fire's light falls on: the stone, the oak, the iron, the leather, the gilt and the ivory near it.
LIT = (set(STONE) | set(OAK) | set(IRON) | set(LEATHER) | set(GILT) | set(IV) | set(HO) | set(RD) | set(SMOKE)
       | set(HALL))


def firelight(p: Pix):
    """By night the fire's light on what stands near it, laid into the colours themselves: within its reach what
    it falls on is a tone lighter on its own ramp, and in the near half of its reach two tones, so the stones of
    the kerb, the horn, the purse and the tablemen take the light nearest the flames and fall dark away from them.
    The fire's own pixels and the words are left as they are. Drawn lighter, the light keeps its near half."""
    base = p.layers["base"]
    for (cx, cy, r, _, own) in p.lamps:
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y))
                if c is None or (x, y) in own or c not in LIT:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15) / r
                if d >= (0.5 if p.lite else 1):
                    continue
                base[(x, y)] = step(c, 2 if d < 0.5 else 1)
    p.lamps = []


def flames(w: int, h: int, seed: int, frame: int = 0) -> list:
    """A frame of a fire `w` wide and `h` tall as character art, 2 to 6 its tongues' heat from the deep orange at
    their edges to the white at their roots: one tall tongue and four lower ones, the same tongues in every frame,
    each frame leaping them higher or lower and leaning their tips as the draught takes them, each tapering to its
    tip."""
    rnd = random.Random(seed)
    tongues = [(w / 2 + rnd.uniform(-1, 1), h * 0.94, w * 0.34, rnd.uniform(-1.5, 1.5))]
    for _ in range(4):
        tongues.append((rnd.uniform(w * 0.15, w * 0.85), h * rnd.uniform(0.38, 0.68), w * rnd.uniform(0.13, 0.21),
                        rnd.uniform(-2, 2)))
    rows = []
    for y in range(h):
        row = ""
        for x in range(w):
            best = 0.0
            for i, (tx, th, tw, curl) in enumerate(tongues):
                sway = math.sin(frame * 2.1 + i * 1.7)
                th = min(h, th * (1 + 0.13 * sway))
                curl = curl + 1.6 * math.sin(frame * 2.1 + i * 2.3)
                t = (h - 1 - y) / th
                if 0 <= t <= 1:
                    hw = tw * (1 - t) ** 0.6 + 0.4
                    d = abs(x + 0.5 - (tx + curl * t * t)) / hw
                    if d <= 1:
                        best = max(best, (1 - d * 0.55) * (1 - t * 0.7))
            row += "." if best <= 0 else "6" if best > 0.82 else "5" if best > 0.66 else "4" if best > 0.48 else \
                "3" if best > 0.3 else "2"
        rows.append(row)
    return rows


# The fire by night, tall, and by day banked low, each in three frames that follow one another.
FIRE_NIGHT = [flames(24, 34, 7, f) for f in range(3)]
FIRE_DAY = [flames(20, 17, 7, f) for f in range(3)]
BURN = BLINKS["flicker"][2]     # seconds the fire's three frames take, round and round: the engine's flicker


def fire(p: Pix, cx, foot, night: bool, motion: bool, frames=None):
    """The fire on the hearth, its foot on the row above `foot` about column cx: by night tall, its tongues leaping
    frame by frame, sparks flying up from it with them and its glow in the air round it; by day banked low, its
    tongues shorter. What the frames share burns still and only the tongues that change, and by night the sparks,
    are drawn in each frame. A still drawing keeps its first frame, its sparks standing in the air. Returns its
    pixels in the first frame."""
    frames = frames or (FIRE_NIGHT if night else FIRE_DAY)
    cells = []
    for rows in frames:
        x0, y0 = round(cx - len(rows[0]) / 2), foot - len(rows)
        cells.append({(x0 + k, y0 + j): FIRE[int(ch)] for j, row in enumerate(rows) for k, ch in enumerate(row)
                      if ch != "."})
    common = {xy: c for xy, c in cells[0].items() if all(f.get(xy) == c for f in cells[1:])} if motion else cells[0]
    for xy, c in common.items():
        p.px(*xy, c)
    h = len(frames[0])
    if motion:
        for i, f in enumerate(cells):
            L = p.seq(f"fire{i}", i / 3, (i + 1) / 3, BURN, keep=i == 0, z=0.7)
            for xy, c in f.items():
                if xy not in common:
                    p.px(*xy, c, L)
            if night:
                for (dx, dy) in ((-3, 4), (2, 9), (-1, 15), (4, 20)):
                    yy = foot - h - 2 - ((dy + 8 * i) % 24)
                    p.px(cx + dx + (i % 2), yy, FIRE[5] if (dy + i) % 3 else FIRE[6], L)
    own = set(cells[0])
    keep(p, own)
    if night:
        glow(p, cx, foot - h * 0.45, h * 0.62, h * 0.75, FIRE[3], (0.08, 0.16, 0.26), L=p.flicker(0, back=True))
        if not motion:
            for (dx, dy) in ((-3, 4), (2, 9), (4, 15)):
                p.px(cx + dx, foot - h - 2 - dy, FIRE[5], "base")
    return own


def smoke(p: Pix, cx, y0, y1, night: bool, motion: bool, width=7):
    """The smoke going up from the fire from row y0 to row y1 about column cx toward the smoke hole in the roof:
    wisps that waver as they rise and thin as they go, grey by day and by night warm where the fire lights them
    from under, fewer of them on a drawing made lighter. In a moving header the column of wisps rises, a third of
    its height a step, and comes round; drawn once, it is placed twice, one copy following the other, inside the
    column's own bounds."""
    rnd = random.Random(17)
    h = y0 - y1
    cells = {}
    for _ in range(8 if p.lite else 12):
        t, side, n = rnd.random(), rnd.uniform(-1, 1), rnd.randint(2, 4)
        y = round(h * (1 - t))
        x = round(side * width * (0.4 + t) + 2.2 * math.sin(t * 7 + side * 3))
        col = (FIRE[3] if t < 0.25 else SMOKE[3]) if night else SMOKE[4 if t < 0.5 else 5]
        a = round((0.5 if night else 0.55) * (1 - t * 0.8), 2)
        for k in range(n):
            cells[(x + k, y)] = f"{col}:{a}"
    sid = f"sm{len(p.defs)}"
    p.defs.append(f'<g id="{sid}">{paths(cells)}</g>')
    keep(p, {(cx + x, y1 + y) for (x, y) in cells})
    still = f'<use href="#{sid}" x="{cx}" y="{y1}"/>'
    if not motion:
        p.raw(0.75, still, still)
        return
    cid = f"{sid}c"
    steps = ";".join(f"0 {-round(h * i / 6)}" for i in range(6))
    moving = (f'<clipPath id="{cid}"><rect x="{cx - 3 * width}" y="{y1}" width="{6 * width}" height="{h}"/></clipPath>'
              f'<g clip-path="url(#{cid})"><g transform="translate({cx} {y1})"><g><use href="#{sid}"/>'
              f'<use href="#{sid}" y="{h}"/><animateTransform attributeName="transform" type="translate" '
              f'values="{steps}" dur="4.2s" repeatCount="indefinite" calcMode="discrete"/></g></g></g>')
    p.raw(0.75, moving, still)


def stones(p: Pix, x0, x1, top, foot, night: bool, seed=0, L="base"):
    """A kerb of rounded stones laid edge to edge from x0 to x1 between rows top and foot, each lit on its upper
    left and dark at its foot, flecked, with deep cracks between them; on a drawing made lighter each stone in two
    tones, unflecked."""
    rnd = random.Random(seed)
    k = -1 if night else 0
    x = x0
    h = foot - top
    while x < x1:
        w = min(x1 - x, rnd.randint(7, 11))
        if x1 - (x + w) < 5:
            w = x1 - x
        rx, ry = w / 2, h / 2
        for yy in range(top, foot):
            for xx in range(x, x + w):
                dx, dy = (xx + 0.5 - x - rx) / rx, (yy + 0.5 - top - ry) / ry
                d = dx ** 4 + dy ** 4
                if d > 1:
                    continue
                if d > 0.62:
                    c = STONE[0]
                else:
                    lam = -0.6 * dx - 0.8 * dy
                    if p.lite:
                        t = 5 if lam > 0.3 else 3
                    else:
                        t = 5 if lam > 0.55 else 4 if lam > 0.05 else 3 if lam > -0.45 else 2
                    if (xx * 7 + yy * 3 + seed) % 11 == 0 and not p.lite:
                        t -= 1
                    c = STONE[max(1, t + k)]
                p.px(xx, yy, c, L)
        x += w


# The drinking horn hung on the hall's post by a sling of leather from a peg: a cow's horn lying in the sling, its
# mouth banded in gilt and dark inside, curving to its tip capped in gilt, mottled as horn is. K its outline, 6 to 2
# the horn from its palest to its dark foot, g G gilt, m its mouth, o the peg, l L the strap.
HORN = [
    "Ko......................",
    "KoK.....................",
    ".KlK....................",
    "..lLL...................",
    "..l..LL.................",
    "..l....LL...............",
    "..l......LL.............",
    ".KgK.......LL...........",
    "KgGGK........LL.........",
    "KGmmGK.........LL.....K.",
    "KGmmmGK..........LL..KgK",
    ".KGmmGK............LLKGK",
    "..KGggGK..........KK66K.",
    "...K665KKK.....KKK6654K.",
    "....K66555KKKKK6655543K.",
    ".....K66655555544443K...",
    "......KK66554443332K....",
    "........KKK44332KKK.....",
    "...........KKKK.........",
]
# The dragon's head carved on the top of the hall's post, its neck rising from the post and turning to face across
# the hall, its crest curled back, its eye gilt, its jaws open on its teeth. K the cut, 6 to 1 the oak, e the gilt
# eye, w a tooth.
DRAGON_HEAD = [
    "..KKK.............",
    ".K665K............",
    ".K6K5K.KKKK.......",
    "..K55KK6655KK.....",
    "...K66KeK5544KKK..",
    "...K665K55444433K.",
    "...K665444KKKKK43K",
    "...K665KKKwKwKwKK.",
    "...K654K.KK4K4KK..",
    "...K654K..K4443K..",
    "..K6654K...KKKK...",
    "..K6543K..........",
    ".K66543K..........",
    ".K65432K..........",
]
# A round shield hung on the wall, painted in quarters of red and ivory, bound in iron round its rim, its iron boss
# in the middle.
ROUND_SHIELD = [
    "....KKKKK....",
    "..KKRRR66KK..",
    ".KRRRRR6666K.",
    ".KRRRRR6665K.",
    "KRRRRKKK6655K",
    "KRRRKiIiK655K",
    "KRRRKIiiK554K",
    "K665KiiiKRRRK",
    "K6655KKKRRRRK",
    ".K6555RRRRRK.",
    ".K6554RRRRRK.",
    "..KK54RRRKK..",
    "....KKKKK....",
]
# A low bench of oak on the hall's floor, its seat lit along its edge, on two stout legs.
BENCH = [
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKK",
    "K66666655555555555444444443K",
    "K54444444444444443333333322K",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKK",
    "..K54K................K43K..",
    "..K54K................K43K..",
    "..K54K................K43K..",
    ".KK54KK..............KK43KK.",
]
# The iron cauldron hung over the fire on its pot-chain: its hook, its rim lit, its lugs, its belly dark.
CAULDRON = [
    "........KK........",
    ".......K55K.......",
    "........KK........",
    "..KKKKKKKKKKKKKK..",
    ".K66666655554443K.",
    "KK5KKKKKKKKKKK2KKK",
    "K6K555444443332K1K",
    "K65544444433332211",
    "K55444444333322211",
    "K54444443333222211",
    ".K444443333222211K",
    ".K433333332222111K",
    "..K3332222221111K.",
    "...KKKKKKKKKKKKK..",
]
# The gaming purse: a pouch of leather, its neck gathered by a gilt-tipped thong, open and spilling its tablemen.
PURSE = [
    "......KK.KK.....",
    ".....K65K54K....",
    "......KKKKK.....",
    ".....K6l5lK.....",
    "....K665544K....",
    "...K66555544K...",
    "..K6655554443K..",
    ".K665555444433K.",
    ".K655544444332K.",
    "K6555444443332K.",
    "K6554444433322K.",
    ".K54444333222K..",
    "..KK4433222KK...",
    "....KKKKKKK.....",
]
# A tableman lying on the floor seen from the front: a round counter, its rim lit, a ring cut in its face.
TABLEMAN = [".KKKK.", "K6655K", "K5KK4K", ".KKKK."]


def post(p: Pix, x, top, foot, night: bool, L="base"):
    """The hall's post of oak from row `top` to its foot at row `foot`, 6 wide from x: lit down its left, dark down
    its right, a band carved round it every so often (the bands left smooth on a drawing made lighter)."""
    k = -1 if night else 0
    for y in range(top, foot):
        band = (y - top) % 18 if not p.lite else 9
        tones = (OAK[0], OAK[6 + k], OAK[5 + k], OAK[4 + k], OAK[3 + k], OAK[0])
        if band == 0:
            tones = (OAK[0], OAK[6 + k], OAK[6 + k], OAK[5 + k], OAK[4 + k], OAK[0])
        elif band in (1, 2):
            tones = (OAK[0], OAK[3 + k], OAK[2], OAK[2], OAK[1], OAK[0])
        for i, c in enumerate(tones):
            p.px(x + i, y, c, L)


def horn(p: Pix, x, y, night: bool, L="base"):
    """The drinking horn hung in its sling from the peg at (x, y) on the hall's post."""
    k = -1 if night else 0
    pal = {"K": OAK[0], "6": HO[6 + k], "5": HO[5 + k], "4": HO[4 + k], "3": HO[3 + k], "2": HO[1], "g": GILT[5 + k],
           "G": GILT[3 + k], "m": OAK[0], "o": OAK[5 + k], "l": LEATHER[4 + k], "L": LEATHER[3 + k]}
    stamp(p, x, y, HORN, pal, L)


def dragon_head(p: Pix, x, y, night: bool, L="base"):
    """The dragon's head carved on the top of the hall's post, its top left at (x, y)."""
    k = -1 if night else 0
    stamp(p, x, y, DRAGON_HEAD, {"K": OAK[0], "e": GILT[5 + k], "w": IV[6 + k],
                                 **{str(t): OAK[max(1, t + k)] for t in range(1, 7)}}, L)


def round_shield(p: Pix, x, y, night: bool, L="base"):
    """A round shield hung on the wall, its top left at (x, y)."""
    k = -1 if night else 0
    stamp(p, x, y, ROUND_SHIELD, {"K": IRON[0], "R": RD[3 + k], "i": IRON[3 + k], "I": IRON[5 + k],
                                  **{str(t): IV[max(1, t + k)] for t in range(1, 7)}}, L)


def bench(p: Pix, x, foot, night: bool, L="base"):
    """A low bench of oak standing on the floor with its feet on the row above `foot`, from column x."""
    k = -1 if night else 0
    stamp(p, x, foot - len(BENCH), BENCH, {"K": OAK[0], **{str(t): OAK[max(1, t + k)] for t in range(1, 7)}}, L)


BENCH_W = len(BENCH[0])


def cauldron(p: Pix, cx, top, bottom, night: bool, L="base"):
    """The iron cauldron hung on its pot-chain from the roof, the chain from row `top`, the pot's foot at row
    `bottom`, about column cx; on a drawing made lighter the chain's links run together into one bar."""
    k = -1 if night else 0
    y0 = bottom - len(CAULDRON)
    for y in range(top, y0 + 1):
        link = (y - top) % 3 if not p.lite else 2
        p.px(cx, y, IRON[4 + k] if link else IRON[1], L)
        p.px(cx + 1, y, IRON[2 + k] if link == 1 else IRON[3 + k] if link else IRON[1], L)
    stamp(p, cx - 8, y0, CAULDRON, {"K": IRON[0], **{str(t): IRON[max(1, t + k)] for t in range(1, 7)}}, L)


def purse(p: Pix, x, foot, night: bool, L="base", spill=True):
    """The gaming purse, open on the floor with its foot on the row above `foot` from x, and the tablemen spilled
    out of it, ivory and red: across the floor beside it, or where the room is close, in a heap at its mouth."""
    k = -1 if night else 0
    stamp(p, x, foot - len(PURSE), PURSE, {"K": LEATHER[0], "l": GILT[4 + k],
                                          **{str(t): LEATHER[max(1, t + k)] for t in range(1, 7)}}, L)
    spilled = ((14, 0), (19, 1), (16, -3), (21, -3)) if spill else ((9, 0), (5, 1), (11, -3))
    for i, (dx, dy) in enumerate(spilled):
        R = IV if i % 2 == 0 else RD
        stamp(p, x + dx, foot - 4 + dy, TABLEMAN, {"K": R[0], "6": R[6 + k], "5": R[5 + k], "4": R[4 + k]}, L)


def tripod(p: Pix, cx, apex, g, night: bool, spread=20, L="base"):
    """An iron tripod over the fire, its legs from the floor at row g splayed out from cx to its apex at row `apex`,
    the near leg lit and the far ones in shade."""
    k = -1 if night else 0
    n = g - apex
    for side, t in ((-1, 5), (1, 3)):
        for j in range(n):
            x = round(cx + side * spread * j / n)
            p.px(x, apex + j, IRON[t + k], L)
            p.px(x + side, apex + j, IRON[1], L)
    p.px(cx, apex - 1, IRON[5 + k], L)
    p.px(cx + 1, apex - 1, IRON[2 + k], L)


def hearth(p: Pix, x0, g, night: bool, motion: bool, top=13, compact=False, spill=True, wall=2):
    """The hearth of the hall on the floor at row g from x0, 56 wide: the hall's post at its left, a dragon's head
    carved on its top and the drinking horn hung in its sling below it, and a round shield hung on the wall beyond
    the pot's chain (the head and the shield as the rows and `wall` allow, the horn always); the long fire laid on
    its bed of embers between two kerbs of stones, logs crossed in it; the iron cauldron hung over it on its chain
    from the roof (from row `top`); the smoke going up round the pot; and the gaming purse open on the floor before
    the kerb with its tablemen spilled. By night the fire is the only light: its glow in the air, a pool of its
    light on the ivory round it and its light on the stones, the pot, the post, the horn and the purse. A
    `compact` hearth, where no roof is overhead to hang the pot from, sets it on an iron tripod over the fire, the
    post as tall as the room. Returns the span of the rule it covers."""
    k = -1 if night else 0
    post(p, x0, top, g + 1, night)
    y = top + 1
    if wall >= 1 and y + 15 + len(HORN) <= (g - 46 if compact else g - 39):
        dragon_head(p, x0 + 2, y, night)
        y += 15
    horn(p, x0 + 4, y, night)
    if wall >= 2 and not compact:
        round_shield(p, x0 + 35, top + 6, night)
    kx0, kx1 = x0 + 8, x0 + 50
    cx = (kx0 + kx1) // 2
    stones(p, kx0 + 4, kx1 - 4, g - 14, g - 8, night, seed=3)
    every = 7 if p.lite else 3
    for x in range(kx0 + 2, kx1 - 2):
        for y in range(g - 10, g - 7):
            fleck = (x + y) % every == 0
            p.px(x, y, (FIRE[1] if fleck else FIRE[2]) if night else (SMOKE[3] if fleck else HALL[5]))
    for i, (a, b) in enumerate(((kx0 + 6, kx1 - 12), (kx0 + 12, kx1 - 6))):
        n = b - a
        for j, x in enumerate(range(a, b)):
            y = g - 12 + (j if i == 0 else n - 1 - j) * 3 // max(1, n)
            p.px(x, y, OAK[4 + k])
            p.px(x, y + 1, OAK[2 + k])
            p.px(x, y + 2, OAK[1])
        end = a if i == 0 else b - 1
        p.px(end, g - 11, FIRE[4] if night else OAK[5 + k])
    own = fire(p, cx, g - 9, night, motion)
    if compact:
        cauldron(p, cx, g - 44, g - 25, night)
        tripod(p, cx, g - 45, g - 6, night)
    else:
        cauldron(p, cx, top, g - 25, night)
    stones(p, kx0, kx1, g - 8, g, night, seed=8)
    purse(p, kx1 - 14, g + 1, night, spill=spill)
    smoke(p, cx, g - 40, max(top + 2, g - 64) if not compact else max(top, g - 56), night, motion, width=9)
    if night:
        glow(p, cx, g - 18, 56, 40, FIRE[2], (0.05, 0.1, 0.16))
        lamp(p, cx, g - 16, 42, own)
    return (x0 - 1, kx1 + 12)


# --------------------------------------------------------------------------- the great pieces
def great(p: Pix, kind: str, side: str, b: Board, f, r, night: bool, face=1):
    """One of the great pieces standing on a stretch of the board on file f, rank r, drawn once and placed."""
    x, y = b.at(f, r)
    return piece(p, kind, side, x, y, night, face=face, reuse=True)


def dais(p: Pix, x0, x1, g, sq, night: bool, pieces, ranks=2, files=8):
    """A stretch of the board `ranks` ranks deep and `files` files long, its near edge from x0 on the floor at row g
    and cut off at x1, its squares `sq` wide, and the great pieces `pieces` standing on it, each (kind, side, file,
    rank), their shadows on the squares under them: short by day and, by night, thrown long away from the hearth on
    the left."""
    b = Board(x0, g - 5, sq, round(sq * 0.4 * ranks), shrink=0.93, files=files)
    shade = set()
    for kind, side, f, r in pieces:
        shade |= shadow_cells(b, f, r, night)
    board_squares(p, b, night, x1, shade, ranks=ranks)
    boxes = [great(p, kind, side, b, f, r, night) for kind, side, f, r in sorted(pieces, key=lambda q: -q[3])]
    return b, boxes


# The court a section's header stands at its right, by how much of the floor the words leave it: the whole court
# across the floor, the showpieces of the king with the berserker before him, or the king alone, and where the
# header is too low for the showpieces, the same at the great pieces' smaller size. Each is (files, ranks, pieces),
# every piece (kind, side, file, rank) on a stretch of the board 18 wide a square.
COURTS = {
    "spread": (15, 4, (("pawn_m", "ivory", 0.8, 1.2), ("knight_m", "ivory", 2.5, 0.6), ("queen_m", "red", 4.5, 1.9),
                       ("pawn_m", "red", 6.2, 0.8), ("bishop_m", "ivory", 7.9, 1.6),
                       ("berserker_xl", "red", 10.4, 0.25), ("king_xl", "ivory", 13.1, 0.7))),
    "wide": (5, 4, (("berserker_xl", "red", 0.75, 0.25), ("king_xl", "ivory", 3.3, 0.8))),
    "narrow": (4, 3, (("king_xl", "ivory", 2.2, 0.6),)),
    "wide_l": (4, 5, (("berserker_l", "red", 0.7, 0.6), ("king_l", "ivory", 2.75, 3.1))),
    "narrow_l": (2, 3, (("king_l", "ivory", 1.2, 1.6),)),
}
# The same for a strip's queen, 16 wide a square: the queen with her own pieces before her and the red side's
# coming on across the floor, the queen with a red pawn on the square before her, or the queen alone; and the same
# with the queen at her smaller size where the strip is too low for her full one.
SEATS = {
    "spread": (13, 3, (("pawn_m", "red", 1.2, 1.2), ("knight_m", "red", 3.0, 0.6), ("pawn_m", "ivory", 5.2, 1.4),
                       ("bishop_m", "ivory", 7.1, 0.7), ("pawn_m", "red", 9.2, 0.3), ("queen_xl", "ivory", 11.3, 0.4))),
    "wide": (4, 2, (("pawn_m", "red", 0.55, 0.2), ("queen_xl", "ivory", 2.55, 0.4))),
    "narrow": (3, 2, (("queen_xl", "ivory", 1.55, 0.4),)),
    "wide_l": (3, 2, (("pawn", "red", 0.5, 0.2), ("queen_l", "ivory", 1.85, 0.5))),
    "narrow_l": (2, 2, (("queen_l", "ivory", 1.1, 0.5),)),
}
COURT_ORDER = ("spread", "wide", "narrow", "wide_l", "narrow_l")


def court(p: Pix, x1, g, night: bool, layout: str):
    """The right of a section's header, ending at column x1 on the floor at row g: the ivory king on his throne,
    large, set back on a stretch of the board; where the room runs wide the red berserker before him biting his
    shield; and where the words leave the whole floor the court across it, a knight, a bishop, pawns and the red
    queen standing back across the board from him (see COURTS). Returns the span of the rule it covers."""
    files, ranks, pieces = COURTS[layout]
    x0 = x1 - files * 18 - (6 if files > 2 else 4)
    dais(p, x0, x1, g, 18, night, list(pieces), ranks=ranks, files=max(8, files + 1))
    return (x0 - 3, x1 + 1)


def queen_seat(p: Pix, x1, g, night: bool, layout: str):
    """The right of a strip's header, ending at column x1 on the floor at row g: the ivory queen on her throne, her
    hand to her cheek, on a stretch of the board; where the room runs wide a red pawn on the square before her; and
    where the words leave the whole floor her bishop and her pawns before her and the red side coming on across the
    board (see SEATS). Returns the span of the rule it covers."""
    files, ranks, pieces = SEATS[layout]
    x0 = x1 - files * 16 - 4
    dais(p, x0, x1, g, 16, night, list(pieces), ranks=ranks, files=max(8, files + 1))
    return (x0 - 3, x1 + 1)


# --------------------------------------------------------------------------- a phone's scenes
def phone_hall(p: Pix, g, night: bool, room: int):
    """A phone's hall on the floor at row g, in the `room` rows its words leave over it: the hearth at the left,
    its pot on a tripod over the fire and the horn hung on its post, and at the right the game on its table, staged
    for a phone (see STAGES), the knight on his first square."""
    hearth(p, 6, g, night, False, top=g - room, compact=True)
    staged_game(p, NARROW_RIGHT, g, night, False, "phone")


NARROW_RIGHT = 176  # the right edge of a phone's scene, inside its frame


def phone_court(p: Pix, g, night: bool):
    """A section's court across a phone, under its words: the showpieces, the ivory king on his throne set back on a
    stretch of the board and the red berserker before him biting his shield, an ivory pawn at the board's edge."""
    sq = 18
    x1 = NARROW_RIGHT
    x0 = x1 - 8 * sq
    dais(p, x0, x1, g, sq, night, [("pawn_m", "ivory", 0.4, 0.5), ("berserker_xl", "red", 2.3, 0.3),
                                     ("king_xl", "ivory", 5.6, 0.8)], ranks=3)


def phone_queen(p: Pix, g, night: bool):
    """A strip's queen across a phone, under its words: the ivory queen on her throne at her full size, her hand to
    her cheek, on a stretch of the board, a red pawn and the red knight before her."""
    sq = 16
    x1 = NARROW_RIGHT
    x0 = x1 - 9 * sq
    dais(p, x0, x1, g, sq, night, [("knight_m", "red", 1.6, 0.5), ("pawn_m", "red", 3.9, 0.3),
                                     ("queen_xl", "ivory", 6.6, 0.8)], ranks=2)


# --------------------------------------------------------------------------- the footer: the board's edge
def turned(rows: list, q: int = 1) -> list:
    """Pixel art turned a quarter round clockwise `q` times: a piece laid on its side."""
    for _ in range(q % 4):
        rows = ["".join(rows[len(rows) - 1 - j][i] for j in range(len(rows))) for i in range(len(rows[0]))]
    return rows


# The king at a smaller size, for the toppled king of checkmate at the corner of a footer's notes: crowned on his
# throne, his eyes staring, his sword across his knees.
KING_S = [
    "...K.K.K...",
    "..K6K6K5K..",
    "..K66654K..",
    ".KKKKKKKKK.",
    "K5K56565K2K",
    "K5K6e6e4K2K",
    "K5K55554K2K",
    "K5K53334K2K",
    "K5KK545KK2K",
    "K56666665KK",
    "K3K44433K1K",
    "K3K54433K1K",
    "K3K54333K1K",
    "K3KK5KK3K1K",
    "K655554433K",
    "KKKKKKKKKKK",
]
# The pieces taken in the game, laid on their sides beside the board, largest first: (kind, side, quarter turns).
CAPTURED = (("pawn_s", "red", 1), ("pawn_s", "ivory", 3), ("pawn_s", "red", 3), ("pawn_s", "ivory", 1),
            ("pawn_xs", "red", 1), ("pawn_xs", "ivory", 3))
# A candle in its iron pricket, lit by night: its flame, the wax, the pricket's dish and foot.
CANDLE = ["..f..", ".fFf.", ".fFf.", "..w..", ".WwW.", ".Www.", ".Www.", ".Www.", "IiiiI", ".IiI.", "IIIII"]


def laid(p: Pix, kind: str, side: str, q: int, x, foot, night: bool):
    """A piece laid on its side with its lowest row on the row above `foot` from x. Returns its (w, h)."""
    rows = turned(PIECES[kind], q)
    cells = piece_cells(rows, side, night)
    h = len(rows)
    for (i, j), c in cells.items():
        p.px(x + i, foot - h + j, c)
    return len(rows[0]), h


def size_laid(kind: str) -> tuple:
    """The width and height of a piece laid on its side."""
    rows = PIECES[kind]
    return len(rows), len(rows[0])


def candle(p: Pix, x, foot, night: bool):
    """A candle in its iron pricket on the row above `foot` from x, its flame lit by night and its light round it."""
    k = -1 if night else 0
    pal = {"I": IRON[3 + k], "i": IRON[5 + k], "W": IV[6 + k], "w": IV[4 + k]}
    if night:
        pal.update({"f": FIRE[4], "F": FIRE[6]})
    stamp(p, x, foot - len(CANDLE), CANDLE, pal)
    if night:
        cx, cy = x + 2.5, foot - len(CANDLE) + 1.5
        p.halo(cx, cy, 9, 8, FIRE[3], (0.1, 0.2, 0.32), L=p.flicker(1, back=True))
        lamp(p, cx, cy, 16, {(x + i, foot - len(CANDLE) + j) for j in range(3) for i in range(5)})


def edge_band(p: Pix, tops: list, night: bool, face: int):
    """The board's edge along a footer's foot from row `face`, its top at column x at row `tops[x]`: where it lies
    lowest its face alone, squares of ivory and of red bone by turns, lit along their tops and darkening to their
    feet; where it rises, the board's surface over its face, squares of ivory inlay and dark oak in a rank or two."""
    w, h = p.w, p.h
    k = -2 if night else 0
    deep = h - face
    for x in range(w):
        t = tops[x]
        red = (x // 4) % 2 == 1
        R, tones = (RD, (5, 3, 2, 1)) if red else (IV, (6, 5, 4, 3))
        tones = tones[:deep - 1] + tones[-1:]
        for j in range(deep):
            p.px(x, face + j, R[max(1, tones[j] + k)])
        for y in range(t, face):
            rank = (face - 1 - y) // 2
            light = ((x // 6) + rank) % 2 == 0
            c = (IV[3 if night else 5] if light else OAK[1 if night else 3])
            if y == t:
                c = IV[2 if night else 6] if light else OAK[2 if night else 4]
            p.px(x, y, c)
        if t < face:
            p.px(x, t - 1, IV[0]) if t - 1 >= 0 else None
    keep(p, {(x, y) for x in range(w) for y in range(tops[x] - (1 if tops[x] < face else 0), h)})


RISE = 2            # the rows the board's edge rises over its face where a footer's cells leave it room: a rank
RUN = 24            # the fewest columns a stretch of the edge rises along


def _free_rows(p: Pix, x, top, most, boxes) -> int:
    """The rows over row `top` at column x clear of every word by two rows and of anything else drawn, up to
    `most`."""
    base = p.layers["base"]
    n = 0
    while n < most:
        y = top - 1 - n
        if y < 6 or (x, y) in base or not p.clear_of_words(x - 1, y - 2, x + 2, y + 1) \
                or any(a <= x < c and b <= y < d for a, b, c, d in boxes):
            break
        n += 1
    return n


def toppled(p: Pix, x, foot, night: bool, big=False):
    """The toppled king of checkmate lying on his side with his crown to the left, his lowest row on the row above
    `foot` from x, and by night a candle burning behind him, its flame showing over him: the king of the board's own
    size where the footer leaves him room, else the smaller king."""
    rows = turned(KING if big else KING_S, 3)
    if night:
        dx, dy = (10, 7) if big else (6, 2)
        candle(p, x + dx, foot - dy, night)
    cells = piece_cells(rows, "ivory", night)
    for (i, j), c in cells.items():
        p.px(x + i, foot - len(rows) + j, c)
    keep(p, {(x + i, foot - len(rows) + j) for (i, j) in cells})


# The king lying, larger and smaller, and the flame of his candle over him: (width, height) of each.
TOPPLED = {True: (len(KING), len(KING[0]) + 4), False: (len(KING_S), len(KING_S[0]) + 9)}


def _clear_box(p: Pix, x0, y0, x1, y1) -> bool:
    """Whether the box from (x0, y0) to (x1, y1), ends excluded, keeps two units from every word and lies on nothing
    drawn but the paper."""
    base = p.layers["base"]
    return p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and not any(
        (x, y) in base for x in range(x0, x1) for y in range(y0, y1))


RANK_ROOM = 24      # the rows a rank of the board and the pieces standing on it need over a footer's foot
RANK_MIN = 70       # the fewest columns a footer's rank is laid along
RANK_SQ = 11        # a square of a footer's rank
# The pieces taken in the game, standing in a row on a footer's rank, as many as its length holds.
TAKEN = (("pawn", "red", 1), ("knight", "ivory", 1), ("pawn", "ivory", -1), ("bishop", "red", -1),
         ("berserker", "ivory", 1), ("pawn", "red", -1), ("queen", "red", -1))


def _rank_stretch(p: Pix, face) -> tuple | None:
    """The longest run of columns along a footer's foot with RANK_ROOM rows clear over it, if it is RANK_MIN long."""
    w = p.w
    free = [_free_rows(p, x, face - 1, RANK_ROOM, []) >= RANK_ROOM if 6 < x < w - 7 else False for x in range(w)]
    best, x = None, 0
    while x < w:
        if not free[x]:
            x += 1
            continue
        b = next((i for i in range(x, w) if not free[i]), w)
        if b - x >= RANK_MIN and (best is None or b - x > best[1] - best[0]):
            best = (x, b)
        x = b
    return best


def footer_rank(p: Pix, x0, x1, face, night: bool) -> tuple:
    """A short rank of the board laid along a footer's foot from column x0 to x1, where its cells leave the room: a
    rank of squares in perspective on the board's edge, the pieces taken in the game standing on it in a row, red
    and ivory, each throwing its shadow on the squares, and the toppled king of checkmate lying across its end, his
    candle burning beside him by night. Returns the span it covers."""
    kw, kh = TOPPLED[True]
    files = max(2, (x1 - x0 - 2) // RANK_SQ)
    x0 = x1 - 1 - files * RANK_SQ
    b = Board(x0, face, RANK_SQ, 40, shrink=0.94, files=files)
    standing = []
    fx = 0.6
    for kind, side, face_ in TAKEN:
        wide = len(PIECES[kind][0]) / RANK_SQ
        if x0 + (fx + wide) * RANK_SQ > x1 - kw - 6:
            break
        standing.append((kind, side, fx + wide / 2 - 0.5, 0.45, face_))
        fx += wide + 0.45
    shade = set()
    for kind, side, f, r, _ in standing:
        shade |= shadow_cells(b, f, r, night)
    board_squares(p, b, night, x1, shade, ranks=2)
    for kind, side, f, r, fc in standing:
        x, y = b.at(f, r)
        piece(p, kind, side, x, y, night, face=fc, reuse=True)
    toppled(p, x1 - kw - 3, face - 1, night, big=True)
    return (x0 - 2, x1 + 2)


def footing(p: Pix, night: bool, rule: str):
    """A footer once its words are set: the board's edge along its foot, four rows deep, or as few as two where the
    lowest word comes down nearer the foot, rising by up to RISE rows into a rank or two of the board's squares
    wherever the cells leave it room along RUN columns or more, the ruled lines between
    the cells standing on it; at the corner of the notes, on the board's edge or on the rule under them, the toppled
    king of checkmate lying on his side, at the board's own size where a cell has room for him, a candle burning
    behind him by night; and the pawns taken in the game laid on their sides beside the board wherever the room over
    its edge lets them lie."""
    w, h = p.w, p.h
    base = p.layers["base"]
    face = min(h - 2, max(h - 4, max((b[3] for b in p.words), default=0) + 1))
    stretch = _rank_stretch(p, face)
    room = [_free_rows(p, x, face, RISE + 14, []) if 5 < x < w - 5 and not (stretch and stretch[0] - 2 <= x <
                                                                              stretch[1] + 2) else 0 for x in range(w)]
    ruled = {x for x in range(5, w - 5) if sum(base.get((x, y)) == rule for y in range(face - RISE - 2, face)) >= 2}
    tops = [face] * w
    x = 5
    while x < w - 5:
        if room[x] < 3 or x in ruled:
            x += 1
            continue
        b = next((i for i in range(x, w - 5) if room[i] < 3 or i in ruled), w - 5)
        if b - x >= RUN:
            rise = min(RISE, min(room[i] for i in range(x, b)) - 1)
            tops[x:b] = [face - rise] * (b - x)
        x = b
    for xy in [xy for xy, c in base.items() if c == rule and xy[1] >= face - 1]:
        del base[xy]
    taken = []
    mark = getattr(p, "mark_at", None)
    if stretch:
        taken.append(footer_rank(p, stretch[0], stretch[1], face, night))
    elif mark:
        mx, my = mark
        floors = sorted({tops[x] for x in range(max(5, mx - 40), min(w - 5, mx + 2))}, reverse=True)
        floors += [y for y in range(h - 5, my, -1) if all(base.get((xx, y)) == rule for xx in range(mx - 30, mx - 2))]
        placed = False
        for big in (True, False):
            kw, kh = TOPPLED[big]
            for foot in floors:
                for x in range(min(mx - kw, w - 6 - kw), mx - kw - 26, -1):
                    if foot - kh > my - 6 and _clear_box(p, x - 1, foot - kh, x + kw + 1, foot):
                        toppled(p, x, foot, night, big=big)
                        taken.append((x - 2, x + kw + 2))
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
    edge_band(p, tops, night, face)
    i, x = 0, 8
    while x < w - 8 and i < len(CAPTURED):
        kind, side, q = CAPTURED[i]
        kw, kh = size_laid(kind)
        t = min(tops[x:x + kw])
        clear = not any(a <= x + kw and x <= b for a, b in taken) and _clear_box(p, x - 1, t - kh - 2, x + kw + 1,
                                                                                    t - 1)
        if not clear:
            x += 2
            continue
        laid(p, kind, side, q, x, t, night)
        taken.append((x - 2, x + kw + 2))
        x += kw + 10
        i += 1
    if night:
        firelight(p)


# --------------------------------------------------------------------------- links: tablemen
# The icons carved in a link's tableman, 9 by 7: a pawn, a crown, a knight's horse's head, a bishop's mitre. # is the
# carving.
LINK_ICONS = {
    "pawn": ["...###...", "..#####..", "...###...", "....#....", "...###...", "..#####..", ".#######."],
    "crown": ["#...#...#", "##.###.##", "#########", "#.##.##.#", "#########", ".#######.", "........."],
    "knight": ["...##....", "..#####..", ".###.###.", "######...", "...####..", "..######.", ".#######."],
    "mitre": ["....#....", "...###...", "..##.##..", "..##.##..", "..#####..", "..##.##..", ".#######."],
}
LINK_ORDER = ("crown", "knight", "mitre", "pawn")


LINK_TEXT = 19      # the column a link's label starts at, clear of its tableman


def tableman_link(p: Pix, index: int, night: bool):
    """A link button as a tableman on its tag: the round gaming counter at the left, of ivory or of bone stained red
    by turns, its rim lit on its upper left and shaded on its lower right and its face polished, the button's icon
    carved in it; behind it a tag of ivory the label is lettered on, its edge outlined, lit along its top and
    shaded along its foot."""
    w = p.w
    k = -1 if night else 0
    R = IV if index % 2 == 0 else RD
    for y in range(2, 13):
        for x in range(10, w):
            edge = y in (2, 12) or x == w - 1
            if (x == w - 1) and y in (2, 12):
                continue
            p.px(x, y, IV[0] if edge else IV[6 + k] if y == 3 else IV[3 + k] if y == 11 else IV[5 + k])
    cx, cy, r = 9.0, 6.5, 6.5
    for y in range(13):
        for x in range(17):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d > r:
                continue
            lit = (x + 0.5 - cx) * -0.6 + (y + 0.5 - cy) * -0.8
            if d > r - 1:
                c = R[0]
            elif d > r - 2:
                c = R[6 + k] if lit > 1 else R[3 + k] if lit < -1 else R[5 + k]
            else:
                c = (R[5 + k] if lit > -0.5 else R[4 + k]) if R is IV else (R[4 + k] if lit > -0.5 else R[3 + k])
            p.px(x, y, c)
    rows, pal = link_icon(index, night)
    stamp(p, 5, 3, rows, pal)


def link_icon(index: int, night: bool) -> tuple:
    """The icon carved in a link's tableman and the colour of its cut: dark in the ivory, and in the red bone the pale
    of the ivory under the stain."""
    R = IV if index % 2 == 0 else RD
    cut = IV[1] if R is IV else IV[6 - (1 if night else 0)]
    return LINK_ICONS[LINK_ORDER[index % len(LINK_ORDER)]], {"#": cut}


# --------------------------------------------------------------------------- the rule: a rank of the board inlaid
def rank_inlay(p: Pix, x0, x1, y, night: bool, L="base"):
    """Along a rule at row y from x0 to x1, a rank of the board inlaid in the ivory over it: a strip of small squares
    of ivory and of red bone by turns, three rows deep, lit along their tops and shaded toward the rule, set in a
    dark cut along its top and its ends; laid only where no word lies within two units, each run beginning and
    ending on a whole square."""
    k = -1 if night else 0
    ok = [p.clear_of_words(x - 2, y - 6, x + 3, y + 1) for x in range(x0, x1)]
    runs, start = [], None
    for i, good in enumerate(ok + [False]):
        if good and start is None:
            start = i
        elif not good and start is not None:
            a = x0 + start + 1
            a += (-a) % 4
            b = x0 + i - 1
            b -= b % 4
            if b - a >= 8:
                runs.append((a, b))
            start = None
    for a, b in runs:
        for x in range(a - 1, b + 1):
            p.px(x, y - 4, IV[1], L)
        for x in range(a, b):
            red = (x // 4) % 2 == 1
            R = RD if red else IV
            p.px(x, y - 3, R[(5 if red else 6) + k], L)
            p.px(x, y - 2, R[(4 if red else 5) + k], L)
            p.px(x, y - 1, R[(2 if red else 3) + k], L)
        for yy in range(y - 3, y):
            p.px(a - 1, yy, IV[1], L)
            p.px(b, yy, IV[1], L)


# --------------------------------------------------------------------------- the elements
def tableman_disc(p: Pix, cx, cy, r, night: bool, red=False, L="base"):
    """A tableman seen face on, about (cx, cy) with radius r: its rim lit on its upper left and shaded on its lower
    right, a ring cut round its face, its face polished. Ivory, or bone stained red."""
    k = -1 if night else 0
    R = RD if red else IV
    cells = {}
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d > r:
                continue
            lit = ((x + 0.5 - cx) * -0.6 + (y + 0.5 - cy) * -0.8) / max(1.0, r)
            if d > r - 1:
                c = R[0]
            elif d > r - 2:
                c = R[6 + k] if lit > 0.3 else R[3 + k] if lit < -0.3 else R[5 + k]
            elif r >= 5 and r - 2.9 < d <= r - 2:
                c = R[3 + k]
            else:
                c = R[5 + k] if not red else R[4 + k]
            cells[(x, y)] = c
            p.px(x, y, c, L)
    return cells


def tablet_card(p: Pix, x, y, w, h, night: bool, ink: str, seed=0, lid=True):
    """A schematic's card as a tablet of ivory: at its left its icon carved in a tableman, of bone stained red and of
    ivory by turns (the layout drew the icon in `ink`, which this takes up and carves again, pale through the stain
    and dark in the ivory); and along its lid a rank of the board inlaid, squares of ivory and of red bone by
    turns, stopping short of a note's number."""
    k = -1 if night else 0
    icon_y = y + (h - 7) // 2
    icon = {(xx - x - 2, yy - icon_y) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9)
            if p.get(xx, yy) == ink}
    cy = y + h / 2
    red = seed % 2 == 0
    tableman_disc(p, x + 7.5, cy, 6.5, night, red=red)
    cut = IV[6 + k] if red else IV[1]
    for (u, v) in icon:
        p.px(x + 4 + u, round(cy) - 3 + v, cut)
    if lid:
        for xx in range(x + 16, x + w - 12):
            sq = ((xx - x - 16) // 3) % 2
            p.px(xx, y + 1, RD[4 + k] if sq else IV[6 + k])
            p.px(xx, y + 2, RD[2 + k] if sq else IV[4 + k])


def thong(p: Pix, cells, night: bool):
    """A schematic's wire as a thong of leather twisted on itself, light and dark by turns along it, its shade along
    the row under a level run and the column beside an upright one, knotted where it bends."""
    k = -1 if night else 0
    kinds: dict = {}
    for i, (x, y, d) in enumerate(cells):
        kinds.setdefault((x, y), set()).add(d)
        p.px(x, y, LEATHER[5 + k] if (i // 2) % 2 else LEATHER[3 + k])
        if d == "h":
            p.px(x, y + 1, LEATHER[1])
        else:
            p.px(x + 1, y, LEATHER[1])
    for (x, y), ds in kinds.items():
        if len(ds) == 2:
            for (dx, dy, t) in ((0, 0, 6), (-1, 0, 4), (1, 0, 3), (0, -1, 5), (0, 1, 2), (1, 1, 1)):
                p.px(x + dx, y + dy, LEATHER[max(0, t + k)])


def tablemen_stack(p: Pix, bx, base, bw, v, night: bool, i=0):
    """A week's commits as a stack of tablemen standing on the base line, `v` tall: counters of ivory laid one on
    another, each its own rim lit along its top and its edge in shade, and every fifth stained red, as a player
    counts his men."""
    k = -1 if night else 0
    y = base
    n = 0
    while y > base - v:
        h = min(3, y - (base - v))
        R = RD if n % 5 == 4 else IV
        for j in range(h):
            yy = y - 1 - j
            for xx in range(bx, bx + bw):
                u = (xx - bx) / max(1, bw - 1)
                edge = xx in (bx, bx + bw - 1)
                if j == h - 1 and h == 3:
                    c = R[6 + k] if u < 0.5 else R[5 + k]
                elif j == 0:
                    c = R[1]
                else:
                    c = R[5 + k] if u < 0.3 else R[4 + k] if u < 0.7 else R[3 + k]
                p.px(xx, yy, R[0] if edge else c)
        y -= 3
        n += 1


def crown_mark(p: Pix, x, y, night: bool):
    """A small crown of red bone over the busiest week's count."""
    k = -1 if night else 0
    stamp(p, x, y, ["K.K.K", "KRKRK", "RrRrR", "KKKKK"], {"K": RD[0], "R": RD[5 + k], "r": RD[3 + k]})


def quadrant(p: Pix, arc, night: bool):
    """The dial as a quadrant of carved ivory: its band of ivory bent over the face, lit along its upper left, cut
    with a groove along its middle, between two dark edges."""
    from ...holidays.pixel import tube
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        if abs(o) > 0.8:
            return IV[0]
        if abs(o) < 0.18:
            return IV[2 + k]
        return IV[6 + k] if lam > 0.75 else IV[5 + k] if lam > 0.5 else IV[4 + k] if lam > 0.25 else IV[3 + k]
    tube(p, arc, 3.2, colour, outline=IV[0])


def ring_dot(p: Pix, x, y, night: bool):
    """A tick on the quadrant: a ring and dot cut in the ivory."""
    k = -1 if night else 0
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        p.px(x + dx, y + dy, IV[1])
    p.px(x, y, IV[6 + k])


def crozier_hand(p: Pix, night: bool, accent: str):
    """The dial's hand redrawn as a bishop's crozier laid from the hub to the count, in place of the plain line the
    layout drew in `accent`: its staff of ivory two pixels thick, lit along its upper side and in the honey of its
    patina along the other, and at its head the crook curling forward, over and back into itself, all cut round with
    a dark edge."""
    cx, cy, r = p.dial
    reach = r - 11
    base = p.layers["base"]
    hand = [(x, y) for (x, y), c in base.items() if c == accent
            and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2]
    if not hand:
        return
    k = -1 if night else 0
    for xy in hand:
        del base[xy]
    far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
    ux, uy = far[0] + 0.5 - (cx + 0.5), far[1] + 0.5 - (cy + 0.5)
    n = math.hypot(ux, uy) or 1
    ux, uy = ux / n, uy / n
    vx, vy = -uy, ux
    if vy > 0 or (vy == 0 and vx > 0):
        vx, vy = -vx, -vy
    ox, oy = cx + 0.5, cy + 0.5
    lit, shade = IV[6 + k], HO[3 + k]
    core: dict = {}

    def put(fx, fy, c):
        core[(math.floor(fx), math.floor(fy))] = c
    length = reach - 4.5
    for i in range(12, round(length * 4) + 1):
        t = i / 4
        put(ox + ux * t + vx * 0.5, oy + uy * t + vy * 0.5, lit)
        put(ox + ux * t - vx * 0.5, oy + uy * t - vy * 0.5, shade)
    hx, hy = ox + ux * length, oy + uy * length
    R = 3.0
    ex, ey = hx + vx * R, hy + vy * R
    for i in range(0, 331, 6):
        a = math.radians(i)
        rr = R - 1.3 * i / 330
        for d, c in ((rr + 0.45, lit), (rr - 0.45, shade)):
            dx = math.cos(a) * -vx + math.sin(a) * ux
            dy = math.cos(a) * -vy + math.sin(a) * uy
            put(ex + d * dx, ey + d * dy, c if i < 200 else (shade if c == lit else lit))
    for (x, y) in list(core):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in core and (x + dx - cx) ** 2 + (y + dy - cy) ** 2 > 9:
                    base[(x + dx, y + dy)] = IV[0]
    for xy, c in core.items():
        base[xy] = c


def ivory_boss(p: Pix, cx, cy, night: bool):
    """The hub the crozier turns on: a boss of ivory."""
    from ...holidays.pixel import sphere
    sphere(p, cx + 0.5, cy - 0.5, 3.2, IV if not night else IV[:6], lo=1, hi=6 if not night else 5)


MATTERS = ("ivory", "stain", "oak", "horn", "stone", "leather", "gilt", "iron")


def matter(i, xx, yy, y0, y1, lift, night: bool) -> str:
    """The materials of the hall by turns: walrus ivory with its grain, bone stained red, oak, horn mottled pale and
    dark, grey stone, leather, gilt and iron."""
    k = -1 if night else 0
    kind = MATTERS[i % len(MATTERS)]
    if kind == "ivory":
        c = IV[5 + k] if (yy * 7 + xx // 9) % 5 else IV[4 + k]
    elif kind == "stain":
        c = RD[3 + k] if (xx + yy) % 5 else RD[2 + k]
    elif kind == "oak":
        c = OAK[4 + k] if ((xx // 7) + yy) % 3 else OAK[3 + k]
    elif kind == "horn":
        c = HO[5 + k] if ((xx * 3 + yy * 5) // 4) % 3 else HO[2 + k]
    elif kind == "stone":
        c = STONE[4 + k] if (xx * 7 + yy * 3) % 11 else STONE[2 + k]
    elif kind == "leather":
        c = LEATHER[4 + k] if (xx + 2 * yy) % 7 else LEATHER[2 + k]
    elif kind == "gilt":
        c = GILT[4 + k] if (xx - yy) % 6 else GILT[6 + k]
    else:
        c = IRON[4 + k] if (xx + yy) % 4 else IRON[3 + k]
    try:
        return step(c, lift)
    except KeyError:
        return c


def counter_disc(q: Pix, ox, oy, night: bool, L="far"):
    """A cell of the counters, 11 by 15: a tableman standing on its edge, an upright oval of ivory, its rim lit on
    its upper left and in shade on its lower right, cut round with a dark edge, and its face smooth where the
    numeral is carved. It lies on a layer under the drawing's own, so its numeral is always carved over it."""
    k = -1 if night else 0
    for j in range(15):
        for i in range(11):
            dx, dy = (i + 0.5 - 5.5) / 5.5, (j + 0.5 - 8.0) / 6.5
            e = math.hypot(dx, dy)
            if e > 1:
                continue
            if e > 0.86:
                c = IV[1]
            elif e > 0.72:
                c = IV[6 + k] if dx * -0.6 + dy * -0.8 > 0 else IV[3 + k]
            else:
                c = IV[5 + k]
            q.px(ox + i, oy + j, c, L)
    q.px(ox + 3, oy + 4, IV[6 + k], L)


def rank_line(p: Pix, x0, x1, y, night: bool):
    """The time line as a rank of the board up to today: squares of ivory and of red bone by turns, two rows deep,
    between its dark top edge and the shade along its foot, the releases standing on it."""
    k = -1 if night else 0
    for x in range(x0, x1):
        red = ((x - x0) // 4) % 2 == 1
        R = RD if red else IV
        p.px(x, y - 1, IV[0])
        p.px(x, y, R[(5 if red else 6) + k])
        p.px(x, y + 1, R[(3 if red else 4) + k])
        p.px(x, y + 2, R[1] if red else IV[2 + k])


# A release's pawn, 7 by 8, a size between the small pawn and the board's; and the small queen at today's end of the
# time line, veiled before her throne's back, her hand to her cheek.
PAWN_R = [
    ".KKKKK.",
    "K66654K",
    "K65543K",
    "KKKKKKK",
    ".K654K.",
    ".K543K.",
    "K65432K",
    "KKKKKKK",
]
QUEEN_S = [
    "..KKKKKKK..",
    ".K6KKKKK3K.",
    ".K6K656K3K.",
    ".K6Ke5eK3K.",
    "K66K555K32K",
    "K6K66544K2K",
    "K6K6K543K2K",
    "K5KKKKKKK2K",
    "K5K54433K1K",
    "K655443332K",
    "KKKKKKKKKKK",
]
CROWN_S = ["k.k.k", "GsGgG", "kkkkk"]   # a crown of gilt, 5 by 3


def gilt_crown(p: Pix, x, y, night: bool, L="base"):
    """The small crown of gilt, its top left at (x, y)."""
    k = -1 if night else 0
    stamp(p, x, y, CROWN_S, {"k": GILT[0], "G": GILT[5 + k], "g": GILT[3 + k], "s": GILT[6]}, L)


def release_piece(p: Pix, x, gy, kind: str, night: bool, i=0):
    """A release standing on the rank at x, its foot on the rank's shaded foot: a pawn of ivory, one of bone stained
    red for a big release, a small pawn for a patch, a pawn only outlined for one still to come, and a tableman laid
    down on the rank for the repository's founding."""
    k = -1 if night else 0
    if kind == "made":
        stamp(p, x - 3, gy - 1, [".KKKKK.", "K66654K", "K65432K", ".KKKKK."],
              {"K": RD[0], "6": RD[6 + k], "5": RD[5 + k], "4": RD[4 + k], "3": RD[3 + k], "2": RD[2 + k]})
        return
    rows = PAWN_R if kind in ("big", "major", "next") else PAWN_XS
    w, h = len(rows[0]), len(rows)
    x0, y0 = x - w // 2, gy + 3 - h
    if kind == "next":
        ink = X["rule_night"] if night else X["rule_day"]
        stamp(p, x0, y0, rows, {"K": ink})
        return
    side = "red" if kind == "big" else "ivory"
    stamp(p, x0, y0, rows, piece_pal(side, night))
    p.stood_at = getattr(p, "stood_at", []) + [(x0, y0, x0 + w, gy + 3)]


def queen_crowned(p: Pix, x, foot, night: bool):
    """The small queen standing with her foot on the row above `foot`, centred on x, and a row over her head the
    crown of gilt being set on it, a glint of its light either side."""
    w, h = len(QUEEN_S[0]), len(QUEEN_S)
    stamp(p, x - w // 2, foot - h, QUEEN_S, piece_pal("ivory", night))
    gilt_crown(p, x - 2, foot - h - 4, night)
    p.px(x - 4, foot - h - 4, GILT[6])
    p.px(x + 4, foot - h - 4, GILT[6])


QUEEN_S_H = len(QUEEN_S) + 4    # the queen and the crown over her


# --------------------------------------------------------------------------- the roster's busts
# A contributor as the head and shoulders of one of the chessmen, 17 by 20: a king crowned and bearded, a queen
# veiled with her hand to her cheek, a bishop in his mitre with his crozier, a warder in his helm biting the rim of
# his shield. The digits are the ivory of the face, a to f the stain of the robe and the headgear, k its darkest, o
# an eye's pupil and w the white of the eye and the teeth.
BUST_KING = [
    "....K...K...K....",
    "...KfK.KfK.KdK...",
    "...KffKfffKddK...",
    "...KfeefeeddcK...",
    "..KKKKKKKKKKKKK..",
    ".K43666666665K2K.",
    ".K435KKK6KKK4K2K.",
    ".K435wow6wow4K2K.",
    ".K43566656664K2K.",
    ".K43566545664K2K.",
    ".K435KK666KK4K2K.",
    ".K43K56565654K2K.",
    "kK43K65656564K2Kk",
    "kfKK.K56565K.KKck",
    "kffeK.K656K.Kccbk",
    "kfeeeK.K5K.Kcccbk",
    "kfeeedK.K.Kcccbbk",
    "kfeeddcKKKccbbbak",
    "kfeddccccccbbbbak",
    "kkkkkkkkkkkkkkkkk",
]
BUST_QUEEN = [
    "....K...K...K....",
    "...KfK.KfK.KdK...",
    "...KffKfffKddK...",
    "..KKKKKKKKKKKKK..",
    ".KffeeeeeedddcK..",
    "kfeK666666665Kck.",
    "kfeK5KK666KK4Kcbk",
    "kfeK5wow6wow4Kcbk",
    "kfK6K6666666Kcbbk",
    "kK666K665566Kcbbk",
    "K6666K654466Kcbbk",
    "K6556K66KK64Kcbbk",
    "K5554K666664Kcbak",
    ".K44KfK44444Kcbak",
    "kfKKffeKKKKKdcbak",
    "kfeeeeeddddddcbak",
    "kfeeddKdddKcccbak",
    "kfeeddKdddKcccbak",
    "kfeedddKddKcccbak",
    "kkkkkkkkkkkkkkkkk",
]
BUST_BISHOP = [
    "......K......KKK.",
    ".....KfK....KdddK",
    "....KffeK...KdKdK",
    "...KffeedK..KdKK.",
    "..KfffeeddK.KdK..",
    ".KfffeeeddcKKdK..",
    ".KKKKKKKKKKKKdK..",
    ".K666666665KKdK..",
    ".K5KKK6KKK4KKdK..",
    ".K5wow6wow4KKdK..",
    ".K566656664KKdK..",
    ".K566545664KKdK..",
    ".K566KKK664KKdK..",
    "..K5666664K.KdK..",
    "kfeKK6665KKcKdKbk",
    "kfeedcKKKcdcK665K",
    "kfeedcKdKcdcK654K",
    "kfeedcKdKcccKdKbk",
    "kfeddcKdKccbKdKak",
    "kkkkkkkkkkkkkkkkk",
]
BUST_WARDER = [
    "........K........",
    ".......KfK.......",
    "......KffeK......",
    ".....KffeedK.....",
    "....KfffeeddK....",
    "...KfffeeeddcK...",
    "..KKKKKKKKKKKKK..",
    "..K66666666654K..",
    "..K5KKK6KKK443K..",
    "..K5wow6wow443K..",
    "..K56665666433K..",
    "..K56654566433K..",
    "..K5KwKwKwKw43K..",
    "KKKKKKKKKKKKKKKKK",
    "KfffffeKeeddddccK",
    "KffeeeKwKedddccbK",
    "KfeeeKw6wKddccbbK",
    ".KeeeeKwKdddccbK.",
    "..KeeddKdddccbK..",
    "...KKKKKKKKKKK...",
]
BUST_PAWN = [
    "....KKKKKKKKK....",
    "...K666666654K...",
    "..K66666665543K..",
    "..K65555554432K..",
    "..K65544444332K..",
    "..K65544444332K..",
    "..KKKKKKKKKKKKK..",
    "...K654444332K...",
    "...K654444332K...",
    "...K654443332K...",
    "...K654443322K...",
    "...K654433322K...",
    "...K654433322K...",
    "..KKKKKKKKKKKKK..",
    "..K66555544433K..",
    ".K6655554443332K.",
    ".K6555444433322K.",
    ".KKKKKKKKKKKKKKK.",
]
BUSTS = (BUST_KING, BUST_QUEEN, BUST_BISHOP, BUST_WARDER)
STAINS = ("stain", "woad", "verd", "weld", "sloe")      # the colours a contributor's piece is stained, by turns


def bust(p: Pix, cx, cy, i: int, night: bool, bot=False):
    """A contributor as one of the chessmen, head and shoulders, 17 wide and 20 tall about (cx, cy): a king, a queen,
    a bishop and a warder by turns, the face of ivory and the robe and headgear stained in the contributor's own
    colour; a bot as a plain pawn of ivory."""
    k = -1 if night else 0
    rows = BUST_PAWN if bot else BUSTS[i % len(BUSTS)]
    S = RAMP[STAINS[i % len(STAINS)]]
    pal = {"K": IV[0], "o": HALL[0], "w": IV[6], "k": S[0]}
    for t in range(1, 7):
        pal[str(t)] = IV[max(1, t + k)] if bot else IV[t]
        pal["abcdef"[t - 1]] = S[max(1, t + k)]
    stamp(p, cx - 8, cy - 10 + (1 if bot else 0), rows, pal)


# --------------------------------------------------------------------------- the commit bar, the seal, the kist
def counters_bar(p: Pix, x, y, w, fill, night: bool):
    """A contributor's share as a groove cut in the ivory, `w` long, and laid in it as far as their commits reach a
    row of tablemen stained red, each its own rim lit along its top."""
    k = -1 if night else 0
    for xx in range(x, x + w + 2):
        p.px(xx, y, IV[1])
        p.px(xx, y + 3, IV[5 + k] if not night else IV[2])
    p.px(x, y + 1, IV[1])
    p.px(x, y + 2, IV[1])
    p.px(x + w + 1, y + 1, IV[3 + k])
    p.px(x + w + 1, y + 2, IV[3 + k])
    for xx in range(x + 1, x + w + 1):
        p.px(xx, y + 1, IV[3 + k])
        p.px(xx, y + 2, IV[4 + k])
    for xx in range(x + 1, x + 1 + fill):
        u = (xx - x - 1) % 3
        p.px(xx, y + 1, RD[0] if u == 2 else RD[5 + k])
        p.px(xx, y + 2, RD[0] if u == 2 else RD[3 + k])


def crown_seal(p: Pix, cx, cy, r0, r1, n, night: bool):
    """The seal's rosette as a king's crown of bone stained red carved round it: a band about the seal's disc, lit on
    its upper left and studded with ivory, and rising from its upper half the crown's points, tall and short by turns,
    each tall one ending in a round knob, all cut round with a dark edge."""
    k = -1 if night else 0
    band = r0 + 2.6
    points = 7
    spread = 180 / (points - 1)
    cells: dict = {}
    for y in range(math.floor(cy - r1) - 4, math.ceil(cy + r1) + 3):
        for x in range(math.floor(cx - r1) - 4, math.ceil(cx + r1) + 5):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d < r0 - 1 or d > r1 + 4:
                continue
            lit = (-dx * 0.6 - dy * 0.8) / max(d, 1.0)
            inside = d <= band
            if not inside and dy < 1:
                a = math.degrees(math.atan2(dy, dx)) % 360
                j = round((a - 180) / spread)
                if 0 <= j < points:
                    off = abs(a - (180 + j * spread)) * math.pi / 180 * d
                    tall = j % 2 == 1
                    tip = r1 + 1.5 if tall else r1 - 2.5
                    if d <= tip - (1.8 if tall else 0):
                        half = 3.4 - 2.9 * (d - band) / max(1.0, tip - band)
                        inside = off <= half
                    if tall:
                        ta = math.radians(180 + j * spread)
                        kx, ky = cx + (tip - 1.4) * math.cos(ta), cy + (tip - 1.4) * math.sin(ta)
                        inside = inside or math.hypot(x + 0.5 - kx, y + 0.5 - ky) <= 1.9
            if not inside:
                continue
            c = RD[6 + k] if lit > 0.55 else RD[5 + k] if lit > 0.05 else RD[4 + k] if lit > -0.45 else RD[3 + k]
            if band - 1.1 <= d <= band and dy >= 1:
                c = RD[2 + k]
            cells[(x, y)] = c
    for i in range(16):
        a = math.radians(i * 22.5 + 11.25)
        sx, sy = math.floor(cx + (r0 + 1.6) * math.cos(a)), math.floor(cy + (r0 + 1.6) * math.sin(a))
        if (sx, sy) in cells:
            cells[(sx, sy)] = IV[6 + k]
    for (x, y), c in cells.items():
        p.px(x, y, c)
    for (x, y) in list(cells):
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xy = (x + ddx, y + ddy)
            if xy not in cells and math.hypot(xy[0] + 0.5 - cx, xy[1] + 0.5 - cy) > r0 - 0.5:
                p.px(*xy, RD[0])


def seal_tableman(p: Pix, x, y, night: bool):
    """A tableman of ivory set at the seal's foot."""
    tableman_disc(p, x + 7.5, y + 3.5, 4.2, night)


def ribbon_band(p: Pix, x, y, w, h, night: bool, tail=4):
    """The ribbon under the seal as a band of tablet weaving: red, its edges woven in a running chevron of ivory, its
    ends falling either side of the tag cut in forks."""
    for xx in range(x, x + w):
        p.px(xx, y, IV[5] if (xx - x) % 4 in (0, 1) else RD[4])
        p.px(xx, y + h - 1, IV[5] if (xx - x) % 4 in (2, 3) else RD[4])
    for j in range(h):
        for i in range(tail):
            drop = 1 if i >= 2 else 0
            if i == tail - 1 and j == h // 2:
                continue
            c = RD[1] if j in (0, h - 1) else RD[2]
            p.px(x - 1 - i, y + j + drop, c)
            p.px(x + w + i, y + j + drop, c)


def kist(p: Pix, night: bool):
    """The placard as the stone kist the hoard was found in, seen from the front within the board's edge: its lid a
    slab of stone across its top, lit along its edge and carved along its front with a running knot, the shade of the
    lid's overhang under it; its sides two upright slabs; and its front slab, where the words are, a smooth stone
    flecked a shade darker, every word on it at 4.5:1."""
    k = -1 if night else 0
    w, h = p.w, p.h
    paper(p, night, uid="pl")
    frame(p, night, uid="plf")
    face, fleck = (X["kist_night"], X["kist_fleck_n"]) if night else (X["kist"], X["kist_fleck"])
    rnd = random.Random(7)
    p.rect(4, 21, w - 8, h - 25, face)
    for _ in range((w * h) // 55):
        fx, fy = rnd.randrange(8, w - 8), rnd.randrange(23, h - 5)
        p.px(fx, fy, fleck)
    for y in range(4, 21):
        for x in range(4, w - 4):
            if y == 4:
                c = STONE[6 + k]
            elif y >= 19:
                c = STONE[2 + k] if y == 19 else STONE[1]
            else:
                c = STONE[5 + k] if (x * 7 + y * 13) % 17 else STONE[4 + k]
            p.px(x, y, c)
    for (x0, x1) in ((4, 8), (w - 8, w - 4)):
        for y in range(21, h - 4):
            for x in range(x0, x1):
                lit = x == x0
                p.px(x, y, STONE[5 + k] if lit else STONE[3 + k] if x < x1 - 1 else STONE[1])
    knot(p, 26, w - 26, 15, night)


def knot(p: Pix, x0, x1, y, night: bool):
    """A running knot carved along the lid's front from x0 to x1 about row y: two strands winding round each other,
    each lit along its upper edge and in shade along its lower, and where they cross the one passing under cut away
    either side of the one passing over, by turns."""
    k = -1 if night else 0
    for x in range(x0, x1):
        u = x - x0
        lift = round(2.2 * math.sin(2 * math.pi * u / 16))
        crossing = round(u / 8)
        near = abs(u - crossing * 8) <= 1
        for s, off in ((0, -lift), (1, lift)):
            over = (crossing + s) % 2 == 0
            if near and not over:
                continue
            p.px(x, y + off - 1, STONE[6 + k])
            p.px(x, y + off, STONE[3 + k])
            if (x, y + off + 1) not in p.layers["base"] or p.get(x, y + off + 1) not in (STONE[6 + k], STONE[3 + k]):
                p.px(x, y + off + 1, STONE[2 + k])
