# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Heaven, by day: its cumulus and its far-off deck of cloud, and its pearly gates, every one lit from the upper
left."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import LX, LY, LZ, Pix
from .kit import clear, ellipse, glow, outline, poly
from .palette import C, RAMP, X

GOLD, PEARL, CLOUD, LINEN = RAMP["gold"], RAMP["pearl"], RAMP["cloud"], RAMP["linen"]


# --------------------------------------------------------------------------- clouds
def puffs_for(x0, x1, foot, top, seed=0, big=1.0, crown=0.5) -> list:
    """The puffs of a bank of cumulus between x0 and x1 standing on row `foot` and heaped to about row `top`: puffs
    strung along the bank's dome, highest at `crown` of its span and falling away to its ends, and broader ones
    filling it below, so the bank has a lumpy round top and a flat foot."""
    rnd = random.Random(seed)
    height = max(4.0, foot - top)
    span = max(1.0, x1 - x0)
    out = []

    def dome(t):
        d = 1 - abs(t - crown) / max(crown, 1 - crown)
        return max(0.18, d) ** 0.55

    x = x0 + rnd.uniform(0.5, 2.0)
    while x < x1 - 0.5:
        t = (x - x0) / span
        e = height * dome(t) * rnd.uniform(0.82, 1.0)
        r = max(2.6, min(e * 0.62, height * rnd.uniform(0.16, 0.3) * big))
        out.append((x, foot - e + r * 0.95, r))
        x += r * rnd.uniform(0.75, 1.15)
    fill = []
    x = x0 + rnd.uniform(1, 4)
    while x < x1 - 1:
        t = (x - x0) / span
        e = height * dome(t)
        r = max(3.0, e * rnd.uniform(0.42, 0.55))
        fill.append((x, foot - r * 0.6, r))
        x += r * rnd.uniform(0.8, 1.2)
    return fill + out


def cloud(p: Pix, puffs, foot, L="base", lo=1, hi=6, keep=None, gilt=True, night=False, x0=None, x1=None,
          flat=False) -> set:
    """A cloud of round puffs standing on row `foot`, each shaded as a ball lit from the upper left and falling into
    blue shade toward the cloud's flat foot, a puff in front casting its shade on the one behind; edged in its
    deepest blue along its foot and its far side and left soft against the sky, and gilded along the tops where
    heaven's light falls. `keep(x, y)`, when given, says which cells it may take; x0 and x1 trim it."""
    owner = {}
    top = min(cy - r for cx, cy, r in puffs) if puffs else foot
    for i, (cx, cy, r) in enumerate(puffs):
        for y in range(math.floor(cy - r), min(foot, math.ceil(cy + r) + 1)):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if (x0 is not None and x < x0) or (x1 is not None and x >= x1):
                    continue
                dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
                d2 = dx * dx + dy * dy
                if d2 > 1 or (keep is not None and not keep(x, y)):
                    continue
                z = math.sqrt(1 - d2) * r + cy * 0.4
                if (x, y) not in owner or owner[(x, y)][0] < z:
                    owner[(x, y)] = (z, i, dx, dy, math.sqrt(1 - d2))
    cells = set(owner)
    span = max(1.0, foot - top)
    for (x, y), (z, i, dx, dy, nz) in owner.items():
        q = owner.get((x - 1, y - 1)) or owner.get((x, y - 1))
        behind = q and q[1] != i and q[0] > z + 0.5
        if flat:
            # a long low cloud in the pixel artist's flat manner: a white body, a lit rim, its own shade under each
            # puff, the shade of a puff in front, and the blue gathering in the rows over its foot
            up = foot - y
            if (x, y - 1) not in owner:
                t = 3 if dx > 0.15 else 4                         # its edge against the sky, coolest on its far side
            elif (x, y - 2) not in owner:
                t = 6                                              # the lit rim just inside it
            elif up <= 1:
                t = 2
            elif behind or up <= 3:
                t = 3
            elif dy > 0.5:
                t = 4
            else:
                t = 5
        else:
            lam = max(0.0, dx * LX + dy * LY + nz * LZ)
            v = lo + (hi - lo + 0.5) * lam ** 1.25
            v -= 2.2 * max(0.0, (y - top) / span - 0.42)          # the shade gathering toward the foot
            if behind:
                v -= 1.4                                           # in the shade of the puff in front of it
            t = max(lo, min(hi, int(v + 0.5)))
        p.px(x, y, CLOUD[t], L)
    for (x, y) in cells:
        for ddx, ddy in ((1, 0), (0, 1), (-1, 0)):
            q = (x + ddx, y + ddy)
            if q in cells or q[1] >= foot:
                continue
            if ddy == 1 or ddx == 1:
                p.px(q[0], q[1], CLOUD[1] if not night else CLOUD[0], L)
    if gilt:
        for (x, y) in cells:
            if (x, y - 1) not in cells and owner[(x, y)][3] < -0.6 and -0.6 < owner[(x, y)][2] < 0.2:
                p.px(x, y, GOLD[6], L)
    return cells


# --------------------------------------------------------------------------- the pearly gates
def pillar(p: Pix, x, top, foot, w=6, L="base"):
    """A pillar of white marble, `w` wide, lit down its left side and shaded down its right, fluted, with a capital
    and a base of gilt."""
    for y in range(top + 3, foot - 2):
        for i in range(w):
            t = (i + 0.5) / w
            v = 6 - (0 if t < 0.25 else 1 if t < 0.5 else 2 if t < 0.8 else 3)
            if i in (2, w - 2) and (y + i) % 1 == 0 and v > 3:
                v -= 1
            p.px(x + i, y, PEARL[v], L)
        p.px(x - 1, y, PEARL[2], L)
        p.px(x + w, y, PEARL[1], L)
    for (yy, ext, tones_) in ((top, 1, (6, 5, 4, 2)), (top + 1, 1, (5, 4, 3, 1)), (top + 2, 0, (4, 4, 3, 1)),
                              (foot - 2, 1, (6, 5, 3, 1)), (foot - 1, 2, (5, 4, 3, 1))):
        a, b = x - ext - 1, x + w + ext
        for xx in range(a, b + 1):
            t = (xx - a) / max(1, b - a)
            k = tones_[0] if t < 0.2 else tones_[1] if t < 0.55 else tones_[2] if t < 0.85 else tones_[3]
            p.px(xx, yy, GOLD[k], L)


def pearly_gates(p: Pix, x, foot, w=44, h=58, night=False, motion=True, L="base"):
    """The pearly gates on their cloud, (x, foot) the foot of their left pillar: two marble pillars with gilt
    capitals under an arch of gold set with pearls, and between them the two leaves of a gate of gilt bars, scrolled
    at the top and studded with pearls where its rails cross, standing a little open on the light that pours through
    from beyond."""
    top = foot - h
    pw = 6
    gx0, gx1 = x + pw + 1, x + w - pw - 1           # the opening between the pillars
    mid = (gx0 + gx1) / 2
    r_out = (gx1 - gx0) / 2 + pw * 0.5 + 1
    arch_y = top + r_out                             # the arch springs from here
    # the light from beyond, behind everything of the gate
    inside = poly([(gx0, foot), (gx0, arch_y), (mid, arch_y - (gx1 - gx0) / 2), (gx1, arch_y), (gx1, foot)])
    inside |= {(xx, yy) for (xx, yy) in ellipse(mid, arch_y, (gx1 - gx0) / 2, (gx1 - gx0) / 2) if yy < arch_y}
    for (xx, yy) in inside:
        d = abs(xx + 0.5 - mid) / ((gx1 - gx0) / 2)
        p.px(xx, yy, C["white"] if d < 0.5 else (GOLD[6] if d < 0.85 else GOLD[5]), L)
    glow(p, mid, foot - h * 0.42, w * 0.75, h * 0.62, X["glory"], (0.1, 0.18, 0.28))
    # the gate's two leaves, swung a little open on their hinges, so the light pours through between them
    half = (gx1 - gx0) / 2
    leaf_w = max(5, int(half * 0.62))
    for side in (0, 1):
        lx0 = gx0 if side == 0 else gx1 - leaf_w
        bars = list(range(lx0, lx0 + leaf_w, 3)) if side == 0 else list(range(lx0 + leaf_w - 1, lx0 - 1, -3))
        for bx in bars:
            bar_top = int(arch_y - math.sqrt(max(0.0, half ** 2 - (bx + 0.5 - mid) ** 2)) + 3)
            for yy in range(bar_top, foot - 1):
                p.px(bx, yy, GOLD[3], L)
            p.px(bx, bar_top - 1, GOLD[5], L)
            p.px(bx, bar_top - 2, PEARL[6], L)
        hinge = lx0 if side == 0 else lx0 + leaf_w - 1
        for yy in range(int(arch_y) - 2, foot - 1):
            p.px(hinge, yy, GOLD[2], L)
        for ry in (int(arch_y + 3), int(foot - h * 0.33), foot - 4):
            for xx in range(lx0, lx0 + leaf_w):
                p.px(xx, ry, GOLD[5], L)
                p.px(xx, ry + 1, GOLD[1], L)
            for bx in bars:
                p.px(bx, ry, PEARL[6], L)
        sx = lx0 + leaf_w // 2 - 2
        sy = int((arch_y + 3 + foot - h * 0.33) / 2) - 2
        scroll = [".##.", "#..#", "#.##", ".#.."]
        p.sprite(sx, sy, scroll if side == 0 else [r[::-1] for r in scroll], {"#": GOLD[2]}, 1, L)
    # the light pouring out between the leaves and falling on the cloud before the gate
    beam = poly([(mid - half * 0.36, foot - 1), (mid + half * 0.36, foot - 1), (mid + half * 1.5, foot + 3),
                 (mid - half * 1.5, foot + 3)])
    for (xx, yy) in beam:
        p.apx(xx, yy, GOLD[6], 0.8, "pool")
    # the arch of gold set with pearls, springing from the pillars' capitals
    for (xx, yy) in ellipse(mid, arch_y, r_out, r_out):
        if yy > arch_y:
            continue
        d = math.hypot(xx + 0.5 - mid, yy + 0.5 - arch_y)
        if d >= r_out - 3.2:
            nx, ny = (xx + 0.5 - mid) / d, (yy + 0.5 - arch_y) / d
            lam = max(0.0, nx * LX + ny * LY + 0.55)
            band = d - (r_out - 3.2)
            k = 5 if band > 2.2 and lam > 0.7 else 4 if lam > 0.55 else 3 if lam > 0.3 else 2
            if band < 0.9:
                k -= 1
            p.px(xx, yy, GOLD[k], L)
    for i in range(11):
        a = math.pi * (i + 0.5) / 11
        px_, py_ = mid - math.cos(a) * (r_out - 1.6), arch_y - math.sin(a) * (r_out - 1.6)
        p.px(int(px_), int(py_), PEARL[6], L)
    keystone = [".aa.", "abba", "abbc", ".cc."]
    p.sprite(int(mid) - 2, int(arch_y - r_out) - 1, keystone, {"a": PEARL[6], "b": PEARL[4], "c": PEARL[2]}, 1, L)
    pillar(p, x, int(arch_y) - 3, foot, pw, L)
    pillar(p, x + w - pw, int(arch_y) - 3, foot, pw, L)


# --------------------------------------------------------------------------- the sea of cloud
def deck(p: Pix, x0, x1, foot, height: dict, seed=0, L="base") -> set:
    """Heaven's sea of cloud seen far off, lying low along a header's foot where its words leave little room: a
    deck of cloud standing on row `foot` and rising at each column x to no more than height[x] rows, its top
    rolling in long low swells, white where heaven's light lies along it and deepening through pearl to lavender
    toward its foot. Returns the cells it took."""
    rnd = random.Random(seed)
    a, b = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
    cells = set()
    for x in range(x0, x1):
        h = height.get(x, 0)
        if h < 2:
            continue
        swell = 0.5 + 0.32 * math.sin(x / 6.5 + a) + 0.18 * math.sin(x / 2.7 + b)
        top = foot - max(2, min(h, round(h * (0.55 + 0.45 * swell))))
        for y in range(top, foot):
            depth, up = y - top, foot - 1 - y
            c = C["white"] if depth == 0 else CLOUD[5] if depth == 1 else CLOUD[4]
            if up == 0:
                c = CLOUD[2]
            elif up == 1:
                c = CLOUD[3]
            p.px(x, y, c, L)
            cells.add((x, y))
    return cells
