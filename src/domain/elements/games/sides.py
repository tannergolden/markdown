# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The two sides of every game on the profile: the house, @tannergolden, and GitHub, everyone else.

Each side's colour is fixed in every game, and only who moves first changes. The house always plays White in Chess,
Checkers and Pentago, and X in Tic-Tac; GitHub always plays Black, or O. Which side moves first is the game's own:
the house opens Chess, GitHub opens Checkers, since Black moves first there, and under the Ghost Rule the Arbiter
draws who opens Tic-Tac and Pentago once each side has set its ghost. Every pair of sides is said the house's first,
and the house stands on the left of the panel, as chess's White does.
"""
from __future__ import annotations

from ..chess.game import GITHUB, HOUSE, SIDES, called

__all__ = ["GITHUB", "HOUSE", "SIDES", "name", "other", "playing"]


def name(side: str) -> str:
    """A side by name: GitHub, or the house's own login."""
    return called(side)


def other(side: str) -> str:
    return GITHUB if side == HOUSE else HOUSE


def playing(n: int) -> str:
    """How many have played for GitHub, as the matchup says it."""
    return f"{n} player{'s' if n != 1 else ''}" if n else "everyone else"
