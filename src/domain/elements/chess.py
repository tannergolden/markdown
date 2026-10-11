# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess element: the game on @tannergolden's profile, drawn as a sheet of the page's print.

The board is a drawing like any other on the paper: files and ranks lettered
along it as a drawing letters its dimensions, the dark squares lined as a
draughtsman shows solid material, and the last move marked at both of its
squares and drawn between them. Beside it, on a wide sheet, stand whose turn
it is, the last move, the score sheet and the Hall of Fame; a phone's sheet
keeps the first two under the board.

The pieces are six silhouettes of this kit's own, on one shared plinth, in a
box of 100 units. A print has two colours, its paper and its line, and the
dark theme swaps which is the lighter, so a piece takes its fill by
lightness: White's are always the lighter of the two and Black's the darker,
whatever the theme. Each piece is drawn once in the file's defs and placed
on its square with `<use>`.

The game itself is played elsewhere, by the profile's own workflow, which
writes what this draws into the page's settings after every move. Nothing
here knows the rules: the position arrives as FEN, the moves as notation.
"""
from __future__ import annotations

import re

from ..canvas import c
from ..drafting import hair, sheet
from ..lettering import cap_height, f1, fit, fx, width
from .draw import _open, caption, geometry, new, plate, say, title

# The one page the game is drawn on: it is @tannergolden's own, played from that profile and nowhere else.
OWNER = "tannergolden"
FILES = "abcdefgh"
NAMES = {"p": "pawn", "n": "knight", "b": "bishop", "r": "rook", "q": "queen", "k": "king"}
FEN = re.compile(r"(?:[pnbrqkPNBRQK1-8]{1,8}/){7}[pnbrqkPNBRQK1-8]{1,8} [wb] (?:-|[KQkq]{1,4}) (?:-|[a-h][36]) \d+ \d+")
SQUARE = re.compile(r"[a-h][1-8]")
UCI = re.compile(r"[a-h][1-8][a-h][1-8][qrbn]?")
SAN = re.compile(r"(?:O-O(?:-O)?|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?)[+#]?")
# A move's link opens a ready-made issue on GitHub, and nothing else: no space, no bracket, no quote.
LINK = re.compile(r"https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/issues/new\?[A-Za-z0-9._~%&=+-]+")
LINE = re.compile(r"[^<>|\n\r]{1,400}")
WORDS = {"king": "King", "queen": "Queen", "rook": "Rook", "bishop": "Bishop", "knight": "Knight", "pawn": "Pawn"}

# The plinth every piece stands on, then each piece's body, and the detail cut into it.
PLINTH = "M20 90V86Q20 82 24 82H76Q80 82 80 86V90ZM27 82V78Q27 76 29 76H71Q73 76 73 78V82Z"
PIECES = {
    "p": ("M33 76C36 66 43 60 44 52H56C57 60 64 66 67 76Z"
          "M36 49.5Q36 45 40 45H60Q64 45 64 49.5Q64 53 60 53H40Q36 53 36 49.5Z"
          "M62 33A12 12 0 1 1 38 33A12 12 0 1 1 62 33Z", ""),
    "r": ("M35 76L38 46H62L65 76Z"
          "M33 46V42Q33 40 35 40H65Q67 40 67 42V46Z"
          "M30 40V19H38V26H45V19H55V26H62V19H70V40Z", "M31 33H69"),
    "b": ("M37 76C40 68 44 62 45 58H55C56 62 60 68 63 76Z"
          "M37 55Q37 52 40 52H60Q63 52 63 55Q63 58 60 58H40Q37 58 37 55Z"
          "M50 17C61 25 66 35 62 45Q58 52 50 52Q42 52 38 45C34 35 39 25 50 17Z"
          "M54.5 12.5A4.5 4.5 0 1 1 45.5 12.5A4.5 4.5 0 1 1 54.5 12.5Z", "M45 28L57 40"),
    "n": ("M30 76C30 66 33 60 38 56C33 56 27 54 24 50C20 46 19 41 22 38L35 22C36 18 39 15 43 14L45 7L50 14"
          "C62 16 71 28 72 44C73 56 70 66 70 76Z",
          "M53 18C62 24 66 36 66 52M23 44.5L29 45"),
    "q": ("M36 76C40 66 44 58 45 52H55C56 58 60 66 64 76Z"
          "M35 49Q35 46 38 46H62Q65 46 65 49Q65 52 62 52H38Q35 52 35 49Z"
          "M33 46L28 22L37.5 33L39 16L45 31L50 12L55 31L61 16L62.5 33L72 22L67 46Z"
          "M31.6 20A3.6 3.6 0 1 1 24.4 20A3.6 3.6 0 1 1 31.6 20Z"
          "M42.6 14A3.6 3.6 0 1 1 35.4 14A3.6 3.6 0 1 1 42.6 14Z"
          "M53.6 10A3.6 3.6 0 1 1 46.4 10A3.6 3.6 0 1 1 53.6 10Z"
          "M64.6 14A3.6 3.6 0 1 1 57.4 14A3.6 3.6 0 1 1 64.6 14Z"
          "M75.6 20A3.6 3.6 0 1 1 68.4 20A3.6 3.6 0 1 1 75.6 20Z", "M32 40H68"),
    "k": ("M35 76C39 66 43 58 44 52H56C57 58 61 66 65 76Z"
          "M34 49Q34 46 37 46H63Q66 46 66 49Q66 52 63 52H37Q34 52 34 49Z"
          "M35 46L31 30Q50 22 69 30L65 46Z"
          "M47.5 26V16H42V11H47.5V5H52.5V11H58V16H52.5V26Z", "M33 38H67"),
}
EYE = (38, 27, 2.2)  # the knight's eye, a dot of the detail colour


class ChessError(ValueError):
    pass


def placement(fen: str) -> dict[str, str]:
    """The pieces by square, from the FEN's first field: {"e1": "K", "e8": "k", ...}."""
    board = {}
    for row, text in enumerate(fen.split()[0].split("/")):
        f = 0
        for ch in text:
            if ch.isdigit():
                f += int(ch)
            else:
                board[f"{FILES[f]}{8 - row}"] = ch
                f += 1
    return board


def check(d: dict) -> list[str]:
    """What the element's data gets wrong, said precisely."""
    errors = []
    fen = str(d.get("fen", ""))
    if not FEN.fullmatch(fen):
        errors.append(f"fen {fen!r} is not a position in FEN")
    else:
        pieces = placement(fen)
        if list(pieces.values()).count("K") != 1 or list(pieces.values()).count("k") != 1:
            errors.append("fen does not have one king a side")
    if d.get("last") and not UCI.fullmatch(str(d["last"])):
        errors.append(f"last {d['last']!r} is not a move in UCI, such as e2e4")
    if d.get("check") and not SQUARE.fullmatch(str(d["check"])):
        errors.append(f"check {d['check']!r} is not a square, such as e8")
    for key in ("prompt", "note"):
        if d.get(key) and not LINE.fullmatch(str(d[key])):
            errors.append(f"{key} is one line of text, without <, > or |")
    moves = d.get("moves") or []
    if not isinstance(moves, list):
        return errors + ["moves is a list of each piece and its links"]
    for group in moves:
        if not isinstance(group, dict) or group.get("piece") not in WORDS or not isinstance(group.get("links"), list):
            errors.append(f"moves: {group!r} is not a piece ({', '.join(WORDS)}) with a list of links")
            continue
        for pair in group["links"]:
            if not (isinstance(pair, list) and len(pair) == 2 and SAN.fullmatch(str(pair[0]))
                    and LINK.fullmatch(str(pair[1]))):
                errors.append(f"moves: {pair!r} is not a move in SAN and the link to its ready-made issue")
    return errors


def text(d: dict) -> str:
    """What the README carries under the board: the prompt, every legal move as a link, a piece a row, the note.

    An image cannot be clicked square by square, so the moves are links in the page itself."""
    parts = [str(d["prompt"])] if d.get("prompt") else []
    rows = [f"| {WORDS[group['piece']]} | " + " \u00b7 ".join(f"[{san}]({url})" for san, url in group["links"]) + " |"
            for group in d.get("moves") or [] if group["links"]]
    if rows:
        parts.append("\n".join(["| Piece | Moves |", "| :---- | :---- |", *rows]))
    if d.get("note"):
        parts.append(str(d["note"]))
    return "\n\n".join(parts)


START = {"p": 8, "n": 2, "b": 2, "r": 2, "q": 1}


def captured(fen: str) -> tuple[str, str]:
    """The pieces each side has taken, worth most first: Black's lost to White, then White's lost to Black.

    Counted against the opening set, so a promotion reads as the pawn taken."""
    on = list(placement(fen).values())
    lost = {colour: "".join(kind * max(0, START[kind] - on.count(kind if colour == "b" else kind.upper()))
                            for kind in "qrbnp") for colour in "wb"}
    return lost["b"], lost["w"].upper()


def sides(d: dict) -> tuple[str, str]:
    return str(d.get("white") or "White"), str(d.get("black") or "Black")


def turn(d: dict) -> str:
    """`w` or `b`, from the FEN."""
    return str(d["fen"]).split()[1]


def mover(d: dict) -> str:
    white, black = sides(d)
    return white if turn(d) == "w" else black


def describe(d: dict) -> dict:
    """The sheet's title and description, from the game, when the data gives none."""
    d = dict(d)
    white, black = sides(d)
    d.setdefault("title", f"Chess: {white} vs. {black}")
    where = f"Game {d['game']}, move {d['move']}. " if d.get("game") and d.get("move") else ""
    last = f" The last move was {d['last_san']}." if d.get("last_san") else ""
    d.setdefault("desc", f"{where}{'White' if turn(d) == 'w' else 'Black'} to move: {mover(d)}.{last}")
    return d


# --- the pieces ---------------------------------------------------------------------------------

def tones(col: dict) -> tuple[str, str]:
    """The lighter and the darker of the print's two colours in this theme."""
    return (c(col["line"]), c(col["paper"])) if col["dark"] else (c(col["paper"]), c(col["line"]))


def define(cv, col, piece: str, s: float, ids: dict) -> str:
    """One piece, drawn into the defs the first time a board places it, at a square of `s`; returns its id."""
    if piece in ids:
        return ids[piece]
    light, deep = tones(col)
    line = c(col["line"])
    fill = light if piece.isupper() else deep
    cut = c(col["paper"]) if fill == line else line
    body, detail = PIECES[piece.lower()]
    pid = cv.uid("pc")
    k = s / 100
    g = (f'<g id="{pid}" transform="scale({fx(k, 4)})"><path d="{PLINTH}{body}" fill="{fill}" stroke="{line}" '
         f'stroke-width="3" stroke-linejoin="round"/>')
    if detail:
        g += f'<path d="{detail}" fill="none" stroke="{cut}" stroke-width="2.4" stroke-linecap="round"/>'
    if piece.lower() == "n":
        g += f'<circle cx="{EYE[0]}" cy="{EYE[1]}" r="{EYE[2]}" fill="{cut}"/>'
    cv.defs.append(g + "</g>")
    ids[piece] = pid
    return pid


# --- the board ----------------------------------------------------------------------------------

def board(cv, col, d: dict, *, x0: float, y0: float, s: float) -> None:
    """The board with its pieces, lettered along its foot and its left, the last move and any check marked."""
    line, dark = c(col["line"]), col["dark"]
    side = 8 * s

    def at(sq: str) -> tuple[float, float]:
        return x0 + FILES.index(sq[0]) * s, y0 + (8 - int(sq[1])) * s

    if dark:  # by night the light squares carry a wash, so the lined ones stay the darker
        cv.add(f'<rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(side)}" height="{f1(side)}" fill="{line}" fill-opacity=".08"/>')
    lined = cv.uid("h")
    cv.defs.append(f'<pattern id="{lined}" width="4.5" height="4.5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                   f'<path d="M0 0V4.5" stroke="{line}" stroke-width="1" stroke-opacity="{".3" if dark else ".5"}"/></pattern>')
    squares = "".join(f"M{f1(x0 + f * s)} {f1(y0 + r * s)}h{f1(s)}v{f1(s)}h{f1(-s)}z"
                      for r in range(8) for f in range(8) if (r + f) % 2)
    cv.add(f'<path d="{squares}" fill="{c(col["paper"])}"/>'
           + ("" if dark else f'<path d="{squares}" fill="{line}" fill-opacity=".07"/>')
           + f'<path d="{squares}" fill="url(#{lined})"/>')

    last = str(d.get("last") or "")
    if last:
        (fx0, fy0), (tx0, ty0) = at(last[0:2]), at(last[2:4])
        tick = s * .22
        for (x, y), dash in (((fx0, fy0), ' stroke-dasharray="2.4 2.2"'), ((tx0, ty0), "")):
            i = s * .07
            a, b, e = x + i, y + i, s - 2 * i
            corners = (f"M{f1(a)} {f1(b + tick)}V{f1(b)}H{f1(a + tick)}M{f1(a + e - tick)} {f1(b)}H{f1(a + e)}V{f1(b + tick)}"
                       f"M{f1(a + e)} {f1(b + e - tick)}V{f1(b + e)}H{f1(a + e - tick)}M{f1(a + tick)} {f1(b + e)}H{f1(a)}"
                       f"V{f1(b + e - tick)}")
            cv.add(f'<path d="{corners}" fill="none" {hair(col, .95)} stroke-width="1.6"{dash}/>')
        cx0, cy0, cx1, cy1 = fx0 + s / 2, fy0 + s / 2, tx0 + s / 2, ty0 + s / 2
        cv.add(f'<path d="M{f1(cx0)} {f1(cy0)}L{f1(cx1)} {f1(cy1)}" fill="none" {hair(col, .5)} stroke-width="1.2" '
               f'stroke-dasharray="1.6 2.6"/>')

    ids: dict[str, str] = {}
    for sq, piece in sorted(placement(str(d["fen"])).items()):
        x, y = at(sq)
        cv.add(f'<use href="#{define(cv, col, piece, s, ids)}" x="{f1(x)}" y="{f1(y)}"/>')

    if d.get("check"):
        x, y = at(str(d["check"]))
        cv.add(f'<circle cx="{f1(x + s / 2)}" cy="{f1(y + s / 2)}" r="{f1(s * .47)}" fill="none" {hair(col, .95)} '
               f'stroke-width="1.6"/><circle cx="{f1(x + s / 2)}" cy="{f1(y + s / 2)}" r="{f1(s * .47 + 3)}" fill="none" '
               f'{hair(col, .45)} stroke-width=".8"/>')

    cv.add(f'<rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(side)}" height="{f1(side)}" fill="none" {hair(col, .95)} '
           f'stroke-width="1.6"/><rect x="{f1(x0 - 4)}" y="{f1(y0 - 4)}" width="{f1(side + 8)}" height="{f1(side + 8)}" '
           f'fill="none" {hair(col, .55)} stroke-width=".8"/>')
    size = 8.5 if s >= 40 else 7.5
    for i in range(8):
        say(cv, FILES[i], x=x0 + i * s + s / 2, y=y0 + side + 8 + cap_height("meta", size) + 3, col=col, size=size,
            anchor="middle", op=.7)
        say(cv, str(8 - i), x=x0 - 13, y=y0 + i * s + s / 2 + cap_height("meta", size) / 2, col=col, size=size,
            anchor="middle", op=.7)


# --- the panel ----------------------------------------------------------------------------------

def _rule(cv, col, x0: float, x1: float, y: float) -> None:
    cv.add(_open(col, f"M{f1(x0)} {f1(y)}H{f1(x1)}", .55, ' stroke-width=".8"'))


def to_move(cv, col, d: dict, *, x: float, right: float, y: float, big: float = 24) -> float:
    """Whose turn: the side's plate, the player's name, and the note under it. Returns the last baseline."""
    caption(cv, col, "TO MOVE", x=x, y=y)
    colour = "WHITE" if turn(d) == "w" else "BLACK"
    plate(cv, col, colour, right - width(colour, "num", 8.5, 1.3) - 12, y - 11, h=15, size=8.5, pad=6)
    name = mover(d)
    size = fit(name, "num", right - x, big, 12, 1.2)
    say(cv, name, x=x, y=y + 10 + cap_height("num", size), col=col, size=size, face="num", ls=1.2)
    base = y + 10 + cap_height("num", size)
    note = str(d.get("turn_note") or "")
    if d.get("check"):
        note = "IN CHECK" + (f"  ·  {note}" if note else "")
    if note:
        caption(cv, col, note.upper(), x=x, y=base + 16)
        base += 16
    return base


def last_move(cv, col, d: dict, *, x: float, right: float, y: float, big: float = 20) -> float:
    caption(cv, col, "LAST MOVE", x=x, y=y)
    san = str(d.get("last_san") or "")
    if not san:
        say(cv, "THE GAME OPENS", x=x, y=y + 10 + cap_height("num", 14), col=col, size=14, face="num", ls=1.2, op=.8)
        return y + 10 + cap_height("num", 14)
    size = fit(san, "num", right - x - 120, big, 12, 1.2)
    base = y + 10 + cap_height("num", size)
    say(cv, san, x=x, y=base, col=col, size=size, face="num", ls=1.2)
    by = str(d.get("last_by") or "")
    if by:
        say(cv, by.upper(), x=right, y=base, col=col, size=8, anchor="end", ls=1.2, op=.72)
    return base


def taken(cv, col, d: dict, *, x: float, right: float, y: float) -> float:
    """The pieces each side has taken, a row each, small, White's takings first."""
    caption(cv, col, "CAPTURED", x=x, y=y)
    by_white, by_black = captured(str(d["fen"]))
    ids: dict[str, str] = {}
    size, step = 20, 15
    white, black = sides(d)
    names = [who.upper() for who in (white, black)]
    room = min(max(width(n, "meta", 7.5, 1.2) for n in names) + 16, (right - x) / 3)
    for i, (who, pieces) in enumerate(zip(names, (by_white, by_black))):
        top = y + 8 + i * 22
        say(cv, who, x=x, y=top + 14, col=col, size=fit(who, "meta", room - 16, 7.5, 6, 1.2), ls=1.2, op=.6)
        if not pieces:
            say(cv, "NONE YET", x=x + room, y=top + 14, col=col, size=8, ls=1.2, op=.5)
        for j, piece in enumerate(pieces):
            cv.add(f'<use href="#{define(cv, col, piece, size, ids)}" x="{f1(x + room + j * step - 3)}" y="{f1(top)}"/>')
    return y + 8 + 22 + size


def score_sheet(cv, col, d: dict, *, x: float, right: float, y: float, rows: int) -> float:
    """The last moves as a score sheet writes them, a numbered row for each, White's then Black's."""
    caption(cv, col, "SCORE SHEET", x=x, y=y)
    history = [list(row) for row in d.get("history") or []][-rows:]
    if not history:
        say(cv, "NO MOVES YET", x=x, y=y + 22, col=col, size=9, ls=1.2, op=.6)
        return y + 22
    base = y
    for i, row in enumerate(history):
        base = y + 22 + i * 17
        number, white = str(row[0]), str(row[1] if len(row) > 1 else "")
        black = str(row[2] if len(row) > 2 else "")
        say(cv, f"{number}.", x=x + 22, y=base, col=col, size=10, face="mono", anchor="end", op=.6)
        say(cv, white, x=x + 34, y=base, col=col, size=10.5, face="mono")
        if black:
            say(cv, black, x=x + 124, y=base, col=col, size=10.5, face="mono")
    return base


def hall(cv, col, d: dict, *, x: float, right: float, y: float, rows: int) -> float:
    """The latest finished games: number, result, who decided it and how."""
    caption(cv, col, "HALL OF FAME", x=x, y=y)
    games = [list(row) for row in d.get("hall") or []][-rows:]
    if not games:
        say(cv, "NO GAME FINISHED YET", x=x, y=y + 22, col=col, size=9, ls=1.2, op=.6)
        return y + 22
    base = y
    for i, row in enumerate(reversed(games)):
        base = y + 22 + i * 17
        number, result, who, move = (str(v) for v in (row + ["", "", "", ""])[:4])
        say(cv, f"GAME {number}", x=x, y=base, col=col, size=9, ls=1.2)
        say(cv, result, x=x + 78, y=base, col=col, size=10.5, face="mono")
        say(cv, who.upper(), x=x + 134, y=base, col=col, size=9, ls=1.2)
        if move:
            say(cv, move, x=right, y=base, col=col, size=10.5, face="mono", anchor="end", op=.8)
    return base


# --- the sheet ----------------------------------------------------------------------------------

def draw(d: dict, tone: str, th: dict, variant: str = "wide") -> str:
    """The whole sheet: the board, and beside it on a wide sheet, or under it on a phone's, the game's state."""
    d = describe(d)
    g = geometry(variant)
    W, B, narrow = g["W"], g["B"], g["narrow"]
    white, black = sides(d)
    subject = f"{white} vs. {black}"
    right = "  ·  ".join(p for p in (f"GAME {d['game']}" if d.get("game") else "",
                                           f"MOVE {d['move']}" if d.get("move") else "") if p)
    if narrow:
        s = 36
        H = 72 + 8 * s + 34 + 140
        cv, col = new("chess", variant, th, tone, W, H, d["title"], d["desc"])
        x0 = (W - 8 * s) / 2 + 7
        sheet(cv, col, W=W, H=H, border=B, zones=g["zones"], plain=((x0, 72, 8 * s, 8 * s),))
        title(cv, col, g, "CHESS", subject)
        board(cv, col, d, x0=x0, y0=72, s=s)
        top = 72 + 8 * s + 34
        _rule(cv, col, B, W - B, top)
        left, edge = B + 14, W - B - 14
        to_move(cv, col, d, x=left, right=edge, y=top + 22, big=18)
        _rule(cv, col, B, W - B, top + 66)
        last_move(cv, col, d, x=left, right=edge, y=top + 86, big=15)
        return cv.svg()
    s, x0, y0, split = 44, 56, 78, 448
    H = 474
    cv, col = new("chess", variant, th, tone, W, H, d["title"], d["desc"])
    sheet(cv, col, W=W, H=H, border=B, zones=g["zones"], plain=((x0, y0, 8 * s, 8 * s),))
    title(cv, col, g, "CHESS", subject, right)
    board(cv, col, d, x0=x0, y0=y0, s=s)
    cv.add(_open(col, f"M{split} 52V{H - B}", .55, ' stroke-width=".8"'))
    x, edge = split + 22, W - B - 20
    base = to_move(cv, col, d, x=x, right=edge, y=80)
    _rule(cv, col, split, W - B, base + 14)
    base = last_move(cv, col, d, x=x, right=edge, y=base + 36)
    _rule(cv, col, split, W - B, base + 14)
    base = taken(cv, col, d, x=x, right=edge, y=base + 36)
    _rule(cv, col, split, W - B, base + 10)
    base = score_sheet(cv, col, d, x=x, right=edge, y=base + 32, rows=4)
    _rule(cv, col, split, W - B, base + 14)
    hall(cv, col, d, x=x, right=edge, y=base + 36, rows=2)
    return cv.svg()
