# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Checkers' motion: chess's choreography (`chess.motion`), and a man that slides, hops and is crowned.

The board's edge is plotted in as chess's is and the panel rises a section at a time on chess's beats. The last
move's man starts when chess's piece does: a step slides it across, lifted a little as chess lifts a glide; a jump
hops it over each man it takes, as chess's knight leaps, each taken man fading on its own square as the jumper
passes over it, the jump's path drawn in behind it; it lands when chess's piece would after one hop, later after
more; and a man that reaches the far row is crowned, a second man dropped onto it from above with a bounce. Every
animated attribute holds its resting value, so a file is complete without SMIL, and inside `at_rest()` nothing
moves at all: the still files.
"""
from __future__ import annotations

import math

from ...lettering import f1, fx
from ..chess.motion import ani, appear, at_rest, moving, rise, risen, stroke_in, wiped  # noqa: F401  (chess's)

START = .4                 # the man sets off: chess's piece's beat, a quarter of its leap
SLIDE = .75                # a step, start to landing: chess's glide
HOP, REST = .5, .1         # a jump: each hop, and the pause on each landing
LIFT = {"slide": .12, "hop": .58}   # how high it rises on the way, in squares: chess's glide's, and a knight's
CROWN_DROP, CROWN_H = .22, .55      # the crown's man: when it drops after the landing, and from how many squares



def journey(offsets: list[tuple[float, float]], jump: bool, s: float, lifted: bool = True
            ) -> tuple[str, str, float, list[float]]:
    """The last move's man on its way, through `offsets` (each landing's offset from where it rests, the first its
    starting square, the last (0, 0)): its translation, its lift, when it lands, and when it passes over each man it
    takes. Not `lifted`, the same journey along the board: where its shadow goes."""
    hops = len(offsets) - 1
    leg = HOP if jump else SLIDE
    lift = LIFT["hop" if jump else "slide"] * s if lifted else 0
    times, values, splines, scale, scale_t, passes = [0.0, START], [], ["0 0 1 1"], ["1", "1"], [0.0, START], []
    sx, sy = offsets[0]
    values += [f"{f1(sx)} {f1(sy)}", f"{f1(sx)} {f1(sy)}"]
    t = START
    for i in range(hops):
        (ax, ay), (bx, by) = offsets[i], offsets[i + 1]
        mid = t + leg / 2
        times += [mid, t + leg]
        values += [f"{f1((ax + bx) / 2)} {f1((ay + by) / 2 - lift)}", f"{f1(bx)} {f1(by)}"]
        splines += [".3 0 .6 1", ".4 0 .25 1"]
        scale += ["1.12" if jump else "1.07", "1"]
        scale_t += [mid, t + leg]
        passes.append(mid)
        t += leg
        if i < hops - 1:
            times.append(t + REST)
            values.append(f"{f1(bx)} {f1(by)}")
            splines.append("0 0 1 1")
            scale.append("1")
            scale_t.append(t + REST)
            t += REST
    land = t
    dur = land + .45
    times.append(dur)
    values.append("0 0")
    splines.append("0 0 1 1")
    scale.append("1")
    scale_t.append(dur)
    keys = ";".join(fx(x / dur, 3) for x in times)
    move = ani("transform", ";".join(values), keys, dur, spline=";".join(splines), kind="animateTransform",
               typ="translate")
    grow = ani("transform", ";".join(scale), ";".join(fx(x / dur, 3) for x in scale_t), dur,
               kind="animateTransform", typ="scale")
    return move, grow, land, passes


def fade_at(t: float, dur: float = .18) -> str:
    """A taken man fading on its square as the jumper passes over it, `t` seconds in."""
    end = t + dur
    return ani("opacity", "1;1;0", f"0;{fx(t / end, 3)};1", end)



def crowned(land: float, s: float) -> str:
    """The crown's man, dropped onto the man that reached the far row, `land` seconds in: it falls, bounces once
    and settles."""
    h = CROWN_H * s
    g = 2100.0
    tf = math.sqrt(2 * h / g)
    b = .14 * s
    tb = math.sqrt(2 * b / g)
    at = land + CROWN_DROP
    times = [0, at, at + tf, at + tf + tb, at + tf + 2 * tb]
    dur = times[-1]
    keys = ";".join(fx(x / dur, 3) for x in times)
    move = ani("transform", f"0 {f1(-h)};0 {f1(-h)};0 0;0 {f1(-b)};0 0", keys, dur,
               spline="0 0 1 1;.333 0 .667 .333;.333 .667 .667 1;.333 0 .667 .333", kind="animateTransform",
               typ="translate")
    show = ani("opacity", "0;0;1;1", f"0;{fx(at / dur, 3)};{fx((at + .06) / dur, 3)};1", dur)
    return move + show
