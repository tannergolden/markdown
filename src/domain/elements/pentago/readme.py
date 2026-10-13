# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries under the Pentago sheet: every empty hole as a move with its eight turns, folded, then the
note.

A Pentago move is two choices, a hole for the marble and then a quarter to turn and which way, so the list is one row
for each empty hole, named for where it is and never for what it does ("Take the Centre of the Upper Left Quarter!"),
with its eight turns after it, each a link that opens its own ready-made issue: ↻ for a quarter turned clockwise and
↺ anticlockwise, and the quarter's initials. Under the Ghost Rule a ghost's hole is one choice, and its row one link.
The engine writes the names; this draws what goes under the sheet, as chess's does (`games.readme`). A turn with more
than ten holes is grouped by quarter, the board as it is read, as chess groups its moves by piece. The side to move is
signed with its marbles, ⚪ for the house's White and ⚫ for GitHub's Black, whichever side the Arbiter drew.
"""
from __future__ import annotations

from ..games import readme as R
from ..games.sides import GITHUB, HOUSE
from .game import QNAME, QUARTERS, quarter_of, state

UNIT = ("empty hole", "empty holes")
GHOSTS = ("hole for a ghost", "holes for a ghost")
SIGN = {HOUSE: "⚪", GITHUB: "⚫"}          # the house's first, as every pair of sides is said
ARROW = {"cw": "↻", "acw": "↺"}


def turned_table(moves: list) -> str:
    """The holes and their turns: each hole's name and notation, its words, and a link for each of its eight turns."""
    rows = ["|  | Hole | In words | Then turn |", "| :-: | :--- | :--- | :--- |"]
    for emoji, title, cell, words, links in moves:
        if isinstance(links, list):
            turns = " ".join(f"[{ARROW[w]}&#8202;{q.upper()}]({url})" for q, w, url in links)
        else:
            turns = f"[Play ↗]({links})"
        rows.append(f"| {emoji} | **{title}** `{cell}` | {words} | {turns} |")
    return "\n".join(rows)


def groups(moves: list) -> list[tuple[str, list]]:
    """The holes by quarter, each quarter's in the order the engine listed them, the board as it is read."""
    out = []
    for q in QUARTERS:
        rows = [move for move in moves if isinstance(move[2], str) and quarter_of(move[2]) == q]
        if rows:
            out.append((f"{QNAME[q].title()} Quarter", rows))
    return out


def text(d: dict) -> str:
    """What the README carries under the board's picture: every empty hole and its turns, folded, then the note."""
    st = state(d)
    return R.text(d, st, SIGN, GHOSTS if st["ghosting"] else UNIT, groups, table=turned_table)
