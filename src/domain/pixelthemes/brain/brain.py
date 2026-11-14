# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The brain, seen from its left side as an anatomist draws it, its frontal lobe to the left: every gyrus a rounded,
glistening fold of tissue, the sulci dark between them, the Sylvian fissure parting the temporal lobe from the rest,
the cerebellum tucked under the back with its fine folia, and the stem going down from under it.

By day the lab's lamps light it from the upper left: each fold is shaded as the rounded thing it is, wet light
catching its crown. By night the lamps are out and the jar's fluid lights it from below and behind: the tissue falls
dark, and every fold is rimmed in the fluid's aqua.

Electrodes sit on its crown, where the jar's wires come down to it. At work, sparks run along its folds and its
synapses fire in waves from the front of the head to the back."""
from __future__ import annotations

import math
import random
from functools import lru_cache

from ...holidays.pixel import LX, LY, LZ, Pix
from .kit import closed, depth, edge, ellipse, poly, signal, spline, trace
from .palette import C, RAMP

TISSUE, FLUID, STEEL, BRASS, ARC, NIXIE = (RAMP["tissue"], RAMP["fluid"], RAMP["steel"], RAMP["brass"], RAMP["arc"],
                                           RAMP["nixie"])

# --------------------------------------------------------------------------- the anatomy, in a box 100 by 84
W, H = 100, 84
OUTLINE = [(2, 44), (3, 34), (7, 25), (13, 17), (21, 10.5), (31, 5.5), (42, 2.5), (53, 1.5), (64, 2.5), (74, 5.8),
           (83, 11.5), (90.5, 19), (95.5, 28), (98.5, 37), (99, 45), (96.5, 52.5), (91, 57.5), (83, 59.5),
           (75, 60), (68, 61.5), (60, 64.5), (50, 66.5), (40, 66), (32, 63), (27, 59), (24.5, 54.5), (23, 51.5),
           (18, 53), (11, 52), (5.5, 49)]
STEM = [(60, 60), (72, 60), (73.5, 65), (72.5, 70), (70.5, 74), (70.2, 84), (64.4, 84), (64.2, 74), (62.2, 70),
        (60.4, 65)]
CEREBELLUM = (81, 67, 15.5, 9.5)
# The gyri: (centreline, radius). Gaps left between them are the sulci.
GYRI = [
    ([(46, 5.5), (37, 6), (28, 8.5), (20, 13), (13, 19.5), (8, 26)], 3.9),                     # superior frontal
    ([(42, 15), (33, 16.5), (25, 19), (17, 23.5), (10, 30), (5.5, 37)], 3.9),                  # middle frontal
    ([(39, 26), (31, 28), (23, 31), (15, 35.5), (9, 41), (6, 46.5)], 3.6),                     # inferior frontal
    ([(32, 37.5), (24, 40.5), (17, 44.5), (11, 48.5)], 3.2),                                   # orbital
    ([(51, 3), (49, 10), (48, 17), (46, 24), (44, 31), (42, 38), (40, 44)], 3.7),              # precentral
    ([(59, 3.5), (58, 10), (57, 17), (55, 24), (53.5, 31), (52.5, 38)], 3.7),                  # postcentral
    ([(66, 6), (73, 9), (80, 13.5), (86, 20)], 3.9),                                           # superior parietal
    ([(61, 28), (64, 22.5), (70, 21), (76, 24), (78, 30), (74, 35)], 3.6),                     # supramarginal
    ([(79, 35), (85, 29.5), (90, 32), (91.5, 39), (86, 43)], 3.4),                             # angular
    ([(65, 13.5), (71, 15.5), (77, 18.5)], 3.0),
    ([(89, 22), (94, 28.5), (97, 36)], 3.4),                                                   # occipital
    ([(93, 42), (97, 47), (94, 53)], 3.1),
    ([(84, 47.5), (89, 51.5), (86, 56.5)], 3.0),
    ([(27, 53), (35, 49.5), (44, 47), (53, 45), (61, 43), (68, 40), (72, 35.5)], 3.6),         # superior temporal
    ([(30, 58.5), (39, 55.5), (49, 53.5), (59, 52), (68, 49), (76, 45.5), (81, 40.5)], 3.7),   # middle temporal
    ([(37, 63.2), (47, 61.8), (57, 60), (66, 57), (75, 53.5), (82, 50.5)], 3.3),               # inferior temporal
    ([(46, 40), (52, 38.5), (58, 37)], 2.9),                                                   # the operculum
]
# The deepest fissures, which part the lobes: the lateral (Sylvian) fissure, under which the temporal lobe lies, and
# the central sulcus, between the frontal lobe and the parietal.
FISSURES = [
    [(23.5, 51.5), (31, 48.6), (40, 45.6), (49, 43.2), (57, 41.2), (63, 38.6), (67, 34.5), (69.5, 30)],
    [(54.6, 2.2), (53.2, 8), (52.8, 14), (51.2, 20), (49.8, 27), (48.4, 34), (47.2, 40.4)],
]
# Where the electrodes sit on its crown, and the route a thought takes as its synapses fire in turn.
ELECTRODES = [(29, 6.5), (55, 2.5), (81, 12)]
CASCADE = [(12, 30), (22, 18), (34, 9), (48, 9), (58, 18), (70, 18), (84, 26), (92, 38), (86, 50), (72, 46),
           (58, 50), (44, 51), (34, 43), (24, 36)]


def _meander(points, seed, amp=0.8, every=10.0) -> list:
    """A gyrus as it really runs: through its points, wandering a little either side."""
    line = spline(points, 5)
    rnd = random.Random(seed)
    phase, run, out = rnd.uniform(0, 6.3), 0.0, []
    for i, (x, y) in enumerate(line):
        if i:
            run += math.hypot(x - line[i - 1][0], y - line[i - 1][1])
        a, b = line[max(0, i - 1)], line[min(len(line) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        off = amp * math.sin(phase + run * 2 * math.pi / every)
        out.append((x - dy / n * off, y + dx / n * off))
    return out


def _seg_dist(px, py, ax, ay, bx, by) -> float:
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


@lru_cache(maxsize=None)
def folds() -> tuple:
    """Every gyrus in the brain's own units, (centreline, radius): the ones drawn above, wandering as folds do, and
    short ones laid wherever they leave the tissue bare, lying along their nearest neighbour as gyri lie side by
    side."""
    out = [(tuple(_meander(pts, seed=3 + i * 5)), r * 1.12) for i, (pts, r) in enumerate(GYRI)]
    mask = poly(closed(OUTLINE, 4), s=1.0)
    inner = {q for q in mask if all((q[0] + dx, q[1] + dy) in mask for dx in (-3, 0, 3) for dy in (-3, 0, 3))}
    rnd = random.Random(7)
    for _ in range(3):
        for gy in range(3, 66, 2):
            for gx in range(3, 99, 2):
                if (gx, gy) not in inner:
                    continue
                x, y = gx + 0.5, gy + 0.5
                near_d, along = 99.0, (1.0, 0.0)
                for line, r in out:
                    for i in range(len(line) - 1):
                        d = _seg_dist(x, y, *line[i], *line[i + 1]) - r
                        if d < near_d:
                            near_d = d
                            along = (line[i + 1][0] - line[i][0], line[i + 1][1] - line[i][1])
                if near_d < 1.2:
                    continue
                a = math.atan2(along[1], along[0]) + rnd.uniform(-0.3, 0.3)
                ln = rnd.uniform(4.5, 7.5)
                pts = [(x + ln * t * math.cos(a), y + ln * t * math.sin(a)) for t in (-0.5, 0, 0.5)]
                out.append((tuple(spline(pts, 3)), 3.2))
    return tuple(out)


class Shape:
    """The brain at one size, its top left at (0, 0): every cell of each part, the light on it by day and by
    night, and the paths its sparks run."""

    def __init__(self, k: float):
        self.k = s = k
        self.w, self.h = math.ceil(W * s) + 1, math.ceil(H * s) + 1
        self.cerebrum = poly(closed(OUTLINE, 4), s=s)
        cx, cy, rx, ry = CEREBELLUM
        self.cerebellum = ellipse(cx * s, cy * s, rx * s, ry * s) - self.cerebrum
        self.stem = poly(closed(STEM, 3), s=s) - self.cerebrum - self.cerebellum
        if s >= 0.5:
            self.lines = [([(x * s, y * s) for x, y in line], r * s) for line, r in folds()]
        else:
            # drawn small, a brain keeps its main folds, each a little fuller, so it reads at a glance
            self.lines = [([(x * s, y * s) for x, y in _meander(pts, seed=3 + i * 5, amp=0.6)], r * s * 1.3)
                          for i, (pts, r) in enumerate(GYRI)]
        # the height of the tissue: the tallest fold under each cell, on a dome that falls away to the edge
        cap = max(2.5, 8 * s)
        dome = depth(self.cerebrum, cap)
        hgt, owner = {}, {}
        boxes = [(min(x for x, _ in l) - r, min(y for _, y in l) - r, max(x for x, _ in l) + r, max(y for _, y in l) + r)
                 for l, r in self.lines]
        for (x, y) in self.cerebrum:
            px, py = x + 0.5, y + 0.5
            best, who = 0.0, -1
            for j, ((line, r), b) in enumerate(zip(self.lines, boxes)):
                if not (b[0] <= px <= b[2] and b[1] <= py <= b[3]):
                    continue
                d = min(_seg_dist(px, py, *line[i], *line[i + 1]) for i in range(len(line) - 1))
                if d < r:
                    v = r * math.sqrt(1 - (d / r) ** 2)
                    if v > best:
                        best, who = v, j
            f = math.sqrt(max(0.0, 1 - (1 - dome[(x, y)] / cap) ** 2))
            hgt[(x, y)] = best * (0.45 + 0.55 * f) + f * cap * 0.35
            owner[(x, y)] = who
        self.owner = owner
        rmax = max(r for _, r in self.lines)
        self.crevice = {q for q, v in hgt.items() if (owner[q] < 0 or v - _domepart(dome[q], cap) < rmax * 0.2)}
        self.edge = edge(self.cerebrum)
        # the fissures, cut deep, their lower lip catching the light
        self.fissure, self.lip = set(), set()
        for line in FISSURES:
            cells = [c for c in trace([(x * s, y * s) for x, y in spline(line, 4)]) if c in self.cerebrum]
            for (x, y) in cells:
                self.fissure.add((x, y))
                if s >= 0.8 and (x, y + 1) in self.cerebrum:
                    self.fissure.add((x, y + 1))
            for (x, y) in cells:
                below = (x, y + (2 if s >= 0.8 else 1))
                if below in self.cerebrum and below not in self.fissure:
                    self.lip.add(below)
        for q in self.fissure:
            hgt[q] = hgt[q] - rmax * 0.6
        self.light, self.back, self.spec = _shade(hgt)
        # the cerebellum: a dome with its folia cut across it
        cd = depth(self.cerebellum, max(2.0, 5 * s))
        gap = max(2, round(2.2 * s + 0.4))
        self.folia = set()
        for (x, y) in self.cerebellum:
            u = (y - (cy - ry) * s) - 0.6 * ((x - cx * s) / max(1.0, rx * s)) ** 2 * ry * s
            if int(u) % gap == 0 and (x, y) not in edge(self.cerebellum):
                self.folia.add((x, y))
        ch = {q: math.sqrt(max(0.0, 1 - (1 - v / max(2.0, 5 * s)) ** 2)) * 3 - (0.35 if q in self.folia else 0)
              for q, v in cd.items()}
        self.cb_light, self.cb_back, _ = _shade(ch)
        sd = depth(self.stem, max(2.0, 3 * s))
        self.st_light, self.st_back, _ = _shade({q: math.sqrt(max(0.0, 1 - (1 - v / max(2.0, 3 * s)) ** 2)) * 2.4
                                                 for q, v in sd.items()})
        whole = self.cerebrum | self.cerebellum | self.stem
        self.ring = {(x + dx, y + dy) for (x, y) in whole for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - whole
        self.electrodes = [(round(x * s), round(y * s)) for x, y in ELECTRODES]

    def crowns(self, n=5) -> list:
        """The centrelines of the longest folds, as cells, for sparks to run along."""
        by = sorted(self.lines, key=lambda lr: -sum(math.hypot(b[0] - a[0], b[1] - a[1])
                                                    for a, b in zip(lr[0], lr[0][1:])))
        out = []
        for line, r in by[:n]:
            cells = [c for c in trace(line) if c in self.cerebrum]
            if len(cells) >= 6:
                out.append(cells)
        return out


def _domepart(v, cap):
    f = math.sqrt(max(0.0, 1 - (1 - v / cap) ** 2))
    return f * cap * 0.35


def _shade(h: dict) -> tuple:
    """The light each cell of a height field takes: from the lamp at the upper left, from the fluid's glow below and
    behind it, and the wet glint of the lamp on it."""
    light, back, spec = {}, {}, {}
    hx, hy, hz = LX, LY, LZ + 1.0
    hn = math.sqrt(hx * hx + hy * hy + hz * hz)
    hx, hy, hz = hx / hn, hy / hn, hz / hn
    for (x, y), z in h.items():
        gx = (h.get((x + 1, y), z - 0.6) - h.get((x - 1, y), z - 0.6)) / 2
        gy = (h.get((x, y + 1), z - 0.6) - h.get((x, y - 1), z - 0.6)) / 2
        nx, ny, nz = -gx * 1.5, -gy * 1.5, 1.0
        n = math.sqrt(nx * nx + ny * ny + nz * nz)
        nx, ny, nz = nx / n, ny / n, nz / n
        light[(x, y)] = max(0.0, nx * LX + ny * LY + nz * LZ)
        back[(x, y)] = max(0.0, nx * 0.62 + ny * 0.7 + nz * 0.36)
        spec[(x, y)] = max(0.0, nx * hx + ny * hy + nz * hz) ** 18
    return light, back, spec


@lru_cache(maxsize=None)
def shape(k: float) -> Shape:
    return Shape(round(k, 2))


def extent(k: float) -> tuple:
    """The brain's width and height at scale `k`, its outline included."""
    s = shape(k)
    return s.w + 1, s.h + 1


# --------------------------------------------------------------------------- drawing it
def brain(p: Pix, ox: int, oy: int, k: float, night: bool, L="base", rim=None):
    """The brain at scale `k`, the top left of its box at (ox, oy): lit by the lab's lamps by day, by the jar's
    glow by night. `rim`, a colour, is the light the fluid round it throws on its lower edges by day."""
    s = shape(k)
    big = k >= 0.45
    T = TISSUE
    # the stem and the cerebellum first, the cerebrum over them
    for (x, y), v in s.st_light.items():
        if night:
            c = FLUID[3] if s.st_back[(x, y)] > 0.8 else T[1 + min(2, int(v * 2.6))]
        else:
            c = T[min(5, 2 + int(v * 3.6))]
        p.px(ox + x, oy + y, c, L)
    for (x, y), v in s.cb_light.items():
        fol = (x, y) in s.folia
        if night:
            t = 1 + min(2, int(v * 2.6))
            c = T[t - 1] if fol else (FLUID[3] if s.cb_back[(x, y)] > 0.84 else T[t])
        else:
            t = min(5, 2 + int(v * 3.4))
            c = T[max(1, t - 1)] if fol else T[t]
        p.px(ox + x, oy + y, c, L)
    for (x, y), v in s.light.items():
        q = (x, y)
        if q in s.crevice:
            c = T[0]
        elif night:
            b = s.back[q]
            c = T[min(3, int(v * 3.6))]
            if b > 0.92 and y > s.h * 0.5:
                c = FLUID[2]
            if s.spec[q] > 0.75:
                c = T[4]
        else:
            t = 1 + (4.6 * v ** 1.15) + 0.7 * (0.42 - y / s.h) - 0.35 * (x / s.w - 0.4)
            ti = int(t)
            if k >= 0.6 and t - ti > 0.45 and (x + y) % 2 == 0:
                ti += 1
            c = T[max(1, min(5, ti))]
            if s.spec[q] > (0.7 if k >= 0.5 else 0.82):
                c = T[6] if s.spec[q] < 0.93 else C["white"]
        p.px(ox + x, oy + y, c, L)
    for q in s.fissure:
        p.px(ox + q[0], oy + q[1], T[0], L)
    for q in s.lip:
        if q not in s.crevice:
            p.px(ox + q[0], oy + q[1], (T[4] if not night else T[2]), L)
    if night:
        # the fluid's light round its silhouette, strongest below and behind
        for (x, y) in s.edge:
            lower = y > s.h * 0.3 or x > s.w * 0.75
            if lower and (x, y) not in s.crevice:
                p.px(ox + x, oy + y, FLUID[4] if y > s.h * 0.45 else FLUID[3], L)
    # its outline, and the fluid's light along its lower edges
    for (x, y) in s.ring:
        below = (x, y - 1) in s.cerebrum or (x - 1, y) in s.cerebrum
        p.px(ox + x, oy + y, T[0] if not night else RAMP["room"][0], L)
    if rim and not night:
        for (x, y) in s.ring:
            if ((x, y - 1) in s.cerebrum or (x, y - 1) in s.cerebellum) and y > s.h * 0.55:
                p.px(ox + x, oy + y - 1, rim, L)
    # the electrodes on its crown
    for (x, y) in s.electrodes:
        for dx, dy, c in ((-1, 0, STEEL[3]), (0, 0, BRASS[5]), (1, 0, STEEL[2]), (0, -1, STEEL[5]), (0, 1, STEEL[1])):
            p.px(ox + x + dx, oy + y + dy, c, L)


# --------------------------------------------------------------------------- the brain at work
def spark_key(p: Pix, night: bool):
    key = ("spark", night)
    if key not in p.syms:
        arm = FLUID[5] if night else NIXIE[5]
        p.symbol(key, {(0, 0): C["white"], (1, 0): arm, (-1, 0): arm, (0, 1): arm, (0, -1): arm})
    return key


def work(p: Pix, ox, oy, k, night):
    """The brain at work: sparks running along its folds, each on a loop of its own, and its synapses firing in
    four waves, front to back, one after another."""
    s = shape(k)
    key = spark_key(p, night)
    for i, cells in enumerate(s.crowns(3)):
        run = [(ox + x, oy + y) for (x, y) in (cells if i % 2 == 0 else cells[::-1])][::2]
        path = run + [run[-1]] * (5 + (i * 5) % 11)
        signal(p, key, path, len(path) * 0.12)
    waves = (CASCADE[0:5], CASCADE[5:10], CASCADE[10:14])
    for i, wave in enumerate(waves):
        L = p.seq(f"syn{i}", i * 0.14, i * 0.14 + 0.12, 4.0, z=9)
        for (x, y) in (wave if k >= 0.5 else wave[::2]):
            burst(p, ox + round(x * k), oy + round(y * k), night, L, big=k >= 0.5)


def burst(p: Pix, cx, cy, night, L, big=True):
    """A synapse firing: a white heart and four arms of light."""
    arm, tip = (FLUID[5], FLUID[3]) if night else (NIXIE[5], NIXIE[3])
    p.px(cx, cy, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(cx + dx, cy + dy, arm, L)
        if big:
            p.px(cx + 2 * dx, cy + 2 * dy, tip, L)


def flash(p: Pix, ox, oy, k, night, L):
    """The idea striking: the crown of every fold lit at once."""
    s = shape(k)
    for (x, y), v in s.light.items():
        if (x, y) not in s.crevice and v > 0.82 and (x + y) % 3 == 0:
            p.px(ox + x, oy + y, (FLUID[6] if night else C["white"]) + ":0.8", L)
