# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""Tic-Tac's motion: chess's choreography (`chess.motion`), and the beats of a mark drawn by hand.

The board's edge is drawn in as chess's is and the panel rises a section at a time on chess's beats. The last
mark draws itself, stroke by stroke, as the pen would: the X's two strokes one after the other, the O in one sweep;
its square is boxed as the pen lifts. A mark that wins its board strikes the board's three, and then the board's own
mark is drawn across it, as large as the board, by the same pen; a mark that wins the game strikes the three boards
once the third board's mark is down. The board the next mark is sent to is bracketed last, once the pen has done. A
ghost just placed appears in its square as the pen would touch down. Every animated attribute holds its resting
value, so a file is complete without SMIL, and inside `at_rest()` nothing moves at all: the still files.
"""
from __future__ import annotations

from ..chess.motion import ani, appear, at_rest, moving, rise, risen, stroke_in, wiped  # noqa: F401  (chess's)

DRAW_AT, DRAW = .45, .8          # the last mark: when the pen touches down, and how long the mark takes
LIFT = DRAW_AT + DRAW            # the pen lifts: the square is boxed
STRIKE_AT, STRIKE = 1.5, .5      # a won board's three: when the strike starts, and how long it takes
CLAIM_AT = STRIKE_AT + STRIKE + .05   # a won board's own mark, drawn across it once its three are struck
WIN_AT = CLAIM_AT + DRAW + .2         # the game's three boards struck, once the third board's mark is down
