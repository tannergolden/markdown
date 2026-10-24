# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Subway set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is a station wall of glazed subway tile laid in a running bond: pale celadon by day, each tile catching
the light along its top, and teal-black after hours, when the station empties. A border of bottle-green tile runs down
each side, a band of terracotta and ochre tile along the foot, and along a header's top a mosaic frieze of ochre with
lozenges of terracotta and cobalt, stopping either side of the month's mark. Titles are the station's name laid in
mosaic, tessera by tessera in terracotta set in dark grout, each tessera's glaze catching the light at its upper left
and the letters' shadow cast on the tile; after hours the fluorescent light glints on them. Headers stand under the
light from the street, falling through the gratings in shafts across the wall: on the platform, the tunnel's mouth in
its tall mosaic arch at the left, a signal burning in the dark of it, and the train coming up the tunnel head on, its
two headlights blazing and its sign reading in the code's own glyphs; at the right a fan turning on a steel column,
the station clock, a poster lit from behind, a bench, a fluorescent tube hanging overhead that flickers after hours,
and a lone figure in a long dark coat waiting at the yellow line, his coat stirring in the train's wind as a sheet of
newspaper tumbles along the platform toward him; the stair down from the street, walled in green tile, its arched way
out in the July sun, green globes on its newel posts and a woman in a red summer dress coming down it; and the token
booth under its lit sign, the clerk at its glass beside the turnstile.

The footers stand on the platform's edge, rising into a dado of tile where the cells leave room, with the green globes
after their last cell; the links' icons, the badges' frieze and every element's touch are cut from the same tile,
mosaic, enamel, steel and phosphor. Everything is shaded from the one light in the upper left on the set's own ramps,
and every light is the hand's phosphor. A drawing made lighter still keeps every piece of its scene and all its
motion, thinning only texture no one misses at 1x: the light from the street laid in one band, the headlights' flare
shorter and their glows in fewer rings, the poster's streams shorter, and the title's tesserae in one tone."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, Pix, fold, num
from .. import rain
from .palette import C, RAMP, TILE_H, TILE_W, X

TERRA, OCHRE, COBALT, BOTTLE = RAMP["terra"], RAMP["ochre"], RAMP["cobalt"], RAMP["bottle"]
STEEL, TUNNEL, CONCRETE, YELLOW, OAK = RAMP["steel"], RAMP["tunnel"], RAMP["concrete"], RAMP["yellow"], RAMP["oak"]
COAT, ENAMEL, FLAME, GLAZE = RAMP["coat"], RAMP["enamel"], RAMP["flame"], RAMP["glaze"]
EDGE = 4          # the frame's width down each side and along the foot
TOP = 3           # the row the wall's first course of tile starts on, under the cornice
COURSE = TILE_H + 1
LOOP = 4.0        # seconds the waiting man's coat takes to stir and settle: within the hand's four to eight
TICK = 60.0       # seconds the clock's second hand takes to go round, a fifth of a minute a step
ARRIVE = 8.0      # seconds the train takes to come up the tunnel and stand at its mouth, round and round



def ramp_at(ramp: list, i: int) -> str:
    """A ramp's tone `i`, held to the ramp's ends, so a night's darkening never wraps round to its lightest."""
    return ramp[max(0, min(len(ramp) - 1, i))]

# --------------------------------------------------------------------------- the wall
def wall(p: Pix, night: bool, uid: str = "p"):
    """The sheet: a wall of glazed subway tile laid in a running bond, each course offset half a tile from the one
    over it, every tile's top row catching the light and the grout between them; celadon by day and teal-black after
    hours. Laid as a pattern of two courses."""
    w, h = p.w, p.h
    face, lit, grout = (C["tile_n"], C["tile_lit_n"], C["grout_n"]) if night else (C["tile"], C["tile_lit"], C["grout"])
    pw = 2 * (TILE_W + 1)
    p.under.append(f'<rect width="{w}" height="{h}" fill="{face}"/>')
    half = (TILE_W + 1) // 2
    p.defs.append(f'<pattern id="{uid}t" y="{TOP}" width="{pw}" height="{2 * COURSE}" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{lit}" d="M0 .5h{TILE_W}m1 0h{TILE_W}M0 {COURSE + .5}h{half}m1 0h{TILE_W}m1 0h'
                  f'{TILE_W - half}"/><path stroke="{grout}" d="M{TILE_W + .5} 0v{TILE_H}M{pw - .5} 0v{TILE_H}'
                  f'M0 {TILE_H + .5}h{pw}M{half + .5} {COURSE}v{TILE_H}M{half + TILE_W + 1.5} {COURSE}v{TILE_H}'
                  f'M0 {COURSE + TILE_H + .5}h{pw}"/></pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}t)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: a tile's lit top row, its glaze, or the grout under a course."""
    r = (y - TOP) % COURSE
    if r == 0:
        return C["tile_lit_n"] if night else C["tile_lit"]
    if r == TILE_H:
        return C["grout_n"] if night else C["grout"]
    return C["tile_n"] if night else C["tile"]


# --------------------------------------------------------------------------- the frame
def frame(p: Pix, night: bool, header: bool = False, foot: bool = True):
    """The border: a column of bottle-green bullnose tile down each side, its glaze lit along its left and a joint
    every few rows; a cornice of the same green along the top; and along the foot a band of terracotta and ochre tile
    in a chequer under a lit edge of ochre. Without its `foot`, as a footer has it, the border leaves the band to the
    footing, which lays it under the platform's edge (see `footing`)."""
    w, h = p.w, p.h
    k = -1 if night else 0
    B = BOTTLE
    for x0 in (0, w - EDGE):
        p.vline(x0, 0, h, B[0])
        p.vline(x0 + 1, 0, h, ramp_at(B, 5 + k))
        p.vline(x0 + 2, 0, h, ramp_at(B, 3 + k))
        p.vline(x0 + 3, 0, h, ramp_at(B, 2 + k))
    uid = "fr"
    for n, x0 in enumerate((0, w - EDGE)):
        p.defs.append(f'<pattern id="{uid}s{n}" x="{x0}" y="2" width="4" height="7" patternUnits="userSpaceOnUse">'
                      f'<path stroke="{ramp_at(B, 1 + k)}" d="M1 .5h3"/>'
                      f'<path stroke="{ramp_at(B, 6 + k)}" d="M1 1.5h1"/></pattern>')
        p.shapes["base"].append(f'<rect x="{x0}" y="2" width="4" height="{h - 6}" fill="url(#{uid}s{n})"/>')
    p.hline(0, w, 0, B[0])
    p.hline(1, w - 1, 1, ramp_at(B, 4 + k))
    p.hline(1, w - 1, 2, ramp_at(B, 2 + k))
    if not foot:
        p.hline(0, EDGE, h - 1, TERRA[0])
        p.hline(w - EDGE, w, h - 1, TERRA[0])
        return
    p.hline(EDGE, w - EDGE, h - 4, ramp_at(OCHRE, 5 + k))
    T, O = TERRA, OCHRE
    p.defs.append(f'<pattern id="{uid}c" x="{EDGE}" y="{h - 3}" width="6" height="2" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{ramp_at(T, 3 + k)}" d="M0 .5h3M3 1.5h3"/>'
                  f'<path stroke="{ramp_at(O, 3 + k)}" d="M3 .5h3M0 1.5h3"/>'
                  f'<path stroke="{ramp_at(T, 5 + k)}" d="M0 .5h1"/><path stroke="{ramp_at(O, 5 + k)}" d="M3 .5h1"/>'
                  f'</pattern>')
    p.shapes["base"].append(f'<rect x="{EDGE}" y="{h - 3}" width="{w - 2 * EDGE}" height="2" fill="url(#{uid}c)"/>')
    p.hline(0, w, h - 1, T[0])


# --------------------------------------------------------------------------- the frieze
LOZENGE = ["...##...", "..####..", "..####..", "...##..."]   # a lozenge of the frieze, on its ochre field


def frieze(p: Pix, x0, x1, night: bool, box, marked: bool, top: int = 4):
    """The mosaic frieze along a header's top, from x0 to x1, six rows deep: a field of ochre between two lines of
    bottle green, set with lozenges of terracotta and cobalt by turns, each lozenge lit at its upper left; it stops
    either side of the month's mark, two units clear, against a green tile end, and runs on unbroken with no mark.
    Laid as a pattern of two lozenges."""
    a, _, b, _ = box
    runs = [(x0, a - 1), (b + 1, x1)] if marked else [(x0, x1)]
    k = -2 if night else 0
    O, T, Co, B = OCHRE, TERRA, COBALT, BOTTLE
    cols: dict = {}
    for i, colour in enumerate(((ramp_at(T, 3 + k), ramp_at(T, 5 + k)), (ramp_at(Co, 3 + k), ramp_at(Co, 5 + k)))):
        base, lit = colour
        for j, row in enumerate(LOZENGE):
            for c, ch in enumerate(row):
                if ch == "#":
                    first = row.index("#")
                    tone = lit if (c == first and j < 2) else base
                    cols.setdefault(tone, []).append(f"M{i * 8 + c} {j}h1v1h-1z")
    body = "".join(f'<path fill="{col}" d="{"".join(ds)}"/>' for col, ds in cols.items())
    pid = "fz"
    p.defs.append(f'<pattern id="{pid}" x="{x0}" y="{top + 1}" width="16" height="4" patternUnits="userSpaceOnUse">'
                  f'<rect width="16" height="4" fill="{ramp_at(O, 4 + k)}"/>{body}</pattern>')
    for r0, r1 in runs:
        p.hline(r0, r1, top, ramp_at(B, 4 + k))
        p.shapes["base"].append(f'<rect x="{r0}" y="{top + 1}" width="{r1 - r0}" height="4" fill="url(#{pid})"/>')
        p.hline(r0, r1, top + 5, ramp_at(B, 2 + k))
        p.hline(r0, r1, top + 6, ramp_at(B, 1 + k))
        for end in (r0, r1 - 2):
            p.rect(end, top, 2, 7, ramp_at(B, 3 + k))
            p.vline(end, top, top + 7, ramp_at(B, 5 + k))


# --------------------------------------------------------------------------- the titles
TONES = (3, 3, 4, 3, 2, 3, 4, 3, 3)       # each tessera's tone in a block of three by three, laid by hand


def mosaic(p: Pix, scale: int, night: bool) -> str:
    """The pattern the title's letters are laid in: tesserae of terracotta three by three, a font unit each, the dark
    grout between them along each one's right and foot, every tessera a tone of its own as a hand lays them (`TONES`),
    its glaze catching the light at its upper left. After hours the tesserae are a tone paler in the fluorescent light.
    Set in the face's units, a tile of three by three, so it repeats down and along every letter. A drawing made
    lighter lays every tessera in the one tone, still lit and grouted."""
    pid = f"ms{scale}{'n' if night else 'd'}"
    if ("pattern", pid) in p.syms:
        return pid
    k = 1 if night else 0
    n = 3 * scale
    face = scale - 1 if scale >= 3 else scale
    base = TERRA[3 + k]
    by: dict = {}
    for ty in range(3):
        for tx in range(3):
            t = (3 if p.lite else TONES[ty * 3 + tx]) + k
            x0, y0 = tx * scale, ty * scale
            if TERRA[t] != base:
                by.setdefault(TERRA[t], []).append(f"M{x0} {y0}h{face}v{face}h-{face}z")
            by.setdefault(TERRA[min(6, t + 2)], []).append(f"M{x0} {y0}h1v1h-1z")
            if scale == 2:
                by.setdefault(TERRA[1 + k], []).append(f"M{x0 + 1} {y0 + 1}h1v1h-1z")
    if scale >= 3:
        grout = TERRA[0] if night else TERRA[1]
        by.setdefault(grout, []).extend(f"M0 {i * scale + face}h{n}v1h-{n}zM{i * scale + face} 0h1v{n}h-1z"
                                        for i in range(3))
    body = f'<rect width="{n}" height="{n}" fill="{base}"/>' + "".join(
        f'<path fill="{col}" d="{"".join(ds)}"/>' for col, ds in by.items())
    p.defs.append(f'<pattern id="{pid}" width="3" height="3" patternUnits="userSpaceOnUse">'
                  f'<g transform="scale({num(1 / scale)})">{body}</g></pattern>')
    p.syms[("pattern", pid)] = pid
    return pid


RING = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))


def _at(dx, dy) -> str:
    return (f' x="{dx}"' if dx else "") + (f' y="{dy}"' if dy else "")


def mosaic_title(p: Pix, x, y, s, scale, night: bool) -> int:
    """A title laid in mosaic: the line's letters set once from the face's own glyphs, their shadow cast down and right
    on the tile, a ring of grout laid round them as the line moved a unit every way, and over it the letters in
    tesserae (see `mosaic`). After hours a
    tessera here and there glints with the fluorescent light. A long title costs little more than a short one.
    Returns its width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    cx = x
    placed = []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    rows = max((len(glyphs[ch][1]) for ch, _ in placed), default=0)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    if not placed:
        return max(0, w)
    tid = f"mt{len(p.defs)}"
    letters = "".join(f'<use href="#{p.syms[("glyph", "57", ch)]}"'
                      + (f' x="{num((gx - x) / scale)}"' if gx > x else "") + "/>" for ch, gx in placed)
    p.defs.append(f'<g id="{tid}" transform="translate({x} {y}) scale({scale})">{letters}</g>')
    grout = TERRA[0] if night else TERRA[1]
    cast = f'<use href="#{tid}" x="2" y="3" stroke="{X["shade_ink"]}" stroke-opacity="{".5" if night else ".22"}"/>'
    ring = f'<g stroke="{grout}">' + "".join(f'<use href="#{tid}"{_at(dx, dy)}/>' for dx, dy in RING) + "</g>"
    body = f'<use href="#{tid}" stroke="url(#{mosaic(p, scale, night)})"/>'
    p.raw(0.1, cast + ring + body, cast + ring + body)
    if night and scale >= 3:
        rnd = random.Random(len(s) * 3 + scale)
        for i, (ch, gx) in enumerate(placed):
            cells = [(c, r) for r, cs in enumerate(glyphs[ch][1]) for c in cs]
            c, r = cells[rnd.randrange(len(cells))]
            p.px(gx + c * scale, y + r * scale, FLAME[6], p.twinkle(i))
    return w


# --------------------------------------------------------------------------- the tunnel and the train
def _arch(cx, top, r, x0, x1, g) -> set:
    """The cells of an arched opening: a half circle of radius r over upright sides from x0 to x1, down to row g."""
    out = set()
    spring = top + r
    for y in range(top, g + 1):
        for x in range(x0, x1):
            if y >= spring or (x + 0.5 - cx) ** 2 + (y + 0.5 - spring) ** 2 <= r * r:
                out.add((x, y))
    return out


def tunnel(p: Pix, x0, x1, top, g, night: bool) -> set:
    """The tunnel's mouth at the end of the platform, an arch from x0 to x1 with its crown at row `top`: the dark
    going back into it, the station's light catching two of its rings, and round it a band of mosaic three tesserae
    deep, voussoirs of ochre and terracotta by turns, each lit at its upper left, with a keystone of cobalt and a band
    of green at its springing. Returns the cells of its opening."""
    r = (x1 - x0) / 2
    cx = x0 + r
    hole = _arch(cx, top, r, x0, x1, g)
    rim = _arch(cx, top - 3, r + 3, x0 - 3, x1 + 3, g) - hole
    k = -1 if night else 0
    for (x, y) in hole:
        p.px(x, y, TUNNEL[2])
    for depth, band, beyond in ((3, 4, 1), (8, 3, 0)):
        ring = _arch(cx, top + depth, r - depth, round(x0 + depth), round(x1 - depth), g)
        inner = _arch(cx, top + depth + 1, r - depth - 1, round(x0 + depth + 1), round(x1 - depth - 1), g)
        for (x, y) in ring - inner:
            p.px(x, y, TUNNEL[band])
        for (x, y) in inner:
            p.px(x, y, TUNNEL[beyond])
    spring = top + r
    for (x, y) in rim:
        ang = math.atan2(y + 0.5 - spring, x + 0.5 - cx)
        n = int((ang + math.pi) / math.pi * 13)
        key = abs(x + 0.5 - cx) < 2.1 and y < top + 1
        if key:
            base = ramp_at(COBALT, 3 + k)
        elif y < spring:
            base = (ramp_at(OCHRE, 4 + k), ramp_at(TERRA, 3 + k))[n % 2]
        else:
            base = ramp_at(TERRA, 2 + k)
        edge = (x - 1, y) not in rim and (x - 1, y) not in hole or (x, y - 1) not in rim and (x, y - 1) not in hole
        p.px(x, y, step_up(base) if edge else base)
    for x in range(x0 - 3, x1 + 3):
        if (x, spring) in rim:
            p.px(x, spring, ramp_at(BOTTLE, 3 + k))
    return hole


def step_up(c: str) -> str:
    """The tone a step lighter than `c` on its own ramp, for a glaze's lit edge."""
    for ramp in (OCHRE, TERRA, COBALT, BOTTLE):
        if c in ramp:
            return ramp[min(6, ramp.index(c) + 1)]
    return c


def train(p: Pix, x, top, w, h, night: bool, L: str = "base") -> list:
    """The train coming out of the tunnel toward the platform, seen head on, its face `w` wide and `h` tall with its
    top-left at (x, top), on layer `L`: stainless steel rounded over its roof and lit down its left, its sign over the
    cab reading in the code's glyphs, the cab's two windows either side of the door's tall window, marker lights at its
    corners, its two headlights blazing phosphor low down, and the anticlimber across its foot. A face drawn small, far
    back in the tunnel, keeps only what still reads at its size. Returns where the headlights are."""
    k = -2 if night else 0
    S = STEEL
    r = 3 if w >= 20 else 2 if w >= 12 else 1
    cells = {}
    for j in range(h):
        for i in range(w):
            if j < r and ((i < r and (r - i - 0.5) ** 2 + (r - j - 0.5) ** 2 > r * r)
                          or (i >= w - r and (i - (w - 1 - r) - 0.5) ** 2 + (r - j - 0.5) ** 2 > r * r)):
                continue
            t = i / (w - 1)
            tone = 6 if j == 0 else 5 if t < 0.12 else 2 if t > 0.86 else 3 if t > 0.7 else 4
            cells[(i, j)] = ramp_at(S, tone + k)
    for (i, j) in list(cells):
        if any((i + dx, j + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, -1))):
            cells[(i, j)] = S[0]
    sx0, sx1, sy0, sy1 = round(w * 0.3), round(w * 0.7), max(1, round(h * 0.08)), max(2, round(h * 0.21))
    for j in range(sy0, sy1):
        for i in range(sx0, sx1):
            cells[(i, j)] = TUNNEL[1]
    wy0, wy1 = round(h * 0.27), round(h * 0.52)
    for (a, b) in ((round(w * 0.09), round(w * 0.36)), (round(w * 0.64), round(w * 0.91))):
        for j in range(wy0, wy1):
            for i in range(a, b):
                edge = (j == wy0 or i == a or i == b - 1) and w >= 14
                lit = (i - a) + (j - wy0) < 3
                if night:
                    c = S[0] if edge else FLAME[2] if lit else FLAME[1]
                else:
                    c = S[0] if edge else COBALT[4] if lit else COBALT[1]
                cells[(i, j)] = c
    da, db = round(w * 0.39), round(w * 0.61)
    if w >= 14:
        for j in range(round(h * 0.2), round(h * 0.9)):
            cells[(da, j)] = S[0]
            cells[(db, j)] = S[0]
        for j in range(round(h * 0.25), round(h * 0.6)):
            for i in range(da + 2, db - 1):
                lit = (i - da) + (j - round(h * 0.25)) < 4
                cells[(i, j)] = (FLAME[2] if lit else FLAME[1]) if night else (COBALT[4] if lit else COBALT[2])
    by = round(h * 0.88)
    for j in range(by, h):
        for i in range(1, w - 1):
            cells[(i, j)] = ramp_at(S, 3 + k) if j == by else S[1] if (i + j) % 3 else S[0]
    lights = []
    ly = round(h * 0.72)
    lamp = 3 if w >= 24 else 2 if w >= 14 else 1
    for lx in (round(w * 0.17), round(w * 0.83) - lamp):
        for j in range(ly - 1, ly + lamp + 1):
            for i in range(lx - 1, lx + lamp + 1):
                cells[(i, j)] = S[0]
        for j in range(ly, ly + lamp):
            for i in range(lx, lx + lamp):
                cells[(i, j)] = FLAME[5] if (lamp == 3 and (i - lx, j - ly) == (2, 2)) else FLAME[6]
        lights.append((x + lx + lamp / 2, top + ly + lamp / 2))
    if w >= 20:
        for mx in (round(w * 0.1), round(w * 0.9) - 1):
            cells[(mx, 2)] = FLAME[4] if night else FLAME[3]
    for (i, j), c in cells.items():
        p.px(x + i, top + j, c, L)
    if w >= 20:
        gx = x + sx0 + 1
        for n in ("o", "5"):
            for (cx, cy) in rain.cells(n):
                if cy % 2 == 0:
                    p.px(gx + cx // 2 + (cx > 2), top + sy0 + 1 + cy // 3, FLAME[4] if night else FLAME[3], L)
            gx += 5
    return lights


def headlights(p: Pix, lights, g, night: bool, motion: bool, clear: bool = False, L: str = "pool", size: float = 1.0):
    """The headlights' glare, on layer `L`, `size` times as large as a train's at the tunnel's mouth: a glow over the
    tunnel's mouth after hours, a halo round each lamp spilling out over the tile and the platform, and through each a
    cross of light, the beam's flare, its arms fading in steps, none of it on a word when `clear` asks it to keep
    clear of them. A drawing made lighter draws the flare's arms shorter and its glows in fewer rings."""
    near = size >= 1
    if night and lights and near:
        mx = sum(x for x, _ in lights) / len(lights)
        p.halo(mx, lights[0][1] - 6 * size, 23 * size, 16 * size, FLAME[3],
               (0.06, 0.14) if p.lite else (0.03, 0.06, 0.1, 0.14), L=L)
    for n, (lx, ly) in enumerate(lights):
        if not near:
            p.halo(lx, ly, 6 * size, 5 * size, FLAME[5], (0.14, 0.34) if night else (0.12, 0.3), L=L, shape=True)
            continue
        if night:
            p.halo(lx, ly, 8 * size, 7 * size, FLAME[5], (0.15, 0.34, 0.5) if p.lite else (0.1, 0.2, 0.34, 0.5), L=L,
                   shape=True)
        else:
            p.halo(lx, ly, 5, 4, FLAME[5], (0.12, 0.25, 0.4), L=L, shape=True)
        reach = round((15 if night else 6) * size * (0.6 if p.lite else 1))
        Lf = p.flicker(n + 1) if (night and motion and L == "pool") else L
        cx, cy = math.floor(lx), math.floor(ly)
        for d in range(2, reach):
            a = (0.6 if night else 0.4) * (3 - (3 * d) // reach) / 3
            arms = ((cx + d, cy), (cx - d, cy)) + (((cx, cy - d), (cx, cy + d)) if d < reach // 2 else ())
            for (fx, fy) in arms:
                if not clear or p.clear_of_words(fx - 2, fy - 2, fx + 3, fy + 3):
                    p.apx(fx, fy, FLAME[6], a, Lf)


def platform(p: Pix, x0, x1, g, night: bool, uid: str = "pf"):
    """The platform's edge along the foot from x0 to x1: the yellow line, its tactile bumps catching the light, over
    the concrete lip."""
    k = -2 if night else 0
    Y, Q = YELLOW, CONCRETE
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{g - 1}" width="3" height="2" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{ramp_at(Y, 4 + k)}" d="M0 .5h3"/><path stroke="{ramp_at(Y, 6 + k)}" d="M1 .5h1"/>'
                  f'<path stroke="{ramp_at(Q, 3 + k)}" d="M0 1.5h3"/><path stroke="{ramp_at(Q, 5 + k)}" d="M0 1.5h1"/>'
                  f'</pattern>')
    p.shapes["base"].append(f'<rect x="{x0}" y="{g - 1}" width="{x1 - x0}" height="2" fill="url(#{uid})"/>')


# --------------------------------------------------------------------------- the light from the street
def _sky_clip(p: Pix, foot: int, box) -> str:
    """The wall the atmosphere may cross: the whole sheet between the frame's columns down to row `foot`, above the
    tagline, but for the month's mark's box, `box`, two units clear. Made once; returns its id."""
    cid = "atm"
    if not any(f'id="{cid}"' in d for d in p.defs):
        a, _, b, d = box
        rects = [(EDGE, 2, a - 2, foot), (b + 2, 2, p.w - EDGE, foot), (a - 2, d + 2, b + 2, foot)]
        p.defs.append(f'<clipPath id="{cid}">' + "".join(
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>' for x0, y0, x1, y1 in rects
            if x1 > x0 and y1 > y0) + "</clipPath>")
    return cid


# The shafts of light falling through the gratings in the street overhead, each (where it meets the ceiling, its
# breadth), slanting down across the wall as the sun or the street lamps stand.
SHAFTS = ((26, 12), (96, 16), (172, 10), (244, 15), (318, 12))
SLANT = 0.5       # how far along a shaft runs for every row it falls
MOTES = 30.0      # seconds the dust takes to drift down a tile of it: one of the hand's slow sweeps


def shafts(p: Pix, foot: int, box, night: bool, motion: bool, seed: int = 6):
    """The light from the street falling through the gratings overhead in shafts slanting down across the whole wall,
    behind the title and the frieze, brightest under the ceiling and fading as they fall, ending above the tagline;
    pale daylight by day and the street lamps' phosphor after hours; and in them dust turning slowly as it drifts
    down, a few motes catching the light. They keep out of the month's mark (see `_sky_clip`). A drawing made lighter
    lays each shaft's light in one band, the motes still turning in it."""
    cid = _sky_clip(p, foot, box)
    light, alpha = (C["white"], (0.2, 0.14, 0.1)) if not night else (FLAME[3], (0.08, 0.06, 0.05))
    if p.lite:
        alpha = alpha[:1]
    polys = []
    for x, w in SHAFTS:
        polys.append([(x, 2), (x + w, 2), (x + w + (foot - 2) * SLANT, foot), (x + (foot - 2) * SLANT, foot)])
    bands = []
    for n, a in enumerate(alpha):
        y1 = foot - n * (foot - 2) // 3
        pts = " ".join(
            f'<polygon points="{num(q[0][0])} 2 {num(q[1][0])} 2 {num(q[1][0] + (y1 - 2) * SLANT)} {y1} '
            f'{num(q[0][0] + (y1 - 2) * SLANT)} {y1}"/>' for q in polys)
        bands.append(f'<g fill-opacity="{num(a)}">{pts}</g>')
    sid = "shc"
    p.defs.append(f'<clipPath id="{sid}">' + "".join(
        f'<polygon points="{" ".join(f"{num(px)} {py}" for px, py in q)}"/>' for q in polys) + "</clipPath>")
    rnd = random.Random(seed)
    tw, th = 30, 24
    dots: dict = {}
    for i in range(5):
        c = (C["white"] if i % 2 else ENAMEL[5]) if not night else (FLAME[5] if i % 2 else FLAME[4])
        dots.setdefault(c, {}).setdefault(rnd.randrange(th), []).append(rnd.randrange(tw))
    tile = "".join(f'<path stroke="{c}" d="{Pix._d(r)}"/>' for c, r in dots.items())
    drift = (f'<animateTransform attributeName="patternTransform" type="translate" '
             f'values="{";".join(f"{i // 2} {i}" for i in range(th))}" dur="{num(MOTES)}s" repeatCount="indefinite" '
             f'calcMode="discrete"/>') if motion else ""
    p.defs.append(f'<pattern id="mt" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">{tile}{drift}</pattern>')
    markup = (f'<g clip-path="url(#{cid})"><g fill="{light}">{"".join(bands)}</g><g clip-path="url(#{sid})">'
              f'<rect x="{EDGE}" y="2" width="{p.w - 2 * EDGE}" height="{foot - 2}" fill="url(#mt)" '
              f'opacity="{".7" if night else ".8"}"/></g></g>')
    p.raw(-9, markup, markup)


def floor_glow(p: Pix, cx, g, rx, alphas=(0.1, 0.2, 0.32, 0.45)):
    """The headlights' phosphor thrown along the platform's edge from the tunnel, strongest by the mouth: rings of it
    laid on the platform's two rows and nowhere else."""
    cid = f"fg{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{EDGE}" y="{g - 1}" width="{p.w - 2 * EDGE}" height="2"/>'
                  f'</clipPath>')
    n, prev, rings = len(alphas), 0.0, []
    for i, a in enumerate(alphas):
        f = (n - i) / n
        rings.append(f'<ellipse cx="{num(cx)}" cy="{g}" rx="{num(rx * f)}" ry="3" '
                     f'fill-opacity="{num(1 - (1 - a) / (1 - prev))}"/>')
        prev = a
    markup = f'<g clip-path="url(#{cid})" fill="{FLAME[4]}">{"".join(rings)}</g>'
    p.raw(3, markup, markup)


# --------------------------------------------------------------------------- the platform's things
def column(p: Pix, x, top, g, night: bool):
    """A steel column of the platform, painted bottle green, from the ceiling at row `top` down to the floor: its
    flanges either side lit on the left and in shade on the right, the web between, rivets down its flanges, and a
    base plate and a cap where it meets the floor and the girder."""
    k = -2 if night else 0
    B = BOTTLE
    p.vline(x, top, g + 1, ramp_at(B, 5 + k))
    p.vline(x + 1, top, g + 1, ramp_at(B, 4 + k))
    p.rect(x + 2, top, 2, g + 1 - top, ramp_at(B, 2 + k))
    p.vline(x + 4, top, g + 1, ramp_at(B, 3 + k))
    p.vline(x + 5, top, g + 1, ramp_at(B, 1 + k))
    for yy in range(top + 3, g - 2, 6):
        p.px(x, yy, ramp_at(B, 6 + k))
        p.px(x + 5, yy, B[0])
    for yy in (top, g - 1):
        p.hline(x - 1, x + 7, yy, ramp_at(B, 4 + k))
        p.hline(x - 1, x + 7, yy + 1, ramp_at(B, 1 + k))


FAN = 0.24        # seconds the fan's blades take to turn a third of the way round, in three frames


def fan(p: Pix, cx, cy, night: bool, motion: bool):
    """A station fan on its bracket against the July heat, its blades turning behind a cage of steel wire in three
    frames, round and round; its motor's housing lit at its upper left. The still twin holds the first frame."""
    k = -2 if night else 0
    S = STEEL
    p.hline(cx + 4, cx + 8, cy, ramp_at(S, 3 + k))
    p.rect(cx + 3, cy - 1, 2, 3, ramp_at(S, 2 + k))
    for f in range(3 if motion else 1):
        L = p.seq(f"fn{f}", f / 3, (f + 1) / 3, FAN, keep=f == 0, z=1) if motion else "base"
        for b in range(3):
            a = (f / 3 + b / 3) * math.tau
            for d in (1, 2, 3):
                p.px(cx + round(math.cos(a) * d), cy + round(math.sin(a) * d), ramp_at(BOTTLE, 4 + k), L)
    for y in range(cy - 5, cy + 6):
        for x in range(cx - 5, cx + 6):
            d = math.hypot(x - cx, y - cy)
            if 4.4 < d <= 5.2:
                p.px(x, y, ramp_at(S, 5 + k) if (x - cx) + (y - cy) < 0 else ramp_at(S, 2 + k), "near")
            elif d <= 4.4 and (x - cx) % 3 == 0 and d > 1.5:
                p.px(x, y, ramp_at(S, 3 + k) + ":0.6", "near")
    p.px(cx, cy, ramp_at(S, 1 + k), "near")


def signal(p: Pix, x, y, night: bool, motion: bool):
    """The signal on the tunnel's wall: a black box on its bracket with two lamps, the upper burning phosphor,
    blinking now and then, to say the train is coming."""
    k = -1 if night else 0
    p.rect(x, y, 5, 9, TUNNEL[2])
    p.vline(x, y, y + 9, ramp_at(STEEL, 3 + k))
    p.hline(x, x + 5, y, ramp_at(STEEL, 4 + k))
    p.hline(x - 2, x, y + 4, ramp_at(STEEL, 2 + k))
    L = p.blink(2) if motion else "base"
    p.rect(x + 2, y + 2, 2, 2, FLAME[5], L)
    p.px(x + 2, y + 2, FLAME[6], L)
    p.rect(x + 2, y + 5, 2, 2, TUNNEL[4])
    if night:
        p.halo(x + 3, y + 3, 4, 4, FLAME[4], (0.12, 0.24))


def poster(p: Pix, x, y, w, h, night: bool, motion: bool, seed: int = 4):
    """An advertisement lit from behind in its steel frame on the wall: the code falling down it in phosphor, a few
    glyphs bright; after hours it glows, its light thrown round it on the tile. A drawing made lighter draws each
    stream of it shorter, its bright head kept."""
    k = -1 if night else 0
    p.rect(x - 1, y - 1, w + 2, h + 2, STEEL[1])
    p.hline(x - 1, x + w + 1, y - 1, ramp_at(STEEL, 5 + k))
    p.vline(x - 1, y - 1, y + h + 1, ramp_at(STEEL, 4 + k))
    p.rect(x, y, w, h, TUNNEL[1] if night else TUNNEL[2])
    rnd = random.Random(seed)
    for n, cx in enumerate(range(x + 1, x + w - rain.W + 1, rain.COLUMN + 1)):
        head = y + 1 + (h - rain.H - 2) * ((n * 2 + 1) % 3) // 2
        for i in range(3 if p.lite else 5):
            gy = head - i * rain.PITCH
            if y < gy and gy + rain.H < y + h:
                c = FLAME[6] if i == 0 else FLAME[4] if i == 1 else FLAME[3] if i == 2 else FLAME[2]
                L = p.twinkle(cx) if (motion and i == 0) else "base"
                rain.write(p, cx, gy, rnd.choice(rain.NAMES), c, L)
    if night:
        p.halo(x + w / 2, y + h / 2, w * 0.9, h * 0.75, FLAME[3], (0.03, 0.06, 0.09))


def tube(p: Pix, x0, x1, y, night: bool, motion: bool, phase: int = 0, ceiling: int = 11) -> tuple:
    """A fluorescent tube hanging from the ceiling at row `ceiling` on two rods, its steel housing over the tube;
    the tube burns phosphor, and after hours it flickers. Returns where it hangs."""
    k = -2 if night else 0
    S = STEEL
    for rx in (x0 + 3, x1 - 4):
        p.vline(rx, ceiling, y, ramp_at(S, 2 + k))
    p.hline(x0, x1, y, ramp_at(S, 5 + k))
    p.hline(x0, x1, y + 1, ramp_at(S, 3 + k))
    p.px(x0, y + 1, ramp_at(S, 1 + k))
    p.px(x1 - 1, y + 1, ramp_at(S, 1 + k))
    L = p.flicker(phase) if (night and motion) else "base"
    p.hline(x0 + 1, x1 - 1, y + 2, FLAME[6] if night else FLAME[5], L)
    if night:
        Lb = p.flicker(phase, back=True) if motion else "haze"
        p.halo((x0 + x1) / 2, y + 3, (x1 - x0) * 0.45, 7, FLAME[4], (0.05, 0.1, 0.16), L=Lb)
    return ((x0 + x1) / 2, y + 2)


def cone(p: Pix, cx, top, g, w, night: bool, motion: bool, phase: int = 0, spread: float = 0.2):
    """The light a tube throws down on the platform after hours: a cone of phosphor widening from the tube to the
    floor, a brighter core in it, flickering with the tube. The caller sizes it to keep clear of the words."""
    if not night:
        return
    L = p.flicker(phase, back=True) if motion else "haze"
    h = g - top
    for half, a in ((w / 2, 0.08), (w / 4, 0.06)):
        wide = half + h * spread * (half / (w / 2))
        p.shapes[p._on(L) if L in p.layers else p.layer(L)].append(
            f'<polygon points="{num(cx - half)} {top} {num(cx + half)} {top} {num(cx + wide)} {g + 1} '
            f'{num(cx - wide)} {g + 1}" fill="{FLAME[3]}" fill-opacity="{num(a)}"/>')


def clock(p: Pix, cx, cy, night: bool, motion: bool, r: int = 6, ceiling: int = 11):
    """The station clock hanging from the ceiling at row `ceiling` on its rod: a white enamel face in a steel rim lit
    at its upper left, its hours marked, its hands at ten past ten and its second hand stepping round a fifth of a
    minute at a time in a moving header."""
    k = -1 if night else 0
    p.vline(cx, ceiling, cy - r - 1, ramp_at(STEEL, 2 + k))
    p.hline(cx - 1, cx + 2, cy - r - 1, ramp_at(STEEL, 3 + k))
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = math.hypot(x + 0.5 - cx - 0.5, y + 0.5 - cy - 0.5)
            if d <= r - 1:
                p.px(x, y, ramp_at(ENAMEL, 5 + k))
            elif d <= r + 0.5:
                lit = (x - cx) + (y - cy) < -1
                p.px(x, y, ramp_at(STEEL, 5 + k) if lit else ramp_at(STEEL, 2 + k))
    for i in range(12):
        a = i / 12 * math.tau
        tx, ty = cx + round(math.sin(a) * (r - 2)), cy - round(math.cos(a) * (r - 2))
        if i % 3 == 0:
            p.px(tx, ty, COAT[2])
    ink = COAT[1]
    for (dx, dy) in ((-1, 0), (-2, -1), (-3, -1)):
        p.px(cx + dx, cy + dy, ink)
    for (dx, dy) in ((0, -1), (1, -2), (1, -3), (2, -4)):
        p.px(cx + dx, cy + dy, ink)
    p.px(cx, cy, COAT[0])
    steps = 12
    for i in range(steps if motion else 1):
        a = i / steps * math.tau + 2.2
        L = p.seq(f"sh{i}", i / steps, (i + 1) / steps, TICK, keep=i == 0, z=1) if motion else "base"
        for d in range(2, r - 1):
            p.px(cx + round(math.sin(a) * d), cy - round(math.cos(a) * d), TERRA[3], L)


def bench(p: Pix, x0, x1, g, night: bool):
    """A platform bench: three oak slats for its back and two for its seat, each lit along its top, on legs and arms
    of black cast iron."""
    k = -2 if night else 0
    O, K = OAK, COAT
    for y in (g - 15, g - 12, g - 9):
        p.hline(x0 + 1, x1 - 1, y, ramp_at(O, 5 + k))
        p.hline(x0 + 1, x1 - 1, y + 1, ramp_at(O, 3 + k))
    p.hline(x0, x1, g - 6, ramp_at(O, 5 + k))
    p.hline(x0, x1, g - 5, ramp_at(O, 3 + k))
    p.hline(x0 + 1, x1 - 1, g - 4, ramp_at(O, 1 + k))
    for lx in (x0 + 2, x1 - 4):
        p.vline(lx, g - 16, g + 1, K[3])
        p.vline(lx + 1, g - 16, g + 1, K[1])
        p.hline(lx - 1, lx + 3, g, K[2])
        p.hline(lx - 2, lx + 3, g - 7, K[3])


# The man waiting at the yellow line, 16 by 34, facing left toward the train: dark glasses, his hands in the pockets
# of his long coat. Hair (q h H), skin (o e s S), the glasses (v), the coat (k x c C, its lapel w), trousers (P p) and
# shoes (N n).
WAIT = [
    "......qqqq......",
    "....qqHHHHq.....",
    "...qHHHhhhhq....",
    "...qHhhhhhhq....",
    "...shhhhhhhq....",
    "..sSShhhhhhq....",
    "..vvvvShhhhq....",
    "..vvvvSsehq.....",
    ".sSssssshq......",
    "..oSssssq.......",
    "...oesssq.......",
    "....oeesk.......",
    "....kkwsskk.....",
    "...kCCwCccckk...",
    "..kCCCwCcccccxk.",
    "..kCCCwcccccxxk.",
    "..kCCcwcccccxxk.",
    "..kCCcwcccccxxk.",
    "..kCCcwkccccxxk.",
    "..kCCcwkcccxxxk.",
    "..kCCcwcccccxxk.",
    "..kCccwcccccxxk.",
    "..kCccwccccxxxk.",
    "..kCccwccccxxxk.",
    "..kCccwccccxxxk.",
    "...kcwcccccxxxk.",
    "...kcwccccxxxxk.",
    "...kcwccccxxxxxk",
    "...kkkkkkkkkkkk.",
    "....kPpk.kPpk...",
    "....kPpk.kPpk...",
    "...kPPpk.kPpk...",
    "..kNNNnk.kNNnk..",
    ".kNNnnnk.kNnnnk.",
]
WAIT_FACE = (4.5, 7.5)     # where his face is on his art, for the light it takes after hours
# The tail of his coat blown back by the train's wind, the other half of his stir: the cells it changes.
GUST = {(14, 21): "x", (15, 22): "k", (15, 23): "x", (16, 24): "k", (15, 24): "x", (16, 25): "k", (15, 25): "x",
        (16, 26): "k", (15, 26): "x", (16, 27): "k", (15, 27): "x", (14, 28): "k", (15, 28): "k", (16, 28): "k"}


def waiting(p: Pix, x, g, night: bool, motion: bool, light=None):
    """The man waiting at the yellow line in his long dark coat, his feet on row g from column x: in a moving header
    the tail of his coat is blown back as the train's wind reaches him and settles, on a four-second loop. After hours
    the tube over him lays its light along his shoulders and on his face, which keeps its tone."""
    K, S = COAT, RAMP["skin1"]
    pal = {"k": K[0], "x": K[2], "c": K[3], "C": K[5], "w": K[6], "P": K[3], "p": K[1], "N": K[4], "n": K[1],
           "q": K[0], "h": K[2], "H": K[4], "o": S[1], "e": S[2], "s": S[3], "S": S[4], "v": X["glasses"]}
    top = g - len(WAIT) + 1
    cells = {(i, j): pal[ch] for j, row in enumerate(WAIT) for i, ch in enumerate(row) if pal.get(ch)}
    if night and light:
        for (i, j), c in list(cells.items()):
            if j >= 12 and c in (K[0], K[2], K[3], K[4], K[5], K[6]) and (i, j - 1) not in cells:
                cells[(i, j)] = FLAME[2]
    a, b = ("wait", night, bool(light)), ("waitgust", night)
    if a not in p.syms:
        p.symbol(a, cells)
    if b not in p.syms:
        p.symbol(b, {(i, j): pal[ch] for (i, j), ch in GUST.items()})
    sa, sb = p.syms[a], p.syms[b]
    still = f'<use href="#{sa}" x="{x}" y="{top}"/>'
    if motion:
        moving = still + (f'<use href="#{sb}" x="{x}" y="{top}" opacity="0"><animate attributeName="opacity" '
                          f'values="0;1;0;1" keyTimes="0;.25;.5;.75" dur="{num(LOOP)}s" repeatCount="indefinite" '
                          f'calcMode="discrete"/></use>')
    else:
        moving = still
    p.raw(1, moving, still)
    if night and light:
        p.halo(x + WAIT_FACE[0], top + WAIT_FACE[1], 4, 4, FLAME[3], (0.06, 0.12), L="pool", shape=True)


# A sheet of newspaper tumbling along the platform in the train's wind, three ways round: flat, folding and on edge,
# its lit side in # and its shaded side in +.
PAPER = [["#+++#", ".##+."], [".#+.", "#++#", ".+#."], ["#++#+"]]


def newspaper(p: Pix, path, night: bool, motion: bool):
    """A sheet of newspaper blown along the platform by the train's wind, tumbling over and over as it goes along the
    path `path`, three units a step, round and round; the still twin holds it where its path begins."""
    k = -2 if night else 0
    pal = {"#": ramp_at(ENAMEL, 5 + k), "+": ramp_at(ENAMEL, 3 + k)}
    keys = []
    for i, art in enumerate(PAPER):
        key = ("paper", i, night)
        if key not in p.syms:
            p.symbol(key, {(dx, dy): pal[ch] for dy, row in enumerate(art) for dx, ch in enumerate(row) if ch in pal})
        keys.append(key)
    if motion:
        p.fly(keys, path, round(len(path) * 0.16, 2), z=4, flap=0.16)
    else:
        p.use(keys[0], *path[0], "pool")


# --------------------------------------------------------------------------- the rules
def inlay(p: Pix, x0, x1, y, night: bool, seed: int = 0):
    """Tesserae let into a rule from x0 to x1 on row y: a pair every twelfth unit, ochre and terracotta by turns, the
    first of each lit, a step dimmer after hours; their places step with `seed` so no two rules are set alike."""
    k = -2 if night else 0
    for i, x in enumerate(range(x0 + 3 + seed % 12, x1 - 3, 12)):
        R = OCHRE if i % 2 == 0 else TERRA
        p.px(x, y, ramp_at(R, 5 + k))
        p.px(x + 1, y, ramp_at(R, 3 + k))


# --------------------------------------------------------------------------- the footers and links
# A heart laid in terracotta tesserae, seven by six, each digit a tone of the glaze: lit at its upper left lobe and
# darkest toward its point.
HEART = [".54.43.", "5443332", "4433321", ".33321.", "..321..", "...1..."]


def heart(p: Pix, x, y, L="base"):
    """The heart in BUILT WITH (heart) BY, laid in terracotta mosaic."""
    p.sprite(x, y, HEART, {str(i): TERRA[i] for i in range(7)}, 1, L)


def scale_tiles(p: Pix, x0, y0, w, h, period=5):
    """The graphic scale's bar as a run of glazed tiles, ochre and cobalt by turns, `period` units a tile: each
    tile's glaze catching the light along its top and in shade along its foot."""
    for xx in range(x0, x0 + w):
        R = OCHRE if ((xx - x0) // period) % 2 == 0 else COBALT
        for yy in range(y0, y0 + h):
            p.px(xx, yy, R[5] if yy == y0 else R[2] if yy == y0 + h - 1 else R[4] if R is OCHRE else R[3])


# The links' icons, each seven by seven, of the station: the train head on with its headlights, the station clock,
# a token for the turnstile and the signal at the tunnel's mouth. Steel in S (lit L, shade d), glass in g, a lamp
# in #, the clock's enamel in w and its hands in k, the token's brass in o (lit O).
ICONS = {
    "train": [".LLLLL.", "LggSggd", "LggSggd", "LSSSSSd", "L#SSS#d", "LSSSSSd", ".d...d."],
    "clock": ["..LLL..", ".LwwwS.", "LwwkwwS", "Lwwkkwd", "LwwwwwS", ".dwwwd.", "..ddd.."],
    "token": ["..ooo..", ".oOOOo.", "oO.O.Oo", "oOO.OOo", "oOO.OOo", ".oOOOo.", "..ooo.."],
    "signal": [".LLLd..", "L#..d..", "L##.d..", "Lgg.d..", "Lgg.d..", ".ddd...", "..S...."],
}
LINK_SPRITES = ("train", "clock", "token", "signal")


def icon_pal(night: bool, ink: str) -> dict:
    """The icons' tones on the enamel sign: steel lit at its upper left, the glass dark, the lamps phosphor, the
    clock's enamel white and its hands dark, the token brass; a step dimmer after hours."""
    k = -1 if night else 0
    return {"L": ramp_at(STEEL, 6 + k), "S": ramp_at(STEEL, 4 + k), "d": ramp_at(STEEL, 2 + k),
            "g": TUNNEL[3], "#": FLAME[5], "w": ramp_at(ENAMEL, 6 + k), "k": COAT[1],
            "o": ramp_at(OCHRE, 3 + k), "O": ramp_at(OCHRE, 5 + k)}


# --------------------------------------------------------------------------- the way down from the street
STEP = 5          # a stair's tread and riser, in units: a flight at forty-five degrees
DRESS = RAMP["dress"]
# What a globe's light falls on after hours: the stair's concrete, its yellow nosings, its green iron and tile, and
# the mosaic band under its steps.
STAIR_LIT = frozenset(RAMP["concrete"] + RAMP["yellow"] + RAMP["bottle"] + RAMP["terra"] + RAMP["ochre"])


def stair_top(fx, g, i, step=STEP) -> int:
    """The row the tread of step `i` of a flight lies on, its foot at column fx on the platform's row g."""
    return g - (i + 1) * step + 1


def _tiles(p: Pix, pid: str, face: str, lit: str, grout: str) -> str:
    """A running bond of glazed tile as a pattern of two courses, each tile's top row catching the light: the wall's
    own bond in other glazes, for a wall built in front of it. Made once a file; returns its id."""
    if ("pattern", pid) not in p.syms:
        pw, half = 2 * (TILE_W + 1), (TILE_W + 1) // 2
        p.defs.append(f'<pattern id="{pid}" y="{TOP}" width="{pw}" height="{2 * COURSE}" patternUnits="userSpaceOnUse">'
                      f'<rect width="{pw}" height="{2 * COURSE}" fill="{face}"/>'
                      f'<path stroke="{lit}" d="M0 .5h{TILE_W}m1 0h{TILE_W}M0 {COURSE + .5}h{half}m1 0h{TILE_W}m1 0h'
                      f'{TILE_W - half}"/><path stroke="{grout}" d="M{TILE_W + .5} 0v{TILE_H}M{pw - .5} 0v{TILE_H}'
                      f'M0 {TILE_H + .5}h{pw}M{half + .5} {COURSE}v{TILE_H}M{half + TILE_W + 1.5} {COURSE}v{TILE_H}'
                      f'M0 {COURSE + TILE_H + .5}h{pw}"/></pattern>')
        p.syms[("pattern", pid)] = pid
    return pid


def stairs(p: Pix, fx, g, n, x2, night: bool, step: int = STEP) -> dict:
    """The stair down from the street, seen from its side, rising to the right from its foot at column fx on the
    platform's row g, `n` steps of `step` units, then its landing on to column x2: the side of the flight walled down
    to the platform in bottle-green tile, with a band of terracotta mosaic running up under the steps; each tread's
    concrete lit along its top, the yellow of a safety nosing at its edge, and each riser in shade; and over it the
    balustrade of iron painted the station's green, a baluster every third unit under a handrail lit along its top,
    with a newel post at the foot and at the head. Returns where its head, its landing and its newel posts are."""
    k = -2 if night else 0
    Q, B, Y, T = CONCRETE, BOTTLE, YELLOW, TERRA
    rail = 11                                   # the handrail's height over the treads' nosings
    x1 = fx + n * step                          # where the landing begins
    head = stair_top(fx, g, n - 1, step)
    # The side wall: the flight's sawtooth over the platform, tiled in a running bond of the bottle glaze.
    pts = [(fx, g + 1)]
    for i in range(n):
        x, top = fx + i * step, stair_top(fx, g, i, step)
        pts += [(x, top + 2), (x + step, top + 2)]
    pts += [(x2, head + 2), (x2, g + 1)]
    pid = _tiles(p, f"st{'n' if night else 'd'}", ramp_at(B, 3 + k), ramp_at(B, 4 + k), ramp_at(B, 1 + k))
    p.shapes["base"].append(f'<polygon points="{" ".join(f"{x} {y}" for x, y in pts)}" fill="url(#{pid})"/>')
    for x in range(fx, x2):
        i = min(n - 1, (x - fx) // step)
        top = stair_top(fx, g, i, step)
        riser = x == fx + i * step and x < x1
        p.px(x, top, ramp_at(Y, 5 + k) if riser else ramp_at(Q, 5 + k))
        p.px(x, top + 1, ramp_at(Y, 3 + k) if riser else ramp_at(Q, 3 + k))
        if riser:
            p.vline(x, top + 2, min(g + 1, top + step + 2), ramp_at(Q, 2 + k))
        # The mosaic band running up under the steps, parallel to the flight, a lozenge of ochre now and then.
        band = g + 6 - (x - fx) if x < x1 else head + 6
        if band + 2 <= g:
            for j, c in enumerate((ramp_at(T, 4 + k), ramp_at(T, 3 + k), ramp_at(T, 1 + k))):
                if top + 2 < band + j <= g:
                    p.px(x, band + j, ramp_at(OCHRE, 5 + k) if (j == 1 and x % 6 == 0) else c)
    # The balustrade: balusters every third unit and the handrail over them, parallel to the flight.
    for x in range(fx + 1, x2 - 1):
        i = min(n - 1, (x - fx) // step)
        top = stair_top(fx, g, i, step)
        hy = (g - rail - (x - fx)) if x < x1 else head - rail
        if (x - fx) % 3 == 1:
            p.vline(x, hy + 2, top, ramp_at(B, 2 + k))
        p.px(x, hy, ramp_at(B, 5 + k))
        p.px(x, hy + 1, ramp_at(B, 2 + k))
    newels = []
    for nx, base in ((fx - 3, g), (x2 - 6, head - 1)):
        top = (g - rail - 3) if nx < fx else head - rail - 3
        p.rect(nx, top, 3, base - top + 1, ramp_at(B, 3 + k))
        p.vline(nx, top, base + 1, ramp_at(B, 5 + k))
        p.vline(nx + 2, top, base + 1, ramp_at(B, 1 + k))
        p.hline(nx - 1, nx + 4, top, ramp_at(B, 4 + k))
        p.hline(nx - 1, nx + 4, top + 1, ramp_at(B, 2 + k))
        newels.append((nx + 1, top))
    return {"head": (x1, head), "newels": newels, "landing": (x1, x2)}


def globe(p: Pix, cx, cy, night: bool, motion: bool, phase: int = 0, r: float = 4.4):
    """A globe lamp of green glass on its iron finial, as the station's way in is marked: its glass a light on the
    hand's phosphor, white-hot where the bulb burns at its heart and catching the light at its upper left, in shade
    toward its lower right, a collar of iron under it; by night it flickers and throws its light round it, onto the
    tile and onto whatever stands near (see `lamplit`)."""
    k = -2 if night else 0
    p.rect(cx - 1, cy + round(r), 3, 2, ramp_at(BOTTLE, 2 + k))
    p.px(cx - 1, cy + round(r), ramp_at(BOTTLE, 4 + k))
    p.hline(cx - 2, cx + 3, cy + round(r) + 1, ramp_at(BOTTLE, 3 + k))
    R = math.ceil(r)
    for y in range(cy - R, cy + R + 1):
        for x in range(cx - R, cx + R + 1):
            d = math.hypot(x - cx, y - cy)
            if d > r:
                continue
            lean = (x - cx) + (y - cy)
            if night:
                c = FLAME[6] if d < r * 0.3 else FLAME[5] if d < r * 0.6 else FLAME[4] if lean < 2 else FLAME[3]
            else:
                c = FLAME[5] if d < r * 0.3 else FLAME[4] if d < r * 0.62 else FLAME[3] if lean < 2 else FLAME[2]
            p.px(x, y, c)
    p.px(cx - 2, cy - 2, FLAME[6])
    p.px(cx - 1, cy - 3, FLAME[6])
    if night:
        L = p.flicker(phase) if motion else "base"
        p.rect(cx - 1, cy - 1, 3, 2, FLAME[6], L)
        p.halo(cx + 0.5, cy + 0.5, 13, 12, FLAME[4], (0.04, 0.08, 0.14, 0.22),
               L=p.flicker(phase, back=True) if motion else "haze", shape=True)


def lamplit(p: Pix, cx, cy, rx, ry, colours, alphas=(0.08, 0.16, 0.26), L="base"):
    """A lamp's phosphor laid over the solid things near it that are of `colours`, stepped as a halo is: the light a
    globe or a booth's window throws onto the steps, the balustrade and the floor after hours."""
    p.halo(cx, cy, rx, ry, FLAME[4], alphas, L=L, only=set(colours))


def way_out(p: Pix, x0, x1, top, base, night: bool):
    """The way out to the street at the head of the stair: an arch of terracotta and ochre mosaic from x0 to x1 over
    the landing, its crown at row `top`, and through it the street in the July sun, a white glare paling down to the
    landing by day; after hours the dark street, a lamp's phosphor falling into it from above. Returns the cells of
    its opening."""
    k = -2 if night else 0
    r = (x1 - x0) / 2
    cx = x0 + r
    hole = _arch(cx, top, r, x0, x1, base)
    rim = _arch(cx, top - 3, r + 3, x0 - 3, x1 + 3, base) - hole
    spring = top + r
    for (x, y) in hole:
        f = (y - top) / max(1, base - top)
        if night:
            c = TUNNEL[4] if f < 0.25 else TUNNEL[3] if f < 0.6 else TUNNEL[2]
        else:
            c = C["white"] if f < 0.4 else ENAMEL[6] if f < 0.75 else ENAMEL[5]
        p.px(x, y, c)
    for (x, y) in rim:
        if x >= p.w - EDGE:
            continue
        ang = math.atan2(y + 0.5 - spring, x + 0.5 - cx)
        n = int((ang + math.pi) / math.pi * 9)
        key = abs(x + 0.5 - cx) < 1.6 and y < top
        base_c = ramp_at(COBALT, 3 + k) if key else (ramp_at(OCHRE, 4 + k), ramp_at(TERRA, 3 + k))[n % 2] \
            if y < spring else ramp_at(TERRA, 2 + k)
        edge = (x - 1, y) not in rim and (x - 1, y) not in hole or (x, y - 1) not in rim and (x, y - 1) not in hole
        p.px(x, y, step_up(base_c) if edge else base_c)
    if night:
        p.halo(cx, top + 2, r * 1.4, 7, FLAME[4], (0.08, 0.16, 0.26), shape=True)
        p.px(round(cx), top + 1, FLAME[5])
        p.px(round(cx) - 1, top + 1, FLAME[4])
    return hole


# A woman in a red summer dress coming down to the platform, 11 by 27, facing left, in two steps: her hair (h, lit
# H), her skin (s, lit S, in shade F) with a single dark unit for her eye (e), the dress (r, lit R, in shade d) and
# her shoes (k).
RIDER = (
    ["....HHh....", "...HHhhh...", "..SsHhhhh..", "..eshhhhh..", ".ssshhhhh..", "..sFhhhh...", "...F.hhh...",
     "..SRRrdhh..", "..sRRrrd...", "..sRrrrd...", "..FRrrrd...", "...Rrrrd...", "...Rrrrdd..", "..RRrrrdd..",
     "..RRrrrrd..", ".RRrrrrrdd.", ".RRrrrrrdd.", "RRrrrrrrddd", "..sS..sF...", "..sS..sF...", "..sS...sF..",
     ".sS....sF..", ".sF.....sF.", "kkF.....sF.", "kk......kkk", "...........", "..........."],
    ["....HHh....", "...HHhhh...", "..SsHhhhh..", "..eshhhhh..", ".ssshhhhh..", "..sFhhhh...", "...F.hhh...",
     "..SRRrdhh..", "..sRRrrd...", "..sRrrrd...", "..FRrrrd...", "...Rrrrd...", "...Rrrrdd..", "..RRrrrdd..",
     "..RRrrrrd..", "..RRrrrrd..", ".RRrrrrrdd.", ".RRrrrrrdd.", "...sSsF....", "...sSsF....", "...sSsF....",
     "...sSsF....", "...sSsF....", "...sSsF....", "..kkkkk....", "...........", "..........."],
)


def rider(p: Pix, path, night: bool, motion: bool):
    """The woman in the red dress coming down the stair to the platform along `path`, the feet's row and her left
    at each point, a step at a time in two strides, round and round on a loop of eight seconds; the still twin
    holds her at its head. Her face keeps its tone after hours."""
    k = -1 if night else 0
    S, D = RAMP["skin2"], DRESS
    pal = {"h": COAT[1], "H": COAT[3], "s": S[3], "S": S[4], "F": S[2], "e": COAT[0],
           "r": ramp_at(D, 3 + k), "R": ramp_at(D, 5 + k), "d": ramp_at(D, 1 + k), "k": COAT[1]}
    keys = []
    for i, art in enumerate(RIDER):
        key = ("rider", i, night)
        if key not in p.syms:
            p.symbol(key, {(x, y): pal[ch] for y, row in enumerate(art) for x, ch in enumerate(row) if ch in pal})
        keys.append(key)
    at = [(x, y - len(RIDER[0]) + 3) for x, y in path]
    if motion:
        p.fly(keys, at, 8.0, z=2, flap=round(8.0 / len(at), 3))
    else:
        p.use(keys[0], *at[0])


def daylight(p: Pix, fx, g, x1, top, head, night: bool):
    """The July sun pouring in through the way out at the head of the stair and down the flight by day: a beam of it
    falling at the flight's own slant from the opening, its edges paler than its core, laid over the steps, the
    balustrade and the wall behind them; after hours none, the globes lighting the steps instead (see `globe`)."""
    if night:
        return
    cid = f"dl{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{fx - 6}" y="{top}" width="{p.w - EDGE - fx + 6}" '
                  f'height="{g + 1 - top}"/></clipPath>')
    right = p.w - EDGE
    bands = []
    for inset, a in ((0, 0.14), (5, 0.12)):
        pts = [(x1 + 1 + inset, top), (right, top), (right, head - inset), (right - (g - head) - inset, g + 1),
               (x1 + 1 + inset - (g + 1 - top), g + 1)]
        bands.append(f'<polygon points="{" ".join(f"{num(x)} {y}" for x, y in pts)}" fill-opacity="{num(a)}"/>')
    p.layer("pool")
    p.shapes["pool"].append(f'<g clip-path="url(#{cid})" fill="{C["white"]}">{"".join(bands)}</g>')


# --------------------------------------------------------------------------- the token booth
BOOTH_W = 44      # the booth's width
BOOTH_LOW, BOOTH_HIGH = 44, 60    # the least and the most rows it stands, from its sign's top to the floor
SIGN_ROOM = 26    # the row a booth's top must stand at or under for a hanging sign to fit over it, under the frieze
# The clerk in the booth, 9 by 10, head and shoulders, looking out to the left over the counter: his hair (h, lit H),
# his skin (s, lit S, in shade F) with a single dark unit for his eye (e), and his uniform's shirt (u, lit U) with its
# collar (c).
CLERK = ["..hhhh...", ".hHHHhh..", ".SsHhhh..", ".eshhhh..", "sssshhh..", ".ssFhh...", "..FF.....",
         ".cUuuuc..", "UUuuuuuu.", "Uuuuuuuuu"]


def booth(p: Pix, x, top, g, night: bool, motion: bool, seed: int = 9) -> dict:
    """The token booth on the platform, from its sign's top at row `top` to its foot on row g, from column x: a
    kiosk of steel painted the station's green on a concrete plinth, riveted, lit along its upper left and in shade
    at its right; its band of thick glass in three panes, as tall as the booth allows, the booth's own tube along its
    head, the clerk behind the middle pane with a stack of tokens before him, the tray under the glass at the
    counter; a cornice of steel; and along its roof a sign lit in phosphor, two of the code's glyphs on it for the
    tokens it sells. After hours the tube lights the glass from inside, flickering, and throws its light out over the
    counter and the floor before it. Returns where its window and its sign are."""
    k = -2 if night else 0
    B, S = BOTTLE, STEEL
    w = BOOTH_W
    sign = (x + 3, top, w - 6, 11)
    sx, sy, sw, sh = sign
    p.rect(sx, sy, sw, sh, ramp_at(S, 1 + k))
    p.hline(sx, sx + sw, sy, ramp_at(S, 5 + k))
    p.vline(sx, sy, sy + sh, ramp_at(S, 4 + k))
    p.rect(sx + 2, sy + 2, sw - 4, sh - 4, TUNNEL[2])
    lit = FLAME[5] if night else FLAME[3]
    for i, name in enumerate(("ka", "n", "ku")):
        rain.write(p, sx + 6 + i * 9, sy + 2, name, lit)
    if night:
        p.halo(sx + sw / 2, sy + sh / 2, sw * 0.7, 8, FLAME[3], (0.05, 0.1, 0.16), shape=True)
    for lx in (sx + 3, sx + sw - 4):
        p.vline(lx, sy + sh, sy + sh + 2, ramp_at(S, 2 + k))
    # The cornice, the roof's lip.
    cy = top + sh + 2
    p.hline(x - 1, x + w + 1, cy, ramp_at(S, 6 + k))
    p.hline(x - 1, x + w + 1, cy + 1, ramp_at(S, 4 + k))
    p.hline(x, x + w, cy + 2, ramp_at(S, 2 + k))
    # The glass: three panes between steel mullions, the booth's tube along their head, the clerk behind the middle.
    body = 12
    gy0 = cy + 3
    gy1 = g - 2 - body - 2
    p.rect(x, gy0, w, gy1 - gy0, ramp_at(S, 3 + k))
    panes = [(x + 2, x + 15), (x + 16, x + 28), (x + 29, x + w - 2)]
    for a, b in panes:
        for yy in range(gy0 + 1, gy1):
            f = (yy - gy0) / (gy1 - gy0)
            if night:
                c = FLAME[2] if f < 0.2 else FLAME[1] if f < 0.65 else FLAME[0]
            else:
                c = GLAZE[5] if f < 0.3 else GLAZE[4] if f < 0.7 else GLAZE[3]
            p.hline(a, b, yy, c)
        p.vline(a, gy0 + 1, gy1, ramp_at(S, 1 + k))
    S1 = RAMP["skin1"]
    pal = {"h": COAT[1], "H": COAT[3], "s": S1[3], "S": S1[4], "F": S1[2], "e": COAT[0], "u": ramp_at(COBALT, 2 + k),
           "U": ramp_at(COBALT, 4 + k), "c": ENAMEL[5] if not night else ENAMEL[3]}
    p.sprite(x + 18, gy1 - len(CLERK), CLERK, pal)
    for i in range(3):                           # the stack of tokens before him, brass
        p.hline(x + 26, x + 29, gy1 - 1 - i, ramp_at(OCHRE, (5 if i == 2 else 3) + k))
    L = p.flicker(seed) if (night and motion) else "base"
    p.hline(panes[0][0] + 1, panes[-1][1] - 1, gy0 + 1, FLAME[5] if night else FLAME[4], L)
    if not night:
        for a, b in panes:                       # the glass catches the light, a glint across each pane
            for d in range(4):
                p.px(a + 2 + d, gy0 + 6 - d, C["white"])
                p.px(a + 3 + d, gy0 + 9 - d, GLAZE[6])
    # The counter and the tray under the glass.
    p.hline(x - 1, x + w + 1, gy1, ramp_at(S, 6 + k))
    p.hline(x - 1, x + w + 1, gy1 + 1, ramp_at(S, 3 + k))
    p.rect(x + 18, gy1 + 1, 9, 2, TUNNEL[2])
    # The body: steel panels painted green, riveted, lit at its upper left and in shade at its right.
    by0 = gy1 + 2
    p.rect(x, by0, w, g - 1 - by0, ramp_at(B, 3 + k))
    p.vline(x, by0, g - 1, ramp_at(B, 5 + k))
    p.vline(x + w - 1, by0, g - 1, ramp_at(B, 1 + k))
    p.hline(x, x + w, by0, ramp_at(B, 4 + k))
    for px_ in (x + 15, x + 29):
        p.vline(px_, by0 + 1, g - 1, ramp_at(B, 2 + k))
        p.vline(px_ + 1, by0 + 1, g - 1, ramp_at(B, 4 + k))
    for ry in (by0 + 2, g - 3):
        for rx in range(x + 3, x + w - 1, 5):
            p.px(rx, ry, ramp_at(B, 6 + k))
    p.hline(x - 1, x + w + 1, g - 1, ramp_at(CONCRETE, 4 + k))
    p.hline(x - 1, x + w + 1, g, ramp_at(CONCRETE, 2 + k))
    if night:
        p.halo(x + w / 2, (gy0 + gy1) / 2, w * 0.75, (gy1 - gy0) * 0.9, FLAME[3], (0.04, 0.08, 0.13), shape=True)
        lamplit(p, x + w / 2, gy1 + 4, w * 0.9, 11, BOOTH_LIT)
    return {"window": (x, gy0, x + w, gy1), "sign": sign}


# What the booth's light falls on after hours: its counter's steel, its green body, the turnstile and the floor.
BOOTH_LIT = frozenset(RAMP["steel"] + RAMP["bottle"] + RAMP["concrete"] + RAMP["yellow"])
# A turnstile, 12 by 16, seen from the side as it stands across the way to the trains: its steel cabinet waist high
# with the slot for a token lit on its top (o), and its tripod of bright steel arms on their hub (A, lit; a, in
# shade; the hub #), one reaching out level across the way, one rising and one falling behind it. Steel in S (lit L,
# shade d).
TURNSTILE = ["......LLLd..", "......LoSd..", "..a...LSSd..", "...a..LSSd..", "....a.LSSd..", "AAAAAA#SSd..",
             "....a.LSSd..", "...a..LSSd..", "..a...LSSd..", "......LSSd..", "......LSSd..", "......LSSd..",
             "......LSSd..", "......LSSd..", ".....LLSSdd.", ".....dddddd."]


def turnstile(p: Pix, x, g, night: bool):
    """A turnstile at the booth, its foot on row g from column x: its steel cabinet with the slot for a token on its
    top lit in phosphor, its three arms of bright steel on their hub, one reaching out level across the way."""
    k = -2 if night else 0
    pal = {"L": ramp_at(STEEL, 5 + k), "S": ramp_at(STEEL, 3 + k), "d": ramp_at(STEEL, 1 + k),
           "A": ramp_at(STEEL, 6 + k), "a": ramp_at(STEEL, 4 + k), "o": FLAME[5] if night else FLAME[3],
           "#": ramp_at(STEEL, 2 + k)}
    p.sprite(x, g - len(TURNSTILE) + 1, TURNSTILE, pal)


def hanging_sign(p: Pix, x0, x1, y, ceiling: int, night: bool, glyphs=("ki", "7")):
    """A sign of black enamel hung from the ceiling at row `ceiling` on two rods, its top at row `y` from x0 to x1:
    a white enamel border, an arrow pointing the way to the trains and two of the code's glyphs, the station's
    words in the code's own script, in white enamel, a tone dimmer after hours. Returns its foot's row."""
    k = -2 if night else 0
    h = 11
    for rx in (x0 + 3, x1 - 4):
        p.vline(rx, ceiling, y, ramp_at(STEEL, 2 + k))
    p.rect(x0, y, x1 - x0, h, TUNNEL[2])
    p.box(x0, y, x1 - x0, h, ramp_at(STEEL, 3 + k))
    p.hline(x0 + 1, x1 - 1, y, ramp_at(STEEL, 5 + k))
    ink = ramp_at(ENAMEL, 6 + k)
    p.box(x0 + 1, y + 1, x1 - x0 - 2, h - 2, ramp_at(ENAMEL, 2 + k))
    ax, ay = x0 + 4, y + 5
    p.hline(ax, ax + 7, ay, ink)
    for d in (1, 2, 3):
        p.px(ax + d, ay - d, ink)
        p.px(ax + d, ay + d, ink)
    for i, name in enumerate(glyphs):
        rain.write(p, ax + 11 + i * 7, y + 2, name, ink)
    return y + h


# --------------------------------------------------------------------------- the footers' footing
FOOT_RISE, FOOT_RUN = 5, 24     # how many rows the tiled dado rises where the cells leave it room, and its least run
GLOBES_W, POST_W = 23, 9        # the width of the pair of globes on their posts with the railing between, and of one
RISE, STUB = 12, 6              # the rows a post rises over its foot, and one cut short where a whole one has no room


def globes(p: Pix, x, base, night: bool, motion: bool = False):
    """The way down to the trains marked as the street marks it: two posts of iron painted the station's green,
    their feet on row `base` from column x, a railing of two rails between them, and on each post a globe of green
    glass, a light on the hand's phosphor, burning by day and blazing after hours."""
    k = -2 if night else 0
    B = BOTTLE
    posts = (x + 1, x + GLOBES_W - 4)
    for px_ in posts:
        p.rect(px_, base - 12, 3, 13, ramp_at(B, 3 + k))
        p.vline(px_, base - 12, base + 1, ramp_at(B, 5 + k))
        p.vline(px_ + 2, base - 12, base + 1, ramp_at(B, 1 + k))
        p.hline(px_ - 1, px_ + 4, base, ramp_at(B, 2 + k))
    for ry in (base - 10, base - 5):
        p.hline(posts[0] + 3, posts[1], ry, ramp_at(B, 4 + k))
        p.hline(posts[0] + 3, posts[1], ry + 1, ramp_at(B, 1 + k))
    for xx in range(posts[0] + 5, posts[1] - 1, 3):
        p.vline(xx, base - 8, base - 5, ramp_at(B, 2 + k))
        p.vline(xx, base - 3, base, ramp_at(B, 2 + k))
    for i, px_ in enumerate(posts):
        globe(p, px_ + 1, base - 17, night, motion, phase=i, r=3.6)


def globe_post(p: Pix, x, base, night: bool, rise: int = RISE):
    """One globe of green glass on its iron post painted the station's green, its foot on row `base` from column x
    and `rise` rows tall: the way down marked where a pair has no room."""
    k = -2 if night else 0
    px_ = x + 3
    p.rect(px_, base - rise, 3, rise + 1, ramp_at(BOTTLE, 3 + k))
    p.vline(px_, base - rise, base + 1, ramp_at(BOTTLE, 5 + k))
    p.vline(px_ + 2, base - rise, base + 1, ramp_at(BOTTLE, 1 + k))
    p.hline(px_ - 1, px_ + 4, base, ramp_at(BOTTLE, 2 + k))
    globe(p, px_ + 1, base - rise - 5, night, False, r=3.6)


def footing(p: Pix, night: bool, after: int = 0):
    """A footer once its words are set: along its foot the frame's band of terracotta and ochre tile, which the footing
    lays in the frame's place, and over it the platform's edge, the concrete lip under the yellow line with its studs
    catching the light, as much of it as keeps a unit clear of the lowest word, the band's foot at the least;
    rising into a dado of bottle-green tile wherever the cells leave it room along FOOT_RUN columns or more, the ruled
    lines between the cells standing on it; and at the rightmost place from column `after` on where the cells leave
    the wall free, the way down to the trains, a pair of green globes on their posts (see `globes`), or one where a
    pair has no room (see `globe_post`), on a post cut short where a whole one has none, burning after hours."""
    w, h = p.w, p.h
    k = -2 if night else 0
    Y, Q, B, T, O = YELLOW, CONCRETE, BOTTLE, TERRA, OCHRE
    base = p.layers["base"]
    low = max((b[3] for b in p.words), default=0)
    ledge = max(low + 1, h - 7)                  # the footing's top row: the yellow line's, where it has the room
    for x in range(EDGE, w - EDGE):
        for y in range(ledge, h):
            up = h - 1 - y                       # rows over the foot: the band, its edge, the lip, the yellow line
            if up == 0:
                c = T[0]
            elif up in (1, 2):
                tile = ((x - EDGE) // 3 + (up == 1)) % 2
                c = ramp_at((T, O)[tile], (5 if (x - EDGE) % 3 == 0 and up == 2 else 3) + k)
            elif up == 3:
                c = ramp_at(O, 5 + k)
            elif up == 4:
                c = ramp_at(Q, 5 + k)
            elif up == 5:
                c = ramp_at(Y, 3 + k)
            else:
                c = ramp_at(Y, 6 + k) if (x - EDGE) % 3 == 1 else ramp_at(Y, 4 + k)
            p.px(x, y, c)
    ledge = min(ledge, h - 4)                    # what rises stands on the band's edge at the lowest

    def free(x0, y0, x1, y1):
        """Whether the box from (x0, y0) to (x1, y1) lies on the bare tile, nothing solid drawn on it, a unit and more
        from every word."""
        return EDGE + 1 <= x0 and x1 <= w - EDGE - 1 and 3 <= y0 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) \
            and not any(":" not in base.get((x, y), ":") for x in range(x0, x1) for y in range(y0, y1))
    mark = None
    for mw, rise in ((GLOBES_W, RISE), (POST_W, RISE), (POST_W, STUB)):
        mark = next(((x, mw, rise) for x in range(w - EDGE - 2 - mw, max(EDGE + 1, after) - 1, -1)
                     if free(x - 1, ledge - rise - 10, x + mw + 1, ledge)), None)
        if mark:
            break
    taken = range(mark[0] - 2, mark[0] + mark[1] + 2) if mark else range(0)
    rise = [x not in taken and free(x, ledge - FOOT_RISE - 1, x + 1, ledge) for x in range(w)]
    x = EDGE + 1
    while x < w - EDGE - 1:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - EDGE - 1) if not rise[i]), w - EDGE - 1)
        if b - x >= FOOT_RUN:
            for xx in range(x, b):
                for y in range(ledge - FOOT_RISE, ledge):
                    row = y - (ledge - FOOT_RISE)
                    joint = (xx - x + (3 if row >= 3 else 0)) % (TILE_W + 1) == TILE_W
                    if row == 0:
                        c = ramp_at(B, 5 + k)
                    elif y == ledge - 1:
                        c = ramp_at(B, 1 + k)
                    elif row == 3 or joint:
                        c = ramp_at(B, 2 + k)
                    else:
                        c = ramp_at(B, 3 + k)
                    p.px(xx, y, c)
                p.px(xx, ledge - FOOT_RISE - 1, C["tile_lit_n"] if night else C["grout"])
            p.vline(x, ledge - FOOT_RISE, ledge, ramp_at(B, 4 + k))
            p.vline(b - 1, ledge - FOOT_RISE, ledge, ramp_at(B, 1 + k))
        x = b
    if mark:
        if mark[1] == GLOBES_W:
            globes(p, mark[0], ledge - 1, night)
        else:
            globe_post(p, mark[0], ledge - 1, night, rise=mark[2])


# --------------------------------------------------------------------------- the elements
LINES = ("terra", "cobalt", "bottle", "ochre")      # the colours the subway map's lines run in, by turns


def card_glaze(p: Pix, night: bool, x, y, w, h, lid: bool):
    """A schematic card as a panel of glazed tile: its icon's cell glazed celadon by day and bottle green after hours,
    a strip of mosaic down the cell's edge, terracotta and ochre by turns; and on a card with a lid a band of ochre
    along its top set with lozenges of cobalt, as the frieze runs along the wall."""
    k = -2 if night else 0
    cell = BOTTLE[1] if night else GLAZE[4]
    fill = C["tile_lit_n"] if night else GLAZE[6]
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + 11):
            if p.get(xx, yy) == fill:
                p.px(xx, yy, cell)
    for yy in range(y + 1, y + h - 1):
        R = TERRA if (yy - y) // 2 % 2 == 0 else OCHRE
        p.px(x + 11, yy, ramp_at(R, 4 + k))
        p.px(x + 12, yy, ramp_at(R, 2 + k))
    if lid:
        for xx in range(x + 14, x + w - 2):
            on = (xx - x) % 6 in (2, 3)
            p.px(xx, y + 1, ramp_at(COBALT, 4 + k) if on else ramp_at(OCHRE, 4 + k))


def wire_lamps(p: Pix, cells, night: bool):
    """The wire as conduit painted the station's green, clipped to the wall every eighth unit, a signal lamp burning
    phosphor where it turns."""
    k = -2 if night else 0
    for i, (x, y, d) in enumerate(cells[1:-4], 1):
        if i % 8 == 0:
            if d == "h":
                p.px(x, y - 1, ramp_at(STEEL, 5 + k))
                p.px(x, y + 1, ramp_at(STEEL, 2 + k))
            else:
                p.px(x - 1, y, ramp_at(STEEL, 5 + k))
                p.px(x + 1, y, ramp_at(STEEL, 2 + k))
    turns = [c for i, c in enumerate(cells) if 0 < i < len(cells) - 4 and cells[i - 1][2] != c[2]]
    for (x, y, _) in turns:
        p.px(x, y, FLAME[5] if night else FLAME[4])
        if night:
            p.halo(x + 0.5, y + 0.5, 3, 3, FLAME[4], (0.12, 0.24))


def tile_bar(p: Pix, bx, base, bw, v, night: bool):
    """A week's commits as a stack of glazed tiles standing on the base line: a course of terracotta and a course of
    ochre by turns, four rows a course, each tile's top catching the light and the grout under it, the stack's right
    in shade."""
    k = -1 if night else 0
    for j in range(v):
        y = base - 1 - j
        course = j // 4
        R = TERRA if course % 2 == 0 else OCHRE
        row = j % 4
        for xx in range(bx, bx + bw):
            if row == 0:
                c = ramp_at(R, 1 + k)                 # the grout under the course
            elif row == 3 or y == base - v:
                c = ramp_at(R, 5 + k)                 # the tile's lit top
            elif xx == bx + bw - 1:
                c = ramp_at(R, 2 + k)
            else:
                c = ramp_at(R, 3 + k)
            p.px(xx, y, c)


def signal_lamp(p: Pix, x, y, night: bool):
    """A small signal lamp, burning phosphor: the mark beside the busiest week's count."""
    p.rect(x, y, 3, 3, FLAME[4] if night else FLAME[3])
    p.px(x + 1, y + 1, FLAME[6] if night else FLAME[5])
    if night:
        p.halo(x + 1.5, y + 1.5, 4, 4, FLAME[4], (0.12, 0.24))


def token(p: Pix, x, y, night: bool, s: int = 1):
    """A token for the turnstile, brass with its cut-out letter, seven units across at `s` units a pixel."""
    p.sprite(x, y, ICONS["token"], icon_pal(night, ""), s)


def roundel(p: Pix, cx, cy, i, night: bool) -> str:
    """An enamel roundel, fifteen across, centred on (cx, cy): a ring in the colour of one of the subway map's lines,
    `LINES` by turns, round a disc of white enamel, the ring lit at its upper left. Returns the ink a name on its
    disc takes."""
    k = -1 if night else 0
    R = RAMP[LINES[i % len(LINES)]]
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 7, cx + 8):
            d = math.hypot(x - cx, y - cy)
            if d > 7.3:
                continue
            if d > 5.2:
                lit = (x - cx) + (y - cy) < -3
                c = ramp_at(R, 4 + k) if lit else ramp_at(R, 2 + k) if d > 6.5 else ramp_at(R, 3 + k)
            else:
                c = ramp_at(ENAMEL, 6 + k) if (x - cx) + (y - cy) < 2 else ramp_at(ENAMEL, 5 + k)
            p.px(x, y, c)
    return COAT[1]


def map_line(p: Pix, x0, x1, y, night: bool):
    """The line the releases are stops on, drawn as a subway map draws one: a band of terracotta three rows deep, its
    top lit."""
    k = -1 if night else 0
    p.hline(x0, x1, y - 1, ramp_at(TERRA, 5 + k))
    p.hline(x0, x1, y, ramp_at(TERRA, 3 + k))
    p.hline(x0, x1, y + 1, ramp_at(TERRA, 2 + k))


def stop(p: Pix, x, gy, kind: str, night: bool):
    """A release as a stop on the map's line at column x: a disc of white enamel ringed dark for a release, a wider
    pill for a big one where lines meet, a notch for a patch, a hollow ring for one still to come, and for the first
    survey the terminus's bar across the line."""
    k = -1 if night else 0
    white, ring = ramp_at(ENAMEL, 6 + k), COAT[1]
    if kind in ("minor", "next") and night:
        ring = ENAMEL[3]                         # after hours a patch's notch and a stop to come are drawn pale
    if kind == "minor":
        p.px(x, gy - 2, ring)
        p.px(x, gy + 2, ring)
        return
    if kind == "made":
        p.rect(x - 1, gy - 4, 3, 9, ring)
        p.vline(x, gy - 3, gy + 4, white)
        return
    wide = 3 if kind == "big" else 0
    for dy in range(-3, 4):
        for dx in range(-3 - wide, 4 + wide):
            ex = max(0, abs(dx) - wide)
            d = math.hypot(ex, dy)
            if d > 3.4:
                continue
            if d > 2.2:
                p.px(x + dx, gy + dy, ring)
            elif kind != "next":
                p.px(x + dx, gy + dy, white)


def little_train(p: Pix, x, y, night: bool):
    """The train at today's end of the line, its car of stainless steel seen from the side, nine by six, its windows
    lit phosphor and its headlight burning at its nose, running toward the stops to come."""
    k = -2 if night else 0
    S = STEEL
    p.rect(x - 4, y - 7, 9, 5, ramp_at(S, 4 + k))
    p.hline(x - 4, x + 5, y - 7, ramp_at(S, 6 + k))
    p.hline(x - 4, x + 5, y - 3, ramp_at(S, 2 + k))
    for wx in (x - 3, x, x + 3):
        p.px(wx, y - 5, FLAME[4] if night else COBALT[3])
    p.px(x + 5, y - 4, FLAME[6] if night else FLAME[5])
    p.px(x - 3, y - 2, COAT[1])
    p.px(x + 3, y - 2, COAT[1])


def tesserae_ring(p: Pix, cx, cy, r0, r1, night: bool):
    """A ring of mosaic round a seal, from radius r0 to r1: tesserae of terracotta and ochre by turns, each lit at its
    upper left, set in dark grout."""
    k = -1 if night else 0
    for y in range(cy - r1 - 1, cy + r1 + 2):
        for x in range(cx - r1 - 1, cx + r1 + 2):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if not r0 <= d <= r1:
                continue
            ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
            n = int((ang + math.pi) / (2 * math.pi) * 24)
            frac = (ang + math.pi) / (2 * math.pi) * 24 - n
            if frac < 0.12 or abs(d - (r0 + r1) / 2) > (r1 - r0) / 2 - 0.6:
                c = ramp_at(TERRA, 0 + max(0, k + 1))
            else:
                R = TERRA if n % 2 == 0 else OCHRE
                lit = (x - cx) + (y - cy) < 0
                c = ramp_at(R, (5 if lit else 3) + k)
            p.px(x, y, c)


def enamel_plate(q: Pix, ox, oy, night: bool):
    """A counter's digit as a platform's number plate, eleven by fifteen: a face of enamel in a rim of cobalt, white
    by day and cobalt after hours, the rim lit at its upper left and a screw at its head and its foot."""
    k = -1 if night else 0
    face = COBALT[1] if night else ENAMEL[5]
    q.rect(ox, oy, 11, 15, face)
    q.box(ox, oy, 11, 15, COBALT[2] if not night else STEEL[2])
    q.hline(ox + 1, ox + 10, oy, COBALT[4] if not night else STEEL[4])
    q.vline(ox, oy + 1, oy + 14, COBALT[4] if not night else STEEL[4])
    for sy in (oy + 1, oy + 13):
        q.px(ox + 5, sy, ramp_at(STEEL, 4 + k))
