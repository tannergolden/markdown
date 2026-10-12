# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries round the Checkers sheet: the turn's banner, and every legal move, folded.

Each move is named in checkers' own words for what it is, never for what it does, as chess's are: a man's step ("Push
the Man From 9 to 13!"), a jump and the men it takes ("Jump the Man on 11!"), a man crowned ("Crown the Man From 6 on
1!"), with no opening's name and nothing of what follows. The engine writes the names; this draws the block round the
sheet, as chess's does (`games.readme`). The side to move is signed with its men, ⛀ for the house's White and ⛂ for GitHub's Black. A turn with
more than ten moves is grouped as chess groups its moves by piece: the men's, then the kings', each named for as many as
have a move in it.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import GITHUB, HOUSE
from .game import path, state

UNIT = ("legal move", "legal moves")
SIGN = {HOUSE: "⛀", GITHUB: "⛂"}          # the house's first, as every pair of sides is said


def grouped(pieces: dict):
    """How a long list of moves is grouped: by what makes each move, a man or a king, read from the square it
    leaves; each group named for one or several, as many as there are squares its moves leave from."""
    def groups(moves: list) -> list[tuple[str, list]]:
        out = []
        for king, one, many in ((False, "Man", "Men"), (True, "King", "Kings")):
            rows = [m for m in moves if pieces.get(path(m[2])[0], "").isupper() == king]
            if rows:
                out.append((many if len({path(m[2])[0] for m in rows}) > 1 else one, rows))
        return out
    return groups


def text(d: dict) -> tuple[str, str]:
    """The board's README block round its picture: what goes above it, and what goes under it."""
    st = state(d)
    return R.text(d, st, SIGN, UNIT, grouped(st["pieces"]))
