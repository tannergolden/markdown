# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rooftop set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is the sky over the city in summer: pale blue by day, deepest overhead and paling toward the haze, and by
night the city's deep blue with the code's glyphs showing through it for stars. A steel column stands down each side,
riveted, a girder truss runs along the top, parting either side of the month's mark, and the foot is a parapet's
concrete coping. Titles are towers of blue mirror glass, a tower to a letter, their mullions ruling them in floors
and bays and the sky running down their faces, their roofs catching the light; by night the glass goes dark and its
windows are lit here and there in phosphor. The headers' pieces: clouds drifting across the sky by day and
searchlights sweeping it by night; towers of brick with their fire escapes, their water towers on their stilts and
their bulkheads, pigeons on their parapets by day; the man in the long dark coat leaping off a roof, the coat flaring
behind him, and bending back from the bullets in bullet time, the agent aiming at him; a helicopter hovering, its
rotor turning and by night its spotlight on the roof; a tower of blue glass rising behind a roof's parapet with its
aviation light; and far below the city in two rows of towers, hazy by day and lit window by window by night under the
hand's moon. The footers' parapet of brick and its small water tower with its lamp, and the steel, glass, concrete,
brick, brass and paint every link, badge and element is made of. Everything is shaded from the one light in the upper
left on the set's own ramps, and every light is the hand's phosphor. A drawing made lighter thins only texture: fewer
clouds in their tile, fewer windows lit, the near city's windows by day and the joints between a water tower's
staves, keeping every piece and all the motion."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, Paint, Pix, fold, num, tube
from .palette import C, DAY_SKY, NIGHT_SKY, RAMP, X

GLASS, STEEL, CONCRETE, BRICK = RAMP["glass"], RAMP["steel"], RAMP["concrete"], RAMP["brick"]
CEDAR, COAT, HAZE, DUSK = RAMP["cedar"], RAMP["coat"], RAMP["haze"], RAMP["dusk"]
OLIVE, PIGEON, CLOUD, FLAME, MOON = RAMP["olive"], RAMP["pigeon"], RAMP["cloud"], RAMP["flame"], RAMP["moon"]
EDGE = 4          # the frame's width down each side and along the foot
LOOP = 4.0        # seconds the leaper's hang takes, round and round: within the hand's four to eight
ROTOR = 0.32      # seconds the rotor takes to turn a half turn, in four frames



def ramp_at(ramp: list, i: int) -> str:
    """A ramp's tone `i`, held to the ramp's ends, so a night's darkening never wraps round to its lightest."""
    return ramp[max(0, min(len(ramp) - 1, i))]

# --------------------------------------------------------------------------- the sky
def _edges(h: int, n: int) -> list:
    return [round(i * h / n) for i in range(n + 1)]


def sky(p: Pix, night: bool):
    """The sheet: the summer sky in bands by day, deepest overhead and paling toward the haze over the city; by night
    the city's deep blue, deepest overhead and lifting toward the city's glow."""
    bands = NIGHT_SKY if night else DAY_SKY
    edges = _edges(p.h, len(bands))
    for i, col in enumerate(bands):
        at = f' y="{edges[i]}"' if edges[i] else ""
        p.under.append(f'<rect{at} width="{p.w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the band of sky it falls in."""
    bands = NIGHT_SKY if night else DAY_SKY
    edges = _edges(p.h, len(bands))
    return next(bands[i] for i in range(len(bands)) if y < edges[i + 1] or i == len(bands) - 1)


# --------------------------------------------------------------------------- the frame
def frame(p: Pix, night: bool, header: bool = False):
    """The border: a steel column down each side, its flange lit along its left edge and shaded along its right, its
    rivets in a file down it; a steel flange along the top; and along the foot a parapet's coping of concrete, its top
    catching the light over its face and the drip under it in shade, laid in lengths with a joint between."""
    w, h = p.w, p.h
    k = -1 if night else 0
    S = STEEL
    for x0 in (0, w - EDGE):
        p.vline(x0, 0, h, S[0])
        p.vline(x0 + 1, 0, h, ramp_at(S, 5 + k))
        p.vline(x0 + 2, 0, h, ramp_at(S, 3 + k))
        p.vline(x0 + 3, 0, h, ramp_at(S, 1 + k))
    uid = "fr"
    for n, x0 in enumerate((0, w - EDGE)):
        p.defs.append(f'<pattern id="{uid}r{n}" x="{x0}" y="3" width="4" height="9" patternUnits="userSpaceOnUse">'
                      f'<path stroke="{ramp_at(S, 6 + k)}" d="M2 .5h1"/><path stroke="{S[0]}" d="M2 1.5h1"/></pattern>')
        p.shapes["base"].append(f'<rect x="{x0}" width="4" height="{h - 4}" fill="url(#{uid}r{n})"/>')
    p.hline(0, w, 0, S[0])
    p.hline(1, w - 1, 1, ramp_at(S, 4 + k))
    Q = CONCRETE
    p.hline(0, w, h - 4, ramp_at(Q, 6 + k))
    p.hline(1, w - 1, h - 3, ramp_at(Q, 4 + k))
    p.hline(1, w - 1, h - 2, ramp_at(Q, 2 + k))
    p.hline(0, w, h - 1, Q[0])
    p.defs.append(f'<pattern id="{uid}j" x="{EDGE + 20}" y="{h - 3}" width="37" height="2" '
                  f'patternUnits="userSpaceOnUse"><path stroke="{ramp_at(Q, 1 + k)}" d="M.5 0v2"/>'
                  f'<path stroke="{ramp_at(Q, 5 + k)}" d="M1.5 0v1"/></pattern>')
    p.shapes["base"].append(f'<rect x="{EDGE}" y="{h - 3}" width="{w - 2 * EDGE}" height="2" fill="url(#{uid}j)"/>')


# --------------------------------------------------------------------------- the truss
PANEL = 8         # a bay of the truss


def truss(p: Pix, x0, x1, night: bool, box, marked: bool, top: int = 2):
    """The girder truss along a header's top, from x0 to x1, eight rows deep: its top and bottom chords lit along
    their upper faces, a post in every bay and the braces zigzagging between them, a rivet at every joint, and a post
    doubled at each end with a gusset plate. Where the month's mark hangs it stops either side of its box, two units
    clear, and runs on unbroken with no mark. By night a warning light burns phosphor at each end of the span,
    blinking. Laid as a pattern of a pair of bays, so the truss costs little however long."""
    a, _, b, _ = box
    runs = [(x0, a - 1), (b + 1, x1)] if marked else [(x0, x1)]
    k = -1 if night else 0
    S = STEEL
    tid = "tr"
    span = 2 * PANEL
    web = (f'<path stroke="{ramp_at(S, 5 + k)}" d="M0 .5h{span}"/>'
           f'<path stroke="{ramp_at(S, 3 + k)}" d="M0 1.5h{span}"/>'
           f'<path stroke="{ramp_at(S, 3 + k)}" d="M.5 2v4M{PANEL + .5} 2v4"/>'
           f'<path stroke="{ramp_at(S, 4 + k)}" d="M1 2.5h2M3 3.5h2M5 4.5h2M7 5.5h1M{PANEL + 7} 2.5h1M{PANEL + 5} 3.5h2'
           f'M{PANEL + 3} 4.5h2M{PANEL + 1} 5.5h2"/>'
           f'<path stroke="{ramp_at(S, 4 + k)}" d="M0 6.5h{span}"/>'
           f'<path stroke="{ramp_at(S, 1 + k)}" d="M0 7.5h{span}"/>'
           f'<path stroke="{ramp_at(S, 6 + k)}" d="M0 1.5h1M0 6.5h1M{PANEL} 1.5h1M{PANEL} 6.5h1"/>')
    p.defs.append(f'<pattern id="{tid}" x="{x0}" y="{top}" width="{span}" height="8" patternUnits="userSpaceOnUse">'
                  f'{web}</pattern>')
    for i, (r0, r1) in enumerate(runs):
        p.shapes["base"].append(f'<rect x="{r0}" y="{top}" width="{r1 - r0}" height="8" fill="url(#{tid})"/>')
        for end in (r0, r1 - 2):
            p.rect(end, top, 2, 8, ramp_at(S, 3 + k))
            p.vline(end, top, top + 8, ramp_at(S, 5 + k))
            p.px(end, top + 7, ramp_at(S, 1 + k))
        for gx in (r0 + 2, r1 - 5):
            p.rect(gx, top + 2, 3, 4, ramp_at(S, 2 + k))
            p.px(gx, top + 2, ramp_at(S, 5 + k))
            p.px(gx + 1, top + 3, ramp_at(S, 6 + k))
        if night:
            for j, end in enumerate((r0 + 1, r1 - 1)):
                L = p.blink(i * 2 + j)
                p.px(end, top + 8, FLAME[5], L)
                p.px(end, top + 9, FLAME[3], L)


# --------------------------------------------------------------------------- the titles
SIDES = {"r": (-1, 0), "d": (0, -1), "l": (1, 0), "u": (0, 1)}   # each mask: the line moved so a unit shows through
#                                                                  it where its neighbour that way is a letter's too
DEPTH = ((1, 0), (2, 0), (2, 1))       # where a letter's tower stands back from its face: its side in shade


def _at(dx, dy) -> str:
    return (f' x="{dx}"' if dx else "") + (f' y="{dy}"' if dy else "")


def _glass_fill(r, c, scale, night):
    """Mirror glass ruled in floors and bays: a floor's spandrel along the foot of every row of the face and a mullion
    every fourth column, each a tone deeper than the glass beside it, and the panes between reflecting the sky, palest
    at a tower's head and deepening down it, crossed by a slanting gleam. By night the glass is the dusk's blue with
    the city in it, and pane after pane is lit in phosphor."""
    band = r / (7 * scale)
    if night:
        floor, bay = r // scale, c // 4
        h = (floor * 7 + bay * 5 + floor * bay * 3) % 9
        if r % scale == scale - 1 or c % 4 == 3:
            return GLASS[2]
        return FLAME[5] if h == 0 else FLAME[4] if h == 4 else FLAME[3] if h in (2, 7) else \
            GLASS[5] if (c - r) % 16 < 4 else GLASS[4] if band < 0.5 else GLASS[3]
    t = 5 if band < 0.3 else 4 if band < 0.7 else 3
    if (c - r) % 16 < 5:
        t += 1
    if r % scale == scale - 1 or c % 4 == 3:
        t -= 2
    return GLASS[max(1, min(6, t))]


GLASS_PAINT = Paint("glass", _glass_fill, period=16)


def glass_title(p: Pix, x, y, s, scale, night: bool) -> int:
    """A title in towers of blue mirror glass, a tower to a letter.

    The line's letters are set once, from the face's own glyphs, and laid again
    for every part: the tower's side standing back from its face to the right in
    shade, then the letters in the tone of their lower and right edges, again where
    the units to their right and below are a letter's too in the pale of their
    roofs and their lit left edges, and again in their glass where all four
    neighbours are, each through masks of the line moved a unit. The glass is ruled
    in floors and bays and reflects the sky (see `_glass_fill`); by night it is dark,
    lit pane by pane, and a few panes go on and off. A long title costs little more
    than a short one. Returns its width."""
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
    p.words.append((x - 1, y - 1, x + w + 3, y + rows * scale + 2))
    if not placed:
        return max(0, w)
    tid = f"gt{len(p.defs)}"
    letters = "".join(f'<use href="#{p.syms[("glyph", "57", ch)]}"'
                      + (f' x="{num((gx - x) / scale)}"' if gx > x else "") + "/>" for ch, gx in placed)
    p.defs.append(f'<g id="{tid}" transform="translate({x} {y}) scale({scale})">{letters}</g>')
    box = f'maskUnits="userSpaceOnUse" x="{x - 2}" y="{y - 2}" width="{w + 6}" height="{rows * scale + 6}"'
    for name, (dx, dy) in SIDES.items():
        p.defs.append(f'<mask id="{tid}{name}" {box}><use href="#{tid}"{_at(dx, dy)} stroke="{C["white"]}"/></mask>')
    G = GLASS
    side, edge, lit, body = (G[1], G[0], G[6], f"url(#{p._pattern(GLASS_PAINT, scale, True)})") if night else \
        (G[1], G[1], G[6], f"url(#{p._pattern(GLASS_PAINT, scale, False)})")

    def masked(names, colour):
        inner = f'<use href="#{tid}" stroke="{colour}"/>'
        for n in names:
            inner = f'<g mask="url(#{tid}{n})">{inner}</g>'
        return inner
    depth = f'<g stroke="{side}">' + "".join(f'<use href="#{tid}"{_at(dx, dy)}/>' for dx, dy in DEPTH) + "</g>"
    body = f'<use href="#{tid}" stroke="{edge}"/>' + masked("rd", lit) + masked("rdlu", body)
    p.raw(0.1, depth + body, depth + body)
    if night and scale >= 3:
        rnd = random.Random(len(s) * 5 + scale)
        for i, (ch, gx) in enumerate(placed):
            cols = [(c, r) for r, cs in enumerate(glyphs[ch][1]) for c in cs]
            c, r = cols[rnd.randrange(len(cols))]
            wx = gx + c * scale + rnd.randrange(max(1, scale - 1)) // 4 * 4
            wy = y + r * scale + (scale // 2 // 2) * 2
            p.px(wx, wy, FLAME[5], p.twinkle(i))
    return w


# --------------------------------------------------------------------------- the night sky
def moon(p: Pix, cx, cy, r: float = 5.0, glow: float = 2.4):
    """The hand's moon, full, lit from the upper left on its ramp with its seas in shade and a halo round it."""
    for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            lam = -0.6 * dx - 0.7 * dy + 0.4 * math.sqrt(max(0, 1 - d2))
            c = MOON[5] if lam > 0.55 else MOON[4] if lam > 0.15 else MOON[3] if lam > -0.3 else MOON[2]
            p.px(x, y, c)
    for q in ((0, 1), (1, 1), (-2, -1), (2, -2), (-1, 3)):
        x, y = round(cx) + q[0], round(cy) + q[1]
        if p.get(x, y) in (MOON[3], MOON[4]):
            p.px(x, y, MOON[2])
    p.halo(cx, cy, r * glow, r * glow, MOON[3], (0.04, 0.08, 0.13))


def _sky_clip(p: Pix, foot: int, box) -> str:
    """The sky the atmosphere may cross: the whole sheet between the frame's columns down to row `foot`, above the
    tagline, but for the month's mark's box, `box`, two units clear. Made once; returns its id."""
    cid = "atm"
    if not any(f'id="{cid}"' in d for d in p.defs):
        a, _, b, d = box
        rects = [(EDGE, 2, a - 2, foot), (b + 2, 2, p.w - EDGE, foot), (a - 2, d + 2, b + 2, foot)]
        p.defs.append(f'<clipPath id="{cid}">' + "".join(
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>' for x0, y0, x1, y1 in rects
            if x1 > x0 and y1 > y0) + "</clipPath>")
    return cid


# The searchlights, each (its lamp's column and row, the two bearings it sweeps between in degrees from the upright,
# clockwise, and the seconds a sweep there and back takes): one on each roof, sweeping across the sky over the title so
# their beams cross and part again.
BEAM_REACH = 320


def beams(p: Pix, foot: int, box, lights, motion: bool):
    """Searchlights by night, their beams of phosphor rising from the roofs and sweeping slowly across the whole sky,
    behind the title and the truss, crossing and parting: each a pale core in a wider glow, laid faint so the title
    reads through them, two degrees a step on one of the hand's slow sweeps, the still twin holding each part way
    over. They end above the tagline and keep out of the month's mark (see `_sky_clip`)."""
    cid = _sky_clip(p, foot, box)
    moving, still = [], []
    for (ox, oy), a0, a1, dur in lights:
        r = BEAM_REACH
        beam = (f'<polygon points="{ox - 2} {oy} {ox + 2} {oy} {ox + 18} {oy - r} {ox - 18} {oy - r}" '
                f'fill="{FLAME[3]}" fill-opacity=".11"/>'
                f'<polygon points="{ox - 1} {oy} {ox + 1} {oy} {ox + 7} {oy - r} {ox - 7} {oy - r}" '
                f'fill="{FLAME[4]}" fill-opacity=".17"/>')
        step = 2 if a1 > a0 else -2
        angles = list(range(a0, a1, step)) + list(range(a1, a0, -step))
        at = round(len(angles) * 0.3)
        angles = angles[at:] + angles[:at]
        values = ";".join(f"{a} {ox} {oy}" for a in angles)
        moving.append(f'<g>{beam}<animateTransform attributeName="transform" type="rotate" values="{values}" '
                      f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
        still.append(f'<g transform="rotate({angles[0]} {ox} {oy})">{beam}</g>')
    m, st = (f'<g clip-path="url(#{cid})">{"".join(x)}</g>' for x in (moving, still))
    p.raw(-9, m if motion else st, st)


# The clouds drifting across the summer sky, each a cluster of puffs (centre across and down, radius) over a flat
# foot, laid in a tile that drifts along.
PUFFS = (((4, 6, 3.2), (9, 4, 4.4), (15, 3.4, 5), (21, 4.6, 4.2), (26, 6.4, 3)),
         ((3, 4.4, 2.6), (7, 3, 3.6), (12, 4, 3)),
         ((4, 5, 3.4), (10, 3.2, 4.6), (16, 4.4, 4), (21, 5.6, 2.8)))
CLOUD_AT = ((8, 11, 0), (66, 31, 1), (104, 12, 2), (158, 37, 0), (200, 17, 1))  # where each lies in the tile, and which
CLOUD_TILE = (240, 52)
DRIFT = 44.0      # seconds the clouds take to drift a tile's breadth, two units a step: one of the hand's slow sweeps


def _cloud(puffs) -> dict:
    """A cloud's cells and tones: the puffs' union over a flat foot, lit along its tops, shaded along its foot."""
    foot = max(round(cy) + 2 for _, cy, _ in puffs)
    cells = set()
    for cx, cy, r in puffs:
        for y in range(math.floor(cy - r), foot):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    cells.add((x, y))
    out = {}
    for (x, y) in cells:
        up = (x, y - 1) not in cells
        out[(x, y)] = CLOUD[6] if up else CLOUD[2] if y == foot - 1 else CLOUD[4] if y == foot - 2 else CLOUD[5]
    return out


def cloud_drift(p: Pix, foot: int, box, motion: bool):
    """Summer clouds by day drifting slowly across the whole sky from the left, behind the title and the truss: a tile
    of them stepping two units along at a time and round again on one of the hand's slow sweeps, the still twin holding
    them where they begin. They end above the tagline and keep out of the month's mark (see `_sky_clip`). A drawing
    made lighter lays fewer of them in the tile."""
    cid = _sky_clip(p, foot, box)
    tw, th = CLOUD_TILE
    rows: dict = {}
    for cx, cy, n in CLOUD_AT[:3] if p.lite else CLOUD_AT:
        for (x, y), c in _cloud(PUFFS[n]).items():
            rows.setdefault(c, {}).setdefault(cy + y, []).append(cx + x)
    tile = "".join(f'<path stroke="{c}" d="{Pix._d(r)}"/>' for c, r in rows.items())
    drift = (f'<animateTransform attributeName="patternTransform" type="translate" '
             f'values="{";".join(f"{x} 0" for x in range(0, tw, 2))}" dur="{num(DRIFT)}s" repeatCount="indefinite" '
             f'calcMode="discrete"/>') if motion else ""
    p.defs.append(f'<pattern id="cdt" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">{tile}{drift}</pattern>')
    layer = f'<g clip-path="url(#{cid})"><rect x="{EDGE}" y="2" width="{p.w - 2 * EDGE}" height="{foot - 2}" ' \
            f'fill="url(#cdt)"/></g>'
    p.raw(-9, layer, layer)


def lamp(p: Pix, x, y, night: bool):
    """A searchlight's lamp on a roof, its drum on a yoke on a post, its face toward the sky: by night burning
    phosphor, its light thrown round it."""
    k = -2 if night else 0
    S = STEEL
    p.vline(x + 1, y + 3, y + 6, ramp_at(S, 2 + k))
    p.hline(x - 1, x + 4, y + 6, ramp_at(S, 3 + k))
    p.rect(x, y, 3, 3, ramp_at(S, 3 + k))
    p.px(x, y, ramp_at(S, 5 + k))
    if night:
        p.hline(x, x + 3, y - 1, FLAME[6])
        p.halo(x + 1.5, y - 1, 6, 5, FLAME[3], (0.06, 0.12, 0.2))
    else:
        p.hline(x, x + 3, y - 1, GLASS[5])


# --------------------------------------------------------------------------- the buildings
def facade(p: Pix, x0, x1, top, g, night: bool, seed: int = 3, lit: float = 0.4):
    """A building's brick face from x0 to x1 below its parapet at row `top`, down to row g: courses of brick in its
    tones, a row of windows every floor with a lintel over each, and the corner it turns toward the light lit. By
    night the brick goes dark and a window here and there burns phosphor, a few going on and off; fewer in a drawing
    made lighter, the ones going on and off all kept."""
    rnd = random.Random(seed)
    k = -3 if night else 0
    B = BRICK
    pid = f"bk{x0}"
    p.defs.append(f'<pattern id="{pid}" y="{top + 2}" width="4" height="3" patternUnits="userSpaceOnUse">'
                  f'<rect width="4" height="3" fill="{ramp_at(B, 3 + k)}"/><path stroke="{ramp_at(B, 2 + k)}" '
                  f'd="M0 .5h4"/></pattern>')
    p.shapes["base"].append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{g - top + 1}" fill="url(#{pid})"/>')
    p.vline(x0, top, g + 1, ramp_at(B, 5 + k))
    p.vline(x1 - 1, top, g + 1, ramp_at(B, 1 + k))
    cols, rows = list(range(x0 + 3, x1 - 5, 6)), list(range(top + 3, g - 3, 7))
    if not cols or not rows:
        return
    if night:
        pane = f'<rect x="1" y="1" width="3" height="4" fill="{DUSK[0]}"/>'
    else:
        pane = (f'<rect x="1" y="1" width="3" height="4" fill="{GLASS[2]}"/><path stroke="{GLASS[1]}" d="M3.5 2v3"/>'
                f'<path stroke="{GLASS[5]}" d="M1 1.5h1"/><path stroke="{GLASS[4]}" d="M2 1.5h1"/>')
    wid = f"wn{x0}"
    p.defs.append(f'<pattern id="{wid}" x="{cols[0] - 1}" y="{rows[0] - 1}" width="6" height="7" '
                  f'patternUnits="userSpaceOnUse"><path stroke="{CONCRETE[4 if not night else 1]}" d="M0 .5h5"/>'
                  f'{pane}</pattern>')
    p.shapes["base"].append(f'<rect x="{cols[0] - 1}" y="{rows[0] - 1}" width="{cols[-1] - cols[0] + 5}" '
                            f'height="{rows[-1] - rows[0] + 5}" fill="url(#{wid})"/>')
    if night:
        for wy in rows:
            for wx in cols:
                roll = rnd.random()
                if roll < (min(lit, 0.2) if p.lite else lit):
                    L = p.twinkle(wx + wy) if roll < 0.08 else "base"
                    p.rect(wx, wy, 3, 4, FLAME[2], L)
                    p.hline(wx, wx + 3, wy, FLAME[4], L)


def fire_escape(p: Pix, x0, x1, top, g, night: bool):
    """An iron fire escape down a building's face from x0 to x1: a landing at every floor under its windows, railed,
    and a stair slanting between each landing and the next, black iron lit along its top; by night a silhouette
    against the lit windows behind it."""
    k = -1 if night else 0
    S = STEEL
    iron, lit = ramp_at(S, 1 + k), ramp_at(S, 3 + k)
    floors = list(range(top + 7, g - 1, 7))
    for n, y in enumerate(floors):
        p.hline(x0, x1, y, lit)
        p.hline(x0, x1, y + 1, iron)
        p.hline(x0, x1, y - 3, iron)
        for bx in range(x0, x1 + 1, 2):
            p.vline(bx, y - 2, y, iron)
        if n + 1 < len(floors):
            y2 = floors[n + 1]
            for i in range(y2 - y - 1):
                sx = (x0 + 2 + i) if n % 2 == 0 else (x1 - 2 - i)
                p.px(sx, y + 2 + i, lit)
                p.px(sx + (1 if n % 2 == 0 else -1), y + 2 + i, iron)


def parapet(p: Pix, x0, x1, y, night: bool):
    """A parapet's coping along a roof's edge from x0 to x1, its top at row y: the cap's lit top, its face, and the
    shade it casts on the brick under it."""
    k = -2 if night else 0
    Q = CONCRETE
    p.hline(x0 - 1, x1 + 1, y, ramp_at(Q, 6 + k))
    p.hline(x0 - 1, x1 + 1, y + 1, ramp_at(Q, 4 + k))
    p.hline(x0, x1, y + 2, ramp_at(Q, 2 + k))
    p.px(x0 - 1, y + 1, ramp_at(Q, 5 + k))


def water_tower(p: Pix, x, roof, night: bool, legs: int = 13, w: int = 21, tank: int = 15):
    """The water tower on its stilts on the roof at row `roof`, from column x, `w` wide: four steel legs braced in an X
    under a deck, the cedar tank on it, `tank` rows tall, its staves lit down its left and in shade down its right,
    bound in steel hoops, and its conical roof with a finial; a ladder up its side. A drawing made lighter lets the
    joints between the staves go. Returns the row of its finial's tip."""
    k = -2 if night else 0
    S, W = STEEL, CEDAR
    c = w // 2
    deck = roof - legs
    for lx in (x + 2, x + w - 3):
        p.vline(lx, deck, roof, ramp_at(S, 3 + k))
        p.vline(lx + 1, deck, roof, ramp_at(S, 1 + k))
    for lx in (x + w // 3, x + w - 1 - w // 3):
        p.vline(lx, deck + 1, roof, ramp_at(S, 2 + k))
    for i in range(legs - 1):
        t = i / max(1, legs - 2)
        p.px(x + 3 + round(t * (w - 7)), deck + 1 + i, ramp_at(S, 2 + k))
        p.px(x + w - 4 - round(t * (w - 7)), deck + 1 + i, ramp_at(S, 2 + k))
    p.hline(x, x + w, deck, ramp_at(S, 4 + k))
    p.hline(x, x + w, deck - 1, ramp_at(S, 2 + k))
    tank_top = deck - tank
    for xx in range(x + 1, x + w - 1):
        t = (xx - x - 1) / (w - 3)
        tone = 5 if t < 0.22 else 4 if t < 0.45 else 3 if t < 0.7 else 2 if t < 0.88 else 1
        p.vline(xx, tank_top, deck - 1, ramp_at(W, tone + k))
        if (xx - x) % 3 == 0 and 0.1 < t < 0.9 and not p.lite:
            p.vline(xx, tank_top + 1, deck - 1, ramp_at(W, max(0, tone - 1) + k))
    for hy in range(tank_top + 2, deck - 2, 5):
        p.hline(x + 1, x + w - 1, hy, ramp_at(S, 2 + k))
        p.hline(x + 2, x + 2 + round((w - 3) / 3), hy, ramp_at(S, 4 + k))
    rows = 7 if w == 21 else max(3, round(7 * w / 21))
    slope = 1.6 if w == 21 else c / (rows - 1)
    for i in range(rows):
        half = 1 + round(i * slope)
        yy = tank_top - rows + i
        for xx in range(x + c - half, x + c + 1 + half):
            t = (xx - (x + c - half)) / max(1, 2 * half)
            p.px(xx, yy, ramp_at(W, 4 + k) if t < 0.4 else ramp_at(W, 2 + k) if t < 0.8 else ramp_at(W, 1 + k))
    p.hline(x - 1, x + w + 1, tank_top - 1, ramp_at(W, 1 + k))
    p.vline(x + c, tank_top - rows - 3, tank_top - rows, ramp_at(S, 3 + k))
    p.px(x + c, tank_top - rows - 4, ramp_at(S, 5 + k))
    for yy in range(tank_top, roof, 2):
        p.px(x + w, yy, ramp_at(S, 3 + k))
    p.vline(x + w + 1, tank_top, roof, ramp_at(S, 2 + k))
    return tank_top - rows - 4


# --------------------------------------------------------------------------- the people
# The man in the long coat leaping off the edge, 31 by 23, facing right: his front leg drawn up, the other trailing
# from the push, his arms flung out, and his coat flaring back behind him in two tails. Hair (q h H), skin (o e s S),
# his dark glasses (v), the coat's black leather (k x c C, its lapel w), his trousers (P p r) and his shoes (N n).
LEAP = [
    "..................qqqq.........",
    ".................qHHHhq........",
    ".................qHhhhsSo......",
    ".................qhhsvvvo......",
    "................kqhssssSo......",
    ".........oo....kkCqoesso....oo.",
    "........oSsokkkcCCkoeek.kkkkSso",
    "...kk..oseccccCCCwckccccCCCcseo",
    "..kcckkkkkxxccCCCwcxxxxccxxxkoo",
    "..kccccccccccxCCcwxxxkkxxkkk...",
    "...kcccccckkkCCccwxxck.kk......",
    "....kcccckcccCCccwxcck.........",
    ".....kccckcccccPPpxcck.........",
    "......kkckccccPpppppkk.........",
    "........kPPprxrrrppPprk........",
    "......kkPpprrcccrrrPprk........",
    "..k.kkPPprrkkkkkkkkPprk........",
    ".knkPPprrkk.......kprk.........",
    "knnnnrrkk.........kprk.........",
    ".kknnkk..........kpprkk........",
    "...kk............kpNNNnk.......",
    "..................knnnnk.......",
    "...................kkkk........",
]
# The coat's tails in the other half of his hang, a unit higher and flung wider, laid over the same rows.
TAILS_UP = {(1, 7): "k", (2, 7): "k", (2, 6): "k", (3, 6): "k", (4, 6): "k", (3, 7): "c", (4, 7): "c",
            (1, 8): "k", (2, 9): "c", (3, 10): "c", (4, 11): "c"}


def _leap_pal(night: bool) -> dict:
    K, S = COAT, RAMP["skin0"]
    return {"k": K[0], "x": K[2], "c": K[3], "C": K[5 if not night else 4], "w": K[6 if not night else 5],
            "P": K[4], "p": K[2], "r": K[1], "N": K[4], "n": K[1], "q": RAMP["coat"][0], "h": K[2], "H": K[4],
            "o": S[1], "e": S[2], "s": S[3], "S": S[4], "v": X["glasses"]}


def leaper(p: Pix, x, y, night: bool, motion: bool):
    """The man in the long dark coat leaping off the roof's edge toward the far roof, his top-left at (x, y): in a
    moving header he hangs in the air and rises a unit, his coat's tails lifting, and settles again on a four-second
    loop. By night the moon lays its light along his back and on his face, which keeps its tone. Returns the box
    he takes."""
    pal = _leap_pal(night)
    cells = {(i, j): pal[ch] for j, row in enumerate(LEAP) for i, ch in enumerate(row) if pal.get(ch)}
    if night:
        cloth = set(COAT)
        for (i, j), c in list(cells.items()):
            if c in cloth and ((i - 1, j) not in cells or (i, j - 1) not in cells):
                cells[(i, j)] = MOON[1]
    key = ("leap", night)
    if key not in p.syms:
        p.symbol(key, cells)
    key2 = ("leaptails", night)
    if key2 not in p.syms:
        p.symbol(key2, {(i, j - 1): pal[ch] for (i, j), ch in TAILS_UP.items() if (i, j - 1) not in cells})
    a, b = p.syms[key], p.syms[key2]
    still = f'<use href="#{a}" x="{x}" y="{y}"/>'
    if motion:
        moving = (f'<g><use href="#{a}" x="{x}" y="{y}"/><use href="#{b}" x="{x}" y="{y}" opacity="0">'
                  f'<animate attributeName="opacity" values="0;1" keyTimes="0;.5" dur="{num(LOOP)}s" '
                  f'repeatCount="indefinite" calcMode="discrete"/></use><animateTransform attributeName="transform" '
                  f'type="translate" values="0 0;0 -1" keyTimes="0;.5" dur="{num(LOOP)}s" repeatCount="indefinite" '
                  f'calcMode="discrete"/></g>')
    else:
        moving = still
    p.raw(2, moving, still)
    if night:
        p.halo(x + 21.5, y + 3, 4, 4, MOON[3], (0.06, 0.12), L="pool", shape=True)
    return (x, y - 1, x + len(LEAP[0]), y + len(LEAP))


# --------------------------------------------------------------------------- the far roof
# The helicopter hovering, 48 by 18, facing left: the bubble of its canopy (w, its gleam W, the pilot's shape in it
# p), the cabin lit along its upper half (B) and in shade below it (b), its belly (d), the housing of its engine on the
# cabin's roof (O lit, o), the open door dark (v), the tail boom (t) running out to the fin (f) with its stabiliser,
# and the skids on their struts under it; k its outline.
HELI = [
    "...................kk...........................",
    "...............kkkkOOkkkk.......................",
    ".............kkOOOOOOOOOOkk.....................",
    "............kOOOOOOOOOOOOOokk.................kk",
    ".......kkkkkOOOOOOOOOOOOOOooook..............kfk",
    ".....kkwwwwkBBBBBBBBBBBBBBBBBBBkkk..........kffk",
    "....kwWWwwwkBBBBBkkkkkkkBBBBBBBBBBkkkkkkkkkkkffk",
    "...kwWWwppwkBBBBBkvvvvvkBBBBBBBBBBBttttttttttffk",
    "..kwWWwpppwkBBBBBkvvvvvkBBBBBBBBBbbbbbbbbbbbbffk",
    "..kwWwwpppwkBBBBBkvvvvvkBBBBBBBbbbbkkkkkkkkkkkfk",
    ".kwwWwppppwkbbbbbkvvvvvkbbbbbbbbbbk...kddk...kk.",
    ".kwwwwppppwkbbbbbkvvvvvkbbbbbbbbbk....kkkk......",
    ".kdwwwwwwwwkbbbbbkkkkkkkbbbbbbbbk...............",
    "..kddddddddddddddddddddddddddddk................",
    "...kkkkkdddddddddddddddddddkkk..................",
    ".......kk.....k..........k......................",
    "..k...k.......k..........k......................",
    "...kkkkkkkkkkkkkkkkkkkkkkkkkkkk.................",
]
HUB = (19, 0)      # where the rotor's mast stands on the helicopter's art
TAIL = (45, 4)     # where the tail rotor turns
BELLY = (13, 14)   # where its spotlight hangs under the cabin


def helicopter(p: Pix, x, y, night: bool, motion: bool, span: int = 23, aim=None):
    """The helicopter hovering with its top-left at (x, y): olive drab, its canopy catching the sky, its rotor over it
    turning in four frames, the blades broadside, slanting, end on and slanting again, a frame every hundredth of a
    third of a second, and its tail rotor turning in two; by night a light on its belly blinking phosphor and its
    spotlight thrown down onto the roof under it, to row `aim`, a cone of phosphor with a pool where it lands. The
    still twin holds the rotor broadside."""
    k = -2 if night else 0
    OL, G = OLIVE, GLASS
    pal = {"k": OL[0], "B": ramp_at(OL, 4 + k), "b": ramp_at(OL, 3 + k), "d": ramp_at(OL, 2 + k),
           "O": ramp_at(OL, 5 + k), "o": ramp_at(OL, 4 + k), "f": ramp_at(OL, 3 + k), "t": ramp_at(OL, 4 + k),
           "w": ramp_at(G, 3 + k), "W": ramp_at(G, 5 + k), "v": ramp_at(OL, 1 + k), "p": ramp_at(G, 1 + k)}
    p.sprite(x, y, HELI, pal, 1, "base", reuse=True)
    hx, hy = x + HUB[0], y + HUB[1] - 1
    frames = (span, round(span * 0.7), 3, round(span * 0.7))
    for f, half in enumerate(frames):
        L = p.seq(f"ro{f}", f / 4, (f + 1) / 4, ROTOR, keep=f == 0, z=1) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        p.hline(hx - half + 1, hx + half + 1, hy, ramp_at(OL, 1 + k) if f != 2 else ramp_at(OL, 2 + k), L)
        if f in (0, 2):
            p.hline(hx - half + 3, hx + half - 1, hy - 1, ramp_at(OL, 4 + k) + ":0.35", L)
    p.px(hx, hy, OL[0])
    p.px(hx + 1, hy, OL[0])
    tx, ty = x + TAIL[0], y + TAIL[1]
    for f in range(2):
        L = p.seq(f"tr{f}", f / 2, (f + 1) / 2, ROTOR / 2, keep=f == 0, z=1) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        if f == 0:
            p.vline(tx, ty - 3, ty + 4, ramp_at(OL, 1 + k), L)
        else:
            p.hline(tx - 3, tx + 3, ty, ramp_at(OL, 1 + k), L)
    if night:
        L = p.blink(1) if motion else "base"
        p.px(x + 30, y + 13, FLAME[5], L)
        p.px(x + 47, y + 3, FLAME[4], L)
        if aim:
            bx, by = x + BELLY[0], y + BELLY[1]
            p.shapes[p.layer("pool")].append(f'<polygon points="{bx} {by} {bx + 2} {by} {bx + 13} {aim} {bx - 11} '
                                             f'{aim}" fill="{FLAME[3]}" fill-opacity=".12"/>')
            p.halo(bx + 1, aim - 1, 13, 3, FLAME[3], (0.08, 0.16, 0.26), L="pool", shape=True)
            p.px(bx, by, FLAME[6])
            p.px(bx + 1, by, FLAME[5])


def vents(p: Pix, x, roof, night: bool):
    """The far roof's plant from column x on the roof at row `roof`: two vent stacks under their caps and a cooling unit
    with its fan behind a grille, steel lit along its left."""
    k = -2 if night else 0
    S = STEEL
    for vx, h in ((x, 6), (x + 4, 4)):
        p.rect(vx, roof - h, 2, h, ramp_at(S, 3 + k))
        p.vline(vx, roof - h, roof, ramp_at(S, 5 + k))
        p.hline(vx - 1, vx + 3, roof - h - 1, ramp_at(S, 4 + k))
        p.hline(vx - 1, vx + 3, roof - h - 2, ramp_at(S, 2 + k))
    ux = x + 8
    p.rect(ux, roof - 7, 10, 7, ramp_at(S, 3 + k))
    p.hline(ux, ux + 10, roof - 7, ramp_at(S, 5 + k))
    p.vline(ux, roof - 7, roof, ramp_at(S, 4 + k))
    p.vline(ux + 9, roof - 6, roof, ramp_at(S, 1 + k))
    for yy in range(roof - 5, roof - 1):
        for xx in range(ux + 2, ux + 7):
            if (xx - ux - 4) ** 2 + (yy - roof + 3.5) ** 2 <= 5:
                p.px(xx, yy, ramp_at(S, 1 + k) if (xx + yy) % 2 else ramp_at(S, 2 + k))


def bulkhead(p: Pix, x0, x1, top, roof, night: bool):
    """The stair's bulkhead on the far roof: a box of brick under a flat cap with its door, lit along its left."""
    k = -3 if night else 0
    B = BRICK
    p.rect(x0, top, x1 - x0, roof - top, ramp_at(B, 3 + k))
    p.vline(x0, top, roof, ramp_at(B, 5 + k))
    p.vline(x1 - 1, top, roof, ramp_at(B, 1 + k))
    for yy in range(top + 3, roof, 3):
        p.hline(x0 + 1, x1 - 1, yy, ramp_at(B, 2 + k))
    parapet(p, x0, x1, top - 2, night)
    dx = x0 + 3
    p.rect(dx, roof - 8, 5, 8, ramp_at(STEEL, 2 + k // 2) if not night else STEEL[1])
    p.vline(dx, roof - 8, roof, STEEL[4] if not night else STEEL[2])
    p.px(dx + 3, roof - 4, STEEL[5] if not night else FLAME[2])


# --------------------------------------------------------------------------- the city below
# The city's two rows of towers, far and near: how tall each may stand, how narrow and how wide, the most room between
# them, and how many of a tower's windows are lit by night.
ROWS = ((34, 5, 10, 1, 0.22), (20, 6, 13, 3, 0.45))


def far_city(p: Pix, x0, x1, g, night: bool, motion: bool, seed: int = 8):
    """The city far below between the two roofs, from x0 to x1, in two rows: towers standing up out of it as tall as
    the words over them leave room for, two units clear, the far row taller and fainter. By day they fade into the
    haze, their lit edges toward the light; by night they are dark on the dusk, the far row darkest, and their windows
    are lit a pane at a time, a few going on and off. A drawing made lighter leaves the near row's windows out by
    day."""
    for row, (most, wmin, wmax, gap, lit) in enumerate(ROWS):
        rnd = random.Random(seed + 11 * row)
        if night:
            face, edge_lit, edge = (DUSK[1], DUSK[2], DUSK[0]) if row == 0 else (DUSK[2], DUSK[3], DUSK[1])
        else:
            face, edge_lit, edge = (HAZE[5], HAZE[6], HAZE[4]) if row == 0 else (HAZE[4], HAZE[6], HAZE[3])
        x = x0 + rnd.randrange(4)
        while x < x1 - 4:
            w = min(rnd.randrange(wmin, wmax + 1), x1 - x)
            want = rnd.randrange(most // 3, most + 1)
            h = next((hh for hh in range(want, 2, -1) if p.clear_of_words(x - 2, g - hh - 2, x + w + 2, g + 1)), 0)
            if h >= 3:
                top = g - h + 1
                p.shapes["base"].append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{face}"/>')
                p.vline(x, top, g + 1, edge_lit)
                p.hline(x, x + w, top, edge_lit)
                p.vline(x + w - 1, top + 1, g + 1, edge)
                if night:
                    for wy in range(top + 2, g, 2):
                        for wx in range(x + 2, x + w - 2, 2):
                            roll = rnd.random()
                            if roll < (min(lit, 0.12) if p.lite else lit) or (motion and row and roll < 0.05):
                                L = p.twinkle(wx * 3 + wy) if (motion and row and roll < 0.05) else "base"
                                p.px(wx, wy, FLAME[1] if row == 0 or roll > lit * 0.6 else FLAME[3] if roll < 0.1
                                     else FLAME[2], L)
                elif row and w > 4 and h > 3 and not p.lite:
                    if not any(d.startswith('<pattern id="cw"') for d in p.defs):
                        p.defs.append(f'<pattern id="cw" width="2" height="2" patternUnits="userSpaceOnUse">'
                                      f'<path stroke="{HAZE[3]}" d="M0 .5h1"/></pattern>')
                    p.shapes["base"].append(f'<rect x="{x + 2}" y="{top + 2}" width="{w - 4}" height="{h - 3}" '
                                            f'fill="url(#cw)"/>')
            x += w + rnd.randrange(0, gap + 1)


# --------------------------------------------------------------------------- the pigeons
PIGEON_SIT = ["...hh.", "..hHhb", "wwggg.", ".wggg.", "..f.f."]
PIGEON_UP = ["ww...", ".wwhh", ".gggb", "..g.."]
PIGEON_DOWN = ["...hh", ".gggb", "ww...", "w...."]


def _pigeon_pal() -> dict:
    G = PIGEON
    return {"h": G[3], "H": G[5], "b": CONCRETE[1], "w": G[2], "g": G[4], "f": BRICK[4]}


def pigeons(p: Pix, spots, flight, motion: bool):
    """Pigeons by day: one perched at each of `spots` (its feet's row and column), and one flying the path `flight`
    round the roof, wings up and down, a step at a time on a slow loop."""
    pal = _pigeon_pal()
    for i, (x, y) in enumerate(spots):
        art = PIGEON_SIT if i % 2 == 0 else [r[::-1] for r in PIGEON_SIT]
        p.sprite(x, y - len(art) + 1, art, pal, 1, "base", reuse=True)
    if flight:
        keys = []
        for n, art in (("up", PIGEON_UP), ("down", PIGEON_DOWN)):
            key = ("pigeon", n)
            if key not in p.syms:
                p.symbol(key, {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if ch in pal})
            keys.append(key)
        if motion:
            p.fly(keys, flight, 30.0, z=16, flap=0.3)
        else:
            p.use(keys[0], *flight[0], "near")


# --------------------------------------------------------------------------- the footers and the links
# A heart painted on the brick in red, 7 by 6: its lobes lit on the left, a fleck of the sky's white on the upper lobe.
HEART = [".wL.LM.", "wLMMMmd", "LMMmmdd", ".Mmmdd.", "..mdd..", "...d..."]


def heart(p: Pix, x, y, L="base"):
    """The heart in BUILT WITH (heart) BY: painted red on the brick, its lobes lit on the left, a fleck of white."""
    pal = {"w": CLOUD[6], "L": BRICK[6], "M": BRICK[5], "m": BRICK[4], "d": BRICK[2]}
    p.sprite(x, y, HEART, pal, 1, L, reuse=True)


def hazard(p: Pix, x0, y0, w, h, period=5, L="base"):
    """The graphic scale's bar as a steel beam painted in hazard stripes, a cab's yellow and black slanting by turns,
    `period` wide, lit along the top and in shade along the foot."""
    Y, K = RAMP["taxi"], COAT
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.25 else 1 if f < 0.75 else 2
        for xx in range(x0, x0 + w):
            yellow = ((xx - x0 + yy - y0) // period) % 2 == 0
            p.px(xx, yy, (Y[6], Y[4], Y[2])[band] if yellow else (K[4], K[2], K[0])[band], L)


# The links' icons, 9 by 7, one for each link in turn: the water tower, the helicopter, the skyline and the long coat's
# dark glasses.
ICONS = {
    "tower": ["...rr....", "..rRRr...", ".tTTTTtt.", ".tTtTtTt.", ".tTTTTtt.", "..l...l..", ".l.l.l.l."],
    "heli": ["kkkkkkkk.", "....k....", "..wkkkk..", ".wWkOOkkk", ".wwkOOk..", "..kkkk...", ".kkkkkk.."],
    "skyline": ["...g.....", "..gG..b..", "..gGg.bB.", "bBgYgbbB.", "bBgGgbYBb", "bYgGgbbBb", "bbgggbbbb"],
    "shades": [".........", "kkkkkkkkk", "kgGgkgGgk", "kggGkggGk", ".kkk.kkk.", ".........", "........."],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a button of blue glass, by day or by night: the skyline's windows lit in phosphor by
    night."""
    k = -1 if night else 0
    lit = FLAME[4] if night else GLASS[6]
    return {"r": ramp_at(CEDAR, 2 + k), "R": ramp_at(CEDAR, 4 + k), "t": ramp_at(CEDAR, 3 + k),
            "T": ramp_at(CEDAR, 5 + k), "l": STEEL[5 + k], "k": COAT[0], "w": GLASS[3], "W": GLASS[5],
            "O": ramp_at(OLIVE, 4 + k), "g": STEEL[4 + k], "G": STEEL[6 + k], "b": STEEL[3 + k], "B": STEEL[5 + k],
            "Y": lit, "#": ink}


# --------------------------------------------------------------------------- the fight on the roof
# The man in the long coat in bullet time, 33 by 29, facing left toward the gun: his knees bent forward over his
# planted feet, his body leaning far back from the bullets, his head thrown back, one arm flung up and back and the
# other swinging down behind him, and his coat falling from his shoulders to the roof. Hair (q h H), skin (o e s S),
# the coat's black leather (k x c C), his trousers (P p r) and his shoes (N n).
NEO = [
    ".............oo..................",
    "............oSeo.................",
    "............oeeck................",
    ".............kxcckk..............",
    "..............kxccxk.............",
    "...............kxcxk.............",
    "................kxxxk....ooo.....",
    ".................kccxk..oSSso....",
    ".................kccxkkoSSHHhq...",
    "..................kcCCccsHHhhq...",
    "................kkCCCCcsehhhhq...",
    "...............kCCCCccCcxchhhq...",
    ".............kkCCCCccxccxcckq....",
    "...........kkCCCCccxxxcccccck....",
    "..........kCCCCcccxxxxcccxcck....",
    "..........kCCcccxxxxcccxcccck....",
    ".......kkkcPPpxxxxxCccccxccck....",
    "....kkkPPPPpprrxxkCCcccccxcxk....",
    "...kPpPppprrrrxkkCCcccccccxxk....",
    "...kprrrrrrrrkkCCcccccxcccxxk....",
    "...kprrpprrkkkCCcccccxxccccxSeo..",
    "...kppkpprk.kCCccccccxxcccccko...",
    "...kpprkppk.kCcccccccxcccccxk....",
    "...kpprkpprkkCcccccccxxccccxxk...",
    "...kpprkpprkkCccccccccxccccxxk...",
    "..kkpprkkprkkCcccccccccxcccxxxk..",
    ".knnnnrNnnnkkCccccccccxxccccxxxk.",
    ".knnnnknnnk.kCcccccccxxcccccxxxxk",
    "..kkkk.kkk...kkkkkkkkkkkkkkkkkkkk",
]
# The agent standing square to the right, aiming, 18 by 32: his hair (q h H), his face (o e s S) behind dark glasses
# (v), his suit (k x c C) over a white shirt (T) and a dark tie (u), his trousers and shoes, and the pistol (g).
AGENT = [
    ".....qqq..........",
    "....qHHhq.........",
    "...qHhhhhq........",
    "...qhhsSSo........",
    "...qhvvvvv........",
    "....hsSsso........",
    "....oesseo........",
    ".....oeeo.........",
    "...kkCTTukk.......",
    "..kCCcTucxcxxkk...",
    "..kCcccucxccccSgg.",
    "..kCcccucxxxxkkgk.",
    "..kCcccucxk.......",
    "..kCccccuxk.......",
    "..kCccccxxk.......",
    "..kCcccxxxk.......",
    "..kCcccxxxk.......",
    "..ksccccxxk.......",
    "..koCccxxxk.......",
    "...kPPpprrk.......",
    "...kPPpprrk.......",
    "...kPPpprrk.......",
    "...kPPpprrk.......",
    "...kPPpkprk.......",
    "...kPpkkprk.......",
    "...kPpk.kprk......",
    "...kPpk.kprk......",
    "...kPpk.kprk......",
    "..kPpk..kprk......",
    "..kPpk..kprk......",
    "..kNnnk.kNnnk.....",
    "..knnnnk.knnnnk...",
]
GUN = (16, 10)      # where the agent's muzzle is on his art


def _person(art, night: bool) -> dict:
    """A figure's cells in the coat's black and the hand's skin, and by night the moon's light laid along the edges of
    his clothes that face it, up and to the left; his face keeps its tone."""
    pal = dict(_leap_pal(night), T=C["white"], u=COAT[0], g=STEEL[4])
    cells = {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if pal.get(ch)}
    if night:
        cloth = set(COAT)
        for (i, j), c in list(cells.items()):
            if c in cloth and ((i - 1, j) not in cells or (i, j - 1) not in cells):
                cells[(i, j)] = MOON[1]
    return cells


def figure(p: Pix, name: str, x, g, night: bool) -> tuple:
    """The man in the long coat bending back (`NEO`) or the agent aiming (`AGENT`), standing on row g from column x,
    drawn once and laid. Returns the box he takes."""
    art = NEO if name == "neo" else AGENT
    key = (name, night)
    if key not in p.syms:
        p.symbol(key, _person(art, night))
    top = g - len(art) + 1
    p.use(key, x, top)
    return (x, top, x + len(art[0]), g + 1)


def bullets(p: Pix, x0, x1, y, night: bool, motion: bool):
    """The bullets in bullet time between x0 and x1 along row y: three slugs of brass flying from the gun, each with
    rings of rippling air trailing behind it, fainter as they go; in a moving header they creep on a unit at a time,
    as time slowed would let them, and round again on a slow loop. Laid as one group, so the loop moves them all."""
    q = Pix(p.w, p.h)
    Y, R = RAMP["taxi"], RAMP["rust"]
    ring = GLASS[6] if night else GLASS[3]
    n = 3
    room = max(1, x1 - x0 - 6)
    for i in range(n):
        bx = x0 + 4 + round(room * (i + 0.5) / n)
        by = y + (0, -2, 1)[i]
        for d, ry, a in ((3, 2, 0.6), (6, 3, 0.42), (9, 4, 0.26)):
            cx = bx - d
            for yy in range(by - ry, by + ry + 2):
                t = (yy + 0.5 - (by + 0.5)) / (ry + 0.5)
                if abs(t) > 1:
                    continue
                dx = round(1.4 * math.sqrt(max(0.0, 1 - t * t)))
                for xx in {cx - dx, cx + dx}:
                    q.apx(xx, yy, ring, a, "base")
        q.px(bx, by, Y[6])
        q.px(bx + 1, by, Y[5])
        q.px(bx + 2, by, R[5])
        q.px(bx, by + 1, Y[3])
        q.px(bx + 1, by + 1, Y[2])
        q.px(bx + 2, by + 1, R[3])
    body = q._paths(q.layers["base"])
    steps = 6
    moving = (f'<g>{body}<animateTransform attributeName="transform" type="translate" '
              f'values="{";".join(f"{i} 0" for i in range(steps))}" dur="{num(steps * 1.5)}s" '
              f'repeatCount="indefinite" calcMode="discrete"/></g>') if motion else body
    p.raw(3, moving, body)


def glass_tower(p: Pix, x0, x1, top, base, night: bool, motion: bool, seed: int = 5) -> tuple:
    """A tower of blue mirror glass from x0 to x1, its roof at row `top` under its crown and its foot at row `base`:
    its face ruled in floors and bays by its mullions, the face toward the light carrying the sky down it, brightest
    high up, and the face turned from it a tone deeper, a crown of two setbacks and a mast on top with its aviation
    light. By night the glass goes dark, a window here and there burns phosphor, a few going on and off, and the
    aviation light blinks. The glass and its mullions are shapes and a pattern, so a tall tower costs no more than a
    short one. Returns its box."""
    k = -1 if night else 0
    w = x1 - x0
    split = x0 + round(w * 0.62)
    crown = top + 12
    G = GLASS
    sky, lit, turned, mullion = (G[2], G[1], G[0], G[0]) if night else (G[5], G[4], G[2], G[3])
    h = base - crown + 1
    reach = round(h * 0.6)
    p.shapes["base"].append(
        f'<rect x="{x0}" y="{crown}" width="{split - x0}" height="{h}" fill="{lit}"/>'
        f'<rect x="{split}" y="{crown}" width="{x1 - split}" height="{h}" fill="{turned}"/>'
        f'<polygon points="{x0} {crown} {split} {crown} {split} {crown + reach // 3} {x0} {crown + reach}" '
        f'fill="{sky}"/>')
    gid = f"gt{len(p.defs)}"
    p.defs.append(f'<pattern id="{gid}" x="{x0 + 1}" y="{crown + 2}" width="3" height="4" '
                  f'patternUnits="userSpaceOnUse"><path stroke="{mullion}" d="M0 .5h3M.5 1v3"/></pattern>')
    p.shapes["base"].append(f'<rect x="{x0 + 1}" y="{crown + 2}" width="{w - 2}" height="{h - 2}" '
                            f'fill="url(#{gid})"/>')
    p.vline(x0, crown, base + 1, ramp_at(G, 6 + k))
    p.vline(x1 - 1, crown, base + 1, ramp_at(G, 1 + k))
    p.hline(x0, x1, crown, ramp_at(G, 6 + k))
    for i, (a, b, rows) in enumerate(((2, 2, 5), (5, 5, 4))):
        yy0 = crown - (5 if i == 0 else 9)
        p.rect(x0 + a, yy0, w - a - b, rows, ramp_at(STEEL, 4 + k) if i == 0 else ramp_at(STEEL, 3 + k))
        p.hline(x0 + a, x1 - b, yy0, ramp_at(STEEL, 6 + k))
        p.vline(x1 - b - 1, yy0 + 1, yy0 + rows, ramp_at(STEEL, 1 + k))
    mx = x0 + w // 2
    p.vline(mx, top + 1, crown - 9, ramp_at(STEEL, 4 + k))
    p.vline(mx + 1, top + 4, crown - 9, ramp_at(STEEL, 2 + k))
    if night:
        L = p.blink(3) if motion else "base"
        p.px(mx, top, FLAME[6], L)
        p.px(mx, top - 1, FLAME[4], L)
        rnd = random.Random(seed)
        for wy in range(crown + 4, base - 1, 4):
            for wx in range(x0 + 2, x1 - 2, 3):
                roll = rnd.random()
                if roll < (0.12 if p.lite else 0.24):
                    Lw = p.twinkle(wx + wy) if (motion and roll < 0.04) else "base"
                    p.px(wx, wy, FLAME[3] if roll < 0.08 else FLAME[1], Lw)
                    p.px(wx + 1, wy, FLAME[2] if roll < 0.08 else FLAME[1], Lw)
    else:
        p.px(mx, top, STEEL[5])
    return (x0, top - 1, x1, base + 1)


def roof_deck(p: Pix, x0, x1, g, night: bool):
    """The roof the fight is on, from x0 to x1: the parapet across the back, its brick face under its concrete coping,
    lit along the coping's top, and the deck of concrete in front of it to the rule, paler toward the parapet, its
    slabs' joints running toward us."""
    k = -2 if night else 0
    Q, B = CONCRETE, BRICK
    p.hline(x0, x1, g - 12, ramp_at(Q, 6 + k))
    p.hline(x0, x1, g - 11, ramp_at(Q, 3 + k))
    for yy in range(g - 10, g - 6):
        p.hline(x0, x1, yy, ramp_at(B, (3 if yy % 2 else 2) + k))
    p.hline(x0, x1, g - 6, ramp_at(Q, 1 + k))
    for yy in range(g - 5, g + 1):
        p.hline(x0, x1, yy, ramp_at(Q, (5 if yy < g - 3 else 4) + k))
    for jx in range(x0 + 9, x1, 24):
        p.vline(jx, g - 5, g + 1, ramp_at(Q, 3 + k))


def bullet_time(p: Pix, x0, x1, top, g, night: bool, motion: bool, city: bool = True) -> tuple:
    """The fight on the roof from x0 to x1, rising from the rule at row g to row `top`: at the right a tower of blue
    glass rising full height behind the parapet; across the back the city's far towers; on the deck the agent at the
    left, aiming, and at the right the man in the long coat bending back from the bullets, which fly between them
    rippling the air. Returns its box."""
    tx0 = x1 - 29
    if city:
        far_city(p, x0 + 1, tx0 - 1, g - 13, night, motion, seed=13)
    glass_tower(p, tx0, x1, top, g - 13, night, motion)
    roof_deck(p, x0, x1, g, night)
    agent = figure(p, "agent", x0 + 1, g - 1, night)
    neo = figure(p, "neo", x1 - 47, g - 1, night)
    bullets(p, agent[0] + GUN[0] + 2, neo[0] + 8, agent[1] + GUN[1], night, motion)
    return (x0, top - 1, x1, g + 1)


# --------------------------------------------------------------------------- the water tower on the roof
def roof_tower(p: Pix, x0, x1, top, g, night: bool, motion: bool) -> tuple:
    """A strip's hero from x0 to x1, rising its full height from the rule at row g to row `top`: a building's top, its
    brick face lit window by window by night, its parapet's coping, and on its roof the great water tower on its
    stilts, its legs as long as the room allows; a pigeon on the tower's roof by day, a searchlight's lamp on the
    parapet burning by night. Returns its box."""
    room = g - top
    legs = max(8, min(18, room - 40))
    roof = top + 35 + legs
    if roof < g - 3:
        facade(p, x0, x1, roof + 3, g, night, seed=9, lit=0.4)
    parapet(p, x0, x1, roof, night)
    tw = 31
    tx = x0 + max(1, (x1 - x0 - tw) // 2 + 3)
    tip = water_tower(p, tx, roof + 1, night, legs=legs, w=tw, tank=20)
    lamp(p, x0 + 3, roof - 7, night)
    if not night:
        pigeons(p, [(tx + tw // 2 + 2, tip + 6)], None, motion)
    return (x0, tip, x1, g + 1)


# --------------------------------------------------------------------------- on a phone
def phone_jump(p: Pix, g, room, night: bool):
    """A phone's H1, the jump across the phone under the words, standing on the rule at row g in `room` rows: at the
    left the near tower with its water tower on its roof, at the right the far tower with its bulkhead and its
    searchlight and, where the rows allow, the helicopter hovering over it; the man in the long coat in the air
    between them, and the city far below."""
    w = p.w
    near = g - max(8, min(22, room - 36))
    far = g - max(14, min(24, room - 30))
    far_city(p, 40, w - 46, g, night, False, seed=17)
    facade(p, 4, 40, near + 3, g, night, seed=3, lit=0.45)
    parapet(p, 4, 40, near, night)
    water_tower(p, 7, near + 1, night, legs=max(4, min(8, room - 40)))
    lamp(p, 34, near - 7, night)
    facade(p, w - 44, w - 4, far + 3, g, night, seed=6, lit=0.5)
    parapet(p, w - 44, w - 4, far, night)
    bulkhead(p, w - 30, w - 13, far - 11, far, night)
    lamp(p, w - 9, far - 7, night)
    if room >= 50:
        helicopter(p, w - 52, g - room + 2, night, False, aim=far - 1)
    leaper(p, 44, near - 26, night, False)


# --------------------------------------------------------------------------- the footers and the links
FLOOR = 8           # how high the parapet stands over a footer's foot at the most, its coping on top
RISE = 3            # how much higher it stands where the cells leave it room
RUN = 18            # the fewest columns a rise runs
EMBLEM = (22, 18)   # the water tower and the lamp beside it: their width and height


def footing(p: Pix, night: bool, after: int = 0, emblem: bool = True):
    """A footer once its words are set: the parapet along its foot, courses of brick down to the frame's foot under a
    coping of concrete, lit along its top and shading the brick under it, as high as keeps a row clear of the lowest
    word; rising by RISE rows wherever the cells leave it room along RUN columns or more; and in the rightmost
    place from column `after` on where the cells leave the sky free, a small water tower on its stilts on the parapet
    with a searchlight's lamp beside it, burning phosphor by night."""
    w, h = p.w, p.h
    k = -2 if night else 0
    base = p.layers["base"]
    ledge = min(h - 2, max(h - FLOOR, max((b[3] for b in p.words), default=0) + 1))

    def free(x0, y0, x1, y1):
        return 5 <= x0 and x1 <= w - 5 and 5 <= y0 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0 - 1, x1 + 1) for y in range(y0, y1)
                    if base.get((x, y)) not in (None,))
    mark = None
    if emblem:
        ew, eh = EMBLEM
        top = ledge - RISE - eh
        mark = next(((x, top) for x in range(w - 6 - ew, max(5, after), -1) if free(x, top, x + ew, ledge - RISE)),
                    None)
    rise = [free(x, ledge - RISE - 1, x + 1, ledge) for x in range(w)]
    tops = [ledge] * w
    x = 5
    while x < w - 5:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - 5) if not rise[i]), w - 5)
        if b - x >= RUN or (mark and x <= mark[0] and mark[0] + EMBLEM[0] <= b):
            tops[x:b] = [ledge - RISE] * (b - x)
        x = b
    Q, B = CONCRETE, BRICK
    L = p.layer("foot", z=0.5)
    for x in range(EDGE, w - EDGE):
        t = tops[x]
        edge = (x > EDGE and tops[x - 1] > t) or (x < w - EDGE - 1 and tops[x + 1] > t)
        p.px(x, t, ramp_at(Q, (5 if edge else 6) + k), L)
        p.px(x, t + 1, ramp_at(Q, 4 + k), L)
        if t + 2 < h - 1:
            p.px(x, t + 2, ramp_at(B, 1 + k), L)
        for y in range(t + 3, h - 1):
            course = (y - t) % 3 == 0
            joint = (x + (0 if (y - t) // 3 % 2 else 3)) % 6 == 0
            p.px(x, y, ramp_at(B, (2 if course or joint else 3) + k), L)
    if mark:
        mx, top = mark
        water_tower(p, mx + 1, top + EMBLEM[1] - 1, night, legs=2, w=13, tank=6)
        lamp(p, mx + 17, top + EMBLEM[1] - 7, night)


def beam_top(p: Pix, x0, x1, y, night: bool):
    """A steel beam two rows deep from x0 to x1 at row y, its flange lit along its top and a rivet's head every six
    columns along its web, dark at its ends."""
    k = -1 if night else 0
    S = STEEL
    p.hline(x0, x1, y, ramp_at(S, 5 + k))
    p.hline(x0, x1, y + 1, ramp_at(S, 3 + k))
    for x in range(x0 + 3, x1 - 2, 6):
        p.px(x, y + 1, ramp_at(S, 6 + k))
        p.px(x + 1, y + 1, ramp_at(S, 1 + k))
    for x in (x0, x1 - 1):
        p.px(x, y, ramp_at(S, 2 + k))
        p.px(x, y + 1, ramp_at(S, 1 + k))


def rivets(p: Pix, x0, x1, y, night: bool, seed: int = 0):
    """A rule riveted every so often from x0 to x1 at row y: a rivet's head lit along its top, on the rule, where
    no word comes within two units of it."""
    k = -1 if night else 0
    S = STEEL
    for x in range(x0 + 6 + seed % 13, x1 - 4, 26):
        if not p.clear_of_words(x - 2, y - 3, x + 4, y + 3):
            continue
        p.px(x, y - 1, ramp_at(S, 6 + k))
        p.px(x + 1, y - 1, ramp_at(S, 4 + k))
        p.px(x, y, ramp_at(S, 3 + k))
        p.px(x + 1, y, ramp_at(S, 1 + k))


# --------------------------------------------------------------------------- the elements
def card_deco(p: Pix, x, y, w, h, night: bool, lid: bool):
    """A schematic's card made a panel of glass in a steel frame: a steel beam down its icon cell's edge, lit down its
    left with a rivet every four rows, and on its lid a steel bracket over each upper corner, riveted."""
    k = -1 if night else 0
    S = STEEL
    for yy in range(y + 1, y + h - 1):
        p.px(x + 10, yy, ramp_at(S, 5 + k))
        p.px(x + 11, yy, ramp_at(S, 6 + k) if (yy - y) % 4 == 2 else ramp_at(S, 3 + k))
        p.px(x + 12, yy, ramp_at(S, 1 + k))
    if lid:
        for fx, way in ((x - 1, 1), (x + w, -1)):
            for i in range(5):
                p.px(fx + way * i, y - 1, ramp_at(S, 5 + k))
                p.px(fx, y - 1 + i, ramp_at(S, 4 + k if way > 0 else 2 + k))
            p.px(fx + way, y, ramp_at(S, 6 + k))


def cable_lights(p: Pix, cells, night: bool):
    """What hangs on a wire made a steel cable: an aviation light every so often, under it where it runs level and
    beside it where it runs upright, its glass unlit by day and burning phosphor by night."""
    k = -1 if night else 0
    glass, glow = (FLAME[5], FLAME[3]) if night else (GLASS[5], GLASS[3])
    for i, (x, y, d) in enumerate(cells[6:-8]):
        if i % 14:
            continue
        if d == "h":
            p.px(x, y + 1, ramp_at(STEEL, 2 + k))
            p.px(x - 1, y + 2, glass)
            p.px(x, y + 2, glass)
            p.px(x - 1, y + 3, glow)
            p.px(x, y + 3, glow)
        else:
            p.px(x + 1, y, ramp_at(STEEL, 2 + k))
            p.px(x + 2, y, glass)
            p.px(x + 2, y + 1, glow)


def tower_bar(p: Pix, bx, top, bw, v, night: bool):
    """A week's commits as a tower of blue glass `bw` wide standing from row top + v up to row top: its face lit down
    its left and turned from the light down its right, ruled in floors every three rows, and its roof capped in steel;
    by night the glass goes dark and a window here and there burns phosphor."""
    k = -2 if night else 0
    base = top + v
    for yy in range(top, base):
        floor = (base - 1 - yy) % 3 == 2
        for xx in range(bx, bx + bw):
            u = (xx - bx) / max(1, bw - 1)
            tone = 5 if u < 0.2 else 4 if u < 0.62 else 3
            if floor:
                tone -= 2
            p.px(xx, yy, ramp_at(GLASS, tone + k))
        if night and not floor and (yy * 7) % 5 == 1:
            p.px(bx + 1 + (yy * 3) % max(1, bw - 2), yy, FLAME[2])
    p.hline(bx, bx + bw, top, ramp_at(STEEL, 5 + k // 2))


def mast(p: Pix, x, y, night: bool):
    """The mark by the busiest week's count: a mast with its aviation light, unlit glass by day and phosphor by
    night."""
    k = -1 if night else 0
    p.vline(x + 1, y + 2, y + 7, ramp_at(STEEL, 4 + k))
    p.hline(x, x + 3, y + 7, ramp_at(STEEL, 2 + k))
    lit, shade = (FLAME[5], FLAME[3]) if night else (GLASS[5], GLASS[3])
    p.px(x + 1, y, lit)
    p.px(x + 2, y, shade)
    p.px(x + 1, y + 1, shade)
    p.px(x + 2, y + 1, shade)


def steel_rim(p: Pix, arc, night: bool):
    """The dial's half ring made a ring of steel bent over it, lit along its upper edge, a rivet's head every few
    units round it."""
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        if int(s) % 7 == 3 and abs(o) < 0.45:
            return ramp_at(STEEL, 6 + k)
        return ramp_at(STEEL, max(1, min(5, round(1.6 + 3.4 * lam) + k)))
    tube(p, arc, 2.6, colour, outline=STEEL[0])


# The paints a file type's wrapper is in, by turns: brick in its courses, blue glass in its mullions, hazard stripes,
# concrete with its gravel showing and a steel deck plate.
PATTERNS = ("brick", "glass", "hazard", "concrete", "plate")


def wrapper(i: int, xx, yy, y0, lift: int, night: bool) -> str:
    """The colour at (xx, yy) of the `i`-th wrapper, its pattern one of PATTERNS by turns, `lift` steps lighter on its
    lit top row and darker along its foot."""
    k = (-1 if night else 0) + lift
    kind = PATTERNS[i % len(PATTERNS)]
    yy -= y0
    if kind == "brick":
        joint = yy % 3 == 0 or (xx + (3 if (yy // 3) % 2 else 0)) % 6 == 0
        return ramp_at(BRICK, (2 if joint else 4) + k)
    if kind == "glass":
        return ramp_at(GLASS, (1 if xx % 4 == 0 or yy % 4 == 0 else 4) + k)
    if kind == "hazard":
        return ramp_at(RAMP["taxi"], 4 + k) if ((xx + yy) // 3) % 2 == 0 else ramp_at(COAT, 2 + k)
    if kind == "concrete":
        return ramp_at(CONCRETE, (3 if (xx * 7 + yy * 5) % 11 == 0 else 5) + k)
    on = (xx + yy) % 4 == 0 and (xx // 2 + yy // 2) % 2 == 0
    return ramp_at(STEEL, (6 if on else 3) + k)


def flip_cell(q: Pix, ox, oy, night: bool):
    """The 11 by 15 cell a counter's digit turns on, a flap of a split-flap board: black, its split across its
    middle, lit along its top and edged in steel."""
    k = -1 if night else 0
    q.rect(ox, oy, 11, 15, COAT[2])
    q.box(ox, oy, 11, 15, ramp_at(STEEL, 2 + k))
    q.hline(ox + 1, ox + 10, oy + 1, COAT[4])
    q.hline(ox + 1, ox + 10, oy + 7, COAT[0])
    q.px(ox, oy + 7, ramp_at(STEEL, 4 + k))
    q.px(ox + 10, oy + 7, ramp_at(STEEL, 4 + k))


def girder(p: Pix, x0, x1, y, night: bool):
    """The steel girder the releases hang from, up to today: its flange lit along its top and a rivet every eight
    columns along its web."""
    k = -1 if night else 0
    S = STEEL
    p.hline(x0, x1, y, ramp_at(S, 5 + k))
    p.hline(x0, x1, y + 1, ramp_at(S, 3 + k))
    for x in range(x0 + 4, x1 - 2, 8):
        p.px(x, y + 1, ramp_at(S, 6 + k))
    p.px(x0, y + 1, ramp_at(S, 1 + k))


PAINTS = ("taxi", "go", "plum", "brick")       # the paints a release's sign is in, by turns


def sign(p: Pix, x, gy, kind: str, night: bool, i: int = 0):
    """A release hung from the girder at x, whose top row is gy, as a sign on two hangers: a big release's seven wide
    and a release's five, painted by turns a cab's yellow, a street sign's green, an awning's plum and brick, a white
    band across it; a patch a work light in its cage; one still to come a sign drawn in outline; and the repository's
    founding its cornerstone of concrete."""
    k = -1 if night else 0
    S = STEEL
    if kind == "made":
        p.rect(x - 3, gy + 3, 7, 5, ramp_at(CONCRETE, 4 + k))
        p.hline(x - 3, x + 4, gy + 3, ramp_at(CONCRETE, 6 + k))
        p.vline(x + 3, gy + 4, gy + 8, ramp_at(CONCRETE, 2 + k))
        p.hline(x - 1, x + 2, gy + 5, ramp_at(CONCRETE, 2 + k))
        p.vline(x, gy + 2, gy + 3, ramp_at(S, 3 + k))
        return
    if kind == "minor":
        p.px(x, gy + 2, ramp_at(S, 3 + k))
        p.hline(x - 1, x + 2, gy + 3, ramp_at(S, 4 + k))
        lit = FLAME[4] if night else GLASS[5]
        p.px(x - 1, gy + 4, lit)
        p.px(x, gy + 4, lit)
        p.px(x + 1, gy + 4, ramp_at(S, 2 + k))
        p.hline(x - 1, x + 2, gy + 5, ramp_at(S, 2 + k))
        return
    paint = RAMP[PAINTS[i % len(PAINTS)]]
    half, foot = (3, gy + 9) if kind == "big" else (2, gy + 8)
    for hx in (x - half + 1, x + half - 1):
        p.px(hx, gy + 2, ramp_at(S, 3 + k))
    for yy in range(gy + 3, foot + 1):
        for xx in range(x - half, x + half + 1):
            edge = xx in (x - half, x + half) or yy in (gy + 3, foot)
            if kind == "next":
                if edge:
                    p.px(xx, yy, ramp_at(paint, 4 + k))
                continue
            tone = 5 if yy == gy + 3 else 2 if xx == x + half or yy == foot else 4
            p.px(xx, yy, ramp_at(paint, tone + k))
    if kind != "next":
        p.hline(x - half + 1, x + half, gy + 5, ramp_at(CLOUD, 6 + k))


def searchlight(p: Pix, x, y, night: bool):
    """The mark at today's end of the girder: a searchlight on it, its face to the sky, burning phosphor by night and
    its glass catching the day."""
    k = -1 if night else 0
    S = STEEL
    p.rect(x, y - 3, 3, 3, ramp_at(S, 3 + k))
    p.px(x, y - 3, ramp_at(S, 5 + k))
    p.hline(x, x + 3, y - 4, FLAME[6] if night else GLASS[5])
    p.px(x + 1, y - 5, FLAME[3] if night else GLASS[4])
    p.px(x + 1, y - 6, (FLAME[2] if night else GLASS[4]) + ":0.5")


AVATARS = ("glass", "brick", "go", "plum")     # the paints a contributor's pane is in, by turns


def pane(p: Pix, cx, cy, i: int, person: dict, night: bool):
    """A contributor as a pane in a steel frame, painted in their colour, lit along its upper left, their initials on
    it in white; a bot is an agent, dark glasses and all."""
    k = -1 if night else 0
    S = STEEL
    bot = not person.get("initials")
    R = STEEL if bot else RAMP[AVATARS[i % len(AVATARS)]]
    p.rect(cx - 7, cy - 7, 15, 15, ramp_at(S, 2 + k))
    p.hline(cx - 7, cx + 8, cy - 7, ramp_at(S, 5 + k))
    p.vline(cx - 7, cy - 7, cy + 8, ramp_at(S, 4 + k))
    for yy in range(cy - 6, cy + 7):
        for xx in range(cx - 6, cx + 7):
            lit = (xx - cx) + (yy - cy) < -5
            p.px(xx, yy, ramp_at(R, (4 if lit else 2) + k))
    if bot:
        art = ["..qqqqq..", ".qhhhhhq.", ".hsSSSso.", ".vvvvvvv.", ".osSSsso.", "..oeeeo..", "...kkk..."]
        pal = dict(_leap_pal(night), k=COAT[0])
        p.sprite(cx - 4, cy - 4, art, pal, 1, "base", reuse=True)
        return
    p.text(cx - 3, cy - 2, str(person["initials"])[:2], C["white"], "35", shadow=R[0])


def brass(p: Pix, cx, cy, r0, r1, n: int, night: bool):
    """The seal's ring of brass round its pressed centre, lit along its upper left, a rivet's head at its rim every
    so often."""
    k = -1 if night else 0
    Y = RAMP["taxi"]
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if r0 <= d <= r1:
                a = math.atan2(yy + 0.5 - cy, xx + 0.5 - cx)
                lam = -math.cos(a + math.pi * 0.25)
                rivet = d > r1 - 1.6 and int(((a + math.pi) / (2 * math.pi)) * n * 2) % 2 == 0
                c = ramp_at(STEEL, 6 + k) if rivet else ramp_at(Y, (5 if lam > 0.35 else 4 if lam > -0.35 else 3) + k)
                p.px(xx, yy, c)


def billboard(p: Pix, night: bool):
    """The placard as a billboard on a roof: its face pale by day and the night's own dark by night, framed in steel
    four units deep, lit along its top and left and riveted, the whole canvas its face."""
    k = -1 if night else 0
    w, h = p.w, p.h
    p.rect(0, 0, w, h, DUSK[2] if night else CLOUD[5])
    S = STEEL
    for i, tone in enumerate((0, 5, 3, 1)):
        p.hline(i, w - i, i, ramp_at(S, tone + k) if tone else S[0])
        p.hline(i, w - i, h - 1 - i, ramp_at(S, (1 if i else 0) + k))
        p.vline(i, i, h - i, ramp_at(S, tone + k) if tone else S[0])
        p.vline(w - 1 - i, i, h - i, ramp_at(S, (2 if i else 0) + k))
    for x in range(10, w - 8, 12):
        p.px(x, 1, ramp_at(S, 6 + k))
        p.px(x, h - 2, ramp_at(S, 4 + k))
    for y in range(10, h - 8, 12):
        p.px(1, y, ramp_at(S, 6 + k))
        p.px(w - 2, y, ramp_at(S, 4 + k))
