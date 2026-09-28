# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Colour and light for the holiday sets: the ramps every sprite is shaded on, and the one lamp.

Every set lights its sprites from the same place, up and to the left and
toward the viewer, and shades them on ramps of seven tones, dark to light,
whose shadows lean purple and whose lights lean gold, the way pixel artists
shade. A set's palette is closed: every colour one of its files uses is a
tone on one of its ramps or a colour it names, so `tones` hands each set its
own `step` and `ramp_for`, which refuse a colour the set does not have.
"""
from __future__ import annotations

import colorsys
import math


def _rgb(h: str) -> tuple:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _hex(r, g, b) -> str:
    return "#%02X%02X%02X" % tuple(round(max(0, min(255, v))) for v in (r, g, b))


def _toward(h: float, target: float, amount: float) -> float:
    """Turn hue `h` toward `target` by `amount` of a full turn, the short way round."""
    d = (target - h + 0.5) % 1.0 - 0.5
    step = max(-abs(d), min(abs(d), amount)) if d >= 0 else -min(abs(d), amount)
    return (h + step) % 1.0


def make_ramp(base: str, n: int = 7, mid: int = 3) -> list[str]:
    """Seven tones, dark to light, around `base`: shadows lean purple and gain
    saturation, lights lean yellow and wash out, the way pixel artists shade."""
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in _rgb(base)))
    out = []
    for i in range(n):
        k = i - mid
        if k < 0:
            hh, ss, vv = _toward(h, 0.76, 0.03 * -k), min(1.0, s + 0.07 * -k), v * (0.72 ** -k)
        elif k > 0:
            hh, ss, vv = _toward(h, 0.15, 0.025 * k), s * (0.62 ** k), min(1.0, v + (1 - v) * 0.5 * k + 0.04 * k)
        else:
            hh, ss, vv = h, s, v
        r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
        out.append(_hex(r * 255, g * 255, b * 255))
    return out


def tones(ramps: dict):
    """A set's `step` and `ramp_for`, bound to its ramps.

    `step(col, k)` is the tone `k` steps lighter (or, negative, darker) than
    `col` on its own ramp: how a lit edge or a shaded foot is coloured without
    inventing a colour. `ramp_for(col)` is the ramp a colour is on. A colour on
    none of the set's ramps is a design bug, so both raise.
    """
    def ramp_for(col: str) -> list[str]:
        for r in ramps.values():
            if col in r:
                return r
        raise KeyError(f"{col} is on no ramp")

    def step(col: str, k: int) -> str:
        ramp = ramp_for(col)
        i = ramp.index(col)
        return ramp[max(0, min(len(ramp) - 1, i + k))]

    return step, ramp_for


def luminance(h: str) -> float:
    """The relative luminance of a #RRGGBB, as WCAG 2 defines it."""
    out = []
    for v in _rgb(h):
        v /= 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    r, g, b = out
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """The WCAG 2 contrast ratio between two colours, from 1 to 21."""
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


# --------------------------------------------------------------------------- light
LIGHT = (-0.55, -0.68, 0.62)   # up and to the left, toward the viewer
_LN = math.sqrt(sum(c * c for c in LIGHT))
LX, LY, LZ = (c / _LN for c in LIGHT)


def _tone(v: float, x: int, y: int, lo: int, hi: int) -> int:
    """A value on the ramp, rounded, with a thin band of checkerboard where two tones meet."""
    b = math.floor(v)
    f = v - b
    if f >= 0.62 or (f > 0.38 and (x + y) % 2 == 0):
        b += 1
    return max(lo, min(hi, b))


def sphere(p, cx, cy, r, ramp, L="base", lo=1, hi=None, spec=True, rim=True, outline=True, only=None):
    """A lit ball: Lambert light from the upper left stepped down the ramp, a glint where the light
    lands, bounce light on the far rim, and a selective outline, darker on the shaded side."""
    hi = len(ramp) - 1 if hi is None else hi
    cells = {}
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1.0:
                continue
            nz = math.sqrt(1 - d2)
            lam = max(0.0, dx * LX + dy * LY + nz * LZ)
            v = lo + (hi - 1 - lo + 0.4) * lam ** 1.1
            t = _tone(v, x, y, lo, hi - 1)
            if rim and d2 > 0.55 and (dx * LX + dy * LY) < -0.42:
                t = max(t, lo + 1)
            cells[(x, y)] = t
    if only is not None:
        cells = {k: v for k, v in cells.items() if only(*k)}
    if spec and cells:
        sx, sy = cx + LX * r * 0.5, cy + LY * r * 0.5
        best = min(cells, key=lambda q: (q[0] + 0.5 - sx) ** 2 + (q[1] + 0.5 - sy) ** 2)
        cells[best] = hi
        if r >= 4.5:
            for q in ((best[0] + 1, best[1]), (best[0], best[1] + 1)):
                if q in cells:
                    cells[q] = max(cells[q], hi - 1)
    for (x, y), t in cells.items():
        p.px(x, y, ramp[t], L)
    if outline and r >= 2.5:
        for (x, y) in list(cells):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q in cells:
                    continue
                far = (q[0] + 0.5 - cx) * LX + (q[1] + 0.5 - cy) * LY < 0
                p.px(q[0], q[1], ramp[0] if far else ramp[min(lo, 1)], L)
    return cells


def tube(p, path, rad, colour_at, L="base", step=0.2, outline=None):
    """A lit rope along a polyline: each pixel finds its nearest point on the line, reads its
    place across the rope as a cylinder's normal, and `colour_at(s, o, lam, x, y)` colours it,
    given how far along (s), how far across (o, -1..1) and how much light (lam, 0..1)."""
    pts = []
    s = 0.0
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(seg / step))
        for i in range(n):
            t = i / n
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, s + seg * t, (x1 - x0) / seg, (y1 - y0) / seg))
        s += seg
    lx_, ly_ = path[-1]
    pts.append((lx_, ly_, s, pts[-1][3], pts[-1][4]))
    grid = {}
    for q in pts:
        grid.setdefault((int(q[0] // 3), int(q[1] // 3)), []).append(q)
    xs = [q[0] for q in pts]
    ys = [q[1] for q in pts]
    cells = {}
    for y in range(math.floor(min(ys) - rad) - 1, math.ceil(max(ys) + rad) + 1):
        for x in range(math.floor(min(xs) - rad) - 1, math.ceil(max(xs) + rad) + 1):
            px_, py_ = x + 0.5, y + 0.5
            best, bd = None, 1e9
            gx, gy = int(px_ // 3), int(py_ // 3)
            for ix in range(gx - 2, gx + 3):
                for iy in range(gy - 2, gy + 3):
                    for q in grid.get((ix, iy), ()):
                        d = (q[0] - px_) ** 2 + (q[1] - py_) ** 2
                        if d < bd:
                            best, bd = q, d
            if best is None or bd > rad * rad:
                continue
            qx, qy, qs, tx, ty = best
            nx, ny = -ty, tx                        # the rope's left-hand normal
            o = ((px_ - qx) * nx + (py_ - qy) * ny) / rad
            o = max(-1.0, min(1.0, o))
            nz = math.sqrt(max(0.0, 1 - o * o))
            lam = max(0.0, (nx * o) * LX + (ny * o) * LY + nz * LZ)
            cells[(x, y)] = colour_at(qs, o, lam, x, y)
    for (x, y), c in cells.items():
        p.px(x, y, c, L)
    if outline:
        for (x, y) in list(cells):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in cells and p.get(*q, L) is None:
                    p.px(q[0], q[1], outline, L)
    return cells


def cylinder(p, spans, ramp, L="base", lo=1, hi=None, outline=True):
    """Rows of pixels shaded as a column lit from the left: `spans` is [(y, x0, x1), ...]."""
    hi = len(ramp) - 2 if hi is None else hi
    for (y, a, b) in spans:
        for x in range(a, b + 1):
            t = (x + 0.5 - a) / max(1, b + 1 - a)
            nx = 2 * t - 1
            nz = math.sqrt(max(0.0, 1 - nx * nx))
            lam = max(0.0, nx * LX + nz * LZ + 0.12)
            v = lo + (hi - lo + 0.5) * lam
            c = _tone(v, x, y, lo, hi)
            if outline and (x == b):
                c = max(0, lo - 1)
            p.px(x, y, ramp[c], L)
