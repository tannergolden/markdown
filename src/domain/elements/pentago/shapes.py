# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The quarters' and the marbles' shapes, shared by every theme, each in proportion to a quarter's pitch.

Each quarter is a plate of three holes by three, drawn in plan as a part is, every hole a circle a marble is seen
through, with a margin of plate round them; the four stand with a gap between them, so each can turn. A marble is seen
face on, a coin with a raised rim, a groove inside it and a flat face, a hair of the plate showing round its rim
inside its hole. A ghost is the same marble that is nobody's.
"""
from __future__ import annotations

HOLE = .385      # a hole's radius, in pitches
DISC = .345      # a marble's radius: a little smaller than its hole, so its own rim shows inside it
GROOVE = .215    # the groove round a marble's face
MARGIN = .26     # the plate round the holes
GAP = {"wide": 12, "narrow": 9}   # between the quarters, so each can turn
# Line shading, as on chess's white pieces, across a light marble of radius 1: closer together toward its right.
SHADE = (.18, .38, .55, .69, .8, .88, .94)
