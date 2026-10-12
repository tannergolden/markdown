# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries round the Tic-Tac-Toe sheet: the turn's banner, and every open cell as a move, folded.

Each move is named for what it is, never for what it does: the cell its mark takes and where the other marks stand
round it, in plain geometric words ("Take the Centre by Their Corner!", "Take the Corner Across From Theirs!"), with a
title of its own across the whole game, so a winning mark and a quiet one read alike and no `+` or `#` marks one out.
The engine writes the names; this draws the block round the sheet, as chess's does (`games.readme`).
The side to move is signed with the mark it plays, ❌ for the house's X and ⭕ for GitHub's O, whichever side the Arbiter
opened for.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import GITHUB, HOUSE
from .game import state

UNIT = ("open cell", "open cells")
SIGN = {HOUSE: "❌", GITHUB: "⭕"}          # the house's first, as every pair of sides is said


def text(d: dict) -> tuple[str, str]:
    """The board's README block round its picture: what goes above it, and what goes under it."""
    return R.text(d, state(d), SIGN, UNIT)
