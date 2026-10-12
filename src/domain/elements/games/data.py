# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What every game's data is checked for, and the state every sheet reads from it.

The profile's own engine plays each game and writes what its sheet draws after every move, as it does for chess:
the game and move numbers, how many have played for GitHub, the day the move is due by, the last move in the game's
notation with its words and who played it when, the score sheet's latest rows, the turn's banner, a note, and every
legal move with an emoji, a title, its notation, its words and its link. Once a game is over its board stays up for
two days: then it carries how the game ended and the day the fresh board comes, and offers no move.

Nothing here knows a game's rules: a field is checked for its shape, as chess's are (a number is a number within
its ceiling and never a bool or text YAML read in its place, a day is a real day, a line of the README opens no
block of its own), since a title and a login end up in the README; the game's own module checks its board.
"""
from __future__ import annotations

import re

from ..chess.game import (EMOJI, MOST, TITLE, WHO, WORDS, check_end, check_lines, is_day, is_number, is_text)
from .sides import GITHUB, HOUSE

NUMBER = r"[1-9][0-9]{0,8}"


def link(kind: str, code: str) -> re.Pattern:
    """A move's link: it opens the move's ready-made issue in tannergolden/play, titled with the move's `code` as an
    issue names it, and nothing else."""
    return re.compile(r"https://github\.com/tannergolden/play/issues/new\?template=move\.yml&title=" + kind
                      + rf"%3A%20{code}%20%C2%B7%20game%20{NUMBER}%20%C2%B7%20move%20{NUMBER}")


def check(d: dict, kind: str, notation: re.Pattern, code: str, ends: dict[str, bool], moved: str,
          alerts: tuple[str, ...]) -> list[str]:
    """What the fields every game shares get wrong, said precisely: `notation` is the shape of the game's moves,
    `code` how an issue's title names one, `ends` how the game can end and whether each end has a winner, `moved`
    the side that made the last move, the only one that can have won, and `alerts` what its turn's plate can say."""
    errors = []
    for key, low in (("game", 1), ("move", 1), ("players", 0)):
        if key in d and not is_number(d[key], low, MOST):
            errors.append(f"{key} {d[key]!r} is not a number from {low} to {MOST:,}")
    if d.get("due") and not is_day(d["due"]):
        errors.append(f"due {d['due']!r} is not a day, such as 18 Oct")
    elif not d.get("due") and not d.get("result"):
        errors.append("due: a game under way says the day its move is due by, such as 18 Oct, its first move's too")
    if d.get("alert") and d["alert"] not in alerts:
        errors.append(f"alert {d['alert']!r} is not what this game's turn can say: {', '.join(alerts)}")
    elif d.get("alert") and d.get("result"):
        errors.append("alert: a finished board has nothing left to block or to take")
    last = d.get("last")
    if last:
        if not isinstance(last, dict):
            errors.append("last is the last move: its move, words, by and when")
        else:
            shapes = {"move": notation, "words": WORDS, "by": WHO}
            for key in (*shapes, "when"):
                if not (is_text(last.get(key), shapes[key]) if key in shapes else is_day(last.get(key))):
                    errors.append(f"last: {key} {last.get(key)!r} is not what a last move's {key} is")
    history = d.get("history")
    if history is not None and not isinstance(history, list):
        errors.append("history is a list of the score sheet's rows")
    for row in history if isinstance(history, list) else []:
        if not (isinstance(row, list) and len(row) == 4 and is_number(row[0], 1, MOST)
                and all(cell == "" or is_text(cell, notation) for cell in row[1:3])
                and (row[3] == "" or is_text(row[3], WHO))):
            errors.append(f"history: {row!r} is not a row of a move's number up to {MOST:,}, the opening side's"
                          " move, the reply and who chose it")
        elif row[2] and not row[1]:
            errors.append(f"history: {row!r} has the reply without the move it answers")
    errors += check_lines(d)
    moves = d.get("moves") or []
    if not isinstance(moves, list):
        return errors + ["moves is a list of every legal move"] + check_end(d, moved, ends, 0)
    shape = link(kind, code)
    for move in moves:
        if not (isinstance(move, list) and len(move) == 5 and is_text(move[0], EMOJI) and is_text(move[1], TITLE)
                and is_text(move[2], notation) and is_text(move[3], WORDS) and is_text(move[4], shape)):
            errors.append(f"moves: {move!r} is not an emoji, a title, a move, its words and its link")
    return errors + check_end(d, moved, ends, len(moves))


def number(d: dict, key: str, low: int = 0) -> int:
    v = d.get(key)
    return v if is_number(v, low, MOST) else low


def state(d: dict, *, to_move: str, opens: str) -> dict:
    """What every game's sheet reads: who opened, whose turn it is, the numbers, the clock, the last move as the
    engine wrote it, how the game ended and when the fresh board comes, and the score sheet's rows. The game's own
    state adds its board."""
    last = None
    if d.get("last"):
        last = dict(d["last"], side=GITHUB if to_move == HOUSE else HOUSE)
    result = {"winner": d["result"]["winner"], "how": d["result"]["how"]} if d.get("result") else None
    history = [(row[0], row[1], row[2], row[3]) for row in d.get("history") or []]
    return {"to_move": to_move, "opens": opens, "last": last, "result": result,
            "game": number(d, "game", 1), "move": number(d, "move", 1), "players": number(d, "players"),
            "due": str(d.get("due") or ""), "next": str(d.get("next") or "") if result else "",
            "alert": "" if result else str(d.get("alert") or ""), "history": history}


def numbered(st: dict) -> str:
    """The last move's number as a score sheet writes it: "3." for the opening side's move, "3..." for the reply."""
    last = st["last"]
    n = last.get("number") or st["move"]
    return f"{n}." if last["side"] == st["opens"] else f"{n}..."
