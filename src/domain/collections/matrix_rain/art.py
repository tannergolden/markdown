# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rain set's scenery and sprites, drawn on the shared pixel canvas.

By night every sheet is the glass of a terminal in a dark room, scanned in lines and held in the moulded case of the
monitor, and the code falls down it in streams of phosphor; by day the same code comes off a line printer onto
greenbar paper, its tractor strips punched down either side and its bars of pale green across it, printed in a
ribbon's ink. Titles glow on the glass, scanned, their upper and left edges white-hot and their light blooming
round them, and by day they are struck in the dots of a printer's head. Headers open on the room the code is
watched from, the terminal on its desk with its keyboard and a hacker asleep over it, and on the city the code is
the world of, its towers traced in phosphor and windowed in glyphs; on the corridor of code, the world drawn in its
lines, a man in a long coat standing in it before the door at its end; and on the city's great tower, stepping back
to its spire.

The footers stand on the keyboard, the terminal after their last cell; the links' keys and icons, the badges' stream
and every element's touch are cut from the same glass, case, paper, ribbon and phosphor. Everything is shaded from
the one light in the upper left on the set's own ramps, and every light is the hand's phosphor. A drawing made lighter
still keeps every piece of its scene and all its motion: it lets the second stream of each column behind a title go,
and a title loses its glow."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, Paint, Pix, fold, num
from .. import rain
from .palette import BAND, C, NIGHT_SKY, RAMP

PAPER, RIBBON, GLASS, CASE = RAMP["paper"], RAMP["ribbon"], RAMP["glass"], RAMP["case"]
DESK, CLOTH, HAIR, FLAME = RAMP["desk"], RAMP["cloth"], RAMP["hair"], RAMP["flame"]
BEIGE = RAMP["beige"]
EDGE = 4          # the frame's width: the case round the glass, or the tractor strip down the paper
OFFSET = 2        # the row the greenbar's first green band starts on


# --------------------------------------------------------------------------- the paper
def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: by night the terminal's glass, darkest at its top and foot where the tube's
    light falls off, scanned in a dark line every other row; by day a line printer's greenbar, white paper with a
    band of pale green every other line of print."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
        p.defs.append(f'<pattern id="{uid}s" width="8" height="2" patternUnits="userSpaceOnUse">'
                      f'<path stroke="{GLASS[0]}" stroke-opacity=".6" d="M0 1.5h8"/></pattern>')
        p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}s)"/>')
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
        p.defs.append(f'<pattern id="{uid}g" y="{OFFSET}" width="8" height="{2 * BAND}" patternUnits="userSpaceOnUse">'
                      f'<rect width="8" height="{BAND}" fill="{C["bar"]}"/></pattern>')
        p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}g)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the band of glass by night, the green bar or the white paper by day."""
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        return next(NIGHT_SKY[i] for i in range(n) if y < edges[i + 1] or i == n - 1)
    return C["bar"] if ((y - OFFSET) // BAND) % 2 == 0 else C["paper"]


# --------------------------------------------------------------------------- the frame
def frame(p: Pix, night: bool, header: bool = False, foot: bool = True):
    """The border: by night the moulded case of the monitor round its glass, lit along its top and left and in
    shade along its foot and right, the glass's corners rounded into it and its power light burning at the foot of
    a header; by day the tractor strips down the paper's sides, punched for the printer's pins, with the
    perforations they tear off along. Without its `foot`, as a footer has it, the border leaves its foot between
    its sides to the keyboard laid there (see `footing`)."""
    if night:
        _case(p, header)
    else:
        _tractor(p)
    if not foot:
        base = p.layers["base"]
        for y in range(p.h - (EDGE if night else 1), p.h):
            for x in range(EDGE, p.w - EDGE):
                base.pop((x, y), None)


def _case(p: Pix, header: bool):
    w, h = p.w, p.h
    p.box(0, 0, w, h, CASE[0])
    p.hline(1, w - 1, 1, CASE[5])
    p.hline(1, w - 1, 2, CASE[4])
    p.vline(1, 1, h - 1, CASE[5])
    p.vline(2, 2, h - 2, CASE[4])
    p.hline(2, w - 1, h - 2, CASE[1])
    p.hline(3, w - 2, h - 3, CASE[2])
    p.vline(w - 2, 2, h - 1, CASE[1])
    p.vline(w - 3, 3, h - 2, CASE[2])
    p.hline(3, w - 3, 3, GLASS[0])
    p.vline(3, 3, h - 3, GLASS[0])
    p.hline(4, w - 3, h - 4, CASE[3])
    p.vline(w - 4, 4, h - 3, CASE[3])
    # The glass's corners, rounded into the case.
    r = 5
    for dy in range(r):
        for dx in range(r):
            if (r - dx - 0.5) ** 2 + (r - dy - 0.5) ** 2 > r * r:
                p.px(EDGE + dx, EDGE + dy, CASE[4])
                p.px(w - EDGE - 1 - dx, EDGE + dy, CASE[3])
                p.px(EDGE + dx, h - EDGE - 1 - dy, CASE[3])
                p.px(w - EDGE - 1 - dx, h - EDGE - 1 - dy, CASE[2])
    if header:
        p.hline(w - 16, w - 13, h - 3, FLAME[4])
        p.hline(w - 16, w - 13, h - 2, FLAME[2])


def _tractor(p: Pix):
    w, h = p.w, p.h
    p.box(0, 0, w, h, PAPER[3])
    for x in (EDGE, w - EDGE - 1):
        for y in range(2, h - 2, 2):
            p.px(x, y, PAPER[3])
    for cx in (2, w - 3):
        for cy in range(4, h - 3, 6):
            p.px(cx, cy - 1, PAPER[0])
            p.px(cx - 1, cy, PAPER[0])
            p.px(cx, cy, PAPER[2])
            p.px(cx + 1, cy, PAPER[3])
            p.px(cx, cy + 1, PAPER[3])


# --------------------------------------------------------------------------- the titles
def _scanned(r, c, scale, night):
    return FLAME[4] if r % 2 == 0 else FLAME[3]


SCANNED = Paint("ph", _scanned, period=1)


def phosphor_title(p: Pix, x, y, s, scale) -> int:
    """A title lit on the glass: its letters in phosphor scanned in lines, their upper and left edges burning white
    and their foot a step dimmer, the light blooming round them into the glass. Returns its width."""
    kw = dict(paint=SCANNED, night=True)
    if scale >= 3:
        kw["bevel"] = (FLAME[6], FLAME[2])
    if scale >= 2:
        kw["glow"] = (FLAME[3], (0.05, 0.1, 0.17) if scale >= 3 else (0.14,))
    return p.text(x, y, s, FLAME[4], "57", scale, **kw)


# The dot a printer's pin strikes for each unit of a letter, by the size it is set at: (dx, dy, colour), its corners
# softer where the pin's edge strikes lighter.
DOTS = {
    4: [(dx, dy, RIBBON[2] if (dx in (0, 3) and dy in (0, 3)) else RIBBON[0]) for dy in range(4) for dx in range(4)],
    3: [(dx, dy, RIBBON[2] if (dx != 1 and dy != 1) else RIBBON[0]) for dy in range(3) for dx in range(3)],
    2: [(0, 0, RIBBON[0]), (1, 0, RIBBON[1]), (0, 1, RIBBON[1]), (1, 1, RIBBON[1])],
    1: [(0, 0, RIBBON[0])],
}


def printed_title(p: Pix, x, y, s, scale) -> int:
    """A title struck by a printer's head: every unit of its letters a dot of the ribbon's ink, softer at its
    corners. Each letter is drawn once a file and placed. Returns its width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    dots = DOTS[min(4, scale)]
    cx = x
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        key = ("dots", ch, scale)
        if key not in p.syms:
            cells = {}
            for r, cols in enumerate(g[1]):
                for col in cols:
                    for dx, dy, c in dots:
                        cells[(col * scale + dx, r * scale + dy)] = c
            p.symbol(key, cells)
        p.use(key, cx, y)
        cx += (g[0] + 1) * scale
    w = cx - x - scale
    rows = max((len(glyphs[ch][1]) for ch in s if ch != " "), default=0)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    return w


# --------------------------------------------------------------------------- the code
def falling(p: Pix, night: bool, top: int, ground: int, seed: int = 1, keep=(), titles=(), sides=0.9, middle=0.55,
            veil=0.8):
    """The code falling down the sheet, the sky the design's words stand in: in every column clear of the words a
    stream from `top` to wherever the first word under it begins, or to the `ground`, two streams a column down the
    sides; and behind the title's letters (the boxes in `titles`, which the code passes behind as it passes behind no
    other word) dim streams with no white head, ending above the words under the title. None falls in the columns of
    the boxes in `keep` (the month's mark). `sides`, `middle` and `veil` are the shares of those columns that fall.
    Columns that end at the same row, in the same tones, fall together, in one box. A drawing made lighter lets the
    second stream of each column behind the title go, where they are dimmest; every column keeps its first, falling
    at its own pace."""
    rnd = random.Random(seed)
    ramp = FLAME if night else RIBBON
    words = [b for b in p.words if not any(b[0] <= t[0] + 1 and b[2] >= t[2] - 1 and b[1] <= t[1] + 1
                                           and b[3] >= t[3] - 1 for t in titles)]
    boxes: dict = {}
    for x in range(EDGE + 2, p.w - EDGE - rain.W - 1, rain.COLUMN):
        if any(a - 2 <= x + rain.W and x - 2 <= c for a, b, c, d in keep):
            continue
        end = ground
        for b in words:
            if b[0] - 3 < x + rain.W and x - 3 < b[2] and b[1] > top:
                end = min(end, b[1] - 3)
        if end - top < 2 * rain.PITCH:
            continue
        behind = any(t[0] - 3 < x + rain.W and x - 3 < t[2] and t[1] < end for t in titles)
        boxes.setdefault((end, behind), []).append(x)
    for (end, behind), xs in sorted(boxes.items()):
        side = end >= ground - 8 and not behind
        share = sides if side else veil if behind else middle
        r = rain.Rain(p, (min(xs), top, max(xs) + rain.W, end), ramp, night, seed=rnd.randrange(1000),
                      lengths=(4, 13) if side else (3, 9), dim=behind)
        for x in xs:
            if rnd.random() >= share:
                continue
            span = (end - top) // rain.PITCH + 13
            first = rnd.randrange(span)
            pace = rnd.choice((0.08, 0.11, 0.15))
            r.stream(x, top + first * rain.PITCH, pace=pace)
            if side or (behind and not p.lite):
                r.stream(x, top + ((first + span // 2) % span) * rain.PITCH, pace=pace)
        r.fall(z=-9 if behind else -8)


# --------------------------------------------------------------------------- the terminal
# A 90s monitor seen from the front, 25 by 23: its moulded case (c, lit L, shaded s and S), the bezel's dark lip
# round the glass (d), the glass (g), its power button (o), the vents along its side (v) and its swivel base (b).
MONITOR = [
    "..LLLLLLLLLLLLLLLLLLLLLc.",
    ".LcccccccccccccccccccccsS",
    "Lccdddddddddddddddddddcss",
    "Lcdgggggggggggggggggggdcs",
    "Lcdgggggggggggggggggggdcv",
    "Lcdgggggggggggggggggggdcs",
    "Lcdgggggggggggggggggggdcv",
    "Lcdgggggggggggggggggggdcs",
    "Lcdgggggggggggggggggggdcv",
    "Lcdgggggggggggggggggggdcs",
    "Lcdgggggggggggggggggggdcv",
    "Lcdgggggggggggggggggggdcs",
    "Lcdgggggggggggggggggggdcv",
    "Lcdgggggggggggggggggggdcs",
    "LccLLLLLLLLLLLLLLLLLLLccs",
    "Lcccccccccccccccccccocccs",
    ".sssssssssssssssssssssssS",
    "........bbbbbbbbb........",
    ".......LbbbbbbbbbS.......",
    ".....LLbbbbbbbbbbbSS.....",
    "....SSSSSSSSSSSSSSSSS....",
]
GLASS_AT, GLASS_SIZE = (3, 3), (19, 11)   # where the glass is in the monitor, and its width and height
# The hacker asleep at the keyboard, 27 by 25, facing left: his head down on his folded arms on the desk, his back
# rounded over them, sitting on in his jeans with his trainers under the desk. His hair (h, lit H), an ear, his neck
# and his arms in skin (f, shaded F, lit a), a black shirt (t, lit T, its edge k), jeans (j, lit J) and trainers (n).
SLEEPER = [
    ".....hhhhh.................",
    "...hhHHHHHhh...............",
    "..hHHHHHHHHHh..............",
    ".hHHHHHHHHHHHh.............",
    ".hhHHHHHHHHHHhh..ttt.......",
    "aahhhhHHHHHhhfFtTTTtt......",
    "aaaahhhhhhhhffttTTTTTtt....",
    "aaaaaaaaaaaaFtttTTTTTTtk...",
    ".............kttTTTTTttk...",
    "..............kttTTTTTttk..",
    "...............kttTTTTttk..",
    "................kttTTTTtk..",
    "................kttTTTttk..",
    ".................kttTTttk..",
    ".................kttTTttk..",
    ".................jjjjjJJjk.",
    "...........jjjjjjjjjjjJJj..",
    "......jjjjjjjjjjjjjjjJJj...",
    "......jjJJJJJJJJJJJJjj.....",
    "......jj...................",
    "......jj...................",
    "......jj...................",
    "......jJ...................",
    ".....nnnn..................",
    "....nnnnnn.................",
]
# His office chair, 9 by 18, behind him: its back (r, lit R), its seat, its post (p) and its wheels (w).
CHAIR = [
    ".......rR",
    ".......rR",
    ".......rR",
    ".......rR",
    ".......rR",
    ".......rR",
    ".......rR",
    ".......rR",
    ".......rR",
    "rrrrrrrrR",
    "RRRRRRRRR",
    "....pp...",
    "....pp...",
    "....pp...",
    "....pp...",
    "...pppp..",
    ".pppppppp",
    ".w..w..w.",
]
# The tower under the desk, 9 by 15: its beige case (c, lit L, shaded s), its drive bays (d) and its power light (o).
TOWER = [
    "LLLLLLLLc",
    "Lcccccccs",
    "Lddddddcs",
    "Lcccccccs",
    "Lddddddcs",
    "Lcccccccs",
    "Lcccccccs",
    "Lccccoccs",
    "Lcccccccs",
    "Lcccccccs",
    "Lcvcvcvcs",
    "Lcccccccs",
    "Lcvcvcvcs",
    "Lcccccccs",
    "sssssssss",
]


def _tones(night: bool) -> dict:
    """The terminal's colours: its beige case, the sleeper's clothes and hair and the chair, by day in the room's
    light and by night in the dark, where only the glass lights them. His skin keeps its tone by night, as the hand's
    canon has it, and takes the glass's light (see `screen`)."""
    k = -2 if night else 0
    B, S, D = BEIGE, RAMP["skin1"], RAMP["denim"]

    def b(i):
        return B[max(0, i + k)]
    return {
        "L": b(6), "c": b(4), "s": b(2), "S": b(1), "d": B[1] if night else B[2], "v": b(2), "b": b(3),
        "o": CASE[3] if not night else CASE[2], "g": GLASS[1],
        "h": HAIR[1] if night else HAIR[2], "H": HAIR[3] if night else HAIR[5],
        "f": S[3], "F": S[2], "a": S[4],
        "t": CLOTH[1] if night else CLOTH[3], "T": CLOTH[3] if night else CLOTH[5], "k": CLOTH[0],
        "j": D[1] if night else D[3], "J": D[2] if night else D[4], "n": PAPER[1] if night else PAPER[6],
        "r": CASE[1] if night else CASE[3], "R": CASE[2] if night else CASE[5],
        "p": CASE[1] if night else CASE[2], "w": CASE[0] if night else CASE[1],
    }


def desk(p: Pix, x0, x1, top, g, night):
    """The desk the terminal stands on, its top at row `top`: a slab lit along its upper face with its edge in shade
    under it, and two legs down to the floor at row g."""
    D = DESK if night else RAMP["wood"]
    p.hline(x0, x1, top, D[6] if not night else D[4])
    p.hline(x0, x1, top + 1, D[4] if not night else D[3])
    p.hline(x0, x1, top + 2, D[2] if not night else D[1])
    p.hline(x0 + 1, x1 - 1, top + 3, D[1] if not night else D[0])
    for lx in (x0 + 1, x1 - 4):
        p.rect(lx, top + 4, 3, g - top - 3, D[2] if not night else D[1])
        p.vline(lx, top + 4, g + 1, D[4] if not night else D[2])
        p.vline(lx + 2, top + 4, g + 1, D[0])


def screen(p: Pix, x, y, w, h, night, motion, seed=2):
    """What the terminal's glass shows: the code falling down it in streams a unit wide, their heads twinkling in a
    moving header, and a prompt with its cursor; by night the glass's light thrown round it onto the desk and the
    sleeper."""
    rnd = random.Random(seed)
    for cx in range(x + 1, x + w - 1, 2):
        if rnd.random() < 0.2:
            continue
        head = y + rnd.randrange(h + 3)
        for i in range(rnd.randint(3, h)):
            yy = head - i
            if y <= yy < y + h:
                c = (FLAME[6] if i == 0 else FLAME[4] if i < 2 else FLAME[3] if i < 4 else FLAME[2] if i < 7
                     else FLAME[1])
                p.px(cx, yy, c, p.twinkle(cx) if (motion and i == 0) else "base")
    p.hline(x + 1, x + 4, y + h - 2, FLAME[5])
    p.px(x + 6, y + h - 2, FLAME[6], p.blink(0) if motion else "base")
    if night:
        p.halo(x + w / 2, y + h / 2 + 2, w * 1.25, h * 1.6, FLAME[3], (0.04, 0.08, 0.13))
        lit = set(HAIR + RAMP["skin1"] + CLOTH + DESK + BEIGE + RAMP["denim"])
        p.halo(x + w + 8, y + h + 4, 14, 9, FLAME[3], (0.08, 0.16, 0.26), L="base", only=lit)
        for xx in range(x - 1, x + w + 1):
            p.px(xx, y - 1, FLAME[1])
        for yy in range(y, y + h):
            p.px(x - 1, yy, FLAME[1])
            p.px(x + w, yy, FLAME[0])


def terminal(p: Pix, x0, g, night, motion):
    """The room the code is watched from, standing on the rule at row g from column x0: the desk with the tower
    under it, the monitor on it with the code falling down its glass, the keyboard before it, and the hacker asleep
    over his folded arms on the desk in his chair. Returns the span it covers."""
    t = _tones(night)
    top = g - 17
    desk(p, x0, x0 + 38, top, g, night)
    p.sprite(x0 + 6, g - len(TOWER), TOWER, t)
    p.px(x0 + 11, g - len(TOWER) + 7, FLAME[4] if night else FLAME[2])
    mx, my = x0, top - len(MONITOR)
    p.sprite(mx, my, MONITOR, t)
    screen(p, mx + GLASS_AT[0], my + GLASS_AT[1], *GLASS_SIZE, night, motion)
    p.hline(x0 + 23, x0 + 31, top - 1, t["s"])
    p.hline(x0 + 24, x0 + 31, top - 2, t["c"])
    p.sprite(x0 + 40, g - len(CHAIR), CHAIR, t)
    p.sprite(x0 + 23, g - len(SLEEPER), SLEEPER, t)
    return (x0 - 1, x0 + 50)


# --------------------------------------------------------------------------- the city of code
# The towers, back row first: (x, width, height, row), a back tower traced dimmer than one in front.
TOWERS = ((0, 13, 50, 0), (37, 14, 60, 0), (5, 14, 40, 1), (17, 17, 70, 1), (32, 12, 48, 1), (42, 10, 30, 1))


def city(p: Pix, x0, g, night, motion, seed=5, room=74):
    """The city the code is the world of, standing on the rule at row g from column x0 and rising up to `room` rows:
    towers traced in phosphor by night and in the ribbon's ink by day, the back row dimmer, each lit along its top
    and left edges with a setback near its head, its face windowed in the code's glyphs, a few of them lit and
    twinkling by night, and on the tallest a spire whose light blinks. Drawn back to front, each face hiding what
    stands behind it. Returns the span it covers."""
    rnd = random.Random(seed)
    tall = max(h for _, _, h, _ in TOWERS)
    k = min(1.0, room / (tall + 12))
    for dx, w, h, row in TOWERS:
        h = round(h * k)
        x, top = x0 + dx, g - h
        if night:
            face, edge, lit, dim, win, hot = (GLASS[2], FLAME[1], FLAME[2], FLAME[0], FLAME[1], FLAME[3]) if row == 0 \
                else (GLASS[3], FLAME[2], FLAME[4], FLAME[1], FLAME[2], FLAME[5])
        else:
            face, edge, lit, dim, win, hot = (PAPER[4], RIBBON[4], RIBBON[3], RIBBON[6], RIBBON[5], RIBBON[3]) \
                if row == 0 else (PAPER[3], RIBBON[2], RIBBON[0], RIBBON[5], RIBBON[4], RIBBON[1])
        step = 3 if w >= 12 else 0
        p.rect(x + step, top, w - step, h, face)
        if step:
            p.rect(x, top + 5, step, h - 5, face)
            p.hline(x + step, x + w, top, lit)
            p.vline(x + step, top, top + 5, lit)
            p.hline(x, x + step + 1, top + 5, lit)
            p.vline(x, top + 5, g, lit)
        else:
            p.hline(x, x + w, top, lit)
            p.vline(x, top, g, lit)
        p.vline(x + w - 1, top + 1, g, edge)
        for gx in range(x + 2, x + w - rain.W, rain.COLUMN):
            for gy in range(top + 7, g - rain.H - 1, rain.PITCH):
                bright = rnd.random() < (0.12 if row == 0 else 0.2)
                c = hot if bright else (win if rnd.random() < 0.6 else dim)
                L = p.twinkle(gx + gy) if (night and motion and bright) else "base"
                rain.write(p, gx, gy, rnd.choice(rain.NAMES), c, L)
    dx, w, h, _ = TOWERS[3]
    h = round(h * k)
    mx, spire = x0 + dx + w // 2, min(10, max(0, g - h - 18))
    lit = FLAME[4] if night else RIBBON[0]
    if spire >= 4:
        p.vline(mx, g - h - spire, g - h, lit)
        p.hline(mx - 1, mx + 2, g - h - 2, lit)
        p.px(mx, g - h - spire - 1, FLAME[5] if night else RIBBON[0], p.blink(1) if motion and night else "base")
        if night:
            p.halo(mx + 0.5, g - h - spire - 0.5, 3, 3, FLAME[4], (0.1, 0.2))
    return (x0 - 1, x0 + 54)


# --------------------------------------------------------------------------- the corridor of code
class WallRain(rain.Rain):
    """The code falling down a wall seen in perspective: a `rain.Rain` over the wall's bounding box, clipped to the
    wall's own outline, `points`."""

    def __init__(self, p: Pix, points, ramp, night: bool, seed: int = 1, lengths=(3, 9), dim: bool = False):
        xs, ys = [x for x, _ in points], [y for _, y in points]
        box = (math.floor(min(xs)), math.floor(min(ys)), math.ceil(max(xs)), math.ceil(max(ys)))
        super().__init__(p, box, ramp, night, seed=seed, lengths=lengths, dim=dim)
        self.points = points

    def fall(self, z: float = -8):
        p, n = self.p, len(self.p.raws)
        super().fall(z)
        if len(p.raws) == n:
            return
        cid = f"wc{sum(1 for d in p.defs if d.startswith(WALL_CLIP))}"
        p.defs.append(f'{WALL_CLIP}{cid[2:]}"><polygon points="'
                      + " ".join(f"{num(x)} {num(y)}" for x, y in self.points) + '"/></clipPath>')
        depth, order, moving, still = p.raws[-1]
        p.raws[-1] = (depth, order, f'<g clip-path="url(#{cid})">{moving}</g>',
                      f'<g clip-path="url(#{cid})">{still}</g>')


WALL_CLIP = '<clipPath id="wc'
DEPTHS = (1.0, 1.32, 1.75, 2.3, 3.0)      # the depths the corridor's ribs stand at, the near edge first


def _line(p: Pix, x0, y0, x1, y1, c, L="base"):
    """A line of single units from (x0, y0) to (x1, y1), stepped as a pixel line is."""
    x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        p.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c, L)


def corridor(p: Pix, x0, y0, x1, g, night: bool, motion: bool, seed: int = 13) -> dict:
    """The corridor of code, the world as the code that writes it, from x0 to x1 and from row y0 down to the floor at
    row g: a hallway seen down its length to a door at its far end, its walls, ceiling and floor drawn in the code's
    own lines, ribs of phosphor across them at even steps of depth and the floor's seams running away to the door,
    and down both walls the code falling, its streams clipped to the walls as they recede. By night the lines burn on
    the dark glass and the door at the end blazes white, its light thrown down the floor toward the viewer; by day the
    corridor is printed on the greenbar in the ribbon's ink, the door left bare paper. Returns where its floor and its
    door are."""
    cx, cy = (x0 + x1) / 2, y0 + (g + 1 - y0) * 0.42
    s = 1 / DEPTHS[-1]

    def at(k):                                  # the corridor's section at scale k: (left, top, right, foot)
        return cx - (cx - x0) * k, cy - (cy - y0) * k, cx + (x1 - cx) * k, cy + (g + 1 - cy) * k
    fx0, fy0, fx1, fy1 = at(s)
    walls = {"left": [(x0, y0), (fx0, fy0), (fx0, fy1), (x0, g + 1)],
             "right": [(x1, y0), (fx1, fy0), (fx1, fy1), (x1, g + 1)],
             "ceiling": [(x0, y0), (x1, y0), (fx1, fy0), (fx0, fy0)],
             "floor": [(x0, g + 1), (x1, g + 1), (fx1, fy1), (fx0, fy1)]}
    if night:                                   # the glass of each surface, under the code that falls down it
        fills = {"ceiling": GLASS[1], "left": GLASS[2], "right": GLASS[2], "floor": GLASS[3]}
        p.layer("far")
        p.shapes["far"].extend(f'<polygon points="{" ".join(f"{num(x)} {num(y)}" for x, y in walls[k])}" '
                               f'fill="{c}"/>' for k, c in fills.items())
        p.shapes["far"].append(f'<rect x="{num(fx0)}" y="{num(fy0)}" width="{num(fx1 - fx0)}" '
                               f'height="{num(fy1 - fy0)}" fill="{GLASS[0]}"/>')
    rib, edge, seam = (FLAME[1], FLAME[3], FLAME[1]) if night else (RIBBON[4], RIBBON[1], RIBBON[5])
    # The code down both walls, falling, its streams brightest at the near end.
    ramp = FLAME if night else RIBBON
    rnd = random.Random(seed)
    for side, pts in (("left", walls["left"]), ("right", walls["right"])):
        r = WallRain(p, pts, ramp, night, seed=rnd.randrange(1000), lengths=(3, 9))
        xs = range(x0 + 1, round(fx0) - 3, rain.COLUMN) if side == "left" else \
            range(x1 - rain.W - 1, round(fx1) + 2, -rain.COLUMN)
        for x in xs:
            span = (g - y0) // rain.PITCH + 10
            r.stream(x, y0 + rnd.randrange(span) * rain.PITCH, pace=rnd.choice((0.09, 0.12, 0.15)))
        r.fall(z=-7)
    # The ribs across the walls, the ceiling and the floor, and the floor's seams running away to the door.
    for k in [1 / d for d in DEPTHS[1:-1]]:
        a, b, c, d = at(k)
        for (xa, ya), (xb, yb) in (((a, b), (c, b)), ((a, d), (c, d)), ((a, b), (a, d)), ((c, b), (c, d))):
            _line(p, xa, ya, xb, yb, rib)
    for i in (1, 2, 3):
        xn = x0 + (x1 - x0) * i / 4
        _line(p, xn, g, cx + (xn - cx) * s, fy1, seam)
    # The corridor's four long edges, burning brightest.
    for (xa, ya), (xb, yb) in (((x0, y0), (fx0, fy0)), ((x1, y0), (fx1, fy0)), ((x0, g), (fx0, fy1)),
                               ((x1, g), (fx1, fy1))):
        _line(p, xa, ya, xb, yb, edge)
    _line(p, fx0, fy0, fx1, fy0, edge)
    _line(p, fx0, fy1, fx1, fy1, edge)
    _line(p, fx0, fy0, fx0, fy1, edge)
    _line(p, fx1, fy0, fx1, fy1, edge)
    # The door at the far end.
    dw, dh = max(4, round((fx1 - fx0) * 0.32)), max(7, round((fy1 - fy0) * 0.72))
    dx, dy = round(cx - dw / 2), round(fy1) - dh
    if night:
        p.rect(dx, dy, dw, dh, FLAME[5])
        p.rect(dx + 1, dy + 1, dw - 2, dh - 1, FLAME[6])
        p.halo(cx, dy + dh / 2, dw * 2.2, dh * 1.1, FLAME[4], (0.05, 0.1, 0.18, 0.28), shape=True)
        cid = f"dr{len(p.defs)}"
        floor = " ".join(f"{num(x)} {num(y)}" for x, y in walls["floor"])
        p.defs.append(f'<clipPath id="{cid}"><polygon points="{floor}"/></clipPath>')
        p.layer("pool")
        p.shapes["pool"].append(f'<g clip-path="url(#{cid})" fill="{FLAME[4]}"><polygon points="{num(dx)} {round(fy1)} '
                                f'{num(dx + dw)} {round(fy1)} {num(cx + (x1 - cx) * 0.55)} {g + 1} '
                                f'{num(cx - (cx - x0) * 0.55)} {g + 1}" fill-opacity=".12"/></g>')
    else:
        p.box(dx - 1, dy - 1, dw + 2, dh + 1, RIBBON[1])
    return {"floor": (x0, x1, g), "door": (dx, dy, dw, dh), "vanish": (cx, cy), "far": (fx0, fy0, fx1, fy1)}


# The man in the long coat seen from behind, standing in the corridor looking down it, 16 by 32: the back of his head
# (h, lit H), his collar (n), his long coat (c, in shade C) and his boots (k); the cells along his outline take the
# light from the door ahead (see `stranger`). The second is his coat's hem stirring in the code's wind.
STRANGER = (
    ["......hhhh......", ".....hHHhhh.....", ".....hHhhhh.....", ".....hhhhhh.....", "......hhhh......",
     "......nnnn......", "....ccccccccc...", "...cccccccccccc.", "..cccccccccccccc", "..cccccccccccccc",
     "..cccccccccccccc", "..cccccccccccccc", "..ccccccccccccc.", "..ccccccccccccc.", "..ccccccccccccc.",
     "..ccccccccccccc.", "..ccccccccccccc.", "...cccccccccccc.", "...cccccccccccc.", "...cccccccccccc.",
     "...ccccccCcccc..", "...ccccccCcccc..", "...ccccccCccccc.", "..cccccccCccccc.", "..cccccccCccccc.",
     "..ccccccCCcccccc", ".cccccccCCcccccc", ".ccccccc.Ccccccc", "....kkk...kkk...", "....kkk...kkk...",
     "....kkk...kkk...", "...kkkk...kkkk.."],
    ["......hhhh......", ".....hHHhhh.....", ".....hHhhhh.....", ".....hhhhhh.....", "......hhhh......",
     "......nnnn......", "....ccccccccc...", "...cccccccccccc.", "..cccccccccccccc", "..cccccccccccccc",
     "..cccccccccccccc", "..cccccccccccccc", "..ccccccccccccc.", "..ccccccccccccc.", "..ccccccccccccc.",
     "..ccccccccccccc.", "..ccccccccccccc.", "...cccccccccccc.", "...ccccccccccccc", "...cccccccccccccc",
     "...ccccccCccccccc", "...ccccccCcccccc.", "...ccccccCcccccc", "..cccccccCcccccc", "..cccccccCcccccc.",
     "..ccccccCCccccccc", ".cccccccCCccccccc", ".ccccccc.Cccccccc", "....kkk...kkk...", "....kkk...kkk...",
     "....kkk...kkk...", "...kkkk...kkkk.."],
)
STIR = 4.0        # seconds his coat takes to stir and settle: within the hand's four to eight


def stranger(p: Pix, x, g, night: bool, motion: bool):
    """The man in the long coat standing in the corridor, his feet on row g from column x, seen from behind as he
    looks down it to the door: dark against the light, the cells along his outline lit by the door ahead, in
    phosphor by night and left as the paper by day where the ribbon's ink stops; in a moving header his coat's hem
    stirs and settles on a four-second loop. The still twin holds it settled."""
    if night:
        pal = {"h": HAIR[1], "H": HAIR[3], "n": CLOTH[2], "c": CLOTH[1], "C": CLOTH[0], "k": CLOTH[0]}
        rim = FLAME[3]
    else:
        pal = {"h": RIBBON[0], "H": RIBBON[2], "n": RIBBON[1], "c": RIBBON[1], "C": RIBBON[0], "k": RIBBON[0]}
        rim = RIBBON[3]
    keys = []
    for i, art in enumerate(STRANGER):
        cells = {(cx, cy): pal[ch] for cy, row in enumerate(art) for cx, ch in enumerate(row) if ch in pal}
        for (cx, cy) in list(cells):
            edge = any((cx + dx, cy + dy) not in cells for dx, dy in ((1, 0), (-1, 0)))
            if edge and 0 < cy < len(art) - 4:
                cells[(cx, cy)] = rim
        key = ("stranger", i, night)
        if key not in p.syms:
            p.symbol(key, cells)
        keys.append(key)
    top = g - len(STRANGER[0]) + 1
    sa, sb = p.syms[keys[0]], p.syms[keys[1]]
    still = f'<use href="#{sa}" x="{x}" y="{top}"/>'
    moving = still
    if motion:
        moving = (f'<use href="#{sa}" x="{x}" y="{top}"><animate attributeName="opacity" values="1;0;1;0" '
                  f'keyTimes="0;.25;.5;.75" dur="{num(STIR)}s" repeatCount="indefinite" calcMode="discrete"/></use>'
                  f'<use href="#{sb}" x="{x}" y="{top}" opacity="0"><animate attributeName="opacity" values="0;1;0;1" '
                  f'keyTimes="0;.25;.5;.75" dur="{num(STIR)}s" repeatCount="indefinite" calcMode="discrete"/></use>')
    p.raw(1, moving, still)


# --------------------------------------------------------------------------- the great tower
# The great tower's sections, from its foot up: (width, the share of its height its top stands at). Each steps back
# from the one under it, as a tower of the twenties steps back as it climbs.
SECTIONS = ((26, 0.5), (20, 0.72), (14, 0.88), (8, 1.0))


def _face(p: Pix, x, top, w, g, night: bool, motion: bool, rnd, near: bool, windows: bool = True, great=False):
    """One tower's face from row `top` to the ground at row g: glass by night and the paper's green by day, traced
    along its top and left in phosphor or the ribbon's ink and in shade down its right, windowed in the code's glyphs,
    a few lit and twinkling by night; a face standing back (`near` false) traced dimmer, and the great tower's
    (`great`) brightest of all, its windows burning."""
    if night:
        face, edge, lit, dim, win, hot = (GLASS[4], FLAME[3], FLAME[5], FLAME[2], FLAME[3], FLAME[6]) if great \
            else (GLASS[3], FLAME[2], FLAME[4], FLAME[1], FLAME[2], FLAME[5]) if near \
            else (GLASS[2], FLAME[1], FLAME[2], FLAME[0], FLAME[1], FLAME[3])
    else:
        face, edge, lit, dim, win, hot = (PAPER[2], RIBBON[1], RIBBON[0], RIBBON[4], RIBBON[2], RIBBON[0]) if great \
            else (PAPER[3], RIBBON[2], RIBBON[0], RIBBON[5], RIBBON[4], RIBBON[1]) if near \
            else (PAPER[4], RIBBON[4], RIBBON[3], RIBBON[6], RIBBON[5], RIBBON[3])
    p.rect(x, top, w, g + 1 - top, face)
    p.hline(x, x + w, top, lit)
    p.vline(x, top, g + 1, lit)
    p.vline(x + w - 1, top + 1, g + 1, edge)
    if windows:
        for gx in range(x + 2, x + w - rain.W, rain.COLUMN):
            for gy in range(top + 3, g - rain.H - 1, rain.PITCH):
                bright = rnd.random() < (0.22 if near else 0.12)
                c = hot if bright else (win if rnd.random() < 0.6 else dim)
                L = p.twinkle(gx + gy) if (night and motion and bright) else "base"
                rain.write(p, gx, gy, rnd.choice(rain.NAMES), c, L)


def tower(p: Pix, x0, x1, top, g, night: bool, motion: bool, seed: int = 21) -> dict:
    """The great tower of the city of code, rising from the ground at row g to its spire's tip at row `top`, between
    x0 and x1: stepping back three times as it climbs to a crown and a spire, its every face windowed in the code's
    glyphs and traced in phosphor by night or the ribbon's ink by day, a light blinking on its spire's tip after dark;
    a lesser tower standing back at either side of it and a low block before it at the left, each windowed in the
    glyphs too, all of it standing in the code that falls behind it. Returns where its spire's tip is."""
    rnd = random.Random(seed)
    w = SECTIONS[0][0]
    cx = min(round(x0 + (x1 - x0) * 0.6), x1 - 4 - w // 2)
    body = g - top - 12                          # the rows the tower's sections climb, under its spire
    left = max(x0, cx - w // 2 - 17)
    if cx - w // 2 + 2 - left >= 10:
        _face(p, left, g - round(body * 0.64), cx - w // 2 + 2 - left, g, night, motion, rnd, near=False)
    right = min(x1, cx + w // 2 + 13)
    _face(p, cx + w // 2 - 3, g - round(body * 0.46), right - (cx + w // 2 - 3), g, night, motion, rnd, near=False)
    base = g
    for wd, share in SECTIONS:
        st = g - round(body * share)
        _face(p, cx - wd // 2, st, wd, base, night, motion, rnd, near=True, great=True)
        base = st
    tip = base - 12
    lit = FLAME[4] if night else RIBBON[0]
    p.vline(cx, tip, base, lit)
    p.hline(cx - 1, cx + 2, base - 4, lit)
    p.hline(cx - 1, cx + 2, base - 8, lit)
    p.px(cx, tip - 1, FLAME[5] if night else RIBBON[0], p.blink(1) if (motion and night) else "base")
    if night:
        p.halo(cx + 0.5, tip - 0.5, 3, 3, FLAME[4], (0.1, 0.2))
    _face(p, max(x0, left - 6), g - round(body * 0.28), 13, g, night, motion, rnd, near=True)
    return {"tip": (cx, tip)}


# --------------------------------------------------------------------------- the rules
def ruled(p: Pix, x0, x1, y, night: bool, seed: int = 0):
    """A rule as a line of the terminal's cells, from x0 to x1 on row y: a dash two units long every sixth unit, in
    phosphor by night and the ribbon's ink by day, their places stepping with `seed` so no two rules dash alike."""
    c = FLAME[2] if night else RIBBON[3]
    for x in range(x0 + 2 + seed % 6, x1 - 2, 6):
        p.hline(x, x + 2, y, c)


# --------------------------------------------------------------------------- the footers and links
# A heart lit on the glass, seven by six, each digit a tone of the phosphor: white-hot at its upper left lobe, where
# the one light strikes it, and dimmer toward its point.
HEART = [".65.54.", "6554443", "5444332", ".44332.", "..332..", "...2..."]


def heart(p: Pix, x, y, L="base"):
    """The heart in BUILT WITH (heart) BY, lit in phosphor: it reads on the printout by day as on the glass by
    night, as a lit cell does on either."""
    p.sprite(x, y, HEART, {str(i): FLAME[i] for i in range(7)}, 1, L)


def scale_bar(p: Pix, x0, y0, w, h, period=5):
    """The graphic scale's bar as a line of the terminal's cells, lit and dark by turns, `period` units a cell: a
    lit cell of phosphor bright along its top and a step dimmer at its foot, a dark one of the glass with its scan
    line, so the bar reads on the printout and on the glass alike."""
    for xx in range(x0, x0 + w):
        lit = ((xx - x0) // period) % 2 == 0
        for yy in range(y0, y0 + h):
            top, foot = yy == y0, yy == y0 + h - 1
            if lit:
                p.px(xx, yy, FLAME[5] if top else FLAME[3] if foot else FLAME[4])
            else:
                p.px(xx, yy, GLASS[5] if top else GLASS[1] if foot else GLASS[3])


# The links' icons, each seven by seven at most and of the room the code is watched from: the terminal with a
# prompt on its glass, a floppy disk, a punched card and the cursor blinking after a prompt. Their case and plastic in
# L (lit), c and d (shade), the glass in g, a lit cell in #, a shutter or a label in w, a card's manila in m (lit M,
# in shade n) with its holes punched through.
ICONS = {
    "terminal": ["LLLLLLc", "Lggggdd", "Lg##gdd", "Lggggdd", "cdddddd", "..Lcd..", ".ccccd."],
    "floppy": ["LLLLLLc", "Lcwwwcd", "Lcw.wcd", "Lcccccd", "Lwwwwwd", "Lwwwwwd", "cdddddd"],
    "card": [".......", "..MMMMn", ".Mm.mmn", "M.m.m.n", "Mmm.m.n", "Mnnnnnn", "......."],
    "cursor": [".......", "#......", ".#.....", "..#....", ".#.....", "#..###.", "......."],
}
LINK_SPRITES = ("terminal", "floppy", "card", "cursor")


def icon_pal(night: bool, ink: str) -> dict:
    """The icons' tones: by night a dark case lit by its own glass, by day the printout's ribbon on the paper; a
    lit cell is phosphor by night and the ribbon's ink by day, a cursor is drawn in the letters' own ink, and a
    punched card is manila, a step dimmer by night."""
    M = RAMP["manila"]
    if night:
        return {"L": CASE[5], "c": CASE[3], "d": CASE[1], "g": GLASS[2], "w": BEIGE[3], "#": ink,
                "M": M[4], "m": M[3], "n": M[1]}
    return {"L": RIBBON[3], "c": RIBBON[2], "d": RIBBON[0], "g": RIBBON[1], "w": PAPER[6], "#": ink,
            "M": M[5], "m": M[4], "n": M[2]}


def prompt(p: Pix, x, y, night: bool):
    """A prompt and its cursor, seven by five, top-left at (x, y): the chevron the terminal waits behind and the block
    of its cursor, lit in phosphor by night and struck in the ribbon's ink by day."""
    c, hot = (FLAME[4], FLAME[6]) if night else (RIBBON[1], RIBBON[0])
    for d in range(3):
        p.px(x + d, y + d, c)
        p.px(x + d, y + 4 - d, c)
    p.rect(x + 4, y + 3, 3, 2, hot)


# --------------------------------------------------------------------------- the footers' footing
KEY_W, KEY_H = 6, 4     # a key of the keyboard and the gap after it, and its rows from its lit top to its shadow
FOOT_RUN = 24           # the least run of columns the keyboard's upper row rises along where the cells leave it room
# A small terminal, 13 by 12, where the whole one has no room: its case (L lit, c, s shaded), the glass (g) with a
# prompt lit on it (#) and the cursor after it (o), and its stand.
SMALL_MONITOR = ["LLLLLLLLLLLLc", "Lcccccccccccs", "Lcgggggggggcs", "Lcg##g#gggcs.", "Lcgggggggggcs",
                 "Lcg###ogggcs.", "Lcgggggggggcs", "Lcccccccccccs", ".ssssssssssss", "....LcccS....",
                 "..LLcccccSS..", "..SSSSSSSSS.."]


def _key(p: Pix, x, y, night: bool, rows: int = KEY_H):
    """One key of the keyboard with its top-left at (x, y), `rows` tall: its cap lit along its top, its face, and its
    foot in shade; beige plastic by day, the dark case's plastic by night."""
    if night:
        top, face, foot = CASE[4], CASE[3], CASE[1]
    else:
        top, face, foot = BEIGE[5], BEIGE[3], BEIGE[1]
    p.hline(x, x + KEY_W - 1, y, top)
    if rows > 2:
        p.rect(x, y + 1, KEY_W - 1, rows - 2, face)
    if rows > 1:
        p.hline(x, x + KEY_W - 1, y + rows - 1, foot)


def footing(p: Pix, night: bool, after: int = 0):
    """A footer once its words are set: the keyboard the code is typed on along its foot, seated in the frame's foot,
    a row of keys its whole width as tall as keeps a unit clear of the lowest word, the gaps between them dark; its
    upper row rising, set half a key over, wherever the cells leave it room along FOOT_RUN columns or more, the ruled
    lines between the cells standing on it; and at the rightmost place from column `after` on where the cells leave it
    free, the terminal standing behind the keys with the code on its glass, its power light burning, or a small one
    where it has less room. By night the glass glows and its light falls on the keys."""
    w, h = p.w, p.h
    base = p.layers["base"]
    low = max((b[3] for b in p.words), default=0)
    ledge = max(low + 1, h - 1 - KEY_H)                  # the keys' top row; the keyboard's dark base is the last
    rows = h - 1 - ledge
    gap = CASE[0] if night else BEIGE[0]
    for x in range(EDGE, w - EDGE):
        for y in range(ledge, h):
            p.px(x, y, gap)
    for x in range(EDGE + 1, w - EDGE - KEY_W + 1, KEY_W):
        _key(p, x, ledge, night, rows)

    def free(x0, y0, x1, y1):
        """Whether the box from (x0, y0) to (x1, y1) lies on the bare sheet, nothing solid drawn on it, a unit and more
        from every word."""
        return EDGE + 1 <= x0 and x1 <= w - EDGE - 1 and EDGE <= y0 \
            and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) \
            and not any(":" not in base.get((x, y), ":") for x in range(x0, x1) for y in range(y0, y1))
    mark = None
    for art in (MONITOR, SMALL_MONITOR):
        mw, mh = len(art[0]), len(art)
        mark = next(((x, art) for x in range(w - EDGE - 2 - mw, max(EDGE + 1, after) - 1, -1)
                     if free(x - 1, ledge - mh, x + mw + 1, ledge)), None)
        if mark:
            break
    taken = range(mark[0] - 2, mark[0] + len(mark[1][0]) + 2) if mark else range(0)
    rise = [x not in taken and free(x, ledge - KEY_H - 1, x + 1, ledge) for x in range(w)]
    x = EDGE + 1
    while x < w - EDGE - 1:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - EDGE - 1) if not rise[i]), w - EDGE - 1)
        if b - x >= FOOT_RUN:
            for xx in range(x, b):
                for y in range(ledge - KEY_H, ledge):
                    p.px(xx, y, gap)
            for kx in range(x + KEY_W // 2, b - KEY_W + 1, KEY_W):
                _key(p, kx, ledge - KEY_H, night)
        x = b
    if mark:
        mx, art = mark
        top = ledge - len(art)
        t = _tones(night)
        if art is MONITOR:
            p.sprite(mx, top, art, t)
            screen(p, mx + GLASS_AT[0], top + GLASS_AT[1], *GLASS_SIZE, night, False, seed=7)
        else:
            p.sprite(mx, top, art, dict(t, **{"#": FLAME[4] if night else FLAME[3], "o": FLAME[6] if night
                                              else FLAME[4]}))
            if night:
                p.halo(mx + 6, top + 4, 9, 6, FLAME[3], (0.05, 0.1, 0.16))


# --------------------------------------------------------------------------- the elements
def card_screen(p: Pix, night: bool, x, y, w, h, lid: bool):
    """A schematic card as a window on the terminal: its icon's cell dark glass by night and the printout's green bar
    by day, a scan line of phosphor down the cell's edge, or by day the perforation the paper tears along; and on a
    card with a lid a row of three status lights at its top right, the middle one burning."""
    cell = GLASS[1] if night else PAPER[4]
    fill = GLASS[3] if night else PAPER[6]
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + 11):
            if p.get(xx, yy) == fill:
                p.px(xx, yy, cell)
    for yy in range(y + 1, y + h - 1):
        if night:
            p.px(x + 11, yy, FLAME[1])
        elif yy % 2 == 0:
            p.px(x + 11, yy, RIBBON[4])
    if lid:
        for i, c in enumerate((FLAME[2], FLAME[5], FLAME[2]) if night else (RIBBON[4], RIBBON[1], RIBBON[4])):
            p.px(x + w - 12 + i * 2, y + 1, c)


def wire_code(p: Pix, cells, night: bool):
    """The code running along a wire: every seventh unit a white-hot head with a short trail fading behind it, as a
    stream runs down the glass; by day struck in the ribbon's ink."""
    tones = (FLAME[6], FLAME[4], FLAME[3]) if night else (RIBBON[0], RIBBON[1], RIBBON[2])
    run = cells[1:-4]
    for i in range(len(run) - 1, 1, -7):
        for j, c in enumerate(tones):
            if i - j >= 0:
                x, y, _ = run[i - j]
                p.px(x, y, c)


def code_bar(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a bar lit on the glass, standing on the base line: scanned in lines, its left edge
    brightest, its head white-hot as a stream's is; by day struck by the printer's head in rows of dots."""
    for j in range(v):
        y = base - 1 - j
        for xx in range(bx, bx + bw):
            if night:
                if j >= v - 2:
                    c = FLAME[6] if j == v - 1 else FLAME[5]
                elif xx == bx:
                    c = FLAME[4]
                elif xx == bx + bw - 1:
                    c = FLAME[2]
                else:
                    c = FLAME[3] if j % 2 else FLAME[2]
            else:
                if j == v - 1:
                    c = RIBBON[0]
                elif xx == bx + bw - 1:
                    c = RIBBON[1]
                else:
                    c = RIBBON[1] if j % 2 else RIBBON[3]
            p.px(xx, y, c)


def cursor(p: Pix, x, y, night: bool, w: int = 2, h: int = 4):
    """The cursor, a block `w` by `h` with its top-left at (x, y), white-hot by night and the ribbon's darkest by
    day."""
    p.rect(x, y, w, h, FLAME[6] if night else RIBBON[0])
    if night:
        p.halo(x + w / 2, y + h / 2, w + 2, h + 1, FLAME[4], (0.1, 0.2))


def media(i: int, xx, yy, y0, y1, night: bool) -> str:
    """The `i`-th file type as the media the code was kept on, by turns: a punched card's manila with its holes, a
    floppy's blue with its shutter every tenth unit, the brown of magnetic tape with its sheen, and the printout's
    greenbar in bands; a step dimmer by night."""
    k = -1 if night else 0
    kind = i % 4
    if kind == 0:
        M = RAMP["manila"]
        return M[max(0, 1 + k + 1)] if (xx % 4 == 1 and (yy - y0) % 4 == 2) else M[4 + k]
    if kind == 1:
        D = RAMP["denim"]
        return BEIGE[5 + k] if xx % 10 in (3, 4) else D[3 + k]
    if kind == 2:
        W = RAMP["desk"]
        return W[5 + k] if yy == y0 + 3 else W[3 + k]
    return PAPER[max(0, (5 if (yy - y0) // 3 % 2 == 0 else 4) + k)]


def glass_cell(q: Pix, ox, oy, night: bool):
    """A counter's digit cut into a cell of glass in the terminal's case, eleven by fifteen, the case lit along its
    top and left and in shade along its foot and right; by day a cell printed on the paper, ruled in the ribbon's
    ink."""
    if night:
        q.rect(ox, oy, 11, 15, GLASS[1])
        q.bevel(ox - 1, oy - 1, 13, 17, CASE[5], CASE[1])
    else:
        q.rect(ox, oy, 11, 15, PAPER[5])
        q.box(ox, oy, 11, 15, RIBBON[3])
        q.hline(ox + 1, ox + 10, oy + 14, RIBBON[4])


def code_line(p: Pix, x0, x1, y, night: bool):
    """The releases' line as a line of the code: a trace two rows deep with a lit cell every fourth unit, in phosphor
    by night and the ribbon's ink by day."""
    top, foot, dot = (FLAME[2], FLAME[1], FLAME[4]) if night else (RIBBON[2], RIBBON[4], RIBBON[0])
    p.hline(x0, x1, y, top)
    p.hline(x0, x1, y + 1, foot)
    for x in range(x0 + 2, x1, 4):
        p.px(x, y, dot)


def lit_cell(p: Pix, x, gy, kind: str, night: bool):
    """A release on the line as a cell lit on the glass at column x: a block seven across, white-hot at its heart, for
    a big one; five across for a release; a single unit over the line for a patch; an empty frame for one still to
    come; and the cursor for the first survey."""
    hot, lit, dim = (FLAME[6], FLAME[5], FLAME[2]) if night else (RIBBON[0], RIBBON[0], RIBBON[3])
    if kind == "minor":
        p.px(x, gy - 2, lit)
    elif kind == "made":
        p.rect(x - 1, gy - 5, 2, 4, lit)
    elif kind == "next":
        p.box(x - 1, gy - 4, 3, 3, dim)
    elif kind == "big":
        p.rect(x - 3, gy - 8, 7, 7, lit)
        p.rect(x - 1, gy - 6, 3, 3, hot)
        if night:
            p.halo(x + 0.5, gy - 4.5, 7, 7, FLAME[4], (0.1, 0.2))
    else:
        p.rect(x - 2, gy - 6, 5, 5, lit)
        p.rect(x - 1, gy - 5, 3, 3, hot if night else lit)


# A contributor's disk, fifteen across: a floppy seen from the front, its plastic shell lit along its top and left
# (b, L) and shaded down its right and foot (S), the corner cut at its top right, the metal shutter across its top
# (m, lit M) with the slot in it (d), and its label (w) under a stripe of colour (g).
FLOPPY = [
    "LLLLLLLLLLLLL..",
    "LbbMMMMMMMMbbS.",
    "LbbmmmmmddmbbbS",
    "LbbmmmmmddmbbbS",
    "LbbmmmmmmmmbbbS",
    "LbbbbbbbbbbbbbS",
    "LbgggggggggggbS",
    "LbwwwwwwwwwwwbS",
    "LbwwwwwwwwwwwbS",
    "LbwwwwwwwwwwwbS",
    "LbwwwwwwwwwwwbS",
    "LbwwwwwwwwwwwbS",
    "LbwwwwwwwwwwwbS",
    "LbwwwwwwwwwwwbS",
    "SSSSSSSSSSSSSSS",
]
DISKS = ("case", "denim", "red", "beige")     # the plastics the shells are moulded in, a contributor's each by turns


def floppy(p: Pix, cx, cy, i: int, night: bool) -> tuple:
    """Contributor `i`'s floppy disk centred on (cx, cy): its shell in the plastic of DISKS that falls to it, its
    shutter of pale metal with the slot in it, and its white label under a stripe of the ribbon's red, all a tone down
    by night, when only the glass lights the room. Returns the label's box under its stripe."""
    k = -2 if night else 0
    R = RAMP[DISKS[i % len(DISKS)]]

    def t(ramp, j):
        return ramp[max(0, min(len(ramp) - 1, j + k))]
    x0, y0 = cx - 7, cy - 7
    p.sprite(x0, y0, FLOPPY, {"L": t(R, 4), "b": t(R, 3), "S": t(R, 1), "M": t(PAPER, 6), "m": t(PAPER, 4),
                              "d": CASE[1], "g": t(RAMP["red"], 4), "w": t(PAPER, 6)})
    return (x0 + 2, y0 + 7, 11, 7)


def lit_ring(p: Pix, cx, cy, r0, r1, night: bool):
    """A ring of the code's cells round a seal, from radius r0 to r1: sixteen cells lit on it by turns bright and dim,
    and a fine circle of the dimmest round them; by day struck in the ribbon's ink."""
    fine, lit, dim = (FLAME[1], FLAME[5], FLAME[2]) if night else (RIBBON[4], RIBBON[0], RIBBON[3])
    for a in range(0, 360, 3):
        ang = math.radians(a)
        p.px(round(cx + r1 * math.cos(ang) - 0.5), round(cy + r1 * math.sin(ang) - 0.5), fine)
    mid = (r0 + r1) / 2
    for i in range(16):
        ang = math.radians(i * 22.5)
        x, y = round(cx + mid * math.cos(ang) - 1), round(cy + mid * math.sin(ang) - 1)
        p.rect(x, y, 2, 2, lit if i % 2 == 0 else dim)
