# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hovercraft set's scenery and sprites, drawn on the shared pixel canvas.

Every sheet is the wall of a sewer tunnel in the real world: board-marked concrete, pale and rust-grey by day under
the ship's floodlights, its formwork joints and tie holes weeping rust, and by night the black of the tunnel. Riveted
steel plate runs down its sides and along its foot, and across a header's top run the tunnel's pipes, a great main
of gunmetal and a smaller one of rusted copper, flanged and strapped, ending at the top centre either side of the
month's mark, steam leaking from a joint at the left. Titles are stencilled in military paint on a scuffed steel
plate riveted to the wall, casting its shadow on the concrete, the stencil's bridges cutting each letter from its
stem, the paint oversprayed at its edges and worn where things have scraped it; by night two work lamps at the
plate's corners light it green. Across the tunnel's sky behind the title sweeps the beam of the ship's searchlight,
slowly, dust glinting in it by night. Headers open on the tunnel: at the left the ship, an armoured hovercraft
battered and patched, hovering low over the black water on pads that glow phosphor, the water shimmering with their
light and thrown up in spray under them, its bridge windows lit and its searchlight high on its mast; at the right a
machine sliding out of a great drain in a brick headwall, a carapace of iron plates and a face of a dozen red eyes,
its tentacles spread wide across the wall and hanging to the water, its eyes' red on the brick and in the channel,
while water drips from the drain's lip. On a strip a machine hangs from the pipes over the water instead, its gaze a
cone of red swinging over the channel; on a phone the ship's searchlight is held on the machine at the drain. Under
the pipes limescale hangs in straws and work lamps in their cages, litter lies on the rules, and the drops on the
concrete glint in the dark where another set has stars. A footer stands on the channel's water with the ship in
little after its last cell, its searchlight on a drain where the machine's eyes burn. Everything is shaded from the
one light in the upper left on the set's own ramps, every light is the hand's phosphor, and only the machine's eyes
burn red."""
from __future__ import annotations

import math
import random

from ...holidays.pixel import FONTS, LX, LY, LZ, Pix, fold, num
from .palette import C, NIGHT_SKY, RAMP, X

CONCRETE, TUNNEL, STEEL, PLATE = RAMP["concrete"], RAMP["tunnel"], RAMP["steel"], RAMP["plate"]
DRAB, RUST, BRICK, WATER = RAMP["drab"], RAMP["rust"], RAMP["brick"], RAMP["water"]
IRON, EYE, FLAME = RAMP["iron"], RAMP["eye"], RAMP["flame"]
EDGE = 4          # the steel's width down the sides and along the foot
TOP = 15          # the rows a header's pipes take across its top
SHIP_L = 46       # the ship's length, stern to nose
HULL = 16         # its hull's depth, deck to keel
SWEEP = 36.0      # the seconds the searchlight's beam takes to sweep the tunnel's sky and back


def _t(R, i):
    """Tone `i` of ramp R, held to the ramp's ends."""
    return R[max(0, min(len(R) - 1, i))]


def _shade(R, k: int):
    """Ramp R stepped `k` tones (down, as by night, when negative), as a function of the tone: `_shade(R, k)(i)` is
    tone i + k, held to the ramp's ends."""
    def tone(i):
        return _t(R, i + k)
    return tone


# --------------------------------------------------------------------------- the concrete
def _boards(night: bool) -> dict:
    """The concrete's tile, forty units by twenty: the joint between two lifts of formwork along its top, the
    boards' grain faint across it, two tie holes, and a streak of rust weeping from one of them."""
    if night:
        joint, grain, hole, lip, rust = TUNNEL[3], TUNNEL[3], TUNNEL[0], TUNNEL[4], TUNNEL[3]
    else:
        joint, grain, hole, lip, rust = CONCRETE[3], CONCRETE[4], CONCRETE[2], CONCRETE[6], RUST[6]
    cells = {}
    for x in range(40):
        cells[(x, 0)] = joint
    for x in range(3, 37, 9):
        for i in range(4):
            cells[(x + i, 7 if x % 2 else 13)] = grain
    for hx in (9, 29):
        cells[(hx, 10)] = hole
        cells[(hx + 1, 10)] = hole
        cells[(hx, 11)] = lip
        cells[(hx + 1, 11)] = lip
    for j in range(4):
        cells[(30, 12 + j)] = rust
    return cells


def paper(p: Pix, night: bool, uid: str = "p"):
    """The ground a drawing sits on: the tunnel's board-marked concrete, pale rust-grey by day under the ship's
    floodlights and black by night, a breath lighter toward the water."""
    w, h = p.w, p.h
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            at = f' y="{edges[i]}"' if edges[i] else ""
            p.under.append(f'<rect{at} width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    else:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')
    p.defs.append(f'<pattern id="{uid}c" x="4" y="2" width="40" height="20" patternUnits="userSpaceOnUse">'
                  f'{p.markup(_boards(night))}</pattern>')
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}c)"/>')


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: the concrete by day, by night the tunnel's band."""
    if night:
        n = len(NIGHT_SKY)
        edges = [round(i * p.h / n) for i in range(n + 1)]
        return next(NIGHT_SKY[i] for i in range(n) if y < edges[i + 1] or i == n - 1)
    return C["paper"]


# --------------------------------------------------------------------------- the frame
def _strip(p: Pix, pid: str, w: int, h: int, cells: dict, x: int, y: int, rw: int, rh: int):
    """A run of riveted steel laid as a pattern of `cells`, w by h, over the box (x, y, rw, rh), under what is drawn."""
    p.defs.append(f'<pattern id="{pid}" x="{x}" y="{y}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells)}</pattern>')
    p.shapes["base"].append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="url(#{pid})"/>')


def frame(p: Pix, night: bool, header: bool = False, clear=None):
    """The border: riveted steel plate down the sides and along the foot, lit on its upper and left faces and in
    shade on the others, a rivet every eight units; across a header's top the pipes (see `pipes`), and across a
    footer's a strip of the same plate."""
    w, h = p.w, p.h
    k = -2 if night else 0
    s = _shade(STEEL, k)
    side = (STEEL[0], s(5), s(4), s(2))
    left = {(i, j): side[i] for i in range(4) for j in range(8)}
    left[(2, 4)], left[(2, 5)], left[(1, 5)] = s(6), s(1), s(3)
    _strip(p, "fl", 4, 8, left, 0, 0, 4, h)
    right = {(3 - i, j): (STEEL[0], s(2), s(3), s(5))[i] for i in range(4) for j in range(8)}
    right[(1, 4)], right[(1, 5)], right[(2, 5)] = s(6), s(1), s(2)
    _strip(p, "fr", 4, 8, right, w - 4, 0, 4, h)
    foot = {(i, j): (s(5), s(3), s(2), STEEL[0])[j] for i in range(8) for j in range(4)}
    foot[(4, 1)], foot[(4, 2)], foot[(5, 2)] = s(6), s(1), s(1)
    _strip(p, "ff", 8, 4, foot, 4, h - 4, w - 8, 4)
    if not header:
        top = {(i, j): (STEEL[0], s(5), s(4), s(2))[j] for i in range(8) for j in range(4)}
        top[(4, 2)], top[(4, 3)] = s(6), s(1)
        _strip(p, "ft", 8, 4, top, 4, 0, w - 8, 4)
        return
    p.hline(0, w, 0, STEEL[0])
    p.hline(1, w - 1, 1, s(5))
    p.hline(1, w - 1, 2, s(2))
    pipes(p, night, clear)


def pipes(p: Pix, night: bool, clear=None):
    """The tunnel's pipes across a header's top: a great main of gunmetal, lit along its crown, and under it a
    smaller one of rusted copper, both strapped to the plate every thirty-two units and the main flanged and bolted
    every forty-eight; where `clear` keeps the top centre for the month's mark each pipe ends in a blind flange."""
    w = p.w
    k = -2 if night else 0
    s = _shade(STEEL, k)
    r = _shade(RUST, k)
    main = [s(4), s(6), s(5), s(4), s(3), s(1)]
    small = [r(5), r(3), r(1)]
    cells_main = {(0, j): c for j, c in enumerate(main)}
    cells_small = {(0, j): c for j, c in enumerate(small)}
    spans = [(EDGE, w - EDGE)] if not clear else [(EDGE, clear[0] - 1), (clear[1] + 1, w - EDGE)]
    p.defs.append(f'<pattern id="pm" y="3" width="1" height="6" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells_main)}</pattern>')
    p.defs.append(f'<pattern id="ps" y="10" width="1" height="3" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells_small)}</pattern>')
    for a, b in spans:
        p.shapes["base"].append(f'<rect x="{a}" y="3" width="{b - a}" height="6" fill="url(#pm)"/>'
                                f'<rect x="{a}" y="10" width="{b - a}" height="3" fill="url(#ps)"/>')
        p.hline(a, b, 9, TUNNEL[1] if night else CONCRETE[3])
        p.hline(a, b, 13, (TUNNEL[0] if night else CONCRETE[2]) + ":0.6")
        p.hline(a, b, 14, (TUNNEL[0] if night else CONCRETE[3]) + ":0.35")
        for x in range(a + 10, b - 4, 48):                  # the main's flanges, bolted
            p.vline(x, 2, 10, s(5))
            p.vline(x + 1, 2, 10, s(2))
            p.px(x, 3, s(6))
            p.px(x, 7, s(6))
            p.vline(x + 2, 3, 9, s(0))
        for x in range(a + 26, b - 4, 32):                  # the straps
            p.vline(x, 3, 13, s(1))
            p.vline(x + 1, 3, 13, s(3))
            p.px(x + 1, 13, s(0))
        for x in (a, b - 3):                                # the blind flanges at each end
            if EDGE < x < w - EDGE - 3:
                p.rect(x, 2, 3, 8, s(4))
                p.vline(x, 2, 10, s(6) if x == a else s(5))
                p.vline(x + 2, 2, 10, s(1))
                p.rect(x, 10, 3, 3, r(2))
                p.px(x + 1, 4, s(1))
                p.px(x + 1, 7, s(1))


# --------------------------------------------------------------------------- the title
def _bridges(glyph_rows: list, width: int) -> list:
    """Where a stencil cuts a letter of the title face, as (column, row) in its own units: a cut down the left edge of
    column 1 on every row where a bar runs from the stem, the same down column `width - 1` where one runs into the
    right stem, and one through the middle of a bar that closes a bowl at its top or its foot."""
    out = []
    for r, cols in enumerate(glyph_rows):
        cs = set(cols)
        if {0, 1} <= cs and any(c >= 2 for c in cs):
            out.append((1, r))
        if {width - 1, width - 2} <= cs and any(c <= width - 3 for c in cs) and width >= 4:
            out.append((width - 1, r))
        if r in (0, len(glyph_rows) - 1) and cs and min(cs) >= 1 and max(cs) - min(cs) >= 2:
            out.append(((min(cs) + max(cs) + 1) / 2, r))
    return out


def over_words(p: Pix, name: str, dz: float) -> str:
    """The layer `name`, just over the words at depth `dz`; or, while a part is drawn onto a layer of its own (see
    `Pix.onto`), as a game's panel draws each section that appears in turn, its twin just over that layer, so what
    is cut into a word appears with it."""
    into = getattr(p, "into", None)
    if not into:
        return p.layer(name, z=dz)
    twin = into + name
    if twin not in p.layers:
        z, anim = (p.meta[into][0], p.meta[into][2]) if into in p.meta else (0, None)
        p.layer(twin, anim, z=z + dz)
    return twin


def stencil_title(p: Pix, x, y, s, night: bool, scale: int) -> int:
    """A title stencilled in military paint: by day drab olive, oversprayed a little round its edges; by night the
    same paint lit by the work lamps' green, its upper and left edges catching their light. The stencil's bridges cut
    each letter from its stem and through its bowls, and here and there the paint is worn through, to the steel of
    the plate behind it (see `title_plate`) or, where there is none, to the sheet. Returns its width."""
    if night:
        kw = dict(glow=(FLAME[2], (0.14,)) if scale >= 3 else None)
        if scale >= 3:
            kw["bevel"] = (FLAME[5], FLAME[1])
        colour = FLAME[3]
    else:
        kw = dict(glow=(DRAB[4], (0.18,)) if scale >= 3 else None)
        colour = DRAB[1]
    if not kw.get("glow"):
        kw.pop("glow", None)
    w = p.text(x, y, s, colour, "57", scale, **kw)
    if scale < 3:
        return w
    plate = getattr(p, "plate", None)

    def under(px_, py_):
        """What the paint is on at (px_, py_): the plate's steel, or the sheet."""
        if plate and plate[0] <= px_ < plate[2] and plate[1] <= py_ < plate[3]:
            return C["plate_night"] if night else PLATE[4]
        return bg_at(p, night, py_)
    L = over_words(p, "stencil", 0.4)
    glyphs, _, space = FONTS["57"]
    cx = x
    rnd = random.Random(len(s) * 13 + x)
    for ch in fold(s, "57"):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        gw, rows = glyphs[ch]
        for col, r in _bridges(rows, gw):
            bx = cx + int(col * scale) - (0 if col == int(col) else scale // 2)
            for yy in range(y + r * scale, y + (r + 1) * scale):
                p.px(bx, yy, under(bx, yy), L)
        for _ in range(2):                                    # worn through to what it is painted on
            r = rnd.randrange(len(rows))
            if rows[r]:
                c = rnd.choice(rows[r])
                wx, wy = cx + c * scale + rnd.randrange(scale - 1), y + r * scale + rnd.randrange(scale - 1)
                p.px(wx, wy, under(wx, wy), L)
                if rnd.random() < 0.5:
                    p.px(wx + 1, wy, under(wx + 1, wy), L)
        cx += (gw + 1) * scale
    return w


def title_plate(p: Pix, box: tuple, night: bool, motion: bool):
    """The steel plate the title is stencilled on, riveted to the tunnel wall over `box` (x0, y0, x1, y1), drawn
    with the sky before the title is set: pale scuffed steel lit along its top and left, a rivet every twelve units
    along its top and its foot, scratches across it and rust weeping from a few rivets, its shadow cast on the
    concrete down and to the right; and at its upper corners the two work lamps that light it, green, flickering,
    their light pooled on the plate by night. The drawing keeps the box, for the stencil's cuts (see
    `stencil_title`)."""
    x0, y0, x1, y1 = box
    p.plate = box
    k = -3 if night else 0
    face = C["plate_night"] if night else PLATE[4]
    q = _shade(PLATE, k)
    L = p.layer("plate", z=-1)
    shadow = (TUNNEL[0] + ":0.5") if night else (CONCRETE[1] + ":0.45")
    for i in (1, 2):                                            # its shadow on the wall
        p.hline(x0 + i, x1 + i, y1 + i - 1, shadow, L)
        p.vline(x1 + i, y0 + i, y1 + i - 1, shadow, L)
    p.shapes[L].append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{face}"/>')
    p.box(x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2, STEEL[0], L)
    p.hline(x0, x1, y0, q(6), L)
    p.vline(x0, y0, y1, q(5), L)
    p.hline(x0 + 1, x1, y1 - 1, q(2), L)
    p.vline(x1 - 1, y0 + 1, y1, q(2), L)
    rivet = {(0, 0): q(6), (1, 0): q(2), (0, 1): q(1)}
    p.defs.append(f'<pattern id="rv" x="{x0 + 3}" y="{y0 + 2}" width="12" height="2" patternUnits="userSpaceOnUse">'
                  f'{p.markup(rivet)}</pattern>')
    for yy in (y0 + 2, y1 - 3):                                 # a rivet every twelve units along top and foot
        p.shapes[p.layer("rivets", z=-0.9)].append(
            f'<rect x="{x0 + 3}" y="{yy}" width="{x1 - x0 - 6}" height="2" fill="url(#rv)"/>')
    for xx in range(x0 + 15, x1 - 3, 36):                      # rust weeping from a few of them
        for j in range(4, 7):
            p.px(xx + 1, y0 + j, RUST[3] + ":0.5" if not night else RUST[1] + ":0.6", L)
    rnd = random.Random(7)
    for _ in range(6):                                          # scratches
        sx, sy = rnd.randrange(x0 + 4, x1 - 8), rnd.randrange(y0 + 3, y1 - 3)
        for i in range(rnd.randint(3, 6)):
            p.px(sx + i, sy - i // 2, q(6) if not night else q(4), L)
    for lx in (x0 + 2, x1 - 6):                                 # the work lamps
        p.rect(lx, y0 + 1, 4, 2, _t(STEEL, 3 + k))
        p.hline(lx, lx + 4, y0 + 1, _t(STEEL, 5 + k))
        bulb = p.flicker(0 if lx == x0 + 2 else 2) if motion else "base"
        p.hline(lx + 1, lx + 3, y0 + 3, FLAME[5], bulb)
        p.px(lx, y0 + 3, _t(STEEL, 1 + k))
        p.px(lx + 3, y0 + 3, _t(STEEL, 1 + k))
        if night:
            p.halo(lx + 2, y0 + 6, 26, 14, FLAME[3], (0.04, 0.07, 0.1), L=p.flicker(1, back=True) if motion
                   else "haze")


def beam(p: Pix, lens: tuple, night: bool, motion: bool, keep: tuple, floor: int):
    """The signature of the tunnel's sky: the beam of the ship's searchlight, from its lens at `lens` out across the
    sheet behind the title, a long cone of phosphor brighter down its middle, sweeping slowly up toward the pipes and
    back down toward the far wall in steps, never lower than its lens, so it ends above the words under the title;
    by night dust hangs in it, glinting. It is clipped to the sky above row `floor` and kept out of the box `keep`
    (the month's mark). The still file holds it partway up."""
    lx, ly = lens
    reach, half, core = 430, 30, 11
    a = (0.1, 0.15) if night else (0.12, 0.18)
    cone = (f'<path fill="{FLAME[4]}" fill-opacity="{a[0]}" d="M{lx} {ly - 1}L{lx + reach} {ly - half}V{ly + half}'
            f'L{lx} {ly + 2}z"/><path fill="{FLAME[5]}" fill-opacity="{a[1]}" d="M{lx} {ly}L{lx + reach} '
            f'{ly - core}V{ly + core}L{lx} {ly + 1}z"/>')
    dust = ""
    if night:
        rnd = random.Random(3)
        groups = []
        for n in range(3):
            pts = []
            for _ in range(5):
                dx = rnd.randrange(40, 380)
                dy = round(rnd.uniform(-0.8, 0.8) * half * dx / reach)
                pts.append(f"M{lx + dx} {ly + dy + 0.5}h1")
            vals = ("1;.2;1", ".2;1;.2", "1;1;.2")[n]
            groups.append(f'<path stroke="{FLAME[6]}" d="{"".join(pts)}">'
                          + (f'<animate attributeName="opacity" values="{vals}" dur="1.5s" repeatCount="indefinite" '
                             f'calcMode="discrete"/>' if motion else "") + '</path>')
        dust = "".join(groups)
    kx0, ky0, kx1, ky1 = keep
    cid = "bmc"
    clip = (f'<clipPath id="{cid}"><path clip-rule="evenodd" d="M{EDGE} 3H{p.w - EDGE}V{floor}H{EDGE}z'
            f'M{kx0} {ky0}H{kx1}V{ky1}H{kx0}z"/></clipPath>')
    angles = (-6, -9, -13, -18, -24, -30, -36, -30, -24, -18, -13, -9)
    still = f'{clip}<g clip-path="url(#{cid})"><g transform="rotate(-13 {lx} {ly})">{cone}{dust}</g></g>'
    if not motion:
        p.raw(-18, still, still)
        return
    vals = ";".join(f"{v} {lx} {ly}" for v in angles)
    moving = (f'{clip}<g clip-path="url(#{cid})"><g>{cone}{dust}<animateTransform attributeName="transform" '
              f'type="rotate" values="{vals}" dur="{num(SWEEP)}s" repeatCount="indefinite" calcMode="discrete"/>'
              f'</g></g>')
    p.raw(-18, moving, still)


# --------------------------------------------------------------------------- the water
def water(p: Pix, x0, x1, g, night: bool, motion: bool, glints=()):
    """The channel of black water along the tunnel's floor from x0 to x1, its surface at row g - 6 catching a line of
    light, ripples drifting over it in two frames, and every light over it laid on it as a broken streak that
    shimmers, stepping between two frames: `glints` are (x, width, colour)."""
    top = g - 6
    p.wet = getattr(p, "wet", []) + [(x0, x1)]          # where the litter on a rule keeps off (see `debris`)
    body, deep, surface = (TUNNEL[2], TUNNEL[1], TUNNEL[5]) if night else (WATER[2], WATER[1], WATER[5])
    p.shapes["base"].append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{g - top + 1}" fill="{body}"/>'
                            f'<rect x="{x0}" y="{top + 3}" width="{x1 - x0}" height="{g - top - 2}" fill="{deep}"/>')
    p.hline(x0, x1, top, surface)
    rnd = random.Random(x0 * 3 + g)
    ripples = [(rnd.randrange(x0, x1 - 4), top + rnd.choice((2, 4)), rnd.randint(2, 4))
               for _ in range((x1 - x0) // (28 if p.lite else 14))]     # a drawing made lighter keeps half of them
    for f in range(2):
        L = p.seq(f"rp{x0}{f}", f / 2, (f + 1) / 2, 1.6, keep=f == 0, z=0.5) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        for rx, ry, rw in ripples:
            p.hline(rx + f * 2, rx + f * 2 + rw, ry, (TUNNEL[4] if night else WATER[4]), L)
        for gx, gw, col in glints:
            for j, yy in enumerate(range(top + 1, g + 1)):
                wdt = gw - j * 2
                if wdt < 2 or (j + f) % 2:
                    continue
                off = (1, -1, 2, 0)[(j + f) % 4] - wdt // 2
                cut = 2 + (j + f * 2) % 3
                a = ":0.75" if j < 2 else ":0.45"
                p.hline(gx + off, gx + off + cut, yy, col + a, L)
                p.hline(gx + off + cut + 1, gx + off + wdt, yy, col + a, L)


def wash(p: Pix, xs, g, night: bool, motion: bool):
    """The water churned up under the hover pads at columns `xs`: spray thrown up off the surface at row g - 6 in
    two frames that alternate, white by day and lit green by night."""
    top = g - 6
    col = (FLAME[5] + ":0.65") if night else (X["drop"] + ":0.9")
    for f in range(2):
        L = p.seq(f"ws{f}", f / 2, (f + 1) / 2, 0.8, keep=f == 0, z=0.7) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        for x in xs:
            for dx, dy in ((-6, 0), (-4, -1), (-2, -2), (0, -1), (2, -2), (4, -1), (6, 0), (-7, -2), (7, -1))[f::2]:
                p.px(x + dx, top + dy, col, L)
            for dx in (-8, -5, 5, 8):
                p.px(x + dx + f, top - 3 - (dx % 2), col, L)


def mist(p: Pix, spans, g, night: bool, motion: bool):
    """Mist lying on the water just over its surface at row g - 6, in the spans (x0, x1) given: long thin wisps
    that drift a step and back in two frames."""
    col = (FLAME[2] + ":0.3") if night else (CONCRETE[6] + ":0.6")
    rnd = random.Random(g)
    for f in range(2):
        L = p.seq(f"ms{f}", f / 2, (f + 1) / 2, 6.0, keep=f == 0, z=0.8) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        for x0, x1 in spans:
            for i in range((x1 - x0) // (18 if p.lite else 9)):         # a drawing made lighter, half the wisps
                wx = x0 + rnd.randrange(max(1, x1 - x0 - 8)) + f * 3
                p.hline(wx, min(x1, wx + rnd.randint(4, 8)), g - 7 - (i % 2), col, L)


def steam(p: Pix, x, y, night: bool, motion: bool, reach: int):
    """Steam leaking from a joint of the main at (x, y) and rolling out along the tunnel's ceiling under the pipes as
    far as column `reach`: billows heaped along it, soft at their edges and fainter the farther they have rolled,
    the bank drifting a step along and back on a slow loop. By night it carries the lamps' green. The still file
    holds it where it starts."""
    col, edge = (FLAME[4], FLAME[3]) if night else (CONCRETE[6], CONCRETE[5])
    k = 0.55 if night else 1.0
    parts, cx, i = [], x + 3, 0
    while cx < reach - 4:
        r = 3 + min(4, i)
        a = max(0.16, 0.55 - i * 0.06) * k
        cy = y + 4 + r * 0.6 + (i % 2)
        outer, inner = num(round(a * 0.6 * 25) / 25), num(round(a * 25) / 25)
        parts.append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(r * 1.6)}" ry="{num(r)}" fill="{edge}" '
                     f'fill-opacity="{outer}"/><ellipse cx="{num(cx)}" cy="{num(cy - 0.5)}" '
                     f'rx="{num(r * 1.1)}" ry="{num(r * 0.65)}" fill="{col}" fill-opacity="{inner}"/>')
        cx += r * 1.9
        i += 1
    bank = "".join(parts)
    if not motion:
        p.raw(5, bank, bank)
        return
    p.raw(5, f'<g>{bank}<animateTransform attributeName="transform" type="translate" values="0 0;2 0;4 1;2 1" '
             f'dur="6s" repeatCount="indefinite" calcMode="discrete"/></g>', bank)


# --------------------------------------------------------------------------- the ship
def ship_place(g):
    """Where the ship hovers in a header whose ground is row g: its stern's column, the row of its deck, and its
    searchlight's lens, which the sky's beam is drawn from before the ship is (see `beam`)."""
    x0, y0 = 8, g - 13 - (HULL - 1)
    return x0, y0, (x0 + 29, y0 - 20)


def _crown(x):
    """The row of the hull's crown at column x from its stern: chamfered at the stern, a flat deck, and rounded down
    toward the nose."""
    n = SHIP_L - 12
    if x < 2:
        return 2 - x
    if x >= n:
        return round(6 * (1 - math.sqrt(max(0.0, 1 - ((x - n) / 12) ** 2))))
    return 0


def _keel(x):
    """The row of the hull's keel at column x: swept up a little at the stern and under the nose."""
    n = SHIP_L - 15
    if x < 3:
        return HULL - 1 - (3 - x)
    if x >= n:
        return HULL - 1 - round(8 * (1 - math.sqrt(max(0.0, 1 - ((x - n) / 15) ** 2))))
    return HULL - 1


def ship(p: Pix, x0, y0, night: bool, motion: bool) -> dict:
    """The ship, an armoured hovercraft seen side on and heading right, its stern at column x0 and its deck at row
    y0: a deep hull rounded at the nose, its plates of gunmetal lit along its crown and its upper flank and in shade
    toward the keel, seamed, riveted, patched with plates of another age, dented and scorched, a row of portholes;
    the armoured cockpit at the prow with its windows along its sloped face, lit phosphor by night, a railing along
    the deck; a lattice mast amidships with the searchlight at its head, its lens burning; an aerial with a light
    blinking at its tip;
    two hover pads under the keel glowing phosphor, flickering, their light on the keel; and a cable hanging loose.
    Returns where its pads are."""
    k = -2 if night else 0
    s = _shade(STEEL, k)
    cells = {}
    for x in range(SHIP_L):
        t, b = _crown(x), _keel(x)
        for y in range(t, b + 1):
            d = y - t
            if y in (t, b):
                c = STEEL[0]
            elif d == 1:
                c = s(6)
            elif d <= 3:
                c = s(5)
            elif y < 8:
                c = s(4)
            elif y == 8:
                c = s(2)
            elif y < 12:
                c = s(3)
            else:
                c = s(2) if y < b - 1 else s(1)
            cells[(x, y)] = c
    for (x, y) in list(cells):                                 # the stern's face toward the light, the nose's away
        if (x - 1, y) not in cells:
            cells[(x, y)] = STEEL[0]
            if (x + 1, y) in cells and cells[(x + 1, y)] != STEEL[0]:
                cells[(x + 1, y)] = s(5)
        elif (x + 1, y) not in cells:
            cells[(x, y)] = STEEL[0]
            if cells.get((x - 1, y)) not in (None, STEEL[0]):
                cells[(x - 1, y)] = s(2)
    for x in (10, 18, 26, 34):                                 # seams, riveted
        for y in range(2, 8):
            if cells.get((x, y)) not in (None, STEEL[0]):
                cells[(x, y)] = s(2)
        cells[(x + 1, 2)] = s(6)
        for y in range(9, 14):
            if cells.get((x + 4, y)) not in (None, STEEL[0]):
                cells[(x + 4, y)] = s(1)
        for rx in range(x + 2, x + 8, 3):
            if (rx, 3) in cells:
                cells[(rx, 3)] = s(6)
    for px_, py_, w_, h_, tone in ((13, 9, 6, 3, RUST), (28, 3, 5, 3, RUST), (21, 10, 4, 3, STEEL)):
        for y in range(py_, py_ + h_):                         # patches of another age
            for x in range(px_, px_ + w_):
                cells[(x, y)] = _t(tone, (5 if y == py_ else 3) + k - (tone is STEEL))
        for q in ((px_, py_ + 1), (px_ + w_ - 1, py_ + 1), (px_, py_ + h_ - 1), (px_ + w_ - 1, py_ + h_ - 1)):
            cells[q] = s(6)
    for dx, dy in ((0, 0), (1, 0), (2, 0), (1, 1), (2, 1), (3, 1), (1, -1)):   # a scorch toward the nose
        cells[(37 + dx, 6 + dy)] = s(1)
    for dx, dy in ((7, 11), (31, 12), (40, 9)):                # dents
        cells[(dx, dy)] = s(1)
        cells[(dx - 1, dy - 1)] = s(6)
    for x in range(6, SHIP_L - 13, 6):                         # portholes
        cells[(x, 5)] = FLAME[4] if night else s(1)
        cells[(x + 1, 5)] = FLAME[3] if night else s(1)
        cells[(x, 4)] = s(6) if not night else s(4)
    for r in range(1, 8):                                      # the armoured cockpit at the prow, its face sloped
        a, b = 27, SHIP_L - 6 - r
        for x in range(a, b):
            cells[(x, -r)] = s(6) if r == 7 else s(5) if x == a else s(2) if x == b - 1 else s(4)
        cells[(a - 1, -r)] = STEEL[0]
        cells[(b, -r)] = STEEL[0]
    for x in range(26, SHIP_L - 13):
        cells[(x, -8)] = STEEL[0]
    for r in (3, 4, 5):                                        # its windows along the slope
        b = SHIP_L - 6 - r
        for x in range(b - 7, b - 1):
            if cells.get((x, -r)) not in (None, STEEL[0]):
                strut = (x - b) % 3 == 0
                cells[(x, -r)] = s(3) if strut else (FLAME[4] if r > 3 else FLAME[6]) if night else \
                    (s(1) if r < 5 else s(6))
    for x in range(1, 27):                                     # the railing along the deck
        if x % 4 == 1:
            cells[(x, -2)] = s(2)
            cells[(x, -1)] = s(2)
        cells[(x, -3)] = s(5) if x > 2 else s(4)
    for (x, y), c in cells.items():
        p.px(x0 + x, y0 + y, c)
    # the lattice mast and the searchlight at its head
    mx = x0 + 22
    for yy in range(y0 - 18, y0):
        p.px(mx, yy, s(5))
        p.px(mx + 3, yy, s(2))
        p.px(mx + 1 + (yy % 4 < 2), yy, s(3) if (yy % 2) else s(1))
    for yy in range(y0 - 16, y0, 4):
        p.hline(mx, mx + 4, yy, s(4))
    hx, hy = x0 + 23, y0 - 22
    p.box(hx - 1, hy - 1, 8, 6, STEEL[0])
    p.rect(hx, hy, 6, 4, s(3))
    p.hline(hx, hx + 6, hy, s(5))
    p.vline(hx, hy, hy + 4, s(4))
    p.hline(hx, hx + 6, hy + 3, s(1))
    p.px(x0 + 29, y0 - 21, FLAME[6])
    p.px(x0 + 29, y0 - 20, FLAME[5])
    p.px(x0 + 30, y0 - 21, FLAME[5])
    p.halo(x0 + 30, y0 - 20, 4, 3, FLAME[5], (0.25, 0.5) if night else (0.15, 0.3), L="haze")
    # the aerial
    p.vline(x0 + 10, y0 - 13, y0 - 3, s(5))
    p.px(x0 + 10, y0 - 14, FLAME[5], p.blink(1) if motion else "base")
    # the pads and their glow
    pads = []
    for i, px_ in enumerate((5, 25)):
        ax = x0 + px_
        p.hline(ax, ax + 13, y0 + HULL, s(3))
        p.hline(ax, ax + 13, y0 + HULL + 1, s(1))
        p.px(ax, y0 + HULL, STEEL[0])
        p.px(ax + 12, y0 + HULL, STEEL[0])
        L = p.flicker(i) if motion else "base"
        p.hline(ax + 1, ax + 12, y0 + HULL + 2, FLAME[5], L)
        p.hline(ax + 3, ax + 10, y0 + HULL + 2, FLAME[6], L)
        pads.append(ax + 6)
        p.halo(ax + 6.5, y0 + HULL + 4, 10, 3, FLAME[3], (0.14, 0.3) if night else (0.08, 0.16), L="haze")
    for j in range(8):                                         # a cable hanging loose at the stern
        p.px(x0 + 1 + j, y0 + HULL - 1 + round(3 * math.sin(math.pi * j / 7)), STEEL[0] if j % 3 else s(1))
    if night:
        for (qx, qy) in [q for q in cells if q[1] >= HULL - 3]:
            near = min(abs(x0 + qx - pc) for pc in pads)
            if near < 8:
                p.apx(x0 + qx, y0 + qy, FLAME[4], 0.3 if qy >= HULL - 2 else 0.15, "base")
    return dict(pads=pads)


# --------------------------------------------------------------------------- the drain and the machine
def headwall(p: Pix, x0, x1, top, bottom, night: bool):
    """The brick headwall the drain comes out through, from x0 to x1 and row `top` down to the water at `bottom`:
    courses of brick in a pattern, a stone coping along its top and a quoin of headers down its left edge."""
    k = -4 if night else 0
    b = _shade(BRICK, k)
    mortar = TUNNEL[2] if night else CONCRETE[3]
    cells = {}
    for yy in range(6):
        for xx in range(12):
            row = yy // 3
            if yy % 3 == 2 or (xx + row * 6) % 12 == 11:
                cells[(xx, yy)] = mortar
            elif yy % 3 == 0:
                cells[(xx, yy)] = b(5)
            else:
                cells[(xx, yy)] = b(4) if (xx + row * 6) % 12 < 6 else b(3)
    p.defs.append(f'<pattern id="bw" x="{x0}" y="{top}" width="12" height="6" patternUnits="userSpaceOnUse">'
                  f'{p.markup(cells)}</pattern>')
    p.shapes["base"].append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" fill="url(#bw)"/>')
    p.hline(x0 - 1, x1, top - 2, _t(CONCRETE, 6 + k) if not night else TUNNEL[5])
    p.hline(x0 - 1, x1, top - 1, _t(CONCRETE, 3 + k) if not night else TUNNEL[3])
    p.hline(x0, x1, top, (TUNNEL[0] if night else CONCRETE[1]) + ":0.5")
    for yy in range(top, bottom):
        p.px(x0, yy, b(6) if (yy - top) % 6 < 3 else b(2))
        p.px(x0 - 1, yy, BRICK[0])


def outlet(p: Pix, cx, cy, r, night: bool):
    """The great drain's mouth centred on (cx, cy), `r` across its opening, set in the headwall under an arch of
    brick voussoirs a third of its radius deep, lit on the arch's upper left: inside, the pipe's concrete rings
    recede into the black, each a little smaller, darker and lower than the last, slime along their foot, and a stone
    sill under the mouth where the water spills over. Returns the sill's row."""
    k = -3 if night else 0
    b = _shade(BRICK, k)
    ring = r + 5
    mortar = TUNNEL[3] if night else CONCRETE[3]
    inner = TUNNEL if night else CONCRETE
    for y in range(cy - ring - 1, cy + ring + 2):
        for x in range(cx - ring - 1, cx + ring + 2):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                # the rings receding: each band of the pipe's depth drawn smaller and lower than the one before
                depth = 0
                for n in range(1, 5):
                    rr = r * (1 - 0.2 * n)
                    if math.hypot(x + 0.5 - cx - n * 0.8, y + 0.5 - cy - n * 1.2) <= rr:
                        depth = n
                tone = (inner[3] if not night else inner[4], inner[2] if not night else inner[3], inner[1], inner[0],
                        TUNNEL[0])[depth]
                if not night and depth == 0 and (y - cy) > r * 0.55:
                    tone = WATER[3]
                p.px(x, y, tone if depth < 4 else IRON[0])
            elif d <= ring:
                ang = math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx)) % 360
                seg = int(ang // 24)
                if abs(ang - seg * 24) < 1.6:
                    p.px(x, y, mortar)
                else:
                    lit = (x - cx) + (y - cy) < -r * 0.4
                    if night:
                        p.px(x, y, b(5) if lit else b(4))
                    else:
                        p.px(x, y, b(5) if lit else b(3) if d < ring - 1.2 else b(2))
    sill = cy + r - 1
    p.hline(cx - r - 3, cx + r + 4, sill, _t(CONCRETE, 6 + k) if not night else TUNNEL[5])
    p.hline(cx - r - 3, cx + r + 4, sill + 1, _t(CONCRETE, 3 + k) if not night else TUNNEL[3])
    for i in range(6):
        p.vline(cx - 6 + i * 2, sill + 2, sill + 5 + (i * 3) % 8, _t(WATER, 4 if not night else 1) + ":0.7")
    return sill + 1


def _tentacle(p: Pix, pts, L, tones, thick: int):
    """A tentacle of iron segments along the points `pts`, two points a segment: each lit, then in shade, in turn,
    the first `thick` points a unit thicker underneath."""
    for j, (tx, ty) in enumerate(pts):
        p.px(tx, ty, tones[0] if (j // 2) % 2 == 0 else tones[1], L)
        if j < thick:
            p.px(tx, ty + 1, tones[2], L)



# The machine's face: a dozen eyes clustered on it, (column, row) of each eye's lit corner.
EYES = ((7, 3), (11, 3), (4, 6), (8, 6), (12, 6), (2, 9), (6, 9), (10, 9), (14, 9), (5, 12), (9, 12), (13, 12))


def _head(night: bool) -> dict:
    """The machine's head as {(x, y): colour}, face first to the left: a carapace of iron plates forty units long,
    round like a squid's mantle, lit from the upper left and ridged between its plates; a disc of a face at its front
    set with a dozen red eyes, each burning at its upper left; outlined in the darkest iron."""
    k = -1 if night else 0
    cells = {}
    cx, cy, rx, ry = 25, 8.5, 15, 8.5
    for y in range(18):
        for x in range(41):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1:
                nz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
                lam = max(0.0, dx * LX + dy * LY + nz * LZ)
                t = (1, 3, 4, 6)[min(3, int(lam * 4))]
                if (x - 14) % 6 == 0 and 1 < y < 16:
                    t = max(0, t - 2)
                cells[(x, y)] = _t(IRON, t + k)
    for y in range(18):
        for x in range(20):
            if (x + 0.5 - 9.5) ** 2 + (y + 0.5 - 8.5) ** 2 <= 8.5 ** 2:
                cells[(x, y)] = IRON[1]
    for ex, ey in EYES:
        cells[(ex, ey)] = EYE[6]
        cells[(ex + 1, ey)] = EYE[4]
        cells[(ex, ey + 1)] = EYE[4]
        cells[(ex + 1, ey + 1)] = EYE[2]
    edge = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in cells:
                edge[(x + dx, y + dy)] = IRON[0]
    cells.update(edge)
    return cells


def _curve(a, b, c, n):
    """n + 1 whole units along the quadratic curve from a through the pull of b to c."""
    out = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0]
        y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]
        q = (round(x), round(y))
        if not out or out[-1] != q:
            out.append(q)
    return out


def sentinel(p: Pix, x, y, night: bool, motion: bool, mouth: tuple, floor: int, reach_x: int, reach_y: int = TOP + 4):
    """The machine coming out of the great drain, the front of its head at (x, y), lunging left: a carapace of iron
    plates, round like a squid's mantle, and a face of a dozen red eyes, three of them blinking; hooked feelers
    under its face; its tentacles spread wide, streaming back into the dark of the drain, reaching out across the
    wall as far left as column `reach_x` and as high as row `reach_y`, and hanging down over the headwall toward the
    water at row `floor`,
    swaying in two frames. Its eyes throw their red: by night on the brick round it, on its own plates and in a
    glow round its face, and by day a red glint on its plates."""
    k = -1 if night else 0
    mx, my, mr = mouth
    tones = (_t(IRON, 5 + k), _t(IRON, 3 + k), IRON[0])
    for t in range(4):                                         # streaming back into the drain
        a = (x + 34, y + 5 + t * 2)
        pts = [q for q in _curve(a, (mx - 4, my + t * 2 - 3), (mx + 2, my + t - 1), 40)
               if math.hypot(q[0] + 0.5 - mx, q[1] + 0.5 - my) >= mr - 2]
        _tentacle(p, pts, "base", tones, len(pts))
    for t in range(2):                                         # reaching out across the wall
        a = (x + 24 + t * 6, y + 1)
        end = (reach_x + t * 18, reach_y + t * 4)
        pts = _curve(a, ((a[0] + end[0]) // 2 + 6, end[1] - 4 + t * 2), end, 70)
        _tentacle(p, pts, "base", tones, len(pts) * 3 // 4)
        p.px(end[0] - 1, end[1], tones[1])
    a = (x + 27, y + 16)                                       # one hanging still, its tip in the water
    pts = _curve(a, (a[0] - 4, (a[1] + floor) // 2), (a[0] + 2, floor - 1), floor - a[1])
    _tentacle(p, pts, "base", tones, len(pts) // 2)
    for t in range(2):                                         # and along the wall to the right
        a = (x + 38, y + 9 + t * 4)
        pts = _curve(a, (a[0] + 12, a[1] + 12 + t * 4), (p.w - EDGE - 1, a[1] + 6 + t * 10), 40)
        _tentacle(p, pts, "base", tones, len(pts) // 2)
    head = _head(night)
    for (hx, hy), c in head.items():
        p.px(x + hx, y + hy, c)
    for ex, ey in (EYES[1], EYES[6], EYES[10]):
        p.px(x + ex, y + ey, C["white"] if night else EYE[6], p.blink(ex % 3) if motion else "base")
    for i in range(6):                                         # the hooked feelers under its face
        fx = x + 3 + i * 3
        for j in range(4):
            p.px(fx - j // 2 - (j == 3), y + 18 + j, tones[j % 2])
    for f in range(2):                                         # hanging toward the water
        L = p.seq(f"tn{f}", f / 2, (f + 1) / 2, 4.2, keep=f == 0, z=0.6) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        for t, rx in enumerate((x + 20, x + 33)):
            ry = y + 16
            length = max(0, floor - ry - 3 - t * 4)
            sway = 2 * f - 1
            pts = [(rx + round(math.sin(j / 5 + t * 1.9 + f * 0.7) * 2 + sway * j / max(1, length) * 3 - j * 0.1),
                    ry + j) for j in range(length)]
            _tentacle(p, pts, L, tones, length // 2)
    fx, fy = x + 9, y + 9
    if night:
        p.halo(fx, fy, 22, 15, EYE[3], (0.05, 0.1, 0.16), L="haze")
        p.halo(fx + 22, fy + 8, 24, 18, EYE[3], (0.06, 0.12), L="base")
    plates = set(_t(IRON, n + k) for n in range(1, 7))
    for (hx, hy), c in head.items():
        if c in plates and 14 < hx < 24 and math.hypot(hx - 9, hy - 9) < 14:
            p.apx(x + hx, y + hy, EYE[4], 0.32 if night else 0.18, "base")


def lurker(p: Pix, mouth: tuple, night: bool, motion: bool, floor: int):
    """The machine still in the drain, where a header leaves the drain too little room to come out: only the cluster
    of its red eyes in the dark of the pipe, two of them blinking, and the ends of its tentacles hanging over the lip
    toward the water at row `floor`, swaying in two frames."""
    k = -1 if night else 0
    mx, my, mr = mouth
    ex, ey = mx - 2, my - 1
    for dx, dy, c in ((0, 0, EYE[5]), (2, 1, EYE[4]), (-2, 1, EYE[4]), (1, -2, EYE[3]), (-1, 2, EYE[3]),
                      (3, -1, EYE[3]), (-3, -1, EYE[3]), (0, 2, EYE[4])):
        p.px(ex + dx, ey + dy, c)
    for dx, dy in ((0, 0), (2, 1)):
        p.px(ex + dx, ey + dy, EYE[6], p.blink(dx % 3) if motion else "base")
    if night:
        p.halo(ex + 0.5, ey + 0.5, 5, 4, EYE[3], (0.1, 0.2), L="haze")
    tones = (_t(IRON, 5 + k), _t(IRON, 3 + k), _t(IRON, 1 + k))
    for f in range(2):
        L = p.seq(f"lk{f}", f / 2, (f + 1) / 2, 4.2, keep=f == 0, z=0.6) if motion else ("base" if f == 0 else None)
        if L is None:
            continue
        for t, rx in enumerate((mx - 5, mx + 1)):
            ry = my + mr - 1
            length = max(0, min(floor - ry - 2, 16 - t * 4))
            pts = [(rx + round(math.sin(j / 4 + t * 2 + f * 0.8) * 1.5 + (2 * f - 1) * j / 10), ry + j)
                   for j in range(length)]
            _tentacle(p, pts, L, tones, length // 2)


SCAN = 7.0        # the seconds a hanging machine's red gaze takes to sweep the water and back


def hanging(p: Pix, x, y, night: bool, motion: bool, grip: int, floor: int, keep: tuple) -> tuple:
    """A machine hanging from the pipes over the channel, the front of its head at (x, y), facing left: three
    tentacles reach up from its carapace and coil round the pipe at row `grip`, its dozen red eyes burn, three of
    them blinking, its feelers curl under its face, and its tentacles trail down to the water at row `floor`,
    swaying in two frames. Its gaze sweeps the water under it, a cone of red light swinging slowly down and back,
    kept inside the box `keep` (x0, y0, x1, y1); by night its eyes' red glows round its face and lies on its own
    plates. Returns where its eyes' light falls on the water, for the water's glints."""
    k = -1 if night else 0
    tones = (_t(IRON, 5 + k), _t(IRON, 3 + k), IRON[0])
    for t in range(3):                                         # up to the pipe, coiled round it
        a = (x + 18 + t * 8, y + 1)
        gx = x + 14 + t * 11
        pts = _curve(a, (a[0] + (t - 1) * 4, (a[1] + grip) // 2), (gx, grip + 3), max(8, a[1] - grip) * 2)
        _tentacle(p, pts, "base", tones, len(pts) // 3)
        for dx, dy in ((0, 2), (1, 1), (2, 0), (3, -1), (3, 0), (2, 1)):
            p.px(gx + dx - 1, grip + dy - 1, tones[(dx + dy) % 2])
        p.px(gx + 3, grip - 2, tones[2])
    for t, (dx, length) in enumerate(((20, 0), (27, 4), (33, 2), (38, 6))):   # trailing down to the water
        for f in range(2):
            L = p.seq(f"hg{f}", f / 2, (f + 1) / 2, 4.6, keep=f == 0, z=0.6) if motion else \
                ("base" if f == 0 else None)
            if L is None:
                continue
            rx, ry = x + dx, y + 15
            n = max(0, floor - ry - 2 - length)
            pts = [(rx + round(math.sin(j / 5 + t * 1.7 + f * 0.8) * 2 + (2 * f - 1) * j / max(1, n) * 3
                               - j * 0.12), ry + j) for j in range(n)]
            _tentacle(p, pts, L, tones, n // 2)
    head = _head(night)
    for (hx, hy), c in head.items():
        p.px(x + hx, y + hy, c)
    for ex, ey in (EYES[0], EYES[7], EYES[9]):
        p.px(x + ex, y + ey, C["white"] if night else EYE[6], p.blink(ex % 3) if motion else "base")
    for i in range(6):                                         # the hooked feelers under its face
        fx = x + 3 + i * 3
        for j in range(4):
            p.px(fx - j // 2 - (j == 3), y + 18 + j, tones[j % 2])
    plates = set(_t(IRON, n + k) for n in range(1, 7))
    for (hx, hy), c in head.items():
        if c in plates and 14 < hx < 26 and math.hypot(hx - 9, hy - 9) < 15:
            p.apx(x + hx, y + hy, EYE[4], 0.32 if night else 0.18, "base")
    if night:
        p.halo(x + 9, y + 9, 20, 14, EYE[3], (0.05, 0.1, 0.16), L="haze")
    # its gaze: a cone of red from its face down across the water, swinging
    ex, ey = x + 8, y + 12
    reach = floor - ey + 6
    a = (0.1, 0.18) if night else (0.08, 0.13)
    cone = (f'<path fill="{EYE[4]}" fill-opacity="{a[0]}" d="M{ex} {ey}L{ex - 13} {ey + reach}H{ex + 13}z"/>'
            f'<path fill="{EYE[5]}" fill-opacity="{a[1]}" d="M{ex} {ey}L{ex - 5} {ey + reach}H{ex + 5}z"/>')
    kx0, ky0, kx1, ky1 = keep
    cid = f"gz{x}"
    clip = f'<clipPath id="{cid}"><rect x="{kx0}" y="{ky0}" width="{kx1 - kx0}" height="{ky1 - ky0}"/></clipPath>'
    angles = (6, 0, -6, -12, -18, -24, -18, -12, -6, 0, 6, 12)
    still = f'{clip}<g clip-path="url(#{cid})"><g transform="rotate(-6 {ex} {ey})">{cone}</g></g>'
    if motion:
        vals = ";".join(f"{v} {ex} {ey}" for v in angles)
        p.raw(0.3, f'{clip}<g clip-path="url(#{cid})"><g>{cone}<animateTransform attributeName="transform" '
                   f'type="rotate" values="{vals}" dur="{num(SCAN)}s" repeatCount="indefinite" calcMode="discrete"/>'
                   f'</g></g>', still)
    else:
        p.raw(0.3, still, still)
    return [(ex + 4, 12, EYE[4] if night else EYE[3])]


def drips(p: Pix, x, y0, y1, night: bool, motion: bool, phase: float = 0.0, dur: float = 2.6):
    """A drop of water gathering at (x, y0) and falling to row y1 in steps, then a splash where it lands; in a loop
    `dur` seconds long. The still file shows the drop hanging at the lip."""
    col = X["drop"] if not night else FLAME[2]
    steps = 6
    if not motion:
        p.px(x, y0, col)
        return
    for i in range(steps):
        t0 = (phase + 0.5 + i * 0.06) % 1
        t1 = min(1.0, t0 + 0.06)
        yy = y0 + round((y1 - y0) * (i / (steps - 1)) ** 1.6)
        L = p.seq(f"dr{x}{i}", t0, t1, dur, z=1)
        p.vline(x, yy, yy + 2, col, L)
    L = p.seq(f"dr{x}s", min(0.94, (phase + 0.86) % 1), min(1.0, (phase + 0.86) % 1 + 0.06), dur, z=1)
    p.px(x - 2, y1 - 1, col, L)
    p.px(x + 2, y1 - 1, col, L)
    p.px(x, y0, col, p.seq(f"dr{x}h", 0.0, 0.5, dur, keep=True, z=1))


# --------------------------------------------------------------------------- a phone's scenes
PHONE_WORLD = 58   # the rows a phone's H1 gives the tunnel under its words


def phone_beam(p: Pix, lens: tuple, box: tuple, night: bool):
    """The ship's searchlight held on the machine, on a phone: a cone of phosphor from its lens across the tunnel to
    the right, brighter down its middle, clipped to the scene's box (x0, y0, x1, y1)."""
    lx, ly = lens
    reach, half, core = 150, 16, 6
    a = (0.1, 0.15) if night else (0.12, 0.18)
    x0, y0, x1, y1 = box
    cid = "pbm"
    p.raw(-18, *(2 * (f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>'
                      f'</clipPath><g clip-path="url(#{cid})"><g transform="rotate(8 {lx} {ly})">'
                      f'<path fill="{FLAME[4]}" fill-opacity="{a[0]}" d="M{lx} {ly - 1}L{lx + reach} {ly - half}'
                      f'V{ly + half}L{lx} {ly + 2}z"/><path fill="{FLAME[5]}" fill-opacity="{a[1]}" d="M{lx} {ly}'
                      f'L{lx + reach} {ly - core}V{ly + core}L{lx} {ly + 1}z"/></g></g>',)))


def phone_world(p: Pix, g, night: bool, top: int) -> list:
    """A phone's H1 under its words, from row `top` to the water at row g, across the phone: the channel of black
    water along the foot with mist on it, the ship hovering over it at the left, its searchlight held on the drain at
    the right, where the machine comes out of the headwall, its tentacles reaching out across the tunnel; where the
    rows are too few for the machine to come out, only its eyes in the dark of the drain."""
    x0, y0, lens = ship_place(g)
    phone_beam(p, lens, (lens[0], top, p.w - EDGE, g - 6), night)
    wall_top = top + 4
    headwall(p, 138, p.w - EDGE, wall_top, g - 6, night)
    glints = []
    if g - wall_top >= 44:
        r = 12
        cx, cy = 160, wall_top + r + 2
        lip = outlet(p, cx, cy, r, night)
        sentinel(p, 112, cy - 3, night, False, (cx, cy, r), g - 7, 66, top + 2)
        drips(p, cx + 5, lip + 1, g - 7, night, False)
        if night:
            glints.append((122, 10, EYE[3]))
    else:
        r = 9
        cx, cy = 158, wall_top + r + 4
        outlet(p, cx, cy, r, night)
        lurker(p, (cx, cy, r), night, False, g - 7)
    shp = ship(p, x0, y0, night, False)
    wash(p, shp["pads"], g, night, False)
    glints += [(x, 11, FLAME[4] if night else FLAME[2]) for x in shp["pads"]]
    water(p, EDGE, p.w - EDGE, g, night, False, glints)
    mist(p, [(5, 60), (130, 175)], g, night, False)
    return [(EDGE, p.w - EDGE)]


def phone_hunter(p: Pix, x0, x1, g, night: bool, top: int):
    """A phone's H3 under its words, from row `top` to the water at row g: a pipe run across the tunnel, flanged, the
    machine hanging from it over the channel, its tentacles trailing to the water and its red gaze held on it, and
    at the right the brick headwall it came out through, water dripping from its drain."""
    k = -2 if night else 0
    s = _shade(STEEL, k)
    py = top + 2
    for j, c in enumerate((s(4), s(6), s(4), s(3), s(1))):
        p.hline(x0, x1, py + j, c)
    p.hline(x0, x1, py + 5, (TUNNEL[0] if night else CONCRETE[2]) + ":0.6")
    for x in range(x0 + 14, x1 - 4, 40):
        p.vline(x, py - 1, py + 6, s(5))
        p.vline(x + 1, py - 1, py + 6, s(2))
        p.vline(x + 2, py, py + 5, s(0))
    wall = x1 - 46
    headwall(p, wall, x1, py + 9, g - 6, night)
    r = 9
    cx, cy = wall + 25, py + 9 + r + 5
    lip = outlet(p, cx, cy, r, night)
    drips(p, cx + 4, lip + 1, g - 7, night, False)
    hx = x0 + 34
    gl = hanging(p, hx, py + 12, night, False, py + 3, g - 6, (x0, py + 8, x1, g - 5))
    water(p, x0, x1, g, night, False, gl)
    mist(p, [(x0 + 2, x1 - 2)], g, night, False)


# --------------------------------------------------------------------------- what hangs, lies and glints
def straws(p: Pix, x0, x1, night: bool, motion: bool, clear=None, keep=()):
    """What hangs under the pipes across a header's top: limescale grown down from the copper line in straws, a drop
    of water at each tip catching the light, and here and there a work lamp in its cage on a short chain, its bulb
    burning phosphor by night and flickering; none in the columns `clear` keeps for the month's mark, and no lamp
    over a box of `keep`."""
    k = -3 if night else 0
    s = _shade(STEEL, -2 if night else 0)
    lime, tip = (TUNNEL[5], FLAME[2]) if night else (CONCRETE[6], X["drop"])
    rnd = random.Random(11 + p.w)
    x, n = x0 + 3 + rnd.randrange(6), 0
    lamps = set(range(x0 + 40, x1 - 20, 92))
    while x < x1 - 2:
        if clear and clear[0] - 3 <= x <= clear[1] + 3:
            x += 3
            continue
        lamp_here = any(abs(x - lx) < 3 for lx in lamps)
        over = any(a - 3 <= x <= c + 3 for a, b, c, d in keep)
        if lamp_here and not over:
            for yy in range(13, 16):
                p.px(x, yy, s(1) if yy % 2 else s(4))
            p.rect(x - 2, 16, 5, 2, s(4))
            p.hline(x - 2, x + 3, 16, s(5))
            bulb = p.flicker(n % 3) if motion and night else "base"
            p.hline(x - 1, x + 2, 18, FLAME[5] if night else PLATE[6], bulb)
            p.px(x, 19, FLAME[6] if night else PLATE[5], bulb)
            p.px(x - 2, 18, s(1))
            p.px(x + 2, 18, s(1))
            if night:
                p.halo(x + 0.5, 18.5, 7, 4, FLAME[3], (0.08, 0.16), L="haze")
            n += 1
            x += 7
            continue
        length = rnd.choice((1, 2, 2, 3, 4))
        p.vline(x, 13, 13 + length, _t(CONCRETE, 5 + k) if length > 2 else lime)
        p.px(x, 13, lime)
        if length > 1:
            p.px(x, 13 + length, tip)
        x += 5 + rnd.randrange(9)


# The machine's head in little, for the mark after SECTION A-A: o its outline, I its lit iron, i its shade, e its eyes,
# t its tentacles.
SENTINEL = ["...oooo...", ".ooIIIIoo.", "oeIeIIIIio", "oIeIeIIiio", "oeIeIIiiio", ".ooiiiioo.", "..t.t.t.t.",
            ".t..t..t.."]


def sentinel_mark(p: Pix, x, y, night: bool):
    """The machine's head in little, its face of red eyes to the left and its tentacles trailing under it."""
    k = -1 if night else 0
    pal = {"o": IRON[0], "I": _t(IRON, 5 + k), "i": _t(IRON, 3 + k), "e": EYE[5] if night else EYE[4],
           "t": _t(IRON, 4 + k)}
    p.sprite(x, y, SENTINEL, pal)


# What lies on a rule: a spanner, a coil of cable, a nut and a puddle with a drop in it.
SPANNER = ["WW.....WW", ".wwwwwww.", "ww.....ww"]
COIL = ["..ooo..", ".oCCCo.", "o.ooo.o", ".ooooo."]
NUT = [".NN.", "nnnn"]


def debris(p: Pix, x0, x1, y, seed: int, night: bool):
    """The tunnel's litter lying on a rule here and there where no scene stands and no word comes within two units:
    a spanner, a coil of cable, a rusted nut, a puddle with a drop of light in it; none in the water of a scene."""
    rnd = random.Random(seed)
    k = -2 if night else 0
    s = _shade(STEEL, k)
    x = x0 + 10 + rnd.randrange(24)
    kinds = ["spanner", "puddle", "coil", "nut"]
    i = rnd.randrange(4)
    while x + 10 < x1:
        kind = kinds[i % 4]
        wet = any(a - 2 <= x + 10 and x - 2 <= b for a, b in getattr(p, "wet", ()))
        if not wet and p.clear_of_words(x - 2, y - 6, x + 12, y + 2):
            if kind == "spanner":
                p.sprite(x, y - 3, SPANNER, {"W": s(5), "w": s(3)})
            elif kind == "coil":
                p.sprite(x, y - 4, COIL, {"o": STEEL[0], "C": s(3)})
            elif kind == "nut":
                p.sprite(x, y - 2, NUT, {"N": _t(RUST, 5 + k), "n": _t(RUST, 2 + k)})
            else:
                p.hline(x, x + 8, y - 1, (TUNNEL[2] if night else WATER[3]))
                p.hline(x + 2, x + 5, y - 1, (TUNNEL[4] if night else WATER[5]))
                p.px(x + 6, y - 1, FLAME[3] if night else X["drop"])
        i += 1
        x += 40 + rnd.randrange(34)


def glints(p: Pix, x0, y0, x1, y1, n: int, seed: int, twinkling: bool, avoid=()):
    """Drops of water on the concrete in the dark, `n` of them between (x0, y0) and (x1, y1), catching what light
    there is, faintly, in the hand's phosphor; none in a box of `avoid`."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, max(x0 + 1, x1)), rnd.randrange(y0, max(y0 + 1, y1))
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        L = p.twinkle(i % 3, back=True) if twinkling else "base"
        p.px(x, y, FLAME[4] + (":0.4" if i % 3 else ":0.6"), L)
        if i % 4 == 0:
            p.px(x, y + 1, FLAME[2] + ":0.3", L)


# --------------------------------------------------------------------------- the footers, the links and the badges
def footing(p: Pix, night: bool, x0: int = EDGE, x1: int | None = None) -> int:
    """The channel of black water along a footer's foot, inside the steel: its surface catching a line of light over
    two rows of water with ripples on them, left out wherever a word comes within a unit of it. Returns the row of
    its surface."""
    x1 = p.w - EDGE if x1 is None else x1
    g = p.h - EDGE - 1
    surface, body, ripple = (TUNNEL[5], TUNNEL[2], TUNNEL[4]) if night else (WATER[5], WATER[2], WATER[4])
    rnd = random.Random(p.w + p.h)
    rip = {(x, g - rnd.randrange(2)) for x in range(x0, x1) if rnd.random() < 0.18}
    for xx in range(x0, x1):
        for yy in (g - 2, g - 1, g):
            if p.clear_of_words(xx - 1, yy - 1, xx + 2, yy + 2):
                p.px(xx, yy, surface if yy == g - 2 else ripple if (xx, yy) in rip else body)
    return g - 2


# The ship in little, for a title block: m its mast, L its searchlight's lens, o the steel's dark, 6 to 2 its plates
# from the lit crown down, w the cockpit's windows, r its railing and the rust patch, p its portholes, G its pads.
MINI_SHIP = [
    "...........m....................",
    "..........mLm...................",
    "...........m....................",
    "...........m..........oooo......",
    "...........m.........o5555o.....",
    ".r..r..r..rmr..r..r.o5wwww5o....",
    "oooooooooooooooooooo66666666oo..",
    "o6666666666666666666666666666oo.",
    "o555p555p555p555p5555555555555o.",
    "o444444444444rrr444444444444444o",
    "o33333333333333333333333333333o.",
    ".o222222222222222222222222222o..",
    "..ooooooooooooooooooooooooooo...",
    "...GGGGGGGG.........GGGGGGGG....",
]


def mini_ship(p: Pix, x, y, night: bool):
    """The ship in little with its top-left at (x, y), hovering, heading right: by night its portholes and cockpit
    windows lit and its pads and lens burning phosphor, flickering. Returns where its lens is."""
    k = -2 if night else 0
    s = _shade(STEEL, k)
    pal = {"m": s(4), "o": STEEL[0], "6": s(6), "5": s(5), "4": s(4), "3": s(3), "2": s(2), "r": _t(RUST, 4 + k)}
    lights = {"L": FLAME[6], "G": FLAME[5], "w": FLAME[4] if night else s(1), "p": FLAME[4] if night else s(1)}
    p.sprite(x, y, MINI_SHIP, pal)
    if night:
        for i, ch in enumerate("LGwp"):
            p.sprite(x, y, MINI_SHIP, {ch: lights[ch]}, L=p.flicker(i % 3))
        p.halo(x + 7.5, y + 15, 7, 2, FLAME[3], (0.12, 0.24), L="haze")
        p.halo(x + 24.5, y + 15, 7, 2, FLAME[3], (0.12, 0.24), L="haze")
    else:
        p.sprite(x, y, MINI_SHIP, lights)
    return x + 11, y + 1


def emblem(p: Pix, x0, x1, g, night: bool) -> bool:
    """The tunnel after a title block's last cell, between columns x0 and x1, over the water at row g: the ship in
    little hovering at the left, its searchlight held on a drain in a brick headwall at the right, where the
    machine's red eyes burn in the dark; by night the ship's lights burn and flicker in phosphor. Drawn only where it
    has room, two units clear of every word; where it has not, the ship alone if it can, and failing that the
    machine's eyes in a drain (see `peeper`). Returns whether anything was."""
    w, top = 72, g - 22
    x = x1 - w - 2
    if x < x0 or top < 5 or not p.clear_of_words(x - 2, top - 2, x1 + 2, g + 1):
        sx = x1 - 34
        if sx >= x0 and g - 18 >= 5 and p.clear_of_words(sx - 2, g - 20, x1 + 1, g + 1):
            mini_ship(p, sx, g - 17, night)
            return True
        dx = x1 - 8                                   # where the ship has no room, the machine's eyes in a drain
        if dx >= x0 and g - 9 >= 5 and p.clear_of_words(dx - 2, g - 10, x1 + 1, g + 1):
            peeper(p, dx, g - 7, night)
            return True
        return False
    lens = mini_ship(p, x, g - 17, night)
    wx = x + w - 18                                   # the headwall and its drain
    k = -4 if night else 0
    b = _shade(BRICK, k)
    mortar = TUNNEL[2] if night else CONCRETE[3]
    for yy in range(top + 2, g - 2):
        for xx in range(wx, x1 - 1):
            row = (yy - top) // 3
            m = (yy - top) % 3 == 2 or (xx - wx + row * 3) % 6 == 5
            p.px(xx, yy, mortar if m else b(5) if (yy - top) % 3 == 0 else b(3))
    p.hline(wx - 1, x1 - 1, top + 1, _t(CONCRETE, 6 + k) if not night else TUNNEL[5])
    p.vline(wx - 1, top + 2, g - 2, BRICK[0])
    cx, cy, r = wx + 8, top + 10, 5
    for yy in range(cy - r - 2, cy + r + 2):
        for xx in range(cx - r - 2, cx + r + 2):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if d <= r:
                p.px(xx, yy, TUNNEL[0] if d < r - 1 else IRON[1])
            elif d <= r + 1.5:
                p.px(xx, yy, b(6) if (xx - cx) + (yy - cy) < 0 else b(2))
    for dx, dy, c in ((-2, -1, EYE[5]), (0, -1, EYE[4]), (2, -1, EYE[5]), (-1, 1, EYE[4]), (1, 1, EYE[5])):
        p.px(cx + dx, cy + dy, c)
    if night:
        p.halo(cx, cy, 6, 5, EYE[3], (0.1, 0.2), L="haze")
    lx, ly = lens                                      # the searchlight's beam on the drain
    a = 0.14 if night else 0.18
    L = p.layer("beam", z=-0.5)
    p.shapes[L].append(f'<path fill="{FLAME[4]}" fill-opacity="{a}" d="M{lx + 1} {ly}L{cx - 2} {cy - 6}V{cy + 6}'
                       f'L{lx + 1} {ly + 1}z"/>')
    return True


def peeper(p: Pix, x, y, night: bool):
    """A drain seven across with its top-left at (x, y), set in a ring of brick lit at its upper left, and in its dark
    the machine's red eyes, watching."""
    k = -4 if night else 0
    b = _shade(BRICK, k)
    cx, cy = x + 3.5, y + 3.5
    for yy in range(y, y + 7):
        for xx in range(x, x + 7):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if d <= 2.2:
                p.px(xx, yy, TUNNEL[0])
            elif d <= 3.6:
                p.px(xx, yy, b(6) if (xx - cx) + (yy - cy) < -1 else b(4) if (xx - cx) + (yy - cy) < 2 else b(2))
    for dx, dy, c in ((2, 3, EYE[5]), (4, 3, EYE[4]), (3, 4, EYE[5])):
        p.px(x + dx, y + dy, c)
    if night:
        p.halo(cx, cy, 4, 3, EYE[3], (0.1, 0.2), L="haze")


VALVE = ["..ooo..", ".o.o.o.", "o..o..o", "oooOooo", "o..o..o", ".o.o.o.", "..ooo.."]


def valve_mark(p: Pix, x, y, night: bool):
    """A valve wheel of rusted iron, its hub lit, for the corner of the closing notes."""
    k = -1 if night else 0
    p.sprite(x, y, VALVE, {"o": _t(RUST, 3 + k), "O": _t(RUST, 6 + k)})


def rivets(p: Pix, x0, x1, y, seed: int, night: bool):
    """A link's steel plate along its top edge: a rivet head in the edge every eight units, lit at its upper left,
    and here and there a flake of rust beside one."""
    rnd = random.Random(seed)
    for x in range(x0 + 4, x1 - 2, 8):
        p.px(x, y, PLATE[6] if not night else STEEL[6])
        p.px(x + 1, y, STEEL[0])
        if rnd.random() < 0.25:
            p.px(x - 1, y, RUST[3] if not night else RUST[2])


def heart(p: Pix, x, y, L="base"):
    """A heart cut from steel plate and painted the machines' red, 7 by 6, the paint lit on its upper-left lobe and
    worn through to the steel at its point."""
    art = [".65.54.", "6554443", "5443332", ".43322.", "..322..", "...s..."]
    pal = {str(i): EYE[i] for i in range(7)}
    pal["s"] = STEEL[4]
    p.sprite(x, y, art, pal, 1, L)


def plate_bar(p: Pix, x0, y0, w, h, period=5, L="base"):
    """A strip of riveted steel plates, `period` wide, pale and dark by turns, each lit along its top, shaded along
    its foot, a seam at its left and a rivet in its corner."""
    for xx in range(x0, x0 + w):
        k = (xx - x0) % period
        dark = ((xx - x0) // period) % 2 == 1
        lit, face, low = (PLATE[3], PLATE[2], PLATE[0]) if dark else (PLATE[6], PLATE[4], PLATE[2])
        for yy in range(y0, y0 + h):
            j = yy - y0
            c = lit if j == 0 else low if j == h - 1 else face
            if k == 0:
                c = STEEL[3]
            elif k == 1 and j == 1:
                c = PLATE[6] if dark else STEEL[4]
            p.px(xx, yy, c, L)


# The links' icons, nine by seven, each from the tunnel: the ship (h its hull, H lit, m its mast, l its searchlight, g
# its pads' glow), the machine (i its iron, I lit, e its eyes), a valve wheel (o rust, O lit) and a caged work lamp (q
# its cage, l its light).
ICONS = {
    "ship": ["...m.....", "...ml....", "..hhhh...", "hhhhhhhhh", "HHHHHHHHh", "hhhhhhhh.", ".g...g..."],
    "machine": ["..iiiii..", ".iIIIIIi.", "iIeIeIeIi", "iIIeIeIIi", ".iIIIIIi.", "..i.i.i..", ".i..i..i."],
    "valve": ["..ooooo..", ".o..o..o.", "o...o...o", "ooooOoooo", "o...o...o", ".o..o..o.", "..ooooo.."],
    "lamp": ["...qqq...", "..qllLq..", "..qlllq..", "..qllLq..", "...qqq...", "....q....", "..qqqqq.."],
}
LINK_ICONS = ("ship", "machine", "valve", "lamp")


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a link's steel plate, by day or by night."""
    return {"h": STEEL[2] if not night else STEEL[4], "H": STEEL[4] if not night else STEEL[6], "m": STEEL[1],
            "l": FLAME[5], "L": FLAME[6], "g": FLAME[3], "i": IRON[1] if not night else IRON[4],
            "I": IRON[3] if not night else IRON[6], "e": EYE[4], "o": RUST[2], "O": RUST[5],
            "q": STEEL[1] if not night else STEEL[5], "#": ink}


# The main deck cut away is drawn in its own module and placed from here, as a piece of a scene like any other.
from . import deck as _deck

deck = _deck.deck
