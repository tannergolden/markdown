# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Connect Four sheet is drawn from: the game as the profile's own engine hands it over, checked and read.

The board arrives as its six rows, the top row first, each seven cells of L (a White disc, the house's), D (a Black
one, GitHub's) or a dot, as a FEN gives chess's ranks. Its columns are numbered 1 to 7 from the left and its rows 1 to
6 from the foot, and a move is the column a disc is dropped down, `4`, the score sheet adding a `#` to the drop
that connected four.

The house always drops the White discs and GitHub the Black. The Arbiter opens every game for a side drawn at
random, with a random first move, and `opens` says which side that was, so a game opens with a White disc when it
was opened for the house and a Black one when for GitHub. Nothing here assumes which side opened: the two sides are
told apart by their discs, never by their order. Once a side has won, the four cells of the winning `line` come
with the board.

Nothing on the sheet helps a player choose: no column a side could connect four down next, no call to block, and
no `+` or `#` on a move still to play. The field that once said so, `threats`, is turned away with a word on why.
"""
from __future__ import annotations

import re

from ..chess.game import OWNER, is_number, is_text
from ..games import data as D
from ..games.sides import GITHUB, HOUSE, SIDES, name, other

KIND = "connectfour"
COLS, ROWS, EACH = 7, 6, 21          # the frame, and the discs each side has
BOARD = re.compile(r"(?:[LD.]{7}/){5}[LD.]{7}")
MOVE = re.compile(r"[1-7]#?")
OFFER = re.compile(r"[1-7]")         # a move still to play: never a mark that says what it would do
CODE = r"[1-7]"                      # a move as an issue's title names it: its column
GONE = {"threats": "the frame never shows a column a side could connect four down next, which would tell a player"
                   " where to drop"}
# How a game ends, and whether that end has a winner: four in a row, or every hole filled without one.
ENDS = {"four in a row": True, "a full frame": False}
STEPS = ((1, 0), (0, 1), (1, 1), (1, -1))   # a line's direction: across, up, and the two diagonals


def placement(board: str) -> dict[tuple[int, int], str]:
    """The discs by (column, row), both counted from 1 at the lower left: {(4, 1): "L", ...}."""
    out = {}
    for i, text in enumerate(board.split("/")):
        for j, ch in enumerate(text):
            if ch != ".":
                out[(j + 1, ROWS - i)] = ch
    return out


def heights(board: dict) -> dict[int, int]:
    return {col: sum(1 for (c, _) in board if c == col) for col in range(1, COLS + 1)}


LETTER = {HOUSE: "L", GITHUB: "D"}          # each side's discs on the board: the house's White, GitHub's Black
COLOUR = {HOUSE: "White", GITHUB: "Black"}   # and what a reader is told they are


def material_of(side: str) -> str:
    """The material a side's discs are drawn in: the light one for the house's White, the dark for GitHub's Black."""
    return "light" if side == HOUSE else "dark"


def to_move(discs: dict, opens: str) -> str:
    """Whose turn it is: the opener's when both sides have dropped as many discs, else the other side's."""
    first = sum(1 for v in discs.values() if v == LETTER[opens])
    return opens if first == len(discs) - first else other(opens)


def in_a_row(line) -> bool:
    """Whether `line` is four cells of the frame, each [column, row], one after another along a straight line."""
    if not (isinstance(line, list) and len(line) == 4
            and all(isinstance(p, list) and len(p) == 2 and all(is_number(v, 1, 7) for v in p) and p[1] <= ROWS
                    for p in line)):
        return False
    steps = {(b[0] - a[0], b[1] - a[1]) for a, b in zip(line, line[1:])}
    return len(steps) == 1 and (steps <= set(STEPS) or {(-x, -y) for x, y in steps} <= set(STEPS))


def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    board = d.get("board", "")
    if not is_text(board, BOARD):
        return [f"board {board!r} is six rows of seven L, D or dots, the top row first"]
    errors = []
    discs = placement(board)
    for (col, row) in sorted(discs):
        if row > 1 and (col, row - 1) not in discs:
            errors.append(f"board has a disc in column {col}, row {row}, over an empty hole: discs fall")
            break
    if "light" in d:
        errors.append("light is gone: the house always drops the White discs and GitHub the Black, and opens names"
                      " the side that dropped first")
    errors += [f"{key} is gone: {why}" for key, why in GONE.items() if key in d]
    opens = d.get("opens")
    if opens not in SIDES:
        return errors + [f"opens {opens!r} is the side the Arbiter opened for, which dropped the first disc: house,"
                         " which drops White, or github, which drops Black"]
    white = sum(1 for v in discs.values() if v == "L")
    first = sum(1 for v in discs.values() if v == LETTER[opens])
    if first - (len(discs) - first) not in (0, 1):
        errors.append(f"board has {white} White discs and {len(discs) - white} Black: {COLOUR[opens]} dropped first,"
                      f" the Arbiter having opened for {opens}, so it has as many as {COLOUR[other(opens)]} or one"
                      " more")
    turn = to_move(discs, opens)
    result = d.get("result")
    winner = result.get("winner") if isinstance(result, dict) else None
    line = d.get("line")
    if line and not in_a_row(line):
        errors.append("line is the four cells connected, one after another, each a column and a row, such as"
                      " [[2, 4], [3, 3], [4, 2], [5, 1]]")
    elif line and not (winner in SIDES
                       and all(discs.get(tuple(p)) == LETTER[winner] for p in line)):
        errors.append("line: the winning line is the winner's four discs, and only a won game has one")
    elif winner in SIDES and not line:
        errors.append("line: a won game names its winning line, its four cells")
    last = d.get("last")
    move = last.get("move") if isinstance(last, dict) else None
    if is_text(move, MOVE):
        col = int(move[0])
        top = max((row for (c, row) in discs if c == col), default=0)
        if not top:
            errors.append(f"last: move {move!r} is down a column with no disc in it")
        elif discs[(col, top)] != LETTER[other(turn)]:
            errors.append(f"last: move {move!r} is not topped by a disc of the side that moved last")
    return errors + D.check(d, KIND, MOVE, CODE, ENDS, other(turn), (), OFFER)


def state(d: dict) -> dict:
    """The board as the sheet draws it: the discs, whose turn it is, the last disc and where it landed, the winning
    line, the discs each side has left, and the common state every game's sheet reads."""
    board = placement(d["board"])
    opens = d["opens"]
    turn = to_move(board, opens)
    st = D.state(d, to_move=turn, opens=opens)
    tall = heights(board)
    if st["last"]:
        col = int(st["last"]["move"][0])
        mine = sum(1 for v in board.values() if v == LETTER[st["last"]["side"]])
        st["last"].update(column=col, row=tall[col], number=mine)
    left = {side: EACH - sum(1 for v in board.values() if v == LETTER[side]) for side in SIDES}
    st.update(KIND=KIND, board=board, left=left, line=[tuple(p) for p in d.get("line") or []])
    return st


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = state(d)
    d.setdefault("title", f"Connect Four: game {st['game']}, move {st['move']}")
    who = f"@{OWNER} drops the White discs and GitHub the Black"   # the house's side first, as every pair is said
    if st["last"]:
        words = st["last"]["words"]
        said = words[0].lower() + words[1:]
        by = (f", the Arbiter's move for {name(st['last']['side'])}" if st["last"]["by"] == "the Arbiter" else "")
        head = (f"Game {st['game']} of @{OWNER} against GitHub, {who}, after {D.numbered(st)} {st['last']['move']}"
                f"{by}: {said}.")
    else:
        head = f"Game {st['game']} of @{OWNER} against GitHub, {who}, before its first disc."
    if st["result"]:
        w = st["result"]["winner"]
        turn = f" {name(w)} won with four in a row." if w else " The game was drawn on a full frame."
        turn += f" Game {st['game'] + 1} opens {st['next']}." if st["next"] else ""
    else:
        turn = (f" It is {name(st['to_move'])}'s turn as {COLOUR[st['to_move']]}"
                + (f", due by {st['due']}." if st["due"] else "."))
    cols = []
    for col in range(1, COLS + 1):
        stack = [st["board"][(col, row)] for row in range(1, ROWS + 1) if (col, row) in st["board"]]
        if stack:
            cols.append(f"column {col}, from the foot: " + ", ".join("White" if v == "L" else "Black" for v in stack))
    said = "; ".join(cols)
    d.setdefault("desc", head + turn + (f" {said[0].upper()}{said[1:]}." if cols else " The frame is empty."))
    return d
