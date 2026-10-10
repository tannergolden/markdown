# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Juneteenth set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the frame, the scenery a header stands on,
and every sprite, each shaded from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ..pixel import FONTS, LX, LY, LZ, Pix, fold, num, sphere
from ..pixel.shade import _tone
from .palette import C, CONFETTI, GROUND, NIGHT_SKY, RAMP, X, step


def foil_fill(r, c, scale, night, arc=3):
    """The colour a title's letter takes at row `r` and column `c` of the letter, counted in pixels from
    its top-left: painted like the Juneteenth flag, blue above and red below, parted by the white arc of
    its horizon at band `arc` of the face, the blue lit at the crown and the red deepening to the foot. By
    night every band is a tone lighter, so each keeps 4.5:1 against the night sky."""
    B, R, L = RAMP["blue"], RAMP["red"], RAMP["linen"]
    band = min(6, r // scale)
    if band == arc:
        return L[6]
    if band < arc:
        ramp = (B[6], B[5], B[5]) if night else (B[5], B[4], B[3])
        return ramp[min(2, band + (3 - arc))]
    ramp = (R[6], R[5], R[5]) if night else (R[4], R[3], R[2])
    return ramp[min(2, band - arc - 1)]


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: warm white paper with a dot grid by day, by night a June sky over the
    Gulf, deep blue overhead and lighter toward the horizon in five bands."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
        if dots:
            p.defs.append(f'<pattern id="{uid}d" width="8" height="8" patternUnits="userSpaceOnUse">'
                          f'<rect x="4" y="4" width="1" height="1" fill="{C["grid"]}"/></pattern>')
            p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')
        return
    n = len(NIGHT_SKY)
    edges = [y + round(i * h / n) for i in range(n + 1)]
    for i, col in enumerate(NIGHT_SKY):
        p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    if dots:
        p.defs.append(f'<pattern id="{uid}d" width="8" height="8" patternUnits="userSpaceOnUse">'
                      f'<rect x="4" y="4" width="1" height="1" fill="{C["grid_n"]}"/></pattern>')
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')


def sparkle(p: Pix, x, y, big=False, L="base", night=True, warm=False):
    """A four-point glint: a white heart, arms that fade, longer arms on the brightest."""
    arm = RAMP["gold"][6] if warm else X["star_pale"]
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.5", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """A June night's stars at three magnitudes: faint pinpricks, bright points, and a few glints. None is
    set inside a box in `avoid` (x0, y0, x1, y1), so no glint sits in a letter or beside a word."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.5 or faint:
            p.px(x, y, rnd.choice((X["star_faint"], X["star_dim"])), "haze")
        elif k < 0.88:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.5) else "haze"
            p.px(x, y, rnd.choice((C["white"], RAMP["gold"][6], X["star_pale"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.4)


# --------------------------------------------------------------------------- the border
BURST3 = ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2))          # a white star three pixels square


def tricolor_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="tc", chase=False):
    """The sheet's border: a ribbon three pixels wide in the red, black and green often flown beside the
    Juneteenth flag, red on the outside and green on the inside on every side, with a small white star
    across it every twelve pixels; inside it a gold rule. Each side is one pattern tile placed along it,
    so the border costs a few hundred bytes. With `chase`, by night the stars along the top and the foot
    light up in turn."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    R, G, K = RAMP["red"], RAMP["green"], RAMP["coal"]
    k = -1 if night else 0
    bands = (R[3 + k], K[1], G[3 + k])                     # outside to inside
    star = C["white"] if not night else RAMP["linen"][5]

    def tile(side):
        cells = {}
        for a in range(12):
            for b in range(3):
                depth = b if side in ("top", "left") else 2 - b   # how far in from the sheet's edge
                cells[(a, b) if side in ("top", "bottom") else (b, a)] = bands[depth]
        for (sx, sy) in BURST3:
            cells[(sx + 5, sy) if side in ("top", "bottom") else (sy, sx + 5)] = star
        return cells

    for side in ("top", "bottom", "left", "right"):
        tw, th = (12, 3) if side in ("top", "bottom") else (3, 12)
        p.defs.append(f'<pattern id="{uid}{side[0]}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
                      f'{p._paths(tile(side))}</pattern>')
    p.defs.append(f'<rect id="{uid}T" width="{w}" height="3" fill="url(#{uid}t)"/>')
    p.defs.append(f'<rect id="{uid}B" width="{w}" height="3" fill="url(#{uid}b)"/>')
    p.defs.append(f'<rect id="{uid}L" width="3" height="{h - 6}" fill="url(#{uid}l)"/>')
    p.defs.append(f'<rect id="{uid}R" width="3" height="{h - 6}" fill="url(#{uid}r)"/>')
    for (name, bx, by) in (("T", x, y), ("B", x, y + h - 3), ("L", x, y + 3), ("R", x + w - 3, y + 3)):
        p.shapes["base"].append(f'<use href="#{uid}{name}" x="{bx}" y="{by}"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, RAMP["gold"][5] if night else RAMP["gold"][3])
    if chase and night:                                      # the stars light up in turn along top and foot
        i = 0
        for sx in range(x + 5, x + w - 3, 24):
            for sy in (y, y + h - 3):
                L = p.twinkle(i)
                for (a, b) in BURST3:
                    p.px(sx + a, sy + b, RAMP["gold"][6], L)
                i += 1


# --------------------------------------------------------------------------- flags on a string
def mini_flag_cells(night=False):
    """A little Juneteenth flag seven pixels wide and five deep: blue above and red below, parted by a white
    arc that rises toward the middle, and a white star over the arc's crown."""
    B, R, L = RAMP["blue"], RAMP["red"], RAMP["linen"]
    k = -1 if night else 0
    arc = [3, 3, 2, 2, 2, 3, 3]
    cells = {}
    for i in range(7):
        for j in range(5):
            if j == arc[i]:
                c = L[6 + k]
            elif j < arc[i]:
                c = B[4 + k] if i < 3 else B[3 + k]
            else:
                c = R[4 + k] if i < 3 else R[3 + k]
            cells[(i, j)] = c
    cells[(3, 1)] = C["white"] if not night else L[5]           # the star, just over the arc's crown
    return cells


def _pennant_cells(night=False):
    """A pennant in red, black and green, seven wide at its top and coming to a point five rows down."""
    R, G, K = RAMP["red"], RAMP["green"], RAMP["coal"]
    k = -1 if night else 0
    rows = [(0, 7, R[4 + k]), (1, 5, R[3 + k]), (1, 5, K[2]), (2, 3, G[4 + k]), (3, 1, G[3 + k])]
    cells = {}
    for j, (a, n, c) in enumerate(rows):
        for i in range(a, a + n):
            cells[(i, j)] = c
    return cells


def _garland_span(sp, sag, night, variant):
    """One span of the garland, tack to tack, as pixels: a cord sagging `sag` rows at the middle and hung
    along it, a hand apart, little Juneteenth flags and red, black and green pennants by turns."""
    q = Pix(sp + 2, sag + 9)
    oy = 1
    cord = RAMP["linen"][3] if not night else RAMP["linen"][2]
    pts = [(xx, oy + round(sag * 4 * (xx / sp) * (1 - xx / sp))) for xx in range(sp + 1)]
    for (xx, yy) in pts:
        q.px(xx, yy, cord)
    for (a_, b_) in zip(pts, pts[1:]):
        if abs(a_[1] - b_[1]) > 1:
            for yy in range(min(a_[1], b_[1]) + 1, max(a_[1], b_[1])):
                q.px(a_[0], yy, cord)
    for j, fx in enumerate(range(3, sp - 7, 10)):
        cells = mini_flag_cells(night) if (j + variant) % 2 == 0 else _pennant_cells(night)
        ty = max(pts[fx][1], pts[min(sp, fx + 6)][1]) + 1
        for (a, b), c in cells.items():
            q.px(fx + a, ty + b, c)
    return {(x, y - oy): c for (x, y), c in q.layers["base"].items()}


def flag_garland(p: Pix, x0, x1, y, span=40, sag=4, night=False):
    """A garland along the top: a cord swagged from tack to tack, hung with little Juneteenth flags and red,
    black and green pennants by turns, and a gold star at every tack. Each swag is drawn once and hung
    again and again; the last is cut to fit."""
    xs = list(range(x0, x1, span))
    for i, xa in enumerate(xs):
        sp = min(span, x1 - xa)
        if sp < 12:
            continue
        key = ("garland", sp, sag, night, i % 2)
        if key not in p.syms:
            p.symbol(key, _garland_span(sp, sag, night, i % 2))
        p.use(key, xa, y)
    G = RAMP["gold"]
    k = -1 if night else 0
    for xa in xs + [x1]:
        key = ("tack", night)
        if key not in p.syms:
            cells = {(0, -1): G[6 + k], (-1, 0): G[5 + k], (0, 0): G[6 + k], (1, 0): G[4 + k], (0, 1): G[4 + k],
                     (-1, 1): G[3 + k], (1, 1): G[3 + k]}
            p.symbol(key, cells)
        p.use(key, min(xa, x1 - 2), y)


def confetti_colour(fam, night, lit=True):
    """A piece of confetti's colour in the family `fam`: its lit face or its turned face."""
    R = RAMP[fam]
    t = (5 if lit else 3) if fam != "linen" else (6 if lit else 4)
    return R[t - (1 if night and fam not in ("gold", "linen") else 0)]


def confetti_on(p: Pix, x0, x1, y, seed=7, L="base", night=False, gap=(3, 9)):
    """Confetti lying along a ledge whose top edge is row `y`: little squares and strips of red, blue, gold,
    green and white, some face up and some turned, and now and then a tiny star. None lies where it would
    touch a word."""
    rnd = random.Random(seed * 131 + x0)
    x = x0 + rnd.randint(1, 4)
    while x < x1 - 3:
        fam = rnd.choice(CONFETTI)
        if not p.clear_of_words(x, y - 4, x + 4, y):
            x += rnd.randint(*gap)
            continue
        r = rnd.random()
        if r < 0.08 and not night:                           # a tiny gold star
            for (dx, dy) in ((1, -3), (0, -2), (1, -2), (2, -2), (1, -1)):
                p.px(x + dx, y + dy, RAMP["gold"][4 if (dx, dy) != (1, -2) else 5], L)
            x += 3
        elif r < 0.45:                                       # a strip lying flat
            p.px(x, y - 1, confetti_colour(fam, night, True), L)
            p.px(x + 1, y - 1, confetti_colour(fam, night, False), L)
            x += 2
        else:                                                # a square, face up or turned
            p.px(x, y - 1, confetti_colour(fam, night, rnd.random() < 0.6), L)
            x += 1
        x += rnd.randint(*gap)


# --------------------------------------------------------------------------- the lawn and the sand
def lawn(p: Pix, x0, x1, y_top, y_bot, seed=5, night=False, L="base", flowers=True):
    """A lawn along the foot of a drawing: a rolling crest of summer grass with blades standing up from it,
    darker toward the rule it rests on, and here and there a firewheel, the red and gold wildflower that
    blooms across Texas in June."""
    G, R, Gd = RAMP["green"], RAMP["red"], RAMP["gold"]
    rnd = random.Random(seed)
    k = -1 if night else 0
    h = rnd.randint(2, 3)
    prev = h
    for x in range(x0, x1):
        h = max(1, min(y_bot - y_top, h + rnd.choice((-1, 0, 0, 0, 1))))
        top = y_bot - h
        for yy in range(top, y_bot):
            c = G[4 + k] if yy == top else (G[3 + k] if yy < y_bot - 1 else G[2 + k])
            if yy == top and h < prev:
                c = G[3 + k]
            p.px(x, yy, c, L)
        prev = h
        r_ = rnd.random()
        if flowers and r_ > 0.955 and x + 2 < x1:            # a firewheel: red petals tipped with gold
            p.px(x, top - 1, G[3 + k], L)
            p.px(x - 1, top - 2, R[4 + k], L)
            p.px(x + 1, top - 2, R[4 + k], L)
            p.px(x, top - 2, Gd[3 + k], L)
            p.px(x, top - 3, Gd[5 + k], L)
        elif r_ < 0.34:
            p.px(x, top - 1, G[5 + k] if rnd.random() < 0.5 else G[4 + k], L)
            if r_ < 0.1:
                p.px(x, top - 2, G[4 + k], L)


def sand(p: Pix, x0, x1, y_top, y_bot, seed=4, night=False, L="base"):
    """A strip of beach along the foot of a drawing: pale sand lit along its top, a grain here and there,
    and a shell or two."""
    S = RAMP["sand"]
    rnd = random.Random(seed)
    k = -1 if night else 0
    for x in range(x0, x1):
        for yy in range(y_top, y_bot):
            c = S[5 + k] if yy == y_top else (S[4 + k] if yy < y_bot - 1 else S[3 + k])
            if rnd.random() < 0.08:
                c = S[3 + k]
            p.px(x, yy, c, L)
        if rnd.random() < 0.03:
            p.px(x, y_top, RAMP["linen"][6 + k], L)


# --------------------------------------------------------------------------- the Gulf
def gulf(p: Pix, x0, x1, y_top, y_bot, night=False, motion=True, seed=6, dur=2.4):
    """The Gulf of Mexico from the shore, from its horizon at `y_top` down to the water's edge at `y_bot`:
    pale toward the horizon where it takes the sky and deeper nearer in, rows of whitecaps that run along
    it in a moving file, the sun's glitter on it by day, by night the last light lying along the horizon,
    and at its edge a line of foam that washes up and draws back."""
    Se, Ln, D = RAMP["sea"], RAMP["linen"], RAMP["dusk"]
    rnd = random.Random(seed)
    h = y_bot - y_top
    if night:                                                     # the last light over the Gulf
        for j, a in enumerate((0.3, 0.2, 0.12, 0.06)):
            for xx in range(x0, x1):
                p.apx(xx, y_top - 1 - j, D[5], a, "haze")
    for yy in range(y_top, y_bot):
        f = (yy - y_top) / max(1, h - 1)
        if night:
            c = D[4] if yy == y_top else (D[3] if f < 0.3 else (D[2] if f < 0.7 else Se[1]))
        else:
            c = Se[6] if yy == y_top else (Se[5] if f < 0.3 else (Se[4] if f < 0.7 else Se[3]))
        p.hline(x0, x1, yy, c)
    foam = Ln[6] if not night else D[5]
    frames = [p.seq(f"wave{f}", round(f / 3, 3), round((f + 1) / 3, 3), dur, keep=f == 0, z=0.3) for f in range(3)] \
        if motion else ["base"]
    rows = list(range(y_top + 2, y_bot - 1, 3))
    for f, L in enumerate(frames):
        for r_, yy in enumerate(rows):
            period = 11 + r_ * 3
            for xx in range(x0, x1):
                if (xx + r_ * 5 + f * (2 + r_)) % period in (0, 1) and (xx * 7 + yy) % 5:
                    p.px(xx, yy, foam if (xx + f) % period == 0 or r_ > 0 else Se[6] if not night else D[4], L)
    shore = [p.seq(f"shore{f}", round(f / 3, 3), round((f + 1) / 3, 3), dur * 1.6, keep=f == 0, z=0.3)
             for f in range(3)] if motion else ["base"]
    for f, L in enumerate(shore):
        reach = (0, 1, 2)[f] if motion else 1
        for xx in range(x0, x1):
            yy = y_bot - 1 + (1 if (xx // 5 + f) % 3 == 0 else 0) - reach + 1
            p.px(xx, min(y_bot, yy), Ln[6] if not night else D[5], L)
    if not night:
        for i in range(max(1, (x1 - x0) // 9)):                            # the sun's glitter on the water
            gx, gy = rnd.randrange(x0 + 1, x1 - 1), rnd.randrange(y_top + 1, y_bot - 2)
            p.px(gx, gy, C["white"], p.twinkle(i) if motion else "base")


def gull_cells(up: bool) -> dict:
    """A gull on the wing, seven wide: a white body, grey wings raised or lowered, black tips."""
    Ln, S, K = RAMP["linen"], RAMP["silver"], RAMP["coal"]
    art = ["k.....k", ".s...s.", "..sws..", "...w..."] if up else ["..sws..", ".s...s.", "k.....k", "......."]
    pal = {"k": K[2], "s": S[3], "w": Ln[6]}
    return {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if ch in pal}


def gulls(p: Pix, flights, motion=True, z=16):
    """Gulls over the Gulf: each (path, dur) is one gull wheeling along its path, its wings beating, round
    and round. The still file holds each at its path's first point."""
    frames = []
    for up in (True, False):
        key = ("gull", up)
        if key not in p.syms:
            p.symbol(key, gull_cells(up))
        frames.append(key)
    for path, dur in flights:
        if not motion:
            p.use(frames[0], *path[0], "near")
            continue
        p.fly(frames, path, dur, z=z, flap=0.35)


# --------------------------------------------------------------------------- the sky by day
def sun(p: Pix, cx, cy, r, L="base"):
    """The June sun, high and hot: a disc bright toward its heart, its rim a deeper gold, a soft glow round it."""
    G = RAMP["gold"]
    p.halo(cx, cy, r * 2.6, r * 2.6, G[5], (0.05, 0.09, 0.14), L="haze")
    for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / r
            if d <= 1:
                p.px(x, y, G[6] if d < 0.5 else (G[5] if d < 0.85 else G[4]), L)


def cloud(p: Pix, x, y, w, h=None, L="haze"):
    """A fair-weather cloud, its top-left at (x, y): round puffs on a flat foot, white on top and a pale
    warm grey underneath, with a pale edge round it."""
    h = h or max(4, round(w * 0.4))
    Ln = RAMP["linen"]
    cells = set()
    r1, r2, r3 = h * 0.42, h * 0.55, h * 0.38
    for yy in range(h):
        for xx in range(w):
            px_, py_ = xx + 0.5, yy + 0.5
            if (math.hypot(px_ - w * 0.28, py_ - (h - r1)) <= r1 or math.hypot(px_ - w * 0.52, py_ - (h - r2)) <= r2
                    or math.hypot(px_ - w * 0.76, py_ - (h - r3)) <= r3 or (py_ > h - r3 and w * 0.2 < px_ < w * 0.86)):
                cells.add((xx, yy))
    top, bot = min(c[1] for c in cells), max(c[1] for c in cells)
    for (cx_, cy_) in cells:
        f = (cy_ - top) / max(1, bot - top)
        p.px(x + cx_, y + cy_, C["white"] if f < 0.6 else (Ln[5] if f < 0.9 else Ln[4]), L)
    for (cx_, cy_) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (cx_ + dx, cy_ + dy)
            if q not in cells:
                p.px(x + q[0], y + q[1], Ln[4] if dy <= 0 else Ln[3], L)


# --------------------------------------------------------------------------- fireworks, by night only
BURST_TIERS = 3   # 0 a star's white-hot head, 1 the bright part of its trail, 2 the trail as it cools


def _burst_frame(kind, r, frame, seed=0):
    """The pixels of one frame of a firework, relative to where it bursts, each with a tier: "trail1" and
    "trail2" (the shell rising), "open" (the break), "bloom" (the full burst), "fall" and "fade". Every star
    flies on its own arc, slowed by the air and pulled down, its trail drawn behind it. A nova throws out
    twelve stars evenly, like the points of the burst round the star on the Juneteenth flag, and leaves a
    white star at its heart."""
    rnd = random.Random(seed * 17 + int(r * 10))
    cells = {}

    def put(x, y, t):
        q = (math.floor(x), math.floor(y))
        if q not in cells or cells[q] > t:
            cells[q] = t

    if frame in ("trail1", "trail2"):
        y0 = r + 7 if frame == "trail1" else round(r * 0.45) + 3
        wob = 1 if seed % 2 else -1
        for i, t in enumerate((0, 1, 1, 2, 2, 2)):
            put(0.5 + (wob if i in (3, 5) else 0) * (i >= 3) * 0.6, y0 + i + 0.5, t)
        return cells
    n = 12 if kind == "nova" else (16 if r >= 12 else (12 if r >= 8 else 10))
    if kind == "ring":
        n = 22 if r >= 12 else 16
    drop = {"peony": 0.12, "willow": 0.4, "ring": 0.08, "nova": 0.06}[kind] * r
    a0 = -math.pi / 2 if kind == "nova" else rnd.uniform(0, 2 * math.pi / n)
    stars_ = []
    for j in range(n):
        a = a0 + j * 2 * math.pi / n + (0 if kind == "nova" else rnd.uniform(-0.07, 0.07))
        stars_.append((math.cos(a), math.sin(a), r * (1.0 if kind == "nova" else rnd.uniform(0.9, 1.04))))

    def at(ca, sa, rj, t):
        out = rj * (1 - math.exp(-2.2 * t)) / (1 - math.exp(-2.2))
        return 0.5 + ca * out, 0.5 + sa * out + drop * t * t

    def arc(ca, sa, rj, t_end, length, tiers):
        pts = [at(ca, sa, rj, t_end - length * i / 8) for i in range(9)]
        seg = {}
        for (xa, ya), (xb, yb) in zip(pts[1:], pts):
            _line(seg, xa, ya, xb, yb)
        hx, hy = pts[0]
        order = sorted(seg, key=lambda q: math.hypot(q[0] + 0.5 - hx, q[1] + 0.5 - hy))
        for i, q in enumerate(order):
            put(q[0], q[1], tiers[min(len(tiers) - 1, i * len(tiers) // max(1, len(order)))])

    if frame == "open":
        for dx, dy, t in ((0, 0, 0), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (1, 1, 1), (-1, 1, 1), (1, -1, 1),
                          (-1, -1, 1), (2, 0, 2), (-2, 0, 2), (0, 2, 2), (0, -2, 2)):
            put(0.5 + dx, 0.5 + dy, t)
        for ca, sa, rj in stars_[::2]:
            arc(ca, sa, rj, 0.34, 0.14, (0, 1))
        return cells
    if kind == "nova" and frame == "bloom":                  # the white star at its heart
        for (dx, dy) in ((0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1),
                         (0, 1), (1, 1), (-1, 2), (1, 2)):
            put(0.5 + dx, 0.5 + dy, 0)
    for k, (ca, sa, rj) in enumerate(stars_):
        if kind == "ring":
            if frame == "bloom":
                x, y = at(ca, sa, rj, 1.0)
                put(x, y, 0 if k % 2 == 0 else 1)
                x2, y2 = at(ca, sa, rj, 0.8)
                put(x2, y2, 2)
            elif frame == "fall" and k % 2 == 0:
                arc(ca, sa, rj, 1.35, 0.15, (1, 2))
            elif frame == "fade" and rnd.random() < 0.35:
                x, y = at(ca, sa, rj, 1.7)
                put(x, y, 2)
            continue
        if frame == "bloom":
            if kind == "willow":
                arc(ca, sa, rj, 1.0, 0.72, (0, 1, 2, 2, 2))
            elif kind == "nova":
                arc(ca, sa, rj, 1.0, 0.5, (0, 1, 1, 2, 2))
            else:
                arc(ca, sa, rj, 1.0, 0.42, (0, 1, 1, 2, 2, 2))
                if r >= 12 and k % 2 == 1:
                    x, y = at(ca, sa, rj * 0.45, 1.0)
                    put(x, y, 2)
        elif frame == "fall":
            if kind == "willow":
                arc(ca, sa, rj, 1.45, 0.9, (1, 2, 2, 2))
            else:
                arc(ca, sa, rj, 1.35, 0.3, (1, 2, 2))
                if rnd.random() < 0.5:
                    x, y = at(ca, sa, rj, 1.35)
                    put(x + rnd.choice((-2, -1, 1, 2)), y + rnd.choice((-2, -1, 1)), 0)
        else:
            if rnd.random() < (0.7 if kind == "willow" else 0.5):
                if kind == "willow":
                    arc(ca, sa, rj, 1.85, 0.5, (2,))
                else:
                    x, y = at(ca, sa, rj, 1.75)
                    put(x, y, 2)
    return cells


def _burst_symbols(p: Pix, kind, r, frame, seed):
    """A frame drawn once: one path for each of its three tiers, each taking its colour where it is used."""
    key = ("burst", kind, r, frame, seed)
    if key not in p.syms:
        cells = _burst_frame(kind, r, frame, seed)
        tiers = []
        for t in range(BURST_TIERS):
            part = {q: 1 for q, tt in cells.items() if tt == t}
            if part:
                tiers.append((t, p.symbol((key, t), part, mono=True)))
        p.syms[key] = tiers
    return key


# The colours a burst takes by night: each star's head, the bright part of its trail and the trail as it
# cools. Fireworks are for the night only; the day files keep a clear sky.
_R, _B, _Gd, _Gn, _L = RAMP["red"], RAMP["blue"], RAMP["gold"], RAMP["green"], RAMP["linen"]
BURST_COLOURS = {
    "red": (C["white"], _R[5], _R[3]),
    "blue": (C["white"], _B[5], _B[3]),
    "gold": (_Gd[6], _Gd[4], _Gd[2]),
    "green": (C["white"], _Gn[5], _Gn[3]),
    "white": (C["white"], _L[5], _L[3]),
}
FRAMES = [("trail1", 0.0, 0.06), ("trail2", 0.06, 0.12), ("open", 0.12, 0.17), ("bloom", 0.17, 0.34),
          ("fall", 0.34, 0.45), ("fade", 0.45, 0.54)]
SHOW_SPAN = 1 - FRAMES[-1][2]      # how far round the loop the last firework of a show may start


def firework(p: Pix, cx, cy, r, colour="red", kind="peony", motion=True, offset=0.0, dur=6.0, seed=0, name=None,
             light=0, keep="bloom"):
    """A firework bursting at (cx, cy), `r` pixels across its sparks, drawn only in a night file. In a
    moving file it rises on a trail of sparks, breaks with a flash, blooms, sinks and goes out in embers,
    each frame shown for its moment of a loop `dur` seconds long starting at `offset` of the way round,
    so several can take turns. The still file shows it in full bloom. `light` (a radius) washes its colour
    over whatever lies below it while it blooms: the water, the sand, the roofs."""
    cols = BURST_COLOURS[colour]
    name = name or f"fw{len([k for k in p.layers if k.startswith('fw')])}"
    frames = FRAMES if motion else [f for f in FRAMES if f[0] == keep]
    for fname, t0, t1 in frames:
        if motion:
            L = p.seq(f"{name}{fname[0]}{fname[-1]}", round(offset + t0, 3), round(offset + t1, 3), dur,
                      keep=fname == keep)
        else:
            L = p.layer("fw", z=-12)
        key = _burst_symbols(p, kind, r, fname, seed)
        if fname == "open":
            p.shapes[L].append(f'<ellipse cx="{num(cx + 0.5)}" cy="{num(cy + 0.5)}" rx="3.5" ry="3.5" '
                               f'fill="{cols[1]}" fill-opacity=".3"/>')
        for t, sid in p.syms[key]:
            p.uses[L].append((cols[t], sid, cx, cy, 1))
        if light and fname == "bloom":
            flash(p, cx, cy, light, cols[1], L)


def flash(p: Pix, cx, cy, r, col, L):
    """A firework's light on the drawn things below it, strongest nearest the burst, on a layer of its own
    over the drawing that shows while the burst is in bloom. The sky and the words take none."""
    base = p.layers["base"]
    Lf = L + "f"
    if Lf not in p.layers:
        p.layer(Lf, p.meta[L][2], z=2.5)
    alphas = (0.07, 0.13, 0.2)
    n = len(alphas)
    for (x, y) in list(base):
        d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 0.8) / r
        if d < 1 and y > cy:
            p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], Lf)


# --------------------------------------------------------------------------- night lights
def fireflies(p: Pix, x0, x1, y0, y1, n, night, seed=0, motion=True, avoid=()):
    """Fireflies over the grass on a June night, each a warm point in a small glow that flashes and goes
    out in its own time. By day there are none to see. None is set in a box in `avoid`."""
    if not night:
        return
    rnd = random.Random(seed)
    Gd, Gr = RAMP["gold"], RAMP["green"]
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        if (any(a - 2 <= x < c + 2 and b - 2 <= y < d + 2 for a, b, c, d in avoid)
                or not p.clear_of_words(x - 2, y - 2, x + 3, y + 3)):
            continue
        L = p.blink(i, z=16) if motion else "base"
        key = ("firefly", i % 2)
        if key not in p.syms:
            hot, warm = (Gd[6], Gd[4]) if i % 2 == 0 else (Gr[6], Gr[5])
            cells = {(0, 0): hot}
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cells[(dx, dy)] = f"{warm}:0.45"
            for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                cells[(dx, dy)] = f"{warm}:0.18"
            p.symbol(key, cells)
        p.use(key, x, y, L)


def string_lights(p: Pix, x0, x1, y, sag, night, motion=True, L="base"):
    """A string of party lights swagged between two posts at row `y`: a dark cord and a bulb every five
    pixels, red, gold, green and white by turns. By night they are lit, each with a small glow, and some
    brighten and dim in turn."""
    K, Gd = RAMP["coal"], RAMP["gold"]
    cols = (RAMP["red"], Gd, RAMP["green"], RAMP["linen"])
    span = x1 - x0
    pts = [(xx, y + round(sag * 4 * ((xx - x0) / span) * (1 - (xx - x0) / span))) for xx in range(x0, x1 + 1)]
    for (xx, yy) in pts:
        p.px(xx, yy, K[3] if not night else K[4], L)
    for i, (xx, yy) in enumerate(pts[2:-2:5]):
        R = cols[i % 4]
        if night:
            hot = R[6] if R is not RAMP["linen"] else C["white"]
            p.px(xx, yy + 1, hot, p.twinkle(i) if motion and i % 3 == 0 else L)
            p.px(xx, yy + 2, R[5], L)
            glow = glow_cells(xx + 0.5, yy + 1.8, 2.6, 2.6, R[5], (0.1, 0.2), {(xx, yy + 1), (xx, yy + 2)})
            for (qx, qy), c in glow.items():
                p.px(qx, qy, c, "haze")
        else:
            p.px(xx, yy + 1, R[4] if R is not RAMP["linen"] else R[5], L)
            p.px(xx, yy + 2, R[3] if R is not RAMP["linen"] else R[4], L)


def glow_cells(cx, cy, rx, ry, col, alphas, skip=()):
    """A small stepped glow as see-through pixels around (cx, cy), leaving out the pixels in `skip`."""
    out, n = {}, len(alphas)
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d < 1 and (x, y) not in skip:
                out[(x, y)] = f"{col}:{alphas[min(n - 1, int((1 - d) * n))]:g}"
    return out


# --------------------------------------------------------------------------- light that falls on things
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a light at (cx, cy): once everything is drawn, `lamplight` lays its warm light on
    whatever stands within `r` of it, flickering with it. `own` are the light's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def lamplight(p: Pix, night: bool):
    """The finishing pass: each ember's, window's or lamp's light on the drawn things near it, strongest
    nearest the light. The paper, the sky and the words take none."""
    base = p.layers["base"]
    col = RAMP["gold"][5]
    alphas = (0.08, 0.15, 0.24) if night else (0.035, 0.07)
    n = len(alphas)
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if (x, y) not in base or (x, y) in own:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.25) / r
                if d < 1:
                    p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], L)


def contact(p: Pix, cx, y, rx):
    """The shadow a thing standing on the lawn or the sand leaves right under it: only the ground takes it."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.7, X["shade_ink"], (0.16, 0.3), L="pool", only=GROUND, shape=False)


def _line(cells: dict, x0, y0, x1, y1, tag=1):
    """A one-pixel line, each step touching the last."""
    x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.floor(x1), math.floor(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        cells.setdefault((x0, y0), tag)
        if (x0, y0) == (x1, y1):
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# --------------------------------------------------------------------------- shading a flat shape
def pillow(p: Pix, cells, ramp, L="base", lo=1, hi=None, outline=True, spec=True, spec_at=None, rim=True, soft=1.0):
    """Shade a flat shape as if it were stuffed: its height rises from its edge to its middle, and each
    pixel takes the light from the upper left by the slope it faces; a glint where the light lands (at
    `spec_at`, or up and left of its middle), bounce light along its lower right rim, and a selective
    outline, darker on the shaded side. Returns the tone each pixel took."""
    hi = len(ramp) - 1 if hi is None else hi
    cells = set(cells)
    if not cells:
        return {}
    n4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
    dist, frontier = {}, []
    for c in cells:
        if any((c[0] + dx, c[1] + dy) not in cells for dx, dy in n4):
            dist[c] = 1
            frontier.append(c)
    while frontier:
        nxt = []
        for c in frontier:
            for dx, dy in n4:
                q = (c[0] + dx, c[1] + dy)
                if q in cells and q not in dist:
                    dist[q] = dist[c] + 1
                    nxt.append(q)
        frontier = nxt
    dmax = max(dist.values())

    def ht(c):
        f = min(1.0, dist.get(c, 0) / (dmax + 0.5))
        return math.sqrt(max(0.0, 1 - (1 - f) ** 2)) * (dmax + 0.5) * soft

    tones = {}
    for (x, y) in cells:
        gx = ht((x + 1, y)) - ht((x - 1, y))
        gy = ht((x, y + 1)) - ht((x, y - 1))
        nx, ny, nz = -gx, -gy, 2.0
        m = math.sqrt(nx * nx + ny * ny + nz * nz)
        lam = max(0.0, (nx * LX + ny * LY + nz * LZ) / m)
        v = lo + (hi - 1 - lo + 0.4) * lam ** 1.1
        t = _tone(v, x, y, lo, hi - 1)
        if rim and dist[(x, y)] == 1 and (nx * LX + ny * LY) / m < -0.35:
            t = max(t, lo + 1)
        tones[(x, y)] = t
    if spec:
        xs = [c[0] for c in cells]
        ys = [c[1] for c in cells]
        if spec_at is None:
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            r = (max(xs) - min(xs)) / 2
            spec_at = (mx + LX * r * 0.55, my + LY * r * 0.55)
        best = min(cells, key=lambda q: (q[0] + 0.5 - spec_at[0]) ** 2 + (q[1] + 0.5 - spec_at[1]) ** 2)
        tones[best] = hi
        if dmax >= 3:
            for q in ((best[0] + 1, best[1]), (best[0], best[1] + 1)):
                if q in tones:
                    tones[q] = max(tones[q], hi - 1)
    for (x, y), t in tones.items():
        p.px(x, y, ramp[t], L)
    if outline:
        cx_, cy_ = sum(c[0] for c in cells) / len(cells), sum(c[1] for c in cells) / len(cells)
        for (x, y) in cells:
            for dx, dy in n4:
                q = (x + dx, y + dy)
                if q in cells:
                    continue
                far = (q[0] - cx_) * LX + (q[1] - cy_) * LY < 0
                p.px(q[0], q[1], ramp[0] if far else ramp[min(lo, 1)], L)
    return tones


# --------------------------------------------------------------------------- stars and marks
STAR_ART = {
    5: ["..#..", "..#..", "#####", ".###.", ".#.#."],
    7: ["...#...", "..###..", "#######", ".#####.", "..###..", ".##.##.", ".#...#."],
    9: ["....#....", "....#....", "...###...", "#########", ".#######.", "..#####..", "..#####..", ".###.###.",
        ".##...##."],
}
STAR_RAMPS = {"gold": ("gold", 3), "white": ("linen", 4), "blue": ("blue", 3), "red": ("red", 3)}


def star5(p: Pix, x, y, size=7, colour="gold", night=False, L="base", reuse=False):
    """A five-point star, `size` square, top-left at (x, y), bevelled: each arm has a ridge down its middle,
    the facet facing the light a tone up and the other a tone down, with a glint at its heart."""
    key = ("star5", size, colour, night)
    if key not in p.syms or not reuse:
        name, mid = STAR_RAMPS[colour]
        Rm = RAMP[name]
        if night and colour != "white":
            mid += 1
        art = STAR_ART[size]
        cx, cy = size / 2, size * 0.54
        cells = {}
        for j, row in enumerate(art):
            for i, ch in enumerate(row):
                if ch != "#":
                    continue
                dx, dy = i + 0.5 - cx, j + 0.5 - cy
                th = math.atan2(dy, dx)
                k = round((th + math.pi / 2) / (2 * math.pi / 5))
                axis = -math.pi / 2 + k * 2 * math.pi / 5
                side = 1 if ((th - axis + math.pi) % (2 * math.pi) - math.pi) > 0 else -1
                nx, ny = math.cos(axis + side * math.pi / 2), math.sin(axis + side * math.pi / 2)
                lit = nx * LX + ny * LY
                t = mid + (1 if lit > 0.2 else (-1 if lit < -0.2 else 0))
                if math.hypot(dx, dy) < 0.8:
                    t = mid + 1
                cells[(i, j)] = Rm[max(1, min(6, t))]
        hx, hy = round(cx - 1.2), round(cy - 1.0)
        if (hx, hy) in cells and size >= 7:
            cells[(hx, hy)] = Rm[min(6, mid + 3)]
        if not reuse:
            for (i, j), c in cells.items():
                p.px(x + i, y + j, c, L)
            return
        p.symbol(key, cells)
    p.use(key, x, y, L)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["red"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)


# --------------------------------------------------------------------------- the Juneteenth flag
def _in_poly(x, y, pts):
    inside = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _near_poly(x, y, pts, d=0.6):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        vx, vy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((x - x1) * vx + (y - y1) * vy) / max(1e-9, vx * vx + vy * vy)))
        if math.hypot(x - (x1 + t * vx), y - (y1 + t * vy)) < d:
            return True
    return False


def _star_pts(cx, cy, r_out, r_in, n):
    return [(cx + (r_out if k % 2 == 0 else r_in) * math.cos(-math.pi / 2 + k * math.pi / n),
             cy + (r_out if k % 2 == 0 else r_in) * math.sin(-math.pi / 2 + k * math.pi / n)) for k in range(2 * n)]


def jflag_part(w, h, i, j):
    """What lies at column `i`, row `j` of a Juneteenth flag `w` by `h`: the white star, the white outline of
    the burst round it (a nova, a new star), the white arc of the horizon that parts the fields, or the
    blue field above the arc or the red below it. The star sits on the arc at the flag's middle, and the
    arc runs behind the burst, so inside it only the two fields meet."""
    def arc(u):
        v = u / w * 2 - 1
        return h * 0.64 - h * 0.16 * (1 - v * v)

    cx, cy = w / 2, arc(w / 2)
    x, y = i + 0.5, j + 0.5
    r_out = h * 0.4
    burst = _star_pts(cx, cy, r_out, r_out * 0.76, 12)
    if _in_poly(x, y, _star_pts(cx, cy - h * 0.02, h * 0.235, h * 0.1, 5)):
        return "star"
    if _near_poly(x, y, burst, 0.62):
        return "burst"
    a = arc(x)
    if abs(y - a) < 0.55 and not _in_poly(x, y, burst):
        return "arc"
    return "blue" if y < a else "red"


FLUTTER_FROM = 0.45    # the part of the flag's length from the hoist that holds still while the rest flutters


def _jflag_wave(w, h, i, flutter=None):
    """Column `i` of the flag rippling: how far it rises or falls, and how it faces the light (-1 turned
    away, 0 square on, 1 toward it, 2 a crest catching the light). `flutter`, a phase, adds a quicker wave
    out at the fly and nothing where it starts, so the free end flutters while the part by the pole holds
    still."""
    amp = 0.6 + 0.07 * h

    def off(k):
        u = k / w
        o = amp * u * math.sin(2 * math.pi * (u * 1.35))
        if flutter is not None and u > FLUTTER_FROM:
            env = ((u - FLUTTER_FROM) / (1 - FLUTTER_FROM)) ** 1.4
            o += (0.5 + 0.06 * h) * env * math.sin(2 * math.pi * (u * 1.8 - flutter))
        return o

    slope = off(i + 1) - off(i - 1) if i else off(1) - off(0)
    shade = 1 if slope < -0.22 else (-1 if slope > 0.22 else 0)
    crest = abs(slope) < 0.12 and math.sin(2 * math.pi * (i / w * 1.35)) < 0 and i > w * 0.15
    return round(off(i)), shade + (1 if crest else 0)


def _jflag_colour(part, tone, night, lifted):
    B, R, Ln = RAMP["blue"], RAMP["red"], RAMP["linen"]
    t = tone + (1 if lifted else 0)
    if part == "blue":
        return B[max(1, min(5, 3 + t))]
    if part == "red":
        return R[max(1, min(5, 3 + t))]
    return Ln[6] if t >= 0 else Ln[5]


def juneteenth_flag(p: Pix, x, y, w, h, night=False, motion=True, name="jf", frames=3, dur=1.3):
    """The Juneteenth flag flying from its hoist at (x, y), `w` by `h`: the blue field above and the red below,
    parted by the white arc of a new horizon, and on the arc at its middle the white star in the outline of
    a bursting nova. It ripples, each column rising and falling on a wave that grows toward the fly, the
    cloth lit where it faces the light and shaded where it turns away; in a moving file the free end
    flutters in `frames` frames round a loop `dur` seconds long. By night it is lit from below, by the lamp
    at the foot of its pole. The still file keeps the first frame."""
    i0 = round(w * FLUTTER_FROM)
    layers = [p.seq(f"{name}{f}", round(f / frames, 3), round((f + 1) / frames, 3), dur, keep=f == 0, z=0.2)
              for f in range(frames)] if motion else ["base"]
    parts = {(i, j): jflag_part(w, h, i, j) for i in range(w) for j in range(h)}
    for f, L in enumerate(layers):
        for i in range(w):
            if i < i0 and f:
                continue
            oy, tone = _jflag_wave(w, h, i, f / frames)
            Lx = "base" if i < i0 else L
            for j in range(h):
                lifted = night and j >= h * 0.55
                p.px(x + i, y + j + oy, _jflag_colour(parts[(i, j)], tone, night, lifted), Lx)
    return i0


def flagpole(p: Pix, x, top, base, night=False, L="base", flag_foot=None):
    """A flagpole standing on row `base`: a silver pole two pixels wide, lit on its left, a gold ball at its
    top and a halyard down its side to a cleat. By night a lamp at its foot lights the pole and the flag."""
    S, Gd, K = RAMP["silver"], RAMP["gold"], RAMP["coal"]
    for yy in range(top + 3, base):
        p.px(x, yy, S[5] if not night else S[4], L)
        p.px(x + 1, yy, S[3] if not night else S[2], L)
    p.hline(x - 1, x + 3, top + 3, S[4] if not night else S[3], L)
    sphere(p, x + 1, top + 1.5, 1.6, Gd, lo=2, outline=False)
    if flag_foot is not None:
        for yy in range(flag_foot, base - 7):
            p.px(x + 2, yy, S[3] if not night else S[2], L)
        p.px(x + 2, base - 7, K[4], L)
        p.px(x + 3, base - 7, K[3], L)
    if night:
        for (dx, c) in ((3, K[4]), (4, K[3]), (5, K[2])):
            p.px(x + dx, base - 1, c, L)
        p.px(x + 3, base - 2, K[4], L)
        p.px(x + 4, base - 2, Gd[6], L)
        for yy in range(base - 12, base - 1):
            p.px(x, yy, S[6], L)
            p.px(x + 1, yy, S[4], L)
        for (qx, qy), c in glow_cells(x + 4.5, base - 1.5, 3.0, 2.4, Gd[5], (0.25, 0.45), {(x + 4, base - 2)}).items():
            p.px(qx, qy, c, "pool")


# --------------------------------------------------------------------------- the cookout
def smoker(p: Pix, x, base, night=False, L="base", motion=True, phase=0, light=True):
    """An offset smoker, the barbecue pit of a Texas cookout, its left end at `x` and standing on row `base`,
    about 27 wide: a long black barrel on legs, round in the light from above, its lid seamed and handled
    with a thermometer on it; the firebox at its right end with the embers glowing through its vent; and
    the stack at its left end, where the smoke comes out. With `light` its embers light what stands near
    them once the drawing is done. Returns the top of the stack."""
    K, S, Gd, R = RAMP["coal"], RAMP["silver"], RAMP["gold"], RAMP["red"]
    k = -1 if night else 0
    bx0, bx1, cy, r = x + 2, x + 20, base - 10, 4
    for xx in range(bx0, bx1):
        for yy in range(cy - r, cy + r):
            f = (yy - (cy - r) + 0.5) / (2 * r)
            corner = (xx in (bx0, bx1 - 1)) and yy in (cy - r, cy + r - 1)
            if corner:
                continue
            c = K[5 + k] if f < 0.15 else (K[4 + k] if f < 0.38 else (K[3] if f < 0.72 else K[2]))
            if xx == bx0:
                c = K[5 + k] if f < 0.5 else K[3]
            elif xx == bx1 - 1:
                c = K[2]
            p.px(xx, yy, c, L)
    p.hline(bx0 + 1, bx1 - 1, cy - 1, K[1], L)                  # the lid's seam
    p.hline(bx0 + 6, bx0 + 12, cy - r - 1, S[4 + k], L)         # its handle
    p.px(bx0 + 6, cy - r, S[3], L)
    p.px(bx0 + 11, cy - r, S[3], L)
    p.px(bx0 + 3, cy - 3, S[5 + k], L)                          # the thermometer
    p.px(bx0 + 3, cy - 2, S[3], L)
    for yy in range(cy - r - 7, cy - r):                        # the stack
        p.px(x + 3, yy, K[5 + k], L)
        p.px(x + 4, yy, K[3], L)
    p.hline(x + 2, x + 6, cy - r - 8, K[4 + k], L)
    fx0 = bx1
    for xx in range(fx0, fx0 + 7):                              # the firebox
        for yy in range(cy - 1, cy + r + 1):
            c = K[4 + k] if yy == cy - 1 else (K[3] if xx < fx0 + 5 else K[2])
            p.px(xx, yy, c, L)
    Lf = p.flicker(phase) if motion else L
    for (dx, dy, c) in ((1, 2, R[4]), (2, 2, Gd[5]), (3, 2, R[4]), (4, 2, Gd[4]), (1, 3, R[3]), (2, 3, R[4]),
                        (3, 3, R[3]), (4, 3, R[3])):
        p.px(fx0 + dx, cy + dy, c if (night or dy == 2) else R[2 + (1 if c != R[3] else 0)], Lf)
    for lx in (bx0 + 2, bx1 - 3, fx0 + 5):                      # legs
        p.vline(lx, cy + r, base, K[2], L)
    p.px(bx0 + 1, base - 1, K[1], L)
    p.px(bx0 + 3, base - 1, K[1], L)
    if light:
        own = {(fx0 + dx, cy + dy) for dx in range(1, 5) for dy in (2, 3)}
        lamp(p, fx0 + 3, cy + 2.5, 10 if night else 6, phase, own)
    if night:
        p.halo(fx0 + 3, cy + 2.5, 4.2, 3.2, Gd[5], (0.1, 0.2, 0.3), L=p.flicker(phase, back=True) if motion else "haze")
    return x + 3, cy - r - 8


def _smoke_cells(seed, night, turn):
    """A drift of smoke, three soft puffs in a 12 by 10 square, pale and see-through; `turn` shifts them,
    the way smoke billows as it rises."""
    rnd = random.Random(seed)
    col = RAMP["linen"][5] if not night else RAMP["dusk"][5]
    cells = {}
    for i in range(3):
        cx, cy = rnd.uniform(2, 9), 7 - i * 3 + rnd.uniform(-0.5, 0.5)
        r = 1.6 + i * 0.5 + (0.4 if turn else 0)
        for yy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for xx in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) / r
                if d < 1 and 0 <= xx < 12 and 0 <= yy < 10:
                    a = 0.5 if d < 0.55 else 0.3
                    old = cells.get((xx, yy))
                    if old is None or float(old.split(":")[1]) < a:
                        cells[(xx, yy)] = f"{col}:{a:g}"
    return cells


def smoke(p: Pix, x, y, top, night, motion=True, drift=8, dur=6.0, seed=5, z=15):
    """Smoke rising from the stack at (x, y) to row `top`, drifting `drift` pixels with the wind, billowing as
    it goes, and gone, round and round. The still file holds a puff at the stack's mouth."""
    frames = []
    for turn in (False, True):
        key = ("smoke", seed, night, turn)
        if key not in p.syms:
            p.symbol(key, _smoke_cells(seed, night, turn))
        frames.append(key)
    if not motion:
        p.use(frames[0], x - 5, y - 10, "near")
        return
    n = max(12, round((y - top) / 2.4))
    path = []
    for s in range(n):
        t = s / (n - 1)
        path.append((round(x - 5 + drift * t ** 1.3 + 1.2 * math.sin(2 * math.pi * t * 1.3)),
                     round(y - 10 - (y - top) * t)))
    path += [(-30, -30)] * 2
    p.fly(frames, path, dur, z=z, flap=0.5)


def picnic_table(p: Pix, x, base, w=34, night=False, L="base"):
    """A picnic table under a red-and-white gingham cloth, its left end at `x` and standing on row `base`: the
    cloth's checks two pixels square, deep red where two red stripes cross, pale red where red crosses
    white, lit along its top edge and hanging over the front in scallops; below it the table's oak posts
    and, in front of them, the bench, its seat lit along the top. Returns the row its top is at."""
    R, Ln, O = RAMP["red"], RAMP["linen"], RAMP["oak"]
    k = -1 if night else 0
    top = base - 9
    for xx in range(x, x + w):
        for j in range(4):
            yy = top + j
            a, b = (xx - x) // 2 % 2, (j + 1) // 2 % 2
            c = (R[3 + k] if (a and b) else (R[5 + k] if (a or b) else Ln[6 + k]))
            if j == 0:
                c = step(c, 1) if c not in (Ln[6], Ln[5]) else c
            if j == 3 and (xx - x) % 4 == 3:
                continue                                         # the hem's scallop
            p.px(xx, yy, c, L)
    for px_ in (x + 3, x + w - 5):                               # the table's posts
        for yy in range(top + 4, base):
            p.px(px_, yy, O[4 + k], L)
            p.px(px_ + 1, yy, O[2 + k], L)
    p.hline(x + 1, x + w - 1, base - 4, O[5 + k], L)             # the bench, in front
    p.hline(x + 1, x + w - 1, base - 3, O[3 + k], L)
    for bx in (x + 6, x + w - 8):
        p.px(bx, base - 2, O[3 + k], L)
        p.px(bx, base - 1, O[2 + k], L)
    return top


def drink_jar(p: Pix, x, base, night=False, L="base", motion=True, phase=0, dur=2.0):
    """A glass jar of red drink, hibiscus steeped and sweetened, its left edge at `x`, standing on row `base`,
    9 wide and 14 tall: a silver lid, the glass bright down its left, the drink red and lit on its left with
    ice and a slice of lemon floating at its top, and a tap at its foot. In a moving file bubbles rise
    through it in turn."""
    S, R, Ln, Gd = RAMP["silver"], RAMP["red"], RAMP["linen"], RAMP["gold"]
    k = -1 if night else 0
    top = base - 14
    p.hline(x + 1, x + 8, top, S[5 + k], L)                     # the lid
    p.hline(x + 1, x + 8, top + 1, S[3 + k], L)
    for yy in range(top + 2, base - 1):
        for i in range(9):
            if i in (0, 8):
                c = S[6 + k] if i == 0 else S[3 + k]
            elif yy < top + 4:
                c = Ln[6 + k] if i < 3 else S[5 + k]
            else:
                c = R[5 + k] if i <= 2 else (R[4 + k] if i < 6 else R[3 + k])
            p.px(x + i, yy, c, L)
    for (dx, dy) in ((2, 4), (3, 4), (5, 5), (6, 5)):            # ice at the top of the drink
        p.px(x + dx, top + dy, Ln[6 + k] if dx % 2 else S[5 + k], L)
    p.px(x + 4, top + 4, Gd[5 + k], L)                          # a slice of lemon
    p.px(x + 4, top + 5, Gd[4 + k], L)
    p.hline(x, x + 9, base - 1, S[4 + k], L)                    # its foot
    p.px(x + 9, base - 4, S[5 + k], L)                          # the tap
    p.px(x + 10, base - 4, S[3 + k], L)
    p.px(x + 10, base - 3, S[3 + k], L)
    spots = [(x + 2, base - 4), (x + 5, base - 7), (x + 3, base - 10)]
    if not motion:
        p.px(*spots[0], R[6 + k], L)
        return
    for f in range(3):
        Lf = p.seq(f"dj{phase}{f}", round(f / 3, 3), round((f + 1) / 3, 3), dur, keep=f == 0, z=1)
        for s in range(2):
            p.px(*spots[(s + f) % 3], R[6 + k], Lf)


def glass_of_red(p: Pix, x, base, night=False, L="base"):
    """A mason jar of red drink, 4 wide and 6 tall, ice at its top and a straw leaning in it."""
    S, R, Ln = RAMP["silver"], RAMP["red"], RAMP["linen"]
    k = -1 if night else 0
    for yy in range(base - 6, base):
        for i in range(4):
            c = (S[6 + k] if i == 0 else S[3 + k]) if i in (0, 3) else (R[5 + k] if i == 1 else R[4 + k])
            if yy == base - 6 and i in (1, 2):
                c = Ln[6 + k]
            p.px(x + i, yy, c, L)
    p.px(x + 3, base - 8, Ln[6 + k], L)
    p.px(x + 2, base - 7, R[4 + k], L)


def watermelon_slices(p: Pix, x, base, n=3, night=False, L="base"):
    """Slices of watermelon on a platter, their left edge at `x`: each a wedge standing on its rind, the rind
    green, a pale band inside it, the flesh red and lit toward its tip, and black seeds. Returns the width."""
    R, G, Ln, K, S = RAMP["red"], RAMP["green"], RAMP["linen"], RAMP["coal"], RAMP["silver"]
    k = -1 if night else 0
    art = ["...a...", "..aba..", ".abkbb.", "abbbbkc", "ppppppp", "GGgggGG"]
    pal = {"a": R[5 + k], "b": R[4 + k], "c": R[3 + k], "k": K[0], "p": Ln[5 + k], "G": G[4 + k], "g": G[3 + k]}
    w = n * 6 + 1
    p.hline(x, x + w + 2, base - 1, S[5 + k], L)                # the platter
    p.hline(x + 1, x + w + 1, base - 2, S[4 + k], L)
    for i in range(n):
        p.sprite(x + 1 + i * 6, base - 8, art, pal, 1, L)
    return w + 2


def red_velvet_cake(p: Pix, x, base, night=False, L="base"):
    """A red velvet layer cake on a glass stand, its left edge at `x`, 13 wide: cream-cheese frosting white
    over its top with red crumbs on it, and a slice cut from its front, where the three red layers show
    between the white."""
    R, Ln, S = RAMP["red"], RAMP["linen"], RAMP["silver"]
    k = -1 if night else 0
    p.hline(x + 5, x + 8, base - 1, S[4 + k], L)                # the stand's foot
    p.px(x + 6, base - 2, S[5 + k], L)
    p.px(x + 6, base - 3, S[4 + k], L)
    p.hline(x, x + 13, base - 4, S[5 + k], L)                   # its plate
    p.hline(x + 1, x + 12, base - 5, S[6 + k], L)
    top = base - 12
    for yy in range(top, base - 5):
        for xx in range(x + 1, x + 12):
            cut = xx >= x + 7 and yy >= top + 1
            if cut:
                layer = (yy - top - 1) % 2
                c = R[3 + k] if layer == 0 else Ln[6 + k]
                if xx == x + 7:
                    c = R[2 + k] if layer == 0 else Ln[5 + k]
            else:
                c = Ln[6 + k] if xx < x + 5 else Ln[5 + k]
                if yy == base - 6:
                    c = Ln[4 + k]
            p.px(xx, yy, c, L)
    for (dx, dy) in ((2, 0), (4, 0), (3, 1), (8, 0)):           # crumbs on top
        p.px(x + dx, top + dy - (1 if dy == 0 else 0), R[4 + k], L)


def hibiscus(p: Pix, x, base, night=False, L="base"):
    """A red hibiscus in a clay pot, the flower the red drink is steeped from, its left edge at `x`: a bush of
    dark glossy leaves and three open blooms, each five red petals round a deeper heart and a gold stamen."""
    Bk, G, R, Gd = RAMP["brick"], RAMP["green"], RAMP["red"], RAMP["gold"]
    k = -1 if night else 0
    for j, (a, n) in enumerate(((0, 11), (1, 9), (1, 9), (2, 7), (2, 7))):   # the pot
        yy = base - 5 + j
        for i in range(n):
            c = Bk[5 + k] if j == 0 else (Bk[4 + k] if i < n // 2 else Bk[3 + k])
            p.px(x + a + i, yy, c, L)
    cells = set()
    for yy in range(base - 17, base - 5):
        for xx in range(x - 1, x + 12):
            if math.hypot((xx + 0.5 - (x + 5.5)) / 6.8, (yy + 0.5 - (base - 11)) / 6) <= 1:
                cells.add((xx, yy))
    pillow(p, cells, G if not night else G[:-1], L, lo=1, outline=True, spec=False)
    bloom = ["..a..", ".abb.", "abkbc", ".bbc.", "..c.."]
    for (fx, fy) in ((x - 1, base - 18), (x + 6, base - 16), (x + 2, base - 12)):
        p.sprite(fx, fy, bloom, {"a": R[5 + k], "b": R[4 + k], "c": R[3 + k], "k": R[1]}, 1, L)
        p.px(fx + 3, fy + 1, Gd[5 + k], L)                      # its stamen, standing out of the heart


def sign(p: Pix, x, base, text, night=False, L="base"):
    """A hand-painted sign on a stake, its left edge at `x`: a board of oak, lit along its top, the words in
    dark paint. By night the lamp beside it keeps it lit."""
    O = RAMP["oak"]
    w = Pix.measure(text, "35") + 6
    top = base - 15
    for yy in range(top, top + 9):
        for xx in range(x, x + w):
            c = O[6] if yy == top else (O[3] if yy == top + 8 else O[5])
            if xx in (x, x + w - 1):
                c = O[3]
            p.px(xx, yy, c, L)
    for yy in range(top + 9, base):
        p.px(x + w // 2, yy, O[3], L)
        p.px(x + w // 2 + 1, yy, O[2], L)
    p.text(x + 3, top + 2, text, C["ink"], "35", L=L)
    return w


# --------------------------------------------------------------------------- the island
def chapel(p: Pix, x, base, night=False, L="base", w=25, motion=True):
    """A brick chapel of the island, its left end at `x`, its front to us: red brick laid in courses, lit
    down its left, a steep gable roof, and over its door a bell tower with an open belfry, a pointed spire
    and a gold cross, pale stone quoins at its corners. A tall lancet of coloured glass in a stone frame
    stands each side of the tower, a round window over the door, and the door of oak stands under a
    pointed arch at the top of two steps. By night the windows glow warm through their colours."""
    Bk, K, O, Gd, B, R = RAMP["brick"], RAMP["coal"], RAMP["oak"], RAMP["gold"], RAMP["blue"], RAMP["red"]
    k = -1 if night else 0
    wall_top = base - 18
    for yy in range(wall_top, base):
        for xx in range(x, x + w):
            j = yy - wall_top
            mortar = j % 3 == 2 or (xx + (j // 3) * 2) % 5 == 0 and j % 3 != 2
            c = Bk[2 + k] if mortar and j % 3 == 2 else (Bk[5 + k] if xx < x + 2 else
                                                         (Bk[3 + k] if xx > x + w - 3 else Bk[4 + k]))
            if mortar and j % 3 != 2:
                c = Bk[3 + k]
            p.px(xx, yy, c, L)
    mid = x + w // 2
    for j in range(10):                                          # the gable roof
        yy = wall_top - 1 - j
        half = w // 2 + 1 - round(j * (w / 2 + 1) / 10)
        for xx in range(mid - half, mid + half + 1):
            c = K[4 + k] if xx < mid else K[3 + k]
            if xx in (mid - half,):
                c = K[5 + k]
            p.px(xx, yy, c, L)
    tw = 7
    tx = mid - tw // 2
    for yy in range(base - 34, base):                             # the tower
        for xx in range(tx, tx + tw):
            j = yy - (base - 34)
            c = Bk[5 + k] if xx == tx else (Bk[3 + k] if xx == tx + tw - 1 else Bk[4 + k])
            if j % 3 == 2:
                c = Bk[2 + k]
            p.px(xx, yy, c, L)
    for yy in range(base - 31, base - 26):                        # the belfry
        for xx in range(tx + 2, tx + 5):
            p.px(xx, yy, K[1], L)
    p.px(tx + 3, base - 32, K[1], L)
    p.px(tx + 3, base - 28, Gd[3 + k], L)                         # its bell
    p.px(tx + 3, base - 27, Gd[4 + k], L)
    for j in range(11):                                           # the spire
        yy = base - 35 - j
        half = 4 - round(j * 4 / 10)
        for xx in range(mid - half, mid + half + 1):
            p.px(xx, yy, K[4 + k] if xx <= mid else K[2 + k], L)
    p.px(mid, base - 46, Gd[5], L)                                # the cross
    p.px(mid, base - 47, Gd[5], L)
    p.px(mid, base - 48, Gd[5], L)
    p.px(mid - 1, base - 47, Gd[4], L)
    p.px(mid + 1, base - 47, Gd[4], L)
    for yy in range(base - 8, base):                              # the door under its arch
        for xx in range(mid - 2, mid + 3):
            if yy == base - 8 and xx != mid:
                continue
            if yy == base - 7 and xx in (mid - 2, mid + 2):
                continue
            p.px(xx, yy, O[4 + k] if xx < mid else O[3 + k], L)
    Ln = RAMP["linen"]
    stone, shade = (Ln[5 + k], Ln[3 + k]) if not night else (Ln[3], Ln[2])
    for c in range(6):                                            # quoins of pale stone at the corners
        n = 2 if c % 2 == 0 else 1
        for dy in range(2):
            for dx in range(n):
                p.px(x + dx, wall_top + 3 * c + dy, stone, L)
                p.px(x + w - 1 - dx, wall_top + 3 * c + dy, shade, L)
    glass = (B[3], R[3], Gd[3]) if not night else (B[5], R[5], Gd[5])
    own = set()
    lancet = ["..s..", ".sgs.", "sgggs", "sgggs", "sgggs", "sgggs", "sgggs", "sgggs", "sssss"]
    for wx in (x + 3, x + w - 8):                                 # a lancet each side, coloured glass in stone
        for j, row in enumerate(lancet):
            for dx, ch in enumerate(row):
                if ch == ".":
                    continue
                xx, yy = wx + dx, base - 16 + j
                if ch == "s":
                    p.px(xx, yy, stone if dx < 2 or j == 8 else shade, L)
                    continue
                pane = (glass[2] if j < 3 or (j // 2) % 2 else glass[1]) if dx == 2 else glass[(j // 2) % 2]
                if not night and j % 2 == 0 and j > 1:
                    pane = K[2]                                       # the leading between the panes
                p.px(xx, yy, pane, L)
                own.add((xx, yy))
        if night:
            p.halo(wx + 2.5, base - 11.5, 3.4, 4.6, Gd[5], (0.1, 0.2), L="haze")
            lamp(p, wx + 2, base - 12, 9, (wx // 3) % 3, own)
    rx, ry = mid, base - 16                                        # a round window on the tower
    for (dx, dy) in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        p.px(rx + dx, ry + dy, stone if dx < 1 and dy < 1 else shade, L)
    p.px(rx, ry, (R[5] if night else R[3]), L)
    if night:
        p.halo(rx + 0.5, ry + 0.5, 2.2, 2.2, Gd[5], (0.12, 0.22), L="haze")
    p.hline(mid - 4, mid + 5, base - 1, stone, L)                 # the steps up to the door
    p.hline(mid - 3, mid + 4, base - 2, shade, L)


def palm(p: Pix, x, base, h=30, night=False, L="base", lean=1, seed=0):
    """A palm along the seawall, standing on row `base` at column `x`: a slender trunk ringed where old fronds
    fell, leaning a little, and a crown of long fronds drooping all round, each a lit rib with a fringe of
    leaflets hanging from it, and two young fronds standing up from the heart."""
    O, G = RAMP["oak"], RAMP["green"]
    k = -1 if night else 0
    tx = x
    for j in range(h):
        yy = base - 1 - j
        tx = x + round(lean * (j / h) ** 2 * 4)
        ring = j % 3 == 0
        p.px(tx, yy, O[3 + k] if ring else O[5 + k], L)
        p.px(tx + 1, yy, O[2 + k] if ring else O[3 + k], L)
    cx, cy = tx + 1, base - h
    rnd = random.Random(seed)
    fronds = [(-165, 12), (-138, 11), (-112, 7), (-68, 7), (-42, 11), (-15, 12), (200, 9), (160, 9)]
    for a, length in fronds:
        th = math.radians(a + rnd.uniform(-5, 5))
        length += rnd.uniform(-1, 1)
        up = math.sin(th) < -0.9
        for s in range(1, int(length) + 1):
            t = s / length
            fx = cx + math.cos(th) * s
            fy = cy + math.sin(th) * s * (0.9 if up else 0.5) + (0 if up else (t ** 1.6) * length * 0.7)
            p.px(fx, fy, G[5 + k] if t < 0.6 else G[4 + k], L)
            p.px(fx, fy + 1, G[4 + k], L)
            if not up and t > 0.2:
                drop = 1 + (s % 2) + (1 if t > 0.6 else 0)
                for dd in range(2, 2 + drop):
                    p.px(fx, fy + dd, G[3 + k] if dd < 1 + drop else G[2 + k], L)
    for (dx, dy, c) in ((-1, 0, O[2 + k]), (0, 0, O[3 + k]), (-1, 1, O[2 + k]), (0, 1, O[2 + k]), (1, 1, O[1 + k])):
        p.px(cx + dx, cy + dy, c, L)


def _clump_cells(night, w, h, back=False, seed=1):
    """A clump of live-oak leaves `w` by `h` as pixels: a rounded mass lit on its upper left and dark beneath,
    its edge broken into leafy bumps and its face flecked; a clump at the back of the crown is a tone
    darker, in the shade of the ones in front."""
    G = RAMP["green"]
    k = (-1 if night else 0) - (1 if back else 0)
    rnd = random.Random(seed)
    cells = {}
    for yy in range(h):
        for xx in range(w):
            dx, dy = (xx + 0.5 - w / 2) / (w / 2), (yy + 0.5 - h * 0.55) / (h * 0.5)
            d2 = dx * dx + dy * dy
            if d2 > 1 - rnd.uniform(0, 0.22):
                continue
            lit = -(dx * 0.7 + dy * 0.9)
            t = 5 if lit > 0.5 else (4 if lit > 0.0 else (3 if lit > -0.55 else 2))
            if (xx * 3 + yy * 5 + seed) % 11 == 0:
                t = max(1, t - 1)                                  # a leafy fleck
            elif (xx + yy * 2 + seed) % 13 == 0 and t < 5:
                t += 1
            cells[(xx, yy)] = G[max(1, t + k)]
    return cells


def live_oak(p: Pix, x0, x1, base, trunk_x, night=False, top=24, bottom=60, seed=4):
    """A live oak spreading over the cookout, the shade tree of a Texas park and of Galveston: a short, thick
    trunk at `trunk_x` standing on row `base`, flared at its foot and furrowed, forking low into great limbs
    that reach out nearly level; a broad, low dome of leaf clumps from `x0` to `x1` between rows `top` and
    `bottom`, its underside a tone darker in its own shade, its top lit from the upper left and the gaps
    deep inside it in shadow; and Spanish moss hanging in grey strands from its underside. Each kind of
    clump is drawn once and placed again and again. Returns the row under the crown, where lights can
    hang."""
    O, S = RAMP["oak"], RAMP["silver"]
    k = -1 if night else 0
    fork = bottom + 10
    for yy in range(fork, base):                               # the trunk, flaring at its foot
        flare = 2 if yy >= base - 2 else (1 if yy >= base - 5 else 0)
        for i in range(-flare, 6 + flare):
            x = trunk_x + i
            c = O[4 + k] if i <= 0 else (O[2 + k] if i >= 4 else O[3 + k])
            if i in (1, 3) and (yy * 5 + i) % 4 == 0:
                c = O[2 + k]                                   # a furrow in the bark
            p.px(x, yy, c)
    limbs = {}
    mid = (x0 + x1) // 2
    _line(limbs, trunk_x + 1, fork + 1, trunk_x - 8, fork - 5)  # the great limb reaching out over the table
    _line(limbs, trunk_x - 8, fork - 5, trunk_x - 22, fork - 8)
    _line(limbs, trunk_x - 22, fork - 8, x0 + 26, bottom - 1)
    _line(limbs, x0 + 26, bottom - 1, x0 + 15, bottom - 6)
    _line(limbs, trunk_x + 2, fork, mid, bottom - 8)             # a limb up into the crown
    _line(limbs, trunk_x + 4, fork, x1 - 2, bottom - 4)          # and one out the other side
    for (x, y) in sorted(limbs):
        p.px(x, y, O[4 + k])
        p.px(x, y + 1, O[3 + k])
        p.px(x, y + 2, O[2 + k])
    rnd = random.Random(seed)
    shapes = {"back": (18, 10, True, 3), "under": (16, 9, True, 11), "top": (18, 11, False, 5),
              "end": (12, 7, False, 9)}
    cells = {}
    for name, (w, h, back, sd) in shapes.items():
        cells[name] = _clump_cells(night, w, h, back, sd)
        key = ("oak", name, night)
        if key not in p.syms:
            p.symbol(key, cells[name])
    span, depth = x1 - x0, bottom - top
    def at(u, v, w, h):
        return (round(x0 + u * span - w / 2) + rnd.randint(-1, 1), round(top + v * depth - h / 2) + rnd.randint(-1, 1))
    places = [("back", u, v) for u, v in ((0.12, 0.36), (0.36, 0.22), (0.6, 0.2), (0.84, 0.3))]
    places += [("under", u, v) for u, v in ((0.1, 0.72), (0.3, 0.8), (0.52, 0.84), (0.74, 0.8), (0.93, 0.74))]
    places += [("top", u, v) for u, v in ((0.2, 0.3), (0.44, 0.14), (0.68, 0.16), (0.9, 0.34))]
    places += [("end", u, v) for u, v in ((0.02, 0.58), (0.3, 0.52), (0.58, 0.5), (0.98, 0.58))]
    leaf = set()
    for i, (name, u, v) in enumerate(places):
        w, h, _, _ = shapes[name]
        x, y = at(u, v, w, h)
        places[i] = (name, x, y)
        leaf |= {(x + cx, y + cy) for (cx, cy) in cells[name]}
    span_of = {}
    for (x, y) in leaf:
        lo, hi = span_of.get(x, (y, y))
        span_of[x] = (min(lo, y), max(hi, y))
    def close(vals, low):
        """Fill notches in an edge no more than two columns wide, keeping its true bends."""
        out = {}
        for x in vals:
            a = [vals[i] for i in range(x - 2, x + 1) if i in vals]
            b = [vals[i] for i in range(x, x + 3) if i in vals]
            out[x] = min(max(a), max(b)) if low else max(min(a), min(b))
        return out
    his = close({x: hi for x, (lo, hi) in span_of.items()}, True)
    los = close({x: lo for x, (lo, hi) in span_of.items()}, False)
    span_of = {x: (los[x], his[x]) for x in span_of}
    G = RAMP["green"]
    for x, (lo, hi) in span_of.items():                       # the shade deep inside the crown
        for y in range(lo, hi + 1):
            if (x, y) not in leaf:
                p.px(x, y, G[1 + k])
    for name, x, y in places:
        p.use(("oak", name, night), x, y)
    Ln = RAMP["linen"]
    moss = (S[3], Ln[2], S[2]) if not night else (S[2], Ln[1], S[1])
    for i in range(11):                                       # Spanish moss hanging from the underside
        mx = x0 + 18 + round(i * (span - 24) / 10) + rnd.randint(-2, 2)
        if mx not in span_of or mx > 410:
            continue
        my = span_of[mx][1] + 1
        n = rnd.randint(3, 7)
        for j in range(n):
            p.px(mx + (1 if j > n * 0.6 and i % 2 else 0), my + j, moss[min(2, j * 3 // n)])
        p.px(mx + 1, my, moss[1])
        if n > 4:
            p.px(mx - 1, my + 1, moss[0])
            p.px(mx - 1, my + 3, moss[2])
    return max(hi for lo, hi in span_of.values()) + 1


def woodpile(p: Pix, x, base, night=False, L="base"):
    """A stack of split post oak for the pit, its left edge at `x`: three logs on the ground, two on them and
    one on top, their ends to us, each a round of pale heartwood ringed with dark bark, a ring in the wood
    and a dark heart."""
    O = RAMP["oak"]
    k = -1 if night else 0
    end = [".bbb.", "bhhhb", "bhrhb", "bhhhb", ".bbb."]
    pal = {"b": O[2 + k], "h": O[6 + k], "r": O[4 + k]}
    for row, (n, dx0) in enumerate(((3, 0), (2, 2), (1, 4))):
        for i in range(n):
            p.sprite(x + dx0 + i * 4, base - 5 - row * 4, end, pal, 1, L)


def ice_chest(p: Pix, x, base, night=False, L="base", w=12, h=8):
    """A red ice chest standing on row `base`, its left edge at `x`: a white lid lit along its top with a
    hinge line under it, a red body lit down its left and shaded to its right, and a white handle at its
    end."""
    R, Ln = RAMP["red"], RAMP["linen"]
    k = -1 if night else 0
    top = base - h
    for yy in range(top, base):
        for xx in range(x, x + w):
            j = yy - top
            if j < 2:
                c = Ln[6 + k] if j == 0 else Ln[4 + k]
            elif j == 2:
                c = Ln[3 + k]
            else:
                c = R[5 + k] if xx < x + 2 else (R[4 + k] if xx < x + w - 2 else R[3 + k])
            p.px(xx, yy, c, L)
    p.px(x + w, top + 4, Ln[5 + k], L)                          # the handle
    p.px(x + w, top + 5, Ln[4 + k], L)
    p.px(x + 3, top + 4, R[6 + k], L)
    p.hline(x + 1, x + w - 1, base - 1, R[2 + k], L)


def sailboat(p: Pix, x, y, night=False, L="base"):
    """A sailboat out on the Gulf, its hull's top-left at (x, y): a white mainsail lit on its luff and shaded
    toward its leech, a jib forward of the mast, a navy hull with a white boot stripe; by night its sails
    grey in the dark and a light burning at its masthead."""
    Ln, K, Gd, B, D = RAMP["linen"], RAMP["coal"], RAMP["gold"], RAMP["blue"], RAMP["dusk"]
    art = ["....m....", "...sm....", "..ssmj...", ".sssmjj..", "sssSmjjj.", "ssSSmjjj.",
           "hhhhhhhhh", "wwwwwwwww", ".hhhhhhh."]
    if not night:
        pal = {"s": Ln[6], "S": Ln[3], "m": K[3], "j": Ln[4], "h": B[2], "w": Ln[6]}
    else:
        pal = {"s": D[5], "S": D[4], "m": K[4], "j": D[4], "h": K[1], "w": D[4]}
    p.sprite(x, y - 6, art, pal, 1, L)
    if night:
        p.px(x + 4, y - 7, Gd[6], L)


def nova_glint(p: Pix, x, y, L="base"):
    """A glint like the flag's bursting star: a white heart, arms in the four directions and four fainter
    points between them."""
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, X["star_pale"], L)
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        p.px(x + dx, y + dy, RAMP["gold"][6] + ":0.55", L)


def dune(p: Pix, x0, x1, top, base, night=False, seed=3):
    """A sand dune between the seawall and the water, highest at `x0` and running down to the beach at `x1`:
    pale sand lit along its crest, and sea oats standing in it with their seed heads nodding."""
    S, G, Gd = RAMP["sand"], RAMP["green"], RAMP["gold"]
    k = -1 if night else 0
    rnd = random.Random(seed)
    for x in range(x0, x1):
        f = (x - x0) / max(1, x1 - x0 - 1)
        h = round((base - top) * (1 - f ** 1.6))
        crest = base - h
        for yy in range(crest, base):
            c = S[5 + k] if yy == crest else (S[4 + k] if yy < crest + 4 else S[3 + k])
            p.px(x, yy, c)
        if rnd.random() < 0.3 and h > 3:                      # sea oats
            for j in range(1, 5):
                p.px(x, crest - j, G[4 + k] if j < 3 else G[5 + k])
            p.px(x + 1, crest - 5, Gd[4 + k])
            p.px(x + 1, crest - 4, Gd[3 + k])


# --------------------------------------------------------------------------- a header's pieces
def flag_on_pole(p: Pix, x, top, base, w, h, night, motion, name="jf"):
    """The Juneteenth flag, `w` by `h`, flying from a pole standing on row `base` at column `x`, the flag's head
    a pixel under the pole's ball at row `top`."""
    flagpole(p, x, top, base, night, flag_foot=top + 4 + h)
    juneteenth_flag(p, x + 2, top + 4, w, h, night, motion=motion, name=name)


def wavy(x0, y0, x1, y1, n, amp=3, turns=1.0):
    """A path of `n` steps from (x0, y0) to (x1, y1), swaying up and down `amp` pixels."""
    return [(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + amp * math.sin(2 * math.pi * turns * t)))
            for t in (s / (n - 1) for s in range(n))]


def show(p: Pix, bursts, night, motion, dur=10.0, start=0.0):
    """The fireworks of a header, for the night only: each (x, y, r, colour, kind, light) goes up in turn from
    `start` of the way round a loop `dur` seconds long. A burst whose sparks or trail would cross a word is
    left out, and the rest keep their turns. The day files keep a clear sky."""
    if not night:
        return
    n = len(bursts)
    for i, (x, y, r, colour, kind, light) in enumerate(bursts):
        if not p.clear_of_words(x - r - 3, y - r - 3, x + r + 4, y + r + 14):
            continue
        off = start + (SHOW_SPAN - start) * i / max(1, n - 1)
        firework(p, x, y, r, colour, kind, motion=motion, offset=round(off, 3), dur=dur, seed=i + x, name=f"fw{i}",
                 light=light)


def title_edge(p: Pix, x, y, s, scale, edge, shadow):
    """What a day title set at (x, y) stands on, drawn before its letters: a `shadow` half a font pixel down and
    to the right, and an `edge` a pixel round every letter. Each letter's edge is the letter grown a pixel each
    way, kept once for each letter and size and placed again, which costs a quarter of four offset copies."""
    off = max(1, scale // 2)
    p.text(x + off, y + off, s, shadow, "57", scale)
    p.words.pop()                                   # the shadow is drawing, not words
    glyphs, _, space = FONTS["57"]
    cx = x
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        width, rows = glyphs[ch]
        key = ("edge", ch, scale)
        if key not in p.syms:
            ink = {(col * scale + dx, r * scale + dy) for r, cols in enumerate(rows) for col in cols
                   for dx in range(scale) for dy in range(scale)}
            p.symbol(key, {(a + ex, b + ey): 1 for (a, b) in ink for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))},
                     mono=True)
        p.use(key, cx, y, stroke=edge)
        cx += (width + 1) * scale


def title_glints(p: Pix, x, y, s, scale):
    """Here and there on a title set at (x, y) a glint like the flag's bursting star: on every third letter, at
    the top of its first stroke, each twinkling in its turn in a moving file."""
    glyphs, _, space = FONTS["57"]
    cx, n = x, 0
    for i, ch in enumerate(fold(s, "57")):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        width, rows = glyphs[ch]
        if i % 3 == 1 and rows[0]:
            nova_glint(p, cx + min(rows[0]) * scale + 1, y + 1, L=p.twinkle(n))
            n += 1
        cx += (width + 1) * scale


# --------------------------------------------------------------------------- the footers' and elements' pieces
def little_flag(p: Pix, x, y, base, night):
    """A little Juneteenth flag on a stick, its stick at column `x` from row `y` down to row `base`."""
    for yy in range(y, base):
        p.px(x, yy, RAMP["oak"][3 if night else 4])
    p.px(x, y - 1, RAMP["gold"][5])
    for (a, b), c in mini_flag_cells(night).items():
        p.px(x + 1 + a, y + b, c)


def clock_ring(p: Pix, cx, cy, r0, r1, night):
    """The upper half of a clock's face as a dial, between radii r0 and r1: a cream face lit on its left,
    a gold bezel round it bright along its upper left, and a tick at every hour of the half turn."""
    G, Lc = RAMP["gold"], RAMP["linen"]
    k = -1 if night else 0
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy) + 1):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not r0 <= rho <= r1 or dy > 0:
                continue
            if rho > r1 - 2.4:
                c = G[(5 if dx < 0 else 4) + k] if rho > r1 - 1.2 else G[3 + k]
            else:
                c = Lc[(6 if dx < -r1 * 0.2 else 5) + k]
                f = math.atan2(-dy, dx) / (math.pi / 6)
                if abs(f - round(f)) < 0.09 and rho > r1 - 6:
                    c = RAMP["blue"][2]                             # an hour's tick
            p.px(xx, yy, c)


def nova_seal(p: Pix, cx, cy, r, night, n=12):
    """A seal made like the Juneteenth flag's star, for behind a disc of radius `r`: a ring blue above and
    red below, parted by a white arc, and round it the white outline of a bursting nova, `n` points."""
    B, R, Ln = RAMP["blue"], RAMP["red"], RAMP["linen"]
    k = -1 if night else 0
    burst = _star_pts(cx, cy, r + 3, r - 0.5, n)
    for yy in range(math.floor(cy - r - 4), math.ceil(cy + r + 4)):
        for xx in range(math.floor(cx - r - 4), math.ceil(cx + r + 4)):
            px_, py_ = xx + 0.5, yy + 0.5
            if _near_poly(px_, py_, burst, 0.62):
                p.px(xx, yy, Ln[5] if night else Ln[6])
                continue
            if not _in_poly(px_, py_, burst):
                continue
            arc = cy + r * 0.2 - r * 0.3 * (1 - ((px_ - cx) / r) ** 2)
            if abs(py_ - arc) < 0.55:
                c = Ln[6 + k]
            else:
                lit = -((px_ - cx) * LX + (py_ - cy) * LY) / r
                t = 4 if lit > 0.2 else (3 if lit > -0.3 else 2)
                c = (B if py_ < arc else R)[t + k]
            p.px(xx, yy, c)


def pin(p: Pix, cx, cy, fam, face, night, initials="", letters=None, icon=None):
    """A celebration pin centred on (cx, cy): a flat button on the `fam` ramp, its face tone `face`, with a
    white rim rolled over its edge, lit on its upper left and shaded on its lower right, a darker ring inside
    the rim and a shine along the face's upper left; by day it casts a little shadow on the paper. On it the
    `initials` in `letters`, or an `icon` in dark ink."""
    ox, oy = cx + 0.5, cy + 1.5
    Rm, Ln = RAMP[fam], RAMP["linen"]
    for y in range(math.floor(oy - 9), math.ceil(oy + 9)):
        for x in range(math.floor(ox - 9), math.ceil(ox + 9)):
            dx, dy = x + 0.5 - ox, y + 0.5 - oy
            dd = math.hypot(dx, dy)
            if dd > 7.5:
                if not night and dd <= 8.6 and dx > 0.5 and dy > 0.5:
                    p.apx(x, y, RAMP["coal"][2], 0.2)                # its shadow on the paper
                continue
            if dd > 6.5:
                c = (Ln[6] if dx + dy < 0 else Ln[4]) if not night else (Ln[5] if dx + dy < 0 else Ln[3])
            elif dd > 5.5:
                c = Rm[face - 2]
            elif dd > 4.4 and dx + dy < -3.0:
                c = Rm[face + 2]
            else:
                c = Rm[face]
            p.px(x, y, c)
    if icon:
        p.sprite(round(cx) - 3, round(cy) - 2, icon, {"#": RAMP["coal"][2]})
    else:
        p.text(round(cx) - 3, round(cy) - 1, initials, letters, "35")
