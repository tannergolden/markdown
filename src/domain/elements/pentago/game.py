# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""What the Pentago sheet is drawn from: the game as the profile's own engine hands it over, checked and read.

The board is six holes by six in four quarters of three by three, the upper left (a4 to c6), the upper right (d4 to
f6), the lower left (a1 to c3) and the lower right (d1 to f3). It arrives as its six rows, the top row first, each
six holes of W (a White marble, the house's), B (a Black one, GitHub's), G (a ghost) or a dot, as a FEN gives chess's
ranks. Its holes are named as chess names squares, a file a to f and a rank 1 to 6, a1 at the lower left.

A move sets a marble in an empty hole and then turns one quarter a quarter turn, clockwise or anticlockwise as the
board is seen, everything on it turning with it. It is written as the hole, the quarter and the way it turned,
`e4-ur-cw`, the score sheet adding a `#` to the move that won; a marble that makes five in a row on its own wins
before any quarter turns, and is written as its hole alone, `e4#`. Five in a row of one colour, across, up and down
or on a diagonal, wins: the mover's, or the other side's if the turn makes five for it alone, so either side can win
on a move. A turn that makes five for both is a draw, and so is a full board without five.

The Ghost Rule: before the first marble, each side sets one ghost, a marble that is nobody's, in a hole of its
choosing, the side the Arbiter drew setting first (`places`). A ghost's hole is written as the hole alone, `b5`, on
the score sheet's G row. A ghost turns with its quarter, so it can wander, unless it stands on a quarter's centre,
and no five runs through it. Once both are down, the Arbiter draws which side sets the first marble (`opens`). With
two holes taken by ghosts, each side has seventeen marbles.

The house always plays White and GitHub always Black, whichever side sets first or opens. Nothing on the sheet helps
a player choose: no hole or turn that would make five, no call to block, and no `+` or `#` on a move still to play.
"""
from __future__ import annotations

import re

from ..chess.game import OWNER, is_text
from ..games import data as D
from ..games.sides import GITHUB, HOUSE, SIDES, name, other

KIND = "pentago"
FILES = "abcdef"
EACH = 17                                  # the marbles each side has: 34 holes, two of 36 taken by the ghosts
BOARD = re.compile(r"(?:[WBG.]{6}/){5}[WBG.]{6}")
QUARTERS = {"ul": (0, 3), "ur": (3, 3), "ll": (0, 0), "lr": (3, 0)}   # each quarter's lowest file and rank
QNAME = {"ul": "upper left", "ur": "upper right", "ll": "lower left", "lr": "lower right"}
WAYS = {"cw": "clockwise", "acw": "anticlockwise"}
# a move on the score sheet: a hole, its quarter and the way it turned, or a hole alone for a ghost or a marble that
# made five before any turn; a `#` on the move that won
MOVE = re.compile(r"[a-f][1-6]-(?:ul|ur|ll|lr)-(?:cw|acw)#?|[a-f][1-6]#?")
OFFER = re.compile(r"[a-f][1-6]")          # a move still to play: its hole, each turn after it linked on its own
CODE = r"[a-f][1-6](?:-(?:ul|ur|ll|lr)-(?:cw|acw))?"   # a move as an issue's title names it: a hole, then its turn
GHOST = "G"
SETTING = "set a ghost"
ALERTS = (SETTING,)                        # the one thing a turn's plate says: a ghost to set
# How a game ends, and whether that end has a winner.
ENDS = {"five in a row": True, "five for both": False, "a full board": False}
LETTER = {HOUSE: "W", GITHUB: "B"}           # each side's marbles on the board: the house's White, GitHub's Black
COLOUR = {HOUSE: "White", GITHUB: "Black"}   # and what a reader is told they are


def material_of(side: str) -> str:
    """The material a side's marbles are drawn in: the light one for the house's White, the dark for GitHub's Black."""
    return "light" if side == HOUSE else "dark"


def xy(cell: str) -> tuple[int, int]:
    return FILES.index(cell[0]), int(cell[1]) - 1


def hole(x: int, y: int) -> str:
    return f"{FILES[x]}{y + 1}"


def quarter_of(cell: str) -> str:
    x, y = xy(cell)
    return next(q for q, (qx, qy) in QUARTERS.items() if qx <= x < qx + 3 and qy <= y < qy + 3)


def quarter_cells(q: str) -> list[str]:
    """A quarter's nine holes, as it is read: its top row first, each from the left."""
    qx, qy = QUARTERS[q]
    return [hole(qx + i, qy + j) for j in (2, 1, 0) for i in range(3)]


def _lines() -> tuple[tuple[str, ...], ...]:
    out = []
    for y in range(6):
        out += [tuple(hole(x + k, y) for k in range(5)) for x in range(2)]
    for x in range(6):
        out += [tuple(hole(x, y + k) for k in range(5)) for y in range(2)]
    for x in range(2):
        for y in range(2):
            out += [tuple(hole(x + k, y + k) for k in range(5)), tuple(hole(x + k, y + 4 - k) for k in range(5))]
    return tuple(out)


LINES = _lines()                              # the 32 lines of five


def turned(cells: dict, quarter: str, way: str) -> dict:
    """The board with `quarter` turned a quarter turn `way`, clockwise or anticlockwise as the board is seen."""
    qx, qy = QUARTERS[quarter]
    out = {c: v for c, v in cells.items() if quarter_of(c) != quarter}
    for i in range(3):
        for j in range(3):
            v = cells.get(hole(qx + i, qy + j))
            if v is not None:
                ni, nj = (j, 2 - i) if way == "cw" else (2 - j, i)
                out[hole(qx + ni, qy + nj)] = v
    return out


def landed(cell: str, quarter: str, way: str) -> str:
    """Where a marble set in `cell` stands once `quarter` has turned `way`."""
    return next(iter(turned({cell: "x"}, quarter, way))) if quarter_of(cell) == quarter else cell


def fives(cells: dict, letter: str) -> list[tuple[str, ...]]:
    return [line for line in LINES if all(cells.get(c) == letter for c in line)]


def parse(move: str) -> dict:
    """A move as the score sheet writes it, read: its hole, the quarter and the way it turned, if one did, and
    whether it won."""
    won = move.endswith("#")
    parts = move.rstrip("#").split("-")
    return {"cell": parts[0], "quarter": parts[1] if len(parts) == 3 else None,
            "way": parts[2] if len(parts) == 3 else None, "won": won}


def placement(board: str) -> dict[str, str]:
    """The marbles and ghosts by hole, from the board's six rows: {"b5": "G", "d4": "W", ...}."""
    out = {}
    for row, text in enumerate(board.split("/")):
        for f, ch in enumerate(text):
            if ch != ".":
                out[f"{FILES[f]}{6 - row}"] = ch
    return out


def to_move(cells: dict, places: str, opens: str | None) -> str:
    """Whose turn it is: while the ghosts go down, the side that sets first and then the other; after them, the side
    the Arbiter drew to open when both have set as many marbles, else the other side."""
    ghosts = sum(1 for v in cells.values() if v == GHOST)
    if ghosts < 2 or opens not in SIDES:
        return places if ghosts == 0 else other(places)
    first = sum(1 for v in cells.values() if v == LETTER[opens])
    made = sum(1 for v in cells.values() if v in "WB")
    return opens if first == made - first else other(opens)


def turns(links, hole_: str) -> bool:
    """Whether `links` is a hole's eight turns, each [quarter, way, link] to its own move's ready-made issue: every
    quarter turned each way, once, in the order the board names them."""
    if not (isinstance(links, list) and len(links) == len(QUARTERS) * len(WAYS)):
        return False
    want = [(q, w) for q in QUARTERS for w in WAYS]
    for (q, w), turn in zip(want, links):
        if not (isinstance(turn, list) and len(turn) == 3 and turn[0] == q and turn[1] == w
                and is_text(turn[2], D.link(KIND, re.escape(f"{hole_}-{q}-{w}")))):
            return False
    return True


def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    board = d.get("board", "")
    if not is_text(board, BOARD):
        return [f"board {board!r} is not six rows of six W, B, G or dots, the top row first"]
    errors = []
    cells = placement(board)
    white = sum(1 for v in cells.values() if v == "W")
    black = sum(1 for v in cells.values() if v == "B")
    ghosts = sum(1 for v in cells.values() if v == GHOST)
    places, opens = d.get("places"), d.get("opens")
    if "light" in d:
        errors.append("light is gone: the house always plays White and GitHub Black, and places and opens name the"
                      " sides the Arbiter drew")
    if ghosts > 2:
        errors.append(f"board has {ghosts} ghosts: the Ghost Rule sets two, one for each side")
    elif ghosts < 2 and white + black:
        errors.append(f"board has {white + black} marble{'s' if white + black != 1 else ''} and {ghosts}"
                      f" ghost{'s' if ghosts != 1 else ''}: no marble"
                      " goes down until both ghosts are")
    if places not in SIDES:
        return errors + [f"places {places!r} is the side the Arbiter drew to set the first ghost: house, which plays"
                         " White, or github, which plays Black"]
    if ghosts == 2 and opens not in SIDES:
        return errors + [f"opens {opens!r} is the side the Arbiter drew to set the first marble once both ghosts were"
                         " down: house, which plays White, or github, which plays Black"]
    if ghosts < 2 and opens is not None:
        errors.append("opens: the Arbiter draws the side that sets the first marble once both ghosts are down")
    if ghosts == 2:
        first = sum(1 for v in cells.values() if v == LETTER[opens])
        if first - (white + black - first) not in (0, 1):
            errors.append(f"board has {white} White marble{'s' if white != 1 else ''} and {black} Black:"
                          f" {COLOUR[opens]} set first, the"
                          f" Arbiter having drawn {opens} to open, so it has as many as {COLOUR[other(opens)]} or"
                          " one more")
    turn = to_move(cells, places, opens)
    result = d.get("result")
    winner = result.get("winner") if isinstance(result, dict) else None
    line = d.get("line")
    if line and not (isinstance(line, list) and all(isinstance(c, str) for c in line)
                     and (tuple(line) in LINES or tuple(line[::-1]) in LINES)):
        errors.append(f"line {line!r} is five holes in a row, such as [a3, b3, c3, d3, e3]")
    elif line and not (winner in SIDES and all(cells.get(c) == LETTER[winner] for c in line)):
        errors.append("line: the winning line is the winner's five marbles, and only a won game has one")
    elif winner in SIDES and not line:
        errors.append("line: a won game names its winning line, its five holes")
    last = d.get("last")
    move = last.get("move") if isinstance(last, dict) else None
    if is_text(move, MOVE):
        mv = parse(move)
        if mv["quarter"] is None and not mv["won"]:
            if cells.get(mv["cell"]) != GHOST or white + black:
                errors.append(f"last: move {move!r} is a ghost's hole, and the last move is a ghost's only before the"
                              " first marble, on a hole the board has a ghost on")
        else:
            at = landed(mv["cell"], mv["quarter"], mv["way"]) if mv["quarter"] else mv["cell"]
            if cells.get(at) != LETTER[other(turn)]:
                errors.append(f"last: move {move!r} does not leave a marble of the side that moved last where its"
                              " marble lands")
    elif white + black:
        errors.append("last: a board with marbles on it names the last move")
    if ghosts < 2 and not d.get("alert") and not d.get("result"):
        errors.append(f"alert: while the ghosts go down, the plate says so: {SETTING}")
    elif ghosts == 2 and d.get("alert"):
        errors.append(f"alert: once both ghosts are down a turn calls nothing out, since a call to block would tell"
                      f" the side to move where to go; {SETTING!r} is for the ghosts alone")
    moved = SIDES if white + black else (places if ghosts == 1 else other(places))   # a turn can win for either

    def links(move) -> bool:
        """Once both ghosts are down, a marble's hole is its eight turns, a link each: the hole's own, whatever its
        notation says, which the check holds to a move still to play on its own. A ghost's hole is one link."""
        return isinstance(move[2], str) and turns(move[4], move[2].removesuffix("#"))

    return errors + D.check(d, KIND, MOVE, CODE, ENDS, moved, ALERTS, OFFER, ghost_row=True,
                            links=links if ghosts == 2 else None)


def state(d: dict) -> dict:
    """The board as the sheet draws it: the marbles and the ghosts, whose turn it is, the last move with the hole its
    marble went in, the quarter it turned and where it landed, the board as it stood before the turn, the winning
    line, the marbles each side has left, and the common state every game's sheet reads."""
    cells = placement(d["board"])
    places, opens = d["places"], d.get("opens")
    ghosts = sorted((c for c, v in cells.items() if v == GHOST), key=lambda c: (-xy(c)[1], xy(c)[0]))
    ghosting = len(ghosts) < 2
    turn = to_move(cells, places, opens)
    first = places if ghosting or opens not in SIDES else opens
    st = D.state(d, to_move=turn, opens=first)
    last = st["last"]
    before = dict(cells)
    if last:
        mv = parse(last["move"])
        if mv["quarter"] is None and not mv["won"]:
            side = places if len(ghosts) == 1 else other(places)
            last.update(cell=mv["cell"], landed=mv["cell"], quarter=None, way=None, turned=False, ghost=True,
                        number=GHOST, side=side, second=len(ghosts) == 2)
        else:
            did = mv["quarter"] is not None
            at = landed(mv["cell"], mv["quarter"], mv["way"]) if did else mv["cell"]
            if did:          # the board before the turn: the quarter turned back the other way
                before = turned(cells, mv["quarter"], "acw" if mv["way"] == "cw" else "cw")
            last.update(cell=mv["cell"], landed=at, quarter=mv["quarter"], way=mv["way"], turned=did, ghost=False,
                        number=sum(1 for v in cells.values() if v == LETTER[last["side"]]))
    left = {side: EACH - sum(1 for v in cells.values() if v == LETTER[side]) for side in SIDES}
    st.update(KIND=KIND, cells=cells, before=before, ghosts=ghosts, ghosting=ghosting, places=places,
              first_marble=opens if opens in SIDES else None, left=left, line=[str(c) for c in d.get("line") or []],
              stage="ghosts" if ghosting else "")
    return st


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = state(d)
    d.setdefault("title", f"Pentago: game {st['game']}, " + ("the ghosts" if st["ghosting"] else f"move {st['move']}"))
    who = f"@{OWNER} plays White and GitHub Black, under the Ghost Rule"   # the house's side first
    ghosts = " and ".join(st["ghosts"])
    head = f"Game {st['game']} of @{OWNER} against GitHub, {who}." + (f" Ghosts on {ghosts}." if ghosts else "")
    if st["last"]:
        words = st["last"]["words"]
        said = words[0].lower() + words[1:]
        by = (f", the Arbiter's move for {name(st['last']['side'])}" if st["last"]["by"] == "the Arbiter" else "")
        head += f" After {D.numbered(st)} {st['last']['move']}{by}: {said}."
    if st["result"]:
        w = st["result"]["winner"]
        how = {"five for both": "drawn, a turn making five for both sides",
               "a full board": "drawn on a full board"}
        turn = (f" {name(w)} won with five in a row, from {st['line'][0]} to {st['line'][-1]}." if w
                else f" The game was {how[st['result']['how']]}.")
        turn += f" Game {st['game'] + 1} opens {st['next']}." if st["next"] else ""
    elif st["ghosting"]:
        turn = (f" It is {name(st['to_move'])}'s turn to set a ghost"
                + (f", due by {st['due']}." if st["due"] else "."))
    else:
        drew = (f" The Arbiter drew {name(st['first_marble'])} to set the first marble."
                if not any(v in "WB" for v in st["cells"].values()) else "")
        turn = (f"{drew} It is {name(st['to_move'])}'s turn as {COLOUR[st['to_move']]}"
                + (f", due by {st['due']}." if st["due"] else "."))
    quarters = []
    for q in QUARTERS:
        held = [f"{'White' if st['cells'][c] == 'W' else 'Black' if st['cells'][c] == 'B' else 'a ghost'} on {c}"
                for c in quarter_cells(q) if c in st["cells"]]
        if held:
            quarters.append(f"the {QNAME[q]} quarter: " + ", ".join(held))
    said = "; ".join(quarters)
    d.setdefault("desc", head + turn + (f" {said[0].upper()}{said[1:]}." if said else " The board is empty."))
    return d
