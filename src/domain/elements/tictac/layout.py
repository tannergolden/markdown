# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tic-Tac sheet's layout: its board of nine boards, and what its panel counts, inside the sheet every game
shares.

The board stands where chess's does, the same size: nine small boards three a side, the bars between them in the
material of chess's dark squares, and inside each its nine squares, a fine edge round every one with a gutter
between. The files a to i run under it and the ranks 1 to 9 beside it, a1 at the lower left. The last mark draws
itself stroke by stroke as the file opens and its square is boxed as the pen lifts. A board closed is washed back:
a won one under its winner's mark, drawn as large as the board, and a drawn one lined across. A mark that wins its
board strikes the board's three before the board's mark is drawn; a mark that wins the game strikes the three
boards. The board the side to move is sent to is bracketed at its four corners, as a drawing marks a detail to look
at, since the rules send it there; when it may play any open board, nothing is bracketed and its plate says so.

Under the Ghost Rule a ghost's square is filled as the bars are and edged in phantom lines: nobody can take it, and
no line runs through it. In place of chess's taken pieces the panel counts the boards each side has won, and says
across its heading where the ghosts stand and how many boards were drawn. Nothing on the sheet helps a player
choose: no square a side could win a board on next, and no board a side could win the game on.

The house always plays X, drawn in the light material, and GitHub always O, drawn in the dark, in the standard theme
and every print, as chess draws White and Black: the matchup has the house as X on the left. Only who places the
first ghost and who makes the first mark change, each drawn by the Arbiter.
"""
from __future__ import annotations

import sys

from ...canvas import c
from ...lettering import f1, fx
from ..games import sheet as S
from ..games.sides import HOUSE, name, other
from . import motion as M
from .game import FILES, GHOST, KIND, PLACE, mark_of  # noqa: F401  (KIND: the sheet's stamp)
from .shapes import LENGTH, strokes
from .skins import geometry

GAP = 8             # what keeps a label off its tray, chess's
RACK = 72           # where a rack starts: past its widest label, O · GITHUB, in the standard theme's letters and a
                    # gap, so the label is never set smaller, in any theme

LABEL = "tic-tac"
glyph = glyph_width = None              # a move names its mark, Xe5, and a ghost's row is the score sheet's G


def material(mark: str) -> str:
    """X, the house's mark, is drawn in the light material and O, GitHub's, in the dark: a game's colours never
    change, whichever side moves first."""
    return "light" if mark == "X" else "dark"


def board_box(b, x0, y0, n, small) -> tuple[float, float, float]:
    """A board's top left corner and its width."""
    bar, _, s, _ = geometry(n, small)
    bx, by = b
    return x0 + bx * (s + bar), y0 + (2 - by) * (s + bar), s


def cell_box(cell, x0, y0, n, small) -> tuple[float, float, float]:
    """A square's top left corner and its width."""
    _, gut, _, q = geometry(n, small)
    x, y = FILES.index(cell[0]), int(cell[1]) - 1
    X, Y, _ = board_box((x // 3, y // 3), x0, y0, n, small)
    return X + (x % 3) * (q + gut), Y + (2 - y % 3) * (q + gut), q


def centre(cell, x0, y0, n, small) -> tuple[float, float]:
    x, y, q = cell_box(cell, x0, y0, n, small)
    return x + q / 2, y + q / 2


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
    """Before the first ghost, who drew the side that places it."""
    return "drawn by the Arbiter"


def opening(st) -> tuple[str, str, str, str]:
    """Before the first ghost, the move to come: the ghosts' row, and the side the Arbiter drew to place first."""
    return f"{GHOST}.", "?", st["places"], f"{name(st['places'])} places the first ghost"


def medallion(cv, sk, st, cx, cy, r, side) -> str:
    """A side's medallion, holding the mark it plays this game, in that mark's own material."""
    b, mark = 2 * r * 1.02, mark_of(side)
    return sk.medal(cv, cx, cy, r, material(mark)) + sk.pen_mark(cv, mark, material(mark), cx - b / 2, cy - b / 2, b,
                                                                  shadow=False, edge=.9)


# --------------------------------------------------------------------------- the board
def pen(cv, drawn: str, mark: str, x, y, box, at: float = M.DRAW_AT, dur: float = M.DRAW) -> str:
    """A mark drawn in by its own pen strokes from `at`, over `dur`: a mask that follows each stroke in turn."""
    mid = cv.uid("m")
    paths, t = [], at
    for d, length in zip(strokes(mark), LENGTH[mark]):
        part = dur * length / sum(LENGTH[mark])
        extra, anim = M.stroke_in(length, t, part)
        paths.append(f'<path d="{d}" fill="none" stroke="{c("white")}" stroke-width="24" stroke-linecap="round"'
                     f'{extra}>{anim}</path>')
        t += part
    cv.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{f1(x - 10)}" y="{f1(y - 10)}" '
                   f'width="{f1(box + 20)}" height="{f1(box + 20)}"><g transform="translate({f1(x)} {f1(y)}) '
                   f'scale({fx(box / 100, 4)})">' + "".join(paths) + "</g></mask>")
    return f'<g mask="url(#{mid})">{drawn}</g>'


def struck(cells: list, x0, y0, n, small, reach: float) -> tuple[str, float]:
    """A line through the centres of `cells`, run on past each end by `reach`: its path, and its length."""
    (ax, ay), (bx, by) = cells[0], cells[-1]
    span = max(abs(bx - ax), abs(by - ay))
    ox, oy = (bx - ax) / span * reach, (by - ay) / span * reach
    d = f"M{f1(ax - ox)} {f1(ay - oy)}L{f1(bx + ox)} {f1(by + oy)}"
    return d, ((bx - ax + 2 * ox) ** 2 + (by - ay + 2 * oy) ** 2) ** .5


def board(cv, sk, st, x0, y0, n, *, small=False) -> None:
    bar, gut, s, q = geometry(n, small)
    box = q * .86                        # a mark's 100-unit box, on this board
    moving = M.moving()
    sk.board_base(cv, x0, y0, n, small)
    last = st["last"]
    if last:
        x, y, lq = cell_box(last["cell"], x0, y0, n, small)
        sk.cell_mark(cv, x, y, lq, lq, M.appear(M.LIFT - .05, .2) if moving else "")
    clip = cv.uid("b")
    cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(n)}" height="{f1(n)}"/>'
                   "</clipPath>")
    sk.board_over(cv, clip, x0, y0, n / 8, None, "")      # the board's face catching the lamp, as chess's does
    marks = []
    for cell in (f"{f}{r}" for r in range(9, 0, -1) for f in FILES):
        cx, cy = centre(cell, x0, y0, n, small)
        if cell in st["ghosts"]:
            gx, gy, gq = cell_box(cell, x0, y0, n, small)
            now = last and last["ghost"] and last["cell"] == cell and moving
            marks.append(sk.ghost(cv, gx, gy, gq, M.appear(M.DRAW_AT, .3) if now else ""))
            continue
        mark = st["cells"].get(cell)
        if not mark:
            marks.append(sk.centre_mark(cx, cy, q * .14))
            continue
        drawn = sk.pen_mark(cv, mark, material(mark), cx - box / 2, cy - box / 2, box,
                            edge=1.05 if not small else .95)
        if last and cell == last["cell"] and moving:
            drawn = pen(cv, drawn, mark, cx - box / 2, cy - box / 2, box)
        marks.append(drawn)
    cv.add("".join(marks))
    if last:
        # the pen lifts, or the ghost is down: a ring running out from it, as a chess piece's landing sends one out
        cx, cy = centre(last["cell"], x0, y0, n, small)
        cv.add(sk.ripple_at(cx, cy, q * .32, q * .7, M.LIFT, clip=clip))
    # the boards that are closed: washed back, a won one under its winner's mark, a drawn one lined across
    claimed_now = last["claimed"] if last else None
    for b, who in st["boards"].items():
        if not who:
            continue
        X, Y, _ = board_box(b, x0, y0, n, small)
        now = bool(last and claimed_now and last["board"] == b)
        if now and who != "draw" and last["small_line"]:
            # the three that won it, struck through once the mark is down, as Tic-Tac-Toe strikes its line
            d, length = struck([centre(cell, x0, y0, n, small) for cell in last["small_line"]], x0, y0, n, small,
                               q * .3)
            extra, anim = M.stroke_in(length, M.STRIKE_AT, M.STRIKE) if moving else ("", "")
            cv.add(sk.strike(d, 3.2 if not small else 2.8, extra, anim))
        appear = M.appear(M.CLAIM_AT - .1, .25) if now and moving else ""
        keep = ""
        if now:
            # the move that closed the board stays clear of the wash: its square boxed and its mark whole
            lx, ly, lq = cell_box(last["cell"], x0, y0, n, small)
            lb = lq * .86
            keep = sk.kept(lx, ly, lq) + sk.pen_mark(cv, last["mark"], material(last["mark"]), lx + (lq - lb) / 2,
                                                     ly + (lq - lb) / 2, lb, edge=1.05 if not small else .95)
        if who == "draw":
            cv.add(f"<g>{appear}{sk.wash(X, Y, s)}{sk.drawn(cv, X, Y, s)}{keep}</g>")
            continue
        B = s * .9
        big = sk.pen_mark(cv, who, material(who), X + (s - B) / 2, Y + (s - B) / 2, B, edge=1.7 if not small else 1.5)
        if now and moving:
            big = pen(cv, big, who, X + (s - B) / 2, Y + (s - B) / 2, B, M.CLAIM_AT, M.DRAW)
        cv.add(f"<g>{appear}{sk.wash(X, Y, s)}{keep}</g>" + big)
    # where the side to move must play, the rules' call: bracketed once the last move has done
    if not st["result"] and st["target"] is not None:
        X, Y, _ = board_box(st["target"], x0, y0, n, small)
        at = M.CLAIM_AT + M.DRAW if claimed_now else M.LIFT + .05
        cv.add(sk.brackets(X, Y, s, small, M.appear(at, .25) if moving and last else ""))
    if st["line"]:
        pts = [(board_box(b, x0, y0, n, small)[0] + s / 2, board_box(b, x0, y0, n, small)[1] + s / 2)
               for b in st["line"]]
        d, length = struck(pts, x0, y0, n, small, s * .3)
        extra, anim = M.stroke_in(length, M.WIN_AT, M.STRIKE) if moving else ("", "")
        cv.add(sk.strike(d, 7 if not small else 6, extra, anim))
    size = 8 if not small else 7.5
    for i in range(9):
        X, _, _ = board_box((i // 3, 0), x0, y0, n, small)
        cx = X + (i % 3) * (q + gut) + q / 2
        _, Yr, _ = board_box((0, (8 - i) // 3), x0, y0, n, small)
        cy = Yr + (i % 3) * (q + gut) + q / 2
        cv.add(sk.say(cv, FILES[i], cx, y0 + n + 15, size, role="muted", anchor="middle"),
               sk.say(cv, str(9 - i), x0 - 11, cy + sk.cap(size) / 2, size, role="muted", anchor="middle"))
    sk.bevel(cv, x0, y0, n)


# --------------------------------------------------------------------------- the panel's count
def count(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """The boards each side has won, where chess counts what each side took: each won board's mark on its side's
    tray, the house's X on top, both trays as long, the number beside each; and across the heading where the ghosts
    stand and how many boards were drawn. It counts and says nothing more."""
    cv.add(sk.heading(cv, "boards won", x0, y))
    said = ([f"ghost{'s' if len(st['ghosts']) > 1 else ''} " + " · ".join(st["ghosts"])] if st["ghosts"] else [])
    said += [f"{st['drawn']} drawn"] if st["drawn"] else []
    if said:
        cv.add(sk.capped(cv, "  ·  ".join(said), x1, y, 7.5, 6, (x1 - x0) * .55, ls=.6, anchor="end")[0])
    mini = 20 if not small else 18
    yy, px = y + 10, x0 + RACK
    pitch, b = mini * 1.2, mini * 1.04                  # a place on the rack, and the mark that fills it
    places = max(1, *st["won"].values())               # both trays as long, the longer side's count
    for side in (HOUSE, other(HOUSE)):
        mark = mark_of(side)
        cv.add(sk.capped(cv, f"{mark} · {'house' if side == HOUSE else 'github'}", x0, yy + mini / 2 + 3, 7.5, 6,
                         px - 4 - GAP - x0, ls=.6, role="muted")[0])
        won = st["won"][side]
        sk.tray(cv, px - 4, yy - 1, places * pitch + 8, mini + 2)
        cy = yy + mini / 2
        out = []
        for i in range(places):
            cx = px + 2 + i * pitch + pitch / 2
            out.append(sk.pen_mark(cv, mark, material(mark), cx - b / 2, cy - b / 2, b, shadow=False, edge=.9)
                       if i < won else sk.centre_mark(cx, cy, mini * .32))
        cv.add("".join(out))
        chip = sk.chip(f"{won}", "", size=7.5, lab="accent" if won else "label")
        cv.add(chip.draw(cv, px + places * pitch + 14, yy + (mini - chip.h) / 2, "left"))
        yy += mini + 7
    return yy


def board_sheet(sk, st, title, desc, variant="wide") -> str:
    return S.board_sheet(sk, sys.modules[__name__], st, title, desc, variant)
