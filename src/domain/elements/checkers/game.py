# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Checkers sheet is drawn from: the game as the profile's own engine hands it over, checked and read.

The position arrives as checkers writes one, a PDN FEN: whose turn, then White's men's squares and Black's, a K
before a king's, as `B:W21,22,K30:B1,2,9`. The game is American checkers in every respect: the thirty-two dark
squares are numbered 1 to 32 from Black's back row, Black's men start on 1 to 12 and White's on 21 to 32, Black moves
first, and a move is written as checkers writes it: `11-15` for a step and `22x15x8` for a jump, a square for every
landing. GitHub always plays Black, so GitHub opens every game, and the house always plays White. What the engine
knows that the board does not say comes with it: whether the last move `crowned` its man, the kings each side has
made, and that the side to move `must jump`.
"""
from __future__ import annotations

import re

from ..chess.game import OWNER, is_number, is_text
from ..games import data as D
from ..games.sides import GITHUB, HOUSE, SIDES, name, other

KIND = "checkers"
SQUARES = range(1, 33)
_LIST = r"(?:K?(?:3[0-2]|[12]?[0-9])(?:,K?(?:3[0-2]|[12]?[0-9]))*)?"
FEN = re.compile(rf"[BW]:W{_LIST}:B{_LIST}")
SQ = r"(?:3[0-2]|[12][0-9]|[1-9])"
CODE = rf"{SQ}(?:-{SQ}|(?:x{SQ}){{1,12}})"   # a move as checkers writes it, and as an issue's title names it
MOVE = re.compile(CODE)                       # a jump takes a man at every landing: twelve at most
MEN = 12
FAR = {"d": range(29, 33), "l": range(1, 5)}  # where each colour's men are crowned: the other side's back row
LETTER = {HOUSE: "l", GITHUB: "d"}            # each side's men in the FEN: the house's White, GitHub's Black
COLOUR = {HOUSE: "White", GITHUB: "Black"}    # and what a reader is told they are
OPENS = GITHUB                                # Black moves first, as American checkers has it: GitHub opens
# How a game ends, and whether that end has a winner: the side to move with no move left loses; a position come
# round a third time, or forty moves each without a capture or a man moved, is drawn, since nobody is there to
# agree a draw.
ENDS = {"no move left": True, "repetition": False, "forty moves": False}


def rc(n: int) -> tuple[int, int]:
    """A square's row and column, both from 0, as American checkers' diagrams print it, White at the foot: Black's
    back row on top, square 1 at its second column, and White's along the foot, square 32 at its seventh."""
    r, i = divmod(n - 1, 4)
    return r, 2 * i + (1 if r % 2 == 0 else 0)


def square(r: int, col: int) -> int | None:
    if not (0 <= r < 8 and 0 <= col < 8) or (r + col) % 2 == 0:
        return None
    return r * 4 + col // 2 + 1


def pieces_of(fen: str) -> list[tuple[int, str]]:
    """Every piece the FEN names, in its order, a square given twice standing twice: [(1, "d"), (30, "L"), ...],
    d and l for men, D and L for kings."""
    out = []
    for part in fen.split(":")[1:]:
        letter = "d" if part[0] == "B" else "l"
        for token in filter(None, part[1:].split(",")):
            out.append((int(token.lstrip("K")), letter.upper() if token.startswith("K") else letter))
    return out


def placement(fen: str) -> dict[int, str]:
    """The pieces by square, from the FEN: {1: "d", 30: "L", ...}."""
    return dict(pieces_of(fen))


def path(move: str) -> list[int]:
    return [int(n) for n in re.split(r"[-x]", move)]


def jumped(move: str) -> list[int]:
    """The squares a jump passes over: one between every two of its landings."""
    if "x" not in move:
        return []
    out = []
    squares = path(move)
    for a, b in zip(squares, squares[1:]):
        (ra, ca), (rb, cb) = rc(a), rc(b)
        out.append(square((ra + rb) // 2, (ca + cb) // 2))
    return out


def material_of(side: str) -> str:
    """The material a side's men are drawn in: the light one for the house's White, the dark for GitHub's Black."""
    return "light" if side == HOUSE else "dark"


def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    fen = d.get("fen", "")
    if not is_text(fen, FEN):
        return [f"fen {fen!r} is not a checkers position in PDN, such as B:W21,22,23:B1,2,3"]
    errors = []
    listed = pieces_of(fen)
    pieces = dict(listed)
    if any(n not in SQUARES for n, _ in listed):
        errors.append("fen names a square that is not one of the 32")
    if len(pieces) < len(listed):
        errors.append("fen names a square twice: one piece stands on a square")
    for colour in ("d", "l"):
        if sum(1 for p in pieces.values() if p.lower() == colour) > MEN:
            errors.append(f"fen has more than {MEN} {'Black' if colour == 'd' else 'White'} pieces")
    if any(p in FAR and n in FAR[p] for n, p in pieces.items()):
        errors.append("fen has a man on its far row, where it would have been crowned")
    if "dark" in d:
        errors.append("dark is gone: GitHub always plays Black, which moves first, and the house White")
    turn = GITHUB if fen[0] == "B" else HOUSE
    last = d.get("last")
    move = last.get("move") if isinstance(last, dict) else None
    if is_text(move, MOVE):
        moved, landed = path(move), path(move)[-1]
        piece = pieces.get(landed, "")
        if not piece:
            errors.append(f"last: move {move!r} does not end on a piece the board has")
        elif piece.lower() != ("l" if fen[0] == "B" else "d"):
            errors.append(f"last: move {move!r} ends on a piece of the side to move, not of the side that moved")
        elif any(n in pieces for n in jumped(move) if n) or None in jumped(move):
            errors.append(f"last: move {move!r} jumps a man the board still has, or jumps no square")
        crowned = last.get("crowned", False)
        if not isinstance(crowned, bool):
            errors.append("last: crowned is true or false: whether the move crowned its man")
        elif crowned and piece and not (piece.isupper() and landed in FAR[piece.lower()]):
            errors.append(f"last: move {move!r} crowned its man, which stands as a king on its far row")
        elif len(set(moved)) < 2:
            errors.append(f"last: move {move!r} goes nowhere")
    kings = d.get("kings") or {}
    if not (isinstance(kings, dict) and set(kings) <= set(SIDES) and all(is_number(v, 0, MEN) for v in kings.values())):
        errors.append(f"kings gives each side the number of kings it has made, up to {MEN}")
    return errors + D.check(d, KIND, MOVE, CODE, ENDS, other(turn), ("must jump",), MOVE)


def state(d: dict) -> dict:
    """The board as the sheet draws it: the pieces, whose turn it is, the last move's path, the men it jumped and
    whether it crowned, what each side has taken and the kings it has made, and the common state."""
    pieces = placement(d["fen"])
    turn = GITHUB if d["fen"][0] == "B" else HOUSE
    st = D.state(d, to_move=turn, opens=OPENS)
    if st["last"]:
        move = st["last"]["move"]
        st["last"].update(path=path(move), jumped=jumped(move), crowned=bool(st["last"].get("crowned")),
                          number=st["move"] if st["last"]["side"] == OPENS else st["move"] - 1)
    left = {side: sum(1 for p in pieces.values() if p.lower() == LETTER[side]) for side in SIDES}
    took = {side: MEN - left[other(side)] for side in SIDES}
    on_board = {side: sum(1 for p in pieces.values() if p == LETTER[side].upper()) for side in SIDES}
    kings = {side: int((d.get("kings") or {}).get(side, on_board[side])) for side in SIDES}
    # the men that must jump: where every jump among the legal moves sets out from
    jumpers = sorted({path(m[2])[0] for m in d.get("moves") or [] if "x" in str(m[2])}) if st["alert"] else []
    st.update(KIND=KIND, pieces=pieces, took=took, kings=kings, jumpers=jumpers)
    return st


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = state(d)
    d.setdefault("title", f"Checkers: game {st['game']}, move {st['move']}")
    if st["last"]:
        words = st["last"]["words"]
        said = words[0].lower() + words[1:]
        by = (f", the Arbiter's move for {name(st['last']['side'])}" if st["last"]["by"] == "the Arbiter" else "")
        head = f"Game {st['game']} of @{OWNER} against GitHub, after {D.numbered(st)} {st['last']['move']}{by}: {said}."
    else:
        head = f"Game {st['game']} of @{OWNER} against GitHub, before its first move."
    if st["result"]:
        w, how = st["result"]["winner"], st["result"]["how"]
        turn = (f" {name(w)} won: {name(other(w))} had no move left." if w
                else f" The game was drawn by {'repetition' if how == 'repetition' else 'the forty-move rule'}.")
        turn += f" Game {st['game'] + 1} opens {st['next']}." if st["next"] else ""
    else:
        turn = (f" It is {name(st['to_move'])}'s turn as {COLOUR[st['to_move']]}"
                + (", and a jump must be taken" if st["alert"] else "")
                + (f", due by {st['due']}." if st["due"] else "."))
    sides = []
    for side in (HOUSE, other(HOUSE)):
        men = sorted(n for n, p in st["pieces"].items() if p == LETTER[side])
        kings = sorted(n for n, p in st["pieces"].items() if p == LETTER[side].upper())
        said = f"men on {', '.join(map(str, men)) or 'no square'}" + (f", kings on {', '.join(map(str, kings))}"
                                                                    if kings else "")
        sides.append(f"{name(side)}, {COLOUR[side]}: {said}")
    d.setdefault("desc", head + turn + " " + "; ".join(sides) + ".")
    return d
