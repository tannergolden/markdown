# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The ship's main deck, cut away, for a section header and a phone's.

The hull is opened along its near side, so the deck stands framed in the cut edge of its plating, a band of riveted
steel rounded at its upper corner: the far wall of riveted plates on its ribs, the conduits along the deckhead with
cables slung in loops off them, a ladder up to the hatch, work lamps hanging in their cages, and the grating of the
deck. At the left the operator's post, a rack of old monitors running the code in phosphor over the console, and the
operator on his chair before it with his headset on, his back to us; at the right the chair, its leather worn, and a
crew member lying back in it with her eyes shut, jacked in, the cable rising from the back of her head to a junction
box on the deckhead, a lamp on the chair's arm blinking while she is under. By night the screens and the lamps are
the only light: the code lights the operator's back and the wall round the rack, and the lamps pool on the deck."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Pix
from .art import _shade, _t
from .palette import RAMP

STEEL, PLATE, RUST, BRICK, DRAB = RAMP["steel"], RAMP["plate"], RAMP["rust"], RAMP["brick"], RAMP["drab"]
FLAME = RAMP["flame"]
SKIN_OP, SKIN_JACK = RAMP["skin2"], RAMP["skin0"]
CRT_W, CRT_H = 14, 11      # a monitor, its casing round a screen ten by seven
CODE_LOOP = 1.2            # the seconds the code takes to fall through its four frames


# --------------------------------------------------------------------------- the code on the screens
def _code_frame(f: int, seed: int) -> dict:
    """One frame of the code falling down a screen ten by seven, {(x, y): colour}: a stream down every other column,
    each a bright head with its trail fading behind it, two rows further down in each frame."""
    rnd = random.Random(seed)
    cells = {}
    for x in range(0, 10, 2):
        start = rnd.randrange(12)
        trail = rnd.randint(2, 4)
        head = (start + f * 3) % 12 - 2
        for j in range(trail + 1):
            y = head - j
            if 0 <= y < 7:
                cells[(x, y)] = FLAME[6] if j == 0 else FLAME[4] if j == 1 else FLAME[3] if j == 2 else FLAME[2]
    return cells


def _crt(p: Pix, x, y, night: bool):
    """A monitor's casing at (x, y), CRT_W by CRT_H: grey plastic gone yellow, lit along its top and left, a dark
    screen in it and its power light; the code is laid over the screen (see `screens`)."""
    k = -2 if night else 0
    q = _shade(PLATE, k)
    p.box(x, y, CRT_W, CRT_H, STEEL[0])
    p.rect(x + 1, y + 1, CRT_W - 2, CRT_H - 2, q(3))
    p.hline(x + 1, x + CRT_W - 1, y + 1, q(5))
    p.vline(x + 1, y + 2, y + CRT_H - 1, q(4))
    p.vline(x + CRT_W - 2, y + 2, y + CRT_H - 1, q(1))
    p.hline(x + 2, x + CRT_W - 1, y + CRT_H - 2, q(1))
    p.rect(x + 2, y + 2, 10, 7, FLAME[0] if night else STEEL[0])
    p.px(x + CRT_W - 3, y + CRT_H - 2, FLAME[4])


def screens(p: Pix, spots: list, night: bool, motion: bool):
    """The code falling down each screen whose top-left is in `spots`, in four frames on a loop, each screen a frame
    on from the last; the still file holds the first. Each frame is drawn once and placed on every screen."""
    keys = []
    for f in range(4):
        key = ("code", f)
        if key not in p.syms:
            p.symbol(key, _code_frame(f, 11))
        keys.append(key)
    for f in range(4):
        if motion:
            L = p.seq(f"cd{f}", f / 4, (f + 1) / 4, CODE_LOOP, keep=f == 0, z=1)
        elif f:
            break
        else:
            L = "base"
        for i, (sx, sy) in enumerate(spots):
            p.use(keys[(f + i * 3) % 4], sx, sy, L)


# --------------------------------------------------------------------------- the people
# The operator from behind on his chair: H his hair, h its light, s and S his skin, P his headset and p its light, m
# its mic, K his sweater, L its light, k its shade, x where it is worn through, a his arms reaching for the keys, B
# the chair's back, b its light, c its column and foot.
OPERATOR = [
    ".....HHHH.....",
    "....HhhhHH....",
    "...PHhhHHHP...",
    "...pHHHHHHp...",
    "...PsHHHHsP...",
    "...mssSSss....",
    "..LLLKKKKKkk..",
    ".aLLKKKKKKkka.",
    "aaLKKKxKKKKkaa",
    "aLLKKKKKKKKkka",
    ".LLKKKKKKxKkk.",
    ".LKKbbbbbbbkk.",
    "..KbBBBBBBBk..",
    "...bBBBBBBBk..",
    "...bBBBBBBBk..",
    "....kkkkkkk...",
    "......cc......",
    "......cc......",
    "......cc......",
    "....cccccc....",
]


def operator(p: Pix, x, g, night: bool) -> tuple:
    """The operator on his chair at column x on the deck at row g, seen from behind as he watches the code: his hair
    cropped close, a headset over it with its mic at his cheek, a knitted sweater worn through, his elbows out as he
    types. Returns the top-left of his drawing."""
    k = -1 if night else 0
    s = _shade(STEEL, -2 if night else 0)
    pal = {"H": SKIN_OP[0], "h": SKIN_OP[1], "s": SKIN_OP[2], "S": SKIN_OP[3], "P": s(1), "p": s(5), "m": s(1),
           "K": _t(DRAB, 4 + k), "k": _t(DRAB, 2 + k), "L": _t(DRAB, 5 + k), "x": _t(DRAB, 1 + k),
           "a": _t(DRAB, 3 + k), "B": s(2), "b": s(4), "c": s(3)}
    top = g - len(OPERATOR) + 1
    p.sprite(x, top, OPERATOR, pal)
    return x, top


def _spine(pts, x):
    """The row of the chair's seat at column x, along the polyline `pts`."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if ax <= x <= bx:
            return ay + (by - ay) * (x - ax) / max(1, bx - ax)
    return pts[-1][1]


# Her head, lying back on the headrest with her face turned up: h and H her hair, S and s her skin, n her nose, e her
# shut eye.
HEAD = ["......n..", "..hhhSSS.", ".hHHSSeSS", "hHHHSSSSS", "hHHHSSSSs", ".hHHssSs.", "..HH.ss.."]


def chair(p: Pix, x, g, night: bool, motion: bool) -> tuple:
    """The chair at column x on the deck at row g, and the crew member jacked in on it: a reclined chair of worn
    leather on a steel column, its headrest at the left with the port in it; she lies back on it, her eyes shut, her
    hair against the headrest, in a ragged tunic, her arm along her side, her boots at its foot. A lamp on the chair's
    arm blinks while she is under. Returns where the port is, for the cable, and the span the chair takes."""
    k = -2 if night else 0
    s = _shade(STEEL, k)
    lb = _shade(BRICK, -1 if night else 0)
    hx, hy = x + 5, g - 21                   # the head end of the seat
    n = 46
    pts = [(hx, hy), (hx + 20, hy + 7), (hx + 33, hy + 7), (hx + n - 1, hy + 12)]
    cx = hx + 25                             # the column and its foot
    p.vline(cx, hy + 12, g - 1, s(5))
    p.vline(cx + 1, hy + 12, g - 1, s(3))
    p.vline(cx + 2, hy + 12, g - 1, STEEL[0])
    p.rect(cx - 6, g - 2, 15, 2, s(3))
    p.hline(cx - 6, cx + 9, g - 2, s(5))
    p.hline(cx - 6, cx + 9, g, STEEL[0])
    p.rect(cx - 2, hy + 11, 7, 2, s(4))
    for xx in range(hx - 1, hx + n):         # the seat, five rows of leather under its line, a seam along it
        y = round(_spine(pts, xx))
        for j, c in enumerate((lb(6), lb(5), lb(4), lb(3), lb(2))):
            p.px(xx, y + j, c)
        p.px(xx, y + 5, BRICK[0])
        if xx % 7 == 3:
            p.px(xx, y + 2, lb(3))
    end = round(_spine(pts, hx + n - 1))
    p.vline(hx - 2, hy, hy + 6, BRICK[0])
    p.vline(hx + n, end, end + 6, BRICK[0])
    p.rect(hx - 4, hy - 9, 6, 10, lb(4))     # the headrest, the port in it
    p.vline(hx - 4, hy - 9, hy + 1, lb(5))
    p.hline(hx - 4, hx + 2, hy - 9, lb(6))
    p.vline(hx + 1, hy - 8, hy + 1, lb(2))
    p.box(hx - 5, hy - 10, 8, 12, BRICK[0])
    p.rect(hx - 3, hy - 5, 2, 3, s(5))
    p.px(hx - 2, hy - 4, STEEL[0])
    ax = hx + 18                             # the arm, its lamp
    p.hline(ax, ax + 15, hy + 2, s(5))
    p.hline(ax, ax + 15, hy + 3, s(2))
    p.vline(ax + 9, hy + 4, hy + 8, s(3))
    p.rect(ax + 13, hy - 1, 3, 3, s(3))
    p.hline(ax + 13, ax + 16, hy - 1, s(5))
    p.px(ax + 14, hy - 2, FLAME[5] if night else FLAME[4], p.blink(2) if motion else "base")
    pal = {"H": BRICK[0], "h": BRICK[2], "S": SKIN_JACK[3], "s": SKIN_JACK[2], "n": SKIN_JACK[3],
           "e": SKIN_JACK[1]}
    p.sprite(hx - 2, hy - 8, HEAD, pal)
    t = _shade(PLATE, -3 if night else -1)
    for xx in range(hx + 5, hx + n):         # her tunic, her legs and her boots
        y = round(_spine(pts, xx))
        if xx < hx + 21:
            top = y - 6 + (1 if xx < hx + 8 else 0)
            for yy in range(top, y):
                p.px(xx, yy, t(5) if yy == top else t(4) if yy == top + 1 else t(3) if yy < y - 1 else t(1))
            if xx in (hx + 11, hx + 16):
                p.px(xx, top + 3, t(1))      # worn through
        elif xx < hx + n - 5:
            for yy in range(y - 4, y):
                p.px(xx, yy, _t(DRAB, (4 if yy == y - 4 else 3 if yy == y - 3 else 2 if yy == y - 2 else 1) + k // 2))
            if xx == hx + 33:
                p.px(xx, y - 3, _t(DRAB, 1 + k // 2))
        else:
            for yy in range(y - 7, y):
                p.px(xx, yy, s(1) if yy > y - 7 else s(5))
            p.px(xx, y - 6, s(3))
    for i in range(12):                      # her arm along her side, her hand at its end
        xx = hx + 8 + i
        yy = round(_spine(pts, xx)) - 4 + i // 5
        p.px(xx, yy, t(6))
        p.px(xx, yy + 1, t(2))
    p.rect(hx + 20, round(_spine(pts, hx + 20)) - 2, 2, 2, SKIN_JACK[3])
    p.rect(hx + 5, hy - 4, 2, 3, SKIN_JACK[2])   # her neck
    return (hx - 4, hy - 4), (x, hx + n + 1)


def cable(p: Pix, a: tuple, b: tuple, night: bool, sag: float = 6.0, thick: bool = True):
    """A black cable from a to b, sagging `sag` rows at its middle, lit along one side."""
    k = -2 if night else 0
    (ax, ay), (bx, by) = a, b
    n = max(abs(bx - ax), abs(by - ay), 1) * 2
    last = None
    for i in range(n + 1):
        t = i / n
        q = (round(ax + (bx - ax) * t), round(ay + (by - ay) * t + sag * math.sin(math.pi * t)))
        if q == last:
            continue
        last = q
        p.px(q[0], q[1], STEEL[0])
        if thick:
            p.px(q[0] + 1, q[1], _t(STEEL, 3 + k))


def jack(p: Pix, a: tuple, b: tuple, night: bool):
    """The cable that jacks her in, thick and black, from the junction box at a down to the port in the headrest at
    b, swinging out to the right as it falls, lit down its left side; by night a thread of phosphor runs in it."""
    k = -2 if night else 0
    (ax, ay), (bx, by) = a, b
    n = (by - ay) * 2
    last = None
    for i in range(n + 1):
        t = i / n
        x = ax + (bx - ax) * t * t + 7 * math.sin(math.pi * t) * (1 - t)
        q = (round(x), round(ay + (by - ay) * t))
        if q == last:
            continue
        last = q
        p.px(q[0] - 1, q[1], _t(STEEL, 4 + k))
        p.px(q[0], q[1], STEEL[0])
        p.px(q[0] + 1, q[1], STEEL[0] if not night else (FLAME[2] if q[1] % 3 else FLAME[3]))
        p.px(q[0] + 2, q[1], _t(STEEL, 1 + k))


def lamp(p: Pix, x, y0, y, night: bool, motion: bool, phase: int):
    """A work lamp hanging on its flex from row y0 at column x, its cage at row y: a steel shade over a bulb in a
    wire cage, the bulb pale by day and burning phosphor by night, flickering."""
    k = -2 if night else 0
    s = _shade(STEEL, k)
    p.vline(x, y0, y, s(1))
    p.rect(x - 2, y, 5, 2, s(4))
    p.hline(x - 3, x + 4, y + 2, s(2))
    bulb = p.flicker(phase) if motion and night else "base"
    p.rect(x - 1, y + 3, 3, 2, FLAME[5] if night else PLATE[6], bulb)
    p.px(x, y + 5, FLAME[6] if night else PLATE[5], bulb)
    for dx in (-2, 2):
        p.vline(x + dx, y + 3, y + 6, s(1))
    p.hline(x - 1, x + 2, y + 6, s(1))


# --------------------------------------------------------------------------- the deck
def deck(p: Pix, x0, x1, g, night: bool, motion: bool, top: int) -> tuple:
    """The main deck, cut away, from column x0 to x1 and row `top` down to the deck at row g (see the module's
    docstring); where the deck is too narrow for the operator's post and the chair both, the chair alone. Returns
    the span of the rule it stands on."""
    k = -3 if night else 0
    s = _shade(STEEL, k)
    w = x1 - x0
    hold = p.layer("hold", z=-1)             # the far wall: plates on their ribs, a seam, a rivet down each rib
    wall = s(2) if night else s(3)
    p.shapes[hold].append(f'<rect x="{x0 + 4}" y="{top + 4}" width="{w - 4}" height="{g - top - 4}" fill="{wall}"/>')
    for yy in range(top + 18, g - 3, 12):
        p.hline(x0 + 4, x1, yy, s(1), hold)
        p.hline(x0 + 4, x1, yy + 1, s(3), hold)
    for xx in range(x0 + 20, x1 - 2, 24):
        p.vline(xx, top + 4, g - 3, s(4), hold)
        p.vline(xx + 1, top + 4, g - 3, s(3), hold)
        p.vline(xx + 2, top + 4, g - 3, s(0), hold)
        for yy in range(top + 14, g - 4, 12 if p.lite else 6):     # a drawing made lighter rivets every other
            p.px(xx, yy, s(6), hold)
    for yy, tone in ((top + 5, 4), (top + 9, 3)):  # the conduits along the deckhead
        p.hline(x0 + 4, x1, yy, s(tone + 2))
        p.hline(x0 + 4, x1, yy + 1, s(tone))
        p.hline(x0 + 4, x1, yy + 2, s(1))
    hangers = list(range(x0 + 10, x1 - 4, 22))
    for xx in hangers:
        p.rect(xx, top + 4, 2, 8, s(5))
        p.px(xx + 1, top + 4, s(1))
    for a, b in zip(hangers, hangers[1:]):          # cables slung in loops between the hangers
        cable(p, (a + 1, top + 12), (b, top + 12), night, sag=4 + (a // 7) % 3, thick=False)
    for xx in range(x0 + 4, x1):                    # the deck's grating
        p.px(xx, g - 3, s(5))
        p.px(xx, g - 2, s(3) if xx % 3 else s(1))
        p.px(xx, g - 1, s(1) if xx % 3 else s(0))
        p.px(xx, g, STEEL[0])
    room = w >= 96
    lx_ = x1 - 7                                    # the ladder up to the hatch
    if room:
        for yy in range(top + 13, g - 3):
            p.px(lx_, yy, s(5))
            p.px(lx_ + 4, yy, s(3))
        for yy in range(top + 16, g - 3, 4):
            p.hline(lx_ + 1, lx_ + 4, yy, s(4))
            p.hline(lx_ + 1, lx_ + 4, yy + 1, s(0))
        p.rect(lx_ - 2, top + 4, 9, 3, s(4))
        p.hline(lx_ - 2, lx_ + 7, top + 4, s(6))
        p.hline(lx_ - 2, lx_ + 7, top + 7, STEEL[0])
        p.px(lx_ + 2, top + 5, _t(RUST, 4 + k // 2))
    ox = oy = None
    rx = x0 + 9
    console = g - 12
    if room:                                        # the operator's post
        cols = 2                                    # as many rows of monitors as the deck has room for, five at most,
        rows = max(1, min(5, (console - 1 - (top + 14)) // (CRT_H + 1)))   # keeping the lamp its room over four
        if rows > 4 and console - 1 - rows * (CRT_H + 1) < top + 23:
            rows -= 1
        rack_top = console - 1 - rows * (CRT_H + 1)
        right = rx + cols * (CRT_W + 1)
        for xx in (rx - 2, right):
            p.vline(xx, top + 12, console, s(5))
            p.vline(xx + 1, top + 12, console, s(2))
        spots = []
        for r in range(rows):
            for c in range(cols):
                sx, sy = rx + c * (CRT_W + 1), rack_top + r * (CRT_H + 1)
                _crt(p, sx, sy, night)
                spots.append((sx + 2, sy + 2))
        p.hline(rx - 4, right + 6, console, s(6))
        p.hline(rx - 4, right + 6, console + 1, s(3))
        p.hline(rx - 4, right + 6, console + 2, STEEL[0])
        for xx in range(rx + 3, rx + 24, 2):        # the keyboard
            p.px(xx, console - 1, s(5))
        p.vline(rx - 3, console + 3, g - 3, s(4))
        p.vline(right + 4, console + 3, g - 3, s(4))
        cable(p, (right + 1, console - 4), (right + 6, g - 4), night, sag=2)
        screens(p, spots, night, motion)
        ox, oy = operator(p, rx + 8, g - 4, night)
        if rack_top - 9 >= top + 14:
            lamp(p, rx + 15, top + 12, rack_top - 9, night, motion, 0)
    chx = x0 + 42 if room else x0 + max(4, (w - 56) // 2)
    port, _ = chair(p, chx, g - 4, night, motion)
    jx = chx + 14                                   # the junction box and the cable down to her
    p.rect(jx - 2, top + 12, 6, 5, s(3))
    p.hline(jx - 2, jx + 4, top + 12, s(5))
    p.box(jx - 3, top + 11, 8, 7, STEEL[0])
    p.px(jx + 2, top + 14, FLAME[4])
    jack(p, (jx, top + 18), port, night)
    lamp(p, chx + 38, top + 12, top + 24, night, motion, 2)
    edge = {}                                       # the hull's cut edge, rounded at its upper corner
    r = 8
    for yy in range(top, g + 1):
        for xx in range(x0, x1 + 1):
            dx, dy = max(0, x0 + r - xx), max(0, top + r - yy)
            if dx and dy:
                d = math.hypot(dx, dy)
                if d <= r and d > r - 4:
                    edge[(xx, yy)] = (STEEL[0], s(6), s(4), s(2))[min(3, int(r - d))]
            elif xx < x0 + 4 or yy < top + 4:
                band = min(xx - x0 if xx < x0 + 4 else 9, yy - top if yy < top + 4 else 9)
                edge[(xx, yy)] = (STEEL[0], s(6), s(4), s(2))[band]
    for (xx, yy), c in edge.items():
        p.px(xx, yy, c)
    for yy in range(top + 12, g - 2, 8):
        p.px(x0 + 2, yy, s(6))
        p.px(x0 + 2, yy + 1, s(1))
    for xx in range(x0 + 12, x1 - 2, 8):
        p.px(xx, top + 2, s(6))
        p.px(xx + 1, top + 2, s(1))
    if night:                                       # the light of the code and the lamps
        if room:
            p.halo(rx + 15, console - 22, 34, 30, FLAME[3], (0.05, 0.09, 0.14), L=p.layer("glow", z=-0.5))
            lit = {_t(DRAB, n) for n in range(7)} | {SKIN_OP[0], SKIN_OP[1], SKIN_OP[2]}
            for (xx, yy), c in list(p.layers["base"].items()):
                if ox <= xx < ox + 14 and oy <= yy < oy + 12 and c in lit:
                    p.apx(xx, yy, FLAME[4], 0.32 if yy < oy + 6 else 0.2, "base")
        floor = {s(5), s(3), s(1)}
        p.halo(chx + 38.5, g - 3, 18, 3, FLAME[4], (0.1, 0.2), L="base", only=floor)
        p.halo(chx + 38.5, top + 29, 9, 6, FLAME[4], (0.08, 0.16), L="haze")
        if room:
            p.halo(rx + 15.5, g - 3, 16, 3, FLAME[4], (0.08, 0.16), L="base", only=floor)
    return x0, x1
