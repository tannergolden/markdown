# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Valentine's Day set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the frame, the scenery a header stands on,
and every sprite, each shaded from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ..pixel import FONTS, LX, LY, LZ, Pix, fold, sphere
from ..pixel.shade import _tone
from .palette import C, GROUND, NIGHT_SKY, PETALS, RAMP, RUNNER, STONE, X, step


def foil_fill(r, c, scale, night):
    """The colour a title's letter takes at row `r` and column `c` of the letter, counted in pixels from
    its top-left. By day candy-apple lacquer, a band for each row of the face: coral at the crown, deepening
    to crimson, a gloss of coral where the lacquer catches the light across its middle, and deep red again
    to the foot. By night the letters are a pink neon sign, a paler core across the crown and the middle,
    every band a tone that keeps 4.5:1 against the plum sky."""
    R, B = RAMP["rose"], RAMP["blush"]
    band = min(6, r // scale)
    if night:
        return (B[6], B[5], B[4], B[6], B[5], B[4], B[4])[band]
    return (R[5], R[4], R[3], R[5], R[4], R[3], R[2])[band]


def glints(p: Pix, x, y, s, scale):
    """Glints where the light catches a title's lacquer: on every third letter from the second, at the left
    end of its top stroke, each on one of the three twinkling layers, so they twinkle in a moving file and
    hold in a still one."""
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
    """The ground a drawing sits on: soft blush-white paper with a dot grid by day, by night the plum sky,
    lighter toward the horizon in five bands."""
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
    """A February night's stars at three magnitudes: faint pinpricks, bright points, and a few glints,
    some white and some the pink of a petal. None is set inside a box in `avoid` (x0, y0, x1, y1), so no
    glint sits in a letter or beside a word."""
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
            p.px(x, y, rnd.choice((C["white"], RAMP["blush"][6], X["star_pale"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.3)


# --------------------------------------------------------------------------- the ribbon round the sheet
STITCH = ((0, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2))      # a heart three pixels square


def ribbon_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="rb"):
    """The sheet's border: a red satin ribbon three pixels wide, lit along its outer edge and deeper along
    its inner one, with a little white heart stitched into it every eight pixels, upright on every side;
    inside it a pink rule. Each side is one pattern tile placed along it, so the border costs a few hundred
    bytes."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    R, B = RAMP["rose"], RAMP["blush"]
    k = -1 if night else 0
    heart = B[5] if night else C["white"]

    def tile(horizontal):
        cells = {}
        for a in range(8):
            for b in range(3):
                shade = (R[4 + k], R[3 + k], R[2 + k])[b]
                cells[(a, b) if horizontal else (b, a)] = shade
        for (hx, hy) in STITCH:
            cells[(hx + 3, hy) if horizontal else (hx, hy + 3)] = heart
        return cells

    for name, horizontal in (("h", True), ("v", False)):
        cells = tile(horizontal)
        tw, th = (8, 3) if horizontal else (3, 8)
        p.defs.append(f'<pattern id="{uid}{name}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
                      f'{p._paths(cells)}</pattern>')
    p.defs.append(f'<rect id="{uid}H" width="{w}" height="3" fill="url(#{uid}h)"/>')
    p.defs.append(f'<rect id="{uid}V" width="3" height="{h - 6}" fill="url(#{uid}v)"/>')
    for (name, bx, by) in (("H", x, y), ("H", x, y + h - 3), ("V", x, y + 3), ("V", x + w - 3, y + 3)):
        p.shapes["base"].append(f'<use href="#{uid}{name}" x="{bx}" y="{by}"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, B[3] if night else B[4])


def heart_chase(p: Pix, x=0, y=0, w=None, h=None):
    """The ribbon's stitched hearts along its top and its foot lighting up white in turn, every other one,
    the way a string of lights chases: each on one of the three twinkling layers, over the ribbon."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    i = 0
    for hx in range(x + 3, x + w - 3, 16):
        for hy in (y, y + h - 3):
            L = p.twinkle(i)
            for (a, b) in STITCH:
                p.px(hx + a, hy + b, C["white"], L)
            i += 1


# --------------------------------------------------------------------------- bunting and petals
def _heart_art(fam, night, lace=False):
    """A paper heart five pixels square as sprite rows and colours: lit on its upper-left lobe, shaded
    toward its point. A lace heart is white with a pink edge."""
    art = [".a.b.", "aabbc", "abbbc", ".bcc.", "..c.."]
    if lace:
        B = RAMP["blush"]
        return [".e.e.", "eaaae", "eabbe", ".ebe.", "..e.."], {
            "a": C["white"], "b": RAMP["lace"][5 if not night else 3], "e": B[4 if not night else 3]}
    R = RAMP[fam]
    k = -1 if night else 0
    return art, {"a": R[5 + k], "b": R[4 + k], "c": R[3 + k]}


def _bunting_span(sp, sag, night, variant):
    """One span of the bunting, tack to tack, as pixels: a twine sagging `sag` rows at the middle and paper
    hearts hung from it a hand apart, red, pink and lace by turns."""
    q = Pix(sp + 2, sag + 10)
    oy = 1
    twine = RAMP["cocoa"][5] if not night else RAMP["lace"][2]
    pts = [(xx, oy + round(sag * 4 * (xx / sp) * (1 - xx / sp))) for xx in range(sp + 1)]
    for (xx, yy) in pts:
        q.px(xx, yy, twine)
    for (a_, b_) in zip(pts, pts[1:]):
        if abs(a_[1] - b_[1]) > 1:
            for yy in range(min(a_[1], b_[1]) + 1, max(a_[1], b_[1])):
                q.px(a_[0], yy, twine)
    fams = ("rose", "blush", "lace", "rose", "blush")
    for j, hx in enumerate(range(4, sp - 3, 8)):
        fam = fams[(j + variant) % len(fams)]
        art, pal = _heart_art(fam, night, lace=fam == "lace")
        ty = pts[hx + 2][1] + 1
        q.sprite(hx, ty, art, pal)
    return {(x, y - oy): c for (x, y), c in q.layers["base"].items()}


def _bow(night):
    """The red satin bow at a tack, as pixels round the tack: two loops, a knot and two tails."""
    R = RAMP["rose"]
    k = -1 if night else 0
    art = ["ad.da", "adkda", "a.c.a", "..c.."]
    pal = {"a": R[4 + k], "d": R[5 + k], "k": R[2 + k], "c": R[3 + k]}
    return {(i - 2, j - 1): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if ch in pal}


def bunting(p: Pix, x0, x1, y, span=40, sag=4, night=False, reuse=True):
    """Bunting along the top: a twine swagged from tack to tack with paper hearts hung along it, and a
    red satin bow at every tack. Each swag is drawn once and hung again and again; the last is cut to fit.
    With `reuse` off it is drawn in pixels instead, so whatever is set over it later hides it."""
    xs = list(range(x0, x1, span))
    hung = [(("bunting", min(span, x1 - xa), sag, night, i % 2), xa) for i, xa in enumerate(xs) if x1 - xa >= 10]
    hung += [(("bow", night), min(xa, x1 - 3)) for xa in xs + [x1]]
    for key, x in hung:
        if not reuse:
            for (cx, cy), c in (_bow(night) if key[0] == "bow" else _bunting_span(*key[1:])).items():
                p.px(x + cx, y + cy, c)
            continue
        if key not in p.syms:
            p.symbol(key, _bow(night) if key[0] == "bow" else _bunting_span(*key[1:]))
        p.use(key, x, y)


def petals_on(p: Pix, x0, x1, y, seed=7, L="base", night=False, gap=(4, 11)):
    """Rose petals lying along a ledge whose top edge is row `y`, red and pink, curled or flat, and here and
    there a little heart standing on its point. None lies where it would touch a word."""
    rnd = random.Random(seed * 131 + x0)
    x = x0 + rnd.randint(1, 4)
    k = -1 if night else 0
    while x < x1 - 3:
        R = RAMP[rnd.choice(PETALS)]
        if not p.clear_of_words(x, y - 4, x + 4, y):
            x += rnd.randint(*gap)
            continue
        r = rnd.random()
        if r < 0.16:                                         # a little heart on its point
            for (dx, dy, t) in ((0, -3, 5), (2, -3, 4), (0, -2, 4), (1, -2, 4), (2, -2, 3), (1, -1, 3)):
                p.px(x + dx, y + dy, R[t + k], L)
            x += 3
        elif r < 0.6:                                        # a petal lying curled
            p.px(x, y - 1, R[4 + k], L)
            p.px(x + 1, y - 1, R[3 + k], L)
            x += 2
        else:                                                # a petal on its edge
            p.px(x, y - 1, R[5 + k], L)
            x += 1
        x += rnd.randint(*gap)


# --------------------------------------------------------------------------- what things stand on
def lace_runner(p: Pix, x0, x1, y_top, y_bot, seed=5, night=False, L="base", petals=True):
    """A lace runner along the foot of a drawing, the table the party is laid on: a pink top lit along its
    edge, a row of eyelets, a scalloped hem, and petals fallen on it. By night it is plum in the candlelight."""
    hi, mid, lo = RUNNER[night]
    rnd = random.Random(seed)
    for x in range(x0, x1):
        for j, yy in enumerate(range(y_top, y_bot)):
            if j == 0:
                c = hi
            elif j == y_bot - y_top - 1:
                c = lo if x % 2 == 0 else mid
            else:
                c = lo if x % 3 == 1 else mid
            p.px(x, yy, c, L)
    if petals:
        k = -1 if night else 0
        for x in range(x0 + 1, x1 - 1):
            if rnd.random() < 0.12:
                R = RAMP[rnd.choice(PETALS)]
                p.px(x, y_top, R[(4 if rnd.random() < 0.6 else 3) + k], L)


def quay(p: Pix, x0, x1, base, night=False, h=4, rail=6, seed=2, L="base", locks=True):
    """The quay along the river: a parapet of dressed stone `h` rows tall, its coping lit, its blocks laid
    in a running bond; on it an iron railing `rail` rows tall, hung thick with love locks toward its middle,
    gold, red, pink, lilac and steel, each a padlock two pixels wide."""
    hi, mid, lo = STONE[night]
    rnd = random.Random(seed)
    top = base - h
    for x in range(x0, x1):
        for yy in range(top, base):
            j = yy - top
            if j == 0:
                c = hi
            elif (j % 2 == 1 and (x - x0 + (j // 2) * 4) % 8 == 0) or j == h - 1 and x % 2 == 0:
                c = lo
            else:
                c = mid
            p.px(x, yy, c, L)
    iron = RAMP["coal"][3] if not night else RAMP["coal"][2]
    lit = RAMP["coal"][5] if not night else X["moonlit"]
    rt = top - rail
    p.hline(x0, x1, rt, lit, L)
    p.hline(x0, x1, top - 1, iron, L)
    for x in range(x0, x1, 3):
        p.vline(x, rt + 1, top - 1, iron, L)
    if not locks:
        return
    fams = ("gold", "rose", "blush", "lilac", "silver", "rose", "gold")
    k = -1 if night else 0
    mid_x, span = (x0 + x1) / 2, (x1 - x0) / 2
    for x in range(x0 + 1, x1 - 2, 2):
        for yy in range(rt + 2, top - 1, 2):
            near = 1 - abs(x - mid_x) / span
            if rnd.random() < 0.25 + 0.55 * near:
                R = RAMP[rnd.choice(fams)]
                p.px(x + rnd.randint(0, 1), yy - 1, R[5 + k] if R is not RAMP["silver"] else R[5], L)   # its shackle
                p.px(x, yy, R[4 + k], L)
                p.px(x + 1, yy, R[3 + k], L)


# --------------------------------------------------------------------------- Paris
def paris(p: Pix, x0, x1, base, night=False, seed=3, lo=10, hi=18, L="base", sun_x=None, lit=0.4):
    """The roofs of Paris: a terrace of stone houses under zinc mansard roofs with dormers and chimney pots,
    a balcony along the second floor. By day the stone is cream, lit on the side toward the sun, the
    windows dark; by night the stone is plum, the roofs catch the moon along their ridge and some windows
    are lit."""
    rnd = random.Random(seed)
    Lc, S, W, G, K = RAMP["lace"], RAMP["silver"], RAMP["wine"], RAMP["gold"], RAMP["coal"]
    x = x0
    while x < x1 - 4:
        w = min(rnd.randint(10, 15), x1 - x)
        if x1 - x - w < 6:
            w = x1 - x
        fh = rnd.randint(lo, hi)
        rh = 5
        top = base - fh
        sunny = sun_x is not None and sun_x > x + w / 2
        for xx in range(x, x + w):
            edge_l, edge_r = xx == x, xx == x + w - 1
            for yy in range(top, base):
                if night:
                    c = W[3] if edge_l else (W[1] if edge_r else W[2])
                elif (edge_r and sunny) or (edge_l and not sunny):
                    c = Lc[5]
                else:
                    c = Lc[3] if (edge_l and sunny) or edge_r else Lc[4]
                fy, fx = yy - top, xx - x
                if 1 <= fx < w - 1 and fy % 3 == 1 and fx % 3 == 1 and yy < base - 1:
                    if night:
                        c = G[5] if rnd.random() < lit else (G[3] if rnd.random() < 0.12 else W[0])
                    else:
                        c = S[2] if fy % 6 == 1 else S[1]
                elif fy == 5 and not edge_l and not edge_r:          # the balcony along the second floor
                    c = K[2] if not night else K[1]
                p.px(xx, yy, c, L)
        for j in range(rh):                                          # the mansard, a pixel in each side
            yy = top - rh + j
            inset = 1 if j < 2 else 0
            for xx in range(x + inset, x + w - inset):
                if night:
                    c = X["moonlit"] if j == 0 else (K[4] if xx == x + inset else K[2])
                else:
                    c = S[5] if j == 0 else (S[4] if xx == x + inset else S[3])
                p.px(xx, yy, c, L)
            if j == 2:
                for dx in range(2, w - 2, 4):                        # dormers
                    p.px(x + dx, yy, (G[4] if rnd.random() < lit else W[0]) if night else Lc[5], L)
                    p.px(x + dx, yy + 1, (W[1] if night else S[1]), L)
        cx_ = x + rnd.randint(1, max(1, w - 4))                      # a chimney stack and its pots
        for yy in range(top - rh - 2, top - rh):
            p.px(cx_, yy, W[3] if night else Lc[3], L)
            p.px(cx_ + 1, yy, W[2] if night else Lc[2], L)
        p.px(cx_, top - rh - 3, RAMP["cocoa"][3] if night else RAMP["rose"][2], L)
        p.px(cx_ + 1, top - rh - 3, RAMP["cocoa"][2] if night else RAMP["cocoa"][4], L)
        x += w


def eiffel(p: Pix, cx, base, h=64, night=False, L="far", motion=True, sparkles=16):
    """The Eiffel Tower across the river: four legs that curve in over an arch to the first platform, a
    lattice tapering to the second and a spire to the top. By day its iron is bronze, lit down the side
    toward the sun; by night it is lit gold from below, and on the hour it sparkles, a scatter of white
    lights coming and going all over it, with the beacon at its top."""
    Cc, G = RAMP["cocoa"], RAMP["gold"]
    lit_, mid_, dark_, lat_ = (G[5], G[4], G[3], G[2]) if night else (Cc[5], Cc[4], Cc[2], Cc[3])
    p1, p2, p3 = round(h * 0.2), round(h * 0.42), round(h * 0.88)

    def hw(t):
        if t < 0.2:
            return 7 + 5.5 * (1 - t / 0.2) ** 1.7
        if t < 0.42:
            return 3.6 + 2.6 * (1 - (t - 0.2) / 0.22) ** 1.3
        if t < 0.88:
            return 0.9 + 2.5 * (1 - (t - 0.42) / 0.46) ** 1.6
        return 0.5

    cells = {}
    for j in range(h):
        t = j / h
        y = base - 1 - j
        half = hw(t)
        for x in range(math.floor(cx - half), math.ceil(cx + half) + 1):
            d = abs(x + 0.5 - cx)
            if d > half + 0.35:
                continue
            leftside = x + 0.5 < cx
            edge = d > half - (1.6 if t < 0.2 else 1.0)
            if t < 0.14:                                           # the arch between the legs
                gap = (half - 2.6) * math.sqrt(max(0.0, 1 - (t / 0.14) ** 2))
                if d < gap:
                    continue
            if j in (p1, p1 + 1, p2, p3):                           # the platforms
                c = mid_ if j != p1 + 1 else dark_
            elif edge:
                c = lit_ if leftside else dark_
            else:
                if (x + y) % 2:
                    continue
                c = lat_
            cells[(x, y)] = c
    for j, extra in ((p1, 2), (p2, 1)):                               # the platforms stand out past the lattice
        y = base - 1 - j
        half = hw(j / h)
        for x in (math.floor(cx - half) - extra, math.ceil(cx + half) + extra):
            for xx in range(min(x, math.floor(cx)), max(x, math.ceil(cx)) + 1):
                if (xx, y) not in cells:
                    cells[(xx, y)] = mid_
    top = base - 1 - h
    for yy in range(top - 4, top + 1):                                # the mast
        cells[(math.floor(cx), yy)] = mid_
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    if not night:
        return
    rnd = random.Random(h)
    spots = [c for c in cells if c[1] < base - 2]
    for i in range(sparkles):                                         # the sparkle, on the hour
        sx, sy = rnd.choice(spots)
        p.px(sx, sy, C["white"], p.twinkle(i) if motion else "near")
    bx, by = math.floor(cx), top - 5
    p.px(bx, by, C["white"], p.twinkle(1) if motion else "near")      # the beacon
    p.halo(bx + 0.5, by + 0.5, 3.2, 3.2, G[5], (0.1, 0.22), L="haze")


def lamp_post(p: Pix, x, base, h=20, night=False, L="base", phase=0):
    """A lamp of the quays in cast iron, its left edge at `x`, 5 wide and `h` tall: a stepped foot, a
    fluted post, a lantern of four panes under a pointed roof and a finial. By night its lantern is lit and
    throws its light round it and down on the stone."""
    K, G, Lc = RAMP["coal"], RAMP["gold"], RAMP["lace"]
    iron = K[3] if not night else K[2]
    edge = K[5] if not night else X["moonlit"]
    for i, c in enumerate((edge, iron, iron, iron, K[1])):
        p.px(x + i, base - 1, c, L)
    for i in range(1, 4):
        p.px(x + i, base - 2, edge if i == 1 else iron, L)
    for yy in range(base - h + 7, base - 2):
        p.px(x + 2, yy, edge if (yy % 3) else iron, L)
    ly = base - h
    p.px(x + 2, ly - 1, iron, L)                                  # finial
    p.hline(x + 1, x + 4, ly, iron, L)                            # roof
    p.hline(x, x + 5, ly + 1, edge, L)
    for yy in range(ly + 2, ly + 6):
        p.px(x, yy, iron, L)
        p.px(x + 4, yy, iron, L)
        for xx in range(x + 1, x + 4):
            if night:
                c = C["white"] if (xx == x + 2 and yy == ly + 3) else (G[6] if xx == x + 1 else G[5])
            else:
                c = Lc[6] if xx == x + 1 else Lc[4]
            p.px(xx, yy, c, L)
    p.hline(x, x + 5, ly + 6, iron, L)
    p.px(x + 2, ly + 7, iron, L)
    if night:
        own = {(xx, yy) for xx in range(x + 1, x + 4) for yy in range(ly + 2, ly + 6)}
        lamp(p, x + 2.5, ly + 4, 13, phase, own)
        p.halo(x + 2.5, ly + 4, 6.5, 6.5, G[5], (0.08, 0.15, 0.24), L=p.flicker(phase, back=True))
        light_pool(p, x + 2.5, base - 0.5, 8, 2.4, night)


# --------------------------------------------------------------------------- the sky
def sun(p: Pix, cx, cy, r, L="base"):
    """A winter sun, low and warm: a disc bright toward its heart, its rim a deeper gold, and a soft glow round it."""
    G = RAMP["gold"]
    p.halo(cx, cy, r * 2.4, r * 2.4, G[5], (0.05, 0.09, 0.14), L="haze")
    for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / r
            if d <= 1:
                p.px(x, y, G[6] if d < 0.5 else (G[5] if d < 0.85 else G[4]), L)


def moon(p: Pix, cx, cy, r, L="base"):
    """A crescent moon, its horns to the right, pale gold and lit along its outer curve, a crater or two
    on it, and a faint glow round it."""
    G, Lc = RAMP["gold"], RAMP["lace"]
    p.halo(cx, cy, r * 2.6, r * 2.6, X["star_pale"], (0.04, 0.07, 0.1), L="haze")
    for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / r
            cut = math.hypot(x + 0.5 - (cx + r * 0.55), y + 0.5 - (cy - r * 0.2)) / (r * 0.86)
            if d <= 1 and cut > 1:
                p.px(x, y, Lc[6] if d > 0.78 else (G[6] if cut > 1.25 else Lc[5]), L)


def _puff_cells(w, h, heart=False):
    if heart:
        return heart_mask(w)
    cells = set()
    r1, r2, r3 = h * 0.42, h * 0.55, h * 0.38
    for y in range(h):
        for x in range(w):
            px_, py_ = x + 0.5, y + 0.5
            puffs = (math.hypot(px_ - w * 0.28, py_ - (h - r1)) <= r1, math.hypot(px_ - w * 0.52, py_ - (h - r2)) <= r2,
                     math.hypot(px_ - w * 0.76, py_ - (h - r3)) <= r3)
            if any(puffs) or (py_ > h - r3 and w * 0.2 < px_ < w * 0.86):
                cells.add((x, y))
    return cells


def cloud(p: Pix, x, y, w, h=None, heart=False, L="haze"):
    """A fair-weather cloud, its top-left at (x, y): round puffs on a flat foot, white on top with a pink
    underside where the low sun reaches it and a pale edge round it. `heart` makes it the one cloud in the
    sky shaped like a heart."""
    h = h or (round(w * 0.9) if heart else max(4, round(w * 0.42)))
    cells = _puff_cells(w, h, heart)
    B, Lc = RAMP["blush"], RAMP["lace"]
    top = min(cy for _, cy in cells)
    bot = max(cy for _, cy in cells)
    for (cx_, cy_) in cells:
        f = (cy_ - top) / max(1, bot - top)
        c = C["white"] if f < 0.55 else (B[6] if f < 0.85 else B[5])
        p.px(x + cx_, y + cy_, c, L)
    for (cx_, cy_) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (cx_ + dx, cy_ + dy)
            if q not in cells:
                p.px(x + q[0], y + q[1], Lc[4] if dy <= 0 else B[5], L)


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
    """A warm light pooled on the ground round its foot: only the runner or the stone takes it."""
    col = col or RAMP["gold"][4]
    if night:
        p.halo(cx, y, rx, ry, col, (0.1, 0.18, 0.27, 0.36), L="pool", only=GROUND)
    else:
        p.halo(cx, y, rx, ry, col, (0.05, 0.09), L="pool", only=GROUND)


# --------------------------------------------------------------------------- motion: petals, hearts, lanterns
def _petal_cluster(seed, night, turn):
    """A little fall of rose petals, six in a 12 by 12 square, as pixels: each a curl two pixels long, lit
    or turned; `turn` flips every petal, the way a petal tumbles as it falls."""
    rnd = random.Random(seed)
    cells = {}
    k = -1 if night else 0
    for _ in range(6):
        x, y = rnd.randrange(0, 11), rnd.randrange(0, 11)
        R = RAMP[rnd.choice(PETALS)]
        lit = rnd.random() < 0.5
        if turn:
            lit = not lit
        a, b = (R[5 + k], R[3 + k]) if lit else (R[4 + k], R[2 + k])
        cells[(x, y)] = a
        cells[(x + (0 if turn else 1), y + (1 if turn else 0))] = b
    return cells


def falling_petals(p: Pix, falls, night, motion=True, z=16):
    """Rose petals coming down: each (x, y, ground, drift, dur, phase, seed) is a little fall that starts at
    (x, y), sways side to side as it drops, every petal tumbling, lands at row `ground` a little to the side
    by `drift`, and is gone, round and round. The still file leaves each where its fall begins."""
    for (x, y, gy, drift, dur, phase, seed) in falls:
        frames = []
        for turn in (False, True):
            key = ("petals", seed, night, turn)
            if key not in p.syms:
                p.symbol(key, _petal_cluster(seed, night, turn))
            frames.append(key)
        if not motion:
            p.use(frames[0], x, y, "near")
            continue
        n = max(14, round((gy - y) / 2.2))
        path = []
        for s in range(n):
            t = s / (n - 1)
            sway = 2.6 * math.sin(2 * math.pi * (t * 1.8 + phase))
            path.append((round(x + drift * t + sway), round(y + (gy - 11 - y) * t)))
        path += [path[-1]] * 2 + [(-30, -30)] * 2
        p.fly(frames, path, dur, z=z, flap=0.3)


def _hearts_cluster(seed, night, beat):
    """Three hearts rising together in a 12 by 14 square, one five pixels across and two three across, red
    and pink; on the `beat` the small ones swell to five and the big one draws in, as a heart beats."""
    rnd = random.Random(seed)
    cells = {}
    k = -1 if night else 0
    spots = [(rnd.randrange(0, 7), rnd.randrange(8, 10)), (rnd.randrange(0, 3), rnd.randrange(0, 3)),
             (rnd.randrange(7, 9), rnd.randrange(3, 6))]
    for i, (x, y) in enumerate(spots):
        R = RAMP[("rose", "blush", "rose")[(i + seed) % 3]]
        big = (i == 0) != beat
        if big:
            art = [".a.b.", "aabbc", "abbbc", ".bcc.", "..c.."]
        else:
            art = ["a.b", "abc", ".c."]
        pal = {"a": R[5 + k], "b": R[4 + k], "c": R[3 + k]}
        for j, row in enumerate(art):
            for ii, ch in enumerate(row):
                if ch in pal:
                    cells[(x + ii, y + j)] = pal[ch]
    return cells


def rising_hearts(p: Pix, rises, night, motion=True, z=16):
    """Hearts drifting up: each (x, y, top, drift, dur, phase, seed) is a little flight of three that starts
    at (x, y), sways as it rises, beating as it goes, to row `top` a little to the side by `drift`, and is
    gone, round and round. The still file leaves each where its flight begins."""
    for (x, y, top, drift, dur, phase, seed) in rises:
        frames = []
        for beat in (False, True):
            key = ("hearts", seed, night, beat)
            if key not in p.syms:
                p.symbol(key, _hearts_cluster(seed, night, beat))
            frames.append(key)
        if not motion:
            p.use(frames[0], x, y, "near")
            continue
        n = max(12, round((y - top) / 2.4))
        path = []
        for s in range(n):
            t = s / (n - 1)
            sway = 2.2 * math.sin(2 * math.pi * (t * 1.4 + phase))
            path.append((round(x + drift * t + sway), round(y - (y - top) * t)))
        path += [(-30, -30)] * 3
        p.fly(frames, path, dur, z=z, flap=0.45)


def _lantern_cells(night, bright):
    """A paper sky lantern, 5 wide and 7 tall, lit from the flame inside it, and its glow round it."""
    G, R = RAMP["gold"], RAMP["rose"]
    art = [".aab.", "aabbc", "abbbc", "abbbc", ".bcc.", "..f..", "....."]
    pal = {"a": G[6], "b": G[5] if bright else G[4], "c": R[5], "f": C["white"]}
    cells = glow_cells(2.5, 3.5, 5.5, 6, G[5], (0.07, 0.13, 0.2) if bright else (0.05, 0.1, 0.15))
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch in pal:
                cells[(i, j)] = pal[ch]
    return {(x + 3, y + 3): c for (x, y), c in cells.items()}


def sky_lanterns(p: Pix, rises, motion=True, z=15):
    """Sky lanterns let go into the night: each (x, y, top, drift, dur, phase) rises slowly from (x, y) to
    row `top`, drifting and swaying, its flame flickering, and is gone. The still file holds each where it
    was let go."""
    frames = []
    for bright in (True, False):
        key = ("lantern", bright)
        if key not in p.syms:
            p.symbol(key, _lantern_cells(True, bright))
        frames.append(key)
    for (x, y, top, drift, dur, phase) in rises:
        if not motion:
            p.use(frames[0], x - 3, y - 3, "near")
            continue
        n = max(14, round((y - top) / 1.6))
        path = []
        for s in range(n):
            t = s / (n - 1)
            sway = 1.6 * math.sin(2 * math.pi * (t * 1.1 + phase))
            path.append((round(x - 3 + drift * t + sway), round(y - 3 - (y - top) * t)))
        path += [(-30, -30)] * 2
        p.fly(frames, path, dur, z=z, flap=0.3)


# --------------------------------------------------------------------------- light that falls on things
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a light at (cx, cy): once everything is drawn, `lamplight` lays its warm light on
    whatever stands within `r` of it, flickering with it. `own` are the light's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def lamplight(p: Pix, night: bool):
    """The finishing pass: each candle's or lamp's light on the drawn things near it, strongest nearest
    the flame. The paper, the sky and the words take none."""
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
    """The shadow a thing standing on the runner leaves right under it: only the ground takes it."""
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


def cells_of(q: Pix, L="base") -> dict:
    """What a scratch drawing holds on one layer, for keeping as a symbol."""
    return dict(q.layers[L]) if L in q.layers else {}


# --------------------------------------------------------------------------- hearts
_HEARTS = {
    3: ["#.#", "###", ".#."],
    5: [".#.#.", "#####", "#####", ".###.", "..#.."],
    7: [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."],
    9: [".###.###.", "#########", "#########", "#########", ".#######.", "..#####..", "...###...", "....#...."],
}


def heart_mask(w: int, h: int | None = None) -> set:
    """The cells of a heart `w` wide with its top-left at (0, 0): the small ones drawn by hand the way pixel
    artists draw them, a larger one as two round lobes and the curved sides that run down from them to
    the point."""
    if w in _HEARTS and h is None:
        return {(x, y) for y, row in enumerate(_HEARTS[w]) for x, ch in enumerate(row) if ch == "#"}
    h = h or round(w * 0.9)
    r = w / 4 + 0.35
    cells = set()
    for y in range(h):
        for x in range(w):
            px_, py_ = x + 0.5, y + 0.5
            lobe = math.hypot(px_ - w / 4, py_ - r) <= r or math.hypot(px_ - 3 * w / 4, py_ - r) <= r
            v = False
            if py_ >= r:
                f = min(1.0, (py_ - r) / max(0.5, h - r))
                v = abs(px_ - w / 2) <= (w / 2) * (1 - f) ** 0.8 + 0.2
            if lobe or v:
                cells.add((x, y))
    return cells


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


def puffy_heart(p: Pix, x, y, w, fam="rose", night=False, L="base", outline=True, lo=1, hi=None):
    """A stuffed satin heart `w` wide, its top-left at (x, y), shaded round from the upper left."""
    R = RAMP[fam]
    ramp = R if not night else R[:-1]
    mask = heart_mask(w)
    return pillow(p, {(x + a, y + b) for a, b in mask}, ramp, L, lo=lo, hi=hi, outline=outline,
                  spec_at=(x + w * 0.27, y + w * 0.22))


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["rose"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)


def tiny_heart(p: Pix, x, y, fam="rose", night=False, L="base", reuse=False):
    """A heart three pixels square, lit on its left lobe."""
    R = RAMP[fam]
    k = -1 if night else 0
    p.sprite(x, y, ["a.b", "abc", ".c."], {"a": R[5 + k], "b": R[4 + k], "c": R[3 + k]}, 1, L, reuse=reuse)


# --------------------------------------------------------------------------- balloons
def heart_balloon(p: Pix, cx, y, fam="rose", night=False, L="base", string=10, w=11, curl=1):
    """A foil balloon in the shape of a heart, `w` wide with its top at row `y`, centred on `cx`: puffed and
    shaded from the upper left, a hard white glint of foil on its left lobe, a darker seam round it; its
    knot under the point and its ribbon hanging `string` pixels in a curl. Returns the column of its knot
    and the row under it."""
    R = RAMP[fam]
    ramp = R if not night else R[:-1]
    mask = heart_mask(w)
    h = max(b for _, b in mask) + 1
    x0 = math.floor(cx) - w // 2
    cells = {(x0 + a, y + b) for a, b in mask}
    pillow(p, cells, ramp, L, lo=1, spec_at=(x0 + w * 0.25, y + h * 0.28))
    gx, gy = x0 + round(w * 0.22), y + 2                     # the foil's glint, a short streak
    for (dx, dy) in ((0, 0), (1, -1), (0, 1)):
        if (gx + dx, gy + dy) in cells:
            p.px(gx + dx, gy + dy, C["white"] if (dx, dy) == (0, 0) else ramp[-1], L)
    kx, ky = math.floor(cx), y + h
    p.px(kx, ky, R[2], L)
    p.px(kx - 1, ky + 1, R[3], L)
    p.px(kx + 1, ky + 1, R[2], L)
    ribbon = RAMP["lace"][3] if not night else RAMP["lace"][2]
    for j in range(string):
        p.px(kx + ((j // 2) % 2) * curl, ky + 2 + j, ribbon, L)
    return kx, ky + 2


# --------------------------------------------------------------------------- roses
ROSE = {
    5: [".e.a.", "abdbc", "bddbc", ".bcc.", "..g.."],
    7: [".ae.ea.", "aebdbac", "abddbbc", "bbdbdcc", ".cbbcc.", "..ccc..", ".g.g.g."],
}


def rose(p: Pix, x, y, fam="rose", night=False, L="base", size=5):
    """A rose in bloom seen from the side, `size` wide with its top-left at (x, y): the outer petals cupped
    and lit on the left, the inner ones curling in a darker spiral, the green sepals under it."""
    R, G = RAMP[fam], RAMP["leaf"]
    k = -1 if night else 0
    pal = {"a": R[5 + k], "e": R[6 + k], "b": R[4 + k], "c": R[3 + k], "d": R[2 + k], "g": G[3 + k]}
    p.sprite(x, y, ROSE[size], pal, 1, L)


def a_rose(p: Pix, x, y, night=False, L="base", fam="rose"):
    """A single long-stemmed rose, its bloom's top-left at (x, y): the bloom seven wide, a stem and a leaf."""
    rose(p, x, y, fam, night, L, 7)
    G = RAMP["leaf"]
    k = -1 if night else 0
    for yy in range(y + 7, y + 11):
        p.px(x + 3, yy, G[3 + k], L)
    p.px(x + 4, y + 8, G[5 + k], L)
    p.px(x + 5, y + 8, G[4 + k], L)
    p.px(x + 5, y + 7, G[5 + k], L)


def vase_of_roses(p: Pix, cx, base, night=False, L="base", n=5):
    """A bud vase of red roses standing on row `base`, centred on `cx`: a glass vase, its water line and the
    stems seen through it, bright down its left side; the stems rising out of its neck and fanning to a dome
    of blooms, red and one pink, leaves along them and sprigs of baby's breath between. About 13 wide and
    30 tall."""
    S, G, Lc = RAMP["silver"], RAMP["leaf"], RAMP["lace"]
    k = -1 if night else 0
    cx = math.floor(cx)
    rows = [7, 5, 5, 7, 9, 9, 9, 9, 7, 5]                    # the vase, top to foot
    top = base - len(rows)
    water = top + 4
    for j, w_ in enumerate(rows):
        yy = top + j
        x0 = cx - w_ // 2
        for i in range(w_):
            xx = x0 + i
            edge = i == 0 or i == w_ - 1 or j == 0 or j == len(rows) - 1
            if edge:
                c = (S[5] if i <= 1 else S[3]) if not night else (S[4] if i <= 1 else S[2])
            elif yy >= water:
                c = (S[6] if i == 1 else S[5]) if not night else (S[4] if i == 1 else S[3])
                if xx in (cx - 1, cx + 1) and j < len(rows) - 2:
                    c = G[4 + k]
            else:
                c = (Lc[6] if i == 1 else Lc[5]) if not night else (S[3] if i == 1 else S[2])
            p.px(xx, yy, c, L)
    blooms = [(-7, -24, 5, "rose"), (-2, -29, 7, "rose"), (4, -25, 5, "blush"), (-5, -20, 7, "rose"),
              (2, -20, 7, "rose")][:n]
    stems = {}
    for (dx, dy, s, _) in blooms:
        _line(stems, cx + dx + s // 2, base + dy + s, cx, top + 1)
    for (sx, sy) in stems:
        p.px(sx, sy, G[3 + k], L)
    for i, (dx, dy, s, _) in enumerate(blooms):                 # a leaf on each stem, alternately left and right
        sx, sy = cx + dx + s // 2, base + dy + s + 2
        d = -1 if i % 2 == 0 else 1
        for (lx, ly, t) in ((d, 0, 5), (2 * d, -1, 4), (d, -1, 5), (2 * d, 0, 3)):
            p.px(sx + lx, sy + ly, G[t + k], L)
    for (dx, dy) in ((-9, -19), (8, -21), (-4, -25), (6, -28), (-8, -27)):   # baby's breath
        p.px(cx + dx, base + dy, Lc[6] if not night else Lc[4], L)
        p.px(cx + dx + 1, base + dy - 1, Lc[5] if not night else Lc[3], L)
        p.px(cx + dx + 1, base + dy + 1, G[4 + k], L)
    for (dx, dy, s, fam) in sorted(blooms, key=lambda b: b[1]):
        rose(p, cx + dx, base + dy, fam, night, L, s)


# --------------------------------------------------------------------------- chocolates
def truffle(p: Pix, x, y, kind=0, night=False, L="base"):
    """A chocolate truffle in its paper cup, 5 wide and 4 tall, top-left at (x, y): dark, milk or white,
    lit on its crown, a drizzle across it, the cup pleated gold."""
    Co, G, Lc = RAMP["cocoa"], RAMP["gold"], RAMP["lace"]
    k = -1 if night else 0
    body = [(Co[2 + k], Co[1], Co[3 + k]), (Co[4 + k], Co[3 + k], Co[5 + k]), (Lc[5 + k], Lc[3 + k], Lc[6 + k])][kind]
    art = [".chb.", "cbbba", "gGgGg", ".gGg."]
    p.sprite(x, y, art, {"a": body[1], "b": body[0], "c": body[0], "h": body[2], "g": G[3 + k], "G": G[5 + k]}, 1, L)


def chocolate_box(p: Pix, x, base, night=False, L="base"):
    """A heart-shaped box of chocolates standing open on row `base`, its left edge at `x`, about 21 wide: its
    lid of red satin leaning behind it, puffed and tied with a pink bow; the box seen from above, its gold
    rim bright on the near side, its satin well holding truffles, dark, milk and white, in gold cups; its
    side wall red, lit on the left."""
    R, G, B = RAMP["rose"], RAMP["gold"], RAMP["blush"]
    k = -1 if night else 0
    ramp = R if not night else R[:-1]
    lid = {(x + 2 + a, base - 22 + b) for a, b in heart_mask(15)}
    pillow(p, lid, ramp, L, lo=1, spec_at=(x + 5.5, base - 19.5))
    for (bx, by, c) in ((8, -21, B[4 + k]), (7, -22, B[5 + k]), (9, -22, B[3 + k]), (6, -21, B[5 + k]),   # its bow
                        (10, -21, B[3 + k]), (8, -20, B[3 + k]), (7, -19, B[4 + k]), (9, -19, B[3 + k])):
        p.px(x + 1 + bx, base + by, c, L)
    w, h = 21, 10
    top = base - 4 - h
    mask = {(a, round(b * h / 18)) for a, b in heart_mask(w, 18)}
    n4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
    inner = {(a, b) for (a, b) in mask if all((a + dx, b + dy) in mask for dx, dy in n4)}
    for (a, b) in mask:                                           # the wall below the rim
        if (a, b + 1) not in mask:
            for j in range(1, 5):
                c = R[4 + k] if a < w * 0.3 else (R[3 + k] if a < w * 0.7 else R[2 + k])
                if j == 4:
                    c = G[3 + k]
                p.px(x + a, top + b + j, c, L)
    for (a, b) in mask:
        if (a, b) in inner:
            c = R[1 + k] if b < 3 else R[2 + k]
        else:
            c = G[5 + k] if b > h * 0.45 else G[4 + k]
        p.px(x + a, top + b, c, L)
    for i, (a, b) in enumerate(((5, 2), (10, 3), (3, 5), (8, 6), (13, 5), (15, 2), (10, 8))):
        if all((a + dx, b + dy) in inner for dx in range(5) for dy in range(3)):
            truffle(p, x + a, top + b - 1, (i * 2) % 3, night, L)


# --------------------------------------------------------------------------- a teddy bear
def teddy(p: Pix, cx, base, night=False, L="base", heart_fam="rose"):
    """A teddy bear sitting on row `base`, centred on `cx`, about 15 wide and 17 tall: round ears with pink
    insides, a paler muzzle and a dark nose, button eyes, a round body and two paws held in front of it
    round a red satin heart, and his feet out with pale pads, all shaded from the upper left."""
    Co, B = RAMP["cocoa"], RAMP["blush"]
    k = -1 if night else 0
    fur = Co if not night else Co[:-1]
    cx = math.floor(cx) + 0.5
    for sx in (-5, 5):                                            # feet, pads to us
        sphere(p, cx + sx, base - 2.5, 2.3, fur, L=L, lo=1, hi=5, spec=False)
    sphere(p, cx, base - 7, 5.2, fur, L=L, lo=1, hi=5, spec=False)                     # body
    for sx in (-5, 5):
        p.px(math.floor(cx + sx), base - 2, Co[6 + k], L)
        p.px(math.floor(cx + sx) + (1 if sx > 0 else -1), base - 2, Co[5 + k], L)
    for sx in (-4, 4):                                            # ears
        sphere(p, cx + sx, base - 16.5, 1.9, fur, L=L, lo=1, hi=5, spec=False)
        p.px(math.floor(cx + sx), base - 17, B[4 + k], L)
    sphere(p, cx, base - 13, 4.3, fur, L=L, lo=2, hi=6 if not night else 5, spec=True)   # head
    for (dx, dy, t) in ((-1, -12, 6), (0, -12, 6), (1, -12, 5), (-2, -11, 5), (-1, -11, 6), (0, -11, 6), (1, -11, 5),
                        (2, -11, 4), (-1, -10, 5), (0, -10, 5), (1, -10, 4)):
        p.px(math.floor(cx) + dx, base + dy, Co[t + k], L)                                # muzzle
    p.px(math.floor(cx), base - 12, Co[1], L)                                            # nose
    p.px(math.floor(cx) - 1, base - 12, Co[0], L)
    for ex in (-2, 2):                                                                   # eyes
        p.px(math.floor(cx) + ex, base - 14, C["coal"], L)
    p.px(math.floor(cx) - 2, base - 15, Co[6 + k], L)
    puffy_heart(p, math.floor(cx) - 3, base - 9, 7, heart_fam, night, L)
    for sx in (-4, 3):                                                                   # paws round the heart
        sphere(p, cx + sx + 0.5, base - 7.5, 1.6, fur, L=L, lo=2, hi=5, spec=False, outline=False)


# --------------------------------------------------------------------------- gifts and letters
def gift_box(p: Pix, x, base, w=11, h=8, fam="blush", ribbon="rose", night=False, L="base"):
    """A present standing on row `base`, its left edge at `x`: a box `w` wide and `h` tall in `fam` paper
    lit down its left, a lid a pixel wider, a satin ribbon tied round both ways and a bow on top with its
    two loops and tails."""
    P, Rb = RAMP[fam], RAMP[ribbon]
    k = -1 if night else 0
    top = base - h
    mid = x + w // 2
    for yy in range(top + 2, base):
        for xx in range(x, x + w):
            c = P[4 + k] if xx < x + 2 else (P[3 + k] if xx < x + w - 2 else P[2 + k])
            if xx in (mid - 1, mid):
                c = Rb[4 + k] if xx == mid - 1 else Rb[3 + k]
            p.px(xx, yy, c, L)
    for yy in (top, top + 1):                                       # the lid
        for xx in range(x - 1, x + w + 1):
            c = P[5 + k] if yy == top else P[3 + k]
            if xx in (mid - 1, mid):
                c = Rb[5 + k] if yy == top else Rb[3 + k]
            p.px(xx, yy, c, L)
    bow = ["aa...bb", "abakbcb", ".aakbb.", "..c.c.."]
    p.sprite(mid - 4, top - 3, bow, {"a": Rb[5 + k], "b": Rb[4 + k], "k": Rb[2 + k], "c": Rb[3 + k]}, 1, L)


def love_letter(p: Pix, x, y, night=False, L="base", w=11, h=7, seal="rose"):
    """A love letter in its envelope, its top-left at (x, y): cream paper with a pale edge, the flap's fold
    running in from both top corners to a red wax seal in the shape of a heart."""
    Lc = RAMP["lace"]
    k = -1 if night else 0
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            edge = yy in (y, y + h - 1) or xx in (x, x + w - 1)
            c = (Lc[3 + k] if not night else Lc[2]) if edge else (Lc[6] if not night else Lc[4])
            p.px(xx, yy, c, L)
    mx = x + w // 2
    for i in range(1, w // 2):
        yy = y + round(i * (h - 3) / (w // 2))
        p.px(x + i, yy, Lc[4] if not night else Lc[3], L)
        p.px(x + w - 1 - i, yy, Lc[4] if not night else Lc[3], L)
    tiny_heart(p, mx - 1, y + h - 4, seal, night, L)


def lovebirds(p: Pix, x, y, night=False, L="base"):
    """Two lovebirds on a twig, beak to beak, their top-left at (x, y), 17 wide and 9 tall: green backs lit
    along the top, peach faces, red beaks, a black eye ringed pale, long dark tails; and a little heart
    rising between them."""
    G, R, Co, Lc = RAMP["leaf"], RAMP["rose"], RAMP["cocoa"], RAMP["lace"]
    k = -1 if night else 0
    bird = ["...FFf..",
            "..FffFf.",
            ".gFfwef.",
            "gGGffffb",
            "gGGGgff.",
            ".gGgggg.",
            "..tgg...",
            ".tt....."]
    pal = {"F": R[6 + k], "f": R[5 + k], "e": C["coal"], "w": Lc[6 + k], "b": R[3 + k], "g": G[4 + k],
           "G": G[5 + k], "t": G[2 + k]}
    p.sprite(x, y + 1, bird, pal, 1, L)
    p.sprite(x + 9, y + 1, bird, pal, 1, L, flip=True)
    p.hline(x - 1, x + 18, y + 9, Co[3 + k], L)
    p.hline(x + 2, x + 6, y + 9, Co[4 + k], L)
    p.px(x + 13, y + 10, Co[3 + k], L)
    tiny_heart(p, x + 7, y - 3, "rose", night, L)


# --------------------------------------------------------------------------- candles
def candle(p: Pix, x, base, h=8, night=False, L="base", motion=True, phase=0, fam="lace", w=3, holder=True):
    """A candle standing on row `base`, its left edge at `x`, `w` wide and `h` tall in `fam` wax lit down its
    left, a drip of wax from its rim, its wick and a flame of three pixels, white at its heart and gold at
    its tip, flickering; a gold saucer under it. By night its light falls warm on what stands near."""
    Wx, G = RAMP[fam], RAMP["gold"]
    k = -1 if night else 0
    foot = base - (1 if holder else 0)
    top = foot - h
    for yy in range(top, foot):
        for i in range(w):
            c = Wx[5 + k] if i == 0 else (Wx[4 + k] if i < w - 1 else Wx[3 + k])
            if yy == top:
                c = Wx[6 + k] if i < w - 1 else Wx[4 + k]
            p.px(x + i, yy, c, L)
    p.px(x + w - 1, top + 1, Wx[6 + k], L)                             # a drip from the rim
    p.px(x + w - 1, top + 2, Wx[5 + k], L)
    wx = x + w // 2
    p.px(wx, top - 1, RAMP["coal"][2], L)
    Lf = p.flicker(phase) if motion else L
    for (dy, c) in ((-2, C["white"]), (-3, G[6]), (-4, G[5])):
        p.px(wx, top + dy, c, Lf)
    p.px(wx - 1, top - 2, G[5] + ":0.6", Lf)
    p.px(wx + 1, top - 2, G[4] + ":0.5", Lf)
    if holder:
        p.hline(x - 1, x + w + 1, base - 1, G[4 + k], L)
        p.px(x - 1, base - 1, G[5 + k], L)
    own = {(wx, top + dy) for dy in (-2, -3, -4)}
    lamp(p, wx + 0.5, top - 2.5, 11 if night else 7, phase, own)
    if night:
        p.halo(wx + 0.5, top - 2.5, 4.5, 5.5, G[5], (0.08, 0.16, 0.26),
               L=p.flicker(phase, back=True) if motion else "haze")


# --------------------------------------------------------------------------- conversation hearts
CANDY = {"blush": 5, "lilac": 5, "leaf": 6, "gold": 6, "lace": 6}


def candy_heart(p: Pix, x, y, word, fam="blush", night=False, L="base", w=None, foot=None):
    """A conversation heart, its top-left at (x, y), or standing with its point on row `foot`: chalky pastel
    candy, pale where the light falls and a tone deeper round its edge, and its word pressed into it in
    small wine capitals, on two lines when it has two words. Returns its width."""
    R = RAMP[fam]
    lines = word.split(" ") if " " in word else [word]
    tw = max(Pix.measure(s, "35") for s in lines)
    th = 6 * len(lines) - 1

    def fits(w_):
        m = heart_mask(w_)
        h_ = max(b for _, b in m) + 1
        ty_ = max(2, (h_ - th) // 2 - 1)
        for i, s in enumerate(lines):
            sw = Pix.measure(s, "35")
            x0_ = (w_ - sw) // 2
            for yy in range(ty_ + i * 6 - 1, ty_ + i * 6 + 6):
                if not all((xx, yy) in m for xx in range(x0_ - 1, x0_ + sw + 1)):
                    return None
        return ty_

    w = w or max(11, tw + 4 + (tw + 4 + 1) % 2)
    while fits(w) is None:
        w += 2
    mask = heart_mask(w)
    if foot is not None:
        y = foot - (max(b for _, b in mask) + 1)
    t = CANDY.get(fam, 5)
    cells = {(x + a, y + b) for a, b in mask}
    for (cx_, cy_) in cells:
        edge = any((cx_ + dx, cy_ + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        lit = (cx_ - x) + (cy_ - y) < w * 0.45
        p.px(cx_, cy_, R[t - 1] if edge else (R[min(6, t + 1)] if lit and t < 6 else R[t]), L)
    ty = y + fits(w)
    for i, s in enumerate(lines):
        p.text(x + (w - Pix.measure(s, "35")) // 2, ty + i * 6, s, RAMP["rose"][1], "35", L=L)
    return w


# --------------------------------------------------------------------------- Cupid
SKIN = [RAMP["cocoa"][3], RAMP["cocoa"][5], RAMP["rose"][6], RAMP["blush"][6], RAMP["lace"][5], RAMP["lace"][6]]


def _wing(q: Pix, x, y, up, night):
    """Cupid's wing at his shoulder (x, y): three rows of white feathers with pale lines between them,
    raised or lowered."""
    Lc = RAMP["lace"]
    W = C["white"] if not night else Lc[5]
    edge = Lc[2] if not night else Lc[3]
    line = Lc[4] if not night else Lc[3]
    art = (["...ee..", "..eWWe.", ".eWlWWe", "eWlWlWe", "eWWlWe.", ".eWWe..", "..ee..."] if up else
           ["..eee..", ".eWWWe.", "eWlWlWe", "eWWlWWe", ".eWWlWe", "..eWWe.", "...ee.."])
    q.sprite(x - 6, y - (6 if up else 2), art, {"e": edge, "W": W, "l": line})


def cupid_cells(frame: str, night=False) -> dict:
    """Cupid as pixels, 22 by 18, facing right: a chubby cherub with golden curls, rosy cheeks and a red sash,
    a white wing at his back raised or lowered, and his golden bow held out in front. `frame` is "up" or
    "down" for the wing, "aim" with an arrow nocked and the string drawn ("aim2" the same with the wing
    lowered), or "loosed" with the string back and the arrow gone."""
    q = Pix(24, 20)
    G, R, Co = RAMP["gold"], RAMP["rose"], RAMP["cocoa"]
    k = -1 if night else 0
    skin = SKIN if not night else [RAMP["cocoa"][2]] + SKIN[:-1]
    _wing(q, 8, 8, frame not in ("down", "aim2"), night)
    sphere(q, 9.5, 12, 3.4, skin, lo=1, hi=5, spec=False)                     # body
    for (dx, dy) in ((-2, 16), (-1, 16), (-3, 15), (1, 16), (2, 16)):          # legs tucked up
        q.px(9 + dx, dy, skin[3], "base")
    q.px(6, 16, skin[1], "base")
    q.px(10, 17, skin[2], "base")
    for (dx, dy) in ((8, 10), (9, 11), (10, 12), (11, 13), (12, 13)):         # the sash
        q.px(dx, dy, R[4 + k], "base")
    q.px(7, 10, R[5 + k], "base")
    sphere(q, 10.5, 5.5, 3.7, skin, lo=1, hi=5, spec=True)                     # head
    for (dx, dy, t) in ((7, 2, 5), (8, 1, 4), (9, 1, 5), (10, 1, 5), (11, 1, 4), (12, 1, 5), (13, 2, 4), (7, 3, 4),
                        (8, 2, 3), (10, 2, 3), (12, 2, 3), (6, 4, 4), (6, 5, 3), (7, 6, 3), (14, 3, 3), (9, 0, 4),
                        (11, 0, 5)):
        q.px(dx, dy, G[t + k], "base")                                         # curls
    q.px(12, 5, C["coal"], "base")                                             # eye
    q.px(13, 7, R[5 + k], "base")                                              # cheek
    q.px(14, 6, skin[2], "base")
    hand_y = 10
    for xx in range(12, 16):                                                   # the arm out to the bow
        q.px(xx, hand_y, skin[4] if xx < 14 else skin[3], "base")
    q.px(16, hand_y, skin[4], "base")
    bow_x = 17
    for yy in range(3, 18):                                                    # the bow, a golden arc
        off = round(2.6 * math.sin(math.pi * (yy - 3) / 14))
        q.px(bow_x + off, yy, G[5 + k] if yy < 10 else G[4 + k], "base")
    q.px(bow_x, 3, G[3 + k], "base")
    q.px(bow_x, 17, G[3 + k], "base")
    string = Co[5] if not night else RAMP["lace"][3]
    pull = 13 if frame in ("aim", "aim2") else bow_x
    for yy in range(4, 17):
        f = 1 - abs(yy - hand_y) / (hand_y - 4 if yy < hand_y else 16 - hand_y)
        q.px(round(bow_x + (pull - bow_x) * max(0.0, f)), yy, string, "base")
    if frame in ("aim", "aim2", "up", "down"):
        aim = frame in ("aim", "aim2")
        arrow_cells(q, 13 if aim else 16, hand_y, 10 if aim else 7, night)
    return cells_of(q)


def arrow_cells(q: Pix, x, y, length, night=False, L="base"):
    """Cupid's arrow pointing right from its tail at (x, y): pink fletching, a gilt shaft and a red heart
    for its head."""
    G, R, B = RAMP["gold"], RAMP["rose"], RAMP["blush"]
    k = -1 if night else 0
    q.px(x, y - 1, B[5 + k], L)
    q.px(x, y + 1, B[4 + k], L)
    q.px(x + 1, y - 1, B[4 + k], L)
    q.px(x + 1, y + 1, B[3 + k], L)
    for xx in range(x, x + length):
        q.px(xx, y, G[4 + k] if (xx - x) % 3 else G[5 + k], L)
    hx = x + length
    for (dx, dy, t) in ((0, -1, 5), (1, -1, 4), (0, 0, 4), (1, 0, 4), (2, 0, 3), (0, 1, 3), (1, 1, 3)):
        q.px(hx + dx, y + dy, R[t + k], L)
    q.px(hx + 1, y - 2, R[5 + k], L)
    q.px(hx - 1, y - 2, R[5 + k], L)


def cupid(p: Pix, x, y, frame="up", night=False, L="base"):
    """Cupid, his top-left at (x, y): see `cupid_cells`."""
    key = ("cupid", frame, night)
    if key not in p.syms:
        p.symbol(key, cupid_cells(frame, night))
    p.use(key, x, y, L)
    return key


# --------------------------------------------------------------------------- seals and marks
def wax_seal(p: Pix, cx, cy, r, night=False, L="base", seed=4):
    """A seal of red wax, round but for the bumps where the wax spread, lit on its upper left, its pressed
    face a ring a tone darker, and a heart standing proud in the middle."""
    R = RAMP["rose"]
    ramp = R if not night else R[:-1]
    rnd = random.Random(seed)
    bumps = [rnd.uniform(-0.6, 0.7) for _ in range(12)]
    cells = set()
    for y in range(math.floor(cy - r - 2), math.ceil(cy + r + 2)):
        for x in range(math.floor(cx - r - 2), math.ceil(cx + r + 2)):
            a = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
            rr = r + bumps[int((a + math.pi) / (2 * math.pi) * 12) % 12]
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= rr:
                cells.add((x, y))
    pillow(p, cells, ramp, L, lo=1)
    ring = r * 0.68
    for (x, y) in cells:
        d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
        if abs(d - ring) < 0.55:
            p.px(x, y, ramp[2] if (x + 0.5 - cx) + (y + 0.5 - cy) > 0 else ramp[3], L)
    hw = 5 if r < 6 else 7
    mask = heart_mask(hw)
    hh = max(b for _, b in mask) + 1
    hx, hy = math.floor(cx) - hw // 2, math.floor(cy) - hh // 2
    for (a, b) in mask:
        edge = any((a + dx, b + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        lit = a + b < hw * 0.6
        p.px(hx + a, hy + b, (ramp[5] if lit else ramp[2]) if edge else ramp[4], L)


# --------------------------------------------------------------------------- what moves in a header
def bobbing(p: Pix, motion, name="bob0", lift=(0, 0, 1, 2, 2, 1), dur=3.0):
    """A layer that rises and settles a pixel or two, round and round: how a balloon rides the air. A still
    drawing has no such layer, and what would ride it stands still."""
    return p.layer(name, ("bob", list(lift), dur)) if motion else "base"


def tether(p: Pix, x0, y0, x1, y1, night, L="base", tail=3):
    """A balloon's ribbon from its knot at (x0, y0) down to where it is tied at (x1, y1), in a gentle curve;
    on a bobbing layer the last few pixels are drawn again still, so the ribbon never parts from the knot."""
    col = RAMP["lace"][3] if not night else RAMP["lace"][2]
    n = max(2, y1 - y0)
    pts = []
    for j in range(n + 1):
        t = j / n
        pts.append((round(x0 + (x1 - x0) * t + 1.4 * math.sin(math.pi * t)), y0 + j))
    for (xx, yy) in pts:
        p.px(xx, yy, col, L)
    if L != "base":
        for (xx, yy) in pts[-tail:]:
            p.px(xx, yy, col, "base")


def wavy(x0, y0, x1, y1, n, amp=3, turns=1.0):
    """A path of `n` steps from (x0, y0) to (x1, y1), swaying up and down `amp` pixels."""
    return [(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + amp * math.sin(2 * math.pi * turns * t)))
            for t in (s / (n - 1) for s in range(n))]


def cupid_flies(p: Pix, path, night, motion, dur=9.0):
    """Cupid on the wing across the sky, his wing beating as he goes, along `path` and out of the sheet,
    round and round; the still file holds him at the path's first point."""
    frames = []
    for f in ("up", "down"):
        key = ("cupid", f, night)
        if key not in p.syms:
            p.symbol(key, cupid_cells(f, night))
        frames.append(key)
    if not motion:
        p.use(frames[0], *path[0], "near")
        return
    p.fly(frames, path, dur, z=17, flap=0.3)


def perched_cupid(p: Pix, x, y, night, motion, dur=0.8):
    """Cupid sitting on a cloud with his bow drawn, his top-left at (x, y), his wing beating in a moving
    file; the cloud is white with a pink underside by day, and plum, lit along its top by the moon, by
    night."""
    if night:
        W = RAMP["wine"]
        cells = {(a_, b_) for a_, b_ in ((i, j) for j in range(6) for i in range(26))
                 if math.hypot((a_ - 12.5) / 13, (b_ - 3) / 3.4) <= 1 or (b_ >= 3 and 2 <= a_ <= 23)}
        for (a_, b_) in cells:
            p.px(x - 2 + a_, y + 15 + b_, W[5] if b_ <= 1 else (W[4] if b_ < 4 else W[3]))
    else:
        cloud(p, x - 2, y + 14, 26, 7, L="base")
    if motion:
        cupid(p, x, y, "aim", night, L=p.seq("cw0", 0.0, 0.5, dur, keep=True, z=1))
        cupid(p, x, y, "aim2", night, L=p.seq("cw1", 0.5, 1.0, dur, z=1))
    else:
        cupid(p, x, y, "aim", night)


# --------------------------------------------------------------------------- the footers' and elements' pieces
def candy_ribbon(p: Pix, x0, y0, w, h, period=5):
    """A bar striped like a length of candy ribbon, red and white, `period` pixels a stripe: lit along the
    top, shaded along the bottom."""
    R, Lc = RAMP["rose"], RAMP["lace"]
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
        for xx in range(x0, x0 + w):
            red = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (R[5], R[4], R[3])[band] if red else (Lc[6], Lc[5], Lc[4])[band])


def ribbon_bar(p: Pix, bx, base, bw, v, night, edge):
    """A week's commits as a length of red satin ribbon hung to its count, `bw` wide and `v` tall on row
    `base`: round in the light from the left, a sheen down it, its top cut with pinking shears, and a thread
    of `edge` round it."""
    R = RAMP["rose"]
    kk = -1 if night else 0
    for xx in range(bx, bx + bw):
        nx = 2 * (xx - bx + 0.5) / bw - 1
        lam = max(0.0, nx * LX + math.sqrt(1 - nx * nx) * LZ)
        for yy in range(base - v, base):
            c = R[max(1, min(6, round(2.6 + 2.6 * lam) + kk))]
            if yy == base - v and (xx - bx) % 2 == 1:
                c = R[2 + kk]                              # the pinked edge
            p.px(xx, yy, c)
    for xx in range(bx - 1, bx + bw + 1):
        if xx in (bx - 1, bx + bw):
            p.vline(xx, base - v, base, edge)
        else:
            p.px(xx, base - v - 1, edge)


def clock_ring(p: Pix, cx, cy, r0, r1, night):
    """The upper half of a clock's face as a dial, between radii r0 and r1: a cream face lit on its left,
    a gold bezel round it bright along its upper left, and a tick at every hour of the half turn."""
    G, Lc = RAMP["gold"], RAMP["lace"]
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
                c = Lc[(6 if dx < -r1 * 0.2 else 5) + k]
                f = th / (math.pi / 6)
                if abs(f - round(f)) < 0.09 and rho > r1 - 6:
                    c = RAMP["rose"][2]                        # an hour's tick
            p.px(xx, yy, c)


def boss(p: Pix, cx, cy):
    """The gold boss the dial's hand turns on, a cross of five pixels lit from the upper left."""
    G = RAMP["gold"]
    for (dx, dy, t) in ((0, 0, 6), (-1, 0, 5), (1, 0, 4), (0, -1, 5), (0, 1, 3)):
        p.px(cx + dx, cy + dy - 1, G[t])


def cloth(i, xx, yy, y0, lift):
    """The colour of the `i`-th cloth of a sweetheart's dress at (xx, yy), in a bar whose top is row `y0`,
    `lift` tones lighter on its lit top row and darker down its foot: red satin with a sheen running across
    it, pink lace pierced in a grid, chocolate velvet with a nap, cream silk woven in a check."""
    R, B, Co, Lc = RAMP["rose"], RAMP["blush"], RAMP["cocoa"], RAMP["lace"]
    kind = i % 4
    if kind == 0:
        c = R[5] if (xx - yy) % 9 in (0, 1) else R[4]
    elif kind == 1:
        c = B[4] if (xx % 3 == 1) and ((yy - y0) % 3 == 1) else B[5]
    elif kind == 2:
        c = Co[3] if (xx + yy * 3) % 7 else Co[4]
    else:
        c = Lc[5] if ((xx + yy) // 3) % 2 == 0 else Lc[4]
    return step(c, lift)


def flip_tile(q: Pix, ox, oy):
    """One counter's tile on a flip clock, 11 by 15, in plum lacquer: its upper leaf a shade lighter than its
    lower, split by the hinge across its middle, lit along its top edge, a gold pin at each end of the hinge."""
    W = RAMP["wine"]
    for yy in range(15):
        for xx in range(11):
            c = W[3] if yy < 7 else W[2]
            if yy == 0:
                c = W[5]
            if yy == 7:
                c = W[0]
            if xx == 10 or yy == 14:
                c = W[1]
            q.px(ox + xx, oy + yy, c)
    q.px(ox, oy + 7, RAMP["gold"][4])
    q.px(ox + 9, oy + 7, RAMP["gold"][4])


def twine(p: Pix, x0, x1, y, night):
    """The cord the releases hang from: red and white baker's twine, its two strands twisting every two
    pixels, a shade darker underneath."""
    R, Lc = RAMP["rose"], RAMP["lace"]
    kk = -1 if night else 0
    for x in range(x0, x1):
        red = (x // 2) % 2 == 0
        p.px(x, y, R[4 + kk] if red else Lc[6 + kk])
        p.px(x, y + 1, R[2 + kk] if not red else Lc[4 + kk])


CHARMS = ("rose", "blush", "lilac", "rose")


def charm(p: Pix, x, gy, kind, night, i=0, ink=None):
    """A release hanging from the baker's twine on row `gy` like a charm: a stuffed heart in its colour for
    a release, a bigger one of gold for a big release, a red bead for a patch, for one still to come a heart
    drawn in outline in `ink`, not yet filled, and for the repository's creation the love letter it began
    with. By night the hearts glow a little in the lamplight."""
    Lc = RAMP["lace"]
    kk = -1 if night else 0
    hook = Lc[3] if not night else Lc[2]
    if kind in ("big", "major"):
        fam = "gold" if kind == "big" else CHARMS[i % 4]
        w_ = 9 if kind == "big" else 7
        p.px(x + 1, gy + 2, hook)
        puffy_heart(p, x + 1 - w_ // 2, gy + 3, w_, fam, False)          # lit by the lamps, bright by night too
        if night:
            skip = {(x + 1 - w_ // 2 + a, gy + 3 + b) for a, b in heart_mask(w_)}
            for (qx, qy), c in glow_cells(x + 1.5, gy + 3 + w_ * 0.42, w_ * 0.72, w_ * 0.72, RAMP[fam][5],
                                          (0.12, 0.22), skip).items():
                p.px(qx, qy, c, "haze")
    elif kind == "minor":
        R = RAMP[CHARMS[i % 4]]
        p.px(x, gy + 2, hook)
        p.px(x, gy + 3, R[5 + kk])
        p.px(x + 1, gy + 3, R[4 + kk])
        p.px(x, gy + 4, R[3 + kk])
    elif kind == "made":
        p.px(x + 1, gy + 2, hook)
        love_letter(p, x - 2, gy + 3, night, w=7, h=6)
    else:
        p.px(x + 1, gy + 2, hook)
        p.sprite(x - 1, gy + 3, [".#.#.", "#.#.#", "#...#", ".#.#.", "..#.."], {"#": ink})


def doily(p: Pix, cx, cy, r, night, n=22):
    """A paper lace doily behind the certificate's disc: a ring of `n` scallops round a radius `r`, pierced
    with a ring of eyelets, pale where the light falls on its upper left."""
    Lc, B = RAMP["lace"], RAMP["blush"]
    k = -1 if night else 0
    for yy in range(math.floor(cy - r - 3), math.ceil(cy + r + 3)):
        for xx in range(math.floor(cx - r - 3), math.ceil(cx + r + 3)):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            f = (math.atan2(dy, dx) + math.pi) / (2 * math.pi / n)
            within = f - math.floor(f)
            edge = r + 2.2 * math.sqrt(max(0.0, 1 - (within * 2 - 1) ** 2))
            if rho > edge or rho < r - 7:
                continue
            lit = -(dx * LX + dy * LY) / r
            c = Lc[6 + k] if lit > 0.2 else (Lc[5 + k] if lit > -0.4 else Lc[4 + k])
            if rho > edge - 1:
                c = Lc[3 + k] if lit < 0 else Lc[4 + k]
            ring = (r - 2.5) - rho
            if abs(ring) < 0.8 and abs(within - 0.5) < 0.22:
                c = B[4 + k]                                   # an eyelet
            p.px(xx, yy, c)


SWEETHEARTS = (("rose", 1, 4, False), ("gold", 3, 6, True), ("lilac", 1, 4, False))


def sweetheart(p: Pix, cx, cy, i, initials, night):
    """A contributor as a sweetheart, centred on (cx, cy): a stuffed satin heart in the `i`-th of red, gold
    and lilac with their initials on it, white with a shadow or, on the gold, dark; with no initials (a
    bot), a love letter sealed with a heart, the way its pull requests arrive."""
    cx, cy = round(cx), round(cy)
    if not initials:
        love_letter(p, cx - 7, cy - 3, night, w=15, h=11)
        return
    fam, lo, hi, dark = SWEETHEARTS[i % len(SWEETHEARTS)]
    Rm = RAMP[fam]
    pillow(p, {(cx - 8 + a, cy - 7 + b) for a, b in heart_mask(17)}, Rm, lo=lo, hi=hi, spec_at=(cx - 5, cy - 5))
    if dark:
        p.text(cx - 3, cy - 4, initials, RAMP["coal"][0], "35")
    else:
        p.text(cx - 3, cy - 4, initials, C["white"], "35", shadow=Rm[0])


def candy_share(p: Pix, x, y, w, fill, edge):
    """A contributor's share as a bar of candy ribbon, red and white by turns every two pixels, `fill` of its
    `w` full, in a thread of `edge`."""
    R, Lc = RAMP["rose"], RAMP["lace"]
    p.box(x, y, w + 2, 4, edge)
    for xx in range(fill):
        red = (xx // 2) % 2 == 0
        p.px(x + 1 + xx, y + 1, R[5] if red else Lc[6])
        p.px(x + 1 + xx, y + 2, R[3] if red else Lc[4])


# --------------------------------------------------------------------------- the link buttons
def satin_trim(p: Pix, x0, x1, y, seed, night):
    """A strip of red satin ribbon along a button's top edge, on row `y` and the one under it, lit along its
    top, a seed pearl sewn on it every four pixels."""
    R, Lc = RAMP["rose"], RAMP["lace"]
    k = -1 if night else 0
    for xx in range(x0, x1):
        p.px(xx, y, R[5 + k] if (xx + seed) % 4 == 2 else R[4 + k])
        p.px(xx, y + 1, Lc[6] if (xx + seed) % 4 == 1 else R[2 + k])


# The set's sprites at a link button's size, seven pixels square at most: the footer's heart, a love letter
# sealed with a heart (the envelope at its smallest), a rose in bloom and a present tied with a bow.
ICONS = {
    "heart": [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."],
    "letter": ["eeeeeee", "efpppfe", "epapbpe", "epabcpe", "eppcppe", "eeeeeee"],
    "rose": ROSE[7],
    "gift": [".ad.da.", "..dkd..", "LLLRLLL", "PPQrQqq", "PPQrQqq", "PPQrQqq", "PPQrQqq"],
}


def icon(name: str, night: bool) -> tuple:
    """A link's sprite and its colours, shaded a tone deeper by night as the set's sprites are (all but
    the heart, which is the footer's own, the same by day and by night)."""
    R, B, Lc, G = RAMP["rose"], RAMP["blush"], RAMP["lace"], RAMP["leaf"]
    k = -1 if night else 0
    if name == "heart":
        pal = {str(i): R[i] for i in range(7)}
    elif name == "letter":
        pal = {"e": Lc[3 + k] if not night else Lc[2], "p": Lc[6] if not night else Lc[4],
               "f": Lc[4] if not night else Lc[3], "a": R[5 + k], "b": R[4 + k], "c": R[3 + k]}
    elif name == "rose":
        pal = {"a": R[5 + k], "e": R[6 + k], "b": R[4 + k], "c": R[3 + k], "d": R[2 + k], "g": G[3 + k]}
    else:
        pal = {"a": R[5 + k], "d": R[4 + k], "k": R[2 + k], "R": R[5 + k], "r": R[4 + k],
               "L": B[5 + k], "P": B[4 + k], "Q": B[3 + k], "q": B[2 + k]}
    return ICONS[name], pal
