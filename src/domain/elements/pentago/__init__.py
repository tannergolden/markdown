# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Pentago element: the second tier of the games on @tannergolden's profile, drawn as chess is drawn.

  pentago  the four quarters as they stand and the state of play beside them, with every empty hole and its turns
           named in the README

Six holes by six in four quarters that turn: a move sets a marble and then turns any quarter a quarter turn, and five
in a row wins. The house always plays White and GitHub Black. Under the Ghost Rule each side first sets one ghost, a
marble that is nobody's, the side the Arbiter drew setting first, and then the Arbiter draws which side sets the
first marble, so neither side holds the first move's edge by right. Its sheet is chess's (`games.sheet`): the same
card or drafting sheet, band, materials and panel, around a board of its own (`layout`, `shapes`, `skins`) whose last
quarter turns as the file opens (`motion`), with a still file of each for anyone who asks for reduced motion. What
it is drawn from is the profile's own engine's (`game`), and the README's words round it are `readme`'s. It is drawn
on that profile alone.
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
