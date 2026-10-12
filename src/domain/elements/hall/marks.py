# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Each game's pieces, as the Hall draws them, shared by every theme: one set of outlines in chess's 45-unit box.

The Hall names every game by what it is played with, its two pieces in the order their colours move, the first on the
left: an X and then an O as a pen draws them, a dark disc and then a light one as Connect Four's frame holds them, a
dark man and then a light one standing as a checkers man stands on its square, and chess's own kings, the white and
then the black. A game's colours never change, but who plays them can: in Tic-Tac-Toe and Connect Four the Arbiter
opens for a side drawn at random, so the house plays X or O, the dark discs or the light, from game to game. So a mark
names the game alone, never a side, and is the same whoever won. Each piece is drawn as its game's board draws it, at
the Hall's size: the X and the O as pen strokes with a body, a disc as a coin with a groove round its face, a man as
a short milled cylinder seen from a little above, its foot where a chessman's is. A skin decides what they are made
of: lit enamel in the standard theme, ink and line shading on a print.
"""
from __future__ import annotations

import math

from ...lettering import f1

# Each game's two pieces in the order its colours move, as the materials they are made of: light is a white chessman's,
# paper edged in ink, and dark a black one's. X moves first, then O; the dark discs drop first, then the light; the
# dark men move first, then the light; White moves first, then Black.
MOVE_ORDER = {"tictactoe": ("light", "dark"), "connectfour": ("dark", "light"), "checkers": ("dark", "light"),
              "chess": ("light", "dark")}
# The pen's two marks: X drawn as a light piece is and O as a dark one, so the pair reads as two pieces of a set do.
MARKS = {"light": "X", "dark": "O"}
STEP = .58                 # how far a game's second piece stands to the right of its first, as a share of one
CY = 23.5                  # the middle of a flat piece, an X, an O or a disc, in the box
PEN, RING = 5.6, 11.2      # an X's and an O's stroke, and the O's radius
DISC, GROOVE = 14.2, 8.9   # a disc's radius and its groove's
# A man, as Checkers draws one: the centre of its faces, their radii, its thickness and its foot, where a chessman's is.
CX, RX, RY, T, FOOT = 22.5, 16.6, 8.0, 7.2, 38.6
BASE = FOOT - RY           # the centre of a man's foot
FACE = BASE - T            # the centre of its face
# Line shading on a light piece, as on chess's white pieces: lines down it, closer together toward its right.
SHADE = (.18, .38, .55, .69, .8, .88, .94)


def stroke(x1: float, y1: float, x2: float, y2: float, w: float) -> str:
    """A pen stroke from one point to another, `w` wide with round ends, as an outline a clip can use."""
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    px, py = -dy / n * w / 2, dx / n * w / 2
    r = f1(w / 2)
    return (f"M{f1(x1 + px)} {f1(y1 + py)}L{f1(x2 + px)} {f1(y2 + py)}A{r} {r} 0 0 0 {f1(x2 - px)} {f1(y2 - py)}"
            f"L{f1(x1 - px)} {f1(y1 - py)}A{r} {r} 0 0 0 {f1(x1 + px)} {f1(y1 + py)}Z")


def circle(cx: float, cy: float, r: float, sweep: int = 0) -> str:
    """A circle as path data, two half arcs, wound one way or the other."""
    return (f"M{f1(cx - r)} {f1(cy)}A{f1(r)} {f1(r)} 0 1 {sweep} {f1(cx + r)} {f1(cy)}"
            f"A{f1(r)} {f1(r)} 0 1 {sweep} {f1(cx - r)} {f1(cy)}Z")


def ellipse(cy: float, k: float = 1.0) -> str:
    """A man's face, centred at `cy`, at `k` of its size, as path data."""
    rx, ry = RX * k, RY * k
    return (f"M{f1(CX - rx)} {f1(cy)}A{f1(rx)} {f1(ry)} 0 1 0 {f1(CX + rx)} {f1(cy)}"
            f"A{f1(rx)} {f1(ry)} 0 1 0 {f1(CX - rx)} {f1(cy)}Z")


# The pen marks' bodies: the X's two strokes, and the O's ring, its inner edge wound the other way.
BODY = {"X": stroke(11.4, 12.4, 33.6, 34.6, PEN) + stroke(33.6, 12.4, 11.4, 34.6, PEN),
        "O": circle(22.5, CY, RING + PEN / 2) + circle(22.5, CY, RING - PEN / 2, 1)}
# Where the lamp catches an O: a short bright arc on its upper left, along the stroke's middle.
O_SPEC = (f"M{f1(22.5 + RING * math.cos(math.radians(-160)))} {f1(CY + RING * math.sin(math.radians(-160)))}"
          f"A{RING} {RING} 0 0 1 {f1(22.5 + RING * math.cos(math.radians(-112)))} "
          f"{f1(CY + RING * math.sin(math.radians(-112)))}")
# A disc's glint: a short arc on its upper left, between its rim and its groove.
_G = (DISC + GROOVE) / 2 + 1.1
DISC_SPEC = (f"M{f1(22.5 + _G * math.cos(math.radians(-165)))} {f1(CY + _G * math.sin(math.radians(-165)))}"
             f"A{f1(_G)} {f1(_G)} 0 0 1 {f1(22.5 + _G * math.cos(math.radians(-112)))} "
             f"{f1(CY + _G * math.sin(math.radians(-112)))}")


def band() -> str:
    """A man's milled side: down its left, round the front of its foot, up its right and back round its face."""
    return (f"M{f1(CX - RX)} {f1(FACE)}V{f1(BASE)}A{RX} {RY} 0 0 0 {f1(CX + RX)} {f1(BASE)}V{f1(FACE)}"
            f"A{RX} {RY} 0 0 1 {f1(CX - RX)} {f1(FACE)}Z")


def silhouette() -> str:
    """A man's whole outline, its face and its side, as one path: what a clip uses."""
    return (f"M{f1(CX - RX)} {f1(FACE)}V{f1(BASE)}A{RX} {RY} 0 0 0 {f1(CX + RX)} {f1(BASE)}V{f1(FACE)}"
            f"A{RX} {RY} 0 0 0 {f1(CX - RX)} {f1(FACE)}Z")


def ridges(n: int = 13) -> list[tuple[float, float, float]]:
    """The ridges round a man's side, as its edge is milled: (x, top, bottom), spaced as a turned part's shading is,
    closer toward its sides."""
    out = []
    for i in range(1, n):
        a = math.pi * i / n
        e = RY * math.sin(a)
        out.append((CX - RX * math.cos(a), FACE + e, FACE + T + e))
    return out


def shade_lines(cx: float, half: float, top: float, bottom: float) -> str:
    """Line shading down a light piece `half` wide either side of `cx`: closer together toward its right."""
    return "".join(f"M{f1(cx + k * half)} {f1(top)}V{f1(bottom)}" for k in SHADE)

