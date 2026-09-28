# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Halloween set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the frame, the scenery a header stands on,
and every sprite, each shaded from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ..pixel import LX, LY, LZ, Pix
from .palette import BULBS, C, GROUND, NIGHT_SKY, RAMP, X, ramp_for


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: fog-lilac paper with a dot grid by day, by night a sky that
    lightens toward the horizon in five bands of purple."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["fog"]}"/>')
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
    arm = RAMP["flame"][5] if warm else (X["star_pale"] if night else RAMP["ghost"][3])
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
            p.px(x, y, rnd.choice((C["white"], RAMP["flame"][5], X["star_pale"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.3)


def web(p: Pix, x, y, r=9, flip=False, night=False, L="base"):
    """A cobweb across a corner at (x, y): four threads fanning out from the corner and three rounds of
    spiral strung between them, each strand sagging toward the corner, all of them one clean pixel
    wide. Drawn once, placed with <use>."""
    key = ("web", r, flip, night)
    if key not in p.syms:
        col = X["web_night"] if night else X["web_day"]
        cells: dict = {}
        ends = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (5, 45, 85)]
        for (ex, ey) in ends:
            _line(cells, 0.5, 0.5, ex + 0.5, ey + 0.5)
        for f in (0.5, 0.95):
            for (ax, ay), (bx, by) in zip(ends, ends[1:]):
                pts = []
                for i in range(6):
                    t = i / 5
                    qx, qy = (ax + (bx - ax) * t) * f, (ay + (by - ay) * t) * f
                    d = math.hypot(qx, qy) or 1.0
                    k = (d - 1.6 * f * math.sin(math.pi * t)) / d
                    pts.append((qx * k + 0.5, qy * k + 0.5))
                for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                    _line(cells, x0, y0, x1, y1)
        _pixel_perfect(cells)
        out = {(-q[0] if flip else q[0], q[1]): col for q in cells}
        p.symbol(key, out)
    p.use(key, x, y, L)


def stocking_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="rod", webs=False):
    """The sheet's border: a rod striped like a witch's stockings, orange and black, two pixels thick
    and lit along its top-left face, and a purple rule inside. The stripes are two six-pixel pattern
    tiles, one lit and one in shade, so the border costs a few hundred bytes however long it runs.
    `webs` strings a cobweb across each top corner."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    P, K = RAMP["pumpkin"], RAMP["coal"]
    tiles = {"L": (P[5], K[3]), "D": (P[3], K[1])}
    rows = {}
    for j in range(6):
        for i in range(6):
            if ((i + j) // 3) % 2 == 0:
                rows.setdefault(j, []).append(i)
    for name, (orange, black) in tiles.items():
        p.defs.append(f'<pattern id="{uid}{name}" width="6" height="6" patternUnits="userSpaceOnUse">'
                      f'<rect width="6" height="6" fill="{black}"/><path stroke="{orange}" d="{Pix._d(rows)}"/></pattern>')
    bands = [(x, y, w, 1, "L"), (x + 1, y + 1, w - 2, 1, "D"), (x, y + h - 1, w, 1, "D"), (x + 1, y + h - 2, w - 2, 1, "L"),
             (x, y + 1, 1, h - 2, "L"), (x + 1, y + 2, 1, h - 4, "D"), (x + w - 1, y + 1, 1, h - 2, "D"),
             (x + w - 2, y + 2, 1, h - 4, "L")]
    for (bx, by, bw, bh, name) in bands:
        p.shapes["base"].append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#{uid}{name})"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, C["lilac"] if night else C["violet"])
    if webs:
        web(p, x + 4, y + 4, 9, False, night, "haze")
        web(p, x + w - 5, y + 4, 9, True, night, "haze")


def ooze(p: Pix, x0, x1, y, seed=7, L="base", drips=0.0, reach=2, cap=2, glints=0.0):
    """Slime lying on a ledge whose top edge is row `y`: patches one or two pixels deep with rounded
    ends, lit along the top and darker where each patch ends. `drips` is the chance of one hanging
    from the ledge at each spot, never longer than `reach`; `glints` is how many catch the light per 100 px."""
    S = RAMP["slime"]
    rnd = random.Random(seed * 131 + x0)
    cols = {}
    x = x0 + rnd.randint(0, 3)
    while x < x1:
        run = rnd.randint(4, 13)
        hgt = min(cap, rnd.choice((1, 1, 2, 2, 2)))
        e = min(x + run, x1)
        for xx in range(x, e):
            k = min(xx - x, e - 1 - xx)
            cols[xx] = max(1, min(hgt, 1 + k))
        x = e + rnd.choice((1, 2, 3, 4, 6, 9))
    for xx, hh in cols.items():
        right_end = cols.get(xx + 1, 0) < hh
        for i in range(hh):
            p.px(xx, y - hh + i, S[5] if i == 0 else (S[3] if right_end else S[4]), L)
        p.px(xx, y, S[3] if (cols.get(xx - 1, 0) and cols.get(xx + 1, 0)) else S[2], L)
    if glints:
        spots = sorted(cols)
        for _ in range(int(len(spots) * glints / 100)):
            xx = rnd.choice(spots)
            p.px(xx, y - cols[xx], S[6], L)
    if drips:
        last = -9
        for xx in sorted(cols):
            if not (cols.get(xx - 1) and cols.get(xx + 1)) or xx - last < 3 or rnd.random() >= drips:
                continue
            last = xx
            ln = min(reach, rnd.choice((1, 1, 2, 2, 3, 4)))
            for i in range(1, ln + 1):
                p.px(xx, y + i, S[4] if i < ln else S[3], L)
            if ln >= 2:
                p.px(xx, y + ln - 1, S[5], L)


def fog(p: Pix, x0, x1, y0, y1, night, seed=3, n=None, motion=True, name="fog", speed=0.34):
    """Fog lying along the ground between x0 and x1: soft banks of see-through pixels, denser where
    they overlap, that drift slowly to the right and wrap round, so the loop never shows a seam."""
    period = x1 - x0
    rnd = random.Random(seed)
    col = X["fog_night"] if night else X["fog_day"]
    anim = None
    if motion:
        cid = f"{name}c"
        p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{period}" height="{y1 - y0}"/></clipPath>')
        anim = ("drift", x0, y0, x1, y1, period, cid, speed)
    L = p.layer(name, anim, z=14)
    for _ in range(n or max(4, period // 6)):
        cx = rnd.randrange(x0, x1)
        w = rnd.randint(12, 26)
        by = rnd.randrange(y1 - 3, y1)
        for r, (cut, a) in enumerate(((0, 0.3), (6, 0.24), (12, 0.18))):
            ww = w - cut
            if ww < 3 or by - r < y0:
                break
            for xx in range(cx - ww // 2, cx + ww - ww // 2):
                p.apx(x0 + (xx - x0) % period, by - r, col, a, L)


BULB_GLASS = [(0, 0, 4), (1, 0, 5), (2, 0, 3), (0, 1, 4), (1, 1, 6), (2, 1, 3), (0, 2, 3), (1, 2, 4), (2, 2, 2), (1, 3, 2)]


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
    """A glass bulb in a dark socket at (x+1, y): lit from inside, hot at the core, and a glow that
    blinks with it. The glass and its glow are drawn once per colour and placed with <use>."""
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


# A jack-o'-lantern small enough to hang on a string: ramp tones, `h` the stem, `f` the carved face.
MINI_JACK = ["...h...", ".45432.", "45f4f21", "4544321", "34fff21", ".23321."]


def mini_lantern(p: Pix, x, y, night=False, phase=0, L="base"):
    """A little jack-o'-lantern, 7 by 6, its stem at (x+3, y): the rind shaded from the upper left,
    the face lit from inside and flickering, with a glow that flickers with it."""
    P, F = RAMP["pumpkin"], RAMP["flame"]
    kb = ("minijack", night)
    if kb not in p.syms:
        cells = {}
        for j, row in enumerate(MINI_JACK):
            for i, ch in enumerate(row):
                if ch == "h":
                    cells[(i, j)] = RAMP["slime"][0 if night else 1]
                elif ch == "f":
                    cells[(i, j)] = P[0]
                elif ch.isdigit():
                    d = int(ch)
                    near = any(MINI_JACK[jj][ii] == "f" for jj in range(max(0, j - 1), min(len(MINI_JACK), j + 2))
                               for ii in range(max(0, i - 1), min(7, i + 2)))
                    cells[(i, j)] = P[max(1, d - 1) if night and not near else d]
        p.symbol(kb, cells)
    kf = ("minijackface", night)
    if kf not in p.syms:
        body = {(i, j) for j, row in enumerate(MINI_JACK) for i, ch in enumerate(row) if ch != "."}
        cells = glow_cells(3.5, 3.4, 5.4, 4.8, P[4], (0.14, 0.26) if night else (0.05, 0.1), body)
        for j, row in enumerate(MINI_JACK):
            for i, ch in enumerate(row):
                if ch == "f":
                    cells[(i, j)] = F[5] if j == 2 else (F[6] if i == 3 else F[4])
        p.symbol(kf, cells)
    p.use(kb, x, y, L)
    p.use(kf, x, y, p.flicker(phase))


def lanterns(p: Pix, x0, x1, y, sag=4, span=38, spacing=10, night=False, seed=0):
    """A string of lanterns: a sagging black wire between hooks, and hanging from it by turns a little
    jack-o'-lantern that flickers and a glass bulb, purple or green, that twinkles."""
    K = RAMP["coal"]
    wire, hi_ = (K[4], K[6]) if night else (K[2], K[4])
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
        if k % spacing == spacing // 2 and 4 <= xx - x0 and x1 - xx >= 4:
            if (i + seed) % 2 == 0:
                mini_lantern(p, xx - 3, yy + 1, night, i + seed)
            else:
                bulb(p, xx - 1, yy + 1, BULBS[1 + (i // 2 + seed) % 2], p.twinkle(i + seed), night)
            i += 1


def mound(p: Pix, x0, x1, y_top, y_bot, seed=5, night=False, L="base"):
    """Graveyard earth heaped along the foot of a drawing: a rolling crest with blades of dead grass,
    the soil darker toward the rule it rests on."""
    E, S = RAMP["earth"], RAMP["slime"]
    rnd = random.Random(seed)
    h = rnd.randint(2, 3)
    prev = h
    for x in range(x0, x1):
        h = max(1, min(y_bot - y_top, h + rnd.choice((-1, 0, 0, 0, 1))))
        top = y_bot - h
        for yy in range(top, y_bot):
            c = E[4] if yy == top else (E[3] if yy < y_bot - 1 else E[2])
            if yy == top and h < prev:
                c = E[3]
            p.px(x, yy, c, L)
        prev = h
        if rnd.random() < 0.28:
            p.px(x, top - 1, S[1] if night else S[2], L)
            if rnd.random() < 0.4:
                p.px(x, top - 2, S[2] if night else S[3], L)


def light_pool(p: Pix, cx, y, rx, ry, night):
    """A lantern's light pooled on the earth around its foot: only the soil takes it."""
    if night:
        p.halo(cx, y, rx, ry, RAMP["pumpkin"][4], (0.1, 0.18, 0.27, 0.36), L="pool", only=GROUND)
    else:
        p.halo(cx, y, rx, ry, RAMP["pumpkin"][4], (0.05, 0.09), L="pool", only=GROUND)


def moon(p: Pix, cx, cy, r, L="base", night=True, halo=True):
    """A full moon: a pale disc lit almost face on, a little brighter toward the upper left and a little
    darker at its limb. Its grey seas are soft-edged and its craters are dark with a lit lower rim. By
    night a halo steps out into the sky; by day it hangs pale in the afternoon, outlined."""
    M = RAMP["moon"]
    if night and halo:
        p.halo(cx, cy, r * 2.5, r * 2.5, M[5], (0.03, 0.05, 0.08, 0.12))
    cells = {}
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            lam = 0.55 * nz + 0.45 * max(0.0, dx * LX + dy * LY + nz * LZ)
            cells[(x, y)] = 3.1 + 3.0 * lam
    for (mx, my, mr) in ((-0.3, -0.2, 0.3), (0.22, 0.12, 0.24), (-0.05, 0.46, 0.2), (0.42, -0.32, 0.15)):
        sx, sy = cx + mx * r, cy + my * r
        for q in cells:
            d = math.hypot(q[0] + 0.5 - sx, q[1] + 0.5 - sy) / (mr * r)
            if d <= 0.72:
                cells[q] -= 1.0
            elif d <= 1.0:
                cells[q] -= 0.5
    for (x, y), v in cells.items():
        p.px(x, y, M[max(2, min(6, round(v)))], L)
    for (mx, my) in ((0.3, 0.45), (-0.52, 0.18), (0.05, -0.55)):
        qx, qy = math.floor(cx + mx * r), math.floor(cy + my * r)
        if (qx, qy) in cells and (qx + 1, qy + 1) in cells:
            p.px(qx, qy, M[2], L)
            p.px(qx + 1, qy + 1, M[6], L)
    for (x, y) in list(cells):
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ddx, y + ddy)
            if q in cells:
                continue
            far = (q[0] + 0.5 - cx) * LX + (q[1] + 0.5 - cy) * LY < 0
            if not night:
                p.px(q[0], q[1], M[1] if far else M[2], L)
            elif far:
                p.px(x, y, M[3], L)
    return cells


# Bats: wings raised, then wings swept down; `#` is the bat, its ears two points on its head.
BAT_ART = [
    ["#.............#", "##...........##", ".##.........##.", ".###..#.#..###.", "..###.###.###..",
     "..###########..", "...#.#####.#...", "......###......", ".......#......."],
    ["......#.#......", "......###......", "....#######....", "..###########..", ".#############.",
     "###..#####..###", "#.....###.....#", ".......#......."],
]
BAT_EYES = [(4, (6, 8)), (1, (6, 8))]


def bat_symbol(p: Pix, frame: int, night: bool):
    """A bat drawn once: black, the leading edge of each wing and the top of its head caught by the
    light, the membrane between the bones a shade lighter by night, two red eyes."""
    key = ("bat", frame, night)
    if key not in p.syms:
        K = RAMP["coal"]
        art = BAT_ART[frame]
        ink = {(i, j) for j, r in enumerate(art) for i, ch in enumerate(r) if ch == "#"}
        cells = {}
        for (i, j) in ink:
            if (i, j - 1) not in ink:
                c = X["moonlit"] if night else K[4]
            elif (i + 1, j) not in ink or (i, j + 1) not in ink:
                c = K[1] if night else K[0]
            else:
                c = K[3] if night else K[1]
            cells[(i, j)] = c
        row, cols = BAT_EYES[frame]
        for col in cols:
            cells[(col, row)] = RAMP["blood"][5]
        p.symbol(key, cells)
    return key


def bat(p: Pix, x, y, frame=0, night=False, L="base"):
    p.use(bat_symbol(p, frame, night), x, y, L)


def bats(p: Pix, cx, cy, rx, ry, n, night, motion=True, seed=0, steps=56, dur=7.0, z=16):
    """Bats circling (cx, cy), each on a loop of its own and the other way round from the next,
    bobbing as they beat their wings. The still file leaves each where its loop begins."""
    rnd = random.Random(seed)
    frames = [bat_symbol(p, 0, night), bat_symbol(p, 1, night)]
    for i in range(n):
        a0 = rnd.uniform(0, 2 * math.pi)
        krx, kry = rx * rnd.uniform(0.75, 1.1), ry * rnd.uniform(0.65, 1.0)
        turn = 1 if i % 2 == 0 else -1
        path = []
        for s in range(steps):
            a = a0 + turn * 2 * math.pi * s / steps
            path.append((round(cx + krx * math.cos(a) - 7), round(cy + kry * math.sin(a) + 1.5 * math.sin(3 * a) - 4)))
        if motion:
            p.fly(frames, path, dur * rnd.uniform(0.85, 1.15), z)
        else:
            p.use(frames[i % 2], path[0][0], path[0][1], "base")


# --------------------------------------------------------------------------- light that falls on things
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `lamplight` lays its warm light on
    whatever stands within `r` of it, flickering with the flame. `own` are the lamp's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def lamplight(p: Pix, night: bool):
    """The finishing pass: each lamp's light on the drawn things near it (the earth, a headstone, a
    tree's roots, the rule), strongest nearest the flame. The paper, the sky and the words take none."""
    base = p.layers["base"]
    col = RAMP["pumpkin"][4]
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
    """The shadow a thing standing on the earth leaves right under it: only the soil takes it."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.7, X["shade_ink"], (0.22, 0.38), L="pool", only=GROUND, shape=False)


# --------------------------------------------------------------------------- lines and limbs
_PRI = {"twig": 0, "limb": 1, "trunk": 2}


def _put(cells: dict, q, tag):
    old = cells.get(q)
    if old is None or _PRI[tag] >= _PRI[old]:
        cells[q] = tag


def _disc(cells: dict, x, y, r, tag):
    for yy in range(math.floor(y - r), math.ceil(y + r) + 1):
        for xx in range(math.floor(x - r), math.ceil(x + r) + 1):
            if (xx + 0.5 - x) ** 2 + (yy + 0.5 - y) ** 2 <= r * r:
                _put(cells, (xx, yy), tag)


def _line(cells: dict, x0, y0, x1, y1, tag="twig"):
    """A one-pixel line, each step touching the last, the way a pixel artist draws a twig."""
    x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.floor(x1), math.floor(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        _put(cells, (x0, y0), tag)
        if (x0, y0) == (x1, y1):
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _pixel_perfect(cells: dict):
    """Take the corner out of every L in a one-pixel line, so a twig steps cleanly from pixel to pixel."""
    for q in [q for q, t in cells.items() if t == "twig"]:
        x, y = q
        n8 = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and (x + dx, y + dy) in cells]
        if len(n8) != 2:
            continue
        (ax, ay), (bx, by) = n8
        if abs(ax - bx) == 1 and abs(ay - by) == 1 and (ax == x or bx == x) and (ay == y or by == y):
            del cells[q]


def _branch(cells: dict, rnd, x, y, a, length, r, depth, sag=0.0, curl=True):
    """A limb from (x, y) at angle `a` (screen radians: -pi/2 is straight up). It wanders a little,
    narrows to a twig, forks `depth` more times and, as dead wood does, hooks over at its tip. Thick
    parts are discs; thin parts are one-pixel lines."""
    n = max(2, int(length))
    forks = set(rnd.sample(range(max(1, n // 4), max(2, n - n // 3)), min(2, depth))) if depth > 0 and n >= 7 else set()
    px_, py_ = x, y
    for i in range(1, n + 1):
        t = i / n
        a += rnd.uniform(-0.11, 0.11) + sag * t * (0.05 if math.cos(a) >= 0 else -0.05)
        x += math.cos(a)
        y += math.sin(a)
        rr = r * (1 - 0.8 * t)
        if rr >= 0.7:
            _disc(cells, x, y, rr, "limb")
        else:
            _line(cells, px_, py_, x, y)
        px_, py_ = x, y
        if i in forks:
            side = rnd.choice((-1, 1))
            _branch(cells, rnd, x, y, a + side * rnd.uniform(0.5, 0.85), length * (1 - t) * rnd.uniform(0.55, 0.8),
                    rr * 0.8, depth - 1, sag, curl)
    if curl:
        turn = 0.75 if math.cos(a) >= 0 else -0.75
        for _ in range(2):
            a += turn
            nx_, ny_ = x + math.cos(a) * 1.3, y + math.sin(a) * 1.3
            _line(cells, x, y, nx_, ny_)
            x, y = nx_, ny_


# --------------------------------------------------------------------------- the haunted tree
def dead_tree(p: Pix, cx, base, height, night=False, seed=4, hollow=True, L="base", phase=0, clip=None):
    """A bare, crooked tree with its roots on row `base`: a trunk that twists as it climbs and flares
    into roots, a limb low down, a crown of limbs that fork and wander and end in hooked twigs.

    By day the bark is shaded as a column lit from the left, split by dark cracks. By night the tree is
    a dark shape with moonlight along the edges that face the moon. `hollow` cuts a knothole whose lip
    catches the light, and by night two eyes in it that blink."""
    rnd = random.Random(seed)
    cells: dict = {}
    tw = max(1.5, height / 13.5)
    fork = max(6, int(height * 0.4))
    sway = rnd.uniform(0.9, 1.6) * (1 if seed % 2 else -1)
    rows = {}
    for i in range(fork + 3):
        t = min(1.0, i / fork)
        xc = cx + 0.5 + sway * math.sin(t * 3.1)
        r = tw * (1 - 0.42 * t) + (1.6 if i == 0 else 0.9 if i == 1 else 0.4 if i == 2 else 0)
        y = base - 0.5 - i
        _disc(cells, xc, y, r, "trunk")
        rows[math.floor(y)] = (xc, r)
    tx, ty = rows[math.floor(base - 0.5 - fork)][0], base - 0.5 - fork
    for a in (0.12, math.pi - 0.12):
        _branch(cells, rnd, cx + 0.5 + math.cos(a) * tw * 0.9, base - 1.2, a, tw * 2.3, 1.05, 0, curl=False)
    if height >= 30:
        sy = base - 0.5 - round(fork * 0.62)
        side = -1 if sway > 0 else 1
        _branch(cells, rnd, rows[math.floor(sy)][0] + side * tw * 0.4, sy, -math.pi / 2 + side * 1.2, height * 0.28,
                tw * 0.42, 1, sag=0.7)
    spread = [-2.6, -1.98, -1.28, -0.58] if height >= 40 else [-2.45, -1.55, -0.72]
    for i, a in enumerate(spread):
        outer = i in (0, len(spread) - 1)
        _branch(cells, rnd, tx, ty + (2 if outer else 0), a + rnd.uniform(-0.1, 0.1),
                height * (0.55 if outer else 0.47) * rnd.uniform(0.9, 1.05), tw * (0.6 if outer else 0.68),
                2 if height >= 40 else 1, sag=0.8 if outer else 0.15)
    _pixel_perfect(cells)
    if clip:
        cells = {q: t for q, t in cells.items() if clip[0] <= q[0] < clip[1]}
    Wd, K = RAMP["wood"], RAMP["coal"]
    for (x, y), tag in cells.items():
        if y >= base:
            continue
        lo, ro = (x - 1, y) not in cells, (x + 1, y) not in cells
        uo, do = (x, y - 1) not in cells, (x, y + 1) not in cells
        if tag == "trunk" and y in rows:
            xc, r = rows[y]
            u = (x + 0.5 - xc) / max(1.0, r)
            crack = (x - math.floor(xc)) % 4 == 1 and -0.45 < u < 0.6 and (y // 3) % 3 != 0
            if night:
                c = X["moonlit"] if lo else (K[1] if ro else (K[4] if u < -0.2 else K[3] if u < 0.45 else K[2]))
                c = K[2] if crack and c in (K[4], K[3]) else c
            else:
                c = Wd[4] if lo else (Wd[0] if ro else (Wd[3] if u < -0.2 else Wd[2] if u < 0.45 else Wd[1]))
                c = Wd[1] if crack and c in (Wd[3], Wd[2]) else c
        elif tag == "limb":
            if night:
                c = X["moonlit"] if (lo and uo) else (K[5] if (lo or uo) else (K[2] if (ro or do) else K[3]))
            else:
                c = Wd[3] if (lo or uo) else (Wd[1] if (ro or do) else Wd[2])
        else:
            c = K[4] if night else Wd[2]
        p.px(x, y, c, L)
    if hollow and height >= 40:
        hy = round(base - 0.5 - fork * 0.55)
        hx = math.floor(rows[hy][0]) if hy in rows else math.floor(cx)
        for dx, dy in ((0, -2), (-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (0, 1)):
            p.px(hx + dx, hy + dy, K[0], L)
        for dx, dy in ((1, 1), (2, 0)):
            p.px(hx + dx, hy + dy, K[5] if night else Wd[5], L)
        p.px(hx - 1, hy + 1, K[2] if night else Wd[1], L)
        if night:
            eyes = p.blink(phase)
            p.px(hx - 1, hy - 1, RAMP["flame"][5], eyes)
            p.px(hx + 1, hy - 1, RAMP["flame"][5], eyes)
    return dict(top=base - height, fork=ty)


# --------------------------------------------------------------------------- pumpkins
def _in_face(u, v, face):
    """Whether (u, v), a point on the pumpkin's face in units of its radii, is carved away."""
    au = abs(u)
    ey, eh, ex, ew = -0.3, 0.36, 0.36, 0.21
    if ey - eh / 2 <= v <= ey + eh / 2:
        f = (v - (ey - eh / 2)) / eh
        if abs(au - ex) <= ew * max(0.18, f):
            return True
    if face != "o" and 0.0 <= v <= 0.16 and au <= 0.1 * max(0.35, v / 0.16):
        return True
    top, bot = 0.3 - 0.42 * u * u, 0.64 - 0.9 * u * u
    if au <= 0.64 and top <= v <= bot:
        if face == "grin" and ((-0.26 <= u <= -0.09 and v < top + 0.13) or (0.1 <= u <= 0.27 and v > bot - 0.13)):
            return False
        return True
    return False


def _small_face(cx, cy, rx, ry):
    """A face for a pumpkin too small to carve by the formula: two eyes and a grin with a tooth."""
    ey = round(cy - 0.3 * ry)
    l_eye, r_eye = round(cx - 0.42 * rx), round(cx + 0.42 * rx) - 1
    cells = {(l_eye, ey), (r_eye, ey)}
    if rx >= 4.5 and r_eye - l_eye >= 5:
        cells |= {(l_eye + 1, ey), (r_eye - 1, ey)}
    my = round(cy + 0.3 * ry)
    xa, xb = round(cx - 0.5 * rx), round(cx + 0.5 * rx) - 1
    for x in range(xa, xb + 1):
        if x != round(cx):
            cells.add((x, my))
    if rx >= 4.5:
        cells |= {(xa - 1, my - 1), (xb + 1, my - 1)}
    return cells


def pumpkin(p: Pix, cx, base, rx, ry=None, night=False, face=None, L="base", phase=0, glow=True, vine=True):
    """A pumpkin sitting on row `base`, centred on `cx`. Its lobes bulge, each lit from the upper left
    with a glossy streak down its lit side, creased where it meets the one behind. It has a curved
    stem with a cut end and, on a big one, a leaf and a curl of vine.

    A `face` ("grin", "o" or "plain") carves it into a jack-o'-lantern lit from inside: the holes glow,
    hottest round the candle, the cut rind catches the light along their upper edges, and the rind
    round the face glows through. By day the sun lights the rind; by night it is dim, lit by the moon
    along its rim and from within, and the lantern throws its light on whatever stands near it."""
    P, F, S, W = RAMP["pumpkin"], RAMP["flame"], RAMP["slime"], RAMP["wood"]
    ry = ry or max(2.5, rx * 0.78)
    cy = base - ry
    n = 5 if rx >= 6 else 3
    lobes = []
    for i in range(n):
        off = (i - (n - 1) / 2) / ((n - 1) / 2)
        lcx = cx + off * rx * (0.6 if n == 5 else 0.48)
        hw = rx * (0.45 if n == 5 else 0.56)
        hh = ry * (0.95 if off == 0 else (1.0 if abs(off) < 0.6 else 0.9))
        lobes.append((abs(off), lcx, hw, hh))
    owner, lam_ = {}, {}
    for k in sorted(range(n), key=lambda i: -lobes[i][0]):
        ao, lcx, hw, hh = lobes[k]
        for y in range(math.floor(cy - hh) - 1, math.ceil(cy + hh) + 1):
            for x in range(math.floor(lcx - hw) - 1, math.ceil(lcx + hw) + 1):
                lx, ly = (x + 0.5 - lcx) / hw, (y + 0.5 - cy) / hh
                if lx * lx + ly * ly > 1 or y >= base:
                    continue
                gx, gy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                gz = math.sqrt(max(0.0, 1 - min(1.0, gx * gx + gy * gy)))
                lz = math.sqrt(max(0.0, 1 - lx * lx - ly * ly))
                nx, ny, nz = 0.45 * gx + 0.55 * lx, 0.45 * gy + 0.55 * ly, 0.45 * gz + 0.55 * lz
                ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                owner[(x, y)] = k
                lam_[(x, y)] = max(0.0, (nx * LX + ny * LY + nz * LZ) / ln)
    if face:
        if face == "plain" or rx < 6:
            holes = _small_face(cx, cy, rx, ry) & set(owner)
        else:
            holes = {q for q in owner if _in_face((q[0] + 0.5 - cx) / rx, (q[1] + 0.5 - cy) / ry, face)}
    else:
        holes = set()
    glowing = ({(x + dx, y + dy) for (x, y) in holes for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - holes) if night else set()
    for (x, y), k in owner.items():
        lam = lam_[(x, y)]
        v = (0.8 + 2.7 * lam) if night else (1.3 + 3.9 * lam)
        if any(owner.get((x + dx, y)) is not None and lobes[owner[(x + dx, y)]][0] < lobes[k][0] for dx in (-1, 1)):
            v -= 1.15
        if (x, y) in glowing:
            v += 1.2 if night else 0.45
        p.px(x, y, P[max(1, min(5, round(v)))], L)
    for k, (ao, lcx, hw, hh) in enumerate(lobes):
        if lcx > cx + 0.5:
            continue
        sx = round(lcx - 0.34 * hw - 0.5)
        mine = [y for (x, y), o in owner.items() if o == k and x == sx]
        if not mine:
            continue
        y0, y1 = min(mine), max(mine)
        top_ = y0 + max(1, round((y1 - y0) * 0.18))
        for y in range(top_, top_ + max(1, round((y1 - y0) * 0.38))):
            if owner.get((sx, y)) == k and (sx, y) not in holes and (sx, y) not in glowing:
                p.px(sx, y, P[4] if night else P[5], L)
        if ao == 0 and not night and rx >= 4:
            p.px(sx, top_, P[6], L)
    for (x, y) in list(owner):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in owner or q[1] >= base:
                continue
            lit = (q[0] + 0.5 - cx) * LX + (q[1] + 0.5 - cy) * LY > 0.25 * rx
            p.px(q[0], q[1], (X["moonlit"] if night else P[1]) if lit and dy <= 0 else P[0], L)
    # the stem: rooted in a dimple, curving up and over to the right, a pale cut end
    top = min(y for (x, y), o in owner.items() if lobes[o][0] == 0)
    sw = 2 if rx >= 6 else 1
    sh = max(2, round(ry * 0.42))
    sx0 = round(cx) - sw // 2
    p.hline(sx0 - 1, sx0 + sw + 1, top, P[2] if night else P[3], L)
    for j in range(1, sh + 1):
        lean = round(0.9 * (j / sh) ** 2 * (sw + 0.5))
        for i in range(sw):
            c = (S[2] if i == 0 else S[1]) if sw == 2 else S[2]
            if night:
                c = S[1] if i == 0 else S[0]
            p.px(sx0 + i + lean, top - j, c, L)
    cap = round(0.9 * (sw + 0.5))
    for i in range(sw):
        p.px(sx0 + i + cap, top - sh - 1, W[5] if i == 0 else W[4], L)
    if vine and rx >= 8:
        for (dx, dy) in ((sw + 1, -1), (sw + 2, -2), (sw + 3, -2), (sw + 4, -1), (sw + 4, 0), (sw + 3, 0)):
            p.px(sx0 + dx, top + dy, S[3] if not night else S[2], L)
        leaf = ((-1, -1, 4), (-2, -1, 4), (-3, -2, 5), (-2, -2, 4), (-3, -1, 3), (-4, -1, 3), (-4, 0, 2), (-3, 0, 2), (-2, 0, 2))
        for (dx, dy, t) in leaf:
            p.px(sx0 + dx, top + dy, S[t - 1] if night else S[t], L)
    if not face:
        return owner
    for (x, y) in holes:
        p.px(x, y, P[0], L)
        if not night and (x, y + 1) not in holes and (x, y + 1) in owner:
            p.px(x, y + 1, P[4], L)        # by day the sun catches the cut rind along each hole's foot
    Lf = p.flicker(phase)
    ccx, ccy = cx, cy + 0.34 * ry
    for (x, y) in holes:
        d = math.hypot((x + 0.5 - ccx) / rx, (y + 0.5 - ccy) / ry)
        if night:
            c = F[6] if d < 0.3 else (F[5] if d < 0.62 else F[4])
            if (x, y - 1) not in holes and rx >= 6:
                c = P[5]
        else:
            c = F[4] if d < 0.3 else (P[3] if d < 0.55 else None)   # a dim ember deep in the cut
        if c:
            p.px(x, y, c, Lf)
    if glow and night:
        p.halo(cx, cy, rx * 2.1, ry * 2.2, P[4], (0.05, 0.09, 0.15), L=p.flicker(phase, back=True))
    lamp(p, cx, cy + ry * 0.4, rx * (2.6 if night else 2.0), phase, set(owner) | holes)
    return owner


# --------------------------------------------------------------------------- the graveyard
def tombstone(p: Pix, x, base, w=13, h=17, night=False, carve="RIP", L="base", seed=0, moss=True):
    """A headstone on row `base`: a slab with a round top on a wider plinth. It is shaded as a column
    lit from the left, with a bevel along its crown that catches the light. The letters are cut in,
    dark in the cut with a lip of light along their foot. It has a crack, a chipped corner and moss
    climbing from its foot; too narrow for letters, it takes a cross. By night moonlight runs down its
    left edge and over its crown."""
    S, M = RAMP["stone"], RAMP["slime"]
    rnd = random.Random(seed)
    r = w / 2
    top = base - h
    pl = 2
    cells = set()
    for yy in range(top, base - pl):
        for xx in range(x, x + w):
            cy_ = top + r
            if yy + 0.5 < cy_ and math.hypot(xx + 0.5 - (x + r), yy + 0.5 - cy_) > r + 0.1:
                continue
            cells.add((xx, yy))
    chip = (x + w - 1, top + int(r) + 3)
    cells.discard(chip)
    lo_ = 2 if night else 3
    for (xx, yy) in cells:
        t = (xx + 0.5 - x) / w
        v = lo_ + 2.4 * (1 - t) ** 1.3
        c = S[max(1, min(5, round(v)))]
        crown = (xx, yy - 1) not in cells and yy < top + r
        if (xx - 1, yy) not in cells or crown:
            c = X["moonlit"] if night else S[6] if crown else S[5]
        elif (xx + 1, yy) not in cells:
            c = S[1]
        elif (xx, yy - 2) not in cells and yy < top + r + 1:
            c = S[5] if not night else S[4]
        p.px(xx, yy, c, L)
    for xx in range(x - 1, x + w + 1):
        for i in range(pl):
            yy = base - pl + i
            c = (S[4] if not night else S[3]) if i == 0 else (S[2] if not night else S[1])
            if xx == x - 1:
                c = X["moonlit"] if night else S[5]
            elif xx == x + w:
                c = S[1]
            p.px(xx, yy, c, L)
    if carve and p.measure(carve, "35") <= w - 4:
        tw = p.measure(carve, "35")
        tx, ty = x + (w - tw + 1) // 2, top + int(r) + 1
        cells_t, _ = p._cells(tx, ty, carve, "35", 1, 1)
        for (cx_, cy_) in cells_t:
            p.px(cx_, cy_, S[0] if not night else S[0], L)
            if (cx_, cy_ + 1) not in cells_t:
                p.px(cx_, cy_ + 1, S[5] if not night else S[4], L)
    else:
        mx = x + w // 2
        for yy in range(top + 3, top + 10):
            p.px(mx, yy, S[0], L)
            p.px(mx + 1, yy, S[5] if not night else S[4], L)
        for xx in range(mx - 2, mx + 3):
            p.px(xx, top + 5, S[0], L)
            p.px(xx, top + 6, S[5] if not night else S[4], L)
        p.px(mx, top + 5, S[0], L)
        p.px(mx, top + 6, S[0], L)
    kx, ky = x + w - 4, top + 2
    for i in range(6):
        p.px(kx, ky + i, S[1], L)
        if i:
            kx += rnd.choice((-1, 0, 1)) if i % 2 else 0
    if moss:
        for xx in range(x - 1, x + w + 1):
            k = rnd.random()
            if k < 0.6:
                p.px(xx, base - pl - 1 if (xx, base - pl - 1) in cells else base - pl, M[3] if k < 0.25 else M[2], L)
            if k < 0.2 and (xx, base - pl - 2) in cells:
                p.px(xx, base - pl - 2, M[4] if not night else M[3], L)
        for yy in range(top + 3, top + 3 + rnd.randint(2, 4)):
            p.px(x, yy, M[3] if not night else M[2], L)
    return cells


def ghost(p: Pix, x, y, w=13, h=16, night=False, L="base", glow=True, arms=True, blush=True, sway=1):
    """A ghost in a sheet, top-left at (x, y). Its head is round, its body flares to a scalloped hem
    that trails to one side as it floats, and its little arms are raised for a boo. The sheet hangs in
    folds from the arms. It is lit from the upper left: a bright crown on its head, soft lavender where
    it turns from the light and in the shadow under its arms. The hem thins to nothing. By day the
    sheet is white linen; by night it glows from within, brightest at its heart, with a halo. The face
    has dark eyes with a glint in each, a mouth open in an O and a blush under the eyes."""
    G, K = RAMP["ghost"], RAMP["coal"]
    r = w / 2
    body = {}
    for yy in range(h):
        fy = yy + 0.5
        t = max(0.0, (fy - r) / (h - r))
        shift = sway * 1.7 * t * t
        for xx in range(-3, w + 3):
            fx = xx + 0.5 - shift
            if fy <= r:
                if math.hypot(fx - r, fy - r) > r:
                    continue
                nx, ny, fade = (fx - r) / r, (fy - r) / r, 9.0
            else:
                hw = r + 0.85 * t
                if abs(fx - r) > hw:
                    continue
                hem = h - 1.9 + 1.45 * math.cos(2 * math.pi * fx / (w / 3) + 0.5)
                if fy > hem:
                    continue
                nx, ny, fade = (fx - r) / hw, 0.12, hem - fy
            nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            lam = max(0.0, nx * LX + ny * LY + nz * LZ)
            fold = 0.0
            if fy > r + 1:
                for fcx, depth in ((r + 0.36 * w, 0.9), (r - 0.18 * w, 0.45)):
                    fold -= depth * max(0.0, 1 - abs(fx - fcx) / 0.9) * min(1.0, t * 2.2)
            body[(xx, yy)] = (lam, fade, fold)
    ay = int(r + 1)
    if arms:
        for (ax, ay_, lam) in ((-1, ay, 0.9), (-2, ay - 1, 1.0), (-2, ay - 2, 1.0), (w, ay, 0.25), (w + 1, ay - 1, 0.3),
                               (w + 1, ay - 2, 0.35)):
            body[(ax, ay_)] = (lam, 9.0, 0.0)
    if glow and night:
        p.halo(x + r + 0.5, y + h * 0.48, w * 0.95, h * 0.74, G[5], (0.04, 0.07, 0.1), L=L, shape=True)
    for (xx, yy), (lam, fade, fold) in body.items():
        v = (3.9 + 2.6 * lam) if night else (3.1 + 3.2 * lam)
        v += fold
        if arms and yy in (ay + 1, ay + 2) and (xx <= 1 or xx >= w - 2):
            v -= 0.9
        if night:
            core = math.hypot((xx + 0.5 - r) / r, (yy + 0.5 - h * 0.45) / (h * 0.45))
            v += 0.6 * max(0.0, 1 - core)
        c = G[max(2, min(6, round(v)))]
        if (xx + 1, yy) not in body and fade > 2:
            c = G[2] if not night else G[3]
        if fade < 1.0:
            p.apx(x + xx, y + yy, c, 0.45, L)
        elif fade < 2.0:
            p.apx(x + xx, y + yy, c, 0.8, L)
        else:
            p.px(x + xx, y + yy, c, L)
    for (xx, yy), (lam, fade, fold) in body.items():
        if fade < 2.5:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            q = (xx + dx, yy + dy)
            if q not in body:
                p.px(x + q[0], y + q[1], (G[1] if dx > 0 else G[2]) if not night else (G[2] if dx > 0 else G[3]), L)
    ex = [round(r - 3.2), round(r + 1.2)] if w >= 11 else [round(r - 2.2), round(r + 1.2)]
    eh = 3 if w >= 11 else 2
    ew = 2 if w >= 11 else 1
    ey = round(r - 1.6)
    for e in ex:
        for dy in range(eh):
            for dx in range(ew):
                p.px(x + e + dx, y + ey + dy, K[1], L)
        p.px(x + e, y + ey, C["white"], L)
        if ew == 2:
            p.px(x + e + 1, y + ey + eh - 1, K[3], L)
    mx, my = x + math.floor(r), y + ey + eh + (2 if w >= 11 else 1)
    if w >= 15:
        for (dx, dy, c) in ((0, 0, K[1]), (-1, 1, K[1]), (0, 1, K[0]), (1, 1, K[1]), (-1, 2, K[1]), (0, 2, K[0]),
                            (1, 2, K[1]), (0, 3, K[1])):
            p.px(mx + dx, my + dy, c, L)
    else:
        for dy in range(2 if w >= 11 else 1):
            p.px(mx, my + dy, K[1], L)
    if blush and w >= 11:
        for e in (ex[0] - 1, ex[1] + ew):
            p.apx(x + e, y + ey + eh, RAMP["blood"][5], 0.5, L)
    return body


# --------------------------------------------------------------------------- things of the night
CORN_PROFILE = {5: [(1, "w"), (3, "w"), (3, "o"), (5, "o"), (5, "y"), (3, "y")],
                7: [(1, "w"), (3, "w"), (3, "w"), (5, "o"), (5, "o"), (7, "y"), (7, "y"), (5, "y")]}


def candy_corn(p: Pix, x, y, size=5, L="base", night=False):
    """A kernel of candy corn, tip up, `size` wide: a white tip, an orange band and a yellow foot, each
    band lit on the left and shaded on the right, with a glint on the orange band's shoulder."""
    B, P, F = RAMP["bone"], RAMP["pumpkin"], RAMP["flame"]
    k = -1 if night else 0
    ramps = {"w": (B, 3, 6), "o": (P, 2, 5), "y": (F, 2, 5)}
    for j, (wd, band) in enumerate(CORN_PROFILE[size]):
        R, lo, hi = ramps[band]
        x0 = x + (size - wd) // 2
        for i in range(wd):
            u = (i + 0.5) / wd
            t = hi if (wd == 1 or u < 0.34) else (hi - 1 if u < 0.67 else lo)
            p.px(x0 + i, y + j, R[max(0, t + k)], L)
    j = 3 if size == 7 else 2
    p.px(x + (size - CORN_PROFILE[size][j][0]) // 2, y + j, P[6 + k], L)


def witch_hat(p: Pix, x, y, w=15, h=14, night=False, L="base"):
    """A witch's hat, `w` by `h`, top-left at (x, y). The crown is a cone whose tip droops over to the
    right, shaded round from the left with a sheen along its lit side and a crease where the tip bends.
    It has an orange band with a gold buckle that catches the light, and a wide brim, lit on its upper
    face and dark beneath."""
    Pu, P, F = RAMP["purple"], RAMP["pumpkin"], RAMP["flame"]
    lo, hi = (0, 4) if night else (1, 5)
    brim = y + h - 3
    ch = h - 3
    c0 = x + w / 2 - 0.5
    cells = {}
    for j in range(ch):
        t = j / max(1, ch - 1)
        half = 3.4 * (1 - t) ** 0.85 + 0.35
        c = c0 + 3.4 * t ** 2.3
        yy = brim - 1 - j
        for xx in range(math.floor(c - half), math.ceil(c + half) + 1):
            u = (xx + 0.5 - c) / max(0.6, half)
            if abs(u) > 1.0:
                continue
            nz = math.sqrt(max(0.0, 1 - u * u))
            lam = max(0.0, u * LX + nz * LZ)
            v = lo + 0.4 + (hi - lo) * lam
            if -0.62 < u < -0.3 and 0.1 < t < 0.7:
                v += 0.8
            if 0.62 < t < 0.75:
                v -= 1.0
            cells[(xx, yy)] = Pu[max(lo, min(hi, round(v)))]
    tipx = max(xx for (xx, yy) in cells if yy == brim - ch)
    cells[(tipx + 1, brim - ch + 1)] = Pu[lo + 1]
    for (q, c) in cells.items():
        p.px(q[0], q[1], c, L)
    for xx in range(x + 3, x + w - 3):
        if (xx, brim - 2) in cells or (xx, brim - 1) in cells:
            u = (xx - x - 3) / max(1, w - 7)
            p.px(xx, brim - 2, P[5] if u < 0.3 else P[4] if u < 0.75 else P[3], L)
            p.px(xx, brim - 1, P[3] if u < 0.75 else P[2], L)
    bx = round(c0) - 1
    for (dx, dy, c) in ((0, -2, F[5]), (1, -2, F[4]), (2, -2, F[3]), (0, -1, F[4]), (2, -1, F[2])):
        p.px(bx + dx, brim + dy, c, L)
    p.px(bx + 1, brim - 1, Pu[lo], L)
    for xx in range(x, x + w):
        u = (xx + 0.5 - x) / w
        edge = xx in (x, x + w - 1)
        top_c = Pu[hi] if u < 0.3 else Pu[hi - 1] if u < 0.7 else Pu[hi - 2]
        if not edge:
            p.px(xx, brim, top_c, L)
        p.px(xx, brim + 1, Pu[lo + 1] if not edge else Pu[hi - 2], L)
        if not edge and 0 < xx - x < w - 1:
            p.px(xx, brim + 2, Pu[lo], L)


def cauldron(p: Pix, x, y, night=False, L="base", phase=1):
    """A witch's cauldron, 17 by 18, top-left at (x, y), over a fire of two logs. It is a black pot
    shaded as a ball, with a sheen down its lit side and a thick lip. The green brew bubbles over the
    lip and glows, lighting the rim from inside, while the fire flickers and lights the pot's belly
    from below."""
    K, S, F, P, W = RAMP["coal"], RAMP["slime"], RAMP["flame"], RAMP["pumpkin"], RAMP["wood"]
    cx, cy, r = x + 8.5, y + 8.5, 7.4
    pot = {}
    for yy in range(y + 4, y + 15):
        for xx in range(x + 1, x + 16):
            dx, dy = (xx + 0.5 - cx) / r, (yy + 0.5 - cy) / (r * 0.82)
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            lam = max(0.0, dx * LX + dy * LY + nz * LZ)
            v = 1.0 + 3.2 * lam
            if dy > 0.55:
                v = max(v, 2.2 + 1.5 * (dy - 0.55) / 0.45)
            pot[(xx, yy)] = v
    for (xx, yy), v in pot.items():
        c = K[max(1, min(4, round(v)))]
        if yy >= y + 13:
            c = P[2] if (yy == y + 14 or (xx + yy) % 2 == 0) else K[2]
        p.px(xx, yy, c, L)
    for yy in range(y + 6, y + 10):
        p.px(x + 4, yy, K[5] if not night else K[4], L)
    p.px(x + 4, y + 6, K[6] if not night else K[5], L)
    for xx in range(x + 1, x + 16):
        u = (xx - x - 1) / 14
        p.px(xx, y + 4, K[6] if u < 0.25 else K[5] if u < 0.6 else K[4], L)
        p.px(xx, y + 5, K[3] if u < 0.6 else K[2], L)
    for xx in range(x + 2, x + 15):
        u = (xx - x - 2) / 12
        p.px(xx, y + 3, S[5] if 0.25 < u < 0.6 else S[4] if u < 0.85 else S[3], L)
    for (dx, dy, c) in ((5, 2, S[5]), (6, 2, S[4]), (6, 1, S[6]), (9, 1, S[5]), (10, 2, S[4]), (10, 1, S[5]),
                        (8, 0, S[6]), (12, 2, S[4]), (3, 4, S[4]), (3, 5, S[3]), (3, 6, S[2]), (13, 4, S[3]), (13, 5, S[2])):
        p.px(x + dx, y + dy, c, L)
    for (dx, c) in ((4, K[4]), (5, K[1]), (11, K[4]), (12, K[1])):
        p.px(x + dx, y + 15, c, L)
    for (dx, dy, c) in ((3, 16, W[3]), (4, 16, W[2]), (5, 16, W[4]), (6, 16, W[3]), (7, 16, W[2]),
                        (9, 16, W[3]), (10, 16, W[4]), (11, 16, W[2]), (12, 16, W[3]), (13, 16, W[1]),
                        (4, 17, W[1]), (7, 17, W[1]), (9, 17, W[1]), (12, 17, W[1]), (5, 17, W[5]), (10, 17, W[5])):
        p.px(x + dx, y + dy, c, L)
    Lf = p.flicker(phase)
    for (dx, dy, c) in ((6, 15, F[4]), (7, 15, F[6]), (8, 15, F[5]), (9, 15, F[6]), (10, 15, F[4]),
                        (7, 14, F[4]), (9, 14, F[5]), (8, 16, F[6]), (6, 16, P[4]), (10, 16, P[4])):
        p.px(x + dx, y + dy, c, Lf)
    brew = S[4]
    p.halo(x + 8.5, y + 2.5, 9, 4.5, brew, (0.06, 0.12, 0.2) if night else (0.03, 0.06), L="haze", shape=True)
    if night:
        p.halo(x + 8.5, y + 16, 7, 3.2, P[4], (0.08, 0.15), L=p.flicker(phase, back=True), shape=True)
    lamp(p, x + 8.5, y + 16, 9, phase, set(pot))


BLACK_CAT = [
    "..#......#...",
    "..##....##...",
    "..###..###...",
    "..########...",
    ".##ee##ee##..",
    ".##########..",
    "..###nn###...",
    "...######....",
    "...#######...",
    "..#########..",
    ".##########.#",
    ".###########.",
    ".##########.#",
    ".##########.#",
    "..###..###..#",
    "..##...##..#.",
]


def black_cat(p: Pix, x, y, night=False, L="base"):
    """A black cat sitting, 13 by 16, top-left at (x, y): pointed ears with a warm inner ear, round
    green eyes that shine with a pupil and a glint, a pink nose, and its tail curled up at its side.
    Light runs along its back and the tops of its ears; by night it is moonlight, and its eyes glow."""
    K, S = RAMP["coal"], RAMP["slime"]
    ink = {(i, j) for j, r in enumerate(BLACK_CAT) for i, ch in enumerate(r) if ch != "."}
    for (i, j) in ink:
        ch = BLACK_CAT[j][i]
        if ch == "e":
            left = BLACK_CAT[j][i - 1] != "e"
            c = (S[6] if left else S[4]) if night else (S[5] if left else S[3])
        elif ch == "n":
            c = RAMP["blood"][5] if BLACK_CAT[j][i - 1] != "n" else RAMP["blood"][4]
        elif (i, j - 1) not in ink or (i - 1, j) not in ink:
            c = X["moonlit"] if night else K[4]
        elif (i + 1, j) not in ink:
            c = K[2] if night else K[0]
        else:
            c = K[3] if night else K[1]
        p.px(x + i, y + j, c, L)
    for (i, j) in ((3, 1), (8, 1)):
        p.px(x + i, y + j + 1, RAMP["blood"][2], L)
    p.px(x + 4, y + 4, K[0], L)
    p.px(x + 8, y + 4, K[0], L)
    if night:
        for (i, j) in ((3, 4), (7, 4)):
            p.halo(x + i + 1, y + j + 0.5, 1.8, 1.3, S[5], (0.25,), L="haze", shape=False)


SKULL = [
    "...abbbc...",
    ".aabbbbccd.",
    "abbbbbbccdd",
    "abbbbbbcccd",
    "bkkkbbkkkcd",
    "bkKkbbkKkcd",
    ".bkkbnbkkd.",
    "..bbnnnbd..",
    "..bcccccd..",
    "..c.c.c.d..",
]


def skull(p: Pix, x, y, L="base", night=False, phase=2):
    """A skull, 11 by 10, top-left at (x, y): bone shaded as a ball lit from the upper left, deep eye
    sockets, a nose, cheekbones and a row of teeth. By night an ember glows in each socket."""
    B, K, F = RAMP["bone"], RAMP["coal"], RAMP["flame"]
    k = -1 if night else 0
    pal = {"a": B[6 + k], "b": B[5 + k], "c": B[4 + k], "d": B[2 + k], "k": K[1], "K": K[2], "n": K[2]}
    p.sprite(x, y, SKULL, pal, 1, L)
    if night:
        Lf = p.flicker(phase)
        p.px(x + 2, y + 5, F[5], Lf)
        p.px(x + 7, y + 5, F[5], Lf)


SPIDER = [
    ".#.......#.",
    "#.#.....#.#",
    "...#.h.#...",
    ".##.bhb.##.",
    "#..#bbb#..#",
    "...#bbb#...",
    "..#..b..#..",
    ".#.......#.",
]


def spider(p: Pix, x, y, top=None, night=False, L="base"):
    """A spider, 11 by 8, top-left at (x, y), let down on its thread from row `top`: a round body with
    a glint on its shoulder, a red mark on its back, two red eyes, and eight legs bent at the knee."""
    K = RAMP["coal"]
    if top is not None:
        for yy in range(top, y + 3):
            p.px(x + 5, yy, X["web_night"] if night else X["web_day"], L)
    pal = {"#": K[5] if night else K[3], "b": K[3] if night else K[1], "h": K[4] if night else K[2]}
    p.sprite(x, y, SPIDER, pal, 1, L)
    p.px(x + 4, y + 4, X["moonlit"] if night else K[5], L)
    p.px(x + 5, y + 5, RAMP["blood"][4], L)
    p.px(x + 4, y + 2, RAMP["blood"][5], L)
    p.px(x + 6, y + 2, RAMP["blood"][5], L)


def candle(p: Pix, x, base, h=9, night=False, L="base", phase=0):
    """A candle, 3 wide, standing on row `base` in a pool of its own wax. Its bone-white wax is lit on
    the left, with wax run down its side and a melted cup at the top. It has a black wick and a
    teardrop flame, white at the heart and orange at the edge, that flickers with its glow and lights
    what stands near it."""
    B, F, P = RAMP["bone"], RAMP["flame"], RAMP["pumpkin"]
    k = -1 if night else 0
    top = base - h
    for yy in range(top, base):
        p.px(x, yy, B[5 + k], L)
        p.px(x + 1, yy, B[4 + k], L)
        p.px(x + 2, yy, B[3 + k], L)
    p.px(x, top, B[6], L)
    p.px(x + 1, top, B[4 + k], L)
    p.px(x + 2, top, B[5 + k], L)
    for yy in range(top + 1, top + 4):
        p.px(x - 1 if yy > top + 1 else x, yy, B[6 + k], L)
    p.px(x + 2, top + 1, B[5 + k], L)
    p.px(x + 2, top + 2, B[4 + k], L)
    for xx in range(x - 2, x + 5):
        p.px(xx, base - 1, B[5 + k] if xx < x + 1 else B[3 + k], L)
    p.px(x + 1, top - 1, RAMP["coal"][1], L)
    Lf = p.flicker(phase)
    flame = ((1, -2, F[6]), (1, -3, F[6]), (1, -4, F[5]), (1, -5, F[4]), (1, -6, P[4]), (0, -3, F[4]), (2, -3, F[4]),
             (0, -2, P[4]), (2, -2, P[4]))
    for (dx, dy, c) in flame:
        p.px(x + dx, top + dy, c, Lf)
    own = {(x + dx, top + dy) for dx, dy, _ in flame}
    for (qx, qy), c in glow_cells(x + 1.5, top - 3, 4.4, 5.0, F[4], (0.12, 0.22) if night else (0.05, 0.1), own).items():
        p.px(qx, qy, c, Lf)
    lamp(p, x + 1.5, top - 3, 7 if night else 5, phase, own | {(xx, yy) for xx in range(x - 2, x + 5) for yy in range(top - 1, base)})


def flame(p: Pix, x, y, night=False, phase=0, L=None):
    """A small flame, 3 by 5, its foot at (x+1, y): a white heart, a yellow body and an orange tip,
    flickering with its glow and lighting what is near it."""
    F, P = RAMP["flame"], RAMP["pumpkin"]
    Lf = L or p.flicker(phase)
    cells = ((1, 0, F[6]), (1, -1, F[6]), (0, -1, F[4]), (2, -1, P[4]), (1, -2, F[5]), (0, -2, P[4]),
             (2, -2, P[3]), (1, -3, F[4]), (1, -4, P[4]))
    for (dx, dy, c) in cells:
        p.px(x + dx, y + dy, c, Lf)
    own = {(x + dx, y + dy) for dx, dy, _ in cells}
    for (qx, qy), c in glow_cells(x + 1.5, y - 1.5, 3.8, 4.2, F[4], (0.14, 0.26) if night else (0.06, 0.12), own).items():
        p.px(qx, qy, c, Lf)
    lamp(p, x + 1.5, y - 1.5, 6 if night else 4, phase, own)


def bone(p: Pix, x, y, length=11, L="base", night=False):
    """A bone lying level, `length` long, top-left at (x, y): a shaft lit along its top and shaded
    beneath, and at each end a pair of knuckles, each a little ball lit from the upper left."""
    B = RAMP["bone"]
    k = -1 if night else 0
    for xx in range(x + 3, x + length - 3):
        p.px(xx, y + 1, B[6 + k], L)
        p.px(xx, y + 2, B[4 + k], L)
        p.px(xx, y + 3, B[2 + k], L)
    ends = (["abb.", "abbc", "bbcd", "abbc", "bccd"], [".bbc", "bbcd", "bccd", "bbcd", "ccdd"])
    for ex, art in ((x, ends[0]), (x + length - 4, ends[1])):
        p.sprite(ex, y, art, {"a": B[6 + k], "b": B[5 + k], "c": B[4 + k], "d": B[2 + k]}, 1, L)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["blood"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)


# --------------------------------------------------------------------------- glyphs and icons
ARROW = ["...#...", "..###..", ".#.#.#.", "#..#..#", "...#...", "...#...", "...#..."]
CHECK = ["......#", ".....##", "#...##.", "##.##..", ".###...", "..#...."]
# 7x7 icons for buttons, nodes and badges, lit from the upper left like everything else. Tones:
# o O p pumpkin, y candlelight, g stem, w W ghost, e eyes, k K bat, v V u witch's purple, b band,
# a A bone, # ink.
ICONS = {
    "pumpkin": ["...g...", ".oOOOp.", "oyOOyOp", "oOOOOOp", "oyyyyOp", ".OyOyp.", "..ppp.."],
    "bat": [".......", "K.K.K.K", "kKkkkKk", "kkkekkk", ".kk.kk.", "..k.k..", "......."],
    "ghost": ["..www..", ".wwwwW.", "wewweWW", "wwwwwWW", "wwwewWW", "wwwwwWW", "w.ww.W."],
    "hat": ["....u..", "...Vu..", "...VV..", "..vVVu.", "..bbbb.", "vvVVVVu", "......."],
    "skull": [".aaaaA.", "aaaaaaA", "aeeaeeA", "aeeaeeA", ".aaeaA.", "..aAA..", "..a.A.."],
    "corn": ["...w...", "..wwW..", "..oOp..", ".oOOOp.", ".yyyyp.", "yyyyyyp", "......."],
    "pulse": [".......", "...#...", "...#...", "#.#.#.#", "..#.#..", "..#....", "......."],
}
ICON5 = {
    "pumpkin": ["..g..", ".oOp.", "oyOyp", "oyyyp", ".oOp."],
    "bat": ["K.K.K", "kKkKk", "kkekk", ".k.k.", "....."],
    "ghost": [".www.", "wewew", "wwwwW", "wwewW", "w.w.W"],
    "hat": ["...u.", "..Vu.", ".bbb.", "vVVVu", "....."],
    "skull": [".aaA.", "aeaeA", "aaaaA", ".aeA.", ".a.A."],
    "corn": ["..w..", ".wwW.", ".oOp.", "yyyyp", "....."],
    "pulse": [".....", "..#..", "#.#.#", "...#.", "....."],
}


def icon_pal(mode="day", ink=None) -> dict:
    """The icons' tones on paper by day, on the night sky, or pressed into a live plate."""
    P, F, G, K, Pu, B, S = (RAMP[k] for k in ("pumpkin", "flame", "ghost", "coal", "purple", "bone", "slime"))
    if mode == "live":
        return {"o": K[3], "O": K[2], "p": K[1], "y": P[3], "g": K[2], "w": K[3], "W": K[2], "e": P[3],
                "k": K[1], "K": K[3], "v": K[3], "V": K[2], "u": K[1], "b": P[3], "a": K[3], "A": K[2], "#": ink}
    night = mode == "night"
    return {"o": P[5] if night else P[4], "O": P[4] if night else P[3], "p": P[3] if night else P[2],
            "y": F[5] if night else F[4], "g": S[4] if night else S[2],
            "w": C["white"] if night else G[3], "W": G[4] if night else G[1], "e": K[1],
            "k": K[4] if night else K[1], "K": X["moonlit"] if night else K[4],
            "v": Pu[5] if night else Pu[4], "V": Pu[4] if night else Pu[3], "u": Pu[3] if night else Pu[1],
            "b": P[4], "a": B[6] if night else B[4], "A": B[4] if night else B[2], "#": ink}
