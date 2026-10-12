# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Connect Four element: the second tier of the games on @tannergolden's profile, drawn as chess is drawn.

  connectfour  the frame as it stands and the state of play beside it, with every open column named in the README

About 4.5 trillion positions, solved in 1988: whoever drops the first disc can force a win with perfect play, so the
Arbiter opens every game, for a side drawn at random, with a random move, and that side drops the dark discs.
Nothing here assumes which side that is. Its sheet is chess's (`games.sheet`): the same card or drafting sheet,
band, materials and panel, around a frame of its own (`layout`, `shapes`, `skins`) that its last disc falls down as
the file opens (`motion`), with a still file of each for anyone who asks for reduced motion. What it is drawn from
is the profile's own engine's (`game`), and the README's words round it are `readme`'s. It is drawn on that profile
alone.
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
    """One file: `variant` of the frame, by `theme` day or dark, in the page's `tone`."""
    sk = Standard(theme) if tone == STANDARD else Print(theme, tone)
    with M.at_rest(variant.endswith("still")):
        d = describe(d)
        return board_sheet(sk, state(d), d["title"], d["desc"], "narrow" if variant.startswith("narrow") else "wide")
