# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries under a game's sheet, as it does under chess's: every legal move, folded shut under one line
saying whose they are and how many, then the note.

An image cannot be clicked cell by cell, so each move is a row of its emoji, a title in the game's own voice, its
notation, the move in plain words and a link that opens its ready-made issue, none of them saying what the move would do
to the game. No banner goes over the picture: the sheet itself says whose turn it is and by when, and once the game is
over, who won and when the fresh board comes, so a finished board's block is its picture and its note, with no move to
play. The block folds the game under its name (`data.fold`). A turn with more than ten moves is grouped, as chess groups
its moves by piece, when the game says how (`groups`).
"""
from __future__ import annotations

from typing import Callable

from ..chess.game import OWNER
from ..chess.readme import FEW, table
from .sides import GITHUB


def move_list(d: dict, st: dict, sign: dict, unit: tuple[str, str],
              groups: Callable[[list], list[tuple[str, list]]] | None = None,
              table: Callable[[list], str] = table) -> str:
    """Every legal move, folded shut under the line that says whose turn it is and how many it has: `sign` is each
    side's mark, `unit` what a move is called, one and many ("open cell", "open cells"). Past ten, `groups` sorts
    the moves into named groups, each folded open under its own line, as chess sorts its moves by piece. A game
    whose move is two choices sets its own `table`, its second choices linked in each row."""
    moves = d.get("moves") or []
    if not moves or st["result"]:
        return ""
    n = len(moves)
    count = f"{n} {unit[0] if n == 1 else unit[1]}"
    side = st["to_move"]
    if side == GITHUB:
        line = f"{sign[side]} <b>GitHub's Turn</b> · {count} · open to choose one"
    else:
        line = f"{sign[side]} <b>@{OWNER}'s Turn</b> · {count} · only @{OWNER} can play these"
    if n <= FEW or groups is None:
        inside = table(moves)
    else:
        inside = "\n\n".join(f"<details open>\n<summary>{sign[side]} {title} · {len(rows)}"
                             f" move{'s' if len(rows) != 1 else ''}</summary>\n\n{table(rows)}\n\n</details>"
                             for title, rows in groups(moves))
    return f"<details>\n<summary>{line}</summary>\n\n{inside}\n\n</details>"


def text(d: dict, st: dict, sign: dict, unit: tuple[str, str],
         groups: Callable[[list], list[tuple[str, list]]] | None = None,
         table: Callable[[list], str] = table) -> str:
    """What the README carries under the sheet's picture: every legal move and the note, or once the game is over
    the note alone."""
    return "\n\n".join(part for part in (move_list(d, st, sign, unit, groups, table), d.get("note") or "") if part)
