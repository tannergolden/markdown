# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chateau set's smaller surfaces, drawn on the shared pixel canvas: the footers' footing, emblem, heart and graphic
scale, the link buttons, the badges and plates, and the stuffs of its boards and its podium.

Every footer stands on the red carpet's border under a gilt rod, laid along its foot over the frame's, a balustrade of
marble balusters under a gilt-capped rail rising behind it wherever the cells leave the wall free, and a title block
hangs the chateau's emblem after its last cell, the gilded shield charged with the gold lily between two sconces; a gilt
candlestick burns in the corner of its notes. The heart is a ruby of red velvet set in gold; the graphic scale's bar is
gilt and red velvet by turns, lit along its top and shaded along its foot. A link button is red velvet in a rim of gilt,
its letters gold, and the sprite at its start is one of the banquet's things: the chandelier, a goblet of wine, the
candelabrum with its three green flames, and two swords crossed. A badge's label is wine-dark velvet lettered in gold, a
live badge's label is gilt, and a plate is champagne silk by day and wine-dark silk by night, framed in gilt, its value
on red velvet. The boards are polished white marble and mahogany parquet in a frame of gilt beads, and the winners stand
on a crenellated podium of veined white marble."""
from __future__ import annotations

from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import Pix
from . import art as A
from .palette import C, RAMP, step

GOLD, CARPET, WINE, SILK = RAMP["gold"], RAMP["carpet"], RAMP["wine"], RAMP["silk"]
CRYSTAL, LINEN, STEEL, FLAME = RAMP["crystal"], RAMP["linen"], RAMP["steel"], RAMP["flame"]
MARBLE, VEIN = RAMP["marble"], RAMP["vein"]


# --------------------------------------------------------------------------- the footers
# The heart in BUILT WITH (heart) BY, 7 by 6: a ruby of red velvet, lit on its upper-left lobe, a glint of gold on it.
HEART = [".54.43.", "5g44432", "4443321", ".33321.", "..321..", "...1..."]


def heart(p: Pix, x, y, L="base"):
    """The heart, 7 by 6, its top-left at (x, y)."""
    pal = {str(i): CARPET[i] for i in range(7)}
    pal["g"] = GOLD[6]
    p.sprite(x, y, HEART, pal, 1, L)


def bar(p: Pix, x0, y0, w, h, period=5, L="base"):
    """The graphic scale's bar: gilt and red velvet by turns, `period` units each, lit along its top and shaded along
    its foot."""
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.25 else (1 if f < 0.75 else 2)
        for xx in range(x0, x0 + w):
            gilt = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (GOLD[5], GOLD[4], GOLD[2])[band] if gilt else (CARPET[4], CARPET[3], CARPET[1])[band], L)


FOOT_RISE = 8     # the fewest rows a balustrade rises above the carpet, where the cells leave it room
FOOT_MOST = 15    # and the most
FOOT_RUN = 20     # the fewest columns a balustrade runs along
SCONCE_W = 9      # a sconce's width, its candles' flames included


def footing(p: Pix, night: bool, after: int = 0):
    """A footer once its words are set: the foot of the chateau's wall along its foot, the red carpet's border under
    a gilt rod on the marble floor, laid over the frame's foot down to its gilt edge and as deep as six rows or, where
    the lowest word comes down nearer the foot, as shallow as keeps a row clear of it; wherever the cells leave the wall
    free along FOOT_RUN columns or more, a balustrade of marble balusters under a gilt-capped rail rising behind it as
    tall as they leave it, the ruled lines between the cells standing on the carpet; and, at the rightmost place from
    column `after` on where the cells leave the wall free, the chateau's emblem hung on the wall (see `emblem`). The
    carpet lies on a layer of its own over the frame's foot. By night the sconces' green light is laid on the gilt, the
    marble and the velvet near them."""
    w, h = p.w, p.h
    base = p.layers["base"]
    low = max((b[3] for b in p.words), default=0) + 1
    floor = h - 2
    ledge = min(floor - 1, max(floor - 5, low))

    def free(x0, y0, x1, y1):
        """Whether the box from (x0, y0) to (x1, y1) lies on the bare silk, nothing solid drawn on it, two units clear
        of every word."""
        inside = A.EDGE + 1 <= x0 and x1 <= w - A.EDGE - 1 and 4 <= y0
        return inside and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0, x1) for y in range(y0, y1))
    mark = emblem_spot(p, ledge, after, free)
    taken = (mark[0] - 2, mark[0] + mark[2] + 2) if mark else (0, 0)
    rise = [x not in range(*taken) and free(x, ledge - FOOT_RISE, x + 1, ledge) for x in range(w)]
    runs, x = [], A.EDGE + 1
    while x < w - A.EDGE - 1:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - A.EDGE - 1) if not rise[i]), w - A.EDGE - 1)
        if b - x >= FOOT_RUN:
            tall = next(r for r in range(FOOT_MOST, FOOT_RISE - 1, -1)
                        if r == FOOT_RISE or free(x, ledge - r, b, ledge))
            runs.append((x, b, tall))
        x = b
    for a, b, tall in runs:
        balustrade(p, a, b, ledge, tall, night)
    band = floor - ledge + 1
    rows = {2: ["rod", "carpet"], 3: ["rod", "carpet", "edge"], 4: ["rod", "carpet", "border", "edge"],
            5: ["rod", "carpet", "border", "floor", "edge"]}
    rows = rows.get(band, ["rod", "carpet", "border", "deep", "floor", "edge"])
    near = [b for b in p.words if b[3] + 1 > ledge]
    L = p.layer("foot", z=0.1)
    for x in range(A.EDGE, w - A.EDGE):
        for i, kind in enumerate(rows):
            if any(b[0] - 1 <= x < b[2] + 1 and b[1] - 1 <= ledge + i < b[3] + 1 for b in near):
                continue
            if kind == "rod":
                c = A._g(6 if x % 12 == 0 else 5, night)
            elif kind == "carpet":
                c = A.tone("carpet", 4, night)
            elif kind == "border":
                c = A._g(4, night) if x % 4 == 1 else A.tone("carpet", 2, night)
            elif kind == "deep":
                c = A.tone("carpet", 1, night)
            elif kind == "edge":
                c = A._g(2, night)
            else:
                c = A.tone("marble", 2 if (x * 7) % 11 == 0 else 4, night)
            p.px(x, ledge + i, c, L)
    if mark:
        emblem(p, mark, night)
    A.candlelight(p, night)


def balustrade(p: Pix, x0, x1, ledge: int, tall: int, night: bool):
    """A balustrade from column x0 to x1, `tall` rows high, standing on the carpet's rod at row `ledge`: a rail of
    marble capped in gilt, balusters every four columns under it, each swelling from a neck to a belly and narrowing to
    a foot, lit down its left, a plinth of marble along its foot, and its ends squared in pedestals of marble."""
    t = ledge - tall
    lit, mid, shade = (A.tone("marble", i, night) for i in (6, 4, 2))
    for x in range(x0, x1):
        p.px(x, t, A._g(5, night))
        p.px(x, t + 1, A.tone("marble", 5, night))
        p.px(x, t + 2, shade)
        p.px(x, ledge - 1, A.tone("marble", 3, night))
    bh = ledge - 1 - (t + 3)
    for bx in range(x0 + 4, x1 - 5, 4):
        for j in range(bh):
            y = t + 3 + j
            if j == 0 or j == bh - 2:
                p.px(bx + 1, y, mid)
            else:
                p.px(bx, y, lit)
                p.px(bx + 1, y, mid)
                p.px(bx + 2, y, shade)
    for px in (x0, x1 - 3):
        for y in range(t, ledge):
            p.px(px, y, lit)
            p.px(px + 1, y, mid)
            p.px(px + 2, y, shade)
        p.hline(px, px + 3, t, A._g(6, night))


def emblem_spot(p: Pix, ledge: int, after: int, free) -> tuple | None:
    """The rightmost place from column `after` on where the chateau's emblem hangs free over the footing's ledge, as
    (x, top, width, sconces): with its two sconces where there is room for them and the shield alone where less."""
    h = len(A.SHIELD)
    for sconces in (True, False):
        mw = len(A.SHIELD[0]) + (2 * (SCONCE_W + 2) if sconces else 0)
        top = ledge - 1 - h
        if top < 4:
            return None
        for x in range(p.w - A.EDGE - 2 - mw, max(A.EDGE + 1, after), -1):
            if free(x, top, x + mw, ledge):
                return (x, top, mw, sconces)
    return None


def emblem(p: Pix, mark: tuple, night: bool):
    """The chateau's emblem hung on the wall at `mark` (see `emblem_spot`): the gilded shield charged with the gold
    lily, a sconce burning on either side of it where there is room."""
    x, top, mw, sconces = mark
    sw = len(A.SHIELD[0])
    sx = x + (SCONCE_W + 2 if sconces else 0)
    A.shield(p, sx + sw // 2, top, night)
    if sconces:
        for i, cx in enumerate((x + SCONCE_W // 2, x + mw - 1 - SCONCE_W // 2)):
            A.sconce(p, cx, top + 6, night, False, phase=i)


# The ornament in the corner of a title block's notes, 5 by 10: a candlestick of gilt, its candle burning green.
CANDLESTICK = ["..f..", "..F..", "..w..", "..w..", "..W..", ".gGh.", "..G..", "..g..", ".gGh.", "gGGhh"]


def footer_mark(p: Pix, x, y, night: bool):
    """A candlestick of gilt in the corner of the closing notes, its candle burning on the hand's phosphor."""
    pal = {"f": FLAME[4], "F": FLAME[6], "w": A.tone("linen", 6, night), "W": A.tone("linen", 4, night),
           "g": A._g(5, night), "G": A._g(4, night), "h": A._g(2, night)}
    p.sprite(x + 4, y - 2, CANDLESTICK, pal)


# --------------------------------------------------------------------------- the link buttons
# The sprites at a button's start, 9 by 7: the chandelier, a goblet of wine, the candelabrum and two swords crossed.
# g G the gilt light and deep, k K the crystal, f a green flame, r R the wine, s S the steel, h the hilts.
ICONS = {
    "chandelier": ["f..fgf..f", "g..gGg..g", "gggGGGggg", ".gGGGGGg.", "..kgggk..", ".k.k.k.k.", "..k.K.k.."],
    "goblet": ["..ggggg..", "..rRRRr..", "..grrrg..", "...gGg...", "....g....", "....G....", "..ggGgg.."],
    "candelabrum": ["f...f...f", "g...g...g", "gg.ggg.gg", ".ggGgGgg.", "....g....", "....G....", "..ggGgg.."],
    "swords": ["s.......s", ".s.....s.", "..s...s..", "...sSs...", "...hSh...", "..h...h..", ".h.....h."],
}
LINK_SPRITES = ("chandelier", "goblet", "candelabrum", "swords")


def icon_pal(night: bool, ink=None) -> dict:
    """The sprites' tones on a button, by day and by night: the gilt, the crystal, the wine, the steel and the
    candles' green flame."""
    k = -1 if night else 0
    return {"g": GOLD[5 + k], "G": GOLD[3 + k], "k": CRYSTAL[6 + k], "K": CRYSTAL[4 + k], "f": FLAME[4],
            "r": CARPET[4 + k], "R": CARPET[3 + k], "s": STEEL[6 + k], "S": STEEL[4 + k], "h": GOLD[4 + k],
            "#": ink}


def link_top(p: Pix, x0, x1, y, night: bool):
    """A button finished as a panel of velvet in a gilt frame: a string of gilt beads along its top edge, every third
    a little brighter, and its velvet lit along the top and down the left and shaded down the right."""
    fill, edge, _, shade = link_colours(night)
    for x in range(x0, x1):
        if x % 2 == 0:
            p.px(x, y - 1, GOLD[5 if x % 6 == 0 else 4] if not night else GOLD[4 if x % 6 == 0 else 3])
    lit = CARPET[2] if not night else WINE[4]
    p.hline(1, p.w - 1, y + 1, lit)
    p.vline(1, y + 1, y + 9, lit)
    p.vline(p.w - 2, y + 2, y + 9, shade)


def link_colours(night: bool) -> tuple:
    """A button's face, edge, letters and the shade along its foot: red velvet in a rim of gilt, its letters gold;
    by night the velvet deepens to wine."""
    if night:
        return WINE[3], GOLD[3], GOLD[5], WINE[0]
    return CARPET[1], GOLD[2], GOLD[5], CARPET[0]


# --------------------------------------------------------------------------- the badges
def badge_top(p: Pix, w: int, s: dict, night: bool, inside, text_y: int, label_blocks: tuple):
    """A badge in a gilt frame, kept inside its shape and off its letters: a string of gilt beads along its top two
    rows, every fourth a little brighter over the frame's dark gilt, the badge's foot a gilt edge in shadow, and its
    two blocks bevelled as panels, lit along their top and left and shaded along their foot and right, a seam of gilt
    between the label and the value."""
    h = s["h"]
    text_rows = range(text_y - 1, text_y + (7 if s["font"] == "57" else 5) + 1)

    def ins(x, y):
        return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
    row = h - 2 if (h - 2) % 4 != 2 else h - 3
    first = next((x for x in range(w) if ins(x, row)), 0)
    edge = next((x for x in range(first + 1, w) if ins(x, row) and p.get(x, row) != p.get(first, row)), w)
    if edge == w and p.get(first, row) not in label_blocks:
        edge = 0
    for y in range(h):
        for x in range(w):
            if not ins(x, y):
                continue
            if y == 0:
                p.px(x, y, GOLD[5] if x % 4 == 1 else GOLD[3] if x % 2 else GOLD[1])
                continue
            if y == 1:
                p.px(x, y, GOLD[2] if x % 2 else GOLD[1])
                continue
            if y == h - 1:
                p.px(x, y, GOLD[1])
                continue
            c = p.get(x, y)
            try:
                if x == edge and edge:
                    p.px(x, y, GOLD[3])
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
    """A static badge's label: wine-dark velvet lettered in gold."""
    return WINE[2], GOLD[5]


def badge_gold() -> tuple:
    """A live badge's label: gilt, lettered in the wine's darkest."""
    return GOLD[3], WINE[0]


def badge_states() -> dict:
    """The states a live badge shows: the candles' green, gilt, red velvet and steel."""
    return {"green": (FLAME[1], C["white"]), "yellow": (GOLD[4], WINE[0]), "red": (CARPET[3], C["white"]),
            "slate": (STEEL[2], C["white"])}


def badge_swatches() -> dict:
    """The colours a static badge's value may take, by name: each block lettered to hold 4.5:1 on it."""
    W, CO, M, CL = RAMP["wood"], RAMP["cocoa"], RAMP["marble"], RAMP["cloth"]
    return {"velvet": (CARPET[3], C["white"], None), "ruby": (CARPET[1], GOLD[5], None),
            "gilt": (GOLD[4], WINE[0], None), "champagne": (SILK[4], WINE[1], None),
            "wine": (WINE[4], GOLD[5], None), "linen": (LINEN[6], WINE[1], None),
            "marble": (M[3], WINE[0], None), "steel": (STEEL[2], C["white"], None),
            "crystal": (CRYSTAL[1], C["white"], None), "cocoa": (CO[3], GOLD[6], None),
            "mahogany": (W[3], GOLD[6], None), "sable": (CL[2], GOLD[5], None),
            "phosphor": (FLAME[1], C["white"], None)}


def plate_colours(mode: str) -> dict:
    """A plate: champagne silk by day and wine-dark silk by night, a lily dotted on it, framed in gilt, its value on
    red velvet lettered in gold; a live plate is gilt."""
    if mode == "day":
        return dict(paper=SILK[4], dot=SILK[2], frame=GOLD[2], block=CARPET[2], ink=WINE[1], letters=GOLD[5])
    if mode == "night":
        return dict(paper=WINE[2], dot=WINE[5], frame=GOLD[3], block=CARPET[2], ink=C["body_night"], letters=GOLD[5])
    return dict(paper=GOLD[3], dot=GOLD[4], frame=WINE[0], edge=GOLD[1], ink=WINE[0])


# --------------------------------------------------------------------------- the games
def game_squares(night: bool) -> tuple:
    """A board of the chateau's floor: squares of polished white marble with a sheen running across them and of
    mahogany laid as parquet, each a tone down by night, as every board of the year is dimmer after dark."""
    return Stuff(MARBLE, 4 if night else 5, "satin"), Stuff(RAMP["wood"], 3 if night else 4, "wood")


def game_frame(night: bool) -> tuple:
    """A frame of gilt with a row of beads."""
    return Stuff(GOLD, 3), "gilt"


def game_podium(night: bool) -> Podium:
    """A podium of veined white marble, crenellated as the chateau's towers are."""
    return Podium(Stuff(MARBLE, 4, "stone"), "crenels")
