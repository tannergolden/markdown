# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tic-Tac-Toe's motion: chess's choreography (`chess.motion`), and the beats of a mark drawn by hand.

The board's edge is drawn in as chess's is and the panel rises a section at a time on chess's beats. The last
mark draws itself, stroke by stroke, as the pen would: the X's two strokes one after the other, the O in one sweep;
its cell is marked as the pen lifts; a threat's mark blooms as chess's check does; and a won line is struck through
once the winning mark is down. Every animated attribute holds its resting value, so a file is complete without SMIL,
and inside `at_rest()` nothing moves at all: the still files.
"""
from __future__ import annotations

from ..chess.motion import ani, appear, at_rest, moving, rise, risen, stroke_in, wiped  # noqa: F401  (chess's)

DRAW_AT, DRAW = .45, .8          # the last mark: when the pen touches down, and how long the mark takes
LIFT = DRAW_AT + DRAW            # the pen lifts: the cell is marked
STRIKE_AT, STRIKE = 1.5, .5      # a won line: when its strike starts, and how long it takes
