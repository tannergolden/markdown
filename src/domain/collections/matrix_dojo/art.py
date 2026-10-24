# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Dojo set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is a wall of shoji: honey paper by day behind a lattice of pale hinoki kumiko, a sliding panel's stiles
standing up through it, and by night the same paper glowing deep indigo with the city's light behind it, the kumiko
standing out against it in silhouette. Black lacquered beams frame it, gold fittings at their joints, and along the
foot runs the edge of a tatami, its black brocade worked in gold; a shimenawa of twisted straw hangs in swags along a
header's top with its zigzags of white paper. Titles are black lacquer edged in gold leaf and brushed, the dry brush
fraying a stroke's end here and there; by night they are gold leaf catching the light. Cherry petals drift across
every header's sky. The headers' pieces: the fighter in a dark gi at the top of his flying kick, the afterimages of
his leap trailing behind him; his opponent waiting in his guard; byobu laid in gold leaf and painted with the great
wave or the great pine; a great round window onto the city, and the shoji slid open on a garden where a pagoda rises
among cherry blossom; paper lanterns written in the code and stone lanterns that by night burn phosphor and pool
their light on the tatami. The footers' floor of tatami and its dais of hinoki, the alcove with its hanging scroll, and
the lacquer, gold, silk, bamboo, straw and paper every link, badge and element is made of. Everything is shaded from
the one light in the upper left on the set's own ramps, and every light is the hand's phosphor. A drawing made lighter
thins only texture: the petals, the wave's striations, the pine's furrows, the towers' shading and their lit windows,
and the light the lanterns throw, keeping every piece and all the motion."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, Paint, Pix, fold, num, tube
from .. import rain
from .palette import C, GLOW, NIGHT_GLOW, NIGHT_SKY, PANE_H, PANE_W, PANE_X, PANE_Y, RAMP, X

PAPER, HINOKI, WASHI, LACQUER = RAMP["paper"], RAMP["hinoki"], RAMP["washi"], RAMP["lacquer"]
GOLD, TATAMI, STRAW, SHIDE = RAMP["gold"], RAMP["tatami"], RAMP["straw"], RAMP["shide"]
GI, INDIGO, HAIR, STONE = RAMP["gi"], RAMP["indigo"], RAMP["hair"], RAMP["stone"]
WOOD, SAKURA = RAMP["wood"], RAMP["sakura"]
RED, FLAME, SKY, MOON = RAMP["red"], RAMP["flame"], RAMP["sky"], RAMP["moon"]
EDGE = 4          # the frame's width down each side and along the foot
STILES = 4        # the panes between one sliding panel's stiles and the next
LOOP = 4.0        # seconds a fighter's idle takes, round and round: within the hand's four to eight


def ramp_at(ramp: list, i: int) -> str:
    """A ramp's tone `i`, held to the ramp's ends, so a night's darkening never wraps round to its lightest."""
    return ramp[max(0, min(len(ramp) - 1, i))]


# --------------------------------------------------------------------------- the paper
def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the shoji, its paper laid behind a lattice of kumiko a unit wide that parts it
    into panes, and every few panes a sliding panel's stile standing up through it, lit along its left edge. By day
    the paper is honey ivory and the kumiko pale hinoki; by night the paper glows deep indigo with the city's light
    behind it, paling toward the floor and brightest across the middle of every pane, and the kumiko stand out against
    it in silhouette."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
        p.defs.append(f'<pattern id="{uid}g" x="{PANE_X}" y="{PANE_Y}" width="{PANE_W}" height="{PANE_H}" '
                      f'patternUnits="userSpaceOnUse"><rect x="{GLOW[0]}" y="{GLOW[1]}" width="{PANE_W - 2 * GLOW[0]}" '
                      f'height="{PANE_H - 2 * GLOW[1]}" fill="{WASHI[6]}" fill-opacity="{num(GLOW[2])}"/></pattern>')
        p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}g)"/>')
        bar, lit, shade = X["kumiko_night"], WASHI[1], X["kumiko_night"]
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
        bar, lit, shade = C["kumiko"], HINOKI[6], HINOKI[4]
    p.defs.append(f'<pattern id="{uid}k" x="{PANE_X}" y="{PANE_Y}" width="{PANE_W}" height="{PANE_H}" '
                  f'patternUnits="userSpaceOnUse"><path stroke="{bar}" d="M0 .5h{PANE_W}M.5 1v{PANE_H - 1}"/>'
                  f'</pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}k)"/>')
    span = STILES * PANE_W
    p.defs.append(f'<pattern id="{uid}t" x="{PANE_X - 1}" width="{span}" height="8" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{lit}" d="M.5 0v8"/><path stroke="{shade}" d="M2.5 0v8"/></pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}t)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: a kumiko where one crosses the row, else the paper; by night its band, and across
    the middle of a pane the band with the city's glow through it."""
    r = (y - PANE_Y) % PANE_H
    if r == 0:
        return X["kumiko_night"] if night else C["kumiko"]
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        i = next(i for i in range(n) if y < edges[i + 1] or i == n - 1)
        return NIGHT_GLOW[i] if GLOW[1] <= r < PANE_H - GLOW[1] else NIGHT_SKY[i]
    return C["paper"]


# --------------------------------------------------------------------------- the frame
# A gold fitting where a post meets the beam, 5 by 5: the petals of a rosette round its boss, lit on its upper left.
FITTING = [".lgl.", "lgLgd", "gLwgd", "lggdd", ".ddd."]


def fitting(p: Pix, x, y, night: bool, L="base"):
    """A kugikakushi, the gold fitting that hides a nail where a post meets the beam."""
    k = -1 if night else 0
    pal = {"l": ramp_at(GOLD, 4 + k), "g": ramp_at(GOLD, 3 + k), "L": ramp_at(GOLD, 5 + k), "w": GOLD[6],
           "d": ramp_at(GOLD, 1 + k)}
    p.sprite(x, y, FITTING, pal, 1, L, reuse=True)


def frame(p: Pix, night: bool, header: bool = False):
    """The border: a post of black lacquer down each side and a beam along the top, each lit along its upper and left
    edges with its foot in shade, a gold fitting at each joint; and along the foot the edge of a tatami, a row of its
    green-gold rush over the band of black brocade that binds it, worked in a lozenge of gold."""
    w, h = p.w, p.h
    L = LACQUER
    for x0 in (0, w - EDGE):
        p.vline(x0, 0, h, L[0])
        p.vline(x0 + 1, 1, h - 1, L[5] if x0 == 0 else L[4])
        p.vline(x0 + 2, 1, h - 1, L[3])
        p.vline(x0 + 3, 1, h - 1, L[1])
    p.hline(0, w, 0, L[0])
    p.hline(1, w - 1, 1, L[5])
    p.hline(2, w - 2, 2, L[3])
    p.hline(3, w - 3, 3, L[1])
    k = -1 if night else 0
    p.hline(EDGE, w - EDGE, h - 4, ramp_at(TATAMI, 5 + k))
    uid = "fb"
    lozenge = (f'<path stroke="{L[1]}" d="M0 .5h8M0 1.5h8"/>'
               f'<path stroke="{ramp_at(GOLD, 3 + k)}" d="M3 .5h2M2 1.5h1M5 1.5h1"/>'
               f'<path stroke="{ramp_at(GOLD, 2 + k)}" d="M0 1.5h1M7 1.5h1"/>')
    p.defs.append(f'<pattern id="{uid}" x="{EDGE}" y="{h - 3}" width="8" height="2" patternUnits="userSpaceOnUse">'
                  f'{lozenge}</pattern>')
    p.shapes["base"].append(f'<rect x="{EDGE}" y="{h - 3}" width="{w - 2 * EDGE}" height="2" fill="url(#{uid})"/>')
    p.hline(EDGE, w - EDGE, h - 1, L[0])
    for x in (0, w - 5):
        fitting(p, x, 0, night)
        fitting(p, x, h - 5, night)


# --------------------------------------------------------------------------- the shimenawa
# A shide, a zigzag of paper folded down from the rope, 4 by 11: its lit face (a) and its shaded edge (b).
SHIDE_ART = ["aab.", "aab.", ".aab", ".aab", "aab.", "aab.", ".aab", ".aab", "aab.", "aab.", ".ab."]


def _twist(p: Pix, uid: str, night: bool) -> str:
    """The rope's twist as a pattern tile: strands three tones deep running across it on the slant, a unit further
    along every row, so a run of rope laid at any height carries the twist on."""
    k = -2 if night else 0
    tones = (ramp_at(STRAW, 5 + k), ramp_at(STRAW, 4 + k), ramp_at(STRAW, 2 + k))
    rows: dict = {}
    for r in range(6):
        c = 0
        while c < 6:
            tone = tones[((c + r) // 2) % 3]
            n = next((i for i in range(c + 1, 6) if tones[((i + r) // 2) % 3] != tone), 6) - c
            rows.setdefault(tone, []).append(f"M{c} {r}h{n}v1h-{n}z")
            c += n
    body = "".join(f'<path fill="{col}" d="{"".join(ds)}"/>' for col, ds in rows.items())
    p.defs.append(f'<pattern id="{uid}" width="6" height="6" patternUnits="userSpaceOnUse">{body}</pattern>')
    return uid


def shimenawa(p: Pix, x0, x1, night: bool, box, marked: bool, span: int = 41, sag: int = 3, top: int = 5):
    """The shimenawa along a header's top, from x0 to x1: a rope of twisted straw four rows thick, lit along its top
    and dark along its foot, hung in swags from the beam, a knot where each swag meets the next, a zigzag of white
    paper hanging from the low point of each swag and a tassel of loose straw either side of it. Where the month's
    mark hangs at the top centre the rope parts and is knotted either side of its box, two units clear; with no mark
    it runs on unbroken. The twist is a pattern laid along the rope in one path, a block for each run of it at one
    height, so the rope costs little however long. A drawing made lighter keeps the rope, its knots and its paper and
    lets the tassels go."""
    a, _, b, _ = box
    runs = [(x0, a - 1), (b + 1, x1)] if marked else [(x0, x1)]
    k = -2 if night else 0
    tid = _twist(p, "rope", night)
    blocks = []
    for r0, r1 in runs:
        n = max(1, round((r1 - r0) / span))
        width = (r1 - r0) / n
        for i in range(n):
            s0, s1 = r0 + i * width, r0 + (i + 1) * width
            level = {}
            for x in range(round(s0), round(s1)):
                t = (x + 0.5 - s0) / (s1 - s0)
                level[x] = top + round(sag * math.sin(math.pi * t))
            xs = sorted(level)
            start = xs[0]
            for x in xs[1:] + [None]:
                if x is not None and level[x] == level[start]:
                    continue
                end = (x if x is not None else xs[-1] + 1)
                yc = level[start]
                blocks.append((start, yc, end - start))
                start = x
            mid = round((s0 + s1) / 2)
            _shide(p, mid - 2, top + sag + 3, night)
            for tx in (() if p.lite else (mid - 6, mid + 6)):
                yt = level.get(tx, top + sag) + 3
                for j, dx in enumerate((-1, 0, 1)):
                    p.vline(tx + dx, yt, yt + (4, 6, 4)[j], ramp_at(STRAW, 3 + k) if dx else ramp_at(STRAW, 4 + k))
            if i:
                _knot(p, round(s0), top, night)
        for end in (r0 + 1, r1 - 2):
            _knot(p, end, top, night, tail=True)
    d, at = [], (0, 0)
    for x, y, w in blocks:
        d.append(f"m{x - at[0]} {y - at[1]}h{w}v2h-{w}z")
        at = (x, y)
    rid = f"{tid}{len(p.defs)}"
    p.defs.append(f'<path id="{rid}" d="M{"".join(d)[1:]}"/>'.replace(" -", "-"))
    p.shapes["base"].append(f'<use href="#{rid}" y="-1" fill="{ramp_at(STRAW, 5 + k)}"/>'
                            f'<use href="#{rid}" y="1" fill="{ramp_at(STRAW, 1 + k)}"/>'
                            f'<use href="#{rid}" fill="url(#{tid})"/>')


# A knot of straw binding the rope, 3 by 6: lit down its left (l) and at its top (L), its body (m) and its foot (d);
# and where the rope ends, the short tail of straw hanging from it (t lit, T, s in shade).
KNOT = ["Lmm", "lmm", "lmm", "lmm", "lmm", "ddd"]
TAIL = ["tTs", "tTs", "tTs", ".Ts", "..s"]


def _knot(p: Pix, x, top, night: bool, tail: bool = False):
    """A knot of straw binding the rope (`KNOT`), lit at its upper left; where the rope ends, a short tail of straw
    hanging from it (`TAIL`). Each is drawn once and laid again."""
    k = -2 if night else 0
    pal = {"L": ramp_at(STRAW, 5 + k), "l": ramp_at(STRAW, 4 + k), "m": ramp_at(STRAW, 2 + k),
           "d": ramp_at(STRAW, 1 + k), "t": ramp_at(STRAW, 4 + k), "T": ramp_at(STRAW, 3 + k),
           "s": ramp_at(STRAW, 2 + k)}
    p.sprite(x - 1, top - 2, KNOT, pal, 1, "base", reuse=True)
    if tail:
        p.sprite(x - 1, top + 4, TAIL, pal, 1, "base", reuse=True)


def _shide(p: Pix, x, y, night: bool):
    """A shide, a zigzag of white paper hanging from the rope, lit along its left edge."""
    k = -3 if night else 0
    p.sprite(x, y, SHIDE_ART, {"a": ramp_at(SHIDE, 6 + k), "b": ramp_at(SHIDE, 3 + k)}, 1, "base", reuse=True)


# --------------------------------------------------------------------------- the titles
def _ends(ch: str) -> list:
    """The ends of a letter's strokes, in its face's units: a unit with one neighbour along its stroke, as
    (col, row, dx, dy), the way the stroke runs out toward (dx, dy)."""
    g = FONTS["57"][0][ch]
    cells = {(col, r) for r, cols in enumerate(g[1]) for col in cols}
    out = []
    for (c, r) in sorted(cells):
        n = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (c + dx, r + dy) in cells]
        if len(n) == 1:
            out.append((c, r, -n[0][0], -n[0][1]))
    return out


# The gold leaf's bands down a letter, a band a row of the face: brightest just under its top where the light runs
# along it, darkening toward its foot, as burnished leaf on a curve takes the light.
LEAF = (4, 5, 4, 4, 3, 3, 3, 2, 2)
LEAF_PAINT = Paint("leaf", lambda r, c, scale, night: GOLD[LEAF[min(len(LEAF) - 1, r // scale)]])
RING_LIT = ((-1, 0), (0, -1), (-1, -1))                  # where the ring round a letter lies toward the light
RING_SHADE = ((1, 0), (0, 1), (1, 1), (1, -1), (-1, 1))   # and away from it
CAST = ((X["shade_ink"], 0.2), (LACQUER[0], 0.55))      # the shadow the letters cast down and right, by day and night
SIDES = {"r": (-1, 0), "d": (0, -1), "l": (1, 0), "u": (0, 1)}   # each mask: the line moved so a unit shows through
#                                                                  it where its neighbour that way is a letter's too


def _at(dx, dy) -> str:
    return (f' x="{dx}"' if dx else "") + (f' y="{dy}"' if dy else "")


def lacquer_title(p: Pix, x, y, s, scale, night: bool) -> int:
    """A title in letters of black lacquer edged in gold leaf, brushed, by day; by night in gold leaf ringed in
    lacquer, a glint catching every other letter now and then.

    The line's letters are set once, from the face's own glyphs, and laid again
    for every part: the shadow they cast two units down and right; the ring a unit
    round every letter, lit above and left and in shade below and right, laid as
    the line moved a unit each way; then the letters
    themselves in the tone of their lower and right edges, again where the units to
    their right and below are a letter's too in the shine down their left edges,
    and again in their body's tone where the unit to their left is a letter's too,
    each through masks of the line moved a unit; a gleam lies on the upper corner
    of every stroke. By day the body is lacquer, its shine down its left and deep
    along its foot, the ring gold, and at some strokes' ends the dry brush frays, a
    bristle's streak of the paper showing through at the tip; by night the body is
    gold leaf in bands (`LEAF`), ringed in lacquer. A long title costs little more
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
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    if not placed:
        return max(0, w)
    tid = f"lt{len(p.defs)}"
    letters = "".join(f'<use href="#{p.syms[("glyph", "57", ch)]}"'
                      + (f' x="{num((gx - x) / scale)}"' if gx > x else "") + "/>" for ch, gx in placed)
    p.defs.append(f'<g id="{tid}" transform="translate({x} {y}) scale({scale})">{letters}</g>')
    box = f'maskUnits="userSpaceOnUse" x="{x - 2}" y="{y - 2}" width="{w + 4}" height="{rows * scale + 4}"'
    for name, (dx, dy) in SIDES.items():
        p.defs.append(f'<mask id="{tid}{name}" {box}><use href="#{tid}"{_at(dx, dy)} stroke="{C["white"]}"/></mask>')
    L, G = LACQUER, GOLD
    if night:
        lit, shade, edge, gloss, body = L[2], L[0], G[1], G[5], f"url(#{p._pattern(LEAF_PAINT, scale, True)})"
    else:
        lit, shade, edge, gloss, body = G[5], G[2], L[0], L[3], L[1]

    def masked(names, colour):
        inner = f'<use href="#{tid}" stroke="{colour}"/>'
        for n in names:
            inner = f'<g mask="url(#{tid}{n})">{inner}</g>'
        return inner
    ring = (f'<g stroke="{shade}">' + "".join(f'<use href="#{tid}"{_at(dx, dy)}/>' for dx, dy in RING_SHADE)
            + f'</g><g stroke="{lit}">' + "".join(f'<use href="#{tid}"{_at(dx, dy)}/>' for dx, dy in RING_LIT) + "</g>")
    body = f'<use href="#{tid}" stroke="{edge}"/>' + masked("rd", gloss) + masked("rdl", body)
    cast = f'<use href="#{tid}" x="2" y="2" stroke="{CAST[night][0]}" stroke-opacity="{num(CAST[night][1])}"/>'
    p.raw(0.1, cast + ring + body, cast + ring + body)
    if not night and scale >= 3:
        fray = p.layer("fray", z=0.2)
        for ch, gx in placed:
            rnd = random.Random(ord(ch) * 7 + scale)
            for (c, r, dx, dy) in _ends(ch):
                if rnd.random() < 0.5:
                    continue
                x0, y0 = gx + c * scale, y + r * scale
                tip = scale - 1
                if dx:      # a stroke running out across: the bristles fray along its rows at the tip
                    xt = x0 + (tip if dx > 0 else 0)
                    for row in range(y0 + 1, y0 + scale - 1, 2):
                        p.px(xt, row, C["paper"], fray)
                        if scale >= 4:
                            p.px(xt - dx, row, L[4], fray)
                else:       # running out up or down: the bristles fray down its columns at the tip
                    yt = y0 + (tip if dy > 0 else 0)
                    for col in range(x0 + 1, x0 + scale - 1, 2):
                        p.px(col, yt, C["paper"], fray)
                        if scale >= 4:
                            p.px(col, yt - dy, L[4], fray)
    if scale >= 3:
        gleam = p.layer("gleam", z=0.25)
        for ch, gx in placed:
            cells = {(c, r) for r, cs in enumerate(glyphs[ch][1]) for c in cs}
            for (c, r) in cells:
                if (c - 1, r) not in cells and (c, r - 1) not in cells:
                    p.px(gx + c * scale, y + r * scale, G[6] if night else L[5], gleam)
                    p.px(gx + c * scale + 1, y + r * scale, G[5] if night else L[4], gleam)
                    p.px(gx + c * scale, y + r * scale + 1, G[5] if night else L[4], gleam)
    if night and scale >= 3:
        for i, (ch, gx) in enumerate(placed[::2]):
            col = min(glyphs[ch][1][0])
            sx, sy = gx + col * scale + 1, y + 1
            Lt = p.twinkle(i)
            p.px(sx, sy, C["white"], Lt)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(sx + dx, sy + dy, G[6], Lt)
    return w


# --------------------------------------------------------------------------- the byobu
# The great wave painted across the folding screen, 44 by 46: its wall of water rising from the lower left and curling
# over in a hook, its claws of foam hanging from the lip, the spray flying off its crest, a small wave rising at the
# right, the sea along the foot and the far mountain in the trough between, its snow on its peak. W the wave and w the
# streaks down its face, F its foam and f the foam's shadow, S the sea, M the mountain and n its snow; the gold leaf
# the screen is laid in shows wherever there is no paint.
WAVE = [
    "............................................",
    "...............................F......F.....",
    "...........................F................",
    "........................F.........F.........",
    ".....................................F......",
    ".....................FFFFfffffFF............",
    "...................FFffffWWWWfffffF.........",
    ".................FFfWWWWWWWWWWWWWffF....F...",
    "................FfWWWWWWWWWWWWWWWWWffF......",
    "..............FffWWWWWWWWWWWWWWWWWWWffF.....",
    ".............FfWWWWwwwwwww.....WWWWWWffF..F.",
    "............FWWWWwwwwww...........WWWWWf....",
    "...........FfWWwwwwwwW.............WWWWfF..F",
    "..........FfWWwwwwwwW...............WWWWfF..",
    ".........FWWWwwwwwwW.................WWWff..",
    "........FWWWwwwwwwW..................WWWWf..",
    ".......fWWWWwWwWwW...................WWWWf..",
    ".......WWWWwWwwwWW....................WWWWF.",
    "......WWWWwwwwwwW.....................WWWWF.",
    "......WWWWwWwWwW......................WWWWF.",
    ".....WWWWwwWwWwW......................WWWWF.",
    "....WWWWWwWwWwwW......................WWWW..",
    "....WWWWWwWwWwW......................WWWWf..",
    "...WWWWWWwWwWwW.....................WWWWWF..",
    "...WWWWWwwwwwwW....................WWWWWWFf.",
    "...WWWWWwWwWwWW...................WWWWWW.Ff.",
    "..WWWWWWwWwWwW.................Ff.WWWWWFf...",
    "..WWWWWWwWwWwW................Ff..Ff.FfFf...",
    "..WWWWWWwWwWwW...............Ff..Ff.Ff.Ff...",
    "..WWWWWwwWwWwW..................Ff..Ff......",
    ".WWWWWWwWwwWwW..................Ff..........",
    ".WWWWWWwWwWwWW..............nn..............",
    ".WWWWWWwWwWwWW.............nnnn.............",
    ".WWWWWWwWwWwWW.............MMMM.............",
    "WWWWWWWwWwWwW.............MMMMMM............",
    "WWWWWWWwWwWwW............MMMMMMMM...........",
    "WWWWWWWwWwWwW............MMMMMMMM...........",
    "WWWWWWWwWwWwW...........MMMMMMMMMM...FFWWWFF",
    "WWWWWWWwWwWwW..........MMMMMMMMMMMM.FWWWWWWW",
    "WWWWWWWwWwWwW.........MMMMMMMMMMMMMFWWWWWWWW",
    "WWWWWWWwWwWwW...................FFWWWWWWWWWW",
    "WWWWWWWwWwWwW..FFFFFFFFFFFFFFFFFSFWWWWWWWWWW",
    "WWWWWWWwWwWwWFFSSSSSSSSSSSSSSSSSWWWWWWWWWWWW",
    "WWWWWWWwWwWwWSSSSSSSSSSSSSSSSSSWWWWWWWWWWWWW",
    "WWWWWWWwWwWwWSSSSSSSSSSSSSSSSSSWWWWWWWWWWWWW",
    "WWWWWWWwWwWwWSSSSSSSSSSSSSSSSSWWWWWWWWWWWWWW",
]
PANELS = 4        # the byobu's folds
PANEL_W = 12      # each panel's width, its frame shared with the next
# The bands of gold cloud drifting across the screen's sky, each (left, right, row) from the screen's top left.
KASUMI = ((2, 22, 5), (20, 43, 13), (1, 15, 21))
SUN = (34, 6, 6)   # the red sun over the wave: its centre from the screen's top left, and its radius


def screen(p: Pix, x, top, g, night: bool, panels: int, panel_w: int, art: str = "") -> tuple:
    """A byobu, a folding screen of `panels` panels laid in gold leaf, each `panel_w` wide with its frame shared with
    the next, standing on the tatami from column x with its feet on row g and its head at row `top`, its picture
    painted across the panels inside their frames: "wave", the great wave under the red sun (`wave`), or "pine", the
    great pine (`pine`). The panels fold
    in a zigzag, so every other one turns from the light a tone deeper, and the leaf is laid in squares whose seams
    show faintly (a pattern under the picture, so a tall screen costs no more than a short one); each panel is framed
    in black lacquer, gold hinges where it meets the next, a band of brocade runs along the screen's head, and the
    screen throws its shadow on the paper behind it. By night the gold sinks a tone, catching what light there is.
    Returns its box."""
    k = -1 if night else 0
    w = panels * (panel_w - 1) + 1
    h = g - top + 1
    for yy in range(top + 2, g):
        p.px(x + w, yy, X["shade_ink"] + ":0.22")
        p.px(x + w + 1, yy, X["shade_ink"] + ":0.12")
    for lit in (True, False):
        pid = f"lf{int(lit)}{top}{'n' if night else ''}"
        leaf, seam = ramp_at(GOLD, (4 if lit else 3) + k), ramp_at(GOLD, (3 if lit else 2) + k)
        if not any(d.startswith(f'<pattern id="{pid}"') for d in p.defs):
            p.defs.append(f'<pattern id="{pid}" y="{top + 8}" width="8" height="6" patternUnits="userSpaceOnUse">'
                          f'<rect width="8" height="6" fill="{leaf}"/><path stroke="{seam}" d="M0 .5h8"/></pattern>')
        for n in range(panels):
            if (n % 2 == 0) == lit:
                x0 = x + n * (panel_w - 1)
                p.shapes["base"].append(f'<rect x="{x0 + 1}" y="{top + 3}" width="{panel_w - 2}" height="{h - 4}" '
                                        f'fill="url(#{pid})"/>')
    if art == "wave":
        wave(p, x, top, w, g, k)
    elif art == "pine":
        pine(p, x + 1, top + 3, x + w - 1, g, k, flip=True)
    for n in range(panels):
        x0 = x + n * (panel_w - 1)
        if n % 2:
            for yy in range(top + 3, g):
                p.px(x0 + 1, yy, X["shade_ink"] + ":0.18")
    for n in range(panels + 1):
        fx = x + n * (panel_w - 1)
        p.vline(fx, top, g + 1, LACQUER[1] if n in (0, panels) else ramp_at(GOLD, 1 + k))
        if 0 < n < panels:
            for hy in (top + 9, g - 9):
                p.px(fx, hy, ramp_at(GOLD, 5 + k))
    p.hline(x, x + w, top, ramp_at(LACQUER, 4 + k // 2))
    p.hline(x, x + w, top + 1, LACQUER[1])
    for bx in range(x + 1, x + w - 1):
        p.px(bx, top + 2, ramp_at(GOLD, 3 + k) if bx % 3 == 0 else LACQUER[2])
    p.hline(x, x + w, g, LACQUER[0])
    return (x, top, x + w, g + 1)


def kasumi(p: Pix, x0, y0, x1, y1, bands, k: int):
    """Bands of gold cloud drifting across a screen's sky, each (left, right, row) from (x0, y0), kept inside it."""
    for a, b, r in bands:
        yy = y0 + r
        for dy, (pad, tone) in enumerate(((2, 6), (0, 5), (1, 5), (3, 3))):
            if y0 <= yy + dy < y1:
                p.hline(max(x0, x0 + a + pad), min(x1, x0 + b - pad), yy + dy, ramp_at(GOLD, tone + k))


def wave(p: Pix, x, top, w, g, k: int):
    """The picture on the byobu of the great wave, `w` wide from column x, its head at row `top` and its feet on row
    g: bands of gold cloud across its sky, the red sun, and under them the great wave (`WAVE`), sinking with the
    gold by night (`k`)."""
    x0, y0, x1, y1 = x + 1, top + 3, x + w - 1, g
    kasumi(p, x0 - 1, y0, x1, y1, KASUMI, k)
    sx, sy, sr = SUN
    cx, cy = x + sx + 0.5, top + 3 + sy + 0.5
    for (px, py) in _disc(cx, cy, sr):
        d = (px + 0.5 - cx + 2) ** 2 + (py + 0.5 - cy + 2) ** 2
        p.px(px, py, ramp_at(RED, (4 if d < 10 else 3 if d < 50 else 2) + k))
    pal = {"W": ramp_at(INDIGO, 3 + k), "w": ramp_at(INDIGO, 5 + k), "F": ramp_at(SHIDE, 6 + k),
           "f": ramp_at(SHIDE, 3 + k), "S": ramp_at(INDIGO, 2 + k), "M": ramp_at(INDIGO, 4 + k),
           "n": ramp_at(SHIDE, 5 + k)}
    if p.lite:                      # a drawing made lighter lets the wave's striations and the foam's shade go
        pal["w"], pal["f"] = pal["W"], pal["F"]
    wx, wy = x + (w - len(WAVE[0])) // 2, g - len(WAVE)
    for j, row in enumerate(WAVE):
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c and y0 <= wy + j < y1 and x < wx + i < x + w - 1:
                p.px(wx + i, wy + j, c)


def byobu(p: Pix, x, top, g, night: bool) -> tuple:
    """The byobu of the great wave: four panels painted with the great wave under the red sun (see `screen`).
    Returns its box."""
    return screen(p, x, top, g, night, PANELS, PANEL_W, "wave")


# The great pine painted across a byobu, as the painters of the screens drew it on gold: its trunk rising from a rock
# at the lower left and leaning out, bent back on itself, and its boughs reaching out level, each ending in a pad of
# needles laid flat as clouds. Each bough: where it leaves the trunk (a share of the way up it), which way it reaches,
# how far (a share of the screen's width) and how big its pad is (a share of the width, and rows).
BOUGHS = ((0.42, 1, 0.48, 0.24, 6), (0.55, -1, 0.2, 0.17, 5), (0.68, 1, 0.38, 0.22, 5), (0.8, -1, 0.16, 0.15, 4),
          (0.9, 1, 0.24, 0.2, 5), (1.0, 1, 0.06, 0.18, 5))
PINE_KASUMI = ((0.04, 0.42, 0.1), (0.52, 0.98, 0.3), (0.0, 0.3, 0.62))   # its clouds: (left, right, row) as shares


def _curve(pts, n: int) -> list:
    """`n` points along a Catmull-Rom spline through `pts`, end to end."""
    out = []
    m = len(pts) - 1
    for i in range(n):
        t = i / (n - 1) * m
        j = min(m - 1, int(t))
        u = t - j
        p0, p1, p2, p3 = pts[max(0, j - 1)], pts[j], pts[j + 1], pts[min(m, j + 2)]
        out.append(tuple(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u
                               + (-a + 3 * b - 3 * c + d) * u * u * u) for a, b, c, d in zip(p0, p1, p2, p3)))
    return out


def pine(p: Pix, x0, y0, x1, y1, k: int, seed: int = 3, flip: bool = False):
    """The great pine (`BOUGHS`) painted in the box from (x0, y0) to (x1, y1): gold clouds across its sky, a rock at
    its foot with moss on it, its trunk of bark lit along its left and furrowed, and its pads of needles dark green,
    lit along their tops, each tufted with needles and shaded under its rim. Flipped, it rises at the right and
    reaches out to the left."""
    rnd = random.Random(seed)
    w, h = x1 - x0, y1 - y0

    def at(f):
        """A share of the width across from the side the pine rises at."""
        return x1 - f * w if flip else x0 + f * w
    kasumi(p, x0, y0, x1, y1, [(round(a * w), round(b * w), round(r * h)) for a, b, r in PINE_KASUMI], k)
    W, M, S = WOOD, RAMP["moss"], STONE
    base = (at(0.24), y1 - 3)
    spine = [base, (at(0.36), y1 - 0.3 * h), (at(0.2), y1 - 0.58 * h), (at(0.38), y1 - 0.8 * h),
             (at(0.5), y0 + 0.08 * h)]
    path = _curve(spine, max(12, h * 2))
    for i, (cx, cy) in enumerate(path):
        t = i / (len(path) - 1)
        half = 3.4 - 2.2 * t
        for dx in range(math.floor(-half), math.ceil(half) + 1):
            xx, yy = round(cx + dx), round(cy)
            u = (dx + half) / (2 * half)
            tone = 4 if u < 0.25 else 3 if u < 0.6 else 2 if u < 0.85 else 1
            if (xx + yy * 3) % 7 == 0 and 0.2 < u < 0.8 and not p.lite:
                tone -= 1
            p.px(xx, yy, ramp_at(W, tone + k))
    for at, way, reach, pad, rows in BOUGHS:
        sx, sy = path[min(len(path) - 1, round(at * (len(path) - 1)))]
        ex = sx + (-way if flip else way) * reach * w
        ey = sy - 0.04 * h - rnd.random() * 3
        bough = _curve([(sx, sy), ((sx + ex) / 2, sy - 3), (ex, ey)], max(6, round(abs(ex - sx) * 1.5)))
        for (bx, by) in bough:
            p.px(round(bx), round(by), ramp_at(W, 2 + k))
            p.px(round(bx), round(by) + 1, ramp_at(W, 1 + k))
        rx, ry = pad * w, rows
        cx, cy = ex, ey - ry * 0.4
        for yy in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for xx in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                d = ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2
                lump = 0.12 * math.sin((xx - cx) * 1.3 + seed)
                if d > 1 + lump or not (x0 <= xx < x1 and y0 <= yy < y1):
                    continue
                v = (yy + 0.5 - (cy - ry)) / (2 * ry)
                tone = 5 if v < 0.18 else 4 if v < 0.4 else 3 if v < 0.72 else 2
                if (xx * 5 + yy * 3) % 9 == 0 and tone > 2 and not p.lite:
                    tone -= 1
                p.px(xx, yy, ramp_at(M, tone + k))
            if yy == math.floor(cy - ry) + 1:
                for xx in range(math.floor(cx - rx) + 2, math.ceil(cx + rx) - 1, 3):
                    if x0 <= xx < x1 and y0 <= yy - 1:
                        p.px(xx, yy - 1, ramp_at(M, 5 + k))
        under = math.ceil(cy + ry)
        for xx in range(math.floor(cx - rx * 0.8), math.ceil(cx + rx * 0.8)):
            if x0 <= xx < x1 and under < y1:
                p.px(xx, under, ramp_at(M, 1 + k))
    rx = 0.2 * w
    for yy in range(y1 - 7, y1):
        for xx in range(math.floor(base[0] - rx), math.ceil(base[0] + rx)):
            d = ((xx + 0.5 - base[0]) / rx) ** 2 + ((yy + 0.5 - y1) / 7) ** 2
            if d <= 1 and x0 <= xx < x1:
                top = d > 0.55 and yy < y1 - 4
                p.px(xx, yy, ramp_at(M, 3 + k) if top else ramp_at(S, (4 if xx < base[0] else 2) + k))


# --------------------------------------------------------------------------- the pagoda
def pagoda(p: Pix, cx, base, height, night: bool, motion: bool = False, phase: int = 2):
    """A pagoda standing on row `base` at column cx, `height` rows tall to the tip of its spire, of as many storeys
    as its height holds at nine rows or so a storey (an odd number, three to nine, five for a strip): each
    storey narrower than the one under it, walls of white plaster between vermilion posts and a dark opening, under a
    roof of grey tiles lit along its ridge, its eaves turning up at their tips; over the topmost roof the spire of
    gilt bronze, ringed, with its finial. By night it stands dark against the sky, a lamp burning phosphor in each
    storey's opening, flickering."""
    k = -2 if night else 0
    spire = max(9, min(16, round(height * 0.2)))
    n = max(3, min(9, round((height - spire) / 9)))
    n -= 1 - n % 2                                  # an odd number of storeys, as a pagoda has
    th = (height - spire) / n
    Lf = p.flicker(phase) if (night and motion) else "base"
    for i in range(n):
        yb, yt = base - round(i * th), base - round((i + 1) * th)
        hb = round(9 - i * 6 / max(1, n - 1))
        hr = hb + 4 + (1 if i == 0 else 0)
        roof = 3
        for yy in range(yt + roof, yb + 1):
            for xx in range(cx - hb, cx + hb + 1):
                edge = xx in (cx - hb, cx + hb)
                c = ramp_at(RED, 3 + k) if edge else ramp_at(SHIDE, (5 if xx < cx else 4) + k)
                p.px(xx, yy, c)
        door = max(1, hb // 3)
        for yy in range(yt + roof + 1, yb):
            for xx in range(cx - door, cx + door + 1):
                c = FLAME[3 if yy > yt + roof + 1 else 4] if night else LACQUER[1]
                p.px(xx, yy, c, Lf if night else "base")
        p.hline(cx - hr + 2, cx + hr - 1, yt, ramp_at(STONE, 3 + k))
        p.hline(cx - hr + 1, cx + hr, yt + 1, ramp_at(STONE, 1 + k))
        p.hline(cx - hr, cx + hr + 1, yt + 2, ramp_at(STONE, 2 + k))
        p.px(cx - hr - 1, yt + 1, ramp_at(STONE, 3 + k))
        p.px(cx + hr + 1, yt + 1, ramp_at(STONE, 2 + k))
        p.hline(cx - hr + 1, cx + hr, yt + 3, ramp_at(WOOD, 1 + k))
        if night:
            p.halo(cx + 0.5, (yt + yb) / 2 + 1, hb + 2, th * 0.6, FLAME[3], (0.04, 0.08), L="pool", shape=True)
    top = base - round(n * th)
    for yy in range(top - spire, top):
        p.px(cx, yy, ramp_at(GOLD, (4 if (top - yy) % 3 else 2) + k))
        if (top - yy) % 3 == 0 and top - yy < spire - 3:
            p.px(cx - 1, yy, ramp_at(GOLD, 3 + k))
            p.px(cx + 1, yy, ramp_at(GOLD, 2 + k))
    p.px(cx, top - spire - 1, ramp_at(GOLD, 6 + k))


def _blossom(p: Pix, cx, cy, rx, ry, k: int, x0, x1, seed: int):
    """A cherry tree in blossom seen far off: a cloud of pink lit along its top and deeper under it, on a dark trunk,
    kept between columns x0 and x1."""
    rnd = random.Random(seed)
    for yy in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for xx in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2
            if d > 1 + 0.15 * math.sin(xx * 1.7 + yy) or not x0 <= xx < x1:
                continue
            v = (yy - cy + ry) / (2 * ry)
            tone = 5 if v < 0.3 else 4 if v < 0.65 else 3
            if rnd.random() < 0.12:
                tone += 1 if tone < 5 else -1
            p.px(xx, yy, ramp_at(SAKURA, tone + k))
    for yy in range(round(cy + ry * 0.6), round(cy + ry * 1.5)):
        if x0 <= round(cx) < x1:
            p.px(round(cx), yy, ramp_at(WOOD, 1 + k))


def pagoda_window(p: Pix, x0, x1, top, g, night: bool, motion: bool, seed: int = 6) -> tuple:
    """The shoji slid open on the garden, an opening from column x0 to x1 with its lintel at row `top` and its sill on
    the tatami at row g, framed in dark hinoki lit along its left: through it the sky, pale blue by day and the
    night's indigo after dark with the code falling down it and the hand's moon; a pagoda (`pagoda`) rising nearly
    the opening's full height, cherry trees in blossom at its foot either side and the garden's moss under them.
    Returns the box it takes."""
    k = -2 if night else 0
    inner_top, inner_bot = top + 2, g - 2
    sky = p.layer("wsky", z=-9)
    for yy in range(inner_top, inner_bot + 1):
        t = (yy - inner_top) / max(1, inner_bot - inner_top)
        c = (WASHI[0] if t < 0.5 else WASHI[1]) if night else (SKY[3] if t < 0.35 else SKY[4] if t < 0.7 else SKY[5])
        p.hline(x0 + 2, x1 - 2, yy, c, sky)
    if night:
        cid = f"pw{len(p.defs)}"
        p.defs.append(f'<clipPath id="{cid}"><rect x="{x0 + 2}" y="{inner_top}" width="{x1 - x0 - 4}" '
                      f'height="{inner_bot - inner_top + 1}"/></clipPath>')
        kinds = rain.strands(p, FLAME, True, *((2, (2, 3)) if p.lite else (3, (3, 5))), seed=seed)
        rnd = random.Random(seed)
        loop = ((inner_bot - inner_top) + 6 * rain.PITCH) // rain.PITCH * rain.PITCH
        uses = []
        for i, x in enumerate(range(x0 + 3, x1 - 2 - rain.W, rain.COLUMN + 2)):
            head = inner_top + rnd.randrange(loop // rain.PITCH) * rain.PITCH
            uses.append(f'<use href="#{kinds[i % len(kinds)][0]}" x="{x}" y="{head}"/>')
        gid = f"{cid}g"
        p.defs.append(f'<g id="{gid}" opacity=".7">{"".join(uses)}</g>')
        steps = loop // rain.PITCH
        values = ";".join(f"0 {i * rain.PITCH}" for i in range(steps))
        moving = (f'<g clip-path="url(#{cid})"><g><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/>'
                  f'<animateTransform attributeName="transform" type="translate" values="{values}" '
                  f'dur="{num(steps * 0.14)}s" repeatCount="indefinite" calcMode="discrete"/></g></g>')
        still = f'<g clip-path="url(#{cid})"><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/></g>'
        p.raw(-8.5, moving if motion else still, still)
        mx, my = x1 - 9, inner_top + 8
        for (xx, yy) in _disc(mx, my, 3.2):
            d = (xx + 0.5 - mx + 0.9) ** 2 + (yy + 0.5 - my + 0.9) ** 2
            p.px(xx, yy, MOON[5] if d < 3 else MOON[4] if d < 7 else MOON[3])
        for q in _disc(mx, my, 5.2) - _disc(mx, my, 3.2):
            if x0 + 2 <= q[0] < x1 - 2 and inner_top <= q[1]:
                p.px(*q, WASHI[2], sky)
    cx = (x0 + x1) // 2
    height = inner_bot - inner_top - 3
    ground = inner_bot - 2
    for xx in range(x0 + 2, x1 - 2):
        p.px(xx, ground + 1, ramp_at(RAMP["moss"], 2 + k))
        p.px(xx, ground + 2, ramp_at(RAMP["moss"], 1 + k))
    w = x1 - x0
    _blossom(p, x0 + 2 + w * 0.12, ground - 5, w * 0.16, 5, k, x0 + 2, x1 - 2, seed)
    _blossom(p, x1 - 2 - w * 0.12, ground - 4, w * 0.15, 4.5, k, x0 + 2, x1 - 2, seed + 1)
    pagoda(p, cx, ground, height, night, motion)
    kk = -1 if night else 0
    for xx, lit in ((x0, True), (x1 - 2, False)):
        p.vline(xx, top, g + 1, ramp_at(WOOD, (5 if lit else 2) + kk))
        p.vline(xx + 1, top, g + 1, ramp_at(WOOD, (3 if lit else 1) + kk))
    p.hline(x0, x1, top, ramp_at(WOOD, 4 + kk))
    p.hline(x0, x1, top + 1, ramp_at(WOOD, 2 + kk))
    p.hline(x0, x1, g - 1, ramp_at(WOOD, 4 + kk))
    p.hline(x0, x1, g, ramp_at(WOOD, 1 + kk))
    return (x0, top, x1, g + 1)


# --------------------------------------------------------------------------- the round window
# The city beyond the round window, each tower (x from the window's left, width, height over its sill), back to front,
# for a window 44 across inside; a smaller or larger window scales them.
TOWERS = ((1, 7, 22), (7, 6, 33), (12, 8, 18), (19, 6, 28), (24, 8, 14), (31, 6, 25), (36, 7, 16))


def _disc(cx, cy, r) -> set:
    return {(x, y) for y in range(math.floor(cy - r), math.ceil(cy + r) + 1)
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1)
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r}


def window(p: Pix, cx, cy, r, night: bool, motion: bool, seed: int = 4):
    """A marumado, a round window in the shoji with its frame of dark wood, lit on its upper left, and through it the
    city: by day towers pale in the haze of a summer sky with a cloud drifting slowly across it; by night towers dark
    against the night with their windows lit in phosphor, a few going on and off, the hand's moon over them, and the
    code falling down the sky behind them. A drawing made lighter to fit its budget draws the towers flat, lights fewer
    of their windows and writes the code in fewer glyphs. Returns the box it takes."""
    rnd = random.Random(seed)
    inner = _disc(cx, cy, r - 2)
    ring = _disc(cx, cy, r) - inner
    x0, y0 = math.floor(cx - r), math.floor(cy - r)
    sill = math.ceil(cy + r - 2)
    sky_layer = p.layer("wsky", z=-9)
    top_y, bot_y = min(y for _, y in inner), max(y for _, y in inner)
    for (x, y) in inner:
        t = (y - top_y) / max(1, bot_y - top_y)
        if night:
            c = WASHI[0] if t < 0.45 else WASHI[1]
        else:
            c = SKY[3] if t < 0.3 else SKY[4] if t < 0.65 else SKY[5]
        p.px(x, y, c, sky_layer)
    if night:
        _window_rain(p, cx, cy, r - 2, seed)
        mx, my = cx - r * 0.38, cy - r * 0.42
        for (x, y) in _disc(mx, my, 3.2):
            if (x, y) in inner:
                d = (x + 0.5 - mx + 0.9) ** 2 + (y + 0.5 - my + 0.9) ** 2
                p.px(x, y, MOON[5] if d < 3 else MOON[4] if d < 7 else MOON[3])
        for q in ((round(mx), round(my) + 1), (round(mx) + 1, round(my) - 1)):
            p.px(*q, MOON[2])
        glow = _disc(mx, my, 5.2) - _disc(mx, my, 3.2)
        for q in glow & inner:
            p.px(*q, WASHI[2], sky_layer)
    f = (r - 2) / 22
    for dx, w, h in TOWERS:
        tx, w = x0 + 2 + round(dx * f), max(3, round(w * f))
        top = sill - round(h * f)
        for yy in range(top, sill + 1):
            for xx in range(tx, tx + w):
                if (xx, yy) not in inner:
                    continue
                if night:
                    c = WASHI[2] if p.lite else WASHI[4] if xx == tx else WASHI[3] if yy == top else WASHI[2]
                elif p.lite:
                    c = SKY[2] if xx == tx else SKY[1]
                else:
                    c = SKY[2] if xx == tx else SKY[1] if xx == tx + w - 1 else SKY[2] if yy == top else SKY[1]
                    c = SKY[3] if xx == tx and yy > top else c
                p.px(xx, yy, c)
        for wy in range(top + 2, sill - 1, 2):
            for wx in range(tx + 1, tx + w - 1, 2):
                if (wx, wy) not in inner:
                    continue
                if night:
                    roll = rnd.random()
                    if roll < (0.12 if p.lite else 0.45):
                        L = p.twinkle(wx + wy) if (motion and roll < 0.08) else "base"
                        p.px(wx, wy, FLAME[4] if roll < 0.12 else FLAME[2] if roll < 0.3 else FLAME[1], L)
                elif rnd.random() < 0.35:
                    p.px(wx, wy, SKY[3])
    if not night:
        _cloud(p, cx, cy, r - 2, inner, motion)
    k = -1 if night else 0
    for (x, y) in ring:
        nx, ny = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
        lit = nx * -0.6 + ny * -0.75
        outer = (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 > (r - 1) ** 2
        if outer:
            c = ramp_at(WOOD, 1 + k) if lit < 0.2 else ramp_at(WOOD, 3 + k)
        else:
            c = ramp_at(WOOD, 5 + k) if lit < -0.3 else ramp_at(WOOD, 2 + k) if lit > 0.3 else ramp_at(WOOD, 4 + k)
        p.px(x, y, c)
    for xx in range(x0 + 3, x0 + 2 * r - 2):
        if (xx, sill + 1) in ring or (xx, sill + 1) in inner:
            p.px(xx, sill + 1, ramp_at(WOOD, 1 + k))
    return (x0, y0, x0 + 2 * r + 1, y0 + 2 * r + 1)


def _cloud(p: Pix, cx, cy, r, inner, motion):
    """A summer cloud drifting across the window, a unit a step, round every thirty-six seconds; the still twin holds
    it where it starts. Clipped to the glass."""
    art = ["..aaa....", ".aaaaab..", "aaaaaaaab", ".bbbbbbb."]
    key = ("cloud",)
    if key not in p.syms:
        p.symbol(key, {(i, j): (SKY[6] if ch == "a" else SKY[5]) for j, row in enumerate(art)
                       for i, ch in enumerate(row) if ch != "."})
    sid = p.syms[key]
    cid = f"wcl{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}"/></clipPath>')
    y = round(cy - r * 0.55)
    x0, x1 = round(cx - r - 9), round(cx + r)
    start = round(cx - 6)
    if motion:
        steps = list(range(start, x1)) + list(range(x0, start))
        values = ";".join(f"{x} {y}" for x in steps)
        moving = (f'<g clip-path="url(#{cid})"><use href="#{sid}"><animateTransform attributeName="transform" '
                  f'type="translate" values="{values}" dur="{num(len(steps) * 1.0)}s" repeatCount="indefinite" '
                  f'calcMode="discrete"/></use></g>')
    else:
        moving = ""
    still = f'<g clip-path="url(#{cid})"><use href="#{sid}" x="{start}" y="{y}"/></g>'
    p.raw(-8, moving or still, still)


def _window_rain(p: Pix, cx, cy, r, seed):
    """The code falling down the night sky behind the towers, in the round window's glass: short streams of the rain's
    glyphs, the column of them drawn once and laid twice so the loop never shows its seam, clipped to the glass."""
    kinds = rain.strands(p, FLAME, True, *((2, (2, 3)) if p.lite else (3, (3, 5))), seed=seed)
    cid = f"wr{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}"/></clipPath>')
    rnd = random.Random(seed)
    x0, y0 = math.floor(cx - r), math.floor(cy - r)
    loop = (2 * round(r) + 6 * rain.PITCH) // rain.PITCH * rain.PITCH
    uses = []
    for i, x in enumerate(range(x0 + 1, x0 + 2 * round(r) - rain.W, rain.COLUMN + 1)):
        sid, _ = kinds[i % len(kinds)]
        head = y0 + rnd.randrange(loop // rain.PITCH) * rain.PITCH
        uses.append(f'<use href="#{sid}" x="{x}" y="{head}"/>')
    gid = f"{cid}g"
    p.defs.append(f'<g id="{gid}" opacity=".8">{"".join(uses)}</g>')
    steps = loop // rain.PITCH
    values = ";".join(f"0 {i * rain.PITCH}" for i in range(steps))
    moving = (f'<g clip-path="url(#{cid})"><g><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/>'
              f'<animateTransform attributeName="transform" type="translate" values="{values}" '
              f'dur="{num(steps * 0.14)}s" repeatCount="indefinite" calcMode="discrete"/></g></g>')
    still = f'<g clip-path="url(#{cid})"><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/></g>'
    p.raw(-8.5, moving, still)


# --------------------------------------------------------------------------- the paper lantern
# A chochin of white paper on its ribs of bamboo, 11 by 19: its caps of black lacquer (k, lit K), the paper (P lit,
# p, q in shade) and its ribs (b), the tassel under it (t); the code's glyph is brushed on its middle.
CHOCHIN = [
    "...kkkkk...",
    "..kKKKKkkk.",
    ".bPPPPPPppb",
    "pPPPPPPPppq",
    "pPPPPPPPppq",
    "bbbbbbbbbbb",
    "pPPPPPPPppq",
    "pPPPPPPPppq",
    "bbbbbbbbbbb",
    "pPPPPPPPppq",
    "pPPPPPPPppq",
    "bbbbbbbbbbb",
    "pPPPPPPPppq",
    ".bPPPPPPppb",
    "..kKKKKkkk.",
    "...kkkkk...",
    ".....t.....",
    "....ttt....",
    "....t.t....",
]


def chochin(p: Pix, x, y, night: bool, motion: bool, glyph: str = "ki", phase: int = 1, cord: int = 4) -> tuple:
    """A paper lantern hanging from the beam on its cord, its top-left at (x, y): white paper on bamboo ribs between
    caps of black lacquer, the code's glyph brushed on it in sumi, a red tassel under it. By night it burns phosphor
    through its paper, flickering, the glyph a shadow on the glow, and its light falls round it. Returns where its
    light is."""
    k = -1 if night else 0
    p.vline(x + 5, cord, y, LACQUER[2])
    if night:
        pal = {"k": LACQUER[1], "K": LACQUER[3], "P": FLAME[5], "p": FLAME[4], "q": FLAME[3], "b": FLAME[3],
               "t": RED[2]}
    else:
        pal = {"k": LACQUER[1], "K": LACQUER[4], "P": SHIDE[6], "p": SHIDE[4], "q": SHIDE[3], "b": SHIDE[3],
               "t": RED[3]}
    paper_cells = {(i, j) for j, row in enumerate(CHOCHIN) for i, ch in enumerate(row) if ch in "Ppqb"}
    Lf = p.flicker(phase) if (night and motion) else "base"
    for j, row in enumerate(CHOCHIN):
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                p.px(x + i, y + j, c, Lf if (i, j) in paper_cells else "base")
    for (i, j) in rain.cells(glyph):
        p.px(x + 3 + i, y + 4 + j, FLAME[1] if night else LACQUER[1], Lf)
    light = (x + 5.5, y + 8.5)
    if night:
        p.halo(light[0], light[1], 9, 12, FLAME[3], (0.04, 0.08, 0.14))
    else:
        p.px(x + 4, y + 16, ramp_at(RED, 5 + k))
    return light


# --------------------------------------------------------------------------- the stone lantern
# A kasuga lantern of granite, 15 by 31: the jewel on its head (j), the roof with its corners curling up (r, lit R,
# its underside u), the fire box with its windows (w, the window's frame f), the platform under it (t), the post with
# its rings (o) and the base (b); lit faces in capitals, shade in d.
LANTERN = [
    ".......j.......",
    "......jJj......",
    "......jjj......",
    ".....rrRrr.....",
    "...rrRRRRrrr...",
    "R.rrRRRRRrrrr.r",
    "RrRRRRRrrrrrrrr",
    ".uuuuuuuuuuuuu.",
    "...fffffffff...",
    "...fwwwfwwwfd..",
    "...fwwwfwwwfd..",
    "...fwwwfwwwfd..",
    "...fwwwfwwwfd..",
    "...fffffffffd..",
    "..ttTTTTttttd..",
    "..ddddddddddd..",
    "......oOod.....",
    "......oOod.....",
    "......oOod.....",
    ".....ooOood....",
    "......oOod.....",
    "......oOod.....",
    "......oOod.....",
    "......oOod.....",
    "......oOod.....",
    ".....ooOood....",
    "....bbbBbbbd...",
    "...bbBBBbbbbd..",
    "..bbBBBBbbbbbd.",
    ".bbbbbbbbbbbbbd",
    ".ddddddddddddd.",
]
LANTERN_LIGHT = (7.5, 10.5)     # the middle of its fire box


def lantern(p: Pix, x, g, night: bool, motion: bool, phase: int = 0, glow: bool = True) -> tuple:
    """The stone lantern standing on the floor at row g from column x: granite lit on its upper and left faces, moss
    on its roof by day; by night its fire box burns phosphor, flickering, its light thrown round it on the paper and
    in a pool on the tatami at its foot, unless `glow` is False or the drawing is made lighter. Returns where its
    light is."""
    top = g - len(LANTERN) + 1
    k = -2 if night else 0
    S = STONE
    face, lit, shade = ramp_at(S, 3 + k), ramp_at(S, 5 + k), ramp_at(S, 1 + k)
    pal = {"j": ramp_at(S, 4 + k), "J": ramp_at(S, 6 + k), "r": face, "R": lit, "u": shade, "f": face,
           "w": S[0] if not night else None, "t": face, "T": lit, "o": face, "O": lit, "b": face, "B": lit, "d": shade}
    p.sprite(x, top, LANTERN, pal)
    if not night:
        for mx, my in ((3, 5), (4, 4), (9, 5), (10, 6), (2, 6), (6, 29), (7, 28), (12, 28)):
            p.px(x + mx, top + my, TATAMI[3])
    light = (x + LANTERN_LIGHT[0], top + LANTERN_LIGHT[1])
    if night:
        Lf = p.flicker(phase) if motion else "base"
        for j in range(9, 13):
            for i in (4, 5, 6, 8, 9, 10):
                p.px(x + i, top + j, FLAME[5] if j == 9 else FLAME[4], Lf)
        if not glow or p.lite:      # a drawing made lighter keeps the fire and lets the light it throws go
            return light
        p.halo(light[0], light[1], 20, 17, FLAME[3], (0.04, 0.08, 0.13))
        p.halo(light[0], light[1] + 2, 15, 12, FLAME[3], (0.03, 0.06, 0.09), L="pool")
        pool(p, light[0], g, 18, night)
    return light


def pool(p: Pix, cx, g, rx, night: bool):
    """A pool of a lantern's phosphor on the tatami at its foot, after dark, brightest under it."""
    if night:
        p.halo(cx, g - 1, rx, 2.4, FLAME[3], (0.06, 0.12, 0.2), L="pool", shape=True)


# --------------------------------------------------------------------------- the fighters
# The fighter in his flying kick, 36 by 25, facing right: his left leg drawn up under him, his right driving out level
# at the height of a man's head with the heel leading, his body leaning back from it, one fist up to guard his face
# and the other flung back. Hair (q h H), skin (o e s S, the eye y), the gi (k d g G, its collar w) and his belt (b B).
KICK = [
    "....qqqqq...........................",
    "...qHHHHhq..........................",
    "...qHhhhhhq.........................",
    "...qhhhhhsSo.....oo.................",
    "...qhhhhsSyo....oSso................",
    "....qhhhsSSo....osseo...............",
    ".....qhoesso....oeeo................",
    "......kwwesk...kGgdk................",
    "......kGGwwGGgdkGgdk..............o.",
    ".....kGGddwwddgGgdk..............oso",
    "....kGgddddwggdGgdk.............oSeo",
    "...kGgddkkddwggdddkkkkkkkkkkkkkkoseo",
    "...kGgdk..kddgwBggGGGGGGGGGGGGGGSseo",
    "..kGgdk....kddbBBGGGGGGGGGgggggggSeo",
    ".kGgddk.....kddGGgggggggggddddddeeo.",
    ".oSsdk.......kdgggddddddddddddkkoo..",
    ".oeeo.......kBbdddddddddkkkkkk......",
    "..oo.......kBbkkdddgggkk............",
    "..........kbbk..kddgGGgk............",
    ".........kbkk...kkGGGgddk...........",
    "..........k...okGGgggdddk...........",
    "............ooSSggdddddk............",
    "...........oSsseedddkkk.............",
    "...........oeekddkkk................",
    "............oo.kk...................",
]
KICK_FACE = (10.5, 4.5)     # where his face is on his art, for the light it takes by night
TRAIL = ((-5, 7, 0.65), (-10, 14, 0.32))   # his afterimages: how far back down his leap each lies, and how strong
ECHO = ((0.75, 0), (0.6, 0.8))             # how strong an afterimage's body and its outline are, by day and by night
ECHO_TONE = ((GOLD[6], GOLD[6]), (FLAME[1], FLAME[4]))     # and the tones of its body and its outline
# His opponent in his guard, 21 by 32, facing left: shaven-headed, his lead fist forward at the height of his chin
# and the other drawn back by it, his knees bent and his weight between his feet.
GUARD = [
    "........oooo.........",
    ".......oSSSso........",
    "......oSSSsseo.......",
    "......oSyssseo.......",
    ".....oSsssseeo.......",
    "......oessseo........",
    ".......oeeeok........",
    "..o....kwGsgdk.......",
    ".oSo..okGwegddk......",
    "osseooSsGgwgddk......",
    ".oeedoeGgddwddk......",
    ".kdggdGGgdgwddk......",
    "..kdggdgdggwddk......",
    "...kgggddggwddk......",
    "....kgddgdgwddk......",
    "....kddkGGgwddk......",
    ".....kkBBBbbbbbk.....",
    "......kGGgddbbbk.....",
    ".....kGGggddddgdk....",
    ".....kGGgdddgggdk....",
    "....kGGgddkkggggdk...",
    "....kGgdddkkdgGGgk...",
    "...kGGgddk..kgGgddk..",
    "...kGgddk....kggddk..",
    "...kGgddk....kgggdk..",
    "..kgGgdk.....kgggdk..",
    "..kGggdk.....kgggdk..",
    "..kGgddk......kggdk..",
    ".okGgdk.......kggdk..",
    "oSSSSdk.......oSSSSo.",
    "oeeeeo........oeeeeo.",
    ".oooo..........oooo..",
]
GUARD_FACE = (8.5, 3.5)
WAIST = 17        # the guard's first row below his belt: what stays planted while his body sinks and rises


def _figure_pal(cloth: list, skin: list, night: bool) -> dict:
    """A fighter's colours: his gi on `cloth`, his skin on the hand's `skin`, which keeps its tone by night, his hair
    and his belt."""
    return {"k": cloth[0], "d": cloth[2], "g": cloth[3], "G": cloth[5 if not night else 4], "w": cloth[6 if not night
            else 5], "o": skin[1], "e": skin[2], "s": skin[3], "S": skin[4], "y": skin[0], "q": HAIR[0], "h": HAIR[2],
            "H": HAIR[4], "b": LACQUER[1], "B": LACQUER[5]}


def _cells(art, pal, rim=None, toward=(1, 0)) -> dict:
    """A sprite's cells and colours; with `rim`, (cloth, colour), a light's colour laid over the cloth along the
    edges that face the light, which lies `toward` (dx, dy) of it: (1, 0) for a light at the right, (0, -1) above."""
    cells = {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if pal.get(ch)}
    if rim:
        cloth, colour = rim
        dx, dy = toward
        for (i, j), c in list(cells.items()):
            if c in cloth and (i + dx, j + dy) not in cells:
                cells[(i, j)] = colour
    return cells


def kicker(p: Pix, x, y, night: bool, motion: bool, light=None):
    """The fighter in his flying kick, his top-left at (x, y), and the afterimages of his leap trailing behind him
    down and to the left, fainter as they go, as the eye holds a body moving faster than it can: by day in the toner's
    green and by night in phosphor. In a moving header he hangs at the top of his leap and rises a unit and settles on
    a four-second loop, the afterimages strobing. By night the lantern over him lays its phosphor along his back and
    shoulders and lights his face, which keeps its tone. Returns the cells he covers."""
    pal = _figure_pal(GI, RAMP["skin1"], night)
    key = ("kick", night)
    if key not in p.syms:
        rim = (set(GI), FLAME[1]) if night and light else None
        p.symbol(key, _cells(KICK, pal, rim, (0, -1)))
    body = set(_cells(KICK, pal))
    edge = {(i, j) for (i, j) in body if any((i + a, j + b) not in body for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    tone, edge_tone = ECHO_TONE[night]
    fill, line = ECHO[night]
    for name, cells in (("kickghost", body), ("kickedge", edge if line else ())):
        if (name,) not in p.syms and cells:
            p.symbol((name,), {xy: 1 for xy in cells}, mono=True)
    sid, gid, eid = p.syms[key], p.syms[("kickghost",)], p.syms.get(("kickedge",))

    def echo(dx, dy, a, anim=""):
        return (f'<g opacity="{num(a)}">{anim}<use href="#{gid}" x="{x + dx}" y="{y + dy}" stroke="{tone}" '
                f'stroke-opacity="{num(fill)}"/>'
                + (f'<use href="#{eid}" x="{x + dx}" y="{y + dy}" stroke="{edge_tone}" stroke-opacity="{num(line)}"/>'
                   if line else "") + "</g>")
    still = "".join(echo(dx, dy, a) for dx, dy, a in TRAIL) + f'<use href="#{sid}" x="{x}" y="{y}"/>'
    if motion:
        ghosts = "".join(echo(dx, dy, a, f'<animate attributeName="opacity" values="{num(a)};{num(a * 0.4)};'
                                       f'{num(a)};0" keyTimes="0;.25;.5;.75" dur="{num(LOOP / 2)}s" '
                                       f'begin="{num(i * 0.25)}s" repeatCount="indefinite" calcMode="discrete"/>')
                         for i, (dx, dy, a) in enumerate(TRAIL))
        moving = (f'{ghosts}<g><use href="#{sid}" x="{x}" y="{y}"/><animateTransform attributeName="transform" '
                  f'type="translate" values="0 0;0 -1" keyTimes="0;.5" dur="{num(LOOP)}s" repeatCount="indefinite" '
                  f'calcMode="discrete"/></g>')
    else:
        moving = still
    p.raw(1, moving, still)
    if night and light:
        p.halo(x + KICK_FACE[0], y + KICK_FACE[1], 4, 4, FLAME[3], (0.06, 0.12), L="pool", shape=True)
    return {(x + i, y + j) for j, row in enumerate(KICK) for i, ch in enumerate(row) if ch != "."}


def guard(p: Pix, x, g, night: bool, motion: bool, light=None):
    """His opponent waiting in his guard, standing on the floor at row g from column x: in a moving header his body
    sinks a unit over his planted feet and rises again, on a four-second loop. By night the lantern behind him lays
    its phosphor along his back and lights his face, which keeps its tone."""
    pal = _figure_pal(INDIGO, RAMP["skin2"], night)
    rim = (set(INDIGO), FLAME[2]) if night and light else None

    top = g - len(GUARD) + 1
    upper = ("guardup", night)
    if upper not in p.syms:
        p.symbol(upper, _cells(GUARD[:WAIST], pal, rim))
    lower = _cells(GUARD[WAIST:], pal, rim)
    for (i, j), c in lower.items():
        p.px(x + i, top + WAIST + j, c)
    sid = p.syms[upper]
    still = f'<use href="#{sid}" x="{x}" y="{top}"/>'
    if motion:
        moving = (f'<g><use href="#{sid}" x="{x}" y="{top}"/><animateTransform attributeName="transform" '
                  f'type="translate" values="0 0;0 1" keyTimes="0;.5" dur="{num(LOOP)}s" begin="1s" '
                  f'repeatCount="indefinite" calcMode="discrete"/></g>')
    else:
        moving = still
    p.raw(0.2, moving, still)
    if night and light:
        p.halo(x + GUARD_FACE[0], top + GUARD_FACE[1], 4, 4, FLAME[3], (0.06, 0.12), L="pool", shape=True)


def shadow(p: Pix, cx, g, rx):
    """The shadow a fighter in the air throws on the tatami under him, darkest at its middle."""
    for x in range(round(cx - rx), round(cx + rx) + 1):
        d = abs(x + 0.5 - cx) / rx
        if d < 1:
            p.px(x, g - 1, X["shade_ink"] + (":0.32" if d < 0.6 else ":0.16"), "base")
            if d < 0.75:
                p.px(x, g, X["shade_ink"] + ":0.24", "base")


# --------------------------------------------------------------------------- the floor
def tatami(p: Pix, x0, x1, g, night: bool, uid: str = "tm"):
    """The tatami along the floor from x0 to x1, its top at row g - 1: its rush lit along the upper row and woven in
    the row under it, and every mat's length a seam of black brocade."""
    k = -1 if night else 0
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{g - 1}" width="45" height="2" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{ramp_at(TATAMI, 5 + k)}" d="M0 .5h45"/>'
                  f'<path stroke="{ramp_at(TATAMI, 3 + k)}" d="M0 1.5h45"/>'
                  f'<path stroke="{ramp_at(TATAMI, 4 + k)}" d="{"".join(f"M{i} 1.5h1" for i in range(1, 44, 4))}"/>'
                  f'<path stroke="{LACQUER[1]}" d="M44.5 0v2"/>'
                  f'<path stroke="{ramp_at(GOLD, 2 + k)}" d="M44.5 1v1"/></pattern>')
    p.shapes["base"].append(f'<rect x="{x0}" y="{g - 1}" width="{x1 - x0}" height="2" fill="url(#{uid})"/>')


def fallen(p: Pix, spans, g, night: bool, seed: int = 12):
    """Petals fallen on the tatami along the spans `spans` of the floor, one here and there, lit or in shade."""
    k = -2 if night else 0
    rnd = random.Random(seed)
    for a, b in spans:
        for x in range(a, b, 1):
            if rnd.random() < 0.07:
                p.px(x, g - 1, ramp_at(SAKURA, (5 if rnd.random() < 0.5 else 3) + k))


# --------------------------------------------------------------------------- the petals on the wind
# A petal turning as it drifts, each way round: the near ones three units across, lit (o) and in shade (x), and the far
# ones two.
NEAR = [[".o.", "oox", ".xx"], ["oo.", "oxx", ".x."], [".oo", "xox", "xx."], ["o..", "oox", ".xx"]]
FAR = [["ox", "x."], ["xo", ".x"], [".o", "ox"], ["o.", "xo"]]
PETAL_TILE = (120, 60)    # the tile the drifting petals are laid in: it steps two along and one down as they drift
PETALS = 20               # how many drift in a tile, half of them near
DRIFT = 36.0              # seconds the petals take to drift a tile's breadth: one of the hand's slow sweeps


def petal_drift(p: Pix, night: bool, motion: bool, foot: int, box, seed: int = 7, z: float = -9):
    """Cherry petals drifting across the whole sky of the sheet, behind the title and the scenes, from the upper left
    down toward the right: a tile of them, near and far, stepping two units along and one down at a time and round
    again on one of the hand's slow sweeps. They end above the tagline, above row `foot`, and keep out of the month's
    mark's box, `box`, two units clear. Laid as a pattern, so the whole sky of them costs a tile's few petals; the
    still twin holds them where they begin."""
    k = -1 if night else 0
    tw, th = PETAL_TILE
    rnd = random.Random(seed)
    body: dict = {}
    spots: list = []
    while len(spots) < (PETALS // 4 if p.lite else PETALS):
        q = (rnd.randrange(tw - 3), rnd.randrange(th - 3))
        if all(abs(q[0] - a) + abs(q[1] - b) > 11 for a, b in spots):
            spots.append(q)
    for i, (px, py) in enumerate(spots):
        art, near = (NEAR[i % 4], True) if i % 2 == 0 else (FAR[i % 4], False)
        for dy, row in enumerate(art):
            for dx, ch in enumerate(row):
                if ch != ".":
                    c = ramp_at(SAKURA, ((4 if ch == "o" else 2) if near else (3 if ch == "o" else 2)) + k)
                    body.setdefault(c, {})[(px + dx, py + dy)] = c
    tile = "".join(f'<path stroke="{c}" d="{Pix._d(_rows(cells))}"/>' for c, cells in body.items())
    steps = th
    drift = (f'<animateTransform attributeName="patternTransform" type="translate" '
             f'values="{";".join(f"{2 * i} {i}" for i in range(steps))}" dur="{num(DRIFT)}s" '
             f'repeatCount="indefinite" calcMode="discrete"/>') if motion else ""
    pid, cid = "pdt", "atm"
    p.defs.append(f'<pattern id="{pid}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">{tile}{drift}'
                  f'</pattern>')
    a, _, b, d = box
    rects = [(EDGE, 4, a - 2, foot), (b + 2, 4, p.w - EDGE, foot), (a - 2, d + 2, b + 2, foot)]
    p.defs.append(f'<clipPath id="{cid}">' + "".join(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>'
                                                       for x0, y0, x1, y1 in rects if y1 > y0 and x1 > x0)
                  + "</clipPath>")
    layer = f'<g clip-path="url(#{cid})"><rect x="{EDGE}" y="4" width="{p.w - 2 * EDGE}" height="{foot - 4}" ' \
            f'fill="url(#{pid})"/></g>'
    p.raw(z, layer, layer)


def _rows(cells) -> dict:
    """Cells as the canvas keeps a colour's pixels for its paths: each row's columns."""
    rows: dict = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
    return rows


def glow_on(p: Pix, box, cx, cy, rx, ry, alphas=(0.05, 0.1, 0.16)):
    """A light's phosphor laid over what stands in `box` and nowhere else: rings of it, stronger toward (cx, cy). A
    drawing made lighter lets it go, the last pass of light."""
    if p.lite:
        return
    x0, y0, x1, y1 = box
    cid = f"go{len(p.defs)}"
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
    n, prev, rings = len(alphas), 0.0, []
    for i, a in enumerate(alphas):
        f = (n - i) / n
        rings.append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx * f)}" ry="{num(ry * f)}" '
                     f'fill-opacity="{num(1 - (1 - a) / (1 - prev))}"/>')
        prev = a
    markup = f'<g clip-path="url(#{cid})" fill="{FLAME[3]}">{"".join(rings)}</g>'
    p.raw(3, markup, markup)


# --------------------------------------------------------------------------- the crest
def _sakura_cells(cx, cy, r: float) -> dict:
    """A cherry blossom crest centred on (cx, cy), `r` its petals' reach: five rounded petals, each notched at its
    tip, round a heart. Returns its cells as {(x, y): part}, the part 'p' a petal, 'e' a petal's lit edge, 'h' the
    heart."""
    out = {}
    pr, pd = r * 0.42, r * 0.55
    for yy in range(math.floor(cy - r - 1), math.ceil(cy + r) + 2):
        for xx in range(math.floor(cx - r - 1), math.ceil(cx + r) + 2):
            fx, fy = xx + 0.5 - cx, yy + 0.5 - cy
            for n in range(5):
                a = -math.pi / 2 + n * 2 * math.pi / 5
                px, py = math.cos(a) * pd, math.sin(a) * pd
                tx, ty = math.cos(a) * (pd + pr), math.sin(a) * (pd + pr)
                if (fx - px) ** 2 + (fy - py) ** 2 <= pr * pr and (fx - tx) ** 2 + (fy - ty) ** 2 > (pr * 0.36) ** 2:
                    out[(xx, yy)] = "e" if (fx - px) + (fy - py) < -pr * 0.45 else "p"
            if fx * fx + fy * fy <= (r * 0.22) ** 2:
                out[(xx, yy)] = "h"
    return out


def crest(p: Pix, cx, cy, r: float, night: bool, disc: bool = True, L="base"):
    """The dojo's crest, a cherry blossom of gold leaf: on a disc of black lacquer in a ring of gold when `disc`,
    the disc lit along its upper left; by night the gold catching the lantern light. Kept as a symbol, so a crest
    laid again costs a use."""
    k = -1 if night else 0
    key = ("crest", r, disc, night)
    if key not in p.syms:
        cells = {}
        if disc:
            R = r + 2.5
            for (xx, yy) in _disc(0, 0, R):
                d = math.hypot(xx + 0.5, yy + 0.5)
                lit = (xx + yy) < -1
                cells[(xx, yy)] = (ramp_at(GOLD, (5 if lit else 3) + k) if d > R - 1.1 else
                                   LACQUER[3] if lit and d > R - 2.4 else LACQUER[1])
        for (xx, yy), part in _sakura_cells(0, 0, r).items():
            cells[(xx, yy)] = {"p": ramp_at(GOLD, 4 + k), "e": ramp_at(GOLD, 6 + k), "h": ramp_at(RED, 3 + k)}[part]
        p.symbol(key, cells)
    p.use(key, cx, cy, L)


def petals_on_rule(p: Pix, x0, x1, y, night: bool, seed: int = 0):
    """Cherry petals fallen along a header's rule from x0 to x1, one here and there, lit or in shade, each two units
    clear of every word."""
    k = -2 if night else 0
    rnd = random.Random(seed)
    for x in range(x0 + 3, x1 - 3):
        if rnd.random() < 0.05 and p.clear_of_words(x - 2, y - 4, x + 4, y + 2):
            art = FAR[rnd.randrange(4)]
            for dy, row in enumerate(art):
                for dx, ch in enumerate(row):
                    if ch != ".":
                        p.px(x + dx, y - 2 + dy, ramp_at(SAKURA, (5 if ch == "o" else 3) + k))


# --------------------------------------------------------------------------- the footers' floor and alcove
# The kanji on a hanging scroll, 7 by 7: 力, strength, brushed: the stroke across bending down into its hook, and
# the long stroke sweeping down to the left through it.
CHIKARA = ["...#...", "...#...", "######.", "...#..#", "..#...#", ".#....#", "#....#."]
SCROLL = 13         # a hanging scroll's width, its roller's knobs beyond it


def kakejiku(p: Pix, x, y, night: bool, length: int = 24):
    """A hanging scroll with its top at row y, SCROLL wide and `length` tall: its cord over the hook on the beam, the
    rod across its head, the moss-green silk of its mount, the paper brushed with 力 in sumi and the vermilion seal
    under it, and the roller across its foot with its knobs of lacquer tipped with gold; its shadow down its right."""
    k = -1 if night else 0
    M, w = RAMP["moss"], SCROLL
    hx = x + w // 2
    for i in range(1, 4):
        p.px(hx - i, y - 3 + i, ramp_at(STRAW, 2 + k))
        p.px(hx + i, y - 3 + i, ramp_at(STRAW, 1 + k))
    p.px(hx, y - 3, ramp_at(GOLD, 4 + k))
    for yy in range(y + 2, y + length):
        p.px(x + w, yy, X["shade_ink"] + ":0.2")
    p.hline(x, x + w, y, ramp_at(WOOD, 5 + k))
    p.hline(x, x + w, y + 1, ramp_at(WOOD, 2 + k))
    p.rect(x, y + 2, w, length - 5, ramp_at(M, 3 + k))
    p.vline(x, y + 2, y + length - 3, ramp_at(M, 5 + k))
    p.vline(x + w - 1, y + 2, y + length - 3, ramp_at(M, 1 + k))
    top, bottom = y + 4, y + length - 6
    p.rect(x + 2, top, w - 4, bottom - top + 1, PAPER[6] if not night else PAPER[3])
    p.vline(x + w - 3, top, bottom + 1, PAPER[4] if not night else PAPER[2])
    for j, row in enumerate(CHIKARA):
        for i, ch in enumerate(row):
            if ch == "#" and top + 1 + j <= bottom:
                p.px(x + 3 + i, top + 1 + j, LACQUER[1])
    if bottom - top >= 11:
        p.px(x + w - 5, bottom - 2, ramp_at(RED, 3 + k))
        p.px(x + w - 5, bottom - 1, ramp_at(RED, 2 + k))
    yb = y + length - 3
    p.hline(x - 1, x + w + 1, yb, ramp_at(WOOD, 4 + k))
    p.hline(x - 1, x + w + 1, yb + 1, ramp_at(WOOD, 1 + k))
    for kx in (x - 2, x + w + 1):
        p.rect(kx, yb - 1, 1, 3, LACQUER[1])
        p.px(kx, yb - 1, ramp_at(GOLD, 5 + k))


# The alcove a footer hangs after its cells, by the room it has, largest first: its width, its height, and whether
# a paper lantern hangs either side of the scroll.
ALCOVES = ((41, 21, True), (17, 21, False))
FLOOR = 5           # the floor's rows along a footer's foot: the rush of the tatami, and its brocade edge
DAIS = 3            # how far the dais rises where the cells leave it room
DAIS_RUN = 18       # the fewest columns a dais runs


def footing(p: Pix, night: bool, after: int = 0, alcove: bool = True):
    """A footer once its words are set: the dojo's floor along its foot, the rush of the tatami lit along its top
    row and woven, a mat's seam of black brocade every so often and the brocade edge under it worked in gold, as
    deep as the frame's foot or as shallow as keeps a row clear of the lowest word; a dais of hinoki rising by DAIS
    rows wherever the cells leave it room along DAIS_RUN columns or more; and in the rightmost place from column
    `after` on where the cells leave the paper free, the alcove: a hanging scroll brushed with 力 between two paper
    lanterns, or the scroll alone where there is less room, the lanterns burning phosphor by night, flickering."""
    w, h = p.w, p.h
    k = -1 if night else 0
    base = p.layers["base"]
    ledge = min(h - 2, max(h - FLOOR, max((b[3] for b in p.words), default=0) + 1))

    def free(x0, y0, x1, y1):
        return 5 <= x0 and x1 <= w - 5 and 5 <= y0 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2) and \
            not any(":" not in base.get((x, y), ":") for x in range(x0 - 1, x1 + 1) for y in range(y0, y1)
                    if base.get((x, y)) not in (None,))
    mark = None
    if alcove:
        for aw, ah, lanterns in ALCOVES:
            top = ledge - DAIS - ah
            mark = next(((x, top, aw, ah, lanterns) for x in range(w - 6 - aw, max(5, after), -1)
                         if free(x, top, x + aw, ledge - DAIS)), None)
            if mark:
                break
    rise = [free(x, ledge - DAIS - 1, x + 1, ledge) for x in range(w)]
    tops = [ledge] * w
    x = 5
    while x < w - 5:
        if not rise[x]:
            x += 1
            continue
        b = next((i for i in range(x, w - 5) if not rise[i]), w - 5)
        if b - x >= DAIS_RUN or (mark and x <= mark[0] and mark[0] + mark[2] <= b):
            tops[x:b] = [ledge - DAIS] * (b - x)
        x = b
    T, L, G, H = TATAMI, LACQUER, GOLD, HINOKI
    for x in range(EDGE, w - EDGE):
        t = tops[x]
        if t < ledge:
            for y in range(t, ledge):
                c = ramp_at(H, (5 if y == t else 3 if y < ledge - 1 else 1) + k)
                p.px(x, y, c)
            if x > EDGE and tops[x - 1] == ledge:
                for y in range(t, ledge):
                    p.px(x, y, ramp_at(H, 6 + k))
            if x < w - EDGE - 1 and tops[x + 1] == ledge:
                for y in range(t, ledge):
                    p.px(x, y, ramp_at(H, 1 + k))
        for y in range(ledge, h - 1):
            row = y - ledge
            if row == 0:
                c = ramp_at(T, 5 + k)
            elif y >= h - 3:
                lz = (x - EDGE) % 8
                c = ramp_at(G, 3 + k) if (y == h - 3 and lz in (3, 4)) or (y == h - 2 and lz in (2, 5)) else L[1]
            else:
                c = ramp_at(T, (4 if (x + y) % 4 == 1 else 3) + k)
            if (x - EDGE) % 45 == 44 and y < h - 3:
                c = L[1]
            p.px(x, y, c)
        p.px(x, h - 1, L[0])
    if mark:
        mx, top, aw, ah, lanterns = mark
        sx = mx + (14 if lanterns else 2)
        kakejiku(p, sx, top + 3, night, ah - 3)
        if lanterns:
            for lx, phase in ((mx, 0), (mx + aw - 11, 2)):
                chochin(p, lx, top + 1, night, False, phase=phase, cord=EDGE)


def rope(p: Pix, x0, x1, y, night: bool):
    """A rope of twisted straw two rows deep from x0 to x1 at row y, its strands slanting, a knot at each end."""
    k = -2 if night else 0
    for x in range(x0, x1):
        t = x % 3
        p.px(x, y, ramp_at(STRAW, (5 if t == 0 else 4 if t == 1 else 2) + k))
        p.px(x, y + 1, ramp_at(STRAW, (3 if t == 0 else 2 if t == 1 else 1) + k))
    for x in (x0, x1 - 1):
        p.px(x, y, ramp_at(STRAW, 1 + k))
        p.px(x, y + 1, ramp_at(STRAW, 0 + k))


# --------------------------------------------------------------------------- the footers and the links
# A heart of vermilion lacquer, 7 by 6: its lobes lit on the left, a fleck of gold leaf on the upper-left lobe.
HEART = [".gL.LM.", "gLMMMmd", "LMMmmdd", ".Mmmdd.", "..mdd..", "...d..."]


def heart(p: Pix, x, y, L="base"):
    """The heart in BUILT WITH (heart) BY: vermilion lacquer, its lobes lit on the left, a fleck of gold on it."""
    pal = {"g": GOLD[5], "L": RED[5], "M": RED[4], "m": RED[3], "d": RED[1]}
    p.sprite(x, y, HEART, pal, 1, L, reuse=True)


def scabbard(p: Pix, x0, y0, w, h, period=5, L="base"):
    """The graphic scale's bar as a lacquered scabbard: bands of black lacquer and of gold leaf by turns, each
    `period` long, lit along the top and in shade along the foot."""
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.25 else 1 if f < 0.75 else 2
        for xx in range(x0, x0 + w):
            gold = ((xx - x0) // period) % 2 == 1
            p.px(xx, yy, (GOLD[5], GOLD[4], GOLD[2])[band] if gold else (LACQUER[4], LACQUER[2], LACQUER[0])[band], L)


# The links' icons, 9 by 7, one for each link in turn: a paper lantern, a torii, a cherry blossom and a katana.
ICONS = {
    "lantern": ["...kkk...", "..pPPPp..", ".pPPrPPp.", ".bbrrrbb.", ".pPPrPPp.", "..pPPPp..", "...kkk..."],
    "torii": ["r.......r", "rRRRRRRRr", ".r.....r.", "rrrrrrrrr", "..r...r..", "..r...r..", ".rr...rr."],
    "blossom": ["...SS....", ".s.Ss.S..", "sSs.g.sS.", ".ssgYgs..", ".sS.g.Ss.", "..sS.Ss..", "...s..s.."],
    "katana": ["......lW.", ".....lW..", "....lW...", "...lW....", ".ggW.....", "..gg.....", ".k..g...."],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a lacquered button, by day or by night: the lantern's paper burning phosphor by night."""
    k = -1 if night else 0
    lantern = (FLAME[5], FLAME[4]) if night else (SHIDE[6], SHIDE[4])
    return {"k": GOLD[3 + k], "P": lantern[0], "p": lantern[1], "b": GOLD[2], "r": RED[4], "R": RED[5],
            "S": SAKURA[5], "s": SAKURA[4], "g": GOLD[4], "Y": GOLD[6], "l": SHIDE[3], "W": SHIDE[6], "#": ink}


# --------------------------------------------------------------------------- the elements
def card_deco(p: Pix, x, y, w, h, night: bool, lid: bool):
    """A schematic's card made a lacquered box: a band of black lacquer down its icon cell's edge, capped with gold
    top and foot, and on its lid gold fittings over its two upper corners."""
    k = -1 if night else 0
    for yy in range(y + 1, y + h - 1):
        p.px(x + 10, yy, LACQUER[4])
        p.px(x + 11, yy, LACQUER[2])
        p.px(x + 12, yy, LACQUER[0])
    for yy in (y + 1, y + h - 2):
        p.hline(x + 10, x + 13, yy, ramp_at(GOLD, (5 if yy == y + 1 else 3) + k))
    if lid:
        for fx in (x - 1, x + w - 4):
            fitting(p, fx, y - 1, night)


# A paper lantern hung under a wire, 3 by 7 under its cord: a cap of gold (g), its paper vermilion (R, the shade r)
# with a white band (W, w) round its middle, and a tassel (t).
WIRE_LANTERN = [".c.", "ggg", "RRr", "WWw", "RRr", "ggg", ".t."]


def cord_lights(p: Pix, cells, night: bool):
    """What hangs on a wire made a cord of vermilion silk: a paper lantern under it every so often where it runs
    level, vermilion with a white band by day and burning phosphor by night, and a knot of gold where it runs
    upright."""
    k = -1 if night else 0
    key = ("wire-lantern", night)
    if key not in p.syms:
        if night:
            pal = {"c": LACQUER[4], "g": GOLD[3], "R": FLAME[4], "r": FLAME[3], "W": FLAME[6], "w": FLAME[5],
                   "t": GOLD[3]}
        else:
            pal = {"c": LACQUER[2], "g": GOLD[4], "R": RED[4], "r": RED[2], "W": SHIDE[6], "w": SHIDE[4], "t": RED[3]}
        p.symbol(key, {(i - 1, j + 1): pal[ch] for j, row in enumerate(WIRE_LANTERN) for i, ch in enumerate(row)
                       if ch != "."})
    for i, (x, y, d) in enumerate(cells[6:-8]):
        if i % 16:
            continue
        if d == "h":
            p.use(key, x, y)
        else:
            p.px(x - 1, y, ramp_at(GOLD, 5 + k))
            p.px(x + 1, y, ramp_at(GOLD, 3 + k))


def bamboo(p: Pix, x, top, w, h, night: bool):
    """A cane of bamboo `w` wide standing from row top + h up to row top: lit down its left and in shade down its
    right, a node every seven rows from its foot, and its cut end pale at its top."""
    k = -1 if night else 0
    M = RAMP["moss"]
    base = top + h
    for yy in range(top, base):
        node = (base - yy) % 7
        for xx in range(x, x + w):
            u = (xx - x) / max(1, w - 1)
            tone = 5 if u < 0.2 else 4 if u < 0.55 else 3 if u < 0.85 else 2
            if node == 0:
                tone = 1
            elif node == 1:
                tone = min(6, tone + 1)
            p.px(xx, yy, ramp_at(M, tone + k))
    if h > 1:
        p.hline(x, x + w, top, ramp_at(TATAMI, 6 + k))


def drum_rim(p: Pix, arc, night: bool):
    """The dial's half ring made the rim of a taiko drum: vermilion lacquer bent over it, lit along its upper edge,
    and a stud of gold every few units round it."""
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        if int(s) % 6 == 2 and abs(o) < 0.5:
            return ramp_at(GOLD, 5 + k)
        return ramp_at(RED, max(1, min(5, round(1.4 + 3.6 * lam) + k)))
    tube(p, arc, 2.6, colour, outline=LACQUER[0])


# The dyed patterns a file type's wrapper is woven in, by turns: waves of the sea, the hemp leaf, a check, cherry
# blossom and the tortoise shell.
PATTERNS = ("seigaiha", "asanoha", "ichimatsu", "sakura", "kikko")


def dyed(i: int, xx, yy, y0, lift: int, night: bool) -> str:
    """The colour at (xx, yy) of the `i`-th wrapper, its pattern one of PATTERNS by turns, `lift` steps lighter on
    its lit top row and darker along its foot."""
    k = (-1 if night else 0) + lift
    kind = PATTERNS[i % len(PATTERNS)]
    yy -= y0
    if kind == "seigaiha":
        cx, cy = (xx // 6) * 6 + (3 if (yy // 3) % 2 else 0), (yy // 3) * 3 + 3
        d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
        return ramp_at(INDIGO, (5 if 2.2 < d < 3.2 else 3) + k)
    if kind == "asanoha":
        on = (xx + yy) % 6 == 0 or (xx - yy) % 6 == 0 or xx % 6 == 0
        return ramp_at(GOLD, 4 + k) if on else ramp_at(RED, 2 + k)
    if kind == "ichimatsu":
        return ramp_at(RAMP["moss"], 3 + k) if ((xx // 3) + (yy // 3)) % 2 == 0 else ramp_at(LACQUER, 2 + k)
    if kind == "sakura":
        return ramp_at(SHIDE, 6 + k) if (xx % 6, yy % 4) in ((2, 1), (1, 2), (3, 2), (2, 3)) else ramp_at(SAKURA, 3 + k)
    on = yy % 4 == 0 or (xx + (yy // 4) * 3) % 6 == 0
    return ramp_at(GOLD, 2 + k) if on else ramp_at(GOLD, 4 + k)


def nafuda(q: Pix, ox, oy, night: bool):
    """The 11 by 15 cell a counter's digit is brushed on, a dojo's wooden name plate: pale hinoki by day and the
    same wood dark with the night by night, edged darker, lit along its top and shaded down its right, hung from a
    peg of gold."""
    H = HINOKI
    face, edge, lit, shade = (H[1], LACQUER[0], H[2], H[0]) if night else (H[5], H[1], H[6], H[4])
    q.rect(ox, oy, 11, 15, face)
    q.box(ox, oy, 11, 15, edge)
    q.hline(ox + 1, ox + 10, oy + 1, lit)
    q.vline(ox + 9, oy + 2, oy + 14, shade)
    q.px(ox + 5, oy, GOLD[4 if night else 5])


# A patch's shide, 3 by 6: a small zigzag of white paper hanging from the rope, its lit face (a) and its edge (b).
PATCH = ["ab.", "ab.", ".ab", ".ab", "ab.", ".a."]


def nobori(p: Pix, x, gy, kind: str, night: bool, i: int = 0):
    """A release hung from the rope at x, whose top row is gy, as the banners hang at a festival: a big release a
    banner five wide on its rod, a white crest on it and its foot cut in a swallowtail, a release a narrower one with
    a white band across it, each dyed by turns vermilion, indigo, moss and wisteria; a patch a shide of white paper;
    one still to come a banner drawn in outline; and the repository's founding a torii, the rope across its top."""
    k = -1 if night else 0
    if kind == "made":
        R = RED
        p.hline(x - 3, x + 4, gy + 2, ramp_at(LACQUER, 3 - k))
        p.hline(x - 2, x + 3, gy + 3, ramp_at(R, 3 + k))
        p.hline(x - 3, x + 4, gy + 5, ramp_at(R, 4 + k))
        for xx, tone in ((x - 2, 4), (x + 2, 2)):
            p.vline(xx, gy + 4, gy + 11, ramp_at(R, tone + k))
            p.px(xx, gy + 5, ramp_at(R, 4 + k))
        return
    if kind == "minor":
        k3 = -3 if night else 0
        p.sprite(x - 1, gy + 2, PATCH, {"a": ramp_at(SHIDE, 6 + k3), "b": ramp_at(SHIDE, 3 + k3)}, 1, "base",
                 reuse=True)
        return
    dye = (RED, INDIGO, RAMP["moss"], RAMP["fuji"])[i % 4]
    half, foot = (2, gy + 11) if kind == "big" else (1, gy + 9)
    p.hline(x - half - 1, x + half + 2, gy + 2, ramp_at(WOOD, 4 + k))
    p.px(x - half - 1, gy + 2, ramp_at(WOOD, 2 + k))
    p.px(x + half + 1, gy + 2, ramp_at(WOOD, 2 + k))
    for yy in range(gy + 3, foot + 1):
        for xx in range(x - half, x + half + 1):
            if yy == foot and xx == x:
                continue                                  # the swallowtail
            edge = xx in (x - half, x + half) or yy in (gy + 3, foot) or (yy == foot - 1 and xx == x)
            if kind == "next":
                if edge:
                    p.px(xx, yy, ramp_at(dye, 4 + k))
                continue
            tone = 4 if xx == x - half else 2 if xx == x + half else 3
            p.px(xx, yy, ramp_at(dye, tone + k))
    if kind == "next":
        return
    white, shade = ramp_at(SHIDE, 6 + k), ramp_at(SHIDE, 4 + k)
    if kind == "big":
        for dx, dy in ((0, 4), (-1, 5), (0, 5), (1, 5), (0, 6)):
            p.px(x + dx, gy + dy, white if dx <= 0 else shade)
    else:
        p.hline(x - 1, x + 1, gy + 5, white)
        p.px(x + 1, gy + 5, shade)


def hinomaru(p: Pix, x, y, night: bool):
    """The mark at today's end of the rope: the red sun, lit at its upper left, where the rope ends."""
    k = -1 if night else 0
    cx, cy = x + 2.5, y + 1.5
    for (xx, yy) in _disc(cx, cy, 3.3):
        d = (xx + 0.5 - cx + 1) ** 2 + (yy + 0.5 - cy + 1) ** 2
        p.px(xx, yy, ramp_at(RED, (5 if d < 2.5 else 3) + k))


AVATARS = ("indigo", "red", "moss", "fuji")     # the dyes a contributor's crest is in, by turns


def mon(p: Pix, cx, cy, i: int, person: dict, night: bool, ink: str):
    """A contributor as a crest: a disc dyed in their colour, lit along its upper left, ringed in gold, their
    initials on it in white; a bot's disc is granite, a cross on it."""
    k = -1 if night else 0
    bot = not person.get("initials")
    R = STONE if bot else RAMP[AVATARS[i % len(AVATARS)]]
    for (xx, yy) in _disc(cx + 0.5, cy + 0.5, 7.5):
        d = math.hypot(xx - cx, yy - cy)
        lit = (xx - cx) + (yy - cy) < -2
        p.px(xx, yy, ramp_at(GOLD, (5 if lit else 3) + k) if d > 6.3 else ramp_at(R, (4 if lit else 3) + k))
    if bot:
        p.hline(cx - 3, cx + 4, cy, SHIDE[6])
        p.vline(cx, cy - 3, cy + 4, SHIDE[6])
        return
    p.text(cx - 3, cy - 2, str(person["initials"])[:2], ink, "35", shadow=R[0])


def seal(p: Pix, cx, cy, r0, r1, n: int, night: bool):
    """The vermilion of a seal round its pressed centre, lit along its upper left, studded with gold at its rim."""
    k = -1 if night else 0
    for yy in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for xx in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if r0 <= d <= r1:
                a = math.atan2(yy + 0.5 - cy, xx + 0.5 - cx)
                lam = -math.cos(a + math.pi * 0.25)
                stud = d > r1 - 1.2 and int(((a + math.pi) / (2 * math.pi)) * n * 2) % 2 == 0
                c = ramp_at(GOLD, 5 + k) if stud else ramp_at(RED, (4 if lam > 0.35 else 3 if lam > -0.35 else 2) + k)
                p.px(xx, yy, c)


def kanban(p: Pix, night: bool):
    """The placard as a dojo's signboard: a board of pale hinoki by day and of dark wood by night, its grain running
    across it, in a frame of black lacquer with gold fittings at its corners."""
    w, h = p.w, p.h
    ground, streak = (WOOD[2], WOOD[3]) if night else (HINOKI[5], HINOKI[6])
    p.rect(0, 0, w, h, ground)
    for yy in range(4, h - 3):
        for xx in range(4, w - 4):
            if math.sin(xx / 9.0 + yy * 0.8 + math.sin(xx / 23.0) * 2) > 0.9:
                p.px(xx, yy, streak)
    for xx in range(w):
        for yy, c in ((0, LACQUER[0]), (1, LACQUER[4]), (2, LACQUER[2]), (3, LACQUER[1]), (h - 1, LACQUER[0]),
                      (h - 2, LACQUER[1]), (h - 3, LACQUER[2])):
            p.px(xx, yy, c)
    for yy in range(h):
        for xx, c in ((0, LACQUER[0]), (1, LACQUER[4]), (2, LACQUER[2]), (3, LACQUER[1]), (w - 1, LACQUER[0]),
                      (w - 2, LACQUER[1]), (w - 3, LACQUER[2]), (w - 4, LACQUER[1])):
            p.px(xx, yy, c)
    for fx, fy in ((0, 0), (w - 5, 0), (0, h - 5), (w - 5, h - 5)):
        fitting(p, fx, fy, night)
