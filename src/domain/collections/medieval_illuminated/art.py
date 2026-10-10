# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Illuminated set's scenery and sprites, drawn on the shared pixel canvas.

A page from a scriptorium: vellum ruled by a scribe, a painted border of knotwork and gold leaf, a vine of
gilded leaves across the top, titles in gold leaf on a lapis or oxblood ground behind a decorated initial,
and in the margins what an illuminator drew there: the monk at his desk under his shelf of books, the
candle that lights him, a wyvern, a snail, a hare with a trumpet and birds on the vine; the great book open
on its lectern and the great quill in its inkhorn. Everything is lit from the one light in the upper left
and shaded on the set's own ramps and the collection's hand's, whose flame every candle burns with and
whose skins its people are painted in."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, Paint, Pix, fold, num, sphere, tube
from .palette import C, HAND, NIGHT_SKY, RAMP, X

G, O, B, V = RAMP["gold"], RAMP["oxblood"], RAMP["lapis"], RAMP["verdigris"]


# --------------------------------------------------------------------------- the vellum
def band_edges(y: int, h: int) -> list:
    """Where the night's bands begin, the rows `bg_at` says: band i holds every row y with y * n // h == i."""
    n = len(NIGHT_SKY)
    return [y + math.ceil(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, ruled=True, uid="p"):
    """The ground a drawing sits on: by day warm cream vellum with the faint ruling a scribe drew, a line
    every eight rows and the pricks he ruled from down each margin; by night the same vellum in a candlelit
    scriptorium, deep brown at the top and the foot and lit warm toward the middle, in bands."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
        line = C["ruling"]
    else:
        edges = band_edges(y, h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" '
                               f'fill="{col}"/>')
        line = C["ruling_n"]
    if ruled:
        p.defs.append(f'<pattern id="{uid}r" width="8" height="8" patternUnits="userSpaceOnUse">'
                      f'<rect y="7" width="8" height="1" fill="{line}"/></pattern>')
        p.under.append(f'<rect x="{x + 6}" y="{y + 4}" width="{w - 12}" height="{h - 8}" fill="url(#{uid}r)"/>')
        if not night and w > 60:
            pricks = {}
            for yy in range(y + 11, y + h - 5, 8):
                pricks.setdefault(yy, []).extend((x + 6, x + w - 7))
            p.under.append(f'<path stroke="{C["prick"]}" d="{Pix._d(pricks)}"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`."""
    if not night:
        return C["paper"]
    return NIGHT_SKY[min(len(NIGHT_SKY) - 1, y * len(NIGHT_SKY) // p.h)]


# --------------------------------------------------------------------------- the painted border
# The border's band, one tile: runs of lapis, oxblood and verdigris five pixels long, a bead of gold leaf
# between each pair, lit along the top and shaded along the foot.
BAND = (("lapis", 5), ("gold", 1), ("oxblood", 5), ("gold", 1), ("verdigris", 5), ("gold", 1), ("oxblood", 5),
        ("gold", 1))
TILE = sum(n for _, n in BAND)
FRAME = 4    # how many pixels the border takes from the edge: a gold fillet, the band two deep, a gold line


def _band_tile(night: bool, horizontal: bool, outer_first: bool) -> dict:
    """The cells of one tile of the border, laid along an edge: the gold fillet on the outside and the fine
    gold line on the inside (`outer_first` when the outside is the top or the left), the band between them
    lit along its top, or its left, and shaded along its other side."""
    k = -1 if night else 0
    lines = (0, 1, 2, 3) if outer_first else (3, 1, 2, 0)   # the fillet, the lit row, the shaded row, the line
    cells = {}

    def put(along, across, c):
        cells[(along, across) if horizontal else (across, along)] = c

    a = 0
    for name, n in BAND:
        R = RAMP[name]
        for i in range(n):
            if name == "gold":
                lit, shade = G[6], G[4]
            else:
                lit = R[5 + k] if i == n // 2 else R[4 + k]
                shade = R[2 + k]
            put(a + i, lines[1], lit)
            put(a + i, lines[2], shade)
        a += n
    for i in range(TILE):
        put(i, lines[0], G[5] if i % 6 == 1 else G[4])
        put(i, lines[3], G[2] if not night else G[3])
    return cells


def knot_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, uid="kf"):
    """The sheet's border: a fillet of gold leaf outside, a band of lapis, oxblood and verdigris with beads
    of gold between the colours, and a fine gold line inside, with a gilded quatrefoil at each corner. Each
    side is one pattern tile placed along it, so the border costs a few hundred bytes however long it
    runs. The foot and the right side differ from the head and the left only in which of their edges is
    the fillet and which the line, so a drawing made lighter lays the head's and the left's tiles along
    them too and draws those two edges over (see `_edges_over`)."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    sides = (("t", True, True, x, y, w, FRAME), ("b", True, False, x, y + h - FRAME, w, FRAME),
             ("l", False, True, x, y + FRAME, FRAME, h - 2 * FRAME),
             ("r", False, False, x + w - FRAME, y + FRAME, FRAME, h - 2 * FRAME))
    for name, horizontal, outer_first, bx, by, bw, bh in sides:
        if p.lite and not outer_first:
            p.shapes["base"].append(f'<use href="#{uid}{"T" if horizontal else "L"}" x="{bx}" y="{by}"/>')
            _edges_over(p, night, horizontal, bx, by, bw, bh, uid)
            continue
        cells = _band_tile(night, horizontal, outer_first)
        tw, th = (TILE, FRAME) if horizontal else (FRAME, TILE)
        p.defs.append(f'<pattern id="{uid}{name}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
                      f'{p._paths(cells)}</pattern>')
        # A rect kept in the defs and placed with a use, so the tiles start where the rect does.
        p.defs.append(f'<rect id="{uid}{name.upper()}" width="{bw}" height="{bh}" fill="url(#{uid}{name})"/>')
        p.shapes["base"].append(f'<use href="#{uid}{name.upper()}" x="{bx}" y="{by}"/>')
    for (cx, cy) in ((x + 2, y + 2), (x + w - 3, y + 2), (x + 2, y + h - 3), (x + w - 3, y + h - 3)):
        quatrefoil(p, cx, cy, night)


def _edges_over(p: Pix, night: bool, horizontal, bx, by, bw, bh, uid):
    """Over the head's (or the left's) tiles laid along the foot (or the right), the two edges they have the
    wrong way round: the fine gold line along the inner edge and the beaded fillet along the outer, the
    fillet one pattern tile of a bead every sixth pixel, placed so its tiles start where the side does."""
    line = G[2] if not night else G[3]
    tile = f"{uid}f{'h' if horizontal else 'v'}"
    if horizontal:
        inner, outer, size, pw, ph = (bx, by, bw, 1), (bx, by + bh - 1), (bw, 1), 6, 1
        bead = '<path stroke="{}" d="M0 .5h1m1 0h4"/><path stroke="{}" d="M1 .5h1"/>'
    else:
        inner, outer, size, pw, ph = (bx, by, 1, bh), (bx + bw - 1, by), (1, bh), 1, 6
        bead = '<path stroke="{}" d="M.5 0v1m0 1v4"/><path stroke="{}" d="M.5 1v1"/>'
    if ("pattern", tile) not in p.syms:
        p.defs.append(f'<pattern id="{tile}" width="{pw}" height="{ph}" patternUnits="userSpaceOnUse">'
                      f'{bead.format(G[4], G[5])}</pattern>')
        p.defs.append(f'<rect id="{tile.upper()}" width="{size[0]}" height="{size[1]}" fill="url(#{tile})"/>')
        p.syms[("pattern", tile)] = tile
    p.shapes["base"].append(f'<rect x="{inner[0]}" y="{inner[1]}" width="{inner[2]}" height="{inner[3]}" '
                            f'fill="{line}"/>')
    p.shapes["base"].append(f'<use href="#{tile.upper()}" x="{outer[0]}" y="{outer[1]}"/>')


def quatrefoil(p: Pix, cx, cy, night, L="base"):
    """A gilded quatrefoil five pixels square centred on (cx, cy), a lapis stone at its heart."""
    art = [".g.g.", "gGgGg", ".gLg.", "gGgGg", ".d.d."]
    p.sprite(cx - 2, cy - 2, art, {"g": G[5], "G": G[4], "d": G[3], "L": B[3 if not night else 4]}, 1, L,
             reuse=True)


def colophon_rule(p: Pix, x0, x1, y, night, L="near"):
    """The twisted cord along the top of a footer, the colophon's rule: two strands, one of oxblood and
    one of lapis, crossing each other every fourth pixel under a binding of gold, two rows deep from row
    `y`, lit along the top and shaded along the foot; one pattern tile hung from `x0` to `x1`, over
    whatever rules the cells draw up to it."""
    k = -1 if night else 0
    A, Bl = (O[4 + k], O[3 + k]), (B[4 + k], B[3 + k])
    cells = {}
    for i in range(8):
        if i % 4 == 3:
            cells[(i, 0)], cells[(i, 1)] = G[5], G[3]
            continue
        top, foot = (A, Bl) if i < 4 else (Bl, A)
        cells[(i, 0)], cells[(i, 1)] = top[0], foot[1]
    uid = "cr"
    if ("pattern", uid) not in p.syms:
        p.defs.append(f'<pattern id="{uid}" width="8" height="2" patternUnits="userSpaceOnUse">{p._paths(cells)}'
                      f'</pattern>')
        p.defs.append(f'<rect id="{uid.upper()}" width="{x1 - x0}" height="2" fill="url(#{uid})"/>')
        p.syms[("pattern", uid)] = uid
    if L not in p.layers:
        p.layer(L)
    p.shapes[L].append(f'<use href="#{uid.upper()}" x="{x0}" y="{y}"/>')
    for xx in (x0 - 1, x1):                                   # a bead of gold at either end
        p.px(xx, y, G[6], L)
        p.px(xx, y + 1, G[4], L)


def frame_glints(p: Pix, w, h, seed=0):
    """In a moving header, the gold beads of the border catch the light in turn: a bright pixel on every
    other bead along the top, the foot and the sides, twinkling on the three phases."""
    i = seed
    for bx in range(5, w - 5, TILE // 2):
        for by in (1, h - 3):
            p.px(bx, by, G[6], p.twinkle(i))
            i += 1
    for by in range(FRAME + 5, h - FRAME - 5, TILE // 2):
        for bx in (1, w - 3):
            p.px(bx, by, G[6], p.twinkle(i))
            i += 1


# --------------------------------------------------------------------------- the vine across the top
LEAF = ["Lg.", "GdL", ".Ld"]    # a gilded ivy leaf, lit on its upper left; L is the dark outline


def gilt_leaf(p: Pix, x, y, night=False, L="base", flip=False, reuse=True):
    """A gilded leaf three pixels square, top-left at (x, y), turned over when `flip`."""
    pal = {"g": G[6 if night else 5], "G": G[5 if night else 4], "d": G[3], "L": G[1]}
    p.sprite(x, y, LEAF, pal, 1, L, flip=flip, reuse=reuse)


def _sag(sp, sag, xx) -> int:
    """How far a span of the vine `sp` wide, sagging `sag` at its middle, hangs below its tacks at `xx`."""
    return round(sag * 4 * (xx / sp) * (1 - xx / sp))


def _vine_flower(sp, sag, night, variant) -> dict:
    """The flower that hangs under the sag of a span of the vine, oxblood or lapis as the spans alternate,
    with a bead of gold at its heart, as cells where it hangs in the span (see `_vine_span`)."""
    k = -1 if night else 0
    fx, fy = sp // 2, _sag(sp, sag, sp // 2) + 2
    R = O if variant % 2 == 0 else B
    cells = {(fx, fy): V[3 + k]}
    for (dx, dy, t) in ((0, 1, 5), (-1, 2, 4), (1, 2, 4), (0, 3, 3), (-1, 1, 4), (1, 1, 4), (-1, 3, 3), (1, 3, 3)):
        cells[(fx + dx, fy + dy)] = R[t + k]
    cells[(fx, fy + 2)] = G[6]
    return cells


def _vine_span(sp, sag, night, variant):
    """One span of the vine, tack to tack, as pixels: a verdigris stem two deep sagging `sag` rows at the
    middle, gilded leaves on short stalks above and below it by turns, and under the sag a flower, oxblood
    or lapis as the spans alternate, with a bead of gold at its heart (left off when `variant` is None)."""
    k = -1 if night else 0
    oy = 5
    q = Pix(sp + 2, oy + sag + 8)
    pts = [(xx, oy + _sag(sp, sag, xx)) for xx in range(sp)]
    for i, (xx, yy) in enumerate(pts):
        q.px(xx, yy, V[5 + k] if i % 9 == 4 else V[4 + k])
        q.px(xx, yy + 1, V[2 + k])
    for (a_, b_) in zip(pts, pts[1:]):
        if abs(a_[1] - b_[1]) > 1:
            for yy in range(min(a_[1], b_[1]) + 1, max(a_[1], b_[1]) + 1):
                q.px(a_[0], yy, V[3 + k])
    mid = sp // 2
    # Leaves hang under the stem by the tacks, where it runs just under the border, and stand over it where
    # it has sagged; the middle is left for a bird to perch on.
    for off, above in ((5, False), (mid - 7, True), (mid + 7, True), (sp - 6, False)):
        if not 2 <= off < sp - 3:
            continue
        xx, yy = off, pts[off][1]
        if above:
            q.px(xx, yy - 1, V[3 + k])
            gilt_leaf(q, xx - 1, yy - 4, night, flip=off > mid, reuse=False)
        else:
            q.px(xx, yy + 2, V[3 + k])
            gilt_leaf(q, xx - 1, yy + 3, night, flip=off > mid, reuse=False)
    cells = {(x, y - oy): c for (x, y), c in q.layers["base"].items()}
    if variant is not None:
        cells.update(_vine_flower(sp, sag, night, variant))
    return cells


def tacks(x0, x1, span) -> list:
    """Where the vine across a sheet from x0 to x1 is tacked: at the sheet's middle, under the month's mark,
    and every `span` units out from it to either side, the vine's two ends hung as the same shorter span. So the
    mark covers a tack and the leaves on either side of it whole, or none of them, and cuts no leaf."""
    mid = (x0 + x1) // 2
    n = (mid - x0) // span
    out = [mid + k * span for k in range(-n, n + 1)]
    end = mid - x0 - n * span
    return ([x0] if end else []) + out + ([mid + n * span + end] if end else [])


def vine(p: Pix, x0, x1, y, span=45, sag=3, night=False):
    """The vine across a sheet's top: swagged from tack to tack (see `tacks`), each span drawn once and hung
    again, a gold boss at every tack, its two ends hung as a shorter span without a flower. The two kinds of
    span differ only in their flower, so a drawing made lighter draws the span once without it and each kind
    as that span and its flower."""
    xs = tacks(x0, x1, span)
    for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
        sp = xb - xa
        if sp < 8:
            continue
        variant = i % 2 if sp == span else None
        key = ("vine", sp, sag, night, variant)
        if key not in p.syms:
            if p.lite and variant is not None:
                bare = p.symbol(("vine", sp, sag, night, None), _vine_span(sp, sag, night, None))
                p.symbol(key, _vine_flower(sp, sag, night, variant), shapes=f'<use href="#{bare}"/>')
            else:
                p.symbol(key, _vine_span(sp, sag, night, variant))
        p.use(key, xa, y)
    for xa in xs:
        key = ("boss", night)
        if key not in p.syms:
            p.symbol(key, {(0, -1): G[5], (-1, 0): G[5], (0, 0): G[6], (1, 0): G[4], (0, 1): G[3]})
        p.use(key, min(xa, x1 - 2), y)


def vine_low(x0, x1, span, sag, i) -> tuple:
    """Where the `i`-th span of the vine across a sheet from x0 to x1 hangs lowest: the column of its middle and
    the stem's row there, counted from where it is tacked."""
    xs = tacks(x0, x1, span)
    sp = xs[i + 1] - xs[i]
    mid = sp // 2
    return xs[i] + mid, round(sag * 4 * (mid / sp) * (1 - mid / sp))


# --------------------------------------------------------------------------- gold leaf for the titles
def leaf_fill(r, c, scale, night):
    """The colour a title's letter takes at row `r` and column `c` of the letter, counted in canvas pixels
    from its top-left: gold leaf laid on gesso, bright along the crown of each letter and deepening toward
    its foot, with a streak of burnish running down it on the diagonal where the leaf catches the light. By
    night every band is a tone lighter: the gold glows in candlelight."""
    band = min(6, r // scale)
    t = (5, 5, 4, 4, 4, 3, 3)[band] + (1 if night else 0)
    if (c - r) % 20 < 3:
        t += 1
    return G[min(6, t)]


# The titles' gold leaf: a tile twenty canvas pixels wide, so the burnish crosses every letter once or so.
LEAF_PAINT = Paint("leaf", leaf_fill, period=20)
# The grounds the gold is laid on, by day and by night: the panel's ramp and the initial's square's. The
# panel takes the ramp's second tone, deep enough for every band of the leaf to hold 4.5:1 on it, its
# diaper the third; the square takes the other pigment's third.
GROUNDS = {False: (B, O), True: (O, B)}


def _glyph(p: Pix, ch: str) -> str:
    """The id of a title's letter, drawn once a file as one path that takes the stroke of where it is used,
    as the canvas sets every letter."""
    key = ("glyph", "57", ch)
    if key not in p.syms:
        p.symbol(key, {(col, r): 1 for r, cols in enumerate(FONTS["57"][0][ch][1]) for col in cols}, mono=True)
    return p.syms[key]


def _edged(g: str, scale, edge, shadow) -> str:
    """The shadow and the dark edge of what the symbol `g` draws, in its own units: the shadow half a font
    pixel down and to the right, the edge a pixel out on every side."""
    d, off = num(1 / scale), num(max(1, scale // 2) / scale)
    return (f'<use href="#{g}" x="{off}" y="{off}" stroke="{shadow}"/><g stroke="{edge}">'
            + "".join(f'<use href="#{g}" {a}="{sg}{d}"/>' for a in "xy" for sg in ("-", "")) + "</g>")


def title_edge(p: Pix, x, y, s, scale, edge, shadow, L="base"):
    """What a title's letters stand on, drawn before them: a shadow half a font pixel down and to the
    right, as gilding raised on gesso throws, and a fine dark edge a pixel wide round every letter. Each
    letter's edge and shadow are one symbol, kept once a file for each letter and size and placed once a
    letter, so a long title stays light."""
    glyphs, _, space = FONTS["57"]
    cx = x
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = _glyph(p, ch)
        key = ("edge", ch, scale, edge, shadow)
        if key not in p.syms:
            p.symbol(key, {}, shapes=_edged(g, scale, edge, shadow))
        p.use(key, cx, y, L, scale=scale)
        cx += (glyphs[ch][0] + 1) * scale


def _along(p: Pix, s: str, ids) -> tuple[str, int]:
    """The uses that set a line of a title in its letters' own units, a use of `ids(ch)` where each letter
    stands, and the line's width in those units."""
    glyphs, _, space = FONTS["57"]
    parts, cx = [], 0
    for ch in s:
        if ch == " ":
            cx += space + 1
            continue
        parts.append(f'<use href="#{ids(ch)}" x="{cx}"/>' if cx else f'<use href="#{ids(ch)}"/>')
        cx += glyphs[ch][0] + 1
    return "".join(parts), cx - 1


def title_line(p: Pix, s: str) -> int:
    """A line of a title as one symbol, kept under the key ("line", s): its letters in their own units, each
    where it stands, so the whole line is placed at once wherever it is wanted, under the gold for its
    edge, in gold, round it for the glow and through a mask for the glint. Returns its width in those
    units."""
    shapes, n = _along(p, s, lambda ch: _glyph(p, ch))
    if ("line", s) not in p.syms:
        p.symbol(("line", s), {}, shapes=shapes)
    return n


def _grown(g: str, scale, ring, alpha) -> str:
    """What the symbol `g` draws grown by `ring` canvas pixels on every side, seen through `alpha`: a title's
    glow, as the canvas draws one, each letter's runs that much longer and its rows that much taller. Here
    the letters are placed once at every offset within the ring, in a group seen through the alpha whole,
    so where the copies overlap the glow is no stronger."""
    steps = [num(k / scale) for k in range(-ring, ring + 1)]
    uses = "".join(f'<use href="#{g}"' + (f' x="{dx}"' if dx != "0" else "") + (f' y="{dy}"' if dy != "0" else "")
                   + "/>" for dy in steps for dx in steps)
    return f'<g opacity="{num(alpha)}">{uses}</g>'


def title_set(p: Pix, x, y, s, scale, night, edge, shadow, glow=None, L="base") -> int:
    """A line of a title set whole: its letters made one symbol (see `title_line`) and placed once for each
    thing the letters are, the shadow and the dark edge under them, their gold leaf, and by night their glow
    (`glow`, a colour and the alpha of each ring, outermost first) in the haze behind (see `_grown`). The
    same drawing as `title_edge` under the letters set one by one, in the bytes of a few letters, for a
    drawing made lighter to fit its budget. The line's box is kept with the words, so nothing is set on it.
    Returns its width."""
    n = title_line(p, s)
    line = p.syms[("line", s)]
    key = ("line edge", s, scale, edge, shadow)
    if key not in p.syms:
        p.symbol(key, {}, shapes=_edged(line, scale, edge, shadow))
    p.use(key, x, y, L, scale=scale)
    if glow:
        col, alphas = glow
        for i, a in enumerate(alphas):
            halo = ("line glow", s, scale, len(alphas) - i, a)
            if halo not in p.syms:
                p.symbol(halo, {}, shapes=_grown(line, scale, len(alphas) - i, a))
            p.use(halo, x, y, "haze", stroke=col, scale=scale)
    p.use(("line", s), x, y, L, stroke=f"url(#{p._pattern(LEAF_PAINT, scale, night)})", scale=scale)
    w = n * scale
    rows = max((len(FONTS["57"][0][ch][1]) for ch in s if ch != " "), default=0)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    return w


def _diaper(p: Pix, col: str) -> str:
    """A diaper of dots in `col`, two to every eight pixels square, as a pattern drawn once a file."""
    pid = f"dp{col[1:]}"
    if ("pattern", pid) not in p.syms:
        p.defs.append(f'<pattern id="{pid}" width="8" height="8" patternUnits="userSpaceOnUse">'
                      f'<path stroke="{col}" d="M0 .5h1m3 4h1"/></pattern>')
        p.syms[("pattern", pid)] = pid
    return pid


def title_ground(p: Pix, x, y, s, w, scale, night, versal=True):
    """The ground a title's gold is laid on, behind the letters: a panel of lapis by day and oxblood by
    night, a hairline of gold inside its edge and a diaper of lighter dots across it; and when `versal`,
    the first letter's own square in the other pigment, standing a row proud of the panel above and below,
    framed in gold with white penwork dotted inside the frame and curls in its corners: the decorated
    initial. The panel and the square are shapes, so a title costs what its letters cost. Returns the box
    of the initial's square, or None."""
    ground, other = GROUNDS[night]
    Lp = p.layer("panel", z=-22)
    x0, y0, x1, y1 = x - 3, y - 2, x + w + 3, y + 7 * scale + 2
    p.shapes[Lp].append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{ground[1]}"/>')
    p.shapes[Lp].append(f'<rect x="{x0 + 3}" y="{y0 + 3}" width="{x1 - x0 - 6}" height="{y1 - y0 - 6}" '
                        f'fill="url(#{_diaper(p, ground[2])})"/>')
    first = fold(s, "57")[:1] if versal else ""
    if not first or first == " ":
        p.box(x0 + 1, y0 + 1, x1 - x0 - 2, y1 - y0 - 2, G[3], Lp)
        return None
    gw = FONTS["57"][0][first][0] * scale
    sx1 = x + gw + 3
    p.hline(sx1 - 1, x1 - 1, y0 + 1, G[3], Lp)                 # the panel's hairline, beyond the square
    p.hline(sx1 - 1, x1 - 1, y1 - 2, G[3], Lp)
    p.vline(x1 - 2, y0 + 1, y1 - 1, G[3], Lp)
    p.shapes[Lp].append(f'<rect x="{x0}" y="{y0 - 1}" width="{sx1 - x0}" height="{y1 - y0 + 2}" '
                        f'fill="{other[2]}"/>')
    p.box(x0 + 1, y0, sx1 - x0 - 2, y1 - y0, G[4], Lp)
    p.hline(x0 + 1, sx1 - 1, y0, G[5], Lp)
    p.vline(x0 + 1, y0, y1, G[5], Lp)
    pen = RAMP["vellum"][6]
    for xx in range(x0 + 3, sx1 - 3, 2):                        # penwork dotted inside the frame
        p.px(xx, y0 + 1, pen, Lp)
        p.px(xx, y1 - 2, pen, Lp)
    for yy in range(y0 + 3, y1 - 3, 2):
        p.px(x0 + 2, yy, pen, Lp)
        p.px(sx1 - 3, yy, pen, Lp)
    for (cx, cy, dx, dy) in ((x0 + 2, y0 + 1, 1, 1), (sx1 - 3, y0 + 1, -1, 1), (x0 + 2, y1 - 2, 1, -1),
                             (sx1 - 3, y1 - 2, -1, -1)):
        p.px(cx, cy, G[6], Lp)                                     # a curl of gold in each corner
        p.px(cx + dx, cy, G[5], Lp)
        p.px(cx, cy + dy, G[5], Lp)
        if scale >= 3:
            p.px(cx + dx, cy + dy, other[4], Lp)
            p.px(cx + 2 * dx, cy, G[3], Lp)
            p.px(cx, cy + 2 * dy, G[3], Lp)
    return (x0, y0 - 1, sx1, y1 + 1)


def title_glint(p: Pix, x, y, s, scale, w, n):
    """In a moving header a glint of burnish crosses a title's gold leaf on the hand's period, once every
    `HAND.glint` seconds: a slanted band of the palest gold, laid on the letters alone through a mask of their
    glyphs, sweeps across the title from left to right in the first two fifths of the period and rests beyond
    it for the rest. The still twin keeps the burnish painted into the leaf. A line set whole (see
    `title_set`) is masked by its one symbol."""
    glyphs, _, space = FONTS["57"]
    uses, cx = [], x
    if ("line", s) in p.syms:
        uses.append(f'<use href="#{p.syms[("line", s)]}" transform="translate({x} {y}) scale({scale})"/>')
    else:
        for ch in fold(s, "57"):
            if ch == " ":
                cx += (space + 1) * scale
                continue
            uses.append(f'<use href="#{p.syms[("glyph", "57", ch)]}" transform="translate({cx} {y}) '
                        f'scale({scale})"/>')
            cx += (glyphs[ch][0] + 1) * scale
    tall = 7 * scale
    mid = f"gl{n}"
    p.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x - 1}" y="{y - 1}" width="{w + 2}" '
                  f'height="{tall + 2}"><g stroke="{C["white"]}">{"".join(uses)}</g></mask>')
    reach = w + tall + 5
    band = f"M{x - tall} {y}h5l{tall} {tall}h-5z"
    p.raw(0.5, f'<g mask="url(#{mid})"><path fill="{C["white"]}" fill-opacity=".7" d="{band}"><animateTransform '
               f'attributeName="transform" type="translate" values="0;{reach};{reach}" keyTimes="0;.4;1" '
               f'dur="{num(HAND.glint)}s" repeatCount="indefinite"/></path></g>', "")


def flourish(p: Pix, box, night, side, L="near"):
    """The bar that grows from a decorated initial into the margin, as the illuminators drew: a bar of
    gold leaf a pixel off the panel's side (`side` -1 for the left margin, 1 for the right), running from
    the panel's foot to above its head, where it curls outward into a tendril with gilded ivy leaves and
    a bud of oxblood, or of lapis by night. Nothing hangs below the panel, where the tagline is set."""
    k = -1 if night else 0
    x0, y0, x1, y1 = box
    bx = x0 - 3 if side < 0 else x1 + 2
    top = y0 - 4
    for yy in range(top, y1 - 1):
        p.px(bx, yy, G[5] if yy % 5 == 2 else G[4], L)
        p.px(bx - side, yy, G[2], L)
    p.px(bx, y1 - 1, G[3], L)
    p.px(bx - side, y1 - 1, G[1], L)
    for (dx, dy) in ((0, -1), (-1, -2), (-2, -3), (-3, -3), (-4, -2), (-5, -1)):
        p.px(bx + side * dx, top + dy, V[4 + k] if dy == -3 else V[3 + k], L)
    gilt_leaf(p, bx + side * 4 - 1, top - 7, night, L, flip=side < 0, reuse=False)
    gilt_leaf(p, bx + side * 7 - 1, top - 2, night, L, flip=side < 0, reuse=False)
    R = B if night else O
    for (dx, dy, t) in ((-2, 1, 4), (-3, 1, 3), (-2, 2, 3), (-3, 2, 2)):
        p.px(bx + side * dx, top + dy, R[t + k], L)
    p.px(bx + side * -2, top + 1, G[6], L)
    gilt_leaf(p, bx + side * 3 - 1, (y0 + y1) // 2 - 1, night, L, flip=side < 0, reuse=False)
    p.px(bx + side * 2, (y0 + y1) // 2, V[3 + k], L)


def room(p: Pix, x0, y0, x1, y1) -> bool:
    """Whether a box touches no word and nothing yet drawn, and lies inside the sheet's border."""
    if x0 < FRAME + 1 or y0 < FRAME + 1 or x1 > p.w - FRAME - 1 or y1 > p.h - FRAME - 1:
        return False
    if not p.clear_of_words(x0, y0, x1, y1):
        return False
    for name in ("base", "near", "panel"):
        cells = p.layers.get(name, {})
        if any((xx, yy) in cells for xx in range(x0, x1) for yy in range(y0, y1)):
            return False
    return True


# --------------------------------------------------------------------------- light
def glow_cells(cx, cy, rx, ry, col, alphas, skip=()):
    """A small stepped glow as see-through pixels around (cx, cy), leaving out the pixels in `skip`."""
    out, n = {}, len(alphas)
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d < 1 and (x, y) not in skip:
                out[(x, y)] = f"{col}:{alphas[min(n - 1, int((1 - d) * n))]:g}"
    return out


def lamp(p: Pix, cx, cy, r, phase, own=(), pool=None):
    """Register a flame at (cx, cy): once everything is drawn, `candlelight` lays its warm light on
    whatever stands within `r` of it, flickering with the flame, and pools it on the vellum round the
    flame, `pool` being how far the pool reaches across and down. `own` are the flame's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own), pool))


def candlelight(p: Pix, night: bool):
    """The finishing pass, by night only: each candle's light pooled on the vellum round it, warm at the
    flame and falling off into the brown, flickering with the flame behind everything drawn; and on the
    drawn things near it, the monk, his hands and his page, the desk, the book, strongest nearest the
    flame. The words take none of it, and where the edge of a pool reaches behind a word the word still
    holds 4.5:1 on it. A drawing made lighter to fit its budget leaves off the faintest, outermost ring of
    each light, on the vellum and on what it falls on; the two rings within are as they always are."""
    if not night:
        return
    base = p.layers["base"]
    col = RAMP["flame"][5]
    alphas = (0.12, 0.2, 0.3)
    n = len(alphas)
    for (cx, cy, r, phase, own, pool) in p.lamps:
        if pool:
            rx, ry = pool
            if p.lite:
                p.halo(cx, cy + ry * 0.3, rx * 2 / 3, ry * 2 / 3, col, (0.18, 0.3), L=p.flicker(phase, back=True))
            else:
                p.halo(cx, cy + ry * 0.3, rx, ry, col, (0.09, 0.18, 0.3), L=p.flicker(phase, back=True))
        Lf = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if (x, y) not in base or (x, y) in own:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1) / r
                ring = int((1 - d) * n)
                if d < 1 and (ring or not p.lite):
                    p.apx(x, y, col, alphas[min(n - 1, ring)], Lf)


def shadow_under(p: Pix, cx, y, rx):
    """The soft shadow a thing standing on the rule throws on the vellum beside its foot."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.6, X["shade_ink"], (0.07, 0.13), L="pool", shape=False)


# --------------------------------------------------------------------------- candles
def candle(p: Pix, x, base, h=28, night=False, L="base", phase=0, motion=True, stick=True):
    """A candle on an iron pricket stand, its foot on row `base` and the candle's wick `h` rows above it:
    a spreading foot, a shaft with a knop, a drip pan, and a cream candle run with wax. By night its flame
    burns, a teardrop white at the heart and orange at the edge, that flickers with its glow in a moving
    file and lights what stands near it. By day it is unlit, its wick black."""
    A, Ve, F = RAMP["ash"], RAMP["vellum"], RAMP["flame"]
    k = -1 if night else 0
    top = base - h
    if stick:
        for (dx, c) in ((-2, A[3]), (-1, A[4]), (0, A[3]), (1, A[2]), (2, A[1])):
            p.px(x + dx, base, c, L)
        p.px(x - 1, base - 1, A[3], L)
        p.px(x, base - 1, A[3], L)
        p.px(x + 1, base - 1, A[2], L)
        for yy in range(top + 8, base - 1):
            p.px(x, yy, A[3] if yy % 5 else A[4], L)
        knop = base - (h // 2)
        for dx, c in ((-1, A[4]), (0, A[3]), (1, A[2])):
            p.px(x + dx, knop, c, L)
        for dx, c in ((-2, A[4]), (-1, A[4]), (0, A[3]), (1, A[3]), (2, A[2])):
            p.px(x + dx, top + 7, c, L)
    for yy in range(top, top + 7):
        p.px(x - 1, yy, Ve[6 + k], L)
        p.px(x, yy, Ve[5 + k], L)
        p.px(x + 1, yy, Ve[4 + k], L)
    p.px(x - 1, top, Ve[5 + k], L)
    p.px(x + 1, top + 2, Ve[6 + k], L)
    p.px(x + 1, top + 3, Ve[6 + k], L)
    p.px(x - 2, top + 1, Ve[6 + k], L)
    p.px(x, top - 1, RAMP["ink"][0], L)
    if not night:
        return
    Lf = p.flicker(phase) if motion else L
    flame = ((0, -2, F[6]), (0, -3, F[6]), (0, -4, F[5]), (0, -5, F[4]), (0, -6, F[3]), (-1, -3, F[4]), (1, -3, F[4]),
             (-1, -2, F[3]), (1, -2, F[3]), (-1, -4, F[4]), (1, -4, F[3]))
    for (dx, dy, c) in flame:
        p.px(x + dx, top + dy, c, Lf)
    own = {(x + dx, top + dy) for dx, dy, _ in flame}
    for (qx, qy), c in glow_cells(x + 0.5, top - 3, 4.6, 5.4, F[4], (0.12, 0.24), own).items():
        p.px(qx, qy, c, Lf)
    tall = h > 20
    lamp(p, x + 0.5, top - 3, 40 if tall else 16, phase,
         own | {(x + dx, yy) for dx in (-2, -1, 0, 1, 2) for yy in range(top - 1, base + 1)},
         pool=(44, 32) if tall else (18, 9))


def candle_stub(p: Pix, x, base, night=False, L="base"):
    """A stub of candle on a brass dish, where a corner has no room for a stand: the dish on row `base`,
    five wide about `x`, the candle three rows above it and its wick, nine rows in all with its flame. By
    night the flame burns and lights what lies near; by day the wick is black."""
    Ve, F = RAMP["vellum"], RAMP["flame"]
    k = -1 if night else 0
    for (dx, c) in ((-2, G[3]), (-1, G[4]), (0, G[4]), (1, G[3]), (2, G[2])):
        p.px(x + dx, base, c, L)
    for (dx, c) in ((-2, G[5]), (-1, G[5]), (0, G[4]), (1, G[4]), (2, G[3])):
        p.px(x + dx, base - 1, c, L)
    for yy in range(base - 4, base - 1):
        p.px(x - 1, yy, Ve[6 + k], L)
        p.px(x, yy, Ve[5 + k], L)
        p.px(x + 1, yy, Ve[4 + k], L)
    p.px(x, base - 5, RAMP["ink"][0], L)
    if not night:
        return
    flame = ((0, -6, F[6]), (0, -7, F[5]), (0, -8, F[3]), (-1, -6, F[4]), (1, -6, F[3]), (-1, -7, F[3]))
    for (dx, dy, c) in flame:
        p.px(x + dx, base + dy, c, L)
    own = {(x + dx, base + dy) for dx, dy, _ in flame}
    for (qx, qy), c in glow_cells(x + 0.5, base - 6.5, 3.6, 4.2, F[4], (0.12, 0.24), own).items():
        p.px(qx, qy, c, L)
    stub = {(x + dx, yy) for dx in (-2, -1, 0, 1, 2) for yy in range(base - 5, base + 1)}
    lamp(p, x + 0.5, base - 6.5, 11, 0, own | stub, pool=(16, 7))


# --------------------------------------------------------------------------- the monk at his desk
# Tones: A to F the habit, lit to its outline; s t u r the skin, on the hand's light skin, lit to shaded; H h
# the hair; k the eye and mouth.
MONK = [
    "....................ssss..........",
    "..................sssssst.........",
    ".................sssssssst........",
    ".................hhhsssstHH.......",
    ".................HHHHHHHHHH.......",
    ".................HHssstttHH.......",
    "..................sssttttH........",
    "..................skstkttu........",
    "..................ssttttuu........",
    "...................ssttur.........",
    "...................stkttu.........",
    "....................ttuu..........",
    "..................FFFuuFFF........",
    "...............FFFBBBBBBBBFFF.....",
    ".............FFBBAABBBBBBBBBBFF...",
    "............FBBAAABBBBBBBBBBBBBF..",
    "...........FBBAAABBBBBBBBCBBBBBBF.",
    "..........FBBAAABBBBBBBBBCCBBBBBBF",
    "..........FBAAABBBBBBBBBBBCCBBBBBF",
    ".........FBBAAABBFBBBBBBBBFCCBBBBF",
    ".........FBAAABBFBBBBBBBBBBFCCBBBF",
    ".........FBAABBBFBBBBBBBBBBBFCCBBF",
    "..........FBABBBFBBBBBBBBBBBFBCCBF",
    "..........FBBBBFBBBBBBBBBBBBBFBCBF",
    "...........FBBBFBBBBBBBBBBBBBFBBBF",
    "...........FBBBFBBBBBBBBBBBBBFBBBF",
    "............FBBF.............FBBF.",
    "............FutF.............FtuF.",
    "............uttu.............tuut.",
    ".............uu...............uu..",
]
MONK_PAL = {"A": "habit:5", "B": "habit:4", "C": "habit:3", "D": "habit:2", "E": "habit:1", "F": "habit:0",
            "s": "skin0:4", "t": "skin0:3", "u": "skin0:2", "r": "skin0:2", "H": "ink:3", "h": "ink:4", "k": "ink:0"}


def _pal(spec: dict, night: bool, lift: int = 0) -> dict:
    """A sprite's palette from `ramp:tone` names, every tone `lift` steps lighter by night."""
    out = {}
    for ch, name in spec.items():
        ramp, t = name.split(":")
        t = int(t) + (lift if night else 0)
        out[ch] = RAMP[ramp][max(0, min(6, t))]
    return out


def scriptorium_desk(p: Pix, x, base, night=False, L="base"):
    """The scribe's slanted desk, its feet on row `base` and its left edge at `x`, 42 wide: the sloped top
    seen from the front, a page of vellum lying on it with its lines written and its rubric and initial
    painted, an inkhorn set in the top corner, a lip along the near edge, a carved front panel and two
    legs on a stretcher."""
    W, Ve, I = RAMP["wood"], RAMP["vellum"], RAMP["ink"]
    k = -1 if night else 0
    far, near = base - 21, base - 12
    for yy in range(far, near + 1):
        t = (yy - far) / (near - far)
        left, right = x + 3 - round(3 * t), x + 39 + round(3 * t)
        for xx in range(left, right + 1):
            c = W[4 + k] if yy % 3 or (xx * 5 + yy) % 9 else W[3 + k]
            if yy == far:
                c = W[5 + k]
            elif yy == near:
                c = W[6 + k] if xx < right - 2 else W[4 + k]
            elif xx == left:
                c = W[5 + k]
            elif xx == right:
                c = W[2 + k]
            p.px(xx, yy, c, L)
    for yy in range(far + 1, near):                         # the page
        t = (yy - far - 1) / (near - far - 2)
        left, right = x + 12 - round(2 * t), x + 34 + round(2 * t)
        for xx in range(left, right + 1):
            c = Ve[6 + k] if xx < right - 1 else Ve[5 + k]
            if yy == near - 1:
                c = Ve[4 + k]
            p.px(xx, yy, c, L)
        if yy in (far + 2, far + 4, far + 6) and yy < near - 1:
            for xx in range(left + 4, right - 2):
                if (xx + yy) % 7 not in (0, 3):
                    p.px(xx, yy, I[3 if yy != far + 2 else 2], L)
    R = RAMP["oxblood"]
    for xx in range(x + 16, x + 21):                       # the rubric and the initial on the page
        p.px(xx, far + 2, R[3 + k], L)
    p.rect(x + 12, far + 2, 3, 3, RAMP["lapis"][3 + k], L)
    p.px(x + 13, far + 3, G[5], L)
    for (dx, dy, c) in ((36, 0, I[1]), (37, 0, I[1]), (38, 0, I[2]), (36, 1, I[1]), (37, 1, I[3]), (38, 1, I[1]),
                        (37, 2, I[1]), (37, 3, I[0]), (36, -1, I[1]), (37, -1, I[2]), (38, -1, I[1])):
        p.px(x + dx, far + 2 + dy, c, L)                     # the inkhorn
    for yy in range(near + 1, base - 3):                    # the front panel
        for xx in range(x + 2, x + 41):
            inner = x + 7 <= xx <= x + 35 and near + 3 <= yy <= base - 6
            c = W[2 + k] if inner else W[3 + k]
            if inner and (xx == x + 7 or yy == near + 3):
                c = W[1 + k]
            elif inner and (xx == x + 35 or yy == base - 6):
                c = W[4 + k]
            elif xx == x + 2:
                c = W[4 + k]
            elif xx == x + 40:
                c = W[1 + k]
            p.px(xx, yy, c, L)
    for yy in range(base - 3, base + 1):                    # the legs and the stretcher
        for xx in (x + 3, x + 4, x + 38, x + 39):
            p.px(xx, yy, W[3 + k] if xx in (x + 3, x + 38) else W[1 + k], L)
        if yy == base - 2:
            for xx in range(x + 5, x + 38):
                p.px(xx, yy, W[2 + k], L)
    quatrefoil(p, x + 21, base - 7, night, L)


QUILL = [
    "..........ff",
    ".........fff",
    "........ffe.",
    "........fe..",
    ".......ffe..",
    ".......fe...",
    "......ffe...",
    "......fe....",
    ".....fe.....",
    ".....fe.....",
    "....ee......",
    "....e.......",
    "...e........",
    "...e........",
    "..e.........",
    "..a.........",
]


def quill(p: Pix, x, y, night=False, L="base", up=0, reach=16):
    """A quill, its nib at (x, y), the feather leaning up and to the right: a grey shaft and a white vane
    with a cut end, `reach` rows of it from the nib up. `up` lifts the nib a row, the hand between
    strokes."""
    A, Ve = RAMP["ash"], RAMP["vellum"]
    k = -1 if night else 0
    art = QUILL[len(QUILL) - reach:]
    p.sprite(x - 2, y - up - len(art) + 1, art, {"f": Ve[6 + k], "e": A[4 + k], "a": RAMP["ink"][0]}, 1, L)


def monk_at_desk(p: Pix, x, base, night=False, motion=True):
    """The monk at his desk, 42 wide from `x` and 46 tall from row `base`: tonsured, in a brown habit, bent
    over the page, a penknife in his left hand holding the page down and a quill in his right. In a moving
    file he writes for three seconds, lifts his quill a moment and writes again."""
    scriptorium_desk(p, x, base, night)
    pal = _pal(MONK_PAL, night)
    p.sprite(x + 4, base - 47, MONK, pal)
    A = RAMP["ash"]
    k = -1 if night else 0
    hx, hy = x + 4 + 13, base - 47 + 27                    # the left hand, and the knife point down from it
    p.px(hx + 1, hy - 1, RAMP["wood"][4 + k])
    p.px(hx + 1, hy - 2, RAMP["wood"][3 + k])
    for i in range(1, 4):
        p.px(hx + 1, hy + 1 + i, A[5 + k] if i < 3 else A[3 + k])
    qx, qy = x + 4 + 31, base - 47 + 29                    # the right hand's quill
    if not motion:
        quill(p, qx, qy + 1, night)
        return
    for i, (t0, t1, up) in enumerate(((0.0, 0.7, 0), (0.7, 1.0, 1))):
        Lq = p.seq(f"qu{i}", t0, t1, 4.2, keep=i == 0, z=1)
        quill(p, qx, qy + 1, night, Lq, up=up)


# --------------------------------------------------------------------------- creatures in the margin
# The wyvern's head, facing left, its horns swept back: 1 its outline, 3 and 4 its scales, 5 lit, h its
# horns, e its eye, a its teeth.
WYVERN_HEAD = [
    "......hh....",
    ".....1h11h..",
    "....1554h41.",
    "...154e44441",
    "..1544444441",
    ".15444444441",
    "1aa3344441..",
    ".1133334411.",
]
WYVERN_PAL = {"1": "verdigris:0", "3": "verdigris:2", "4": "verdigris:3", "5": "verdigris:4", "h": "ash:5",
              "e": "gold:6", "a": "ash:6", "x": "oxblood:4", "w": "oxblood:3", "l": "oxblood:5", "b": "ink:2"}
# Its wing, spread and raised, its root at the lower left: two fingers of bone fanning out from the arm,
# the membrane between them scalloped at its edge, lit (x, l) along the leading edge and in shade (w)
# toward the body.
WING = [
    ["..........b......", ".........blb...b.", "........blxb..bb.", ".......blxxbbxxb.", "......blxxxbxxxb.",
     ".....blxxxxbxxwb.", "....blxxxxbxwwwb.", "...blxxxxbxwwwwb.", "..blxxxxbwwwwwb..", ".blxxxbbwwwwwb...",
     ".bxxbbwwwwwwb....", "bbbbwwwwwwwb.....", "...bbbbbbbb......"],
    ["......b..........", ".....blb.........", "....blxb....b....", "....blxb...bb....", "...blxxb..bxb....",
     "...blxxbbbxxb....", "..blxxxbxxxxwb...", "..blxxxbxxxwwb...", ".blxxxbxxwwwwb...", ".blxxbbxwwwwb....",
     "bbxxbwwwwwwb.....", "bbbbwwwwwwb......", "...bbbbbbb......."],
]
WYVERN_LEG = [".13.", "134.", "1341", ".1a1", ".aa."]


def _scales(night: bool):
    """A colour for each pixel of the wyvern's body: verdigris scales on its back, darkest along the ridge,
    and gold leaf along its belly, each lit by the tube's light."""
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        if o > 0.4:
            return G[5 if lam > 0.55 else 4 if lam > 0.25 else 3]
        v = 1.7 + 2.9 * lam - k
        if (x + 2 * y) % 4 == 0:
            v -= 0.8
        if o < -0.65:
            v -= 0.9
        return V[max(1, min(5, round(v)))]
    return colour


def wyvern(p: Pix, x, y, night=False, motion=True, L="base"):
    """The wyvern coiled in the margin, 36 wide and 40 tall, top-left at (x, y): its head turned to the
    page, its neck arched, its body coiled down and round with its tail curled under it, verdigris
    scales on its back and gold leaf along its belly, a horn, a gold eye, two clawed legs, and a bat's
    wing of oxblood that it raises and folds again every five seconds and a half in a moving file."""
    scales = _scales(night)
    tail = [(x + 18.5, y + 31.5), (x + 11.5, y + 32.5), (x + 6.5, y + 29.5), (x + 6.5, y + 24.5), (x + 11.5, y + 21.5),
            (x + 16.5, y + 22.5)]
    body = [(x + 10.5, y + 8.5), (x + 16.5, y + 6.5), (x + 23.5, y + 9.5), (x + 28.5, y + 15.5), (x + 29.5, y + 22.5),
            (x + 25.5, y + 28.5), (x + 18.5, y + 31.5)]
    tube(p, tail, 2.1, scales, L, outline=V[0])
    tube(p, body, 3.3, scales, L, outline=V[0])
    spade = ["..1..", ".141.", "14441", ".141.", "..1.."]
    p.sprite(x + 15, y + 19, spade, {"1": V[0], "4": G[4]}, 1, L)   # the spade at the end of its tail
    pal = _pal(WYVERN_PAL, night)
    p.sprite(x, y + 2, WYVERN_HEAD, pal, 1, L)
    p.px(x + 6, y + 5, RAMP["ink"][0], L)                     # the pupil
    p.px(x - 1, y + 8, RAMP["redlead"][4], L)                  # its tongue
    p.px(x - 2, y + 7, RAMP["redlead"][4], L)
    for (lx, ly) in ((x + 29, y + 24), (x + 24, y + 30)):
        p.sprite(lx, ly, WYVERN_LEG, pal, 1, L)
    for i in range(1, 7):                                     # the spines along its back
        sx, sy = x + 22 + i * 1.3, y + 5 + (i * i) // 5
        p.px(round(sx), round(sy), V[1], L)
    if not motion:
        p.sprite(x + 15, y - 5, WING[0], pal, 1, L)
        return
    for i, (t0, t1) in enumerate(((0.0, 0.6), (0.6, 1.0))):
        Lw = p.seq(f"wy{i}", t0, t1, 5.6, keep=i == 0, z=1)
        p.sprite(x + 15, y - 5, WING[i], pal, 1, Lw)


# The hare standing to blow its trumpet, facing right: W X Y its fur, P its belly, k its eye.
HARE = [
    ".W..W....",
    ".WX.WX...",
    ".WX.WX...",
    ".WWWWW...",
    ".WWkWW...",
    ".WWWWWP..",
    "..WWWX...",
    ".XWWWWX..",
    ".XWWWWWX.",
    ".XWPPWWX.",
    ".XWPPWWX.",
    ".XWWWWWX.",
    "..XWWWX..",
    "..XWWWWX.",
    ".XWWWWWXX",
    ".XX..XX..",
]
HARE_PAL = {"W": "wood:5", "X": "wood:3", "Y": "wood:2", "P": "vellum:6", "k": "ink:0"}


def hare_trumpeter(p: Pix, x, base, night=False, motion=True, L="base"):
    """A hare standing on its hind legs on row `base`, its left edge at `x`, blowing a gold trumpet that
    points up to the right; in a moving file notes come out of its bell in turn, a note every second and a
    half."""
    pal = _pal(HARE_PAL, night, 1)
    p.sprite(x, base - 15, HARE, pal, 1, L)
    k = -1 if night else 0
    mx, my = x + 7, base - 10                               # the mouthpiece, and the tube rising to the right
    for i in range(9):
        xx, yy = mx + i, my - (i + 1) // 2
        p.px(xx, yy, G[6] if i % 4 == 2 else G[5], L)
        p.px(xx, yy + 1, G[3], L)
    bx, by = mx + 9, my - 5                                 # the bell, flaring
    for (dx, dy, t) in ((0, -1, 5), (0, 0, 5), (0, 1, 4), (0, 2, 3), (1, -2, 6), (1, -1, 5), (1, 0, 4), (1, 1, 4),
                        (1, 2, 3), (1, 3, 2), (2, -2, 5), (2, 3, 2)):
        p.px(bx + dx, by + dy, G[t], L)
    for (dx, dy) in ((2, -1), (2, 0), (2, 1), (2, 2)):
        p.px(bx + dx, by + dy, G[2], L)                       # the bell's dark mouth
    p.px(x + 6, base - 8, pal["W"], L)                      # a paw on the tube
    p.px(x + 7, base - 8, pal["X"], L)
    notes = ((bx + 5, by - 2), (bx + 7, by - 5), (bx + 4, by - 7))
    for i, (nx, ny) in enumerate(notes):
        if not motion and i:
            break
        Ln = p.seq(f"nt{i}", round(i / 3, 3), round((i + 1) / 3, 3), 4.5, keep=i == 0, z=1) if motion else L
        for (dx, dy) in ((1, 0), (1, 1), (2, 1), (1, 2), (0, 3), (1, 3)):
            p.px(nx + dx, ny + dy, RAMP["ink"][2 + k], Ln)


SNAIL = [
    "...WWWW..",
    "..WXZXXW.",
    ".WXZYZXW.",
    ".WXZZXXW.",
    "stWWWWWW.",
    "ttttttt..",
]
SNAIL_PAL = {"W": "wood:5", "X": "wood:4", "Y": "wood:2", "Z": "wood:1", "s": "ash:5", "t": "ash:4", "k": "ink:1"}


def snail(p: Pix, x, base, night=False, L="base", flip=False):
    """A snail on row `base`, 9 wide, creeping left from `x` with its eyes up on their stalks; `flip`
    turns it to creep right."""
    pal = _pal(SNAIL_PAL, night, 1)
    p.sprite(x, base - 5, SNAIL, pal, 1, L, flip=flip)
    ex = x + (8 if flip else 0)
    d = -1 if flip else 1
    p.px(ex, base - 3, pal["t"], L)
    p.px(ex, base - 4, pal["k"], L)
    p.px(ex + d, base - 4, pal["t"], L)
    p.px(ex + d, base - 5, pal["k"], L)


BIRD = [
    ["....ll...", "...lLLLkm", "lLLLGGGL.", ".lLLLLLL.", "..lLLLL..", "...a..a.."],
    ["..l.lll..", "...lLLLkm", "lLLLGGGL.", ".lLLLLLL.", "..lLLLL..", "...a..a.."],
]
BIRD_PAL = {"l": "lapis:5", "L": "lapis:4", "G": "gold:5", "k": "ink:0", "m": "redlead:4", "a": "ash:3"}
BIRD_RED = {"l": "oxblood:5", "L": "oxblood:4", "G": "gold:5", "k": "ink:0", "m": "ash:6", "a": "ash:3"}


def bird(p: Pix, x, y, night=False, motion=True, red=False, L="base", flip=False):
    """A small bird perched with its feet on row `y + 5`, 9 wide, top-left at (x, y): lapis or oxblood
    with a gold breast, an orange beak and dark feet, facing right (left when `flip`); in a moving file
    it lifts its wings now and then, every four seconds and more on one of three beats. A drawing made
    lighter keeps each beat's two frames once, for every bird that flaps on it."""
    pal = _pal(BIRD_RED if red else BIRD_PAL, night, 1)
    if not motion:
        p.sprite(x, y, BIRD[0], pal, 1, L, flip=flip)
        return
    for i, (t0, t1) in enumerate(((0.0, 0.7), (0.7, 1.0))):
        Lb = p.seq(f"bd{x % 3 if p.lite else x}{i}", t0, t1, 4.2 + 0.6 * (x % 3), keep=i == 0, z=1)
        p.sprite(x, y, BIRD[i], pal, 1, Lb, flip=flip)


# --------------------------------------------------------------------------- the books
def codex(p: Pix, x, y, w=13, cover="oxblood", night=False, L="base"):
    """A closed book lying flat, `w` wide and 4 tall, top-left at (x, y): its cover in the pigment named,
    the page block showing cream at the fore-edge, a gold clasp at the middle of its edge."""
    R, Ve = RAMP[cover], RAMP["vellum"]
    k = -1 if night else 0
    for xx in range(x, x + w):
        p.px(xx, y, R[4 + k], L)
        p.px(xx, y + 1, R[3 + k] if xx < x + w - 2 else Ve[5 + k], L)
        p.px(xx, y + 2, R[3 + k] if xx < x + w - 2 else Ve[4 + k], L)
        p.px(xx, y + 3, R[1 + k], L)
    p.px(x, y, R[5 + k], L)
    p.px(x + w - 1, y + 1, G[5], L)
    p.px(x + w - 1, y + 2, G[3], L)
    p.px(x + 2, y + 1, G[4], L)
    p.px(x + 2, y + 2, G[3], L)


# --------------------------------------------------------------------------- the great book on its lectern
# The letter the great book's first page opens with: the B of Beatus vir, the first psalm, the page a psalter
# painted most richly, set in gold leaf on a square of lapis.
BEATUS = "B"


def _lines(p: Pix, x0, x1, y0, y1, c, L, seed=0):
    """Lines of writing on a page, a row of words every second row from y0 to y1 and from x0 to x1, a gap
    between the words, and now and then a paragraph ending short."""
    for i, yy in enumerate(range(y0, y1, 2)):
        end = x1 - (3 + (seed + i) % 5 if i % 4 == 3 else 0)
        for xx in range(x0, end):
            if (xx * 3 + yy * 5 + seed) % 11 not in (0, 6):
                p.px(xx, yy, c, L)


def great_book(p: Pix, x, y, w, h, night=False, L="base"):
    """A great book lying open, `w` wide and `h` tall with its top-left at (x, y), as it lies on a lectern
    seen from the front: covers of oxblood leather showing round two pages of vellum that curve down into the
    gutter, the edges of the leaves in stripes along their foot. The left page opens with a decorated initial,
    the B of Beatus vir in gold leaf on lapis in a gold frame, a bar of oxblood running down the margin from
    it, and is written in iron-gall ink with a rubric in red; the right page has a miniature in a gold frame,
    the sun in gold leaf over a verdigris hill and a tower on it under a lapis sky, and is written below it.
    Two ribbons, lapis and oxblood, hang from the gutter below the book. By night it is a tone darker but
    the gold, which candlelight finds. A book under 40 wide, a phone's, is painted more simply at its size:
    its initial a square of lapis framed in gold, its miniature a sun over the hill."""
    Ve, I = RAMP["vellum"], RAMP["ink"]
    k = -1 if night else 0
    big = w >= 40
    mid = x + w // 2
    half = w // 2 - 2
    foot = y + h - 1
    # the covers: lit along the top and the left, in shade along the right and the foot, the corners rounded
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx in (x, x + w - 1)) and (yy in (y, foot)):
                continue
            c = O[3 + k]
            if yy == y or xx == x:
                c = O[4 + k]
            elif xx == x + w - 1 or yy == foot:
                c = O[1 + k]
            p.px(xx, yy, c, L)
    for (bx, by) in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, foot - 2), (x + w - 3, foot - 2)):
        if big:
            p.rect(bx, by, 2, 2, G[4], L)                           # a boss of gold on each corner
        p.px(bx, by, G[6], L)
    for (bx, by) in ((x, y + h // 2 - 1), (x + w - 1, y + h // 2 - 1)):
        p.vline(bx, by, by + 3, G[5] if bx == x else G[3], L)       # and a clasp at each side
    # the leaves: their tops dip into the gutter, the left page in the light and the right a tone lower,
    # each shaded toward the gutter, and the stripes of their edges along the foot
    tops = {}
    for xx in range(x + 2, x + w - 2):
        d = abs(xx - mid) / half
        tops[xx] = y + 1 + round((3 if big else 2) * max(0.0, 1 - d) ** 2)
        for yy in range(tops[xx], foot - 2):
            if xx == mid:
                c = Ve[2 + k]
            elif xx < mid:
                c = Ve[4 + k] if xx >= mid - 2 else Ve[6 + k]
            else:
                c = Ve[4 + k] if xx <= mid + 1 else Ve[5 + k]
            p.px(xx, yy, c, L)
        if xx != mid:
            p.px(xx, foot - 2, Ve[4 + k], L)
            p.px(xx, foot - 1, Ve[3 + k] if (xx - x) % 3 else Ve[2 + k], L)
    for xx in (x + 2, x + w - 3):                                   # the leaves' outer edges
        for yy in range(tops[xx] + 2, foot - 4):
            p.px(xx, yy, Ve[5 + k] if xx < mid else Ve[3 + k], L)
    top = y + (5 if big else 3)
    # the left page: the initial in its frame, the bar running down the margin, and the writing
    lx0, lx1 = (x + 6, mid - 4) if big else (x + 4, mid - 2)
    ini_w, ini_h = (9, 11) if big else (5, 5)
    p.rect(lx0, top, ini_w, ini_h, B[3 + k], L)
    p.box(lx0, top, ini_w, ini_h, G[3], L)
    p.hline(lx0, lx0 + ini_w, top, G[5], L)
    p.vline(lx0, top, top + ini_h, G[5], L)
    if big:
        glyph = FONTS["57"][0][BEATUS][1]
        for r, cols in enumerate(glyph):
            for col in cols:
                p.px(lx0 + 2 + col, top + 2 + r, G[5] if r < 3 else G[4], L)
        p.px(lx0 + 1, top + 1, G[6], L)
        for yy in range(top + ini_h, foot - 4):                    # the bar of oxblood and its leaf
            p.px(lx0 + 1, yy, O[3 + k] if yy % 4 else G[4], L)
        gilt_leaf(p, lx0, foot - 6, night, L, reuse=False)
    else:
        p.px(lx0 + 2, top + 2, G[6], L)
    _lines(p, lx0 + (3 if big else 0), lx1, top + ini_h + 2, foot - 4, I[3 + k], L, seed=1)
    _lines(p, lx0 + ini_w + 2, lx1, top + 1, top + ini_h + 1, I[3 + k], L, seed=4)
    for xx in range(lx0 + ini_w + 2, lx1 - 2):                      # the rubric under the initial
        if (xx * 3 + 5) % 11 not in (0, 6):
            p.px(xx, top + ini_h + 2, O[3 + k], L)
    # the right page: the miniature in its frame, and the writing under it
    rx0, rx1 = (mid + 4, x + w - 6) if big else (mid + 2, x + w - 4)
    mh = max(9 if big else 5, (foot - top) * 2 // 5)
    p.rect(rx0, top, rx1 - rx0, mh, B[3 + k], L)
    p.rect(rx0 + 1, top + 1, rx1 - rx0 - 2, max(1, mh // 3), B[4 + k], L)
    hill = top + mh * 3 // 5
    for xx in range(rx0 + 1, rx1 - 1):                              # the hill
        crest = hill + round(2 * abs(xx - (rx0 + rx1) / 2) / max(1, (rx1 - rx0) / 2))
        for yy in range(crest, top + mh - 1):
            p.px(xx, yy, V[4 + k] if yy == crest else V[3 + k], L)
    if big:
        tx = rx0 + (rx1 - rx0) * 3 // 5                              # the tower on the hill
        for yy in range(hill - 5, hill + 1):
            p.px(tx, yy, Ve[6 + k], L)
            p.px(tx + 1, yy, Ve[5 + k], L)
            p.px(tx + 2, yy, Ve[3 + k], L)
        p.px(tx + 1, hill - 3, I[1], L)
        for dx, c in ((-1, O[4 + k]), (0, O[4 + k]), (1, O[3 + k]), (2, O[3 + k]), (3, O[2 + k])):
            p.px(tx + dx, hill - 6, c, L)
        p.px(tx + 1, hill - 7, O[3 + k], L)
        sx, sy = rx0 + 4, top + 3                                    # the sun in gold leaf
        for dx, dy, t in ((0, -1, 5), (-1, 0, 5), (0, 0, 6), (1, 0, 4), (0, 1, 4)):
            p.px(sx + dx, sy + dy, G[t], L)
    else:
        p.px(rx0 + 2, top + 2, G[6], L)
    p.box(rx0, top, rx1 - rx0, mh, G[4], L)                          # its frame
    p.hline(rx0, rx1, top, G[5], L)
    p.vline(rx0, top, top + mh, G[5], L)
    p.hline(rx0 + 1, rx1, top + mh - 1, G[2], L)
    p.vline(rx1 - 1, top + 1, top + mh, G[2], L)
    _lines(p, rx0, rx1, top + mh + 2, foot - 4, I[3 + k], L, seed=7)
    # the ribbons hanging from the gutter
    hang = 7 if big else 4
    for cx, R in ((mid - 2, B), (mid + 1, O)):                       # each cut on the slant at its end
        for yy in range(foot - 4, foot + hang):
            p.px(cx, yy, R[4 + k], L)
            if yy < foot + hang - 1:
                p.px(cx + 1, yy, R[3 + k] if yy < foot + hang - 2 else R[2 + k], L)
    return mid


def lectern_stand(p: Pix, cx, top, base, w, night=False, L="base"):
    """The stand a great book `w` wide lies on, centred on cx: a ledge of oak across under the book from row
    `top`, lit along its top, the book's foot resting against it; a block under it narrowing into a turned post
    with a carved ring under the block and a knop halfway down; and a spreading foot on row `base`."""
    W = RAMP["wood"]
    k = -1 if night else 0
    x0, x1 = cx - w // 2 - 2, cx + w // 2 + 2
    for xx in range(x0, x1):                                          # the ledge
        p.px(xx, top, W[6 + k] if xx < x1 - 2 else W[4 + k], L)
        p.px(xx, top + 1, W[4 + k], L)
        p.px(xx, top + 2, W[2 + k], L)
    for j in range(4):                                               # the block, narrowing
        hw = max(3, w // 5 - j * (w // 5 - 3) // 3)
        for xx in range(cx - hw, cx + hw + 1):
            p.px(xx, top + 3 + j, W[(4 if xx < cx - hw // 2 else 3 if xx < cx + hw // 2 else 2) + k], L)
    knop = (top + 7 + base) // 2
    for yy in range(top + 7, base - 3):                              # the post, turned
        hw = 4 if yy in (knop - 1, knop, knop + 1) else 3 if yy in (top + 8, knop - 3, knop + 3) else 2
        for dx in range(-hw, hw + 1):
            t = 5 if dx < -1 else 4 if dx < 1 else 3 if dx < 2 else 2
            p.px(cx + dx, yy, W[t + k], L)
    for dx, t in ((-4, 5), (-3, 5), (-2, 6), (-1, 5), (0, 4), (1, 4), (2, 3), (3, 3), (4, 2)):
        p.px(cx + dx, knop, G[t], L)                                # its knop gilded
    p.px(cx - 2, knop - 1, G[6], L)
    for dx in range(-11, 12):                                        # the foot, in two steps
        t = 5 if dx < -5 else (4 if dx < 1 else (3 if dx < 6 else 2))
        p.px(cx + dx, base, W[t + k], L)
        if abs(dx) <= 8:
            p.px(cx + dx, base - 1, W[(6 if dx < -4 else 4 if dx < 2 else 3) + k], L)
        if abs(dx) <= 4:
            p.px(cx + dx, base - 2, W[(5 if dx < 0 else 3) + k], L)
            p.px(cx + dx, base - 3, W[(4 if dx < 0 else 2) + k], L)


def book_on_lectern(p: Pix, x, base, w, h, stand, night=False, L="base"):
    """The great book `w` wide and `h` tall (see `great_book`) open on its lectern (see `lectern_stand`),
    the stand `stand` rows tall from its ledge to its foot on row `base`, its left edge at `x`. Returns the
    column of the book's gutter."""
    top = base - stand
    lectern_stand(p, x + w // 2, top, base, w, night, L)
    return great_book(p, x, top - h + 2, w, h, night, L)


# --------------------------------------------------------------------------- the great quill in its inkhorn
def feather(p: Pix, nib, tip, night=False, L="base", reach=0.3, wide=8.0):
    """A goose quill from its nib at `nib` (x, y) to the tip of its feather at `tip`, on a gentle bow: the bare
    barrel of the quill in its lower part, pale and catching the light, and from `reach` of the way up the
    feather, a narrow vane on its left in the light and a broad one on its right in shade, `wide` across at the
    most, grey goose down drawn round with a darker edge, a dark spine up its middle, the barbs on the slant and
    a notch or two in the edge where they have parted. Returns the feather's cells."""
    A = RAMP["ash"]
    k = -1 if night else 0
    (nx, ny), (tx, ty) = nib, tip
    rows = ny - ty
    cells = {}
    for j in range(rows + 1):
        u = j / rows                                                # 0 at the nib, 1 at the tip
        yy = ny - j
        x0 = round(nx + (tx - nx) * u + 2.0 * math.sin(math.pi * u))   # the spine, bowed to the right
        if u < reach:
            cells[(x0, yy)] = A[6 + k] if j % 6 else A[5 + k]
            cells[(x0 + 1, yy)] = A[4 + k]
            continue
        f = (u - reach) / (1 - reach)
        width = wide * min(1.0, 3.2 * f) * (1 - f) ** 0.55
        left, right = round(width * 0.5), round(width)
        notch = j % 9 == 4
        for dx in range(-left, right + 1):
            edge = dx in (-left, right)
            if notch and dx == right and right > 2:
                continue
            if dx == 0:
                c = A[3 + k]
            elif dx < 0:
                c = A[4 + k] if edge else A[6 + k]
            elif edge:
                c = A[2 + k]
            else:
                c = A[4 + k] if (dx + j) % 3 == 0 else A[5 + k]
            cells[(x0 + dx, yy)] = c
    for (xx, yy), c in cells.items():
        p.px(xx, yy, c, L)
    return cells


INKHORN = ["..111111111..", ".12223333221.", "1223333333221", ".12233333221.", ".12233333221.", ".gGGGgggggd..",
           ".12233333221.", ".12233333221.", "..123333321..", "..123333321..", "..gGGggggd...", "..12233321...",
           "...1223321...", "...1222221...", "....11111...."]


def great_inkhorn(p: Pix, x, base, night=False, L="base"):
    """A great inkhorn in its oak stand on row `base`, 22 wide from `x` and 19 tall: the stand a block of oak
    lit along its top and in shade along its foot and its right, and set in it a horn of dark leather bound
    in two bands of gold, its mouth flared, black ink shining in it. Returns the column and row of the
    middle of its mouth."""
    W, I = RAMP["wood"], RAMP["ink"]
    k = -1 if night else 0
    for j, t in enumerate((6, 4, 3, 2)):                             # the stand
        for xx in range(x + (1 if j == 0 else 0), x + (21 if j == 0 else 22)):
            p.px(xx, base - 3 + j, W[(t if xx < x + 20 else max(1, t - 2)) + k], L)
    hx, hy = x + 4, base - 4 - len(INKHORN)
    p.sprite(hx, hy, INKHORN, {"1": I[0], "2": I[1], "3": I[2], "g": G[4], "G": G[5], "d": G[2]}, 1, L)
    p.px(hx + 3, hy + 1, RAMP["lapis"][5], L)                        # the ink shining
    p.px(hx + 4, hy + 1, I[3], L)
    return hx + 6, hy


def great_quill(p: Pix, x, base, top, night=False, L="base", wide=8.0):
    """The scribe's great quill standing in his great inkhorn: the inkhorn in its stand on row `base` from `x`
    (see `great_inkhorn`) and the quill rising from inside it to row `top`, leaning a little to the left, its
    feather as tall as the room it has and `wide` across at its broadest. Returns the feather's cells."""
    mx, my = x + 10, base - 4 - len(INKHORN)
    lean = max(4, (my - top) // 6)
    cells = feather(p, (mx, my + 6), (mx - lean, top), night, L, wide=wide)
    great_inkhorn(p, x, base, night, L)
    return cells


def inkstand(p: Pix, x, base, night=False, L="base"):
    """A scribe's inkstand on row `base`, 24 wide and 28 tall from `x`: a wooden stand holding the inkhorn,
    black ink shining in it, with the quill standing in it leaning to the right, a pounce pot of vellum
    beside it, and the penknife lying in front."""
    W, I, A, Ve = RAMP["wood"], RAMP["ink"], RAMP["ash"], RAMP["vellum"]
    k = -1 if night else 0
    for xx in range(x + 2, x + 20):                      # the stand
        p.px(xx, base - 3, W[5 + k] if xx < x + 18 else W[3 + k], L)
        p.px(xx, base - 2, W[4 + k] if xx < x + 18 else W[2 + k], L)
        p.px(xx, base - 1, W[3 + k] if xx < x + 18 else W[1 + k], L)
    for xx in (x + 3, x + 4, x + 17, x + 18):
        p.px(xx, base, W[(3 if xx < x + 10 else 1) + k], L)
    horn = ["...11...", "..1221..", "..1231..", ".12231..", ".122331.", "1223331.", "12233311", "01222310", ".011110."]
    p.sprite(x + 4, base - 12, horn, {"0": I[0], "1": I[1], "2": I[2], "3": I[3]}, 1, L)
    p.px(x + 7, base - 12, I[3], L)
    p.px(x + 8, base - 12, RAMP["lapis"][5], L)         # the ink shining
    quill(p, x + 8, base - 13, night, L, reach=16)
    for yy in range(base - 8, base - 3):                 # the pounce pot
        for dx in range(5):
            c = Ve[(5 if dx < 2 else 4 if dx < 4 else 3) + k]
            if yy == base - 8:
                c = Ve[6 + k] if dx else Ve[4 + k]
            p.px(x + 13 + dx, yy, c, L)
    p.px(x + 15, base - 9, W[2 + k], L)
    for i in range(9):                                   # the penknife
        p.px(x + 10 + i, base, A[6] if i < 6 else W[(4 if i < 8 else 2) + k], L)
    p.px(x + 10, base - 1, A[6], L)
    for i in range(1, 6):
        p.px(x + 10 + i, base - 1, A[4 + k], L)


def inkhorn(p: Pix, x, base, night=False, L="base", pen=True, knife=True):
    """An inkhorn in its wooden stand on row `base`, 7 wide and 8 tall from `x`, black ink shining in it,
    and when `pen` a quill standing in it, leaning to the right; when `knife` the penknife lies beside it."""
    W, I, A = RAMP["wood"], RAMP["ink"], RAMP["ash"]
    k = -1 if night else 0
    for xx in range(x, x + 7):
        p.px(xx, base, W[3 + k] if xx < x + 5 else W[1 + k], L)
        p.px(xx, base - 1, W[4 + k] if xx < x + 5 else W[2 + k], L)
    for (dx, dy, c) in ((1, -2, I[1]), (2, -2, I[1]), (3, -2, I[2]), (4, -2, I[1]), (1, -3, I[1]), (2, -3, I[3]),
                        (3, -3, I[2]), (4, -3, I[1]), (1, -4, I[1]), (2, -4, I[2]), (3, -4, I[1]), (4, -4, I[1]),
                        (2, -5, I[1]), (3, -5, I[1]), (1, -5, I[0]), (4, -5, I[0]), (2, -6, I[0]), (3, -6, I[0])):
        p.px(x + dx, base + dy, c, L)
    p.px(x + 2, base - 6, RAMP["lapis"][5], L)             # the ink's shine
    if pen:
        quill(p, x + 3, base - 7, night, L, reach=12)
    if not knife:
        return
    for i in range(6):                                     # the penknife
        p.px(x + 8 + i, base, A[5 + k] if i < 4 else W[3 + k], L)
    p.px(x + 8, base - 1, A[6], L)
    p.px(x + 13, base - 1, W[4 + k], L)


def foot_vine(p: Pix, x0, x1, y, night=False, L="base"):
    """The floor of a colophon, a vine running along its foot from x0 to x1 just inside the border: a stem of
    verdigris two rows deep on rows `y` and `y + 1`, lit along its top, with a gilded leaf rising from it every
    seventh column and a flower of oxblood or lapis now and then. It runs only where it keeps two units clear of
    every word and of what already stands on the foot, so the cells' rules come down to it and a candle or an
    inkhorn stands in it. Returns the columns it runs along."""
    k = -1 if night else 0
    base = p.layers["base"]

    def free(xx, top):
        return p.clear_of_words(xx - 2, top - 2, xx + 3, y + 4) and not any(
            (xx + dx, yy) in base for dx in (-1, 0, 1) for yy in range(top, y + 2))
    run = [xx for xx in range(x0, x1) if free(xx, y)]
    sprigs = [xx for xx in range(x0 + 3, x1 - 3, 7) if all(free(xx + dx, y - 4) for dx in (-1, 0, 1, 2))]
    for xx in run:
        p.px(xx, y, V[5 + k] if xx % 9 == 4 else V[4 + k], L)
        p.px(xx, y + 1, V[2 + k], L)
    for i, xx in enumerate(sprigs):
        p.px(xx, y - 1, V[3 + k], L)
        if i % 4 == 3:
            R = O if i % 8 == 3 else B
            for (dx, dy, t) in ((0, -3, 5), (-1, -2, 4), (1, -2, 4), (0, -2, 5)):
                p.px(xx + dx, y + dy, R[t + k], L)
            p.px(xx, y - 2, G[6], L)
        else:
            gilt_leaf(p, xx - (0 if i % 2 else 2), y - 4, night, L, flip=i % 2 == 0)
    return run


# The books standing on the scriptorium's shelf, left to right: each its cover's pigment, its height and its
# width, the fourth leaning on the third.
SHELF_BOOKS = (("oxblood", 10, 3), ("lapis", 8, 3), ("vellum", 9, 2), ("verdigris", 7, 3), ("oxblood", 9, 2),
               ("tyrian", 10, 3), ("lapis", 7, 2))


def book_shelf(p: Pix, x0, x1, y, night=False, L="base"):
    """A shelf of oak on the scriptorium's wall from x0 to x1, its top on row `y`, on two brackets: lit along
    its top and in shade under its edge, and on it the books put by standing up, bound in oxblood, lapis,
    verdigris, Tyrian purple and plain vellum, each lit down its left side with a band of gold across its spine,
    and a scroll lying at the end. Returns the highest row the books reach."""
    W = RAMP["wood"]
    k = -1 if night else 0
    for xx in range(x0, x1):
        p.px(xx, y, W[5 + k], L)
        p.px(xx, y + 1, W[3 + k], L)
        p.px(xx, y + 2, W[1 + k], L)
    for bx in (x0 + 3, x1 - 4):                                       # the brackets
        for j in range(3):
            p.px(bx, y + 3 + j, W[3 + k], L)
            if j < 2:
                p.px(bx + 1, y + 3 + j, W[2 + k], L)
    xx, top = x0 + 2, y
    for i, (cover, h, w) in enumerate(SHELF_BOOKS):
        R = RAMP[cover]
        lean = i == 3
        for dx in range(w):
            for j in range(h):
                yy = y - 1 - j
                sx = xx + dx + (j // 4 if lean else 0)
                c = R[(5 if dx == 0 else 4 if dx < w - 1 else 3) + k]
                if j in (2, h - 3):
                    c = G[4] if dx < w - 1 else G[3]                  # the gold bands on the spine
                p.px(sx, yy, c, L)
        top = min(top, y - h)
        xx += w + (2 if lean else 0)
    for dx in range(min(9, x1 - xx - 2)):                           # the scroll lying at the end
        p.px(xx + 1 + dx, y - 1, RAMP["vellum"][4 + k], L)
        p.px(xx + 1 + dx, y - 2, RAMP["vellum"][6 + k], L)
    return top


def scribe_corner(p: Pix, x, base, night=False, L="base"):
    """The scribe's corner, the design's mark at the end of a colophon, 40 wide from `x` with its foot on row
    `base`: two bound books lying one on another, the inkhorn with its quill standing in it on them, and a candle
    on its pricket beside them, unlit by day and burning by night with its light pooled round it. Returns the
    columns it stands on."""
    for (bx, by, cover, w) in ((x, base - 3, "oxblood", 16), (x + 1, base - 7, "lapis", 14)):
        codex(p, bx, by, w, cover, night, L)
    inkhorn(p, x + 4, base - 8, night, L, knife=False)
    codex(p, x + 18, base - 3, 12, "verdigris", night, L)
    candle(p, x + 34, base, h=17, night=night, phase=2, motion=False, L=L)
    shadow_under(p, x + 9, base, 9)
    shadow_under(p, x + 34, base, 3)
    return (x - 1, x + 38)


def rubric_mark(p: Pix, x, y, night=False, L="base"):
    """The rubricator's paragraph mark in red, three wide and six tall from (x, y), set in the gutter
    before the first line of a colophon's notes."""
    k = -1 if night else 0
    p.sprite(x, y, ["oo.", "lOO", "oOO", ".O.", ".O.", ".o."], {"o": O[3 + k], "O": O[2 + k], "l": O[4 + k]}, 1, L)


def quill_flat(p: Pix, x, y, night=False, L="base"):
    """A quill lying on the page, its nib at the left on row `y + 2`, thirteen wide and three tall from
    (x, y): the cream vane lit along its top and shaded along its underside, so it stands off the vellum,
    the grey shaft, the nib cut black."""
    A, Ve = RAMP["ash"], RAMP["vellum"]
    k = -1 if night else 0
    art = [".....ffffff..", "..eeFFFFFFFFf", "ae.eddddddddd"]
    p.sprite(x, y, art, {"f": Ve[6 + k], "F": Ve[5 + k], "d": Ve[3 + k], "e": A[4 + k], "a": RAMP["ink"][0]}, 1, L)


# --------------------------------------------------------------------------- small gilt things
MEDALLION = [
    "..ggg..",
    ".gGGGg.",
    "gGLgLGd",
    "gGgggGd",
    "gGLgLGd",
    ".dGGGd.",
    "..ddd..",
]


def medallion(p: Pix, x, y, night=False, L="base", reuse=False):
    """A gilded medallion seven pixels across, top-left at (x, y): a disc of gold leaf bevelled from the
    upper left with a cross of gold on a lapis field."""
    pal = {"g": G[5], "G": G[4], "d": G[3], "L": B[3 if not night else 4]}
    p.sprite(x, y, MEDALLION, pal, 1, L, reuse=reuse)


FLEURON = ["..g..", ".gGg.", "gGdGd", ".dGd.", "..d.."]


def fleuron(p: Pix, x, y, L="base", reuse=True):
    """A gilded fleuron five pixels square, top-left at (x, y), lit on its upper left."""
    p.sprite(x, y, FLEURON, {"g": G[6], "G": G[5], "d": G[3]}, 1, L, reuse=reuse)


def gilt_star(p: Pix, x, y, L="base", big=False):
    """A star of gold leaf, five pixels square (seven when `big`), top-left at (x, y), with a glint at its
    heart."""
    if big:
        art = ["...g...", "...g...", ".ggGgg.", "gGGwGGd", ".dgGdd.", "...d...", "...d..."]
    else:
        art = ["..g..", ".gGd.", "gGwGd", ".dGd.", "..d.."]
    p.sprite(x, y, art, {"g": G[6], "G": G[4], "d": G[2], "w": C["white"]}, 1, L)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, painted in oxblood and lit on its upper-left lobe, with a glint of gold."""
    art = [".54.43.", "5443321", "4433211", ".33211.", "..211..", "...1..."]
    p.sprite(x, y, art, {str(i): O[i] for i in range(7)}, 1, L)
    p.px(x + 1, y + 1, G[6], L)


def gilt_bar(p: Pix, x0, y0, w, h, period=5):
    """A bar of gold leaf and lapis by turns, `period` pixels a stripe: lit along the top, shaded along
    the bottom."""
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
        for xx in range(x0, x0 + w):
            gold = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (G[6], G[4], G[2])[band] if gold else (B[4], B[3], B[1])[band])


def leaves_on(p: Pix, x0, x1, y, seed=7, L="base", night=False, gap=(22, 40)):
    """Gilded ivy leaves resting along a rule whose row is `y`, on a scrap of stem, a leaf every twenty
    pixels or so, and now and then a flower of oxblood or lapis. None lies where it would touch a word."""
    rnd = random.Random(seed * 131 + x0)
    k = -1 if night else 0
    x = x0 + rnd.randint(2, 9)
    i = 0
    while x < x1 - 4:
        if p.clear_of_words(x - 1, y - 5, x + 4, y):
            if i % 4 == 3:
                R = O if i % 8 == 3 else RAMP["lapis"]
                for (dx, dy, t) in ((1, -3, 5), (0, -2, 4), (2, -2, 4), (1, -2, 5)):
                    p.px(x + dx, y + dy, R[t + k], L)
                p.px(x + 1, y - 1, V[3 + k], L)
            else:
                gilt_leaf(p, x, y - 4, night, L, flip=i % 2 == 1)
                p.px(x + (2 if i % 2 else 0), y - 1, V[3 + k], L)
        x += rnd.randint(*gap)
        i += 1


# --------------------------------------------------------------------------- the elements' pieces
def gilt_panel(p: Pix, bx, base, bw, v, edge):
    """A week's commits as gilded panels stacked to its count, `v` pixels, standing on `base`: gold leaf lit
    along its left edge, a seam every six pixels, outlined in `edge`."""
    for xx in range(bx, bx + bw):
        nx = 2 * (xx - bx + 0.5) / bw - 1
        for yy in range(base - v, base):
            t = 5 if nx < -0.5 else (4 if nx < 0.45 else 3)
            if (base - yy) % 6 == 0 and yy > base - v:
                t = 2
            elif yy == base - v:
                t = min(6, t + 1)
            p.px(xx, yy, G[t])
    p.vline(bx - 1, base - v - 1, base, edge)
    p.vline(bx + bw, base - v - 1, base, edge)
    p.hline(bx - 1, bx + bw + 1, base - v - 1, edge)


def astrolabe_ring(p: Pix, cx, cy, r, night):
    """The limb of an astrolabe as a dial's half ring, its outer edge at radius `r` and four pixels deep: a
    ring of brass lit on its left, the degree scale engraved along its outer band and a fine line dividing
    it from the inner, with a pointer of the rete at each hour."""
    I = RAMP["ink"]
    for yy in range(math.floor(cy - r) - 1, math.ceil(cy) + 1):
        for xx in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not r - 4 <= rho <= r or dy > 0.5:
                continue
            th = math.degrees(math.atan2(-dy, dx))
            lit = -(dx * LX + dy * LY) / r
            t = 5 if lit > 0.35 else (4 if lit > -0.2 else 3)
            if rho > r - 1:
                c = G[max(2, t - 1)]
            elif rho < r - 3:
                c = G[t]
            else:
                c = G[t]
                f = th / 6
                if abs(f - round(f)) < 0.16 and 0 < th < 180:
                    c = I[2]
            if r - 2.6 <= rho < r - 1.6 and (round(th) % 30) > 2:
                c = G[max(1, t - 2)]
            p.px(xx, yy, c)


def vellum_tablet(q: Pix, ox, oy, night):
    """One counter's cell, 11 by 15, top-left at (ox, oy): a tablet of vellum in a frame of gold leaf, the
    frame lit along its top and left and shaded along its right and foot with a bead at each corner, the
    vellum inside it lit at its upper left and falling into shade at its lower right."""
    Ve = RAMP["vellum"]
    for yy in range(15):
        for xx in range(11):
            c = Ve[6] if (xx + yy) % 7 else Ve[5]
            if xx == 0 or yy == 0:
                c = G[5]
            elif xx == 10 or yy == 14:
                c = G[2]
            elif xx == 1 or yy == 1:
                c = C["white"]
            elif xx == 9 or yy == 13:
                c = Ve[4]
            q.px(ox + xx, oy + yy, c)
    for (dx, dy) in ((0, 0), (10, 0), (0, 14), (10, 14)):
        q.px(ox + dx, oy + dy, G[6] if dy == 0 else G[3])


LEAF4 = ["Lgg.", "gGGL", "LGdL", ".LL."]    # a bigger ivy leaf, four across, for the vine the releases hang from


def big_leaf(p: Pix, x, y, night=False, L="base", flip=False):
    """A gilded leaf four pixels square, top-left at (x, y), turned over when `flip`."""
    pal = {"g": G[6 if night else 5], "G": G[5 if night else 4], "d": G[3], "L": G[1]}
    p.sprite(x, y, LEAF4, pal, 1, L, flip=flip, reuse=True)


def stem(p: Pix, x0, x1, y, night):
    """The vine the releases hang from, from x0 to x1 along row `y`: a verdigris stem three deep, lit
    along its top, with a gilded leaf on a stalk every nine pixels, above and below by turns."""
    k = -1 if night else 0
    for x in range(x0, x1):
        p.px(x, y - 1, V[5 + k] if x % 9 == 4 else V[4 + k])
        p.px(x, y, V[3 + k])
        p.px(x, y + 1, V[2 + k])
    i = 0
    for x in range(x0 + 4, x1 - 4, 9):
        if i % 2 == 0 and p.clear_of_words(x - 1, y - 7, x + 4, y - 1):
            p.px(x, y - 2, V[3 + k])
            big_leaf(p, x - 1, y - 6, night, flip=True)
        elif i % 2 == 1 and p.clear_of_words(x - 1, y + 2, x + 4, y + 8):
            p.px(x, y + 2, V[3 + k])
            big_leaf(p, x - 1, y + 3, night)
        i += 1


def margin_vine(p: Pix, x, top, base, night, motion, seed=0):
    """A vine climbing the margin from row `base` up to `top`, its stem winding about column `x`: gilded
    leaves on short stalks to either side, a flower where it has grown a while, and a bird perched on it
    for every twenty-six rows it climbs, two at most."""
    k = -1 if night else 0
    rnd = random.Random(seed)
    col = {}
    for yy in range(top, base + 1):
        xx = x + round(2.2 * math.sin((yy - top) / 5.5 + seed))
        col[yy] = xx
        p.px(xx, yy, V[4 + k] if (yy - top) % 7 == 3 else V[3 + k])
        p.px(xx + 1, yy, V[2 + k])
    perches = min(2, (base - top) // 26)
    roosts = [top + (base - top) * (i + 1) // (perches + 1) for i in range(perches)]
    for i, yy in enumerate(range(base - 6, top + 3, -7)):
        side = -1 if i % 2 else 1
        if any(abs(yy - r) < 6 for r in roosts):
            continue
        sx = col[yy] + (2 if side > 0 else -1)
        p.px(sx, yy, V[3 + k])
        if i % 5 == 4:
            R = O if rnd.random() < 0.5 else B
            for (dx, dy, t) in ((0, -1, 5), (-1, 0, 4), (1, 0, 4), (0, 1, 3), (0, 0, 4)):
                p.px(sx + side + dx, yy + dy, R[t + k])
            p.px(sx + side, yy, G[6])
        else:
            gilt_leaf(p, sx + (1 if side > 0 else -3), yy - 1, night, flip=side < 0)
    for i, yy in enumerate(roosts):
        bird(p, col[yy] - 3, yy - 5, night, motion, red=i % 2 == 1, flip=i % 2 == 0)


ROUNDELS = ("lapis", "oxblood", "verdigris", "tyrian")


def roundel(p: Pix, x, y, kind, night, i=0, unlit=None):
    """A release hanging from the vine at x, the stem on row `y`: a painted roundel with a gold rim, in
    lapis, oxblood, verdigris or Tyrian purple by turns; a bigger one with a gold star for a big release;
    a gilded bud for a patch; for the repository's making a small versal of gold on oxblood; and for a
    release still to come an empty roundel outlined in `unlit`."""
    k = -1 if night else 0
    if kind in ("major", "big"):
        R = RAMP[ROUNDELS[i % len(ROUNDELS)]] if kind == "major" else RAMP["oxblood"]
        p.px(x, y + 2, V[3 + k])
        rad = 3.5 if kind == "major" else 4.5
        cy = y + 3 + rad
        for yy in range(math.floor(cy - rad), math.ceil(cy + rad) + 1):
            for xx in range(math.floor(x + 0.5 - rad), math.ceil(x + 0.5 + rad) + 1):
                dx, dy = xx + 0.5 - (x + 0.5), yy + 0.5 - cy
                rho = math.hypot(dx, dy)
                if rho > rad:
                    continue
                lit = -(dx * LX + dy * LY) / rad
                if rho > rad - 1.1:
                    c = G[5] if lit > 0.2 else G[3]
                else:
                    c = R[4 + k] if lit > 0.3 else (R[3 + k] if lit > -0.3 else R[2 + k])
                p.px(xx, yy, c)
        if kind == "big":
            gilt_star(p, x - 2, round(cy) - 2)
        else:
            p.px(x, round(cy) - 1, G[6])
    elif kind == "minor":
        p.px(x, y + 2, V[3 + k])
        p.px(x, y + 3, G[5])
        p.px(x + 1, y + 3, G[4])
        p.px(x, y + 4, G[3])
    elif kind == "made":
        p.px(x, y + 2, V[3 + k])
        p.rect(x - 2, y + 3, 5, 5, O[2 + k])
        p.box(x - 2, y + 3, 5, 5, G[4])
        p.px(x, y + 5, G[6])
    else:
        p.px(x, y + 2, V[3 + k])
        ring = ["..ggggg..", ".gGGGGGd.", "gG.....Gd", "gG.....Gd", "gG.....Gd", "gG.....Gd", "gG.....Gd", ".dGGGGGd.",
                "..ddddd.."]
        p.sprite(x - 4, y + 3, ring, {"g": G[5], "G": G[4], "d": G[2]})
        p.px(x, y + 7, unlit)


# A sitter for a miniature, 13 by 13: H the hair, s the skin, k the eyes, m the mouth, n the neck, R the
# robe and g its clasp. The hair's rows are redrawn for each style (see `bust`).
SITTER = [
    ".....HHH.....",
    "....HHHHH....",
    "...HHHHHHH...",
    "...HsssssH...",
    "...HsksksH...",
    "....sssss....",
    "....ssmss....",
    ".....sss.....",
    "...RRRnRRR...",
    "..RRRRRRRRR..",
    ".RRRRRgRRRRR.",
    "RRRRRRRRRRRRR",
    "RRRRRRRRRRRRR",
]
# The hair's tones, the skin (one of the hand's three, light to dark) and the robe's pigments a sitter may have,
# chosen by the seed of their name.
HAIR = (("ink", 1), ("wood", 2), ("wood", 4), ("gold", 4), ("ash", 5), ("oxblood", 2), ("ink", 3))
SKIN = ("skin0", "skin1", "skin2")
ROBES = (("lapis", "oxblood"), ("oxblood", "lapis"), ("verdigris", "oxblood"), ("tyrian", "verdigris"),
         ("redlead", "lapis"), ("habit", "lapis"))
# The bot as a little automaton: a head of brass with a winding key on top, glass eyes and a slot of a
# mouth, on shoulders of riveted iron.
AUTOMATON = [
    ".....rbr.....",
    "......b......",
    "...dBBBBbd...",
    "..dBBBBBBbd..",
    "..rBeeBeebr..",
    "..dBgeBgebd..",
    "..dBBBBBBbd..",
    "...dbmmmbd...",
    "....dbbbd....",
    "..IIIInIIIi..",
    ".IIIInnnIIIi.",
    "IIIIrIIIIrIii",
    "IIIIIIIIIIIii",
]
AUTOMATON_PAL = {"b": "gold:4", "B": "gold:5", "d": "gold:3", "r": "gold:6", "e": "ink:0", "g": "lapis:5",
                 "m": "ink:1", "n": "ash:2", "i": "ash:2", "I": "ash:3"}


def seed_of(name) -> int:
    """A number for a name, the same in every run: the sitter's looks are drawn from it."""
    return sum((i + 1) * ord(ch) for i, ch in enumerate(str(name)))


def bust(p: Pix, cx, cy, name, night, L="base"):
    """A sitter painted from the chest up, 13 by 13 centred on (cx, cy): their hair, skin and robe drawn
    from the seed of their name, the skin one of the hand's three, the hair cropped, long, tonsured or under
    a veil, the robe lit from the left with a clasp of gold at the throat. Returns the robe's pigment, so the
    ground can be another."""
    seed = seed_of(name)
    k = -1 if night else 0
    hair_ramp, hair_t = HAIR[seed % len(HAIR)]
    skin = SKIN[(seed // 7) % len(SKIN)]
    robe, ground = ROBES[(seed // 29) % len(ROBES)]
    style = (seed // 3) % 4
    Hr, S, R = RAMP[hair_ramp], RAMP[skin], RAMP[robe]
    rows = [list(r) for r in SITTER]
    if style == 1:                                     # long hair, falling to the shoulders
        for yy in range(3, 8):
            rows[yy][3] = rows[yy][9] = "H"
        for yy in range(5, 9):
            rows[yy][2] = rows[yy][10] = "H"
    elif style == 2:                                   # a tonsure: the crown shaved, a ring of hair round it
        rows[0] = list(".............")
        rows[1] = list("....sssss....")
        rows[2] = list("...HsssssH...")
    elif style == 3:                                   # a veil of cream linen over the hair
        hair_ramp, hair_t, Hr = "vellum", 5, RAMP["vellum"]
        for yy in range(3, 8):
            rows[yy][3] = rows[yy][9] = "H"
            rows[yy][2] = rows[yy][10] = "H"
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            if ch == "H":
                c = Hr[min(6, hair_t + (1 if i < 6 and j < 3 else 0) + k)]
            elif ch in "sn":
                c = S[min(6, 3 + (1 if i < 6 else 0) + k)]
            elif ch == "k":
                c = RAMP["ink"][0]
            elif ch == "m":
                c = RAMP["oxblood"][3 if skin == "skin2" else 4]
            elif ch == "g":
                c = G[6]
            else:
                c = R[(4 if i < 5 else 3 if i < 10 else 2) + k]
            p.px(cx - 6 + i, cy - 6 + j, c, L)
    return ground


def automaton(p: Pix, cx, cy, night, L="base"):
    """The bot's portrait, 13 by 13 centred on (cx, cy): a little automaton of brass and iron."""
    p.sprite(cx - 6, cy - 6, AUTOMATON, _pal(AUTOMATON_PAL, night), 1, L)


def portrait(p: Pix, cx, cy, i, person, night):
    """A contributor as a miniature portrait centred on (cx, cy): a frame of gold leaf two deep, lit from
    the upper left, with a bead at each corner and a tendril curling from it, round a diapered ground of
    lapis, oxblood or verdigris on which the sitter is painted from the chest up; a bot's portrait is of a
    little automaton on a ground of verdigris."""
    k = -1 if night else 0
    bot = not person.get("initials")
    Lp = p.layer("far")
    if bot:
        ground = "verdigris"
    else:
        ground = bust(p, cx, cy, person.get("name", ""), night)
    R = RAMP[ground]
    p.rect(cx - 6, cy - 6, 13, 13, R[2 + k], Lp)
    for yy in range(cy - 4, cy + 5, 4):
        for xx in range(cx - 4 + ((yy - cy) // 4 % 2) * 2, cx + 5, 4):
            p.px(xx, yy, R[3 + k], Lp)
    if bot:
        automaton(p, cx, cy, night)
    p.box(cx - 8, cy - 8, 17, 17, G[3])
    p.box(cx - 7, cy - 7, 15, 15, G[4])
    p.hline(cx - 8, cx + 8, cy - 8, G[4])
    p.vline(cx - 8, cy - 8, cy + 8, G[4])
    p.hline(cx - 7, cx + 7, cy - 7, G[5])
    p.vline(cx - 7, cy - 7, cy + 7, G[5])
    p.hline(cx - 6, cx + 8, cy + 7, G[3])
    p.vline(cx + 7, cy - 6, cy + 8, G[3])
    p.hline(cx - 7, cx + 9, cy + 8, G[2])
    p.vline(cx + 8, cy - 7, cy + 9, G[2])
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):   # the corners: a bead, and a tendril curling out
        bx, by = cx + 8 * sx, cy + 8 * sy
        p.px(bx, by, G[6])
        p.px(bx + sx, by, G[4])
        p.px(bx, by + sy, G[4])
        p.px(bx + sx, by + sy, G[5])


def wax_seal(p: Pix, cx, cy, r0, r1, night):
    """A pendant seal of red wax round the certificate's disc, from radius r0 out to r1: the wax pressed
    into an uneven edge, lit from the upper left, darker where it turns from the light."""
    k = -1 if night else 0
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 1):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
            dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
            rho = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            edge = r1 - 1.2 - 1.3 * abs(math.sin(5 * th + 0.4)) - 0.5 * abs(math.sin(11 * th))
            if rho < r0 - 0.6 or rho > edge:
                continue
            lit = -(dx * LX + dy * LY) / r1
            t = 4 if lit > 0.3 else (3 if lit > -0.25 else 2)
            if rho > edge - 1.1:
                t -= 1
            p.px(xx, yy, O[max(0, t + k)])


def ribbon_tails(p: Pix, x, y, night):
    """The ribbon a pendant seal hangs by, its two tails below the seal, top-left at (x, y): one of lapis
    and one of oxblood, each cut in a swallowtail and fringed with gold."""
    k = -1 if night else 0
    for i, R in enumerate((RAMP["lapis"], RAMP["oxblood"])):
        ox = x + 1 + i * 8
        for yy in range(y, y + 6):
            w = 5 if yy < y + 4 else (4 if yy == y + 4 else 2)
            for dx in range(w if yy < y + 5 else 5):
                if yy == y + 5 and dx == 2:
                    continue
                p.px(ox + dx, yy, R[(4 if dx == 0 else 3 if dx < 4 else 2) + k])
        p.px(ox, y + 6, G[4])
        p.px(ox + 4, y + 6, G[4])


def words_ribbon(p: Pix, x, y, w, h, night):
    """The ribbon under a certificate's seal that its lower words are lettered on, `w` by `h` from (x, y):
    silk of two colours, lapis above and oxblood below with a thread of gold between, lit along its top
    and shaded along its foot, and at either end a cap of gold cut in a swallowtail."""
    k = -1 if night else 0
    half = h // 2
    p.rect(x, y, w, half, B[3 + k])
    p.rect(x, y + half, w, h - half, O[3 + k])
    p.hline(x, x + w, y, B[4 + k])
    p.hline(x, x + w, y + h - 1, O[2 + k])
    p.hline(x, x + w, y + half, G[4])
    for side, ex in ((-1, x - 1), (1, x + w)):
        for yy in range(y, y + h):
            p.px(ex, yy, G[5] if yy < y + half else G[3])
        for yy in range(y, y + h):
            if abs(yy - (y + h / 2 - 0.5)) > h / 4:
                p.px(ex + side, yy, G[4] if yy < y + half else G[2])
        p.px(ex, y + half, G[6])


def gold_roundel(p: Pix, cx, cy, L="base"):
    """A roundel of gold leaf nine pixels across, centred on the pixel (cx, cy), lit from the upper left,
    the icon of a link button sits on."""
    sphere(p, cx + 0.5, cy + 0.5, 4.6, G, L=L, lo=1)


def panel_frame(p: Pix, x, y, w, h, night):
    """A schematic card as a painted panel: a frame of gold leaf round its edge, lit along the top and
    the left and shaded along the foot and the right, with a bead of light at each corner, and a hairline
    of oxblood just inside it."""
    k = -1 if night else 0
    p.box(x, y, w, h, G[4])
    p.hline(x, x + w, y, G[5])
    p.vline(x, y, y + h, G[5])
    p.hline(x + 1, x + w, y + h - 1, G[3])
    p.vline(x + w - 1, y + 1, y + h, G[3])
    for (cx, cy) in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        p.px(cx, cy, G[6])
    p.box(x + 1, y + 1, w - 2, h - 2, O[3 + k])


def icon_cell(p: Pix, x, y, w, h, night, body):
    """The icon's cell at the left of a schematic card, a square of lapis by day and oxblood by night
    between the card's hairline and the gilded band, the icon itself turned to gold leaf."""
    R = B if not night else O
    k = -1 if night else 0
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + 10):
            c = p.get(xx, yy)
            if c == body:
                p.px(xx, yy, G[6])
            else:
                p.px(xx, yy, R[2 + k] if (xx + yy) % 4 else R[3 + k])


def wire_bosses(p: Pix, cells, night):
    """A boss of gold at every join of a wire, where it turns a corner, and where it leaves its card."""
    joins = [cells[0][:2]]
    for a, b in zip(cells, cells[1:]):
        if a[:2] == b[:2] and a[2] != b[2]:
            joins.append(a[:2])
    on = {c[:2] for c in cells}
    for (x, y) in joins:
        p.px(x, y, G[6])
        for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) in on:
                p.px(x + dx, y + dy, G[4])
