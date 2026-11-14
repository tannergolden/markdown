# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The elements' trim, from the laboratory: cards banded in enamel and riveted, a warning lamp on each lid, signals
on the wires, the histogram's weeks as test tubes filled with the jar's fluid, a gauge in a bezel of brass, the
counters' digits in nixie tubes, the releases along a cable, the people who made it behind portholes, the seal ringed
by a gear, and the placard a riveted plate."""
from __future__ import annotations

import math

from ...holidays.pixel import LX, Pix, sphere, tube
from .palette import C, RAMP

FLUID, ENAMEL, BRASS, STEEL, NIXIE, ARC, TISSUE, SAGE, ROOM = (RAMP["fluid"], RAMP["enamel"], RAMP["brass"],
                                                              RAMP["steel"], RAMP["nixie"], RAMP["arc"],
                                                              RAMP["tissue"], RAMP["sage"], RAMP["room"])


def node_deco(p: Pix, night, x, y, w, h, seed, lid):
    """A card's own touch: a band of enamel riveted down its icon cell's edge, and on a lid a warning lamp."""
    for yy in range(y + 1, y + h - 1):
        rivet = (yy - y) % 5 == 2
        p.px(x + 11, yy, (BRASS[5] if not night else NIXIE[4]) if rivet else (ENAMEL[4] if not night else ENAMEL[2]))
        p.px(x + 12, yy, ENAMEL[3] if not night else ENAMEL[1])
        p.px(x + 13, yy, ENAMEL[2] if not night else ENAMEL[0])
    if not lid:
        return
    cx = x + w // 2
    lit = (TISSUE[4], TISSUE[6]) if not night else (NIXIE[4], NIXIE[6])
    p.sprite(cx - 2, y - 3, [".ab..", "aabb.", "ccccc"], {"a": lit[0], "b": lit[1], "c": STEEL[3] if not night else
                                                         STEEL[2]})


def wire_ink(night) -> str:
    return FLUID[3] if night else STEEL[3]


def wire_lights(p: Pix, cells, night, seed):
    """What the wires carry: a signal every ninth pixel, amber by day and the fluid's light by night."""
    for i, (x, y, d) in enumerate(cells[5:-7]):
        if i % 9:
            continue
        key = ("wirelight", night)
        if key not in p.syms:
            R = FLUID if night else NIXIE
            p.symbol(key, {(0, 0): C["white"], (1, 0): R[5], (-1, 0): R[5], (0, 1): R[4], (0, -1): R[4]})
        p.use(key, x, y)


def dashes(night) -> list:
    return [FLUID[3], NIXIE[3]] if night else [ENAMEL[3], BRASS[3]]


ORNAMENT_K = 0.12   # the scale of the brain in a schematic's little jar


def ornament(kind: str, p: Pix | None, x, y, night) -> tuple:
    """A schematic's ornament in a free corner: the brain in a little jar, a cell clear of it all round."""
    if kind != "schematic":
        return (0, 0)
    from . import lab as LB
    w, h = LB.little_size(ORNAMENT_K)
    if p is not None:
        LB.little_jar(p, x + 1, y + 1, night, ORNAMENT_K)
    return (w + 2, h + 2)


def hist_bar(p: Pix, bx, base, bw, v, night):
    """A week's commits as a test tube filled to its count with the jar's fluid, a meniscus at its top."""
    top = base - v
    for yy in range(top - 1, base):
        for xx in range(bx - 1, bx + bw + 1):
            wall = xx in (bx - 1, bx + bw)
            if wall:
                p.px(xx, yy, STEEL[4] if not night else STEEL[2])
            elif yy >= top:
                f = (xx - bx) / max(1, bw - 1)
                c = (FLUID[5] if f < 0.3 else FLUID[4] if f < 0.75 else FLUID[3]) if not night else (
                    FLUID[5] if f < 0.3 else FLUID[4])
                p.px(xx, yy, c)
    if v >= 2:
        for xx in range(bx, bx + bw):
            p.px(xx, top, FLUID[6])
    for xx in range(bx - 1, bx + bw + 1):
        p.px(xx, base, STEEL[2] if not night else STEEL[1])
    if night and v >= 3:
        p.halo(bx + bw / 2, top, bw * 0.9 + 1, 2.2, FLUID[3], (0.14, 0.24))


def peak_mark(p: Pix, x, y, night):
    R = FLUID
    for dx, dy, c in ((1, 0, C["white"]), (0, 0, R[5]), (2, 0, R[5]), (1, -1, R[6]), (1, 1, R[4])):
        p.px(x + dx, y + dy + 2, c)


def dial_ring(p: Pix, arc, night):
    """The gauge's half ring: a bezel of brass."""
    def colour(s, o, lam, x, y):
        v = 2 + 3.6 * lam
        return BRASS[max(2, min(6, round(v)))] if not night else BRASS[max(1, min(4, round(v) - 1))]
    tube(p, arc, 2.4, colour, outline=BRASS[1] if not night else BRASS[0])


def dial_tick(p: Pix, x, y, night):
    p.px(x, y, C["white"] if not night else NIXIE[5])
    p.px(x + 1, y, STEEL[3])


def dial_hub(p: Pix, cx, cy, night):
    sphere(p, cx + 0.5, cy - 0.5, 2.6, BRASS, lo=2)


def material(i: int, xx, yy, y0, y1, lift, night) -> str:
    """The wrappers of the bytes by file type: the brain's tissue, the jar's fluid, brass and enamel."""
    kinds = ((TISSUE, 3), (FLUID, 4), (BRASS, 4), (ENAMEL, 4))
    R, t = kinds[i % 4]
    if night:
        t -= 1
    if (xx + yy) % 5 == 0:
        t += 1
    return R[max(0, min(6, t + lift))]


def counter_cell(q: Pix, ox, oy, night):
    """A counter's digit in a nixie tube, 11 by 15: dark glass in a socket of steel, its mesh faint across it."""
    for yy in range(15):
        for xx in range(11):
            top = yy < 2 and xx in (0, 10)
            if top:
                continue
            c = ROOM[2] if (xx + yy) % 3 else ROOM[3]
            if xx in (0, 10) or yy == 0:
                c = STEEL[4] if not night else STEEL[2]
            elif yy == 14:
                c = STEEL[2] if not night else STEEL[1]
            q.px(ox + xx, oy + yy, c)


def counter_ink(night, dim: bool) -> str:
    return NIXIE[1] if dim else (NIXIE[4] if not night else NIXIE[5])


def timeline_line(p: Pix, x0, x1, y, night):
    """The line the releases hang from: a cable, clipped every so often."""
    for x in range(x0, x1):
        p.px(x, y, STEEL[1] if not night else ROOM[0])
        p.px(x, y + 1, STEEL[3] if not night else STEEL[1])
        if x % 12 == 0:
            p.px(x, y, BRASS[4] if not night else BRASS[2])


def release(p: Pix, x, gy, kind, night, i=0):
    """A release on the line: a little jar for a big one, a lamp lit for a release, a rivet for a patch, a lamp not
    yet lit for one still to come, and a flask for the day it was made."""
    if kind == "big":
        from . import lab as LB
        LB.tiny_jar(p, x - len(LB.TINY_JAR[0]) // 2, gy + 1, night)
    elif kind == "major":
        lit = NIXIE[5] if night else BRASS[5]
        p.sprite(x - 2, gy + 1, [".aaa.", "abbba", "abcba", ".aba.", "..d.."], {"a": STEEL[3], "b": lit, "c": C["white"],
                                                                             "d": STEEL[2]})
    elif kind == "minor":
        p.sprite(x - 1, gy + 1, ["ab", "bc"], {"a": BRASS[6], "b": BRASS[4], "c": BRASS[2]})
    elif kind == "made":
        p.sprite(x - 2, gy + 1, [".#.#.", ".#.#.", "#ooo#", "#ooo#", ".###."], {"#": STEEL[4], "o": FLUID[4]})
    else:
        p.sprite(x - 2, gy + 1, [".aaa.", "a...a", "a...a", ".a.a."], {"a": STEEL[3]})


def today_mark(p: Pix, x, y, night):
    R = ARC
    p.px(x, y - 1, C["white"])
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y - 1 + dy, R[5])


def avatar(p: Pix, cx, cy, i, person, night):
    """A contributor behind a porthole: a ring of brass, the glass tinted, the initials on it; a bot is a little
    gear."""
    if not person.get("initials"):
        p.sprite(cx - 3, cy - 3, ["..#.#..", ".#####.", "##.#.##", ".#...#.", "##.#.##", ".#####.", "..#.#.."],
                 {"#": STEEL[4] if not night else STEEL[3]})
        return
    R = (FLUID, ENAMEL, TISSUE)[i % 3]
    sphere(p, cx + 0.5, cy + 0.5, 7.2, R, lo=1 if not night else 1, hi=4)
    for a in range(0, 360, 8):
        x = cx + 0.5 + 7.6 * math.cos(math.radians(a))
        y = cy + 0.5 + 7.6 * math.sin(math.radians(a))
        lit = math.cos(math.radians(a)) * LX + math.sin(math.radians(a)) * -0.6 < 0
        p.px(math.floor(x), math.floor(y), (BRASS[5] if lit else BRASS[2]) if not night else (BRASS[3] if lit else
                                                                                             BRASS[1]))
    ini = str(person["initials"])[:2]
    p.text(cx - 3, cy - 1, ini, C["white"], "35", shadow=R[1])


def commit_bar(p: Pix, x, y, w, fill, night):
    """A contributor's share: a tube filled with the jar's fluid."""
    p.box(x, y, w + 2, 4, STEEL[3] if not night else STEEL[2])
    for xx in range(fill):
        p.px(x + 1 + xx, y + 1, FLUID[5])
        p.px(x + 1 + xx, y + 2, FLUID[3])


def rosette(p: Pix, cx, cy, r0, r1, n, night):
    """The ring round the certificate's seal: the teeth of a gear of brass."""
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 1):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            tooth = (th / (2 * math.pi) * n) % 1 < 0.5
            outer = r1 if tooth else r0 + (r1 - r0) * 0.45
            if r0 - 0.5 <= rho <= outer:
                facing = math.cos(th) * LX + math.sin(th) * -0.6
                t = 5 if facing < -0.3 else 4 if facing < 0.3 else 2
                p.px(x, y, BRASS[t] if not night else BRASS[max(1, t - 2)])


def seal_mark(p: Pix, x, y, night):
    p.sprite(x, y, [".###.", "#aba#", ".###."], {"#": TISSUE[1], "a": TISSUE[4], "b": TISSUE[5]})


def placard_mark(p: Pix, x, y, night):
    p.sprite(x, y, ["..#.#.", "..#.#.", ".#...#", "#ooooo#", "#oOooo#", ".#####."][:6],
             {"#": STEEL[4] if not night else STEEL[3], "o": FLUID[4], "O": C["white"]})


def badge_top(p: Pix, w, s, seed, night, inside):
    """Along a badge's top edge, inside its shape: rivets."""
    for x in range(2, w - 2):
        if inside(x, 1, w, s["h"], s["corner"]) and x % 6 == 0:
            p.px(x, 1, BRASS[6] if not night else NIXIE[4])


def placard_board(p: Pix, night):
    """A placard as a plate of steel riveted to the wall, the wall inside it as on every sheet: lit along its top
    and left, a rivet of brass at each corner and along each side, and caged lamps hung along its top, laid in
    pixels so the owner's tag stands in front of them."""
    from . import sheet as S
    S.paper(p, night, uid="pl")
    w, h = p.w, p.h
    for y in range(h):
        for x in range(w):
            sides = {0: y, 1: x, 2: h - 1 - y, 3: w - 1 - x}
            side = min(sides, key=sides.get)
            across = sides[side]
            if across > 3:
                continue
            along = x if side in (0, 2) else y
            lit = side in (0, 1)
            if night:
                c = (STEEL[0], STEEL[3] if lit else STEEL[1], STEEL[2], STEEL[1])[across]
                if across == 2 and along % 8 == 4:
                    c = NIXIE[4]
            else:
                c = (STEEL[1], STEEL[5] if lit else STEEL[3], STEEL[4], STEEL[2])[across]
                if across == 2 and along % 8 == 4:
                    c = BRASS[5]
            p.px(x, y, c)
    S.festoon(p, 86, 150, 4, night, sag=3, span=32, pixels=True)
