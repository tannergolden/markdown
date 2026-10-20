# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The twins in flight, the H3's: the herald of heaven flying to the left blowing a long trumpet of gold, a banner
hung from it streaming back, its wings raised behind it and its robe trailing; and the herald of hell, flying where
the angel flew, blowing a black ram's horn hung with a tattered pennant, on bat wings, its tail streaming. Each
herald's call crosses the sky before it (`call`): by day a fan of heaven's light from the trumpet's bell, by night
a jet of fire from the horn.

Each is drawn in its own units about its head at (0, 0), facing left, scaled by `k`."""
from __future__ import annotations

import math

from ...holidays.pixel import Pix
from .kit import curve, ellipse, flat, form, glow, outline, poly, stroke
from .palette import C, RAMP, X

GOLD, LINEN, PEARL, AZURE = RAMP["gold"], RAMP["linen"], RAMP["pearl"], RAMP["azure"]
HIDE, HORN, MEMBRANE, IRON, FIRE, LAVA = (RAMP["hide"], RAMP["horn"], RAMP["membrane"], RAMP["iron"], RAMP["fire"],
                                          RAMP["lava"])


class Flight:
    """A flyer's place and size: its units, about its head, turned into the canvas's cells."""

    def __init__(self, x, y, k=1.0):
        self.x, self.y, self.k = x, y, k

    def pt(self, u, v):
        return (self.x + u * self.k, self.y + v * self.k)

    def poly(self, pts):
        return poly([self.pt(u, v) for u, v in pts])

    def ellipse(self, u, v, rx, ry):
        cx, cy = self.pt(u, v)
        return ellipse(cx, cy, rx * self.k, ry * self.k)

    def stroke(self, pts, r0, r1=None):
        r1 = r0 if r1 is None else r1
        return stroke([self.pt(u, v) for u, v in pts], max(0.55, r0 * self.k), max(0.5, r1 * self.k))


# The flight feathers of a wing swept up and back, (root, tip), outermost first: the long primaries from the wrist
# high over the back, the shorter secondaries from the forearm, all streaming back to the right as it flies.
SWEPT = (
    ((19.0, -13.0), (35.0, -20.0)),
    ((17.0, -11.5), (33.0, -15.0)),
    ((15.0, -9.5), (30.5, -10.5)),
    ((13.0, -7.5), (27.5, -6.0)),
    ((11.0, -5.5), (24.0, -2.0)),
    ((9.0, -3.5), (20.0, 1.6)),
)
SWEPT_ARCH = ((5.0, 2.0), (8.5, -4.5), (13.5, -10.0), (19.5, -13.8))


def swept_wing(p: Pix, f: Flight, dx=0.0, dy=0.0, shade=0, L="base"):
    """A feathered wing swept up and back over a flying angel, offset by (dx, dy); `shade` darkens it a tone, for
    the far wing behind the body."""
    cells_all = set()
    for i, (root, tip) in enumerate(SWEPT):
        r, t = (root[0] + dx, root[1] + dy), (tip[0] + dx, tip[1] + dy)
        mid = ((r[0] + t[0]) / 2 + 0.6, (r[1] + t[1]) / 2 - 1.2)
        cells = f.stroke(curve([r, mid, t], 8), 2.2 - 0.1 * i, 1.0) - cells_all
        for (x, y) in cells:
            under = (x, y + 1) not in cells
            c = LINEN[3 - shade] if under else LINEN[5 - shade]
            p.px(x, y, c, L)
        cells_all |= cells
    arch = f.stroke([(u + dx, v + dy) for u, v in SWEPT_ARCH], 1.8, 1.2)
    for (x, y) in arch:
        p.px(x, y, (GOLD[6] if not shade else PEARL[5]) if (x, y - 1) not in arch else PEARL[6 - shade], L)
    cells_all |= arch
    outline(p, cells_all, LINEN[1], LINEN[2], L, only_free=True)
    return cells_all


def herald(p: Pix, x, y, k=1.0, motion=True, L="base"):
    """The herald of heaven in flight, its head at (x, y), facing left: a long trumpet of gold at its lips and a
    banner of white and azure hung from it, its wings swept up behind it, its robe of white trailing in folds, a halo
    over its head."""
    f = Flight(x, y, k)
    SK, HR = RAMP["skin0"], RAMP["blond"]
    swept_wing(p, f, dx=-2.5, dy=-4.0, shade=1, L=L)             # the far wing, behind, raised a little higher
    # the robe, trailing back from the shoulders past the feet, its folds streaming
    robe = f.poly([(2.0, 2.4), (8.0, 1.6), (16.0, 3.0), (26.0, 4.4), (36.0, 3.0), (33.0, 6.4), (38.0, 8.8),
                   (30.0, 9.4), (22.0, 9.2), (14.0, 8.4), (6.0, 7.0), (2.2, 5.6)])
    form(p, robe, LINEN, lo=2, hi=6, L=L, depth=1.8)
    for fold in (((12, 4.2), (24, 6.2), (35, 6.0)), ((10, 6.6), (22, 8.0), (31, 8.4))):
        for (qx, qy) in f.stroke(list(fold), 0.4):
            if (qx, qy) in robe:
                p.px(qx, qy, LINEN[3], L)
    for (qx, qy) in robe:
        if (qx + 1, qy) not in robe and qx > f.pt(30, 0)[0]:
            p.px(qx, qy, GOLD[4], L)                               # the gold hem at its trailing edge
    outline(p, robe, LINEN[1], LINEN[2], L)
    feet = f.ellipse(31.0, 9.8, 1.6, 0.9) | f.ellipse(27.0, 10.2, 1.6, 0.9)
    form(p, feet, SK, lo=2, hi=5, L=L, depth=0.8)
    # the sash of azure across the body
    sash = f.stroke([(4.0, 2.6), (12.0, 6.6)], 0.9)
    flat(p, sash, AZURE[3], L)
    # the arm reaching forward to hold the trumpet
    arm = f.stroke([(3.0, 3.6), (-2.0, 4.2), (-6.0, 2.8)], 1.3, 1.0)
    form(p, arm, SK, lo=2, hi=5, L=L, depth=1.0)
    outline(p, arm, SK[0], SK[1], L, only_free=True)
    # the hair streaming back, the head, the face in profile
    hair = f.ellipse(1.0, -0.6, 3.8, 3.5) | f.poly([(2.0, -2.0), (8.0, -0.6), (7.0, 2.4), (2.6, 2.6)])
    form(p, hair, HR, lo=1, hi=5, L=L, depth=1.4)
    outline(p, hair, HR[0], HR[1], L, only_free=True)
    head = f.ellipse(-0.6, 0.4, 2.9, 3.1)
    form(p, head, SK, lo=2, hi=5, L=L, depth=1.6)
    ex, ey = f.pt(-1.6, 0.0)
    p.px(int(ex), int(ey), RAMP["brown"][1], L)
    p.px(int(ex) + 1, int(ey) + 2, RAMP["rose"][4], L)
    # the trumpet: a long tube of gold from its lips, flaring to a bell
    tube = f.stroke([(-3.0, 1.2), (-26.0, 2.6)], 0.75)
    for (qx, qy) in tube:
        p.px(qx, qy, GOLD[5] if (qx, qy - 1) not in tube else GOLD[3], L)
    bell = f.poly([(-25.0, 2.0), (-31.0, -1.4), (-31.6, 6.6), (-25.0, 3.4)])
    form(p, bell, GOLD, lo=2, hi=6, L=L, depth=1.4)
    outline(p, tube | bell, GOLD[1], GOLD[2], L, only_free=True)
    bx, by = f.pt(-31.4, 2.6)
    glow(p, bx, by, 5 * k, 6 * k, X["glory"], (0.18, 0.32))
    # the banner hung from the trumpet, streaming back, swallow-tailed, white with a band of azure, fringed in gold
    banner = f.poly([(-20.0, 2.8), (-9.0, 3.0), (-8.0, 13.0), (-11.6, 10.6), (-14.0, 14.4), (-17.0, 11.2),
                     (-20.6, 12.6)])
    form(p, banner, LINEN, lo=3, hi=6, L=L, depth=1.4)
    band = f.poly([(-20.4, 6.6), (-8.6, 6.8), (-8.4, 8.8), (-20.6, 8.6)])
    flat(p, band & banner, AZURE[3], L)
    outline(p, banner, GOLD[3], GOLD[4], L, only_free=True)
    swept_wing(p, f, L=L)                                          # the near wing, before the body
    # the halo, tilted with the head
    hx, hy = f.pt(1.0, -6.4)
    ring = ellipse(hx, hy, 4.4 * k, 1.4 * k) - ellipse(hx, hy + 0.2, 4.4 * k - 1.1, max(0.4, 1.4 * k - 0.9))
    for (qx, qy) in ring:
        p.px(qx, qy, GOLD[6] if qx < hx else GOLD[4], L)
    glow(p, hx, hy, 6 * k, 3 * k, X["glory"], (0.2, 0.34))
    Lt = p.twinkle(2) if motion else L
    p.px(int(hx - 3 * k), int(hy) - 1, C["white"], Lt)
    blast(p, f, False, motion)


def clear_cells(p: Pix, cells, margin=2):
    """The cells of `cells` that lie `margin` units clear of every word."""
    return [(x, y) for (x, y) in cells if p.clear_of_words(x - margin, y - margin, x + 1 + margin, y + 1 + margin)]


def blast(p: Pix, f: Flight, night: bool, motion=True):
    """What the herald's call looks like: by day a fan of heaven's light from the trumpet's bell, twinkling at its
    edge; by night a gout of fire and smoke from the horn. Only where it stays two units clear of every word."""
    if night:
        bx, by = -27.0, 9.0
        Lf = p.flicker(2) if motion else "base"
        flame = [(-1.0, 1.0, FIRE[6]), (-2.0, 1.6, FIRE[5]), (-1.0, 2.4, FIRE[5]), (-3.0, 2.4, FIRE[4]),
                 (-2.0, 3.2, FIRE[4]), (-4.0, 3.4, LAVA[4]), (-3.0, 4.2, LAVA[4]), (-5.0, 4.6, LAVA[3])]
        cells = {(int(f.pt(bx + u, by + v)[0]), int(f.pt(bx + u, by + v)[1])): c for u, v, c in flame}
        for (x, y) in clear_cells(p, cells):
            p.px(x, y, cells[(x, y)], Lf)
        smoke = []
        for u, v, r in ((-6.0, 6.0, 1.8), (-8.6, 8.4, 2.2), (-11.0, 11.2, 2.6)):
            cx, cy = f.pt(bx + u, by + v)
            smoke += list(ellipse(cx, cy, r * f.k, r * f.k * 0.8))
        for (x, y) in clear_cells(p, smoke):
            p.apx(x, y, RAMP["smoke"][3], 0.5, "fog")
        return
    bx, by = -31.6, 2.6
    rays = []
    for a in (-26, -9, 8, 25):
        t = math.radians(180 + a)
        for d in range(2, 12):
            q = f.pt(bx + math.cos(t) * d, by + math.sin(t) * d)
            rays.append((int(q[0]), int(q[1]), d))
    keep = set(clear_cells(p, {(x, y) for x, y, _ in rays}))
    for (x, y, d) in rays:
        if (x, y) in keep:
            p.apx(x, y, X["glory"] if d > 4 else GOLD[6], max(0.2, 0.8 - d * 0.06), "haze")
    Lt = p.twinkle(1) if motion else "base"
    for a in (-26, 25):
        t = math.radians(180 + a)
        q = f.pt(bx + math.cos(t) * 12, by + math.sin(t) * 12)
        q = (int(q[0]), int(q[1]))
        if clear_cells(p, [q]):
            p.px(q[0], q[1], C["white"], Lt)


# The bat wing swept back, the herald of hell's: its arm from the shoulder to the wrist high over its back, and
# the tips of its fingers streaming back.
BAT_SWEPT_ARM = ((5.0, 2.0), (11.0, -7.0), (18.0, -14.0))
BAT_SWEPT_TIPS = ((34.0, -19.0), (35.0, -9.0), (29.5, -0.5), (18.0, 3.5))


def bat_swept(p: Pix, f: Flight, dx=0.0, dy=0.0, shade=0, L="base"):
    arm = [(u + dx, v + dy) for u, v in BAT_SWEPT_ARM]
    tips = [(u + dx, v + dy) for u, v in BAT_SWEPT_TIPS]
    wrist = arm[-1]
    pts = list(arm) + [tips[0]]
    for a, c in zip(tips, tips[1:]):
        mx, my = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
        pts += [(mx + (wrist[0] - mx) * 0.3, my + (wrist[1] - my) * 0.3), c]
    pts += [(10.0 + dx, 4.0 + dy)]
    skin = f.poly(pts)
    ux, uy = f.pt(*wrist)
    for (x, y) in skin:
        d = math.hypot(x + 0.5 - ux, y + 0.5 - uy) / (22 * f.k)
        p.px(x, y, MEMBRANE[max(1, (4 if d > 0.8 else 3 if d > 0.4 else 2) - shade)], L)
    bones = f.stroke(arm, 1.3, 1.0)
    for t in tips:
        bones |= f.stroke([wrist, t], 0.8, 0.45)
    for (x, y) in bones:
        p.px(x, y, HIDE[4 - shade] if (x, y - 1) not in bones else HIDE[2 - shade], L)
    outline(p, skin | bones, MEMBRANE[0], MEMBRANE[2], L, only_free=True)


def fiend(p: Pix, x, y, k=1.0, motion=True, L="base"):
    """The herald of hell, flying where the angel flew: a black ram's horn at its lips, a tattered pennant of black
    edged in red hung from it, bat wings swept up behind it, its red hide bare, its tail streaming back to a barb,
    horns curling from its brow and its eyes burning."""
    f = Flight(x, y, k)
    bat_swept(p, f, dx=-2.5, dy=-4.0, shade=1, L=L)
    # the tail, streaming back
    tail = f.stroke(curve([(16.0, 5.0), (30.0, 8.0), (38.0, 3.0), (44.0, 6.0)], 12), 1.1, 0.5)
    flat(p, tail, HIDE[3], L)
    tx, ty = f.pt(44.0, 6.0)
    flat(p, poly([(tx - 1, ty - 2.4 * k), (tx + 2.8 * k, ty), (tx - 1, ty + 2.4 * k)]), HIDE[4], L)
    # the body, lean and long, the legs drawn back
    body = f.poly([(2.0, 2.0), (9.0, 1.4), (16.0, 3.0), (18.0, 6.4), (12.0, 8.0), (4.0, 6.4)])
    legs = f.stroke([(15.0, 5.0), (23.0, 6.6), (29.0, 9.8)], 1.6, 1.0) | f.stroke([(14.0, 6.4), (21.0, 9.8),
                                                                                  (26.0, 12.2)], 1.5, 0.9)
    form(p, body | legs, HIDE, lo=1, hi=5, L=L, depth=1.6)
    for hx_, hy_ in ((29.4, 10.0), (26.4, 12.4)):
        hx, hy = f.pt(hx_, hy_)
        p.px(int(hx), int(hy), IRON[2], L)
        p.px(int(hx) + 1, int(hy), IRON[1], L)
    outline(p, body | legs | tail, HIDE[0], HIDE[1], L, only_free=True)
    arm = f.stroke([(3.0, 3.6), (-2.0, 4.4), (-6.0, 3.0)], 1.4, 1.1)
    form(p, arm, HIDE, lo=1, hi=4, L=L, depth=1.0)
    outline(p, arm, HIDE[0], HIDE[1], L, only_free=True)
    # the head: ears pointed, horns curling back from the brow
    head = f.ellipse(-0.4, 0.4, 2.9, 3.1) | f.poly([(1.6, -1.0), (5.6, -2.8), (2.4, 1.0)])
    form(p, head, HIDE, lo=1, hi=5, L=L, depth=1.6)
    hn = f.stroke(curve([(0.4, -2.4), (4.0, -6.0), (8.4, -6.2), (9.6, -3.0)], 8), 1.1, 0.35)
    for (qx, qy) in hn:
        p.px(qx, qy, HORN[5] if (qx, qy - 1) not in hn else HORN[3], L)
    outline(p, head | hn, HIDE[0], HIDE[1], L, only_free=True)
    ex, ey = f.pt(-1.6, 0.0)
    Lb = p.blink(0) if motion else L
    p.px(int(ex), int(ey), FIRE[6], Lb)
    p.px(int(ex) + 1, int(ey), FIRE[4], Lb)
    # the ram's horn at its lips, black, ringed, curling down to its bell
    horn_path = curve([(-3.0, 1.4), (-14.0, 0.0), (-24.0, 2.6), (-27.0, 8.6)], 14)
    horn = set()
    for i, q in enumerate(horn_path[:-1]):
        r = 0.7 + 1.9 * i / len(horn_path)
        horn |= stroke([f.pt(*q), f.pt(*horn_path[i + 1])], max(0.55, r * k), max(0.55, r * k))
    for (qx, qy) in horn:
        ring = int((qx * 0.7 + qy * 0.3)) % 3 == 0
        p.px(qx, qy, HORN[2] if ring else (HORN[4] if (qx, qy - 1) not in horn else HORN[3]), L)
    outline(p, horn, HORN[0], HORN[1], L, only_free=True)
    bx, by = f.pt(-27.0, 9.0)
    glow(p, bx, by, 4 * k, 4 * k, X["heat"], (0.2, 0.32), L=p.flicker(1) if motion else "haze")
    # the pennant hung from the horn, black, tattered, edged in red
    pen = f.poly([(-19.0, 2.2), (-9.0, 1.2), (-8.0, 12.0), (-10.4, 9.6), (-12.0, 13.4), (-14.4, 10.0),
                  (-16.4, 12.8), (-19.4, 10.4)])
    form(p, pen, IRON, lo=1, hi=3, L=L, depth=1.2)
    outline(p, pen, LAVA[2], LAVA[3], L, only_free=True)
    bat_swept(p, f, L=L)
    blast(p, f, True, motion)


def _reach(p: Pix, ox, oy, t, most, box, margin=2) -> float:
    """How far a line from (ox, oy) at angle `t` runs, up to `most` units, before it leaves `box`, (x0, y0, x1, y1),
    or comes within `margin` units of a word."""
    x0, y0, x1, y1 = box
    d = 2.0
    while d < most:
        x, y = int(ox + math.cos(t) * d), int(oy + math.sin(t) * d)
        if not (x0 <= x < x1 and y0 <= y < y1) or not p.clear_of_words(x - margin, y - margin, x + 1 + margin,
                                                                         y + 1 + margin):
            return d - 1
        d += 1.0
    return most


def call(p: Pix, x, y, k, night: bool, motion=True, box=None, most=160):
    """The herald's call carried out across the sky before it, its head at (x, y): by day a fan of heaven's light
    thrown from the trumpet's bell, its beams long and pale, shimmering; by night a gout of fire from the horn,
    yellow at its heart and red at its ragged edge, flickering, its smoke rolling off its end. Every beam and
    tongue stops two units short of every word and inside `box`, (x0, y0, x1, y1)."""
    import random
    rnd = random.Random(7)
    f = Flight(x, y, k)
    box = box or (6, 6, p.w - 6, p.h - 6)
    if not night:
        ox, oy = f.pt(-32.6, 2.6)
        for i, a in enumerate((-21, -12, -4, 4, 12, 21)):
            t, da = math.radians(180 + a), math.radians(rnd.uniform(1.6, 2.6))
            n = min(_reach(p, ox, oy, t - da, most, box), _reach(p, ox, oy, t + da, most, box),
                    _reach(p, ox, oy, t, most, box))
            if n < 10:
                continue
            pts = [(ox, oy)] + [(ox + math.cos(b) * n, oy + math.sin(b) * n) for b in (t - da, t + da)]
            L = p.twinkle(i, back=True) if motion else "haze"
            p.shapes[L].append(f'<polygon points="{" ".join(f"{u:.1f},{v:.1f}" for u, v in pts)}" '
                               f'fill="{X["glory"]}" fill-opacity="{0.62 if a in (-4, 4) else 0.46}"/>')
            if n > 24:
                ex, ey = int(ox + math.cos(t) * n), int(oy + math.sin(t) * n)
                p.px(ex, ey, C["white"], p.twinkle(i + 1) if motion else "base")
        glow(p, ox, oy, 7 * k, 5 * k, X["glory"], (0.22, 0.36, 0.5), shape=True)
        return
    ox, oy = f.pt(-28.0, 9.4)
    most = min(most, 70 * k)
    # the horn's fire goes where the sky before it is clearest, from level to well upward
    full, aim = max(((min(_reach(p, ox, oy, math.radians(180 + aim + a), most, box) for a in (-14, -7, 0, 7, 14)),
                      aim) for aim in range(-4, 40, 4)), key=lambda q: q[0])
    if full < 10:
        return
    phi = math.radians(aim)
    D, N = (-math.cos(phi), -math.sin(phi)), (-math.sin(phi), math.cos(phi))

    def at(u, w):
        return (ox + D[0] * u + N[0] * w, oy + D[1] * u + N[1] * w)

    # the fire itself, a flame turned on its side: white-hot at the horn's mouth and along its heart, yellow, then
    # orange, breaking into ragged red tongues toward its end and its edges, its outer tongues flickering
    n = full
    cells = {}
    for (qx, qy) in poly([at(0, -1.5 * k), at(n, -math.tan(math.radians(16)) * n - 1.5 * k),
                          at(n * 1.04, 0), at(n, math.tan(math.radians(16)) * n + 1.5 * k), at(0, 1.5 * k)]):
        vx, vy = qx + 0.5 - ox, qy + 0.5 - oy
        u = vx * D[0] + vy * D[1]
        w = vx * N[0] + vy * N[1]
        if u < 0:
            continue
        t = min(1.0, u / n)
        half = math.tan(math.radians(16)) * u + 1.5 * k
        r = abs(w) / half
        # tongues streaming along the fire, wider toward its end
        wave = (0.15 * math.sin(w / k * 1.25 + u / k * 0.22 + 1.3) + 0.1 * math.sin(u / k * 0.7 - w / k * 0.5)) * t
        heat = (1 - t) ** 0.6 * (1 - r * r) + wave
        if heat < 0.06:
            continue
        cells[(qx, qy)] = (FIRE[6] if heat > 0.72 else FIRE[5] if heat > 0.52 else FIRE[4] if heat > 0.36 else
                           FIRE[3] if heat > 0.22 else LAVA[3], heat)
    keep = set(clear_cells(p, cells))
    for (qx, qy), (col, heat) in cells.items():
        if (qx, qy) in keep:
            p.px(qx, qy, col, ("base" if heat > 0.36 else p.flicker((qx + qy) % 3)) if motion else "base")
    # its smoke rolling up off the end of the fire, and sparks flung out of it
    for s in range(3):
        cx, cy = at(full * (0.84 + 0.12 * s), 0)
        cy -= (1.5 + 2.2 * s) * k
        r = (2.2 + s * 0.9) * k
        if p.clear_of_words(int(cx - r) - 2, int(cy - r) - 2, int(cx + r) + 3, int(cy + r) + 3) and cx - r > box[0] \
                and cy - r > box[1]:
            p.shapes[p.layer("fog")].append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.8:.1f}" '
                                   f'fill="{RAMP["smoke"][4]}" fill-opacity=".38"/>')
    for s in range(6):
        u = full * rnd.uniform(0.3, 1.0)
        qx, qy = (int(c) for c in at(u, rnd.uniform(-1, 1) * math.tan(math.radians(17)) * u))
        if clear_cells(p, [(qx, qy)]):
            p.px(qx, qy, FIRE[5], p.twinkle(s) if motion else "base")
