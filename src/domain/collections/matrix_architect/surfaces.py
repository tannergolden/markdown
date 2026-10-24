# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Architect set's smaller surfaces, drawn on the shared pixel canvas: the footers' footing, emblem, heart and
graphic scale, the link buttons, the badges and plates, and the stuffs of its boards and its podium.

Every footer stands on the front edge of the Architect's console, a brass rail over its charcoal face set with a row
of keys, a few of them lit, laid along its foot over the frame's; its meter bridge rises behind it wherever the cells
leave the wall free, a row of little tubes each showing a level in the phosphor, and a title block stands a set on it
after its last cell, showing the room itself; a little set glows in the corner of its notes. The heart burns on a
screen in the hand's phosphor; the graphic scale's bar is a row of little tubes, lit and dark by turns, as a level
meter on the console lights. A link button is a set's charcoal plastic in a rim of the frame's pale grey, vents slotted
along its top and its letters the phosphor's green, and the sprite at its start is one of the room's things: a
television with its picture on, the white wingback, the pen and the white rabbit. A badge wears a band of a set's
charcoal plastic along its top, its vents slotted in it and a power light burning green at its right end; its label is
charcoal plastic lettered in pale grey, a live badge's label is the pen's brass, and a plate is the white room's wall
by day and its dark by night, framed in charcoal, its value on a tube's dark glass lettered in the phosphor. The boards
are the white room's warm white tiles and the frame's brushed pale grey plastic in a frame of a set's charcoal, screwed
at its corners, and the winners stand on a plain podium of the wingback's white leather."""
from __future__ import annotations

from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import Pix
from . import art as A
from .palette import C, RAMP, step

WALL, DUSK, PLASTIC, GLASS, SHELL = RAMP["wall"], RAMP["dusk"], RAMP["plastic"], RAMP["glass"], RAMP["shell"]
LEATHER, STEEL, SUIT, BRASS = RAMP["leather"], RAMP["steel"], RAMP["suit"], RAMP["brass"]
SIGNAL, FLAME = RAMP["signal"], RAMP["flame"]


# --------------------------------------------------------------------------- the footers
# The heart in BUILT WITH (heart) BY, 7 by 6: a heart drawn on a screen in the phosphor, white-hot at its upper-left
# lobe and dimming to its point.
HEART = [".54.43.", "5654432", "4544332", ".43322.", "..322..", "...2..."]


def heart(p: Pix, x, y, L="base"):
    """The heart, 7 by 6, its top-left at (x, y)."""
    p.sprite(x, y, HEART, {str(i): FLAME[i] for i in range(7)}, 1, L)


def bar(p: Pix, x0, y0, w, h, period=5, L="base"):
    """The graphic scale's bar: a row of little tubes `period` units long, lit in the phosphor and dark by turns, as
    the console's level meter lights, each lit along its top and shaded along its foot."""
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.25 else (1 if f < 0.75 else 2)
        for xx in range(x0, x0 + w):
            lit = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (FLAME[5], FLAME[3], FLAME[1])[band] if lit else (GLASS[5], GLASS[3], GLASS[1])[band], L)


FOOT_RISE = 7     # the rows the console's meter bridge rises above its desk where the cells leave it room
FOOT_RUN = 20     # the fewest columns a meter bridge runs along


def footing(p: Pix, night: bool, after: int = 0):
    """A footer once its words are set: the front edge of the Architect's console along its foot, a brass rail over
    its charcoal face set with a row of keys, a few of them lit in the phosphor, laid over the frame's foot and as
    deep as six rows or, where the lowest word comes down nearer the foot, as shallow as keeps a row clear of it;
    wherever the cells leave the wall free along FOOT_RUN columns or more, the console's meter bridge rising behind
    it, a row of little tubes each showing a level in the phosphor; and, at the rightmost place from column `after` on
    where the cells leave the wall free, a set on the console showing the room itself (see `art.tv`). The desk lies on
    a layer of its own over the frame's foot. By night every tube's light is laid on the plastic near it."""
    w, h = p.w, p.h
    base = p.layers["base"]
    low = max((b[3] for b in p.words), default=0) + 1
    floor = h - 2
    ledge = min(floor - 1, max(floor - 5, low))

    def free(x0, y0, x1, y1):
        """Whether the box from (x0, y0) to (x1, y1) lies on the bare wall, nothing solid drawn on it, two units clear
        of every word."""
        inside = A.EDGE + 1 <= x0 and x1 <= w - A.EDGE - 1 and 4 <= y0
        return inside and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0, x1) for y in range(y0, y1))
    mark = None
    top = ledge - 1 - A.TV_H
    if top >= 4:
        mark = next((x for x in range(w - A.EDGE - 2 - A.TV_W, max(A.EDGE + 1, after), -1)
                     if free(x, top, x + A.TV_W, ledge)), None)
    taken = (mark - 2, mark + A.TV_W + 2) if mark is not None else (0, 0)
    rise = [x not in range(*taken) and free(x, ledge - FOOT_RISE, x + 1, ledge) for x in range(w)]
    x = A.EDGE + 1
    while x < w - A.EDGE - 1:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - A.EDGE - 1) if not rise[i]), w - A.EDGE - 1)
        if b - x >= FOOT_RUN:
            meter_bridge(p, x, b, ledge, night)
        x = b
    band = floor - ledge + 1
    rows = {2: ["rail", "keys"], 3: ["rail", "keys", "edge"], 4: ["rail", "keys", "face", "edge"],
            5: ["rail", "keys", "face", "shade", "edge"]}.get(band, ["rail", "keys", "face", "keys", "shade", "edge"])
    near = [b for b in p.words if b[3] + 1 > ledge]
    L = p.layer("foot", z=0.1)
    k = A._case(night)
    for x in range(A.EDGE, w - A.EDGE):
        for i, kind in enumerate(rows):
            y = ledge + i
            if any(b[0] - 1 <= x < b[2] + 1 and b[1] - 1 <= y < b[3] + 1 for b in near):
                continue
            if kind == "rail":
                c = BRASS[5] if x % 10 else BRASS[6]
            elif kind == "keys":
                cap = FLAME[4] if (x * 7 + i) % 23 == 0 else PLASTIC[5] if not night else PLASTIC[3]
                c = cap if x % 3 else k["c"]
            elif kind == "face":
                c = k["c"]
            elif kind == "shade":
                c = k["s"]
            else:
                c = k["o"]
            p.px(x, y, c, L)
    if mark is not None:
        A.tv(p, mark, top, "architect", night, False)
    A.screenlight(p, night)


def meter_bridge(p: Pix, x0, x1, ledge: int, night: bool):
    """The console's meter bridge from column x0 to x1, standing on its desk at row `ledge`: a charcoal panel lit along
    its top, holding a row of little tubes, each showing a level in the phosphor, the taller the further along."""
    k = A._case(night)
    t = ledge - FOOT_RISE
    for y in range(t, ledge):
        for x in range(x0, x1):
            c = k["L"] if y == t or x == x0 else k["s"] if x == x1 - 1 or y == ledge - 1 else k["c"]
            p.px(x, y, c)
    for i, tx in enumerate(range(x0 + 2, x1 - 5, 6)):
        level = 1 + (i * 5 + x0) % 4
        for y in range(t + 2, ledge - 2):
            for x in range(tx, tx + 4):
                lit = ledge - 2 - y <= level
                glow = FLAME[4] if ledge - 2 - y == level else FLAME[2]
                p.px(x, y, glow if lit and x in (tx + 1, tx + 2) else GLASS[2])
        A.lamp(p, tx + 2, ledge - 4, 6)


# A little set in the corner of a title block's notes, 7 by 6: its pale case, its tube glowing, its stand.
LITTLE = ["ccccccc", "cGgggSc", "cgggggc", "cggggSc", "ccccccc", "..CCC.."]


def footer_mark(p: Pix, x, y, night: bool):
    """A little set in the corner of the closing notes, its tube glowing in the phosphor."""
    k = -1 if night else 0
    p.sprite(x + 3, y - 1, LITTLE, {"c": SHELL[5 + k], "C": SHELL[3 + k], "g": FLAME[2], "G": FLAME[4],
                                    "S": FLAME[1]})


# --------------------------------------------------------------------------- the link buttons
# The sprites at a button's start, 9 by 7: a television with its picture on, the white wingback, the pen and the
# white rabbit. c C the case light and deep, g G the picture, w W the white light and deep, b the brass, s the steel.
ICONS = {
    "tv": ["ccccccccc", "cGgggggGc", "cgGgGgGgc", "cGgggggGc", "ccccccccc", "..C...C..", ".CC...CC."],
    "chair": ["....wwww.", "...wwwwW.", "...wwwwW.", "...wwwwW.", "WwwwwwwW.", "WWWWWWWW.", ".s.....s."],
    "pen": ["........b", ".......sb", "......sC.", ".....cC..", "....cC...", "...cC....", "..bb....."],
    "rabbit": ["..w.w....", "..w.w....", "..www....", ".wwwWw...", ".wwwwwb..", "..WwwW.b.", "..w..w..."],
}
LINK_SPRITES = ("tv", "chair", "pen", "rabbit")


def icon_pal(night: bool, ink=None) -> dict:
    """The sprites' tones on a button, by day and by night: the frame's pale plastic, the phosphor's picture, the
    chair's white leather, the pen's brass and steel."""
    k = -1 if night else 0
    return {"c": SHELL[5 + k], "C": SHELL[3 + k], "g": FLAME[3], "G": FLAME[5], "w": LEATHER[6 + k],
            "W": LEATHER[4 + k], "b": BRASS[5 + k], "s": STEEL[5 + k], "#": ink}


def link_top(p: Pix, x0, x1, y, night: bool):
    """A button finished as a set's case: the vents along its top edge, slots in the plastic every other unit, and its
    face lit along the top and down the left and shaded down the right."""
    fill, edge, _, shade = link_colours(night)
    for x in range(x0 + 1, x1 - 1):
        if x % 3:
            p.px(x, y - 1, PLASTIC[4] if not night else PLASTIC[3])
    lit = PLASTIC[3] if not night else GLASS[5]
    p.hline(1, p.w - 1, y + 1, lit)
    p.vline(1, y + 1, y + 9, lit)
    p.vline(p.w - 2, y + 2, y + 9, shade)


def link_colours(night: bool) -> tuple:
    """A button's face, edge, letters and the shade along its foot: a set's charcoal plastic in a rim of the frame's
    pale grey, its letters the phosphor's green; by night the face is a tube's dark glass in a rim of the charcoal."""
    if night:
        return GLASS[3], PLASTIC[5], FLAME[4], GLASS[0]
    return PLASTIC[2], SHELL[2], FLAME[4], PLASTIC[0]


# --------------------------------------------------------------------------- the badges
def badge_top(p: Pix, w: int, s: dict, night: bool, inside, text_y: int, label_blocks: tuple):
    """A badge as a set's case, kept inside its shape and off its letters: a band of charcoal plastic along its top two
    rows, its vents slotted in it and a power light burning green at its right end, the badge's foot a charcoal edge,
    and its two blocks bevelled as panels, lit along their top and left and shaded along their foot and right, a seam
    of charcoal between the label and the value."""
    h = s["h"]
    text_rows = range(text_y - 1, text_y + (7 if s["font"] == "57" else 5) + 1)

    def ins(x, y):
        return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
    row = h - 2 if (h - 2) % 4 != 2 else h - 3
    first = next((x for x in range(w) if ins(x, row)), 0)
    edge = next((x for x in range(first + 1, w) if ins(x, row) and p.get(x, row) != p.get(first, row)), w)
    if edge == w and p.get(first, row) not in label_blocks:
        edge = 0
    light = max((x for x in range(w) if ins(x, 0) and ins(x, 1)), default=0) - 2
    for y in range(h):
        for x in range(w):
            if not ins(x, y):
                continue
            if y == 0:
                p.px(x, y, PLASTIC[4] if x % 3 else PLASTIC[1])
                continue
            if y == 1:
                p.px(x, y, FLAME[4] if x == light else PLASTIC[2] if x % 3 else PLASTIC[0])
                continue
            if y == h - 1:
                p.px(x, y, PLASTIC[0])
                continue
            c = p.get(x, y)
            try:
                if x == edge and edge:
                    p.px(x, y, PLASTIC[0])
                elif y == 2 and y not in text_rows:
                    p.px(x, y, step(c, 1))
                elif y == h - 2:
                    p.px(x, y, step(c, -1))
                elif not ins(x - 1, y):
                    p.px(x, y, step(c, 1))
                elif not ins(x + 1, y):
                    p.px(x, y, step(c, -1))
            except KeyError:
                pass


def badge_shine(c: str, y: int, h: int) -> str:
    """Plastic's gloss: its top row a step lighter, its foot a step darker."""
    try:
        return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
    except KeyError:
        return c


def badge_label() -> tuple:
    """A static badge's label: charcoal plastic lettered in the frame's pale grey."""
    return PLASTIC[2], SHELL[5]


def badge_gold() -> tuple:
    """A live badge's label: the pen's brass, lettered in the charcoal's darkest."""
    return BRASS[3], PLASTIC[0]


def badge_states() -> dict:
    """The states a live badge shows: the phosphor, brass, red enamel and steel."""
    return {"green": (FLAME[1], C["white"]), "yellow": (BRASS[4], PLASTIC[0]), "red": (SIGNAL[3], C["white"]),
            "slate": (STEEL[2], C["white"])}


def badge_swatches() -> dict:
    """The colours a static badge's value may take, by name: each block lettered to hold 4.5:1 on it."""
    return {"phosphor": (FLAME[1], C["white"], None), "glow": (FLAME[3], GLASS[0], None),
            "glass": (GLASS[4], FLAME[4], None), "charcoal": (PLASTIC[2], SHELL[5], None),
            "shell": (SHELL[3], PLASTIC[0], None), "wall": (WALL[4], PLASTIC[1], None),
            "suit": (SUIT[1], C["white"], None), "steel": (STEEL[3], C["white"], None),
            "brass": (BRASS[4], PLASTIC[0], None), "leather": (LEATHER[5], PLASTIC[1], None),
            "enamel": (SIGNAL[3], C["white"], None), "dusk": (DUSK[6], FLAME[4], None)}


def plate_colours(mode: str) -> dict:
    """A plate: the white room's wall by day and its dark by night, dotted, framed in charcoal plastic, its value on a
    tube's dark glass lettered in the phosphor; a live plate is brass."""
    if mode == "day":
        return dict(paper=WALL[4], dot=WALL[2], frame=PLASTIC[2], block=GLASS[3], ink=PLASTIC[1], letters=FLAME[4])
    if mode == "night":
        return dict(paper=DUSK[4], dot=DUSK[6], frame=PLASTIC[4], block=GLASS[3], ink=C["body_night"],
                    letters=FLAME[4])
    return dict(paper=BRASS[3], dot=BRASS[4], frame=PLASTIC[0], edge=BRASS[1], ink=PLASTIC[0])


# --------------------------------------------------------------------------- the games
def game_squares(night: bool) -> tuple:
    """A board of the white room's floor: squares of its warm white tiles and of the frame's pale grey plastic,
    brushed, each a tone down by night, as every board of the year is dimmer after dark."""
    return Stuff(WALL, 4 if night else 5, "tile"), Stuff(SHELL, 1 if night else 2, "metal")


def game_frame(night: bool) -> tuple:
    """A frame of a set's charcoal plastic, screwed at its corners."""
    return Stuff(PLASTIC, 3), "iron"


def game_podium(night: bool) -> Podium:
    """A podium of the wingback's white leather, its sheen running across it, plain."""
    return Podium(Stuff(LEATHER, 5, "satin"), "plain")
