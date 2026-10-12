# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Tic-Tac-Toe sheet is drawn from: the game as the profile's own engine hands it over, checked and read.

The board arrives as three rows of X, O or a dot, the top row first, as a FEN gives chess's ranks: `O../XX./O.X`.
Its cells are named as chess names squares, a file and a rank, a1 at the lower left and c3 at the upper right, and
a move is the mark and its cell, `Xb2`, the score sheet adding a `#` to the move that won, as chess marks a mate. The
house always plays X and GitHub always O. The Arbiter opens every game for a side drawn at random, with a random
first move, and `opens` says which side that was: its mark moves first, so in a game opened for GitHub, O does, and
nothing here assumes which. Once a side has won, the three cells of the winning `line` come with the board.

Nothing on the sheet helps a player choose: no cell a side could win on next, no word of what perfect play makes of
the game, no call to block, and no `+` or `#` on a move still to play. The fields that once said so, `threats` and
`outlook`, are turned away with a word on why.
"""
from __future__ import annotations

import re

from ..chess.game import OWNER, is_text
from ..games import data as D
from ..games.sides import GITHUB, HOUSE, SIDES, name, other

KIND = "tictactoe"
FILES = "abc"
BOARD = re.compile(r"[XO.]{3}/[XO.]{3}/[XO.]{3}")
MOVE = re.compile(r"[XO][a-c][1-3]#?")
OFFER = re.compile(r"[XO][a-c][1-3]")    # a move still to play: never a mark that says what it would do
CODE = r"[a-c][1-3]"                     # a move as an issue's title names it: its cell
GONE = {"threats": "the board never shows where a side could win next, which would tell a player where to go",
        "outlook": "the board never says what perfect play makes of the game, which would tell a player how to play"}
LINES = (("a1", "b1", "c1"), ("a2", "b2", "c2"), ("a3", "b3", "c3"), ("a1", "a2", "a3"), ("b1", "b2", "b3"),
         ("c1", "c2", "c3"), ("a1", "b2", "c3"), ("a3", "b2", "c1"))
# How a game ends, and whether that end has a winner: three in a row, or every cell taken without one.
ENDS = {"three in a row": True, "a full board": False}


def placement(board: str) -> dict[str, str]:
    """The marks by cell, from the board's three rows: {"b2": "X", "a1": "O", ...}."""
    out = {}
    for row, text in enumerate(board.split("/")):
        for f, ch in enumerate(text):
            if ch != ".":
                out[f"{FILES[f]}{3 - row}"] = ch
    return out


MARK = {HOUSE: "X", GITHUB: "O"}            # each side's mark, in every game: the house X, GitHub O


def mark_of(side: str) -> str:
    """The mark a side plays: X for the house, O for GitHub, whoever opened."""
    return MARK[side]


def each(side: str, opens: str) -> int:
    """The marks a side has for the game: five for the side that moves first, four for the other, nine cells in all."""
    return 5 if side == opens else 4


def to_move(marks: dict[str, str], opens: str) -> str:
    """Whose turn it is: the side that opened when both have made as many marks, else the other side."""
    first = sum(1 for m in marks.values() if m == MARK[opens])
    return opens if first == len(marks) - first else other(opens)


def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    board = d.get("board", "")
    if not is_text(board, BOARD):
        return [f"board {board!r} is not three rows of X, O or a dot, such as O../XX./O.X"]
    errors = []
    marks = placement(board)
    xs = sum(1 for m in marks.values() if m == "X")
    noughts = len(marks) - xs
    if abs(xs - noughts) > 1:
        errors.append(f"board has {xs} X and {noughts} O: the sides take turns, so one has as many marks as the other"
                      " or one more")
    if "x" in d:
        errors.append("x is gone: the house always plays X and GitHub O, and opens names the side that moved first")
    errors += [f"{key} is gone: {why}" for key, why in GONE.items() if key in d]
    opens = d.get("opens")
    if opens not in SIDES:
        return errors + [f"opens {opens!r} is the side the Arbiter opened for, which moved first: house, which plays"
                         " X, or github, which plays O"]
    first, then = MARK[opens], MARK[other(opens)]
    if abs(xs - noughts) <= 1 and sum(1 for m in marks.values() if m == first) < len(marks) / 2:
        errors.append(f"board has {xs} X and {noughts} O: {first} moved first, the Arbiter having opened for {opens},"
                      f" so {first} has as many marks as {then} or one more")
    turn = to_move(marks, opens)
    result = d.get("result")
    winner = result.get("winner") if isinstance(result, dict) else None
    line = d.get("line")
    if line and not (isinstance(line, list) and all(isinstance(cell, str) for cell in line)
                     and tuple(line) in LINES + tuple(t[::-1] for t in LINES)):
        errors.append(f"line {line!r} is three cells in a row, such as [c1, b2, a3]")
    elif line and not (winner in SIDES and all(marks.get(cell) == MARK[winner] for cell in line)):
        errors.append("line: the winning line is the winner's three marks, and only a won game has one")
    elif winner in SIDES and not line:
        errors.append("line: a won game names its winning line, its three cells")
    last = d.get("last")
    move = last.get("move") if isinstance(last, dict) else None
    if is_text(move, MOVE):
        if marks.get(move[1:3]) != move[0]:
            errors.append(f"last: move {move!r} is not a mark the board has where it says")
        elif move[0] != MARK[other(turn)]:
            errors.append(f"last: move {move!r} is not the mark of the side that moved last")
    return errors + D.check(d, KIND, MOVE, CODE, ENDS, other(turn), (), OFFER)


def state(d: dict) -> dict:
    """The board as the sheet draws it: the marks, whose turn it is, the last mark and its number, the marks each side
    has for the game and has left, the winning line, and the common state every game's sheet reads."""
    board = placement(d["board"])
    opens = d["opens"]
    turn = to_move(board, opens)
    st = D.state(d, to_move=turn, opens=opens)
    if st["last"]:
        mark = st["last"]["move"][0]                 # its number is how many of its marks the board holds
        st["last"].update(cell=st["last"]["move"][1:3], mark=mark, number=sum(1 for m in board.values() if m == mark))
    marks = {side: each(side, opens) for side in SIDES}
    left = {side: marks[side] - sum(1 for m in board.values() if m == MARK[side]) for side in SIDES}
    st.update(KIND=KIND, board=board, each=marks, left=left, line=[str(c) for c in d.get("line") or []])
    return st


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = state(d)
    d.setdefault("title", f"Tic-Tac-Toe: game {st['game']}, move {st['move']}")
    who = f"@{OWNER} plays X and GitHub O"            # the house's side first, as every pair of sides is said
    if st["last"]:
        words = st["last"]["words"]
        said = words if words[:2] in ("X ", "O ") else words[0].lower() + words[1:]   # a mark keeps its capital
        by = (f", the Arbiter's move for {name(st['last']['side'])}" if st["last"]["by"] == "the Arbiter" else "")
        head = (f"Game {st['game']} of @{OWNER} against GitHub, {who}, after {D.numbered(st)} {st['last']['move']}"
                f"{by}: {said}.")
    else:
        head = f"Game {st['game']} of @{OWNER} against GitHub, {who}, before its first mark."
    if st["result"]:
        w = st["result"]["winner"]
        turn = (f" {name(w)} won with three in a row, from {st['line'][0]} to {st['line'][-1]}." if w
                else " The game was drawn on a full board.")
        turn += f" Game {st['game'] + 1} opens {st['next']}." if st["next"] else ""
    else:
        turn = (f" It is {name(st['to_move'])}'s turn as {mark_of(st['to_move'])}"
                + (f", due by {st['due']}." if st["due"] else "."))
    marks = []
    for mark in ("X", "O"):
        cells = sorted(c for c, m in st["board"].items() if m == mark)
        said = " and ".join(cells) if len(cells) < 3 else ", ".join(cells[:-1]) + " and " + cells[-1]
        marks.append(f"{mark}: {said or 'no mark yet'}")
    d.setdefault("desc", head + turn + " " + "; ".join(marks) + ".")
    return d
