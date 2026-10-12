# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Connect Four's motion: chess's choreography (`chess.motion`), and a disc that falls.

The frame's edge is drawn in as chess's board edge is and the panel rises a section at a time on chess's beats.
The last disc is held over its column, let go, and falls down it under gravity, glimpsed through each hole it
passes behind, then lands with a bounce and a smaller one and settles; its hole is ringed as it lands. A won game's
four are ringed one after another, counted off, and joined by a line. Every animated attribute holds its resting
value, so a file is complete without SMIL, and inside `at_rest()` nothing moves at all: the still files.
"""
from __future__ import annotations

import math

from ...lettering import f1, fx
from ..chess.motion import ani, appear, at_rest, moving, rise, risen, stroke_in, wiped  # noqa: F401  (chess's)

HOLD, LET_GO = .2, .5      # the disc appears over its column, and is let go
G = 2100.0                 # gravity, in pixels a second a second: the longest fall takes about half a second
BOUNCE = (.17, .05)        # how high it bounces, then bounces again, in pitches
FALL = ".333 0 .667 .333"  # a fall from rest, quickening: the curve of t squared
RISE = ".333 .667 .667 1"  # a rise to rest, slowing


def fall_time(distance: float) -> float:
    return math.sqrt(2 * max(distance, 1) / G)


def drop(distance: float, pitch: float) -> tuple[str, float]:
    """The last disc's fall from `distance` above where it rests: the animations its group holds, and when it
    lands. It is held, let go, falls, and bounces twice before it settles."""
    tf = fall_time(distance)
    hops = [(b * pitch, fall_time(b * pitch)) for b in BOUNCE]
    times = [0, LET_GO, LET_GO + tf]
    values = [f"0 {f1(-distance)}", f"0 {f1(-distance)}", "0 0"]
    splines = ["0 0 1 1", FALL]
    t = LET_GO + tf
    for h, th in hops:
        times += [t + th, t + 2 * th]
        values += [f"0 {f1(-h)}", "0 0"]
        splines += [RISE, FALL]
        t += 2 * th
    dur = t
    keys = ";".join(fx(x / dur, 3) for x in times)
    move = ani("transform", ";".join(values), keys, dur, spline=";".join(splines), kind="animateTransform",
               typ="translate")
    show = ani("opacity", "0;0;1;1", f"0;{fx(HOLD / dur, 3)};{fx((HOLD + .18) / dur, 3)};1", dur)
    return move + show, LET_GO + tf
