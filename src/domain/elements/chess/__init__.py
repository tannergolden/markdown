# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess elements: the game on @tannergolden's profile and its Hall of Fame, drawn in every theme.

  chess       the board as it stands and the state of play beside it, with every legal move named in the README
  chess-hall  the series between the house and GitHub, the podium and everyone who has won, with a badge each

One layout (`layout`) in two materials (`skins`): the standard theme's enamel and a print's drawing, so the sheets
stand the same in every theme and only what they are made of changes. Each sheet has a wide file and a phone's,
each moving as it opens and still for anyone who asks for reduced motion (`motion`). What they are drawn from is
the profile's own engine's (`game`), and the README's words round them are `readme`'s. Both are drawn on that
profile alone.
"""
from __future__ import annotations

from ...prints import STANDARD
from . import motion as M
from .game import (OWNER, PEOPLE, board_state, captured, check, check_hall, describe, describe_hall, hall_state,
                   placement)
from .layout import board_sheet, hall_sheet
from .readme import badges, text
from .skins import Print, Standard

__all__ = ["OWNER", "PEOPLE", "badges", "board_state", "captured", "check", "check_hall", "describe",
           "describe_hall", "draw", "hall_state", "placement", "text", "variants"]

KINDS = ("chess", "chess-hall")
SHEETS = ("wide", "narrow", "still", "narrow-still")  # each sheet's files: wide and a phone's, moving and still


def variants(kind: str, d: dict) -> tuple[str, ...]:
    """The files a chess element writes: its sheets, and for the Hall of Fame a badge per winner, the leader's
    with a still twin."""
    if kind == "chess" or check_hall(d):
        return SHEETS
    n = len(d.get("people") or [])
    return SHEETS + (("badge-1", "badge-1-still") if n else ()) + tuple(f"badge-{i}" for i in range(2, n + 1))


def draw(kind: str, d: dict, tone: str, theme: str, variant: str) -> str:
    """One file: `variant` of the `kind` element, by `theme` day or dark, in the page's `tone`."""
    sk = Standard(theme) if tone == STANDARD else Print(theme, tone)
    shape = "narrow" if variant.startswith("narrow") else "wide"
    with M.at_rest(variant.endswith("still")):
        if kind == "chess":
            d = describe(d)
            return board_sheet(sk, board_state(d), d["title"], d["desc"], shape)
        h = hall_state(d)
        if variant.startswith("badge-"):
            i = int(variant.split("-")[1]) - 1
            return sk.badge_file(i, h["people"][i])
        d = describe_hall(d)
        return hall_sheet(sk, h, d["title"], d["desc"], shape)
