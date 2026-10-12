# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the README carries round the chess sheets: the banner, every legal move, the badges and the leaderboard.

An image cannot be clicked square by square, so the board's README block puts the game's words round it: the
turn's banner above, green on GitHub's turn and red on the house's; under it every legal move as a row of its
emoji, its title and notation, what it does in plain words, and a link that opens its ready-made issue, folded
shut under one line saying whose moves they are and how many; then the note. A turn with more than ten moves is
grouped by piece, each group named for as many of the pieces as have a move in it. The Hall of Fame's block follows
its sheet with a row of badges, one per winner, each linking to that player's profile, since the names in a sheet
cannot be clicked either; then the leaderboard, folded shut like the moves: the house's own moves, wins and games on
top, and GitHub's leading players under it. Each player is linked by the login their account has now, and one whose
account is gone is not linked at all, since the login it had may be someone else's.
"""
from __future__ import annotations

import re
from html import escape

from .game import OWNER, hall_state

SIGN = {"black": {"king": "♚", "queen": "♛", "rook": "♜", "bishop": "♝", "knight": "♞", "pawn": "♟"},
        "white": {"king": "♔", "queen": "♕", "rook": "♖", "bishop": "♗", "knight": "♘", "pawn": "♙"}}
GROUP = {"king": "King", "queen": "Queen", "rook": "Rook", "bishop": "Bishop", "knight": "Knight", "pawn": "Pawn"}
FROM = re.compile(r"title=chess%3A%20([a-h][1-8])")  # the square a move's ready-made title moves its piece from
FEW = 10  # a list this long or shorter is one table; a longer one is grouped by piece
MEDALS = ("🥇", "🥈", "🥉")


def to_move(d: dict) -> str:
    return "white" if str(d.get("fen", "")).split()[1:2] == ["w"] else "black"


def banner(d: dict) -> str:
    """The turn's banner: GitHub's turn as a tip, the house's as a caution."""
    if not d.get("prompt"):
        return ""
    return f"> [!{'TIP' if to_move(d) == 'black' else 'CAUTION'}]\n> {d['prompt']}"


def table(moves: list) -> str:
    rows = ["|  | Move | What it does | Play |", "| :-: | :--- | :--- | :-: |"]
    rows += [f"| {emoji} | **{title}** `{san}` | {words} | [Play ↗]({url}) |" for emoji, title, san, words, url in moves]
    return "\n".join(rows)


def group_name(piece: str, moves: list) -> str:
    """A group's name, for one piece or for several: as many as there are squares its moves leave from, which each
    move's link names. There is one king, so it is the King whatever it can do."""
    pieces = {m[1] for m in (FROM.search(move[4]) for move in moves) if m}
    return GROUP[piece] + ("s" if piece != "king" and len(pieces) > 1 else "")


def move_list(d: dict) -> str:
    """Every legal move, folded shut under the line that says whose turn it is and how many moves it has."""
    groups = [g for g in d.get("moves") or [] if g.get("list")]
    n = sum(len(g["list"]) for g in groups)
    if not n:
        return ""
    side = to_move(d)
    count = f"{n} legal move{'s' if n != 1 else ''}"
    if side == "black":
        line = f"{SIGN['black']['king']} <b>GitHub's Turn</b> · {count} · open to choose one"
    else:
        line = f"{SIGN['white']['king']} <b>@{OWNER}'s Turn</b> · {count} · only @{OWNER} can play these"
    if n <= FEW:
        inside = table([move for g in groups for move in g["list"]])
    else:
        parts = []
        for g in groups:
            k = len(g["list"])
            parts.append(f"<details open>\n<summary>{SIGN[side][g['piece']]} {group_name(g['piece'], g['list'])} ·"
                         f" {k} move{'s' if k != 1 else ''}</summary>\n\n{table(g['list'])}\n\n</details>")
        inside = "\n\n".join(parts)
    return f"<details>\n<summary>{line}</summary>\n\n{inside}\n\n</details>"


def text(d: dict) -> tuple[str, str]:
    """The board's README block round its picture: what goes above it, and what goes under it."""
    below = [part for part in (move_list(d), d.get("note") or "") if part]
    return banner(d), "\n\n".join(below)


def badges(eid: str, d: dict, rel: str) -> str:
    """A badge per winner, each in a link to that player's profile, by the login their account has now, and unlinked
    when it is gone; the leader's glints, with a still twin for anyone who asks for reduced motion."""
    people = hall_state(d)["people"]
    if not people:
        return ""
    lines = ['<div align="center">', ""]
    for i, p in enumerate(people):
        base = f"{rel}/{eid}-badge-{i + 1}"
        alt = f"#{i + 1} {p['badge']}, {p['wins']} win{'s' if p['wins'] != 1 else ''}"
        still = (f'<source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" '
                 f'srcset="{base}-still-dark.svg"><source media="(prefers-reduced-motion: reduce)" '
                 f'srcset="{base}-still-day.svg">') if i == 0 else ""
        pic = (f'<picture>{still}<source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg"><img '
               f'alt="{escape(alt)}" src="{base}-day.svg"></picture>')
        lines.append(f'<a href="https://github.com/{p["login"]}">{pic}</a>' if p["linked"] else pic)
    return "\n".join(lines + ["", "</div>"])


def leaderboard(d: dict) -> str:
    """The leaderboard, folded shut under one line: the house's own row on top, then GitHub's leading players by
    their wins and then their moves, each linking to their profile by the login their account has now, or unlinked
    when it is gone."""
    rows = hall_state(d)["leaders"]
    if not rows:
        return ""
    k = len(rows) - 1
    if k:
        line = (f"🏆 <b>Leaderboard</b> · @{OWNER} and GitHub's top {k if k > 1 else 'player'}"
                " · ranked by wins, then moves")
    else:
        line = f"🏆 <b>Leaderboard</b> · @{OWNER} · GitHub's players join with their first move"
    lines = ["|  | Player | Moves | Wins | Games |", "| :-: | :--- | --: | --: | --: |"]
    for i, r in enumerate(rows):
        place = SIGN["white"]["king"] if r["house"] else MEDALS[i - 1] if i <= len(MEDALS) else str(i)
        who = f"[@{r['login']}](https://github.com/{r['login']})" if r["linked"] else f"@{r['login']}"
        cells = [who, f"{r['moves']:,}", f"{r['wins']:,}", f"{r['games']:,}"]
        lines.append(f"| {place} | " + " | ".join(f"**{c}**" if r["house"] else c for c in cells) + " |")
    rule = ("A win is a mating move of one's own; a move or a mate the Arbiter plays, for either side, counts for"
            " nobody.")
    return f"<details>\n<summary>{line}</summary>\n\n" + "\n".join(lines) + f"\n\n{rule}\n\n</details>"
