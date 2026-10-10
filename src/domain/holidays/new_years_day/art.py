# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The New Year's Day set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the frame, the scenery a header stands on,
and every sprite, each shaded from the one light in the upper left on the set's own ramps.

The year is never written in. Whatever shows it is handed the year it celebrates, as its figures: the
balloons take the largest face their room allows, and the frame of lamps on the tower's roof widens to fit."""
from __future__ import annotations

import math
import random

from ..pixel import FONTS, LX, LY, LZ, Paint, Pix, fold, num, sphere
from .palette import C, CONFETTI, GROUND, NIGHT_SKY, RAMP, X, step


def foil_fill(r, c, scale, night):
    """The colour a title's letter takes at row `r` and column `c` of the letter, counted in pixels from
    its top-left: gold foil, a band for each row of the face, bright at the crown, darkening, then a
    bright line where the foil catches the light across its middle, and darker again to the foot, the way
    polished metal reflects a room. By night every band is a tone lighter, so each keeps 4.5:1 against the
    midnight sky."""
    G = RAMP["gold"]
    band = min(6, r // scale)
    if night:
        return (G[6], G[5], G[4], G[6], G[5], G[4], G[3])[band]
    return (G[5], G[4], G[3], G[5], G[4], G[3], G[2])[band]


# The titles' gold foil, a band for each row of the face.
FOIL = Paint("foil", foil_fill)


def edged(p: Pix, x, y, s, scale, shadow, edge, L="base"):
    """What lies under a title's foil by day, as `Pix.text` would set it: a shadow half a font pixel
    down-right, and a dark edge a pixel round every letter. Each letter's edge, its four copies a pixel
    off, is drawn once as a symbol and placed once a letter, so a long title stays light."""
    glyphs, _, space = FONTS["57"]
    off = max(1, scale // 2)
    cx = x
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(g[1]) for col in cols}, mono=True)
        ring = ("edge", ch, scale)
        if ring not in p.syms:
            sid = p.syms[key]
            p.symbol(ring, shapes="".join(f'<use href="#{sid}" transform="translate({dx} {dy}) scale({scale})"/>'
                                          for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))))
        p.use(key, cx + off, y + off, L, stroke=shadow, scale=scale)
        p.use(ring, cx, y, L, stroke=edge)
        cx += (g[0] + 1) * scale


def glints(p: Pix, x, y, s, scale):
    """Here and there a glint where a title's foil catches the light: on every third letter whose top row
    has ink, at its top-left, twinkling in a moving file."""
    glyphs, _, space = FONTS["57"]
    cx, n = x, 0
    for i, ch in enumerate(fold(s, "57")):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        if i % 3 == 1 and g[1][0]:
            sparkle(p, cx + min(g[1][0]) * scale + 1, y + 1, L=p.twinkle(n))
            n += 1
        cx += (g[0] + 1) * scale


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: soft white paper with a dot grid by day, by night the midnight sky,
    lighter toward the horizon in five bands where the city's lights reach it."""
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
    """A winter night's stars at three magnitudes: faint pinpricks, bright points, and a few glints.
    None is set inside a box in `avoid` (x0, y0, x1, y1), so no glint sits in a letter or beside a word."""
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


def marquee_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="mq"):
    """The sheet's border: a marquee three pixels wide, a dark panel between two gold edges with a bulb
    lit every four pixels, the way a theatre's sign is framed; inside it a rule. Each side is one pattern
    tile placed along it, so the border costs a few hundred bytes."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    G, M, Ch = RAMP["gold"], RAMP["midnight"], RAMP["champagne"]
    k = -1 if night else 0

    def tile(horizontal):
        cells = {}
        for a in range(4):
            for b in range(3):
                if b == 0:
                    c = G[5 + k] if a == 1 else G[4 + k]
                elif b == 2:
                    c = G[3 + k]
                else:
                    c = Ch[6] if a == 0 else (G[5] if a in (1, 3) else M[2])
                cells[(a, b) if horizontal else (b, a)] = c
        return cells

    for name, horizontal in (("h", True), ("v", False)):
        cells = tile(horizontal)
        tw, th = (4, 3) if horizontal else (3, 4)
        p.defs.append(f'<pattern id="{uid}{name}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
                      f'{p._paths(cells)}</pattern>')
    p.defs.append(f'<rect id="{uid}H" width="{w}" height="3" fill="url(#{uid}h)"/>')
    p.defs.append(f'<rect id="{uid}V" width="3" height="{h - 6}" fill="url(#{uid}v)"/>')
    for (name, bx, by) in (("H", x, y), ("H", x, y + h - 3), ("V", x, y + 3), ("V", x + w - 3, y + 3)):
        p.shapes["base"].append(f'<use href="#{uid}{name}" x="{bx}" y="{by}"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, G[4] if night else M[3])


def marquee_chase(p: Pix, x=0, y=0, w=None, h=None):
    """By night, in a moving file, a few of the marquee's bulbs along its top and its foot flare in turn."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    i = 0
    for bx in range(x + 8, x + w - 4, 12):
        for by in (y + 1, y + h - 2):
            if (bx - x) % 4 == 0:
                L = p.twinkle(i)
                p.px(bx, by, C["white"], L)
                i += 1


# --------------------------------------------------------------------------- streamers and confetti
def confetti_colour(fam, night, lit=True):
    """A piece of confetti's colour in the family `fam`: its lit face or its turned face."""
    R = RAMP[fam]
    t = (5 if lit else 3) if fam != "silver" else (6 if lit else 4)
    return R[t - (1 if night and fam != "gold" else 0)]


def _streamer_span(sp, sag, night, variant):
    """One span of the streamers, tack to tack, as pixels: two crêpe streamers twisted round each other
    and sagging `sag` rows at the middle, and hanging from them a foil star on its thread and a curl of
    ribbon."""
    a_fam, b_fam = (("gold", "rose"), ("silver", "teal"))[variant % 2]
    A, B = RAMP[a_fam], RAMP[b_fam]
    k = -1 if night else 0
    oy = 2
    q = Pix(sp + 2, sag + 16)
    pts = [(xx, oy + round(sag * 4 * (xx / sp) * (1 - xx / sp))) for xx in range(sp)]
    for (xx, yy) in pts:
        twist = (xx // 3) % 2
        top, bot = (A, B) if twist == 0 else (B, A)
        crossing = xx % 3 == 0
        q.px(xx, yy, (top[5 + k] if not crossing else top[4 + k]))
        q.px(xx, yy + 1, (bot[4 + k] if not crossing else bot[3 + k]))
    for (a_, b_) in zip(pts, pts[1:]):
        if abs(a_[1] - b_[1]) > 1:
            for yy in range(min(a_[1], b_[1]) + 1, max(a_[1], b_[1]) + 1):
                q.px(a_[0], yy, A[4 + k])
    sx = round(sp * 0.36)                                    # a foil star on its thread
    sy = pts[sx][1] + 2
    G = RAMP["gold" if variant % 2 == 0 else "silver"]
    for j in range(2):
        q.px(sx, sy + j, RAMP["silver"][3 + k])
    for (dx, dy, t) in ((0, 2, 6), (-1, 3, 5), (0, 3, 6), (1, 3, 4), (-2, 4, 5), (-1, 4, 5), (0, 4, 5), (1, 4, 4),
                        (2, 4, 3), (-1, 5, 4), (0, 5, 4), (1, 5, 3), (-1, 6, 4), (1, 6, 3)):
        q.px(sx + dx, sy + dy, G[t + k] if not (G is RAMP["silver"]) else G[min(6, t + 1) + k])
    cx_ = round(sp * 0.7)                                    # a curl of ribbon
    cy_ = pts[cx_][1] + 2
    R = RAMP["teal" if variant % 2 == 0 else "rose"]
    for j in range(6):
        q.px(cx_ + (j % 2), cy_ + j, R[(5 if j % 2 == 0 else 3) + k])
    return {(x, y - oy): c for (x, y), c in q.layers["base"].items()}


def streamers(p: Pix, x0, x1, y, span=45, sag=5, night=False):
    """Streamers along the top: two crêpe streamers twisted together, swagged from tack to tack, gold
    with rose and silver with teal by turns, a foil star and a curl of ribbon hanging from each swag and a
    rosette of foil at every tack. Each swag is drawn once and hung again and again; the last is cut to
    fit."""
    xs = list(range(x0, x1, span))
    for i, xa in enumerate(xs):
        sp = min(span, x1 - xa)
        if sp < 8:
            continue
        key = ("streamer", sp, sag, night, i % 2)
        if key not in p.syms:
            p.symbol(key, _streamer_span(sp, sag, night, i % 2))
        p.use(key, xa, y)
    G = RAMP["gold"]
    k = -1 if night else 0
    for xa in xs + [x1]:
        key = ("rosette", night)
        if key not in p.syms:
            cells = {}
            for (dx, dy, t) in ((0, -1, 5), (-1, 0, 5), (0, 0, 6), (1, 0, 4), (0, 1, 3), (-1, -1, 4), (1, 1, 3),
                                (1, -1, 4), (-1, 1, 4)):
                cells[(dx, dy)] = G[t + k]
            p.symbol(key, cells)
        p.use(key, min(xa, x1 - 2), y)


def confetti_on(p: Pix, x0, x1, y, seed=7, L="base", night=False, gap=(3, 9)):
    """Confetti lying along a ledge whose top edge is row `y`: little squares and strips of gold, rose,
    teal, silver and violet, some face up and some turned, now and then a curl of streamer. None lies
    where it would touch a word."""
    rnd = random.Random(seed * 131 + x0)
    x = x0 + rnd.randint(1, 4)
    while x < x1 - 2:
        fam = rnd.choice(CONFETTI)
        if not p.clear_of_words(x, y - 3, x + 3, y):
            x += rnd.randint(*gap)
            continue
        r = rnd.random()
        if r < 0.1:                                          # a curl of streamer
            for j, (dx, dy) in enumerate(((0, -1), (1, -2), (2, -1), (3, -2))):
                p.px(x + dx, y + dy, confetti_colour(fam, night, j % 2 == 0), L)
            x += 4
        elif r < 0.45:                                       # a strip lying flat
            p.px(x, y - 1, confetti_colour(fam, night, True), L)
            p.px(x + 1, y - 1, confetti_colour(fam, night, False), L)
            x += 2
        else:                                                # a square, face up or turned
            p.px(x, y - 1, confetti_colour(fam, night, rnd.random() < 0.6), L)
            x += 1
        x += rnd.randint(*gap)


# --------------------------------------------------------------------------- the snow and the city
def snow(p: Pix, x0, x1, y_top, y_bot, seed=5, night=False, L="base", confetti=True):
    """Snow along the foot of a drawing: a soft rolling crest, bright where it faces the light and blue
    in its hollows, confetti fallen on it. By night it is blue with the city's light along its crest."""
    S, M = RAMP["silver"], RAMP["midnight"]
    rnd = random.Random(seed)
    h = rnd.randint(2, 3)
    prev = h
    tops = {}
    for x in range(x0, x1):
        h = max(1, min(y_bot - y_top, h + rnd.choice((-1, 0, 0, 0, 1))))
        top = y_bot - h
        tops[x] = top
        for yy in range(top, y_bot):
            if night:
                c = M[6] if yy == top else (M[5] if yy < y_bot - 1 else M[4])
            else:
                c = S[6] if yy == top else (S[5] if yy < y_bot - 1 else S[4])
            if yy == top and h < prev:
                c = step(c, -1)
            p.px(x, yy, c, L)
        prev = h
    if confetti:
        for x in range(x0 + 1, x1 - 1):
            if rnd.random() < 0.14:
                fam = rnd.choice(CONFETTI)
                p.px(x, tops[x], confetti_colour(fam, night, rnd.random() < 0.6), L)
    return tops


def _building_face(night, edge_l, edge_r, sun_side, S, M, Ch, D):
    """A building's wall colour at one column: by night dark with a lighter edge; by day pale in the haze,
    lit on its left, shaded on its right, and warmed by the sunrise on the side that faces it."""
    if night:
        return M[2] if edge_l else M[1]
    if sun_side == "r" and edge_r or sun_side == "l" and edge_l:
        return D[6]
    return S[5] if edge_l else (S[3] if edge_r else S[4])


def landmark(p: Pix, x, base, kind, night=False, L="base", sun_side=None, seed=0, h=30):
    """One of the city's landmark towers, its left edge at `x` and its foot on row `base`: "deco", an art
    deco tower that steps back three times to a mast, or "crown", a tower crowned with stacked arches that
    narrow to a needle, triangular windows in each arch. By night each is floodlit gold at its top."""
    S, M, G, Ch, D = RAMP["silver"], RAMP["midnight"], RAMP["gold"], RAMP["champagne"], RAMP["dawn"]
    rnd = random.Random(seed)
    if kind == "deco":
        tiers = [(11, h), (7, 5), (5, 4), (3, 3)]               # widths and heights, from the foot up
    else:
        tiers = [(9, h)]
    y = base
    cx = x + tiers[0][0] // 2
    for n, (w_, h_) in enumerate(tiers):
        left = cx - w_ // 2
        for xx in range(left, left + w_):
            for yy in range(y - h_, y):
                c = _building_face(night, xx == left, xx == left + w_ - 1, sun_side, S, M, Ch, D)
                if n > 0 and night:
                    c = G[4] if xx < cx else G[3]              # floodlit
                p.px(xx, yy, c, L)
        if n == 0:
            for yy in range(y - h_ + 2, y - 2, 2):
                for xx in range(left + 2, left + w_ - 1, 2):
                    if night:
                        p.px(xx, yy, rnd.choice((G[5], Ch[5], M[2], M[2], M[2])), L)
                    else:
                        p.px(xx, yy, S[6] if rnd.random() < 0.55 else S[5], L)
        y -= h_
    if kind == "deco":
        for j in range(1, 10):
            p.px(cx, y - j, (M[3] if night else S[3]), L)
        if night:
            p.px(cx, y - 10, RAMP["rose"][4], p.blink(seed))
        return
    # the crown: arches in tiers, narrowing, a triangular window in each, then the needle
    for n, (w_, h_) in enumerate(((9, 3), (7, 3), (5, 3), (3, 2))):
        left = cx - w_ // 2
        for xx in range(left, left + w_):
            for yy in range(y - h_, y):
                arch_top = y - h_ + (0 if (xx - left) % 2 == 1 else 1)
                if yy < arch_top:
                    continue
                c = (G[4] if xx < cx else G[3]) if night else (S[6] if xx < cx else S[4])
                p.px(xx, yy, c, L)
        for xx in range(left + 1, left + w_ - 1, 2):
            p.px(xx, y - 1, (Ch[6] if night else S[2]), L)       # the triangular windows
        y -= h_
    for j in range(1, 7):
        p.px(cx, y - j, (G[5] if night else S[4]), L)


# How far above its roof what stands on a building reaches: a spire, a mast and its light, a water tower.
ROOF_REACH = {"spire": 5, "mast": 7, "water": 4}


def skyline(p: Pix, x0, x1, base, night=False, seed=3, lo=10, hi=30, L="base", lit=0.35, taper=(True, True),
            sun_x=None, landmarks=(), clear=None):
    """A city's skyline far off, its buildings' feet on row `base` between x0 and x1: towers of different
    widths and heights, flat-roofed, stepped back, with a spire or a mast or a water tower on the roof, and
    their windows in rows, with its `landmarks` (x, kind, height) among them. By day, seen through the morning's
    haze, they are pale and cool, their windows catching the light, and where `sun_x` is given each is
    warmed by the sunrise on the side that faces it. By night they are dark shapes against the sky with a
    share `lit` of their windows lit, a red light blinking on each mast. `taper` lowers the line toward
    either end. `clear(x0, y0, x1, y1)`, when given, says whether a box is free of words: a building that
    would reach one loses what stands on its roof and is cut down until it clears it, its windows keeping
    their places, so the rest of the line stands as it would."""
    S, M, G, Ch, R, D = (RAMP[n] for n in ("silver", "midnight", "gold", "champagne", "rose", "dawn"))
    rnd = random.Random(seed)
    x = x0
    i = 0
    while x < x1:
        bw = rnd.randint(6, 12)
        f0 = (x - x0) / max(1, x1 - x0)
        bh = rnd.randint(lo, hi)
        if taper[0]:
            bh = round(bh * min(1.0, 0.5 + f0 * 3))
        if taper[1]:
            bh = round(bh * min(1.0, 0.5 + (1 - f0) * 3))
        bh = max(6, bh)
        right = min(x + bw, x1)
        roof = rnd.choice(("flat", "water", "step", "spire", "mast"))
        top = base - bh
        low = top                                               # the row it is drawn from
        if clear is not None and not clear(x, top - ROOF_REACH.get(roof, 0), right, base):
            low = top + 1
            while low < base - 6 and not clear(x, low, right, base):
                low += 1
        sun_side = None if sun_x is None else ("r" if (x + right) / 2 < sun_x else "l")
        for xx in range(x, right):
            edge_l, edge_r = xx == x, xx == right - 1
            ty = top
            if roof == "step" and (xx - x < 2 or right - 1 - xx < 2):
                ty = top + 3
            for yy in range(max(ty, low), base):
                p.px(xx, yy, _building_face(night, edge_l, edge_r, sun_side, S, M, Ch, D), L)
        # windows: a grid of single pixels, a column in from each side and a row down from the roof
        for yy in range(top + 2, base - 2, 2):
            for xx in range(x + 2, right - 1, 2):
                if roof == "step" and (xx - x < 2 or right - 1 - xx < 2) and yy < top + 4:
                    continue
                shown = yy >= low + 2
                if night:
                    r_ = rnd.random()
                    if r_ < lit:
                        c = rnd.choice((G[5], Ch[5]))
                        if shown:
                            Lw = p.blink(i + xx) if (r_ < lit * 0.08 and "tw" not in L) else L
                            p.px(xx, yy, c, Lw)
                    elif shown:
                        p.px(xx, yy, M[2], L)
                else:
                    c = S[6] if rnd.random() < 0.55 else S[5]
                    if shown:
                        p.px(xx, yy, c, L)
        cx = (x + right - 1) // 2
        on_roof = roof if low == top else None                  # a building cut down keeps nothing on its roof
        if on_roof == "spire":
            for j in range(1, 6):
                w_ = 1 if j > 2 else 3
                for dx in range(-(w_ // 2), w_ // 2 + 1):
                    p.px(cx + dx, top - j, (M[2] if night else S[4]), L)
        elif on_roof == "mast":
            for j in range(1, 7):
                p.px(cx, top - j, (M[3] if night else S[3]), L)
            if night:
                p.px(cx, top - 7, R[4], p.blink(i))
        elif on_roof == "water" and right - x >= 7:               # a water tower on its legs
            wx = x + 2
            for (dx, dy, t) in ((0, -1, 1), (3, -1, 1), (0, -2, 2), (1, -2, 3), (2, -2, 3), (3, -2, 2), (0, -3, 3),
                                (1, -3, 4), (2, -3, 3), (3, -3, 2), (1, -4, 3), (2, -4, 2)):
                p.px(wx + dx, top + dy, (M[t // 2 + 1] if night else Ch[t]), L)
        x = right + (1 if rnd.random() < 0.25 else 0)
        i += 1
    for (lx, kind, lh) in landmarks:
        landmark(p, lx, base, kind, night, L, None if sun_x is None else ("r" if lx < sun_x else "l"), seed=lx, h=lh)


def clouds(p: Pix, streaks, night=False, L="haze"):
    """Thin clouds lying across the morning sky: each (x, y, length), a long streak with a shorter one
    under it, pale and lit peach along its underside by the sun below the horizon."""
    if night:
        return
    D, Ch = RAMP["dawn"], RAMP["champagne"]
    for (x, y, n) in streaks:
        for i in range(n):
            p.px(x + i, y, Ch[6] if i % 7 else D[6], L)
            if 2 <= i < n - 3:
                p.px(x + i + 1, y + 1, D[5] if i % 5 else D[6], L)


def sunrise(p: Pix, cx, horizon, r, L="base"):
    """The first sunrise of the year, for the morning files: the sun half risen at `horizon`, a pale gold
    disc warming to peach at its rim, a haze of its light stepping out into the sky round it and along the
    horizon, and a few long rays. Whatever stands in front of it is drawn after it."""
    D, G = RAMP["dawn"], RAMP["gold"]
    p.halo(cx, horizon, r * 5.0, r * 1.6, D[5], (0.05, 0.09, 0.13))
    p.halo(cx, horizon - r * 0.3, r * 2.4, r * 2.4, G[5], (0.05, 0.09, 0.14))
    for y in range(math.floor(horizon - r) - 1, horizon):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - horizon) / r
            if d <= 1:
                c = G[6] if d < 0.55 else (D[6] if d < 0.85 else D[5])
                p.px(x, y, c, L)
    for a in (-2.4, -2.0, -1.57, -1.14, -0.74):             # long rays, fading as they go
        for j in range(int(r * 1.4), int(r * 2.6)):
            x, y = cx + math.cos(a) * j, horizon + math.sin(a) * j
            p.apx(math.floor(x), math.floor(y), D[5], 0.35 if j < r * 2 else 0.18, "haze")


# --------------------------------------------------------------------------- fireworks at midnight
BURST_TIERS = 3   # 0 a star's white-hot head, 1 the bright part of its trail, 2 the trail as it cools
DROP = {"peony": 0.12, "willow": 0.4, "ring": 0.08}   # how far each kind's stars sink, for its size


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
    drop = DROP[kind] * r
    a0 = rnd.uniform(0, 2 * math.pi / n)
    stars_ = []
    for j in range(n):
        a = a0 + j * 2 * math.pi / n + rnd.uniform(-0.07, 0.07)
        stars_.append((math.cos(a), math.sin(a), r * rnd.uniform(0.9, 1.04)))

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


# The colours a burst takes by night: each star's head, the bright part of its trail and the trail as it
# cools into the sky. Fireworks are for midnight: no day file has one.
BURST_COLOURS = {
    "gold": (RAMP["gold"][6], RAMP["gold"][5], RAMP["gold"][3]),
    "silver": (C["white"], RAMP["silver"][5], RAMP["silver"][3]),
    "rose": (RAMP["rose"][6], RAMP["rose"][5], RAMP["rose"][3]),
    "teal": (RAMP["teal"][6], RAMP["teal"][5], RAMP["teal"][3]),
    "violet": (RAMP["violet"][6], RAMP["violet"][5], RAMP["violet"][3]),
}
FRAMES = [("trail1", 0.0, 0.06), ("trail2", 0.06, 0.12), ("open", 0.12, 0.17), ("bloom", 0.17, 0.34),
          ("fall", 0.34, 0.45), ("fade", 0.45, 0.54)]
SHOW_SPAN = 1 - FRAMES[-1][2]      # how far round the loop the last firework of a show may start


def firework(p: Pix, cx, cy, r, colour="gold", kind="peony", motion=True, offset=0.0, dur=5.4, seed=0, name=None,
             glow=True, light=0, rise=None, keep="bloom"):
    """A firework bursting at (cx, cy), `r` pixels across its sparks, by night. In a moving file it rises
    as a trail of sparks, breaks with a flash, blooms, sinks with glitter crackling among its stars and
    goes out in embers, each frame shown for its moment of a loop `dur` seconds long starting at `offset`
    of the way round, so several can take turns. The still file keeps the frame `keep`. `light` (a radius)
    washes its colour over whatever stands below it while it blooms. `rise` shortens the trail where words
    lie below, so it never passes behind them."""
    cols = BURST_COLOURS[colour]
    name = name or f"fw{len([k for k in p.layers if k.startswith('fw')])}"
    frames = FRAMES if motion else [f for f in FRAMES if f[0] == keep]
    for fname, t0, t1 in frames:
        if motion:
            L = p.seq(f"{name}{fname[0]}{fname[-1]}", round(offset + t0, 3), round(offset + t1, 3), dur,
                      keep=fname == keep)
        else:
            L = p.layer("fw", z=-12)
        key = _burst_symbols(p, kind, r, fname, seed, rise)
        if glow and fname == "open":
            p.shapes[L].append(f'<ellipse cx="{num(cx + 0.5)}" cy="{num(cy + 0.5)}" rx="3.5" ry="3.5" '
                               f'fill="{cols[1]}" fill-opacity=".3"/>')
        for t, sid in p.syms[key]:
            p.uses[L].append((cols[t], sid, cx, cy, 1))
        if light and fname == "bloom":
            flash(p, cx, cy, light, cols[1], L)


def flash(p: Pix, cx, cy, r, col, L):
    """A firework's light on the drawn things below it (the towers, the snow, whatever stands on it),
    strongest nearest the burst, on a layer of its own over the drawing that shows while the burst is in
    bloom. The sky and the words take none."""
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


def burst_box(x, y, r, kind) -> tuple:
    """The box (x0, y0, x1, y1) a burst at (x, y) reaches over all its frames, from the break to the last
    embers: its stars fly a little past `r` before they slow, glitter crackles a pixel or two beyond them,
    and they sink as they burn out, a willow's furthest."""
    spread = math.ceil(1.15 * r) + 2
    sink = math.ceil(1.15 * r + 3.5 * DROP[kind] * r) + 2
    return (x - spread, y - spread, x + spread + 1, y + sink + 1)


def show(p: Pix, bursts, night, motion, dur=12.0, start=0.0, room=None):
    """The fireworks of a header, for midnight only: each (x, y, r, colour, kind, light) goes up in turn from
    `start` of the way round a loop `dur` seconds long, so where the ball drops they answer it as it lands.
    `room(x, y, r, kind)`, when given, says how far below a burst its trail may first show, or None to leave
    out a burst that would reach a word; the others keep their turns. The day files' sky stays clear."""
    if not night:
        return
    n = len(bursts)
    for i, (x, y, r, colour, kind, light) in enumerate(bursts):
        rise = room(x, y, r, kind) if room else None
        if room and rise is None:
            continue
        off = start + (SHOW_SPAN - start) * i / max(1, n - 1)
        firework(p, x, y, r, colour, kind, motion=motion, offset=round(off, 3), dur=dur, seed=i + x, name=f"fw{i}",
                 light=light, rise=rise)


# --------------------------------------------------------------------------- light
def glow_cells(cx, cy, rx, ry, col, alphas, skip=()):
    """A small stepped glow as see-through pixels around (cx, cy), leaving out the pixels in `skip`."""
    out, n = {}, len(alphas)
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d < 1 and (x, y) not in skip:
                out[(x, y)] = f"{col}:{alphas[min(n - 1, int((1 - d) * n))]:g}"
    return out


def light_pool(p: Pix, cx, y, rx, ry, night, col=None):
    """A warm light pooled on the snow round its foot: only the snow takes it."""
    col = col or RAMP["gold"][4]
    if night:
        p.halo(cx, y, rx, ry, col, (0.1, 0.18, 0.27, 0.36), L="pool", only=GROUND)
    else:
        p.halo(cx, y, rx, ry, col, (0.05, 0.09), L="pool", only=GROUND)


# --------------------------------------------------------------------------- motion: confetti
def _confetti_cluster(seed, night, turn):
    """A little flurry of confetti, eight pieces in a 12 by 12 square, as pixels: each piece a square or a
    strip in its colour, lit or turned; `turn` flips every piece, the way paper tumbles as it falls."""
    rnd = random.Random(seed)
    cells = {}
    for _ in range(8):
        x, y = rnd.randrange(0, 11), rnd.randrange(0, 11)
        fam = rnd.choice(CONFETTI)
        lit = rnd.random() < 0.5
        if turn:
            lit = not lit
        strip = rnd.random() < 0.5
        cells[(x, y)] = confetti_colour(fam, night, lit)
        if strip:
            cells[(x + (0 if turn else 1), y + (1 if turn else 0))] = confetti_colour(fam, night, not lit)
    return cells


def falling_confetti(p: Pix, falls, night, motion=True, z=16):
    """Confetti coming down: each (x, y, ground, drift, dur, phase, seed) is a little flurry that starts at
    (x, y), sways side to side as it falls, every piece tumbling, lands at row `ground` a little to the
    side by `drift`, and is gone, round and round. The still file leaves each where its fall begins."""
    for (x, y, gy, drift, dur, phase, seed) in falls:
        frames = []
        for turn in (False, True):
            key = ("confetti", seed, night, turn)
            if key not in p.syms:
                p.symbol(key, _confetti_cluster(seed, night, turn))
            frames.append(key)
        if not motion:
            p.use(frames[0], x, y, "near")
            continue
        n = max(14, round((gy - y) / 2.2))
        path = []
        for s in range(n):
            t = s / (n - 1)
            path.append((round(x + drift * t + 2.6 * math.sin(2 * math.pi * (t * 1.8 + phase))),
                         round(y + (gy - 11 - y) * t)))
        path += [path[-1]] * 2 + [(-30, -30)] * 2
        p.fly(frames, path, dur, z=z, flap=0.25)


def flurries(p: Pix, specs, night, motion):
    """Confetti falling across a header: each (x, y, ground, drift, dur, phase), two flurries by turns."""
    falling_confetti(p, [(x, y, gy, drift, dur, ph, 11 + i % 2) for i, (x, y, gy, drift, dur, ph) in enumerate(specs)],
                     night, motion)


def bobbing(p: Pix, motion, name="bob0", lift=(0, 0, 1, 2, 2, 1), dur=3.0):
    """A layer that rises and settles a pixel or two, round and round: how a balloon rides the air."""
    return p.layer(name, ("bob", list(lift), dur)) if motion else "base"


# --------------------------------------------------------------------------- light that falls on things
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a light at (cx, cy): once everything is drawn, `lamplight` lays its warm light on
    whatever stands within `r` of it, flickering with it. `own` are the light's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def lamplight(p: Pix, night: bool):
    """The finishing pass: each sparkler's or lantern's light on the drawn things near it, strongest
    nearest the flame. The paper, the sky and the words take none."""
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
    """The shadow a thing standing on the snow leaves right under it: only the snow takes it."""
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


# --------------------------------------------------------------------------- the clock
def grandfather_clock(p: Pix, cx, base, night=False, L="base", motion=True, phase=0, dur=2.0):
    """A tall case clock standing on row `base`, centred on `cx`, 11 wide and 32 tall: black lacquer
    lit on its left with gold mouldings; in its hood a cream dial with its hands together at twelve,
    under a broken arch with a gold finial; in its trunk a glass door with the brass pendulum swinging
    behind it; a plinth on gilt feet. The pendulum swings in the moving files and hangs straight in the
    still ones."""
    M, G, Ch, K = RAMP["midnight"], RAMP["gold"], RAMP["champagne"], RAMP["coal"]
    k = -1 if night else 0
    x0 = round(cx) - 5

    def case(x, y, w):
        for i in range(w):
            c = (K[4] if i == 0 else (K[3] if i < w // 2 else K[2])) if not night else (K[3] if i == 0 else K[2])
            p.px(x + i, y, c, L)

    for j in range(4):                                      # the plinth and its feet
        case(x0, base - 1 - j, 11)
    p.px(x0, base - 1, G[3 + k], L)
    p.px(x0 + 10, base - 1, G[2 + k], L)
    p.hline(x0, x0 + 11, base - 5, G[4 + k], L)
    for j in range(15):                                     # the trunk, with its glass door
        case(x0 + 1, base - 6 - j, 9)
    wx, wy, ww, wh = x0 + 3, base - 19, 5, 12
    for yy in range(wy, wy + wh):
        for xx in range(wx, wx + ww):
            p.px(xx, yy, M[1] if not night else M[0], L)
    p.box(wx - 1, wy - 1, ww + 2, wh + 2, G[4 + k], L)
    p.px(wx, wy, M[3], L)                                   # a glint on the glass
    p.px(wx, wy + 1, M[2], L)
    p.hline(x0, x0 + 11, base - 21, G[4 + k], L)
    for j in range(10):                                     # the hood
        case(x0, base - 22 - j, 11)
    fcx, fcy, fr = round(cx) + 0.5, base - 26.5, 3.6        # the dial
    for yy in range(math.floor(fcy - fr) - 1, math.ceil(fcy + fr) + 1):
        for xx in range(math.floor(fcx - fr) - 1, math.ceil(fcx + fr) + 1):
            d = math.hypot(xx + 0.5 - fcx, yy + 0.5 - fcy)
            if d <= fr:
                p.px(xx, yy, Ch[6 + k] if xx + 0.5 < fcx else Ch[5 + k], L)
            elif d <= fr + 1:
                p.px(xx, yy, G[4 + k] if yy + 0.5 < fcy else G[3 + k], L)
    fx, fy = round(cx), base - 27
    for (dx, dy) in ((0, -3), (3, 0), (0, 3), (-3, 0)):
        p.px(fx + dx, fy + dy, K[3], L)                     # the hours at twelve, three, six and nine
    for dy in (0, -1, -2):
        p.px(fx, fy + dy, K[0], L)                          # both hands at twelve
    p.px(fx, fy, G[3], L)
    for (dx, dy) in ((-5, -10), (-4, -10), (-4, -11), (4, -11), (4, -10), (5, -10), (0, -12), (0, -11)):
        p.px(fx + dx, base - 22 + dy, G[4 + k] if dx <= 0 else G[3 + k], L)   # the broken arch and finial
    p.px(fx, base - 35, G[6 + k], L)
    # the pendulum, swinging: left, straight, right, straight
    pivot = (round(cx), wy)
    frames = [(-2, 0.0, 0.25), (0, 0.25, 0.5), (2, 0.5, 0.75), (0, 0.75, 1.0)] if motion else [(0, 0, 1)]
    for i, (sw, t0, t1) in enumerate(frames):
        Lp = p.seq(f"pd{phase}{i}", t0, t1, dur, keep=(sw == 0 and t0 == 0.25), z=1) if motion else L
        cells = {}
        _line(cells, pivot[0], pivot[1], pivot[0] + sw, pivot[1] + 8)
        for (qx, qy) in cells:
            p.px(qx, qy, G[3 + k], Lp)
        bx_, by_ = pivot[0] + sw, pivot[1] + 9
        for (dx, dy, t) in ((0, 0, 6), (-1, 0, 5), (1, 0, 4), (0, 1, 4), (-1, 1, 4), (1, 1, 3), (0, -1, 5)):
            p.px(bx_ + dx, by_ + dy, G[t + k], Lp)


# --------------------------------------------------------------------------- the year
# The ways the year can be set in balloons, largest first: the 5 by 7 face at twice its size, at its own
# size, then the 3 by 5 face. A year takes the largest that fits the room it has.
YEAR_FACES = (("57", 2, 3), ("57", 1, 2), ("35", 1, 1))


def year_width(year: str, font="57", scale=2, gap=3) -> int:
    """How wide the year is set in a face at a size, each figure `gap` from the next: a one is narrower
    than the other figures in the 5 by 7 face, so a year's width depends on its figures."""
    glyphs = FONTS[font][0]
    return sum(glyphs[ch][0] * scale for ch in year) + gap * (len(year) - 1)


def year_face(year: str, room: int) -> tuple:
    """The largest of the year faces the year fits in `room` pixels, or the smallest if none does."""
    for face in YEAR_FACES:
        if year_width(year, *face) <= room:
            return face
    return YEAR_FACES[-1]


# --------------------------------------------------------------------------- the ball drop
def ball_drop(p: Pix, cx, base, night=False, L="base", motion=True, dur=12.0, h=40, *, year: str):
    """The tower the ball drops from, standing on row `base`, centred on `cx`: a narrow tower of stone
    and glass, its windows in rows, `year` (its figures) in lamps on its roof on a frame as wide as they
    need, and above them a mast with the ball at its top, faceted in silver, gold, rose and teal crystal
    with glints. By day the ball waits at the top. By night it comes down the mast in the last seconds of
    the year, the year lights as it lands, and it glows while the fireworks go up; the still night file
    holds that moment."""
    S, M, G, R, T = RAMP["silver"], RAMP["midnight"], RAMP["gold"], RAMP["rose"], RAMP["teal"]
    k = -1 if night else 0
    tw = 13
    x0 = round(cx) - tw // 2
    top = base - h
    for xx in range(x0, x0 + tw):                           # the tower
        for yy in range(top, base):
            if night:
                c = M[2] if xx == x0 else M[1]
            else:
                c = S[5] if xx == x0 else (S[3] if xx == x0 + tw - 1 else S[4])
            p.px(xx, yy, c, L)
    rnd = random.Random(5)
    for yy in range(top + 9, base - 2, 2):                  # its windows
        for xx in range(x0 + 2, x0 + tw - 1, 2):
            if night:
                p.px(xx, yy, rnd.choice((G[5], RAMP["champagne"][5], M[2], M[2])), L)
            else:
                p.px(xx, yy, S[6] if rnd.random() < 0.5 else S[5], L)
    for yy in (top + 2, top + 6):                           # screens round its top, dark by day, bright by night
        for xx in range(x0, x0 + tw):
            p.px(xx, yy, (T[5] if xx % 3 else R[5]) if night else S[2], L)
    # the year, in lamps on a frame standing on the roof, as wide as its figures need
    glyphs = FONTS["35"][0]
    yw = year_width(year, "35", 1, 1)
    yx = round(cx) - yw // 2
    lamps = {}
    gx = yx
    for ch in year:
        for r_, cols in enumerate(glyphs[ch][1]):
            for col in cols:
                lamps[(gx + col, top - 6 + r_)] = 1
        gx += glyphs[ch][0] + 1
    p.hline(yx - 1, yx + yw + 1, top - 1, S[3 + k] if not night else M[3], L)
    for yy in range(top - 7, top - 1):
        p.px(yx - 1, yy, S[3 + k] if not night else M[3], L)
        p.px(yx + yw, yy, S[3 + k] if not night else M[3], L)
    dark = S[2] if not night else M[3]
    for (qx, qy) in lamps:
        p.px(qx, qy, dark, L)
    # the mast
    mt = top - 26
    for yy in range(mt, top - 7):
        p.px(round(cx), yy, S[5 + k] if not night else S[3], L)
    p.hline(round(cx) - 2, round(cx) + 3, top - 7, S[3 + k], L)

    def ball(q_, bx, by):
        """The ball's cells around (bx, by), nine across: crystal facets in rows, each lit or shaded, a
        bright crescent on its upper left and a darker one on its lower right."""
        pal = (S[6], S[5], G[5], R[5], T[5], S[4], G[4], S[5], T[4], R[4])
        for yy in range(-4, 5):
            for xx in range(-4, 5):
                if xx * xx + yy * yy > 18:
                    continue
                facet = pal[((xx + 4) // 2 + (yy + 4) * 3) % len(pal)]
                if xx + yy < -4:
                    facet = C["white"] if (xx + yy) % 2 == 0 else S[6]
                elif xx + yy > 4:
                    facet = step(facet, -1)
                q_[(bx + xx, by + yy)] = facet
        return q_

    def rays(Lr, bx, by):
        """Light thrown off the ball once it has landed: eight short rays, white at their roots."""
        for n_ in range(8):
            a = n_ * math.pi / 4 + math.pi / 8
            for j, rr in enumerate((6, 7, 8)):
                p.px(round(bx + math.cos(a) * rr), round(by + math.sin(a) * rr), (C["white"], G[6], G[5])[j], Lr)

    key = ("ball", night)
    if key not in p.syms:
        p.symbol(key, ball({}, 0, 0))
    ball_top, ball_low = mt - 3, top - 12
    if not night or not motion:
        by_ = ball_top if not night else ball_low
        p.use(key, round(cx), by_, "near" if night else L)
        if night:                                           # the year lit, the ball glowing, its light thrown out
            for (qx, qy) in lamps:
                p.px(qx, qy, G[6] if (qx + qy) % 2 else G[5], "near")
            p.halo(round(cx) + 0.5, by_ + 0.5, 8, 8, G[5], (0.08, 0.15, 0.25))
            rays("near", round(cx), by_)
        return
    # by night, moving: it waits at the top, comes down the mast, lands as the year lights, then glows
    n = 5
    for s in range(n + 1):
        t0 = 0.05 + 0.4 * s / (n + 1)
        t1 = 0.05 + 0.4 * (s + 1) / (n + 1)
        by_ = round(ball_top + (ball_low - ball_top) * s / n)
        Lb = p.seq(f"bd{s}", round(t0, 3), round(t1, 3), dur, z=19)
        p.uses[Lb].append((None, p.syms[key], round(cx), by_, 1))
    Lw = p.seq("bdw", 0.95, 1.0, dur, z=19)                 # back at the top for the next year
    p.uses[Lw].append((None, p.syms[key], round(cx), ball_top, 1))
    Lw0 = p.seq("bdv", 0.0, 0.05, dur, z=19)
    p.uses[Lw0].append((None, p.syms[key], round(cx), ball_top, 1))
    Ll = p.seq("bdl", 0.45, 0.95, dur, keep=True, z=19)     # landed: the year lit, the ball glowing
    p.uses[Ll].append((None, p.syms[key], round(cx), ball_low, 1))
    for (qx, qy) in lamps:
        p.px(qx, qy, G[6] if (qx + qy) % 2 else G[5], Ll)
    glass = {(round(cx) + dx, ball_low + dy) for dx in range(-4, 5) for dy in range(-4, 5)}
    for (qx, qy), c in glow_cells(round(cx) + 0.5, ball_low + 0.5, 8, 8, G[5], (0.08, 0.15, 0.25), glass).items():
        p.px(qx, qy, c, Ll)
    rays(p.seq("bdr", 0.47, 0.95, dur, keep=True, z=19.5), round(cx), ball_low)


# --------------------------------------------------------------------------- the toast
def champagne_bottle(p: Pix, x, base, night=False, L="base", motion=True, dur=6.0, phase=0, cork=True):
    """A bottle of champagne standing on row `base`, its left edge at `x`, 7 wide and 22 tall: dark green
    glass lit down its left side, a cream label with a gold crest, gold foil round its neck and the cork
    under its wire cage. In a moving file the cork pops now and then: it flies up and a spray of foam
    arcs out and falls, and the bottle is corked again for the next time. The still file keeps it
    corked."""
    Bt, G, Ch, S = RAMP["bottle"], RAMP["gold"], RAMP["champagne"], RAMP["silver"]
    k = -1 if night else 0
    rows = [1, 1, 1, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]   # half-widths from the lip down
    top = base - len(rows)
    cxb = x + 3
    for j, hw in enumerate(rows):
        yy = top + j
        for xx in range(cxb - hw, cxb + hw + 1):
            u = (xx - cxb) / max(1, hw)
            t = 4 if u < -0.5 else (3 if u < 0.2 else 2)
            c = Bt[t + k]
            if j < 6:                                       # the foil round the neck
                c = G[(5 if u < -0.2 else 4 if u < 0.4 else 3) + k]
            elif 9 <= j <= 14 and abs(u) < 0.9:             # the label
                c = Ch[(6 if u < -0.3 else 5) + k] if j not in (11,) else G[4 + k]
            p.px(xx, yy, c, L)
    for j in range(7, 17, 3):
        p.px(cxb - 3, top + j, Bt[5 + k], L)                # a glint down the glass
    p.px(cxb - 2, top + 16, Bt[5 + k], L)

    def corked(Lc):
        for (dx, dy, c) in ((-1, -1, Ch[4 + k]), (0, -1, Ch[5 + k]), (1, -1, Ch[3 + k]), (0, -2, Ch[4 + k]),
                            (-1, -2, Ch[5 + k]), (1, -2, Ch[3 + k]), (0, -3, S[4 + k])):
            p.px(cxb + dx, top + dy, c, Lc)

    if not cork:
        return
    if not motion:
        corked(L)
        return
    corked(p.seq(f"ck{phase}a", 0.0, 0.62, dur, keep=True, z=1))
    La = p.seq(f"ck{phase}b", 0.62, 0.7, dur, z=19)         # the pop: the cork just off, a burst of foam
    for (dx, dy, c) in ((0, -4, Ch[5]), (1, -5, Ch[4]), (0, -5, Ch[4]), (-1, -2, C["white"]), (1, -2, C["white"]),
                        (0, -2, Ch[6]), (-2, -3, Ch[6]), (2, -3, Ch[6])):
        p.px(cxb + dx, top + dy, c, La)
    Lb = p.seq(f"ck{phase}c", 0.7, 0.8, dur, z=19)          # the cork high, the spray arcing out
    for (dx, dy, c) in ((2, -10, Ch[5]), (3, -11, Ch[4]), (2, -11, Ch[4]), (-1, -4, C["white"]), (-3, -5, Ch[6]),
                        (-4, -4, Ch[6]), (1, -4, C["white"]), (3, -5, Ch[6]), (4, -4, Ch[6]), (0, -6, Ch[6]),
                        (-2, -7, Ch[5]), (2, -7, Ch[5])):
        p.px(cxb + dx, top + dy, c, Lb)
    Lc_ = p.seq(f"ck{phase}d", 0.8, 0.9, dur, z=19)         # the spray falling, the cork gone
    for (dx, dy, c) in ((-4, -2, Ch[5]), (-5, 0, Ch[5]), (4, -2, Ch[5]), (5, 0, Ch[5]), (-3, -4, Ch[6]),
                        (3, -4, Ch[6]), (0, -2, C["white"]), (-1, -3, Ch[6])):
        p.px(cxb + dx, top + dy, c, Lc_)
    corked(p.seq(f"ck{phase}e", 0.9, 1.0, dur, z=1))


def flute(p: Pix, x, base, night=False, L="base", motion=True, phase=0, fill=0.7, dur=1.8):
    """A champagne flute standing on row `base`, its left edge at `x`, 5 wide and 16 tall: a tall glass
    bowl, bright along its left side and its rim, filled `fill` of the way with champagne, gold and lit on
    its left, a line of foam on top and bubbles rising through it; a thin stem and a round foot. In a
    moving file the bubbles rise in turn."""
    S, G, Ch = RAMP["silver"], RAMP["gold"], RAMP["champagne"]
    k = -1 if night else 0
    bowl_top, bowl_h = base - 16, 9
    level = bowl_top + round(bowl_h * (1 - fill))
    for j in range(bowl_h):
        yy = bowl_top + j
        w_ = 5 if j < bowl_h - 2 else 3
        x0 = x + (5 - w_) // 2
        for i in range(w_):
            edge = i == 0 or i == w_ - 1
            if yy < level:
                c = ((S[6] if i == 0 else S[4]) if night else (S[4] if i == 0 else S[2])) if edge else None
            elif yy == level:
                c = Ch[6 + k] if not edge else (S[5] if night else S[3])
            else:
                c = (G[5 + k] if i <= 1 else G[4 + k] if i < w_ - 1 else G[3 + k])
                if edge:
                    c = (S[5] if night else S[3]) if i == 0 else G[2 + (0 if night else 0)]
            if c:
                p.px(x0 + i, yy, c, L)
    p.hline(x, x + 5, bowl_top, S[6] if night else S[3], L)   # the rim
    for yy in range(bowl_top + bowl_h, base - 1):           # the stem
        p.px(x + 2, yy, S[5 + k], L)
    for i, c in enumerate((S[5 + k], S[6 + k], S[5 + k], S[4 + k], S[3 + k])):
        p.px(x + i, base - 1, c, L)                          # the foot
    spots = [(x + 2, level + 5), (x + 1, level + 3), (x + 3, level + 1)]
    if not motion:
        p.px(*spots[0], Ch[6], L)
        p.px(*spots[2], Ch[6], L)
        return
    for f in range(3):                                      # bubbles rising in turn
        Lf = p.seq(f"bb{phase}{f}", round(f / 3, 3), round((f + 1) / 3, 3), dur, keep=f == 0, z=1)
        for s in range(3):
            bx_, by_ = spots[(s + f) % 3]
            if by_ > level:
                p.px(bx_, by_, Ch[6], Lf)


# --------------------------------------------------------------------------- balloons and hats
def balloon(p: Pix, cx, y, fam="gold", night=False, L="base", string=10, curl=1):
    """A round balloon, 7 wide and 9 tall with its top at row `y`, centred on `cx`: shaded round from the
    upper left with a bright glint, its knot below, and its ribbon hanging `string` pixels in a curl."""
    R = RAMP[fam]
    k = -1 if night else 0
    sphere(p, cx, y + 4.2, 3.6, R if not night else R[:-1], L=L, lo=1, spec=True, rim=True, outline=True)
    p.px(math.floor(cx), y + 8, R[2 + k], L)
    p.px(math.floor(cx) - 1, y + 9, R[3 + k], L)
    p.px(math.floor(cx) + 1, y + 9, R[2 + k], L)
    for j in range(string):
        p.px(math.floor(cx) + ((j // 2) % 2) * curl, y + 10 + j, RAMP["silver"][4 + k], L)


def year_balloons(p: Pix, x, y, night=False, L="base", strings=18, face=YEAR_FACES[0], *, year: str):
    """`year` (its figures) in foil balloons, its left edge at `x` and its top at row `y`, in `face` (a font,
    a size and the gap between figures): gold foil, puffed and bright along its upper left, darker toward
    its lower right, a dark seam round each figure; a ribbon from each down `strings` pixels to where it is
    tied. Returns the column under the middle of each figure, where its ribbon hangs, and the row under the
    figures."""
    G = RAMP["gold"]
    font, s, gap = face
    k = -1 if night else 0
    glyphs = FONTS[font][0]
    zero = (5, [[1, 2, 3], [0, 4], [0, 4], [0, 4], [0, 4], [0, 4], [1, 2, 3]])   # a nought without its slash
    mids, gx = [], x
    tall = FONTS[font][1] * s
    for ch in year:
        g = zero if (ch == "0" and font == "57") else glyphs[ch]
        cells = set()
        for r_, cols in enumerate(g[1]):
            for col in cols:
                for dy in range(s):
                    for dx in range(s):
                        cells.add((gx + col * s + dx, y + r_ * s + dy))
        span = max(1, g[0] * s + tall)
        for (qx, qy) in cells:
            lit = ((qx - gx) * 0.6 + (qy - y) * 0.35) / span * 14
            t = 6 if lit < 2.4 else (5 if lit < 5 else (4 if lit < 7.6 else 3))
            p.px(qx, qy, G[t + k], L)
        for (qx, qy) in cells:
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                q = (qx + dx, qy + dy)
                if q not in cells:
                    p.px(q[0], q[1], G[2 + k] if dx > 0 or dy > 0 else G[3 + k], L)
        mid = gx + (g[0] * s) // 2
        mids.append(mid)
        for j in range(strings):
            p.px(mid + (j // 3) % 2, y + tall + 1 + j, RAMP["silver"][4 + k], L)
        gx += g[0] * s + gap
    return mids, y + tall + 1


def party_hat(p: Pix, cx, base, fam="rose", night=False, L="base"):
    """A party hat standing on row `base`, centred on `cx`: a paper cone 7 wide and 9 tall in stripes of
    its colour and gold that wind round it, lit on its left, a gold band round its brim and a pompom of
    tinsel on its point."""
    R, G = RAMP[fam], RAMP["gold"]
    k = -1 if night else 0
    for j in range(9):
        yy = base - 1 - j
        hw = 3.5 * (1 - j / 9)
        for xx in range(math.floor(cx - hw), math.ceil(cx + hw)):
            u = (xx + 0.5 - cx) / max(0.5, hw)
            stripe = int((xx + j * 1.0) / 2) % 2 == 0
            F = G if stripe else R
            t = 5 if u < -0.35 else (4 if u < 0.35 else 3)
            p.px(xx, yy, F[t + k], L)
    p.hline(math.floor(cx - 3.5), math.ceil(cx + 3.5), base - 1, G[3 + k], L)
    for (dx, dy, t) in ((0, -11, 6), (-1, -10, 5), (0, -10, 6), (1, -10, 4), (0, -9, 5)):
        p.px(math.floor(cx) + dx, base + dy, G[t + k], L)


def noisemaker(p: Pix, x, y, fam="teal", night=False, L="base"):
    """A party horn, its mouthpiece at (x, y): a paper tube in stripes and its blowout unrolled in a curl
    with a fringe of foil at its end."""
    R, G = RAMP[fam], RAMP["gold"]
    k = -1 if night else 0
    for i in range(7):
        p.px(x + i, y, (G if i % 2 else R)[(5 if i < 3 else 4) + k], L)
        p.px(x + i, y + 1, (G if i % 2 else R)[3 + k], L)
    for (dx, dy) in ((7, -1), (8, -2), (9, -2), (10, -1), (10, 0), (9, 1), (8, 1)):
        p.px(x + dx, y + dy, R[4 + k], L)
    for (dx, dy) in ((11, -2), (11, 0), (12, -1)):
        p.px(x + dx, y + dy, G[5 + k], L)


def party_popper(p: Pix, x, base, night=False, L="base"):
    """A party popper standing on row `base` at `x`: a gold cone with its streamers burst out of it in
    curls of rose, teal and silver, and confetti thrown up around them."""
    G = RAMP["gold"]
    k = -1 if night else 0
    for j in range(6):
        hw = 1 + j * 0.45
        for xx in range(math.floor(x + 2 - hw), math.ceil(x + 2 + hw)):
            p.px(xx, base - 1 - (5 - j), G[(5 if xx < x + 2 else 3) + k], L)
    for fam, pts in (("rose", ((1, -8), (0, -9), (0, -10), (1, -11), (2, -12))),
                     ("teal", ((3, -8), (4, -9), (5, -9), (6, -10), (6, -11))),
                     ("silver", ((2, -8), (2, -9), (3, -10), (3, -11), (4, -12), (4, -13)))):
        for (dx, dy) in pts:
            p.px(x + dx, base + dy, confetti_colour(fam, night, True), L)
    for (dx, dy, fam) in ((-2, -12, "gold"), (7, -13, "rose"), (-1, -14, "teal"), (8, -9, "violet"), (1, -15, "gold")):
        p.px(x + dx, base + dy, confetti_colour(fam, night, True), L)


def ice_bucket(p: Pix, x, base, night=False, L="base"):
    """A silver bucket of ice standing on row `base` at `x`, 11 wide: polished and lit on its left with a
    bright band at its lip and two ring handles, ice heaped at its top and a bottle's gold neck standing
    out of it at a slant."""
    S, G, Bt = RAMP["silver"], RAMP["gold"], RAMP["bottle"]
    k = -1 if night else 0
    for j in range(8):
        yy = base - 1 - j
        hw = 4.5 + j * 0.12
        for xx in range(math.floor(x + 5.5 - hw), math.ceil(x + 5.5 + hw)):
            u = (xx + 0.5 - (x + 5.5)) / hw
            t = 6 if u < -0.6 else (5 if u < -0.2 else (4 if u < 0.4 else 3))
            p.px(xx, yy, S[t + k], L)
    p.hline(x - 0, x + 12, base - 9, S[6 + k], L)
    for (dx, dy) in ((-1, -6), (-1, -5), (12, -6), (12, -5)):
        p.px(x + dx, base + dy, S[3 + k], L)
    for (dx, dy) in ((1, -10), (2, -10), (3, -11), (7, -10), (8, -10), (9, -11), (10, -10)):
        p.px(x + dx, base + dy, S[6 + k] if dx % 2 else S[5 + k], L)       # the ice
    for j in range(8):                                     # the bottle's neck, at a slant
        xx, yy = x + 4 + j // 3, base - 10 - j
        p.px(xx, yy, Bt[3 + k] if j < 3 else G[4 + k], L)
        p.px(xx + 1, yy, Bt[2 + k] if j < 3 else G[3 + k], L)
    p.px(x + 7, base - 18, RAMP["champagne"][4 + k], L)


def calendar_page(p: Pix, x, y, night=False, L="base"):
    """A leaf of a tear-off calendar, 13 by 15, top-left at (x, y): two silver rings at its head, a rose
    band with JAN in white, and the first of the month large on the page below."""
    S, R, Ch = RAMP["silver"], RAMP["rose"], RAMP["champagne"]
    k = -1 if night else 0
    for yy in range(y, y + 15):
        for xx in range(x, x + 13):
            c = R[3 + k] if yy < y + 6 else (C["white"] if xx < x + 12 else Ch[5])
            if yy == y + 14 or xx == x + 12:
                c = S[4 + k] if yy >= y + 6 else R[2 + k]
            p.px(xx, yy, c, L)
    for rx in (x + 3, x + 9):
        p.px(rx, y - 1, S[5 + k], L)
        p.px(rx, y, S[3 + k], L)
    glyphs = FONTS["35"][0]
    tx = x + (12 - (sum(glyphs[ch][0] for ch in "JAN") + 2)) // 2
    for ch in "JAN":
        for r_, cols in enumerate(glyphs[ch][1]):
            for col in cols:
                p.px(tx + col, y + 1 + r_, C["white"], L)
        tx += glyphs[ch][0] + 1
    g1 = FONTS["57"][0]["1"]
    for r_, cols in enumerate(g1[1]):
        for col in cols:
            p.px(x + 5 + col, y + 7 + r_, C["ink"], L)


def sparkler(p: Pix, x, base, h=12, night=False, L="base", phase=0, motion=True, lean=0):
    """A sparkler held upright, its foot on row `base`: a grey wire, its upper part crusted where the
    powder is, burning at its tip, white-hot in a gold glow, throwing short sparks on three layers that
    take turns so in a moving file they crackle; its light falls on whatever stands near it."""
    S, G = RAMP["silver"], RAMP["gold"]
    wire = []
    for j in range(h):
        wire.append((x + round(lean * (h - j) / h), base - 1 - j))
    for i, (xx, yy) in enumerate(wire):
        p.px(xx, yy, (S[2] if i > h * 0.4 else S[3]) if night else (S[3] if i > h * 0.4 else S[4]), L)
    tx, ty = wire[-1][0], wire[-1][1] - 1
    Lf = p.flicker(phase) if motion else L
    p.px(tx, ty, C["white"], Lf)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(tx + dx, ty + dy, G[6], Lf)
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
                p.px(q[0], q[1], G[6] if n_ == 0 else (G[5] if n_ == 1 else G[4]), Ls)
            if not motion and _ % 2:
                break
    own = {(tx + dx, ty + dy) for dx in range(-7, 8) for dy in range(-7, 8)}
    for (qx, qy), c in glow_cells(tx + 0.5, ty + 0.5, 2.6, 2.6, G[5], (0.3, 0.5) if night else (0.12, 0.2),
                                  {(tx, ty)}).items():
        if (qx, qy) not in p.layers.get(Lf, {}):
            p.px(qx, qy, c, Lf)
    lamp(p, tx + 0.5, ty + 0.5, 9 if night else 6, phase, own | set(wire))


def hourglass(p: Pix, x, base, night=False, L="base"):
    """An hourglass standing on row `base` at `x`, 7 wide and 11 tall: gold ends and posts, and glass
    bulbs with the last of the year's sand running from the top into the heap below."""
    G, S, Ch = RAMP["gold"], RAMP["silver"], RAMP["champagne"]
    k = -1 if night else 0
    p.hline(x, x + 7, base - 1, G[3 + k], L)
    p.hline(x, x + 7, base - 11, G[4 + k], L)
    for yy in range(base - 10, base - 1):
        p.px(x, yy, G[4 + k], L)
        p.px(x + 6, yy, G[3 + k], L)
    for j, hw in enumerate((2, 2, 1, 0, 0, 1, 2, 2, 2)):
        yy = base - 10 + j
        for xx in range(x + 3 - hw, x + 4 + hw):
            sand = ((j <= 1 and abs(xx - (x + 3)) <= 0) or j >= 7 or (j == 6 and abs(xx - (x + 3)) <= 1)
                    or (3 <= j <= 5 and xx == x + 3))
            p.px(xx, yy, (Ch[4 + k] if sand else S[6 + k] if xx < x + 3 else S[5 + k]), L)


def star5(p: Pix, x, y, fam="gold", night=False, L="base", reuse=True):
    """A five-point foil star, 5 by 5, top-left at (x, y), lit on its upper-left points."""
    R = RAMP[fam]
    k = -1 if night else 0
    art = ["..a..", "aabbc", ".abc.", ".b.c.", "b...c"]
    p.sprite(x, y, art, {"a": R[6 + k] if fam != "silver" else R[6], "b": R[5 + k], "c": R[4 + k]}, 1, L,
             reuse=reuse)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["rose"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)


# --------------------------------------------------------------------------- the elements' pieces
ON_ICE = (28, 18)   # champagne on ice with two flutes poured: its width and its height


def champagne_on_ice(p: Pix, x, y, night=False):
    """Champagne on ice beside two flutes poured, top-left at (x, y), all standing on its foot row: the
    silver bucket with the bottle's neck out of it, a full flute and one half drunk."""
    base = y + ON_ICE[1]
    ice_bucket(p, x + 1, base, night)
    flute(p, x + 17, base, night, motion=False)
    flute(p, x + 23, base, night, motion=False, fill=0.55)


def stripe_bar(p: Pix, x0, y0, w, h, period=5):
    """A bar striped like a party streamer, gold and midnight, `period` pixels a stripe: lit along the top,
    shaded along the bottom."""
    G, M = RAMP["gold"], RAMP["midnight"]
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
        for xx in range(x0, x0 + w):
            bright = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (G[6], G[5], G[3])[band] if bright else (M[4], M[3], M[2])[band])


def champagne_glass(p: Pix, bx, base, bw, v, night, edge):
    """A week's commits as a tall glass of champagne poured to its count, `v` pixels, standing on `base`:
    silver walls, bright on the left, the wine gold and lit on its left with bubbles rising through it, a
    crown of foam on top, and an outline in `edge`."""
    G, S, Ch = RAMP["gold"], RAMP["silver"], RAMP["champagne"]
    k = -1 if night else 0
    for xx in range(bx, bx + bw):
        nx = 2 * (xx - bx + 0.5) / bw - 1
        lam = max(0.0, nx * LX + math.sqrt(1 - nx * nx) * LZ)
        for yy in range(base - v, base):
            if xx in (bx, bx + bw - 1):
                c = S[6 + k] if xx == bx else S[3 + k]           # the glass walls
            elif yy < base - v + 2:
                c = Ch[6 + k] if yy == base - v else Ch[5 + k]   # the foam
            else:
                c = G[max(1, min(6, round(3.2 + 2.0 * lam) + k))]
            p.px(xx, yy, c)
    if bw >= 5 and v >= 5:                                      # bubbles rising
        rnd = random.Random(bx * 31 + v)
        for _ in range(max(1, v // 5)):
            p.px(bx + rnd.randint(2, bw - 3), base - rnd.randint(2, max(3, v - 3)), Ch[6])
    p.vline(bx - 1, base - v, base, edge)
    p.vline(bx + bw, base - v, base, edge)
    p.hline(bx, bx + bw, base - v - 1, edge)


def clock_ring(p: Pix, cx, cy, r0, r1, night):
    """The upper half of a clock's face as a dial, between radii r0 and r1: a cream face lit on its left,
    a gold bezel round it bright along its upper left, and a tick at every hour of the half turn."""
    G, Ch, K = RAMP["gold"], RAMP["champagne"], RAMP["coal"]
    k = -1 if night else 0
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy) + 1):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not r0 <= rho <= r1 or dy > 0:
                continue
            th = math.atan2(-dy, dx)
            if rho > r1 - 2.4:
                c = G[(5 if dx < 0 else 4) + k] if rho > r1 - 1.2 else G[3 + k]
            else:
                c = Ch[(6 if dx < -r1 * 0.2 else 5) + k]
                f = th / (math.pi / 6)
                if abs(f - round(f)) < 0.09 and rho > r1 - 6:
                    c = K[3]                                # an hour's tick
            p.px(xx, yy, c)


def flip_tile(q: Pix, ox, oy):
    """One counter's tile on a flip clock, 11 by 15, top-left at (ox, oy): dark, its upper leaf a shade
    lighter than its lower, split by the hinge across its middle, lit along its top edge."""
    K = RAMP["coal"]
    for yy in range(15):
        for xx in range(11):
            c = K[3] if yy < 7 else K[2]
            if yy == 0:
                c = K[5]
            if yy == 7:
                c = K[0]
            if xx == 10 or yy == 14:
                c = K[1]
            q.px(ox + xx, oy + yy, c)
    q.px(ox, oy + 7, RAMP["silver"][3])
    q.px(ox + 9, oy + 7, RAMP["silver"][3])


def twine(p: Pix, x0, x1, y, night):
    """The cord the party lights hang from: a dark flex with a glint along its top."""
    K = RAMP["coal"]
    for x in range(x0, x1):
        p.px(x, y, K[5] if x % 4 == 0 else (K[4] if not night else K[5]))
        p.px(x, y + 1, K[2] if not night else K[4])


LIGHT_FAMILIES = ("rose", "teal", "gold", "violet")   # the party lights' colours, by turns


def party_light(p: Pix, x, gy, kind, night, i=0, unlit=None):
    """A release hanging from the cord of party lights at x, the cord's top on row `gy`: a lit bulb in its
    colour, a bigger gold one for a big release, a bead of light for a patch, a silver foil star for the
    repository's making, and for one still to come a bulb not yet lit, outlined in `unlit`. By night the
    lit ones glow."""
    K = RAMP["coal"]
    k = -1 if night else 0
    if kind in ("big", "major"):
        R = RAMP["gold" if kind == "big" else LIGHT_FAMILIES[i % 4]]
        big = kind == "big"
        p.px(x, gy + 2, K[4])
        p.px(x + 1, gy + 2, K[3])
        rows = [3, 5, 5, 5, 5, 3] if big else [2, 4, 4, 4, 2]
        for j, wdt in enumerate(rows):
            x0 = x + 1 - wdt // 2
            for ii in range(wdt):
                t = 6 if (ii == 0 and j < 2) else (5 if ii < wdt // 2 + 1 else 4)
                p.px(x0 + ii, gy + 3 + j, R[t] if night else R[t - 1])
        if night:
            glass = {(x + dx, gy + 3 + dy) for dx in range(-2, 4) for dy in range(len(rows))}
            r = 5.2 if big else 4.2
            for (qx, qy), c in glow_cells(x + 1, gy + 3 + len(rows) / 2, r, r, R[6], (0.16, 0.3), glass).items():
                p.px(qx, qy, c, "haze")
    elif kind == "minor":
        R = RAMP[LIGHT_FAMILIES[i % 4]]
        p.px(x, gy + 2, K[4])
        p.px(x, gy + 3, R[5 + k])
        p.px(x + 1, gy + 3, R[4 + k])
    elif kind == "made":
        p.px(x, gy + 2, K[4])
        p.px(x + 1, gy + 2, K[3])
        star5(p, x - 1, gy + 3, "silver", night, reuse=False)
    else:
        p.px(x, gy + 2, K[4])
        p.px(x + 1, gy + 2, K[3])
        p.sprite(x - 1, gy + 3, [".##.", "#..#", "#..#", "#..#", ".##."], {"#": unlit})


# The colour a guest's ball is shaded in, its ramp's darkest and lightest tones, so their initials keep
# 4.5:1, and the colour of the hat each wears.
GUESTS = {"rose": ((1, 4), "teal"), "gold": ((3, 6), "rose"), "teal": ((0, 3), "gold")}


def guest(p: Pix, cx, cy, fam, initials, night):
    """A contributor as a party guest, centred on (cx, cy): a ball in their colour with their initials on
    it, under a striped paper hat with a tinsel pompom."""
    Rm = RAMP[fam]
    (lo, hi), hat = GUESTS[fam]
    sphere(p, cx + 0.5, cy + 1.5, 7.0, Rm, lo=lo, hi=hi)
    tx = cx - p.measure(initials, "35") // 2
    if fam == "gold":
        p.text(tx, cy, initials, RAMP["coal"][0], "35")
    else:
        p.text(tx, cy, initials, C["white"], "35", shadow=Rm[0])
    party_hat(p, cx + 0.5, cy - 4, hat, night)


def alarm_clock(p: Pix, cx, cy, night):
    """A bot as a little gold alarm clock with an aerial, centred on (cx, cy): its cream face and hands, a
    bell each side of its top, two feet, and a light at the aerial's tip."""
    G, Ch, K = RAMP["gold"], RAMP["champagne"], RAMP["coal"]
    k = -1 if night else 0
    sphere(p, cx + 0.5, cy + 2.5, 6.0, G, lo=2, hi=6)
    for yy in range(math.floor(cy + 2.5 - 4.2), math.ceil(cy + 2.5 + 4.2)):
        for xx in range(math.floor(cx + 0.5 - 4.2), math.ceil(cx + 0.5 + 4.2)):
            if math.hypot(xx + 0.5 - cx - 0.5, yy + 0.5 - cy - 2.5) <= 4.2:
                p.px(xx, yy, Ch[6] if xx < cx else Ch[5])
    for dy in range(-3, 1):
        p.px(round(cx), round(cy + 2.5) + dy, K[1])
    p.px(round(cx) + 1, round(cy + 2.5), K[1])
    p.px(round(cx) + 2, round(cy + 2.5), K[1])
    for (dx, dy) in ((-5, -4), (-4, -5), (-3, -5), (4, -5), (5, -5), (5, -4)):
        p.px(round(cx) + dx, round(cy) + dy, G[5 + k] if dx < 0 else G[4 + k])     # its two bells
    for (dx, dy) in ((-4, 8), (5, 8)):
        p.px(round(cx) + dx, round(cy) + dy, K[3])
    p.vline(round(cx), cy - 9, cy - 4, K[4] if night else K[3])
    p.halo(cx + 0.5, cy - 9.5, 2.2, 2.2, G[4], (0.25, 0.4))
    p.px(round(cx), cy - 10, G[6])


def foil_seal(p: Pix, cx, cy, r, night, n=24):
    """A seal of gold foil behind the certificate's disc: a starburst of `n` points round a ring of radius
    `r`, each point folded so one face catches the light and the other falls in shade, the whole lit on
    its upper left."""
    G = RAMP["gold"]
    k = -1 if night else 0
    for yy in range(math.floor(cy - r - 4), math.ceil(cy + r + 4)):
        for xx in range(math.floor(cx - r - 4), math.ceil(cx + r + 4)):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if rho < r - 5:
                continue
            f = (math.atan2(dy, dx) + math.pi) / (2 * math.pi / n)
            within = f - math.floor(f)
            if rho > r + 2.6 * (1 - abs(within - 0.5) * 2):
                continue
            lit = -(dx * LX + dy * LY) / r
            t = 5 if lit > 0.3 else (4 if lit > -0.3 else 3)
            if within > 0.5:
                t -= 1                                        # the point's shaded face
            p.px(xx, yy, G[max(1, t + k)])


# --------------------------------------------------------------------------- icons
# The link buttons' sprites, 7 by 7, lit from the upper left like everything else. Tones: a b c a foil
# star, r o q n s a balloon with its knot and string, w f g a flute of champagne, p t u y d a party hat.
ICONS = {
    "star": ["...a...", "..aab..", "aaabbbc", ".abbbc.", "..bbc..", ".bb.cc.", "bb...cc"],
    "balloon": ["..rro..", ".roooq.", ".ooooq.", ".oooqq.", "..oqq..", "...n...", "..s...."],
    "flute": [".wwwww.", ".wfffw.", ".wgggw.", "..wgw..", "...w...", "...w...", "..www.."],
    "hat": ["...p...", "...t...", "..tyu..", "..ytu..", ".tyyuu.", ".yttyu.", "ddddddd"],
}


def icon_pal(night: bool) -> dict:
    """The icons' tones: by day a tone deeper, so they read on the button's white face; by night lighter,
    on its midnight one."""
    G, R, T, S, Ch = (RAMP[n] for n in ("gold", "rose", "teal", "silver", "champagne"))
    k = 0 if night else -1
    return {"a": G[6 + k], "b": G[5 + k], "c": G[4 + k],
            "r": R[6 + k], "o": R[5 + k], "q": R[4 + k], "n": R[3 + k], "s": S[4 + k],
            "w": S[5 + k] if night else S[3], "f": Ch[6 + k], "g": G[5 + k],
            "p": G[6 + k], "t": T[5 + k], "u": T[4 + k], "y": G[5 + k], "d": G[4 + k]}
