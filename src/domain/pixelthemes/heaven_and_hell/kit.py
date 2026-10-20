# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Heaven & Hell theme's drawing kit: shapes cut into pixels, and forms shaded by the one lamp.

A sprite here is built the way a pixel artist builds one: its parts cut as shapes (a polygon, an ellipse, a
stroke), each part shaded as a rounded form lit from the upper left on its own material's ramp, and the whole
outlined selectively, darkest where it turns from the light. Nothing here belongs to heaven or to hell."""
from __future__ import annotations

import math

from ...holidays.pixel import LX, LY, LZ, Pix


# --------------------------------------------------------------------------- shapes, as sets of cells
def poly(points, ox=0.0, oy=0.0, s=1.0) -> set:
    """The cells whose centres lie inside a polygon, its points (x, y) scaled by `s` and moved by (ox, oy)."""
    pts = [(ox + x * s, oy + y * s) for x, y in points]
    ys = [y for _, y in pts]
    out = set()
    for row in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
        cy = row + 0.5
        xs = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 <= cy < y1) or (y1 <= cy < y0):
                xs.append(x0 + (cy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for col in range(math.ceil(a - 0.5), math.floor(b - 0.5) + 1):
                out.add((col, row))
    return out


def ellipse(cx, cy, rx, ry) -> set:
    """The cells inside an ellipse centred on (cx, cy)."""
    out = set()
    for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def stroke(path, r0, r1=None) -> set:
    """The cells within a radius of a polyline, the radius running from `r0` at its start to `r1` at its end: a
    limb, a horn, a feather or a blade."""
    r1 = r0 if r1 is None else r1
    lengths = [0.0]
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        lengths.append(lengths[-1] + math.hypot(x1 - x0, y1 - y0))
    total = lengths[-1] or 1.0
    xs = [x for x, _ in path]
    ys = [y for _, y in path]
    rm = max(r0, r1)
    out = set()
    for y in range(math.floor(min(ys) - rm) - 1, math.ceil(max(ys) + rm) + 1):
        for x in range(math.floor(min(xs) - rm) - 1, math.ceil(max(xs) + rm) + 1):
            px_, py_ = x + 0.5, y + 0.5
            for i, ((x0, y0), (x1, y1)) in enumerate(zip(path, path[1:])):
                dx, dy = x1 - x0, y1 - y0
                seg = dx * dx + dy * dy
                t = 0.0 if seg == 0 else max(0.0, min(1.0, ((px_ - x0) * dx + (py_ - y0) * dy) / seg))
                qx, qy = x0 + dx * t, y0 + dy * t
                r = r0 + (r1 - r0) * (lengths[i] + t * math.sqrt(seg)) / total
                if (px_ - qx) ** 2 + (py_ - qy) ** 2 <= r * r:
                    out.add((x, y))
                    break
    return out


def curve(ctrl, n=24) -> list:
    """Points along a quadratic or cubic Bezier through its control points."""
    out = []
    for i in range(n + 1):
        t = i / n
        if len(ctrl) == 3:
            (ax, ay), (bx, by), (cx, cy) = ctrl
            x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * bx + t * t * cx
            y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * by + t * t * cy
        else:
            (ax, ay), (bx, by), (cx, cy), (dx, dy) = ctrl
            x = (1 - t) ** 3 * ax + 3 * (1 - t) ** 2 * t * bx + 3 * (1 - t) * t * t * cx + t ** 3 * dx
            y = (1 - t) ** 3 * ay + 3 * (1 - t) ** 2 * t * by + 3 * (1 - t) * t * t * cy + t ** 3 * dy
        out.append((x, y))
    return out


def spline(points, n=6) -> list:
    """A smooth line through every one of `points`, a Catmull-Rom spline with `n` steps between each pair."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append((0.5 * (2 * x1 + (-x0 + x2) * t + (2 * x0 - 5 * x1 + 4 * x2 - x3) * t2 + (-x0 + 3 * x1 - 3 * x2 + x3) * t3),
                        0.5 * (2 * y1 + (-y0 + y2) * t + (2 * y0 - 5 * y1 + 4 * y2 - y3) * t2 + (-y0 + 3 * y1 - 3 * y2 + y3) * t3)))
    out.append(points[-1])
    return out


def edge(cells) -> set:
    """The cells of a shape that touch its outside."""
    return {(x, y) for x, y in cells
            if any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


# --------------------------------------------------------------------------- light on a form
def _depth(cells: set, cap: float) -> dict:
    """How far each cell lies inside its shape, in cells, up to `cap`: a chamfer distance from the outside."""
    d = {}
    frontier = []
    for (x, y) in cells:
        if any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            d[(x, y)] = 1.0
            frontier.append((x, y))
    steps = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.41), (1, -1, 1.41), (-1, 1, 1.41),
             (-1, -1, 1.41))
    while frontier:
        nxt = []
        for (x, y) in frontier:
            base = d[(x, y)]
            if base >= cap:
                continue
            for dx, dy, w in steps:
                q = (x + dx, y + dy)
                if q in cells and d.get(q, 1e9) > base + w:
                    d[q] = base + w
                    nxt.append(q)
        frontier = nxt
    return {q: min(cap, d.get(q, cap)) for q in cells}


def lambert(cells: set, depth: float = 3.0, tilt=(0.0, 0.0)) -> dict:
    """The light each cell of a rounded form catches, 0 to 1, from the one lamp: the form's height rises from its
    edge to `depth` cells in and its normal follows. `tilt` leans the whole form, (x, y), as a face turned away."""
    d = _depth(cells, depth)
    h = {q: math.sqrt(max(0.0, 1 - (1 - v / depth) ** 2)) for q, v in d.items()}
    out = {}
    for (x, y), z in h.items():
        gx = (h.get((x + 1, y), 0.0) - h.get((x - 1, y), 0.0)) / 2
        gy = (h.get((x, y + 1), 0.0) - h.get((x, y - 1), 0.0)) / 2
        nx, ny, nz = -gx * 1.6 + tilt[0], -gy * 1.6 + tilt[1], 1.0
        n = math.sqrt(nx * nx + ny * ny + nz * nz)
        out[(x, y)] = max(0.0, (nx * LX + ny * LY + nz * LZ) / n)
    return out


def tone(v: float, x: int, y: int, lo: int, hi: int) -> int:
    """A value on a ramp, rounded, with a thin band of checkerboard where two tones meet."""
    b = math.floor(v)
    f = v - b
    if f >= 0.62 or (f > 0.38 and (x + y) % 2 == 0):
        b += 1
    return max(lo, min(hi, b))


def form(p: Pix, cells: set, ramp, lo=1, hi=None, L="base", depth=3.0, tilt=(0.0, 0.0), gain=1.0, bias=0.0,
         dither=False) -> dict:
    """A part shaded as a rounded form on its ramp, from tone `lo` in shade to `hi` in the light, with a band of
    checkerboard where two tones meet only when it is large enough to want one (`dither`). Returns the tone each
    cell took."""
    hi = len(ramp) - 2 if hi is None else hi
    lit = lambert(cells, depth, tilt)
    out = {}
    for (x, y), lam in lit.items():
        v = lo + (hi - lo + 0.45) * min(1.0, max(0.0, lam * gain + bias)) ** 1.15
        t = tone(v, x, y, lo, hi) if dither else max(lo, min(hi, int(v + 0.5)))
        out[(x, y)] = t
        p.px(x, y, ramp[t], L)
    return out


def flat(p: Pix, cells, colour, L="base"):
    for (x, y) in cells:
        p.px(x, y, colour, L)


def outline(p: Pix, cells: set, dark: str, lit: str | None = None, L="base", only_free=False, skip=()):
    """A selective outline round a shape: `dark` on the side turned from the lamp, `lit` (or `dark`) on the side
    facing it. `only_free` keeps it off pixels already drawn on the layer."""
    lit = dark if lit is None else lit
    layer = p.layers.get(L, {})
    seen = set()
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cells or q in seen or q in skip:
                continue
            seen.add(q)
            if only_free and q in layer:
                continue
            facing = dx * LX + dy * LY > 0          # an outline pixel on the lamp's side of the shape
            p.px(q[0], q[1], lit if facing else dark, L)


def rim(p: Pix, cells: set, colour, L="base", side=(-1, -1)):
    """A line of light along the edge of a shape that faces `side`: the lit lip of a form."""
    for (x, y) in cells:
        if (x + side[0], y) not in cells or (x, y + side[1]) not in cells:
            p.px(x, y, colour, L)


def glow(p: Pix, cx, cy, rx, ry, col, alphas, L="haze", only=None, shape=None):
    """A stepped glow (see `Pix.halo`); a drawing made lighter keeps its inner rings."""
    if p.lite and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, L=L, only=only, shape=shape)


def clear(p: Pix, cells, margin=2) -> bool:
    """Whether a sprite's cells keep `margin` units clear of every word set."""
    if not cells:
        return True
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    return p.clear_of_words(min(xs) - margin, min(ys) - margin, max(xs) + 1 + margin, max(ys) + 1 + margin)


def free_rows(p: Pix, x0, x1, foot, most) -> int:
    """How many rows over row `foot` between x0 and x1 are clear of words, two units of margin kept, up to `most`."""
    n = 0
    while n < most and p.clear_of_words(x0 - 2, foot - n - 3, x1 + 2, foot + 1):
        n += 1
    return n


def reach(p: Pix, x0, top, foot, step=1, limit=None) -> int:
    """How far from x0 a band from row `top` to `foot` runs clear of words, two units kept: to `limit` at most."""
    x = x0
    while (limit is None or (x < limit if step > 0 else x > limit)) and p.clear_of_words(x - 2, top - 2, x + 3, foot):
        x += step
    return x
