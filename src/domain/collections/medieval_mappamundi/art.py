# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mappa Mundi set's scenery and sprites, drawn on the shared pixel canvas.

The parchment every sheet is drawn on and the chart a header opens on (the sea washed in verdigris with its
fine wave lines, the land in ochre with its coast water-lined, the unknown land left bare), the ruled border with
its graduated scale and the wind heads blowing at its top corners, the band of gilded compass stars across a
header's top, letters engraved as on a copper plate on an unfurling banderole, the map's own drawings (the walled
city at its river mouth, hills and trees, the compass rose and its rhumb lines, the cog on its dotted route, the
sea serpent, the whale, the dragon and the islands with the map's marks on them), the lantern, its pool of light
and the brass dividers of the navigator's table by night, the compass rose in its medallion and the sea a
footer opens onto, and the things of the chart every element and badge is made of. The drawings are flat and
cartographic: ink outlines, washes of colour and hatching, lit from the upper left."""
from __future__ import annotations

import functools
import heapq
import math
import random

from ...holidays.designs.banners import MARK_Y
from ...holidays.pixel import Paint, Pix, num
from ..hand import MEDIEVAL
from .palette import C, NIGHT_SKY, RAMP, X, step

INK, PARCH, SEA, LAND = RAMP["ink"], RAMP["parch"], RAMP["sea"], RAMP["land"]
VERM, GOLD, GREEN, SLATE = RAMP["verm"], RAMP["gold"], RAMP["green"], RAMP["slate"]
SKIN, FLAME, NIGHT, DEEP, DUSK = RAMP["skin"], RAMP["flame"], RAMP["night"], RAMP["deep"], RAMP["dusk"]
K = INK[1]          # the ink every drawing is outlined in
BAND = 5            # the depth of the ruled border on every side
TOP_BAND = 10       # the depth of a header's top band of graduated scale and compass stars


def _paths(cols: dict) -> str:
    """Paths for {colour or colour:alpha: {y: [x, ...]}}."""
    out = []
    for c, rows in cols.items():
        if not rows:
            continue
        if ":" in c:
            col, a = c.split(":")
            out.append(f'<path stroke="{col}" stroke-opacity="{a}" d="{Pix._d(rows)}"/>')
        else:
            out.append(f'<path stroke="{c}" d="{Pix._d(rows)}"/>')
    return "".join(out)


def _put(cols: dict, c: str, x: int, y: int):
    cols.setdefault(c, {}).setdefault(y, []).append(x)


def _mark(p: Pix, cells):
    """Keep `cells` in the drawing's `filled`, so a check that gathers what a hook draws finds the cells a
    shape fills as it finds pixels set one by one."""
    if not hasattr(p, "filled"):
        p.filled = set()
    p.filled.update(cells)


def top_centre(p: Pix) -> tuple | None:
    """The box (x0, y0, x1, y1), ends excluded, that a header keeps clear at its top centre for the hand's month's
    mark: the box the mark is drawn in (see `Holiday.month_mark`) and two units round it. Nothing of the chart is
    drawn in it but the band across the top and the sea itself, whether the mark is drawn or not, so the mark
    never cuts a drawing at its edge and the chart is the same with it and without it. None on a sheet that is not
    a header."""
    if not getattr(p, "chart", None):
        return None
    n = MEDIEVAL.mark_size
    x0, y0 = p.w // 2 - n // 2, MARK_Y - n // 2
    return (x0 - 2, y0 - 2, x0 + n + 2, y0 + n + 2)


def _off_top_centre(p: Pix, x0, y0, x1, y1) -> bool:
    """Whether the box (x0, y0, x1, y1), ends excluded, keeps out of the top centre a header keeps for the mark."""
    keep = top_centre(p)
    return keep is None or x1 <= keep[0] or x0 >= keep[2] or y1 <= keep[1] or y0 >= keep[3]


# --------------------------------------------------------------------------- the parchment
def _grain(uid: str, night: bool) -> str:
    """A pattern tile of the parchment's grain, 41 by 31: specks and short fibres of see-through ink by day, and
    of the lantern's warm light and of shadow by night, so one tile ages the parchment, the sea and the land."""
    rnd = random.Random(11)
    cols: dict = {}
    dark = f"{X['grain']}:.16" if not night else f"{X['shade_ink']}:.3"
    faint = f"{X['grain']}:.09" if not night else f"{PARCH[6]}:.035"
    for _ in range(26):
        x, y = rnd.randrange(41), rnd.randrange(31)
        _put(cols, dark if rnd.random() < 0.45 else faint, x, y)
    for _ in range(6):
        x, y = rnd.randrange(38), rnd.randrange(31)
        for i in range(rnd.choice((2, 3))):
            _put(cols, faint, x + i, y)
    return f'<pattern id="{uid}g" width="41" height="31" patternUnits="userSpaceOnUse">{_paths(cols)}</pattern>'


def _foxing(p: Pix, x0, y0, x1, y1, night, seed, n=5):
    """Foxing: a few brown spots where the parchment has aged, each a darker core in a soft ring."""
    rnd = random.Random(seed)
    cols: dict = {}
    core = f"{X['grain']}:.2" if not night else f"{X['shade_ink']}:.3"
    ring = f"{X['grain']}:.09" if not night else f"{X['shade_ink']}:.16"
    for _ in range(n):
        cx, cy = rnd.uniform(x0 + 6, x1 - 6), rnd.uniform(y0 + 4, y1 - 4)
        r = rnd.uniform(1.6, 3.4)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                d = math.hypot((x + 0.5 - cx) / r, (y + 0.5 - cy) / (r * 0.8))
                if d < 0.45:
                    _put(cols, core, x, y)
                elif d < 1 and (x * 7 + y * 3) % 4:
                    _put(cols, ring, x, y)
    p.under.append(_paths(cols))


def _fold(p: Pix, x, y0, y1, night):
    """A fold in the parchment, upright at column x: its lit side and its shadowed side."""
    lit = f"{C['white']}:.22" if not night else f"{PARCH[6]}:.05"
    dark = f"{X['grain']}:.13" if not night else f"{X['shade_ink']}:.32"
    p.under.append(f'<path stroke="{lit.split(":")[0]}" stroke-opacity="{lit.split(":")[1]}" d="M{x + .5} {y0}V{y1}"/>'
                   f'<path stroke="{dark.split(":")[0]}" stroke-opacity="{dark.split(":")[1]}" '
                   f'd="M{x + 1.5} {y0}V{y1}"/>')


def night_band(p: Pix, y: int) -> str:
    """The night parchment's colour at row y: dark at the top and the foot, warmer through the middle."""
    n = len(NIGHT_SKY)
    return NIGHT_SKY[min(n - 1, max(0, int(y * n / max(1, p.h))))]


def _ground(p: Pix, night: bool, x, y, w, h):
    """The plain parchment over a box: one colour by day, the night's bands by night."""
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
        return
    n = len(NIGHT_SKY)
    edges = [round(i * p.h / n) for i in range(n + 1)]
    for i, col in enumerate(NIGHT_SKY):
        a, b = max(y, edges[i]), min(y + h, edges[i + 1])
        if b > a:
            p.under.append(f'<rect x="{x}" y="{a}" width="{w}" height="{b - a}" fill="{col}"/>')


# --------------------------------------------------------------------------- the calm round the words
# How the sea's marks (its wave lines, the rhumb lines, the parchment's grain, foxing and fold) give way round a
# word: (units clear across, units clear down, how much of them is taken away), from the outermost in. Within
# two units of a word's box nothing of them is left.
CALM = ((6, 4, 0.5), (2, 2, 1.0))


def _strips(boxes, w: int, h: int) -> list:
    """The union of `boxes` (x0, y0, x1, y1), kept to the sheet, as rectangles that do not overlap: row by row
    the runs the boxes cover, and rows that cover the same runs merged."""
    rows = []
    for y in range(h):
        runs = sorted((max(0, a), min(w, c)) for a, b, c, d in boxes if b <= y < d and a < c)
        merged: list = []
        for a, c in runs:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], c))
            else:
                merged.append((a, c))
        rows.append(tuple(merged))
    rects, start = [], 0
    for y in range(1, h + 1):
        if y == h or rows[y] != rows[start]:
            rects += [(a, start, c, y) for a, c in rows[start]]
            start = y
    return rects


def calm_mask(p: Pix) -> str:
    """The mask that keeps the sea calm round the words: the whole sheet shows, but within a few units of every
    word's box the marks it masks fade out by steps (see CALM) and next to the word are gone. On a header only
    the chart above its rule carries marks, so only the words there are calmed."""
    w, h = p.w, p.h
    top = getattr(p, "chart", (None, h))[1]
    parts = [f'<rect width="{w}" height="{h}" fill="{C["white"]}"/>']
    for (mx, my, a) in CALM:
        rects = _strips([(math.floor(x0) - mx, math.floor(y0) - my, math.ceil(x1) + mx, math.ceil(y1) + my)
                         for (x0, y0, x1, y1) in p.words if y0 < top], w, top)
        if rects:
            d = "".join(f"M{x0} {y0}h{x1 - x0}v{y1 - y0}h{x0 - x1}z" for (x0, y0, x1, y1) in rects)
            parts.append(f'<path fill="{INK[0]}"' + ("" if a >= 1 else f' fill-opacity="{num(a)}"') + f' d="{d}"/>')
    return f'<mask id="calm" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">{"".join(parts)}</mask>'


def _calm_open(p: Pix):
    """Set the sheet's calm in its definitions before a word is set: for now it masks nothing, and `calm` lays
    it round the words once they are all set."""
    if not hasattr(p, "calm_at"):
        p.calm_at = len(p.defs)
        p.defs.append(f'<mask id="calm" maskUnits="userSpaceOnUse" x="0" y="0" width="{p.w}" height="{p.h}">'
                      f'<rect width="{p.w}" height="{p.h}" fill="{C["white"]}"/></mask>')


def calm(p: Pix):
    """Lay the calm round every word set so far (see `calm_mask`)."""
    if hasattr(p, "calm_at"):
        p.defs[p.calm_at] = calm_mask(p)


def _calmed(p: Pix, n: int):
    """Gather what has been laid under the drawing since its nth piece into one group the calm masks."""
    if len(p.under) > n:
        p.under[n:] = [f'<g mask="url(#calm)">{"".join(p.under[n:])}</g>']


def paper(p: Pix, night: bool, uid: str = "p"):
    """The parchment a footer, an element or a placard is drawn on; by night the same parchment on the
    navigator's table, dark at its top and foot and warmer through the middle where the lantern's light falls.
    An element's parchment is aged and grained, foxed here and there and folded down the middle of a wide sheet,
    all of it calmed round the words once they are set (see `calm`); a footer's and a placard's, which their words
    cover from end to end, are left plain."""
    _ground(p, night, 0, 0, p.w, p.h)
    if uid.startswith("e"):
        _calm_open(p)
        n = len(p.under)
        p.defs.append(_grain(uid, night))
        p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="url(#{uid}g)"/>')
        _foxing(p, BAND, BAND, p.w - BAND, p.h - BAND, night, seed=p.w * 7 + p.h, n=max(2, p.w * p.h // 9000))
        if p.w >= 300:
            _fold(p, p.w // 2, BAND, p.h - BAND, night)
        _calmed(p, n)
    if night:
        falloff(p, p.h)


# --------------------------------------------------------------------------- the chart a header opens on
WAVE_W, WAVE_H = 48, 24
# The swell lines an engraver cuts for the open sea, of three lengths, each a low crest.
SWELLS = {3: ((0, 1), (1, 0), (2, 1)), 5: ((0, 1), (1, 0), (2, 0), (3, 0), (4, 1)),
          7: ((0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 1), (6, 1))}


def _waves(uid: str, night: bool) -> str:
    """A pattern tile of the open sea's swell lines, 48 by 24, as an engraver cuts them: four rows of short crests
    of three lengths, set at loose and uneven spacing so the tile does not show itself, the rows staggered."""
    col = X["wave"] if not night else DEEP[5]
    rnd = random.Random(23)
    cols: dict = {}
    for r, y in enumerate((2, 8, 14, 20)):
        x = rnd.randrange(WAVE_W)
        for _ in range(2 + r % 2):
            n = rnd.choice((3, 5, 5, 7))
            for (dx, dy) in SWELLS[n]:
                _put(cols, col, (x + dx) % WAVE_W, y + dy)
            x += n + rnd.randrange(9, 17)
    return (f'<pattern id="{uid}w" width="{WAVE_W}" height="{WAVE_H}" patternUnits="userSpaceOnUse">'
            f'{_paths(cols)}</pattern>')


def coast_profile(n: int, base, amp: float, seed: int, run: int = 3) -> list:
    """A coastline's reach at each of `n` rows: `base(i)` and a wander of up to `amp` either side, holding each
    reach for at least `run` rows where it wanders, so the coast steps as a drawn coast does in pixels (and its
    columns of ink are each one stroke)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    out, held, since = [], None, 0
    for i in range(n):
        u = i / max(1, n - 1)
        wander = (0.55 * math.sin(2 * math.pi * 1.4 * u + ph[0]) + 0.3 * math.sin(2 * math.pi * 3.3 * u + ph[1])
                  + 0.15 * math.sin(2 * math.pi * 7.9 * u + ph[2]))
        x = round(base(u) + amp * wander)
        if held is None or (x != held and (since >= run or abs(x - held) > 2)):
            held, since = x, 0
        since += 1
        out.append(held)
    return out


# The water lines an engraver runs out from a coast: how far out each lies, and the dashes it is broken into
# (a dash of `on` in every `every` along it), close and long by the shore and looser further out.
WATER_LINES = ((3, 9, 7), (6, 7, 4), (10, 6, 2))


def _water_lines(p: Pix, lands, rule: int, night: bool) -> str:
    """The water lines following every coast of the chart out into the sea, as an engraver runs them: each the
    sea's cells at one distance from the land, measured round bays and points alike, broken into dashes that
    loosen the further out it lies. Returns their paths."""
    land = set()
    for side, _, reach in lands:
        for y, r in enumerate(reach[:rule]):
            if r is not None:
                land.update((x, y) for x in (range(0, max(0, r)) if side < 0 else range(r + 1, p.w)))
    if not land:
        return ""
    far = WATER_LINES[-1][0] + 1
    dist = {q: 0.0 for q in land}
    heap = [(0.0, q) for q in land if any((q[0] + u, q[1] + v) not in land for u, v in ((1, 0), (-1, 0), (0, 1),
                                                                                         (0, -1)))]
    heapq.heapify(heap)
    while heap:
        d, (x, y) = heapq.heappop(heap)
        if d > dist.get((x, y), far):
            continue
        for u, v, pace in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.41), (1, -1, 1.41),
                           (-1, 1, 1.41), (-1, -1, 1.41)):
            q = (x + u, y + v)
            out = d + pace
            if out < far and 0 <= q[0] < p.w and 0 <= q[1] < rule and out < dist.get(q, far):
                dist[q] = out
                heapq.heappush(heap, (out, q))
    col = DEEP[5] if night else X["wave"]
    cols: dict = {}
    for (x, y), d in dist.items():
        for (at, every, on) in WATER_LINES:
            if at - 0.5 <= d < at + 0.5 and ((x + y) // 2) % every < on:
                _put(cols, col, x, y)
    return _paths(cols)


def _land_path(side: int, reach: list, w: int) -> str:
    """A land's region, from the edge on its `side` in to its reach at each row, as one path of level and upright
    steps."""
    out = []
    y = 0
    n = len(reach)
    while y < n:
        if reach[y] is None:
            y += 1
            continue
        start = y
        pts = []
        while y < n and reach[y] is not None:
            x = reach[y] if side < 0 else reach[y] + 1
            if not pts or pts[-1][1] != x:
                pts.append((y, x))
            y += 1
        edge = 0 if side < 0 else w
        d = [f"M{edge} {start}"]
        for (yy, x) in pts:
            d.append(f"V{yy}H{x}")
        d.append(f"V{y}H{edge}z")
        out.append("".join(d))
    return "".join(out)


def chart_lands(kind: str, w: int, rule: int, top: int = 0) -> list:
    """The lands of a header's chart, each (side, known, reach by row from 0 to the rule): `side` -1 for a land
    coming in from the left edge, 1 from the right; `known` a land washed in ochre with its coast drawn and
    water-lined, else the unknown land left bare with its coast dotted; `reach` how far it comes in at each row
    (None where it does not reach that row)."""
    n = rule
    if kind == "H1" and w > 300:
        # The known coast on the left, the city on its promontory and the bay under it where the river comes
        # down, falling back to leave the sea for the compass rose and the cog; the unknown land on the right,
        # where the dragon is, its coast wandering down from under the wind head and back to the edge.
        city = h1_city_base(rule)

        def left(u):
            y = u * n
            if y <= city + 1:
                return 38 + 12 * (y / max(1, city)) ** 1.6
            return max(-4.0, 50 - 54 * min(1.0, (y - city - 1) / 9.0) ** 0.7)

        def right(u):
            y = u * n
            top = h1_dragon_base(rule)
            if y <= top + 2:
                return w - 30 - 14 * math.sin(math.pi * 0.9 * min(1.0, y / max(1, top)))
            return min(w + 4.0, w - 42 + 46 * min(1.0, (y - top - 2) / 9.0) ** 0.8)
        lr = coast_profile(n, left, 2.2, 3)
        rr = coast_profile(n, right, 2.6, 5)
        return [(-1, True, [x if x > 1 else None for x in lr]), (1, False, [x if x < w - 1 else None for x in rr])]
    if kind == "H2" and w > 300:
        def cape(u):
            y = u * n
            start = n - 34
            if y < start:
                return w + 4.0
            return w - 8 - 22 * math.sin(math.pi / 2 * min(1.0, (y - start) / 30.0))
        rr = coast_profile(n, cape, 1.3, 7)
        return [(1, True, [x if x < w - 1 else None for x in rr])]
    if kind == "H1":
        # A phone's map: the known coast rising at the left to the promontory the city stands on, and the unknown
        # land at the right where the dragon is, each as tall as the rows under the words allow.
        lo, ro = max(top + 10, n - 46), max(top + 6, n - 42)

        def left(u):
            y = u * n
            return -4.0 if y < lo else 6 + 34 * math.sin(math.pi / 2 * min(1.0, (y - lo) / 18.0))

        def right(u):
            y = u * n
            return w + 4.0 if y < ro else w - 6 - 34 * math.sin(math.pi / 2 * min(1.0, (y - ro) / 16.0))
        lr = coast_profile(n, left, 1.0, 13)
        rr = coast_profile(n, right, 1.0, 15)
        return [(-1, True, [x if x > 1 else None for x in lr]), (1, False, [x if x < w - 1 else None for x in rr])]
    if kind == "H2" and w <= 300:
        # A phone's section: the cape coming in from the right at the foot, under the words, as the wide section
        # has it, broad enough for its watch tower or the lantern (see `phone_rose`).
        lo = max(top + 8, n - 26)

        def cape(u):
            y = u * n
            return w + 4.0 if y < lo else w - 6 - 22 * math.sin(math.pi / 2 * min(1.0, (y - lo) / 14.0))
        return [(1, True, [x if x < w - 1 else None for x in coast_profile(n, cape, 1.0, 19)])]
    if kind == "H3" and w <= 300:
        # A phone's strip: the known coast coming down to the sea at the left under the words, its point broad
        # enough for the walled city, beside the great serpent (see `phone_serpent`).
        lo = max(top + 8, n - 32)

        def coast(u):
            y = u * n
            return -4.0 if y < lo else 4 + 36 * math.sin(math.pi / 2 * min(1.0, (y - lo) / 14.0))
        return [(-1, True, [x if x > 1 else None for x in coast_profile(n, coast, 1.0, 17)])]
    return []


def h1_city_base(rule: int) -> int:
    """The row the walled city stands on in a wide H1's left column, lower as the sheet is taller."""
    return 16 + round((rule - 16) * 0.46)


def h1_dragon_base(rule: int) -> int:
    """The row the dragon stands on in the unknown land at a wide H1's right."""
    return 16 + max(25, round((rule - 16) * 0.33))


def chart(p: Pix, night: bool, kind: str, rule: int, motion: bool = False, uid: str = "p"):
    """The paper a header is drawn on: the chart above its rule, the sea washed in faded verdigris with its fine
    wave lines drifting in a moving header, the known land in ochre with its coast inked and water-lined, the
    unknown land left bare with its coast dotted, grained and foxed and folded down the middle of a wide sheet (a
    sheet drawn lighter to fit its budget leaves out only the grain, the foxing and the fold), all its marks
    calmed round the words once they are set (see `calm`); and under the rule the plain parchment of the chart's
    margin the figures are written on. By night the same chart on the navigator's table: the sea dark, the land
    and the parchment fallen to shadow, and the coasts gilt so they catch the lantern's light."""
    w, h = p.w, p.h
    p.chart = (kind, rule)
    _calm_open(p)
    _ground(p, night, 0, rule, w, h - rule)       # the sea hides the parchment above the rule
    sea = C["sea_night"] if night else C["sea"]
    p.under.append(f'<rect width="{w}" height="{rule}" fill="{sea}"/>')
    p.defs.append(_waves(uid, night))
    n = len(p.under)
    if motion:
        steps = ";".join(str(i) for i in range(WAVE_W))        # a translation's y left out is 0
        p.under.append(f'<g><rect x="-{WAVE_W}" width="{w + WAVE_W}" height="{rule}" fill="url(#{uid}w)"/>'
                       f'<animateTransform attributeName="transform" type="translate" values="{steps}" '
                       f'dur="{num(WAVE_W * 0.5)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
    else:
        p.under.append(f'<rect width="{w}" height="{rule}" fill="url(#{uid}w)"/>')
    _calmed(p, n)
    lands = chart_lands(kind, w, rule, getattr(p, "words_end", 0))
    p.lands = lands
    for side, known, reach in lands:
        fill = (DUSK[3] if known else NIGHT[2]) if night else (C["land"] if known else C["paper"])
        rim = (DUSK[4] if known else NIGHT[3]) if night else (LAND[4] if known else PARCH[4])
        coast = (GOLD[2] if known else GOLD[1]) if night else (INK[3] if known else INK[4])
        if fill:
            p.under.append(f'<path fill="{fill}" d="{_land_path(side, reach, w)}"/>')
        # the coast steps down the land's edge row by row, and the rim lies a pixel inside it: the one line is
        # drawn once and stroked twice, the unknown land's coast dotted by a chequer of its ink
        rows: dict = {}
        prev = None
        for y, r in enumerate(reach):
            if r is None:
                prev = None
                continue
            edge = r - 1 if side < 0 else r + 1
            for x in ([edge] if prev is None else range(min(prev, edge), max(prev, edge) + 1)):
                rows.setdefault(y, []).append(x - side)
            prev = edge
        if not rows:
            continue
        lid = f"{uid}L{len(p.defs)}"
        p.defs.append(f'<path id="{lid}" d="{Pix._d(rows)}"/>')
        paint = coast
        if not known:
            paint = f"url(#{lid}k)"
            p.defs.append(f'<pattern id="{lid}k" width="2" height="2" patternUnits="userSpaceOnUse">'
                          f'<path stroke="{coast}" d="M1 .5h1m-2 1h1"/></pattern>')
        p.under.append(f'<use href="#{lid}" x="{side}" stroke="{paint}"/><use href="#{lid}" stroke="{rim}"/>')
    n = len(p.under)
    p.under.append(_water_lines(p, lands, rule, night))
    if not p.lite:
        # the parchment's age, which a drawing made lighter to fit its budget leaves out
        p.defs.append(_grain(uid, night))
        p.under.append(f'<rect width="{w}" height="{rule}" fill="url(#{uid}g)"/>')
        _foxing(p, BAND, BAND, w - BAND, rule, night, seed=w * 3 + h, n=max(3, w * rule // 8000))
        if w > 300:
            _fold(p, w // 2, BAND, rule, night)
    _calmed(p, n)
    if night:
        falloff(p, rule)


def falloff(p: Pix, rule: int):
    """By night the chart falls dark toward its edges, beyond the lantern's light: three steps of shadow laid
    along its sides and its top, under everything drawn on it."""
    w = p.w
    steps = ((0, 0.34), (6, 0.22), (13, 0.12)) if w > 300 else ((0, 0.3), (5, 0.16))
    if rule < 70:
        steps = ((0, 0.28), (5, 0.14))
    for d, a in steps:
        p.under.append(f'<path fill="{X["shade_ink"]}" fill-opacity="{num(a)}" d="M{d} {d}H{w - d}V{rule}H{w - d - 6}'
                       f'V{d + 6}H{d + 6}V{rule}H{d}z"/>')


# --------------------------------------------------------------------------- the ruled border
def _tones(night: bool) -> dict:
    """The border's tones: ink and parchment by day; by night its rules and its scale gilt in the lantern's
    light against the shadowed parchment."""
    if night:
        return dict(rule=GOLD[2], gap=NIGHT[2], dark=NIGHT[0], light=GOLD[3], lit=GOLD[5], shade=GOLD[1])
    return dict(rule=K, gap=PARCH[6], dark=INK[2], light=PARCH[6], lit=GOLD[4], shade=GOLD[2])


def _border(uid: str, night: bool, vertical: bool) -> str:
    """A pattern tile of the ruled border, 8 along and 5 deep: an outer rule, a fine gap, the graduated scale
    of dark and light degrees four long, and an inner rule; turned a quarter down a side."""
    T = _tones(night)
    cols: dict = {}
    for a in range(8):
        for d in range(BAND):
            c = T["rule"] if d in (0, BAND - 1) else T["gap"] if d == 1 else (T["dark"] if a < 4 else T["light"])
            x, y = (d, a) if vertical else (a, d)
            _put(cols, c, x, y)
    w, h = (BAND, 8) if vertical else (8, BAND)
    return f'<pattern id="{uid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{_paths(cols)}</pattern>'


def _scale_bar(uid: str, night: bool, y: int) -> str:
    """The pattern of a chart's scale bar, the plinth a footer stands on, starting at row `y`: between its rules a
    row of fine graduation, a tick every second column, over a bar of leagues ten long, dark and light by turns,
    its lower row the reverse of its upper as a scale is ruled."""
    T = _tones(night)
    cols: dict = {}
    for a in range(20):
        for d in range(BAND):
            if d in (0, BAND - 1):
                c = T["rule"]
            elif d == 1:
                c = T["dark"] if a % 2 == 0 else T["light"]
            else:
                c = T["dark"] if (a < 10) == (d == 2) else T["light"]
            _put(cols, c, a, d)
    return (f'<pattern id="{uid}" y="{y}" width="20" height="{BAND}" patternUnits="userSpaceOnUse">'
            f'{_paths(cols)}</pattern>')


def corner(p: Pix, x, y, night, L="base"):
    """A corner piece where two rules meet: a square of the rule with a gilt boss in it, drawn once a file and
    placed."""
    key = ("corner", night)
    if key not in p.syms:
        T = _tones(night)
        cells = {}
        for j in range(BAND):
            for i in range(BAND):
                edge = i in (0, BAND - 1) or j in (0, BAND - 1)
                inner = T["lit"] if (i, j) == (1, 1) else T["shade"] if (i, j) == (3, 3) else GOLD[4]
                cells[(i, j)] = T["rule"] if edge else inner
        p.symbol(key, cells)
    p.use(key, x, y, L)


def frame(p: Pix, night: bool, footer: bool = False, uid: str = "fr"):
    """The sheet's border: a double rule round all four sides with the graduated scale of degrees between,
    dark and light by turns, and a corner piece where the sides meet; a footer stands on the chart's scale bar,
    its leagues longer and ticked."""
    w, h = p.w, p.h
    p.defs.append(_border(uid + "h", night, False))
    p.defs.append(_border(uid + "v", night, True))
    p.shapes["base"].append(f'<rect width="{w}" height="{BAND}" fill="url(#{uid}h)"/>')
    p.defs.append(f'<rect id="{uid}V" width="{BAND}" height="{h}" fill="url(#{uid}v)"/>')
    p.shapes["base"].append(f'<use href="#{uid}V"/><use href="#{uid}V" x="{w - BAND}"/>')
    if footer:
        p.defs.append(_scale_bar(uid + "s", night, h - BAND))
        p.shapes["base"].append(f'<rect y="{h - BAND}" width="{w}" height="{BAND}" fill="url(#{uid}s)"/>')
        for x in range(BAND, w - BAND):
            p.apx(x, h - BAND - 1, X["shade_ink"], 0.18 if not night else 0.4, "base")
    else:
        p.shapes["base"].append(f'<rect y="{h - BAND}" width="{w}" height="{BAND}" fill="url(#{uid}h)"/>')
    for (cx, cy) in ((0, 0), (w - BAND, 0), (0, h - BAND), (w - BAND, h - BAND)):
        corner(p, cx, cy, night)


# --------------------------------------------------------------------------- compass stars and roses
def star_cells(cx: float, cy: float, points) -> dict:
    """The cells of a star of compass points about (cx, cy): each of `points` is (angle in degrees from north,
    length, half-width at the hub, light tone, dark tone), drawn in order so a later point lies over an earlier
    one, each split down its length into a lit half and a shaded half."""
    cells = {}
    for (deg, rk, wk, lt, dk) in points:
        ang = math.radians(deg - 90)
        ca, sa = math.cos(ang), math.sin(ang)
        for y in range(math.floor(cy - rk) - 1, math.ceil(cy + rk) + 1):
            for x in range(math.floor(cx - rk) - 1, math.ceil(cx + rk) + 1):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                along = dx * ca + dy * sa
                perp = -dx * sa + dy * ca
                if -0.3 <= along <= rk and abs(perp) <= wk * (1 - max(0.0, along) / rk) + 0.3:
                    cells[(x, y)] = lt if perp < 0 else dk
    return cells


def outline(cells: dict, col: str) -> dict:
    """The cells round `cells` that a one-pixel outline in `col` takes."""
    out = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                out[q] = col
    return out


def gilt_star_cells(night: bool) -> dict:
    """A small gilded compass star, 11 by 11 about its centre cell (5, 5): four long points and four short,
    gilt lit and shaded, outlined in ink."""
    pts = [(d, 3.4, 1.15, GOLD[5], GOLD[2]) for d in (45, 135, 225, 315)]
    pts += [(d, 5.4, 1.5, GOLD[6] if night else GOLD[5], GOLD[3] if night else GOLD[2]) for d in (0, 90, 180, 270)]
    cells = star_cells(5.5, 5.5, pts)
    cells.update(outline(cells, NIGHT[0] if night else K))
    cells[(5, 5)] = VERM[4] if night else VERM[3]
    gap = _tones(night)["gap"]
    for y in range(1, 10):
        for x in range(-2, 13):
            if (x, y) not in cells and (abs(x - 5) < 6 or (x - 5) ** 2 + (y - 5) ** 2 <= 40):
                cells[(x, y)] = gap
    return cells


# --------------------------------------------------------------------------- the top band and the wind heads
# A cherub's head blowing on its cloud, 22 by 22, facing right: its curls of gold (Y y q), its face (F), the near
# cheek blown round (S highlight, c blush), its eyes screwed shut (e) under their brows (b), the nose (n) and the
# lips pursed round the wind (L, the mouth m); under it the cloud it rides on (W lit, w shaded), hanging down the
# border; outlined in ink (k). Wherever it reaches past column 12 it keeps above row 14, and below that it keeps
# to the border's side, so no word or dimension a layout sets near a corner comes within two units of it.
WIND_HEAD = [
    "......kkkkkkk.........",
    "....kkYYyYYYykk.......",
    "...kYyyqyYyqyYyk......",
    "..kYqyYyqyyYqyyyk.....",
    ".kYyqyyqkkkkkkqyyk....",
    ".kyqyykkFFFFFFkkyk....",
    "kYyqkkFFbbbFFbbFFk....",
    "kyqykFFeeeFFFeeFFFk...",
    "kYqkFFSSFFFFFFFnFFk...",
    "kyqkFSSScFFFFFnnFFFk..",
    "WkqkFSSccFFFFFFFFFLLk.",
    "WWkkFSccccFFFFFFFLmmLk",
    "WWWWkFccFFFFFFFFFFLLk.",
    "wWWWWkkFFFFFFFFFkkkk..",
    "wwWWWWWkkkkkk.........",
    "kwwWWWWWWkWWk.........",
    ".kwwWWWkWWWWk.........",
    "kWwwWWWWkkkk..........",
    "kWWwwWWk..............",
    ".kWWwwWk..............",
    ".kwWWwk...............",
    "..kkkk................",
]
MOUTH = (21, 11)    # the lips' tip, where the wind leaves them


def wind_pal(night: bool) -> dict:
    """A wind head's tones: its curls of gold, its face on the hand's lightest skin (the face its base tone and the
    nose a tone darker, by day and by night alike, and by day the blown cheek a tone lighter), the blush and lips
    of vermilion and its cloud."""
    k = -1 if night else 0
    return {"k": K, "Y": GOLD[5 + k], "y": GOLD[4 + k], "q": GOLD[2 + k], "F": SKIN[3], "S": SKIN[4 + k],
            "c": VERM[5 + k], "e": INK[1], "b": GOLD[1], "n": SKIN[2], "L": VERM[4 + k], "m": VERM[1],
            "W": NIGHT[6] if night else PARCH[6], "w": NIGHT[4] if night else PARCH[4]}


def wind_head(p: Pix, x, y, night, flip=False, L="base"):
    """A cherub's head on its cloud at a top corner, top-left at (x, y), blowing to the right (to the left when
    `flip`). It is drawn once a file and placed."""
    key = ("windhead", night)
    w = len(WIND_HEAD[0])
    if key not in p.syms:
        pal = wind_pal(night)
        sid = p.symbol(key, {(i, j): pal[ch] for j, row in enumerate(WIND_HEAD) for i, ch in enumerate(row)
                             if ch != "."})
        p.symbol(("windhead-twin", night), {}, shapes=f'<use href="#{sid}" transform="matrix(-1 0 0 1 {w} 0)"/>')
    p.use(("windhead-twin", night) if flip else key, x, y, L)
    _mark(p, {(x + (w - 1 - i if flip else i), y + j) for j, row in enumerate(WIND_HEAD)
              for i, ch in enumerate(row) if ch != "."})


def wind_stream(p: Pix, x, y, night, reach=32, flip=False, L="base"):
    """The wind a head blows from its lips at (x, y): three lines fanning a little as they go, each wandering and
    breaking into dashes toward its end; to the left when `flip`. Nothing goes below row 13."""
    col, tip = (INK[2], INK[5]) if not night else (GOLD[3], GOLD[1])
    s = -1 if flip else 1
    for (dy, ln, ph) in ((-2, reach, 0.0), (0, reach + 6, 1.7), (2, reach - 8, 3.1)):
        for i in range(ln):
            yy = min(13, y + dy + round(math.sin(i / 3.6 + ph)))
            if i > ln - 9 and i % 3 == 2:
                continue
            p.px(x + s * i, yy, col if i < ln - 9 else tip, L)


def top_band(p: Pix, night: bool, uid: str = "tb"):
    """A header's top band across the border: the outer rule, two graduated scales of degrees and minutes
    between rules, and a gilded compass star set into it at every station, each with a glint that twinkles in a
    moving header; its shadow lies along the chart under it. The stations are an even number, evenly spaced, so
    the run of stars ends either side of the top centre the header keeps for the month's mark (see `top_centre`):
    the band runs on behind the mark, and no star is cut by it."""
    w = p.w
    T = _tones(night)
    cols: dict = {}
    tile = 8
    for a in range(tile):
        for d in range(TOP_BAND - 1):
            if d in (0, 4, TOP_BAND - 2):
                c = T["rule"]
            elif d in (1, 7):
                c = T["gap"]
            elif d in (2, 3):
                c = T["dark"] if a < 4 else T["light"]
            elif d == 5:
                c = T["dark"] if a % 2 == 0 else T["light"]
            else:
                c = T["light"]
            _put(cols, c, a, d)
    p.defs.append(f'<pattern id="{uid}" width="{tile}" height="{TOP_BAND - 1}" patternUnits="userSpaceOnUse">'
                  f'{_paths(cols)}</pattern>')
    p.shapes["base"].append(f'<rect width="{w}" height="{TOP_BAND - 1}" fill="url(#{uid})"/>')
    for x in range(BAND, w - BAND):
        p.apx(x, TOP_BAND - 1, X["shade_ink"], 0.16 if not night else 0.4, "base")
    key = ("giltstar", night)
    if key not in p.syms:
        p.symbol(key, gilt_star_cells(night))
    n = max(2, (w - 64) // 44)
    n += n % 2
    gap = (w - 64) / (n - 1)
    for i in range(n):
        cx = round(32 + i * gap)
        p.use(key, cx - 5, -1)
        p.px(cx - 1, 1, C["white"] if not night else GOLD[6], p.twinkle(i))
    _mark(p, {(x, y) for x in range(w) for y in range(TOP_BAND)})


def garland(p: Pix, night: bool, kind: str):
    """A header's top: the band of graduated scales and gilded compass stars, and at each top corner a wind
    head blowing a stream of wind lines in toward the map under the band."""
    top_band(p, night)
    w = p.w
    hw = len(WIND_HEAD[0])
    wind_head(p, 0, 0, night)
    wind_head(p, w - hw, 0, night, flip=True)
    reach = 32 if w > 300 else 22
    wind_stream(p, MOUTH[0] + 1, 12, night, reach=reach)
    wind_stream(p, w - MOUTH[0] - 2, 12, night, reach=reach, flip=True)


# --------------------------------------------------------------------------- the engraved title on its banderole
def _ribbon_tones(night: bool) -> dict:
    """The banderole's tones: pale parchment with its reverse shaded by day; by night in shadow, its upper edge
    gilt where the lantern catches it."""
    if night:
        return dict(face=NIGHT[5], lit=NIGHT[6], shade=NIGHT[3], back=NIGHT[4], backd=NIGHT[2], edge=GOLD[3],
                    foot=NIGHT[0], k=NIGHT[0], tail=GOLD[1])
    return dict(face=PARCH[6], lit=PARCH[6], shade=PARCH[4], back=PARCH[4], backd=PARCH[2], edge=K, foot=K, k=K,
                tail=K)


def _free_columns(p: Pix, x, top, bot, step, most) -> int:
    """How many columns from x outward (by `step`) are free for a banderole's tail between rows top and bot:
    no pixel of the border or a dimension there, and no word within a unit."""
    n = 0
    base = p.layers["base"]
    drawn = getattr(p, "filled", set())
    for i in range(most):
        xx = x + step * i
        if xx < BAND + 1 or xx > p.w - BAND - 2:
            break
        if (any((xx, yy) in base for yy in range(top, bot + 1))
                or not p.clear_of_words(xx - 1, top - 1, xx + 2, bot + 2)):
            break
        if any((xx + dx, yy) in drawn for dx in (-2, -1, 0, 1, 2) for yy in range(top - 4, bot + 5)):
            break
        n += 1
    return n


def banderole(p: Pix, x0, x1, top, bot, night, left=9, right=9, L="base"):
    """The ribbon a title is engraved on, from x0 to x1 (exclusive), rows top to bot: its face lit along its upper
    edge and hatched in shadow along its foot, and its ends folded back level behind it as tails two rows
    narrower, hatched as its reverse and cut with a swallowtail notch, each as long as the room at that end
    allows (`left`, `right`)."""
    T = _ribbon_tones(night)
    H = bot - top + 1
    for side, room in ((-1, left), (1, right)):
        e = min(room, max(4, round(H * 0.45)))
        if e < 3:
            continue
        t0, t1 = top + 2, bot - 2
        mid, half = (t0 + t1) / 2, (t1 - t0) / 2
        depth = min(4, max(2, round(half * 0.7)), e - 2)
        for i in range(1, e + 1):
            xx = x0 - i if side < 0 else x1 - 1 + i
            for yy in range(t0, t1 + 1):
                reach = e - depth * (1 - abs(yy - mid) / max(1, half))
                if i > reach + 0.5:
                    continue
                if yy in (t0, t1) or i > reach - 0.5:
                    c = T["tail"]
                elif i == 1:
                    c = T["backd"]
                else:
                    c = T["backd"] if (yy - t0) % 2 == 1 else T["back"]
                p.px(xx, yy, c, L)
    rects = [(top, 1, T["edge"]), (top + 1, 1, T["lit"]), (top + 2, bot - top - 2, T["face"]), (bot, 1, T["foot"])]
    rects += [(yy, 1, T["shade"]) for yy in range(top + 2, bot) if yy >= bot - 2 and (yy - bot) % 2 == 1]
    shapes = p.shapes[L] if L in p.shapes else p.shapes[p.layer(L)]
    for (yy, hh, c) in rects:
        shapes.append(f'<rect x="{x0}" y="{yy}" width="{x1 - x0}" height="{hh}" fill="{c}"/>')
    shapes.append(f'<rect x="{x0}" y="{top + 1}" width="1" height="{bot - top - 1}" fill="{T["k"]}"/>'
                  f'<rect x="{x1 - 1}" y="{top + 1}" width="1" height="{bot - top - 1}" fill="{T["k"]}"/>')
    _mark(p, {(x, y) for x in range(x0, x1) for y in range(top, bot + 1)})


def _hatch_fill(face: str, line: str):
    """A paint for an engraver's shadow: fine level lines of `line` on every other row of the letters' pixels,
    and between them the banderole's own `face`, so the lines lie on the ribbon as if cut into it."""
    def fill(r, c, scale, night):
        return line if r % 2 == 0 else face
    return fill


HATCH_DAY = Paint("hatchd", _hatch_fill(PARCH[6], INK[4]), period=1)
HATCH_NIGHT = Paint("hatchn", _hatch_fill(NIGHT[5], GOLD[2]), period=1)


def _gilt_fill(r, c, scale, night):
    """Gilt letters by night: each row of the face a band of gold, bright where the lantern catches the top of a
    stroke and across its middle, deeper toward its foot."""
    return (GOLD[6], GOLD[5], GOLD[5], GOLD[6], GOLD[5], GOLD[4], GOLD[3])[min(6, r // scale)]


GILT = Paint("gilt", _gilt_fill)


def engraved_title(p: Pix, x, y, s, night, scale, colour=None, lit=None) -> int:
    """A line of a title engraved as on a copper plate: solid letters of ink cut with an engraver's shadow of fine
    level lines down and to their right, on a banderole that unfurls a little past them each way, its tails
    folded back as far as the room at each end allows; by night the letters gilt, their upper and left edges
    catching the lantern, on a ribbon in shadow with a gilt edge. `colour` and `lit` are the letters' colour and
    how they are lit (the set's title ink and `lit`). The banderole is kept as a word, so nothing else is drawn
    over it. Returns the width."""
    w = p.measure(s, "57", scale)
    pad = max(1, scale // 2)
    top, bot = y - pad - 1, y + 7 * scale + pad
    x0, x1 = x - 3, x + w + 3
    # A phone's section and strip keep the room beside their titles for their maps: their tails are short. A wide
    # H1's banderole keeps within the column of its words, leaving the map at each side its own.
    kind = getattr(p, "kind", "")
    most_left = most_right = 4 if p.w < 300 and kind in ("H2", "H3") else 10
    if p.w > 300 and kind == "H1":
        most_left, most_right = max(0, min(10, x0 - 56)), max(0, min(10, p.w - 57 - x1))
    left = _free_columns(p, x0 - 1, top + 2, bot - 2, -1, most_left)
    right = _free_columns(p, x1, top + 2, bot - 2, 1, most_right)
    banderole(p, x0, x1, top, bot, night, left=left, right=right)
    off = pad + (1 if scale >= 4 else 0)
    if scale >= 3 or (scale == 2 and len(s) <= 14):
        n = len(p.words)
        p.text(x + off, y + off, s, INK[4], "57", scale, paint=HATCH_NIGHT if night else HATCH_DAY, night=night)
        del p.words[n:]         # the shadow is cut into the banderole, not a word of its own
    if lit is None:
        lit = dict(paint=GILT, night=True) if night else {}
    p.text(x, y, s, colour or (GOLD[5] if night else INK[1]), "57", scale, **lit)
    p.words.append((x0 - 1, top - 1, x1 + 1, bot + 1))
    for room, a, b in ((left, x0 - min(left, 10) - 1, x0), (right, x1, x1 + min(right, 10) + 1)):
        if room >= 3:
            p.words.append((a, top + 1, b, bot))
    return w


# --------------------------------------------------------------------------- the compass rose and its needle
FLEUR = ["..#..", ".###.", "#.#.#", "#####", "..#.."]


def rose_tones(night: bool) -> dict:
    """The rose's tones: its eight winds gilt and ink, the half winds in parchment and verdigris, the quarter winds
    in vermilion; by night gilt and shadow, with a gilt line round it."""
    if night:
        return dict(card=(GOLD[5], NIGHT[1]), inter=(NIGHT[6], DEEP[2]), half=(VERM[4], VERM[1]), line=GOLD[1],
                    hub=GOLD[4], ring=GOLD[2])
    return dict(card=(GOLD[5], INK[2]), inter=(PARCH[6], SEA[1]), half=(VERM[5], VERM[2]), line=K, hub=GOLD[4],
                ring=INK[3])


def rose_cells(cx: float, cy: float, R: float, night: bool) -> dict:
    """A sixteen-point compass rose of radius R about (cx, cy): the four cardinal points longest, the four between
    them shorter, the eight half winds shortest, each lit down one side and shaded down the other, all outlined,
    with a fleur-de-lis on the north point, a cross on the east, a ring through the points and a gilt hub."""
    T = rose_tones(night)
    pts = [(d + 22.5, R * 0.52, R * 0.13, *T["half"]) for d in range(0, 360, 45)]
    pts += [(d, R * 0.74, R * 0.2, *T["inter"]) for d in (45, 135, 225, 315)]
    pts += [(d, R, R * 0.25, *T["card"]) for d in (0, 90, 180, 270)]
    cells = {}
    rr = R * 0.6
    if R >= 8:
        for a in range(0, 360, 2):
            q = (math.floor(cx + rr * math.cos(math.radians(a))), math.floor(cy + rr * math.sin(math.radians(a))))
            cells[q] = T["ring"]
    cells.update(star_cells(cx, cy, pts))
    cells.update({q: c for q, c in outline(cells, T["line"]).items() if q not in cells})
    hx, hy = math.floor(cx), math.floor(cy)
    for (dx, dy) in ((-1, -1), (0, -1), (-1, 0), (0, 0)):
        cells[(hx + dx, hy + dy)] = T["hub"] if (dx, dy) != (0, 0) else GOLD[2]
    if R >= 7:
        tip = math.floor(cy - R)
        for j, row in enumerate(FLEUR):
            for i, ch in enumerate(row):
                if ch == "#":
                    cells[(hx - 2 + i, tip - 4 + j)] = GOLD[5] if j < 2 else GOLD[3]
        for q in outline({(hx - 2 + i, tip - 4 + j): 1 for j, row in enumerate(FLEUR) for i, ch in enumerate(row)
                          if ch == "#"}, T["line"]):
            cells.setdefault(q, T["line"])
    return cells


def rose(p: Pix, cx, cy, R, night, L="base"):
    """A compass rose (see `rose_cells`) centred on (cx, cy), drawn in place among the drawing's own pixels: a
    file seldom holds two of one size, and one drawn as a symbol costs more than its cells."""
    cells = rose_cells(0.0, 0.0, R, night)
    for (x, y), c in cells.items():
        p.px(cx + x, cy + y, c, L)
    _mark(p, {(cx + x, cy + y) for (x, y) in cells})
    if not hasattr(p, "roses"):
        p.roses = []
    p.roses.append((cx, cy, R))


def needle_cells(R: float, deg: float, night: bool) -> dict:
    """A magnetised needle across a rose of radius R about (0, 0), turned `deg` from north: a long diamond, its
    north half in vermilion and its south half in steel, each lit down one side, on a gilt pivot."""
    ang = math.radians(deg - 90)
    ca, sa = math.cos(ang), math.sin(ang)
    ln = R * 0.82
    cells = {}
    for y in range(math.floor(-R) - 1, math.ceil(R) + 1):
        for x in range(math.floor(-R) - 1, math.ceil(R) + 1):
            along = (x + 0.5) * ca + (y + 0.5) * sa
            perp = -(x + 0.5) * sa + (y + 0.5) * ca
            if abs(along) <= ln and abs(perp) <= 1.25 * (1 - abs(along) / ln) + 0.32:
                north = along > 0
                k = -1 if night else 0
                cells[(x, y)] = ((VERM[4 + k] if perp < 0 else VERM[2]) if north
                                 else (SLATE[5 + k] if perp < 0 else SLATE[2]))
    cells[(-1, -1)] = GOLD[5]
    cells[(0, -1)] = GOLD[4]
    cells[(-1, 0)] = GOLD[4]
    cells[(0, 0)] = GOLD[2]
    return cells


# How the needle swings before it settles: its turn from north in each step, and the share of the loop each
# step lasts; the last step, settled on north, holds the rest of the loop and is the one a still file keeps.
SWING = ((-36, 0.07), (24, 0.07), (-12, 0.07), (5, 0.07), (0, 0.72))


def needle(p: Pix, cx, cy, R, night, motion=True, dur=6.0):
    """The needle over a rose at (cx, cy), swinging and settling on north in a moving file (see SWING): each step
    of its swing drawn on its own, or on a drawing made lighter to fit its budget the settled needle itself
    turned through the same steps about its pivot, drawn once."""
    key = ("needle", R, 0, night)
    if not motion or p.lite:
        if key not in p.syms:
            p.symbol(key, needle_cells(R, 0, night))
    if not motion:
        p.use(key, cx, cy, p.layer("needle", z=1.5))
        return
    if p.lite:
        sid = p.syms[key]
        turns = ";".join(f"{deg} {cx} {cy}" for deg, _ in SWING)
        times = ";".join(num(sum(share for _, share in SWING[:i])) for i in range(len(SWING)))
        still = f'<use href="#{sid}" x="{cx}" y="{cy}"/>'
        p.raw(1.5, f'<g>{still}<animateTransform attributeName="transform" type="rotate" values="{turns}" '
                   f'keyTimes="{times}" dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></g>', still)
        return
    t = 0.0
    for i, (deg, share) in enumerate(SWING):
        key = ("needle", R, deg, night)
        if key not in p.syms:
            p.symbol(key, needle_cells(R, deg, night))
        L = p.seq(f"needle{len(getattr(p, 'roses', ()))}x{i}", t, min(1.0, t + share), dur, keep=deg == 0, z=1.5)
        p.use(key, cx, cy, L)
        t += share


def rhumb_lines(p: Pix, night, margin=3):
    """The rhumb lines raking the sea from each rose the drawing keeps (`p.roses`): sixteen fine lines from the
    rose's rim out to the border, the eight winds in ink and the half winds in verdigris, under everything drawn
    on the chart, broken where a sprite lies, `margin` short of a word and at the top centre a header keeps for
    the month's mark (see `top_centre`), and fading out as they come near a word under the sheet's calm (see
    `calm`). Drawn as fine strokes."""
    roses = getattr(p, "roses", ())
    if not roses:
        return
    kind, rule = getattr(p, "chart", ("", p.h))
    x0, y0, x1, y1 = BAND + 1, TOP_BAND + 1, p.w - BAND - 1, rule - 1
    boxes = [(a - margin, b - margin, c + margin, d + margin) for a, b, c, d in p.words]
    boxes += [top_centre(p)] if top_centre(p) else []
    base = p.layers["base"]
    cols = {INK[5] if not night else GOLD[1]: [], SEA[3] if not night else DEEP[6]: []}
    keys = list(cols)
    cells = set()
    for (cx, cy, R) in roses:
        for k in range(16):
            ang = math.radians(k * 22.5 - 90)
            dx, dy = math.cos(ang), math.sin(ang)
            col = keys[0] if k % 2 == 0 else keys[1]
            seg, t = None, R + 2.0
            while True:
                x, y = cx + dx * t, cy + dy * t
                inside = x0 <= x < x1 and y0 <= y < y1
                if not inside:
                    break
                q = (math.floor(x), math.floor(y))
                free = (q not in base and all(not (a <= x < c and b <= y < d) for a, b, c, d in boxes))
                if free:
                    cells.add(q)
                    seg = seg or (x, y)
                    end = (x, y)
                elif seg:
                    cols[col].append((seg, end))
                    seg = None
                t += 0.5
            if seg:
                cols[col].append((seg, end))
    paths = []
    for col, segs in cols.items():
        if segs:
            d = "".join(f"M{num(round(a[0], 1))} {num(round(a[1], 1))}L{num(round(b[0], 1))} {num(round(b[1], 1))}"
                        for a, b in segs if a != b)
            paths.append(f'<path stroke="{col}" stroke-width=".5" d="{d}"/>')
    if paths:
        g = (f'<g mask="url(#calm)">{"".join(paths)}</g>' if hasattr(p, "calm_at") else "".join(paths))
        p.raw(-1, g, g)
    _mark(p, cells)


# --------------------------------------------------------------------------- the cog and its route
# A cog under sail, 28 by 23, facing right: the pennant at the masthead (V v), the fighting top (H h), the yard
# and mast (M m), the square sail bellied (W lit, w shaded) with a cross of vermilion (R), the castles at stern
# and bow with their rails (C c), the clinker hull in planks of oak (H h) on a dark wale (d), and the rudder (r).
COG = [
    "..............k.............",
    ".............kVVVVvk........",
    ".............kVVvk..........",
    "............kkkkkk..........",
    "............kHhHhk..........",
    ".......kkkkkkkMkkkkkkk......",
    "......kWWWWWWRRWWWWWWk......",
    ".....kWWWWWWWRRWWWWWWWk.....",
    ".....kWWWWWWWRRWWWWWWWk.....",
    ".....kRRRRRRRRRRRRRRRRk.....",
    ".....kWWWWWWWRRWWWWWWwk.....",
    ".....kwWWWWWWRRWWWWWwwk.....",
    "......kwwWWWWRRWWWWwwk......",
    ".kkkkkkkkkkkkkkkkkkkk.......",
    ".kCkCkCk.....kMk.....kkkkkk.",
    ".kcccccck....kmk....kCkCkCk.",
    "kkcccccckkkkkkkkkkkkkcccccck",
    "krkddddddddddddddddddddddddk",
    "krkHHHHHHHHHHHHHHHHHHHHHHHk.",
    "krkhhhhhhhhhhhhhhhhhhhhhhk..",
    ".kkHHHHHHHHHHHHHHHHHHHHHk...",
    "...khhhhhhhhhhhhhhhhhhhk....",
    "....kkkkkkkkkkkkkkkkkkk.....",
]
COG_SMALL = [
    ".......k.......",
    "......kVVvk....",
    "...kkkkMkkkk...",
    "...kWWWRWWWk...",
    "..kRRRRRRRRRk..",
    "..kWWWWRWWWwk..",
    "...kkkkkkkkk...",
    "kkkk...k...kkkk",
    "kcck...m...kcck",
    "kkddddddddddddk",
    ".kHHHHHHHHHHHk.",
    "..khhhhhhhhhk..",
    "...kkkkkkkkk...",
]


def cog_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"k": K, "V": VERM[4 + k], "v": VERM[2 + k], "H": LAND[3 + k], "h": LAND[2 + k], "M": LAND[3 + k],
            "m": LAND[1 + k], "W": PARCH[6] if not night else NIGHT[6], "w": PARCH[4] if not night else NIGHT[4],
            "R": VERM[3 + k], "C": LAND[5 + k], "c": LAND[4 + k], "d": LAND[1 + k], "r": LAND[2 + k]}


# How long each cog's bob on the swell takes, in seconds, by its phase: an idle of the hand's four to eight, and
# no two the same, so two ships on one chart never rise together.
BOB = (4.2, 4.0, 4.4, 4.8)


def cog(p: Pix, x, wl, night, motion=False, small=False, phase=0):
    """A cog under sail, its waterline at row wl, from column x: the big one 28 wide, the small one 15; she bobs
    on the swell in a moving header (see `BOB`), the sea's near edge drawn in front of her keel. Returns her
    span."""
    art = COG_SMALL if small else COG
    h = len(art)
    L = p.layer(f"cog{phase}", ("bob", [0, 0, 1, 1, 1, 0, 0, -1, -1, -1], BOB[phase % len(BOB)]) if motion else None,
                z=1)
    p.sprite(x, wl - h + 2, art, cog_pal(night), 1, L)
    _mark(p, {(x + i, wl - h + 2 + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."})
    near = p.layer("near")
    foam, swell = (PARCH[6], SEA[4]) if not night else (DEEP[6], DEEP[4])
    w = len(art[0])
    for xx in range(x - 1, x + w + 2):
        p.px(xx, wl + 1, swell if (xx * 3) % 7 else SEA[3] if not night else DEEP[5], near)
    for (dx, dy) in ((w - 1, 0), (w, 0), (w + 1, 1), (w - 2, 1), (-1, 1), (-2, 0)):
        p.px(x + dx, wl + dy, foam, near)
    _mark(p, {(xx, wl + 1) for xx in range(x - 2, x + w + 2)} | {(x + w, wl), (x + w + 1, wl), (x - 2, wl)})
    return (x - 2, x + w + 2)


def route(p: Pix, pts, night, margin=2, every=3, L="base"):
    """A ship's route drawn as a chart draws it: a dotted line through `pts`, a dot every `every` pixels,
    left out wherever a word or a drawing lies near and in the top centre a header keeps for the month's mark."""
    col = INK[3] if not night else GOLD[2]
    base = p.layers["base"]
    n = 0
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        steps = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(steps):
            x, y = round(xa + (xb - xa) * i / steps), round(ya + (yb - ya) * i / steps)
            n += 1
            if n % every:
                continue
            if (x, y) in base or not p.clear_of_words(x - margin, y - margin, x + margin + 1, y + margin + 1):
                continue
            if not _off_top_centre(p, x, y, x + 1, y + 1):
                continue
            p.px(x, y, col, L)


# --------------------------------------------------------------------------- the walled city, hills and trees
def _stone(night: bool) -> tuple:
    """The city's stone: its lit face, its face and its shaded side; pale by day, in shadow by night."""
    return (PARCH[6], PARCH[5], PARCH[3]) if not night else (NIGHT[6], NIGHT[5], NIGHT[3])


def block(p: Pix, x, top, w, base, night, L="base"):
    """A block of stone from column x over w columns, rows top to base - 1: inked round, lit down its left and
    shaded down its right."""
    lit, face, shade = _stone(night)
    for yy in range(top, base):
        for xx in range(x, x + w):
            if xx in (x, x + w - 1) or yy == top:
                c = K
            elif xx == x + 1:
                c = lit
            elif xx >= x + w - 2 - (1 if w > 6 else 0):
                c = shade
            else:
                c = face
            p.px(xx, yy, c, L)


def cone(p: Pix, cx, top, half, h, ramp, light=4, dark=2, L="base"):
    """A pointed roof, its apex at (cx, top) and `half` wide each side at its eaves `h` rows down: lit on its left
    half, shaded on its right, inked round."""
    for j in range(h + 1):
        r = round(half * j / h)
        for xx in range(cx - r, cx + r + 1):
            edge = xx in (cx - r, cx + r) or j == h
            p.px(xx, top + j, K if edge else (ramp[light] if xx <= cx else ramp[dark]), L)


def merlons(p: Pix, x, top, w, night, L="base"):
    """Crenellations along a block's top: merlons of stone three wide with a gap of one between, inked round."""
    lit, face, _ = _stone(night)
    for xx in range(x, x + w):
        i = (xx - x) % 4
        if i == 3:
            continue
        p.px(xx, top - 2, K, L)
        p.px(xx, top - 1, K if i != 1 else lit, L)


def slits(p: Pix, x, top, w, base, L="base"):
    """Arrow slits down the middle of a tower, two rows tall every four."""
    cx = x + w // 2
    for yy in range(top + 2, base - 2, 4):
        p.px(cx, yy, K, L)
        p.px(cx, yy + 1, K, L)


def tower(p: Pix, x, base, w, h, night, roof="cone", ramp=None, flag=False, L="base"):
    """A tower w wide and h tall standing on row `base` from column x, its roof a cone (in `ramp`), a spire of
    verdigris copper with a gilt cross, or crenellations; a pennant on a pole at its top when `flag`."""
    ramp = ramp or VERM
    top = base - h
    block(p, x, top, w, base, night, L)
    slits(p, x, top, w, base, L)
    k = -1 if night else 0
    if roof == "cone":
        cone(p, x + w // 2, top - (w + 1), w // 2 + 1, w + 1, ramp, 4 + k, 2 + k, L)
        peak = top - (w + 1)
    elif roof == "spire":
        cone(p, x + w // 2, top - 2 * w - 2, w // 2 + 1, 2 * w + 2, SEA, 4 + k, 2 + k, L)
        peak = top - 2 * w - 2
        cx = x + w // 2
        for (dx, dy, c) in ((0, -1, GOLD[4]), (0, -2, GOLD[5]), (-1, -2, GOLD[3]), (1, -2, GOLD[3]), (0, -3, GOLD[5])):
            p.px(cx + dx, peak + dy, c, L)
        peak -= 3
    else:
        merlons(p, x, top, w, night, L)
        peak = top - 2
    if flag:
        fx = x + w // 2
        for yy in range(peak - 5, peak):
            p.px(fx, yy, K, L)
        for (dx, dy, c) in ((1, 0, VERM[4 + k]), (2, 0, VERM[4 + k]), (3, 0, VERM[3 + k]), (4, 0, VERM[2 + k]),
                            (1, 1, VERM[3 + k]), (2, 1, VERM[2 + k])):
            p.px(fx + dx, peak - 5 + dy, c, L)


def wall(p: Pix, x, base, w, h, night, L="base"):
    """A curtain wall w long and h high on row `base`: crenellated, its courses of stone marked."""
    top = base - h
    block(p, x, top, w, base, night, L)
    merlons(p, x, top, w, night, L)
    _, _, shade = _stone(night)
    for yy in range(top + 2, base - 1, 2):
        for xx in range(x + 2 + (yy // 2) % 2 * 2, x + w - 2, 4):
            p.px(xx, yy, shade, L)


def gate(p: Pix, cx, base, night, h=5, L="base"):
    """A gate in a wall, its arch dark with the portcullis's bars."""
    for yy in range(base - h, base):
        for xx in range(cx - 2, cx + 3):
            r = abs(xx - cx)
            if yy == base - h and r == 2:
                continue
            p.px(xx, yy, INK[2] if (r < 2 or yy > base - h) and r < 2 else K, L)
    for xx in (cx - 1, cx + 1):
        for yy in range(base - h + 1, base):
            p.px(xx, yy, INK[4] if not night else GOLD[1], L)


def house(p: Pix, x, base, w, h, night, L="base"):
    """A house with a gabled roof of red tiles behind a wall."""
    top = base - h
    block(p, x, top, w, base, night, L)
    k = -1 if night else 0
    rh = (w + 2) // 2
    for j in range(rh):
        a, b = x - 1 + j, x + w - j
        for xx in range(a, b + 1):
            edge = xx in (a, b) or j == rh - 1
            p.px(xx, top - 1 - j, K if edge else (VERM[4 + k] if xx < x + w // 2 else VERM[2 + k]), L)
    p.px(x + w // 2, base - 2, K, L)


def city(p: Pix, x, base, night, small=False, L="base"):
    """The walled city on its coast, its gate on row `base`: a crenellated wall between two round towers with
    red cones, and over it the church's spire of verdigris copper with its gilt cross, the keep with its
    pennant and the red roofs of the houses; 37 wide, or 24 when `small`. Returns its span."""
    if small:
        house(p, x + 5, base - 5, 5, 3, night, L)
        tower(p, x + 9, base - 4, 5, 9, night, roof="spire", L=L)
        tower(p, x + 15, base - 4, 4, 9, night, roof="crenel", flag=True, L=L)
        wall(p, x + 3, base, 18, 5, night, L)
        gate(p, x + 12, base, night, h=3, L=L)
        tower(p, x, base, 4, 8, night, L=L)
        tower(p, x + 20, base, 4, 8, night, L=L)
        _mark(p, {(xx, yy) for xx in range(x - 1, x + 25) for yy in range(base - 24, base)
                  if p.get(xx, yy, L) is not None})
        return (x - 1, x + 25)
    house(p, x + 6, base - 7, 6, 4, night, L)
    house(p, x + 22, base - 7, 5, 4, night, L)
    tower(p, x + 13, base - 6, 7, 12, night, roof="spire", L=L)
    tower(p, x + 26, base - 6, 5, 14, night, roof="crenel", flag=True, L=L)
    wall(p, x + 4, base, 29, 7, night, L)
    gate(p, x + 18, base, night, L=L)
    tower(p, x, base, 6, 11, night, L=L)
    tower(p, x + 31, base, 6, 11, night, L=L)
    _mark(p, {(xx, yy) for xx in range(x - 1, x + 38) for yy in range(base - 40, base)
              if p.get(xx, yy, L) is not None})
    return (x - 1, x + 38)


# Map symbols: a hill drawn as a mound inked round and hatched down its shaded side, a round tree and a fir.
HILL = [
    ".....kkk.....",
    "...kkLLLkk...",
    "..kLLLLLhLk..",
    ".kLLLLLLLhLk.",
    "kLLLLLLLhLhLk",
]
HILL_SMALL = ["...kkk...", ".kkLLhkk.", "kLLLLhLhk"]
TREE = [".kkk.", "kGGgk", "kGGgk", ".kgk.", "..t..", "..t.."]
FIR = ["..k..", ".kGk.", ".kGgk", "kGGgk", "kGggk", "..t.."]


def symbol_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"k": K, "L": LAND[4 + k] if not night else DUSK[5], "h": LAND[2 + k] if not night else DUSK[3],
            "G": GREEN[4 + k], "g": GREEN[2 + k], "t": INK[3]}


def map_symbol(p: Pix, art, x, base, night, L="base"):
    """A map symbol (a hill, a tree, a fir) standing on row `base` from column x, drawn once a file and placed."""
    key = ("mapsym", tuple(art), night)
    if key not in p.syms:
        pal = symbol_pal(night)
        p.symbol(key, {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."})
    p.use(key, x, base - len(art), L)
    _mark(p, {(x + i, base - len(art) + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."})


def river(p: Pix, pts, night, L="base"):
    """A river winding from its source to the sea through `pts`: a ribbon of verdigris two wide, inked along its
    banks."""
    water, bank = (SEA[3], SEA[1]) if not night else (DEEP[5], DEEP[2])
    cells = set()
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        steps = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(steps + 1):
            x, y = round(xa + (xb - xa) * i / steps), round(ya + (yb - ya) * i / steps)
            cells.update({(x, y), (x + 1, y)})
    for q in cells:
        p.px(q[0], q[1], water, L)
    for q, c in outline({q: 1 for q in cells}, bank).items():
        if p.get(q[0], q[1], L) is None:
            p.px(q[0], q[1], c, L)
    _mark(p, cells | set(outline({q: 1 for q in cells}, bank)))


# --------------------------------------------------------------------------- islands
# The washes an island takes, as a chart colours its islands: ochre like the mainland, vermilion and gilt; each
# (fill, its shaded shore, its lit shore) by day and by night.
ISLE_WASH = {
    "land": ((C["land"], LAND[4], LAND[6]), (DUSK[4], DUSK[2], DUSK[6])),
    "verm": ((VERM[4], VERM[2], VERM[5]), (VERM[2], VERM[1], VERM[3])),
    "gold": ((GOLD[4], GOLD[2], GOLD[5]), (GOLD[2], GOLD[1], GOLD[3])),
}


def isle_cells(rx: int, ry: int, seed: int) -> set:
    """The cells of an island about (0, 0), rx across and ry down from its middle: an oval with its coast worn
    into bays and points by three waves of different lengths round it, and sometimes an islet off its shore."""
    rnd = random.Random(seed)
    waves = [(rnd.uniform(0.2, 0.3), rnd.choice((2, 3)), rnd.uniform(0, 6.3)),
             (rnd.uniform(0.1, 0.16), rnd.choice((4, 5)), rnd.uniform(0, 6.3)),
             (rnd.uniform(0.06, 0.1), rnd.choice((7, 8, 9)), rnd.uniform(0, 6.3))]
    cells = set()
    for y in range(-ry - 3, ry + 4):
        for x in range(-rx - 4, rx + 5):
            t = math.atan2(y / ry, x / rx)
            if math.hypot(x / rx, y / ry) < 0.92 * (1 + sum(a * math.sin(k * t + ph) for a, k, ph in waves)):
                cells.add((x, y))
    if rx >= 8:
        for side in rnd.sample((-1, 1), rnd.choice((1, 1, 2))):
            ox, oy = side * (rx + 4), rnd.choice((-1, 1)) * (ry // 2)
            cells |= {(ox + x, oy + y) for y in (-1, 0, 1) for x in range(-2, 3) if abs(x) + abs(y) < 3}
    return cells


# The map's own marks for what stands on an island, drawn as a cartographer marks land: a hill (L lit, h shaded),
# a tree (G lit, g shaded, t trunk) and a sapling for an island too small for the tree, a tower with its red cone
# and the pole of its pennant, and a town of red roofs (R lit, r shaded) round a church tower (W stone); all
# inked (k).
ISLE_HILL = ["...kkk...", ".kkLLhkk.", "kLLLLhLhk"]
ISLE_TREE = [".kkk.", "kGGgk", "kGGgk", ".kgk.", "..t.."]
ISLE_SAPLING = [".k.", "kGk", "kgk", ".t."]
ISLE_TOWER = ["..k..", "..r..", ".rRr.", "rRRRr", ".kWk.", ".kWk.", ".kkk."]
ISLE_TOWN = [".....k.....", "....rRr....", "...rRRRr...", ".rr.kWk.rr.", "rRRrkWkrRRr", "kWWkkWkkWWk",
             "kkkkkkkkkkk"]


def isle_pal(night: bool) -> dict:
    """The tones of the marks on an island."""
    k = -1 if night else 0
    return {"k": K if not night else GOLD[3], "L": LAND[4] if not night else DUSK[5], "h": LAND[2] if not night
            else DUSK[3], "G": GREEN[4 + k], "g": GREEN[2 + k], "t": INK[3] if not night else GOLD[2],
            "r": VERM[3 + k], "R": VERM[5 + k], "W": PARCH[6] if not night else NIGHT[6]}


def isle(p: Pix, cx, cy, rx, ry, night, seed, wash="land", L="base"):
    """An island in the open sea about (cx, cy), drawn as a cartographer draws land: washed in one of the
    chart's colours, lit along its upper and left shores and shaded along its lower and right, its coastline
    inked dark and hatched with short strokes out into the sea all round; and on it the map's marks as it has
    room, a town of red roofs round a church on the biggest, a tower on the next, hills and trees on the rest.
    Returns the cells it covers."""
    fill, rim, lit = ISLE_WASH[wash][1 if night else 0]
    coast = K if not night else GOLD[3]
    hatch = INK[4] if not night else GOLD[1]
    land = {(cx + x, cy + y) for (x, y) in isle_cells(rx, ry, seed)}
    edge = outline({q: 1 for q in land}, coast)
    got = land | set(edge)
    # the shore hatched: a short stroke out from every other cell of the coast
    ring = sorted(edge, key=lambda q: math.atan2(q[1] + 0.5 - cy, (q[0] + 0.5 - cx) * ry / rx))
    for i, (x, y) in enumerate(ring):
        if i % 2:
            continue
        dx, dy = x + 0.5 - cx, (y + 0.5 - cy) * rx / ry
        n = math.hypot(dx, dy) or 1
        for t in (1, 2):
            q = (round(x + dx / n * t), round(y + dy / n * t * ry / rx))
            if q not in got:
                p.px(q[0], q[1], hatch, L)
                got.add(q)
    for (x, y) in land:
        if (x + 1, y) not in land or (x, y + 1) not in land:
            p.px(x, y, rim, L)
        elif (x - 1, y) not in land or (x, y - 1) not in land:
            p.px(x, y, lit, L)
        else:
            p.px(x, y, fill, L)
    for q, c in edge.items():
        p.px(q[0], q[1], c, L)
    # the marks on the land, each kept a cell inside the coast and clear of the others, as near the middle as
    # they go; an island too small for any of its plan's marks takes a sapling or two
    pal, held = isle_pal(night), set()
    spots = sorted(((ox, oy) for oy in range(-ry, ry + 1) for ox in range(-rx, rx + 1)),
                   key=lambda o: (abs(o[0]) + 2 * abs(o[1]), o))

    def mark(art) -> bool:
        w, h = len(art[0]), len(art)
        for (ox, oy) in spots:
            x0, y0 = cx + ox - w // 2, cy + oy - h // 2
            cells = {(x0 + i, y0 + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."}
            near = {(a + u, b + v) for (a, b) in cells for u in (-1, 0, 1) for v in (-1, 0, 1)}
            if near <= land and not near & held:
                p.sprite(x0, y0, art, pal, 1, L)
                held.update(near)
                return True
        return False
    plan = ([ISLE_TOWN, ISLE_TREE, ISLE_HILL] if rx >= 15 else [ISLE_TOWER, ISLE_HILL, ISLE_TREE] if rx >= 12
            else [ISLE_HILL, ISLE_TREE] if rx >= 9 else [ISLE_TREE])
    if not [art for art in plan if mark(art)]:
        mark(ISLE_SAPLING)
        mark(ISLE_SAPLING)
    _mark(p, got)
    return got


def _sea_free(p: Pix, x0, y0, x1, y1, margin=4) -> bool:
    """Whether the box (x0, y0, x1, y1) lies in open sea: `margin` clear of every word, every drawing and every
    land's coast, and of the top centre a header keeps for the month's mark (see `top_centre`)."""
    if not p.clear_of_words(x0 - margin - 1, y0 - margin - 1, x1 + margin + 1, y1 + margin + 1):
        return False
    if not _off_top_centre(p, x0 - margin, y0 - margin, x1 + margin + 1, y1 + margin + 1):
        return False
    filled = getattr(p, "filled", set())
    layers = [d for d in p.layers.values() if d]
    for y in range(y0 - margin, y1 + margin + 1):
        for x in range(x0 - margin, x1 + margin + 1):
            if (x, y) in filled or any((x, y) in d for d in layers):
                return False
    for side, _, reach in getattr(p, "lands", ()):
        for y in range(max(0, y0 - margin), min(len(reach), y1 + margin + 1)):
            r = reach[y]
            if r is not None and (x0 - margin <= r + 4 if side < 0 else x1 + margin >= r - 4):
                return False
    return True


def islands(p: Pix, g, night, most=2, apart=70, x0=12, x1=None, seed=0, sizes=((16, 8), (13, 6), (10, 5), (8, 4))):
    """Islands scattered in the open sea of a header's chart above row g, where the words and the drawings leave
    it: up to `most`, each `apart` from the others, between columns x0 and x1, the first one ochre and the
    others vermilion and gilt by turns; the biggest of `sizes` placed first, wherever they fit."""
    x1 = p.w - 12 if x1 is None else x1
    rnd = random.Random(p.w * 7 + g * 13 + seed)
    spots = [(x, y) for y in range(TOP_BAND + 16, g - 6, 3) for x in range(x0 + 10, x1 - 10, 5)]
    rnd.shuffle(spots)
    placed = []
    for (rx, ry) in sizes:
        for (x, y) in spots:
            if len(placed) >= most:
                return placed
            if any(math.hypot(x - a, (y - b) * 2) < apart for a, b in placed):
                continue
            if y + ry + 6 < g and _sea_free(p, x - rx - 9, y - ry - 6, x + rx + 9, y + ry + 6):
                isle(p, x, y, rx, ry, night, seed=x * 31 + y, wash=("land", "verm", "gold")[len(placed) % 3])
                placed.append((x, y))
    return placed


# --------------------------------------------------------------------------- the sea serpent
# The serpent's head, 14 by 12, facing left: its crest of gilt spines (Y), its head of vermilion (V lit, v
# shaded) with a gilt eye (e), its jaws open on white fangs (t) round its red gullet and a forked tongue (r),
# the neck leaving it at the foot on the right; inked round (k).
SERPENT_HEAD = [
    "......k.k.k...",
    ".....kYkYkYk..",
    "...kkVVVVVVk..",
    "..kVVVVVkeVVk.",
    ".kVVVVVVVkVVVk",
    "kVVkkkkVVVVVVk",
    "kt.t.tkkVVVVvk",
    ".rr..r.kVVVvk.",
    "rr.t.t.kVVVvk.",
    ".kkkkkkVVVvvk.",
    "......kVVvvk..",
    "......kkvvvk..",
]


def _serpent_colour(night: bool):
    """A colour for each pixel of the serpent's body: its back of vermilion marked with darker scales, its belly
    pale and ringed, lit where the light falls on it."""
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        if o > 0.38:
            return (GOLD[5 + k] if int(s) % 2 else GOLD[4 + k]) if lam > 0.45 else GOLD[3 + k]
        if (int(s * 1.0) % 3 == 0) and o < 0.1:
            return VERM[2 + k]
        return VERM[5 + k] if lam > 0.82 else VERM[4 + k] if lam > 0.45 else VERM[3 + k]
    return colour


def serpent(p: Pix, x, wl, night, motion=False, phase=0, coils=2):
    """The sea serpent looping out of the waves, its head reared at the left from column x, its waterline at row
    wl: the neck rising to the head with its open jaws and forked tongue, and behind it its coils arching out of
    the water and back, the last ending in its forked tail; a spine of gilt down each coil and the sea broken
    white where it goes in and out. In a moving header its coils rise and sink in turn, each on an idle of four to
    five seconds of its own. Returns its span."""
    from ...holidays.pixel import tube
    colour = _serpent_colour(night)
    k = -1 if night else 0
    head = p.layer(f"sph{phase}", ("bob", [0, 0, 0, 1, 1, 1, 0, 0], 4.4) if motion else None, z=1)
    neck = [(x + 11, wl - 7), (x + 12, wl - 4), (x + 13, wl - 1), (x + 13, wl + 2)]
    cells = tube(p, neck, 2.3, colour, L=head, outline=K)
    p.sprite(x, wl - 18, SERPENT_HEAD, {"k": K, "V": VERM[4 + k], "v": VERM[2 + k], "Y": GOLD[4 + k],
                                        "e": GOLD[6], "t": PARCH[6], "r": VERM[5 + k]}, 1, head)
    marked = set(cells) | {(x + i, wl - 18 + j) for j, row in enumerate(SERPENT_HEAD) for i, ch in enumerate(row)
                           if ch != "."}
    arches = ((x + 18, x + 31, 10), (x + 34, x + 43, 6)) if coils > 1 else ((x + 17, x + 27, 8),)
    ends = [x + 13]
    for i, (xa, xb, h) in enumerate(arches):
        L = p.layer(f"spa{phase}{i}", ("bob", [1, 1, 0, 0, 0, 1, 1, 1] if i % 2 else [0, 0, 1, 1, 1, 1, 0, 0],
                                       4.0 + 0.8 * i) if motion else None, z=1)
        xm, half = (xa + xb) / 2, (xb - xa) / 2
        arch = [(xm - half * math.cos(t / 24 * math.pi), wl + 2 - (h + 2) * math.sin(t / 24 * math.pi))
                for t in range(25)]
        got = tube(p, arch, 2.3, colour, L=L, outline=K)
        marked |= set(got)
        for t in range(3, 22, 3):
            ang = t / 24 * math.pi
            sx = round(xm - (half + 2.4) * math.cos(ang))
            sy = round(wl + 2 - (h + 2 + 2.4) * math.sin(ang))
            p.px(sx, sy, GOLD[4 + k], L)
            p.px(sx, sy - 1, K, L)
            marked |= {(sx, sy), (sx, sy - 1)}
        ends += [xa, xb]
    tail = x + 46 if coils > 1 else x + 30
    Lt = p.layer(f"spa{phase}t", None, z=1)
    for (dx, dy, c) in ((0, 0, VERM[3 + k]), (1, -1, VERM[4 + k]), (2, -2, VERM[4 + k]), (3, -3, K),
                        (1, 0, VERM[2 + k]), (2, -1, VERM[3 + k]), (3, -1, VERM[4 + k]), (4, -1, K),
                        (3, -2, VERM[3 + k]), (-1, 0, K), (0, -1, K), (1, -2, K), (2, -3, K), (4, -2, K)):
        p.px(tail + dx, wl + dy, c, Lt)
        marked.add((tail + dx, wl + dy))
    ends.append(tail + 1)
    # nothing of the serpent shows below the sea it goes into
    for name in {head, Lt} | {f"spa{phase}{i}" for i in range(len(arches))}:
        for q in [q for q in p.layers.get(name, {}) if q[1] > wl + 3]:
            del p.layers[name][q]
            marked.discard(q)
    # the sea in front of the coils, broken white where the serpent goes in and out
    near = p.layer("near")
    foam = PARCH[6] if not night else DEEP[6]
    wave = X["wave"] if not night else DEEP[5]
    sea = C["sea"] if not night else C["sea_night"]
    for ex in ends:
        for xx in range(ex - 3, ex + 4):
            for yy in (wl + 1, wl + 2, wl + 3):
                p.px(xx, yy, sea, near)
                marked.add((xx, yy))
        for (dx, dy, c) in ((-3, 0, foam), (-2, -1, foam), (-1, 0, foam), (1, 0, foam), (2, -1, foam), (3, 0, foam),
                            (-2, 1, wave), (-1, 1, wave), (1, 1, wave), (2, 1, wave)):
            p.px(ex + dx, wl + dy, c, near)
            marked.add((ex + dx, wl + dy))
    _mark(p, marked)
    return (x - 1, tail + 6)


# The great serpent's head, 26 by 21, facing left: its two horns swept back (Y y g), its head of vermilion lit
# along its brow and snout (H V) and shaded toward its jaw and nape (v d), scales on its cheek (d), its eye of gilt
# (Y e y) slit with ink (p) under a frowning brow, its nostril, its jaws open on its fangs (t) round its dark
# gullet (D) and forked tongue (r), its lower jaw and throat gilt beneath (y g); inked round (k). Its neck leaves
# it at GREAT_THROAT.
GREAT_HEAD = [
    "....................k.....",
    "...................kyk....",
    "..................kYgk..k.",
    ".................kYgk..kyk",
    "................kYyk..kYgk",
    ".........kkkkkkkYygkkkYgk.",
    ".......kkHHHHHkkkVgVVVYgk.",
    ".....kkHHVVVkkkVVVVVdVVVgk",
    "...kkHVVVVVkYepkVVVVVVdVvk",
    "..kHVkVVVVVVkypkVVdVVVVvdk",
    ".kHVVVVVVVVVVddVVVVVVdvvdk",
    ".kvvvvvvvvvvvvvVVVVdVVvddk",
    ".kkkkkkkkkkkkkkvVVVVvvvddk",
    "..tDDtDDtDDtDDDkvVVvvvvdk.",
    "rr.tDDtDDtDDDDkvvvvvvvdk..",
    "..rrrrrrrDDDDkyvvvvvvvdk..",
    "rr.DtDDtDDDkkgyyvvvvvvdk..",
    "...kkkkkkkkVgyyyvvvvvvdk..",
    "...kVVVVVVVVgyyyvvvvvddk..",
    "....kyyyyyyykgyyyvvvvddk..",
    ".....kkkkkkkkkgyyvvvvdk...",
]
GREAT_THROAT = (18.5, 15.0)
SERPENT_TOP = 14       # the highest row a strip's great serpent rears its horns to, under the wind head's stream


def great_head_pal(night: bool) -> dict:
    """The great serpent's head's tones, a tone darker by night but for its eye."""
    k = -1 if night else 0
    return {"k": K, "H": VERM[5 + k], "V": VERM[4 + k], "v": VERM[3 + k], "d": VERM[2 + k], "D": VERM[1],
            "Y": GOLD[5 + k], "y": GOLD[4 + k], "g": GOLD[3 + k], "e": GOLD[6], "p": INK[0], "t": PARCH[6],
            "r": VERM[5 + k]}


def serpent_coils(x, coils: int, rise: int = 18) -> tuple:
    """The great serpent's coils behind its neck, its tongue at column x: each arch (from, to, how high it rises,
    how thick it is), the first rising `rise` rows, and the column its tail flicks out of the water at; two
    coils, or one and shorter."""
    if coils > 1:
        arches = ((x + 27, x + 43, rise, 3.4), (x + 46, x + 52, rise // 2, 2.6))
    else:
        arches = ((x + 26, x + 37, rise * 3 // 4, 3.2),)
    return arches, arches[-1][1] + 3


def serpent_boxes(x, wl, top, coils: int) -> list:
    """The boxes (x0, y0, x1, y1), ends excluded, the great serpent covers (see `great_serpent`): its head with its
    horns and its tongue, and its neck, its coils and its tail down to the foam at its foot."""
    _, tail = serpent_coils(x, coils)
    head = (x - 1, top - 1, x + len(GREAT_HEAD[0]) + 1, top + len(GREAT_HEAD) + 1)
    return [head, (x + 5, top + 18, tail + 6, wl + 4)]


def great_serpent(p: Pix, x, wl, top, night, motion=False, phase=0, coils=2, bow=6.0):
    """The great sea serpent rearing up out of the waves, a strip's hero: its head reared high at the left, its
    top on row `top` and its tongue at column x, facing the words; its neck rising to it from the waterline at
    row wl, bowed back `bow` columns, and in an S where it is long; and behind it to the right its coils arching
    out of the water and back, `coils` of them, the last ending in its forked tail. A crest of gilt spines runs
    down the back of its neck and along each coil, its belly is gilt, and the sea breaks white where it goes in
    and out. In a moving header its head and neck sway and its coils rise and sink in turn, each on an idle of
    its own. Returns its span."""
    from ...holidays.pixel import tube
    colour = _serpent_colour(night)
    k = -1 if night else 0
    head = p.layer(f"gsh{phase}", ("bob", [0, 0, 0, 1, 1, 1, 0, 0], 4.4) if motion else None, z=1)
    hx, hy = x + GREAT_THROAT[0], top + GREAT_THROAT[1]
    foot = wl + 3
    bends = 1 if foot - hy < 56 else 2
    n = 8 * bends + 6
    neck = [(hx + bow * math.sin(bends * math.pi * i / n) - 1.5 * i / n, hy + (foot - hy) * i / n)
            for i in range(n + 1)]
    marked = set(tube(p, neck, 4.4, colour, L=head, outline=K))
    # the crest down the back of the neck: a gilt spine every four units along it, its tip inked
    run = 0.0
    for (ax, ay), (bx, by) in zip(neck[2:-2], neck[3:-1]):
        d = math.hypot(bx - ax, by - ay) or 1
        nx, ny = (by - ay) / d, -(bx - ax) / d          # the back, to the right of the neck going down
        if nx < 0:
            nx, ny = -nx, -ny
        steps = max(1, round(d))
        for j in range(steps):
            run += d / steps
            if run < 4:
                continue
            run = 0.0
            cx_, cy_ = ax + (bx - ax) * j / steps, ay + (by - ay) * j / steps
            sx, sy = round(cx_ + nx * 5.4), round(cy_ + ny * 5.4)
            p.px(sx, sy, GOLD[4 + k], head)
            p.px(sx + 1, sy, K, head)
            p.px(sx, sy - 1, K, head)
            marked |= {(sx, sy), (sx + 1, sy), (sx, sy - 1)}
    p.sprite(x, top, GREAT_HEAD, great_head_pal(night), 1, head)
    marked |= {(x + i, top + j) for j, row in enumerate(GREAT_HEAD) for i, ch in enumerate(row) if ch != "."}
    base = round(neck[-1][0])
    arches, tail = serpent_coils(x, coils, rise=min(18, max(12, round((wl - top) / 3))))
    ends = [(base, 6)]
    for i, (xa, xb, h, rad) in enumerate(arches):
        L = p.layer(f"gsa{phase}{i}", ("bob", [1, 1, 0, 0, 0, 1, 1, 1] if i % 2 else [0, 0, 1, 1, 1, 1, 0, 0],
                                       4.0 + 0.8 * i) if motion else None, z=1)
        xm, half = (xa + xb) / 2, (xb - xa) / 2
        arch = [(xm - half * math.cos(t / 24 * math.pi), wl + 2 - (h + 2) * math.sin(t / 24 * math.pi))
                for t in range(25)]
        marked |= set(tube(p, arch, rad, colour, L=L, outline=K))
        for t in range(3, 22, 3):
            ang = t / 24 * math.pi
            sx = round(xm - (half + rad + 0.6) * math.cos(ang))
            sy = round(wl + 2 - (h + 2 + rad + 0.6) * math.sin(ang))
            p.px(sx, sy, GOLD[4 + k], L)
            p.px(sx, sy - 1, K, L)
            marked |= {(sx, sy), (sx, sy - 1)}
        ends += [(xa, math.ceil(rad) + 2), (xb, math.ceil(rad) + 2)]
    Lt = p.layer(f"gsa{phase}t", None, z=1)
    for (dx, dy, c) in ((0, 0, VERM[3 + k]), (1, -1, VERM[4 + k]), (2, -2, VERM[4 + k]), (3, -3, K),
                        (1, 0, VERM[2 + k]), (2, -1, VERM[3 + k]), (3, -1, VERM[4 + k]), (4, -1, K),
                        (3, -2, VERM[3 + k]), (-1, 0, K), (0, -1, K), (1, -2, K), (2, -3, K), (4, -2, K)):
        p.px(tail + dx, wl + dy, c, Lt)
        marked.add((tail + dx, wl + dy))
    ends.append((tail + 1, 3))
    for name in {head, Lt} | {f"gsa{phase}{i}" for i in range(len(arches))}:
        for q in [q for q in p.layers.get(name, {}) if q[1] > wl + 3]:
            del p.layers[name][q]
            marked.discard(q)
    near = p.layer("near")
    foam = PARCH[6] if not night else DEEP[6]
    wave = X["wave"] if not night else DEEP[5]
    sea = C["sea"] if not night else C["sea_night"]
    for ex, r in ends:
        for xx in range(ex - r, ex + r + 1):
            for yy in (wl + 1, wl + 2, wl + 3):
                p.px(xx, yy, sea, near)
                marked.add((xx, yy))
        for (dx, dy, c) in ((-r, 0, foam), (-r + 1, -1, foam), (-r + 2, 0, foam), (r - 2, 0, foam), (r - 1, -1, foam),
                            (r, 0, foam), (-r + 1, 1, wave), (-r + 2, 1, wave), (r - 2, 1, wave), (r - 1, 1, wave)):
            p.px(ex + dx, wl + dy, c, near)
            marked.add((ex + dx, wl + dy))
    _mark(p, marked)
    return (x - 1, tail + 6)


# --------------------------------------------------------------------------- the whale
# A whale spouting, 30 by 15, facing right: the jets of its spout (W), its blowhole, its great head and back
# of slate (B lit, b hatched in shadow), an eye (e), its mouth set with teeth (t) and its flukes raised behind;
# inked round (k). Its waterline is row 12.
WHALE = [
    "..................WW.....WW...",
    ".................W..W...W..W..",
    "....................WW.WW.....",
    "......................W.......",
    "...........kkkkkkkkkkkkkkk....",
    "kk......kkkBBBBBBBBBBBBBBBkk..",
    "kBk...kkBBBBBBBBBBBBBBBBBBBBk.",
    ".kBk.kBBBBBBBBBBBBBBBBBBBkeBBk",
    "..kBkBBBbBBBBBBBBBBBBBBBBBBBBk",
    "..kBBBbBbBBBBBBBBBBBBBBBBBkkkk",
    ".kBbbBbBbBBBBBBBBBBBBBBkkttttk",
    "kBbkkbbbbbbbbbbbbbbbbbbbbbbbk.",
    "kk...kkkkkkkkkkkkkkkkkkkkkkk..",
]


# How long a whale's breath takes in a moving header, in seconds, and how much of it its spout plays for: the
# spout rises, falls and is gone, and the whale rests before it blows again.
BREATH, SPOUT = 4.8, 0.375


def whale(p: Pix, x, wl, night, motion=False, phase=0):
    """A whale spouting, from column x, its waterline at row wl, the sea lapping its flank in front. In a moving
    header it breathes (see `BREATH`): its spout plays and falls, and it rests. Returns its span."""
    k = -1 if night else 0
    pal = {"k": K, "B": SLATE[4 + k], "b": SLATE[2 + k], "e": PARCH[6], "t": PARCH[6],
           "W": C["white"] if not night else DEEP[6]}
    top = wl - 11
    body = [row.replace("W", ".") for row in WHALE]
    p.sprite(x, top, body, pal)
    spout = [row if "W" in row else "." * len(row) for row in WHALE[:4]]
    if motion:
        for f, cut in enumerate((0, 1, 2)):
            Ls = p.seq(f"spout{phase}{f}", SPOUT * f / 3, SPOUT * (f + 1) / 3, BREATH, keep=f == 0, z=0.5)
            p.sprite(x, top + cut, spout[:4 - cut], pal, 1, Ls)
    else:
        p.sprite(x, top, spout, pal)
    marked = {(x + i, top + j) for j, row in enumerate(WHALE) for i, ch in enumerate(row) if ch != "."}
    near = p.layer("near")
    sea = C["sea"] if not night else C["sea_night"]
    foam = PARCH[6] if not night else DEEP[6]
    wave = X["wave"] if not night else DEEP[5]
    for xx in range(x - 2, x + 31):
        p.px(xx, wl + 1, sea, near)
        p.px(xx, wl + 2, wave if (xx + phase) % 5 == 0 else sea, near)
        marked |= {(xx, wl + 1), (xx, wl + 2)}
        if xx % 4 == 1:
            p.px(xx, wl, foam, near)
            marked.add((xx, wl))
    _mark(p, marked)
    return (x - 2, x + 31)


# --------------------------------------------------------------------------- the dragon in the unknown land
# A dragon standing in the unknown land, 32 by 24, facing left: its wings raised (R membrane, r ribs), its
# horned head with a gilt eye (e) and open jaws breathing a tongue of flame (f F), its neck and body of green
# (G lit, g shaded) with a gilt belly (Y), its legs and claws, and its tail curling behind; inked round (k).
DRAGON = [
    "........................k.......",
    ".................k.....kRk......",
    "................kRk...kRRk......",
    "...............kRrk..kRrRk......",
    "..............kRrRk.kRrRRk......",
    ".............kRrRRkkRrRRrk......",
    "..k.k.......kRrRRkkRrRRrk.......",
    ".kGkGk.....kRrRRkkRrRRrk........",
    "kGGeGGk...kRrRrkRrRrrrk.........",
    "kGGGGGGk.kRrrrkRrrrrkk..........",
    "FkkkkGGGkGGGkkkkkkkk............",
    "fFFk.kGGGGGGGGGk................",
    "FkkkkGGGGGGGGGGGk...............",
    "...kGGGkYYGGGGGGGk..............",
    "....kkkYYYYGGGGGGGk.........kk..",
    "......kYYYYYGGGGGGGk.......kGk..",
    ".......kYYYYYGGGGgGGkk....kGk...",
    "........kYYYYYGGGgggGGkkkkGk....",
    ".........kkYYkGGkgggGGGGGGk.....",
    "..........kYkkGGkkkggGGkk.......",
    ".........kYk.kGk..kkkkk.........",
    "........kYk..kGk................",
    ".......kkkk.kkkk................",
]


def dragon(p: Pix, x, base, night, L="base"):
    """The dragon in the unknown land, standing on row `base` from column x. Returns its span."""
    k = -1 if night else 0
    pal = {"k": K, "R": VERM[4 + k], "r": VERM[2 + k], "G": GREEN[4 + k], "g": GREEN[2 + k], "Y": GOLD[4 + k],
           "e": GOLD[6], "F": VERM[4 + k], "f": GOLD[5 + k]}
    top = base - len(DRAGON)
    p.sprite(x, top, DRAGON, pal, 1, L)
    _mark(p, {(x + i, top + j) for j, row in enumerate(DRAGON) for i, ch in enumerate(row) if ch != "."})
    return (x - 1, x + len(DRAGON[0]) + 1)


# --------------------------------------------------------------------------- the navigator's lantern and dividers
# The navigator's lantern, 15 by 26: its iron ring, its cone of brass pierced with vents (o) the light shows
# through, its collar and foot of brass (B lit, b shaded, d darkest), and its horn panes between their straps, the
# front one full in the light (G) and the sides less (h, g), with the candle (c lit, C shaded) burning within, its
# flame (F) round its bright heart (W); inked round (k).
LANTERN_BIG = [
    "......kkk......",
    ".....k...k.....",
    ".....k...k.....",
    "......kBk......",
    ".....kBBbk.....",
    "....kBBBBbk....",
    "...kBoBBoBbk...",
    "..kBBBBBBBBbk..",
    ".kBBoBBoBBoBbk.",
    "kkkkkkkkkkkkkkk",
    "kBBBBBBBBBBBBbk",
    ".kkkkkkkkkkkkk.",
    ".khhkGGGGGkggk.",
    ".khhkGGGGGkggk.",
    ".khhkGGFGGkggk.",
    ".khhkGFFFGkggk.",
    ".khhkGFWFGkggk.",
    ".khhkGFWFGkggk.",
    ".khhkGGFGGkggk.",
    ".khhkGGcGGkggk.",
    ".khhkGcccGkggk.",
    ".khhkGcCCGkggk.",
    ".kkkkkkkkkkkkk.",
    "kBBBBBBBBBBBBbk",
    "kbbbbbbbbbbbbdk",
    ".kk.........kk.",
]
# The same lantern, 13 by 19, where the rows are fewer.
LANTERN = [
    ".....kkk.....",
    "....k...k....",
    ".....kBk.....",
    "....kBBbk....",
    "...kBoBobk...",
    "..kBBBBBBbk..",
    ".kBoBBoBBobk.",
    "kkkkkkkkkkkkk",
    ".khkGGGGGkgk.",
    ".khkGGFGGkgk.",
    ".khkGFFFGkgk.",
    ".khkGFWFGkgk.",
    ".khkGGFGGkgk.",
    ".khkGGcGGkgk.",
    ".khkGccCGkgk.",
    ".kkkkkkkkkkk.",
    "kBBBBBBBBBBbk",
    "kbbbbbbbbbbdk",
    ".kk.......kk.",
]
FLAME_AT = {True: (7, 16), False: (6, 11)}   # the flame's heart, in the big lantern and the smaller
# The steps of a lantern's light pooled on the chart, from its edge in to the flame: how far out each runs, as a
# share of the light's reach, and how strong the light is within it. Where a step reaches a word it is held to
# POOL_WORDS, which keeps every text colour of the night at 4.5:1 on whatever the light falls on.
POOL = ((1.0, 0.08), (0.78, 0.14), (0.58, 0.2), (0.42, 0.26), (0.28, 0.33), (0.16, 0.4))
POOL_WORDS = 0.25


def lantern_pal(night: bool) -> dict:
    """The lantern's tones: its brass, and its horn and candle, which by night glow round the flame, the flame and
    the light through the horn all tones of the hand's flame."""
    lit = night
    return {"k": K, "B": GOLD[4], "b": GOLD[2], "d": GOLD[1], "o": FLAME[4] if lit else INK[2],
            "G": FLAME[4] if lit else PARCH[6], "h": FLAME[3] if lit else PARCH[5], "g": FLAME[2] if lit else PARCH[4],
            "F": FLAME[5] if lit else PARCH[5], "W": FLAME[6] if lit else PARCH[6], "c": PARCH[6], "C": PARCH[4]}


def pool(p: Pix, cx, cy, rx, ry, alphas=POOL):
    """The lantern's light pooled on the chart round (cx, cy) by night: rings of warm light, stronger toward the
    flame, laid over the chart and everything drawn and written on it, which catch the light as the parchment
    does, and kept to the chart above its rule; on a drawing made lighter to fit its budget, without its faintest
    ring."""
    rule = getattr(p, "chart", (None, p.h))[1]
    n = getattr(p, "pools", 0)
    p.pools = n + 1
    cid = f"pk{n}"
    p.defs.append(f'<clipPath id="{cid}"><rect width="{p.w}" height="{rule}"/></clipPath>')
    rings, prev = [], 0.0
    # a drawing made lighter to fit its budget leaves out the faintest, outermost ring
    for f, a in alphas[1:] if p.lite else alphas:
        for (x0, y0, x1, y1) in p.words:
            nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
            if math.hypot((nx - cx) / (rx * f), (ny - cy) / (ry * f)) < 1:
                a = min(a, POOL_WORDS)
                break
        if a <= prev:
            continue
        o = 1 - (1 - a) / (1 - prev)
        prev = a
        rings.append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx * f)}" ry="{num(ry * f)}" '
                     f'fill-opacity="{num(o)}"/>')
    g = f'<g clip-path="url(#{cid})" fill="{FLAME[3]}">{"".join(rings)}</g>'
    p.raw(21, g, g)


def lantern(p: Pix, x, base, night, phase=0, reach=40, motion=True, big=False):
    """The navigator's lantern standing on the chart, its foot on row `base`, from column x: brass and horn, and
    by night its candle burning and flickering, a glow round it, and its light pooled `reach` across the chart,
    which the finishing pass lays once every word is set (see `pool`), the lantern itself standing in front of
    its own light. Returns its span."""
    art = LANTERN_BIG if big else LANTERN
    top = base - len(art)
    L = p.layer("lamp", None, z=22) if night else "base"
    p.sprite(x, top, art, lantern_pal(night), 1, L)
    own = {(x + i, top + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."}
    _mark(p, own)
    for xx in range(x + 1, x + len(art[0]) + 1):
        p.apx(xx, base, X["shade_ink"], 0.4, L)
    if night:
        fx, fy = x + FLAME_AT[big][0], top + FLAME_AT[big][1]
        Lf = p.layer(f"lampf{phase}", ("flicker", phase) if motion else None, z=23)
        for (dx, dy) in ((0, -2), (0, -1), (-1, 0), (1, 0), (0, 1)):
            p.px(fx + dx, fy + dy, FLAME[5] if dy < -1 or dx else FLAME[6], Lf)
        Lg = p.layer(f"lampg{phase}", ("flicker", phase) if motion else None, z=21.5)
        p.halo(fx + 0.5, fy + 0.5, 12 if big else 10, 11 if big else 9, FLAME[4], (0.1, 0.18, 0.26), L=Lg, shape=True)
        p.lights = getattr(p, "lights", []) + [(fx + 0.5, fy + 0.5, reach, reach * 0.72)]
    return (x - 1, x + len(art[0]) + 1)


def _divider_tones(night: bool) -> tuple:
    """The dividers' brass (lit, body, shaded) and steel (lit, shaded)."""
    k = -1 if night else 0
    return GOLD[6 + k], GOLD[4 + k], GOLD[2 + k], SLATE[6 + k], SLATE[3 + k]


def _boss(cells: dict, hx, hy, night):
    """The dividers' hinge: a round boss of brass, lit at its upper left, with its rivet at the middle."""
    lit, body, shade, _, _ = _divider_tones(night)
    for j, row in enumerate((".LLM.", "LLLMM", "LMRMD", "MMMDD", ".MDD.")):
        for i, ch in enumerate(row):
            if ch != ".":
                cells[(hx - 2 + i, hy - 2 + j)] = {"L": lit, "M": body, "D": shade, "R": GOLD[1]}[ch]


def dividers_box(hx, hy, length, ang, spread) -> tuple:
    """The box a pair of dividers lying with the hinge at (hx, hy) covers (see `dividers`), with their ink and
    shadow."""
    xs, ys = [hx - 3, hx + 3], [hy - 3, hy + 3]
    for a in (math.radians(ang + s * spread / 2) for s in (-1, 1)):
        xs.append(hx + math.cos(a) * length)
        ys.append(hy + math.sin(a) * length)
    back = math.radians(ang + 180)
    xs.append(hx + math.cos(back) * 6)
    ys.append(hy + math.sin(back) * 6)
    return (math.floor(min(xs)) - 2, math.floor(min(ys)) - 2, math.ceil(max(xs)) + 3, math.ceil(max(ys)) + 3)


def dividers_cells(hx, hy, night, length=30, ang=20.0, spread=22.0) -> tuple:
    """The cells of a pair of brass dividers lying with the hinge at (hx, hy) (see `dividers`): their brass and
    steel, the lower leg first and the upper lying over it, and their ink round them."""
    lit, body, shade, steel, steel_dark = _divider_tones(night)
    cells: dict = {}
    legs = sorted((math.radians(ang + s * spread / 2) for s in (-1, 1)), key=lambda a: -math.sin(a))
    for a in legs:
        dx, dy = math.cos(a), math.sin(a)
        steep = abs(dy) > abs(dx)
        for i in range(2, length + 1):
            x, y = round(hx + dx * i), round(hy + dy * i)
            tip = length - i
            cells[(x, y)] = steel if tip < 5 else body if i > 4 else lit
            if tip >= 2:
                cells[(x + 1, y) if steep else (x, y + 1)] = steel_dark if tip < 5 else shade
    back = math.radians(ang + 180)
    for i, c in ((3, body), (4, lit), (5, shade)):
        cells[(round(hx + math.cos(back) * i), round(hy + math.sin(back) * i))] = c
    _boss(cells, hx, hy, night)
    return cells, outline(cells, K)


def dividers(p: Pix, hx, hy, night, length=30, ang=20.0, spread=22.0, L="base"):
    """A pair of brass dividers lying across the chart, the hinge at (hx, hy) and the legs opened `spread` degrees
    about `ang` (degrees turned clockwise from pointing right): each leg a bar of brass two pixels thick, lit
    along its upper edge and running out to a point of steel, the hinge a round boss with its rivet and a knob
    behind it to turn them by; inked round, with their shadow on the chart. Returns the cells they cover."""
    cells, edge = dividers_cells(hx, hy, night, length, ang, spread)
    for q in set(edge) | set(cells):
        p.apx(q[0] + 1, q[1] + 1, X["shade_ink"], 0.3, L)
    for q, c in edge.items():
        p.px(q[0], q[1], c, L)
    for q, c in cells.items():
        p.px(q[0], q[1], c, L)
    got = set(cells) | set(edge)
    _mark(p, got)
    return got


# --------------------------------------------------------------------------- the scenes
def _ticks(p: Pix, period: int, col: str) -> str:
    """The pattern of one row of ticks, one every `period` columns from column 0, drawn once a file for each
    spacing and colour. Returns its id."""
    ids = p.__dict__.setdefault("ticks", {})
    if (period, col) not in ids:
        ids[(period, col)] = f"dt{len(ids)}"
        p.defs.append(f'<pattern id="{ids[(period, col)]}" width="{period}" height="1" patternUnits="userSpaceOnUse">'
                      f'<rect width="1" height="1" fill="{col}"/></pattern>')
    return ids[(period, col)]


def degree_ticks(p: Pix, x0, x1, y, night, tall=True, L="base"):
    """The graduation along a chart's lower neatline: a tick every two pixels over the rule at row y and a longer
    one every ten, left out wherever a word lies within two units; each run of them laid as one strip of a
    pattern of ticks, and kept in the drawing's `filled`."""
    col = INK[3] if not night else GOLD[2]
    short = [x for x in range(x0 + 1, x1 - 1) if x % 2 == 0 and p.clear_of_words(x - 2, y - 4, x + 3, y + 1)]
    tens = [x for x in short if tall and x % 10 == 0 and p.clear_of_words(x - 2, y - 5, x + 3, y)]
    for period, xs, row in ((2, short, y - 1), (10, tens, y - 2)):
        runs = []
        for x in xs:
            if runs and x - runs[-1][1] == period:
                runs[-1][1] = x
            else:
                runs.append([x, x])
        for a, b in runs:
            pid = _ticks(p, period, col)
            p.shapes[L].append(f'<rect x="{a}" y="{row}" width="{b - a + 1}" height="1" fill="url(#{pid})"/>')
    _mark(p, {(x, y - 1) for x in short} | {(x, y - 2) for x in tens})


def _box_free(p: Pix, x0, y0, x1, y1, taken=(), margin=3) -> bool:
    """Whether the box (x0, y0, x1, y1) keeps `margin` from every word, touches none of `taken` and keeps out of
    the top centre a header keeps for the month's mark (see `top_centre`)."""
    if not p.clear_of_words(x0 - margin, y0 - margin, x1 + margin, y1 + margin):
        return False
    if not _off_top_centre(p, x0, y0, x1, y1):
        return False
    return all(x1 <= a or x0 >= c or y1 <= b or y0 >= d for a, b, c, d in taken)


def _lie(p: Pix, hinges, g, taken) -> tuple | None:
    """Where a pair of dividers can lie across the chart above row g: the hinge at the first column of `hinges`
    that leaves them room, keeping clear of every word and of the `taken` boxes, at the longest and widest
    opening that fits and as low on the chart as they go; None when none fits."""
    for hx in hinges:
        for (length, ang, spread) in ((30, 14, 28), (30, 8, 22), (26, 6, 20), (24, 2, 18)):
            for hy in range(g - 10, g - 22, -1):
                box = dividers_box(hx, hy, length, ang, spread)
                if box[3] <= g + 1 and _box_free(p, *box, taken=taken, margin=2):
                    return (hx, hy, length, ang, spread)
    return None


def map_h1(p: Pix, rule: int, night: bool, motion: bool) -> list:
    """The wide H1's map. On the known coast at the left, hills and trees and the walled city on its promontory
    with the river coming down to the bay beside it, and in the sea under it the compass rose and the cog on her
    dotted route out of the harbour; in the unknown land at the right the dragon, and in the sea under it the
    serpent looping and the whale spouting. Where the words leave the sea beside the title free, the rose takes
    it at the left and a second ship at the right. By night the lantern stands on the chart at the foot of the
    right side with its light pooled round it, the whale gone to where the words leave room, and the brass
    dividers lie across the sea under the city. Returns the spans of the rule the scene covers."""
    w = p.w
    g = rule - 1
    spans = []
    moving = motion
    city_base = h1_city_base(rule)
    # the known coast: hills inland behind the city, trees among them, the river down to the bay
    for (hx, hb, art) in ((5, 0, HILL), (17, -3, HILL_SMALL), (26, -1, HILL), (13, 1, TREE), (37, -2, FIR),
                          (2, 2, FIR)):
        base = city_base - 20 + hb
        if base - len(art) > TOP_BAND + 11:
            map_symbol(p, art, hx, base, night)
    river(p, [(40, city_base - 23), (38, city_base - 16), (41, city_base - 9), (44, city_base + 2)], night)
    spans.append(city(p, 6, city_base, night))
    # the rose: in the sea beside the title where it is free, else under the city
    R = 11
    title_side = None
    for (ux, uy) in ((84, 44), (78, 42), (90, 44)):
        if _box_free(p, ux - R - 2, uy - R - 6, ux + R + 2, uy + R + 2, margin=2):
            title_side = (ux, uy)
            break
    rc = title_side or (19, g - 14)
    rose_top = rc[1] - R - 5
    if title_side or rose_top > city_base + 4:
        rose(p, rc[0], rc[1], R, night)
        needle(p, rc[0], rc[1], R, night, motion=moving)
    # the cog on her dotted route out of the harbour, beside the rose or, when the rose is up by the title,
    # nearer the shore
    wl = g - 3
    cx = 10 if title_side else 28
    if not _box_free(p, cx - 2, wl - 22, cx + 30, wl + 3, margin=2):
        cx = 30
    if wl - 22 > city_base + 3:
        cog(p, cx, wl, night, motion=moving)
        route(p, [(48, city_base + 3), (46, city_base + 9), (cx + 3, wl + 3)], night)
        route(p, [(cx + 30, wl + 2), (cx + 46, wl + 1), (cx + 64, wl + 2)], night)
    # a second ship beside the title at the right, where the sea there is free
    for sx in (322, 328, 316):
        if _box_free(p, sx - 3, 34, sx + 18, 52, margin=2):
            cog(p, sx, 48, night, motion=moving, small=True, phase=1)
            route(p, [(sx - 14, 52), (sx - 4, 50)], night)
            route(p, [(sx + 18, 49), (sx + 30, 51)], night)
            break
    # the unknown land: the dragon on it, and the serpent in the sea under it
    db = h1_dragon_base(rule)
    spans.append(dragon(p, w - 42, db, night))
    swl = db + 23
    if swl + 3 < g - 4:
        serpent(p, w - 52, swl, night, motion=moving, coils=2)
    if night:
        big = swl + 4 < g - len(LANTERN_BIG) - 1
        lx = w - 24 if big else w - 22
        spans.append(lantern(p, lx, g, night, motion=motion, big=big, reach=82))
        taken = [(lx - 3, g - 27, w, g + 2), (w - 54, swl - 20, w, swl + 5)]
        lie = _lie(p, range(lx - 36, 250, -4), g, taken)
        if lie:
            dividers(p, *lie[:2], night, length=lie[2], ang=lie[3], spread=lie[4], L=p.layer("lie", None, z=2))
        else:
            dividers(p, 9, city_base + 7, night, length=30, ang=30)
    elif swl + 3 < g - 16:
        spans.append(whale(p, w - 40, g - 3, night, motion=moving))
    elif _box_free(p, 296, g - 16, 334, g + 1):
        whale(p, 300, g - 3, night, motion=moving)
    return spans


def map_h2(p: Pix, rule: int, night: bool, motion: bool) -> list:
    """The section header's chart beside the title: the great compass rose with its needle swinging and settling
    on north in a moving header and its rhumb lines raking the sea under the words, the cape at the foot with
    its watch tower, and a cog sailing under the rose where the words leave room; by night the lantern stands
    on the cape with its light pooled over the rose, and the brass dividers lie across the sea at its foot.
    Built to the room the words leave: the rose is smaller as the words come nearer. Returns the spans of the
    rule it covers."""
    w = p.w
    g = rule - 1
    moving = motion
    spans = []
    R = 20
    cx = w - 54
    while R > 11 and not _box_free(p, cx - R - 2, TOP_BAND + 8, cx + R + 2, g - 12, margin=2):
        R -= 3
    cy = max(TOP_BAND + 10 + R, min(g - 30, (TOP_BAND + 6 + g - 12) // 2 + 2))
    if _box_free(p, cx - R - 2, cy - R - 6, cx + R + 2, cy + R + 2, margin=2):
        rose(p, cx, cy, R, night)
        needle(p, cx, cy, R, night, motion=moving)
    # the cape with its tower, or by night the lantern on it
    tx = w - 26
    taken = [(cx - R - 3, cy - R - 7, cx + R + 3, cy + R + 3)]
    if night:
        big = g - 1 - len(LANTERN_BIG) > TOP_BAND + 14
        lx = tx - 4 if big else tx - 2
        spans.append(lantern(p, lx, g - 1, night, reach=74, motion=motion, big=big))
        taken.append((lx - 3, g - 28, w, g + 2))
        lie = _lie(p, range(lx - 36, w - 150, -4), g, taken)
        if lie:
            dividers(p, *lie[:2], night, length=lie[2], ang=lie[3], spread=lie[4], L=p.layer("lie", None, z=2))
            taken.append(dividers_box(*lie[:2], *lie[2:]))
    else:
        tower(p, tx, g - 3, 6, 14, night, flag=True)
        spans.append((tx - 2, tx + 8))
    for sx in (w - 104, w - 110, w - 120, w - 130, w - 140):
        if _box_free(p, sx - 3, g - 22, sx + 44, g + 2, taken=taken, margin=2):
            cog(p, sx, g - 3, night, motion=moving, phase=2)
            route(p, [(sx + 30, g - 1), (sx + 44, g - 2), (w - 34, g - 4)], night)
            spans.append((sx - 2, sx + 30))
            taken.append((sx - 3, g - 22, sx + 30, g + 2))
            break
    return spans


def map_h3(p: Pix, rule: int, night: bool, motion: bool) -> list:
    """The strip's chart: its hero at its right, the great sea serpent rearing up out of the waves as tall as the
    strip, from the foam at its foot to its horns under the band across the top, its head facing the words, its
    coils arching behind it and rising and sinking in a moving header (see `great_serpent`); by night coiled once,
    with the lantern standing beside it and its light pooled round it. Where a word comes too near for both its
    coils, it rears with one, nearer the border. In the open sea the words leave, a cog under sail on her dotted
    route, and islands (see `finish`). Returns the spans of the rule it covers."""
    w = p.w
    g = rule - 1
    moving = motion
    wl = g - 4
    spans, taken = [], []
    lamp_x = w - BAND - 13
    tries = [(w - BAND - 59, 1)] if night else [(w - BAND - 59, 2), (w - BAND - 46, 1)]
    for x, coils in tries:
        top = next((t for t in range(SERPENT_TOP, wl - 40) if all(
            _box_free(p, *b, margin=2) for b in serpent_boxes(x, wl, t, coils))), None)
        if top is not None:
            spans.append(great_serpent(p, x, wl, top, night, motion=moving, coils=coils))
            taken.append((x - 2, top - 2, w, g + 2))
            break
    if night:
        spans.append(lantern(p, lamp_x, g, night, reach=60, motion=motion))
        taken.append((lamp_x - 2, g - 21, w, g + 2))
    # a cog under sail on her dotted route across the open sea, where the words leave it
    for sx in range(w - 100, w // 2 - 30, -10):
        if _box_free(p, sx - 16, g - 23, sx + 44, g + 1, taken=taken, margin=3):
            cog(p, sx, g - 3, night, motion=moving, phase=3)
            route(p, [(sx - 16, g - 1), (sx - 3, g - 2)], night)
            route(p, [(sx + 30, g - 2), (sx + 42, g - 1)], night)
            spans.append((sx - 2, sx + 30))
            break
    return spans


def section_star_cells(night: bool) -> dict:
    """A small compass star in gilt, 7 by 7 from (0, 0): four long points and four short, outlined."""
    pts = [(d, 1.7, 0.8, GOLD[5], GOLD[2]) for d in (45, 135, 225, 315)]
    pts += [(d, 2.6, 1.0, GOLD[6] if night else GOLD[5], GOLD[3] if night else GOLD[2]) for d in (0, 90, 180, 270)]
    cells = star_cells(3.5, 3.5, pts)
    cells.update(outline(cells, NIGHT[0] if night else K))
    cells[(3, 3)] = VERM[3]
    return cells


def section_star(p: Pix, x, y, night, L="base"):
    """A small compass star in gilt after SECTION A-A, its top a row under the hook's row or lower, as far down
    as keeps it two units clear of the banderole over it. Drawn once a file and placed."""
    key = ("sectionstar", night)
    cells = section_star_cells(night)
    if key not in p.syms:
        p.symbol(key, cells)
    top = y + 1
    while top < y + 5 and not p.clear_of_words(x - 3, top - 3, x + 10, top + 1):
        top += 1
    p.use(key, x, top, L)
    _mark(p, {(x + i, top + j) for (i, j) in cells})


# A small wind head for a strip, 13 by 11, facing right: curls, a blown cheek, an eye shut and pursed lips.
WIND_SMALL = [
    "...kkkkk.....",
    ".kkYyYyYkk...",
    "kYyqyYyqyyk..",
    "kyqykkkkkyk..",
    "kYqkFFFFFkk..",
    "kyqkFeeFFFk..",
    "kYkFSSFFFFLk.",
    ".kkSccFFFLmLk",
    "..kFccFFFFLk.",
    "...kkFFFkkk..",
    ".....kkk.....",
]


def strip_wind(p: Pix, x, y, night, L="base"):
    """A small wind head beside a strip's title, top-left at (x, y) or as far right of it as keeps it two units
    clear of the banderole, blowing a few short lines of wind toward the right; its wind shortened, or the head
    left out, where the room runs short."""
    for dx in range(0, 24):
        if p.clear_of_words(x + dx - 3, y - 3, x + dx + 16, y + 14):
            x += dx
            break
    else:
        return
    pal = wind_pal(night)
    p.sprite(x, y, WIND_SMALL, pal, 1, L)
    cells = {(x + i, y + j) for j, row in enumerate(WIND_SMALL) for i, ch in enumerate(row) if ch != "."}
    col, tip = (INK[2], INK[5]) if not night else (GOLD[3], GOLD[1])
    for (dy, ln, ph) in ((-1, 14, 0.0), (1, 11, 1.8)):
        for i in range(ln):
            yy = y + 7 + dy + round(math.sin(i / 3.0 + ph))
            if (i > ln - 5 and i % 2) or not p.clear_of_words(x + 11 + i, yy - 3, x + 16 + i, yy + 4):
                continue
            p.px(x + 13 + i, yy, col if i < ln - 5 else tip, L)
            cells.add((x + 13 + i, yy))
    _mark(p, cells)


# The islands a phone's sea takes, smaller than a wide chart's.
PHONE_ISLES = ((12, 6), (10, 5), (8, 4))


def _open(p: Pix, box, taken=(), margin=3, sea=True) -> bool:
    """Whether `box` (x0, y0, x1, y1) keeps `margin` from every word, touches none of `taken` and, for a thing
    afloat (`sea`), keeps two clear of every land's coast."""
    x0, y0, x1, y1 = box
    if not _box_free(p, x0, y0, x1, y1, taken=taken, margin=margin):
        return False
    if sea:
        for side, _, reach in getattr(p, "lands", ()):
            for y in range(max(0, y0 - 2), min(len(reach), y1 + 3)):
                r = reach[y]
                if r is not None and (x0 - 2 <= r if side < 0 else x1 + 2 >= r):
                    return False
    return True


def _land_at(p: Pix, side: int, y: int):
    """How far the land on `side` (-1 the left, 1 the right) reaches at row y, or None."""
    for s, _, reach in getattr(p, "lands", ()):
        if s == side and 0 <= y < len(reach):
            return reach[y]
    return None


def phone_h1(p: Pix, y, night):
    """A phone's map in the rows its words leave above the rule at row y: the walled city on its promontory at
    the left with hills behind it, the dragon in the unknown land at the right and by night the lantern standing
    there with its light pooled, the cog on her dotted route out of the bay, the serpent looping, the compass
    rose over them with its rhumb lines and the whale in the open sea; each set where it fits and left out where
    it does not, so the map is built to the room the words leave."""
    g = y - 1
    top = getattr(p, "words_end", g - 30) + 2
    w = p.w
    taken = []
    # the walled city on the promontory, as low on it as it stands, and hills and trees inland behind it
    for base in range(g - 3, top + 22, -1):
        r = _land_at(p, -1, base)
        if r is not None and r >= 31 and _open(p, (4, base - 23, 32, base + 1), taken, 2, sea=False):
            city(p, 6, base, night, small=True)
            taken.append((4, base - 23, 32, base + 1))
            for (hx, hb, art) in ((4, -21, HILL_SMALL), (16, -24, HILL_SMALL), (27, -20, TREE)):
                hr = _land_at(p, -1, base + hb)
                if hr is not None and hr >= hx + len(art[0]) + 2 and _open(
                        p, (hx - 1, base + hb - len(art) - 1, hx + len(art[0]) + 1, base + hb + 1), taken, 2, False):
                    map_symbol(p, art, hx, base + hb, night)
                    taken.append((hx - 1, base + hb - len(art) - 1, hx + len(art[0]) + 1, base + hb + 1))
            break
    else:
        for (hx, art) in ((6, HILL), (20, FIR), (25, TREE)):
            if _open(p, (hx - 1, g - 3 - len(art), hx + len(art[0]) + 1, g - 2), taken, 3, sea=False):
                map_symbol(p, art, hx, g - 3, night)
    # by night the lantern standing on the unknown land at the foot with its light pooled, and the dragon in that
    # land where it is still free
    if night:
        for lx in (w - 20, w - 24):
            if _open(p, (lx - 2, g - 21, lx + 14, g + 1), taken, 2, sea=False):
                lantern(p, lx, g, night, reach=60, motion=False)
                taken.append((lx - 2, g - 21, lx + 14, g + 1))
                break
    for base in range(g - 2, top + 22, -1):
        r = _land_at(p, 1, base)
        if r is not None and r <= w - 38 and _open(p, (w - 38, base - 23, w - 4, base + 1), taken, 2, sea=False):
            dragon(p, w - 37, base, night)
            taken.append((w - 38, base - 23, w - 4, base + 1))
            break
    # the cog on her dotted route out of the bay
    for cx in range(44, 110, 4):
        if _open(p, (cx - 2, g - 24, cx + 31, g + 1), taken):
            cog(p, cx, g - 3, night)
            route(p, [(30, g - 6), (cx - 3, g - 1)], night)
            taken.append((cx - 4, g - 24, cx + 31, g + 1))
            break
    # the serpent looping where the sea is still open at the foot
    for sx in range(150, 40, -4):
        if _open(p, (sx - 1, g - 23, sx + 37, g + 1), taken):
            serpent(p, sx, g - 4, night, coils=1)
            taken.append((sx - 2, g - 23, sx + 37, g + 1))
            break
    # the compass rose over them, as big as the room above them or beside the words allows and as low as it goes,
    # its rhumb lines raking the sea
    placed = False
    for R in (11, 9, 7):
        for cy in range(g - R - 3, TOP_BAND + R + 6, -1):
            for cx in sorted(range(16, w - 16, 3), key=lambda c: abs(c - w // 2)):
                if _open(p, (cx - R - 2, cy - R - 6, cx + R + 3, cy + R + 3), taken):
                    rose(p, cx, cy, R, night)
                    needle(p, cx, cy, R, night, motion=False)
                    taken.append((cx - R - 2, cy - R - 6, cx + R + 3, cy + R + 3))
                    placed = True
                    break
            if placed:
                break
        if placed:
            break
    # the whale in the open sea that is left
    for wl in range(top + 13, g - 1):
        for wx in range(10, w - 44, 4):
            if _open(p, (wx - 2, wl - 12, wx + 31, wl + 3), taken):
                whale(p, wx, wl, night)
                return


def serpent_head(p: Pix, x, wl, night):
    """The serpent's head and neck alone rising from the waves, for the smallest room."""
    from ...holidays.pixel import tube
    k = -1 if night else 0
    colour = _serpent_colour(night)
    neck = [(x + 11, wl - 7), (x + 12, wl - 4), (x + 13, wl - 1), (x + 13, wl + 1)]
    cells = set(tube(p, neck, 2.3, colour, outline=K))
    p.sprite(x, wl - 18, SERPENT_HEAD, {"k": K, "V": VERM[4 + k], "v": VERM[2 + k], "Y": GOLD[4 + k],
                                        "e": GOLD[6], "t": PARCH[6], "r": VERM[5 + k]})
    cells |= {(x + i, wl - 18 + j) for j, row in enumerate(SERPENT_HEAD) for i, ch in enumerate(row) if ch != "."}
    foam = PARCH[6] if not night else DEEP[6]
    for dx in (9, 10, 11, 15, 16, 17):
        p.px(x + dx, wl, foam)
        cells.add((x + dx, wl))
    _mark(p, cells)


def _spoken(p: Pix, margin=2, coast=3, top=TOP_BAND, rule=None):
    """What of a sheet is spoken for, kept as a summed-area table: every cell within `margin` of a word, under
    anything drawn there but light and shadow, in the border, above row `top` (a header's top band) or from row
    `rule` down (the chart's rule, or a footer's foot), in the top centre a header keeps for the month's mark (see
    `top_centre`), and on a land or within `coast` of its shore. Returns free(box): whether the box (x0, y0, x1,
    y1), ends excluded, holds none of it."""
    w, h = p.w, p.h
    rule = getattr(p, "chart", (None, h))[1] if rule is None else rule
    busy = [[not (BAND < x < w - BAND - 1 and top < y < rule) for x in range(w)] for y in range(h)]
    keep = top_centre(p)
    boxes = [(a - margin, b - margin, c + margin, d + margin) for a, b, c, d in p.words] + ([keep] if keep else [])
    for (x0, y0, x1, y1) in boxes:
        for y in range(max(0, y0), min(h, y1)):
            for x in range(max(0, x0), min(w, x1)):
                busy[y][x] = True
    cells = set(getattr(p, "filled", ()))
    for name, layer in p.layers.items():
        if not (name.startswith(("haze", "lampg", "fb", "tb", "swell")) or name.endswith("+")):
            cells |= {q for q, c in layer.items() if ":" not in c}      # a see-through shadow or light holds nothing
    for (x, y) in cells:
        if 0 <= x < w and 0 <= y < h:
            busy[y][x] = True
    for side, _, reach in getattr(p, "lands", ()):
        for y in range(min(h, len(reach))):
            if reach[y] is not None:
                for x in (range(0, min(w, reach[y] + coast + 1)) if side < 0 else range(max(0, reach[y] - coast), w)):
                    busy[y][x] = True
    S = [[0] * (w + 1) for _ in range(h + 1)]
    for y in range(h):
        acc = 0
        for x in range(w):
            acc += busy[y][x]
            S[y + 1][x + 1] = S[y][x + 1] + acc

    def free(box) -> bool:
        x0, y0, x1, y1 = box
        if x0 < 0 or y0 < 0 or x1 > w or y1 > h or x0 >= x1 or y0 >= y1:
            return False
        return S[y1][x1] - S[y0][x1] - S[y1][x0] + S[y0][x0] == 0
    return free


@functools.lru_cache(maxsize=64)
def _isle_extent(rx: int, ry: int, seed: int) -> tuple:
    """The furthest an island's cells reach about its middle: (left, top, right, bottom), ends included."""
    cells = isle_cells(rx, ry, seed)
    return (min(q[0] for q in cells), min(q[1] for q in cells), max(q[0] for q in cells), max(q[1] for q in cells))


def _sea_box(name, x, wl) -> tuple:
    """The box (x0, y0, x1, y1), ends excluded, that a thing afloat on a footer's open chart takes (see
    `_furnish`): the cog, the small cog, the whale or the serpent's head, drawn from column x on the waterline
    at row wl."""
    return {"cog": (x - 3, wl - 22, x + 31, wl + 3), "small cog": (x - 3, wl - 12, x + 18, wl + 3),
            "whale": (x - 3, wl - 12, x + 32, wl + 4), "head": (x - 1, wl - 19, x + 19, wl + 5)}[name]


# The rows a phone's section and strip ask for under their words, for their heroes at their full height: the great
# compass rose over the sea, and the great serpent rearing beside the coast.
PHONE_ROWS = {"H2": 54, "H3": 50}
ROSE_R = 22            # the great compass rose's radius on a phone section, a little greater than a wide one's
SERPENT_TALL = 46      # the rows a phone strip's great serpent rises, from the foam at its foot to its horns


def phone_rose(p: Pix, y0: int, y1: int, night: bool) -> tuple:
    """A phone section's hero, under its words from their last line at row y0 down to the rule at y1: the great
    compass rose over the sea, ROSE_R across from its middle, its needle on north and its rhumb lines raking the
    chart (see `finish`); the cog under sail on her dotted route at its left, the whale spouting at its right,
    and the cape coming in at the foot beyond it (see `chart_lands`) with its watch tower, or by night the lantern
    standing on it, its light pooled over them. Each keeps two units clear of every word. Returns the rose's
    middle and its radius."""
    g = y1 - 1
    wl = g - 3
    R, cx = ROSE_R, BAND + 70
    cy = g - R - 2
    while R > 12 and not _box_free(p, cx - R - 2, cy - R - 6, cx + R + 3, cy + R + 3, margin=2):
        R -= 1
        cy = g - R - 2
    rose(p, cx, cy, R, night)
    needle(p, cx, cy, R, night, motion=False)
    cog(p, BAND + 4, wl, night)
    route(p, [(BAND + 35, wl + 2), (cx - R - 4, wl + 1)], night)
    whale(p, cx + R + 5, wl, night)
    tip = min((r for r in (_land_at(p, 1, y) for y in range(y0, g)) if r is not None), default=p.w - BAND)
    if night:
        lantern(p, tip + 6, g - 1, night, reach=52, motion=False)
    else:
        tower(p, tip + 8, g - 2, 6, 14, night, flag=True)
    p.strip = (y0, y1)
    return (cx, cy, R)


def phone_serpent(p: Pix, y0: int, y1: int, night: bool) -> tuple:
    """A phone strip's hero, under its words from their last line at row y0 down to the rule at y1: the great
    serpent rearing out of the waves at the right, as the wide strip has it, SERPENT_TALL rows from the foam to
    its horns, its coils arching behind it; at the left the known coast coming down to the sea (see
    `chart_lands`), the walled city on its point with the hills behind it; and between them the cog sailing out
    of the harbour on her dotted route. By night the serpent is coiled once and the lantern stands beside it with
    its light pooled over them. Returns the serpent's span."""
    g = y1 - 1
    wl = g - 4
    x = p.w - BAND - 59
    span = great_serpent(p, x, wl, wl + 4 - SERPENT_TALL, night, coils=1 if night else 2)
    if night:
        lantern(p, p.w - BAND - 13, g, night, reach=52, motion=False)
    taken = [(x - 2, wl + 4 - SERPENT_TALL - 2, p.w, g + 2)]
    for base in range(g - 2, y0 + 24, -1):
        r = _land_at(p, -1, base)
        if r is not None and r >= 31 and _open(p, (4, base - 24, 32, base + 1), taken, 2, sea=False):
            city(p, 6, base, night, small=True)
            taken.append((4, base - 24, 32, base + 1))
            for (hx, hb, art) in ((4, -21, HILL_SMALL), (17, -24, HILL_SMALL)):
                hr = _land_at(p, -1, base + hb)
                box = (hx - 1, base + hb - len(art) - 1, hx + len(art[0]) + 1, base + hb + 1)
                if hr is not None and hr >= hx + len(art[0]) + 2 and _open(p, box, taken, 2, False):
                    map_symbol(p, art, hx, base + hb, night)
                    taken.append(box)
            break
    reach = next((r for r in (_land_at(p, -1, y) for y in range(g, y0, -1)) if r is not None), BAND)
    for cx in range(max(reach + 8, 44), x - 30):
        if _open(p, (cx - 3, wl - 22, cx + 31, wl + 3), taken):
            cog(p, cx, wl + 1, night)
            route(p, [(reach + 2, wl - 2), (cx - 4, wl + 2)], night)
            break
    p.strip = (y0, y1)
    return span


def finish(p: Pix, night: bool):
    """A sheet's last pass, once every word is set, which a header drawn lighter to fit its budget is given too:
    on a time line islands along its voyage (see `voyage_isles`); on a header islands in the open sea its words
    and drawings leave (two on a wide H1 or H3, three on a wide H2, one on an H1 phone, and on a phone's H2 or H3
    two over the hero standing under its words); then the rhumb lines raking the sea from each compass rose,
    broken round every word and drawing; by night each lantern's light pooled over the chart; and the calm laid
    round every word (see `calm`)."""
    chart = getattr(p, "chart", None)
    if getattr(p, "voyage_at", None):
        voyage_isles(p, night)
    if chart:
        if p.w > 300:
            islands(p, chart[1] - 1, night, most={"H2": 3}.get(getattr(p, "kind", ""), 2))
        elif chart[0] in ("H2", "H3"):
            islands(p, getattr(p, "strip", (chart[1],))[0], night, x0=8, x1=p.w - 8, sizes=PHONE_ISLES)
        else:
            islands(p, chart[1] - 1, night, most=1, x0=8, x1=p.w - 8, sizes=PHONE_ISLES)
    rhumb_lines(p, night)
    for (cx, cy, rx, ry) in getattr(p, "lights", ()):
        pool(p, cx, cy, rx, ry)
    calm(p)


# --------------------------------------------------------------------------- the footers
# A small lantern for a footer's corner, 9 by 13: its ring, its cap and foot of brass (B b), its panes (G g) and
# the candle's flame (F f) and wax (W) within; inked round (k). By night its flame and the light through its
# panes are tones of the hand's flame, its heart the brightest.
LANTERN_SMALL = [
    "...kkk...",
    "..k...k..",
    "...kBk...",
    "..kBBbk..",
    ".kBBBBbk.",
    ".kkkkkkk.",
    ".kGgFgGk.",
    ".kGFFFgk.",
    ".kGgfgGk.",
    ".kGgWgGk.",
    ".kkkkkkk.",
    "..kBBbk..",
    ".kkkkkkk.",
]


def small_lantern(p: Pix, x, base, night, reach=30):
    """A small lantern standing on row `base` from column x: by night burning, its light pooled `reach` round it
    over the parchment and the words, held where it reaches a word to what the inks are checked against (see
    `pool`), the lantern standing in front of its own light."""
    k = -1 if night else 0
    pal = {"k": K, "B": GOLD[4 + k], "b": GOLD[2 + k], "G": FLAME[4] if night else PARCH[6],
           "g": FLAME[3] if night else PARCH[4], "F": FLAME[5] if night else PARCH[5],
           "f": FLAME[4] if night else PARCH[4], "W": PARCH[6]}
    top = base - len(LANTERN_SMALL)
    L = p.layer("lamp", None, z=22) if night else "base"
    p.sprite(x, top, LANTERN_SMALL, pal, 1, L)
    own = {(x + i, top + j) for j, row in enumerate(LANTERN_SMALL) for i, ch in enumerate(row) if ch != "."}
    _mark(p, own)
    if night:
        p.px(x + 4, top + 6, FLAME[6], L)
        pool(p, x + 4.5, top + 7.5, reach, reach * 0.72)


def footer_mark(p: Pix, x, y, night):
    """Mark the corner of a footer's closing notes, from (x, y), for the footer's last pass, which sets the
    compass rose in its medallion there with the brass dividers laid before it, and by night the lantern lit
    beside it, once every word is set and the room they leave is known (see `footer_finish`)."""
    p.corner = (x, y)


def medallion_cells(R: int, night: bool) -> dict:
    """A compass rose in its medallion about (0, 0), R to the outer edge of its ring: a roundel of the sea in a
    ring of brass lit along its upper left, inked round, and on the sea the rose, its points running out to the
    ring and its fleur-de-lis standing up through it."""
    k = -1 if night else 0
    sea = C["sea"] if not night else C["sea_night"]
    cells = {}
    for y in range(-R - 1, R + 1):
        for x in range(-R - 1, R + 1):
            dx, dy = x + 0.5, y + 0.5
            rho = math.hypot(dx, dy)
            if rho <= R - 1.6:
                cells[(x, y)] = sea
            elif rho <= R + 0.2:
                facing = (dx * -0.6 + dy * -0.8) / max(0.1, rho)
                cells[(x, y)] = GOLD[5 + k] if facing > 0.45 else GOLD[4 + k] if facing > -0.35 else GOLD[2 + k]
    out = outline(cells, K)
    out.update(cells)
    out.update(rose_cells(0.0, 0.0, R - 1.2, night))
    return out


def closing_cells(R: int, night: bool, side: int) -> tuple:
    """The piece a footer's closing corner holds, about the medallion's middle at (0, 0): the compass rose in its
    medallion of radius R (see `medallion_cells`) with a pair of brass dividers laid before its foot, their
    shadow on the parchment, and by night the lantern standing beside it on `side` (-1 the left, 1 the right, 2
    in front of the medallion's rim at the right). Returns the cells, the shadow's cells and where the lantern
    stands (its column and its foot's row), or None by day."""
    cells = medallion_cells(R, night)
    legs, edge = dividers_cells(-R + 3, R - 2, night, length=2 * R - 1, ang=-9, spread=13)
    shadow = {(x + 1, y + 1) for (x, y) in set(legs) | set(edge)} - set(legs) - set(edge)
    cells.update(edge)
    cells.update(legs)
    lamp = None
    if night and side:
        lamp = {1: (R + 2, R + 3), -1: (-R - 11, R + 3), 2: (R - 5, R + 4)}[side]
    return cells, shadow, lamp


def _piece_box(cells, shadow, lamp) -> tuple:
    """The box (x0, y0, x1, y1), ends excluded, round a closing piece's cells and its lantern."""
    xs = [q[0] for q in cells] + [q[0] for q in shadow]
    ys = [q[1] for q in cells] + [q[1] for q in shadow]
    if lamp:
        xs += [lamp[0], lamp[0] + len(LANTERN_SMALL[0]) - 1]
        ys += [lamp[1] - len(LANTERN_SMALL), lamp[1] - 1]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def closing_piece(p: Pix, night: bool, free, near=None) -> tuple | None:
    """Set the closing piece (see `closing_cells`) where the words leave it room, as big as that room allows (a
    medallion of radius 11 down to 6, the rose in those under 9 too small for its fleur), and by night with its
    lantern on whichever side has room, or standing in front of the medallion's rim where neither has: in the
    middle of the room round `near`, the corner of the closing notes, or with no notes at the far end of the room
    the cells leave. Returns its box, or None where there is no room for it."""
    for R in (11, 10, 9, 8, 7, 6):
        for side in ((1, -1, 2) if night else (0,)):
            cells, shadow, lamp = closing_cells(R, night, side)
            bx0, by0, bx1, by1 = _piece_box(cells, shadow, lamp)
            fits = []
            for cy in range(BAND + 1 - by0, p.h - BAND - by1 + 1):
                for cx in range(BAND + 1 - bx0, p.w - BAND - 1 - bx1 + 1):
                    if near and abs(cx - near[0]) > 60:
                        continue
                    if free((cx + bx0 - 1, cy + by0 - 1, cx + bx1 + 1, cy + by1 + 1)):
                        fits.append((cx, cy))
            if not fits:
                continue
            if near:
                mx = sum(c[0] for c in fits) / len(fits)
                my = sum(c[1] for c in fits) / len(fits)
                cx, cy = min(fits, key=lambda c: (c[0] - mx) ** 2 + (c[1] - my) ** 2)
            else:
                cx, cy = max(fits, key=lambda c: (c[0], -abs(c[1] - p.h / 2)))
            for (x, y) in shadow:
                p.apx(cx + x, cy + y, X["shade_ink"], 0.3, "base")
            for (x, y), c in cells.items():
                p.px(cx + x, cy + y, c)
            _mark(p, {(cx + x, cy + y) for (x, y) in cells} | {(cx + x, cy + y) for (x, y) in shadow})
            if lamp:
                small_lantern(p, cx + lamp[0], cy + lamp[1], night)
            return (cx + bx0, cy + by0, cx + bx1, cy + by1)
    return None


def swell_row(p: Pix, x0, x1, y, night, seed, L="swell"):
    """A row of the sea's swell lines from column x0 to x1 on row y, as the engraver cuts them: short crests of
    three lengths at loose and uneven spacing."""
    rnd = random.Random(seed)
    col = X["wave"] if not night else DEEP[5]
    p.layer(L, z=-10)
    x = x0 + rnd.randrange(7)
    while x < x1 - 7:
        n = rnd.choice((3, 5, 5, 7))
        for (dx, dy) in SWELLS[n]:
            p.px(x + dx, y + dy, col, L)
        x += n + rnd.randrange(5, 13)


def _stretches(p: Pix, x0, x1, top, foot, wide=40) -> list:
    """A cell's columns x0 to x1 split where a stretch of at least `wide` of them holds no word between rows top
    and foot: the stretches with words and the stretches without, in order."""
    bare = [p.clear_of_words(x - 2, top, x + 3, foot) for x in range(x0, x1)]
    out, start = [], x0
    x = x0
    while x < x1:
        if bare[x - x0]:
            end = x
            while end < x1 and bare[end - x0]:
                end += 1
            if end - x >= wide:
                if x > start:
                    out.append((start, x))
                out.append((x, end))
                start = end
            x = end
        else:
            x += 1
    if start < x1:
        out.append((start, x1))
    return out


def sea_band(p: Pix, night: bool, most=6, least=4) -> list:
    """The sea in a footer wherever its cells leave it room, along its foot and along each rule that runs its
    width: under each cell between its upright rules the rows below the cell's lowest word, `most` at the most,
    washed with the sea and its rows of swell lines from one rule to the other under a dotted shore, of one depth
    all along the foot (the depth of its shallowest cell), and none along a foot whose cells leave fewer than
    `least` rows or leave it less than seven tenths of its length; and in each stretch of a cell that holds no
    word, at least forty long, the sea from the rule above to the foot, the chart seen through the footer, its
    coast dotted where it meets the parchment the words are written on and water-lined. Returns the stretches
    laid, as (x0, x1, top, foot, coasts): `coasts` the sides (-1, 1) a stretch of open chart meets the
    parchment on, None for a band under words."""
    w, h = p.w, p.h
    base = p.layers["base"]
    rule = X["rule_night"] if night else X["rule_day"]
    full = [y for y in range(BAND + 1, h - BAND - 2) if sum(base.get((x, y)) == rule for x in range(BAND, w - BAND))
            > 0.8 * w]
    laid, ceiling = [], BAND
    for foot in sorted(set(full) | {h - BAND}):
        uprights = [x for x in range(BAND + 1, w - BAND - 1) if all(base.get((x, y)) == rule for y in
                                                                     range(foot - 4, foot))]
        edges = [BAND] + uprights + [w - BAND - 1]
        cells = []
        for a, b in zip(edges, edges[1:]):
            for (x0, x1) in _stretches(p, a + 1, b, ceiling, foot):
                if x1 - x0 < 20:
                    continue
                low = max((y1 for (u0, v0, u1, y1) in p.words if u0 - 2 < x1 and x0 < u1 + 2 and v0 < foot
                           and y1 > ceiling), default=None)
                if low is None and x1 - x0 >= 40 and foot - ceiling > 12:
                    laid.append((x0, x1, ceiling + 1, foot, tuple(s for s, e, at in ((-1, x0, a + 1), (1, x1, b))
                                                                  if e != at)))
                    continue
                top = max(ceiling + 1 if low is None else low + 2, foot - most)
                if foot - top >= least:
                    cells.append((x0, x1, top))
        if cells and sum(x1 - x0 for x0, x1, _ in cells) >= 0.7 * (w - 2 * BAND):
            top = max(t for _, _, t in cells)
            laid += [(x0, x1, top, foot, None) for x0, x1, _ in cells]
        ceiling = foot + 1
    sea = C["sea"] if not night else C["sea_night"]
    shore = INK[4] if not night else GOLD[2]
    rects = []
    for i, (x0, x1, top, foot, coasts) in enumerate(laid):
        if coasts is None:
            rects.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{foot - top}"/>')
            for x in range(x0, x1, 2):
                p.px(x, top, shore, "swell")
            for j, y in enumerate(range(top + 2, foot - 2, 3)):
                swell_row(p, x0, x1, y, night, seed=i * 7 + j * 3 + x0)
            continue
        left = coast_profile(foot - top, lambda u: x0 + 2, 1.4, x0 * 3 + top, run=2) if -1 in coasts else None
        right = coast_profile(foot - top, lambda u: x1 - 3, 1.4, x1 * 5 + top, run=2) if 1 in coasts else None
        prev = {}
        for j, y in enumerate(range(top, foot)):
            lo = left[j] if left else x0
            hi = right[j] + 1 if right else x1
            rects.append(f'<rect x="{lo}" y="{y}" width="{hi - lo}" height="1"/>')
            for side, at in ((-1, lo - 1 if left else None), (1, hi if right else None)):
                if at is None:
                    continue
                run = [at] if side not in prev else list(range(min(prev[side], at), max(prev[side], at) + 1))
                for x in run:
                    if (x + y) % 2 == 0:
                        p.px(x, y, shore, "swell")
                prev[side] = at
                if (y // 2) % 3 < 2:
                    p.px(at - side * 4, y, X["wave"] if not night else DEEP[5], "swell")
        for j, y in enumerate(range(top + 3, foot - 2, 5)):
            swell_row(p, x0 + (5 if left else 1), x1 - (5 if right else 1), y, night, seed=i * 11 + j * 5 + x0)
    if rects:
        p.under.append(f'<g fill="{sea}">{"".join(rects)}</g>')
    return laid


def _furnish(p: Pix, night: bool, x0, x1, top, foot, used: set) -> list:
    """The open chart a footer shows (see `sea_band`) furnished as the words and the closing piece leave it room:
    the cog under sail (the small one where the big one has no room) with her dotted route trailing behind her,
    the whale spouting, and the serpent's head reared out of the waves; each but once in a footer (`used` keeps
    what its other stretches hold), kept two clear of every word and drawing and four in from the coast, each as
    far to the right and as low as it goes. Returns the boxes taken."""
    taken = []
    for name in ("cog", "small cog", "whale", "head"):
        if name.split()[-1] in used:
            continue
        free = _spoken(p, top=BAND, rule=p.h - BAND)
        hit = None
        for wl in range(foot - 3, top + 8, -1):
            for x in range(x1 - 6, x0 + 5, -1):
                box = _sea_box(name, x, wl)
                if box[0] < x0 + 5 or box[2] > x1 - 1 or box[1] < top or box[3] > foot:
                    continue
                if free(box) and not any(box[0] < t[2] + 4 and t[0] < box[2] + 4 for t in taken):
                    hit = (x, wl, box)
                    break
            if hit:
                break
        if not hit:
            continue
        x, wl, box = hit
        if name.endswith("cog"):
            small = name == "small cog"
            cog(p, x, wl, night, small=small)
            route(p, [(max(x0 + 6, x - 40), wl - 7), (max(x0 + 6, x - 20), wl), (x - 3, wl)], night)
        elif name == "whale":
            whale(p, x, wl, night)
        else:
            serpent_head(p, x, wl, night)
        used.add(name.split()[-1])
        taken.append(box)
    return taken


def footer_finish(p: Pix, night: bool):
    """A footer's last pass, once every word is set, which its layout gives no hook for: the closing piece (see
    `closing_piece`) at the corner of its closing notes, or with none at the far end of the room its cells leave;
    the sea wherever its cells leave it room, along its foot and as open chart in a stretch that holds no word,
    and on the open chart the cog, the whale and the serpent's head where they fit (see `sea_band` and
    `_furnish`); and the parchment's grain and foxing, calmed round every word (see `calm`). Returns the closing
    piece's box, or None."""
    taken = closing_piece(p, night, _spoken(p, top=BAND, rule=p.h - BAND), getattr(p, "corner", None))
    used: set = set()
    for (x0, x1, top, foot, coasts) in sorted(sea_band(p, night), key=lambda r: r[0] - r[1]):
        if coasts is not None:
            _furnish(p, night, x0, x1, top, foot, used)
    _calm_open(p)
    n = len(p.under)
    p.defs.append(_grain("fg", night))
    p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="url(#fgg)"/>')
    _foxing(p, BAND, BAND, p.w - BAND, p.h - BAND, night, seed=p.w * 5 + p.h, n=max(2, p.w * p.h // 7000))
    _calmed(p, n)
    calm(p)
    return taken


def leagues(p: Pix, x0, y0, w, h, night, period=5, L="base"):
    """A chart's scale of leagues for the graphic scale: its leagues dark and light by turns, the lower half of
    each the reverse of its upper half, as a scale is ruled."""
    T = _tones(night)
    for xx in range(x0, x0 + w):
        i = (xx - x0) // period
        for yy in range(y0, y0 + h):
            upper = yy - y0 < (h + 1) // 2
            dark = (i % 2 == 0) == upper
            p.px(xx, yy, T["dark"] if dark else T["light"], L)


# --------------------------------------------------------------------------- the links
# Icons for the link buttons, 9 by 7, bold enough to read at the kit's size and inked in: a compass star, a cog
# under sail, an anchor and a tower. Tones: g G gilt, r vermilion, w the sail, h the hull, s stone, # the
# button's letters.
ICONS = {
    "star": ["....G....", "...GGg...", ".GGGrggg.", "GGGrrrggg", ".gggrGGG.", "...gGG...", "....g...."],
    "ship": ["....#....", "..ww#ww..", "..rrrrr..", "..ww#ww..", "#########", ".#hhhhh#.", "..#####.."],
    "anchor": ["...###...", "...#.#...", "....#....", ".#######.", "....#....", "#...#...#", ".#######."],
    "tower": ["#.#.#.#..", "#######..", ".#sss#...", ".#s#s#...", ".#sss#...", ".#s#s#...", ".#####..."],
}
LINK_ICONS = ("star", "ship", "anchor", "tower")


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a cartouche by day or by night."""
    k = -1 if night else 0
    return {"#": ink, "G": GOLD[5 + k], "g": GOLD[3 + k], "r": VERM[3 + k], "w": PARCH[6] if not night else NIGHT[6],
            "h": LAND[3 + k], "s": PARCH[6] if not night else NIGHT[6]}


def cartouche_ends(p: Pix, w: int, night: bool):
    """A link button finished as a small cartouche: its ends rolled like a scroll's, each a roll of parchment
    inked round with its curl showing, a hairline ruled inside its border, and a shadow under it."""
    k = -1 if night else 0
    roll, rolld, edge = (PARCH[5], PARCH[3], K) if not night else (NIGHT[6], NIGHT[3], GOLD[2])
    for (x0, s) in ((0, 1), (w - 3, -1)):
        for yy in range(1, 13):
            for i in range(3):
                xx = x0 + i
                c = edge if yy in (1, 12) or i == (0 if s > 0 else 2) else (roll if i == 1 else rolld)
                p.px(xx, yy, c)
        p.px(x0 + 1, 4, edge)
        p.px(x0 + 1, 9, edge)
    for xx in range(4, w - 4):
        p.px(xx, 3, GOLD[3 + k] if night else PARCH[5])


# --------------------------------------------------------------------------- the elements: cards and routes
# A cartouche's curl at its top left corner, the frame's rule running out past the corner and turning down and
# in on itself, as (across, down) from the corner; the other corners mirror it.
CURL = ((-1, 0), (-2, 0), (-3, 0), (-4, 1), (-4, 2), (-3, 3), (-2, 3), (-2, 2))


def cartouche_card(p: Pix, x, y, w, h, night, seed, ink, fill):
    """A schematic's card as a cartouche, a label on the chart: its parchment framed in a fine double rule, an
    inked rule a pixel out from its edge and a hairline a pixel in, the outer rule running out at each corner and
    curling back on itself; its shadow on the chart under it; and at its left a roundel washed in one of the map's
    colours by turns (the sea, the land, vermilion or gilt) with the card's icon inked in it. `ink` is the colour
    the layout drew the icon in and `fill` its parchment; the card's words are set over it afterwards."""
    edge, hair = (K, INK[4]) if not night else (GOLD[2], GOLD[1])
    washes = ((C["sea"], SEA[3]), (C["land"], LAND[3]), (VERM[5], VERM[3]), (GOLD[5], GOLD[3])) if not night else \
        ((DEEP[5], DEEP[3]), (DUSK[5], DUSK[3]), (VERM[2], VERM[1]), (GOLD[2], GOLD[1]))
    wash, deep = washes[seed % len(washes)]
    icon_y = y + (h - 7) // 2
    icon = [(xx - x - 2, yy - icon_y) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9)
            if p.get(xx, yy) == ink]
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            p.px(xx, yy, fill)
    # its shadow on the chart, down and to the right
    a = 0.22 if not night else 0.4
    for xx in range(x + 2, x + w + 2):
        p.apx(xx, y + h + 1, X["shade_ink"], a, "base")
    for yy in range(y + 1, y + h + 1):
        p.apx(x + w + 1, yy, X["shade_ink"], a, "base")
    # the double rule: the inked rule a pixel out, the hairline a pixel in
    p.hline(x, x + w - 1, y - 1, edge)
    p.hline(x, x + w - 1, y + h, edge)
    p.vline(x - 1, y, y + h - 1, edge)
    p.vline(x + w, y, y + h - 1, edge)
    p.hline(x + 2, x + w - 3, y + 1, hair)
    p.hline(x + 2, x + w - 3, y + h - 2, hair)
    p.vline(x + 1, y + 2, y + h - 3, hair)
    p.vline(x + w - 2, y + 2, y + h - 3, hair)
    # the outer rule curling out and back at each corner
    for (cx0, cy0, sx, sy) in ((x - 1, y - 1, 1, 1), (x + w, y - 1, -1, 1), (x - 1, y + h, 1, -1),
                               (x + w, y + h, -1, -1)):
        for (dx, dy) in CURL:
            p.px(cx0 + sx * dx, cy0 + sy * dy, edge)
    # the roundel at the left with the icon inked in it
    cx, cy = x + 8.5, icon_y + 3.5
    for yy in range(math.floor(cy - 7), math.ceil(cy + 7)):
        for xx in range(x + 2, x + 16):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if d <= 4.6:
                p.px(xx, yy, deep if (xx + 0.5 - cx) + (yy + 0.5 - cy) > 3.4 else wash)
            elif d <= 5.6:
                p.px(xx, yy, edge)
    for (i, j) in icon:
        p.px(x + 5 + i, icon_y + j, K if not night else GOLD[5])


def wire_route(p: Pix, cells, night):
    """A schematic's wire as a ship's route on a chart: its line broken into dashes, and a small gilt star of the
    compass at every bend."""
    gap = PARCH[6] if not night else NIGHT[3]
    seen: dict = {}
    for i, (x, y, d) in enumerate(cells):
        seen.setdefault((x, y), set()).add(d)
        if 2 < i < len(cells) - 4 and i % 4 == 3:
            p.px(x, y, gap)
    for (x, y), ds in seen.items():
        if len(ds) == 2:
            for (dx, dy, c) in ((0, 0, VERM[3]), (1, 0, GOLD[4]), (-1, 0, GOLD[4]), (0, 1, GOLD[2]), (0, -1, GOLD[5])):
                p.px(x + dx, y + dy, c)


# --------------------------------------------------------------------------- the elements: instruments
ROOFS = (VERM, SEA, RAMP["blue"], GOLD)


def tower_bar(p: Pix, bx, base, bw, v, night, i=0):
    """A week's commits as a tower drawn as a chart draws a city: a shaft of stone `bw` wide inked round, lit down
    its left and shaded down its right, its windows dark, under a pointed roof in its own colour (vermilion,
    verdigris copper, blue slate and gilt by turns); the roof takes the top of the bar's height."""
    k = -1 if night else 0
    lit, face, shade = _stone(night)
    ramp = ROOFS[i % len(ROOFS)]
    roof = min(v - 2, max(2, bw // 2 + 1)) if v > 4 else 0
    top = base - v + roof
    for yy in range(top, base):
        for xx in range(bx, bx + bw):
            if xx in (bx, bx + bw - 1) or yy == top:
                c = K
            elif xx == bx + 1:
                c = lit
            elif xx >= bx + bw - 2 and bw > 4:
                c = shade
            else:
                c = face
            p.px(xx, yy, c)
    if bw >= 5:
        cx = bx + bw // 2
        for yy in range(top + 3, base - 2, 5):
            p.px(cx, yy, K)
            p.px(cx, yy + 1, K)
    if roof:
        half = bw / 2
        for j in range(roof):
            r = half * (j + 1) / roof
            a, b = math.floor(bx + half - r), math.ceil(bx + half + r) - 1
            for xx in range(a, b + 1):
                edge = xx in (a, b)
                p.px(xx, base - v + j, K if edge else (ramp[4 + k] if xx < bx + half else ramp[2 + k]))
    p.last_bar = (bx, base, bw, v, i)


def pennant_mark(p: Pix, x, y, night):
    """A pennant on a staff beside the busiest week's count, flown from its tower."""
    k = -1 if night else 0
    for yy in range(y, y + 7):
        p.px(x, yy, K)
    for (dx, dy, c) in ((1, 0, VERM[4 + k]), (2, 0, VERM[4 + k]), (3, 0, VERM[3 + k]), (4, 1, VERM[2 + k]),
                        (1, 1, VERM[3 + k]), (2, 1, VERM[3 + k]), (3, 1, VERM[2 + k]), (1, 2, VERM[2 + k])):
        p.px(x + dx, y + dy, c)


def bezel_cells(cx: float, cy: float, r: float, night: bool) -> dict:
    """The compass's half bezel for the dial: a ring of brass lit along its upper left, and inside it the points of
    the rose, thirty-two of them, ink and vermilion by turns, standing in from the ring."""
    k = -1 if night else 0
    cells = {}
    for y in range(math.floor(cy - r) - 3, math.ceil(cy) + 1):
        for x in range(math.floor(cx - r) - 3, math.ceil(cx + r) + 3):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            if dy > 0.5:
                continue
            if r - 1.6 <= rho <= r + 1.4:
                facing = (dx * -0.6 + dy * -0.8) / max(0.1, rho)
                cells[(x, y)] = GOLD[5 + k] if facing > 0.4 else GOLD[4 + k] if facing > -0.2 else GOLD[2 + k]
                if rho > r + 0.7 or rho < r - 1.1:
                    cells[(x, y)] = K if rho > r + 0.7 else GOLD[2 + k]
                continue
            ang = math.degrees(math.atan2(dy, dx)) % 360
            seg = ang / 11.25
            off = abs(seg - round(seg)) * 11.25
            n = int(round(seg)) % 32
            reach = 5.0 if n % 8 == 0 else 3.5 if n % 4 == 0 else 2.5 if n % 2 == 0 else 1.6
            if r - 1.6 - reach <= rho < r - 1.6 and off < 3.2 * (rho - (r - 1.6 - reach)) / reach:
                cells[(x, y)] = (INK[2] if not night else GOLD[2]) if n % 2 == 0 else VERM[3 + k]
    return cells


def dial_rose(p: Pix, cx, cy, r, night):
    """The compass card under the dial's needle: the upper half of a sixteen-point rose about the pivot in the
    chart's own tones, inked round, as big as the figures round the face leave room for."""
    room = min((math.hypot(min(max(cx, x0), x1) - cx, min(max(cy, y0), y1) - cy) for (x0, y0, x1, y1) in p.words
                if y0 < cy), default=r)
    R = min(r - 4, room - 3)
    if R < 6:
        return
    T = rose_tones(night)
    pts = [(d + 22.5, R * 0.52, R * 0.14, *T["half"]) for d in range(0, 360, 45)]
    pts += [(d, R * 0.74, R * 0.2, *T["inter"]) for d in (45, 135, 225, 315)]
    pts += [(d, R, R * 0.26, *T["card"]) for d in (0, 90, 180, 270)]
    cells = {q: c for q, c in star_cells(cx, cy, pts).items() if q[1] < cy}
    cells.update({q: c for q, c in outline(cells, T["line"]).items() if q[1] < cy and q not in cells})
    L = p.layer("dialrose", None, z=-1)
    for (x, y), c in cells.items():
        p.px(x, y, c, L)


def gauge_needle(p: Pix, cx, cy, r, night, accent):
    """The dial's hand as a magnetised needle laid from the pivot, in place of the plain line the layout drew: a
    long diamond, its pointing half in vermilion and its tail in steel, each lit along one side."""
    reach = r - 11
    hand = [(x, y) for (x, y), c in p.layers["base"].items() if c == accent
            and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2]
    if not hand:
        return
    far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
    ang = math.atan2(far[1] + 0.5 - cy, far[0] + 0.5 - cx)
    ca, sa = math.cos(ang), math.sin(ang)
    k = -1 if night else 0
    for (x, y) in hand:
        p.px(x, y, VERM[3 + k])
    tail = reach * 0.45
    for y in range(math.floor(cy - reach) - 2, math.ceil(cy + reach) + 2):
        for x in range(math.floor(cx - reach) - 2, math.ceil(cx + reach) + 2):
            along = (x + 0.5 - cx) * ca + (y + 0.5 - cy) * sa
            perp = -(x + 0.5 - cx) * sa + (y + 0.5 - cy) * ca
            if along >= 0:
                width = 1.6 * (1 - along / reach) + 0.25 if along <= reach else -1
                if abs(perp) <= width:
                    p.px(x, y, VERM[4 + k] if perp < 0 else VERM[2 + k])
            elif along >= -tail:
                width = 1.6 * (1 + along / tail) + 0.25
                if abs(perp) <= width and y <= cy + 1:
                    p.px(x, y, SLATE[5 + k] if perp < 0 else SLATE[2 + k])


def material_wash(i: int, xx, yy, y0, y1, lift, night) -> str:
    """The map's washes by turns for a ribbon of file types: the sea in verdigris with its ripples, the land in
    ochre stippled, vermilion, gilt, slate, and bare parchment hatched; each lit along its top and shaded along its
    foot."""
    kind = i % 6
    k = -1 if night else 0
    if kind == 0:
        c = SEA[4 + k] if ((xx + (yy - y0) * 3) % 8 in (0, 1) and (yy - y0) % 4 == 1) else SEA[5 + k]
    elif kind == 1:
        c = LAND[3 + k] if (xx * 3 + yy * 5) % 7 == 0 else LAND[4 + k]
    elif kind == 2:
        c = VERM[3 + k]
    elif kind == 3:
        c = GOLD[5 + k] if (xx + yy) % 5 == 0 else GOLD[4 + k]
    elif kind == 4:
        c = SLATE[4 + k]
    else:
        c = PARCH[4 + k] if (xx - yy) % 4 == 0 else PARCH[6 + k]
    return step(c, lift)


def scale_cell(q: Pix, ox, oy, night):
    """The 11 by 15 cell a counter's numeral is engraved in: a box of the chart's graduated scale, its border inked,
    its top and foot graduated with ticks, dark and light degrees down its sides, and the parchment between."""
    face = PARCH[6] if not night else NIGHT[4]
    line = INK[1] if not night else GOLD[2]
    tick = INK[4] if not night else GOLD[1]
    for yy in range(15):
        for xx in range(11):
            if xx in (0, 10) or yy in (0, 14):
                c = line
            elif xx in (1, 9):
                c = (INK[2] if not night else GOLD[3]) if (yy // 3) % 2 == 0 else face
            elif yy in (1, 13) and xx % 2 == 0:
                c = tick
            else:
                c = face
            q.px(ox + xx, oy + yy, c)


# --------------------------------------------------------------------------- the elements: the voyage
def voyage_line(p: Pix, x0, x1, y, night):
    """The time line as a voyage up to today: a band of sea washed in verdigris with its ripples, and the ship's
    dotted route along it."""
    sea, ripple = (C["sea"], X["wave"]) if not night else (C["sea_night"], DEEP[5])
    dot = INK[2] if not night else GOLD[3]
    for xx in range(x0, x1):
        for yy in range(y - 1, y + 3):
            p.px(xx, yy, sea)
        if (xx - x0) % 9 in (2, 3) and xx < x1 - 2:
            p.px(xx, y + 2 if (xx - x0) % 9 == 2 else y + 1, ripple)
        if (xx - x0) % 3 == 0:
            p.px(xx, y, dot)
    _mark(p, {(xx, yy) for xx in range(x0, x1) for yy in range(y - 1, y + 3)})
    a, b, _ = getattr(p, "voyage_at", (0, 0, 0))
    if x1 - x0 > b - a:
        p.voyage_at = (x0, x1, y)       # the longest of the sheet's voyages, the time line itself


def voyage_isles(p: Pix, night: bool) -> list:
    """Islands along a time line's voyage (see `voyage_line`), drawn as land on the chart the way the portolan
    makers drew them on the bare parchment of their sea: up to three on a wide sheet and one on a narrower, each
    where the labels, the anchors and the route leave it room within thirty rows of the route, spread along it,
    as near it as they fit, ochre, vermilion and gilt by turns. Returns their middles."""
    x0, x1, y = p.voyage_at
    placed = []
    for i, size in enumerate(((10, 5), (9, 4), (8, 4))[:3 if p.w > 300 else 1]):
        free = _spoken(p, margin=3, top=BAND, rule=p.h - BAND)
        seed = 13 * i + 5
        ex0, ey0, ex1, ey1 = _isle_extent(*size, seed)
        best, score = None, None
        for cy in range(y - 32, y + 33):
            for cx in range(x0 + 8, x1 - 8, 2):
                if not free((cx + ex0 - 3, cy + ey0 - 3, cx + ex1 + 4, cy + ey1 + 4)):
                    continue
                apart = min([abs(cx - a) for a, _ in placed] or [200])
                if apart < 50:
                    continue
                sc = min(apart, 160) * 0.5 - abs(cy - y)
                if score is None or sc > score:
                    best, score = (cx, cy), sc
        if best:
            isle(p, *best, *size, night, seed=seed, wash=("land", "verm", "gold")[i])
            placed.append(best)
    return placed


# An anchor for a release, 7 by 8: its ring, its stock, its shank and its arms curving up to their flukes.
ANCHOR = ["..kak..", "..k.k..", "kkkakkk", "...a...", "...a...", "k..a..k", "ka.a.ak", ".kaaak."]
ANCHOR_BIG = ["...kak...", "...k.k...", ".kkkakkk.", "....a....", "....a....", "....a....", "k...a...k",
              "ka..a..ak", ".ka.a.ak.", "..kaaak.."]


def anchor(p: Pix, x, gy, kind, night, L="base"):
    """A release on the voyage at x, the route's row gy: an anchor let go from it, gilt for a big release, of iron
    for a release, a small buoy for a patch, a dotted outline for one still to come, and a harbour tower for the
    repository's founding."""
    k = -1 if night else 0
    if kind == "made":
        tower(p, x - 2, gy + 1, 5, 9, night, roof="cone")
        return
    if kind == "minor":
        for (dx, dy, c) in ((0, 3, K), (-1, 4, VERM[4 + k]), (0, 4, VERM[3 + k]), (1, 4, VERM[2 + k]),
                            (0, 5, PARCH[6] if not night else NIGHT[6]), (0, 6, K)):
            p.px(x + dx, gy + dy, c, L)
        return
    art = ANCHOR_BIG if kind == "big" else ANCHOR
    metal = (GOLD[5 + k], GOLD[2 + k]) if kind == "big" else (SLATE[5 + k], SLATE[2 + k])
    pal = {"k": K, "a": metal[0]}
    if kind == "next":
        pal = {"k": INK[5] if not night else GOLD[1], "a": INK[5] if not night else GOLD[1]}
    w = len(art[0])
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch == "." or (kind == "next" and (i + j) % 2):
                continue
            c = pal[ch]
            if ch == "a" and kind != "next" and i > w // 2:
                c = metal[1]
            p.px(x - w // 2 + i, gy + 2 + j, c, L)


def today_ship(p: Pix, x, y, night):
    """The cog at today's end of the voyage, sailing on."""
    cog(p, x - 7, y + 1, night, small=True)


# --------------------------------------------------------------------------- the elements: wind heads for the roster
# A contributor as a wind head, 17 by 16, facing right (and drawn facing left, blowing away from its name): curls
# of hair in its own colour (H, q its shade), two eyes
# screwed shut (e) under their brows (b), the near cheek blown round with its light (S) and its blush (c), the nose
# (n), the lips pursed round the wind (L, the mouth m) and the chin in shadow (f); inked round (k). The wind
# leaves the lips in three lines (AVATAR_WIND, across from the wind's far end).
AVATAR = [
    ".....kkkkkk......",
    "...kkHHqHHHkk....",
    "..kHqHHHqHHqHk...",
    ".kHHHqkkkkHHqHk..",
    ".kqHkkFFFFkkHHk..",
    "kHHkFFFFFFFFkqk..",
    "kHqkFbbFFFbbFk...",
    "kqHkFeeFFFFeeFk..",
    "kHkSSFFFFFFFnFk..",
    "kqkSSccFFFFnnFLk.",
    "kHkScccFFFFFFLmLk",
    ".kkFcccFFFFFFFLk.",
    "..kFFcFFFFFFFkk..",
    "..kfFFFFFFFFkk...",
    "...kkfFFFFfkk....",
    ".....kkkkkk......",
]
# The bot is the north wind, an old head with grey hair and a long beard (B, b its strands).
AVATAR_BOT = AVATAR[:11] + [
    ".kkBBBBBBBFFFFLk.",
    "..kBBBBBBBBBBkk..",
    "..kBBbBBbBBBk....",
    "...kBBBBBBBk.....",
    "....kkBBbBkk.....",
    "......kkkk.......",
]
AVATAR_WIND = ((2, 8), (3, 8), (4, 8), (1, 10), (2, 10), (3, 10), (4, 10), (2, 12), (3, 12), (4, 12))
HAIRS = ("gold", "verm", "ink", "land")


def wind_avatar(p: Pix, cx, cy, i, night, bot=False):
    """A contributor as a wind head blowing, about (cx, cy), facing left so its wind blows out into the margin and
    not at its name: its hair in its own colour by turns (gilt, vermilion, ink and ochre), its face on the hand's
    lightest skin as the wind heads' are (see `wind_pal`), its cheek blown round, its eyes screwed shut and three
    lines of wind from its pursed lips reaching eleven units left of cx; a bot is the north wind, old and grey and
    bearded."""
    k = -1 if night else 0
    ramp = RAMP[HAIRS[i % len(HAIRS)]] if not bot else SLATE
    hair = (INK[4], INK[2]) if ramp is INK else (ramp[5 + k], ramp[3 + k])
    pal = {"k": K, "H": hair[0], "q": hair[1], "F": SKIN[3], "f": SKIN[2], "S": SKIN[4 + k],
           "c": VERM[5 + k], "e": INK[1], "b": SLATE[4 + k] if bot else INK[3], "n": SKIN[2],
           "L": VERM[4 + k], "m": VERM[1], "B": SLATE[6 + k]}
    x0, y0 = cx - 12, cy - 8
    p.sprite(x0 + 5, y0, AVATAR_BOT if bot else AVATAR, pal, flip=True)
    col = INK[3] if not night else GOLD[3]
    for (dx, dy) in AVATAR_WIND:
        p.px(x0 + dx, y0 + dy, col)


# --------------------------------------------------------------------------- the elements: the seal and the placard
def wax_rose(p: Pix, cx, cy, r0, r1, night):
    """A compass rose pressed in red wax round the certificate's seal, from r0 out to r1: the wax pooled round
    the seal's face with a rough edge, and out of it the rose's sixteen points, the four winds longest, the four
    between them shorter and the eight between those shortest, each a sharp point lit down one side and shaded
    down the other, the whole edged in the darkest wax."""
    k = -1 if night else 0
    lit, body, shade, edge = VERM[5 + k], VERM[3 + k], VERM[2 + k], VERM[0]
    rnd = random.Random(7)
    lumps = [rnd.uniform(-0.5, 0.9) for _ in range(24)]
    pool_r = r0 + 2.4
    cells: dict = {}
    for y in range(math.floor(cy - r1) - 3, math.ceil(cy + r1) + 4):
        for x in range(math.floor(cx - r1) - 3, math.ceil(cx + r1) + 4):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            if r0 - 0.6 <= rho <= pool_r + lumps[int((math.degrees(math.atan2(dy, dx)) % 360) // 15)]:
                cells[(x, y)] = shade if dx * 0.6 + dy * 0.8 > rho * 0.55 else body
    base = r0 + 1.5
    for n in sorted(range(16), key=lambda n: (n % 4 == 0, n % 2 == 0)):
        tip = r1 + 1 if n % 4 == 0 else r1 - 2 if n % 2 == 0 else r1 - 4
        half = 4.2 if n % 4 == 0 else 3.4 if n % 2 == 0 else 2.5
        theta = math.radians(n * 22.5 - 90)
        for y in range(math.floor(cy - tip) - 1, math.ceil(cy + tip) + 2):
            for x in range(math.floor(cx - tip) - 1, math.ceil(cx + tip) + 2):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                rho = math.hypot(dx, dy)
                if not base - 1 <= rho <= tip:
                    continue
                d = (math.atan2(dy, dx) - theta + math.pi) % (2 * math.pi) - math.pi
                arc = d * rho
                if abs(arc) <= half * min(1.0, (tip - rho) / (tip - base)) + 0.35:
                    cells[(x, y)] = lit if arc < 0 else shade
    for q, c in outline(cells, edge).items():
        if math.hypot(q[0] + 0.5 - cx, q[1] + 0.5 - cy) > r0:
            p.px(q[0], q[1], c)
    for q, c in cells.items():
        p.px(q[0], q[1], c)


def fleur(p: Pix, x, y, night, L="base"):
    """A fleur-de-lis in gilt, 5 by 5, inked round, at the seal's foot."""
    k = -1 if night else 0
    cells = {(x + i, y + j): (GOLD[5 + k] if j < 2 else GOLD[3 + k]) for j, row in enumerate(FLEUR)
             for i, ch in enumerate(row) if ch == "#"}
    for q, c in outline(cells, K).items():
        p.px(q[0], q[1], c, L)
    for q, c in cells.items():
        p.px(q[0], q[1], c, L)


def ribbon(p: Pix, x, y, w, h, night):
    """The ribbon under the seal as a banderole: its face in vermilion, lit along its top, with its tails folded
    back and notched."""
    k = -1 if night else 0
    for side in (-1, 1):
        for i in range(1, 5):
            xx = x - i if side < 0 else x + w - 1 + i
            for yy in range(y + 1, y + h - 1):
                mid = y + h / 2 - 0.5
                if i >= 3 and abs(yy - mid) < (i - 2) * 1.0:
                    continue
                c = K if yy in (y + 1, y + h - 2) or i == 4 else (VERM[1 + k] if i == 1 else VERM[2 + k])
                p.px(xx, yy, c)
    p.rect(x, y, w, h, VERM[2])
    p.hline(x, x + w, y, K)
    p.hline(x, x + w, y + 1, VERM[4])
    p.hline(x, x + w, y + h - 1, K)


def cartouche(p: Pix, night: bool):
    """A placard as a cartouche over the whole card: a panel of parchment in the chart's ruled border along its top
    and foot, its two ends rolled like a scroll's down its sides, each roll shaded round as a cylinder with its curl
    showing at its top and its foot, and the shadow of the rolls on the parchment beside them."""
    w, h = p.w, p.h
    paper(p, night, uid="pl")
    frame(p, night, uid="plf")
    lit, face, shade, deep = (PARCH[6], PARCH[5], PARCH[3], PARCH[2]) if not night else \
        (NIGHT[6], NIGHT[5], NIGHT[3], NIGHT[1])
    edge = K if not night else GOLD[2]
    for x0 in (0, w - 7):
        for yy in range(2, h - 2):
            for i in range(7):
                c = edge if i in (0, 6) else lit if i == 2 else face if i in (1, 3) else shade if i == 4 else deep
                if i in (2, 3, 4) and (yy - 2) % 7 == 0:
                    c = deep if i != 2 else face
                p.px(x0 + i, yy, c)
        for (yy, dy) in ((0, 1), (h - 1, -1)):
            for i in range(1, 6):
                p.px(x0 + i, yy, edge)
            for i in range(7):
                p.px(x0 + i, yy + dy, edge if i in (0, 6) else lit if i < 3 else shade)
            for (i, j) in ((2, 2), (3, 2), (4, 2), (2, 3), (4, 3), (3, 4)):
                p.px(x0 + i, yy + dy * j, edge)
        sx = 7 if x0 == 0 else w - 8
        for yy in range(BAND, h - BAND):
            p.apx(sx, yy, X["shade_ink"], 0.22 if not night else 0.4, "base")
