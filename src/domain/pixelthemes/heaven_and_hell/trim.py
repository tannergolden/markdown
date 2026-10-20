# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The elements' trim, by day in heaven's gold, pearl and light and by night in hell's iron, bone and fire: the
cards' bands and what sits on their lids, the lights on the wires, the histogram's pillars, the dial's halo, the
counters' tablets, the releases along the time line, the faces of the people who made it, and the seal's sun."""
from __future__ import annotations

import math

from ...holidays.pixel import LX, LY, LZ, Pix, sphere, tube
from .palette import C, RAMP, X, step

GOLD, PEARL, LINEN, AZURE, ROSE = RAMP["gold"], RAMP["pearl"], RAMP["linen"], RAMP["azure"], RAMP["rose"]
LAVA, FIRE, IRON, BASALT, BONE, HIDE, HORN = (RAMP["lava"], RAMP["fire"], RAMP["iron"], RAMP["basalt"], RAMP["bone"],
                                              RAMP["hide"], RAMP["horn"])


def node_deco(p: Pix, night, x, y, w, h, seed, lid):
    """A card's own touch: a band of gilt (by night of glowing ember) down its icon cell's edge, and on a lid a
    little halo floating over it, or by night a pair of horns."""
    R = LAVA if night else GOLD
    for yy in range(y + 1, y + h - 1):
        p.px(x + 11, yy, R[5] if night else R[5])
        p.px(x + 12, yy, R[3])
        p.px(x + 13, yy, R[2] if night else R[2])
    if not lid:
        return
    cx = x + w // 2
    if night:
        horn = [".#.....#.", "#o.....o#", "o.......o"]
        p.sprite(cx - 4, y - 3, horn, {"#": HORN[5], "o": HORN[3]})
    else:
        ring = [".aaaaa.", "b.....c", ".ddddd."]
        p.sprite(cx - 3, y - 4, ring, {"a": GOLD[6], "b": GOLD[5], "c": GOLD[3], "d": GOLD[3]})


def wire_ink(night) -> str:
    return LAVA[3] if night else GOLD[2]


def wire_lights(p: Pix, cells, night, seed):
    """What the wires carry: little stars of gold every ninth pixel by day, embers by night, each drawn once."""
    for i, (x, y, d) in enumerate(cells[5:-7]):
        if i % 9:
            continue
        key = ("wirelight", night)
        if key not in p.syms:
            if night:
                cells_ = {(0, 0): FIRE[5], (1, 0): LAVA[4], (0, 1): LAVA[3], (-1, 0): LAVA[3] + ":0.6",
                          (0, -1): LAVA[4] + ":0.5"}
            else:
                cells_ = {(0, 0): C["white"], (1, 0): GOLD[5], (-1, 0): GOLD[5], (0, 1): GOLD[4], (0, -1): GOLD[6]}
            p.symbol(key, cells_)
        p.use(key, x, y)


def dashes(night) -> list:
    return [LAVA[3], IRON[4]] if night else [GOLD[3], AZURE[3]]


def ornament(kind: str, p: Pix | None, x, y, night) -> tuple:
    """A schematic's ornament in a free corner: a cherub on its cloud by day, an imp on its burning rock by night."""
    if kind != "schematic":
        return (0, 0)
    if p is None:
        return (18, 20)
    from . import small as SM
    if night:
        SM.imp_on_rock(p, x + 9, y + 19, k=0.8, motion=False)
        for i in range(18):
            p.px(x + i, y + 19, RAMP["basalt"][3] if i % 5 else LAVA[4])
    else:
        from .heaven import cloud
        cloud(p, [(x + 4, y + 19, 3.0), (x + 9, y + 18, 4.0), (x + 14, y + 19, 3.0)], y + 20)
        SM.cherub(p, x + 9, y + 17, k=0.75, motion=False)
    return (18, 20)


def hist_bar(p: Pix, bx, base, bw, v, night):
    """A week's commits as a pillar: by day of white marble with a capital of gold, lit down its left; by night of
    black stone, its top glowing like lava cooling."""
    R = BASALT if night else PEARL
    for xx in range(bx, bx + bw):
        nx = 2 * (xx - bx + 0.5) / bw - 1
        lam = max(0.0, nx * LX + (1 - nx * nx) ** 0.5 * LZ)
        lo, hi = (2, 5) if night else (2, 6)
        t = max(lo, min(hi, round(lo + (hi - lo) * lam * 1.3)))
        for yy in range(base - v, base):
            p.px(xx, yy, R[t])
    cap = (LAVA[5], LAVA[3]) if night else (GOLD[5], GOLD[3])
    if v >= 3:
        for xx in range(bx - 1, bx + bw + 1):
            p.px(xx, base - v, cap[0])
            if v >= 5:
                p.px(xx, base - v + 1, cap[1])
    if night and v >= 3:
        p.halo(bx + bw / 2, base - v, bw * 0.9 + 1, 2.2, X["heat"], (0.14, 0.26))


def peak_mark(p: Pix, x, y, night):
    if night:
        for dx, dy, c in ((1, 0, FIRE[6]), (1, -1, FIRE[5]), (0, -1, FIRE[4]), (2, -1, LAVA[4]), (1, -2, FIRE[4]),
                          (1, -3, LAVA[4])):
            p.px(x + dx, y + dy + 3, c)
    else:
        for dx, dy, c in ((1, 0, C["white"]), (0, 0, GOLD[5]), (2, 0, GOLD[5]), (1, -1, GOLD[6]), (1, 1, GOLD[4])):
            p.px(x + dx, y + dy + 2, c)


def dial_ring(p: Pix, arc, night):
    """The dial's half ring: a halo of gold by day, a ring of fire by night."""
    R = FIRE if night else GOLD

    def colour(s, o, lam, x, y):
        v = 2 + 3.6 * lam
        return R[max(2, min(6, round(v)))]
    tube(p, arc, 2.4, colour, outline=LAVA[1] if night else GOLD[1])


def dial_tick(p: Pix, x, y, night):
    p.px(x, y, C["white"] if not night else FIRE[6])
    p.px(x + 1, y, GOLD[3] if not night else LAVA[3])


def dial_hub(p: Pix, cx, cy, night):
    sphere(p, cx + 0.5, cy - 0.5, 2.6, BASALT if night else GOLD, lo=2)


def material(i: int, xx, yy, y0, y1, lift, night) -> str:
    """The wrappers of the bytes by file type: gold leaf, pearl, azure silk and rose by day; lava, iron, hide and
    smoke by night."""
    kinds = ((LAVA, 3), (IRON, 3), (HIDE, 3), (RAMP["smoke"], 4)) if night else ((GOLD, 4), (PEARL, 4), (AZURE, 3),
                                                                               (ROSE, 4))
    R, t = kinds[i % 4]
    if (xx + yy) % 5 == 0:
        t += 1
    return R[max(0, min(6, t + lift))]


def counter_cell(q: Pix, ox, oy, night):
    """A counter's blank tablet, 11 by 15: white marble lit along its left and top by day, black stone with a
    hot edge by night."""
    R = BASALT if night else PEARL
    for yy in range(15):
        for xx in range(11):
            if yy < 3 and (xx < 1 or xx > 9) and yy < 1:
                continue
            c = R[4] if night else R[5]
            if xx == 0 or yy == 0:
                c = (LAVA[3] if night else C["white"])
            elif xx == 10 or yy == 14:
                c = R[2]
            elif xx == 9 or yy == 13:
                c = R[3] if night else R[4]
            q.px(ox + xx, oy + yy, c)


def counter_ink(night, dim: bool) -> str:
    if night:
        return BASALT[2] if dim else C["ink_n"]
    return PEARL[2] if dim else C["ink"]


def timeline_line(p: Pix, x0, x1, y, night):
    """The line the releases hang from: a thread of gold by day, a chain of iron by night."""
    for x in range(x0, x1):
        if night:
            p.px(x, y, IRON[4] if (x // 2) % 2 else IRON[5])
            p.px(x, y + 1, IRON[2] if (x // 2) % 2 else IRON[1])
        else:
            p.px(x, y, GOLD[5])
            p.px(x, y + 1, GOLD[2])


def release(p: Pix, x, gy, kind, night, i=0):
    """A release on the line: by day a halo for a big one, a star of gold for a release, a pearl for a patch, a
    star not yet lit for one still to come and a feather for the day it was made; by night a skull, a flame, an
    ember, a coal not yet lit and a horn."""
    if night:
        if kind == "big":
            from .hell import skull
            skull(p, x - 3, gy + 1, motion=False)
        elif kind == "major":
            for dx, dy, c in ((0, 4, FIRE[6]), (0, 3, FIRE[5]), (-1, 4, FIRE[4]), (1, 4, FIRE[4]), (0, 2, FIRE[4]),
                              (-1, 3, LAVA[4]), (1, 2, LAVA[4]), (0, 1, LAVA[4])):
                p.px(x + dx, gy + 1 + dy, c)
        elif kind == "minor":
            p.px(x, gy + 2, FIRE[5])
            p.px(x - 1, gy + 2, LAVA[3])
            p.px(x, gy + 3, LAVA[3])
        elif kind == "made":
            p.sprite(x - 2, gy + 1, ["#....", "#o...", ".#o..", "..##.", "...##"], {"#": HORN[5], "o": HORN[3]})
        else:
            p.sprite(x - 1, gy + 1, [".o.", "o.o", ".o."], {"o": BASALT[4]})
        return
    if kind == "big":
        ring = [".aaaaa.", "a.....c", ".ccccc."]
        p.sprite(x - 3, gy + 1, ring, {"a": GOLD[6], "c": GOLD[3]})
        p.halo(x + 0.5, gy + 2.5, 5, 3, X["glory"], (0.2, 0.36))
    elif kind == "major":
        p.sprite(x - 2, gy + 1, ["..a..", ".abc.", "abbcd", ".b.d."], {"a": GOLD[6], "b": GOLD[5], "c": GOLD[4],
                                                                     "d": GOLD[2]})
    elif kind == "minor":
        p.sprite(x - 1, gy + 1, ["ab", "bc"], {"a": C["white"], "b": PEARL[4], "c": PEARL[2]})
    elif kind == "made":
        p.sprite(x - 2, gy + 1, ["...ab", "..abc", ".abc.", "abc..", "c...."], {"a": C["white"], "b": LINEN[4],
                                                                               "c": LINEN[2]})
    else:
        p.sprite(x - 2, gy + 1, ["..o..", ".o.o.", "o...o", ".o.o."], {"o": GOLD[3]})


def today_mark(p: Pix, x, y, night):
    if night:
        for dx, dy, c in ((0, 0, FIRE[6]), (0, -1, FIRE[5]), (-1, 0, FIRE[4]), (1, 0, LAVA[4]), (0, -2, LAVA[4])):
            p.px(x + dx, y + dy - 1, c)
    else:
        p.px(x, y - 1, C["white"])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p.px(x + dx, y - 1 + dy, GOLD[5])


SKINS = ("skin0", "skin1", "skin2")


def avatar(p: Pix, cx, cy, i, person, night):
    """A contributor as one of the host: by day a face under a halo, by night a face of red hide under horns, the
    initials over it; a bot is a dove by day and an imp by night."""
    from . import small as SM
    if not person.get("initials"):
        key = SM.imp_symbol(p, 0) if night else SM.dove_symbol(p, 0)
        p.use(key, cx - 5, cy - 4)
        return
    R = HIDE if night else RAMP[SKINS[i % 3]]
    sphere(p, cx + 0.5, cy + 0.5, 7.2, R, lo=1, hi=5 if night else 5)
    ini = str(person["initials"])[:2]
    ink = C["white"] if (night or i % 3 == 2) else C["ink"]
    p.text(cx - 3, cy - 1, ini, ink, "35", shadow=R[1])
    if night:
        horn = [".#.......#.", "#o.......o#", "o.........o"]
        p.sprite(cx - 5, cy - 10, horn, {"#": HORN[5], "o": HORN[3]})
    else:
        ring = ["..aaaaaaa..", ".a.......c.", "..ccccccc.."]
        p.sprite(cx - 5, cy - 11, ring, {"a": GOLD[6], "c": GOLD[3]})
        p.halo(cx + 0.5, cy - 10, 7, 2.6, X["glory"], (0.2, 0.34))


def commit_bar(p: Pix, x, y, w, fill, night):
    """A contributor's share: a bar of gold by day, of fire by night."""
    R = FIRE if night else GOLD
    p.box(x, y, w + 2, 4, LAVA[2] if night else GOLD[2])
    for xx in range(fill):
        p.px(x + 1 + xx, y + 1, R[5])
        p.px(x + 1 + xx, y + 2, R[3])


def rosette(p: Pix, cx, cy, r0, r1, n, night):
    """The ring round the certificate's seal: a sun of gold rays by day, a ring of flames by night."""
    k = 0
    step_a = 2 * math.pi / n
    R = FIRE if night else GOLD
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 1):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not r0 - 0.5 <= rho <= r1:
                continue
            th = math.atan2(dy, dx)
            j = round(th / step_a)
            off = th - j * step_a
            f = (rho - r0) / (r1 - r0)
            half = step_a * (0.42 * (1 - f) + 0.06) if not night else step_a * (0.45 * (1 - f * f) + 0.03)
            if abs(off) > half:
                continue
            ang = j * step_a
            facing = math.cos(ang) * LX + math.sin(ang) * LY
            if night:
                t = 6 if f < 0.25 else 5 if f < 0.5 else 4 if f < 0.75 else 3
            else:
                t = max(2, min(6, round(3.5 + 2.4 * facing - 1.2 * f)))
            p.px(x, y, R[t + k])


def seal_mark(p: Pix, x, y, night):
    if night:
        p.sprite(x, y, ["#...#", "o...o", ".o.o."], {"#": HORN[5], "o": HORN[3]})
    else:
        p.sprite(x, y, [".aaa.", "a...c", ".ccc."], {"a": GOLD[6], "c": GOLD[3]})


def placard_mark(p: Pix, x, y, night):
    if night:
        from .hell import skull
        skull(p, x, y, motion=False)
    else:
        p.sprite(x, y, ["....ab", "...abc", "..abc.", ".abc..", "abc...", "c....."], {"a": C["white"], "b": LINEN[4],
                                                                                     "c": LINEN[2]})


def badge_top(p: Pix, w, s, seed, night, inside):
    """Along a badge's top edge, inside its shape: a string of pearls by day, a seam of embers by night."""
    for x in range(2, w - 2):
        if not inside(x, 1, w, s["h"], s["corner"]):
            continue
        if night:
            if (x * 7 + seed) % 5 == 0:
                p.px(x, 1, LAVA[4])
        elif x % 3 == 0:
            p.px(x, 1, PEARL[6])
