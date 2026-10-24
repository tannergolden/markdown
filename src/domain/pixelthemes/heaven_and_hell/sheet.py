# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Heaven & Hell theme's sheet: its two skies, its frames, what hangs along the top of a header, its titles,
what lies along a header's rule, and the marks and link buttons beside them.

By day the sheet is heaven: a deep azure warming to gold over the clouds, each band of the sky laid into the next
over two rows of checkerboard, heaven's light falling through it in shafts from the upper left, a gilt frame strung
with pearls and a festoon of pearls along the top hung with gold stars. By night it is hell: black smoke reddening
to a crimson horizon over the fires below, embers rising through it, a frame of iron studded red-hot and a chain
along the top hung with flames."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import Paint, Pix, num
from ...holidays.pixel.type import FONTS, fold
from .kit import ellipse, glow
from .palette import C, DAY_SKY, NIGHT_SKY, RAMP, X

GOLD, PEARL, CLOUD, LINEN, STEEL, AZURE = (RAMP["gold"], RAMP["pearl"], RAMP["cloud"], RAMP["linen"], RAMP["steel"],
                                           RAMP["azure"])
LAVA, FIRE, IRON, BASALT, SMOKE = RAMP["lava"], RAMP["fire"], RAMP["iron"], RAMP["basalt"], RAMP["smoke"]
HIDE, HORN, BONE = RAMP["hide"], RAMP["horn"], RAMP["bone"]
GLINT = 12.0        # seconds between the glints that cross a gilt title


# --------------------------------------------------------------------------- the skies
def band_edges(h: int, n: int) -> list:
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p"):
    """The ground a drawing sits on: heaven's sky by day, from a pale celestial blue at the top through pearl to
    the warm gold of the light over the clouds; hell's by night, black smoke reddening toward the fires. The
    drawing keeps whether it is night, for the parts the kit hands no `night`."""
    p.night, p.sheet = night, uid
    sky = NIGHT_SKY if night else DAY_SKY
    edges = band_edges(p.h, len(sky))
    for i, col in enumerate(sky):
        if edges[i + 1] > edges[i]:
            p.under.append(f'<rect y="{edges[i]}" width="{p.w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    # each band laid into the next over two rows of checkerboard, as a pixel artist blends a sky
    for i in range(1, len(sky)):
        e = edges[i]
        if edges[i - 1] < e - 1 and e + 1 < edges[i + 1]:
            p.defs.append(f'<pattern id="{uid}k{i}" y="{e - 1}" width="2" height="2" patternUnits="userSpaceOnUse">'
                          f'<rect width="1" height="1" fill="{sky[i]}"/>'
                          f'<rect x="1" y="1" width="1" height="1" fill="{sky[i - 1]}"/></pattern>')
            p.under.append(f'<rect y="{e - 1}" width="{p.w}" height="2" fill="url(#{uid}k{i})"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    sky = NIGHT_SKY if night else DAY_SKY
    edges = band_edges(p.h, len(sky))
    for i in range(len(sky)):
        if y < edges[i + 1]:
            return sky[i]
    return sky[-1]


def rays(p: Pix, ox=-30.0, oy=-70.0, seed=1, n=7):
    """Heaven's light falling through the sky in shafts from the upper left, where the lamp is: long wedges of
    pale light fanning out over the sheet, each a little brighter at its heart, calm behind every word."""
    rnd = random.Random(seed)
    out = []
    a0, a1 = math.radians(28), math.radians(68)
    for i in range(n):
        a = a0 + (a1 - a0) * (i + rnd.uniform(0.15, 0.85)) / n
        spread = math.radians(rnd.uniform(1.6, 3.4))
        far = 900
        pts = [(ox, oy)]
        for b in (a - spread, a + spread):
            pts.append((ox + far * math.cos(b), oy + far * math.sin(b)))
        out.append(f'<polygon points="{" ".join(f"{num(x)},{num(y)}" for x, y in pts)}" '
                   f'fill-opacity="{num(rnd.uniform(0.28, 0.42))}"/>')
        if not p.lite and rnd.random() < 0.6:
            core = spread * 0.38
            pts = [(ox, oy)] + [(ox + far * math.cos(b), oy + far * math.sin(b)) for b in (a - core, a + core)]
            out.append(f'<polygon points="{" ".join(f"{num(x)},{num(y)}" for x, y in pts)}" fill-opacity=".3"/>')
    p.under.append(f'<g fill="{X["ray"]}">{"".join(out)}</g>')


def sparkle(p: Pix, x, y, big=False, L="base", warm=True):
    """A four-point glint of light: a white heart and arms that fade."""
    arm = GOLD[5] if warm else PEARL[5]
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.55", L)


def glints(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, avoid=()):
    """Heaven's sky by day: a few points of light, gold and white, kept out of the boxes in `avoid`."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        if any(a - 2 <= x < c + 2 and b - 2 <= y < d + 2 for a, b, c, d in avoid):
            continue
        L = p.twinkle(i, back=True) if twinkling else "haze"
        if rnd.random() < 0.45:
            sparkle(p, x, y, big=rnd.random() < 0.35, L=L, warm=rnd.random() < 0.7)
        else:
            p.px(x, y, rnd.choice((C["white"], GOLD[6], GOLD[5])), L)


def embers(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """Hell's sky by night: embers, sparks and ash, more of them low over the fires, kept out of `avoid`."""
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.randrange(x0, x1)
        y = y0 + int((y1 - y0) * (1 - rnd.random() ** 1.6))
        if any(a - 1 <= x < c + 1 and b - 1 <= y < d + 1 for a, b, c, d in avoid):
            continue
        k = rnd.random()
        if faint or k < 0.45:
            p.px(x, y, rnd.choice((LAVA[1], LAVA[2], SMOKE[3])), "haze")
        elif k < 0.9:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.6) else "haze"
            p.px(x, y, rnd.choice((LAVA[4], FIRE[4], FIRE[5], LAVA[5])), L)
        else:
            L = p.twinkle(i, back=True) if twinkling else "haze"
            p.px(x, y, FIRE[6], L)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(x + dx, y + dy, LAVA[4] + ":0.6", L)


def rising(p: Pix, x0, x1, y0, y1, n, seed=5, dur=6.0):
    """Sparks rising from the fires on loops of their own, each a step at a time, swaying as they climb: the night's
    slow ambient motion. The still file leaves each where its climb begins."""
    rnd = random.Random(seed)
    for i in range(n):
        key = ("spark", i % 3)
        if key not in p.syms:
            col = (FIRE[5], LAVA[5], FIRE[6])[i % 3]
            p.symbol(key, {(0, 0): col, (0, 1): LAVA[3] + ":0.6"})
        x = rnd.randrange(x0, x1)
        path = []
        steps = rnd.randint(14, 18)
        phase = rnd.uniform(0, 6.3)
        for s in range(steps):
            f = s / (steps - 1)
            path.append((x + round(2.2 * math.sin(phase + f * 7.5)), round(y1 - (y1 - y0) * f)))
        p.fly([key], path, dur * rnd.uniform(0.8, 1.25), z=9, flap=60)


def heat(p: Pix, y0, y1, x0=4, x1=None):
    """The red of the fires below thrown up the night sky: a wash that deepens toward the foot, under everything."""
    x1 = p.w - 4 if x1 is None else x1
    n = 4
    for i in range(n):
        top = y0 + (y1 - y0) * i // n
        p.under.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{y1 - top}" fill="{X["heat"]}" '
                       f'fill-opacity=".045"/>')


# --------------------------------------------------------------------------- the frames
def _tile(p: Pix, pid: str, w: int, h: int, cells: dict):
    by = {}
    for (x, y), c in cells.items():
        by.setdefault(c, []).append((x, y))
    body = "".join(f'<path stroke="{c}" d="{Pix._d(_rows(pts))}"/>' for c, pts in sorted(by.items()))
    p.defs.append(f'<pattern id="{pid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{body}</pattern>')


def _rows(pts):
    rows = {}
    for x, y in pts:
        rows.setdefault(y, []).append(x)
    return rows


def frame(p: Pix, night: bool, header=False, uid="fr"):
    """The sheet's border. By day a moulding of gilt two units deep, lit along its top and left and shaded along
    its foot and right, with a string of pearls inside it. By night a band of black iron, its rivets red-hot, and
    inside it a line of the fire's glow."""
    w, h = p.w, p.h
    rects = []
    if not night:
        rects += [(0, 0, w, 1, GOLD[1]), (0, h - 1, w, 1, GOLD[1]), (0, 0, 1, h, GOLD[1]), (w - 1, 0, 1, h, GOLD[1]),
                  (1, 1, w - 2, 1, GOLD[5]), (1, 1, 1, h - 2, GOLD[4]), (1, h - 2, w - 2, 1, GOLD[2]),
                  (w - 2, 1, 1, h - 2, GOLD[2])]
        _tile(p, f"{uid}h", 3, 1, {(0, 0): PEARL[6], (1, 0): PEARL[3]})
        _tile(p, f"{uid}v", 1, 3, {(0, 0): PEARL[6], (0, 1): PEARL[3]})
    else:
        rects += [(0, 0, w, 1, IRON[0]), (0, h - 1, w, 1, IRON[0]), (0, 0, 1, h, IRON[0]), (w - 1, 0, 1, h, IRON[0]),
                  (1, 1, w - 2, 1, IRON[4]), (1, 1, 1, h - 2, IRON[3]), (1, h - 2, w - 2, 1, IRON[1]),
                  (w - 2, 1, 1, h - 2, IRON[1])]
        _tile(p, f"{uid}h", 6, 1, {(0, 0): LAVA[4], (1, 0): LAVA[2], (2, 0): LAVA[1], (3, 0): LAVA[1],
                                    (4, 0): LAVA[1], (5, 0): LAVA[2]})
        _tile(p, f"{uid}v", 1, 6, {(0, 0): LAVA[4], (0, 1): LAVA[2], (0, 2): LAVA[1], (0, 3): LAVA[1],
                                    (0, 4): LAVA[1], (0, 5): LAVA[2]})
    out = [f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="{c}"/>' for x, y, rw, rh, c in rects]
    out += [f'<rect x="3" y="3" width="{w - 6}" height="1" fill="url(#{uid}h)"/>',
            f'<rect x="3" y="{h - 4}" width="{w - 6}" height="1" fill="url(#{uid}h)"/>',
            f'<rect x="3" y="4" width="1" height="{h - 8}" fill="url(#{uid}v)"/>',
            f'<rect x="{w - 4}" y="4" width="1" height="{h - 8}" fill="url(#{uid}v)"/>']
    p.shapes["base"].append("".join(out))
    if night:
        for (x, y) in _rivets(w, h):
            p.px(x, y, FIRE[5])
            p.px(x + 1, y, LAVA[4])
            p.px(x, y + 1, LAVA[3])
            p.px(x + 1, y + 1, LAVA[2])
    else:
        for (x, y) in _rivets(w, h):
            p.px(x, y, GOLD[6])
            p.px(x + 1, y, GOLD[4])
            p.px(x, y + 1, GOLD[4])
            p.px(x + 1, y + 1, GOLD[2])
    if header:
        corners(p, night)


def _rivets(w, h):
    """The studs set into a frame's corners."""
    return ((1, 1), (w - 3, 1), (1, h - 3), (w - 3, h - 3))


WING_CORNER = [
    "#aaaaaaaaaaa.....",
    "abbbbbbbbbbbaa...",
    "abccbccbccbbbba..",
    ".bc.dc.dc.dcbbba.",
    "..d..d..d.ddcbbd.",
    "..........d.dcd..",
    "............d....",
]
HORN_CORNER = [
    "####...........",
    "#oo##..........",
    "#...o#.........",
    ".....o#........",
    "......o#.......",
    ".......o#......",
]


def corners(p: Pix, night: bool):
    """A header's top corners: by day a gilt wing spreading along the frame from each, by night a horn curling
    out of each, as the frame's iron grows them."""
    art = HORN_CORNER if night else WING_CORNER
    if night:
        pal = {"#": RAMP["horn"][4], "o": RAMP["horn"][2]}
    else:
        pal = {"#": C["white"], "a": GOLD[5], "b": GOLD[4], "c": GOLD[6], "d": GOLD[2]}
    p.sprite(4, 4, art, pal)
    p.sprite(p.w - 4 - len(art[0]), 4, art, pal, flip=True)


# --------------------------------------------------------------------------- along the top
def festoon(p: Pix, x0, x1, y, night: bool, seed=0, sag=4, span=38, pixels=False):
    """What hangs along a header's top. By day a festoon of pearls swagged between gilt studs, a gold star
    hanging at the foot of every swag and twinkling. By night an iron chain swagged between red-hot studs, a flame
    burning in a little cage at the foot of every swag. Every swag is the same, so one is drawn and hung as often
    as the top has room for; `pixels` lays each in pixels instead, under whatever is drawn over it later, as a
    placard's tags are."""
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
        cx = a + w // 2
        foot = y + sag + 1
        if night:
            caged_flame(p, cx, foot, phase=i, pixels=pixels)
        else:
            hanging_star(p, cx, foot, phase=i, pixels=pixels)
        stud(p, a + w, y, night)
    stud(p, x0, y, night)


def swag(w: int, sag: int, night: bool) -> dict:
    """One swag of the festoon, `w` wide and sagging `sag` rows, from the stud at its left: pearls on a gold cord
    by day, the links of an iron chain by night."""
    cells = {}
    for x in range(1, w):
        t = x / w
        yy = round(sag * (1 - (2 * t - 1) ** 2))
        if night:
            if (x // 2) % 2:
                cells[(x, yy)] = IRON[4]
                cells[(x, yy + 1)] = IRON[2]
            else:
                cells[(x, yy)] = IRON[5]
                cells[(x, yy - 1)] = IRON[3]
                cells[(x, yy + 1)] = IRON[1]
        else:
            bead = x % 3
            if bead == 0:
                cells[(x, yy)] = GOLD[4]                     # the gold cord between the pearls
            else:
                cells[(x, yy)] = C["white"] if bead == 1 else PEARL[4]
                cells[(x, yy + 1)] = PEARL[3] if bead == 1 else PEARL[1]
                cells.setdefault((x, yy - 1), PEARL[5] if bead == 1 else PEARL[3])
    return cells


def stud(p: Pix, x, y, night):
    if night:
        p.px(x, y, LAVA[4])
        p.px(x - 1, y, IRON[3])
        p.px(x + 1, y, IRON[2])
    else:
        p.px(x, y, GOLD[6])
        p.px(x - 1, y, GOLD[4])
        p.px(x + 1, y, GOLD[2])


HUNG_STAR = ["...o...", "...a...", "..aac..", "abbbbcd", ".bbbcd.", ".bc.cd.", "b.....d"]


def hanging_star(p: Pix, cx, y, phase=0, pixels=False):
    """A little gold star hung on a thread, lit on its upper left, its heart twinkling: drawn once, hung often, or
    laid in pixels."""
    pal = {"o": GOLD[3], "a": GOLD[6], "b": GOLD[5], "c": GOLD[4], "d": GOLD[2]}
    if pixels:
        p.sprite(cx - 3, y, HUNG_STAR, pal)
    else:
        key = ("star",)
        if key not in p.syms:
            p.symbol(key, {(i - 3, j): pal[ch] for j, r in enumerate(HUNG_STAR) for i, ch in enumerate(r)
                           if ch in pal})
        p.use(key, cx, y)
    p.px(cx, y + 3, C["white"], p.twinkle(phase))


def caged_flame(p: Pix, cx, y, phase=0, pixels=False):
    """A little iron cage hung on a chain, a flame in it that flickers: drawn once a phase, hung often, or laid in
    pixels."""
    ph = phase % 3
    if pixels:
        cage(p, cx, y, ph)
    else:
        p.stamp(("cage", ph), lambda q, ox, oy: cage(q, ox, oy, ph), cx, y, pad=8)


def cage(q: Pix, ox, oy, ph):
    q.px(ox, oy, IRON[3])
    q.sprite(ox - 2, oy + 1, ["#.#.#", "#...#", "#...#", ".###."], {"#": IRON[4]})
    L = q.flicker(ph)
    for dx, dy, c in ((0, 3, FIRE[6]), (0, 2, FIRE[5]), (-1, 3, FIRE[4]), (1, 3, FIRE[4]), (0, 1, FIRE[3]),
                      (0, 0, LAVA[4])):
        q.px(ox + dx, oy + 1 + dy, c, L)
    for (qx, qy) in ((ox - 2, oy + 2), (ox + 2, oy + 2)):
        q.px(qx, qy, LAVA[4] + ":0.3", L)


# --------------------------------------------------------------------------- the titles
def _gilt(r, c, scale, night):
    """Gilt letters, a colour for each row of the face: pale gold catching the light at the top, deepening to old
    gold at the foot."""
    band = min(6, r // scale)
    return GOLD[(6, 5, 5, 4, 4, 3, 3)[band]]


def _fire(r, c, scale, night):
    """Letters of hellfire, a colour for each row of the face: white-hot at the foot where they burn, through
    yellow and orange to red at their tips."""
    band = min(6, r // scale)
    return (LAVA[3], LAVA[4], FIRE[3], FIRE[4], FIRE[5], FIRE[5], FIRE[6])[band]


GILT = Paint("gilt", _gilt)
FIRE_PAINT = Paint("fire", _fire)


def licks(p: Pix, cells, scale, L, rnd, y0):
    """Flames licking up off a title's letters: from the tops of its strokes, here and there, little tongues of fire
    that flicker, each on one of the three phases."""
    if scale < 2:
        return
    tops = sorted({(gx, gy) for (gx, gy) in cells if (gx, gy - 1) not in cells})
    used = set()
    for (gx, gy) in tops:
        if gy > y0 + 3 * scale or rnd.random() > (0.2 if scale >= 3 else 0.12):
            continue
        if any(abs(gx - ux) < 3 and abs(gy - uy) < 3 for ux, uy in used):
            continue
        used.add((gx, gy))
        h = rnd.randint(2, 3 + scale // 2)
        Lf = p.flicker(rnd.randrange(3))
        for i in range(1, h + 1):
            f = i / h
            col = FIRE[5] if f < 0.34 else (FIRE[4] if f < 0.67 else LAVA[4])
            sway = 1 if (i == h and rnd.random() < 0.5) else 0
            p.px(gx + sway, gy - i, col, Lf)
        if scale >= 3:
            p.px(gx + 1, gy - 1, FIRE[4], Lf)


def title(p: Pix, x, y, s, night: bool, scale: int, motion: bool) -> int:
    """A title as the set letters it. By day in gilt, edged in the gold's darkest tone, lit down its left edges and
    shaded along its foot, haloed in the glory round it; in a wide moving header a glint crosses it every
    `GLINT` seconds. By night in hellfire, edged in the dark of the lava, glowing red and licked by flames."""
    # a drawing made lighter to fit its budget sets its title over a shadow in place of the edge all round it
    edge = {"shadow": X["title_day"] if not night else LAVA[0]} if p.lite else {"outline": X["title_day"] if not night
                                                                                else LAVA[0]}
    if not night:
        w = p.text(x, y, s, X["title_day"], "57", scale, paint=GILT, bevel=(GOLD[6], GOLD[2]),
                   glow=(X["glory"], (0.34,)), night=False, **edge)
        if motion and scale >= 2 and not p.lite:
            glint(p, x, y, s, scale, w)
        return w
    return p.text(x, y, s, X["title_night"], "57", scale, paint=FIRE_PAINT, glow=(X["heat"], (0.26,)),
                  finish=licks if motion else None, night=True, **edge)


def glint(p: Pix, x, y, s, scale, w):
    """The glint that crosses a gilt title: its letters again in white light, seen only through a narrow slanting
    window that sweeps across the line, rests, and comes round again."""
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
              f'type="translate" values="{a} 0;{b} 0;{b} 0" keyTimes="0;.35;1" dur="{num(GLINT)}s" '
              f'repeatCount="indefinite"/></polygon></clipPath><g clip-path="url(#{cid})" stroke="{X["glint"]}" '
              f'stroke-opacity=".8">{"".join(uses)}</g>')
    p.raw(0.4, moving, "")


# --------------------------------------------------------------------------- on the rule
def wisps(p: Pix, x0, x1, y, seed=0):
    """Cloud lying along a header's rule where nothing stands on it: little banks of cloud a row or two deep,
    lit along their tops, with gaps between."""
    rnd = random.Random(seed * 37 + x0)
    x = x0 + rnd.randint(0, 6)
    while x < x1 - 3:
        run = rnd.randint(5, 14)
        e = min(x + run, x1)
        hgt = rnd.choice((1, 2, 2, 3))
        for xx in range(x, e):
            k = min(xx - x, e - 1 - xx)
            hh = max(1, min(hgt, 1 + k // 2))
            for i in range(hh):
                c = CLOUD[6] if i == hh - 1 else CLOUD[4]
                p.px(xx, y - 1 - i, c)
            p.px(xx, y - 1, CLOUD[3] if hh > 1 else CLOUD[5])
        x = e + rnd.randint(3, 12)


def crust(p: Pix, x0, x1, y, seed=0):
    """Lava crusted along a header's rule where nothing stands on it: black rock a row or two deep, its cracks
    glowing, and now and then a drop of fire running off its edge."""
    rnd = random.Random(seed * 41 + x0)
    x = x0 + rnd.randint(0, 4)
    while x < x1 - 2:
        run = rnd.randint(4, 12)
        e = min(x + run, x1)
        hgt = rnd.choice((1, 1, 2, 2))
        for xx in range(x, e):
            k = min(xx - x, e - 1 - xx)
            hh = max(1, min(hgt, 1 + k))
            for i in range(hh):
                p.px(xx, y - 1 - i, BASALT[4] if i == hh - 1 else BASALT[2])
            if rnd.random() < 0.18:
                p.px(xx, y - 1, LAVA[4])
        if rnd.random() < 0.35:
            dx = rnd.randrange(x, e)
            p.px(dx, y + 1, LAVA[4])
            p.px(dx, y + 2, LAVA[3])
        x = e + rnd.randint(2, 9)


# --------------------------------------------------------------------------- the marks and the link buttons
# Four sprites, 7 by 7, each a thing of heaven drawn where its fallen twin stands by night: the halo and the horned
# head, the feather and the skull, the star and the flame, the sword of light and the pitchfork. The link buttons
# carry them by turns; the H2's mark is the first pair and the H3's the third.
TWINS = (("halo", "devil"), ("feather", "skull"), ("star", "flame"), ("sword", "pitchfork"))
ICONS = {
    "halo": [".......", ".awaab.", "a.....c", "b.....d", ".bccdd.", ".......", "......."],
    "devil": ["a.....a", "ab...ba", ".bhhhb.", ".hefeh.", ".hhhhh.", "..hgh..", "...h..."],
    "feather": [".....ab", "....aab", "...aab.", "..aab..", ".aab...", ".ab....", "q......"],
    "skull": [".abbbc.", "abbbbbc", "beeceec", "bfgcfgc", "bbbcbbd", ".bcccd.", ".c.c.d."],
    "star": ["...a...", "..aab..", "aaabbbc", ".abbbc.", "..bbc..", ".bc.cc.", "b.....c"],
    "flame": ["...1...", "..121..", "..232..", ".23431.", "1345431", "2456542", ".35653."],
    "sword": ["......w", ".....ab", "....ab.", ".c.ab..", "..c....", ".d.c...", "e......"],
    "pitchfork": [".a.a.a.", ".b.b.b.", ".ccccc.", "...b...", "...b...", "...b...", "...b..."],
}


def icon_pal(name: str) -> dict:
    """A sprite's tones: heaven's for a day face, lit from the upper left; hell's for a night face, lit by the fire."""
    return {
        "halo": {"w": C["white"], "a": GOLD[5], "b": GOLD[4], "c": GOLD[3], "d": GOLD[2]},
        "devil": {"a": HORN[5], "b": HORN[3], "h": HIDE[4], "e": FIRE[5], "f": HIDE[2], "g": HORN[6]},
        "feather": {"a": LINEN[3], "b": LINEN[1], "q": GOLD[3]},
        "skull": {"a": BONE[6], "b": BONE[5], "c": BONE[3], "d": BONE[2], "e": BASALT[0], "f": LAVA[4],
                  "g": FIRE[5]},
        "star": {"a": GOLD[5], "b": GOLD[4], "c": GOLD[2]},
        "flame": {str(i): FIRE[i] for i in range(7)},
        "sword": {"w": C["white"], "a": STEEL[4], "b": STEEL[2], "c": GOLD[3], "d": AZURE[2], "e": GOLD[2]},
        "pitchfork": {"a": LAVA[4], "b": IRON[6], "c": IRON[5]},
    }[name]


def icon(index: int, night: bool) -> tuple:
    """The `index`-th link button's sprite and its tones."""
    name = TWINS[index % len(TWINS)][1 if night else 0]
    return ICONS[name], icon_pal(name)


def section_mark(p: Pix, x, y, night: bool):
    """After an H2's SECTION A-A, the sign of the guardian it shows: by day a halo in the glory of its own light, lit
    on its far rim and its left and twinkling there; by night a horned head, its eyes burning in the heat round it."""
    if night:
        glow(p, x + 3.5, y + 3.0, 5.0, 4.5, X["heat"], (0.12, 0.22))
        p.sprite(x, y - 1, ICONS["devil"], icon_pal("devil"))
        Lb = p.blink(1)
        p.px(x + 2, y + 2, FIRE[6], Lb)
        p.px(x + 4, y + 2, FIRE[6], Lb)
        return
    cx, cy = x + 5.0, y + 3.0
    glow(p, cx, cy, 7.0, 3.6, X["glory"], (0.2, 0.36))
    for (qx, qy) in ellipse(cx, cy, 5.0, 2.0) - ellipse(cx, cy + 0.15, 3.4, 0.8):
        t = 4 + (1 if qy < cy else -1) + (1 if qx + 0.5 < cx - 2 else -1 if qx + 0.5 > cx + 2 else 0)
        p.px(qx, qy, GOLD[max(2, min(6, t))])
    p.px(int(cx) - 3, int(cy) - 2, C["white"], p.twinkle(1))


def strip_mark(p: Pix, x, y, night: bool):
    """Beside an H3's title, the herald's own light: by day a gold star, its heart twinkling and a glint beside it;
    by night a flame of hell's own fire, flickering, and sparks flying off it."""
    if night:
        from .hell import flame
        glow(p, x + 3.5, y, 4.5, 6.0, X["heat"], (0.1, 0.2), L=p.flicker(1, back=True))
        flame(p, x + 3, y + 4, s=0.8, phase=1, halo=False)
        p.px(x + 8, y - 5, FIRE[5], p.twinkle(2))
        p.px(x + 9, y - 8, LAVA[4], p.twinkle(0))
    else:
        p.sprite(x, y - 3, ICONS["star"], icon_pal("star"))
        p.px(x + 3, y, C["white"], p.twinkle(0))
        sparkle(p, x + 10, y - 4, L=p.twinkle(2))


def link_top(p: Pix, x0, x1, y, seed, night: bool):
    """Along a link button's top edge, the sheet's frame in little. By day gilt, lit along its top, over a string of
    pearls on a gold cord. By night black iron studded red-hot every six pixels, over a seam of the fire's glow, as
    the frame's own iron is."""
    for xx in range(x0 - 1, x1 + 1):
        k = xx + seed
        if night:
            p.px(xx, y, FIRE[5] if k % 6 == 0 else IRON[4])
            p.px(xx, y + 1, (LAVA[4], LAVA[2], LAVA[1], LAVA[1], LAVA[1], LAVA[2])[k % 6])
        else:
            p.px(xx, y, GOLD[5])
            p.px(xx, y + 1, (C["white"], PEARL[2], GOLD[3])[k % 3])
