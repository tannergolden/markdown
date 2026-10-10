# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tapestry set's cloth and stitches, drawn on the shared pixel canvas.

The woven linen every sheet is stitched on, the rod it hangs from with its finials, the hems down its sides and the
fringe along its foot; the border band of beasts and knotwork across a header's top with the comet that crosses behind
it, and the lower border its scenes stand on and a footer is sewn along; the torches that light the hall by night;
letters laid in wool; the knights of the charge on horses set pixel by pixel, the shield wall, the great horseman with
his great banner, Harold grown twice with his hawk and his great hound, and the trees, the tall one growing to the
rows a scene gives it; Halley's comet, a footer's mark; and the needles, gonfanons, roundels and figures every element
and badge carries. Everything is embroidery: flat wool in the tapestry's colours, couched down with a darker thread,
and shaded only where a thread catches the light; the torches burn on the collection's flame and the faces and hands
are stitched in its three skins (see `collections.hand`). What repeats along an edge (a hem's stitches, the rod's
turnings, a rule, the fringe, the braid) is a pattern tile, and a figure or a title's letter that stands more than
once in a drawing is kept once, so a sheet stays light. A drawing made lighter to fit its budget keeps every figure,
light and motion, and thins only fine texture: the linen's slubs, the vine's variety, the rod's turnings, the laid
work of the horses and the rings of the mail, and the loose ends of a title's couching thread."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, Paint, Pix, fold, num
from .palette import C, NIGHT_SKY, RAMP, WOOLS

L_, T_, M_, O_, W_, U_, G_, F_, I_, S_ = (RAMP[n] for n in ("linen", "terracotta", "mustard", "olive", "woad",
                                                            "umber", "gold", "flame", "iron", "steel"))
SKINS = tuple(RAMP[f"skin{i}"] for i in range(3))      # the hand's skins, light to dark
ROD = 3          # the rows the hanging rod takes at the top of a sheet; the cloth hangs from the row under it
BAND = (5, 13)   # the rows of the border band's twin rules across a header
FRINGE = 3       # the rows the fringe hangs below the cloth


def skin(i: int, night: bool) -> str:
    """The wool a face and its hands are stitched in, on the hand's skin `i` (0 the lightest, 2 the darkest): the
    skin's own tone, a tone deeper by torchlight as every wool is."""
    return SKINS[i % len(SKINS)][3 - (1 if night else 0)]


# --------------------------------------------------------------------------- the linen
def _twill(uid: str, weft: str, warp: str) -> str:
    """A pattern tile of the twill weave, four pixels square: a diagonal of the weft's shadow and, two
    pixels over, a diagonal where the warp catches the light."""
    return (f'<pattern id="{uid}t" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<path stroke="{weft}" d="M0 .5h1m0 1h1m0 1h1m0 1h1"/>'
            f'<path stroke="{warp}" d="M2 .5h1m0 1h1m-3 1h1m0 1h1"/></pattern>')


def _slubs(uid: str, slub: str) -> str:
    """A pattern tile of the odd slub, 64 by 48: a few short thick threads in the weft where the spinner
    let the yarn run coarse."""
    return (f'<pattern id="{uid}s" width="64" height="48" patternUnits="userSpaceOnUse">'
            f'<path stroke="{slub}" d="M5 7.5h3M41 19.5h4M22 33.5h3M53 41.5h3"/></pattern>')


def lay_cloth(p: Pix, foot: int = FRINGE):
    """The linen laid from under the rod to `foot` rows above the sheet's edge, where the fringe hangs:
    cream by day with its twill and its slubs; by night fallen to umber, warm under the torches at the top
    and darker toward the foot. Laid again with another `foot` it replaces what it laid before. A drawing made
    lighter keeps the twill and goes without the slubs."""
    x, y, w, h, uid, night = p.cloth
    y1 = h - foot
    parts = []
    if not night:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{y1 - y}" fill="{C["paper"]}"/>')
    else:
        n = len(NIGHT_SKY)
        edges = [y + round(i * (y1 - y) / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                parts.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" '
                             f'fill="{col}"/>')
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{y1 - y}" fill="url(#{uid}t)"/>')
    if not p.lite:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{y1 - y}" fill="url(#{uid}s)"/>')
    slot = getattr(p, "cloth_slot", None)
    if slot is None:
        p.cloth_slot = (len(p.under), len(parts))
        p.under.extend(parts)
    else:
        i, n = slot
        p.under[i:i + n] = parts
        p.cloth_slot = (i, len(parts))


def paper(p: Pix, night: bool, x=0, y=None, w=None, h=None, uid="p"):
    """The ground a drawing sits on: woven linen hanging from the rod along the sheet's top, unbleached
    cream by day and by night the same cloth in a torch-lit hall. The drawing keeps which sheet it is
    (`uid`: "p" for a header or a footer) and whether it is night, for the hooks the layouts call
    without saying."""
    y = ROD if y is None else y
    w = p.w if w is None else w
    h = p.h if h is None else h
    p.sheet, p.night = uid, night
    p.cloth = (x, y, w, h, uid, night)
    p.defs.append(_twill(uid, C["weft_n" if night else "weft"], C["warp_n" if night else "warp"]))
    if not p.lite:
        p.defs.append(_slubs(uid, C["slub_n" if night else "slub"]))
    lay_cloth(p, foot=FRINGE)


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the linen, or by night the band of the torchlit linen the row lies in."""
    if not night:
        return C["paper"]
    return NIGHT_SKY[min(len(NIGHT_SKY) - 1, max(0, (y - ROD) * len(NIGHT_SKY) // max(1, p.h - ROD - FRINGE)))]


# --------------------------------------------------------------------------- stitches
def tile(p: Pix, pid: str, w: int, h: int, cells: dict) -> str:
    """A pattern tile `w` by `h` of `cells` ({(x, y): colour}), kept once a file by its id."""
    key = ("pattern", pid)
    if key not in p.syms:
        by: dict = {}
        for (x, y), c in cells.items():
            by.setdefault(c, {}).setdefault(y, []).append(x)
        paths = "".join(f'<path stroke="{c}" d="{Pix._d(rows)}"/>' for c, rows in by.items())
        p.defs.append(f'<pattern id="{pid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{paths}</pattern>')
        p.syms[key] = pid
    return pid


def filled(p: Pix, pid: str, x, y, w, h, L="base"):
    """A box filled with a pattern tile, drawn under the pixels of its layer."""
    if w <= 0 or h <= 0:
        return
    if L not in p.layers:
        p.layer(L)
    p.shapes[L].append(f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="url(#{pid})"/>')


def couched(p: Pix, x0, x1, y, wool: str, thread: str, L="base", phase: int = 0):
    """A laid thread along row `y` from x0 to x1, couched down with a stitch of a darker thread every
    fourth pixel: a pattern tile, so a long rule costs a line."""
    pid = tile(p, f"cd{wool[1:]}{thread[1:]}{phase}", 4, 1,
               {(xx, 0): thread if (xx + phase) % 4 == 1 else wool for xx in range(4)})
    filled(p, pid, x0, y, x1 - x0, 1, L)


def running(p: Pix, x0, x1, y, thread: str, L="base", phase: int = 0, on: int = 2, off: int = 2):
    """A running stitch along row `y`: a dash of thread `on` pixels long, a gap `off` long."""
    for xx in range(x0, x1):
        if (xx + phase) % (on + off) < on:
            p.px(xx, y, thread, L)


def braid(p: Pix, x0, x1, y, night: bool, L="base"):
    """Two rows of knotwork between a border's twin rules: a chevron braid of mustard and olive wool,
    each strand lit a tone where it crosses over the other; a pattern tile twelve wide."""
    k = -1 if night else 0
    cells = {}
    for xx in range(12):
        t = xx % 6
        up = t < 3
        a, b = (M_[4 + k], O_[3 + k]) if (xx // 6) % 2 == 0 else (O_[3 + k], M_[4 + k])
        cells[(xx, 0)] = a if up else b
        cells[(xx, 1)] = b if up else a
        if t in (0, 3):
            cells[(xx, 0 if up else 1)] = M_[5 + k] if (a == M_[4 + k]) == up else O_[4 + k]
    pid = tile(p, f"br{'n' if night else 'd'}", 12, 2, cells)
    filled(p, pid, x0, y, x1 - x0, 2, L)


def outline(p: Pix, cells: dict, colour: str, L="base", skip=()):
    """A couched outline round a stitched figure: every pixel beside one of `cells` that is none of them
    takes the outline's thread, except the `skip` pixels."""
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and q not in skip:
                p.px(q[0], q[1], colour, L)


def stitch(p: Pix, x, y, art, pal, L="base", flip=False, edge=None, s=1):
    """A figure stitched from rows of characters looked up in `pal`, with a couched outline in `edge`
    round it when one is given. Returns its pixels."""
    rows = [r[::-1] if flip else r for r in art]
    cells = {}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                for dy in range(s):
                    for dx in range(s):
                        cells[(x + i * s + dx, y + j * s + dy)] = c
    if edge:
        outline(p, cells, edge, L)
    for (xx, yy), c in cells.items():
        p.px(xx, yy, c, L)
    return cells


# --------------------------------------------------------------------------- the frame
def rod(p: Pix, night: bool, x=0, w=None, L="base"):
    """The hanging rod along the top of a sheet: a turned oak pole lit along its top, ringed with a darker turning
    every eleventh pixel, with a knob of a finial at each end standing a little proud of the cloth. The turned pole
    is a pattern tile eleven pixels long, so its turnings cost nothing, and the drawing keeps where it lies for the
    torches' light (see `torchlight`); a drawing made lighter lays the pole plain, without its turnings."""
    w = p.w if w is None else w
    k = -1 if night else 0
    tones = [U_[5 + k], U_[4 + k], U_[2 + k]]
    if p.lite:
        for yy, c in enumerate(tones):
            p.hline(x + 3, x + w - 3, yy, c, L)
    else:
        cells = {(xx, yy): c for yy, c in enumerate(tones) for xx in range(11)}
        cells[(8, 1)] = U_[3 + k]
        filled(p, tile(p, f"pole{'n' if night else 'd'}", 11, 3, cells), x + 3, 0, w - 6, 3, L)
        p.pole = {(xx, yy) for yy in range(3) for xx in range(x + 3, x + w - 3)}
    knob = [".KKKK.", "KLkkKD", "KkkkKD", "KKKKDD", ".DDDD."]
    pal = {"K": U_[3 + k], "L": U_[6 + k], "k": U_[5 + k], "D": U_[1 + k]}
    stitch(p, x, 0, knob, pal, L)
    stitch(p, x + w - 6, 0, knob, pal, L, flip=True)


def hem_tones(night: bool) -> tuple:
    """The hem's cloth: its folded edge, its face, its lit face, and the thread of its running stitch."""
    if night:
        return U_[1], U_[2], U_[3], U_[5]
    return L_[2], L_[4], L_[5], U_[2]


def hems(p: Pix, night: bool, foot: int, L="base"):
    """The cloth's hems: the top turned over the rod with its stitches showing, a hem down each side
    with a running stitch, and along the foot the hem the fringe hangs from. Each is a pattern tile.
    `foot` is how many rows the fringe takes."""
    edge, face, lit, thread = hem_tones(night)
    w, h = p.w, p.h
    tag = "n" if night else "d"
    y1 = h - foot
    top = tile(p, f"hmt{tag}", 5, 1, {(xx, 0): thread if xx < 3 else lit for xx in range(5)})
    filled(p, top, 0, ROD, w, 1, L)
    side = tile(p, f"hml{tag}", 4, 5, {**{(0, yy): edge for yy in range(5)}, **{(1, yy): lit for yy in range(5)},
                                       **{(2, yy): thread if yy < 3 else face for yy in range(5)},
                                       **{(3, yy): face for yy in range(5)}})
    filled(p, side, 0, ROD + 1, 4, y1 - ROD - 1, L)
    right = tile(p, f"hmr{tag}", 4, 5, {**{(3, yy): edge for yy in range(5)}, **{(2, yy): face for yy in range(5)},
                                        **{(1, yy): thread if yy > 1 else face for yy in range(5)},
                                        **{(0, yy): lit for yy in range(5)}})
    filled(p, right, w - 4, ROD + 1, 4, y1 - ROD - 1, L)
    foot_row = tile(p, f"hmf{tag}", 5, 1, {(xx, 0): thread if xx < 3 else face for xx in range(5)})
    filled(p, foot_row, 0, y1 - 1, w, 1, L)


def fringe(p: Pix, night: bool, foot: int, L="base"):
    """The fringe of tassels along the foot, hanging below the hem over whatever ground the sheet is shown
    on: a tassel every fourth pixel in the wools by turns, two threads wide, gathered bright at its head
    and darkening to its end; a pattern tile sixteen wide."""
    k = -1 if night else 0
    cells = {}
    for i, wool in enumerate(WOOLS):
        R = RAMP[wool]
        for yy in range(foot):
            t = (5 if yy == 0 else 4 if yy < foot - 1 else 3) + k
            cells[(i * 4 + 1, yy)] = R[t]
            cells[(i * 4 + 2, yy)] = R[t - 1]
    pid = tile(p, f"fr{'n' if night else 'd'}{foot}", 16, foot, cells)
    filled(p, pid, 0, p.h - foot, p.w, foot, L)


def top_band(p: Pix, night: bool, L="base"):
    """The border's knotwork alone across a sheet that has no room for its beasts: twin couched rules
    with a braid between them, in the four rows under the top hem."""
    k = -1 if night else 0
    thread = U_[1] if not night else U_[0]
    couched(p, 4, p.w - 4, ROD + 1, T_[3 + k], thread, L)
    braid(p, 4, p.w - 4, ROD + 2, night, L)
    couched(p, 4, p.w - 4, ROD + 4, T_[3 + k], thread, L, phase=2)


def border_rules(p: Pix, x0, x1, night: bool, L="base"):
    """The twin rules of the border band across a header, couched terracotta wool."""
    k = -1 if night else 0
    thread = U_[1] if not night else U_[0]
    couched(p, x0, x1, BAND[0], T_[3 + k], thread, L)
    couched(p, x0, x1, BAND[1], T_[3 + k], thread, L, phase=2)


def frame(p: Pix, night: bool, header: bool = False, footer: bool = False):
    """The sheet's frame: the rod it hangs from, its hems, and the fringe along its foot. A header gets its
    border band from the garland; an element's sheet has the knotwork alone under the top hem; a footer, whose
    words stand right under its hem, has none there and stands on the lower border instead (see
    `foot_floor`). By night torches burn in their brackets at a header's top corners and their light pools on
    the linen; an element's sheet has its torches set in its last pass (see `sheet_torches`), and a footer one
    of its own at the corner of its notes."""
    hems(p, night, FRINGE)
    fringe(p, night, FRINGE)
    rod(p, night)
    if not header and not footer:
        top_band(p, night)
    if night and header:
        torches(p)


FOOT_BEASTS = 40   # the fewest columns a stretch of a footer's floor raises the border's beasts over
FOOT_RULE = 8      # the fewest it couches its rule over the braid along: a shorter stretch has the braid alone
FOOT_LEAST = 40    # and the fewest it lays its braid along: a shorter scrap of it is left off, the hem bare


def foot_spans(p: Pix, low=()) -> list:
    """How the lower border stands along a footer's hem, two units clear of every word: [(from, to, level)], ends
    excluded, at its full height with the border's beasts (3), the braid with a couched rule over it (2), the braid
    alone (1), or not at all, the hem bare (0). In the columns of `low`, [(from, to)], the band rises no higher than
    braid and rule. A stretch of the full band under `FOOT_BEASTS` columns is counted as braid and rule, one of
    braid and rule under `FOOT_RULE` columns as the braid alone, and any stretch under `FOOT_LEAST` columns as bare
    hem."""
    h = p.h

    def level(x):
        for lv, top in ((3, h - 16), (2, h - 9), (1, h - 8)):
            if p.clear_of_words(x - 2, top, x + 3, h - 4):
                return lv
        return 0

    def runs(levels, same) -> list:
        out: list = []
        for x, lv in enumerate(levels, 4):
            if out and same(out[-1][2], lv):
                out[-1][1] = x + 1
            else:
                out.append([x, x + 1, lv])
        return out
    levels = [min(level(x), 2 if any(a <= x < b for a, b in low) else 3) for x in range(4, p.w - 4)]
    for a, b, lv in runs(levels, lambda u, v: u == v):
        if lv == 3 and b - a < FOOT_BEASTS:
            levels[a - 4:b - 4] = [2] * (b - a)
    for a, b, lv in runs(levels, lambda u, v: u == v):
        if lv == 2 and b - a < FOOT_RULE:
            levels[a - 4:b - 4] = [1] * (b - a)
    for a, b, lv in runs(levels, lambda u, v: bool(u) == bool(v)):
        if lv and b - a < FOOT_LEAST:
            levels[a - 4:b - 4] = [0] * (b - a)
    return [tuple(s) for s in runs(levels, lambda u, v: u == v)]


FOOT_TOP = {3: 14, 2: 7, 1: 6, 0: 4}   # how far over a footer's foot its floor rises at each level (see `foot_spans`)


def foot_floor(p: Pix, night: bool, rule: str, low=()) -> list:
    """A footer's floor once its words are set: the lower border of the hanging sewn on its hem, as the headers' scenes
    stand on it over their rules (see `lower_band`). Wherever the words leave it the rows, the braid runs along the
    hem; where they leave one more, a couched rule over it; and along every stretch they leave free to the band's full
    height, the band rises whole, its upper rule high over the braid with the border's beasts and knots walking
    between, closed at each end by an upright of couched thread; but in the columns of `low` no higher than braid and
    rule. The dividers of the cells, ruled in `rule`, stop where the floor lies over them. Returns its spans (see
    `foot_spans`)."""
    k = -1 if night else 0
    thread = U_[1] if not night else U_[0]
    h = p.h
    spans = foot_spans(p, low)
    base = p.layers["base"]
    for a, b, lv in spans:
        if not lv:
            continue
        top = h - FOOT_TOP[lv]
        for xy in [xy for xy, c in base.items() if c == rule and a <= xy[0] < b and xy[1] >= top]:
            del base[xy]
        braid(p, a, b, h - 6, night)
        if lv >= 2:
            couched(p, a, b, top, T_[3 + k], thread, phase=a % 4)
        if lv == 3:
            for x in (a, b - 1):
                for y in range(h - 13, h - 6):
                    p.px(x, y, thread if y % 3 == 0 else T_[3 + k])
            beasts_along(p, a + 2, b - 2, h - 13, night, seed=a)
    return spans


# --------------------------------------------------------------------------- the comet, a footer's mark
# Halley's comet as the embroidery shows it over the men who marvel at it, a footer's mark: a star of gold thread
# couched round, its upper left lit and its heart bright, with short rays stitched about its front, and behind it a
# tail of streamers of wool, terracotta, mustard, olive and terracotta again, each laid widest at the star and tapering
# as it waves out behind, lit along its upper edge and shaded along its lower. Each stream is (its slope, its length
# as a share of the tail's, its width at the star).
STREAMS = ((-0.22, 0.8, 3), (-0.06, 1.0, 3), (0.1, 0.92, 3), (0.26, 0.72, 2))
SMALL_STREAMS = ((-0.2, 0.85, 2), (0.0, 1.0, 3), (0.2, 0.8, 2))
STEEP_STREAMS = ((-0.03, 0.8, 3), (0.0, 1.0, 4), (0.03, 0.85, 3))   # close and broad, one fiery tail
COMET_WOOLS = ("terracotta", "mustard", "olive", "terracotta")
# The comet at its sizes, the greatest first: the length of its tail, the radius of its star, its streams, the angles
# of its rays from straight ahead, and the way its tail streams behind it, in degrees round from the right with the
# rows running down: 180 straight back to the left, -60 up and to the right behind a comet falling to the left.
COMETS = (
    (44, 4.3, STREAMS, (-70, -35, 0, 35, 70), 180, COMET_WOOLS),                          # 55 columns by 15 rows
    (30, 4.3, STREAMS, (-70, -35, 0, 35, 70), 180, COMET_WOOLS),                          # 41 by 15
    (22, 4.3, STREAMS, (-70, -35, 0, 35, 70), 180, COMET_WOOLS),                          # 33 by 15
    (21, 3.3, STEEP_STREAMS, (-60, 0, 60), -60, ("terracotta", "mustard", "terracotta")),  # falling, 17 by 25
    (13, 3.3, SMALL_STREAMS, (-60, 0, 60), 180, COMET_WOOLS),                             # 21 by 9
)


def great_comet_cells(size: int = 0) -> dict:
    """The comet's flat picture (see `STREAMS`) at its `size`, 0 the greatest (see `COMETS`), its star ahead and its
    tail streaming back behind it, with its top left at (0, 0). Its roles: the star's body, lit and heart, its
    couching and its rays, and each stream's wool, lit thread and shade by number, each stream lit along its edge
    toward the upper left."""
    key = ("comet", size)
    if key not in FIGURES:
        length, r, streams, rays, tail, _ = COMETS[size]
        small = r < 4
        level = tail == 180
        bx, by = math.cos(math.radians(tail)), math.sin(math.radians(tail))   # back along the tail
        cx, cy = (by, -bx) if by - bx > 0 else (-by, bx)                       # across it, toward its shaded edge
        cells: dict = {}
        n = len(streams)
        fan = min(1, 22 / length)                  # a longer tail fans no wider than the middle comet's
        for i, (slope, share, width) in enumerate(streams):
            root = (i - (n - 1) / 2) * 1.8
            span = int(length * share)
            for t in (k / (1 if level else 2) for k in range(span * (1 if level else 2))):
                across = root + slope * fan * t + 0.8 * fan ** 0.5 * math.sin(t / 3.0 + i * 2.1) * min(1, t / 6)
                thick = max(1, round(width * (1 - t / span) + 0.45))
                ox = bx * (r - 1 + t) + cx * (across - thick / 2 + 0.01)
                oy = by * (r - 1 + t) + cy * (across - thick / 2 + 0.01)
                for w in range(thick):
                    role = "lit" if w == 0 and thick > 1 else "shade" if w == thick - 1 and thick > 2 else "wool"
                    at = (math.floor(ox), round(oy) + w) if level else (round(ox + cx * w), round(oy + cy * w))
                    cells.setdefault(at, (role, i))
        star = {}
        for y in range(-int(r) - 1, int(r) + 2):
            for x in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, y)
                if d <= r:
                    star[(x, y)] = ("heart" if d < r * 0.4 else "bright" if x + y < -1.6 else "star", 0)
        for (x, y) in list(star):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in star:
                    cells[(x + dx, y + dy)] = ("ink", 0)
        cells.update(star)
        ahead = math.radians(tail + 180)
        for ang in rays:
            ray = ahead + math.radians(ang)
            for s in range(int(r) + 2, int(r) + 3 + (0 if small else 1)):
                cells[(round(s * math.cos(ray)), round(s * math.sin(ray)))] = ("ray", 0)
        x0, y0 = min(x for x, _ in cells), min(y for _, y in cells)
        FIGURES[key] = {(x - x0, y - y0): role for (x, y), role in cells.items()}
    return FIGURES[key]


def great_comet(p: Pix, x, y, night: bool, size: int = 0, L="base"):
    """The comet (see `great_comet_cells`) at its `size` with its top left at (x, y), kept once a file: its star in
    gold that catches the light, its streams in the wools a tone deep by day and by torchlight alike."""
    key = ("greatcomet", size, night)
    if key not in p.syms:
        star = {"star": G_[4], "bright": G_[6] if night else G_[5], "heart": G_[6], "ink": U_[1],
                "ray": G_[5] if night else G_[3]}
        tones = {"lit": 4, "wool": 3, "shade": 2}
        wools = COMETS[size][-1]
        p.symbol(key, {xy: star[role] if role in star else RAMP[wools[i]][tones[role]]
                       for xy, (role, i) in great_comet_cells(size).items()})
    p.use(key, x, y, L)


def comet_spot(p: Pix, x0, x1, y0, y1, sizes=range(len(COMETS))):
    """Where the comet lies in the box from (x0, y0) to (x1, y1), ends excluded, two units clear of every word and of
    every pixel set on the base layer (the box itself keeps it off the floor, whose braid, rules and beasts are laid as
    patterns and figures): at the greatest of its `sizes` that has the room, as far right as it goes, and then as
    near the box's middle row as it can. Returns (x, y, size), or None where none of them has the room."""
    base = p.layers["base"]
    for size in sizes:
        cells = great_comet_cells(size)
        w, h = max(x for x, _ in cells) + 1, max(y for _, y in cells) + 1
        ring = {(cx + dx, cy + dy) for (cx, cy) in cells for dx in range(-2, 3) for dy in range(-2, 3)}
        mid = (y0 + y1 - h) // 2
        for x in range(x1 - w, x0 - 1, -1):
            for y in sorted(range(y0, y1 - h + 1), key=lambda v: (abs(v - mid), v)):
                if clear_of(p, placed(cells, x, y), x0, y0) and not any((x + a, y + b) in base for (a, b) in ring):
                    return x, y, size
    return None


# --------------------------------------------------------------------------- torches and their light
# The hall's torch in its iron bracket on the left hem, 10 wide and 18 tall: the flame (f its rim, F its body, Y
# its heart, W its white core, a second tongue licking up beside the first), the head wrapped in pitch and bound
# (h, b), and the bracket of iron: a plate on the hem (P), an arm to the collar round the ash shaft (w) with a
# scroll under it, and the cup its foot stands in (i, I where the iron catches the light). The right hem's is its
# mirror.
TORCH = [
    "....f.....", "...fFf....", "..fFYf.f..", "..fFYFfF..", ".fFYWYFf..", ".fFYWWYFf.", ".fFYWWYFf.",
    "..fFYYFf..", "...fFFf...", "...hhhh...", "...hbbh...", "PPiIIIIi..", "PP..ww....", "Pi..ww....",
    "P.i.ww....", "P..iww....", "PP.iIIi...", "P...ii....",
]
FLAME_ROWS = 9     # the flame is the first nine rows, which flicker
# A small torch, 7 by 14, for the corner of a footer's notes.
SMALL_TORCH = ["...f...", "..fFf..", ".fFWFf.", ".fFWFf.", "..fFf..", "..hhh..", "..hhh..", "...s...", "...s...",
               "aaaisii", "...s...", "...s...", ".R.s.R.", ".IIIII."]
# The smoke rising from a flame: three wisps that come and go in turn, drifting up off the flame's tip.
SMOKE = (((1, -2), (0, -3), (1, -4)), ((0, -3), (0, -5), (-1, -6)), ((1, -5), (2, -6), (1, -7)))
TORCH_IN = 4   # how far in from a sheet's side its corner torch stands


def torch(p: Pix, x, y, night: bool, phase: int = 0, side: int = 1, pool=(96, 66), L="near"):
    """A torch of the hall in its iron bracket by night, 10 by 18 from (x, y), its bracket on the hem at `side`
    (1 the left hem, -1 the right): the flame flickering in its glow with the smoke drifting off its tip in turn,
    and its light pooled wide on the linen below, a warm pool that falls away into the umber."""
    if not night:
        return
    flip = side < 0
    iron = {"h": U_[0], "b": U_[3], "w": U_[4], "i": I_[4], "I": I_[6], "P": I_[3]}
    stitch(p, x, y + FLAME_ROWS, TORCH[FLAME_ROWS:], iron, L, flip=flip)
    Lf = p.flicker(phase)
    cells = stitch(p, x, y, TORCH[:FLAME_ROWS], {"f": F_[3], "F": F_[4], "Y": F_[5], "W": F_[6]}, Lf, flip=flip)
    tip = x + (4 if not flip else 5)
    for n, wisp in enumerate(SMOKE):
        for (dx, dy) in wisp:
            p.px(tip + (dx if not flip else -dx), y + dy, L_[1] if n % 2 else L_[2], p.twinkle(n + phase))
    cx = x + 5
    p.halo(cx, y + 5, 9, 9, F_[3], (0.08, 0.15, 0.24), L=p.flicker(phase, back=True))
    p.halo(cx, y + 11, pool[0], pool[1], F_[4], (0.05, 0.09, 0.14, 0.2))
    p.lamps.append((cx, y + 4, 30, phase, set(cells)))


def small_torch(p: Pix, x, y, phase: int = 0, L="near"):
    """The small torch at the corner of a footer's notes, 7 by 14 from (x, y), its flame flickering in its glow
    and its light pooled round it on the linen."""
    pal = {"s": U_[4], "h": U_[1], "a": I_[4], "i": I_[5], "I": I_[3], "R": I_[6]}
    stitch(p, x, y + 5, SMALL_TORCH[5:], pal, L)
    cells = stitch(p, x, y, SMALL_TORCH[:5], {"f": F_[3], "F": F_[5], "W": F_[6]}, p.flicker(phase))
    p.halo(x + 3.5, y + 2.5, 7, 6.5, F_[3], (0.08, 0.16, 0.26), L=p.flicker(phase, back=True))
    p.halo(x + 3.5, y + 4, 30, 19, F_[4], (0.05, 0.09, 0.15))
    p.lamps.append((x + 3.5, y + 3, 22, phase, set(cells)))


def torches(p: Pix):
    """The hall's torches at the top corners of a header, in brackets on either hem, and their pools of light on
    the linen, wide on a wide sheet and narrower on a phone's. A header's words keep clear of its corners down to
    row 27 on a wide sheet (the torches stand low enough there for their smoke to rise over the linen) and row 23
    on a phone, so the torches stand before any word is set."""
    wide = p.w > 300
    pool = (96, 66) if wide else (60, 46)
    y = 8 if wide else 4
    torch(p, TORCH_IN, y, True, phase=0, side=1, pool=pool)
    torch(p, p.w - TORCH_IN - 10, y, True, phase=2, side=-1, pool=pool)


def sheet_torches(p: Pix):
    """The hall's torches by night on an element's sheet, set in the last pass once its words and its drawing are
    down: on each hem the highest place below the sheet's rule where a torch and its bracket lie two units clear of
    every word and of everything drawn, with its pool of light; on a hem with no such place, none."""
    pool = (80, 56) if p.w > 300 else (56, 42)
    base = p.layers["base"]
    for side, x, phase in ((1, TORCH_IN - 3, 0), (-1, p.w - TORCH_IN - 7, 2)):
        for y in range(22, p.h - 26, 3):
            box = (x - 3, y - 10, x + 13, y + 21)
            if not p.clear_of_words(*box):
                continue
            if any(box[0] <= bx < box[2] and box[1] <= by < box[3] and 4 <= bx < p.w - 4 for (bx, by) in base):
                continue
            torch(p, x, y, True, phase=phase, side=side, pool=pool)
            break


def torchlight(p: Pix, night: bool):
    """The finishing pass by night: each torch's light on the things stitched near it (and on the rod's pole),
    strongest nearest the flame. The linen and the words take none."""
    if not night:
        return
    base, pole = p.layers["base"], getattr(p, "pole", set())
    col = F_[4]
    alphas = (0.1, 0.22)
    n = len(alphas)
    for (cx, cy, r, phase, own) in p.lamps:
        Lf = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if ((x, y) not in base and (x, y) not in pole) or (x, y) in own:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15) / r
                if d < 1:
                    p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], Lf)


# --------------------------------------------------------------------------- the border's beasts
# The creatures of the border, each seven rows tall, as the embroiderers stitched them: flat wool in a couched
# outline with a round eye, each a silhouette of its own, and set so that each pair faces the other. A lion passant
# facing right, gold with a madder mane, his tail curled over his back to its tuft and a forepaw raised; a griffin
# facing left with an eagle's head and its hooked beak, a feathered wing raised over its lion's body; a hawk facing
# right with its wings raised; and a hound running left in its collar, its ears back.
LION = [
    "...tt...........mm...", "..t..t.........mmmm..", "..t....bbbbbbbbmEmmm.", "...t..bbbbbbbbbbmmmbb",
    "....ttbbbbbbbbbbmm.b.", "......b.bb...bb..bb..", ".....bb.b...bb.......",
]
GRIFFIN = [
    "......w.w.w.w......", ".hh....wwwwwww.....", "khEh....wwwwww....t", ".hhhbbbbbbbbbbb..t.",
    "...bbbbbbbbbbbbbt..", "...b.bb.....bb.b...", "..bb.b.....bb..bb..",
]
HAWK = [
    ".w.......w.", ".ww.....ww.", "..ww.hh.ww.", "..wwwhEkww.", "...wwhhww..", "....ttt....", "....f.f....",
]
HOUND = [
    ".ee.............", "hhhh..........t.", "Ehhhcbbbbbbbbbt.", "...cbbbbbbbbbb..", "..bb.b.....b.bb.",
    ".b....b...b....b", "b......bbb......",
]
KNOT = [
    "..111..", ".1..11.", "1..2.21", "1.222.1", ".12.21.", "..2.2..", "...2...",
]
BEASTS = ("lion", "griffin", "hawk", "hound")
ARTS = {"lion": LION, "griffin": GRIFFIN, "hawk": HAWK, "hound": HOUND}


def beast_pal(name: str, night: bool) -> tuple:
    """The wools a border creature is stitched in, and its outline's thread."""
    k = -1 if night else 0
    eye = L_[6]
    if name == "lion":
        return {"b": M_[4 + k], "m": T_[3 + k], "t": M_[3 + k], "E": eye}, U_[1]
    if name == "griffin":
        return {"b": W_[3 + k], "w": W_[4 + k], "h": W_[4 + k], "k": M_[4 + k], "t": W_[3 + k], "E": eye}, U_[1]
    if name == "hawk":
        return {"h": O_[4 + k], "w": O_[3 + k], "k": M_[4 + k], "t": O_[2 + k], "f": M_[4 + k], "E": eye}, U_[1]
    return {"b": T_[4 + k], "h": T_[4 + k], "e": T_[3 + k], "c": M_[4 + k], "t": T_[3 + k], "E": eye}, U_[1]


def symbol_of(p: Pix, key, art, pal, edge, flip=False):
    """A stitched figure kept once a file as a symbol, its outline included."""
    if key not in p.syms:
        q = Pix(len(art[0]) + 2, len(art) + 2)
        stitch(q, 1, 1, art, pal, "base", flip=flip, edge=edge)
        p.symbol(key, {(cx - 1, cy - 1): c for (cx, cy), c in q.layers["base"].items()})
    return key


def beast(p: Pix, name: str, x, y, night: bool, flip: bool = False, L="base"):
    """One creature of the border with its top-left at (x, y), facing the way its rows draw it unless
    flipped; drawn once a file and placed with a use. Returns its width."""
    art = ARTS[name]
    pal, edge = beast_pal(name, night)
    p.use(symbol_of(p, ("beast", name, night, flip), art, pal, edge, flip), x, y, L)
    return len(art[0])


def knot(p: Pix, x, y, night: bool, L="base"):
    """A knot of two strands, terracotta and olive, between the beasts."""
    k = -1 if night else 0
    p.use(symbol_of(p, ("knot", night), KNOT, {"1": T_[3 + k], "2": O_[3 + k]}, U_[1]), x, y, L)
    return 7


def vine_cells(length: int, variant: int, night: bool) -> dict:
    """A span of the border's vine `length` long: a stem wandering a row up and down, with a leaf turned up
    or down every so often and now and then a berry."""
    k = -1 if night else 0
    rnd = random.Random(variant * 13 + length)
    cells = {}
    yy = 3
    for i in range(length):
        if i % 4 == 3:
            yy = max(2, min(4, yy + rnd.choice((-1, 0, 1))))
        cells[(i, yy)] = O_[2 + k]
        if i % 7 == 3 and length - i > 3:
            up = (i // 7 + variant) % 2 == 0
            ly = yy - 1 if up else yy + 1
            cells[(i, ly)] = O_[4 + k]
            cells[(i + 1, ly)] = O_[3 + k]
            cells[(i + 1, ly - 1 if up else ly + 1)] = O_[4 + k]
            if rnd.random() < 0.3:
                cells[(i - 1, ly)] = T_[4 + k]
    return cells


def vine(p: Pix, x0, x1, y, night: bool, seed: int = 0, L="base"):
    """A span of the vine from x0 to x1 about row `y`: one of a few spans kept once a file, cut to the
    length and placed. A drawing made lighter keeps one span for each length, its leaves turned alike."""
    length = x1 - x0
    if length <= 0:
        return
    variant = 0 if p.lite else seed % 3
    key = ("vine", length, variant, night)
    if key not in p.syms:
        p.symbol(key, {(cx, cy - 3): c for (cx, cy), c in vine_cells(length, variant, night).items()})
    p.use(key, x0, y, L)


def beasts_along(p: Pix, x0, x1, y, night: bool, seed: int = 0, trail: bool = True) -> list:
    """The border's creatures in a row from x0 to x1 with their tops on row y: a lion, a griffin, a hawk and a
    hound by turns, each pair facing each other as the embroiderers set them, a knot between every other pair and
    the vine running on between, and on to x1 after the last of them. Without `trail` the run ends with its last
    whole creature and the span of vine before it, and nothing runs on. Returns what it set, in turn: (name, x,
    width, the span of vine before it), a knot named "knot"."""
    x, i, placed = x0, 0, []
    while x < x1:
        gap = 10 if i % 2 == 0 else 7
        name = "knot" if i % 4 == 3 else BEASTS[(i + seed) % len(BEASTS)]
        w = len(KNOT[0]) if name == "knot" else len(ARTS[name][0])
        if not trail and x + gap + w > x1:
            break
        if x + gap > x1:
            vine(p, x, x1, y + 3, night, seed + i)
            break
        vine(p, x, x + gap, y + 3, night, seed + i)
        x += gap
        if x + w > x1:
            vine(p, x, x1, y + 3, night, seed + i)
            break
        placed.append((name, x, w, gap))
        if name == "knot":
            knot(p, x, y, night)
        else:
            beast(p, name, x, y, night)
        x += w + 1
        i += 1
    return placed


def border(p: Pix, x0, x1, night: bool, seed: int = 0, comet: bool = False, gap=None):
    """The border band across a header between x0 and x1: twin couched rules with the beasts between them. In a
    wide header the comet crosses behind them. Given a `gap` (from, to), the box the month's mark takes with its
    margin, the beasts and the vine pause for it, and only the twin rules run on behind it: the run of beasts ends
    on its left with its last whole creature, and on its right the same creatures stand again in the mirror of
    their places, back to the band's end, so that the border stands even about the mark. No beast is cut at the
    mark's edge, and every creature and every span of the vine is one the band already keeps."""
    border_rules(p, x0, x1, night)
    y = BAND[0] + 1
    if comet:
        comet_drift(p, x0, x1, y, night, seed)
    if gap is None:
        beasts_along(p, x0 + 2, x1 - 2, y, night, seed)
        return
    a, b = gap
    placed = beasts_along(p, x0 + 2, a, y, night, seed, trail=False)
    turn = a + b                          # a column x on the left comes back at turn - x on the right
    for i, (name, bx, w, before) in enumerate(placed):
        rx = turn - bx - w
        vine(p, rx + w, rx + w + before, y + 3, night, seed + i)
        if name == "knot":
            knot(p, rx, y, night)
        else:
            beast(p, name, rx, y, night)


# --------------------------------------------------------------------------- the comet
def comet_cells(night: bool) -> dict:
    """The comet as the embroiderers stitched it: a star of gold with rays, trailing a long tail of three
    threads, gold between mustard, that fan apart as they go."""
    k = -1 if night else 0
    cells = {}
    for i in range(26):
        t = i / 25
        cells[(-4 - i, 0 if i < 9 else 1)] = G_[4 + k] if i % 3 != 2 else G_[5 + k]
        if i >= 3:
            cells[(-4 - i, -1 - int(t * 2))] = M_[4 + k] if i % 3 != 1 else M_[5 + k]
            cells[(-4 - i, 1 + int(t * 2) + (1 if i >= 9 else 0))] = M_[4 + k] if i % 3 != 0 else M_[5 + k]
    for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        cells[(dx, dy)] = G_[6]
    for (dx, dy) in ((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        cells[(dx, dy)] = G_[5 + k]
    for (dx, dy) in ((3, 0), (-3, 0), (0, 3), (2, 2), (2, -2), (-2, 2), (-2, -2)):
        cells[(dx, dy)] = G_[4 + k]
    return cells


STEP = 0.11   # the seconds the comet takes to step a pixel along the border band
STRIDE = 16   # the pixels it steps one at a time before the stride that carries them moves on


def _drift(values, dur: float) -> str:
    """A discrete translation through `values` (pixels to the right), each shown for an equal share of `dur`."""
    return (f'<animateTransform attributeName="transform" type="translate" values="{";".join(map(str, values))}" '
            f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/>')


def comet_drift(p: Pix, x0, x1, y, night: bool, seed: int = 0, name="cm"):
    """The comet crossing behind the border's beasts in a moving header, seen through the band from x0 to x1:
    placed once and again a period to the left, the two stepping right a pixel every 0.11 seconds, so it crosses,
    is gone a while, and crosses again. The period is the band's width rounded up to whole strides of sixteen
    pixels, and the steps are written as two drifts, one inside the other: sixteen steps of a pixel, carried along
    by a stride of sixteen at the end of each, so the motion costs forty numbers, not one for every pixel of the
    band. A still drawing shows it where it starts, among the beasts."""
    window = x1 - x0
    period = -(-window // STRIDE) * STRIDE
    cid = f"{name}c"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y}" width="{window}" height="{BAND[1] - y}"/></clipPath>')
    key = ("comet", night)
    if key not in p.syms:
        p.symbol(key, comet_cells(night))
    cx, cy, sid = x0 + window * 2 // 3 + (seed % 7), y + 3, p.syms[key]
    comet = f'<use href="#{sid}" x="{cx}" y="{cy}"/>'
    p.raw(-11, f'<g clip-path="url(#{cid})"><g><g>{comet}<use href="#{sid}" x="{cx - period}" y="{cy}"/>'
               f'{_drift(range(STRIDE), STRIDE * STEP)}</g>'
               f'{_drift(range(0, period, STRIDE), period * STEP)}</g></g>',
          f'<g clip-path="url(#{cid})">{comet}</g>')


# --------------------------------------------------------------------------- the title in wool
def wool_fill(r, c, scale, night, variant):
    """The colour of a title's letter at row `r` and column `c`: laid work in one of the wools, by letter,
    its threads lying on the diagonal, a darker thread and then a lighter one every sixth, by day and by
    torchlight alike (the gold of the night is in the couching and the finish)."""
    R = RAMP[WOOLS[variant % len(WOOLS)]]
    d = (c + r // 2) % 6
    if d == 0:
        return R[3]
    if d == 3:
        return R[5]
    return R[4]


def _by_letter(mid: float) -> int:
    """Which wool a letter takes: the line in four parts, a wool each."""
    return min(3, int(mid * 4))


WOOL = Paint("wool", wool_fill, period=6, variant=_by_letter)


def wool_tile(p: Pix, scale: int, night: bool, variant: int) -> str:
    """The laid work of a letter's wool (see `wool_fill`) as a pattern tile in the letter's own units, so that it
    starts at each letter's top left: a ground of the wool's middle tone with the darker thread and the lighter one
    laid over it on the diagonal, a step a pixel wide and two rows deep, kept once a file for each size and wool
    under the id the canvas would give it."""
    pid = f"pawool{scale}{'n' if night else 'd'}{variant}"
    if ("pattern", pid) not in p.syms:
        R = RAMP[WOOLS[variant % len(WOOLS)]]
        rows = 7 * scale
        threads = []
        for shift, colour in ((0, R[3]), (3, R[5])):
            d, at = [], (0, 0)
            for r in range(0, rows, 2):
                c = (shift - r // 2) % 6
                d.append(f"{'m' if d else 'M'}{c - at[0]} {r - at[1]}h1v{min(2, rows - r)}h-1z")
                at = (c, r)
            threads.append(f'<path fill="{colour}" d="{"".join(d)}"/>')
        p.defs.append(f'<pattern id="{pid}" width="{num(6 / scale)}" height="7" patternUnits="userSpaceOnUse">'
                      f'<g transform="scale({num(1 / scale)})"><rect width="6" height="{rows}" fill="{R[4]}"/>'
                      f'{"".join(threads)}</g></pattern>')
        p.syms[("pattern", pid)] = pid
    return pid


def inked(x, y, s: str, scale: int) -> set:
    """Every pixel a line of the title's face inks at `scale` with its top left at (x, y)."""
    glyphs, _, space = FONTS["57"]
    cells, cx = set(), x
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        for r, cols in enumerate(glyphs[ch][1]):
            for col in cols:
                x0, y0 = cx + col * scale, y + r * scale
                cells.update((x0 + dx, y0 + dy) for dy in range(scale) for dx in range(scale))
        cx += (glyphs[ch][0] + 1) * scale
    return cells


def letter(p: Pix, ch: str, scale: int, night: bool) -> tuple:
    """A title's letter, kept once a file for each letter and size as one symbol in the order it is stitched: the
    couching thread round it a pixel wide, dark by day and gold by night; the letter laid in the wool of the place it
    is set (it takes its stroke from there, see `title`); and by night the gold thread laid along the upper edge of
    every stroke and down its left, where the torchlight from above catches it. Returns its key."""
    key = ("letter", ch, scale, night)
    if key not in p.syms:
        glyph = ("glyph", "57", ch)
        if glyph not in p.syms:
            p.symbol(glyph, {(col, r): 1 for r, cols in enumerate(FONTS["57"][0][ch][1]) for col in cols}, mono=True)
        g, d = p.syms[glyph], num(1 / scale)
        couching = "".join(f'<use href="#{g}" {a}="{sg}{d}"/>' for a in "xy" for sg in ("-", ""))
        gold = {}
        if night:
            cells = inked(0, 0, ch, scale)
            for (x, y) in cells:
                if (x, y - 1) not in cells:
                    gold[(x, y)] = G_[5]
                elif (x - 1, y) not in cells:
                    gold[(x, y)] = G_[4]
        p.symbol(key, gold, shapes=f'<g transform="scale({scale})"><g stroke="{G_[2] if night else U_[1]}">'
                                   f'{couching}</g><use href="#{g}"/></g>')
    return key


def title(p: Pix, x, y, s, scale, night: bool, ink: str, lite: bool = False) -> int:
    """A title stitched in wool: every letter laid in one of the wools by turns, the line in four parts, couched
    round with a darker thread, and by night couched in gold, which catches the torchlight along the upper and left
    edges of every stroke and glints here and there; and a few loose ends of the couching thread left showing, which
    a drawing made lighter goes without. Each letter is one symbol (see `letter`) placed in its wool, so a title
    costs a use a letter and a letter it repeats costs nothing more. Its box is kept among the words, as a line of
    text's is. Returns its width (`ink` is the colour a title set in one colour would take; the wool stands in for
    it)."""
    s = fold(s, "57")
    glyphs, _, space = FONTS["57"]
    placed, cx = [], x
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    for ch, gx in placed:
        wool = wool_tile(p, scale, night, WOOL.variant((gx + glyphs[ch][0] * scale / 2 - x) / max(1, w)))
        p.use(letter(p, ch, scale, night), gx, y, stroke=f"url(#{wool})")
    rows = max((len(glyphs[ch][1]) for ch, _ in placed), default=0)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    cells = inked(x, y, s, scale)
    rnd = random.Random(len(s) * 7 + x * 3 + y)
    if night:
        tops = sorted(c for c in cells if (c[0], c[1] - 1) not in cells)
        for n in range(6 if scale >= 3 else 2):
            gx, gy = rnd.choice(tops)
            p.px(gx, gy, G_[6], p.twinkle(n))
    ends = sorted(c for c in cells if (c[0] + 1, c[1]) not in cells and (c[0], c[1] + 1) not in cells)
    if ends and not lite:
        L = p.layer("base~", z=0.3)
        for _ in range(3 if scale >= 3 else 2):
            gx, gy = rnd.choice(ends)
            for (dx, dy) in ((1, 1), (2, 1), (2, 2)):
                if (gx + dx, gy + dy) not in cells:
                    p.px(gx + dx, gy + dy, U_[1] if not night else G_[3], L)
    return w


# --------------------------------------------------------------------------- figures drawn once, worn in many wools
# A figure that stands more than once in a drawing in other wools (the two knights of the charge, the men of the
# shield wall) is composed once as a flat picture in which every cell has one role. The roles every one of them
# wears alike (the dark couching thread, the mail, the steel, the faces) make one symbol in their own colours; each
# role that changes (a horse's wool, a shield's field) makes a symbol of one path that takes the colour of the place
# it is used. So a figure's shape is written once a file however often it stands, and since no two roles share a
# cell, the order its symbols are drawn in does not matter.
def compose(parts) -> dict:
    """The flat picture of a figure from its `parts`, laid in turn each over those before it: (rows, chars, (x, y),
    edged), where `chars` maps a character of the rows to its role, and an `edged` part is couched round with the
    dark thread, the role "ink", over whatever lies under it. Returns {(x, y): role}."""
    cells: dict = {}
    for rows, chars, (ox, oy), edged in parts:
        own = {(ox + i, oy + j): chars[ch] for j, row in enumerate(rows) for i, ch in enumerate(row) if ch in chars}
        if edged:
            for (x, y) in own:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, y + dy) not in own:
                        cells[(x + dx, y + dy)] = "ink"
        cells.update(own)
    return cells


def shape(p: Pix, key, cells: dict, fixed: dict) -> tuple:
    """A figure's flat picture kept once a file under `key`: the cells of the roles named in `fixed` ({role:
    colour}) as one symbol in those colours, and each other role as a symbol of one path. Returns their keys."""
    k = ("shape", key)
    if k not in p.syms:
        own = {xy: fixed[r] for xy, r in cells.items() if r in fixed}
        fk = (k, "") if own else None
        if fk:
            p.symbol(fk, own)
        monos = {}
        for r in sorted({r for r in cells.values() if r not in fixed}):
            monos[r] = (k, r)
            p.symbol(monos[r], {xy: 1 for xy, rr in cells.items() if rr == r}, mono=True)
        p.syms[k] = (fk, monos)
    return p.syms[k]


def wear(p: Pix, keys: tuple, wools: dict, x, y, L="base"):
    """A figure kept by `shape` set with its frame's origin at (x, y) on layer L, each changing role in the colour
    `wools` gives it."""
    fk, monos = keys
    if fk:
        p.use(fk, x, y, L)
    for role, mk in monos.items():
        p.use(mk, x, y, L, stroke=wools[role])


# --------------------------------------------------------------------------- the horse
# A horse at the gallop as the embroiderers drew it, set pixel by pixel: it faces right in a frame 36 wide with its
# ears on row 0 and its hooves on row 24; a small head with its ears pricked, a round eye and the noseband of its
# bridle, an arched neck under a mane of another wool, a deep chest, a round rump and its tail flying. b the horse's
# wool, m its mane and tail, e the white of its eye, p the eye, the nostril and the noseband.
HORSE = [
    "......................b.b...........",
    ".....................mbbb...........",
    "....................mmbbbb..........",
    "...................mmbbbbbb.........",
    "..................mmbbbbepbb........",
    ".................mmbbbbbbbbbb.......",
    "................mmbbbbbbbbbbbb......",
    "...............mmbbbbbbbb.bbpbb.....",
    "..mmm.bbbb....mmbbbbbbbb...pbbpb....",
    ".mmmmmbbbbbbbbmbbbbbbbbb....pbb.....",
    "mm..mbbbbbbbbbbbbbbbbbbb............",
    "m...mbbbbbbbbbbbbbbbbbbbb...........",
    "m...bbbbbbbbbbbbbbbbbbbbb...........",
    "....bbbbbbbbbbbbbbbbbbbbb...........",
    "....bbbbbbbbbbbbbbbbbbbbb...........",
    ".....bbbbbbbbbbbbbbbbbbb............",
    "......bbbbbbbbbbbbbbbbb.............",
]
# The stem stitch in the deepest wool that marks the horse's shoulder and its haunch.
HORSE_LINES = {(16, 10), (17, 11), (17, 12), (18, 13), (18, 14), (19, 15), (8, 10), (7, 11), (7, 12), (7, 13),
               (8, 14), (9, 15)}
# Its legs from row 14, under the body, at three moments of the gallop (stretched out, gathered under, landing on a
# foreleg) and standing with a forefoot raised. h the near legs in the horse's wool, f the far legs in a deeper
# one, k the hooves.
GALLOP = (
    [".......hhhff.......ffhh.............", ".......hhhfff......ffhhh............",
     "......hhhhff.......ffhhh............", "......hhhfff........ffhhh...........",
     "......hh.ff.........fffhh...........", ".....hhh.ff..........ffhhh..........",
     "....hhh.ff............ffhhh.........", "...hhh.fff............fffhhh........",
     "...hh..ff..............ff.hh........", "..hh..ff................ff.hh.......",
     ".kk..kk..................kk.kk......"],
    ["........hhhf.......ffhh.............", "........hhhff.....ffhhh.............",
     ".........hhhf.....fffhhh............", ".........hhhf......ffhhh............",
     "..........hhf......fffhhh...........", "..........hhhf......ff.hh...........",
     "...........hhf......ffhhh...........", "............hhf....ffhh.............",
     "............hhff...fhh..............", ".............hhfkkfkkh..............",
     "..............kk...................."],
    [".......hhhff.......ffhh.............", ".......hhhfff.....ffhhh.............",
     "......hhhhff.......fhhh.............", "......hhhfff........fhh.............",
     ".....hhh..ff.........hh.............", ".....hh...ff.........hh.............",
     "....hhh..ff..........hh.............", "....hh...ff..........hh.............",
     "...hh....ff.........ffh.............", "...hh....f.........kkfh.............",
     "..kk....kk............kk............"],
)
STAND = [".......hhff........ffhh.............", ".......hhff........ffhh.............",
         "......hhhff........ffhhh............", "......hhhff........ffhhhh...........",
         "......hh.ff........ff..hh...........", ".....hh..ff........ff..hh...........",
         ".....hh..ff........ff.hh............", "....hh...ff........ff.hk............",
         "....hh...ff........ff...............", "....hh...ff........ff...............",
         "...kk....kk........kk..............."]


def _laid(rows: list) -> list:
    """The horse's rows with its laid work showing: a diagonal of the couching thread every fourth pixel across
    the body below its back, and the stem stitch of its shoulder and haunch."""
    out = []
    for j, row in enumerate(rows):
        out.append("".join("d" if ch == "b" and (i, j) in HORSE_LINES else
                           "x" if ch == "b" and j > 8 and (i + j) % 4 == 0 else ch for i, ch in enumerate(row)))
    return out


HORSE_LAID = _laid(HORSE)
HORSE_ROLES = {"b": "horse", "x": "hatch", "d": "deep", "m": "mane", "e": "white", "p": "ink"}
LEG_ROLES = {"h": "horse", "f": "deep", "k": "ink"}

# --------------------------------------------------------------------------- the knight
# The knight in the saddle, set over the horse's frame from row -7: a conical helm of steel with its nasal over a
# coif of mail, his face with its round eye, a hauberk of mail to the saddle, the kite shield on his far arm held up
# before him with its device, his near hand on the lance and his leg down the horse's side to the stirrup. H the
# helm, h its shade and the nasal, b its brim, c the coif and his arm, F his face, e his eye and his shoe, m the mail,
# g his hand, S the shield, x its device.
RIDER = [
    "..............H.......", ".............HHh......", "............HHHh......", "............HHHhh.....",
    "...........bbbbbbh....", "...........ccccFFh....", "...........cccFeF.....", "...........ccccFF.....",
    "..........mmmmcc.SSS..", "..........mmcmmmSSSSS.", "..........mmcmmmSSxSS.", "..........mmmcmSSxxxS.",
    "..........mmmmcgSSxSS.", "..........mmmmmmSSxSS.", "..........mmmmmm.SxS..", ".........mmmmmmmmSSS..",
    "........mmmmmmmmm.S...", ".............mm.......", ".............mm.......", "..............mm......",
    "..............mm......", "..............mm......", "..............mm......", "..............mmm.....",
    ".............eeee.....",
]
# The saddle cloth under him, its edge of another tone, and its fringe.
SADDLE = ["........sssssss.", ".......ssssssss.", ".......zsssssss.", "........sssssss.", ".........zzzzz.."]
RIDER_ROLES = {"H": "helm", "h": "shade", "b": "brim", "c": "coif", "F": "face", "e": "ink", "m": "mail",
               "g": "hand", "S": "shield", "x": "device"}


def _ringed(rows: list) -> list:
    """The mail of a rider's rows worked in rings: every other pixel a link catching the light."""
    return ["".join("r" if ch == "m" and (i + j) % 2 == 0 else ch for i, ch in enumerate(row))
            for j, row in enumerate(rows)]


RIDER_RINGED = _ringed(RIDER)
LANCE_ROW = 5   # the row of the horse's frame a couched lance lies along
FIGURES: dict = {}


def knight_cells(arms: str = "lance", plain: bool = False) -> dict:
    """The flat picture of a knight on his horse without its legs: the horse, the saddle cloth, the rider, and
    what he carries in his near hand: a lance couched along row 5, its butt behind him and its point well ahead of
    the horse's nose (it passes behind the shield and the horse's head), or the pole of a banner held upright.
    `plain` lays the horse's body without the diagonal of its laid work and the mail without its rings, the fine
    texture a drawing made lighter goes without."""
    if ("knight", arms, plain) not in FIGURES:
        horse = dict(HORSE_ROLES, x="horse") if plain else HORSE_ROLES
        parts = [(HORSE_LAID, horse, (0, 0), True), (SADDLE, {"s": "cloth", "z": "fringe"}, (0, 8), True),
                 (RIDER_RINGED, dict(RIDER_ROLES, r="mail" if plain else "ring"), (0, -7), True)]
        if arms == "lance":
            parts += [(["w" * 13], {"w": "wood"}, (2, LANCE_ROW), False),
                      (["g"], {"g": "hand"}, (15, LANCE_ROW), False),
                      (["wwwwwwwwPP"], {"w": "wood", "P": "point"}, (30, LANCE_ROW), False)]
        elif arms == "banner":
            parts += [(["w"] * 11, {"w": "wood"}, (20, -8), False), (["g"], {"g": "hand"}, (20, 2), False)]
        FIGURES[("knight", arms, plain)] = compose(parts)
    return FIGURES[("knight", arms, plain)]


def legs_cells(frame, arms: str = "lance") -> dict:
    """A moment of the horse's legs, `frame` a moment of the gallop or "stand", couched round and cut away where
    the knight above them lies, so they can be drawn in a layer of their own under or over him."""
    if ("legs", frame, arms) not in FIGURES:
        rows = STAND if frame == "stand" else GALLOP[frame % 3]
        over = knight_cells(arms)
        FIGURES[("legs", frame, arms)] = {xy: r for xy, r in compose([(rows, LEG_ROLES, (0, 14), True)]).items()
                                          if xy not in over}
    return FIGURES[("legs", frame, arms)]


def mirrored(cells: dict, w: int = 36) -> dict:
    """A flat picture turned to face the other way within a frame `w` wide."""
    return {(w - 1 - x, y): r for (x, y), r in cells.items()}


def knight_fixed(night: bool) -> dict:
    """The colours a knight wears whatever his wools: the couching thread, his mail and steel, and the ash of his
    lance (pale by torchlight, where umber would be lost). His face and his hands are on his own skin (see
    `knight_wools`)."""
    k = -1 if night else 0
    return {"ink": U_[1], "white": L_[6], "helm": S_[4 + k], "shade": S_[2 + k], "brim": S_[3 + k], "coif": W_[2 + k],
            "mail": W_[3 + k], "ring": W_[4 + k], "leather": U_[3 + k] if not night else U_[3],
            "wood": U_[4] if not night else L_[2], "point": S_[5 + k]}


def knight_wools(night: bool, horse: str, mane: str, cloth: str, shield: str, device: str, face: int = 0) -> dict:
    """The wools a knight's changing roles take: his horse's body, its laid work and its far legs, its mane, the
    saddle cloth and its fringe, the shield's field and its device, and his face and hands on the hand's skin
    `face`."""
    k = -1 if night else 0
    return {"horse": RAMP[horse][4 + k], "hatch": RAMP[horse][3 + k], "deep": RAMP[horse][2 + k],
            "mane": RAMP[mane][4 + k], "cloth": RAMP[cloth][3 + k], "fringe": RAMP[cloth][5 + k],
            "shield": RAMP[shield][4 + k], "device": RAMP[device][2 + k], "face": skin(face, night),
            "hand": skin(face, night)}


def pennon_cells(frame: int) -> dict:
    """A lance's pennon at a moment of its wave, flying back from its hoist at x 0: two tails, the upper in one
    wool and the lower in another, the far ends lifting and falling, couched round."""
    own = {}
    for j, n in enumerate((8, 6, 6, 8)):
        for i in range(n):
            lift = ((frame + i // 3) % 3) - 1 if i >= 3 else 0
            own[(-i, j + lift)] = "a" if j < 2 else "b"
    cells = {}
    for (x, y) in own:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in own:
                cells[(x + dx, y + dy)] = "ink"
    cells.update(own)
    return cells


def pennon(p: Pix, x, y, night: bool, wools: tuple, frame: int, L: str, flip: bool = False):
    """A pennon at a moment of its wave with its hoist at (x, y), in its two `wools`, kept once a file; `flip`
    flies it the other way."""
    k = -1 if night else 0
    key = ("pennon", wools, frame % 3, flip, night)
    if key not in p.syms:
        colours = {"ink": U_[1], "a": RAMP[wools[0]][4 + k], "b": RAMP[wools[1]][4 + k]}
        p.symbol(key, {(-cx if flip else cx, cy): colours[r] for (cx, cy), r in pennon_cells(frame % 3).items()})
    p.use(key, x, y, L)


def wave_layer(p: Pix, k: int, still: bool = False, z: float = 1) -> str:
    """One of three moments of a wave, shown in turn; a still drawing keeps the first, laid in the base."""
    if still:
        return "base"
    return p.seq(f"wv{k % 3}", (k % 3) / 3, (k % 3 + 1) / 3, 1.2, keep=k % 3 == 0, z=z)


def gallop_layer(p: Pix, k: int) -> str:
    """One of three moments of the gallop, shown in turn, quicker than the wave, under every knight."""
    return p.seq(f"gp{k % 3}", (k % 3) / 3, (k % 3 + 1) / 3, 0.66, keep=k % 3 == 0, z=-3)


def knight(p: Pix, x, g, night: bool, scheme: tuple, L: str, moving: bool = False, phase: int = 0,
           arms: str = "lance", gait: str = "gallop", colours: tuple = ("mustard", "terracotta"), flip: bool = False,
           face: int = 0):
    """A mounted knight riding right, his horse's frame from column x with its hooves on row g, on layer L: his
    horse in the wools of `scheme` (horse, mane, saddle cloth, shield, device), its legs at the gallop (three
    moments in turn in a moving drawing, `phase` moments along) or standing; and the pennon on his lance in the two
    wools of `colours`, waving under his layer so the lance lies over its tails (every pennon of a drawing waves
    in the same three moments, under the first knight's layer); `flip` turns him to ride left; his face and his
    hands are on the hand's skin `face`. His shape is kept once a file, so a second knight costs only his wools; a
    drawing made lighter stitches him plain (see `knight_cells`)."""
    top = g - 24
    if arms == "lance":
        z = p.meta[L][0] if L in p.meta else 0
        for slot in range(3 if moving else 1):
            Lp = p.seq(f"pennon{slot}", slot / 3, (slot + 1) / 3, 1.2, keep=slot == 0, z=z - 0.1) if moving else L
            pennon(p, x + (37 if not flip else -2), top + 1, night, colours, slot + phase, Lp, flip)
    fixed = knight_fixed(night)
    wools = knight_wools(night, *scheme, face=face)

    def turned(cells):
        return mirrored(cells) if flip else cells
    key = ("knight", arms, flip, night) + (("plain",) if p.lite else ())
    wear(p, shape(p, key, turned(knight_cells(arms, p.lite)), fixed), wools, x, top, L)
    if gait == "gallop" and moving:
        for slot in range(3):
            frame = (slot + phase) % 3
            wear(p, shape(p, ("legs", frame, arms, flip, night), turned(legs_cells(frame, arms)), fixed), wools, x,
                 top, gallop_layer(p, slot))
    else:
        frame = 0 if gait == "gallop" else "stand"
        wear(p, shape(p, ("legs", frame, arms, flip, night), turned(legs_cells(frame, arms)), fixed), wools, x, top,
             L)


# --------------------------------------------------------------------------- the shield wall
# A man of the English shield wall, facing left in a frame 11 wide from his helm's point on row 0 to his shoes on
# row 21: a conical helm with its nasal, his face and his moustache, a coif of mail, a tunic of his own wool and
# cross gartered legs. H the helm, h its shade, b its brim, F his face, e his eye, u his moustache and his garters,
# c the coif, t the tunic, k his shoes.
MAN = [
    ".....H.....", "....HHh....", "....HHHh...", "...bbbbbb..", "..hFFcccc..", "...eFcccc..", "..uuFcccc..",
    "...FFccc...", "...ttttttt.", "..tttttttt.", "..ttttttttt", "..ttttttttt", "..ttttttttt", "..ttttttttt",
    "...tttttt..", "...tttttt..", "....tttt...", "....tt.tt..", "....tt..t..", "....uu..u..", "....uu..u..",
    "...kkk.kk..",
]
# His kite shield, held before him so that the wall's shields overlap: S its field, o its device, O its boss.
WALL_SHIELD = ["..SSSS..", ".SSSSSS.", "SSSSSSSS", "SSSoSSSS", "SSoOoSSS", "SSSoSSSS", "SSSSSSSS", ".SSSSSS.",
               ".SSSSSS.", "..SSSS..", "..SSSS..", "...SS..."]
MAN_ROLES = {"H": "helm", "h": "shade", "b": "brim", "F": "face", "e": "ink", "u": "garter", "c": "coif",
             "t": "tunic", "k": "ink"}
SHIELD_ROLES = {"S": "shield", "o": "device", "O": "boss"}
# The men from the front of the wall (the left) to its back: each one's offset, tunic, shield and device, his spear
# from his hand (braced low at the horses of the charge, raised to strike, and upright) and the hand's skin he is
# stitched in.
WALL = ((0, "olive", "woad", "mustard", ((10, 11), (-12, 17)), 0),
        (8, "terracotta", "mustard", "woad", ((16, 9), (2, -7)), 2),
        (16, "mustard", "terracotta", "mustard", ((24, 9), (24, -16)), 1))


def man_fixed(night: bool) -> dict:
    """The colours a man of the wall wears whatever his tunic: the couching thread, his helm and coif, his garters
    and his shield's boss. His face is on his own skin (see `man`)."""
    k = -1 if night else 0
    return {"ink": U_[1], "helm": S_[4 + k], "shade": S_[2 + k], "brim": S_[3 + k],
            "garter": U_[3 + k] if not night else U_[4], "coif": W_[2 + k], "boss": S_[5 + k]}


def man(p: Pix, x, top, night: bool, tunic: str, face: int, L="base"):
    """A man of the wall, kept once a file, with his frame from (x, top), in a tunic of the wool `tunic` and his
    face on the hand's skin `face`."""
    shaped = shape(p, ("man", night), compose([(MAN, MAN_ROLES, (0, 0), True)]), man_fixed(night))
    wear(p, shaped, {"tunic": RAMP[tunic][4 - (1 if night else 0)], "face": skin(face, night)}, x, top, L)


def line(a, b) -> list:
    """The pixels of a straight stitch from a to b, a pixel at a time."""
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]


def spear(p: Pix, a, b, night: bool, L: str):
    """A spear from its butt at a to its point at b: an ash shaft and a leaf of steel, cut short of any word."""
    keep = []
    for (x, y) in line(a, b):
        if not p.clear_of_words(x - 3, y - 3, x + 4, y + 4):
            break
        keep.append((x, y))
    if len(keep) < 4:
        return
    wood = U_[4] if not night else L_[2]
    for (x, y) in keep[:-2]:
        p.px(x, y, wood, L)
    for (x, y) in keep[-2:]:
        p.px(x, y, S_[5 if not night else 4], L)


def shield_wall(p: Pix, x, g, night: bool, room: int, spears: bool = True):
    """Three men of the English shield wall facing left, their feet on row g and the first man's frame from column
    x: the men in their tunics behind their overlapping kite shields, and with the `room` for them (40 rows) their
    spears at three angles, the first braced low at the charge, the second raised to strike, the third upright;
    with less, every spear held low. The men and their shields stand in layers of their own, the back of the wall
    first and every shield over every man, so the shields overlap as a wall. Returns the span covered."""
    top = g - 21
    fixed = man_fixed(night)
    k = -1 if night else 0
    guard = shape(p, ("wallshield", night), compose([(WALL_SHIELD, SHIELD_ROLES, (0, 0), True)]), fixed)
    Ls = p.layer("sp", z=-0.6)
    for i, (dx, tunic, sh, dev, (a, b), face) in enumerate(reversed(WALL)):
        if spears:
            if room < 40:
                a, b = (dx + 10, 11), (dx - 12, 11)
            spear(p, (x + a[0], top + a[1]), (x + b[0], top + b[1]), night, Ls)
        man(p, x + dx, top, night, tunic, face, p.layer(f"wm{i}", z=-0.5 + i * 0.01))
        wear(p, guard, {"shield": RAMP[sh][4 + k], "device": RAMP[dev][3 + k]}, x + dx - 1, top + 9,
             p.layer(f"ws{i}", z=-0.45 + i * 0.01))
    return (x - 2, x + 28)


# --------------------------------------------------------------------------- the trees
# A tall tree as the embroiderers stitched them, 25 wide and 46 tall: a trunk of two strands twisting about each
# other, parting into boughs that cross once and open into fans of leaves in three wools, and roots that spread. 1 a
# strand in terracotta and 5 the other a tone deeper, 2 olive leaves, 3 mustard and 4 sage.
TALL = [
    ".........3.3333..........", ".......33333333.3........", ".......33333333333.......", ".......33333333333.......",
    "......333333333333.......", ".....333333333333344.....", ".....22....11..4444444...", "..222222...11.4444444444.",
    ".222222222.11..444444444.", ".222222222211444444444444", "222222222221144445544444.", "2222211222211...555......",
    "......111..11...55.......", ".......111..1..55........", ".........11.1.55.........", ".......4.411155..22......",
    ".....44444411522222.2....", "......4444455122222222...", "....444444455122222222...", "....44445455411221222....",
    "........5555.11.11.......", ".........55...111........", "........55....111........", ".......5555...111........",
    "........555...11.........", "........555..111.........", ".........555.11..........", ".........555111..........",
    "..........5551...........", "...........55............", "..........5511...........", "..........5115...........",
    "..........1155...........", "..........1551...........", "..........5511...........", "..........5115...........",
    "..........1155...........", "..........1551...........", "..........5511...........", "..........5115...........",
    "..........1155...........", "..........1551...........", ".........111111..........", "........11111111.........",
    "......111.1111.111.......", ".....111..1111..111......",
]
# A smaller tree for a phone or a strip, 20 wide and 26 tall: a trunk of terracotta whose branches twist round one
# another in a knot and open into tufts of leaves in three wools.
TREE = [
    "......2222..33333...", ".....22222.33333333.", ".....222222.3333333.", "..2.2..2222.3.333...",
    "2222.2.2211.1.333...", ".2222222.111.1..3...", "..22..1..111.1..4...", ".....11..111.1.44...",
    ".....1111.111..444..", "......11.11.11444...", ".......1111.1444....", "........11.11.4.....",
    ".......111.111......", "......1111111.......", "......111.111.......", ".......11111........",
    "........111.........", "........111.........", "........111.........", "........111.........",
    "........111.........", ".......1111.........", ".......11111........", "......1111111.......",
    ".....11111111.......", "....11111.1111......",
]


def tree_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"1": T_[3 + k], "5": T_[2 + k], "2": O_[4 + k], "3": M_[4 + k], "4": RAMP["sage"][4 + k]}


TRUNK = (30, 42)   # the tall tree's twisted trunk, rows 30 to 41, its two strands crossing every four rows
TALLEST = 62       # the tallest the tall tree grows, its trunk twisting on for sixteen rows more


def tall_rows(height: int = len(TALL)) -> list:
    """The tall tree's rows grown or cut to `height` rows by twisting its trunk on for more rows or fewer, so that its
    crown, its boughs and its roots keep their shape whatever its height: from 38 rows to `TALLEST`."""
    a, b = TRUNK
    n = max(4, b - a + min(height, TALLEST) - len(TALL))
    twist = TALL[a:a + 4]
    return TALL[:a] + [twist[(i - n) % 4] for i in range(n)] + TALL[b:]


def tall_tree(p: Pix, x, g, night: bool, L="base", height: int = len(TALL)):
    """The tall tree with its roots on row g and its frame from column x, grown or cut to `height` rows (see
    `tall_rows`). Returns the span covered."""
    rows = tall_rows(height)
    stitch(p, x, g - len(rows) + 1, rows, tree_pal(night), L, edge=U_[1])
    return (x - 1, x + 26)


def tree(p: Pix, x, g, night: bool, L="base", height: int | None = None, hawk: bool = False):
    """The smaller tree with its roots on the row above `g`, 20 wide from x, cut to `height` rows from the ground
    when the words leave fewer than it stands; a hawk sits in its upper branches when asked."""
    rows = TREE if height is None or height >= len(TREE) else TREE[len(TREE) - height:]
    stitch(p, x, g - len(rows), rows, tree_pal(night), L, edge=U_[1])
    if hawk and (height is None or height >= 22):
        q = Pix(13, 9)
        stitch(q, 1, 1, HAWK, beast_pal("hawk", night)[0], "base", edge=U_[1])
        for (cx, cy), c in q.layers["base"].items():
            p.px(x + 8 + cx - 1, g - len(rows) - 9 + cy - 1, c, L)
    return (x - 1, x + 21)


# --------------------------------------------------------------------------- banners
GONFANON = ["11111111", "11111111", "11111111", "11111111", "11111111", "11111111", "11.11.11", "11.11.11",
            "11.11.11", "11.11.11"]


def banner_frames(p: Pix, wool: str, night: bool) -> list:
    """A small gonfanon, the square banner with three tails hanging, at three moments of its wave: the keys of
    its symbols, each with a cross of the contrasting wool on its field."""
    k = -1 if night else 0
    R = RAMP[wool]
    charge = M_[4 + k] if wool != "mustard" else T_[3 + k]
    keys = []
    for frame in range(3):
        key = ("gonfanon", wool, frame, night)
        if key not in p.syms:
            cells = {}
            for j, row in enumerate(GONFANON):
                for i, ch in enumerate(row):
                    if ch != "1":
                        continue
                    sway = ((frame + j // 2) % 3) - 1 if j >= 6 else (1 if frame == 1 and j > 2 else 0)
                    c = R[4 + k] if j < 6 else R[3 + k]
                    if j < 6 and (i == 3 or j == 2):
                        c = charge
                    cells[(i + sway, j)] = c
            for q in list(cells):
                for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    if (q[0] + dx, q[1] + dy) not in cells:
                        cells.setdefault((q[0] + dx, q[1] + dy), U_[1])
            p.symbol(key, cells)
        keys.append(key)
    return keys


def banner(p: Pix, x, top, foot, night: bool, wool: str = "mustard", still: bool = True, L="base", phase=0):
    """A small gonfanon on a pole from `foot` up to `top` at column x, flying to the right from the pole's head
    and waving in a moving header; the pole is tipped with steel."""
    k = -1 if night else 0
    for yy in range(top, foot):
        p.px(x, yy, U_[4] if not night else L_[2], L)
    p.px(x, top - 1, S_[6 + k], L)
    frames = banner_frames(p, wool, night)
    for slot in range(1 if still else 3):
        p.use(frames[(slot + phase) % 3], x + 1, top, wave_layer(p, slot, still))


def standard_cells(frame: int) -> dict:
    """The horseman's great gonfanon at a moment of its wave, flying from its pole at x 0 to the right: a field 11
    wide and 9 deep with a cross on it and a border along its head and foot, and three tails from its fly that lift
    and fall, couched round. f the field, c the cross and the border, t the tails."""
    own = {}
    for j in range(9):
        lift = 1 if frame == 1 and j > 3 else 0
        for i in range(1, 12):
            role = "c" if j in (0, 8) or i == 5 or j == 4 else "f"
            own[(i, j + (lift if i > 6 else 0))] = role
    for n, j in enumerate((0, 4, 8)):
        for i in range(12, 18):
            sway = ((frame + i // 2 + n) % 3) - 1 if i > 13 else 0
            own[(i, j + sway)] = "t"
    cells = {}
    for (x, y) in own:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in own and x + dx > 0:
                cells[(x + dx, y + dy)] = "ink"
    cells.update(own)
    return cells


def standard(p: Pix, x, y, night: bool, wools: tuple, frame: int, L: str, flip: bool = False):
    """The great gonfanon with its pole's head at (x, y), flying right (left when `flip`), in its field's wool and
    its cross's, kept once a file at each moment of its wave."""
    k = -1 if night else 0
    key = ("standard", wools, frame % 3, flip, night)
    if key not in p.syms:
        colours = {"ink": U_[1], "f": RAMP[wools[0]][4 + k], "c": RAMP[wools[1]][4 + k], "t": RAMP[wools[0]][3 + k]}
        p.symbol(key, {(-cx if flip else cx, cy): colours[r] for (cx, cy), r in standard_cells(frame % 3).items()})
    p.use(key, x, y, L)


def horseman(p: Pix, x0, x1, g, night: bool, room: int, still: bool = True) -> bool:
    """A lone horseman with his banner raised, riding toward the title at the left, in the columns from x0 to x1
    over the ground at row g, built to the `room` of rows free over it: the tall tree at the edge with 46 rows; the
    horseman before it on his horse standing with a forefoot raised, with 56 rows his great gonfanon streaming back
    from the head of a tall pole as high as the room allows (no higher than a lance and a half) and waving in a
    moving header, with fewer his lance couched; a hound running ahead of him where the columns allow; under 32
    rows a man of the wall stands alone, and under 22 nothing."""
    if room < 22:
        return False
    k = -1 if night else 0
    if room < 32:
        man(p, x1 - 16, g - 21, night, "woad", 1)
        return True
    edge = x1
    if room >= 46:
        tall_tree(p, x1 - 26, g, night, p.layer("tr", z=-0.7))
        edge = x1 - 22
    x = edge - 37
    scheme = ("mustard", "olive", "terracotta", "terracotta", "mustard")
    if room < 56:
        knight(p, x, g, night, scheme, "base", moving=not still, gait="stand", colours=("woad", "mustard"), flip=True)
    else:
        knight(p, x, g, night, scheme, "base", moving=not still, arms="banner", gait="stand", flip=True)
        top = max(g - room + 2, g - 24 - 46)
        pole = x + 15
        for yy in range(top + 1, g - 32):
            p.px(pole, yy, U_[4] if not night else L_[2])
        p.px(pole, top, S_[6 + k])
        for slot in range(1 if still else 3):
            standard(p, pole, top + 1, night, ("terracotta", "mustard"), slot, wave_layer(p, slot, still))
    if x - x0 >= 26:
        hound(p, x - 25, g, night, "terracotta", "mustard", flip=True)
    return True


# --------------------------------------------------------------------------- the great horseman
# The hero of a section's header is a horseman as large again as the knights of the charge, as the embroiderers drew
# the duke larger than the men about him: the knight's own figure grown to twice its size by the pixel artist's rule
# (`scale2x`), so that he keeps the embroidery's proportions, and stitched again at the thread's own fineness: couched
# round a pixel wide, the horse's laid work and its stem stitches laid again, the mail in its rings, and the eyes set
# as the knights' are. His frame is 72 wide, his horse's ears on its row 0 and its hooves on its row 49.
GREAT_W, GREAT_FOOT = 72, 49
GREAT_ROOM = 70     # the rows over the ground the great horseman and the head of his banner's pole take


def scale2x(rows: list) -> list:
    """Pixel art grown to twice its size as pixel artists grow it (Scale2x): every pixel becomes four, and each of
    the four takes the character of the two neighbours that meet at its corner where those two agree and the other
    two do not, so a diagonal steps a pixel at a time rather than in blocks and a figure keeps its shape. The
    characters stand for what is stitched there; '.' is the bare cloth."""
    h, w = len(rows), max(len(r) for r in rows)

    def at(i, j):
        return rows[j][i] if 0 <= j < h and 0 <= i < len(rows[j]) else "."
    out = [["."] * (2 * w) for _ in range(2 * h)]
    for j in range(h):
        for i in range(w):
            c, up, right, left, down = at(i, j), at(i, j - 1), at(i + 1, j), at(i - 1, j), at(i, j + 1)
            out[2 * j][2 * i] = up if left == up and left != down and up != right else c
            out[2 * j][2 * i + 1] = right if up == right and up != left and right != down else c
            out[2 * j + 1][2 * i] = left if down == left and down != right and left != up else c
            out[2 * j + 1][2 * i + 1] = down if right == down and right != up and down != left else c
    return ["".join(r) for r in out]


def _stem(points) -> set:
    """The pixels of a stem stitch through `points`, a pixel at a time from each to the next."""
    out = set()
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        out.update((round(x0 + (x1 - x0) * t / n), round(y0 + (y1 - y0) * t / n)) for t in range(n + 1))
    return out


def great_knight_cells(plain: bool = False) -> dict:
    """The flat picture of the great horseman bearing his banner, without his horse's legs (see `GREAT_W`): his horse,
    its saddle cloth and the rider grown twice and couched round a pixel wide, and the pole of his banner in his near
    hand; the horse's laid work again on the diagonal every fourth thread below its back, with the stem stitches at
    its shoulder and its haunch; the mail in rings; and the eyes set as an eye is, the rider's a dark stitch with a
    white one behind it, the horse's a dark stitch in its white. `plain` stitches the horse without its laid work
    and the mail without its rings, the fine texture a drawing made lighter goes without."""
    key = ("great", plain)
    if key not in FIGURES:
        shoe = scale2x(RIDER[:-1] + [RIDER[-1].replace("e", "o")])     # his shoe in leather, couched round
        cells = compose([(scale2x(HORSE), HORSE_ROLES, (0, 0), True),
                         (scale2x(SADDLE), {"s": "cloth", "z": "fringe"}, (0, 16), True),
                         (shoe, dict(RIDER_ROLES, o="leather"), (0, -14), True),
                         (["ww"] * 22, {"w": "wood"}, (40, -16), False), (["gg", "gg"], {"g": "hand"}, (40, 4), False)])
        if not plain:
            for (x, y), r in list(cells.items()):
                if r == "horse" and y > 17 and (x + y) % 4 == 0:
                    cells[(x, y)] = "hatch"
                elif r == "mail" and (x + y) % 2 == 0:
                    cells[(x, y)] = "ring"
            shoulder = [(2 * x, 2 * y) for (x, y) in sorted(HORSE_LINES) if x >= 16]
            haunch = [(2 * x, 2 * y) for (x, y) in sorted(HORSE_LINES, key=lambda q: q[1]) if x < 16]
            for xy in _stem(sorted(shoulder, key=lambda q: q[1])) | _stem(haunch):
                if cells.get(xy) in ("horse", "hatch"):
                    cells[xy] = "deep"
        # the rider's eye: a dark stitch looking ahead, a white one behind it, his face round them
        ex, ey = 30, 2 * 6 - 14
        cells.update({(ex, ey): "white", (ex + 1, ey): "ink", (ex, ey + 1): "face", (ex + 1, ey + 1): "face"})
        # the horse's eye: its white, and in it a dark stitch looking ahead
        cells.update({(48, 8): "white", (49, 8): "white", (48, 9): "white", (49, 9): "ink",
                      (50, 8): "horse", (51, 8): "horse", (50, 9): "horse", (51, 9): "horse"})
        FIGURES[key] = cells
    return FIGURES[key]


def great_legs_cells() -> dict:
    """The great horse's legs standing with a forefoot raised, grown twice and couched round, its hooves in a
    darker wool than the thread round them, cut away where its body and its rider lie."""
    if ("greatlegs",) not in FIGURES:
        over = great_knight_cells()
        FIGURES[("greatlegs",)] = {xy: r for xy, r in compose([(scale2x(STAND), dict(LEG_ROLES, k="leather"), (0, 28),
                                                                True)]).items() if xy not in over}
    return FIGURES[("greatlegs",)]


def great_standard(p: Pix, x, y, night: bool, wools: tuple, frame: int, L: str):
    """The horseman's great gonfanon grown twice as he is, its pole's head at (x, y), flying back from it to the
    right at a moment of its wave, couched round a pixel wide, kept once a file at each moment."""
    k = -1 if night else 0
    key = ("greatstandard", wools, frame % 3, night)
    if key not in p.syms:
        own = {xy: r for xy, r in standard_cells(frame % 3).items() if r != "ink"}
        x0, y0 = min(x for x, _ in own), min(y for _, y in own)
        w, h = max(x for x, _ in own) - x0 + 1, max(y for _, y in own) - y0 + 1
        rows = ["".join(own.get((x0 + i, y0 + j), ".") for i in range(w)) for j in range(h)]
        grown = compose([(scale2x(rows), {"f": "f", "c": "c", "t": "t"}, (2 * x0, 2 * y0), True)])
        colours = {"ink": U_[1], "f": RAMP[wools[0]][4 + k], "c": RAMP[wools[1]][4 + k], "t": RAMP[wools[0]][3 + k]}
        p.symbol(key, {xy: colours[r] for xy, r in grown.items() if xy[0] > 0})
    p.use(key, x, y, L)


def great_horseman(p: Pix, x0, x1, g, night: bool, room: int, still: bool = True) -> bool:
    """The hero of a section's header, riding toward the title at the left, in the columns from x0 to x1 over the
    ground at row g, built to the `room` of rows free over it: the tall tree at the edge, and before it the great
    horseman (see `great_knight_cells`) on his horse standing with a forefoot raised, his face on the hand's lightest
    skin, his great gonfanon streaming back from the head of a pole as tall as the room allows and waving in a moving
    header; and a hound of his own size running ahead of him where the columns allow. Where the room is less than
    `GREAT_ROOM` rows, or the columns too few, the horseman of the knights' own size stands instead (see
    `horseman`). His shape is kept once a file; a drawing made lighter stitches him plain."""
    x = x1 - 26 - GREAT_W + 8                 # his horse's tail over the tree's trunk
    if room < GREAT_ROOM or x < x0:
        return horseman(p, x0, x1, g, night, room, still)
    k = -1 if night else 0
    tall_tree(p, x1 - 26, g, night, p.layer("tr", z=-0.7))
    top = g - GREAT_FOOT
    scheme = ("mustard", "olive", "terracotta", "terracotta", "mustard")
    fixed, wools = knight_fixed(night), knight_wools(night, *scheme, face=0)
    key = ("great", night) + (("plain",) if p.lite else ())
    wear(p, shape(p, key, mirrored(great_knight_cells(p.lite), GREAT_W), fixed), wools, x, top)
    wear(p, shape(p, ("greatlegs", night), mirrored(great_legs_cells(), GREAT_W), fixed), wools, x, top)
    pole = x + GREAT_W - 2 - 40               # the pole in his hand, two threads wide, its head as high as the room
    head = max(g - room + 2, top - 16 - 30)
    for yy in range(head + 1, top - 16):
        p.hline(pole, pole + 2, yy, U_[4] if not night else L_[2])
    p.hline(pole, pole + 2, head, S_[6 + k])
    for slot in range(1 if still else 3):
        great_standard(p, pole + 1, head + 1, night, ("terracotta", "mustard"), slot, wave_layer(p, slot, still))
    if x - 46 >= x0:
        great_hound(p, x - 46, g, night, "terracotta", "mustard")
    return True


def great_hound(p: Pix, x, g, night: bool, coat: str, collar: str, L="base"):
    """A hound of the hunt grown twice with the great horseman, running left before him with its paws on row g and
    its frame from column x, couched round a pixel wide, its eye a dark stitch in a white one; kept once a file."""
    k = -1 if night else 0
    key = ("greathound", coat, collar, night)
    if key not in p.syms:
        cells = compose([(scale2x([r[::-1] for r in HOUND_RUN]), {"b": "coat", "e": "ears", "c": "collar",
                                                                    "E": "eye"}, (0, 0), True)])
        eye = sorted(xy for xy, r in cells.items() if r == "eye")
        for xy in eye[1:]:
            cells[xy] = "coat"
        if eye:
            cells[(eye[0][0] + 1, eye[0][1])] = "white"
        C_ = RAMP[coat]
        colours = {"ink": U_[1], "coat": C_[4 + k], "ears": C_[2 + k], "collar": RAMP[collar][4 + k],
                   "eye": U_[1], "white": L_[6]}
        p.symbol(key, {xy: colours[r] for xy, r in cells.items()})
    p.use(key, x, g - 2 * len(HOUND_RUN) + 1, L)


def great_hound_cells() -> set:
    """Every pixel the great hound covers, its couching included, in its frame (see `great_hound`)."""
    if ("greathound",) not in FIGURES:
        FIGURES[("greathound",)] = set(compose([(scale2x([r[::-1] for r in HOUND_RUN]), {c: c for c in "becE"},
                                                 (0, 0), True)]))
    return FIGURES[("greathound",)]


# --------------------------------------------------------------------------- Harold grown twice
# The hero of a strip's header is Harold himself, on foot with his hawk on his fist as the tapestry shows him going
# down to Bosham, grown twice as the great horseman is (see `scale2x`), so that he stands the strip's height: bare
# headed, with the moustache the English wear, a cloak clasped at his throat and falling behind him to his knees, a
# belted tunic with a border at its hem, cross gartered hose and shoes, and his hawk on his raised fist before his
# face. He faces left, toward the words. h his hair, F his face, e his eye, u his moustache, c the clasp, K the cloak,
# t the tunic and his sleeve, d the belt, m the border, g his hand, s his hose, o his shoes; the hawk: b its body, l
# its breast, E its eye, k its beak and talons, w its wing.
HAROLD = [
    "..........hhhh......",
    ".........hhhhhh.....",
    "..bb.....FFhhhhh....",
    ".kEbb....eFhhhh.....",
    "..lbb...FFFFhhh.....",
    "..lbww..uuFFhh......",
    "..bwww...FFFcKK.....",
    "..www...tttttKKK....",
    "...k.ttttttttKKK....",
    "...gg...ttttttKKK...",
    "........ddddddKKK...",
    "........ttttttKKK...",
    ".......tttttttKKK...",
    ".......ttttttttKK...",
    ".......mmmmmmmmKK...",
    ".........ss.ss......",
    ".........ss.ss......",
    ".........ss.ss......",
    ".........ss.ss......",
    ".........ss.ss......",
    "........ooo.ooo.....",
]
HAROLD_ROLES = {"h": "hair", "F": "face", "e": "eye", "u": "moustache", "c": "clasp", "K": "cloak", "t": "tunic",
                "d": "belt", "m": "border", "g": "hand", "s": "hose", "o": "shoe", "b": "hawk", "l": "breast",
                "E": "glance", "k": "beak", "w": "wing"}
HAROLD_FOOT = 2 * len(HAROLD) - 1    # the row of his frame, grown, his shoes stand on


def great_harold_cells(plain: bool = False) -> dict:
    """The flat picture of Harold grown twice (see `HAROLD`), couched round a pixel wide: his eye and his hawk's set
    as an eye is, a dark stitch looking ahead with a white one behind it; the garters wound round his hose on the
    diagonal both ways; and the laid work of his tunic and his cloak on the diagonal every fourth thread, which
    `plain`, the fine texture a drawing made lighter goes without, leaves out."""
    key = ("harold", plain)
    if key not in FIGURES:
        cells = compose([(scale2x(HAROLD), HAROLD_ROLES, (0, 0), True)])
        for role in ("eye", "glance"):
            eye = sorted(xy for xy, r in cells.items() if r == role)
            for xy in eye:
                cells[xy] = "face" if role == "eye" else "hawk"
            cells[eye[0]] = "eye"
            cells[(eye[0][0] + 1, eye[0][1])] = "white"
        for (x, y), r in list(cells.items()):
            if r == "hose" and ((x + y) % 4 == 0 or (x - y) % 4 == 0):
                cells[(x, y)] = "garter"
            elif not plain and r in ("tunic", "cloak") and (x + y) % 4 == 0:
                cells[(x, y)] = r + "_laid"
        FIGURES[key] = cells
    return FIGURES[key]


def harold_fixed(night: bool) -> dict:
    """The colours Harold and his hawk wear: his hair and moustache, a cloak of woad clasped in gold over a tunic of
    terracotta with a mustard border, olive hose wound with umber garters; the hawk in umber with a pale breast and
    a mustard beak. His face and his hand are on the hand's skin (see `great_harold`)."""
    k = -1 if night else 0
    dark = U_[3] if night else U_[2]
    return {"ink": U_[1], "eye": U_[1], "white": L_[6], "hair": U_[4] if night else U_[3], "moustache": dark,
            "clasp": G_[4 + k], "cloak": W_[3 + k], "cloak_laid": W_[2 + k], "tunic": T_[4 + k],
            "tunic_laid": T_[3 + k], "belt": dark, "border": M_[4 + k], "hose": O_[3 + k],
            "garter": U_[4] if night else U_[3], "shoe": U_[2], "hawk": U_[5 + k], "breast": L_[5 + k],
            "wing": U_[4] if night else U_[3], "beak": M_[4 + k]}


def great_harold(p: Pix, x, g, night: bool, L="base"):
    """Harold grown twice (see `great_harold_cells`) with his frame from column x and his shoes on row g, his face
    and his hand on the hand's lightest skin; kept once a file, and stitched plain on a drawing made lighter."""
    key = ("harold", night) + (("plain",) if p.lite else ())
    face = skin(0, night)
    wear(p, shape(p, key, great_harold_cells(p.lite), harold_fixed(night)), {"face": face, "hand": face}, x,
         g - HAROLD_FOOT, L)


def tall_cells(height: int) -> set:
    """Every pixel the tall tree grown to `height` rows covers, its couching included, its roots on row 0."""
    if ("tall", height) not in FIGURES:
        rows = tall_rows(height)
        FIGURES[("tall", height)] = set(compose([(rows, {c: c for c in "12345"}, (0, 1 - len(rows)), True)]))
    return FIGURES[("tall", height)]


def clear_of(p: Pix, cells, x0: int, top: int) -> bool:
    """Whether `cells` lie two units clear of every word, taken a column at a time from the highest of each column's
    pixels to its lowest, and none of them left of column x0 or above row `top`."""
    cols: dict = {}
    for (x, y) in cells:
        lo, hi = cols.get(x, (y, y))
        cols[x] = (min(lo, y), max(hi, y))
    return all(x >= x0 and lo >= top and p.clear_of_words(x - 2, lo - 2, x + 3, hi + 3) for x, (lo, hi) in cols.items())


def placed(cells, x, y) -> set:
    """`cells` moved to (x, y)."""
    return {(x + dx, y + dy) for (dx, dy) in cells}


def great_hunt(p: Pix, x0, x1, g, night: bool, top: int) -> tuple | None:
    """The hunt as a strip's hero, standing on the ground at row g with its right end at column x1, ends excluded, in
    the columns from x0, no higher than row `top`, and two units clear of every word: at the right the tall tree,
    grown as tall as the rows allow (see `tall_rows`); Harold grown twice before it with his hawk on his fist, his
    cloak over the tree's lowest boughs (see `great_harold`); and his great hound running on ahead of him toward the
    words, its tail behind his heel. Where the columns are too few for all three the hound stays back, and then the
    tree; Harold always stands, or nothing does. Returns the columns it covers, from and to, or None."""
    harold = great_harold_cells()
    hw = max(x for x, _ in harold) + 1
    tx = x1 - 26                                  # the tree's frame, its couching to x1
    hound = great_hound_cells()
    tree = None
    for height in range(min(TALLEST, g - top), 37, -1):
        if clear_of(p, placed(tall_cells(height), tx, g), x0, top):
            tree = height
            break
    # Harold's frame, his cloak over the tree's lowest boughs, or over more of them where the columns are few
    for parts, x in ((("hound", "tree"), tx + 7 - hw), (("tree",), tx + 7 - hw), (("tree",), tx + 11 - hw),
                     ((), x1 - hw)):
        dx = x + 18 - max(c for c, _ in hound)    # the hound's frame, its tail behind his heel
        if "tree" in parts and tree is None:
            continue
        if not clear_of(p, placed(harold, x, g - HAROLD_FOOT), x0, top):
            continue
        if "hound" in parts and not clear_of(p, placed(hound, dx, g - 2 * len(HOUND_RUN) + 1), x0, top):
            continue
        if "tree" in parts:
            tall_tree(p, tx, g, night, p.layer("tr", z=-0.7), height=tree)
        if "hound" in parts:
            great_hound(p, dx, g, night, "terracotta", "mustard")
        great_harold(p, x, g, night)
        return (dx if "hound" in parts else x + 1, x1)
    return None


# --------------------------------------------------------------------------- small stitched things
KITE = [".11111.", "1111111", "1111111", ".11111.", ".11111.", "..111..", "...1..."]


def kite_shield(p: Pix, x, y, night: bool, wool: str = "terracotta", L="base", charge: bool = True):
    """A kite shield 7 by 7 with its top-left at (x, y), in `wool` with a cross of the other, couched round."""
    k = -1 if night else 0
    R = RAMP[wool]
    cells = stitch(p, x, y, KITE, {"1": R[3 + k]}, L, edge=U_[1])
    if charge:
        other = M_[4 + k] if wool != "mustard" else T_[3 + k]
        for yy in range(y + 1, y + 6):
            if (x + 3, yy) in cells:
                p.px(x + 3, yy, other, L)
        for xx in range(x + 1, x + 6):
            p.px(xx, y + 2, other, L)
    return cells


CROWN = ["1.1.1", "11111", "12121", ".111."]


def crown(p: Pix, x, y, night: bool, L="base", big: bool = False):
    """A crown stitched in gold, 5 by 4 (7 by 6 when big), two stones of madder on its band."""
    k = -1 if night else 0
    art = CROWN if not big else ["1..1..1", "11.1.11", "1111111", ".12121.", ".11111.", ".11111."]
    stitch(p, x, y, art, {"1": G_[4 + k], "2": RAMP["madder"][4]}, L, edge=U_[1])
    p.px(x, y + 1, G_[5 + k], L)


def knots_along(p: Pix, x0, x1, y, night: bool, seed=0, every=(24, 44), L="base"):
    """French knots along a rule, every so often, a cluster of three in two wools where no word lies near."""
    k = -1 if night else 0
    rnd = random.Random(seed * 31 + x0)
    x = x0 + rnd.randint(3, 9)
    while x < x1 - 4:
        if p.clear_of_words(x - 3, y - 5, x + 7, y + 3):
            p.px(x, y - 1, T_[4 + k], L)
            p.px(x + 1, y - 1, T_[3 + k], L)
            p.px(x + 2, y - 2, M_[4 + k], L)
            p.px(x + 3, y - 1, O_[4 + k], L)
        x += rnd.randint(*every)


HEART = [".55.55.", "5444445", "5443445", ".54345.", "..534..", "...5..."]


def heart(p: Pix, x, y, L="base"):
    """A heart stitched in terracotta, 7 by 6, a darker thread on its diagonal, couched round."""
    stitch(p, x, y, HEART, {"5": T_[4], "4": T_[3], "3": T_[2]}, L, edge=U_[1])


def wool_blocks(p: Pix, x0, y0, w, h, period=5, L="base"):
    """Blocks of terracotta and mustard wool by turns, the laid work's diagonal showing on each."""
    for yy in range(y0, y0 + h):
        for xx in range(x0, x0 + w):
            R = T_ if ((xx - x0) // period) % 2 == 0 else M_
            p.px(xx, yy, R[3] if (xx + yy) % 3 == 0 else R[4], L)


def whip_edge(p: Pix, x, y, w, h, night: bool, seed: int = 0, L="near"):
    """A patch's whip-stitched edge: slanting stitches of the edge's thread over every edge of the box from
    (x, y), `w` by `h`, each a short diagonal crossing the edge, bright where it catches the light. The
    stitches are pattern tiles laid over the patch, so a long label costs no more than a short one."""
    thread = G_[4] if night else T_[3]
    bright = G_[5] if night else T_[4]
    tag = "n" if night else "d"
    slant = tile(p, f"wh{tag}", 3, 3, {(0, 0): thread, (1, 1): bright, (2, 2): thread})
    filled(p, slant, x + 2, y - 1, w - 4, 3, L)
    filled(p, slant, x + 2, y + h - 2, w - 4, 3, L)
    left = tile(p, f"wl{tag}", 2, 3, {(0, 0): thread, (1, 1): thread})
    right = tile(p, f"wr{tag}", 2, 3, {(1, 0): thread, (0, 1): thread})
    filled(p, left, x, y + 2, 2, h - 4, L)
    filled(p, right, x + w - 2, y + 2, 2, h - 4, L)


# The link buttons' icons, 9 by 7, stitched bold enough to read at the kit's size: a kite shield, a crown,
# a hawk and a horse's head. Tones: 1 terracotta, 2 mustard, 3 olive, 4 blue grey, 5 umber, 6 cream, 7 gold,
# 8 steel, 9 the button's ink.
ICONS = {
    "shield": ["1111111..", "1121111..", "1222211..", "1121111..", ".11211...", "..1211...", "...11...."],
    "crown": ["7.7.7.7..", "77.7.7.77", "777777777", ".7777777.", ".7777777.", ".7..7..7.", "........."],
    "hawk": ["....33...", "...3363..", "..23333..", "...33333.", "...33333.", "....333..", "...2.2.3."],
    "horse": [".....11..", "...11111.", "..1611111", ".11111111", "1111.1111", "111...111", ".1....111"],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' wools on a patch: deep on the day linen, light on the night cloth."""
    k = -1 if not night else 1
    return {"1": T_[3 + k], "2": M_[4 + k], "3": O_[3 + k], "4": W_[3 + k], "5": U_[1], "6": L_[6],
            "7": G_[4 + k], "8": S_[4 + k], "9": ink}


NEEDLE = [".....8..", "....878.", "....8.8.", "...8.8..", "...888..", "..88....", ".88.....", "88......",
          "8......."]


def needle(p: Pix, x, y, night: bool, L="base"):
    """A needle laid on the cloth, 8 by 9 from (x, y), its eye at the top with the thread through it,
    trailing a loop of terracotta thread beside it."""
    k = -1 if night else 0
    pal = {"8": S_[5 + k], "7": T_[4 + k]}
    stitch(p, x, y, NEEDLE, pal, L)
    p.px(x, y, S_[6 + k], L)
    for (dx, dy) in ((6, 0), (7, 1), (8, 2), (8, 3), (8, 4), (7, 5), (6, 6), (5, 6), (4, 7), (3, 8), (2, 8)):
        p.px(x + dx, y + dy, T_[4 + k] if (dx + dy) % 2 else T_[3 + k], L)
    for (dx, dy) in ((9, 6), (10, 7), (11, 7), (12, 6)):
        p.px(x + dx, y + dy, T_[4 + k], L)


# --------------------------------------------------------------------------- the elements' stitches
def laid_tile(p: Pix, wool: str, night: bool) -> str:
    """The laid and couched work of a wool as a pattern tile 4 by 8: the laid threads on the diagonal, a light one
    and a dark one in every four, and a bar of dark couching stitches across them every eighth row."""
    R = RAMP[wool]
    k = -1 if night else 0
    cells = {}
    for y in range(8):
        for x in range(4):
            d = (x + y) % 4
            cells[(x, y)] = U_[1] if y == 5 and x % 2 else R[3 + k] if d == 0 else R[5 + k] if d == 2 else R[4 + k]
    return tile(p, f"lw{wool[:4]}{'n' if night else 'd'}", 4, 8, cells)


def column(p: Pix, x, base, w, v, night: bool, i: int = 0):
    """A week's commits as a column of laid and couched work standing on `base`, in its own layer over the chart's
    guides: the wool laid on the diagonal with its couching bars showing, a band of upright stitches in gold along
    its top, and a dark couched outline round it."""
    L = p.layer("hb", z=0.1)
    filled(p, laid_tile(p, WOOLS[i % len(WOOLS)], night), x, base - v, w, v, L)
    k = -1 if night else 0
    for xx in range(x, x + w):
        up = (xx - x) % 2 == 0
        p.px(xx, base - v, G_[5 + k] if up else U_[1], L)
        if v > 3:
            p.px(xx, base - v + 1, G_[4 + k] if up else G_[2 + k], L)
    p.box(x - 1, base - v - 1, w + 2, v + 2, U_[1], L)


def couched_thread(p: Pix, x0, x1, y, night: bool, L="base", knots: bool = True):
    """The timeline's cord: two laid threads of blue grey wool along rows y and y + 1, couched down every fourth
    pixel with a stitch of mustard across them, and a knot every so often."""
    k = -1 if night else 0
    for xx in range(x0, x1):
        tie = xx % 4 == 1
        p.px(xx, y, M_[4 + k] if tie else W_[4 + k], L)
        p.px(xx, y + 1, M_[3 + k] if tie else W_[3 + k], L)
        if tie:
            p.px(xx, y - 1, M_[4 + k], L)
            p.px(xx, y + 2, M_[3 + k], L)
    if knots:
        for xx in range(x0 + 13, x1 - 4, 26):
            thread_knot(p, xx, y, night, L)


def thread_knot(p: Pix, x, y, night: bool, L="base"):
    """A knot in a thread at (x, y): a thicker turn, lit on its upper left."""
    k = -1 if night else 0
    for (dx, dy, t) in ((0, -1, 5), (1, -1, 4), (-1, 0, 4), (0, 0, 4), (1, 0, 3), (2, 0, 3), (0, 1, 3), (1, 1, 2)):
        p.px(x + dx, y + dy, T_[max(0, t + k)], L)


# A release's gonfanon, hung from the timeline's cord: its head sewn over the cord, a square field of wool 9 wide
# with its device, and three tails tapering to points. h the head, f the field, d its device, t the tails.
GONFANONS = {
    "major": ["hhhhhhhhh", "fffffffff", "ffffdffff", "fffdddfff", "ffffdffff", "fffffffff", "ttt.ttt.t",
              "ttt.ttt.t", ".t...t...", ".t...t..."],
    "big": ["hhhhhhhhh", "ffffdffff", "ffffdffff", "ddddddddd", "ffffdffff", "ffffdffff", "ttt.ttt.t",
            "ttt.ttt.t", ".t...t...", ".t...t..."],
}


def gonfanon(p: Pix, x, y, wool: str, night: bool, kind: str = "major", L="base"):
    """A release as a gonfanon hung from the cord at row y and centred on column x, couched round: a plain field
    for a release, a field with a cross for a big one, and for one still to come its outline alone, its cloth not
    yet laid."""
    k = -1 if night else 0
    R = RAMP[wool]
    art = GONFANONS["big" if kind == "big" else "major"]
    if kind == "next":
        cells = {(x - 4 + i, y + j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."}
        for (cx, cy) in cells:
            if any((cx + dx, cy + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                p.px(cx, cy, R[3 + k], L)
        return
    pal = {"h": U_[2 + k] if not night else G_[3], "f": R[4 + k], "t": R[3 + k],
           "d": M_[4 + k] if wool != "mustard" else T_[3 + k]}
    stitch(p, x - 4, y, art, pal, L, edge=U_[1])


def small_comet(p: Pix, x, y, night: bool, L="base"):
    """A small stitched comet, 11 by 5, its star at the right end and its tail trailing left."""
    k = -1 if night else 0
    for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, G_[6], L)
    for (dx, dy) in ((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        p.px(x + dx, y + dy, G_[5 + k], L)
    for i in range(3, 10):
        p.px(x - i, y, G_[4 + k] if i % 2 else M_[4 + k], L)
        if i >= 5:
            p.px(x - i, y - 1, M_[4 + k], L)
            p.px(x - i, y + 1, M_[4 + k], L)


# A head and shoulders in profile as the embroiderers stitched a figure, 13 wide and 15 tall: hair cut
# straight across the brow, a round eye, a pointed nose, a tunic with a cloak over one shoulder clasped at
# the neck. 1 hair, 2 face, 3 eye, 4 tunic, 5 cloak, 6 clasp, 7 helm, 8 mail.
FIGURE = [
    "....1111.....", "...111111....", "..11111111...", "..11222222...", "..1223222....", "..122222.....",
    "..12222222...", "...22222.....", "....2222.....", ".....22......", "...4446444...", ".44445554444.",
    "4444455544444", "4444555544444", "4445555544444",
]
HELMED = [
    ".....7.......", "....777......", "...77777.....", "..7777777....", "..88722288...", "..8822322....",
    "..88222.8....", "..8822228....", "...88288.....", "....882......", "...8886888...", ".88888888888.",
    "8888888888888", "8888888888888", "8888888888888",
]
HAIRS = (U_[2], M_[3], U_[4], T_[2], U_[1])


def figure(p: Pix, cx, cy, i: int, night: bool, bot: bool = False, L="base"):
    """A contributor as a figure in profile centred on (cx, cy), in a tunic of one of the wools and a cloak
    of another by turns, their hair a colour of its own and their face on the hand's skins by turns; a bot wears a
    conical helm over a coif of mail."""
    k = -1 if night else 0
    tunic = RAMP[WOOLS[i % len(WOOLS)]]
    cloak = RAMP[WOOLS[(i + 2) % len(WOOLS)]]
    face = skin(i, night)
    if bot:
        pal = {"7": S_[4 + k], "8": W_[3 + k], "2": skin(1, night), "3": U_[1], "6": G_[4 + k]}
        stitch(p, cx - 6, cy - 7, HELMED, pal, L, edge=U_[1])
        p.px(cx - 2, cy - 7, S_[6 + k], L)
        return
    pal = {"1": HAIRS[i % len(HAIRS)], "2": face, "3": U_[1], "4": tunic[4 + k], "5": cloak[3 + k], "6": G_[4 + k]}
    stitch(p, cx - 6, cy - 7, FIGURE, pal, L, edge=U_[1])
    p.px(cx - 2, cy - 2, L_[6], L)           # the white of the round eye
    p.px(cx - 1, cy - 2, U_[1], L)


def roundel(p: Pix, cx, cy, r0, r1, night: bool, L="base"):
    """A stitched roundel round a seal's disc, from r0 to r1: a ring of terracotta wool with its laid
    work on the diagonal, edged in gold thread, and a point of gold at every sixteenth of the turn."""
    k = -1 if night else 0
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            if rho < r0 - 0.5 or rho > r1 + 0.5:
                continue
            if rho > r1 - 0.6 or rho < r0 + 0.4:
                p.px(x, y, G_[3 + k], L)
            else:
                th = math.atan2(dy, dx)
                spoke = abs(((th / (2 * math.pi)) * 16) % 1 - 0.5) < 0.1 and rho > r0 + 2
                p.px(x, y, M_[4 + k] if spoke else (T_[3 + k] if (x + y) % 3 else T_[2 + k]), L)
    for j in range(16):
        th = 2 * math.pi * j / 16
        x, y = cx + (r1 + 1.2) * math.cos(th), cy + (r1 + 1.2) * math.sin(th)
        p.px(math.floor(x), math.floor(y), G_[5 + k], L)


def patch_cell(q: Pix, ox, oy, night: bool):
    """A patch of linen 11 by 15 a counter's numeral is stitched on: the weave showing, whip-stitched round
    its edge in terracotta (gold by night)."""
    k = -1 if night else 0
    face, dot = (L_[5], L_[4]) if not night else (U_[2], U_[3])
    thread = T_[3] if not night else G_[4 + k]
    for yy in range(15):
        for xx in range(11):
            q.px(ox + xx, oy + yy, dot if (xx + yy) % 4 == 0 else face)
    for xx in range(0, 11, 2):
        q.px(ox + xx, oy, thread)
        q.px(ox + xx + 1 if xx < 10 else ox + xx, oy + 14, thread)
    for yy in range(1, 14, 2):
        q.px(ox, oy + yy, thread)
        q.px(ox + 10, oy + yy + 1 if yy < 13 else oy + yy, thread)


def card_panel(p: Pix, x, y, w, h, night: bool, body: str, fill: str, lid: bool, L="base"):
    """A schematic card as an embroidered panel: its icon's cell a square of terracotta wool with the icon turned
    to cream, the seam between the cell and the panel a braid of mustard and olive plaited down it, its edge whip
    stitched round with slanting stitches over the border, and a French knot on its lid."""
    k = -1 if night else 0
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + 10):
            c = p.get(xx, yy)
            if c == body:
                p.px(xx, yy, L_[6], L)
            elif c == fill or c is None:
                p.px(xx, yy, T_[3 + k] if (xx + yy) % 3 else T_[2 + k], L)
    for yy in range(y + 1, y + h - 1):
        t = (yy - y) % 4
        a, b = (M_[4 + k], O_[3 + k]) if t < 2 else (O_[3 + k], M_[4 + k])
        p.px(x + 10, yy, M_[5 + k] if t == 0 else a, L)
        p.px(x + 11, yy, O_[4 + k] if t == 2 else b, L)
        p.px(x + 12, yy, U_[1], L)
    whip_edge(p, x, y, w, h, night, L=p.layer("wh", z=0.2))
    if lid:
        p.px(x + w // 2, y - 2, T_[4 + k], L)
        p.px(x + w // 2 + 1, y - 2, T_[3 + k], L)
        p.px(x + w // 2, y - 3, M_[4 + k], L)


def couching(p: Pix, cells, night: bool, L="base"):
    """A wire as a couched cord in two wools: beside the laid thread of blue grey wool the layout draws, a second
    one a tone deeper, and every fourth pixel a stitch of mustard across both, a pixel proud of them on either
    side, so the couching shows."""
    k = -1 if night else 0
    run = cells[2:-4]
    for i, (x, y, d) in enumerate(run):
        dx, dy = (0, 1) if d == "h" else (1, 0)
        p.px(x + dx, y + dy, W_[2 + k], L)
        if i % 4 == 1:
            for j in (-1, 0, 1, 2):
                p.px(x + dx * j, y + dy * j, M_[4 + k] if j < 2 else M_[3 + k], L)


def banner_board(p: Pix, night: bool):
    """A placard as a cloth banner hung from a rod: the rod with its finials and the two loops the cloth
    hangs by, the linen below with its hems, and a long fringe along its foot."""
    p.cloth = (0, ROD, p.w, p.h, "pl", night)
    lay_cloth(p, foot=3)
    hems(p, night, 3)
    fringe(p, night, 3)
    rod(p, night)
    k = -1 if night else 0
    for cx in (14, p.w - 16):
        for yy in range(0, 4):
            p.px(cx, yy, T_[3 + k])
            p.px(cx + 1, yy, T_[2 + k])
    top_band(p, night)


# --------------------------------------------------------------------------- the lower border
LOW = 10   # the rows the lower border band rises over a header's stats rule: its upper rule, the beasts, the braid


def band_spans(p: Pix, x0, x1, rule) -> list:
    """How the lower border stands along a header's stats rule from x0 to x1, two units from every word: at its
    full height (2), the braid alone (1), or the rule alone (0). Returns [(a, b, level)]; a stretch of the full
    band too short to hold a beast between its ends is counted as braid."""
    def level(x):
        if p.clear_of_words(x - 2, rule - LOW - 2, x + 3, rule + 1):
            return 2
        return 1 if p.clear_of_words(x - 2, rule - 4, x + 3, rule + 1) else 0
    spans: list = []
    for x in range(x0, x1):
        lv = level(x)
        if spans and spans[-1][2] == lv:
            spans[-1][1] = x + 1
        else:
            spans.append([x, x + 1, lv])
    for s in spans:
        if s[2] == 2 and s[1] - s[0] < 22:
            s[2] = 1
    return [tuple(s) for s in spans]


def ground(spans, x0, x1, rule) -> int:
    """The row a scene standing between x0 and x1 has its feet on: the lower border's upper rule where the band
    stands at its full height under all of it, else the braid, else the rule."""
    levels = [lv for a, b, lv in spans if a < x1 and b > x0]
    low = min(levels) if levels else 0
    return rule - LOW - 1 if low == 2 else rule - 3 if low == 1 else rule - 1


def stretch(spans, level: int, x1: int):
    """The column a scene ending at column x1, ends excluded, may reach back to while the lower border stands at
    `level` under all of it (see `band_spans`): two columns in from where that run of the border begins, so the
    scene stands on it whole; None where the border stands otherwise under column x1 - 1."""
    start = None
    for a, b, lv in spans:
        start = (a if start is None else start) if lv == level else None
        if a <= x1 - 1 < b:
            return None if start is None else start + 2
    return None


def lower_band(p: Pix, x0, x1, rule, night: bool, seed: int = 0):
    """The lower border of the hanging over a header's stats rule, as the Bayeux border runs under its scenes: where
    the words leave it the room, an upper couched rule, a row of the border's beasts and knots, and the braid over
    the stats rule, which it couches in terracotta; where they come nearer, the braid alone, and nearer still the
    rule alone. Each stretch of the full band is closed at its ends by an upright of couched thread."""
    k = -1 if night else 0
    thread = U_[1] if not night else U_[0]
    for a, b, lv in band_spans(p, x0, x1, rule):
        if lv >= 1:
            braid(p, a, b, rule - 2, night)
        if lv == 2:
            couched(p, a, b, rule - LOW, T_[3 + k], thread)
            for x in (a, b - 1):
                for y in range(rule - LOW + 1, rule - 2):
                    p.px(x, y, thread if y % 3 == 0 else T_[3 + k])
            beasts_along(p, a + 2, b - 2, rule - LOW + 1, night, seed=seed)
    couched(p, x0, x1, rule, T_[3 + k], thread, p.layer("lb", z=0.05), phase=1)


# --------------------------------------------------------------------------- the headers' scenes
PERCH = 36    # the rows free over the ground the hawk needs to sit in the small tree's top
# The two knights of the charge: the wools of the horse, its mane, the saddle cloth, the shield and its device, and
# of the pennon's two tails.
FRONT = (("terracotta", "mustard", "olive", "mustard", "terracotta"), ("woad", "mustard"))
REAR = (("olive", "mustard", "terracotta", "terracotta", "mustard"), ("mustard", "terracotta"))


def charger_cells() -> set:
    """Every pixel a knight of the charge covers at any moment of his gallop and of his pennon's wave, his couching
    included, his frame's top left at (0, 0) (see `knight`)."""
    if ("charger",) not in FIGURES:
        cells = set(knight_cells("lance"))
        for frame in range(3):
            cells |= set(legs_cells(frame, "lance")) | {(37 + x, 1 + y) for (x, y) in pennon_cells(frame)}
        FIGURES[("charger",)] = cells
    return FIGURES[("charger",)]


def charge(p: Pix, x0, x1, g, night: bool, top: int, still: bool = True) -> bool:
    """The charge at the left of a sheet, riding right toward the shield wall, the knights' frames from column x0 to
    x1 - 40 with their hooves on row g, each two units clear of every word at every moment of his gallop and of his
    pennon's wave, and none higher than row `top`: the first as far right as he rides clear, and the second further
    back by 10 to 16 columns and higher by 20 to 26 rows, as far back and as high as he rides clear, so that the two
    overlap only at the edges, their lances level and their pennons flying. Where the second has no room the first
    rides alone, and where the first has none, nothing stands. In a moving header the horses gallop, a moment
    apart."""
    cells = charger_cells()
    front = next((x for x in range(x1 - 40, x0 - 1, -1) if clear_of(p, placed(cells, x, g - 24), x0, top)), None)
    if front is None:
        return False
    rear = next(((front - s, g - v) for v in range(26, 19, -1) for s in range(16, 9, -1)
                 if clear_of(p, placed(cells, front - s, g - v - 24), x0, top)), None)
    if rear:
        knight(p, *rear, night, REAR[0], p.layer("kr", z=-2), moving=not still, phase=1, colours=REAR[1], face=1)
    knight(p, front, g, night, FRONT[0], p.layer("kf", z=-1), moving=not still, colours=FRONT[1])
    return True


def tree_cells(height: int) -> set:
    """Every pixel the smaller tree cut to `height` rows covers, its couching included, its top row on row 0."""
    if ("tree", height) not in FIGURES:
        FIGURES[("tree", height)] = set(compose([(TREE[len(TREE) - height:], {c: c for c in "12345"}, (0, 0), True)]))
    return FIGURES[("tree", height)]


def wall_cells() -> set:
    """Every pixel the men of the shield wall and their shields cover, couching included, the first man's frame from
    (0, 0) (see `shield_wall`)."""
    if ("wall",) not in FIGURES:
        cells: set = set()
        for dx, *_ in WALL:
            cells |= placed(compose([(MAN, MAN_ROLES, (0, 0), True)]), dx, 0)
            cells |= placed(compose([(WALL_SHIELD, SHIELD_ROLES, (0, 0), True)]), dx - 1, 9)
        FIGURES[("wall",)] = cells
    return FIGURES[("wall",)]


def defenders(p: Pix, x0, x1, g, night: bool, top: int, rise: int = len(TALL)) -> bool:
    """The English at the right of a sheet facing the charge, standing on row g with the tree's edge at column x1,
    ends excluded, two units clear of every word, from column x0 and no higher than row `top`: at the edge the tall
    tree grown to `rise` rows, or as near it as the rows allow (see `tall_rows`), and where it has no room the smaller
    tree cut to the rows it has; and before it the shield wall where its men have the room, their spears at three
    angles where those have it too, else every spear held low. Where not even the smaller tree has ten rows, nothing
    stands."""
    Lt = p.layer("tr", z=-0.7)
    tall = next((h for h in range(min(TALLEST, rise, g - top), 37, -1)
                 if clear_of(p, placed(tall_cells(h), x1 - 26, g), x0, top)), None)
    if tall:
        tall_tree(p, x1 - 26, g, night, Lt, height=tall)
    else:
        small = next((h for h in range(len(TREE), 9, -1)
                      if clear_of(p, placed(tree_cells(h), x1 - 21, g + 1 - h), x0, top)), None)
        if small is None:
            return False
        tree(p, x1 - 21, g + 1, night, Lt, height=small)
    x, helms = x1 - 50, g - 21                    # the first man's frame, from his helm's point
    if clear_of(p, placed(wall_cells(), x, helms), x0, top):
        raised = all(y >= top and p.clear_of_words(sx - 3, y - 3, sx + 4, y + 4) for *_, (a, b), _ in WALL
                     for sx, y in line((x + a[0], helms + a[1]), (x + b[0], helms + b[1])))
        shield_wall(p, x, g, night, 40 if raised else 30)
    return True


# A hound of the hunt running right, 22 wide and 10 tall, longer legged than the border's: its ears laid back, a
# collar of another wool, its tail streaming. b its coat, e its ears, c the collar, E its eye.
HOUND_RUN = [
    "..................ee..", ".................eeb..", "b...............bbbbb.", ".bb...........ccbbbEbb",
    "..bbbbbbbbbbbbbcbbb...", "...bbbbbbbbbbbbbb.....", "..bbb.bbbbbbb..bb.....", ".bb....b....b....bb...",
    "bb.....b.....b....bb..", "b.....bb.....bb....b..",
]


def hound(p: Pix, x, g, night: bool, coat: str, collar: str, flip: bool = False, L="base"):
    """A hound of the hunt with its paws on row g and its frame from column x, running right (left when `flip`), in
    a coat of the ramp `coat` with a collar of `collar`."""
    k = -1 if night else 0
    C = RAMP[coat]
    pal = {"b": C[4 + k], "e": C[2 + k], "c": RAMP[collar][4 + k], "E": L_[6] if coat != "linen" else U_[1]}
    stitch(p, x, g - len(HOUND_RUN) + 1, HOUND_RUN, pal, L, flip=flip, edge=U_[1])


def charge_narrow(p: Pix, x0, x1, g, night: bool, room: int) -> bool:
    """A phone's charge: one knight at the gallop, held still, when the room allows him (33 rows, 40 columns), and
    with less a hound running on ahead of the charge (12 rows)."""
    if room >= 33 and x1 - x0 >= 40:
        knight(p, x1 - 40, g, night, FRONT[0], p.layer("kf", z=-1), colours=FRONT[1])
        return True
    if room >= 12 and x1 - x0 >= 26:
        hound(p, x1 - 25, g, night, "terracotta", "mustard")
        return True
    return False


def defenders_narrow(p: Pix, x0, x1, g, night: bool, room: int) -> bool:
    """A phone's defenders: the smaller tree cut to the room and, with 22 rows, a man of the wall before it."""
    if room < 10:
        return False
    tree(p, x1 - 21, g + 1, night, p.layer("tr", z=-0.7), height=min(len(TREE), room - 1), hawk=room >= PERCH)
    if room >= 22:
        guard = shape(p, ("wallshield", night), compose([(WALL_SHIELD, SHIELD_ROLES, (0, 0), True)]), man_fixed(night))
        k = -1 if night else 0
        man(p, x1 - 33, g - 21, night, "olive", 1, p.layer("wm2", z=-0.46))
        wear(p, guard, {"shield": RAMP["woad"][4 + k], "device": RAMP["mustard"][3 + k]}, x1 - 34, g - 12,
             p.layer("ws2", z=-0.45))
    return True


def bearer_narrow(p: Pix, x0, g, night: bool, room: int):
    """The right of a phone's section where its title leaves only 22 columns: a man of the wall holding the
    gonfanon on its pole, the pole as tall as the rows allow; under 18 rows a man alone, under 14 nothing."""
    if room < 14:
        return None
    man(p, x0, g - 21, night, "woad", 2)
    if room >= 18:
        banner(p, x0 + 10, g - min(room - 3, 32), g - 10, night, "terracotta", True)
    return (x0 - 1, x0 + 21)


def ride_narrow(p: Pix, x0, x1, g, night: bool, room: int) -> bool:
    """The horseman under a phone's words, riding left as the wide H2's does, in the columns from x0 to x1 over the
    ground at row g, built to the `room` of rows free over it: the smaller tree at the right, cut to the room; before
    it the horseman on his standing horse with his lance couched and its pennon flying, where the room allows him
    (33 rows, 38 columns); ahead of him his man bearing the gonfanon on its pole (see `bearer_narrow`); and a hound
    running on ahead, as the columns left allow. Under 14 rows nothing stands."""
    if room < 14 or x1 - x0 < 24:
        return False
    tree(p, x1 - 21, g + 1, night, p.layer("tr", z=-0.7), height=min(len(TREE), room - 1))
    ahead = x1 - 23
    if room >= 33 and ahead - x0 >= 38:
        knight(p, ahead - 37, g, night, ("mustard", "olive", "terracotta", "terracotta", "mustard"), "base",
               gait="stand", colours=("woad", "mustard"), flip=True)
        ahead -= 43
    if ahead - x0 >= 22:
        bearer_narrow(p, ahead - 21, g, night, room)
        ahead -= 25
    if ahead - x0 >= 24:
        hound(p, ahead - 22, g, night, "terracotta", "mustard", flip=True)
    return True


def hem_torch(p: Pix, g: int):
    """A torch of the hall in its bracket on a phone's right hem beside the scene under its words, by night, its
    foot clear of the lower border the scene stands on at row g and its light pooled on the scene; none where it
    would come within two units of a word."""
    x, y = p.w - TORCH_IN - 7, g - 19
    if p.clear_of_words(x - 2, y - 9, x + 12, y + 20):
        torch(p, x, y, True, phase=1, side=-1, pool=(56, 42))


def wheel(p: Pix, arc, night: bool, L="base"):
    """A dial's ring as the felloe of the wheel of fortune: a band of blue grey wool four pixels deep laid on the
    diagonal, a running stitch of gold round its rim and a dark couched line along its inner edge. Its spokes are
    laid at the end (see `spokes`), when the dial's figures are set and they can be kept clear of them."""
    k = -1 if night else 0
    (x0, y0), (x1, _) = arc[0], arc[-1]
    cx, cy = (x0 + x1) / 2, y0
    rho = (x1 - x0) / 2
    for y in range(math.floor(cy - rho) - 4, math.ceil(cy) + 2):
        for x in range(math.floor(cx - rho) - 4, math.ceil(cx + rho) + 4):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            if dy > 0.5:
                continue
            d = math.hypot(dx, dy)
            if d > rho + 2.1 or d < rho - 2.4:
                continue
            if d > rho + 1.2:
                dash = int(math.atan2(-dy, dx) * rho / 2) % 2
                c = G_[4 + k] if dash == 0 else U_[1]
            elif d < rho - 1.4:
                c = U_[1]
            else:
                c = W_[3 + k] if (x + y) % 3 else W_[2 + k]
            p.px(x, y, c, L)


def spokes(p: Pix, night: bool, avoid: str, L="base"):
    """The spokes of the wheel of fortune, laid once the dial's figures and its hand are set: six couched threads
    of umber and terracotta from the hub to the felloe, between the figures, each kept a pixel clear of every word
    and of the hand (pixels of colour `avoid`)."""
    cx, cy, r = p.dial
    base = p.layers["base"]
    for deg in (15, 45, 75, 105, 135, 165):
        a = math.radians(deg)
        for i in range(8, int(r - 4)):
            x, y = math.floor(cx + i * math.cos(a)), math.floor(cy - i * math.sin(a))
            if base.get((x, y)) == avoid or not p.clear_of_words(x - 1, y - 1, x + 2, y + 2):
                continue
            p.px(x, y, (U_[3] if i % 3 else T_[3]) if not night else (U_[5] if i % 3 else T_[3]), L)


HUB = [".111.", "12221", "12321", "12221", ".111."]


def hub(p: Pix, cx, cy, night: bool, L="base"):
    """A stitched roundel the hand turns on, 5 wide: a ring of terracotta round a stitch of cream."""
    k = -1 if night else 0
    stitch(p, cx - 2, cy - 2, HUB, {"1": T_[2 + k], "2": T_[4 + k], "3": L_[6]}, L)
