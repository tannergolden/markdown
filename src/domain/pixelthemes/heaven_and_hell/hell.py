# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Hell, by night: its fires, its gates and their braziers, and its river of lava under a far bank of black rock
backlit by the red of the fires along the horizon. Hell has no sky to light it: everything here is lit by its own
fires, from below and from within."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Pix
from .kit import ellipse, glow, poly
from .palette import RAMP, X

LAVA, FIRE, BASALT, IRON, SCORCH = RAMP["lava"], RAMP["fire"], RAMP["basalt"], RAMP["iron"], RAMP["scorch"]
BONE, SMOKE = RAMP["bone"], RAMP["smoke"]


# --------------------------------------------------------------------------- fire
FLAME = [
    # a tall flame, 7 wide, its tones on the fire ramp: 6 the white heart, 1 its dark red tip
    "...1...",
    "..12...",
    "..232..",
    ".1343..",
    ".23432.",
    "1345431",
    "2456542",
    "3456653",
    "3566654",
    ".45665.",
    "..454..",
]
FLAME2 = [
    "....1..",
    "...12..",
    "..232..",
    "..3431.",
    ".23453.",
    "1345542",
    "2456642",
    "3456653",
    "3566654",
    ".45665.",
    "..454..",
]


def _scaled(art, s):
    h, w = len(art), len(art[0])
    hh, ww = max(3, round(h * s)), max(3, round(w * s))
    return ["".join(art[min(h - 1, int(j * h / hh))][min(w - 1, int(i * w / ww))] for i in range(ww)) for j in range(hh)]


def flame(p: Pix, cx, foot, s=1.0, phase=0, motion=True, L=None, halo=True, back=False):
    """A flame standing on row `foot`, centred on column `cx`, about `s` times its size, flickering on one of the
    engine's three phases (behind what stands before it, with `back`), a glow round it unless a fire it is part of
    has one glow for all its flames (`halo`). Each shape and size of flame is drawn once and placed as often as it
    burns, on whichever phase it flickers."""
    s = max(0.4, round(s * 5) / 5)
    ph = phase % 3
    variant = phase % 2
    rows = _scaled(FLAME if variant == 0 else FLAME2, s)
    w, h = len(rows[0]), len(rows)
    key = ("flame", variant, s)
    if key not in p.syms:
        p.symbol(key, {(i - w // 2, j - h): FIRE[int(ch)] for j, r in enumerate(rows) for i, ch in enumerate(r)
                       if ch != "."})
    Lf = L or (p.flicker(ph, back=back) if motion else ("far" if back else "base"))
    p.use(key, int(cx), int(foot), Lf)
    if halo:
        glow(p, int(cx) + 0.5, foot - h * 0.45, w * 1.1 + 2, h * 0.8 + 2, X["heat"], (0.1, 0.2, 0.3),
             L=p.flicker(ph, back=True) if motion else "haze", shape=True)
    p.lamps.append((cx + 0.5, foot - h * 0.4, 9 + 6 * s, ph))


def brazier(p: Pix, cx, top, phase=0, motion=True, L="base"):
    """An iron brazier, its bowl on a stem, a fire burning in it."""
    bowl = ["#########", ".#ooooo#.", "..#ooo#..", "...###...", "....#...."]
    p.sprite(cx - 4, top, bowl, {"#": IRON[4], "o": IRON[2]}, 1, L)
    p.px(cx - 4, top, IRON[5], L)
    for i in range(9):
        p.px(cx - 4 + i, top - 1, LAVA[4] if i % 2 else FIRE[5], L)
    flame(p, cx, top, s=1.0, phase=phase, motion=motion)


# --------------------------------------------------------------------------- the gates of hell
def stones(p: Pix, x, top, foot, w, L="base", seed=0):
    """A pillar of black stone blocks, its joints glowing faintly with the heat."""
    rnd = random.Random(seed)
    y = foot - 1
    course = 0
    while y > top:
        hgt = rnd.randint(4, 6)
        for yy in range(max(top, y - hgt + 1), y + 1):
            for i in range(w):
                edge_ = i == 0
                c = BASALT[4] if edge_ else BASALT[3] if i < w // 2 else BASALT[2]
                if yy == y - hgt + 1:
                    c = BASALT[5] if i < w - 1 else BASALT[3]
                p.px(x + i, yy, c, L)
            p.px(x + w - 1, yy, BASALT[1], L)
        joint = y - hgt
        if joint > top:
            for i in range(w):
                p.px(x + i, joint, SCORCH[3], L)
        y = joint
        course += 1


def hell_gates(p: Pix, x, foot, w=44, h=58, motion=True, L="base"):
    """The gates of hell on their crag, (x, foot) the foot of their left pillar, the twin of the pearly gates: two
    pillars of black stone each crowned with a brazier, an arch of stone over them with a skull for its keystone,
    and between them two leaves of iron bars, speared at the top, standing a little open on the fire beyond."""
    top = foot - h
    pw = 6
    gx0, gx1 = x + pw + 1, x + w - pw - 1
    mid = (gx0 + gx1) / 2
    half = (gx1 - gx0) / 2
    r_out = half + pw * 0.5 + 1
    arch_y = top + r_out + 4
    inside = poly([(gx0, foot), (gx0, arch_y), (gx1, arch_y), (gx1, foot)])
    inside |= {(xx, yy) for (xx, yy) in ellipse(mid, arch_y, half, half) if yy < arch_y}
    # the fire beyond, as one shape behind the bars: the dark of its smoke above, its red glow below
    low = (arch_y - half) + 0.55 * (foot - (arch_y - half))
    r = half + 0.6
    p.shapes[L].append(f'<path fill="{LAVA[1]}" d="M{gx0} {foot}V{arch_y:.1f}A{r:.1f} {r:.1f} 0 0 1 {gx1} {arch_y:.1f}'
                       f'V{foot}Z"/><rect x="{gx0}" y="{int(low)}" width="{gx1 - gx0}" height="{foot - int(low)}" '
                       f'fill="{LAVA[2]}"/>')
    rnd = random.Random(int(x) * 7 + 3)
    room = foot - (arch_y - half) - 3
    fx, i = gx0 + 3, 0
    sizes = (min(1.2, room / 11), min(1.6, room / 11))
    while fx < gx1 - 2:
        flame(p, fx, foot - 1, s=sizes[i % 2], phase=i, motion=motion, halo=False)
        fx += rnd.randint(4, 6)
        i += 1
    glow(p, mid, foot - h * 0.35, w * 0.7, h * 0.55, X["heat"], (0.08, 0.15, 0.24))
    leaf_w = max(5, int(half * 0.62))
    for side in (0, 1):
        lx0 = gx0 if side == 0 else gx1 - leaf_w
        bars = list(range(lx0, lx0 + leaf_w, 3)) if side == 0 else list(range(lx0 + leaf_w - 1, lx0 - 1, -3))
        for bx in bars:
            bar_top = int(arch_y - math.sqrt(max(0.0, half ** 2 - (bx + 0.5 - mid) ** 2)) + 4)
            for yy in range(bar_top, foot - 1):
                p.px(bx, yy, IRON[1], L)
            spear = ((0, -1, IRON[3]), (0, -2, IRON[4]), (0, -3, IRON[5]), (-1, -1, IRON[2]), (1, -1, IRON[1]))
            for dx, dy, c in spear:
                p.px(bx + dx, bar_top + dy, c, L)
        hinge = lx0 if side == 0 else lx0 + leaf_w - 1
        for yy in range(int(arch_y) - 2, foot - 1):
            p.px(hinge, yy, IRON[2], L)
        for ry in (int(arch_y + 4), int(foot - h * 0.33), foot - 4):
            for xx in range(lx0, lx0 + leaf_w):
                p.px(xx, ry, IRON[3], L)
                p.px(xx, ry + 1, IRON[0], L)
    # the arch of rough black stone, its voussoirs' joints glowing, a skull its keystone
    for (xx, yy) in ellipse(mid, arch_y, r_out, r_out):
        if yy > arch_y:
            continue
        d = math.hypot(xx + 0.5 - mid, yy + 0.5 - arch_y)
        if d >= r_out - 3.4:
            a = math.atan2(yy + 0.5 - arch_y, xx + 0.5 - mid)
            joint = int((a + math.pi) / (math.pi / 9)) != int((a + math.pi + 0.06) / (math.pi / 9))
            band = d - (r_out - 3.4)
            c = SCORCH[4] if joint else (BASALT[4] if band > 2.4 else BASALT[3] if band > 1.2 else BASALT[2])
            p.px(xx, yy, c, L)
    skull(p, int(mid) - 3, int(arch_y - r_out) - 2, motion=motion, L=L)
    stones(p, x, int(arch_y) - 3, foot, pw, L, seed=1)
    stones(p, x + w - pw, int(arch_y) - 3, foot, pw, L, seed=2)
    brazier(p, x + pw // 2, int(arch_y) - 8, phase=0, motion=motion)
    brazier(p, x + w - pw + pw // 2 - 1, int(arch_y) - 8, phase=1, motion=motion)


SKULL = [
    ".abbbc.",
    "abbbbbc",
    "beeceec",
    "beeceec",
    "bbbcbbd",
    ".bcccd.",
    ".c.c.d.",
]


def skull(p: Pix, x, y, motion=True, L="base", eyes=True):
    """A skull, 7 by 7, lit from below by the fire, its sockets burning."""
    pal = {"a": BONE[6], "b": BONE[5], "c": BONE[3], "d": BONE[2], "e": BASALT[0]}
    p.sprite(x, y, SKULL, pal, 1, L)
    if eyes:
        Lb = p.flicker(2) if motion else L
        for (ex, ey) in ((x + 1, y + 3), (x + 4, y + 3)):
            p.px(ex + 1, ey, FIRE[5], Lb)
            p.px(ex, ey, LAVA[4], Lb)


# --------------------------------------------------------------------------- light by night
HIDE_SET = set(RAMP["hide"])
LIT = set(BASALT) | set(IRON) | set(SCORCH) | set(BONE) | set(SMOKE) | set(RAMP["hide"]) | set(RAMP["horn"]) \
    | set(RAMP["membrane"])


def firelight(p: Pix):
    """Each fire's light laid into what stands near it, once everything is drawn: within its reach the rock, the
    iron, the bone and the demons' hide are a tone lighter on their own ramps, two in the near half of it."""
    from .palette import step
    base = p.layers["base"]
    for (cx, cy, r, phase) in p.lamps:
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y))
                if c is None or c not in LIT:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.2) / r
                if d >= 1:
                    continue
                lit = step(c, 2 if d < 0.45 else 1)
                if c in HIDE_SET and RAMP["hide"].index(lit) > 4:
                    lit = RAMP["hide"][4]                   # firelight warms the hide; it never blanches it
                base[(x, y)] = lit
    p.lamps = []


# --------------------------------------------------------------------------- the river of lava
def far_bank(p: Pix, x0, x1, surface, height: dict, seed=0, L="base", lite=False) -> set:
    """Hell's far bank, lying low along a header's foot where its words leave little room, the twin of heaven's
    deck of cloud: black rock standing on row `surface` and rising at each column x to no more than height[x]
    rows, in broken shoulders and short spires, lit red from below where the lava glows on it, black above and
    edged along its top by the red of the fires behind it. Returns the cells it took."""
    rnd = random.Random(seed)
    tops = {}
    x = x0 - rnd.uniform(0, 8)
    while x < x1 + 2:
        spire = rnd.random() < 0.3
        w = rnd.uniform(4, 8) if spire else rnd.uniform(10, 24)
        a, b = rnd.uniform(0.45, 0.75), rnd.uniform(0.45, 0.75)
        peak = rnd.uniform(0.9, 1.0) if spire else rnd.uniform(0.75, 0.95)
        for xx in range(math.floor(x), math.ceil(x + w)):
            if not x0 <= xx < x1:
                continue
            t = min(1.0, max(0.0, (xx + 0.5 - x) / w))
            if spire:
                f = peak * (1 - abs(2 * t - 1)) ** 0.8
            else:
                f = a + (b - a) * t + (peak - max(a, b)) * math.sin(math.pi * t) ** 0.5
            tops[xx] = min(tops.get(xx, surface), surface - max(0, int(round(f * height.get(xx, 0)))))
        x += w * (0.7 if spire else 0.85)
    cells = {(xx, y) for xx, top in tops.items() for y in range(top, surface)}
    for (xx, y) in cells:
        up = surface - 1 - y
        if (xx, y - 1) not in cells:
            c = LAVA[3] if not lite else SCORCH[5]                 # its edge, caught by the fires behind it
        elif (xx, y - 2) not in cells and not lite:
            c = SCORCH[2]
        elif up == 0:
            c = SCORCH[5]
        elif up == 1:
            c = SCORCH[3]
        elif up == 2:
            c = SCORCH[1]
        else:
            c = BASALT[0]
        p.px(xx, y, c, L)
    return cells


def lava_river(p: Pix, x0, x1, foot, room: dict, depth=3, seed=0, L="base", lite=False, motion=True):
    """A river of lava `depth` rows deep along the foot from column x0 to x1, as deep at each column as room[x]
    lets it run: white-hot in streaks along its top, darker below, crusting black in plates, and glowing up into
    the dark over it and on the fires' red along the horizon behind it. A drawing made lighter leaves out the
    streaks and the crust."""
    rnd = random.Random(seed)
    surface = foot - depth
    deep = {xx for xx in range(x0, x1) if room.get(xx, 0) >= depth}
    for d in range(depth):
        y = surface + d
        run = [xx for xx in range(x0, x1) if room.get(xx, 0) >= foot - y]
        for a, b in _runs(run):
            p.hline(a, b, y, (LAVA[5], LAVA[4], LAVA[3], LAVA[2])[min(d, 3)], L)
    if not lite and deep:
        x = x0 + rnd.randint(0, 6)
        while x < x1 - 2:
            w = rnd.randint(3, 8)
            for a, b in _runs([xx for xx in range(x, min(x1, x + w)) if xx in deep]):
                p.hline(a, b, surface, LAVA[6], L)                 # a streak running fast and hot
            x += w + rnd.randint(8, 16)
        x = x0 + rnd.randint(2, 10)
        while x < x1 - 3:
            w = rnd.randint(3, 7)
            for a, b in _runs([xx for xx in range(x, min(x1, x + w)) if xx in deep]):
                p.hline(a, b, surface + 1, BASALT[3], L)           # a plate of crust
                if b - a > 2:
                    p.hline(a + 1, b - 1, surface + 2, LAVA[1], L)
            x += w + rnd.randint(9, 18)
    glow(p, (x0 + x1) / 2, surface + 0.5, (x1 - x0) / 2 + 4, 7, X["heat"], (0.08, 0.15),
         L=p.flicker(seed % 3, back=True) if motion else "haze", shape=True)


def horizon(p: Pix, x0, x1, surface, rows):
    """The red of the fires along hell's horizon, `rows` deep over row `surface`: what its rock stands black
    against."""
    for i, a in enumerate((0.07, 0.07, 0.09)):
        top = surface - rows + i * rows // 3
        p.under.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{surface - top}" fill="{X["heat"]}" '
                       f'fill-opacity="{a}"/>')


def _runs(xs) -> list:
    """Runs of consecutive columns in `xs`, as (start, end) with the end one past the last."""
    out = []
    for x in sorted(xs):
        if out and out[-1][1] == x:
            out[-1][1] = x + 1
        else:
            out.append([x, x + 1])
    return [tuple(r) for r in out]
