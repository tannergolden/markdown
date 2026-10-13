# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Pentago sheet's layout: its four quarters, and what its panel counts, inside the sheet every game shares.

The board stands where chess's does, the same size: four quarter plates of three holes a side, cut and lined as one
plate is, with a gap between them so each can turn. The files a to f run under it and the ranks 1 to 6 beside it, a1
at the lower left. The marbles are seen face on through their holes: the house's White in the light material,
GitHub's Black in the dark, and a ghost, nobody's, as the plate's own.

The last move plays as it was made: its marble is set in its hole, which is ringed, with a ripple; then its quarter
turns its quarter turn from where it stood when the marble went in, everything on it turning with it, a ghost too,
and an arrow round the quarter's outer corner is drawn the way it went. A won game's five are ringed one after
another and joined. A move is written as the sheet draws it: the marble's colour, its hole, and the turn, a small
circular arrow and the quarter's initials, `e4 ↻ UR`; a ghost's, the ghost and its hole. In place of chess's taken
pieces the panel counts each side's marbles left, a rack of seventeen, and says across its heading where the ghosts
stand now. Nothing on the sheet helps a player choose: no hole or turn that would make five, and no call to block.
The house always plays White and GitHub Black, and every word on the sheet says so, the house's White first.
"""
from __future__ import annotations

import sys

from ...lettering import f1, fx
from ..games import sheet as S
from ..games.sides import HOUSE, name, other
from . import motion as M
from .game import COLOUR, EACH, FILES, GHOST, KIND, QUARTERS, material_of, parse, quarter_cells, quarter_of  # noqa: F401
from .shapes import DISC, GAP, HOLE, MARGIN

RACK_GAP = 8        # what keeps a label off its tray, chess's
RACK = 86           # where a rack starts: past its widest label, BLACK · GITHUB, in the standard theme's
                    # letters and a gap, so the label is never set smaller, in any theme

LABEL = "pentago"


def geometry(n, small) -> tuple[float, float, float, float]:
    """The board's measures, `n` wide: the gap between the quarters, a quarter's width, its pitch and its margin."""
    gap = GAP["narrow" if small else "wide"]
    q = (n - gap) / 2
    p = q / (3 + 2 * MARGIN)
    return gap, q, p, MARGIN * p


def quarter_box(qk, x0, y0, n, small) -> tuple[float, float, float]:
    gap, q, _, _ = geometry(n, small)
    qx, qy = QUARTERS[qk]
    return x0 + (0 if qx == 0 else q + gap), y0 + (0 if qy == 3 else q + gap), q


def centre(cell, x0, y0, n, small) -> tuple[float, float]:
    """A hole's centre."""
    _, _, p, m = geometry(n, small)
    x, y = FILES.index(cell[0]), int(cell[1]) - 1
    qk = quarter_of(cell)
    qx, qy = QUARTERS[qk]
    X, Y, _ = quarter_box(qk, x0, y0, n, small)
    return X + m + (x - qx + .5) * p, Y + m + (2 - (y - qy) + .5) * p


# --------------------------------------------------------------------------- the sheet's questions
def band_mark(x, y, size, paper, block="") -> str:
    """The band's mark: the board's four quarters, one holding a marble."""
    return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 20, 4)})" fill="none" stroke="{paper}" '
            f'stroke-width="1.8"><rect x="1.5" y="1.5" width="7.6" height="7.6" rx="1.4"/>'
            f'<rect x="10.9" y="1.5" width="7.6" height="7.6" rx="1.4"/><rect x="1.5" y="10.9" width="7.6" '
            f'height="7.6" rx="1.4"/><rect x="10.9" y="10.9" width="7.6" height="7.6" rx="1.4"/>'
            f'<circle cx="14.7" cy="5.3" r="1.9" fill="{paper}" stroke="none"/></g>')


def room(x0, y0, n) -> tuple:
    return (x0 - 2, y0 - 2, n + 10, n + 10)


def height(n, small=False) -> float:
    return n


def side_name(side, st) -> str:
    return COLOUR[side]


def first(st) -> str:
    """Before the first ghost, who drew the side that sets it."""
    return "drawn by the Arbiter"


def opening(st) -> tuple[str, str, str, str]:
    """Before the first ghost, the move to come: the ghosts' row, and the side the Arbiter drew to set first."""
    return f"{GHOST}.", "?", st["places"], f"{name(st['places'])} sets the first ghost"


def medallion(cv, sk, st, cx, cy, r, side) -> str:
    """A side's medallion, holding a marble of its own: White for the house, Black for GitHub."""
    mat = material_of(side)
    return sk.medal(cv, cx, cy, r, mat) + sk.disc(cv, mat, cx, cy, 0, r=r * .72)


def glyph(cv, sk, st, side, x, base, size) -> tuple[str, float]:
    """The marble a move is set with, before its hole. Returns it and the room it takes."""
    r = size * .3
    return sk.disc(cv, material_of(side), x + r + .5, base - sk.cap(size) / 2, 0, r=r), glyph_width(size)


def glyph_width(size) -> float:
    return 2 * size * .3 + size * .22


def write(cv, sk, st, side, move, x, base, size, role="ink") -> float:
    """A move as the sheet writes it: the marble's colour, its hole, and the quarter turn after it, a circular arrow
    and the quarter's initials; a ghost's, the ghost and its hole. Returns how wide it is."""
    x0 = x
    mv = parse(move)
    if mv["quarter"] is None and not mv["won"]:
        r = size * .3
        cv.add(sk.ghost_marble(cv, x + r + .5, base - sk.cap(size) / 2, r))
        x += glyph_width(size)
    else:
        mark, w = glyph(cv, sk, st, side, x, base, size)
        cv.add(mark)
        x += w
    text = mv["cell"] + ("#" if mv["won"] and not mv["quarter"] else "")
    cv.add(sk.say(cv, text, x, base, size, role=role))
    x += sk.width(text, "bold", size)
    if mv["quarter"]:
        x += size * .3
        icon, w = sk.turn_glyph(x, base - sk.cap(size) / 2, size * .3, mv["way"], role)
        cv.add(icon)
        x += w + size * .12
        tail = mv["quarter"].upper() + ("#" if mv["won"] else "")
        cv.add(sk.say(cv, tail, x, base, size, role=role))
        x += sk.width(tail, "bold", size)
    return x - x0


def written(sk, move, size) -> float:
    """How wide a move is, written as `write` writes it."""
    mv = parse(move)
    w = glyph_width(size) + sk.width(mv["cell"] + ("#" if mv["won"] and not mv["quarter"] else ""), "bold", size)
    if mv["quarter"]:
        w += size * .3 + 2 * size * .3 + size * .3 * .35 + size * .12
        w += sk.width(mv["quarter"].upper() + ("#" if mv["won"] else ""), "bold", size)
    return w


# --------------------------------------------------------------------------- the board
def board(cv, sk, st, x0, y0, n, *, small=False) -> None:
    _, q, p, m = geometry(n, small)
    rh = HOLE * p
    last = st["last"]
    moving = M.moving()
    played = bool(last and not last["ghost"])
    tq = last["quarter"] if played and last["turned"] else None
    for qk in QUARTERS:
        X, Y, _ = quarter_box(qk, x0, y0, n, small)
        sk.frame_shadow(cv, X, Y, q, q)
    for qk in QUARTERS:
        X, Y, _ = quarter_box(qk, x0, y0, n, small)
        start = len(cv.body)
        cells = quarter_cells(qk)
        holes = [centre(cl, x0, y0, n, small) for cl in cells]
        empty = [centre(cl, x0, y0, n, small) for cl in cells if cl not in st["cells"]]
        set_in = last["landed"] if last else None        # where the last marble stands, its quarter turned
        marbles = []
        for cell in cells:
            v = st["cells"].get(cell)
            if not v:
                continue
            cx, cy = centre(cell, x0, y0, n, small)
            drawn = (sk.ghost_marble(cv, cx, cy, DISC * p) if v == GHOST
                     else sk.disc(cv, "light" if v == "W" else "dark", cx, cy, p))
            if moving and cell == set_in:
                drawn = f"<g>{M.appear(M.DROP, .2)}{drawn}</g>"     # set in as the move begins
            marbles.append(drawn)
        cv.add("".join(marbles))
        sk.plate(cv, X, Y, q, q, holes, p, empty)
        if set_in and quarter_of(set_in) == qk:
            lx, ly = centre(set_in, x0, y0, n, small)
            cv.add(sk.hole_ring(cv, lx, ly, rh + 2.6, M.appear(M.LAND - .02, .12) if moving else ""),
                   sk.ripple_at(lx, ly, rh, p * .95, M.LAND))
        drawn_q = "".join(cv.body[start:])
        del cv.body[start:]
        if qk == tq and moving:
            # the quarter, drawn as it stands, turned back to where it stood when the marble went in, and turning
            # its quarter turn into place: at rest, and without SMIL, it stands as it is
            cx, cy = X + q / 2, Y + q / 2
            back = -90 if last["way"] == "cw" else 90
            t = M.TWIST_AT + M.TWIST
            anim = M.ani("transform", f"{back} {f1(cx)} {f1(cy)};{back} {f1(cx)} {f1(cy)};0 {f1(cx)} {f1(cy)}",
                         f"0;{fx(M.TWIST_AT / t, 3)};1", t, spline=f"0 0 1 1;{M.TURN_EASE}", kind="animateTransform",
                         typ="rotate")
            cv.add(f"<g>{anim}{drawn_q}</g>")
        else:
            cv.add(drawn_q)
    if tq:
        X, Y, _ = quarter_box(tq, x0, y0, n, small)
        cv.add(sk.turn_mark(X, Y, q, tq, last["way"], m * .55, M.appear(M.TWIST_AT, .2) if moving else ""))
    if st["line"]:
        land = M.TWIST_AT + M.TWIST if tq else M.LAND
        pts = [centre(cl, x0, y0, n, small) for cl in st["line"]]
        for i, (cx, cy) in enumerate(pts):
            cv.add(sk.hole_ring(cv, cx, cy, rh + 2.6, M.appear(land + .3 + i * .14, .1) if moving else "", 2.4))
        (ax, ay), (bx, by) = pts[0], pts[-1]
        d = f"M{f1(ax)} {f1(ay)}L{f1(bx)} {f1(by)}"
        extra, anim = M.stroke_in(((bx - ax) ** 2 + (by - ay) ** 2) ** .5, land + 1.05, .45)
        cv.add(sk.connect(d, 5 if not small else 4, extra, anim))
    size = 9 if not small else 8.5
    for f in FILES:
        cx, _ = centre(f"{f}1", x0, y0, n, small)
        cv.add(sk.say(cv, f, cx, y0 + n + 15, size, role="muted", anchor="middle"))
    for r in range(1, 7):
        _, cy = centre(f"a{r}", x0, y0, n, small)
        cv.add(sk.say(cv, str(r), x0 - 11, cy + sk.cap(size) / 2, size, role="muted", anchor="middle"))


# --------------------------------------------------------------------------- the panel's count
def count(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """Each side's marbles left, where chess counts what each side took: a rack of seventeen, emptying as the board
    fills, the house's White on top, as every pair of the game's sides is listed; and across the heading where the
    ghosts stand now, since a turn can move them."""
    cv.add(sk.heading(cv, "marbles left", x0, y))
    if st["ghosts"]:
        said = f"ghost{'s' if len(st['ghosts']) > 1 else ''} " + " · ".join(st["ghosts"])
        cv.add(sk.capped(cv, said, x1, y, 7.5, 6, (x1 - x0) * .5, ls=.6, anchor="end")[0])
    mini = 20 if not small else 18
    yy, px = y + 10, x0 + RACK
    for side in (HOUSE, other(HOUSE)):
        mat = material_of(side)
        cv.add(sk.capped(cv, f"{COLOUR[side]} · {'house' if side == HOUSE else 'github'}", x0, yy + mini / 2 + 3, 7.5,
                         6, px - 4 - RACK_GAP - x0, ls=.6, role="muted")[0])
        left = st["left"][side]
        chip = sk.chip(f"{left}", "", size=7.5, lab="accent" if left else "label")
        room_ = x1 - px - chip.w - 14
        pitch = min(mini * .56, (room_ - 8) / EACH)
        r = min(pitch * .46, mini * .3)
        sk.tray(cv, px - 4, yy - 1, EACH * pitch + 8, mini + 2)
        cy = yy + mini / 2
        cv.add("".join(sk.disc(cv, mat, px + 2 + i * pitch + pitch / 2, cy, 0, r=r) if i < left
                       else sk.slot(px + 2 + i * pitch + pitch / 2, cy) for i in range(EACH)))
        cv.add(chip.draw(cv, px + EACH * pitch + 14, yy + (mini - chip.h) / 2, "left"))
        yy += mini + 7
    return yy


def board_sheet(sk, st, title, desc, variant="wide") -> str:
    return S.board_sheet(sk, sys.modules[__name__], st, title, desc, variant)
