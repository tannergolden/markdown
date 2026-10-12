# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries round the Tic-Tac-Toe sheet: the turn's banner, and every open cell as a move, folded.

Chess names its moves as orders to an army; Tic-Tac-Toe is a duel, and names each move as a call across it: "Strike
the Heart!" for the centre, "Parry the Thrust!" for a block, "Touché!" for the win. The engine writes the names;
this draws the block round the sheet, as chess's does (`games.readme`). The side to move is signed with the mark it
plays this game, ❌ for X and ⭕ for O, whichever side the Arbiter opened for.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import other
from .game import state

UNIT = ("open cell", "open cells")


def text(d: dict) -> tuple[str, str]:
    """The board's README block round its picture: what goes above it, and what goes under it."""
    st = state(d)
    return R.text(d, st, {st["x"]: "❌", other(st["x"]): "⭕"}, UNIT)
