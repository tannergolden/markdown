# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The scenes the theme's headers stand on, each drawn twice to one plan: heaven by day and its fallen twin by
night.

Every header stands on one ground the length of its foot (`band`): by day heaven's sea of cloud, heaped into
cumulus where a figure stands and lying low as a far-off deck of cloud under the words; by night a river of lava
the whole length, fire licking up off it, and hell's far bank of black rock heaped where the cumulus stood.

The H1 is heaven's gate: the pearly gates on their cloud at the left and the archangel on guard at the right, its
wings raised high, doves wheeling where the sky is clear; by night the gates of hell on their ledge, the lava
pouring out over their threshold, the demon standing where the angel stood and imps where the doves were. The H2
is the guardian drawn large, keeping its vigil: by day before the glory of heaven's light, by night before a wall
of fire. The H3 is a herald in flight, sounding a trumpet whose call crosses the sky as a fan of light, and by
night the herald of hell, a jet of fire roaring from its horn; with no room for one to fly, a cherub on its cloud,
or an imp on a burning rock. Each is drawn as large as the room the words leave it, and nothing comes within two
units of a word."""
from __future__ import annotations

import math
from functools import lru_cache

from ...holidays.pixel import Pix
from . import figures as F
from . import flyers as FL
from . import heaven as HV
from . import hell as HL
from . import small as SM
from .kit import clear, glow, reach
from .palette import RAMP, X

TOP = 15            # the highest row a scene reaches, clear of what hangs along the top


@lru_cache(maxsize=None)
def extent(night: bool, pose: str, spread: float, wings: str = "raised") -> tuple:
    """The box a guardian takes in its own units, (x0, y0, x1, y1) about its feet: drawn once at full size and
    measured."""
    p = Pix(200, 200)
    draw = F.demon if night else F.archangel
    draw(p, 100, 150, k=1.0, motion=False, pose=pose, spread=spread, wings=wings)
    cells = [q for name, layer in p.layers.items() if name != "haze" for q in layer] + list(getattr(p, "winged", ()))
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    return (min(xs) - 100, min(ys) - 150, max(xs) + 1 - 100, max(ys) + 1 - 150)


def fit_guardian(p: Pix, x0, x1, foot, night, pose, spread, most=1.6, least=0.4, centre=False, wings="raised"):
    """The largest guardian, (cx, k), that stands on row `foot` between columns x0 and x1, below row `TOP` and two
    units clear of every word; None when even the smallest has no room. The demon is measured with the angel and
    both take the smaller size, so the twins stand the same size by day and by night."""
    ea, ed = extent(False, pose, spread, wings), extent(True, pose, spread, wings)
    e = (min(ea[0], ed[0]), min(ea[1], ed[1]), max(ea[2], ed[2]), max(ea[3], ed[3]))
    k = most
    while k >= least:
        w = (e[2] - e[0]) * k
        if w <= x1 - x0 and foot + e[1] * k >= TOP:
            # as far right as it can stand, or in the middle of its room
            cx = (x0 + x1) / 2 - (e[0] + e[2]) / 2 * k if centre else x1 - e[2] * k
            box = (int(cx + e[0] * k) - 2, int(foot + e[1] * k) - 2, int(cx + e[2] * k) + 3, foot)
            if p.clear_of_words(*box):
                return cx, k
        k = round(k - 0.04, 2)
    return None


def guardian(p: Pix, cx, foot, k, night, pose, spread, motion, wings="raised", aura=True, rim=False):
    """The guardian, the angel by day and the demon by night, with the light that stands behind it: by day a glow
    of heaven's gold that lifts its white wings off the sky, by night the red of the fires."""
    if aura:
        e = extent(night, pose, spread, wings)
        cy = foot + (e[1] + e[3]) / 2 * k
        rx, ry = (e[2] - e[0]) * k * 0.5, (e[3] - e[1]) * k * 0.5
        glow(p, cx, cy, rx * 0.9, ry * 0.85, X["heat"] if night else X["glory"],
             (0.07, 0.13, 0.2) if night else (0.12, 0.2, 0.3), shape=True)
    if night:
        F.demon(p, cx, foot, k=k, motion=motion, pose=pose, spread=spread, wings=wings, rim=rim)
    else:
        F.archangel(p, cx, foot, k=k, motion=motion, pose=pose, spread=spread, wings=wings, rim=rim)


def room_along(p: Pix, x0, x1, g, most) -> dict:
    """How many rows over row `g` each column from x0 to x1 may take, two units clear of every word above it."""
    from .kit import free_rows
    return {x: free_rows(p, x, x + 1, g, most) for x in range(x0, x1)}


def band(p: Pix, x0, x1, g, most, night, seed, motion, ends=(), caps=None, low=7) -> list:
    """The ground the length of a header's foot. Each of `ends`, (x0, x1), is a heap where something stands, as
    high as the words leave it room: by day a bank of cumulus heaped and shaded in full, by night crags of black
    rock. Between them it lies low, no more than `low` rows: by day heaven's deck of cloud seen far off, by night
    hell's far bank of rock over a river of lava, which runs the whole length of the foot. `caps`, {column: rows},
    holds it lower where something stands in it. Returns the spans it covers."""
    room = room_along(p, x0, x1, g, most)
    for x, n in (caps or {}).items():
        if x in room:
            room[x] = min(room[x], n)
    heaped = {x for a, b in ends for x in range(max(x0, a), min(x1, b))}
    flat = {x: min(room[x], low) for x in range(x0, x1) if x not in heaped}
    foot = g + 1
    if night:
        depth = 3 if p.w > 300 else 2
        HL.horizon(p, x0, x1, foot - depth, max(room.values()) + 2)
        heights = {x: max(0, (room[x] if x in heaped else min(room[x], low + 2)) - depth) for x in range(x0, x1)}
        HL.far_bank(p, x0, x1, foot - depth, heights, seed=seed, lite=p.lite)
        HL.lava_river(p, x0, x1, foot, room, depth=depth, seed=seed + 1, lite=p.lite, motion=motion)
        if not p.lite:
            # fire licking up off the river where the words leave it the room
            import random
            rnd = random.Random(seed + 2)
            x, i = x0 + rnd.randint(8, 16), 0
            while x < x1 - 6:
                for s in (1.0, 0.8):
                    tall = int(11 * s) + 2
                    if x not in heaped and all(room.get(xx, 0) >= tall for xx in range(x - 5, x + 6)):
                        HL.flame(p, x, foot - depth + 1, s=s, phase=i, motion=motion, halo=False)
                        i += 1
                        x += rnd.randint(14, 30)
                        break
                x += rnd.randint(10, 22)
    else:
        HV.deck(p, x0, x1, foot, flat, seed=seed)
        for i, (a, b) in enumerate(ends):
            top = foot - max([room[x] for x in range(max(x0, a), min(x1, b))] or [0])
            HV.cloud(p, HV.puffs_for(a, b, foot, top, seed + 7 * i, 1.9, crown=0.5), foot,
                     keep=lambda x, y: x in room and y >= foot - room[x], x0=a, x1=b)
    spans, cur = [], None
    for x in range(x0, x1):
        if room[x] >= 2:
            cur = [x, x + 1] if cur is None else [cur[0], x + 1]
        elif cur:
            spans.append(tuple(cur))
            cur = None
    if cur:
        spans.append(tuple(cur))
    return spans


def caps_for(spans, rows) -> dict:
    """Caps for a band: no more than `rows` rows over the foot in each of `spans`, (x0, x1)."""
    return {x: rows for a, b in spans for x in range(int(a), int(b))}


def flock(p: Pix, cx, cy, rx, ry, n, night, motion, seed):
    """Doves by day and imps by night, wheeling where the sky round them is clear of words; a drawing made lighter
    to fit its budget leaves them out."""
    if p.lite:
        return True
    box = SM.flock_box(cx, cy, rx, ry)
    if box[1] >= TOP - 3 and box[0] > 4 and box[2] < p.w - 4 and p.clear_of_words(*box):
        SM.flock(p, cx, cy, rx, ry, n, night, motion=motion, seed=seed)
        return True
    return False


def glory(p: Pix, cx, cy, r, seed=0):
    """Heaven's light behind a guardian keeping its vigil: rays of pale gold fanning out from about its head."""
    import random
    rnd = random.Random(seed)
    parts = []
    n = 16
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-0.2, 0.2)) / n
        da = math.radians(rnd.uniform(3.5, 6.5))
        rr = r * rnd.uniform(0.75, 1.0)
        pts = [(cx, cy)] + [(cx + rr * math.cos(b), cy + rr * math.sin(b)) for b in (a - da, a + da)]
        parts.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
    p.under.append(f'<g fill="{X["glory"]}" fill-opacity=".38">{"".join(parts)}</g>')
    glow(p, cx, cy, r * 0.55, r * 0.55, RAMP["gold"][6], (0.08, 0.16, 0.26), shape=True)


def wall_of_fire(p: Pix, x0, x1, g, height, motion, seed=0):
    """A wall of fire behind a demon keeping its watch: flames leaping along the crags, each flickering on its
    own phase, and one glow for all of them thrown up the dark."""
    import random
    rnd = random.Random(seed)
    x = x0 + rnd.randint(0, 4)
    i = 0
    sizes = (1.0 * height / 16, 1.4 * height / 16)
    while x < x1 - 3:
        HL.flame(p, x, g - (4 if i % 2 else 7), s=sizes[i % 2], phase=i, motion=motion, halo=False, back=True)
        x += rnd.randint(6, 9)
        i += 1
    glow(p, (x0 + x1) / 2, g - height * 0.6, (x1 - x0) / 2 + 6, height * 0.9, X["heat"], (0.08, 0.15, 0.24),
         L=p.flicker(1, back=True) if motion else "haze", shape=True)


# --------------------------------------------------------------------------- the headers, wide
def h1(p: Pix, rule: int, night: bool, motion: bool) -> list:
    g = rule - 1
    W = p.w
    caps, ends = {}, []
    # the gates at the left, as large as the words let them stand
    for gw, gh in ((46, 66), (44, 62), (40, 56), (36, 50), (32, 44)):
        gx = 8
        if g - 2 - gh - 4 >= TOP - 6 and p.clear_of_words(gx - 3, g - gh - 8, gx + gw + 4, g + 1):
            if night:
                HL.hell_gates(p, gx, g - 2, w=gw, h=gh, motion=motion)
            else:
                HV.pearly_gates(p, gx, g - 2, w=gw, h=gh, motion=motion)
            if night:
                caps.update(caps_for([(gx - 3, gx + gw)], 5))           # the ledge it stands on
                caps.update(caps_for([(gx + 7, gx + gw - 7)], 3))      # the lava pouring out over its threshold
                ends.append((gx + gw - 1, gx + gw + 16))
            else:
                ends.append((5, gx + gw + 16))
            break
    # the guardian at the right, on guard, its wings raised high
    zone0 = reach(p, W - 6, TOP, g - 4, -1, W - 120)
    fit = fit_guardian(p, zone0 + 1, W - 5, g - 4, night, "raised", 0.0, most=1.2, wings="high")
    if fit:
        cx, k = fit
        guardian(p, cx, g - 4, k, night, "raised", 0.0, motion, wings="high", rim=True)
        caps.update(caps_for([(cx - 8 * k, cx + 8 * k)], 5 if night else 10))
        ends.append((int(cx - 20 * k), W - 5))
    # the doves, or the imps, over the gates where the sky is clear
    flock(p, 92, 34, 22, 9, 2, night, motion, seed=5) or flock(p, 60, 26, 10, 5, 1, night, motion, seed=6)
    covered = band(p, 5, W - 5, g, 14, night, 3, motion, ends=ends, caps=caps)
    # feathers drifting down past heaven's gate, or sparks rising off the fires before hell's
    SM.drift(p, (14, TOP + 4, 50, g - 14), 2 if not night else 3, night, motion, seed=2)
    if night:
        HL.firelight(p)
    return covered


def h2(p: Pix, rule: int, night: bool, motion: bool) -> list:
    g = rule - 1
    W = p.w
    zone0 = reach(p, W - 6, TOP, g - 4, -1, W - 160)
    zone0 = max(zone0, 200)
    fit = fit_guardian(p, zone0 + 1, W - 5, g - 6, night, "planted", 0.35, most=1.6)
    covered = []
    if fit:
        cx, k = fit
        e = extent(night, "planted", 0.35)
        head = (cx, g - 6 - 52 * k)
        if p.lite:
            pass
        elif night:
            wall_of_fire(p, int(cx - 30 * k), int(cx + 30 * k), g, 18 * k, motion, seed=4)
        else:
            glory(p, head[0], head[1], 46 * k, seed=3)
        guardian(p, cx, g - 6, k, night, "planted", 0.35, motion, rim=True)
        caps = caps_for([(cx - 9 * k, cx + 9 * k)], 6 if night else 9)
        ends = [(int(cx + e[0] * k) - 8, W - 5)]
    else:
        caps, ends = {}, [(W - 60, W - 5)]
    covered = band(p, 5, W - 5, g, 16, night, 12, motion, ends=ends, caps=caps)
    flock(p, 248, 36, 24, 8, 2, night, motion, seed=9) or flock(p, 230, 22, 14, 4, 1, night, motion, seed=10)
    if fit:
        # feathers drifting down beside the guardian, or sparks rising off the wall of fire round the demon, in the
        # first stretch of sky beside it that the words leave clear
        left = int(cx + e[0] * k)
        for box in ((left - 18, TOP + 6, left - 4, g - 18), (left - 16, TOP + 4, left - 2, 64),
                    (196, TOP + 4, 228, 60)):
            if p.clear_of_words(box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2):
                SM.drift(p, box, 2 if not night else 3, night, motion, seed=6)
                break
    if night:
        HL.firelight(p)
    return covered


@lru_cache(maxsize=None)
def flyer_extent(night: bool) -> tuple:
    """The box a herald in flight takes in its own units about its head: drawn once at full size and measured."""
    p = Pix(240, 160)
    (FL.fiend if night else FL.herald)(p, 100, 80, k=1.0, motion=False)
    cells = [q for name, layer in p.layers.items() if name != "haze" for q in layer]
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    return (min(xs) - 100, min(ys) - 80, max(xs) + 1 - 100, max(ys) + 1 - 80)


def fit_flyer(p: Pix, x1, y0, y1, most=1.2, least=0.55, left=150):
    """The largest herald in flight, (x, y, k) of its head, whose box ends at column x1 and lies between rows y0 and
    y1, two units clear of every word; the twins are measured together so both fly the same size."""
    ea, ed = flyer_extent(False), flyer_extent(True)
    e = (min(ea[0], ed[0]), min(ea[1], ed[1]), max(ea[2], ed[2]), max(ea[3], ed[3]))
    k = most
    while k >= least:
        h = (e[3] - e[1]) * k
        if h <= y1 - y0:
            # as far right as there is a sky clear of words for it, along the strip
            for shift in range(0, 300, 4):
                x = x1 - e[2] * k - shift
                if x + e[0] * k < left:
                    break
                for y in range(int(y0 - e[1] * k), int(y1 - e[3] * k) + 1):
                    box = (int(x + e[0] * k) - 2, int(y + e[1] * k) - 2, int(x + e[2] * k) + 3,
                           int(y + e[3] * k) + 3)
                    if p.clear_of_words(*box):
                        return x, y, k
        k = round(k - 0.05, 2)
    return None


def h3(p: Pix, rule: int, night: bool, motion: bool) -> list:
    g = rule - 1
    W = p.w
    covered = band(p, 5, W - 5, g, 12, night, 14, motion, ends=[(max(W - 66, reach(p, W - 6, g - 12, g, -1, W - 120)), W - 5)])
    # the herald in flight over the right of the strip, as large as the sky the words leave it
    fly = fit_flyer(p, W - 8, TOP, g - 12)
    if fly:
        x, y, k = fly
        (FL.fiend if night else FL.herald)(p, x, y, k=k, motion=motion)
        if not p.lite:
            FL.call(p, x, y, k, night, motion, box=(8, TOP - 6, W - 8, g - 6))
        for cx, cy in ((250, 30), (220, 26), (196, 22)):
            if flock(p, cx, cy, 18, 6, 2, night, motion, seed=12):
                break
        if night:
            HL.flame(p, W - 14, g - 4, s=0.9, phase=1, motion=motion)
            HL.firelight(p)
        return covered
    for k in (1.3, 1.15, 1.0, 0.85, 0.7):
        cx = W - 26
        box = (int(cx - 10 * k) - 2, int(g - 8 - 21 * k) - 2, int(cx + 10 * k) + 3, g)
        if box[1] >= TOP - 4 and p.clear_of_words(*box):
            if night:
                HL.flame(p, W - 12, g - 4, s=0.9, phase=1, motion=motion)
                SM.imp_on_rock(p, cx, g - 7, k=k, motion=motion)
            else:
                SM.cherub(p, cx, g - 7, k=k, motion=motion)
            break
    flock(p, 372, 30, 12, 5, 1, night, motion, seed=12)
    if night:
        HL.firelight(p)
    return covered


# --------------------------------------------------------------------------- the headers on a phone
PHONE_ROWS = {"H1": 48, "H2": 56, "H3": 42}


def narrow(design: str, p: Pix, y: int, night: bool):
    """The small mark beside a phone's words: a dove or an imp beside H2's SECTION A-A; H3's beside its title."""
    if design == "H2":
        x = p.w - 22
        if p.clear_of_words(x - 2, y - 4, x + 13, y + 10):
            p.use((SM.imp_symbol if night else SM.dove_symbol)(p, 0), x, y - 2)


def h1_phone(p: Pix, y: int, night: bool):
    """A phone's H1 stands on its rule at `y`, in the rows under the words: the gates at the left and the guardian
    at the right, its wings raised high, on one ground of cloud or of crags."""
    W = p.w
    g = y - 1
    caps, ends = {}, []
    for gw, gh in ((32, 44), (30, 40), (26, 34), (22, 28)):
        if p.clear_of_words(4, g - gh - 6, 8 + gw + 3, g + 1):
            (HL.hell_gates if night else HV.pearly_gates)(p, 8, g - 2, w=gw, h=gh, motion=False)
            if night:
                caps.update(caps_for([(8 + 6, 8 + gw - 6)], 2))
            ends.append((5, 8 + gw + 8))
            break
    fit = fit_guardian(p, W - 74, W - 5, g - 4, night, "raised", 0.0, most=0.9, least=0.3, wings="high")
    if fit:
        guardian(p, fit[0], g - 4, fit[1], night, "raised", 0.0, False, wings="high")
        caps.update(caps_for([(fit[0] - 8 * fit[1], fit[0] + 8 * fit[1])], 3 if night else 5))
        ends.append((int(fit[0] - 18 * fit[1]), W - 5))
    band(p, 5, W - 5, g, 11, night, 21, False, ends=ends, caps=caps, low=5)
    if night:
        HL.firelight(p)


def under(design: str, p: Pix, y0: int, y1: int, night: bool):
    """The scene in the rows a phone's H2 or H3 leaves under its words: the guardian keeping its vigil on H2's, the
    cherub or the imp on H3's."""
    W = p.w
    g = y1 - 1
    if design == "H2":
        fit = fit_guardian(p, 8, W - 8, g - 4, night, "planted", 0.35, most=0.95, least=0.3, centre=True)
        if fit:
            cx, k = fit
            if night:
                wall_of_fire(p, int(cx - 26 * k), int(cx + 26 * k), g, 18 * k, False, seed=4)
            else:
                glory(p, cx, g - 4 - 52 * k, 40 * k, seed=3)
            guardian(p, cx, g - 4, k, night, "planted", 0.35, False, rim=True)
            band(p, 5, W - 5, g, 9, night, 31, False, ends=((5, 44), (W - 44, W - 5)),
                 caps=caps_for([(cx - 9 * k, cx + 9 * k)], 3 if night else 6), low=5)
        else:
            band(p, 5, W - 5, g, 9, night, 31, False, ends=((5, 44), (W - 44, W - 5)), low=5)
    else:
        band(p, 5, W - 5, g, 9, night, 33, False, ends=((W - 60, W - 5),), low=5)
        fly = fit_flyer(p, W - 10, y0 + 2, g - 6, most=1.1, least=0.5, left=8)
        if fly:
            x, y, k = fly
            (FL.fiend if night else FL.herald)(p, x, y, k=k, motion=False)
            if not p.lite:
                FL.call(p, x, y, k, night, False, box=(8, y0, W - 8, g - 4), most=110)
        if night:
            HL.flame(p, W - 16, g - 4, s=0.8, phase=1, motion=False)
    if night:
        HL.firelight(p)
