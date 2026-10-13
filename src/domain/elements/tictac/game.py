# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Tic-Tac sheet is drawn from: the game as the profile's own engine hands it over, checked and read.

Tic-Tac is Tic-Tac-Toe played on nine boards at once, three a side, the game also known as Ultimate Tic-Tac-Toe.
The board arrives as its nine rows of nine squares, the top row first, each square X, O, G (a ghost) or a dot, as a
FEN gives chess's ranks. Its squares are named as chess names them, a file a to i and a rank 1 to 9, a1 at the lower
left, and the small boards as Tic-Tac-Toe names its cells, a1 the lower left board and c3 the upper right. A move is
the mark and its square, `Xe5`, the score sheet adding a `#` to the move that won.

The square a mark takes inside its board sends the other side to the board in the same place on the big board:
take a board's upper right corner and the other side plays in the upper right board. Three in a row inside a board
wins it and closes it; a board whose open squares are all taken without a line is drawn and closed too. A side sent
to a closed board plays any open square of any open board, as the first mark may. Three boards won in a row wins the
game, and a game that neither side can still win that way is drawn.

The Ghost Rule: before the first mark, each side locks one square with a ghost, the side the Arbiter drew placing
first (`places`). A ghost's square is written as the square alone, `e5`, on the score sheet's G row. Nobody can take
it, no line runs through it, and a board with a ghost is full once its other squares are taken. Once both ghosts are
down, the Arbiter draws which side makes the first mark (`opens`), anywhere.

The house always plays X and GitHub always O, whichever side places first or opens. The turn's plate says where the
side to move must play, since that is the rules, as checkers calls out a jump: in a board (`alert` "upper right
board"), in any open board ("any board"), or a ghost to place ("place a ghost"). Nothing else on the sheet helps a
player choose: no square a side could win a board on next, no board a side could win the game on, no call to block,
and no `+` or `#` on a move still to play.
"""
from __future__ import annotations

import re

from ..chess.game import OWNER, is_text
from ..games import data as D
from ..games.sides import GITHUB, HOUSE, SIDES, name, other

KIND = "tictac"
FILES = "abcdefghi"
BOARDS = "abc"                                # the small boards' files, as Tic-Tac-Toe names its cells
BOARD = re.compile(r"(?:[XOG.]{9}/){8}[XOG.]{9}")
MOVE = re.compile(r"[XO][a-i][1-9]#?|[a-i][1-9]")     # a mark, or a ghost's square
OFFER = re.compile(r"[XO][a-i][1-9]|[a-i][1-9]")      # a move still to play: never a mark that says what it would do
CODE = r"[a-i][1-9]"                                  # a move as an issue's title names it: its square
GHOST = "G"                                           # the score sheet's row of the two ghosts
# The eight lines of three, in a board and on the big board, each as (file, rank) steps from its lower left.
LINES = (((0, 0), (1, 0), (2, 0)), ((0, 1), (1, 1), (2, 1)), ((0, 2), (1, 2), (2, 2)),
         ((0, 0), (0, 1), (0, 2)), ((1, 0), (1, 1), (1, 2)), ((2, 0), (2, 1), (2, 2)),
         ((0, 0), (1, 1), (2, 2)), ((0, 2), (1, 1), (2, 0)))
# Where a board stands on the big board, and a square in its board, by (file, rank) from the lower left.
PLACE = {(0, 2): "upper left", (1, 2): "top", (2, 2): "upper right", (0, 1): "left", (1, 1): "centre",
         (2, 1): "right", (0, 0): "lower left", (1, 0): "bottom", (2, 0): "lower right"}
SQUARE = {(0, 2): "upper left corner", (1, 2): "top edge", (2, 2): "upper right corner", (0, 1): "left edge",
          (1, 1): "centre", (2, 1): "right edge", (0, 0): "lower left corner", (1, 0): "bottom edge",
          (2, 0): "lower right corner"}
GHOSTING, ANYWHERE = "place a ghost", "any board"
# What a turn's plate says, the rules alone: a ghost to place, any open board, or the board the side is sent to.
ALERTS = (GHOSTING, ANYWHERE, *(f"{p} board" for p in PLACE.values()))
# How a game ends, and whether that end has a winner: three boards in a row, or no line of three boards left to win.
ENDS = {"three boards in a row": True, "no line left": False}
GONE = {"x": "the house always plays X and GitHub O, and places and opens name the sides the Arbiter drew"}

MARK = {HOUSE: "X", GITHUB: "O"}            # each side's mark, in every game: the house X, GitHub O


def mark_of(side: str) -> str:
    """The mark a side plays: X for the house, O for GitHub, whoever places first or opens."""
    return MARK[side]


def xy(cell: str) -> tuple[int, int]:
    """A square's file and rank, from 0 at the lower left."""
    return FILES.index(cell[0]), int(cell[1]) - 1


def square(x: int, y: int) -> str:
    return f"{FILES[x]}{y + 1}"


def board_of(cell: str) -> tuple[int, int]:
    """The board a square stands in, by its file and rank on the big board, from 0 at the lower left."""
    x, y = xy(cell)
    return x // 3, y // 3


def spot_of(cell: str) -> tuple[int, int]:
    """Where a square stands inside its board: the board on the big board it sends the other side to."""
    x, y = xy(cell)
    return x % 3, y % 3


def board_name(b: tuple[int, int]) -> str:
    """A board as Tic-Tac-Toe names a cell: a1 the lower left board, c3 the upper right."""
    return f"{BOARDS[b[0]]}{b[1] + 1}"


def board_at(text: str) -> tuple[int, int]:
    return BOARDS.index(text[0]), int(text[1]) - 1


def cells_of(b: tuple[int, int]) -> list[str]:
    """A board's nine squares, as it is read: its top row first, each from the left."""
    bx, by = b
    return [square(bx * 3 + i, by * 3 + j) for j in (2, 1, 0) for i in range(3)]


def placement(board: str) -> dict[str, str]:
    """The marks and ghosts by square, from the board's nine rows: {"e5": "G", "d4": "X", ...}."""
    out = {}
    for row, text in enumerate(board.split("/")):
        for f, ch in enumerate(text):
            if ch != ".":
                out[f"{FILES[f]}{9 - row}"] = ch
    return out


def won_line(squares: dict, b: tuple[int, int], mark: str) -> list[str] | None:
    """The first line of three `mark` holds in board `b`, as its squares, or None."""
    bx, by = b
    for line in LINES:
        cells = [square(bx * 3 + i, by * 3 + j) for i, j in line]
        if all(squares.get(c) == mark for c in cells):
            return cells
    return None


def boards(squares: dict) -> dict[tuple[int, int], str | None]:
    """Each board as it stands: won by X or O, drawn ("draw"), or still open (None). A board is won by its line, and
    drawn once every square without a ghost is taken."""
    out = {}
    for b in PLACE:
        won = next((m for m in "XO" if won_line(squares, b, m)), None)
        out[b] = won or ("draw" if all(c in squares for c in cells_of(b)) else None)
    return out


def big_line(closed: dict, mark: str) -> list[tuple[int, int]] | None:
    """The first line of three boards `mark` has won, or None."""
    for line in LINES:
        if all(closed[b] == mark for b in line):
            return list(line)
    return None


def open_lines(closed: dict, mark: str) -> bool:
    """Whether `mark` could still win three boards in a row: a line none of whose boards is won by the other mark or
    drawn."""
    return any(all(closed[b] in (None, mark) for b in line) for line in LINES)


def to_move(squares: dict, places: str, opens: str | None) -> str:
    """Whose turn it is: while the ghosts go down, the side that places first and then the other; after them, the side
    the Arbiter drew to open when both have made as many marks, else the other side."""
    ghosts = sum(1 for m in squares.values() if m == GHOST)
    if ghosts < 2 or opens not in SIDES:
        return places if ghosts == 0 else other(places)
    first = sum(1 for m in squares.values() if m == MARK[opens])
    made = sum(1 for m in squares.values() if m in "XO")
    return opens if first == made - first else other(opens)


def target(squares: dict, closed: dict, last_cell: str | None) -> tuple[int, int] | None:
    """The board the side to move is sent to: the one in the same place on the big board as the last mark's square in
    its own, while it is open; None, any open board, when it is closed or before the first mark."""
    if not last_cell or squares.get(last_cell) not in ("X", "O"):
        return None
    b = spot_of(last_cell)
    return b if closed[b] is None else None


def alert_of(squares: dict, closed: dict, last_cell: str | None) -> str:
    """What the turn's plate says: a ghost to place, the board the side is sent to, or any board."""
    if sum(1 for m in squares.values() if m == GHOST) < 2:
        return GHOSTING
    b = target(squares, closed, last_cell)
    return f"{PLACE[b]} board" if b else ANYWHERE


def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    board = d.get("board", "")
    if not is_text(board, BOARD):
        return [f"board {board!r} is not nine rows of nine X, O, G or dots, the top row first"]
    errors = []
    squares = placement(board)
    xs = sum(1 for m in squares.values() if m == "X")
    noughts = sum(1 for m in squares.values() if m == "O")
    ghosts = sum(1 for m in squares.values() if m == GHOST)
    errors += [f"{key} is gone: {why}" for key, why in GONE.items() if key in d]
    places, opens = d.get("places"), d.get("opens")
    if ghosts > 2:
        errors.append(f"board has {ghosts} ghosts: the Ghost Rule locks two squares, one for each side")
    elif ghosts < 2 and xs + noughts:
        errors.append(f"board has {xs + noughts} mark{'s' if xs + noughts != 1 else ''} and {ghosts}"
                      f" ghost{'s' if ghosts != 1 else ''}: no mark goes"
                      " down until both ghosts are")
    if places not in SIDES:
        return errors + [f"places {places!r} is the side the Arbiter drew to place the first ghost: house, which plays"
                         " X, or github, which plays O"]
    if ghosts == 2 and opens not in SIDES:
        return errors + [f"opens {opens!r} is the side the Arbiter drew to make the first mark once both ghosts were"
                         " down: house, which plays X, or github, which plays O"]
    if ghosts < 2 and opens is not None:
        errors.append("opens: the Arbiter draws the side that makes the first mark once both ghosts are down")
    if ghosts == 2:
        first, then = MARK[opens], MARK[other(opens)]
        made = {"X": xs, "O": noughts}
        if made[first] - made[then] not in (0, 1):
            errors.append(f"board has {xs} X and {noughts} O: {first} moved first, the Arbiter having drawn {opens} to"
                          f" open, so {first} has as many marks as {then} or one more")
    closed = boards(squares)
    for b, who in closed.items():
        if who in ("X", "O") and won_line(squares, b, "X" if who == "O" else "O"):
            errors.append(f"board {board_name(b)} has three in a row for both marks: a board closes once it is won")
    turn = to_move(squares, places, opens)
    result = d.get("result")
    winner = result.get("winner") if isinstance(result, dict) else None
    line = d.get("line")
    names = [board_name(line_b) for line_b in PLACE]
    if line and not (isinstance(line, list) and len(line) == 3 and all(b in names for b in line if isinstance(b, str))
                     and all(isinstance(b, str) for b in line)
                     and tuple(board_at(b) for b in line) in LINES + tuple(t[::-1] for t in LINES)):
        errors.append(f"line {line!r} is three boards in a row, each named as Tic-Tac-Toe names a cell, such as"
                      " [a3, b2, c1]")
    elif line and not (winner in SIDES and all(closed[board_at(b)] == MARK[winner] for b in line)):
        errors.append("line: the winning line is three boards the winner has won, and only a won game has one")
    elif winner in SIDES and not line:
        errors.append("line: a won game names its winning line, its three boards")
    last = d.get("last")
    move = last.get("move") if isinstance(last, dict) else None
    last_cell = None
    if is_text(move, MOVE):
        ghost = move[0] not in "XO"
        last_cell = move if ghost else move[1:3]
        if ghost and (squares.get(last_cell) != GHOST or xs + noughts):
            errors.append(f"last: move {move!r} is a ghost's square, and the last move is a ghost's only before the"
                          " first mark, on a square the board has a ghost on")
        elif not ghost and squares.get(last_cell) != move[0]:
            errors.append(f"last: move {move!r} is not a mark the board has where it says")
        elif not ghost and move[0] != MARK[other(turn)]:
            errors.append(f"last: move {move!r} is not the mark of the side that moved last")
    elif xs + noughts:
        errors.append("last: a board with marks on it names the last of them")
    alert = d.get("alert")
    if not d.get("result") and isinstance(alert, str) and alert in ALERTS:
        due = alert_of(squares, closed, last_cell)
        if alert != due:
            errors.append(f"alert {alert!r} is not where the side to move must play: {due}")
    elif not d.get("result") and not alert:
        errors.append(f"alert: a game under way says where the side to move must play: {', '.join(ALERTS[:2])} or a"
                      " board, such as upper right board")
    moved = other(turn) if xs + noughts else (places if ghosts == 1 else other(places))
    return errors + D.check(d, KIND, MOVE, CODE, ENDS, moved, ALERTS, OFFER, ghost_row=True)


def state(d: dict) -> dict:
    """The board as the sheet draws it: the marks and the ghosts, whose turn it is and where, the last move and its
    number, each board won or drawn, the winning lines, and the common state every game's sheet reads."""
    squares = placement(d["board"])
    places, opens = d["places"], d.get("opens")
    ghosts = sorted((c for c, m in squares.items() if m == GHOST), key=lambda c: (-xy(c)[1], xy(c)[0]))
    ghosting = len(ghosts) < 2
    turn = to_move(squares, places, opens)
    # the score sheet's columns: the ghosts' row in the order they went down, and the marks' in the opener's order
    first = places if ghosting or opens not in SIDES else opens
    st = D.state(d, to_move=turn, opens=first)
    closed = boards(squares)
    last = st["last"]
    cell = None
    if last:
        move = last["move"]
        if move[0] in "XO":
            cell, mark = move[1:3], move[0]
            claimed = closed[board_of(cell)]
            small = won_line(squares, board_of(cell), mark) if claimed == mark else None
            last.update(cell=cell, mark=mark, ghost=False, board=board_of(cell), claimed=claimed, small_line=small,
                        number=sum(1 for m in squares.values() if m == mark))
        else:
            cell = move
            side = places if len(ghosts) == 1 else other(places)
            last.update(cell=cell, mark="", ghost=True, board=board_of(cell), claimed=None, small_line=None,
                        number=GHOST, side=side, second=len(ghosts) == 2)
    won = {side: sum(1 for v in closed.values() if v == MARK[side]) for side in SIDES}
    st.update(KIND=KIND, cells={c: m for c, m in squares.items() if m in "XO"}, ghosts=ghosts, ghosting=ghosting,
              places=places, first_mark=opens if opens in SIDES else None, boards=closed, won=won,
              drawn=sum(1 for v in closed.values() if v == "draw"),
              target=None if st["result"] or ghosting else target(squares, closed, cell),
              line=[board_at(str(b)) for b in d.get("line") or []], stage="ghosts" if ghosting else "")
    return st


def where(st: dict) -> str:
    """Where the side to move plays, in words: in the board it is sent to, or in any open board."""
    return f"in the {PLACE[st['target']]} board" if st["target"] else "in any open board"


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = state(d)
    d.setdefault("title", f"Tic-Tac: game {st['game']}, " + ("the ghosts" if st["ghosting"] else f"move {st['move']}"))
    who = f"@{OWNER} plays X and GitHub O, under the Ghost Rule"   # the house's side first, as every pair is said
    ghosts = " and ".join(st["ghosts"])
    head = f"Game {st['game']} of @{OWNER} against GitHub, {who}." + (f" Ghosts lock {ghosts}." if ghosts else "")
    if st["last"]:
        words = st["last"]["words"]
        said = words if words[:2] in ("X ", "O ") else words[0].lower() + words[1:]   # a mark keeps its capital
        by = (f", the Arbiter's move for {name(st['last']['side'])}" if st["last"]["by"] == "the Arbiter" else "")
        head += f" After {D.numbered(st)} {st['last']['move']}{by}: {said}."
    if st["result"]:
        w = st["result"]["winner"]
        turn = (f" {name(w)} won with three boards in a row." if w
                else " The game was drawn, with no line of three boards left for either side.")
        turn += f" Game {st['game'] + 1} opens {st['next']}." if st["next"] else ""
    elif st["ghosting"]:
        turn = (f" It is {name(st['to_move'])}'s turn to place a ghost"
                + (f", due by {st['due']}." if st["due"] else "."))
    else:
        drew = (f" The Arbiter drew {name(st['first_mark'])} to make the first mark." if not st["cells"] else "")
        turn = (f"{drew} It is {name(st['to_move'])}'s turn as {mark_of(st['to_move'])}, {where(st)}"
                + (f", due by {st['due']}." if st["due"] else "."))
    count = f" Boards won: X {st['won'][HOUSE]}, O {st['won'][GITHUB]}" + (f", {st['drawn']} drawn." if st["drawn"]
                                                                            else ".")
    d.setdefault("desc", head + turn + count)
    return d
