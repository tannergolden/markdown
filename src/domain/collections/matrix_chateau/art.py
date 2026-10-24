# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chateau set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is a wall hung with silk damask, champagne gold by day and wine-dark by night, woven in an ogee lattice of
S-curved stems with a lily in each cell, its stems catching the light along their left edge. A gilded frame holds it,
lit along its top and left and in shade along its foot and right, strung with beads down its sides, and along a
header's top it deepens into a frieze of egg and dart between two corner blocks carved with rosettes, parting either
side of the month's mark, where an acanthus scroll hangs from each end and the two frame the mark between them. Titles
are gold leaf on carved letters, each stroke chiselled to a ridge so one face takes the candles' light and the other
falls into shade, the upper half of every letter brighter than its foot, the whole edged in the gilt's darkest brown
over the shadow the letters cast on the silk. Behind the title the chandeliers' crystal throws a shimmer of light
across the silk (`shimmer`), glints of gold by day and of the candles' green by night, twinkling in a moving header.

A header opens on the chateau's hall: two marble columns with gilded capitals frame a grand staircase whose red
carpet runs down the middle of its marble steps under brass rods, between balustrades that close in as they climb to
a landing and a tall arched window, the day's pale sky in its panes by day and the moon and the code's glyph stars by
night; a lamp burns on each newel post at the foot of the stair, and a crystal chandelier hangs over it all from the
frieze, with more of them across the hall wherever the words leave room. The carpet runs on along the floor to the
banquet: the end of a long table in white linen, its cloth falling in folds to a gold fringe under a runner of red
velvet, a five-branched candelabrum and a tiered chocolate cake on a gilt stand on it among goblets of wine; on the wall
over it two swords crossed behind a gilded shield between a pair of sconces, and before it a guest in a long dark coat
and dark glasses with a sword drawn. Every candle in the chateau burns on the hand's phosphor, for in the Matrix every
flame is code: by night their green light is laid on the gilt, the marble, the linen and the velvet near them and
pools on the stair, the cloth and the floor, and in a moving header the flames flicker, the crystal glitters and a
glint crosses the guest's glasses.

Under the frieze hangs a valance of red velvet swags, a gold fringe along each hem and a gilt clasp and a tassel where
two meet, parting round the month's mark. The section header stands the salon's fireplace (`fireplace`): a hearth of
white marble, fluted pilasters under a frieze carved with a gilt shell, three flames leaping from the logs in its brick
firebox, a clock and two candelabra on its mantel, a pier glass in a gilt frame over it and a torchere of five candles
at either side. The strip stands the suit of armour (`armour`) on its marble plinth with its halberd, a red banner
charged with the lily hung over it from the frieze so that it rises the strip's full height, and a torchere beside it.
On a phone the whole chateau stands under the words (`phone_chateau`), the guest warms himself at the fireplace
(`phone_salon`) and two suits of armour guard the trophy of swords (`phone_armoury`). Everything is shaded from the
one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random
import weakref

from ...holidays.pixel import FONTS, LX, LY, LZ, Pix, fold
from .. import rain
from .palette import C, NIGHT_SKY, RAMP, ramp_for, step

SILK, WINE, GOLD, MARBLE, VEIN = (RAMP[k] for k in ("silk", "wine", "gold", "marble", "vein"))
CARPET, CRYSTAL, LINEN, STEEL = (RAMP[k] for k in ("carpet", "crystal", "linen", "steel"))
WOOD, COCOA, FLAME, MOON = (RAMP[k] for k in ("wood", "cocoa", "flame", "moon"))
EDGE = 4          # the frame's width down a sheet's sides and along its foot
TOP = 13          # the depth of the gilded frieze along a header's top
# The canvases drawn lighter to fit a budget. On them only texture a reader does not miss at 1x is thinned: the
# crystal's shimmer keeps half its glints and the titles' gold half its glints, the damask goes without its lilies,
# every candle's glow and every pool of its light without its outermost ring, what the fire and the candles light
# without the wash laid over it, and the last pass lays only the nearer half of each candle's light. Every piece of a
# scene, every light, the titles and all the motion stay.
THIN: weakref.WeakSet = weakref.WeakSet()


def _g(i: int, night: bool) -> str:
    """A tone of the gilt, a tone deeper by night, where only the candles light it."""
    return GOLD[max(0, min(6, i - (1 if night else 0)))]


# --------------------------------------------------------------------------- drawing in few bytes
def _blocks(rows: dict) -> str:
    """Path data filling the cells {y: [x, ...]} as rectangles: each row's runs, a run that lies the same in the rows
    under it one rectangle with them, every move after the first relative to the last rectangle's corner."""
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


def markup(cells: dict) -> str:
    """Cells {(x, y): colour} as paths: each colour's as strokes along its rows, as the canvas writes pixels, or as
    filled rectangles where its runs repeat down the rows enough to make that shorter."""
    by: dict = {}
    for (x, y), c in cells.items():
        by.setdefault(c, {}).setdefault(y, []).append(x)
    out = []
    for c, rows in sorted(by.items()):
        strokes, blocks = Pix._d(rows), _blocks(rows)
        if len(blocks) + 2 < len(strokes):
            out.append(f'<path fill="{c}" d="{blocks}"/>')
        else:
            out.append(f'<path stroke="{c}" d="{strokes}"/>')
    return "".join(out)


# --------------------------------------------------------------------------- the silk
DAMASK_W, DAMASK_H = 28, 40     # the damask's repeat: an ogee lattice, its cells' lilies half a repeat apart
LILY = [
    "...#...",
    "..###..",
    "..###..",
    "#..#..#",
    "##.#.##",
    ".#####.",
    "...#...",
    ".#####.",
    "#.#.#.#",
    "..#.#..",
]


def _damask(lilies: bool = True) -> dict:
    """The damask's repeat as {(x, y): 0 for the woven figure, 1 for its sheen}: an ogee lattice of S-curved stems,
    each two units thick with its left unit catching the light, and in each of its cells a lily (the `lilies` a
    drawing made lighter leaves out)."""
    W, H = DAMASK_W, DAMASK_H
    out: dict = {}
    for base, sign in ((0, 1), (W // 2, -1)):
        for y in range(H):
            a = base + sign * (W / 4) * math.sin(2 * math.pi * y / H)
            b = base + sign * (W / 4) * math.sin(2 * math.pi * (y + 1) / H)
            x0, x1 = round(min(a, b)), round(max(a, b))
            for x in range(x0, x1 + 2):
                out.setdefault((x % W, y), 0)
            out[(x0 % W, y)] = 1
    for cx, cy in ((W // 4, 3 * H // 4), (3 * W // 4, H // 4)) if lilies else ():
        for j, row in enumerate(LILY):
            for i, ch in enumerate(row):
                if ch == "#":
                    q = ((cx - 3 + i) % W, (cy - 5 + j) % H)
                    left = i == 0 or row[i - 1] != "#"
                    out[q] = 1 if (left or j == 0 or LILY[j - 1][i] != "#") and i <= 3 else 0
    return out


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: silk damask, champagne gold by day, and by night wine-dark, deepest at the head
    and foot of the sheet where the candles' light does not reach; its figure woven a shade off the ground and its
    sheen a shade lighter, drawn once a file as a pattern."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
        figure, sheen = WINE[4], WINE[5]
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
        figure, sheen = SILK[4], SILK[6]
    rows: dict = {figure: {}, sheen: {}}
    for (x, y), t in _damask(lilies=p not in THIN).items():
        rows[sheen if t else figure].setdefault(y, []).append(x)
    body = "".join(f'<path stroke="{c}" d="{Pix._d(r)}"/>' for c, r in rows.items() if r)
    p.defs.append(f'<pattern id="{uid}d" width="{DAMASK_W}" height="{DAMASK_H}" patternUnits="userSpaceOnUse">'
                  f'{body}</pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}d)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the band of wine-dark silk by night, the champagne silk by day."""
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        return next(NIGHT_SKY[i] for i in range(n) if y < edges[i + 1] or i == n - 1)
    return C["paper"]


# --------------------------------------------------------------------------- the frame
def _egg(night: bool) -> dict:
    """One repeat of the frieze's egg and dart, eight units by seven: an egg lit from the upper left in its cup of
    gilt, and a dart pointing down between the cups, on the recess's dark gilt."""
    cells = {(x, y): _g(1, night) for x in range(8) for y in range(7)}
    for y in range(7):
        for x in range(6):
            dx, dy = (x + 0.5 - 3) / 2.45, (y + 0.5 - 3.1) / 2.9
            d2 = dx * dx + dy * dy
            if d2 <= 1:
                lam = max(0.0, dx * LX + dy * LY + math.sqrt(1 - d2) * LZ)
                cells[(x, y)] = _g(2 + min(4, round(lam * 4.4)), night)
            elif d2 <= 1.55 and y >= 3:
                cells[(x, y)] = _g(4 if x < 3 else 2, night)
    for y in range(5):
        cells[(7, y)] = _g(4 if y < 4 else 5, night)
    cells[(6, 4)] = cells[(0, 4)] = _g(3, night)
    cells[(7, 5)] = _g(2, night)
    return cells


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


def _beads(night: bool, across: bool) -> dict:
    """A string of gilt beads, each three units long and lit at its upper or left end, one unit between."""
    tones = (_g(6, night), _g(4, night), _g(2, night), GOLD[0])
    return {((i, 0) if across else (0, i)): c for i, c in enumerate(tones)}


def _rosette(p: Pix, x, y, n, night: bool, L="base"):
    """A corner block `n` units square carved with a rosette of eight petals round a boss, lit from the upper left."""
    p.rect(x, y, n, n, _g(2, night), L)
    p.hline(x, x + n, y, _g(5, night), L)
    p.vline(x, y, y + n, _g(5, night), L)
    p.hline(x, x + n, y + n - 1, GOLD[0], L)
    p.vline(x + n - 1, y, y + n, GOLD[0], L)
    c = (n - 1) / 2
    for j in range(1, n - 1):
        for i in range(1, n - 1):
            dx, dy = i - c, j - c
            r = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            reach = (n / 2 - 1.4) * (0.62 + 0.38 * abs(math.cos(4 * th)))
            if r > reach:
                continue
            if r < 1.3:
                tone = 6 if dx + dy < 0 else 4
            else:
                lam = -(dx * LX + dy * LY) / max(r, 0.1)
                tone = 4 + round(lam * 1.6) if r < reach - 0.8 else 1
            p.px(x + i, y + j, _g(max(0, min(6, tone)), night), L)


# An acanthus scroll hung from the frieze at the left of the month's mark, its mirror at the right, so that the two
# frame the mark as a cartouche would: a volute at its head with a glint in its eye, a leaf running down its outer
# edge in lobes, and a curl at its foot turning in toward the mark. 12 units wide and 20 tall, from the frieze's top
# to two rows short of the tallest title's; o is its outline, h G g the gilt deep to lit, w the glint.
SCROLL = [
    "......oooo..",
    "....oogggGo.",
    "...ogGhhhhGo",
    "..ogGho..ohG",
    "..oGho.wo.hG",
    "..oGho.oGhGo",
    "..oGGhoGGho.",
    "..ogGGGGho..",
    ".oggGhhoo...",
    "ogGhGo......",
    ".oGGho......",
    "..oGho......",
    ".ogGGo......",
    "ogGhGo......",
    ".oGGho...oo.",
    "..oGgo..oGgo",
    "..ohGgooGhGo",
    "...ohGGGhGo.",
    "....ohhhoo..",
    ".....oooo...",
]


def frame(p: Pix, night: bool, header: bool = False, gap=None):
    """The gilded frame: a dark edge, a fillet lit along the top and left and shaded along the foot and right, a
    string of beads, and the sight edge in the gilt's darkest. Along a header's top it deepens into a frieze of egg and
    dart between corner blocks carved with rosettes, parting either side of `gap`, the columns (x0, x1) the month's
    mark keeps clear, a bracket closing each end and an acanthus scroll hung from each (see `SCROLL`), the two framing
    the mark between them."""
    w, h = p.w, p.h
    G0 = GOLD[0]
    p.box(0, 0, w, h, G0)
    p.vline(1, 1, h - 1, _g(5, night))
    p.vline(w - 2, 1, h - 1, _g(2, night))
    p.hline(1, w - 1, h - 2, _g(2, night))
    _lay(p, _pattern(p, "fbv", 1, 4, _beads(night, False)), 2, 2, 1, h - 4)
    _lay(p, _pattern(p, "fbv", 1, 4, _beads(night, False)), w - 3, 2, 1, h - 4)
    _lay(p, _pattern(p, "fbh", 4, 1, _beads(night, True)), 2, h - 3, w - 4, 1)
    top = TOP if header else 3
    p.vline(3, top, h - 3, G0)
    p.vline(w - 4, top, h - 3, G0)
    p.hline(3, w - 3, h - 4, G0)
    if not header:
        p.hline(1, w - 1, 1, _g(5, night))
        _lay(p, _pattern(p, "fbh", 4, 1, _beads(night, True)), 2, 2, w - 4, 1)
        p.hline(3, w - 3, 3, G0)
        return
    p.hline(1, w - 1, 1, _g(5, night))
    p.hline(2, w - 2, 2, _g(4, night))
    spans = [(EDGE, w - EDGE)] if gap is None else [(EDGE, gap[0]), (gap[1], w - EDGE)]
    egg = _pattern(p, "fe", 8, 7, _egg(night), x0=0, y0=3)
    for a, b in spans:
        _lay(p, egg, a, 3, b - a, 7)
        p.hline(a, b, 10, _g(3, night))
        _lay(p, _pattern(p, "fbh", 4, 1, _beads(night, True)), a, 11, b - a, 1)
        p.hline(a, b, 12, G0)
    if gap is not None:
        for x, face in ((gap[0] - 3, 5), (gap[1], 4)):
            p.rect(x, 3, 3, 10, _g(face - 1, night))
            p.vline(x, 3, 13, _g(face + 1, night))
            p.vline(x + 2, 3, 13, GOLD[0])
            p.hline(x, x + 3, 12, GOLD[0])
        pal = {"o": GOLD[0], "h": _g(2, night), "G": _g(4, night), "g": _g(5, night), "w": _g(6, night)}
        key = ("scroll", night)
        if key not in p.syms:
            p.symbol(key, {}, shapes=markup({(i, j): pal[ch] for j, row in enumerate(SCROLL)
                                             for i, ch in enumerate(row) if ch in pal}))
        sid, x = p.syms[key], gap[0] - len(SCROLL[0])
        L = p.layer("scroll", z=0.2)
        p.shapes[L].append(f'<use href="#{sid}" x="{x}" y="3"/><use href="#{sid}" x="{x}" y="3" '
                           f'transform="matrix(-1 0 0 1 {gap[0] + gap[1]} 0)"/>')
    key = ("rosette", night)
    if key not in p.syms:
        q = Pix(TOP, TOP)
        _rosette(q, 0, 0, TOP, night)
        p.symbol(key, dict(q.layers["base"]))
    p.use(key, 0, 0)
    p.use(key, w - TOP, 0)


# --------------------------------------------------------------------------- the titles: gold leaf on carved letters
def _lit_face(font, c, r, dx, dy, s) -> bool:
    """Whether a unit of a chiselled stroke faces the light: the upper face of a stroke that runs across, the left
    face of one that runs down, and at a corner the faces mitred where the two meet."""
    L, R, U, D = (c - 1, r) in font, (c + 1, r) in font, (c, r - 1) in font, (c, r + 1) in font
    half = s / 2
    if (U or D) and not (L or R):
        return dx < half - 0.01
    if (L or R) and not (U or D):
        return dy < half - 0.01
    if R and D and not L and not U:
        return dx < half or dy < half
    if L and U and not R and not D:
        return dx < half and dy < half
    return dx + dy < s - 1


def _gilt(ch: str, s: int, night: bool) -> dict:
    """A letter in gold leaf `s` units to the face's unit, as {(x, y): colour} from its top-left: the shadow it casts
    on the silk half a face unit down and to the right, its edge a unit round it in the gilt's darkest, and the leaf on
    its chiselled strokes, the lit faces bright and their shaded faces deeper, every tone brighter in the letter's
    upper half than toward its foot, with a band of shade across its middle where the polished leaf mirrors the dark
    of the hall. At twice the face's size the strokes are too narrow to carve, and are bevelled instead."""
    font = {(c, r) for r, cols in enumerate(FONTS["57"][0][ch][1]) for c in cols}
    ink = {(c * s + dx, r * s + dy): (c, r, dx, dy) for (c, r) in font for dx in range(s) for dy in range(s)}
    out = {}
    off = max(1, s // 2)
    for (x, y) in ink:
        out[(x + off, y + off)] = WINE[0] if night else SILK[2]
    for (x, y) in ink:
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if (x + ddx, y + ddy) not in ink:
                    out[(x + ddx, y + ddy)] = GOLD[0]
    tall = 7 * s
    for (x, y), (c, r, dx, dy) in ink.items():
        t = y / tall
        if s >= 3:
            if _lit_face(font, c, r, dx, dy, s):
                col = GOLD[6] if t < 0.2 else GOLD[5] if t < 0.45 else GOLD[4] if t < 0.56 else GOLD[5]
            else:
                col = GOLD[4] if t < 0.45 else GOLD[2] if t < 0.56 else GOLD[3]
        elif (x, y + 1) not in ink or (x + 1, y) not in ink:
            col = GOLD[2]
        elif (x - 1, y) not in ink or (x, y - 1) not in ink:
            col = GOLD[5]
        else:
            col = GOLD[4]
        out[(x, y)] = col
    return out


def gilt_title(p: Pix, x, y, s: str, scale: int, night: bool) -> int:
    """A title in gold leaf on carved letters (see `_gilt`), each letter drawn once a file and placed. The line's box
    is kept with the words, exactly as the canvas keeps a line it sets. Returns its width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    cx = x
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        key = ("gilt", ch, scale, night)
        if key not in p.syms:
            p.symbol(key, {}, shapes=markup(_gilt(ch, scale, night)))
        p.use(key, cx, y)
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    rows = max((len(glyphs[ch][1]) for ch in s if ch != " "), default=0)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    return w


def sparkles(p: Pix, x, y, s: str, scale: int, night: bool = False, seed: int = 0):
    """Glints of candlelight on a title's gold, in a moving header: a small star of light on the upper corner of every
    other letter, six to a line at the most and three on a drawing made lighter, twinkling on the engine's cadence,
    each letter's in its turn; by night the candles' green is in them."""
    glyphs, _, space = FONTS["57"]
    cx = x
    rnd = random.Random(seed)
    most, n = (3 if p in THIN else 6), 0
    for i, ch in enumerate(fold(s, "57")):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        rows = glyphs[ch][1]
        if i % 2 == 0 and rows and rows[0] and n < most:
            n += 1
            col = min(rows[0]) if rnd.random() < 0.6 else max(rows[0])
            sx, sy = cx + col * scale + scale // 2, y + scale // 2
            L = p.twinkle(i)
            p.px(sx, sy, C["white"], L)
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(sx + ddx, sy + ddy, FLAME[5] if night else GOLD[6], L)
        cx += (glyphs[ch][0] + 1) * scale


# --------------------------------------------------------------------------- light
# How many tones darker each material is drawn by night, before the candles light what stands near them; the gilt,
# which holds what little light there is, is a tone darker (see `_g`).
DARK = {"marble": 3, "vein": 1, "linen": 3, "carpet": 2, "steel": 2, "wood": 1, "cocoa": 1}
LIT = {c for name in ("marble", "vein", "linen", "carpet", "steel", "wood", "cocoa", "gold", "cloth", "hair")
       for c in RAMP[name]}
PALE = set(MARBLE) | set(LINEN)


def tone(name: str, i: int, night: bool) -> str:
    """Tone `i` of material `name`, drawn darker by night by the material's own count (see `DARK`)."""
    return RAMP[name][max(0, min(6, i - (DARK.get(name, 1) if night else 0)))]


def lamp(p: Pix, cx, cy, r):
    """A flame, or a cluster of them, at (cx, cy) whose light reaches `r` units: by night `candlelight` lays it on
    whatever stands near it."""
    p.lamps.append((cx, cy, r))


def _lit(c: str, d: float) -> str:
    """A colour `d` from a candle, 0 at the flame and 1 at the edge of its reach, in its light: marble and linen near
    the flame take the phosphor's own green, as white things do by a green light, and everything else is lit two
    tones lighter on its own ramp near the flame and one further off."""
    if c in PALE and d < 0.42:
        return FLAME[3] if ramp_for(c).index(c) >= 2 else FLAME[2]
    return step(c, 2 if d < 0.55 else 1)


def candlelight(p: Pix, night: bool):
    """The finishing pass, by night only: every candle's light laid into the colours of what stands near it, the
    nearest candle's for each pixel, on its gilt, marble, linen, velvet, steel and chocolate, and on a footer's
    carpet. The words, set as symbols, take none of it. A drawing made lighter lays only the nearer, brighter half of
    each candle's light, the faint step at its edge left out."""
    if not night or not p.lamps:
        return
    reach = 0.55 if p in THIN else 1
    for name in ("base", "foot"):
        cells = p.layers.get(name, {})
        for (x, y), c in list(cells.items()):
            if c not in LIT:
                continue
            best = None
            for (cx, cy, r) in p.lamps:
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15) / r
                if d < reach and (best is None or d < best):
                    best = d
            if best is not None:
                cells[(x, y)] = _lit(c, best)


GLOW = (0.04, 0.08, 0.13)     # the rings of a candle's glow on the silk, outermost first


def glow(p: Pix, cx, cy, rx, ry, night: bool):
    """By night the green light a cluster of candles throws round itself on the silk, in rings, drawn in no nearer
    than two units to any word: each size of glow drawn once a file and placed as often as it is lit."""
    while night and rx > 3 and not p.clear_of_words(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2):
        rx, ry = rx - 1, ry - 1
    if not night or rx <= 3:
        return
    rings = GLOW[1:] if p in THIN else GLOW
    key = ("glow", rx, ry, len(rings))
    if key not in p.syms:
        q = Pix(1, 1)
        q.halo(0, 0, rx, ry, FLAME[3], rings, L="haze", shape=True)
        p.symbol(key, {}, shapes="".join(q.shapes["haze"]).replace(' cx="0" cy="0"', ""))
    p.use(key, cx, cy, "haze")


# --------------------------------------------------------------------------- the candles
def flame(p: Pix, x, y, motion: bool, phase: int = 0):
    """A candle's flame with its foot on row y over column x, burning on the hand's phosphor: a white-hot core in a
    tongue of green, flickering in a moving header."""
    L = p.flicker(phase) if motion else "base"
    p.px(x, y - 2, FLAME[4], L)
    p.px(x, y - 1, FLAME[6], L)
    p.px(x, y, FLAME[3], L)


def candle(p: Pix, x, foot, h: int, night: bool, motion: bool, phase: int = 0):
    """A white candle `h` units tall standing on row `foot`, lit at its top, its flame over it."""
    for y in range(foot - h + 1, foot + 1):
        p.px(x, y, tone("linen", 5, night))
    p.px(x, foot - h + 1, tone("linen", 6, night))
    flame(p, x, foot - h, motion, phase)


# --------------------------------------------------------------------------- the hall
def column(p: Pix, x, top, g, night: bool):
    """A marble column seven units wide from the top of its capital on row `top` to the foot of its plinth on the
    floor at row g: a gilded capital of acanthus under its abacus, a shaft of white marble fluted and veined in grey,
    lit down its left and shaded down its right, and a base of a torus on a square plinth."""
    def m(i):
        return tone("marble", i, night)
    p.hline(x, x + 7, top, _g(5, night))
    p.hline(x, x + 7, top + 1, _g(3, night))
    for i, c in enumerate((5, 2, 5, 3, 5, 2, 1)):
        p.px(x + i, top + 2, _g(c, night))
    for i, c in enumerate((1, 5, 3, 6, 3, 4, 1)):
        p.px(x + i, top + 3, _g(c, night))
    for i, c in enumerate((4, 2, 5, 2, 3)):
        p.px(x + 1 + i, top + 4, _g(c, night))
    p.hline(x + 1, x + 6, top + 5, _g(2, night))
    for y in range(top + 6, g - 3):
        for i, t in enumerate((5, 6, 3, 4, 2)):
            p.px(x + 1 + i, y, m(t))
    p.vline(x, top + 6, g - 3, tone("vein", 2, night))
    p.vline(x + 6, top + 6, g - 3, tone("vein", 1, night))
    rnd = random.Random(x * 7 + top)
    for _ in range((g - top) // 9):
        vx, vy = x + 1 + rnd.randrange(4), top + 8 + rnd.randrange(max(1, g - top - 14))
        for j in range(3):
            if top + 6 <= vy + j < g - 3:
                p.px(x + 1 + (vx - x - 1 + (j if rnd.random() < 0.5 else 0)) % 5, vy + j, tone("vein", 4, night))
    for i, t in enumerate((4, 6, 5, 4, 3, 2, 1)):
        p.px(x + i, g - 3, m(t))
    p.hline(x + 1, x + 6, g - 2, m(2))
    p.hline(x, x + 6, g - 1, m(5))
    p.hline(x, x + 6, g, m(3))
    p.px(x + 6, g - 1, m(2))
    p.px(x + 6, g, m(1))


def window(p: Pix, x0, x1, top, foot, night: bool, motion: bool):
    """A tall arched window from column x0 to x1 and row `top` to `foot`, in a gilded frame with a mullion and a
    transom: the day's pale sky in its panes by day with a gleam across the glass; by night the dark sky with the
    hand's moon in it, the code's stars twinkling round it and one of its glyphs showing faintly through a pane."""
    w = x1 - x0
    r = w / 2
    cx = x0 + r
    inside = set()
    for y in range(top, foot):
        for x in range(x0, x1):
            dy = (top + r) - (y + 0.5)
            if dy > 0 and math.hypot(x + 0.5 - cx, dy) > r:
                continue
            inside.add((x, y))
    glass = {q for q in inside if all((q[0] + a, q[1] + b) in inside for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    for q in inside - glass:
        p.px(*q, _g(5 if q[0] < cx and q[1] < foot - 1 else 2, night))
    for (x, y) in glass:
        if night:
            c = WINE[0] if y < top + r + 2 else WINE[1]
        else:
            c = CRYSTAL[5] if (x - y) % 9 > 1 else CRYSTAL[6]
            if y > foot - (foot - top) // 3:
                c = CRYSTAL[4] if (x - y) % 9 > 1 else CRYSTAL[5]
        p.px(x, y, c)
    xm = round(cx - 0.5)
    ty = round(top + r)
    if night:
        mx, my = cx + r * 0.38, top + r * 0.55
        for (x, y) in glass:
            dx, dy = x + 0.5 - mx, y + 0.5 - my
            d = math.hypot(dx, dy)
            if d < 2.8:
                lam = max(0.0, -(dx * LX + dy * LY) / 2.8 + 0.45)
                p.px(x, y, MOON[min(6, 3 + round(lam * 3))])
        rnd = random.Random(top)
        for i in range(12):
            sx, sy = x0 + 1 + rnd.randrange(w - 2), top + 2 + rnd.randrange(foot - top - 6)
            if (sx, sy) in glass and math.hypot(sx - mx, sy - my) > 4.5 and sx != xm and sy != ty:
                p.px(sx, sy, FLAME[3] if i % 3 else FLAME[4], p.twinkle(i, back=False) if motion and i % 2 else "base")
    if night and foot - ty > rain.H + 2 and xm - x0 > rain.W:
        rain.write(p, x0 + 1, foot - rain.H - 2, "ki", FLAME[1])
    for y in range(top + 1, foot):
        if (xm, y) in glass:
            p.px(xm, y, _g(3, night))
    for x in range(x0, x1):
        if (x, ty) in glass:
            p.px(x, ty, _g(3, night))
    p.hline(x0 - 1, x1 + 1, foot, _g(5, night))
    p.hline(x0 - 1, x1 + 1, foot + 1, _g(2, night))


def curtain(p: Pix, x, top, foot, night: bool, flip=False):
    """A drape of red velvet hung beside the window from row `top` to `foot`, gathered at its middle by a gold
    tassel, its folds lit on their left."""
    for y in range(top, foot):
        t = (y - top) / max(1, foot - top)
        pinch = 1 if 0.45 < t < 0.6 else 0
        for i in range(4 - pinch):
            p.px(x + (3 - i if flip else i), y, tone("carpet", (5, 4, 3, 4)[i] - 1, night))
    ty = top + round((foot - top) * 0.52)
    tx = x + (0 if flip else 2)
    p.px(tx, ty, _g(5, night))
    p.px(tx + 1, ty, _g(3, night))
    p.px(tx, ty + 1, _g(4, night))
    p.px(tx, ty + 2, _g(2, night))


def newel_lamp(p: Pix, nx, g, night: bool, motion: bool, phase: int = 0):
    """A newel post of marble three units wide at column nx, from the floor at row g, its cap gilded, and on it a gilt
    lamp of three candles burning on the hand's phosphor."""
    for y in range(g - 9, g + 1):
        p.px(nx, y, tone("marble", 5, night))
        p.px(nx + 1, y, tone("marble", 4, night))
        p.px(nx + 2, y, tone("marble", 2, night))
    p.hline(nx - 1, nx + 4, g - 10, _g(5, night))
    p.hline(nx - 1, nx + 4, g - 9, _g(2, night))
    p.px(nx + 1, g - 11, _g(4, night))
    p.px(nx + 1, g - 12, _g(5, night))
    p.hline(nx - 1, nx + 4, g - 13, _g(4, night))
    p.px(nx - 1, g - 13, _g(5, night))
    p.px(nx + 3, g - 13, _g(2, night))
    for i, (cx, h) in enumerate(((nx - 1, 2), (nx + 1, 3), (nx + 3, 2))):
        candle(p, cx, g - 14, h, night, motion, phase=(i + phase) % 3)
    lamp(p, nx + 1.5, g - 17, 10)
    glow(p, nx + 1.5, g - 17, 9, 8, night)


def staircase(p: Pix, x0, x1, g, steps: int, night: bool, motion: bool) -> tuple:
    """A grand staircase seen from its foot, from column x0 to x1 at the floor on row g, climbing `steps` steps that
    narrow as they rise: marble treads lit on top and risers in half light, the red carpet down their middle over the
    treads and risers with a gold border, held into each step by a brass rod, and on each side a balustrade of marble
    balusters under a mahogany rail that closes in as it climbs, a lamp on the newel post at its foot. Returns the
    landing's columns and row: (left, right, row)."""
    def m(i):
        return tone("marble", i, night)

    def red(i):
        return tone("carpet", i, night)
    cx2 = x0 + x1                     # twice the middle, so an even or odd width centres alike
    edges = []
    for i in range(steps):
        inset = round(i * 0.7)
        lx, rx = x0 + inset, x1 - inset
        tread = g - 2 - 3 * i
        half = 6 - i * 0.28
        cl, cr = math.floor(cx2 / 2 - half), math.ceil(cx2 / 2 + half)
        for x in range(lx, rx + 1):
            on = cl <= x <= cr
            border = x in (cl, cr)
            p.px(x, tread, (_g(4, night) if border else red(5)) if on else m(6))
            p.px(x, tread + 1, (_g(3, night) if border else red(3)) if on else m(4))
            p.px(x, tread + 2, (_g(5, night) if x < cx2 / 2 else _g(3, night)) if on else m(3))
        p.px(lx, tread, m(5))
        p.px(rx, tread + 1, m(2))
        p.px(rx, tread + 2, m(2))
        edges.append((lx, rx, tread))
    lx, rx, tread = edges[-1]
    p.hline(lx - 1, rx + 2, tread - 1, m(5))
    p.hline(lx - 1, rx + 2, tread - 2, m(3))
    for side in (-1, 1):
        rail = []
        for i, (lx, rx, tread) in enumerate(edges):
            bx = lx - 1 if side < 0 else rx + 1
            hb = 6 - i // 3
            for j in range(hb):
                p.px(bx, tread + 2 - j, m(5) if j in (1, hb - 2) else m(3) if j == 0 else m(4))
            rail.append((bx, tread + 2 - hb))
            p.px(bx - side, tread + 2, m(2))
        for (ax, ay), (bx, by) in zip(rail, rail[1:]):
            for t in range(4):
                xx, yy = round(ax + (bx - ax) * t / 3), round(ay + (by - ay) * t / 3)
                p.px(xx, yy, tone("wood", 2, night))
                p.px(xx, yy - 1, tone("wood", 4, night))
        newel_lamp(p, x0 - 3 if side < 0 else x1 + 1, g, night, motion, phase=side + 1)
    return (edges[-1][0] - 1, edges[-1][1] + 1, edges[-1][2] - 1)


# A crystal chandelier, 29 units wide and 31 tall, drawn by hand: its chain and crown, an upper ring of four candles on
# curling arms, a lower ring of six on a deeper hoop seen a little from below, crystal knops on its stem, drops and
# swags of crystal hung all round, and a bowl of crystal ending in a great drop. o is the gilt's outline, g G h H the
# gilt light to deep, w W the candles' wax, k K j the crystal light to dark, and f a flame's foot, where it burns.
CHANDELIER = [
    "..............o..............",
    "..............g..............",
    "..............H..............",
    "..............g..............",
    "............oGgGo............",
    "...........oHhghHo...........",
    "..............k..............",
    ".....f.......jKj.......f.....",
    ".....w........G........w.....",
    ".....W...f....G....f...W.....",
    "....gGh..w...kKj...w..gGh....",
    ".....oGg.W....G....W.gHo.....",
    "......oGgGh..oGo..gGhHo......",
    "........oHGgGgGgGhGHo........",
    "........k.K.j.K.j.K.k........",
    "..f.....j...k.K.k...j.....f..",
    "..w....K.k..j.G.j..k.K....w..",
    "..W.f....j...kKj...j....f.W..",
    ".gGhw.......jKkKj.......wgHh.",
    "..oGW.....oGgGgGgGHo....WGo..",
    "...oGg..ogGhHGgGhHhGHo..gHo..",
    "....oGgGgHhoK.GkG.KoHGgHGo...",
    "....k.oHHhGgGgGgGhGhHHo.k....",
    "....j.k.j.k.j.K.j.k.j.k.j....",
    "....K.j.K.j.k.k.k.j.K.j.K....",
    "......K...K..jKj..K...K......",
    "..........j..kKk..j..........",
    "..............K..............",
    ".............jKj.............",
    ".............kKj.............",
    "..............j..............",
]


def _chandelier(q: Pix, cx, top, night: bool, motion: bool):
    """The chandelier drawn on `q`, its chain's top at (cx, top)."""
    x0 = cx - len(CHANDELIER[0]) // 2
    crystal = (lambda i: FLAME[max(0, i - 1)]) if night else (lambda i: CRYSTAL[i if i == 6 else i - 1])
    pal = {"o": GOLD[1], "g": _g(5, night), "G": _g(4, night), "h": _g(3, night), "H": _g(2, night),
           "w": tone("linen", 6, night), "W": tone("linen", 4, night),
           "k": crystal(6), "K": crystal(5), "j": crystal(3)}
    sparks = []
    for j, row in enumerate(CHANDELIER):
        for i, ch in enumerate(row):
            if ch == "f":
                flame(q, x0 + i, top + j, motion, phase=i % 3)
            elif ch in pal:
                q.px(x0 + i, top + j, pal[ch])
                if ch == "k" and j > 12:
                    sparks.append((x0 + i, top + j))
    if motion:
        for n, (sx, sy) in enumerate(sparks[::2]):
            q.px(sx, sy, C["white"] if not night else FLAME[6], q.twinkle(n))
    if night:
        q.halo(cx + 0.5, top + 18, 22, 16, FLAME[3], GLOW)


def chandelier(p: Pix, cx, top, night: bool, motion: bool, drop: int = 0) -> tuple:
    """The crystal chandelier (see `CHANDELIER`) hung from row `top` on column cx, `drop` units of chain more than
    its own above it. Its candles burn on the hand's phosphor; by night their light fills its crystal and falls round
    it, and in a moving header its crystal glitters. It is drawn once a file and placed as often as the hall hangs
    one, its flames flickering and its crystal glittering wherever it hangs. Returns its box."""
    for y in range(top, top + drop):
        p.px(cx, y, _g(4, night) if (y - top) % 2 == 0 else _g(2, night))
    p.stamp(("chandelier", night, motion), lambda q, ox, oy: _chandelier(q, ox, oy, night, motion), cx, top + drop,
            pad=40)
    lamp(p, cx + 0.5, top + drop + 17, 17)
    w = len(CHANDELIER[0])
    return (cx - w // 2, top, cx - w // 2 + w, top + drop + len(CHANDELIER))


def hall(p: Pix, x0, x1, g, night: bool, motion: bool, top: int = TOP) -> tuple:
    """The chateau's hall between columns x0 and x1, standing on the floor at row g: a marble column at each side
    framing the grand staircase, which climbs to a landing under a tall arched window hung with red drapes, and over
    it the crystal chandelier hung from the frieze (or from row `top`), the stair taking as many steps as leave the
    window clear of the chandelier, ten at the most, and the chandelier's chain let down to hang it midway over a
    taller stair. Returns the span of the floor it covers."""
    steps = max(5, min(10, (g - top - len(CHANDELIER) - 27) // 3))
    lx, rx, ly = staircase(p, x0 + 10, x1 - 10, g, steps, night, motion)
    wx0, wx1 = lx + 2, rx - 1
    window(p, wx0, wx1, ly - 22, ly - 2, night, motion)
    curtain(p, wx0 - 4, ly - 23, ly - 2, night)
    curtain(p, wx1, ly - 23, ly - 2, night, flip=True)
    p.hline(wx0 - 5, wx1 + 5, ly - 24, _g(5, night))
    p.hline(wx0 - 5, wx1 + 5, ly - 23, _g(2, night))
    column(p, x0, top + 1, g, night)
    column(p, x1 - 6, top + 1, g, night)
    drop = max(0, (ly - 28 - top - len(CHANDELIER)) // 2)
    chandelier(p, (x0 + x1) // 2, top, night, motion, drop=drop)
    if night:
        light_on(p, (x0 + x1) / 2, g - 6, 16, 9, (0.1, 0.2, 0.3), set(MARBLE) | set(CARPET))
        pool(p, (x0 + x1) / 2, g, 24)
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the banquet
SWORD = 24        # how far a sword's blade reaches along each axis from its guard to its point


def sword(p: Pix, hx, hy, d: int, night: bool):
    """A rapier hung on the wall, its hilt at (hx, hy) and its blade climbing to its point `SWORD` units up and across
    the way `d` points (1 to the right, -1 to the left): a steel blade lit along its upper edge, quillons of gilt at
    right angles to it and a swept cup over the hand, a grip bound in wire and a round pommel."""
    for i in range(1, SWORD + 1):
        x, y = hx + d * i, hy - i
        p.px(x, y, tone("steel", 6 if i == SWORD else 5, night))
        if i < SWORD:
            p.px(x, y + 1, tone("steel", 2, night))
    for j in (-3, -2, -1, 1, 2, 3):
        p.px(hx + j, hy + d * j, _g(5 if j < 0 else 3, night))
    p.px(hx - 3, hy - 3 * d + 1, _g(4, night))
    p.px(hx + 3, hy + 3 * d - 1, _g(2, night))
    p.px(hx, hy, _g(6, night))
    p.px(hx - d, hy - 1, _g(4, night))
    p.px(hx, hy + 1, _g(3, night))
    p.px(hx + d, hy + 1, _g(2, night))
    p.px(hx + d, hy, _g(3, night))
    for i in range(1, 4):
        p.px(hx - d * i, hy + i, tone("wood", 2, night) if i % 2 else _g(3, night))
    p.px(hx - d * 4, hy + 4, _g(5, night))
    p.px(hx - d * 5, hy + 4, _g(3, night))
    p.px(hx - d * 4, hy + 5, _g(2, night))
    p.px(hx - d * 5, hy + 5, _g(1, night))


SHIELD = [
    "ooooooooooooo",
    "ogggggggggggo",
    "ogrrrrrrrrRho",
    "ogrrrrlrrrRho",
    "ogrrrlllrrRho",
    "ogrlrrlrrlRho",
    "ogrllrlrllRho",
    "ogrrlllllrRho",
    "ogrrrrlrrrRho",
    "ogrrrlllrrRho",
    ".ogrrrrrrRho.",
    ".ogrrrrrrRho.",
    "..ogrrrrRho..",
    "...ogrrRho...",
    "....oghho....",
    ".....ooo.....",
]


def shield(p: Pix, cx, top, night: bool):
    """A gilded shield thirteen units wide, its field of red velvet charged with a gold lily, its rim lit along its
    top and left."""
    pal = {"o": GOLD[1], "g": _g(5, night), "h": _g(2, night), "r": tone("carpet", 4, night),
           "R": tone("carpet", 2, night), "l": _g(5, night)}
    p.sprite(cx - 6, top, SHIELD, pal)


def trophy(p: Pix, cx, cy, night: bool):
    """Two rapiers crossed on the wall behind a gilded shield, the crossing at (cx, cy)."""
    half = SWORD // 2
    sword(p, cx - half, cy + half, 1, night)
    sword(p, cx + half, cy + half, -1, night)
    shield(p, cx, cy - 7, night)


def sconce(p: Pix, cx, top, night: bool, motion: bool, phase: int = 0):
    """A gilt sconce on the wall, its shell-shaped backplate's top on row `top` at column cx, two arms curling out of
    it with a candle on each, burning on the hand's phosphor."""
    for j, (a, b) in enumerate(((0, 0), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (0, 0), (0, 0), (0, 0))):
        for i in range(a, b + 1):
            p.px(cx + i, top + j, _g(5 if i < 0 else 4 if i == 0 else 2, night))
    for d in (-1, 1):
        p.px(cx + d * 2, top + 6, _g(4 if d < 0 else 3, night))
        p.px(cx + d * 3, top + 5, _g(5 if d < 0 else 3, night))
        p.px(cx + d * 3, top + 4, _g(5, night))
        p.px(cx + d * 3 - 1, top + 4, _g(4, night))
        p.px(cx + d * 3 + 1, top + 4, _g(2, night))
        candle(p, cx + d * 3, top + 3, 3, night, motion, phase=(phase + d) % 3)
    lamp(p, cx + 0.5, top + 2, 9)
    glow(p, cx + 0.5, top + 1, 9, 8, night)


def goblet(p: Pix, x, foot, night: bool):
    """A gilt goblet three units wide on row `foot`, red wine standing in its bowl."""
    p.px(x - 1, foot - 4, tone("carpet", 1, night))
    p.px(x, foot - 4, tone("carpet", 3, night))
    p.px(x + 1, foot - 4, tone("carpet", 1, night))
    p.px(x - 1, foot - 3, _g(5, night))
    p.px(x, foot - 3, _g(4, night))
    p.px(x + 1, foot - 3, _g(2, night))
    p.px(x, foot - 2, _g(3, night))
    p.px(x, foot - 1, _g(4, night))
    p.px(x - 1, foot, _g(5, night))
    p.px(x, foot, _g(3, night))
    p.px(x + 1, foot, _g(2, night))


def candelabrum(p: Pix, cx, foot, night: bool, motion: bool):
    """A five-branched candelabrum of gilt standing on row `foot`: a domed foot, a knopped stem, two pairs of arms
    curling up from it to cups at three heights, and a candle on each, the middle one tallest."""
    p.hline(cx - 3, cx + 4, foot, _g(2, night))
    p.hline(cx - 2, cx + 3, foot - 1, _g(4, night))
    p.px(cx - 2, foot - 1, _g(5, night))
    for y in range(foot - 13, foot - 1):
        p.px(cx, y, _g(6, night) if y % 4 == 0 else _g(4, night))
    p.px(cx - 1, foot - 6, _g(5, night))
    p.px(cx + 1, foot - 6, _g(2, night))
    for d, reach, cup in ((-1, 6, 11), (1, 6, 11), (-1, 3, 13), (1, 3, 13)):
        y0 = foot - cup + 4
        for i in range(1, reach + 1):
            y = y0 - round(3 * (i / reach) ** 2)
            p.px(cx + d * i, y, _g(5 if d < 0 else 3, night))
        top = y0 - 4
        p.px(cx + d * reach, top, _g(5, night))
        p.px(cx + d * reach - 1, top, _g(4, night))
        p.px(cx + d * reach + 1, top, _g(2, night))
        candle(p, cx + d * reach, top - 1, 3, night, motion, phase=(reach + d) % 3)
    p.hline(cx - 1, cx + 2, foot - 14, _g(5, night))
    p.px(cx + 1, foot - 14, _g(2, night))
    candle(p, cx, foot - 15, 4, night, motion, phase=0)
    lamp(p, cx + 0.5, foot - 10, 17)
    glow(p, cx + 0.5, foot - 15, 13, 11, night)


def cake(p: Pix, cx, foot, night: bool):
    """A tiered chocolate cake on a gilt stand on row `foot`: three tiers of chocolate, each smaller than the one under
    it, iced white along their tops with the icing dripping down their sides, gold pearls round their feet, and a
    cherry on top."""
    p.hline(cx - 3, cx + 4, foot, _g(2, night))
    p.px(cx, foot - 1, _g(4, night))
    p.hline(cx - 7, cx + 8, foot - 2, _g(5, night))
    p.px(cx + 7, foot - 2, _g(2, night))
    y = foot - 3
    for half, tall in ((6, 5), (4, 4), (2, 3)):
        for j in range(tall):
            for i in range(-half, half + 1):
                p.px(cx + i, y - j, tone("cocoa", 5 if i < -half + 2 else 4 if i < 1 else 3 if i < half else 2,
                                         night))
        top = y - tall + 1
        for i in range(-half, half + 1):
            p.px(cx + i, top, tone("linen", 6 if i < 1 else 4, night))
            if (i + half) % 2 == 0 and i not in (-half, half):
                p.px(cx + i, top + 1, tone("linen", 5, night))
                if (i + half) % 4 == 0:
                    p.px(cx + i, top + 2, tone("linen", 4, night))
        for i in range(-half, half + 1, 2):
            p.px(cx + i, y, _g(5 if i < 0 else 4, night))
        y = top - 1
    p.px(cx, y, tone("carpet", 4, night))
    p.px(cx + 1, y, tone("carpet", 2, night))
    p.px(cx, y - 1, tone("carpet", 5, night))
    p.px(cx + 1, y - 2, tone("wood", 3, night))


def table(p: Pix, x0, x1, top, g, night: bool):
    """The banquet table from column x0 to its end at x1, its top on row `top`: white linen laid over it, lit along
    its top and falling to a hem a unit over the floor at row g in folds lit on their left, a gold fringe along the
    hem; a runner of red velvet bordered in gold laid down its middle and over its end, fringed in gold."""
    def ln(i):
        return tone("linen", i, night)
    p.hline(x0, x1 + 1, top, ln(6))
    p.hline(x0, x1 + 1, top + 1, ln(4))
    for x in range(x0, x1 + 1):
        f = (x - x0) % 6
        for y in range(top + 2, g - 1):
            p.px(x, y, ln((5, 5, 4, 3, 3, 4)[f]))
        hem = g - 2 + (1 if f in (1, 2, 3) else 0)
        p.px(x, hem, _g(4 if f < 3 else 3, night))
        if f in (0, 4):
            p.px(x, hem + 1, _g(2, night))
    for y in range(top, g):
        p.px(x1 + 1, y, ln(2))
        if y > top + 1:
            p.px(x1 + 2, y, ln(1))
    # the runner, on the top and over the end
    p.hline(x0, x1 + 2, top, tone("carpet", 4, night))
    for y in range(top, top + 9):
        p.px(x1 + 1, y, tone("carpet", 3, night))
        p.px(x1 + 2, y, tone("carpet", 2, night))
    p.px(x1 + 1, top + 9, _g(5, night))
    p.px(x1 + 2, top + 9, _g(3, night))
    p.px(x1 + 1, top + 10, _g(3, night))


# A guest of the chateau, 17 units wide and 32 tall, facing us and nearer than the hall: dark glasses and his hair
# slicked back, a long dark coat hanging open over a dark suit and flaring at its hem, and a sword drawn and held low
# in his right hand. h H his hair, s S t his skin light to shade, G his glasses and q their glint, k c C the coat dark
# to light, v his shirt, p his trousers and b his shoes, y the sword's hilt and e its blade.
GUEST = [
    ".......hhh.......",
    "......hHHHh......",
    "......hsssh......",
    "......GqGGG......",
    "......tsssS......",
    ".......tsS.......",
    ".......kvk.......",
    ".....kcCvCCk.....",
    "....kcCCvCCCk....",
    "....kcCkvkCCk....",
    "...kcCCkvkCCCk...",
    "...kcCkkvkkCCk...",
    "...kcCkvvvkCCk...",
    "...kcCkvvvkCCk...",
    "..kcCCkpvpkCCCk..",
    "..scCCkpppkCCCs..",
    ".y.cCCkpppkCCCk..",
    "e..cCCkpkpkCCCk..",
    "e..cCCkpkpkCCCCk.",
    "e.kcCCkpkpkCCCCk.",
    "e.kcCCkpkpkkCCCk.",
    "e.kcCCkpkpk.kCCCk",
    "e.kcCC.pkp..kCCCk",
    "e.kcCC.pkp...kCCk",
    "e.kcC..pkp....kCk",
    "..kk...pkp.....kk",
    ".......p.p.......",
    ".......p.p.......",
    ".......p.p.......",
    "......pp.pp......",
    ".....bbb.bbb.....",
    "....bbbb.bbbb....",
]


def guest(p: Pix, x, g, night: bool, motion: bool = False):
    """The guest (see `GUEST`) standing on the floor at row g with his art's left at column x. His skin keeps its tone
    by night, as the hand's canon has it, and takes the candles' green light, which glints in his glasses too; in a
    moving header a glint crosses his glasses once every six seconds, as he turns his head to the light."""
    skin = RAMP["skin1"]
    pal = {"h": tone("hair", 1, night), "H": tone("hair", 3, night), "s": skin[4], "S": skin[3], "t": skin[2],
           "G": RAMP["cloth"][0], "q": FLAME[4] if night else CRYSTAL[3], "k": tone("cloth", 1, night),
           "c": tone("cloth", 4, night), "C": tone("cloth", 3, night), "v": tone("cloth", 2, night),
           "p": tone("cloth", 2, night), "b": RAMP["cloth"][0], "y": _g(4, night),
           "e": STEEL[4] if night else STEEL[2]}
    top = g - len(GUEST) + 1
    p.sprite(x, top, GUEST, pal)
    if night:
        p.halo(x + 8.5, top + 3, 3.5, 4, FLAME[4], (0.12, 0.2), L="base", only=set(skin))
    if motion:
        for n, col in enumerate((7, 9)):
            L = p.seq(f"gg{n}", 0.5 + n * 0.02, 0.52 + n * 0.02, 6.0, z=1)
            p.px(x + col, top + 3, FLAME[6] if night else C["white"], L)


def banquet(p: Pix, x0, x1, g, night: bool, motion: bool, trophy_y=None, sconce_y=None) -> tuple:
    """The banquet from column x0 to x1, standing on the floor at row g: the end of the long table in its linen and
    its runner, the candelabrum, the tiered cake and goblets of wine on it; on the wall over it two swords crossed
    behind a gilded shield, their crossing on row `trophy_y`, between a pair of sconces on row `sconce_y` (where a
    header's frieze sets them unless told, and none where a row is False); and a guest in a long dark coat standing
    before the table with a sword drawn. Returns the span of the floor it covers."""
    top = g - 13
    end = x1 - 4
    table(p, x0 + 6, end, top, g, night)
    candelabrum(p, x0 + 22, top - 1, night, motion)
    cake(p, end - 8, top - 1, night)
    goblet(p, x0 + 30, top - 1, night)
    goblet(p, end - 1, top - 1, night)
    if trophy_y is not False:
        trophy(p, x0 + 26, min(TOP + 29, top - 45) if trophy_y is None else trophy_y, night)
    if sconce_y is not False:
        sy = min(TOP + 11, top - 63) if sconce_y is None else sconce_y
        sconce(p, x0 + 5, sy, night, motion, phase=1)
        sconce(p, x1 - 4, sy, night, motion, phase=2)
    guest(p, x0, g, night, motion)
    if night:
        light_on(p, x0 + 22.5, top + 1, 22, 10, (0.1, 0.2, 0.32), set(LINEN))
        pool(p, x0 + 26, g, 30)
    return (x0 - 1, x1 + 3)


def light_on(p: Pix, cx, cy, rx, ry, alphas, only: set):
    """By night a candle's or the fire's green light laid over what stands near it, in rings, on the pixels of the
    colours `only`; a drawing made lighter goes without it, its last pass still lighting what stands nearest."""
    if p not in THIN:
        p.halo(cx, cy, rx, ry, FLAME[4], alphas, L="base", only=only)


def pool(p: Pix, cx, g, rx):
    """By night the candles' green light pooled on the floor at row g round column cx, `rx` units each way."""
    p.halo(cx, g - 1.5, rx, 3.5, FLAME[3], (0.12, 0.22, 0.34)[1 if p in THIN else 0:], L="pool", shape=True)


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


def runner(p: Pix, x0, x1, y, night: bool):
    """The red carpet laid along the floor from column x0 to x1 over the rule on row y, from the foot of the stair to
    the banquet, wherever no word lies near: its top lit, its edge in shade with a gold border, and a gold fringe at
    each end."""
    for a, b in _clear_runs(p, x0, x1, y - 3, y - 1):
        p.hline(a, b, y - 3, _g(4, night))
        p.hline(a, b, y - 2, tone("carpet", 4, night))
        p.hline(a, b, y - 1, tone("carpet", 2, night))
        for x in (a, b - 1):
            p.vline(x, y - 3, y, _g(5, night) if x == a else _g(3, night))


# --------------------------------------------------------------------------- the shimmer of the crystal
def shimmer(p: Pix, night: bool, motion: bool, avoid, keep=None, n: int = 24, seed: int = 9):
    """The light the chandeliers' crystal throws across the silk behind the title: sparse glints from under the frieze
    down to two rows above the words under the title (the second box of `avoid`), never in the box the month's mark
    takes (`keep`), gold by day and the candles' green by night, a few of them small stars, twinkling behind the
    drawing in a moving header; half of them on a drawing made lighter, each twinkling layer keeping some."""
    if p.w < 300 or len(avoid) < 2:
        return
    rnd = random.Random(seed)
    y1 = avoid[1][1] - 3
    for i in range(n):
        x, y = rnd.randrange(EDGE + 2, p.w - EDGE - 2), rnd.randrange(TOP + 2, y1)
        if keep and keep[0] - 2 <= x < keep[2] + 2 and keep[1] - 2 <= y < keep[3] + 2:
            continue
        if p in THIN and i % 6 >= 3:
            continue
        L = p.twinkle(i, back=True) if motion else "haze"
        star = rnd.random() < 0.25
        p.px(x, y, (FLAME[6] if star else FLAME[4]) if night else (C["white"] if star else GOLD[4]), L)
        if star:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(x + dx, y + dy, FLAME[3] if night else GOLD[4], L)


# --------------------------------------------------------------------------- the salon: the fireplace (H2)
FIRE_HALF = 30        # half the width of the fireplace's surround, its mantel overhanging it by two
FIRE_TALL = 36        # the rows from the hearth to the mantel's shelf
MIRROR_LEAST = 18     # the fewest rows the mirror over the mantel is drawn in
TORCH_TALL = 58       # the rows from the floor to the cups of a torchere's candles


def _pilaster(p: Pix, x0, top, foot, night: bool):
    """A fluted marble pilaster nine units wide from row `top` to `foot`: a gilt capital and base, and between them
    its flutes, lit along their left edges."""
    for y in range(top, foot + 1):
        for i in range(9):
            if y < top + 2 or y > foot - 2:
                c = _g((5, 5, 4, 4, 4, 3, 3, 2, 1)[i], night) if y in (top, foot - 1) else _g(2, night)
            elif i in (0, 8):
                c = tone("marble", 5 if i == 0 else 2, night)
            elif i % 2 == 1:
                c = tone("marble", 6 if i < 4 else 5, night)
            else:
                c = tone("marble", 3, night)
            p.px(x0 + i, y, c)


def _clock(p: Pix, cx, foot, night: bool):
    """A gilt mantel clock nine units wide on row `foot`: a waisted case under a domed top, its white dial with the
    hands at ten to two, a pendulum's window under it."""
    rows = ["...ggh...", "..gGGGh..", ".gGwwwGh.", ".gwwkwwh.", ".gwkkwwh.", ".gwwwwwh.", ".gGwwwGh.",
            "..gGGGh..", "..gkGkh..", "..gGGGh..", ".gGGGGGh.", "ggGGGGGhh"]
    pal = {"g": _g(5, night), "G": _g(4, night), "h": _g(2, night), "w": tone("linen", 6, night),
           "k": RAMP["cloth"][1]}
    p.sprite(cx - 4, foot - len(rows) + 1, rows, pal)


def _branch(p: Pix, cx, foot, night: bool, motion: bool, phase: int = 0):
    """A three-branched candelabrum of gilt on the mantel, standing on row `foot`, its candles burning green."""
    p.hline(cx - 1, cx + 2, foot, _g(2, night))
    p.px(cx, foot - 1, _g(4, night))
    p.px(cx, foot - 2, _g(5, night))
    p.px(cx, foot - 3, _g(4, night))
    p.hline(cx - 2, cx + 3, foot - 4, _g(4, night))
    p.px(cx - 2, foot - 5, _g(5, night))
    p.px(cx + 2, foot - 5, _g(3, night))
    p.px(cx, foot - 5, _g(4, night))
    for i, (x, h) in enumerate(((cx - 2, 3), (cx, 4), (cx + 2, 3))):
        candle(p, x, foot - 6, h, night, motion, phase=(phase + i) % 3)
    lamp(p, cx + 0.5, foot - 9, 12)
    glow(p, cx + 0.5, foot - 9, 8, 7, night)


# A chandelier as the pier glass catches it from across the salon, 13 by 9: c its crystal and gilt, a shade deeper
# than the glass, and f its candles' green flames.
REFLECTION = ["..f...c...f..", "..c...c...c..", "..c.f.c.f.c..", "..ccccccccc..", ".c..c.c.c..c.", "c...c.c.c...c",
              "....c.c.c....", ".....ccc.....", "......c......"]


def mirror(p: Pix, cx, top, foot, night: bool, motion: bool):
    """A tall pier glass over the mantel, its gilt frame from row `top` to `foot` under a crest of gilt scrolls, the
    glass catching the room: a chandelier across the salon reflected in it, its flames green, a pale sheen slanting
    across it by day, and by night the dark of the salon with the fire's green and the crystal glinting in it."""
    x0, x1 = cx - 19, cx + 20
    crest = ["....ooo....", "..ooGgGoo..", ".oGgwGgGho.", "oGgo.g.ohGo", ".oo..g..oo.", ".....o....."]
    pal = {"o": GOLD[1], "g": _g(5, night), "G": _g(4, night), "h": _g(2, night), "w": _g(6, night)}
    p.sprite(cx - 5, top - len(crest) + 2, crest, pal)
    for y in range(top, foot + 1):
        for x in range(x0, x1):
            edge = min(x - x0, x1 - 1 - x, y - top, foot - y)
            if edge == 0:
                c = GOLD[1]
            elif edge == 1:
                c = _g(5 if (x - x0 < 2 or y - top < 2) else 2, night)
            elif edge == 2:
                c = _g(4 if (x + y) % 4 else 6, night)
            elif edge == 3:
                c = GOLD[1]
            elif night:
                c = WINE[1] if (x - y) % 11 > 2 else WINE[3]
            else:
                c = CRYSTAL[5] if (x - y) % 11 > 2 else CRYSTAL[6]
                if y > foot - (foot - top) // 3:
                    c = CRYSTAL[4] if (x - y) % 11 > 2 else CRYSTAL[5]
            p.px(x, y, c)
    ghost = {"c": CRYSTAL[3] if not night else WINE[4], "f": FLAME[3]}
    for j, row in enumerate(REFLECTION):
        for i, ch in enumerate(row):
            if ch in ghost:
                p.px(cx - len(row) // 2 + i, top + 4 + j, ghost[ch])
    mid = (top + foot) // 2
    rnd = random.Random(top * 7 + cx)
    for i in range(5):
        gx, gy = rnd.randrange(x0 + 5, x1 - 5), rnd.randrange(top + 5, max(top + 6, mid))
        L = p.twinkle(i + 1) if motion and i % 2 else "base"
        p.px(gx, gy, FLAME[4] if night else C["white"], L)
    if night:
        for dx in (-12, -10, 10, 12):
            p.px(cx + dx, foot - 5, FLAME[2])
            p.px(cx + dx, foot - 6, FLAME[1])


def _tongue(h: int, w: float, lean: float = 0.0) -> dict:
    """A tongue of flame `h` rows tall and `w` units either side of its axis at its widest, a third of the way up,
    leaning `lean` units a row: its cells {(dx, dy): tone}, dy counted up from its foot, white-hot down its heart and
    greener toward its edges and its tip."""
    cells = {}
    for dy in range(h):
        t = dy / max(1, h - 1)
        half = w * (0.55 + 0.45 * t / 0.25) if t <= 0.25 else w * (1 - (t - 0.25) / 0.75) ** 1.4
        axis = lean * dy + 0.6 * math.sin(dy * 1.3 + w) * t
        for dx in range(math.floor(axis - half), math.ceil(axis + half) + 1):
            d = abs(dx - axis) / max(half, 0.5)
            if d > 1:
                continue
            tone_ = 6 if d < 0.34 and t < 0.45 else 5 if d < 0.6 and t < 0.65 else 4 if d < 0.85 and t < 0.85 else 3
            cells[(dx, dy)] = tone_
    return cells


def fire(p: Pix, cx, g, night: bool, motion: bool):
    """The fire in the hearth, on row g at column cx: two logs on their andirons and three flames over them, the middle
    one the tallest, burning on the hand's phosphor as every flame in the chateau does, white-hot at their hearts, a
    green tongue leaping from each and flickering on its own phase of the engine's flicker, a spark or two of the code
    rising over them."""
    for x in range(cx - 11, cx + 12):
        p.px(x, g - 3, tone("wood", 4 if x % 5 else 5, night))
        p.px(x, g - 2, tone("wood", 2, night))
    for x in range(cx - 8, cx + 9):
        p.px(x, g - 5, tone("wood", 5 if x % 4 else 6, night))
        p.px(x, g - 4, tone("wood", 3, night))
    for x in (cx - 13, cx + 13):
        for y in range(g - 6, g):
            p.px(x, y, _g(4 if y > g - 5 else 3, night))
        p.px(x, g - 7, _g(6, night))
        p.px(x, g - 8, _g(5, night))
        p.px(x - 1, g - 1, _g(2, night))
        p.px(x + 1, g - 1, _g(2, night))
    for base_x, h, w, lean in ((-7, 9, 2.6, 0.12), (7, 9, 2.6, -0.12), (0, 13, 3.4, 0.0)):
        for (dx, dy), t in _tongue(h, w, lean).items():
            p.px(cx + base_x + dx, g - 6 - dy, FLAME[t])
    tongues = ((-7, 9, 4, 1.4, 0.25), (0, 13, 6, 2.0, -0.15), (7, 9, 4, 1.4, -0.25))
    for phase, (base_x, rise, h, w, lean) in enumerate(tongues):
        L = p.flicker(phase) if motion else "base"
        for (dx, dy), t in _tongue(h + 2, w, lean).items():
            if dy >= 2:
                p.px(cx + base_x + dx, g - 6 - rise - dy + 2, FLAME[max(2, t - 1)], L)
    if motion:
        for i, (dx, dy) in enumerate(((-3, 14), (4, 16), (-1, 18), (2, 15))):
            p.px(cx + dx, g - 5 - dy, FLAME[4 - i % 3], p.twinkle(i))
    lamp(p, cx + 0.5, g - 9, 34)


def torchere(p: Pix, cx, g, tall: int, night: bool, motion: bool, phase: int = 0):
    """A torchere of gilt standing on the floor at row g on column cx, `tall` rows to the cups of its candles: a
    tripod foot, a slender knopped shaft, and a crown of five candles burning green over a drip pan hung with crystal
    drops."""
    p.hline(cx - 3, cx + 4, g, _g(2, night))
    p.hline(cx - 2, cx + 3, g - 1, _g(4, night))
    p.px(cx - 3, g - 1, _g(5, night))
    p.px(cx + 3, g - 1, _g(3, night))
    for y in range(g - tall + 4, g - 1):
        knop = (g - y) % 13 == 6
        p.px(cx, y, _g(6 if knop else 5, night))
        p.px(cx + 1, y, _g(4 if knop else 2, night))
        if knop:
            p.px(cx - 1, y, _g(5, night))
            p.px(cx + 2, y, _g(2, night))
    top = g - tall
    p.hline(cx - 4, cx + 6, top + 3, _g(4, night))
    p.hline(cx - 3, cx + 5, top + 4, _g(2, night))
    p.px(cx - 4, top + 3, _g(5, night))
    for i, dx in enumerate((-3, 4)):
        p.px(cx + dx, top + 5, tone("crystal", 6, night))
        p.px(cx + dx, top + 6, tone("crystal", 4, night))
    for i, (dx, h) in enumerate(((-4, 3), (-2, 4), (0, 5), (3, 4), (5, 3))):
        candle(p, cx + dx, top + 2, h, night, motion, phase=(phase + i) % 3)
    lamp(p, cx + 0.5, top - 3, 14)
    glow(p, cx + 0.5, top - 3, 10, 9, night)


def fireplace(p: Pix, cx, g, night: bool, motion: bool, room: int) -> tuple:
    """The salon's fireplace, centred on column cx and standing on the floor at row g: a hearth of marble, a surround
    of two fluted pilasters under a frieze carved with a gilt shell, the firebox's brick back in shadow and the fire
    burning in it (see `fire`), the mantel's shelf edged in gilt with a clock and two candelabra on it, over it a pier
    glass in a gilt frame (see `mirror`) as tall as the `room` rows over the floor leave it, and a torchere burning at
    either side (see `torchere`). By night the fire's green light pools on the hearth and the floor and is laid on the
    marble, the gilt and the brass near it. Returns the span of the floor it covers."""
    half = FIRE_HALF
    for x in range(cx - half - 4, cx + half + 5):
        p.px(x, g, tone("marble", 3, night))
        p.px(x, g - 1, tone("marble", 6 if x < cx + half + 3 else 4, night))
    shelf = g - FIRE_TALL
    _pilaster(p, cx - half, shelf + 3, g - 2, night)
    _pilaster(p, cx + half - 8, shelf + 3, g - 2, night)
    for y in range(shelf + 3, shelf + 9):
        for x in range(cx - half + 9, cx + half - 8):
            c = tone("marble", 5 if y == shelf + 3 else 4 if y < shelf + 7 else 2, night)
            p.px(x, y, c)
    shell = ["..ggg..", ".gGgGg.", "gGgGgGh", ".hhhhh."]
    p.sprite(cx - 3, shelf + 4, shell, {"g": _g(5, night), "G": _g(3, night), "h": _g(2, night)})
    for y in range(shelf + 9, g - 1):
        for x in range(cx - half + 9, cx + half - 8):
            inner = min(x - (cx - half + 9), cx + half - 9 - x)
            if inner == 0:
                c = tone("marble", 2, night)
            elif (y + (x // 4) % 2 * 2) % 4 == 0:
                c = RAMP["cocoa"][1]
            else:
                c = RAMP["cocoa"][2] if inner > 3 else RAMP["cocoa"][1]
            if night:
                c = WINE[0] if inner == 0 else (RAMP["cocoa"][2] if (y + (x // 4) % 2 * 2) % 4 else RAMP["cocoa"][3])
            p.px(x, y, c)
    fire(p, cx, g - 1, night, motion)
    for x in range(cx - half - 2, cx + half + 3):
        p.px(x, shelf, tone("marble", 6, night))
        p.px(x, shelf + 1, _g(5 if x % 6 else 6, night))
        p.px(x, shelf + 2, _g(2, night))
    _clock(p, cx, shelf - 1, night)
    _branch(p, cx - half + 4, shelf - 1, night, motion, phase=1)
    _branch(p, cx + half - 4, shelf - 1, night, motion, phase=2)
    top = max(TOP + 8, g - room + 6)
    if shelf - 13 - top >= MIRROR_LEAST:
        mirror(p, cx, top, shelf - 13, night, motion)
    tall = min(TORCH_TALL, room - 6)
    if tall >= FIRE_TALL:
        torchere(p, cx - half - 9, g, tall, night, motion, phase=0)
        torchere(p, cx + half + 8, g, tall, night, motion, phase=1)
    if night:
        light_on(p, cx, g - 10, half + 6, 14, (0.1, 0.18, 0.28), set(MARBLE) | set(GOLD))
        glow(p, cx + 0.5, g - 12, 26, 18, night)
        pool(p, cx, g, half + 10)
    return (cx - half - 13, cx + half + 13)


def section_mark(p: Pix, x, y, night: bool):
    """The goblet of red wine beside SECTION A-A, a gilt cup seven units tall, from a row over the words to one under
    them."""
    rows = [".rRRr.", "gRRRRh", ".grrh.", "..gh..", "..g...", "..G...", ".gGGh."]
    p.sprite(x, y - 1, rows, {"r": tone("carpet", 4, night), "R": tone("carpet", 3, night), "g": _g(5, night),
                              "G": _g(4, night), "h": _g(2, night)})


# --------------------------------------------------------------------------- the armoury: a suit of armour (H3)
# A suit of plate armour on its stand, 17 units wide and 31 tall, facing us: a plume of red velvet over a close helm
# with its visor down, a gilt gorget, pauldrons, a breastplate with a gilt rib, a gilt belt over the tassets, and
# cuisses, poleyns, greaves and sabatons. p P the plume, h H the helm lit and in shade, d the visor's slits, s S k the
# plate lit, mid and in shadow, g the gilt.
ARMOUR = [
    ".......ppp.......",
    "......ppPpp......",
    ".....pPPpp.......",
    "......hhhhH......",
    ".....hhhhhHH.....",
    ".....hdddddH.....",
    ".....hhhhhHH.....",
    ".....hdhdhdH.....",
    "......hhhHH......",
    ".......gGg.......",
    "...sssSSSSSSkk...",
    "..sssSsSSSSSSkk..",
    "..ssSksSSSSkSSk..",
    "..sSk.sSgSSk.SSk.",
    "..sSk.sSgSSk.SSk.",
    "..sSk.sSSSSk.SSk.",
    "..gSk.ssSSSk.Sgk.",
    "..sSk..sSSk..SSk.",
    "..sSk.gggggg.SSk.",
    "..ssk.sSSSSk.ssk.",
    "..kk..sSSSSk..kk.",
    "......sSkSSk.....",
    "......sSkSSk.....",
    "......sSkSSk.....",
    "......gSkgSk.....",
    "......sSksSk.....",
    "......sSksSk.....",
    "......sSksSk.....",
    "......sSksSk.....",
    ".....ssSkssSk....",
    ".....kkk.kkkk....",
]
ARMOUR_LEAST = 46     # the fewest rows the armour, its stand and its halberd stand in


def armour(p: Pix, cx, g, night: bool, motion: bool, room: int) -> tuple:
    """The suit of armour on its stand of marble, centred on column cx on the floor at row g (see `ARMOUR`), a halberd
    held upright at its side, its axe and spike of steel on an ash shaft, a torchere of gilt burning beside it (see
    `torchere`), and over it a banner of red velvet hung from a gilt rod at the top of the `room` rows over the floor
    (see `banner`), so that it rises their full height. By night the torchere's green light is laid on the plate,
    glints on the helm and pools on the floor. Returns the span of the floor it covers."""
    w, h = len(ARMOUR[0]), len(ARMOUR)
    banner(p, cx, g - room + 2, g - 9 - h - 3, night)
    for x in range(cx - 10, cx + 11):
        p.px(x, g, tone("marble", 2, night))
        p.px(x, g - 1, tone("marble", 4, night))
    for y in range(g - 6, g - 1):
        for x in range(cx - 8, cx + 9):
            c = tone("marble", 6 if x == cx - 8 else 2 if x == cx + 8 else 5 if y == g - 6 else 4, night)
            p.px(x, y, c)
    p.hline(cx - 9, cx + 10, g - 7, _g(5, night))
    p.hline(cx - 9, cx + 10, g - 8, _g(4, night))
    foot = g - 9
    pal = {"p": tone("carpet", 5, night), "P": tone("carpet", 3, night), "h": tone("steel", 6, night),
           "H": tone("steel", 4, night), "d": RAMP["cloth"][0], "s": tone("steel", 5, night),
           "S": tone("steel", 4, night), "k": tone("steel", 2, night), "g": _g(5, night), "G": _g(3, night)}
    x0 = cx - w // 2
    p.sprite(x0, foot - h + 1, ARMOUR, pal)
    hx = x0 + 1
    top = max(g - room + 2, foot - h - 9)
    for y in range(top + 6, foot + 1):
        p.px(hx, y, tone("wood", 5 if y % 7 else 6, night))
    head = ["...s.", "..sss", "sssSs", "ssSSs", ".sSSs", "..sS.", "..sS."]
    p.sprite(hx - 3, top, head, {"s": tone("steel", 6, night), "S": tone("steel", 3, night)})
    p.px(hx, foot - 13, tone("steel", 4, night))
    if motion:
        p.px(x0 + 6, foot - h + 5, C["white"] if not night else FLAME[5], p.twinkle(2))
    tall = min(TORCH_TALL, room - 4)
    torchere(p, cx + 15, g, max(30, tall), night, motion, phase=2)
    if night:
        light_on(p, cx + 6, foot - 14, 16, 18, (0.08, 0.16, 0.26), set(STEEL) | set(GOLD))
        pool(p, cx + 4, g, 20)
    return (cx - 11, cx + 20)


def banner(p: Pix, cx, top, foot, night: bool):
    """A banner of red velvet thirteen units wide hung over the armour from a gilt rod on row `top`, its finials lit,
    down to a forked tail ending on row `foot`, edged in gold and charged with the gold lily under its head; none where
    fewer than sixteen rows are left it."""
    if foot - top < 16:
        return
    for x in range(cx - 8, cx + 9):
        p.px(x, top, _g(5 if x < cx + 6 else 3, night))
        p.px(x, top + 1, _g(2, night))
    for x in (cx - 9, cx + 9):
        p.px(x, top, _g(6, night))
        p.px(x, top - 1, _g(5, night))
        p.px(x, top + 1, _g(3, night))
    for y in range(top + 2, foot + 1):
        fork = y - (foot - 5)
        for i in range(13):
            x = cx - 6 + i
            if fork > 0 and abs(i - 6) < fork + 1:
                continue
            edge = i in (0, 12) or y == top + 2
            c = _g(4 if i == 0 or y == top + 2 else 2, night) if edge else tone("carpet", 4 if i < 4 else 3, night)
            if not edge and i == 1:
                c = tone("carpet", 5, night)
            p.px(x, y, c)
    for j, row in enumerate(LILY):
        for i, ch in enumerate(row):
            if ch == "#":
                p.px(cx - 3 + i, top + 5 + j, _g(5 if i < 3 else 3, night))


def strip_mark(p: Pix, x, y, night: bool):
    """The small candelabrum beside a strip's title, its three candles burning green: nine units wide and twelve
    tall, raised so that its foot stays two rows clear of the tagline under the title."""
    foot = y + 4
    p.hline(x + 1, x + 8, foot, _g(2, night))
    p.hline(x + 2, x + 7, foot - 1, _g(4, night))
    p.px(x + 4, foot - 2, _g(5, night))
    p.px(x + 4, foot - 3, _g(4, night))
    p.hline(x + 1, x + 8, foot - 4, _g(4, night))
    p.px(x + 1, foot - 5, _g(5, night))
    p.px(x + 7, foot - 5, _g(3, night))
    p.px(x + 4, foot - 5, _g(5, night))
    for i, (cx, hh) in enumerate(((x + 1, 2), (x + 4, 3), (x + 7, 2))):
        candle(p, cx, foot - 6, hh, night, False, phase=i)


# --------------------------------------------------------------------------- on a phone
PHONE_SCENE = 64      # the rows a phone's H1 gives its hall and its banquet under its words
PHONE_LEAST = 48      # the fewest rows they are drawn in


def phone_chateau(p: Pix, g, night: bool, room: int) -> tuple:
    """The whole chateau across a phone under its words, standing on the floor at row g in the `room` rows free over
    it: the hall at the left, its columns, its stair and its window under the chandelier, and the banquet at the right,
    the guest before the table with his sword drawn and the trophy on the wall over it where the rows leave it room,
    the red carpet running between them. Returns the span of the floor it covers."""
    top = g - room
    hall(p, 5, 53, g, night, False, top=top)
    ty = g - 13 - 22
    banquet(p, 118, p.w - 5, g, night, False, trophy_y=ty if ty - 12 >= top + 1 else False, sconce_y=False)
    if room >= 56:
        chandelier(p, 86, top, night, False)
    return (4, p.w - 4)


# The rows a phone's H2 and H3 ask for under their words, whatever the words: room for the fireplace with its glass
# and its torcheres, and for the armour with its halberd and its torchere.
UNDER = {"H2": 70, "H3": 58}


def phone_salon(p: Pix, g, night: bool, room: int) -> tuple:
    """A phone's H2 under its words: the fireplace across the phone at the height the `room` rows leave it, the guest
    warming himself at its left, and at its right a side table in its linen with a candelabrum and a goblet on it."""
    fireplace(p, 94, g, night, False, room)
    guest(p, 6, g, night, False)
    top = g - 9
    table(p, 145, p.w - 6, top, g, night)
    candelabrum(p, 152, top - 1, night, False)
    goblet(p, 166, top - 1, night)
    return (4, p.w - 4)


def phone_armoury(p: Pix, g, night: bool, room: int) -> tuple:
    """A phone's H3 under its words: two suits of armour under their banners guarding the trophy of swords crossed
    behind the gilded shield between two sconces, a torchere burning beside each suit, as tall as the `room` rows
    leave them."""
    armour(p, 17, g, night, False, room)
    armour(p, 150, g, night, False, room)
    if room >= 40:
        trophy(p, 90, g - room + 15, night)
        sconce(p, 72, g - room + 24, night, False, phase=0)
        sconce(p, 108, g - room + 24, night, False, phase=1)
    return (4, p.w - 4)


# --------------------------------------------------------------------------- the valance under the frieze
SWAG = 5              # the rows a swag of the valance sags at its middle


def valance(p: Pix, x0, x1, night: bool, gap=None, span: int = 41):
    """Swags of red velvet hung from the frieze between column x0 and x1, each `span` units wide and sagging SWAG rows
    at its middle, its folds catching the light and a gold fringe along its hem, a gilt clasp and a gold tassel where
    two swags meet; parting either side of `gap`, the columns the month's mark and its scrolls keep clear, and centred
    in the room each stretch leaves. Each swag is drawn once a file and placed as often as it hangs."""
    spans = [(x0, x1)] if gap is None else [(x0, gap[0]), (gap[1], x1)]
    key = ("swag", span, night)
    if key not in p.syms:
        p.symbol(key, swag(span, night))
        p.symbol(("tassel", night), tassel(night))
    for a, b in spans:
        n = (b - a) // span
        if n < 1:
            continue
        start = a + ((b - a) - n * span) // 2
        for i in range(n):
            p.use(key, start + i * span, TOP)
        for i in range(n + 1):
            p.use(("tassel", night), start + i * span - 1, TOP)


def swag(span: int, night: bool) -> dict:
    """One swag of the valance, `span` units wide, as {(x, y): colour} from its left end under the frieze."""
    cells = {}
    for x in range(span + 1):
        t = x / span
        bell = 4 * t * (1 - t)
        low = 1 + round(SWAG * bell)
        thick = 2 + round(2 * bell)
        fold = x % 7
        for k in range(thick):
            if k == 0:
                c = tone("carpet", 3, night)
            elif k == thick - 1:
                c = tone("carpet", 2, night)
            else:
                c = tone("carpet", 5 if fold == 2 else 4, night)
            cells[(x, low - k)] = c
        for y in range(0, low - thick + 1):
            cells[(x, y)] = tone("carpet", 2 if y == 0 else 3, night)
        if x % 2 == 0:
            cells[(x, low + 1)] = _g(5 if x % 4 == 0 else 3, night)
    return cells


def tassel(night: bool) -> dict:
    """A gilt clasp where two swags meet under the frieze and a gold tassel hanging from it, three units wide, as
    {(x, y): colour} from its clasp's left end."""
    cells = {}
    for i in range(3):
        cells[(i, 0)] = _g(5, night)
        cells[(i, 1)] = _g(3, night)
        cells[(i, 4)] = _g(5, night)
        cells[(i, 5)] = _g(3, night)
    cells[(1, 2)] = _g(4, night)
    cells[(1, 3)] = _g(5, night)
    cells[(0, 6)] = _g(4, night)
    cells[(2, 6)] = _g(2, night)
    return cells
