# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The Tic-Tac element: the first tier of the games on @tannergolden's profile, drawn as chess is drawn.

  tictac  the nine boards as they stand and the state of play beside it, with every open square named in the README

Tic-Tac-Toe on nine boards at once, the game also known as Ultimate Tic-Tac-Toe: where a mark goes in its board sends
the other side to the board in that place, three in a row wins a board, and three boards in a row wins the game.
The house always plays X and GitHub O. Under the Ghost Rule each side first locks one square with a ghost, the side
the Arbiter drew placing first, and then the Arbiter draws which side makes the first mark, so neither side holds
the first move's edge by right. Its sheet is chess's (`games.sheet`): the same card or drafting sheet, band,
materials and panel, around a board of its own (`layout`) and its marks (`shapes`, `skins`), drawn by hand as the
file opens (`motion`), with a still file of each for anyone who asks for reduced motion. What it is drawn from is the
profile's own engine's (`game`), and the README's words round it are `readme`'s. It is drawn on that profile alone.
"""
from __future__ import annotations

from ...prints import STANDARD
from . import motion as M
from .game import KIND, check, describe, placement, state
from .layout import board_sheet
from .readme import text
from .skins import Print, Standard

__all__ = ["KIND", "KINDS", "SHEETS", "check", "describe", "draw", "placement", "state", "text", "variants"]

KINDS = (KIND,)
SHEETS = ("wide", "narrow", "still", "narrow-still")  # each sheet's files: wide and a phone's, moving and still


def variants(kind: str, d: dict) -> tuple[str, ...]:
    return SHEETS


def draw(kind: str, d: dict, tone: str, theme: str, variant: str) -> str:
    """One file: `variant` of the board, by `theme` day or dark, in the page's `tone`."""
    sk = Standard(theme) if tone == STANDARD else Print(theme, tone)
    with M.at_rest(variant.endswith("still")):
        d = describe(d)
        return board_sheet(sk, state(d), d["title"], d["desc"], "narrow" if variant.startswith("narrow") else "wide")
