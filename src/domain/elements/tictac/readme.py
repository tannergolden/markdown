# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries under the Tic-Tac sheet: every square the side to move can take as a move, folded, then
the note.

Each move is named as players name it, for the kind of square its mark takes in its board and never for what it does
("Centre Move", "Corner Move", "Edge Move"), and under the Ghost Rule for the kind of square a ghost would lock ("Centre
Ghost"), so a mark that wins and a quiet one read alike and no `+` or `#` marks one out; its words say where it goes.
The engine writes the names; this draws what goes under the sheet, as chess's does (`games.readme`). A turn with more
than ten moves, any open board's or a ghost's, is grouped by board, the board as it is read, top row first, as chess
groups its moves by piece. The side to move is signed with the mark it plays, ❌ for the house's X and ⭕ for GitHub's O,
whichever side the Arbiter drew.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import GITHUB, HOUSE
from .game import MOVE, PLACE, board_of, state

UNIT = ("open square", "open squares")
GHOSTS = ("square to lock", "squares to lock")
SIGN = {HOUSE: "❌", GITHUB: "⭕"}          # the house's first, as every pair of sides is said
READING = [(bx, by) for by in (2, 1, 0) for bx in range(3)]   # the boards as the big board is read


def cell_of(notation: str) -> str:
    return notation if notation[0] not in "XO" else notation[1:3]


def groups(moves: list) -> list[tuple[str, list]]:
    """The moves by board, each board's in the order the engine listed them, the boards as the big board is read."""
    out = []
    for b in READING:
        rows = [move for move in moves if MOVE.fullmatch(str(move[2])) and board_of(cell_of(move[2])) == b]
        if rows:
            out.append((f"{PLACE[b].title()} Board", rows))
    return out


def text(d: dict) -> str:
    """What the README carries under the board's picture: every square the side to move can take, folded, then the
    note."""
    st = state(d)
    return R.text(d, st, SIGN, GHOSTS if st["ghosting"] else UNIT, groups)
