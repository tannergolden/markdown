# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The frame's and the discs' shapes, shared by every theme, each in proportion to the frame's pitch.

The frame stands upright, drawn in elevation as a part is: a plate of seven columns by six rows, every hole a circle
the discs are seen through, on two legs that stand on the ground. A disc is a coin with a raised rim, a groove
inside it and a flat face; behind the plate only what a hole shows of it is seen, as on the real thing,
a hair of the paper behind showing round its rim.
"""
from __future__ import annotations

HOLE = .385      # a hole's radius, in pitches
DISC = .345      # a disc's radius: a little smaller than its hole, so its own rim shows inside it
GROOVE = .215    # the groove round a disc's face
MARGIN = .26     # the plate round the holes
LEG = .5         # a leg's height under the plate, and its width
# Line shading, as on chess's white pieces, across a light disc of radius 1: closer together toward its right.
SHADE = (.18, .38, .55, .69, .8, .88, .94)
