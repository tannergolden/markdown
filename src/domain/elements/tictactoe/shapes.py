# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The marks' shapes, shared by every theme: an X and an O as a pen draws them, each in a 100-unit box.

A mark is its pen strokes, in the order a hand draws them: the X's falling stroke and then its rising one, the O
from the top round to the left and back, a little past where it began, so the last mark drawing itself is drawn as
anyone would draw it. A skin decides what the strokes are made of: the house's X is drawn in outline and shaded, as
chess's white pieces are, GitHub's O in solid ink, as its black ones.
"""
from __future__ import annotations

import math

from ...lettering import f1

PEN = 11.5                       # the stroke's width, in the box
R = 25.5                         # the O's radius


def _at(deg: float, r: float = R) -> str:
    t = math.radians(deg)
    return f"{f1(50 + r * math.cos(t))} {f1(50 + r * math.sin(t))}"


X = ("M26.5 26.5L73.5 73.5", "M73.5 26.5L26.5 73.5")
# from just right of the top, anticlockwise (the angle falling) round twice half way, 380 degrees in all
O = (f"M{_at(-82)}A{R} {R} 0 1 0 {_at(-272)}A{R} {R} 0 1 0 {_at(-462)}",)
LENGTH = {"X": (66.5, 66.5), "O": (2 * math.pi * R * 380 / 360,)}
# where the lamp catches GitHub's O: a short bright arc on its upper left, inside the stroke
SPEC = f"M{_at(-160, R + 2.6)}A{R + 2.6} {R + 2.6} 0 0 1 {_at(-112, R + 2.6)}"
SHADOW = (3.2, 3.8)             # how far a mark's shadow falls, down and to the right, away from the lamp


def strokes(mark: str) -> tuple[str, ...]:
    return X if mark == "X" else O
