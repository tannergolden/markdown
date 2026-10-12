# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries round a game's sheet, as it does round chess's: the turn's banner above the picture, and
under it every legal move, folded shut under one line saying whose they are and how many, then the note.

An image cannot be clicked cell by cell, so each move is a row of its emoji, a title in the game's own voice, its
notation, what it does in plain words and a link that opens its ready-made issue. The banner is a tip on GitHub's
turn, a caution on the house's, and once the game is over, the result as an important note; a finished board's
block is that banner, its board and its note, with no move to play. A turn with more than ten moves is grouped, as
chess groups its moves by piece, when the game says how (`groups`).
"""
from __future__ import annotations

from typing import Callable

from ..chess.game import OWNER
from ..chess.readme import FEW, table
from .sides import GITHUB


def banner(d: dict, st: dict) -> str:
    """The turn's banner: GitHub's turn as a tip, the house's as a caution, a finished game as an important note."""
    if not d.get("prompt"):
        return ""
    kind = "IMPORTANT" if st["result"] else "TIP" if st["to_move"] == GITHUB else "CAUTION"
    return f"> [!{kind}]\n> {d['prompt']}"


def move_list(d: dict, st: dict, sign: dict, unit: tuple[str, str],
              groups: Callable[[list], list[tuple[str, list]]] | None = None) -> str:
    """Every legal move, folded shut under the line that says whose turn it is and how many it has: `sign` is each
    side's mark, `unit` what a move is called, one and many ("open cell", "open cells"). Past ten, `groups` sorts
    the moves into named groups, each folded open under its own line, as chess sorts its moves by piece."""
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
         groups: Callable[[list], list[tuple[str, list]]] | None = None) -> tuple[str, str]:
    """The sheet's README block round its picture: what goes above it, and what goes under it: every legal move and
    the note, or once the game is over the note alone."""
    below = [part for part in (move_list(d, st, sign, unit, groups), d.get("note") or "") if part]
    return banner(d, st), "\n\n".join(below)
