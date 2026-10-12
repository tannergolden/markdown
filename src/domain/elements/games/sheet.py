# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A game's board sheet, wide and a phone's, drawn as chess's is: the same card or drafting sheet and its band, the
board in the same place at the same size, and beside it (under it, on a phone) the same panel a section at a time.

A game is a module that answers what its sheet needs (see `Game`): its kind and name, the mark in its band, its
board, what each side plays with, how its moves are written and what it counts. Every coordinate and beat here is
chess's, so the four sheets stand the same on a page, in the standard theme and in every print. A sheet is as tall
as its board and its panel need, the same in every theme.
"""
from __future__ import annotations

from typing import Callable, Protocol

from ...lettering import Lettering
from ..chess import motion as M
from ..chess.game import OWNER
from . import panel as P

WIDE, NARROW = 830, 360
BAND, PAD = 40, 20          # the head's depth and the sheet's margin, chess's
BOARD = {"wide": 368, "narrow": 296}   # the square chess's board fills: 8 squares of 46, and of 37 on a phone


class Game(Protocol):
    KIND: str                                   # the element's kind, as its files are stamped
    LABEL: str                                  # its name in the band
    glyph: Callable | None                      # the mark before a move where the notation cannot say whose it is
    glyph_width: Callable | None                # the room that mark takes, at a size

    def band_mark(self, x: float, y: float, size: float, paper: str, block: str = "") -> str: ...
    def room(self, x0: float, y0: float, n: float) -> tuple: ...
    def height(self, n: float, small: bool = False) -> float: ...
    def board(self, cv, sk, st: dict, x0: float, y0: float, n: float, *, small: bool = False) -> None: ...
    def medallion(self, cv, sk, st: dict, cx: float, cy: float, r: float, side: str) -> str: ...
    def side_name(self, side: str, st: dict) -> str: ...
    def first(self, st: dict) -> str: ...
    def count(self, cv, sk, st: dict, x0: float, x1: float, y: float, *, small: bool = False) -> float: ...


class Measured(Lettering):
    """Lettering that sets nothing: a sheet measures its panel's height on it before it draws the panel."""

    def text(self, s, **k) -> str:
        return ""


def measure(sk, W: float, title: str, desc: str):
    """A canvas to draw the panel on once, to learn where it ends, without a letter set."""
    cv = sk.new(W, 100, title, desc, "")
    cv.L = Measured()
    return cv


def board_sheet(sk, g, st: dict, title: str, desc: str, variant: str = "wide") -> str:
    still = "" if M.MOTION else " still"
    if variant == "wide":
        W, n = WIDE, BOARD["wide"]
        x0, y0 = PAD + 18, BAND + 22
        px0, px1 = x0 + n + 32, W - PAD
        end = P.panel(measure(sk, W, title, desc), sk, g, st, px0, px1, y0 + 1)
        H = max(y0 + n + 22, end + 8) + PAD
        cv = sk.new(W, H, title, desc, f"elements {g.KIND} wide", still)
        sk.frame(cv, W, H, g.LABEL, g.band_mark, f"game {st['game']}  ·  move {st['move']}", f"@{OWNER} vs. github",
                 plain=[g.room(x0, y0, n)])
        g.board(cv, sk, st, x0, y0, n)
        cv.add(sk.vrule(px0 - 16, y0, y0 + n))
        P.panel(cv, sk, g, st, px0, px1, y0 + 1)
        return cv.svg()
    W, n = NARROW, BOARD["narrow"]
    x0, y0 = PAD + 14, BAND + 18
    top = y0 + g.height(n, True) + 30
    px0, px1 = PAD, W - PAD
    end = P.panel(measure(sk, W, title, desc), sk, g, st, px0, px1, top, small=True)
    H = end + 8 + PAD
    cv = sk.new(W, H, title, desc, f"elements {g.KIND} narrow", still)
    sk.frame(cv, W, H, g.LABEL, g.band_mark, f"move {st['move']}", plain=[g.room(x0, y0, n)])
    g.board(cv, sk, st, x0, y0, n, small=True)
    P.panel(cv, sk, g, st, px0, px1, top, small=True)
    return cv.svg()
