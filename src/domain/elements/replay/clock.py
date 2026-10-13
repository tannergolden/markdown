# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A replay's one timeline: every animated attribute in the file runs the whole loop and repeats forever.

Each animation places its moments as keyTimes across the loop, holds its first value from the loop's start and its
last to the loop's end, and starts again with every other in step, so the file plays the game, holds on its finale
and plays it again, however long it is left open. Nothing waits on a click or a begin event: an image in a README
runs no script and hears no event, and a loop of keyTimes plays the same in every browser that plays SMIL.
"""
from __future__ import annotations

LIN = "0 0 1 1"
EASE = ".45 0 .25 1"            # a glide, set off and set down
OUT = ".2 .7 .3 1"              # quick away, settling: the README's rise
FALL = ".333 0 .667 .333"       # from rest under gravity
RISE = ".333 .667 .667 1"       # to rest against gravity


def num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Clock:
    def __init__(self, total: float):
        self.D = total

    def anim(self, attr: str, frames: list, *, transform: str | None = None, discrete: bool = False) -> str:
        """`attr` through `frames`, each (t, value) or (t, value, the spline into the next), in order: held at its
        first value from the loop's start and at its last to the loop's end."""
        fr = [tuple(f) + ((LIN,) if len(f) == 2 else ()) for f in frames]
        for (a, *_), (b, *_) in zip(fr, fr[1:]):
            if b < a - 1e-9:
                raise ValueError(f"{attr}: moment {b} comes before {a}")
        if fr[0][0] > 0:
            fr.insert(0, (0.0, fr[0][1], LIN))
        if fr[-1][0] < self.D:
            fr.append((self.D, fr[-1][1], LIN))
        kts, last = [], 0.0
        for t, _, _ in fr:
            k = max(last, min(1.0, round(t / self.D, 4)))
            kts.append(k)
            last = k
        kts[0], kts[-1] = 0.0, 1.0
        values = ";".join(str(v) for _, v, _ in fr)
        times = ";".join(f"{k:.4f}".rstrip("0").rstrip(".") or "0" for k in kts)
        tag = "animateTransform" if transform else "animate"
        extra = f' type="{transform}"' if transform else ""
        if discrete:
            return (f'<{tag} attributeName="{attr}"{extra} values="{values}" keyTimes="{times}" dur="{num(self.D)}s" '
                    f'repeatCount="indefinite" calcMode="discrete"/>')
        splines = ";".join(s for _, _, s in fr[:-1])
        return (f'<{tag} attributeName="{attr}"{extra} values="{values}" keyTimes="{times}" dur="{num(self.D)}s" '
                f'repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>')

    def windows(self, spans: list[tuple[float, float]]) -> str:
        """Visible during each span and hidden between them: one animation however many spans."""
        merged: list[list[float]] = []
        for a, b in sorted(spans):
            if merged and a <= merged[-1][1] + 1e-6:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        fr = [] if merged and merged[0][0] <= 0 else [(0, "hidden")]
        for a, b in merged:
            fr += [(max(0.0, a), "visible")]
            if b < self.D:
                fr.append((b, "hidden"))
        return self.anim("visibility", fr, discrete=True)

    def appear(self, at: float, fade: float = .2, until: float | None = None) -> str:
        """Opacity that is 0 until `at`, fades in over `fade`, and holds, or goes again at `until`: the README's
        `appear`, at its moment on the loop."""
        fr = [(0, 0), (at, 0), (at + fade, 1)]
        if until is not None:
            fr += [(max(until, at + fade), 1), (max(until, at + fade), 0)]
        return self.anim("opacity", fr)
