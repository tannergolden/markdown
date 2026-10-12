# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hall of Fame's one layout, which every theme draws: the series of all four games, and the podium.

Every coordinate, size and beat of motion here is the standard theme's, and none of it changes with the theme: a skin
(see `skins`) is handed each part to draw at the place this module gives it and decides only what the part is made
of, so the Hall stands the same in the standard theme and in every print.

The sheet reads top to bottom as a match card. The two sides face each other across the top, as they do on every
board's panel; under them the series, a table whose columns are the house's wins and GitHub's with a bar of the share
between them, the draws in its middle: first all four games together, then each game on a row of its own, Chess
first, named by its mark, its two pieces, the house's first. Then the podium, three blocks in gold, silver and bronze
with the three leading winners standing on them, each with all their wins and their wins in every game beside that
game's mark, in the same order, and the two places after it.
What the data says is fitted to the room each part is given: a name, a login or a number too long for its room is set
a little smaller, down to a floor, and past the floor cut short with an ellipsis.

The motion plays once as the file opens, every animated attribute carrying its resting value: the sides rise; the
series fills row by row, each game's two pieces meeting from either side as its row arrives and each bar sliding open;
the podium's blocks rise out of the floor and the winners step up onto them, third, second, first; and a glint runs
round the gold medal every seven seconds. Drawn inside `motion.at_rest()`, the same sheets are the still files.
"""
from __future__ import annotations

from ...lettering import f1, fx
from ..chess import motion as M
from ..chess.layout import GAP, cut, fit, fitting, flow
from .marks import GITHUB, HOUSE, STEP
from .record import ORDER, OWNER, TITLES
from .skins import Standard

WIDE, NARROW = 830, 360
BAND, PAD = 40, 20
RISE = {2: 1.0, 1: 1.2, 0: 1.4}    # the podium rises third, then second, then first
STAND = (1, 0, 2)                   # the podium's blocks from the left: second, first, third
NAME_ROOM = 120                     # the least room a place's name keeps beside its wins in each game on one row
# How tall each part of a sheet stands, wide and on a phone: the two sides' row; the series, from the top of all four
# games' row to the foot of the last game's; the podium's blocks, the first's the tallest; and the room a winner's
# medal, name and counts take over the tallest block.
MATCH = {"wide": 40, "narrow": 30}
TABLE = {"wide": 40 + 3 * 36 + 22, "narrow": 66 + 3 * 40 + 26}
BLOCKS = {"wide": (58, 44, 32), "narrow": (40, 31, 23)}
STANDING = {"wide": 150, "narrow": 122}


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'s' if n != 1 else ''}"


def games_line(s: dict) -> str:
    """Under a game's name: how many of its games have finished, and how many were drawn."""
    if not s["games"]:
        return "no game finished yet"
    return f"{plural(s['games'], 'game')}  ·  {s['draws']} drawn"


def rose(cv, begin: float, n0: int, how=M.rise) -> None:
    """Everything added to the file since `n0`, risen into place `begin` seconds after it opens, or brought in by
    `how`."""
    added = "".join(cv.body[n0:])
    del cv.body[n0:]
    cv.add(how(added, begin))


def landed(markup: str, begin: float, dur: float = .6, drop: float = 18.0) -> str:
    """Markup that drops onto its place from a little above, `begin` seconds in, and settles with a small bounce:
    a winner stepping up onto their block."""
    if not M.MOTION:
        return markup
    t = begin + dur
    k, k2 = fx(begin / t, 3), fx((begin + dur * .62) / t, 3)
    return (f'<g opacity="1"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k};{k2};1" '
            f'dur="{fx(t, 2)}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" '
            f'values="0 {f1(-drop)};0 {f1(-drop)};0 1.5;0 0" keyTimes="0;{k};{k2};1" dur="{fx(t, 2)}s" '
            f'calcMode="spline" keySplines="0 0 1 1;.5 0 1 .7;.2 .6 .4 1" fill="freeze"/>{markup}</g>')


def grown(cv, markup: str, x: float, top: float, w: float, bottom: float, begin: float, dur: float = .6) -> str:
    """Markup revealed from the bottom up, once, `begin` seconds in: the podium's blocks rising out of the floor."""
    if not M.MOTION:
        return markup
    cid = cv.uid("c")
    t, h = begin + dur, bottom - top
    k = fx(begin / t, 3)
    timing = f'keyTimes="0;{k};1" dur="{fx(t, 2)}s" calcMode="spline" keySplines="0 0 1 1;.2 .7 .2 1" fill="freeze"'
    cv.defs.append(f'<clipPath id="{cid}"><rect x="{f1(x)}" y="{f1(top)}" width="{f1(w)}" height="{f1(h)}">'
                   f'<animate attributeName="y" values="{f1(bottom)};{f1(bottom)};{f1(top)}" {timing}/>'
                   f'<animate attributeName="height" values="0;0;{f1(h)}" {timing}/></rect></clipPath>')
    return f'<g clip-path="url(#{cid})">{markup}</g>'


def slid(markup: str, dx: float, begin: float, dur: float = .55) -> str:
    """Markup that slides `dx` across into its place `begin` seconds in, once."""
    if not M.MOTION:
        return markup
    t = begin + dur
    return ("<g>" + M.ani("transform", f"{f1(dx)} 0;{f1(dx)} 0;0 0", f"0;{fx(begin / t, 3)};1", t,
                          spline="0 0 1 1;.2 .7 .3 1", kind="animateTransform", typ="translate") + markup + "</g>")


def emblem(cv, sk, game: str, x: float, y: float, size: float, *, small: bool = False, begin: float | None = None):
    """A game's own mark: its two pieces, the house's on the left in front of GitHub's, a piece `size` square, the
    house's top-left at (x, y). The white king and then the black, the white man and then the black, the white disc
    and then the black, X and then O: each side's own, whoever moved first. Given `begin`, the two meet from either
    side as their row arrives."""
    behind = sk.piece(cv, game, GITHUB, x + size * STEP, y, size, small=small)
    front = sk.piece(cv, game, HOUSE, x, y, size, small=small)
    if begin is None:
        return behind + front
    return slid(behind, 14, begin) + slid(front, -14, begin)


# --------------------------------------------------------------------------- the two sides
def matchup(cv, sk, x0, x1, y, *, small=False) -> float:
    """The house on the left and GitHub on the right, each on their medallion, as every board's panel sets them;
    wide, a badge between them says what this is, VS, over the halfway line of every bar of the series under it.
    Returns where the row ends."""
    r = 20 if not small else 15
    cy = y + r
    key = 6 if not small else 5.5
    for side, name, sub, tone in (("white", f"@{OWNER.upper()}", "the house", "house"),
                                  ("black", "GITHUB", "everyone else", "world")):
        left = side == "white"
        cx = x0 + r + 4 if left else x1 - r - 4
        cv.add(sk.medallion(cv, cx, cy, r, side))
        tx = cx + r + 12 if left else cx - r - 12
        anchor = "start" if left else "end"
        # the side's key, the colour or the material of its share of every bar, before its words
        cv.add(sk.say(cv, name, tx, cy - 2, 11 if not small else 9.5, ls=.9, anchor=anchor, what="player"),
               sk.key(cv, tx if left else tx - key, cy + 11 - key, key, tone),
               sk.caps(cv, sub, tx + key + 5 if left else tx - key - 5, cy + 11, 7.5 if not small else 7, ls=.6,
                       anchor=anchor, what="side"))
    if not small:
        cols = columns(x0, x1)
        vs = sk.chip("vs", "", size=8.5, lab="label")
        cv.add(vs.draw(cv, (cols["bar0"] + cols["bar1"]) / 2 - vs.w / 2, cy - vs.h / 2, "versus"))
    return y + 2 * r


# --------------------------------------------------------------------------- the series
def columns(x0, x1, *, small=False) -> dict:
    """The series' columns: the name's, the house's count (its right edge), the bar, and GitHub's count."""
    if small:
        return {"name": x0 + 40, "house": x0 + 68, "bar0": x0 + 76, "bar1": x1 - 36, "github": x1 - 28}
    return {"name": x0 + 54, "house": x0 + 250, "bar0": x0 + 262, "bar1": x1 - 82, "github": x1 - 70}


def split(cv, sk, s, x0, x1, y, h, begin) -> str:
    """A bar of a series' games, the house's wins from the left, GitHub's from the right and the draws between, its
    middle ticked; it slides open once. Before a game has finished, an empty track."""
    w = x1 - x0
    out = [sk.track(cv, x0, y, w, h)]
    if s["games"]:
        parts, x = [], x0
        for key, tone in (("house", "house"), ("draws", "draws"), ("github", "world")):
            part = w * s[key] / s["games"]
            if part:
                parts.append(sk.segment(cv, x, y, max(part - (2 if x + part < x1 - .5 else 0), 1), h, tone))
            x += part
        out = [M.wiped(cv, "".join(parts), x0, y - 1, w, h + 2, begin, .9)]
    out.append(sk.tick((x0 + x1) / 2, y - 3, y + h + 3))
    return "".join(out)


def counts(cv, sk, s, cols, y, size) -> None:
    """A row's two counts at the ends of its bar: the house's ending where the bar starts, GitHub's after it."""
    cv.add(sk.say(cv, str(s["house"]), cols["house"], y, size, role="strong", anchor="end", what="house"),
           sk.say(cv, str(s["github"]), cols["github"], y, size, role="strong", what="github"))


def sized(sk, s, size, floor, rooms) -> float:
    """The one size a row's two counts are set at: `size`, or smaller down to `floor` until each fits its room."""
    return min(fit(sk, str(s[key]), "bold", size, floor, room) for key, room in zip(("house", "github"), rooms))


def row(cv, sk, s, label, x1, y, cols, *, size, floor, name, sub=6.5) -> None:
    """A row of the series, wide: its name and how many games it counts, its two counts and the bar between. The
    counts give way before the name does, down to their floor, so a name is whole whatever the counts."""
    lw = sk.width(label.upper(), "bold", name, .7)
    size = sized(sk, s, size, floor, (cols["house"] - cols["name"] - lw - GAP, x1 - cols["github"]))
    room = cols["house"] - sk.width(str(s["house"]), "bold", size) - GAP - cols["name"]
    text, ns = fitting(sk, label.upper(), "bold", name, name - 1.5, room, .7)
    games, gs = fitting(sk, games_line(s), "caps", sub, 5.5, room, .5)
    cv.add(sk.say(cv, text, cols["name"], y + 4, ns, ls=.7, what="series"),
           sk.caps(cv, games, cols["name"], y + 16, gs, ls=.5, what="series games"))
    counts(cv, sk, s, cols, y + 4 + size * .36, size)


def series(cv, sk, h, x0, x1, y) -> float:
    """The series, wide: all four games together, then each game on a row of its own, Chess first."""
    cols = columns(x0, x1)
    t = h["totals"]
    n0 = len(cv.body)
    row(cv, sk, t, "all four games", x1, y, cols, size=26, floor=8, name=10.5)
    cv.add(split(cv, sk, t, cols["bar0"], cols["bar1"], y, 10, .45))
    rose(cv, .3, n0)
    top, y = y, y + 40
    cv.add(sk.rule(cols["name"], x1, y - 10))
    for i, game in enumerate(ORDER):
        s, at = h["series"][game], .55 + .12 * i
        n0 = len(cv.body)
        cv.add(emblem(cv, sk, game, x0, y - 9, 26, begin=at))
        row(cv, sk, s, TITLES[game], x1, y, cols, size=13, floor=7, name=10)
        cv.add(split(cv, sk, s, cols["bar0"], cols["bar1"], y + .5, 7, at + .1))
        rose(cv, at, n0)
        y += 36
    return top + TABLE["wide"]


def series_small(cv, sk, h, x0, x1, y) -> float:
    """The series on a phone: the totals across the middle, big, either side of VS, over the bar of their share;
    then each game on two lines, its pieces and name over the bar of its own share."""
    t = h["totals"]
    mid = (x0 + x1) / 2
    n0 = len(cv.body)
    vs = sk.chip("vs", "", size=7.5, lab="label")
    side = mid - vs.w / 2 - GAP - x0
    big = sized(sk, t, 24, 10, (side, side))
    cv.add(sk.say(cv, str(t["house"]), mid - vs.w / 2 - GAP, y + 17, big, role="strong", anchor="end", what="house"),
           vs.draw(cv, mid - vs.w / 2, y + 8.5 - vs.h / 2 + 1, "versus"),
           sk.say(cv, str(t["github"]), mid + vs.w / 2 + GAP, y + 17, big, role="strong", what="github"))
    line, ls = fitting(sk, f"all four games  ·  {games_line(t)}", "caps", 6.5, 5.5, x1 - x0, .5)
    cv.add(sk.caps(cv, line, mid, y + 31, ls, ls=.5, anchor="middle"))
    cv.add(split(cv, sk, t, x0, x1, y + 38, 8, .45))
    rose(cv, .3, n0)
    top, y = y, y + 66
    cols = columns(x0, x1, small=True)
    for i, game in enumerate(ORDER):
        s, at = h["series"][game], .55 + .12 * i
        n0 = len(cv.body)
        cv.add(emblem(cv, sk, game, x0, y - 5, 22, begin=at))
        title = TITLES[game].upper()
        nw = sk.width(title, "bold", 9.5, .6)
        sub, ss = fitting(sk, games_line(s), "caps", 6.5, 5.5, x1 - cols["name"] - nw - GAP, .5)
        cv.add(sk.say(cv, title, cols["name"], y + 3, 9.5, ls=.6, what="series"),
               sk.caps(cv, sub, x1, y + 3, ss, ls=.5, anchor="end"))
        size = sized(sk, s, 11.5, 5.5, (cols["house"] - cols["name"], x1 - cols["github"]))
        counts(cv, sk, s, cols, y + 20, size)
        cv.add(split(cv, sk, s, cols["bar0"], cols["bar1"], y + 12, 6, at + .1))
        rose(cv, at, n0)
        y += 40
    return top + TABLE["narrow"]


# --------------------------------------------------------------------------- the podium
def by_game(cv, sk, p, x, y, room, *, size=13, rows=1, anchor="start") -> float:
    """A winner's wins in every game, Chess first, each beside that game's own mark, a game they have yet to win set
    faint: in slots of one width, on one row or on two rows of two, no wider in all than `room`; from `x`, or centred
    on it when `anchor` is middle. Where the room is short the marks give way first, set smaller down to the width of
    a single piece, so a count keeps its size; only past that is a count set smaller, so none meets the next game's
    mark. Returns the width it took."""
    per = len(ORDER) // rows
    figure = 9 if size > 12 else 8.5
    texts = [str(p["by_game"][game]) for game in ORDER]
    widest = max(sk.width(t, "bold", figure) for t in texts)
    natural = size * (1 + STEP)
    slot = min(room / per, natural + 2 + widest + 10)
    mark = max(size, min(natural, slot - 2 - widest - 6))   # the mark's width: what the slot leaves beside its count
    piece = mark / (1 + STEP)
    left = x - slot * per / 2 if anchor == "middle" else x
    for i, game in enumerate(ORDER):
        col, row = i % per, i // per
        n, text = p["by_game"][game], texts[i]
        ns = fit(sk, text, "bold", figure, 4.5, slot - mark - 2 - 6)
        gx, gy = left + col * slot, y + row * (size + 3)
        pieces = emblem(cv, sk, game, gx, gy - size * .78 + (size - piece) / 2, piece, small=True)
        word = sk.say(cv, text, gx + mark + 2, gy, ns, role="strong" if n else "muted", what="wins in a game")
        cv.add(f'<g opacity=".38">{pieces}{word}</g>' if not n else pieces + word)
    return slot * per


def by_game_width(sk, p, size=12, rows=1) -> float:
    """How wide a winner's wins in every game stand, at their size: what `by_game` takes when it has the room."""
    figure = 9 if size > 12 else 8.5
    widest = max(sk.width(str(p["by_game"][game]), "bold", figure) for game in ORDER)
    return (len(ORDER) // rows) * (size * (1 + STEP) + 2 + widest + 10)


def stand(cv, sk, p, i, cx, top, w, *, small=False) -> None:
    """A winner standing on their block, centred on `cx` over the block's top at `top`: their medal, their name and
    handle, all their wins, their wins in each game, and on a wide sheet the day of their last."""
    k = 1 if not small else .82
    r = 20 if not small else 15
    room = w - (16 if not small else 8)
    if small:
        pips, wins, handle, name = top - 22, top - 38, top - 53, top - 63
    else:
        pips, wins, handle, name = top - 24, top - 42, top - 61, top - 74
    face = name - 10.5 * k - 7 - r - 4.5
    if i == 0:
        cv.add(sk.spotlight(cv, cx, face, r))
    cv.add(sk.face(cv, cx, face, r, p, i, medal=i, glint=i == 0))
    nsize = sk.fitted(p["name"], 10.5 * k, 7, room, .07)
    hsize = fit(sk, p["handle"], "caps", 7.5 * k, 6, room, .6)
    cv.add(sk.say(cv, cut(sk, p["name"], "bold", nsize, room, nsize * .07), cx, name, nsize, ls=nsize * .07,
                  anchor="middle"),
           sk.caps(cv, cut(sk, p["handle"], "caps", hsize, room, .6), cx, handle, hsize, ls=.6, anchor="middle"))
    num = str(p["wins"])
    label = "wins" if p["wins"] != 1 else "win"
    lw = sk.width(label.upper(), "caps", 7.5 * k, .6)
    ns = fit(sk, num, "bold", 20 * k, 10, room - lw - 5)
    nw = sk.width(num, "bold", ns)
    left = cx - (nw + 5 + lw) / 2
    cv.add(sk.say(cv, num, left, wins, ns, role="strong"), sk.caps(cv, label, left + nw + 5, wins, 7.5 * k, ls=.6))
    if small:
        by_game(cv, sk, p, cx, pips, room, size=11, rows=2, anchor="middle")
    else:
        by_game(cv, sk, p, cx, pips, room, size=13, anchor="middle")
        games = plural(p["games"], "game")
        line, gs = fitting(sk, f"last win {p['last']}  ·  {games}" if p["last"] else games, "caps", 7, 6, room, .5)
        cv.add(sk.caps(cv, line, cx, top - 8, gs, ls=.5, anchor="middle"))


def empty(cv, sk, i, cx, top, w, *, small=False) -> None:
    """A place on the podium nobody has taken yet: an empty medal, waiting, and who stands there next, said whole
    on a line, or on two where a phone's place is too narrow for one."""
    k = 1 if not small else .82
    r = 20 if not small else 15
    said = "the next to win stands here" if i == 0 else "a place on the podium"
    size, lines = flow(lambda line, z: sk.width(line.upper(), "caps", z, .6), said, 7 * k, 6, w - 8)
    name = top - 26 * k - 9 * (len(lines) - 1)
    cv.add(sk.vacant(cv, cx, name - 10.5 * k - 8 - r - 4.5, r, i),
           sk.say(cv, "NOBODY YET", cx, name, 10.5 * k, role="muted", ls=.7, anchor="middle"),
           *(sk.caps(cv, line, cx, name + 14 * k + j * 9, size, ls=.6, anchor="middle")
             for j, line in enumerate(lines)))


def podium(cv, sk, h, x0, x1, ground, *, small=False) -> None:
    """The three leading winners on their blocks, second, first and third from the left, the first's the tallest;
    each place rises in turn, third, second, first."""
    heights = BLOCKS["narrow" if small else "wide"]
    w = (x1 - x0) / 3
    steps = [(x0 + col * w, w, heights[place], place) for col, place in enumerate(STAND)]
    n0 = len(cv.body)
    sk.podium(cv, steps, ground, 24 if not small else 18)
    rose(cv, .8, n0, lambda markup, begin: grown(cv, markup, x0 - 2, ground - heights[0] - 2, x1 - x0 + 10,
                                                   ground + 8, begin))
    people = h["people"]
    for x, sw, sh, place in sorted(steps, key=lambda s: -s[3]):
        n0 = len(cv.body)
        if place < len(people):
            stand(cv, sk, people[place], place, x + sw / 2, ground - sh, sw, small=small)
            rose(cv, RISE[place], n0, landed)
        else:
            empty(cv, sk, place, x + sw / 2, ground - sh, sw, small=small)
            rose(cv, RISE[place], n0)


def mentions(cv, sk, h, x0, x1, y, start=3, *, small=False) -> float:
    """The places after the podium: the number, the name and handle, the wins in each game and all of them on a
    badge; two to a row, the wins in each game two by two, and on a phone one to a row, its wins in each game on a
    line under the name."""
    rest = h["people"][start:]
    per = 1 if small else 2
    colw = (x1 - x0) / per
    step = 46 if small else 34
    for i, p in enumerate(rest):
        col, row = i % per, i // per
        x, yy = x0 + col * colw, y + row * step
        cv.add(sk.number(cv, start + i + 1, x, yy, 18))
        chip = sk.chip("wins", str(p["wins"]), size=7.5, lab="label", msg="place")
        cx = x + colw - chip.w - (0 if small or col else 14)
        if small:
            named(cv, sk, p, x + 28, yy + 9, cx - GAP - x - 28)
            by_game(cv, sk, p, x + 28, yy + 34, x + colw - x - 28, size=12)
        else:
            # the wins in each game on one row where the name keeps room enough beside it, else two by two: as the
            # standard theme's letters measure it, so a place stands the same in every theme
            free = cx - GAP - x - 28
            rows = 1 if one_row(p, colw - (0 if col else 14) - GAP - 28) else 2
            games = min(by_game_width(sk, p, 12, rows), free / 2)
            named(cv, sk, p, x + 28, yy + 9, cx - GAP - games - GAP - x - 28)
            by_game(cv, sk, p, cx - GAP - games, yy + (12 if rows == 1 else 8), games, size=12, rows=rows)
        cv.add(chip.draw(cv, cx, yy - 2, "wins"))
    return y + ((len(rest) + per - 1) // per) * step


def one_row(p, room: float) -> bool:
    """Whether a place's wins in each game stand on one row beside its name, which keeps `NAME_ROOM` of `room`, the
    width its column leaves after its number: measured in the standard theme's letters and badge, whatever the tone."""
    std = Standard("day")
    chip = std.chip("wins", str(p["wins"]), size=7.5, lab="label", msg="place")
    return room - chip.w - by_game_width(std, p, 12) - GAP >= NAME_ROOM


def named(cv, sk, p, x, y, room) -> None:
    """A place's name, and its handle under it in small capitals, each fitted to `room`."""
    ns = sk.fitted(p["name"], 9, 7, room, .6 / 9)
    handle, hs = fitting(sk, p["handle"], "caps", 7, 6, room, .5)
    cv.add(sk.say(cv, cut(sk, p["name"], "bold", ns, room, ns * .6 / 9), x, y, ns, ls=ns * .6 / 9),
           sk.caps(cv, handle, x, y + 12, hs, ls=.5))


# --------------------------------------------------------------------------- the sheet
def hall_sheet(sk, h: dict, title: str, desc: str, variant: str = "wide") -> str:
    still = "" if M.MOTION else " still"
    games = plural(h["totals"]["games"], "game") if h["totals"]["games"] else "no games yet"
    rest = h["people"][3:]
    if variant == "wide":
        W = WIDE
        top = BAND + 22
        series_top = top + MATCH["wide"] + 26
        ground = series_top + TABLE["wide"] + 30 + STANDING["wide"] + BLOCKS["wide"][0]
        H = ground + 14 + (22 + 34 * ((len(rest) + 1) // 2) if rest else 0) + PAD
        cv = sk.new(W, H, title, desc, "elements hall-of-fame wide", still)
        sk.frame(cv, W, H, "hall of fame", "trophy", games, f"four games  ·  @{OWNER} vs. github")
        M.risen(cv, .15, matchup, cv, sk, PAD, W - PAD, top)
        y = series(cv, sk, h, PAD, W - PAD, series_top)
        cv.add(sk.rule(PAD, W - PAD, y + 8))
        podium(cv, sk, h, PAD, W - PAD, ground)
        if rest:
            cv.add(sk.rule(PAD, W - PAD, ground + 16))
            M.risen(cv, 1.6, mentions, cv, sk, h, PAD, W - PAD, ground + 32)
        return cv.svg()
    W = NARROW
    top = BAND + 20
    series_top = top + MATCH["narrow"] + 20
    ground = series_top + TABLE["narrow"] + 24 + STANDING["narrow"] + BLOCKS["narrow"][0]
    H = ground + 12 + (20 + 46 * len(rest) if rest else 0) + PAD
    cv = sk.new(W, H, title, desc, "elements hall-of-fame narrow", still)
    sk.frame(cv, W, H, "hall of fame", "trophy", games)
    M.risen(cv, .15, matchup, cv, sk, PAD, W - PAD, top, small=True)
    y = series_small(cv, sk, h, PAD, W - PAD, series_top)
    cv.add(sk.rule(PAD, W - PAD, y + 4))
    podium(cv, sk, h, PAD, W - PAD, ground, small=True)
    if rest:
        cv.add(sk.rule(PAD, W - PAD, ground + 14))
        M.risen(cv, 1.6, mentions, cv, sk, h, PAD, W - PAD, ground + 30, small=True)
    return cv.svg()
