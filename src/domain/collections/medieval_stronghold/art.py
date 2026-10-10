# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Stronghold set's scenery and sprites, drawn on the shared pixel canvas.

The ashlar the sheet is dressed in, the battlements and corner towers of its frame, the pennants that wave
across its top, the castle, gatehouse and watchtower its headers stand on, the clouds and the hawk of the
day, the torches, the moon and the dragon of the night, letters carved into the stone, and the heraldry
every element and badge carries: shields, swords, lions, helms, pennants and wax. Everything is shaded
from the one light in the upper left on the set's own ramps.

A title's line is drawn once and placed for each wall of its cut, and a drawing's last pass lays each tower's
courses as a pattern, so a full page keeps its whole scene within its budget. A drawing made lighter still thins
only texture no one misses at 1x (see `THIN`)."""
from __future__ import annotations

import math
import random
import weakref

from ...holidays.designs.banners import MARK_Y
from ...holidays.pixel import FONTS, LX, LY, LZ, Paint, Pix, fold, num, sphere
from ..hand import MEDIEVAL
from .palette import C, NIGHT_SKY, RAMP, STONE, TINCTURES, WATER, X

# The canvases drawn lighter to fit a budget. On them only texture a reader does not miss at 1x is thinned: the
# stone goes without its stipple, each torch's light without its outer ring, and the night without its faintest
# stars. Every figure, building, light and title and all the motion stay.
THIN: weakref.WeakSet = weakref.WeakSet()
# For each canvas, the stretches of its rule that the moat of a phone's scene under its words lies on, which the
# ivy keeps off.
MOATS: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def mark_box(p: Pix, margin=2) -> tuple:
    """The box the month's mark takes at the top centre of a header, `margin` units more all round: (x0, y0, x1, y1),
    ends excluded. A header keeps it clear of its scene whether or not it is drawn as its month's design."""
    n = MEDIEVAL.mark_size
    x0, y0 = p.w // 2 - n // 2, MARK_Y - n // 2
    return (x0 - margin, y0 - margin, x0 + n + margin, y0 + n + margin)


def _tone(v: float, x: int, y: int, lo: int, hi: int) -> int:
    """A value on a ramp, rounded, with a thin band of checkerboard where two tones meet."""
    b = math.floor(v)
    f = v - b
    if f >= 0.62 or (f > 0.38 and (x + y) % 2 == 0):
        b += 1
    return max(lo, min(hi, b))


def stone_ramp(night: bool) -> list:
    """The stone's tones: warm limestone by day, the same stone moonlit by night."""
    return RAMP["slate" if night else "stone"]


# --------------------------------------------------------------------------- the paper
def _ashlar(uid: str, lit: str, mortar: str, shade: str) -> str:
    """A pattern tile of dressed stone, two courses of blocks in running bond, 40 by 16: each block's top
    and left edge catch the light, its right and foot fall into shade, and a line of mortar runs between."""
    out = {lit: {}, mortar: {}, shade: {}}
    for y in range(16):
        course, r = divmod(y, 8)
        for x in range(40):
            xs = (x - 10 * course) % 20
            if r == 7 or xs == 19:
                c = mortar
            elif r == 0 or xs == 0:
                c = lit
            elif r == 6 or xs == 18:
                c = shade
            else:
                continue
            out[c].setdefault(y, []).append(x)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(rows)}"/>' for c, rows in out.items() if rows)
    return f'<pattern id="{uid}a" width="40" height="16" patternUnits="userSpaceOnUse">{paths}</pattern>'


def paper(p: Pix, night: bool, x=0, y=None, w=None, h=None, uid="p"):
    """The ground a drawing sits on: a wall of dressed limestone by day, the same wall in moonlit blue-grey
    by night, darker toward its foot. The paper starts under the frame's merlons (row 2), so the crenels
    between them stay open to whatever ground the file is shown on."""
    y = 2 if y is None else y
    w = p.w if w is None else w
    h = p.h - y if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
        p.defs.append(_ashlar(uid, C["lit"], C["mortar"], C["shade"]))
    else:
        n = len(NIGHT_SKY)
        edges = [y + round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" '
                           f'fill="{col}"/>')
        p.defs.append(_ashlar(uid, C["lit_n"], C["mortar_n"], C["shade_n"]))
    p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}a)"/>')


# --------------------------------------------------------------------------- the night sky
def sparkle(p: Pix, x, y, big=False, L="base", warm=False):
    """A four-point glint: a white heart, arms that fade, longer arms on the brightest."""
    arm = RAMP["gold"][5] if warm else X["star_pale"]
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.5", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """A night's stars over the wall at three magnitudes: faint pinpricks, bright points, and a few glints.
    None is set inside a box in `avoid` (x0, y0, x1, y1), so no glint sits in a letter or beside a word. A
    drawing made lighter leaves the faint pinpricks out; every other star stands where it would."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.5 or faint:
            c = rnd.choice((X["star_faint"], X["star_dim"]))
            if p not in THIN:
                p.px(x, y, c, "haze")
        elif k < 0.88:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.5) else "haze"
            p.px(x, y, rnd.choice((C["white"], RAMP["gold"][5], X["star_pale"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.3)


def moon(p: Pix, cx, cy, r, L="base"):
    """A crescent moon, the collection's moon on its moon ramp: its lit limb shaded as a ball, the earthshine on its
    dark part in the ramp's darkest tone, a halo in the sky and two seas on the limb."""
    M = RAMP["moon"]
    ox, oy, rr = cx + r * 0.58, cy - r * 0.28, r * 0.92

    def lit(xx, yy):
        return math.hypot(xx + 0.5 - ox, yy + 0.5 - oy) > rr

    p.halo(cx, cy, r * 2.6, r * 2.6, M[3], (0.03, 0.05, 0.08, 0.12))
    for yy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for xx in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            if math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) <= r and not lit(xx, yy):
                p.px(xx, yy, M[0], L)
    sphere(p, cx, cy, r, M, L, lo=2, hi=6, rim=False, outline=False, only=lit)
    for (dx, dy) in ((-0.5, 0.1), (-0.25, 0.55)):
        qx, qy = math.floor(cx + dx * r), math.floor(cy + dy * r)
        if lit(qx, qy) and math.hypot(qx + 0.5 - cx, qy + 0.5 - cy) <= r - 0.5:
            p.px(qx, qy, M[2], L)


# --------------------------------------------------------------------------- the day sky
def _cloud_symbol(p: Pix, kind: int):
    """A cloud drawn once: a bank of puffs 30 to 40 wide with a flat foot, bright where the light lands on
    its crown and left, its body soft white, and its underside shaded down to a grey that reads against the
    stone."""
    key = ("cloud", kind)
    if key in p.syms:
        return key
    rnd = random.Random(kind * 17 + 3)
    Cl = RAMP["cloud"]
    puffs = [(0, 0, 4.2)]
    x = 0.0
    for _ in range(rnd.randint(4, 6)):
        x += rnd.uniform(3.8, 5.4)
        puffs.append((x, rnd.uniform(-1.4, 1.0), rnd.uniform(3.2, 5.4)))
    cells = {}
    for (px_, py_, r) in puffs:
        for yy in range(math.floor(py_ - r), math.ceil(py_ + r) + 1):
            for xx in range(math.floor(px_ - r), math.ceil(px_ + r) + 1):
                dx, dy = xx + 0.5 - px_, (yy + 0.5 - py_) * 1.3
                if dx * dx + dy * dy <= r * r and yy <= py_ + r * 0.5:
                    cells[(xx, yy)] = 5
    base = max(yy for (_, yy) in cells)
    for (xx, yy) in list(cells):
        up, left = (xx, yy - 1) not in cells, (xx - 1, yy) not in cells
        if yy == base:
            cells[(xx, yy)] = 1
        elif yy == base - 1:
            cells[(xx, yy)] = 2
        elif yy == base - 2:
            cells[(xx, yy)] = 3
        elif up or left:
            cells[(xx, yy)] = 6
        elif (xx + 1, yy) not in cells:
            cells[(xx, yy)] = 4
    p.symbol(key, {(x_, y_ + 7): Cl[t] for (x_, y_), t in cells.items()})
    return key


DRIFT = 48.0        # seconds the clouds take to drift the width of the sky: the slowest of the hand's sweeps


def clouds(p: Pix, x0, y0, x1, y1, n, seed=5, motion=True, name="cl"):
    """Clouds drifting slowly across the sky behind everything on the sheet, between x0 and x1 and above
    y1: drawn once and shown again a window to the left, stepping right a pixel at a time, so the drift
    loops without a seam once every `DRIFT` seconds. A still drawing leaves them where they lie."""
    rnd = random.Random(seed)
    period = x1 - x0
    anim = None
    if motion:
        cid = f"{name}c"
        p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{period}" height="{y1 - y0}"/></clipPath>')
        anim = ("drift", x0, y0, x1, y1, period, cid, DRIFT / period)
    L = p.layer(name, anim, z=-11)
    for i in range(n):
        key = _cloud_symbol(p, i % 5)
        p.use(key, x0 + rnd.randrange(0, period), rnd.randrange(y0, max(y0 + 1, y1 - 14)), L)


# A hawk seen from below, 21 wide: wings spread with fingered tips, a short head and a rust-red fanned tail
# (`t`), its wings raised in a shallow V and then held level.
HAWK = [
    ["#...................#", "##.................##", ".###.............###.", "..####....#....####..",
     "....######.######....", ".......###.###.......", "........#t#t#........", ".........ttt........."],
    [".....................", "..........#..........", "#########.#.#########", ".###################.",
     "...###.........###...", "........#.#.#........", ".........ttt.........", "........t...t........"],
]


def _hawk_symbol(p: Pix, frame: int):
    key = ("hawk", frame)
    if key not in p.syms:
        W, R = RAMP["wood"], RAMP["gules"]
        art = HAWK[frame]
        ink = {(i, j): ch for j, r in enumerate(art) for i, ch in enumerate(r) if ch != "."}
        cells = {}
        for (i, j), ch in ink.items():
            if ch == "t":
                cells[(i, j)] = R[3] if (i, j - 1) in ink else R[4]
            else:
                cells[(i, j)] = W[3] if (i, j - 1) not in ink else W[1]
        cells[(10, 3 if frame == 0 else 1)] = W[5]          # the head catches the light
        p.symbol(key, cells)
    return key


def hawk(p: Pix, cx, cy, rx, ry, motion=True, seed=0, steps=48, dur=8.0):
    """A hawk soaring in a slow circle over (cx, cy), once round in `dur` seconds, a figure's loop in the hand's
    four to eight, beating its wings now and then; the still file leaves it where its circle begins."""
    rnd = random.Random(seed)
    frames = [_hawk_symbol(p, 0), _hawk_symbol(p, 1)]
    a0 = rnd.uniform(0, 2 * math.pi)
    path = [(round(cx + rx * math.cos(a0 + 2 * math.pi * s / steps) - 10),
             round(cy + ry * math.sin(a0 + 2 * math.pi * s / steps) - 4)) for s in range(steps)]
    if motion:
        p.fly(frames, path, dur, 16, flap=0.7)
    else:
        p.use(frames[0], path[0][0], path[0][1], "base")


# --------------------------------------------------------------------------- the dragon
def _dragon_symbol(p: Pix, frame: int, flip: bool):
    """A dragon in flight, drawn once: a long neck to a horned head, bat wings raised or swept down, a
    tail ending in a spade, and a short flame from its mouth. Dark against the night, with moonlight along
    the edges that face the sky."""
    key = ("dragon", frame, flip)
    if key in p.syms:
        return key
    D, F = RAMP["dragon"], RAMP["flame"]
    cells: dict = {}

    def disc(x, y, r, tag):
        for yy in range(math.floor(y - r), math.ceil(y + r) + 1):
            for xx in range(math.floor(x - r), math.ceil(x + r) + 1):
                if (xx + 0.5 - x) ** 2 + (yy + 0.5 - y) ** 2 <= r * r:
                    cells[(xx, yy)] = tag

    def line(x0, y0, x1, y1, tag, r=0.6):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) * 2))
        for i in range(n + 1):
            t = i / n
            disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, tag)

    def tri(a, b, c, tag):
        xs = [a[0], b[0], c[0]]
        ys = [a[1], b[1], c[1]]
        for yy in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
            for xx in range(math.floor(min(xs)), math.ceil(max(xs)) + 1):
                px_, py_ = xx + 0.5, yy + 0.5
                d1 = (px_ - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (py_ - b[1])
                d2 = (px_ - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (py_ - c[1])
                d3 = (px_ - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (py_ - a[1])
                if not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0)):
                    cells[(xx, yy)] = tag

    if frame == 0:
        tri((10.5, 6.5), (16.5, -0.5), (18.5, 5.5), "wing")      # the near wing, raised
        tri((9.5, 6.5), (5.5, 0.5), (8.5, 5.0), "wing")          # the far wing
    else:
        tri((10.5, 7.0), (14.5, 13.5), (18.0, 8.5), "wing")      # swept down
        tri((9.5, 7.0), (6.5, 12.0), (8.0, 8.5), "wing")
    disc(12.0, 7.5, 2.6, "body")
    disc(9.0, 7.5, 2.0, "body")
    line(7.0, 6.5, 3.6, 3.4, "neck", 0.95)
    disc(3.0, 2.9, 1.6, "head")
    disc(1.2, 3.4, 1.0, "head")
    cells[(2, 0)] = "horn"
    cells[(3, 1)] = "horn"
    line(14.5, 7.5, 20.5, 5.0, "tail", 0.75)
    line(20.5, 5.0, 23.5, 6.5, "tail", 0.55)
    for q in ((23, 5), (24, 6), (23, 7), (22, 6)):
        cells[q] = "tail"
    for (lx, ly) in ((10, 10), (13, 10)):
        cells[(lx, ly)] = cells[(lx, ly + 1)] = "leg"
        cells[(lx - 1, ly + 2)] = "leg"
    out = {}
    for (x, y), tag in cells.items():
        up, left = (x, y - 1) not in cells, (x - 1, y) not in cells
        if tag == "wing":
            c = D[3] if (up and left) else D[4] if up else (D[1] if (x + y) % 3 else D[2])
        elif tag == "horn":
            c = D[5]
        elif tag == "leg":
            c = D[1]
        else:
            c = D[5] if (up and left) else D[4] if (up or left) else (D[1] if (x + 1, y) not in cells else D[2])
        out[(x, y)] = c
    out[(2, 3)] = F[5]                     # the eye
    for q, c in (((-1, 4), F[5]), ((-2, 4), F[4]), ((-3, 4), F[3]), ((-2, 3), F[6]), ((-4, 4), F[2]), ((-3, 5), F[3])):
        out[q] = c
    if flip:
        out = {(-x, y): c for (x, y), c in out.items()}
    p.symbol(key, out)
    return key


def glide(p: Pix, frames, path, dur, z, clip, flap=0.42):
    """Something that flies through a window of the sky: like `Pix.fly`, but clipped to `clip`
    (x0, y0, x1, y1), so it can enter from beyond the frame and leave behind a tower. The still file shows
    the first frame at the path's first point."""
    ids = [p.syms[f] for f in frames]
    steps = ";".join(f"{x} {y}" for x, y in path)
    n = len(ids)
    uses = []
    for i, sid in enumerate(ids):
        vals = ";".join("1" if j == i else "0" for j in range(n))
        hidden = ' opacity="0"' if i else ""
        uses.append(f'<use href="#{sid}"{hidden}><animate attributeName="opacity" values="{vals}" '
                    f'dur="{num(flap * n)}s" repeatCount="indefinite" calcMode="discrete"/></use>')
    cid = f"gl{len(p.raws)}"
    x0, y0, x1, y1 = clip
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    moving = (f'<g clip-path="url(#{cid})"><g>{"".join(uses)}<animateTransform attributeName="transform" '
              f'type="translate" values="{steps}" dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/>'
              f'</g></g>')
    sx, sy = path[0]
    p.raw(z, moving, f'<use href="#{ids[0]}" x="{sx}" y="{sy}"/>')


def dragon(p: Pix, start, hide, clip, motion=True, toward=-1, hold=10, step=2, dur=None):
    """A dragon crossing the sky: it enters from beyond the frame, flies the way `toward` points (-1 left),
    dipping as it goes, and lands out of sight behind the tower at `hide`, where it waits before the loop
    begins again beyond the frame. `start` is where the still file shows it, mid-flight. Drawn behind the
    castle, so a tower can hide it."""
    flip = toward > 0
    frames = [_dragon_symbol(p, 0, flip), _dragon_symbol(p, 1, flip)]
    if not motion:
        p.use(frames[0], start[0], start[1], "far")
        return
    x0, y0, x1, y1 = clip
    far = x1 + 6 if toward < 0 else x0 - 30
    sx, sy = start
    hx, hy = hide
    path = []
    n = max(1, round(max(abs(hx - sx) / step, abs(hy - sy) / (2 * step))))
    for i in range(n):
        t = i / n
        path.append((round(sx + (hx - sx) * t), round(sy + (hy - sy) * t * t)))
    path += [hide] * hold
    m = max(1, round(abs(sx - far) / step))
    for i in range(m):
        t = i / m
        path.append((round(far + (sx - far) * t), round(y0 + 2 + (sy - y0 - 2) * t ** 1.4)))
    glide(p, frames, path, dur or len(path) * 0.09, -5, clip)


# --------------------------------------------------------------------------- the frame
def _band(uid: str, S: list, vertical: bool) -> str:
    """A pattern tile of carved stone moulding four pixels across: a lit outer edge, a face with a billet
    cut every eight pixels, and the shadow it throws on the wall."""
    cols = {S[6]: {}, S[4]: {}, S[3]: {}, S[1]: {}}
    for i in range(8):
        for k in range(4):
            billet = i in (6, 7)
            c = S[1] if (k == 3 or billet) else S[6] if k == 0 else S[4] if k == 1 else S[3]
            if billet and k == 0:
                c = S[3]
            x, y = (k, i) if vertical else (i, k)
            cols[c].setdefault(y, []).append(x)
    w, h = (4, 8) if vertical else (8, 4)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(rows)}"/>' for c, rows in cols.items() if rows)
    return f'<pattern id="{uid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{paths}</pattern>'


def _parapet(uid: str, S: list) -> str:
    """A pattern tile of the parapet, 24 by 4: merlons two rows tall with the crenels between them open, over
    a lit coping and a row of the wall's face with its joints."""
    cols: dict = {}
    for xx in range(24):
        k = xx % 8
        if k < 5:
            cols.setdefault(S[6] if k < 4 else S[3], {}).setdefault(0, []).append(xx)
            cols.setdefault(S[6] if k == 0 else S[4] if k < 4 else S[2], {}).setdefault(1, []).append(xx)
        cols.setdefault(S[6], {}).setdefault(2, []).append(xx)
        cols.setdefault(S[2] if xx % 6 == 1 else S[4], {}).setdefault(3, []).append(xx)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(rows)}"/>' for c, rows in cols.items())
    return f'<pattern id="{uid}m" width="24" height="4" patternUnits="userSpaceOnUse">{paths}</pattern>'


def frame(p: Pix, night: bool, towers: bool = False, plinth: bool = False, x=0, y=0, w=None, h=None, uid="fr"):
    """The sheet's border in dressed stone: carved mouldings down the sides and, along the top, a parapet
    with its merlons, with a round tower at each corner on a header (`towers`) and from edge to edge on any
    other sheet. The foot is the moulding too, or on a footer (`plinth`) a plinth: a lit ledge standing proud
    of the wall over courses of blocks, its shadow on the wall above it. The crenels between the merlons are
    open: the paper stops under them."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    S = stone_ramp(night)
    foot = 5 if plinth else 4
    p.defs.append(_band(uid + "v", S, True))
    for bx in (x, x + w - 4):
        p.shapes["base"].append(f'<rect x="{bx}" y="{y + 4}" width="4" height="{h - 4 - foot}" fill="url(#{uid}v)"/>')
    if plinth:
        ledge = y + h - foot
        for xx in range(x, x + w):
            p.apx(xx, ledge - 1, X["shade_ink"], 0.22, "base")
            p.px(xx, ledge, S[6])
            for yy in range(ledge + 1, y + h - 1):
                p.px(xx, yy, S[2] if (xx - x + (yy - ledge) * 5) % 12 == 0 else S[4])
            p.px(xx, y + h - 1, S[1])
    else:
        p.defs.append(_band(uid + "h", S, False))
        p.shapes["base"].append(f'<rect x="{x}" y="{y + h - 4}" width="{w}" height="4" fill="url(#{uid}h)"/>')
    p.defs.append(_parapet(uid, S))
    inset = 8 if towers else 0
    p.shapes["base"].append(f'<rect x="{x + inset}" y="{y}" width="{w - 2 * inset}" height="4" fill="url(#{uid}m)"/>')
    for xx in range(x + 4, x + w - 4):
        p.apx(xx, y + 4, X["shade_ink"], 0.22, "base")
    if towers:
        for (tx, flip) in ((x, False), (x + w - 9, True)):
            corner_tower(p, tx, y, 9, 9, night, flip)


def corner_tower(p: Pix, x, y, w, h, night, flip=False, L="base"):
    """A round tower at a frame's corner, `w` by `h` with its top at `y`: shaded as a column lit from the
    left, with merlons of its own and a dark arrow slit, standing proud of the wall."""
    S = stone_ramp(night)
    lo, hi = (1, 4) if night else (2, 5)
    for yy in range(y + 2, y + h):
        for xx in range(x, x + w):
            u = (xx + 0.5 - x) / w
            nx = 2 * u - 1
            lam = max(0.0, nx * LX + math.sqrt(max(0.0, 1 - nx * nx)) * LZ + 0.1)
            t = max(lo, min(hi, round(lo + (hi - lo + 0.6) * lam)))
            if (yy - y) % 3 == 1:
                t = max(lo - 1, t - 1)
            p.px(xx, yy, S[t], L)
        p.px(x, yy, S[hi + 1], L)
        p.px(x + w - 1, yy, S[lo - 1], L)
    for xx in range(x, x + w):
        k = (xx - x) % 3
        if k != 2:
            p.px(xx, y, S[6] if k == 0 else S[4], L)
            p.px(xx, y + 1, S[5] if k == 0 else S[3], L)
    p.hline(x, x + w, y + 2, S[6], L)
    sx = x + w // 2
    p.vline(sx, y + 4, y + 7, S[0], L)
    if flip:
        return
    for yy in range(y + 2, y + h):
        p.apx(x + w, yy, X["shade_ink"], 0.22, L)


# --------------------------------------------------------------------------- pennants
WAVE = ("wave0", "wave1", "wave2")


def wave_layer(p: Pix, k: int, lite: bool = False) -> str:
    """One of three moments of a wave, shown in turn, a pennant's tail swinging left, straight, right. The
    still file keeps the first, and so does a banner that holds one moment (`lite`), as a phone's do."""
    if lite:
        return "base"
    return p.seq(WAVE[k % 3], (k % 3) / 3, (k % 3 + 1) / 3, 1.35, keep=k % 3 == 0, z=1)


PENNANT = ["#####", "#####", ".###.", ".###.", "..#..", "..#.."]


def _pennant_symbol(p: Pix, tincture: str, frame: int, night: bool):
    """A pennant hanging from a cord, 5 by 6, drawn once for each tincture and moment of its wave: lit along
    its left edge, shaded down its right, its tail swung a pixel left or right as the wind takes it."""
    key = ("pennant", tincture, frame, night)
    if key in p.syms:
        return key
    R = RAMP[tincture]
    k = -1 if night else 0
    cells = {}
    swing = (0, -1, 1)[frame]
    for j, row in enumerate(PENNANT):
        inked = [i for i, ch in enumerate(row) if ch == "#"]
        dx = swing if j >= 3 else 0
        for i in inked:
            t = 5 if i == inked[0] else (3 if i == inked[-1] else 4)
            if j == 0:
                t = min(6, t + 1)
            cells[(i + dx, j)] = R[max(0, t + k)]
    p.symbol(key, cells)
    return key


def cord(p: Pix, pts, night, L="base"):
    """A rope strung along `pts`: twisted, a strand catching the light every fourth pixel."""
    W = RAMP["wood"]
    for i, (xx, yy) in enumerate(pts):
        p.px(xx, yy, (W[4] if night else W[5]) if i % 4 == 0 else (W[2] if night else W[3]), L)
    for (a, b) in zip(pts, pts[1:]):
        if abs(a[1] - b[1]) > 1:
            for yy in range(min(a[1], b[1]), max(a[1], b[1])):
                p.px(a[0], yy, W[2] if night else W[3], L)


def pennants(p: Pix, x0, x1, y, sag=4, span=38, spacing=10, night=False, seed=0):
    """A line of heraldic pennants, gules, or, azure and argent by turns, hanging from a rope that sags
    between its hooks and waving in the wind of a moving header: each pennant is shown at three moments
    of its swing in turn, its neighbours a moment behind, so a ripple runs down the line. The rope runs on
    behind the month's mark at the top centre, but the pennants pause there, two units clear of its box, so
    none is cut at the roundel's edge, whether or not the mark is drawn."""
    I = RAMP["iron"]
    a, b, c, d = mark_box(p)
    pts = []
    x = x0
    while x < x1:
        seg_end = min(x + span, x1)
        for xx in range(x, seg_end):
            t = (xx - x) / max(1, seg_end - x)
            pts.append((xx, y + round(sag * 4 * t * (1 - t))))
        x = seg_end
    cord(p, pts, night)
    for hx in (x0, x1 - 1):
        p.px(hx, y, I[5])
        p.px(hx, y + 1, I[3])
    i = 0
    for k, (xx, yy) in enumerate(pts):
        if k % spacing == spacing // 2 and 4 <= xx - x0 and x1 - xx >= 4:
            if xx - 3 < c and a < xx + 4 and yy + 1 < d and b < yy + 7:
                continue
            tincture = TINCTURES[(i + seed) % len(TINCTURES)]
            for slot in range(3):
                frame = (slot + i) % 3
                p.use(_pennant_symbol(p, tincture, frame, night), xx - 2, yy + 1, wave_layer(p, slot))
            i += 1


def flag(p: Pix, x, y, tincture: str, night: bool, lite: bool = False, size: int = 5, big: bool = False):
    """A banner on a tower's pole: the pole at x from `y` down, the flag flying to the right from its top
    at three moments of its wave in turn (one, held, when `lite`). `big` flies a square banner with a
    charge instead of a pennant."""
    I = RAMP["iron"]
    R = RAMP[tincture]
    k = -1 if night else 0
    p.vline(x, y, y + size + 3, I[4] if night else I[3])
    p.px(x, y - 1, RAMP["gold"][4])
    for slot in range(1 if lite else 3):
        key = ("flag", tincture, slot, night, size, big)
        if key not in p.syms:
            cells = {}
            rows = size - 1 if big else 3
            for j in range(rows):
                w = size if big else (size - j if j else size)
                lift = ((slot + j) % 3) - 1 if j else 0
                for i in range(w):
                    t = 5 if j == 0 else (4 if i < w - 1 else 3)
                    if big and (i == size // 2 or j == rows // 2):
                        cells[(1 + i, j + lift)] = RAMP["gold" if tincture != "gold" else "gules"][4 + k]
                        continue
                    cells[(1 + i, j + lift)] = R[max(0, t + k)]
            p.symbol(key, cells)
        p.use(key, x, y, wave_layer(p, slot, lite))


# --------------------------------------------------------------------------- torches and lamplight
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `lamplight` lays its warm light on the stone
    within `r` of it, flickering with the flame. `own` are the lamp's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def pool(p: Pix, cx, cy, rx, ry, col, alphas, **kw):
    """A pool of light, in `Pix.halo`'s stepped rings. A drawing made lighter leaves out the faint outer ring
    and keeps the rings inside it as they were."""
    kw.setdefault("shape", kw.get("only") is None and max(rx, ry) > 6)
    if p in THIN and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, **kw)


def lamplight(p: Pix):
    """The finishing pass by night: each torch's light on the stone near it, strongest nearest the flame.
    The sky, the paper and the words take none. A drawing made lighter keeps only the inner, stronger ring."""
    base = p.layers["base"]
    col = RAMP["flame"][3]
    alphas = (0.1, 0.24)
    n = len(alphas)
    reach = 0.5 if p in THIN else 1
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y))
                if c is None or (x, y) in own or c not in STONE:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15) / r
                if d < reach:
                    p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], L)


def torch(p: Pix, x, y, phase=0, side=1, reach=8, L="base"):
    """A torch in an iron sconce on a wall, its flame's foot at (x, y): a teardrop flame that flickers
    with its glow, and warm light on the stone round it (see `lamplight`). Night only."""
    F, I, W = RAMP["flame"], RAMP["iron"], RAMP["wood"]
    p.px(x, y + 1, W[3], L)
    p.px(x, y + 2, W[2], L)
    p.px(x + side, y + 2, I[4], L)
    p.px(x + side, y + 3, I[2], L)
    Lf = p.flicker(phase)
    cells = ((0, 0, F[6]), (0, -1, F[6]), (-1, -1, F[4]), (1, -1, F[4]), (0, -2, F[5]), (-1, -2, F[3]), (1, -2, F[3]),
             (0, -3, F[4]), (0, -4, F[3]))
    for (dx, dy, c) in cells:
        p.px(x + dx, y + dy, c, Lf)
    pool(p, x + 0.5, y - 1.5, 7.5, 7.0, F[3], (0.06, 0.12, 0.2), L=p.flicker(phase, back=True))
    own = {(x + dx, y + dy) for dx, dy, _ in cells} | {(x, y + 1), (x, y + 2)}
    lamp(p, x + 0.5, y - 1, reach, phase, own)


SCONCE = ["..hhh..", ".hHhhh.", ".hhhhh.", "...s...", ".LIsIi.", "...s...", ".RIsIR.", ".IIsII.", ".RIIIR."]


def sconce(p: Pix, x, y, night, phase=0, L="base"):
    """A torch in an iron wall bracket, 7 by 9 from (x, y): a plate riveted to the stone at its corners, the
    ring above it that holds the torch's oak shaft, and the pitch-wrapped head above that, unlit by day and
    by night burning, with its light on the wall round it."""
    I, W, F = RAMP["iron"], RAMP["wood"], RAMP["flame"]
    k = -1 if night else 0
    pal = {"h": W[1], "H": W[2], "s": W[4 + k], "I": I[3 + k], "L": I[5 + k], "i": I[2 + k], "R": I[6 + k]}
    p.sprite(x, y, SCONCE, pal, 1, L)
    if not night:
        return
    Lf = p.flicker(phase)
    fx, fy = x + 3, y + 1
    cells = ((0, 0, F[6]), (0, -1, F[6]), (-1, -1, F[4]), (1, -1, F[4]), (0, -2, F[5]), (-1, -2, F[3]), (1, -2, F[3]),
             (0, -3, F[4]), (0, -4, F[3]))
    for (dx, dy, c) in cells:
        p.px(fx + dx, fy + dy, c, Lf)
    pool(p, fx + 0.5, fy - 1.5, 9, 8, F[3], (0.07, 0.14, 0.24), L=p.flicker(phase, back=True))


def lit_window(p: Pix, x, y, h, night, phase=0, L="base"):
    """An arrow slit `h` tall at (x, y): dark by day; by night candlelit, a steady warm light with a
    brighter heart that flickers faintly, and a little of its light on the stone round it."""
    S, F = stone_ramp(night), RAMP["flame"]
    if not night:
        p.vline(x, y, y + h, S[0], L)
        return
    for yy in range(y, y + h):
        p.px(x, yy, F[3], L)
    Lf = p.flicker(phase)
    p.px(x, y + h // 2, F[5], Lf)
    for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        p.px(x + dx, y + h // 2 + dy, F[3] + ":0.3", Lf)


def glimmer(p: Pix, x, g, phase=0):
    """A torch's light on the moat under it: a warm pool on the water's surface, row g and the two above,
    and the streak of its reflection, shivering with the flame."""
    F = RAMP["flame"]
    Lf = p.flicker(phase)
    pool(p, x + 0.5, g - 0.5, 8, 2.6, F[3], (0.1, 0.2, 0.32), L=Lf, only=WATER, shape=False)
    for yy in range(g - 2, g + 1):
        for dx in (-1, 0, 1):
            if (yy + dx) % 2 == 0:
                p.apx(x + dx, yy, F[4], 0.3, Lf)


# --------------------------------------------------------------------------- masonry
# The tower bodies drawn on each canvas, in the order drawn, for `lay_courses`: (x0, top, w, base, tile).
COURSES: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def _course_tone(i, row, w, lo, hi) -> int:
    """The tone of a round tower's stone `i` pixels in from its left and `row` rows up from its foot: shaded as
    a column lit from the left, a step darker along the joint under each course and at each block's end, with
    a lit left edge and a dark right edge. Every eighth row repeats: the courses are four rows tall and each
    course's joints fall half a block along from the one under it."""
    if i == w - 1:
        return lo - 1
    if i == 0:
        return hi + 1
    u = (i + 0.5) / w
    nx = 2 * u - 1
    lam = max(0.0, nx * LX + math.sqrt(max(0.0, 1 - nx * nx)) * LZ + 0.1)
    t = max(lo, min(hi, round(lo + (hi - lo + 0.6) * lam)))
    if row % 4 == 3 or (i + (row // 4) * 4) % 8 == 0:
        t = max(lo - 1, t - 1)
    return t


def lay_courses(p: Pix):
    """The last pass over a drawing: each tower's body, drawn a pixel at a time, laid again as a pattern of its
    eight repeating rows of courses, and its pixels let go wherever they still show the body's own stone. Every
    pixel looks as it did, the body now under what was drawn over it; a body too small or too hidden to save
    bytes this way is left as it was drawn."""
    bodies = COURSES.pop(p, [])
    if not bodies:
        return
    base = p.layers["base"]
    by: dict = {}                  # the layer's pixels by colour, as its paths are written
    for (x, y), c in base.items():
        by.setdefault(c, set()).add((x, y))

    def cost(cells) -> int:
        rows: dict = {}
        for (x, y) in cells:
            rows.setdefault(y, []).append(x)
        return len(Pix._d(rows)) + 28 if rows else 0     # 28: the path's own tag and colour
    for k, (x0, top, w, foot, tile) in enumerate(bodies):
        # The body's pixels that still show its own stone; one under a body drawn later is that body's to lay.
        later = [(a, t, a + n, f) for a, t, n, f, _ in bodies[k + 1:]]
        shown: dict = {}
        for y in range(top, foot):
            for x in range(x0, x0 + w):
                c = tile[(x - x0, (foot - 1 - y) % 8)]
                if base.get((x, y)) == c and not any(a <= x < b and t <= y < f for a, t, b, f in later):
                    shown.setdefault(c, set()).add((x, y))
        key = ("courses", w, tuple(sorted(tile.items())))
        pid = p.syms.get(key) or f"cs{sum(1 for q in p.syms if isinstance(q, tuple) and q[0] == 'courses')}"
        pattern = "" if key in p.syms else _courses_pattern(pid, w, tile)
        rect = (f'<rect transform="translate({x0} {foot})" y="-{foot - top}" width="{w}" height="{foot - top}" '
                f'fill="url(#{pid})"/>')
        saved = sum(cost(by[c]) - cost(by[c] - cells) for c, cells in shown.items())
        if saved <= len(rect) + len(pattern):
            continue
        if pattern:
            p.defs.append(pattern)
            p.syms[key] = pid
        p.shapes["base"].append(rect)
        for c, cells in shown.items():
            by[c] -= cells
            for xy in cells:
                del base[xy]


def _courses_pattern(pid: str, w: int, tile: dict) -> str:
    """A tower body's eight rows of courses, `w` wide, as a pattern tile laid from the body's foot up."""
    rows: dict = {}
    for (i, r), c in tile.items():
        rows.setdefault(c, {}).setdefault(7 - r, []).append(i)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(rs)}"/>' for c, rs in sorted(rows.items()))
    return f'<pattern id="{pid}" width="{w}" height="8" patternUnits="userSpaceOnUse">{paths}</pattern>'


def tower(p: Pix, cx, base, w, h, night, roof=False, banner=None, slits=(), phase=0, lite=False, L="base",
          big_flag=False):
    """A round tower standing on row `base`, `w` wide and `h` tall to the top of its merlons (or the eave of
    its roof): shaded as a column lit from the left with courses of blocks, a lit left edge and a dark
    right edge; merlons or a conical slate roof on top; arrow slits at the heights in `slits`, candlelit
    by night; and a banner in `banner`'s tincture flying from a pole. Its body is kept for `lay_courses`."""
    S = stone_ramp(night)
    lo, hi = (1, 4) if night else (2, 5)
    x0 = cx - w // 2
    top = base - h
    body_top = top if roof else top + 2
    tile = {(i, r): S[_course_tone(i, r, w, lo, hi)] for i in range(w) for r in range(8)}
    for y in range(body_top, base):
        for x in range(x0, x0 + w):
            p.px(x, y, tile[(x - x0, (base - 1 - y) % 8)], L)
    if L == "base" and body_top < base:
        COURSES.setdefault(p, []).append((x0, body_top, w, base, tile))
    if roof:
        I = RAMP["iron"]
        rh = w - 1
        for j in range(rh + 1):
            half = (w / 2 + 1) * (1 - j / (rh + 1))
            y = top - 1 - j
            for x in range(math.floor(cx + 0.5 - half), math.ceil(cx + 0.5 + half)):
                u = (x + 0.5 - cx - 0.5) / max(0.5, half)
                c = I[5 if u < -0.35 else 4 if u < 0.2 else 3 if u < 0.7 else 2]
                if night:
                    c = I[4 if u < -0.35 else 3 if u < 0.2 else 2 if u < 0.7 else 1]
                p.px(x, y, c, L)
        p.px(cx, top - rh - 2, RAMP["gold"][4], L)
        p.hline(x0 - 1, x0 + w + 1, top, I[1], L)
        pole_y = top - rh - 2
    else:
        period = 3 if w <= 9 else 4
        for x in range(x0, x0 + w):
            k = (x - x0) % period
            if k != period - 1:
                p.px(x, top, S[6] if k == 0 else S[hi], L)
                p.px(x, top + 1, S[hi] if k == 0 else S[hi - 1], L)
        p.hline(x0, x0 + w, top + 2, S[6], L)
        pole_y = top - 1
    for i, dy in enumerate(slits):
        lit_window(p, cx, base - dy, 3, night, phase + i, L)
    if banner:
        flag(p, cx, pole_y - 7, banner, night, lite, size=5, big=big_flag)
    return top


def wall(p: Pix, x0, x1, base, h, night, merlons=True, L="base"):
    """A curtain wall from x0 to x1 standing on row `base`, `h` tall to the top of its merlons: a face of
    coursed blocks, a lit edge on the left, a dark one on the right, and the merlons along the top."""
    S = stone_ramp(night)
    face = 2 if night else 3
    top = base - h
    for y in range(top + (2 if merlons else 0), base):
        row = base - 1 - y
        for x in range(x0, x1):
            t = face
            if row % 4 == 3 or (x - x0 + (row // 4) * 4) % 9 == 0:
                t = face - 1
            elif (x * 7 + y * 13) % 41 == 0 and p not in THIN:
                t = face + 1
            p.px(x, y, S[t], L)
        p.px(x0, y, S[face + 2], L)
        p.px(x1 - 1, y, S[face - 2], L)
    if merlons:
        for x in range(x0, x1):
            k = (x - x0) % 5
            if k < 3:
                p.px(x, top, S[6] if k == 0 else S[face + 1], L)
                p.px(x, top + 1, S[face + 1] if k == 0 else S[face], L)
        p.hline(x0, x1, top + 2, S[face + 3], L)
    return top


def arch(p: Pix, cx, foot, w, h, night, portcullis=True, drop=0.55, L="base"):
    """A gate: a round-headed opening `w` wide and `h` tall whose foot is row `foot`, dark inside, its
    voussoirs lit; and a portcullis of iron bars lowered `drop` of the way, its points showing."""
    S, I = stone_ramp(night), RAMP["iron"]
    r = w / 2
    x0 = cx - w // 2
    top = foot - h
    cells = set()
    for y in range(top, foot):
        for x in range(x0, x0 + w):
            dy = y + 0.5 - (top + r)
            if dy < 0 and math.hypot(x + 0.5 - (x0 + r), dy) > r + 0.1:
                continue
            cells.add((x, y))
    for (x, y) in cells:
        p.px(x, y, S[0], L)
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                lit_side = dy < 0 or (dx < 0 and y < top + r + 2)
                p.px(q[0], q[1], S[6 if lit_side else 2] if not night else S[5 if lit_side else 1], L)
    if portcullis:
        bottom = top + round(h * drop)
        for x in range(x0 + 1, x0 + w - 1, 3):
            for y in range(top, bottom):
                if (x, y) in cells:
                    p.px(x, y, I[4] if (y - top) % 4 else I[5], L)
            if (x, bottom) in cells:
                p.px(x, bottom, I[3], L)
        for y in range(top + 2, bottom, 4):
            for x in range(x0, x0 + w):
                if (x, y) in cells:
                    p.px(x, y, I[3] if x % 3 else I[4], L)
    return cells


def drawbridge(p: Pix, cx, y, w, night, rows=3, widen=1.0, L="base"):
    """A drawbridge lowered toward the viewer from a gate's foot at row `y`: a deck of oak planks that
    widens by `widen` a side each row as it comes nearer (half that, down a slope). Returns the x of its
    two near corners, for the chains that hold it."""
    W = RAMP["wood"]
    k = -1 if night else 0
    half = w // 2
    for j in range(rows):
        half = w // 2 + int(j * widen)
        for x in range(cx - half, cx + half + 1):
            t = 5 if j == 0 else 4 if j % 2 else 3
            if (x - cx + half) % 3 == 2:
                t -= 2
            p.px(x, y + j, W[max(0, t + k)], L)
    return (cx - half, cx + half)


def chain(p: Pix, x0, y0, x1, y1, night, L="base"):
    """A chain from (x0, y0) to (x1, y1): links drawn a pixel at a time, light and dark by turns."""
    I = RAMP["iron"]
    n = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / max(1, n))
        y = round(y0 + (y1 - y0) * i / max(1, n))
        p.px(x, y, I[5 if i % 2 == 0 else 2] if not night else I[4 if i % 2 == 0 else 1], L)


def moat(p: Pix, x0, x1, y0, y1, night, seed=3, motion=True, L="base"):
    """The moat along the foot of a scene, rows y0 to y1: still water, a paler band where the sky lies on
    it, and ripples that glint by day and shiver by night, twinkling in a moving file."""
    Wt = RAMP["water"]
    rnd = random.Random(seed)
    for y in range(y0, y1):
        for x in range(x0, x1):
            t = (2 if y == y0 else 1) if night else (4 if y == y0 else 3)
            p.px(x, y, Wt[t], L)
    n = max(3, (x1 - x0) // 7)
    for i in range(n):
        x = rnd.randrange(x0 + 1, x1 - 3)
        y = rnd.randrange(y0, y1)
        Lt = p.twinkle(i) if motion else L
        c = Wt[3 if night else 6] if y == y0 else Wt[2 if night else 5]
        p.hline(x, x + rnd.choice((2, 2, 3)), y, c, Lt)


def crag(p: Pix, x0, x1, base, h, night, seed=4, L="base", flat=None):
    """Rock rising from the water from x0 to x1 to `h` above row `base`, grass on its crown and the
    stone shaded from the left, with the top held level between `flat`'s two x where a castle stands."""
    E, G = RAMP["earth"], RAMP["grass"]
    rnd = random.Random(seed)
    k = -1 if night else 0
    mid, half = (x0 + x1) / 2, (x1 - x0) / 2
    for x in range(x0, x1):
        t = (x + 0.5 - mid) / half
        hh = h * max(0.0, 1 - t * t) ** 0.6
        if flat and flat[0] <= x < flat[1]:
            hh = h
        hh = max(1, round(hh + rnd.uniform(-0.6, 0.6)))
        top = base - hh
        for y in range(top, base):
            if y == top:
                c = G[4 + k] if (x % 3) else G[3 + k]
            elif y == top + 1 and hh > 3:
                c = G[2 + k]
            else:
                depth = (y - top) / max(1, hh)
                c = E[max(0, (4 if t < -0.2 else 3 if t < 0.5 else 2) + k - (1 if depth > 0.7 else 0))]
                if (x * 5 + y * 3) % 19 == 0 and p not in THIN:
                    c = E[max(0, 1 + k)]
            p.px(x, y, c, L)


def contact(p: Pix, cx, y, rx):
    """The shadow a thing standing on the rock leaves right under it: only the stone takes it."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.6, X["shade_ink"], (0.2, 0.34), L="pool", only=STONE, shape=False)


# --------------------------------------------------------------------------- the castle and the gatehouse
def castle(p: Pix, x0, g, night, motion=True, lite=False, phase=0, room=76):
    """The castle on its crag above the moat, from x0 across about 58 pixels, the water's surface at row g:
    a curtain wall between two corner towers, its gatehouse of two drum towers round a portcullised gate,
    the drawbridge down the slope to the water on its chains, and behind the wall the keep with its twin
    turrets under slate roofs. It is built to the `room` of rows free of words above the water: with 74
    rows or more the keep rises toward the garland with banners on every tower; with fewer the keep and
    its turrets are lower and the turrets' banners furled, under 39 rows the corner towers' too, under 30
    the keep is left out, and under 26 nothing is built. By night the windows are candlelit, torches burn
    beside the gate, and their light lies on the stone and shivers on the moat."""
    if room < 26:
        return None
    moat(p, x0 - 1, x0 + 59, g - 2, g + 1, night, seed=3, motion=motion)
    crag(p, x0, x0 + 57, g - 2, 8, night, seed=5, flat=(x0 + 4, x0 + 51))
    base = g - 10
    full = room >= 74
    kb = base - 4
    if room >= 30:
        keep_h = 40 if full else max(14, min(36, room - 34))
        turret_h = keep_h + 6 if full else min(keep_h - 2, room - 20)
        tower(p, x0 + 17, kb, 5, turret_h, night, roof=True, banner="gules" if full else None, lite=lite)
        tower(p, x0 + 33, kb, 5, turret_h, night, roof=True, banner="azure" if full else None, lite=lite)
        tower(p, x0 + 25, kb, 17, keep_h, night, banner="gold" if room >= 37 else None,
              slits=tuple(d for d in (12, 24) if d <= keep_h - 4), phase=phase, lite=lite, big_flag=True)
    wall(p, x0 + 4, x0 + 48, base, 13, night)
    corner_h = 32 if room >= 51 else max(16, room - 19)
    corner_slits = (16,) if corner_h >= 24 else (corner_h - 8,)
    for (cx, tincture, dp) in ((x0 + 6, "argent", 1), (x0 + 45, "gules", 2)):
        tower(p, cx, base, 9, corner_h, night, banner=tincture if room >= 39 else None, slits=corner_slits,
              phase=phase + dp, lite=lite)
    drum_h = min(22, room - 10)
    for (cx, dp) in ((x0 + 19, 1), (x0 + 31, 2)):
        tower(p, cx, base, 7, drum_h, night, slits=(11,) if drum_h >= 16 else (), phase=phase + dp, lite=lite)
    arch(p, x0 + 25, base, 7, 9, night, portcullis=True, drop=0.5)
    left, right = drawbridge(p, x0 + 25, base, 7, night, rows=8, widen=0.5)
    chain(p, left, base + 7, x0 + 21, base - 11, night)
    chain(p, right, base + 7, x0 + 29, base - 11, night)
    if night:
        torch(p, x0 + 21, base - 8, phase, side=-1)
        torch(p, x0 + 29, base - 8, phase + 1, side=1)
        glimmer(p, x0 + 21, g, phase)
        glimmer(p, x0 + 29, g, phase + 1)
    return (x0 - 1, x0 + 59)


def guard(p: Pix, x0, g, night, motion=True, lite=False, phase=0, room=76):
    """The castle's defenders on the crag across the water, from x0 over about 56 pixels: a mounted knight
    with lance and pennant riding toward the gate, and behind him a watchtower with a sentry on its
    battlements, a torch burning at its foot by night. Built to the `room` of rows free of words above the
    water: the tower stands as tall as they allow, under 41 rows the sentry comes down, under 34 the knight
    rides off, and under 24 nothing is built."""
    if room < 24:
        return None
    moat(p, x0 - 2, x0 + 56, g - 2, g + 1, night, seed=11, motion=motion)
    crag(p, x0, x0 + 54, g - 2, 6, night, seed=13, flat=(x0 + 3, x0 + 51))
    base = g - 8
    guarded = room >= 41
    h = min(44, room - 21) if guarded else min(44, room - 8)
    top = tower(p, x0 + 46, base, 11, h, night, slits=tuple(d for d in (14, 28) if d <= h - 6), phase=phase,
                lite=lite)
    if guarded:
        sentry(p, x0 + 43, top - 1, night)
    if room >= 34:
        knight(p, x0 + 2, base, night)
    if night:
        torch(p, x0 + 39, base - 10, phase, side=-1, reach=7)
        glimmer(p, x0 + 39, g, phase)
    return (x0 - 2, x0 + 56)


def gatehouse(p: Pix, cx, g, night, motion=True, lite=False, phase=0, room=70):
    """The gatehouse beside a section's title, centred on cx with the water's surface at row g: a gate block
    with a wide portcullised arch between two drum towers, a sentry on the block and the keep's tower
    behind it, the drawbridge down across the moat on its chains, and by night torches on either side of
    the gate. Built to the `room` of rows free of words above the water: with 66 rows or more the towers
    stand full height with their banners; with fewer they are lower, under 42 rows the keep's tower and the
    sentry go, under 40 the banners are furled, and under 20 nothing is built."""
    if room < 20:
        return None
    moat(p, cx - 48, cx + 48, g - 2, g + 1, night, seed=7, motion=motion)
    crag(p, cx - 45, cx + 45, g - 2, 4, night, seed=9, flat=(cx - 40, cx + 40))
    base = g - 5
    banners = room >= 40
    tower_h = min(52, room - 14) if banners else min(52, room - 5)
    wall_h = min(24, room - 5)
    if room >= 42:
        keep_h = min(38, room - 17)
        tower(p, cx - 1, base - 3, 17, keep_h, night, banner="gold", phase=phase, lite=lite, big_flag=True,
              slits=tuple(d for d in (18, 30) if d <= keep_h - 4))
    wall(p, cx - 24, cx + 25, base, wall_h, night)
    if room >= 42:
        sentry(p, cx + 13, base - 24, night)
    for (tx, tincture, dp) in ((cx - 30, "gules", 1), (cx + 30, "azure", 2)):
        tower(p, tx, base, 13, tower_h, night, banner=tincture if banners else None,
              slits=tuple(d for d in (16, 30) if d <= tower_h - 6), phase=phase + dp, lite=lite)
    arch(p, cx, base, 11, min(14, wall_h - 4), night, portcullis=True, drop=0.5)
    left, right = drawbridge(p, cx, base, 11, night, rows=3)
    chain(p, left, base + 2, cx - 9, base - min(15, wall_h - 3), night)
    chain(p, right, base + 2, cx + 9, base - min(15, wall_h - 3), night)
    if night:
        torch(p, cx - 10, base - min(12, wall_h - 2), phase, side=-1)
        torch(p, cx + 10, base - min(12, wall_h - 2), phase + 1, side=1)
        glimmer(p, cx - 10, g, phase)
        glimmer(p, cx + 10, g, phase + 1)
    return (cx - 48, cx + 48)


PHONE_LEAST = 40    # the fewest rows over the water a phone's whole stronghold is built in


def phone_castle(p: Pix, g, night, room):
    """The stronghold across the whole of a phone's H1 under its words, the moat running the width of the phone at
    row g and everything built to the `room` of rows free over it: at the left a watchtower on its rock flying its
    banner, in the middle the castle on its crag with its keep, its towers and their banners and its drawbridge
    down, and at the right the knight riding along the far bank toward it past the guard's tower and its sentry.
    By night the windows are candlelit and the torches burn, their light on the stone and the water. Returns the
    span it covers, or None where fewer than PHONE_LEAST rows are free."""
    if room < PHONE_LEAST:
        return None
    moat(p, 4, p.w - 4, g - 2, g + 1, night, seed=21, motion=False)
    watchtower(p, 22, g, night, motion=False, lite=True, phase=1, w=9, banner="azure", spread=17, room=room)
    castle(p, 46, g, night, motion=False, lite=True, phase=0, room=room)
    guard(p, 116, g, night, motion=False, lite=True, phase=2, room=room)
    return (4, p.w - 4)


GATE_FULL = 66      # the rows over the water the gatehouse stands in at its full height, its banners flying
KEEP_PHONE = 64     # the most rows over the water a phone's great keep stands in, its banner's head in the top one


def phone_gate(p: Pix, g, night, room):
    """The gatehouse under a phone's words, the hero of its H2, across the phone with the moat running its width at
    row g: at the right the gatehouse of a wide H2 at its full height, the keep's tower behind it, the sentry on its
    gate block, the banners flying and the drawbridge down on its chains; and at the left the knight riding along
    the near bank toward its gate. Built to the `room` of rows free over the water, GATE_FULL at the most. By night
    the torches burn either side of the gate and the windows are candlelit, their light on the stone and the
    water. Returns the span it covers."""
    moat(p, 4, p.w - 4, g - 2, g + 1, night, seed=23, motion=False)
    crag(p, 5, 58, g - 2, 5, night, seed=25, flat=(9, 52))
    knight(p, 16, g - 7, night, flip=True)
    gatehouse(p, 122, g, night, motion=False, lite=True, phase=0, room=min(room, GATE_FULL))
    return (4, p.w - 4)


def phone_keep(p: Pix, g, night, room):
    """The great keep under a phone's words, the hero of its H3, across the phone with the moat running its width at
    row g: at the right the great keep of a wide H3, its banner's head in the room's top row, with its curtain
    wall, its gate, its sentry and its drum tower to the left of it; at the left the watchtower on its rock with
    its sentry on its battlements; and between them the knight riding along the near bank toward the keep's gate.
    Built to the `room` of rows free over the water, KEEP_PHONE at the most. By night the torches burn at the
    watchtower's door and either side of the gate, and the slits are candlelit. Returns the span it covers."""
    room = min(room, KEEP_PHONE)
    moat(p, 4, p.w - 4, g - 2, g + 1, night, seed=27, motion=False)
    watchtower(p, 22, g, night, motion=False, lite=True, phase=2, h=34, w=9, guard=True, spread=17, room=room)
    crag(p, 44, 96, g - 2, 5, night, seed=29, flat=(47, 92))
    knight(p, 56, g - 7, night, flip=True)
    great_keep(p, 104, p.w - 4, g, night, motion=False, lite=True, phase=1, room=room, left=room)
    return (4, p.w - 4)


def watchtower(p: Pix, cx, g, night, motion=True, lite=False, phase=0, h=26, w=9, banner="gules", guard=False,
               spread=18, room=None):
    """A lone watchtower on a crag over the water, `h` tall and `w` wide, a banner flying from it (or a sentry
    with his pennant on its battlements, when `guard`) and, by night, a torch at its door. The moat reaches
    `spread` either side. Given the `room` of rows free of words above the water, the tower is built to it:
    it stands as tall as the rows allow, its sentry stands with 32 rows or more and its banner flies with
    30, and under 18 it is not built."""
    if room is not None:
        if room < 18:
            return None
        guard = guard and room >= 32
        banner = banner if room >= 30 else None
        h = min(h, room - 18) if guard else min(h, room - 14) if banner else min(h, room - 6)
    moat(p, cx - spread, cx + spread, g - 2, g + 1, night, seed=11, motion=motion)
    crag(p, cx - spread + 3, cx + spread - 3, g - 2, 4, night, seed=13, flat=(cx - 7, cx + 7))
    base = g - 5
    top = tower(p, cx, base, w, h, night, banner=None if guard else banner, slits=(h - 9,), phase=phase, lite=lite)
    if guard:
        sentry(p, cx - 4, top - 1, night)
    S = stone_ramp(night)
    p.rect(cx - 1, base - 4, 3, 4, S[0])
    p.px(cx, base - 5, S[0])
    if night:
        torch(p, cx + w // 2 + 2, base - 9, phase, side=1, reach=7)
        glimmer(p, cx + w // 2 + 2, g, phase)
    return (cx - spread, cx + spread)


KEEP_W = 19         # the great keep's width
KEEP_LEAST = 30     # the fewest rows over the water the great keep is built in


def great_keep(p: Pix, x0, x1, g, night, motion=True, lite=False, phase=0, room=54, left=None):
    """The great keep of the stronghold, the hero of a strip, from x0 to x1 over the water's surface at row g and
    built to the `room` of rows free over the water, its banner's head in the room's top row: the keep itself at
    the right, a round donjon of dressed stone with its parapet on corbels, a bartizan under a slate cone at each
    corner and the stronghold's great banner flying over it, its slits candlelit by night; and, given `left`, the
    rows free over the water to the keep's left, the curtain wall running from it to a drum tower with its
    pennant, a sentry on the wall-walk, and in the wall the gate, its portcullis half down and its drawbridge
    lowered over the moat on its chains, a torch burning either side of it by night. Returns the span it covers,
    or None where fewer than KEEP_LEAST rows are free."""
    if room < KEEP_LEAST:
        return None
    S = stone_ramp(night)
    moat(p, x0 - 1, x1, g - 2, g + 1, night, seed=17, motion=motion)
    crag(p, x0 + 1, x1 - 1, g - 2, 6, night, seed=19, flat=(x0 + 3, x1 - 3))
    base = g - 8
    k0 = x1 - 3 - KEEP_W
    kcx = k0 + KEEP_W // 2
    top = g - room + 10                  # the keep's merlons, its banner's head nine rows over them
    kh = base - top
    if left and left >= 24:
        wall_h = min(18, left - 12)
        wx0 = x0 + 8
        gx = (wx0 + k0) // 2
        wtop = wall(p, wx0, k0 + 1, base, wall_h, night)
        arch(p, gx, base, 9, min(11, wall_h - 5), night, portcullis=True, drop=0.5)
        left, right = drawbridge(p, gx, base, 9, night, rows=7, widen=0.5)
        chain(p, left, base + 6, gx - 4, base - min(10, wall_h - 6), night)
        chain(p, right, base + 6, gx + 4, base - min(10, wall_h - 6), night)
        dh = min(wall_h + 10, left - 17 if left >= 40 else left - 6)
        tower(p, x0 + 6, base, 9, dh, night, banner="azure" if left >= 40 else None,
              slits=(dh - 8,) if dh >= 16 else (), phase=phase + 2, lite=lite)
        if left >= 36:
            sentry(p, k0 - 11, wtop, night)
        if night:
            for i, side in enumerate((-1, 1)):
                tx = gx + side * 7
                torch(p, tx, base - min(8, wall_h - 4), phase + i, side=side, reach=7)
                glimmer(p, tx, g, phase + i)
    tower(p, kcx, base, KEEP_W, kh, night, banner="gules", big_flag=True, slits=tuple(range(11, kh - 15, 11)),
          phase=phase, lite=lite)
    lo, hi = (1, 4) if night else (2, 5)
    for y in range(top, top + 3):        # the parapet stands proud of the wall on its corbels
        p.px(k0 - 1, y, S[6] if y != top + 1 else S[hi])
        p.px(k0 + KEEP_W, y, S[lo])
    for x in range(k0 - 1, k0 + KEEP_W + 1):
        corbel = (x - k0) % 2 == 0
        p.px(x, top + 3, S[hi] if corbel else S[0])
        if corbel and k0 <= x < k0 + KEEP_W:
            p.px(x, top + 4, S[lo - 1])
    window(p, kcx, top + 8, night, phase + 1)
    for bx in (k0, k0 + KEEP_W - 1):
        tower(p, bx, top + 6, 5, 8, night, roof=True, lite=lite)
    contact(p, kcx, base - 1, KEEP_W / 2 + 1)
    return (x0 - 1, x1)


def window(p: Pix, cx, y, night, phase=0, L="base"):
    """A round-headed window three wide and five tall with its top at row y about cx, a lit sill under it: dark by
    day, and by night candlelit, its heart flickering and its light on the stone round it."""
    S, F = stone_ramp(night), RAMP["flame"]
    cells = [(cx, y)] + [(cx + dx, y + dy) for dy in range(1, 5) for dx in (-1, 0, 1)]
    for (x, yy) in cells:
        p.px(x, yy, S[0] if not night else F[3], L)
    p.hline(cx - 2, cx + 3, y + 5, S[6] if not night else S[4], L)
    if night:
        Lf = p.flicker(phase)
        p.px(cx, y + 2, F[5], Lf)
        p.px(cx, y + 3, F[4], Lf)
        lamp(p, cx + 0.5, y + 2.5, 7, phase, set(cells))


# --------------------------------------------------------------------------- the carved title
def inlay_fill(r, c, scale, night):
    """Gold inlaid in the carved letters by night: a band for each row of the face, bright where the
    torchlight catches the crown of each stroke and across its middle, deeper between."""
    G = RAMP["gold"]
    band = min(6, r // scale)
    return (G[5], G[4], G[3], G[5], G[4], G[3], G[3])[band]


INLAY = Paint("inlay", inlay_fill)


def line(p: Pix, s: str) -> tuple:
    """A line of a title's letters drawn once, as one symbol in the face's own units: placed at the title's
    scale it inks the very pixels its letters would, one by one, in a few bytes a placing instead of a few
    for every letter. Returns its key."""
    s = fold(s, "57")
    key = ("glyph", "57", s) if len(s) == 1 and s != " " else ("line", s)    # one letter: its own glyph
    if key not in p.syms:
        glyphs, _, space = FONTS["57"]
        cells, cx = {}, 0
        for ch in s:
            if ch == " ":
                cx += space + 1
                continue
            g = glyphs[ch]
            for r, cols in enumerate(g[1]):
                for col in cols:
                    cells[(cx + col, r)] = 1
            cx += g[0] + 1
        p.symbol(key, cells, mono=True)
    return key


def unplaced_letters(p: Pix):
    """The glyphs `Pix.text` drew for a title's letters that the title's line now places instead (see `as_line`),
    let go of when nothing else places them: the last of a drawing's last pass."""
    placed = {sid for uses in p.uses.values() for _, sid, _, _, _ in uses}
    for key, sid in list(p.syms.items()):
        if isinstance(key, tuple) and key[0] == "glyph" and sid not in placed:
            p.defs.remove(next(d for d in p.defs if d.startswith(f'<path id="{sid}" ')))
            del p.syms[key]


def as_line(p: Pix, at: int, x, y, s, scale, L="base"):
    """The letters `Pix.text` has just placed on `L` one by one (its uses from `at` on), placed instead as their
    line's one symbol (see `line`) in the same stroke; left as they are unless they share one stroke and size."""
    placed = p.uses[L][at:]
    if not placed or len({(stroke, size) for stroke, _, _, _, size in placed}) != 1:
        return
    stroke = placed[0][0]
    del p.uses[L][at:]
    p.use(line(p, s), x, y, L, stroke=stroke, scale=scale)


def carve(p: Pix, x, y, s, scale, dark, light, L="base", hair=None):
    """The cut of a carved title, drawn before its letters: the letter again half a font pixel up and to
    the left in `dark` (the wall of the cut that turns from the light), the same down and to the right in
    `light` (the wall that catches it), and between the letter and that lit wall a `hair` of gold inlay a
    pixel wide; any of the three is left out when None. Each wall is the line's one symbol, placed once."""
    off = max(1, round(scale / 2))
    lit = off + (1 if hair and off == 1 else 0)      # the lit wall shows beyond the hairline
    key = line(p, s)
    if light:
        p.use(key, x + lit, y + lit, L, stroke=light, scale=scale)
    if hair:
        p.use(key, x + 1, y + 1, L, stroke=hair, scale=scale)
    if dark:
        p.use(key, x - off, y - off, L, stroke=dark, scale=scale)


PASS = 0.16         # the share of the hand's glint period a title's glint takes to pass along it


def glints(p: Pix, x, y, s, scale, night: bool):
    """The title's glint. Once every `glint` seconds of the collection's hand a glint passes along the title's
    gold, the inlay by night and the hairline of gold by day: a sparkle catches the light at the top-left of every
    third letter whose top row has ink, the sparkles shown through a window a quarter of the title wide that
    sweeps along it from its first letter to its last, and then the gold lies still until the glint comes round
    again. The sparkles are written once, and the window is the only thing that moves. The still file keeps the
    night's sparkles where the inlay catches the torchlight, and none of the day's."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    w = max(1, Pix.measure(s, "57", scale))
    q = Pix(p.w, p.h)
    cx = x
    for i, ch in enumerate(s):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        if i % 3 == 1 and g[1][0]:
            sparkle(q, cx + min(g[1][0]) * scale + 1, y + 1, warm=True)
        cx += (g[0] + 1) * scale
    if not q.layers["base"]:
        return
    sparkles = q._paths(q.layers["base"])
    band = w // 4 + 4
    a, b = x - band - 2, x + w + 2
    cid = f"tg{len(p.raws)}"
    moving = (f'<clipPath id="{cid}"><rect y="{y - 2}" width="{band}" height="5"><animateTransform '
              f'attributeName="transform" type="translate" values="{a} 0;{b} 0;{b} 0" keyTimes="0;{num(PASS)};1" '
              f'dur="{num(MEDIEVAL.glint)}s" repeatCount="indefinite"/></rect></clipPath>'
              f'<g clip-path="url(#{cid})">{sparkles}</g>')
    p.raw(10, moving, sparkles if night else "")


# --------------------------------------------------------------------------- heraldry
SHIELD = ["LFFFFFFFD", "LFFFFFFFD", "LFFFFFFFD", "LFFFFFFFD", "LFFFFFFFD", ".LFFFFFD.", ".LFFFFFD.", "..LFFFD..",
          "..LFFFD..", "...LFD...", "....D...."]
SHIELD_SMALL = ["LFFFFFD", "LFFFFFD", "LFFFFFD", ".LFFFD.", ".LFFFD.", "..LFD..", "..LFD..", "...D..."]
# A lion rampant, 12 by 14, facing dexter: one forepaw raised high, the other reaching, a maned head (`m`)
# with its jaws open (`k`), standing on its hind legs, its tail erect and tufted.
LION_RAMPANT = [
    ".#.......#..", "##......##..", "#..mmm..#...", "#.mm##m.#...", "#.m#e#m#....", "##k###mm#...", ".###mm####..",
    "###..######.", "....######..", ".....#####..", ".....##.##..", "....##...##.", "...##.....#.", "...#......#.",
]
# A fleur-de-lis, 9 by 11.
FLEUR = ["....#....", "...###...", "...###...", ".#.###.#.", "##.###.##", "#..###..#", ".#######.", "...###...",
         "..#.#.#..", ".#..#..#.", "#...#...#"]


def lion_rampant(p: Pix, x, y, night=False, L="base"):
    """The lion rampant in gold, top-left at (x, y), lit along the tops of its limbs, a darker mane, a dark
    eye and a red mouth."""
    G, R = RAMP["gold"], RAMP["gules"]
    k = -1 if night else 0
    ink = {(i, j): ch for j, row in enumerate(LION_RAMPANT) for i, ch in enumerate(row) if ch != "."}
    for (i, j), ch in ink.items():
        if ch == "m":
            c = G[3 + k]
        elif ch == "e":
            c = G[1]
        elif ch == "k":
            c = R[4 + k]
        else:
            c = G[5 + k] if (i, j - 1) not in ink else G[4 + k]
        p.px(x + i, y + j, c, L)


def fleur(p: Pix, x, y, night=False, L="base"):
    """A fleur-de-lis in gold, 9 by 11, top-left at (x, y), lit along its upper edges."""
    G = RAMP["gold"]
    k = -1 if night else 0
    ink = {(i, j) for j, row in enumerate(FLEUR) for i, ch in enumerate(row) if ch == "#"}
    for (i, j) in ink:
        p.px(x + i, y + j, G[5 + k] if (i, j - 1) not in ink else G[4 + k], L)


def shield(p: Pix, x, y, tincture="gules", night=False, L="base", charge=None, s=1, small=False):
    """A heater shield, 9 by 11 at `s` 1 (7 by 8 when `small`), in `tincture`: lit down its left edge, shaded
    down its right, a dark outline, and a charge on its field: a `lion` rampant in gold, a `cross` or a
    `chevron`."""
    R = RAMP[tincture]
    k = -1 if night else 0
    pal = {"L": R[min(6, 5 + k)], "F": R[max(0, 3 + k)], "D": R[max(0, 1 + k)]}
    art = SHIELD_SMALL if small else SHIELD
    p.sprite(x, y, art, pal, s, L)
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch != ".":
                for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                    jj, ii = j + dy, i + dx
                    if not (0 <= jj < len(art) and 0 <= ii < len(row) and art[jj][ii] != "."):
                        p.rect(x + ii * s, y + jj * s, s, s, R[0], L)
    G = RAMP["gold"]
    if charge == "lion" and s >= 2:
        lion_rampant(p, x + 3 * (s - 1), y + (s - 2), night, L)
    elif charge == "lion":
        charge = "chevron"
    if charge == "cross":
        for j in range(1, 9):
            p.rect(x + 4 * s, y + j * s, s, s, G[4 + k], L)
        for i in range(2, 7):
            p.rect(x + i * s, y + 3 * s, s, s, G[4 + k], L)
    elif charge == "chevron":
        for i in range(4):
            p.rect(x + (4 - i) * s, y + (3 + i) * s, s, s, G[4 + k], L)
            p.rect(x + (4 + i) * s, y + (3 + i) * s, s, s, G[4 + k], L)


# A mounted knight riding toward the castle, 30 by 27: a horse (`h`, lit `H`, eye `E`, mane `m`, hooves `k`)
# under a caparison gules (`c`) powdered with gold (`C`), the rider in steel (`a`, lit `A`, visor `e`) with a
# plume (`p`), a shield azure (`s`) with a gold charge (`G`), and a lance (`l`) flying a pennant (`F`).
KNIGHT = [
    "...........l..................",
    "...........lFF................",
    "...........lFFFF..............",
    "...........lFFFFF.............",
    "...........lFFF...............",
    "...........l......pp..........",
    "...........l.....pAAp.........",
    "...........l....AAAAa.........",
    "...........l....Aeeaa.........",
    "...........l....aaaaa.........",
    "...hh......l...aAAAaaa........",
    "..hHhhh....l..aaAAaaaa........",
    "..hEhhhh..al..ssssaaa.........",
    "...hhhhhm.al..sGsssaa.........",
    "......hhhmhl..ssssaaa.........",
    ".......hhhmlccsGssccc.........",
    "........hhhccccsscccccc.......",
    "........hhccCccCccCcccch......",
    "........hhcCcCcCcCcCccchh.....",
    "........hhccCccCccCcccchhh....",
    ".........hcccccccccccchhh.....",
    ".........hccccccccccchh.......",
    ".........hhc.cccc.hhh.h.......",
    ".........hh..hh..hh..hh.......",
    "........hh..hh..hh...hh.......",
    "........hh..hh..hh...hh.......",
    "........kk..kk..kk...kk.......",
]
# A sentry on a wall, 9 by 13, facing dexter: helm and plume, a shield on his arm, a spear with a pennant.
SENTRY = [
    "......l..", "......lFF", "......lF.", "..pA..l..", ".AAAa.l..", ".Aeea.l..", ".aaaa.l..", ".aaaaal..",
    "ssaaa.l..", "ssaaa....", ".aaa.....", ".a.a.....", ".k.k.....",
]


def _armour_pal(night: bool) -> dict:
    """The tones a knight's sprite is painted in, a step darker by moonlight."""
    W, A, I, R, G, Az = (RAMP[n] for n in ("wood", "argent", "iron", "gules", "gold", "azure"))
    k = -1 if night else 0
    return {"h": W[2 + k], "H": W[4 + k], "E": I[0], "m": W[1], "k": I[1], "c": R[3 + k], "C": G[4 + k],
            "s": Az[3 + k], "G": G[4 + k], "a": A[4 + k], "A": A[6 + k], "e": I[0], "p": R[4 + k], "l": I[5 + k],
            "F": G[4 + k]}


def knight(p: Pix, x, base, night=False, L="base", flip=False):
    """A mounted knight with his lance raised and its pennant flying, riding toward the gate, his hooves
    on the row above `base`, 30 wide from x: to the left, or to the right when `flip`."""
    p.sprite(x, base - len(KNIGHT), KNIGHT, _armour_pal(night), 1, L, flip=flip)


def sentry(p: Pix, x, base, night=False, L="base"):
    """A sentry standing on a wall-walk, his feet on the row above `base`, 9 wide from x, his spear's
    pennant gules."""
    pal = dict(_armour_pal(night), F=RAMP["gules"][4 + (-1 if night else 0)])
    p.sprite(x, base - len(SENTRY), SENTRY, pal, 1, L)


def swords(p: Pix, cx, cy, half=7, night=False, L="base"):
    """Two swords crossed behind a shield, centred on (cx, cy): blades of steel with a lit edge, gold
    crossguards and dark grips."""
    A, G, I = RAMP["argent"], RAMP["gold"], RAMP["iron"]
    k = -1 if night else 0
    for d in (-1, 1):
        for i in range(-half, half + 1):
            x, y = cx + d * i, cy + i
            p.px(x, y, A[5 + k] if i < 0 else I[2], L)
            if i < 0:
                p.px(x + d, y, A[3 + k], L)
        gx, gy = cx + d * 3, cy + 3
        for j in (-1, 0, 1):
            p.px(gx + j, gy, G[4 + k], L)
            p.px(gx + d * j, gy + j, G[3 + k], L)
        p.px(cx + d * (half + 1), cy + half + 1, G[5 + k], L)


def section_mark(p: Pix, x, y, night, L="base"):
    """A small shield, a chevron on it, over crossed swords, 11 by 10 from (x + 1, y - 1), for the mark after
    SECTION A-A: the swords' tips at the shield's shoulders and their pommels at its foot, so the mark stands
    no taller than the shield and its outline and keeps two rows clear of the title above and the tagline
    below."""
    swords(p, x + 5, y + 3, 4, night, L)
    shield(p, x + 2, y, "gules", night, L, small=True)
    G = RAMP["gold"]
    for (dx, dy) in ((3, 2), (2, 3), (4, 3), (1, 4), (5, 4)):
        p.px(x + 2 + dx, y + dy, G[3 if night else 4], L)


def arms(p: Pix, x, y, night, lion=True, L="base"):
    """A single shield with a lion over crossed swords, about 23 by 25 at twice the shield's size."""
    swords(p, x + 11, y + 1, 10, night, L)
    shield(p, x + 2, y, "gules", night, L, charge="lion" if lion else "cross", s=2)


HELM = ["..#######..", ".#########.", ".#########.", "#####LLL###", "##########.", "###.###.###", ".#########.",
        ".#########.", "..#######..", "...#####..."]


def helm(p: Pix, x, y, plume="gules", night=False, L="base"):
    """A great helm, 11 by 10, top-left at (x, y): steel shaded round from the left, a dark eye slit, breath
    holes, a gold band, and a plume in `plume`'s tincture rising from its crown and bending to the right."""
    A, G, I, R = RAMP["argent"], RAMP["gold"], RAMP["iron"], RAMP[plume]
    k = -1 if night else 0
    for j, row in enumerate(HELM):
        inked = [i for i, ch in enumerate(row) if ch != "."]
        for i in inked:
            ch = row[i]
            if ch == "L":
                c = I[1]
            elif j == 3 and ch == "#":
                c = I[0]
            else:
                u = (i - inked[0]) / max(1, inked[-1] - inked[0])
                c = A[max(0, (5 if u < 0.2 else 4 if u < 0.55 else 3 if u < 0.85 else 1) + k)]
                if j == 0:
                    c = A[min(6, 6 + k)]
            p.px(x + i, y + j, c, L)
    for i in (3, 7):
        p.px(x + i, y + 5, I[1], L)
    for i in range(2, 9):
        p.px(x + i, y + 6, G[3 + k], L)
    for (dx, dy, t) in ((5, -1, 4), (5, -2, 5), (6, -3, 4), (7, -4, 5), (8, -4, 3), (6, -2, 3), (7, -3, 3)):
        p.px(x + dx, y + dy, R[max(0, t + k)], L)


CROWN = ["#.#.#", "#####", "#j###", ".###."]


def crown(p: Pix, x, y, night=False, L="base"):
    """A small gold crown, 5 by 4, a jewel on its band."""
    G = RAMP["gold"]
    k = -1 if night else 0
    p.sprite(x, y, CROWN, {"#": G[4 + k], "j": RAMP["gules"][4]}, 1, L)
    p.px(x, y + 1, G[5 + k], L)
    p.px(x + 4, y + 2, G[2 + k], L)


def heart(p: Pix, x, y, L="base"):
    """A heart gules, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["gules"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)


def iron_ring(p: Pix, x, y, night=False, L="base"):
    """A mooring ring on an iron plate, 9 by 10, top-left at (x, y): the plate riveted at its corners, the
    ring hanging from a staple, lit along its upper left."""
    I = RAMP["iron"]
    k = -1 if night else 0
    for xx in range(x, x + 9):
        p.px(xx, y, I[4 + k], L)
        p.px(xx, y + 1, I[3 + k], L)
        p.px(xx, y + 2, I[2 + k], L)
    for (dx, dy) in ((0, 0), (8, 0), (0, 2), (8, 2)):
        p.px(x + dx, y + dy, I[6 + k] if dy == 0 else I[4 + k], L)
    p.px(x + 4, y + 3, I[2 + k], L)
    for yy in range(y + 4, y + 10):
        for xx in range(x + 1, x + 8):
            d = math.hypot(xx + 0.5 - (x + 4.5), yy + 0.5 - (y + 6.5))
            if 2.1 <= d <= 3.4:
                lit = (xx - x - 4.5) * LX + (yy - y - 6.5) * LY > 0.3
                p.px(xx, yy, I[(5 if lit else 3) + k], L)


def ivy(p: Pix, x0, x1, y, seed=0, night=False, every=(22, 44), L="base"):
    """Ivy that has found the joint along a rule: a sprig every so often, its leaves on the rule and the two
    rows above it (nothing hangs under, where a figure's label may follow), set only where no word lies
    within two units of a leaf."""
    G = RAMP["grass"]
    k = -1 if night else 0
    rnd = random.Random(seed * 71 + x0)
    x = x0 + rnd.randint(2, 9)
    while x < x1 - 3:
        if p.clear_of_words(x - 3, y - 4, x + 4, y + 3):
            p.px(x, y - 1, G[1 + k], L)
            p.px(x - 1, y - 1, G[4 + k], L)
            p.px(x + 1, y - 2, G[3 + k], L)
            p.px(x + 1, y, G[2 + k], L)
            if rnd.random() < 0.6:
                p.px(x, y - 2, G[4 + k], L)
            if rnd.random() < 0.5:
                p.px(x - 1, y, G[3 + k], L)
        x += rnd.randint(*every)


# --------------------------------------------------------------------------- stone and iron for the elements
def courses(p: Pix, x0, y0, w, h, night, L="base", outline=True):
    """A stack of stone blocks `w` by `h` with its top-left at (x0, y0): courses three pixels tall with
    their joints staggered, each block lit along its top and left and shaded along its foot, a dark line
    round the whole."""
    S = stone_ramp(night)
    face = 3 if night else 4
    for y in range(y0, y0 + h):
        row = y - y0
        for x in range(x0, x0 + w):
            c = S[face]
            if row % 3 == 2:
                c = S[face - 2]
            elif (x - x0 + (row // 3) * 2) % 4 == 3:
                c = S[face - 2]
            elif row % 3 == 0:
                c = S[face + 2]
            p.px(x, y, c, L)
    if outline:
        p.box(x0 - 1, y0 - 1, w + 2, h + 2, S[0], L)


def tablet_card(p: Pix, x, y, w, h, night, L="base"):
    """A schematic card as a stone tablet: a dressed slab filling the card right of its icon's cell and the
    iron band beside it, lit along its top and left, shaded along its foot and right, with an iron plate
    riveted over each corner of the card."""
    S, I = stone_ramp(night), RAMP["iron"]
    k = -1 if night else 0
    face, lit, shade = (2, 4, 0) if night else (5, 6, 3)
    for yy in range(y + 1, y + h - 1):
        for xx in range(x + 13, x + w - 1):
            c = S[face]
            if yy == y + 1 or xx == x + 13:
                c = S[lit]
            elif yy == y + h - 2 or xx == x + w - 2:
                c = S[shade]
            p.px(xx, yy, c, L)
    for (px, py) in ((x, y), (x + w - 4, y), (x, y + h - 4), (x + w - 4, y + h - 4)):
        for j in range(4):
            for i in range(4):
                c = I[5 + k] if (i == 0 or j == 0) else I[1] if (i == 3 or j == 3) else I[3 + k]
                p.px(px + i, py + j, c, L)
        p.px(px + 2, py + 2, I[6 + k], L)
        p.px(px + 1, py + 1, I[4 + k], L)


def banner_tails(p: Pix, x, y, w, h, night, tail=5, L="base"):
    """The forked ends of a banner either side of its block from x to x + w, `tail` units long: each lit
    along its top and shaded along its foot like the block, cut to a swallowtail at its end, with a fold in
    shadow where it leaves the block."""
    R = RAMP["gules"]
    mid = (h - 1) / 2
    for j in range(h):
        length = tail - max(0, 3 - int(abs(j - mid)))
        tone = R[4] if j == 0 else R[0] if j == h - 1 else R[2]
        for i in range(length):
            c = R[1] if i == 0 else tone
            p.px(x - 1 - i, y + j, c, L)
            p.px(x + w + i, y + j, c, L)


# Small charges for the chief of a contributor's shield, 7 by 3, by turns: a chevron, a cross, a mullet, a
# fleur-de-lis, a lozenge and a bar.
CHARGES = (["...#...", "..#.#..", ".#...#."], ["...#...", ".#####.", "...#..."], ["...#...", ".#####.", "..#.#.."],
           ["..#.#..", ".#.#.#.", "..###.."], ["...#...", "..###..", "...#..."], [".......", "#######", "......."])


def charge(p: Pix, x, y, i, night=False, L="base"):
    """The `i`-th small charge in gold, top-left at (x, y)."""
    G = RAMP["gold"]
    p.sprite(x, y, CHARGES[i % len(CHARGES)], {"#": G[(4 if night else 5)]}, 1, L)


def rope_over(p: Pix, cells, night, L="base"):
    """A wire redrawn as a rope along its `cells` (x, y, direction): the twist's light and dark strands by
    turns, and its shadow along the row under a level run and the column right of an upright one."""
    W = RAMP["wood"]
    k = -1 if night else 0
    for (x, y, d) in cells:
        twist = ((x + y) // 2) % 2 == 0
        p.px(x, y, W[5 + k] if twist else W[3 + k], L)
        if d == "h":
            p.px(x, y + 1, W[1 + k] if twist else W[2 + k], L)
        else:
            p.px(x + 1, y, W[1 + k] if twist else W[2 + k], L)


CROWN_BIG = ["#..#..#", "##.#.##", "#######", ".#j#j#.", ".#####.", ".#####."]


def crown_big(p: Pix, x, y, night=False, L="base"):
    """A crown 7 by 6, its band set with two jewels, lit along its upper left."""
    G = RAMP["gold"]
    k = -1 if night else 0
    p.sprite(x, y, CROWN_BIG, {"#": G[4 + k], "j": RAMP["gules"][4]}, 1, L)
    for (dx, dy) in ((0, 0), (3, 0), (6, 0), (0, 1), (1, 1), (0, 2), (1, 3)):
        p.px(x + dx, y + dy, G[5 + k], L)
    for (dx, dy) in ((6, 2), (5, 4), (5, 5), (6, 1)):
        p.px(x + dx, y + dy, G[2 + k], L)


def tablet(q: Pix, ox, oy, night):
    """A stone tablet 11 by 15 a numeral is cut into: chamfered corners, a lit top and left, a shaded foot
    and right side, and mortar round it."""
    S = stone_ramp(night)
    face, lit, shade = (2, 4, 0) if night else (5, 6, 3)
    for yy in range(15):
        for xx in range(11):
            if (xx, yy) in ((0, 0), (10, 0), (0, 14), (10, 14)):
                continue
            c = S[face]
            if yy == 0 or xx == 0:
                c = S[lit]
            elif yy == 14 or xx == 10:
                c = S[shade]
            elif yy == 13 or xx == 9:
                c = S[face - 1]
            q.px(ox + xx, oy + yy, c)


def chequy(p: Pix, x0, y0, w, h, period=5, L="base"):
    """A field chequy gules and or, lit along the top and shaded along the foot."""
    R, G = RAMP["gules"], RAMP["gold"]
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
        for xx in range(x0, x0 + w):
            red = ((xx - x0) // period + (yy - y0) // period) % 2 == 0
            p.px(xx, yy, (R[4], R[3], R[1])[band] if red else (G[5], G[4], G[2])[band], L)


def rope_colour(night: bool, seed=0):
    """A colour for each pixel of a rope: the tube's light twisted by a darker strand."""
    W = RAMP["wood"]
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        v = 3 + 2.4 * lam + k
        if int(s * 0.8 + o * 1.4 + seed) % 4 == 0:
            v -= 1.6
        return W[max(0, min(6, round(v)))]
    return colour


def knot(p: Pix, x, y, night=False, L="base"):
    """A knot in the rope at (x, y): a thicker turn, lit on its upper left."""
    W = RAMP["wood"]
    k = -1 if night else 0
    for (dx, dy, t) in ((0, -1, 5), (1, -1, 4), (-1, 0, 4), (0, 0, 4), (1, 0, 3), (2, 0, 3), (0, 1, 3), (1, 1, 2)):
        p.px(x + dx, y + dy, W[max(0, t + k)], L)


def pennant_flag(p: Pix, x, y, tincture, night=False, L="base", kind="major"):
    """A release's flag on a pole standing on the rope at (x, y): a pennant for a release, a square banner
    with a gold charge for a big one, a tower for the repository's founding, and for a release still to
    come a pennant drawn in outline."""
    I, G = RAMP["iron"], RAMP["gold"]
    k = -1 if night else 0
    R = RAMP[tincture]
    if kind == "made":
        S = stone_ramp(night)
        for yy in range(y - 7, y + 1):
            for xx in range(x - 2, x + 3):
                p.px(xx, yy, S[(5 if xx == x - 2 else 4 if xx < x + 2 else 2) + (-1 if night else 0)], L)
        for xx in (x - 2, x, x + 2):
            p.px(xx, y - 8, S[5 + (-1 if night else 0)], L)
        p.px(x, y - 2, S[0], L)
        p.px(x, y - 1, S[0], L)
        return
    p.vline(x, y - 10, y + 1, I[4 + k] if kind != "next" else I[3 + k], L)
    p.px(x, y - 11, G[4 + k], L)
    if kind == "next":
        for (dx, dy) in ((1, -10), (2, -10), (3, -10), (4, -10), (5, -10), (1, -9), (5, -9), (1, -8), (4, -8), (1, -7),
                         (3, -7), (1, -6), (2, -6)):
            p.px(x + dx, y + dy, I[5 + k], L)
        return
    if kind == "big":
        for j in range(5):
            for i in range(1, 8):
                c = R[max(0, (5 if j == 0 else 4 if i < 7 else 3) + k)]
                if i == 4 or j == 2:
                    c = G[4 + k] if tincture != "gold" else RAMP["gules"][4 + k]
                p.px(x + i, y - 10 + j, c, L)
        return
    for j in range(4):
        for i in range(1, 7 - j):
            p.px(x + i, y - 10 + j, R[max(0, (5 if j == 0 else 4 if i < 6 - j else 3) + k)], L)


def wax(p: Pix, cx, cy, r0, r1, night, seed=2):
    """The wax of a seal round its pressed centre, from r0 to r1: a red rim that bulges unevenly where
    the wax ran, lit along its upper left and dark where it turns from the light."""
    R = RAMP["gules"]
    rnd = random.Random(seed)
    bumps = [rnd.uniform(-0.9, 1.1) for _ in range(12)]
    for y in range(math.floor(cy - r1) - 2, math.ceil(cy + r1) + 2):
        for x in range(math.floor(cx - r1) - 2, math.ceil(cx + r1) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            j = int(((th + math.pi) / (2 * math.pi)) * 12) % 12
            f = ((th + math.pi) / (2 * math.pi)) * 12 - j
            edge = r1 - 1.6 + bumps[j] * (1 - f) + bumps[(j + 1) % 12] * f
            if not (r0 - 0.6 <= rho <= edge):
                continue
            facing = (dx * LX + dy * LY) / max(0.1, rho)
            t = 4 if facing > 0.55 else 3 if facing > -0.2 else 2
            if rho > edge - 1.0:
                t = min(5, t + 1) if facing > 0.3 else 1
            elif rho < r0 + 0.6:
                t = 1 if facing > 0 else 2
            p.px(x, y, R[max(0, t - (1 if night else 0))])


def inn_sign(p: Pix, night: bool):
    """A hanging inn sign over the whole canvas: a riveted iron bracket arm along the top, two rings on it
    and the chains the board hangs by, a board of smoothed oak planks with their grain running along them in
    a frame of darker rails, strapped with iron at the corners and nailed."""
    I, W = RAMP["iron"], RAMP["wood"]
    w, h = p.w, p.h
    k = -1 if night else 0
    field, grain, lit = (X["oak_night"], X["oak_night_grain"], X["oak_night_lit"]) if night \
        else (X["oak_day"], X["oak_day_grain"], X["oak_day_lit"])
    rnd = random.Random(5)
    # the bracket arm, three rows of iron with a rivet every twelve pixels, and the rings the chains hang from
    p.hline(0, w, 0, I[5 + k])
    p.hline(0, w, 1, I[3 + k])
    p.hline(0, w, 2, I[1])
    for xx in range(6, w - 6, 12):
        p.px(xx, 1, I[6 + k])
        p.px(xx, 2, I[0])
    for cx in (22, w - 24):
        for (dx, dy) in ((0, 2), (1, 2), (-1, 3), (2, 3), (0, 4), (1, 4)):
            p.px(cx + dx, dy, I[6 + k] if dy < 4 else I[2])
        for yy in range(4, 7):
            p.px(cx, yy, I[5 + k] if yy % 2 == 0 else I[2])
            p.px(cx + 1, yy, I[2] if yy % 2 == 0 else I[5 + k])
    p.rect(1, 7, w - 2, h - 7, field)
    plank = 7
    while plank < h - 4:
        ph = rnd.choice((10, 11, 12))
        end = min(h - 4, plank + ph)
        for yy in range(plank, end):
            if yy == plank and plank > 7:
                p.hline(4, w - 4, yy, W[1] if night else W[3])
            elif yy == plank + 1 and plank > 7:
                p.hline(4, w - 4, yy, lit)
        # the grain: two streaks the length of the plank, wandering a row and breaking now and then
        for streak in (plank + 3 + rnd.randint(0, 2), plank + ph - 4 + rnd.randint(0, 2)):
            yy = streak
            for xx in range(4, w - 4):
                if rnd.random() < 0.06:
                    yy = min(end - 1, max(plank + 2, yy + rnd.choice((-1, 1))))
                if plank + 2 <= yy < end - 1 and rnd.random() > 0.12:
                    p.px(xx, yy, grain)
        plank += ph
    for (kx, ky) in ((48, 33), (161, 58)):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (2, 1)):
            p.px(kx + dx, ky + dy, grain)
        p.px(kx, ky, W[1] if night else W[2])
    rail_face, rail_lit, rail_dark = (W[1], W[2], W[0]) if night else (W[3], W[5], W[1])
    for (rx, ry, rw, rh) in ((1, 7, w - 2, 3), (1, h - 3, w - 2, 3), (1, 7, 3, h - 7), (w - 4, 7, 3, h - 7)):
        p.rect(rx, ry, rw, rh, rail_face)
    p.hline(1, w - 1, 7, rail_lit)
    p.vline(1, 7, h, rail_lit)
    p.hline(1, w - 1, h - 1, rail_dark)
    p.vline(w - 2, 7, h, rail_dark)
    p.hline(1, w - 1, 10, rail_dark)
    p.hline(4, w - 4, h - 4, rail_lit)
    p.vline(4, 10, h - 4, rail_dark)
    p.vline(w - 5, 10, h - 4, rail_lit)
    for (sx, sy, dx, dy) in ((2, 8, 1, 1), (w - 3, 8, -1, 1), (2, h - 2, 1, -1), (w - 3, h - 2, -1, -1)):
        for i in range(7):
            p.px(sx + dx * i, sy, I[3 + k])
            p.px(sx, sy + dy * i, I[3 + k])
        p.px(sx, sy, I[5 + k])
        p.px(sx + dx * 5, sy, I[6 + k])
        p.px(sx, sy + dy * 5, I[6 + k])


# --------------------------------------------------------------------------- a footer: its footing and its banner
# The stronghold's banners hung on a footer's wall, (width, height) with their hooks and tails: the great banner of the
# lion, and where it has no room the banner of the fleur-de-lis.
GONFALON = {"lion": (16, 24), "fleur": (13, 19)}
SCONCE_W = len(SCONCE[0])
FOOT_RISE = 4       # the rows a footer's footing rises by where its cells leave it room: a course of blocks
FOOT_RUN = 24       # the fewest columns it rises along
BLOCK = 12          # a block of the footing's courses


def gonfalon(p: Pix, x, y, night, charge="lion", L="base"):
    """The stronghold's banner hung on the wall from (x, y), as wide and as tall as `GONFALON` has it for its
    `charge`: gules, a lion rampant or (or a fleur-de-lis or), hung from a gilt rod by two cords from an iron hook
    in the wall, its cloth lit down its left edge, shaded down its right and outlined in the red's darkest tone,
    its foot fringed with gold and cut in three tails."""
    R, G, I = RAMP["gules"], RAMP["gold"], RAMP["iron"]
    k = -1 if night else 0
    GONFALON_W, GONFALON_H = GONFALON[charge]
    cx = x + GONFALON_W // 2
    p.px(cx, y, I[5 + k], L)
    p.px(cx - 1, y, I[2 + k], L)
    for i in range(1, 4):
        p.px(cx - 1 - 2 * i, y + i, G[4 + k], L)
        p.px(cx - 2 * i, y + i, G[3 + k], L)
        p.px(cx + 2 * i - 1, y + i, G[3 + k], L)
        p.px(cx + 2 * i, y + i, G[2 + k], L)
    rod = y + 4
    p.hline(x, x + GONFALON_W, rod, G[4 + k], L)
    p.px(x, rod, G[5 + k], L)
    p.px(x + GONFALON_W - 1, rod, G[2 + k], L)
    top, foot = rod + 1, y + GONFALON_H - 3
    for yy in range(top, foot):
        for xx in range(x + 1, x + GONFALON_W - 1):
            u = xx - x - 1
            c = R[4 + k] if u == 0 else R[1 + k] if u == GONFALON_W - 3 else R[2 + k] if u >= GONFALON_W - 5 \
                else R[3 + k]
            p.px(xx, yy, R[2 + k] if yy == top else c, L)
        p.px(x, yy, R[0], L)
        p.px(x + GONFALON_W - 1, yy, R[0], L)
    for i in range(1, GONFALON_W - 1):
        p.px(x + i, foot - 1, G[4 + k] if i % 2 else G[2 + k], L)
    tail = (GONFALON_W - 2) // 3
    for t in range(3):
        tx = x + 1 + (GONFALON_W - 2 - tail * 3 + 1) // 2 * (t > 0) + tail * t
        for j, (a, b) in enumerate(((0, tail - 1), (1, tail - 2), (1, tail - 2))):
            for xx in range(tx + a, tx + b):
                p.px(xx, foot + j, R[0] if j == 2 else R[3 + k] if xx > tx + a else R[4 + k], L)
    if charge == "lion":
        lion_rampant(p, x + 2, top + 1, night, L)
    else:
        fleur(p, x + 2, top + 1, night, L)


def footing(p: Pix, night: bool, rule: str, after=0):
    """A footer once its words are set: the footing of the wall along its foot, a lit ledge over a course of
    rusticated blocks, as deep as the plinth the frame lays there or, where the lowest word comes down nearer the
    foot, as shallow as keeps a row clear of it, the frame's moulding carried down the sides to meet it; rising by
    a course wherever the cells leave it room along FOOT_RUN columns or more, the ruled lines between the cells
    standing on it; and the rightmost place from column `after` on where the cells leave the wall free, the
    stronghold's banner hung on the wall (see `gonfalon`), the lion's where it has the room and the fleur-de-lis's
    where it has less, a torch in its bracket either side of it where there is room, burning by night."""
    w, h = p.w, p.h
    S = stone_ramp(night)
    base = p.layers["base"]
    ledge = min(h - 2, max(h - 5, max((b[3] for b in p.words), default=0) + 1))
    plinth = {S[1], S[2], S[4], S[6]}           # the frame's plinth, which the footing takes the place of
    for y in range(h - 5, ledge):
        for x in range(w):
            if base.get((x, y)) in plinth:
                del base[(x, y)]
        for x0 in (0, w - 4):
            for k in range(4):
                billet = y % 8 in (6, 7)
                p.px(x0 + k, y, S[1] if k == 3 or (billet and k) else S[3] if k == 0 and billet else
                     S[6] if k == 0 else S[4] if k == 1 else S[3])

    def free(x0, y0, x1, y1):
        """Whether the box from (x0, y0) to (x1, y1) lies on the bare wall, nothing solid drawn on it, two units from
        every word."""
        return 5 <= x0 and x1 <= w - 5 and 5 <= y0 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0 - 1, x1 + 1) for y in range(y0, y1))
    mark = None
    for charge, torches in (("lion", True), ("lion", False), ("fleur", True), ("fleur", False)):
        bw, bh = GONFALON[charge]
        mw = bw + (2 * (SCONCE_W + 2) if torches else 0)
        top = ledge - 1 - bh
        mark = next(((x, top, mw, torches, charge) for x in range(w - 6 - mw, max(4, after), -1)
                     if free(x, top, x + mw, ledge)), None)
        if mark:
            break
    taken = (mark[0] - 2, mark[0] + mark[2] + 2) if mark else (0, 0)
    rise = [x not in range(*taken) and free(x, ledge - FOOT_RISE - 1, x + 1, ledge) for x in range(w)]
    tops = [ledge] * w
    x = 5
    while x < w - 5:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - 5) if not rise[i]), w - 5)
        if b - x >= FOOT_RUN:
            tops[x:b] = [ledge - FOOT_RISE] * (b - x)
        x = b
    for x in range(w):
        t = tops[x]
        if p.clear_of_words(x - 1, t - 2, x + 2, t + 1):
            p.apx(x, t - 1, X["shade_ink"], 0.22, "base")
        for y in range(t, h):
            course = 0 if y >= ledge else 1
            row = (y - t) if course else (y - ledge)
            joint = (x + 6 * course) % BLOCK == 0
            if y == h - 1:
                c = S[1]
            elif row == 0:
                c = S[6]
            elif joint:
                c = S[2]
            elif (x + 6 * course) % BLOCK == 1:
                c = S[5]
            else:
                c = S[4] if row == 1 else S[3]
            if course and y == ledge - 1:
                c = S[2]
            p.px(x, y, c)
        if t < ledge and (tops[x - 1] == ledge or tops[min(w - 1, x + 1)] == ledge):
            for y in range(t, ledge):
                p.px(x, y, S[5] if tops[x - 1] == ledge else S[1])
    if mark:
        x, top, mw, torches, charge = mark
        bx = x + (SCONCE_W + 2 if torches else 0)
        gonfalon(p, bx, top, night, charge)
        if torches:
            for i, sx in enumerate((x, x + mw - SCONCE_W)):
                sconce(p, sx, top + GONFALON[charge][1] // 2 - 3, night, phase=i)


# --------------------------------------------------------------------------- icons
# Heraldic charges for the link buttons, 9 by 7, bold enough to read at the kit's size and lit from the
# upper left like everything else: a tower and crossed swords argent, a crown and a fleur-de-lis or. Tones:
# a A argent, g G gold, r red, i I iron, # the button's ink.
ICONS = {
    "tower": ["a.a.a.a.a", "aAAAAAAAa", ".aAAAAAA.", ".aAAiAAA.", ".aAAiAAA.", ".aAAAAAA.", "aAAAiAAAa"],
    "crown": ["g...g...g", "gG..G..Gg", "gGG.G.GGg", "gGGGGGGGg", ".gGrGrGg.", ".gGGGGGg.", ".ggggggg."],
    "fleur": ["....g....", "...gGg...", ".g.gGg.g.", "gG.gGg.Gg", ".gGGGGGg.", "...gGg...", ".gg.g.gg."],
    "swords": ["a.......a", ".a.....a.", "..a...a..", "...a.a...", "....a....", "...g.g...", "..I...I.."],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a button by day or by night."""
    A, G, I = RAMP["argent"], RAMP["gold"], RAMP["iron"]
    k = -1 if night else 0
    return {"a": A[6 + k], "A": A[4 + k], "g": G[5 + k], "G": G[3 + k], "r": RAMP["gules"][4], "i": I[1], "I": I[3 + k],
            "#": ink}
