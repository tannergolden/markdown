# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess sheets' one layout, which every theme draws: the board and its panel, and the Hall of Fame.

Every coordinate, size and beat of motion here is the standard theme's, and none of it changes with the theme: a
skin (see `skins`) is handed each part to draw at the place this module gives it and decides only what the part is
made of. So the board stands in the same place, the same size, beside the same panel, in the standard theme and in
every print, and a page that changes theme keeps its layout.

What the data says is fitted to the room each part is given, measured in the skin's own letters: a sentence, a
name or a login too long for its room is set a little smaller, down to a floor, and past the floor cut short with
an ellipsis, so nothing runs into the next part or off the sheet. The last move's words take a line or two, as many
as the standard theme's letters need, so a sheet is as tall in every theme.

The motion plays once as the file opens, every animated attribute carrying its resting value so a file is complete
without it: the last move's piece comes in from its square, a knight leaping and anything else gliding, a castling
king's rook hopping round it, its square is marked as it lands and a check blooms on the king; the panel rises into
place a section at a time. On the Hall of Fame the podium rises third, second, first, the bars fill, and a glint
runs round the gold medal every seven seconds. Drawn inside `motion.at_rest()`, the same sheets are the still files.
"""
from __future__ import annotations

import itertools

from ...lettering import f1, fx, width
from . import motion as M
from .game import FILES, GITHUB, NAMES, OWNER, VALUE, called, turn_name
from .shapes import FOOT

WIDE, NARROW = 830, 360
BAND, PAD = 40, 20  # the head's depth and the sheet's margin, the standard theme's
GAP = 8             # what keeps a run of lettering off the next thing along: a rule, a number, a badge
LEAD = 14           # from one line of the last move's words to the next
TRIM = " ,.;:-·"    # what an ellipsis takes off the end it follows, so it never comes after a space or a comma


def sq_xy(name: str, x0: float, y0: float, s: float) -> tuple[float, float]:
    f, r = FILES.index(name[0]), int(name[1])
    return x0 + f * s, y0 + (8 - r) * s


# --------------------------------------------------------------------------- lettering that fits
# `face` is a skin's: "bold" for names and figures, "regular" for a sentence, "caps" for the small capitals.
def fit(sk, s, face, size, floor, room, ls=0.0) -> float:
    """The largest size, from `size` down to `floor` a quarter point at a time, at which `s` fits `room`."""
    s = str(s).upper() if face == "caps" else str(s)
    while size > floor and sk.width(s, face, size, ls) > room:
        size -= .25
    return size


def cut(sk, s, face, size, room, ls=0.0, tail="") -> str:
    """`s` and its `tail` as they fit `room` at `size`: whole, or `s` cut short with an ellipsis before the tail."""
    s = str(s)

    def wide(t):
        t += tail
        return sk.width(t.upper() if face == "caps" else t, face, size, ls)
    if wide(s) <= room:
        return s + tail
    while s and wide(s.rstrip(TRIM) + "…") > room:
        s = s[:-1]
    return s.rstrip(TRIM) + "…" + tail


def fitting(sk, s, face, size, floor, room, ls=0.0) -> tuple[str, float]:
    """`s` as it fits `room`, and its size: smaller down to `floor` if it must be, and cut short there if even that
    is not enough."""
    size = fit(sk, s, face, size, floor, room, ls)
    return cut(sk, s, face, size, room, ls), size


def flow(measure, s: str, size: float, floor: float, room: float, rows: int = 2, least: int = 1):
    """A sentence wrapped into `least` to `rows` lines no wider than `room`, as `measure(line, size)` measures a
    line: the fewest lines, split evenest, at the largest size from `size` down to `floor` half a point at a time.
    A split at the sentence's commas is taken where it is nearly as even, so a line ends where a reader pauses.
    Past the floor the lines are filled in turn and the last is cut short with an ellipsis. (size, lines)"""
    words = s.split()
    while True:
        for count in range(least, min(rows, len(words)) + 1):
            best = None
            for cuts in itertools.combinations(range(1, len(words)), count - 1):
                bounds = (0, *cuts, len(words))
                lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:])]
                widest = max(measure(line, size) for line in lines)
                pause = all(line.endswith((",", ".", ";")) for line in lines[:-1])
                score = widest + (0 if pause else room * .15)
                if widest <= room and (best is None or score < best[0]):
                    best = (score, lines)
            if best:
                return size, best[1]
        if size <= floor:
            break
        size = max(floor, size - .5)
    lines = []
    while len(words) > 1 and len(lines) < rows - 1 and measure(words[0], size) <= room:
        n = 1
        while n < len(words) and measure(" ".join(words[:n + 1]), size) <= room:
            n += 1
        lines.append(" ".join(words[:n]))
        words = words[n:]
    rest = " ".join(words)
    if measure(rest, size) > room:
        while rest and measure(rest.rstrip(TRIM) + "…", size) > room:
            rest = rest[:-1]
        rest = rest.rstrip(TRIM) + "…"
    return size, lines + [rest]


# --------------------------------------------------------------------------- the board
def passed(last: dict, placed: dict) -> str:
    """The square the piece the last move took stood on: the one the taker landed on, except for a pawn taken en
    passant, which stood beside the pawn that took it, a rank short of where that one landed."""
    beside = last["to"][0] + last["from"][1]
    if (last["piece"] == "pawn" and last.get("captured") == "pawn" and last["from"][0] != last["to"][0]
            and "en passant" in last["words"].lower() and beside not in placed):
        return beside
    return last["to"]


def castled(last: dict, placed: dict) -> tuple[str, str] | None:
    """For a king that castled, its rook's squares: the corner it came from and the one it stands on; else None."""
    if (last["piece"] != "king" or last["from"][1] != last["to"][1]
            or abs(FILES.index(last["to"][0]) - FILES.index(last["from"][0])) != 2):
        return None
    rank = last["to"][1]
    corner, beside = ("h" + rank, "f" + rank) if last["to"] > last["from"] else ("a" + rank, "d" + rank)
    return (corner, beside) if placed.get(beside, "").lower() == "r" else None


def arrive(cv, sk, kind, side, x, y, fx0, fy0, s, beats, lift, swell) -> str:
    """A piece coming in to its square at (x, y) from the one at (fx0, fy0) on `beats`, the keyTimes of the last
    move's `LEAP` at which it sets off, passes the midpoint and lands: it rises `lift` of a square by the midpoint,
    swelling by `swell`, and its shadow slides along under it, thinning as it lifts."""
    k = s / 45
    go, mid, land = beats
    dx, dy = fx0 - x, fy0 - y
    mx, my = dx / 2, dy / 2 - s * lift
    t = f"0;{go};{mid};{land};1"
    sx, sy, rx, ry = x + FOOT[0] * k, y + FOOT[1] * k, FOOT[2] * k, FOOT[3] * k
    shadow = (f'<g>{M.ani("transform", f"{f1(dx)} {f1(dy)};{f1(dx)} {f1(dy)};0 0;0 0", f"0;{go};{land};1", M.LEAP, spline="0 0 1 1;.35 0 .35 1;0 0 1 1", kind="animateTransform", typ="translate")}'
              + sk.foot(cv, sx, sy, rx, ry,
                        M.ani("rx", f"{f1(rx)};{f1(rx)};{f1(rx * .5)};{f1(rx)};{f1(rx)}", t, M.LEAP)
                        + M.ani("opacity", "1;1;.35;1;1", t, M.LEAP))
              + "</g>")
    pid = sk.piece_def(cv, kind, side, shadow=False)
    cx, cy = x + s / 2, y + s / 2
    return (shadow
            + f'<g>{M.ani("transform", f"{f1(dx)} {f1(dy)};{f1(dx)} {f1(dy)};{f1(mx)} {f1(my)};0 0;0 0", t, M.LEAP, spline="0 0 1 1;.3 0 .6 1;.4 0 .25 1;0 0 1 1", kind="animateTransform", typ="translate")}'
            f'<g transform="translate({f1(cx)} {f1(cy)})"><g>'
            + M.ani("transform", f"1;1;{swell};1;1", t, M.LEAP, spline="0 0 1 1;.3 0 .6 1;.4 0 .25 1;0 0 1 1",
                    kind="animateTransform", typ="scale")
            + f'<use href="#{pid}" transform="translate({f1(-s / 2)} {f1(-s / 2)}) scale({fx(k, 4)})"/>'
            + "</g></g></g>")


def board(cv, sk, g: dict, x0: float, y0: float, s: float) -> None:
    """The eight ranks with their pieces, the last move marked from and to, the checked king marked, and the
    coordinates round it. The piece that moved last comes in from its square as the file opens: a knight leaps,
    anything else glides, and a castling king's rook hops round it a beat behind; what it took fades as it lands,
    on the square it stood on."""
    placed = g["placement"]
    last = g["last"]
    n = 8 * s
    k = s / 45
    sk.board_base(cv, x0, y0, s)
    if last:
        fx0, fy0 = sq_xy(last["from"], x0, y0, s)
        tx0, ty0 = sq_xy(last["to"], x0, y0, s)
        sk.mark_from(cv, fx0, fy0, s, last)
        sk.mark_to(cv, tx0, ty0, s, M.ani("opacity", "0;0;1;1", f"0;{M.LAND - .04};{M.LAND + .06};1", M.LEAP))
    clip = cv.uid("b")
    cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(n)}" height="{f1(n)}"/></clipPath>')
    check = sq_xy(g["check"], x0, y0, s) if g["check"] else None
    pulse = M.ani("opacity", "0;0;1;.5;1;.5;1", ".0;.27;.38;.52;.66;.8;1", M.LEAP / M.LAND * 1.18 + 2.4)
    sk.board_over(cv, clip, x0, y0, s, check, pulse)
    sk.bevel(cv, x0, y0, n)
    pieces, moving = [], []
    rook = castled(last, placed) if last and M.MOTION else None
    for name in sorted(placed, key=lambda q: (-int(q[1]), FILES.index(q[0]))):
        pc = placed[name]
        x, y = sq_xy(name, x0, y0, s)
        kind, side = NAMES[pc.lower()], "white" if pc.isupper() else "black"
        if last and name == last["to"] and M.MOTION:
            leap = kind == "knight"
            mover = arrive(cv, sk, kind, side, x, y, fx0, fy0, s, (".25", ".48", f"{M.LAND}"), .62 if leap else .12,
                           "1.16" if leap else "1.07")
            if last.get("captured"):
                other = "black" if side == "white" else "white"
                gone = sk.piece_def(cv, last["captured"], other)
                gx, gy = sq_xy(passed(last, placed), x0, y0, s)
                mover = (f'<use href="#{gone}" transform="translate({f1(gx)} {f1(gy)}) scale({fx(k, 4)})" opacity="0">'
                         + M.ani("opacity", "1;1;0;0", f"0;{M.LAND - .05};{M.LAND + .05};1", M.LEAP) + "</use>"
                         + mover)
            moving.insert(0, mover)
            continue
        if rook and name == rook[1]:
            # the castle's rook: it sets off a beat after its king and hops round it, landing a beat after it
            rx0, ry0 = sq_xy(rook[0], x0, y0, s)
            moving.append(arrive(cv, sk, kind, side, x, y, rx0, ry0, s, (".36", ".6", ".84"), .4, "1.07"))
            continue
        pieces.append(sk.put(cv, kind, side, x, y, s))
    cv.add("".join(pieces) + "".join(moving))
    if last and M.MOTION:
        # the landing: a flash on the square and a ring running out from it
        cx, cy = tx0 + s / 2, ty0 + s / 2
        cv.add(f'<rect x="{f1(tx0)}" y="{f1(ty0)}" width="{f1(s)}" height="{f1(s)}" fill="{sk.flash}" opacity="0">'
               + M.ani("opacity", "0;0;.7;0;0", f"0;{M.LAND - .02};{M.LAND + .03};.95;1", M.LEAP) + "</rect>"
               f'<g clip-path="url(#{clip})"><circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(s * .3)}" fill="none" '
               f'{sk.ripple} opacity="0">'
               + M.ani("r", f"{f1(s * .3)};{f1(s * .3)};{f1(s * 1.15)};{f1(s * 1.15)}", f"0;{M.LAND};.98;1", M.LEAP + .5)
               + M.ani("opacity", "0;0;.9;0;0", f"0;{M.LAND - .01};{M.LAND + .02};.98;1", M.LEAP + .5)
               + "</circle></g>")
    size = 9 if s > 40 else 8.5
    for i in range(8):
        cv.add(sk.say(cv, FILES[i], x0 + i * s + s / 2, y0 + n + 16, size, role="muted", anchor="middle", what="file"),
               sk.say(cv, str(8 - i), x0 - 11, y0 + i * s + s / 2 + sk.cap(size) / 2, size, role="muted",
                      anchor="middle", what="rank"))


# --------------------------------------------------------------------------- the panel
def matchup(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """The two sides across one row, the house on the left and GitHub on the right, the side to move ringed."""
    r = 15 if not small else 13
    cy = y + r
    n = st["players"]
    playing = f"{n} PLAYER{'S' if n != 1 else ''}" if n else "EVERYONE ELSE"
    for side, name, sub in (("white", f"@{OWNER.upper()}", "WHITE  ·  THE HOUSE"),
                            ("black", "GITHUB", f"BLACK  ·  {playing}")):
        left = side == "white"
        cx = x0 + r + 3 if left else x1 - r - 3
        cv.add(sk.medallion(cv, cx, cy, r, side))
        if st["to_move"] == side and not st.get("result"):     # once the game is over, it is nobody's turn
            cv.add(sk.turn_ring(cv, cx, cy, r + 3.4, 1.1))
        tx = cx + r + 11 if left else cx - r - 11
        anchor = "start" if left else "end"
        cv.add(sk.say(cv, name, tx, cy - 2, 10 if not small else 9.5, ls=.8, anchor=anchor, what="player"),
               sk.caps(cv, sub, tx, cy + 11, 7, ls=.55, anchor=anchor, what="player role"))
    if not small:   # a phone's row has no room between the names for it: the two sides stand apart without it
        cv.add(sk.caps(cv, "vs", (x0 + x1) / 2, cy + 3, 8, ls=1, anchor="middle", what="versus"))
    return y + 2 * r + 3


def turn_row(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """Whose turn it is, a badge under that side, and the day the move is due by on the other; once the game is
    over, who won and how (`finished`). In check, the badge's second panel slides open out of it as the move
    lands; every eight seconds a glint crosses it, the call to play."""
    if st.get("result"):
        return plate_row(cv, sk, x0, x1, y, *finished(st), small=small, keep_note=True)
    notes = ((f"due by {st['due']}", f"by {st['due']}") if st["due"]
             else ("no clock until the first move", "no clock yet"))
    return plate_row(cv, sk, x0, x1, y, f"{turn_name(st)}'s turn", "in check" if st["check"] else "", "play",
                     st["to_move"] == "black", notes, small=small)


def finished(st: dict) -> tuple[str, str, str, bool, tuple[str, ...]]:
    """A finished game's plate, as every game sets it in the turn's place: who won, under the winner's side, with
    how in its second panel, or that it was drawn; and across the row the day the fresh board comes.
    (label, message, icon, on the right, notes)"""
    winner, how = st["result"]["winner"], st["result"]["how"]
    notes = ((f"next game {st['next']}", f"next {st['next']}") if st["next"]
             else (f"game {st['game']} is over", "game over"))
    return (f"{called(winner)} wins" if winner else "drawn", how, "trophy" if winner else "scale",
            winner == GITHUB, notes)


def outcome(st: dict) -> str:
    """Where a finished game's score sheet would name whose turn it is: who won, or that it was drawn."""
    winner = st["result"]["winner"]
    return f"{called(winner)} wins" if winner else "drawn"


def plate_row(cv, sk, x0, x1, y, label, message, icon, right, notes, *, small=False, keep_note=False) -> float:
    """A plate across the panel's row, under the side it is about (on the `right`, GitHub's), with what it adds
    sliding open out of it as the move lands, and across the row the first of `notes` that fits beside it. Every
    eight seconds a glint crosses the plate. It is set at its size, or smaller if the row cannot hold it; a plate
    that must `keep_note` gives way to the note as well, a little to say it in full and as far as it must to say it
    short, so the note is never cut."""
    def plate(size):
        return (sk.chip(label, message, icon=icon, size=size, lab="turn", msg="alert") if message
                else sk.chip(label, "", icon=icon, size=size, lab="turn"))

    def beside(note, size):
        return plate(size).w + GAP + sk.width(note.upper(), "caps", 6.5, .6)

    size = 10 if not small else 8.5
    tall = plate(size).h                  # the row is as tall as the plate at its size, whatever it is set at
    while True:
        full = plate(size)
        if full.w <= x1 - x0 or size <= 7:
            break
        size -= .25
    if keep_note:
        # as far as 6.5 to say it short: the house's win by three boards in a row, Tic-Tac's longest, on a phone
        for note, floor in ((notes[0], size - 1.5), (notes[-1], 6.5)):
            fits = size
            while fits > floor and beside(note, fits) > x1 - x0:
                fits -= .25
            if beside(note, fits) <= x1 - x0 or note is notes[-1]:
                size, full = fits, plate(fits)
                break
    top, y = y, y + (tall - full.h) / 2     # a plate set smaller stands in the middle of its row
    bx = x1 - full.w if right else x0
    n0 = len(cv.body)
    cv.add(full.draw_label(cv, bx, y, "turn"))
    if M.MOTION:
        paint, peak = sk.glint(cv, solid=not message)
        clip = cv.uid("b")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(bx)}" y="{f1(y)}" width="{f1(full.lw)}" '
                       f'height="{f1(full.h)}"/></clipPath>')
        cv.add(f'<g clip-path="url(#{clip})"><rect x="{f1(bx - 40)}" y="{f1(y - 4)}" width="30" '
               f'height="{f1(full.h + 8)}" fill="{paint}" opacity="0" transform="skewX(-20)">'
               + M.ani("x", f"{f1(bx - 40)};{f1(bx - 40)};{f1(bx + full.lw + 40)};{f1(bx + full.lw + 40)}",
                       "0;.82;.95;1", 8, begin=2.4, repeat=True)
               + M.ani("opacity", f"0;0;{peak};{peak};0", "0;.82;.83;.95;1", 8, begin=2.4, repeat=True)
               + "</rect></g>")
    added = "".join(cv.body[n0:])
    del cv.body[n0:]
    cv.add(M.rise(added, .25))
    if message:
        panel = full.draw_message(cv, bx + full.lw, y, message)
        cv.add(M.wiped(cv, panel, bx + full.lw, y, full.mw, full.h, 1.18, .42))
    # the note keeps clear of the badge across the row: said in full where there is room, else said short
    room = x1 - x0 - full.w - GAP
    least = 6.5 if keep_note else 7       # a note the plate gave way to is said in full down to its floor
    note = next((n for n in notes if sk.width(n.upper(), "caps", least, .6) <= room), notes[-1])
    note, size = fitting(sk, note, "caps", 7, 6, room, .6)
    cv.add(sk.caps(cv, note, x0 if right else x1, y + full.h / 2 + 3, size, ls=.6,
                   anchor="start" if right else "end", what="due"))
    return top + tall


def in_words(sk, st, room, *, small=False) -> tuple[int, float, list[str]]:
    """The last move in words, flowed to the panel's width (`flowed`); before the first move, who opens the game."""
    words = st["last"]["words"] if st["last"] else f"@{OWNER} opens game {st['game']}"
    return flowed(sk, words, room, small=small)


def flowed(sk, words: str, room: float, *, small=False) -> tuple[int, float, list[str]]:
    """A move's words flowed to the panel's width: on as many lines as the standard theme's letters take, two at
    most, so the panel stands the same in every theme; smaller only if it must be, and cut short only past that.
    Every game's panel says its last move so. (lines the layout gives it, size, lines)"""
    size, floor = (11, 9) if not small else (10.5, 8.5)
    rows = len(flow(lambda s, z: width(s, "sans", z), words, size, floor, room)[1])
    return (rows, *flow(lambda s, z: sk.width(s, "regular", z), words, size, floor, room, rows=rows, least=rows))


def last_move(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """The last move in notation, in words on a line or two of their own, and who played it when; before a game's
    first move, who opens it."""
    last = st["last"]
    big = 22 if not small else 18
    room = x1 - x0
    if last:
        shown = f"{last['number']}." if last["side"] == "white" else f"{last['number']}..."
        shown += f" {last['san']}"
    else:
        shown = "1. ?"
    cv.add(sk.key(cv, x0, y - 7, 7, "last"), sk.heading(cv, "last move" if last else "first move", x0 + 12, y))
    cv.add(sk.say(cv, cut(sk, shown, "bold", big, room), x0, y + 12 + big * .74, big, role="strong", what="move"))
    rows, size, lines = in_words(sk, st, room, small=small)
    top = y + 12 + big + (14 if not small else 13)
    for i, line in enumerate(lines):
        cv.add(sk.say(cv, line, x0, top + i * LEAD, size, face="regular", what="move in words"))
    # who played it, and when: the login cut short before the day is, if it comes to that
    yy = top + (rows - 1) * LEAD + (17 if not small else 15)
    if last:
        when = f"  ·  {last['when']}"
        by = f"by {last['by']}{when}"
        bs = fit(sk, by, "caps", 7.5, 6.5, room, .6)
        by = cut(sk, f"by {last['by']}", "caps", bs, room, .6, tail=when)
    else:
        by, bs = "white moves first", 7.5
    cv.add(sk.caps(cv, by, x0, yy, bs, ls=.6))
    return yy + (9 if not small else 10)


def taken(cv, sk, st, x0, x1, y, *, mini=20) -> float:
    """What each side has taken, on a tray of the board's light square, and the side ahead by the pieces' worth;
    a full tray's pieces stand a little closer, so the badge of the lead stays inside the panel."""
    cv.add(sk.heading(cv, "taken", x0, y))
    t = st["taken"]
    worth = {s: sum(VALUE[k] for k in t[s]) for s in t}
    lead = worth["white"] - worth["black"]
    yy = y + 10
    for side, label, pieces_of in (("white", "WHITE TOOK", "black"), ("black", "BLACK TOOK", "white")):
        cv.add(sk.caps(cv, label, x0, yy + mini / 2 + 3, 7.5, ls=.6, role="muted"))
        px = x0 + 72
        ahead = lead if side == "white" else -lead
        chip = sk.chip(f"+{ahead}", "", size=7.5, lab="accent") if ahead > 0 else None
        step = mini * .8
        if t[side]:
            step = min(step, (x1 - px - (chip.w + 10 if chip else 5)) / len(t[side]))
        sk.tray(cv, px - 4, yy - 1, len(t[side]) * step + 9, mini + 2)
        for kind in t[side]:
            cv.add(sk.put(cv, kind, pieces_of, px, yy, mini, sw=2.2, shadow=False))
            px += step
        if chip:
            cv.add(chip.draw(cv, px + 10, yy + (mini - chip.h) / 2, "material"))
        yy += mini + 7
    return yy


def rows_of(st) -> list:
    """The score sheet's rows, the move to come included: on a board before its first move, that one alone."""
    rows = list(st["history"])
    if not rows:
        rows = [(1, "", "", "", False)]
    return rows


def history(cv, sk, st, x0, x1, y, rows=3) -> float:
    """The last moves, who chose each of GitHub's, the latest move's row marked, and whose turn the next one is;
    once the game is over, who won it in that place. Each column stands where it always has, further right only for
    a number or a move too wide to leave it there."""
    cv.add(sk.heading(cv, "moves", x0, y))
    yy = y + 21
    turn = outcome(st) if st.get("result") else f"{turn_name(st)}'s turn"
    said = "ink" if st.get("result") else "alert"      # a result is said in the ink; a turn calls out in red
    latest = st["last"]["number"] if st["last"] else None
    shown = rows_of(st)[-rows:]
    wx = x0 + max(26, max(sk.width(f"{n}.", "caps", 8, .3) for n, *_ in shown) + 5)
    bx = wx + max(56, max(sk.width(w, "bold", 10) for _, w, *_ in shown) + 6)
    ox = bx + max(54, max(sk.width(b, "bold", 10) for _, _, b, *_ in shown) + 6)
    for n, w, b, who, safe in shown:
        if n == latest:
            cv.add(sk.row_mark(x0 - 6, yy - 12.5, x1 - x0 + 6, 18))
        cv.add(sk.caps(cv, f"{n}.", x0, yy, 8, ls=.3, what="move number"))
        if not w:
            cv.add(sk.caps(cv, turn, wx, yy, 7, ls=.5, role=said, what="to move"))
        else:
            cv.add(sk.say(cv, w, wx, yy, 10, what="white's move"))
            if b:
                cv.add(sk.say(cv, b, bx, yy, 10, what="black's move"))
                tx = ox
                if safe:
                    chip = sk.chip("safe play", "", icon="shield", size=6.5, lab="safe")
                    cv.add(chip.draw(cv, tx, yy - 3.7 - chip.h / 2, "safe play"))
                    tx += chip.w + 7
                    who = f"for {who}"
                if who:
                    who, size = fitting(sk, who, "caps", 7, 6, x1 - tx, .5)
                    cv.add(sk.caps(cv, who, tx, yy, size, ls=.5, what="mover"))
            else:
                cv.add(sk.caps(cv, turn, bx, yy, 7, ls=.5, role=said, what="to move"))
        yy += 19
    return yy


def board_sheet(sk, st: dict, title: str, desc: str, variant: str = "wide") -> str:
    still = "" if M.MOTION else " still"
    subject = f"game {st['game']}  ·  move {st['move']}"
    if variant == "wide":
        W, s = WIDE, 46
        x0, y0 = PAD + 18, BAND + 22
        H = y0 + 8 * s + 22 + PAD
        cv = sk.new(W, H, title, desc, "elements chessboard wide", still)
        sk.frame(cv, W, H, "chess", "pawn", subject, f"@{OWNER} vs. github", plain=[sk.board_room(x0, y0, s)])
        board(cv, sk, st, x0, y0, s)
        px0, px1 = x0 + 8 * s + 32, W - PAD
        cv.add(sk.vrule(px0 - 16, y0, y0 + 8 * s))
        y = M.risen(cv, .15, matchup, cv, sk, st, px0, px1, y0 + 1)
        y = turn_row(cv, sk, st, px0, px1, y + 14)
        cv.add(sk.rule(px0, px1, y + 16))
        y = M.risen(cv, .3, last_move, cv, sk, st, px0, px1, y + 36)
        cv.add(sk.rule(px0, px1, y - 4))
        y = M.risen(cv, .45, taken, cv, sk, st, px0, px1, y + 16)
        cv.add(sk.rule(px0, px1, y + 1))
        M.risen(cv, .6, history, cv, sk, st, px0, px1, y + 21)
        return cv.svg()
    W, s = NARROW, 37
    x0, y0 = PAD + 14, BAND + 18
    top = y0 + 8 * s + 30
    H = top + 340 + LEAD * (in_words(sk, st, W - 2 * PAD, small=True)[0] - 1)   # a line more for words that take two
    cv = sk.new(W, H, title, desc, "elements chessboard narrow", still)
    sk.frame(cv, W, H, "chess", "pawn", f"move {st['move']}", plain=[sk.board_room(x0, y0, s)])
    board(cv, sk, st, x0, y0, s)
    px0, px1 = PAD, W - PAD
    y = M.risen(cv, .15, matchup, cv, sk, st, px0, px1, top, small=True)
    y = turn_row(cv, sk, st, px0, px1, y + 12, small=True)
    cv.add(sk.rule(px0, px1, y + 14))
    y = M.risen(cv, .3, last_move, cv, sk, st, px0, px1, y + 34, small=True)
    cv.add(sk.rule(px0, px1, y - 2))
    y = M.risen(cv, .45, taken, cv, sk, st, px0, px1, y + 18, mini=18)
    cv.add(sk.rule(px0, px1, y + 1))
    M.risen(cv, .6, history, cv, sk, st, px0, px1, y + 21, rows=2)
    return cv.svg()


# --------------------------------------------------------------------------- the hall of fame
def scoreboard(cv, sk, h, x0, x1, y, *, small=False) -> float:
    """The series: the house's wins, GitHub's and the draws, each keyed to its share of the bar. Wide, three columns
    of a medallion, a number and its label; on a phone, three stacked and centred. Before any game has finished,
    the bar is an empty track."""
    total = h["games"]
    cols = (("house", f"@{OWNER.upper()}", "wins", "white"), ("world", "GITHUB", "wins", "black"),
            ("draws", "DRAWS", f"in {total} game{'s' if total != 1 else ''}" if total else "none yet", None))
    colw = (x1 - x0) / 3
    r = 15 if not small else 12
    n0 = len(cv.body)
    for i, (key, label, sub, side) in enumerate(cols):
        x = x0 + i * colw
        cx = x + r if not small else x + colw / 2
        cy = y + r
        cv.add(sk.medallion(cv, cx, cy, r, side) if side else sk.draws_disc(cv, cx, cy, r))
        n = str(h[key])
        if not small:
            tx = x + 2 * r + 10
            big = 20
            cv.add(sk.say(cv, n, tx, cy + big * .36, big, role="strong"))
            lx = tx + sk.width(n, "bold", big) + 8
            cv.add(sk.key(cv, lx, cy - 8.5, 7, key),
                   sk.caps(cv, label, lx + 11, cy - 1.5, 8, ls=.7, role="ink"),
                   sk.caps(cv, sub, lx + 11, cy + 10, 7, ls=.6))
        else:
            big = 16
            cv.add(sk.say(cv, n, cx, cy + r + 6 + big * .74, big, role="strong", anchor="middle"))
            lw = sk.width(label, "caps", 6.5, .65 * len(label) / max(len(label), 1))
            ly = cy + r + 6 + big + 10
            cv.add(sk.key(cv, cx - lw / 2 - 9, ly - 6, 6, key),
                   sk.caps(cv, label, cx + 4, ly, 6.5, ls=.5, role="ink", anchor="middle"),
                   sk.caps(cv, sub, cx, ly + 10, 6, ls=.5, anchor="middle"))
    added = "".join(cv.body[n0:])
    del cv.body[n0:]
    cv.add(M.rise(added, .1))
    by = y + 2 * r + 12 if not small else y + 2 * r + 6 + 16 + 30
    bx, bw = x0, x1 - x0
    if not total:
        cv.add(sk.track(cv, bx, by, bw, 6))
        return by + 6
    bars = []
    for key, *_ in cols:
        w = bw * h[key] / total
        if w:
            bars.append(sk.segment(cv, bx, by, max(w - 2, 1), 6, key))
        bx += w
    cv.add(M.wiped(cv, "".join(bars), x0, by - 1, bw, 8, .3, 1.1))
    return by + 6


def named(cv, sk, p, x, y, room, size, ls, hsize, hls, dy) -> None:
    """A winner's name, and their handle `dy` under it in small capitals, each fitted to `room`: a long one a little
    smaller, the name keeping its letter-spacing in proportion, and the longest cut short."""
    em = ls / size
    ns = sk.fitted(p["name"], size, 7.5, room, em)
    handle, hs = fitting(sk, p["handle"], "caps", hsize, hsize - 1, room, hls)
    cv.add(sk.say(cv, cut(sk, p["name"], "bold", ns, room, ns * em), x, y, ns, ls=ns * em),
           sk.caps(cv, handle, x, y + dy, hs, ls=hls))


def vacant(cv, sk, x, y, colw, i) -> None:
    """A podium's place nobody has taken yet: an empty medal, waiting."""
    cv.add(sk.vacant(cv, x + 28, y + 28, 22, i),
           sk.say(cv, "NOBODY YET", x + 66, y + 16, 10.5, role="muted", ls=.7),
           sk.caps(cv, "the next to win stands here" if i == 0 else "a place on the podium", x + 66, y + 30, 7.5,
                   ls=.6))


def podium(cv, sk, h, x0, x1, y) -> float:
    """The first three, each in a column: medal, name and handle, wins and a bar of them against the most anyone
    has. Every line of a column ends where its bar does, short of the rule to the next."""
    people = h["people"]
    most = max((p["wins"] for p in people), default=1)
    colw = (x1 - x0) / 3
    order = {2: .45, 1: .7, 0: 1.0}           # third, then second, then first
    for i in range(3):
        x = x0 + colw * i
        if i:
            cv.add(sk.vrule(x - 6, y - 4, y + 108))
        n0 = len(cv.body)
        if i >= len(people):
            vacant(cv, sk, x, y, colw, i)
            added = "".join(cv.body[n0:])
            del cv.body[n0:]
            cv.add(M.rise(added, order[i]))
            continue
        p = people[i]
        cv.add(sk.face(cv, x + 28, y + 28, 22, p, i, medal=i, glint=i == 0))
        rank = sk.chip(f"#{i + 1}", "", size=7.5, lab=f"medal{i + 1}")
        cv.add(rank.draw(cv, x + 28 - rank.w / 2, y + 58, "rank"))
        tx = x + 66
        room = colw - 74
        named(cv, sk, p, tx, y + 16, room, 10.5, .735, 7.5, .6, 14)
        num = str(p["wins"])
        cw = sk.width(num, "bold", 20)
        cv.add(sk.say(cv, num, tx, y + 58, 20, role="strong"),
               sk.caps(cv, "wins" if p["wins"] != 1 else "win", tx + cw + 5, y + 58, 7.5))
        games = f"{p['games']} game{'s' if p['games'] != 1 else ''}"
        games, gs = fitting(sk, f"last win {p['last']}  ·  {games}" if p["last"] else games, "caps", 7, 6, room,
                            .5)
        cv.add(sk.caps(cv, games, tx, y + 92, gs, ls=.5))
        added = "".join(cv.body[n0:])
        del cv.body[n0:]
        cv.add(M.rise(added, order[i]))
        cv.add(sk.track(cv, tx, y + 66, room, 6)
               + M.wiped(cv, sk.fill_bar(cv, tx, y + 66, bar(room, p["wins"], most), 6), tx, y + 65, room, 8,
                         order[i] + .25, .9))
    return y + 112


def bar(room, wins, most) -> float:
    """A winner's bar: their wins against the most anyone has, never past its track nor too short to see."""
    return min(room, max(3, room * wins / max(most, 1)))


def mentions(cv, sk, h, x0, x1, y, start=3) -> float:
    """The places after the podium, two to a row: the number, the name and handle, and the wins on a badge."""
    rest = h["people"][start:]
    colw = (x1 - x0) / 2
    for i, p in enumerate(rest):
        col, row = i % 2, i // 2
        x, yy = x0 + col * colw, y + row * 34
        cv.add(sk.number(cv, start + i + 1, x, yy, 18))
        chip = sk.chip("wins", str(p["wins"]), size=7.5, lab="label", msg="place")
        cx = x + colw - chip.w - 14
        named(cv, sk, p, x + 28, yy + 9, cx - GAP - x - 28, 9, .6, 7, .5, 12)
        cv.add(chip.draw(cv, cx, yy - 2, "wins"))
    return y + ((len(rest) + 1) // 2) * 34


def hall_sheet(sk, h: dict, title: str, desc: str, variant: str = "wide") -> str:
    still = "" if M.MOTION else " still"
    games = f"{h['games']} game{'s' if h['games'] != 1 else ''}" if h["games"] else "no games yet"
    rest = h["people"][3:]
    if variant == "wide":
        W = WIDE
        top = BAND + 26
        H = top + 52 + 30 + 112 + (18 + 34 * ((len(rest) + 1) // 2) if rest else -6) + PAD + 4
        cv = sk.new(W, H, title, desc, "elements chess hall wide", still)
        sk.frame(cv, W, H, "hall of fame", "trophy", games, f"@{OWNER} vs. github")
        y = scoreboard(cv, sk, h, PAD, W - PAD, top)
        cv.add(sk.rule(PAD, W - PAD, y + 16))
        y = podium(cv, sk, h, PAD, W - PAD, y + 34)
        if rest:
            cv.add(sk.rule(PAD, W - PAD, y + 4))
            M.risen(cv, 1.25, mentions, cv, sk, h, PAD, W - PAD, y + 20)
        return cv.svg()
    W = NARROW
    top = BAND + 22
    H = top + 86 + 24 + 3 * 62 + (10 + 34 * len(rest) if rest else -8) + PAD + 4
    cv = sk.new(W, H, title, desc, "elements chess hall narrow", still)
    sk.frame(cv, W, H, "hall of fame", "trophy", games)
    y = scoreboard(cv, sk, h, PAD, W - PAD, top, small=True)
    cv.add(sk.rule(PAD, W - PAD, y + 12))
    y += 28
    people = h["people"]
    most = max((p["wins"] for p in people), default=1)
    order = {2: .45, 1: .7, 0: 1.0}
    rows = {i: y + i * 62 for i in range(3)}
    for i in (2, 1, 0):
        yy = rows[i]
        if i:
            cv.add(sk.rule(PAD, W - PAD, yy - 8))
        n0 = len(cv.body)
        if i >= len(people):
            cv.add(sk.vacant(cv, PAD + 20, yy + 20, 15, i),
                   sk.say(cv, "NOBODY YET", PAD + 52, yy + 12, 9.5, role="muted", ls=.6),
                   sk.caps(cv, "the next to win stands here" if i == 0 else "a place on the podium", PAD + 52,
                           yy + 25, 7, ls=.5))
            added = "".join(cv.body[n0:])
            del cv.body[n0:]
            cv.add(M.rise(added, order[i]))
            continue
        p = people[i]
        cv.add(sk.face(cv, PAD + 20, yy + 20, 15, p, i, medal=i, glint=i == 0))
        tx = PAD + 52
        num = str(p["wins"])
        named(cv, sk, p, tx, yy + 12, W - PAD - 34 - sk.width(num, "bold", 17) - GAP - tx, 9.5, .6, 7, .5, 13)
        cv.add(sk.say(cv, num, W - PAD - 34, yy + 20, 17, role="strong", anchor="end"),
               sk.caps(cv, "wins" if p["wins"] != 1 else "win", W - PAD - 30, yy + 20, 7))
        added = "".join(cv.body[n0:])
        del cv.body[n0:]
        cv.add(M.rise(added, order[i]))
        room = W - PAD - tx
        cv.add(sk.track(cv, tx, yy + 33, room, 4)
               + M.wiped(cv, sk.fill_bar(cv, tx, yy + 33, bar(room, p["wins"], most), 4), tx, yy + 32, room, 6,
                         order[i] + .25, .9))
    y += 3 * 62
    if not rest:
        return cv.svg()
    cv.add(sk.rule(PAD, W - PAD, y - 8))

    def rest_rows():
        for i, p in enumerate(rest):
            yy = y + 6 + i * 34
            cv.add(sk.number(cv, 4 + i, PAD, yy, 18))
            chip = sk.chip("wins", str(p["wins"]), size=7.5, lab="label", msg="place")
            named(cv, sk, p, PAD + 28, yy + 9, W - PAD - chip.w - GAP - PAD - 28, 9, .6, 7, .5, 12)
            cv.add(chip.draw(cv, W - PAD - chip.w, yy - 2, "wins"))
    M.risen(cv, 1.25, rest_rows)
    return cv.svg()
