# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Hall of Fame of all four games is drawn from: the record the profile's engines hand over, checked and read.

Every game on @tannergolden's profile, Chess, Checkers, Connect Four and Tic-Tac-Toe, writes the same element into
the page's settings after each move: `hall-of-fame`, recomputed from all four games' state. It carries the series of
each game, the leading winners across all four, and the leaderboard, and every field is checked before it is drawn,
since a login ends up in the README. A field YAML reads as something else, a number for a login or a list for a
count, is turned away like any other mistake, and every number has a ceiling the sheets have room to letter.

The data lists a player's wins one count to a game in tier order, Tic-Tac-Toe first (`GAMES`), as the engines have
always written them; everything a reader sees lists the games Chess first (`ORDER`), each count read by its game.

Its rows read as chess-hall's do, a list of wins in place of one count. A row may carry its player's account ID as
its fifth field, and a run reads each ID's account as it is now (`logins`, beside the winners' `names`), so a player
is shown and linked by the login their account has now, and one whose account is gone is left off the page, the rows
under them moving up. The engine hands over twice the rows the page has places for, so the places stay full.
"""
from __future__ import annotations

import re

from ..chess.game import (ACCOUNT, DATE, DAYS, DEPTH, ID, LEADERS, LOGIN, MOST, OWNER, PEOPLE, TALLY, account,
                          initials, named, shown)

# The four games in tier order, from a game a child solves to one nobody has: the order the data lists a player's
# wins in, one count to a game.
GAMES = ("tictactoe", "connectfour", "checkers", "chess")
# The same four in the order a reader meets them, everywhere the Hall lists them: its series, the wins by each winner,
# the leaderboard's columns and the words for anyone who cannot see it.
ORDER = ("chess", "checkers", "connectfour", "tictactoe")
TITLES = {"tictactoe": "Tic-Tac-Toe", "connectfour": "Connect Four", "checkers": "Checkers", "chess": "Chess"}
SERIES = ("games", "house", "github", "draws")  # a game's series: the games finished, each side's wins, the draws


def _number(value, low: int, high: int) -> bool:
    """Whether `value` is a whole number from `low` to `high`: an int, never a bool or text YAML read in its place."""
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def _text(value, shape: re.Pattern) -> bool:
    """Whether `value` is text of `shape`, never a number, a bool or a list YAML read in its place."""
    return isinstance(value, str) and shape.fullmatch(value) is not None


def _day(value) -> bool:
    """Whether `value` is a day as the sheets letter it, such as 18 Oct: a real day of a real month."""
    m = DATE.fullmatch(value) if isinstance(value, str) else None
    return m is not None and int(m[1]) <= DAYS.get(m[2].casefold(), 0)


def by_game(value) -> bool:
    """Whether `value` is a player's wins in each of the four games, in tier order: four counts up to `TALLY`."""
    return isinstance(value, list) and len(value) == len(GAMES) and all(_number(n, 0, TALLY) for n in value)


# --- the checks ----------------------------------------------------------------------------------------------------
def check(d: dict) -> list[str]:
    """What the Hall of Fame's data gets wrong, said precisely."""
    errors = check_series(d.get("series"))
    people = d.get("people") or []
    if not isinstance(people, list) or len(people) > PEOPLE * DEPTH:
        return errors + [f"people is a list of at most {PEOPLE * DEPTH} winners"]
    shaped = [isinstance(row, list) and len(row) in (4, 5) and _text(row[0], LOGIN) and by_game(row[1])
              and sum(row[1]) >= 1 and (row[2] == "" or _day(row[2])) and _number(row[3], 0, TALLY)
              and (len(row) == 4 or _number(row[4], 1, ACCOUNT)) for row in people]
    errors += [f"people: {row!r} is not a winner's login, their wins in each of the four games ({', '.join(GAMES)}),"
               " one at least, the day of the last, the games they played, and their account's ID if known"
               for row, fine in zip(people, shaped) if not fine]
    wins = [sum(row[1]) for row in people] if all(shaped) else []
    if wins != sorted(wins, reverse=True):
        errors.append("people: the winners are ranked by their wins in all four games, the most first")
    names = d.get("names") or {}
    if not isinstance(names, dict) or not all(_text(k, LOGIN) and named(v) for k, v in names.items()):
        errors.append("names gives a login its name: plain text without an @, at most 40 letters in capitals,"
                      " with something in it to see")
    logins = d.get("logins") or {}
    if not isinstance(logins, dict) or not all(_text(k, ID) and (v == "" or _text(v, LOGIN))
                                               for k, v in logins.items()):
        errors.append("logins gives an account's ID its login as it is now, or \"\" for an account that is gone")
    return errors + check_leaders(d.get("leaders") or [])


def check_series(series) -> list[str]:
    """What the series gets wrong: each of the four games' games finished, the house's wins, GitHub's and the draws,
    the three adding up to the first. Without a series, no game has finished yet."""
    if series is None:
        return []
    if not isinstance(series, dict) or set(series) != set(GAMES):
        return [f"series gives each of the four games, {', '.join(GAMES[:-1])} and {GAMES[-1]}, its games finished,"
                " the house's wins, GitHub's and the draws"]
    errors = []
    for game in GAMES:
        row = series[game]
        if not (isinstance(row, list) and len(row) == len(SERIES) and all(_number(n, 0, TALLY) for n in row)):
            errors.append(f"series: {game} {row!r} is not the games finished, the house's wins, GitHub's and the"
                          f" draws, each a count up to {TALLY:,}")
        elif sum(row[1:]) != row[0]:
            errors.append(f"series: {game}'s wins and draws add up to {sum(row[1:])} games, not the {row[0]}"
                          " finished")
    return errors


def check_leaders(leaders) -> list[str]:
    """What the leaderboard's rows get wrong: the house's own row first, then GitHub's players by their wins in all
    four games and then their moves, each a login with the moves and games they played across all four, their wins
    in each, and their account's ID if known."""
    if not isinstance(leaders, list) or len(leaders) > LEADERS * DEPTH + 1:
        return [f"leaders is @{OWNER}'s row, then at most {LEADERS * DEPTH} of GitHub's players"]
    errors = []
    for i, row in enumerate(leaders):
        if not (isinstance(row, list) and len(row) in (4, 5) and _text(row[0], LOGIN) and _number(row[1], 0, MOST)
                and _number(row[2], 0, TALLY) and by_game(row[3]) and sum(row[3]) <= row[2] <= row[1]
                and (len(row) == 4 or _number(row[4], 1, ACCOUNT))):
            errors.append(f"leaders: {row!r} is not a login, then the moves and games they played, their wins in each"
                          " of the four games, no more in all than their games, and their account's ID if known")
        elif (row[0].casefold() == OWNER) != (i == 0):
            errors.append(f"leaders: @{OWNER}'s row is the first, and the only one of theirs")
        elif i and not row[1]:
            errors.append(f"leaders: @{row[0]} is on it without a move")
    if errors:
        return errors
    ranks = [(-sum(row[3]), -row[1]) for row in leaders[1:]]
    return [] if ranks == sorted(ranks) else ["leaders: GitHub's players are ranked by their wins in all four games,"
                                              " then their moves"]


# --- what the sheets read ------------------------------------------------------------------------------------------
def state(d: dict) -> dict:
    """The Hall of Fame as the sheet draws it: each game's series and the totals across all four, its leading winners
    in order, each with their wins in every game; and its leaderboard as the README lists it. Each player is shown by
    the login their account has now (`shown`), with the account's ID when the row carries one. A player whose account
    is gone is left out of both, and the players under them move up into the places the page has: `PEOPLE` winners,
    and the house's row over `LEADERS` of GitHub's players."""
    names, logins = d.get("names") or {}, d.get("logins") or {}
    series = d.get("series") or {}
    games = {game: dict(zip(SERIES, series.get(game) or (0,) * len(SERIES))) for game in GAMES}
    totals = {key: sum(games[game][key] for game in GAMES) for key in SERIES}
    people = []
    for row in d.get("people") or []:
        login, (wins, last, played) = shown(row, logins), row[1:4]
        if not login:
            continue
        house = row[0].casefold() == OWNER
        name = names.get(login) or names.get(login.casefold()) or ""
        # a winner with no name on their profile is named by their login, and the line under it says their side
        people.append({"login": login, "name": f"@{OWNER.upper()}" if house else (name or f"@{login}").upper(),
                       "handle": "the house" if house else f"@{login}" if name else "github  ·  challenger",
                       "badge": f"@{login}", "wins": sum(wins),
                       "by_game": dict(zip(GAMES, wins)), "house": house, "initials": initials(name, login),
                       "last": last.upper(), "games": played, "id": account(row)})
    leaders = [{"login": login, "moves": row[1], "games": row[2], "wins": sum(row[3]),
                "by_game": dict(zip(GAMES, row[3])), "house": row[0].casefold() == OWNER, "id": account(row)}
               for row in d.get("leaders") or [] if (login := shown(row, logins))]
    return {"series": games, "totals": totals, "people": people[:PEOPLE], "leaders": leaders[:LEADERS + 1]}


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'s' if n != 1 else ''}"


def listed(words: list[str], last: str = "and") -> str:
    """Words as a sentence lists them: one alone, or the rest with commas between and `last` before the last."""
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + f" {last} " + words[-1]


def in_games(by: dict) -> str:
    """A winner's wins in words, game by game in the order a reader meets them, the games they have won in alone:
    5 in Chess and 4 in Tic-Tac-Toe."""
    return listed([f"{by[game]} in {TITLES[game]}" for game in ORDER if by[game]])


def describe(d: dict) -> dict:
    """The Hall's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    h = state(d)
    d.setdefault("title", "Hall of Fame: four games")
    total = h["totals"]
    titles = [TITLES[game] for game in ORDER]
    if not total["games"]:
        desc = (f"No game of @{OWNER} against GitHub has finished yet, in {listed(titles, 'or')}, so the podium waits"
                " for its first winner.")
    else:
        draws = total["draws"]
        drawn = "none were" if not draws else f"{draws} {'was' if draws == 1 else 'were'}"
        desc = (f"{plural(total['games'], 'game')} of @{OWNER} against GitHub, across {listed(titles)}: @{OWNER} won"
                f" {total['house']}, GitHub {total['github']}, and {drawn} drawn.")
        for game in ORDER:
            s = h["series"][game]
            desc += (f" {TITLES[game]}: {plural(s['games'], 'game')}, @{OWNER} {s['house']}, GitHub {s['github']},"
                     f" {s['draws']} drawn." if s["games"] else f" {TITLES[game]}: none finished yet.")
        if h["people"]:
            ranked = [f"{p['badge']} with {plural(p['wins'], 'win')} ({in_games(p['by_game'])})" for p in h["people"]]
            desc += " Ranked by wins: " + ", ".join(ranked) + "."
    d.setdefault("desc", desc)
    return d
