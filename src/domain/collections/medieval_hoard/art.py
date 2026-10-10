# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hoard set's scenery and sprites, drawn on the shared pixel canvas.

The barrow's chamber every header is, walled in chalk laid dry in long courses, every block of its words on a
great dressed stone, the corbelled roof's flat stones along its top, lit cold by the snow at its mouth and warm by
the gold, and the chalk with its flints that footers and elements lie on, rimed with frost at its edges; the great
stones of its passage for a frame, standing stones down the sides and a lintel carved with spirals across the top,
icicles hanging from it; titles of gold cloisonne set with cut garnets; the dragon asleep, coiled round and over a
mountain of gold and drawn to whatever room it has, its smoke rising and its eye half opening, and its great head
drawn large for a section; the hoard itself (coins pouring to the floor, a sword driven in, an open chest, a
round shield, the helmet, drinking horns, goblets, the crown, cut gems, the golden standard of the poem, and the
great helm of the ship burial with its buckle and its shoulder clasps), a glint wandering over its gold; the
barrow's mouth between the great stones of a passage grave carved with spirals, the snow drifted in, the thief
near the door going away with the cup he took and his footprints going out; by night the barrow lit only by its
own lights, the dragon's amber eye and its ember breath laying its light far across the floor and the gold, the
standard's glow and the moon's cold shaft in at the mouth, with the moon and a few stars over the snow; the
footer's drift of coins with the dragon's tail curled round a cup; and the gold and garnet every element, link and
badge is made of. Everything is shaded from the one light in the upper left on the set's own ramps; the big quiet
things (the walls, the stones, the drifts of coins) are pattern tiles of whole pixels, so the files stay light
enough to carry the rest."""
from __future__ import annotations

import functools
import math
import random
import re

from ...holidays.pixel import FONTS, LX, LY, LZ, Pix, fold, num
from ..hand import MEDIEVAL
from .palette import C, NIGHT_SKY, RAMP, X, step

CHALK, SAND, FLINT, FROST = RAMP["chalk"], RAMP["sand"], RAMP["flint"], RAMP["frost"]
STONE, EARTH, GOLD, GARNET = RAMP["stone"], RAMP["earth"], RAMP["gold"], RAMP["garnet"]
DRAKE, WING, BONE, EMBER = RAMP["drake"], RAMP["wing"], RAMP["bone"], RAMP["ember"]
SMOKE, NIGHT, IRON, SILVER = RAMP["smoke"], RAMP["night"], RAMP["iron"], RAMP["silver"]
OAK, GLASS, AMBER, EMERALD = RAMP["oak"], RAMP["glass"], RAMP["amber"], RAMP["emerald"]
MOONLIT = RAMP["moon"]             # the hand's moon
K = DRAKE[0]                       # the outline every figure is drawn round with


# --------------------------------------------------------------------------- small helpers
def stamp(p: Pix, x, y, art, pal, L="base", below=None):
    """Pixel art from rows of characters with its top-left at (x, y), each looked up in `pal`; a character the
    palette lacks is left clear, and rows from `below` down are left out."""
    for j, row in enumerate(art):
        if below is not None and y + j >= below:
            break
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                p.px(x + i, y + j, c, L)


def keep(p: Pix, cells):
    """Remember cells a shape fills without setting them pixel by pixel, so a check that gathers what a scene
    draws finds them as it finds pixels set one by one."""
    if not hasattr(p, "filled"):
        p.filled = set()
    p.filled.update(cells)


def _blocks(rows: dict) -> str:
    """Path data filling the cells {y: [x, ...]} as blocks: each row's runs, a run that lies the same in the rows
    under it one block with them, every move after the first relative to the last block's corner."""
    blocks, last = [], {}
    for y in sorted(rows):
        xs = sorted(set(rows[y]))
        runs, start = [], xs[0]
        for a, b in zip(xs, xs[1:] + [None]):
            if b != a + 1:
                runs.append((start, a - start + 1))
                start = b
        now = {}
        for run in runs:
            block = last.get(run)
            if block is not None and block[1] + block[3] == y:
                block[3] += 1
            else:
                block = [run[0], y, run[1], 1]
                blocks.append(block)
            now[run] = block
        last = now
    out, at = [], None
    for x, y, w, h in sorted(blocks, key=lambda b: (b[1], b[0])):
        out.append((f"M{x} {y}" if at is None else f"m{x - at[0]} {y - at[1]}") + f"h{w}v{h}h-{w}z")
        at = (x, y)
    return "".join(out).replace(" -", "-")


def paths(cols: dict) -> str:
    """Paths for {colour or colour:alpha: {y: [x, ...]}}: each colour's cells as strokes along their rows, or as
    filled blocks where the rows repeat enough to make that shorter."""
    out = []
    for c, rows in sorted(cols.items()):
        if not rows:
            continue
        col, a = c.split(":") if ":" in c else (c, None)
        strokes, blocks = Pix._d(rows), _blocks(rows)
        if len(blocks) + 2 < len(strokes):
            out.append(f'<path fill="{col}"' + (f' fill-opacity="{a}"' if a else "") + f' d="{blocks}"/>')
        else:
            out.append(f'<path stroke="{col}"' + (f' stroke-opacity="{a}"' if a else "") + f' d="{strokes}"/>')
    return "".join(out)


def by_colour(cells: dict) -> dict:
    """{(x, y): colour} as {colour: {y: [x, ...]}}, for `paths`."""
    cols: dict = {}
    for (x, y), c in cells.items():
        cols.setdefault(c, {}).setdefault(y, []).append(x)
    return cols


def tile(p: Pix, pid: str, w: int, h: int, cells: dict, x=0, y=0) -> str:
    """A pattern `w` by `h` from the cells {(x, y): colour}, kept once a file under `pid`, its origin at (x, y). A
    tile its cells cover wholly is laid on a ground of its commonest colour, the other colours drawn over it, where
    that is the shorter to write."""
    if ("tile", pid) not in p.syms:
        at = (f' x="{x}"' if x else "") + (f' y="{y}"' if y else "")
        body = paths(by_colour(cells))
        if len(cells) == w * h:
            counts: dict = {}
            for c in cells.values():
                counts[c] = counts.get(c, 0) + 1
            ground = max(sorted(counts), key=counts.get)
            laid = f'<rect width="{w}" height="{h}" fill="{ground}"/>' + \
                paths(by_colour({xy: c for xy, c in cells.items() if c != ground}))
            body = min(body, laid, key=len)
        p.defs.append(f'<pattern id="{pid}"{at} width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
                      f'{body}</pattern>')
        p.syms[("tile", pid)] = pid
    return pid


def fill(p: Pix, pid: str, x, y, w, h, L="base"):
    """A block filled with the pattern `pid`."""
    if w > 0 and h > 0:
        p.shapes[L].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')
        keep(p, {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)})


# --------------------------------------------------------------------------- the barrow's wall
TILE_W, TILE_H = 192, 66          # the chalk's tile: it wraps both ways, so its flints run on without a seam
# The chalk's beds down the tile, top to bottom: (rows, kind); between them the flints lie in loose lines along
# the partings, as they lie in chalk.
BEDS = ((10, "chalk"), (1, "flint"), (21, "chalk"), (1, "flint"), (20, "chalk"), (1, "flint"), (12, "chalk"))


def _wave(x: int, i: int) -> float:
    """How far the parting under bed `i` rises or falls at column x: a gentle swell that wraps with the tile."""
    u = 2 * math.pi * x / TILE_W
    return 0.9 * math.sin(u + i * 1.3) + 0.45 * math.sin(3 * u + i * 2.1) + 0.3 * math.sin(5 * u + i * 0.7)


def _strata_cells(night: bool, lite: bool = False) -> dict:
    """The chalk's cells: its flints in loose lines along its partings, each nodule with a pale rind, and a speck
    of the chalk's own grain here and there. By day every tone is light enough that a word over it keeps its
    contrast, so the chalk reads as one even pale stone; by night the flints just show in the dark. Drawn
    lighter, the flints lose their rinds and the chalk its grain."""
    rnd = random.Random(41)
    flint, rind, speck = (CHALK[3], CHALK[6], CHALK[4]) if not night else (X["flint_n"], X["rim_n"], X["speck_n"])
    cells = {}
    y0 = 0
    for i, (rows, kind) in enumerate(BEDS):
        if kind == "flint":
            x = rnd.randrange(8)
            while x < TILE_W - 4:
                w, h = rnd.choice((3, 4, 5, 5, 6, 7)), rnd.choice((2, 2, 3))
                cy = y0 + _wave(x, i) - h // 2
                for dx in range(w):
                    for dy in range(h):
                        if dx in (0, w - 1) and dy in (0, h - 1) and (w < 5 or rnd.random() < 0.8):
                            continue
                        cells[((x + dx) % TILE_W, math.floor(cy + dy + 0.5) % TILE_H)] = flint
                for dx in range(1, w - 1) if not lite else ():
                    cells[((x + dx) % TILE_W, math.floor(cy - 0.5) % TILE_H)] = rind
                x += w + rnd.randrange(10, 34)
        y0 += rows
    for _ in range(0 if lite else 60):
        cells.setdefault((rnd.randrange(TILE_W), rnd.randrange(TILE_H)), speck)
    return cells


def strata(uid: str, night: bool, lite: bool = False) -> str:
    """The pattern tile of the barrow's chalk (see `_strata_cells`)."""
    cells = _strata_cells(night, lite)
    return (f'<pattern id="{uid}s" width="{TILE_W}" height="{TILE_H}" patternUnits="userSpaceOnUse">'
            f'{paths(by_colour(cells))}</pattern>')


def band_edges(h: int) -> list:
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p"):
    """The ground a drawing sits on: the barrow's inner wall of chalk with its flints, an even pale stone lit cold
    and blue-white by day from the snow at its mouth on the left; by night the same chalk in darkness, its flints
    just showing, warming a little toward the floor. A header builds its walling over it once its words are set
    (see `wall`), under the light from the mouth. The drawing keeps which sheet it is (`uid`) and whether it is
    night."""
    p.sheet, p.night = uid, night
    w, h = p.w, p.h
    if not night:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{CHALK[5]}"/>')
    else:
        edges = band_edges(h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                p.under.append(f'<rect y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    p.chalk = (strata(uid, night, lite=p.lite), f'<rect width="{w}" height="{h}" fill="url(#{uid}s)"/>')
    p.defs.append(p.chalk[0])
    p.under.append(p.chalk[1])
    p.walled_at = len(p.under)
    if not night:
        snowlight(p)


DRY_W = 128                               # the drystone walling's tile, a course after course of it
DRY_COURSES = (7, 5, 8, 6, 7, 5)          # the courses' depths down the tile


def _drystone_cells(night: bool, seed=14, lite=False) -> tuple:
    """The walling of the barrow's chamber as a tile: courses of long flat stones of chalk laid dry, each stone's
    top edge catching the light and a joint under it and after it, a stone here and there a shade paler and some
    settled a little at the middle, a nodule of flint in one now and then, the faces left to the tile's ground.
    Drawn lighter, every stone is the one shade and plain. Returns the cells, the tile's size and its ground."""
    rnd = random.Random(seed)
    face, alt, lit, joint = (CHALK[4], CHALK[5], CHALK[6], CHALK[3]) if not night else \
        (EARTH[1], EARTH[2], EARTH[3], NIGHT[0])
    flint, gleam = (FLINT[3], FLINT[5]) if not night else (X["flint_n"], X["rim_n"])
    cells = {}
    y = 0
    for depth in DRY_COURSES:
        x0, x = rnd.randrange(DRY_W), 0
        while x < DRY_W:
            w = min(DRY_W - x, rnd.choice((14, 18, 22, 26, 30, 36)))
            if DRY_W - x - w < 12:
                w = DRY_W - x
            pale, dip = rnd.random() < 0.15 and not lite, rnd.choice((0, 0, 1))
            for i in range(w):
                bottom = depth - 1 - (dip if 2 <= i < w - 2 else 0)
                for j in range(bottom + 1):
                    c = joint if j == bottom or i == w - 1 else lit if j == 0 and 0 < i < w - 2 else \
                        alt if pale else None
                    if c:
                        cells[((x0 + x + i) % DRY_W, y + j)] = c
            if rnd.random() < 0.3 and depth >= 6 and not lite:
                i, j = rnd.randrange(3, w - 6), rnd.randrange(2, depth - 3)
                for (di, dj), c in (((0, 0), gleam), ((1, 0), flint), ((2, 0), flint), ((1, 1), flint),
                                    ((2, 1), flint)):
                    cells[((x0 + x + i + di) % DRY_W, y + j + dj)] = c
            x += w
        y += depth
    return cells, (DRY_W, y), face


# The great flat stones of the roof along the top, under the lintel: (where each starts along it, its width, its
# depth). At each end of the roof two more courses step down the wall under it, each set out from the one under it,
# as a corbelled roof is built: (their width, their depth) from the top down.
CORBELS = ((0, 46, 8), (46, 31, 7), (77, 54, 8), (131, 38, 7), (169, 50, 8), (219, 35, 7), (254, 58, 8),
           (312, 41, 7), (353, 70, 8))
STEPS = ((34, 7), (18, 6))


def _stones(p: Pix, x0, y0, x1, y1, pad=4) -> set:
    """The cells of the great dressed stones a header's words are cut on, the orthostats of the chamber: the
    title's lines on one stone with the mark beside it, and every run of lines under it that follow one another
    closely on another, each stone `pad` rows clear of its words and a little more at its ends, the lowest
    standing on the floor at row y1 where no scene stands in the room under it, the walling between two stones
    that would leave only a sliver filled in with stone, and every stone's corners knocked off."""
    boxes = sorted((w for w in p.words if w[3] <= y1 + 2 and w[1] >= y0 - 4), key=lambda w: w[1])
    titles = [w for w in boxes if w[3] - w[1] >= 14]
    # the marks beside a title or beside SECTION A-A are cut on the stone of the words beside them
    for m in getattr(p, "marks", ()):
        boxes.append(m)
        if any(m[1] < t[3] and t[1] < m[3] for t in titles):
            titles.append(m)
    boxes.sort(key=lambda w: w[1])
    groups = []
    for title in (True, False):
        mine = []
        for (a, b, c, d) in (w for w in boxes if (w in titles) == title):
            if mine and b - mine[-1][3] < 13 and a < mine[-1][2] + 20 and c > mine[-1][0] - 20:
                A0, B0, C0, D0 = mine[-1]
                mine[-1] = (min(A0, a), B0, max(C0, c), max(D0, d))
            else:
                mine.append((a, b, c, d))
        groups += [(a, b, c, d, title) for (a, b, c, d) in mine]
    # the lowest stone stands on the floor, unless a scene stands in the room under it
    low = max((d for (a, b, c, d, title) in groups), default=y0)
    taken = set(p.layers["base"]) | set(getattr(p, "filled", ()))
    for (a, b, c, d, title) in groups:
        if d == low:
            under = [(x, y) for x in range(a, c) for y in range(d + pad, y1 - 8)]
            if under and sum(xy in taken for xy in under) > 0.12 * len(under):
                low = None
    calm = {(x, y) for (a, b, c, d, title) in groups for x in range(max(x0, a - pad - 3), min(x1, c + pad + 3))
            for y in range(max(y0, b - pad), y1 if d == low else min(y1, d + pad))}
    # a sliver of walling between two stones, across or down, is stone too
    for y in range(y0, y1):
        xs = sorted(x for x in range(x0, x1) if (x, y) in calm)
        for a, b in zip(xs, xs[1:]):
            if 1 < b - a <= 10:
                calm |= {(x, y) for x in range(a, b)}
    for x in range(x0, x1):
        ys = sorted(y for y in range(y0, y1) if (x, y) in calm)
        for a, b in zip(ys, ys[1:]):
            if 1 < b - a <= 6:
                calm |= {(x, y) for y in range(a, b)}
    corners = set()
    for (x, y) in calm:
        for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            if (x - dx, y) not in calm and (x, y - dy) not in calm and (x - dx, y - dy) not in calm:
                corners |= {(x, y), (x + dx, y), (x, y + dy)}
    return calm - corners


def _rows_of(cells: set) -> dict:
    """{(x, y), ...} as {y: [x, ...]}, for `_blocks`."""
    rows: dict = {}
    for (x, y) in cells:
        rows.setdefault(y, []).append(x)
    return rows


def wall(p: Pix, night: bool, x0, y0, x1, y1):
    """A header's chamber walling, laid once its words are set, over the room from (x0, y0) to (x1, y1) down to
    its floor: courses of drystone walling behind the scenes, every block of words cut on a great dressed stone
    set in it (see `_stones`), its face even, a joint round it, its arris lit along its top and its left and by
    day its foot in shade, where they keep two units from its words (a drawing made lighter keeps only the joint),
    so nothing but even stone lies behind a word; and along the top under the lintel the great flat
    stones of the corbelled roof, stepping down the wall at each end where the words leave them room, each lit
    along its top and casting its shadow on the wall under it. By day the walling is chalk, lit cold by the snow
    at the mouth (see `snowlight`) and warmed by the gold at the right (see `goldlight`); by night it is dark but
    where a light falls on it."""
    calm = _stones(p, x0, y0, x1, y1)
    if getattr(p, "chalk", None):
        # a header's walling and its dressed stones stand in place of the chalk's flints
        p.defs.remove(p.chalk[0])
        p.under.remove(p.chalk[1])
        p.walled_at -= 1
        p.chalk = None
    if night:
        # and the night's bands the walling hides wholly are left out
        for band in [u for u in p.under[:p.walled_at] if re.fullmatch(r'<rect y="\d+" width="\d+" height="\d+" '
                                                                      r'fill="#[0-9A-F]{6}"/>', u)]:
            top, high = (int(v) for v in re.findall(r'(?:y|height)="(\d+)"', band))
            if top + high <= y1:
                p.under.remove(band)
                p.walled_at -= 1
    cells, (tw, th), ground = _drystone_cells(night, lite=p.lite)
    pid = tile(p, f"ds{'n' if night else 'd'}", tw, th, cells, x=x0, y=y0)
    holes = _blocks(_rows_of(calm)) if calm else ""
    d = f"M{x0} {y0}h{x1 - x0}v{y1 - y0}h{x0 - x1}z" + holes
    walled = [f'<path fill="{ground}" fill-rule="evenodd" d="{d}"/>',
              f'<path fill="url(#{pid})" fill-rule="evenodd" d="{d}"/>']
    if night and holes:
        walled.append(f'<path fill="{EARTH[2]}" d="{holes}"/>')
    L = p.layer("wall", z=-19.5)
    # the roof: its great flat stones along the top, and the courses stepping down at each end
    slabs = [(x0 + a, y0, min(x1, x0 + a + w), y0 + dep) for (a, w, dep) in CORBELS if x0 + a < x1 - 6]
    for (w, dep) in STEPS:
        for (a, b) in ((x0, x0 + w), (x1 - w, x1)):
            yy = max(s[3] for s in slabs if s[0] < b and s[2] > a)
            if all(p.clear_of_words(x - 2, yy - 2, x + 3, yy + dep + 2) for x in range(a, b, 3)) and \
                    not any((x, y) in calm for x in range(a, b) for y in range(yy, yy + dep + 1)):
                slabs.append((a, yy, b, yy + dep))
    face, lit, joint, shade = (STONE[4], STONE[5], STONE[1], STONE[3]) if not night else \
        (STONE[2], STONE[3], STONE[0], STONE[1])
    walled.append(f'<path fill="{face}" d="' + "".join(f"M{a} {b}h{c - a}v{e - b}h{a - c}z"
                                                     for (a, b, c, e) in slabs) + '"/>')
    for (a, b, c, e) in slabs:
        p.hline(a, c - 1, b, lit, L)
        p.hline(a, c - 1, e - 2, shade, L)
        p.hline(a, c - 1, e - 1, joint, L)
        p.vline(c - 1, b, e - 1, joint, L)
    p.under[p.walled_at:p.walled_at] = walled
    # each dressed stone: a joint round it, its arris lit along its top and its left, its foot in shade
    edge, arris, foot = (STONE[4], CHALK[6], CHALK[4]) if not night else (NIGHT[0], EARTH[4], None)
    for (x, y) in calm:
        if not p.clear_of_words(x - 2, y - 2, x + 3, y + 3):
            continue
        if any((x + dx, y + dy) not in calm for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            if x0 < x < x1 - 1 and y0 < y < y1:
                p.px(x, y, edge, L)
        elif p.lite:
            continue
        elif (x - 2, y) not in calm or (x, y - 2) not in calm:
            p.px(x, y, arris, L)
        elif foot and ((x + 2, y) not in calm or (x, y + 2) not in calm):
            p.px(x, y, foot, L)
    p.stones = calm
    return calm


WARMTH = ((0.72, 0.04), (0.8, 0.07), (0.87, 0.11), (0.93, 0.16))


def goldlight(p: Pix):
    """By day the warmth of the gold on the wall about the hoard at the right: a wash in steps, strongest by the
    hoard and falling away toward the middle, so the chalk is coldest by the mouth (see `snowlight`) and warmest
    by the dragon."""
    w, h = p.w, p.h
    edges = [round(a * w) for a, _ in WARMTH] + [w]
    for (a, alpha), x0, x1 in zip(WARMTH, edges, edges[1:]):
        p.under.append(f'<rect x="{x0}" width="{x1 - x0}" height="{h}" fill="{GOLD[6]}" '
                       f'fill-opacity="{num(alpha)}"/>')


SNOWLIGHT = ((0.0, 0.3), (0.05, 0.23), (0.12, 0.17), (0.22, 0.12), (0.36, 0.07), (0.55, 0.035))


def snowlight(p: Pix):
    """By day the snowlight from the barrow's mouth on the wall: a cold blue wash in steps, strongest at the left
    where the mouth is and falling away across the sheet, so the chalk is coldest nearest the snow."""
    w, h = p.w, p.h
    edges = [round(a * w) for a, _ in SNOWLIGHT] + [round(0.8 * w)]
    for (a, alpha), x0, x1 in zip(SNOWLIGHT, edges, edges[1:]):
        p.under.append(f'<rect x="{x0}" width="{x1 - x0}" height="{h}" fill="{FROST[5]}" '
                       f'fill-opacity="{num(alpha)}"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: by day the chalk, by night the row's band."""
    if not night:
        return CHALK[5]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


# --------------------------------------------------------------------------- the great stones
SIDE = 5            # the standing stones' width down each side of a sheet
LINTEL = 6          # the lintel's depth over a sheet...
HEAD_LINTEL = 10    # ...and over a header, where the icicles hang from it
UPRIGHT = 46        # the rows a standing stone stands before the next one down the passage
# The lintel's carving over a header, seven rows of its face: spirals cut in pairs that wind into one another
# as the passage graves' builders cut them. '#' is the groove; its lower lip catches the light.
SPIRALS = [
    "..####........####..",
    ".#....#......#....#.",
    "#..##..#....#..##..#",
    "#.#..#.#....#.#..#.#",
    "#.#.#..#....#..#.#.#",
    "#..#..#......#..#..#",
    ".#...#........#...#.",
]
# Over any other sheet, three rows: a running zigzag.
ZIGZAG = [
    "#...#...",
    ".#.#.#.#",
    "..#...#.",
]


def _carved(art: list, night: bool, lit=True) -> dict:
    """A carving's cells on the stone's face: each groove dark, and the face under it (where it is not groove
    too) catching the light along the groove's lower lip."""
    k = -1 if night else 0
    groove, lip = STONE[1 + k], STONE[5 + k]
    out = {}
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch == "#":
                out[(i, j)] = groove
                if lit and (j + 1 >= len(art) or art[j + 1][i] != "#"):
                    out.setdefault((i, j + 1), lip)
    return out


def _stone_face(x, y, night: bool, seed=0) -> str:
    """The tone of a great stone's dressed face at (x, y): grey greywacke, a darker fleck and a fleck of quartz
    here and there."""
    k = -1 if night else 0
    v = (x * 7 + y * 13 + seed * 5) % 31
    if v == 0:
        return STONE[5 + k]
    return STONE[3 + k] if v in (5, 17) else STONE[4 + k]


def _motifs(cells) -> list:
    """The runs of columns the motifs of a tile take, (first, last): the columns holding any of `cells`, run
    together."""
    cols = sorted({x for x, _ in cells})
    runs = []
    for x in cols:
        if runs and x == runs[-1][1] + 1:
            runs[-1][1] = x
        else:
            runs.append([x, x])
    return [tuple(r) for r in runs]


def paused(spans, period: int, origin: int, end: int, clear: tuple) -> tuple:
    """Where a band of motifs, their columns `spans` in a tile repeating every `period` columns from column `origin`,
    pauses for the month's mark at the top centre: (a, b), the band drawn up to column a and again from column b,
    so that every motif it draws is whole and none lies in the columns `clear`, (from, to)."""
    lo, hi = clear
    a, b = origin, end
    for n in range((end - origin) // period + 2):
        for s, e in spans:
            s0, e0 = origin + n * period + s, origin + n * period + e
            if e0 < lo:
                a = max(a, e0 + 1)
            elif s0 >= hi:
                b = min(b, s0)
    return a, b


def _lintel(p: Pix, w: int, top: int, night: bool, uid: str, clear=None):
    """The lintel across the top of a sheet, `top` rows deep: a dark edge over a lit arris, its dressed face
    carved along its length (spirals over a header, a zigzag elsewhere), and its underside in shadow. Its face is
    a pattern tile, so it costs little however wide the sheet. Over a header its spirals pause for the month's
    mark, a plain panel of the face left over the columns `clear` and a whole spiral ending on either side."""
    k = -1 if night else 0
    art = SPIRALS if top >= HEAD_LINTEL else ZIGZAG
    tw = len(art[0])
    face = top - 3
    cells = {}
    for x in range(tw):
        for y in range(face):
            cells[(x, y)] = _stone_face(x, y, night, 3)
    pad = (face - len(art)) // 2
    carved = {(i, j + pad): c for (i, j), c in _carved(art, night, lit=art is SPIRALS).items() if 0 <= j + pad < face}
    cells.update(carved)
    pid = tile(p, f"{uid}l", tw, face, cells, x=SIDE + 2, y=2)
    p.hline(0, w, 0, STONE[0])
    p.hline(0, w, 1, STONE[6 + k])
    a, b = paused(_motifs(carved), tw, SIDE + 2, w, clear) if clear and art is SPIRALS else (w, w)
    fill(p, pid, 0, 2, a, face)
    if b > a:
        p.shapes["base"].append(f'<rect x="{a}" y="2" width="{b - a}" height="{face}" fill="{STONE[4 + k]}"/>')
        fill(p, pid, b, 2, w - b, face)
    p.hline(0, w, top - 1, STONE[1 + k])
    for x in range(SIDE, w - SIDE):
        p.apx(x, top, X["shade_ink"], 0.22, "base")


def _upright(night: bool, right: bool) -> dict:
    """A standing stone of the passage's wall, SIDE wide and UPRIGHT tall, as cells: its face dressed, its edge
    toward the sheet lit on the right-hand stone and shaded on the left, a small cup-and-ring carved on it, and a
    dark joint at its foot where the next stone stands."""
    k = -1 if night else 0
    cells = {}
    for y in range(UPRIGHT):
        for x in range(SIDE):
            c = _stone_face(x, y, night, 7 if right else 1)
            inner = 0 if right else SIDE - 1
            outer = SIDE - 1 if right else 0
            if x == outer:
                c = STONE[0]
            elif x == inner:
                c = STONE[5 + k] if right else STONE[1 + k]
            cells[(x, y)] = c
    # the joint: the foot rounded off and a dark gap
    for x in range(SIDE):
        cells[(x, UPRIGHT - 1)] = STONE[0]
    for x in (0, SIDE - 1):
        cells[(x, UPRIGHT - 2)] = STONE[0]
        cells[(x, 0)] = STONE[0]
    # a cup-and-ring mark in its middle
    ring = ["...", ".#.", "..."]
    cy = UPRIGHT // 2 - 1
    for (i, j), c in _carved(ring, night).items():
        cells[(1 + i, cy + j)] = c
    for (i, j) in ((1, cy - 2), (2, cy - 2), (3, cy - 2)):
        cells[(i, j)] = STONE[1 + k]
    for (i, j) in ((1, cy + 2), (2, cy + 2), (3, cy + 2)):
        cells[(i, j)] = STONE[5 + k]
    return cells


def frame(p: Pix, night: bool, header: bool = False, footer: bool = False, uid="fr", clear=None):
    """The sheet's border, the great stones of a passage grave: a standing stone down each side, one stone after
    another down a tall sheet, each with a cup-and-ring carved on it; and across the top a lintel resting on them,
    carved with running spirals over a header and a zigzag over any other sheet, its underside in shadow, the
    spirals pausing over the columns `clear` for the month's mark. Along the foot the threshold, which a footer
    leaves to its drift of coins (see `footing`). Frost rimes the stones' inner edges by day. Where the stones'
    width divides the sheet's, both sides stand the one stone, the right-hand one's own edges laid over it, dark
    outside and lit toward the sheet, so its light still falls from the upper left."""
    w, h = p.w, p.h
    top = HEAD_LINTEL if header else LINTEL
    shared = w % SIDE == 0
    for right in (False, True):
        own = right and not shared
        pid = tile(p, f"{uid}{'r' if own else 'l'}{'n' if night else 'd'}", SIDE, UPRIGHT,
                   _upright(night, own), x=w - SIDE if own else 0, y=top - 2)
        fill(p, pid, w - SIDE if right else 0, top, SIDE, h - top)
    if shared:
        k = -1 if night else 0
        p.vline(w - 1, top, h, STONE[0])
        for y in range(top, h):
            if (y - top + 2) % UPRIGHT not in (0, UPRIGHT - 2, UPRIGHT - 1):
                p.px(w - SIDE, y, STONE[5 + k])
    _lintel(p, w, top, night, uid, clear)
    if not footer:
        k = -1 if night else 0
        p.hline(0, w, h - 3, STONE[4 + k])
        p.hline(0, w, h - 2, STONE[2 + k])
        p.hline(0, w, h - 1, STONE[0])
    rime(p, night, top, footer)


def rime(p: Pix, night: bool, top: int, footer: bool = False):
    """Frost on the stones' inner edges by day: feathery crystals grown out from the standing stones, thickest
    near the mouth at the left, and a rime along the lintel's underside, laid as pattern tiles. By night only the
    left stone, in the moonlight from the mouth, shows a little."""
    w, h = p.w, p.h
    c1, c2 = (FROST[6], FROST[4]) if not night else (FROST[1], FROST[0])
    for side in ((0,) if night else (0, 1)):
        rnd = random.Random(17 + side)
        cells = {}
        for y in range(40):
            if rnd.random() < (0.45 if side == 0 else 0.25):
                n = rnd.choice((1, 1, 2, 2, 3))
                for i in range(n):
                    cells[(i if side == 0 else 2 - i, y)] = c1 if i < n - 1 else c2
                if n >= 2 and rnd.random() < 0.5:
                    cells[(1, (y + rnd.choice((1, 39))) % 40)] = c2
        x = SIDE if side == 0 else w - SIDE - 3
        pid = tile(p, f"rm{side}{'n' if night else 'd'}", 3, 40, cells, x=x, y=top + 1)
        fill(p, pid, x, top + 1, 3, max(0, h - 4 - top - 1))
# --------------------------------------------------------------------------- the icicles
ICE_FOOT = 22       # the lowest row an icicle reaches: two clear of the highest a title is ever set


def _icicle(L: int, root: int, night: bool) -> dict:
    """An icicle `L` rows long hanging from row 0, `root` (2 to 4) columns wide where it hangs, as cells: it
    narrows a column at a time to a single pixel at its tip, lit down its left, clear ice in its middle and its
    shadow down its right, its tip catching the light. By night it is dark ice with a pale edge."""
    lit, mid, body, dark, tip = (FROST[6], FROST[5], FROST[4], FROST[2], C["white"]) if not night else \
        (FROST[3], FROST[2], FROST[1], FROST[0], FROST[4])
    out = {}
    for j in range(L):
        f = j / max(1, L - 1)
        n = max(1, root - int(f * root * 0.999 + 0.25))
        x0 = (root - n + 1) // 2
        for i in range(n):
            if n == 1:
                c = body
            elif i == 0:
                c = lit
            elif i == n - 1:
                c = dark
            else:
                c = mid if i == 1 else body
            out[(x0 + i, j)] = c
    out[((root - 1 + 1) // 2, L - 1)] = tip
    return out


ICE_RUN = 138        # the run of the lintel a tile of icicles covers before it repeats


def _icicle_cells(w: int, top: int, foot: int, night: bool, seed=0, lite=False) -> tuple:
    """A run of icicles `w` columns long hanging from row `top` (as row 0): a crust of ice along the stone and from
    it icicles in clusters, each round a long one, none reaching past `foot`. Returns their cells and where
    each tip hangs."""
    rnd = random.Random(seed * 7 + w)
    crust, under = (FROST[5], FROST[3]) if not night else (FROST[2], FROST[0])
    cells = {(x, 0): crust if (x * 5 + seed) % 7 else under for x in range(w)}
    tips = []
    x = rnd.randrange(1, 4)
    while x < w - 4:
        most = max(3, foot - top - 1 - rnd.choice((0, 0, 2, 4)))
        lengths = sorted((rnd.randrange(2, 4), rnd.randrange(3, 5), most - rnd.randrange(0, 3)), reverse=True)
        order = [lengths[1], lengths[0], lengths[2]] if rnd.random() < 0.6 else [lengths[2], lengths[0]]
        cx = x
        for L in order:
            root = 4 if L >= 8 else 3 if L >= 4 else 2
            if cx + root > w:
                break
            if lite and L < 8:
                cx += root + 1
                continue
            for (i, j), c in _icicle(L, root, night).items():
                cells[(cx + i, 1 + j)] = c
            for i in range(root):
                cells[(cx + i, 0)] = crust
            tips.append((cx + root // 2, L))
            cx += root + rnd.choice((0, 1, 1))
        x = cx + rnd.randrange(4, 12)
    return cells, tips


def icicles(p: Pix, x0, x1, top: int, night: bool, seed=0, foot=None, clear=None):
    """The icicles along a lintel's underside from x0 to x1, hanging from row `top`: a crust of ice along the
    stone, and from it icicles in clusters, each cluster round a long one, every one ending by `foot` (ICE_FOOT
    under a header's lintel). Over a long run they are a pattern tile, so they cost little however wide the
    lintel. Where the columns `clear` are kept for the month's mark, the clusters pause, the run ending on either
    side of them with a whole cluster and the crust going on between. The drawing keeps where each tip hangs, so
    the last pass can let a drop gather and fall from one (see `drip`). Drawn lighter, each cluster keeps only its
    long icicle."""
    foot = foot or ICE_FOOT
    w = x1 - x0
    run = min(w, ICE_RUN)
    cells, tips = _icicle_cells(run, top, foot, night, seed, lite=p.lite)
    a, b = paused(_motifs([xy for xy in cells if xy[1] >= 1]), run, x0, x1, clear) if clear else (x1, x1)
    if w > run:
        pid = tile(p, f"ic{'n' if night else 'd'}{seed}", run, foot - top + 1, cells, x=x0, y=top)
        fill(p, pid, x0, top, a - x0, foot - top + 1)
        fill(p, pid, b, top, x1 - b, foot - top + 1)
        tips = [(x0 + n * run + tx, top + ty) for n in range(w // run + 1) for tx, ty in tips if n * run + tx < w]
    else:
        for (x, y), c in cells.items():
            if not a <= x0 + x < b:
                p.px(x0 + x, top + y, c)
        tips = [(x0 + tx, top + ty) for tx, ty in tips]
    crust, under = (FROST[5], FROST[3]) if not night else (FROST[2], FROST[0])
    for x in range(a, b):
        p.px(x, top, crust if (x - x0) % 7 else under)
    p.icicles = getattr(p, "icicles", []) + [(x, y) for x, y in tips if not a <= x < b]


DRIP = 4.8          # seconds a drop takes to gather and fall, round and round
DRIP_TIMES = ((0.0, 0.4), (0.4, 0.66), (0.66, 0.8), (0.8, 0.92))


def drip(p: Pix, night: bool):
    """In a wide moving header, a drop of meltwater that gathers on the tip of an icicle, swells, falls and is
    gone, coming round again: the icicle chosen nearest an end of the lintel whose fall runs clear of every word
    and every sprite under it. The still file keeps the drop just gathered on its tip."""
    tips = sorted(getattr(p, "icicles", ()), key=lambda t: (min(t[0], p.w - t[0]), -t[1]))
    base = p.layers["base"]
    lit, mid = (C["white"], FROST[4]) if not night else (FROST[4], FROST[2])
    for (x, y) in tips:
        fall = 14
        if all(p.clear_of_words(x - 2, yy - 2, x + 3, yy + 3) and (x, yy) not in base
               for yy in range(y + 1, y + fall + 2)):
            frames = [[(0, 1, mid)], [(0, 1, lit), (0, 2, mid)], [(0, 7, lit), (0, 8, mid)], [(0, 14, mid)]]
            for i, (cells, t) in enumerate(zip(frames, DRIP_TIMES)):
                L = p.seq(f"dr{i}", *t, DRIP, keep=i == 0, z=1)
                for dx, dy, c in cells:
                    p.px(x + dx, y + dy, c, L)
            return (x, y)
    return None


# --------------------------------------------------------------------------- the title: gold cloisonne
def cell_fill(r, c, scale, night):
    """Gold cloisonne set with garnets: the letter cut into cells two font pixels long by gold walls a pixel
    thick, so its strokes read as slabs of garnet laid in gold, as the ship burial's jewellers set them; the
    garnet lit along the letter's top and falling to its deep red at its foot, the gold foil behind it glinting
    through here and there. By night the garnets glow with the gold behind them."""
    k = 1 if night else 0
    cell = 2 * scale
    if c % cell == cell - 1:
        return GOLD[3 + k]
    if r % cell == cell - 1:
        return GOLD[4 + k]
    band = min(6, r // scale)
    if (r * 3 + c * 5) % 13 == 0 and 0 < band < 6:
        return GARNET[4 + k]
    return GARNET[(4, 3, 3, 3, 2, 2, 2)[band] + k]


_CELL_PAINTS = {}


def _cell_paint(scale: int):
    from ...holidays.pixel import Paint
    if scale not in _CELL_PAINTS:
        _CELL_PAINTS[scale] = Paint(f"cl{scale}", cell_fill, period=2 * scale)
    return _CELL_PAINTS[scale]


AFTER = ((1, 0), (0, 1), (1, 1))      # where the gold rim lies past a letter's right and its foot, in shade
BEFORE = ((-1, 0), (0, -1))           # and past its left and its top, lit


def _shifted(tid: str, offsets) -> str:
    return "".join(f'<use href="#{tid}"' + (f' x="{dx}"' if dx else "") + (f' y="{dy}"' if dy else "") + "/>"
                   for dx, dy in offsets)


def cloisonne_title(p: Pix, x, y, s, night: bool, scale: int, motion: bool = False) -> int:
    """A title in letters of gold cloisonne set with cut garnets, after the ship burial's treasure: each letter
    a slab of garnet cut into cells by gold walls (see `cell_fill`), a rim of gold round it, lit along its
    left and top and dark along its right and foot where it stands proud of the wall, and by day its shadow on
    the chalk. In a wide moving header a glint crosses the letters now and then. The line's letters are kept
    once as a group the drawing places as often as it needs them, so a long title costs little more than its
    letters. Returns the width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    cx = x
    placed = []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    if not placed:
        return max(0, w)
    tid = f"tt{len(p.defs)}"
    letters = []
    for ch, gx in placed:
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        letters.append(f'<use href="#{p.syms[key]}"' + (f' x="{num((gx - x) / scale)}"' if gx > x else "") + "/>")
    p.defs.append(f'<g id="{tid}" transform="translate({x} {y}) scale({scale})">{"".join(letters)}</g>')
    k = 1 if night else 0
    body = []
    if not night:
        off = max(1, scale // 2) + 1
        body.append(f'<use href="#{tid}" x="{off}" y="{off}" stroke="{X["shade_ink"]}" opacity=".22"/>')
    body.append(f'<g stroke="{GOLD[5 + k]}">{_shifted(tid, BEFORE)}</g>')
    body.append(f'<g stroke="{GOLD[1 + k]}">{_shifted(tid, AFTER)}</g>')
    pat = p._pattern(_cell_paint(scale), scale, night)
    body.append(f'<use href="#{tid}" stroke="url(#{pat})"/>')
    markup = "".join(body)
    p.raw(0.1, markup, markup)
    rows = max(len(glyphs[ch][1]) for ch, _ in placed)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    if motion and scale >= 2:
        glint(p, x, y, scale, w, tid, night)
    return w


def glint(p: Pix, x, y, scale, w, tid, night):
    """The glint that crosses a gold title: its letters again (the line's group `tid`) in the gold's palest
    light, seen only through a narrow slanting window that sweeps across the line, rests, and comes round on the
    hand's period, whatever the title's length."""
    h = 7 * scale
    band = 2 * scale
    cid = f"gl{len(p.raws)}"
    a, b = x - band - h, x + w + band
    poly = f"0 {y + h + 1} {band} {y + h + 1} {band + h} {y - 1} {h} {y - 1}"
    dur = num(MEDIEVAL.glint)
    moving = (f'<clipPath id="{cid}"><polygon points="{poly}"><animateTransform attributeName="transform" '
              f'type="translate" values="{a} 0;{b} 0;{b} 0" keyTimes="0;.4;1" dur="{dur}s" '
              f'repeatCount="indefinite"/></polygon></clipPath><g clip-path="url(#{cid})" stroke="{X["glint"]}" '
              f'stroke-opacity=".75"><use href="#{tid}"/></g>')
    p.raw(0.4, moving, "")


# --------------------------------------------------------------------------- light by night
def lamp(p: Pix, cx, cy, r, col, own=(), phase=0, only=None):
    """Register a light at (cx, cy): once everything is drawn, `lights` lays its warmth into the gold, the
    scales, the bone and the stone within `r` of it, or only into the colours `only`. `own` are the light's own
    pixels, which it leaves alone."""
    p.lamps.append((cx, cy, r, col, set(own), phase, only))


def flick(p: Pix, phase: int, back: bool = False) -> str:
    """The flickering layer a glow of `phase` burns on; a drawing made lighter lets every glow keep one time."""
    return p.flicker(0 if p.lite else phase, back=back)


def halo(p: Pix, cx, cy, rx, ry, col, alphas, L="haze", shape=None):
    """A stepped glow (see `Pix.halo`). A drawing made lighter keeps its light but leaves out the faint outer
    ring, the glow drawn to its inner rings' reach."""
    if p.lite and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, L=L, shape=shape)


# What a light falls on: the gold, the garnets, the dragon's scales and bone, the stones and the earth.
LIT = set(GOLD) | set(GARNET) | set(DRAKE) | set(WING) | set(BONE) | set(STONE) | set(EARTH) | set(IRON) \
    | set(SILVER) | set(SMOKE)


def lights(p: Pix):
    """By night each light laid into the colours of what stands near it: within its reach what it falls on is a
    tone lighter on its own ramp, and in the near half of it two tones, so the dragon's scales nearest its
    breath come up out of the dark and the bone and the gold catch it. A light's own pixels are left as they
    are. Drawn lighter, each light keeps its near half."""
    base = p.layers["base"]
    for (cx, cy, r, col, own, phase, only) in p.lamps:
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y))
                if c is None or (x, y) in own or c not in (only or LIT):
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15) / r
                if d >= (0.5 if p.lite else 1):
                    continue
                base[(x, y)] = step(c, 2 if d < 0.5 else 1)
    p.lamps = []


# --------------------------------------------------------------------------- the dragon
# The dragon's head in profile, facing left, drawn from planes in its own units: its nose at x 0 and its nape at
# x 100, the top of its brow at y 0, so it draws at any size from a phone's to a section's. HEAD is its outline,
# jaw and all, and MOUTH the line of its lips with its jaw under it; BROW the heavy ridge over its eye; CHEEK the
# ridge of its cheek bone; its horns swept back, the near one and the far one behind it; the spikes at the back of
# its cheek and its jaw.
HEAD = ((0, 27), (0, 21), (2, 17), (5, 14), (9, 13), (13, 15), (22, 14), (32, 11), (38, 7), (42, 2), (47, -2),
        (54, -2), (61, 0), (66, 4), (78, 5), (90, 10), (100, 18), (101, 31), (97, 42), (88, 48), (74, 48), (58, 45),
        (40, 40), (22, 37), (9, 35), (2, 32))
MOUTH = ((0, 27.5), (20, 28), (40, 29.5), (56, 31.5), (70, 33), (78, 31.5))
BROW = ((36, 9), (41, 3), (47, -2), (54, -2), (61, 0), (66, 4), (64, 10), (56, 12), (46, 12))
CHEEK = ((58, 23), (74, 21), (88, 22), (100, 27))
HORN_NEAR = ((60, 4), (68, -1), (84, -8), (104, -13), (122, -13), (104, -7), (86, 2), (74, 8))
HORN_FAR = ((74, 3), (84, -2), (100, -7), (120, -6), (102, -1), (88, 5), (80, 7))
SPIKES = (((94, 26), (114, 28), (98, 33)), ((88, 40), (108, 47), (90, 46)), ((90, 11), (108, 10), (98, 17)))
LIDS = (46, 16, 58, 15)     # the corners of its eye under the brow
NOSTRIL = (5, 18)
FANGS = (9, 21)             # where its fangs hang over its lip
NAPE = (93, 26)             # where its neck leaves its head
JAW_FOOT = 48               # the lowest row of its jaw
RESTING = 10                # the rows over the floor its jaw rests at on its forelegs


def _inside(poly, x, y) -> bool:
    """Whether the point (x, y) lies inside the polygon `poly`."""
    hit, j = False, len(poly) - 1
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def _along(line, x) -> float:
    """The row of the polyline `line` at x, held level past its ends."""
    if x <= line[0][0]:
        return line[0][1]
    for (x0, y0), (x1, y1) in zip(line, line[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return line[-1][1]


@functools.lru_cache(maxsize=48)
def _head(L: int, night: bool, eye: int = 0) -> tuple:
    """The dragon's head `L` long as ((x, y), colour) pairs, its nose at x 0 and the top of its brow at y 0: the
    lit top of its snout, its brow lit over the shadow it casts on its eye, its cheek bone, the darker side of its
    jaw with the ivory plates under its chin, its horns and spikes of ivory lit along their tops, its outline and
    the line of its mouth dark, its nostril, its fangs; drawn large, the rows of its scales catching the light and
    its teeth along its lip. `eye` 0 is its
    eye shut, 1 half open on a slit of gold and 2 open on its black pupil, the gold an ember by night."""
    k = -1 if night else 0
    f = L / 100
    region = {}
    for py in range(math.floor(-16 * f) - 2, math.ceil(52 * f) + 2):
        for px in range(-1, math.ceil(125 * f) + 2):
            x, y = (px + 0.5) / f, (py + 0.5) / f
            r = "far" if _inside(HORN_FAR, x, y) else None
            if any(_inside(sp, x, y) for sp in SPIKES):
                r = "spike"
            if _inside(HEAD, x, y):
                r = "jaw" if y > _along(MOUTH, x) else "brow" if _inside(BROW, x, y) else "upper"
            if _inside(HORN_NEAR, x, y):
                r = "near"
            if r:
                region[(px, py)] = r
    head = {"upper", "brow", "jaw"}
    top = {}
    for (px, py), r in region.items():
        if r in head:
            top[px] = min(top.get(px, py), py)
    out = {}
    for (px, py), r in region.items():
        x, y = (px + 0.5) / f, (py + 0.5) / f
        above, below = region.get((px, py - 1)), region.get((px, py + 1))
        if r in ("far", "near", "spike"):
            t = 6 if above != r else 2 if below != r else 4 if r == "near" else 3
            c = BONE[max(1, t + k)]
        elif r == "jaw":
            c = DRAKE[max(1, (3 if y - _along(MOUTH, x) < 5 else 2) + k)]
            if below not in head and x < 84:
                c = BONE[(3 if px % 3 else 2) + k]
        elif r == "brow":
            t = 6 if above not in head else 1 if below == "upper" else 5
            c = DRAKE[max(1, t + k)]
        else:
            d = py - top.get(px, py)
            if x < 40:
                t = 6 if d == 0 else 5 if d / f < 5 else 4 if y < 24 else 3
            else:
                t = 6 if d == 0 else 4 if y < 22 else 3
                ridge = _along(CHEEK, x)
                if x > 62 and abs(y - ridge) < 1 / f:
                    t = 5
                elif x > 62 and y > ridge:
                    t = 3 if y < ridge + 6 else 2
            if f >= 0.48 and 3 <= t <= 4 and py % 3 == 0 and (px + (py // 3) * 2) % 5 == 0:
                t += 1
            c = DRAKE[max(1, t + k)]
        out[(px, py)] = c
    for (px, py), r in region.items():
        if any((px + dx, py + dy) not in region for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[(px, py)] = K
        elif r == "jaw" and region.get((px, py - 1)) in ("upper", "brow"):
            out[(px, py)] = K
        elif r in head and "near" in (region.get((px, py - 1)), region.get((px + 1, py))):
            out[(px, py)] = K
    gold, hot, rim = (GOLD[5], GOLD[6], GOLD[4]) if not night else (AMBER[5], AMBER[6], AMBER[4])
    ex0, ey0, ex1, ey1 = (v * f for v in LIDS)
    n = max(3, round(ex1 - ex0))
    for i in range(n):
        x, y = round(ex0) + i, round(ey0 + (ey1 - ey0) * i / (n - 1))
        inner = 0 < i < n - 1
        if not eye:
            out[(x, y + (1 if 0 < i < n - 1 and n > 3 else 0))] = K
            if inner:
                out[(x, y)] = DRAKE[5 + k] if n > 3 else K
            continue
        out[(x, y)] = gold if inner else K
        out[(x, y + 1)] = K
        if eye == 2:
            out[(x, y - 1)] = rim if inner else K
            if inner and f >= 0.6:
                out[(x, y - 2)] = K
    if eye:
        mx, my = round(ex0) + n // 2, round(ey0)
        out[(mx, my)] = K
        if eye == 2:
            out[(mx, my - 1)] = K
            out[(round(ex0) + 1, my - 1)] = hot
    nx, ny = round(NOSTRIL[0] * f), round(NOSTRIL[1] * f)
    out[(nx, ny)] = K
    if f > 0.5:
        out[(nx + 1, ny)] = K
    for fx in FANGS:
        x, y0 = round(fx * f), round(_along(MOUTH, fx) * f)
        for dy in range(max(2, round(4 * f))):
            out[(x, y0 + dy)] = BONE[(6 if dy < max(1, round(2 * f)) else 4) + k]
    if f >= 0.45:
        for tx in range(15, 62, 6):
            x, y0 = round(tx * f), round(_along(MOUTH, tx) * f)
            out[(x, y0)] = BONE[5 + k]
            if f >= 0.6:
                out[(x, y0 + 1)] = BONE[3 + k]
    return tuple(out.items())


def drake_pal(night: bool) -> dict:
    """The colours of the dragon's pixel art (its tail tip in a footer): its scales on their ramp, its belly plates,
    horns, spines and claws in old ivory, the membranes of its wings, its teeth; by night all a step into the dark.
    K its outline; 1 to 6 its scales dark to light; a b c d its belly plates; h i j its horns and spines; u v w x y
    its membranes and D the bones in them; e its shut eye; n its nostril; t its teeth; o O its claws."""
    k = -1 if night else 0
    D, B, Wg = DRAKE, BONE, WING
    if night:
        scales = {"1": D[0], "2": D[1], "3": D[1], "4": D[2], "5": D[3], "6": D[4]}
    else:
        scales = {str(i): D[i] for i in range(1, 7)}
    return {"K": D[0], **scales,
            "a": B[1], "b": B[3 + k], "c": B[4 + k], "d": B[4 + k], "D": B[5 + k], "h": B[4 + k], "i": B[6 + k],
            "j": B[2 + k], "u": Wg[1], "v": Wg[2 + k], "w": Wg[3 + k], "x": Wg[4 + k], "y": Wg[5 + k],
            "e": D[1], "n": D[0], "t": B[6 + k], "o": B[5 + k], "O": B[3 + k]}


EYE_TIMES = ((0.62, 0.68), (0.68, 0.8), (0.8, 0.86))
EYE_LOOP = 7.5


def head(p: Pix, nx, hy, L: int, night: bool, motion: bool, frames="ey", times=EYE_TIMES, loop=EYE_LOOP,
         floor=None) -> dict:
    """The dragon's head `L` long with its nose at column nx and the top of its brow at row hy (see `_head`), asleep.
    In a moving header its eye half opens, opens on the room a moment and falls shut again, in three frames named
    from `frames`, by night glowing amber as it opens and lighting the scales about it (but in a drawing made
    lighter); its smoke rises from its nostril (see `smoke`) and by night its breath glows there and, where
    its head lies on the floor at row `floor`, pools across the floor (see `breath`). Returns where its nose, its
    eye and its nape are, and the row its jaw rests on."""
    shut = dict(_head(L, night))
    for (x, y), c in shut.items():
        p.px(nx + x, hy + y, c)
    f = L / 100
    if motion:
        ex, ey = nx + (LIDS[0] + LIDS[2]) / 2 * f, hy + (LIDS[1] + LIDS[3]) / 2 * f
        for i, (eye, t) in enumerate(zip((1, 2, 1), times)):
            Le = p.seq(f"{frames}{i}", *t, loop, keep=False, z=1)
            opened = dict(_head(L, night, eye))
            if night and eye == 2 and not p.lite:
                # by night its eye glows amber as it opens, lighting the scales about it
                r = max(4.0, 0.1 * L)
                for (x, y), c in shut.items():
                    d = math.hypot(nx + x + 0.5 - ex, (hy + y + 0.5 - ey) * 1.3)
                    if d < r and c in DRAKE[1:] and opened.get((x, y)) == c:
                        opened[(x, y)] = step(c, 1)
            for (x, y), c in opened.items():
                if shut.get((x, y)) != c:
                    p.px(nx + x, hy + y, c, Le)
    nose = (nx + round(NOSTRIL[0] * f), hy + round(NOSTRIL[1] * f))
    p.nose = nose
    if night:
        breath(p, *nose, floor=floor)
    smoke(p, nose[0], nose[1] - 1, night, motion)
    return {"nose": nose, "eye": (nx + round(LIDS[0] * f), hy + round(LIDS[1] * f)),
            "nape": (nx + NAPE[0] * f, hy + NAPE[1] * f), "jaw": hy + round(JAW_FOOT * f)}


SMOKE_LOOP = 4.8    # seconds the smoke takes to curl up from its nostril, round and round: one of its idles
# The ways its smoke may go from its nostril: rising and curling where the room over its snout is clear, else
# drifting out low along the floor before it.
SMOKE_RISE = ((0, 0), (0, -1), (1, -2), (1, -3), (0, -4), (-1, -5), (-1, -6), (0, -7), (1, -8), (2, -9), (2, -10),
        (1, -11), (0, -12), (0, -13), (1, -14), (2, -15))
SMOKE_DRIFT = ((0, 0), (-1, 0), (-2, -1), (-3, -1), (-4, -1), (-5, -2), (-6, -2), (-7, -1), (-8, -1), (-9, -2),
         (-10, -2), (-11, -3), (-12, -3), (-13, -2), (-14, -2), (-15, -3))


def smoke(p: Pix, x, y, night: bool, motion: bool):
    """The dragon's smoke from its nostril at (x, y) in a curling thread that thins as it goes, rising where the
    room over its snout is clear and drifting out low before it where the words above leave it none, as far as it
    keeps clear of every word; three frames round and round in a moving header, one curl of it in a still drawing.
    By night the smoke is lit from under by the ember of its breath."""
    tones = (SMOKE[5], SMOKE[4]) if not night else (EMBER[3], SMOKE[3])

    def clear(path):
        return path[:next((i for i, (dx, dy) in enumerate(path)
                           if not p.clear_of_words(x + dx - 3, y + dy - 2, x + dx + 4, y + dy + 3)), len(path))]
    path = clear(SMOKE_RISE)
    if len(path) < 10:
        path = max(path, clear(SMOKE_DRIFT), key=len)
    frames = 3
    for fr in range(frames if motion else 1):
        L = p.seq(f"sm{fr}", fr / frames, (fr + 1) / frames, SMOKE_LOOP, keep=fr == 0, z=2) if motion else \
            p.layer("sm", z=2)
        for i, (dx, dy) in enumerate(path):
            if (i + fr * 3) % 12 in (8, 9, 10, 11):
                continue
            if i > 10 and (i + fr) % 2:
                continue
            wob = 1 if (i + fr) % 6 == 3 else 0
            c = tones[min(1, i // 6)]
            p.px(x + dx + (wob if path[-1][1] < -12 else 0), y + dy - (wob if path[-1][1] >= -12 else 0), c, L)


def breath(p: Pix, nx, ny, floor=None):
    """By night the ember of the dragon's breath in its nostrils, glowing and flickering: its glow on the wall about
    its snout and a red light far up the wall over it, its light on its scales and the gold nearest it, and where it
    lies on the floor at row `floor`, the light pooling out a long way across the floor before it and catching the
    coins and the treasures along it."""
    hot = flick(p, 1)
    p.px(nx, ny, EMBER[6], hot)
    p.px(nx - 1, ny, EMBER[5], hot)
    p.px(nx, ny + 1, EMBER[4], hot)
    p.px(nx - 1, ny + 1, EMBER[3], hot)
    halo(p, nx + 4, ny + 2, 16, 11, EMBER[4], (0.08, 0.18), L=flick(p, 1, back=True), shape=True)
    pool(p, nx + 2, ny + 4, 62, 30, EMBER[3], (0.06, 0.14, 0.24))
    lamp(p, nx + 0.5, ny + 1, 18, EMBER[4], {(nx, ny), (nx - 1, ny), (nx, ny + 1), (nx - 1, ny + 1)}, phase=1)
    if floor is not None:
        pool(p, nx - 24, floor - 1, 130, 12, EMBER[3], (0.05, 0.11, 0.18))
        lamp(p, nx - 20, floor - 3, 48, EMBER[4], phase=1, only=set(GOLD))
        lamp(p, nx - 64, floor - 2, 40, EMBER[3], phase=1, only=set(GOLD))
    p.embers = getattr(p, "embers", []) + [(nx, ny)]


# --------------------------------------------------------------------------- its body
def _spline(ctrl: tuple, step: float = 0.4) -> list:
    """Points about `step` apart along a smooth curve through the points `ctrl`."""
    pts = (ctrl[0],) + tuple(ctrl) + (ctrl[-1],)
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1:i + 3]
        n = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * (2 * p1[a] + (p2[a] - p0[a]) * t
                                    + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t * t
                                    + (3 * p1[a] - p0[a] - 3 * p2[a] + p3[a]) * t ** 3) for a in (0, 1)))
    out.append(tuple(ctrl[-1]))
    return out


def _radius(spec: tuple, s: float, total: float) -> float:
    """How thick a body is `s` along its length of `total`: ("even", a, b) from a at its start to b at its end;
    ("tail", r, n) r over its last n and tapering to a point before them."""
    kind, a, b = spec
    if kind == "tail":
        start = max(1.0, total - b)
        return a if s >= start else max(0.6, a * (s / start) ** 0.55)
    return a + (b - a) * s / max(1.0, total)


@functools.lru_cache(maxsize=96)
def _body(ctrl: tuple, spec: tuple) -> tuple:
    """The cells a body covers along the curve through `ctrl`, as thick as `spec` (see `_radius`), as
    ((x, y), (o, s, r, nx, ny)) pairs: each cell's place across it (o, -1 to 1, + on the right of the way the
    curve runs), how far along it (s), its radius there and the normal there; and its length."""
    pts = _spline(ctrl)
    samples, total = [], 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0) or 1e-6
        samples.append((x0, y0, total, (x1 - x0) / seg, (y1 - y0) / seg))
        total += seg
    near = {}
    for (qx, qy, qs, tx, ty) in samples:
        r = _radius(spec, qs, total)
        for y in range(math.floor(qy - r), math.ceil(qy + r) + 1):
            for x in range(math.floor(qx - r), math.ceil(qx + r) + 1):
                d = (x + 0.5 - qx) ** 2 + (y + 0.5 - qy) ** 2
                if d <= r * r and d < near.get((x, y), (1e9,))[0]:
                    near[(x, y)] = (d, qx, qy, qs, tx, ty, r)
    cells = []
    for (x, y), (d, qx, qy, qs, tx, ty, r) in near.items():
        o = max(-1.0, min(1.0, ((x + 0.5 - qx) * -ty + (y + 0.5 - qy) * tx) / r))
        cells.append(((x, y), (o, qs, r, -ty, tx)))
    return tuple(cells), total


def scales(p: Pix, body: tuple, night: bool, belly=1, plates=0.0, dark=0, floor=None, right=None, shade=0.0,
           ceiling=None, L="base"):
    """A body (see `_body`) laid as the dragon's: lit from the upper left and rounding into shadow on its flank, the
    edges of its scales catching the light along its lit side; the plates of its belly along its side `belly` (+1
    the right of the way it runs) from `plates` along it on (None for none), old ivory banded by their seams, by
    night lit gold from the hoard under it; its outline dark. Drawn lighter, it keeps its light and its plates but
    not the edges of its scales nor the seams between the plates. `dark` steps it further into shadow, for a limb
    on the far side, and so does the first `shade` of its length, the part of it lying in the shadow of the rest;
    what lies on the floor at row `floor` is cut off flat along it, and what reaches past column `right` or over
    row `ceiling` is left out."""
    cells, total = body
    for (x, y), (o, s, r, nx, ny) in cells:
        k = (-1 if night else 0) - dark - (1 if s < shade else 0)
        if (floor is not None and y > floor) or (right is not None and x > right) or \
                (ceiling is not None and y < ceiling):
            continue
        if abs(o) > 1 - min(0.5, 1 / max(r, 1.0)) or y == floor:
            p.px(x, y, K, L)
            continue
        lam = max(0.0, nx * o * LX + ny * o * LY + math.sqrt(max(0.0, 1 - o * o)) * LZ)
        if plates is not None and s >= plates and o * belly > 0.38 and r >= 2.5:
            ramp = GOLD if night else BONE
            t = 2 if (s / 2.8) % 1 < 0.3 and not p.lite else 5 if lam > 0.62 else 4 if lam > 0.38 else 3
            c = ramp[max(1, t + k)]
        else:
            t = 0.4 + lam * 6.2
            if lam > 0.45 and t < 6 and not p.lite and (s / 4 + abs(o) * 0.6) % 1 < 0.2:
                t += 1
            c = DRAKE[max(1, min(6, int(t)) + k)]
        p.px(x, y, c, L)


def spines(p: Pix, ctrl: tuple, spec: tuple, night: bool, side=1, every=5.0, s0=0.0, s1=None, size=1.0,
           right=None, ceiling=None):
    """Spines along the ridge of a body: little blades of ivory raked back along the way it runs, lit along their
    leading edge, every `every` from s0 to s1 along it, on its side `side` (+1 the right of the way it runs), none
    of it past column `right` or over row `ceiling`."""
    k = -1 if night else 0
    pts = _spline(ctrl)
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
    s1 = total if s1 is None else s1
    s, nxt = 0.0, s0 + every / 2
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0) or 1e-6
        if s >= nxt and s <= s1:
            nxt = s + every
            tx, ty = (x1 - x0) / seg, (y1 - y0) / seg
            nx, ny = -ty * side, tx * side
            r = _radius(spec, s, total)
            h = max(2.0, min(4.0, r * 0.5 * size))
            for i in range(int(h * 2) + 1):
                t = i / (h * 2)
                for w in ((0.0, 0.8) if t < 0.5 else (0.0,)):
                    cx = x0 + nx * (r - 0.3 + h * t) + tx * (h * 0.7 * t - w)
                    cy = y0 + ny * (r - 0.3 + h * t) + ty * (h * 0.7 * t - w)
                    if (right is None or cx < right + 1) and (ceiling is None or cy >= ceiling):
                        p.px(math.floor(cx), math.floor(cy), BONE[(5 if w == 0 else 3) + k])
        s += seg


def _cells_in(poly) -> set:
    xs, ys = [q[0] for q in poly], [q[1] for q in poly]
    return {(x, y) for y in range(math.floor(min(ys)) - 1, math.ceil(max(ys)) + 2)
            for x in range(math.floor(min(xs)) - 1, math.ceil(max(xs)) + 2) if _inside(poly, x + 0.5, y + 0.5)}


def _line(a, b) -> list:
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    return [(round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n)) for i in range(n + 1)]


def wing(p: Pix, shoulder, wrist, tips, root, night: bool):
    """The dragon's wing folded on its back: its arm up from the shoulder to the wrist, a claw at the wrist, its
    fingers raked back from the wrist to their tips in bones of ivory, and the membrane between them hanging in
    scallops, lit toward the wrist and folded in a pleat under each bone, its trailing edge back to the body at
    `root`."""
    k = -1 if night else 0
    poly = [shoulder, wrist]
    for i, t in enumerate(tips):
        poly.append(t)
        if i + 1 < len(tips):
            mx, my = (t[0] + tips[i + 1][0]) / 2, (t[1] + tips[i + 1][1]) / 2
            poly.append((mx + (wrist[0] - mx) * 0.3, my + (wrist[1] - my) * 0.3))
    poly.append(root)
    cells = _cells_in(poly)
    span = max(math.hypot(t[0] - wrist[0], t[1] - wrist[1]) for t in tips)
    bones = [_line(wrist, t) for t in tips]
    on_bone = {c for b in bones for c in b}
    out = {}
    for (x, y) in cells:
        t = 5.0 - math.hypot(x + 0.5 - wrist[0], y + 0.5 - wrist[1]) / span * 3.2
        if (x, y - 1) in on_bone or (x - 1, y - 1) in on_bone:
            t -= 1.5
        out[(x, y)] = WING[max(1, min(6, int(t) + k))]
        if any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[(x, y)] = WING[0]
    for b in bones:
        for i, q in enumerate(b):
            out[q] = BONE[(6 if i < 3 else 5 if i < len(b) * 0.6 else 4) + k]
    for (x, y) in _line(shoulder, wrist):
        out[(x, y)], out[(x + 1, y)], out[(x + 2, y)] = K, DRAKE[5 + k], DRAKE[3 + k]
    wx, wy = round(wrist[0]), round(wrist[1])
    for dx, dy, c in ((0, -1, BONE[6 + k]), (-1, -2, BONE[5 + k]), (-2, -2, BONE[3 + k]), (1, -1, K), (-1, -1, K)):
        out[(wx + dx, wy + dy)] = c
    for (x, y), c in out.items():
        p.px(x, y, c)


def claws(p: Pix, x, y, night: bool, n=3, gap=2):
    """A hind foot's claws of ivory curled on the floor, its first at (x, y) and the rest behind it, `gap` apart."""
    k = -1 if night else 0
    for i in range(n):
        p.px(x + i * gap, y, BONE[5 + k])
        p.px(x + i * gap - 1, y + 1, BONE[3 + k])


# A forepaw laid on the floor, 7 by 6, its toes forward to the left with a claw of ivory curled from each: the end
# of a foreleg. K its outline; 5 4 3 its scales lit to dark; o O its claws.
PAW = [
    "...KKKK",
    "..K5554",
    ".K55444",
    "K554433",
    "oK4KoK3",
    ".O.O.OK",
]


def paw(p: Pix, x, y, night: bool, dark=0):
    """A forepaw with its toes' tips at column x and its claws on the floor at row y (see `PAW`); `dark` steps it
    into shadow, for the far one."""
    pal = drake_pal(night)
    for ch in "345":
        pal[ch] = DRAKE[max(1, int(ch) - dark + (-1 if night else 0))]
    stamp(p, x, y - len(PAW) + 1, PAW, pal)


# The dragon's coil in its room, as fractions across its column (u, 0 its left edge and 1 its right) and down it
# (v, 0 the top of the room and 1 the floor): the arch of its back from its flank over the hoard to its shoulders,
# coming down the room's right from its haunch and round under its hip to the floor; its neck from its shoulders
# bowed out to the left and down to its head; its wing folded on its back, the shoulder, the wrist, the tips of its
# fingers and where its trailing edge meets its back; its hind leg from its haunch to its foot.
ARCH = ((0.404, 0.966), (0.692, 0.905), (0.846, 0.784), (0.923, 0.595), (0.942, 0.405), (0.885, 0.23),
        (0.731, 0.108), (0.519, 0.068), (0.327, 0.122))
NECK = ((0.346, 0.108), (0.173, 0.27), (0.173, 0.459), (0.308, 0.608))
FOLD = ((0.385, 0.162), (0.538, -0.014), ((0.769, 0.0), (0.904, 0.068), (0.981, 0.176), (0.981, 0.311)),
        (0.846, 0.297))
HIND = ((0.846, 0.676), (0.942, 0.811), (0.904, 0.919), (0.788, 0.98))


def pool(p: Pix, cx, cy, rx, ry, col, alphas):
    """By night a pool of a light's colour round it on the wall and the floor, in steps, strongest at its heart:
    kept with the drawing until its header's walls are built and laid over them (see `light`)."""
    if not hasattr(p, "pools"):
        p.pools = []
    p.pools.append((cx, cy, rx, ry, col, alphas))


def shaft(p: Pix, rings: list, col, alphas):
    """By night a shaft of light lying across the floor, kept with the pools (see `pool`): `rings` are its
    outlines from the faintest to the brightest, each a list of points, laid one over another in the steps
    `alphas`."""
    if not hasattr(p, "pools"):
        p.pools = []
    p.pools.append((rings, col, alphas))


def light(p: Pix, x0, y0, x1, y1):
    """By night every pool and shaft of light a header's scenes keep, laid at last over its walls once they are
    built, in the room from (x0, y0) to its floor at row y1: the walling and the floor take all of it, and the
    dressed stones the words are cut on only a little from the words' lowest line up, so the light falls softly
    round the words and never strongly on one. Drawn lighter, a pool keeps its reach in fewer steps."""
    pools, p.pools = getattr(p, "pools", []), []
    if not pools:
        return
    mid = f"lm{len(p.defs)}"
    # the stones take only a little of the light from their words' lowest line up; under it, where no word is, all
    low = max((w[3] for w in p.words if w[3] <= y1), default=y0) + 2
    calm = {(x, y) for (x, y) in getattr(p, "stones", None) or () if y < low}
    stones = f'<path fill="{STONE[4]}" d="{_blocks(_rows_of(calm))}"/>' if calm else ""
    p.defs.append(f'<mask id="{mid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" '
                  f'fill="{C["white"]}"/>{stones}</mask>')
    body = []
    for glow in pools:
        if len(glow) == 3:
            rings, col, alphas = glow
            prev = 0.0
            for ring, a in zip(rings, alphas):
                pts = " ".join(f"{round(x)},{round(y)}" for x, y in ring)
                body.append(f'<polygon points="{pts}" fill="{col}" '
                            f'fill-opacity="{num(round(1 - (1 - a) / (1 - prev), 2))}"/>')
                prev = a
            continue
        cx, cy, rx, ry, col, alphas = glow
        alphas = alphas[1::2] if p.lite and len(alphas) > 2 else alphas
        prev, n = 0.0, len(alphas)
        for i, a in enumerate(alphas):
            f = (n - i) / n
            body.append(f'<ellipse cx="{round(cx)}" cy="{round(cy)}" rx="{round(rx * f)}" ry="{round(ry * f)}" '
                        f'fill="{col}" fill-opacity="{num(round(1 - (1 - a) / (1 - prev), 2))}"/>')
            prev = a
    group = f'<g mask="url(#{mid})">{"".join(body)}</g>'
    p.raw(-19, group, group)


def glitter(p: Pix, spots, night: bool, motion: bool, seed=0):
    """The hoard's glitter: points of light on its coins that catch and wink out in turn, three phases, more of
    them by night when the ember lights them; in a still drawing they shine steady."""
    rnd = random.Random(seed)
    base = p.layers["base"]
    for i, (x, y) in enumerate(spots):
        under = base.get((x, y))
        if under is not None and under not in GOLD:
            continue
        if rnd.random() < (0.5 if night else 0.3):
            L = p.twinkle(i) if motion else "base"
            p.px(x, y, GOLD[6] if not night else X["glint"], L)
            if rnd.random() < 0.35:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    p.px(x + dx, y + dy, GOLD[5], L)


# --------------------------------------------------------------------------- the hoard
COINS = [
    ".ZGGg.qGgg.z",
    "ZGGggqzGGgzq",
    "gggzq.ZGGg.z",
    "qzq.ZGGggqzg",
    ".ZGgqGggzq.Z",
    "GGggqzzq.ZGG",
    "zzq.ZGGg.zgg",
    "..ZGGggq.qzq",
]
COIN_TONE = {"Z": 6, "G": 5, "g": 4, ".": 2, "z": 2, "q": 1}


def _hill(u: float, peak: float) -> float:
    """The heap's rise at `u` (0 to 1 across it), its peak at `peak`: a rounded bell with long slopes."""
    d = (u - peak) / (peak if u < peak else 1 - peak)
    d = min(1.0, abs(d))
    return (0.5 + 0.5 * math.cos(math.pi * d)) ** 0.85


def heap(p: Pix, x0, x1, foot, height, night: bool, seed=0, peak=0.5, gems=True, L="base") -> dict:
    """A heap of gold coins from x0 to x1 standing on row `foot`, `height` rows at its peak: coins lying every way
    in overlapping rows, each lit along its upper rim, the far slope in shade and the foot of the heap in its own
    shadow; a coin standing on edge here and there along its crest, and garnets, blue glass and pearls spilt
    among the coins. By night the gold lies in the dark but where a light falls on it. Returns the heap's crest,
    {x: the row of its top}."""
    rnd = random.Random(seed)
    k = -2 if night else 0
    crest = {}
    for x in range(x0, x1):
        u = (x - x0 + 0.5) / max(1, x1 - x0)
        lump = (0.8 * math.sin(x * 1.7 + seed) + 0.6 * math.sin(x * 0.53 + seed * 2)) if height > 3 else 0
        top = round(foot - height * _hill(u, peak) - lump * min(1.0, height / 10))
        top = min(top, foot)
        crest[x] = top
        for y in range(top, foot + 1):
            ch = COINS[(y - foot) % len(COINS)][x % len(COINS[0])]
            t = COIN_TONE[ch]
            if u > peak + 0.12:
                t -= 1
            if foot - y < 2:
                t -= 1
            if y == top and t < 5:
                t += 1
            p.px(x, y, GOLD[max(0, min(6, t + k))], L)
    for x in range(x0 + 2, x1 - 2, 1):
        if rnd.random() < 0.12 and crest[x] < foot - 2:
            t = crest[x]
            for dy, c in enumerate((GOLD[6 + k], GOLD[4 + k], GOLD[2 + k])):
                p.px(x, t - 3 + dy, c, L)
    if gems:
        for _ in range(max(1, (x1 - x0) // 9)):
            x = rnd.randrange(x0 + 2, x1 - 2)
            if crest[x] >= foot - 1:
                continue
            y = rnd.randrange(crest[x] + 1, foot)
            gem(p, x, y, rnd.choice(("garnet", "garnet", "glass", "pearl", "amber")), night, L=L)
    return crest


def gem(p: Pix, x, y, kind: str, night: bool, L="base"):
    """A gem spilt among the coins: a cut garnet or a piece of blue glass, two pixels square with its table lit,
    a pearl, or a bead of amber."""
    k = -1 if night else 0
    if kind == "pearl":
        p.px(x, y, BONE[6 + k], L)
        p.px(x + 1, y, BONE[4 + k], L)
        return
    R = {"garnet": GARNET, "glass": GLASS, "amber": AMBER}[kind]
    p.px(x, y, R[5 + k], L)
    p.px(x + 1, y, R[3 + k], L)
    p.px(x, y + 1, R[3 + k], L)
    p.px(x + 1, y + 1, R[1 + k], L)


# --------------------------------------------------------------------------- the lair
def clear_art(p: Pix, art, x, y, margin=2) -> bool:
    """Whether every pixel of `art` set with its top-left at (x, y) keeps `margin` units from every word."""
    return all(p.clear_of_words(x + i - margin, y + j - margin, x + i + margin + 1, y + j + margin + 1)
               for j, row in enumerate(art) for i, ch in enumerate(row) if ch != ".")


def _q(v):
    """A pose's numbers rounded to hundredths, so the same pose drawn again finds its cells kept."""
    if isinstance(v, (tuple, list)):
        return tuple(_q(a) for a in v)
    return round(v, 2) if isinstance(v, float) else v


def room_top(p: Pix, x, top, g) -> int:
    """The highest row, never above `top`, from which column x is clear of every word down to the floor at row g,
    two units kept."""
    y = g
    while y - 1 >= top and p.clear_of_words(x - 2, y - 3, x + 3, y + 2):
        y -= 1
    return y


def head_room(p: Pix, nx, hy, L: int) -> bool:
    """Whether the dragon's head `L` long with its nose at column nx and the top of its brow at row hy keeps two
    units from every word."""
    cells = {q for q, _ in _head(L, False)}
    return all(p.clear_of_words(nx + x - 2, hy + y - 2, nx + x + 3, hy + y + 3) for (x, y) in cells
               if not {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} <= cells)


def lair(p: Pix, x0c, x1, top, g, night: bool, motion: bool, nx, L: int, tail_x) -> tuple:
    """The dragon asleep on its hoard at the right of a header, coiled round and over it in the room from column x0c
    to x1 and from row `top` to the floor at row g (see `ARCH`): a mountain of coins filling the coil under the arch
    of its back, heaped to the wall behind it and pouring down before it to the floor as far as the tail's tip,
    a sword driven into it and a drinking horn lying on it inside the coil, a coin slipping down it in a moving
    header; the dragon on it, its tail swept out along the floor to the left as far as column `tail_x`, round under
    its hip and up its flank, its back arched over the hoard with its spines along it and its wing folded on it, its
    hind leg drawn up, its neck bowed down from its shoulders to its head `L` long resting on its forelegs on the
    floor with its nose at column nx (see `head`); before it on the gold its treasures (see `set_out`) and gems in
    garnet, emerald and sapphire, and a glint wandering over the gold. By night its ember breath lights the gold and
    its light pools far across the floor, and the heap glows under it. Returns the span of the rule it covers."""
    W, H = x1 - x0c, g - top
    s = max(0.5, min(1.2, W / 52, H / 74))
    f = L / 100

    def at(u, v):
        return (x0c + u * W, top + v * H)
    hy = g - RESTING - round(JAW_FOOT * f)
    nape = (nx + NAPE[0] * f, hy + NAPE[1] * f)
    # the hoard: a mountain of coins filling the coil under the arch of its back, heaped against the wall behind it
    # and pouring down before it to the floor as far as the words leave it room
    px_, py_ = at(0.56, 0.22)
    foot = min(tail_x + 2, nx - 8)
    crest = {}
    for x in range(foot, x1 + 1):
        if x <= px_:
            rise = ((x - foot + 0.5) / max(1.0, px_ - foot)) ** 1.5
        else:
            rise = 1 - 0.25 * ((x - px_) / max(1.0, x1 - px_)) ** 2
        t = round(g - (g - py_) * rise - 0.8 * math.sin(x * 1.3) - 0.6 * math.sin(x * 0.45 + 1))
        crest[x] = min(g - 1, max(t, room_top(p, x, top, g) + 1))
    _coins(p, crest, g, night, far=round(px_) + 10, clear=True)
    if motion and not slide(p, crest, nx - 3, max(foot + 4, nx - 48), night):
        slide(p, crest, round(px_) - 1, round(at(0.3, 0)[0]), night)
    # a sword driven into the gold inside the coil, its garnet pommel standing out of it, a drinking horn lying on
    # the gold beside it and gems in garnet, emerald and sapphire
    shine = []
    sx = round(at(0.38, 0)[0])
    if sx + 3 in crest and crest[sx + 3] - 9 > top:
        treasure(p, sx, crest[sx + 3] - 9, SWORD, night, below=crest[sx + 3] + 1)
        shine.append((sx + 2, crest[sx + 3] - 9))
    hx = sx + 7
    if hx + len(HORN[0]) in crest:
        rest = max(crest[x] for x in range(hx, hx + len(HORN[0])))
        if rest - len(HORN) > top:
            treasure(p, hx, rest - len(HORN) + 2, HORN, night, below=rest + 1)
            shine.append((hx + 1, rest - len(HORN) + 3))
    rnd = random.Random(x0c + g)
    for kind in ("garnet", "emerald", "sapphire", "garnet"):
        x = rnd.randrange(round(at(0.3, 0)[0]), round(at(0.8, 0)[0]))
        if x + 4 in crest and crest[x] + 6 < g:
            jewel(p, x, max(crest[x], crest[x + 3]) + rnd.randrange(2, 6), kind, night)
    # its tail from its tip along the floor, round under its hip, up its flank and over the arch of its back
    arch = [at(u, v) for u, v in ARCH]
    run = arch[0][0] - tail_x
    tail = [(tail_x + run * i / max(1, round(run / 28)), g - 2.0) for i in range(max(1, round(run / 28)))]
    ctrl = _q(tuple(tail + arch))
    reach = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(arch[1:], arch[2:]))
    spec = _q(("tail", 7.0 * s, reach + 6 * s))
    body = _body(ctrl, spec)
    scales(p, body, night, belly=-1, plates=body[1] - reach - 8 * s, floor=g,
           shade=sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ctrl, ctrl[1:])
                     if b[0] <= nape[0] + 0.1 * L))
    spines(p, ctrl, spec, night, side=1, every=5 * s, s0=body[1] - reach * 0.62, size=s)
    sh, wr, tips, root = FOLD
    wing(p, at(*sh), at(*wr), [at(*t) for t in tips], at(*root), night)
    hind = _q(tuple(at(u, v) for u, v in HIND))
    scales(p, _body(hind, _q(("even", 6.5 * s, 3.5 * s))), night, plates=None, floor=g)
    claws(p, round(hind[-1][0]) - 5, g - 1, night)
    # its neck bowed down from its shoulders to its head, its forelegs under its chin
    neck = _q(tuple([at(u, v) for u, v in NECK] + [nape]))
    nspec = _q(("even", 6.6 * s, 5.2 * s))
    scales(p, _body(neck, nspec), night, belly=1)
    spines(p, neck, nspec, night, side=-1, every=5 * s, s1=_body(neck, nspec)[1] * 0.8, size=s)
    # the coins heaped about its feet under the arch
    front = {x: g - 2 - (1 if (x * 5) % 7 == 0 else 0) for x in range(round(nape[0]) + 2, x1 + 1)}
    _coins(p, front, g, night, seed=3)
    # before it on the gold where the words leave them room, its treasures (see `set_out`) and gems
    shine += set_out(p, crest, nx + 4, max(tail_x + 4, foot), g, night)
    for kind in ("emerald", "sapphire", "garnet"):
        x = rnd.randrange(foot + 2, max(foot + 3, nx - 4))
        y = max(crest[x], crest[x + 3]) + 1
        if y + 2 < g and clear_art(p, CABOCHON, x, y) and all(p.get(x + i, y + j) in (None,) + tuple(GOLD)
                                                               for i in range(4) for j in range(3)):
            jewel(p, x, y, kind, night)
    # its forelegs laid along the floor, its head resting on them, the far one behind it
    far = _q(((nape[0] + 0.02 * L, g - 10.0), (nape[0] - 0.3 * L, g - 7.4), (nx + 0.3 * L, g - 7.4)))
    scales(p, _body(far, _q(("even", 3.0 * s, 2.6 * s))), night, plates=None, dark=1, floor=g)
    paw(p, round(nx + 0.3 * L) - 6, g - 4, night, dark=1)
    head(p, nx, hy, L, night, motion, floor=g)
    near = _q(((nape[0] + 0.06 * L, g - 10.0), (nape[0] - 0.12 * L, g - 4.6), (nx + 0.16 * L, g - 4.4)))
    scales(p, _body(near, _q(("even", 3.4 * s, 3.0 * s))), night, plates=None, floor=g)
    paw(p, round(nx + 0.16 * L) - 6, g - 1, night)
    # the glint wandering over it, on the crest of the gold and the treasures
    base, k = p.layers["base"], -2 if night else 0
    spots = [(x, crest[x]) for x in range(foot + 2, x1 - 2, 2) if base.get((x, crest[x])) in (GOLD[5 + k], GOLD[4 + k])]
    spots = [(x, y) for (x, y) in spots + shine if p.clear_of_words(x - 3, y - 3, x + 4, y + 4)]
    wander(p, spots, night, motion, seed=x0c)
    if night:
        pool(p, px_, g - H * 0.3, W * 0.95, H * 0.55, GOLD[3], (0.06, 0.14))
    return (min(tail_x, foot) - 1, x1 + 1)


# The treasures set out on the gold before the dragon, the first that fit nearest it: (the art, how many rows of it
# lie sunk in the coins, whether it stands on the floor rather than lying on the gold).
SET_OUT = (("CUP", 2, False), ("CHEST", 1, True), ("SHIELD", 3, False), ("HELMET", 3, True), ("HORN", 2, False),
           ("GOBLET", 2, False), ("CROWN", 2, False))


def set_out(p: Pix, crest: dict, x1, x0, g, night: bool, pieces=SET_OUT) -> list:
    """The hoard's treasures on its gold (its crest, {x: row}) from column x1 back to x0, the nearest x1 their room
    allows, two units clear of every word and each beside the last: the chest and the helmet standing on the floor at
    row g, the others lying on the gold, high on it where the words leave them room and else on its face lower down,
    each sunk a little in the coins: the cup, an open chest with its coins spilling out over its lip, a round shield
    with its boss, the helmet, a drinking horn, a goblet and the crown (or the `pieces` given, as for `SET_OUT`), as
    many as the room holds. Returns spots on their gold a glint may catch on."""
    taken, laid = [], []
    for name, sunk, floor in pieces:
        art = globals()[name]
        w, h = len(art[0]), len(art)
        spot = None
        for x in range(x1 - w, x0 - 1, -1):
            if not all(x + i in crest for i in range(w)):
                continue
            rest = crest[x + w // 2] + sunk
            for y in ([g - h + 1 + sunk] if floor else range(min(rest, g + sunk) - h + 1, g - h + 2 + sunk)):
                if all(x + w <= a + 4 or x >= c - 4 for a, b, c, e in taken) and clear_art(p, art, x, y):
                    spot = (x, y)
                    break
            if spot:
                break
        if spot:
            x, y = spot
            taken.append((x, y, x + w, y + h - sunk))
            laid.append((y + h, name, x, y, sunk))
    shine = []
    for bottom, name, x, y, sunk in sorted(laid):
        art = globals()[name]
        if name == "CHEST":
            chest(p, x, bottom - 1 - sunk, night)
            spill = x
            while spill > x - 5 and p.clear_of_words(spill - 3, g - 6, spill + 2, g + 3):
                spill -= 1
            heap(p, spill, x + 6, g, 3, night, seed=x, peak=0.75, gems=False)
        else:
            treasure(p, x, y, art, night, below=bottom - sunk)
        shine += [(x + i, y + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch == "Z"][:2]
    return shine


SLIDE = 4.2         # seconds a coin takes to slip down the heap and come to rest, round and round
COIN = ["YZG", "YgY"]


def slide(p: Pix, crest: dict, x0, x1, night: bool):
    """In a moving header a coin that slips from the heap's crest at column x0 and slides and tumbles down its slope
    toward column x1 a step at a time, rests at its foot a moment and is gone, round and round: one coin moved
    along its way, on the steps of it that keep two units from every word. Returns whether it slides."""
    k = -1 if night else 0
    pal = {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[3 + k]}
    way = [x for x in list(range(x0, x1 - 1, -1 if x1 < x0 else 1))[::3]
           if x in crest and p.clear_of_words(x - 2, crest[x] - 4, x + 5, crest[x] + 2)]
    if len(way) < 3:
        return False
    sx, sy = way[0], crest[way[0]] - 2
    parts = []
    for c in sorted(set(pal.values())):
        runs = [f"M{sx + i} {sy + j + 0.5}h1" for j, row in enumerate(COIN) for i, ch in enumerate(row)
                if pal[ch] == c]
        parts.append(f'<path stroke="{c}" d="{"".join(runs)}"/>')
    steps = ";".join(["0 0"] + [f"{x - sx} {crest[x] - 2 - sy}" for x in way])
    times = ";".join(["0"] + [num(0.3 + 0.55 * i / (len(way) - 1)) for i in range(len(way))])
    moving = (f'<g opacity="0">{"".join(parts)}<animateTransform attributeName="transform" type="translate" '
              f'values="{steps}" keyTimes="{times}" dur="{SLIDE}s" repeatCount="indefinite" calcMode="discrete"/>'
              f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;.3;.95" dur="{SLIDE}s" '
              f'repeatCount="indefinite" calcMode="discrete"/></g>')
    p.raw(0.5, moving, "")
    return True


def skyline(crest: dict, g: int) -> str:
    """Path data for the shape under a crest, {x: the row of its top}, down to the floor at row g: one column at
    a time, a run of columns at the same height one step."""
    xs = sorted(crest)
    if not xs:
        return ""
    out = [f"M{xs[0]} {g + 1}"]
    prev = None
    for x in xs:
        top = crest[x]
        if top != prev:
            out.append(f"V{top}")
            prev = top
        out.append(f"H{x + 1}")
    out.append(f"V{g + 1}Z")
    d, merged = "".join(out), []
    # a run of H steps with no V between them is one H
    for part in re.findall(r"[A-Z][^A-Z]*", d):
        if part[0] == "H" and merged and merged[-1][0] == "H":
            merged[-1] = part
        else:
            merged.append(part)
    return "".join(merged)


def coin_tile(p: Pix, night: bool) -> str:
    """The pattern of coins lying every way in overlapping rows, each lit along its upper rim (see `COINS`); by
    night two steps into the dark. Made once a file."""
    k = -2 if night else 0
    pid = f"cn{'n' if night else 'd'}0"
    cells = {(x, y): GOLD[max(0, min(6, COIN_TONE[ch] + k))] for y, row in enumerate(COINS)
             for x, ch in enumerate(row)}
    return tile(p, pid, len(COINS[0]), len(COINS), cells)


def _coins(p: Pix, crest: dict, g, night: bool, seed=0, far=None, L="base", clear=False):
    """Coins heaped from each column's crest (`crest`, {x: row}) down to the floor at row g, laid as a pattern of
    coins in a shape that follows the crest: the far slope (the columns from `far` on) a step darker, the crest
    itself lit, a coin on its edge here and there along it (where it keeps two units from every word, if `clear`).
    By night the gold lies in the dark until a light falls on it."""
    k = -2 if night else 0
    xs = sorted(crest)
    if not xs:
        return
    away = {x: t for x, t in crest.items() if far is not None and x >= far}
    p.shapes[L].append(f'<path fill="url(#{coin_tile(p, night)})" d="{skyline(crest, g)}"/>')
    keep(p, {(x, y) for x, t in crest.items() for y in range(t, g + 1)})
    if away:
        p.shapes[L].append(f'<path fill="{X["shade_ink"]}" fill-opacity=".2" d="{skyline(away, g)}"/>')
    for x in xs:
        top = crest[x]
        if top <= g:
            p.px(x, top, GOLD[(5 if far is None or x < far else 4) + k], L)
        if (x * 11 + seed) % 13 == 0 and top < g - 3 and not (clear and not p.clear_of_words(x - 2, top - 5, x + 3,
                                                                                             top + 2)):
            for dy, c in enumerate((GOLD[6 + k], GOLD[4 + k], GOLD[2 + k])):
                p.px(x, top - 3 + dy, c, L)


# --------------------------------------------------------------------------- the floor between
def dropped(p: Pix, x0, x1, y, night: bool, seed=0):
    """What lies along a header's rule where no scene stands: the coins the thief let fall as he went, lying flat
    or on their edge, now and then two together or a garnet among them, each lit along its rim; kept two units
    from every word."""
    rnd = random.Random(seed * 13 + x0)
    k = -1 if night else 0
    flat = {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[4 + k], "g": GOLD[2 + k]}
    x = x0 + rnd.randrange(3, 12)
    while x < x1 - 4:
        if p.clear_of_words(x - 2, y - 5, x + 6, y + 2):
            kind = rnd.random()
            if kind < 0.6:
                stamp(p, x, y - 2, [".ZG.", "YGgY"], flat)
            elif kind < 0.8:
                stamp(p, x, y - 3, [".ZG..", "YGgZG", ".YGgY"], flat)
            elif kind < 0.92:
                stamp(p, x, y - 3, ["Z", "G", "g"], flat)
            else:
                gem(p, x, y - 2, "garnet", night)
        x += rnd.randrange(9, 26)


# --------------------------------------------------------------------------- the treasures
# A jewelled cup, 9 by 11: its bowl set with garnets under a lit rim, its stem with a garnet knop, its foot.
# Y its dark edge; Z G g z gold light to dark; r R garnets.
CUP = [
    "YYYYYYYYY",
    "YZGGGGGgY",
    "YGrGgRgzY",
    ".YgGgggY.",
    "..YgGzY..",
    "...YgY...",
    "...YGY...",
    "..YgRgY..",
    "...YgY...",
    ".YGGgzzY.",
    ".YYYYYYY.",
]
# The helmet of the ship burial, 13 by 15: its cap of iron panelled in tinned bronze, the crest down its middle,
# the gilt brows over its eyes set with garnets, the gilt nose and moustache, its face mask, its cheek guards.
# Y its dark edge; m M tinned bronze; G g gilt; r garnet; I J iron.
HELMET = [
    ".....YYY.....",
    "...YYMGMYY...",
    "..YMmMGmMmY..",
    ".YMmMmGMmMmY.",
    ".YmMmYGYMmMY.",
    "YmMYYYGYYYmMY",
    "YMYGGGGGGGYMY",
    "YmYrYYGYYrYmY",
    "YMYYYGgGYYYMY",
    "YmYYGGgGGYYmY",
    "YMYmYYGYYmYMY",
    "YmYMMmMmMMYmY",
    ".YMY.YYY.YMY.",
    ".YmY.....YmY.",
    "..YY.....YY..",
]
# A sword thrust into the hoard, 5 wide: its pommel of gold cloisonne with a garnet, its grip bound in gold wire,
# its guard, and the top of its blade going into the coins.
SWORD = [
    ".YZY.",
    "YGrGY",
    ".YgY.",
    "..YJY",
    "..YIY",
    "..YJY",
    ".YGGGY",
    "...M.",
    "...M.",
    "...Mm",
    "...Mm",
]
# A crown of gold, 11 by 6, its points tipped and garnets set round its band.
CROWN = [
    "Y...Y...Y..",
    "YG.YGY.YGY.",
    "YGGYgGYGgGY",
    "YGRGgGgGRGY",
    "YGGGGGGGGGY",
    ".YYYYYYYYY.",
]


# A drinking horn lying on the hoard, 18 by 7: its mouth at the left in a gilt rim, the horn bowing down and away to
# its tip in a gilt terminal, a gilt band about its middle. Y its dark edge; Z G g gold; B b d the horn, lit to dark.
HORN = [
    "YYY...............",
    "YZGY..............",
    "YGgBYY..Y.........",
    "YgBBbbYYGYY.....YY",
    ".YbBBbbbGbbYYYYYZY",
    "..YYdbbbgbbbbddGY.",
    "....YYYYYYYYYYYY..",
]
# A goblet of gold, 7 by 8, its bowl set with garnets.
GOBLET = [
    "YYYYYYY",
    "YZGGGgY",
    "YGrGRgY",
    ".YgGgY.",
    "..YgY..",
    "..YGY..",
    ".YGgzY.",
    ".YYYYY.",
]
# A gem cut en cabochon, 4 by 3, its dome lit at its top left: L M D the stone, lit to dark.
CABOCHON = [".LM.", "LMMD", ".DD."]
JEWELS = {"garnet": GARNET, "emerald": EMERALD, "sapphire": GLASS}


def treasure_pal(night: bool) -> dict:
    """The treasures' colours: gold and its dark edge, garnets, the helmet's tinned bronze and iron and the dark of
    its eyes, a horn's horn, a shield's board of garnet red; by night a step into the dark, until a light falls on
    them."""
    k = -1 if night else 0
    return {"Y": GOLD[0], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[3 + k], "z": GOLD[2 + k],
            "r": GARNET[3 + k], "R": GARNET[5 + k], "m": SILVER[2 + k], "M": SILVER[4 + k], "I": IRON[2 + k],
            "J": IRON[4 + k], "B": BONE[5 + k], "b": BONE[4 + k], "d": BONE[2 + k], "o": GARNET[3 + k],
            "O": GARNET[4 + k], "k": IRON[1], "s": SILVER[5 + k]}


def treasure(p: Pix, x, y, art, night: bool, L="base", below=None):
    """One of the hoard's treasures (`CUP`, `GOBLET`, `HELMET`, `SWORD`, `CROWN`, `HORN`, `SHIELD`) with its
    top-left at (x, y), rows from `below` down left out where it is sunk in the coins."""
    stamp(p, x, y, art, treasure_pal(night), L, below=below)


def jewel(p: Pix, x, y, kind: str, night: bool, L="base"):
    """A gem cut en cabochon lying on the gold: a garnet, an emerald or a sapphire (see `CABOCHON`)."""
    R, k = JEWELS[kind], -1 if night else 0
    stamp(p, x, y, CABOCHON, {"L": R[6 + k], "M": R[4 + k], "D": R[2 + k]}, L)


WANDER = 24.0       # seconds the glint takes to wander over the hoard and come round: a slow sweep of light


def wander(p: Pix, spots, night: bool, motion: bool, seed=0, n=12):
    """A glint wandering over the gold in a moving header: a star of light that swells on one spot of it and fades,
    and swells again on the next a little way along, round and round, by day and by night. `spots` are where it may
    catch, (x, y) on lit gold clear of every word; a drawing made lighter lets it catch on half as many, and a still
    drawing keeps it caught on the first."""
    if not spots:
        return
    rnd = random.Random(seed)
    picks = sorted(rnd.sample(sorted(spots), min(n // 2 if p.lite else n, len(spots))))
    path = picks[::2] + picks[1::2][::-1]
    linger = WANDER / len(path)
    core, arm, tip = (C["white"], GOLD[6], GOLD[5]) if not night else (X["glint"], GOLD[5], GOLD[4])
    cells = {(0, 0): core}
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cells[(dx, dy)], cells[(2 * dx, 2 * dy)] = arm, tip
    sid = p.symbol(("glint", night), cells)
    x0, y0 = path[0]
    still = f'<use href="#{sid}" x="{x0}" y="{y0}"/>'
    if not motion or len(path) < 2:
        p.raw(0.6, still, still)
        return
    steps = ";".join(f"{x} {y}" for x, y in path)
    moving = (f'<g><use href="#{sid}"/><animate attributeName="opacity" values="0;1;0" dur="{num(linger)}s" '
              f'repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" '
              f'values="{steps}" dur="{num(WANDER)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
    p.raw(0.6, moving, still)


# --------------------------------------------------------------------------- the barrow's mouth
# A bare tree on the downs, 9 by 10, seen against the sky: its trunk, its boughs and its twigs.
TREE = [
    "#...#....",
    ".#..#..#.",
    "..#.#.#.#",
    "#..###...",
    ".#..#..#.",
    "..#.#.#..",
    "...###...",
    "....#....",
    "....#....",
    "...###...",
]
TREE_S = ["#...#", ".#.#.", "#.##.", ".##.#", "..#..", "..#.."]
# The thief going away from the barrow over the snow, 11 by 20, seen from behind and dark against the snow: his
# hood, his cloak, his legs striding, and his arm raised high holding up the cup he took. k him; Z G g the cup, Y
# its dark edge.
THIEF = [
    ".......YZY.",
    ".......GgG.",
    "........G..",
    "........k..",
    "...kk...k..",
    "..kkkk..k..",
    "..kkkk..k..",
    "...kkk.kk..",
    "..kkkkkkk..",
    ".kkkkkkkk..",
    ".kkkkkkk...",
    ".kkkkkkk...",
    "kkkkkkkk...",
    "kkkkkkkk...",
    ".kkkkkkk...",
    "..kkkkk....",
    "..kk.kk....",
    "..kk..kk...",
    ".kk....k...",
    ".k.....kk..",
]
THIEF_CUP = (8, 0)  # the cup's lit rim, where it glints
# The same thief, 9 by 15, further off up the slope, for a door too small for him near.
THIEF_S = [
    "......ZG.",
    "......GgY",
    ".......Y.",
    "......k..",
    "..kk..k..",
    ".kkkk.k..",
    "..kk..k..",
    ".kkkkkk..",
    ".kkkkk...",
    ".kkkkk...",
    "..kkkk...",
    "..kkk....",
    "..k.k....",
    ".k...k...",
    ".k...k...",
]
# The moon by night, 5 by 5, with its shadowed limb.
MOON = [".MMm.", "MMMMm", "MMMMm", "MMMmm", ".mmm."]


def stone_tile(p: Pix, night: bool) -> str:
    """The dressed face of a great stone as a pattern, made once a file."""
    cells = {(x, y): _stone_face(x, y, night, 4) for x in range(23) for y in range(13)}
    return tile(p, f"st{'n' if night else 'd'}", 23, 13, cells)


def _rock(p: Pix, x0, y0, x1, y1, night: bool, seed=0, carve=None, L="base"):
    """A great stone from (x0, y0) to (x1, y1), its corners knocked off: its face mottled, lit along its top and
    its left, in shadow along its foot and its right, a dark edge round it, and a carving (`carve`, art in
    grooves) centred on its face."""
    k = -1 if night else 0
    w, h = x1 - x0, y1 - y0
    d = (f"M{x0 + 2} {y0}h{w - 4}v1h1v1h1v{h - 4}h-1v1h-1v1h-{w - 4}v-1h-1v-1h-1v-{h - 4}h1v-1h1z")
    p.shapes[L].append(f'<path fill="url(#{stone_tile(p, night)})" d="{d}"/>')
    keep(p, {(x, y) for x in range(x0, x1) for y in range(y0, y1)})
    p.hline(x0 + 2, x1 - 2, y0, STONE[0], L)
    p.hline(x0 + 2, x1 - 2, y1 - 1, STONE[0], L)
    p.vline(x0, y0 + 2, y1 - 2, STONE[0], L)
    p.vline(x1 - 1, y0 + 2, y1 - 2, STONE[0], L)
    for (cx, cy) in ((x0 + 1, y0 + 1), (x1 - 2, y0 + 1), (x0 + 1, y1 - 2), (x1 - 2, y1 - 2)):
        p.px(cx, cy, STONE[0], L)
    p.hline(x0 + 2, x1 - 2, y0 + 1, STONE[5 + k], L)
    p.vline(x0 + 1, y0 + 2, y1 - 2, STONE[5 + k], L)
    p.hline(x0 + 2, x1 - 2, y1 - 2, STONE[2 + k], L)
    p.vline(x1 - 2, y0 + 2, y1 - 2, STONE[2 + k], L)
    if carve:
        cx = (x0 + x1 - len(carve[0])) // 2
        cy = (y0 + y1 - len(carve)) // 2
        for (i, j), c in _carved(carve, night).items():
            p.px(cx + i, cy + j, c, L)


def _view(p: Pix, x0, y0, x1, y1, night: bool, motion: bool, thief=True):
    """The world outside the barrow's mouth, seen through it from (x0, y0) to (x1, y1): the snowy downs rolling
    away under a pale winter sky by day, a bare tree on the far ridge and the thief striding away just outside the
    door, sixteen units tall and dark against the snow with the cup he took held high against the downs (further
    off up the near slope where the door is too small for him near), the low sun's glints on the snow; by night the
    same downs blue under a deep sky with the moon and a few stars over them, and the cup glinting in his hand.
    Returns where his feet are, for his footprints back to the door, or None where the view is too narrow for him."""
    w, h = x1 - x0, y1 - y0
    k = -1 if night else 0
    horizon = y0 + round(h * 0.46)
    sky = (FROST[6], FROST[5], FROST[4]) if not night else (NIGHT[0], NIGHT[1], NIGHT[2], NIGHT[3])
    far, snow, shade = (FROST[5], C["white"], FROST[4]) if not night else (FROST[2], FROST[3], FROST[1])
    edges = [y0 + i * (horizon + 3 - y0) // len(sky) for i in range(len(sky) + 1)]
    for c, a, b in zip(sky, edges, edges[1:]):
        p.shapes["base"].append(f'<rect x="{x0}" y="{a}" width="{w}" height="{b - a}" fill="{c}"/>')
    # the far downs along the horizon, and the near slope rising before them
    ridge = {x: horizon + round(1.4 * math.sin((x - x0) * 0.33) + math.sin((x - x0) * 0.12 + 1)) for x in range(x0, x1)}
    slope = {x: max(ridge[x] + 3, horizon + round(h * 0.16) - round(2.2 * math.sin((x - x0) * 0.16 + 0.5)))
             for x in range(x0, x1)}
    p.shapes["base"].append(f'<path fill="{far}" d="{skyline(ridge, y1 - 1)}"/>')
    p.shapes["base"].append(f'<path fill="{snow}" d="{skyline(slope, y1 - 1)}"/>')
    keep(p, {(x, y) for x in range(x0, x1) for y in range(y0, y1)})
    for x in range(x0, x1):
        p.px(x, ridge[x], snow if not night else FROST[4])
        p.px(x, slope[x], C["white"] if not night else FROST[4])
        p.px(x, slope[x] + 1, shade if (x - x0) % 4 else snow)
    tree = C["ink"] if not night else NIGHT[0]
    art = TREE if w >= 24 else TREE_S
    tx = x1 - len(art[0]) - 1
    stamp(p, tx, ridge[tx + len(art[0]) // 2] - len(art) + 1, art, {"#": tree})
    if not night:
        for i, (gx, gy) in enumerate(((x0 + 3, y1 - 3), (x0 + w - 4, y1 - 6), (x0 + w // 2, y1 - 2))):
            p.px(gx, gy, X["glint"], p.twinkle(i) if motion else "base")
    else:
        # under the icicles hung at the top of the door, the moon and a few stars
        mx, my = x0 + 2, y0 + min(10, round(h * 0.22))
        stamp(p, mx, my, MOON, {"M": MOONLIT[4], "m": MOONLIT[2]})
        p.halo(mx + 2.5, my + 2.5, 5, 5, MOONLIT[3], (0.12, 0.24), L="haze", shape=False)
        for i, (sx, sy) in enumerate(((x0 + w - 3, my - 1), (x0 + w // 2 + 2, my + 2), (x0 + w - 7, my + 6),
                                      (x0 + 9, my + 9))):
            if sy < horizon - 2:
                p.px(sx, sy, FROST[6] if i % 2 else FROST[5], p.twinkle(i) if motion else "base")
    if not thief or w < 12:
        return None
    pal = {"k": C["ink"] if not night else NIGHT[0], "G": GOLD[5 + k], "Z": GOLD[6], "g": GOLD[3 + k], "Y": GOLD[1]}
    if w >= 15 and h >= 30:
        # near the door, striding away over the snow, the cup held high against the downs
        art, cup = THIEF, THIEF_CUP
        tx = x0 + max(1, (w - len(art[0])) // 2 - 1)
        ty = y1 - 3 - len(art)
    else:
        art, cup = THIEF_S, (6, 0)
        tx = x0 + 1 if w < 24 else x0 + w // 2 - 6
        ty = slope[tx + 4] - len(art) + 3
    stamp(p, tx, ty, art, pal)
    if motion:
        p.px(tx + cup[0], ty + cup[1], X["glint"], p.twinkle(2))
    return (tx + 3, ty + len(art))


def footprints(p: Pix, x0, y0, x1, y1, night: bool):
    """The thief's footprints going out across the snow from (x0, y0) to (x1, y1): each print a little hollow in
    the snow in its blue shadow, left and right by turns a stride apart, laid over the light on the snow."""
    c = FROST[2] if not night else FROST[0]
    L = p.layer("prints", z=4)
    n = max(1, round(math.hypot(x1 - x0, y1 - y0) / 3.5))
    for i in range(n + 1):
        t = i / n
        x = round(x0 + (x1 - x0) * t) + (1 if i % 2 and abs(x1 - x0) < abs(y1 - y0) else 0)
        y = round(y0 + (y1 - y0) * t) + (1 if i % 2 and abs(x1 - x0) >= abs(y1 - y0) else 0)
        p.hline(x, x + 2, y, c, L)


def drift(p: Pix, x0, x1, g, height, night: bool, peak=0.0, L="base") -> dict:
    """A drift of snow on the barrow's floor from x0 to x1, standing on row g, `height` rows deep at `peak` (0 its
    left end) and thinning away from it: lit white along its crest and its blue shadow along its foot and in its
    hollows. Returns its crest, {x: the row of its top}."""
    snow, lit, shade, deep = (FROST[4], C["white"], FROST[3], FROST[2]) if not night else \
        (FROST[2], FROST[3], FROST[1], FROST[0])
    crest = {}
    for x in range(x0, x1):
        u = (x - x0) / max(1, x1 - x0)
        d = abs(u - peak)
        top = g - round(height * max(0.0, 1 - d * 1.15) ** 1.4 + 0.6 * math.sin(x * 0.7))
        crest[x] = min(top, g)
    p.shapes[L].append(f'<path fill="{snow}" d="{skyline(crest, g)}"/>')
    keep(p, {(x, y) for x, t in crest.items() for y in range(t, g + 1)})
    for x, top in crest.items():
        p.px(x, top, lit, L)
        p.px(x, g, deep, L)
        if top < g - 2 and (x * 7) % 11 == 0:
            p.px(x, top + 2, shade, L)
    return crest


# The carvings on the mouth's stones: rings and lozenges down a jamb; across the capstone the three spirals of the
# passage grave's entrance stone, wound into one another, or where the stone is less deep a pair of them.
LOZENGES = [".###.", "#...#", "#.#.#", "#...#", ".###.", ".....", ".###.", "#...#", "#.#.#", "#...#", ".###."]
TWIN_SPIRAL = SPIRALS[:6]
TRIPLE_SPIRAL = [
    ".............####.............",
    "............##...##...........",
    "...........#.......#..........",
    "...........#.#####.##.........",
    "..........#..#...#..#.........",
    "..........##.##..#............",
    "......###..#.....#...###......",
    ".....#..##..##..#...##..#.....",
    "....#.....#..###...#.....#....",
    "....#..##.##......##.##..#....",
    ".#..#...#..#......#..#...#..#.",
    ".##.#####.#........#.#####.##.",
    "..#.......#........#.......#..",
    "...##...##..........##...##...",
    ".....####............####.....",
]


MOUTH_ROOMS = (56, 52, 48, 42)   # the widths the mouth may take past its first column, widest first


def mouth(p: Pix, x0, g, night: bool, motion: bool, rows: int, reach: int, room: int = 52) -> tuple:
    """The barrow's mouth at the left of a header, from column x0 on the floor at row g, as tall as `rows` allow
    and as wide as `room` (see `MOUTH_ROOMS`): the great stones of a passage grave's entrance, two massive jambs
    carved with rings and lozenges and a deep capstone over them carved with the three spirals (a pair of them on
    a shallower stone), icicles along its foot, and through the door the world outside (see `_view`); the snow
    blown in through it, heaped against the jambs and spread across the floor as far as `reach`, and the thief's
    footprints going out over it and on over the snow outside. By day the snowlight spills round the door onto
    the wall; by night the moon's blue light lies in a pool on the drift and in a cold shaft across the floor into
    the barrow. Returns the span of the rule it covers."""
    cap = 19 if rows >= 64 and room >= 48 else 12
    oh = max(18, min(46, rows - cap - 3))
    jw = 12 if room >= 52 else 11 if room >= 48 else 9
    ow = 25 if room >= 56 and oh >= 40 else 21 if room >= 52 else 19 if room >= 48 else 17
    top = g - oh - cap
    view = (x0 + jw, g - oh, x0 + jw + ow, g)
    door = x0 + jw + ow // 2
    if not night:
        halo(p, door, g - oh / 2, ow + 14, oh * 0.62 + 8, FROST[6], (0.14, 0.26, 0.4), shape=True)
    else:
        pool(p, door + 6, g - 2, ow + 30, 14, FROST[2], (0.06, 0.13, 0.2))
        pool(p, door, g - oh / 2, ow + 4, oh * 0.6, NIGHT[3], (0.1,))
        # the moon's cold light falling in at the door and lying in a shaft across the floor into the barrow
        far = max(door + 24, min(reach, door + 180))
        rings = [[(door - ow * 0.45, g + 1), (door - ow * 0.45, g - lift), (door + ow * 0.55, g - lift),
                  (door + (far - door) * reach_, g - 2), (door + (far - door) * reach_, g + 1)]
                 for reach_, lift in ((1.0, 9), (0.7, 7), (0.42, 5))]
        shaft(p, rings, FROST[4], (0.14, 0.25, 0.38))
    end = _view(p, *view, night, motion)
    _rock(p, x0, g - oh - 1, x0 + jw, g + 1, night, seed=1, carve=LOZENGES if oh >= 26 else None)
    _rock(p, x0 + jw + ow, g - oh - 1, x0 + 2 * jw + ow, g + 1, night, seed=2,
          carve=LOZENGES if oh >= 26 else None)
    _rock(p, x0 - 3, top, x0 + 2 * jw + ow + 3, g - oh + 1, night, seed=3,
          carve=TRIPLE_SPIRAL if cap >= 19 else TWIN_SPIRAL)
    icicles(p, x0 + 2, x0 + 2 * jw + ow, g - oh + 1, night, seed=11, foot=g - oh + 9)
    # snow heaped against the jambs inside, and the drift across the floor, lit where the light pours in
    crest = drift(p, x0 + jw - 2, reach, g, 7, night, peak=0.06)
    drift(p, x0 + 1, x0 + jw + 2, g, 5, night, peak=0.9)
    shine = C["white"] if not night else FROST[4]
    halo(p, door + 4, g - 1, ow + 22, 7, shine, (0.14, 0.28, 0.42) if not night else (0.08, 0.16, 0.26), L="pool",
         shape=True)
    out = min(reach - 8, door + 70)
    footprints(p, out, crest.get(out, g) + 2, door + 4, g - 2, night)
    if end:
        footprints(p, door + 2, g - 2, end[0] + 1, end[1] - 1, night)
    return (x0 - 4, reach + 1)


# A round shield of limewood, 11 by 11, its board painted, its rim bound in iron and its boss and mounts gilt.
SHIELD = [
    "...YYYYY...",
    "..YJIIIJY..",
    ".YJooOooJY.",
    "YJoOGooOoJY",
    "YIooYYYooJY",
    "YIoYGZgYoJY",
    "YIooYgYooJY",
    "YJoOooGOoJY",
    ".YJooOooJY.",
    "..YJIIIJY..",
    "...YYYYY...",
]


# The standard all of gold that stood high over the hoard, 17 by 33: a banner woven of gold thread in lozenges
# between bands of garnet, hung from a gilt crossbar at the head of its pole, its foot cut in three tails with
# tassels, and a gilt boar on the pole's head. Y its dark edge; Z G g z its gold light to dark; R r its garnet
# bands; P Q the pole lit and in shade; T t its tassels.
STANDARD = [
    "......YY.........",
    ".....YZGY..Y.....",
    "....YZGGgYYgY....",
    "....YGgggggzY....",
    ".....YgYzzYY.....",
    "........PQ.......",
    "YYYYYYYYPQYYYYYYY",
    "YZGGGGGGGGGGGGGzY",
    ".YYYYYYYYYYYYYYY.",
    ".YRRRRRRRRRRRRRY.",
    ".YrrrrrrrrrrrrrY.",
    ".YGgGzGgGgGzGgGY.",
    ".YgGzZzGgGzZzGgY.",
    ".YGzZGZzGzZGZzGY.",
    ".YgGzZzGgGzZzGgY.",
    ".YGgGzGgGgGzGgGY.",
    ".YgGgGgGzGgGgGgY.",
    ".YGgGgGzZzGgGgGY.",
    ".YgGgGzZGZzGgGgY.",
    ".YGgGgGzZzGgGgGY.",
    ".YgGgGgGzGgGgGgY.",
    ".YGgGzGgGgGzGgGY.",
    ".YgGzZzGgGzZzGgY.",
    ".YGzZGZzGzZGZzGY.",
    ".YgGzZzGgGzZzGgY.",
    ".YGgGzGgGgGzGgGY.",
    ".YRRRRRRRRRRRRRY.",
    ".YrrrrrrrrrrrrrY.",
    ".YGgGgYGgGYgGgGY.",
    ".YgGgY.YgY.YgGgY.",
    "..YgY...Y...YgY..",
    "..TtT...T...TtT..",
    "...T.........T...",
]
STANDARD_FOOT = 33  # the row of the art its pole leaves the banner from


def standard(p: Pix, cx, g, top, night: bool, motion: bool) -> tuple:
    """The golden standard of the hoard, its pole planted in a heap of its own gold on the floor at row g with
    its foot at column cx and its banner's head at row `top`: the heap with a round shield leaning on it and a
    chest of iron-bound oak beside it, its lid thrown back and its coins brimming over; in a moving header its
    gold catching the light as it stirs; and by night shining with its own light, as the poem tells, its glow
    on the wall about it and on the gold under it. Returns the span of the rule it covers."""
    k = -1 if night else 0
    x0, x1 = cx - 24, cx + 26
    crest = heap(p, x0, x1, g, 9, night, seed=cx, peak=0.45)
    pal = {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "z": GOLD[3 + k],
           "R": GARNET[4 + k], "r": GARNET[2 + k], "P": OAK[5 + k], "Q": OAK[2 + k], "T": GOLD[4 + k],
           "t": GARNET[4 + k]}
    bx = cx - 8
    stamp(p, bx, top, STANDARD, pal)
    for y in range(top + STANDARD_FOOT, crest[cx] + 2):
        p.px(cx, y, OAK[5 + k])
        p.px(cx + 1, y, OAK[2 + k])
    # the shield leaning on the heap, the chest beside it
    sh = dict(treasure_pal(night))
    sh.update({"o": GARNET[3 + k], "O": GARNET[4 + k]})
    stamp(p, x0 + 6, crest[x0 + 11] - 7, SHIELD, sh)
    chest(p, cx + 9, g, night)
    # its gold catching the light, a glint at a time
    weave = [(bx + i, top + j) for j, row in enumerate(STANDARD) for i, ch in enumerate(row) if ch == "Z"]
    if motion:
        for i, (x, y) in enumerate(weave[::3]):
            p.px(x, y, X["glint"], p.twinkle(i))
    if night:
        halo(p, cx + 0.5, top + 18, 16, 22, GOLD[4], (0.05, 0.1, 0.16), shape=True)
        pool(p, cx, top + 20, 46, 34, GOLD[3], (0.04, 0.08, 0.12))
        lamp(p, cx + 0.5, top + 18, 26, GOLD[4], {(bx + i, top + j) for j, row in enumerate(STANDARD)
                                                  for i, ch in enumerate(row) if ch != "."})
    glitter(p, [(x, crest[x] + 1) for x in range(x0 + 2, x1 - 2, 3)], night, motion, seed=cx)
    return (x0 - 1, x1 + 1)


# A chest of the hoard, 17 by 12, standing open: its oak boards bound in iron, its lid thrown back behind it, its
# coins heaped above its rim. o O its oak; I J its iron; c its coins; Y their dark edge.
CHEST = [
    "..IJJJJJJJJJJJI..",
    ".IoOOOOOOOOOOOoI.",
    ".IoOOOOOOOOOOOoI.",
    "..YcYcYcYcYcYcY..",
    ".YcZcGcZcGcZcGcY.",
    "IJJJJJJJJJJJJJJJI",
    "IoOOoIOOOOOIoOOoI",
    "IoOoOIOOJOOIoOoOI",
    "IoOOoIOOOOOIoOOoI",
    "IoOoOIOOOOOIoOoOI",
    "IJJJJJJJJJJJJJJJI",
    ".I.............I.",
]


def chest(p: Pix, x, g, night: bool):
    """An open chest with its left at column x on the floor at row g (see `CHEST`)."""
    k = -1 if night else 0
    stamp(p, x, g - len(CHEST) + 1, CHEST, {"o": OAK[3 + k], "O": OAK[4 + k], "I": IRON[1], "J": IRON[4 + k],
                                            "c": GOLD[4 + k], "Z": GOLD[6 + k], "G": GOLD[5 + k], "Y": GOLD[2 + k]})


BIG_EYE_TIMES = ((0.5, 0.56), (0.56, 0.84), (0.84, 0.9))
BIG_EYE_LOOP = 8.0


def head_on_gold(p: Pix, nx, L: int, x1, g, night: bool, motion: bool, top=None) -> tuple:
    """A section's header: the dragon's great head `L` long resting its jaw on its gold with its nose at column nx
    and the floor at row g, as much of its neck as the room to column x1 allows rising behind it out of the hoard,
    its spines along it and its throat plated in ivory; the coins heaped under its jaw and up against its neck and
    lying before it, a cup before its nose, a sword thrust in the gold behind its head and gems in garnet, emerald
    and sapphire on it; its smoke rising, and in a moving header its eye opening on the room a while and closing
    again and a glint wandering over the gold. By night its breath glows in its nostrils and lights its snout and
    the coins. Nothing of it rises over row `top`. Returns the span of the rule it covers and where its nose, its eye
    and its nape are."""
    top = ICE_FOOT + 3 if top is None else top
    f = L / 100
    hy = g - 4 - round(JAW_FOOT * f)
    nape = (nx + NAPE[0] * f, hy + NAPE[1] * f)
    x0 = nx - 8
    while x0 < nx and not p.clear_of_words(x0 - 2, g - 8, x0 + 3, g + 3):
        x0 += 1
    crest = {x: min(g, round(g - 4 - max(0.0, (x - nx - 0.55 * L) / (x1 - nx - 0.55 * L + 1)) * 0.42 * L
                             - 0.8 * math.sin(x * 1.1))) for x in range(x0, x1 + 1)}
    _coins(p, crest, g, night, far=round(nape[0]))
    stamp(p, round(nape[0] - 0.12 * L), crest[round(nape[0] - 0.1 * L)] - len(SWORD) + 3, SWORD, treasure_pal(night))
    rise = max(0.0, min(0.32 * L, hy - top - 0.24 * L))
    neck = _q(((x1 + 0.3 * L, hy - rise), (x1 + 0.04 * L, hy - min(rise, 0.06 * L)),
               (nape[0] + 0.14 * L, nape[1] - 0.06 * L), nape))
    nspec = _q(("even", 0.19 * L, 0.15 * L))
    scales(p, _body(neck, nspec), night, belly=-1, right=x1, ceiling=top)
    spines(p, neck, nspec, night, side=1, every=0.09 * L, s0=0.0, size=1.2, right=x1, ceiling=top)
    look = head(p, nx, hy, L, night, motion, frames="be", times=BIG_EYE_TIMES, loop=BIG_EYE_LOOP)
    front = {x: g - 2 - (1 if x % 5 == 0 else 0) for x in range(x0, x1 + 1)}
    _coins(p, front, g, night, seed=2)
    if clear_art(p, CUP, nx - 13, g - len(CUP) + 1):
        treasure(p, nx - 13, g - len(CUP) + 1, CUP, night)
    base = p.layers["base"]
    rnd = random.Random(nx + g)
    for kind in ("garnet", "emerald", "sapphire"):
        x = rnd.randrange(round(nape[0]), max(round(nape[0]) + 1, x1 - 4))
        y = max(crest[x], crest[min(x1, x + 3)]) + rnd.randrange(1, 4)
        if y + 2 < g and clear_art(p, CABOCHON, x, y) and \
                all(base.get((x + i, y + j)) in (None,) + tuple(GOLD) for i in range(4) for j in range(3)):
            jewel(p, x, y, kind, night)
    k = -2 if night else 0
    spots = [(x, crest[x]) for x in range(x0, x1, 2) if base.get((x, crest[x])) in (GOLD[5 + k], GOLD[4 + k])]
    spots += [(x, g - 2) for x in range(x0, nx, 3)]
    wander(p, [(x, y) for x, y in spots if p.clear_of_words(x - 3, y - 3, x + 4, y + 4)], night, motion, seed=nx)
    if night:
        pool(p, nx + 0.45 * L, g - 0.2 * L, 0.9 * L, 0.45 * L, GOLD[3], (0.04, 0.08, 0.12, 0.16))
    return (min(x0, nx - 14) - 1, x1 + 1), look


def head_place(p: Pix, x0, x1, g, top, most=72, least=20, lift=4, neck=0.5) -> tuple:
    """The largest head, from `most` long down to `least`, that rests its jaw `lift` rows over the floor at row g
    between columns x0 and x1 with its horns under row `top`, keeping two units from every word: its nose as far
    left as leaves room for its neck behind it, up to `neck` of its length, and its horns inside x1. Returns its
    nose's column and its length, or None."""
    for L in range(most, least - 1, -2):
        f = L / 100
        hy = g - lift - round(JAW_FOOT * f)
        if hy - round(14 * f) < top:
            continue
        for nx in range(max(x0, x1 - round((1.22 + neck) * L)), x1 - round(1.22 * L) + 1):
            if head_room(p, nx, hy, L):
                return nx, L
    return None


# A gold coin struck with a cross, 7 by 7, its rim lit along its upper left: the mark of a section.
COIN_MARK = [
    "..YYY..",
    ".YZGGY.",
    "YZGYGgY",
    "YGYYYgY",
    "YGgYggY",
    ".YggzY.",
    "..YYY..",
]


def coin_mark(p: Pix, x, y, night: bool):
    """A gold coin struck with a cross, the mark beside SECTION A-A."""
    k = -1 if night else 0
    stamp(p, x, y, COIN_MARK, {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k],
                               "z": GOLD[3 + k]})


# --------------------------------------------------------------------------- the helmet, for a strip
# The helmet of the ship burial drawn as the showpiece of a strip, 25 by 30, as it was found: its cap of iron
# panelled in tinned bronze, lit from the left, the crest down its middle ending over the brows in a gilt dragon's
# head; the brows gilt and set with garnets, a boar's head at each end; the eyes dark; the gilt dragon flying up
# the face, its body the nose and its tail the moustache; the mouth, the face mask, and the cheek guards hanging
# beside it. Letters as for HELMET; k the dark of the eyes, s the tinned bronze where the light is on it.
GREAT_HELM = [
    "........YYYYYYYYY........",
    "......YYsMMYZYmmMYY......",
    ".....YsMMMMYGYmmmmMY.....",
    "....YsMMJMMYZYmmImmMY....",
    "...YsMMMJMMYGYmmImmmMY...",
    "...YMMMMJMMYZYmmImmmmY...",
    "..YJJJJJJJJYGYIIIIIIIIY..",
    "..YsMJMMJMJYZYImImmImMY..",
    ".YsMMMMMJMMYGYmmImmmmmMY.",
    ".YMJMMJMJMYZZGYmImImmImY.",
    "YMMMMMMMJYZGZgGYImmmmmmmY",
    "YIIIIIIIIYGZGGgYIIIIIIIIY",
    "YMsYZGGGGGGZZGggggggGYMmY",
    "YMmYYgRrRrRrGrRrRrRgYYmmY",
    "YJmYMYYkkkkYZYkkkkYYmYmJY",
    "YMmYMYkkkkkYGYkkkkkYmYmmY",
    "YMJYMMYkkkYYZYYkkkYmmYImY",
    "YMmYMMMYYYMYGYmYYYmmmYmmY",
    "YMmYMMMMMMYGZgYmmmmmmYmmY",
    "YJmYMMMMMYZgGgGYmmmmmYmJY",
    "YMmYMMMMYZGGYggGYmmmmYmmY",
    "YMmYMMYZGGgggggggGYmmYmmY",
    "YMJYMYZGgYYYYYYYggGYmYImY",
    "YMmYMYgYMMMMMmmmmYgYmYmmY",
    "YMmYMMYMMMMMMmmmmmYmmYmmY",
    "YJmYYMMMMMMMMmmmmmmmYYmJY",
    "YMmY.YYMMMMMMmmmmmYY.YmmY",
    "YMmY...YYYYYYYYYYY...YmmY",
    ".YmY.................YmY.",
    "..YY.................YY..",
]
# The same helmet drawn small, 21 by 24, for a phone. Letters as for HELMET.
SMALL_HELM = [
    ".......YYYYYYY.......",
    ".....YYMmYGZYmMYY....",
    "...YYMMmmYGgYmmMMYY..",
    "..YMMmmYMYGgYMYmmMMY.",
    ".YMMmmYMMYGgYMMYmmMMY",
    ".YMmmYMMmYGgYmMMYmmMY",
    "YMMmmYMMmYGgYmMMYmmMY",
    "YMMmmYMMmYGgYmMMYmmMY",
    "YmYYYYYYYYGYYYYYYYYmY",
    "YMYgGrGGrGZGrGGrGgYMY",
    "YmYGYYYYYYGYYYYYYGYmY",
    "YMYYKKKKKYGYKKKKKYYMY",
    "YmMYKKKKYGgGYKKKKYMmY",
    "YMmMYYYYGGgGGYYYYMmMY",
    "YmMMmmYGGgGgGGYmmMMmY",
    "YMMmmYZgYYGYYgZYmmMMY",
    "YmMmYgYMMmmmMMYgYmMmY",
    "YMMmmYmMYYYYYMmYmmMMY",
    "YmMMmmmMMmmmMMmmmMMmY",
    ".YMmmYMMmmmmmMMYmmMY.",
    ".YmMMYMMmmmmmMMYMMmY.",
    "..YMmYYMMmmmMMYYmMY..",
    "..YmY..YMMmMMY..YmY..",
    "...YY...YYYYY...YY...",
]


# The great gold buckle of the ship burial, 18 by 7, lying on the coins: its loop and tongue at the left, its plate
# worked with interlace, its three bosses. Letters as for HELMET.
BUCKLE = [
    "..YYY..YYYYYYYYY..",
    ".YZGGY.YZGGGGGGGY.",
    "YZgYGGYZGYZGYZGgzY",
    "YGYZYGGGgYGgYGgYzY",
    "YzGgGYYgGGzGGzGgzY",
    ".YzzY.YgzzzzzzzzY.",
    "..YY...YYYYYYYYY..",
]
# The pair of shoulder clasps, 17 by 6, gold set with garnets in stepped cells, their halves pinned together.
CLASPS = [
    "YYYYYYYY.YYYYYYYY",
    "YZGGGGGYMYZGGGGGY",
    "YGRrRrGYMYGRrRrGY",
    "YGrRrRGYMYGrRrRGY",
    "YGGGGGgYMYGGGGGgY",
    "YYYYYYYY.YYYYYYYY",
]
# A sword laid along the coins, 26 by 5: its pommel of gold set with a garnet, its grip bound in iron, its gilt
# guard and its long blade.
BLADE = [
    ".YYY......YY..............",
    "YZRGYYYYYYGZYYYYYYYYYYYYY.",
    "YGrgYJIJIJGGsMMMMMMMMMMMMY",
    "YgggYYYYYYGgmmmmmmmmmmmmY.",
    ".YYY......YY..............",
]
# What lies on the coins along a strip's floor before the helm, as for `SET_OUT`.
BAND_OUT = (("BUCKLE", 1, False), ("CLASPS", 1, False), ("BLADE", 1, False), ("HORN", 2, False))


def helm_on_gold(p: Pix, x1, g, night: bool, motion: bool, cup=False, spread=8, art=SMALL_HELM, left=None,
                 room=0) -> tuple:
    """A strip's scene, ending at column x1 on the floor at row g: the helm (`art`, the great one or the small one
    for a phone) set on a heap of coins, the heap running `spread` columns before it, its garnets catching the
    light, the heap of the great one as high as the `room` (the rows over the floor clear of words) lets it raise the
    helm; a sword laid against the heap of the small one, and where the title left the strip's own cup no room
    beside it, the jewelled cup standing on the coins before it. Where the words leave the floor clear back to
    column `left`, the hoard spills along it from the heap filling the band under them, a drift of coins as deep as
    the words over it leave it room, and the great gold buckle, the shoulder clasps, a sword and a drinking horn
    lie heaped on it nearest the helm (see `set_out`), gems in garnet, emerald and sapphire among them. A glint
    wanders over the gold, and by night the gleam of the gold round the helm lights it. Returns the span of the
    rule it covers."""
    w, big = len(art[0]), art is GREAT_HELM
    hx = x1 - w - (4 if big else 8)
    x0 = hx - (16 if cup else spread) - (12 if big else 0)
    left = x0 if left is None else min(left, x0)
    crest = {}
    high = max(11, min(18, room - len(art) - 1)) if big else 9
    for x in range(left, x1):
        if x >= x0:
            t = g - round(high * _hill((x - x0 + 0.5) / (x1 - x0), 0.58)) - (1 if x % 4 == 0 else 0)
        else:
            u = (x - left + 0.5) / max(1, x0 - left)
            t = round(g - 1 - 6 * u ** 1.6 - 0.8 * math.sin(x * 1.1) - 0.5 * math.sin(x * 0.37 + 2))
        crest[x] = min(g - 1, max(t, room_top(p, x, ICE_FOOT, g) + 1))
    _coins(p, crest, g, night, far=hx + w, clear=True)
    k = -1 if night else 0
    if not big:
        for i in range(12):
            p.px(x1 - 4 - i // 2, g - 16 + i, SILVER[4 + k] if i % 2 else SILVER[2 + k])
        stamp(p, x1 - 5, g - 20, SWORD[:6], treasure_pal(night))
    top = crest[hx + w // 2] - len(art) + 3
    stamp(p, hx, top, art, treasure_pal(night))
    if cup:
        treasure(p, x0 + 3, crest[x0 + 7] - len(CUP) + 2, CUP, night)
    shine = [(hx + w // 2, top + 11), (hx + w // 2, top + 20)]
    if big:
        shine += set_out(p, crest, hx + 6, left, g, night, BAND_OUT)
        rnd = random.Random(left + g)
        for kind in ("garnet", "emerald", "sapphire", "garnet", "emerald", "sapphire"):
            x = rnd.randrange(left, x1 - 4)
            y = max(crest[x], crest[x + 3]) + 1
            if y + 2 < g and clear_art(p, CABOCHON, x, y) and \
                    all(p.get(x + i, y + j) in (None,) + tuple(GOLD) for i in range(4) for j in range(3)):
                jewel(p, x, y, kind, night)
    spots = [(x, crest[x]) for x in range(left + 1, x1, 2) if crest[x] < g - 1] + shine
    wander(p, [(x, y) for x, y in spots if p.clear_of_words(x - 3, y - 3, x + 4, y + 4)], night, motion, seed=x1)
    if night:
        pool(p, hx + w / 2, g - 10, (x1 - x0) * 0.7, 22, GOLD[3], (0.05, 0.1, 0.15, 0.2))
        if left < x0:
            pool(p, (left + x0) / 2, g - 3, (x0 - left) * 0.6, 10, GOLD[3], (0.05, 0.1))
        lamp(p, hx + w / 2, crest[hx + w // 2], w * 0.9, GOLD[4],
             only=set(SILVER) | set(IRON) | set(GOLD) | set(GARNET))
    return (left - 1, x1 + 1)


# --------------------------------------------------------------------------- a phone's pieces
def head_peeking(p: Pix, x1, g, night: bool):
    """The dragon's great head resting on a little heap of its gold beside a phone's SECTION A-A, ending at column
    x1 on the ground at row g, as large as the room there allows (see `head_on_gold`), its eye shut and its smoke
    rising. Returns the box it takes, or None where no head fits."""
    spot = head_place(p, SIDE + 2, x1, g, ICE_FOOT + 2, most=48, least=34, neck=0.2)
    if not spot:
        return None
    nx, L = spot
    (a, b), _ = head_on_gold(p, nx, L, x1, g, night, False, top=ICE_FOOT + 2)
    return (a - 2, g - round(0.62 * L) - 18, b, g + 1)


def phone_barrow(p: Pix, g, rows: int, night: bool):
    """A phone's H1 across the rows under its words: the dragon coiled on its hoard at the right, drawn to the
    rows (see `lair`), its tail swept along the floor toward the barrow's mouth at the left, as tall as the rows
    allow with its snow drifted in."""
    x1 = p.w - SIDE - 1
    s = min(1.0, (rows - 3) / 74)
    W = round(52 * s)
    L = round(40 * s)
    lair(p, x1 - W, x1, g - rows + 3, g, night, False, x1 - round(1.62 * L), L, 62)
    mouth(p, 7, g, night, False, rows, 66)


def phone_section(p: Pix, y0, g, night: bool):
    """A phone's H2 under its words, from row y0 to the floor at row g: the dragon's great head resting on its gold
    at the right as large as the rows allow (see `head_on_gold`), and the helmet and the crown spilt from the hoard
    on the floor before it."""
    x1 = p.w - SIDE - 1
    spot = head_place(p, 60, x1, g, y0 + 2, most=72, least=24, neck=0.3)
    left = x1
    if spot:
        (left, _), _ = head_on_gold(p, *spot, x1, g, night, False, top=y0 + 2)
    pal = treasure_pal(night)
    crest = {x: g - 2 - (1 if x % 4 == 0 else 0) for x in range(SIDE + 2, left)}
    _coins(p, crest, g, night, seed=6)
    for art, x in ((HELMET, 14), (CROWN, 34)):
        if x + len(art[0]) < left - 2:
            stamp(p, x, g - len(art) - 1, art, pal)


def phone_strip(p: Pix, y0, g, night: bool):
    """A phone's H3 under its words, from row y0 to the floor at row g: the great helm raised on its heap as high
    as the rows allow, the jewelled cup before it and the buckle, the clasps, a sword and a horn on the coins
    nearest it (see `helm_on_gold`), and the coins spilt along the floor to the left with the crown and a shield
    among them."""
    x1 = p.w - SIDE - 2
    left, _ = helm_on_gold(p, x1, g, night, False, cup=True, art=GREAT_HELM, left=SIDE + 2, room=g - y0 - 1)
    pal = {**treasure_pal(night), "o": OAK[3 + (-1 if night else 0)], "O": OAK[5 + (-1 if night else 0)]}
    for art, x in ((CROWN, 14), (SHIELD, 34)):
        if clear_art(p, art, x, g - len(art) - 1) and \
                not any(p.get(x + i, g - len(art) - 1 + j) not in (None,) + tuple(GOLD)
                        for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."):
            stamp(p, x, g - len(art) - 1, art, pal)


# --------------------------------------------------------------------------- the footer's drift of coins
# The footer's mark, 19 by 17: the dragon's tail tip curled round a jewelled cup, its barb hooked over the rim,
# its spines along its curve, and the rest of it lying along the coins. Letters as for `drake_pal` and CUP.
TAIL_CUP = [
    "..........K.K......",
    ".........K5K5K.....",
    "..YYYYYYYYK54K.....",
    "..YZGGGGGgYK4K.....",
    "..YGrGgRgzY.K4K....",
    "...YgGgggY..K4hK...",
    "....YgGzY...K43K...",
    ".....YgY....K43hK..",
    ".....YGY...K443K...",
    "....YgRgY..K443hK..",
    ".....YgY..K443K....",
    "..KKKYGGgK443K.....",
    ".K5544YYYY332K.....",
    "K55444443333222KKKK",
    "K44333333222211111K",
    ".KK222111111KKKKKK.",
    "...KKKKKKKKK.......",
]
# The same mark drawn small, 9 by 13, for a footer whose words leave it only a narrow corner: the tail's barb hooked
# over the cup's rim.
TAIL_CUP_S = [
    "......K.K",
    ".....K5K5",
    "YYYYYYK5K",
    "YZGGgzK4K",
    "YGrRgYK4K",
    ".YgGzYK4K",
    "..YgY.K43",
    "...Y..K43",
    "..YgY.K43",
    ".YGGgY433",
    "KKKKKK332",
    "K4433322K",
    ".KKKKKKK.",
]
RISE = 8            # the most rows a footer's drift heaps up over its lowest where a cell leaves it room
HEAP_RUN = 14       # the fewest columns a heap rises along


def footer_mark(p: Pix, x, y, night: bool):
    """Where the footer's mark goes at the corner of its closing notes, its top at row y: drawn by `footing`
    once the footer's words are set, standing on the coins."""
    p.mark_at = (x, y)


def _room_over(p: Pix, x, top, rule: str) -> int:
    """The rows over row `top` at column x clear of every word by two rows and of anything else drawn there (a
    ruled line between cells excepted), up to RISE."""
    base = p.layers["base"]
    n = 0
    while n < RISE:
        y = top - 1 - n
        if not p.clear_of_words(x - 1, y - 2, x + 2, y + 1):
            break
        if base.get((x, y)) not in (None, rule):
            break
        n += 1
    return n


def _mark_spot(p: Pix, art, tops: dict, top: int, rule: str):
    """Where the footer's mark `art` stands, its top-left: at the corner of the notes on the coins or on the first
    line ruled under them; or wherever the coins leave it room, the right end first (after the way back up), on
    the coins or sunk into them. None where it finds no room clear of every word, a unit clear of everything
    drawn but the lines ruled along the foot, and off the lines ruled between the cells."""
    w, h = p.w, p.h
    base = p.layers["base"]
    mw, mh = len(art[0]), len(art)
    inked = [(i, j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."]
    upright = {x for x in range(w) if sum(base.get((x, y)) == rule for y in range(h)) >= 8}

    def apart(x0, y0):
        return not any(x0 - 1 <= x <= x0 + mw for x in upright) and \
            not any(base.get((x0 + i + dx, y0 + j + dy)) not in (None, rule) for i, j in inked
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    spots = []
    mark = getattr(p, "mark_at", None)
    if mark:
        mx, my = mark
        under = next((y for y in range(my + 4, h) if base.get((mx + mw // 2, y)) == rule
                      and base.get((mx + 2, y)) == rule), None)
        for x0 in (mx, mx - 2, mx + 2, mx - 4):
            if SIDE <= x0 and x0 + mw <= w - SIDE:
                spots.append((x0, min(tops[x0 + i] for i in range(mw)) + 1))
                if under is not None:
                    spots.append((x0, under))
    for x0 in range(w - SIDE - mw, SIDE, -1):
        crest = min(tops[x0 + i] for i in range(mw)) + 1
        for foot in range(crest, top + 2):
            spots.append((x0, foot))
    return next(((x0, foot - mh) for x0, foot in spots if foot - mh >= LINTEL + 1
                 and clear_art(p, art, x0, foot - mh, margin=1) and apart(x0, foot - mh)), None)


def footing(p: Pix, night: bool, rule: str):
    """A footer once its words are set: a drift of coins along its foot, two or three rows deep under the lowest
    word, heaping up in mounds wherever a cell leaves room under its words along HEAP_RUN columns or more, the
    lines ruled between the cells standing on it; the mark, the dragon's tail tip curled round a cup, at the
    corner of the notes where they leave it room, else wherever they do, standing on the coins, and drawn small
    where the words leave it only a narrow corner; the gold glinting here and there, and by night the glow of the
    gold on the stones round it."""
    w, h = p.w, p.h
    low = max((b[3] for b in p.words), default=0)
    top = min(h - 2, max(h - 4, low + 2))
    room = [_room_over(p, x, top, rule) if SIDE <= x < w - SIDE else 0 for x in range(w)]
    tops = {x: top for x in range(w)}
    x = SIDE
    while x < w - SIDE:
        if room[x] < 3:
            x += 1
            continue
        b = next((i for i in range(x, w - SIDE) if room[i] < 3), w - SIDE)
        if b - x >= HEAP_RUN:
            for i in range(x, b):
                u = (i - x + 0.5) / (b - x)
                rise = min(room[j] for j in range(max(x, i - 2), min(b, i + 3)))
                tops[i] = top - round(rise * math.sin(math.pi * u) ** 0.7)
        x = b
    base = p.layers["base"]
    for xy in [xy for xy, c in base.items() if c == rule and xy[1] >= tops.get(xy[0], h)]:
        del base[xy]
    placed = None
    for art in (TAIL_CUP, TAIL_CUP_S):
        placed = _mark_spot(p, art, tops, top, rule)
        if placed:
            break
    _coins(p, {x: t for x, t in tops.items()}, h - 1, night, seed=5, clear=True)
    if placed:
        x0, y0 = placed
        stamp(p, x0, y0, art, {**drake_pal(night), **treasure_pal(night)})
        p.marked_at = (x0, y0)
        if night:
            for gx, gy in ((x0 + 4, y0 + 3), (x0 + 3, y0 + 9)) if art is TAIL_CUP_S else \
                    ((x0 + 4, y0 + 3), (x0 + 6, y0 + 9)):
                p.px(gx, gy, X["glint"])
    glitter(p, [(x, tops[x] + 1) for x in range(SIDE + 2, w - SIDE - 2, 7)], night, False, seed=w + h)
    if night:
        for cx in range(40, w, 120):
            halo(p, cx, h, 70, 14, GOLD[3], (0.04, 0.08, 0.12), shape=True)


# --------------------------------------------------------------------------- the links
# The coin at the head of a link button, 13 by 13: Y its dark edge; Z G g its rim lit round its upper left and z q
# in shade round its lower right; f its field, where the device is struck.
LINK_COIN = [
    "....YYYYY....",
    "..YYZZGGgYY..",
    ".YZGfffffgzY.",
    ".YGfffffffzY.",
    "YZfffffffffzY",
    "YGfffffffffzY",
    "YGfffffffffzY",
    "YGfffffffffzY",
    "YGfffffffffqY",
    ".YgfffffffqY.",
    ".YzgfffffqqY.",
    "..YYzzqqqYY..",
    "....YYYYY....",
]
# The devices struck in it, 7 by 7, in the row's order: the cup, the crown, a sword and the dragon's head.
LINK_DEVICES = {
    "cup": ["ddddddd", ".ddddd.", "..ddd..", "...d...", "...d...", "..ddd..", ".ddddd."],
    "crown": ["d..d..d", "dd.d.dd", "ddddddd", "d.d.d.d", "ddddddd", ".......", "......."],
    "sword": ["...d...", "...d...", "...d...", "...d...", ".ddddd.", "...d...", "..ddd.."],
    "dragon": [".....d.", "..dddd.", ".dd.ddd", "ddddddd", "...dddd", "dddd.dd", "...dddd"],
}
LINK_ORDER = ("cup", "crown", "sword", "dragon")


def link_strap(p: Pix, w: int, seed: int, night: bool):
    """A link button finished as a strap of garnet set in gold with a gold coin at its head: the strap's gold
    rim lit along its top and dark along its foot, a strap-end of gold with a garnet set in it; and the coin over its
    head, lit round its upper rim and struck with its device, the next of `LINK_ORDER`. The kit draws the label
    after it, in pale gold on the garnet."""
    k = -1 if night else 0
    base = p.layers["base"]
    for xy in list(base):
        del base[xy]
    x0 = 8
    p.rect(x0, 3, w - x0 - 1, 9, GARNET[2])
    p.hline(x0, w - 2, 3, GARNET[3])
    p.hline(x0, w - 2, 11, GARNET[1])
    p.hline(x0, w - 1, 2, GOLD[5 + k])
    p.hline(x0, w - 1, 12, GOLD[1])
    for y in range(2, 13):
        p.px(w - 4, y, GOLD[1])
        p.px(w - 3, y, GOLD[5 + k] if y < 8 else GOLD[4 + k])
        p.px(w - 2, y, GOLD[4 + k] if y < 8 else GOLD[3 + k])
        p.px(w - 1, y, GOLD[2 + k] if 2 < y < 12 else GOLD[1])
    for y, c in ((6, GARNET[5]), (7, GARNET[4]), (8, GARNET[2])):
        p.px(w - 3, y, c)
        p.px(w - 2, y, step(c, -1))
    stamp(p, 1, 0, LINK_COIN, {"Y": GOLD[0], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "z": GOLD[2 + k],
                               "q": GOLD[1 + k], "f": GOLD[4 + k]})
    stamp(p, 4, 3, LINK_DEVICES[LINK_ORDER[seed % len(LINK_ORDER)]], {"d": GOLD[1]})


# --------------------------------------------------------------------------- the elements: gold and garnet
def fillet(p: Pix, x0, x1, y, night: bool):
    """The rule under a sheet's tag laid as a fillet of gold: a beaded wire lit along its top and dark along its
    foot, the way the goldsmith edged a mount."""
    k = -1 if night else 0
    for x in range(x0, x1):
        p.px(x, y - 1, GOLD[5 + k])
        p.px(x, y, GOLD[4 + k] if x % 2 else GOLD[2 + k])
        p.px(x, y + 1, GOLD[1])


def plaque(p: Pix, x, y, w, h, night: bool, ink: str):
    """A schematic's card as a plaque of gold: a raised rim round its face, lit along its top and left and dark
    along its foot and right; and down its left a slab of garnet in gold walls, cut in three cells, the card's
    icon (which the layout drew in `ink`, and this takes up) worked in gold on the middle one."""
    k = -1 if night else 0
    icon_y = y + (h - 7) // 2
    icon = {(xx - x - 2, yy - icon_y) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9)
            if p.get(xx, yy) == ink}
    face = GOLD[6] if not night else GOLD[0]
    p.rect(x + 2, y + 2, w - 4, h - 4, face)
    # the rim: a dark edge, then the raised rim lit along its top and left
    p.box(x, y, w, h, GOLD[1] if not night else GOLD[2])
    p.hline(x + 1, x + w - 1, y + 1, GOLD[5 + k])
    p.vline(x + 1, y + 1, y + h - 1, GOLD[5 + k])
    p.hline(x + 2, x + w - 1, y + h - 2, GOLD[3 + k])
    p.vline(x + w - 2, y + 2, y + h - 1, GOLD[3 + k])
    # the garnet slab, its walls, and the cells cut across it over and under the icon
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + 12):
            lit = (xx - x - 2) + (yy - y - 2) * 0.6
            c = GARNET[5 + k] if lit < 3 else GARNET[4 + k] if lit < 8 else GARNET[3 + k] if lit < 14 \
                else GARNET[2 + k]
            p.px(xx, yy, c)
    for yy in (icon_y - 2, icon_y + 8):
        if y + 3 < yy < y + h - 3:
            p.hline(x + 2, x + 12, yy, GOLD[4 + k])
    p.vline(x + 12, y + 2, y + h - 2, GOLD[4 + k])
    p.vline(x + 13, y + 2, y + h - 2, GOLD[1] if not night else GOLD[0])
    for (u, v) in icon:
        p.px(x + 3 + u, icon_y + v, GOLD[6 + k] if (u, v - 1) not in icon or (u - 1, v) not in icon else GOLD[4 + k])


def chain(p: Pix, cells, night: bool):
    """A schematic's wire as a chain of gold: its links by turns lying flat, a ring lit along its upper side with
    the wall showing through it, and seen on their edge, a short bar along the line; and where it turns, a garnet
    in a gold setting."""
    k = -1 if night else 0
    base = p.layers["base"]
    turns: dict = {}
    for x, y, d in cells:
        turns.setdefault((x, y), set()).add(d)
    for i, (x, y, d) in enumerate(cells):
        j = i % 8

        def at(b):
            return (x, y + b) if d == "h" else (x + b, y)
        if j in (0, 4):
            p.px(*at(0), GOLD[3 + k])
        elif j in (1, 2, 3):
            p.px(*at(-1), GOLD[5] if j == 2 else GOLD[4])
            p.px(*at(1), GOLD[1] if j == 3 else GOLD[2 + k])
            base.pop(at(0), None)
        else:
            p.px(*at(0), GOLD[4] if j != 6 else GOLD[5])
            p.px(*at(1), GOLD[2 + k])
    for (x, y), ds in turns.items():
        if len(ds) == 2:
            stamp(p, x - 1, y - 1, [".Y.", "YRY", ".Y."], {"Y": GOLD[4 + k], "R": GARNET[5 + k]})


def coin_stack(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a stack of gold coins `v` tall standing on the row `base`: coins laid one on another,
    each its rim lit over its milled edge with a dark line under it, set a little askew as a hand stacks them,
    and the top coin's face catching the light."""
    k = -1 if night else 0
    rnd = random.Random(bx * 7 + v)
    top = base - v
    y = base - 1
    n = 0
    while y >= top:
        off = rnd.choice((-1, 0, 0, 1)) if n and bw >= 5 else 0
        x0, x1 = bx + off, bx + off + bw
        rows = [("edge", y), ("mill", y - 1), ("rim", y - 2)]
        for kind, yy in rows:
            if yy < top:
                continue
            for xx in range(x0, x1):
                u = (xx - x0) / max(1, bw - 1)
                if kind == "rim":
                    c = GOLD[6 + k] if u < 0.3 else GOLD[5 + k] if u < 0.75 else GOLD[4 + k]
                elif kind == "mill":
                    c = (GOLD[4 + k] if u < 0.5 else GOLD[3 + k]) if (xx - x0) % 2 else GOLD[2 + k]
                else:
                    c = GOLD[1]
                p.px(xx, yy, c)
            p.px(x0 - 1, yy, GOLD[1] if kind != "rim" else GOLD[2 + k])
            p.px(x1, yy, GOLD[1] if kind != "rim" else GOLD[2 + k])
        y -= 3
        n += 1
    # the top coin's face, seen from a little above
    if v >= 3:
        y0 = top
        for xx in range(bx + 1, bx + bw - 1):
            p.px(xx, y0, GOLD[6 + k] if xx < bx + bw // 2 else GOLD[5 + k])
        p.px(bx + 1, y0, X["glint"] if not night else GOLD[6])


def gem_mark(p: Pix, x, y, night: bool):
    """A cut garnet in a gold setting beside the busiest week's count, its table catching the light."""
    k = -1 if night else 0
    stamp(p, x, y, ["..YYY..", ".YWRrY.", "YRRrrqY", "YrrrqqY", ".YqqqY.", "..YYY.."],
          {"Y": GOLD[4 + k], "W": GARNET[6], "R": GARNET[5 + k], "r": GARNET[4 + k], "q": GARNET[2 + k]})


def arm_ring(p: Pix, arc, night: bool):
    """The dial as a gold arm-ring: a thick rod of gold twisted along its length, its strands lit and dark by
    turns. Its ends, dragons' heads, are set once the words are (see `dragon_hand`)."""
    from ...holidays.pixel import tube
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        if abs(o) > 0.86:
            return GOLD[1]
        strand = (s * 0.9 + o * 2.4) % 3
        if strand < 0.7:
            return GOLD[2 + k] if lam < 0.5 else GOLD[3 + k]
        return GOLD[6 + k] if lam > 0.8 else GOLD[5 + k] if lam > 0.55 else GOLD[4 + k] if lam > 0.3 else GOLD[3 + k]
    tube(p, arc, 2.7, colour)


def dial_tick(p: Pix, x, y, night: bool):
    """A ring punched into the arm-ring's gold: the punch's dark hollow, lit along its lower edge."""
    k = -1 if night else 0
    p.px(x, y, GOLD[1])
    p.px(x + 1, y, GOLD[6 + k])


# An arm-ring's end, 7 by 7, a dragon's head seen from above with its snout down, laid over the end of the ring:
# its ears, its garnet eyes, its nostrils. Y its dark edge; Z G g z its gold light to dark; r its eyes; q its
# nostrils; b its ears.
TERMINAL = [
    "b.YGY.b",
    "bYZGgYb",
    "YrGGGrY",
    "YGGGggY",
    ".YGggY.",
    ".YqgqY.",
    "..YYY..",
]
# The dial's hand's head, 10 by 7, pointing right along the hand with its lit side up: its horn swept back, its
# brow, its garnet eye, its mouth. K its outline; L S s its scales light to dark; r its eye; m its mouth; b its
# horn.
HAND_HEAD = [
    "bbb.......",
    ".bbKKK....",
    ".KLLLLKK..",
    "KSSSrSSSKK",
    "KSSSSSSSSK",
    "KssssmmKK.",
    ".KKKKK....",
]


def dragon_hand(p: Pix, night: bool, accent: str):
    """The dial made the arm-ring's dragon, once every word is set: its ends finished in dragons' heads where the
    words leave them room, and the hand the layout drew in `accent` redrawn as a dragon's neck reaching from the
    hub toward the count, scaled in the dragon's blue with its belly along its lower side, its head at the end
    with its jaws parted; all of it kept clear of every word."""
    cx, cy, r = p.dial
    k = -1 if night else 0
    for ax in (cx - (r - 1.5), cx + (r - 1.5)):
        x0, y0 = round(ax) - 3, cy - 3
        if clear_art(p, TERMINAL, x0, y0, margin=0):
            stamp(p, x0, y0, TERMINAL, {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[3 + k],
                                        "z": GOLD[2 + k], "r": GARNET[5 + k], "q": GOLD[0], "b": GOLD[4 + k]})
    base = p.layers["base"]
    reach = round(r - 11)
    hand = [(x, y) for (x, y), c in base.items() if c == accent
            and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= (reach + 1) ** 2]
    if not hand:
        return
    for xy in hand:
        del base[xy]
    far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
    ux, uy = far[0] - cx, far[1] - cy
    n = math.hypot(ux, uy) or 1
    ux, uy = ux / n, uy / n
    vx, vy = uy, -ux                    # across the hand, toward its lit side, up or to the left
    if vy > 0 or (vy == 0 and vx > 0):
        vx, vy = -vx, -vy
    hw, hh = len(HAND_HEAD[0]), len(HAND_HEAD)
    pal = {"K": K, "L": DRAKE[5 + k], "S": DRAKE[4 + k], "s": DRAKE[2 + k], "r": GARNET[5 + k],
           "m": GARNET[1], "W": BONE[6 + k], "b": BONE[5 + k]}

    def head_at(x, y, tip):
        """The head's colour at canvas (x, y) with its snout's tip `tip` out from the hub, or None."""
        dx, dy = x + 0.5 - (cx + 0.5), y + 0.5 - (cy + 0.5)
        t, o = dx * ux + dy * uy, dx * vx + dy * vy
        i, j = math.floor(t - (tip - hw)), math.floor(hh / 2 - o)
        if 0 <= i < hw and 0 <= j < hh:
            return pal.get(HAND_HEAD[j][i])
        return None

    def neck_at(x, y, tip):
        dx, dy = x + 0.5 - (cx + 0.5), y + 0.5 - (cy + 0.5)
        t, o = dx * ux + dy * uy, dx * vx + dy * vy
        if not 4 <= t <= tip - hw + 3 or abs(o) > 2.1:
            return None
        if abs(o) > 1.5:
            return K
        if o < -0.5:
            return BONE[4 + k] if int(t) % 2 else BONE[3 + k]
        return DRAKE[5 + k] if o > 0.5 else DRAKE[4 + k] if int(t) % 3 else DRAKE[3 + k]
    box = [(x, y) for y in range(cy - reach - 3, cy + reach + 4) for x in range(cx - reach - 3, cx + reach + 4)]
    tip = reach + 1
    while tip > hw + 2:
        cells = [(x, y) for (x, y) in box if head_at(x, y, tip)]
        if all(p.clear_of_words(x - 1, y - 1, x + 2, y + 2) for x, y in cells):
            break
        tip -= 1
    for (x, y) in box:
        c = head_at(x, y, tip) or neck_at(x, y, tip)
        if c and p.clear_of_words(x - 1, y - 1, x + 2, y + 2):
            p.px(x, y, c)


def boss(p: Pix, cx, cy, night: bool):
    """The hub the dragon turns on: a gold boss with a garnet set in it."""
    k = -1 if night else 0
    stamp(p, cx - 3, cy - 3, [".YYYYY.", "YGZGGgY", "YZRRrgY", "YGRrqgY", "YGrqqzY", "YggzzzY", ".YYYYY."],
          {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "z": GOLD[2 + k],
           "R": GARNET[5 + k], "r": GARNET[3 + k], "q": GARNET[1 + k]})


MATTERS = ("gold", "garnet", "silver", "amber", "jet", "glass")
# A coin of the ribbon's gold, 6 by 6 with the dark between it and its neighbours: lit round its upper left.
MATTER_COIN = [".ZGg..", "ZGGgz.", "GGggz.", "Gggzq.", ".zzq..", "......"]


def matter(i: int, xx, yy, y0, y1, lift, night: bool) -> str:
    """The hoard's matters by turns along the ribbon of file types: gold coins overlapping, garnet in its cells,
    hacked silver, amber beads, jet and blue glass, each with its own grain."""
    k = -1 if night else 0
    kind = MATTERS[i % len(MATTERS)]
    v = yy - y0
    if kind == "gold":
        ch = MATTER_COIN[v % 6][(xx + 3 * ((v // 6) % 2)) % 6]
        c = GOLD[{"Z": 6, "G": 5, "g": 4, "z": 3, "q": 2, ".": 1}[ch] + (k if ch != "." else 0)]
    elif kind == "garnet":
        wall = (v % 4 == 0) or ((xx + (2 if (v // 4) % 2 else 0)) % 5 == 0)
        c = GOLD[4 + k] if wall else GARNET[4 + k] if (xx + v) % 5 < 2 else GARNET[3 + k]
    elif kind == "silver":
        c = SILVER[6 + k] if (xx * 2 + v) % 9 == 0 else SILVER[3 + k] if (xx + v * 3) % 7 == 0 else SILVER[5 + k]
    elif kind == "amber":
        bead = ((xx % 6) - 2.5) ** 2 + ((v % 6) - 2.5) ** 2
        c = AMBER[6 + k] if bead < 1.2 else AMBER[4 + k] if bead < 5 else AMBER[2 + k]
    elif kind == "jet":
        c = FLINT[5 + k] if (xx - v) % 7 == 0 else FLINT[1 + k]
    else:
        c = GLASS[5 + k] if (xx + v * 2) % 8 < 2 else GLASS[3 + k]
    try:
        return step(c, lift)
    except KeyError:
        return c


def ingot(q: Pix, ox, oy, night: bool, L="far"):
    """A counter's cell, 11 by 15, as a gold ingot stood on its end: its bevelled edges lit along its top and left
    and in shade along its foot and right, round a calm face for the numeral, a dark edge round it all. It lies on a
    layer under the drawing's own, so its numeral is set over it whatever its colour."""
    k = -1 if night else 0
    for yy in range(15):
        for xx in range(11):
            if xx in (0, 10) or yy in (0, 14):
                c = GOLD[0]
            elif yy == 1 or xx == 1:
                c = GOLD[6 + k] if yy == 1 and xx > 1 else GOLD[5 + k]
            elif yy == 13 or xx == 9:
                c = GOLD[2 + k]
            else:
                c = GOLD[4 + k]
            q.px(ox + xx, oy + yy, c, L)


TRAIL_COIN = [".ZG.", "ZGgz", ".zq."]


def coin_trail(p: Pix, x0, x1, y, night: bool):
    """The time line as a trail of gold coins spilt up to today: coins lying flat, each overlapping the last and
    by turns a row higher and a row lower, each lit along its upper rim."""
    k = -1 if night else 0
    pal = {"Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "z": GOLD[2 + k], "q": GOLD[1]}
    if x1 - x0 < 4:
        stamp(p, x0, y - 1, TRAIL_COIN, pal)
        return
    for i, x in enumerate(range(x0, x1 - 3, 3)):
        stamp(p, x, y - 1 - (i % 2), TRAIL_COIN, pal)


def coin_column(p: Pix, x, y0, y1, night: bool):
    """A phone's time line, run down its left from row y0 to row y1, as a trail of gold coins spilt down it, each
    overlapping the one above and by turns a column to the left and to the right."""
    k = -1 if night else 0
    pal = {"Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "z": GOLD[2 + k], "q": GOLD[1]}
    for i, y in enumerate(range(y0, y1 - 1, 2)):
        stamp(p, x - 2 + (i % 2), y, TRAIL_COIN, pal)


GEMS = {
    "big": ["...DDD...", ".DDYYYDD.", ".DYWRrYD.", "DYRRrrrYD", "DYRrrrqYD", "DYrrrqqYD", ".DYrqqYD.",
            ".DDYYYDD.", "...DDD..."],
    "major": ["..DDD..", ".DYYYD.", "DYWRrYD", "DYRrqYD", "DYrqqYD", ".DYYYD.", "..DDD.."],
    "minor": [".DDD.", "DYLYD", "DLlmD", "DYmYD", ".DDD."],
    "next": ["..DDD..", ".DYYYD.", "DY...YD", "DY...YD", "DY...YD", ".DYYYD.", "..DDD.."],
}


def release_gem(p: Pix, x, gy, kind: str, night: bool):
    """A release set on the trail of coins as a gem in its gold setting: a great garnet for a big release, a garnet
    for a release, a bead of blue glass for a patch, an empty setting for one still to come, and a gold crown
    standing on the trail for the hoard's founding."""
    k = -1 if night else 0
    if kind == "made":
        stamp(p, x - 5, gy - 7, CROWN, treasure_pal(night))
        return
    pal = {"Y": GOLD[4 + k], "D": GOLD[1], "W": GARNET[6], "R": GARNET[5 + k], "r": GARNET[4 + k],
           "q": GARNET[2 + k], "L": GLASS[6 + k], "l": GLASS[4 + k], "m": GLASS[2 + k]}
    art = GEMS.get(kind, GEMS["major"])
    stamp(p, x - len(art[0]) // 2, gy - len(art) // 2, art, pal)


# The dragon's eye at today's end of the trail, 13 by 9, in a patch of its scales: its brow over it, the gold
# iris round a black slit, the light in its corner. K the lids; L S s the scales light to dark; Z G g o the
# iris light to dark; P the slit; W the light.
EYE = [
    "...LLLSSs....",
    ".LLSSSSSSss..",
    "LSSKKKKKKSss.",
    "SSKZGgPggoKss",
    "SKGWGgPgggoKs",
    "SSKGggPgooKss",
    ".sSKKKKKKKss.",
    "..sssssssss..",
    ".....sss.....",
]


def dragon_eye(p: Pix, x, y, night: bool):
    """Today's mark at the end of the trail: the dragon's eye in a patch of its scales, open and watching."""
    k = -1 if night else 0
    stamp(p, x - 6, y - 4, EYE, {"L": DRAKE[5 + k], "S": DRAKE[3 + k], "s": DRAKE[2 + k], "K": DRAKE[0],
                                 "Z": GOLD[6], "G": GOLD[5 + k], "g": GOLD[4 + k], "o": GOLD[2 + k], "P": DRAKE[0],
                                 "W": X["glint"]})


ENAMELS = ("garnet", "glass", "emerald", "wing", "flint")
# The heads stamped on a bracteate's field in gold relief, 13 by 13, facing left as on the northern medallions: a
# king in his diadem with his hair rolled behind; a warrior in his helmet; a woman with her hair knotted; a bearded
# elder. H the relief lit, h in shade, z its deep lines, D a diadem or a crest, x the eye, sunk.
HEADS = (
    [".....DDDD....", "....hHHHHh...", "...hHHHHHhh..", "..HHHHHHhhzh.", "..HxHHHHhzhh.", ".HHHHHHhhzh..",
     "HHHHHHHhzhh..", ".zHHHHHhhzh..", ".HHHHHHhh....", "..HHHHhh.....", "..zHHHH......", "...HHHHH....."],
    ["...hDDDh.....", "..hHHHHHh....", ".hHHHHHHHh...", ".zzzzzzzzz...", "..HxHHHhh....", ".HHHHHhhh....",
     "HHHHHHhhh....", ".zHHHHhh.....", ".HHHHHhh.....", "..HHHhh......", "..HHHHH......", ".HHHHHHH....."],
    ["....hhhh.hh..", "...hHHHHhHHh.", "..hHHHHHhhHh.", "..HHHHHHhhh..", "..HxHHHHhzh..", ".HHHHHHhhzh..",
     "HHHHHHhhzh...", ".zHHHHhhzh...", ".HHHHHhhzh...", "..HHHhhzhh...", "...HHHzhh....", "...HHHHH....."],
    [".....hhh.....", "....hHHHhh...", "...HHHHHHhh..", "..HHHHHHhhh..", "..HxHHHHhhh..", ".HHHHHHhhh...",
     "HHHHHHhhh....", ".zhzhHHhh....", ".hzhzhHh.....", ".zhzhzh......", "..hzhz.......", "...hHHHH....."],
)


def _medallion() -> list:
    """A bracteate's disc, 17 by 17: its rim of beads (B and b lit, c and C in shade), the dark wire inside it
    (w) and the field (e)."""
    rows = []
    for y in range(17):
        row = ""
        for x in range(17):
            d = math.hypot(x - 8, y - 8)
            a = math.degrees(math.atan2(y - 8, x - 8)) % 360
            if d > 8.6:
                row += "."
            elif d > 7.3:
                bead = int(a // 20) % 2 == 0
                row += ("B" if bead else "b") if 135 <= a <= 315 else ("c" if bead else "C")
            elif d > 6.4:
                row += "w"
            else:
                row += "e"
        rows.append(row)
    return rows


MEDALLION = _medallion()


def bracteate(p: Pix, cx, cy, person: dict, night: bool):
    """A contributor as a gold bracteate, the northern medallion, 17 wide on its loop: a beaded gold rim round a
    field enamelled in the person's own colour, and on it their head in gold relief, facing left (a king in his
    diadem, a warrior in his helmet, a woman, an elder; which, and the colour, follow from their name). A bot's
    bracteate is stamped with its icon instead."""
    from ...holidays.pixel import GLYPHS
    k = -1 if night else 0
    name = str(person.get("name", ""))
    mark = sum((j + 1) * ord(ch) for j, ch in enumerate(name))
    enamel = RAMP[ENAMELS[mark % len(ENAMELS)]]
    x0, y0 = cx - 8, cy - 8
    stamp(p, cx - 2, y0 - 3, [".YY.", "Y..Y", "YGgY"], {"Y": GOLD[1], "G": GOLD[5 + k], "g": GOLD[3 + k]})
    stamp(p, x0, y0, MEDALLION, {"B": GOLD[6 + k], "b": GOLD[4 + k], "c": GOLD[4 + k], "C": GOLD[2 + k],
                                 "w": GOLD[1], "e": enamel[2 + k]})
    if not person.get("initials"):
        icon = GLYPHS[7].get(person.get("icon") or "gear", GLYPHS[7]["gear"])
        stamp(p, x0 + 6, y0 + 6, icon, {"#": GOLD[1]})
        stamp(p, x0 + 5, y0 + 5, icon, {"#": GOLD[5 + k]})
        return
    head = HEADS[(mark // len(ENAMELS)) % len(HEADS)]
    stamp(p, x0 + 2, y0 + 2, head, {"H": GOLD[5 + k], "h": GOLD[3 + k], "z": GOLD[2 + k], "D": GOLD[6 + k],
                                    "x": GOLD[1]})


def channel_bar(p: Pix, x, y, w, fill, night: bool):
    """A contributor's share as gold run into a channel cut in garnet as far as their commits reach, the gold lit
    along its top and its end rounded."""
    k = -1 if night else 0
    p.box(x, y, w + 2, 4, GOLD[1] if not night else GOLD[2])
    p.hline(x + 1, x + w + 1, y + 1, GARNET[2 + k])
    p.hline(x + 1, x + w + 1, y + 2, GARNET[1 + k])
    p.hline(x + 1, x + 1 + fill, y + 1, GOLD[6 + k])
    p.hline(x + 1, x + 1 + fill, y + 2, GOLD[4 + k])
    if fill >= 2:
        p.px(x + fill, y + 2, GOLD[2 + k])


def brooch(p: Pix, cx, cy, r0, r1, night: bool):
    """The certificate's seal as a disc brooch of gold and garnet: round the seal's face a ring of garnet cells,
    every other one stepped, set in gold walls with the gold foil glinting through them, inside a beaded gold rim
    lit along its upper left; and four bosses of gold set at the quarters."""
    k = -1 if night else 0
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d < r0 - 0.5 or d > r1 + 0.5:
                continue
            a = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            lit = (-dx * 0.63 - dy * 0.78) / max(d, 1.0)
            if d > r1 - 1.0:
                bead = int(a / 6) % 2 == 0
                c = (GOLD[6 + k] if bead else GOLD[4 + k]) if lit > -0.2 else (GOLD[4 + k] if bead else GOLD[2 + k])
            elif d > r1 - 2.0:
                c = GOLD[1]
            elif d < r0 + 1.0:
                c = GOLD[5 + k] if lit > 0 else GOLD[3 + k]
            else:
                cell = int(a // 15)
                mid = (r0 + r1) / 2
                wall = (a % 15) < 1.6 or (cell % 2 and abs(d - mid) < 0.55 and (a % 15) < 9)
                if wall:
                    c = GOLD[5 + k] if lit > 0 else GOLD[3 + k]
                else:
                    c = GARNET[5 + k] if lit > 0.45 else GARNET[4 + k] if lit > -0.1 else GARNET[3 + k] \
                        if lit > -0.6 else GARNET[2 + k]
                    if (x * 3 + y * 5) % 11 == 0 and lit > -0.4:
                        c = GARNET[6]
            p.px(x, y, c)
    for a in (45, 135, 225, 315):
        bx = cx + (r0 + r1) / 2 * math.cos(math.radians(a))
        by = cy + (r0 + r1) / 2 * math.sin(math.radians(a))
        stamp(p, round(bx) - 2, round(by) - 2, [".YYY.", "YZGgY", "YGgzY", "YgzzY", ".YYY."],
              {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[3 + k], "z": GOLD[2 + k]})


def keystone(p: Pix, x, y, night: bool):
    """The mark at the brooch's foot: a great garnet cut to a point and set in gold, hanging from its rim."""
    k = -1 if night else 0
    stamp(p, x + 2, y, ["YYYYYYYYY", "YWRRrrrqY", ".YRrrrqY.", "..YrrqY..", "...YqY...", "....Y...."],
          {"Y": GOLD[4 + k], "W": GARNET[6], "R": GARNET[5 + k], "r": GARNET[4 + k], "q": GARNET[2 + k]})


def gold_face(p: Pix, cx, cy, r, night: bool, fill: str):
    """The seal's face made gold: every pixel of the disc still in the card's `fill` laid in pale gold by day and
    in the gold's deep shadow by night, the words and the check over it left as they are."""
    face = GOLD[6] if not night else GOLD[0]
    base = p.layers["base"]
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if base.get((x, y)) == fill and math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r:
                base[(x, y)] = face


def chest_lid(p: Pix, night: bool):
    """A placard as the lid of a treasure chest over the whole card: boards of ash running along it with their
    grain and the dark joints between them, bound round its edge with a band of iron riveted down with gilt nails,
    and an angle of gilt bronze set with a garnet at each corner. By day the ash is pale in the snowlight; by night
    it lies dark."""
    k = -1 if night else 0
    w, h = p.w, p.h
    p.sheet, p.night = "pl", night
    cells = {}
    for y in range(30):
        for x in range(64):
            v = y % 10
            if v == 9:
                c = SAND[3] if not night else OAK[0]
            elif v == 0:
                c = SAND[6] if not night else OAK[2]
            else:
                grain = (x * 5 + (y // 10) * 23 + int(3 * math.sin(x * 0.21 + y))) % 29
                c = (SAND[4] if grain < 3 else SAND[5]) if not night else (OAK[2] if grain < 3 else OAK[1])
            cells[(x, y)] = c
    pid = tile(p, f"ash{'n' if night else 'd'}", 64, 30, cells, y=2)
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{pid})"/>')
    I = IRON
    for x in range(w):
        for y in (0, 1, 2, 3, h - 4, h - 3, h - 2, h - 1):
            j = y if y < 4 else y - (h - 4)
            p.px(x, y, (I[1], I[5 + k], I[4 + k], I[2 + k])[j] if y < 4 else (I[4 + k], I[3 + k], I[2 + k], I[1])[j])
    for y in range(4, h - 4):
        for x in (0, 1, 2, 3, w - 4, w - 3, w - 2, w - 1):
            j = x if x < 4 else x - (w - 4)
            p.px(x, y, (I[1], I[5 + k], I[4 + k], I[2 + k])[j] if x < 4 else (I[4 + k], I[3 + k], I[2 + k], I[1])[j])
    for x in range(4, w - 4):
        p.apx(x, 4, X["shade_ink"], 0.35)
    for y in range(5, h - 4):
        p.apx(4, y, X["shade_ink"], 0.25)
    nail = {"Z": GOLD[6 + k], "z": GOLD[3 + k]}
    for x in range(16, w - 14, 18):
        stamp(p, x, 1, ["Z.", ".z"], nail)
        stamp(p, x, h - 3, ["Z.", ".z"], nail)
    for y in range(16, h - 14, 18):
        stamp(p, 1, y, ["Z.", ".z"], nail)
        stamp(p, w - 3, y, ["Z.", ".z"], nail)
    angle = ["YYYYYYY", "YZGGGgY", "YGRrgY.", "YGrgY..", "YGgY...", "YgY....", "YY....."]
    pal = {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[3 + k], "R": GARNET[5 + k],
           "r": GARNET[3 + k]}
    for fx, fy in ((False, False), (True, False), (False, True), (True, True)):
        art = [row[::-1] for row in angle] if fx else angle
        art = art[::-1] if fy else art
        stamp(p, w - 7 if fx else 0, h - 7 if fy else 0, art, pal)


def mount(p: Pix, x, y, night: bool):
    """The mark beside a placard's title: a round mount of gold cloisonne nailed to the lid, its garnets set in a
    stepped cross round a gold boss, inside a lit gold rim."""
    k = -1 if night else 0
    art = [
        "...YYYYY...",
        ".YYZGGGgYY.",
        ".YRRGgGrqY.",
        "YZRrYGYrqgY",
        "YGGYZGgYggY",
        "YGgGGgzzgzY",
        "YGrqYgYqqzY",
        ".YrqGzGqqY.",
        ".YYgzzzzYY.",
        "...YYYYY...",
    ]
    stamp(p, x, y, art, {"Y": GOLD[1], "Z": GOLD[6 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "z": GOLD[2 + k],
                         "R": GARNET[5 + k], "r": GARNET[4 + k], "q": GARNET[2 + k]})


def helm_heap(p: Pix, x, y, night: bool):
    """The schematic's ornament, 24 by 22, in a free corner: the helmet of the ship burial set on a little heap of
    coins, a sword thrust in beside it."""
    foot = y + 21
    crest = heap(p, x, x + 24, foot, 7, night, seed=x, peak=0.45, gems=True)
    treasure(p, x + 19, crest[x + 21] - 9, SWORD, night)
    treasure(p, x + 4, crest[x + 10] - len(HELMET) + 3, HELMET, night)
