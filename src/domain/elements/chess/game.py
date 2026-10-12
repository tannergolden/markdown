# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the chess sheets are drawn from: the game as the profile's own engine hands it over, checked and read.

The game is played by @tannergolden's profile repository, which writes two elements into the page's settings
after every move: `chess`, the board as it stands, and `chess-hall`, the series and everyone who has won it.
Nothing here knows the rules. The position arrives as FEN and the moves in notation, each with the title and the
plain words the engine gave it, and every field is checked before it is drawn, since a move's title and a
player's login end up in the README. A field YAML reads as something else, a number for a name or a list for a
note, is turned away like any other mistake, and every number has a ceiling the sheets have room to letter.

A finished game keeps its final board up for two days before the fresh one comes. Its data then carries how it
ended (`result`: the winner, the house or GitHub, or none for a draw, and how) and the day the fresh board comes
(`next`), and offers no move: nothing can be played while the final board is up.

A row of the Hall of Fame may carry its player's account ID after its counts. A login can be given up and taken by
someone else, so a run reads each ID's account as it is now (`logins`, measured beside the winners' `names`), and
the row is shown and linked by that account's login. A player whose account is gone is left off the page, and the
rows under them move up: the engine hands over more rows than the page has places for, so the places stay full.

The checks of a field's shape (`is_number`, `is_text`, `is_day`), of the README's lines (`check_lines`) and of how
a game ended (`check_end`) are every game's on the profile, so the four are checked alike.
"""
from __future__ import annotations

import re
import unicodedata

from ...lettering import missing

# The one page the game is drawn on: it is @tannergolden's own, played from that profile and nowhere else.
OWNER = "tannergolden"
FILES = "abcdefgh"
NAMES = {"k": "king", "q": "queen", "r": "rook", "b": "bishop", "n": "knight", "p": "pawn"}
KINDS = ("king", "queen", "rook", "bishop", "knight", "pawn")
VALUE = {"queen": 9, "rook": 5, "bishop": 3, "knight": 3, "pawn": 1, "king": 0}
TAKEN = ("queen", "rook", "bishop", "knight", "pawn")  # the order a taken row lists them in
TOOK = re.compile(r"[qrbnp]{0,15}")  # what a side took, as the letters of the pieces
# The most each number may be, which the sheets have room to letter: a game, a move and its players up to nine digits;
# the move a position is on and a score sheet's row up to five; the Hall's tallies up to six; and an account's ID, as
# GitHub numbers its accounts, up to sixteen.
MOST, MOVES, TALLY, ACCOUNT = 999_999_999, 99_999, 999_999, 9_999_999_999_999_999
# A position: eight ranks of pieces and ASCII digits, each rank eight squares (`squares`), then the side to move,
# castling, en passant, the halfmove clock and the move it is on.
FEN = re.compile(r"(?:[pnbrqkPNBRQK1-8]{1,8}/){7}[pnbrqkPNBRQK1-8]{1,8} [wb] (?:-|[KQkq]{1,4}) (?:-|[a-h][36]) "
                 r"[0-9]+ [1-9][0-9]{0,4}")
SQUARE = re.compile(r"[a-h][1-8]")
SAN = re.compile(r"(?:O-O(?:-O)?|[KQRBN][a-h]?[1-8]?x?[a-h][1-8]|[a-h](?:x[a-h])?[1-8](?:=[QRBN])?)[+#]?")
# A move's link opens its ready-made issue in tannergolden/play, and nothing else: no space, bracket or quote.
LINK = re.compile(r"https://github\.com/tannergolden/play/issues/new\?template=move\.yml&title=chess%3A%20"
                  r"[a-h][1-8][a-h][1-8][qrbn]?%20%C2%B7%20game%20[1-9][0-9]{0,8}%20%C2%B7%20move%20[1-9][0-9]{0,8}")
# The README's own lines: one line each, nothing that opens HTML or breaks a table.
LINE = re.compile(r"[^<>|\n\r]{1,400}")
# Nor anything that starts a block of its own where the line is set: space before it, a fence, a heading, a quote, a
# list's item, a link's definition, or a rule, which under the banner's first line would make that line a heading.
BLOCK = re.compile(r"\s|```|~~~|#{1,6}(?:\s|$)|>|[-*+](?:\s|$)|[0-9]+[.)](?:\s|$)|\[[^\]]*\]:|[-=*_\s]+$")
# A move's title, set in bold in the README, which a space at either end would leave as plain asterisks.
TITLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9 ,.'!-]{0,46}[A-Za-z0-9,.'!-])?")
WORDS = re.compile(r"[A-Za-z][A-Za-z0-9 ,.'-]{0,79}")
EMOJI = re.compile("[←-⯿\U0001f000-\U0001faff‍️]{1,8}")
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
WHO = re.compile(r"@[A-Za-z0-9][A-Za-z0-9-]{0,38}|the Arbiter")
DATE = re.compile(r"([1-9][0-9]?) ([A-Za-z]{3})")  # 18 Oct, a real day of a real month (`DAYS`)
DAYS = {"jan": 31, "feb": 29, "mar": 31, "apr": 30, "may": 31, "jun": 30, "jul": 31, "aug": 31, "sep": 30, "oct": 31,
        "nov": 30, "dec": 31}
# A winner's name: plain text without an @, so it never passes for a login, and at most forty letters in capitals.
NAME = re.compile(r"[^<>|\n\r\[\]()`*_\\@]{1,40}")
ID = re.compile(r"[1-9][0-9]{0,15}")  # an account's ID as `logins` keys it
# The faces a winner's name is lettered in, in every tone: the standard theme's DejaVu Sans Bold and a print's Barlow
# Condensed Bold (`skins`).
LETTERED = ("sans-bold", "num")
PEOPLE = 5  # the hall's places: a podium of three, and two more beside it
LEADERS = 10  # the leaderboard's places for GitHub's players, under the house's own row
DEPTH = 2  # each list may run to twice its places, so the rows under a player whose account is gone fill theirs
# The two sides of every game on the profile, as a finished game's result names its winner: the house, @tannergolden,
# and GitHub, everyone else. In chess the house plays White.
HOUSE, GITHUB = "house", "github"
SIDES = (HOUSE, GITHUB)
# How a game of chess ends on the profile, and whether that end has a winner: a mate does; every draw is one that
# needs nobody to claim it, since nobody is there to.
ENDS = {"checkmate": True, "stalemate": False, "insufficient material": False, "fivefold repetition": False,
        "seventy-five moves": False, "dead position": False}


def placement(fen: str) -> dict[str, str]:
    """The pieces by square, from the FEN's first field: {"e1": "K", "e8": "k", ...}."""
    board = {}
    for row, text in enumerate(fen.split()[0].split("/")):
        f = 0
        for ch in text:
            if ch.isdigit():
                f += int(ch)
            else:
                board[f"{FILES[f]}{8 - row}"] = ch
                f += 1
    return board


def captured(fen: str) -> tuple[str, str]:
    """What each side has taken, counted from what is missing: (White's takings, Black's), as piece letters.
    The engine says what was taken; this is what a board says without it."""
    full = {"q": 1, "r": 2, "b": 2, "n": 2, "p": 8}
    left = list(placement(fen).values())
    white_took = "".join(k * max(0, n - left.count(k)) for k, n in full.items())
    black_took = "".join(k.upper() * max(0, n - left.count(k.upper())) for k, n in full.items())
    return white_took, black_took


def squares(fen: str) -> bool:
    """Whether every rank of the FEN's first field holds exactly eight squares, its digits counting empty ones."""
    return all(sum(int(ch) if ch in "12345678" else 1 for ch in rank) == 8 for rank in fen.split()[0].split("/"))


def is_number(value, low: int, high: int) -> bool:
    """Whether `value` is a whole number from `low` to `high`: an int, never a bool or text YAML read in its place."""
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def is_text(value, shape: re.Pattern) -> bool:
    """Whether `value` is text of `shape`, never a number, a bool or a list YAML read in its place."""
    return isinstance(value, str) and shape.fullmatch(value) is not None


def is_day(value) -> bool:
    """Whether `value` is a day as the sheets letter it, such as 18 Oct: a real day of a real month."""
    m = DATE.fullmatch(value) if isinstance(value, str) else None
    return m is not None and int(m[1]) <= DAYS.get(m[2].casefold(), 0)


def _int(d: dict, key: str, default: int, low: int = 0, high: int = MOST) -> int:
    value = d.get(key)
    return value if is_number(value, low, high) else default


def named(name) -> bool:
    """Whether `name` is a winner's name the sheets can set: plain text, at most forty letters once in capitals (an ß
    is two), with something in it to see."""
    return (is_text(name, NAME) and len(name.upper()) <= 40
            and any(unicodedata.category(ch)[0] in "LNPS" for ch in name))


def letterable(name: str) -> bool:
    """Whether every tone letters `name` as it is: each of its capitals a glyph of every face a winner's name is
    lettered in, so none is drawn as a question mark. Needs the outlines a run hands the lettering first."""
    return not any(missing(name.upper(), face) for face in LETTERED)


def turn_name(st: dict) -> str:
    """Whose turn it is, by name: GitHub's, or the house's."""
    return "GitHub" if st["to_move"] == "black" else f"@{OWNER}"


def called(side: str) -> str:
    """A side by name, as every game says it: GitHub, or the house's own login."""
    return "GitHub" if side == GITHUB else f"@{OWNER}"


def check_lines(d: dict) -> list[str]:
    """What the README's own lines get wrong: the turn's banner (`prompt`) and the `note` are each one line of
    text, which opens no block of its own where it is set and shows no image."""
    errors = []
    for key in ("prompt", "note"):
        value = d.get(key)
        if value and not is_text(value, LINE):
            errors.append(f"{key} is one line of text, without <, > or |")
        elif value and BLOCK.match(value):
            errors.append(f"{key} {value!r} would open a block of its own in the README, such as a heading, a list, a"
                          " rule or a fence: it starts with a word or an emoji")
        elif value and "![" in value:
            errors.append(f"{key} shows an image: a line of the README carries words and links alone")
    return errors


def check_end(d: dict, moved: str, ends: dict[str, bool], offered: int) -> list[str]:
    """What a board's `result` and `next` get wrong. How a game ended is one of `ends`, each with a winner or
    drawn, and only the side that made the last move (`moved`) can have won it; the day the fresh board comes is a
    finished board's alone; and a finished board offers nothing to play, where its data lists `offered` moves."""
    errors = []
    result = d.get("result")
    if result:
        if not (isinstance(result, dict) and set(result) == {"winner", "how"} and result["winner"] in (*SIDES, None)
                and isinstance(result["how"], str) and result["how"] in ends):
            errors.append("result is how the game ended: its winner (house, github, or null for a draw) and how: "
                          + ", ".join(ends))
        elif ends[result["how"]] and result["winner"] is None:
            errors.append(f"result: a game ended by {result['how']} has a winner")
        elif not ends[result["how"]] and result["winner"] is not None:
            errors.append(f"result: a game ended by {result['how']} is drawn, its winner null")
        elif result["winner"] not in (None, moved):
            errors.append(f"result: the winner is the side that made the last move, {moved}")
        if offered:
            errors.append("moves: a finished board offers no move, since nothing is played while it is up")
    nxt = d.get("next")
    if nxt and not is_day(nxt):
        errors.append(f"next {nxt!r} is not a day, such as 14 Oct")
    elif nxt and not result:
        errors.append("next is the day a finished game's fresh board comes: a game under way has none")
    return errors


# --- the board ---------------------------------------------------------------------------------------------------
def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    errors = []
    fen = d.get("fen", "")
    if not is_text(fen, FEN):
        return [f"fen {fen!r} is not a position in FEN, on a move from 1 to {MOVES:,}"]
    if not squares(fen):
        return [f"fen {fen!r} does not have eight squares on every rank"]
    board, white = placement(fen), fen.split()[1] == "w"
    pieces = list(board.values())
    if pieces.count("K") != 1 or pieces.count("k") != 1:
        errors.append("fen does not have one king a side")
    for key, low in (("game", 1), ("move", 1), ("players", 0)):
        if key in d and not is_number(d[key], low, MOST):
            errors.append(f"{key} {d[key]!r} is not a number from {low} to {MOST:,}")
    if d.get("check") and not (is_text(d["check"], SQUARE) and board.get(d["check"]) == ("K" if white else "k")):
        errors.append(f"check {d['check']!r} is not the square of the king to move, such as e8")
    if d.get("due") and not is_day(d["due"]):
        errors.append(f"due {d['due']!r} is not a day, such as 18 Oct")
    last = d.get("last")
    if last:
        if not isinstance(last, dict):
            errors.append("last is the last move: its san, from, to, piece, words, by and when")
        else:
            shapes = {"san": SAN, "from": SQUARE, "to": SQUARE, "words": WORDS, "by": WHO}
            for key in (*shapes, "when"):
                if not (is_text(last.get(key), shapes[key]) if key in shapes else is_day(last.get(key))):
                    errors.append(f"last: {key} {last.get(key)!r} is not what a last move's {key} is")
            if last.get("piece") not in KINDS or (last.get("captured") or "") not in ("", *KINDS):
                errors.append("last: piece and captured each name a piece, such as knight")
            if white and fen.split()[5] == "1":
                errors.append("last: a board before White's first move has no last move")
    taken = d.get("taken")
    if taken is not None and (not isinstance(taken, dict) or set(taken) - {"white", "black"}
                              or not all(is_text(v, TOOK) for v in taken.values())):
        errors.append("taken gives white and black each the letters of what it took, such as qnp")
    history = d.get("history")
    if history is not None and not isinstance(history, list):
        errors.append("history is a list of the score sheet's rows")
    for row in history if isinstance(history, list) else []:
        if not (isinstance(row, list) and len(row) == 4 and is_number(row[0], 1, MOVES)
                and all(cell == "" or is_text(cell, SAN) for cell in row[1:3])
                and (row[3] == "" or is_text(row[3], WHO))):
            errors.append(f"history: {row!r} is not a row of a move's number up to {MOVES:,}, White's move, Black's"
                          " and who chose it")
        elif row[2] and not row[1]:
            errors.append(f"history: {row!r} has Black's move without White's")
    errors += check_lines(d)
    moves = d.get("moves") or []
    if not isinstance(moves, list):
        return errors + ["moves is a list of each piece and its moves"] + check_end(d, GITHUB if white else HOUSE,
                                                                                    ENDS, 0)
    for group in moves:
        if not isinstance(group, dict) or group.get("piece") not in KINDS or not isinstance(group.get("list"), list):
            errors.append(f"moves: {group!r} is not a piece ({', '.join(KINDS)}) with a list of its moves")
            continue
        for move in group["list"]:
            if not (isinstance(move, list) and len(move) == 5 and is_text(move[0], EMOJI) and is_text(move[1], TITLE)
                    and is_text(move[2], SAN) and is_text(move[3], WORDS) and is_text(move[4], LINK)):
                errors.append(f"moves: {move!r} is not an emoji, a title, a move in SAN, its words and its link")
    offered = sum(len(g["list"]) for g in moves if isinstance(g, dict) and isinstance(g.get("list"), list))
    # the side that made the last move: Black, when it is White's turn
    return errors + check_end(d, GITHUB if white else HOUSE, ENDS, offered)


def board_state(d: dict) -> dict:
    """The board as the sheet draws it: the position, the last move and what it took, whose turn and until when,
    what each side has taken, the latest moves, and how many have played for GitHub; once the game is over, how it
    ended and the day the fresh board comes."""
    fen = d["fen"]
    turn, fullmove = fen.split()[1], int(fen.split()[5])
    to_move = "white" if turn == "w" else "black"
    last = None
    if d.get("last"):
        raw = d["last"]
        last = {"san": raw["san"], "side": "black" if to_move == "white" else "white",
                "number": fullmove - 1 if to_move == "white" else fullmove, "from": raw["from"], "to": raw["to"],
                "piece": raw["piece"], "captured": raw.get("captured") or None, "words": raw["words"],
                "by": raw["by"], "when": raw["when"]}
    if isinstance(d.get("taken"), dict):
        took = {side: [NAMES[k] for k in str(d["taken"].get(side, ""))] for side in ("white", "black")}
    else:
        white, black = captured(fen)
        took = {"white": [NAMES[k] for k in white], "black": [NAMES[k.lower()] for k in black]}
    for side in took:
        took[side].sort(key=TAKEN.index)
    history = [(row[0], row[1], row[2], row[3], False) for row in d.get("history") or []]
    result = {"winner": d["result"]["winner"], "how": d["result"]["how"]} if d.get("result") else None
    # without a move of its own, the board is on the move its position says
    return {"fen": fen, "placement": placement(fen), "to_move": to_move, "last": last, "taken": took,
            "check": d.get("check") or None, "game": _int(d, "game", 1, 1), "move": _int(d, "move", fullmove, 1),
            "players": _int(d, "players", 0), "due": str(d.get("due") or ""), "history": history,
            "result": result, "next": str(d.get("next") or "") if result else ""}


def pieces_in_words(board: dict[str, str]) -> str:
    """Every piece on the board, side by side, for anyone who cannot see it."""
    out = []
    for side, upper in (("White", True), ("Black", False)):
        parts = []
        for letter in "kqrbnp":
            squares = sorted(sq for sq, piece in board.items() if piece == (letter.upper() if upper else letter))
            if squares:
                name = NAMES[letter] + ("s" if len(squares) > 1 else "")
                said = " and ".join(squares) if len(squares) < 3 else ", ".join(squares[:-1]) + " and " + squares[-1]
                parts.append(f"{name} {said}")
        out.append(f"{side}: " + "; ".join(parts))
    return ". ".join(out) + "."


def describe(d: dict) -> dict:
    """The board's title and description, for the file and for anyone who cannot see it."""
    d = dict(d)
    if check(d):
        return d
    st = board_state(d)
    d.setdefault("title", f"Chess: game {st['game']}, move {st['move']}")
    if st["last"]:
        last = st["last"]
        num = f"{last['number']}." if last["side"] == "white" else f"{last['number']}..."
        said = last["words"][0].lower() + last["words"][1:]
        head = f"Game {st['game']} of @{OWNER} against GitHub, after {num} {last['san']}: {said}."
    else:
        head = f"Game {st['game']} of @{OWNER} against GitHub, before its first move."
    if st["result"]:
        turn = ended(st)
    else:
        turn = f" It is {turn_name(st)}'s turn" + (", in check" if st["check"] else "")
        turn += f", due by {st['due']}." if st["due"] else "."
    d.setdefault("desc", head + turn + " " + pieces_in_words(st["placement"]))
    return d


def ended(st: dict) -> str:
    """How a finished game ended, and when the fresh board comes, as every game's description says it."""
    winner, how = st["result"]["winner"], st["result"]["how"]
    said = f" {called(winner)} won: {how}." if winner else f" The game was drawn: {how}."
    return said + (f" Game {st['game'] + 1} opens {st['next']}." if st["next"] else "")


# --- the Hall of Fame ------------------------------------------------------------------------------------------------
def check_hall(d: dict) -> list[str]:
    """What the Hall of Fame's data gets wrong, said precisely."""
    errors = []
    counts = [d.get(key, 0) for key in ("games", "house", "world", "draws")]
    if not all(is_number(n, 0, TALLY) for n in counts):
        return [f"games, house, world and draws are counts of games, up to {TALLY:,}"]
    if sum(counts[1:]) != counts[0]:
        errors.append(f"house, world and draws add up to {sum(counts[1:])} games, not the {counts[0]} played")
    people = d.get("people") or []
    if not isinstance(people, list) or len(people) > PEOPLE * DEPTH:
        return errors + [f"people is a list of at most {PEOPLE * DEPTH} winners"]
    shaped = [isinstance(row, list) and len(row) in (4, 5) and is_text(row[0], LOGIN) and is_number(row[1], 1, TALLY)
              and (row[2] == "" or is_day(row[2])) and is_number(row[3], 0, TALLY)
              and (len(row) == 4 or is_number(row[4], 1, ACCOUNT)) for row in people]
    errors += [f"people: {row!r} is not a winner's login, wins, the day of the last and games played, and their"
               " account's ID if known" for row, fine in zip(people, shaped) if not fine]
    wins = [row[1] for row in people] if all(shaped) else []
    if wins != sorted(wins, reverse=True):
        errors.append("people: the winners are ranked by their wins, the most first")
    names = d.get("names") or {}
    if not isinstance(names, dict) or not all(is_text(k, LOGIN) and named(v) for k, v in names.items()):
        errors.append("names gives a login its name: plain text without an @, at most 40 letters in capitals,"
                      " with something in it to see")
    logins = d.get("logins") or {}
    if not isinstance(logins, dict) or not all(is_text(k, ID) and (v == "" or is_text(v, LOGIN))
                                               for k, v in logins.items()):
        errors.append("logins gives an account's ID its login as it is now, or \"\" for an account that is gone")
    return errors + check_leaders(d.get("leaders") or [])


def check_leaders(leaders) -> list[str]:
    """What the leaderboard's rows get wrong: the house's own row first, then GitHub's players by their wins and
    then their moves, each a login with the moves, wins and games they played, and their account's ID if known."""
    if not isinstance(leaders, list) or len(leaders) > LEADERS * DEPTH + 1:
        return [f"leaders is @{OWNER}'s row, then at most {LEADERS * DEPTH} of GitHub's players"]
    errors = []
    for i, row in enumerate(leaders):
        if not (isinstance(row, list) and len(row) in (4, 5) and is_text(row[0], LOGIN)
                and all(is_number(n, 0, MOST) for n in row[1:4]) and row[2] <= row[3] <= row[1]
                and (len(row) == 4 or is_number(row[4], 1, ACCOUNT))):
            errors.append(f"leaders: {row!r} is not a login, then the moves, wins and games they played, and their"
                          " account's ID if known")
        elif (row[0].casefold() == OWNER) != (i == 0):
            errors.append(f"leaders: @{OWNER}'s row is the first, and the only one of theirs")
        elif i and not row[1]:
            errors.append(f"leaders: @{row[0]} is on it without a move")
    if errors:
        return errors
    ranks = [(-row[2], -row[1]) for row in leaders[1:]]
    return [] if ranks == sorted(ranks) else ["leaders: GitHub's players are ranked by their wins, then their moves"]


def account(row: list) -> int | None:
    """The ID of the account a row of the Hall is for, which the row carries after its counts; None without one."""
    uid = row[4] if len(row) > 4 else None
    return uid if is_number(uid, 1, ACCOUNT) else None


def shown(row: list, logins: dict) -> str:
    """The login a row of the Hall is shown by: for a row with its account's ID, the login that account has now, as
    a run read it into `logins`, or "" when GitHub finds no account by that ID any more, and the row is left out.
    The house's row, a row without an ID and one whose ID no run has read yet are shown by their own login."""
    login, uid = row[0], account(row)
    if login.casefold() == OWNER or uid is None or str(uid) not in logins:
        return login
    return logins[str(uid)]


def initials(name: str, login: str) -> str:
    """Two letters for a winner's medallion: their name's, else their login's. A name's words are split on what is
    neither a letter nor a digit in any script, so Élodie Durand's are ÉD."""
    words = [w for w in re.split(r"[\W_]+", name) if w]
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return (words[0] if words else login)[:2].upper()


def hall_state(d: dict) -> dict:
    """The Hall of Fame as the sheet draws it: the series between the house and GitHub, and its leading winners in
    order; and its leaderboard as the README lists it. Each player is shown by the login their account has now
    (`shown`), with the account's ID when the row carries one. A player whose account is gone is left out of both,
    and the players under them move up into the places the page has: `PEOPLE` winners, and the house's row over
    `LEADERS` of GitHub's players."""
    names, logins = d.get("names") or {}, d.get("logins") or {}
    people = []
    for row in d.get("people") or []:
        login, (wins, last, games) = shown(row, logins), row[1:4]
        if not login:
            continue
        house = row[0].casefold() == OWNER
        name = names.get(login) or names.get(login.casefold()) or ""
        # a winner with no name on their profile is named by their login, and the line under it says their side
        people.append({"login": login, "name": f"@{OWNER.upper()}" if house else (name or f"@{login}").upper(),
                       "handle": "the house  ·  white" if house else f"@{login}" if name else "github  ·  black",
                       "badge": f"@{login}",
                       "wins": wins, "house": house, "initials": initials(name, login), "last": last.upper(),
                       "games": games, "id": account(row)})
    leaders = [{"login": login, "moves": row[1], "wins": row[2], "games": row[3], "house": row[0].casefold() == OWNER,
                "id": account(row)} for row in d.get("leaders") or [] if (login := shown(row, logins))]
    return {"games": _int(d, "games", 0, high=TALLY), "house": _int(d, "house", 0, high=TALLY),
            "world": _int(d, "world", 0, high=TALLY), "draws": _int(d, "draws", 0, high=TALLY),
            "people": people[:PEOPLE], "leaders": leaders[:LEADERS + 1]}


def describe_hall(d: dict) -> dict:
    d = dict(d)
    if check_hall(d):
        return d
    h = hall_state(d)
    d.setdefault("title", "Chess: Hall of Fame")
    if not h["games"]:
        desc = f"No game of @{OWNER} against GitHub has finished yet, so the podium waits for its first winner."
    else:
        games = f"{h['games']} game{'s' if h['games'] != 1 else ''}"
        drawn = "none were" if not h["draws"] else f"{h['draws']} {'was' if h['draws'] == 1 else 'were'}"
        desc = (f"{games} of @{OWNER} against GitHub: @{OWNER} won {h['house']}, GitHub {h['world']}, and {drawn}"
                " drawn.")
        if h["people"]:
            ranked = [f"{p['badge']} with {p['wins']} win{'s' if p['wins'] != 1 else ''}" for p in h["people"]]
            desc += " Ranked by wins: " + ", ".join(ranked) + "."
    d.setdefault("desc", desc)
    return d
