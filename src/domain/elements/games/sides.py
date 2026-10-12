# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The two sides of every game on the profile: the house, @tannergolden, and GitHub, everyone else.

Chess names its sides white and black, and the house plays white. A game beside it names them as they are, the
house and GitHub, and each game says what each side plays with that game: X or O, the dark discs or the light, the
dark men or the light. Which side moves first is the game's own: the house opens Checkers, and the Arbiter opens
Tic-Tac-Toe and Connect Four for a side drawn at random, which then plays X or the dark discs. The house stands on
the left of the panel, as chess's White does, whichever it plays. A game's colours never change, only who plays
which side: X is always drawn light and O dark, as the dark discs and the dark men are always dark.
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
