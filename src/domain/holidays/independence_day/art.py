# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Independence Day set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the frame, the scenery a header stands on,
and every sprite, each shaded from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ..pixel import LX, LY, LZ, Paint, Pix, num, sphere
from .palette import C, GROUND, NIGHT_SKY, RAMP, X, step


def flag_fill(r, c, scale, night):
    """The colour the flag lays on a title's letter at row `r` and column `c` of the letter, counted in
    pixels from its top-left: the union's blue over its top three rows of the face, white stars on it in
    staggered rows, then stripes of white and red two pixels deep, ending on red at the letter's foot as
    the flag does. By night the blue is lit and the red a shade lighter, so both read on the sky."""
    R, N, W = RAMP["red"], RAMP["navy"], RAMP["cloth"]
    if r < 3 * scale:
        if r % 3 == 1 and (c + (r // 3) * 2) % 4 == 1:
            return W[6]
        return N[5] if night else N[3]
    k = (r - 3 * scale) // 2
    red = ((4 * scale + 1) // 2 - 1 - k) % 2 == 0
    if red:
        return X["flag_red_night"] if night else R[3]
    return W[5]


# The flag as a paint for a title's letters: one tile twelve pixels wide, the width of three of the union's
# stars, as tall as a letter, so every letter carries the same stars and stripes.
FLAG = Paint("flg", flag_fill, period=12)


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: cool white paper with a dot grid by day, by night a sky that
    lightens toward the horizon in five bands of blue."""
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
    arm = RAMP["gold"][5] if warm else (X["star_pale"] if night else RAMP["cloth"][3])
    p.px(x, y, C["white"] if night else RAMP["gold"][3], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.5", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """A night sky's stars at three magnitudes: faint pinpricks, bright points, and a few glints. None
    is set inside a box in `avoid` (x0, y0, x1, y1), so no glint sits in a letter or beside a word."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.5 or faint:   # `faint`: pinpricks only, for a sheet where a glint beside a word reads as a speck
            p.px(x, y, rnd.choice((X["star_faint"], X["star_dim"])), "haze")
        elif k < 0.88:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.5) else "haze"
            p.px(x, y, rnd.choice((C["white"], RAMP["gold"][5], X["star_pale"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.3)


def star_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="rod", corners=False):
    """The sheet's border: a band of the union's blue three pixels wide, lit along its top-left edge and
    set with white stars, and inside it a red rule. Each side is one pattern tile repeated, so the
    border costs a few hundred bytes however long it runs. `corners` sets a gold star at each corner."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    N, W = RAMP["navy"], RAMP["cloth"]
    tones = (N[5], N[4], N[3]) if night else (N[4], N[3], N[2])
    arm = (W[5], W[4], W[3]) if night else (W[4], W[3], W[2])
    gap = 8

    def tile(horizontal):
        cells = {}
        for a in range(gap):
            for b in range(3):
                cells[(a, b) if horizontal else (b, a)] = tones[b]
        c = 3
        star = {(c, 1): C["white"], (c - 1, 1): arm[1], (c + 1, 1): arm[1], (c, 0): arm[0], (c, 2): arm[2]}
        for (a, b), col in star.items():
            cells[(a, b) if horizontal else (b, a)] = col
        return cells

    for name, horizontal in (("h", True), ("v", False)):
        cells = tile(horizontal)
        tw, th = (gap, 3) if horizontal else (3, gap)
        p.defs.append(f'<pattern id="{uid}{name}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
                      f'{p._paths(cells)}</pattern>')
    p.defs.append(f'<rect id="{uid}H" width="{w}" height="3" fill="url(#{uid}h)"/>')
    p.defs.append(f'<rect id="{uid}V" width="3" height="{h - 6}" fill="url(#{uid}v)"/>')
    for (name, bx, by) in (("H", x, y), ("H", x, y + h - 3), ("V", x, y + 3), ("V", x + w - 3, y + 3)):
        p.shapes["base"].append(f'<use href="#{uid}{name}" x="{bx}" y="{by}"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, RAMP["red"][4] if night else RAMP["red"][3])
    if corners:
        for (cx_, cy_) in ((x + 1, y + 1), (x + w - 6, y + 1), (x + 1, y + h - 6), (x + w - 6, y + h - 6)):
            star5(p, cx_, cy_, 5, "gold", night, reuse=True)


def spangles(p: Pix, x0, x1, y, seed=7, L="base", night=False, twinkling=False, big=0.0, gap=(9, 26)):
    """Stars lying along a ledge whose top edge is row `y`, the way snow or slime would lie in another
    set: little four-point stars in gold, red and white, each lit at its heart, set at uneven gaps, now
    and then a five-point star where `big` allows. In a moving file a few of them twinkle."""
    rnd = random.Random(seed * 131 + x0)
    R, N, Gd, W = RAMP["red"], RAMP["navy"], RAMP["gold"], RAMP["cloth"]
    kinds = [("gold", Gd[5] if night else Gd[3], Gd[6] if night else Gd[4], Gd[3] if night else Gd[2]),
             ("red", R[5] if night else R[3], R[6] if night else R[4], R[4] if night else R[2]),
             ("white", W[5] if night else N[4], C["white"] if night else N[5], W[3] if night else N[3])]
    x = x0 + rnd.randint(2, 6)
    i = 0
    while x < x1 - 2:
        name, arm, core, foot = kinds[(i + seed) % 3]
        if big and rnd.random() < big and x + 5 < x1:
            star5(p, x - 2, y - 5, 5, name if (night or name != "white") else "navy", night, L=L)
            x += 4
        else:
            Lx = p.twinkle(i, back=False) if twinkling and rnd.random() < 0.35 else L
            p.px(x, y - 2, core, Lx)
            p.px(x - 1, y - 2, arm, Lx)
            p.px(x + 1, y - 2, arm, Lx)
            p.px(x, y - 3, arm, Lx)
            p.px(x, y - 1, foot, Lx)
        x += rnd.randint(*gap)
        i += 1


# --------------------------------------------------------------------------- bunting
def _swag_cells(span, depth, night):
    """One swag of bunting, `span` wide, gathered at both ends and hanging `depth` at its middle: the
    union's blue along the top with white stars, then a white band and a red one, each band lit along
    its upper edge. It is gathered into folds that fan out from the tacks, lit on their left faces."""
    R, N, W = RAMP["red"], RAMP["navy"], RAMP["cloth"]
    k = 0 if not night else -1
    cells = {}
    for i in range(span + 1):
        u = i / span
        s = math.sin(math.pi * u)
        top = round(1.2 * s)
        bot = round(depth * s ** 0.75) + 1
        fold = math.sin(u * math.pi * 7) * (0.4 + 0.6 * s)       # the folds, stronger toward the middle
        n = bot - top + 1

        def band(yy):
            f = (yy - top + 0.5) / n
            return 0 if f < 0.34 else (1 if f < 0.67 else 2)

        for yy in range(top, bot + 1):
            b = band(yy)
            edge_top = yy == top or band(yy - 1) != b
            t = 3 + (1 if fold > 0.35 else (-1 if fold < -0.35 else 0)) + (1 if edge_top else 0)
            if yy == bot:
                t -= 1
            if b == 0:
                c = N[max(1, min(5, t + k))]
                if (i * 3 + yy * 5) % 7 == 0 and n >= 4 and yy > top:
                    c = W[6] if not night else W[5]
            elif b == 1:
                c = W[max(2, min(6, t + 2 + k))]
            else:
                c = R[max(1, min(5, t + k))]
            cells[(i, yy)] = c
    return cells


def rosette(p: Pix, x, y, night=False, L="base", reuse=True):
    """A bunting rosette, 5 by 5, top-left at (x, y): a red ring, a white ring and a blue heart, lit
    from the upper left. It covers each tack the swags hang from."""
    R, N, W = RAMP["red"], RAMP["navy"], RAMP["cloth"]
    k = -1 if night else 0
    art = [".abb.", "awwwc", "bwnwc", "bwwwd", ".ccd."]
    pal = {"a": R[5 + k], "b": R[4 + k], "c": R[3 + k], "d": R[2 + k], "w": W[5 + k], "n": N[3 + k]}
    p.sprite(x, y, art, pal, L=L, reuse=reuse)


def bunting(p: Pix, x0, x1, y, span=41, depth=7, night=False):
    """Swags of bunting along the top: each swag drawn once and hung again and again from a rosette at
    every tack, the last swag cut to fit."""
    xs = list(range(x0, x1 - span // 2, span))
    for i, xa in enumerate(xs):
        sp = min(span, x1 - xa)
        key = ("swag", sp, depth, night)
        if key not in p.syms:
            p.symbol(key, _swag_cells(sp, depth, night))
        p.use(key, xa, y)
    for xa in xs + [min(xs[-1] + span, x1)]:
        star5(p, xa - 2, y - 2, 5, "gold", night, reuse=True)


def half_fan(p: Pix, cx, y, r, night=False, L="base", quarter=None):
    """A pleated fan of bunting hanging from row `y`, centred on `cx`: a blue heart with white stars,
    then stripes of white and red out to a red rim, gathered into pleats that alternate lit and shaded.
    `quarter` ("left" or "right") keeps only one half, for a corner."""
    R, N, W = RAMP["red"], RAMP["navy"], RAMP["cloth"]
    k = -1 if night else 0
    heart = r * 0.38
    width = max(1.6, (r - heart) / 4)
    for yy in range(y, y + math.ceil(r) + 1):
        for xx in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - y
            rho = math.hypot(dx, dy)
            if rho > r or dy < 0:
                continue
            if quarter == "left" and dx > 0.5 or quarter == "right" and dx < -0.5:
                continue
            th = math.atan2(dy, dx)                  # 0 to pi across the fan
            pleat = int(th / (math.pi / 11))
            lit = 1 if pleat % 2 == 0 else -1
            if rho <= heart:
                c = N[3 + k + (1 if lit > 0 else 0)]
                if (xx * 3 + yy * 7) % 6 == 0 and rho > 1.2:
                    c = W[6 + k]
            else:
                band = int((rho - heart) / width)
                if band % 2 == 0:
                    c = W[5 + k + (0 if lit > 0 else -1)]
                else:
                    c = R[3 + k + (1 if lit > 0 else 0)]
                if rho > r - 1:
                    c = R[2 + k + (1 if lit > 0 else 0)]
            p.px(xx, yy, c, L)
    rosette(p, round(cx) - 2, y - 2, night, L, reuse=False)


def fan_ring(p: Pix, cx, cy, r0, r1, night, L="base"):
    """The upper half of a pleated fan of bunting between radii r0 and r1: a band of the union's blue with
    white stars, then stripes of white and red out to a red rim, gathered into twenty pleats. Each pleat
    is folded: its face toward the light a tone up, its face away a tone down, and a crease between."""
    R, W, N = RAMP["red"], RAMP["cloth"], RAMP["navy"]
    k = -1 if night else 0
    n = 20
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy) + 1):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not r0 <= rho <= r1 or dy > 0:
                continue
            th = math.atan2(-dy, dx)                       # 0 at the right, pi at the left
            f = (math.pi - th) / (math.pi / n)              # which pleat, and how far across it
            within = f - math.floor(f)
            face = 1 if within < 0.5 else -1               # the half toward the light, then the half away
            crease = within > 0.9 and rho > r0 + 2.2
            if rho < r0 + 2.2:
                c = N[max(1, 3 + k + (1 if face > 0 else -1))]
                if (xx * 5 + yy * 3) % 4 == 0:
                    c = W[6 + k]
                p.px(xx, yy, c, L)
                continue
            band = int((rho - r0 - 2.2) / ((r1 - r0 - 2.2) / 3))
            if rho > r1 - 1 or band % 2 == 0:
                c = R[max(1, min(6, 3 + k + face))]
            else:
                c = W[max(2, min(6, 5 + k + (1 if face > 0 else -1)))]
            if crease:
                c = step(c, -1)
            p.px(xx, yy, c, L)


def seal_rosette(p: Pix, cx, cy, r0, r1, night, L="base"):
    """A prize rosette round a seal, pleated: rings of white, red and blue from r0 out to r1, gathered
    into pleats that are lit and shaded by turns, lit on the side that faces the light."""
    R, W, N = RAMP["red"], RAMP["cloth"], RAMP["navy"]
    k = -1 if night else 0
    n = 28
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 1):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            wob = 0.7 * math.cos(th * n)                        # the pleats crimp the rim
            if not r0 - 0.5 <= rho <= r1 + wob - 0.3:
                continue
            pleat = int((th + math.pi) / (2 * math.pi / n))
            facing = (dx * LX + dy * LY) / max(1.0, rho)
            t = (1 if pleat % 2 == 0 else -1) + (1 if facing > 0.35 else (-1 if facing < -0.35 else 0))
            f = (rho - r0) / (r1 - r0)
            if f < 0.34:
                c = W[max(2, min(6, 5 + t + k))]
            elif f < 0.67:
                c = R[max(1, min(6, 3 + t + k))]
            else:
                c = N[max(1, min(6, 3 + t + k))]
            p.px(x, y, c, L)


# --------------------------------------------------------------------------- fireworks
BURST_TIERS = 3   # 0 a star's white-hot head, 1 the bright part of its trail, 2 the trail as it cools


def _burst_frame(kind, r, frame, seed=0, rise=None):
    """The pixels of one frame of a firework, relative to where it bursts, each with a tier: `frame` is
    "trail1" and "trail2" (the shell rising on its trail of sparks), "open" (the break: a flash and the
    stars just thrown out), "bloom" (the full burst), "fall" (the stars sinking, glitter crackling among
    them) or "fade" (the last embers). Every star flies on its own arc: thrown out from the break, slowed
    by the air and pulled down, and its trail is drawn along the arc behind it, white-hot at the head and
    cooling back along it. A willow's stars are heavy and fall far, so its trails weep. `rise` is how far
    below the burst the rising trail first shows."""
    rnd = random.Random(seed * 17 + int(r * 10))
    cells = {}

    def put(x, y, t):
        q = (math.floor(x), math.floor(y))
        if q not in cells or cells[q] > t:
            cells[q] = t

    if frame in ("trail1", "trail2"):
        y0 = (r + 7 if rise is None else rise) if frame == "trail1" else round(r * 0.45) + 3
        wob = 1 if seed % 2 else -1
        for i, t in enumerate((0, 1, 1, 2, 2, 2)):
            put(0.5 + (wob if i in (3, 5) else 0) * (i >= 3) * 0.6, y0 + i + 0.5, t)
        return cells
    n = 16 if r >= 12 else (12 if r >= 8 else 10)
    if kind == "ring":
        n = 22 if r >= 12 else 16
    drop = {"peony": 0.12, "willow": 0.4, "ring": 0.08}[kind] * r        # how far a star has fallen at full bloom
    a0 = rnd.uniform(0, 2 * math.pi / n)
    stars_ = []
    for j in range(n):
        a = a0 + j * 2 * math.pi / n + rnd.uniform(-0.07, 0.07)
        stars_.append((math.cos(a), math.sin(a), r * rnd.uniform(0.9, 1.04)))

    def at(ca, sa, rj, t):
        out = rj * (1 - math.exp(-2.2 * t)) / (1 - math.exp(-2.2))      # thrown out, slowed by the air
        return 0.5 + ca * out, 0.5 + sa * out + drop * t * t             # and pulled down

    def arc(ca, sa, rj, t_end, length, tiers):
        """The star at time `t_end` and its trail back along its arc for `length` of the flight."""
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
    for k, (ca, sa, rj) in enumerate(stars_):
        if kind == "ring":
            if frame == "bloom":
                x, y = at(ca, sa, rj, 1.0)
                put(x, y, 0 if k % 2 == 0 else 1)
                x2, y2 = at(ca, sa, rj, 0.8)
                put(x2, y2, 2)
                if k % 2 == 0:
                    x3, y3 = at(ca, sa, rj * 0.5, 1.0)
                    put(x3, y3, 2)
            elif frame == "fall" and k % 2 == 0:
                arc(ca, sa, rj, 1.35, 0.15, (1, 2))
            elif frame == "fade" and rnd.random() < 0.35:
                x, y = at(ca, sa, rj, 1.7)
                put(x, y, 2)
            continue
        if frame == "bloom":
            if kind == "willow":
                arc(ca, sa, rj, 1.0, 0.72, (0, 1, 2, 2, 2))
            else:
                arc(ca, sa, rj, 1.0, 0.42, (0, 1, 1, 2, 2, 2))
                if r >= 12 and k % 2 == 1:                     # an inner shell, smaller and dimmer
                    x, y = at(ca, sa, rj * 0.45, 1.0)
                    put(x, y, 2)
        elif frame == "fall":
            if kind == "willow":
                arc(ca, sa, rj, 1.45, 0.9, (1, 2, 2, 2))
            else:
                arc(ca, sa, rj, 1.35, 0.3, (1, 2, 2))
                if rnd.random() < 0.5:                         # glitter crackling among the falling stars
                    x, y = at(ca, sa, rj, 1.35)
                    put(x + rnd.choice((-2, -1, 1, 2)), y + rnd.choice((-2, -1, 1)), 0)
        else:   # fade: the last embers, sinking and going out
            if rnd.random() < (0.7 if kind == "willow" else 0.5):
                if kind == "willow":
                    arc(ca, sa, rj, 1.85, 0.5, (2,))
                else:
                    x, y = at(ca, sa, rj, 1.75)
                    put(x, y, 2)
                    if rnd.random() < 0.35:
                        put(x + rnd.choice((-1, 1)), y - 2, 1)
    return cells


def _burst_symbols(p: Pix, kind, r, frame, seed, rise=None):
    """A frame drawn once: one path for each of its three tiers, each taking its colour where it is used."""
    key = ("burst", kind, r, frame, seed, rise if frame == "trail1" else None)
    if key not in p.syms:
        cells = _burst_frame(kind, r, frame, seed, rise)
        tiers = []
        for t in range(BURST_TIERS):
            part = {q: 1 for q, tt in cells.items() if tt == t}
            if part:
                tiers.append((t, p.symbol((key, t), part, mono=True)))
        p.syms[key] = tiers
    return key


def burst_cells(kind, r, frames, seed=0, rise=None) -> set:
    """Every pixel a firework's `frames` light, relative to where it bursts: what must lie clear of words."""
    return {q for frame in frames for q in _burst_frame(kind, r, frame, seed, rise)}


# The colours a burst takes: each star's head, the bright part of its trail and the trail as it cools.
# By night the heads burn white and the trails fade into the sky; by day, on the paper, the heads are
# the deepest tone and the trails lighten away from them.
R_, N_, G_, E_, W_ = RAMP["red"], RAMP["navy"], RAMP["gold"], RAMP["ember"], RAMP["cloth"]
BURST_COLOURS = {
    "red": {"day": (R_[2], R_[3], R_[4]), "night": (C["white"], R_[5], R_[3])},
    "blue": {"day": (N_[2], N_[3], N_[5]), "night": (C["white"], N_[6], N_[4])},
    "gold": {"day": (E_[3], G_[3], G_[4]), "night": (G_[6], G_[4], G_[2])},
    "white": {"day": (N_[3], W_[2], W_[3]), "night": (C["white"], W_[5], W_[3])},
}
FRAMES = [("trail1", 0.0, 0.06), ("trail2", 0.06, 0.12), ("open", 0.12, 0.17), ("bloom", 0.17, 0.34),
          ("fall", 0.34, 0.45), ("fade", 0.45, 0.54)]
SHOW_SPAN = 1 - FRAMES[-1][2]      # how far round the loop the last firework of a show may start


def firework(p: Pix, cx, cy, r, colour="red", kind="peony", night=False, motion=True, offset=0.0, dur=5.4,
             seed=0, name=None, glow=True, light=0, rise=None):
    """A firework bursting at (cx, cy), `r` pixels across its sparks. In a moving file it rises as a
    trail of sparks, breaks with a flash, blooms, sinks with glitter crackling among its stars and goes
    out in embers, each frame shown for its moment of a loop `dur` seconds long starting at `offset` of
    the way round, so several can take turns. The still file shows it in full bloom. By night `light` (a
    radius) washes its colour over whatever stands below it while it blooms. `rise` shortens the trail
    where words lie below, so it never passes behind them."""
    mode = "night" if night else "day"
    cols = BURST_COLOURS[colour][mode]
    name = name or f"fw{len([k for k in p.layers if k.startswith('fw')])}"
    frames = FRAMES if motion else [f for f in FRAMES if f[0] == "bloom"]
    for fname, t0, t1 in frames:
        if motion:
            L = p.seq(f"{name}{fname[0]}{fname[-1]}", round(offset + t0, 3), round(offset + t1, 3), dur,
                      keep=fname == "bloom")
        else:
            L = p.layer("fw", z=-12)
        key = _burst_symbols(p, kind, r, fname, seed, rise)
        if glow and night and fname == "open":
            p.shapes[L].append(f'<ellipse cx="{num(cx + 0.5)}" cy="{num(cy + 0.5)}" rx="3.5" ry="3.5" '
                               f'fill="{cols[1]}" fill-opacity=".3"/>')
        for t, sid in p.syms[key]:
            p.uses[L].append((cols[t], sid, cx, cy, 1))
        if light and fname == "bloom":
            flash(p, cx, cy, light, cols[1], L, night)


def flash(p: Pix, cx, cy, r, col, L, night):
    """A firework's light on the drawn things below it (the pole, the grass, the picnic, the rule),
    strongest nearest the burst, on a layer of its own over the drawing that shows while the burst is in
    bloom. The paper, the sky and the words take none."""
    base = p.layers["base"]
    Lf = L + "f"
    if Lf not in p.layers:
        p.layer(Lf, p.meta[L][2], z=2.5)
    alphas = (0.07, 0.13, 0.2) if night else (0.04, 0.07)
    n = len(alphas)
    for (x, y) in list(base):
        d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 0.8) / r
        if d < 1 and y > cy:
            p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], Lf)


# --------------------------------------------------------------------------- the lawn
def lawn(p: Pix, x0, x1, y_top, y_bot, seed=5, night=False, L="base", flowers=True):
    """A lawn along the foot of a drawing: a rolling crest of mown grass with blades standing up from
    it, darker toward the rule it rests on, and here and there a clover flower."""
    G = RAMP["green"]
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
        if r_ < 0.34:
            p.px(x, top - 1, G[5 + k] if rnd.random() < 0.5 else G[4 + k], L)
            if r_ < 0.1:
                p.px(x, top - 2, G[4 + k], L)
        elif flowers and r_ > 0.975:
            p.px(x, top - 1, RAMP["cloth"][6 + k], L)


def treeline(p: Pix, x0, x1, base, h=12, night=False, seed=3, L="base", taper=(True, True)):
    """A line of trees along the far edge of the lawn, their foot on row `base`: rounded crowns that
    overlap, the tallest about `h`, each lit on its upper left, with leaves speckled darker through them.
    By day they are a tone lighter than the lawn in front of them, as far things are; by night they stand
    dark against the sky, the night's blue light on their crowns. `taper` lowers the
    line toward either end, where it gives way to the paper or the sky."""
    G, K = RAMP["green"], RAMP["coal"]
    rnd = random.Random(seed)
    crowns = []
    x = x0 - 2
    while x < x1 + 2:
        r = rnd.uniform(3.5, 6.5)
        hc = rnd.uniform(0.55, 1.0) * h
        f0 = (x - x0) / max(1, x1 - x0)
        if taper[0]:
            hc *= min(1.0, 0.45 + f0 * 3.5)
        if taper[1]:
            hc *= min(1.0, 0.45 + (1 - f0) * 3.5)
        crowns.append((x + r * 0.5, r, hc))
        x += rnd.uniform(3.5, 6.5)
    top, owner = {}, {}
    for xx in range(x0, x1):
        best = None
        for (cxc, r, hc) in crowns:
            dxn = (xx + 0.5 - cxc) / r
            if abs(dxn) >= 1:
                continue
            t = base - hc * math.sqrt(1 - dxn * dxn) ** 0.6
            if best is None or t < best[0]:
                best = (t, (cxc, r, hc))
        if best:
            top[xx], owner[xx] = round(best[0]), best[1]
    for xx, ty in top.items():
        cxc, r, hc = owner[xx]
        for yy in range(ty, base):
            dxn = (xx + 0.5 - cxc) / r
            dyn = (yy + 0.5 - (base - hc * 0.6)) / max(1.0, hc * 0.6)
            lit = -dxn * 0.55 - dyn * 0.6
            edge = yy == ty
            if night:
                c = K[3] if lit > 0.35 else K[2]
                if edge and dxn < -0.25:
                    c = K[4]
            else:                                              # far off, so a tone lighter than the lawn before them
                c = G[5] if lit > 0.45 else (G[4] if lit > -0.1 else G[3])
                if edge and dxn < 0.1:
                    c = G[6]
            if not edge and (xx * 7 + yy * 5 + seed) % 9 == 0:
                c = (K[1] if night else G[3]) if c != (K[1] if night else G[3]) else c
            p.px(xx, yy, c, L)


def light_pool(p: Pix, cx, y, rx, ry, night, col=None):
    """A light pooled on the grass round its foot: only the lawn takes it."""
    col = col or RAMP["gold"][4]
    if night:
        p.halo(cx, y, rx, ry, col, (0.1, 0.18, 0.27, 0.36), L="pool", only=GROUND)
    else:
        p.halo(cx, y, rx, ry, col, (0.05, 0.09), L="pool", only=GROUND)


def glow_cells(cx, cy, rx, ry, col, alphas, skip=()):
    """A small stepped glow as see-through pixels around (cx, cy), leaving out the pixels in `skip`."""
    out, n = {}, len(alphas)
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d < 1 and (x, y) not in skip:
                out[(x, y)] = f"{col}:{alphas[min(n - 1, int((1 - d) * n))]:g}"
    return out


def fireflies(p: Pix, x0, x1, y0, y1, n, night, seed=0, motion=True):
    """Fireflies over the grass on a summer night, each a warm point in a small glow that flashes and
    goes out in its own time. By day there are none to see."""
    if not night:
        return
    rnd = random.Random(seed)
    Gd, Gr = RAMP["gold"], RAMP["green"]
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
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


# --------------------------------------------------------------------------- light that falls on things
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `lamplight` lays its warm light on
    whatever stands within `r` of it, flickering with the flame. `own` are the lamp's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def lamplight(p: Pix, night: bool):
    """The finishing pass: each sparkler's light on the drawn things near it (the grass, the blanket,
    the rule), strongest nearest the flame. The paper, the sky and the words take none."""
    base = p.layers["base"]
    col = RAMP["gold"][4]
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
    """The shadow a thing standing on the lawn leaves right under it: only the grass takes it."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.7, X["shade_ink"], (0.22, 0.38), L="pool", only=GROUND, shape=False)


# --------------------------------------------------------------------------- lines
def _line(cells: dict, x0, y0, x1, y1, tag=1):
    """A one-pixel line, each step touching the last, the way a pixel artist draws a spark."""
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


# --------------------------------------------------------------------------- stars
STAR_ART = {
    5: ["..#..", "..#..", "#####", ".###.", ".#.#."],
    7: ["...#...", "..###..", "#######", ".#####.", "..###..", ".##.##.", ".#...#."],
    9: ["....#....", "....#....", "...###...", "#########", ".#######.", "..#####..", "..#####..", ".###.###.",
        ".##...##."],
    11: [".....#.....", ".....#.....", "....###....", "....###....", "###########", ".#########.", "..#######..",
         "...#####...", "..#######..", "..###.###..", ".##.....##."],
}
STAR_RAMPS = {"gold": ("gold", 3), "red": ("red", 3), "white": ("cloth", 3), "navy": ("navy", 3)}


def star_cells(size=7, colour="gold", night=False) -> dict:
    """A five-point star's pixels, `size` square, {(x, y): colour} from its top-left, bevelled: each arm
    has a ridge down its middle, the facet facing the light a tone up and the other a tone down, with a
    glint at its heart."""
    name, mid = STAR_RAMPS[colour]
    Rm = RAMP[name]
    if night:
        mid += 2 if colour == "white" else 1
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
    return cells


def star5(p: Pix, x, y, size=7, colour="gold", night=False, L="base", reuse=False):
    """A five-point star (see `star_cells`), top-left at (x, y). `reuse` draws it once in <defs> and places
    it with <use>, for a star that appears again and again."""
    key = ("star5", size, colour, night)
    if not reuse:
        for (i, j), c in star_cells(size, colour, night).items():
            p.px(x + i, y + j, c, L)
        return
    if key not in p.syms:
        p.symbol(key, star_cells(size, colour, night))
    p.use(key, x, y, L)


# --------------------------------------------------------------------------- the flag
def _flag_geometry(sh):
    """The flag's proportions on the grid for stripes `sh` pixels deep: its hoist, its fly, the union."""
    h = 13 * sh
    return h, round(h * 1.9), 7 * sh, round(h * 0.76)


FLUTTER_FROM = 0.45    # the part of the flag's length from the hoist that holds still while the rest flutters


def _flag_wave(sh, i, phase=0.0, flutter=None):
    """Column `i` of a flag rippling at `phase`: how far it rises or falls, and how it faces the light
    (-1 turned away, 0 square on, 1 toward it, 2 a crest catching the light full on). `flutter`, a phase,
    adds a second, quicker wave out at the fly, nothing at all where it starts, so the flag's free end can
    flutter while the part by the pole holds still."""
    h, w, _, _ = _flag_geometry(sh)
    amp = 1.1 + 0.08 * h

    def off(k):
        u = k / w
        o = amp * u * math.sin(2 * math.pi * (u * 1.35 - phase))
        if flutter is not None and u > FLUTTER_FROM:
            env = ((u - FLUTTER_FROM) / (1 - FLUTTER_FROM)) ** 1.4
            o += (0.6 + 0.07 * h) * env * math.sin(2 * math.pi * (u * 1.8 - flutter))
        return o

    slope = off(i + 1) - off(i - 1) if i else off(1) - off(0)
    shade = 1 if slope < -0.22 else (-1 if slope > 0.22 else 0)
    crest = abs(slope) < 0.12 and math.sin(2 * math.pi * (i / w * 1.35 - phase)) < 0 and i > w * 0.15
    return round(off(i)), shade + (1 if crest else 0)


def _flag_kind(sh, i):
    """What column `i` of the flag holds: the union with stars on its even rows, the union with stars on
    its odd rows, the union with none, a column of stripes, or the last column at the fly's hem."""
    h, w, uh, uw = _flag_geometry(sh)
    if i < uw:
        sx = i - 1
        if 0 <= sx < uw - 2 and sx % 2 == 0:
            return ("union", sx % 4)
        return ("union", None)
    return ("hem",) if i == w - 1 else ("stripes",)


def _flag_column(sh, kind, tone, night):
    """One column of the flag as its pixels, top to bottom: stripes red and white `sh` deep, or the union's
    blue with its stars, `tone` steps lit or shaded. By night the lower rows are a tone brighter, where the
    lamp at the foot of the pole throws its light up the cloth."""
    R, N, W = RAMP["red"], RAMP["navy"], RAMP["cloth"]
    h, w, uh, uw = _flag_geometry(sh)
    k = -1 if night else 0
    cells = {}
    for j in range(h):
        lift = 1 if night and j >= h * 0.55 else 0
        t = tone + k + lift
        if kind[0] == "union" and j < uh:
            sy = j - 1
            star = kind[1] is not None and 0 <= sy < uh - 2 and sy % 2 == 0 and (kind[1] + (sy // 2) % 2 * 2) % 4 == 0
            c = (W[6] if tone >= 0 else W[5]) if star else N[max(1, min(5, 3 + t))]
        elif (j // sh) % 2 == 0:
            c = R[max(1, min(6, 3 + t))]
        else:
            c = W[max(2, min(6, 5 + t))] if kind[0] != "hem" else W[3 + k + lift]
        cells[(0, j)] = c
    return cells


def flag(p: Pix, x, y, sh=2, night=False, L="base", phase=0.0, flutter=None):
    """The flag, flying from its hoist at (x, y): thirteen stripes `sh` pixels deep, red at the top and
    the foot, and the union, blue with its stars in staggered rows, over the top seven. It ripples: each
    column rises and falls on a wave that grows toward the fly, and the cloth is lit where it faces the
    light and shaded where it turns away. By night it is lit from below, as the Flag Code asks of a flag
    flown after dark. Drawn in pixels, for a flag that holds still. Returns its pixels."""
    h, w, _, _ = _flag_geometry(sh)
    cells = {}
    for i in range(w):
        oy, tone = _flag_wave(sh, i, phase, flutter)
        for (_, j), c in _flag_column(sh, _flag_kind(sh, i), tone, night).items():
            cells[(x + i, y + j + oy)] = c
    for (q, c) in cells.items():
        p.px(q[0], q[1], c, L)
    return cells


def waving_flag(p: Pix, x, y, sh=2, night=False, frames=3, dur=1.2, motion=True):
    """The flag in the wind: the part by the pole holds its ripple while the free end flutters, a quicker
    wave running out along it in `frames` frames shown in turn round a loop `dur` seconds long. The free
    end is made of a few kinds of column, each drawn once and placed at its height in every frame. The
    still file keeps the first frame; a file that holds still draws the flag as it is at that moment."""
    h, w, _, _ = _flag_geometry(sh)
    i0 = round(w * FLUTTER_FROM)
    frame_layers = [p.seq(f"flg{f}", round(f / frames, 3), round((f + 1) / frames, 3), dur, keep=f == 0, z=0.2)
                    for f in range(frames)] if motion else ["base"]
    for f, L in enumerate(frame_layers):
        for i in range(w):
            if i < i0 and f:
                continue
            oy, tone = _flag_wave(sh, i, 0.0, f / frames)
            kind = _flag_kind(sh, i)
            if i < i0 or not motion:
                for (_, j), c in _flag_column(sh, kind, tone, night).items():
                    p.px(x + i, y + j + oy, c)
                continue
            key = ("flagcol", sh, kind, tone, night)       # a fluttering column: drawn once, placed in each frame
            if key not in p.syms:
                p.symbol(key, _flag_column(sh, kind, tone, night))
            p.use(key, x + i, y + oy, L)


def flagpole(p: Pix, x, top, base, night=False, L="base", light=True, flag_foot=None):
    """A flagpole standing on row `base`: a silver pole two pixels wide, lit on its left, a gold ball at
    its top and a halyard down its side to a cleat from the flag's foot at row `flag_foot`. By night a lamp
    stands at its foot, lighting the pole and, through the flag's own shading, the cloth above it."""
    W, Gd, K = RAMP["cloth"], RAMP["gold"], RAMP["coal"]
    for yy in range(top + 3, base):
        p.px(x, yy, W[5] if not night else W[4], L)
        p.px(x + 1, yy, W[3] if not night else W[2], L)
    p.hline(x - 1, x + 3, top + 3, W[4] if not night else W[3], L)            # the truck under the ball
    sphere(p, x + 1, top + 1.5, 1.6, Gd, lo=2, outline=False)
    if flag_foot is not None:
        for yy in range(flag_foot, base - 9):
            p.px(x + 2, yy, W[3] if not night else W[2], L)                   # the halyard, down to its cleat
        p.px(x + 2, base - 9, K[4], L)
        p.px(x + 3, base - 9, K[3], L)
    if night and light:
        for (dx, c) in ((3, K[4]), (4, K[3]), (5, K[2])):                      # the lamp, its lens toward the flag
            p.px(x + dx, base - 1, c, L)
        p.px(x + 3, base - 2, K[4], L)
        p.px(x + 4, base - 2, Gd[6], L)
        for yy in range(base - 12, base - 1):                                # its light on the foot of the pole
            p.px(x, yy, W[6], L)
            p.px(x + 1, yy, W[4], L)
        for (qx, qy), c in glow_cells(x + 4.5, base - 1.5, 3.0, 2.4, Gd[5], (0.25, 0.45), {(x + 4, base - 2)}).items():
            p.px(qx, qy, c, "pool")


# --------------------------------------------------------------------------- things that burn
def sparkler(p: Pix, x, base, h=12, night=False, L="base", phase=0, motion=True, lean=0):
    """A sparkler standing in the grass on row `base`: a grey wire, its upper part crusted where the
    powder is, burning at its tip. The tip is white-hot in a gold glow and throws short sparks, split
    across three layers that take turns, so in a moving file they crackle; its light falls on the
    grass and whatever stands near it."""
    W, Gd, E = RAMP["cloth"], RAMP["gold"], RAMP["ember"]
    wire = []
    for j in range(h):
        xx = x + round(lean * (h - j) / h)
        wire.append((xx, base - 1 - j))
    for i, (xx, yy) in enumerate(wire):
        crust = i > h * 0.4
        crusted = RAMP["bronze"][3] if not night else RAMP["bronze"][2]
        p.px(xx, yy, crusted if crust else (W[3] if not night else W[2]), L)
    tx, ty = wire[-1][0], wire[-1][1] - 1
    Lf = p.flicker(phase) if motion else L
    p.px(tx, ty, C["white"], Lf)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(tx + dx, ty + dy, Gd[6], Lf)
    rnd = random.Random(x * 7 + base)
    for s in range(3):
        Ls = p.twinkle(phase + s) if motion else L
        for _ in range(4):
            a = rnd.uniform(0, 2 * math.pi)
            r0, r1 = rnd.uniform(2.0, 3.0), rnd.uniform(3.5, 6.0)
            cells = {}
            _line(cells, tx + 0.5 + math.cos(a) * r0, ty + 0.5 + math.sin(a) * r0,
                  tx + 0.5 + math.cos(a) * r1, ty + 0.5 + math.sin(a) * r1)
            for n_, q in enumerate(sorted(cells, key=lambda q: math.hypot(q[0] - tx, q[1] - ty))):
                p.px(q[0], q[1], Gd[6] if n_ == 0 else (Gd[5] if n_ == 1 else E[5]), Ls)
            if not motion and _ % 2:
                break
    own = {(tx + dx, ty + dy) for dx in range(-7, 8) for dy in range(-7, 8)}
    for (qx, qy), c in glow_cells(tx + 0.5, ty + 0.5, 2.6, 2.6, Gd[5], (0.3, 0.5) if night else (0.12, 0.2),
                                  {(tx, ty)}).items():
        if (qx, qy) not in p.layers.get(Lf, {}):
            p.px(qx, qy, c, Lf)
    lamp(p, tx + 0.5, ty + 0.5, 9 if night else 6, phase, own | set(wire))


def fuse_spark(p: Pix, x, y, night=False, phase=0, motion=True, L=None):
    """The burning end of a fuse at (x, y): a white-hot point, gold sparks on three layers that take
    turns, and a glow; it lights what is near it."""
    Gd, E = RAMP["gold"], RAMP["ember"]
    Lf = L or (p.flicker(phase) if motion else "base")
    p.px(x, y, C["white"], Lf)
    for dx, dy, c in ((1, 0, Gd[5]), (-1, 0, E[4]), (0, -1, Gd[6]), (0, 1, E[4])):
        p.px(x + dx, y + dy, c, Lf)
    sparks = [[(2, -2), (3, -3), (-2, -2)], [(2, 1), (-3, -1), (1, -3)], [(3, 0), (-2, 1), (0, -3), (-1, -4)]]
    for s, pts in enumerate(sparks):
        Ls = p.twinkle(phase + s) if motion else Lf
        for (dx, dy) in pts:
            p.px(x + dx, y + dy, Gd[5] if abs(dx) + abs(dy) < 4 else E[5], Ls)
    own = {(x + dx, y + dy) for dx in range(-4, 5) for dy in range(-5, 3)}
    for (qx, qy), c in glow_cells(x + 0.5, y + 0.5, 2.6, 2.6, Gd[5], (0.3, 0.5) if night else (0.12, 0.2),
                                  {(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}).items():
        if (qx, qy) not in p.layers.get(Lf, {}):
            p.px(qx, qy, c, Lf)
    lamp(p, x + 0.5, y + 0.5, 7 if night else 5, phase, own)


def rocket(p: Pix, x, base, night=False, colour="red", L="base", stick=True, lit=False):
    """A skyrocket standing on its guide stick, 5 wide, its foot on row `base`: a paper tube in the
    set's colour with a white band, shaded round from the left, a blue nose cone lit on its left face,
    and a fuse at its foot. It stands about 17 pixels tall with its stick."""
    R = RAMP[{"red": "red", "blue": "navy", "white": "cloth"}[colour]]
    N, W, Wd = RAMP["navy"], RAMP["cloth"], RAMP["wood"]
    k = -1 if night else 0
    body_top = base - (17 if stick else 11)
    for j in range(8):
        yy = body_top + 4 + j
        band = j in (2, 3)
        for i in range(5):
            t = (5, 4, 3, 3, 2)[i]
            c = W[max(2, t + 1 + k)] if band else R[max(1, min(6, t - 1 + k))]
            p.px(x + i, yy, c, L)
    for j, row in enumerate(["..a..", ".abc.", "abccd", "abccd"]):
        for i, ch in enumerate(row):
            if ch != ".":
                p.px(x + i, body_top + j, N[{"a": 5, "b": 4, "c": 3, "d": 2}[ch] + k], L)
    for (dx, dy, t) in ((-1, 9, 4), (-1, 10, 3), (-1, 11, 3), (5, 9, 3), (5, 10, 2), (5, 11, 2)):   # the fins
        p.px(x + dx, body_top + dy + 1, N[max(1, t + k)], L)
    if stick:
        for yy in range(body_top + 12, base):
            p.px(x + 4, yy, Wd[4 + k], L)
            p.px(x + 5, yy, Wd[2 + k], L)
    p.px(x + 2, body_top + 12, RAMP["coal"][3], L)
    p.px(x + 2, body_top + 13, RAMP["coal"][2], L)
    if lit:
        fuse_spark(p, x + 2, body_top + 14, night)


def firecracker(p: Pix, x, base, night=False, L="base", h=9):
    """A firecracker standing on row `base`, 4 wide: a red paper tube shaded round from the left, a white
    band round its middle with a blue star on it, a pale cap and a black fuse curling from the top."""
    R, W, N, K = RAMP["red"], RAMP["cloth"], RAMP["navy"], RAMP["coal"]
    k = -1 if night else 0
    top = base - h
    for j in range(h):
        yy = top + j
        band = h // 2 - 1 <= j <= h // 2 + 1
        for i in range(4):
            t = (4, 3, 3, 2)[i]
            c = W[max(2, t + 2 + k)] if band else R[max(1, t + k)]
            if j == h - 1:
                c = step(c, -1)
            p.px(x + i, yy, c, L)
    p.px(x + 1, top + h // 2, N[4 + k], L)
    p.px(x + 2, top + h // 2, N[3 + k], L)
    for i in range(4):
        p.px(x + i, top, W[5 + k] if i < 2 else W[4 + k], L)
    for (dx, dy) in ((2, -1), (2, -2), (3, -3), (4, -3)):
        p.px(x + dx, top + dy, K[3] if not night else K[5], L)


# --------------------------------------------------------------------------- the Liberty Bell
def liberty_bell(p: Pix, x, y, night=False, L="base", w=15):
    """The Liberty Bell, `w` wide, top-left at (x, y), about w + 2 tall. A dark bronze bell: a rounded
    crown, a waist that swells to a heavy lip, raised rings at the shoulder and above the lip with the
    band of lettering between them, shaded round from the left with a sheen down its lit side and light
    thrown back on its far edge. Its mouth shows dark under the lip, and its famous crack climbs from the
    lip, widened where it was drilled. It hangs from its wooden yoke, a beam with iron straps."""
    B, Wd, K = RAMP["bronze"], RAMP["wood"], RAMP["coal"]
    k = -1 if night else 0
    cx = x + w / 2
    top = y + 4
    h = w - 2

    def half(t):
        if t < 0.1:
            return w * (0.2 + 0.07 * math.sqrt(t / 0.1))
        if t < 0.72:
            return w * (0.27 + 0.05 * ((t - 0.1) / 0.62) ** 1.6)
        return w * (0.32 + 0.18 * ((t - 0.72) / 0.28) ** 1.7)

    cells = {}
    for j in range(h):
        t = j / (h - 1)
        hw = half(t)
        for xx in range(math.floor(cx - hw), math.ceil(cx + hw)):
            u = (xx + 0.5 - cx) / hw
            if abs(u) > 1:
                continue
            nz = math.sqrt(max(0.0, 1 - u * u))
            lam = max(0.0, u * LX + nz * LZ)
            v = 1.3 + 3.3 * lam
            if -0.64 < u < -0.38 and 0.12 < t < 0.9:
                v += 1.0                                     # the sheen down the lit side
            if u > 0.8:
                v += 0.7                                     # light thrown back on the far edge
            cells[(xx, top + j)] = v
    ring = {round(0.16 * (h - 1)): 1, round(0.2 * (h - 1)) + 1: -1,
            round(0.76 * (h - 1)): 1, round(0.76 * (h - 1)) + 1: -1}
    letters = range(round(0.2 * (h - 1)) + 2, round(0.2 * (h - 1)) + 4)
    for (xx, yy), v in cells.items():
        j = yy - top
        v += ring.get(j, 0) * 0.9
        if j in letters and (xx + j) % 2 == 0 and abs(xx + 0.5 - cx) < half(j / (h - 1)) - 1:
            v -= 1.1                                         # the lettering cast round the shoulder
        if j == h - 1:
            v -= 1.2
        c = B[max(1, min(6, round(v + k)))]
        p.px(xx, yy, c, L)
    lip = top + h
    hw = half(1.0)
    for xx in range(math.floor(cx - hw) + 1, math.ceil(cx + hw) - 1):
        p.px(xx, lip, K[1] if abs(xx + 0.5 - cx) < hw - 2 else B[1 + max(0, k + 1)], L)   # the mouth, dark
    # the crack, climbing from the lip a little right of the middle, widened where it was drilled
    for j, (dx, wide) in enumerate(((0.14, 0), (0.13, 0), (0.11, 1), (0.11, 1), (0.1, 1), (0.08, 0), (0.07, 0),
                                    (0.08, 0), (0.06, 0))):
        if j >= h * 0.7:
            break
        cxk = round(cx + dx * w)
        p.px(cxk, top + h - 1 - j, K[1], L)
        if wide:
            p.px(cxk + 1, top + h - 1 - j, K[2], L)
    # the yoke: a beam across the top, chamfered at its ends, and iron straps down to the crown
    for xx in range(x + 1, x + w - 1):
        u = (xx - x) / w
        p.px(xx, y, Wd[5 + k] if u < 0.45 else Wd[4 + k], L)
        p.px(xx, y + 1, Wd[4 + k] if u < 0.45 else Wd[3 + k], L)
        p.px(xx, y + 2, Wd[2 + k], L)
    p.px(x, y + 1, Wd[4 + k], L)
    p.px(x + w - 1, y + 1, Wd[2 + k], L)
    for sx in (round(cx) - 3, round(cx) + 2):
        for yy in range(y + 1, top + 1):
            p.px(sx, yy, K[4] if sx < cx else K[3], L)
    return cells


# --------------------------------------------------------------------------- hats and things for a picnic
def top_hat(p: Pix, x, y, w=13, h=13, night=False, L="base"):
    """Uncle Sam's hat, `w` by `h`, top-left at (x, y): a tall crown striped red and white, shaded round
    from the left, a blue band set with white stars, and a wide blue brim, lit on its top and dark
    beneath. The crown flares a little toward its top, as his does."""
    R, W, N = RAMP["red"], RAMP["cloth"], RAMP["navy"]
    k = -1 if night else 0
    brim = y + h - 2
    crown_h = h - 2
    c0 = x + w / 2
    for j in range(crown_h):
        yy = y + j
        half = 3.2 + 0.5 * (1 - j / max(1, crown_h - 1))
        band = j >= crown_h - 3
        for xx in range(math.floor(c0 - half), math.ceil(c0 + half)):
            u = (xx + 0.5 - c0) / half
            if abs(u) > 1.02:
                continue
            nz = math.sqrt(max(0.0, 1 - min(1.0, u * u)))
            lam = max(0.0, u * LX + nz * LZ)
            t = 2 + round(2.2 * lam)
            if j == 0:
                t += 1
            if band:
                c = N[max(1, min(6, t + k))]
                if (xx + j) % 3 == 0 and j == crown_h - 2 and abs(u) < 0.85:
                    c = W[6]
            else:
                stripe = int((u + 1) * 3.4) % 2 == 0
                c = W[max(2, min(6, t + 2 + k))] if stripe else R[max(1, min(6, t + 1 + k))]
            p.px(xx, yy, c, L)
    for xx in range(x, x + w):
        u = (xx + 0.5 - x) / w
        edge = xx in (x, x + w - 1)
        p.px(xx, brim, N[(5 if u < 0.3 else 4 if u < 0.7 else 3) + k] if not edge else N[3 + k], L)
        if not edge:
            p.px(xx, brim + 1, N[1 + k] if k == 0 else N[0], L)


def watermelon(p: Pix, x, base, night=False, L="base", w=13):
    """A slice of watermelon lying on its rind, `w` wide, its foot on row `base`: the cut face up, red
    flesh lit toward the top with black seeds in a ring, a pale rind and a dark green skin round its curve."""
    R, G, W, K = RAMP["red"], RAMP["green"], RAMP["cloth"], RAMP["coal"]
    k = -1 if night else 0
    r = w / 2
    cx = x + r
    rows = math.ceil(r * 0.8)
    top = base - rows
    for yy in range(top, base):
        for xx in range(x, x + w):
            dx, dy = xx + 0.5 - cx, (yy + 0.5 - top) / 0.8
            rho = math.hypot(dx, dy)
            if rho > r:
                continue
            if rho > r - 1.1:
                c = G[3 + k] if dx < 0 else G[2 + k]
            elif rho > r - 2.1:
                c = W[5 + k] if dx < 0 else W[4 + k]
            else:
                t = 4 if yy == top else 3
                if dx < -r * 0.25 and yy < top + 2:
                    t += 1
                c = R[max(2, min(6, t + k))]
            p.px(xx, yy, c, L)
    for (u, v) in ((-0.42, 0.28), (-0.1, 0.52), (0.26, 0.4), (0.5, 0.12)):
        p.px(math.floor(cx + u * r), math.floor(top + v * r * 0.8), K[1], L)


def basket(p: Pix, x, base, night=False, L="base", w=15):
    """A picnic basket on row `base`, `w` wide: woven wicker in rows of light and shade, a lid in two
    halves, a bent handle over the top, and a red-and-white cloth peeking out at one side."""
    Wd, R, W = RAMP["wood"], RAMP["red"], RAMP["cloth"]
    k = -1 if night else 0
    h = 8
    top = base - h
    for j in range(h):
        for i in range(w):
            weave = ((i // 2) + j) % 2 == 0
            t = 4 if weave else 3
            if i == 0:
                t += 1
            if i >= w - 2:
                t -= 1
            if j == h - 1:
                t -= 1
            p.px(x + i, top + j, Wd[max(1, min(6, t + k))], L)
    for i in range(-1, w + 1):
        p.px(x + i, top - 1, Wd[5 + k] if i < w // 2 else Wd[4 + k], L)
        p.px(x + i, top, Wd[2 + k], L)
    for (dx, dy) in ((3, -2), (3, -3), (4, -4), (5, -5), (6, -5), (7, -5), (8, -5), (9, -5), (10, -4), (11, -3),
                     (11, -2)):
        p.px(x + dx, top + dy, Wd[3 + k] if dx < 8 else Wd[2 + k], L)
    for (dx, dy, red) in ((-2, 1, True), (-1, 1, False), (-2, 2, False), (-1, 2, True), (-2, 3, True)):
        p.px(x + dx, top + dy, (R[4 + k] if red else W[5 + k]), L)


def blanket(p: Pix, x0, x1, base, night=False, L="base", rows=3):
    """A picnic blanket spread on the grass along row `base`: red-and-white gingham, the checks where a
    red thread crosses a red one darker, its front edge folded under and in shade."""
    R, W = RAMP["red"], RAMP["cloth"]
    k = -1 if night else 0
    for j in range(rows):
        yy = base - rows + j
        for xx in range(x0 + (rows - 1 - j), x1 - (rows - 1 - j) // 2):
            a, b = (xx // 2) % 2 == 0, j % 2 == 0
            if a and b:
                c = R[3 + k]
            elif a or b:
                c = R[5 + k]
            else:
                c = W[5 + k]
            if j == rows - 1:
                c = step(c, -1)
            p.px(xx, yy, c, L)


POP = ["..rr..", ".rRRr.", ".rRRr.", ".rRRq.", ".wWWv.", ".wWWv.", ".wWWv.", ".bBBc.", ".bBBc.", ".bBBc.",
       "..ss..", "..ss..", "..ss.."]


def rocket_pop(p: Pix, x, y, night=False, L="base"):
    """An ice pop in three flavours, 6 by 13, top-left at (x, y): red, white and blue from the top down,
    each lit on its left, on a wooden stick."""
    R, W, N, Wd = RAMP["red"], RAMP["cloth"], RAMP["navy"], RAMP["wood"]
    k = -1 if night else 0
    pal = {"r": R[4 + k], "R": R[3 + k], "q": R[2 + k], "w": W[6 + k], "W": W[5 + k], "v": W[3 + k],
           "b": N[5 + k], "B": N[4 + k], "c": N[3 + k], "s": Wd[5 + k]}
    p.sprite(x, y, POP, pal, 1, L)
    p.px(x + 2, y + 1, R[6 + k], L)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["red"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)
