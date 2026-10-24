# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Architect set's six elements, drawn on the shared pixel canvas: the room of screens carried into every chart.

A schematic's cards are monitors in the frame's pale plastic, a charcoal band down the edge of each one's icon with its
power light burning green and a pair of rabbit ears on every third one's lid; its wires are black cables with tally
lights along them, its groups bordered in phosphor and charcoal, and a set showing the white rabbit stands in a free
corner. The instruments stand each week's commits as a level meter, a column of little tubes lit in the phosphor to
its count, mark the busiest with a spark, bend a charcoal bezel over the dial on a brass knob, show the bytes by file
type as what a screen shows (the code falling, a test card, snow, scanlines and the white room's wall), and cut every
count into a little tube, its numeral glowing. The milestones run along a cable, every release a set on it with its
picture on, a big one a set showing the code, a patch a tally light and one still to come a set switched off; the pen
stands at today. The roster shows each contributor on a set, their initials glowing on it, a bot's set lost to snow,
over a level meter; the certificate's seal is ringed in a test card's rings with the white rabbit at its foot; and
the placard is a panel of the white room in the frame of little sets, its power light burning in its corner."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Pix, sphere, tube
from . import art as A
from .palette import RAMP, step

WALL, DUSK, PLASTIC, GLASS, SHELL = RAMP["wall"], RAMP["dusk"], RAMP["plastic"], RAMP["glass"], RAMP["shell"]
LEATHER, STEEL, BRASS, FLAME = RAMP["leather"], RAMP["steel"], RAMP["brass"], RAMP["flame"]


def card_bevel(night: bool) -> tuple:
    """A card's bevel: pale plastic lit along its top and left and shaded along its foot and right."""
    return (PLASTIC[4], PLASTIC[0]) if night else (SHELL[6], SHELL[2])


def node_deco(p: Pix, night: bool, x, y, w, h, seed, lid):
    """A card as a monitor: a band of charcoal down the edge of its icon's cell with its power light burning green at
    its foot, and on every third card's lid a pair of rabbit ears."""
    for yy in range(y + 1, y + h - 1):
        p.px(x + 10, yy, PLASTIC[4] if not night else PLASTIC[3])
        p.px(x + 11, yy, PLASTIC[2])
        p.px(x + 12, yy, PLASTIC[0])
    p.px(x + 11, y + h - 4, FLAME[4])
    if lid and seed % 3 == 0:
        mx = x + 13 + (w - 13) // 2
        p.hline(mx - 1, mx + 2, y - 1, PLASTIC[2])
        for i in range(1, 5):
            p.px(mx - i, y - 1 - i, STEEL[4] if not night else STEEL[3])
            p.px(mx + i, y - 1 - i, STEEL[4] if not night else STEEL[3])


def wire_ink(night: bool) -> str:
    """A wire is a black cable, its sheath grey by night."""
    return PLASTIC[4] if night else PLASTIC[1]


def wire_lights(p: Pix, cells, night: bool, seed):
    """Tally lights on the cable every twelfth unit, a green one burning and a dark one by turns."""
    for i, (x, y, d) in enumerate(cells[5:-7]):
        if i % 12:
            continue
        on = (i // 12 + seed) % 2 == 0
        key = ("tally", d, on)
        if key not in p.syms:
            c, s = (FLAME[4], FLAME[1]) if on else (PLASTIC[4], PLASTIC[0])
            cells_ = {(0, -1): c, (1, -1): s, (0, 0): s} if d == "h" else {(-1, 0): c, (-1, 1): s, (0, 0): s}
            p.symbol(key, cells_)
        p.use(key, x, y)


def dashes(night: bool) -> list:
    """A group's dashed border, the phosphor and charcoal by turns."""
    return [FLAME[3] if night else FLAME[1], PLASTIC[4] if night else PLASTIC[2]]


def ornament(kind: str, p, x, y, night: bool) -> tuple:
    """A set showing the white rabbit in a free corner of the schematic, 24 by 18."""
    if kind == "schematic":
        if p is not None:
            A.tv(p, x, y, "rabbit", night, False)
        return (A.TV_W, A.TV_H)
    return (0, 0)


def hist_bar(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a level meter: a column of little tubes in a charcoal case, lit in the phosphor up to its
    count, the top one white-hot."""
    for yy in range(base - v, base):
        for xx in range(bx, bx + bw):
            edge = xx in (bx, bx + bw - 1) or yy == base - v
            if edge:
                c = PLASTIC[3] if xx == bx or yy == base - v else PLASTIC[1]
            elif (base - yy) % 3 == 0:
                c = PLASTIC[1]
            elif yy < base - v + 3:
                c = FLAME[6] if xx < bx + bw - 2 else FLAME[4]
            else:
                c = FLAME[3] if xx < bx + bw - 2 else FLAME[2]
            p.px(xx, yy, c)


def peak_mark(p: Pix, x, y, night: bool):
    """A spark of the phosphor over the busiest week's count."""
    spark = ((2, 0, 4), (2, 1, 6), (0, 2, 4), (1, 2, 6), (2, 2, 6), (3, 2, 6), (4, 2, 4), (2, 3, 6), (2, 4, 4))
    for dx, dy, t in spark:
        p.px(x + dx, y + dy, FLAME[t])


def dial_ring(p: Pix, arc, night: bool):
    """A charcoal bezel bent over the dial, lit along its upper left, a phosphor glint every so often."""
    def colour(s, o, lam, x, y):
        if int(s) % 9 == 4 and abs(o) < 0.45:
            return FLAME[4]
        return PLASTIC[max(1, min(5, round(1 + 4 * lam)))]
    tube(p, arc, 2.6, colour, outline=PLASTIC[0])


def dial_tick(p: Pix, x, y, night: bool):
    p.px(x, y, FLAME[4])
    p.px(x + 1, y + 1, FLAME[1])


def dial_hub(p: Pix, cx, cy, night: bool):
    """A brass knob on a charcoal collar."""
    for i, xx in enumerate(range(cx - 4, cx + 5)):
        p.px(xx, cy + 2, PLASTIC[4] if i < 3 else PLASTIC[2] if i < 7 else PLASTIC[0])
    sphere(p, cx + 0.5, cy - 0.5, 3.0, BRASS, lo=1, hi=6)


def material(i: int, xx, yy, y0, y1, lift, night: bool) -> str:
    """What a screen shows, by turns: the code falling, a test card's bars stepped down the phosphor, snow, scanlines,
    and the white room's wall."""
    kind = i % 5
    if kind == 0:
        c = FLAME[3] if (xx % 3 == 0 and (yy + xx * 5) % 4 != 0) else GLASS[3]
    elif kind == 1:
        c = FLAME[5 - min(4, (xx // 4) % 5)]
    elif kind == 2:
        c = FLAME[(xx * 7 + yy * 13) % 5 // 2 + 1] if (xx * 3 + yy * 7) % 5 else GLASS[2]
    elif kind == 3:
        c = GLASS[5] if (yy - y0) % 2 == 0 else GLASS[2]
    else:
        c = WALL[2] if xx % 9 == 0 else WALL[5]
    try:
        return step(c, lift)
    except KeyError:
        return c


def counter_cell(q: Pix, ox, oy, night: bool):
    """A little tube 11 by 15 a numeral glows on: a charcoal bezel lit along its top and left and shaded along its foot
    and right, its glass dark with a gleam at its upper left."""
    for yy in range(15):
        for xx in range(11):
            if (xx, yy) in ((0, 0), (10, 0), (0, 14), (10, 14)):
                continue
            if xx == 0 or yy == 0:
                c = PLASTIC[4]
            elif xx == 10 or yy == 14:
                c = PLASTIC[1]
            elif xx == 1 or yy == 1 or xx == 9 or yy == 13:
                c = PLASTIC[0]
            else:
                c = GLASS[2]
            q.px(ox + xx, oy + yy, c)
    q.px(ox + 2, oy + 2, GLASS[5])
    q.px(ox + 3, oy + 2, GLASS[4])


def counter_ink(night: bool, dim: bool) -> str:
    """A numeral glowing in the phosphor, nearly white; a leading nought dim. (A tone the sheet's words never take, so
    the numerals are written over their tubes.)"""
    return FLAME[1] if dim else FLAME[5]


def timeline_line(p: Pix, x0, x1, y, night: bool):
    """A cable the releases stand on, up to today, a grey coupling every so often."""
    if x1 - x0 < 3:
        return

    def colour(s, o, lam, x, yy):
        return PLASTIC[max(1, min(5, round(1 + 4 * lam)))]
    tube(p, [(x0, y + 1.5), (x1, y + 1.5)], 2.0, colour, outline=PLASTIC[0])
    for x in range(x0 + 26, x1 - 4, 52):
        for dy in range(3):
            p.px(x, y + dy, SHELL[5] if dy == 0 else SHELL[3])
            p.px(x + 1, y + dy, SHELL[3] if dy == 0 else SHELL[1])


# A little set on the cable, 7 by 6: its pale case, its picture on, its stand. c C the case, g G S the picture.
LITTLE = ["ccccccc", "cGgggSc", "cgggggc", "cggggSc", "ccccccc", "..CCC.."]


def release(p: Pix, x, gy, kind, night: bool, i=0):
    """A release as a little set standing on the cable at x: its picture on for a release, the code falling for a big
    one, switched off for one still to come; a patch a tally light; and the repository's founding the white wingback."""
    k = -1 if night else 0
    if kind == "minor":
        p.px(x, gy - 1, FLAME[4])
        p.px(x + 1, gy - 1, FLAME[1])
        p.px(x, gy, PLASTIC[1])
        return
    if kind == "made":
        rows = ["....LL", "...LLL", "...LLL", "LLLLLS", "SSSSSS", ".m..m."]
        p.sprite(x - 3, gy - 5, rows, {"L": LEATHER[6 + k], "S": LEATHER[3 + k], "m": STEEL[3]})
        return
    on = kind != "next"
    pal = {"c": SHELL[5 + k], "C": SHELL[3 + k], "g": FLAME[2] if on else GLASS[2],
           "G": FLAME[4] if on else GLASS[4], "S": FLAME[1] if on else GLASS[3]}
    if kind == "big":
        pal.update({"g": GLASS[2], "G": FLAME[5], "S": FLAME[3]})
    p.sprite(x - 3, gy - 6, LITTLE, pal)


def today_mark(p: Pix, x, y, night: bool):
    """The Architect's pen standing upright at today's end of the cable, its cap black and its barrel brass."""
    for yy in range(y - 9, y + 1):
        p.px(x, yy, STEEL[0] if yy < y - 5 else BRASS[5])
        p.px(x + 1, yy, STEEL[1] if yy < y - 5 else BRASS[3])
    p.px(x - 1, y - 8, STEEL[3])
    p.px(x, y + 1, BRASS[6])


def avatar(p: Pix, cx, cy, i, person, night: bool):
    """A contributor on a set: their initials glowing in the phosphor on its tube, in its pale case on a little stand;
    a bot's set lost to snow."""
    k = -1 if night else 0
    for yy in range(cy - 7, cy + 6):
        for xx in range(cx - 7, cx + 8):
            edge = xx in (cx - 7, cx + 7) or yy in (cy - 7, cy + 5)
            if edge:
                c = SHELL[5 + k] if (xx == cx - 7 or yy == cy - 7) else SHELL[2 + k]
            elif xx in (cx - 6, cx + 6) or yy in (cy - 6, cy + 4):
                c = SHELL[4 + k]
            else:
                c = GLASS[2]
            p.px(xx, yy, c)
    p.hline(cx - 2, cx + 3, cy + 6, SHELL[3 + k])
    p.hline(cx - 3, cx + 4, cy + 7, SHELL[2 + k])
    if not person.get("initials"):
        rnd = random.Random(i)
        for yy in range(cy - 5, cy + 4):
            for xx in range(cx - 5, cx + 6):
                if rnd.random() < 0.45:
                    p.px(xx, yy, FLAME[rnd.choice((0, 1, 3))])
        return
    p.text(cx - 3, cy - 3, str(person["initials"])[:2], FLAME[4], "35")


def commit_bar(p: Pix, x, y, w, fill, night: bool):
    """A contributor's share as a level meter: the phosphor filling a charcoal case."""
    p.box(x, y, w + 2, 4, PLASTIC[2] if not night else PLASTIC[4])
    p.hline(x + 1, x + 1 + w, y + 1, GLASS[2])
    p.hline(x + 1, x + 1 + w, y + 2, GLASS[2])
    p.hline(x + 1, x + 1 + fill, y + 1, FLAME[4])
    p.hline(x + 1, x + 1 + fill, y + 2, FLAME[2])


def rosette(p: Pix, cx, cy, r0, r1, n, night: bool):
    """A test card's rings round the seal: bands stepped down the phosphor from its rim, crossed by its spokes."""
    for y in range(cy - r1 - 1, cy + r1 + 2):
        for x in range(cx - r1 - 1, cx + r1 + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d < r0 or d > r1:
                continue
            band = int((d - r0) / max(1, (r1 - r0)) * 4)
            ang = math.atan2(dy, dx)
            spoke = abs(math.sin(ang * n / 2)) < 0.12
            c = PLASTIC[0] if spoke else (FLAME[5], FLAME[3], FLAME[2], FLAME[1])[min(3, band)]
            if d > r1 - 0.8:
                c = PLASTIC[1]
            p.px(x, y, c)


def seal_mark(p: Pix, x, y, night: bool):
    """The white rabbit at the seal's foot, running."""
    rows = ["..w.w..", "..w.w..", "..www..", ".wwwWw.", "wwwwwW.", ".wW.wW.", ".w...w."]
    k = -1 if night else 0
    p.sprite(x + 4, y, rows, {"w": LEATHER[6 + k], "W": LEATHER[3 + k]})


def placard_board(p: Pix, night: bool, design):
    """The placard: a panel of the white room in the frame of little sets, its power light burning in its corner."""
    design.paper(p, night, uid="pl")
    design.frame(p, night)
    p.px(p.w - 7, p.h - 7, FLAME[4])
    p.px(p.w - 6, p.h - 7, FLAME[1])


def placard_mark(p: Pix, x, y, night: bool):
    """A little set beside the placard's title, its picture on."""
    k = -1 if night else 0
    p.sprite(x + 2, y - 3, LITTLE, {"c": SHELL[5 + k], "C": SHELL[3 + k], "g": FLAME[2], "G": FLAME[4],
                                    "S": FLAME[1]})
