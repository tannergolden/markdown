# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Christmas set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the snow that falls in it, the frame, the
lights, the snow that rests on every ledge, the scenery a header stands on, and every sprite, each shaded
from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ..pixel import LX, LY, LZ, Pix, cylinder, sphere, tube
from .palette import BULBS, C, NIGHT_SKY, RAMP, SNOW, X, ramp_for


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: icy paper with a dot grid by day, by night a winter sky that
    lightens toward the horizon in five bands."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["ice"]}"/>')
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
    arm = C["gold4"] if warm else (X["glint"] if night else SNOW[False]["glint"])
    p.px(x, y, C["white"], L)
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
            p.px(x, y, rnd.choice((C["white"], C["gold4"], X["star_blue"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.3)


FALL = (("far", 0.62, 0.22, -10), ("near", 0.38, 0.11, 20))   # each depth's share of the flakes, s a step, z


def fall(p: Pix, x0, y0, x1, y1, n, night, seed=11, name="snow", avoid=(), near=True):
    """Snow falling in a clipped window, at two depths: small slow flakes behind the drawing and fewer,
    brighter, quicker ones in front (left out when `near` is false). Each depth is drawn once and shown
    again a window higher, and the pair steps down a pixel at a time, so the drop loops without a seam.
    The still file keeps the far flakes where they lie, those clear of the boxes in `avoid`, and leaves
    the near ones out, so none sits on a letter."""
    period = y1 - y0
    rnd = random.Random(seed)
    for depth, share, speed, z in FALL if near else FALL[:1]:
        q = Pix(p.w, p.h)
        for _ in range(round(n * share)):
            x, y = rnd.randrange(x0 + 1, x1 - 1), rnd.randrange(y0, y1)
            if depth == "far":
                q.px(x, y, SNOW[True]["shade"] if night else X["flake_far_day"])
            elif rnd.random() < 0.3:
                col = C["white"] if night else X["frost_blue"]
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    q.px(x + dx, y + dy, col if (dx, dy) == (0, 0) else col + ":0.55")
            else:
                q.px(x, y, C["white"] if night else X["frost_blue"])
        cid, gid = f"{name}{depth}c", f"{name}{depth}g"
        clip = f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{period}"/></clipPath>'
        steps = ";".join(f"0 {i}" for i in range(period))
        moving = (f'{clip}<g clip-path="url(#{cid})"><g><g id="{gid}">{_markup(q)}</g>'
                  f'<use href="#{gid}" y="-{period}"/>'
                  f'<animateTransform attributeName="transform" type="translate" values="{steps}" '
                  f'dur="{period * speed:.2f}s" repeatCount="indefinite" calcMode="discrete"/></g></g>')
        still = f'{clip}<g clip-path="url(#{cid})">{_markup(q, avoid)}</g>' if depth == "far" else ""
        p.raw(z, moving, still)


def _markup(q: Pix, avoid=()) -> str:
    """A scratch drawing's pixels as paths, its see-through ones over its solid ones, leaving out any in
    a box in `avoid`."""
    def clear(xy):
        return not any(a <= xy[0] < c and b <= xy[1] < d for a, b, c, d in avoid)
    return "".join(q._paths({xy: c for xy, c in q.layers.get(name, {}).items() if clear(xy)})
                   for name in ("base", "base+"))


def candy_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="cane"):
    """The sheet's border: a candy-cane rod two pixels thick, lit along its top-left face, and a pine
    rule inside. The stripes are two six-pixel pattern tiles, one lit and one in shade, so the
    border costs a few hundred bytes however long it runs."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    R = RAMP["red"]
    tiles = {"L": (R[4], C["white"]), "D": (R[2], X["frost_hi"])}
    rows = {}
    for j in range(6):
        for i in range(6):
            if ((i + j) // 3) % 2 == 0:
                rows.setdefault(j, []).append(i)
    for name, (red, white) in tiles.items():
        p.defs.append(f'<pattern id="{uid}{name}" width="6" height="6" patternUnits="userSpaceOnUse">'
                      f'<rect width="6" height="6" fill="{white}"/><path stroke="{red}" d="{Pix._d(rows)}"/></pattern>')
    bands = [(x, y, w, 1, "L"), (x + 1, y + 1, w - 2, 1, "D"), (x, y + h - 1, w, 1, "D"),
             (x + 1, y + h - 2, w - 2, 1, "L"), (x, y + 1, 1, h - 2, "L"), (x + 1, y + 2, 1, h - 4, "D"),
             (x + w - 1, y + 1, 1, h - 2, "D"), (x + w - 2, y + 2, 1, h - 4, "L")]
    for (bx, by, bw, bh, name) in bands:
        p.shapes["base"].append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#{uid}{name})"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, C["pine4"] if night else C["pine2"])


def snowcap(p: Pix, x0, x1, y, seed=7, L="base", night=False, icicles=0.0, glints=0.0, reach=3, cap=3):
    """Snow resting on a ledge whose top edge is row `y`: drifts one to three pixels deep with rounded
    ends, white where the light lands, blue underneath and at the far end of each drift. `icicles` is
    the chance of one hanging from the ledge at each spot, `glints` the number per 100 pixels that
    twinkle above the drifts, each where no word is near."""
    T = SNOW[night]
    rnd = random.Random(seed * 131 + x0)
    cols = {}
    x = x0
    while x < x1:
        run = rnd.randint(5, 16)
        hgt = min(cap, rnd.choice((1, 2, 2, 2, 3)))
        e = min(x + run, x1)
        for xx in range(x, e):
            k = min(xx - x, e - 1 - xx)
            cols[xx] = max(1, min(hgt, 1 + k))
        x = e + rnd.choice((0, 0, 1, 2, 4))
    for xx, hh in cols.items():
        right_end = cols.get(xx + 1, 0) < hh
        for i in range(hh):
            c = T["top"] if i == 0 else T["body"]
            if right_end and i > 0:
                c = T["shade"]
            p.px(xx, y - hh + i, c, L)
        p.px(xx, y, T["shade"] if cols.get(xx - 1, 0) and cols.get(xx + 1, 0) else T["deep"], L)
    if glints:
        spots = sorted(cols)
        for _ in range(int(len(spots) * glints / 100)):
            xx = rnd.choice(spots)
            gy = y - cols[xx] - 2
            phase = rnd.randrange(3)
            if p.clear_of_words(xx - 3, gy - 3, xx + 4, gy + 4):
                sparkle(p, xx, gy, big=False, L=p.twinkle(phase), night=night)
    if icicles:
        xx = x0 + rnd.randint(1, 6)
        while xx < x1 - 1:
            if rnd.random() < icicles:
                ln = min(reach, rnd.choice((1, 2, 2, 3, 4)))
                for i in range(ln):
                    p.px(xx, y + 1 + i, T["ice"][min(2, i * 3 // max(1, ln))], L)
                if ln >= 3:
                    p.px(xx - 1, y + 1, T["ice"][1], L)
            xx += rnd.randint(3, 10)


def snowbank(p: Pix, x0, x1, y_top, y_bot, seed=5, L="base", night=False):
    """A drift across the foot of a drawing: rolling snow, lit on its crest, blue in its hollows."""
    T = SNOW[night]
    rnd = random.Random(seed)
    h = rnd.randint(2, 4)
    prev = h
    for x in range(x0, x1):
        h = max(1, min(y_bot - y_top, h + rnd.choice((-1, 0, 0, 0, 1))))
        top = y_bot - h
        for yy in range(top, y_bot):
            c = T["top"] if yy == top else T["body"]
            if yy == top and h < prev:
                c = T["shade"]
            if yy >= y_bot - 1:
                c = T["shade"]
            p.px(x, yy, c, L)
        prev = h


# --------------------------------------------------------------------------- light that falls on the snow
def light_pool(p: Pix, cx, y, rx, ry, night):
    """Warm light from a lit tree, pooled on the snow around its foot: only snow pixels take it."""
    T = SNOW[night]
    snow = {T["top"], T["body"], T["shade"], T["deep"], C["white"]}
    if night:
        p.halo(cx, y, rx, ry, C["gold3"], (0.1, 0.18, 0.27, 0.36), L="pool", only=snow)
    else:
        p.halo(cx, y, rx, ry, C["gold3"], (0.05, 0.09), L="pool", only=snow)


def ground_shadow(p: Pix, x0, x1, y, night):
    """A soft shadow on the snow to the lower right of something standing on it, by day."""
    T = SNOW[night]
    snow = {T["top"], T["body"], T["shade"], C["white"]}
    p.halo((x0 + x1) / 2, y, (x1 - x0) / 2, 2.2, RAMP["snow"][0], (0.16, 0.26), L="pool", only=snow)


# --------------------------------------------------------------------------- lights
BULB_GLASS = [(0, 0, 4), (1, 0, 5), (2, 0, 3), (0, 1, 4), (1, 1, 6), (2, 1, 3), (0, 2, 3), (1, 2, 4), (2, 2, 2),
              (1, 3, 2)]


def glow_cells(cx, cy, rx, ry, col, alphas, skip=()):
    """A small stepped glow as see-through pixels around (cx, cy), leaving out the pixels in `skip`."""
    out, n = {}, len(alphas)
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d < 1 and (x, y) not in skip:
                out[(x, y)] = f"{col}:{alphas[min(n - 1, int((1 - d) * n))]:g}"
    return out


def bulb(p: Pix, x, y, col, L="base", night=False, glow=True):
    """A C9 bulb in a dark socket at (x+1, y): glass lit from inside, hot at the core, and a glow
    that blinks with it. The glass and its glow are drawn once per colour and placed with <use>."""
    R = ramp_for(col)
    p.px(x + 1, y, RAMP["coal"][3])
    p.px(x + 1, y + 1, RAMP["coal"][1])
    key = ("bulb", col, night, glow)
    if key not in p.syms:
        glass = {(dx, dy): R[t] for dx, dy, t in BULB_GLASS}
        cells = glow_cells(1.5, 1.0, 3.6, 4.1, R[4], (0.16, 0.3) if night else (0.08, 0.15), glass) if glow else {}
        cells.update(glass)
        p.symbol(key, cells)
    p.use(key, x, y + 2, L)


def lights(p: Pix, x0, x1, y, sag=4, span=38, spacing=9, night=False, seed=0):
    """A string of lights: a sagging pine-green wire between hooks, bulbs hanging from it in turn, each
    on a twinkle layer with a glow that blinks with it."""
    wire, hi_ = (RAMP["pine"][3], RAMP["pine"][5]) if night else (RAMP["pine"][1], RAMP["pine"][3])
    pts = []
    x = x0
    while x < x1:
        seg_end = min(x + span, x1)
        for xx in range(x, seg_end):
            t = (xx - x) / max(1, seg_end - x)
            pts.append((xx, y + round(sag * 4 * t * (1 - t))))
        x = seg_end
    for i, (xx, yy) in enumerate(pts):
        p.px(xx, yy, hi_ if i % 7 == 3 else wire)
    for (a, b) in zip(pts, pts[1:]):
        if abs(a[1] - b[1]) > 1:
            for yy in range(min(a[1], b[1]), max(a[1], b[1])):
                p.px(a[0], yy, wire)
    i = 0
    for k, (xx, yy) in enumerate(pts):
        if k % spacing == spacing // 2:
            bulb(p, xx - 1, yy + 1, BULBS[(i + seed) % len(BULBS)], p.twinkle(i + seed), night)
            i += 1


def light(p: Pix, x, y, col, L, night=False, big=True):
    """One light on a tree: a hot two-by-two point (one pixel on a small tree) and its glow."""
    R = ramp_for(col)
    key = ("light", col, night, big)
    if key not in p.syms:
        core = {(0, 0): R[6], (1, 0): R[4], (0, 1): R[4], (1, 1): R[3]} if big else {(0, 0): R[5]}
        cells = glow_cells(1.0 if big else 0.5, 1.0 if big else 0.5, 2.6, 2.6, R[4],
                           (0.2, 0.36) if night else (0.1, 0.18), core)
        cells.update(core)
        p.symbol(key, cells)
    p.use(key, x, y, L)


def wire_bulb(p: Pix, x, y, d, col, night):
    """A bulb hanging from a wire at (x, y), under it on a level wire (`d` 'h') and to its left on an
    upright one: its socket, its glass and its glow, drawn once for each colour and way."""
    R = ramp_for(col)
    key = ("wirebulb", col, d, night)
    if key not in p.syms:
        if d == "h":
            glass = {(-1, 2): R[4], (0, 2): R[6], (1, 2): R[3], (-1, 3): R[3], (0, 3): R[4], (1, 3): R[2], (0, 4): R[2]}
            socket, centre = (0, 1), (0.5, 3.5)
        else:
            glass = {(-2, -1): R[4], (-3, -1): R[3], (-2, 0): R[6], (-3, 0): R[4], (-4, 0): R[2], (-2, 1): R[3],
                     (-3, 1): R[2]}
            socket, centre = (-1, 0), (-2.5, 0.5)
        cells = glow_cells(centre[0], centre[1], 3.2, 3.2, R[4], (0.16, 0.3) if night else (0.08, 0.15), glass)
        cells.update(glass)
        cells[socket] = RAMP["coal"][2]
        p.symbol(key, cells)
    p.use(key, x, y)


# --------------------------------------------------------------------------- stars and the moon
def _star_mask(r):
    if r <= 2:
        return ["..#..", ".###.", "#####", ".###.", ".#.#."]
    if r == 3:
        return ["...#...", "..###..", "#######", ".#####.", "..###..", ".##.##.", ".#...#."]
    pts = []
    for i in range(10):
        a = math.radians(-90 + 36 * i)
        rr = r + 0.5 if i % 2 == 0 else (r + 0.5) * 0.47
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    size = 2 * r + 1
    rows = []
    for j in range(size):
        row = ""
        for i in range(size):
            px_, py_ = i - r, j - r + 0.35
            inside = False
            for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
                if (ay > py_) != (by > py_) and px_ < (bx - ax) * (py_ - ay) / (by - ay) + ax:
                    inside = not inside
            row += "#" if inside else "."
        rows.append(row)
    return rows


def star(p: Pix, cx, cy, r, L="base", ramp=None, outline=None, glow=None, rays=None):
    """A five-point star centred on (cx, cy): each arm split down its ridge into a lit face and a
    shaded one, brightest at the heart. `glow` is a halo colour, `rays` a twinkle phase for its rays."""
    G = ramp or RAMP["gold"]
    mask = _star_mask(r)
    h_ = len(mask)
    w_ = len(mask[0])
    ox, oy = cx - w_ // 2, cy - h_ // 2
    if glow:
        p.halo(cx + 0.5, cy + 0.5, r * 2.6 + 1, r * 2.6 + 1, glow, (0.05, 0.1, 0.17, 0.26))
    cells = {}
    for j, row in enumerate(mask):
        for i, ch in enumerate(row):
            if ch != "#":
                continue
            dx, dy = i + 0.5 - w_ / 2, j + 0.5 - h_ / 2
            if abs(dx) < 1 and abs(dy) < 1:
                cells[(ox + i, oy + j)] = 6
                continue
            ang = math.degrees(math.atan2(dy, dx))
            k = round((ang + 90) / 72)
            axis = -90 + 72 * k
            side = 1 if ((ang - axis + 180) % 360 - 180) > 0 else -1
            phi = math.radians(axis + side * 90)
            lam = max(0.0, 0.62 * (math.cos(phi) * LX + math.sin(phi) * LY) + 0.78 * LZ)
            cells[(ox + i, oy + j)] = max(2, min(5, round(1.6 + 4.2 * lam)))
    for (x, y), t in cells.items():
        p.px(x, y, G[t], L)
    if outline:
        for (x, y) in list(cells):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in cells:
                    p.px(x + dx, y + dy, outline, L)
    if rays is not None:
        R = p.twinkle(rays)
        for d in range(1, 3):
            a = f"{C['gold4']}:{0.8 if d == 1 else 0.45}"
            for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(cx + sx * (r + d), cy + sy * (r + d), a, R)
    return cells


def moon(p: Pix, cx, cy, r, L="base", night=True):
    """A crescent moon: its lit limb shaded as a sphere, a crater or two, and by night earthshine on
    the dark part and a halo stepped out into the sky."""
    M = RAMP["moon"]
    ox, oy, rr = cx + r * 0.62, cy - r * 0.3, r * 0.9

    def lit(xx, yy):
        return math.hypot(xx + 0.5 - ox, yy + 0.5 - oy) > rr

    if night:
        p.halo(cx, cy, r * 2.6, r * 2.6, C["gold4"], (0.03, 0.05, 0.08, 0.12))
        for yy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for xx in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) <= r and not lit(xx, yy):
                    p.px(xx, yy, X["earthshine"], L)
    sphere(p, cx, cy, r, M, L, lo=2, hi=6, rim=False, outline=not night, only=lit)
    for (dx, dy) in ((-0.55, 0.05), (-0.3, 0.55)):
        qx, qy = math.floor(cx + dx * r), math.floor(cy + dy * r)
        if lit(qx, qy):
            p.px(qx, qy, M[3], L)
            p.px(qx + 1, qy, M[4], L)


# --------------------------------------------------------------------------- the tree
BAUBLE7 = ["..454..", ".45543.", "4565433", "4554332", "3443322", ".33222.", "..232.."]
BAUBLE3 = [".5.", "463", ".2."]


def tree(p: Pix, cx, base, height, night=False, seed=4, lights_on=True, snow=True, garland=None):
    """A layered fir with its trunk on row `base`: tiers that overlap from the top down, each with
    drooping tips, needles drawn as strokes that point down and out, the shadow each tier casts on
    the one below, snow on the tips, a garland, baubles, glowing lights and a faceted star."""
    rnd = random.Random(seed)
    P = RAMP["pine"]
    T = SNOW[night]
    top = base - height
    sr = 5 if height >= 60 else (4 if height >= 40 else (3 if height >= 28 else 2))
    trunk_h = max(2, height // 11)
    trunk_w = max(3, (height // 10) | 1)
    apex = top + sr + (1 if sr >= 3 else 2)
    canopy_bot = base - trunk_h
    H = canopy_bot - apex
    tiers = 3 if height < 36 else (4 if height < 70 else 5)
    W = max(4, round(height * 0.36))
    tip_sp = 4 if height >= 40 else 3
    owner, tone, tips_at = {}, {}, []
    for k in range(tiers - 1, -1, -1):
        yb = apex + round(H * (k + 1) / tiers) - 2
        yt = apex if k == 0 else apex + round(H * k / tiers) - round(H / tiers * 0.5)
        b = W * (k + 1.3) / (tiers + 0.3)
        a = 0.4 if k == 0 else b * 0.4
        rows = yb - yt + 1
        for y in range(yt, yb + 1):
            t = (y - yt) / max(1, rows - 1)
            hw = a + (b - a) * t ** 0.85
            if (y - yt) % 3 == 1 and 0.12 < t < 0.92 and hw > 3:
                hw -= 0.9
            hwi = int(hw + 0.5)
            for x in range(cx - hwi, cx + hwi + 1):
                rel = (x - cx) / max(1.0, hw)
                owner[(x, y)] = k
                tone[(x, y)] = 1.2 + 2.9 * (0.5 - 0.5 * rel) + 1.0 * t
        bi = int(b + 0.5)
        n_t = max(1, (2 * bi) // tip_sp)
        for j in range(n_t + 1):
            x = cx - bi + round(j * 2 * bi / n_t)
            tips_at.append((x, yb, k))
            for d, dd in ((0, 2), (-1, 1), (1, 1)):
                xx = x + d
                if abs(xx - cx) > bi:
                    continue
                for jj in range(1, dd + 1):
                    owner[(xx, yb + jj)] = k
                    tone[(xx, yb + jj)] = tone.get((xx, yb), 2.5) - 0.35 * jj
        for side in (-1, 1):
            xx = cx + side * (bi + 1)
            for jj in (0, 1):
                owner[(xx, yb + jj)] = k
                tone[(xx, yb + jj)] = (3.4 if side < 0 else 1.2) - 0.5 * jj
    # the shadow each tier throws on the one below, and the needles
    for (x, y), k in owner.items():
        v = tone[(x, y)]
        up1, up2 = owner.get((x, y - 1)), owner.get((x, y - 2))
        up3 = owner.get((x, y - 3))
        if up1 is not None and up1 < k:
            v -= 1.9
        elif up2 is not None and up2 < k:
            v -= 1.1
        elif up3 is not None and up3 < k:
            v -= 0.45
        m = ((x + y) if x < cx else (x - y)) % 4
        v += {0: 0.6, 1: 0.1, 2: -0.5, 3: 0.0}[m]
        tone[(x, y)] = v
    edge = {q for q in owner
            if any((q[0] + dx, q[1] + dy) not in owner for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    for (x, y) in owner:
        if (x, y) in edge:
            lit_side = (x - 1, y) not in owner or (x, y - 1) not in owner
            if lit_side and x < cx:
                c = X["moonlit_pine"] if night else P[2]
            elif lit_side:
                c = P[1]
            else:
                c = P[0]
        else:
            c = P[max(1, min(5, round(tone[(x, y)])))]
        p.px(x, y, c)
    # snow on alternate tips
    if snow:
        for i, (x, yb, k) in enumerate(tips_at):
            if i % 2 or (x, yb - 1) not in owner:
                continue
            for dx in (-1, 0, 1):
                if (x + dx, yb) in owner and (x + dx, yb) not in edge or dx == 0:
                    p.px(x + dx, yb - 1, T["top"])
                    p.px(x + dx, yb, T["shade"] if dx == 1 else T["body"])
    # the trunk, shaded under the boughs
    tx0 = cx - trunk_w // 2
    cylinder(p, [(yy, tx0, tx0 + trunk_w - 1) for yy in range(canopy_bot, base)], RAMP["wood"], lo=2, hi=4)
    for xx in range(tx0, tx0 + trunk_w):
        p.px(xx, canopy_bot, RAMP["wood"][1])
    # a garland of gold beads swooping across the tiers
    inside = [q for q in owner if q not in edge]
    if garland is None:
        garland = height >= 60
    if garland:
        for k in range(1, tiers):
            ys = [y for (x, y), kk in owner.items() if kk == k]
            y0, y1 = min(ys), max(ys)
            ya, yb_ = y0 + (y1 - y0) * 0.45, y0 + (y1 - y0) * 0.8
            row_a = sorted(x for (x, y) in owner if y == round(ya) and owner[(x, y)] == k)
            if len(row_a) < 6:
                continue
            xa, xb = row_a[0] + 1, row_a[-1] + 2
            for x in range(xa, xb):
                t = (x - xa) / max(1, xb - xa)
                y = round(ya + (yb_ - ya) * t + 2.2 * math.sin(math.pi * t))
                if (x, y) in owner and (x, y) not in edge:
                    lit = t < 0.55
                    c = RAMP["gold"][5 if lit else 3] if x % 2 == 0 else RAMP["gold"][3 if lit else 2]
                    p.px(x, y, c)
    # baubles and lights on a jittered grid
    spots = []
    step_y = 6 if height >= 40 else 4
    for y in range(apex + 5, canopy_bot - 1, step_y):
        row = sorted(x for (x, yy) in inside if yy == y)
        if len(row) < 4:
            continue
        off = (y // step_y) % 2 * 3
        for x in range(row[0] + 1 + off, row[-1], 7 if height >= 40 else 5):
            q = (x + rnd.randint(-1, 1), y + rnd.randint(-1, 1))
            if q in owner and q not in edge and (q[0], q[1] + 1) in owner:
                spots.append(q)
    rnd.shuffle(spots)
    orn = [RAMP["red"], RAMP["gold"], RAMP["silver"], RAMP["cyan"], RAMP["pink"]]
    for i, (x, y) in enumerate(spots):
        if lights_on and i % 5 in (0, 2, 4):
            light(p, x, y, BULBS[i % len(BULBS)], p.twinkle(i), night, big=height >= 40)
        else:
            Rm = orn[i % len(orn)]
            if height >= 40:
                p.px(x + 1, y - 1, RAMP["gold"][4])
                p.sprite(x, y, BAUBLE3, {str(t): Rm[t] for t in range(7)})
            else:
                p.px(x, y, Rm[5])
                p.px(x + 1, y, Rm[4])
                p.px(x, y + 1, Rm[3])
                p.px(x + 1, y + 1, Rm[2])
    # the star, and its light
    star(p, cx, top + sr, sr, ramp=RAMP["gold"], outline=None if night else RAMP["gold"][2],
         glow=C["gold3"] if night else None, rays=1 if height >= 22 else None)
    if night:
        p.halo(cx + 0.5, apex + H * 0.55, W * 1.25, H * 0.66, C["gold3"], (0.02, 0.035, 0.055))
    return dict(apex=apex, W=W, H=H, bottom=base)


# --------------------------------------------------------------------------- presents and ornaments
BOWS = {
    "s": [".45.54.", "4453544", ".3.2.3."],
    "m": [".45...54.", "455424554", "344363443", ".33.3.33."],
    "l": ["..45...54..", ".4554.4554.", "45443534454", "34432623443", ".333.3.333.", "....3.3...."],
}


def bow(p: Pix, x, y, size, ramp, L="base"):
    """A ribbon's bow, top-left at (x, y): two loops lit from the upper left and the tails between them."""
    p.sprite(x, y, BOWS[size], {str(i): ramp[i] for i in range(7)}, 1, L)


def gift(p: Pix, x, y, w, h, box, ribbon, lid=True, with_bow=True):
    """A wrapped box lit from the upper left, `box` and `ribbon` the names of its ramps: a lid that
    overhangs and throws a shadow, a ribbon over the lid and down the front, and a bow on top."""
    B, Rb = RAMP[box], RAMP[ribbon]
    lid_h = 2 if (lid and h >= 6) else (1 if lid else 0)
    rx = x + w // 2 - (1 if w >= 8 else 0)
    rw = 2 if w >= 8 else 1
    for yy in range(y + lid_h, y + h):
        for xx in range(x, x + w):
            t = (xx - x) / max(1, w - 1)
            c = 4 if t < 0.2 else (3 if t < 0.7 else 2)
            if xx == x + w - 1 or yy == y + h - 1:
                c = 1
            if yy == y + lid_h and lid:
                c = min(c, 1)
            if rx <= xx < rx + rw:
                cr = (5 if xx == rx else 4) if yy != y + lid_h or not lid else 2
                if yy == y + h - 1:
                    cr = 2
                p.px(xx, yy, Rb[cr])
            else:
                p.px(xx, yy, B[c])
    if h >= 9:
        hy = y + lid_h + (h - lid_h) // 2
        for xx in range(x, x + w):
            if not rx <= xx < rx + rw:
                p.px(xx, hy, Rb[4 if xx < x + w * 0.6 else 3])
                p.px(xx, hy + 1, Rb[2])
    if lid:
        for yy in range(y, y + lid_h):
            for xx in range(x - 1, x + w + 1):
                c = 5 if yy == y else 4
                if xx == x + w:
                    c = 2
                elif xx == x - 1:
                    c = 4
                if rx <= xx < rx + rw:
                    p.px(xx, yy, Rb[6 if (yy == y and xx == rx) else 5 if yy == y else 4])
                else:
                    p.px(xx, yy, B[c])
    if with_bow:
        size = "s" if w < 10 else ("m" if w < 16 else "l")
        bw, bh = len(BOWS[size][0]), len(BOWS[size])
        bow(p, rx + (rw - bw) // 2 + (1 if rw == 2 and bw % 2 else 0), y - bh + 1, size, Rb)


def ornament(p: Pix, x, y, ramp, L="base", big=False):
    """A glass bauble on the ramp named `ramp`: a gold cap and loop at (x+3, y), the ball below it lit
    from the upper left. `big` is a bauble two pixels wider, for the release a milestones sheet marks
    as big."""
    R, G = RAMP[ramp], RAMP["gold"]
    p.px(x + 3, y, G[2], L)
    p.px(x + 2, y + 1, G[5], L)
    p.px(x + 3, y + 1, G[4], L)
    p.px(x + 4, y + 1, G[2], L)
    if big:
        sphere(p, x + 3.5, y + 6.5, 4.6, R, L, lo=1, outline=False)
    else:
        p.sprite(x, y + 2, BAUBLE7, {str(t): R[t] for t in range(7)}, 1, L)


def candy(p: Pix, x, y, h=16, flip=False):
    """A candy cane `h` tall: a round stick with a hook, striped on the diagonal, lit from the upper left."""
    rad = 1.6 if h >= 14 else 1.1
    hook = 3.0 if h >= 14 else 2.2
    lx = x + rad + 0.3
    hc = lx + hook
    top = y + rad + 0.3
    path = [(lx, y + h - rad)]
    path.append((lx, top + hook))
    for i in range(1, 25):
        a = math.pi + math.pi * i / 24
        path.append((hc + hook * math.cos(a), top + hook + hook * math.sin(a)))
    path.append((hc + hook, top + hook + 2.2))
    if flip:
        mid = x + (hook * 2 + rad * 2 + 0.6) / 2
        path = [(2 * mid - px_, py_) for (px_, py_) in path]
    red, white = RAMP["red"], RAMP["snow"]

    def colour(s_, o, lam, xx, yy):
        stripe = int((s_ + o * 1.4 * (-1 if flip else 1)) / 2.4) % 2
        v = lam * 4.2
        if stripe == 0:
            return red[max(2, min(5, round(1.6 + v)))]
        return white[max(2, min(6, round(2.4 + v)))]

    tube(p, path, rad + 0.35, colour, outline=RAMP["red"][1] if h >= 14 else None)


def candy_bar(p: Pix, x0, y0, w, h, period=5):
    """A striped candy stick lying flat: red and white bands, lit along the top, shaded along the bottom."""
    R = RAMP["red"]
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
        for xx in range(x0, x0 + w):
            red = ((xx - x0 + (yy - y0)) // period) % 2 == 0
            p.px(xx, yy, (R[5], R[3], R[1])[band] if red else (C["white"], RAMP["snow"][4], RAMP["snow"][2])[band])


def needles(seed=0, lo=1, hi=5):
    """A colour for each pixel of a pine rope: the tube's light, broken up into needles."""
    rnd = random.Random(seed)
    P = RAMP["pine"]

    def colour(s, o, lam, x, y):
        v = lo + 0.3 + (hi - lo) * lam + rnd.uniform(-0.8, 0.8) + (0.45 if (x + 2 * y) % 5 == 0 else 0)
        return P[max(lo, min(hi, round(v)))]
    return colour


# --------------------------------------------------------------------------- the snowman
def snowman(p: Pix, x, y, night=False, scarf="red"):
    """A snowman 21 wide and 30 tall, top-left at (x, y): three lit snowballs, a top hat with a band and
    a sprig, coal eyes, a carrot, a knitted scarf with a fringed tail, and twig arms."""
    T = SNOW[True]
    S = [T["line"], T["deep"], T["shade"], T["body"], T["top"], RAMP["snow"][5], C["white"]] if night else RAMP["snow"]
    K, W_, O = RAMP["coal"], RAMP["wood"], RAMP["carrot"]
    Rs = RAMP[scarf]
    cx = x + 10.5
    # arms first, so the body overlaps their roots
    for (ax, ay), (bx, by) in (((x + 6, y + 16), (x + 1, y + 11)), ((x + 15, y + 16), (x + 20, y + 12))):
        n = max(abs(bx - ax), abs(by - ay))
        for i in range(n + 1):
            px_ = round(ax + (bx - ax) * i / n)
            py_ = round(ay + (by - ay) * i / n)
            p.px(px_, py_, W_[2])
            p.px(px_, py_ + 1, W_[1])
    p.px(x + 2, y + 10, W_[2])
    p.px(x + 0, y + 12, W_[2])
    p.px(x + 19, y + 10, W_[2])
    p.px(x + 20, y + 13, W_[2])
    body = dict(lo=2, hi=6, rim=True)
    sphere(p, cx, y + 23.5, 6.4, S, **body)
    sphere(p, cx, y + 15.5, 4.9, S, **body)
    sphere(p, cx, y + 8.6, 3.7, S, **body)
    # the hat: a crown lit on the left, a red band, a brim
    for yy in range(y, y + 4):
        for xx in range(x + 7, x + 14):
            t = xx - (x + 7)
            p.px(xx, yy, K[4] if t == 0 else K[3] if t == 1 else K[2] if t < 5 else K[1])
    for xx in range(x + 7, x + 14):
        p.px(xx, y + 3, Rs[4] if xx < x + 10 else Rs[3] if xx < x + 13 else Rs[2])
    p.px(x + 12, y + 2, RAMP["pine"][4])
    p.px(x + 12, y + 3, RAMP["red"][5])
    for xx in range(x + 5, x + 16):
        p.px(xx, y + 4, K[3] if xx < x + 9 else K[2] if xx < x + 14 else K[1])
    p.px(x + 7, y, K[5])
    # the face
    p.px(x + 9, y + 7, K[0])
    p.px(x + 12, y + 7, K[0])
    p.px(x + 9, y + 6, K[3] if not night else K[4])
    p.px(x + 11, y + 8, O[4])
    p.px(x + 12, y + 8, O[3])
    p.px(x + 13, y + 8, O[2])
    p.px(x + 12, y + 9, O[1])
    for xx, yy in ((x + 8, y + 10), (x + 9, y + 11), (x + 11, y + 11), (x + 12, y + 10)):
        p.px(xx, yy, K[1])
    # the scarf: a wrap at the neck and a tail with a fringe
    for xx in range(x + 6, x + 16):
        t = (xx - (x + 6)) / 9
        p.px(xx, y + 12, Rs[5] if t < 0.3 else Rs[4] if t < 0.7 else Rs[3])
        p.px(xx, y + 13, Rs[3] if t < 0.7 else Rs[2])
    for yy in range(y + 14, y + 19):
        p.px(x + 7, yy, Rs[4])
        p.px(x + 8, yy, Rs[3])
        p.px(x + 9, yy, Rs[2])
        if (yy - y) % 2 == 0:
            p.px(x + 7, yy, Rs[5])
    for xx, c in ((x + 7, Rs[5]), (x + 9, Rs[5])):
        p.px(xx, y + 19, c)
    for yy in (y + 15, y + 18, y + 22, y + 25):
        p.px(round(cx), yy, K[1])
        p.px(round(cx) - 1, yy, K[3] if yy < y + 20 else None)


# --------------------------------------------------------------------------- holly, and small things
def leaf(p: Pix, sx, sy, tx, ty, half, ramp, L="base", spines=3):
    """A holly leaf from its stem (sx, sy) to its tip (tx, ty): a spined margin with hollows between
    the spines, a pale midrib, the half that turns to the light a tone brighter, a dark outline."""
    ln = math.hypot(tx - sx, ty - sy)
    ux, uy = (tx - sx) / ln, (ty - sy) / ln
    nx, ny = -uy, ux
    lit_side = 1 if (nx * LX + ny * LY) > 0 else -1
    cells = {}
    for y in range(math.floor(min(sy, ty) - half) - 1, math.ceil(max(sy, ty) + half) + 2):
        for x in range(math.floor(min(sx, tx) - half) - 1, math.ceil(max(sx, tx) + half) + 2):
            rx, ry = x + 0.5 - sx, y + 0.5 - sy
            u = (rx * ux + ry * uy) / ln
            v = rx * nx + ry * ny
            if not 0 <= u <= 1.02:
                continue
            hw = half * math.sin(math.pi * min(1.0, u * 0.94 + 0.03)) ** 0.7
            hw -= 0.42 * half * math.sin(math.pi * spines * u) ** 2
            if abs(v) > hw:
                continue
            if abs(v) < 0.55 and 0.12 < u < 0.9:
                t = 5
            else:
                t = 4 if (v * lit_side > 0) else 2
                if u > 0.72 and t == 2:
                    t = 3
            cells[(x, y)] = t
    for (x, y), t in cells.items():
        p.px(x, y, ramp[t], L)
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                p.px(q[0], q[1], ramp[0], L)
    return cells


def berry(p: Pix, x, y, L="base"):
    """A holly berry, three by three: a glint, a lit face and a dark underside."""
    Rr = RAMP["red"]
    p.sprite(x, y, [".4.", "463", ".2."], {str(i): Rr[i] for i in range(7)}, 1, L)
    for (dx, dy) in ((-1, 1), (3, 1), (1, 3), (0, 2), (2, 2), (0, 0), (2, 0), (1, -1)):
        p.px(x + dx, y + dy, Rr[1], L)


def holly(p: Pix, x, y, L="base"):
    """A sprig of holly about 16 by 10: two spined leaves splayed from the stem and three berries."""
    P = RAMP["pine"]
    leaf(p, x + 7.5, y + 7.0, x + 0.6, y + 2.2, 2.6, P, L)
    leaf(p, x + 8.5, y + 7.0, x + 15.4, y + 2.2, 2.6, P, L)
    berry(p, x + 5, y + 6, L)
    berry(p, x + 9, y + 6, L)
    berry(p, x + 7, y + 3, L)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["red"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)


def santa_hat(p: Pix, x, y, L="base"):
    """A Santa hat, 13 by 11, leaning to the right: red felt lit on its left, a pompom at the tip and a fur brim."""
    Rr = RAMP["red"]
    S = RAMP["snow"]
    art = ["..........WW.",
           ".........WWWs",
           ".......23.ss.",
           "......2542...",
           ".....25441...",
           "....254431...",
           "...2544431...",
           "..25544321...",
           ".2554443211..",
           "WWWWWWWWWWWW.",
           "vWWvWWvWWvWu."]
    pal = {"1": Rr[1], "2": Rr[2], "3": Rr[3], "4": Rr[4], "5": Rr[5],
           "W": S[6], "w": S[5], "v": S[4], "s": S[3], "u": S[2]}
    p.sprite(x, y, art, pal, 1, L)


# --------------------------------------------------------------------------- snow on letters
def snow_on_letters(night: bool):
    """A title's finish (see `Pix.text`): snow settled along the top edge of every stroke, a pixel deep
    and now and then two, the far end of each drift shaded blue on a big title."""
    shade = SNOW[night]["shade"]

    def finish(p: Pix, cells, scale, L, rnd, y0):
        tops = {(gx, gy) for (gx, gy) in cells if (gx, gy - 1) not in cells}
        for (gx, gy) in sorted(tops):
            left_end, right_end = (gx - 1, gy) not in tops, (gx + 1, gy) not in tops
            p.px(gx, gy, C["white"], L)
            if not (left_end or right_end) or rnd.random() < 0.45:
                p.px(gx, gy - 1, C["white"], L)
            if scale >= 3 and not (left_end or right_end) and rnd.random() < 0.16:
                p.px(gx, gy - 2, C["white"], L)
            if scale >= 3 and right_end:
                p.px(gx, gy + 1, shade, L)
    return finish


# --------------------------------------------------------------------------- icons
# 7x7 icons for the link buttons and a bot's avatar. Tones: y Y z gold, g G h pine, r R q red, w W snow,
# b wood, # ink. Lit from the upper left like everything else.
ICONS = {
    "tree": ["...y...", "..gGh..", ".gGrGh.", "..gGh..", ".gyGGh.", "gGGGrGh", "...b..."],
    "star": ["...y...", "..yyY..", "yyyyYYz", ".yyYYz.", "..yYz..", ".yY.Yz.", ".y...z."],
    "gift": [".rR.Rq.", "...R...", "gggyggG", "hhhzhhh", "gGGyGGh", "yyyyYYz", "gGGYGhh"],
    "bell": ["...z...", "..yYz..", ".yyYYz.", ".yyYYz.", ".yYYYz.", "yyyYYYz", "...q..."],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on paper by day, or on the night sky."""
    G, P, R = RAMP["gold"], RAMP["pine"], RAMP["red"]
    return {"y": G[5] if night else G[4], "Y": G[4] if night else G[3], "z": G[3] if night else G[2],
            "g": P[5] if night else P[4], "G": P[4] if night else P[3], "h": P[3] if night else P[1],
            "r": R[5] if night else R[4], "R": R[4] if night else R[3], "q": R[3] if night else R[1],
            "w": C["white"] if night else X["frost_blue"], "W": X["glint"] if night else X["icon_shade_day"],
            "b": RAMP["wood"][4] if night else RAMP["wood"][2], "#": ink}
