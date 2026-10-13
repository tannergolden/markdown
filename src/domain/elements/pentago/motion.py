# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Pentago's motion: chess's choreography (`chess.motion`), and a marble set and a quarter turned.

The board's edge is drawn in as chess's is and the panel rises a section at a time on chess's beats. The last move
plays as it was made: its marble is set in its hole, which is ringed as it settles, with a ripple; then its quarter
turns its quarter turn from where it stood, everything on it turning with it, a ghost too, easing into place, and
the arrow round the quarter's outer corner is drawn the way it went. A won game's five are ringed one after another
once the turn is done, counted off, and joined by a line. Every animated attribute holds its resting value, so a file
is complete without SMIL, and inside `at_rest()` nothing moves at all: the still files.
"""
from __future__ import annotations

from ..chess.motion import ani, appear, at_rest, moving, rise, risen, stroke_in, wiped  # noqa: F401  (chess's)

DROP, LAND = .45, .75            # the marble set in its hole; its hole ringed, with a ripple
TWIST_AT, TWIST = 1.05, .75      # its quarter's quarter turn: when it starts, and how long it takes
TURN_EASE = ".45 0 .25 1"        # the turn eases out as a hand turns a quarter and lets it settle
