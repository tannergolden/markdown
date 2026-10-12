# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries round the Connect Four sheet: the turn's banner, and every open column as a move, folded.

Chess names its moves as orders to an army on the ground; Connect Four's come from the sky, each disc a paratrooper
dropped down a column: "Green Light, Go!" for the first, "Hold the Drop Zone!" for the centre, "Plug the Gap!" for
a block, "Link Up, All Four!" for the win. The engine writes the names; this draws the block round the sheet, as
chess's does (`games.readme`). The side to move is signed with the discs it drops, ⚪ for the house's White and ⚫
for GitHub's Black, whichever side the Arbiter opened for.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import GITHUB, HOUSE
from .game import state

UNIT = ("open column", "open columns")
SIGN = {HOUSE: "⚪", GITHUB: "⚫"}          # the house's first, as every pair of sides is said


def text(d: dict) -> tuple[str, str]:
    """The board's README block round its picture: what goes above it, and what goes under it."""
    return R.text(d, state(d), SIGN, UNIT)
