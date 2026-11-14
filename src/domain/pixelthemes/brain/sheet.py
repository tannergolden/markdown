# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The brain theme's sheet: the lab's wall, its frames, the lamps along the top of a header, its titles, the cables
along a header's rule, and the marks and link buttons beside them.

By day the wall is sage tiles in the light of the lamps, a little dust turning in it; the frame is steel riveted in
brass, with a bracket of brass at each top corner; caged lamps hang lit along the top; the titles are enamel, a
glint crossing them. By night the lamps are out: the wall is dark, sparks drift in it, the rivets glow, and the
titles are lit like the figures in a nixie tube."""
from __future__ import annotations

import random

from ...holidays.pixel import Paint, Pix, num
from ...holidays.pixel.type import FONTS, fold
from .kit import glow
from .palette import C, DAY_SKY, NIGHT_SKY, RAMP, X

FLUID, ENAMEL, BRASS, STEEL, NIXIE, ARC, TISSUE, SAGE, ROOM = (RAMP["fluid"], RAMP["enamel"], RAMP["brass"],
                                                              RAMP["steel"], RAMP["nixie"], RAMP["arc"],
                                                              RAMP["tissue"], RAMP["sage"], RAMP["room"])
GLINT = 11.0        # seconds between the glints that cross a title


# --------------------------------------------------------------------------- the wall
def band_edges(h: int, n: int) -> list:
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p"):
    """The wall a drawing sits on: sage tiles by day, deepening toward the floor; the dark of the room by night,
    each band laid into the next over two rows of checkerboard, the tiles' joints faint across it."""
    p.night, p.sheet = night, uid
    sky = NIGHT_SKY if night else DAY_SKY
    edges = band_edges(p.h, len(sky))
    for i, col in enumerate(sky):
        if edges[i + 1] > edges[i]:
            p.under.append(f'<rect y="{edges[i]}" width="{p.w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    for i in range(1, len(sky)):
        e = edges[i]
        if edges[i - 1] < e - 1 and e + 1 < edges[i + 1]:
            p.defs.append(f'<pattern id="{uid}k{i}" y="{e - 1}" width="2" height="2" patternUnits="userSpaceOnUse">'
                          f'<rect width="1" height="1" fill="{sky[i]}"/>'
                          f'<rect x="1" y="1" width="1" height="1" fill="{sky[i - 1]}"/></pattern>')
            p.under.append(f'<rect y="{e - 1}" width="{p.w}" height="2" fill="url(#{uid}k{i})"/>')
    # the tiles' joints: a course every eight rows, every other course set over by half a tile
    joint = SAGE[3] if not night else ROOM[4]
    p.defs.append(f'<pattern id="{uid}t" width="16" height="16" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{joint}" d="M0 .5h16M0 8.5h16M.5 0v8M8.5 8v8"/></pattern>')
    p.under.append(f'<rect width="{p.w}" height="{p.h}" fill="url(#{uid}t)" fill-opacity="{".28" if not night else ".5"}"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    sky = NIGHT_SKY if night else DAY_SKY
    edges = band_edges(p.h, len(sky))
    for i in range(len(sky)):
        if y < edges[i + 1]:
            return sky[i]
    return sky[-1]


def motes(p: Pix, x0, y0, x1, y1, n, night, seed=3, twinkling=True, faint=False, avoid=()):
    """What turns in the air: by day dust in the lamps' light, by night a spark or two off the coils. On a sheet of
    words, `faint`, only a dim speck of dust here and there, that no word is read through."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        if any(a - 2 <= x < c + 2 and b - 2 <= y < d + 2 for a, b, c, d in avoid):
            continue
        if faint:
            if i % 2 == 0:
                p.px(x, y, rnd.choice((ROOM[4], ROOM[5], ARC[1])) if night else SAGE[4], "haze")
            continue
        L = p.twinkle(i, back=True) if twinkling else "haze"
        if night:
            p.px(x, y, rnd.choice((ARC[5], NIXIE[4], FLUID[5], ARC[4])), L)
        else:
            p.px(x, y, rnd.choice((C["white"], BRASS[6], SAGE[6])), L)


def room_glow(p: Pix, cx, cy, rx, ry, colour=None):
    """The jar's light on the dark of the room by night."""
    p.halo(cx, cy, rx, ry, colour or FLUID[3], (0.04, 0.07, 0.11), L="haze", shape=True)


# --------------------------------------------------------------------------- the frames
def _tile(p: Pix, pid: str, w: int, h: int, cells: dict):
    by = {}
    for (x, y), c in cells.items():
        by.setdefault(c, []).append((x, y))
    rows = lambda pts: {y: [x for x, yy in pts if yy == y] for _, y in pts}
    body = "".join(f'<path stroke="{c}" d="{Pix._d(rows(pts))}"/>' for c, pts in sorted(by.items()))
    p.defs.append(f'<pattern id="{pid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{body}</pattern>')


def frame(p: Pix, night: bool, header=False, uid="fr"):
    """The sheet's border: a band of steel lit along its top and left and shaded along its foot and right, a row of
    rivets inside it, brass by day and glowing by night."""
    w, h = p.w, p.h
    S = STEEL
    if night:
        rects = [(0, 0, w, 1, S[0]), (0, h - 1, w, 1, S[0]), (0, 0, 1, h, S[0]), (w - 1, 0, 1, h, S[0]),
                 (1, 1, w - 2, 1, S[3]), (1, 1, 1, h - 2, S[2]), (1, h - 2, w - 2, 1, S[1]), (w - 2, 1, 1, h - 2, S[1])]
        rivet = {(0, 0): NIXIE[4], (1, 0): S[1], (2, 0): S[2], (3, 0): S[2], (4, 0): S[2], (5, 0): S[1]}
    else:
        rects = [(0, 0, w, 1, S[1]), (0, h - 1, w, 1, S[1]), (0, 0, 1, h, S[1]), (w - 1, 0, 1, h, S[1]),
                 (1, 1, w - 2, 1, S[5]), (1, 1, 1, h - 2, S[4]), (1, h - 2, w - 2, 1, S[3]), (w - 2, 1, 1, h - 2, S[3])]
        rivet = {(0, 0): BRASS[5], (1, 0): S[4], (2, 0): S[4], (3, 0): S[4], (4, 0): S[4], (5, 0): S[3]}
    _tile(p, f"{uid}h", 6, 1, rivet)
    _tile(p, f"{uid}v", 1, 6, {(0, x): c for (x, _), c in rivet.items()})
    out = [f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="{c}"/>' for x, y, rw, rh, c in rects]
    out += [f'<rect x="2" y="2" width="{w - 4}" height="1" fill="url(#{uid}h)"/>',
            f'<rect x="2" y="{h - 3}" width="{w - 4}" height="1" fill="url(#{uid}h)"/>',
            f'<rect x="2" y="3" width="1" height="{h - 6}" fill="url(#{uid}v)"/>',
            f'<rect x="{w - 3}" y="3" width="1" height="{h - 6}" fill="url(#{uid}v)"/>']
    p.shapes["base"].append("".join(out))
    if header:
        corners(p, night)


BRACKET = ["aaaaaaab", "ab.....c", "ab...cc.", "ab.cc...", "abc.....", "ab......", "ab......", "bc......"]


def corners(p: Pix, night: bool):
    """A header's top corners: a bracket of brass riveted across each."""
    pal = {"a": BRASS[5], "b": BRASS[3], "c": BRASS[2]} if not night else {"a": BRASS[3], "b": BRASS[1], "c": BRASS[0]}
    p.sprite(3, 3, BRACKET, pal)
    p.sprite(p.w - 3 - len(BRACKET[0]), 3, BRACKET, pal, flip=True)
    for x in (5, p.w - 6):
        p.px(x, 5, NIXIE[4] if night else BRASS[6])


# --------------------------------------------------------------------------- along the top
def festoon(p: Pix, x0, x1, y, night: bool, seed=0, sag=4, span=38, pixels=False):
    """What hangs along a header's top: a cable swagged between hooks of brass, a caged lamp at the foot of every
    swag, lit by day; by night the lamps are out but for a flicker now and then. One swag is drawn and hung as often
    as the top has room for; `pixels` lays each in pixels instead."""
    n = max(1, round((x1 - x0) / span))
    w = (x1 - x0) // n
    x0 += ((x1 - x0) - n * w) // 2
    key = ("swag", night, w, sag)
    if not pixels and key not in p.syms:
        p.symbol(key, swag(w, sag, night))
    cells = swag(w, sag, night) if pixels else {}
    for i in range(n):
        a = x0 + w * i
        if pixels:
            for (dx, dy), c in cells.items():
                p.px(a + dx, y + dy, c)
        else:
            p.use(key, a, y)
        lamp(p, a + w // 2, y + sag + 1, night, phase=i, pixels=pixels)
        if not night and not pixels and not p.lite:
            beam(p, a + w // 2, y + sag + 7, min(46, p.h - y - sag - 14))
        hook(p, a + w, y, night)
    hook(p, x0, y, night)


def beam(p: Pix, cx, y, length):
    """The lamp's light falling down the wall below it, a soft wedge fading as it spreads."""
    if length < 8:
        return
    spread = length * 0.42
    pts = f"{cx - 2},{y} {cx + 3},{y} {num(cx + 1 + spread)},{y + length} {num(cx + 1 - spread)},{y + length}"
    p.under.append(f'<polygon points="{pts}" fill="{BRASS[6]}" fill-opacity=".3"/>')


def shadow(p: Pix, x0, y0, x1, y1, night):
    """A machine's shadow on the wall behind it, cast down and to the right by the lamps; by night none."""
    if night:
        return
    p.under.append(f'<rect x="{x0 + 3}" y="{y0 + 3}" width="{x1 - x0}" height="{y1 - y0 - 3}" fill="{X["shade_ink"]}" '
                   f'fill-opacity=".07"/>')


def swag(w: int, sag: int, night: bool) -> dict:
    cells = {}
    for x in range(1, w):
        t = x / w
        yy = round(sag * (1 - (2 * t - 1) ** 2))
        cells[(x, yy)] = STEEL[1] if not night else ROOM[0]
        if not night:
            cells[(x, yy - 1)] = cells.get((x, yy - 1), STEEL[3]) if x % 3 else STEEL[3]
    return cells


def hook(p: Pix, x, y, night):
    p.px(x, y, BRASS[5] if not night else BRASS[2])
    p.px(x - 1, y, BRASS[3] if not night else BRASS[1])
    p.px(x + 1, y, BRASS[2] if not night else BRASS[0])


LAMP = ["..a..", ".bbb.", "c#c#c", "#ded#", "cdedc", "#ded#", ".c#c."]


def lamp(p: Pix, cx, y, night, phase=0, pixels=False):
    """A caged lamp: a cap of brass, a cage of wire, and its bulb, lit by day and dark by night."""
    if night:
        pal = {"a": BRASS[2], "b": BRASS[1], "c": STEEL[2], "#": STEEL[1], "d": ROOM[3], "e": ROOM[4]}
    else:
        pal = {"a": BRASS[4], "b": BRASS[3], "c": STEEL[3], "#": STEEL[2], "d": BRASS[6], "e": C["white"]}
    if pixels:
        p.sprite(cx - 2, y, LAMP, pal)
    else:
        key = ("lamp", night)
        if key not in p.syms:
            p.symbol(key, {(i - 2, j): pal[ch] for j, r in enumerate(LAMP) for i, ch in enumerate(r) if ch in pal})
        p.use(key, cx, y)
    if night and not pixels and phase % 3 == 1 and not p.lite:
        L = p.seq(f"lampfl{phase}", 0.6 + 0.05 * (phase % 2), 0.66 + 0.05 * (phase % 2), 6.0, z=11)
        for dx, dy in ((0, 3), (0, 4), (0, 5), (-1, 4), (1, 4)):
            p.px(cx + dx, y + dy, NIXIE[5] if (dx, dy) != (0, 4) else NIXIE[6], L)
    elif not night:
        p.px(cx, y + 4, C["white"], p.twinkle(phase) if not p.lite else "base")


# --------------------------------------------------------------------------- the titles
def _enamel(r, c, scale, night):
    """Letters of enamel by day, a colour for each row of the face: lit at the top, deepening to the foot."""
    band = min(6, r // scale)
    return TISSUE[(5, 4, 4, 3, 3, 2, 2)[band]]


def _nixie(r, c, scale, night):
    """Letters of nixie light by night: white-hot at the heart of the stroke's top, amber through its body."""
    band = min(6, r // scale)
    return NIXIE[(6, 5, 5, 5, 4, 4, 4)[band]]


ENAMEL_PAINT = Paint("enamel", _enamel)
NIXIE_PAINT = Paint("nixie", _nixie)


def title(p: Pix, x, y, s, night: bool, scale: int, motion: bool) -> int:
    """A title as the set letters it. By day in the brain's own crimson enamel, edged in the darkest of the machines'
    paint, lit down its left edges and shaded along its foot; by night in the amber of a nixie tube, glowing. In a
    wide moving header a glint crosses it every `GLINT` seconds."""
    edge_c = X["title_day"] if not night else NIXIE[0]
    edge = {"shadow": edge_c} if p.lite else {"outline": edge_c}
    if not night:
        w = p.text(x, y, s, X["title_day"], "57", scale, paint=ENAMEL_PAINT, bevel=(TISSUE[6], TISSUE[1]),
                   glow=(TISSUE[5], (0.22,)), night=False, **edge)
    else:
        w = p.text(x, y, s, X["title_night"], "57", scale, paint=NIXIE_PAINT, glow=(NIXIE[3], (0.32,)),
                   night=True, **edge)
    if motion and scale >= 2 and not p.lite:
        glint(p, x, y, s, scale, w)
    return w


def glint(p: Pix, x, y, s, scale, w):
    glyphs, _, space = FONTS["57"]
    uses, cx = [], x
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        key = ("glyph", "57", ch)
        uses.append(f'<use href="#{p.syms[key]}" transform="translate({num(cx)} {num(y)}) scale({scale})"/>')
        cx += (glyphs[ch][0] + 1) * scale
    h = 7 * scale
    band = 2 * scale
    cid = f"gl{len(p.raws)}"
    a, b = x - band - h, x + w + band
    poly = f"0 {y + h + 1} {band} {y + h + 1} {band + h} {y - 1} {h} {y - 1}"
    moving = (f'<clipPath id="{cid}"><polygon points="{poly}"><animateTransform attributeName="transform" '
              f'type="translate" values="{a} 0;{b} 0;{b} 0" keyTimes="0;.3;1" dur="{num(GLINT)}s" '
              f'repeatCount="indefinite"/></polygon></clipPath><g clip-path="url(#{cid})" stroke="{C["white"]}" '
              f'stroke-opacity=".8">{"".join(uses)}</g>')
    p.raw(0.4, moving, "")


# --------------------------------------------------------------------------- the marks
FLASK = ["..##...", "..##...", "..##...", ".#..#..", "#oooo#.", "#oOoo#.", ".####.."]


def section_mark(p: Pix, x, y, night):
    """After SECTION A-A: a flask of the jar's fluid."""
    p.sprite(x, y - 1, FLASK, {"#": STEEL[4] if not night else STEEL[3], "o": FLUID[4] if not night else FLUID[5],
                               "O": C["white"] if not night else FLUID[6]})


BOLT = ["....oooo", "...owwvo", "...owvo.", "..owvo..", "..owvooo", ".owwwwvo", ".ooovwo.", "...owo..",
        "..owo...", "..oo....", ".oo....."]


def strip_mark(p: Pix, x, y, night):
    """Beside an H3's title: a bolt off the coil, white in an edge of violet, a spark jumping off it; by night it
    glows, flickering."""
    if night:
        glow(p, x + 4, y + 0.5, 5.5, 7.0, ARC[4], (0.08, 0.16), L=p.flicker(1, back=True))
    p.sprite(x, y - 5, BOLT, {"o": ARC[1] if night else ARC[2], "w": ARC[6] if night else C["white"], "v": ARC[4]})
    p.px(x + 9, y - 6, ARC[5] if night else ARC[3], p.twinkle(2))


# --------------------------------------------------------------------------- along the rule
def cables(p: Pix, x0, x1, y, night, seed=0):
    """Cables lying along a header's rule where nothing stands on it: a black one and a red one, crossing now and
    then, clipped to the floor."""
    rnd = random.Random(seed * 31 + x0)
    a, b = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
    import math
    for x in range(x0, x1):
        ya = y - 1 - (1 if math.sin(x / 9 + a) > 0.3 else 0)
        yb = y - 1 - (1 if math.sin(x / 11 + b) > 0.1 else 0)
        p.px(x, yb, TISSUE[2] if not night else TISSUE[1])
        p.px(x, ya, STEEL[1] if not night else ROOM[0])
        if ya == y - 2:
            p.px(x, ya - 1, STEEL[3] if not night else STEEL[1])
        if x % 37 == 0:
            p.px(x, y - 1, BRASS[4] if not night else BRASS[1])


# --------------------------------------------------------------------------- the link buttons
def link_top(p: Pix, x0, x1, y, seed, night):
    """Along a link button's top: rivets, brass by day and glowing by night."""
    for x in range(x0, x1):
        p.px(x, y, (BRASS[5] if not night else NIXIE[4]) if x % 6 == 0 else (STEEL[4] if not night else STEEL[2]))


ICONS = {
    "brain": ["..###..", ".#aba#.", "#abaab#", "#babab#", ".#####.", "...#.#.", "...#..."],
    "flask": ["..#.#..", "..#.#..", ".#...#.", "#.....#", "#aaaaa#", "#abaaa#", ".#####."],
    "bolt": ["...###.", "..##...", ".####..", "...##..", "..##...", ".##....", ".#....."],
    "gear": ["..#.#..", ".#####.", "##.#.##", ".#...#.", "##.#.##", ".#####.", "..#.#.."],
}
ORDER = ("brain", "flask", "bolt", "gear")


def icon(index: int, night: bool) -> tuple:
    """The sprite at the start of the `index`-th link button: the brain, a flask, a bolt and a gear by turns."""
    name = ORDER[index % len(ORDER)]
    if night:
        pal = {"#": {"brain": TISSUE[4], "flask": STEEL[5], "bolt": ARC[5], "gear": NIXIE[4]}[name],
               "a": FLUID[5] if name == "flask" else TISSUE[5], "b": FLUID[6] if name == "flask" else TISSUE[3]}
    else:
        pal = {"#": {"brain": TISSUE[1], "flask": STEEL[2], "bolt": ARC[3], "gear": ENAMEL[3]}[name],
               "a": FLUID[4] if name == "flask" else TISSUE[4], "b": C["white"] if name == "flask" else TISSUE[5]}
    return ICONS[name], pal
