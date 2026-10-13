# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Replays: a finished game on @tannergolden's profile, played again move by move on its own board, looping.

  check(facts)                                  what the facts get wrong, said precisely; none when they are right
  draw(facts, tone, theme, faces, gone)         one file: the replay by `theme` day or dark, in the print `tone`

A game won by a person's own move gets a replay, which tannergolden/play keeps and posts on the winning move's issue.
The profile's engine writes what each turn did (`check` says the shape), and this draws it: the profile's board in
the profile's frame, every turn played with the README's own last-move motion (`chess`, `checkers`, `pentago`,
`tictac`), the panel following the game turn by turn, and the finale, the winner ringed and the losers fading, all on
one loop (`sheet`, `clock`). Each player is drawn as a halftone of their avatar, made from a small grey bitmap of it
(`portrait`). A replay is drawn in a print: a page in a theme with no replay look of its own, the standard theme, a
holiday's set or a collection's design, as the profile's Chessmen is, has its replay in blackprint.
It is drawn for that profile alone, and only from what its engine wrote.
"""
from __future__ import annotations

import datetime as dt
import re

from ... import prints
from ..chess import motion as CM
from ..chess.game import OWNER
from ..chess.skins import Print as ChessPrint
from ..checkers.skins import Print as CheckersPrint
from ..pentago.skins import Print as PentagoPrint
from ..tictac.skins import Print as TicTacPrint
from .checkers import Checkers
from .chess import Chess
from .pentago import Pentago
from .portrait import Faces
from .sheet import H, N, PX0, W, X0, Y0, Panel, curtain, plan
from .tictac import TicTac

__all__ = ["FALLBACK", "GAMES", "VERSION", "check", "draw", "tone_of"]

VERSION = 1                     # the facts' shape this reads, as the profile's engine writes it
FALLBACK = "blackprint"         # the print a replay is drawn in when the page's theme has no replay look
GAMES = {"chess": (Chess, ChessPrint), "checkers": (Checkers, CheckersPrint), "pentago": (Pentago, PentagoPrint),
         "tictac": (TicTac, TicTacPrint)}
WINS = {"chess": "checkmate", "checkers": "no move left", "pentago": "five in a row", "tictac": "three boards in a row"}
SIDES = ("house", "github")
MOST = 999_999_999
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
DAY = re.compile(r"[1-9][0-9]? (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)")
MOMENT = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
WORDS = re.compile(r"[^\x00-\x1f\x7f<>&]{1,120}")
SQUARE = re.compile(r"[a-h][1-8]")
HOLE = re.compile(r"[a-f][1-6]")
CELL = re.compile(r"[a-i][1-9]")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def tone_of(theme: str) -> str:
    """The print a replay is drawn in: the page's own theme when it is a print, else blackprint."""
    return theme if theme in prints.PRINTS else FALLBACK


def _count(v, low=0, high=MOST) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and low <= v <= high


def _text(v, shape: re.Pattern) -> bool:
    return isinstance(v, str) and bool(shape.fullmatch(v))


def _ply(kind: str, i: int, p) -> list[str]:
    """What one turn's facts get wrong."""
    at = f"plies[{i}]"
    if not isinstance(p, dict):
        return [f"{at} is not a turn's facts"]
    errors = []
    if p.get("side") not in SIDES:
        errors.append(f"{at}: side {p.get('side')!r} is house or github")
    for key in ("notation", "move", "words"):
        if not _text(p.get(key), WORDS):
            errors.append(f"{at}: {key} {p.get(key)!r} is a line of up to 120 letters")
    if isinstance(p.get("notation"), str) and " " not in p["notation"]:
        errors.append(f"{at}: notation {p['notation']!r} is the turn's number, then its move")
    by, by_id = p.get("by"), p.get("by_id")
    if not ((by is None and by_id is None) or (_text(by, LOGIN) and _count(by_id, 1, 10 ** 16))):
        errors.append(f"{at}: by and by_id are who played it, a login and an account ID, or both null for the Arbiter")
    if not _text(p.get("when"), DAY):
        errors.append(f"{at}: when {p.get('when')!r} is a day, such as 14 Oct")
    if kind == "chess":
        if not (_text(p.get("from"), SQUARE) and _text(p.get("to"), SQUARE)):
            errors.append(f"{at}: from and to are the squares the piece moved between")
        if not _text(p.get("piece"), re.compile(r"[KQRBNPkqrbnp]")):
            errors.append(f"{at}: piece {p.get('piece')!r} is the piece that moved, as a FEN letters it")
        for key in ("taken_at", "check"):
            if p.get(key) is not None and not _text(p.get(key), SQUARE):
                errors.append(f"{at}: {key} {p.get(key)!r} is a square, or null")
        rook = p.get("rook")
        if rook is not None and not (isinstance(rook, list) and len(rook) == 2 and all(_text(r, SQUARE) for r in rook)):
            errors.append(f"{at}: rook is a castling rook's two squares, or null")
        if p.get("promotion") not in (None, "q", "r", "b", "n"):
            errors.append(f"{at}: promotion {p.get('promotion')!r} is q, r, b, n or null")
    elif kind == "checkers":
        path, caps = p.get("path"), p.get("captures")
        if not (isinstance(path, list) and len(path) >= 2 and all(_count(q, 1, 32) for q in path)):
            errors.append(f"{at}: path is every square the piece stood on, 1 to 32")
        if not (isinstance(caps, list) and all(_count(q, 1, 32) for q in caps)):
            errors.append(f"{at}: captures are the squares of the men it took")
        elif isinstance(path, list) and caps and len(caps) != len(path) - 1:
            errors.append(f"{at}: a jump takes one man a hop")
        if not isinstance(p.get("crowns"), bool):
            errors.append(f"{at}: crowns says whether the man was crowned")
        if p.get("piece") not in ("d", "l", "D", "L"):
            errors.append(f"{at}: piece {p.get('piece')!r} is d, l, D or L")
    elif kind == "pentago":
        if not _text(p.get("cell"), HOLE):
            errors.append(f"{at}: cell {p.get('cell')!r} is a hole, a1 to f6")
        if not p.get("ghost"):
            if p.get("quarter") not in ("ul", "ur", "ll", "lr") or p.get("way") not in ("cw", "acw"):
                errors.append(f"{at}: quarter and way are the quarter turned and which way")
            if not isinstance(p.get("unturned"), bool):
                errors.append(f"{at}: unturned says whether the marble made five before any turn")
    elif kind == "tictac":
        if not _text(p.get("cell"), CELL):
            errors.append(f"{at}: cell {p.get('cell')!r} is a square, a1 to i9")
        if p.get("mark") not in ("X", "O", "G"):
            errors.append(f"{at}: mark {p.get('mark')!r} is X, O or G for a ghost")
    return errors


def check(f) -> list[str]:
    """What a replay's facts get wrong, said precisely: none when they can be drawn."""
    if not isinstance(f, dict):
        return ["the facts are a map of the finished game"]
    if f.get("replay") != VERSION:
        return [f"replay {f.get('replay')!r}: these are version {VERSION}'s facts, as the profile's engine writes them"]
    kind = f.get("kind")
    if kind not in GAMES:
        return [f"kind {kind!r} is one of {', '.join(GAMES)}"]
    errors = []
    if not _count(f.get("game"), 1):
        errors.append(f"game {f.get('game')!r} is a number from 1")
    if f.get("winner") not in SIDES:
        errors.append(f"winner {f.get('winner')!r} is house or github: a replay is a game a side won")
    if not (_text(f.get("by"), LOGIN) and _count(f.get("by_id"), 1, 10 ** 16)):
        errors.append("by and by_id are who made the winning move: a login and an account ID")
    if f.get("issue") is not None and not _count(f.get("issue"), 1, 10 ** 16):
        errors.append(f"issue {f.get('issue')!r} is the winning move's issue, or null")
    if f.get("reason") != WINS[kind]:
        errors.append(f"reason {f.get('reason')!r}: a game of {kind} is won by {WINS[kind]}")
    for key in ("started", "ended"):
        if not _text(f.get(key), MOMENT):
            errors.append(f"{key} {f.get(key)!r} is a moment, such as 2026-10-15T01:00:00Z")
    if kind in ("pentago", "tictac"):
        for key in ("places", "opens"):
            if f.get(key) not in SIDES:
                errors.append(f"{key} {f.get(key)!r} is the side the Arbiter drew: house or github")
    players = f.get("players")
    if not (isinstance(players, list) and all(isinstance(p, dict) and _text(p.get("player"), LOGIN)
                                               and _count(p.get("player_id"), 1, 10 ** 16)
                                               and _count(p.get("moves"), 1) for p in players)):
        errors.append("players are GitHub's players, each {player, player_id, moves}")
    if not _count(f.get("house_moves"), 0):
        errors.append("house_moves is a count")
    plies = f.get("plies")
    if not (isinstance(plies, list) and plies):
        return errors + ["plies are the game's turns, from the first"]
    if len(plies) > 2000:
        return errors + ["plies: no game of the profile's runs to 2000 turns"]
    for i, p in enumerate(plies):
        errors += _ply(kind, i, p)
    if errors:
        return errors
    if plies[-1]["side"] != f["winner"] or plies[-1]["by"] != f["by"]:
        errors.append("plies: the last turn is the winning move, the winner's own")
    if kind in ("pentago", "tictac"):
        ghosts = [p for p in plies[:2] if p.get("ghost") or p.get("mark") == "G"]
        if len(ghosts) != 2 or any(p.get("ghost") or p.get("mark") == "G" for p in plies[2:]):
            errors.append("plies: under the Ghost Rule the first two turns are the ghosts, and no other is")
    return errors


def _day(stamp: str) -> str:
    moment = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return f"{moment.day} {MONTHS[moment.month - 1]} {moment.year}"


def prepared(f: dict) -> dict:
    """The facts with what the finale says worked out: the day the game ended, the losing side's moves, and the
    days it ran over."""
    f = dict(f)
    f["ended_day"] = _day(f["ended"])
    f["loser_moves"] = (f["house_moves"] if f["winner"] == "github" else sum(p["moves"] for p in f["players"]))
    first, last = f["plies"][0]["when"], f["plies"][-1]["when"]
    f["span"] = first if first == last else f"{first} to {last}"
    return f


def draw(f: dict, tone: str, theme: str, faces: dict | None = None, gone: frozenset = frozenset()) -> str:
    """One file: the replay of a finished game, by `theme` day or dark, in the print `tone` (blackprint when it is
    none). `faces` are each player's grey bitmap by account ID, from `portrait.read`; `gone` the IDs whose accounts
    are gone, drawn with no face and no name."""
    errors = check(f)
    if errors:
        raise ValueError("; ".join(errors))
    with CM.at_rest(True):      # every motion in a replay is its own, on its one loop: none of the README's opening
        return _drawn(f, tone, theme, faces or {}, frozenset(gone))


def _drawn(f: dict, tone: str, theme: str, faces: dict, gone: frozenset) -> str:
    game, Skin = GAMES[f["kind"]]
    sk = Skin(theme, tone_of(tone))
    f = prepared(f)
    pl = plan(game.durations(f["plies"]))
    winner = f"@{OWNER}" if f["winner"] == "house" else ("a deleted account" if f["by_id"] in gone else f"@{f['by']}")
    title = f"Replay of {game.LABEL.title()} game {f['game']}: {winner} wins with {f['plies'][-1]['notation']}"
    desc = (f"Every move of game {f['game']} of {game.LABEL.title()} on @{OWNER}'s profile replayed on the board, who "
            f"played each, and the finale: {winner} wins by {f['reason']}.")
    cv = sk.new(W, H, title, desc, f"replay {f['kind']} wide", "")
    sk.frame(cv, W, H, game.LABEL, game.band(sk), f"game {f['game']}  ·  replay", f"@{OWNER} vs. github",
             plain=[sk.board_room(X0, Y0, N / 8)])
    layer = curtain(pl)
    game.board(cv, sk, pl, f, layer)
    cv.add(sk.vrule(PX0 - 16, Y0, Y0 + N))
    Panel(cv, sk, pl, f, game, Faces(cv, sk, faces, gone), game.matchup(f)).draw(layer)
    return cv.svg()
