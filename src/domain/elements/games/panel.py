# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The panel beside every game's board, a section at a time, as chess's is: the two sides, the turn, the last move
and the score sheet, with the game's own count between them (`sheet` places them).

Each section is chess's, drawn for any game: the sides are the house and GitHub, each in a medallion holding what
that side plays with (`game.medallion`); the turn is chess's plate, and once the game is over the same plate says
who won and how, with the day the fresh board comes across the row; the last move is written in the game's own
notation, with a mark before it where the notation alone cannot say whose it is (`game.glyph`), or drawn by the
game itself where its notation is more than letters can say, as a Pentago move's quarter turn is (`game.write`), and
its words stand on a line or two of their own under it, as chess's do. Every name, login, number and line of words is
fitted to the room it has, at the largest size that fits, down to a floor, then cut with an ellipsis, so nothing on
a wide sheet or a phone's runs into anything else.
"""
from __future__ import annotations

from ...lettering import f1  # noqa: F401  (the panel's coordinates, as chess's)
from ..chess import layout as CL
from ..chess import motion as M
from ..chess.game import OWNER
from .data import numbered
from .sides import GITHUB, HOUSE, name, other, playing

LEAD = CL.LEAD          # from one line of the last move's words to the next, chess's


# --------------------------------------------------------------------------- the sides
def matchup(cv, sk, g, st, x0, x1, y, *, small=False) -> float:
    """The two sides across one row, the house on the left and GitHub on the right, the side to move ringed; once
    the game is over, neither."""
    r = 15 if not small else 13
    cy = y + r
    gap = 14 if not small else 4            # what each side leaves clear in the middle, for the "vs"
    for side, who in ((HOUSE, f"@{OWNER.upper()}"), (GITHUB, "GITHUB")):
        left = side == HOUSE
        cx = x0 + r + 3 if left else x1 - r - 3
        cv.add(g.medallion(cv, sk, st, cx, cy, r, side))
        if st["to_move"] == side and not st["result"]:
            cv.add(sk.turn_ring(cv, cx, cy, r + 3.4, 1.1))
        tx = cx + r + 11 if left else cx - r - 11
        room = (x1 - x0) / 2 - (2 * r + 14) - gap
        anchor = "start" if left else "end"
        role = "the house" if left else playing(st["players"])
        cv.add(sk.said(cv, who, tx, cy - 2, 10 if not small else 9.5, 8, room, ls=.8, anchor=anchor)[0],
               sk.capped(cv, f"{g.side_name(side, st)}  ·  {role}", tx, cy + 11, 7, 6, room, ls=.55,
                         anchor=anchor)[0])
    if not small:
        cv.add(sk.caps(cv, "vs", (x0 + x1) / 2, cy + 3, 8, ls=1, anchor="middle", what="versus"))
    return y + 2 * r + 3


# --------------------------------------------------------------------------- the turn
def turn_row(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """Whose turn it is, chess's plate under that side, and the day the move is due by on the other; once the game
    is over, the same plate says who won and how, or that it was drawn, with the day the fresh board comes. A plate
    with something to add (a block that must be made, a jump that must be taken, how the game ended) slides that
    panel open out of it as the move lands."""
    if st["result"]:
        return CL.plate_row(cv, sk, x0, x1, y, *CL.finished(st), small=small, keep_note=True)
    notes = (f"due by {st['due']}", f"by {st['due']}") if st["due"] else ("", "")
    return CL.plate_row(cv, sk, x0, x1, y, f"{name(st['to_move'])}'s turn", st["alert"], "play",
                        st["to_move"] == GITHUB, notes, small=small, keep_note=True)


# --------------------------------------------------------------------------- the last move
def last_move(cv, sk, g, st, x0, x1, y, *, small=False) -> float:
    """The last move in notation, its words on a line or two of their own under it, and who played it when;
    before a game's first move, who opens it, or what opens it where the game says (`g.opening`)."""
    last = st["last"]
    big = 22 if not small else 18
    room = x1 - x0
    if last:
        number, move, side, words = numbered(st), last["move"], last["side"], last["words"]
    elif getattr(g, "opening", None):
        number, move, side, words = g.opening(st)
    else:
        number, move, side, words = "1.", "?", st["opens"], f"{name(st['opens'])} opens game {st['game']}"
    cv.add(sk.key(cv, x0, y - 7, 7, "last"), sk.heading(cv, "last move" if last else "first move", x0 + 12, y))
    base = y + 12 + big * .74
    head = f"{number} "
    cv.add(sk.say(cv, head, x0, base, big, role="strong", what="move"))
    x = x0 + sk.width(head, "bold", big)
    if getattr(g, "write", None) and last:
        g.write(cv, sk, st, side, move, x, base, big, role="strong")
    else:
        glyph = g.glyph if last else getattr(g, "opening_glyph", None) or g.glyph   # before the first move, its own
        if glyph:
            mark, w = glyph(cv, sk, st, side, x, base, big)
            cv.add(mark)
            x += w
        cv.add(sk.said(cv, move, x, base, big, 14, x0 + room - x, role="strong")[0])
    rows, size, lines = CL.flowed(sk, words, room, small=small)
    top = y + 12 + big + (14 if not small else 13)
    for i, line in enumerate(lines):
        cv.add(sk.say(cv, line, x0, top + i * LEAD, size, face="regular", what="move in words"))
    # who played it, and when: the login cut short before the day is, if it comes to that
    yy = top + (rows - 1) * LEAD + (17 if not small else 15)
    if last:
        when = f"  ·  {last['when']}"
        bs = CL.fit(sk, f"by {last['by']}{when}", "caps", 7.5, 6.5, room, .6)
        by = CL.cut(sk, f"by {last['by']}", "caps", bs, room, .6, tail=when)
    else:
        by, bs = g.first(st), 7.5
    cv.add(sk.caps(cv, by, x0, yy, bs, ls=.6))
    return yy + (9 if not small else 10)


# --------------------------------------------------------------------------- the score sheet
def rows_of(st) -> list:
    """The score sheet's rows, the move to come included: on a board before its first move, that one alone."""
    shown = list(st["history"])
    if not shown:
        shown = [(1, "", "", "")]
    return shown


def history(cv, sk, g, st, x0, x1, y, rows=3, *, small=False) -> float:
    """The last moves, each side's under the side that played it, who chose each of GitHub's, the latest move's row
    marked, and whose turn the next one is; once the game is over, who won it in that place."""
    cv.add(sk.heading(cv, "moves", x0, y))
    yy = y + 21
    due = CL.outcome(st) if st["result"] else f"{name(st['to_move'])}'s turn"
    said = "ink" if st["result"] else "alert"      # a result is said in the ink; a turn calls out in red
    latest = st["last"]["number"] if st["last"] else None
    shown = rows_of(st)[-rows:]
    first, reply = st["opens"], other(st["opens"])

    def cell_w(text):
        if getattr(g, "write", None):
            return g.written(sk, text, 10)
        return sk.width(text, "bold", 10) + (g.glyph_width(10) if g.glyph else 0)

    nw = max(26.0, max(sk.width(f"{n}.", "caps", 8, .3) for n, *_ in shown) + 9)
    mw = max([cell_w(m) for _, a, b, _ in shown for m in (a, b) if m] + [0])
    col = max(56.0, mw + 14)
    if x0 + nw + 2 * col + 72 > x1:      # a long jump's row: the moves give way, fitted, so the login keeps its room
        col = max(56.0, (x1 - x0 - nw - 72) / 2)
    ax, bx = x0 + nw, x0 + nw + col
    for n, a, b, who in shown:
        if n == latest:
            cv.add(sk.row_mark(x0 - 6, yy - 12.5, x1 - x0 + 6, 18))
        cv.add(sk.caps(cv, f"{n}.", x0, yy, 8, ls=.3, what="move number"))
        wx = bx + col                     # who chose GitHub's move: after the row's moves, whichever side opened
        for text, side, cx in ((a, first, ax), (b, reply, bx)):
            if not text:
                label, w = sk.capped(cv, due, cx, yy, 7, 6, (x1 - cx) - (80 if who else 0), ls=.5, role=said)
                cv.add(label)
                wx = max(wx if cx == bx else 0, cx + w + 12)
                break
            if getattr(g, "write", None):
                g.write(cv, sk, st, side, text, cx, yy, 10)
                continue
            if g.glyph:
                mark, w = g.glyph(cv, sk, st, side, cx, yy, 10)
                cv.add(mark)
                cx += w
            cv.add(sk.said(cv, text, cx, yy, 10, 7.5, col - 8)[0])
        if who:
            cv.add(sk.capped(cv, who, wx, yy, 7, 6, x1 - wx, ls=.5)[0])
        yy += 19
    return yy


# --------------------------------------------------------------------------- the panel
def panel(cv, sk, g, st, x0, x1, y, *, small=False) -> float:
    """The panel, a section at a time, each rising into place in turn as chess's does; returns where it ends."""
    y = M.risen(cv, .15, matchup, cv, sk, g, st, x0, x1, y, small=small)
    y = turn_row(cv, sk, st, x0, x1, y + (12 if small else 14), small=small)
    cv.add(sk.rule(x0, x1, y + (14 if small else 16)))
    y = M.risen(cv, .3, last_move, cv, sk, g, st, x0, x1, y + (34 if small else 36), small=small)
    cv.add(sk.rule(x0, x1, y - (2 if small else 4)))
    count = CL.countdown if st.get("countdown") else g.count   # a final board counts down to the next game
    y = M.risen(cv, .45, count, cv, sk, st, x0, x1, y + (18 if small else 16), small=small)
    cv.add(sk.rule(x0, x1, y + 1))
    return M.risen(cv, .6, history, cv, sk, g, st, x0, x1, y + 21, rows=2 if small else 3, small=small)
