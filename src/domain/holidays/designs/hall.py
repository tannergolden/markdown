# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hall of Fame of all four games as a pixel set draws it: the series, the podium, and a badge for every winner.

The Hall reads as it does in the standard theme and every print, a match card, top to bottom: the house and GitHub
facing each other across the top on their medallions; the series under them, all four games together and then each
on a row of its own, Chess first, each named by its two pieces, the house's first, its two counts either side of a
bar of the share; then the podium, three blocks struck in the trophies' gold, silver and bronze, second, first and
third from the left, each winner standing on theirs as the set draws a person, its avatar, in a ring of its metal,
with their wins and their wins in every game; and the two places after it. What the set adds is its world: its paper,
frame and tag, its lettering, its avatars and its tags for every count.

As the file opens the series fills row by row, the blocks rise out of the floor, third, second, first, the winners
appear on them, and a glint runs round the gold ring every so often, on the hand's period in a collection's design.
A winner's badge is the set's own badge, the leader's in the set's gold, glinting.
"""
from __future__ import annotations

import math

from ...elements.chess.game import OWNER
from ...elements.hall import record as R
from ..pixel import GLYPHS, Pix, fold, measure
from . import pieces as PC
from .boards import put, ring_cells
from .games import _nothing, _paths, _t, appear, steps
from .trophies import FLARE, METALS

STAND = (1, 0, 2)            # the podium's blocks from the left: second, first, third
BLOCKS = {"wide": (30, 23, 17), "narrow": (21, 16, 12)}
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


def games_line(s: dict) -> str:
    if not s["games"]:
        return "no game finished yet"
    return f"{plural(s['games'], 'game')}  ·  {s['draws']} drawn"


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
    """One of a game's pieces at the Hall's size, its foot on row `y + 11`: a king, a man, a disc or a pen's
    mark. Returns its drawing's width."""
    if game == "chess":
        d = PC.chessman("king", "mini", material)
    elif game == "checkers":
        d = PC.man(material, 4, 2, 2)
    elif game == "connectfour":
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
            for xx in range(x, min(inner1, x + part)):
                for j in range(hgt):
                    if ramp is None:
                        c = b["dark"] if 0 < j < hgt - 1 else (b["light"] if j == 0 else b["edge"])
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


def block(h, p, x: int, w: int, ground: int, ht: int, place: int, night: bool, L: str = "base") -> None:
    """A block of the podium: its front struck in its place's metal, lit along its top and down its left, its
    number on its face."""
    ramp = METALS[METAL[place]]
    top = ground - ht
    for yy in range(top, ground):
        for xx in range(x, x + w):
            tone = 4 if yy < top + 2 else 3
            if xx == x:
                tone = 5
            elif xx >= x + w - 2:
                tone = 2
            if yy == ground - 1:
                tone = 1
            p.px(xx, yy, ramp[tone], L)
    p.hline(x, x + w, top, ramp[6], L)
    p.hline(x, x + w, top + 1, ramp[5], L)
    label = str(place + 1)
    scale = 2 if ht >= 16 else 1
    lw = measure(label, "57", scale)
    lx, ly = x + (w - lw) // 2, top + (ht - 7 * scale) // 2 + 1
    p.text(lx, ly, label, ramp[0], "57", scale, L=L, shadow=ramp[5])


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
    h.say(p, cx, y, person["name"], k["body"], room=room, anchor="middle")
    y += 8
    h.say(p, cx, y, person["handle"].upper(), k["muted"], room=room, anchor="middle")
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
    p = h.canvas(W, end + 10)
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
            h.say(p, cols["name"], y + 9, games_line(t).upper(), k["muted"],
                  room=cols["house"] - hw - GAP - cols["name"])
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
                h.say(p, cols["name"], y + 7, games_line(s).upper(), k["muted"],
                      room=cols["house"] - hw - GAP - cols["name"])
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
            h.say(p, mid, y + 17, f"ALL FOUR GAMES  ·  {games_line(t)}".upper(), k["muted"], anchor="middle",
                  room=x1 - x0)
            shares(h, p, t, x0, x1, y + 25, night)
        y += 37
        cols = phone_columns(hs, x0, x1)
        for i, game in enumerate(R.ORDER):
            s = hs["series"][game]
            with section(f"row{i}", .45 + .12 * i):
                mark(p, game, x0, y)
                title = R.TITLES[game].upper()
                tw = h.say(p, cols["name"], y, title, k["body"])
                h.say(p, x1, y, games_line(s).upper(), k["muted"], anchor="end", room=x1 - cols["name"] - tw - 6)
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
        block(h, p, bx + 1, bw - 2, ground, heights[place], place, night, L)
        if place < len(people):
            with section(f"stand{place}", RISE[place] + .05):
                winner(h, p, people[place], place, bx + bw // 2, top, bw, night, not wide, moving, rows, lift)
        else:
            with section(f"stand{place}", RISE[place] + .05):
                vacant(h, p, place, bx + bw // 2, top, bw, night, not wide, lift)
    p.hline(x0 - 2, x1 + 2, ground, b["shade"])
    y = ground + 6
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
