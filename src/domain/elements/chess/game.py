# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the chess sheets are drawn from: the game as the profile's own engine hands it over, checked and read.

The game is played by @tannergolden's profile repository, which writes two elements into the page's settings
after every move: `chess`, the board as it stands, and `chess-hall`, the series and everyone who has won it.
Nothing here knows the rules. The position arrives as FEN and the moves in notation, each with the title and the
plain words the engine gave it, and every field is checked before it is drawn, since a move's title and a
player's login end up in the README.
"""
from __future__ import annotations

import re

# The one page the game is drawn on: it is @tannergolden's own, played from that profile and nowhere else.
OWNER = "tannergolden"
FILES = "abcdefgh"
NAMES = {"k": "king", "q": "queen", "r": "rook", "b": "bishop", "n": "knight", "p": "pawn"}
KINDS = ("king", "queen", "rook", "bishop", "knight", "pawn")
VALUE = {"queen": 9, "rook": 5, "bishop": 3, "knight": 3, "pawn": 1, "king": 0}
TAKEN = ("queen", "rook", "bishop", "knight", "pawn")  # the order a taken row lists them in
FEN = re.compile(r"(?:[pnbrqkPNBRQK1-8]{1,8}/){7}[pnbrqkPNBRQK1-8]{1,8} [wb] (?:-|[KQkq]{1,4}) (?:-|[a-h][36]) \d+ \d+")
SQUARE = re.compile(r"[a-h][1-8]")
SAN = re.compile(r"(?:O-O(?:-O)?|[KQRBN][a-h]?[1-8]?x?[a-h][1-8]|[a-h](?:x[a-h])?[1-8](?:=[QRBN])?)[+#]?")
# A move's link opens its ready-made issue in tannergolden/play, and nothing else: no space, bracket or quote.
LINK = re.compile(r"https://github\.com/tannergolden/play/issues/new\?template=move\.yml&title=chess%3A%20"
                  r"[a-h][1-8][a-h][1-8][qrbn]?%20%C2%B7%20game%20[1-9][0-9]{0,8}%20%C2%B7%20move%20[1-9][0-9]{0,8}")
# The README's own lines: one line each, nothing that opens HTML or breaks a table.
LINE = re.compile(r"[^<>|\n\r]{1,400}")
TITLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ,.'!-]{0,47}")
WORDS = re.compile(r"[A-Za-z][A-Za-z0-9 ,.'-]{0,79}")
EMOJI = re.compile("[←-⯿\U0001f000-\U0001faff‍️]{1,8}")
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
WHO = re.compile(r"@[A-Za-z0-9][A-Za-z0-9-]{0,38}|the Arbiter")
DATE = re.compile(r"[1-9][0-9]? [A-Za-z]{3}")  # 18 Oct
NAME = re.compile(r"[^<>|\n\r\[\]()`*_\\]{1,40}")
PEOPLE = 5  # the hall's places: a podium of three, and two more beside it


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


def _int(d: dict, key: str, low: int = 0) -> int:
    value = d.get(key, low)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= low else low


def turn_name(st: dict) -> str:
    """Whose turn it is, by name: GitHub's, or the house's."""
    return "GitHub" if st["to_move"] == "black" else f"@{OWNER}"


# --- the board ---------------------------------------------------------------------------------------------------
def check(d: dict) -> list[str]:
    """What the board's data gets wrong, said precisely."""
    errors = []
    fen = str(d.get("fen", ""))
    if not FEN.fullmatch(fen):
        return [f"fen {fen!r} is not a position in FEN"]
    pieces = list(placement(fen).values())
    if pieces.count("K") != 1 or pieces.count("k") != 1:
        errors.append("fen does not have one king a side")
    if d.get("check") and not SQUARE.fullmatch(str(d["check"])):
        errors.append(f"check {d['check']!r} is not a square, such as e8")
    if d.get("due") and not DATE.fullmatch(str(d["due"])):
        errors.append(f"due {d['due']!r} is not a day, such as 18 Oct")
    last = d.get("last")
    if last:
        if not isinstance(last, dict):
            errors.append("last is the last move: its san, from, to, piece, words, by and when")
        else:
            shapes = {"san": SAN, "from": SQUARE, "to": SQUARE, "words": WORDS, "by": WHO, "when": DATE}
            for key, shape in shapes.items():
                if not shape.fullmatch(str(last.get(key, ""))):
                    errors.append(f"last: {key} {last.get(key)!r} is not what a last move's {key} is")
            if last.get("piece") not in KINDS or (last.get("captured") or "") not in ("", *KINDS):
                errors.append("last: piece and captured each name a piece, such as knight")
    taken = d.get("taken")
    if taken is not None and (not isinstance(taken, dict) or set(taken) - {"white", "black"}
                              or not all(re.fullmatch(r"[qrbnp]{0,15}", str(v)) for v in taken.values())):
        errors.append("taken gives white and black each the letters of what it took, such as qnp")
    for row in d.get("history") or []:
        if not (isinstance(row, list) and len(row) == 4 and isinstance(row[0], int)
                and all(cell == "" or SAN.fullmatch(str(cell)) for cell in row[1:3])
                and (row[3] == "" or WHO.fullmatch(str(row[3])))):
            errors.append(f"history: {row!r} is not a row of a number, White's move, Black's and who chose it")
    for key in ("prompt", "note"):
        if d.get(key) and not LINE.fullmatch(str(d[key])):
            errors.append(f"{key} is one line of text, without <, > or |")
    moves = d.get("moves") or []
    if not isinstance(moves, list):
        return errors + ["moves is a list of each piece and its moves"]
    for group in moves:
        if not isinstance(group, dict) or group.get("piece") not in KINDS or not isinstance(group.get("list"), list):
            errors.append(f"moves: {group!r} is not a piece ({', '.join(KINDS)}) with a list of its moves")
            continue
        for move in group["list"]:
            if not (isinstance(move, list) and len(move) == 5 and EMOJI.fullmatch(str(move[0]))
                    and TITLE.fullmatch(str(move[1])) and SAN.fullmatch(str(move[2]))
                    and WORDS.fullmatch(str(move[3])) and LINK.fullmatch(str(move[4]))):
                errors.append(f"moves: {move!r} is not an emoji, a title, a move in SAN, its words and its link")
    return errors


def board_state(d: dict) -> dict:
    """The board as the sheet draws it: the position, the last move and what it took, whose turn and until when,
    what each side has taken, the latest moves, and how many have played for GitHub."""
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
    return {"fen": fen, "placement": placement(fen), "to_move": to_move, "last": last, "taken": took,
            "check": d.get("check") or None, "game": _int(d, "game", 1), "move": _int(d, "move", 1) or fullmove,
            "players": _int(d, "players"), "due": str(d.get("due") or ""), "history": history}


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
    turn = f" It is {turn_name(st)}'s turn" + (", in check" if st["check"] else "")
    turn += f", due by {st['due']}." if st["due"] else "."
    d.setdefault("desc", head + turn + " " + pieces_in_words(st["placement"]))
    return d


# --- the Hall of Fame ------------------------------------------------------------------------------------------------
def check_hall(d: dict) -> list[str]:
    """What the Hall of Fame's data gets wrong, said precisely."""
    errors = []
    counts = [d.get(key, 0) for key in ("games", "house", "world", "draws")]
    if not all(isinstance(n, int) and not isinstance(n, bool) and n >= 0 for n in counts):
        return ["games, house, world and draws are counts of games"]
    if sum(counts[1:]) != counts[0]:
        errors.append(f"house, world and draws add up to {sum(counts[1:])} games, not the {counts[0]} played")
    people = d.get("people") or []
    if not isinstance(people, list) or len(people) > PEOPLE:
        return errors + [f"people is a list of at most {PEOPLE} winners"]
    for row in people:
        if not (isinstance(row, list) and len(row) == 4 and LOGIN.fullmatch(str(row[0]))
                and isinstance(row[1], int) and row[1] >= 1 and (row[2] == "" or DATE.fullmatch(str(row[2])))
                and isinstance(row[3], int) and row[3] >= 0):
            errors.append(f"people: {row!r} is not a winner's login, wins, the day of the last and games played")
    names = d.get("names") or {}
    if not isinstance(names, dict) or not all(LOGIN.fullmatch(str(k)) and NAME.fullmatch(str(v))
                                              for k, v in names.items()):
        errors.append("names gives a login its name, in plain text")
    return errors


def initials(name: str, login: str) -> str:
    """Two letters for a winner's medallion: their name's, else their login's."""
    words = [w for w in re.split(r"[^A-Za-z0-9]+", name) if w]
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return (words[0] if words else login)[:2].upper()


def hall_state(d: dict) -> dict:
    """The Hall of Fame as the sheet draws it: the series between the house and GitHub, and its winners in order."""
    names = d.get("names") or {}
    people = []
    for login, wins, last, games in d.get("people") or []:
        house = login.casefold() == OWNER
        name = names.get(login) or names.get(login.casefold()) or ""
        people.append({"login": login, "name": f"@{OWNER.upper()}" if house else (name or f"@{login}").upper(),
                       "handle": "the house  ·  white" if house else f"@{login}", "badge": f"@{login}",
                       "wins": wins, "house": house, "initials": initials(name, login), "last": last.upper(),
                       "games": games})
    return {"games": _int(d, "games"), "house": _int(d, "house"), "world": _int(d, "world"),
            "draws": _int(d, "draws"), "people": people}


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
