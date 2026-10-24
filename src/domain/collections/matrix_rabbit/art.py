# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rabbit set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is a page of a storybook in spring, pale yellow-green by day and sprigged with small flowers printed a
tone off the paper, and by night a deep indigo garden under the stars, held in a frame of clipped hedge: its leaves
lit along their upper edges, and across a header's top a deeper hedge set with roses, some of them white roses half
painted red, the paint still running, parting either side of the month's mark. Across the sky behind the title a
pack of playing cards tumbles on the wind, turning over and over. Every letter of a title is printed on a playing
card, red or black by its suit, with a small pip in its corner, the cards dealt a little askew and overlapping as a
hand of them lies on a table. Headers open on Wonderland after Tenniel: at the left the White Rabbit in his jacket
and waistcoat, bounding along and looking at his gold watch under an arch of roses, tulips and Easter eggs in the
grass about him, a butterfly fluttering round the arch by day and the moon in it by night; at the right an old tree,
the Cheshire Cat grinning on its bough by day and only his grin left there by night, its roots arching over the
rabbit hole at its foot, the code glowing up out of the hole in phosphor, faint by day and bright by night, lighting
the roots, the grass and everything that stands by it, with toadstools beside it, a little bottle with a tag on its
neck, and a trail of fallen cards leading to it. A section's header has the Caterpillar on the giant mushroom, his
hookah beside him and its smoke rising in rings of the code, foxgloves at its foot; a strip's the rose tree in its
tub, the Two of Spades painting its roses red and a lantern hung in it. The little golden key and the rabbit's watch
are the marks beside a title, and tufts of spring grass lie along a rule. A phone's headers have the same world
under their words: the whole of Wonderland, the Caterpillar, and the gardeners at a rose bush and the rose tree. The
footers stand on the hedge's top, the clipped hedge rising over it, the rabbit hole in its mound glowing with the
code; the links are playing cards under a sprig of hedge; and the elements are built of playing cards, the hedge's
briar, roses painted red, stacks of cards, the rabbit's gold watch and a wreath of hedge. Everything is shaded from
the one light in the upper left on the set's own ramps, and every light is the hand's phosphor."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, LZ, Pix, fold, num
from .. import rain
from .palette import C, NIGHT_SKY, RAMP, X

PAGE, GARDEN, HEDGE, ROSE = RAMP["page"], RAMP["garden"], RAMP["hedge"], RAMP["rose"]
CARD, SPADE, FUR, PINK = RAMP["card"], RAMP["spade"], RAMP["fur"], RAMP["pink"]
TWEED, BLUE, GOLD, BARK = RAMP["tweed"], RAMP["blue"], RAMP["gold"], RAMP["bark"]
SOIL, BOTTLE, FLAME, MOON = RAMP["soil"], RAMP["bottle"], RAMP["flame"], RAMP["moon"]
EDGE = 4          # the hedge's depth down each side and along the foot
TOP = 14          # the rows the hedge and its roses take across a header's top


def fills(cells: dict) -> str:
    """Filled paths for {(x, y): colour}, blocks a colour (see `blocks`): the shapes a pattern's tile is drawn in,
    since a browser paints thin strokes inside a pattern poorly when the file asks for crisp edges. A tile every cell
    of which is painted is laid on a ground of its commonest colour, and only the rest drawn over it."""
    by: dict = {}
    for xy, c in cells.items():
        by.setdefault(c, set()).add(xy)
    w, h = max(x for x, _ in cells) + 1, max(y for _, y in cells) + 1
    ground = ""
    if len(cells) == w * h and min(x for x, _ in cells) == 0 and min(y for _, y in cells) == 0:
        c = max(by, key=lambda k: len(by[k]))
        ground = f'<rect width="{w}" height="{h}" fill="{c}"/>'
        del by[c]
    return ground + "".join(f'<path fill="{c}" d="{blocks(cs)}"/>' for c, cs in sorted(by.items()))


def blocks(cells) -> str:
    """Path data filling `cells` as blocks: each row's runs, a run lying the same in the rows under it one block with
    them, so a card drawn a little askew costs a few blocks rather than a stroke a row; every move after the first
    relative to where the last block began."""
    rows: dict = {}
    for (x, y) in cells:
        rows.setdefault(y, []).append(x)
    runs = {}
    for y, xs in rows.items():
        xs.sort()
        out, start, prev = [], xs[0], xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            out.append((start, prev + 1))
            if x is not None:
                start = prev = x
        runs[y] = out
    done, parts, at = set(), [], None
    for y in sorted(runs):
        for run in runs[y]:
            if (y, run) in done:
                continue
            h = 1
            while run in runs.get(y + h, ()):
                done.add((y + h, run))
                h += 1
            a, b = run
            parts.append((f"M{a} {y}" if at is None else f"m{a - at[0]} {y - at[1]}") + f"h{b - a}v{h}h{a - b}z")
            at = (a, y)
    return "".join(parts)


def columns(runs) -> str:
    """Paths for upright runs of colour, [(colour, x, y, height)]: each colour's runs as strokes down the middle of
    their columns, one path a colour, every move after the first relative to where the last run ended."""
    by: dict = {}
    for c, x, y, h in runs:
        if h > 0:
            by.setdefault(c, []).append((x, y, h))
    out = []
    for c, items in by.items():
        d, at = [], None
        for x, y, h in sorted(items):
            d.append(f"M{x + 0.5:g} {y}v{h}" if at is None else f"m{x + 0.5 - at[0]:g} {y - at[1]}v{h}")
            at = (x + 0.5, y + h)
        out.append(f'<path stroke="{c}" d="{"".join(d)}"/>')
    return "".join(out)


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


def sprite(p: Pix, x, y, art, pal, L="base", flip=False):
    """Pixel art from rows of characters, each looked up in `pal`; a character it does not name is left clear."""
    for j, row in enumerate(art):
        for i, ch in enumerate(row[::-1] if flip else row):
            c = pal.get(ch)
            if c:
                p.px(x + i, y + j, c, L)


# --------------------------------------------------------------------------- the page
TILE_W, TILE_H = 30, 22     # the repeat of the flowers printed on the page


def _sprigs(uid: str, night: bool) -> str:
    """The page's print as a pattern tile TILE_W by TILE_H: two small flowers a tile, a daisy of five petals round its
    heart and a sprig of three leaves, printed a tone off the paper by day; by night the garden's own small flowers,
    a tone over the dark."""
    petal, heart, leaf = (GARDEN[5], GARDEN[4], GARDEN[4]) if night else (PAGE[6], PAGE[4], PAGE[4])
    cells = {}
    for cx, cy in ((6, 6), (21, 17)):
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, 1)):
            cells[((cx + dx) % TILE_W, (cy + dy) % TILE_H)] = petal
        cells[(cx, cy)] = heart
    for cx, cy in ((19, 5), (5, 16)):
        for dx, dy in ((0, 0), (-1, -1), (1, -1), (0, 1)):
            cells[((cx + dx) % TILE_W, (cy + dy) % TILE_H)] = leaf
    return (f'<pattern id="{uid}f" width="{TILE_W}" height="{TILE_H}" patternUnits="userSpaceOnUse">'
            f'{fills(cells)}</pattern>')


def band_edges(h: int) -> list:
    """The rows the night's bands change at, down a sheet `h` tall."""
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the storybook's spring page, pale yellow-green with its small printed flowers,
    or by night the indigo garden, deepest overhead; a drawing made lighter to fit its budget leaves the printed
    flowers out, which no one misses at 1x. The drawing keeps which sheet it is and whether it is night."""
    p.sheet, p.night = uid, night
    w, h = p.w, p.h
    if night:
        edges = band_edges(h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                at = f' y="{edges[i]}"' if edges[i] else ""
                p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
    if not p.lite:
        p.defs.append(_sprigs(uid, night))
        p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}f)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the page, or the night's band of the garden there."""
    if not night:
        return C["paper"]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


# --------------------------------------------------------------------------- the hedge
def _leaves(uid: str, night: bool) -> str:
    """The clipped hedge as a pattern tile 12 by 12: small leaves packed close, each lit along its upper left and
    darker at its lower right, deep gaps of shadow between them."""
    k = -2 if night else 0
    rnd = random.Random(12)
    cells = {(x, y): HEDGE[max(0, 1 + k)] for y in range(12) for x in range(12)}
    for _ in range(26):
        cx, cy = rnd.randrange(12), rnd.randrange(12)
        t = rnd.choice((3, 3, 4, 4, 5))
        for dx, dy, dt in ((0, 0, 0), (1, 0, -1), (0, 1, -1), (1, 1, -2), (-1, 0, 1), (0, -1, 1)):
            cells[((cx + dx) % 12, (cy + dy) % 12)] = HEDGE[max(0, min(6, t + dt + k))]
    return f'<pattern id="{uid}" width="12" height="12" patternUnits="userSpaceOnUse">{fills(cells)}</pattern>'


def frame(p: Pix, night: bool):
    """The border: a clipped hedge down each side and along the foot, its leaves packed close, its inner face lit
    where it turns to the light and its shadow on the page inside it."""
    w, h = p.w, p.h
    uid = f"{getattr(p, 'sheet', 'p')}h"
    p.defs.append(_leaves(uid, night))
    p.syms[("leaves", night)] = uid
    sh = p.shapes["base"]
    for x, y, rw, rh in ((0, 0, EDGE, h), (w - EDGE, 0, EDGE, h), (EDGE, h - EDGE, w - 2 * EDGE, EDGE)):
        sh.append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="url(#{uid})"/>')
    k = -2 if night else 0
    sh.append(f'<rect x="{EDGE - 1}" width="1" height="{h - EDGE}" fill="{HEDGE[max(0, 5 + k)]}"/>')
    sh.append(f'<rect x="{w - EDGE}" width="1" height="{h - EDGE}" fill="{HEDGE[max(0, 2 + k)]}"/>')
    sh.append(f'<rect x="{EDGE}" y="{h - EDGE}" width="{w - 2 * EDGE}" height="1" fill="{HEDGE[max(0, 5 + k)]}"/>')
    shade = X["shade_n"] if night else X["shade"]
    sh.append(f'<rect x="{EDGE}" width="1" height="{h - EDGE}" fill="{shade}" fill-opacity=".18"/>')


ROSE_ART = [".aba.", "abcba", "bcdcb", "abcba", ".aba."]   # a rose in bloom, its petals curling to its heart


def rose(p: Pix, x, y, night, painted=1.0, L="base"):
    """A rose 5 wide on the hedge, its top-left at (x, y): red, or a white rose with only the share `painted` of it,
    from the left, painted red, a drip of paint running from it. Each kind is drawn once a file and placed."""
    key = ("rose", painted, night)
    if key not in p.syms:
        k = -2 if night else 0
        red = {"a": ROSE[max(0, 2 + k)], "b": ROSE[max(0, 3 + k)], "c": ROSE[max(0, 4 + k)], "d": ROSE[max(0, 6 + k)]}
        white = {"a": CARD[max(0, 3 + k)], "b": CARD[max(0, 4 + k)], "c": CARD[max(0, 5 + k)],
                 "d": CARD[max(0, 6 + k)]}
        cells = {}
        for j_, row in enumerate(ROSE_ART):
            for i_, ch in enumerate(row):
                if ch in red:
                    cells[(i_, j_)] = (red if i_ < 5 * painted else white)[ch]
        if painted < 1:
            cells[(2, 5)] = ROSE[max(0, 3 + k)]
            cells[(2, 6)] = ROSE[max(0, 2 + k)]
        p.symbol(key, cells)
    p.use(key, x, y, L)


def hedge_top(p: Pix, night: bool, gap=None, motion=False):
    """The deeper hedge across a header's top: its leaves packed close and lit along their upper edges, its foot in
    shade over its shadow on the page, and roses set along it, every third a white rose half painted red with the
    paint still running. `gap` is the span (x0, x1) it parts either side of, the month's mark, each end clipped
    round; None runs it unbroken from side to side."""
    w = p.w
    k = -2 if night else 0
    uid = f"{getattr(p, 'sheet', 'p')}h"
    L = p.layer("hedgetop", z=-1)
    sh = p.shapes[L]
    runs = [(0, w)] if gap is None else [(0, gap[0]), (gap[1], w)]
    shade = X["shade_n"] if night else X["shade"]
    foot = TOP - 2
    for a, b in runs:
        a2, b2 = (a + 3 if a > 0 else a), (b - 3 if b < w else b)
        sh.append(f'<rect x="{a2}" y="0" width="{b2 - a2}" height="{foot}" fill="url(#{uid})"/>')
        sh.append(f'<rect x="{a2}" y="{foot}" width="{b2 - a2}" height="1" fill="{HEDGE[max(0, 1 + k)]}"/>')
        sh.append(f'<rect x="{a}" y="{foot + 1}" width="{b - a}" height="1" fill="{shade}" fill-opacity=".22"/>')
        # The clipped ends, rounded off where the hedge parts: a cap of leaves three columns deep.
        for end, side in (((a, -1),) if a > 0 else ()) + (((b - 1, 1),) if b < w else ()):
            for i in range(3):
                x = end + i if side < 0 else end - i
                inset = (2, 1, 0)[i]
                for y in range(inset, foot + 1 - inset):
                    edge = y in (inset, foot - inset) or i == 0
                    t = (5 if side < 0 else 2) if edge else (4 if (x + y) % 3 else 3)
                    p.px(x, y, HEDGE[max(0, t + k)], L)
        for i, x in enumerate(range(a + 8, b - 7, 13)):
            y = 2 + (i * 5) % 6
            rose(p, x, y, night, 1.0 if i % 3 else 0.5, L)
            for dx, dy in ((-1, 2), (5, 1)):
                p.px(x + dx, y + dy, HEDGE[max(0, 5 + k)], L)


# --------------------------------------------------------------------------- the title: playing cards
PIPS = {
    "heart": ["#.#", "###", ".#."],
    "spade": [".#.", "###", "#.#"],
    "diamond": [".#.", "###", ".#."],
    "club": ["###", "###", ".#."],
}
SUITS = ("heart", "spade", "diamond", "club")
TILTS = (-3.0, 2.5, -1.5, 3.0, -2.5, 1.5)        # how far each card is dealt askew, in degrees, by turns


def _card(cw: int, ch: int, angle: float, night: bool) -> dict:
    """A playing card cw by ch turned `angle` degrees about its middle, as {(x, y): colour} from its unturned top-left:
    its rim, its face of white card, lit along its upper left and a tone deeper along its lower right where its edge
    turns away, its corners rounded."""
    t = math.radians(angle)
    ca, sa = math.cos(t), math.sin(t)
    hx, hy = cw / 2, ch / 2
    r = 2.2
    inside = set()
    pad = 3
    for y in range(-pad, ch + pad):
        for x in range(-pad, cw + pad):
            dx, dy = x + 0.5 - hx, y + 0.5 - hy
            a, b = dx * ca + dy * sa, -dx * sa + dy * ca
            if abs(a) > hx or abs(b) > hy:
                continue
            ex, ey = abs(a) - (hx - r), abs(b) - (hy - r)
            if ex > 0 and ey > 0 and ex * ex + ey * ey > r * r:
                continue
            inside.add((x, y))
    k = -1 if night else 0
    face, lit, deep, rim = CARD[5 + k], CARD[6 + k], CARD[3 + k], CARD[1]
    out = {}
    for (x, y) in inside:
        if any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[(x, y)] = rim
        elif (x + 1, y) not in inside or (x, y + 1) not in inside or \
                ((x + 2, y) not in inside and (x, y + 2) not in inside):
            out[(x, y)] = deep
        elif (x - 1, y) not in inside or (x, y - 1) not in inside:
            out[(x, y)] = lit
        else:
            out[(x, y)] = face
    for (x, y) in list(out):
        if out[(x, y)] != rim and ((x + 1, y + 1) not in inside):
            out[(x, y)] = deep
    return out


def card_title(p: Pix, x, y, s, night, scale, L="base") -> int:
    """A title whose every letter is printed on a playing card (see `_card`): the cards dealt left to right, each a
    little askew and lying over the last, every letter red or black by its suit, hearts and diamonds red and spades
    and clubs black, a small pip of its suit in the card's upper corner. Each card is drawn once a file for each size
    and slant and placed; each letter is the face's own, drawn once and laid on its card. Returns its width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    mx, mt, mb = scale, scale, scale - (2 if scale >= 3 else 1)
    cx, i, placed = x, 0, []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        placed.append((ch, cx, i))
        cx += (glyphs[ch][0] + 1) * scale
        i += 1
    w = cx - x - scale
    rows = 7
    th = rows * scale
    lo = min((lx - mx for ch, lx, _ in placed), default=x) - 1
    hi = max((lx + glyphs[ch][0] * scale + mx for ch, lx, _ in placed), default=x + w) + 1
    for ch, lx, n in placed:
        gw = glyphs[ch][0] * scale
        cw, chh = gw + 2 * mx, th + mt + mb
        angle = TILTS[n % len(TILTS)] if scale >= 3 else 0.0
        key = ("card", cw, chh, angle, night)
        if key not in p.syms:
            p.symbol(key, _card(cw, chh, angle, night))
        p.use(key, lx - mx, y - mt, L)
        suit = SUITS[n % 4]
        red = suit in ("heart", "diamond")
        colour = ROSE[3] if red else SPADE[1]
        gkey = ("glyph", "57", ch)
        if gkey not in p.syms:
            p.symbol(gkey, {(c, r): 1 for r, cols in enumerate(glyphs[ch][1]) for c in cols}, mono=True)
        p.use(gkey, lx, y, L, stroke=colour, scale=scale)
        if scale >= 3:
            pkey = ("pip", suit)
            if pkey not in p.syms:
                p.symbol(pkey, {(i_, j): 1 for j, row in enumerate(PIPS[suit]) for i_, c in enumerate(row) if c == "#"},
                         mono=True)
            t = math.radians(angle)
            ox, oy = -cw / 2 + 2.5, -chh / 2 + 2.5
            px_ = lx - mx + cw / 2 + ox * math.cos(t) - oy * math.sin(t)
            py_ = y - mt + chh / 2 + ox * math.sin(t) + oy * math.cos(t)
            p.use(pkey, round(px_ - 1), round(py_ - 1), L, stroke=colour)
    p.words.append((lo, y - mt - 1, hi, y + th + mb + 1))
    return w


# --------------------------------------------------------------------------- the pack of cards in the air
def _tumbling(p: Pix, night: bool) -> list:
    """The frames of a playing card tumbling through the air, each kept once a file as a symbol: its face turned one
    way, a heart on it, its edge, its back turned the other way, red and latticed inside its white border, and its
    edge again. Returns their ids, in turn."""
    key = ("tumbling", night)
    if key in p.syms:
        return p.syms[key]
    k = -1 if night else 0
    face = _card(8, 11, -18.0, night)
    for j, row in enumerate(PIPS["heart"]):
        for i_, c in enumerate(row):
            if c == "#":
                face[(3 + i_, 4 + j)] = ROSE[3]
    back = _card(8, 11, 14.0, night)
    inside = set(back)
    for (x, y) in list(back):
        if all((x + dx, y + dy) in inside for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
               if abs(dx) + abs(dy) <= 2):
            back[(x, y)] = ROSE[4 + k] if (x + y) % 3 == 0 or (x - y) % 3 == 0 else ROSE[2 + k]
    edge = {}
    for y in range(11):
        x = 3 + round((y - 5) * 0.35)
        edge[(x, y)] = CARD[1]
        edge[(x + 1, y)] = CARD[5 + k]
    ids = [p.symbol(("tumbling", n, night), cells) for n, cells in enumerate((face, edge, back))]
    p.syms[key] = [ids[0], ids[1], ids[2], ids[1]]
    return p.syms[key]


def pack_of_cards(p: Pix, box, night, motion, holes=(), n=14, seed=11):
    """A pack of playing cards tumbling across the sky in the box (x0, y0, x1, y1) on the wind, behind the title and
    never in the boxes `holes` (the month's mark): `n` cards strewn along the sky, the whole pack blown from the left
    to the right and round again every forty seconds, rising and falling a little as it goes, every card turning over
    and over, face, edge, back and edge, every other card half a turn behind the next. The
    pack is drawn once and laid twice, a sheet's width apart, so it comes round without a seam; the still twin holds
    every card face up where it lies when the loop begins."""
    x0, y0, x1, y1 = box
    if y1 - y0 < 16:
        return
    frames = _tumbling(p, night)
    uid = f"{getattr(p, 'sheet', 'p')}pk"
    # Face up for six tenths of a second, edge on for two, face down for six and edge on for two; the second half of
    # the pack half a turn behind the first, face down while it is face up. A still drawing keeps none of it.
    marks = (0, 0.375, 0.5, 0.875, 1)
    for v in range(2 if motion else 0):
        order = frames[v * 2:] + frames[:v * 2]
        uses = []
        for i, sid in enumerate(order):
            a, b = marks[i], marks[i + 1]
            if a == 0:
                vals, kt = "1;0", f"0;{num(b)}"
            elif b == 1:
                vals, kt = "0;1", f"0;{num(a)}"
            else:
                vals, kt = "0;1;0", f"0;{num(a)};{num(b)}"
            uses.append(f'<use href="#{sid}"{" opacity=\"0\"" if i else ""}><animate attributeName="opacity" '
                        f'values="{vals}" keyTimes="{kt}" dur="1.6s" repeatCount="indefinite" calcMode="discrete"/>'
                        f'</use>')
        p.defs.append(f'<g id="{uid}{v}">{"".join(uses)}</g>')
    rnd = random.Random(seed)
    period = x1 - x0 + 16
    lo, hi = y0 + 2, y1 - 13
    spots = []
    for i in range(n):
        x = x0 - 12 + round(period * (i + rnd.uniform(0.1, 0.7)) / n)
        y = round(lo + (hi - lo) * ((i * 7 + 3) % n) / (n - 1))
        spots.append((x, y))
    if motion:
        flock = "".join(f'<use href="#{uid}{i % 2}" x="{x}" y="{y}"/>' for i, (x, y) in enumerate(spots))
        p.defs.append(f'<g id="{uid}f">{flock}</g>')
    cut = [(max(a, x0), max(b, y0), min(c, x1), min(d, y1)) for a, b, c, d in holes]
    clip = f"M{x0} {y0}h{x1 - x0}v{y1 - y0}h{x0 - x1}z" + "".join(
        f"M{a} {b}h{c - a}v{d - b}h{a - c}z" for a, b, c, d in cut if a < c and b < d)
    p.defs.append(f'<clipPath id="{uid}c"><path clip-rule="evenodd" d="{clip}"/></clipPath>')
    wave = ";".join(f"{round(period * j / 4)} {(0, -3, 1, -2, 0)[j]}" for j in range(5))
    moving = (f'<g clip-path="url(#{uid}c)"><g><use href="#{uid}f"/><use href="#{uid}f" x="-{period}"/>'
              f'<animateTransform attributeName="transform" type="translate" values="{wave}" dur="40s" '
              f'repeatCount="indefinite"/></g></g>') if motion else ""
    still = (f'<g clip-path="url(#{uid}c)">'
             + "".join(f'<use href="#{frames[0]}" x="{x}" y="{y}"/>' for x, y in spots) + "</g>")
    p.raw(-1.5, moving or still, still)


# --------------------------------------------------------------------------- the white rabbit
# The White Rabbit after Tenniel, 28 wide and 32 tall, running to the right and looking at the gold watch he holds
# out in front of him, his ears laid back and his coat tails flying: his fur (w, lit W, shaded v, outline o), the
# pink in his ears (p), his eye (e) with its glint (E) and his nose (n), the frilled ruff at his throat (r, shaded R),
# his tweed jacket (j, lit J, its check c, dark k), his blue waistcoat (b, lit B) and its gold buttons (u), and the
# watch on its chain (g, lit G, dark d), its face (f) and hands (h).
RABBIT = [
    "...........o....oo..........",
    "...........oo..oWwo.........",
    "...........ovpooWpo.........",
    "...........ovpooWpo.........",
    "...........ovpooWpo.........",
    "............opooWpo.........",
    "............opooWpo.........",
    "............ovoowpo.........",
    ".............ovoWWWooo......",
    "..............oWWwwwwwo.....",
    "..............oWwwwweeo.....",
    ".............oWwwwwweEwo....",
    ".............oWwwwwvwwwwo...",
    ".............owwwwwwwwvwn...",
    "..............ovvwwwvvvoo...",
    "..............kWvvvvwo......",
    "............orrrrrrrro......",
    "...........kjorRrRrRo.......",
    "...........kjjjcbbB...dGdd..",
    "..........kJjjjjbuBkkdgfff..",
    "..........kjjjjjbbBjcGGfhf..",
    ".........kJjjjjjbuBJkkdffh..",
    "........kjJJjjjjbbBgd..dd...",
    ".......kJccJjjjjbujk........",
    "......kjJJWWJjjjbbk.........",
    ".....kjjcWwwokkkcco.........",
    "......kcWwwo....oWwo........",
    "......oWwwo......owwo.......",
    "....oowwwoo......owwwooooo..",
    "...owwwoo.........owwwwwwwo.",
    "...oooo............oooowwwo.",
    ".......................ooo..",
]


def white_rabbit(p: Pix, x0, g, night, motion):
    """The White Rabbit running and looking at his watch, his feet on the grass at row g from column x0: white fur
    shaded on the moon's cool side, pink in his ears and eyes, a ruff at his throat, his tweed jacket and blue
    waistcoat, and his gold watch on its chain; in a moving header he bounds along, leaping nine units off the grass
    and landing again every two seconds and a bit. Returns his span."""
    k = -1 if night else 0
    pal = {"o": FUR[1], "w": FUR[5 + k], "W": FUR[6 + k], "v": FUR[3 + k], "p": PINK[4 + k], "e": PINK[1],
           "E": C["white"], "n": PINK[3], "r": CARD[6 + k], "R": CARD[4 + k], "j": TWEED[3 + k], "J": TWEED[5 + k],
           "c": TWEED[2 + k], "k": TWEED[1], "b": BLUE[3 + k], "B": BLUE[5 + k], "u": GOLD[5], "g": GOLD[4 + k],
           "G": GOLD[6 + k], "d": GOLD[2], "f": CARD[6 + k], "h": SPADE[1]}
    L = p.layer("hop", ("bob", (0, 0, 0, 0, 3, 6, 8, 9, 8, 6, 3), 2.2), z=0.2) if motion else "base"
    sprite(p, x0, g - len(RABBIT) + 1, RABBIT, pal, L)
    return (x0, x0 + len(RABBIT[0]))


# --------------------------------------------------------------------------- the old tree and the hole
def _code_up(p: Pix, box, night, motion, n=0, seed=4):
    """The code glowing up out of the rabbit hole: streams of the rain's glyphs rising from it, each led upward by a
    white-hot glyph with its trail fading down behind it to the hole, stepping up a glyph every 0.12 seconds, drawn
    once and laid twice so the loop never shows its seam; faint by day and bright by night, clipped to the box it
    rises in, and held where its loop begins in the still twin."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    tones = (FLAME[6], FLAME[5], FLAME[4], FLAME[3], FLAME[3], FLAME[2], FLAME[2], FLAME[1]) if night else \
        (FLAME[3], FLAME[2], FLAME[2], FLAME[1], FLAME[1], FLAME[1], FLAME[0], FLAME[0])
    loop = ((y1 - y0) // rain.PITCH + 5) * rain.PITCH
    by: dict = {}
    for gx in range(x0, x1 - rain.W + 1, rain.COLUMN):
        for start in (rnd.randrange(loop // rain.PITCH),):
            head = start * rain.PITCH
            for j in range(rnd.randint(4, 6)):
                c = tones[min(j, len(tones) - 1)]
                gy = y0 + (head + j * rain.PITCH) % loop
                sid = p.syms[rain.symbol(p, rnd.choice(rain.NAMES))]
                by.setdefault(c, []).append(f'<use href="#{sid}" x="{gx}" y="{gy}"/>')
    inner = "".join(f'<g stroke="{c}">{"".join(us)}</g>' for c, us in by.items())
    uid = f"{getattr(p, 'sheet', 'p')}u{n}"
    p.defs.append(f'<clipPath id="{uid}c"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'
                  f'<g id="{uid}g">{inner}</g>')
    copies = f'<use href="#{uid}g"/><use href="#{uid}g" y="{loop}"/>'
    steps = loop // rain.PITCH
    values = ";".join(f"0 {-i * rain.PITCH}" for i in range(steps))
    # The code thins as it rises: a mask of bands, each a step fainter than the one under it.
    n_bands, h = 5, y1 - y0
    bands = "".join(f'<rect x="{x0}" y="{y0 + h * i // n_bands}" width="{x1 - x0}" height="{h // n_bands + 1}" '
                    f'fill="{C["white"]}" fill-opacity="{num((i + 1) / n_bands * (1 if night else 0.6))}"/>'
                    for i in range(n_bands))
    p.defs.append(f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{x1 - x0}" height="{h}">'
                  f'{bands}</mask>')
    p.raw(-0.6, f'<g clip-path="url(#{uid}c)" mask="url(#{uid}m)"><g>{copies}<animateTransform '
                f'attributeName="transform" type="translate" values="{values}" dur="{num(steps * 0.12)}s" '
                f'repeatCount="indefinite" calcMode="discrete"/></g></g>',
          f'<g clip-path="url(#{uid}c)" mask="url(#{uid}m)">{copies}</g>')


def toadstool(p: Pix, x, g, night, h=6, w=7):
    """A toadstool on the grass at row g from column x, `w` wide and `h` tall: its red cap lit along its crown and
    spotted white, its pale stem under it."""
    k = -2 if night else 0
    cap = ellipse(x + w / 2, g - h + 2, w / 2, 2.4)
    for (cx, cy) in cap:
        if cy > g - h + 2:
            continue
        lam = light((cx + 0.5 - x - w / 2) / w * 2, (cy - (g - h)) / 3 - 0.5, 0.6)
        p.px(cx, cy, ROSE[max(0, min(6, 2 + round(3 * lam) + k))])
    for sx, sy in ((x + 1, g - h + 1), (x + w // 2, g - h), (x + w - 2, g - h + 1)):
        p.px(sx, sy, CARD[max(0, 6 + k)])
    p.hline(x + 1, x + w - 1, g - h + 3, ROSE[max(0, 1 + k)])
    for yy in range(g - h + 3, g + 1):
        p.px(x + w // 2 - 1, yy, CARD[max(0, 5 + k)])
        p.px(x + w // 2, yy, CARD[max(0, 3 + k)])


def bottle(p: Pix, x, g, night):
    """The little bottle on the grass at row g from column x, 5 wide and 9 tall: its glass lit down its left side,
    its cork, and the paper tag tied to its neck by a thread, which says DRINK ME in a hand too small to read."""
    k = -1 if night else 0
    for yy in range(g - 5, g + 1):
        for xx in range(x, x + 5):
            t = 5 if xx == x + 1 else 3 if xx < x + 4 else 1
            if xx in (x, x + 4) and yy in (g - 5, g):
                continue
            p.px(xx, yy, BOTTLE[max(0, t + k)])
    p.vline(x + 2, g - 7, g - 5, BOTTLE[max(0, 4 + k)])
    p.px(x + 2, g - 8, TWEED[max(0, 4 + k)])
    p.px(x + 2, g - 9, TWEED[max(0, 3 + k)])
    p.px(x + 3, g - 7, CARD[2])
    p.rect(x + 4, g - 7, 4, 3, CARD[max(0, 6 + k)])
    p.hline(x + 5, x + 7, g - 6, SPADE[3])


# The Cheshire Cat after Tenniel, 11 wide and 12 tall, sitting on the bough and grinning: a tabby (s, its stripes d,
# outline k), its eyes (e), its grin of teeth (t); and the grin alone, which is what is left of him by night.
CAT = [
    "..k.....k..",
    ".kdk...kdk.",
    ".ksskkkssk.",
    "ksdssdssdsk",
    "kseesssseek",
    "kstttttttsk",
    ".kkttttttk.",
    "..kksssskk.",
    ".ksdsdsdssk",
    "ksdsdsdsdsk",
    "ksssdsdsssk",
    ".kkkkkkkkk.",
]
GRIN = ["...........", "...........", "...........", "...........", "..e.....e..", ".t.......t.",
        "..ttttttt..", "...ttttt..."]


def _crown(p: Pix, blobs, night, uid, L, top):
    """A crown of spring leaves made of the round clusters `blobs`, (cx, cy, rx, ry) each: filled with the hedge's
    leaf pattern `uid` under a wash of spring's lighter green, lit along the upper left of each cluster and darker
    along its foot, blossom here and there."""
    k = -2 if night else 0
    cells, parts = set(), []
    for cx, cy, rx, ry in blobs:
        blob = {(x, y) for (x, y) in ellipse(cx, cy, rx, ry) if y >= top}
        parts.append((blob, cx, cy, rx, ry))
        cells |= blob
    p.defs.append(f'<path id="{uid}c" d="{blocks(cells)}"/>')
    p.shapes[L].append(f'<use href="#{uid}c" fill="url(#{uid})"/><use href="#{uid}c" fill="{HEDGE[6]}" '
                       f'fill-opacity="{".2" if night else ".24"}"/>')
    blossom = (CARD[max(0, 6 + k)], PINK[max(0, 5 + k)])
    for blob, cx, cy, rx, ry in parts:
        for (x, y) in blob:
            up, left_, down = (x, y - 1) not in cells, (x - 1, y) not in cells, (x, y + 1) not in cells
            if up or (left_ and y < cy):
                p.px(x, y, HEDGE[max(0, 6 + k)], L)
            elif down:
                p.px(x, y, HEDGE[max(0, 1 + k)], L)
        for bx, by, bb in ((cx - rx * 0.4, cy - ry * 0.2, 0), (cx + rx * 0.35, cy - ry * 0.45, 1),
                           (cx + rx * 0.05, cy + ry * 0.3, 0)):
            if (round(bx), round(by)) in cells:
                p.px(round(bx), round(by), blossom[bb], L)


def tree(p: Pix, x0, x1, g, night, motion, reach=None, top=TOP) -> tuple:
    """The right of the page, standing on the grass at row g from column x0 to x1: an old tree, its gnarled trunk
    rising out of the sheet at the right on buttress roots, its bark furrowed and lit down its left side, a knot in
    it, a crown of spring leaves and blossom spreading out over the page from a bough, on which the Cheshire Cat sits
    grinning by day, and by night only his grin, the cat coming and going round it in a moving header; a great root
    arches over the rabbit hole at its foot, out of which the code glows up (see `_code_up`), green in the hole's depths
    by night and its light pooled round the hole and lying on the roots and on everything that stands by it, with
    toadstools beside it and the little bottle with its tag. Over the words' rows its bough and crown reach no further
    left than column `reach`; it rises from row `top`. Returns its span."""
    k = -2 if night else 0
    reach = x0 if reach is None else reach
    tx0, tx1 = x1 - 23, x1
    T = p.layer("trunk", z=-0.4)
    sh = p.shapes[T]

    def left(y):
        f = (g - y) / (g - top)
        return tx0 + round(6 * f) - round(9 * max(0.0, (y - (g - 16)) / 16) ** 2)
    first = {}
    for y in range(top, g + 1):
        for x in range(left(y), tx1):
            first.setdefault(x, y)
    runs = []
    for x, y0 in sorted(first.items()):
        u = (x - tx0) / (tx1 - tx0)
        t = 4 if u < 0.28 else 3 if u < 0.62 else 2
        runs.append((BARK[max(0, t + k)], x, y0, g + 1 - y0))
    sh.append(columns(runs))
    runs = []
    rnd = random.Random(3)
    for fx in sorted(rnd.sample(range(tx0 + 7, tx1 - 1), 5)) if not p.lite else ():
        y = top
        while y < g - 4:
            n = rnd.randint(8, 22)
            y0 = max(y, first.get(fx, y))
            n = min(n, g + 1 - y0)
            if n > 0:
                runs.append((BARK[max(0, 1 + k)], fx, y0, n))
                runs.append((BARK[max(0, 4 + k)], fx - 1, y0, max(1, n - 3)))
            y += n + rnd.randint(3, 8)
    sh.append(columns(runs))
    for y in range(top, g + 1):
        a = left(y)
        p.px(a, y, BARK[max(0, 5 + k)], T)
        p.px(a - 1, y, BARK[0], T)
    knot = ellipse(tx0 + 12, top + 40, 2.5, 3.5)
    for (x, y) in knot:
        p.px(x, y, BARK[0] if (x, y + 1) in knot and (x - 1, y) in knot else BARK[max(0, 5 + k)], T)
    # The bough reaching out to the left, and the crown of spring leaves over it.
    by0 = top + 12
    for x in range(max(x0 + 6, reach + 1), tx0 + 6):
        yy = by0 - round(((tx0 + 6 - x) / (tx0 - x0)) ** 1.5 * 6)
        p.px(x, yy, BARK[max(0, 5 + k)])
        p.px(x, yy + 1, BARK[max(0, 3 + k)])
        p.px(x, yy + 2, BARK[0])
    uid = p.syms.get(("leaves", night))
    if uid is None:
        uid = p.syms[("leaves", night)] = f"{getattr(p, 'sheet', 'p')}h"
        p.defs.append(_leaves(uid, night))
    blobs = ((x0 + 6, by0 - 6, 6, 4), (x0 + 16, by0 - 9, 8, 5), (x0 + 28, by0 - 8, 8, 5.5),
             (tx0 + 6, by0 - 10, 12, 7), (x0 + 11, by0, 6, 3.4), (x0 + 22, by0 - 1, 6, 3.2), (x1 - 4, by0 - 2, 6, 6))
    _crown(p, [b for b in blobs if b[0] - b[2] >= reach], night, uid, p.layer("crown", z=-0.3), top)
    if x0 + 14 >= reach:
        cx, cy = x0 + 14, by0 - 11
        pal = {"k": TWEED[0], "s": TWEED[max(0, 4 + k)], "d": TWEED[max(0, 2 + k)], "e": GOLD[5], "t": CARD[6]}
        if not night:
            sprite(p, cx, cy, CAT, pal)
            for x in range(cx + 9, cx + 12):
                p.px(x, cy + 12 + (x - cx - 9), TWEED[3])
            p.px(cx + 11, cy + 15, TWEED[3])
            p.px(cx + 10, cy + 16, TWEED[2])
        else:
            sprite(p, cx, cy, GRIN, {"e": GOLD[5], "t": CARD[6]}, p.layer("grin", z=0.5))
            if motion:
                sprite(p, cx, cy, CAT, pal, p.seq("cat", 0.1, 0.4, 8.0, z=0.45))
    # The great root arching over the hole, the hole itself, glowing green in its depths by night, and the lesser
    # roots.
    hx0, hx1 = x0 + 11, x0 + 31
    cx = (hx0 + hx1) / 2
    hole = ellipse(cx, g + 2, (hx1 - hx0) / 2, 12)
    for (x, y) in hole:
        if y <= g:
            d = abs(x + 0.5 - cx) / ((hx1 - hx0) / 2) + max(0, (g - 6 - y)) * 0.05
            if night:
                p.px(x, y, FLAME[2] if d < 0.3 and y > g - 4 else FLAME[1] if d < 0.45 else FLAME[0] if d < 0.62
                     else SOIL[1] if d < 0.8 else SOIL[2])
            else:
                p.px(x, y, SOIL[0] if d < 0.55 else SOIL[1] if d < 0.8 else SOIL[2])
    span = hx1 - hx0 + 8
    for i in range(span + 1):
        x = hx0 - 4 + i
        y = g - round(11 * math.sin(math.pi * i / span)) - 1
        for dy, t in ((0, 5), (1, 4), (2, 2), (3, 1)):
            if y + dy <= g:
                p.px(x, y + dy, BARK[max(0, t + k)])
    for x in range(hx1 + 3, tx0 - 2):
        yy = g - 2 - round(4 * (x - hx1) / max(1, tx0 - hx1))
        for dy, t in ((0, 4), (1, 3), (2, 1)):
            p.px(x, yy + dy, BARK[max(0, t + k)])
    # The code rising out of the hole, the toadstools and the bottle; and the code's light pooled round the hole on
    # the trunk and the grass, and lying on the roots and on everything that stands by it, brightest by night; a
    # drawing made lighter leaves out the faint outer ring of that light, as it leaves out the bark's furrows.
    _code_up(p, (hx0, max(top, g - 58), hx1 + 1, g - 2), night, motion)
    toadstool(p, x0 + 1, g, night, h=9, w=8)
    toadstool(p, x0 + 6, g, night, h=5, w=5)
    bottle(p, hx1 + 5, g, night)
    uid = f"{getattr(p, 'sheet', 'p')}hg"
    p.defs.append(f'<clipPath id="{uid}"><rect x="{x0 - 8}" y="{g - 40}" width="{x1 - x0 + 8}" height="41"/>'
                  f'</clipPath>')
    rings = ((26, 16, ".12"), (15, 9, ".2"), (8, 5, ".28")) if night else ((18, 10, ".08"), (9, 5, ".12"))
    glow = (f'<g clip-path="url(#{uid})">' + "".join(f'<ellipse cx="{num(cx)}" cy="{g}" rx="{rx}" ry="{ry}" '
                                                     f'fill="{FLAME[3]}" fill-opacity="{a}"/>' for rx, ry, a in rings)
            + "</g>")
    p.raw(-0.35, glow, glow)
    lit = {BARK[max(0, t + k)] for t in range(7)} | {SOIL[1], SOIL[2]} | \
        {ROSE[max(0, t - 2)] for t in range(7)} | {CARD[max(0, t - 2)] for t in range(7)} | \
        {BOTTLE[max(0, t + k)] for t in range(7)}
    rings = ((0.12, 0.26, 0.42) if night else (0.06, 0.12)) if not p.lite else ((0.26, 0.42) if night else (0.12,))
    p.halo(cx, g - 3, 20 * len(rings) / (3 if night else 2), 13 * len(rings) / (3 if night else 2), FLAME[4], rings,
           L="base", only=lit)
    return (x0 - 1, x1 + 1)


def fallen_cards(p: Pix, x0, g, night):
    """Three playing cards fallen in the grass at row g from column x0, a trail of them leading to the hole, each
    lying askew where it fell, a pip of its suit on its face. Each is drawn as the title's cards are (see `_card`)."""
    for i, (dx, suit, angle) in enumerate(((0, "heart", -14.0), (12, "club", 9.0), (23, "diamond", -6.0))):
        key = ("card", 7, 9, angle, night)
        if key not in p.syms:
            p.symbol(key, _card(7, 9, angle, night))
        x, y = x0 + dx, g - 8 + (i % 2)
        p.use(key, x, y)
        pkey = ("pip", suit)
        if pkey not in p.syms:
            p.symbol(pkey, {(i_, j_): 1 for j_, row in enumerate(PIPS[suit]) for i_, c in enumerate(row) if c == "#"},
                     mono=True)
        p.use(pkey, x + 2, y + 3, stroke=ROSE[3] if suit in ("heart", "diamond") else SPADE[1])


# --------------------------------------------------------------------------- the grass, the eggs and the night
def meadow(p: Pix, x0, x1, g, night, seed=2):
    """The grass along the foot of the page from column x0 to x1 at row g, as a pattern tile 24 wide: blades lit at
    their tips, and among them small spring flowers, daisies and bluebells."""
    k = -2 if night else 0
    rnd = random.Random(seed)
    cells = {}
    for x in range(24):
        cells[(x, 3)] = HEDGE[max(0, 2 + k)]
        if rnd.random() < 0.7:
            cells[(x, 2)] = HEDGE[max(0, rnd.choice((3, 4, 4, 5)) + k)]
        if rnd.random() < 0.3:
            cells[(x, 1)] = HEDGE[max(0, 5 + k)]
    for fx, c in ((5, CARD[max(0, 6 + k)]), (17, BLUE[max(0, 5 + k)]), (11, CARD[max(0, 6 + k)])):
        cells[(fx, 0)] = c
        cells[(fx, 1)] = HEDGE[max(0, 4 + k)]
    uid = f"{getattr(p, 'sheet', 'p')}g"
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{g - 3}" width="24" height="4" patternUnits="userSpaceOnUse">'
                  f'{fills(cells)}</pattern>')
    p.shapes[p.layer("meadow", z=-0.5)].append(f'<rect x="{x0}" y="{g - 3}" width="{x1 - x0}" height="4" '
                                               f'fill="url(#{uid})"/>')


def egg(p: Pix, x, g, night, ramp, band):
    """An Easter egg in the grass at row g from column x, 4 wide and 5 tall: painted, lit at its upper left, a band of
    another colour round its middle."""
    k = -1 if night else 0
    cells = ellipse(x + 2, g - 2, 2, 2.6)
    for (cx, cy) in cells:
        if cy > g:
            continue
        lam = light(cx + 0.5 - x - 2, cy + 0.5 - g + 2, 1.2)
        c = ramp[max(0, min(6, 2 + round(4 * lam) + k))]
        if cy == g - 2:
            c = band[max(0, 4 + k)]
        p.px(cx, cy, c)


def night_sky(p: Pix, box, motion, avoid=()):
    """The night over the garden in the box (x0, y0, x1, y1): the code showing through it as stars, a few twinkling,
    and now and then a glyph, faint; none in the boxes `avoid`. A drawing made lighter leaves out the faintest, the
    single dim units, and keeps every star that twinkles and every glyph."""
    x0, y0, x1, y1 = box
    before = set(p.layers["haze"])
    rain.stars(p, x0, y0, x1, y1, max(4, (x1 - x0) * (y1 - y0) // 160), FLAME, seed=6, twinkling=motion,
               avoid=avoid)
    if p.lite:                                      # the faint single stars go; the twinkling ones and glyphs stay
        for xy in set(p.layers["haze"]) - before:
            if p.layers["haze"][xy] == FLAME[1]:
                del p.layers["haze"][xy]


def moon(p: Pix, cx, cy, r=5):
    """The hand's moon over the garden, a round of its pale ramp lit from the upper left, with its glow round it,
    whose faint outer ring a drawing made lighter leaves out."""
    from ...holidays.pixel import sphere
    sphere(p, cx, cy, r, MOON, lo=2, hi=6)
    if p.lite:
        p.halo(cx, cy, r * 2.6 * 2 / 3, r * 2.6 * 2 / 3, MOON[4], (0.08, 0.12))
    else:
        p.halo(cx, cy, r * 2.6, r * 2.6, MOON[4], (0.04, 0.08, 0.12))


def fireflies(p: Pix, box, motion, n=7, seed=8):
    """Fireflies over the grass in the box (x0, y0, x1, y1): sparks of phosphor that come and go by turns, each with a
    soft glow either side of it, which a drawing made lighter leaves out."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        L = p.twinkle(i) if motion else "base"
        p.px(x, y, FLAME[5], L)
        if not p.lite:
            p.apx(x - 1, y, FLAME[3], 0.4, L)
            p.apx(x + 1, y, FLAME[3], 0.4, L)


def rose_arch(p: Pix, x0, x1, spring, g, night):
    """An arch of trellis grown over with leaves and roses from column x0 to x1, its posts rising from the grass at
    row g to its spring at row `spring` and a round head over them: the leaves packed close, lit on the upper left of
    the arch and in shade on its lower right, roses set along it, every third a white rose half painted red."""
    k = -2 if night else 0
    cx = (x0 + x1) / 2
    R = (x1 - x0) / 2
    band = 5
    cells = set()
    for y in range(round(spring - R) - 1, g + 1):
        for x in range(x0, x1):
            if y <= spring:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - spring)
                if R - band <= d <= R:
                    cells.add((x, y))
            elif x < x0 + band or x >= x1 - band:
                cells.add((x, y))
    for (x, y) in cells:
        dx, dy = x + 0.5 - cx, y + 0.5 - min(y, spring)
        d = math.hypot(dx, dy) or 1
        outer = (x, y - 1) not in cells or ((x - 1, y) not in cells and x < cx)
        inner = (x, y + 1) not in cells or ((x + 1, y) not in cells and x < cx) or ((x - 1, y) not in cells and x > cx)
        lam = light(dx / d, dy / d, 0.8) if y <= spring else (0.7 if x < cx else 0.35)
        t = 2 + round(3 * lam)
        if inner:
            t -= 1
        if outer and lam > 0.4:
            t += 1
        p.px(x, y, HEDGE[max(0, min(6, t + k))])
    n = 0
    for i in range(0, 181, 22):
        t = math.radians(180 + i)
        rx, ry = cx + (R - band / 2) * math.cos(t), spring + (R - band / 2) * math.sin(t)
        rose(p, round(rx - 2.5), round(ry - 2.5), night, 1.0 if n % 3 else 0.5)
        n += 1
    for y in range(spring + 8, g - 4, 11):
        for x in (x0, x1 - band):
            rose(p, x, y, night, 1.0 if (y // 11) % 2 else 0.5)


def tulips(p: Pix, x, g, night, colours, n=3):
    """A clump of `n` spring tulips on the grass at row g from column x: each a cup of petals lit on its left, on a
    stem with a long leaf, a little taller or shorter than the next."""
    k = -2 if night else 0
    for i in range(n):
        tx = x + i * 3
        h = (9, 12, 10, 8)[i % 4]
        ramp = colours[i % len(colours)]
        for y in range(g - h + 3, g + 1):
            p.px(tx + 1, y, HEDGE[max(0, 3 + k)])
        p.px(tx + (2 if i % 2 else 0), g - 2, HEDGE[max(0, 5 + k)])
        p.px(tx + (2 if i % 2 else 0), g - 3, HEDGE[max(0, 4 + k)])
        cup = [(0, 0, 4), (2, 0, 3), (0, 1, 5), (1, 1, 4), (2, 1, 2), (0, 2, 4), (1, 2, 3), (2, 2, 2)]
        for dx, dy, t in cup:
            p.px(tx + dx, g - h + dy, ramp[max(0, t + k)])


def butterfly(p: Pix, path, motion, n=0):
    """A butterfly fluttering round the page by day on a slow loop, its wings up and down by turns, the stillness
    holding it where its path begins."""
    up = ("bfly", n, 0)
    down = ("bfly", n, 1)
    wing, body = PINK[4], SPADE[2]
    if up not in p.syms:
        p.symbol(up, {(0, 0): wing, (1, 0): wing, (3, 0): wing, (4, 0): wing, (0, 1): wing, (1, 1): PINK[2],
                      (2, 1): body, (3, 1): PINK[2], (4, 1): wing, (2, 2): body})
        p.symbol(down, {(1, 1): PINK[2], (2, 1): body, (3, 1): PINK[2], (0, 2): wing, (1, 2): wing, (2, 2): body,
                        (3, 2): wing, (4, 2): wing})
    if motion:
        p.fly([up, down], path, 32.0, z=16, flap=0.18)
    else:
        p.use(up, path[0][0], path[0][1], "near")


# --------------------------------------------------------------------------- the caterpillar on the mushroom
# The Caterpillar after Tenniel, 30 wide and 33 tall, sitting up on the mushroom with his two pairs of arms folded
# and the hookah's mouthpiece at his lips, facing right toward it, his tail coiled along the cap: his blue body ringed
# into segments (b, lit B and W, shaded d and D, outline o), his eye (e), his folded arms (a, shaded A), the gold
# mouthpiece (g, lit G) and his little feet (k).
CATERPILLAR = [
    "........oooooo................",
    ".......oWWBBbbo...............",
    "......oWBBbbbbbo..............",
    ".....oWBbbbbbbbbo.............",
    ".....oBbbbbbbbbbbo............",
    ".....oBbbbbebbbbbbo...........",
    ".....oBbbbbbbbbbbbbo..........",
    ".....obbbbbbbbbbbbbbo.........",
    "......obbbbbbbbbbbogGG........",
    ".......odbbbbbbbdo............",
    "........oddddddo..............",
    ".......oBbbbbbbbo.............",
    "......oBbbbbbbbbdo............",
    "......oBaaaaaaabdo............",
    "......oBAAAAAAAbdo............",
    "......obbbbbbbbbdo............",
    ".......odbbbbbbdo.............",
    ".......oBbbbbbbbo.............",
    "......oBbbbbbbbbdo............",
    "......oBaaaaaaabdo............",
    "......oBAAAAAAAbdo............",
    "......obbbbbbbbbdo............",
    ".......odbbbbbbdo.............",
    ".......oBbbbbbbbo.............",
    "......oBbbbbbbbbbo............",
    ".....oBbbbbbbbbbbdo...........",
    "....oBbbbbbbbbbbbbdoooooo.....",
    "...oBbbbbbbbbbbbbbbdoBBBbo....",
    "...obbbbbbbbbbbbbbbbbbbbbbo...",
    "...odbbbbbdbbbbbbdbbbbbdbbdo..",
    "...oDdbbbdDbbbbbdDbbbbdDbbdo..",
    "....oDDDDDoDDDDDDoDDDDDDDDo...",
    ".....k.k.k..k.k.k..k.k.k.k....",
]
# The hookah on the mushroom's cap, 14 wide and 19 tall: the coal in its bowl (r, glowing), the gold bowl, neck and
# foot (g, lit G, shaded n), and its glass belly of water (l, lit L, its gleam w, shaded s), the hose's joint (h).
HOOKAH = [
    ".....rrr......",
    "....gGGGg.....",
    "....ngggn.....",
    ".....nGn......",
    "......Gg......",
    "......gn......",
    "......Gg......",
    ".....gGgn.....",
    "....lLLLLl....",
    "...lLwwLLll...",
    "..lLwwLLlllh..",
    "..lLwLLllllh..",
    "..lLLLllllls..",
    "..llllllllss..",
    "...llllllss...",
    "....lsssss....",
    ".....gGGn.....",
    "....gGGGGn....",
    "...gGGGGGGn...",
]


def mushroom(p: Pix, cx, g, night, rw, cap_y, ch=18, stem_w=18, L="base") -> set:
    """The giant mushroom standing on the grass at row g, centred on column cx: a domed cap `rw` units either side of
    its middle and `ch` tall, its crown at row `cap_y`, red and spotted white, lit along its upper left and in shade
    along its rim; the pale gills under its rim; and its stem, stout and pale, lit down its left side, in the cap's
    shadow at its top, a ragged ring of skirt under the cap and its foot swelling into the grass. Returns the cap's
    cells."""
    k = -2 if night else 0
    cap = {(x, y) for (x, y) in ellipse(cx, cap_y + ch, rw, ch) if y <= cap_y + ch - 3}
    for (x, y) in cap:
        lam = light((x + 0.5 - cx) / rw, (y + 0.5 - cap_y - ch) / ch, 0.55)
        edge = (x, y + 1) not in cap
        t = 1 if edge else 2 + round(4 * lam ** 0.9)
        p.px(x, y, ROSE[max(0, min(6, t + k))], L)
    rnd = random.Random(int(cx) * 3 + int(rw))
    spots = [(-0.55, -0.35, 2.6), (-0.15, -0.75, 2.2), (0.3, -0.5, 3.0), (0.72, -0.2, 2.0), (-0.85, -0.05, 1.6),
             (0.05, -0.25, 1.8), (0.55, -0.85, 1.5), (-0.4, -0.85, 1.4), (0.92, -0.05, 1.3), (-0.62, -0.62, 1.3)]
    for fx, fy, size in spots:                      # the spots, round and white, smaller toward the rim
        sx, sy = cx + fx * rw, cap_y + ch + fy * ch + rnd.uniform(-0.6, 0.6)
        for (x, y) in ellipse(sx, sy, size * 1.25, size * 0.8):
            if (x, y) in cap and (x, y + 1) in cap:
                lit = (x + 0.5 - sx) * LX + (y + 0.5 - sy) * LY > 0.15
                p.px(x, y, CARD[max(0, (6 if lit else 4) + k)], L)
    rim = cap_y + ch - 3
    xs = [x for (x, y) in cap if y == rim]
    a, b = min(xs), max(xs)
    for x in range(a + 2, b - 1):                   # the gills under the rim, in shade
        p.px(x, rim + 1, CARD[max(0, 2 + k)] if x % 2 else CARD[max(0, 3 + k)], L)
        if a + 6 < x < b - 5:
            p.px(x, rim + 2, CARD[max(0, 1 + k)] if x % 3 else CARD[max(0, 2 + k)], L)
    s0 = cx - stem_w // 2
    for y in range(rim + 2, g + 1):
        flare = max(0, (y - (g - 7))) * 2 // 3
        for x in range(s0 - flare, s0 + stem_w + flare):
            u = (x - (s0 - flare)) / max(1, stem_w + 2 * flare - 1)
            t = 6 if u < 0.12 else 5 if u < 0.42 else 4 if u < 0.72 else 3 if u < 0.9 else 2
            if y < rim + 5:
                t -= 2                               # the stem in the cap's shadow
            if x in (s0 - flare, s0 + stem_w + flare - 1):
                t = 1 if x > cx else max(t - 1, 2)
            p.px(x, y, CARD[max(0, t + k)], L)
    for x in range(s0 - 2, s0 + stem_w + 2):        # the skirt, its ragged hem
        p.px(x, rim + 6, CARD[max(0, 5 + k)] if x < cx else CARD[max(0, 3 + k)], L)
        p.px(x, rim + 7, CARD[max(0, 4 + k)] if x < cx else CARD[max(0, 2 + k)], L)
        if x % 3:
            p.px(x, rim + 8, CARD[max(0, 2 + k)] if x < cx else CARD[max(0, 1 + k)], L)
    return cap


def _rings(p: Pix, box, mouth, night, motion, seed=5, n=0):
    """The smoke of the hookah rising from the Caterpillar's lips in the box (x0, y0, x1, y1): rings of smoke, a glyph
    of the code rising between them, drifting up and to the left and thinning as they rise, a soft green by day and
    bright phosphor by night; in a moving header they rise a step every half second round a six-second loop, drawn
    once and laid twice so the loop never shows its seam, and the still twin holds them where the loop begins."""
    x0, y0, x1, y1 = box
    if y1 - y0 < 18:
        return
    mx, my = mouth
    rnd = random.Random(seed)
    tones = ((FLAME[6], FLAME[5]), (FLAME[5], FLAME[4]), (FLAME[4], FLAME[3])) if night else \
        ((FLAME[1], FLAME[2]), (FLAME[2], FLAME[3]), (FLAME[2], FLAME[3]))
    loop = 48
    by: dict = {}
    uses: dict = {}
    for i in range(7):
        up = i * 8 + rnd.randrange(2)
        cx = mx - 4 - round(up * 0.45) + (i % 2) * 3 - 1
        cy = my - 5 - up
        rx = 3.2 + 0.6 * (i % 3) + i * 0.25
        ry = rx * 0.62
        dark, lit = tones[min(2, i // 3)]
        outer = ellipse(cx, cy, rx + 0.7, ry + 0.7)
        hole = ellipse(cx, cy, rx - 0.7, ry - 0.6)
        for (x, y) in outer - hole:
            upper = (x + 0.5 - cx) * LX + (y + 0.5 - cy) * LY > 0
            by.setdefault(lit if upper else dark, set()).add((x, y))
        if i % 2 == 1:
            sid = p.syms[rain.symbol(p, rnd.choice(rain.NAMES))]
            uses.setdefault(lit, []).append(f'<use href="#{sid}" x="{cx + round(rx) + 2}" y="{cy - 3}"/>')
    inner = "".join(f'<path stroke="{c}" d="{p._d(_rows(v))}"/>' for c, v in by.items())
    inner += "".join(f'<g stroke="{c}">{"".join(v)}</g>' for c, v in uses.items())
    uid = f"{getattr(p, 'sheet', 'p')}k{n}"
    h = y1 - y0
    p.defs.append(f'<clipPath id="{uid}c"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{h}"/></clipPath>'
                  f'<g id="{uid}g">{inner}</g>')
    bands = "".join(f'<rect x="{x0}" y="{y0 + 4 * i}" width="{x1 - x0}" height="{4 if i < 3 else h - 12}" '
                    f'fill="{C["white"]}" fill-opacity="{num((i + 1) / 4)}"/>' for i in range(4))
    p.defs.append(f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{x1 - x0}" height="{h}">'
                  f'{bands}</mask>')
    copies = f'<use href="#{uid}g"/><use href="#{uid}g" x="{round(loop * 0.45)}" y="{loop}"/>'
    steps = 12
    values = ";".join(f"{-round(i * 4 * 0.45)} {-i * 4}" for i in range(steps))
    p.raw(-0.6, f'<g clip-path="url(#{uid}c)" mask="url(#{uid}m)"><g>{copies}<animateTransform '
                f'attributeName="transform" type="translate" values="{values}" dur="6s" repeatCount="indefinite" '
                f'calcMode="discrete"/></g></g>',
          f'<g clip-path="url(#{uid}c)" mask="url(#{uid}m)">{copies}</g>')


def _rows(cells) -> dict:
    """{y: [x, ...]} for a set of cells, the shape `Pix._d` writes a path from."""
    out: dict = {}
    for (x, y) in cells:
        out.setdefault(y, []).append(x)
    return out


def foxglove(p: Pix, x, g, night, h=26, L="base"):
    """A foxglove on the grass at row g, column x its stem: a spike `h` tall hung thick with pink bells along its
    upper half, each bell lit on its upper left with a dark speckled mouth, the bells smaller toward the tip, and broad
    leaves at its foot."""
    k = -2 if night else 0
    for y in range(g - h, g + 1):
        p.px(x, y, HEDGE[max(0, 3 + k)], L)
    for dx, dy, t in ((-1, 0, 4), (-2, 0, 4), (-3, -1, 5), (-4, -1, 4), (1, 0, 2), (2, 0, 2), (3, -1, 3), (4, -1, 2),
                      (-2, -1, 3), (2, -1, 1), (-1, -2, 5), (1, -2, 3), (-3, 0, 3), (3, 0, 1)):
        p.px(x + dx, g + dy, HEDGE[max(0, t + k)], L)
    bells = list(range(g - h + 1, g - h // 3, 2))
    for i, y in enumerate(bells):
        side = 1 if i % 2 == 0 else -1
        size = 1 if i < 2 else 2 if i < 4 else 3
        for j in range(size):
            bx = x + side * (1 + j)
            p.px(bx, y, PINK[max(0, (5 if j == 0 else 4) + k)], L)
            p.px(bx, y + 1, PINK[max(0, (3 if j < size - 1 else 1) + k)], L)
        p.px(x, y + 1, PINK[max(0, 2 + k)], L)
    p.px(x, g - h - 1, HEDGE[max(0, 5 + k)], L)


def caterpillar_scene(p: Pix, x0, x1, g, night, motion, top=TOP + 2, stem=None, foxgloves=6) -> tuple:
    """The right of an H2's page, standing on the grass at row g between columns x0 and x1: the giant mushroom, the
    Caterpillar sitting up on its cap with his arms folded and the hookah's mouthpiece at his lips, the hookah on the
    cap beside him, its hose curling to him, and the smoke rising from his lips in rings of the code, up to the hedge
    at the page's top; foxgloves at the mushroom's foot on the left and toadstools on the right. By night the hookah's
    coal burns phosphor, flickering, its light on the Caterpillar, the cap and the stem, and the smoke glows; fireflies
    hang over the grass. The mushroom stands taller the more rows the page gives it (or `stem` rows tall), and the
    smoke rises no higher than row `top`. Returns its span."""
    k = -1 if night else 0
    rw = min(40, (x1 - x0) // 2 - 10)
    cx = x1 - rw - 4
    ch = 18
    if stem is None:
        stem = max(20, min(30, 22 + (g - 106) // 3))   # the stem's height: a little taller on a taller page
    cap_y = g - stem - (ch - 3)
    for i, fx in enumerate(list(range(x0 + 5, cx - rw - 2, 7))[:foxgloves]):
        foxglove(p, fx, g, night, h=min(36, g - top - 10) - 8 * (i % 2))
    cap = mushroom(p, cx, g, night, rw, cap_y, ch=ch)
    crown = min(y for _, y in cap)
    sx = cx - rw + 4
    sy = crown + 5 - len(CATERPILLAR)
    pal = {"o": BLUE[1], "W": BLUE[max(0, 6 + k)], "B": BLUE[max(0, 5 + k)], "b": BLUE[max(0, 4 + k)],
           "d": BLUE[max(0, 3 + k)], "D": BLUE[max(0, 2 + k)], "e": SPADE[0], "a": BLUE[max(0, 6 + k)],
           "A": BLUE[max(0, 3 + k)], "g": GOLD[max(0, 3 + k)], "G": GOLD[max(0, 5 + k)], "k": BLUE[1]}
    sprite(p, sx, sy, CATERPILLAR, pal)
    hx, hy = cx + rw - 22, crown + 9 - len(HOOKAH)
    hpal = {"g": GOLD[max(0, 3 + k)], "G": GOLD[max(0, 5 + k)], "n": GOLD[1], "l": BOTTLE[max(0, 3 + k)],
            "L": BOTTLE[max(0, 5 + k)], "w": BOTTLE[6] if not night else BOTTLE[4], "s": BOTTLE[max(0, 1 + k)],
            "h": GOLD[max(0, 3 + k)], "r": FLAME[1] if not night else None}
    sprite(p, hx, hy, HOOKAH, hpal)
    # The hose, from the hookah's belly sagging down and round, and up to the mouthpiece, lit along its top.
    mx, my = sx + 21, sy + 8
    ax, ay = hx + 12, hy + 11
    n = max(12, ax - mx + 6)
    for i in range(n + 1):
        t = i / n
        x = round(ax + (mx - ax) * t + 3 * math.sin(math.pi * t))
        y = round(ay + (my - ay) * t + 9 * math.sin(math.pi * t))
        p.px(x, y, TWEED[max(0, 2 + k)])
        p.px(x, y - 1, TWEED[max(0, 4 + k)])
    if x1 - 3 > cx + rw + 8:
        toadstool(p, cx + rw + 2, g, night, h=8, w=7)
    _rings(p, (x0 + 2, top, sx + 26, sy + 8), (mx - 1, my), night, motion)
    if night:
        coal = p.flicker(1) if motion else "base"
        p.px(hx + 6, hy, FLAME[6], coal)
        p.px(hx + 5, hy, FLAME[5], coal)
        p.px(hx + 7, hy, FLAME[5], coal)
        p.px(hx + 6, hy - 1, FLAME[4], coal)
        p.halo(hx + 6.5, hy, 7, 6, FLAME[3], (0.12, 0.22, 0.34), L=p.flicker(1, back=True) if motion else "haze")
        lit = {BLUE[max(0, t - 1)] for t in range(7)} | {ROSE[max(0, t - 2)] for t in range(7)} | \
            {CARD[max(0, t - 2)] for t in range(7)} | {GOLD[max(0, t - 1)] for t in range(7)} | \
            {BOTTLE[max(0, t - 1)] for t in range(7)} | {TWEED[max(0, t - 1)] for t in range(7)}
        p.halo(hx + 3, hy + 4, 30, 22, FLAME[4], (0.1, 0.2, 0.32), L="base", only=lit)
        fireflies(p, (x0 + 2, g - 26, x1 - 2, g - 4), motion, n=6, seed=12)
    return (x0 - 1, x1 + 1)


# --------------------------------------------------------------------------- painting the roses red
# A card gardener after Tenniel, 19 wide and 28 tall, the Two of Spades, facing right with his brush raised: his cap
# (h), his face in profile on the hand's medium skin (s, lit S, shaded z) with a single dark eye (e), the card he is
# (w, its shade c, its rim r, its two spades and its index p), his sleeves and hose of the spades' black (a, lit A),
# his shoes (f), and the brush (t its handle, B its bristles wet with red paint).
GARDENER = [
    ".....hhh...........",
    "....hhhhh..........",
    "....hSssz..........",
    "....hssesS.........",
    ".....sssz.......BB.",
    "......zz.......BB..",
    "..rrrrrrrrrrr.tt...",
    "..rpwwwwwwwwr.t....",
    "..rwwwwpwwwcrAt....",
    "..rwwwpppwwcAa.....",
    ".arwwpppppwcr......",
    ".arwwwwpwwwcr......",
    ".arwwwwwwwwcr......",
    ".arwwwwwwwwcr......",
    ".SrwwwwwwwwcrS.....",
    "..rwwwwwwwwcr......",
    "..rwwwwpwwwcr......",
    "..rwwpppppwcr......",
    "..rwwwpppwwcr......",
    "..rwwwwpwwwcr......",
    "..rwwwwwwwpcr......",
    "..rrrrrrrrrrr......",
    ".....a...a.........",
    ".....A...a.........",
    ".....a...a.........",
    ".....A...a.........",
    ".....a...a.........",
    ".....ff..ff........",
]


# The faces a card gardener may be, nine columns by fourteen rows of his card: the Two of Spades and the Five.
FACES = {
    "two": ["pwwwwwwww", "wwwwpwwwc", "wwwpppwwc", "wwpppppwc", "wwwwpwwwc", "wwwwwwwwc", "wwwwwwwwc", "wwwwwwwwc",
            "wwwwwwwwc", "wwwwpwwwc", "wwpppppwc", "wwwpppwwc", "wwwwpwwwc", "wwwwwwwpc"],
    "five": ["pwwwwwwww", "wwpwwwpwc", "wpppwpppc", "wpwpwpwpc", "wwwwwwwwc", "wwwwpwwwc", "wwwpppwwc", "wwwpwpwwc",
             "wwwwwwwwc", "wpwpwpwpc", "wpppwpppc", "wwpwwwpwc", "wwwwwwwwc", "wwwwwwwpc"],
}


def card_gardener(p: Pix, x, g, night, motion, pot=True, face="two") -> tuple:
    """A card gardener, the Two of Spades or the Five (`face`), standing on the grass at row g from column x and
    painting a rose red: a playing card with a head, arms and legs, his face on the hand's medium skin, his brush
    raised to the right; in a moving header he dabs, the brush rising a unit and falling again round a four-second
    loop. His paint pot stands at his feet (`pot`), red paint running down its side. Returns the tip of his brush."""
    k = -1 if night else 0
    S = RAMP["skin1"]
    pal = {"h": TWEED[1], "s": S[3], "S": S[4], "z": S[2], "e": SPADE[0], "w": CARD[6 + k], "c": CARD[4 + k],
           "r": CARD[1], "p": SPADE[1], "a": SPADE[2], "A": SPADE[4], "f": SPADE[0], "t": TWEED[3 + k], "B": ROSE[3]}
    y0 = g - len(GARDENER) + 1
    rows = [row if not 7 <= j <= 20 else row[:3] + FACES[face][j - 7] + row[12:] for j, row in enumerate(GARDENER)]
    body = [row[:13] + "." * (len(row) - 13) for row in rows]
    arm = ["." * 13 + row[13:] for row in rows]
    sprite(p, x, y0, body, pal)
    L = p.layer("dab", ("bob", (0, 0, 1, 1, 0, 0, 0, 0), 4.0), z=0.25) if motion else "base"
    sprite(p, x, y0, arm, pal, L)
    if pot:
        px_ = x - 7
        for yy in range(g - 4, g + 1):
            for xx in range(px_, px_ + 6):
                t = 5 if xx == px_ + 1 else 3 if xx < px_ + 5 else 1
                p.px(xx, yy, FUR[max(0, t + k)])
        p.hline(px_, px_ + 6, g - 5, FUR[1])
        p.hline(px_ + 1, px_ + 5, g - 5, ROSE[3])
        p.px(px_ + 2, g - 4, ROSE[3])
        p.px(px_ + 2, g - 3, ROSE[2])
        p.px(px_ + 4, g - 4, ROSE[2])
        for dx in (-1, 6):
            p.px(px_ + dx, g - 7, FUR[3 + k])
        p.hline(px_, px_ + 6, g - 8, FUR[3 + k])
    return (x + 17, y0 + 4)


def rose_tree(p: Pix, cx, g, night, motion, top, tip=None, bush=False) -> tuple:
    """A standard rose tree in its wooden tub on the grass at row g, centred on column cx and rising to row `top`:
    round heads of leaves packed close, one over another on a straight trunk, as the Queen's gardeners train them, the
    more the taller the room (a strip of seventy rows has one, a taller one two or three), each lit on its upper left
    and in shade at its foot and set with roses, most of them white and some painted red; the trunk lit down its left
    side; the tub's boards banded in iron. The rose nearest the gardener's brush (`tip`) turns from white to red as he
    paints it in a moving header, half painted in the still twin. A `bush` is one head sitting on the grass, with no
    trunk and no tub. Returns the lowest head's middle and radius."""
    k = -2 if night else 0
    tub_w, tub_h = 16, 9
    rise = g - tub_h - top
    tiers = 1 if rise <= 66 else 2 if rise <= 108 else 3
    hr = max(11, min(19, rise // (2 * tiers) - (4 if tiers == 1 else 1)))
    gap = (rise - 2 * hr * tiers - 6) // max(1, tiers - 1) if tiers > 1 else 0
    heads = [(top + hr + i * (2 * hr + gap), hr + (1 if i == tiers - 1 and tiers > 1 else 0)) for i in range(tiers)]
    if bush:
        hr = (g - top) // 2
        heads = [(g - hr + 2, hr)]
    # The tub: boards of the tweed's brown, lit at the left, banded in the spades' iron, its rim catching the light.
    tx = cx - tub_w // 2
    for yy in range(g - tub_h + 1, g + 1) if not bush else ():
        taper = (yy - (g - tub_h + 1)) // 4
        for xx in range(tx + taper, tx + tub_w - taper):
            u = (xx - tx) / tub_w
            t = 5 if u < 0.15 else 4 if u < 0.5 else 3 if u < 0.85 else 2
            if (xx - tx) % 4 == 3:
                t -= 1
            p.px(xx, yy, TWEED[max(0, t + k)])
    if not bush:
        p.hline(tx - 1, tx + tub_w + 1, g - tub_h, TWEED[max(0, 5 + k)])
        p.hline(tx - 1, tx + tub_w + 1, g - tub_h + 1, TWEED[max(0, 2 + k)])
        for yy in (g - tub_h + 3, g - 2):
            p.hline(tx + (yy - (g - tub_h + 1)) // 4, tx + tub_w - (yy - (g - tub_h + 1)) // 4, yy,
                    SPADE[max(0, 3 + k)])
        p.hline(tx + 1, tx + tub_w - 1, g - tub_h + 2, SOIL[3])
    # The trunk, straight, from the tub up through every head.
    for yy in range(heads[0][0], g - tub_h) if not bush else ():
        p.px(cx - 1, yy, BARK[max(0, 5 + k)])
        p.px(cx, yy, BARK[max(0, 3 + k)])
        p.px(cx + 1, yy, BARK[max(0, 1 + k)])
    uid = p.syms.get(("leaves", night))
    if uid is None:
        uid = p.syms[("leaves", night)] = f"{getattr(p, 'sheet', 'p')}h"
        p.defs.append(_leaves(uid, night))
    spots = []
    for n, (hy, r) in enumerate(heads):
        head = ellipse(cx, hy, r, r * 0.92)
        did = f"{getattr(p, 'sheet', 'p')}rt{n}{'b' if bush else ''}"
        p.defs.append(f'<path id="{did}" d="{blocks(head)}"/>')
        p.shapes["base"].append(f'<use href="#{did}" fill="url(#{uid})"/>')
        for (x, y) in head:
            up, left_, down, right_ = ((x, y - 1) not in head, (x - 1, y) not in head, (x, y + 1) not in head,
                                       (x + 1, y) not in head)
            nx, ny = (x + 0.5 - cx) / r, (y + 0.5 - hy) / r
            if up or (left_ and ny < 0.3):
                p.px(x, y, HEDGE[max(0, 6 + k)])
            elif down or (right_ and ny > -0.3):
                p.px(x, y, HEDGE[max(0, 1 + k)])
            elif nx * LX + ny * LY > 0.55 and (x + y) % 3 == 0:
                p.px(x, y, HEDGE[max(0, 5 + k)])
        for i in range(14):
            ang = i * 2.4 + n
            rr = r * (0.35 + 0.5 * ((i * 7) % 10) / 10)
            rx_, ry_ = round(cx + math.cos(ang) * rr - 2.5), round(hy + math.sin(ang) * rr * 0.9 - 2.5)
            if all(abs(rx_ - a) > 4 or abs(ry_ - b) > 4 for a, b in spots):
                spots.append((rx_, ry_))
    rnd = random.Random(int(cx))
    painting = min(spots, key=lambda q: (q[0] - tip[0]) ** 2 + (q[1] - tip[1]) ** 2) if tip else None
    for i, (rx_, ry_) in enumerate(spots):
        if (rx_, ry_) == painting:
            continue
        rose(p, rx_, ry_, night, 1.0 if (i + rnd.randrange(2)) % 3 == 0 else 0.0)
    if painting:
        rx_, ry_ = painting
        if motion:
            for f, (painted, t0, t1) in enumerate(((0.0, 0.0, 0.3), (0.5, 0.3, 0.65), (1.0, 0.65, 1.0))):
                rose(p, rx_, ry_, night, painted, p.seq(f"paint{f}", t0, t1, 4.0, keep=f == 1, z=0.1))
        else:
            rose(p, rx_, ry_, night, 0.5)
    return (cx, heads[-1][0], heads[-1][1])


def lantern(p: Pix, x, y, night, motion, L="base"):
    """A garden lantern hung by its ring from a bough, its top-left at (x, y), 5 wide and 8 tall: an iron cap and
    frame round its glass; by night a light of phosphor burns in it, flickering, and its glow spreads round it; by day
    its glass is dark."""
    k = -1 if night else 0
    p.px(x + 2, y, SPADE[3 + k], L)
    p.hline(x + 1, x + 4, y + 1, SPADE[4 + k], L)
    p.hline(x, x + 5, y + 2, SPADE[3 + k], L)
    for yy in range(y + 3, y + 7):
        p.px(x, yy, SPADE[3 + k], L)
        p.px(x + 4, yy, SPADE[1], L)
        for xx in range(x + 1, x + 4):
            p.px(xx, yy, BOTTLE[2] if not night else FLAME[3], L)
    p.hline(x, x + 5, y + 7, SPADE[2], L)
    if night:
        lit = p.flicker(2) if motion else L
        p.px(x + 2, y + 4, FLAME[6], lit)
        p.px(x + 2, y + 5, FLAME[5], lit)
        p.px(x + 1, y + 4, FLAME[4], lit)
        p.halo(x + 2.5, y + 4.5, 8, 7, FLAME[3], (0.08, 0.16, 0.26), L=p.flicker(2, back=True) if motion else "haze")
    else:
        p.px(x + 1, y + 3, BOTTLE[5], L)


def rose_garden(p: Pix, x0, x1, g, night, motion, top) -> tuple:
    """The right of an H3's strip, standing on the grass at row g between columns x0 and x1 and rising to row `top`,
    the strip's full height: the rose tree in its tub, and the Two of Spades before it painting its white roses red,
    his paint pot at his feet; by night a lantern hung from the tree burns phosphor and lights them both, the roses,
    the card and the tub. Returns its span."""
    cx = x1 - 19
    tip = card_gardener(p, cx - 33, g, night, motion, pot=x0 + 8 <= cx - 40)
    cx_, hy, hr = rose_tree(p, cx, g, night, motion, top, tip=tip)
    lantern(p, cx - hr + 1, hy + hr - 4, night, motion)
    if night:
        lit = {CARD[max(0, t - 1)] for t in range(7)} | {SPADE[max(0, t - 1)] for t in range(7)} | \
            {TWEED[max(0, t - 2)] for t in range(7)} | {HEDGE[max(0, t - 2)] for t in range(7)} | \
            {ROSE[max(0, t - 2)] for t in range(7)} | set(RAMP["skin1"])
        p.halo(cx - hr + 3, hy + hr, 22, 18, FLAME[4], (0.1, 0.2, 0.3), L="base", only=lit)
    return (x0 - 1, x1 + 1)


# The golden key that lies on the glass table, 11 by 5, beside SECTION A-A: its bow (o its gold, O lit, n shaded) and
# its bit; and the White Rabbit's watch, 9 by 11, open on its chain, beside an H3's title (its case g, lit G, shaded
# n, its face f, its hands h and its bow b).
KEY = ["..nGn......", ".n...n.....", ".O...oooooo", ".n...n...o.", "..non....oo"]
WATCH = ["...bbb...", "...b.b...", "...GGG...", ".nGfffGn.", "nGffhffGn", "gffhfffgn", "gffhhffgn",
         "gfffffffn", ".nfffffn.", "..nnnnn..", "........."]


def golden_key(p: Pix, x, y, night):
    """The little golden key, 11 by 5, its bow at the left, lit along its upper edges."""
    k = -1 if night else 0
    sprite(p, x, y, KEY, {"o": GOLD[4 + k], "O": GOLD[6 + k], "n": GOLD[2], "G": GOLD[5 + k]})


def pocket_watch(p: Pix, x, y, night):
    """The White Rabbit's watch, 9 by 10, open on its bow: a gold case lit on its upper left round a white face with
    its two hands."""
    k = -1 if night else 0
    sprite(p, x, y, WATCH, {"b": GOLD[3 + k], "G": GOLD[5 + k], "g": GOLD[4 + k], "n": GOLD[1], "f": CARD[6 + k],
                            "h": SPADE[1]})


# --------------------------------------------------------------------------- the phones
PHONE_SCENE = 60    # the rows a phone's H1 keeps under its words and notes for the whole of Wonderland
PHONE_LEAST = 48    # the fewest it stands it in
UNDER = {"H2": 78, "H3": 66}   # the rows a phone's H2 and H3 ask for under their words, whatever they say


def phone_world(p: Pix, g, night, room) -> tuple:
    """A phone's H1 under its words, standing on the rule at row g and rising `room` rows, the whole of Wonderland
    across the phone: at the left the arch of roses with the White Rabbit bounding under it, looking at his watch,
    tulips and Easter eggs in the grass; a trail of fallen cards leading right to the old tree, the Cheshire Cat on
    its bough by day and his grin by night, its roots arching over the rabbit hole, the code glowing up out of it and
    lighting the grass, with toadstools and the little bottle by it; the moon in the arch and fireflies by night.
    Returns its span."""
    top = g - room + 1
    meadow(p, EDGE, p.w - EDGE, g, night)
    spring = max(26, min(34, room - 26))
    warren(p, 4, g, night, False, width=38, flutter=False, spring=spring)
    tree(p, 104, p.w - EDGE, g, night, False, top=top)
    fallen_cards(p, 62, g, night)
    if night:
        fireflies(p, (8, top + 12, 100, g - 6), False, n=6, seed=9)
    return (4, p.w - EDGE)


def phone_caterpillar(p: Pix, g, night, room) -> tuple:
    """A phone's H2 under its words, standing on the rule at row g and rising `room` rows: the Caterpillar on his
    mushroom with his hookah, the smoke rising in rings of the code, foxgloves at the left (see
    `caterpillar_scene`)."""
    meadow(p, EDGE, p.w - EDGE, g, night)
    return caterpillar_scene(p, 6, p.w - EDGE - 2, g, night, False, top=g - room + 2, stem=20, foxgloves=4)


def phone_garden(p: Pix, g, night, room) -> tuple:
    """A phone's H3 under its words, standing on the rule at row g and rising `room` rows, painting the roses red
    across the phone: at the left the Five of Spades painting a rose bush, a pot of red paint beside it; at the right
    the Two of Spades at the rose tree in its tub, the lantern hung in it burning phosphor by night and lighting them
    (see `rose_garden`). Returns its span."""
    k = -1 if night else 0
    top = g - room + 2
    meadow(p, EDGE, p.w - EDGE, g, night)
    tip = card_gardener(p, 7, g, night, False, pot=False, face="five")
    rose_tree(p, 42, g, night, False, g - 26, tip=tip, bush=True)
    px_ = 66
    for yy in range(g - 4, g + 1):
        for xx in range(px_, px_ + 6):
            t = 5 if xx == px_ + 1 else 3 if xx < px_ + 5 else 1
            p.px(xx, yy, FUR[max(0, t + k)])
    p.hline(px_, px_ + 6, g - 5, FUR[1])
    p.hline(px_ + 1, px_ + 5, g - 5, ROSE[3])
    p.px(px_ + 3, g - 4, ROSE[2])
    rose_garden(p, 98, p.w - EDGE - 1, g, night, False, top)
    return (EDGE, p.w - EDGE)


# --------------------------------------------------------------------------- the footers, links and badges
FOOT_RISE = 7     # the rows the clipped hedge rises along the foot where the cells leave it room
FOOT_RUN = 24     # the fewest columns it rises along


def hole_mound(p: Pix, x, ground, night, tall=True) -> tuple:
    """The rabbit hole in a mound of moss and grass, 18 wide, its foot on row `ground` from column x: the mound lit on
    its upper left, the hole dark in its face, and the code glowing up out of it, two glyphs rising one over the other
    from the hole when the mound stands `tall` and one when it does not, faint by day and by night bright phosphor,
    flickering, its light pooled round the hole. Returns its height."""
    k = -2 if night else 0
    mound = {(xx, yy) for (xx, yy) in ellipse(x + 9, ground + 2, 9, 8) if yy <= ground}
    for (xx, yy) in mound:
        lam = light((xx + 0.5 - x - 9) / 9, (yy + 0.5 - ground - 2) / 8, 0.6)
        top = (xx, yy - 1) not in mound
        p.px(xx, yy, HEDGE[max(0, min(6, (2 + round(4 * lam)) + (1 if top else 0) + k))])
    hole = {(xx, yy) for (xx, yy) in ellipse(x + 9, ground + 1, 4, 4) if yy <= ground}
    for (xx, yy) in hole:
        edge = (xx, yy - 1) not in hole
        if night:
            p.px(xx, yy, FLAME[1] if not edge else SOIL[2])
        else:
            p.px(xx, yy, SOIL[1] if not edge else SOIL[3])
    glyphs = 2 if tall else 1
    L = p.flicker(0) if night else "base"
    tones = (FLAME[5], FLAME[3]) if night else (FLAME[3], FLAME[2])
    for i in range(glyphs):
        rain.write(p, x + 7, ground - 13 - i * rain.PITCH, rain.NAMES[(i * 7 + 3) % len(rain.NAMES)], tones[i], L)
    if night:
        p.halo(x + 9, ground - 2, 9, 6, FLAME[3], (0.1, 0.2), L=p.flicker(0, back=True))
    return 13 + glyphs * rain.PITCH


def footing(p: Pix, night: bool, rule: str, after=0):
    """A footer once its words are set: along its foot the clipped hedge's top, lit and set with roses, some of them
    white roses half painted red, and over it, as deep as keeps a row clear of the lowest word, the spring grass,
    blades lit at their tips with daisies and bluebells among them; a clipped box hedge rising over the grass wherever
    the cells leave it room along FOOT_RUN columns or more, lit along its top and set with roses, the ruled lines
    between the cells left standing; and the rightmost place from column `after` on where the cells leave the page
    free, the rabbit hole in its mound with the code glowing up out of it, a toadstool and the little bottle beside it
    (see `hole_mound`), or the bottle alone where there is less room. By night the code burns phosphor and flickers,
    and fireflies hang over the grass."""
    w, h = p.w, p.h
    k = -2 if night else 0
    ground = h - EDGE - 1
    low = max((b[3] for b in p.words), default=0)
    ledge = max(ground - 3, low + 1)

    def free(x0, y0, x1, y1):
        return EDGE + 1 <= x0 and x1 <= w - EDGE - 1 and y0 >= EDGE + 1 and \
            p.clear_of_words(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
    # The hedge's top along the foot, lit, a rose in it every so often: each unit of it a unit clear of every word,
    # in the hedge's lower rows where a word comes down onto it.
    rnd = random.Random(w * 7 + h)

    def clear(x, y):
        return p.clear_of_words(x - 1, y - 1, x + 2, y + 2)
    for x in range(EDGE, w - EDGE):
        for y, tones in ((ground + 1, (6, 6, 5)), (ground + 2, (3, 3, 4)), (ground + 3, (2, 1, 2))):
            if clear(x, y):
                p.px(x, y, HEDGE[max(0, rnd.choice(tones) + k)])
    for i, x in enumerate(range(EDGE + 6, w - EDGE - 3, 17)):
        red = i % 3 != 2
        y = next((y for y in (ground + 1, ground + 2) if all(clear(x + dx, y + dy) for dx in (0, 1) for dy in (0, 1))),
                 None)
        if y is None:
            continue
        p.px(x, y, (ROSE[5] if red else CARD[6]) if not night else (ROSE[3] if red else CARD[4]))
        p.px(x + 1, y, ROSE[3 + k // 2] if red else CARD[4 + k // 2])
        p.px(x, y + 1, ROSE[2 + k // 2] if red else ROSE[3])
        p.px(x + 1, y + 1, ROSE[1] if red else CARD[3 + k // 2])
    # The grass over it, as deep as the words leave it.
    if ledge <= ground:
        for x in range(EDGE, w - EDGE):
            p.px(x, ground, HEDGE[max(0, 2 + k)])
            for y in range(ledge, ground):
                if rnd.random() < 0.55 + 0.15 * (y - ledge):
                    p.px(x, y, HEDGE[max(0, rnd.choice((3, 4, 4, 5)) + k)])
            if ground - ledge >= 2 and x % 11 in (3, 8) and rnd.random() < 0.6:
                p.px(x, ledge, CARD[max(0, 6 + k)] if x % 11 == 3 else BLUE[max(0, 5 + k)])
    # The emblem: the rabbit hole in its mound, or the bottle alone.
    mark, taken = None, (0, 0)
    for tall, ew, eh in ((True, 32, 25), (False, 32, 17), (None, 10, 10)):
        mark = next(((x, tall) for x in range(w - EDGE - 2 - ew, max(EDGE + 1, after), -1)
                     if free(x, ground - eh, x + ew, ground + 1)), None)
        if mark:
            taken = (mark[0] - 2, mark[0] + ew + 2)
            break
    # The hedge rising where the cells leave it room, broken where a ruled line stands.
    lines = {x for x in range(w) if p.get(x, ledge - 2) == rule}
    rise = [x not in range(*taken) and not lines & {x - 1, x, x + 1} and
            free(x, ledge - FOOT_RISE - 1, x + 1, ledge) for x in range(w)]
    uid = p.syms.get(("leaves", night)) or f"{getattr(p, 'sheet', 'p')}h"
    x = EDGE + 1
    n = 0
    while x < w - EDGE - 1:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - EDGE - 1) if not rise[i]), w - EDGE - 1)
        if b - x >= FOOT_RUN:
            top = ledge - FOOT_RISE
            p.shapes["base"].append(f'<rect x="{x + 1}" y="{top + 1}" width="{b - x - 2}" height="{ledge - top}" '
                                    f'fill="url(#{uid})"/>')
            for xx in range(x, b):
                end = xx in (x, b - 1)
                p.px(xx, top + (1 if end else 0), HEDGE[max(0, (5 if xx < b - 1 else 2) + k)])
                p.px(xx, ledge, HEDGE[max(0, 1 + k)])
                if end:
                    for yy in range(top + 2, ledge):
                        p.px(xx, yy, HEDGE[max(0, (5 if xx == x else 1) + k)])
            for i, rx in enumerate(range(x + 3, b - 6, 9)):
                rose(p, rx, top - 1 + (i % 2), night, 1.0 if (n + i) % 3 else 0.5)
            n += 1
        x = b
    if mark:
        x, tall = mark
        if tall is None:
            bottle(p, x + 1, ground, night)
        else:
            hole_mound(p, x + 6, ground, night, tall)
            toadstool(p, x, ground, night, h=6, w=6)
            bottle(p, x + 24, ground, night)
    if night:
        rnd = random.Random(w + h)
        for i in range(max(3, w // 60)):
            fx, fy = rnd.randrange(EDGE + 4, w - EDGE - 4), rnd.randrange(max(EDGE + 2, ledge - 9), ledge)
            if free(fx - 1, fy - 1, fx + 2, fy + 2) and not (taken[0] <= fx < taken[1]):
                L = p.flicker(i)
                p.px(fx, fy, FLAME[5], L)
                p.apx(fx - 1, fy, FLAME[3], 0.4, L)
                p.apx(fx + 1, fy, FLAME[3], 0.4, L)


def tufts(p: Pix, x0, x1, y, seed, night):
    """Tufts of the spring grass along a rule from x0 to x1 on row y, every so often in the two rows over it, a daisy
    or a bluebell in some of them, each tuft two units clear of every word, sparser on a sheet's own rule under its
    tag, and half as many in a drawing made lighter to fit its budget."""
    k = -2 if night else 0
    every = (29, 47) if y > 21 else (47, 79)
    if p.lite:
        every = (every[0] * 2, every[1] * 2)
    rnd = random.Random(seed)
    x = x0 + 4 + seed % 9
    while x + 6 < x1:
        if p.clear_of_words(x - 3, y - 5, x + 6, y + 1):
            for dx, dy, t in ((0, -1, 3), (1, -1, 4), (1, -2, 5), (2, -1, 3), (3, -1, 4), (-1, -1, 2)):
                p.px(x + dx, y + dy, HEDGE[max(0, t + k)])
            flower = rnd.random()
            if flower < 0.4:
                p.px(x + 1, y - 3, CARD[max(0, 6 + k)])
            elif flower < 0.6:
                p.px(x + 3, y - 2, BLUE[max(0, 5 + k)])
        x += rnd.randrange(*every)


def corner_card(p: Pix, x, y, night):
    """A playing card dropped in the corner of the closing notes, 7 by 9 and a little askew, a heart on its face."""
    key = ("card", 7, 9, 12.0, night)
    if key not in p.syms:
        p.symbol(key, _card(7, 9, 12.0, night))
    p.use(key, x, y)
    pkey = ("pip", "heart")
    if pkey not in p.syms:
        p.symbol(pkey, {(i_, j_): 1 for j_, row in enumerate(PIPS["heart"]) for i_, c in enumerate(row) if c == "#"},
                 mono=True)
    p.use(pkey, x + 2, y + 3, stroke=ROSE[3])


HEART = [".54.43.", "5444432", "4443321", ".33321.", "..321..", "...1..."]   # a heart pip, 7 by 6


def heart(p: Pix, x, y, L="base"):
    """The heart of BUILT WITH (heart) BY, 7 by 6: a playing card's heart pip in the roses' red, lit on its upper
    left lobe and deepening toward its point."""
    p.sprite(x, y, HEART, {str(i): ROSE[i] for i in range(7)}, 1, L)


def painted_bar(p: Pix, x0, y0, w, h, period=5):
    """The graphic scale's bar as the gardeners paint it: blocks of white rose and red paint by turns, `period` units
    a block, each lit along its top and shaded along its foot."""
    for yy in range(y0, y0 + h):
        band = 0 if yy == y0 else 2 if yy == y0 + h - 1 else 1
        for xx in range(x0, x0 + w):
            red = ((xx - x0) // period) % 2 == 1
            p.px(xx, yy, (ROSE[5], ROSE[3], ROSE[1])[band] if red else (CARD[6], CARD[5], CARD[3])[band])


# The link buttons' sprites, 9 by 7: the White Rabbit's gold watch, a card of hearts, a painted rose and the
# rabbit's own head, in their tones (see `icon_pal`).
ICONS = {
    "watch": ["....G....", "..gGGGd..", ".gGfffgd.", ".Gffhffd.", ".gffhhfd.", ".gdfffdd.", "..ddddd.."],
    "card": [".ooooooo.", ".owwwwwo.", ".owRwrwo.", ".owrrrwo.", ".owwrwco.", ".owwwcco.", ".ooooooo."],
    "rose": ["..abba...", ".abxyba..", ".bxyyxb..", ".abxxba..", "..abba.l.", "...L.ll..", "...L....."],
    "rabbit": ["..op.op..", "..op.op..", "..owwwo..", ".owwwwwo.", ".owwvewo.", "..owwwwn.", "...ovvo.."],
}


def link_hedge(p: Pix, x0, x1, y, night, seed=0):
    """A sprig of the clipped hedge along a link button's top edge, row `y` its rim: leaves packed close in the two
    rows over it, lit along their tops, and a rose in bloom every so often, by turns red and white half painted."""
    k = -2 if night else 0
    rnd = random.Random(seed)
    for x in range(x0, x1):
        p.px(x, y - 1, HEDGE[max(0, rnd.choice((3, 4, 4)) + k)])
        if rnd.random() < 0.7:
            p.px(x, y - 2, HEDGE[max(0, rnd.choice((4, 5, 6)) + k)])
    for i, x in enumerate(range(x0 + 4 + seed % 5, x1 - 3, 11)):
        red = i % 3 != 2
        p.px(x, y - 2, (ROSE[5] if red else CARD[6]) if not night else (ROSE[4] if red else CARD[5]))
        p.px(x + 1, y - 2, ROSE[3] if red else CARD[4])
        p.px(x, y - 1, ROSE[3])
        p.px(x + 1, y - 1, ROSE[2] if red else CARD[3])


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a link button by day or by night: the night a tone down."""
    k = -1 if night else 0
    return {"g": GOLD[3 + k], "G": GOLD[5 + k], "d": GOLD[1], "f": CARD[6 + k], "h": SPADE[1], "o": CARD[1],
            "w": CARD[6 + k], "c": CARD[3 + k], "r": ROSE[3 + k], "R": ROSE[5 + k], "a": ROSE[2 + k], "b": ROSE[3 + k],
            "x": ROSE[4 + k], "y": ROSE[6 + k], "l": HEDGE[4 + k], "L": HEDGE[2 + k], "W": FUR[6 + k], "v": FUR[3 + k],
            "p": PINK[4 + k], "e": PINK[1], "n": PINK[3], "#": ink}


# --------------------------------------------------------------------------- the elements
SUIT_INK = {"heart": "rose", "diamond": "rose", "spade": "spade", "club": "spade"}


def pip(p: Pix, x, y, suit, colour, L="base"):
    """A suit's pip, 3 by 3, its top-left at (x, y): drawn once a file and placed."""
    key = ("pip", suit)
    if key not in p.syms:
        p.symbol(key, {(i_, j_): 1 for j_, row in enumerate(PIPS[suit]) for i_, c in enumerate(row) if c == "#"},
                 mono=True)
    p.use(key, x, y, L, stroke=colour)


def suit_colour(suit, night=False) -> str:
    """The ink a suit is printed in: the roses' red for hearts and diamonds, the spades' black for the rest."""
    return ROSE[3] if SUIT_INK[suit] == "rose" else SPADE[1]


def card_node(p: Pix, x, y, w, h, night, seed, lid):
    """A schematic card as a playing card: an inner rim of the roses' red a unit in from its edge, the pip of a suit
    (by turns hearts, spades, diamonds, clubs) in its foot's far corner, a band of the card back's red lattice down its
    icon cell's edge, and on its lid, when it has one, a sprig of the hedge with a rose in bloom."""
    k = -1 if night else 0
    suit = SUITS[seed % 4]
    rim = ROSE[2 + k] if not night else ROSE[3]
    for xx in range(x + 2, x + w - 2):
        p.px(xx, y + 2, rim)
        p.px(xx, y + h - 3, rim)
    for yy in range(y + 3, y + h - 3):
        p.px(x + 2, yy, rim)
        p.px(x + w - 3, yy, rim)
    for yy in range(y + 3, y + h - 3):
        for i, xx in enumerate((x + 11, x + 12)):
            p.px(xx, yy, ROSE[4 + k] if (yy + i) % 3 == 0 else ROSE[2 + k])
    pip(p, x + w - 7, y + h - 7, suit, suit_colour(suit, night) if not night else
        (ROSE[4] if SUIT_INK[suit] == "rose" else CARD[4]))
    if lid:
        for i, xx in enumerate(range(x + 3, x + 12)):
            p.px(xx, y - 1, HEDGE[max(0, (4 if i % 2 else 3) + 2 * k)])
            if i % 3 != 1:
                p.px(xx, y - 2, HEDGE[max(0, (5 if i % 2 else 4) + 2 * k)])
        p.px(x + 6, y - 2, ROSE[5 + k])
        p.px(x + 7, y - 2, ROSE[3 + k])
        p.px(x + 6, y - 3, ROSE[4 + k])
        p.px(x + 7, y - 1, ROSE[2 + k])


def briar(p: Pix, cells, night, seed):
    """The wire as a briar of the rose: a leaf every few units, by turns either side of it, a thorn now and then, and
    every eighteenth unit a rosebud, red or white."""
    k = -2 if night else 0
    for i, (x, y, d) in enumerate(cells[3:-5]):
        side = 1 if (i // 6) % 2 else -1
        if i % 6 == 2:
            if d == "h":
                p.px(x, y + side, HEDGE[max(0, (5 if side < 0 else 3) + k)])
                p.px(x + 1, y + side, HEDGE[max(0, 4 + k)])
            else:
                p.px(x + side, y, HEDGE[max(0, (5 if side < 0 else 3) + k)])
                p.px(x + side, y + 1, HEDGE[max(0, 4 + k)])
        elif i % 9 == 5:
            if d == "h":
                p.px(x, y - side, HEDGE[max(0, 1 + k)])
            else:
                p.px(x - side, y, HEDGE[max(0, 1 + k)])
        if i % 18 == 11:
            red = (i // 18 + seed) % 3 != 2
            cx, cy = (x, y - 2) if d == "h" else (x + 2, y)
            p.px(cx, cy, (ROSE[5] if red else CARD[6]) if not night else (ROSE[4] if red else CARD[5]))
            p.px(cx + 1, cy, ROSE[3] if red else CARD[4])
            p.px(cx, cy + 1, ROSE[3] if red else CARD[3])
            p.px(cx + 1, cy + 1, HEDGE[max(0, 3 + k)])


def big_watch(p: Pix, x, y, night):
    """The White Rabbit's pocket watch, 20 by 24 from its top-left (x, y), open on its bow with its chain trailing: a
    case of gold lit on its upper left and in shade at its lower right, a white enamel face with the hours marked round
    it, its two hands showing it late, and the bow and its ring over it."""
    k = -1 if night else 0
    cx, cy, r = x + 10, y + 13, 9.5
    for yy in range(y + 3, y + 24):
        for xx in range(x, x + 21):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if d > r:
                continue
            nx, ny = (xx + 0.5 - cx) / r, (yy + 0.5 - cy) / r
            if d > r - 2.2:
                lam = light(nx, ny, 0.5)
                c = GOLD[max(0, min(6, 1 + round(5 * lam) + k))]
                if d > r - 0.8:
                    c = GOLD[1] if lam < 0.5 else GOLD[max(0, 3 + k)]
            else:
                c = CARD[max(0, (6 if nx * LX + ny * LY > 0.1 else 5) + k)]
            p.px(xx, yy, c)
    for hr in range(12):
        ang = math.radians(hr * 30 - 90)
        tx, ty = cx + math.cos(ang) * (r - 3.4), cy + math.sin(ang) * (r - 3.4)
        p.px(math.floor(tx), math.floor(ty), SPADE[2] if hr % 3 else ROSE[3])
    for i in range(5):                              # the hour hand, toward ten
        p.px(math.floor(cx - 0.5 - i * 0.8), math.floor(cy - 0.5 - i * 0.45), SPADE[1])
    for i in range(7):                              # the minute hand, toward twelve past: late
        p.px(math.floor(cx - 0.5 + i * 0.35), math.floor(cy - 0.5 - i * 0.95), SPADE[1])
    p.px(math.floor(cx - 0.5), math.floor(cy - 0.5), GOLD[2])
    for xx, yy, t in ((x + 9, y + 2, 5), (x + 10, y + 2, 4), (x + 11, y + 2, 3), (x + 9, y + 1, 4), (x + 11, y + 1, 2),
                      (x + 10, y, 5), (x + 9, y, 3), (x + 11, y, 3)):
        p.px(xx, yy, GOLD[max(0, t + k)])
    for i in range(7):                              # the chain, trailing to the right
        p.px(x + 13 + i, y + 1 + (i * i) // 9, GOLD[max(0, (4 if i % 2 else 2) + k)])


def card_stack(p: Pix, bx, base, bw, v, night, i=0):
    """A week's commits as a stack of playing cards, `v` units tall on the base line: card upon card, each a white face
    lit along its top edge with its edge in shade, the top card face up with a pip of its suit."""
    k = -1 if night else 0
    top = base - v
    for yy in range(top, base):
        for xx in range(bx, bx + bw):
            edge = xx in (bx, bx + bw - 1)
            seam = (base - yy) % 4 == 0
            c = CARD[1] if edge else CARD[3 + k] if seam else CARD[5 + k] if xx < bx + bw - 2 else CARD[4 + k]
            p.px(xx, yy, c)
    p.hline(bx, bx + bw, top, CARD[1])
    if v >= 6 and bw >= 5:
        suit = SUITS[i % 4]
        pip(p, bx + (bw - 3) // 2, top + 2, suit, suit_colour(suit))


def crown(p: Pix, x, y, night):
    """The Queen of Hearts' little crown, 7 by 5, its gold lit on its left, a red jewel in its band."""
    k = -1 if night else 0
    sprite(p, x, y, ["G.G.G.g", "GGgGgGg", "GgggGgn", "grgrgrn", "gnnnnnn"],
           {"G": GOLD[5 + k], "g": GOLD[4 + k], "n": GOLD[2], "r": ROSE[3]})


def gold_ring(p: Pix, arc, night):
    """The dial's ring as the rim of the White Rabbit's watch: a band of gold lit along its upper left."""
    from ...holidays.pixel import tube
    k = -1 if night else 0

    def colour(s_, o, lam, x, y):
        return GOLD[max(1, min(6, round(1.4 + 4.6 * lam) + k))]
    tube(p, arc, 2.2, colour, outline=GOLD[1])


def wrapper(i, xx, yy, y0, y1, lift, night) -> str:
    """The `i`-th file type's wrapper at (xx, yy), by turns: the red lattice of a card's back, the hedge's leaves,
    the waistcoat's blue with its gold buttons, the jacket's tweed check, and the white card's face with its pips.
    `lift` lights its top row and shades its foot."""
    k = -1 if night else 0
    kind = i % 5
    if kind == 0:
        c = ROSE[4 + k] if (xx + yy) % 4 == 0 or (xx - yy) % 4 == 0 else ROSE[2 + k]
    elif kind == 1:
        c = HEDGE[max(0, (5 if (xx * 3 + yy * 5) % 7 < 2 else 3 if (xx + yy * 2) % 5 else 2) + 2 * k)]
    elif kind == 2:
        c = GOLD[5 + k] if (xx % 6 == 2 and yy == (y0 + y1) // 2) else BLUE[3 + k]
    elif kind == 3:
        c = TWEED[4 + k] if xx % 4 == 0 or yy % 4 == 0 else TWEED[3 + k]
        if xx % 4 == 0 and yy % 4 == 0:
            c = TWEED[2 + k]
    else:
        c = ROSE[3] if (xx % 7 == 3 and yy == (y0 + y1) // 2) else CARD[5 + k]
    ramp = next(r for r in (ROSE, HEDGE, GOLD, BLUE, TWEED, CARD) if c in r)
    return ramp[max(0, min(6, ramp.index(c) + lift))]


def card_cell(q: Pix, ox, oy, night):
    """A counter's cell as a playing card, 11 by 15: a white face lit along its top and left and a tone deeper along
    its foot and right, its corners rounded, its rim of the card's grey."""
    k = -1 if night else 0
    for yy in range(oy, oy + 15):
        for xx in range(ox, ox + 11):
            corner = (xx in (ox, ox + 10)) and (yy in (oy, oy + 14))
            if corner:
                continue
            edge = xx in (ox, ox + 10) or yy in (oy, oy + 14)
            if edge:
                c = CARD[1]
            elif yy == oy + 1 or xx == ox + 1:
                c = CARD[6]
            elif yy == oy + 13 or xx == ox + 9:
                c = CARD[4 + k]
            else:
                c = CARD[6] if not night else CARD[5]
            q.px(xx, yy, c)


def hedge_line(p: Pix, x0, x1, y, night):
    """The time line as a low clipped hedge from x0 to x1, three rows deep at row y: lit along its top, its leaves
    packed close and a tone deeper at its foot, a white rose in it every so often."""
    k = -2 if night else 0
    for x in range(x0, x1):
        p.px(x, y, HEDGE[max(0, (6 if x % 3 else 5) + k)])
        p.px(x, y + 1, HEDGE[max(0, (3 if (x * 5) % 7 < 4 else 4) + k)])
        p.px(x, y + 2, HEDGE[max(0, 1 + k)])
    for x in range(x0 + 9, x1 - 4, 23):
        p.px(x, y + 1, CARD[max(0, 6 + k)])


def release_rose(p: Pix, x, gy, kind, night, i=0):
    """A release on the hedge: a red rose on its stem for a release, a rose bush in bloom for a big one, a bud for a
    patch, a white rose not yet painted for a release still to come, and for the repository's beginning the rabbit
    hole."""
    k = -1 if night else 0
    if kind == "made":
        mound = {(xx, yy) for (xx, yy) in ellipse(x, gy + 3, 5, 4) if yy <= gy + 2}
        for (xx, yy) in mound:
            p.px(xx, yy, HEDGE[max(0, (5 if yy < gy else 3) + 2 * k)])
        for xx in range(x - 2, x + 2):
            p.px(xx, gy + 1, SOIL[1])
            p.px(xx, gy + 2, SOIL[0])
        return
    if kind == "minor":
        p.px(x, gy - 1, HEDGE[max(0, 3 + 2 * k)])
        p.px(x, gy - 2, ROSE[4 + k])
        p.px(x, gy - 3, ROSE[3 + k])
        return
    stem = 6 if kind != "big" else 7
    for yy in range(gy - stem, gy):
        p.px(x, yy, HEDGE[max(0, 3 + 2 * k)])
    p.px(x + 1, gy - 3, HEDGE[max(0, 4 + 2 * k)])
    if kind == "big":
        for dx, dy, painted in ((-3, -10, 1.0), (-1, -12, 1.0), (1, -10, 0.5)):
            rose(p, x + dx - 1, gy + dy, night, painted)
        return
    rose(p, x - 2, gy - stem - 4, night, 0.0 if kind == "next" else 1.0)


def card_avatar(p: Pix, cx, cy, i, person, night):
    """A contributor as a playing card held up, 11 by 15: their initials printed on its face in red or black by its
    suit, by turns hearts, spades, diamonds and clubs, a pip in its corner; a bot is a card face down, its back the
    red lattice."""
    k = -1 if night else 0
    x, y = cx - 5, cy - 7
    card_cell(p, x, y, night)
    if not person.get("initials"):
        for yy in range(y + 2, y + 13):
            for xx in range(x + 2, x + 9):
                p.px(xx, yy, ROSE[4 + k] if (xx + yy) % 3 == 0 or (xx - yy) % 3 == 0 else ROSE[2 + k])
        return
    suit = SUITS[i % 4]
    ink = suit_colour(suit)
    pip(p, x + 2, y + 2, suit, ink)
    ini = str(person["initials"])[:2]
    from ...holidays.pixel import measure
    p.text(cx - measure(ini, "35") // 2, cy, ini, ink, "35")


def painted_share(p: Pix, x, y, w, fill, night):
    """A contributor's share as a strip of white roses painted red as far as their commits go: the red lit along its
    top, the rest white card, in a rim of the card's grey."""
    k = -1 if night else 0
    p.box(x, y, w + 2, 4, CARD[1])
    for xx in range(w):
        red = xx < fill
        p.px(x + 1 + xx, y + 1, (ROSE[5 + k] if red else CARD[6 + k]))
        p.px(x + 1 + xx, y + 2, (ROSE[3] if red else CARD[4 + k]))


def wreath(p: Pix, cx, cy, r0, r1, n, night):
    """A wreath of the clipped hedge round the seal from r0 to r1, its leaves lit on the upper left of the ring and
    in shade at its lower right, set with roses by turns red and white half painted red."""
    k = -2 if night else 0
    rnd = random.Random(int(cx * 3 + cy))
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if not r0 <= d <= r1:
                continue
            nx, ny = (xx + 0.5 - cx) / d, (yy + 0.5 - cy) / d
            lam = max(0.0, nx * LX + ny * LY)
            t = 2 + round(3 * lam) + rnd.choice((0, 0, 1, -1))
            if d > r1 - 1:
                t -= 1
            p.px(xx, yy, HEDGE[max(0, min(6, t + k))])
    rad = (r0 + r1) / 2
    for j in range(n // 2):
        ang = math.radians(j * 360 / (n // 2) - 90)
        rose(p, round(cx + math.cos(ang) * rad - 2.5), round(cy + math.sin(ang) * rad - 2.5), night,
             1.0 if j % 2 == 0 else 0.5)


def card_board(p: Pix, night):
    """The placard as a playing card laid in the garden: the page inside the clipped hedge, and inside the hedge a
    rim of the roses' red with a pip of each suit at its corners."""
    paper(p, night, uid="pl")
    frame(p, night)
    uid = f"{getattr(p, 'sheet', 'p')}h"
    p.shapes["base"].append(f'<rect width="{p.w}" height="{EDGE}" fill="url(#{uid})"/>')
    k = -1 if night else 0
    rim = ROSE[2 + k] if not night else ROSE[3]
    w, h = p.w, p.h
    for xx in range(EDGE + 1, w - EDGE - 1):
        p.px(xx, EDGE + 1, rim)
        p.px(xx, h - EDGE - 2, rim)
    for yy in range(EDGE + 2, h - EDGE - 2):
        p.px(EDGE + 1, yy, rim)
        p.px(w - EDGE - 2, yy, rim)


def warren(p: Pix, x0, g, night, motion, width=40, flutter=True, spring=50) -> tuple:
    """The left of the page, standing on the grass at row g from column x0: an arch of roses `width` wide, the moon in
    it by night and by day a butterfly fluttering round it (where the page has room over the arch, `flutter`), and
    under it the White Rabbit bounding along and looking at his watch, filling the arch, painted eggs hidden in the
    grass about his feet; the arch springs `spring` rows over the grass. Returns its span."""
    rose_arch(p, x0 + 1, x0 + 1 + width, g - spring, g, night)
    if night:
        moon(p, x0 + 1 + width // 2, g - spring - 2, 5)
    tulips(p, x0 + 1, g, night, (ROSE, GOLD, PINK))
    tulips(p, x0 + width - 8, g, night, (PINK, ROSE, GOLD))
    white_rabbit(p, x0 + 1 + (width - len(RABBIT[0])) // 2, g, night, motion)
    egg(p, x0 + 9, g, night, ROSE, BLUE)
    egg(p, x0 + width + 2, g, night, BLUE, GOLD)
    egg(p, x0 + width + 7, g, night, GOLD, ROSE)
    if not night and flutter:
        path = [(x0 + width // 2 - 5 + round((width // 2 - 9) * math.cos(i / 24 * 2 * math.pi)),
                 g - 58 + round(9 * math.sin(i / 12 * 2 * math.pi))) for i in range(24)]
        butterfly(p, path, motion)
    return (x0 - 1, x0 + 56)
