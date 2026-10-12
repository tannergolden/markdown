# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Connect Four sheet's layout: its frame, and what its panel counts, inside the sheet every game shares.

The frame stands where chess's board does, as wide, drawn in elevation: seven columns numbered under it between its
legs, six rows numbered up its left side, two legs on the ground. As the file opens the last disc is held over its
column, an arrow marking where it goes in, falls down it behind the plate, glimpsed through each hole it passes, and
lands with a bounce, its column's number set on a block and its hole ringed; a won game's four are ringed one after
another and joined by a line. In place of chess's taken pieces the panel counts each side's discs left, its rack
emptying as the frame fills. Nothing on the sheet helps a player choose: no column a side could connect four down
next, and no call to block. The house always drops the White discs and GitHub the Black, and every word on the sheet
says so: WHITE and BLACK, the house's White first.
"""
from __future__ import annotations

import sys

from ...lettering import f1, fx
from ..games import sheet as S
from ..games.sides import HOUSE, other
from . import motion as M
from .game import COLOUR, COLS, EACH, KIND, ROWS, material_of  # noqa: F401  (KIND: the sheet's stamp)
from .shapes import HOLE, LEG, MARGIN

GAP = 8             # what keeps a label off its tray, chess's
RACK = 86           # where a rack starts: past its widest label, BLACK · GITHUB, in the standard theme's
                    # letters and a gap, so the label is never set smaller, in any theme

LABEL = "connect four"
TOP = {"wide": 42, "narrow": 36}     # room over the frame for the disc held over its column


def geometry(x0, y0, n, small):
    """Where the frame stands in the square chess's board fills: its pitch, its plate, its legs and the ground."""
    p = 46 if not small else 37
    m = MARGIN * p
    w, h = COLS * p + 2 * m, ROWS * p + 2 * m
    fx0 = x0 + (n - w) / 2
    fy0 = y0 + TOP["narrow" if small else "wide"]
    lh = LEG * p
    lw = m * 1.3                     # the legs stand under the frame's ends, clear of the columns' numbers
    legs = [(fx0 + 1, lw, lh), (fx0 + w - 1 - lw, lw, lh)]
    return {"p": p, "m": m, "x": fx0, "y": fy0, "w": w, "h": h, "legs": legs, "ground": fy0 + h + lh}


def centre(g, col, row) -> tuple[float, float]:
    return g["x"] + g["m"] + (col - .5) * g["p"], g["y"] + g["m"] + (ROWS - row + .5) * g["p"]


# --------------------------------------------------------------------------- the sheet's questions
def band_mark(x, y, size, paper, block="") -> str:
    """The band's mark: a piece of the frame, four holes, three of them holding discs."""
    k = size / 20
    return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(k, 4)})"><rect x="1.6" y="2.6" width="16.8" '
            f'height="14.8" rx="2.2" fill="none" stroke="{paper}" stroke-width="1.5"/>'
            f'<circle cx="6.6" cy="7.4" r="2.3" fill="none" stroke="{paper}" stroke-width="1.2"/>'
            f'<circle cx="13.4" cy="7.4" r="2.9" fill="{paper}"/><circle cx="6.6" cy="12.6" r="2.9" fill="{paper}"/>'
            f'<circle cx="13.4" cy="12.6" r="2.9" fill="{paper}"/></g>')


def room(x0, y0, n) -> tuple:
    return (x0 - 2, y0 - 2, n + 10, n + 10)


def height(n, small=False) -> float:
    return geometry(0, 0, n, small)["ground"] + 8


def side_name(side, st) -> str:
    return COLOUR[side]


def first(st) -> str:
    """Before the first disc, which colour drops first: the opener's, White for the house and Black for GitHub."""
    return f"{COLOUR[st['opens']]} drops first"


def medallion(cv, sk, st, cx, cy, r, side) -> str:
    """A side's medallion, holding a disc of its own: White for the house, Black for GitHub."""
    mat = material_of(side)
    return sk.medal(cv, cx, cy, r, mat) + sk.disc(cv, mat, cx, cy, 0, r=r * .72)


def glyph(cv, sk, st, side, x, base, size) -> tuple[str, float]:
    """The disc a move is dropped with, set before its column's number: the notation names the column, the disc
    whose it is. Returns the disc and the room it takes."""
    r = size * .3
    cy = base - sk.cap(size) / 2
    return sk.disc(cv, material_of(side), x + r + .5, cy, 0, r=r), glyph_width(size)


def glyph_width(size) -> float:
    """The room a move's disc takes before its column's number, at `size`."""
    return 2 * size * .3 + size * .22


# --------------------------------------------------------------------------- the frame
def board(cv, sk, st, x0, y0, n, *, small=False) -> None:
    g = geometry(x0, y0, n, small)
    p = g["p"]
    rh = HOLE * p
    last = st["last"]
    holes = [centre(g, col, row) for row in range(ROWS, 0, -1) for col in range(1, COLS + 1)]
    empty = [centre(g, col, row) for row in range(ROWS, 0, -1) for col in range(1, COLS + 1)
             if (col, row) not in st["board"]]
    sk.frame_shadow(cv, g["x"], g["y"], g["w"], g["h"], g["legs"])
    sk.legs(cv, g["legs"], g["y"] + g["h"] - 2)
    sk.ground(cv, g["x"] - p * .3, g["x"] + g["w"] + p * .3, g["ground"])
    # the discs, behind the plate: the last one held over its column, let go, falling
    discs, land = [], M.LET_GO
    for (col, row), v in sorted(st["board"].items()):
        cx, cy = centre(g, col, row)
        mat = "light" if v == "L" else "dark"
        if last and (col, row) == (last["column"], last["row"]) and M.moving():
            hold = g["y"] - TOP["narrow" if small else "wide"] / 2 - 2
            anim, land = M.drop(cy - hold, p)
            discs.append(f'<g>{anim}' + sk.disc(cv, mat, cx, cy, p) + "</g>")
            continue
        discs.append(sk.disc(cv, mat, cx, cy, p))
    cv.add("".join(discs))
    sk.plate(cv, g["x"], g["y"], g["w"], g["h"], holes, p, empty)
    if last:
        cx, cy = centre(g, last["column"], last["row"])
        cv.add(sk.hole_ring(cv, cx, cy, rh + 2.6, M.appear(land - .02, .12) if M.moving() else ""),
               sk.ripple_at(cx, cy, rh, p * .95, land))
    if st["line"]:
        pts = [centre(g, col, row) for col, row in st["line"]]
        for i, (cx, cy) in enumerate(pts):
            cv.add(sk.hole_ring(cv, cx, cy, rh + 2.6, M.appear(land + .3 + i * .14, .1) if M.moving() else "", 2.4))
        (ax, ay), (bx, by) = pts[0], pts[-1]
        d = f"M{f1(ax)} {f1(ay)}L{f1(bx)} {f1(by)}"
        extra, anim = M.stroke_in(((bx - ax) ** 2 + (by - ay) ** 2) ** .5, land + .95, .45)
        cv.add(sk.connect(d, 5 if not small else 4, extra, anim))
    size = 9 if not small else 8.5
    under = g["y"] + g["h"] + (15 if not small else 13.5)      # the columns' numbers, under the frame between its legs
    for col in range(1, COLS + 1):
        cx = g["x"] + g["m"] + (col - .5) * p
        if last and col == last["column"]:
            # the column the last disc fell down: its number set on a block, and an arrow over the frame where it
            # went in, drawn as a drawing shows a part's travel
            cv.add(sk.column_mark(cv, col, cx, under, g["y"] - (8 if not small else 6), size,
                                  M.appear(M.HOLD, .15) if M.moving() else ""))
            continue
        cv.add(sk.say(cv, str(col), cx, under, size, role="muted", anchor="middle"))
    for row in range(1, ROWS + 1):
        cy = g["y"] + g["m"] + (ROWS - row + .5) * p
        cv.add(sk.say(cv, str(row), g["x"] - 11, cy + sk.cap(size) / 2, size, role="muted", anchor="middle"))


# --------------------------------------------------------------------------- the panel's count
def count(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """Each side's discs left, where chess counts what each side took: a rack of twenty-one, emptying as the frame
    fills, the house's White on top, as every pair of the game's sides is listed."""
    cv.add(sk.heading(cv, "discs left", x0, y))
    mini = 20 if not small else 18
    yy, px = y + 10, x0 + RACK
    for side in (HOUSE, other(HOUSE)):
        mat = material_of(side)
        cv.add(sk.capped(cv, f"{COLOUR[side]} · {'house' if side == HOUSE else 'github'}", x0, yy + mini / 2 + 3, 7.5,
                         6, px - 4 - GAP - x0, ls=.6, role="muted")[0])
        left = st["left"][side]
        chip = sk.chip(f"{left}", "", size=7.5, lab="accent" if left else "label")
        room = x1 - px - chip.w - 14
        pitch = min(mini * .56, (room - 8) / EACH)
        r = min(pitch * .46, mini * .3)
        sk.tray(cv, px - 4, yy - 1, EACH * pitch + 8, mini + 2)
        cy = yy + mini / 2
        dots = []
        for i in range(EACH):
            cx = px + 2 + i * pitch + pitch / 2
            if i < left:
                dots.append(sk.disc(cv, mat, cx, cy, 0, r=r))
            else:
                dots.append(sk.slot(cx, cy))
        cv.add("".join(dots))
        cv.add(chip.draw(cv, px + EACH * pitch + 14, yy + (mini - chip.h) / 2, "left"))
        yy += mini + 7
    return yy


def board_sheet(sk, st, title, desc, variant="wide") -> str:
    return S.board_sheet(sk, sys.modules[__name__], st, title, desc, variant)
