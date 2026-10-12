# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The motion every theme shares: one choreography, so a board moves the same way in every skin.

Every animated attribute holds its resting value, so a file is complete without SMIL. A file drawn inside
`at_rest()` has no motion at all: the still files a README serves to anyone who asks for reduced motion.

The games beside chess move on the same beats and with the same few strokes: a line drawn in from its start, as
a pen draws it or as a path follows a piece, and a mark that appears as a move lands (`stroke_in`, `appear`).
"""
from __future__ import annotations

import contextlib

from ...lettering import f1, fx
from ...standard import pieces as P

MOTION = True
LEAP, LAND = 1.6, .72  # the last move: its length in seconds, and the share of it at which the piece lands
GLINT = 7.0  # seconds between the glints round the gold medal


@contextlib.contextmanager
def at_rest(still: bool = True):
    """Everything drawn inside, still when `still` is true."""
    global MOTION
    before, MOTION = MOTION, not still
    try:
        yield
    finally:
        MOTION = before


def moving() -> bool:
    """Whether what is drawn now moves: false inside `at_rest()`."""
    return MOTION


def stroke_in(length: float, begin: float, dur: float, *, eased: bool = True) -> tuple[str, str]:
    """What draws a stroke `length` long in from its start, `begin` seconds after the file opens, over `dur`: the
    attributes its path takes, and the animation it holds. A pen's stroke is `eased` in and out; a path drawn in
    behind a moving piece keeps the piece's pace. Still, nothing: the stroke as it rests."""
    if not MOTION:
        return "", ""
    n = f1(length + 2)
    t = begin + dur
    ease = ' calcMode="spline" keySplines="0 0 1 1;.45 0 .25 1"' if eased else ""
    return (f' stroke-dasharray="{n} {n}" stroke-dashoffset="0"',
            f'<animate attributeName="stroke-dashoffset" values="{n};{n};0" keyTimes="0;{fx(begin / t, 3)};1" '
            f'dur="{fx(t, 2)}s"{ease} fill="freeze"/>')


def appear(at: float, dur: float = .2) -> str:
    """Opacity from nothing to whole, `at` seconds in, over `dur`: what appears as a move lands."""
    t = at + dur
    return ani("opacity", "0;0;1", f"0;{fx(at / t, 3)};1", t)


def ani(attr: str, values: str, times: str, dur: float, *, begin: float = 0, spline: str = "", repeat: bool = False,
        kind: str = "animate", typ: str = "") -> str:
    """One SMIL animation that holds its last value: the file's resting value, so it is complete without motion."""
    if not MOTION:
        return ""
    sp = f' calcMode="spline" keySplines="{spline}"' if spline else ""
    t = f' type="{typ}"' if typ else ""
    b = f' begin="{fx(begin, 2)}s"' if begin else ""
    r = ' repeatCount="indefinite"' if repeat else ' fill="freeze"'
    return f'<{kind} attributeName="{attr}"{t} values="{values}" keyTimes="{times}" dur="{fx(dur, 2)}s"{b}{sp}{r}/>'


def risen(cv, begin: float, fn, *a, **k):
    """Whatever `fn` adds to the file, risen into place `begin` seconds after the file opens."""
    n = len(cv.body)
    result = fn(*a, **k)
    added = "".join(cv.body[n:])
    del cv.body[n:]
    cv.add(P.rise(added, begin) if MOTION else added)
    return result


def rise(markup: str, begin: float) -> str:
    return P.rise(markup, begin) if MOTION else markup


def wiped(cv, markup: str, x, y, w, h, begin: float, dur: float = .8) -> str:
    """Markup revealed left to right, as a panel sliding open, once."""
    return P.wipe(cv, markup, x, y, w, h, begin, dur) if MOTION else markup
