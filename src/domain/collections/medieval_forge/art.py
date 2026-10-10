# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Forge set's scenery and sprites, drawn on the shared pixel canvas.

The hammered plate and its frame of riveted bands, the strip of mail across the top, the titles of polished
steel and of red-hot iron, the embers that rise by night, and the smithy a header stands in: the hearth
and its fire, the bellows, the anvil with a blade on it, the smith and the hammer he swings, the sparks,
the quench bucket, the rack of shields and axes; the armoury's trophy, the shield with the smith's arms under
a helm with two swords crossed behind it; and a footer's floor of the hearth's stone with coal heaped on it and
the smith's anvil at its end. Every sprite is shaded from the one light in the upper left on the set's own ramps,
and outlined in the iron's darkest; by night the forge lights what stands near it from below. The fire, its coals,
its embers and its sparks burn on the collection's flame, and the smith's skin is the collection's skin (see
`collections.hand`)."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import BLINKS, FONTS, LX, LY, LZ, Paint, Pix, cylinder, fold, num, sphere
from ..hand import MEDIEVAL
from .palette import C, NIGHT_SKY, RAMP, X

IRON, STEEL, COAL, EMBER, FLAME = RAMP["iron"], RAMP["steel"], RAMP["coal"], RAMP["ember"], RAMP["flame"]
BRASS, LEATHER, OAK, STONE, SKIN = RAMP["brass"], RAMP["leather"], RAMP["oak"], RAMP["stone"], RAMP["skin"]
FIRE = RAMP["fire"]             # the hand's flame: the forge's fire, its coals, its embers, its sparks and hot blade

# The loops the smithy moves on, in seconds, each a figure's loop of 4 to 8 by the hand: the hammer's swing with
# its sparks, and the bellows' breath with the fire that answers it. They differ, so the two never fall into step.
SWING, BREATH = 4.0, 5.2


def _pal(**tones) -> dict:
    return dict(tones)


# --------------------------------------------------------------------------- the plate
# A hammer's dent in the plate, as cells from its top-left: the hollow, the wall of it that faces the light (its
# lower right), and the rim it raised, which catches the light along its upper left.
DENT_HOLLOW = ((1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (2, 2), (3, 2), (2, 3))
DENT_WALL = ((4, 1), (3, 2), (2, 3))
DENT_RIM = ((1, -1), (2, -1), (3, -1), (0, 0), (-1, 1), (0, 2))
# Where the dents lie in a tile of the plate, and the streaks of its brushed grain (row, from, length).
DENTS = ((3, 4), (21, 2), (30, 13), (9, 17), (16, 27), (33, 30), (25, 36))
GRAIN = ((1, 10, 9), (7, 26, 12), (12, 0, 7), (15, 31, 8), (20, 8, 11), (24, 22, 6), (29, 35, 5), (35, 3, 10),
         (38, 18, 9), (6, 2, 4), (27, 1, 5), (18, 36, 4))


def _plate_rows() -> list:
    """The cells of a tile of the hammered plate, as rows for a path, by their part: the dents' hollows, their
    lit walls and their raised rims, and the brushed grain between them."""
    rows: list = [{}, {}, {}, {}]
    for (dx, dy) in DENTS:
        for (i, j) in DENT_HOLLOW:
            rows[1 if (i, j) in DENT_WALL else 0].setdefault(dy + j, []).append(dx + i)
        for (i, j) in DENT_RIM:
            rows[2].setdefault(dy + j, []).append(dx + i)
    for (y, x0, n) in GRAIN:
        rows[3].setdefault(y, []).extend(range(x0, x0 + n))
    return rows


def _plate_tile(uid: str, tones: tuple, size: int = 40, shared: str = "") -> str:
    """A pattern tile of the hammered plate in `tones`, its hollows', walls', rims' and grain's (a tile with
    three tones has no grain). With `shared`, the ids' stem of the tile's parts drawn once in `<defs>` (see
    `paper`), the tile places those."""
    if shared:
        body = "".join(f'<use href="#{shared}{i}" stroke="{tone}"/>' for i, tone in enumerate(tones))
    else:
        body = "".join(f'<path stroke="{tone}" d="{Pix._d(r)}"/>' for tone, r in zip(tones, _plate_rows()))
    return f'<pattern id="{uid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">{body}</pattern>'


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dents=True, uid="p"):
    """The ground a drawing sits on: a hammered iron plate, gunmetal by day and lit from above, its dents and
    brushed grain across it; by night the same plate lit from below by the forge, dark at the top and warm at
    the foot, in five bands, its dents cool in the dark upper half and warm in the lower. The night's two tiles
    differ only in their tones, so the parts of a tile are drawn once and both tiles place them. A drawing made
    lighter leaves the grain out and keeps the dents."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    parts = 3 if p.lite else 4
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["plate"]}"/>')
        if dents:
            tones = (X["dent_lo"], X["dent_wall"], X["dent_hi"], X["grain_lo"])[:parts]
            p.defs.append(_plate_tile(f"{uid}d", tones))
            p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')
        return
    n = len(NIGHT_SKY)
    edges = [y + round(i * h / n) for i in range(n + 1)]
    for i, col in enumerate(NIGHT_SKY):
        p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    if dents:
        mid = edges[3]
        cool = (X["dent_n_lo"], X["dent_n_wall"], X["dent_n_hi"], X["grain_n"])[:parts]
        warm = (X["dent_w_lo"], X["dent_w_wall"], X["dent_w_hi"], X["grain_w"])[:parts]
        p.defs.append("".join(f'<path id="{uid}t{i}" d="{Pix._d(r)}"/>' for i, r in enumerate(_plate_rows()[:parts])))
        p.defs.append(_plate_tile(f"{uid}n", cool, shared=f"{uid}t"))
        p.defs.append(_plate_tile(f"{uid}w", warm, shared=f"{uid}t"))
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{mid - y}" fill="url(#{uid}n)"/>')
        p.under.append(f'<rect x="{x}" y="{mid}" width="{w}" height="{y + h - mid}" fill="url(#{uid}w)"/>')


# --------------------------------------------------------------------------- rivets and the frame
def rivet(p: Pix, x, y, L="base", night=False, warm=False, brass=False):
    """A rivet's domed head, two pixels square at (x, y): lit on the upper left, shaded on the lower right;
    `warm` turns it round for a rivet the forge lights from below, `brass` is one of brass."""
    if brass:
        a, b, c, d = (BRASS[4], BRASS[2], BRASS[2], BRASS[0]) if night else (BRASS[5], BRASS[3], BRASS[3], BRASS[1])
    elif warm:
        a, b, c, d = STONE[2], STONE[4], STONE[4], STONE[6]
    elif night:
        a, b, c, d = IRON[5], IRON[3], IRON[3], COAL[1]
    else:
        a, b, c, d = C["white"], STEEL[4], STEEL[4], IRON[2]
    p.px(x, y, a, L)
    p.px(x + 1, y, b, L)
    p.px(x, y + 1, c, L)
    p.px(x + 1, y + 1, d, L)


def _band_tile(uid: str, rows: list, rivet_cols: tuple, vertical: bool, period: int = 10) -> str:
    """A pattern tile of one riveted band: `rows` are the band's four tones across its width, `rivet_cols` the
    four tones of the rivet set in its middle two rows every `period` pixels."""
    cells: dict = {}
    for i in range(period):
        for j, tone in enumerate(rows):
            cells[(j, i) if vertical else (i, j)] = tone
    (a, b, c, d) = rivet_cols
    for (dx, dy, tone) in ((0, 1, a), (1, 1, b), (0, 2, c), (1, 2, d)):
        i, j = 4 + dx, dy
        cells[(j, i) if vertical else (i, j)] = tone
    by: dict = {}
    for (cx, cy), tone in cells.items():
        by.setdefault(tone, {}).setdefault(cy, []).append(cx)
    body = "".join(f'<path stroke="{tone}" d="{Pix._d(rows_)}"/>' for tone, rows_ in by.items())
    w, h = (4, period) if vertical else (period, 4)
    return f'<pattern id="{uid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{body}</pattern>'


def _band_tones(night: bool, warm: bool = False) -> tuple:
    """A band's four tones, outer edge to inner, and its rivet's four."""
    if warm:
        return (COAL[1], STONE[3], STONE[5], COAL[1]), (STONE[3], STONE[4], STONE[5], STONE[6])
    if night:
        return (COAL[1], IRON[4], IRON[2], COAL[1]), (IRON[5], IRON[3], IRON[3], COAL[1])
    return (COAL[2], STEEL[6], STEEL[4], IRON[1]), (C["white"], STEEL[4], STEEL[4], IRON[2])


def corner_plate(p: Pix, x, y, night: bool, warm: bool = False, size: int = 7, L="base"):
    """A square plate over a corner of the frame, bevelled, held by four brass rivets, and throwing a shadow on
    the plate below and to its right."""
    face = STONE[4] if warm else (IRON[3] if night else STEEL[4])
    light = STONE[5] if warm else (IRON[5] if night else C["white"])
    dark = COAL[1] if (night or warm) else IRON[1]
    p.rect(x, y, size, size, face, L)
    p.bevel(x, y, size, size, light, dark, L)
    p.box(x - 1, y - 1, size + 2, size + 2, IRON[0], L)
    for i in range(size + 3):
        p.apx(x + size + 1, y + i, X["shade_ink"], 0.3, "haze")
        p.apx(x + i, y + size + 1, X["shade_ink"], 0.3, "haze")
    for (dx, dy) in ((1, 1), (size - 3, 1), (1, size - 3), (size - 3, size - 3)):
        rivet(p, x + dx, y + dy, L, night, brass=True)


def iron_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, uid="fr", corners=True):
    """The sheet's border: riveted iron bands four pixels thick along every edge, each a pattern tile so
    the border costs a few hundred bytes however long it runs, standing proud of the plate with a lit top face
    and a shadow thrown below them, and a plate over each corner. By night the foot band and the lower half of
    the sides are lit from below by the forge."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    cool_rows, cool_riv = _band_tones(night)
    p.defs.append(_band_tile(f"{uid}h", list(cool_rows), cool_riv, False))
    p.defs.append(_band_tile(f"{uid}v", list(cool_rows), cool_riv, True))
    if night:
        warm_rows, warm_riv = _band_tones(night, warm=True)
        p.defs.append(_band_tile(f"{uid}w", list(warm_rows)[::-1], warm_riv, False))
        p.defs.append(_band_tile(f"{uid}u", list(warm_rows), warm_riv, True))
    foot = f"{uid}w" if night else f"{uid}h"
    mid = y + h * 3 // 5
    bands = [(x, y, w, 4, f"{uid}h"), (x, y + h - 4, w, 4, foot)]
    if night:
        bands += [(x, y, 4, mid - y, f"{uid}v"), (x + w - 4, y, 4, mid - y, f"{uid}v"),
                  (x, mid, 4, y + h - mid, f"{uid}u"), (x + w - 4, mid, 4, y + h - mid, f"{uid}u")]
    else:
        bands += [(x, y, 4, h, f"{uid}v"), (x + w - 4, y, 4, h, f"{uid}v")]
    for (bx, by, bw, bh, name) in bands:
        p.shapes["base"].append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#{name})"/>')
    # the shadow the raised bands throw on the plate, below the top one and right of the left one
    a = 0.3 if not night else 0.4
    for xx in range(x + 4, x + w - 4):
        p.apx(xx, y + 4, X["shade_ink"], a, "haze")
    for yy in range(y + 5, y + h - 4):
        p.apx(x + 4, yy, X["shade_ink"], a, "haze")
    if corners:
        corner_plate(p, x + 1, y + 1, night)
        corner_plate(p, x + w - 8, y + 1, night)
        corner_plate(p, x + 1, y + h - 8, night, warm=night)
        corner_plate(p, x + w - 8, y + h - 8, night, warm=night)


def rivet_run(p: Pix, x0, x1, y, night: bool, spacing: int = 11, L="base", seed=0):
    """Rivets along a seam whose line is row `y`: a dome every `spacing` pixels straddling the line, every
    other one of them on a drawing made lighter. The run is one strip filled with a tile of its rivet, drawn
    once a file, which lies under whatever is drawn over the seam after it, as the rivets' own pixels would; the
    cells it covers are kept as `studs`, so the forge's light falls on them as on anything drawn (see `heat`)."""
    step = spacing * (2 if p.lite else 1)
    xs = range(x0 + 2 + (seed * 3) % 5, x1 - 1, step)
    if not xs:
        return
    pid = f"rv{step}{'n' if night else 'd'}"
    if ("pattern", pid) not in p.syms:
        q = Pix(2, 2)
        rivet(q, 0, 0, night=night, warm=night)
        p.defs.append(f'<pattern id="{pid}" width="{step}" height="2" patternUnits="userSpaceOnUse">'
                      f'{q._paths(q.layers["base"])}</pattern>')
        p.syms[("pattern", pid)] = pid
    L = p.layer(L)
    if not hasattr(p, "studs"):
        p.studs = set()
    for x in xs:
        for cell in ((x, y - 1), (x + 1, y - 1), (x, y), (x + 1, y)):
            p.layers[L].pop(cell, None)          # the rivet covers what was drawn there before it
            p.studs.add(cell)
    p.shapes[L].append(f'<rect width="{xs[-1] + 2 - xs[0]}" height="2" fill="url(#{pid})" '
                       f'transform="translate({xs[0]} {y - 1})"/>')


# --------------------------------------------------------------------------- the mail across the top
def _mail_cells(width: int, sag: int, night: bool) -> dict:
    """One span of a mail strip, five rows deep, hung between two hooks `width` apart and sagging by `sag`:
    staggered rows of rings, each ring's crown catching the light and its sides turning from it, dark where
    the holes show through. By night the lowest rows warm in the forge's light."""
    crown, side, hole = (IRON[5], IRON[3], COAL[0]) if night else (STEEL[5], STEEL[3], IRON[1])
    cells = {}
    for i in range(width):
        t = i / max(1, width)
        top = round(sag * 4 * t * (1 - t))
        for j in range(5):
            r = j // 2
            k = (i + 2 * (r % 2)) % 4
            if j % 2 == 0:
                tone = crown if k in (1, 2) else hole
            else:
                tone = side if k in (0, 3) else hole
            if night and j >= 4 and tone is not hole:
                tone = STONE[4] if tone is side else STONE[5]
            cells[(i, top + j)] = tone
    return cells


def mail(p: Pix, x0, x1, y, night: bool, sag: int = 3, span: int = 41, L="base"):
    """A strip of mail hung across the top of a sheet from rivet hooks, sagging between them: one span drawn
    once and placed as often as it repeats, the hooks over it."""
    n = max(1, round((x1 - x0) / span))
    width = (x1 - x0) // n
    key = ("mail", width, sag, night)
    if key not in p.syms:
        p.symbol(key, _mail_cells(width, sag, night))
    for i in range(n):
        p.use(key, x0 + i * width, y, L)
    for i in range(n + 1):
        hx = min(x0 + i * width, x1 - 2)
        rivet(p, hx, y - 1, L, night)


# --------------------------------------------------------------------------- titles
def steel_fill(r, c, scale, night):
    """Polished steel over a title's letters, a band for each row of the face: bright at the crown, darkening,
    a hard white line where the steel reflects the light across its middle, and darker again to the foot."""
    band = min(6, r // scale)
    return (STEEL[6], STEEL[5], STEEL[4], C["white"], STEEL[4], STEEL[3], STEEL[2])[band]


def hot_fill(r, c, scale, night, variant=2):
    """Red-hot iron cooling, a band for each row of the face: dark ember red at the edges through orange to
    the yellow and white heat at the core. The letters toward the middle of a line (`variant` 2) are hottest;
    those at its ends (0) have cooled the most."""
    band = min(6, r // scale)
    if variant >= 2:
        return (EMBER[3], EMBER[5], FLAME[4], FLAME[6], FLAME[4], EMBER[5], EMBER[3])[band]
    if variant == 1:
        return (EMBER[2], EMBER[4], FLAME[3], FLAME[5], FLAME[3], EMBER[4], EMBER[2])[band]
    return (EMBER[2], EMBER[3], EMBER[5], FLAME[4], EMBER[5], EMBER[3], EMBER[1])[band]


def _heat(mid: float) -> int:
    return 2 if 0.3 <= mid <= 0.7 else (1 if 0.12 <= mid <= 0.88 else 0)


# The titles' paints: steel by day, iron fresh from the fire by night.
STEEL_PAINT = Paint("steel", steel_fill)
HOT_PAINT = Paint("hot", hot_fill, variant=_heat)


def _level(ch: str, d: float = 0) -> str:
    """A letter of the title face as path data in its own units, every run of each row one level stroke along the
    row's middle, `d` longer at each end."""
    parts, at = [], None
    for r, cols in enumerate(FONTS["57"][0][ch][1]):
        runs, start, prev = [], None, None
        for cc in sorted(cols):
            if prev is not None and cc == prev + 1:
                prev = cc
                continue
            if prev is not None:
                runs.append((start, prev - start + 1))
            start = prev = cc
        if prev is not None:
            runs.append((start, prev - start + 1))
        for (rx, rw) in runs:
            sx, sy = rx - d, r + 0.5
            parts.append(f"M{num(sx)} {num(sy)}h{num(rw + 2 * d)}" if at is None
                         else f"m{num(sx - at[0])} {num(sy - at[1])}h{num(rw + 2 * d)}")
            at = (sx + rw + 2 * d, sy)
    return "".join(parts)


def _glow_glyph(p: Pix, ch: str, scale: int, k: int) -> str:
    """A letter's glow ring `k` canvas pixels out, in the face's units: its rows as strokes `k / scale` longer at
    each end and as much wider each way, the path `Pix.text` draws a glow ring with. Returns its id."""
    key = ("glow", ("glyph", "57", ch), scale, k)
    if key not in p.syms:
        d = k / scale
        sid = f"q{len(p.syms)}"
        p.defs.append(f'<path id="{sid}" stroke-width="{num(1 + 2 * d)}" d="{_level(ch, d)}"/>')
        p.syms[key] = sid
    return p.syms[key]


def _rows_glyph(p: Pix, ch: str) -> str:
    """A letter of the title face as one path in `<defs>`: a level stroke along each run of each row, the cells
    `Pix.text` inks for it, which a wider stroke widens the same way up and down the whole letter. Returns its
    id."""
    key = ("level", ch)
    if key not in p.syms:
        sid = f"q{len(p.syms)}"
        p.defs.append(f'<path id="{sid}" d="{_level(ch)}"/>')
        p.syms[key] = sid
    return p.syms[key]


def _placed(uses: list) -> str:
    """Uses of symbols, each (id, offset along the line), as markup."""
    return "".join(f'<use href="#{ref}" x="{dx}"/>' if dx else f'<use href="#{ref}"/>' for ref, dx in uses)


def _together(p: Pix, key, uses: list, scale: int = 1) -> tuple:
    """Symbols set together as one, kept once a file under `key`: `uses` are each one's (id, offset along the
    line), drawn `scale` times over. Returns its key, for `Pix.use`."""
    if key not in p.syms:
        sid = f"q{len(p.syms)}"
        p.defs.append(f'<g id="{sid}" transform="scale({scale})">{_placed(uses)}</g>' if scale != 1
                      else f'<g id="{sid}">{_placed(uses)}</g>')
        p.syms[key] = sid
    return key


def title(p: Pix, x, y, s, scale, colour, edge, shadow=None, paint=None, bevel=None, glow=None, night=False,
          L="base") -> int:
    """A title's line set from (x, y), as `Pix.text` sets it with a `paint`, a `bevel` and a `glow`, over a
    `shadow` half a font pixel down and to the right and a dark `edge` a pixel round every letter, but light
    however long it runs: the letters are drawn once as a symbol for each run of them one paint covers, the
    line once as a symbol of its runs, and each is placed whole. Its edge is the line four times a pixel off,
    and each ring of its glow a symbol of its letters' rings, which a drawing made lighter lays from the line
    itself where it can (see below). Returns the line's width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    placed, cx = [], x
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale

    def stroke_of(ch, gx):
        """The paint of the letter `ch` set at `gx`: a variant of the title's by where it falls along the line."""
        if not paint:
            return colour
        variant = paint.variant((gx + glyphs[ch][0] * scale / 2 - x) / max(1, w)) if paint.variant else None
        return f"url(#{p._pattern(paint, scale, night, variant)})"

    runs = []                      # (stroke, x, letters) for each run of letters one paint covers
    for ch, gx in placed:
        stroke = stroke_of(ch, gx)
        if runs and runs[-1][0] == stroke:
            runs[-1][2].append((ch, gx))
        else:
            runs.append((stroke, gx, [(ch, gx)]))
    keys = []
    for stroke, rx, letters in runs:
        uses = [(_rows_glyph(p, ch), (gx - rx) // scale) for ch, gx in letters]
        keys.append((_together(p, ("run", tuple(uses), scale), uses, scale), rx))
    if len(keys) == 1:
        line = keys[0][0]
    else:
        uses = [(p.syms[key], rx - x) for key, rx in keys]
        line = _together(p, ("line", tuple(uses)), uses)
    off = max(1, scale // 2)
    if shadow:
        p.use(line, x + off, y + off, L, stroke=shadow)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        p.use(line, x + dx, y + dy, L, stroke=edge)
    if glow:
        col, alphas = glow
        n = len(alphas)
        G = p.layer("glow", z=p.Z["haze"])          # over the haze, as `Pix.text` lays a glow
        for ring, a in enumerate(alphas):
            k = n - ring
            if p.lite and 2 * k <= scale:
                # On a drawing made lighter, a ring no wider than half the gap between two letters, so meeting no
                # other, is the line's own level strokes k pixels wider each way, set three times k pixels apart
                # and laid at once at its strength: the same ring with no letter's own, its light rounded once.
                p.shapes[G].append(f'<g stroke="{col}" stroke-width="{num(1 + 2 * k / scale)}" opacity="{num(a)}">'
                                   + "".join(f'<use href="#{p.syms[line]}" x="{x + dx}" y="{y}"/>'
                                             for dx in (-k, 0, k)) + "</g>")
                continue
            uses = [(_glow_glyph(p, ch, scale, k), (gx - x) // scale) for ch, gx in placed]
            p.use(_together(p, ("glows", tuple(uses), scale), uses, scale), x, y, G, stroke=f"{col}:{a:g}")
    for (key, rx), (stroke, _, _) in zip(keys, runs):
        p.use(key, rx, y, L, stroke=stroke)
    top = p.layer(L + "~", p.meta[L][2] if L in p.meta else None, z=(p.meta[L][0] if L in p.meta else 0) + 0.3)
    if bevel and scale >= 3:
        light, dark = bevel
        cells = Pix._cells(x, y, s, "57", scale, 1)[0]
        for (gx, gy) in cells:
            if (gx, gy + 1) not in cells:
                p.px(gx, gy, dark, top)
            elif (gx - 1, gy) not in cells:
                p.px(gx, gy, light, top)
    rows = max(len(glyphs[ch][1]) for ch, _ in placed) if placed else 0
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    return w


GLINT_STEPS = 4         # the steps a title's glint passes along its line in
GLINT_PASS = 0.12       # the share of the hand's glint period the glint takes to pass, the rest a pause


def title_glints(p: Pix, x, y, s, scale, night: bool):
    """Where a title catches the light: by day a white glint on the crown of every third letter's first
    stroke, by night a white-hot speck in the core of every other letter. In a moving file the glint passes
    along the line from its first letter to its last once every period of the hand's glint, in GLINT_STEPS steps,
    each lighting the catch-lights of its stretch of the line; the still file keeps them all lit."""
    glyphs, _, space = FONTS["57"]
    cx, lights = x, []
    for i, ch in enumerate(fold(s, "57")):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        width, rows = glyphs[ch]
        if night and i % 2 == 0 and rows[3]:
            gx = cx + min(rows[3]) * scale + scale // 2
            gy = y + 3 * scale + scale // 2
            lights.append([(gx, gy, FLAME[6])] + ([(gx + 1, gy, FLAME[5])] if scale >= 3 else []))
        elif not night and i % 3 == 1 and rows[0]:
            gx = cx + min(rows[0]) * scale
            lights.append([(gx, y, C["white"])] + ([(gx + 1, y, STEEL[6]), (gx, y + 1, STEEL[6])] if scale >= 3
                                                      else []))
        cx += (width + 1) * scale
    for k, light in enumerate(lights):
        step = k * GLINT_STEPS // max(1, len(lights))
        t0 = round(GLINT_PASS * step / GLINT_STEPS, 3)
        L = p.seq(f"tg{step}", t0, round(t0 + GLINT_PASS * 2 / GLINT_STEPS, 3), MEDIEVAL.glint, keep=True, z=0.3)
        for gx, gy, c in light:
            p.px(gx, gy, c, L)


# --------------------------------------------------------------------------- embers and heat
# Each depth's share of the embers, the seconds they take to rise through the window, and its depth among the
# layers: a slow ambient sweep by the hand, the near embers a little quicker than the far.
RISE = (("far", 0.55, 36.0, -10), ("near", 0.45, 24.0, 20))
STEP = '<animateTransform attributeName="transform" type="translate" values="{}" dur="{}s" ' \
       'repeatCount="indefinite" calcMode="discrete"/>'


def _rise(period: int, dur: str) -> list:
    """How the embers' field steps up through `period` rows, two at a time, once every `dur` seconds: the
    (values, seconds) of each animation of its nested groups, innermost first. Where the steps split into a run
    of fine steps repeated along a run of coarse ones, the two nest, which reads the same and costs less."""
    n = len(range(0, period, 2))
    best = [(";".join(f"0 -{i}" for i in range(0, period, 2)), dur)]
    cost = len(best[0][0])
    for a in range(3, n // 3 + 1):
        if n % a:
            continue
        b = n // a
        fine = ";".join(f"0 -{2 * i}" if i else "0 0" for i in range(a))
        coarse = ";".join(f"0 -{2 * a * j}" if j else "0 0" for j in range(b))
        each = f"{float(dur) / b:.6f}".rstrip("0").rstrip(".")
        if len(fine) + len(coarse) + len(STEP) + len(each) + 7 < cost:
            best, cost = [(fine, each), (coarse, dur)], len(fine) + len(coarse) + len(STEP) + len(each) + 7
    return best


def embers(p: Pix, x0, y0, x1, y1, n, seed=11, name="em", avoid=()):
    """Embers rising from the forge across a clipped window, at two depths: small dull ones behind the
    drawing and fewer, brighter, quicker ones in front, all on the hand's flame. Each depth is drawn once and shown
    again a window lower, and the pair steps up two pixels at a time, so the rise loops without a seam, slowly, in
    the seconds RISE gives; each ember flickers on one of the engine's three flicker phases as it goes, and the
    field sways a pixel either way. The still file keeps the far embers where they lie, those clear of the boxes in
    `avoid`, and leaves the near ones out, so none sits on a letter."""
    period = y1 - y0
    rnd = random.Random(seed)
    values, times, beat, gap = BLINKS["flicker"]
    for depth, share, seconds, z in RISE:
        groups = [Pix(p.w, p.h) for _ in range(3)]
        for i in range(round(n * share)):
            q = groups[i % 3]
            x, y = rnd.randrange(x0 + 2, x1 - 2), rnd.randrange(y0, y1)
            if depth == "far":
                q.px(x, y, rnd.choice((FIRE[2], FIRE[3], FIRE[3])))
            elif rnd.random() < 0.3:
                q.px(x, y, FIRE[5])
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q.px(x + dx, y + dy, FIRE[3] + ":0.6")
            else:
                q.px(x, y, rnd.choice((FIRE[3], FIRE[4], FIRE[4])))
        cid, gid = f"{name}{depth}c", f"{name}{depth}g"
        clip = f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{period}"/></clipPath>'
        field = "".join(f'<g>{_markup(q)}<animate attributeName="opacity" values="{values}" keyTimes="{times}" '
                        f'dur="{beat:g}s" begin="{num(k * gap)}s" repeatCount="indefinite" calcMode="discrete"/></g>'
                        for k, q in enumerate(groups))
        rising = f'<g id="{gid}">{field}</g><use href="#{gid}" y="{period}"/>'
        for values_, dur in _rise(period, f"{seconds:g}"):
            rising = f"<g>{rising}{STEP.format(values_, dur)}</g>"
        sway = "0 0;1 0;1 0;0 0;-1 0;-1 0"
        moving = f'{clip}<g clip-path="url(#{cid})"><g>{rising}{STEP.format(sway, "4.7")}</g></g>'
        still = ""
        if depth == "far":
            still = f'{clip}<g clip-path="url(#{cid})">{"".join(_markup(q, avoid) for q in groups)}</g>'
        p.raw(z, moving, still)


def _markup(q: Pix, avoid=()) -> str:
    """A scratch drawing's pixels as paths, its see-through ones over its solid ones, leaving out any in a box
    in `avoid`."""
    def clear(xy):
        return not any(a <= xy[0] < c and b <= xy[1] < d for a, b, c, d in avoid)
    return "".join(q._paths({xy: c for xy, c in q.layers.get(name, {}).items() if clear(xy)})
                   for name in ("base", "base+"))


def pool(p: Pix, cx, cy, rx, ry, col, alphas, **kw):
    """A pool of light, as `Pix.halo` lays one: rings of it, stronger toward the middle. A drawing made lighter
    leaves its faint outermost ring out and keeps the rest where they lie."""
    if p.lite and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, **kw)


def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a hot thing at (cx, cy): once everything is drawn, `heat` lays its light on whatever stands
    within `r` of it, flickering with the fire. `own` are its own pixels, which take none."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def heat(p: Pix, night: bool):
    """The finishing pass: each hot thing's light on the drawn things near it (the anvil, the smith, the
    hearth's stones, the floor), strongest nearest the heat. The plate and the words take none. A drawing made
    lighter keeps the stronger light near the heat and leaves out the faint ring of it beyond."""
    base = p.layers["base"]
    studs = getattr(p, "studs", set())
    alphas = (0.1, 0.24)
    n = len(alphas)
    reach = 0.5 if p.lite else 1
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if ((x, y) not in base and (x, y) not in studs) or (x, y) in own:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.2) / r
                if d < reach:
                    p.apx(x, y, X["heat"], alphas[min(n - 1, int((1 - d) * n))], L)


def floor_glow(p: Pix, cx, y, rx, ry, night, L="pool"):
    """Firelight pooled on the floor under a hot thing by night: a soft halo along the rule."""
    if night:
        pool(p, cx, y, rx, ry, EMBER[5], (0.06, 0.12, 0.2), L=L)


# --------------------------------------------------------------------------- lines
def _line(cells: dict, x0, y0, x1, y1, tone):
    """A one-pixel line from (x0, y0) to (x1, y1), each step touching the last."""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        cells[(x0, y0)] = tone
        if (x0, y0) == (x1, y1):
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _outline(p: Pix, cells, tone, L="base", skip=()):
    """A one-pixel line round a set of pixels, where nothing of the sprite's own lies."""
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and q not in skip:
                p.px(q[0], q[1], tone, L)


# --------------------------------------------------------------------------- the hearth
def masonry(p: Pix, x, y, w, h, night: bool, seed=1, L="base", uid="mas"):
    """A wall of hearth stone: courses three rows tall of stones six wide, each course half a stone over from
    the last, mortar between them and every stone's top edge catching the light, as one pattern tile the wall
    is filled with, and a few stones a tone darker laid over it (none on a drawing made lighter)."""
    k = -1 if night else 0
    face, lit, mortar, dark = STONE[3 + k], STONE[4 + k], STONE[0 if night else 1], STONE[2 + k]
    key = ("masonry", night, x, y)
    if key not in p.syms:
        rows: dict = {lit: {}, face: {}, mortar: {}}
        for j in range(6):
            off = 3 * ((j // 3) % 2)
            for i in range(12):
                if j % 3 == 2 or (i + off) % 6 == 5:
                    rows[mortar].setdefault(j, []).append(i)
                else:
                    rows[lit if j % 3 == 0 else face].setdefault(j, []).append(i)
        body = "".join(f'<path stroke="{t}" d="{Pix._d(r)}"/>' for t, r in rows.items() if r)
        p.defs.append(f'<pattern id="{uid}" width="12" height="6" patternUnits="userSpaceOnUse" '
                      f'patternTransform="translate({x} {y})">{body}</pattern>')
        p.syms[key] = uid
    p.shapes[p.layer(L)].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid})"/>')
    rnd = random.Random(seed)
    for j in range(0, 0 if p.lite else h, 3):
        off = 3 * ((j // 3) % 2)
        for i in range(-off, w, 6):
            if rnd.random() < 0.28:
                for yy in range(y + j, min(y + j + 2, y + h)):
                    for xx in range(max(x, x + i), min(x + i + 5, x + w)):
                        p.px(xx, yy, dark, L)


def coals(p: Pix, x0, x1, y, night: bool, phase=0, L="base"):
    """The bed of coals on the hearth, three rows deep from row `y` up, on the hand's flame: dull red by day, and
    by night lit from within, the hottest at the heart, flickering on the engine's flicker."""
    Lf = p.flicker(phase) if night else L
    for i, yy in enumerate((y, y - 1, y - 2)):
        for xx in range(x0 + i, x1 - i):
            u = abs((xx + 0.5 - (x0 + x1) / 2) / ((x1 - x0) / 2))
            if night:
                tone = FIRE[4] if u < 0.3 and i < 2 else FIRE[3] if u < 0.7 else FIRE[2]
                if i == 2 and u < 0.4:
                    tone = FIRE[5]
            else:
                tone = FIRE[2] if u < 0.35 and i == 1 else FIRE[1] if u < 0.75 else FIRE[0]
            p.px(xx, yy, tone, Lf if (night and i == 2) else L)


# The forge's fire in its two frames, top row first, twelve wide: low while the bellows are open, and high, roaring
# up the hearth's mouth, while they are squeezed. o y Y W its heat from the deep orange at its edges to the white of
# its heart.
FIRE_LOW = [
    ".....o......",
    "....oyo..o..",
    "...oyYyooy..",
    "..oyYWYyy...",
    "..yYWWWYyo..",
    ".oyYWWWWYyo.",
    "oyYYWWWWYYyo",
]
FIRE_HIGH = [
    "......o.....",
    ".....oy.....",
    ".....yyo..o.",
    "....oyYo.oy.",
    "...oyYYyoyy.",
    "...yYWYYyyo.",
    "..oyYWWYYyo.",
    "..yYWWWWYy..",
    ".oyYWWWWYyo.",
    ".yYWWWWWWYy.",
    "oyYYWWWWYYyo",
]
# The heart both frames share, as (column, rows up from the base): it burns on, flickering on the engine's flicker
# over a tone a step cooler, while the tongues over it leap with the bellows.
HEART = tuple((i, j) for j, row in enumerate(reversed(FIRE_LOW)) for i, ch in enumerate(row)
              if ch == "W" and FIRE_HIGH[len(FIRE_HIGH) - 1 - j][i] == "W")


def flames(p: Pix, cx, base, night: bool, motion: bool, w: int = 12, phase: int = 0):
    """The forge's fire over its coals, on the hand's flame, its foot on row `base` about column cx, in two frames
    on the bellows' breath: low while they are open, and high, white at the heart and roaring up the hearth's mouth,
    when they are squeezed; duller by day, when no glow goes with it. The heart both frames share flickers on the
    engine's flicker over a tone a step cooler. The still file keeps the fire low, its heart lit."""
    if night:
        pal = {"o": FIRE[3], "y": FIRE[4], "Y": FIRE[5], "W": FIRE[6]}
    else:
        pal = {"o": FIRE[1], "y": FIRE[2], "Y": FIRE[3], "W": FIRE[4]}
    x0 = cx - w // 2
    heart = {(x0 + i, base - j) for i, j in HEART}
    if not motion:
        for j, row in enumerate(reversed(FIRE_LOW)):
            for i, ch in enumerate(row):
                if ch != ".":
                    p.px(x0 + i, base - j, pal[ch])
        return
    for (x, y) in heart:
        p.px(x, y, pal["Y"])
        p.px(x, y, pal["W"], p.flicker(phase))
    for name, (t0, t1), art in (("fire0", (0.0, 0.55), FIRE_LOW), ("fire1", (0.55, 1.0), FIRE_HIGH)):
        L = p.seq(name, t0, t1, BREATH, keep=name == "fire0", z=1)
        for j, row in enumerate(reversed(art)):
            for i, ch in enumerate(row):
                if ch != "." and (x0 + i, base - j) not in heart:
                    p.px(x0 + i, base - j, pal[ch], L)


def smoke(p: Pix, x, top, night: bool, motion: bool, phase=0):
    """Smoke from the chimney: a few see-through wisps that climb and drift to the right in three frames, the
    first kept by the still file."""
    frames = [[(0, -1), (1, -2), (1, -3), (2, -4)], [(1, -1), (1, -2), (2, -3), (3, -4), (3, -5)],
              [(0, -1), (2, -2), (2, -3), (3, -4), (4, -6), (5, -7)]]
    for f, pts in enumerate(frames):
        L = p.seq(f"sm{phase}{f}", round(f / 3, 3), round((f + 1) / 3, 3), 5.1, keep=f == 0, z=-9) if motion else None
        if L is None and f:
            break
        L = L or "haze"
        for i, (dx, dy) in enumerate(pts):
            p.apx(x + dx, top + dy, X["smoke"], 0.4 if i < 3 else 0.28, L)
            p.apx(x + dx + 1, top + dy, X["smoke"], 0.2, L)


def horseshoe(p: Pix, x, y, night: bool, L="base"):
    """A horseshoe hung on a nail, five by five, its heels down."""
    art = [".###.", "#...#", "#...#", "#...#", "#...#"]
    tone = IRON[4] if night else STEEL[3]
    p.sprite(x, y, art, {"#": tone}, 1, L)
    p.px(x + 1, y, IRON[5] if night else STEEL[5], L)
    p.px(x, y + 1, IRON[5] if night else STEEL[5], L)
    p.px(x + 2, y - 1, IRON[5] if night else STEEL[4], L)


def tongs(p: Pix, x, base, h, night: bool, L="base"):
    """A pair of tongs leaning against something, their jaws up: two arms crossed at the rivet."""
    tone, lit = (IRON[4], IRON[5]) if night else (STEEL[3], STEEL[5])
    top = base - h
    for j in range(h):
        yy = top + j
        if j < 3:
            p.px(x, yy, tone, L)
            p.px(x + 2, yy, tone, L)
        elif j == 3:
            p.hline(x, x + 3, yy, tone, L)
        elif j < h - 1:
            p.px(x + (1 if j % 2 else 0), yy, tone, L)
            p.px(x + 2 if j % 2 else x + 1, yy, lit if j % 3 == 0 else tone, L)
        else:
            p.px(x, yy, tone, L)
            p.px(x + 2, yy, tone, L)
    p.px(x + 1, top + 3, BRASS[4], L)


def hearth(p: Pix, x, base, night: bool, motion: bool, top: int = 14, w: int = 34, phase: int = 0,
           chimney: bool = True, L="base", strong: bool = False) -> dict:
    """The forge: a hearth of stone `w` wide and twenty-six rows tall with its mouth arched in the middle, coals
    burning in it, an iron plate over it and a riveted iron hood narrowing into a chimney that climbs to row
    `top` behind whatever hangs across the sheet. Tongs lean by the mouth and a horseshoe hangs on the stones.
    The fire burns by day and by night; by night it also flickers and lights the stones, the floor and whatever
    stands near. Returns where its mouth is."""
    k = -1 if night else 0
    body_top = base - 26
    masonry(p, x, body_top, w, 26, night, seed=x + base, L=L)
    # the mouth: an arch cut into the stones, black inside, its voussoirs lit along their lower edge
    mx0, mx1 = x + w // 2 - 7, x + w // 2 + 7
    for yy in range(base - 16, base - 1):
        cut = 2 if yy == base - 16 else 1 if yy == base - 15 else 0
        for xx in range(mx0 + cut, mx1 - cut):
            p.px(xx, yy, COAL[0], L)
    for xx in range(mx0 - 1, mx1 + 1):
        p.px(xx, base - 17, STONE[3 if night else 6], L)
        p.px(xx, base - 18, STONE[2 if night else 5], L)
    for (xx, yy) in ((mx0 - 1, base - 16), (mx1, base - 16), (mx0, base - 16), (mx1 - 1, base - 16),
                     (mx0 - 1, base - 15), (mx1, base - 15)):
        p.px(xx, yy, STONE[2 if night else 5], L)
    coals(p, mx0 + 1, mx1 - 1, base - 2, night, phase, L)
    flames(p, (mx0 + mx1) // 2, base - 4, night, motion, phase=phase)
    # the iron plate over the hearth, three rows, and the riveted hood above it
    for xx in range(x - 1, x + w + 1):
        p.px(xx, body_top - 1, IRON[1 if night else 2], L)
        p.px(xx, body_top - 2, IRON[4 + k], L)
        p.px(xx, body_top - 3, IRON[5 + k] if xx < x + 6 else IRON[4 + k], L)
    hood_rows = ((x + 1, x + w - 1), (x + 2, x + w - 2), (x + 4, x + w - 4), (x + 6, x + w - 6), (x + 8, x + w - 8),
                 (x + w // 2 - 7, x + w // 2 + 7), (x + w // 2 - 6, x + w // 2 + 6))
    for j, (a, b) in enumerate(hood_rows):
        yy = body_top - 4 - j
        for xx in range(a, b):
            tone = IRON[5 + k] if xx == a else IRON[1 + k] if xx == b - 1 else IRON[3 + k]
            if j == 1 and xx not in (a, b - 1):
                tone = IRON[2 + k]
            p.px(xx, yy, tone, L)
    band_y = body_top - 5
    for rx in range(x + 5, x + w - 6, 7):
        rivet(p, rx, band_y - 1, L, night)
    hood_top = body_top - 4 - len(hood_rows)
    if chimney:
        cx0, cx1 = x + w // 2 - 5, x + w // 2 + 5
        h = hood_top + 1 - top
        far = p.layer("far")
        for (bx, bw, tone) in ((cx0, 1, IRON[5 + k]), (cx0 + 1, 8, IRON[3 + k]), (cx1 - 1, 1, IRON[1 + k])):
            p.shapes[far].append(f'<rect x="{bx}" y="{top}" width="{bw}" height="{h}" fill="{tone}"/>')
        for yy in range(top + 4, hood_top, 9):
            p.hline(cx0 + 1, cx1 - 1, yy, IRON[2 + k], "far")
            rivet(p, cx0 + 1, yy - 1, "far", night)
            rivet(p, cx1 - 3, yy - 1, "far", night)
        p.hline(cx0 - 1, cx1 + 1, top, IRON[5 + k], "far")
        p.hline(cx0 - 1, cx1 + 1, top + 1, IRON[4 + k], "far")
        smoke(p, (cx0 + cx1) // 2, top - 1, night, motion, phase)
    if w >= 32:
        horseshoe(p, x + w - 8, base - 14, night, L)
    tongs(p, x + 4, base, 15, night, L)
    if night:
        mouth = (mx0 + mx1) / 2, base - 7
        own = {(xx, yy) for xx in range(mx0, mx1) for yy in range(base - 16, base)}
        if strong:          # a sheet with no motion to carry the fire gets a brighter pool of its light
            pool(p, mouth[0], base - 6, 24, 17, EMBER[5], (0.09, 0.18, 0.3), L=p.flicker(phase, back=True))
            floor_glow(p, mouth[0], base - 0.5, 30, 3.5, night)
        else:
            pool(p, mouth[0], base - 6, 20, 15, EMBER[5], (0.06, 0.12, 0.2), L=p.flicker(phase, back=True))
            floor_glow(p, mouth[0], base - 0.5, 26, 3, night)
        lamp(p, mouth[0], mouth[1], 24, phase, own)
    return dict(mouth=(mx0, mx1), body_top=body_top, hood_top=hood_top)


def bellows(p: Pix, x, y, night: bool, motion: bool, flip: bool = False, L="base"):
    """A bellows on an iron stand breathing into the hearth's side, its nozzle at the left (or at the right,
    `flip`), top-left at (x, y), twenty-four wide and twelve deep: an oak board hinged at the nozzle over the
    pleated leather, a board beneath, and a handle bar at the wide end. It opens and squeezes in two frames
    on the breath's loop; the still file keeps it open."""
    k = -1 if night else 0
    pal = {"O": OAK[6 + k], "o": OAK[5 + k], "d": OAK[3 + k], "L": LEATHER[3 + k], "l": LEATHER[1 + k],
           "n": IRON[3 + k], "b": BRASS[4 + k], "h": OAK[4 + k], "s": IRON[3 + k], "S": IRON[1 + k]}
    stand = ["....oooooooooooooooooooo", "....dddddddddddddddddddd", "......sS............sS..",
             "......sS............sS..", "......sS............sS.."]
    open_ = ["..................OOOOOh", "..............OOOOOLLLLh", "..........OOOOOLLlLLLlLh",
             "......OOOOOLLlLLLLLlLLLh", "..OOOOOLLlLLLLlLLLLlLLLh", "bnnnLLlLLLLLlLLLLlLLLLLh",
             "bnnnLlLLLLlLLLLlLLLLlLLh"]
    shut = ["........................", "........................", "........................",
            "........................", "...OOOOOOOOOOOOOOOOOOOOh", "bnnnLLlLLlLLlLLlLLlLLlLh",
            "bnnnLlLLlLLlLLlLLlLLlLLh"]
    p.sprite(x, y + 7, stand, pal, 1, L, flip=flip)
    Lo = p.seq("bel0", 0.0, 0.55, BREATH, keep=True, z=1) if motion else L
    Ls = p.seq("bel1", 0.55, 1.0, BREATH, z=1) if motion else None
    for Lx, art in ((Lo, open_), (Ls, shut)):
        if Lx is None:
            continue
        p.sprite(x, y, art, pal, 1, Lx, flip=flip)


def tools(p: Pix, x, y, night: bool, L="base"):
    """Tools on the wall, from an oak rail at row `y` with two pegs: a pair of tongs hung by their jaws and a
    hammer hung by its head, its haft hanging down."""
    k = -1 if night else 0
    for xx in range(x, x + 18):
        p.px(xx, y, OAK[5 + k], L)
        p.px(xx, y + 1, OAK[2 + k], L)
    for px_ in (x + 4, x + 12):
        p.px(px_, y + 2, OAK[3 + k], L)
    tongs(p, x + 3, y + 18, 15, night, L)
    hammer_head(p, x + 9, y + 3, night, L)
    for j in range(7, 17):
        p.px(x + 12, y + j, OAK[4 + k] if j % 3 else OAK[2 + k], L)


# --------------------------------------------------------------------------- the anvil, the blade, the smith
# The anvil's profile, horn to the left: each row's first and last column, the face on row 0; the big one for
# a wide header's scene, the small one for a phone's and the sheets' ornaments.
ANVIL_BIG = ((5, 28), (2, 29), (0, 29), (2, 28), (5, 26), (9, 24), (11, 23), (11, 23), (9, 25))
ANVIL_SMALL = ((4, 22), (2, 23), (0, 23), (2, 21), (6, 19), (8, 18), (8, 18), (6, 20))


def anvil(p: Pix, x, base, night: bool, L="base", small: bool = False) -> dict:
    """A London anvil on an oak stump, its horn to the left and its feet on row `base`: the face lit from
    above with a bright edge along its left, the body shaded as a column lit from the left and dark at the
    heel, the horn's underside in shade, a dark line round it all. The stump is bound with an iron hoop.
    Returns the face's row and span."""
    k = -2 if night else 0
    S = STEEL
    rows = ANVIL_SMALL if small else ANVIL_BIG
    horn = 6 if small else 9
    stump_h = 3 if small else 4
    face = base - stump_h - len(rows)
    cells = {}
    for j, (a, b) in enumerate(rows):
        for i in range(a, b + 1):
            t = (i - a) / max(1, b - a)
            if j == 0:
                v = 6 if t < 0.3 else 5
            elif j == 1:
                v = 5 if t < 0.8 else 3
            elif j <= 4 and i < horn:
                v = 2 if j >= 3 else 3                   # the horn's underside, turning from the light
            else:
                v = 4 if t < 0.25 else 3 if t < 0.8 else 2
            if i == b and j > 0:
                v = 2
            cells[(x + i, face + j)] = S[max(0, min(6, v + k))]
    for q, c in cells.items():
        p.px(q[0], q[1], c, L)
    _outline(p, cells, IRON[0], L)
    # the stump, and its hoop
    sx0, sx1 = (x + 6, x + 20) if small else (x + 9, x + 25)
    cylinder(p, [(yy, sx0, sx1) for yy in range(base - stump_h, base)], OAK, L, lo=1 if night else 2,
             hi=3 if night else 5)
    for xx in range(sx0, sx1 + 1):
        u = (xx - sx0) / (sx1 - sx0)
        p.px(xx, base - stump_h, (S[4 + k] if u < 0.35 else S[3 + k] if u < 0.8 else S[1 + k]) if u else S[5 + k], L)
    for yy in range(base - stump_h + 1, base):
        if (yy + x) % 2:
            p.px(sx0 + 3 + (yy % 3), yy, OAK[1], L)
    return dict(face=face, span=(x + rows[0][0], x + rows[0][1]), cells=cells)


def blade(p: Pix, x, y, night: bool, length: int = 15, phase: int = 1, L="base", strong: bool = False):
    """A sword blade lying on the anvil's face, its tang at the right and its point at (x, y) over the horn,
    two pixels deep, its heat on the hand's flame, the colours of the fire it came from. By day it is red from the
    point to where the hammer lands and steel toward the tang, with no glow; by night it is fresh from the fire,
    white where the hammer lands, orange and red toward the point, dark at the tang, and it lights what is near."""
    cells = set()
    for i in range(length):
        for j in (0, 1):
            if i == 0 and j == 1:
                continue
            cells.add((x + i, y + j))
            u = i / length
            if i >= length - 2:
                tone = FIRE[1] if night else IRON[3]                     # the tang, held in the tongs
            elif night:
                tone = (FIRE[2] if u < 0.12 else FIRE[3] if u < 0.3 else FIRE[4] if u < 0.5
                        else FIRE[5] if u < 0.62 else FIRE[6] if u < 0.85 else FIRE[4])
                if j == 1 and tone in (FIRE[6], FIRE[5]):
                    tone = FIRE[5] if tone is FIRE[6] else FIRE[4]
            else:
                tone = (FIRE[3] if u < 0.2 else FIRE[2] if u < 0.5 else FIRE[1] if u < 0.62
                        else STEEL[6] if j == 0 else STEEL[4])
                if j == 1 and tone in (FIRE[3], FIRE[2]):
                    tone = FIRE[1]
            p.px(x + i, y + j, tone, L)
    if night:
        hot = x + length * 0.72
        if strong:          # its light on a sheet with no motion
            pool(p, hot, y + 1, 14, 7, EMBER[5], (0.1, 0.2, 0.32), L=p.flicker(phase, back=True))
            lamp(p, hot, y + 1, 16, phase, cells)
        else:
            pool(p, hot, y + 1, 12, 6, EMBER[5], (0.08, 0.16, 0.26), L=p.flicker(phase, back=True))
            lamp(p, hot, y + 1, 14, phase, cells)
    return cells


# The smith, twenty-eight rows tall by the hand's canon, his head a fifth of it, facing left: his hair and a red
# headband, his eye a single dark unit, his beard, a tunic, the leather apron with its straps and belt, his legs and
# boots. h the hair, R the headband, s the skin, e the eye, b the beard, T t the tunic lit and in shade, k a strap, A a
# the apron, L the belt, P p the legs, B the boots.
SMITH = [
    "....hhhhh.....",
    "...hhhhhhh....",
    "..RRRRRRRhh...",
    "..sesssshhh...",
    ".sssssssshh...",
    "..sbbbbsshh...",
    "..bbbbbbbh....",
    "...bbbbbb.....",
    ".TTTTbbTTTTt..",
    "TTTkAAAAAkTTt.",
    "TTTAAAAAAATTt.",
    "TTTAAAAAAATTt.",
    "ssTAAAAAAATTt.",
    ".TTAAAAAAATt..",
    ".LLLLLLLLLLL..",
    ".AAAAAAAAAAa..",
    ".AAAAAAAAAAa..",
    ".aAAAAAAAAAa..",
    ".aAAAAAAAAAa..",
    ".aaaaaaaaaaa..",
    ".PPPP..PPPP...",
    ".PPPp..PPPp...",
    ".PPPp..PPPp...",
    ".PPPp..PPPp...",
    ".PPPp..PPPp...",
    "BBBBB..BBBBB..",
    "BBBBB..BBBBB..",
    "BBBBBB.BBBBBB.",
]
# The near arm and the hammer in each frame of the swing, relative to the smith's top-left: the arm's pixels
# from the shoulder, the fist, the hammer's haft from the fist to its head, whose six by four cells are placed
# at `head`.
SWING_FRAMES = {
    "up": dict(arm=[(10, 8), (11, 7), (11, 6), (12, 5), (12, 4)], fist=(12, 2), haft=[(13, 1), (14, 0), (15, -1)],
               head=(15, -5)),
    "mid": dict(arm=[(9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8)], fist=(2, 7),
                haft=[(1, 6), (0, 5), (-1, 4), (-2, 3)], head=(-8, 1)),
    "down": dict(arm=[(9, 9), (8, 10), (7, 10), (6, 11), (5, 11), (4, 12), (3, 12)], fist=(1, 12),
                 haft=[(0, 12), (-1, 12), (-2, 12), (-3, 12)], head=(-9, 9)),
}
# When each frame shows on the swing's loop: mid-swing (which the still file keeps), the strike, then the long
# hold with the hammer raised behind him, from which it comes forward again; the sparks' three frames and the flash
# of the strike follow the blow.
SWING_TIMES = {"mid": (0.0, 0.1), "down": (0.1, 0.3), "up": (0.3, 1.0)}
SPARK_TIMES = ((0.1, 0.16), (0.16, 0.24), (0.24, 0.34))
FLASH = (0.1, 0.19)


def hammer_head(p: Pix, x, y, night: bool, L="base"):
    """A hammer's head, six by four, lit on its upper left face, drawn once a file and placed where it is."""
    k = -2 if night else 0
    art = ["LFFFFd", "FSSSSd", "FSSSdd", "dddddd"]
    pal = {"L": STEEL[6 + k], "F": STEEL[5 + k], "S": STEEL[3 + k], "d": STEEL[1 + k]}
    p.sprite(x, y, art, pal, 1, L, reuse=True)


def smith(p: Pix, x, base, night: bool, motion: bool, L="base") -> dict:
    """The smith at his anvil, facing left, twenty-eight rows tall with his boots on row `base`, by the hand's
    canon: bare arms and face on the hand's skin, a leather apron over his tunic, a belt with a brass buckle, a
    beard, a headband. His near arm swings the hammer in three frames on the swing's loop: mid-swing (which the still
    file keeps), down on the blade, and raised behind him. By night he is a dark shape against the glow, his skin in
    shadow, lit along his front by the hot iron. Returns where the hammer strikes."""
    top = base - len(SMITH)
    if night:
        pal = {"h": COAL[2], "s": SKIN[1], "e": COAL[0], "R": EMBER[3], "b": COAL[2], "T": COAL[3], "t": COAL[2],
               "k": COAL[2], "A": COAL[3], "a": COAL[2], "L": COAL[1], "P": COAL[2], "p": COAL[1], "B": COAL[1]}
    else:
        pal = {"h": COAL[3], "s": SKIN[3], "e": COAL[0], "R": EMBER[4], "b": COAL[4], "T": IRON[4], "t": IRON[3],
               "k": LEATHER[2], "A": LEATHER[4], "a": LEATHER[3], "L": LEATHER[1], "P": COAL[4], "p": COAL[3],
               "B": LEATHER[1]}
    body = {(x + i, top + j): pal[ch] for j, row in enumerate(SMITH) for i, ch in enumerate(row) if ch != "."}
    for q, c in body.items():
        p.px(q[0], q[1], c, L)
    p.px(x + 2, top + 2, EMBER[4] if night else EMBER[5], L)       # the headband's knot catches the light
    p.px(x + 5, top + 14, BRASS[2] if night else BRASS[4], L)      # the buckle
    p.px(x + 6, top + 14, BRASS[3] if night else BRASS[5], L)
    if night:
        for (qx, qy) in list(body):      # the forge's light along his front and over his shoulders
            skin = body[(qx, qy)] == SKIN[1]
            if (qx - 1, qy) not in body and qy < base - 2:
                p.px(qx, qy, SKIN[3] if skin else EMBER[4] if qy > top + 9 else EMBER[5], L)
            elif (qx, qy - 1) not in body and qy < top + 10:
                p.px(qx, qy, SKIN[2] if skin else EMBER[3], L)
    else:
        shade = {SKIN[3]: SKIN[2], LEATHER[4]: LEATHER[2], IRON[4]: IRON[2]}
        for (qx, qy) in list(body):
            if ((qx + 1, qy) not in body or (qx, qy + 1) not in body) and body[(qx, qy)] in shade:
                p.px(qx, qy, shade[body[(qx, qy)]], L)
    arm = SKIN[1] if night else SKIN[3]
    arm_dark = SKIN[0] if night else SKIN[2]
    haft = OAK[2] if night else OAK[4]
    for name, frame in SWING_FRAMES.items():
        if motion:
            t0, t1 = SWING_TIMES[name]
            Lf = p.seq(f"sw{name}", t0, t1, SWING, keep=name == "mid", z=2)
        elif name != "mid":
            continue
        else:
            Lf = L
        for (i, j) in frame["arm"]:
            p.px(x + i, top + j, arm, Lf)
            p.px(x + i, top + j + 1, arm_dark, Lf)
        fx, fy = frame["fist"]
        p.rect(x + fx, top + fy, 2, 2, arm_dark, Lf)
        p.px(x + fx, top + fy, arm, Lf)
        for (i, j) in frame["haft"]:
            p.px(x + i, top + j, haft, Lf)
        hx, hy = frame["head"]
        hammer_head(p, x + hx, top + hy, night, Lf)
    hx, hy = SWING_FRAMES["down"]["head"]
    return dict(strike=(x + hx + 1, top + hy + 3), top=top)


# Where sparks fly from the strike in three frames, relative to the point struck: the burst, the spread (which
# the still file keeps) and the last of them, falling. W white heat, Y yellow, O orange, o ember, r a dying red.
SPARKS = [
    [(-1, -2, "Y"), (1, -2, "Y"), (-3, -3, "O"), (3, -3, "O"), (0, -4, "W"), (-2, -1, "O"), (2, -1, "O"), (0, -1, "W")],
    [(-4, -5, "Y"), (4, -6, "Y"), (-7, -7, "O"), (6, -8, "O"), (0, -8, "W"), (-2, -6, "Y"), (2, -5, "W"), (-9, -4, "o"),
     (8, -3, "o"), (-5, -9, "o"), (5, -10, "o"), (-11, -6, "o"), (10, -7, "o"), (-1, -3, "O"), (3, -2, "Y")],
    [(-9, -11, "o"), (8, -12, "o"), (-12, -8, "r"), (11, -10, "r"), (-4, -13, "o"), (5, -14, "r"), (-14, -4, "r"),
     (13, -5, "r"), (-7, -2, "r"), (9, -1, "r")],
]
SPARK_PAL = {"W": FIRE[6], "Y": FIRE[5], "O": FIRE[4], "o": FIRE[3], "r": FIRE[2]}     # on the hand's flame


def sparks(p: Pix, sx, sy, night: bool, motion: bool, clear=None, still: int = 1):
    """Sparks off the blade as the hammer lands: a burst, then a spread that the still file keeps, then the
    last of them falling, each frame in its moment of the swing's loop. `clear(x0, y0, x1, y1)` says whether
    a spark may fly where it would; none flies onto a word. By night a flash of light goes with the strike.
    A sheet without motion shows frame `still` alone."""
    for f, (pts, (t0, t1)) in enumerate(zip(SPARKS, SPARK_TIMES)):
        if motion:
            L = p.seq(f"sp{f}", t0, t1, SWING, keep=f == 1, z=3)
        elif f != still:
            continue
        else:
            L = "near"
        for (dx, dy, tone) in pts:
            x, y = sx + dx, sy + dy
            if clear is None or clear(x - 2, y - 2, x + 3, y + 3):
                p.px(x, y, SPARK_PAL[tone], L)
                if tone == "W" and f < 2:
                    p.px(x, y - 1, FIRE[5] + ":0.7", L)
    if night and motion:
        Lf = p.seq("spf", *FLASH, SWING, z=-6)
        pool(p, sx, sy - 2, 14, 9, FIRE[5], (0.1, 0.2), L=Lf)


def anvil_scene(p: Pix, x, base, night: bool, motion: bool, clear=None, strong: bool = False) -> dict:
    """The anvil with the blade on it and the smith beside it, swinging: the anvil's horn at `x`, the smith to
    its right. `strong` gives the blade the brighter light of a sheet with no motion. Returns the span they
    take on the rule."""
    a = anvil(p, x, base, night)
    blade(p, x + 3, a["face"] - 2, night, length=24, strong=strong)
    s = smith(p, x + 30, base, night, motion)
    sparks(p, s["strike"][0], s["strike"][1], night, motion, clear)
    if night:
        floor_glow(p, x + 16, base - 0.5, 26, 3, night)
    return dict(span=(x, x + 46), face=a["face"])


# --------------------------------------------------------------------------- the quench bucket
def bucket(p: Pix, x, base, night: bool, motion: bool, w: int = 12, h: int = 11, L="base"):
    """A quench bucket of oak staves bound with two iron hoops, an iron handle over it, water in it, steam
    rising off the water in three frames (the first kept by the still file) whether the sheet moves or not."""
    k = -1 if night else 0
    top = base - h
    for xx in range(x, x + w):
        u = (xx - x) / (w - 1)
        tone = OAK[5 + k] if u < 0.2 else OAK[4 + k] if u < 0.6 else OAK[3 + k] if u < 0.85 else OAK[2 + k]
        if (xx - x) % 3 == 2:
            tone = OAK[2 + k]
        for yy in range(top, base):
            p.px(xx, yy, tone, L)
    for hy in (top + 2, base - 3):
        for xx in range(x - 1, x + w + 1):
            u = (xx - x + 1) / (w + 1)
            p.px(xx, hy, STEEL[5 + k] if u < 0.3 else STEEL[3 + k] if u < 0.8 else STEEL[1 + k], L)
    for xx in range(x + 1, x + w - 1):
        p.px(xx, top, RAMP["water"][4 + k] if 2 <= xx - x <= 4 else RAMP["water"][3 + k], L)
    p.px(x + 2, top, RAMP["water"][6 + k], L)
    p.px(x, top, OAK[2 + k], L)
    p.px(x + w - 1, top, OAK[1 + k], L)
    handle: dict = {}
    _line(handle, x + 1, top - 1, x + w // 2 - 1, top - 3, IRON[4 + k])
    _line(handle, x + w // 2, top - 3, x + w - 2, top - 1, IRON[3 + k])
    for q, c in handle.items():
        p.px(q[0], q[1], c, L)
    frames = [[(4, -1, 0.4), (5, -2, 0.4), (7, -3, 0.24)], [(3, -1, 0.4), (5, -2, 0.4), (6, -3, 0.24), (8, -5, 0.24)],
              [(5, -1, 0.4), (6, -3, 0.4), (8, -4, 0.24), (9, -6, 0.24), (7, -2, 0.24)]]
    for f, pts in enumerate(frames):
        if motion:
            Ls = p.seq(f"st{f}", round(f / 3, 3), round((f + 1) / 3, 3), 4.3, keep=f == 0, z=4)
        elif f:
            break
        else:
            Ls = "near"
        for (dx, dy, a) in pts:
            p.apx(x + dx, top + dy - 2, X["steam"], a, Ls)
            p.apx(x + dx + 1, top + dy - 2, X["steam"], 0.2, Ls)


# --------------------------------------------------------------------------- shields, swords and axes
def round_shield(p: Pix, cx, cy, r, night: bool, face: str = "steel", L="base"):
    """A round shield seen face on, centred on (cx, cy): a steel rim with rivets round it, a face of
    polished steel or of red or green enamel with a brass cross, and a domed brass boss."""
    k = -1 if night else 0
    F = {"steel": STEEL, "red": EMBER, "green": RAMP["green"]}[face]
    cells = {}
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d > r:
                continue
            lit = (dx * LX + dy * LY) / r
            if d > r - 1.5:
                tone = STEEL[5 + k] if lit > 0.3 else STEEL[3 + k] if lit > -0.3 else STEEL[1 + k]
            elif face != "steel" and (abs(dx) < 1 or abs(dy) < 1):
                tone = BRASS[5 + k] if lit > 0 else BRASS[3 + k]
            else:
                base_t = 4 if face == "steel" else 3
                tone = F[max(1, min(6, base_t + k + (1 if lit > 0.2 else 0)))]
            cells[(x, y)] = tone
    for q, c in cells.items():
        p.px(q[0], q[1], c, L)
    _outline(p, cells, IRON[0], L)
    if r >= 5:
        for a in range(0, 360, 45):
            qx = round(cx + (r - 1.6) * math.cos(math.radians(a)) - 0.5)
            qy = round(cy + (r - 1.6) * math.sin(math.radians(a)) - 0.5)
            p.px(qx, qy, STEEL[6 + k] if a in (180, 225, 270) else STEEL[2 + k], L)
    sphere(p, cx, cy, max(1.6, r * 0.3), BRASS, L, lo=2 if night else 3, outline=False)
    return cells


def sword(p: Pix, x0, y0, x1, y1, night: bool, L="base"):
    """A sword from its pommel at (x0, y0) to its point at (x1, y1): a bright blade with a dark edge on its
    shaded side, a brass crossguard, a leather grip and a brass pommel."""
    k = -1 if night else 0
    cells: dict = {}
    n = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    gx, gy = x0 + ux * 4, y0 + uy * 4
    _line(cells, gx, gy, x1, y1, STEEL[6 + k])
    _line(cells, gx + uy, gy - ux, x1 - ux * 2 + uy, y1 - ux - uy * 2, STEEL[3 + k])
    grip: dict = {}
    _line(grip, x0 + ux, y0 + uy, gx - ux, gy - uy, LEATHER[3 + k])
    guard: dict = {}
    _line(guard, gx - uy * 2.5, gy + ux * 2.5, gx + uy * 2.5, gy - ux * 2.5, BRASS[4 + k])
    for q, c in cells.items():
        p.px(q[0], q[1], c, L)
    _outline(p, cells, IRON[0] if night else IRON[1], L, skip=set(grip) | set(guard))
    for q, c in grip.items():
        p.px(q[0], q[1], c, L)
    for q, c in guard.items():
        p.px(q[0], q[1], c, L)
    p.px(int(x0), int(y0), BRASS[5 + k], L)
    p.px(int(gx + uy * 2.5), int(gy - ux * 2.5), BRASS[5 + k], L)


def axe(p: Pix, x, y, night: bool, L="base"):
    """A bearded axe hung by its head from a peg at (x, y), the haft hanging down to the right of the blade."""
    k = -1 if night else 0
    head = ["..SSS", ".SSSS", "LSSSS", "LSSS.", "LSS..", ".S..."]
    pal = {"S": STEEL[4 + k], "L": STEEL[6 + k]}
    p.sprite(x, y, head, pal, 1, L)
    for j in range(6):
        p.px(x + 4 + (1 if j < 3 else 0), y + 1 + j, STEEL[2 + k] if j < 2 else OAK[4 + k], L)
    for j in range(6, 14):
        p.px(x + 4, y + 1 + j, OAK[4 + k] if j % 4 else OAK[2 + k], L)
    p.px(x + 4, y + 15, LEATHER[2 + k], L)


RACK_SHORT_W = 37      # the columns the rack's short form takes: its beam, the red shield and the axe


def rack(p: Pix, x0, x1, y, night: bool, clear=None, L="base", short: bool = False):
    """The wall behind the smithy: an oak beam from x0 to x1 at row `y`, a round shield of red enamel and one
    of steel hung under it on straps, and a bearded axe; `short`, for a narrow wall, the red shield and the axe
    alone. `clear(x0, y0, x1, y1)` says whether each may hang where it would."""
    k = -1 if night else 0
    for xx in range(x0, x1):
        p.px(xx, y, OAK[5 + k], L)
        p.px(xx, y + 1, OAK[3 + k] if xx % 7 else OAK[2 + k], L)
        p.px(xx, y + 2, OAK[1 + k], L)
    for (cx, face) in ((x0 + 11, "red"),) + (() if short else ((x0 + 33, "steel"),)):
        if clear is None or clear(cx - 11, y, cx + 12, y + 25):
            p.vline(cx, y + 3, y + 6, LEATHER[3 + k], L)
            round_shield(p, cx + 0.5, y + 15.5, 9.5, night, face, L)
    ax = x0 + (25 if short else 46)
    if clear is None or clear(ax - 2, y, ax + 8, y + 22):
        p.px(ax + 2, y + 3, STEEL[3 + k], L)
        axe(p, ax, y + 4, night, L)


def sword_over_shield(p: Pix, cx, cy, night: bool, L="base"):
    """A round shield hung on the wall with a sword laid across it, point up to the right: the strip's badge."""
    round_shield(p, cx + 0.5, cy + 0.5, 9.5, night, "red", L)
    sword(p, cx - 11, cy + 12, cx + 12, cy - 11, night, L)


# The smith's own arms, the device of his touchmark in the round: a hammer raised over an anvil. # is the brass.
DEVICE = [
    "..#####..",
    "..#####..",
    "....#....",
    "....#....",
    ".........",
    "#########",
    "...###...",
    "..#####..",
]


def heater(p: Pix, cx, top, night: bool, w: int = 26, h: int = 32, L="base") -> dict:
    """A heater shield hung on the wall, `w` wide and `h` tall with its top at row `top` about column cx: straight
    down its sides for half its height and curving to its point, a rim of steel round a field of red enamel, and on
    the field the smith's own device in brass at twice its size, the hammer raised over the anvil; the whole a
    little convex, lit from the upper left, its outline the iron's darkest. Returns its cells."""
    k = -1 if night else 0
    cells = set()
    for j in range(h):
        t = j / (h - 1)
        hw = w / 2 if t <= 0.5 else w / 2 * math.sqrt(max(0.0, 1 - ((t - 0.5) / 0.5) ** 1.7))
        for x in range(math.floor(cx - hw + 0.5), math.ceil(cx + hw - 0.5)):
            cells.add((x, top + j))
    for (x, y) in cells:
        nx = (x + 0.5 - cx) / (w / 2)
        ny = (y + 0.5 - top) / h - 0.35
        nz = math.sqrt(max(0.0, 1 - 0.36 * nx * nx - 0.25 * ny * ny))
        lam = max(0.0, 0.6 * nx * LX + 0.5 * ny * LY + nz * LZ)
        rim = any((x + dx, y + dy) not in cells for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
                  if abs(dx) + abs(dy) <= 2)
        if rim:
            tone = STEEL[5 + k] if lam > 0.78 else STEEL[3 + k] if lam > 0.55 else STEEL[1 + k]
        else:
            tone = EMBER[4 + k] if lam > 0.82 else EMBER[3 + k] if lam > 0.58 else EMBER[2 + k]
        p.px(x, y, tone, L)
    s = 2
    gx = cx - len(DEVICE[0]) * s // 2
    gy = top + round(h * 0.2)
    gold = {(gx + i * s + a, gy + j * s + b) for j, row in enumerate(DEVICE) for i, ch in enumerate(row) if ch == "#"
            for a in range(s) for b in range(s)}
    for (x, y) in gold:
        if (x - 1, y) not in gold or (x, y - 1) not in gold:
            tone = BRASS[6 + k]
        elif (x + 1, y) not in gold or (x, y + 1) not in gold:
            tone = BRASS[2 + k]
        else:
            tone = BRASS[4 + k]
        p.px(x, y, tone, L)
        if (x + 1, y + 1) not in gold and (x + 1, y + 1) in cells:
            p.px(x + 1, y + 1, EMBER[1 + k] if k == 0 else EMBER[0], L)
    _outline(p, cells, IRON[0], L)
    return cells


TROPHY_H = 55       # the trophy's height, from its helm's crest to its swords' pommels
TROPHY_TOP = 13     # the highest row its crest hangs from, clear of the mail across the top
TROPHY_X = 384      # its middle on a wide strip, right of the words
PHONE_TROPHY_X = 138   # and on a phone's


def trophy(p: Pix, cx, top, night: bool, L="base") -> tuple:
    """The armoury's trophy hung on the wall, the strip's hero, TROPHY_H rows tall from its crest at row `top`
    about column cx: a heater shield of red enamel bearing the smith's arms, the hammer over the anvil in brass, a
    knight's great helm with its crest set on it, and two swords of polished steel crossed behind, their hilts below
    the shield and their points beside the helm. By night the forge's light, from below, flickers on the wall round
    it. Returns its box (x0, y0, x1, y1)."""
    sword(p, cx - 21, top + TROPHY_H - 1, cx + 19, top + 2, night, L)
    sword(p, cx + 21, top + TROPHY_H - 1, cx - 19, top + 2, night, L)
    heater(p, cx, top + 15, night, h=30, L=L)
    helm(p, cx, top + 10, night, kind=2, L=L, crest=EMBER[4 - (1 if night else 0)])
    if night:
        pool(p, cx - 4, top + TROPHY_H - 6, 26, 22, EMBER[5], (0.04, 0.08, 0.13), L=p.flicker(0, back=True))
    return (cx - 24, top, cx + 24, top + TROPHY_H)


# --------------------------------------------------------------------------- small pieces
# The smith's touchmark, thirteen across: a shield cut into the plate round a hammer raised over an anvil.
# D is the shield's cut, # the hammer's and the anvil's.
MARK = [
    "..DDDDDDDDD..",
    ".D.........D.",
    "D...#####...D",
    "D...#####...D",
    "D.....#.....D",
    "D.....#.....D",
    "D...........D",
    "D.#########.D",
    ".D...###...D.",
    "..D.#####.D..",
    "...D.....D...",
    "....D...D....",
    ".....DDD.....",
]


def stamp_lips(p: Pix, cells, lip, on=None, L="base", diagonal_only: bool = False):
    """The lip of light below and to the right of every pixel in `cells`, where the metal pushed up round a
    cut catches the light from the upper left: drawn only over `on` (a colour, or None for the bare plate)
    and never over the cut itself. `diagonal_only` lips the corner alone, which keeps letters legible."""
    cells = set(cells)
    dirs = ((1, 1),) if diagonal_only else ((1, 1), (1, 0), (0, 1))
    for (qx, qy) in cells:
        for (dx, dy) in dirs:
            q = (qx + dx, qy + dy)
            if q not in cells and p.get(q[0], q[1], L) == on:
                p.px(q[0], q[1], lip, L)


def maker_mark(p: Pix, x, y, night: bool, L="base"):
    """The smith's touchmark struck into the plate, thirteen by thirteen with its lips, top-left at (x, y):
    a shield cut round a hammer raised over an anvil, each cut dark with a lip of light below and to its
    right where the metal was pushed up."""
    cut = IRON[2] if night else IRON[0]      # by night the cut's floor shows a shade lighter than the plate
    lip = STONE[5] if night else C["white"]
    cells = {(x + i, y + j) for j, row in enumerate(MARK) for i, ch in enumerate(row) if ch != "."}
    for (qx, qy) in cells:
        p.px(qx, qy, cut, L)
    stamp_lips(p, cells, lip, None, L)


def buckle(p: Pix, x, y, h, night: bool, L="base"):
    """A brass buckle at the start of a leather strap, four wide and `h` deep, top-left at (x, y): a frame
    lit along its top and left and dark along its foot, the strap's end through it and the tongue across."""
    k = -1 if night else 0
    p.rect(x, y, 4, h, LEATHER[3], L)
    p.hline(x, x + 4, y, BRASS[5 + k], L)
    p.vline(x, y, y + h, BRASS[5 + k], L)
    p.hline(x + 1, x + 4, y + h - 1, BRASS[2 + k], L)
    p.vline(x + 3, y + 1, y + h - 1, BRASS[3 + k], L)
    p.px(x + 1, y + h // 2, BRASS[4 + k], L)
    p.px(x + 2, y + h // 2, BRASS[4 + k], L)


def dome(p: Pix, x, y, night: bool, L="base", warm: bool = False):
    """A big rivet's domed head, three pixels square at (x, y): its crown lit at the upper left, shading to a
    dark foot at the lower right; `warm` is one the forge lights from below."""
    if warm:
        pal = {"c": STONE[6], "l": STONE[5], "m": STONE[3], "s": STONE[2], "d": STONE[1], "f": COAL[0]}
    elif night:
        pal = {"c": IRON[6], "l": IRON[5], "m": IRON[3], "s": IRON[2], "d": COAL[1], "f": COAL[0]}
    else:
        pal = {"c": C["white"], "l": STEEL[6], "m": STEEL[4], "s": STEEL[3], "d": IRON[2], "f": IRON[1]}
    p.sprite(x, y, ["cls", "lmd", "sdf"], pal, 1, L)


def top_band(p: Pix, night: bool, L="base"):
    """A footer's top edge as a heavier band than the frame's: five rows between the corner plates, lit along
    the top face and dark along the lower edge, a domed rivet every nine pixels, and its shadow on the plate."""
    if night:
        rows = (COAL[1], IRON[4], IRON[3], IRON[2], COAL[1])
    else:
        rows = (COAL[2], STEEL[6], STEEL[5], STEEL[4], IRON[1])
    x0, x1 = 8, p.w - 8
    for j, tone in enumerate(rows):
        p.hline(x0, x1, j, tone, L)
    x = x0 + 3
    while x + 3 <= x1:
        dome(p, x, 1, night, L)
        x += 9
    for xx in range(x0, x1):
        p.apx(xx, 5, X["shade_ink"], 0.4 if night else 0.3, "haze")


def rivet_joins(p: Pix, night: bool, rule: str, L="base"):
    """Rivets where a sheet's rules join: at both ends of every upright run of the rule's colour six or
    longer, the dividers between cells, and at both ends of every level run forty or longer that reaches the
    frame, the rules between rows. A dome sits over each join; those in the lower half warm by night."""
    base = p.layers[L]
    cells = {q for q, c in base.items() if c == rule}
    upright = {(x, y) for (x, y) in cells if (x - 1, y) not in cells and (x + 1, y) not in cells}
    level = {(x, y) for (x, y) in cells if (x, y - 1) not in cells and (x, y + 1) not in cells}
    spots = set()
    for (x, y) in upright:
        if (x, y - 1) in upright:
            continue
        yy = y
        while (x, yy + 1) in upright:
            yy += 1
        if yy - y >= 6:
            spots.add((x - 1, y - 2 if (x, y - 1) in cells else y - 1))
            spots.add((x - 1, yy - 1 if (x, yy + 1) in cells else yy - 2))
    for (x, y) in level:
        if (x - 1, y) in level:
            continue
        xx = x
        while (xx + 1, y) in level:
            xx += 1
        if xx - x >= 40 and (x <= 5 or xx >= p.w - 6):
            spots.add((x, y - 1))
            spots.add((xx - 1, y - 1))
    for (x, y) in spots:
        dome(p, x, y, night, L, warm=night and y > p.h // 2)


# --------------------------------------------------------------------------- the footer's floor and its mark
FLOOR = 5           # the rows of the hearth's stone a footer's floor is laid in, where its words leave them
HEAP = 12           # the most rows the coal is heaped over it where the cells leave a long stretch clear
HEAP_RUN = 30       # the fewest columns a heap of coal is laid along
# A tile of coal, 14 by 6: lumps lit on their upper left and dark at their foot, the black of the clinker between
# them. 1 to 5 the coal from its darkest to its lit edge.
COAL_TILE = [
    "13431.24431.24",
    "2342213443213.",
    "1321.1222.1121",
    ".24432.1243.24",
    "234421.234421.",
    "12221..12221.1",
]


def _coal_pattern(p: Pix, night: bool) -> str:
    """The coal's tile as a pattern, defined once a file: its id."""
    pid = f"cl{'n' if night else 'd'}"
    if ("pattern", pid) not in p.syms:
        k = -1 if night else 0
        rows: dict = {}
        for j, row in enumerate(COAL_TILE):
            for i, ch in enumerate(row):
                tone = COAL[0] if ch == "." else COAL[max(0, int(ch) + 1 + k)]
                rows.setdefault(tone, {}).setdefault(j, []).append(i)
        body = "".join(f'<path stroke="{t}" d="{Pix._d(r)}"/>' for t, r in rows.items())
        p.defs.append(f'<pattern id="{pid}" width="{len(COAL_TILE[0])}" height="{len(COAL_TILE)}" '
                      f'patternUnits="userSpaceOnUse">{body}</pattern>')
        p.syms[("pattern", pid)] = pid
    return pid


def _free(p: Pix, x, top, most) -> int:
    """The rows over row `top` at column x clear of every word by two rows and of everything drawn, up to `most`."""
    base = p.layers["base"]
    n = 0
    while n < most:
        y = top - 1 - n
        if y < 7 or (x, y) in base or not p.clear_of_words(x - 2, y - 2, x + 3, y + 3):
            break
        n += 1
    return n


def floor_top(p: Pix) -> int:
    """The row a footer's floor of stone begins at: FLOOR rows over the frame's foot band, or fewer, down to none,
    where the lowest word comes nearer the foot, two rows clear of it."""
    low = max((b[3] for b in p.words), default=0)
    return min(p.h - 4, max(p.h - 4 - FLOOR, low + 2))


def footer_floor(p: Pix, night: bool, rule: str) -> list:
    """A footer's floor once its words are set: a course of the hearth's stone along its foot between the frame's
    sides, laid over its foot band and up to FLOOR rows over it, as many as the lowest word leaves two rows clear,
    its top edge lit, the rules between the cells standing on it;
    the smith's mark, his anvil and hammer, standing on it at the right end of the stretch the cells leave clear
    where it has the room, as it has after Back to Top in a title block without notes; and along every stretch still
    clear, coal heaped as high as the room allows, up to HEAP rows, its lumps lit on their upper left, a few of them
    glowing on the hand's flame, by day the dull red of the last of the heat and by night bright, with the forge's
    light round them. Returns the top row of what lies at each column."""
    w, h = p.w, p.h
    base = p.layers["base"]
    top = floor_top(p)
    for xy in [xy for xy, c in base.items() if c == rule and xy[1] >= top]:
        del base[xy]
    masonry(p, 4, top, w - 8, h - top, night, seed=w + h, uid="mf")
    for x in range(4, w - 4):
        p.px(x, top, STONE[5 if night else 6] if (x // 3) % 4 else STONE[4 if night else 5])
    tops = [top] * w
    span = [_free(p, x, top, SMITHS_MARK_H) >= SMITHS_MARK_H if 6 <= x < w - 6 else False for x in range(w)]
    for x in range(w - 7 - SMITHS_MARK_W, 6, -1):
        if all(span[x:x + SMITHS_MARK_W + 2]):
            box = smiths_mark(p, x + 1, top, night)
            tops[box[0]:box[2]] = [box[1]] * (box[2] - box[0])
            break
    room = [_free(p, x, top, HEAP) if 6 <= x < w - 6 else 0 for x in range(w)]
    x = 6
    pid = _coal_pattern(p, night)
    glowing = []
    while x < w - 6:
        if room[x] < 4:
            x += 1
            continue
        b = next((i for i in range(x, w - 6) if room[i] < 4), w - 6)
        if b - x >= HEAP_RUN:
            n = b - x
            rise = [min(room[x + i] - 1, round(HEAP * math.sin(math.pi * (i + 0.5) / n) ** 0.7)) for i in range(n)]
            for i in range(1, n):                    # a heap's sides slope a row a column at the steepest
                rise[i] = min(rise[i], rise[i - 1] + 1)
            for i in range(n - 2, -1, -1):
                rise[i] = min(rise[i], rise[i + 1] + 1)
            for i in range(n):
                tops[x + i] = top - max(1, rise[i])
            xx = x
            while xx < b:
                t = tops[xx]
                e = next((i for i in range(xx, b) if tops[i] != t), b)
                p.shapes[p.layer("base")].append(f'<rect x="{xx}" y="{t}" width="{e - xx}" height="{top - t}" '
                                                 f'fill="url(#{pid})"/>')
                for xi in range(xx, e):
                    p.px(xi, t, COAL[5 if night else 6] if xi % 3 else COAL[4 if night else 5])
                xx = e
            rnd = random.Random(x * 31 + n)
            i = rnd.randint(2, 6)
            while i < n - 3:
                gy = tops[x + i] + rnd.randint(1, 4)
                if gy < top - 1:
                    glowing.append((x + i, gy))
                i += rnd.randint(5, 12)
        x = b
    for (gx, gy) in glowing:
        if night:
            p.px(gx, gy, FIRE[4])
            p.px(gx + 1, gy, FIRE[3])
            pool(p, gx + 1, gy + 0.5, 4, 3, FIRE[3], (0.12, 0.24), L="haze")
        else:
            p.px(gx, gy, FIRE[2])
            p.px(gx + 1, gy, FIRE[1])
    return tops


def smiths_mark(p: Pix, x, foot, night: bool, L="base") -> tuple:
    """The smith's mark in the round, at the right end of a footer: his anvil on its stump with its feet on the
    row above `foot` from column x, the hammer laid across its face and the tongs leaning against the stump, by night
    a blade cooling on it, still red. Returns its box (x0, y0, x1, y1)."""
    a = anvil(p, x, foot, night, L, small=True)
    face = a["face"]
    hammer_head(p, x + 12, face - 4, night, L)
    for j in range(1, 8):
        p.px(x + 18 + j, face - 2 + j // 4, OAK[3 if night else 5] if j % 2 else OAK[2 if night else 4], L)
    tongs(p, x + 21, foot, 9, night, L)
    if night:
        for i in range(7):
            p.px(x + 3 + i, face - 1, FIRE[2] if i < 3 else FIRE[1], L)
    return (x - 1, face - 5, x + 26, foot)


SMITHS_MARK_W, SMITHS_MARK_H = 27, 17      # the room the smith's mark takes on a footer's floor


def foot_glow(p: Pix, uid: str = "fg", strength: float = 0.24):
    """The forge's light along a sheet's foot by night: an ember glow rising from the bottom band over the
    plate and fading out a dozen rows up, under everything drawn on it."""
    p.defs.append(f'<linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{EMBER[5]}" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="{EMBER[5]}" stop-opacity="{strength}"/></linearGradient>')
    p.shapes["haze"].append(f'<rect x="4" y="{p.h - 18}" width="{p.w - 8}" height="14" fill="url(#{uid})"/>')


def chain(p: Pix, x0, x1, y, night: bool, L="base"):
    """A chain lying level from x0 to x1 along rows `y - 1` to `y + 1`: rings five pixels long, each lit along
    its crown with a glint and dark beneath, the plate showing through its eye, joined by the links between
    them seen edge on."""
    k = -1 if night else 0
    crown, glint, side = STEEL[5 + k], STEEL[6 + k], STEEL[3 + k]
    under, bar = (STEEL[0] if night else IRON[1]), STEEL[2 + k]
    x = x0
    while x < x1:
        e = min(x + 5, x1)
        for xx in range(x, e):
            p.px(xx, y - 1, glint if xx == x + 1 else crown, L)
            p.px(xx, y + 1, under, L)
        for xx in (x, e - 1):
            p.px(xx, y, side, L)
        for xx in range(e, min(e + 2, x1)):
            p.px(xx, y, bar, L)
        x += 7


def hanging_tag(p: Pix, x, y, night: bool, big: bool = False, brass: bool = False, outline_only: bool = False,
                L="base"):
    """A stamped steel tag hung from the chain by a link at (x, y): the link, then the tag, eight pixels wide
    (ten for a big release) and nine deep, its top corners chamfered, a hole at its top for the link, lit
    along its top and left edges, shaded along its foot and right, with a dark line round it. `brass` is the
    latest release's tag; `outline_only` an empty tag for one still to come. A tag is remembered on the
    drawing, so the latest can be found once today's mark is set."""
    k = -1 if night else 0
    R = BRASS if brass else STEEL
    w = 10 if big else 8
    px0, py0 = x - w // 2, y + 2
    p.px(x, y, STEEL[4 + k], L)
    p.px(x, y + 1, STEEL[3 + k], L)
    cells = {(px0 + i, py0 + j) for j in range(9) for i in range(w) if not (i in (0, w - 1) and j == 0)}
    if outline_only:
        for (qx, qy) in cells:
            i, j = qx - px0, qy - py0
            if j in (0, 8) or i in (0, w - 1) or (j == 1 and i in (0, w - 1)):
                p.px(qx, qy, STEEL[3 + k], L)
        p.px(x, py0 + 1, STEEL[3 + k], L)
        return
    for (qx, qy) in cells:
        i, j = qx - px0, qy - py0
        tone = R[4 + k]
        if j == 0 or (i == 0 and j < 8) or (j == 1 and i == 1):
            tone = R[6 + k]
        elif j == 8 or i == w - 1 or (j == 1 and i == w - 2):
            tone = R[2 + k]
        p.px(qx, qy, tone, L)
    _outline(p, cells, IRON[0], L)
    p.px(x, py0 + 1, COAL[1], L)
    tags = getattr(p, "tags", None)
    if tags is None:
        tags = p.tags = []
    tags.append((x, y, big))


def ingot(p: Pix, bx, base, bw, v, heat_f: float, night: bool, L="base"):
    """An iron ingot stood on end, `bw` wide and `v` tall on `base`, hot in proportion to `heat_f` (0 cold, 1
    white hot): a column lit from the left with its top face catching the light, cold steel through dull
    red and orange to yellow heat, and by night a glow round the hot ones."""
    if heat_f < 0.3:
        R, lo, hi = STEEL, 2, 5
    elif heat_f < 0.55:
        R, lo, hi = EMBER, 2, 4
    elif heat_f < 0.8:
        R, lo, hi = EMBER, 3, 5
    else:
        R, lo, hi = FLAME, 3, 5
    if night and R is STEEL:
        lo, hi = 1, 4
    for xx in range(bx, bx + bw):
        nx = 2 * (xx - bx + 0.5) / bw - 1
        lam = max(0.0, nx * LX + math.sqrt(max(0.0, 1 - nx * nx)) * LZ)
        t = max(lo, min(hi, round(lo + 0.2 + (hi - lo) * lam)))
        for yy in range(base - v, base):
            tone = R[t]
            if yy == base - v:
                tone = R[min(6, hi + 1)]
            elif yy == base - 1:
                tone = R[max(0, lo - 1)]
            p.px(xx, yy, tone, L)
    p.box(bx - 1, base - v - 1, bw + 2, v + 1, IRON[0] if night else IRON[1], L)
    if night and heat_f >= 0.55:
        alphas = (0.08, 0.16) if heat_f < 0.8 else (0.1, 0.2, 0.3)
        pool(p, bx + bw / 2, base - v / 2, bw + 3, v / 2 + 3, EMBER[5], alphas)


def spark_glint(p: Pix, x, y, night: bool, L="base", big: bool = False):
    """A spark caught still, five by five (seven, `big`), on the hand's flame: a white heart and arms that fade to
    orange, and by night a glow round it."""
    p.px(x, y, FIRE[6], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, FIRE[5], L)
    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        p.px(x + dx, y + dy, (FIRE[3] if big else FIRE[3] + ":0.6"), L)
    if big:
        for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3)):
            p.px(x + dx, y + dy, FIRE[3] + ":0.5", L)
        for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            p.px(x + dx, y + dy, FIRE[3] + ":0.6", L)
        if night:
            pool(p, x + 0.5, y + 0.5, 6, 6, EMBER[5], (0.1, 0.22), L="haze", shape=False)


def bolt(p: Pix, cx, cy, night: bool, L="base"):
    """A hexagonal bolt head, five across, centred on (cx, cy), lit from the upper left."""
    k = -1 if night else 0
    art = [".LLL.", "LFFFd", "LFFdd", ".ddd."]
    pal = {"L": STEEL[6 + k], "F": STEEL[4 + k], "d": STEEL[2 + k]}
    p.sprite(cx - 2, cy - 2, art, pal, 1, L)
    p.px(cx, cy - 1, STEEL[5 + k], L)


def helm(p: Pix, cx, cy, night: bool, kind: int = 0, L="base", crest=None):
    """A knight's helm seen face on, fifteen across and fourteen deep, centred on (cx, cy): a steel dome lit
    from the upper left, a visor with its rim lit and its eye slit dark, and a faceplate below where a name
    can be stamped. `kind` 0 is a sallet with a brass brow and a crest, 1 a bascinet with a plume, 2 a great
    helm with a nasal bar through its slit and a crest; 3 is a helm with its visor down and breathing holes,
    for a bot. `crest` is the colour the crest or the plume is dyed, the knight's own."""
    k = -1 if night else 0
    dome = ["....HHHHHHH....", "..HHHHHHHHHHH..", ".HHHHHHHHHHHHH.", ".HHHHHHHHHHHHH."]
    x0, y0 = cx - 7, cy - 7
    cells = {}
    for j, row in enumerate(dome):
        for i, ch in enumerate(row):
            if ch == "H":
                cells[(x0 + i, y0 + j)] = (i + 0.5 - 7.5) / 7.5, (j + 0.5 - 5) / 7
    for (qx, qy), (nx, ny) in cells.items():
        nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        lam = max(0.0, nx * LX + ny * LY + nz * LZ)
        p.px(qx, qy, STEEL[max(1, min(6, round(2.2 + 3.6 * lam) + k))], L)
    crest = crest or EMBER[4 + k]
    if kind == 1:                                   # the bascinet's knob, where its plume is set
        for j, row in enumerate(["..###..", ".#####.", "..###.."]):
            for i, ch in enumerate(row):
                if ch == "#":
                    p.px(cx - 3 + i, y0 - 2 + j, STEEL[5 + k], L)
        p.px(cx, y0 - 1, STEEL[6 + k], L)
    elif kind != 3:                                 # a crest of dyed horsehair along the ridge
        for j, row in enumerate(["...#...", "..###..", ".#####."]):
            for i, ch in enumerate(row):
                if ch == "#":
                    p.px(cx - 3 + i, y0 - 3 + j, crest, L)
    # the visor: its rim lit from above, brass on a sallet; the eye slit dark; its lower lip in shade
    p.hline(x0, x0 + 15, cy - 3, BRASS[4 + k] if kind == 0 else STEEL[5 + k], L)
    for i in range(15):
        if kind == 3:
            tone = COAL[0] if i in (3, 6, 9, 12) else STEEL[3 + k]
        else:
            tone = COAL[0] if 1 < i < 13 else IRON[3 + k]
        p.px(x0 + i, cy - 2, tone, L)
        p.px(x0 + i, cy - 1, STEEL[2 + k], L)
    for j in range(cy, cy + 7):
        for i in range(15):
            if i in (0, 14) and j >= cy + 5:
                continue
            tone = STEEL[5 + k] if i == 1 else STEEL[4 + k]        # one tone, so any initials read on it
            if j == cy + 6 or i in (0, 14):
                tone = STEEL[2 + k]
            p.px(x0 + i, j, tone, L)
    if kind == 2:
        p.vline(cx, cy - 2, cy + 1, IRON[3 + k], L)
    if kind == 3:
        for (i, j) in ((3, 2), (7, 2), (11, 2), (5, 4), (9, 4)):
            p.px(x0 + i, cy + j, COAL[1], L)
        p.sprite(cx - 2, cy - 7, [".#.", "###", ".#."], {"#": BRASS[4 + k]}, 1, L)
    _outline(p, {q for q in cells} | {(x0 + i, j) for i in range(15) for j in range(cy - 3, cy + 7)
                                      if not (i in (0, 14) and j >= cy + 5)}, IRON[0], L)


def plume(p: Pix, x, y, night: bool, L="base", colour=None):
    """A plume of feathers in the knight's colour, streaming to the right from (x, y)."""
    k = -1 if night else 0
    art = ["#...", ".##.", "..##", "...#"]
    p.sprite(x, y, art, {"#": colour or EMBER[4 + k]}, 1, L)


# --------------------------------------------------------------------------- icons
# 7x7 icons for the link buttons, lit from the upper left like everything else. Tones: L S d steel from its
# glint to its shade, o O oak, b B brass, # ink.
ICONS = {
    "hammer": [".LSSSSd", ".SSSSSd", ".ddddd.", "...O...", "...O...", "...o...", "...o..."],
    "anvil": [".......", "LSSSSSS", "SdSSSSd", "...ddSd", "...SSd.", "...SSd.", ".ddddd."],
    "horseshoe": [".LSSSS.", "LS...Sd", "S.....d", "S.....d", "S.....d", "Sd...dd", "......."],
    "blade": ["......L", ".....LS", "..b.LS.", "...B...", "..o.b..", ".o.....", "B......"],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones: dark steel on the plate by day, bright steel on the dark plate by night."""
    if night:
        return {"L": STEEL[6], "S": STEEL[4], "d": STEEL[2], "o": OAK[3], "O": OAK[4], "b": BRASS[3], "B": BRASS[5],
                "#": ink}
    return {"L": STEEL[5], "S": STEEL[2], "d": IRON[1], "o": OAK[2], "O": OAK[3], "b": BRASS[2], "B": BRASS[4],
            "#": ink}


def mini_anvil(p: Pix, x, y, night: bool, L="base"):
    """A little anvil, nine by six, top-left at (x, y): the section's mark."""
    k = -2 if night else 0
    art = [".FFFFFFF.", "hSSSSSSSd", ".dSSSSSd.", "...SSS...", "...SSS...", ".SSSSSSSd"]
    pal = {"F": STEEL[5 + k], "h": STEEL[4 + k], "S": STEEL[3 + k], "d": STEEL[1 + k]}
    p.sprite(x, y, art, pal, 1, L)
    p.px(x + 1, y, STEEL[6 + k], L)


def mini_hammer(p: Pix, x, y, night: bool, L="base"):
    """A little hammer, its head six by four at (x, y), the haft hanging down and left: the strip's mark."""
    k = -2 if night else 0
    hammer_head(p, x, y, night, L)
    for j in range(1, 7):
        p.px(x + 3 - (j // 3), y + 3 + j, OAK[4 + k] if j % 2 else OAK[3 + k], L)


def heart(p: Pix, x, y, L="base"):
    """A heart beaten out of red-hot iron, seven by six, lit on its upper-left lobe."""
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): EMBER[i] for i in range(7)}, 1, L)
