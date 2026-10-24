# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Harvest set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is the sky over the fields where the machines grow us: ashen lavender by day, streaked with a high
overcast, and by night a black-purple storm. Ribbed black conduit runs round its edges, clamped in dark metal at the
corners, and across a header's top the cables hang in swags from clamp to clamp, parting either side of the month's
mark; behind them the storm's clouds drift across the sky, lightning crawling through them. Titles are glass tubes of
phosphor fluid, a little empty glass at the top of each, pale glass walls, dark metal caps on the ends of their
strokes, bubbles rising through them; by night they glow. Headers open on the fields: at the left a tower of glass
pods stacked round its spine, each glowing green and holding a sleeper curled in the fluid, cables running up from it
into the dark, and beyond it the next towers fading into the haze; at the right the harvester, a spidery machine of
segmented arms and a cluster of red eyes, clinging to a tower and plucking a pod from it; and along the foot,
wherever the words leave room, the towers of the fields stand to the horizon. A section's header has the awakening,
a sleeper risen out of an open pod as the doctor is let down from the dark to pull his jacks; a strip's the pod tree,
its cables arching out like a willow's boughs hung with glowing pods. Pods as small as marks lie and stand beside a
title, and lengths of cable lie along a rule. A phone's headers have the same world under their words: the whole of
the fields, the awakening and the pod tree. The footers stand on the trench's cables, a pod plugged into its socket
on them; the links are plates of dark metal under ribbed conduit; and the elements are built of the pods' control
panels, cables carrying the code, tubes of the fluid, ribbed conduit and the machines' red eyes. Everything is shaded
from the one light in the upper left on the set's own ramps, every light is the hand's phosphor, and only the
machines' eyes burn red."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, LZ, Paint, Pix, fold, num
from .palette import C, NIGHT_SKY, RAMP, X

ASH, STORM, CONDUIT, METAL, GLASS = RAMP["ash"], RAMP["storm"], RAMP["conduit"], RAMP["metal"], RAMP["glass"]
EYE, FLAME = RAMP["eye"], RAMP["flame"]
SKINS = (RAMP["skin0"], RAMP["skin1"], RAMP["skin2"])
EDGE = 4          # the conduit's width down the sides and along the foot
TOP = 15          # the rows a header's conduit and its swags of cable take across its top
STORM_LOOP = 7.0  # the loop the lightning strikes on


def _t(R, i):
    """Tone `i` of ramp R, held to the ramp's ends."""
    return R[max(0, min(len(R) - 1, i))]


def light(nx: float, ny: float, nz: float) -> float:
    """How much of the one lamp a surface facing (nx, ny, nz) takes, 0 to 1."""
    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return max(0.0, (nx * LX + ny * LY + nz * LZ) / n)


def ellipse(cx, cy, rx, ry) -> set:
    """The cells inside an ellipse centred on (cx, cy)."""
    out = set()
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                out.add((x, y))
    return out


def _shade(R, k: int):
    """Ramp R stepped `k` tones (down, as by night, when negative), as a function of the tone: `_shade(R, k)(i)` is
    tone i + k, held to the ramp's ends."""
    def tone(i):
        return _t(R, i + k)
    return tone


# --------------------------------------------------------------------------- the sky
def _overcast(night: bool) -> dict:
    """The sky's tile, forty-eight units by sixteen: long thin streaks of high cloud in the sky's own tones."""
    a, b = (STORM[2], STORM[3]) if night else (ASH[6], ASH[4])
    cells = {}
    for x in range(3, 17):
        cells[(x, 2)] = a
    for x in range(9, 15):
        cells[(x, 3)] = b
    for x in range(27, 45):
        cells[(x, 10)] = a
    for x in range(31, 38):
        cells[(x, 11)] = b
    return cells


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the sky over the fields, ashen lavender by day and by night the black-purple of
    the storm, a little warmer toward the horizon, streaked with high cloud in its own tones, which a drawing made
    lighter to fit its budget leaves out."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
    if not p.lite:
        p.defs.append(f'<pattern id="{uid}o" x="7" width="48" height="16" patternUnits="userSpaceOnUse">'
                      f'{p.markup(_overcast(night))}</pattern>')
        p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}o)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the ashen sky, by night the storm's band."""
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        return next(NIGHT_SKY[i] for i in range(n) if y < edges[i + 1] or i == n - 1)
    return C["paper"]


# --------------------------------------------------------------------------- the frame
def _strip(p: Pix, pid: str, w: int, h: int, cells: dict, x: int, y: int, rw: int, rh: int):
    """A run of ribbed conduit laid as a pattern of `cells`, w by h, over the box (x, y, rw, rh), under what is
    drawn."""
    p.defs.append(f'<pattern id="{pid}" x="{x}" y="{y}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells)}</pattern>')
    p.shapes["base"].append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="url(#{pid})"/>')


def clamp(p: Pix, x, y, night: bool, w: int = 6, h: int = 6):
    """A clamp of dark metal, w by h, its top-left at (x, y), lit at its upper left, a bolt in its middle: drawn
    once a file for each size and placed."""
    key = ("clamp", w, h, night)
    if key not in p.syms:
        k = -1 if night else 0
        cells = {(i, j): _t(METAL, 3 + k) for i in range(w) for j in range(h)}
        cells.update({(i, 0): _t(METAL, 6 + k) for i in range(w)})
        cells.update({(0, j): _t(METAL, 5 + k) for j in range(1, h)})
        cells.update({(i, h - 1): METAL[0] for i in range(1, w)})
        cells.update({(w - 1, j): METAL[0] for j in range(1, h)})
        cells[(w // 2 - 1, h // 2 - 1)] = _t(METAL, 6 + k)
        cells[(w // 2, h // 2)] = METAL[0]
        p.symbol(key, cells)
    p.use(key, x, y)


def frame(p: Pix, night: bool, header: bool = False, clear=None):
    """The border: ribbed black conduit down the sides and along the foot, each rib's crest catching the light on
    the conduit's lit side, clamped in dark metal at the corners; across a header's top a thicker run of it, and
    across a footer's the same as its sides."""
    w, h = p.w, p.h
    c = CONDUIT
    rib = ((c[0], c[6], c[4], c[2]), (c[0], c[4], c[3], c[1]), (c[0], c[2], c[1], c[0]))
    left = {(i, j): rib[j][i] for i in range(4) for j in range(3)}
    _strip(p, "kl", 4, 3, left, 0, 0, 4, h)
    right = {(3 - i, j): (c[0], c[1], c[3], c[5])[i] if j == 0 else (c[0], c[1], c[2], c[4])[i] if j == 1
             else (c[0], c[0], c[1], c[2])[i] for i in range(4) for j in range(3)}
    _strip(p, "kr", 4, 3, right, w - 4, 0, 4, h)
    foot = {(i, j): ((c[5], c[3], c[1], c[0]), (c[4], c[2], c[1], c[0]), (c[2], c[1], c[0], c[0]))[i][j]
            for i in range(3) for j in range(4)}
    _strip(p, "kf", 3, 4, foot, 4, h - 4, w - 8, 4)
    rows = 5 if header else 4
    top = {(i, j): ((c[0], c[6], c[5], c[3], c[1])[j] if i == 0 else (c[0], c[5], c[4], c[2], c[1])[j] if i == 1
                    else (c[0], c[3], c[2], c[1], c[0])[j]) for i in range(3) for j in range(5)}
    if not header:
        top = {(i, j): v for (i, j), v in top.items() if j < 4}
    _strip(p, "kt", 3, rows, top, 4, 0, w - 8, rows)
    for x, y in ((0, 0), (w - 6, 0), (0, h - 6), (w - 6, h - 6)):
        clamp(p, x, y, night)


def swags(p: Pix, x0, x1, night: bool, clear=None):
    """The cables hung across a header's top in swags from clamp to clamp, three to a span, each sagging its own
    depth, dark rubber lit along its upper edge, none of them crossing `clear` (the columns kept for the month's
    mark)."""
    k = -1 if night else 0
    posts = list(range(x0, x1, 46)) + [x1]
    if clear:
        posts = [x for x in posts if x < clear[0] - 2 or x > clear[1] + 2]
        posts = sorted(set(posts + [clear[0] - 4, clear[1] + 2]))
    for a, b in zip(posts, posts[1:]):
        if clear and a < clear[1] and b > clear[0]:
            continue
        key = ("swag", b - a, night)
        if key not in p.syms:                     # a span of each length drawn once, and placed
            cells = {}
            for n, (sag, y0) in enumerate(((7, 6), (4, 7))):
                for x in range(1, b - a + 1):
                    y = y0 + round(sag * math.sin(math.pi * x / max(1, b - a)))
                    cells[(x, y)] = _t(CONDUIT, 1 + n % 2 + k)
                    cells[(x, y - 1)] = _t(CONDUIT, 4 + k) if n != 1 else _t(CONDUIT, 3 + k)
            p.symbol(key, cells)
        p.use(key, a, 0)
    for x in posts:
        if EDGE + 2 <= x <= p.w - EDGE - 6:
            clamp(p, x - 1, 4, night, w=4, h=5)


# --------------------------------------------------------------------------- the titles
def _fluid(r, c, scale, night):
    """The tubes' fill, row by row of a letter in canvas units: at the top of every tube a little empty glass, pale,
    the fluid's surface under it a bright line where the light catches it, and below that the phosphor fluid,
    brightest under the surface and denser toward the foot."""
    head = max(1, scale - 1)
    if r < head:
        return GLASS[3] if night else GLASS[5]
    if r == head:
        return FLAME[6] if night else FLAME[5]
    band = min(6, r // scale)
    return (FLAME[4], FLAME[4], FLAME[4], FLAME[3], FLAME[3], FLAME[2], FLAME[2])[band]


FLUID = Paint("fl", _fluid, period=1)


def _walls(night: bool):
    """The tubes' glass walls: along a letter's right edges the glass in shade, the fluid seen through it."""
    wall = GLASS[2] if night else GLASS[3]

    def finish(p: Pix, cells, scale, layer, rnd, y):
        if scale < 3:
            return
        for (x, yy) in cells:
            if (x + 1, yy) not in cells and (x, yy + 1) in cells and (x - 1, yy) in cells:
                p.px(x, yy, wall, layer)
    return finish


def _ends(rows: list, width: int) -> list:
    """The ends of a letter's strokes where they meet its edge, as (column, row, dx, dy): a unit with one neighbour,
    counting its corners, on the letter's top or foot row or its outer columns, and the way to that neighbour."""
    cells = {(c, r) for r, cols in enumerate(rows) for c in cols}
    out = []
    for (c, r) in cells:
        nb = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and (c + dx, r + dy) in cells]
        if len(nb) == 1 and (r in (0, len(rows) - 1) or c in (0, width - 1)):
            out.append((c, r) + nb[0])
    return out


def _outlined(p: Pix, x, y, s, scale: int, colour: str, L="base"):
    """The dark line a unit round every letter of `s` set at `scale` from (x, y), written as cheaply as the title
    allows, the same unit for unit: either each letter four times over, a unit up, down, left and right, as the canvas
    outlines a letter, or the ring round each letter drawn once a file as a symbol and placed once a letter, which a
    long title of few letters writes in a fraction of the bytes."""
    glyphs, _, space = FONTS["57"]
    placed, cx = [], x
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    rings = {}
    for ch in {c for c, _ in placed}:
        if ("ring", ch, scale) in p.syms:
            continue
        cells = {(col * scale + dx, r * scale + dy) for r, cols in enumerate(glyphs[ch][1]) for col in cols
                 for dx in range(scale) for dy in range(scale)}
        rings[ch] = {(a + dx, b + dy) for (a, b) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells
    cost_rings = sum(len(Pix._d(_rows(v))) + 30 for v in rings.values()) + 24 * len(placed)
    if cost_rings < 4 * 52 * len(placed):
        for ch, sid in rings.items():
            p.symbol(("ring", ch, scale), {xy: 1 for xy in sid}, mono=True)
        for ch, gx in placed:
            p.use(("ring", ch, scale), gx, y, L, stroke=colour)
    else:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for ch, gx in placed:
                p.use(("glyph", "57", ch), gx + dx, y + dy, L, stroke=colour, scale=scale)


def _rows(cells) -> dict:
    """{y: [x, ...]} for a set of cells, the shape `Pix._d` writes a path from."""
    out: dict = {}
    for (x, y) in cells:
        out.setdefault(y, []).append(x)
    return out


def tube_title(p: Pix, x, y, s, night: bool, scale: int, motion: bool) -> int:
    """A title of glass tubes filled with phosphor fluid: a little empty glass at the top of each tube, the fluid's
    surface a bright line under it, the fluid bright under its surface and denser toward its foot; the glass walls
    pale along the letters' left edges and in shade along their right, each letter outlined dark; a dark metal cap
    on every stroke's end where it meets the letter's edge, and bubbles rising through the tubes, twinkling on three
    phases from the foot up. By night the tubes glow. Returns its width."""
    kw = dict(paint=FLUID, night=night, finish=_walls(night))
    if scale >= 3:
        kw["bevel"] = (GLASS[5] if night else GLASS[6], FLAME[1])
    kw["glow"] = (FLAME[3], (0.09, 0.18) if night else (0.08,)) if scale >= 3 else (FLAME[3], (0.12,))
    _outlined(p, x, y, s, scale, GLASS[0] if night else GLASS[1])
    w = p.text(x, y, s, FLAME[3], "57", scale, **kw)
    if scale < 3:
        return w
    L = p.layer("caps", z=0.4)
    k = -1 if night else 0
    glyphs, _, space = FONTS["57"]
    cx = x
    rnd = random.Random(len(s) * 5 + x)
    half = scale // 2
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        gw, rows = glyphs[ch]
        for c, r, dx, dy in _ends(rows, gw):
            gx, gy = cx + c * scale, y + r * scale
            if dy > 0:                                  # the stroke runs down from here: capped at its top
                box = (gx - 1, gy - 1, scale + 2, half + 1)
            elif dy < 0:
                box = (gx - 1, gy + scale - half, scale + 2, half + 1)
            elif dx < 0:
                box = (gx + scale - half, gy - 1, half + 1, scale + 2)
            else:
                box = (gx - 1, gy - 1, half + 1, scale + 2)
            bx, by, bw, bh = box
            p.rect(bx, by, bw, bh, _t(METAL, 3 + k), L)
            p.hline(bx, bx + bw, by, _t(METAL, 6 + k), L)
            p.vline(bx, by, by + bh, _t(METAL, 5 + k), L)
            p.hline(bx + 1, bx + bw, by + bh - 1, METAL[0], L)
            p.vline(bx + bw - 1, by + 1, by + bh, METAL[0], L)
        for r, cols in enumerate(rows):                  # the glass's glint along the top of each stroke
            for c in cols:
                if c not in (rows[r - 1] if r else ()):
                    gx0 = cx + c * scale + (1 if (c - 1) not in cols else 0)
                    gx1 = cx + (c + 1) * scale - (1 if (c + 1) not in cols else 0)
                    p.hline(gx0, gx1, y + r * scale, GLASS[6] if not night else FLAME[6], L)
        stems = [c for c in range(gw) if sum(1 for cols in rows if c in cols) >= 4]
        for i in range(2):
            if not stems:
                break
            c = rnd.choice(stems)
            for phase in range(3):
                r = 5 - phase * 2
                if c in rows[r] and (c in rows[r - 1] or c in rows[min(6, r + 1)]):
                    bx = cx + c * scale + 1 + (i + phase) % max(1, scale - 2)
                    by = y + r * scale + 1
                    Lb = p.twinkle(phase) if motion else L
                    p.px(bx, by, FLAME[6], Lb)
        cx += (gw + 1) * scale
    return w


# --------------------------------------------------------------------------- the pods
# A pod seen from the front, its sleeper curled in it facing left: its caps of dark metal (m, M lit), the glass (g, G
# catching the light), the fluid (f, F brighter where the light comes through, d denser), and the sleeper curled
# with his knees drawn up (S skin, s its shade, h hair), dim in the fluid.
POD = [
    "...mMMMMm...",
    "..mMMMMMMm..",
    "..gGGGGGGg..",
    ".gGfFfffddg.",
    "gGFfhhhfffdg",
    "gFfhSSShffdg",
    "gFfSSSSsffdg",
    "gFffSSsfffdg",
    "gFfsSSSSSfdg",
    "gffsSSSSSsdg",
    "gfffSSSssSdg",
    "gffffsSSssdg",
    "gfffffssfddg",
    "gfffffffdddg",
    ".gffffffddg.",
    "..mMMMMMMm..",
    "...mmmmmm...",
]
EMPTY = [row.replace("s", "f").replace("S", "F").replace("h", "f") for row in POD]
PODS = ((False, 1), (True, 2), (True, 0))      # the pods' looks: which way the sleeper faces, and his skin


def pod(p: Pix, x, y, night: bool, look: int = 0, empty: bool = False, L="base"):
    """A pod with its top-left at (x, y): a capsule of glass between two caps of dark metal, full of phosphor fluid
    that glows, a sleeper curled in it on one of the hand's skins, the fluid's light on him; or `empty`, the fluid
    alone. Drawn once a file for each of its looks (`PODS`), and placed."""
    k = -1 if night else 0
    flip, skin = PODS[look % len(PODS)]
    S = SKINS[skin]
    pal = {"m": _t(METAL, 2 + k), "M": _t(METAL, 5 + k), "g": GLASS[3] if night else GLASS[4],
           "G": FLAME[5] if night else GLASS[6], "f": FLAME[3] if night else FLAME[2],
           "F": FLAME[4] if night else FLAME[3], "d": FLAME[2] if night else FLAME[1],
           "s": S[2], "S": S[3], "h": METAL[1]}
    p.sprite(x, y, EMPTY if empty else POD, pal, L=L, flip=flip, reuse=True)


def tower(p: Pix, cx, top, g, night: bool, motion: bool, levels: int, skip=(), sides=(0, 1), sky=TOP) -> list:
    """A tower of pods standing on the ground at row g, its spine of dark metal centred on column cx and its top at
    row `top`: segmented, a pod on each of its `sides` (0 its left, 1 its right) at every level, each slung from the
    spine by a cable, the sleepers on the hand's skins; cables run up from its crown into the dark, as high as row
    `sky`. A pod at (level, side) in `skip` is gone: its slot is empty, its cable hanging loose. Returns the pods'
    boxes."""
    k = -1 if night else 0
    p.rect(cx - 2, top, 4, g - top + 1, _t(METAL, 3 + k))
    p.vline(cx - 2, top, g + 1, _t(METAL, 5 + k))
    p.vline(cx - 1, top, g + 1, _t(METAL, 4 + k))
    p.vline(cx + 1, top, g + 1, METAL[1])
    for yy in range(top + 3, g, 5):
        p.hline(cx - 2, cx + 2, yy, _t(METAL, 1 + k))
        p.px(cx - 2, yy + 1, _t(METAL, 6 + k))
    for i, dx in enumerate((-2, 0, 2)):                    # the cables up from its crown into the dark
        for yy in range(sky + 1, top):
            if (yy + i * 3) % 9:
                p.px(cx + dx + (1 if (yy // 8 + i) % 3 == 0 else 0), yy, _t(CONDUIT, 2 + i % 2))
    p.hline(cx - 4, cx + 4, top, _t(METAL, 6 + k))
    p.hline(cx - 4, cx + 4, top + 1, METAL[1])
    boxes = []
    step = (g - top - 17) // max(1, levels - 1) if levels > 1 else 0
    for lv in range(levels):
        py = top + 2 + lv * step
        for side in sides:
            px_ = cx - 15 if side == 0 else cx + 3
            if (lv, side) in skip:
                for j in range(6):
                    p.px(px_ + (10 if side == 0 else 1) + (j % 2), py + 3 + j, _t(CONDUIT, 3))
                continue
            pod(p, px_, py, night, look=side if side == 0 else 1 + lv % 2)
            boxes.append((px_, py, 12, 17))
            if night:
                p.halo(px_ + 6, py + 8.5, 10, min(11, g - py - 8.5), FLAME[3], (0.14,),
                       L=p.flicker(lv + side, back=True) if motion else "haze")
            hx = px_ + 11 if side == 0 else px_
            p.hline(hx, cx - 2, py + 1, _t(CONDUIT, 3)) if side == 0 else p.hline(cx + 2, hx + 1, py + 1,
                                                                                  _t(CONDUIT, 3))
    return boxes


def far_towers(p: Pix, x0, x1, top, bottom, night: bool, seed=9):
    """The next towers of the fields beyond the near one, between x0 and x1 and rows `top` and `bottom`, each smaller
    and paler as it stands farther: a dark spine tapering to its crown with its cables rising from it, and up both
    its sides the pods as little capsules of phosphor, the tower fading into the haze toward its foot."""
    spots = [(x0 + (x1 - x0) * 2 // 9, 1.0), (x0 + (x1 - x0) * 5 // 9, 0.75), (x0 + (x1 - x0) * 8 // 9, 0.55)]
    for i, (cx, scale) in enumerate(spots):
        t = top + round((bottom - top) * (1 - scale) * 0.7)
        far = i > 0
        spine = (STORM[4] if night else ASH[2]) if not far else (STORM[3] if night else ASH[3])
        lit = (STORM[5] if night else ASH[1]) if not far else (STORM[4] if night else ASH[2])
        p.vline(cx, t, bottom, spine)
        p.vline(cx - 1, t + 2, bottom, lit)
        p.vline(cx + 1, t + 4, bottom, spine)
        p.vline(cx, t - 4, t, STORM[3] if night else ASH[3])
        p.px(cx - 1, t - 5, STORM[3] if night else ASH[3])
        gap = max(5, round(8 * scale))
        glow = FLAME[3] if night else GLASS[2] if far else FLAME[1]
        rim = FLAME[2] if night else GLASS[1] if far else FLAME[0]
        pair = {}                                   # a level's two pods, left and right of the spine
        for side in (-1, 1):
            px_ = 2 if side > 0 else -4
            if scale > 0.7:
                pair.update({(px_ + i, j): glow for i in range(3) for j in range(1, 3)})
                pair.update({(px_ + i, 0): rim for i in range(3)})
                pair[(px_ + (2 if side > 0 else 0), 1)] = FLAME[4] if night else FLAME[2]
            else:
                pair.update({(px_ + (1 if side < 0 else 0) + i, j): glow for i in range(2) for j in range(2)})
        for yy in range(t + 3, bottom - 4, gap):
            if yy + 3 <= bottom - 7:                # above the haze: the pair drawn once a file and placed
                key = ("farpods", scale > 0.7, glow, rim, night)
                if key not in p.syms:
                    p.symbol(key, pair)
                p.use(key, cx, yy)
            else:                                   # in it, in pixels, so the haze lies over them
                for (dx, dy), c in pair.items():
                    p.px(cx + dx, yy + dy, c)
        for j, yy in enumerate(range(bottom - 7, bottom)):
            p.hline(cx - 6, cx + 6, yy, (STORM[2] if night else X["haze_day"]) + (":0.5" if j < 3 else ":0.75"))


def crown_cables(p: Pix, cx, top, night: bool, x_min: int, x_max: int, sky=TOP):
    """The cables that run up from a tower's crown at (cx, top) into the dark: two heavy cables, lit along their
    left edges, rising side by side and swaying a little apart and together on their way to the header's top, or
    to row `sky`, between columns x_min and x_max."""
    k = -1 if night else 0
    for n, dx in enumerate((-2, 2)):
        for yy in range(sky, top):
            t = (top - yy) / max(1, top - sky)
            x = cx + dx + round(math.sin(t * 5 + n * 2.1) * 1.4 + dx * t * 0.8)
            x = max(x_min, min(x_max - 1, x))
            p.px(x, yy, _t(CONDUIT, 4 + k))
            p.px(x + 1, yy, CONDUIT[0] if n % 2 else _t(CONDUIT, 1 + k))


def horizon(p: Pix, x0, x1, y0, y1, night: bool):
    """The glow the fields' pods throw up into the low sky along the horizon, from x0 to x1 and rows y0 to y1:
    phosphor in two steps, strongest at the horizon; faint by day."""
    a = (0.07, 0.13) if night else (0.04, 0.07)
    mid = (y0 + y1) // 2
    p.shapes["haze"].append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{FLAME[3]}" '
                            f'fill-opacity="{a[0]}"/><rect x="{x0}" y="{mid}" width="{x1 - x0}" height="{y1 - mid}" '
                            f'fill="{FLAME[3]}" fill-opacity="{a[0]}"/>')


def fields(p: Pix, x0, x1, g, night: bool, uid: str = "fd"):
    """The fields to the horizon along the foot from x0 to x1: rows of distant towers, their pods points of
    phosphor, standing on the ground at row g, as a pattern laid once."""
    cells = {}
    for i, (tx, th) in enumerate(((2, 7), (9, 5), (15, 6), (21, 4))):
        for yy in range(8 - th, 8):
            cells[(tx, yy)] = STORM[3] if night else ASH[3]
        for yy in range(9 - th, 7, 2):
            cells[(tx - 1, yy)] = FLAME[2] if night else FLAME[1]
            cells[(tx + 1, yy)] = FLAME[3] if night else FLAME[2]
    for xx in range(24):
        cells[(xx, 7)] = STORM[2] if night else ASH[4]
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{g - 7}" width="24" height="8" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells)}</pattern>')
    p.shapes[p.layer("fields", z=-1)].append(
        f'<rect x="{x0}" y="{g - 7}" width="{x1 - x0}" height="8" fill="url(#{uid})"/>')


# --------------------------------------------------------------------------- the harvester
# The harvester's body, head to the right: its abdomen of dark metal plates (P lit along its crown, p, d in shade, r
# the ridge down its middle), its outline (o), its head (f) set with a cluster of red eyes (e, E their burning cores),
# and the joints its arms hang from (j).
HARVESTER = [
    "...........oooooooooo.............",
    "........oooPPPPPPPPPPooo..........",
    "......ooPPPpppppppppPPPoo.........",
    ".....oPPpppppprpppppppPPPo........",
    "....oPpppppppprppppppppPPPoooo....",
    "...oPppppppppprpppppppppPofffoo...",
    "..oPpppppppppprppppppppppoffEeffo.",
    "..oppppdpppppprpppppppppoffeEfEfo.",
    ".oPppppdpppppprpppppppppofEeffeEo.",
    ".opppppdpppppprpppppppppoffEeEffo.",
    ".oppppdppppppprpppppppppofEffEefo.",
    ".opppdpppppppprppppppppppoffeEffo.",
    "..oppdpppppppprpppppppppdoffffoo..",
    "..oddppppppppprppppppppdddoooo....",
    "...odddpppppprpppppppdddddo.......",
    "....oodddddddrddddddddddoo........",
    "......ooojoooooooojoooooo.........",
]


def _arm(p: Pix, pts, L, night, thick: int = 3):
    """A segmented arm of dark metal along the joints `pts`: a tube `thick` units across, lit on the side that faces
    the light and dark on the other, ringed every four units, a round knuckle at every joint."""
    k = -1 if night else 0
    lit, mid, dark, ring = _t(METAL, 5 + k), _t(METAL, 3 + k), METAL[0], _t(METAL, 1 + k)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay), 1)
        steep = abs(by - ay) > abs(bx - ax)
        for i in range(n + 1):
            x = round(ax + (bx - ax) * i / n)
            y = round(ay + (by - ay) * i / n)
            across = [(x - 1, y), (x, y), (x + 1, y)] if steep else [(x, y - 1), (x, y), (x, y + 1)]
            if thick == 2:
                across = across[:2]
            for j, q in enumerate(across):
                c = (lit, mid, dark)[j] if thick == 3 else (lit, dark)[j]
                if i % 4 == 0 and j == 1:
                    c = ring
                p.px(q[0], q[1], c, L)
    for (jx, jy) in pts[1:-1]:
        for dx, dy, c in ((0, -1, lit), (-1, 0, lit), (0, 0, mid), (1, 0, dark), (0, 1, dark), (-1, -1, dark),
                          (1, -1, mid), (-1, 1, mid), (1, 1, dark)):
            p.px(jx + dx, jy + dy, c, L)
        p.px(jx - 1, jy - 1, _t(METAL, 6 + k), L)


def harvester(p: Pix, x, y, night: bool, motion: bool, spine: tuple, slot: tuple, floor: int = 55):
    """The harvester, the top-left of its body at (x, y), clinging to the tower at the right with two of its arms,
    two hooked legs hanging under it, and plucking a pod from the tower with a fifth: an abdomen of dark metal plates
    lit along its crown, a head set with a cluster of red eyes, three of them blinking, its arms three units thick
    and knuckled. The plucking arm draws the pod out of its slot and away in three frames on a six-second loop; the
    still file holds it halfway. By night the eyes glow and light its head. `spine` is the tower's (x, top, bottom),
    `slot` the empty slot's top-left; nothing of it hangs below row `floor`."""
    k = -1 if night else 0
    m = _shade(METAL, k)
    pal = {"o": METAL[0], "P": m(6), "p": m(4), "d": m(2), "r": m(1), "f": METAL[1], "e": EYE[3], "E": EYE[5],
           "j": m(5)}
    sx, stop, sbot = spine
    w, h = len(HARVESTER[0]), len(HARVESTER)
    for i, ty in enumerate((stop + 6, slot[1] + 24)):           # the arms that grip the tower
        knee = (x + w + 4 + i * 6, y - 2 + i * 14)
        _arm(p, [(x + w - 8, y + 5 + i * 6), knee, (sx - 3, ty)], "base", night)
        p.rect(sx - 4, ty - 1, 7, 3, m(4))
        p.hline(sx - 4, sx + 3, ty - 1, m(6))
    for i, (ax, ay) in enumerate(((x + 8, y + h - 2), (x + 13, y + h - 1), (x + 19, y + h - 1))):   # its legs
        foot = min(floor, ay + 13 + i * 2)
        knee = (ax - 9 + i * 5, ay + 5 - i)
        _arm(p, [(ax, ay), knee, (ax - 6 + i * 6, foot)], "base", night, thick=2)
    p.sprite(x, y, HARVESTER, pal)
    for ex, ey in ((28, 7), (31, 8), (27, 10)):
        p.px(x + ex, y + ey, EYE[6], p.blink(ex % 3) if motion else "base")
    jx, jy = x + w - 6, y + h - 4
    frames = (slot, (slot[0] - 10, slot[1] - 4), (slot[0] - 19, slot[1] - 6))
    for f, (px_, py_) in enumerate(frames):
        if motion:
            L = p.seq(f"hv{f}", (0.0, 0.3, 0.6)[f], (0.3, 0.6, 1.0)[f], 6.0, keep=f == 1, z=0.6)
        elif f != 1:
            continue
        else:
            L = "base"
        _arm(p, [(jx, jy), ((jx + px_) // 2 + 2, min(py_ + 14, floor - 2)), (px_ + 3, py_ + 9)], L, night, thick=2)
        pod(p, px_, py_, night, look=2, L=L)
        p.rect(px_ + 1, py_ + 7, 4, 4, m(2), L)
        p.hline(px_ + 1, px_ + 5, py_ + 7, m(6), L)
    if night:
        for (qx, qy), c in list(p.layers["base"].items()):     # the pods' light on the arms near the tower
            if sx - 14 <= qx < sx - 3 and stop <= qy < sbot and c in METAL[1:]:
                p.apx(qx, qy, FLAME[4], 0.25, "base")
        p.halo(x + w - 5, y + 9, 10, 8, EYE[3], (0.08, 0.16, 0.26), L="haze")
        for (qx, qy), c in list(p.layers["base"].items()):
            if x + w - 10 <= qx < x + w and y + 3 <= qy < y + h and c in (pal["P"], pal["p"], pal["f"]):
                p.apx(qx, qy, EYE[4], 0.3, "base")


# --------------------------------------------------------------------------- the awakening
# A sleeper waking, 22 wide and 19 tall, risen out of the pod's fluid to the waist, facing left, gasping, his near hand
# gripping its rim: his skin on the hand's light skin, pale from the pod (s, lit S, shaded z), bald, his brow and his
# eye half shut (e), his mouth open (m), his ear, the fluid running off him (f), and the jacks at the base of his skull
# and in his back (j), from which the cables run back into the tower.
WAKER = [
    "........SSSs..........",
    "......SSSsssz.........",
    ".....SSssssssz........",
    ".....Szzsssssz........",
    ".....Sessszssz........",
    "....Ssssssszsz........",
    "....szsssszssz........",
    ".....msssssszj........",
    ".....Sssssssz.........",
    "......zzssssz.........",
    "........Ssszz.........",
    ".......Ssssszz........",
    "....SSSsfsssssszz.....",
    "...SSsssssssssssjz....",
    "..SszSsssssssssszz....",
    ".Ssz.Ssssssfssszz.....",
    "Ssz..Ssssssssssz......",
    "ssz..Ssssssssssz......",
    ".....fssssssssfz......",
]
# The doctor, 21 wide and 12 tall, the little machine let down on its cable to pull a waking sleeper's jacks: its
# shell of dark metal plates (P lit, p, d in shade, o outline, r the ridge down its back), a cluster of red eyes in its
# face (e, E their burning cores) and the housing its claws hang from (c).
DOCTOR = [
    ".......ooooooo.......",
    "....oooPPPPPPPooo....",
    "..ooPPPpppppppPPPoo..",
    ".oPPppppppprppppPPdo.",
    "oPpppppppppppppppddo.",
    "opEepppEepppEeppdddo.",
    "opeeppEeEppppeepdddo.",
    ".oppppeeeppppppdddo..",
    "..oddpppppppppddoo...",
    "...oocccccccccoo.....",
    ".....ooocccooo.......",
    "........ooo..........",
]


def big_pod(p: Pix, cx, top, g, night, motion, w=30) -> dict:
    """A pod standing open on its pedestal at row g, centred on column cx, its rim at row `top`: a tall capsule of
    glass `w` wide, pale walls catching the light at the left and in shade at the right, full of the phosphor fluid,
    its surface a bright line under the rim, bright under it and denser toward the foot, bubbles rising in it; a
    collar of dark metal round its open rim, clamped at either side; its foot capped in metal on a pedestal. By night
    the fluid glows and its light spreads round the pod. Returns where its rim is."""
    k = -1 if night else 0
    h = g - 5 - top
    x0 = cx - w // 2
    cells = set()
    for yy in range(top, top + h):
        f = (yy - top) / max(1, h - 1)
        inset = round(3 * (1 - min(1.0, f * 6)) ** 2) if f < 0.17 else round(3 * max(0.0, (f - 0.86) / 0.14) ** 2)
        for xx in range(x0 + inset, x0 + w - inset):
            cells.add((xx, yy))
    surface = top + 3
    for (xx, yy) in cells:
        left, right = (xx - 1, yy) not in cells, (xx + 1, yy) not in cells
        bottom = (xx, yy + 1) not in cells
        if left or right or bottom or yy == top:
            c = GLASS[5 if left else 2] if not night else GLASS[4 if left else 1]
            if yy == top:
                c = GLASS[6] if not night else GLASS[4]
        elif xx == x0 + (2 if yy > top + 3 else 4) and yy < top + h - 4:
            c = GLASS[6] if not night else FLAME[5]
        elif yy < surface:
            c = GLASS[4] if not night else GLASS[2]
        elif yy == surface:
            c = FLAME[5] if not night else FLAME[6]
        else:
            band = (yy - surface) / max(1, h - (surface - top))
            c = FLAME[4] if band < 0.3 else FLAME[3] if band < 0.65 else FLAME[2]
            if not night:
                c = {FLAME[4]: FLAME[3], FLAME[3]: FLAME[2], FLAME[2]: FLAME[1]}[c]
            if (xx - x0) > w - 6:
                c = FLAME[max(0, FLAME.index(c) - 1)]
        p.px(xx, yy, c)
    # The bubbles, rising in three columns; twinkling by night in a moving header.
    for i, (bx, by) in enumerate(((x0 + 6, top + h - 9), (x0 + 9, top + h - 17), (x0 + 5, top + h - 25),
                                  (x0 + w - 8, top + h - 12), (x0 + w - 9, top + h - 22))):
        if by > surface + 2:
            p.px(bx, by, FLAME[6], p.twinkle(i) if motion and night else "base")
    # The foot: a cap of dark metal and the pedestal under it.
    for yy in range(top + h - 1, g + 1):
        rim_w = w + 2 if yy < top + h + 2 else w - 4
        a = cx - rim_w // 2
        for xx in range(a, a + rim_w):
            t = 5 if xx == a or yy == top + h - 1 else 1 if xx == a + rim_w - 1 or yy == g else 3
            p.px(xx, yy, _t(METAL, t + k))
    # The collar of dark metal round the open rim, lit along its top, its clamps at either side.
    for xx in range(x0 - 1, x0 + w + 1):
        p.px(xx, top - 1, _t(METAL, 6 + k) if xx < x0 + w - 2 else _t(METAL, 4 + k))
        p.px(xx, top, _t(METAL, 3 + k) if xx > x0 else _t(METAL, 5 + k))
        p.px(xx, top + 1, METAL[1])
    for xx in (x0 - 2, x0 + w):
        p.rect(xx, top - 2, 2, 5, _t(METAL, 4 + k))
        p.px(xx, top - 2, _t(METAL, 6 + k))
    if night:
        p.halo(cx, top + h // 2, w * 0.9, h * 0.62, FLAME[3], (0.06, 0.12, 0.2),
               L=p.flicker(1, back=True) if motion else "haze")
    return {"rim": (x0, top, x0 + w)}


def doctor(p: Pix, x, y, night, motion, reach, sky=TOP):
    """The doctor, the little machine let down from the dark on its cable, its shell's top-left at (x, y): dark
    metal plates lit along its crown, a cluster of red eyes in its face, three of them blinking, glowing by night; two
    hooked legs hanging under it and its two claws, knuckled, reaching down to `reach`, the waking sleeper's neck. Its
    cable runs up into the dark as high as row `sky`."""
    k = -1 if night else 0
    m = _shade(METAL, k)
    pal = {"o": METAL[0], "P": m(6), "p": m(4), "d": m(2), "r": m(1), "c": m(3), "e": EYE[3], "E": EYE[5]}
    for yy in range(sky + 1, y + 1):                # its cable up into the dark
        p.px(x + 10, yy, _t(CONDUIT, 4 + k))
        p.px(x + 11, yy, CONDUIT[1])
    rx, ry = reach
    for side, sx in ((-1, x + 2), (1, x + 17)):      # its hooked legs, hanging
        _arm(p, [(sx, y + 7), (sx + side * 5, y + 11), (sx + side * 4, y + 19)], "base", night, thick=2)
    p.sprite(x, y, DOCTOR, pal)
    for ex, ey in ((3, 5), (8, 5), (13, 5)):
        p.px(x + ex, y + ey, EYE[6], p.blink(ex % 3) if motion else "base")
    for side, sx in ((-1, x + 7), (1, x + 13)):      # its claws, reaching for the jack in his neck
        knee = (sx + side * 4, y + 15)
        _arm(p, [(sx, y + 10), knee, (rx + side, ry - 1)], "base", night, thick=2)
        p.px(rx + side * 2, ry, _t(METAL, 5 + k))
    if night:
        p.halo(x + 10.5, y + 6, 12, 8, EYE[3], (0.08, 0.16, 0.26), L="haze")


def awakening(p: Pix, x0, x1, g, night, motion, top=TOP + 2) -> tuple:
    """The right of an H2's sky, standing on the fields' ground at row g between columns x0 and x1 and rising to row
    `top`, the sky's full height: at the right a tower of pods rising into the dark, its pods glowing; before it a
    pod drawn from it standing open on its pedestal, glowing green, its rim collared in metal, a sleeper risen out of
    its fluid to the waist, pale from the pod, his hands on its rim and the cables from his neck and arm running back
    into the tower, only a shade of him showing under the fluid's surface; over him the doctor let down from the dark
    on its cable, its red eyes on him and its claws reaching for his neck; heavy cables along the ground; and at the
    left the next towers of pods fading into the haze. By night the pod's fluid lights him and everything near it.
    Returns its span."""
    k = -1 if night else 0
    tcx = x1 - 6
    levels = max(2, min(4, (g - top - 6) // 17))
    ttop = g - 17 * levels - 4
    tower(p, tcx, ttop, g, night, motion, levels, sides=(0,), sky=top - 1)
    crown_cables(p, tcx, ttop, night, tcx - 20, x1, sky=top)
    cx = tcx - 44
    rim = max(top + 36, g - 50)
    if cx - 15 - 32 > x0:
        far_towers(p, x0 + 2, cx - 17, top + 14, g - 2, night, seed=4)
    pod_ = big_pod(p, cx, rim, g, night, motion)
    S = SKINS[0]
    pal = {"s": S[3], "S": S[4], "z": S[2], "e": METAL[0], "m": S[0], "f": FLAME[4] if night else FLAME[3],
           "j": METAL[4]}
    wx, wy = cx - 11, rim - 17
    # Under the fluid's surface only his shape shows, a shade of it: his hips and his legs drawn up.
    body = ellipse(cx - 1, rim + 9, 5, 7) | ellipse(cx + 2, rim + 15, 6, 3)
    for (xx, yy) in body:
        if yy > rim + 3:
            p.px(xx, yy, FLAME[2])
    p.sprite(wx, wy, WAKER, pal)
    # The cables from his neck and arm, back over the pod's rim and away into the tower.
    for n, (sx, sy) in enumerate(((wx + 14, wy + 7), (wx + 18, wy + 13))):
        tx, ty = tcx - 16, ttop + 8 + n * 17
        steps_ = max(abs(tx - sx), 1)
        for i in range(steps_ + 1):
            t = i / steps_
            x = round(sx + (tx - sx) * t)
            y = round(sy + (ty - sy) * t + 7 * math.sin(math.pi * t))
            p.px(x, y, _t(CONDUIT, 4 + k))
            p.px(x, y + 1, CONDUIT[1])
    for n, (dx, sag) in enumerate(((-14, 4), (14, 3))):  # and from the pod's foot along the ground
        ax, ay = cx + dx, g - 2
        bx = (x0 + 4) if dx < 0 else (tcx - 3)
        for i in range(abs(bx - ax) + 1):
            t = i / max(1, abs(bx - ax))
            y = ay + round(sag * math.sin(math.pi * t) * 0.5)
            if y <= g:
                p.px(round(ax + (bx - ax) * t), y, _t(CONDUIT, 4 + k))
                p.px(round(ax + (bx - ax) * t), y - 1, _t(CONDUIT, 2 + k))
    doctor(p, wx + 9, max(top + 2, rim - 40), night, motion, (wx + 14, wy + 6), sky=top - 1)
    if night:                                       # a drawing made lighter leaves out the light's faint outer ring
        lit = set(S) | {_t(METAL, t) for t in range(7)} | {_t(CONDUIT, t) for t in range(7)}
        if p.lite:
            p.halo(cx, rim, 20, 16, FLAME[4], (0.2, 0.3), L="base", only=lit)
        else:
            p.halo(cx, rim, 30, 24, FLAME[4], (0.1, 0.2, 0.3), L="base", only=lit)
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the pod tree
# A small pod hung from the pod tree, 7 wide and 11 tall: its caps of dark metal (m, M lit), its glass (g, G catching
# the light), its fluid (f, F brighter, d denser) and the sleeper curled in it (s, a shade of the fluid).
SMALL_POD = [
    "..mMm..",
    ".mMMMm.",
    "gGFffdg",
    "gFfsfdg",
    "gFssfdg",
    "gfssfdg",
    "gfsffdg",
    "gfffddg",
    ".gfddg.",
    ".mmmmm.",
    "..mmm..",
]


def small_pod(p: Pix, x, y, night, motion, i=0, L="base"):
    """A small pod hung by its cable, its top-left at (x, y): glass full of glowing fluid round a curled sleeper, capped
    in dark metal; by night its fluid glows, flickering, its light round it."""
    k = -1 if night else 0
    pal = {"m": _t(METAL, 2 + k), "M": _t(METAL, 5 + k), "g": GLASS[3] if night else GLASS[4],
           "G": FLAME[5] if night else GLASS[6], "f": FLAME[3] if night else FLAME[2],
           "F": FLAME[4] if night else FLAME[3], "d": FLAME[2] if night else FLAME[1],
           "s": FLAME[2] if night else FLAME[1]}
    p.sprite(x, y, SMALL_POD, pal, L=L, reuse=True)
    if night:
        p.halo(x + 3.5, y + 5.5, 7, 8, FLAME[3], (0.1, 0.18), L=p.flicker(i, back=True) if motion else "haze")


def pod_tree(p: Pix, x0, x1, g, night, motion, top, sky=TOP, long=46, cut=3) -> tuple:
    """The right of an H3's strip, standing on the fields' ground at row g between columns x0 and x1 and rising to
    row `top`, the strip's full height: a trunk of ribbed conduit seven units across at its foot and five at its crown,
    lit down its left side and ringed where its ribs run, its roots of cable spreading over the ground; from it heavy
    cables, clamped in dark metal where they leave it, arch up and out to the left and droop like a willow's boughs,
    the first `long` units long at the most and each under it `cut` shorter; from them the pods hang like fruit at
    harvest, each glowing green with a sleeper curled in it, the more boughs the taller the strip (a long bough hung
    with a pod every 24 units, where no bough under it passes), and between the pods thin strands of cable hang down
    as a willow's do, a bead of phosphor at each tip; and at its crown its cables run on up into the dark, as high as
    row `sky`. By night every pod glows and the beads burn brighter. Returns its span."""
    k = -1 if night else 0
    tx = x1 - 11
    # The roots, cables spreading over the ground either side of the trunk.
    for n, (bx, sag) in enumerate(((x0 + 2, 3), (x1, 1), (tx - 26, 2))):
        for i in range(abs(bx - tx) + 1):
            t = i / max(1, abs(bx - tx))
            x = round(tx + (bx - tx) * t)
            y = min(g, g - round(sag * (1 - t) * 1.5) + (1 if t > 0.6 else 0))
            p.px(x, y, _t(CONDUIT, 4 + k))
            p.px(x, y - 1, _t(CONDUIT, 2 + k))

    # The trunk: ribbed conduit tapering from seven units across to five, leaning a little, from the ground up.
    def rise(yy):
        return (g - yy) / max(1, g - top)

    def trunk_x(yy):
        return tx - 3 - round(rise(yy) * 2)
    tones = {7: (6, 5, 4, 3, 3, 2, 1), 6: (6, 5, 4, 3, 2, 1), 5: (6, 5, 3, 2, 1)}
    for yy in range(top, g + 1):
        xx, w = trunk_x(yy), 7 - round(rise(yy) * 2)
        rib = yy % 3 == 0
        for d, t in enumerate(tones[w]):
            p.px(xx + d, yy, _t(CONDUIT, (t - 2 if rib and 0 < d < w - 1 else t) + k))
        p.px(xx + w, yy, CONDUIT[0])
        flare = max(0, yy - (g - 6)) // 2            # its foot splaying into the ground like a tree's
        for d in range(1, flare + 1):
            p.px(xx - d, yy, _t(CONDUIT, 5 + k))
            p.px(xx + w + d, yy, _t(CONDUIT, 1 + k))
    for n, dx in enumerate((1, 3)):                 # the crown's cables up into the dark
        for yy in range(sky + 1, top):
            sway = round(math.sin((top - yy) / 6 + n) * 1.2)
            p.px(trunk_x(top) + dx + sway, yy, _t(CONDUIT, 4 + k))
            p.px(trunk_x(top) + dx + sway + 1, yy, CONDUIT[1])
    # The boughs: heavy cables arching up and out to the left and drooping, pods hanging from them on short cables
    # and strands of cable between them.
    span = g - top
    boughs = 2 if span < 76 else 3 if span < 110 else 4
    rows = [top + 6 + b * (span - 25) // boughs for b in range(boughs)]
    reaches = [max(18, min(trunk_x(by) - x0 - 3, long - b * cut)) for b, by in enumerate(rows)]
    shapes = []
    for by, reach in zip(rows, reaches):
        arch, droop = (6, 11) if reach >= 30 else (4, 7)
        shapes.append([(trunk_x(by) - i, by - round(arch * math.sin(math.pi * i / reach * 0.85))
                        + round((i / reach) ** 2 * droop)) for i in range(reach + 1)])
    n_pod = 0
    for b, (by, reach, pts) in enumerate(zip(rows, reaches, shapes)):
        bx0 = trunk_x(by)
        for (x, y) in pts:
            p.px(x, y - 1, _t(CONDUIT, 5 + k))
            p.px(x, y, _t(CONDUIT, 3 + k))
            p.px(x, y + 1, CONDUIT[1])
        p.rect(bx0 - 1, by - 2, 3, 5, _t(METAL, 3 + k))          # its clamp on the trunk
        p.vline(bx0 - 1, by - 2, by + 3, _t(METAL, 5 + k))
        p.px(bx0 - 1, by - 2, _t(METAL, 6 + k))
        if reach >= 60:                             # a long bough: a pod every 24 units from its end
            under = trunk_x(rows[b + 1]) - reaches[b + 1] - 8 if b + 1 < boughs else p.w
            hangs = [f for f in (1 - (i * 24 + 4) / reach for i in range(reach // 24)) if bx0 - f * reach < under]
        else:
            hangs = (0.45, 0.92) if reach >= 30 else (0.8,)
        hung = []
        for j, frac in enumerate(hangs):
            hx, hy = pts[round(frac * reach)]
            drop = 2 + (j + b) % 2 * 3
            if hy + drop + 17 > g - 1:
                continue
            for yy in range(hy + 2, hy + drop + 1):
                p.px(hx, yy, _t(CONDUIT, 3 + k))
            pod(p, hx - 6, hy + drop, night, look=(b + j) % 3)
            hung.append(hx)
            if night:
                p.halo(hx, hy + drop + 8.5, 10, 10, FLAME[3], (0.12,),
                       L=p.flicker(n_pod, back=True) if motion else "haze")
            n_pod += 1
        # The strands, wherever a pod leaves the bough room, each stopping short of the bough under it.
        below = shapes[b + 1] if b + 1 < boughs else []
        for i in range(4, reach - 1, 4):
            sx, sy = pts[i]
            if any(abs(sx - hx) < 8 for hx in hung) or abs(sx - bx0) < 4:
                continue
            floor = min([y for (x, y) in below if x == sx] or [g]) - 4
            n = min(5 + (i * 7) % 8, floor - sy - 2)
            if n < 3:
                continue
            for yy in range(sy + 2, sy + 2 + n):
                p.px(sx, yy, _t(CONDUIT, 4 + k) if yy < sy + 1 + n else _t(CONDUIT, 2 + k))
            p.px(sx, sy + 2 + n, FLAME[4] if night else FLAME[2])
    return (x0 - 1, x1 + 1)


def mini_pod(p: Pix, x, y, night, upright=False):
    """A pod as small as a mark, its glass full of glowing fluid between two caps of dark metal: lying on its side,
    11 by 6, beside SECTION A-A, or standing, 6 by 11, beside a strip's title."""
    k = -1 if night else 0
    rows = ["..mmmmmmm..", ".gGGGGGGGg.", "mgFfffffdgm", "mgffffffdgm", ".gddddddgg.", "..mmmmmmm.."]
    if upright:
        rows = ["".join(r[i] for r in rows[::-1]) for i in range(len(rows[0]))]
        rows = [r[::-1] for r in rows]
    pal = {"m": _t(METAL, 3 + k), "g": GLASS[3] if night else GLASS[4], "G": FLAME[5] if night else GLASS[6],
           "F": FLAME[5] if night else FLAME[4], "f": FLAME[4] if night else FLAME[3], "d": FLAME[2]}
    p.sprite(x, y, rows, pal)


# --------------------------------------------------------------------------- the phones
PHONE_SCENE = 60    # the rows a phone's H1 keeps under its words and notes for the fields
PHONE_LEAST = 48    # the fewest it stands them in
UNDER = {"H2": 76, "H3": 64}   # the rows a phone's H2 and H3 ask for under their words, whatever they say


def phone_fields(p: Pix, g, night, room) -> tuple:
    """A phone's H1 under its words, standing on the rule at row g and rising `room` rows, the fields across the
    phone: at the left a tower of pods glowing green round its spine, cables running up from it; at the right the
    harvester clinging to the next tower and drawing a pod out of its slot; and between them and along the foot the
    fields' towers standing in rows to the horizon, the glow of their pods over it. Returns its span."""
    top = g - room + 1
    fields(p, EDGE, p.w - EDGE, g, night, uid="pfld")
    horizon(p, EDGE, p.w - EDGE, g - 9, g - 1, night)
    levels = max(2, min(3, (room - 6) // 17))
    ttop = g - 17 * levels - 4
    crown_cables(p, 26, ttop, night, 6, 46, sky=top)
    tower(p, 26, ttop, g, night, False, levels, sky=top - 1)
    rt = ttop
    step_ = (g - rt - 17) // max(1, levels - 1)
    tower(p, p.w - 10, rt, g, night, False, levels, skip={(1, 0)}, sides=(0,), sky=top - 1)
    crown_cables(p, p.w - 10, rt, night, p.w - 30, p.w - 5, sky=top)
    harvester(p, 76, top + 2, night, False, (p.w - 10, rt, g), (p.w - 25, rt + 2 + step_), floor=g - 3)
    return (EDGE, p.w - EDGE)


def phone_awakening(p: Pix, g, night, room) -> tuple:
    """A phone's H2 under its words, standing on the rule at row g and rising `room` rows: the awakening across the
    phone (see `awakening`), the fields along its foot."""
    fields(p, EDGE, p.w - EDGE, g, night, uid="pfld")
    horizon(p, EDGE, p.w - EDGE, g - 7, g - 1, night)
    return awakening(p, 6, p.w - EDGE - 1, g, night, False, top=g - room + 2)


def phone_tree(p: Pix, g, night, room) -> tuple:
    """A phone's H3 under its words, standing on the rule at row g and rising `room` rows: the pod tree at the right,
    its upper bough arching right across the phone and its lower one half way, both hung with glowing pods (see
    `pod_tree`), and the fields along its foot."""
    fields(p, EDGE, p.w - EDGE, g, night, uid="pfld")
    horizon(p, EDGE, p.w - EDGE, g - 7, g - 1, night)
    return pod_tree(p, 8, p.w - EDGE - 1, g, night, False, g - room + 12, sky=g - room + 1, long=150, cut=70)


# --------------------------------------------------------------------------- the footers
FOOT_RISE = 5     # the rows a second course of conduit takes over the trench where the cells leave it room
FOOT_RUN = 24     # the fewest columns they rise along


def socket_pod(p: Pix, x, ground, night):
    """A pod on its socket after a footer's last cell, its foot on row `ground` from column x, 14 wide and 21 tall: a
    pod of glass full of glowing fluid with a sleeper curled in it, between caps of dark metal, plugged into a socket
    of riveted metal from which a cable runs down into the trench; by night its fluid burns phosphor, flickering, its
    light round it."""
    k = -1 if night else 0
    p.rect(x, ground - 3, 14, 4, _t(METAL, 3 + k))
    p.hline(x, x + 14, ground - 3, _t(METAL, 5 + k))
    p.hline(x + 1, x + 14, ground, METAL[0])
    p.vline(x + 13, ground - 2, ground + 1, METAL[0])
    for rx in (x + 2, x + 11):
        p.px(rx, ground - 2, _t(METAL, 6 + k))
    pod(p, x + 1, ground - 20, night, look=0)
    for yy in range(ground - 1, ground + 2):
        p.px(x + 14 + (yy - ground + 1), yy, _t(CONDUIT, 4 + k))
    if night:
        L = p.flicker(1)
        p.px(x + 4, ground - 14, FLAME[6], L)
        p.px(x + 8, ground - 9, FLAME[5], L)
        p.halo(x + 7, ground - 11, 10, 11, FLAME[3], (0.1, 0.2), L=p.flicker(1, back=True))


def footing(p: Pix, night: bool, rule: str, after=0):
    """A footer once its words are set: along its foot, over the conduit of the frame, the trench's cables, a heavy
    ribbed cable lit along its top with a thinner one laid on it, a pulse of phosphor running along it every so often,
    each unit of it a unit clear of every word; where the cells leave it room along FOOT_RUN columns or more a second
    course of ribbed conduit lies on the first, clamped in dark metal at its ends with a pulse of phosphor in it, the
    ruled lines between the cells left standing; and the rightmost place from column `after` on where the cells leave
    the sheet free, a pod plugged into its socket, glowing (see `socket_pod`), or a clamp of the conduit where there is
    less room. By night the pulses and the pod burn phosphor and flicker."""
    w, h = p.w, p.h
    k = -1 if night else 0
    ground = h - EDGE - 1

    def clear(x, y):
        return p.clear_of_words(x - 1, y - 1, x + 2, y + 2)

    def free(x0, y0, x1, y1):
        return EDGE + 1 <= x0 and x1 <= w - EDGE - 1 and y0 >= EDGE + 1 and \
            p.clear_of_words(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
    # The heavy cable over the frame's conduit and the thin one on it, and the pulses along them.
    for x in range(EDGE, w - EDGE):
        rib = x % 3 == 0
        for y, t in ((ground + 1, 5 if not rib else 3), (ground + 2, 3 if not rib else 2), (ground + 3, 1)):
            if clear(x, y):
                p.px(x, y, _t(CONDUIT, t + k))
        if clear(x, ground):
            p.px(x, ground, _t(CONDUIT, 2 + k) if (x // 9) % 2 else _t(CONDUIT, 4 + k))
    for i, x in enumerate(range(EDGE + 7, w - EDGE - 3, 23)):
        if clear(x, ground) and clear(x + 1, ground):
            L = p.flicker(i) if night else "base"
            p.px(x, ground, FLAME[5] if night else FLAME[3], L)
            p.px(x + 1, ground, FLAME[3] if night else FLAME[2], L)
    low = max((b[3] for b in p.words), default=0)
    ledge = max(ground - 3, low + 1)
    mark, taken = None, (0, 0)
    for kind, ew, eh in (("pod", 20, 22), ("clamp", 8, 8)):
        mark = next(((x, kind) for x in range(w - EDGE - 2 - ew, max(EDGE + 1, after), -1)
                     if free(x, ground - eh, x + ew, ground + 1)), None)
        if mark:
            taken = (mark[0] - 2, mark[0] + ew + 2)
            break
    lines = {x for x in range(w) if p.get(x, min(ledge, ground) - 2) == rule}
    rise = [x not in range(*taken) and not lines & {x - 1, x, x + 1} and
            free(x, ledge - FOOT_RISE - 1, x + 1, ledge) for x in range(w)]
    x = EDGE + 1
    while x < w - EDGE - 1:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - EDGE - 1) if not rise[i]), w - EDGE - 1)
        if b - x >= FOOT_RUN:
            for xx in range(x + 1, b - 1):          # a second course of conduit laid on the first
                rib = xx % 3 == 0
                p.px(xx, ground - 3, _t(CONDUIT, (6 if not rib else 4) + k))
                p.px(xx, ground - 2, _t(CONDUIT, (4 if not rib else 2) + k))
                p.px(xx, ground - 1, _t(CONDUIT, (2 if not rib else 1) + k))
                p.px(xx, ground, CONDUIT[0])
            for cx_ in (x + 1, b - 5):
                clamp(p, cx_, ground - 4, night, w=4, h=5)
            mid = (x + b) // 2
            L = p.flicker(x) if night else "base"
            p.px(mid, ground - 2, FLAME[5] if night else FLAME[3], L)
            p.px(mid + 1, ground - 2, FLAME[3] if night else FLAME[2], L)
        x = b
    if mark:
        x, kind = mark
        if kind == "pod":
            socket_pod(p, x + 2, ground, night)
        else:
            clamp(p, x + 1, ground - 6, night)


def rule_cable(p: Pix, x0, x1, y, seed, night):
    """Short lengths of cable laid along a rule from x0 to x1 on row y, every so often in the two rows over it: black
    rubber lit along its top, clamped in dark metal at its ends, a pulse of phosphor in it; each length two units clear
    of every word, sparser on a sheet's own rule under its tag."""
    k = -1 if night else 0
    every = (37, 61) if y > 21 else (53, 89)
    rnd = random.Random(seed)
    x = x0 + 6 + seed % 11
    while x + 12 < x1:
        n = rnd.choice((7, 9, 11))
        if p.clear_of_words(x - 2, y - 4, x + n + 2, y + 1):
            for xx in range(x, x + n):
                p.px(xx, y - 1, _t(CONDUIT, (4 if xx % 3 else 2) + k))
            for cx_ in (x, x + n - 1):
                p.px(cx_, y - 2, _t(METAL, 6 + k))
                p.px(cx_, y - 1, _t(METAL, 3 + k))
            p.px(x + n // 2, y - 1, FLAME[4] if night else FLAME[2])
        x += rnd.randrange(*every)


def sentinel_eye(p: Pix, x, y, night):
    """The machines watching from the corner of the closing notes, 9 by 7: a disc of dark metal lit along its upper
    left, three red eyes in it, the middle one burning."""
    k = -1 if night else 0
    m = _shade(METAL, k)
    rows = ["..ooooo..", ".oPPPPpo.", "oPeppEppo", "oPEppppdo", "opppeppdo", ".oddddoo.", "..ooooo.."]
    p.sprite(x, y, rows, {"o": METAL[0], "P": m(5), "p": m(3), "d": m(1), "e": EYE[3], "E": EYE[5]})


# --------------------------------------------------------------------------- the footers, links and badges
# A heart of glass filled with the phosphor fluid, 7 by 6: its glass (o, l where it catches the light), a little
# empty glass at its top, the fluid's bright surface (s) and the fluid under it, denser toward the point (a, b, c).
HEART = [".oo.oo.", "olsosao", "oaaaabo", ".oabbo.", "..obo..", "...o..."]


def heart(p: Pix, x, y, L="base"):
    """The heart of BUILT WITH (heart) BY, 7 by 6: a pod's glass in the shape of a heart, full of glowing fluid."""
    pal = {"o": GLASS[1], "l": GLASS[6], "s": FLAME[6], "a": FLAME[4], "b": FLAME[3], "c": FLAME[2]}
    p.sprite(x, y, HEART, pal, 1, L)


def tube_bar(p: Pix, x0, y0, w, h, period=5):
    """The graphic scale's bar as a tube of the pods' fluid banded in dark metal: a block of glowing phosphor and a
    clamp of metal by turns, `period` units each, the tube's top lit and its foot in shade."""
    for yy in range(y0, y0 + h):
        band = 0 if yy == y0 else 2 if yy == y0 + h - 1 else 1
        for xx in range(x0, x0 + w):
            lit = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (FLAME[5], FLAME[3], FLAME[1])[band] if lit else (METAL[5], METAL[3], METAL[1])[band])


# The link buttons' sprites, 9 by 7: a pod with its sleeper, the harvester's cluster of red eyes, a cable's copper
# plug and a bolt of the storm's green lightning, in their tones (see `icon_pal`).
ICONS = {
    "pod": ["..mMMMm..", ".gGfffdg.", ".gfSSfdg.", ".gfSssdg.", ".gffsfdg.", ".gfffddg.", "..mmmmm.."],
    "eyes": ["..ooooo..", ".oPPPPpo.", "oPeEpeEpo", "oPeepeepo", "opppeEppo", ".oppeepo.", "..ooooo.."],
    "plug": ["..c...c..", "..C...C..", ".mMMMMMm.", ".mMmmmmo.", "..mmmmo..", "....k....", "....k...."],
    "bolt": [".....FF..", "....FF...", "...Ff....", "..FFFFf..", "....Ff...", "...Ff....", "..f......"],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a link button by day or by night: the night's metal a tone down, its lights the same."""
    k = -1 if night else 0
    return {"m": _t(METAL, 2 + k), "M": _t(METAL, 5 + k), "o": METAL[0], "p": _t(METAL, 3 + k), "P": _t(METAL, 5 + k),
            "g": GLASS[3], "G": GLASS[6], "f": FLAME[3], "d": FLAME[1], "S": SKINS[1][3], "s": SKINS[1][2],
            "e": EYE[3], "E": EYE[5], "c": RAMP["copper"][5], "C": RAMP["copper"][3], "k": CONDUIT[4],
            "F": FLAME[5], "#": ink}


def conduit_top(p: Pix, x0, x1, y, night):
    """A run of ribbed conduit along a link button's top edge, row `y` its rim: the two rows over it ribbed, lit along
    their top, a clamp of dark metal at either end."""
    k = -1 if night else 0
    for x in range(x0, x1):
        rib = (x - x0) % 3 == 0
        p.px(x, y - 2, _t(CONDUIT, (4 if rib else 6) + k))
        p.px(x, y - 1, _t(CONDUIT, (1 if rib else 3) + k))
    for cx_ in (x0, x1 - 3):
        p.rect(cx_, y - 2, 3, 3, _t(METAL, 4 + k))
        p.px(cx_, y - 2, _t(METAL, 6 + k))


# --------------------------------------------------------------------------- the elements
def panel_node(p: Pix, x, y, w, h, night, seed, lid):
    """A schematic card as a pod's control panel: a strip of ribbed conduit down its icon cell's edge, a rivet in each
    of its corners, a lamp of phosphor at its foot's far corner, and on its lid, when it has one, a cable plugged into
    it, coiling away."""
    k = -1 if night else 0
    for yy in range(y + 1, y + h - 1):
        rib = (yy - y) % 3 == 0
        p.px(x + 10, yy, _t(CONDUIT, (5 if not rib else 3) + k))
        p.px(x + 11, yy, _t(CONDUIT, (3 if not rib else 1) + k))
        p.px(x + 12, yy, CONDUIT[0])
    for (rx, ry) in ((x + 2, y + 2), (x + w - 3, y + h - 3), (x + 2, y + h - 3)):
        p.px(rx, ry, _t(METAL, 5 + k))
    p.px(x + w - 6, y + h - 4, FLAME[5] if night else FLAME[3])
    p.px(x + w - 5, y + h - 4, FLAME[3] if night else FLAME[2])
    if lid:
        for i in range(6):
            p.px(x + 4 + i // 2, y - 1 - (i % 2), _t(CONDUIT, 4 + k))
        p.rect(x + 3, y - 1, 3, 2, _t(METAL, 3 + k))
        p.px(x + 3, y - 1, _t(METAL, 6 + k))


def data_cable(p: Pix, cells, night, seed):
    """The wire as a cable carrying the code: a pulse of phosphor every twelfth unit along it and a clamp of dark metal
    where it leaves its card and wherever it turns."""
    k = -1 if night else 0
    for i, (x, y, d) in enumerate(cells[2:-5]):
        if (i + seed) % 12 == 5:
            p.px(x, y, FLAME[5] if night else FLAME[3])
            if d == "h":
                p.px(x + 1, y, FLAME[3] if night else FLAME[2])
            else:
                p.px(x, y + 1, FLAME[3] if night else FLAME[2])
    turns = [cells[0]] + [c for i, c in enumerate(cells) if 0 < i < len(cells) - 4 and cells[i - 1][2] != c[2]]
    for (x, y, d) in turns:
        p.px(x - 1, y - 1, _t(METAL, 5 + k))
        p.px(x, y - 1, _t(METAL, 4 + k))
        p.px(x - 1, y, _t(METAL, 3 + k))
        p.px(x + 1, y + 1, METAL[0])


def fluid_tube(p: Pix, bx, base, bw, v, night):
    """A week's commits as a glass tube filled with the pods' fluid as high as the week ran, `v` units over the base
    line: pale glass walls lit at the left and in shade at the right, the fluid bright at its surface and denser
    toward the foot, a bubble or two in it, and a cap of dark metal on the tube."""
    k = -1 if night else 0
    top = base - v
    for yy in range(top, base):
        for xx in range(bx, bx + bw):
            if xx == bx:
                c = GLASS[5] if not night else GLASS[4]
            elif xx == bx + bw - 1:
                c = GLASS[2] if not night else GLASS[1]
            elif yy == top:
                c = FLAME[5] if not night else FLAME[6]
            else:
                f = (yy - top) / max(1, v)
                c = (FLAME[3] if f < 0.4 else FLAME[2] if f < 0.8 else FLAME[1]) if not night else \
                    (FLAME[4] if f < 0.4 else FLAME[3] if f < 0.8 else FLAME[2])
            p.px(xx, yy, c)
    if v >= 10 and bw >= 5:
        p.px(bx + 2, base - v // 3, FLAME[6])
        p.px(bx + bw - 3, base - 2 * v // 3, FLAME[6])
    if v >= 3:
        p.hline(bx - 1, bx + bw + 1, top - 1, _t(METAL, 3 + k))
        p.px(bx - 1, top - 1, _t(METAL, 6 + k))
        p.px(bx + bw, top - 1, METAL[0])


def bolt(p: Pix, x, y, night):
    """A bolt of the storm's lightning, 5 by 7, phosphor like every light: the busiest week struck."""
    rows = ["...FF", "..FF.", ".FFf.", "FFFFf", "..Ff.", ".Ff..", ".f..."]
    p.sprite(x, y, rows, {"F": FLAME[5] if night else FLAME[4], "f": FLAME[3] if night else FLAME[2]})


def conduit_ring(p: Pix, arc, night, ribs=True):
    """The dial's ring as a bend of ribbed conduit: black rubber lit along its upper left, ringed where its ribs run."""
    from ...holidays.pixel import tube
    k = -1 if night else 0

    def colour(s_, o, lam, x, y):
        t = max(1, min(6, round(1.3 + 4.5 * lam) + k))
        if ribs and int(s_ * 0.8) % 3 == 0:
            t = max(0, t - 2)
        return CONDUIT[t]
    tube(p, arc, 2.4, colour, outline=CONDUIT[0])


def eye_hub(p: Pix, cx, cy, night):
    """The dial's hub as a machine's eye: a red eye in a ring of dark metal, its core burning, lit at its upper
    left."""
    from ...holidays.pixel import sphere
    k = -1 if night else 0
    for (x, y) in ellipse(cx + 0.5, cy + 0.5, 4, 4):
        p.px(x, y, _t(METAL, 2 + k))
    sphere(p, cx + 0.5, cy + 0.5, 2.7, EYE, lo=2, hi=6)


def machine_wrapper(i, xx, yy, y0, y1, lift, night) -> str:
    """The `i`-th file type's wrapper at (xx, yy), by turns: a tube of the phosphor fluid with its bubbles, ribbed
    black conduit, riveted dark metal, a coil of copper, and the pods' pale glass. `lift` lights its top row and
    shades its foot."""
    k = -1 if night else 0
    kind = i % 5
    mid = (y0 + y1) // 2
    if kind == 0:
        c = FLAME[6] if ((xx * 7 + yy * 3) % 17 == 0 and yy > y0) else FLAME[3] if yy < mid else FLAME[2]
        R = FLAME
    elif kind == 1:
        c = _t(CONDUIT, (5 if xx % 3 else 3) + k)
        R = CONDUIT
    elif kind == 2:
        c = _t(METAL, (6 if (xx % 6 == 2 and yy == mid) else 4) + k)
        R = METAL
    elif kind == 3:
        c = _t(RAMP["copper"], (5 if yy % 2 else 3) + k)
        R = RAMP["copper"]
    else:
        c = GLASS[6] if xx % 9 == 3 else GLASS[4]
        R = GLASS
    return R[max(0, min(6, R.index(c) + lift))]


def screen_cell(q: Pix, ox, oy, night):
    """A counter's cell as a little screen, 11 by 15: dark glass in a bezel of dark metal lit along its top and
    left, a gleam in the glass's upper left corner."""
    k = -1 if night else 0
    for yy in range(oy, oy + 15):
        for xx in range(ox, ox + 11):
            edge = xx in (ox, ox + 10) or yy in (oy, oy + 14)
            if edge:
                c = _t(METAL, (5 if (xx == ox or yy == oy) else 1) + k)
            else:
                c = GLASS[0] if not night else METAL[0]
            q.px(xx, yy, c)
    q.px(ox + 1, oy + 1, GLASS[2])
    q.px(ox + 2, oy + 1, GLASS[1])


def cable_line(p: Pix, x0, x1, y, night):
    """The time line as a heavy cable from x0 to x1, three rows deep at row y: lit along its top, ribbed, dark at its
    foot, a pulse of phosphor along it every so often."""
    k = -1 if night else 0
    for x in range(x0, x1):
        rib = x % 3 == 0
        p.px(x, y, _t(CONDUIT, (5 if not rib else 3) + k))
        p.px(x, y + 1, _t(CONDUIT, (3 if not rib else 2) + k))
        p.px(x, y + 2, CONDUIT[0])
    for x in range(x0 + 8, x1 - 3, 19):
        p.px(x, y + 1, FLAME[5] if night else FLAME[3])


def release_pod(p: Pix, x, gy, kind, night, i=0):
    """A release on the cable: a pod standing on it, glowing, for a release; a stub of a tower with two pods for a big
    one; a bead of phosphor for a patch; an empty pod, its glass dark, for one still to come; and for the
    repository's beginning the foot of the first tower."""
    k = -1 if night else 0
    if kind == "minor":
        p.px(x, gy - 1, FLAME[5] if night else FLAME[3])
        p.px(x, gy - 2, FLAME[3] if night else FLAME[2])
        return
    if kind == "made":
        p.rect(x - 1, gy - 8, 3, 8, _t(METAL, 3 + k))
        p.vline(x - 1, gy - 8, gy, _t(METAL, 5 + k))
        p.hline(x - 3, x + 4, gy - 1, _t(METAL, 4 + k))
        return
    if kind == "big":
        p.rect(x - 1, gy - 14, 3, 14, _t(METAL, 3 + k))
        p.vline(x - 1, gy - 14, gy, _t(METAL, 5 + k))
        small_pod(p, x - 9, gy - 13, night, False)
        small_pod(p, x + 3, gy - 13, night, False)
        return
    if kind == "next":
        rows = ["..mMm..", ".mMMMm.", "g.....g", "g.....g", "g.....g", "g.....g", ".g...g.", ".mmmmm."]
        p.sprite(x - 3, gy - 8, rows, {"m": _t(METAL, 2 + k), "M": _t(METAL, 4 + k), "g": GLASS[3]})
        return
    small_pod(p, x - 3, gy - 11, night, False)


def pod_avatar(p: Pix, cx, cy, i, person, night):
    """A contributor as a sleeper's pod, 11 by 15: their initials dark on its glowing fluid between its caps of dark
    metal; a bot is the machines' eye, three red eyes in a disc of dark metal."""
    from ...holidays.pixel import measure
    k = -1 if night else 0
    x, y = cx - 5, cy - 7
    if not person.get("initials"):
        for (xx, yy) in ellipse(cx + 0.5, cy + 0.5, 7, 7):
            lam = light((xx + 0.5 - cx) / 7, (yy + 0.5 - cy) / 7, 0.6)
            p.px(xx, yy, _t(METAL, 1 + round(4 * lam) + k))
        for ex, ey in ((-3, -1), (2, -1), (0, 2)):
            p.rect(cx + ex, cy + ey, 2, 2, EYE[3])
            p.px(cx + ex, cy + ey, EYE[5])
        return
    for yy in range(y, y + 15):
        for xx in range(x, x + 11):
            cap = yy in (y, y + 1, y + 13, y + 14)
            if cap and xx in (x, x + 10):
                continue
            if cap:
                c = _t(METAL, (5 if yy in (y, y + 13) else 2) + k)
            elif xx == x:
                c = GLASS[5] if not night else GLASS[4]
            elif xx == x + 10:
                c = GLASS[2] if not night else GLASS[1]
            else:
                c = FLAME[3] if yy < y + 9 else FLAME[2]
            p.px(xx, yy, c)
    ini = str(person["initials"])[:2]
    p.text(cx - measure(ini, "35") // 2, cy - 2, ini, X["pod_ink"], "35")


def filled_share(p: Pix, x, y, w, fill, night):
    """A contributor's share as a tube filling with the fluid as far as their commits go, in a rim of dark metal."""
    k = -1 if night else 0
    p.box(x, y, w + 2, 4, _t(METAL, 3 + k))
    for xx in range(w):
        lit = xx < fill
        p.px(x + 1 + xx, y + 1, (FLAME[5] if night else FLAME[4]) if lit else GLASS[5] if not night else GLASS[1])
        p.px(x + 1 + xx, y + 2, (FLAME[3] if night else FLAME[2]) if lit else GLASS[3] if not night else GLASS[0])


def cable_wreath(p: Pix, cx, cy, r0, r1, n, night):
    """A ring of ribbed conduit round the seal from r0 to r1, clamped in dark metal at its quarters and between."""
    k = -1 if night else 0
    ring = [(cx + (r0 + r1) / 2 * math.cos(math.radians(a)), cy + (r0 + r1) / 2 * math.sin(math.radians(a)))
            for a in range(0, 361, 4)]
    from ...holidays.pixel import tube

    def colour(s_, o, lam, x, y):
        t = max(1, min(6, round(1.3 + 4.5 * lam) + k))
        if int(s_ * 0.8) % 3 == 0:
            t = max(0, t - 2)
        return CONDUIT[t]
    tube(p, ring, (r1 - r0) / 2 - 0.2, colour, outline=CONDUIT[0])
    rad = (r0 + r1) / 2
    for j in range(8):
        ang = math.radians(j * 45 - 90)
        clamp(p, round(cx + math.cos(ang) * rad - 2), round(cy + math.sin(ang) * rad - 2), night, w=4, h=4)


def metal_board(p: Pix, night):
    """The placard as a panel of the towers' dark metal in the conduit: the sky inside the frame, and a rivet in each
    corner of it."""
    paper(p, night, uid="pl")
    frame(p, night)
    k = -1 if night else 0
    for (x, y) in ((7, 7), (p.w - 8, 7), (7, p.h - 8), (p.w - 8, p.h - 8)):
        p.px(x, y, _t(METAL, 6 + k))
        p.px(x + 1, y + 1, METAL[0])


# --------------------------------------------------------------------------- the storm across the sky
# The storm's clouds in one stretch of their drift, CLOUD_P wide, from the top of the band they drift in: a back
# row of heavy clouds, a front row hanging lower under it, and a few lobes lower still, each row as puffs (x, y, r).
ROWS = (((10, 0, 14, 8), (34, -2, 16, 9), (58, 0, 13, 8), (80, -1, 12, 6), (100, 1, 10, 6)),
        ((20, 9, 10, 6), (38, 12, 12, 7), (57, 10, 9, 5), (88, 7, 7, 3)),
        ((29, 19, 7, 4), (46, 21, 6, 4), (38, 25, 4, 2.5)))
CLOUD_P = 104
CLOUD_DRIFT = 40.0   # the seconds the clouds take to drift a stretch to the right


def _crawler(x0, x1, y, seed, strike: int = 0) -> dict:
    """Lightning crawling through the clouds from column x0 to x1 about row y, as {(x, y): part}: a jagged channel
    of short zigzags a unit wide, and forks dropping from it here and there, each jagged too, the first of them
    `strike` units long when it is given, a bolt striking down out of the clouds."""
    rnd = random.Random(seed)
    cells = {}
    yy, xx, pts = y, x0, []
    while xx < x1:
        dy = rnd.choice((-1, 1)) if abs(yy - y) < 4 else (1 if yy < y else -1)
        for _ in range(rnd.randint(2, 5)):
            pts.append((xx, yy))
            xx += 1
            yy += dy if rnd.random() < 0.7 else 0
    for (px_, py_) in pts:
        cells[(px_, py_)] = "core"
    for k in range(3):
        fx, fy = pts[(k * 2 + 1) * len(pts) // 7]
        d = rnd.choice((-1, 1))
        bolt = k == 0 and strike
        for j in range(strike if bolt else rnd.randint(6, 10)):
            if rnd.random() < (0.3 if bolt else 0.6):
                fx += d if not bolt or j % 7 < 4 else -d
            cells.setdefault((fx, fy + 1 + j), "core" if bolt else "fork")
    return cells


def storm(p: Pix, night: bool, motion: bool, band, title, mark, keep: bool = True, strike: int = 0):
    """The signature of a header's sky: the storm across its top, heavy clouds in two rows and a few lobes hanging
    under them, each row lit along its upper left and dark along its foot, drifting slowly to the right, a stretch
    every 40 seconds; and lightning crawling through them, forked, phosphor like every light, lighting the clouds
    round it as it strikes, twice in quick succession on the storm's loop, first through the clouds at the left and
    then those at the right. It passes behind the title and through the top band, but never into the month's mark
    (`mark`), and ends above the words under the title; behind the title's letters (`title`) it is fainter, so they
    read through it. `band` is the box it fills. The still file holds the clouds where they start and the first
    lightning struck (when `keep` says so)."""
    x0, y0, x1, y1 = band
    tones = ((FLAME[0], STORM[4], STORM[3]), (FLAME[1], STORM[5], STORM[3]), (FLAME[1], STORM[6], STORM[4])) \
        if night else ((ASH[2], ASH[5], ASH[3]), (ASH[1], ASH[4], ASH[2]), (ASH[0], ASH[3], ASH[1]))
    rows = []
    for n, (row, (dark, lit, body)) in enumerate(zip(ROWS, tones)):
        sid = f"cr{n}"
        p.defs.append(f'<g id="{sid}">' + "".join(f'<ellipse cx="{cx}" cy="{num(y0 + cy)}" rx="{rx}" ry="{num(ry)}"/>'
                                                  for cx, cy, rx, ry in row) + "</g>")
        rows.append(f'<use href="#{sid}" y="2" fill="{dark}"/><use href="#{sid}" x="-1" y="-1" fill="{lit}"/>'
                    f'<use href="#{sid}" fill="{body}"/>')
    p.defs.append(f'<g id="ct">{"".join(rows)}</g>')
    tx0, ty0, tx1, ty1 = title
    p.defs.append(f'<mask id="cm" maskUnits="userSpaceOnUse" x="0" y="0" width="{p.w}" height="{y1}">'
                  f'<rect x="{x0}" y="{y0 - 10}" width="{x1 - x0}" height="{y1 - y0 + 10}" fill="{C["white"]}"/>'
                  f'<rect x="{tx0}" y="{ty0}" width="{tx1 - tx0}" height="{ty1 - ty0}"/>'
                  f'<rect x="{tx0}" y="{ty0}" width="{tx1 - tx0}" height="{ty1 - ty0}" fill="{C["white"]}" '
                  f'fill-opacity=".5"/>'
                  f'<rect x="{mark[0]}" y="{mark[1]}" width="{mark[2] - mark[0]}" height="{mark[3] - mark[1]}"/>'
                  f'</mask>')
    uses = "".join(f'<use href="#ct" x="{n * CLOUD_P}"/>' for n in range(-1, p.w // CLOUD_P + 1))
    head = '<g mask="url(#cm)">'
    vals = ";".join(f"{i} 0" for i in range(0, CLOUD_P, 2))
    drift = (f'<animateTransform attributeName="transform" type="translate" values="{vals}" '
             f'dur="{num(CLOUD_DRIFT)}s" repeatCount="indefinite" calcMode="discrete"/>')
    p.raw(-9, head + f'<g>{uses}{drift if motion else ""}</g></g>', head + uses + "</g>")
    core, glow, fork = (FLAME[6], FLAME[3], FLAME[5]) if night else (FLAME[4], FLAME[2], FLAME[3])
    mid = (mark[0] + mark[2]) // 2
    for n, ((a, b), t0) in enumerate((((x0 + 58, mark[0] - 2), 0.43), ((mark[2] + 2, x1 - 56), 0.86))):
        cells = _crawler(a, b, y0 + 9 + 3 * n, seed=11 + n * 6, strike=0 if n else strike)
        ids = []
        for part in ("core", "fork"):
            p.symbol(("crawl", n, part), {q: 1 for q, v in cells.items() if v == part}, mono=True)
            ids.append(p.syms[("crawl", n, part)])
        pix = (f'<use href="#{ids[0]}" x="1" y="1" stroke="{glow}"/><use href="#{ids[0]}" stroke="{core}"/>'
               f'<use href="#{ids[1]}" stroke="{fork}"/>')
        light = "".join(f'<circle cx="{xx}" cy="{yy}" r="9"/>' for (xx, yy) in
                        sorted(q for q, part in cells.items() if part == "core")[::18])
        group = (f'<g fill="{FLAME[3]}" fill-opacity=".12">{light}</g>' if night else "") + pix
        if night and n == 0 and motion:                       # the whole sky flashes, faintly, as it strikes
            group = (f'<rect x="{x0}" y="{y0 - 10}" width="{x1 - x0}" height="{p.h - y0 - 2}" fill="{FLAME[3]}" '
                     f'fill-opacity=".05"/>') + group
        still = head + group + "</g>" if keep and n == 0 else ""
        if not motion:
            if still:
                p.raw(-8, still, still)
            continue
        a_, b_, c_, d_ = t0, t0 + 0.02, t0 + 0.04, t0 + 0.065
        p.raw(-8, f'{head}<g opacity="0">{group}<animate attributeName="opacity" values="0;1;0;1;0" '
                  f'keyTimes="0;{a_:g};{b_:g};{c_:g};{d_:g}" dur="{num(STORM_LOOP)}s" repeatCount="indefinite" '
                  f'calcMode="discrete"/></g></g>', still)
    return mid
