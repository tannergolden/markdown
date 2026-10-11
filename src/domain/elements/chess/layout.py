# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess sheets' one layout, which every theme draws: the board and its panel, and the Hall of Fame.

Every coordinate, size and beat of motion here is the standard theme's, and none of it changes with the theme: a
skin (see `skins`) is handed each part to draw at the place this module gives it and decides only what the part is
made of. So the board stands in the same place, the same size, beside the same panel, in the standard theme and in
every print, and a page that changes theme keeps its layout.

The motion plays once as the file opens, every animated attribute carrying its resting value so a file is complete
without it: the last move's piece comes in from its square, a knight leaping and anything else gliding, its square
is marked as it lands and a check blooms on the king; the panel rises into place a section at a time. On the Hall of
Fame the podium rises third, second, first, the bars fill, and a glint runs round the gold medal every seven
seconds. Drawn inside `motion.at_rest()`, the same sheets are the still files.
"""
from __future__ import annotations

from ...lettering import f1, fx
from . import motion as M
from .game import FILES, NAMES, OWNER, VALUE, turn_name
from .shapes import FOOT

WIDE, NARROW = 830, 360
BAND, PAD = 40, 20  # the head's depth and the sheet's margin, the standard theme's


def sq_xy(name: str, x0: float, y0: float, s: float) -> tuple[float, float]:
    f, r = FILES.index(name[0]), int(name[1])
    return x0 + f * s, y0 + (8 - r) * s


# --------------------------------------------------------------------------- the board
def board(cv, sk, g: dict, x0: float, y0: float, s: float) -> None:
    """The eight ranks with their pieces, the last move marked from and to, the checked king marked, and the
    coordinates round it. The piece that moved last comes in from its square as the file opens: a knight leaps,
    anything else glides; what it took fades as it lands."""
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
    pieces, mover = [], ""
    for name in sorted(placed, key=lambda q: (-int(q[1]), FILES.index(q[0]))):
        pc = placed[name]
        x, y = sq_xy(name, x0, y0, s)
        kind, side = NAMES[pc.lower()], "white" if pc.isupper() else "black"
        if last and name == last["to"] and M.MOTION:
            dx, dy = fx0 - x, fy0 - y
            mx, my = dx / 2, dy / 2 - s * (.62 if kind == "knight" else .12)
            t = f"0;.25;.48;{M.LAND};1"
            sx, sy, rx, ry = x + FOOT[0] * k, y + FOOT[1] * k, FOOT[2] * k, FOOT[3] * k
            shadow = (f'<g>{M.ani("transform", f"{f1(dx)} {f1(dy)};{f1(dx)} {f1(dy)};0 0;0 0", f"0;.25;{M.LAND};1", M.LEAP, spline="0 0 1 1;.35 0 .35 1;0 0 1 1", kind="animateTransform", typ="translate")}'
                      + sk.foot(cv, sx, sy, rx, ry,
                                M.ani("rx", f"{f1(rx)};{f1(rx)};{f1(rx * .5)};{f1(rx)};{f1(rx)}", t, M.LEAP)
                                + M.ani("opacity", "1;1;.35;1;1", t, M.LEAP))
                      + "</g>")
            pid = sk.piece_def(cv, kind, side, shadow=False)
            cx, cy = x + s / 2, y + s / 2
            if last.get("captured"):
                other = "black" if side == "white" else "white"
                gone = sk.piece_def(cv, last["captured"], other)
                shadow = (f'<use href="#{gone}" transform="translate({f1(x)} {f1(y)}) scale({fx(k, 4)})" opacity="0">'
                          + M.ani("opacity", "1;1;0;0", f"0;{M.LAND - .05};{M.LAND + .05};1", M.LEAP) + "</use>"
                          + shadow)
            mover = (shadow
                     + f'<g>{M.ani("transform", f"{f1(dx)} {f1(dy)};{f1(dx)} {f1(dy)};{f1(mx)} {f1(my)};0 0;0 0", t, M.LEAP, spline="0 0 1 1;.3 0 .6 1;.4 0 .25 1;0 0 1 1", kind="animateTransform", typ="translate")}'
                     f'<g transform="translate({f1(cx)} {f1(cy)})"><g>'
                     + M.ani("transform", "1;1;1.16;1;1" if kind == "knight" else "1;1;1.07;1;1", t, M.LEAP,
                             spline="0 0 1 1;.3 0 .6 1;.4 0 .25 1;0 0 1 1",
                             kind="animateTransform", typ="scale")
                     + f'<use href="#{pid}" transform="translate({f1(-s / 2)} {f1(-s / 2)}) scale({fx(k, 4)})"/>'
                     + "</g></g></g>")
            continue
        pieces.append(sk.put(cv, kind, side, x, y, s))
    cv.add("".join(pieces) + mover)
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
        if st["to_move"] == side:
            cv.add(sk.turn_ring(cv, cx, cy, r + 3.4, 1.1))
        tx = cx + r + 11 if left else cx - r - 11
        anchor = "start" if left else "end"
        cv.add(sk.say(cv, name, tx, cy - 2, 10 if not small else 9.5, ls=.8, anchor=anchor, what="player"),
               sk.caps(cv, sub, tx, cy + 11, 7, ls=.55, anchor=anchor, what="player role"))
    if not small:   # a phone's row has no room between the names for it: the two sides stand apart without it
        cv.add(sk.caps(cv, "vs", (x0 + x1) / 2, cy + 3, 8, ls=1, anchor="middle", what="versus"))
    return y + 2 * r + 3


def turn_row(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """Whose turn it is, a badge under that side, and the day the move is due by on the other. In check, the
    badge's second panel slides open out of it as the move lands; every eight seconds a glint crosses it, the
    call to play."""
    size = 10 if not small else 8.5
    label = f"{turn_name(st)}'s turn"
    full = (sk.chip(label, "in check", icon="play", size=size, lab="turn", msg="alert") if st["check"]
            else sk.chip(label, "", icon="play", size=size, lab="turn"))
    right = st["to_move"] == "black"
    bx = x1 - full.w if right else x0
    n0 = len(cv.body)
    cv.add(full.draw_label(cv, bx, y, "turn"))
    if M.MOTION:
        paint, peak = sk.glint(cv, solid=not st["check"])
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
    if st["check"]:
        panel = full.draw_message(cv, bx + full.lw, y, "in check")
        cv.add(M.wiped(cv, panel, bx + full.lw, y, full.mw, full.h, 1.18, .42))
    note = f"due by {st['due']}" if st["due"] else "no clock until the first move"
    cv.add(sk.caps(cv, note, x0 if right else x1, y + full.h / 2 + 3, 7, ls=.6,
                   anchor="start" if right else "end", what="due"))
    return y + full.h


def last_move(cv, sk, st, x0, y, *, small=False) -> float:
    """The last move in notation, in words, and who played it when; before a game's first move, who opens it."""
    last = st["last"]
    big = 22 if not small else 18
    if last:
        shown = f"{last['number']}." if last["side"] == "white" else f"{last['number']}..."
        shown += f" {last['san']}"
        words, by = last["words"], f"by {last['by']}  ·  {last['when']}"
    else:
        shown, words, by = "1. ?", f"@{OWNER} opens game {st['game']}", "white moves first"
    cv.add(sk.key(cv, x0, y - 7, 7, "last"), sk.heading(cv, "last move" if last else "first move", x0 + 12, y))
    sw = sk.width(shown, "bold", big)
    cv.add(sk.say(cv, shown, x0, y + 12 + big * .74, big, role="strong", what="move"))
    if small:
        cv.add(sk.say(cv, words, x0 + sw + 10, y + 12 + big * .74, 10.5, face="regular", what="move in words"))
        cv.add(sk.caps(cv, by, x0, y + 12 + big + 12, 7.5, ls=.6))
        return y + 12 + big + 22
    cv.add(sk.say(cv, words, x0, y + 12 + big + 14, 11, face="regular", what="move in words"))
    cv.add(sk.caps(cv, by, x0, y + 12 + big + 31, 7.5, ls=.6))
    return y + 12 + big + 40


def taken(cv, sk, st, x0, x1, y, *, mini=20) -> float:
    cv.add(sk.heading(cv, "taken", x0, y))
    t = st["taken"]
    worth = {s: sum(VALUE[k] for k in t[s]) for s in t}
    lead = worth["white"] - worth["black"]
    yy = y + 10
    for side, label, pieces_of in (("white", "WHITE TOOK", "black"), ("black", "BLACK TOOK", "white")):
        cv.add(sk.caps(cv, label, x0, yy + mini / 2 + 3, 7.5, ls=.6, role="muted"))
        px = x0 + 72
        sk.tray(cv, px - 4, yy - 1, len(t[side]) * mini * .8 + 9, mini + 2)
        for kind in t[side]:
            cv.add(sk.put(cv, kind, pieces_of, px, yy, mini, sw=2.2, shadow=False))
            px += mini * .8
        ahead = lead if side == "white" else -lead
        if ahead > 0:
            chip = sk.chip(f"+{ahead}", "", size=7.5, lab="accent")
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
    """The last moves, who chose each of GitHub's, the latest move's row marked, and whose turn the next one is."""
    cv.add(sk.heading(cv, "moves", x0, y))
    yy = y + 21
    turn = f"{turn_name(st)}'s turn"
    latest = st["last"]["number"] if st["last"] else None
    for n, w, b, who, safe in rows_of(st)[-rows:]:
        if n == latest:
            cv.add(sk.row_mark(x0 - 6, yy - 12.5, x1 - x0 + 6, 18))
        cv.add(sk.caps(cv, f"{n}.", x0, yy, 8, ls=.3, what="move number"))
        if not w:
            cv.add(sk.caps(cv, turn, x0 + 26, yy, 7, ls=.5, role="alert", what="to move"))
        else:
            cv.add(sk.say(cv, w, x0 + 26, yy, 10, what="white's move"))
            if b:
                cv.add(sk.say(cv, b, x0 + 82, yy, 10, what="black's move"))
                tx = x0 + 136
                if safe:
                    chip = sk.chip("safe play", "", icon="shield", size=6.5, lab="safe")
                    cv.add(chip.draw(cv, tx, yy - 3.7 - chip.h / 2, "safe play"))
                    tx += chip.w + 7
                    who = f"for {who}"
                if who:
                    cv.add(sk.caps(cv, who, tx, yy, 7, ls=.5, what="mover"))
            else:
                cv.add(sk.caps(cv, turn, x0 + 82, yy, 7, ls=.5, role="alert", what="to move"))
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
        y = M.risen(cv, .3, last_move, cv, sk, st, px0, y + 36)
        cv.add(sk.rule(px0, px1, y - 4))
        y = M.risen(cv, .45, taken, cv, sk, st, px0, px1, y + 16)
        cv.add(sk.rule(px0, px1, y + 1))
        M.risen(cv, .6, history, cv, sk, st, px0, px1, y + 21)
        return cv.svg()
    W, s = NARROW, 37
    x0, y0 = PAD + 14, BAND + 18
    top = y0 + 8 * s + 30
    H = top + 324
    cv = sk.new(W, H, title, desc, "elements chessboard narrow", still)
    sk.frame(cv, W, H, "chess", "pawn", f"move {st['move']}", plain=[sk.board_room(x0, y0, s)])
    board(cv, sk, st, x0, y0, s)
    px0, px1 = PAD, W - PAD
    y = M.risen(cv, .15, matchup, cv, sk, st, px0, px1, top, small=True)
    y = turn_row(cv, sk, st, px0, px1, y + 12, small=True)
    cv.add(sk.rule(px0, px1, y + 14))
    y = M.risen(cv, .3, last_move, cv, sk, st, px0, y + 34, small=True)
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


def vacant(cv, sk, x, y, colw, i) -> None:
    """A podium's place nobody has taken yet: an empty medal, waiting."""
    cv.add(sk.vacant(cv, x + 28, y + 28, 22, i),
           sk.say(cv, "NOBODY YET", x + 66, y + 16, 10.5, role="muted", ls=.7),
           sk.caps(cv, "the next to win stands here" if i == 0 else "a place on the podium", x + 66, y + 30, 7.5,
                   ls=.6))


def podium(cv, sk, h, x0, x1, y) -> float:
    people = h["people"]
    most = people[0]["wins"] if people else 1
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
        ns = sk.fitted(p["name"], 10.5, 7.5, room, .07)
        cv.add(sk.say(cv, p["name"], tx, y + 16, ns, ls=ns * .07), sk.caps(cv, p["handle"], tx, y + 30, 7.5, ls=.6))
        num = str(p["wins"])
        cw = sk.width(num, "bold", 20)
        cv.add(sk.say(cv, num, tx, y + 58, 20, role="strong"),
               sk.caps(cv, "wins" if p["wins"] != 1 else "win", tx + cw + 5, y + 58, 7.5))
        games = f"{p['games']} game{'s' if p['games'] != 1 else ''}"
        cv.add(sk.caps(cv, f"last win {p['last']}  ·  {games}" if p["last"] else games, tx, y + 92, 7, ls=.5))
        added = "".join(cv.body[n0:])
        del cv.body[n0:]
        cv.add(M.rise(added, order[i]))
        cv.add(sk.track(cv, tx, y + 66, room, 6)
               + M.wiped(cv, sk.fill_bar(cv, tx, y + 66, max(3, room * p["wins"] / most), 6), tx, y + 65, room, 8,
                         order[i] + .25, .9))
    return y + 112


def mentions(cv, sk, h, x0, x1, y, start=3) -> float:
    rest = h["people"][start:]
    colw = (x1 - x0) / 2
    for i, p in enumerate(rest):
        col, row = i % 2, i // 2
        x, yy = x0 + col * colw, y + row * 34
        cv.add(sk.number(cv, start + i + 1, x, yy, 18))
        cv.add(sk.say(cv, p["name"], x + 28, yy + 9, 9, ls=.6), sk.caps(cv, p["handle"], x + 28, yy + 21, 7, ls=.5))
        chip = sk.chip("wins", str(p["wins"]), size=7.5, lab="label", msg="count")
        cv.add(chip.draw(cv, x + colw - chip.w - 14, yy - 2, "wins"))
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
    most = people[0]["wins"] if people else 1
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
        cv.add(sk.say(cv, p["name"], tx, yy + 12, 9.5, ls=.6), sk.caps(cv, p["handle"], tx, yy + 25, 7, ls=.5))
        num = str(p["wins"])
        cv.add(sk.say(cv, num, W - PAD - 34, yy + 20, 17, role="strong", anchor="end"),
               sk.caps(cv, "wins" if p["wins"] != 1 else "win", W - PAD - 30, yy + 20, 7))
        added = "".join(cv.body[n0:])
        del cv.body[n0:]
        cv.add(M.rise(added, order[i]))
        room = W - PAD - tx
        cv.add(sk.track(cv, tx, yy + 33, room, 4)
               + M.wiped(cv, sk.fill_bar(cv, tx, yy + 33, max(3, room * p["wins"] / most), 4), tx, yy + 32, room, 6,
                         order[i] + .25, .9))
    y += 3 * 62
    if not rest:
        return cv.svg()
    cv.add(sk.rule(PAD, W - PAD, y - 8))

    def rest_rows():
        for i, p in enumerate(rest):
            yy = y + 6 + i * 34
            cv.add(sk.number(cv, 4 + i, PAD, yy, 18))
            cv.add(sk.say(cv, p["name"], PAD + 28, yy + 9, 9, ls=.6), sk.caps(cv, p["handle"], PAD + 28, yy + 21, 7,
                                                                              ls=.5))
            chip = sk.chip("wins", str(p["wins"]), size=7.5, lab="label", msg="count")
            cv.add(chip.draw(cv, W - PAD - chip.w, yy - 2, "wins"))
    M.risen(cv, 1.25, rest_rows)
    return cv.svg()
