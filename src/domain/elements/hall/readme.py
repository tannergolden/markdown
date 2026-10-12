# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries under the Hall of Fame's sheet: a badge for each winner, and the leaderboard.

The names in a sheet cannot be clicked, so a row of badges follows it, one per winner it shows, each linking to that
player's profile; the leader's glints, with a still twin for anyone who asks for reduced motion. Then the
leaderboard, folded shut under one line as chess's is: the house's own row on top, then GitHub's leading players, the
first three with medals, each with a column of wins for every game, Chess first, headed by the game's two side signs,
the house's first, then the moves they played across all four and their wins in all; and under it, how a win counts.
Each player is linked by the login their account has now, and one whose account is gone is left out of both, the
players under them moving up.
"""
from __future__ import annotations

from html import escape

from .record import ORDER, OWNER, state

# Each game's two side signs, as every README line of the games writes them, the house's first: the white king and
# the black, the white man and the black, the white disc and the black, X and O. Together they head the game's column
# of wins.
SIGNS = {"chess": "♔♚", "checkers": "⛀⛂", "connectfour": "⚪⚫", "tictactoe": "❌⭕"}
HOUSE = "🏠"  # the house's own row, on top of everyone
MEDALS = ("🥇", "🥈", "🥉")
# How a win counts, under the leaderboard.
RULE = ("A win counts only for the player who makes the winning move: the checkmate in Chess, the move that leaves the"
        " other side no move in Checkers, the fourth disc in a row in Connect Four and the third mark in a row in"
        " Tic-Tac-Toe. A move the Arbiter plays, for either side, counts for nobody, and a draw is nobody's win.")


def badges(eid: str, d: dict, rel: str) -> str:
    """A badge per winner, each in a link to that player's profile by the login their account has now; the
    leader's glints, with a still twin for anyone who asks for reduced motion."""
    people = state(d)["people"]
    if not people:
        return ""
    lines = ['<div align="center">', ""]
    for i, p in enumerate(people):
        base = f"{rel}/{eid}-badge-{i + 1}"
        alt = f"#{i + 1} {p['badge']}, {p['wins']} win{'s' if p['wins'] != 1 else ''}"
        still = (f'<source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" '
                 f'srcset="{base}-still-dark.svg"><source media="(prefers-reduced-motion: reduce)" '
                 f'srcset="{base}-still-day.svg">') if i == 0 else ""
        lines.append(f'<a href="https://github.com/{p["login"]}"><picture>{still}<source media="(prefers-color-scheme: '
                     f'dark)" srcset="{base}-dark.svg"><img alt="{escape(alt)}" src="{base}-day.svg"></picture></a>')
    return "\n".join(lines + ["", "</div>"])


def leaderboard(d: dict) -> str:
    """The leaderboard, folded shut under one line: the house's own row on top, then GitHub's leading players by
    their wins in all four games and then their moves, each linking to their profile by the login their account has
    now, with their wins in each game, Chess first, their moves and their wins in all; under it, how a win counts."""
    rows = state(d)["leaders"]
    if not rows:
        return ""
    k = len(rows) - 1
    if k:
        line = (f"🏆 <b>Leaderboard</b> · @{OWNER} and GitHub's top {k if k > 1 else 'player'}"
                " · ranked by wins in all four games, then moves")
    else:
        line = f"🏆 <b>Leaderboard</b> · @{OWNER} · GitHub's players join with their first move"
    lines = ["|  | Player | " + " | ".join(SIGNS[game] for game in ORDER) + " | Moves | Wins |",
             "| :-: | :--- | " + " | ".join("--:" for _ in ORDER) + " | --: | --: |"]
    for i, r in enumerate(rows):
        place = HOUSE if r["house"] else MEDALS[i - 1] if i <= len(MEDALS) else str(i)
        cells = [f"[@{r['login']}](https://github.com/{r['login']})", *(f"{r['by_game'][game]:,}" for game in ORDER),
                 f"{r['moves']:,}", f"{r['wins']:,}"]
        lines.append(f"| {place} | " + " | ".join(f"**{c}**" if r["house"] else c for c in cells) + " |")
    return f"<details>\n<summary>{line}</summary>\n\n" + "\n".join(lines) + f"\n\n{RULE}\n\n</details>"
