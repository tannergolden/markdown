# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chateau set's six elements, drawn on the shared pixel canvas: the chateau's materials carried into every chart.

A schematic's cards are menu cards on the banquet's linen in a gilt frame, a ribbon of red velvet stitched in gold down
the edge of each one's icon and a gilt clasp on its lid; its wires are gold cords hung with crystal drops, its groups
bordered in red and gold, and a trophy of two swords crossed behind the gilded shield hangs in a free corner. The
instruments stand each week's commits as a marble column under a gilt capital, crown the busiest with a gold crown,
bend a beaded gilt bezel over the dial on a gilt boss, wrap the bytes by file type in the chateau's fabrics (red
velvet figured in gold, gold brocade, champagne silk, wine velvet sewn with gold and veined marble), and cut every
count into a marble tile in a gilt frame. The milestones run along a red velvet rope between gilt posts, every
release a candle in a gilt candlestick burning green on it, a big one a candelabrum and one still to come a candle not
yet lit, and the mantel clock stands at today. The roster hangs each contributor's cameo in an oval gilt frame, a
bot's a close helm, over a bar of red velvet in gilt; the certificate's seal is ringed with a rosette of round gilt
petals, the gold lily at its foot; and the placard is a card of champagne silk in the gilded frame, a carved rosette
at each of its top corners and a goblet of wine beside its title."""
from __future__ import annotations

import math

from ...holidays.pixel import Pix, sphere, tube
from . import art as A
from .palette import C, RAMP, step

GOLD, CARPET, WINE, SILK = RAMP["gold"], RAMP["carpet"], RAMP["wine"], RAMP["silk"]
MARBLE, VEIN, LINEN, STEEL = RAMP["marble"], RAMP["vein"], RAMP["linen"], RAMP["steel"]
CRYSTAL, FLAME, CLOTH = RAMP["crystal"], RAMP["flame"], RAMP["cloth"]
# The fields a contributor's cameo is enamelled in, by turns.
CAMEOS = ("carpet", "wine", "steel", "cocoa")


def card_bevel(night: bool) -> tuple:
    """A card's bevel: gilt lit along its top and left and shaded along its foot and right."""
    return (GOLD[4], GOLD[1]) if night else (GOLD[5], GOLD[2])


def node_deco(p: Pix, night: bool, x, y, w, h, seed, lid):
    """A card as a menu card in a gilt frame: a ribbon of red velvet down the edge of its icon's cell, stitched in gold;
    a gilt bead at each corner; and on its lid, every other card, a gilt clasp."""
    for yy in range(y + 1, y + h - 1):
        p.px(x + 10, yy, A.tone("carpet", 5, night))
        p.px(x + 11, yy, A._g(5, night) if (yy - y) % 3 == 1 else A.tone("carpet", 3, night))
        p.px(x + 12, yy, A.tone("carpet", 2, night))
    for (cx, cy) in ((x, y), (x + w - 2, y), (x, y + h - 2), (x + w - 2, y + h - 2)):
        p.px(cx, cy, A._g(6, night))
        p.px(cx + 1, cy, A._g(4, night))
        p.px(cx, cy + 1, A._g(4, night))
        p.px(cx + 1, cy + 1, A._g(2, night))
    if lid and seed % 2 == 0:
        mx = x + 13 + (w - 13) // 2
        p.hline(mx - 2, mx + 3, y - 1, A._g(5, night))
        p.hline(mx - 1, mx + 2, y - 2, A._g(4, night))
        p.px(mx, y - 3, A._g(6, night))


def wire_ink(night: bool) -> str:
    """A wire is a gold cord."""
    return GOLD[4] if night else GOLD[3]


def wire_lights(p: Pix, cells, night: bool, seed):
    """Crystal drops hung on the cord every twelfth unit, under a level run and beside an upright one, glinting in
    the candles' green by night."""
    for i, (x, y, d) in enumerate(cells[5:-7]):
        if i % 12:
            continue
        key = ("drop", d, night)
        if key not in p.syms:
            top, mid, low = (FLAME[4], CRYSTAL[3], CRYSTAL[1]) if night else (C["white"], CRYSTAL[4], CRYSTAL[2])
            cells_ = ({(0, 1): mid, (0, 2): top, (-1, 2): mid, (1, 2): low, (0, 3): low} if d == "h" else
                      {(-1, 0): mid, (-2, 0): top, (-2, -1): mid, (-2, 1): low, (-3, 0): low})
            p.symbol(key, cells_)
        p.use(key, x, y)


def dashes(night: bool) -> list:
    """A group's dashed border, red velvet and gilt by turns."""
    return [CARPET[4] if night else CARPET[3], GOLD[4] if night else GOLD[3]]


def ornament(kind: str, p, x, y, night: bool) -> tuple:
    """Two rapiers crossed behind the gilded shield in a free corner of the schematic, 26 by 30."""
    if kind == "schematic":
        if p is not None:
            A.trophy(p, x + 13, y + 15, night)
        return (26, 30)
    return (0, 0)


def hist_bar(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a column of veined marble under a gilt capital, on a gilt base, lit down its left."""
    for yy in range(base - v, base):
        for xx in range(bx, bx + bw):
            i = xx - bx
            if yy < base - v + 2 and v > 4:
                c = A._g(5 if yy == base - v else 3, night)
            elif yy >= base - 1:
                c = A._g(4, night)
            elif i == 0:
                c = A.tone("marble", 6, night)
            elif i == bw - 1:
                c = A.tone("marble", 2, night)
            elif (xx * 3 + yy * 5) % 17 == 0:
                c = A.tone("vein", 3, night)
            else:
                c = A.tone("marble", 5 if i < bw // 2 else 4, night)
            p.px(xx, yy, c)


# A small gold crown, 5 by 4, a ruby on its band.
CROWN = ["#.#.#", "#####", "#r#r#", "#####"]


def peak_mark(p: Pix, x, y, night: bool):
    """A gold crown over the busiest week's count."""
    p.sprite(x, y, CROWN, {"#": A._g(5, night), "r": CARPET[4]})
    p.px(x + 4, y + 3, A._g(2, night))


def dial_ring(p: Pix, arc, night: bool):
    """A gilt bezel bent over the dial, beaded, lit along its upper left."""
    def colour(s, o, lam, x, y):
        if int(s) % 5 == 2 and abs(o) < 0.5:
            return A._g(6, night)
        return A._g(max(1, min(5, round(1.5 + 3.5 * lam))), night)
    tube(p, arc, 2.6, colour, outline=GOLD[0])


def dial_tick(p: Pix, x, y, night: bool):
    p.px(x, y, CARPET[4])
    p.px(x + 1, y + 1, CARPET[1])


def dial_hub(p: Pix, cx, cy, night: bool):
    """A gilt boss on a ring of red velvet."""
    for i, xx in enumerate(range(cx - 4, cx + 5)):
        p.px(xx, cy + 2, A.tone("carpet", 4 if i < 3 else 3 if i < 7 else 1, night))
    sphere(p, cx + 0.5, cy - 0.5, 3.0, GOLD, lo=1, hi=6)


def material(i: int, xx, yy, y0, y1, lift, night: bool) -> str:
    """The chateau's fabrics by turns: red velvet figured with gold lilies, gold brocade woven on the slant,
    champagne silk in stripes, wine velvet sewn with gold, and veined marble."""
    kind = i % 5
    if kind == 0:
        c = GOLD[4] if (xx % 6, (yy - y0) % 6) in ((2, 2), (3, 3), (1, 3), (2, 4)) else CARPET[3]
    elif kind == 1:
        c = GOLD[2] if (xx + yy) % 4 == 0 else GOLD[4]
    elif kind == 2:
        c = SILK[3] if xx % 4 < 2 else SILK[5]
    elif kind == 3:
        c = GOLD[5] if (xx % 5 == 2 and (yy - y0) % 4 == 1) else WINE[5]
    else:
        c = VEIN[3] if (xx * 3 + yy * 7) % 11 == 0 else MARBLE[5]
    if night:
        c = step(c, -1)
    try:
        return step(c, lift)
    except KeyError:
        return c


def counter_cell(q: Pix, ox, oy, night: bool):
    """A tile of white marble 11 by 15 in a frame of gilt, a numeral cut into it: the frame lit along its top and left
    and shaded along its foot and right, the marble shaded at its foot."""
    for yy in range(15):
        for xx in range(11):
            if xx in (0, 10) or yy in (0, 14):
                c = A._g(5 if (xx == 0 or yy == 0) else 2, night)
            elif yy == 13 or xx == 9:
                c = A.tone("marble", 4, night)
            else:
                c = A.tone("marble", 6, night)
            q.px(ox + xx, oy + yy, c)


def counter_ink(night: bool, dim: bool) -> str:
    """A numeral cut into the marble in the wine's darkest; a leading nought cut shallower in grey."""
    if night:
        return MARBLE[1] if dim else WINE[0]
    return MARBLE[2] if dim else WINE[1]


def timeline_line(p: Pix, x0, x1, y, night: bool):
    """A rope of red velvet the releases stand on up to today, hung between gilt posts every so often."""
    if x1 - x0 < 3:
        return

    def colour(s, o, lam, x, yy):
        return A.tone("carpet", max(1, min(6, round(1.5 + 4 * lam))), night)
    tube(p, [(x0, y + 1.5), (x1, y + 1.5)], 2.0, colour, outline=A.tone("carpet", 0, night))
    for x in range(x0 + 26, x1 - 4, 52):
        post(p, x, y, night)


def post(p: Pix, x, y, night: bool):
    """A gilt stanchion post the rope is hooked to, a ball on its top."""
    for yy in range(y - 2, y + 5):
        p.px(x, yy, A._g(5, night))
        p.px(x + 1, yy, A._g(3, night))
    p.hline(x - 1, x + 3, y + 5, A._g(2, night))
    p.px(x, y - 3, A._g(6, night))
    p.px(x + 1, y - 3, A._g(4, night))


def release(p: Pix, x, gy, kind, night: bool, i=0):
    """A release as a candle in a gilt candlestick standing on the rope at x, its wax lit down its left and shaded
    down its right and its flame burning green: a big release a three-branched candelabrum, a patch a short candle,
    one still to come a candle not yet lit, its wick dark, and the repository's founding the gilded shield."""
    if kind == "made":
        A.shield(p, x, gy - 15, night)
        return
    if kind == "big":
        p.hline(x - 3, x + 4, gy, A._g(4, night))
        p.px(x, gy - 1, A._g(5, night))
        p.hline(x - 3, x + 4, gy - 2, A._g(4, night))
        for j, (cx, h) in enumerate(((x - 3, 3), (x, 5), (x + 3, 3))):
            A.candle(p, cx, gy - 3, h, night, False, phase=j)
        return
    wax = {"major": 4, "minor": 2, "next": 4}.get(kind, 4)
    p.hline(x - 1, x + 2, gy, A._g(3, night))                  # its foot on the rope
    p.px(x, gy - 1, A._g(5, night))                             # its stem
    p.hline(x - 2, x + 3, gy - 2, A._g(4, night))              # its drip pan, lit at its left
    p.px(x - 2, gy - 2, A._g(6, night))
    p.px(x + 2, gy - 2, A._g(2, night))
    top = gy - 2 - wax
    for yy in range(top, gy - 2):
        if kind == "next":
            p.px(x, yy, A.tone("linen", 3, night))
            p.px(x + 1, yy, A.tone("linen", 2, night))
        else:
            p.px(x, yy, A.tone("linen", 6 if yy == top else 5, night))
            p.px(x + 1, yy, A.tone("linen", 3, night))
    if kind == "next":
        p.px(x, top - 1, A.tone("wood", 1, night))
    else:
        A.flame(p, x, top - 1, False)


def today_mark(p: Pix, x, y, night: bool):
    """The mantel clock standing at today's end of the rope."""
    A._clock(p, x, y - 1, night)


def avatar(p: Pix, cx, cy, i, person, night: bool):
    """A contributor's cameo: their initials on a field of enamel in an oval gilt frame, the fields red velvet, wine,
    steel and chocolate by turns; a bot is a close helm of steel in the same frame."""
    bot = not person.get("initials")
    name = CAMEOS[i % len(CAMEOS)]
    for yy in range(cy - 8, cy + 9):
        for xx in range(cx - 7, cx + 8):
            d = math.hypot((xx + 0.5 - cx) / 7.5, (yy + 0.5 - cy) / 8.5)
            if d > 1:
                continue
            if d > 0.82:
                lit = (xx - cx) + (yy - cy) < 0
                c = A._g(5 if lit else 2, night)
            elif bot:
                c = A.tone("crystal", 5, night) if yy < cy else A.tone("crystal", 4, night)
            else:
                c = A.tone(name, 4 if yy < cy - 2 else 3, night) if name != "steel" else A.tone("steel", 3, night)
            p.px(xx, yy, c)
    if bot:
        helm = [".hhh.", "hhhhH", "hdddH", "hhhhH", "hdhdH", ".hhH."]
        p.sprite(cx - 2, cy - 3, helm, {"h": A.tone("steel", 6, night), "H": A.tone("steel", 4, night),
                                        "d": CLOTH[0]})
        return
    ini = str(person["initials"])[:2]
    p.text(cx - 3, cy - 2, ini, GOLD[6], "35", shadow=GOLD[0])


def commit_bar(p: Pix, x, y, w, fill, night: bool):
    """A contributor's share: red velvet filling a gilt frame."""
    p.box(x, y, w + 2, 4, A._g(3, night))
    p.hline(x + 1, x + 1 + fill, y + 1, A.tone("carpet", 5, night))
    p.hline(x + 1, x + 1 + fill, y + 2, A.tone("carpet", 3, night))


def rosette(p: Pix, cx, cy, r0, r1, n, night: bool):
    """A gilt rosette round the seal: `n` round petals in a ring from radius r0 to r1, each domed and lit on its upper
    left and rimmed in the gilt's darkest tone, on a band of gilt along the disc's edge."""
    rp = (r1 - r0) / 2 + 0.3
    rc = r0 + rp - 0.2
    petals = [(cx + rc * math.cos(2 * math.pi * (k + 0.5) / n), cy + rc * math.sin(2 * math.pi * (k + 0.5) / n))
              for k in range(n)]
    for y in range(math.floor(cy - r1 - 1), math.ceil(cy + r1 + 2)):
        for x in range(math.floor(cx - r1 - 1), math.ceil(cx + r1 + 2)):
            fx, fy = x + 0.5, y + 0.5
            d = math.hypot(fx - cx, fy - cy)
            if d < r0 - 0.5 or d > r1 + 0.6:
                continue
            qx, qy = min(petals, key=lambda q: (q[0] - fx) ** 2 + (q[1] - fy) ** 2)
            dp = math.hypot(fx - qx, fy - qy)
            if dp <= rp:
                if dp > rp - 1:
                    c = A._g(1, night)
                else:
                    lit = -((fx - qx) * 0.63 + (fy - qy) * 0.78) / rp
                    c = A._g(max(2, min(6, round(4 + 2.2 * lit))), night)
            elif d <= r0 + 1.2:
                c = A._g(2, night)
            else:
                continue
            p.px(x, y, c)


def seal_mark(p: Pix, x, y, night: bool):
    """The gold lily at the seal's foot."""
    for j, row in enumerate(A.LILY[:7]):
        for i, ch in enumerate(row):
            if ch == "#":
                p.px(x + 4 + i, y + j, A._g(5 if i < 3 else 3, night))


def placard_board(p: Pix, night: bool, design):
    """The placard: a card of champagne silk, or wine-dark silk by night, in the gilded frame, a carved rosette at each
    of its top corners."""
    design.paper(p, night, uid="pl")
    design.frame(p, night)
    for x in (0, p.w - 9):
        A._rosette(p, x, 0, 9, night)


def placard_mark(p: Pix, x, y, night: bool):
    """A goblet of red wine beside the placard's title."""
    A.section_mark(p, x + 4, y - 2, night)
