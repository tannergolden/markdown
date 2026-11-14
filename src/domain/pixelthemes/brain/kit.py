# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The brain theme's drawing kit: shapes cut into pixels, distances inside them, the room the words leave, a stepped
glow, and a signal that runs along a path."""
from __future__ import annotations

import math

from ...holidays.pixel import Pix, num


def poly(points, ox=0.0, oy=0.0, s=1.0) -> set:
    """The cells whose centres lie inside a polygon, its points (x, y) scaled by `s` and moved by (ox, oy)."""
    pts = [(ox + x * s, oy + y * s) for x, y in points]
    ys = [y for _, y in pts]
    out = set()
    n = len(pts)
    for cy in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
        yc = cy + 0.5
        xs = []
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for cx in range(math.ceil(a - 0.5), math.floor(b - 0.5) + 1):
                out.add((cx, cy))
    return out


def ellipse(cx, cy, rx, ry) -> set:
    """The cells inside an ellipse centred on (cx, cy)."""
    out = set()
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                out.add((x, y))
    return out


def _catmull(p0, p1, p2, p3, t) -> tuple:
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                        + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1))


def spline(points, n=6) -> list:
    """A smooth line through every one of `points`, a Catmull-Rom spline with `n` steps between each pair."""
    if len(points) < 3:
        return list(points)
    pts = [points[0]] + list(points) + [points[-1]]
    out = [_catmull(pts[i - 1], pts[i], pts[i + 1], pts[i + 2], k / n) for i in range(1, len(pts) - 2)
           for k in range(n)]
    out.append(points[-1])
    return out


def closed(points, n=5) -> list:
    """A smooth closed outline through `points`, the same spline carried round from the last point to the first."""
    m = len(points)
    return [_catmull(points[i - 1], points[i], points[(i + 1) % m], points[(i + 2) % m], k / n) for i in range(m)
            for k in range(n)]


def trace(points) -> list:
    """The cells a polyline passes through, in order, each once, stepping diagonally where it runs on a slant: a
    line of single pixels as a pixel artist draws one."""
    out = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) * 2))
        for i in range(n + 1):
            c = (math.floor(x0 + (x1 - x0) * i / n), math.floor(y0 + (y1 - y0) * i / n))
            if not out or out[-1] != c:
                out.append(c)
    return out


def edge(cells) -> set:
    """The cells of a shape that touch its outside."""
    return {(x, y) for x, y in cells
            if any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def depth(cells: set, cap: float) -> dict:
    """How far each cell lies inside its shape, in cells, up to `cap`: a chamfer distance from the outside."""
    d, frontier = {}, []
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


def glow(p: Pix, cx, cy, rx, ry, col, alphas, L="haze", only=None, shape=None):
    """A stepped glow (see `Pix.halo`); a drawing made lighter keeps its inner rings."""
    if p.lite and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, L=L, only=only, shape=shape)


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


def signal(p: Pix, key, path: list, dur: float, z: float = 9):
    """A signal running along `path`, (x, y) a step at a time, round and round: the symbol `key` placed at each
    point in turn. The still file shows it at the path's first point."""
    sid = p.syms[key]
    steps = ";".join(f"{x} {y}" for x, y in path)
    moving = (f'<use href="#{sid}"><animateTransform attributeName="transform" type="translate" values="{steps}" '
              f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></use>')
    x0, y0 = path[0]
    p.raw(z, moving, f'<use href="#{sid}" x="{x0}" y="{y0}"/>')
