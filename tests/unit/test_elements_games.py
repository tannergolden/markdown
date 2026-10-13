# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games beside chess on @tannergolden's profile: Tic-Tac, Pentago and Checkers, drawn as chess is, in the
standard theme and every print, and nowhere but that profile.

Each side's colour is fixed: the house always plays X in Tic-Tac and White in Pentago and Checkers, GitHub always O,
or Black. Tic-Tac and Pentago open under the Ghost Rule: the Arbiter draws the side that places the first ghost, each
side locks a square, or sets a marble that is nobody's, and then the Arbiter draws the side that moves first. So each
is held to its boards both ways round at every stage: a fresh board, one ghost down, both ghosts down with either side
drawn to open, a turn of each side's, and its finished boards, kept up for two days with the result on the plate and
nothing left to play. GitHub opens Checkers, since Black moves first.

Every sample of Tic-Tac and Pentago is a board the profile's own engine set out, playing whole games, its list of
moves cut to a few, and no sheet says what a move would do. In Tic-Tac's game 9 GitHub is sent to the lower right
board, where three of its four squares win the game: the sheet brackets that board, since the rules send the mark
there, and singles out no square in it; GitHub then won the game there. In game 10 the house may play any open board,
two of its twenty-eight squares winning the game. The house won game 8 across the middle row of boards, and game 7
was drawn with no line of three boards left for either side. In Pentago's game 4 GitHub can make five on e5 before any
quarter turns, and any other marble followed by a clockwise turn of the upper right quarter makes five for the house
alone; in game 7 the house can make five on c1 with a clockwise turn of the lower right quarter, and any marble
followed by a clockwise turn of the upper right one hands GitHub five. The house won game 3 with a turn, GitHub won
game 6 with a marble that made five on its own, the house's own turn made five for GitHub alone in game 2, and games 1
and 8 were drawn, on a full board and with five for both. Checkers' GitHub's turn must jump after the house's jump
back, which the rules make it do and its sheet says, and its crowned board is the house's double jump that crowns a
White king on Black's back row."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support

from domain.canvas import BUDGET, lint
from domain.elements import checkers as CK
from domain.elements import data as ED
from domain.elements import draw as E
from domain.elements import pentago as PG
from domain.elements import tictac as TT
from domain.elements.games import sheet as GS
from domain.elements.games.skin import Print as GamePrint
from domain.elements.games.skin import Standard as GameStandard
from domain.lettering import Lettering
from domain.prints import PRINTS, STANDARD
from domain.standard import pieces as P

support.install()
DASHES = ("–", "—", "―")
TONES = (STANDARD, *sorted(PRINTS))
NOTE = "The first move to arrive is the one played."
# Every turn a Pentago hole is offered with, in the order the engine links them: each quarter, clockwise and then
# anticlockwise.
TURNS = [(q, w) for q in ("ul", "ur", "ll", "lr") for w in ("cw", "acw")]
# The engine's notes under a board, a sentence at a time as it writes them: who may play the turn, and the rules.
ANYONE = "Anyone but @tannergolden can play on this turn, and the first pick in is played."
ONLY = "Only @tannergolden can play on this turn: a pick from anyone else is turned away with a comment on its issue."
TT_OPENING = ("@tannergolden always plays X and GitHub O. Under the Ghost Rule each side first locks a square with a "
              "ghost, and then the Arbiter draws who makes the first mark.")
TT_RULES = ("Where a mark goes in its board sends the other side to the board in that place, three in a row wins a "
            "board, and three boards in a row wins the game; once neither side can win three boards in a row, it is a "
            "draw.")
PG_OPENING = ("@tannergolden always plays White and GitHub Black. Under the Ghost Rule each side first sets a ghost, a "
              "marble that is nobody's, and then the Arbiter draws who sets the first marble.")
PG_RULES = ("A move sets a marble, then turns any quarter a quarter turn; five in a row wins, for the other side if "
            "the turn makes five for it alone, and five for both or a full board is a draw.")


def link(kind: str, code: str, game: int, ply: int) -> str:
    """A move's link: its ready-made issue in tannergolden/play, titled with the move and the ply it answers."""
    return (f"https://github.com/tannergolden/play/issues/new?template=move.yml&title={kind}%3A%20{code}"
            f"%20%C2%B7%20game%20{game}%20%C2%B7%20move%20{ply}")


def row(kind: str, emoji: str, title: str, move: str, words: str, game: int, ply: int, code: str = "") -> list:
    return [emoji, title, move, words, link(kind, code or move.rstrip("+#").lstrip("XO"), game, ply)]


def hole(emoji: str, title: str, cell: str, words: str, game: int, ply: int) -> list:
    """A Pentago hole as the engine lists it once both ghosts are down: its emoji, title, hole and words, and its
    eight turns, each linked to its own move's ready-made issue."""
    return [emoji, title, cell, words, [[q, w, link("pentago", f"{cell}-{q}-{w}", game, ply)] for q, w in TURNS]]


def over(kind: str, game: int, day: str, at: str, why: str = "") -> str:
    """A finished board's note, as the engine writes it: when the next game opens, and where every game is kept."""
    return (f"Game {game} is over, and its final board stays up for two days: game {game + 1} opens {day}, {at} EST, "
            f"and nothing can be played until then. {why}{' ' if why else ''}Every finished game is kept as a "
            f"[record](https://github.com/tannergolden/tannergolden/tree/HEAD/.github/{kind}/games).")


# --------------------------------------------------------------------------- the engine's long lists
SPOT = TT.game.SQUARE           # where a square stands in its board, or a hole in its quarter: the same nine names
EVERY_SQUARE = " ".join(f"{f}{r}" for r in range(9, 0, -1) for f in "abcdefghi")
EVERY_HOLE = " ".join(f"{f}{r}" for r in range(6, 0, -1) for f in "abcdef")


def titled(verb: str, spot: str, where: str) -> str:
    """A move's title as the engine writes it, every word capitalized but `the` and `of`."""
    words = f"{verb} the {spot} of the {where}".split()
    return " ".join(w if w in ("the", "of") else w[0].upper() + w[1:] for w in words) + "!"


def squares(mark: str, cells: str, game: int, ply: int) -> list:
    """Every square of `cells` as the engine lists it, for a mark, X or O, or for a ghost where `mark` is empty: its
    emoji, title and words say where it is, never what it does."""
    out = []
    for cell in cells.split():
        spot, board = SPOT[TT.game.spot_of(cell)], f"{TT.game.PLACE[TT.game.board_of(cell)]} board"
        if not mark:
            out.append(row("tictac", "👻", titled("lock", spot, board), cell,
                           f"A ghost locks the {spot} of the {board}", game, ply))
            continue
        emoji = "🔳" if spot == "centre" else "📐" if spot.endswith("corner") else "📏"
        out.append(row("tictac", emoji, titled("take", spot, board), mark + cell,
                       f"{mark} takes the {spot} of the {board}", game, ply))
    return out


def holes(colour: str, cells: str, game: int, ply: int) -> list:
    """Every hole of `cells` as the engine lists it, for a marble, white or black, with its eight turns, or for a ghost
    where `colour` is empty, with its one link."""
    out = []
    for cell in cells.split():
        q = PG.game.quarter_of(cell)
        (x, y), (qx, qy) = PG.game.xy(cell), PG.game.QUARTERS[q]
        spot, quarter = SPOT[(x - qx, y - qy)], f"{PG.game.QNAME[q]} quarter"
        if not colour:
            out.append(row("pentago", "👻", titled("ghost", spot, quarter), cell,
                           f"A ghost on {cell}, the {spot} of the {quarter}", game, ply))
            continue
        out.append(hole("⚪" if colour == "white" else "⚫", titled("take", spot, quarter), cell,
                        f"A {colour} marble on {cell}, then a quarter turns", game, ply))
    return out


# --------------------------------------------------------------------------- Tic-Tac
# Game 11, fresh: the Arbiter drew GitHub to place the first ghost, and anyone but the house may choose its square.
TT_FRESH = {
    "kind": "tictac", "places": "github", "game": 11, "move": 1, "players": 0,
    "board": "........./........./........./........./........./........./........./........./.........",
    "due": "20 Oct", "alert": "place a ghost",
    "history": [["G", "", "", ""]],
    "moves": [row("tictac", "👻", "Lock the Upper Left Corner of the Upper Left Board!",
                  "a9", "A ghost locks the upper left corner of the upper left board", 11, 1),
              row("tictac", "👻", "Lock the Top Edge of the Upper Left Board!",
                  "b9", "A ghost locks the top edge of the upper left board", 11, 1),
              row("tictac", "👻", "Lock the Upper Right Corner of the Upper Left Board!",
                  "c9", "A ghost locks the upper right corner of the upper left board", 11, 1)],
    "note": f"{TT_OPENING} {ANYONE} The ghost is due by 20 Oct, 07:21 EST, or the Arbiter places one at random."}
# GitHub's ghost locks d6, and it is the house's turn to lock a square of its own.
TT_GHOST = {
    "kind": "tictac", "places": "github", "game": 11, "move": 1, "players": 1,
    "board": "........./........./........./...G...../........./........./........./........./.........",
    "due": "21 Oct", "alert": "place a ghost",
    "history": [["G", "d6", "", "@hollyfenwick"]],
    "last": {"move": "d6", "words": "A ghost locks the upper left corner of the centre board", "by": "@hollyfenwick",
             "when": "14 Oct"},
    "moves": [row("tictac", "👻", "Lock the Upper Left Corner of the Upper Left Board!",
                  "a9", "A ghost locks the upper left corner of the upper left board", 11, 2),
              row("tictac", "👻", "Lock the Top Edge of the Upper Left Board!",
                  "b9", "A ghost locks the top edge of the upper left board", 11, 2),
              row("tictac", "👻", "Lock the Upper Right Corner of the Upper Left Board!",
                  "c9", "A ghost locks the upper right corner of the upper left board", 11, 2)],
    "note": f"{TT_OPENING} {ONLY} The ghost is due by 21 Oct, 02:21 EST, or the Arbiter places one at random."}
# Both ghosts down, and the Arbiter drew the house to make the first mark, in any board.
TT_GHOSTS = {
    "kind": "tictac", "places": "github", "opens": "house", "game": 11, "move": 1, "players": 1,
    "board": "........./.......G./........./...G...../........./........./........./........./.........",
    "due": "21 Oct", "alert": "any board",
    "history": [["G", "d6", "h8", "@hollyfenwick"], [1, "", "", ""]],
    "last": {"move": "h8", "words": "A ghost locks the centre of the upper right board", "by": "@tannergolden",
             "when": "14 Oct"},
    "moves": [row("tictac", "📐", "Take the Upper Left Corner of the Upper Left Board!",
                  "Xa9", "X takes the upper left corner of the upper left board", 11, 3),
              row("tictac", "📏", "Take the Top Edge of the Upper Left Board!",
                  "Xb9", "X takes the top edge of the upper left board", 11, 3),
              row("tictac", "📐", "Take the Upper Right Corner of the Upper Left Board!",
                  "Xc9", "X takes the upper right corner of the upper left board", 11, 3)],
    "note": f"{TT_OPENING} {ONLY} The move is due by 21 Oct, 14:21 EST, or the Arbiter plays a random legal move."}
# Game 12 the other way round: the house was drawn to place first and GitHub to make the first mark.
TT_GHOSTS_GITHUB = {
    "kind": "tictac", "places": "house", "opens": "github", "game": 12, "move": 1, "players": 1,
    "board": "........./........./.......G./G......../........./........./........./........./.........",
    "due": "21 Oct", "alert": "any board",
    "history": [["G", "h7", "a6", "@hollyfenwick"], [1, "", "", ""]],
    "last": {"move": "a6", "words": "A ghost locks the upper left corner of the left board", "by": "@hollyfenwick",
             "when": "14 Oct"},
    "moves": [row("tictac", "📐", "Take the Upper Left Corner of the Upper Left Board!",
                  "Oa9", "O takes the upper left corner of the upper left board", 12, 3),
              row("tictac", "📏", "Take the Top Edge of the Upper Left Board!",
                  "Ob9", "O takes the top edge of the upper left board", 12, 3),
              row("tictac", "📐", "Take the Upper Right Corner of the Upper Left Board!",
                  "Oc9", "O takes the upper right corner of the upper left board", 12, 3)],
    "note": f"{TT_OPENING} {ANYONE} The move is due by 21 Oct, 22:02 EST, or the Arbiter plays a random legal move."}
# The house's Xi7 sends GitHub to the lower right board, where h3, g2 and h2 each win the game.
TT_GITHUB = {
    "kind": "tictac", "places": "github", "opens": "github", "game": 9, "move": 25, "players": 3,
    "board": "O..O.O.X./...O..XXG/XXXXX.O.X/XO..XXGO./.O.X..OOX/XO.OXXX.X/.XOO..O.O/.OOO.X..O/XXOOO.O.X",
    "due": "22 Nov", "alert": "lower right board",
    "history": [[23, "Of9", "Xh9", "@hollyfenwick"], [24, "Od8", "Xi7", "@hollyfenwick"], [25, "", "", ""]],
    "last": {"move": "Xi7", "words": "X takes the lower right corner of the upper right board", "by": "@tannergolden",
             "when": "15 Nov"},
    "moves": [row("tictac", "📏", "Take the Top Edge of the Lower Right Board!",
                  "Oh3", "O takes the top edge of the lower right board", 9, 51),
              row("tictac", "📏", "Take the Left Edge of the Lower Right Board!",
                  "Og2", "O takes the left edge of the lower right board", 9, 51),
              row("tictac", "🔳", "Take the Centre of the Lower Right Board!",
                  "Oh2", "O takes the centre of the lower right board", 9, 51),
              row("tictac", "📏", "Take the Bottom Edge of the Lower Right Board!",
                  "Oh1", "O takes the bottom edge of the lower right board", 9, 51)],
    "note": f"{ANYONE} The move is due by 22 Nov, 04:07 EST, or the Arbiter plays a random legal move. {TT_RULES}"}
# GitHub's Od1 sends the house to the lower left board, which the house has won, so it may play any open board: d3 and
# f2 each win the game.
TT_HOUSE = {
    "kind": "tictac", "places": "github", "opens": "house", "game": 10, "move": 23, "players": 3,
    "board": "....OG.OX/O..X.OO../O.XOOX..O/.XO.X.O../.XXOO.XX./X.OOGO.../.X...XXXX/..OOX..X./XXXOOXO.O",
    "due": "18 Nov", "alert": "any board",
    "history": [[21, "Xc5", "Og6", "@hollyfenwick"], [22, "Xc7", "Od1", "@imvale"], [23, "", "", ""]],
    "last": {"move": "Od1", "words": "O takes the lower left corner of the bottom board", "by": "@imvale",
             "when": "11 Nov"},
    "moves": [row("tictac", "📐", "Take the Upper Left Corner of the Upper Left Board!",
                  "Xa9", "X takes the upper left corner of the upper left board", 10, 47),
              row("tictac", "📏", "Take the Top Edge of the Upper Left Board!",
                  "Xb9", "X takes the top edge of the upper left board", 10, 47),
              row("tictac", "📐", "Take the Upper Right Corner of the Upper Left Board!",
                  "Xc9", "X takes the upper right corner of the upper left board", 10, 47)],
    "note": f"{ONLY} The move is due by 18 Nov, 01:00 EST, or the Arbiter plays a random legal move."}
# Every square the house could take on that turn, as the engine listed them.
HOUSE_SQUARES = "a9 b9 c9 d9 g9 b8 c8 e8 h8 i8 b7 g7 h7 a6 d6 f6 h6 i6 a5 f5 i5 b4 g4 h4 i4 d3 e3 f2"
# Game 8: the house's Xi4# won the right board, and with it the middle row of boards.
TT_WON = {
    "kind": "tictac", "places": "house", "opens": "github", "game": 8, "move": 28, "players": 3,
    "board": ".OXO...XO/.OO.O.OOO/X.O.XO.../XXXXXX..X/OXOX..XOX/XOOO...OX/GXXOOX.XO/O..XOOXX./OGX.XXOO.",
    "next": "17 Nov", "result": {"winner": "house", "how": "three boards in a row"}, "line": ["a2", "b2", "c2"],
    "history": [[26, "Oh1", "Xe1", "@devonaraki"], [27, "Of2", "Xi4#", "@devonaraki"], [28, "", "", ""]],
    "last": {"move": "Xi4#", "words": "X takes the lower right corner of the right board", "by": "@tannergolden",
             "when": "15 Nov"},
    "note": over("tictac", 8, "17 Nov", "04:10")}
# Game 9 won by GitHub on h2, in the lower right board the house's Xi7 sent it to.
TT_WON_GITHUB = {
    "kind": "tictac", "places": "github", "opens": "github", "game": 9, "move": 25, "players": 3,
    "board": "O..O.O.X./...O..XXG/XXXXX.O.X/XO..XXGO./.O.X..OOX/XO.OXXX.X/.XOO..O.O/.OOO.X.OO/XXOOO.O.X",
    "next": "18 Nov", "result": {"winner": "github", "how": "three boards in a row"}, "line": ["a1", "b1", "c1"],
    "history": [[23, "Of9", "Xh9", "@hollyfenwick"], [24, "Od8", "Xi7", "@hollyfenwick"],
                [25, "Oh2#", "", "@hollyfenwick"]],
    "last": {"move": "Oh2#", "words": "O takes the centre of the lower right board", "by": "@hollyfenwick",
             "when": "16 Nov"},
    "note": over("tictac", 9, "18 Nov", "08:07")}
# Game 7, drawn: one board drawn and the rest won so that no line of three boards is left to either side.
TT_DRAWN = {
    "kind": "tictac", "places": "house", "opens": "github", "game": 7, "move": 27, "players": 3,
    "board": "XOX...XOX/OO.X..OOX/.OOOOOXXO/XXX.OOOOO/OOX.XX..G/X..X...OO/.XO.XX.../OOXOXX.G./O..X.OXXX",
    "next": "21 Nov", "result": {"winner": None, "how": "no line left"},
    "history": [[25, "Og8", "Xc6", "@imvale"], [26, "Oh9", "Xf3", "@imvale"], [27, "Oh8", "", "@imvale"]],
    "last": {"move": "Oh8", "words": "O takes the centre of the upper right board", "by": "@imvale", "when": "19 Nov"},
    "note": over("tictac", 7, "21 Nov", "15:23")}

# --------------------------------------------------------------------------- Pentago
# Game 5, fresh: the Arbiter drew the house to set the first ghost, so only the house may choose its hole.
PG_FRESH = {
    "kind": "pentago", "places": "house", "game": 5, "move": 1, "players": 0,
    "board": "....../....../....../....../....../......",
    "due": "20 Oct", "alert": "set a ghost",
    "history": [["G", "", "", ""]],
    "moves": [row("pentago", "👻", "Ghost the Upper Left Corner of the Upper Left Quarter!",
                  "a6", "A ghost on a6, the upper left corner of the upper left quarter", 5, 1),
              row("pentago", "👻", "Ghost the Top Edge of the Upper Left Quarter!",
                  "b6", "A ghost on b6, the top edge of the upper left quarter", 5, 1),
              row("pentago", "👻", "Ghost the Upper Right Corner of the Upper Left Quarter!",
                  "c6", "A ghost on c6, the upper right corner of the upper left quarter", 5, 1)],
    "note": f"{PG_OPENING} {ONLY} The ghost is due by 20 Oct, 07:07 EST, or the Arbiter sets one at random."}
# A week passed without the house's ghost, so the Arbiter set it on e1, and it is GitHub's turn to set its own.
PG_GHOST = {
    "kind": "pentago", "places": "house", "game": 5, "move": 1, "players": 0,
    "board": "....../....../....../....../....../....G.",
    "due": "27 Oct", "alert": "set a ghost",
    "history": [["G", "e1", "", ""]],
    "last": {"move": "e1", "words": "A ghost on e1, the bottom edge of the lower right quarter", "by": "the Arbiter",
             "when": "20 Oct"},
    "moves": [row("pentago", "👻", "Ghost the Upper Left Corner of the Upper Left Quarter!",
                  "a6", "A ghost on a6, the upper left corner of the upper left quarter", 5, 2),
              row("pentago", "👻", "Ghost the Top Edge of the Upper Left Quarter!",
                  "b6", "A ghost on b6, the top edge of the upper left quarter", 5, 2),
              row("pentago", "👻", "Ghost the Upper Right Corner of the Upper Left Quarter!",
                  "c6", "A ghost on c6, the upper right corner of the upper left quarter", 5, 2)],
    "note": f"{PG_OPENING} {ANYONE} The ghost is due by 27 Oct, 07:08 EST, or the Arbiter sets one at random."}
# Game 6: both ghosts down, the house's on f3 and GitHub's on b1, and the Arbiter drew GitHub to set the first marble.
PG_GHOSTS = {
    "kind": "pentago", "places": "house", "opens": "github", "game": 6, "move": 1, "players": 1,
    "board": "....../....../....../.....G/....../.G....",
    "due": "21 Oct",
    "history": [["G", "f3", "b1", "@devonaraki"], [1, "", "", ""]],
    "last": {"move": "b1", "words": "A ghost on b1, the bottom edge of the lower left quarter", "by": "@devonaraki",
             "when": "14 Oct"},
    "moves": [hole("⚫", "Take the Upper Left Corner of the Upper Left Quarter!",
                   "a6", "A black marble on a6, then a quarter turns", 6, 3),
              hole("⚫", "Take the Top Edge of the Upper Left Quarter!",
                   "b6", "A black marble on b6, then a quarter turns", 6, 3),
              hole("⚫", "Take the Upper Right Corner of the Upper Left Quarter!",
                   "c6", "A black marble on c6, then a quarter turns", 6, 3)],
    "note": f"{PG_OPENING} {ANYONE} The move is due by 21 Oct, 10:52 EST, or the Arbiter plays a random legal move."}
# Game 3 the other way round: GitHub set the first ghost, on b5, a quarter's centre, which no turn moves, and the
# Arbiter drew the house to set the first marble.
PG_GHOSTS_HOUSE = {
    "kind": "pentago", "places": "github", "opens": "house", "game": 3, "move": 1, "players": 1,
    "board": "....../.G..../....../....../....../.....G",
    "due": "22 Oct",
    "history": [["G", "b5", "f1", "@imvale"], [1, "", "", ""]],
    "last": {"move": "f1", "words": "A ghost on f1, the lower right corner of the lower right quarter",
             "by": "@tannergolden", "when": "15 Oct"},
    "moves": [hole("⚪", "Take the Upper Left Corner of the Upper Left Quarter!",
                   "a6", "A white marble on a6, then a quarter turns", 3, 3),
              hole("⚪", "Take the Top Edge of the Upper Left Quarter!",
                   "b6", "A white marble on b6, then a quarter turns", 3, 3),
              hole("⚪", "Take the Upper Right Corner of the Upper Left Quarter!",
                   "c6", "A white marble on c6, then a quarter turns", 3, 3)],
    "note": f"{PG_OPENING} {ONLY} The move is due by 22 Oct, 06:16 EST, or the Arbiter plays a random legal move."}
# Game 4, GitHub's turn: e5 makes five on its own, and a clockwise turn of the upper right quarter after any other
# marble makes five for the house alone. Its ghosts, set on a2 and d2, have turned with their quarters to b1 and e1.
PG_GITHUB = {
    "kind": "pentago", "places": "house", "opens": "house", "game": 4, "move": 13, "players": 3,
    "board": "..BWWW/.WB..B/.BWBW./BWBWWW/BB..BW/BGWWGB",
    "due": "10 Nov",
    "history": [[11, "c3-ur-cw", "a1-ll-cw", "@hollyfenwick"], [12, "f6-ul-cw", "d4-lr-acw", "@devonaraki"],
                [13, "b5-lr-acw", "", ""]],
    "last": {"move": "b5-lr-acw", "words": "A white marble on b5, then the lower right quarter turns anticlockwise",
             "by": "@tannergolden", "when": "3 Nov"},
    "moves": [hole("⚫", "Take the Upper Left Corner of the Upper Left Quarter!",
                   "a6", "A black marble on a6, then a quarter turns", 4, 28),
              hole("⚫", "Take the Top Edge of the Upper Left Quarter!",
                   "b6", "A black marble on b6, then a quarter turns", 4, 28),
              hole("⚫", "Take the Left Edge of the Upper Left Quarter!",
                   "a5", "A black marble on a5, then a quarter turns", 4, 28)],
    "note": f"{ANYONE} The move is due by 10 Nov, 07:00 EST, or the Arbiter plays a random legal move. {PG_RULES}"}
# Game 7, the house's turn: c1 and a clockwise turn of the lower right quarter make five, and a clockwise turn of the
# upper right quarter after any marble makes five for GitHub alone.
PG_HOUSE = {
    "kind": "pentago", "places": "github", "opens": "house", "game": 7, "move": 13, "players": 3,
    "board": "WB.B.G/BBB.BW/.WB.B./BW.WW./WWG.BW/WW.BBW",
    "due": "3 Nov",
    "history": [[11, "b2-ur-cw", "b4-lr-acw", "@hollyfenwick"], [12, "a4-ul-cw", "a3-lr-cw", "@devonaraki"],
                [13, "", "", ""]],
    "last": {"move": "a3-lr-cw", "words": "A black marble on a3, then the lower right quarter turns clockwise",
             "by": "@devonaraki", "when": "27 Oct"},
    "moves": [hole("⚪", "Take the Upper Right Corner of the Upper Left Quarter!",
                   "c6", "A white marble on c6, then a quarter turns", 7, 27),
              hole("⚪", "Take the Top Edge of the Upper Right Quarter!",
                   "e6", "A white marble on e6, then a quarter turns", 7, 27),
              hole("⚪", "Take the Left Edge of the Upper Right Quarter!",
                   "d5", "A white marble on d5, then a quarter turns", 7, 27)],
    "note": f"{ONLY} The move is due by 3 Nov, 13:28 EST, or the Arbiter plays a random legal move. {PG_RULES}"}
# Game 3: the house set a5 and turned the lower right quarter, making five up file f.
PG_WON = {
    "kind": "pentago", "places": "github", "opens": "house", "game": 3, "move": 10, "players": 3,
    "board": ".W..BW/WG..BW/.BWBBW/W.B..W/BWB..W/..B..G",
    "next": "28 Oct", "result": {"winner": "house", "how": "five in a row"}, "line": ["f2", "f3", "f4", "f5", "f6"],
    "history": [[8, "b2-ur-cw", "e5-ur-acw", "@devonaraki"], [9, "c3-ur-cw", "b1-ll-acw", "@devonaraki"],
                [10, "a5-lr-acw#", "", ""]],
    "last": {"move": "a5-lr-acw#", "words": "A white marble on a5, then the lower right quarter turns anticlockwise",
             "by": "@tannergolden", "when": "26 Oct"},
    "note": over("pentago", 3, "28 Oct", "14:16")}
# Game 6: GitHub's marble on d5 made five along rank 5 on its own, so no quarter turned.
PG_WON_GITHUB = {
    "kind": "pentago", "places": "house", "opens": "github", "game": 6, "move": 13, "players": 3,
    "board": "W.B.WB/BBBBBW/WWBWB./.G..WW/BWWWB./.BB.WG",
    "next": "2 Nov", "result": {"winner": "github", "how": "five in a row"}, "line": ["a5", "b5", "c5", "d5", "e5"],
    "history": [[11, "e5-ll-acw", "f5-ll-cw", "@imvale"], [12, "a6-ul-cw", "d4-lr-cw", "@devonaraki"],
                [13, "d5#", "", "@devonaraki"]],
    "last": {"move": "d5#", "words": "A black marble on d5", "by": "@devonaraki", "when": "31 Oct"},
    "note": over("pentago", 6, "2 Nov", "07:52")}
# Game 2: the house's own turn of the lower left quarter carried its marble to c3 and made five for GitHub alone.
PG_GIVEN = {
    "kind": "pentago", "places": "house", "opens": "house", "game": 2, "move": 15, "players": 3,
    "board": "WBBBWW/.BBWWW/BBWBWB/WBW..W/WB.WB./WBWBGG",
    "next": "7 Nov", "result": {"winner": "github", "how": "five in a row"}, "line": ["b1", "b2", "b3", "b4", "b5"],
    "history": [[13, "a1-lr-cw", "f6-ur-acw", "@devonaraki"], [14, "e5-lr-cw", "b5-ul-cw", "@hollyfenwick"],
                [15, "a3-ll-cw#", "", ""]],
    "last": {"move": "a3-ll-cw#", "words": "A white marble on a3, then the lower left quarter turns clockwise",
             "by": "@tannergolden", "when": "5 Nov"},
    "note": over("pentago", 2, "7 Nov", "00:03", "The move that won it was the other side's, its turn making five for "
                 "the winner alone, so the win counts for nobody.")}
# Game 1: every hole but the ghosts' filled, and five for neither side.
PG_FULL = {
    "kind": "pentago", "places": "house", "opens": "github", "game": 1, "move": 18, "players": 3,
    "board": "WGBWWB/WWWGBB/BBBWWB/BBWBBB/WWBBWW/BWWBWW",
    "next": "10 Nov", "result": {"winner": None, "how": "a full board"},
    "history": [[16, "d6-ur-cw", "c2-lr-acw", "@imvale"], [17, "d1-ll-cw", "c5-ur-cw", "@hollyfenwick"],
                [18, "", "", ""]],
    "last": {"move": "c5-ur-cw", "words": "A white marble on c5, then the upper right quarter turns clockwise",
             "by": "@tannergolden", "when": "8 Nov"},
    "note": over("pentago", 1, "10 Nov", "00:07")}
# Game 8: the house's turn of the lower right quarter made five for both sides at once.
PG_BOTH = {
    "kind": "pentago", "places": "github", "opens": "house", "game": 8, "move": 15, "players": 3,
    "board": "WBW.GB/WBW.WB/BWWWBB/BBW.GB/W.BWBB/WW.WWB",
    "next": "3 Nov", "result": {"winner": None, "how": "five for both"},
    "history": [[13, "f1-ll-acw", "d6-ul-cw", "@hollyfenwick"], [14, "b1-ur-acw", "e3-ur-acw", "@devonaraki"],
                [15, "f2-lr-cw", "", ""]],
    "last": {"move": "f2-lr-cw", "words": "A white marble on f2, then the lower right quarter turns clockwise",
             "by": "@tannergolden", "when": "1 Nov"},
    "note": over("pentago", 8, "3 Nov", "03:35")}

# --------------------------------------------------------------------------- Checkers
# A fresh board: GitHub plays Black, which moves first, so the game opens on GitHub's turn, its clock running.
CK_OPENING = {
    "kind": "checkers", "fen": "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12",
    "game": 6, "move": 1, "players": 0, "due": "21 Oct", "history": [[1, "", "", ""]],
    "kings": {"house": 0, "github": 0},
    "moves": [row("checkers", "👣", "Push the Man From 9 to 13!", "9-13", "Man from 9 to 13", 6, 1),
              row("checkers", "👣", "Push the Man From 9 to 14!", "9-14", "Man from 9 to 14", 6, 1)],
    "note": "A jump must be taken when there is one. " + NOTE}
# The house has just jumped back, and GitHub's Black must jump again.
CK_GITHUB = {
    "kind": "checkers", "fen": "B:W11,21,24,25,27,28,29,30,32:B2,4,5,6,8,9,14,18", "game": 6, "move": 11,
    "players": 11, "due": "18 Oct",
    "history": [[9, "1-6", "22x15", "@sunnypatel"], [10, "11x18", "20x11", "@hollyfenwick"], [11, "", "", ""]],
    "kings": {"house": 0, "github": 0},
    "last": {"move": "20x11", "words": "Man from 20 jumps 16, landing on 11", "by": "@tannergolden", "when": "12 Oct"},
    "alert": "must jump",
    "moves": [row("checkers", "⚔️", "Jump the Man on 11!", "8x15", "Man from 8 jumps 11, landing on 15", 6, 21)],
    "note": "A jump must be taken when there is one."}
# The house's double jump has crowned a White king on Black's back row, and it is GitHub's turn.
CK_CROWNED = {
    "kind": "checkers", "fen": "B:WK1,20,21,24,28,30:B5,8,12,17,18", "game": 5, "move": 19,
    "players": 14, "due": "17 Oct",
    "history": [[17, "2-6", "17-14", "@imvale"], [18, "10x17", "19x10x1", "@tokafor"], [19, "", "", ""]],
    "kings": {"house": 1, "github": 0},
    "last": {"move": "19x10x1", "words": "Man from 19 jumps 15 and 6, landing on 1, crowned", "by": "@tannergolden",
             "when": "9 Oct", "crowned": True},
    "moves": [row("checkers", "👣", "March the Man From 5 to 9!", "5-9", "Man from 5 to 9", 5, 37),
              row("checkers", "👣", "March the Man From 8 to 11!", "8-11", "Man from 8 to 11", 5, 37)],
    "note": "A jump must be taken when there is one."}
# The house's White man took GitHub's last: Black has no move left, and the house wins.
CK_WON = {
    "kind": "checkers", "fen": "B:W10,24,28:B", "game": 4, "move": 31, "players": 12,
    "history": [[29, "7-11", "23-19", "@imvale"], [30, "11-15", "19x10", "@octocat"]],
    "kings": {"house": 1, "github": 2},
    "last": {"move": "19x10", "words": "Man from 19 jumps 15, landing on 10", "by": "@tannergolden", "when": "9 Oct"},
    "result": {"winner": "house", "how": "no move left"}, "next": "14 Oct",
    "note": NOTE}
CK_DRAWN = {
    "kind": "checkers", "fen": "B:WK30:BK3", "game": 3, "move": 88, "players": 20,
    "history": [[87, "8-3", "26-30", "@octocat"], [88, "", "", ""]], "kings": {"house": 3, "github": 4},
    "last": {"move": "26-30", "words": "King from 26 to 30", "by": "@tannergolden", "when": "8 Oct"},
    "result": {"winner": None, "how": "forty moves"}, "next": "14 Oct",
    "note": NOTE}

GAMES = {"tictac": (TT, (TT_FRESH, TT_GHOST, TT_GHOSTS, TT_GHOSTS_GITHUB, TT_GITHUB, TT_HOUSE, TT_WON, TT_WON_GITHUB,
                         TT_DRAWN)),
         "pentago": (PG, (PG_FRESH, PG_GHOST, PG_GHOSTS, PG_GHOSTS_HOUSE, PG_GITHUB, PG_HOUSE, PG_WON, PG_WON_GITHUB,
                          PG_GIVEN, PG_FULL, PG_BOTH)),
         "checkers": (CK, (CK_OPENING, CK_GITHUB, CK_CROWNED, CK_WON, CK_DRAWN))}
# A board under way, one while its ghosts go down or a fresh one, and a finished one of each game, drawn in every tone.
EVERY_TONE = (TT_GITHUB, TT_GHOST, TT_WON, PG_HOUSE, PG_GHOSTS, PG_GIVEN, CK_GITHUB, CK_OPENING, CK_WON)
BOARDS = [d for _, boards in GAMES.values() for d in boards]
# Where a sheet stands its board, as chess's sheet does: its top left corner and its width, wide and on a phone.
AT = {False: (GS.PAD + 18, GS.BAND + 22, GS.BOARD["wide"]), True: (GS.PAD + 14, GS.BAND + 18, GS.BOARD["narrow"])}


def name(d: dict) -> str:
    last = (d.get("last") or {}).get("move", "nothing")
    return f"{d['kind']} game {d['game']} move {d['move']} after {last}{' finished' if d.get('result') else ''}"


def said(block: str) -> str:
    """A README block's words: everything but its picture's markup, whose sources name the dark theme's files."""
    return re.sub(r"<picture>.*?</picture>", "", block, flags=re.S)


def lettered(d: dict, tone: str, variant: str = "still") -> list[str]:
    """Every run of lettering a file sets, in capitals: what a sheet says, since its letters are drawn as paths."""
    runs, text = [], Lettering.text

    def record(self, s, **k):
        runs.append(str(s).upper())
        return text(self, s, **k)
    with mock.patch.object(Lettering, "text", record):
        E.draw(d["kind"], d, tone, "day", variant)
    return runs


def reasons(pkg, d: dict) -> str:
    """Everything a game's check finds in `d`, as one line to look for a reason in."""
    return " ".join(pkg.check(d))


class EveryFile(unittest.TestCase):
    def test_every_board_is_what_its_game_accepts_on_tannergoldens_profile(self):
        for d in BOARDS:
            with self.subTest(board=name(d)):
                self.assertEqual(ED.validate({d["kind"]: d}, {}, subject="tannergolden"), [])

    def test_every_file_in_every_theme_is_well_formed_within_budget_and_deterministic(self):
        for d in EVERY_TONE:
            for tone in TONES:
                for variant in E.variants(d["kind"], d):
                    for theme in ("day", "dark"):
                        svg = E.draw(d["kind"], d, tone, theme, variant)    # the kit's lint and budget, or it raises
                        with self.subTest(board=name(d), tone=tone, variant=variant, theme=theme):
                            minidom.parseString(svg)
                            self.assertEqual(svg, E.draw(d["kind"], d, tone, theme, variant))
                            self.assertNotIn("<text", svg)
                            self.assertEqual(lint(svg, budget=BUDGET["board"]), [])
                            for ch in DASHES:
                                self.assertNotIn(ch, svg)

    def test_every_board_every_way_round_is_drawn_in_the_standard_theme_and_a_print(self):
        for d in BOARDS:
            for tone in (STANDARD, "blackprint"):
                for variant in E.variants(d["kind"], d):
                    for theme in ("day", "dark"):
                        svg = E.draw(d["kind"], d, tone, theme, variant)
                        with self.subTest(board=name(d), tone=tone, variant=variant, theme=theme):
                            self.assertEqual(lint(svg, budget=BUDGET["board"]), [])
                            self.assertEqual(svg.count("<svg"), 1)
                            for ch in DASHES:
                                self.assertNotIn(ch, svg)

    def test_no_sheet_of_tic_tac_or_pentago_singles_out_a_square_a_hole_or_a_turn(self):
        # Nothing is clouded or glowing, since nothing the rules make the side to move answer is there. Tic-Tac boxes
        # the last move's square alone and tones and brackets only the board the rules send the next mark to, never a
        # square or a board a side could win on; Pentago rings the last marble's hole and a won game's five alone, and
        # draws the turn of the last move's quarter alone, never a hole or a turn that would make five.
        seen: dict[str, list] = {"brackets": [], "toned": [], "boxed": [], "rings": [], "turns": []}

        def clouded(*_, **__):
            raise AssertionError("a square or a hole singled out")

        def recording(key, original, at):
            def record(self, *a, **k):
                seen[key].append(at(*a))
                return original(self, *a, **k)
            return record

        def corner(x, y, *_):
            return round(x, 1), round(y, 1)

        patches = [mock.patch.object(skin, "clouded", clouded) for skin in (GameStandard, GamePrint)]
        for skin in (TT.Standard, TT.Print):
            patches += [mock.patch.object(skin, "brackets", recording("brackets", skin.brackets, corner)),
                        mock.patch.object(skin, "target", recording("toned", skin.target, corner)),
                        mock.patch.object(skin, "cell_mark", recording("boxed", skin.cell_mark,
                                                                       lambda cv, x, y, *_: corner(x, y)))]
        for skin in (PG.Standard, PG.Print):
            patches += [mock.patch.object(skin, "hole_ring", recording("rings", skin.hole_ring,
                                                                       lambda cv, x, y, *_: corner(x, y))),
                        mock.patch.object(skin, "turn_mark", recording("turns", skin.turn_mark,
                                                                       lambda X, Y, q, qk, way, *_: (qk, way)))]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        for d in GAMES["tictac"][1] + GAMES["pentago"][1]:
            game = E.game_of(d["kind"])
            st = game.state(game.describe(d))
            for tone in TONES:
                for variant in E.variants(d["kind"], d):
                    small = variant.startswith("narrow")
                    x0, y0, n = AT[small]
                    for got in seen.values():
                        got.clear()
                    E.draw(d["kind"], d, tone, "day", variant)
                    with self.subTest(board=name(d), tone=tone, variant=variant):
                        if d["kind"] == "tictac":
                            sent = [] if st["result"] or st["target"] is None else [st["target"]]
                            self.assertEqual(seen["brackets"],
                                             [corner(*TT.layout.board_box(b, x0, y0, n, small)) for b in sent])
                            self.assertEqual(seen["toned"], seen["brackets"])
                            boxed = [st["last"]["cell"]] if st["last"] else []
                            self.assertEqual(seen["boxed"],
                                             [corner(*TT.layout.cell_box(c, x0, y0, n, small)) for c in boxed])
                        else:
                            ringed = ([st["last"]["landed"]] if st["last"] else []) + st["line"]
                            self.assertEqual(sorted(seen["rings"]),
                                             sorted(corner(*PG.layout.centre(c, x0, y0, n, small)) for c in ringed))
                            turned = st["last"] and st["last"]["turned"]
                            self.assertEqual(seen["turns"], [(st["last"]["quarter"], st["last"]["way"])] if turned
                                             else [])

    def test_the_still_files_stand_still_and_the_rest_move(self):
        for d in BOARDS:
            for tone in (STANDARD, "blackprint"):
                for variant in E.variants(d["kind"], d):
                    svg = E.draw(d["kind"], d, tone, "day", variant)
                    with self.subTest(board=name(d), tone=tone, variant=variant):
                        (self.assertNotIn if variant.endswith("still") else self.assertIn)("<animate", svg)

    def test_each_is_a_kind_of_its_own_drawn_as_chess_is_and_takes_the_place_of_a_game_retired(self):
        for kind in ("tictac", "pentago", "checkers"):
            fn, variants, klass = E.KINDS[kind]
            self.assertEqual((variants, klass), (("wide", "narrow", "still", "narrow-still"), "board"))
            self.assertIn(kind, ED.OWN_THEMES)
            self.assertIn(kind, ED.GAMES, "a holiday's set or a collection's design draws it in its pixels")
        self.assertEqual(E.GAMES, ("tictac", "pentago", "checkers"))
        for old, new in (("tictactoe", "tictac"), ("connectfour", "pentago")):
            with self.subTest(retired=old):
                self.assertNotIn(old, E.KINDS)
                self.assertNotIn(old, ED.GAMES | ED.OWN_THEMES | set(ED.FOLDS))
                self.assertEqual((ED.RETIRED[old], ED.SUCCEEDED[old]), ("1.14.0", new))

    def test_a_sheet_is_the_width_of_chesss_and_as_tall_in_every_theme(self):
        for d in EVERY_TONE:
            for variant, width in (("wide", 830), ("narrow", 360)):
                sizes = {re.search(r'width="(\d+)" height="(\d+)"', E.draw(d["kind"], d, tone, "day", variant)).groups()
                         for tone in TONES}
                with self.subTest(board=name(d), variant=variant):
                    self.assertEqual(len(sizes), 1, sizes)
                    self.assertEqual(int(next(iter(sizes))[0]), width)


class Standard_(unittest.TestCase):
    """In the standard theme each board is drawn in chess's enamel: its card and band, its board, its lit pieces."""

    def test_every_letter_holds_4_5_against_its_ground(self):
        P.PAIRS.clear()
        for d in BOARDS:
            for variant in ("wide", "narrow"):
                for theme in ("day", "dark"):
                    E.draw(d["kind"], d, STANDARD, theme, variant)
        self.assertTrue(P.PAIRS)
        for fill, ground, what in P.PAIRS:
            self.assertGreaterEqual(P.contrast(fill, ground), 4.5, (fill, ground, what))

    def test_the_standard_theme_is_chesss_enamel_and_a_print_its_drawing(self):
        for d in EVERY_TONE:
            standard = E.draw(d["kind"], d, STANDARD, "day", "still")
            printed = E.draw(d["kind"], d, "blackprint", "day", "still")
            with self.subTest(board=name(d)):
                self.assertIn(f"standard elements {d['kind']} wide day still", standard)
                self.assertIn(f"blackprint elements {d['kind']} wide day still", printed)
                self.assertIn(P.hexof(P.ACCENT), standard, "the cobalt of chess's dark squares and the band's block")
                self.assertIn('fill="url(#', standard)

    def test_a_holiday_or_collection_draws_every_file_of_each_game_in_its_pixels(self):
        elements = ED.merged({d["kind"]: dict(d) for d in (TT_GITHUB, PG_HOUSE, CK_GITHUB)}, {},
                             subject="tannergolden")
        printed = ED.render(elements, "blackprint")
        drawn = ED.render(elements, "blackprint", "halloween")
        self.assertEqual(sorted(drawn), sorted(printed), "the same files, whoever draws them")
        for name, svg in drawn.items():
            self.assertIn(f"halloween elements {name.split('-')[0]} ", svg, name)
        standard = ED.render(elements, STANDARD)
        self.assertEqual(sorted(standard), sorted(printed))
        for key in ("tictac", "pentago", "checkers"):
            self.assertNotEqual(standard[f"{key}-day.svg"], printed[f"{key}-day.svg"])


class Settings(unittest.TestCase):
    def test_each_is_drawn_on_tannergoldens_profile_alone(self):
        section = {d["kind"]: dict(d) for d in (TT_GITHUB, PG_GITHUB, CK_GITHUB)}
        self.assertEqual(ED.validate(section, {}, subject="tannergolden"), [])
        self.assertEqual(ED.validate(section, {}, subject="TannerGolden"), [])
        for elsewhere in ("octocat", "tannergolden/markdown", ""):
            with self.subTest(subject=elsewhere):
                errors = ED.validate(section, {}, subject=elsewhere)
                for kind in section:
                    self.assertIn(f"{kind}: the {kind} element is drawn on @tannergolden's profile alone", errors)

    def test_what_each_cannot_be_drawn_without_is_named(self):
        for kind, needs in (("tictac", "board, places"), ("pentago", "board, places"), ("checkers", "fen")):
            with self.subTest(kind=kind):
                errors = ED.validate({kind: {"kind": kind}}, {}, subject="tannergolden")
                self.assertIn(f"{kind}: a {kind} needs {needs}", errors)

    def test_a_board_of_a_game_retired_is_turned_away_with_the_game_that_took_its_place(self):
        # The settings of a page from before 1.14.0 name Tic-Tac-Toe and Connect Four: each is told what happened
        # and which game took its place, and an old board under a new game's name is turned away for its shape.
        old = {"tictactoe": {"kind": "tictactoe", "board": "O../XX./O.X", "opens": "house"},
               "connectfour": {"kind": "connectfour", "board": "......./......./......./......./......./...D...",
                               "opens": "github"}}
        self.assertEqual(ED.validate(old, {}, subject="tannergolden"),
                         ["tictactoe: the tictactoe element was retired in banners v1.14.0, and tictac took its place;"
                          " take it out of the settings",
                          "connectfour: the connectfour element was retired in banners v1.14.0, and pentago took its"
                          " place; take it out of the settings"])
        self.assertIn("board 'O../XX./O.X' is not nine rows of nine X, O, G or dots, the top row first",
                      reasons(TT, {**old["tictactoe"], "kind": "tictac"}))
        self.assertIn("is not six rows of six W, B, G or dots, the top row first",
                      reasons(PG, {**old["connectfour"], "kind": "pentago"}))

    def test_text_is_text_and_a_number_a_number_within_its_ceiling(self):
        # YAML reads `note: 1984` as a number, `true` as a bool and an all-digit login as an int: each is turned away
        # here rather than reaching the README, which would fail on it.
        for pkg, d in ((TT, TT_GITHUB), (PG, PG_GITHUB), (CK, CK_GITHUB)):
            texts = {"note": (1984, True, ["a note"]), "due": (18, "32 Oct"),
                     "last": ({**d["last"], "words": 1984}, {**d["last"], "by": None}, {**d["last"], "when": 11},
                              {**d["last"], "when": "30 Feb"}),
                     "history": ([[3, 1984, "", ""]], [[3, d["last"]["move"], "", 7]], 5, "x"),
                     "moves": ([[*d["moves"][0][:1], 1984, *d["moves"][0][2:]]], [[*d["moves"][0][:4], 5]],
                               [[1, *d["moves"][0][1:]]], {"a": 1})}
            for key, values in texts.items():
                for bad in values:
                    with self.subTest(kind=d["kind"], key=key, bad=bad):
                        self.assertTrue(pkg.check({**d, key: bad}))
            for key in ("game", "move", "players"):
                for bad in ("13", True, -1, 1_000_000_000, 13.0):
                    with self.subTest(kind=d["kind"], key=key, bad=bad):
                        self.assertIn(f"{key} {bad!r} is not a number from", reasons(pkg, {**d, key: bad}))
                with self.subTest(kind=d["kind"], key=key, fine=999_999_999):
                    self.assertEqual(pkg.check({**d, key: 999_999_999}), [])
            for bad_row in ([True, "", "", ""], [0, "", "", ""], [1_000_000_000, "", "", ""], ["3", "", "", ""]):
                with self.subTest(kind=d["kind"], row=bad_row):
                    self.assertIn("is not a row of a move's number", reasons(pkg, {**d, "history": [bad_row]}))
        # the ghosts' row, numbered G, opens the score sheet of a game under the Ghost Rule, and no other
        for pkg, d in ((TT, TT_GHOSTS), (PG, PG_GHOSTS)):
            with self.subTest(kind=d["kind"]):
                self.assertIn("or G for the ghosts' row first",
                              reasons(pkg, {**d, "history": [*d["history"][1:], d["history"][0]]}))
        self.assertIn("is not a row of a move's number", reasons(CK, {**CK_GITHUB, "history": [["G", "", "", ""]]}))

    def test_a_line_of_the_readme_never_opens_a_block_or_shows_an_image(self):
        for pkg, d in ((TT, TT_GITHUB), (PG, PG_GITHUB), (CK, CK_GITHUB)):
            for bad in ("```", "# Heading", "- an item", "1. an item", "    code", "---", "[a]: https://x.io"):
                with self.subTest(kind=d["kind"], bad=bad):
                    self.assertIn(f"note {bad!r} would open a block of its own", reasons(pkg, {**d, "note": bad}))
            self.assertIn("note shows an image", reasons(pkg, {**d, "note": "![x](https://x.io/x.png)"}))
            self.assertIn("note is one line of text", reasons(pkg, {**d, "note": "a | b"}))

    def test_no_banner_goes_over_a_board_whose_sheet_says_whose_turn_it_is(self):
        for kind, (pkg, boards) in GAMES.items():
            for d in boards:
                with self.subTest(board=name(d)):
                    self.assertIn("prompt is gone", reasons(pkg, {**d, "prompt": "🟢 **GitHub's turn!**"}))
                    self.assertNotIn("[!", ED.block(kind, d, "assets/elements"))

    def test_a_move_links_its_own_ready_made_issue_and_nothing_else(self):
        for pkg, d in ((TT, TT_GITHUB), (TT, TT_FRESH), (PG, PG_FRESH), (CK, CK_GITHUB)):
            other = {"tictac": "pentago", "pentago": "checkers", "checkers": "tictac"}[d["kind"]]
            for bad in ("https://example.com/x", d["moves"][0][4].replace(d["kind"], other),
                        d["moves"][0][4] + "&x=1", d["moves"][0][4].replace("move%20", "move%200")):
                with self.subTest(board=name(d), link=bad[-30:]):
                    self.assertTrue(pkg.check({**d, "moves": [[*d["moves"][0][:4], bad]]}))
        self.assertTrue(TT.check({**TT_GITHUB, "moves": [row("tictac", "🎯", "Go", "Oh3", "O h3", 9, 51, code="j3")]}),
                        "a square the game does not have")
        self.assertTrue(PG.check({**PG_FRESH, "moves": [row("pentago", "👻", "Go", "a6", "A ghost", 5, 1, code="g6")]}),
                        "a hole the game does not have")

    def test_nothing_the_settings_can_hold_makes_the_checks_raise(self):
        hostile = (None, True, False, 0, -1, 1984, 10 ** 30, 1.5, "", "x", "```", [], [1], [[]], {}, {"a": 1},
                   ["x", "y", "z", "w", "v"], [[1, 2], [3, 4], [5, 6], [7, 8]])
        for pkg, d in ((TT, TT_FRESH), (TT, TT_GITHUB), (TT, TT_WON), (PG, PG_FRESH), (PG, PG_GITHUB), (PG, PG_WON),
                       (CK, CK_GITHUB), (CK, CK_WON)):
            keys = set(d) | {"x", "places", "opens", "light", "dark", "threats", "line", "result", "next", "kings",
                             "alert", "board", "fen"}
            for key in sorted(keys):
                for bad in hostile:
                    with self.subTest(board=name(d), key=key, bad=bad):
                        self.assertIsInstance(pkg.check({**d, key: bad}), list)
            for bad in hostile:
                with self.subTest(board=name(d), last=bad):
                    self.assertIsInstance(pkg.check({**d, "last": {k: bad for k in d.get("last") or {"move": 1}}}),
                                          list)
                    self.assertIsInstance(pkg.check({**d, "result": {"winner": bad, "how": bad}}), list)
                for move in (d.get("moves") or [])[:1]:
                    with self.subTest(board=name(d), link=bad):
                        for links in (bad, [bad] * 8, [[bad] * 3] * 8, [[q, w, bad] for q, w in TURNS]):
                            self.assertIsInstance(pkg.check({**d, "moves": [[*move[:4], links]]}), list)


class TicTac(unittest.TestCase):
    def test_the_squares_are_named_as_chess_names_squares_and_the_boards_as_tic_tac_toe_names_cells(self):
        self.assertEqual(TT.placement(TT_GHOSTS["board"]), {"h8": "G", "d6": "G"})
        on = TT.placement(TT_GITHUB["board"])
        self.assertEqual([on[c] for c in ("a9", "h9", "i8", "g6", "i1")], ["O", "X", "G", "G", "X"])
        self.assertEqual([TT.game.board_name(TT.game.board_of(c)) for c in ("a1", "e5", "i9", "c7", "g2")],
                         ["a1", "b2", "c3", "a3", "c1"])
        # where a mark stands in its board is the board it sends the other side to: i7, a board's lower right corner
        self.assertEqual(TT.game.PLACE[TT.game.spot_of("i7")], "lower right")

    def test_the_house_plays_x_and_github_o_whoever_places_first_and_whoever_opens(self):
        self.assertEqual((TT.game.mark_of("house"), TT.game.mark_of("github")), ("X", "O"))
        for d, places, turn, said in ((TT_FRESH, "github", "github", "It is GitHub's turn to place a ghost"),
                                      (TT_GHOST, "github", "house", "It is @tannergolden's turn to place a ghost"),
                                      (TT_GHOSTS, "github", "house", "It is @tannergolden's turn as X"),
                                      (TT_GHOSTS_GITHUB, "house", "github", "It is GitHub's turn as O"),
                                      (TT_GITHUB, "github", "github", "It is GitHub's turn as O"),
                                      (TT_HOUSE, "github", "house", "It is @tannergolden's turn as X")):
            st = TT.state(d)
            alt = E.alt("tictac", d)
            with self.subTest(board=name(d)):
                self.assertEqual((st["places"], st["to_move"]), (places, turn))
                self.assertIn("@tannergolden plays X and GitHub O, under the Ghost Rule", alt)
                self.assertIn(said, alt)
        self.assertIn("x is gone: the house always plays X and GitHub O, and places and opens name the sides the"
                      " Arbiter drew", reasons(TT, {**TT_GITHUB, "x": "house"}))
        # a board from before the Ghost Rule names the side the Arbiter opened for alone
        self.assertIn("places None is the side the Arbiter drew to place the first ghost: house, which plays X, or"
                      " github, which plays O", reasons(TT, {k: v for k, v in TT_GITHUB.items() if k != "places"}))
        self.assertIn("places 'white' is the side", reasons(TT, {**TT_GITHUB, "places": "white"}))
        self.assertIn("opens None is the side the Arbiter drew to make the first mark once both ghosts were down",
                      reasons(TT, {k: v for k, v in TT_GHOSTS.items() if k != "opens"}))
        self.assertIn("opens: the Arbiter draws the side that makes the first mark once both ghosts are down",
                      reasons(TT, {**TT_GHOST, "opens": "house"}))
        # the opener's mark leads: X may have one more than O only in a game the house was drawn to open
        self.assertIn("board has 26 X and 27 O: X moved first, the Arbiter having drawn house to open, so X has as many"
                      " marks as O or one more", reasons(TT, {**TT_DRAWN, "opens": "house"}))
        one_more = {**TT_HOUSE, "board": "X" + TT_HOUSE["board"][1:], "opens": "github"}
        self.assertIn("O moved first, the Arbiter having drawn github to open, so O has as many marks as X or one more",
                      reasons(TT, one_more))

    def test_x_is_drawn_light_and_o_dark_whoever_plays_them(self):
        # A game's colours never change, only who moves first: every X the sheet draws (on the board, as the mark of
        # a board won, in the medallions and on the trays) is in the light material and every O in the dark.
        def drawn(d: dict, tone: str) -> list[tuple[str, str]]:
            seen = []

            def recording(original):
                def pen_mark(self, cv, mark, material, *a, **k):
                    seen.append((mark, material))
                    return original(self, cv, mark, material, *a, **k)
                return pen_mark
            with mock.patch.object(TT.Standard, "pen_mark", recording(TT.Standard.pen_mark)), \
                    mock.patch.object(TT.Print, "pen_mark", recording(TT.Print.pen_mark)):
                for variant in ("still", "narrow-still"):
                    E.draw("tictac", d, tone, "day", variant)
            return seen

        for tone in (STANDARD, "blackprint"):
            for d in GAMES["tictac"][1]:
                marks = drawn(d, tone)
                with self.subTest(board=name(d), tone=tone):
                    self.assertEqual({mark for mark, _ in marks}, {"X", "O"}, "both sides' medallions at least")
                    self.assertEqual(sorted(set(marks)), [("O", "dark"), ("X", "light")])
        # the matchup has the house as X on the left and GitHub as O, drawn either way round
        for d in (TT_FRESH, TT_GHOST, TT_GHOSTS, TT_GHOSTS_GITHUB, TT_GITHUB, TT_HOUSE):
            for variant in ("still", "narrow-still"):
                runs = lettered(d, STANDARD, variant)
                with self.subTest(board=name(d), variant=variant):
                    self.assertIn("X  ·  THE HOUSE", runs)
                    self.assertTrue([r for r in runs if r.startswith("O  ·  ") and "PLAYER" in r or
                                     r == "O  ·  EVERYONE ELSE"], "GitHub as O")
                    self.assertFalse([r for r in runs if r.startswith(("O  ·  THE HOUSE", "X  ·  EVERY"))])

    def test_each_side_locks_a_square_with_a_ghost_before_the_first_mark_the_side_drawn_first(self):
        st = TT.state(TT_FRESH)
        self.assertEqual((st["ghosting"], st["ghosts"], st["to_move"], st["alert"], st["stage"], st["last"]),
                         (True, [], "github", "place a ghost", "ghosts", None))
        st = TT.state(TT_GHOST)
        self.assertEqual((st["ghosts"], st["to_move"], st["last"]["side"], st["last"]["number"]),
                         (["d6"], "house", "github", "G"))
        st = TT.state(TT_GHOSTS)
        self.assertEqual((st["ghosting"], st["ghosts"], st["first_mark"], st["to_move"], st["last"]["side"],
                          st["stage"], st["cells"]), (False, ["h8", "d6"], "house", "house", "house", "", {}))
        self.assertIn("Ghosts lock d6. After G. d6: a ghost locks the upper left corner of the centre board. It is"
                      " @tannergolden's turn to place a ghost, due by 21 Oct.", E.alt("tictac", TT_GHOST))
        self.assertIn("Ghosts lock h8 and d6. After G... h8: a ghost locks the centre of the upper right board. The"
                      " Arbiter drew @tannergolden to make the first mark. It is @tannergolden's turn as X, in any"
                      " open board, due by 21 Oct.", E.alt("tictac", TT_GHOSTS))
        # the band says the ghosts are going down, and the panel which side places the first and who drew it
        for d, band in ((TT_FRESH, "GAME 11  ·  GHOSTS"), (TT_GHOST, "GAME 11  ·  GHOSTS"),
                        (TT_GHOSTS, "GAME 11  ·  MOVE 1")):
            with self.subTest(board=name(d)):
                self.assertIn(band, lettered(d, STANDARD))
                self.assertIn(band.split("  ·  ")[1], lettered(d, "blackprint", "narrow-still"))
        runs = lettered(TT_FRESH, STANDARD)
        for said in ("PLACE A GHOST", "FIRST MOVE", "G. ", "GITHUB PLACES THE FIRST GHOST", "DRAWN BY THE ARBITER"):
            self.assertIn(said, runs)
        self.assertEqual(lettered(TT_GHOSTS, STANDARD)[-6:-1], ["G.", "D6", "H8", "@HOLLYFENWICK", "1."],
                         "the ghosts' row first on the score sheet, in the order they went down")
        # a ghost goes down only while the ghosts do, two of them, and no mark goes down before them
        board = TT_GHOSTS["board"]
        self.assertIn("board has 3 ghosts: the Ghost Rule locks two squares, one for each side",
                      reasons(TT, {**TT_GHOSTS, "board": board[:-9] + "G........"}))
        self.assertIn("board has 1 mark and 1 ghost: no mark goes down until both ghosts are",
                      reasons(TT, {**TT_GHOST, "board": TT_GHOST["board"][:-9] + "X........"}))
        self.assertIn("last: move 'i8' is a ghost's square, and the last move is a ghost's only before the first mark",
                      reasons(TT, {**TT_GITHUB, "last": {**TT_GITHUB["last"], "move": "i8"}}))
        self.assertIn("last: move 'e5' is a ghost's square, and the last move is a ghost's only before the first"
                      " mark, on a square the board has a ghost on",
                      reasons(TT, {**TT_GHOST, "last": {**TT_GHOST["last"], "move": "e5"}}))
        self.assertIn("alert 'any board' is not where the side to move must play: place a ghost",
                      reasons(TT, {**TT_GHOST, "alert": "any board"}))

    def test_a_ghost_just_placed_is_boxed_over_its_square_as_any_last_move_is(self):
        # A ghost covers the square it locks, so the box that marks the last move goes on again over it, at its edge,
        # and the ghost just placed is told from the one placed before it, in the standard theme and in a print.
        game = E.game_of("tictac")
        for tone in (STANDARD, "blackprint"):
            skin = TT.Standard if tone == STANDARD else TT.Print
            for d in GAMES["tictac"][1]:
                st = game.state(game.describe(d))
                for small, variant in ((False, "still"), (True, "narrow-still")):
                    boxed = []

                    def ghost_mark(self, x, y, q, *a, _drawn=skin.ghost_mark, _boxed=boxed, **k):
                        _boxed.append((round(x, 1), round(y, 1)))
                        return _drawn(self, x, y, q, *a, **k)
                    with mock.patch.object(skin, "ghost_mark", ghost_mark):
                        E.draw("tictac", d, tone, "day", variant)
                    x0, y0, n = AT[small]
                    last = st["last"]
                    want = ([tuple(round(v, 1) for v in TT.layout.cell_box(last["cell"], x0, y0, n, small)[:2])]
                            if last and last["ghost"] else [])
                    with self.subTest(board=name(d), tone=tone, variant=variant):
                        self.assertEqual(boxed, want)

    def test_after_dark_a_closed_board_is_washed_in_charcoal_and_a_won_boards_o_edged_in_ash(self):
        # Under a film of the night's black card a won board's black O stood no higher than the O's under it: after
        # dark the film is the band's charcoal, pushing back every mark under it alike, and the board's own O is
        # edged in ash, so it stands above its board. By day the film is the card's own.
        film = f'fill="{P.hexof("charcoal")}" fill-opacity=".8"'
        dark = E.draw("tictac", TT_WON, STANDARD, "dark", "still")
        day = E.draw("tictac", TT_WON, STANDARD, "day", "still")
        self.assertIn(film, dark)
        self.assertNotIn(film, day)
        self.assertIn(f'stroke="{P.hexof("ash")}" stroke-width', dark)
        self.assertNotIn(f'stroke="{P.hexof("ash")}" stroke-width', day)

    def test_a_mark_sends_the_other_side_to_the_board_in_its_place_and_the_plate_says_where(self):
        st = TT.state(TT_GITHUB)
        self.assertEqual((st["last"]["cell"], st["target"], st["alert"]), ("i7", (2, 0), "lower right board"))
        self.assertIn("It is GitHub's turn as O, in the lower right board, due by 22 Nov.", E.alt("tictac", TT_GITHUB))
        # sent to a board already won, the side to move may play any open board
        st = TT.state(TT_HOUSE)
        self.assertEqual((st["last"]["cell"], st["boards"][(0, 0)], st["target"], st["alert"]),
                         ("d1", "X", None, "any board"))
        self.assertIn("It is @tannergolden's turn as X, in any open board, due by 18 Nov.", E.alt("tictac", TT_HOUSE))
        for d, plate in ((TT_GITHUB, "LOWER RIGHT BOARD"), (TT_HOUSE, "ANY BOARD"), (TT_GHOST, "PLACE A GHOST")):
            for tone in (STANDARD, "blackprint"):
                with self.subTest(board=name(d), tone=tone):
                    self.assertIn(plate, lettered(d, tone))
        self.assertIn("alert 'upper left board' is not where the side to move must play: lower right board",
                      reasons(TT, {**TT_GITHUB, "alert": "upper left board"}))
        self.assertIn("alert 'lower left board' is not where the side to move must play: any board",
                      reasons(TT, {**TT_HOUSE, "alert": "lower left board"}))
        self.assertIn("alert: a game under way says where the side to move must play",
                      reasons(TT, {k: v for k, v in TT_GITHUB.items() if k != "alert"}))

    def test_what_the_board_is_drawn_from_is_checked(self):
        self.assertIn("is not nine rows of nine X, O, G or dots", reasons(TT, {**TT_GITHUB, "board": "XXX/.../..."}))
        self.assertIn("last: move 'Xf1' is not a mark the board has where it says",
                      reasons(TT, {**TT_GITHUB, "last": {**TT_GITHUB["last"], "move": "Xf1"}}))
        self.assertIn("last: move 'Oa9' is not the mark of the side that moved last",
                      reasons(TT, {**TT_GITHUB, "last": {**TT_GITHUB["last"], "move": "Oa9"}}))
        self.assertIn("last: a board with marks on it names the last of them",
                      reasons(TT, {k: v for k, v in TT_GITHUB.items() if k != "last"}))
        # a board closes once it is won, so it never holds three in a row for both marks
        both = {"kind": "tictac", "places": "house", "opens": "house", "game": 3, "move": 4, "players": 1,
                "board": "........./........./........./........./........./G.......G/OOO....../........./XXX......",
                "due": "20 Oct", "alert": "upper right board", "history": [["G", "a4", "i4", ""]],
                "last": {"move": "Oc3", "words": "O takes the upper right corner of the lower left board",
                         "by": "@imvale", "when": "14 Oct"}}
        self.assertEqual(TT.check(both), ["board a1 has three in a row for both marks: a board closes once it is won"])

    def test_nothing_that_would_help_a_player_choose_is_taken(self):
        # a call to block, and a move offered with the mark that says it wins: each turned away, with a word on why
        self.assertIn("alert 'must block' is not what this game's turn can say",
                      reasons(TT, {**TT_GITHUB, "alert": "must block"}))
        won = row("tictac", "🔳", "Take the Centre of the Lower Right Board!", "Oh2#",
                  "O takes the centre of the lower right board", 9, 51)
        self.assertIn("'Oh2#' says what the move would do", reasons(TT, {**TT_GITHUB, "moves": [won]}))
        self.assertIn("+ is gone", reasons(TT, {**TT_GITHUB, "last": {**TT_GITHUB["last"], "move": "Xi7+"}}))
        self.assertIn("+ is gone", reasons(TT, {**TT_GITHUB, "history": [[23, "Of9", "Xh9+", "@hollyfenwick"],
                                                                         *TT_GITHUB["history"][1:]]}))
        self.assertEqual(TT.check(TT_WON_GITHUB), [], "the score sheet still marks the move that won")

    def test_a_won_game_names_its_three_boards_and_only_a_won_game_has_one(self):
        self.assertIn("line: a won game names its winning line, its three boards", reasons(TT, {**TT_WON, "line": []}))
        self.assertIn("line ['a1', 'b1', 'c2'] is three boards in a row, each named as Tic-Tac-Toe names a cell",
                      reasons(TT, {**TT_WON, "line": ["a1", "b1", "c2"]}))
        self.assertIn("line: the winning line is three boards the winner has won, and only a won game has one",
                      reasons(TT, {**TT_WON, "line": ["a1", "b1", "c1"]}))
        self.assertIn("and only a won game has one", reasons(TT, {**TT_GITHUB, "line": ["a1", "b1", "c1"]}))
        self.assertEqual(TT.check({**TT_WON, "line": ["c2", "b2", "a2"]}), [], "a line either way along")
        won = TT.state(TT_WON)
        self.assertEqual((won["result"]["winner"], won["line"], won["won"], won["alert"], won["target"]),
                         ("house", [(0, 1), (1, 1), (2, 1)], {"house": 3, "github": 2}, "", None))
        self.assertIn("After 27... Xi4#: X takes the lower right corner of the right board. @tannergolden won with"
                      " three boards in a row. Game 9 opens 17 Nov. Boards won: X 3, O 2.", E.alt("tictac", TT_WON))
        self.assertIn("After 25. Oh2#: O takes the centre of the lower right board. GitHub won with three boards in a"
                      " row.", E.alt("tictac", TT_WON_GITHUB))

    def test_a_drawn_game_has_no_line_of_three_boards_left_for_either_side(self):
        self.assertEqual(TT.check(TT_DRAWN), [])
        st = TT.state(TT_DRAWN)
        self.assertEqual((st["won"], st["drawn"], st["line"]), ({"house": 3, "github": 4}, 1, []))
        self.assertIn("The game was drawn, with no line of three boards left for either side. Game 8 opens 21 Nov."
                      " Boards won: X 3, O 4, 1 drawn.", E.alt("tictac", TT_DRAWN))
        self.assertIn("a game ended by no line left is drawn, its winner null",
                      reasons(TT, {**TT_DRAWN, "result": {"winner": "github", "how": "no line left"}}))

    def test_the_panel_counts_the_boards_each_side_has_won_and_says_where_the_ghosts_stand(self):
        for d, count in ((TT_GHOST, ["GHOST D6", "X · HOUSE", "0", "O · GITHUB", "0"]),
                         (TT_GITHUB, ["GHOSTS I8 · G6", "X · HOUSE", "1", "O · GITHUB", "3"]),
                         (TT_DRAWN, ["GHOSTS I5 · H2  ·  1 DRAWN", "X · HOUSE", "3", "O · GITHUB", "4"])):
            for tone in (STANDARD, "blackprint"):
                runs = lettered(d, tone)
                at = runs.index("BOARDS WON")
                with self.subTest(board=name(d), tone=tone):
                    self.assertEqual(runs[at + 1:at + 6], count)


class Pentago(unittest.TestCase):
    def test_the_holes_are_named_as_chess_names_squares_in_four_quarters_that_turn(self):
        self.assertEqual(PG.placement(PG_GHOSTS["board"]), {"f3": "G", "b1": "G"})
        self.assertEqual([PG.game.quarter_of(c) for c in ("a6", "f4", "c1", "d3")], ["ul", "ur", "ll", "lr"])
        self.assertEqual(PG.game.quarter_cells("lr"), ["d3", "e3", "f3", "d2", "e2", "f2", "d1", "e1", "f1"])
        # a quarter turned clockwise as the board is seen carries its upper left corner to its upper right, and
        # anticlockwise to its lower left; its centre and every other quarter's holes stay where they are
        self.assertEqual([PG.game.landed("d6", "ur", way) for way in ("cw", "acw")], ["f6", "d4"])
        self.assertEqual([PG.game.landed(c, "ur", "cw") for c in ("e5", "a1")], ["e5", "a1"])
        self.assertEqual(PG.game.turned({"d4": "G", "a1": "W"}, "ur", "cw"), {"d6": "G", "a1": "W"},
                         "a ghost turns with its quarter")

    def test_the_house_plays_white_and_github_black_whoever_sets_first_and_whoever_opens(self):
        self.assertEqual((PG.game.material_of("house"), PG.game.material_of("github")), ("light", "dark"))
        for d, places, turn, said in ((PG_FRESH, "house", "house", "It is @tannergolden's turn to set a ghost"),
                                      (PG_GHOST, "house", "github", "It is GitHub's turn to set a ghost"),
                                      (PG_GHOSTS, "house", "github", "It is GitHub's turn as Black"),
                                      (PG_GHOSTS_HOUSE, "github", "house", "It is @tannergolden's turn as White"),
                                      (PG_GITHUB, "house", "github", "It is GitHub's turn as Black"),
                                      (PG_HOUSE, "github", "house", "It is @tannergolden's turn as White")):
            st = PG.state(d)
            alt = E.alt("pentago", d)
            with self.subTest(board=name(d)):
                self.assertEqual((st["places"], st["to_move"]), (places, turn))
                self.assertIn("@tannergolden plays White and GitHub Black, under the Ghost Rule", alt)
                self.assertIn(said, alt)
        self.assertIn("light is gone: the house always plays White and GitHub Black, and places and opens name the"
                      " sides the Arbiter drew", reasons(PG, {**PG_GITHUB, "light": "house"}))
        self.assertIn("places None is the side the Arbiter drew to set the first ghost: house, which plays White, or"
                      " github, which plays Black", reasons(PG, {k: v for k, v in PG_GITHUB.items() if k != "places"}))
        self.assertIn("opens None is the side the Arbiter drew to set the first marble once both ghosts were down",
                      reasons(PG, {k: v for k, v in PG_GHOSTS.items() if k != "opens"}))
        self.assertIn("opens: the Arbiter draws the side that sets the first marble once both ghosts are down",
                      reasons(PG, {**PG_GHOST, "opens": "house"}))
        # the opener's colour leads: White may have one more only in a game the house was drawn to open
        self.assertIn("board has 12 White marbles and 13 Black: White set first, the Arbiter having drawn house to"
                      " open, so it has as many as Black or one more", reasons(PG, {**PG_WON_GITHUB, "opens": "house"}))

    def test_every_word_says_white_and_black_the_houses_white_first(self):
        for d in GAMES["pentago"][1]:
            for variant in ("still", "narrow-still"):
                runs = lettered(d, STANDARD, variant)
                racks = [r for r in runs if r.startswith(("WHITE ·", "BLACK ·"))]
                with self.subTest(board=name(d), variant=variant):
                    self.assertEqual(racks, ["WHITE · HOUSE", "BLACK · GITHUB"], "the house's White on top")
                    self.assertIn("WHITE  ·  THE HOUSE", runs)
                    self.assertTrue([r for r in runs if r.startswith("BLACK  ·  ")], "GitHub as Black")
                    self.assertFalse([r for r in runs if re.search(r"\b(LIGHT|DARK)\b", r)])
            with self.subTest(board=name(d)):
                self.assertNotRegex(E.alt("pentago", d), r"\b([Ll]ight|[Dd]ark)\b")
                self.assertNotRegex(said(ED.block("pentago", d, "assets/elements")), r"\b([Ll]ight|[Dd]ark)\b")

    def test_each_side_sets_a_ghost_before_the_first_marble_and_a_ghost_turns_with_its_quarter(self):
        st = PG.state(PG_FRESH)
        self.assertEqual((st["ghosting"], st["ghosts"], st["to_move"], st["alert"], st["stage"], st["left"]),
                         (True, [], "house", "set a ghost", "ghosts", {"house": 17, "github": 17}))
        st = PG.state(PG_GHOST)
        self.assertEqual((st["ghosts"], st["to_move"], st["last"]["side"], st["last"]["number"], st["last"]["by"]),
                         (["e1"], "github", "house", "G", "the Arbiter"))
        self.assertIn("After G. e1, the Arbiter's move for @tannergolden: a ghost on e1, the bottom edge of the lower"
                      " right quarter. It is GitHub's turn to set a ghost, due by 27 Oct.", E.alt("pentago", PG_GHOST))
        self.assertIn("After G... b1: a ghost on b1, the bottom edge of the lower left quarter. The Arbiter drew GitHub"
                      " to set the first marble. It is GitHub's turn as Black, due by 21 Oct.",
                      E.alt("pentago", PG_GHOSTS))
        for d, band in ((PG_FRESH, "GAME 5  ·  GHOSTS"), (PG_GHOST, "GAME 5  ·  GHOSTS"),
                        (PG_GHOSTS, "GAME 6  ·  MOVE 1")):
            with self.subTest(board=name(d)):
                self.assertIn(band, lettered(d, STANDARD))
        runs = lettered(PG_FRESH, "blackprint")
        for said in ("SET A GHOST", "FIRST MOVE", "G. ", "@TANNERGOLDEN SETS THE FIRST GHOST", "DRAWN BY THE ARBITER"):
            self.assertIn(said, runs)
        # game 4's ghosts went down on a2 and d2, and its quarters' turns have carried them to b1 and e1: the panel
        # says where they stand now; game 3's on b5, a quarter's centre, stays put
        self.assertEqual(PG.state(PG_GITHUB)["ghosts"], ["b1", "e1"])
        self.assertIn("GHOSTS B1 · E1", lettered(PG_GITHUB, STANDARD))
        self.assertEqual((PG_GHOSTS_HOUSE["history"][0][1], PG.state(PG_WON)["ghosts"]), ("b5", ["b5", "f1"]))
        # two ghosts, both down before the first marble, the plate saying so while they go down and never after
        board = PG_GHOSTS["board"]
        self.assertIn("board has 3 ghosts: the Ghost Rule sets two, one for each side",
                      reasons(PG, {**PG_GHOSTS, "board": "G" + board[1:]}))
        self.assertIn("board has 1 marble and 1 ghost: no marble goes down until both ghosts are",
                      reasons(PG, {**PG_GHOST, "board": "W" + PG_GHOST["board"][1:]}))
        self.assertIn("last: move 'b1' is a ghost's hole, and the last move is a ghost's only before the first marble",
                      reasons(PG, {**PG_GITHUB, "last": {**PG_GITHUB["last"], "move": "b1"}}))
        self.assertIn("alert: while the ghosts go down, the plate says so: set a ghost",
                      reasons(PG, {k: v for k, v in PG_GHOST.items() if k != "alert"}))
        self.assertIn("alert: once both ghosts are down a turn calls nothing out",
                      reasons(PG, {**PG_GHOSTS, "alert": "set a ghost"}))

    def test_a_move_sets_a_marble_and_then_turns_a_quarter_everything_on_it_turning_with_it(self):
        # The house set a3 and turned its own quarter clockwise, carrying the marble to c3: the sheet sets it in a3,
        # rings the hole it lands in, and turns the quarter from where it stood before
        st = PG.state(PG_GIVEN)
        last = st["last"]
        self.assertEqual((last["cell"], last["quarter"], last["way"], last["landed"], last["turned"], last["side"]),
                         ("a3", "ll", "cw", "c3", True, "house"))
        self.assertEqual((st["before"]["a3"], st["cells"]["c3"]), ("W", "W"))
        self.assertEqual(PG.game.turned(st["before"], "ll", "cw"), st["cells"], "the board before the turn, turned")
        self.assertIn("After 15. a3-ll-cw#: a white marble on a3, then the lower left quarter turns clockwise.",
                      E.alt("pentago", PG_GIVEN))
        self.assertIn("After 12... a3-lr-cw: a black marble on a3, then the lower right quarter turns clockwise.",
                      E.alt("pentago", PG_HOUSE))
        self.assertIn("last: move 'd3-lr-cw' does not leave a marble of the side that moved last where its marble"
                      " lands", reasons(PG, {**PG_HOUSE, "last": {**PG_HOUSE["last"], "move": "d3-lr-cw"}}))
        self.assertIn("last: a board with marbles on it names the last move",
                      reasons(PG, {k: v for k, v in PG_HOUSE.items() if k != "last"}))

    def test_a_move_is_written_as_the_sheet_draws_it_its_hole_then_its_quarters_turn(self):
        # The last move and every move on the score sheet: the hole, then a circular arrow the way the quarter went
        # and the quarter's initials, `b5 ↺ LR`; a marble that made five on its own, its hole alone, `d5#`.
        for d in (PG_GITHUB, PG_GIVEN, PG_WON_GITHUB, PG_GHOST):
            written = [d["last"]["move"]] + [m for _, a, b, _ in d["history"] for m in (a, b) if m]
            moves = [PG.game.parse(m) for m in written]
            ways = [m["way"] for m in moves if m["quarter"]]
            for skin, tone in ((PG.Standard, STANDARD), (PG.Print, "blackprint")):
                drawn: list[str] = []

                def turn_glyph(self, x, cy, r, way, role="ink", original=skin.turn_glyph):
                    drawn.append(way)
                    return original(self, x, cy, r, way, role)
                with mock.patch.object(skin, "turn_glyph", turn_glyph):
                    runs = lettered(d, tone)
                with self.subTest(board=name(d), tone=tone):
                    # the panel is set once to measure it and once to draw it, each time every turn its arrow
                    self.assertEqual(drawn, ways * (len(drawn) // len(ways)) if ways else [])
                    self.assertTrue(drawn or not ways)
                    for m in moves:
                        self.assertIn((m["cell"] + ("#" if m["won"] and not m["quarter"] else "")).upper(), runs)
                        if m["quarter"]:
                            self.assertIn(m["quarter"].upper() + ("#" if m["won"] else ""), runs)

    def test_before_the_first_ghost_the_move_to_come_is_written_with_a_ghost_whoever_sets_it(self):
        # The first move under the Ghost Rule is a ghost, whichever side the Arbiter drew to set it, so the panel
        # writes it with a ghost before its hole, never with that side's own marble; once a move is made, never.
        game = E.game_of("pentago")
        for tone in (STANDARD, "blackprint"):
            for d in GAMES["pentago"][1]:
                st = game.state(game.describe(d))
                opened = []

                def opening_glyph(*a, _drawn=PG.layout.opening_glyph, _opened=opened, **k):
                    _opened.append(a)
                    return _drawn(*a, **k)
                with mock.patch.object(PG.layout, "opening_glyph", opening_glyph):
                    E.draw("pentago", d, tone, "day", "still")
                with self.subTest(board=name(d), tone=tone):
                    self.assertEqual(bool(opened), not st["last"])     # drawn, and measured first, or never

    def test_black_written_small_on_a_dark_sheet_is_a_dark_stone_never_a_ring(self):
        # A small Black marble edged light, as it holds on a tray, reads on the night's card as a ring, the sign a
        # reader takes for White: written with its move it is a slate stone edged in gray in the standard theme, and
        # in a print a dot of ink edged faint, with no groove.
        standard = E.draw("pentago", PG_HOUSE, STANDARD, "dark", "still")
        printed = E.draw("pentago", PG_HOUSE, "blackprint", "dark", "still")
        self.assertIn(f'fill="{P.hexof("slate")}" stroke="{P.hexof("gray")}"', standard)
        self.assertIn('stroke-width=".8" stroke-opacity=".38"', printed)
        for svg in (E.draw("pentago", PG_HOUSE, STANDARD, "day", "still"),
                    E.draw("pentago", PG_HOUSE, "blackprint", "day", "still")):
            self.assertNotIn(f'fill="{P.hexof("slate")}" stroke="{P.hexof("gray")}"', svg)
            self.assertNotIn('stroke-width=".8" stroke-opacity=".38"', svg)

    def test_every_marble_casts_its_shadow_on_the_floor_of_its_hole_and_a_ghost_none(self):
        game = E.game_of("pentago")
        for tone in (STANDARD, "blackprint"):
            skin = PG.Standard if tone == STANDARD else PG.Print
            for d in (PG_HOUSE, PG_GHOSTS, PG_FULL):
                st = game.state(game.describe(d))
                cast = []

                def shadow(self, cv, cx, cy, r, _drawn=skin.cast, _cast=cast):
                    _cast.append((cx, cy))
                    return _drawn(self, cv, cx, cy, r)
                with mock.patch.object(skin, "cast", shadow):
                    E.draw("pentago", d, tone, "day", "still")
                with self.subTest(board=name(d), tone=tone):
                    self.assertEqual(len(cast), sum(1 for v in st["cells"].values() if v != PG.game.GHOST))

    def test_each_hole_is_offered_with_its_eight_turns_each_linked_to_its_own_issue(self):
        first = PG_GITHUB["moves"][0]
        self.assertEqual([turn[:2] for turn in first[4]], [list(t) for t in TURNS])
        for bad in (first[4][:7], [*first[4], first[4][0]], first[4][1:] + first[4][:1],
                    [[q, w, url.replace("a6-", "b6-")] for q, w, url in first[4]],
                    [[q, w, url + "&x=1"] for q, w, url in first[4]],
                    [[q.upper(), w, url] for q, w, url in first[4]],
                    [*first[4][:7], ["lr", "acw", first[4][6][2]]]):
            with self.subTest(links=bad[-1][:2]):
                self.assertIn("is not an emoji, a title, a move, its words and its link",
                              reasons(PG, {**PG_GITHUB, "moves": [[*first[:4], bad]]}))
        # a hole is offered as a hole: a move still to play never carries the # the score sheet gives a win
        won = [*first[:2], "e5#", first[3], [[q, w, link("pentago", f"e5-{q}-{w}", 4, 28)] for q, w in TURNS]]
        self.assertIn("'e5#' says what the move would do", reasons(PG, {**PG_GITHUB, "moves": [won]}))

    def test_either_side_can_win_on_a_move_its_own_five_or_the_other_sides_alone(self):
        # The house's own turn made five for GitHub alone, so GitHub won game 2 on the house's move
        self.assertEqual(PG.check(PG_GIVEN), [])
        st = PG.state(PG_GIVEN)
        self.assertEqual((st["last"]["side"], st["result"]["winner"], st["line"]),
                         ("house", "github", ["b1", "b2", "b3", "b4", "b5"]))
        self.assertIn("GitHub won with five in a row, from b1 to b5. Game 3 opens 7 Nov.", E.alt("pentago", PG_GIVEN))
        # a marble that makes five on its own wins before any quarter turns, written as its hole alone
        st = PG.state(PG_WON_GITHUB)
        self.assertEqual((st["last"]["cell"], st["last"]["quarter"], st["last"]["turned"], st["last"]["landed"]),
                         ("d5", None, False, "d5"))
        self.assertIn("After 13. d5#: a black marble on d5. GitHub won with five in a row, from a5 to e5.",
                      E.alt("pentago", PG_WON_GITHUB))
        self.assertIn("@tannergolden won with five in a row, from f2 to f6.", E.alt("pentago", PG_WON))
        # once the marbles go down either side may have won: only the line says which
        flipped = PG.check({**PG_WON, "result": {"winner": "github", "how": "five in a row"}})
        self.assertEqual(flipped, ["line: the winning line is the winner's five marbles, and only a won game has one"])

    def test_a_won_game_names_its_five_and_only_a_won_game_has_one(self):
        self.assertIn("line: a won game names its winning line, its five holes", reasons(PG, {**PG_WON, "line": []}))
        self.assertIn("line ['a1', 'b2', 'c3', 'd4', 'f6'] is five holes in a row",
                      reasons(PG, {**PG_WON, "line": ["a1", "b2", "c3", "d4", "f6"]}))
        self.assertIn("line: the winning line is the winner's five marbles",
                      reasons(PG, {**PG_WON, "line": ["f1", "f2", "f3", "f4", "f5"]}))
        self.assertIn("and only a won game has one", reasons(PG, {**PG_GITHUB, "line": ["f2", "f3", "f4", "f5", "f6"]}))
        self.assertEqual(PG.check({**PG_WON, "line": ["f6", "f5", "f4", "f3", "f2"]}), [], "a line either way along")

    def test_a_drawn_game_is_a_full_board_or_a_turn_that_makes_five_for_both(self):
        for d, said in ((PG_FULL, "The game was drawn on a full board. Game 2 opens 10 Nov."),
                        (PG_BOTH, "The game was drawn, a turn making five for both sides. Game 9 opens 3 Nov.")):
            with self.subTest(board=name(d)):
                self.assertEqual(PG.check(d), [])
                self.assertIn(said, E.alt("pentago", d))
        self.assertEqual(PG.state(PG_FULL)["left"], {"house": 0, "github": 0}, "seventeen marbles each, all set")
        self.assertIn("a game ended by five for both is drawn, its winner null",
                      reasons(PG, {**PG_BOTH, "result": {"winner": "house", "how": "five for both"}}))

    def test_the_panel_counts_each_sides_marbles_left_and_says_where_the_ghosts_stand_now(self):
        for d, count in ((PG_FRESH, ["WHITE · HOUSE", "17", "BLACK · GITHUB", "17"]),
                         (PG_GITHUB, ["GHOSTS B1 · E1", "WHITE · HOUSE", "4", "BLACK · GITHUB", "5"]),
                         (PG_FULL, ["GHOSTS B6 · D5", "WHITE · HOUSE", "0", "BLACK · GITHUB", "0"])):
            for tone in (STANDARD, "blackprint"):
                runs = lettered(d, tone)
                at = runs.index("MARBLES LEFT")
                with self.subTest(board=name(d), tone=tone):
                    self.assertEqual(runs[at + 1:at + 1 + len(count)], count)

    def test_nothing_that_would_help_a_player_choose_is_taken(self):
        # once the ghosts are down a turn calls nothing out, a call to block least of all
        self.assertIn("alert: once both ghosts are down a turn calls nothing out, since a call to block would tell"
                      " the side to move where to go", reasons(PG, {**PG_GITHUB, "alert": "must block"}))
        self.assertIn("+ is gone", reasons(PG, {**PG_GITHUB, "last": {**PG_GITHUB["last"], "move": "b5-lr-acw+"}}))
        self.assertEqual(PG.check(PG_WON), [], "the score sheet still marks the move that won")


class Finished(unittest.TestCase):
    """A finished game keeps its final board up for two days: the result on the turn's plate, the winning line
    where the game has one, the day the fresh board comes, and nothing left to play."""

    BOARDS = (TT_WON, TT_WON_GITHUB, TT_DRAWN, PG_WON, PG_WON_GITHUB, PG_GIVEN, PG_FULL, PG_BOTH, CK_WON, CK_DRAWN)

    def test_a_finished_board_offers_no_move_and_only_it_has_a_next_day(self):
        moves = {"tictac": TT_GITHUB, "pentago": PG_GITHUB, "checkers": CK_GITHUB}
        for d in self.BOARDS:
            pkg = GAMES[d["kind"]][0]
            with self.subTest(board=name(d)):
                self.assertIn("a finished board offers no move",
                              reasons(pkg, {**d, "moves": moves[d["kind"]]["moves"]}))
                self.assertIn("next '32 Oct' is not a day", reasons(pkg, {**d, "next": "32 Oct"}))
        for d in moves.values():
            with self.subTest(board=name(d)):
                self.assertIn("a game under way has none", reasons(GAMES[d["kind"]][0], {**d, "next": "14 Oct"}))

    def test_only_the_side_that_moved_last_can_have_won_save_in_pentago_and_each_end_is_won_or_drawn(self):
        self.assertIn("the winner is the side that made the last move, house",
                      reasons(TT, {**TT_WON, "result": {"winner": "github", "how": "three boards in a row"}}))
        self.assertIn("the winner is the side that made the last move, github",
                      reasons(TT, {**TT_WON_GITHUB, "result": {"winner": "house", "how": "three boards in a row"}}))
        self.assertIn("a game ended by three boards in a row has a winner",
                      reasons(TT, {**TT_WON, "result": {"winner": None, "how": "three boards in a row"}}))
        self.assertIn("three boards in a row, no line left",
                      reasons(TT, {**TT_WON, "result": {"winner": "house", "how": "three in a row"}}))
        self.assertNotIn("the winner is the side that made the last move",
                         reasons(PG, {**PG_GIVEN, "result": {"winner": "house", "how": "five in a row"}}))
        self.assertIn("a game ended by five in a row has a winner",
                      reasons(PG, {**PG_WON, "result": {"winner": None, "how": "five in a row"}}))
        self.assertIn("five in a row, five for both, a full board",
                      reasons(PG, {**PG_WON, "result": {"winner": "house", "how": "four in a row"}}))
        self.assertIn("result is how the game ended", reasons(CK, {**CK_WON, "result": {"winner": "house"}}))
        self.assertIn("no move left, repetition, forty moves",
                      reasons(CK, {**CK_WON, "result": {"winner": "house", "how": "checkmate"}}))
        self.assertIn("a finished board has nothing left to block", reasons(CK, {**CK_WON, "alert": "must jump"}))
        self.assertIn("a finished board has nothing left to block", reasons(TT, {**TT_WON, "alert": "any board"}))

    def test_its_plate_says_who_won_and_how_and_when_the_fresh_board_comes(self):
        for d, label in ((TT_WON, "@tannergolden wins"), (TT_WON_GITHUB, "GitHub wins"), (TT_DRAWN, "drawn"),
                         (PG_WON, "@tannergolden wins"), (PG_WON_GITHUB, "GitHub wins"), (PG_GIVEN, "GitHub wins"),
                         (PG_FULL, "drawn"), (PG_BOTH, "drawn"), (CK_WON, "@tannergolden wins"), (CK_DRAWN, "drawn")):
            st = GAMES[d["kind"]][0].state(d)
            self.assertEqual((st["result"]["how"], st["next"], st["alert"]), (d["result"]["how"], d["next"], ""))
            day = d["next"].upper()
            for tone in (STANDARD, "blackprint"):
                for variant in ("still", "narrow-still"):
                    runs = lettered(d, tone, variant)
                    with self.subTest(board=name(d), tone=tone, variant=variant):
                        self.assertIn(label.upper(), runs, "the plate's label")
                        self.assertIn(d["result"]["how"].upper(), runs, "and how, in its second panel")
                        self.assertTrue({f"NEXT GAME {day}", f"NEXT {day}"} & set(runs), "the day the next comes")
                        self.assertFalse([r for r in runs if r.endswith("'S TURN") or r.endswith("…")],
                                         "nobody's turn, and nothing cut")
        self.assertIn("@tannergolden won: GitHub had no move left. Game 5 opens 14 Oct.", E.alt("checkers", CK_WON))
        self.assertIn("The game was drawn by the forty-move rule.", E.alt("checkers", CK_DRAWN))


class Readme(unittest.TestCase):
    def test_each_board_is_folded_under_its_name_and_every_move_folded_under_it(self):
        # no banner stands over the fold: the board's own sheet says whose turn it is
        text = ED.block("tictac", TT_GITHUB, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:tictac:start -->\n<details>\n<summary><b>❌ Tic-Tac"
                                        "</b></summary>\n\n<picture>"))
        self.assertIn("</picture>\n\n<details>\n<summary>⭕ <b>GitHub's Turn</b> · 4 open squares · open to choose one"
                      "</summary>\n\n|  | Move | In words | Play |\n| :-: | :--- | :--- | :-: |\n", text)
        self.assertIn("| 🔳 | **Take the Centre of the Lower Right Board!** `Oh2` | O takes the centre of the lower"
                      f" right board | [Play ↗]({link('tictac', 'h2', 9, 51)}) |", text)
        self.assertTrue(text.endswith(f"</details>\n\n{TT_GITHUB['note']}\n\n</details>\n"
                                      "<!-- markdown:element:tictac:end -->"))
        text = ED.block("pentago", PG_GITHUB, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:pentago:start -->\n<details>\n<summary><b>🌀 Pentago"
                                        "</b></summary>\n\n<picture>"))
        self.assertIn("</picture>\n\n<details>\n<summary>⚫ <b>GitHub's Turn</b> · 3 empty holes · open to choose one"
                      "</summary>\n\n|  | Hole | In words | Then turn |\n| :-: | :--- | :--- | :--- |\n", text)
        text = ED.block("checkers", CK_OPENING, "assets/elements")
        self.assertIn("<summary>⛂ <b>GitHub's Turn</b> · 2 legal moves · open to choose one</summary>", text)

    def test_pentagos_list_links_every_turn_of_every_hole_and_a_ghosts_hole_once(self):
        # ↻ for a quarter turned clockwise and ↺ anticlockwise, each with the quarter's initials, and every one its
        # own move's issue; a ghost's hole is one choice, and its row one link
        turns = " ".join(f"[{'↻' if w == 'cw' else '↺'}&#8202;{q.upper()}]({link('pentago', f'a6-{q}-{w}', 4, 28)})"
                         for q, w in TURNS)
        self.assertIn("| ⚫ | **Take the Upper Left Corner of the Upper Left Quarter!** `a6` | A black marble on a6,"
                      f" then a quarter turns | {turns} |\n", ED.block("pentago", PG_GITHUB, "assets/elements"))
        self.assertIn("| 👻 | **Ghost the Upper Left Corner of the Upper Left Quarter!** `a6` | A ghost on a6, the"
                      f" upper left corner of the upper left quarter | [Play ↗]({link('pentago', 'a6', 5, 1)}) |\n",
                      ED.block("pentago", PG_FRESH, "assets/elements"))
        # and neither is linked the other's way: a marble's hole with one link would play no turn, and a ghost's
        # with eight would offer turns the ghosts never take
        marble, ghost = PG_GITHUB["moves"][0], PG_FRESH["moves"][0]
        one = {**PG_GITHUB, "moves": [[*marble[:4], link("pentago", marble[2], 4, 28)], *PG_GITHUB["moves"][1:]]}
        eight = {**PG_FRESH, "moves": [[*ghost[:4], marble[4]], *PG_FRESH["moves"][1:]]}
        for d in (one, eight):
            with self.subTest(board=name(d)):
                self.assertIn("is not an emoji, a title, a move, its words and its link", reasons(PG, d))
        self.assertEqual((PG.check(PG_GITHUB), PG.check(PG_FRESH)), ([], []))

    def test_the_side_to_move_is_signed_with_what_it_plays_both_ways_round(self):
        # the house's sign is ❌, ⚪ or ⛀ and GitHub's ⭕, ⚫ or ⛂, whichever side placed first or opened
        for d, said in ((TT_FRESH, "⭕ <b>GitHub's Turn</b> · 3 squares to lock ·"),
                        (TT_GHOST, "❌ <b>@tannergolden's Turn</b> · 3 squares to lock ·"),
                        (TT_GHOSTS, "❌ <b>@tannergolden's Turn</b> · 3 open squares ·"),
                        (TT_GHOSTS_GITHUB, "⭕ <b>GitHub's Turn</b> · 3 open squares ·"),
                        (TT_GITHUB, "⭕ <b>GitHub's Turn</b> · 4 open squares ·"),
                        (TT_HOUSE, "❌ <b>@tannergolden's Turn</b> · 3 open squares ·"),
                        (dict(TT_GITHUB, moves=TT_GITHUB["moves"][:1]), "⭕ <b>GitHub's Turn</b> · 1 open square ·"),
                        (dict(TT_FRESH, moves=TT_FRESH["moves"][:1]), "⭕ <b>GitHub's Turn</b> · 1 square to lock ·"),
                        (PG_FRESH, "⚪ <b>@tannergolden's Turn</b> · 3 holes for a ghost ·"),
                        (PG_GHOST, "⚫ <b>GitHub's Turn</b> · 3 holes for a ghost ·"),
                        (PG_GHOSTS, "⚫ <b>GitHub's Turn</b> · 3 empty holes ·"),
                        (PG_GHOSTS_HOUSE, "⚪ <b>@tannergolden's Turn</b> · 3 empty holes ·"),
                        (PG_GITHUB, "⚫ <b>GitHub's Turn</b> · 3 empty holes ·"),
                        (PG_HOUSE, "⚪ <b>@tannergolden's Turn</b> · 3 empty holes ·"),
                        (dict(PG_HOUSE, moves=PG_HOUSE["moves"][:1]),
                         "⚪ <b>@tannergolden's Turn</b> · 1 empty hole ·"),
                        (dict(PG_GHOST, moves=PG_GHOST["moves"][:1]), "⚫ <b>GitHub's Turn</b> · 1 hole for a ghost ·"),
                        (CK_GITHUB, "⛂ <b>GitHub's Turn</b> · 1 legal move ·"),
                        (CK_OPENING, "⛂ <b>GitHub's Turn</b> · 2 legal moves ·")):
            with self.subTest(board=name(d), moves=len(d["moves"])):
                self.assertIn(f"<summary>{said}", ED.block(d["kind"], d, "assets/elements"))
        for d in (TT_GHOST, TT_GHOSTS, TT_HOUSE, PG_FRESH, PG_GHOSTS_HOUSE, PG_HOUSE):
            with self.subTest(board=name(d)):
                self.assertIn("only @tannergolden can play these</summary>", ED.block(d["kind"], d, "assets/elements"))
        white_turn = dict(CK_CROWNED, fen="W:WK1,20,21,24,28,30:B5,9,12,17,18", move=19, history=[
            [18, "10x17", "19x10x1", "@tokafor"], [19, "5-9", "", "@imvale"]],
            last={"move": "5-9", "words": "Man from 5 to 9", "by": "@imvale", "when": "10 Oct"},
            moves=[row("checkers", "⚔️", "Jump the Man on 17!", "21x14", "Man from 21 jumps 17, landing on 14", 5, 38)],
            alert="must jump")
        self.assertEqual(CK.check(white_turn), [])
        self.assertIn("<summary>⛀ <b>@tannergolden's Turn</b> · 1 legal move · only @tannergolden can play these"
                      "</summary>", ED.block("checkers", white_turn, "assets/elements"))

    def test_a_long_turn_is_grouped_by_board_or_by_quarter_as_chess_groups_its_moves_by_piece(self):
        # Past ten moves the list is grouped, the boards or the quarters as the board is read, top row first, each
        # with the moves the engine listed in it; a board that is closed, or a quarter with no empty hole, has none.
        for d, unit, groups in (
                (dict(TT_HOUSE, moves=squares("X", HOUSE_SQUARES, 10, 47)), "28 open squares",
                 [("❌", "Upper Left Board", 6), ("❌", "Top Board", 2), ("❌", "Upper Right Board", 5),
                  ("❌", "Left Board", 3), ("❌", "Centre Board", 3), ("❌", "Right Board", 6),
                  ("❌", "Bottom Board", 3)]),
                (dict(TT_FRESH, moves=squares("", EVERY_SQUARE, 11, 1)), "81 squares to lock",
                 [("⭕", f"{place.title()} Board", 9) for place in TT.game.PLACE.values()]),
                (dict(PG_GHOSTS, moves=holes("black", " ".join(c for c in EVERY_HOLE.split() if c not in ("f3", "b1")),
                                             6, 3)), "34 empty holes",
                 [("⚫", "Upper Left Quarter", 9), ("⚫", "Upper Right Quarter", 9), ("⚫", "Lower Left Quarter", 8),
                  ("⚫", "Lower Right Quarter", 8)]),
                (dict(PG_FRESH, moves=holes("", EVERY_HOLE, 5, 1)), "36 holes for a ghost",
                 [("⚪", f"{quarter.title()} Quarter", 9) for quarter in PG.game.QNAME.values()])):
            with self.subTest(board=name(d)):
                self.assertEqual(E.game_of(d["kind"]).check(d), [])
                text = ED.block(d["kind"], d, "assets/elements")
                self.assertIn(f"· {unit} ·", text)
                self.assertEqual(re.findall(r"<details>\n<summary>([^<]*?)</summary>", text),
                                 [f"{sign} {title} · {n} moves" for sign, title, n in groups])
                self.assertNotIn("<details open>", text, "every group folded shut, as the list they are in is")

    def test_a_board_before_its_first_mark_or_marble_says_who_the_arbiter_drew(self):
        self.assertEqual(E.alt("tictac", TT_FRESH), "Tic-Tac: game 11, the ghosts. Game 11 of @tannergolden against"
                         " GitHub, @tannergolden plays X and GitHub O, under the Ghost Rule. It is GitHub's turn to"
                         " place a ghost, due by 20 Oct. Boards won: X 0, O 0.")
        self.assertEqual(E.alt("pentago", PG_FRESH), "Pentago: game 5, the ghosts. Game 5 of @tannergolden against"
                         " GitHub, @tannergolden plays White and GitHub Black, under the Ghost Rule. It is"
                         " @tannergolden's turn to set a ghost, due by 20 Oct. The board is empty.")
        for d, drew in ((TT_GHOSTS, "The Arbiter drew @tannergolden to make the first mark."),
                        (TT_GHOSTS_GITHUB, "The Arbiter drew GitHub to make the first mark."),
                        (PG_GHOSTS, "The Arbiter drew GitHub to set the first marble."),
                        (PG_GHOSTS_HOUSE, "The Arbiter drew @tannergolden to set the first marble.")):
            with self.subTest(board=name(d)):
                self.assertIn(drew, E.alt(d["kind"], d))
                self.assertIn("Under the Ghost Rule each side first", ED.block(d["kind"], d, "assets/elements"))
        self.assertNotIn("The Arbiter drew", E.alt("tictac", TT_GITHUB), "said once, before the first mark alone")

    def test_the_sides_are_named_the_houses_first_both_ways_round(self):
        # X, White and White first, whoever placed first or opened: the house's colour never changes
        for d, said in ((TT_GHOSTS, "@tannergolden plays X and GitHub O"),
                        (TT_GHOSTS_GITHUB, "@tannergolden plays X and GitHub O"),
                        (PG_GHOSTS, "@tannergolden plays White and GitHub Black"),
                        (PG_GHOSTS_HOUSE, "@tannergolden plays White and GitHub Black"),
                        (CK_OPENING, "@tannergolden, White: men on 21"),
                        (CK_GITHUB, "@tannergolden, White: men on 11")):
            with self.subTest(board=name(d)):
                self.assertIn(said, E.alt(d["kind"], d))

    def test_a_finished_game_is_its_board_and_its_note_with_nothing_to_play(self):
        # what the picture cannot say, as the engine writes it on a finished board: a link in it is a link
        over_ = ("Game 1 is over, and its final board stays up for two days: game 2 opens 15 Oct, 16:00 EST, and "
                 "nothing can be played until then. Every finished game is kept as a "
                 "[PDN](https://github.com/tannergolden/tannergolden/tree/HEAD/.github/checkers/games).")
        for d in (*Finished.BOARDS, *(dict(b, note=over_) for b in Finished.BOARDS)):
            text = ED.block(d["kind"], d, "assets/elements")
            with self.subTest(board=name(d), note=d["note"][:20]):
                self.assertEqual(E.game_of(d["kind"]).check(d), [])
                self.assertTrue(text.startswith(f"<!-- markdown:element:{d['kind']}:start -->\n<details>\n<summary><b>"
                                                f"{ED.FOLDS[d['kind']]}</b></summary>\n\n<picture>"))
                self.assertEqual(text.count("<details"), 1, "the game's own fold, and no move in it")
                self.assertTrue(text.endswith(f"</picture>\n\n{d['note']}\n\n</details>\n"
                                              f"<!-- markdown:element:{d['kind']}:end -->"))

    def test_a_long_turn_of_checkers_is_grouped_by_men_and_kings_as_chess_groups_by_piece(self):
        many = [row("checkers", "⛵", f"Make Way {i}!", f"{sq}-{sq + 4}", f"Man from {sq} to {sq + 4}", 6, 1)
                for i, sq in enumerate((5, 6, 7, 8, 9, 10, 11, 12, 9, 10, 11))]
        kings = [row("checkers", "🧭", "Come About!", "14-18", "King from 14 to 18", 6, 1)]
        board = dict(CK_OPENING, fen="B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12,K14",
                     moves=many + kings)
        text = ED.block("checkers", board, "assets/elements")
        self.assertIn("· 12 legal moves ·", text)
        self.assertIn("<details>\n<summary>⛂ Men · 11 moves</summary>", text)
        self.assertIn("<details>\n<summary>⛂ King · 1 move</summary>", text)
        self.assertNotIn("<details open>", text)


if __name__ == "__main__":
    unittest.main()
