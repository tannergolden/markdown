# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Oracle set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is the wall of a small kitchen in 1999, papered in apricot with pinstripes and sprigs of tiny flowers,
tone on tone, warm and dark by night. Oak trim runs down its sides and along its foot, and across a header's top
runs a band of glazed cream tiles, each with a little blue flower, over an oak rail hung with the kitchen's spoons
and ladles, one spoon among them bent, the steam of the baking billowing under it. Titles are cookies, the letters
baked in golden dough studded with chocolate chips, their edges baked dark and their rims pale and crumbly, each
standing off the wall on its own thickness; by night the oven's green light catches their edges and glows round
them. Headers open on the kitchen on its linoleum: the almond oven with its window glowing phosphor and a tray of
cookies steaming on its cooktop under the hood's light, a counter with a mug on it under a window hung with gingham,
the code falling past it by night and the oven's light pooling on the floor; and through a tall doorway on the room
beyond, a jug of sunflowers on a little table under the clock, a child in a saffron robe sitting cross-legged with a
spoon that bends, his toy blocks in the air, and a black cat that walks past, and then walks past again exactly as
it did the first time. A section has the dresser wall, the oak dresser with its plates and its radio, the cat asleep
on its crown, the table where the blue vase tips and falls and the pendant lamp over it; a strip, the refrigerator
in its corner with the cat sitting before it, its door ajar by night. A footer stands on the linoleum with the
kitchen's corner after its last cell, the cookie jar and the mug on a cabinet under the night light; a link is a
long cookie iced along its top; and the elements are the kitchen's recipe cards, twine, cookies, tiles, jars and
sampler. Everything is shaded from the one light in the upper left on the set's own ramps, and every light is the
hand's phosphor."""
from __future__ import annotations

import math
import random
from functools import lru_cache

from ...holidays.pixel import FONTS, Paint, Pix, fold, num, sphere, tube
from .. import rain
from .palette import C, NIGHT_SKY, RAMP, X, step

PAPER, UMBER, OAK, GLAZE, BLUE = RAMP["paper"], RAMP["umber"], RAMP["oak"], RAMP["glaze"], RAMP["blue"]
ENAMEL, STEEL, DOUGH, CHOC, RED = RAMP["enamel"], RAMP["steel"], RAMP["dough"], RAMP["choc"], RAMP["red"]
SUN, LEAF, ROBE, CAT, SKY = RAMP["sun"], RAMP["leaf"], RAMP["robe"], RAMP["cat"], RAMP["sky"]
FLAME, SKIN = RAMP["flame"], RAMP["skin1"]
EDGE = 4          # the trim's width down the sides and along the foot
TOP = 13          # the rows a header's band of tiles and its rail take across its top
TILE_W, TILE_H = 8, 7


def _t(R, i):
    """Tone `i` of ramp R, held to the ramp's ends."""
    return R[max(0, min(len(R) - 1, i))]


def _shade(R, k: int):
    """Ramp R stepped `k` tones (down, as by night, when negative), as a function of the tone: `_shade(R, k)(i)` is
    tone i + k, held to the ramp's ends."""
    def tone(i):
        return _t(R, i + k)
    return tone


def fill(p: Pix, x, y, w, h, c, L="base"):
    """A block of one colour, w by h, its top-left at (x, y), laid as one shape under the pixels of layer L: the same
    on the screen as its pixels, in a fraction of the bytes. What is drawn over it on its layer stays over it."""
    if w > 0 and h > 0:
        if L not in p.layers:
            p.layer(L)
        p.shapes[L].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>')


# --------------------------------------------------------------------------- the wallpaper
def _sprigs(night: bool) -> dict:
    """The wallpaper's tile, sixteen units square: a pair of pinstripes with a dotted line between them, and between
    the stripes a three-petalled flower over a leaf and a cluster of berries under a stalk, tone on tone."""
    if night:
        line, dot, petal, heart = UMBER[3], UMBER[4], UMBER[4], UMBER[5]
    else:
        line, dot, petal, heart = PAPER[4], PAPER[6], PAPER[4], PAPER[3]
    cells = {}
    for y in range(16):
        cells[(0, y)] = line
        cells[(2, y)] = line
    for y in (1, 5, 9, 13):
        cells[(1, y)] = dot
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        cells[(9 + dx, 4 + dy)] = petal
    cells[(9, 4)] = heart
    cells[(10, 6)] = petal
    cells[(11, 7)] = petal
    for dx, dy in ((0, 0), (1, 1), (-1, 1)):
        cells[(9 + dx, 12 + dy)] = petal
    cells[(9, 11)] = heart
    return cells


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the kitchen's wallpaper, apricot by day and by night a warm dark that deepens
    under the ceiling, papered in pinstripes and sprigs of flowers in its own tones."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
    p.defs.append(f'<pattern id="{uid}w" x="5" width="16" height="16" patternUnits="userSpaceOnUse">'
                  f'{p.markup(_sprigs(night))}</pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}w)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the wallpaper's ground, by night its band."""
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        return next(NIGHT_SKY[i] for i in range(n) if y < edges[i + 1] or i == n - 1)
    return C["paper"]


# --------------------------------------------------------------------------- the frame
def _tile_cells(night: bool) -> dict:
    """One glazed tile and its grout, TILE_W by TILE_H: cream, glossy at its upper left and in shade at its foot and
    right, with a little blue flower in its middle; by night the glaze in the dark, its gloss a green glint."""
    k = -3 if night else 0
    cells = {}
    for y in range(TILE_H):
        for x in range(TILE_W):
            if x == TILE_W - 1 or y == TILE_H - 1:
                cells[(x, y)] = _t(GLAZE, 1 + k)
            elif y == 0 or x == 0:
                cells[(x, y)] = _t(GLAZE, 6 + k)
            elif x == TILE_W - 2 or y == TILE_H - 2:
                cells[(x, y)] = _t(GLAZE, 3 + k)
            else:
                cells[(x, y)] = _t(GLAZE, 4 + k)
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        cells[(3 + dx, 3 + dy)] = _t(BLUE, 3 + (k // 2))
    cells[(3, 3)] = _t(BLUE, 5 + k)
    cells[(1, 1)] = FLAME[3] if night else C["white"]
    return cells


def _tiles(p: Pix, x0, x1, y, night: bool, uid: str):
    """A run of glazed tiles from x0 to x1 with its top at row y, as a pattern laid once."""
    pid = f"{uid}tl"
    if ("pattern", pid) not in p.syms:
        p.defs.append(f'<pattern id="{pid}" x="{EDGE}" y="{y}" width="{TILE_W}" height="{TILE_H}" '
                      f'patternUnits="userSpaceOnUse">{p.markup(_tile_cells(night))}</pattern>')
        p.syms[("pattern", pid)] = pid
    p.shapes[p.layer("tiles", z=-1)].append(
        f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{TILE_H}" fill="url(#{pid})"/>')


def frame(p: Pix, night: bool, header: bool = False, clear=None):
    """The border: oak trim down the sides and along the foot, a moulding lit on its slopes that face the light and
    in shade on those that face away, mitred at the corners. Across a header's top runs a band of glazed tiles over
    an oak rail, parting either side of `clear`, the columns kept for the month's mark; a footer's top is trim."""
    w, h = p.w, p.h
    k = -1 if night else 0

    def o(i):
        return _t(OAK, i + k)
    left = (OAK[0], o(5), o(4), o(2))          # from the outer edge in
    right = (OAK[0], o(2), o(3), o(5))
    foot = (OAK[0], o(2), o(4), o(5))
    for i, c in enumerate(foot):
        p.hline(i, w - i, h - 1 - i, c)
    for i, c in enumerate(left):
        p.vline(i, 0, h - i, c)
    for i, c in enumerate(right):
        p.vline(w - 1 - i, 0, h - i, c)
    for i in range(EDGE):                       # the mitres at the foot's corners
        p.px(i, h - 1 - i, OAK[1])
        p.px(w - 1 - i, h - 1 - i, OAK[1])
    rnd = random.Random(5)
    for x in range(EDGE + 6, w - EDGE - 6, 17):  # the grain along the foot
        p.hline(x, x + rnd.randint(3, 6), h - 3, o(3))
    if not header:
        top = (OAK[0], o(5), o(4), o(2))
        for i, c in enumerate(top):
            p.hline(i, w - i, i, c)
        return
    p.hline(0, w, 0, OAK[0])
    p.hline(1, w - 1, 1, o(5))
    p.hline(2, w - 2, 2, o(3))
    spans = [(EDGE, w - EDGE)]
    if clear:
        spans = [(EDGE, clear[0]), (clear[1], w - EDGE)]
    uid = "fr"
    for a, b in spans:
        _tiles(p, a, b, 3, night, uid)
        p.hline(a, b, 3 + TILE_H, o(5))      # the rail: lit along its top, in shade under it
        p.hline(a, b, 4 + TILE_H, o(3))
        p.hline(a, b, 5 + TILE_H, o(1))
        p.hline(a, b, 6 + TILE_H, UMBER[1] + ":0.5" if night else PAPER[3] + ":0.5")
        for x in (a, b - 1):                   # the band's ends, trimmed in oak
            if EDGE < x < w - EDGE - 1:
                p.vline(x, 3, 6 + TILE_H, o(4) if x == a else o(2))
                p.px(x, 6 + TILE_H, OAK[1])


# --------------------------------------------------------------------------- the utensils on the rail
# The kitchen's utensils as they hang from the rail on their hooks, each as rows of pixels: s steel (S lit, d in
# shade), w wood (W lit), h the hook.
UTENSILS = {
    "ladle": ["h", "s", "S", "s", "s", "s", "s", ".dSSs.", "ddsssd", ".dddd."],
    "whisk": ["h", "s", "w", "W", "w", ".sSs.", "s.S.s", "s.S.s", "s.s.s", ".sss."],
    "spatula": ["h", "w", "W", "w", "w", "s", ".SSSs", ".SsSs", ".SSSs", ".ssss"],
    "spoon": ["h", "w", "W", "w", "w", "w", ".WWw.", ".Www.", ".www.", "..w.."],
    "slotted": ["h", "s", "S", "s", "s", "s", ".SSSs", ".S.Ss", ".SS.s", "..ss."],
    "bent": ["h", "s", "S", "s", "s", ".s", "..s", "..SSs", "..ssd"],
}
LOWEST = 22       # the lowest row a utensil reaches, two rows clear of a header's title, which starts at row 26


def utensil(p: Pix, x, y, kind: str, night: bool):
    """A utensil hanging from the rail with the top of its hook at (x, y), its handle centred on column x, cut short
    of row LOWEST."""
    art = UTENSILS[kind][:LOWEST - y + 1]
    k = -2 if night else 0
    pal = {"s": _t(STEEL, 4 + k), "S": _t(STEEL, 6 + k), "d": _t(STEEL, 2 + k), "w": _t(OAK, 4 + k),
           "W": _t(OAK, 6 + k), "h": _t(STEEL, 3 + k)}
    for j, row in enumerate(art):
        ox = x - len(row) // 2
        for i, ch in enumerate(row):
            if ch in pal:
                p.px(ox + i, y + j, pal[ch])


def utensils(p: Pix, x0, x1, night: bool, clear=None, keep=()):
    """The utensils hung along the rail between x0 and x1, a little apart, none in `clear` (the columns kept for the
    month's mark) nor in any box of `keep`."""
    kinds = ["ladle", "whisk", "spatula", "spoon", "slotted", "ladle", "bent", "whisk", "spoon", "spatula"]
    y = 6 + TILE_H
    xs = [x for x in range(x0, x1, 21)]
    i = 0
    for x in xs:
        if clear and clear[0] - 3 <= x <= clear[1] + 3:
            continue
        kind = kinds[i % len(kinds)]
        i += 1
        if any(a - 3 <= x <= c + 3 and b <= y + len(UTENSILS[kind]) + 2 for a, b, c, d in keep):
            continue
        utensil(p, x, y, kind, night)


# --------------------------------------------------------------------------- the titles
@lru_cache(maxsize=None)
def _texture(scale: int, variant: int) -> dict:
    """A tile of baked dough a letter wide and a letter tall, as {(column, row): tone}: the dough's gold with paler
    lumps where it rose and darker cracks where it split, and chocolate chips of two or three sizes, each lit at its
    upper left and in shade along its foot. The chips and lumps keep mostly to where a letter's strokes run, its
    sides and its top, middle and foot, so most of them show."""
    rnd = random.Random(scale * 31 + variant * 7)
    w, h, u = 5 * scale, 7 * scale, scale
    out = {}

    def inked(c, r):
        return c < u or c >= w - u or r // u in (0, 3, 6)

    def spot(cw, ch):
        for _ in range(60):
            c, r = rnd.randrange(w - cw + 1), rnd.randrange(h - ch + 1)
            cells = [(c + i, r + j) for j in range(ch) for i in range(cw)]
            if all(inked(*q) and q not in out for q in cells):
                return c, r
        return None
    for _ in range(4 if scale >= 4 else 3):            # the lumps
        at = spot(2, 1)
        if at:
            out[at] = "lump"
            out[(at[0] + 1, at[1])] = "lump"
    for _ in range(2 if scale >= 3 else 1):            # the cracks
        at = spot(3, 1)
        if at:
            out[at] = "crack"
            out[(at[0] + 1, at[1] + (1 if at[1] + 1 < h else 0))] = "crack"
            out[(at[0] + 2, at[1] + (1 if at[1] + 1 < h else 0))] = "crack"
    sizes = [(2, 2), (3, 2), (2, 2), (2, 3), (3, 2), (2, 2)] if scale >= 3 else [(1, 1)] * 4
    for cw, ch in sizes[:6 if scale >= 4 else 4]:      # the chips
        at = spot(cw, ch)
        if not at:
            continue
        c, r = at
        for j in range(ch):
            for i in range(cw):
                out[(c + i, r + j)] = "lit" if (i, j) == (0, 0) and cw * ch > 1 else "foot" if j == ch - 1 else "chip"
    return out


def _dough(night):
    """The dough's paint: a tile of baked dough a letter wide (see `_texture`), the gold a step darker by night."""
    def fill(r, c, scale, _night, variant=0):
        k = -1 if night else 0
        part = _texture(min(4, scale), variant).get((c, r))
        if part == "lit":
            return CHOC[5]
        if part == "chip":
            return CHOC[2]
        if part == "foot":
            return CHOC[1]
        if part == "lump":
            return _t(DOUGH, 6 + k)
        if part == "crack":
            return _t(DOUGH, 2 + k)
        return _t(DOUGH, 5 + k) if r < scale else _t(DOUGH, 4 + k)
    return fill


def _paint(scale: int, night: bool) -> Paint:
    return Paint(("dn" if night else "dd") + str(scale), _dough(night), period=5 * min(4, scale))


def _crumbs(night: bool):
    """The baked edge: a letter's rim made uneven with lumps of dough here and there, and crumbs fallen from its
    foot, pale by day and lit green by night."""
    def finish(p: Pix, cells, scale, layer, rnd, y):
        if scale < 3:
            return
        rim = DOUGH[3] if night else DOUGH[6]
        for (x, yy) in sorted(cells):
            r = rnd.random()
            if (x, yy + 1) not in cells and r < 0.07:
                q = (x + rnd.choice((-1, 0, 1)), yy + 3)
                if all((q[0] + a, q[1] + b) not in cells for a in (-1, 0, 1) for b in (-2, -1, 0, 1)):
                    p.px(q[0], q[1], rim, layer)
            elif (x - 1, yy) not in cells and (x, yy - 1) in cells and r < 0.05:
                p.px(x - 2, yy, rim, layer)
    return finish


def _word(p: Pix, x, s, scale):
    """A line of a title's letters kept once as a single drawing with no colour of its own, its top-left at its
    origin: so its outline and its thickness are each the whole line placed again, not every letter again."""
    key = ("word", s, scale)
    if key not in p.syms:
        glyphs, _, space = FONTS["57"]
        parts, cx = [], 0
        for ch in fold(s, "57"):
            if ch == " ":
                cx += space + 1
                continue
            parts.append(f'<use href="#{p.syms[("glyph", "57", ch)]}"' + (f' x="{cx}"/>' if cx else "/>"))
            cx += glyphs[ch][0] + 1
        p.symbol(key, {}, shapes=f'<g transform="scale({scale})">' + "".join(parts) + "</g>")
    return key


def beneath(p: Pix, name: str, dz: float) -> str:
    """The layer `name`, just under the words at depth `dz`; or, while a part is drawn onto a layer of its own (see
    `Pix.onto`), as a game's panel draws each section that appears in turn, its twin just under that layer, so what
    is baked under a word appears with it."""
    into = getattr(p, "into", None)
    if not into:
        return p.layer(name, z=dz)
    twin = into + name
    if twin not in p.layers:
        z, anim = (p.meta[into][0], p.meta[into][2]) if into in p.meta else (0, None)
        p.layer(twin, anim, z=z + dz)
    return twin


def cookie_title(p: Pix, x, y, s, night: bool, scale: int) -> int:
    """A title baked as cookies: each letter golden dough studded with chocolate chips, its edge crisp and baked
    dark, its rim pale and crumbly along its left where the light catches it and darker where it was baked against
    the tray at its foot, a crumb or two fallen under it; and under each face the cookie's thickness, baked brown,
    over its shadow on the wallpaper, so the letters stand off the wall. By night the oven's green light catches
    the letters' left edges and glows round them. Returns its width."""
    kw = dict(paint=_paint(scale, night), night=night, finish=_crumbs(night))
    if night:
        if scale >= 3:
            kw["bevel"] = (FLAME[3], DOUGH[1])
        kw["glow"] = (FLAME[3], (0.2,) if scale >= 3 else (0.12,))
        rim, steps = DOUGH[1], (((2, DOUGH[0]),) if scale >= 3 else ((1, UMBER[0]),))
    else:
        if scale >= 3:
            kw["bevel"] = (DOUGH[6], DOUGH[2])
        rim, steps = CHOC[2], (((3, PAPER[2]), (2, CHOC[2])) if scale >= 3 else ((1, PAPER[2]),))
    w = p.text(x, y, s, DOUGH[4], "57", scale, **kw)
    if night and p.lite:
        return w            # by night the baked rim barely shows on the dark paper: a lighter drawing lets it go
    key, L = _word(p, x, s, scale), beneath(p, "dough", -0.05)
    for d, col in steps:
        p.use(key, x + d, y + d, L, stroke=col)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        p.use(key, x + dx, y + dy, L, stroke=rim)
    return w


# --------------------------------------------------------------------------- light
def lit_on(p: Pix, cells, col, alphas, cx, cy, rx, ry):
    """The light of a lamp at (cx, cy) laid over the drawn pixels `cells` within rx by ry of it, stepped; a drawing
    made lighter lays only the inner steps, where it is strongest."""
    if p.lite and len(alphas) > 1:
        alphas, rx, ry = alphas[len(alphas) // 2:], rx * 0.6, ry * 0.6
    n = len(alphas)
    for (x, y) in cells:
        d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
        if d < 1:
            p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], "base")


def near(p: Pix, x0, y0, x1, y1, colours) -> list:
    """The pixels of the base layer from (x0, y0) to (x1, y1), ends excluded, whose colour is one of `colours`."""
    return [(x, y) for (x, y), c in p.layers["base"].items() if x0 <= x < x1 and y0 <= y < y1 and c in colours]


# --------------------------------------------------------------------------- the oven
def slab(p: Pix, x, y, w, h, R, k=0, face=4, outline=True):
    """A block on ramp R, its face in tone `face`, lit along its top and left and in shade along its foot and
    right, outlined a pixel round in the ramp's darkest tone. `k` steps every tone down, as by night."""
    if outline:
        p.box(x - 1, y - 1, w + 2, h + 2, R[0])
    fill(p, x, y, w, h, _t(R, face + k))
    p.hline(x, x + w, y, _t(R, face + 2 + k))
    p.vline(x, y + 1, y + h, _t(R, face + 1 + k))
    p.vline(x + w - 1, y + 1, y + h, _t(R, face - 2 + k))
    p.hline(x + 1, x + w, y + h - 1, _t(R, face - 2 + k))


def knob(p: Pix, x, y, night):
    """A steel knob, two by two, lit at its upper left."""
    k = -2 if night else 0
    p.px(x, y, _t(STEEL, 6 + k))
    p.px(x + 1, y, _t(STEEL, 4 + k))
    p.px(x, y + 1, _t(STEEL, 3 + k))
    p.px(x + 1, y + 1, _t(STEEL, 1 + k))


COOKIE = [".llll.", "lLDcDd", "DcDDdD", ".dddd."]


def cookie(p: Pix, x, y, night, L="base"):
    """A cookie fresh from the oven, six by four: domed, lit at its upper left, its chips showing."""
    k = -1 if night else 0
    pal = {"l": _t(DOUGH, 6 + k), "L": _t(DOUGH, 5 + k), "D": _t(DOUGH, 4 + k), "c": CHOC[1],
           "d": _t(DOUGH, 2 + k)}
    p.sprite(x, y, COOKIE, pal, L=L, reuse=True)


def oven(p: Pix, x, g, night: bool, motion: bool) -> dict:
    """The almond range standing on the floor at row g from column x, twenty-six wide: its backguard with a clock
    lit in phosphor between its knobs, the steel cooktop with a tray of cookies on it, and the oven door with its
    handle and its window glowing phosphor, the cookies inside on their rack against the element, which flickers.
    Returns its cooktop's row and its window's middle."""
    W = 26
    k = -2 if night else 0
    top = g - 25
    slab(p, x + 2, top - 10, W - 4, 9, ENAMEL, k)             # the backguard
    p.rect(x + 9, top - 9, 8, 4, STEEL[0])
    for dx, dy in ((10, -8), (11, -8), (13, -8), (14, -8), (15, -8), (10, -7), (15, -7), (11, -6), (10, -6),
                   (14, -6), (15, -6), (13, -6)):
        p.px(x + dx, top + dy, FLAME[4])
    p.px(x + 12, top - 7, FLAME[5], p.blink(0) if motion else "base")
    p.hline(x + 9, x + 17, top - 5, STEEL[1])
    for kx in (x + 4, x + 6, x + 19, x + 21):
        knob(p, kx, top - 8, night)
    p.hline(x, x + W, top, _t(STEEL, 5 + k))                  # the cooktop
    p.hline(x, x + W, top + 1, _t(STEEL, 3 + k))
    p.hline(x + 1, x + W - 1, top + 2, STEEL[0])
    slab(p, x + 1, top + 4, W - 2, 20, ENAMEL, k)             # the body
    for kx in (x + 4, x + 8, x + 16, x + 20):
        knob(p, kx, top + 5, night)
    p.hline(x + 3, x + W - 3, top + 8, _t(ENAMEL, 2 + k))     # the door, its handle and its window
    p.hline(x + 4, x + W - 4, top + 9, _t(STEEL, 6 + k))
    p.hline(x + 4, x + W - 4, top + 10, _t(STEEL, 2 + k))
    wx0, wy0, ww, wh = x + 5, top + 12, W - 10, 8
    p.box(wx0 - 1, wy0 - 1, ww + 2, wh + 2, STEEL[0])
    glow = p.flicker(1) if motion else "base"
    for yy in range(wy0, wy0 + wh):
        p.hline(wx0, wx0 + ww, yy, FLAME[1] if yy < wy0 + 2 else FLAME[2] if yy < wy0 + wh - 2 else FLAME[3])
    p.hline(wx0 + 1, wx0 + ww - 1, wy0 + wh - 1, FLAME[5], glow)
    p.px(wx0, wy0, FLAME[6], glow)
    p.px(wx0 + 1, wy0, FLAME[5], glow)
    p.hline(wx0, wx0 + ww, wy0 + 5, STEEL[1])                # the rack, and the cookies on it
    for i in range(3):
        cx = wx0 + 1 + i * 5
        p.hline(cx, cx + 4, wy0 + 4, CHOC[2])
        p.hline(cx + 1, cx + 3, wy0 + 3, CHOC[3])
        p.hline(cx + 1, cx + 3, wy0 + 2, FLAME[4])
    for i in range(3):                                       # the glass's gleam
        p.px(wx0 + ww - 2 - i, wy0 + 1 + i, FLAME[6])
    p.hline(x + 3, x + W - 3, g - 4, _t(ENAMEL, 2 + k))       # the drawer and the toe kick
    p.hline(x + 10, x + W - 10, g - 2, _t(STEEL, 2 + k))
    p.hline(x + 1, x + W - 1, g, ENAMEL[0])
    p.hline(x + 1, x + W - 1, g - 1, _t(ENAMEL, 1 + k))
    p.hline(x + 2, x + W - 2, top - 1, _t(STEEL, 6 + k))      # the tray of cookies
    p.px(x + 1, top - 1, _t(STEEL, 3 + k))
    p.px(x + W - 2, top - 1, _t(STEEL, 2 + k))
    for i in range(4):
        cookie(p, x + 1 + i * 6, top - 5, night)
    cx, cy = wx0 + ww / 2, wy0 + wh / 2
    if night:
        p.halo(cx, cy - 2, 26, 11, FLAME[3], (0.04, 0.07, 0.11), L=p.flicker(1, back=True) if motion else "haze")
    return dict(top=top, window=(cx, cy))


def _wisp(length, rise, waves, amp, curl, phase=0.0) -> list:
    """A curl of steam as the pixels of a line a unit wide, in order from its foot: it rises to the right in a
    lazy S, its swing dying away as it goes, and turns over at its end into a curl that closes on itself."""
    pts = []
    for i in range(601):
        t = i / 600
        pts.append((length * t, -rise * t + amp * math.sin(2 * math.pi * (waves * t + phase)) * (1 - 0.5 * t)))
    ex, ey = pts[-1]
    for i in range(1, 300):
        a, r = i / 300 * 1.6 * math.pi, curl * (1 - 0.5 * i / 300)
        pts.append((ex + r * math.sin(a), ey - r + r * math.cos(a)))
    cells = []
    for x, y in pts:
        c = (math.floor(x + 0.5), math.floor(y + 0.5))
        if (not cells or c != cells[-1]) and c not in cells[-3:]:
            cells.append(c)
    line = [cells[0]]
    for i in range(1, len(cells) - 1):          # no elbows: a unit dropped where its neighbours touch diagonally
        a, b = line[-1], cells[i + 1]
        if abs(a[0] - b[0]) > 1 or abs(a[1] - b[1]) > 1:
            line.append(cells[i])
    return line + [cells[-1]]


# The steam in one stretch of the drift, PERIOD wide, from the top of the band it drifts in: its clouds, each as
# puffs (x, y, rx, ry) laid together, and the denser heart of each; and the curls that turn over on top of them,
# (the curl's shape, where its foot is).
CLOUDS = ((7, 16, 8, 3.5), (17, 12, 10, 5), (29, 13, 9, 4), (39, 16, 6, 3), (53, 6, 7, 3.5), (63, 4, 8, 4),
          (72, 6, 6, 3), (80, 31, 7, 3.5), (91, 27, 9, 5), (101, 31, 7, 3.5))
HEARTS = ((17, 12, 7, 3), (29, 13, 5, 2.5), (63, 4, 5, 2.5), (91, 27, 6, 3))
WISPS = (((22, 6, 1.0, 2.0, 2.4, 0.5), (25, 16)), ((16, 4, 0.9, 1.5, 2.0, 0.25), (60, 8)),
         ((18, 5, 1.0, 2.0, 2.2, 0.0), (86, 31)))
PERIOD = 104
DRIFT = 48.0      # the seconds the steam takes to drift a stretch to the right


def vapour(p: Pix, night: bool, motion: bool, band, title, mark):
    """The signature of a header's sky: the steam of the baking billowing across the kitchen under its rail, soft
    clouds of it with denser hearts, curls turning over on top of them, drifting slowly to the right from the oven
    at the left, a stretch every 48 seconds, behind the title and through the top band but never into the month's
    mark (`mark`), and ending above the words under the title. `band` is the box it drifts in; behind the title's
    letters (`title`) it is fainter, so they read through it. By day it is the cream of the steam over the paper; by
    night the oven's green light caught in it. The still file holds it where it starts."""
    x0, y0, x1, y1 = band
    curls = []
    for k, (shape, (fx, fy)) in enumerate(() if (night and p.lite) else WISPS):
        key = ("wisp", k)
        p.symbol(key, {c: 1 for c in _wisp(*shape)}, mono=True)
        curls.append(f'<use href="#{p.syms[key]}" x="{fx}" y="{y0 + fy}"/>')

    def puffs(spec):
        return "".join(f'<ellipse cx="{cx}" cy="{num(y0 + cy)}" rx="{num(rx)}" ry="{num(ry)}"/>'
                       for cx, cy, rx, ry in spec)
    col, (a, b, c) = (FLAME[5], (0.1, 0.1, 0.26)) if night else (X["steam"], (0.55, 0.5, 0.8))
    p.defs.append(f'<g id="stt" fill="{col}"><g opacity="{num(a)}">{puffs(CLOUDS)}</g><g opacity="{num(b)}">'
                  f'{puffs(HEARTS)}</g><g stroke="{col}" stroke-opacity="{num(c)}">{"".join(curls)}</g></g>')
    tx0, ty0, tx1, ty1 = title
    p.defs.append(f'<mask id="stm" maskUnits="userSpaceOnUse" x="0" y="0" width="{p.w}" height="{y1}">'
                  f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{C["white"]}"/>'
                  f'<rect x="{tx0}" y="{ty0}" width="{tx1 - tx0}" height="{ty1 - ty0}"/>'
                  f'<rect x="{tx0}" y="{ty0}" width="{tx1 - tx0}" height="{ty1 - ty0}" fill="{C["white"]}" '
                  f'fill-opacity=".45"/>'
                  f'<rect x="{mark[0]}" y="{mark[1]}" width="{mark[2] - mark[0]}" height="{mark[3] - mark[1]}"/>'
                  f'</mask>')
    uses = "".join(f'<use href="#stt" x="{n * PERIOD}"/>' for n in range(-1, p.w // PERIOD + 1))
    head = '<g mask="url(#stm)">'
    if not motion:
        still = head + uses + "</g>"
        p.raw(-0.95, still, still)
        return
    vals = ";".join(f"{i} 0" for i in range(PERIOD))
    moving = (head + f'<g>{uses}<animateTransform attributeName="transform" type="translate" values="{vals}" '
              f'dur="{num(DRIFT)}s" repeatCount="indefinite" calcMode="discrete"/></g></g>')
    p.raw(-0.95, moving, head + uses + "</g>")


STEAM_LOOP = 3.6   # the seconds every steam in a drawing takes to rise through its three frames


def steam(p: Pix, x0, x1, y, night: bool, motion: bool, seed=3, tall=False):
    """Steam curling up off something hot from x0 to x1 at row y, in three frames that rise and thin, on the loop
    every steam in a drawing shares; the still file keeps the second. `tall` steam, off a tray fresh from the oven,
    rises in longer wisps. By night it carries the green of the light it rises through."""
    rnd = random.Random(seed)
    col = (FLAME[5] + ":0.4") if night else (X["steam"] + ":0.85")
    wisps = [(rnd.randrange(x0, x1), rnd.randrange(3)) for _ in range(max(2, (x1 - x0) // 5))]
    n, rise = (5, 3) if tall else (3, 2)
    for f in range(3):
        if motion:
            L = p.seq(f"st{f}", f / 3, (f + 1) / 3, STEAM_LOOP, keep=f == 1, z=4)
        elif f == 1:
            L = "near"
        else:
            continue
        for wx, ph in wisps:
            for j in range(n - (f == 2) * (2 if tall else 1)):
                p.px(wx + (1 if (j + f + ph) % 4 < 2 else 0), y - 1 - j - f * rise, col, L)


def hood(p: Pix, x, y, w, night: bool, motion: bool, up_to: int):
    """The range hood over the oven, its lip at row y: an almond canopy narrowing to its duct, which runs up to row
    `up_to` in sections, and under its lip a strip light burning phosphor that throws a cone down over the stove."""
    k = -2 if night else 0
    for i in range(7):
        a, b = x + i // 2, x + w - i // 2
        p.hline(a, b, y - i, _t(ENAMEL, (5 if i == 6 else 4) + k))
        p.px(a, y - i, _t(ENAMEL, 6 + k))
        p.px(b - 1, y - i, _t(ENAMEL, 2 + k))
    p.hline(x - 1, x + w + 1, y + 1, ENAMEL[0])
    p.hline(x, x + w, y, _t(ENAMEL, 3 + k))
    p.hline(x + 3, x + w - 3, y - 7, ENAMEL[0])
    dx0, dx1 = x + w // 2 - 4, x + w // 2 + 4
    n = y - 7 - up_to
    fill(p, dx0 + 2, up_to, dx1 - dx0 - 3, n, _t(ENAMEL, 3 + k))
    fill(p, dx0, up_to, 1, n, _t(ENAMEL, 5 + k))
    fill(p, dx0 + 1, up_to, 1, n, _t(ENAMEL, 4 + k))
    fill(p, dx1 - 1, up_to, 1, n, _t(ENAMEL, 1 + k))
    for yy in range(up_to + 4, y - 8, 7):
        p.hline(dx0, dx1, yy, _t(ENAMEL, 1 + k))
        p.hline(dx0, dx1, yy + 1, _t(ENAMEL, 5 + k))
    lamp = p.flicker(2) if motion else "base"
    p.hline(x + 3, x + w - 3, y + 1, FLAME[5], lamp)
    a = 0.18 if night else 0.1
    for j in range(2, 13):
        p.hline(x + 3 - j // 3, x + w - 3 + j // 3, y + 1 + j, FLAME[4] + f":{a:g}", "haze")


# --------------------------------------------------------------------------- the counter and the window
def counter(p: Pix, x0, x1, g, top, night: bool):
    """The counter from x0 to x1, its laminate top at row `top`: a pale top lit along its edge, an oak front of two
    cupboard doors with their brass knobs, and the toe kick in shadow."""
    k = -2 if night else 0
    p.hline(x0, x1, top, _t(GLAZE, 6 + k))
    p.hline(x0, x1, top + 1, _t(GLAZE, 4 + k))
    p.hline(x0, x1, top + 2, _t(GLAZE, 2 + k))
    p.hline(x0, x1, top + 3, OAK[0])
    slab(p, x0 + 1, top + 4, x1 - x0 - 2, g - top - 6, OAK, k, face=4, outline=False)
    mid = (x0 + x1) // 2
    p.vline(mid, top + 5, g - 2, OAK[1])
    for dx0, dx1 in ((x0 + 3, mid - 1), (mid + 2, x1 - 3)):
        p.box(dx0, top + 6, dx1 - dx0, g - top - 10, _t(OAK, 2 + k))
        p.hline(dx0 + 1, dx1 - 1, top + 7, _t(OAK, 5 + k))
        p.vline(dx0 + 1, top + 8, g - 5, _t(OAK, 5 + k))
    for kx in (mid - 3, mid + 2):
        p.px(kx, top + 11, SUN[5] if not night else SUN[2])
        p.px(kx + 1, top + 11, SUN[3] if not night else SUN[1])
    p.hline(x0 + 1, x1 - 1, g - 1, OAK[1])
    p.hline(x0 + 1, x1 - 1, g, OAK[0])


def mug(p: Pix, x, y, night: bool):
    """A red mug of coffee standing at row y, its handle at its right, lit at its upper left."""
    k = -1 if night else 0
    art = [".cccc..", "llrrrd.", "lrrrdhd", "lrrrdhd", "lrrrd..", ".dddd.."]
    pal = {"c": _t(CHOC, 3), "l": _t(RED, 5 + k), "r": _t(RED, 4 + k), "d": _t(RED, 2 + k), "h": _t(RED, 1 + k)}
    p.sprite(x, y - len(art) + 1, art, pal)


def jar(p: Pix, x, y, night: bool):
    """A glass cookie jar standing at row y, its lid knobbed, the cookies stacked in it showing through the glass."""
    k = -2 if night else 0
    art = ["..kk..", ".LLLL.", "gWWWWg", "gDDDDg", "gcDcDg", "gDDcDg", "gcDDDg", ".gggg."]
    pal = {"k": _t(STEEL, 5 + k), "L": _t(STEEL, 4 + k), "g": _t(GLAZE, 5 + k), "W": _t(GLAZE, 6 + k),
           "D": _t(DOUGH, 4 + k), "c": _t(DOUGH, 2 + k)}
    p.sprite(x, y - len(art) + 1, art, pal)


def backsplash(p: Pix, x0, x1, y0, y1, night: bool, uid="bs"):
    """Small square tiles behind the counter, from x0 to x1 and rows y0 to y1, as a pattern laid once."""
    k = -3 if night else 0
    cells = {}
    for yy in range(4):
        for xx in range(4):
            cells[(xx, yy)] = _t(GLAZE, 1 + k) if (xx == 3 or yy == 3) else \
                _t(GLAZE, 6 + k) if (xx == 0 and yy == 0) else _t(GLAZE, 4 + k)
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{y0}" width="4" height="4" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells)}</pattern>')
    p.shapes[p.layer("tiles", z=-1)].append(
        f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{uid})"/>')


def gingham(p: Pix, night: bool) -> str:
    """The curtains' gingham as a pattern: red and cream checked two units square, deepest where the stripes
    cross. Returns its fill."""
    pid = "gg"
    if ("pattern", pid) not in p.syms:
        k = -2 if night else 0
        light, mid, dark = _t(GLAZE, 6 + k - (1 if night else 0)), _t(RED, 5 + k), _t(RED, 3 + k)
        cells = {}
        for yy in range(4):
            for xx in range(4):
                cells[(xx, yy)] = (light, mid, mid, dark)[(xx >= 2) + 2 * (yy >= 2)]
        p.defs.append(f'<pattern id="{pid}" width="4" height="4" patternUnits="userSpaceOnUse">{p.markup(cells)}'
                      f'</pattern>')
        p.syms[("pattern", pid)] = pid
    return f"url(#{pid})"


def stair(x, y0, widths, side=0) -> str:
    """Path data for a shape of whole units, row y0 down, each row `widths[j]` wide, standing on column x at its
    left (side 0) or ending at it on its right (side 1): its outline traced in level and upright steps, a step only
    where its width changes, so its edge keeps to the grid."""
    sign = 1 if side == 0 else -1
    d = f"M{x} {y0}"
    j = 0
    while j < len(widths):
        e = j
        while e < len(widths) and widths[e] == widths[j]:
            e += 1
        d += f"H{x + sign * widths[j]}V{y0 + e}"
        j = e
    return d + f"H{x}z"


def window(p: Pix, x0, x1, y0, y1, night: bool, motion: bool):
    """The window over the counter from x0 to x1 and rows y0 to y1, its frame painted cream and lit at its upper
    left, its panes showing by day a hazy sky over the city and by night the code falling past in phosphor, a
    gingham valance across its top and the curtains tied back at its sides, a pot of basil on its sill."""
    k = -3 if night else 0
    gx0, gx1, gy0, gy1 = x0 + 2, x1 - 2, y0 + 2, y1 - 1
    pane = p.layer("pane", z=-0.8)
    if night:
        p.shapes[pane].append(f'<rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" height="{gy1 - gy0}" '
                              f'fill="{STEEL[0]}"/>')
        r = rain.Rain(p, (gx0, gy0, gx1, gy1), FLAME, True, seed=4, kinds=3, lengths=(3, 5))
        for i, cx in enumerate(range(gx0, gx1 - rain.W + 1, rain.COLUMN)):
            if p.lite and i % 2:
                continue            # a drawing made lighter keeps every other stream of the code
            r.stream(cx, gy0 + random.Random(cx).randrange(0, 5) * rain.PITCH, pace=0.1 + (cx % 3) * 0.02)
        r.fall(z=-0.5)
    else:
        n = gy1 - gy0
        a, b = gy0 + round(n * 0.35), gy0 + round(n * 0.7)
        for y0_, y1_, c in ((gy0, a, SKY[5]), (a, b, SKY[4]), (b, gy1, SKY[3])):
            fill(p, gx0, y0_, gx1 - gx0, y1_ - y0_, c, pane)
        rnd = random.Random(8)
        xx = gx0
        while xx < gx1:                              # the city, hazy, far off
            bw, bh = rnd.randint(3, 6), rnd.randint(4, (gy1 - gy0) * 2 // 3)
            p.rect(xx, gy1 - bh, min(bw, gx1 - xx), bh, SKY[2] if rnd.random() < 0.5 else SKY[1], pane)
            xx += bw + rnd.randint(0, 1)
    fr = _shade(GLAZE, k)
    p.box(x0, y0, x1 - x0, y1 - y0 + 1, GLAZE[0])
    p.box(x0 + 1, y0 + 1, x1 - x0 - 2, y1 - y0 - 1, fr(6))
    p.vline(x1 - 2, y0 + 2, y1, fr(3))
    p.hline(x0 + 2, x1 - 1, y1 - 1, fr(3))
    mx = (x0 + x1) // 2
    p.vline(mx, gy0, gy1, fr(5))
    p.vline(mx + 1, gy0, gy1, fr(3))
    my = (gy0 + gy1) // 2
    p.hline(gx0, gx1, my, fr(5))
    p.hline(gx0, gx1, my + 1, fr(3))
    p.hline(x0 - 2, x1 + 2, y1 + 1, fr(6))                    # the sill
    p.hline(x0 - 2, x1 + 2, y1 + 2, fr(3))
    p.hline(x0 - 1, x1 + 1, y1 + 3, GLAZE[0])
    kk = -2 if night else 0
    cloth = p.layer("cloth", z=0.2)                           # the valance and the curtains, in gingham
    folds = p.layer("folds", z=0.3)
    check = gingham(p, night)
    p.shapes[cloth].append(f'<rect x="{x0 - 3}" y="{y0 - 1}" width="{x1 - x0 + 6}" height="5" fill="{check}"/>')
    p.hline(x0 - 3, x1 + 3, y0 + 4, _t(RED, 2 + kk), folds)
    for xx in range(x0 - 3, x1 + 3, 3):
        p.px(xx, y0 + 5, _t(RED, 3 + kk), folds)
    h = y1 - y0 - 6
    tie = y0 + 5 + h // 2
    widths = [5 if yy < tie - 3 else 3 if yy <= tie + 1 else 4 for yy in range(y0 + 5, y1 - 1)]
    for side in (0, 1):
        a = x0 - 3 if side == 0 else x1 + 3
        p.shapes[cloth].append(f'<path fill="{check}" d="{stair(a, y0 + 5, widths, side)}"/>')
        for j, wdt in enumerate(widths):
            p.px(a + wdt - 1 if side == 0 else a - wdt, y0 + 5 + j, _t(RED, 2 + kk), folds)
        tx = a if side == 0 else a - 4
        p.hline(tx, tx + 4, tie, _t(RED, 1 + kk), folds)
    bx = x1 - 10                                              # the basil on the sill
    pot = [".tttt.", "tTTTTt", ".tTTt.", ".tttt."]
    p.sprite(bx, y1 - 3, pot, {"t": _t(RED, 2 + kk), "T": _t(RED, 4 + kk)})
    leaves = ["..l.l.", ".lLllL", "lLlLl.", ".llLl."]
    p.sprite(bx, y1 - 7, leaves, {"l": _t(LEAF, 3 + kk), "L": _t(LEAF, 5 + kk)})


def floor(p: Pix, x0, x1, g, night: bool) -> set:
    """The kitchen's linoleum from column x0 to x1, its four rows ending on the floor at row g: cream and pale blue
    checks, a narrow row of them at the back and deeper ones in front, set half a check apart so the floor lies
    down; by night in the dark. Laid as a pattern. Returns its colours, for the light that falls on it."""
    k = -4 if night else 0
    a, b = _t(GLAZE, 5 + k), _t(BLUE, 5 + k)
    pid = "lino"
    if ("pattern", pid) not in p.syms:
        cells = {}
        for xx in range(12):
            cells[(xx, 0)] = a if (xx // 3) % 2 else b
            for yy in (1, 2, 3):
                cells[(xx, yy)] = b if ((xx + 2) // 4) % 2 else a
        p.defs.append(f'<pattern id="{pid}" y="{g - 3}" width="12" height="4" patternUnits="userSpaceOnUse">'
                      f'{p.markup(cells)}</pattern>')
        p.syms[("pattern", pid)] = pid
    L = p.layer("lino", z=-0.6)
    p.shapes[L].append(f'<rect x="{x0}" y="{g - 3}" width="{x1 - x0}" height="4" fill="url(#{pid})"/>')
    return {a, b}


def pool(p: Pix, cx, x0, x1, g, rx, alphas, rows=4):
    """Light lying on the linoleum from x0 to x1 in its rows ending at row g, strongest under column cx and fading
    out to rx either side of it, stepped."""
    n = len(alphas)
    for yy in range(g - rows + 1, g + 1):
        for xx in range(max(x0, int(cx - rx)), min(x1, int(cx + rx) + 1)):
            d = abs(xx + 0.5 - cx) / rx
            if d < 1:
                p.apx(xx, yy, FLAME[4], alphas[min(n - 1, int((1 - d) * n))], "base")


def kitchen(p: Pix, x0, g, night: bool, motion: bool, reach: int, top: int, wtop: int) -> tuple:
    """The kitchen standing on its linoleum floor at row g from column x0: the range under its hood, the counter
    beside it with a mug and the cookie jar on it, the tiles behind it and the window over it, as wide as `reach`
    lets it run; the hood as tall as row `top` lets it stand and the window as tall as row `wtop` lets it. By night
    the oven and the hood light it green, and the oven's window throws its light out over the floor, a pool of it
    shimmering in the gloss of the linoleum. Returns the span it covers on the rule."""
    cx0, cx1 = x0 + 28, x0 + 51
    floor(p, x0 - 1, cx1 + 3, g, night)
    f = g - 4
    o = oven(p, x0 + 1, f, night, motion)
    ctop = o["top"]
    sill = ctop - 11
    x1 = min(reach, cx0 + 60)
    if wtop <= sill - 22 and x1 - cx0 >= 26:
        window(p, cx0 + 3, x1 - 4, max(wtop + 3, sill - 30), sill - 3, night, motion)
    backsplash(p, cx0, cx1, sill + 1, ctop, night)
    counter(p, cx0, cx1, f, ctop, night)
    jar(p, cx0 + 3, ctop - 1, night)
    mug(p, cx1 - 9, ctop - 1, night)
    steam(p, cx1 - 8, cx1 - 5, ctop - 7, night, motion, seed=5)
    steam(p, x0 + 3, x0 + 25, ctop - 5, night, motion, seed=3, tall=True)
    if top <= ctop - 32:
        hood(p, x0 + 1, ctop - 16, 26, night, motion, up_to=top)
    if night:
        wx, wy = o["window"]
        lit_on(p, near(p, x0 + 26, ctop + 3, x0 + 40, f + 1, set(OAK)), FLAME[4], (0.12,), wx, wy, 26, 14)
        pool(p, wx, x0 - 1, cx1 + 3, g, 30, (0.12, 0.24, 0.38))
        for n in range(2):                                   # the window's light again in the gloss, shimmering
            L = p.seq(f"gl{n}", n / 2, (n + 1) / 2, 1.2, keep=n == 0, z=0.5) if motion else ("base" if not n else None)
            if L is None:
                continue
            for xx in range(round(wx) - 6, round(wx) + 6):
                if (xx + n) % 2 == 0:
                    p.apx(xx, g - 3 + (xx % 3 == 0), FLAME[5], 0.6, L)
                    p.apx(xx, g - 1 + (xx % 3 == 1), FLAME[4], 0.35, L)
    return (x0 - 2, cx1 + 3)


# --------------------------------------------------------------------------- the room beyond
SUNFLOWER = [
    "..pPp..",
    ".pPPPp.",
    "pPcCcPp",
    "PPcccPp",
    "pPcccpp",
    ".ppppp.",
    "..ppp..",
]
SMALL_FLOWER = [".pPp.", "pPCcp", "Pcccp", ".ppp."]


def sunflower(p: Pix, x, y, night, small=False, L="base"):
    """A sunflower's head with its top-left at (x, y): golden petals lit at their upper left round a brown heart."""
    k = -2 if night else 0
    pal = {"p": _t(SUN, 3 + k), "P": _t(SUN, 5 + k), "c": _t(CHOC, 3), "C": _t(CHOC, 5 + k)}
    p.sprite(x, y, SMALL_FLOWER if small else SUNFLOWER, pal, L=L, reuse=True)


def table(p: Pix, x, top, floor, night: bool, L="base"):
    """A little round table of oak against the far wall, its top at row `top` from column x, twelve wide, on a
    turned pedestal that stands on a foot on the floor at row `floor`."""
    o = _shade(OAK, -2 if night else 0)
    p.hline(x, x + 12, top, o(6), L)
    p.hline(x, x + 12, top + 1, o(4), L)
    p.hline(x + 1, x + 11, top + 2, OAK[0], L)
    for yy in range(top + 3, floor - 1):
        p.hline(x + 5, x + 7, yy, o(3), L)
        p.px(x + 5, yy, o(5), L)
    p.hline(x + 4, x + 8, (top + floor) // 2, o(5), L)
    p.hline(x + 2, x + 10, floor - 1, o(4), L)
    p.hline(x + 2, x + 10, floor, OAK[0], L)


def bouquet(p: Pix, x, top, night: bool, tall: bool = True, L="base"):
    """A blue jug standing at row `top`, its middle at column x, with sunflowers standing up out of it on their
    stalks among their leaves: four of them, or two where the room is short."""
    k = -2 if night else 0
    jug = [".bBBb.", "bBBBbb", "bBbbbd", "bBbbbd", ".bbbd.", ".dddd."]
    p.sprite(x - 3, top - len(jug), jug, {"b": _t(BLUE, 4 + k), "B": _t(BLUE, 6 + k), "d": _t(BLUE, 2 + k)}, L=L)
    jt = top - len(jug)
    stalks = [(-5, -13), (0, -19), (4, -11), (-1, -8)] if tall else [(-3, -8), (3, -10)]
    for sx, sy in stalks:
        steps = abs(sy) - 2
        for j in range(steps):
            p.px(x + round(sx * (j + 1) / steps * 0.9), jt - j, _t(LEAF, 3 + k), L)
    for lx, ly, d in (((-4, -6, -1), (3, -5, 1), (1, -12, 1)) if tall else ((-3, -4, -1), (2, -4, 1))):
        for i in range(3):
            p.px(x + lx + i * d, jt + ly - (i == 1), _t(LEAF, 5 + k) if i == 0 else _t(LEAF, 4 + k), L)
    for sx, sy in stalks:
        small = sy > -10
        sunflower(p, x + sx - (2 if small else 3), jt + sy - (2 if small else 3), night, small, L)


# The child sitting cross-legged on a cushion, facing left, holding a spoon up before his eyes: his shaven head (F
# its outline, H lit, h skin, f shade, b the stubble on its crown), his eye (e), his ear (E) and his mouth (m), his
# bare forearm and his hand (a, A lit), his saffron robe (R lit, r, q shade, Q its darkest) wrapped over his crossed
# legs, his bare foot (a), the cushion (K lit, k, j shade).
CHILD = [
    "......FFFF............",
    "....FHHHHbbF..........",
    "...FHHhhhhbbF.........",
    "...Hehhhhhhbbf........",
    "..hhhhhhhEhbbf........",
    "...fmhhhhhhbf.........",
    "....ffhhhhhf..........",
    "......ffhRRRq.........",
    "....RRRRRRRRrrq.......",
    ".AA.RRRRRRRrrrrq......",
    ".aaRRRRRRRRrrrrqQ.....",
    "..aaRRRRRRrrrrrqQ.....",
    "...aaRRRRrrrrrrrqQ....",
    "....aaRRRrrrrrrrqQ....",
    "....RRRRrrrrrrrrrqQ...",
    "...RRRRRrrrrqrrrrrqQ..",
    "..RRRRRrrrrqrrrrrrrqQ.",
    ".RRRRRrrrrqrrrrrrrrrqQ",
    "RRRRrrrrrqrrrrrrrrrrrq",
    "RRrrrrrrrrrrrrrrrrrrrq",
    "aafQQQQQQQQQQQQQQQQQQ.",
    ".KKKKKKKKKKKKKKKKKKKK.",
    "KKkkkkkkkkkkkkkkkkkkkk",
    "kkkkkkkkkkkkkkkkkkkkkk",
    ".jjjjjjjjjjjjjjjjjjjj.",
]
HAND = (1, 9)     # the top of his fist in the drawing, where the spoon rises from
# The spoon in each frame of its bend, relative to the top of his fist: (dx, dy, part), h the handle, b the bowl, B
# its gleam. Straight, leaning, bending over, bent down.
SPOON = [
    [(0, -1, "h"), (0, -2, "h"), (0, -3, "h"), (0, -4, "h"), (0, -5, "h"), (-1, -6, "b"), (0, -6, "b"),
     (1, -6, "b"), (-1, -7, "b"), (0, -7, "B"), (1, -7, "b"), (0, -8, "b")],
    [(0, -1, "h"), (0, -2, "h"), (0, -3, "h"), (-1, -4, "h"), (-1, -5, "h"), (-3, -6, "b"), (-2, -6, "b"),
     (-1, -6, "b"), (-3, -7, "b"), (-2, -7, "B"), (-1, -7, "b"), (-2, -8, "b")],
    [(0, -1, "h"), (0, -2, "h"), (0, -3, "h"), (-1, -4, "h"), (-2, -5, "h"), (-3, -6, "b"), (-4, -6, "b"),
     (-3, -5, "b"), (-4, -5, "B"), (-5, -5, "b"), (-4, -4, "b"), (-5, -4, "b")],
    [(0, -1, "h"), (0, -2, "h"), (0, -3, "h"), (-1, -4, "h"), (-2, -4, "h"), (-3, -4, "b"), (-2, -3, "b"),
     (-3, -3, "B"), (-4, -3, "b"), (-2, -2, "b"), (-3, -2, "b"), (-4, -2, "b"), (-3, -1, "b")],
]
BEND = ((0.0, 0.42), (0.42, 0.56), (0.56, 0.7), (0.7, 1.0))     # when each frame of the bend shows, of its loop
BEND_LOOP = 6.0


def child(p: Pix, x, g, night: bool, motion: bool, floor=()):
    """The child sitting cross-legged on his cushion on the floor at row g, from column x, facing left, holding a
    spoon up before his eyes and bending it without touching it: straight, then leaning, then bent over, then bent
    down, in four frames on a six-second loop; the still file keeps it bent over. By day the spoon is steel; by
    night it shines in phosphor, the brightest thing in the room: it lights his face, his hand and his robe, and
    its light pools on his cushion and on the `floor` colours round him."""
    top = g - len(CHILD) + 1
    k = -1 if night else 0
    pal = {"F": SKIN[1], "H": SKIN[4], "h": SKIN[3], "f": SKIN[2], "e": CAT[0], "a": SKIN[3], "A": SKIN[4],
           "b": SKIN[2], "E": SKIN[2], "m": SKIN[1],
           "R": _t(ROBE, 5 + k), "r": _t(ROBE, 4 + k), "q": _t(ROBE, 2 + k), "Q": _t(ROBE, 1 + k),
           "k": _t(BLUE, 3 + k), "K": _t(BLUE, 5 + k), "j": _t(BLUE, 1 + k)}
    p.sprite(x, top, CHILD, pal)
    hx, hy = x + HAND[0], top + HAND[1]
    tones = {"h": FLAME[3], "b": FLAME[5], "B": FLAME[6]} if night else \
        {"h": STEEL[2], "b": STEEL[4], "B": C["white"]}
    for f, frame in enumerate(SPOON):
        if motion:
            L = p.seq(f"sp{f}", *BEND[f], BEND_LOOP, keep=f == 2, z=2)
        elif f != 2:
            continue
        else:
            L = "base"
        for dx, dy, part in frame:
            p.px(hx + dx, hy + dy, tones[part], L)
    if night:
        cx, cy = hx - 2, hy - 5
        p.halo(cx + 4, cy, min(13, cx + 4 - x + 6), 11, FLAME[3], (0.05, 0.1, 0.16), L="haze")
        lit_on(p, near(p, x, top, x + 22, g + 1, {pal[c] for c in "FHhfabEmARrq"}), FLAME[4], (0.12, 0.24, 0.36),
               cx, cy, 16, 15)
        p.halo(cx + 6, g - 2, 20, 4, FLAME[4], (0.08, 0.16, 0.26), L="base",
               only={pal["K"], pal["k"], pal["j"]} | set(floor))


BLOCK = [
    "..TTTTTTT",
    ".TTTTTTTs",
    "FFFFFFFss",
    "FmmmmmFss",
    "FmFFFmFss",
    "FmFFFmFss",
    "FmmmmmFs.",
    "FFFFFFF..",
]


def blocks(p: Pix, x0, y0, night: bool, motion: bool):
    """Three wooden toy blocks the child keeps in the air without touching them, red, blue and yellow, each with a
    cream border round its face, each rising and settling a unit on a slow loop of its own; by night with a faint
    phosphor glow under each."""
    k = -2 if night else 0
    for i, (dx, dy, R, dur) in enumerate(((0, 10, RED, 3.2), (12, 0, BLUE, 4.0), (22, 13, SUN, 4.8))):
        key = ("block", i, night)
        if key not in p.syms:
            pal = {"T": _t(R, 6 + k), "F": _t(R, 4 + k), "s": _t(R, 2 + k), "m": _t(GLAZE, 6 + k)}
            p.symbol(key, {(c, r): pal[ch] for r, row in enumerate(BLOCK) for c, ch in enumerate(row) if ch in pal})
        bx, by = x0 + dx, y0 + dy
        place = f'<use href="#{p.syms[key]}" x="{bx}" y="{by}"/>'
        bob = (f'<g>{place}<animateTransform attributeName="transform" type="translate" values="0 0;0 -1" '
               f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
        p.raw(1, bob if motion else place, place)
        if night:
            p.halo(bx + 4, by + 9.5, 6, 2, FLAME[3], (0.1, 0.2), L="haze")


# The black cat walking left in its two strides, its body drawn once and its legs in turn: its fur (k, K lit along
# its back and its ears), its outline (o) and its eye (e).
CAT_BODY = [
    "..o..o.............",
    ".oKooKo.........o..",
    ".okkkko........oKo.",
    "okkkkkko.......oko.",
    "oekkkkko......oKo..",
    "okkkkkkko.....oko..",
    ".okkkkkkoooooooKo..",
    "..okkkkkKKKKKKKko..",
    "..okkkkkkkkkkkkkko.",
    "..okkkkkkkkkkkkkko.",
    "...okkkkkkkkkkkko..",
]
CAT_LEGS = (["...okk.okk...okk.ok", "...oo..oo....oo..oo"], ["....okkok....okkok.", "....oo.oo....oo.oo."])
WALK = 10.0       # the loop the cat walks past in, twice: once, and then once more exactly as before


def cat_symbols(p: Pix, night: bool, ghost: bool = False) -> list:
    """The cat drawn once a file as three symbols, its body and its legs in each stride: in its black fur lit along
    its back, its eye a glint (of phosphor by night); or as its double, the glitch, in phosphor itself, two of its
    rows torn a unit aside."""
    ids = []
    for name, art in (("body", CAT_BODY), ("a", CAT_LEGS[0]), ("b", CAT_LEGS[1])):
        key = ("cat", name, ghost, night)
        if key not in p.syms:
            cells = {}
            oy = 0 if name == "body" else len(CAT_BODY)
            for j, row in enumerate(art):
                shift = 1 if (ghost and oy + j in (4, 5, 8)) else 0
                for i, ch in enumerate(row):
                    if ch == ".":
                        continue
                    if ghost:
                        c = FLAME[3]
                    else:
                        c = {"o": CAT[0], "k": CAT[1] if night else CAT[2], "K": CAT[4] if night else CAT[5],
                             "e": FLAME[5] if night else SUN[5]}[ch]
                    cells[(i + shift, oy + j)] = c
            p.symbol(key, cells, mono=ghost)
        ids.append(p.syms[key])
    return ids


def cat_walk(p: Pix, x0, x1, g, night: bool, motion: bool):
    """The black cat walking left along the far room's floor at row g, across the doorway from x1 to x0, in from
    behind one side of its casing and out behind the other, a unit every tenth of a second, its strides changing as
    it goes; and a moment after, its double walking exactly the same way, faint and torn by a glitch: deja vu. The
    still file holds the cat partway across with its double close behind it."""
    h = len(CAT_BODY) + len(CAT_LEGS[0])
    y = g - h + 1
    wd = len(CAT_BODY[0])
    body, a, b = cat_symbols(p, night)
    gbody, ga, gb = cat_symbols(p, night, ghost=True)
    cid = "catclip"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y - 1}" width="{x1 - x0}" height="{h + 2}"/>'
                  f'</clipPath>')
    mid = x1 - wd - 1
    still = (f'<g clip-path="url(#{cid})"><g transform="translate(0 {y})"><g stroke="{FLAME[3]}" opacity=".45">'
             f'<use href="#{gbody}" x="{mid + 5}" y="-1"/><use href="#{gb}" x="{mid + 5}" y="-1"/></g><use '
             f'href="#{body}" x="{mid}"/><use href="#{a}" x="{mid}"/></g></g>')
    if not motion:
        p.raw(-0.5, still, still)
        return
    steps = x1 - x0 + wd
    n = round(WALK / 0.1)

    def walker(sids, start, attrs=""):
        vals = ";".join(str(x1 - (i - start) if 0 <= i - start <= steps else x1 + 2) for i in range(n))
        legs = []
        for j, sid in enumerate(sids[1:]):
            hidden = ' opacity="0"' if j else ""
            flip = "0;1" if j else "1;0"
            legs.append(f'<use href="#{sid}"{hidden}><animate attributeName="opacity" values="{flip}" dur=".4s" '
                        f'repeatCount="indefinite" calcMode="discrete"/></use>')
        return (f'<g{attrs}><use href="#{sids[0]}"/>{"".join(legs)}<animateTransform attributeName="transform" '
                f'type="translate" values="{vals}" dur="{num(WALK)}s" repeatCount="indefinite" '
                f'calcMode="discrete"/></g>')

    faint = ' opacity=".5" stroke="' + FLAME[3] + '"'
    p.raw(-0.5, f'<g clip-path="url(#{cid})"><g transform="translate(0 {y})">{walker((body, a, b), 0)}'
                f'{walker((gbody, ga, gb), steps + 4, faint)}</g></g>', still)


def doorway(p: Pix, x0, x1, top, g, night: bool) -> tuple:
    """The doorway into the room beyond, from column x0 to x1 and row `top` down to the floor at row g: an oak
    casing lit on its faces toward the light, and through it the far room, its wall papered in sage, darker by
    night, over its skirting and the boards of its floor. Returns the opening (x0, x1) the casing leaves, the row
    the far floor starts at, and the far floor's colours."""
    k = -2 if night else 0
    o = _shade(OAK, k)
    ox0, ox1 = x0 + 4, x1 - 4
    far = p.layer("pane", z=-0.8)
    ft = g - 5
    wall, stripe = (UMBER[3], UMBER[2]) if night else (X["far_day"], X["far_stripe"])
    boards = (UMBER[2], UMBER[1], UMBER[0]) if night else (OAK[5], OAK[4], OAK[3])
    p.defs.append(f'<pattern id="far" x="{ox0 + 2}" width="5" height="4" patternUnits="userSpaceOnUse">'
                  f'<rect width="5" height="4" fill="{wall}"/><rect width="1" height="4" fill="{stripe}"/>'
                  f'<rect x="3" y="1" width="1" height="1" fill="{stripe}"/></pattern>')
    p.shapes[far].append(f'<rect x="{ox0}" y="{top + 4}" width="{ox1 - ox0}" height="{ft - top - 6}" '
                         f'fill="url(#far)"/>')
    p.hline(ox0, ox1, ft - 2, _t(GLAZE, 5 + k - (1 if night else 0)), far)      # the skirting
    p.hline(ox0, ox1, ft - 1, _t(GLAZE, 2 + k), far)
    for j in range(ft, g + 1):                                                   # the boards, lit toward the door
        p.hline(ox0, ox1, j, boards[0] if j == ft else boards[1], far)
    for j, xx in ((ft + 1, ox0 + 7), (ft + 2, ox0 + 19), (ft + 3, ox0 + 2), (ft + 3, ox0 + 30), (ft + 4, ox0 + 13),
                  (ft + 5, ox0 + 25), (ft + 1, ox0 + 33)):
        if xx < ox1:
            p.px(xx, j, boards[2], far)
    for xx in (x0, x1 - 4):                                   # the casing's two legs
        p.vline(xx, top, g + 1, OAK[0])
        p.vline(xx + 1, top + 1, g + 1, o(5))
        p.vline(xx + 2, top + 1, g + 1, o(4))
        p.vline(xx + 3, top + 3, g + 1, o(2) if xx == x0 else o(1))
    p.hline(x0, x1, top, OAK[0])                              # and its head
    p.hline(x0 + 1, x1 - 1, top + 1, o(6))
    p.hline(x0 + 1, x1 - 1, top + 2, o(4))
    p.hline(ox0, ox1, top + 3, o(1))
    return ox0, ox1, ft, set(boards[:2])


def clock(p: Pix, cx, cy, night: bool, L="base"):
    """The clock on the far room's wall, centred on (cx, cy): a red rim lit at its upper left round a cream face
    with its quarters marked and its hands at ten to two; by night in the dark."""
    k = -4 if night else 0
    r = 5
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = math.hypot(x + 0.5 - cx - 0.5, y + 0.5 - cy - 0.5)
            if d <= r - 1.4:
                p.px(x, y, _t(GLAZE, 6 + k), L)
            elif d <= r - 0.3:
                lit = (x - cx) + (y - cy) < 0
                p.px(x, y, _t(RED, (5 if lit else 3) + k), L)
            elif d <= r + 0.6:
                p.px(x, y, RED[0], L)
    for dx, dy in ((0, -3), (3, 0), (0, 3), (-3, 0)):
        p.px(cx + dx, cy + dy, _t(STEEL, 2 + k), L)
    for dx, dy in ((0, -1), (0, -2), (1, 0), (2, -1)):
        p.px(cx + dx, cy + dy, CAT[1], L)
    p.px(cx, cy, RED[2], L)


def room(p: Pix, x0, x1, g, night: bool, motion: bool, top: int) -> tuple:
    """The room beyond the kitchen, on the rule at row g from x0 to x1: a tall doorway, and through it the child
    on his cushion at its threshold bending his spoon, his toy blocks in the air over him, the black cat walking
    past behind him on the far room's floor, twice, a jug of sunflowers on a little table against the far wall and
    the clock over it. Each is built to the rows from `top` down. Returns the span it covers on the rule."""
    dtop = top + 1
    ox0, ox1, ft, boards = doorway(p, x0, x1, dtop, g, night)
    far = "pane"
    if dtop <= g - 52:
        tx = ox1 - 13
        tt = ft - 15
        table(p, tx, tt, ft + 1, night, far)
        bouquet(p, tx + 6, tt, night, tall=dtop <= g - 62, L=far)
        if dtop <= g - 74:
            clock(p, tx + 6, dtop + 12, night, far)
    if dtop <= g - 60:
        blocks(p, ox0 + 2, dtop + 12, night, motion)
    cat_walk(p, ox0, ox1, ft + 3, night, motion)
    child(p, ox0, g, night, motion, floor=boards)
    return (x0 - 1, x1)


# --------------------------------------------------------------------------- the footers, the links and the badges
def heart(p: Pix, x, y, L="base"):
    """A sugar cookie in the shape of a heart, 7 by 6: its golden edge round red icing, the icing lit on its
    upper-left lobe."""
    art = [".dd.dd.", "d65d53d", "d55432d", ".d432d.", "..d3d..", "...d..."]
    pal = {str(i): RED[i] for i in range(7)}
    pal["d"] = DOUGH[3]
    p.sprite(x, y, art, pal, 1, L)


def gingham_bar(p: Pix, x0, y0, w, h, period=5, L="base"):
    """A strip of the curtains' gingham, red and cream: a cream ground crossed by red stripes `period` wide one way
    and two rows deep the other, deepest where they cross."""
    for yy in range(y0, y0 + h):
        across = ((yy - y0) // 2) % 2 == 0
        for xx in range(x0, x0 + w):
            down = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, RED[2] if (down and across) else RED[4] if (down or across) else GLAZE[6], L)


# The links' icons, nine by seven, each from the kitchen or the room beyond: the spoon (s steel, S lit), the black
# cat (o, e its eye), the red mug (r, R lit) with its steam (w), and a toy block (T its top, F its face, s its side,
# m the cream round its face).
ICONS = {
    "spoon": ["....sSs..", "...sSSSs.", "....sss..", "....s....", "...s.....", "..s......", ".s......."],
    "cat": [".o.o.....", ".ooo.....", ".eoo...o.", ".ooo...o.", "..oooo.o.", "..ooooo..", "..oo.oo.."],
    "mug": ["..w..w...", "...w..w..", ".rrrrrr..", ".rRrrrrrr", ".rRrrrr.r", ".rRrrrrrr", "..rrrrr.."],
    "block": ["..TTTTTT.", ".TTTTTTTb", "FFFFFFFbb", "FmmmmmFbb", "FmFFFmFbb", "FmmmmmFb.", "FFFFFFF.."],
}
LINK_ICONS = ("spoon", "cat", "mug", "block")


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a link's golden dough, by day or by night."""
    k = -1 if night else 0
    return {"s": STEEL[1], "S": _t(STEEL, 4 + k), "o": CAT[0], "e": FLAME[4] if night else SUN[6],
            "r": _t(RED, 3 + k), "R": _t(RED, 5 + k), "w": GLAZE[6], "T": _t(BLUE, 5 + k), "F": _t(BLUE, 3 + k),
            "b": BLUE[1], "m": GLAZE[6], "#": ink}


# --------------------------------------------------------------------------- the dresser: a section's hero
# A plate standing on a shelf, seven wide, leaning against the dresser's back: its rim in the tiles' blue (r, R lit),
# its face cream (c, C lit) round its well (w).
PLATE = ["..rRr..", ".rCCcr.", "rCcccwr", "RcwwwcR", "rcwwwcr", ".rccwr.", "..rrr.."]
CUP = [".hh..", "cCCcd", "cCcccd", "cccc.", ".cc.."]
# The vase in the falling of it: standing at the counter's edge, tipping over it, falling, and broken on the floor.
VASE = [
    ["..bBBb..", "...bd...", "...bd...", "..bBbd..", ".bBbbbd.", "bBbbwbbd", "bBwbbbbd", "bBbbwbbd",
     "bBwbbbbd", ".bBbbbd.", "..bbbd..", "..dddd.."],
    ["......bB", ".....bdb", "....bdb.", "...bBbd.", "..bBbbbd", ".bBbwbbd", "bBwbbbd.", "bBbwbbd.",
     "bwbbbd..", ".bbbd...", ".bdd....", "........"],
    ["........", "..dddd..", ".bbbbd..", "bBbbwbd.", "bBwbbbbd", "bBbbwbbd", "bBwbbbbd", ".bBbbbd.",
     "..bBbd..", "...bd...", "..bBBb..", "........"],
]
SHARDS = ["........b...", ".b..bd......", "..bBdd..b.bd", "bBbdwbdd.bdb"]
FALL = ((0.0, 0.62), (0.62, 0.67), (0.67, 0.72), (0.72, 1.0))     # when each moment of the fall shows
FALL_LOOP = 8.0
SLEEPER = ["o.o.........", "oKo.ooooo...", "okkoKKKKKoo.", "okkkkkkkkkko", ".okkkkkkkkko", "..ooooooooo."]


def plates(p: Pix, x0, x1, y, night: bool, seed: int, L="base"):
    """Plates standing on a shelf from x0 to x1 with their feet on row y, leaning against the dresser's back, each
    drawn once and placed, and between them now and then a cup."""
    k = -2 if night else 0
    pal = {"r": _t(BLUE, 3 + k), "R": _t(BLUE, 5 + k), "c": _t(GLAZE, 5 + k), "C": _t(GLAZE, 6 + k),
           "w": _t(GLAZE, 3 + k)}
    cpal = {"h": _t(RED, 2 + k), "c": _t(RED, 4 + k), "C": _t(RED, 5 + k), "d": _t(RED, 2 + k)}
    rnd = random.Random(seed)
    x = x0
    while x + 7 <= x1:
        if rnd.random() < 0.28 and x + 5 <= x1:
            p.sprite(x, y - len(CUP) + 1, CUP, cpal, L=L, reuse=True)
            x += 6
        else:
            p.sprite(x, y - len(PLATE) + 1, PLATE, pal, L=L, reuse=True)
            x += 6


def radio(p: Pix, x, y, night: bool, motion: bool) -> tuple:
    """A kitchen radio of 1999 standing on the counter at row y from column x, fourteen wide: a red case lit at its
    upper left with a handle over it, its speaker's grille and its dial, whose window glows phosphor by night, a
    knob either side. Returns the middle of its dial."""
    k = -1 if night else 0
    top = y - 8
    p.hline(x + 3, x + 11, top - 2, _t(STEEL, 4 + k))
    p.px(x + 3, top - 1, _t(STEEL, 3 + k))
    p.px(x + 10, top - 1, _t(STEEL, 2 + k))
    slab(p, x + 1, top, 12, 8, RED, k)
    for gx in range(x + 3, x + 7):
        for gy in range(top + 2, top + 6):
            if (gx + gy) % 2:
                p.px(gx, gy, _t(RED, 1 + k))
    lamp = p.flicker(0) if (night and motion) else "base"
    p.rect(x + 8, top + 2, 4, 3, FLAME[3] if night else GLAZE[5])
    p.px(x + 9, top + 3, FLAME[5] if night else RED[1], lamp if night else "base")
    p.px(x + 8, top + 6, _t(STEEL, 5 + k))
    p.px(x + 11, top + 6, _t(STEEL, 5 + k))
    return (x + 10, top + 3)


def chair(p: Pix, x, g, night: bool):
    """A ladder-back kitchen chair of oak standing on the floor at row g from column x, fourteen wide: its back
    posts rising over its seat with three slats between them, its rush seat and its legs."""
    o = _shade(OAK, -2 if night else 0)
    seat = g - 13
    for px_, lit in ((x, True), (x + 12, False)):
        for yy in range(g - 31, g + 1):
            p.px(px_, yy, o(5) if lit else o(2))
            p.px(px_ + 1, yy, o(3) if lit else o(1))
        p.px(px_, g - 32, o(6))
    for j in range(3):
        sy = g - 29 + j * 5
        p.hline(x + 2, x + 12, sy, o(5))
        p.hline(x + 2, x + 12, sy + 1, o(2))
    p.hline(x - 1, x + 15, seat, o(6))
    for yy in range(seat + 1, seat + 3):
        for xx in range(x - 1, x + 15):
            p.px(xx, yy, _t(SUN, (3 if (xx + yy) % 3 else 2) + (-2 if night else 0)))
    p.hline(x - 1, x + 15, seat + 3, OAK[0])
    p.hline(x + 2, x + 12, g - 5, o(3))


def dresser(p: Pix, x0, x1, g, night: bool, motion: bool, top: int) -> tuple:
    """The kitchen's oak dresser standing on the floor at row g from column x0 to x1, its crown no higher than row
    `top`: a base of two panelled doors under a drawer and a cream counter, and over the counter its rack of open
    shelves, plates standing on each and cups between them, under a moulded crown. On the counter stands the
    radio. By night the radio's dial glows and lays its light on the counter and the plates. Returns the row of its
    crown."""
    o = _shade(OAK, -2 if night else 0)
    ctop = g - 27
    p.hline(x0 - 2, x1 + 2, ctop, _t(GLAZE, 6 + (-3 if night else 0)))       # the counter
    p.hline(x0 - 2, x1 + 2, ctop + 1, _t(GLAZE, 3 + (-3 if night else 0)))
    p.hline(x0 - 2, x1 + 2, ctop + 2, OAK[0])
    slab(p, x0 + 1, ctop + 4, x1 - x0 - 2, g - ctop - 5, OAK, -2 if night else 0, face=4, outline=False)
    p.box(x0, ctop + 3, x1 - x0, g - ctop - 2, OAK[0])
    mid = (x0 + x1) // 2
    p.hline(x0 + 1, x1 - 1, ctop + 8, OAK[1])                                # the drawer
    p.px(mid, ctop + 6, SUN[5] if not night else SUN[2])
    p.vline(mid, ctop + 9, g - 1, OAK[1])
    for a, b in ((x0 + 3, mid - 2), (mid + 3, x1 - 3)):                         # the doors' panels
        p.box(a, ctop + 11, b - a, g - ctop - 15, o(2))
        p.hline(a + 1, b - 1, ctop + 12, o(5))
        p.vline(a + 1, ctop + 13, g - 5, o(5))
    for kx in (mid - 3, mid + 2):
        p.px(kx, ctop + 17, SUN[5] if not night else SUN[2])
    p.hline(x0 + 1, x1 - 1, g, OAK[0])
    rack0, rack1 = x0 + 3, x1 - 3                                           # the rack of shelves
    shelves = max(1, min(4, (ctop - 8 - top - 6) // 15))
    crown = ctop - 8 - shelves * 15 - 4
    p.hline(rack0 - 3, rack1 + 3, crown, OAK[0])
    p.hline(rack0 - 2, rack1 + 2, crown + 1, o(6))
    p.hline(rack0 - 2, rack1 + 2, crown + 2, o(4))
    p.hline(rack0 - 1, rack1 + 1, crown + 3, o(2))
    back = p.layer("pane", z=-0.8)
    for yy in range(crown + 4, ctop - 7):
        for xx in range(rack0 + 2, rack1 - 2):
            p.px(xx, yy, o(1) if (xx - rack0) % 7 == 0 else o(2), back)
    for xx, lit in ((rack0, True), (rack1 - 2, False)):
        for yy in range(crown + 4, ctop - 6):
            p.px(xx, yy, o(5) if lit else o(3))
            p.px(xx + 1, yy, o(4) if lit else o(2))
    p.vline(rack0 - 1, crown + 4, ctop - 6, OAK[0])
    p.vline(rack1, crown + 4, ctop - 6, OAK[0])
    for i in range(shelves):
        sy = crown + 4 + (i + 1) * 15
        plates(p, rack0 + 3, rack1 - 3, sy - 1, night, seed=i * 5 + 1)
        p.hline(rack0 - 1, rack1 + 1, sy, o(6))
        p.hline(rack0, rack1, sy + 1, o(3))
        p.hline(rack0 + 2, rack1 - 2, sy + 2, o(1), back)
    for yy in range(ctop - 7, ctop):                                         # the wall over the counter
        for xx in range(rack0, rack1):
            if yy == ctop - 7:
                p.px(xx, yy, OAK[0])
    dial = radio(p, rack1 - 16, ctop - 1, night, motion)
    if night:
        cx, cy = dial
        p.halo(cx, cy, 16, 9, FLAME[3], (0.05, 0.1, 0.16), L="haze")
        lit_on(p, near(p, x0 - 2, cy - 12, x1 + 2, ctop + 3, {_t(GLAZE, 6 - 3), _t(GLAZE, 3 - 3), _t(BLUE, 1),
                                                             _t(BLUE, 3), _t(GLAZE, 3), _t(GLAZE, 4)}),
               FLAME[4], (0.12, 0.24), cx, cy, 22, 12)
    return crown


def sleeper(p: Pix, x, y, night: bool):
    """The black cat asleep, curled up with its top-left at (x, y), lit along its back."""
    pal = {"o": CAT[0], "k": CAT[1] if night else CAT[2], "K": CAT[4] if night else CAT[5]}
    p.sprite(x, y, SLEEPER, pal)


def pendant(p: Pix, x, y0, y1, night: bool, motion: bool, reach: int, x_min: int):
    """A pendant lamp hanging from the rail at row y0 on its cord over column x, its shade's foot at row y1: an
    enamel shade, cream outside and lit at its upper left, its rim dark. By night its bulb burns phosphor under the
    shade and throws a cone of light down toward row `reach`, kept right of column `x_min`."""
    k = -2 if night else 0
    for yy in range(y0, y1 - 5):
        p.px(x, yy, _t(STEEL, 2 + k))
    p.hline(x - 1, x + 2, y1 - 6, _t(STEEL, 4 + k))
    for j, half in enumerate((2, 3, 4, 5, 6)):
        yy = y1 - 5 + j
        for xx in range(x - half, x + half + 1):
            t = (xx - x + half) / (2 * half)
            p.px(xx, yy, _t(GLAZE, (6 if t < 0.25 else 5 if t < 0.6 else 3) + k))
    p.hline(x - 6, x + 7, y1, _t(GLAZE, 1 + k))
    if night:
        lamp = p.flicker(2) if motion else "base"
        p.hline(x - 2, x + 3, y1 + 1, FLAME[5], lamp)
        p.px(x, y1 + 2, FLAME[6], lamp)
        cone = p.layer("cone", z=-0.7)
        n = reach - y1
        for j in range(2, n):
            half = 5 + j // 4
            a = 0.16 if j < n // 2 else 0.1
            p.hline(max(x_min, x - half), x + half + 1, y1 + j, FLAME[4] + f":{a:g}", cone)
        p.halo(x + 0.5, y1 + 1, 9, 4, FLAME[4], (0.12, 0.24), L="haze")


def kitchen_table(p: Pix, x0, x1, g, night: bool, motion: bool) -> int:
    """The kitchen table standing on the floor at row g from column x0 to x1: its top under a gingham cloth that
    hangs over its edges, its turned legs, a plate of cookies on it and, at its right end, the blue vase, which in a
    moving header tips over the edge, falls and breaks on the floor, and then stands on the table again exactly as
    it did before. Returns the row of its top."""
    o = _shade(OAK, -2 if night else 0)
    top = g - 15
    for lx in (x0 + 2, x1 - 4):
        for yy in range(top + 4, g + 1):
            p.px(lx, yy, o(5))
            p.px(lx + 1, yy, o(2))
        p.hline(lx - 1, lx + 3, top + 9, o(4))
    p.hline(x0 + 4, x1 - 4, top + 5, o(2))
    cloth = p.layer("cloth", z=0.2)
    check = gingham(p, night)
    p.shapes[cloth].append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="5" fill="{check}"/>')
    kk = -2 if night else 0
    p.hline(x0, x1, top, _t(RED, 5 + kk), cloth)
    p.hline(x0, x1, top + 5, _t(RED, 2 + kk), cloth)
    for xx in range(x0, x1, 3):
        p.px(xx, top + 6, _t(RED, 3 + kk), cloth)
    k = -1 if night else 0
    plate = {"r": _t(BLUE, 3 + k), "c": _t(GLAZE, 6 + k)}
    p.sprite(x0 + 6, top - 2, [".rrrrrrrr.", "rccccccccr", ".rrrrrrrr."], plate)
    for cx in (x0 + 7, x0 + 11):
        cookie(p, cx - 1, top - 6, night)
    vx = x1 - 6
    pal = {"b": _t(BLUE, 3 + k), "B": _t(BLUE, 5 + k), "d": _t(BLUE, 1 + k), "w": _t(GLAZE, 6 + k)}
    spots = ((vx, top - 12), (vx + 3, top - 11), (vx + 7, top + 6))
    for f in range(4):
        if motion:
            L = p.seq(f"vs{f}", *FALL[f], FALL_LOOP, keep=f == 1, z=1)
        elif f != 1:
            continue
        else:
            L = "base"
        if f == 0:
            p.sprite(*spots[0], VASE[0], pal, L=L)
        elif f < 3:
            p.sprite(*spots[f], VASE[f], pal, L=L, flip=True)
        else:
            p.sprite(x1 + 1, g - len(SHARDS) + 1, SHARDS, pal, L=L, flip=True)
    return top


def dresser_wall(p: Pix, x0, x1, g, night: bool, motion: bool, top: int, ceiling: int = TOP + 1) -> tuple:
    """A section's hero, the kitchen's other wall, standing on its linoleum from x0 to x1 on the floor at row g:
    the kitchen table under its gingham cloth with a plate of cookies and the blue vase on it, a pendant lamp
    hanging over it from the rail (or, on a phone, from row `ceiling` under the words), and the dresser with its
    shelves of plates and its radio, the black cat asleep on its crown. By night the lamp and the radio's dial light
    what stands near them. Returns the span it covers on the rule."""
    floor(p, x0, x1 + 1, g, night)
    f = g - 4
    ttop = kitchen_table(p, x0 + 2, x0 + 34, f, night, motion)
    crown = dresser(p, x0 + 50, min(x1 - 3, x0 + 116), f, night, motion, top)
    sleeper(p, min(x1 - 3, x0 + 116) - 15, crown - 6, night)
    pendant(p, x0 + 18, ceiling, max(top + 8, ceiling + 14), night, motion, ttop - 1, x0)
    return (x0 - 1, x1 + 1)

# --------------------------------------------------------------------------- the fridge: a strip's hero
SITTER = ["o...o..", "oKoKo..", "okkkko.", "oekkko.", "okkkkko", ".okkkko", ".okkkko", "okkkkko", "okKkkko",
          ".oooooo"]


def sitter(p: Pix, x, y, night: bool, L="base"):
    """The black cat sitting up, seen from its side, with its top-left at (x, y), its eye a glint, its tail curled
    round its feet."""
    pal = {"o": CAT[0], "k": CAT[1] if night else CAT[2], "K": CAT[4] if night else CAT[5],
           "e": FLAME[4] if night else SUN[5]}
    p.sprite(x, y, SITTER, pal, L=L)


def fridge(p: Pix, x0, x1, top, g, night: bool, motion: bool) -> tuple:
    """A refrigerator of 1999 standing on the floor at row g from column x0 to x1 with its top at row `top`: almond
    enamel with rounded shoulders, lit down its left and in shade down its right, a freezer door over the larger
    one, chrome handles, and on its doors the magnets of a kitchen, a shopping list and a child's drawing of a spoon
    held under them. By night its door stands ajar and its light, the hand's phosphor, spills out of the gap down
    the floor. Returns its door's gap (x, top, bottom)."""
    k = -2 if night else 0
    e = _shade(ENAMEL, k)
    w = x1 - x0
    bands = []
    for xx in range(x0, x1):
        t = (xx - x0) / max(1, w - 1)
        c = e(6) if t < 0.12 else e(5) if t < 0.45 else e(4) if t < 0.85 else e(2)
        if bands and bands[-1][2] == c:
            bands[-1][1] += 1
        else:
            bands.append([xx, 1, c])
    for bx, bw, c in bands:
        fill(p, bx, top + 2, bw, g - top - 1, c)
        for yy, inset in ((top, 2), (top + 1, 1)):
            for xx in range(max(bx, x0 + inset), min(bx + bw, x1 - inset)):
                p.px(xx, yy, c)
    for yy in range(top + 2, g + 1):
        p.px(x0 - 1, yy, ENAMEL[0])
        p.px(x1, yy, ENAMEL[0])
    p.hline(x0 + 2, x1 - 2, top - 1, ENAMEL[0])
    p.px(x0, top, ENAMEL[0])
    p.px(x1 - 1, top, ENAMEL[0])
    split = top + (g - top) // 3
    p.hline(x0, x1, split, _t(ENAMEL, 1 + k))
    p.hline(x0, x1, split + 1, e(6))
    p.hline(x0 + 1, x1 - 1, g - 3, _t(ENAMEL, 1 + k))                 # the grille at its foot
    for xx in range(x0 + 2, x1 - 2, 2):
        p.px(xx, g - 1, ENAMEL[0])
    hx = x1 - 4
    for (a, b) in ((split - 9, split - 2), (split + 4, split + 18)):
        for yy in range(a, b):
            p.px(hx, yy, _t(STEEL, 5 + k))
            p.px(hx + 1, yy, _t(STEEL, 2 + k))
    mk = -1 if night else 0
    for (mx, my, R) in ((x0 + 4, split + 5, RED), (x0 + 13, split + 9, BLUE), (x0 + 7, top + 5, SUN),
                        (x0 + 16, split + 21, LEAF)):
        p.px(mx, my, _t(R, 5 + mk))
        p.px(mx + 1, my, _t(R, 3 + mk))
        p.px(mx, my + 1, _t(R, 3 + mk))
        p.px(mx + 1, my + 1, _t(R, 2 + mk))
    note = _t(GLAZE, 6 + k)
    p.rect(x0 + 3, split + 7, 8, 10, note)                            # the shopping list
    for j in range(3):
        p.hline(x0 + 4, x0 + 9 - (j % 2) * 2, split + 9 + j * 2, _t(BLUE, 3 + mk))
    p.rect(x0 + 12, split + 11, 9, 9, note)                           # and the child's drawing of a spoon
    for dy, xs in ((1, (17,)), (2, (16, 17)), (3, (16,)), (4, (16,)), (5, (15,)), (6, (15,)), (7, (14,))):
        for xx in xs:
            p.px(x0 + xx, split + 11 + dy, _t(STEEL, 3 + mk))
    p.px(x0 + 17, split + 12, _t(STEEL, 1 + mk))
    gap = (x1 - 1, split + 2, g - 4)
    if night:                                   # its door ajar, its light spilling out
        lamp = p.flicker(1) if motion else "base"
        inx0, inx1, iny0, iny1 = x0 + 2, x1 - 2, split + 3, g - 4
        p.rect(inx0, iny0, inx1 - inx0, iny1 - iny0, FLAME[4])
        p.hline(inx0, inx1, iny0, FLAME[6], lamp)
        p.rect(inx0 + 2, iny0 + 1, 3, 2, FLAME[6], lamp)
        for sy in range(iny0 + 7, iny1, 7):
            p.hline(inx0, inx1, sy, FLAME[2])
            p.hline(inx0, inx1, sy + 1, FLAME[3])
        bottles = ((inx0 + 2, iny0 + 7, 3, 5), (inx0 + 6, iny0 + 7, 2, 4), (inx0 + 11, iny0 + 14, 4, 6),
                   (inx0 + 3, iny0 + 14, 5, 4), (inx0 + 16, iny0 + 7, 3, 6))
        for bx, by, bw, bh in bottles:
            if bx + bw <= inx1 and by + 1 <= iny1:
                p.rect(bx, by - bh, bw, bh, FLAME[1])
                p.px(bx, by - bh, FLAME[2])
        p.hline(inx0, inx1, iny1 - 1, FLAME[2])
        for j, yy in enumerate(range(iny0 - 1, iny1 + 2)):        # the door, swung open toward us
            for i in range(5):
                p.px(x1 + i, yy + (i // 2 if j == 0 else 0), (e(4) if i < 3 else e(2)) if i else ENAMEL[0])
        p.vline(x1 + 5, iny0, iny1 + 2, ENAMEL[0])
        gap = (x1 + 5, iny0, iny1)
    return gap


def fridge_corner(p: Pix, x0, x1, g, night: bool, motion: bool, top: int) -> tuple:
    """A strip's hero, standing on its linoleum from x0 to x1 on the floor at row g and rising to row `top`: the
    refrigerator, the cookie jar on its top, and the black cat sitting on the floor before it, looking up at it. By
    night the fridge's light spills from its door across the floor and lights the cat. Returns the span it covers
    on the rule."""
    floor(p, x0, x1 + 1, g, night)
    f = g - 4
    fw = 32
    fx0 = x1 - fw - 16
    ftop = max(top + 9, f - 70)
    gap = fridge(p, fx0, fx0 + fw, ftop, f, night, motion)
    jar(p, fx0 + 10, ftop - 2, night)
    sitter(p, x1 - 8, f - 9, night)
    if night:
        gx, gy0, gy1 = gap
        pool(p, fx0 + fw // 2 + 3, x0, x1 + 1, g, fw // 2 + 14, (0.16, 0.32, 0.5))
        p.halo(fx0 + fw // 2 + 2, (gy0 + gy1) / 2, fw // 2 + 8, (gy1 - gy0) / 2 + 6, FLAME[3], (0.05, 0.1),
               L="haze")
        lit_on(p, near(p, x1 - 9, f - 9, x1, f + 1, {CAT[1], CAT[0], CAT[4]}), FLAME[4], (0.2, 0.35), gx,
               f - 4, 12, 9)
    return (x0 - 1, x1 + 1)


def fridge_kitchen(p: Pix, x0, x1, g, night: bool, top: int):
    """A phone's strip under its words, from x0 to x1 on the floor at row g: the refrigerator's corner at the right
    (see `fridge_corner`), and at its left a run of counter under the backsplash's tiles, the jug of sunflowers and the
    red mug standing on it, all on the linoleum."""
    f = g - 4
    split = x1 - 72
    fridge_corner(p, split, x1, g, night, False, top)
    floor(p, x0, split, g, night)
    cx0, cx1 = x0 + 4, split - 4
    ctop = max(top + 26, f - 21)
    backsplash(p, cx0, cx1, max(top + 2, ctop - 14), ctop, night, uid="bsp")
    counter(p, cx0, cx1, f, ctop, night)
    bouquet(p, cx0 + 12, ctop, night, tall=ctop - 22 > top)
    mug(p, cx1 - 12, ctop - 1, night)


# --------------------------------------------------------------------------- the footers' footing and emblem
def footing(p: Pix, night: bool, x0: int = EDGE, x1: int | None = None) -> int:
    """The kitchen's linoleum along a footer's foot, inside its trim, three rows of cream and pale blue checks,
    left out wherever a word comes within a unit of it. Returns the row of its top."""
    x1 = p.w - EDGE if x1 is None else x1
    k = -4 if night else 0
    a, b = _t(GLAZE, 5 + k), _t(BLUE, 5 + k)
    g = p.h - EDGE - 1
    for xx in range(x0, x1):
        for yy in (g - 2, g - 1, g):
            if p.clear_of_words(xx - 1, yy - 1, xx + 2, yy + 2):
                p.px(xx, yy, (a if (xx // 3) % 2 else b) if yy == g - 2 else (b if ((xx + 2) // 4) % 2 else a))
    return g - 2


NIGHT_LIGHT = [".ss.", "sLLs", "sLls", ".ll.", "..p."]


def emblem(p: Pix, x0, x1, g, night: bool) -> bool:
    """The kitchen's corner after a title block's last cell, between columns x0 and x1, standing on the footing at
    row g: a cabinet of oak under a cream counter with the cookie jar and the red mug on it, a night light plugged
    into the wall over it, and the black cat sitting on the floor beside it; by night the night light burns the
    hand's phosphor and lays its light on the jar, the mug and the cat. Drawn only where it has room, two units
    clear of every word; where it has not, the cat sits there alone if it can. Returns whether either was drawn."""
    w, top = 34, g - 22
    x = x1 - w - 2
    if x < x0 or top < 5 or not p.clear_of_words(x - 2, top - 2, x1 + 2, g + 1):
        cx = x1 - 8                                     # where the corner has no room, the cat alone
        if cx >= x0 and g - 11 >= 4 and p.clear_of_words(cx - 2, g - 11, x1 + 1, g + 1):
            sitter(p, cx, g - 9, night)
            return True
        return False
    k = -2 if night else 0
    ctop = g - 12
    p.hline(x + 10, x + w, ctop, _t(GLAZE, 6 + k))
    p.hline(x + 10, x + w, ctop + 1, _t(GLAZE, 3 + k))
    p.hline(x + 10, x + w, ctop + 2, OAK[0])
    slab(p, x + 11, ctop + 3, w - 12, g - ctop - 3, OAK, k, face=4, outline=False)
    p.box(x + 13, ctop + 5, w - 16, g - ctop - 7, _t(OAK, 2 + k))
    p.px(x + w - 6, ctop + 8, SUN[5] if not night else SUN[2])
    jar(p, x + 12, ctop - 1, night)
    mug(p, x + w - 9, ctop - 1, night)
    sitter(p, x, g - 9, night)
    pal = {"s": _t(GLAZE, 5 + k), "L": FLAME[5] if night else _t(GLAZE, 6 + k), "l": FLAME[4] if night else
           _t(GLAZE, 4 + k), "p": _t(STEEL, 3 + k)}
    nx, ny = x + 22, top + 1
    if night:
        p.sprite(nx, ny, NIGHT_LIGHT, {c: v for c, v in pal.items() if c in "sp"})
        p.sprite(nx, ny, NIGHT_LIGHT, {c: v for c, v in pal.items() if c in "Ll"}, L=p.flicker(1))
        p.halo(nx + 2, ny + 2, 9, 7, FLAME[3], (0.06, 0.12, 0.2), L="haze")
        lit_on(p, near(p, x, ny, x1, g + 1, {CAT[1], CAT[0], CAT[4], _t(RED, 3), _t(RED, 2), _t(GLAZE, 4),
                                            _t(GLAZE, 3)}), FLAME[4], (0.12, 0.24), nx + 2, ny + 4, 18, 14)
    else:
        p.sprite(nx, ny, NIGHT_LIGHT, pal)
    return True


def cookie_bitten(p: Pix, x, y, night: bool):
    """A cookie with a bite out of it and a crumb or two beside it, eight by six, for the corner of the closing
    notes."""
    k = -1 if night else 0
    art = ["..llll..", ".lLDcDd.", "lDcDDdD.", "DDDdcD..", ".dDDd..c", "..dd.c.."]
    pal = {"l": _t(DOUGH, 6 + k), "L": _t(DOUGH, 5 + k), "D": _t(DOUGH, 4 + k), "c": CHOC[1], "d": _t(DOUGH, 2 + k)}
    p.sprite(x, y, art, pal)


def icing(p: Pix, x0, x1, y, night: bool, seed: int):
    """Chocolate icing along a link's top edge, as on a biscuit: a band two rows deep over the cookie's rim, glossy
    along its top, a drip running down from it at each end, clear of the letters."""
    gloss, choc, deep = CHOC[5], CHOC[3], CHOC[1]
    for xx in range(x0, x1):
        p.px(xx, y, gloss if (xx + seed) % 5 else choc)
        p.px(xx, y + 1, choc)
    for xx, n in ((x0 + 1, 2), (x1 - 2, 3)):
        for j in range(n):
            p.px(xx, y + 2 + j, deep if j == n - 1 else choc)


# --------------------------------------------------------------------------- the marks beside a title, and the rules
SPOON_MARK = ["....ss.", "...sSSs", "...sSss", "..s.ss.", ".s.....", "s......"]


def spoon_mark(p: Pix, x, y, night: bool):
    """The bent spoon beside SECTION A-A, seven by six, its bowl lit at its upper left: steel by day, phosphor by
    night."""
    pal = {"s": FLAME[3], "S": FLAME[5]} if night else {"s": STEEL[2], "S": STEEL[5]}
    p.sprite(x, y, SPOON_MARK, pal)


def block_mark(p: Pix, x, y, night: bool):
    """A red toy block beside a strip's title, nine by eight, centred on row y."""
    k = -2 if night else 0
    pal = {"T": _t(RED, 6 + k), "F": _t(RED, 4 + k), "s": _t(RED, 2 + k), "m": _t(GLAZE, 6 + k)}
    p.sprite(x, y - 4, BLOCK, pal)


def crumbs_on_rule(p: Pix, x0, x1, y, seed: int, night: bool):
    """Cookies lying on a rule here and there with a crumb or two beside them, where no word comes within two units
    of them."""
    rnd = random.Random(seed)
    x = x0 + 14 + rnd.randrange(20)
    k = -1 if night else 0
    crumb = _t(DOUGH, 4 + k)
    while x + 8 < x1:
        if p.clear_of_words(x - 2, y - 7, x + 9, y + 2):
            cookie(p, x, y - 4, night)
            p.px(x + 7, y - 1, crumb)
            if rnd.random() < 0.5:
                p.px(x - 2, y - 1, crumb)
        x += 46 + rnd.randrange(30)


# --------------------------------------------------------------------------- the elements
def recipe_card(p: Pix, x, y, w, h, night: bool, lid: bool):
    """A schematic's card as a recipe card: a red rule along its top inside its edge, a strip of gingham down its
    icon cell's edge, its lower right corner turned down, and, on a card with a lid, a red pin pushed through its
    top."""
    k = -2 if night else 0
    red = _t(RED, 3 + k)
    p.hline(x + 14, x + w - 2, y + 2, red)
    for yy in range(y + 1, y + h - 1):
        p.px(x + 13, yy, _t(RED, 4 + k) if (yy - y) % 4 < 2 else _t(GLAZE, 6 + k))
    p.px(x + w - 2, y + h - 2, _t(OAK, 2 + k))
    p.px(x + w - 3, y + h - 2, _t(GLAZE, 3 + k))
    p.px(x + w - 2, y + h - 3, _t(GLAZE, 3 + k))
    if lid:
        cx = x + w // 2
        p.px(cx, y - 2, _t(RED, 5 + k))
        p.px(cx + 1, y - 2, _t(RED, 3 + k))
        p.px(cx, y - 1, _t(RED, 3 + k))
        p.px(cx + 1, y - 1, _t(RED, 1 + k))
        p.px(cx, y, _t(STEEL, 4 + k))


def twine(p: Pix, cells, night: bool):
    """A wire as baker's twine, red and cream twisted, a cream turn every third unit along it."""
    k = -1 if night else 0
    for i, (x, y, _) in enumerate(cells):
        if i % 3 == 2:
            p.px(x, y, _t(GLAZE, 6 + k))


def cookie_stack(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a stack of cookies, `v` rows tall from the base line, each cookie three rows: its domed
    top lit, its chips showing in its middle, its foot baked dark."""
    k = -1 if night else 0
    top = base - v
    for yy in range(top, base):
        j = (base - 1 - yy) % 3
        for xx in range(bx, bx + bw):
            edge = xx in (bx, bx + bw - 1)
            if j == 2:
                c = _t(DOUGH, 6 + k) if not edge else _t(DOUGH, 5 + k)
            elif j == 1:
                c = CHOC[1] if (xx + yy) % 4 == 0 and not edge else _t(DOUGH, 4 + k)
            else:
                c = _t(DOUGH, 2 + k)
            p.px(xx, yy, c)


def star_sticker(p: Pix, x, y, night: bool):
    """A gold star sticker, five by five, beside the busiest week."""
    k = -1 if night else 0
    art = ["..s..", ".sSs.", "sSSSs", ".sSs.", "s...s"]
    p.sprite(x, y, art, {"s": _t(SUN, 3 + k), "S": _t(SUN, 5 + k)})


def oven_dial(p: Pix, arc, night: bool):
    """The dial's ring as an oven's temperature ring: almond enamel bent round the dial, lit along its upper left,
    a red band over its hottest third."""
    k = -2 if night else 0
    n = max(1, len(arc) - 1)

    def colour(s, o, lam, x, y):
        t = min(1.0, max(0.0, (x - arc[0][0]) / max(1.0, arc[-1][0] - arc[0][0])))
        if t > 0.7:
            return _t(RED, max(1, min(5, round(1.5 + 3.5 * lam)) + k))
        return _t(ENAMEL, max(1, min(6, round(1.8 + 4.2 * lam)) + k))
    tube(p, arc, 2.2, colour, outline=ENAMEL[0])
    del n


def knob_hub(p: Pix, cx, cy, night: bool):
    """The hub the hand turns on, the oven's knob: a steel dome on an almond collar, a red mark on it."""
    sphere(p, cx + 0.5, cy - 0.5, 3.0, STEEL, lo=1, hi=5 if night else 6)
    p.px(cx, cy - 2, RED[4])
    for i, xx in enumerate(range(cx - 4, cx + 5)):
        p.px(xx, cy + 2, _t(ENAMEL, (5 if i < 3 else 4 if i < 7 else 2) + (-2 if night else 0)))


def wrapper(i: int, xx, yy, y0, y1, lift, night: bool) -> str:
    """The colour of the `i`-th file type's wrapper at (xx, yy): cookie dough studded with chips, the curtains'
    gingham, the tiles' cream with their blue flowers, oak along its grain, and the robe's saffron in folds, by
    turns."""
    k = -1 if night else 0
    kind = i % 5
    if kind == 0:
        c = CHOC[2] if (xx * 3 + yy * 5) % 11 == 0 else _t(DOUGH, 4 + k)
    elif kind == 1:
        down, across = (xx // 2) % 2 == 0, (yy // 2) % 2 == 0
        c = _t(RED, 2 + k) if (down and across) else _t(RED, 4 + k) if (down or across) else _t(GLAZE, 6 + k)
    elif kind == 2:
        c = _t(BLUE, 4 + k) if (xx % 6 == 2 and (yy - y0) % 6 == 2) else _t(GLAZE, 5 + k)
    elif kind == 3:
        c = _t(OAK, 3 + k) if (xx + (yy - y0) * 3) % 9 == 0 else _t(OAK, 4 + k)
    else:
        c = _t(ROBE, 3 + k) if (xx + yy) % 7 == 0 else _t(ROBE, 4 + k)
    try:
        return step(c, lift)
    except (KeyError, ValueError):
        return c


def tile_cell(q: Pix, ox, oy, night: bool):
    """The cell a counter's digit is set in, eleven by fifteen: a glazed tile, cream by day and the glaze in the
    dark by night, lit along its upper left, its grout round it."""
    face, lit, low, grout = ((UMBER[4], UMBER[6], UMBER[3], UMBER[1]) if night else
                             (GLAZE[5], GLAZE[6], GLAZE[3], GLAZE[1]))
    q.rect(ox, oy, 11, 15, face)
    q.hline(ox, ox + 11, oy, lit)
    q.vline(ox, oy + 1, oy + 15, lit)
    q.hline(ox + 1, ox + 11, oy + 14, low)
    q.vline(ox + 10, oy + 1, oy + 14, low)
    q.box(ox - 1, oy - 1, 13, 17, grout)


def shelf(p: Pix, x0, x1, y, night: bool):
    """The line the releases stand on, as an oak shelf: lit along its top, shaded under it, a bracket under it
    every so often."""
    o = _shade(OAK, -2 if night else 0)
    p.hline(x0, x1, y, o(5))
    p.hline(x0, x1, y + 1, o(2))
    for x in range(x0 + 12, x1 - 4, 30):
        p.px(x, y + 2, o(3))
        p.px(x, y + 3, o(2))
        p.px(x + 1, y + 2, o(1))


def release_jar(p: Pix, x, gy, kind: str, night: bool):
    """A release standing on the shelf at x: a big one a cookie jar, an ordinary one a cookie, a patch a crumb of
    one, one still to come a cookie's outline, and the repository's making a mixing bowl."""
    k = -1 if night else 0
    if kind == "big":
        art = [".kk.", "gWWg", "gccg", "gDcg", ".gg."]
        pal = {"k": _t(STEEL, 5 + k), "g": _t(GLAZE, 5 + k), "W": _t(GLAZE, 6 + k), "c": _t(DOUGH, 3 + k),
               "D": _t(DOUGH, 5 + k)}
        p.sprite(x - 2, gy - 5, art, pal)
    elif kind == "made":
        art = [".bbbbb.", "bBBBBBb", ".bbbbb.", "..bbb.."]
        p.sprite(x - 3, gy - 4, art, {"b": _t(BLUE, 3 + k), "B": _t(BLUE, 5 + k)})
    elif kind == "minor":
        p.px(x, gy - 1, _t(DOUGH, 5 + k))
        p.px(x + 1, gy - 1, _t(DOUGH, 3 + k))
    elif kind == "next":
        for dx, dy in ((0, -4), (1, -4), (-1, -3), (2, -3), (-1, -2), (2, -2), (0, -1), (1, -1)):
            p.px(x + dx, gy + dy, _t(DOUGH, 4 + k) if (dx + dy) % 2 else _t(DOUGH, 2 + k))
    else:
        art = [".ll.", "lDcD", "DcDd", ".dd."]
        pal = {"l": _t(DOUGH, 6 + k), "D": _t(DOUGH, 4 + k), "c": CHOC[1], "d": _t(DOUGH, 2 + k)}
        p.sprite(x - 1, gy - 4, art, pal)


def egg_timer(p: Pix, x, y, night: bool):
    """An egg timer over the shelf's end at today, five by seven, its sand running."""
    k = -1 if night else 0
    art = ["ooooo", ".gsg.", "..s..", ".g.g.", "gsssg", "ooooo"]
    p.sprite(x - 2, y - 7, art, {"o": _t(OAK, 4 + k), "g": _t(GLAZE, 5 + k), "s": _t(SUN, 4 + k)})


def cookie_face(p: Pix, cx, cy, i: int, person: dict, night: bool):
    """A contributor as a round cookie, fifteen across, chips in it, their initials piped on it in icing, cream or
    red by turns; a bot is a chrome toaster with a slice of toast in it."""
    k = -1 if night else 0
    if not person.get("initials"):
        art = ["....ttttt......", "...tTTTTTt.....", "ssssssssssssss.", "sSSSSSSSSSSSSsd", "sSoooooooooooSd",
               "sSSSSSSSSSSSSsd", "sSSSSSSSSSSSSsd", "sSSSSSSSSSSSSsd", "sssssssssssssdd", ".dd........dd.."]
        pal = {"t": _t(DOUGH, 3 + k), "T": _t(DOUGH, 5 + k), "s": _t(STEEL, 4 + k), "S": _t(STEEL, 5 + k),
               "o": _t(STEEL, 1 + k), "d": _t(STEEL, 2 + k)}
        p.sprite(cx - 7, cy - 5, art, pal)
        return
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 7, cx + 8):
            d = math.hypot(x + 0.5 - cx - 0.5, y + 0.5 - cy - 0.5)
            if d > 7.4:
                continue
            lit = (x - cx) * -0.6 + (y - cy) * -0.8
            c = _t(DOUGH, (6 if lit > 3 else 5 if lit > -2 else 3) + k) if d < 6.4 else _t(DOUGH, 2 + k)
            if d < 6 and (x * 7 + y * 3 + i) % 13 == 0:
                c = CHOC[1]
            p.px(x, y, c)
    icing = _t(GLAZE, 6) if i % 2 == 0 else _t(RED, 2)
    p.text(cx - 3, cy - 2, str(person["initials"])[:2], icing, "35")


def gingham_fill(p: Pix, x, y, w, fill, ink, night: bool):
    """A contributor's share as a strip of gingham in an oak edge, `fill` of it full."""
    p.box(x, y, w + 2, 4, ink)
    k = -1 if night else 0
    for xx in range(x + 1, x + 1 + fill):
        for yy in (y + 1, y + 2):
            down = ((xx - x) // 2) % 2 == 0
            p.px(xx, yy, _t(RED, 2 + k) if (down and yy == y + 1) else _t(RED, 4 + k) if down or yy == y + 1
                 else _t(GLAZE, 6 + k))


def pie_crust(p: Pix, cx, cy, r0, r1, n: int, night: bool):
    """The ring round the certificate's seal as a pie's crimped crust: golden pastry between radii r0 and r1,
    pinched into `n` scallops, lit along its upper left and baked darker along its foot."""
    k = -1 if night else 0
    for y in range(int(cy - r1) - 1, int(cy + r1) + 2):
        for x in range(int(cx - r1) - 1, int(cx + r1) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            edge = r1 - 1.6 * (0.5 + 0.5 * math.cos(a * n))
            if r0 <= d <= edge:
                lit = (-dx * 0.6 - dy * 0.8) / max(1.0, d)
                t = 6 if lit > 0.5 else 5 if lit > 0 else 4 if lit > -0.5 else 3
                if d > edge - 1.2:
                    t -= 1
                p.px(x, y, _t(DOUGH, t + k))


def sampler(p: Pix, night: bool):
    """The placard's board as a cross-stitch sampler in an oak frame: an aida cloth ground, cream by day and dark
    by night, stitched with a faint grid of crosses, inside a border of the curtains' gingham."""
    w, h = p.w, p.h
    o = _shade(OAK, -2 if night else 0)
    ground, cross = (UMBER[2], UMBER[3]) if night else (GLAZE[6], GLAZE[4])
    fill(p, 0, 0, w, h, ground, "base")
    cells = {(1, 1): cross, (3, 3): cross, (3, 1): cross, (1, 3): cross, (2, 2): cross}
    pid = "aida"
    if ("pattern", pid) not in p.syms:
        p.defs.append(f'<pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse">{p.markup(cells)}'
                      f'</pattern>')
        p.syms[("pattern", pid)] = pid
    p.shapes["base"].append(f'<rect x="4" y="4" width="{w - 8}" height="{h - 8}" fill="url(#{pid})"/>')
    check = gingham(p, night)
    for (x, y, ww, hh) in ((3, 3, w - 6, 2), (3, h - 5, w - 6, 2), (3, 3, 2, h - 6), (w - 5, 3, 2, h - 6)):
        p.shapes["base"].append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" fill="{check}"/>')
    for i, c in enumerate((OAK[0], o(5), o(4))):
        p.box(i, i, w - 2 * i, h - 2 * i, c)
    p.px(0, 0, OAK[0])


def sunflower_mark(p: Pix, x, y, night: bool):
    """A sunflower beside the placard's title, seven by seven."""
    sunflower(p, x, y - 3, night)
