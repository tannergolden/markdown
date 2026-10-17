# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Birthday set's scenery and sprites, drawn on the shared pixel canvas.

The paper is a party's: cream by day, dotted with the frostings' pastels, and by night a room with the lights off,
where the candles are the only light. The frame is piped icing, the shell border round a cake, flecked with
sprinkles; bunting is hung along the top, and across the middle of every header its pennants spell HAPPY BIRTHDAY.
The scenes are what only a birthday has: the cake and its candles, presents, cupcakes, a sundae, paper honeycomb
balls, and sprinkles over everything. Every sprite is shaded from the one light in the upper left on the set's own
ramps, and by night every candle's flame lights what stands near it.

A repository's cake carries its age in number candles. Once a loop, in a moving file, a breath blows the candles out:
smoke curls up from the wicks, and they light again.
"""
from __future__ import annotations

import math
import random

from ..holidays.pixel import BLINKS, FONTS, LX, LY, Paint, Pix, fold, num, sphere
from .palette import C, GROUND, NIGHT_SKY, PASTELS, RAMP, X, step

S, CR, CO, MI, LE, LI, SK, FL, CH, PL = (RAMP[n] for n in ("strawberry", "cream", "cocoa", "mint", "lemon", "lilac",
                                                            "sky", "flame", "cherry", "plum"))


def dim(night: bool) -> int:
    """How many tones darker a thing stands by night, the lights off: one."""
    return -1 if night else 0


# --------------------------------------------------------------------------- the titles
def frosting_fill(r, c, scale, night):
    """The colour a title's letter takes at row `r` of the letter, counted in pixels from its top: strawberry
    frosting, a band for each row of the face, lightest where the piping catches the light along its crown and
    deepening to its foot. By night every band is a tone lighter, warm in the candlelight, so each keeps 4.5:1
    against the dark."""
    band = min(6, r // scale)
    if night:
        return (S[6], S[5], S[5], S[4], S[4], S[4], S[3])[band]
    return (S[5], S[4], S[4], S[3], S[3], S[3], S[2])[band]


# The titles' frosting, a band for each row of the face.
FROSTING = Paint("frosting", frosting_fill)


def edged(p: Pix, x, y, s, scale, shadow, edge, L="base"):
    """What lies under a title's frosting by day: a shadow half a font pixel down-right, and a chocolate edge a pixel
    round every letter, as icing is piped over a line of ganache. Each letter's edge, its four copies a pixel off,
    is drawn once as a symbol and placed once a letter, so a long title stays light."""
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


SPRINKLE_FAMS = ("mint", "lemon", "sky", "lilac", "cream")


def sprinkle_colour(fam: str, night: bool, lit: bool = True) -> str:
    """A sprinkle's colour in the family `fam`: its lit side or its shaded one."""
    R = RAMP[fam]
    t = (6 if lit else 4) if fam == "cream" else (5 if lit else 3)
    return R[t + (dim(night) if fam != "cream" else 0)]


def title_sprinkles(p: Pix, cells, scale, layer, rnd, y):
    """Sprinkles on a title's frosting: here and there a rod of two pixels, across or upright, on the upper half of a
    letter, never two in a row, so the letters still read."""
    if scale < 3:
        return
    top = sorted(cells, key=lambda q: (q[1], q[0]))
    used = set()
    for (x, yy) in top:
        if (yy - y) > 3 * scale or rnd.random() > 0.035:
            continue
        upright = rnd.random() < 0.5
        pair = ((x, yy), (x, yy + 1)) if upright else ((x, yy), (x + 1, yy))
        if not all(q in cells for q in pair) or any((qx + dx, qy + dy) in used for (qx, qy) in pair
                                                    for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)):
            continue
        fam = rnd.choice(SPRINKLE_FAMS[:4])
        p.px(*pair[0], sprinkle_colour(fam, False, True), layer)
        p.px(*pair[1], sprinkle_colour(fam, False, False), layer)
        used.update(pair)


# --------------------------------------------------------------------------- the paper and the dark
def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: cream paper dotted with the frostings' pastels by day, as party paper is; by
    night a room with the lights off, deep plum, warmer toward the table the candles stand on, in five bands."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
        if dots:
            dots_at = ((3, 3, S[6]), (11, 3, MI[6]), (7, 11, LE[6]), (15, 11, SK[6]))
            body = "".join(f'<rect x="{dx}" y="{dy}" width="1" height="1" fill="{c}"/>' for dx, dy, c in dots_at)
            p.defs.append(f'<pattern id="{uid}d" width="16" height="16" patternUnits="userSpaceOnUse">{body}</pattern>')
            p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')
        return
    n = len(NIGHT_SKY)
    edges = [y + round(i * h / n) for i in range(n + 1)]
    for i, col in enumerate(NIGHT_SKY):
        p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    if dots:
        p.defs.append(f'<pattern id="{uid}d" width="16" height="16" patternUnits="userSpaceOnUse">'
                      f'<rect x="3" y="3" width="1" height="1" fill="{PL[3]}"/>'
                      f'<rect x="11" y="11" width="1" height="1" fill="{PL[3]}"/></pattern>')
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')


def sparkle(p: Pix, x, y, big=False, L="base", warm=False):
    """A four-point glint: a white heart, arms that fade, longer arms on the brightest."""
    arm = FL[6] if warm else X["star_pale"]
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.5", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """The dark's lights: faint motes, warm points, a few glints, and now and then a point in a frosting's colour, as
    if the room were hung with fairy lights. None is set inside a box in `avoid` (x0, y0, x1, y1)."""
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
            fam = rnd.choice(PASTELS)
            p.px(x, y, rnd.choice((C["white"], FL[6], X["star_pale"], RAMP[fam][5])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.5)


# --------------------------------------------------------------------------- the frame: piped icing
# The piping along each side, a tile four beads long, as rows of characters: `b` the band of icing along the outer
# edge, and under it a row of beads, each `h` lit where the light catches it, `l` lighter, `m` its body and `d` its
# shade, with a gap between beads where the paper shows. The light falls from the upper left on every side.
BEADS = {
    "top": ("bbbbbbbbbbbbbbbb", "hlm.hlm.hlm.hlm.", "lmd.lmd.lmd.lmd."),
    "bottom": ("hlm.hlm.hlm.hlm.", "lmd.lmd.lmd.lmd.", "dddddddddddddddd"),
    "left": ("bhl", "blm", "bmd", "b..") * 4,
    "right": ("hld", "lmd", "mdd", "..d") * 4,
}
# Where on each side's tile a sprinkle lies in place of a bead's body: one in four beads, never in line.
BEAD_SPRINKLES = {"top": ((2, 1, "mint"), (10, 2, "lemon")), "bottom": ((5, 0, "sky"), (13, 1, "mint")),
                  "left": ((2, 5, "lemon"), (1, 13, "sky")), "right": ((0, 1, "mint"), (1, 9, "lemon"))}


def _icing_tile(side: str, night: bool) -> tuple[dict, int, int]:
    """One tile of the piped border for a side (`top`, `bottom`, `left` or `right`), its cells coloured and its size:
    a band of strawberry buttercream along the outer edge and a row of piped beads inside it, lit on their upper left,
    two of the four with a sprinkle on them."""
    k = dim(night)
    tone = {"b": 4, "h": 6, "l": 5, "m": 4, "d": 3}
    rows = BEADS[side]
    out = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                t = tone[ch] - (1 if ch == "b" and side in ("bottom", "right") else 0)
                out[(x, y)] = S[max(1, t + k)]
    for (x, y, fam) in BEAD_SPRINKLES[side]:
        out[(x, y)] = sprinkle_colour(fam, night)
    return out, len(rows[0]), len(rows)


def icing_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="ic"):
    """The sheet's border: piped icing three pixels deep, a band of buttercream with a row of beads piped inside it,
    flecked with sprinkles; inside it a rule. Each side is one pattern tile placed along it, so the border costs a few
    hundred bytes."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    origin = {"top": (x, y), "bottom": (x, y + h - 3), "left": (x, y + 3), "right": (x + w - 3, y + 3)}
    for side, (ox, oy) in origin.items():
        cells, tw, th = _icing_tile(side, night)
        p.defs.append(f'<pattern id="{uid}{side[0]}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse" '
                      f'x="{ox}" y="{oy}">{p._paths(cells)}</pattern>')
    p.shapes["base"].append(f'<rect x="{x}" y="{y}" width="{w}" height="3" fill="url(#{uid}t)"/>')
    p.shapes["base"].append(f'<rect x="{x}" y="{y + h - 3}" width="{w}" height="3" fill="url(#{uid}b)"/>')
    p.shapes["base"].append(f'<rect x="{x}" y="{y + 3}" width="3" height="{h - 6}" fill="url(#{uid}l)"/>')
    p.shapes["base"].append(f'<rect x="{x + w - 3}" y="{y + 3}" width="3" height="{h - 6}" fill="url(#{uid}r)"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, S[4] if night else S[2])


# --------------------------------------------------------------------------- the bunting
PENNANT = (7, 7, 5, 5, 3, 3, 1)              # a plain pennant's width, row by row
FLAG = (9, 9, 9, 9, 9, 9, 9, 9, 7, 5, 3, 1)  # a lettered one's, wide and deep enough for a capital with room round it
GREETING = "HAPPY BIRTHDAY"


def _pennant(p: Pix, cx, top, rows, fam, night, letter=""):
    """One pennant hanging from row `top`, centred on `cx`: lit down its left edge, shaded down its right and at its
    tip, its hem a tone lighter; a letter of the greeting, when it carries one, in dark ink across its upper half."""
    R = RAMP[fam]
    t = 5 + dim(night)
    for j, wd in enumerate(rows):
        x0 = cx - wd // 2
        for i in range(wd):
            c = R[t]
            if j == 0:
                c = R[min(6, t + 1)]
            elif i == 0:
                c = R[min(6, t + 1)]
            elif i == wd - 1 or j == len(rows) - 1:
                c = R[t - 1]
            p.px(x0 + i, top + j, c)
    if letter:
        glyphs = FONTS["57"][0]
        g = glyphs[letter]
        lx = cx - g[0] // 2
        for r, cols in enumerate(g[1]):
            for col in cols:
                p.px(lx + col, top + 1 + r, C["ink"])


def _sag(x, xa, xb, y, sag):
    """The row the twine hangs at, at column `x` of a swag from `xa` to `xb` hung at row `y`."""
    t = (x - xa) / max(1, xb - xa)
    return y + round(sag * 4 * t * (1 - t))


def _twine(p: Pix, xa, xb, y, sag, night):
    """The twine of one swag, from tack to tack."""
    col = PL[5] if night else CO[4]
    prev = None
    for x in range(xa, xb + 1):
        yy = _sag(x, xa, xb, y, sag)
        p.px(x, yy, col)
        if prev is not None and abs(yy - prev) > 1:
            for j in range(min(yy, prev) + 1, max(yy, prev)):
                p.px(x, j, col)
        prev = yy


def _tack(p: Pix, x, y, night):
    """A little bow of strawberry ribbon where the bunting is pinned up."""
    k = dim(night)
    for (dx, dy, t) in ((-2, -1, 5), (-1, 0, 4), (-2, 1, 3), (0, 0, 6), (1, 0, 4), (2, -1, 5), (2, 1, 3)):
        p.px(x + dx, y + dy, S[t + k])


def bunting(p: Pix, x0, x1, y, night, seed=0, span=41, sag=4, greet=True):
    """Bunting along the top: triangular pennants in the frostings' pastels hung on twine, swagged from bow to bow.
    Across the middle, when the room allows, a wider run of pennants spells HAPPY BIRTHDAY, a letter each, hung on a
    shallower swag of its own."""
    words = GREETING.split()
    step_ = 10
    banner_w = sum(len(word) for word in words) * step_ - 1 + 6 * (len(words) - 1)
    mid = (x0 + x1) // 2
    spans = []
    if greet and x1 - x0 >= banner_w + 30:
        b0, b1 = mid - banner_w // 2 - 3, mid + (banner_w + 1) // 2 + 3
        spans = [(x0, b0), (b1, x1)]
    else:
        spans = [(x0, x1)]
    fam_i = seed
    for (a, b) in spans:
        n = max(1, round((b - a) / span))
        width = (b - a) / n
        for s in range(n):
            xa, xb = round(a + s * width), round(a + (s + 1) * width)
            _twine(p, xa, xb, y, sag, night)
            x = xa + 6
            while x <= xb - 5:
                top = _sag(x, xa, xb, y, sag) + 1
                _pennant(p, x, top, PENNANT, PASTELS[fam_i % len(PASTELS)], night)
                fam_i += 1
                x += 9
        for xt in sorted({round(a + s * width) for s in range(n + 1)}):
            _tack(p, min(max(xt, x0 + 2), x1 - 3), y, night)
    if len(spans) == 2:
        b0, b1 = spans[0][1], spans[1][0]
        _twine(p, b0, b1, y, 3, night)
        x, i = b0 + 3 + 4, 0
        for word in words:
            for ch in word:
                top = _sag(x, b0, b1, y, 3) + 1
                _pennant(p, x, top, FLAG, PASTELS[i % len(PASTELS)], night, ch)
                x += step_
                i += 1
            x += 6
        for xt in (b0, b1):
            _tack(p, xt, y, night)


# --------------------------------------------------------------------------- sprinkles, the cloth, shadows
def sprinkles_on(p: Pix, x0, x1, y, seed=7, L="base", night=False, gap=(3, 9)):
    """Sprinkles lying along a ledge whose top edge is row `y`: rods of two pixels, mostly lying flat, now and then
    one standing on its end or a round nonpareil, in every frosting's colour. None lies where it would touch a word."""
    rnd = random.Random(seed * 131 + x0)
    x = x0 + rnd.randint(1, 4)
    while x < x1 - 2:
        fam = rnd.choice(SPRINKLE_FAMS)
        if not p.clear_of_words(x, y - 3, x + 3, y):
            x += rnd.randint(*gap)
            continue
        r = rnd.random()
        if r < 0.2:                                          # one on its end
            p.px(x, y - 2, sprinkle_colour(fam, night, True), L)
            p.px(x, y - 1, sprinkle_colour(fam, night, False), L)
        elif r < 0.7:                                        # one lying flat
            p.px(x, y - 1, sprinkle_colour(fam, night, True), L)
            p.px(x + 1, y - 1, sprinkle_colour(fam, night, False), L)
            x += 1
        else:                                                # a nonpareil
            p.px(x, y - 1, sprinkle_colour(fam, night, rnd.random() < 0.6), L)
        x += rnd.randint(*gap)


def tablecloth(p: Pix, x0, x1, base, night, seed=5):
    """The cloth a scene stands on, along the foot from `x0` to `x1`, its two rows ending on row `base`: a strawberry
    runner dotted with cream, lit along its top, darker in the dark, and a few sprinkles fallen on it."""
    k = dim(night)
    for x in range(x0, x1):
        p.px(x, base - 1, CR[6] if (x - x0) % 4 == 1 else S[5 + k])
        p.px(x, base, S[4 + k] if (x - x0) % 4 != 3 else CR[5 + k])
    rnd = random.Random(seed)
    for x in range(x0 + 2, x1 - 2):
        if rnd.random() < 0.08 and (x - x0) % 4 != 1:
            p.px(x, base - 1, sprinkle_colour(rnd.choice(("mint", "lemon", "sky", "lilac")), night, True))


def contact(p: Pix, cx, y, rx):
    """The shadow a thing standing on the cloth leaves right under it: only the cloth takes it."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.7, X["shade_ink"], (0.16, 0.3), L="pool", only=GROUND, shape=False)


def light_pool(p: Pix, cx, y, rx, ry, night):
    """The candles' light pooled on the cloth round the cake's foot: only the cloth takes it."""
    if night:
        p.halo(cx, y, rx, ry, FL[5], (0.08, 0.15, 0.22), L="pool", only=GROUND)


def bobbing(p: Pix, motion, name="bob0", lift=(0, 0, 1, 2, 2, 1), dur=3.0):
    """A layer that rises and settles a pixel or two, round and round: how a paper ball rides the air."""
    return p.layer(name, ("bob", list(lift), dur)) if motion else "base"


# --------------------------------------------------------------------------- candles and their light
# A flame standing on a wick, as (dx, dy, tone) from the pixel just above the wick: its tip a tone of yellow, its
# heart near white, orange at its foot. `TIP` is the pixel a flickering flame reaches up to now and then.
FLAME = ((0, -3, 5), (-1, -2, 4), (0, -2, 6), (1, -2, 4), (-1, -1, 3), (0, -1, 6), (1, -1, 3), (0, 0, 3))
TIP = (0, -4, 5)
# The cake's flames are a size bigger, as a cake's candles are drawn nearer: (dx, dy, tone) as `FLAME`'s.
BIG_FLAME = ((0, -5, 5), (0, -4, 5), (-1, -3, 4), (0, -3, 6), (1, -3, 4), (-1, -2, 4), (0, -2, 6), (1, -2, 4),
             (-2, -1, 3), (-1, -1, 5), (0, -1, 6), (1, -1, 5), (2, -1, 3), (-1, 0, 3), (0, 0, 4), (1, 0, 3))
BIG_TIP = (0, -6, 5)
LIGHT_R = 13           # how far a flame's light reaches, in units


def flame(p: Pix, x, y, night, motion=True, phase=0):
    """A candle's flame on its wick at (x, y + 1), burning steadily and, in a moving file, flickering at its tip;
    by night a warm glow round it. Its light on what stands near it is laid by `lamplight`, last."""
    for (dx, dy, t) in FLAME:
        p.px(x + dx, y + dy, FL[t])
    p.px(x + TIP[0], y + TIP[1], FL[TIP[2]], p.flicker(phase) if motion else "base")
    if night:
        p.halo(x + 0.5, y - 1.5, 6, 7, FL[5], (0.05, 0.09, 0.15), L=p.flicker(phase, back=True) if motion else "haze")
    p.lamps.append((x + 0.5, y - 1.5, LIGHT_R, phase, {(x + dx, y + dy) for dx, dy, _ in FLAME + (TIP,)}))


def _light_cells(p: Pix, cx, cy, r, own, night) -> dict:
    """The warm light a flame at (cx, cy) lays on the drawn things within `r` of it, strongest nearest: the paper,
    the dark and the words take none."""
    base = p.layers["base"]
    col = FL[5]
    alphas = (0.08, 0.16, 0.26) if night else (0.035, 0.07)
    n = len(alphas)
    out = {}
    for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            if (x, y) not in base or (x, y) in own or ":" in base[(x, y)]:
                continue
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.25) / r
            if d < 1:
                out[(x, y)] = alphas[min(n - 1, int((1 - d) * n))]
    return out


def lamplight(p: Pix, night: bool):
    """The finishing pass: each flame's light on the drawn things near it, flickering with it."""
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for (x, y), a in _light_cells(p, cx, cy, r, own, night).items():
            p.apx(x, y, FL[5], a, L)


# A breath blows the cake's candles out once a loop: lit, then out with smoke curling up from the wicks, then lit
# again. As shares of the loop: when they go out, and when they are lit again.
BLOW_DUR, BLOW_OUT, BLOW_ON = 11.0, 0.8, 0.95
SMOKE = (                                   # each frame's wisp, as (dx, dy, alpha) above the wick
    ((0, 0, 0.7), (0, -1, 0.55), (1, -2, 0.4)),
    ((0, -2, 0.55), (1, -3, 0.5), (1, -4, 0.4), (0, -5, 0.3)),
    ((1, -5, 0.4), (0, -6, 0.35), (0, -7, 0.25), (-1, -8, 0.2)),
)


def _glows(cx, cy, night, big=False) -> str:
    """A flame's glow as stacked ellipses, the way `Pix.halo` draws a big one."""
    alphas = (0.05, 0.09, 0.15, 0.22) if night else (0.04, 0.07)
    rx, ry = ((10, 11) if big else (7, 8)) if night else (5, 6)
    out, prev, n = [], 0.0, len(alphas)
    for k, a in enumerate(alphas):
        f = (n - k) / n
        o = 1 - (1 - a) / (1 - prev)
        prev = a
        out.append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx * f)}" ry="{num(ry * f)}" fill="{FL[5]}" '
                   f'fill-opacity="{num(o)}"/>')
    return "".join(out)


def blown(p: Pix, wicks, night, motion, reach=20):
    """The cake's flames, one on each wick in `wicks` (x, y of the pixel just above it), with their glow and the light
    they lay on the cake, drawn as one group: in a moving file it flickers, and once a loop a breath blows it out,
    smoke curls up from every wick for a moment, a spark catches, and the candles are lit again. The still file keeps
    them lit. Called once everything near the candles stands, so the light falls on it."""
    body, flick, glows = {}, {}, []
    own = set()
    for (x, y) in wicks:
        for (dx, dy, t) in BIG_FLAME:
            body[(x + dx, y + dy)] = FL[t]
            own.add((x + dx, y + dy))
        flick[(x + BIG_TIP[0], y + BIG_TIP[1])] = FL[BIG_TIP[2]]
        flick[(x - 1, y - 4)] = FL[5]
        own.update({(x + BIG_TIP[0], y + BIG_TIP[1]), (x - 1, y - 4)})
        glows.append(_glows(x + 0.5, y - 2.5, night, big=True))
    light = {}
    if not p.lite:
        for (x, y) in wicks:
            for cell, a in _light_cells(p, x + 0.5, y - 2.5, reach, own, night).items():
                light[cell] = max(light.get(cell, 0), a)
    lit = {cell: f"{FL[5]}:{min(0.92, round(a * 25) / 25):g}" for cell, a in light.items()}
    halo = "".join(glows)
    if not motion:
        p.raw(8, "", halo + p.markup(body) + p.markup(flick) + p.markup(lit))
        return
    vals, kt, dur, _ = BLINKS["flicker"]
    inner = (f'<g>{p.markup(flick)}{p.markup(lit)}<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
             f'dur="{dur:g}s" repeatCount="indefinite" calcMode="discrete"/></g>')
    moving = (f'<g>{halo}{p.markup(body)}{inner}<animate attributeName="opacity" values="1;0;1" '
              f'keyTimes="0;{num(BLOW_OUT)};{num(BLOW_ON)}" dur="{num(BLOW_DUR)}s" repeatCount="indefinite" '
              f'calcMode="discrete"/></g>')
    p.raw(8, moving, halo + p.markup(body) + p.markup(flick) + p.markup(lit))
    smoke = PL[6] if night else CR[1]
    share = (BLOW_ON - BLOW_OUT - 0.02) / len(SMOKE)
    for i, frame in enumerate(SMOKE):
        t0 = BLOW_OUT + i * share
        L = p.seq(f"smoke{i}", t0, t0 + share, BLOW_DUR, z=9)
        for (x, y) in wicks:
            for (dx, dy, a) in frame:
                p.apx(x + dx, y + dy, smoke, a, L)
    spark = p.seq("spark", BLOW_ON - 0.02, BLOW_ON, BLOW_DUR, z=9)
    for (x, y) in wicks:
        p.px(x, y, FL[6], spark)


def slim_candle(p: Pix, x, top, h, fam, night):
    """A slim candle three pixels wide from row `top` down `h` rows, twisted with a stripe of cream round it, lit on
    its left; its wick black at its top. Returns where its flame stands: the pixel above the wick."""
    R = RAMP[fam]
    k = dim(night)
    for j in range(h):
        for i, t in enumerate((5, 4, 3)):
            stripe = (i + j) % 4 == 0
            p.px(x + i, top + j, (CR[6] if i == 0 else CR[5] if i == 1 else CR[3]) if stripe else R[t + k])
    p.px(x + 1, top - 1, C["coal"])
    return x + 1, top - 2


# The figures a number candle is cast in, seven pixels wide and ten tall, every stroke two pixels thick.
FIGURES = {
    "0": ("..###..", ".##.##.", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##", ".##.##.", "..###.."),
    "1": ("...##..", "..###..", ".####..", "...##..", "...##..", "...##..", "...##..", "...##..", "...##..", ".######"),
    "2": (".#####.", "##...##", ".....##", "....##.", "...##..", "..##...", ".##....", "##.....", "##.....", "#######"),
    "3": (".#####.", "##...##", ".....##", ".....##", "..####.", ".....##", ".....##", ".....##", "##...##", ".#####."),
    "4": ("....##.", "...###.", "..####.", ".##.##.", "##..##.", "#######", "....##.", "....##.", "....##.", "....##."),
    "5": ("#######", "##.....", "##.....", "######.", ".....##", ".....##", ".....##", ".....##", "##...##", ".#####."),
    "6": ("..####.", ".##....", "##.....", "##.....", "######.", "##...##", "##...##", "##...##", "##...##", ".#####."),
    "7": ("#######", ".....##", ".....##", "....##.", "....##.", "...##..", "...##..", "..##...", "..##...", "..##..."),
    "8": (".#####.", "##...##", "##...##", "##...##", ".#####.", "##...##", "##...##", "##...##", "##...##", ".#####."),
    "9": (".#####.", "##...##", "##...##", "##...##", ".######", ".....##", ".....##", ".....##", "....##.", ".####.."),
}


def number_candle(p: Pix, x, top, digit: str, fam, night) -> tuple[int, tuple]:
    """A number candle: the figure `digit` cast in wax, its strokes lit along their top and left and shaded along
    their foot and right, flecked with glitter, its wick at the top of the figure's middle. Returns its width and where
    its flame stands."""
    R = RAMP[fam]
    k = dim(night)
    rows = FIGURES[digit]
    drawn = {(cx, cy) for cy, row in enumerate(rows) for cx, ch in enumerate(row) if ch == "#"}
    cells = {(cx + dx, cy + dy) for (cx, cy) in drawn for dx in (0, 1) for dy in (0, 1)}   # cast thick, as wax is
    for (cx, cy) in cells:
        up, left = (cx, cy - 1) not in cells, (cx - 1, cy) not in cells
        down, right = (cx, cy + 1) not in cells, (cx + 1, cy) not in cells
        t = 4 + (up or left) - (down or right)
        if up and left:
            t = 6
        if (cx * 3 + cy * 5) % 11 == 0 and t < 6:
            t += 1                                           # a fleck of glitter
        p.px(x + cx, top + cy, R[max(1, min(6, t + k))])
    w = len(rows[0]) + 1
    top_row = min(cx for (cx, cy) in cells if cy == 0)
    mid = x + (top_row + max(cx for (cx, cy) in cells if cy == 0)) // 2
    p.px(mid, top - 1, C["coal"])
    return w, (mid, top - 2)


def candle_row(p: Pix, cx, base, night, age=None):
    """What stands on a cake's top: a repository's age in number candles, or five slim candles for a person, all
    standing on row `base`. Returns where each flame stands."""
    wicks = []
    if age:
        figures = str(age)
        fams = ("lilac", "sky", "mint")
        total = 8 * len(figures) + 2 * (len(figures) - 1)
        x = cx - total // 2
        top = base - 10
        for i, d in enumerate(figures):
            _, wick = number_candle(p, x, top, d, fams[i % len(fams)], night)
            wicks.append(wick)
            x += 10
        return wicks
    for i, fam in enumerate(("strawberry", "sky", "lemon", "mint", "lilac")):
        wicks.append(slim_candle(p, cx - 12 + i * 5, base - 8, 9, fam, night))
    return wicks


# --------------------------------------------------------------------------- the cake
def _shells(p: Pix, x0, x1, y, ramp, night, up=True):
    """A row of piped shells along a tier's edge from `x0` to `x1` on row `y`: a bead every three pixels, lit on its
    left, the row under it one tone deeper; `up` sets the beads above the row, as a top rim's are."""
    k = dim(night)
    for x in range(x0, x1):
        p.px(x, y, ramp[4 + k])
        if (x - x0) % 3 == 1:
            p.px(x, y - 1 if up else y + 1, ramp[6 + k] if (x - x0) % 6 == 1 else ramp[5 + k])
        elif (x - x0) % 3 == 0:
            p.px(x, y, ramp[5 + k])


def tier(p: Pix, cx, bottom, w, h, frosting, piping, night, seed=0, swags=True):
    """One tier of the cake, `w` wide and `h` tall, its foot on row `bottom`: frosted all round, lit from the left
    and falling into shade on the right, a rim of piped shells along its top and a bead border along its foot; on
    the big tier swags of piping looped between little rosettes, with nonpareils between them. Returns its top row."""
    R, P = RAMP[frosting], RAMP[piping]
    k = dim(night)
    x0, top = cx - w // 2, bottom - h + 1
    for y in range(top, bottom + 1):
        for x in range(x0, x0 + w):
            t = (x - x0 + 0.5) / w
            lam = max(0.0, (2 * t - 1) * -0.55 + math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2)) * 0.62 + 0.12)
            tone = 2 + lam * 3.4
            b = math.floor(tone)
            if tone - b > 0.62 or (tone - b > 0.38 and (x + y) % 2 == 0):
                b += 1
            if x == x0 + w - 1:
                b = 1
            p.px(x, y, R[max(1, min(6, b + k))])
    _shells(p, x0, x0 + w, top, P, night)
    _shells(p, x0, x0 + w, bottom, P, night, up=False)
    rnd = random.Random(seed)
    if swags:
        gap = 11
        for xa in range(x0 + 2, x0 + w - 6, gap):
            xb = min(xa + gap, x0 + w - 3)
            for x in range(xa, xb + 1):
                tt = (x - xa) / max(1, xb - xa)
                yy = top + 3 + round(4 * tt * (1 - tt) * 3)
                p.px(x, yy, P[6 + k] if x < cx + w // 4 else P[5 + k])
                p.px(x, yy + 1, step(R[3 + k], -1))
            fam = ("lemon", "mint", "sky")[(xa // gap) % 3]
            F = RAMP[fam]
            for (dx, dy, t) in ((0, -1, 6), (-1, 0, 5), (0, 0, 4), (1, 0, 3), (0, 1, 3)):
                p.px(xa + dx, top + 3 + dy, F[t + k])
        for _ in range(w // 3):
            x, y = rnd.randrange(x0 + 2, x0 + w - 3), rnd.randrange(top + 8, bottom - 2)
            if p.get(x, y) in R:
                p.px(x, y, sprinkle_colour(rnd.choice(SPRINKLE_FAMS[:4]), night, rnd.random() < 0.6))
    else:
        for _ in range(w // 2):
            x, y = rnd.randrange(x0 + 2, x0 + w - 3), rnd.randrange(top + 3, bottom - 4)
            if p.get(x, y) in R:
                p.px(x, y, sprinkle_colour(rnd.choice(("strawberry", "mint", "sky", "lilac")), night,
                                           rnd.random() < 0.6))
    return top


def ribbon_band(p: Pix, cx, y, w, fam, night):
    """A satin ribbon three rows deep round a tier from row `y`, tied in a bow at its front."""
    R = RAMP[fam]
    k = dim(night)
    x0 = cx - w // 2
    for x in range(x0, x0 + w):
        edge = x == x0 + w - 1
        p.px(x, y, R[5 + k] if not edge else R[3 + k])
        p.px(x, y + 1, R[4 + k] if not edge else R[2 + k])
        p.px(x, y + 2, R[3 + k] if not edge else R[2 + k])
    bow = (".AA...AA.",
           "AbbA.AbbA",
           "AbbbKbbbA",
           ".AA.K.AA.",
           "...a.a...",
           "..a...a..")
    tone = {"A": 3, "b": 5, "K": 6, "a": 4}
    for j, row in enumerate(bow):
        for i, ch in enumerate(row):
            if ch != ".":
                t = tone[ch] + (1 if ch == "b" and i < 4 else 0)
                p.px(cx - 4 + i, y - 2 + j, R[max(1, min(6, t + k))])


def stand(p: Pix, cx, base, w, night):
    """A porcelain cake stand on row `base`: a broad plate `w` wide lit along its top, on a turned stem and a foot.
    Returns the row the cake sits on."""
    k = dim(night)
    plate = base - 7
    x0 = cx - w // 2
    for x in range(x0, x0 + w):
        t = (x - x0) / max(1, w - 1)
        p.px(x, plate, CR[6] if t < 0.7 else CR[5])
        p.px(x, plate + 1, CR[4 + k] if t < 0.6 else CR[3 + k])
    for x in range(x0 + 2, x0 + w - 2):
        p.px(x, plate + 2, CR[2 + k])
    for (y, half) in ((plate + 3, 9), (plate + 4, 3), (plate + 5, 3), (plate + 6, 5), (base, 9)):
        for x in range(cx - half, cx + half + 1):
            t = (x - cx + half) / max(1, 2 * half)
            p.px(x, y, CR[(5 if t < 0.3 else 4 if t < 0.7 else 3) + k] if y != plate + 3 else CR[3 + k])
    return plate - 1


def cake(p: Pix, cx, base, night, motion, age=None):
    """The birthday cake on its stand, standing on row `base`: a big tier of strawberry frosting swagged in cream
    piping, a vanilla tier on it ringed with mint ribbon, and on top a repository's age in number candles or five slim
    candles, all lit. Returns where each flame stands, for `blown` to light once everything near it is drawn."""
    seat = stand(p, cx, base, 60, night)
    top = tier(p, cx, seat, 50, 18, "strawberry", "cream", night, seed=3)
    upper = tier(p, cx, top - 1, 34, 14, "cream", "strawberry", night, seed=5, swags=False)
    ribbon_band(p, cx, top - 4, 34, "mint", night)
    wicks = candle_row(p, cx, upper - 1, night, age)
    return wicks


# --------------------------------------------------------------------------- presents
def present(p: Pix, x, base, w, h, fam, ribbon, night, wrap="dots", bow=True):
    """A present standing on row `base`, `w` wide and `h` tall: wrapped in `fam` paper, dotted, striped or plain, lit
    down its left and shaded down its right; its lid a row wider each side; a ribbon round it both ways, tied on top
    in a bow. Returns the row its lid's top is on."""
    R, B = RAMP[fam], RAMP[ribbon]
    k = dim(night)
    top = base - h + 1
    lid = 3 if h >= 9 else 2
    mid = x + w // 2
    for y in range(top, base + 1):
        on_lid = y < top + lid
        x0, x1 = (x - 1, x + w + 1) if on_lid else (x, x + w)
        for xx in range(x0, x1):
            t = 4
            if xx == x0:
                t = 5
            elif xx >= x1 - 2:
                t = 3
            if y == base or (on_lid and y == top + lid - 1):
                t = min(t, 3)
            if on_lid and y == top:
                t = 6 if xx < x1 - 2 else 5
            c = R[t + k]
            if not on_lid and wrap == "dots" and (xx - x + (y - top) // 3 * 2) % 4 == 1 and (y - top) % 3 == 1:
                c = CR[6] if t >= 4 else CR[4]
            elif not on_lid and wrap == "stripes" and (xx - x + y) % 5 < 2:
                c = R[min(6, t + 1 + k)] if t + k < 6 else R[6]
            p.px(xx, y, c)
        for xx in (mid - 1, mid):
            p.px(xx, y, B[(5 if xx == mid - 1 else 3) + k] if not on_lid else B[(6 if xx == mid - 1 else 4) + k])
    band = top + lid + (h - lid) // 2
    for xx in range(x, x + w):
        p.px(xx, band, B[(5 if xx < x + w - 2 else 3) + k])
        p.px(xx, band + 1, B[(4 if xx < x + w - 2 else 2) + k])
    if bow:
        for (dx, dy, t) in ((-4, -2, 5), (-3, -3, 6), (-2, -3, 5), (-1, -2, 4), (-4, -1, 4), (-3, -1, 3), (-2, -1, 4),
                            (-1, -1, 5), (0, -1, 6), (1, -2, 4), (2, -3, 5), (3, -3, 4), (4, -2, 3), (1, -1, 3),
                            (2, -1, 4), (3, -1, 3), (4, -1, 2), (0, -2, 5)):
            p.px(mid + dx, top + dy, B[max(1, t + k)])
    return top - (3 if bow else 0)


# --------------------------------------------------------------------------- cupcakes
def cupcake(p: Pix, cx, base, liner, frosting, night, topping="cherry", motion=True, phase=0):
    """A cupcake standing on row `base`, centred on `cx`: a pleated paper liner lit down its left, a swirl of
    frosting piped three turns high with its spiral picked out, sprinkles on it, and on top a cherry, or a slim
    candle burning. Returns where a candle's flame stands, or None."""
    Lr, F = RAMP[liner], RAMP[frosting]
    k = dim(night)
    for j, half in enumerate((5, 5, 5, 4, 4, 4)):
        y = base - 5 + j
        for x in range(cx - half, cx + half):
            pleat = (x - cx + half) % 2 == 0
            t = (5 if x == cx - half else 3 if x >= cx + half - 1 else 4 if pleat else 3) + k
            p.px(x, y, Lr[max(1, t)])
    rows = ((base - 6, 6), (base - 7, 6), (base - 8, 5), (base - 9, 4), (base - 10, 3), (base - 11, 2), (base - 12, 1))
    for (y, half) in rows:
        for x in range(cx - half, cx + half):
            t = (x - cx + half) / max(1, 2 * half - 1)
            tone = 5 if t < 0.3 else 4 if t < 0.75 else 3
            if (x - cx + (base - y) * 2) % 7 == 0 and half > 2:
                tone -= 1
            p.px(x, y, F[max(1, tone + k)])
    rnd = random.Random(cx * 7 + base)
    for _ in range(4):
        x, y = rnd.randrange(cx - 4, cx + 4), rnd.randrange(base - 9, base - 6)
        p.px(x, y, sprinkle_colour(rnd.choice(("lemon", "sky", "mint", "lilac")), night))
    if topping == "cherry":
        sphere(p, cx - 0.5, base - 13.5, 1.8, CH, lo=2, hi=6)
        p.px(cx, base - 16, MI[2 + 1 + k])
        p.px(cx + 1, base - 17, MI[2 + 1 + k])
        return None
    if topping == "candle":
        return slim_candle(p, cx - 1, base - 19, 7, "sky", night)
    return None


# --------------------------------------------------------------------------- the piñata and the paper fans
# The donkey piñata, facing left, as rows of characters: `#` its body, `e` its eye, `t` its tail's tassel.
DONKEY = (
    "...##.##......................",
    "...##.##......................",
    "...##.##......................",
    "...######.....................",
    "..########....................",
    ".####e####....................",
    "##########....................",
    "n#########....................",
    ".#########....................",
    "....#######...................",
    ".....#######..................",
    "......######################..",
    "......#######################t",
    "......######################.t",
    "......######################.t",
    "......######################..",
    ".......####################...",
    ".......###..###......###..###.",
    ".......###..###......###..###.",
    ".......###..###......###..###.",
    ".......hhh..hhh......hhh..hhh.",
)
ROPE_AT = 17            # the column of the donkey's back its rope is tied to
FRINGE = ("strawberry", "lemon", "mint", "sky", "lilac")


def pinata(p: Pix, x, y, night, L="base", rope_top=4):
    """A donkey piñata hung from the ceiling on a rope from row `rope_top`, its top-left at (x, y): covered in rows of
    tissue fringe in the frostings' colours, each row's ragged edge falling over the next, a dark eye, a tassel for a
    tail. The rope passes behind whatever hangs in front of it."""
    k = dim(night)
    rope = PL[5] if night else CO[4]
    for yy in range(rope_top, y + 11):
        if p.get(x + ROPE_AT, yy) is None:
            p.px(x + ROPE_AT, yy, rope, L)
    cells = {(cx, cy): ch for cy, row in enumerate(DONKEY) for cx, ch in enumerate(row) if ch != "."}
    for (cx, cy), ch in cells.items():
        band = cy // 2
        R = RAMP[FRINGE[band % len(FRINGE)]]
        if ch == "e":
            c = C["coal"]
        elif ch == "n":
            c = S[2 + k]
        elif ch == "h":
            c = RAMP["cocoa"][2 + k]
        elif ch == "t":
            c = RAMP[FRINGE[(band + 2) % len(FRINGE)]][5 + k]
        else:
            up, left = (cx, cy - 1) not in cells, (cx - 1, cy) not in cells
            down, right = (cx, cy + 1) not in cells, (cx + 1, cy) not in cells
            t = 5
            if cy % 2 == 1 and (cx + band) % 2 == 0:
                t = 4                                        # the ragged edge of a row of fringe
            if up or left:
                t = 6
            if down or right:
                t = min(t, 3)
            c = R[max(1, t + k)]
        p.px(x + cx, y + cy, c, L)


def paper_fan(p: Pix, cx, cy, r, fam, night, L="base", pleats=12):
    """A tissue paper fan pinned to the wall, centred on (cx, cy): a disc of pleats, every other one in shade, its
    rim scalloped where each pleat ends, lit from the upper left, with a button of lemon at its heart."""
    R = RAMP[fam]
    k = dim(night)
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 2):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            a = (math.atan2(dy, dx) + 2 * math.pi) % (2 * math.pi)
            pleat = int(a / (2 * math.pi / pleats))
            frac = a / (2 * math.pi / pleats) - pleat
            edge = r - 0.9 * abs(frac - 0.5)
            if d > edge:
                continue
            lit = (dx * LX + dy * LY) / max(1.0, d)
            t = 5 if pleat % 2 == 0 else 3
            if lit > 0.35:
                t += 1
            elif lit < -0.35:
                t -= 1
            if d > edge - 1 and pleat % 2 == 0:
                t -= 1
            p.px(x, y, R[max(1, min(6, t + k))], L)
    for (dx, dy, t) in ((0, 0, 5), (-1, 0, 6), (0, -1, 6), (-1, -1, 6), (1, 0, 4), (0, 1, 4), (1, 1, 3),
                        (-1, 1, 4), (1, -1, 4)):
        p.px(round(cx) + dx, round(cy) + dy, LE[max(1, t + k)], L)


# --------------------------------------------------------------------------- hanging honeycomb balls
def honeycomb(p: Pix, cx, cy, r, fam, night, L="base", string_top=4):
    """A paper honeycomb ball hung from the ceiling on a thread from row `string_top`: a sphere of tissue lit from the
    upper left, its folded cells showing as bands across it; the thread passes behind whatever hangs in front."""
    R = RAMP[fam]
    k = dim(night)
    for y in range(string_top, round(cy - r)):
        if p.get(cx, y) is None:
            p.px(cx, y, CR[3] if night else CO[4], L)
    ramp = [R[max(0, min(6, i + k))] for i in range(7)]
    cells = sphere(p, cx, cy, r, ramp, L=L, lo=1, hi=6, spec=False)
    for (x, y), t in cells.items():
        if (y - round(cy - r)) % 3 == 2 and t > 1:
            p.px(x, y, ramp[t - 1], L)
        if (x + y) % 5 == 0 and t > 2 and (y - round(cy - r)) % 3 == 0:
            p.px(x, y, ramp[t - 1], L)
    p.px(cx, round(cy - r) - 1, CR[4 + k], L)
    p.px(cx, round(cy + r), CR[4 + k], L)


# --------------------------------------------------------------------------- the sundae
def sundae(p: Pix, cx, base, night):
    """An ice cream sundae standing on row `base`: a footed glass, three scoops in it, strawberry, vanilla and mint,
    a cloud of whipped cream, a cherry on top and a wafer standing in it."""
    k = dim(night)
    G = SK
    # the foot and the stem
    for x in range(cx - 5, cx + 5):
        p.px(x, base, G[(6 if x < cx - 2 else 5 if x < cx + 2 else 4) + k])
    for y in range(base - 3, base):
        p.px(cx - 1, y, G[6 + k])
        p.px(cx, y, G[4 + k])
    # the bowl, its glass showing the scoops' foot
    for j, half in enumerate((7, 7, 6, 6, 5, 4)):
        y = base - 9 + j
        for x in range(cx - half, cx + half):
            edge = x in (cx - half, cx + half - 1)
            inside = S[3 + k] if x < cx else CR[3 + k]
            p.px(x, y, (G[6 + k] if x == cx - half else G[4 + k]) if edge else inside)
        if j == 1:
            p.px(cx - half + 2, y, C["white"])
    sphere(p, cx - 3.5, base - 11.5, 4.2, [S[max(0, i + k)] for i in range(7)], lo=1, hi=6)
    sphere(p, cx + 3.5, base - 11.5, 4.2, [MI[max(0, i + k)] for i in range(7)], lo=1, hi=6)
    sphere(p, cx, base - 16.5, 4.2, [CR[max(0, i + k)] for i in range(7)], lo=1, hi=6)
    for (dx, dy, t) in ((-2, -21, 6), (-1, -21, 6), (0, -21, 5), (1, -21, 5), (-1, -22, 6), (0, -22, 5),
                        (-3, -20, 6), (2, -20, 4), (0, -23, 6)):
        p.px(cx + dx, base + dy, CR[t])
    sphere(p, cx - 0.5, base - 25, 1.8, CH, lo=2, hi=6)
    p.px(cx, base - 27, MI[3 + k])
    p.px(cx + 1, base - 28, MI[3 + k])
    for j in range(8):                                       # the wafer, standing slantwise in the scoops
        p.px(cx + 4 + j // 3, base - 17 - j, LE[(5 if j % 2 else 4) + k])
        p.px(cx + 5 + j // 3, base - 17 - j, LE[3 + k])
    rnd = random.Random(cx)
    for _ in range(5):
        x, y = rnd.randrange(cx - 6, cx + 6), rnd.randrange(base - 19, base - 9)
        if p.get(x, y) in (S + MI + CR):
            p.px(x, y, sprinkle_colour(rnd.choice(("lemon", "sky", "lilac")), night))


# --------------------------------------------------------------------------- the surprise: a present that opens
SURPRISE_DUR = 6.0
LID_LIFT = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 4, 4, 4, 3, 1, 0)


def surprise(p: Pix, x, base, night, motion):
    """Three presents stacked on row `base`, from `x`: in a moving file the top one's lid jumps open now and then,
    and a burst of sprinkles flies out of it while it is up."""
    present(p, x, base, 26, 16, "mint", "strawberry", night, wrap="dots", bow=False)
    present(p, x + 4, base - 16, 18, 12, "lilac", "lemon", night, wrap="stripes", bow=False)
    small_top = base - 28
    k = dim(night)
    R, B = LE, S
    bx, bw = x + 7, 12
    for y in range(small_top - 6, small_top + 1):
        for xx in range(bx, bx + bw):
            t = 5 if xx == bx else 3 if xx >= bx + bw - 2 else 4
            p.px(xx, y, R[t + k] if y != small_top else R[3 + k])
        for xx in (bx + bw // 2 - 1, bx + bw // 2):
            p.px(xx, y, B[(5 if xx == bx + bw // 2 - 1 else 3) + k])
    lid_y = small_top - 8
    if motion:
        n = len(LID_LIFT)
        lid = p.layer("lid", ("bob", list(LID_LIFT), SURPRISE_DUR))
    else:
        lid = "base"
    for y in (lid_y, lid_y + 1):
        for xx in range(bx - 1, bx + bw + 1):
            t = (6 if y == lid_y else 4) if xx < bx + bw - 1 else 3
            p.px(xx, y, R[t + k], lid)
        for xx in (bx + bw // 2 - 1, bx + bw // 2):
            p.px(xx, y, B[(6 if xx == bx + bw // 2 - 1 else 4) + k], lid)
    for (dx, dy, t) in ((-3, -2, 5), (-2, -3, 6), (-1, -2, 4), (-1, -1, 5), (0, -1, 6), (1, -2, 4), (2, -3, 5),
                        (3, -2, 3), (2, -1, 4), (1, -1, 3)):
        p.px(bx + bw // 2 + dx, lid_y + dy, B[max(1, t + k)], lid)
    if motion:
        n = len(LID_LIFT)
        t0 = (LID_LIFT.index(3) - 0.5) / n
        rnd = random.Random(x)
        for frame, (t_a, t_b, reach) in enumerate(((t0, t0 + 2 / n, 4), (t0 + 2 / n, (n - 2) / n, 8))):
            L = p.seq(f"burst{frame}", t_a, t_b, SURPRISE_DUR, z=12)
            for i in range(9):
                ang = math.pi * (0.15 + 0.7 * i / 8)
                rr = reach * (0.6 + 0.4 * rnd.random())
                sx, sy = bx + bw // 2 + math.cos(ang) * rr * 1.4, lid_y - 1 - math.sin(ang) * rr
                fam = SPRINKLE_FAMS[i % 4]
                p.px(round(sx), round(sy), sprinkle_colour(fam, night, True), L)
                if i % 2:
                    p.px(round(sx) + 1, round(sy), sprinkle_colour(fam, night, False), L)


# --------------------------------------------------------------------------- small things: the footers and links
def heart(p: Pix, x, y, L="base"):
    """The heart in BUILT WITH (heart) BY: a heart-shaped sugar cookie iced in strawberry, a sprinkle on it."""
    art = [".ab.bc.", "abbbbcd", "bbbbccd", ".bbccd.", "..ccd..", "...d..."]
    pal = {"a": S[6], "b": S[4], "c": S[3], "d": S[2]}
    p.sprite(x, y, art, pal, L=L)
    p.px(x + 2, y + 2, LE[5], L)


def stripe_bar(p: Pix, x0, y0, w, h, period=5):
    """The graphic scale's bar, striped slantwise strawberry and cream like a birthday candle, one colour every
    `period` pixels."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            band = ((x - x0) + (y - y0)) // period % 2
            p.px(x, y, S[3] if band == 0 else CR[5])


def cake_slice(p: Pix, x, y, night):
    """A slice of the cake on a plate, its layers showing, a cherry on its frosting: the schematic's ornament, its
    top-left at (x, y), 22 by 14."""
    k = dim(night)
    for xx in range(x, x + 22):                              # the plate
        p.px(xx, y + 13, CR[5 + k] if xx < x + 16 else CR[3 + k])
    for xx in range(x + 2, x + 20):
        p.px(xx, y + 12, CR[6] if xx < x + 6 else CR[5 + k])
    layers = ((S, 2), (CR, 2), (S, 1), (CR, 2), (S, 1), (CR, 2))
    yy = y + 11
    for ramp, rows in layers[::-1]:
        for _ in range(rows):
            for xx in range(x + 3, x + 19):
                t = 5 if xx < x + 5 else 3 if xx > x + 16 else 4
                p.px(xx, yy, ramp[t + k])
            yy -= 1
    for xx in range(x + 2, x + 20):                          # the frosting on top, piped along its edge
        p.px(xx, yy, S[(6 if xx < x + 8 else 5) + k])
        if (xx - x) % 3 == 0:
            p.px(xx, yy - 1, S[5 + k])
    sphere(p, x + 11.5, yy - 2.5, 1.8, CH, lo=2, hi=6)
    p.px(x + 12, yy - 5, MI[3 + k])


SLICE = (22, 14)        # the slice on its plate: its width and its height


# The links' icons, by name: a slice of cake, a present, a cupcake and a candle, seven pixels square.
ICONS = {
    "slice": ["...r...", "..wwww.", ".wwwwww", "ccccccc", "jjjjjjj", "ccccccc", "ppppppp"],
    "gift": ["..b.b..", "...b...", "pppbppp", "qqqbqqq", "bbbbbbb", "qqqbqqq", "qqqbqqq"],
    "cupcake": ["...r...", "..www..", ".wwwww.", "wwwwwww", "lmlmlml", ".lmlml.", ".lmlml."],
    "candle": ["...a...", "..aya..", "...o...", "..sws..", "..wsw..", "..sws..", "..wsw.."],
}
LINK_ICONS = ("slice", "gift", "cupcake", "candle")


def icon_pal(night: bool) -> dict:
    """The icons' tones: by day a tone deeper, so they read on the button's white face; by night lighter, on its
    plum one."""
    k = 0 if night else -1
    return {"r": CH[4 + k], "w": S[5 + k], "c": CR[4 + k] if night else CR[3], "j": S[3 + k], "p": S[4 + k],
            "b": LE[4 + k] if night else LE[3], "q": MI[4 + k], "l": LI[4 + k], "m": LI[3 + k],
            "a": FL[5 + k], "y": FL[6 + k] if night else FL[4], "o": FL[3], "s": SK[4 + k], "h": C["white"]}


# --------------------------------------------------------------------------- the elements
def candle_bar(p: Pix, bx, base, bw, v, night):
    """One week's bar as a birthday candle `v` pixels tall on `base`, twisted with cream, its wick at the top."""
    fams = ("strawberry", "sky", "lemon", "mint", "lilac")
    R = RAMP[fams[(bx // 7) % len(fams)]]
    k = dim(night)
    for y in range(base - v, base):
        for i in range(bw):
            t = 5 if i == 0 else 3 if i == bw - 1 else 4
            stripe = (i + y) % 5 in (0, 1)
            p.px(bx + i, y, (CR[6] if i == 0 else CR[5] if i < bw - 1 else CR[3]) if stripe else R[t + k])
    if v > 2:
        p.px(bx + bw // 2, base - v - 1, C["coal"])


def little_flame(p: Pix, x, y, night):
    """A small flame two pixels high on a wick at (x, y + 1): the busiest week's mark."""
    p.px(x, y - 2, FL[5])
    p.px(x - 1, y - 1, FL[4])
    p.px(x, y - 1, FL[6])
    p.px(x + 1, y - 1, FL[3])
    p.px(x, y, FL[3])


def piped_ring(p: Pix, arc, night):
    """The dial's ring as a crown of piped strawberry beads along `arc`, a bead every three points, each lit on its
    upper left."""
    k = dim(night)
    for i, (x, y) in enumerate(arc):
        p.px(round(x), round(y), S[(4 if i % 3 else 5) + k])
        p.px(round(x), round(y) + 1, S[3 + k])
        if i % 3 == 0:
            p.px(round(x) - 1, round(y), S[6 + k])


def wrapping(i: int, xx, yy, y0, lift, night) -> str:
    """The colour of the `i`-th file type's wrapping paper at (xx, yy): strawberry with cream dots, mint with stripes,
    lemon checked, lilac with confetti, by turns, lit along its top and shaded along its foot by `lift`."""
    k = dim(night)
    kind = i % 4
    if kind == 0:
        c = CR[5] if (xx % 4 == 1 and (yy - y0) % 4 == 1) or (xx % 4 == 3 and (yy - y0) % 4 == 3) else S[4]
    elif kind == 1:
        c = MI[5] if (xx + yy) % 4 < 2 else MI[3]
    elif kind == 2:
        c = LE[5] if ((xx // 2) + ((yy - y0) // 2)) % 2 == 0 else LE[4]
    else:
        c = (S[5], LE[5], SK[5])[(xx + yy) % 3] if (xx * 5 + yy * 3) % 9 == 0 else LI[4]
    try:
        return step(c, lift + k)
    except KeyError:
        return c


def gift_cell(q: Pix, ox, oy, night):
    """The 11 by 15 cell a counter's digit sits in: a little gift box, its lid a strip of ribbon-tied strawberry over a
    cream body, lit on its left."""
    k = dim(night)
    body, edge = (PL[2], PL[4]) if night else (CR[6], CR[4])
    q.rect(ox, oy + 3, 11, 12, body)
    q.box(ox, oy + 3, 11, 12, edge)
    for x in range(ox - 1, ox + 12):
        q.px(x, oy + 1, S[(5 if x < ox + 9 else 3) + k])
        q.px(x, oy + 2, S[(4 if x < ox + 9 else 2) + k])
    q.px(ox + 5, oy, LE[4 + k])
    q.px(ox + 4, oy, LE[5 + k])
    q.px(ox + 6, oy, LE[3 + k])


PENNANT_FAMS = ("strawberry", "mint", "lemon", "sky", "lilac")


def release(p: Pix, x, gy, kind, night, i=0, unlit=None):
    """A release hanging from the bunting's twine at x, the twine on row `gy`: a pennant in a frosting's colour, a big
    one in lemon for a big release, a nonpareil for a patch, the little cake with its one candle for the day the
    repository was made, and for one still to come a pennant only outlined, in `unlit`."""
    k = dim(night)
    if kind in ("big", "major"):
        R = RAMP["lemon" if kind == "big" else PENNANT_FAMS[i % 4 + 1]]
        rows = (7, 7, 5, 5, 3, 3, 1) if kind == "big" else (5, 5, 3, 3, 1)
        for j, wd in enumerate(rows):
            x0 = x + 1 - wd // 2
            for ii in range(wd):
                t = 6 if ii == 0 else 3 if ii == wd - 1 else 5
                p.px(x0 + ii, gy + 1 + j, R[max(1, t + k)])
    elif kind == "minor":
        R = RAMP[PENNANT_FAMS[i % len(PENNANT_FAMS)]]
        p.px(x, gy + 2, R[5 + k])
        p.px(x + 1, gy + 2, R[3 + k])
    elif kind == "made":
        for xx in range(x - 3, x + 5):                       # the little cake the repository was made on
            for yy in range(gy + 4, gy + 9):
                t = 5 if xx == x - 3 else 3 if xx == x + 4 else 4
                p.px(xx, yy, (S if yy > gy + 5 else CR)[t + k])
        p.px(x, gy + 2, CR[6])
        p.px(x + 1, gy + 2, CR[4])
        p.px(x, gy + 3, CR[5])
        p.px(x, gy, FL[5])
        p.px(x, gy + 1, FL[3])
    else:
        rows = (5, 5, 3, 3, 1)
        for j, wd in enumerate(rows):
            x0 = x + 1 - wd // 2
            for ii in range(wd):
                if ii in (0, wd - 1) or j == 0:
                    p.px(x0 + ii, gy + 1 + j, unlit)


def cookie(p: Pix, cx, cy, fam, initials, night, ink):
    """A contributor as a round sugar cookie, iced in their colour with their initials piped on it in dark icing,
    centred on (cx, cy), a sprinkle or two at its rim."""
    R = RAMP[fam]
    k = dim(night)
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 7, cx + 8):
            d = math.hypot(x - cx, y - cy)
            if d > 7.3:
                continue
            if d > 6.2:
                p.px(x, y, CO[(5 if x + y < cx + cy else 3) + k])
            else:
                lit = (x - cx) * -0.55 + (y - cy) * -0.68
                p.px(x, y, R[(6 if lit > 2.5 else 5) + k])
    lw = Pix.measure(initials, "35")
    p.text(cx - lw // 2, cy - 2, initials, ink, "35")
    p.px(cx - 5, cy - 3, sprinkle_colour("sky", night))
    p.px(cx + 5, cy + 3, sprinkle_colour("lemon", night))


def toy_robot(p: Pix, cx, cy, night):
    """A bot as a little wind-up robot, its key at its back, centred on (cx, cy)."""
    k = dim(night)
    G = SK
    for y in range(cy - 6, cy - 1):                          # the head
        for x in range(cx - 4, cx + 4):
            p.px(x, y, G[(5 if x == cx - 4 else 3 if x == cx + 3 else 4) + k])
    p.px(cx - 2, cy - 4, LE[6])
    p.px(cx + 1, cy - 4, LE[6])
    p.hline(cx - 2, cx + 2, cy - 2, G[2 + k])
    p.px(cx, cy - 7, S[4 + k])
    p.px(cx, cy - 8, S[5 + k])
    for y in range(cy - 1, cy + 6):                          # the body
        for x in range(cx - 5, cx + 5):
            p.px(x, y, G[(5 if x == cx - 5 else 3 if x >= cx + 3 else 4) + k])
    p.rect(cx - 2, cy + 1, 4, 3, S[4 + k])
    p.px(cx - 1, cy + 2, S[6])
    for x in (cx - 4, cx + 2):                               # the feet
        p.hline(x, x + 3, cy + 6, G[2 + k])
    p.px(cx + 5, cy + 2, LE[4 + k])                          # the key
    p.px(cx + 6, cy + 1, LE[5 + k])
    p.px(cx + 6, cy + 3, LE[3 + k])


def ribbon_bar(p: Pix, x, y, w, fill, night, edge):
    """A contributor's share as a length of ribbon striped strawberry and cream, slantwise, in its box."""
    p.box(x, y, w + 2, 4, edge)
    k = dim(night)
    for xx in range(fill):
        bright = ((xx + 1) // 2) % 2 == 0
        p.px(x + 1 + xx, y + 1, S[5 + k] if bright else CR[6])
        p.px(x + 1 + xx, y + 2, S[3 + k] if bright else CR[4])


def frosted_seal(p: Pix, cx, cy, r, night):
    """The certificate's seal ringed with piped strawberry shells, round the disc the kit draws: a shell every so far
    round it, each lit on its upper left."""
    k = dim(night)
    n = max(16, round(2 * math.pi * r / 3))
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        lit = math.cos(a) * -0.55 + math.sin(a) * -0.68
        t = 6 if lit > 0.45 else 5 if lit > -0.2 else 4
        p.px(round(x), round(y), S[t + k])
        x2, y2 = cx + math.cos(a) * (r + 1), cy + math.sin(a) * (r + 1)
        p.px(round(x2), round(y2), S[max(1, t - 2 + k)])
