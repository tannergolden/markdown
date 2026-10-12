# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The men's shapes, shared by every theme: a man and a crowned king, each in chess's 45-unit box.

A man is a short cylinder seen from a little above, as chess's pieces are seen standing on their squares: its top
face an ellipse, its ridged side a band under it, its foot where chess's pieces stand, so a man casts the same
shadow a pawn does. A king is two men stacked, as a crowned man is on any table, the upper one carrying a crown on
its face. A skin decides what they are made of.
"""
from __future__ import annotations

import math

from ...lettering import f1

CX, RX, RY, T = 22.5, 16.6, 8.0, 7.2   # the centre, the radii of a face, and a man's thickness
FOOT_Y = 38.6                           # the lowest point of a man's foot, where chess's pieces stand
BASE = FOOT_Y - RY                      # the centre of a man's foot
FACE = BASE - T                         # the centre of a man's face, and of a king's upper man's foot
CROWN_FACE = FACE - T                   # the centre of a king's face
SHADOW = (CX + 2.3, BASE + 1.4, RX + .6, RY + .4)   # the shadow at a man's foot: centre and radii
GROOVE = .6                             # the groove round a face, as a share of the face
# a crown, flattened onto a face seen from above
CROWN = "M-5.6 1.9 -6.4-1.9-3.2 .1 0-3.1 3.2 .1 6.4-1.9 5.6 1.9Z"


def band(face: float) -> str:
    """The side of a man whose face is centred at `face`: down its left, round the front of its foot, up its right
    and back round the front of its face."""
    foot = face + T
    return (f"M{f1(CX - RX)} {f1(face)}V{f1(foot)}A{RX} {RY} 0 0 0 {f1(CX + RX)} {f1(foot)}V{f1(face)}"
            f"A{RX} {RY} 0 0 1 {f1(CX - RX)} {f1(face)}Z")


def ellipse(cy: float, k: float = 1.0) -> str:
    """A face, centred at `cy`, at `k` of its size, as path data."""
    rx, ry = RX * k, RY * k
    return (f"M{f1(CX - rx)} {f1(cy)}A{f1(rx)} {f1(ry)} 0 1 0 {f1(CX + rx)} {f1(cy)}"
            f"A{f1(rx)} {f1(ry)} 0 1 0 {f1(CX - rx)} {f1(cy)}Z")


def ridges(face: float, n: int = 15) -> list[tuple[float, float, float]]:
    """The ridges round a man's side, as its edge is milled: a line down the band at each, spaced as a turned part's
    shading is, closer toward its sides; each (x, top, bottom) with how far round it is, from the left."""
    out = []
    for i in range(1, n):
        a = math.pi * i / n
        x = CX - RX * math.cos(a)
        e = RY * math.sin(a)
        out.append((x, face + e, face + T + e))
    return out


def silhouette(king: bool) -> str:
    """A man's outline, or a king's, as one path: what a clip or a phantom uses."""
    top = CROWN_FACE if king else FACE
    return (f"M{f1(CX - RX)} {f1(top)}V{f1(BASE)}A{RX} {RY} 0 0 0 {f1(CX + RX)} {f1(BASE)}V{f1(top)}"
            f"A{RX} {RY} 0 0 0 {f1(CX - RX)} {f1(top)}Z")
