# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The scenes the theme's headers stand on: the laboratory, lit by day and dark by night.

Every header stands on the lab's floor the length of its foot (`floor`): two rows of chequered tiles, a skirting of
enamel, and the cables lying along it from one machine to the next, signals running along them. The H1 is the lab
at work: the mainframe at the left, its reels turning, its terminal writing and its lights winking, a heavy cable
across the floor to the brain in its jar at the right, its face on its console's screen. The H2 is the jar drawn as
large as the words leave it, a Tesla coil beside it throwing lightning at it. The H3 is the jar small at the right,
an oscilloscope on the wall beside it wired to it, the brain's waves sweeping across its screen. Each is drawn as
large as the room the words leave it, and nothing comes within two units of a word."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Pix
from . import lab as LB
from . import mood as MD
from . import sheet as S
from .kit import free_rows, reach, signal
from .palette import C, RAMP

FLUID, ENAMEL, BRASS, STEEL, NIXIE, ARC, TISSUE, SAGE, ROOM = (RAMP["fluid"], RAMP["enamel"], RAMP["brass"],
                                                              RAMP["steel"], RAMP["nixie"], RAMP["arc"],
                                                              RAMP["tissue"], RAMP["sage"], RAMP["room"])
TOP = 15            # the highest row a scene reaches, clear of what hangs along the top


# --------------------------------------------------------------------------- the floor
def floor(p: Pix, x0, x1, g, most, night, seed, motion, caps=None, low=5) -> list:
    """The lab's floor the length of a header's foot, its last row at `g`: two rows of chequered tiles, a skirting
    of enamel where the room allows, and two cables lying along it, signals running along them. `caps`, {column:
    rows}, holds it lower where something stands on it. Returns the spans it covers."""
    room = {x: min(free_rows(p, x, x + 1, g, most), low) for x in range(x0, x1)}
    for x, n in (caps or {}).items():
        if x in room:
            room[x] = min(room[x], n)
    uid = getattr(p, "sheet", "p") + "f"
    if uid not in p.syms:
        a, b = ((SAGE[5], SAGE[2]), (STEEL[3], SAGE[2])) if not night else ((ROOM[4], ROOM[2]), (ROOM[3], ROOM[1]))
        p.defs.append(f'<pattern id="{uid}" width="8" height="2" patternUnits="userSpaceOnUse">'
                      f'<path stroke="{a[0]}" d="M0 .5h4"/><path stroke="{a[1]}" d="M4 .5h4"/>'
                      f'<path stroke="{b[1]}" d="M0 1.5h4"/><path stroke="{b[0]}" d="M4 1.5h4"/></pattern>')
        p.syms[uid] = uid
    spans = []
    for need in (2, 3, 4):
        cur = None
        for x in range(x0, x1 + 1):
            ok = x < x1 and room[x] >= need
            if ok:
                cur = [x, x + 1] if cur is None else [cur[0], x + 1]
            elif cur:
                a, b = cur
                if need == 2:
                    p.shapes["base"].append(f'<rect x="{a}" y="{g - 1}" width="{b - a}" height="2" fill="url(#{uid})"/>')
                    spans.append((a, b))
                else:
                    c = (ENAMEL[3] if need == 3 else ENAMEL[5]) if not night else (ENAMEL[1] if need == 3 else ENAMEL[2])
                    p.shapes["base"].append(f'<rect x="{a}" y="{g + 1 - need}" width="{b - a}" height="1" fill="{c}"/>')
                cur = None
    rnd = random.Random(seed)
    ca, cb = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
    run_a, run_b = [], []
    for x in range(x0, x1):
        r = room[x]
        if r >= 2:
            ya = g - 1 - (1 if (math.sin(x / 9 + ca) > 0.35 and r >= 3) else 0)
            yb = g - 1 - (1 if (math.sin(x / 13 + cb) > 0.2 and r >= 3) else 0)
            p.px(x, yb, TISSUE[2] if not night else TISSUE[1])
            p.px(x, ya, STEEL[1] if not night else ROOM[0])
            if x % 3 == 0:
                run_a.append((x, ya))
                run_b.append((x, yb))
    if motion and not p.lite:
        key = ("pulse", night)
        if key not in p.syms:
            p.symbol(key, {(0, 0): NIXIE[6] if night else C["white"], (-1, 0): NIXIE[4], (1, 0): NIXIE[5]})
        for run, n in ((run_a, 0), (run_b, 1)):
            if len(run) > 10:
                path = run[n * len(run) // 3:] + run[:n * len(run) // 3]
                signal(p, key, path[::2] + [path[-1]] * 3, len(path[::2]) * 0.12)
    return spans


# --------------------------------------------------------------------------- the jar in its place
def fit_jar(p: Pix, x0, x1, foot, most=64, least=LB.LEAST, centre=False) -> tuple | None:
    """The widest jar, (cx, w), standing on row `foot` between columns x0 and x1, below row `TOP` and two units
    clear of every word; None when even the narrowest has no room."""
    w = most
    while w >= least:
        half = w // 2 + 6
        cx = (x0 + x1) // 2 if centre else x1 - half - 1
        box = LB.jar_box(cx, foot, w)
        if box[0] >= x0 - 1 and box[1] >= TOP and p.clear_of_words(box[0] - 2, box[1] - 2, box[2] + 2, box[3]):
            return cx, w
        w -= 2
    return None


def pipes_clear(p: Pix, cx, w, top) -> bool:
    """Whether the jar's pipes may rise from its cap at row `top` to the ceiling, clear of every word."""
    return all(p.clear_of_words(x - 2, LB.CEILING - 1, x + 4, top) for x in (cx - w // 4, cx + w // 4 - 1))


def the_jar(p: Pix, cx, foot, w, night, motion, mood=True):
    """The brain in its jar on its console, its face on the screen, the light of its mood on the wall, and its
    shadow behind it."""
    z = LB.jar_size(w)
    box = LB.jar_box(cx, foot, w)
    S.shadow(p, box[0] + 2, box[1] + z["gauge"] + 2, box[2] - 1, foot, night)
    if mood and not p.lite:
        MD.light(p, cx, foot - z["h"] * 0.6, w * 1.15, z["h"] * 0.62, night, motion)
    parts = LB.jar(p, cx, foot, w, night, motion, face=MD.face(night, motion),
                   pipes=pipes_clear(p, cx, w, foot - z["h"] + z["gauge"]))
    MD.idea(p, parts, night, motion)
    return parts


def cable(p: Pix, x0, x1, g, night, motion, seed=0):
    """A heavy cable lying along the floor from one machine to the next, sagging where it lies loose, a signal
    running along it."""
    cells = []
    for x in range(x0, x1):
        t = (x - x0) / max(1, x1 - x0)
        y = g - 2 + round(math.sin(t * math.pi * 3 + seed) * 0.6)
        cells.append((x, y))
        p.px(x, y, STEEL[1] if not night else ROOM[0])
        p.px(x, y - 1, STEEL[3] if not night else STEEL[1])
    if motion and not p.lite and len(cells) > 12:
        key = ("pulse", night)
        if key not in p.syms:
            p.symbol(key, {(0, 0): NIXIE[6] if night else C["white"], (-1, 0): NIXIE[4], (1, 0): NIXIE[5]})
        path = [(x, y - 1) for x, y in cells[::3]]
        signal(p, key, path + [path[-1]] * 4, len(path) * 0.09)


def small_jar(p: Pix, x1, g, night) -> int | None:
    """Where the words leave no room for even the smallest jar: the jar drawn small, ending at column x1 on the
    floor at row `g`, the largest little jar that fits, or at the least the tiny one. Returns its left edge, or
    None."""
    sizes = [(LB.little_size(k), k) for k in (0.14, 0.12, 0.1)]
    sizes.append(((len(LB.TINY_JAR[0]), len(LB.TINY_JAR)), None))
    for (w, h), k in sizes:
        x0, y0 = x1 - w, g - h
        if y0 >= TOP and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, g + 1):
            if k:
                LB.little_jar(p, x0, y0, night, k)
            else:
                LB.tiny_jar(p, x0, y0, night)
            return x0
    return None


# --------------------------------------------------------------------------- the headers, wide
def h1(p: Pix, rule: int, night: bool, motion: bool) -> list:
    g = rule - 1
    W = p.w
    caps = {}
    right_of_mainframe = None
    # the mainframe at the left, as tall as the words let it stand
    for k in (1.1, 1.0, 0.92, 0.84, 0.76, 0.68, 0.6, 0.52, 0.44):
        mw, mh = LB.mainframe_size(k)
        x0 = 8
        if g - mh - 1 >= TOP - 4 and p.clear_of_words(x0 - 2, g - mh - 3, x0 + mw + 2, g + 1):
            S.shadow(p, x0, g - mh, x0 + mw, g, night)
            LB.mainframe(p, x0, g - 1, k, night, motion)
            caps.update({x: 1 for x in range(x0, x0 + mw)})
            right_of_mainframe = x0 + mw
            break
    # the jar at the right
    zone0 = reach(p, W - 6, TOP, g - 4, -1, W - 120)
    fit = fit_jar(p, zone0 + 1, W - 6, g - 1, most=52, least=LB.LEAST)
    covered = None
    if fit:
        cx, w = fit
        if night:
            S.room_glow(p, cx, g - 30, 70, 40)
        the_jar(p, cx, g - 1, w, night, motion)
        caps.update({x: 1 for x in range(cx - w // 2 - 6, cx + w // 2 + 7)})
        covered = cx - w // 2 - 6
    else:
        covered = small_jar(p, W - 8, g, night)
    spans = floor(p, 5, W - 5, g, 6, night, 3, motion, caps=caps)
    if right_of_mainframe and covered and covered - right_of_mainframe > 20:
        cable(p, right_of_mainframe, covered, g, night, motion)
    return spans


def h2(p: Pix, rule: int, night: bool, motion: bool) -> list:
    g = rule - 1
    W = p.w
    zone0 = max(reach(p, W - 6, TOP, g - 4, -1, W - 170), 200)
    fit = fit_jar(p, zone0 + 26, W - 6, g - 1, most=60, least=LB.LEAST)
    caps = {}
    if fit:
        cx, w = fit
        if night:
            S.room_glow(p, cx, g - 40, 95, 55)
        parts = the_jar(p, cx, g - 1, w, night, motion)
        caps.update({x: 1 for x in range(cx - w // 2 - 6, cx + w // 2 + 7)})
        # the Tesla coil beside it, as tall as the room to its left allows
        left = cx - w // 2 - 8
        for k in (1.1, 1.0, 0.9, 0.8, 0.7, 0.6):
            ch = round(48 * k)
            bx = left - round(11 * k)
            if bx - 12 > zone0 and p.clear_of_words(bx - 13, g - ch - 6, bx + 12, g + 1):
                S.shadow(p, bx - round(9 * k), g - ch, bx + round(9 * k), g, night)
                LB.coil(p, bx, g - 1, k, night, motion, toward=(parts["x0"] - 3, parts["cap"] + 3))
                caps.update({x: 1 for x in range(bx - 9, bx + 10)})
                break
    else:
        small_jar(p, W - 8, g, night)
    return floor(p, 5, W - 5, g, 6, night, 12, motion, caps=caps)


def h3(p: Pix, rule: int, night: bool, motion: bool) -> list:
    g = rule - 1
    W = p.w
    zone0 = reach(p, W - 6, TOP, g - 4, -1, W - 100)
    fit = fit_jar(p, zone0 + 1, W - 6, g - 1, most=38, least=LB.LEAST)
    caps = {}
    if fit:
        cx, w = fit
        if night:
            S.room_glow(p, cx, g - 24, 50, 30)
        parts = the_jar(p, cx, g - 1, w, night, motion)
        caps.update({x: 1 for x in range(cx - w // 2 - 6, cx + w // 2 + 7)})
        # the oscilloscope on the wall, its waves the brain's, wired to the jar
        x1 = cx - w // 2 - 10
        for h in (26, 23, 20, 17):
            y0 = TOP + 1
            x0 = x1
            while x0 > 100 and x1 - x0 < 116 and p.clear_of_words(x0 - 3, y0 - 2, x1 + 2, y0 + h + 2):
                x0 -= 1
            if x1 - x0 >= 46:
                S.shadow(p, x0 + 1, y0, x1, y0 + h, night)
                LB.scope(p, x0 + 1, y0, x1 - x0 - 1, h, night, motion)
                ly = y0 + h // 2
                for x in range(x1, cx - w // 2 - 4):
                    p.px(x, ly + (1 if (x - x1) % 7 > 4 else 0), STEEL[1] if not night else ROOM[0])
                break
    else:
        small_jar(p, W - 8, g, night)
    return floor(p, 5, W - 5, g, 6, night, 14, motion, caps=caps)


# --------------------------------------------------------------------------- the headers on a phone
PHONE_ROWS = {"H1": 62, "H2": 66, "H3": 60}


def h1_phone(p: Pix, y: int, night: bool):
    W = p.w
    g = y - 1
    caps = {}
    right_of_mainframe = None
    for k in (0.74, 0.66, 0.58, 0.5, 0.44):
        mw, mh = LB.mainframe_size(k)
        if p.clear_of_words(6, g - mh - 3, 10 + mw, g + 1):
            S.shadow(p, 8, g - mh, 8 + mw, g, night)
            LB.mainframe(p, 8, g - 1, k, night, False)
            caps.update({x: 1 for x in range(8, 8 + mw)})
            right_of_mainframe = 8 + mw
            break
    fit = fit_jar(p, W - 84, W - 6, g - 1, most=42, least=LB.LEAST)
    covered = None
    if fit:
        cx, w = fit
        if night:
            S.room_glow(p, cx, g - 24, 50, 30)
        the_jar(p, cx, g - 1, w, night, False)
        caps.update({x: 1 for x in range(cx - w // 2 - 6, cx + w // 2 + 7)})
        covered = cx - w // 2 - 6
    else:
        covered = small_jar(p, W - 8, g, night)
    floor(p, 5, W - 5, g, 5, night, 21, False, caps=caps)
    if right_of_mainframe and covered and covered - right_of_mainframe > 12:
        cable(p, right_of_mainframe, covered, g, night, False)


def under(design: str, p: Pix, y0: int, y1: int, night: bool):
    """The scene in the rows a phone's H2 or H3 leaves under its words: the jar with the coil beside it on H2's,
    the jar with its oscilloscope on H3's."""
    W = p.w
    g = y1 - 1
    caps = {}
    if design == "H2":
        fit = fit_jar(p, 52, W - 26, g - 1, most=48, least=LB.LEAST, centre=True)
        if fit:
            cx, w = fit
            if night:
                S.room_glow(p, cx, g - 30, 60, 36)
            parts = the_jar(p, cx, g - 1, w, night, False)
            caps.update({x: 1 for x in range(cx - w // 2 - 6, cx + w // 2 + 7)})
            bx = cx - w // 2 - 18
            if p.clear_of_words(bx - 13, g - 42, bx + 12, g + 1):
                S.shadow(p, bx - 8, g - 40, bx + 8, g, night)
                LB.coil(p, bx, g - 1, 0.86, night, False, toward=(parts["x0"] - 3, parts["cap"] + 3))
        else:
            small_jar(p, W - 8, g, night)
    else:
        fit = fit_jar(p, W - 70, W - 6, g - 1, most=34, least=LB.LEAST)
        if fit:
            cx, w = fit
            if night:
                S.room_glow(p, cx, g - 22, 46, 28)
            the_jar(p, cx, g - 1, w, night, False)
            caps.update({x: 1 for x in range(cx - w // 2 - 6, cx + w // 2 + 7)})
            x1 = cx - w // 2 - 8
            h = min(24, g - y0 - 10)
            if h >= 16 and x1 - 12 >= 40 and p.clear_of_words(10, y0 + 2, x1 + 2, y0 + 4 + h):
                LB.scope(p, 12, y0 + 3, x1 - 12, h, night, False)
        else:
            small_jar(p, W - 8, g, night)
    floor(p, 5, W - 5, g, 5, night, 31, False, caps=caps)
