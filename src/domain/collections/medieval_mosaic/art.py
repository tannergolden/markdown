# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mosaic set's scenery and sprites, drawn on the shared pixel canvas.

The ground every sheet is laid in, burnished gold tesserae by day in courses of close golds with fine grout, the
sheen that crosses it in a moving header, and by night the vault of quiet lapis tesserae sown with gold stars, the
tiles by each lamp glinting in its light; the jewelled band of its frame with a cut stone in a gold cell at each
corner; the running wave scroll along a header's top; titles built tile by tile; the scenes its headers open on (the
peacocks drinking at the fountain under the vine in the apse, the palace arcade with its curtains drawn on the
empress's court and its door with its fountain, the port with its lighthouse, its ships and its city, the peacock
before its fan, the doves at the basin between their pair of peacocks, and the vine's peopled scroll with its birds);
the bronze lamp crowns and the oil lamps that hang lit in the dark; the floor mosaic a footer is laid on, its
guilloche and its opus sectile, and the doves of Pliny at their bowl; and the tesserae, marble and porphyry every
element and badge is made of. Everything is shaded from the one light in the upper left on the set's own ramps, the
flames on the collection's flame and the faces on its three skins (see `collections.hand`); the big quiet things (the
ground, the frame, the wave scroll, the floor) are pattern tiles of whole tiles, so the files stay light enough to
carry the rest."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, Pix, fold, num
from ..hand import MEDIEVAL
from .palette import CALM, NIGHT_SKY, RAMP, X, step

K = X["outline"]                 # the row of dark tesserae every figure is set round with
TILE, GOLD, LAPIS, AZURE = RAMP["tile"], RAMP["gold"], RAMP["lapis"], RAMP["azure"]
TEAL, GREEN, RED, PURPLE = RAMP["teal"], RAMP["green"], RAMP["red"], RAMP["purple"]
PEARL, STONE, EARTH, VAULT = RAMP["pearl"], RAMP["stone"], RAMP["earth"], RAMP["vault"]
BRONZE, FLAME, PORPHYRY = RAMP["bronze"], RAMP["flame"], RAMP["porphyry"]
SKINS = tuple(RAMP[f"skin{i}"] for i in range(3))      # the hand's skins, light to dark


# --------------------------------------------------------------------------- drawing helpers
def flip(art: list) -> list:
    """Pixel art turned to face the other way."""
    return [row[::-1] for row in art]


def stamp(p: Pix, x, y, art, pal, L="base", below=None):
    """Pixel art from rows of characters with its top-left at (x, y), each looked up in `pal`; a character the
    palette lacks is left clear, and rows from `below` down are left out."""
    for j, row in enumerate(art):
        if below is not None and y + j >= below:
            continue
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                p.px(x + i, y + j, c, L)


def cells_of(art: list, x=0, y=0) -> set:
    """The cells pixel art covers with its top-left at (x, y)."""
    return {(x + i, y + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."}


def keep(p: Pix, cells):
    """Remember cells a shape fills without setting them pixel by pixel, so a check that gathers what a scene draws
    finds them as it finds pixels set one by one."""
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
    for c, rows in cols.items():
        if not rows:
            continue
        col, a = c.split(":") if ":" in c else (c, None)
        strokes, blocks = Pix._d(rows), _blocks(rows)
        if len(blocks) + 2 < len(strokes):
            out.append(f'<path fill="{col}"' + (f' fill-opacity="{a}"' if a else "") + f' d="{blocks}"/>')
        else:
            out.append(f'<path stroke="{col}"' + (f' stroke-opacity="{a}"' if a else "") + f' d="{strokes}"/>')
    return "".join(out)


def cols_of(cells: dict) -> dict:
    """{(x, y): colour} as {colour: {y: [x, ...]}}, for `paths`."""
    out: dict = {}
    for (x, y), c in cells.items():
        out.setdefault(c, {}).setdefault(y, []).append(x)
    return out


def pattern(p: Pix, pid: str, w: int, h: int, cells: dict, x0=0, y0=0) -> str:
    """A pattern tile `w` by `h` from (x0, y0) of {(x, y): colour}, defined once a file. Returns its id."""
    key = ("pattern", pid)
    if key not in p.syms:
        p.defs.append(f'<pattern id="{pid}" x="{x0}" y="{y0}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
                      f'{paths(cols_of(cells))}</pattern>')
        p.syms[key] = pid
    return pid


def lay(p: Pix, pid: str, x, y, w, h, L="base"):
    """A block laid in pattern `pid`, its cells kept as a sprite's."""
    if w <= 0 or h <= 0:
        return
    p.shapes[L].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')
    keep(p, {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)})


def twin(p: Pix, key, draw, axis: int, z: float = 0.0, name="pair", lamps=()) -> dict:
    """Draw something symmetrical once and place it twice: `draw(q)` draws its left half on a scratch sheet the size
    of `p`, which is kept as one symbol and placed as drawn and again turned about the column line `axis`, on a layer
    of its own at depth `z`. By night the light of `lamps`, each (cx, cy, r) and placed as symmetrically as the thing
    they light, is laid into its colours before it is kept (see `light_cells`). Its cells, both halves, are kept as a
    sprite's. Returns the cells of both halves and their colours."""
    q = Pix(p.w, p.h, lite=p.lite)
    q.night = getattr(p, "night", False)
    draw(q)
    cells = dict(q.layers["base"])
    if not cells:
        return {}
    if lamps and getattr(p, "night", False):
        light_cells(cells, [(cx, cy, r * (0.6 if p.lite else 1)) for (cx, cy, r) in lamps])
    sid = p.symbol((key, axis), cells)
    L = p.layer(f"{name}{len(p.layers)}", z=z)
    p.shapes[L].append(f'<use href="#{sid}"/><use href="#{sid}" transform="matrix(-1 0 0 1 {2 * axis} 0)"/>')
    both = dict(cells)
    both.update({(2 * axis - 1 - x, y): c for (x, y), c in cells.items()})
    keep(p, set(both))
    return both


def clear(p: Pix, cells, margin=2) -> bool:
    """Whether every one of `cells` keeps `margin` units from every word."""
    return all(p.clear_of_words(x - margin, y - margin, x + margin + 1, y + margin + 1) for x, y in cells)


# --------------------------------------------------------------------------- the ground
COURSE = 4                  # a course of tesserae: three rows of tile and one of grout
TW, TH = 48, 24             # the ground's pattern tile: six courses, each its own run of tile widths


def _courses(seed=11) -> list:
    """The tiles of the ground's pattern tile, as (x, y, w, tone): six courses, each of tiles three or four wide
    with a column of grout after each, set from its own offset so no two courses line up, and each tile given
    one of five tones by the angle it was set at (2 the darkest, 6 the brightest, 4 the field the words calm to).
    A few tiles carry a glint, the light thrown back by one face of the glass (tone 7)."""
    rnd = random.Random(seed)
    tiles = []
    for row in range(TH // COURSE):
        widths, total = [], 0
        while total < TW:
            w = rnd.choice((4, 4, 4, 5, 5, 3))
            if TW - total - w in (1, 2):
                w = TW - total
            widths.append(w)
            total += w
        x = rnd.randrange(5)
        for w in widths:
            tone = rnd.choices((2, 3, 4, 5, 6), (6, 24, 38, 24, 8))[0]
            if rnd.random() < 0.05:
                tone = 7
            tiles.append((x, row * COURSE, w - 1, tone))
            x += w
    return tiles


TILES = _courses()


def _ground(uid: str, night: bool, lite=False) -> str:
    """The ground's pattern tile, 48 by 24: by day each tile of burnished gold in its tone over the grout the sheet is
    laid in; by night each tile of the vault's quiet lapis lightened or deepened over its band, which shows through
    the plainest. Drawn lighter, the ground keeps its courses but lays every tile in one of three tones, and by night
    in one of two, letting the grout between the tiles of a course go."""
    cells = {}
    for (x, y, w, tone) in TILES:
        if lite:
            tone = 4 if tone in (4, 7) else 3 if tone < 4 else 5
            if night:
                tone = 4 if tone != 5 else 5
        for yy in range(y, y + COURSE - 1):
            for xx in range(x, x + w):
                q = (xx % TW, yy)
                if not night:
                    c = TILE[tone] if tone < 7 else TILE[6]
                    if tone == 7 and (xx - x, yy - y) == (0, 0):
                        c = GOLD[6]
                else:
                    c = {2: f"{VAULT[0]}:.35", 3: f"{VAULT[3]}:.3", 4: None, 5: f"{VAULT[4]}:.32",
                         6: f"{VAULT[4]}:.5", 7: f"{VAULT[6]}:.38"}[tone]
                    if tone == 7 and (xx - x, yy - y) == (0, 0):
                        c = f"{LAPIS[6]}:.5"
                if c:
                    cells[q] = c
        if night:
            for xx in range(x, x + w + 1):
                cells[(xx % TW, y + COURSE - 1)] = VAULT[0]
            for yy in range(y, y + COURSE - 1) if not lite else ():
                cells[((x + w) % TW, yy)] = VAULT[0]
    return (f'<pattern id="{uid}g" width="{TW}" height="{TH}" patternUnits="userSpaceOnUse">'
            f'{paths(cols_of(cells))}</pattern>')


def band_edges(h: int) -> list:
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p"):
    """The ground a drawing sits on: by day the gold ground of the apse, small tiles of close golds set in
    irregular courses with fine grout between them; by night the starry vault, tiles of deep lapis over a band of
    the vault's blue, a shade deeper overhead. The drawing keeps which sheet it is and whether it is night, for the
    hooks the layout calls without saying."""
    w, h = p.w, p.h
    p.sheet, p.night = uid, night
    if not night:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{TILE[1]}"/>')
    else:
        edges = band_edges(h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                p.under.append(f'<rect y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    p.defs.append(_ground(uid, night, lite=p.lite))
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}g)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`, the even field the tiles calm to behind a word: by day the gold, by night the
    row's band of the vault."""
    if not night:
        return CALM
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


def calm(p: Pix, night: bool, boxes=None):
    """Behind every word the tiles calm to an even field: over each word's box, a unit wider all round, the ground is
    laid even in the colour behind it (by night band by band), and whatever glitter lies there is taken up, and any star
    within a unit of it, so no grout, glint or star lies under a letter or against it. By night the field is lifted to
    the tiles' own mean round it, which a drawing made lighter leaves out. The boxes of each colour are laid as one
    field, those that meet or overlap merged."""
    boxes = p.words if boxes is None else boxes
    done = getattr(p, "calmed", set())
    edges = band_edges(p.h)
    rects = []
    for (x0, y0, x1, y1) in boxes:
        if (x0, y0, x1, y1) in done:
            continue
        done.add((x0, y0, x1, y1))
        x0, y0, x1, y1 = max(0, x0 - 1), max(0, y0 - 1), min(p.w, x1 + 1), min(p.h, y1 + 1)
        if x1 <= x0 or y1 <= y0:
            continue
        if not night:
            rects.append((CALM, x0, y0, x1, y1))
        else:
            for i, col in enumerate(NIGHT_SKY):
                a, b = max(y0, edges[i]), min(y1, edges[i + 1])
                if b > a:
                    rects.append((col, x0, a, x1, b))
        for name, layer in p.layers.items():
            if name.startswith(("haze", "tb", "st")):
                for xy in [xy for xy in layer if x0 <= xy[0] < x1 and y0 <= xy[1] < y1]:
                    del layer[xy]
                p.uses[name] = [u for u in p.uses[name] if not (x0 - 8 < u[2] < x1 + 1 and y0 - 8 < u[3] < y1 + 1)]
    p.calmed = done
    by: dict = {}
    for col, x0, y0, x1, y1 in rects:
        rows = by.setdefault(col, {})
        for y in range(y0, y1):
            rows.setdefault(y, set()).update(range(x0, x1))
    for col, rows in by.items():
        p.under.append(f'<path fill="{col}" d="{_blocks({y: sorted(xs) for y, xs in rows.items()})}"/>')
    if night and rects and not p.lite:
        lift: dict = {}
        for rows in by.values():
            for y, xs in rows.items():
                lift.setdefault(y, set()).update(xs)
        p.under.append(f'<path fill="{LIFT}" fill-opacity="{CALM_LIFT}" '
                       f'd="{_blocks({y: sorted(xs) for y, xs in lift.items()})}"/>')


CALM_LIFT = 0.16            # by night the even field under a word is the band lifted to the tiles' own mean
LIFT = VAULT[4]             # by the vault's own lapis


def glitter(p: Pix, x0, y0, x1, y1, n, seed=1, avoid=()):
    """In a moving header the gold glitters: single tiles of the ground catch the light and twinkle, here and there,
    on the engine's twinkle as the stars do by night, a third of them in each of its three phases. Only on tiles of
    the ground, under everything drawn on it, kept out of the boxes in `avoid`; the still file has none."""
    rnd = random.Random(seed)
    spots = []
    for _ in range(n * 4):
        if len(spots) >= n:
            break
        tx, ty, tw, _ = rnd.choice(TILES)
        gx = tx + TW * rnd.randrange(max(1, p.w // TW + 1))
        gy = ty + TH * rnd.randrange(max(1, p.h // TH + 1))
        if not (x0 <= gx and gx + tw <= x1 and y0 <= gy and gy + 3 <= y1):
            continue
        if any(a - 2 <= gx + tw and gx <= c + 2 and b - 2 <= gy + 3 and gy <= d + 2 for a, b, c, d in avoid):
            continue
        spots.append((gx, gy, tw))
    for i, (gx, gy, tw) in enumerate(spots):
        L = p.twinkle(i, back=True)
        for xx in range(gx, gx + tw):
            for yy in range(gy, gy + 3):
                p.px(xx, yy, X["glint"] if (xx - gx, yy - gy) == (0, 0) else GOLD[6] if yy == gy else GOLD[5], L)


SHEEN_BEAT = 24.0           # seconds the sheen takes to cross the gold and rest: one of the hand's slow sweeps
SHEEN_W = 36                # the width of the band of light
SHEEN_LADDER = (TILE[4], TILE[5], TILE[6], GOLD[5], GOLD[6], X["glint"])   # a tile's tones as the light finds it


def _sheen_tile(lite=False) -> dict:
    """A tile of the ground as the sheen finds it, 48 by 24: every tile lit two tones up the ladder from where it lies,
    so each keeps its own angle to the light, its top row a tone brighter still and the brightest throwing back a
    glint. Drawn lighter, a tile is lit in one tone, the brighter of its two."""
    cells = {}
    for (x, y, w, tone) in TILES:
        face = SHEEN_LADDER[min(tone, 6) - (1 if lite else 2)]
        edge = SHEEN_LADDER[min(tone, 6) - 1]
        for yy in range(y, y + COURSE - 1):
            for xx in range(x, x + w):
                cells[(xx % TW, yy)] = edge if yy == y else face
    return cells


def sheen(p: Pix, y0, y1):
    """In a moving header a slow sheen crosses the gold: the light comes in a band slanting across the ground and
    travels it from left to right, the tiles in its way catching it in turn, each as its angle lets it, and rests
    before it comes round again. The band of lit tiles is drawn once, a pattern tile of the ground's own courses, and
    only the window it is seen through moves. It lies on the ground under everything drawn and under the even field
    behind every word, so no word has it behind it."""
    pid = pattern(p, "sh", TW, TH, _sheen_tile(p.lite))
    h = y1 - y0
    cid = f"shc{len(p.under)}"
    p.under.append(
        f'<clipPath id="{cid}"><path d="M{h} {y0}h{SHEEN_W}l-{h} {h}h-{SHEEN_W}z"><animateTransform '
        f'attributeName="transform" type="translate" values="-{h + SHEEN_W} 0;{p.w} 0;{p.w} 0" keyTimes="0;.68;1" '
        f'dur="{num(SHEEN_BEAT)}s" repeatCount="indefinite"/></path></clipPath>'
        f'<rect y="{y0}" width="{p.w}" height="{h}" fill="url(#{pid})" clip-path="url(#{cid})"/>')


def lamp_glints(p: Pix, seed=7):
    """By night in a moving header the tiles nearest each lamp glint in its light, a few at a time, twinkling as the
    stars do, on the gold of the apse and the lapis of the vault alike: the top of a tile set toward the flame thrown
    back warm. Only where the ground shows, under everything drawn on it, never within two units of a word. A
    drawing made lighter keeps one, by the first lamp that has room for it, as it lets most of the stars go."""
    rnd = random.Random(seed)
    taken = set(p.layers["base"]) | getattr(p, "filled", set())
    starts = {}
    for (x, y, w, _) in TILES:
        starts.setdefault(y, []).append((x, w))
    n = 0
    for (cx, cy, r, _, own, _) in p.lamps:
        placed = []
        for _ in range(40):
            if len(placed) >= 3 or (p.lite and n):
                break
            a, d = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.25, 0.7) * r
            gx, gy = int(cx + d * math.cos(a)), int(cy + d * math.sin(a) * 0.8)
            row = gy - gy % COURSE
            tx, tw = next(((x, w) for (x, w) in starts[row % TH] if x <= gx % TW < x + w or
                           x <= gx % TW + TW < x + w), (None, 0))
            if tx is None:
                continue
            tx = gx - (gx % TW - tx) % TW
            cells = [(tx + i, row) for i in range(min(tw, 3))] + [(tx, row + 1)]
            if not (FW < tx and tx + 3 < p.w - FW and SCROLL_FOOT < row < p.h - FW - 2):
                continue
            if any(c in taken or c in own for c in cells) or not p.clear_of_words(tx - 2, row - 2, tx + 5, row + 4):
                continue
            if any(abs(tx - qx) < 4 and abs(row - qy) < 4 for qx, qy in placed):
                continue
            placed.append((tx, row))
            L = p.twinkle(n, back=True)
            n += 1
            for i, (x, y) in enumerate(cells):
                p.px(x, y, FLAME[6] if i == 0 else GOLD[5], L)


# The vault's gold stars: an eight-pointed star of gold tesserae in three sizes, the smallest a point of four rays.
STARS = (
    [".Y.", "YWY", ".Y."],
    ["Y.Y.Y", ".YyY.", "YyWyY", ".YyY.", "Y.Y.Y"],
    ["...Y...", ".Y.Y.Y.", "..YyY..", "YYyWyYY", "..YyY..", ".Y.Y.Y.", "...Y..."],
)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """By night the vault's gold stars, eight-pointed and of three sizes, scattered over the lapis, some twinkling in
    a moving header; on a sheet that is not a header (`faint`) fewer and smaller. None inside a box in `avoid`, and
    any that a word is later set over is taken up when the tiles calm behind it (see `calm`). A drawing made lighter
    sows a quarter of them."""
    rnd = random.Random(seed)
    placed = []
    for i in range(n if not p.lite else (n + 3) // 4):
        size = 0 if faint else rnd.choices((0, 1, 2), (5, 4, 2))[0]
        art = STARS[size]
        s = len(art)
        x, y = rnd.randrange(x0, max(x0 + 1, x1 - s)), rnd.randrange(y0, max(y0 + 1, y1 - s))
        if any(a - 1 <= x + s and x <= c + 1 and b - 1 <= y + s and y <= d + 1 for a, b, c, d in avoid):
            continue
        if any(abs(x - qx) < 9 and abs(y - qy) < 7 for qx, qy in placed):
            continue
        placed.append((x, y))
        L = p.twinkle(i, back=True) if twinkling and rnd.random() < 0.45 else "st"
        if L == "st" and L not in p.layers:
            p.layer("st", z=-14)
        pal = {"Y": GOLD[4] if not faint else GOLD[3], "y": GOLD[5], "W": GOLD[6]}
        p.sprite(x, y, art, pal, L=L, reuse=True)


# --------------------------------------------------------------------------- the frame
FW = 5                      # the frame's width down each side and along the foot
ZIG = (0, 0, 1, 1, 2, 2, 1, 1)  # where the white tesserae run across the band, row by row: a zigzag


def _zig_cells(night: bool, upright: bool, lite=False) -> dict:
    """A pattern tile of the jewelled band: a zigzag of white tesserae stepping across three rows of the band, the
    triangles on its outer side laid in red and those on its inner side in green, each tile its own tone; the dark
    row of setting along the outer edge and a gold line along the inner. Eight along the band; upright for a side."""
    k = -1 if night else 0
    cells = {}
    n = len(ZIG)
    for t in range(n):
        z = ZIG[t]
        for i in range(3):
            v = 0 if lite else 1
            if i == z:
                c = PEARL[(6, 5)[t % 2 * v] + k]
            elif i < z:
                c = RED[(3, 4)[(t + i) % 2 * v] + k]
            else:
                c = GREEN[(3, 2)[(t + i) % 2 * v] + k]
            cells[(i + 1, t) if upright else (t, i + 1)] = c
        cells[(0, t) if upright else (t, 0)] = K
        cells[(4, t) if upright else (t, 4)] = GOLD[(4, 3)[t % 2 * (0 if lite else 1)] + k]
    return cells


# A cut stone in its gold cell at a corner of the frame, 7 by 7: the cell's gold lit along its top and left and in
# shade along its foot and right, and in it a domed stone, its light caught at its upper left and its foot in shade.
# Y G g o the gold light to dark, w the stone's glint, T t S s the stone light to dark.
CORNER = [
    "YGGGGGg",
    "GGTwtGg",
    "GTttSsg",
    "GtttSsg",
    "GtSSssg",
    "ggsssgo",
    "ggggggo",
]
# The same, 7 by 14, at a header's top corners, where the wave scroll ends in a tall cell with an oval stone in it.
CORNER_TALL = [
    "KKKKKKK",
    "YGGGGGg",
    "GGTwtGg",
    "GTwttSg",
    "GTtttSg",
    "GtttSsg",
    "GtttSsg",
    "GttSSsg",
    "GtSSSsg",
    "GtSSssg",
    "GgsssGg",
    "ggggggo",
    "gGGGGgo",
    "KKKKKKK",
]


def corner_stone(p: Pix, x, y, night: bool, stone: str, tall=False, L="base"):
    """A cut stone in its gold cell, its top-left at (x, y): a garnet or an emerald by turns round the frame."""
    k = -1 if night else 0
    S = RAMP[stone]
    pal = {"K": K, "Y": GOLD[6 + k], "G": GOLD[4 + k], "g": GOLD[3 + k], "o": GOLD[1], "w": S[6] if not night else S[5],
           "T": S[5 + k], "t": S[4 + k], "S": S[3 + k], "s": S[2 + k]}
    stamp(p, x, y, CORNER_TALL if tall else CORNER, pal, L)


def frame(p: Pix, night: bool, header: bool = False, uid="fr", footer: bool = False):
    """The sheet's border: the jewelled band, a zigzag of white tesserae between triangles of red and green, set
    between a dark row and a gold line, down each side and along the foot, and along the top of any sheet but a
    header (whose top the wave scroll takes); a footer's foot is left to the floor mosaic it stands on (see `floor`);
    and at each corner a cut stone in a gold cell, garnet and emerald by turns, the header's top two tall to end the
    scroll. One tile of the band lays all four sides, turned to each."""
    w, h = p.w, p.h
    top = 14 if header else FW
    pid = pattern(p, f"{uid}z", FW, len(ZIG), _zig_cells(night, upright=True, lite=p.lite))
    sides = [(top, h - FW, ""), (top, h - FW, f' transform="matrix(-1 0 0 1 {w} 0)"')]
    if not footer:
        sides.append((FW, w - FW, f' transform="matrix(0 -1 1 0 0 {h})"'))
    if not header:
        sides.append((FW, w - FW, ' transform="matrix(0 1 1 0 0 0)"'))
    for a, b, turn in sides:
        p.shapes["base"].append(f'<rect y="{a}" width="{FW}" height="{b - a}" fill="url(#{pid})"{turn}/>')
    keep(p, {(x, y) for y in range(top, h - FW) for x in list(range(FW)) + list(range(w - FW, w))}
         | (set() if footer else {(x, y) for x in range(w) for y in range(h - FW, h)})
         | (set() if header else {(x, y) for x in range(w) for y in range(FW)}))
    corner_stone(p, 0, h - 7, night, "green")
    corner_stone(p, w - 7, h - 7, night, "red")
    corner_stone(p, 0, 0, night, "red", tall=header)
    corner_stone(p, w - 7, 0, night, "green", tall=header)


# --------------------------------------------------------------------------- the wave scroll
# A crest of the running wave scroll, 16 wide and 10 tall: the wave's body in dark blue tesserae curling over into a
# spiral, a band of the lighter blue running inside its edge, on white. D the dark blue, L the light, . the white.
WAVE = [
    "................",
    "........DDDD....",
    "......DDLLLLDD..",
    ".....DLLDDDDLLD.",
    "....DLLD....DLD.",
    "...DLLD..DD.DLD.",
    "..DLLD..DLLDLLD.",
    ".DLLDD...DLLLD..",
    "DLLDDDD....DD...",
    "DDDDDDDDDDDDDDDD",
]
WAVE_W, WAVE_H = 16, 10
SCROLL_TOP = 2              # the row the wave's band begins at, under a dark row and a gold one
SCROLL_FOOT = 13            # the last row of the scroll's border: a title's box keeps two clear of it


def _wave_cells(night: bool, lite=False) -> dict:
    """A crest of the wave scroll, with its tesserae: the white ground in two whites by turns, the dark blue body in
    two deep blues, and the light band in two lighter."""
    k = -1 if night else 0
    cells = {}
    for j, row in enumerate(WAVE):
        for i, ch in enumerate(row):
            v = (i // 2 + j * 3) % 4 if not lite else 1
            if ch == ".":
                c = PEARL[(6 if v else 5) + k]
            elif ch == "D":
                c = LAPIS[(3 if v else 2)]
            else:
                c = AZURE[(4 if v else 3) + k]
            cells[(i, j)] = c
    return cells


def scroll(p: Pix, x0, x1, night: bool, motion=False, uid="ws", centre=None):
    """The running wave scroll along a header's top from x0 to x1: a dark row, a line of gold tesserae, the wave
    curling along a white band in two blues, another gold line and a dark row; given a `centre`, a crest is centred
    on that column, so the month's mark set there covers that crest whole and the run of crests ends evenly either
    side of it. In a moving header the light runs along its crests, crest by crest, a few at a time (see
    `crest_light`)."""
    k = -1 if night else 0
    p.hline(x0, x1, 0, K)
    gold = {(i, 0): GOLD[(5, 4, 4, 3)[i] + k] for i in range(4)}
    pattern(p, f"{uid}a", 4, 1, gold, y0=1)
    lay(p, f"{uid}a", x0, 1, x1 - x0, 1)
    off = x0 + ((x1 - x0) % WAVE_W) // 2 if centre is None else x0 + (centre - WAVE_W // 2 - x0) % WAVE_W
    pattern(p, f"{uid}w", WAVE_W, WAVE_H, _wave_cells(night, p.lite), x0=off, y0=SCROLL_TOP)
    lay(p, f"{uid}w", x0, SCROLL_TOP, x1 - x0, WAVE_H)
    pattern(p, f"{uid}b", 4, 1, {(i, 0): GOLD[(3, 4, 3, 2)[i] + k] for i in range(4)}, y0=SCROLL_TOP + WAVE_H)
    lay(p, f"{uid}b", x0, SCROLL_TOP + WAVE_H, x1 - x0, 1)
    p.hline(x0, x1, SCROLL_FOOT, K)
    if motion:
        crest_light(p, x0, x1, off, night)


CREST_BEAT = 24.0           # seconds the light takes to run along the wave's crests and rest: a slow sweep


def crest_light(p: Pix, x0, x1, off, night: bool):
    """The light catching the wave scroll's crests: the crests' curl lit pale, seen through a window three crests
    wide that steps along the scroll a crest at a time, rests, and comes round again, once every `CREST_BEAT`
    seconds, as slow as the hand's sweeps."""
    cells = {}
    for j, row in enumerate(WAVE[:5]):
        for i, ch in enumerate(row):
            if ch == "L":
                cells[(i, j)] = AZURE[6] if not night else AZURE[5]
            elif ch == "D" and j <= 2:
                cells[(i, j)] = AZURE[4] if not night else AZURE[3]
    pid = pattern(p, "wsl", WAVE_W, WAVE_H, cells, x0=off, y0=SCROLL_TOP)
    first = (off - 3 * WAVE_W) / WAVE_W
    n = (x1 - off) // WAVE_W + 4
    vals = ";".join(str(i) for i in range(n)) + ";" + ";".join([str(n)] * (n // 2))
    cid = f"wc{len(p.raws)}"
    moving = (f'<clipPath id="{cid}"><rect x="{num(first)}" y="{SCROLL_TOP}" width="3" height="5" '
              f'transform="scale({WAVE_W} 1)"><animateTransform attributeName="transform" type="translate" '
              f'values="{vals}" dur="{num(CREST_BEAT)}s" calcMode="discrete" additive="sum" '
              f'repeatCount="indefinite"/></rect></clipPath><rect x="{x0}" y="{SCROLL_TOP}" width="{x1 - x0}" '
              f'height="5" fill="url(#{pid})" clip-path="url(#{cid})"/>')
    p.raw(0.5, moving, "")


# --------------------------------------------------------------------------- the title: built tile by tile
def _tile_fill(r, c, scale, night, lite=False):
    """A letter's tesserae: each font pixel a tile, its tone by its place and the letter's variant, the grout of
    the tile's right column and foot row a shade under it; at twice the font's size the tiles are too small for
    grout, and each is a tone of its own with its foot a shade deeper, by night never deeper than the gold that
    holds its contrast on the vault. Deep blue by day, gold by night."""
    fr, fc = r // scale, c // scale
    v = (fr * 7 + fc * 3) % 6 if not lite else (fr + fc) % 2
    ramp, tones, grout = (GOLD, (4, 5, 4, 3, 5, 4), GOLD[1]) if night else (LAPIS, (3, 2, 3, 4, 3, 2), LAPIS[0])
    tone = ramp[tones[v]]
    if scale >= 3:
        if r % scale == scale - 1 or c % scale == scale - 1:
            return grout
        if (r % scale, c % scale) == (0, 0) and v == 4 and fr % 2:
            return ramp[6] if night else LAPIS[4]
        return tone
    if r % scale == scale - 1 and c % scale == scale - 1:
        return ramp[max(3, tones[v] - 1) if night else tones[v] - 1]
    return tone


def _tile_pattern(p: Pix, scale: int, night: bool) -> str:
    """The tiles a title's letters are laid in, as a pattern over their grout, defined once a file for each size:
    one letter wide (five font pixels) and the face's seven rows tall, a tile at each font pixel `scale` - 1 canvas
    pixels square (at twice the font's size a tile fills its pixel but for its shaded corner), its tone from its
    place (see `_tile_fill`), drawn in the face's units as the letters are."""
    pid = f"tt{scale}{'n' if night else 'd'}"
    if ("pattern", pid) not in p.syms:
        cols: dict = {}
        for fr in range(7):
            for fc in range(5):
                for r in range(scale):
                    for c in range(scale):
                        col = _tile_fill(fr * scale + r, fc * scale + c, scale, night, p.lite)
                        grout = (GOLD[1] if night else LAPIS[0]) if scale >= 3 else None
                        if col != grout:
                            cols.setdefault(col, {}).setdefault(fr * scale + r, []).append(fc * scale + c)
        p.defs.append(f'<pattern id="{pid}" width="5" height="7" patternUnits="userSpaceOnUse"><g transform="scale('
                      f'{num(1 / scale)})">{paths(cols)}</g></pattern>')
        p.syms[("pattern", pid)] = pid
    return pid


def _dilated(p: Pix, ch: str, scale: int, d: float) -> str:
    """The symbol of a letter grown `d` canvas pixels all round, drawn once a file: its rows as strokes `d` longer at
    each end and `2d` wider, in the face's units."""
    key = ("dilate", ch, scale, d)
    if key not in p.syms:
        dd = d / scale
        parts, at = [], None
        for r, cols in enumerate(FONTS["57"][0][ch][1]):
            runs = []
            for c in sorted(cols):
                if runs and c == runs[-1][0] + runs[-1][1]:
                    runs[-1] = (runs[-1][0], runs[-1][1] + 1)
                else:
                    runs.append((c, 1))
            for (rx, rw) in runs:
                sx, sy = rx - dd, r + 0.5
                parts.append(f"M{num(sx)} {num(sy)}h{num(rw + 2 * dd)}" if at is None
                             else f"m{num(sx - at[0])} {num(sy - at[1])}h{num(rw + 2 * dd)}")
                at = (sx + rw + 2 * dd, sy)
        sid = f"q{len(p.syms)}"
        p.defs.append(f'<path id="{sid}" stroke-width="{num(1 + 2 * dd)}" d="{"".join(parts)}"/>')
        p.syms[key] = sid
    return p.syms[key]


def tesserae_title(p: Pix, x, y, s, night: bool, scale: int, motion: bool = False) -> int:
    """A title whose every letter is built from tesserae, a square tile a font pixel with visible grout between the
    tiles: deep blue on gold by day, set in a course of bright gold tiles that hugs each letter, on the even field the
    ground calms to behind words (see `calm`); by night gold glowing on the blue. In a wide moving header a glint
    runs through the letters tile by tile (see `tile_glint`). The line's letters are kept once as a group, which the
    course, the glow, the grout, the tiles and the glint each place whole. Returns the width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    w = p.measure(s, "57", scale)
    cx = x
    letters = []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(g[1]) for col in cols}, mono=True)
        letters.append((ch, cx))
        cx += (g[0] + 1) * scale
    if not letters:
        return w
    tid = f"tl{len(p.defs)}"
    move = f' transform="translate({x} {y}) scale({scale})"'

    def placed(sym) -> str:
        return "".join(f'<use href="#{sym(ch)}"' + (f' x="{num((gx - x) / scale)}"' if gx != x else "") + "/>"
                       for ch, gx in letters)
    p.defs.append(f'<g id="{tid}"{move}>{placed(lambda ch: p.syms[("glyph", "57", ch)])}</g>')
    if not night:
        under = f'<g stroke="{TILE[6]}"{move}>{placed(lambda ch: _dilated(p, ch, scale, 1))}</g>'
    else:
        under = "" if p.lite else (f'<g stroke="{GOLD[4]}" stroke-opacity=".28"{move}>'
                                   f'{placed(lambda ch: _dilated(p, ch, scale, 2))}</g>')
    if under:
        p.raw(-9, under, under)
    grout = (GOLD[1] if night else LAPIS[0]) if scale >= 3 else (GOLD[3] if night else LAPIS[2])
    body = f'<use href="#{tid}" stroke="{grout}"/><use href="#{tid}" stroke="url(#{_tile_pattern(p, scale, night)})"/>'
    p.raw(0.1, body, body)
    rows = max(len(glyphs[ch][1]) for ch, _ in letters)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    if motion and scale >= 2:
        tile_glint(p, x, y, scale, w, tid, night)
    return w


GLINT_STEP = 0.12           # the seconds a title's glint takes over each tile as it crosses the line


def tile_glint(p: Pix, x, y, scale, w, tid, night: bool):
    """The glint that runs through a title tile by tile: its letters again with each tile's face lit, the grout
    left as it lies, seen through a window a tile wide that steps along the line one tile at a time, `GLINT_STEP`
    seconds a tile, and passes once on the hand's glint, every `MEDIEVAL.glint` seconds, resting between: the window
    keeps stepping, and the glint is shown only while it makes the first of the crossings that fit in the period (a
    line too long to cross in it steps faster and takes the whole period). A title of several lines has one glint,
    its window as tall as all of them, crossing them together; each line drawn after the first lengthens it and adds
    its letters to what it lights."""
    pid = f"tg{scale}{'n' if night else 'd'}"
    if ("pattern", pid) not in p.syms:
        f = (scale - 1) / scale if scale >= 3 else 1
        lit = X["glint"] if night else AZURE[6]
        p.defs.append(f'<pattern id="{pid}" width="1" height="1" patternUnits="userSpaceOnUse">'
                      f'<rect width="{num(f)}" height="{num(f)}" fill="{lit}"/></pattern>')
        p.syms[("pattern", pid)] = pid
    g = getattr(p, "glinted", None)
    if g is None or g["scale"] != scale:
        g = p.glinted = {"at": len(p.raws), "x": x, "y": y, "w": w, "y1": y + 7 * scale, "scale": scale, "uses": []}
        p.raw(0.4, "", "")
    g["x"], g["w"] = min(g["x"], x), max(g["x"] + g["w"], x + w) - min(g["x"], x)
    g["y1"] = max(g["y1"], y + 7 * scale)
    g["uses"].append(f'<use href="#{tid}" stroke="url(#{pid})"/>')
    cid = f"gc{g['at']}"
    n = (g["w"] + 2 * scale) // scale + 1
    # the crossings that fit in the period, as many as are a whole number with a short decimal in every time written
    k = next(k for k in (50, 25, 20, 10, 5, 4, 2, 1) if MEDIEVAL.glint / k >= (n + 1) * GLINT_STEP or k == 1)
    gate = (f'<animate attributeName="opacity" values="1;0" keyTimes="0;{num(1 / k)}" dur="{num(MEDIEVAL.glint)}s" '
            f'calcMode="discrete" repeatCount="indefinite"/>' if k > 1 else "")
    gy, h = g["y"] - 1, g["y1"] - g["y"] + 2
    moving = (f'<clipPath id="{cid}"><path d="M{num(g["x"] / scale - 2)} {num(gy / scale)}h1v{num(h / scale)}h-1z" '
              f'transform="scale({scale})"><animateTransform attributeName="transform" type="translate" '
              f'values="{";".join(str(i) for i in range(n + 1))}" dur="{num(MEDIEVAL.glint / k)}s" '
              f'calcMode="discrete" additive="sum" repeatCount="indefinite"/></path></clipPath>'
              f'<g clip-path="url(#{cid})">{gate}{"".join(g["uses"])}</g>')
    z, order, _, _ = p.raws[g["at"]]
    p.raws[g["at"]] = (z, order, moving, "")


# --------------------------------------------------------------------------- light by night
GLOW = (0.1, 0.2, 0.32)          # a flame's glow in the air round it, ring by ring
POOL = (0.06, 0.12, 0.2)         # the warm pool a lamp crown throws on the gold round it


def flick(p: Pix, phase: int, back: bool = False) -> str:
    """The flickering layer a flame of `phase` burns on; a drawing made lighter lets every flame keep one time."""
    return p.flicker(0 if p.lite else phase, back=back)


def light_rings(p: Pix, cx, cy, rx, ry, col, alphas, L="haze"):
    """A stepped glow of `col` about (cx, cy): rings of it, strongest at the heart, each ring's opacity chosen so the
    stack reads as the steps `alphas`. The rings are kept once a file as a symbol a unit round and placed scaled to
    each glow. A drawing made lighter leaves out the faint outer ring."""
    if p.lite and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    key = ("rings", alphas)
    if key not in p.syms:
        sid = f"q{len(p.syms)}"
        prev, n, rings = 0.0, len(alphas), []
        for k_, a in enumerate(alphas):
            rings.append(f'<circle r="{num((n - k_) / n)}" fill-opacity="{num(1 - (1 - a) / (1 - prev))}"/>')
            prev = a
        p.defs.append(f'<g id="{sid}">{"".join(rings)}</g>')
        p.syms[key] = sid
    if L not in p.layers:
        p.layer(L)
    p.shapes[L].append(f'<use href="#{p.syms[key]}" fill="{col}" transform="translate({num(cx)} {num(cy)}) '
                       f'scale({num(rx)} {num(ry)})"/>')


def lamp(p: Pix, cx, cy, r, phase, own=(), within=None):
    """Register a flame at (cx, cy): once everything is drawn, `lamplight` lays its warm light on what stands within
    `r` of it, flickering with the flame. `own` are the flame's own pixels; `within`, columns (x0, x1), keeps its light
    inside the walls of what it hangs in."""
    p.lamps.append((cx, cy, r, phase, set(own), within))


# What a lamp's light falls on: the gold and the glass of the figures, marble, bronze, the birds and the robes; never
# the ground's own tiles, which lie under the drawing, nor the words.
LIT = (set(GOLD) | set(PEARL) | set(BRONZE) | set(TEAL) | set(AZURE) | set(GREEN) | set(PURPLE)
       | {c for skin in SKINS for c in skin} | set(EARTH) | set(RED) | set(STONE) | set(PORPHYRY))


PALE = set(PEARL) | set(STONE)


def warmed(c: str, d: float) -> str:
    """A colour `d` (0 at the flame, 1 at the edge of its reach) from a lamp, in its light: white silk and marble take
    the lamp's own warm white near it and a warm gold further off; everything else is lit a tone, or near the flame
    two, lighter on its own ramp."""
    if c in PALE:
        i = (PEARL if c in PEARL else STONE).index(c)
        return (FLAME[6] if i >= 5 else GOLD[5]) if d < 0.5 else GOLD[min(6, i + 1)]
    return step(c, 2 if d < 0.45 else 1)


def light_cells(cells: dict, lamps, own=()):
    """Lay the light of `lamps`, each (cx, cy, r) and maybe the columns (x0, x1) it keeps inside, into the colours of
    `cells` {(x, y): colour}, in place."""
    for (x, y), c in list(cells.items()):
        if c not in LIT or (x, y) in own:
            continue
        best = None
        for (cx, cy, r, *within) in lamps:
            if within and within[0] and not within[0][0] <= x < within[0][1]:
                continue
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1) / r
            if d < 1 and (best is None or d < best):
                best = d
        if best is not None:
            cells[(x, y)] = warmed(c, best)


def lamplight(p: Pix):
    """The finishing pass by night: each flame's warm light laid into the colours of what stands near it, its
    faces, its gold, its silk and its marble, strongest nearest; the words take none. What a scene drew once and
    placed twice took its light as it was drawn (see `twin`). A drawing made lighter keeps the light nearest each
    flame and leaves out the faint outer step."""
    lamps = [(cx, cy, r * (0.6 if p.lite else 1), within) for (cx, cy, r, _, _, within) in p.lamps]
    own = set().union(*(o for (_, _, _, _, o, _) in p.lamps)) if p.lamps else set()
    light_cells(p.layers["base"], lamps, own)


# A lamp crown, the bronze ring of glass lamps hung on three chains: its hook and the chains gathering to it, the
# ring seen a little from below with its cups of glass along it, each with its flame. 1 the outline, 2 3 4 5 the
# bronze dark to light, 6 the flames (which flicker), 7 the lit glass.
CROWN = [
    ".......1.......",
    "......141......",
    ".......3.......",
    "......1.1......",
    ".....3...3.....",
    "....1.....1....",
    "...3...3...3...",
    "..1....1....1..",
    ".6..6..6..6..6.",
    "17117117117117.",
    "15444444444431.",
    ".1333333333221.",
    "..11111111111..",
    "......141......",
    ".......1.......",
]
CROWN_W, CROWN_H = 15, 15


def lamp_crown(p: Pix, x, top, night: bool, phase=0, chain=0, L="base", within=None):
    """A lamp crown hung from row `top` on a chain `chain` rows long, its ring's middle at column x + 7: by day its
    bronze and glass hang cold, by night its five flames burn and flicker, a glow round each and a warm pool of its
    light thrown on the gold round it, and its light on what hangs and stands near (inside the columns `within`,
    where it hangs in an apse). Returns its box."""
    k = -1 if night else 0
    for y in range(top, top + chain):
        p.px(x + 7, y, BRONZE[3 + k], L)
    y0 = top + chain
    pal = {"1": K, "2": BRONZE[1 + k], "3": BRONZE[3 + k], "4": BRONZE[4 + k], "5": BRONZE[6 + k],
           "7": FLAME[5] if night else PEARL[4 + k]}
    own = set()
    for j, row in enumerate(CROWN):
        for i, ch in enumerate(row):
            if ch == "6":
                if night:
                    p.px(x + i, y0 + j, FLAME[6], flick(p, phase))
                    p.px(x + i, y0 + j - 1, FLAME[4], flick(p, phase))
                    own |= {(x + i, y0 + j), (x + i, y0 + j - 1)}
                continue
            c = pal.get(ch)
            if c:
                p.px(x + i, y0 + j, c, L)
                own.add((x + i, y0 + j))
    if night:
        cx, cy = x + 7.5, y0 + 9
        light_rings(p, cx, cy + 8, 20, 26, FLAME[3], POOL)
        light_rings(p, cx, cy - 1, 11, 6, FLAME[4], GLOW, L=flick(p, phase, back=True))
        lamp(p, cx, cy, 30, phase, own, within)
    return (x, top, x + CROWN_W, y0 + CROWN_H)


# --------------------------------------------------------------------------- the peacocks
# A peacock perched on the rim of the fountain, facing right, 20 wide and 22 tall: its scaled back of green glass
# tesserae edged in gold, its folded wing barred in ochre, its breast and neck of deep blue, its legs gripping the
# rim on the last row. The neck and head are drawn by pose over it (`NECK_UP`, `NECK_DOWN`), and the train hangs
# from its rump (`train`). K the outline; G g d the green; o the gold edges of the scales; R r the wing; B b n the
# blue light to dark; w the white of the face; e the eye; y the beak; c C the crest; l the legs.
PEACOCK = [
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "......KKKKK.........",
    "....KKgGogBK........",
    "..KKgGoGGogbK.......",
    ".KgGoGGoGGogbK......",
    "KgGoGGoGGoggnK......",
    "KgoRRrRRrrgdnK......",
    "KdRRrRRrrrddK.......",
    "KtdrrrrrdddK........",
    "KtTdddddKK..........",
    "KTtTtK.lKlK.........",
]
NECK_UP = [
    "...........C.C.C....",
    "...........c.c.c....",
    "............ccc.....",
    "...........KBBBK....",
    "..........KBwwBBK...",
    "..........KBeKByyK..",
    "..........KBBBBK....",
    "...........KBBK.....",
    "..........KBBnK.....",
    "..........KBbnK.....",
    ".........KBBbnK.....",
    "........KBBbbnK.....",
    "........KBbbnK......",
    "........KBbnK.......",
    "........KbnK........",
]
NECK_DOWN = [
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "............KKK.....",
    "...........KBBBKK...",
    "..........KBBbbBBK..",
    "..........KBbKKnBBK.",
    ".........KBbK..KnBK.",
    ".........KBbK...KbBK",
    ".........KBnK...KbBK",
    "..........KK....KnBK",
    "................KbBK",
    "..............KKBBBK",
    "..............KBwwBK",
    "..............KBeBBK",
    "...............KByyK",
    "................KKyK",
]
PEACOCK_W, PEACOCK_H = 20, 22


def peacock_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"K": K, "G": TEAL[4 + k], "g": TEAL[3 + k], "d": TEAL[1 + k], "o": GOLD[4 + k], "R": EARTH[4 + k],
            "r": EARTH[2 + k], "B": AZURE[3 + k], "b": AZURE[2 + k], "n": AZURE[1 + k], "w": PEARL[6 + k], "e": K,
            "y": PEARL[3 + k], "c": TEAL[1 + k], "C": TEAL[5 + k], "l": STONE[3 + k], "t": TEAL[2 + k],
            "T": TEAL[4 + k], "E": LAPIS[3], "q": AZURE[4 + k], "O": GOLD[4 + k], "u": TEAL[3 + k],
            "Q": AZURE[5 + k]}


def train_art(length: int, flare: int = 3, lite=False) -> list:
    """A peacock's train hanging from its rump, `length` rows long, facing right (it falls on the bird's left): its
    feathers lying over one another down its length, an eye at the end of each, staggered in two files, the train
    widening as it falls by `flare` columns and its edge fringed. t T the train's green, u the feather between the
    eyes, O the eye's gold ring, q its blue ring, E its heart."""
    width = 6
    rows = []
    eye = ["uOOOu", "OqqqO", "OqEqO", "uOqOu"]
    for j in range(length):
        w = width + round(flare * j / max(1, length - 1))
        lead = 0 if j < length // 3 else 1 if j < 2 * length // 3 else 2
        body = []
        for i in range(w):
            body.append("tT"[(lead + i) % 2 if not lite else 1] if i not in (0, w - 1) else "K")
        rows.append([" "] * lead + body)
    # the eyes: every five rows, in two files by turns
    for n, j in enumerate(range(1, length - 4, 5)):
        lead = rows[j].index("K")
        w = len(rows[j]) - lead
        ex = lead + (1 if n % 2 == 0 else max(1, w - 6))
        for dj, er in enumerate(eye):
            for di, ch in enumerate(er):
                if j + dj < length and ex + di < len(rows[j + dj]) - 1:
                    rows[j + dj][ex + di] = ch
    rows.append([" "] * 2 + ["K"] * (width + flare - 2))
    return ["".join(r).replace(" ", ".") for r in rows]


def peacock_train(p: Pix, x, foot, night: bool, face=1, train=26, eyes=None, L="base") -> set:
    """The train of a peacock perched with its feet on row `foot` and its art's left at x (facing right, or `face`
    -1 left), hanging `train` rows from its rump on its far side. The hearts of its eyes are given to `eyes`, a
    list, for their glint. Returns the cells it covers."""
    pal = peacock_pal(night)
    top = foot - PEACOCK_H + 1
    tr = train_art(train, lite=p.lite)
    tx = x if face == 1 else x + PEACOCK_W - len(tr[0])
    rows = [r[::-1] if face == -1 else r for r in tr]
    covered = set()
    ty = top + 18
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                p.px(tx + i, ty + j, c, L)
                covered.add((tx + i, ty + j))
                if ch == "E" and eyes is not None:
                    eyes.append((tx + i, ty + j))
    return covered


def peacock_body(p: Pix, x, foot, night: bool, face=1, L="base") -> set:
    """A peacock's body perched with its feet on row `foot`, its art's left at x (see `PEACOCK`)."""
    art = flip(PEACOCK) if face == -1 else PEACOCK
    top = foot - PEACOCK_H + 1
    stamp(p, x, top, art, peacock_pal(night), L)
    return cells_of(art, x, top)


def peacock_neck(p: Pix, x, foot, night: bool, face=1, pose="up", L="base") -> set:
    """A peacock's neck and head over its body: raised with its crest up (`pose` "up") or bent to drink ("down")."""
    art = NECK_UP if pose == "up" else NECK_DOWN
    art = flip(art) if face == -1 else art
    top = foot - PEACOCK_H + 1
    stamp(p, x, top, art, peacock_pal(night), L)
    return cells_of(art, x, top)


FAN_GLINTS = 6              # the steps the light takes crossing a fan's eyes
FAN_SWEEP = 0.5             # the share of the hand's glint the light takes to cross the fan before it rests


def eye_glints(p: Pix, eyes, night: bool, fan=None):
    """The glint in the eyes of a peacock's train in a moving header: the heart of every other eye twinkling pale as
    the light catches the feathers, on the engine's twinkle as the stars do, a third of them in each of its phases.
    Across a fan open about its rump at `fan`, the light passes over the eyes in turn on the hand's glint, once every
    `MEDIEVAL.glint` seconds as a title's glint passes: from the ground up over the fan and down its far side in the
    first `FAN_SWEEP` of it, each eye's heart and the blue round it catching it as it passes, then resting. A drawing
    made lighter lets every other eye's glint go, and twinkles the rest together."""
    if fan:
        fx, fy = fan
        swept = sorted(eyes, key=lambda q: math.atan2(q[1] - fy, q[0] - fx))[::2 if p.lite else 1]
        for i, (x, y) in enumerate(swept):
            g = i * FAN_GLINTS // len(swept)
            L = p.seq(f"fg{g}", round(g / FAN_GLINTS * FAN_SWEEP, 3), round((g + 1.4) / FAN_GLINTS * FAN_SWEEP, 3),
                      MEDIEVAL.glint, keep=False, z=0.5)
            p.px(x, y, PEARL[6] if not night else AZURE[6], L)
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                p.px(x + dx, y + dy, AZURE[6] if not night else AZURE[5], L)
        return
    for i, (x, y) in enumerate(sorted(eyes, key=lambda q: (q[1], q[0]))[::4 if p.lite else 2]):
        L = p.twinkle(0 if p.lite else i)
        p.px(x, y, AZURE[6] if not night else AZURE[5], L)
        p.px(x, y - 1, AZURE[5] if not night else AZURE[4], L)


# --------------------------------------------------------------------------- the fountain
# The fountain's basin, 28 wide, seen a little from above: its far rim of gold, the water in it, the near rim lit,
# and the bowl of white marble fluted under it down to its knob. K the outline; Y G g the gold light to dark; w the
# light on the water, B b the water; P p W d the marble light, shade, glint and dark.
BASIN = [
    "....KKKKKKKKKKKKKKKKKKKK....",
    "..KKYGGGGGGGGGGGGGGGGGGgKK..",
    ".KgwbbBBBBbbbBBBBBbbbBBBwgK.",
    "KgbBBBBbbbbBBBBBbbbbBBBBBbgK",
    "KGYYYYYYYYYYYYYYYYYYYYYYYYgK",
    ".KGgggggggggggggggggggggggK.",
    "..KPpPWPPpPPPpPPPpPPPpPPdK..",
    "...KPpWPPpPPPpPPPpPPpPdK....",
    ".....KKPpWPPpPPpPPpPdK......",
    ".......KKPpPPpPPpPdK........",
    "........KKKYGGGGgKKK........",
]
BASIN_W = 28
WATER_ROW = 2               # the basin's row the water's surface lies on
STEM = "KPWPPpdK"          # a row of the fluted shaft, 8 wide
FOOT = [
    "KKYGGGGgKK",
    "KYGGGGGGgK",
    "KPPWPPPPdK",
    "KPPPPPPPdK",
    "KKKKKKKKKK",
]
# The jet's water falling back into the basin either side, as (across, down) from the jet's head, in the order a
# drop passes them.
FALL = ((1, -1), (2, -1), (3, 0), (4, 0), (5, 1), (6, 2), (7, 3), (7, 5), (8, 6), (8, 8))
JET_BEAT = 1.2


def fountain_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"K": K, "Y": GOLD[5 + k], "G": GOLD[4 + k], "g": GOLD[2 + k], "w": PEARL[6 + k], "B": AZURE[3 + k],
            "b": AZURE[2 + k], "P": PEARL[5 + k], "p": PEARL[3 + k], "W": PEARL[6 + k], "d": PEARL[2 + k]}


def fountain(p: Pix, cx, rim, foot, night: bool, motion=True, jet=12, L="base") -> tuple:
    """The fountain: a basin of white marble with a rim of gold and the water in it, on a fluted shaft standing on its
    foot on row `foot`, its middle at column cx and its water's surface on row `rim`; out of the water a jet rises `jet`
    rows and falls back into the basin either side, its drops sparkling as they fall in a moving header (`JET_BEAT`).
    Returns the basin's left and its top."""
    pal = fountain_pal(night)
    k = -1 if night else 0
    bx, by = cx - BASIN_W // 2, rim - WATER_ROW
    stamp(p, bx, by, BASIN, pal, L)
    sx = cx - 4
    shaft = {(i, j): (pal["P"] if ch == "W" and j == 3 else pal[ch]) for i, ch in enumerate(STEM) for j in range(4)}
    pid = pattern(p, f"sh{'n' if night else 'd'}", 8, 4, shaft, x0=sx)
    lay(p, pid, sx, by + len(BASIN), 8, foot - len(FOOT) + 1 - by - len(BASIN), L)
    stamp(p, cx - 5, foot - len(FOOT) + 1, FOOT, pal, L)
    # the jet: a column of water two tiles wide, lit along its left, a crown of spray at its head
    head = rim - jet
    for y in range(head + 1, rim):
        p.px(cx - 1, y, AZURE[6] if not night else AZURE[5], L)
        p.px(cx, y, AZURE[4 + k], L)
    for (dx, dy) in ((-1, 0), (0, 0), (-2, 1), (1, 1), (-1, -1)):
        p.px(cx + dx, head + dy, PEARL[6 + k] if dy <= 0 else AZURE[5 + k], L)
    frames = 3 if motion else 1
    for f in range(frames):
        Lf = p.seq(f"jet{f}", f / frames, (f + 1) / frames, JET_BEAT, keep=f == 0, z=0.3) if motion else L
        for n, (dx, dy) in enumerate(FALL):
            if n % 3 != f or head + dy > rim:
                continue
            for side in (-1, 1):
                x = cx - 1 + side * dx if side < 0 else cx + dx
                p.px(x, head + dy, PEARL[6 + k] if n < 5 else AZURE[5 + k], Lf)
    if night:
        p.px(cx, head, FLAME[6], L)
    return bx, by


# --------------------------------------------------------------------------- the vine
# A vine leaf, 7 by 7, five-lobed and lit on its upper left, its stalk at its foot: L l the leaf light and dark, v its
# veins, s the stalk, K the outline. A cluster of grapes, 7 by 9, round grapes heaped to a point, each lit at its
# upper left: P p the grape and its shade, w its light, s the stalk. And a small leaf, 5 by 5, for a tendril's end.
LEAF = ["..K.K..", ".KLKLK.", "KLLlLlK", "KLLvllK", ".KLvlK.", "..KvK..", "...s..."]
LEAF_SMALL = [".KK.K", "KLlKl", "KLLvK", ".KlvK", "..KK."]
GRAPES = ["...s...", "..Ks...", ".KwPwK.", "KPpwPpK", "KwPpwPK", ".KpwPK.", ".KwPpK.", "..KpK..", "...K..."]


def vine_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"K": K, "L": GREEN[4 + k], "l": GREEN[3 + k], "v": GREEN[2 + k], "P": PURPLE[4 + k],
            "p": PURPLE[2 + k], "w": PURPLE[6 + k], "s": EARTH[3 + k]}


def spiral(cx, cy, r0, turns, start, sense=1, steps=90) -> list:
    """Points along a spiral about (cx, cy) closing in from radius r0 over `turns` turns, beginning at angle
    `start` (degrees, 0 the right, 90 down) and turning clockwise with `sense` 1, or anticlockwise with -1."""
    out = []
    for i in range(steps + 1):
        t = i / steps
        a = math.radians(start + sense * 360 * turns * t)
        r = r0 * (1 - 0.78 * t)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def stem(p: Pix, pts, night: bool, L="base", width=2) -> list:
    """A vine's stem along the points `pts`: a tile of the vine's brown along it, and where it is thick a darker
    tile under it or at its right, in shade. Returns its cells in order along it."""
    k = -1 if night else 0
    cells, seen = [], set()
    for (x, y) in pts:
        q = (math.floor(x), math.floor(y))
        if q not in seen:
            seen.add(q)
            cells.append(q)
    out = []
    for i, (x, y) in enumerate(cells):
        nx, ny = cells[min(len(cells) - 1, i + 1)]
        p.px(x, y, GREEN[3 + k], L)
        out.append((x, y))
        if width > 1:
            q = (x, y + 1) if abs(nx - x) >= abs(ny - y) else (x + 1, y)
            if q not in seen:
                p.px(*q, K, L)
                out.append(q)
    return out


def vine_half(q: Pix, cx, root, top, scx, scy, sr, night: bool) -> list:
    """The left half of the apse's vine, drawn on the twin's scratch sheet: its stem rising from the ground at
    `root` beside the fountain's shaft, behind the basin and the bird, up into the conch, and curling there into a
    scroll about (scx, scy) of radius `sr`, with a tendril curling off its rise. Returns where the leaves and the
    grapes hang along it: (x, y, what)."""
    x0, y0 = root
    s0 = math.radians(90)
    ex, ey = scx + sr * math.cos(s0), scy + sr * math.sin(s0)
    rise = []
    n = max(2, int(abs(y0 - ey)))
    for i in range(n + 1):
        t = i / n
        rise.append((x0 + (ex - x0) * t + math.sin(t * math.pi * 1.5) * 2.5, y0 + (ey - y0) * t))
    curl = spiral(scx, scy, sr, 1.2, 90, sense=1)
    stem(q, rise + curl, night)
    tx, ty = rise[int(0.62 * n)]
    tendril = spiral(tx + 4, ty - 3, 3.2, 0.9, 180, sense=1, steps=30)
    stem(q, tendril, night, width=1)
    hangs = []
    hx, hy = curl[-1]
    hangs.append((round(hx) - 3, round(hy) - 3, "leaf"))
    for t in (0.18, 0.5):
        px_, py_ = curl[int(t * (len(curl) - 1))]
        hangs.append((round(px_) - 3, round(py_) - (6 if t < 0.3 else 2), "leaf" if t > 0.3 else "grapes"))
    gx, gy = curl[int(0.36 * (len(curl) - 1))]
    hangs.append((round(gx) - 3, round(gy) + 1, "grapes"))
    for t in (0.3, 0.78):
        px_, py_ = rise[int(t * n)]
        hangs.append((round(px_) - 6, round(py_) - 3, "small"))
    gx, gy = rise[int(0.45 * n)]
    hangs.append((round(gx) + 1, round(gy) - 1, "grapes"))
    return hangs


# --------------------------------------------------------------------------- the apse
ARCH = 4                    # the arch's band: a dark row and three of blue graded toward the gold inside


def _rows_path(cells) -> str:
    rows: dict = {}
    for (x, y) in cells:
        rows.setdefault(y, []).append(x)
    return _blocks(rows)


def _night_gold(lite=False) -> dict:
    """A tile of the apse's gold by night, 24 by 8: two courses of tiles in the deep golds of gold in shadow, its
    grout darker still, which the lamps' pools light where they reach."""
    rnd = random.Random(5)
    cells = {}
    for row in range(2):
        x = rnd.randrange(3)
        while x < 24 + 3:
            tw = rnd.choice((3, 3, 4))
            tone = rnd.choice((GOLD[1], GOLD[1], GOLD[2], BRONZE[2])) if not lite else GOLD[1]
            for yy in range(row * 4, row * 4 + 3):
                for xx in range(x, x + tw):
                    cells[(xx % 24, yy)] = tone
                cells[((x + tw) % 24, yy)] = GOLD[0]
            for xx in range(x, x + tw + 1):
                cells[(xx % 24, row * 4 + 3)] = GOLD[0]
            x += tw + 1
    return cells


def _niche_cells(x0, x1, top, foot) -> tuple:
    """The niche's band, each cell's depth into it and its run along it, and the cells inside the band."""
    r = (x1 - x0) / 2
    cx, cy = x0 + r, top + r
    inside, band = set(), {}
    for y in range(top, foot + 1):
        for x in range(x0, x1):
            px_, py_ = x + 0.5, y + 0.5
            if py_ < cy:
                d = r - math.hypot(px_ - cx, py_ - cy)
                along = math.degrees(math.atan2(py_ - cy, px_ - cx)) * r / 57.3
            else:
                d = min(px_ - x0, x1 - px_)
                along = y
            if d < 0:
                continue
            if d < ARCH:
                band[(x, y)] = (int(d), int(along // 4) % 2)
            else:
                inside.add((x, y))
    return band, inside


def niche_band(p: Pix, x0, x1, top, foot, night: bool, half=None, L="base"):
    """The band round the apse's niche from x0 to x1, its arch's crown on row `top` and its walls down to row `foot`:
    tesserae graded from deep lapis outside to pale blue inside, laid in short runs of two tones, with a capital of
    gold where the arch springs from the wall; only its left half up to column `half` when given."""
    k = -1 if night else 0
    band, _ = _niche_cells(x0, x1, top, foot)
    tones = ((K, K), (LAPIS[3], LAPIS[3]), (AZURE[3 + k], AZURE[2 + k]), (AZURE[5 + k], AZURE[5 + k]))
    for (x, y), (d, alt) in band.items():
        if half is None or x < half:
            p.px(x, y, tones[d][alt], L)
    cy = int(top + (x1 - x0) / 2)
    for side in (0, 1) if half is None else (0,):
        sx = x0 + 1 if side == 0 else x1 - 7
        for i in range(6):
            p.px(sx + i, cy, GOLD[5 + k] if i < 5 else GOLD[2 + k], L)
            p.px(sx + i, cy + 1, GOLD[3 + k] if i < 5 else GOLD[1], L)
        p.hline(sx, sx + 6, cy + 2, K, L)


def niche_inside(p: Pix, x0, x1, top, foot, night: bool):
    """The gold inside the apse's niche: by day a shade deeper than the ground and in shadow under the arch; by night
    the apse's own gold in shadow, lit only where a lamp's pool reaches it."""
    _, inside = _niche_cells(x0, x1, top, foot)
    r = (x1 - x0) / 2
    cx, cy = x0 + r, top + r
    if not night:
        p.under.append(f'<path fill="{TILE[1]}" fill-opacity=".2" d="{_rows_path(inside)}"/>')
        underside = {(x, y) for (x, y) in inside if y + 0.5 < cy + 2 and
                  r - ARCH - math.hypot(x + 0.5 - cx, y + 0.5 - cy) < 3}
        p.under.append(f'<path fill="{X["shade_ink"]}" fill-opacity=".12" d="{_rows_path(underside)}"/>')
    else:
        pid = pattern(p, "apn", 24, 8, _night_gold(p.lite))
        p.under.append(f'<path fill="url(#{pid})" d="{_rows_path(inside)}"/>')
    return inside


def meadow(p: Pix, x0, x1, top, foot, night: bool, L="base"):
    """The green ground the apse's figures stand on, from x0 to x1 and rows top to foot: tesserae of green in two
    tones with a lighter row along its top, and small flowers of red and white tiles in it here and there."""
    k = -1 if night else 0
    for y in range(top, foot + 1):
        for x in range(x0, x1):
            c = GREEN[4 + k] if y == top else GREEN[2 + k] if y == foot else GREEN[3 + k]
            if top < y < foot and (x * 5 + y * 3) % 11 == 0:
                c = GREEN[2 + k]
            p.px(x, y, c, L)
    rnd = random.Random(x0 * 7 + top)
    for x in range(x0 + 2, x1 - 2, 5):
        x += rnd.randrange(3)
        if x < x1 - 1:
            p.px(x, top + 1, (RED[4 + k], PEARL[6 + k])[x % 2], L)


TURN = 6.0                  # seconds the peacocks take turns to drink, round and round: one of the hand's idles


def apse(p: Pix, x0, x1, top, foot, night: bool, motion=True) -> tuple:
    """The apse, the H1's showpiece, from x0 to x1 and from row `top` to the ground on row `foot`: under the niche's
    arch the fountain on its marble shaft, a peacock perched on each end of its basin, one bent to drink while the other
    holds its crested head up, their trains hanging down either side with their eyes; the vine rising from the ground
    beside the shaft, behind the basin and the birds into the conch, and curling there into a scroll either side of the
    lamp crown hung from the arch's crown, with its leaves and its clusters of grapes. By day the lamp hangs cold; by
    night it burns, its light pooled on the gold of the conch and laid on the birds, the vine and the marble. In a
    moving header the birds take turns to drink, the fountain's water sparkles as it falls and the eyes of their trains
    glint. What is the same either side of the fountain is drawn once and placed twice, turned. Returns the span it
    covers."""
    w = (x1 - x0) // 2 * 2
    x1 = x0 + w
    cx = x0 + w // 2
    r = w / 2
    cy = top + r
    # the basin's water a little under the arch's spring where the rows allow, the shaft standing on the ground
    # under it; where they are few, the basin at the spring so the birds' heads stay under the arch
    rim = min(foot - 18, max(int(cy) + 4, min(foot - 38, int(cy) + 20)))
    bx = cx - BASIN_W // 2
    foot_bird = rim + 2
    lx = bx - 8
    length = max(12, foot - 6 - (foot_bird - 3))
    sr = max(5, round(r / 3.2))
    eyes: list = []

    def back(q):
        niche_band(q, x0, x1, top, foot, night, half=cx)
        meadow(q, x0 + ARCH, cx, foot - 3, foot, night)
        for (hx, hy, what) in vine_half(q, cx, (cx - 7, foot - 4), top, cx - round(r / 2.2), round(cy - r / 3.6),
                                        sr, night):
            stamp(q, hx, hy, {"leaf": LEAF, "grapes": GRAPES, "small": LEAF_SMALL}[what], vine_pal(night))
    niche_inside(p, x0, x1, top, foot, night)
    crown = [(cx + 0.5, top + ARCH + 11, 30)]
    twin(p, "apse", back, cx, z=-0.5, lamps=crown)
    twin(p, "train", lambda q: peacock_train(q, lx, foot_bird, night, 1, length, eyes), cx, z=-0.4, lamps=crown)
    for (ex, ey) in list(eyes):
        eyes.append((2 * cx - 1 - ex, ey))
    hung = top + ARCH + 2 + CROWN_H          # the lamp crown's foot: the jet stays two rows under it
    fountain(p, cx, rim, foot - 3, night, motion=motion, jet=max(4, min(13, rim - int(cy) + 2, rim - hung - 2)))
    twin(p, "bird", lambda q: peacock_body(q, lx, foot_bird, night, 1), cx, z=0.1, lamps=crown)
    rx = 2 * cx - lx - PEACOCK_W
    peacock_neck(p, lx, foot_bird, night, 1, "down", p.layer("necks", z=0.2))
    poses = ("up", "down") if motion else ("up",)
    for f, pose in enumerate(poses):
        L = p.seq(f"turn{f}", f / len(poses), (f + 1) / len(poses), TURN, keep=f == 0, z=0.2) if motion else \
            p.layer("necks", z=0.2)
        peacock_neck(p, rx, foot_bird, night, -1, pose, L)
    if motion:
        eye_glints(p, eyes, night)
    lamp_crown(p, cx - 7, top + ARCH, night, phase=1, chain=2, within=(x0, x1))
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the empress's court
# The figures of the court, frontal as the mosaic sets them, 11 wide, with the large dark eyes of the mosaic's faces,
# their whites showing and their brows dark over them. K the outline; Y n y the gold light to dark of a crown, a
# collar or a hem; r g the jewels in them; p the pearls; h the hair; b the brows; f F the face, W the whites of the
# eyes and e their darks, m the mouth; Q q L the robe and its shade and its light (its colour given by the figure),
# s z the gold of its pattern and the stone at the heart of each figure of it; W w the white of a cloak; V v a veil;
# k the shoes; t T the purple panel on a courtier's cloak.
COURT = {
    # the empress as the mosaic shows her: her crown of gold set with jewels and topped with pearls, the strings of
    # pearls falling from it beside her face to her shoulders, the broad collar of gold and jewels over her
    # shoulders, her cloak of purple falling in its folds to its hem embroidered in gold, and a bowl of gold in her
    # hands, red shoes
    "empress": [
        ".p.p.p.p.p.",
        ".YKYKYKYKY.",
        "KYrYgYrYgYK",
        "pKYYYYYYYKp",
        "pKhhhhhhhKp",
        "pKfbbFbbfKp",
        "pKfWeFeWfKp",
        "pKfFFfFFfKp",
        "p.KfFmFfK.p",
        "p..KKfKK..p",
        "KKYnYnYnYKK",
        "KYrYgYrYgYK",
        "KYgYrYrYrYK",
        "KnYYYYYYYnK",
        "KQLnnnnnLqK",
        "KQLQQQQQLqK",
        "KQLfYYYfLqK",
        "KQLKyYyKLqK",
        "KQLQKKKQLqK",
        "KQLQQQQQLqK",
        "KQLQQqQQLqK",
        "KQLQQqQQLqK",
        "KQLQQqQQLqK",
        "KQLQQqQQLqK",
        "KYYYYYYYYYK",
        "KrYgYrYgYrK",
        "KYnYnYnYnYK",
        "KnnnnnnnnnK",
        ".KKKKKKKKK.",
        "..KkK.KkK..",
    ],
    # a lady of the court: her veil over her hair, a collar of gold and jewels, her robe of silk patterned all over
    # in figures of gold, each with its stone
    "lady": [
        "...KKKKK...",
        "..KVVVVVK..",
        ".KVVhhhVVK.",
        ".KVbbFbbVK.",
        ".KVWeFeWVK.",
        ".KVfFfFfVK.",
        ".KvKfmfKvK.",
        ".KvKKfKKvK.",
        "..KYnYnYK..",
        ".KYrYgYrYK.",
        "KQYnnnnnYQK",
        "KQQsQQQsQQK",
        "KQszsQszsQK",
        "KQQsQQQsQQK",
        "KqQQQQQQQqK",
        "KqQQsQsQQqK",
        "KqQszsQszqK",
        "KqQQsQsQQqK",
        "KqQQQQQQQqK",
        "KqsQQQQQsqK",
        "KqzsQQQszqK",
        "KqsQQQQQsqK",
        "KqQQQQQQQqK",
        ".KqQQsQQqK.",
        ".KqQszsQqK.",
        ".KqQQsQQqK.",
        ".KYYYYYYYK.",
        ".KyYyYyYyK.",
        ".KKKKKKKKK.",
        "..KkK.KkK..",
    ],
    # a courtier: his short hair and beard, his white cloak pinned at his right shoulder with a gold brooch and
    # the panel of purple on its front, his white tunic under it
    "courtier": [
        "...KKKKK...",
        "..KhhhhhK..",
        "..KbbFbbK..",
        "..KWeFeWK..",
        "..KfFfFfK..",
        "..KhfmfhK..",
        "...KhhhK...",
        "...KKfKK...",
        ".KKWWWWWKK.",
        "KWWWWWWnWwK",
        "KWWWWWWWWwK",
        "KWWTTTWWWwK",
        "KWWTtTWWWwK",
        "KWWTTTWWWwK",
        "KWWWWWWWWwK",
        "KwWWWfWWWwK",
        "KwWWWWWWWwK",
        "KwWWWWWWwwK",
        "KwWWWWWWwwK",
        "KwWWWWWWwwK",
        "KwWWWWWWwwK",
        ".KwWWWWWwK.",
        ".KwWWWWWwK.",
        ".KwWWWWWwK.",
        ".KwWWWWWwK.",
        ".KQQQQQQQK.",
        ".KQqQqQqQK.",
        ".KKKKKKKKK.",
        "..KkK.KkK..",
    ],
}
FIGURE_W = 11


# The stone at the heart of each figure of gold on a silk, by the silk's colour.
STONE_ON = {"purple": "gold", "pearl": "red", "green": "red", "red": "pearl", "azure": "gold", "porphyry": "gold",
            "teal": "red"}


def court_pal(night: bool, robe="purple", veil="pearl", tint=0, skin=0) -> dict:
    """A figure's colours: its robe and its veil from their ramps, the stone set in the figures of its silk, and the
    gold, the jewels and the white of the court's dress; its face on the hand's skin `skin` (0 the lightest, 2 the
    darkest), the face in the skin's own tone and its contour, as the mosaic models a face, a row of the skin's
    deeper tone; a little dimmer by night. `tint` lifts the face a tone, for a figure turned to a lamp."""
    k = -1 if night else 0
    R, V, S = RAMP[robe], RAMP[veil], SKINS[skin]
    pale = robe == "pearl"
    return {"K": K, "Y": GOLD[5 + k], "n": GOLD[3 + k], "y": GOLD[2 + k], "r": RED[4 + k], "g": GREEN[4 + k],
            "h": EARTH[1], "b": EARTH[1], "f": S[2 + k + tint], "F": S[3 + k + tint], "e": X["outline"],
            "m": RED[3 + k], "p": PEARL[6 + k], "Q": R[5 + k] if pale else R[3 + k],
            "q": R[3 + k] if pale else R[2 + k], "L": R[6 + k] if pale else R[4 + k], "W": PEARL[6 + k],
            "w": PEARL[4 + k], "s": GOLD[4 + k], "z": RAMP[STONE_ON.get(robe, "red")][4 + k],
            "V": V[5 + k] if veil == "pearl" else V[4 + k], "v": V[3 + k] if veil == "pearl" else V[2 + k],
            "k": RED[2 + k], "T": PURPLE[3 + k], "t": PURPLE[2 + k]}


ROBE = {"empress": 20, "lady": 18, "courtier": 17}     # a row of the robe that lengthens as a figure stands taller


def court_art(kind: str, tall: int = 0, lite=False) -> list:
    """A figure's art (see `COURT`), its robe lengthened by `tall` rows, the way the mosaic draws its figures tall.
    Drawn lighter, a silk keeps its colour and its folds and lets the small figures of its pattern go."""
    art = COURT[kind]
    i = ROBE[kind]
    art = art[:i] + [art[i]] * tall + art[i:]
    return [row.replace("s", "Q").replace("z", "Q") for row in art] if lite else art


def figure(p: Pix, kind: str, x, foot, night: bool, robe="purple", veil="pearl", L="base", face=1, tall=0,
           tint=0, skin=0) -> set:
    """A figure of the court standing with its feet on row `foot` and its left at column x (see `COURT`), its robe
    lengthened by `tall` rows and its face on the hand's skin `skin`."""
    art = court_art(kind, tall, p.lite)
    art = art if face == 1 else flip(art)
    top = foot - len(art) + 1
    stamp(p, x, top, art, court_pal(night, robe, veil, tint, skin), L)
    return cells_of(art, x, top)


# --------------------------------------------------------------------------- the palace
# A curtain drawn back to the column at the left of an arch and tied there, as rows from the arch's spring down: each
# row the columns it covers from the column's face. W w the white silk and its folds, b its border of blue and gold,
# Y the gold cord it is tied with.
CURTAIN = [
    "WWwWwb",
    "WwWwb.",
    "WwWwb.",
    "Wwwb..",
    "Wwwb..",
    "Wwb...",
    "Wwb...",
    "Wwb...",
    "Wb....",
    "YY....",
    "Wb....",
    "Wwb...",
    "Wwb...",
    "WwWb..",
    "WwWb..",
    "WwWwb.",
]
COLUMN = 3                  # a column's width: its lit face, its shade and its dark edge
BAY = 15                    # from one column's left to the next


def palace_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"W": PEARL[6 + k], "w": PEARL[4 + k], "b": AZURE[3 + k], "Y": GOLD[5 + k], "K": K}


def palace_half(q: Pix, x0, w, top, foot, night: bool, roof=True, bay=BAY) -> dict:
    """The left half of the palace's front, drawn on the twin's scratch sheet, from x0 across w (an odd number of bays
    `bay` wide, its middle the twin's axis) and from row `top` to the floor on row `foot`: its columns of white marble
    with gold capitals and bases, the arches between them edged in gold, the spandrels over them in gold tesserae, the
    curtains of white silk drawn back to the columns and tied there with gold cords; over the arcade a frieze of gold
    set with garnets, the wings' roofs of red tiles and the pediment over the middle bay, gold with a jewel in it.
    Returns where the arcade's arches spring and the bays' middles."""
    k = -1 if night else 0
    cx = x0 + w // 2
    cols = [x0 + i * bay for i in range(w // bay + 1)]
    ped = top
    frieze = top + (12 if roof else 0)
    arch_top = frieze + 4
    spring = arch_top + 8
    floor = foot - 2
    # the pediment and the roofs of the wings
    if roof:
        for j in range(11):
            y = ped + j
            half = 2 + j * 2
            for x in range(cx - half, cx):
                edge = x == cx - half
                c = K if edge or j == 10 else GOLD[(4, 4, 5, 3)[(x + j) % 4] + k]
                q.px(x, y, c)
        for x in range(cx - 2, cx):
            for y in range(ped + 5, ped + 8):
                q.px(x, y, RED[(4, 3)[(x + y) % 2] + k] if y < ped + 7 else RED[2 + k])
        q.px(cx - 2, ped + 4, K)
        for y in range(ped + 6, frieze):
            for x in range(x0, cx - (2 + (y - ped) * 2) if y < ped + 11 else cx):
                c = K if y == ped + 6 else RED[(3, 2)[((x - x0) // 2 + y) % 2 if not q.lite else 0] + k] \
                    if (y - ped) % 2 else RED[4 + k]
                q.px(x, y, c)
    # the frieze, gold set with garnets
    for x in range(x0, cx):
        q.px(x, frieze, K)
        q.px(x, frieze + 1, GOLD[5 + k] if (x - x0) % 6 not in (2, 3) else RED[4 + k])
        q.px(x, frieze + 2, GOLD[3 + k] if (x - x0) % 6 not in (2, 3) else RED[2 + k])
        q.px(x, frieze + 3, K)
    # the spandrels and the arches
    for a, b in zip(cols, cols[1:]):
        if a >= cx:
            break
        acx = (a + COLUMN + b) / 2
        r = (b - a - COLUMN) / 2
        for y in range(arch_top, spring):
            for x in range(a + COLUMN, min(b, cx)):
                d = math.hypot(x + 0.5 - acx, (y + 0.5 - spring) * 1.0)
                if d >= r + 0.6:
                    q.px(x, y, GOLD[(4, 3)[(x // 2 + y) % 2 if not q.lite else 0] + k])
                elif d >= r - 0.6:
                    q.px(x, y, K)
                elif d >= r - 1.6:
                    q.px(x, y, GOLD[6 + k] if y < spring - 2 else GOLD[5 + k])
    # the columns
    for cxp in cols:
        if cxp >= cx:
            break
        for y in range(arch_top, floor):
            for i, c in enumerate((PEARL[6 + k], PEARL[4 + k], K)):
                q.px(cxp + i, y, c)
        for i in range(-1, COLUMN + 1):
            q.px(cxp + i, spring, GOLD[5 + k])
            q.px(cxp + i, spring + 1, GOLD[3 + k])
            q.px(cxp + i, floor - 1, GOLD[4 + k])
            q.px(cxp + i, floor, K)
    # the curtains drawn back to the columns and tied, both sides of every bay
    pal = palace_pal(night)
    tie = spring + 2 + max(0, (floor - spring - 2 - len(CURTAIN)) // 3)
    for a, b in zip(cols, cols[1:]):
        if a >= cx:
            break
        for side in (1, -1):
            edge = a + COLUMN if side == 1 else b - 1
            for j in range(floor - spring - 2):
                y = spring + 2 + j
                if y < tie:
                    row = CURTAIN[min(j, 8)]
                elif y == tie:
                    row = CURTAIN[9]
                else:
                    row = CURTAIN[min(15, 10 + (y - tie - 1) * 6 // max(1, floor - tie - 2))]
                for i, ch in enumerate(row):
                    xx = edge + i * side
                    if ch != "." and xx < cx:
                        q.px(xx, y, pal["W" if q.lite and ch == "w" else ch])
    # the floor
    for x in range(x0, cx):
        q.px(x, floor + 1, GREEN[4 + k])
        q.px(x, floor + 2, GREEN[2 + k])
    return {"cols": cols, "spring": spring, "arch_top": arch_top, "floor": floor, "tie": tie}


def palace(p: Pix, x0, w, top, foot, night: bool, motion=True, roof=True, bay=BAY) -> tuple:
    """The palace, the H1's second showpiece, from x0 across `w` (an odd number of bays, each `bay` wide, BAY where the
    words leave the room and a column narrower where they leave less) and from row `top` to its floor on row `foot`: its
    arcade with its curtains drawn back and tied to the columns, and in its arches the empress's court, the empress in
    the middle in her crown and her pearls, her jewelled collar and her purple, holding her bowl of gold, and her
    ladies either side in their veils and their patterned silks (see `COURT`); over them the frieze, the roofs and the
    pediment. By day the gold ground shows in its arches; by night the gold behind them lies in shadow, and a lamp
    hangs lit in each arch, high over the head under it, its light on the faces under it. What is the same either side
    of its middle is drawn once and placed twice, turned. Returns the span it covers."""
    cx = x0 + w // 2
    info: dict = {}

    def half(q):
        info.update(palace_half(q, x0, w, top, foot, night, roof=roof, bay=bay))
    probe = Pix(p.w, p.h)
    info.update(palace_half(probe, x0, w, top, foot, night, roof=roof, bay=bay))
    cols, spring, floor = info["cols"], info["spring"], info["floor"]
    bays = [(a + COLUMN + b) // 2 for a, b in zip(cols, cols[1:])]
    room = floor - 1 - (spring + 12)
    heads = [floor - len(COURT["lady"]) - max(0, min(12, room - len(COURT["lady"]))) for _ in bays]
    hung = [max(info["arch_top"] + 3, hd - LAMP_DROP) for hd in heads]
    twin(p, "palace", half, cx, z=-0.3, lamps=[(bx + 2.5, at + 1, 22) for bx, at in zip(bays, hung)])
    if night:
        inside = set()
        for a, b in zip(cols, cols[1:]):
            acx, r = (a + COLUMN + b) / 2, (b - a - COLUMN) / 2
            for y in range(info["arch_top"], floor):
                for x in range(a + COLUMN, b):
                    if y >= spring or math.hypot(x + 0.5 - acx, y + 0.5 - spring) < r - 1.6:
                        inside.add((x, y))
        p.under.append(f'<path fill="url(#{pattern(p, "apn", 24, 8, _night_gold(p.lite))})" d="{_rows_path(inside)}"/>')
    kinds = [("lady", "pearl", "red", 1), ("empress", "purple", "pearl", 0), ("lady", "green", "pearl", 2)]
    n = len(bays)
    order = [kinds[0]] * max(0, n // 2 - 1) + kinds + [kinds[2]] * max(0, n // 2 - 1) if n >= 3 else [kinds[1]]
    room = floor - 1 - (spring + 12)
    for i, (bx, (kind, robe, veil, skin)) in enumerate(zip(bays, order)):
        tall = max(0, min(12, room - len(COURT[kind])))
        figure(p, kind, bx - FIGURE_W // 2, floor - 1, night, robe=robe, veil=veil, face=1 if bx <= cx else -1,
               tall=tall, skin=skin)
        head = floor - len(COURT[kind]) - tall
        hanging_lamp(p, bx, info["arch_top"] + 1, max(info["arch_top"] + 3, head - LAMP_DROP), night, phase=i,
                     within=(x0, x0 + w))
    return (x0 - 1, x0 + w + 1)


# The fountain before the palace's door, 11 wide and 14 tall: its jet rising out of the basin and falling back into it
# either side, the basin of marble with its rim of gold and the water in it, on a fluted shaft and a foot of gold.
# w B b the water light to dark; Y G g the gold; P p W d the marble light, shade, glint and dark.
FOUNT = [
    ".....w.....",
    "....wBw....",
    "...b.B.b...",
    "..b..B..b..",
    ".KKKKKKKKK.",
    "KgwbBBBBbgK",
    "KGYYYYYYYgK",
    ".KPPWPPPdK.",
    "..KPWPPdK..",
    "...KKPKK...",
    "....KWdK...",
    "....KPdK...",
    "...KYGGgK..",
    "..KKKKKKKK.",
]
DOOR_W = 15                 # the doorway's width: a column, its opening and the palace's own first column


def doorway(p: Pix, x0, top, foot, night: bool, roof=True):
    """The door of the palace that the court comes to, at the palace's left from column x0, as tall as its arcade
    (from row `top`, the palace's top, to its floor on row `foot`): a column of white marble with its gold capital and
    base, the arch of gold over the door with its frieze set with garnets, the dark of the hall beyond, and the
    curtain of white silk drawn aside, gathered against the column and tied there with a cord of gold; and on the
    floor before it the small fountain of marble, its jet falling back into its basin."""
    k = -1 if night else 0
    frieze = top + (12 if roof else 0)
    arch_top, floor = frieze + 4, foot - 2
    spring = arch_top + 8
    a, b = x0, x0 + DOOR_W - COLUMN          # the door's own column, and the palace's first one beyond it
    acx, r = (a + COLUMN + b) / 2, (b - a - COLUMN) / 2
    for x in range(a, b):
        p.px(x, frieze, K)
        p.px(x, frieze + 1, GOLD[5 + k] if (x - a) % 6 not in (2, 3) else RED[4 + k])
        p.px(x, frieze + 2, GOLD[3 + k] if (x - a) % 6 not in (2, 3) else RED[2 + k])
        p.px(x, frieze + 3, K)
    for y in range(arch_top, floor):
        for x in range(a + COLUMN, b):
            d = math.hypot(x + 0.5 - acx, y + 0.5 - spring) if y < spring else r - 2
            if d >= r + 0.6:
                p.px(x, y, GOLD[(4, 3)[(x // 2 + y) % 2 if not p.lite else 0] + k])
            elif d >= r - 0.6:
                p.px(x, y, K)
            elif d >= r - 1.6:
                p.px(x, y, GOLD[6 + k] if y < spring - 2 else GOLD[5 + k])
            else:
                p.px(x, y, EARTH[0] if not night else K)
    for y in range(arch_top, floor):
        for i, c in enumerate((PEARL[6 + k], PEARL[4 + k], K)):
            p.px(a + i, y, c)
    for i in range(-1, COLUMN + 1):
        p.px(a + i, spring, GOLD[5 + k])
        p.px(a + i, spring + 1, GOLD[3 + k])
        p.px(a + i, floor - 1, GOLD[4 + k])
        p.px(a + i, floor, K)
    for x in range(a - 1, b):
        p.px(x, floor + 1, GREEN[4 + k])
        p.px(x, floor + 2, GREEN[2 + k])
    # the curtain drawn aside to the column and tied there
    pal = palace_pal(night)
    tie = spring + 2 + max(0, (floor - spring - 2 - len(CURTAIN)) // 2)
    for j in range(floor - spring - 2):
        y = spring + 2 + j
        row = CURTAIN[min(j, 8)] if y < tie else CURTAIN[9] if y == tie else \
            CURTAIN[min(15, 10 + (y - tie - 1) * 6 // max(1, floor - tie - 2))]
        for i, ch in enumerate(row):
            if ch != ".":
                p.px(a + COLUMN + i, y, pal["W" if p.lite and ch == "w" else ch])
    # the fountain before it
    fx = int(acx) - len(FOUNT[0]) // 2
    stamp(p, fx, floor - len(FOUNT), FOUNT, {"K": K, "w": PEARL[6 + k], "B": AZURE[4 + k], "b": AZURE[3 + k],
                                             "g": GOLD[2 + k], "Y": GOLD[5 + k], "G": GOLD[4 + k], "P": PEARL[5 + k],
                                             "p": PEARL[3 + k], "W": PEARL[6 + k], "d": PEARL[2 + k]})
    keep(p, {(x, y) for x in range(a - 1, b) for y in range(frieze, floor + 3)})


# A small oil lamp of bronze hung on its chains: the chains from its ring, its bowl lit on its left with its nozzle,
# and the drop under it. 1 the outline, 2 3 4 5 the bronze dark to light; the flame stands on its nozzle. In the
# palace it hangs in its arch, or on a longer chain where the bay is tall, its bowl LAMP_DROP rows over the head
# under it, so a clear stretch of the gold lies between them.
OIL = ["..1.1..", "...1...", ".14551.", "1544331", ".13321.", "..121..", "...1..."]
LAMP_DROP = 15


def hanging_lamp(p: Pix, x, top, at, night: bool, phase=0, L="base", within=None, reach=22):
    """A small lamp of bronze hung from row `top` on its chain, its bowl at row `at`: cold by day; by night its flame
    burning on its nozzle with a glow round it, a small warm pool of its light on the gold behind it, and its light on
    the faces, the gold and the silk under and beside it as far as `reach`, inside the columns `within` (the palace
    it hangs in)."""
    k = -1 if night else 0
    for y in range(top, at):
        p.px(x, y, BRONZE[3 + k], L)
    pal = {"1": K, "2": BRONZE[2 + k], "3": BRONZE[3 + k], "4": BRONZE[4 + k], "5": BRONZE[6 + k]}
    stamp(p, x - 3, at, OIL, pal, L)
    if night:
        Lf = flick(p, phase)
        p.px(x + 2, at + 1, FLAME[6], Lf)
        p.px(x + 2, at, FLAME[5], Lf)
        p.px(x + 3, at - 1, FLAME[4], Lf)
        light_rings(p, x + 2.5, at + 0.5, 5, 5, FLAME[4], GLOW, L=flick(p, phase, back=True))
        light_rings(p, x + 0.5, at + 4, 8, 10, FLAME[3], POOL)
        lamp(p, x + 2.5, at + 1, reach, phase, {(x + 2, at + 1), (x + 2, at), (x + 3, at - 1)}, within)


# --------------------------------------------------------------------------- the procession
# The court in procession toward the palace, figure by figure from it outward: who walks, their robe, their veil and
# the hand's skin they are laid in. The courtiers are alike, so each is the one figure placed again.
PROCESSION = (("courtier", "pearl", "pearl", 1), ("lady", "red", "pearl", 0), ("courtier", "pearl", "pearl", 1),
              ("lady", "azure", "gold", 2), ("courtier", "pearl", "pearl", 1), ("lady", "pearl", "green", 1),
              ("courtier", "pearl", "pearl", 1), ("lady", "green", "red", 0))
STEP = 13                   # from one figure of the procession to the next


def procession(p: Pix, x0, x1, foot, night: bool, room: int) -> tuple:
    """The jewelled procession of the empress's court on the green ground from x0 to x1, its feet on row `foot`:
    courtiers in white cloaks with their panels of purple and ladies in their veils and robes of every colour, each
    with a jewelled collar, standing in a row from the palace's door outward, as tall as the `room` the words leave
    over them allows. A figure that walks more than once is drawn once a file and placed again each time. Returns the
    span it covers, or None where not one figure fits."""
    n = (x1 - x0 - 2) // STEP
    if n < 1:
        return None
    k = -1 if night else 0
    tall = max(0, min(10, room - 4 - len(COURT["empress"])))
    for x in range(x1 - n * STEP - 2, x1):
        p.px(x, foot + 1, GREEN[4 + k])
        p.px(x, foot + 2, GREEN[2 + k])
    walking = [PROCESSION[i % len(PROCESSION)] for i in range(n)]
    for i, (kind, robe, veil, skin) in enumerate(walking):
        x = x1 - (i + 1) * STEP + 1
        if walking.count((kind, robe, veil, skin)) > 1:
            art = court_art(kind, tall, p.lite)
            p.sprite(x, foot - len(art) + 1, art, court_pal(night, robe, veil, skin=skin), reuse=True)
        else:
            figure(p, kind, x, foot, night, robe=robe, veil=veil, tall=tall, skin=skin)
    return (x1 - n * STEP - 3, x1 + 1)


# --------------------------------------------------------------------------- the vine along a rule
SCROLL_P = 24               # a period of the running vine along a rule
SCROLL_R = 9                # the rows it rises over the rule


def _running_vine(night: bool) -> dict:
    """A period of the running vine scroll along a rule, 24 wide and 9 rows tall: its stem waving along, curling once
    above and once below, a leaf on the one curl and a cluster of grapes hung from the other, laid in tesserae."""
    k = -1 if night else 0
    pal = vine_pal(night)
    cells = {}
    for i in range(SCROLL_P * 4):
        t = i / (SCROLL_P * 4)
        x = t * SCROLL_P
        y = 4.5 + 2.6 * math.sin(2 * math.pi * t)
        cells[(int(x) % SCROLL_P, int(y))] = GREEN[3 + k]
        cells[(int(x) % SCROLL_P, int(y) + 1)] = K
    for (cx, cy, sense) in ((6, 3.2, 1), (18, 5.8, -1)):
        for i in range(24):
            a = math.radians(-90 * sense + 300 * i / 24 * sense)
            r = 2.2 * (1 - 0.5 * i / 24)
            cells[(int(cx + r * math.cos(a)) % SCROLL_P, int(cy + r * math.sin(a)))] = GREEN[3 + k]
    for (art, x, y) in ((LEAF_SMALL, 3, 0), (GRAPES, 15, 0)):
        for j, row in enumerate(art):
            for i, ch in enumerate(row):
                if pal.get(ch) and 0 <= y + j < SCROLL_R:
                    cells[((x + i) % SCROLL_P, y + j)] = pal[ch]
    return {q: c for q, c in cells.items() if 0 <= q[1] < SCROLL_R}


def running_vine(p: Pix, x0, x1, y, night: bool, L="base"):
    """The vine scroll running along a rule at row y where no scene stands: laid as a pattern only where no word lies
    within two units, each run a whole number of periods long and set in from its ends."""
    ok = [p.clear_of_words(x - 2, y - SCROLL_R - 2, x + 3, y + 1) for x in range(x0, x1)]
    runs, start = [], None
    for i, good in enumerate(ok + [False]):
        if good and start is None:
            start = i
        elif not good and start is not None:
            a = -(-(x0 + start + 1) // SCROLL_P) * SCROLL_P
            b = ((x0 + i - 1) // SCROLL_P) * SCROLL_P
            if b - a >= SCROLL_P:
                runs.append((a, b))
            start = None
    if not runs:
        return
    pid = pattern(p, f"rv{'n' if night else 'd'}{y}", SCROLL_P, SCROLL_R, _running_vine(night), y0=y - SCROLL_R)
    for a, b in runs:
        lay(p, pid, a, y - SCROLL_R, b - a, SCROLL_R, L)


def clear_stars(p: Pix, x0, y0, x1, y1):
    """Take up the vault's stars and the ground's glitter from the box a scene stands in."""
    for name, layer in p.layers.items():
        if name.startswith(("tb", "gl", "st")):
            for xy in [xy for xy in layer if x0 <= xy[0] < x1 and y0 <= xy[1] < y1]:
                del layer[xy]
            p.uses[name] = [u for u in p.uses[name] if not (x0 - 7 < u[2] < x1 and y0 - 7 < u[3] < y1)]


# --------------------------------------------------------------------------- the peacock with its tail half open
# A peacock standing on the ground facing left, 30 wide and 34 tall: its crest, its small head with the white of its
# face, its long neck and breast of deep blue, its back in scales of green edged in gold, its wing barred in ochre,
# its grey legs. Letters as for the perched birds (`PEACOCK`). Its rump, where the fan springs, is `RUMP` from its
# art's top-left.
DISPLAY = [
    "......C.C.C...................",
    "......c.c.c...................",
    ".......ccc....................",
    "......KKKKK...................",
    ".....KBwwBBK..................",
    "...KKBwKeBBK..................",
    "..KyyBBBBBBK..................",
    "...KKKBBBBnK..................",
    "......KBBBnK..................",
    "......KBBbnK..................",
    "......KBBbnK..................",
    ".......KBbnK..................",
    ".......KBbnK..................",
    ".......KBbnK..................",
    "......KBBbnnK.................",
    "......KBBbnnK.................",
    ".....KBBBbnnK.................",
    ".....KBBbbnnKK................",
    "....KBBBbbnngGKKK.............",
    "....KBBbbnngGGgggKKK..........",
    "....KBBbbnngGoGGoGggKKK.......",
    "....KBbbnnggGGoGGoGGgggKKK....",
    "....KBbbnngGoGGoGGoGGoggggK...",
    "....KbbnnggRRrRRrRRrRRgggddK..",
    ".....KbnngRRrRRrRRrRRrrgddK...",
    ".....KbnnggrrrrrrrrrrrrddK....",
    "......KnngddddddddddddddK.....",
    ".......KKKddddddddddKKK.......",
    "..........KKKKKKKKKK..........",
    "...........KlK..KlK...........",
    "...........KlK..KlK...........",
    "...........KlK..KlK...........",
    "..........KllK.KllK...........",
    ".........KlKlKKlKlK...........",
]
RUMP = (25, 23)
# The peacock of a section's header, the same bird drawn larger to stand in front of its fan, 38 wide and 44 tall,
# facing left: the fan of its crest, three feathers on bare shafts each tipped with its spoon of green and blue; its
# head with the white over and under its eye; its neck of deep blue with the light running down its front (Q q); its
# breast, its back in scales of green edged in gold, its wing barred in ochre and its long grey legs. Its rump, where
# the fan springs, is `SHOWING_RUMP` from its art's top-left.
SHOWING = [
    "..........CC..........................",
    "......CC..qq..CC......................",
    "......qq.c..c.qq......................",
    "........c.cc.c........................",
    ".........cccc.........................",
    "..........cc..........................",
    ".........KKKKK........................",
    "........KBwwwBK.......................",
    ".......KBBKeKBBK......................",
    ".....KKBBwwwBBBK......................",
    "...KyyKBBBBBBBqK......................",
    ".....KKKBBBBBBqK......................",
    "........KBBBBqnK......................",
    "........KBBBQqnK......................",
    ".........KBBQqnK......................",
    ".........KBBQqnK......................",
    ".........KBBQqnnK.....................",
    ".........KBBBQqnK.....................",
    "........KBBBBQqnK.....................",
    "........KBBBBQqnnK....................",
    ".......KBBBBBQqnnK....................",
    ".......KBBBBBBQqnnKK..................",
    "......KBBBBBBBQqnnngKKK...............",
    "......KBBBBBBBQqnngGGoGKKK............",
    ".....KBBBBBBBBQqnngGoGGoGGgKK.........",
    ".....KBBBBBBBBQqnngGGoGGoGGoggKK......",
    ".....KBBBBBBBQqnnggGoGGoGGoGGoggKK....",
    ".....KBBBBBBBQqnngRRrRRrRRrRRrRggdK...",
    ".....KBBBBBBQqnngRRrRRrRRrRRrRRrgddK..",
    "......KBBBBBQqnngRRrRRrRRrRRrRRgddK...",
    "......KBBBBQqnngrrrrrrrrrrrrrrrgddK...",
    ".......KBBBQqnggrrrrrrrrrrrrrrdddK....",
    ".......KBBQqnngddddddddddddddddK......",
    "........KBqnngdddddddddddddddKK.......",
    ".........KnngddddddddddddKKK..........",
    "..........KKKKdddddddddKK.............",
    ".............KKKKKKKKKK...............",
    "..............KlK...KlK...............",
    "..............KlK...KlK...............",
    "..............KlK...KlK...............",
    "..............KlK...KlK...............",
    "..............KlK...KlK...............",
    ".............KllK..KllK...............",
    "............KlKlK.KlKlK...............",
]
SHOWING_RUMP = (32, 27)
# An eye of the fan, 7 by 7: its gold ring, its turquoise, its blue and its dark heart.
TAIL_EYE = ["..ooo..", ".oOOOo.", "oOqqqOo", "oOqEqOo", "oOqqqOo", ".oOOOo.", "..ooo.."]
FAN = (-84, 6)              # the fan's span, in degrees from the right, upward negative: half open


def fan_cells(fx, fy, R, a0=FAN[0], a1=FAN[1]) -> dict:
    """The fan of a peacock's tail half open about its rump at (fx, fy), R long: each cell's band (0 near the rump
    to 2 at the rim) or -1 for the dark rim, its feathers' tips scalloping the edge."""
    out = {}
    for y in range(math.floor(fy - R) - 2, math.ceil(fy + R) + 2):
        for x in range(math.floor(fx - R) - 2, math.ceil(fx + R) + 2):
            dx, dy = x + 0.5 - fx, y + 0.5 - fy
            r = math.hypot(dx, dy)
            a = math.degrees(math.atan2(dy, dx))
            if not (a0 <= a <= a1) or r < 3:
                continue
            edge = R - 2.4 * abs(math.sin(math.radians((a - a0) * 11.25)))
            if r > edge + 1:
                continue
            out[(x, y)] = -1 if r > edge else (0 if r < 0.45 * edge else 1 if r < 0.78 * edge else 2)
    return out


def display_peacock(p: Pix, x, foot, night: bool, motion=True, R=40, eyes=None) -> set:
    """A peacock standing on the ground at row `foot`, its art's left at x, facing left, its tail half open behind it
    in a fan R long springing from its rump: the fan laid in bands of the train's greens darkening toward the rump,
    the shafts of its longest feathers in gold, rows of eyes along it staggered feather by feather, and its tips
    scalloping its rim; the bird in front of it. The eyes' hearts are given to `eyes`, a list, for their glint.
    Returns the cells it covers."""
    k = -1 if night else 0
    top = foot - len(SHOWING) + 1
    fx, fy = x + SHOWING_RUMP[0], top + SHOWING_RUMP[1]
    cells = fan_cells(fx, fy, R)
    tones = {-1: K, 0: TEAL[1 + k], 1: TEAL[2 + k], 2: TEAL[3 + k]}
    rows: dict = {}
    for (cx_, cy_), band in cells.items():
        rows.setdefault(tones[band], {}).setdefault(cy_, []).append(cx_)
    L = p.layer("fan", z=-0.2)
    p.shapes[L].append("".join(f'<path fill="{c}" d="{_blocks(r)}"/>' for c, r in rows.items()))
    keep(p, set(cells))
    for a in range(FAN[0] + 4, FAN[1], 8):
        for i in range(round(R * 0.3), round(R * 0.95)):
            q = (math.floor(fx + i * math.cos(math.radians(a))), math.floor(fy + i * math.sin(math.radians(a))))
            if cells.get(q, -1) >= 0:
                p.px(*q, GOLD[2 + k] if i < R * 0.6 else GOLD[3 + k], L)
    pal = {"o": GOLD[2 + k], "O": GOLD[4 + k], "q": AZURE[4 + k], "E": LAPIS[2]}
    for n, (frac, off) in enumerate(((0.5, 0), (0.7, 4), (0.89, 0))):
        rr = R * frac
        step_ = 8 if frac > 0.6 else 12
        for a in range(FAN[0] + 2 + off, FAN[1] - 1, step_):
            ex = math.floor(fx + rr * math.cos(math.radians(a))) - 3
            ey = math.floor(fy + rr * math.sin(math.radians(a))) - 3
            if all(cells.get((ex + i, ey + j), -1) >= 0 for j in range(7) for i in range(7)
                   if TAIL_EYE[j][i] != "."):
                p.sprite(ex, ey, TAIL_EYE, pal, L="eyes", reuse=True)
                keep(p, cells_of(TAIL_EYE, ex, ey))
                if eyes is not None:
                    eyes.append((ex + 3, ey + 3))
    p.layer("eyes", z=-0.15)
    stamp(p, x, top, SHOWING, peacock_pal(night))
    return set(cells) | cells_of(SHOWING, x, top)


# --------------------------------------------------------------------------- the port
# The lighthouse on its mole, 13 wide and 32 tall: the basket its fire burns in, the lantern stage of gold, three
# stages of white stone narrowing as they rise with their windows and the door at its foot. K the outline; Y F W
# the fire (by night) or its cold fuel; g G the gold; P p the stone and its shade; k the door.
LIGHTHOUSE = [
    "......Y......",
    ".....YFY.....",
    "....YFWFY....",
    "....KFFFK....",
    "...KKKKKKK...",
    "...KgGGGgK...",
    "...KG.K.GK...",
    "...KgGGGgK...",
    "..KKKKKKKKK..",
    "...KPPPPpK...",
    "...KPKPPpK...",
    "...KPKPPpK...",
    "...KPPPPpK...",
    "...KPPPPpK...",
    "..KKKKKKKKK..",
    "..KPPPPPPpK..",
    "..KPPKPPPpK..",
    "..KPPKPPPpK..",
    "..KPPPPPPpK..",
    "..KPPPPPPpK..",
    "..KPPPPPPpK..",
    "..KPPKPPPpK..",
    "..KPPKPPPpK..",
    "..KPPPPPPpK..",
    ".KKKKKKKKKKK.",
    ".KPPPPPPPPpK.",
    ".KPPPPPPPPpK.",
    ".KPPPKKPPPpK.",
    ".KPPKkkKPPpK.",
    ".KPPKkkKPPpK.",
    ".KPPKkkKPPpK.",
    "KKKKKKKKKKKKK",
]
# A merchant ship under sail, 22 wide and 14 tall: its yard and its sail striped red on white and bellied by the
# wind, its mast, its stem and stern posts curling up, its hull of planks. W the sail, r its stripes, d D the hull.
SHIP = [
    "..........K...........",
    "......KKKKKKKKK.......",
    "......KWWrWWrWK.......",
    "......KWWrWWrWK.......",
    "......KWWrWWrWK.......",
    ".......KWrWWrK........",
    "........KKKKK.........",
    "..........K...........",
    "K.........K..........K",
    "dK........K.........Kd",
    ".dKKKKKKKKKKKKKKKKKKd.",
    "..KdDDdDDdDDdDDdDDdK..",
    "...KdddddddddddddddK..",
    "....KKKKKKKKKKKKKKK...",
]
# A tower of the city's walls, 9 wide, crenellated, with its window: S s the stone, K the outline.
TOWER = ["K.K.K.K.K", "KKKKKKKKK", "KSSSSSSsK", "KSSKKSSsK", "KSSKKSSsK", "KSSSSSSsK"]
# The city's gate, 11 wide and 15 tall, at the end of its walls: a tower over an archway edged in gold, its doors
# open on the dark of the street. o the dark under the arch, Y y its gold edge.
GATE = [
    "K.K.K.K.K.K",
    "KKKKKKKKKKK",
    "KSSSSSSSSsK",
    "KSSSKKKSSsK",
    "KSSSKKKSSsK",
    "KSSSSSSSSsK",
    "KSSKYYYKSsK",
    "KSKYyooyYsK",
    "KSKYooooYsK",
    "KSKYooooYsK",
    "KSKYooooYsK",
    "KSKYooooYsK",
    "KSKYooooYsK",
    "KSKYooooYsK",
    "KKKKKKKKKKK",
]


def port_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"K": K, "Y": FLAME[5] if night else STONE[2], "F": FLAME[3] if night else STONE[1],
            "W": FLAME[6] if night else STONE[3], "g": GOLD[2 + k], "G": GOLD[4 + k], "P": PEARL[6 + k],
            "p": PEARL[3 + k], "k": EARTH[1], "r": RED[3 + k], "d": EARTH[2 + k], "D": EARTH[4 + k],
            "S": EARTH[5 + k], "s": EARTH[3 + k]}


def _water(night: bool) -> dict:
    """A tile of the harbour's water, 16 by 6: courses of blue tesserae with the white of a crest here and there."""
    k = -1 if night else 0
    cells = {}
    for y in range(6):
        for x in range(16):
            c = AZURE[(3, 2, 3, 2, 2, 1)[y] + k]
            if (y == 1 and x in (2, 3, 4)) or (y == 4 and x in (10, 11, 12)):
                c = PEARL[6 + k] if night is False else AZURE[4]
            elif (y == 2 and x in (1, 5)) or (y == 5 and x in (9, 13)):
                c = AZURE[4 + k]
            cells[(x, y)] = c
    return cells


# The buildings of the city behind its walls, left to right: what each is, its width and the rows its body rises over
# the walls at the most, before its roof.
SKYLINE = (("tower", 7, 22), ("house", 11, 12), ("dome", 17, 14), ("house", 9, 17), ("hall", 15, 11),
           ("house", 11, 15), ("tower", 7, 19), ("house", 9, 10), ("hall", 13, 13), ("house", 11, 18))


def _building(p: Pix, kind, x, w, h, foot, night: bool, walls: dict):
    """One of the city's buildings, its left at column x, `w` wide, its body `h` rows tall standing on row `foot`:
    a house of ochre stone under a gabled roof of red tiles, a tower with its battlements, a hall of white marble with
    an arcade along its front under a low gable, or the great hall, its drum and its gold dome on top. Its windows are
    dark by day, and some of them lit by night. The face of its wall between its lit edge and its shaded one is
    gathered into `walls`, by colour, to be laid in one block with every other's (see `skyline`)."""
    k = -1 if night else 0
    marble = kind in ("hall", "dome")
    body = (PEARL[5 + k], PEARL[3 + k], PEARL[6 + k]) if marble else (EARTH[5 + k], EARTH[3 + k], EARTH[6 + k])
    top = foot - h + 1
    p.vline(x, top, foot + 1, K)
    p.vline(x + w - 1, top, foot + 1, K)
    p.vline(x + 1, top, foot + 1, body[2])
    p.vline(x + w - 2, top, foot + 1, body[1])
    walls.setdefault(body[0], set()).update((xx, y) for y in range(top + 1, foot + 1) for xx in range(x + 2, x + w - 2))
    p.hline(x, x + w, top, K)
    lit = FLAME[4] if night else None
    n = 0
    if kind in ("hall", "dome"):
        # an arcade along its foot: dark arches with gold heads
        for ax in range(x + 2, x + w - 3, 4):
            p.px(ax, foot - 4, GOLD[4 + k])
            p.px(ax + 1, foot - 4, GOLD[4 + k])
            for y in range(foot - 3, foot + 1):
                p.px(ax, y, K)
                p.px(ax + 1, y, EARTH[1])
        rows = range(top + 2, foot - 6, 4)
    else:
        rows = range(top + 3, foot - 1, 4)
    for wy in rows:
        for wx in range(x + 2, x + w - 3, 3):
            n += 1
            c = lit if lit and n % 3 == 1 else EARTH[1]
            p.px(wx + (1 if kind == "tower" else 0), wy, c)
            p.px(wx + (1 if kind == "tower" else 0), wy + 1, c)
    if kind == "tower":
        for xx in range(x, x + w, 2):
            p.px(xx, top - 1, K)
        p.hline(x, x + w, top, K)
    elif kind == "dome":
        cx = x + w // 2
        p.hline(x - 1, x + w + 1, top - 1, GOLD[3 + k])
        for j in range(3):
            p.hline(cx - 4, cx + 5, top - 2 - j, PEARL[5 + k] if j else K)
            p.px(cx - 4, top - 2 - j, K)
            p.px(cx + 4, top - 2 - j, K)
        r = 5
        for j in range(r + 1):
            half = round(math.sqrt(max(0, r * r - (r - j - 0.5) ** 2)))
            y = top - 5 - r + j
            for xx in range(cx - half, cx + half + 1):
                edge = xx in (cx - half, cx + half) or j == 0
                p.px(xx, y, K if edge else GOLD[(6 if xx < cx - 1 and j < 3 else 5 if xx < cx else 3) + k])
        p.px(cx, top - 5 - r - 1, GOLD[5 + k])
        p.px(cx, top - 5 - r - 2, K)
    else:
        roof = (w + 1) // 2 - 1 if kind == "house" else 3
        for j in range(roof):
            y = top - 1 - j
            half = (w // 2) - (j if kind == "house" else j * 2)
            for xx in range(x + w // 2 - half, x + w // 2 + half + (w % 2)):
                edge = xx in (x + w // 2 - half, x + w // 2 + half + (w % 2) - 1)
                p.px(xx, y, K if edge else RED[(4, 3)[j % 2] + k])
        p.px(x + w // 2, top - 1 - roof, K)


def skyline(p: Pix, x0, x1, foot, night: bool, room) -> None:
    """The city's buildings rising behind its walls from x0 to x1, their feet on row `foot` just over the walls' top:
    towers, houses under red roofs, halls of marble with their arcades and the great hall under its gold dome, each
    with its roof as tall as `room(xa, xb)` (the rows the words leave over it) allows, and left out where that leaves
    its body fewer than seven rows. The faces of their walls are laid as a block of each colour under the rest of the
    drawing, their windows and their arcades over them."""
    x = x0
    walls: dict = {}
    for kind, w, h in SKYLINE * 3:
        if x + w > x1:
            break
        extra = 12 if kind == "dome" else (w + 1) // 2 if kind == "house" else 4
        hh = min(h, room(x - 1, x + w + 1) - extra)
        if hh >= 7:
            _building(p, kind, x, w, hh, foot, night, walls)
        x += w + 1
    for colour, cells in walls.items():
        p.shapes["base"].append(f'<path fill="{colour}" d="{_rows_path(cells)}"/>')
        keep(p, cells)


def port(p: Pix, x0, x1, top, foot, night: bool, motion=True, mouth="right", room=None) -> tuple:
    """The port, from x0 to x1 and from row `top` to the water's foot on row `foot`: the harbour's water in courses of
    blue with its crests, the city's walls along its far shore with their crenellated towers and the red roofs and a
    dome rising behind them, merchant ships under sail on the water, and the lighthouse on its mole at the harbour's
    mouth, at its right (an H2's port, beside the peacock) or at its left (`mouth` "left", an H1's, beside the apse),
    the walls then running on to the city's gate at its right, where the court sets out in procession; and given
    `room(xa, xb)`, the rows the words leave over the city, its buildings rising behind the walls as tall as that allows
    (see `skyline`), in place of the roofs and the dome. By day its fire basket stands cold; by night its fire burns,
    flickering, with a glow round it and a path of its light across the water. Returns the span it covers."""
    k = -1 if night else 0
    pal = port_pal(night)
    water = foot - 10
    pid = pattern(p, f"wt{'n' if night else 'd'}", 16, 6, _water(night), y0=water)
    lay(p, pid, x0, water, x1 - x0, foot - water + 1)
    p.hline(x0, x1, water - 1, K)
    # the city behind its walls
    wall = water - 9
    if mouth == "right":
        lx = x1 - 15
        c0, c1 = x0, lx - 2
    else:
        lx = x0 + 2
        c0, c1 = lx + 17, x1 - (len(GATE[0]) + 1)
    if room is not None:
        skyline(p, c0 + 3, c1 - 2, wall - 1, night, room)
    # the walls: their dark coping, two courses of ochre blocks in two tones laid as a pattern, and the stone under
    p.hline(c0, c1, wall, K)
    courses = pattern(p, f"wc{'n' if night else 'd'}{(wall + 1) % 2}", 6, 2,
                      {(i, j): EARTH[(5, 4)[(i // 3 + wall + 1 + j) % 2] + k] for i in range(6) for j in range(2)},
                      x0=c0, y0=wall + 1)
    lay(p, courses, c0, wall + 1, c1 - c0, 2)
    for y in range(wall + 3, water - 1):
        p.hline(c0, c1, y, EARTH[4 + k])
    for x in range(c0, c1, 2):
        p.px(x, wall - 1, K)
    for i, tx in enumerate(range(c0 + 2, c1 - 10, 24)):
        stamp(p, tx, wall - len(TOWER) + 1, TOWER, pal)
        for y in range(wall + 1, water - 1):
            p.hline(tx + 1, tx + 8, y, EARTH[5 + k])
            p.px(tx, y, K)
            p.px(tx + 8, y, K)
        # the roofs and a dome behind the walls
        rx = tx + 12
        if rx + 9 < c1 - 1 and room is None:
            for j in range(4):
                p.hline(rx + 3 - j, rx + 6 + j, wall - 5 + j, RED[(4, 3)[j % 2] + k])
            p.hline(rx - 1, rx + 10, wall - 1, K)
        if i == 0 and tx + 22 < c1 - 4 and room is None:
            dx = tx + 14
            for j in range(6):
                half = (0, 2, 3, 4, 4, 4)[j]
                for xx in range(dx - half, dx + half + 1):
                    p.px(xx, wall - 12 + j, GOLD[(5 if xx < dx else 3) + k] if j else K)
            p.px(dx, wall - 13, GOLD[6 + k])
    if mouth != "right":
        stamp(p, c1, water - len(GATE) - 1, GATE, dict(pal, o=EARTH[1], Y=GOLD[5 + k], y=GOLD[3 + k]))
    # the ships
    ships = range(x0 + 4, lx - 26, 34) if mouth == "right" else range(lx + 18, c1 - 18, 34)
    for i, sx in enumerate(ships):
        stamp(p, sx, water - 9 + (i % 2) * 3, SHIP, pal)
    # the lighthouse on its mole of grey stones set in a chequer, laid as a pattern of four tiles
    stamp(p, lx, water - len(LIGHTHOUSE) + 3, LIGHTHOUSE, pal)
    p.hline(lx - 2, lx + 15, water + 2, K)
    mole = pattern(p, f"ml{'n' if night else 'd'}", 2, 2, {(0, 0): STONE[3 + k], (1, 1): STONE[3 + k],
                                                           (1, 0): STONE[2 + k], (0, 1): STONE[2 + k]})
    lay(p, mole, lx - 2, water + 3, 17, foot - water - 2)
    fy = water - len(LIGHTHOUSE) + 3
    if night:
        Lf = flick(p, 2)
        for (dx, dy) in ((6, 0), (5, 1), (7, 1), (6, 1), (6, 2)):
            p.px(lx + dx, fy + dy, FLAME[6] if dy == 1 and dx == 6 else FLAME[5], Lf)
        light_rings(p, lx + 6.5, fy + 2, 14, 12, FLAME[4], GLOW, L=flick(p, 2, back=True))
        # the fire's path across the water, widening as it comes: glints on every other tile of every other course,
        # bright near the mole and paler further out, laid as one pattern over the rows the path takes
        rows = range(water + 1, foot, 2)
        glints = pattern(p, "lp", 2, 2 * len(rows), {(0, 2 * j): FLAME[4] if j < 2 else FLAME[3]
                                                     for j in range(len(rows))}, x0=lx + 3, y0=water + 1)
        d = "".join(f"M{lx + 3 - j} {y}h{7 + 2 * j}v1h-{7 + 2 * j}z" for j, y in enumerate(rows))
        p.shapes[Lf].append(f'<path fill="url(#{glints})" d="{d}"/>')
        lamp(p, lx + 6.5, fy + 2, 26, 2, set())
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- the marks
# A gold star of tesserae, the mark after SECTION A-A: eight-pointed, 7 by 7, a bright heart and its points.
STAR = ["...Y...", ".Y.Y.Y.", "..yWy..", "YYWWWYY", "..yWy..", ".Y.Y.Y.", "...Y..."]


def star_mark(p: Pix, x, y, night: bool, L="base"):
    """A single gold tessera star, eight-pointed, its top-left at (x, y): by day set round with dark tesserae so it
    stands off the gold ground, by night shining on the lapis."""
    k = -1 if night else 0
    if not night:
        cells = cells_of(STAR, x, y)
        for (cx_, cy_) in cells:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (cx_ + dx, cy_ + dy) not in cells:
                    p.px(cx_ + dx, cy_ + dy, LAPIS[2], L)
    stamp(p, x, y, STAR, {"Y": GOLD[4 + k] if night else GOLD[5], "y": GOLD[3 + k], "W": GOLD[6]}, L)


# --------------------------------------------------------------------------- the doves at the fountain
# A dove perched, facing right, 12 by 9: its small head with its dark eye and its beak, its white body shaded under
# its folded wing barred in grey, its red feet. And the same dove bent to drink. W w the white and its shade, g the
# wing's bars, e the eye, y the beak, r the feet.
DOVE = [
    "......KKKK..",
    ".....KWWWWK.",
    "....KWWWeWKy",
    "KK..KWWWWWK.",
    "KWKKWWWWWK..",
    "KwWWWgWgWK..",
    ".KwwWgWgwK..",
    "..KKwwwwK...",
    "....KrKrK...",
]
DOVE_DRINK = [
    "............",
    "............",
    "............",
    "KK.KKKK.....",
    "KWKKWWWKKK..",
    "KwWWgWgWWWK.",
    ".KwWgWgWWeWK",
    "..KKwwwwKWyK",
    "....KrKrK.K.",
]


def dove(p: Pix, x, foot, night: bool, face=1, drink=False, L="base") -> set:
    """A dove with its feet on row `foot`, its art's left at x, facing right (or `face` -1 left), its head up or
    bent to drink."""
    k = -1 if night else 0
    art = DOVE_DRINK if drink else DOVE
    art = art if face == 1 else flip(art)
    top = foot - len(art) + 1
    stamp(p, x, top, art, {"K": K, "W": PEARL[6 + k], "w": PEARL[4 + k], "g": STONE[4 + k], "e": K,
                           "y": RED[4 + k], "r": RED[3 + k]}, L)
    return cells_of(art, x, top)


def basin_fountain(p: Pix, cx, foot, night: bool, motion=True, stem_h=10, jet=7) -> tuple:
    """The fountain the doves drink at: the basin on a short fluted shaft standing on row `foot`, its middle at
    column cx, a low jet in it falling either side, and a dove on each end of its rim, the left one bent to drink and
    the right one with its head up. Returns the box it covers."""
    rim = foot - len(FOOT) - stem_h - len(BASIN) + WATER_ROW + 1
    fountain(p, cx, rim, foot, night, motion=motion, jet=jet)
    bx = cx - BASIN_W // 2
    dove(p, bx + 1, rim + 2, night, face=1, drink=True)
    dove(p, bx + BASIN_W - 13, rim + 2, night, face=-1)
    return (bx - 1, rim - jet - 2, bx + BASIN_W + 1, foot + 1)


# The two-handled vase the vine grows out of, 15 wide and 14 tall: its lip, its handles, its body of gold lit on its
# left with a band of garnet tesserae round it, and its foot. Y G g o the gold light to dark, r the garnets.
VASE = [
    "...KKKKKKKKK...",
    "..KYGGGGGGGgK..",
    "KK.KgggggggK.KK",
    "KGK.KGGGGgK.KgK",
    "KGK.KYGGGgK.KgK",
    ".KGKYGGGGGgKgK.",
    "..KYGGGGGGGgK..",
    "..KrGrGrGrgrK..",
    "..KYGGGGGGGgK..",
    "...KGGGGGGgK...",
    "....KGGGggK....",
    ".....KGggK.....",
    "....KYGGGgK....",
    "...KKKKKKKKK...",
]


# --------------------------------------------------------------------------- the strip's court
# A partridge and a small bird for the vine's scrolls, facing right, perched: K the outline; B b the body light and
# dark, r the bars of its flank and its legs, w its face, e its eye, y its beak; G g the small bird's blue, o its
# breast. And a small cluster of grapes on its stalk, for a bird to peck at.
PARTRIDGE = [
    "........KKK.",
    ".......KwwwK",
    "......KBBeBy",
    "..KKKKKBBBK.",
    ".KbBBBBBBBK.",
    "KbrBrBrBBK..",
    ".KbbbbbbK...",
    "..KKKKKK....",
    "....r.r.....",
]
FINCH = [
    ".....KK..",
    "....KGeKy",
    "KK.KGGoK.",
    "KgKGGooK.",
    ".KggGGK..",
    "..KKKK...",
    "...r.r...",
]
GRAPES_SMALL = ["..s..", ".KsK.", "KPwPK", "KpPpK", ".KPK.", "..K.."]
BIRDS = ("dove", "partridge", "finch")
BIRD_ART = {"dove": DOVE, "partridge": PARTRIDGE, "finch": FINCH}


def bird_pal(night: bool, kind: str) -> dict:
    k = -1 if night else 0
    pal = {"K": K, "W": PEARL[6 + k], "w": PEARL[4 + k], "g": STONE[4 + k], "e": K, "y": RED[4 + k],
           "r": RED[3 + k], "B": STONE[4 + k], "b": STONE[3 + k], "G": AZURE[4 + k], "o": RED[5 + k]}
    if kind == "partridge":
        pal.update(w=EARTH[5 + k], y=STONE[2 + k])
    elif kind == "finch":
        pal.update(g=AZURE[2 + k], y=GOLD[4 + k])
    return pal


def scroll_bird(p: Pix, kind: str, x, foot, night: bool, L="base") -> tuple:
    """A bird of the vine's scrolls with its feet on row `foot` and its art's left at x, facing right: a dove, a
    partridge with its barred flank, or a small blue bird. Returns where its beak is."""
    art = BIRD_ART[kind]
    top = foot - len(art) + 1
    stamp(p, x, top, art, bird_pal(night, kind), L)
    row = next(j for j, r in enumerate(art) if "y" in r)
    return (x + art[row].index("y"), top + row)


def trailing_train(q: Pix, rx, ry, length, foot, night: bool, d=-1, eyes=None) -> set:
    """A peacock's train closed and trailing behind it from its rump at (rx, ry), `length` columns the way `d`
    points (-1 to the left, 1 to the right), drooping to lie along the ground on row `foot`: seven tiles deep at the
    rump and three at its tip, its feathers' greens laid in streaks lit along its top, an eye of gold and blue every
    few tiles along it, staggered either side of its middle, and its edge set in dark tesserae. The eyes' hearts are
    given to `eyes`, a list, for their glint. Returns the cells it covers."""
    k = -1 if night else 0
    cells: dict = {}
    mid = {}
    for i in range(length + 1):
        t = i / max(1, length)
        x = rx + d * i
        y = ry + (foot - 2 - ry) * (1 - (1 - t) ** 2)
        h = 3.3 - 1.8 * t
        mid[i] = (x, y, h)
        for yy in range(math.floor(y - h), math.ceil(y + h) + 1):
            dy = yy + 0.5 - y
            if abs(dy) > h + 0.3:
                continue
            band = 0 if dy < -h + 1.2 else 2 if dy > h - 1.2 else 1
            streak = ((i + (yy - math.floor(y)) * 2) // 2) % 2
            cells[(x, yy)] = TEAL[(5, (4, 3)[streak], 2)[band] + k]
    edge = {}
    for (x, y) in cells:
        for (dx, dy) in ((0, -1), (0, 1), (d, 0)):
            if (x + dx, y + dy) not in cells and (x + dx - rx) * d >= 0:
                edge[(x + dx, y + dy)] = K
    cells.update(edge)
    small = ["uOu", "OEO", "uOu"]
    large = [".uOu.", "uOqOu", "OqEqO", "uOqOu", ".uOu."]
    pal = {"u": TEAL[3 + k], "O": GOLD[4 + k], "q": AZURE[4 + k], "E": LAPIS[2]}
    for n, i in enumerate(range(6, length - 1, 5)):
        x, y, h = mid[i]
        art = large if h >= 2.6 else small
        off = 0 if h < 2.2 else (-1 if n % 2 else 1)
        ex, ey = x - len(art[0]) // 2, round(y) + off - len(art) // 2
        for j, row in enumerate(art):
            for c, ch in enumerate(row):
                xy = (ex + c, ey + j)
                if ch != "." and xy in cells and cells[xy] != K:
                    cells[xy] = pal[ch]
                    if ch == "E" and eyes is not None:
                        eyes.append(xy)
    for (x, y), c in cells.items():
        q.px(x, y, c)
    return set(cells)


# The standing peacock of the strip, facing right (the `DISPLAY` art turned): from its art's left, the front of its
# head, which keeps a tile or two from the basin's rim, and its rump, where its train springs. A pair either side of
# the fountain reaches PAIR_REACH and its train's length from the fountain's middle; its trains run from TRAIN_MIN
# to TRAIN_MAX columns as the room allows.
DISPLAY_FRONT = 27
DISPLAY_RUMP = (len(DISPLAY[0]) - 1 - RUMP[0], RUMP[1])
PAIR_REACH = BASIN_W // 2 + 2 + DISPLAY_FRONT - DISPLAY_RUMP[0] + 1
TRAIN_MIN, TRAIN_MAX = 14, 30


def standing_peacock(q: Pix, x, foot, night: bool, train=20, eyes=None) -> set:
    """A peacock standing on the ground at row `foot` facing right, its art's left at x, its crest up and its train
    closed, trailing behind it `train` columns along the ground (see `trailing_train`). Returns the cells it covers."""
    art = flip(DISPLAY)
    top = foot - len(art) + 1
    cells = trailing_train(q, x + DISPLAY_RUMP[0], top + DISPLAY_RUMP[1], train, foot, night, d=-1, eyes=eyes)
    stamp(q, x, top, art, peacock_pal(night))
    return cells | cells_of(art, x, top)


def peacock_pair(p: Pix, cx, foot, night: bool, motion=True, train=24, lamps=()) -> tuple:
    """A pair of peacocks standing on the ground at row `foot` either side of the fountain whose middle is column
    cx, each facing it, its crest up and its train closed and trailing behind it along the ground `train` columns:
    the left one drawn once and placed again turned, the classic pair either side of a fountain. By night the lamp
    crown over the fountain lays its light on them (`lamps`); in a moving header the eyes of their trains glint.
    Returns the span they cover."""
    eyes: list = []
    bx = cx - BASIN_W // 2 - 2 - DISPLAY_FRONT
    twin(p, "pair", lambda q: standing_peacock(q, bx, foot, night, train, eyes), cx, z=0.05, lamps=lamps)
    for (ex, ey) in list(eyes):
        eyes.append((2 * cx - 1 - ex, ey))
    if motion:
        eye_glints(p, eyes, night)
    return (cx - PAIR_REACH - train, cx + PAIR_REACH + train)


SCROLL_LEAD = 9             # from the vase's middle to the middle of the vine's first scroll, along the vine


def _turned(art: list) -> list:
    """Pixel art turned a quarter: its rows become its columns, so a leaf hanging from its stalk lies along it."""
    return ["".join(row[i] for row in art) for i in range(len(art[0]))]


def vine_scroll(p: Pix, root, extent, R, night: bool, upright=False, mid=None, birds=BIRDS) -> tuple:
    """The vine growing out of a two-handled vase of gold, the peopled scroll of the mosaics: the vase stands with its
    foot on the ground at `root` (its middle column and its foot's row), and the vine's stem rises out of its mouth and
    runs `extent` columns to the left in a wave along row `mid` (or, `upright`, as many rows upward), a tendril
    springing from each turn of it and curling round into a scroll of radius R, the scrolls in a row along the wave's
    middle with the stem passing under one and over the next, and a leaf on its stalk on the outside of each turn. In
    the scrolls by turns hang clusters of grapes, and birds stand pecking at the grapes hanging over them: a dove, a
    partridge and a small blue bird (`birds`), a small scroll taking only the small bird. Returns the box it covers
    and each scroll's middle with the side its stem passes on, or None where not one scroll fits."""
    k = -1 if night else 0
    pal = vine_pal(night)
    rx, foot = root
    vase_top = foot - len(VASE) + 1
    H = 2 * R + 5                       # from one scroll's middle to the next's
    A = R + 2                           # how far the stem swings either side of the scrolls' row
    s0 = SCROLL_LEAD + R
    n = (extent - s0 - R - 4) // H + 1
    if n < 1:
        return None
    stamp(p, rx - 7, vase_top, VASE, {"K": K, "Y": GOLD[6 + k], "G": GOLD[4 + k], "g": GOLD[2 + k], "o": GOLD[1],
                                      "r": RED[3 + k]})
    if upright:
        base = vase_top - 1

        def at(s, o):
            return (rx + o, base - s)
        rise = [(s0 * t, A * t * t) for t in (i / 24 for i in range(25))]
    else:
        mid = vase_top - R - 5 if mid is None else mid

        def at(s, o):
            return (rx - s, mid + o)
        lip = vase_top - mid
        rise = [(s0 * t, lip + (A - lip) * (1 - (1 - t) ** 2)) for t in (i / 24 for i in range(25))]
    wave = []
    s = s0
    while s <= s0 + (n - 1) * H + min(H * 0.6, R + 2):
        wave.append((s, A * math.cos(math.pi * (s - s0) / H)))
        s += 0.25
    drawn = stem(p, [at(a, b) for (a, b) in rise + wave], night)
    scrolls = []
    bird = 0
    leaf_art = LEAF if R >= 9 else LEAF_SMALL
    for i in range(n):
        sc = s0 + i * H
        side = 1 if i % 2 == 0 else -1          # the side of the scroll the stem passes on
        ring = []
        for j in range(61):
            t = j / 60
            a = math.radians(side * (130 + 290 * t))
            r = R * (1 - 0.4 * max(0.0, (t - 0.82) / 0.18))
            ring.append(at(sc + r * math.cos(a), r * math.sin(a)))
        drawn += stem(p, ring, night, width=2 if R >= 9 else 1)
        # a leaf on the outside of the stem's turn, its stalk on the stem
        sx, sy = at(sc, side * A)
        w, h = len(leaf_art[0]), len(leaf_art)
        if upright:
            leaf = _turned(leaf_art) if side < 0 else flip(_turned(leaf_art))
            lx = round(sx) - w - 1 if side < 0 else round(sx) + 3
            ly = round(sy) - h // 2
        else:
            leaf = leaf_art if side < 0 else leaf_art[::-1]
            lx = round(sx) - w // 2
            ly = round(sy) - h if side < 0 else round(sy) + 2
        leaf = leaf if i % 4 < 2 else flip(leaf)
        stamp(p, lx, ly, leaf, pal)
        drawn += list(cells_of(leaf, lx, ly))
        cx_, cy_ = at(sc, 0)
        scrolls.append((cx_, cy_, side))
        if i % 2 == 0:
            grapes = GRAPES if R >= 9 else GRAPES_SMALL
            gx, gy = round(cx_) - len(grapes[0]) // 2, round(cy_) - len(grapes) // 2 - 1
            stamp(p, gx, gy, grapes, pal)
            continue
        kind = birds[bird % len(birds)]
        bird += 1
        if len(BIRD_ART[kind][0]) > 2 * R - 6:
            kind = "finch"
        art = BIRD_ART[kind]
        bx, by = scroll_bird(p, kind, round(cx_) - len(art[0]) // 2 - 2, round(cy_) + R - 4, night)
        stamp(p, bx - 2, by - len(GRAPES_SMALL), GRAPES_SMALL, pal)
    xs = [x for x, _ in drawn] + [rx - 7, rx + 7]
    ys = [y for _, y in drawn]
    return (min(xs), min(ys), max(xs) + 1, foot + 1), scrolls


# --------------------------------------------------------------------------- the floor mosaic a footer is laid on
# The guilloche along a footer's foot, 14 wide and 7 tall: two strands of tesserae plaited round a chain of dark
# eyes, one in garnet reds and one in blues, each lit along its upper edge, the strand rising from left to right
# lying over at each crossing, and a gold tessera at the heart of each eye. A a the red strand light and dark, B b
# the blue, o the gold, . the dark setting. The same plait 10 wide in five rows where the words leave the floor
# fewer, and where they leave it fewer still a string of red and blue tesserae with gold between them.
GUILLOCHE = [
    "AA....BBB....A",
    "aaA..BbbbB..Aa",
    "..aABb...bBAa.",
    "o..Bb..o..Aa..",
    "..BbaA...AabB.",
    "BBb..aAAAa..bB",
    "bb....aaa....b",
]
GUILLOCHE_SMALL = [
    "AA..BBB..A",
    "aaABbbbBAa",
    "o.Bb.o.Aa.",
    "BBbaAAAabB",
    "bb..aaa..b",
]
BEADS = ["AAoBBo", "......"]
# The floor's opus sectile, where it rises over the plait along a cell that leaves it room, 14 wide and 5 tall: on
# white marble veined in grey, a roundel of porphyry and a square of serpentine set on its point by turns, each cut
# and polished, lit on its upper left. W w the marble and its veins, P p h the porphyry, its shade and its light,
# S s T the serpentine, its shade and its light.
SECTILE = [
    "WWpPpWWWWWsWWW",
    "WpPhPpWwWsSsWW",
    "wPhPPPWWsSTSsW",
    "WpPPPpWWWsSsWw",
    "WWpPpWWwWWsWWW",
]
# The doves of Pliny, after the mosaic of them at their bowl: a basin of bronze with its rim of gold on a low foot,
# seen a little from above with the water in it, 22 wide and 11 tall, and two doves on its near rim (its fifth row),
# the one at its left bent to drink and the one at its right facing it with its head up. Y G g the gold, w the light
# on the water, B b the water, E e the bronze.
PLINY_BOWL = [
    ".....KKKKKKKKKKKK.....",
    "...KKYGGGGGGGGGGgKK...",
    "..KgwwbBBBBBBBBBBbgK..",
    ".KgbBBBBBBBBBBBBBBbgK.",
    "KGYYYYYYYYYYYYYYYYYYgK",
    ".KgEEEEEEEEEEEEEEEEgK.",
    "..KeEEEEEEEEEEEEEEeK..",
    "....KKeeeeeeeeeeKK....",
    "........KYGGgK........",
    ".......KYGGGGgK.......",
    ".......KKKKKKKK.......",
]
PLINY_W, PLINY_H = 24, 15   # the bowl with its doves on it, the right one standing out past its rim
# The oil lamp that stands beside them, of bronze on its stand: cold by day, and by night its flame burning, the
# heart of it (H) the brightest of the flames.
LAMP_MARK = [
    ".........Y....",
    "........YFY...",
    "........FHF...",
    "....KKK.KFK...",
    "...KbBBKKBK...",
    "..KbBBBBBBBK..",
    ".KbBbbbbbbbbK.",
    "KKKKKKKKKKKKK.",
    ".....KbbK.....",
    "......Kb......",
    "......Kb......",
    "......Kb......",
    ".....KbBK.....",
    "....KbbbbK....",
    "...KKKKKKKK...",
]
FLOOR = 7                   # the rows the floor's plait takes along a footer's foot where the words leave them
RISE = 6                    # the rows the floor rises over that where a cell leaves it room
RUN = 40                    # the fewest columns a stretch of it rises along


def _floor_tile(night: bool) -> dict:
    """A tile of the floor's white marble, 12 by 4: courses of white tesserae in two whites, grey grout between."""
    k = -1 if night else 0
    cells = {}
    for y in range(4):
        for x in range(12):
            if y == 3 or (x + (6 if y // 4 % 2 else 0) + (3 if y > 1 else 0)) % 6 == 5:
                c = PEARL[3 + k]
            else:
                c = PEARL[(6, 5)[(x // 6 + y // 2) % 2] + k]
            cells[(x, y)] = c
    return cells


def _tiled(art: list, pal: dict) -> dict:
    """The cells of a pattern tile drawn as `art` in `pal`."""
    return {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row)}


def _room(p: Pix, x, top) -> int:
    """The rows over row `top` at column x clear of every word by two rows and of anything drawn, up to RISE."""
    base = p.layers["base"]
    n = 0
    while n < RISE:
        y = top - 1 - n
        if (x, y) in base or not p.clear_of_words(x - 1, y - 2, x + 2, y + 1):
            break
        n += 1
    return n


def _taken(p: Pix, tops) -> list:
    """Summed counts of the cells a mark may not take, row by row and column by column (so a box's count is four
    lookups): the frame, the floor, all that is drawn, and every word with two units round it."""
    w, h = p.w, p.h
    grid = [[x <= FW or x >= w - FW - 1 or y < FW or y >= tops[x] for x in range(w)] for y in range(h)]
    for (x, y) in p.layers["base"]:
        grid[y][x] = True
    for (a, b, c, d) in p.words:
        for y in range(max(0, b - 2), min(h, d + 2)):
            for x in range(max(0, a - 2), min(w, c + 2)):
                grid[y][x] = True
    sums = [[0] * (w + 1) for _ in range(h + 1)]
    for y in range(h):
        run = 0
        for x in range(w):
            run += grid[y][x]
            sums[y + 1][x + 1] = sums[y][x + 1] + run
    return sums


def _clear(sums, x0, y0, x1, y1) -> bool:
    """Whether the box from (x0, y0) to (x1, y1), ends excluded, holds nothing a mark may not take."""
    if x0 < 0 or y0 < 0 or x1 >= len(sums[0]) or y1 >= len(sums):
        return False
    return sums[y1][x1] - sums[y0][x1] - sums[y1][x0] + sums[y0][x0] == 0


def _best(runs) -> tuple | None:
    """The middle of the widest run of places, the rightmost of two as wide."""
    if not runs:
        return None
    run, row = max(runs, key=lambda r: (len(r[0]), r[0][-1]))
    return run[len(run) // 2], row


def _stand(p: Pix, sums, tops, rule, width, height) -> tuple | None:
    """Where a mark `width` wide and `height` tall can stand, as (x, row) with `row` the one it stands on: the floor
    where it lies level under it, or a rule between cells, its box clear of all a mark may not take (see `_taken`)."""
    base = p.layers["base"]
    under: dict = {}
    for x in range(FW + 1, p.w - FW - 1):
        under.setdefault(tops[x], set()).add(x)
    for (x, y), c in base.items():
        if c == rule and FW < x < p.w - FW - 1:
            under.setdefault(y, set()).add(x)
    runs = []
    for row, cols in under.items():
        run = []
        for x in range(FW + 1, p.w - FW - width):
            if all(i in cols for i in range(x, x + width)) and _clear(sums, x, row - height, x + width, row):
                run.append(x)
            elif run:
                runs.append((run, row))
                run = []
        if run:
            runs.append((run, row))
    return _best(runs)


def _ledge(p: Pix, sums, width, height) -> tuple | None:
    """Where a mark `width` wide and `height` tall can stand on a ledge of gold two rows deep and two wider each side,
    where nothing stands for it: as (x, row) with `row` the ledge's top."""
    runs = []
    for top in range(FW, p.h - height - 2):
        run = []
        for x in range(FW + 3, p.w - FW - width - 2):
            if _clear(sums, x - 2, top, x + width + 2, top + height + 2):
                run.append(x)
            elif run:
                runs.append((run, top + height))
                run = []
        if run:
            runs.append((run, top + height))
    return _best(runs)


def pliny(p: Pix, x, stand, night: bool, lamp_beside: bool):
    """The doves of Pliny standing on row `stand`, their art's left at column x: the bowl, the dove bent to drink on
    its rim at the left and the dove facing it at the right; and the oil lamp standing beside them where there is room
    for it, cold by day and by night lit, its glow round it and its light laid on the doves and the bowl."""
    k = -1 if night else 0
    top = stand - len(PLINY_BOWL)
    rim = top + 4
    stamp(p, x + 1, top, PLINY_BOWL, {"K": K, "Y": GOLD[5 + k], "G": GOLD[4 + k], "g": GOLD[2 + k],
                                      "w": PEARL[6 + k], "B": AZURE[3 + k], "b": AZURE[2 + k], "E": BRONZE[4 + k],
                                      "e": BRONZE[2 + k]})
    keep(p, dove(p, x, rim, night, drink=True) | dove(p, x + 12, rim, night, face=-1)
         | cells_of(PLINY_BOWL, x + 1, top))
    if not lamp_beside:
        return
    lx, ly = x + PLINY_W + 1, stand - len(LAMP_MARK)
    pal = {"K": K, "b": BRONZE[2 + k], "B": BRONZE[4 + k]}
    if night:
        pal.update(Y=FLAME[5], F=FLAME[4], H=FLAME[6])
    for j, row in enumerate(LAMP_MARK):
        for i, ch in enumerate(row):
            if pal.get(ch):
                p.px(lx + i, ly + j, pal[ch], flick(p, 1) if ch in "YFH" else "base")
    keep(p, cells_of(LAMP_MARK, lx, ly))
    if night:
        light_rings(p, lx + 9.5, ly + 2, 9, 8, FLAME[3], GLOW, L=flick(p, 1, back=True))
        lamp(p, lx + 9.5, ly + 2, 16, 1, cells_of(LAMP_MARK[:3], lx, ly))


def floor(p: Pix, night: bool, rule: str):
    """A footer once its words are set: the floor mosaic it stands on along its foot, between the frame's corner
    stones, as deep as the lowest word leaves it and a row clear of it: the guilloche plaited in garnet and blue round
    its chain of dark eyes, in seven rows where they leave it room, in five where fewer, and where fewer still a
    string of red and blue tesserae; and along every stretch of a cell that leaves it the room, the floor rising over
    the plait in a band of opus sectile, roundels of porphyry and squares of serpentine in white marble, the ruled
    lines between the cells standing on it. Where the cells leave room the doves of Pliny stand at their bowl, on the
    floor, on a rule or on a ledge of gold, the widest stretch of room they find, and the oil lamp stands beside them
    where there is room, cold by day and lit by night, or else hangs over them where the rows leave it room."""
    k = -1 if night else 0
    w, h = p.w, p.h
    base = p.layers["base"]
    low = max((b[3] for b in p.words), default=0)
    top = min(h - 2, max(h - FLOOR, low + 1))
    room = [_room(p, x, top) if FW < x < w - FW else 0 for x in range(w)]
    tops = [top] * w
    x = FW + 1
    while x < w - FW - 1:
        if room[x] < RISE:
            x += 1
            continue
        b = next((i for i in range(x, w - FW - 1) if room[i] < RISE), w - FW - 1)
        if b - x >= RUN:
            tops[x:b] = [top - RISE] * (b - x)
        x = b
    for xy in [xy for xy, c in base.items() if c == rule and xy[1] >= tops[xy[0]]]:
        del base[xy]
    # the plait along the foot, as deep as the words leave it
    art = next(a for a in (GUILLOCHE, GUILLOCHE_SMALL, BEADS) if h - top >= len(a) or a is BEADS)
    band = h - len(art)
    plait = {"A": RED[5 + k], "a": RED[3 + k], "B": AZURE[5 + k], "b": AZURE[3 + k], "o": GOLD[6 + k], ".": K}
    lay(p, pattern(p, f"fg{len(art)}{'n' if night else 'd'}", len(art[0]), len(art), _tiled(art, plait), y0=band),
        0, band, w, len(art))
    # the floor between the plait and the words: its setting, and the opus sectile where it rises
    marble = pattern(p, f"fl{'n' if night else 'd'}", 12, 4, _floor_tile(night))
    sectile = pattern(p, f"fs{'n' if night else 'd'}", len(SECTILE[0]), len(SECTILE), _tiled(SECTILE, {
        "W": PEARL[6 + k], "w": PEARL[4 + k], "P": PORPHYRY[4 + k], "p": PORPHYRY[2 + k], "h": PORPHYRY[6 + k],
        "S": GREEN[4 + k], "s": GREEN[2 + k], "T": GREEN[6 + k]}), y0=band - len(SECTILE))
    x = 0
    while x < w:
        t = tops[x] if FW <= x < w - FW else top
        b = next((i for i in range(x, w) if (tops[i] if FW <= i < w - FW else top) != t), w)
        if t < band:
            p.hline(x, b, t, K)
            deep = band - t - 1
            inlaid = len(SECTILE) if deep >= len(SECTILE) else 0
            lay(p, sectile, x, band - inlaid, b - x, inlaid)
            lay(p, marble, x, t + 1, b - x, deep - inlaid)
        keep(p, {(xx, yy) for xx in range(x, b) for yy in range(t, h)})
        x = b
    corner_stone(p, 0, h - 7, night, "green")
    corner_stone(p, w - 7, h - 7, night, "red")
    # the doves of Pliny at their bowl, and their lamp: standing beside them where there is room, on the floor or a
    # rule or else on a ledge; where there is not, the doves alone, and the lamp hung over them if the rows allow
    sums = _taken(p, tops)
    for width, beside in ((PLINY_W + 1 + len(LAMP_MARK[0]), True), (PLINY_W, False)):
        spot = _stand(p, sums, tops, rule, width, PLINY_H)
        ledge = None if spot else _ledge(p, sums, width, PLINY_H)
        if spot or ledge:
            break
    else:
        return
    x, row = spot or ledge
    if ledge:
        p.hline(x - 2, x + width + 2, row, GOLD[5 + k])
        p.hline(x - 2, x + width + 2, row + 1, K)
        p.px(x - 2, row, K)
        p.px(x + width + 1, row, K)
    pliny(p, x, row, night, lamp_beside=beside)
    at = row - PLINY_H - len(OIL) - 1
    for hx in (x + 12, x + 18, x + 6) if not beside and at - FW >= 3 else ():
        if _clear(sums, hx - 4, FW, hx + 5, row - PLINY_H):
            hanging_lamp(p, hx, FW, at, night, phase=1, reach=14)
            break


# --------------------------------------------------------------------------- links
# Icons for the link buttons, 9 by 7, inlaid in gold tesserae on a panel of lapis: an eight-pointed star, a cluster of
# grapes, an eye of a peacock's train and an oil lamp lit. Y y the gold and its shade, W its light, r a garnet.
ICONS = {
    "star": ["....Y....", ".Y..Y..Y.", "..yYWYy..", "YYYWWWYYY", "..yYWYy..", ".Y..Y..Y.", "....Y...."],
    "grapes": ["....y.YY.", "...yYYYy.", "..WYY.YY.", ".YYyYYy..", "..YyYY...", "...YY....", "....y...."],
    "eye": ["...yyy...", "..yYYYy..", ".yYrrrYy.", "yYrrWrrYy", ".yYrrrYy.", "..yYYYy..", "...yyy..."],
    "lamp": [".......W.", "......WY.", "..yyy.Yy.", ".yYYYYYYy", "yYYYYYYy.", ".yyyyyy..", "...yYy..."],
}
LINK_ICONS = ("star", "grapes", "eye", "lamp")


def _veins(night: bool, dark=False) -> dict:
    """A tile of white marble with its grey veins, 16 by 9; `dark`, a tile of porphyry with its pale flecks and a
    darker vein, for a field the night's light letters are set on."""
    k = -1 if night else 0
    field, vein = (PEARL[6 + k], PEARL[4 + k]) if not dark else (PORPHYRY[1], PORPHYRY[0])
    cells = {}
    for y in range(9):
        for x in range(16):
            cells[(x, y)] = field
            if dark and (x * 7 + y * 5) % 17 == 0:
                cells[(x, y)] = PORPHYRY[2]
    for i in range(16):
        y = round(1 + i * 0.45 + math.sin(i * 0.9) * 0.8)
        if 0 <= y < 9:
            cells[(i, y)] = vein
    for i in range(6):
        cells[((11 + i) % 16, (6 + i // 2) % 9)] = vein
    return cells


def plaque(p: Pix, w: int, night: bool):
    """A link button finished as a plaque of white marble, its grey veins running across it, set in a gold rim with a
    dark edge, and at its left a panel of lapis tesserae its icon is inlaid on in gold. The marble is a pattern tile,
    so a long label costs no more than a short one."""
    k = -1 if night else 0
    base = p.layers["base"]
    for xy in [xy for xy in base if 3 <= xy[1] <= 11 and 1 <= xy[0] < w - 1]:
        del base[xy]
    pid = pattern(p, f"mv{'n' if night else 'd'}", 16, 9, _veins(night), y0=3)
    p.shapes["base"].append(f'<rect x="1" y="3" width="{w - 2}" height="9" fill="url(#{pid})"/>')
    p.hline(1, w - 1, 3, GOLD[5 + k])
    p.hline(1, w - 1, 11, GOLD[2 + k])
    p.vline(1, 3, 12, GOLD[4 + k])
    p.vline(w - 2, 3, 12, GOLD[2 + k])
    p.rect(3, 4, 11, 7, LAPIS[2])
    p.hline(3, 14, 4, LAPIS[3])


def link_icon(index: int, night: bool) -> tuple:
    k = -1 if night else 0
    pal = {"Y": GOLD[5 + k], "y": GOLD[3 + k], "W": GOLD[6], "r": RED[4 + k]}
    return ICONS[LINK_ICONS[index % len(LINK_ICONS)]], pal


# --------------------------------------------------------------------------- the elements
def mosaic_card(p: Pix, x, y, w, h, night: bool, seed: int, ink: str):
    """A schematic's card as a plaque of white marble set in a rim of gold tesserae, its icon taken up from where the
    layout drew it and inlaid again in gold on a panel of lapis at its left, and a jewel at each top corner."""
    k = -1 if night else 0
    icon_y = y + (h - 7) // 2
    icon = {(xx - x - 2, yy - icon_y) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9)
            if p.get(xx, yy) == ink}
    p.rect(x + 1, y + 1, 13, h - 2, LAPIS[2])
    p.vline(x + 14, y + 1, y + h - 1, GOLD[2 + k])
    for (u, v) in icon:
        p.px(x + 4 + u, icon_y + v, GOLD[5 + k] if (u, v - 1) not in icon else GOLD[4 + k])
    for xx in range(x, x + w):
        p.px(xx, y, GOLD[(5, 4)[(xx - x) // 2 % 2] + k])
        p.px(xx, y + h - 1, GOLD[(3, 2)[(xx - x) // 2 % 2] + k])
    for yy in range(y, y + h):
        p.px(x, yy, GOLD[(5, 4)[(yy - y) // 2 % 2] + k])
        p.px(x + w - 1, yy, GOLD[(3, 2)[(yy - y) // 2 % 2] + k])
    for (jx, stone) in ((x + 2, RED), (x + w - 3, GREEN)):
        p.px(jx, y, stone[4 + k])
        p.px(jx, y + h - 1, stone[2 + k])


def gold_wire(p: Pix, cells, night: bool):
    """A schematic's wire as a line of gold tesserae, two tiles of one gold and two of the next along it, its shade
    under a level run and beside an upright one, and a garnet set in gold where it bends."""
    k = -1 if night else 0
    kinds: dict = {}
    for i, (x, y, d) in enumerate(cells):
        kinds.setdefault((x, y), set()).add(d)
        p.px(x, y, GOLD[5 + k] if (i // 2) % 2 else GOLD[3 + k])
        if d == "h":
            p.px(x, y + 1, GOLD[1 + k])
        else:
            p.px(x + 1, y, GOLD[1 + k])
    for (x, y), ds in kinds.items():
        if len(ds) == 2:
            for (dx, dy, c) in ((0, 0, RED[5 + k]), (-1, 0, GOLD[4 + k]), (1, 0, GOLD[3 + k]), (0, -1, GOLD[5 + k]),
                                (0, 1, GOLD[2 + k]), (1, 1, K)):
                p.px(x + dx, y + dy, c)


STONES = ("lapis", "porphyry", "green", "gold", "red", "purple")


def column_bar(p: Pix, bx, base, bw, v, night: bool, i=0):
    """A week's commits as a column of tesserae `v` tall on the base line, its tiles stacked in courses with grout
    between them, lit on its left, in a stone by turns, and a capital of white marble on its head."""
    k = -1 if night else 0
    S = RAMP[STONES[i % len(STONES)]]
    top = base - v
    for y in range(top, base):
        course = (base - 1 - y) % 3 == 2
        for xx in range(bx, bx + bw):
            u = (xx - bx) / max(1, bw - 1)
            if course:
                c = S[1 + k]
            elif xx == bx + bw - 1:
                c = S[2 + k]
            else:
                c = S[(4 if u < 0.35 else 3) + k + (1 if ((xx - bx) // 2 + (base - y) // 3) % 2 and u >= 0.35 else 0)]
            p.px(xx, y, c)
    if v >= 4:
        p.hline(bx - 1, bx + bw + 1, top - 1, PEARL[6 + k])
        p.hline(bx - 1, bx + bw + 1, top, PEARL[4 + k])
        p.px(bx - 1, top, K)
        p.px(bx + bw, top, K)


def sun_disc(p: Pix, arc, night: bool):
    """The dial as a sun disc of gold tesserae: its rays laid in two golds by turns from the hub outward, a ring of
    the brightest gold round it and a dark edge, every figure on it holding its contrast."""
    from ...holidays.pixel import tube
    k = -1 if night else 0
    cx = (arc[0][0] + arc[-1][0]) / 2
    cy = arc[0][1]
    r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
    p.dial = (cx, cy, r)
    face = sun_face(night)
    for y in range(math.floor(cy - r), math.ceil(cy) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            c = face(x, y, cx, cy, r)
            if c:
                p.px(x, y, c)

    def rim(s, o, lam, x, y):
        if abs(o) > 0.78:
            return K
        return GOLD[(6 if lam > 0.6 else 5 if lam > 0.3 else 4) + k]
    tube(p, arc, 3.0, rim, outline=K)


def sun_face(night: bool):
    """The colour at (x, y) of the sun disc about (cx, cy) of radius r: its rays of two pale golds by day and two deep
    by night, so every figure on it keeps its contrast; None off the disc."""
    a_, b_ = (TILE[6], TILE[5]) if not night else (GOLD[0], BRONZE[2])

    def colour(x, y, cx, cy, r):
        dx, dy = x + 0.5 - cx, cy - (y + 0.5)
        if dy < -0.5 or math.hypot(dx, dy) >= r - 3.6:
            return None
        return a_ if int(math.degrees(math.atan2(max(dy, 0), dx)) // 9) % 2 else b_
    return colour


def gnomon(p: Pix, night: bool, accent: str):
    """The dial's hand redrawn as the gnomon's shadow falling across the sun disc from its hub to the count: a wedge
    of shade, two tiles wide at the hub and one at its tip, in place of the plain line the layout drew in `accent`."""
    cx, cy, r = p.dial
    reach = r - 11
    hand = [(x, y) for (x, y), c in p.layers["base"].items() if c == accent
            and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2]
    if not hand:
        return
    face = sun_face(night)
    for (x, y) in hand:
        c = face(x, y, cx, cy, r)
        if c:
            p.px(x, y, c)
    far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
    ux, uy = far[0] + 0.5 - cx, far[1] + 0.5 - cy
    n = math.hypot(ux, uy) or 1
    ux, uy = ux / n, uy / n
    for i in range(int((reach + 1) * 3)):
        t = i / 3
        half = 1.0 * (1 - t / (reach + 1)) + 0.3
        for o in (-half, 0, half):
            x = math.floor(cx + ux * t - uy * o)
            y = math.floor(cy + uy * t + ux * o)
            p.px(x, y, LAPIS[2] if night else EARTH[1])


def stone_matter(i, xx, yy, y0, y1, lift, night: bool) -> str:
    """The stones of the mosaic by turns, each in its own grain: porphyry flecked pale, serpentine veined, lapis with
    its gold, gold tesserae in courses, white marble veined grey and red jasper."""
    k = -1 if night else 0
    kind = i % 6
    if kind == 0:
        c = PORPHYRY[3 + k] if (xx * 7 + yy * 3) % 11 else PORPHYRY[5 + k]
    elif kind == 1:
        c = GREEN[2 + k] if (xx + yy * 2) % 9 else GREEN[4 + k]
    elif kind == 2:
        c = LAPIS[3] if (xx * 5 + yy * 7) % 13 else GOLD[4 + k]
    elif kind == 3:
        c = GOLD[1 + k] if (yy - y0) % 4 == 3 or (xx + (yy - y0) // 4 * 2) % 4 == 3 else GOLD[4 + k]
    elif kind == 4:
        c = PEARL[4 + k] if (xx + yy) % 7 == 0 else PEARL[6 + k]
    else:
        c = RED[3 + k] if (xx * 3 + yy) % 8 else RED[5 + k]
    try:
        return step(c, lift)
    except KeyError:
        return c


def marble_cell(q: Pix, ox, oy, night: bool, L="far"):
    """A cell of white marble a counter's numeral is laid in tesserae on, 11 by 15: a rim of gold tesserae round it,
    lit along its top and left, and a vein of grey across the marble clear of the numeral."""
    k = -1 if night else 0
    for yy in range(15):
        for xx in range(11):
            if xx in (0, 10) or yy in (0, 14):
                c = GOLD[(5 if xx == 0 or yy == 0 else 2) + k]
            elif (xx, yy) in ((1, 2), (2, 2), (8, 12), (9, 12)):
                c = PEARL[4 + k]
            else:
                c = PEARL[6 + k]
            q.px(ox + xx, oy + yy, c, L)


def vine_line(p: Pix, x0, x1, y, night: bool):
    """The time line as the vine: its stem running along up to today, waving a tile up and down, a dark row under it,
    and a leaf now and then above it."""
    pal = vine_pal(night)
    for x in range(x0, x1):
        dy = 0 if (x // 6) % 2 else -1
        p.px(x, y + dy, GREEN[4] if night else GREEN[3])
        p.px(x, y + dy + 1, GREEN[2] if night else K)
    for x in range(x0 + 10, x1 - 6, 28):
        stamp(p, x, y - 6, LEAF_SMALL, pal)


def grape_release(p: Pix, x, gy, kind: str, night: bool, i=0):
    """A release on the vine: a cluster of grapes hung from the stem, a large one for a big release, a small one for
    a patch, green and unripe for one still to come, and the vase the vine grows from for the repository's founding."""
    k = -1 if night else 0
    pal = vine_pal(night)
    if kind == "made":
        art = ["KKKKK", "KYGgK", ".KGK.", "KYGgK", "KKKKK"]
        stamp(p, x - 2, gy - 4, art, {"K": K, "Y": GOLD[6 + k], "G": GOLD[4 + k], "g": GOLD[2 + k]})
        return
    if kind == "next":
        pal = dict(pal, P=GREEN[5 + k], p=GREEN[3 + k], w=GREEN[6 + k])
    if kind == "big":
        stamp(p, x - 3, gy, GRAPES, pal)
        stamp(p, x + 1, gy - 4, LEAF_SMALL, pal)
    elif kind == "minor":
        stamp(p, x - 1, gy + 1, ["KPK", "PwP", ".p."], pal)
    else:
        stamp(p, x - 3, gy, GRAPES[:-2] + ["..KpK.."], pal)


# A peacock perched on the vine at today, facing left, 9 wide: its crest, head and back over the stem in four rows,
# and its train hanging under the stem, an eye at its end. Letters as for `PEACOCK`.
PERCHED = ["c........", "KBK......", "yBBKggKK.", ".KBgGoGgK"]
PERCHED_TRAIN = ["....KtTK.", "....KtTK.", "....KtTK.", "...KOqOK.", "...KqEqK.", "....KKK.."]


def today_peacock(p: Pix, x, y, night: bool):
    """A peacock perched on the vine at today's end, facing back along it, its crest, head and back over the stem
    and its train hanging under it with an eye at its end, as long as the rows under the stem allow."""
    pal = peacock_pal(night)
    stamp(p, x - 2, y - 4, PERCHED, pal)
    room = min(len(PERCHED_TRAIN), p.h - FW - 2 - (y + 1))
    train = PERCHED_TRAIN[:max(0, room - 3)] + PERCHED_TRAIN[-3:] if room >= 3 else []
    stamp(p, x - 2, y + 1, train, pal)


# A portrait in mosaic, 15 by 17, for a contributor: the head and shoulders frontal on a roundel of gold, a jewelled
# diadem on the hair, the face, a jewelled collar and the robe in the person's colour (Q q). Letters as for `COURT`.
PORTRAIT = [
    "....KKKKKKK....",
    "...KGGGGGGGK...",
    "..KGGKYrYKGGK..",
    ".KGGKYgYgYKGGK.",
    ".KGKhhhhhhhKGK.",
    "KGGKhfFFFfhKGGK",
    "KGGKfeFfeFfKGGK",
    "KGGKfFFFFFfKGGK",
    "KGGGKffmffKGGGK",
    "KGGGGKfffKGGGGK",
    ".KGKKnYnYnKKGK.",
    ".KKQnYrYgYnQKK.",
    "..KQQnnnnnQQK..",
    "..KqQQQQQQQqK..",
    "...KqQQQQQqK...",
    "....KKKKKKK....",
]
ROBES = ("purple", "green", "red", "azure", "porphyry", "teal")


def portrait(p: Pix, cx, cy, i, night: bool, bot=False):
    """A contributor as a portrait in mosaic on a roundel of gold: the face frontal on the hand's skins by turns, a
    jewelled diadem on the hair, a jewelled collar and the robe in their own colour by turns; a bot as a dove on the
    roundel."""
    k = -1 if night else 0
    pal = court_pal(night, ROBES[i % len(ROBES)], skin=i % len(SKINS))
    pal.update({"G": GOLD[4 + k], "h": (EARTH[1], EARTH[3], STONE[2], RED[1])[i % 4]})
    if bot:
        stamp(p, cx - 7, cy - 8, [r.replace("h", "G").replace("f", "G").replace("F", "G").replace("e", "G")
                                  .replace("m", "G").replace("Y", "G").replace("r", "G").replace("g", "G")
                                  for r in PORTRAIT], pal)
        dove(p, cx - 6, cy + 5, night)
        return
    stamp(p, cx - 7, cy - 8, PORTRAIT, pal)


def tile_bar(p: Pix, x, y, w, fill, night: bool):
    """A contributor's share as a bar of tesserae: a dark setting, filled with gold tiles in pairs as far as their
    commits reach, the rest lapis."""
    k = -1 if night else 0
    p.box(x, y, w + 2, 4, K)
    for xx in range(x + 1, x + w + 1):
        lit = xx < x + 1 + fill
        a, b = (GOLD[5 + k], GOLD[3 + k]) if lit else (LAPIS[3], LAPIS[2])
        p.px(xx, y + 1, a if (xx - x) % 3 else b)
        p.px(xx, y + 2, b)


def jewelled_ring(p: Pix, cx, cy, r0, r1, night: bool):
    """The seal's roundel: a broad ring of porphyry about the seal's disc, its grain flecked pale, bound inside and
    out with gold tesserae and set with cut stones of garnet and emerald by turns, each in its gold setting."""
    k = -1 if night else 0
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d > r1 + 0.5 or d < r0 - 0.5:
                continue
            lit = ((x + 0.5 - cx) * -0.63 + (y + 0.5 - cy) * -0.78) / max(d, 1)
            if d > r1 - 0.5:
                c = K
            elif d > r1 - 1.5 or d < r0 + 0.6:
                c = GOLD[(5 if lit > 0.2 else 3) + k]
            else:
                c = PORPHYRY[(4 if lit > 0.3 else 3 if lit > -0.3 else 2) + k]
                if (x * 7 + y * 3) % 13 == 0:
                    c = PORPHYRY[5 + k]
            p.px(x, y, c)
    rm = (r0 + r1) / 2
    for n in range(12):
        a = math.radians(n * 30 + 15)
        gx, gy = math.floor(cx + rm * math.cos(a)), math.floor(cy + rm * math.sin(a))
        stone = (RED, GREEN)[n % 2]
        for (dx, dy, c) in ((0, 0, stone[5 + k]), (1, 0, stone[3 + k]), (0, 1, stone[3 + k]), (1, 1, stone[2 + k])):
            p.px(gx + dx, gy + dy, c)
        for (dx, dy) in ((-1, 0), (2, 0), (0, -1), (1, -1), (0, 2), (1, 2)):
            p.px(gx + dx, gy + dy, GOLD[4 + k])


def gold_check(p: Pix, night: bool, accent: str, shadow: str):
    """The check the layout set in the seal's disc laid again in gold tesserae: each of its tiles, two units square, in
    one of two golds by turns and lit at its upper left, and the shadow it casts set in dark tesserae, so the mark at
    the heart of the porphyry roundel reads as gold inlay on the disc by day and by night."""
    cx, cy = p.seal
    x0, y0 = cx - 7, cy - 15
    base = p.layers["base"]
    for y in range(y0, y0 + 14):
        for x in range(x0, x0 + 16):
            c = base.get((x, y))
            if c == accent:
                i, j = x - x0, y - y0
                base[(x, y)] = GOLD[6] if i % 2 == 0 and j % 2 == 0 else GOLD[(4, 5)[(i // 2 + j // 2) % 2]]
            elif c == shadow:
                base[(x, y)] = K


def _inlay_tile(night: bool) -> dict:
    """Two tiles of the placard's border of cut stones, each 10 by 5: a dark row of setting outside, a disc of
    porphyry in the one and of serpentine in the other cut into a square of yellow marble, then a slab of grey marble,
    and a gold line inside."""
    k = -1 if night else 0
    cells = {}
    for x in range(20):
        cells[(x, 0)] = K
        cells[(x, 4)] = GOLD[(4, 3)[x % 2] + k]
        for y in range(1, 4):
            u = x % 10
            if u < 4:
                corner = u in (0, 3) and y in (1, 3)
                ramp = PORPHYRY if x < 10 else GREEN
                cells[(x, y)] = GOLD[5 + k] if corner else ramp[(4 if u + y < 4 else 2) + k]
            else:
                cells[(x, y)] = STONE[(5 if y == 1 else 4) + k]
    return cells


def inlaid_panel(p: Pix, night: bool):
    """A placard as a panel inlaid in cut marble over the whole card: its field of white marble veined in grey for
    the words by day, and by night of porphyry for the night's light letters; round it a border of cut stones, discs
    of porphyry and of serpentine by turns cut into squares of a yellow marble between slabs of grey marble, inside a
    dark row of setting and a line of gold, with a disc of porphyry at each corner. One tile of the border lays all
    four sides, turned to each."""
    w, h = p.w, p.h
    pid = pattern(p, f"ov{'n' if night else 'd'}", 16, 9, _veins(night, dark=night))
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{pid})"/>')
    sid = pattern(p, f"os{'n' if night else 'd'}", 20, 5, _inlay_tile(night))
    turns = (("", 0, w), (f' transform="matrix(1 0 0 -1 0 {h})"', 0, w),
             (' transform="matrix(0 1 1 0 0 0)"', FW, h - FW), (f' transform="matrix(0 1 -1 0 {w} 0)"', FW, h - FW))
    for turn, a, b in turns:
        p.shapes["base"].append(f'<rect x="{a}" width="{b - a}" height="{FW}" fill="url(#{sid})"{turn}/>')
    for (cx_, cy_) in ((0, 0), (w - 5, 0), (0, h - 5), (w - 5, h - 5)):
        p.rect(cx_, cy_, 5, 5, K)
        disc(p, cx_ + 1, cy_ + 1, PORPHYRY, night)


def disc(p: Pix, x, y, ramp, night: bool):
    """A cut disc of stone, 4 by 4, set in a square of yellow marble, its top-left at (x, y)."""
    k = -1 if night else 0
    for dy in range(4):
        for dx in range(4):
            corner = dx in (0, 3) and dy in (0, 3)
            c = GOLD[5 + k] if corner else ramp[(4 if dx + dy < 3 else 2) + k]
            p.px(x + dx, y + dy, c)
