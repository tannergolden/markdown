# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The Hall of Fame of all four games as a pixel set draws it: the series, the podium, and a badge for every winner.

The Hall reads as it does in the standard theme and every print, a match card, top to bottom: the house and GitHub
facing each other across the top on their medallions; the series under them, all four games together and then each
on a row of its own, Chess first, each named by its two pieces, the house's first, its two counts either side of a
bar of the share; then the podium, three blocks second, first and third from the left, a plaque of the trophies'
gold, silver and bronze set in each, each winner standing on theirs as the set draws a person, its avatar, in a ring
of its metal, with their wins and their wins in every game; and the two places after it. What the set adds is its
world: its paper, frame and tag, its lettering, its avatars and its tags for every count, and what its podium is cut
from and how it is worked (`game_podium`): a castle's crenellated ashlar, presents tied with ribbon, tarred timber
with a ship's shields along its rail, a graveyard's stone cobwebbed, garnets set in gold cells.

As the file opens the series fills row by row, the blocks rise out of the floor, third, second, first, the winners
appear on them, and a glint runs round the gold ring every so often, on the hand's period in a collection's design.
A winner's badge is the set's own badge, the leader's in the set's gold, glinting.
"""
from __future__ import annotations

import math

from ...elements.chess.game import OWNER
from ...elements.hall import record as R
from ..pixel import GLYPHS, Pix, fold, measure
from . import materials as MT
from . import pieces as PC
from .boards import put, ring_cells
from .games import _nothing, _paths, _t, appear, steps
from .trophies import FLARE, METALS

STAND = (1, 0, 2)            # the podium's blocks from the left: second, first, third
BLOCKS = {"wide": (42, 36, 30), "narrow": (30, 25, 21)}
METAL = (3, 2, 1)            # the place each block's metal is struck for: gold, silver, bronze
RISE = {2: 1.0, 1: 1.2, 0: 1.4}
STEP = 6                      # how far a game's second piece stands to the right of its first
MARK = {False: STEP + 10, True: 10}   # a game's mark at its widest: its two pieces, or the house's alone
GAP = 4
# The sizes a count may be set at, the largest first: in the set's title lettering, then its body's 5x7 letters, then
# its 3x5. A count too wide for its room at one is set at the next, so a number is never cut short.
SIZES = {"total": (("title", 2), ("title", 1), ("35", 1)), "count": (("57", 1), ("35", 1)),
         "wins": (("57", 2), ("57", 1), ("35", 1))}
DRAW_IN = 56                  # how far the wide series' bar may be drawn in from either end to make room for a count
PIP = 13                      # the rows a winner's wins in each game take, a row of them


def state(d: dict) -> dict:
    return R.state(d)


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'s' if n != 1 else ''}"


def games_line(s: dict, room: int | None = None) -> str:
    """How many games of a series have finished and how many were drawn, in capitals: its dot set wide, or set close
    where `room` is too short for that, before any letters need setting tighter."""
    if not s["games"]:
        return "NO GAME FINISHED YET"
    wide = f"{plural(s['games'], 'game')}  ·  {s['draws']} drawn".upper()
    if room is None or measure(fold(wide, "35"), "35") <= room:
        return wide
    return f"{plural(s['games'], 'game')} · {s['draws']} drawn".upper()


# --------------------------------------------------------------------------- a count
def size_of(s: str, size: tuple) -> int:
    """How wide `s` is set at `size`, a (lettering, scale) pair."""
    font, scale = size
    return measure(s, "57" if font == "title" else font, scale)


def tall(size: tuple) -> int:
    font, scale = size
    return (5 if font == "35" else 7) * scale


def sized(texts, sizes: tuple, rooms) -> tuple:
    """The largest of `sizes` at which every one of `texts` fits its room in `rooms`, or the smallest."""
    for size in sizes:
        if all(size_of(s, size) <= room for s, room in zip(texts, rooms)):
            return size
    return sizes[-1]


def count(h, p, x: int, mid: int, s: str, size: tuple, night: bool, anchor: str = "start") -> int:
    """A count at `size`, its rows centred on row `mid`: in the set's title lettering, or in its body's ink. Set from
    `x`, or ending at it (`anchor` end). Returns its width."""
    font, scale = size
    w = size_of(s, size)
    x = x - w if anchor == "end" else x
    top = mid - tall(size) // 2
    if font == "title":
        h.game_title(p, x, top, s, night, scale)
    else:
        p.text(x, top, s, h.ink(night)["body"], font, scale)
    return w


# --------------------------------------------------------------------------- a game's mark
def piece(p, game: str, material: str, x: int, y: int, L: str = "base") -> tuple:
    """One of a game's pieces at the Hall's size, its foot on row `y + 11`: a king, a man, a marble or a pen's
    mark. Returns its drawing's width."""
    if game == "chess":
        d = PC.chessman("king", "mini", material)
    elif game == "checkers":
        d = PC.man(material, 4, 2, 2)
    elif game == "pentago":
        d = PC.disc(material, 3.5)
    else:
        mark = "X" if material == "light" else "O"
        d = PC.pen(mark, material, 8)
    put(p, d, ("hall", game, material), x, y + 11 - d[2], L)
    return d[1]


def mark(p, game: str, x: int, y: int, one: bool = False) -> int:
    """A game's own mark: its two pieces, the house's light one in front of GitHub's dark one; or, where the room is
    short, the house's alone. Returns its width."""
    behind = 0 if one else piece(p, game, "dark", x + STEP, y)
    front = piece(p, game, "light", x, y)
    return max(front, STEP + behind) if not one else front


# --------------------------------------------------------------------------- the parts
def shares(h, p, s: dict, x0: int, x1: int, y: int, night: bool) -> None:
    """A bar of a series' games: the house's wins from the left in ivory, GitHub's from the right in ebony, the
    draws between in the set's own colour, on the board's tray, its middle ticked; before a game has finished, an
    empty track."""
    b = h.game_board(night)
    hgt = 5
    h.tray(p, x0, y, x1 - x0, hgt + 2, night)
    inner0, inner1 = x0 + 1, x1 - 1
    w = inner1 - inner0
    if s["games"]:
        x = inner0
        for key, ramp in (("house", PC.IVORY), ("draws", None), ("github", PC.EBONY)):
            part = round(w * s[key] / s["games"]) if key != "github" else inner1 - x
            if part <= 0:
                continue
            grain = MT.surface(b["dark_stuff"], part, hgt) if ramp is None else {}
            for xx in range(x, min(inner1, x + part)):
                for j in range(hgt):
                    if ramp is None:
                        c = grain[(xx - x, j)] if 0 < j < hgt - 1 else (b["light"] if j == 0 else b["edge"])
                    else:
                        c = ramp[5] if j == 0 else ramp[2 if ramp is PC.IVORY else 1] if j == hgt - 1 else ramp[4 if ramp is PC.IVORY else 3]
                    p.px(xx, y + 1 + j, c)
            x += part
    mid = (x0 + x1) // 2
    p.vline(mid, y - 2, y + hgt + 4, b["shade"])


def metal_ring(p, cx: int, cy: int, r: float, t: int, L: str = "base") -> list:
    """A ring of a tier's metal round a winner, two pixels thick, lit from the upper left. Returns its cells."""
    ramp = METALS[t]
    cells = []
    for y in range(math.floor(cy - r) - 3, math.ceil(cy + r) + 3):
        for x in range(math.floor(cx - r) - 3, math.ceil(cx + r) + 3):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if r - .5 <= d < r + 1.5:
                lit = -((x + .5 - cx) * .6 + (y + .5 - cy) * .8) / max(d, 1)
                tone = 5 if lit > .45 else 4 if lit > 0 else 3 if lit > -.5 else 2
                if d >= r + .7:
                    tone = max(1, tone - 2)
                p.px(x, y, ramp[tone], L)
                cells.append((x, y))
    return cells


def gold_glint(h, p, cx: int, cy: int, r: float) -> None:
    """A sparkle running round the gold ring every so often: on the hand's period in a collection's design."""
    period = h._glint_period()
    ramp = METALS[3]
    spots = [(round(cx + (r + .5) * math.cos(a)), round(cy + (r + .5) * math.sin(a)))
             for a in (math.radians(-150 + 30 * i) for i in range(5))]
    frames = []
    for i, (x, y) in enumerate(spots):
        cells = {}
        for j, row in enumerate(FLARE):
            for k, ch in enumerate(row):
                if ch == "#":
                    cells[(x - 2 + k, y - 2 + j)] = ramp[5]
        cells[(x, y)] = ramp[6]
        t0 = .7 + .03 * i
        frames.append(f'<g opacity="0">{_paths(cells)}<animate attributeName="opacity" values="0;1;0" '
                      f'keyTimes="0;{_t(t0)};{_t(t0 + .03)}" dur="{_t(period)}s" begin="1.6s" calcMode="discrete" '
                      'repeatCount="indefinite"/></g>')
    p.raw(26, "".join(frames), "")


def block(h, p, x: int, w: int, ground: int, ht: int, place: int, night: bool, scale: int, L: str = "base") -> None:
    """A block of the podium cut from what the set's podium is made of, seen a little from above: its lid lit and its
    front edge catching the light, its front in the stuff's grain, lit down its left and shaded down its right and
    along its foot, and worked as the set works its podium; and set in its front a plaque of its place's metal with the
    place struck into it at `scale`, a star of the first's metal either side of the first's where there is room."""
    pod = h.game_podium(night)
    s, style = pod.stuff, pod.style
    m = METALS[METAL[place]]
    top = ground - ht
    body = top + ((4 if scale == 2 else 3) if style == "crenels" else 0)    # the wall walk, behind a parapet
    lid = 2 if style == "crenels" or ht < 20 else 3
    f0 = body + 1 + lid                   # the front's first row, under the lid's edge
    for (fx, fy), c in MT.surface(s, w - 2, ground - f0, variant=place).items():
        p.px(x + 1 + fx, f0 + fy, c, L)
    for yy in range(f0, ground - 2):
        p.px(x + 1, yy, s.tone(1), L)
        p.px(x + w - 2, yy, s.tone(-1), L)
    for xx in range(x + 1, x + w - 1):
        p.px(xx, body, s.tone(-3), L)
        for yy in range(body + 1, f0):
            p.px(xx, yy, s.tone(3) if yy == f0 - 1 else s.tone(2), L)
        p.px(xx, ground - 2, s.tone(-1), L)
        p.px(xx, ground - 1, s.tone(-2), L)
    if style == "crenels":
        merlons(p, s, x, w, top, body, f0, L)
    p.vline(x, top + 1 if style == "crenels" else body + 1, ground, s.tone(-3), L)
    p.vline(x + w - 1, top + 1 if style == "crenels" else body + 1, ground, s.tone(-3), L)
    # the plaque, and what the podium is worked with round it
    label = str(place + 1)
    lw = measure(label, "57", scale)
    pw, ph = 5 * scale + 8, 7 * scale + 5
    px0 = x + (w - pw) // 2
    py0 = f0 + (ground - 2 - f0 - ph + 1) // 2
    clear = (px0 - 3, px0 + pw + 3)
    star = GLYPHS[7]["star"]
    sw = len(star[0])
    starred = place == 0 and not (style == "banners" and scale == 1)    # where the banners leave no room, no stars
    if style == "ribbon":
        ribbon(p, pod.trim or s, x, w, body, f0, ground, py0 + ph // 2, scale, L)
    elif style in ("bunting", "shields", "garland", "lace"):
        frieze(h, p, pod, style, x, w, f0, scale, clear, night, L)
    elif style == "banners":
        banners(h, p, pod, x, w, f0, ground, scale, (clear[0] - sw - 4, clear[1] + sw + 4) if starred else clear,
                night, L)
    elif style == "cobwebs":
        cobwebs(h, p, pod, x, w, f0, ground, scale, night, L)
    for yy in range(py0, py0 + ph):
        for xx in range(px0, px0 + pw):
            rim = xx in (px0, px0 + pw - 1) or yy in (py0, py0 + ph - 1)
            if rim and xx in (px0, px0 + pw - 1) and yy in (py0, py0 + ph - 1):
                continue
            c = (m[0] if rim else m[5] if yy == py0 + 1 else m[1] if yy == py0 + ph - 2 else
                 m[4] if xx == px0 + 1 else m[2] if xx == px0 + pw - 2 else m[3])
            p.px(xx, yy, c, L)
    p.text(px0 + (pw - lw) // 2, py0 + 2, label, m[0], "57", scale, L=L, shadow=m[5])
    if starred:
        cy = py0 + ph // 2 - 3
        for sx in (px0 - sw - 4, px0 + pw + 4):
            p.sprite(sx + 1, cy + 1, star, {"#": m[0]}, L=L)
            p.sprite(sx, cy, star, {"#": m[5]}, L=L)


def merlons(p, s, x: int, w: int, top: int, body: int, f0: int, L: str) -> None:
    """A parapet along a block's top, its merlons standing over the wall walk between them, the end ones flush with
    the block's sides: each lit along its top, its face in the stuff's grain down into the block's."""
    mw, cw = (7, 4) if w >= 60 else (5, 3)
    n = max(2, (w + cw) // (mw + cw))
    slack = w - (n * mw + (n - 1) * cw)
    a = x
    for i in range(n):
        width = mw + (slack // 2 if i == 0 else slack - slack // 2 if i == n - 1 else 0)
        face = MT.surface(s, width, f0 - top - 2, variant=i)
        for xx in range(a, a + width):
            edge = xx in (a, a + width - 1)
            p.px(xx, top, s.tone(-3), L)
            for yy in range(top + 1, f0):
                if edge and yy < body + 1:
                    c = s.tone(-3)
                elif yy == top + 1:
                    c = s.tone(2)
                else:
                    c = face.get((xx - a, yy - top - 2), s.base)
                    if xx == a + 1 and yy < body + 1:
                        c = s.tone(1)
                    elif xx == a + width - 2 and yy < body + 1:
                        c = s.tone(-1)
                p.px(xx, yy, c, L)
        a += width + cw


def ribbon(p, t, x: int, w: int, body: int, f0: int, ground: int, cy: int, scale: int, L: str) -> None:
    """A ribbon tied round a block as round a present: down over its lid and front, and round it across the middle of
    its plaque, lit along one edge and shaded along the other, in the shade of the block's foot where it passes."""
    rw = 4 if scale == 2 else 3
    rx = x + (w - rw) // 2
    for yy in range(body + 1, ground):
        for i in range(rw):
            c = t.tone(1) if i == 0 else t.tone(-1) if i == rw - 1 else t.base
            if yy < f0:
                c = t.tone(3) if yy == f0 - 1 else t.tone(2)
            elif yy >= ground - 2:
                c = t.tone(-1) if yy == ground - 2 else t.tone(-2)
            p.px(rx + i, yy, c, L)
    ry = cy - rw // 2
    for xx in range(x + 1, x + w - 1):
        for j in range(rw):
            c = t.tone(1) if j == 0 else t.tone(-1) if j == rw - 1 else t.base
            p.px(xx, ry + j, c, L)


def frieze(h, p, pod, style: str, x: int, w: int, f0: int, scale: int, clear: tuple, night: bool, L: str) -> None:
    """A row of things hung along a block's top, under its lid's edge and clear of its plaque: bunting in the board's
    two colours; a ship's shields along its rail, or a garland of leaves, the trim's and the board's light square's
    turn about; or an edge of lace."""
    b = h.game_board(night)
    s = pod.stuff
    if style == "lace":
        t = pod.trim or b["light_stuff"]
        d = 5 if scale == 2 else 4
        for xx in range(x + 1, x + w - 1):
            p.px(xx, f0, t.base, L)
            k = (xx - x - 1) % d
            depth = (1, 2, 3, 2, 1)[k * 5 // d]
            for yy in range(f0 + 1, f0 + 1 + depth):
                hole = scale == 2 and k == d // 2 and yy == f0 + 1
                p.px(xx, yy, s.tone(-1) if hole else t.base if yy < f0 + depth else t.tone(-1), L)
        return
    trim = pod.trim or b["dark_stuff"]
    if style == "bunting":
        cols, pw, pitch = (b["dark"], b["light"]), (7 if scale == 2 else 5), (9 if scale == 2 else 7)
    elif style == "shields":
        cols, pw, pitch = (trim.base, b["light"]), (11 if scale == 2 else 7), (10 if scale == 2 else 6)
    else:
        cols, pw, pitch = (trim, b["light_stuff"]), (7 if scale == 2 else 5), (10 if scale == 2 else 7)
    n = (w - 4 - pw) // pitch + 1
    x0 = x + (w - (n - 1) * pitch - pw) // 2
    if style in ("bunting", "garland"):
        p.hline(x + 1, x + w - 1, f0, s.tone(-3), L)
    for i in range(n):
        sx = x0 + i * pitch
        if sx + pw > clear[0] and sx < clear[1]:
            continue
        if style == "bunting":
            for j in range((pw + 1) // 2):
                for xx in range(sx + j, sx + pw - j):
                    p.px(xx, f0 + 1 + j, cols[i % 2] if xx < sx + pw - j - 1 else s.tone(-3), L)
        elif style == "shields":
            shield(p, sx, f0 - 2, pw, cols[i % 2], cols[1 - i % 2], s, L)
        else:
            leaf(p, sx, f0, pw, cols[i % 2], i, L)


def shield(p, x: int, y: int, d: int, face: str, quarter: str, s, L: str) -> None:
    """A round shield `d` across with its top-left at (x, y), as a ship carries them along her rail: its face in
    `face`, quartered in `quarter`, its rim and its boss iron, the boss lit."""
    r = d / 2
    for yy in range(d):
        for xx in range(d):
            e = math.hypot(xx + .5 - r, yy + .5 - r)
            if e > r:
                continue
            q = (xx < d // 2) == (yy < d // 2)
            p.px(x + xx, y + yy, s.tone(-3) if e > r - 1 else quarter if q and d >= 7 else face, L)
    m = d // 2
    boss = 1 if d >= 9 else 0
    for yy in range(m - boss, m + boss + 1):
        for xx in range(m - boss, m + boss + 1):
            p.px(x + xx, y + yy, s.tone(-3), L)
    p.px(x + m - boss, y + m - boss, s.tone(3), L)


LEAVES = {5: ("..#..", ".###.", "#####", ".###.", "..#.."),
          7: ("...#...", ".#.#.#.", ".#####.", "#######", ".#####.", "..###..", "...#...")}


def leaf(p, x: int, y: int, d: int, t, i: int, L: str) -> None:
    """A maple leaf of a garland `d` wide, hanging from (x + d // 2, y): lit down its left, its vein down its middle
    and its right in shade, every other one turned a little the other way."""
    rows = LEAVES[d]
    for j, row in enumerate(rows):
        dx = (1 if i % 2 else -1) if j >= len(rows) - 2 and d == 7 else 0
        for k, ch in enumerate(row):
            if ch != "#":
                continue
            mid = d // 2
            c = t.tone(-2) if k == mid and 0 < j < len(rows) - 1 else t.tone(1) if k < mid else \
                t.tone(-1) if k > mid else t.base
            p.px(x + k + dx, y + 1 + j, c, L)


def cobwebs(h, p, pod, x: int, w: int, f0: int, ground: int, scale: int, night: bool, L: str) -> None:
    """A cobweb across each of a block's top corners, under its lid: its threads out from the corner and the rings
    strung between them, in the trim."""
    b = h.game_board(night)
    t = (pod.trim or b["light_stuff"]).base
    r = min(13 if scale == 2 else 8, ground - 3 - f0)
    for cx, dx in ((x + 1, 1), (x + w - 2, -1)):
        ends = [(cx + dx * round(r * math.sin(a)), f0 + round(r * math.cos(a)))
                for a in (math.pi / 2 * k / 3 for k in range(4))]
        for ex, ey in ends:
            line(p, cx, f0, ex, ey, t, L)
        for frac in (.4, .7, 1.0):
            pts = [(cx + round((ex - cx) * frac), f0 + round((ey - f0) * frac)) for ex, ey in ends]
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                mx = (ax + bx) // 2 - dx * round(frac)    # the ring sagging a little toward the corner
                my = (ay + by) // 2 - round(frac)
                line(p, ax, ay, mx, my, t, L)
                line(p, mx, my, bx, by, t, L)


def line(p, x0: int, y0: int, x1: int, y1: int, c: str, L: str) -> None:
    """A line a pixel thick from (x0, y0) to (x1, y1), both ends included."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        p.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c, L)


def banners(h, p, pod, x: int, w: int, f0: int, ground: int, scale: int, clear: tuple, night: bool, L: str) -> None:
    """Two banners hung from a block's lid either side of its plaque, swallow-tailed, the trim's and the board's dark
    square's: each lit down its left and shaded down its right, crossed by a band of the board's light square, on a
    rod."""
    b = h.game_board(night)
    s = pod.stuff
    ramps = (pod.trim or b["dark_stuff"], b["dark_stuff"])
    bw = 11 if scale == 2 else 7
    drop = max(6, (ground - 2 - f0) * 4 // 5)
    band = (f0 + 1 + drop // 3, 2 if scale == 2 else 1)
    for i, cx in enumerate(((x + clear[0]) // 2, (clear[1] + x + w) // 2)):
        t = ramps[i]
        bx = cx - bw // 2
        p.hline(bx - 1, bx + bw + 1, f0, s.tone(-3), L)
        for yy in range(f0 + 1, f0 + 1 + drop):
            cut = yy - (f0 + drop - bw // 2)           # how far into the swallow tail's notch
            for xx in range(bx, bx + bw):
                if cut > 0 and abs(xx - (bx + bw // 2)) < cut:
                    continue
                c = t.tone(1) if xx == bx else t.tone(-1) if xx == bx + bw - 1 else t.base
                if band[0] <= yy < band[0] + band[1]:
                    c = b["light_stuff"].tone(-1) if xx == bx + bw - 1 else b["light"]
                p.px(xx, yy, c, L)


def winner(h, p, person: dict, i: int, cx: int, top: int, w: int, night: bool, small: bool, moving: bool,
           rows: int, lift: int) -> None:
    """A winner standing on their block, centred on `cx` over its top at `top`: their avatar in a ring of their
    place's metal, their name and handle, all their wins, and their wins in each game on `rows` rows, the whole
    `lift` rows higher for every row past the podium's first."""
    k = h.ink(night)
    room = w - 4
    r = 10 if not small else 9
    cy = top - (68 if not small else 72) - lift
    t = METAL[i]
    if i == 0:                 # the first place's light, falling round the ring
        for y in range(cy - r - 6, cy + r + 7):
            for x in range(cx - r - 6, cx + r + 7):
                d = math.hypot(x + .5 - cx, y + .5 - cy) / (r + 6)
                if r + 1 < math.hypot(x + .5 - cx, y + .5 - cy) and d < 1:
                    p.px(x, y, f"{METALS[3][5]}:{(.05, .09, .14)[min(2, int((1 - d) * 3))]}")
    if person.get("house"):
        h.medal(p, cx, cy, r - 1, "light", night)
        d = PC.chessman("king", "narrow", "light")
        put(p, d, ("chess", "king", "narrow", "white"), cx - d[1] // 2, cy - d[2] // 2)
    else:
        h.avatar(p, cx, cy, i, person, night)
    metal_ring(p, cx, cy, r + 1, t)
    if i == 0 and moving:
        gold_glint(h, p, cx, cy, r + 1.5)
    y = cy + r + 5
    # A name may reach a unit nearer its column's edges than the rest of its stand, and the first's, standing higher
    # than the names either side of it with only the foot of their rings beside it, a unit past them.
    named = w + 2 if i == 0 else w - 2
    h.say(p, cx, y, person["name"], k["body"], room=named, anchor="middle")
    y += 8
    h.say(p, cx, y, person["handle"].upper(), k["muted"], room=w - 2, anchor="middle")
    y += 9
    wins = str(person["wins"])
    word = "WINS" if person["wins"] != 1 else "WIN"
    ww = measure(word, "35")
    sizes = SIZES["wins"][1:] if small else SIZES["wins"]
    size = sized((wins,), sizes, (room - GAP - ww,))
    line = tall(sizes[0])       # the line keeps its height whatever size its count is set at, its foot level
    nw = size_of(wins, size)
    left = cx - (nw + GAP + ww) // 2
    p.text(left, y + line - tall(size), wins, k["body"], size[0], size[1])
    p.text(left + nw + GAP, y + line - 5, word, k["muted"], "35")
    y += line + 4
    by_game(h, p, person, cx, y, room, night, rows)


def arrangement(person: dict, room: int, rows: int) -> tuple | None:
    """How a winner's wins in each game stand on `rows` rows in `room`: (slot, one, track), each game's slot, whether
    its mark is the house's piece alone and how its count is spaced; None where they cannot. A mark is its two pieces
    and a count at its spacing where the room allows; where it is short the marks give way first, to the house's piece
    alone, and only then is a count set tight, its letters touching."""
    per = len(R.ORDER) // rows
    for one, track in ((False, 1), (True, 1), (True, 0)):
        slot = least(person, one, track)
        if per * slot - 3 <= room:
            return max(slot, min(room // per, 32)), one, track
    return None


def least(person: dict, one: bool, track: int) -> int:
    """The narrowest slot a winner's wins in each game fit, its mark and its count, with the gap before the next."""
    return MARK[one] + 2 + max(measure(str(person["by_game"][game]), "35", 1, track) for game in R.ORDER) + 3


def pip_rows(people: list, room: int, small: bool) -> int:
    """The rows the podium sets its winners' wins in each game on: one on a wide sheet and two on a phone's, or more
    where a winner's counts are too wide for that, the same for every place so the podium stands level."""
    for rows in ((2, 4) if small else (1, 2, 4)):
        if all(arrangement(person, room, rows) for person in people):
            return rows
    return 4


def by_game(h, p, person: dict, cx: int, y: int, room: int, night: bool, rows: int = 1, left: int | None = None) -> int:
    """A winner's wins in every game, Chess first, each beside that game's mark, a game they have yet to win set
    quietly: on `rows` rows, centred on `cx` or from `left`, as `arrangement` fits them to `room`. Returns the width
    it took."""
    k = h.ink(night)
    per = len(R.ORDER) // rows
    slot, one, track = arrangement(person, room, rows) or (room // per, True, 0)
    texts = [str(person["by_game"][game]) for game in R.ORDER]
    used = (per - 1) * slot + least(person, one, track) - 3
    x0 = left if left is not None else cx - used // 2
    for i, game in enumerate(R.ORDER):
        col, row = i % per, i // per
        x, yy = x0 + col * slot, y + row * PIP
        n = person["by_game"][game]
        w = mark(p, game, x, yy, one)
        p.text(x + w + 2, yy + 5, texts[i], k["body"] if n else k["muted"], "35", track=track)
    return used


# --------------------------------------------------------------------------- the series' columns
def series_columns(hs: dict, x0: int, x1: int) -> tuple[dict, list]:
    """The wide series' columns, the name's, the house's count (its right edge), the bar and GitHub's count, and the
    size each row's two counts are set at, all four games' first. Where a count is too wide for its end of the bar,
    the bar is drawn in from both ends alike, so its middle stays under VS, as far as `DRAW_IN`; past that, the count
    is set smaller."""
    rows = [(hs["totals"], measure("ALL FOUR GAMES", "35"), SIZES["total"])]
    rows += [(hs["series"][game], measure(R.TITLES[game].upper(), "35"), SIZES["count"]) for game in R.ORDER]
    name, house, github = x0 + 26, x0 + 120, x1 - 27

    def rooms(lw: int, shift: int) -> tuple:
        return house + shift - (name + lw + GAP), x1 - (github - shift)
    need = 0
    for s, lw, sizes in rows:
        left, right = rooms(lw, 0)
        need = max(need, size_of(str(s["house"]), sizes[0]) - left, size_of(str(s["github"]), sizes[0]) - right)
    shift = min(max(need, 0), DRAW_IN)
    cols = {"name": name, "house": house + shift, "bar0": house + shift + 7, "bar1": github - shift - 7,
            "github": github - shift}
    return cols, [sized((str(s["house"]), str(s["github"])), sizes, rooms(lw, shift)) for s, lw, sizes in rows]


def phone_columns(hs: dict, x0: int, x1: int) -> dict:
    """A phone's series' columns: the name's, the house's count (its right edge), the bar and GitHub's count, the bar
    drawn in from either end as far as the widest count at that end needs, the house's clear of the game's mark."""
    series = [hs["series"][game] for game in R.ORDER]
    hw = max(measure(str(s["house"]), "35") for s in series)
    gw = max(measure(str(s["github"]), "35") for s in series)
    house = max(x0 + 38, x0 + MARK[False] + 2 + hw)
    github = min(x1 - 14, x1 - gw)
    return {"name": x0 + 22, "house": house, "bar0": house + 4, "bar1": github - 4, "github": github}


# --------------------------------------------------------------------------- the sheet
def sheet(h, hs: dict, night: bool, wide: bool, moving: bool) -> Pix:
    W = 415 if wide else 180
    probe = Pix(W, 900)
    end = draw(h, probe, hs, night, wide, False, measure_only=True)
    p = h.game_canvas(W, end + 10)
    draw(h, p, hs, night, wide, moving)
    h._finish(p, night)
    return p


def draw(h, p, hs: dict, night: bool, wide: bool, moving: bool, measure_only: bool = False) -> int:
    """Everything on the Hall's sheet, top to bottom; returns where it ends."""
    k = h.ink(night)
    b = h.game_board(night)
    totals = hs["totals"]
    games = plural(totals["games"], "game") if totals["games"] else "no games yet"
    if not measure_only:
        h.head(p, night, _Label(), games, f"FOUR GAMES  ·  @{OWNER.upper()} VS. GITHUB" if wide else None)
    x0, x1 = 10, p.w - 10
    y = 27
    if wide:
        cols, sizes = series_columns(hs, x0, x1)

    def section(name: str, at: float):
        return p.onto(p.once(name, appear(at), z=.6)) if moving else _nothing()

    # the two sides
    with section("sides", .15):
        r = 10 if wide else 8
        cy = y + r + 1
        for side, who, sub, mat in (("house", f"@{OWNER.upper()}", "THE HOUSE", "light"),
                                    ("github", "GITHUB", "EVERYONE ELSE", "dark")):
            left = side == "house"
            cx = x0 + r + 1 if left else x1 - r - 1
            h.medal(p, cx, cy, r, mat, night)
            d = PC.chessman("king", "narrow" if r >= 9 else "mini", mat)
            put(p, d, ("chess", "king", "narrow" if r >= 9 else "mini", "white" if left else "black"),
                cx - d[1] // 2, cy - d[2] // 2)
            tx = cx + r + 6 if left else cx - r - 6
            anchor = "start" if left else "end"
            h.say(p, tx, cy - 6, who, k["body"], anchor=anchor, room=(x1 - x0) // 2 - 2 * r - 12)
            kx = tx if left else tx - 5
            p.rect(kx, cy + 2, 5, 5, PC.IVORY[4] if left else PC.EBONY[3])
            p.box(kx, cy + 2, 5, 5, b["shade"])
            h.say(p, tx + 8 if left else tx - 8, cy + 2, sub, k["muted"], anchor=anchor,
                  room=(x1 - x0) // 2 - 2 * r - 20)
        if wide:
            vs = measure("VS", "35") + 8
            mid = (cols["bar0"] + cols["bar1"]) // 2
            h.chip(p, mid - vs // 2, cy - 4, "VS", night)
    y = cy + r + 7
    p.hline(x0, x1, y, k["rule"])
    y += 7
    # the series
    if wide:
        with section("total", .3):
            t = totals
            size = sizes[0]
            hw = count(h, p, cols["house"], y + 8, str(t["house"]), size, night, anchor="end")
            count(h, p, cols["github"], y + 8, str(t["github"]), size, night)
            h.say(p, cols["name"], y + 1, "ALL FOUR GAMES", k["body"])
            room = cols["house"] - hw - GAP - cols["name"]
            h.say(p, cols["name"], y + 9, games_line(t, room), k["muted"], room=room)
            shares(h, p, t, cols["bar0"], cols["bar1"], y + 5, night)
        y += 22
        p.hline(cols["name"], x1, y - 4, k["rule"])
        for i, game in enumerate(R.ORDER):
            s = hs["series"][game]
            with section(f"row{i}", .45 + .12 * i):
                mark(p, game, x0 + 2, y - 1)
                hw = count(h, p, cols["house"], y + 4, str(s["house"]), sizes[1 + i], night, anchor="end")
                count(h, p, cols["github"], y + 4, str(s["github"]), sizes[1 + i], night)
                h.say(p, cols["name"], y, R.TITLES[game].upper(), k["body"])
                room = cols["house"] - hw - GAP - cols["name"]
                h.say(p, cols["name"], y + 7, games_line(s, room), k["muted"], room=room)
                shares(h, p, s, cols["bar0"], cols["bar1"], y + 2, night)
            y += 17
    else:
        mid = (x0 + x1) // 2
        with section("total", .3):
            t = totals
            vs = measure("VS", "35") + 8
            h.chip(p, mid - vs // 2, y + 3, "VS", night)
            room = mid - vs // 2 - 6 - x0
            size = sized((str(t["house"]), str(t["github"])), SIZES["total"], (room, room))
            count(h, p, mid - vs // 2 - 6, y + 7, str(t["house"]), size, night, anchor="end")
            count(h, p, mid + vs // 2 + 6, y + 7, str(t["github"]), size, night)
            line = f"ALL FOUR GAMES  ·  {games_line(t)}"
            if measure(fold(line, "35"), "35") > x1 - x0:
                line = f"ALL FOUR GAMES · {games_line(t, 0)}"
            h.say(p, mid, y + 17, line, k["muted"], anchor="middle", room=x1 - x0)
            shares(h, p, t, x0, x1, y + 25, night)
        y += 37
        cols = phone_columns(hs, x0, x1)
        for i, game in enumerate(R.ORDER):
            s = hs["series"][game]
            with section(f"row{i}", .45 + .12 * i):
                mark(p, game, x0, y)
                title = R.TITLES[game].upper()
                tw = h.say(p, cols["name"], y, title, k["body"])
                room = x1 - cols["name"] - tw - 6
                h.say(p, x1, y, games_line(s, room), k["muted"], anchor="end", room=room)
                h.say(p, cols["house"], y + 9, str(s["house"]), k["body"], anchor="end")
                h.say(p, cols["github"], y + 9, str(s["github"]), k["body"])
                shares(h, p, s, cols["bar0"], cols["bar1"], y + 9, night)
            y += 20
    y += 2
    p.hline(x0, x1, y, k["rule"])
    # the podium
    people = hs["people"]
    heights = BLOCKS["wide" if wide else "narrow"]
    bw = (x1 - x0) // 3
    rows = pip_rows(people[:3], bw - 4, not wide)
    lift = PIP * (rows - (2 if not wide else 1))
    standing = (84 if wide else 88) + lift
    ground = y + 6 + standing + heights[0]
    for col, place in enumerate(STAND):
        bx = x0 + col * bw
        top = ground - heights[place]
        if moving:
            clip = f"gph{col}"
            p.defs.append(f'<clipPath id="{clip}"><rect x="{bx - 2}" y="{ground - heights[0] - 4}" '
                          f'width="{bw + 4}" height="{heights[0] + 4}"/></clipPath>')
            n = 5
            offs = [(0, heights[place])] * 2 + [(0, round(heights[place] * (1 - i / n))) for i in range(1, n + 1)]
            begin = RISE[place] - .55
            times = [0, begin] + [begin + .45 * i / n for i in range(1, n + 1)]
            L = p.once(f"block{place}", steps(offs, times, times[-1] + .05), z=.4, outer=f'clip-path="url(#{clip})"')
        else:
            L = "base"
        block(h, p, bx + 1, bw - 2, ground, heights[place], place, night, 2 if wide else 1, L)
        if place < len(people):
            with section(f"stand{place}", RISE[place] + .05):
                winner(h, p, people[place], place, bx + bw // 2, top, bw, night, not wide, moving, rows, lift)
        else:
            with section(f"stand{place}", RISE[place] + .05):
                vacant(h, p, place, bx + bw // 2, top, bw, night, not wide, lift)
    # the plinth the podium stands on, of what the set's boards are framed in, its edge lit
    f = b["frame"]
    if "plinth" not in p.layers:
        p.layer("plinth", z=-.8)
    for dy, tone in enumerate((1, 0, -1, -2)):
        p.hline(x0 - 2, x1 + 2, ground + dy, f.tone(tone), "plinth")
    y = ground + 8
    rest = people[3:]
    if rest:
        p.hline(x0, x1, y, k["rule"])
        y += 7
        with section("rest", 1.6):
            y = mentions(h, p, rest, x0, x1, y, night, wide)
    return y


def vacant(h, p, i: int, cx: int, top: int, w: int, night: bool, small: bool, lift: int = 0) -> None:
    """A place on the podium nobody has won yet: its metal's ring round an empty disc, and who stands there next."""
    k = h.ink(night)
    r = 10 if not small else 9
    cy = top - (68 if not small else 72) - lift
    for (x, y) in ring_cells(cx, cy, r + 1.5):
        if (x + y) % 3 != 0:
            p.px(x, y, METALS[METAL[i]][3])
    h.say(p, cx, cy - 2, "?", k["muted"], "57", anchor="middle")
    said = "the next to win stands here" if i == 0 else "a place on the podium"
    y = cy + r + 5
    h.say(p, cx, y, "NOBODY YET", k["muted"], anchor="middle", room=w - 4)
    words = said.upper().split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if measure(trial, "35") <= w - 6 or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    for j, line in enumerate(lines[:3]):
        h.say(p, cx, y + 9 + j * 7, line, k["muted"], anchor="middle", room=w - 4)


def mentions(h, p, rest: list, x0: int, x1: int, y: int, night: bool, wide: bool) -> int:
    """The places after the podium: the number on the set's tag, the name and handle, the wins in each game, and
    all of them on a tag; two to a row, or on a phone one, the wins in each game on a line under the name."""
    k = h.ink(night)
    per = 2 if wide else 1
    colw = (x1 - x0) // per
    # on a phone the wins in each game take a row under the name, or two where a place's counts are too wide for one
    rows = 1 if wide or all(arrangement(person, x1 - x0 - 12, 1) for person in rest) else 2
    step = 28 + PIP * (rows - 1)
    for i, person in enumerate(rest):
        col, row = i % per, i // per
        x, yy = x0 + col * colw, y + row * step
        h.numbered(p, x, yy + 1, 4 + i, "", night)
        wins = f"{person['wins']} WIN{'S' if person['wins'] != 1 else ''}"
        cw = measure(wins, "35") + 8
        cx = x + colw - cw - (0 if not wide or col else 8)
        h.chip(p, cx, yy, wins, night)
        if wide:       # the wins in each game two by two, so the name keeps its room beside them, 48 at the least
            beside = cx - x - 14 - 8
            most = max(2 * 26, beside - 48)
            fit = arrangement(person, most, 2)
            games_w = max(2 * 26, 2 * least(person, *fit[1:]) - 3) if fit else most
            name_room = beside - games_w
            h.say(p, x + 12, yy, person["name"], k["body"], room=name_room)
            h.say(p, x + 12, yy + 7, person["handle"].upper(), k["muted"], room=name_room)
            by_game(h, p, person, 0, yy - 1, games_w, night, rows=2, left=cx - games_w - 6)
        else:
            h.say(p, x + 12, yy, person["name"], k["body"], room=cx - x - 16)
            h.say(p, x + 12, yy + 7, person["handle"].upper(), k["muted"], room=cx - x - 16)
            by_game(h, p, person, 0, yy + 15, x1 - x - 12, night, rows=rows, left=x + 12)
    return y + ((len(rest) + per - 1) // per) * step


class _Label:
    """What the head of the Hall's sheet asks of a game: its name and its tag's mark, a trophy."""

    LABEL = "hall of fame"

    @staticmethod
    def mark(p, x: int, y: int, ink: str) -> None:
        p.sprite(x, y, GLYPHS[7]["trophy"], {"#": ink})


# --------------------------------------------------------------------------- the badges
def badge(h, hs: dict, i: int, night: bool, moving: bool, stamp: str) -> str:
    """A winner's own badge, as the set draws a badge: their place and login on the set's label, the leader's in
    the set's gold, and their wins on their place's metal, the rest on the set's slate; the leader's glints."""
    person = hs["people"][i]
    label = f"#{i + 1}  {person['badge']}"
    message = f"{person['wins']} win" + ("s" if person["wins"] != 1 else "")
    lab = h.badge_gold() if i == 0 else h.badge_label()
    if i < 3:
        ramp = METALS[METAL[i]]
        val = (ramp[4], ramp[0])
    else:
        val = h.badge_states()["slate"]
    p = h.classic_badge("for-the-badge", label, message, "trophy" if i == 0 else "medal", lab, val, night=night)
    if i == 0 and moving:
        clip = "gpb"
        p.defs.append(f'<clipPath id="{clip}"><rect width="{p.w}" height="{p.h}"/></clipPath>')
        band = {(x, y): f"{PC.IVORY[6]}:0.55" for y in range(p.h) for x in range(-6 + (p.h - y) // 2, -3 + (p.h - y) // 2)}
        travel = p.w + 10
        n = 16
        values = ";".join(f"{_t(travel * j / (n - 1))} 0" for j in range(n))
        keys = ";".join(_t(.8 + .12 * j / (n - 1)) for j in range(n))
        p.raw(25, f'<g clip-path="url(#{clip})"><g>{_paths(band)}<animateTransform attributeName="transform" '
                  f'type="translate" values="0 0;{values};{_t(travel)} 0" keyTimes="0;{keys};1" '
                  f'dur="{_t(h._glint_period())}s" begin="1s" calcMode="discrete" repeatCount="indefinite"/></g></g>',
              "")
    said = f"Hall of Fame: {person['badge']}"
    return p.svg(said, f"Number {i + 1}, {person['badge']}, {person['wins']} wins", still=not moving,
                 stamp=stamp)
