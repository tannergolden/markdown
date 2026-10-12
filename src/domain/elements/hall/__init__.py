# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hall of Fame of all four games on @tannergolden's profile: Tic-Tac-Toe, Connect Four, Checkers and Chess.

  hall-of-fame  the series of every game and of all four together, the podium of the five leading winners across
                them with each one's wins by game, and a badge for each winner

Chess-hall grown to four games, drawn in its materials (`skins`, chess's own with every game's pieces added) to one
layout (`layout`), each game named by the pieces it is played with (`marks`). It has a wide file and a phone's, each
moving as it opens and still for anyone who asks for reduced motion. What it is drawn from is the profile's own
engines' (`record`), and the README's badges and leaderboard round it are `readme`'s. It is drawn on that profile
alone.
"""
from __future__ import annotations

from ...prints import STANDARD
from ..chess import motion as M
from .layout import hall_sheet
from .readme import badges, leaderboard
from .record import GAMES, OWNER, TITLES, check, describe, state
from .skins import Print, Standard

__all__ = ["GAMES", "KINDS", "OWNER", "TITLES", "badges", "check", "describe", "draw", "leaderboard", "state",
           "variants"]

KINDS = ("hall-of-fame",)
SHEETS = ("wide", "narrow", "still", "narrow-still")  # each sheet's files: wide and a phone's, moving and still


def variants(kind: str, d: dict) -> tuple[str, ...]:
    """The files the Hall writes: its sheets, and a badge per winner it shows, the leader's with a still twin."""
    if check(d):
        return SHEETS
    n = len(state(d)["people"])
    return SHEETS + (("badge-1", "badge-1-still") if n else ()) + tuple(f"badge-{i}" for i in range(2, n + 1))


def draw(kind: str, d: dict, tone: str, theme: str, variant: str) -> str:
    """One file: `variant` of the Hall, by `theme` day or dark, in the page's `tone`."""
    sk = Standard(theme) if tone == STANDARD else Print(theme, tone)
    shape = "narrow" if variant.startswith("narrow") else "wide"
    with M.at_rest(variant.endswith("still")):
        h = state(d)
        if variant.startswith("badge-"):
            i = int(variant.split("-")[1]) - 1
            return sk.badge_file(i, h["people"][i])
        d = describe(d)
        return hall_sheet(sk, h, d["title"], d["desc"], shape)
