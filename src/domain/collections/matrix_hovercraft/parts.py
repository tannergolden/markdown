# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hovercraft set's elements: every sheet the kit draws made of the ship's own stuff.

A schematic's cards are plates of pale steel riveted at their corners, a weld down the edge of each icon's cell and
a work lamp clamped to a card's lid, and its wires are the ship's black cables, tied every so often, a signal light
on them by night. A week's commits stand as a stack of steel plates, the busiest marked with a red warning lamp; the
days since a release are read off a pressure gauge, its bezel of steel and the last of its dial red; the bytes by
file type run as a ribbon of the ship's stuffs, rust and drab paint, pale plate, brick, the machines' iron and the
water; and a counter's digits glow phosphor on the dark glass of a readout. The milestones hang from a pipe, flanged
and bolted, each release a valve on it, the planned ones in outline, today a work lamp burning; the contributors
wear dog tags with their initials stamped in them, and a bot is one of the machines. The certificate's seal sits in
a flange bolted round, the ship at its foot, and the placard is a plate of the ship's steel riveted to the wall."""
from __future__ import annotations

import math

from ...holidays.pixel import Pix
from .art import EDGE, ICONS, SENTINEL, _shade, _t, icon_pal, mini_ship
from .palette import C, RAMP

STEEL, PLATE, RUST, BRICK, DRAB = RAMP["steel"], RAMP["plate"], RAMP["rust"], RAMP["brick"], RAMP["drab"]
IRON, EYE, FLAME, WATER, TUNNEL = RAMP["iron"], RAMP["eye"], RAMP["flame"], RAMP["water"], RAMP["tunnel"]
CONCRETE = RAMP["concrete"]


# --------------------------------------------------------------------------- the schematic
def card(p: Pix, x, y, w, h, night: bool, lid: bool):
    """A schematic's card as a steel plate: a rivet in each corner inside its bevel, a weld run down the edge of its
    icon's cell, and on a card with a lid a work lamp clamped to its top, burning phosphor by night."""
    k = -3 if night else 0
    q = _shade(PLATE, k)
    for cx, cy in ((x + 2, y + 2), (x + w - 3, y + 2), (x + 2, y + h - 3), (x + w - 3, y + h - 3)):
        p.px(cx, cy, q(6) if not night else STEEL[4])
        p.px(cx + 1, cy + 1, q(1) if not night else STEEL[0])
    for yy in range(y + 2, y + h - 2):
        p.px(x + 12, yy, (q(6) if yy % 2 else q(2)) if not night else (STEEL[4] if yy % 2 else STEEL[2]))
    if lid:
        lx = x + w - 14
        s = _shade(STEEL, -2 if night else 0)
        p.rect(lx - 1, y - 2, 5, 2, s(4))
        p.hline(lx - 1, lx + 4, y - 2, s(5))
        p.rect(lx, y - 4, 3, 2, FLAME[5] if night else PLATE[6])
        p.px(lx + 1, y - 5, FLAME[6] if night else PLATE[5])
        p.px(lx - 1, y - 4, s(1))
        p.px(lx + 3, y - 4, s(1))


def cable_ties(p: Pix, cells, night: bool, seed: int):
    """What the ship's cables carry: a tie round them every fourteen units, and by night a signal light every twenty,
    burning phosphor."""
    tie = PLATE[5] if not night else STEEL[5]
    for i, (x, y, d) in enumerate(cells):
        if i % 14 == 7:
            if d == "h":
                p.px(x, y - 1, tie)
                p.px(x, y + 1, tie)
            else:
                p.px(x - 1, y, tie)
                p.px(x + 1, y, tie)
        elif night and i % 20 == (seed % 7) + 3:
            p.px(x, y, FLAME[5])


def ornament(p: Pix, x, y, night: bool):
    """The ship in little hovering over a puddle in a free corner of the schematic, its pads' light on the water."""
    mini_ship(p, x, y, night)
    p.hline(x + 1, x + 31, y + 16, TUNNEL[3] if night else WATER[3])
    p.hline(x + 5, x + 12, y + 16, FLAME[3] if night else WATER[5])
    p.hline(x + 21, x + 28, y + 16, FLAME[3] if night else WATER[5])


# --------------------------------------------------------------------------- the instruments
def plate_stack(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a stack of steel plates, three rows each, lit along their tops and bolted at their left,
    the top plate catching the lamp's light; a stack too short for a plate is one plate cut down."""
    k = -3 if night else 0
    q = _shade(PLATE, k)
    y = base
    n = 0
    while y > base - v:
        h = min(3, y - (base - v))
        top = y - h
        for yy in range(top, y):
            j = yy - top
            c = q(6) if j == 0 else q(4) if j == 1 else q(2)
            p.hline(bx, bx + bw, yy, c)
        if h == 3 and bw >= 5:
            p.px(bx + 1, top + 1, q(1))
        n += 1
        y = top
    p.vline(bx + bw - 1, base - v, base, q(1))
    if night:
        p.hline(bx, bx + bw, base - v, FLAME[3])


def warning_lamp(p: Pix, x, y, night: bool):
    """A red warning lamp in its cage beside the busiest week's count, its light round it by night."""
    s = _shade(STEEL, -2 if night else 0)
    p.hline(x, x + 3, y, s(4))
    p.rect(x, y + 1, 3, 2, EYE[4])
    p.px(x, y + 1, EYE[6])
    p.hline(x, x + 3, y + 3, s(2))
    if night:
        p.halo(x + 1.5, y + 2, 4, 3, EYE[3], (0.12, 0.24), L="haze")


def gauge_ring(p: Pix, arc, night: bool):
    """The dial as a pressure gauge's bezel: a ring of steel two units deep, lit over its upper left and in shade
    toward its right, its last quarter painted red, the danger the needle runs into."""
    s = _shade(STEEL, 0)
    pts = [(round(x), round(y)) for x, y in arc]
    n = len(pts)
    cells = []
    for i, ((ax, ay), (bx, by)) in enumerate(zip(pts, pts[1:])):
        steps = max(abs(bx - ax), abs(by - ay), 1)
        for j in range(steps):
            cells.append((round(ax + (bx - ax) * j / steps), round(ay + (by - ay) * j / steps), i))
    cells.append((*pts[-1], n - 1))
    cx = (pts[0][0] + pts[-1][0]) / 2
    for x, y, i in cells:
        red = i > n * 0.75
        outer = (x, y - 1) if abs(x - cx) < 4 else ((x - 1, y) if x < cx else (x + 1, y))
        if red:
            p.px(x, y, EYE[4] if night else EYE[3])
            p.px(*outer, EYE[2] if night else EYE[1])
        else:
            p.px(x, y, s(5) if i < n * 0.45 else s(4))
            p.px(*outer, STEEL[0] if not night else s(2))


def nut_hub(p: Pix, cx, cy, night: bool):
    """The hub the needle turns on: a hex nut of steel, lit at its upper left."""
    s = _shade(STEEL, -2 if night else 0)
    p.hline(cx - 1, cx + 2, cy - 2, s(5))
    p.rect(cx - 2, cy - 1, 5, 3, s(4))
    p.px(cx - 2, cy - 1, s(6))
    p.hline(cx - 1, cx + 2, cy + 2, s(1))
    p.px(cx, cy, STEEL[0])


def stuff(i: int, xx, yy, y0, y1, lift, night: bool) -> str:
    """The colour of the `i`-th file type's wrapper at (xx, yy), by turns the ship's stuffs: rusted iron, drab
    paint, pale plate riveted, brick in its courses, the machines' iron and the water, each lit along its top and
    shaded along its foot."""
    k = -2 if night else 0
    kind = i % 6
    if kind == 0:
        R, at = RUST, 4
        if (xx * 7 + yy * 3) % 11 == 0:
            at -= 1
    elif kind == 1:
        R, at = DRAB, 4
    elif kind == 2:
        R, at = PLATE, 4
        if (yy - y0) == 2 and xx % 8 == 3:
            at += 2
    elif kind == 3:
        R, at = BRICK, 4
        if (yy - y0) % 4 == 3 or ((xx + ((yy - y0) // 4) * 3) % 6 == 0):
            at = 2
    elif kind == 4:
        R, at = IRON, 4
    else:
        R, at = WATER, 4
        if (xx + yy * 2) % 9 == 0:
            at += 1
    return _t(R, at + lift + k)


def readout(q: Pix, ox, oy, night: bool):
    """A counter's cell, 11 by 15, as a readout: dark glass in a bezel of steel, lit along its top and left, a
    gleam in the glass's corner."""
    s = _shade(STEEL, -2 if night else 0)
    q.box(ox, oy, 11, 15, STEEL[0])
    q.hline(ox + 1, ox + 10, oy + 1, s(5))
    q.vline(ox + 1, oy + 2, oy + 14, s(4))
    q.vline(ox + 9, oy + 2, oy + 14, s(2))
    q.hline(ox + 2, ox + 9, oy + 13, s(2))
    q.rect(ox + 2, oy + 2, 7, 11, TUNNEL[1])
    q.px(ox + 2, oy + 2, STEEL[3])


# --------------------------------------------------------------------------- the milestones
def pipe_line(p: Pix, x0, x1, y, night: bool):
    """The pipe the releases hang from: gunmetal, lit along its crown, flanged every forty units."""
    s = _shade(STEEL, -2 if night else 0)
    p.hline(x0, x1, y - 1, s(6))
    p.hline(x0, x1, y, s(4))
    p.hline(x0, x1, y + 1, s(1))
    for x in range(x0 + 12, x1 - 2, 40):
        p.vline(x, y - 2, y + 3, s(5))
        p.vline(x + 1, y - 2, y + 3, s(2))


VALVE_BIG = ["..ooo..", ".oOoOo.", "oOoooOo", "ooOHOoo", "oOoooOo", ".oOoOo.", "..ooo.."]
VALVE = [".ooo.", "oOoOo", "ooHoo", "oOoOo", ".ooo."]


def valve(p: Pix, x, gy, kind: str, night: bool):
    """A release on the pipe at x: a big valve wheel for a release with a name, a smaller one for each other, a
    bolt for a patch, a wheel in outline for a planned one, and a capped stub for the day it was made; each on a stem
    down from the pipe."""
    k = -1 if night else 0
    s = _shade(STEEL, k)
    if kind == "minor":
        p.rect(x - 1, gy - 1, 2, 2, s(6))
        p.px(x, gy, s(1))
        return
    if kind == "made":
        p.vline(x, gy + 2, gy + 5, s(4))
        p.rect(x - 2, gy + 5, 5, 3, s(3))
        p.hline(x - 2, x + 3, gy + 5, s(5))
        return
    art = VALVE_BIG if kind == "big" else VALVE
    n = len(art)
    top = gy + 3
    p.vline(x, gy + 2, top + 1, s(2))
    if kind == "next":
        for j, row in enumerate(art):
            for i, ch in enumerate(row):
                if ch != "." and (i in (0, n - 1) or j in (0, n - 1) or ch == "H"):
                    p.px(x - n // 2 + i, top + j, s(3) if not night else STEEL[3])
        return
    pal = {"o": _t(RUST, 2 + (1 if night else 0)), "O": _t(RUST, 5 + (1 if night else 0)), "H": s(6)}
    p.sprite(x - n // 2, top, art, pal)


def lamp_mark(p: Pix, x, y, night: bool):
    """Today, at the end of the pipe: a work lamp hanging from it, its bulb burning phosphor, its light round it."""
    s = _shade(STEEL, -2 if night else 0)
    p.vline(x, y + 1, y + 4, s(2))
    p.rect(x - 2, y + 4, 5, 2, s(4))
    p.hline(x - 2, x + 3, y + 4, s(5))
    p.rect(x - 1, y + 6, 3, 2, FLAME[5])
    p.px(x, y + 8, FLAME[6])
    p.halo(x + 0.5, y + 7, 6, 4, FLAME[3], (0.1, 0.2) if night else (0.06, 0.12), L="haze")


# --------------------------------------------------------------------------- the roster
def dog_tag(p: Pix, cx, cy, i: int, person: dict, night: bool):
    """A contributor's dog tag, centred on (cx, cy): a plate of pale steel with its corners rounded, lit along its top
    and left, a hole at its top on its chain, their initials stamped in it; a bot is one of the machines, its red
    eyes burning."""
    if not person.get("initials"):
        k = -1 if night else 0
        pal = {"o": IRON[0], "I": _t(IRON, 5 + k), "i": _t(IRON, 3 + k), "e": EYE[5], "t": _t(IRON, 4 + k)}
        p.sprite(cx - 5, cy - 4, SENTINEL, pal)
        return
    k = -3 if night else 0
    q = _shade(PLATE, k)
    x0, y0 = cx - 6, cy - 6
    for yy in range(y0, y0 + 13):
        for xx in range(x0, x0 + 13):
            corner = (xx in (x0, x0 + 12)) and (yy in (y0, y0 + 12))
            if corner:
                continue
            edge = xx in (x0, x0 + 12) or yy in (y0, y0 + 12)
            if edge:
                c = q(6) if (xx == x0 or yy == y0) else q(1)
            else:
                c = q(4)
            p.px(xx, yy, c)
    p.px(cx, y0 + 2, STEEL[0])
    p.px(cx, y0 + 1, q(2))
    for j in range(3):
        p.px(cx + 1 + j, y0 - 1 - j, STEEL[3] if j % 2 else STEEL[5])
    initials = str(person.get("initials", "?"))[:2]
    p.text(cx - 3 - (2 if len(initials) > 1 else 0) + (2 if len(initials) == 1 else 0), cy - 1, initials,
           STEEL[0] if not night else PLATE[6], "35")


def gauge_bar(p: Pix, x, y, w, fill, night: bool, ink: str):
    """A contributor's share as a gauge glass: a tube of steel `w` long, filled `fill` of the way with phosphor,
    lit along its top."""
    s = _shade(STEEL, -2 if night else 0)
    p.box(x, y, w + 2, 4, ink)
    p.hline(x + 1, x + 1 + w, y + 1, TUNNEL[2] if night else STEEL[2])
    p.hline(x + 1, x + 1 + w, y + 2, TUNNEL[1] if night else STEEL[1])
    p.hline(x + 1, x + 1 + fill, y + 1, FLAME[5])
    p.hline(x + 1, x + 1 + fill, y + 2, FLAME[3])
    p.px(x, y, s(5))


# --------------------------------------------------------------------------- the certificate
def flange(p: Pix, cx, cy, r0, r1, n: int, night: bool):
    """The seal set in a flange of steel, lit over its upper left and in shade toward its lower right, bolted round
    with `n` bolts."""
    s = _shade(STEEL, -2 if night else 0)
    for y in range(cy - r1, cy + r1 + 1):
        for x in range(cx - r1, cx + r1 + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r0 <= d <= r1:
                lit = (x + 0.5 - cx) * -0.63 + (y + 0.5 - cy) * -0.78
                c = s(5) if lit > r1 * 0.4 else s(4) if lit > -r1 * 0.3 else s(3)
                if d > r1 - 1:
                    c = STEEL[0]
                p.px(x, y, c)
    rm = (r0 + r1) / 2
    for i in range(n):
        a = 2 * math.pi * i / n
        bx, by = round(cx + rm * math.cos(a)), round(cy + rm * math.sin(a))
        p.px(bx, by, s(6))
        p.px(bx + 1, by, s(2))
        p.px(bx, by + 1, s(1))
        p.px(bx + 1, by + 1, STEEL[0])


def seal_ship(p: Pix, x, y, night: bool):
    """The ship in little at the seal's foot."""
    p.sprite(x + 2, y, ICONS["ship"], icon_pal(night))


# --------------------------------------------------------------------------- the placard
def placard(p: Pix, night: bool):
    """The placard as a plate of the ship's steel riveted to the tunnel wall: pale scuffed plate by day and the plate
    in the dark by night, framed in gunmetal riveted every ten units, rust weeping from two of the rivets onto the
    plate."""
    w, h = p.w, p.h
    k = -3 if night else 0
    q = _shade(PLATE, k)
    s = _shade(STEEL, -2 if night else 0)
    face = C["plate_night"] if night else PLATE[5]
    p.under.append(f'<rect width="{w}" height="{h}" fill="{face}"/>')
    for i, c in enumerate((STEEL[0], s(5), s(4), s(2))):
        p.box(i, i, w - 2 * i, h - 2 * i, c)
    p.hline(EDGE, w - EDGE, EDGE, q(6))
    p.vline(EDGE, EDGE, h - EDGE, q(5))
    p.hline(EDGE, w - EDGE, h - EDGE - 1, q(2))
    p.vline(w - EDGE - 1, EDGE, h - EDGE, q(2))
    for x in range(8, w - 6, 10):                    # rivets along the frame
        for y in (1, h - 3):
            p.px(x, y, s(6))
            p.px(x + 1, y + 1, STEEL[0])
    for y in range(9, h - 6, 10):
        for x in (1, w - 3):
            p.px(x, y, s(6))
            p.px(x + 1, y + 1, STEEL[0])
    for x in (48, w - 62):                          # rust weeping from two of them onto the plate
        for j in range(3, 7):
            p.px(x + 1, j, (RUST[3] + ":0.5") if not night else (RUST[1] + ":0.6"))
