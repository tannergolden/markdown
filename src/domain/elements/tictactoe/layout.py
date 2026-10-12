# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tic-Tac-Toe sheet's layout: its board, and what its panel counts, inside the sheet every game shares.

The board stands where chess's does, the same size: three cells a side, each as wide as chess's eight squares
shared three ways, the bars between them in the material of chess's dark squares, the files a to c under it and the
ranks 1 to 3 beside it, and the eight lines a game is won on drawn faint through the cells while it goes on, as a
drawing draws its centre lines: all eight, whatever stands on them, so the board never says which a side could
still win on. The last mark draws itself stroke by stroke as the file opens and its cell is marked as the pen
lifts; a won line is struck through. In place of chess's taken pieces the panel counts each side's marks left, a
rack of five for the side that moved first and four for the other, emptying as the board fills, as Connect Four's
counts its discs. Nothing on the sheet helps a player choose: no cell a side could win on next, no word of what
perfect play makes of the game, and no call to block.

The house always plays X, drawn in the light material, and GitHub always O, drawn in the dark, in the standard theme
and every print, as chess draws White and Black: the matchup has the house as X on the left. Only who moves first
changes, the side the Arbiter opened for, so O moves first in a game opened for GitHub.
"""
from __future__ import annotations

import sys

from ...canvas import c
from ...lettering import f1, fx
from ..games import sheet as S
from ..games.sides import HOUSE, other
from . import motion as M
from .game import FILES, KIND, LINES, mark_of  # noqa: F401  (KIND: the sheet's stamp)
from .shapes import LENGTH, strokes

GAP = 8             # what keeps a label off its tray, chess's
RACK = 72           # where a rack starts: past its widest label, O · GITHUB, in the standard theme's letters and a
                    # gap, so the label is never set smaller, in any theme
MOST = 5            # the most marks a side has: the side that moves first

LABEL = "tic-tac-toe"
glyph = glyph_width = None              # a move names its mark, Xb2, so the score sheet needs no mark before it


def material(mark: str) -> str:
    """X, the house's mark, is drawn in the light material and O, GitHub's, in the dark: a game's colours never
    change, whichever side moves first."""
    return "light" if mark == "X" else "dark"


def interior(cell: str, x0, y0, n, bar) -> tuple[float, float, float, float]:
    """A cell's open face: from the board's edge or a bar's to the next."""
    s = n / 3
    i, j = FILES.index(cell[0]), 3 - int(cell[1])
    x = x0 + i * s + (bar / 2 if i else 0)
    y = y0 + j * s + (bar / 2 if j else 0)
    w = s - (bar / 2 if i else 0) - (bar / 2 if i < 2 else 0)
    h = s - (bar / 2 if j else 0) - (bar / 2 if j < 2 else 0)
    return x, y, w, h


def centre(cell: str, x0, y0, n, bar) -> tuple[float, float]:
    x, y, w, h = interior(cell, x0, y0, n, bar)
    return x + w / 2, y + h / 2


# --------------------------------------------------------------------------- the sheet's questions
def band_mark(x, y, size, paper, block="") -> str:
    """The band's mark: an X and an O, the game's two marks, drawn as the pen draws them."""
    return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 20, 4)})" fill="none" stroke="{paper}" '
            f'stroke-width="2.5" stroke-linecap="round"><path d="M1.8 6.6 8.6 13.4M8.6 6.6 1.8 13.4"/>'
            f'<circle cx="14.6" cy="10" r="3.9"/></g>')


def room(x0, y0, n) -> tuple:
    return (x0 - 2, y0 - 2, n + 10, n + 10)


def height(n, small=False) -> float:
    return n


def side_name(side, st) -> str:
    return mark_of(side)


def first(st) -> str:
    """Before the first mark, which mark moves first: the opener's, X for the house and O for GitHub."""
    return f"{mark_of(st['opens'])} moves first"


def medallion(cv, sk, st, cx, cy, r, side) -> str:
    """A side's medallion, holding the mark it plays this game, in that mark's own material."""
    b, mark = 2 * r * 1.02, mark_of(side)
    return sk.medal(cv, cx, cy, r, material(mark)) + sk.pen_mark(cv, mark, material(mark), cx - b / 2, cy - b / 2, b,
                                                                  shadow=False, edge=.9)


# --------------------------------------------------------------------------- the board
def board(cv, sk, st, x0, y0, n, *, small=False) -> None:
    s = n / 3
    bar = 12 if not small else 10
    box = s * .92                        # a mark's 100-unit box, on this board
    sk.board_base(cv, x0, y0, n, bar)
    last = st["last"]
    if last:
        sk.cell_mark(cv, *interior(last["cell"], x0, y0, n, bar), M.appear(M.LIFT - .05, .2) if M.moving() else "")
    clip = cv.uid("b")
    cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(n)}" height="{f1(n)}"/>'
                   "</clipPath>")
    sk.board_over(cv, clip, x0, y0, n / 8, None, "")      # the board's face catching the lamp, as chess's does
    if not st["result"]:
        # the eight lines a game is won on, as a drawing shows its centre lines: all eight, faint, whatever stands on
        # them, so the board never singles out a line a side could still win on, or one no side can
        lines = []
        for line in LINES:
            (ax, ay), (bx, by) = centre(line[0], x0, y0, n, bar), centre(line[-1], x0, y0, n, bar)
            span = max(abs(bx - ax), abs(by - ay))
            ox, oy = (bx - ax) / span * s * .42, (by - ay) / span * s * .42
            lines.append(f"M{f1(ax - ox)} {f1(ay - oy)}L{f1(bx + ox)} {f1(by + oy)}")
        cv.add(sk.open_lines("".join(lines)))
    marks = []
    for row in (3, 2, 1):
        for f in FILES:
            cell = f"{f}{row}"
            cx, cy = centre(cell, x0, y0, n, bar)
            mark = st["board"].get(cell)
            if not mark:
                marks.append(sk.centre_mark(cx, cy, s * .1))
                continue
            drawn = sk.pen_mark(cv, mark, material(mark), cx - box / 2, cy - box / 2, box,
                                edge=1.6 if not small else 1.4)
            if last and cell == last["cell"] and M.moving():
                drawn = pen(cv, drawn, mark, cx - box / 2, cy - box / 2, box)
            marks.append(drawn)
    cv.add("".join(marks))
    if st["line"]:
        (ax, ay), (bx, by) = centre(st["line"][0], x0, y0, n, bar), centre(st["line"][-1], x0, y0, n, bar)
        span = max(abs(bx - ax), abs(by - ay))
        ox, oy = (bx - ax) / span * s * .27, (by - ay) / span * s * .27
        d = f"M{f1(ax - ox)} {f1(ay - oy)}L{f1(bx + ox)} {f1(by + oy)}"
        extra, anim = M.stroke_in(((bx - ax + 2 * ox) ** 2 + (by - ay + 2 * oy) ** 2) ** .5, M.STRIKE_AT, M.STRIKE)
        cv.add(sk.strike(d, 6.5 if not small else 5.5, extra, anim))
    if last:
        # the pen lifts: a ring running out from the mark, as a chess piece's landing sends one out
        cx, cy = centre(last["cell"], x0, y0, n, bar)
        cv.add(sk.ripple_at(cx, cy, s * .3, s * .62, M.LIFT, clip=clip))
    size = 9 if not small else 8.5
    for i in range(3):
        cv.add(sk.say(cv, FILES[i], x0 + i * s + s / 2, y0 + n + 16, size, role="muted", anchor="middle"),
               sk.say(cv, str(3 - i), x0 - 11, y0 + i * s + s / 2 + sk.cap(size) / 2, size, role="muted",
                      anchor="middle"))
    sk.bevel(cv, x0, y0, n)


def pen(cv, drawn: str, mark: str, x, y, box) -> str:
    """The last mark, drawn in by its own pen strokes as the file opens: a mask that follows each stroke in turn."""
    mid = cv.uid("m")
    paths, t = [], M.DRAW_AT
    for d, length in zip(strokes(mark), LENGTH[mark]):
        dur = M.DRAW * length / sum(LENGTH[mark])
        extra, anim = M.stroke_in(length, t, dur)
        paths.append(f'<path d="{d}" fill="none" stroke="{c("white")}" stroke-width="24" stroke-linecap="round"'
                     f'{extra}>{anim}</path>')
        t += dur
    cv.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{f1(x - 10)}" y="{f1(y - 10)}" '
                   f'width="{f1(box + 20)}" height="{f1(box + 20)}"><g transform="translate({f1(x)} {f1(y)}) '
                   f'scale({fx(box / 100, 4)})">' + "".join(paths) + "</g></mask>")
    return f'<g mask="url(#{mid})">{drawn}</g>'


# --------------------------------------------------------------------------- the panel's count
def count(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """Each side's marks left, where chess counts what each side took: a rack of five for the side that moved first
    and four for the other, emptying as the board fills, a used place keeping an open cell's centre mark, the
    house's X on top, as every pair of the game's sides is listed. It counts and says nothing more: no cell a side
    could win on, and no word of what perfect play makes of the game."""
    cv.add(sk.heading(cv, "marks left", x0, y))
    mini = 20 if not small else 18
    yy, px = y + 10, x0 + RACK
    pitch, b = mini * 1.2, mini * 1.04                  # a place on the rack, and the mark that fills it
    for side in (HOUSE, other(HOUSE)):
        mark = mark_of(side)
        cv.add(sk.capped(cv, f"{mark} · {'house' if side == HOUSE else 'github'}", x0, yy + mini / 2 + 3, 7.5, 6,
                         px - 4 - GAP - x0, ls=.6, role="muted")[0])
        left = st["left"][side]
        sk.tray(cv, px - 4, yy - 1, st["each"][side] * pitch + 8, mini + 2)
        cy = yy + mini / 2
        places = []
        for i in range(st["each"][side]):
            cx = px + 2 + i * pitch + pitch / 2
            places.append(sk.pen_mark(cv, mark, material(mark), cx - b / 2, cy - b / 2, b, shadow=False, edge=.9)
                          if i < left else sk.centre_mark(cx, cy, mini * .32))
        cv.add("".join(places))
        chip = sk.chip(f"{left}", "", size=7.5, lab="accent" if left else "label")
        cv.add(chip.draw(cv, px + MOST * pitch + 14, yy + (mini - chip.h) / 2, "left"))
        yy += mini + 7
    return yy


def board_sheet(sk, st, title, desc, variant="wide") -> str:
    return S.board_sheet(sk, sys.modules[__name__], st, title, desc, variant)
