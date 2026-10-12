# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tic-Tac-Toe sheet's layout: its board, and what its panel counts, inside the sheet every game shares.

The board stands where chess's does, the same size: three cells a side, each as wide as chess's eight squares
shared three ways, the bars between them in the material of chess's dark squares, the files a to c under it and the
ranks 1 to 3 beside it, and the eight lines a game is won on drawn faint through the cells, as a drawing draws its
centre lines, while a side can still win on them. The last mark draws itself stroke by stroke as the file opens and
its cell is marked as the pen lifts; a cell the side to move must block is marked as chess marks a king in check,
the threatening mark in phantom lines inside it; a won line is struck through. In place of chess's taken pieces the
panel says what perfect play says: the game is solved, so the sheet says how this one ends if neither side errs
from here, and where each side would win next; once it is over, how it ended and the line.

The house always plays X, drawn in the light material, and GitHub always O, drawn in the dark, in the standard theme
and every print, as chess draws White and Black: the matchup has the house as X on the left. Only who moves first
changes, the side the Arbiter opened for, so O moves first in a game opened for GitHub.
"""
from __future__ import annotations

import sys

from ...canvas import c
from ...lettering import f1, fx
from ..games import sheet as S
from ..games.sides import GITHUB, HOUSE, name, other
from . import motion as M
from .game import FILES, KIND, LINES, mark_of  # noqa: F401  (KIND: the sheet's stamp)
from .shapes import LENGTH, strokes

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
    danger = [] if st["result"] else st["threats"][other(st["to_move"])]
    # the eight lines a game is won on, as a drawing shows its centre lines: each still open to one side or both
    # drawn faint through the cells, a line both sides have marked left out
    open_lines = []
    for line in LINES:
        marks_on = {st["board"].get(c_) for c_ in line} - {None}
        if len(marks_on) < 2 and not st["result"]:
            (ax, ay), (bx, by) = centre(line[0], x0, y0, n, bar), centre(line[-1], x0, y0, n, bar)
            span = max(abs(bx - ax), abs(by - ay))
            ox, oy = (bx - ax) / span * s * .42, (by - ay) / span * s * .42
            open_lines.append(f"M{f1(ax - ox)} {f1(ay - oy)}L{f1(bx + ox)} {f1(by + oy)}")
    if open_lines:
        cv.add(sk.open_lines("".join(open_lines)))
    marks = []
    for row in (3, 2, 1):
        for f in FILES:
            cell = f"{f}{row}"
            cx, cy = centre(cell, x0, y0, n, bar)
            mark = st["board"].get(cell)
            if not mark:
                if cell not in danger:
                    marks.append(sk.centre_mark(cx, cy, s * .1))
                continue
            drawn = sk.pen_mark(cv, mark, material(mark), cx - box / 2, cy - box / 2, box,
                                edge=1.6 if not small else 1.4)
            if last and cell == last["cell"] and M.moving():
                drawn = pen(cv, drawn, mark, cx - box / 2, cy - box / 2, box)
            marks.append(drawn)
    cv.add("".join(marks))
    threat = mark_of(other(st["to_move"]))
    for cell in danger:
        # the cell the side to move must block, marked as chess marks a king in check, blooming as the mark lands,
        # with the threatening mark in phantom lines where it would fall
        x, y, w, h = interior(cell, x0, y0, n, bar)
        side = min(w, h) * .8
        cx, cy = x + w / 2, y + h / 2
        pulse = M.ani("opacity", "0;0;1;.45;1;.45;1", "0;.36;.46;.6;.73;.86;1", M.LIFT + 2.2)
        cv.add(sk.clouded(cv, cx - side / 2, cy - side / 2, side, pulse, clip=clip,
                          inside=sk.phantom_mark(threat, cx - box / 2, cy - box / 2, box)))
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
    """What perfect play says, where chess counts what each side took: how the game ends from here if neither side
    errs (the game is solved), and the cells where each side would win next; once it is over, how, and the line."""
    cv.add(sk.heading(cv, "perfect play", x0, y))
    mini = 20 if not small else 18
    yy, px = y + 10, x0 + 72
    res = st["result"]
    cv.add(sk.caps(cv, "result" if res else "from here", x0, yy + mini / 2 + 3, 7.5, ls=.6, role="muted"))
    if res:
        w = res["winner"]
        plate = sk.chip(f"{mark_of(w)} wins" if w else "drawn", "", size=7.5, lab="turn" if w else "label")
        say = f"{name(w)}, {res['how']}" if w else res["how"]
    elif st["outlook"] in (HOUSE, GITHUB):
        plate = sk.chip(f"{mark_of(st['outlook'])} wins", "", size=7.5, lab="turn")
        say = f"{name(st['outlook'])} wins with best play"
    else:
        plate = sk.chip("draw", "", size=7.5, lab="label")
        say = "best play by both sides draws"
    cv.add(plate.draw(cv, px, yy + (mini - plate.h) / 2, "outlook"))
    cv.add(sk.capped(cv, say, px + plate.w + 9, yy + mini / 2 + 3, 7, 6, x1 - px - plate.w - 9, ls=.5)[0])
    yy += mini + 7
    cv.add(sk.caps(cv, "the line" if res else "wins next", x0, yy + mini / 2 + 3, 7.5, ls=.6, role="muted"))
    if res:
        items = [(mark_of(res["winner"]) if res["winner"] else "", cell) for cell in st["line"]]
    else:
        items = [(mark_of(side), cell) for side in (st["to_move"], other(st["to_move"]))
                 for cell in st["threats"][side]]
    if not items:
        sk.tray(cv, px - 4, yy - 1, 58, mini + 2)
        cv.add(sk.on_tray(cv, "none" if res else "none yet", px + 25, yy + mini / 2 + 3, 7, caps=True, ls=.5,
                          anchor="middle"))
        return yy + mini + 7
    widths = [(mini * .84 if mk else 0) + sk.width(cell, "bold", 9.5) + 9 for mk, cell in items]
    # as many as the row holds, and how many more there are after them
    shown, room = len(items), x1 - px - 3
    while shown and sum(widths[:shown]) + (sk.width(f"+{len(items) - shown}", "bold", 9.5) + 12
                                           if shown < len(items) else 0) > room:
        shown -= 1
    sk.tray(cv, px - 4, yy - 1, sum(widths[:shown]) + 3, mini + 2)
    if shown < len(items):
        cv.add(sk.say(cv, f"+{len(items) - shown}", px + sum(widths[:shown]) + 8, yy + mini / 2 + sk.cap(9.5) / 2,
                      9.5, role="muted"))
    for (mk, cell), w in zip(items[:shown], widths):
        tx = px + 2
        if mk:
            b = mini * 1.06
            cv.add(sk.pen_mark(cv, mk, material(mk), px - b * .18, yy + (mini - b) / 2, b, shadow=False, edge=.9))
            tx = px + mini * .84
        cv.add(sk.on_tray(cv, cell, tx, yy + mini / 2 + sk.cap(9.5) / 2, 9.5))
        px += w
    return yy + mini + 7


def board_sheet(sk, st, title, desc, variant="wide") -> str:
    return S.board_sheet(sk, sys.modules[__name__], st, title, desc, variant)
