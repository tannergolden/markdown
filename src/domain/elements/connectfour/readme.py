# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries under the Connect Four sheet: every open column as a move, folded, then the note.

Each drop is named for what it plainly is, never for what it does, as chess's moves are: the disc, the column and the
row it lands on, and what it lands on ("Send Black to the Floor in Column 2!", "Stack Black on White in Column 5!",
"Lay the Sixth Disc in Column 3!"), so a drop that wins and one that changes nothing read alike, and no `+` or `#`
marks one out. The engine writes the names; this draws what goes under the sheet, as chess's does (`games.readme`).
The side to move is signed with the discs it drops, ⚪ for the house's White and ⚫ for GitHub's Black, whichever side the
Arbiter opened for.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import GITHUB, HOUSE
from .game import state

UNIT = ("open column", "open columns")
SIGN = {HOUSE: "⚪", GITHUB: "⚫"}          # the house's first, as every pair of sides is said


def text(d: dict) -> str:
    """What the README carries under the board's picture: every open column as a move, folded, then the note."""
    return R.text(d, state(d), SIGN, UNIT)
