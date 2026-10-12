# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Tic-Tac-Toe sheet is drawn from: the game as the profile's own engine hands it over, checked and read.

The board arrives as three rows of X, O or a dot, the top row first, as a FEN gives chess's ranks: `O../XX./O.X`.
Its cells are named as chess names squares, a file and a rank, a1 at the lower left and c3 at the upper right, and
a move is the mark and its cell, `Xb2`, with a `+` when it makes a threat and a `#` when it wins, as chess marks a
check and a mate. X moves first, and `x` says which side plays it that game: the Arbiter opens every game for a
side drawn at random, with a random move, so the house plays X in some games and O in others, and nothing here
assumes which. What the engine knows that the board does not say comes with it: the cells each side `threatens` to
win on next, the `outlook` with perfect play from here (the game is solved: a draw from the start), and once a side
has won, the three cells of the winning `line`.
"""
from __future__ import annotations

import re

from ..chess.game import OWNER, is_text
from ..games import data as D
from ..games.sides import GITHUB, HOUSE, SIDES, name, other

KIND = "tictactoe"
FILES = "abc"
BOARD = re.compile(r"[XO.]{3}/[XO.]{3}/[XO.]{3}")
CELL = re.compile(r"[a-c][1-3]")
MOVE = re.compile(r"[XO][a-c][1-3][+#]?")
CODE = r"[a-c][1-3]"                     # a move as an issue's title names it: its cell
OUTLOOKS = ("draw", HOUSE, GITHUB)
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


def to_move(marks: dict[str, str], x: str) -> str:
    """Whose turn it is: X's side when both have made as many marks, else O's."""
    xs = sum(1 for m in marks.values() if m == "X")
    return x if xs == len(marks) - xs else other(x)


def mark_of(st: dict, side: str) -> str:
    """The mark a side plays this game: X for the side the Arbiter opened for, O for the other."""
    return "X" if st["x"] == side else "O"


def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    board = d.get("board", "")
    if not is_text(board, BOARD):
        return [f"board {board!r} is not three rows of X, O or a dot, such as O../XX./O.X"]
    errors = []
    marks = placement(board)
    xs = sum(1 for m in marks.values() if m == "X")
    if xs - (len(marks) - xs) not in (0, 1):
        errors.append(f"board has {xs} X and {len(marks) - xs} O: X moves first, so X has as many marks as O or one"
                      " more")
    x = d.get("x")
    if x not in SIDES:
        return errors + [f"x {x!r} is the side that plays X this game, the one the Arbiter opened for: house or"
                         " github"]
    turn = to_move(marks, x)
    threats = d.get("threats") or {}
    if not (isinstance(threats, dict) and set(threats) <= set(SIDES)
            and all(isinstance(v, list) and len(set(map(str, v))) == len(v)
                    and all(is_text(cell, CELL) and cell not in marks for cell in v)
                    for v in threats.values())):
        errors.append("threats gives each side the open cells it would win on next, each once, such as [c2]")
    if d.get("outlook") and d["outlook"] not in OUTLOOKS:
        errors.append(f"outlook {d['outlook']!r} is draw, house or github")
    result = d.get("result")
    winner = result.get("winner") if isinstance(result, dict) else None
    line = d.get("line")
    if line and not (isinstance(line, list) and all(isinstance(cell, str) for cell in line)
                     and tuple(line) in LINES + tuple(t[::-1] for t in LINES)):
        errors.append(f"line {line!r} is three cells in a row, such as [c1, b2, a3]")
    elif line and not (winner in SIDES and all(marks.get(cell) == ("X" if winner == x else "O") for cell in line)):
        errors.append("line: the winning line is the winner's three marks, and only a won game has one")
    elif winner in SIDES and not line:
        errors.append("line: a won game names its winning line, its three cells")
    last = d.get("last")
    move = last.get("move") if isinstance(last, dict) else None
    if is_text(move, MOVE):
        if marks.get(move[1:3]) != move[0]:
            errors.append(f"last: move {move!r} is not a mark the board has where it says")
        elif move[0] != ("O" if turn == x else "X"):
            errors.append(f"last: move {move!r} is not the mark of the side that moved last")
    return errors + D.check(d, KIND, MOVE, CODE, ENDS, other(turn), ("must block",))


def state(d: dict) -> dict:
    """The board as the sheet draws it: the marks, whose turn it is, the last mark and its number, the threats, the
    outlook, the winning line, and the common state every game's sheet reads."""
    board = placement(d["board"])
    x = d["x"]
    xs = sum(1 for m in board.values() if m == "X")
    turn = to_move(board, x)
    st = D.state(d, to_move=turn, opens=x)
    if st["last"]:
        mark = st["last"]["move"][0]
        st["last"].update(cell=st["last"]["move"][1:3], mark=mark, number=xs if mark == "X" else len(board) - xs)
    threats = {side: [str(c) for c in (d.get("threats") or {}).get(side, [])] for side in SIDES}
    # a threat must be blocked, unless the side to move can win first
    if not st["result"] and not st["alert"] and threats[other(turn)] and not threats[turn]:
        st["alert"] = "must block"
    st.update(KIND=KIND, board=board, x=x, threats=threats, outlook=d.get("outlook") or "",
              line=[str(c) for c in d.get("line") or []])
    return st


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = state(d)
    d.setdefault("title", f"Tic-Tac-Toe: game {st['game']}, move {st['move']}")
    who = f"{name(st['x'])} plays X and {name(other(st['x']))} O"   # in move order, for whichever side it opened
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
        turn = (f" It is {name(st['to_move'])}'s turn as {mark_of(st, st['to_move'])}"
                + (", and it must block" if st["alert"] else "") + (f", due by {st['due']}." if st["due"] else "."))
    marks = []
    for mark in ("X", "O"):
        cells = sorted(c for c, m in st["board"].items() if m == mark)
        said = " and ".join(cells) if len(cells) < 3 else ", ".join(cells[:-1]) + " and " + cells[-1]
        marks.append(f"{mark}: {said or 'no mark yet'}")
    d.setdefault("desc", head + turn + " " + "; ".join(marks) + ".")
    return d
