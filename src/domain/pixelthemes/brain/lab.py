# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The laboratory's machines: the jar the brain lives in, on the console that keeps it, with the screen its moods
show on; the mainframe it works with; the Tesla coil beside it; and the oscilloscope its waves sweep across.

The jar is a cylinder of glass held between two caps of riveted brass by a strut of brass at each side, full of an
aqua fluid with its meniscus near the top, the brain floating in it with its stem in a socket in the lower cap and
wires coming down from the upper one to the electrodes on its crown. A pressure gauge sits on the domed cap, and two
pipes rise from it to the ceiling. Bubbles rise through the fluid. By day the lab's lamps light it and the glass
shines; by night the fluid glows and lights the room."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Pix
from . import brain as BR
from .kit import ellipse, glow, signal, trace
from .palette import C, RAMP

FLUID, ENAMEL, BRASS, STEEL, NIXIE, ARC, TISSUE, ROOM, SAGE = (RAMP["fluid"], RAMP["enamel"], RAMP["brass"],
                                                              RAMP["steel"], RAMP["nixie"], RAMP["arc"], RAMP["tissue"],
                                                              RAMP["room"], RAMP["sage"])
CEILING = 16        # the row the pipes rise to


def _dim(R, t, night, by=2):
    """Tone `t` of ramp `R`, a step or two darker by night when the lamps are out."""
    return R[max(0, t - by)] if night else R[t]


# --------------------------------------------------------------------------- the jar
LEAST = 28          # the narrowest glass a jar is drawn with: the brain at its smallest still fits inside it


def jar_size(w: int) -> dict:
    """The jar's parts for a glass `w` wide, at least `LEAST`: the caps' depths, the glass's height, the console's,
    and the brain's scale, so the brain fills the jar with room for its stem and its wires."""
    k = round(max(0.2, (w - 8) / 100), 2)
    bw, bh = BR.extent(k)
    cap, base = max(4, round(w * 0.11)), max(3, round(w * 0.08))
    glass = bh + max(6, round(w * 0.15))
    console = max(11, round(w * 0.3)) if w < 56 else max(21, round(w * 0.35))
    gauge = 4 if w >= 30 else 0
    return {"w": w, "k": k, "cap": cap, "base": base, "glass": glass, "console": console, "gauge": gauge,
            "h": gauge + cap + glass + base + console}


def jar_box(cx: int, foot: int, w: int) -> tuple:
    """The box the jar and its console take, (x0, y0, x1, y1), standing on row `foot`."""
    z = jar_size(w)
    half = w // 2 + 6
    return (cx - half, foot - z["h"] - 1, cx + half + 1, foot + 1)


def jar(p: Pix, cx: int, foot: int, w: int, night: bool, motion: bool, face=None, pipes=True) -> dict:
    """The jar, its glass `w` wide, on its console standing on row `foot`, centred on column `cx`. `face`, when
    given, draws the screen on the console: face(p, x, y, w, h). Returns where its parts are."""
    z = jar_size(w)
    x0, x1 = cx - w // 2, cx - w // 2 + w
    y_con = foot - z["console"] + 1
    y_base = y_con - z["base"]
    y_glass = y_base - z["glass"]
    y_cap = y_glass - z["cap"]
    if night:
        glow(p, cx, (y_glass + y_base) / 2, w * 0.95, z["glass"] * 0.75, FLUID[4], (0.05, 0.09, 0.14, 0.2),
             shape=True)
    if pipes:
        for dx in (-(w // 4), w // 4 - 1):
            px_ = cx + dx
            for y in range(CEILING, y_cap + 1):
                p.px(px_, y, _dim(STEEL, 4, night))
                p.px(px_ + 1, y, _dim(STEEL, 2, night, 1))
            mid = (CEILING + y_cap) // 2
            if y_cap - CEILING > 8:
                for x in range(px_ - 1, px_ + 3):
                    p.px(x, mid, _dim(BRASS, 5, night))
                    p.px(x, mid + 1, _dim(BRASS, 3, night))
    _console(p, cx, y_con, foot, w + 12, night, face, z)
    # the glass and the fluid in it, rounded as a cylinder is: lighter where the lamp catches it, darker at its far
    # edge
    fluid_top = y_glass + max(2, round(z["glass"] * 0.07))
    R = FLUID
    for y in range(y_glass, y_base):
        f = (y - fluid_top) / max(1, y_base - fluid_top)
        for x in range(x0 + 1, x1 - 1):
            u = (x - x0) / max(1, w - 1)
            if y < fluid_top:
                c = (STEEL[6] + ":0.35") if not night else (FLUID[1] + ":0.5")
            elif y == fluid_top:
                c = R[6]
            else:
                t = (5 if f < 0.08 else 4 if f < 0.5 else 3) if not night else (5 if f < 0.12 else 4 if f < 0.6 else 3)
                if u < 0.12:
                    t += 1
                elif u > 0.86:
                    t -= 1
                c = R[max(1, min(6, t))]
            p.px(x, y, c)
        p.px(x0, y, STEEL[3] if not night else STEEL[2])
        p.px(x1 - 1, y, STEEL[2] if not night else STEEL[1])
    # the brain floating in it, its stem in the socket
    k = z["k"]
    bw, bh = BR.extent(k)
    bx = cx - bw // 2
    by = y_base - bh - 1
    BR.brain(p, bx, by, k, night, rim=FLUID[5])
    sock = bx + round(67 * k)
    for x in range(sock - 2, sock + round(8 * k) + 2):
        p.px(x, y_base - 1, _dim(BRASS, 4, night))
        if x in (sock - 2, sock + round(8 * k) + 1):
            p.px(x, y_base - 2, _dim(BRASS, 5, night))
    # the wires down from the cap to the electrodes on its crown
    s = BR.shape(k)
    ends = []
    for i, (ex, ey) in enumerate(s.electrodes):
        ax, ay = bx + ex, by + ey
        top = (x0 + 4 + i * (w - 8) // 2, y_glass)
        line = trace([(top[0] + 0.5, top[1] + 0.5), ((top[0] + ax) / 2 + (2 if i == 1 else 0), (top[1] + ay) / 2),
                      (ax + 0.5, ay - 0.5)])
        for (x, y) in line[:-1]:
            if y < ay:
                p.px(x, y, (STEEL[1] if i != 1 else TISSUE[2]) if not night else (ROOM[0] if i != 1 else TISSUE[1]))
        ends.append((ax, ay))
    # the glass shines where the lamps catch it: long strokes of light down it, each one rectangle over the fluid
    glare = p.layer("glare", z=0.6)
    gh = y_base - 1 - (y_glass + 1)
    if not night:
        strokes = [(x0 + 2, C["white"], ".6"), (x0 + 3, C["white"], ".3"), (x1 - 3, C["white"], ".35")]
    else:
        strokes = [(x0 + 2, FLUID[6], ".4")]
    for gx, col, a in strokes:
        p.shapes[glare].append(f'<rect x="{gx}" y="{y_glass + 1}" width="1" height="{gh}" fill="{col}" '
                               f'fill-opacity="{a}"/>')
    # the struts of brass that hold the caps together, either side of the glass
    for y in range(y_glass, y_base):
        p.px(x0 - 2, y, _dim(BRASS, 5, night))
        p.px(x0 - 3, y, _dim(BRASS, 3, night))
        p.px(x1 + 1, y, _dim(BRASS, 3, night))
        p.px(x1 + 2, y, _dim(BRASS, 1, night, 1))
    # the caps of riveted brass, the gauge on the upper one
    _cap(p, x0 - 4, x1 + 4, y_cap, z["cap"], night, top=True)
    _cap(p, x0 - 4, x1 + 4, y_base, z["base"], night, top=False)
    if z["gauge"]:
        gauge(p, cx, y_cap - 2, night)
    if motion and not p.lite:
        bubbles(p, x0 + 2, x1 - 2, fluid_top + 1, y_base - 2, night, seed=w)
        BR.work(p, bx, by, k, night)
    for i, x in enumerate(range(x0 + 1, x1 - 1, max(4, w // 5))):
        if motion and not p.lite:
            p.px(x, y_base + z["base"] // 2, (NIXIE[5], FLUID[5], TISSUE[4])[i % 3], p.twinkle(i))
    return {"x0": x0, "x1": x1, "glass": (y_glass, y_base), "fluid": fluid_top, "cap": y_cap, "console": y_con,
            "brain": (bx, by, k), "electrodes": ends}


# --------------------------------------------------------------------------- the jar drawn small
def little_size(k: float) -> tuple:
    """The (w, h) of a little jar round the brain at scale `k`."""
    bw, bh = BR.extent(k)
    return bw + 8, bh + 17


def little_jar(p: Pix, x, y, night, k=0.12) -> tuple:
    """The jar drawn small, at the art's own size, for a corner or a floor too small for the whole one: the brain
    itself at scale `k`, wired to the cap and standing in its socket, in a glass of fluid between caps of brass, on
    a little console whose screen shows two eyes. Its top left at (x, y); returns its (w, h)."""
    W, H = little_size(k)
    bw, bh = BR.extent(k)
    gw = bw + 4
    x0, x1 = x + 2, x + 2 + gw
    y_glass = y + 3
    y_base = y_glass + bh + 7
    y_con = y_base + 2
    for yy in range(y_con, y + H):
        for xx in range(x, x + W):
            t = 5 if yy == y_con else 4 if xx == x else 1 if (xx == x + W - 1 or yy == y + H - 1) else 3
            p.px(xx, yy, _dim(ENAMEL, t, night))
    sx = x + W // 2 - 3
    for xx in range(sx, sx + 6):
        for yy in range(y_con + 1, y_con + 4):
            p.px(xx, yy, ROOM[1])
    p.px(sx + 1, y_con + 2, FLUID[5])
    p.px(sx + 4, y_con + 2, FLUID[5])
    p.px(x + 2, y_con + 2, ENAMEL[1] if not night else ENAMEL[0])
    p.px(x + 3, y_con + 2, ENAMEL[1] if not night else ENAMEL[0])
    p.px(x + W - 3, y_con + 2, _dim(BRASS, 5, night))
    fluid_top = y_glass + 1
    for yy in range(y_glass, y_base):
        f = (yy - fluid_top) / max(1, y_base - fluid_top)
        for xx in range(x0 + 1, x1 - 1):
            u = (xx - x0) / max(1, gw - 1)
            if yy < fluid_top:
                c = (STEEL[6] + ":0.35") if not night else (FLUID[1] + ":0.5")
            elif yy == fluid_top:
                c = FLUID[6]
            else:
                t = (5 if f < 0.1 else 4 if f < 0.55 else 3) + (1 if u < 0.15 else -1 if u > 0.85 else 0)
                c = FLUID[max(1, min(6, t))]
            p.px(xx, yy, c)
        p.px(x0, yy, STEEL[3] if not night else STEEL[2])
        p.px(x1 - 1, yy, STEEL[2] if not night else STEEL[1])
    bx, by = x0 + (gw - bw) // 2, y_base - bh - 1
    BR.brain(p, bx, by, k, night, rim=FLUID[5])
    s = BR.shape(k)
    for i, (ex, ey) in enumerate(s.electrodes):
        ax, ay = bx + ex, by + ey
        tx = x0 + 3 + i * (gw - 6) // max(1, len(s.electrodes) - 1)
        for (qx, qy) in trace([(tx + 0.5, y_glass + 0.5), (ax + 0.5, ay - 0.5)])[:-1]:
            if qy < ay:
                p.px(qx, qy, (STEEL[1] if i != 1 else TISSUE[2]) if not night else (ROOM[0] if i != 1 else TISSUE[1]))
    sock = bx + round(67 * k)
    for xx in range(sock - 1, sock + round(8 * k) + 1):
        p.px(xx, y_base - 1, _dim(BRASS, 4, night))
    for yy in range(y_glass + 1, y_base - 1):
        p.px(x0 + 1, yy, C["white"] + ":0.55" if not night else FLUID[6] + ":0.4")
    for yy in range(y_glass, y_base):
        p.px(x0 - 1, yy, _dim(BRASS, 4, night))
        p.px(x1, yy, _dim(BRASS, 2, night, 1))
    _cap(p, x, x + W, y, 3, night, top=True)
    _cap(p, x, x + W, y_base, 2, night, top=False)
    return W, H


# The jar at its smallest, a mark on a line: a lumpy brain of nine cells, creased, its stem on the lower cap.
TINY_BRAIN = ["ffPPPPPff", "fPPpoPPpf", "PpopPpopP", "ppPpopPpd", "fdppdppdf", "ffffsdfff"]
TINY_JAR = (["..ccccccccc..", "cCCCCCCCCCCCc", ".gwffffffffg."] + [f".g{row}g." for row in TINY_BRAIN]
            + ["cCCCCCCCCCCCc", ".eeeeeeeeeee.", ".eeEeeeeeeee."])


def tiny_jar(p: Pix, x, y, night) -> tuple:
    """The jar at its smallest, 13 by 12, as a mark: its top left at (x, y). Returns its (w, h)."""
    pal = {"c": _dim(BRASS, 3, night), "C": _dim(BRASS, 5, night), "g": STEEL[3] if not night else STEEL[2],
           "w": C["white"] if not night else FLUID[6], "f": FLUID[4] if not night else FLUID[5],
           "P": TISSUE[5] if not night else TISSUE[4], "p": TISSUE[3], "o": TISSUE[1], "d": TISSUE[2],
           "s": TISSUE[2], "e": _dim(ENAMEL, 3, night), "E": FLUID[5]}
    p.sprite(x, y, TINY_JAR, pal)
    return len(TINY_JAR[0]), len(TINY_JAR)


def _cap(p: Pix, x0, x1, y, h, night, top):
    """A cap of brass, lit along its top and riveted, the upper one domed."""
    B = BRASS
    for i in range(h):
        inset = (3 if i == 0 else 1 if i == 1 else 0) if top else 0
        yy = y + i
        for x in range(x0 + inset, x1 - inset):
            u = (x - x0) / max(1, x1 - x0 - 1)
            t = 6 if i == 0 else 5 if i == 1 else (4 if u < 0.7 else 3) if i < h - 1 else 2
            if u < 0.06 and 0 < i < h - 1:
                t = 5
            p.px(x, yy, _dim(B, t, night))
        if 1 < i < h - 1 or (not top and 0 < i < h - 1):
            for x in range(x0 + 3, x1 - 3, 5):
                p.px(x, yy, B[6] if not night else B[3])
                p.px(x + 1, yy, B[2] if not night else B[0])
    for x in range(x0, x1):
        p.px(x, y + h, STEEL[1] if not night else ROOM[0])


def gauge(p: Pix, cx, cy, night):
    """A pressure gauge on the jar's cap: a dial in a ring of brass, its needle up."""
    for (x, y) in ellipse(cx + 0.5, cy + 0.5, 3.2, 3.2):
        d = math.hypot(x + 0.5 - cx - 0.5, y + 0.5 - cy - 0.5)
        p.px(x, y, _dim(BRASS, 5 if (x - cx) + (y - cy) < 0 else 3, night) if d > 2.2 else
             (C["white"] if not night else SAGE[3]))
    p.px(cx, cy, TISSUE[2])
    p.px(cx + 1, cy - 1, TISSUE[2])
    for x in range(cx - 1, cx + 2):
        p.px(x, cy + 3, _dim(BRASS, 2, night))


def _console(p: Pix, cx, y0, foot, w, night, face, z):
    """The console the jar stands on: a cabinet of petrol enamel, its top lit, vents along its left, two knobs of
    brass at its right and the screen set in its middle."""
    x0, x1 = cx - w // 2, cx - w // 2 + w
    E = ENAMEL
    for y in range(y0, foot + 1):
        for x in range(x0, x1):
            t = 3
            if y == y0:
                t = 5
            elif y == y0 + 1:
                t = 4
            elif x == x0:
                t = 4
            elif x == x1 - 1 or y >= foot - 1:
                t = 1
            p.px(x, y, _dim(E, t, night))
    # its vents and its knobs
    vy = y0 + 4
    for i in range(3):
        for x in range(x0 + 3, x0 + 3 + max(3, w // 9)):
            if vy + i * 2 < foot - 2:
                p.px(x, vy + i * 2, E[1] if not night else E[0])
    for j, kx in enumerate((x1 - 6, x1 - 6)):
        ky = y0 + 4 + j * 5
        if ky + 2 < foot - 1:
            for (x, y) in ellipse(kx + 0.5, ky + 0.5, 1.6, 1.6):
                p.px(x, y, _dim(BRASS, 5 if (x - kx) + (y - ky) < 0 else 3, night))
            p.px(kx, ky - 1, C["white"] if not night else BRASS[2])
    if face:
        if z["w"] >= 56:
            sw, sh = min(32, w - 22), z["console"] - 5
        else:
            sw, sh = min(19, w - 14), min(13, z["console"] - 3)
        face(p, cx - sw // 2, y0 + 3, sw, sh)


def bubbles(p: Pix, x0, x1, y0, y1, night, seed=1, n=3):
    """Bubbles rising through the fluid, each on a loop of its own, wobbling as they climb."""
    key = ("bubble", night)
    if key not in p.syms:
        p.symbol(key, {(0, 0): C["white"], (1, 0): FLUID[6], (0, 1): FLUID[6], (1, 1): FLUID[5]})
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.randrange(x0, max(x0 + 1, x1 - 1))
        path = [(x + round(math.sin(i + j * 0.7)), y) for j, y in enumerate(range(y1, y0, -2))]
        if len(path) > 3:
            path += [path[-1]]
            signal(p, key, path, len(path) * rnd.uniform(0.09, 0.14))


# --------------------------------------------------------------------------- the screens
def screen(p: Pix, x, y, w, h, night):
    """A screen set into a machine: a bezel of steel with its corners rounded, glass dark green-black with its scan
    lines, and by night its glow."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            corner = (xx in (x, x + w - 1)) and (yy in (y, y + h - 1))
            if corner:
                continue
            edge_ = xx in (x, x + w - 1) or yy in (y, y + h - 1)
            if edge_:
                lit = xx == x or yy == y
                c = (STEEL[5] if lit else STEEL[2]) if not night else (STEEL[3] if lit else STEEL[1])
            else:
                c = ROOM[2] if (yy - y) % 2 else ROOM[1]
            p.px(xx, yy, c)
    if night:
        p.halo(x + w / 2, y + h / 2, w * 0.75, h * 0.85, FLUID[4], (0.05, 0.1), L="haze", shape=True)


def scope(p: Pix, x0, y0, w, h, night, motion, name="wave"):
    """An oscilloscope on the wall: a case of enamel, its screen ruled in a faint grid, the brain's waves sweeping
    across it, and its knobs underneath."""
    E = ENAMEL
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            t = 5 if y == y0 or x == x0 else 1 if (y == y0 + h - 1 or x == x0 + w - 1) else 3
            p.px(x, y, _dim(E, t, night))
    sx0, sy0, sw, sh = x0 + 3, y0 + 3, w - 6, h - 9
    screen(p, sx0, sy0, sw, sh, night)
    for x in range(sx0 + 1, sx0 + sw - 1):
        for y in range(sy0 + 1, sy0 + sh - 1):
            if (x - sx0) % 6 == 0 or (y - sy0) % 5 == 0:
                p.px(x, y, ROOM[3] if not night else ROOM[4])
    for i, kx in enumerate(range(x0 + 6, x0 + w - 4, max(6, (w - 8) // 4))):
        ky = y0 + h - 4
        p.px(kx, ky, _dim(BRASS, 5, night))
        p.px(kx + 1, ky, _dim(BRASS, 3, night))
        p.px(kx, ky + 1, _dim(BRASS, 2, night))
        p.px(kx + 1, ky + 1, _dim(BRASS, 1, night, 1))
    wave(p, sx0 + 1, sx0 + sw - 1, sy0 + sh // 2, max(2, sh // 2 - 2), night, motion, name)
    return (x0, y0, x0 + w, y0 + h)


def wave(p: Pix, x0, x1, y, amp, night, motion, name="wave"):
    """The brain's waves, sweeping across a screen from x0 to x1 about row `y`, one step at a time, wrapping round so
    the loop never shows a seam; the still file holds where they are."""
    period = x1 - x0
    anim = None
    if motion and not p.lite:
        cid = f"{name}c"
        p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y - amp - 1}" width="{period}" '
                      f'height="{2 * amp + 3}"/></clipPath>')
        anim = ("drift", x0, y - amp - 1, x1, y + amp + 2, period, cid, 0.08)
    L = p.layer(name, anim, z=3)
    ys = []
    for i in range(period):
        t = 2 * math.pi * i / period
        v = (0.5 * math.sin(4 * t) * (0.6 + 0.4 * math.sin(2 * t)) + 0.3 * math.sin(9 * t + 1.1)
             + 0.2 * math.sin(17 * t + 0.4) + (0.9 if i % max(8, period // 3) == 0 else 0))
        ys.append(round(y - amp * max(-1.0, min(1.0, v))))
    ink = FLUID[6] if night else FLUID[5]
    for i in range(period):
        a, b = ys[i], ys[(i + 1) % period]
        for yy in range(min(a, b), max(a, b) + 1):
            p.px(x0 + i, yy, ink, L)


# --------------------------------------------------------------------------- the mainframe
def mainframe_size(k: float) -> tuple:
    """Its width with its side, and its height with its top."""
    W, Hh, d = round(36 * k), round(60 * k), max(3, round(6 * k))
    return W + d, Hh + d


def mainframe(p: Pix, x0: int, foot: int, k: float, night: bool, motion: bool):
    """The mainframe the brain works with: a cabinet of petrol enamel seen a little from the side, two tape reels
    turning behind its window, a row of switches, a terminal writing line after line, a panel of lights winking,
    its vents, and the paper it prints curling to the floor."""
    W, Hh, d = round(36 * k), round(60 * k), max(3, round(6 * k))
    y0 = foot - Hh + 1
    E = ENAMEL
    # its top and its side, seen a little from the right
    for i in range(1, d + 1):
        for x in range(x0 + i, x0 + W + i):
            p.px(x, y0 - i, _dim(E, 5 if i < d else 4, night))
    for j in range(d):
        for y in range(y0 - j, foot - j + 1):
            p.px(x0 + W + j, y, _dim(E, 2 if j < d - 1 else 1, night, 1))
    # its front
    for y in range(y0, foot + 1):
        for x in range(x0, x0 + W):
            t = 3
            if y == y0 or x == x0:
                t = 4
            elif y >= foot - 1:
                t = 1
            p.px(x, y, _dim(E, t, night))
    # the window and its two reels
    wy0, wy1 = y0 + max(2, round(3 * k)), y0 + round(20 * k)
    for y in range(wy0, wy1):
        for x in range(x0 + 2, x0 + W - 2):
            edge_ = y in (wy0, wy1 - 1) or x in (x0 + 2, x0 + W - 3)
            p.px(x, y, (STEEL[2] if not night else STEEL[1]) if edge_ else (ROOM[2] if not night else ROOM[1]))
    r = max(3, round(7 * k))
    centres = [(x0 + W // 4 + 1, (wy0 + wy1) // 2), (x0 + 3 * W // 4 - 1, (wy0 + wy1) // 2)]
    for (rx, ry) in centres:
        for (x, y) in ellipse(rx + 0.5, ry + 0.5, r + 0.5, r + 0.5):
            dd = math.hypot(x - rx, y - ry)
            c = STEEL[1] if dd > r * 0.42 else _dim(BRASS, 4, night)
            if r - 0.7 < dd:
                c = STEEL[5] if not night else STEEL[2]
            p.px(x, y, c)
    if not night:
        p.px(x0 + 4, wy0 + 1, C["white"] + ":0.7")
        p.px(x0 + 5, wy0 + 1, C["white"] + ":0.4")
    frames = 3
    for f in range(frames):
        L = p.seq(f"reel{f}", f / frames, (f + 1) / frames, 0.9, keep=f == 0, z=1) if motion and not p.lite else (
            "base" if f == 0 else None)
        if L is None:
            continue
        for (rx, ry) in centres:
            for j in range(3):
                a = f * (2 * math.pi / 3) / frames + j * 2 * math.pi / 3
                for t in range(1, r):
                    if t > r * 0.42:
                        p.px(round(rx + t * math.cos(a)), round(ry + t * math.sin(a)), STEEL[5] if not night else
                             STEEL[3], L)
    # a row of switches
    sy = wy1 + 2
    for i, x in enumerate(range(x0 + 4, x0 + W - 3, 4)):
        p.px(x, sy, STEEL[1] if not night else ROOM[0])
        p.px(x, sy - (1 if i % 3 else 0) + (0 if i % 3 else 1), _dim(STEEL, 6, night, 3))
    # the terminal, writing line after line, its cursor blinking
    ty0 = sy + 3
    th = max(8, round(13 * k))
    tx0, tw = x0 + 3, W - 6
    screen(p, tx0, ty0, tw, th, night)
    lines = max(2, (th - 3) // 2)
    for i in range(lines):
        ln = [tw - 6, tw - 11, tw - 8, tw - 13, tw - 7][i % 5]
        L = p.seq(f"line{i}", i / (lines + 1), 1.0, 5.0, keep=True, z=2) if motion and not p.lite else "base"
        for x in range(tx0 + 2, tx0 + 2 + max(2, ln)):
            if (x - tx0) % 5 != 4:
                p.px(x, ty0 + 2 + i * 2, FLUID[5] if not night else FLUID[6], L)
    cy_ = ty0 + 2 + lines * 2
    if cy_ < ty0 + th - 1:
        p.px(tx0 + 2, cy_, FLUID[6], p.blink(0) if motion and not p.lite else "base")
    # the panel of lights
    ly = ty0 + th + 2
    cols = max(3, (W - 6) // 3)
    for row in range(2):
        for i in range(cols):
            x, y = x0 + 3 + i * 3, ly + row * 3
            col = (NIXIE[4], FLUID[4], TISSUE[4])[(i + row * 2) % 3]
            p.px(x, y, STEEL[1] if not night else ROOM[0])
            p.px(x + 1, y, STEEL[1] if not night else ROOM[0])
            if motion and not p.lite:
                Lt = p.twinkle(i + row)
                p.px(x, y, col, Lt)
                p.px(x + 1, y, col, Lt)
            elif (i + row) % 2 == 0:
                p.px(x, y, col)
                p.px(x + 1, y, col)
    # the printer's slot, and its printout: fanfold paper, green-barred, holed along both edges for the tractor,
    # hanging from the slot and folding onto the floor in front of the cabinet
    sy = ly + 7
    if sy + 4 < foot:
        for x in range(x0 + 4, x0 + W - 4):
            p.px(x, sy, ROOM[0])
        pw = max(8, W - 14)
        px0 = x0 + (W - pw) // 2
        bar = SAGE[5] if not night else SAGE[2]
        sheet = C["white"] if not night else SAGE[3]
        holes = STEEL[3] if not night else STEEL[1]
        fold = foot - 3
        for i, y in enumerate(range(sy + 1, fold)):
            for dx in range(pw):
                c = bar if (i // 2) % 2 else sheet
                if dx in (1, pw - 2) and i % 2 == 0:
                    c = holes
                elif 3 < dx < pw - 4 and i % 2 == 1 and (dx + i) % 9 > 1 and (i // 2) % 2 == 0:
                    c = STEEL[2] if not night else STEEL[1]
                p.px(px0 + dx, y, c)
        # the folded stack on the floor, each fold a little offset
        for j, y in enumerate(range(fold, foot + 1)):
            off = (j % 2) * 2
            for dx in range(pw + 2):
                c = sheet if dx < pw + 1 else (SAGE[3] if not night else SAGE[1])
                if dx in (0, pw + 1) or y == foot:
                    c = SAGE[3] if not night else SAGE[1]
                p.px(px0 - 1 + dx + off, y, c)
    return (x0, y0 - d, x0 + W + d, foot)


# --------------------------------------------------------------------------- the coil and its lightning
def coil(p: Pix, cx: int, foot: int, k: float, night: bool, motion: bool, toward=None):
    """A Tesla coil: a base of enamel under a plate of brass, a few heavy turns of copper at the foot of a column
    wound fine in brass, and a torus of steel at its top, lightning leaping from it in turn."""
    bw, ch = max(10, round(18 * k)), max(12, round(34 * k))
    by = foot - max(4, round(7 * k)) + 1
    for y in range(by, foot + 1):
        for x in range(cx - bw // 2, cx - bw // 2 + bw):
            t = 5 if y == by else 1 if (y >= foot - 1 or x == cx - bw // 2 + bw - 1) else 3
            p.px(x, y, _dim(ENAMEL, t, night))
    for x in range(cx - bw // 2 + 1, cx - bw // 2 + bw - 1):
        p.px(x, by - 1, _dim(BRASS, 5, night))
    cw = max(3, round(7 * k))
    top = by - 1 - ch
    for y in range(top, by - 1):
        for x in range(cx - cw // 2, cx - cw // 2 + cw):
            wound = (y - top) % 2 == 0
            u = (x - (cx - cw // 2)) / max(1, cw - 1)
            t = (6 if u < 0.2 else 5 if u < 0.6 else 3) if wound else (4 if u < 0.2 else 3 if u < 0.6 else 1)
            p.px(x, y, _dim(BRASS, t, night))
    # the primary: three heavy turns of copper round the column's foot
    for i in range(3):
        y = by - 3 - i * 2
        for x in range(cx - cw // 2 - 3, cx - cw // 2 + cw + 3):
            p.px(x, y, _dim(NIXIE, 3 if x < cx else 2, night))
    tw, th = max(10, round(22 * k)), max(5, round(9 * k))
    ty = top - th + 1
    hole = ellipse(cx + 0.5, ty + th * 0.42, tw * 0.2, max(0.8, th * 0.16))
    for (x, y) in ellipse(cx + 0.5, ty + th / 2, tw / 2, th / 2):
        if (x, y) in hole:
            p.px(x, y, STEEL[1] if not night else STEEL[0])
            continue
        f = (y - ty) / th
        u = (x - (cx - tw / 2)) / tw
        t = 6 if f < 0.2 else 5 if f < 0.45 else 4 if f < 0.7 else 2
        if u > 0.8 and t > 2:
            t -= 1
        p.px(x, y, STEEL[t] if not night else STEEL[max(1, t - 2)])
    for (x, y) in hole:
        if (x, y - 1) not in hole:
            p.px(x, y, STEEL[0])
    if night:
        glow(p, cx, ty + th / 2, tw * 1.4, th * 3.4, ARC[4], (0.06, 0.12, 0.18), shape=True)
    arcs(p, cx, ty + th // 2, tw // 2 + 1, k, night, motion, toward)
    return (cx - max(bw, tw) // 2, ty, cx + max(bw, tw) // 2 + 1, foot)


def bolt(rnd, x0, y0, x1, y1, jag=2.0) -> list:
    """A bolt of lightning from (x0, y0) to (x1, y1): a few sharp zigzags, as lightning forks, not a scribble."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 6))
    pts = [(x0, y0)]
    for i in range(1, n):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + rnd.uniform(-jag, jag), y0 + (y1 - y0) * t + rnd.uniform(-jag, jag)))
    pts.append((x1, y1))
    return trace(pts)


def strike(p: Pix, cells, night, L, rnd=None, forks=0, thick=False, flash=False):
    """A bolt's cells drawn as lightning: a white core, a violet glow about it, a fork or two off it, and with
    `flash` a burst of light where it strikes. By day the violet edges it all round, so its white reads against the
    lit wall."""
    core = ARC[6] if night else C["white"]
    if flash and cells:
        ex, ey = cells[-1]
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            p.px(ex + dx, ey + dy, core, L)
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            p.px(ex + dx, ey + dy, ARC[5] + ":0.7", L)
    body = set(cells)
    if thick:
        body |= {(x + 1, y) for x, y in cells[len(cells) // 4: 3 * len(cells) // 4]}
    for (x, y) in body:
        p.px(x, y, core, L)
    sides = ((0, 1), (1, 0)) if night else ((0, 1), (1, 0), (0, -1), (-1, 0))
    for (x, y) in body:
        for dx, dy in sides:
            if (x + dx, y + dy) not in body:
                p.px(x + dx, y + dy, ARC[4] + ":0.6" if night else ARC[3] + ":0.75", L)
    if rnd and forks:
        for _ in range(forks):
            sx, sy = cells[rnd.randrange(len(cells) // 4, max(len(cells) // 4 + 1, len(cells) - 2))]
            a = rnd.uniform(0, 6.3)
            ln = rnd.uniform(4, 8)
            for (x, y) in bolt(rnd, sx, sy, sx + ln * math.cos(a), sy + ln * math.sin(a), jag=1.2):
                p.px(x, y, ARC[5] if night else ARC[3], L)


def arcs(p: Pix, cx, cy, r, k, night, motion, toward=None, frames=3):
    """Lightning leaping off the coil's torus, one bolt at a time, each shown for its moment in turn and reaching for
    the jar when there is one; the still file keeps the first."""
    if p.lite:
        return
    rnd = random.Random(int(cx * 7 + cy))
    for f in range(frames):
        L = p.seq(f"arc{f}", f / frames, f / frames + 0.26, 0.75, keep=f == 0, z=10) if motion else (
            "base" if f == 0 else None)
        if L is None:
            continue
        if toward:
            tx, ty = toward[0], toward[1] + rnd.uniform(-3, 3)
        else:
            a = rnd.uniform(-2.9, -1.4)
            ln = rnd.uniform(12, 20) * max(0.7, k)
            tx, ty = cx + r * math.cos(a) + ln * math.cos(a), cy + r * 0.3 * math.sin(a) + ln * math.sin(a)
        sx = cx + (r if tx > cx else -r)
        strike(p, bolt(rnd, sx, cy, tx, max(CEILING + 1, ty), jag=2.4), night, L, rnd, forks=1, thick=True,
               flash=toward is not None)
