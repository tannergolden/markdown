# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games beside chess on @tannergolden's profile: Tic-Tac-Toe, Connect Four and Checkers, drawn as chess is, in
the standard theme and every print, and nowhere but that profile.

Each side's colour is fixed: the house always plays X in Tic-Tac-Toe and White in Connect Four and Checkers, GitHub
always O, or Black. The Arbiter opens Tic-Tac-Toe and Connect Four for a side drawn at random, so each is held to its
boards both ways round: opened for the house, which moves first with X or a White disc, and opened for GitHub, which
moves first with O or a Black disc. GitHub opens Checkers, since Black moves first. Each game has a board under way,
the fresh board whose only move is the Arbiter's opening move (or, in Checkers, the board before Black's first
move), and a finished board, kept up for two days with the result on its plate and nothing left to play. The samples
are legal games, and no sheet says what a move would do: Tic-Tac-Toe's GitHub's turn comes with the house a mark from
three in a row on c2, its house's turn with the house able to win on b3, and its finished board is the house's three
in a row on the diagonal; Connect Four's GitHub's turn comes with the house a disc from four down column 7, its
house's turn with the house able to connect four down column 5, and GitHub won game 3 on the diagonal; Checkers'
GitHub's turn must jump after the house's jump back, which the rules make it do and its sheet says, and its crowned
board is the house's double jump that crowns a White king on Black's back row."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support

from domain.canvas import BUDGET, lint
from domain.elements import checkers as CK
from domain.elements import connectfour as C4
from domain.elements import data as ED
from domain.elements import draw as E
from domain.elements import tictactoe as TTT
from domain.elements.games.skin import Print as GamePrint
from domain.elements.games.skin import Standard as GameStandard
from domain.lettering import Lettering
from domain.prints import PRINTS, STANDARD
from domain.standard import pieces as P

support.install()
DASHES = ("–", "—", "―")
TONES = (STANDARD, *sorted(PRINTS))
NOTE = "The first move to arrive is the one played."


def link(kind: str, code: str, game: int, ply: int) -> str:
    """A move's link: its ready-made issue in tannergolden/play, titled with the move and the ply it answers."""
    return (f"https://github.com/tannergolden/play/issues/new?template=move.yml&title={kind}%3A%20{code}"
            f"%20%C2%B7%20game%20{game}%20%C2%B7%20move%20{ply}")


def row(kind: str, emoji: str, title: str, move: str, words: str, game: int, ply: int, code: str = "") -> list:
    return [emoji, title, move, words, link(kind, code or move.rstrip("+#").lstrip("XO"), game, ply)]


# --------------------------------------------------------------------------- Tic-Tac-Toe
# The Arbiter opened for the house, so X moved first: GitHub's turn as O, the house a mark from three in a row on c2.
TTT_GITHUB = {
    "kind": "tictactoe", "board": "O../XX./O.X", "opens": "house", "game": 9, "move": 3, "players": 4,
    "due": "18 Oct",
    "history": [[1, "Xb2", "Oa1", "@imvale"], [2, "Xc1", "Oa3", "@tokafor"], [3, "Xa2", "", ""]],
    "last": {"move": "Xa2", "words": "X takes the left edge", "by": "@tannergolden", "when": "11 Oct"},
    "moves": [row("tictactoe", "📏", "Mark the Head of the Board!", "Ob3", "O takes the head of the board", 9, 6),
              row("tictactoe", "📏", "Mark the Right Edge!", "Oc2", "O takes the right edge", 9, 6)],
    "prompt": "🟢 **GitHub's turn!** @tannergolden played 3. Xa2. Pick a move below by 18 Oct.", "note": NOTE}
# The Arbiter opened for GitHub, so O moved first: the house's turn as X, b3 a cell it would win on.
TTT_HOUSE = {
    "kind": "tictactoe", "board": "X.X/.O./O.O", "opens": "github", "game": 10, "move": 3, "players": 3,
    "due": "19 Oct",
    "history": [[1, "Ob2", "Xa3", "the Arbiter"], [2, "Oa1", "Xc3", "@tokafor"], [3, "Oc1", "", "@wrencastellan"]],
    "last": {"move": "Oc1", "words": "O takes the lower right corner", "by": "@wrencastellan", "when": "12 Oct"},
    "moves": [row("tictactoe", "📏", "Mark the Head of the Board!", "Xb3", "X takes the head of the board", 10, 6),
              row("tictactoe", "📏", "Mark the Foot of the Board!", "Xb1", "X takes the foot of the board", 10, 6)],
    "prompt": "🛑 **@tannergolden's turn!** GitHub played 3. Oc1. Reply due by 19 Oct.", "note": NOTE}
# A fresh board: the Arbiter opened game 11 for GitHub with O in the centre, and it is the house's turn as X.
TTT_FRESH = {
    "kind": "tictactoe", "board": ".../.O./...", "opens": "github", "game": 11, "move": 1, "players": 0,
    "due": "21 Oct", "history": [[1, "Ob2", "", "the Arbiter"]],
    "last": {"move": "Ob2", "words": "O takes the centre", "by": "the Arbiter", "when": "14 Oct"},
    "moves": [row("tictactoe", "📐", "Mark the Upper Left Corner!", "Xa3", "X takes the upper left corner", 11, 2),
              row("tictactoe", "📏", "Mark the Head of the Board!", "Xb3", "X takes the head of the board", 11, 2)],
    "prompt": "🛑 **@tannergolden's turn!** The Arbiter opened game 11 for GitHub with 1. Ob2, at random.",
    "note": "The Arbiter opens every game for a side drawn at random, with a random first move."}
# The same fresh board the other way round: opened for the house with X, and GitHub to reply as O.
TTT_FRESH_HOUSE = dict(TTT_FRESH, board=".../.../X..", opens="house",
                       last={"move": "Xa1", "words": "X takes the lower left corner", "by": "the Arbiter",
                             "when": "14 Oct"}, history=[[1, "Xa1", "", ""]],
                       moves=[row("tictactoe", "🔳", "Mark the Centre!", "Ob2", "O takes the centre", 11, 2)],
                       prompt="🟢 **GitHub's turn!** The Arbiter opened game 11 for @tannergolden with 1. Xa1, at"
                              " random.")
TTT_WON = {
    "kind": "tictactoe", "board": "X.O/OX./XOX", "opens": "house", "game": 8, "move": 4, "players": 6,
    "history": [[2, "Xa1", "Oc3", "@tokafor"], [3, "Xc1", "Ob1", "@jhalloran"], [4, "Xa3#", "", ""]],
    "last": {"move": "Xa3#", "words": "X takes the upper left corner", "by": "@tannergolden", "when": "10 Oct"},
    "result": {"winner": "house", "how": "three in a row"}, "line": ["a3", "b2", "c1"], "next": "14 Oct",
    "prompt": "🏆 **@tannergolden wins game 8!** X took a3, b2 and c1. Game 9 opens 14 Oct.", "note": NOTE}
# Opened for GitHub, so O moved first, and drawn on a full board after O's fifth mark.
TTT_DRAWN = {
    "kind": "tictactoe", "board": "OXO/OXX/XOO", "opens": "github", "game": 6, "move": 5, "players": 7,
    "history": [[3, "Oc3", "Xc2", "@imvale"], [4, "Ob1", "Xa1", "@tokafor"], [5, "Oa2", "", "@jhalloran"]],
    "last": {"move": "Oa2", "words": "O takes the left edge", "by": "@jhalloran", "when": "5 Oct"},
    "result": {"winner": None, "how": "a full board"}, "next": "14 Oct",
    "prompt": "🤝 **Game 6 is drawn!** Nine marks and no line. Game 7 opens 14 Oct.", "note": NOTE}

# --------------------------------------------------------------------------- Connect Four
# The Arbiter opened for GitHub, so a Black disc dropped first: GitHub's turn, the house a disc from four down column 7.
C4_GITHUB = {
    "kind": "connectfour", "board": "......./..D..../..LD.../..DD.../D.DLLL./L.DLDLL", "opens": "github",
    "game": 4, "move": 9, "players": 7, "due": "18 Oct",
    "history": [[7, "4", "6", "@devonaraki"], [8, "4", "5", "@hollyfenwick"], [9, "", "", ""]],
    "last": {"move": "5", "words": "A White disc down column 5, to row 2", "by": "@tannergolden", "when": "12 Oct"},
    "moves": [row("connectfour", "⬇️", "Drop Down Column 7!", "7", "A Black disc down column 7, to row 2", 4, 17),
              row("connectfour", "⬇️", "Drop Down Column 2!", "2", "A Black disc down column 2, to row 1", 4, 17)],
    "prompt": "🟢 **GitHub's turn!** @tannergolden played 8... ⚪5. Pick a move below by 18 Oct.", "note": NOTE}
# The Arbiter opened for the house, so a White disc dropped first: the house to move, able to win down column 5.
C4_HOUSE = {
    "kind": "connectfour", "board": "......./......./......./..DD.../.LLL.../DDLLDLD", "opens": "house",
    "game": 5, "move": 7, "players": 5, "due": "19 Oct",
    "history": [[5, "3", "3", "@imvale"], [6, "5", "7", "@octocat"], [7, "", "", ""]],
    "last": {"move": "7", "words": "A Black disc down column 7, to row 1", "by": "@octocat", "when": "10 Oct"},
    "moves": [row("connectfour", "⬇️", "Drop Down Column 5!", "5", "A White disc down column 5, to row 2", 5, 13)],
    "prompt": "🛑 **@tannergolden's turn!** GitHub played 6... ⚫7. Reply due by 19 Oct.", "note": NOTE}
# A fresh board: the Arbiter opened game 6 for GitHub down the centre column, and it is the house's turn as White.
C4_FRESH = {
    "kind": "connectfour", "board": "......./......./......./......./......./...D...", "opens": "github",
    "game": 6, "move": 1, "players": 0, "due": "21 Oct",
    "history": [[1, "4", "", "the Arbiter"]],
    "last": {"move": "4", "words": "A Black disc down column 4, to row 1", "by": "the Arbiter", "when": "14 Oct"},
    "moves": [row("connectfour", "⬇️", "Drop Down Column 4!", "4", "A White disc down column 4, to row 2", 6, 2),
              row("connectfour", "⬇️", "Drop Down Column 1!", "1", "A White disc down column 1, to row 1", 6, 2)],
    "prompt": "🛑 **@tannergolden's turn!** The Arbiter opened game 6 for GitHub with 1. ⚫4, at random.",
    "note": "The Arbiter opens every game for a side drawn at random, with a random first move."}
# The same fresh board the other way round: opened for the house with a White disc, and GitHub to reply as Black.
C4_FRESH_HOUSE = dict(C4_FRESH, board="......./......./......./......./......./..L....", opens="house",
                      history=[[1, "3", "", ""]],
                      last={"move": "3", "words": "A White disc down column 3, to row 1", "by": "the Arbiter",
                            "when": "14 Oct"},
                      moves=[row("connectfour", "⬇️", "Drop Down Column 3!", "3", "A Black disc down column 3, to row"
                                 " 2", 6, 2),
                             row("connectfour", "⬇️", "Drop Down Column 1!", "1", "A Black disc down column 1, to row"
                                 " 1", 6, 2)],
                      prompt="🟢 **GitHub's turn!** The Arbiter opened game 6 for @tannergolden with 1. ⚪3, at"
                             " random.")
C4_WON = {
    "kind": "connectfour", "board": "....D../....D../.D..L../.LDLD../.LDDDL./DLLLDL.", "opens": "github",
    "game": 3, "move": 10, "players": 9,
    "history": [[8, "3", "6", "@tokafor"], [9, "3", "2", "@wrencastellan"], [10, "2#", "", "@jhalloran"]],
    "last": {"move": "2#", "words": "A Black disc down column 2, to row 4", "by": "@jhalloran", "when": "10 Oct"},
    "result": {"winner": "github", "how": "four in a row"}, "line": [[2, 4], [3, 3], [4, 2], [5, 1]],
    "next": "14 Oct", "prompt": "🏆 **GitHub wins game 3!** Four Black discs on the diagonal. Game 4 opens 14 Oct.",
    "note": NOTE}

# --------------------------------------------------------------------------- Checkers
# A fresh board: GitHub plays Black, which moves first, so the game opens on GitHub's turn, its clock running.
CK_OPENING = {
    "kind": "checkers", "fen": "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12",
    "game": 6, "move": 1, "players": 0, "due": "21 Oct", "history": [[1, "", "", ""]],
    "kings": {"house": 0, "github": 0},
    "moves": [row("checkers", "👣", "Push the Man From 9 to 13!", "9-13", "Man from 9 to 13", 6, 1),
              row("checkers", "👣", "Push the Man From 9 to 14!", "9-14", "Man from 9 to 14", 6, 1)],
    "prompt": "🟢 **GitHub's turn as Black!** Black opens game 6, by 21 Oct.",
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
    "prompt": "🟢 **GitHub's turn!** @tannergolden played 10... 20x11. Must jump! Pick one below by 18 Oct.",
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
    "prompt": "🟢 **GitHub's turn as Black!** @tannergolden played 18... 19x10x1 and crowned a king, by 17 Oct.",
    "note": "A jump must be taken when there is one."}
# The house's White man took GitHub's last: Black has no move left, and the house wins.
CK_WON = {
    "kind": "checkers", "fen": "B:W10,24,28:B", "game": 4, "move": 31, "players": 12,
    "history": [[29, "7-11", "23-19", "@imvale"], [30, "11-15", "19x10", "@octocat"]],
    "kings": {"house": 1, "github": 2},
    "last": {"move": "19x10", "words": "Man from 19 jumps 15, landing on 10", "by": "@tannergolden", "when": "9 Oct"},
    "result": {"winner": "house", "how": "no move left"}, "next": "14 Oct",
    "prompt": "🏆 **@tannergolden wins game 4!** Black has no move left. Game 5 opens 14 Oct.", "note": NOTE}
CK_DRAWN = {
    "kind": "checkers", "fen": "B:WK30:BK3", "game": 3, "move": 88, "players": 20,
    "history": [[87, "8-3", "26-30", "@octocat"], [88, "", "", ""]], "kings": {"house": 3, "github": 4},
    "last": {"move": "26-30", "words": "King from 26 to 30", "by": "@tannergolden", "when": "8 Oct"},
    "result": {"winner": None, "how": "forty moves"}, "next": "14 Oct",
    "prompt": "🤝 **Game 3 is drawn!** Forty moves each without a capture. Game 4 opens 14 Oct.", "note": NOTE}

GAMES = {"tictactoe": (TTT, (TTT_GITHUB, TTT_HOUSE, TTT_FRESH, TTT_FRESH_HOUSE, TTT_WON, TTT_DRAWN)),
         "connectfour": (C4, (C4_GITHUB, C4_HOUSE, C4_FRESH, C4_FRESH_HOUSE, C4_WON)),
         "checkers": (CK, (CK_OPENING, CK_GITHUB, CK_CROWNED, CK_WON, CK_DRAWN))}
# A board under way, a fresh one and a finished one of each game, drawn in every tone.
EVERY_TONE = (TTT_GITHUB, TTT_FRESH, TTT_WON, C4_HOUSE, C4_FRESH, C4_WON, CK_GITHUB, CK_OPENING, CK_WON)
BOARDS = [d for _, boards in GAMES.values() for d in boards]


def name(d: dict) -> str:
    return f"{d['kind']} game {d['game']} move {d['move']}{' finished' if d.get('result') else ''}"


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

    def test_no_sheet_of_tic_tac_toe_or_connect_four_singles_out_a_cell_a_column_or_a_line(self):
        # nothing the rules make the side to move answer, so nothing clouded or glowing; and the board's faint lines
        # are all eight while a game goes on, whatever stands on them, never only the ones a side could still win on
        lines = []

        def faint(skin, d):
            lines.append(d.count("M"))
            return ""

        def clouded(*_, **__):
            raise AssertionError("a cell or a hole singled out")

        with mock.patch.object(GameStandard, "clouded", clouded), mock.patch.object(GamePrint, "clouded", clouded), \
                mock.patch.object(TTT.Standard, "open_lines", faint), mock.patch.object(TTT.Print, "open_lines", faint):
            for d in GAMES["tictactoe"][1] + GAMES["connectfour"][1]:
                for tone in TONES:
                    for variant in E.variants(d["kind"], d):
                        for theme in ("day", "dark"):
                            lines.clear()
                            E.draw(d["kind"], d, tone, theme, variant)
                            with self.subTest(board=name(d), tone=tone, variant=variant, theme=theme):
                                want = [] if d["kind"] == "connectfour" or d.get("result") else [8]
                                self.assertEqual(lines, want)

    def test_the_still_files_stand_still_and_the_rest_move(self):
        for d in BOARDS:
            for tone in (STANDARD, "blackprint"):
                for variant in E.variants(d["kind"], d):
                    svg = E.draw(d["kind"], d, tone, "day", variant)
                    with self.subTest(board=name(d), tone=tone, variant=variant):
                        (self.assertNotIn if variant.endswith("still") else self.assertIn)("<animate", svg)

    def test_each_is_a_kind_of_its_own_drawn_as_chess_is(self):
        for kind in ("tictactoe", "connectfour", "checkers"):
            fn, variants, klass = E.KINDS[kind]
            self.assertEqual((variants, klass), (("wide", "narrow", "still", "narrow-still"), "board"))
            self.assertIn(kind, ED.OWN_THEMES)
        self.assertEqual(E.GAMES, ("tictactoe", "connectfour", "checkers"))

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

    def test_a_holiday_or_collection_leaves_the_games_in_the_pages_own_theme(self):
        elements = ED.merged({d["kind"]: dict(d) for d in (TTT_GITHUB, C4_HOUSE, CK_GITHUB)}, {},
                             subject="tannergolden")
        printed = ED.render(elements, "blackprint")
        self.assertEqual(ED.render(elements, "blackprint", "halloween"), printed)
        standard = ED.render(elements, STANDARD)
        self.assertEqual(sorted(standard), sorted(printed))
        for key in ("tictactoe", "connectfour", "checkers"):
            self.assertNotEqual(standard[f"{key}-day.svg"], printed[f"{key}-day.svg"])


class Settings(unittest.TestCase):
    def test_each_is_drawn_on_tannergoldens_profile_alone(self):
        section = {d["kind"]: dict(d) for d in (TTT_GITHUB, C4_GITHUB, CK_GITHUB)}
        self.assertEqual(ED.validate(section, {}, subject="tannergolden"), [])
        self.assertEqual(ED.validate(section, {}, subject="TannerGolden"), [])
        for elsewhere in ("octocat", "tannergolden/markdown", ""):
            with self.subTest(subject=elsewhere):
                errors = ED.validate(section, {}, subject=elsewhere)
                for kind in section:
                    self.assertIn(f"{kind}: the {kind} element is drawn on @tannergolden's profile alone", errors)

    def test_what_each_cannot_be_drawn_without_is_named(self):
        for kind, needs in (("tictactoe", "board, opens"), ("connectfour", "board, opens"), ("checkers", "fen")):
            with self.subTest(kind=kind):
                errors = ED.validate({kind: {"kind": kind}}, {}, subject="tannergolden")
                self.assertIn(f"{kind}: a {kind} needs {needs}", errors)

    def test_text_is_text_and_a_number_a_number_within_its_ceiling(self):
        # YAML reads `note: 1984` as a number, `true` as a bool and an all-digit login as an int: each is turned away
        # here rather than reaching the README, which would fail on it.
        for pkg, d in ((TTT, TTT_GITHUB), (C4, C4_GITHUB), (CK, CK_GITHUB)):
            texts = {"note": (1984, True, ["a note"]), "prompt": (1984, {"a": 1}), "due": (18, "32 Oct"),
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
                        self.assertIn(f"{key} {bad!r} is not a number from", " ".join(pkg.check({**d, key: bad})))
                with self.subTest(kind=d["kind"], key=key, fine=999_999_999):
                    self.assertEqual(pkg.check({**d, key: 999_999_999}), [])
            for bad_row in ([True, "", "", ""], [0, "", "", ""], [1_000_000_000, "", "", ""], ["3", "", "", ""]):
                with self.subTest(kind=d["kind"], row=bad_row):
                    self.assertIn("is not a row of a move's number", " ".join(pkg.check({**d, "history": [bad_row]})))

    def test_a_line_of_the_readme_never_opens_a_block_or_shows_an_image(self):
        for pkg, d in ((TTT, TTT_GITHUB), (C4, C4_GITHUB), (CK, CK_GITHUB)):
            for key in ("note", "prompt"):
                for bad in ("```", "# Heading", "- an item", "1. an item", "    code", "---", "[a]: https://x.io"):
                    with self.subTest(kind=d["kind"], key=key, bad=bad):
                        self.assertIn(f"{key} {bad!r} would open a block of its own", " ".join(pkg.check({**d,
                                                                                                    key: bad})))
                self.assertIn(f"{key} shows an image", " ".join(pkg.check({**d, key: "![x](https://x.io/x.png)"})))
                self.assertIn(f"{key} is one line of text", " ".join(pkg.check({**d, key: "a | b"})))

    def test_a_move_links_its_own_ready_made_issue_and_nothing_else(self):
        for pkg, d in ((TTT, TTT_GITHUB), (C4, C4_GITHUB), (CK, CK_GITHUB)):
            other = {"tictactoe": "connectfour", "connectfour": "checkers", "checkers": "tictactoe"}[d["kind"]]
            for bad in ("https://example.com/x", d["moves"][0][4].replace(d["kind"], other),
                        d["moves"][0][4] + "&x=1", d["moves"][0][4].replace("move%20", "move%200")):
                with self.subTest(kind=d["kind"], link=bad[-30:]):
                    self.assertTrue(pkg.check({**d, "moves": [[*d["moves"][0][:4], bad]]}))
        self.assertTrue(TTT.check({**TTT_GITHUB, "moves": [row("tictactoe", "🎯", "Go", "Ob3", "O b3", 9, 6,
                                                                 code="d4")]}), "a cell the game does not have")

    def test_nothing_the_settings_can_hold_makes_the_checks_raise(self):
        hostile = (None, True, False, 0, -1, 1984, 10 ** 30, 1.5, "", "x", "```", [], [1], [[]], {}, {"a": 1},
                   ["x", "y", "z", "w", "v"], [[1, 2], [3, 4], [5, 6], [7, 8]])
        for pkg, d in ((TTT, TTT_GITHUB), (TTT, TTT_WON), (C4, C4_GITHUB), (C4, C4_WON), (CK, CK_GITHUB),
                       (CK, CK_WON)):
            keys = set(d) | {"x", "opens", "light", "dark", "threats", "line", "result", "next", "kings", "alert",
                             "outlook", "board", "fen"}
            for key in sorted(keys):
                for bad in hostile:
                    with self.subTest(kind=d["kind"], key=key, bad=bad):
                        self.assertIsInstance(pkg.check({**d, key: bad}), list)
            for bad in hostile:
                with self.subTest(kind=d["kind"], last=bad):
                    self.assertIsInstance(pkg.check({**d, "last": {k: bad for k in d["last"]}}), list)
                    self.assertIsInstance(pkg.check({**d, "result": {"winner": bad, "how": bad}}), list)


class TicTacToe(unittest.TestCase):
    def test_the_cells_are_named_as_chess_names_squares(self):
        self.assertEqual(TTT.placement("O../XX./O.X"), {"a3": "O", "a2": "X", "b2": "X", "a1": "O", "c1": "X"})

    def test_the_house_plays_x_and_github_o_whichever_side_the_arbiter_opened_for(self):
        # opened for the house, X moves first; opened for GitHub, O does: the marks never change hands
        self.assertEqual((TTT.game.mark_of("house"), TTT.game.mark_of("github")), ("X", "O"))
        for d, opens, turn, said in ((TTT_GITHUB, "house", "github", "after 3. Xa2"),
                                     (TTT_HOUSE, "github", "house", "after 3. Oc1"),
                                     (TTT_FRESH, "github", "house", "after 1. Ob2, the Arbiter's move for GitHub"),
                                     (TTT_FRESH_HOUSE, "house", "github",
                                      "after 1. Xa1, the Arbiter's move for @tannergolden")):
            st = TTT.state(d)
            alt = E.alt("tictactoe", d)
            with self.subTest(board=name(d), opens=opens):
                self.assertEqual((st["opens"], st["to_move"]), (opens, turn))
                self.assertIn("@tannergolden plays X and GitHub O", alt)
                self.assertIn(said, alt)
                self.assertIn(f"turn as {'X' if turn == 'house' else 'O'}", alt)
        self.assertIn("x is gone", " ".join(TTT.check({**TTT_GITHUB, "x": "house"})))
        self.assertIn("opens None is the side the Arbiter opened for",
                      " ".join(TTT.check({k: v for k, v in TTT_GITHUB.items() if k != "opens"})))
        self.assertIn("opens 'white' is the side", " ".join(TTT.check({**TTT_GITHUB, "opens": "white"})))
        # the opener's mark leads: O may have one more than X only in a game opened for GitHub
        self.assertIn("O moved first, the Arbiter having opened for github, so O has as many marks as X or one more",
                      " ".join(TTT.check({**TTT_GITHUB, "opens": "github"})))
        self.assertIn("X moved first, the Arbiter having opened for house",
                      " ".join(TTT.check({**TTT_HOUSE, "opens": "house"})))

    def test_x_is_drawn_light_and_o_dark_whoever_plays_them(self):
        # A game's colours never change, only who plays which side: every X the sheet draws (on the board, in the
        # medallions and in the trays) is in the light material and every O in the dark, opened either way round.
        def drawn(d: dict, tone: str) -> list[tuple[str, str]]:
            seen = []

            def recording(original):
                def pen_mark(self, cv, mark, material, *a, **k):
                    seen.append((mark, material))
                    return original(self, cv, mark, material, *a, **k)
                return pen_mark
            with mock.patch.object(TTT.Standard, "pen_mark", recording(TTT.Standard.pen_mark)), \
                    mock.patch.object(TTT.Print, "pen_mark", recording(TTT.Print.pen_mark)):
                for variant in ("still", "narrow-still"):
                    E.draw("tictactoe", d, tone, "day", variant)
            return seen

        for tone in (STANDARD, "blackprint"):
            for d in (TTT_GITHUB, TTT_HOUSE, TTT_FRESH, TTT_FRESH_HOUSE, TTT_WON, TTT_DRAWN):
                marks = drawn(d, tone)
                with self.subTest(board=name(d), opens=d["opens"], tone=tone):
                    self.assertEqual({mark for mark, _ in marks}, {"X", "O"}, "both sides' medallions at least")
                    self.assertEqual(sorted(set(marks)), [("O", "dark"), ("X", "light")])
        # the matchup has the house as X on the left and GitHub as O, opened either way round
        for d in (TTT_GITHUB, TTT_HOUSE, TTT_FRESH, TTT_FRESH_HOUSE):
            for variant in ("still", "narrow-still"):
                runs = lettered(d, STANDARD, variant)
                with self.subTest(board=name(d), opens=d["opens"], variant=variant):
                    self.assertIn("X  ·  THE HOUSE", runs)
                    self.assertTrue([r for r in runs if r.startswith("O  ·  ") and "PLAYER" in r or
                                     r == "O  ·  EVERYONE ELSE"], "GitHub as O")
                    self.assertFalse([r for r in runs if r.startswith(("O  ·  THE HOUSE", "X  ·  EVERY"))])

    def test_each_side_has_five_marks_if_it_moved_first_and_four_if_not_and_the_rack_counts_them_down(self):
        st = TTT.state(TTT_GITHUB)
        self.assertEqual((st["to_move"], st["alert"], st["last"]["number"]), ("github", "", 3))
        self.assertEqual((st["each"], st["left"]), ({"house": 5, "github": 4}, {"house": 2, "github": 2}))
        st = TTT.state(TTT_FRESH)
        self.assertEqual((st["each"], st["left"]), ({"house": 4, "github": 5}, {"house": 4, "github": 4}))
        st = TTT.state(TTT_DRAWN)
        self.assertEqual(st["left"], {"house": 0, "github": 0}, "nine marks down, none left to either side")

    def test_what_the_board_is_drawn_from_is_checked(self):
        cases = {"board": ("XXX/.../...", "the sides take turns"),
                 "line": (["a1", "b1", "c2"], "three cells in a row"),
                 "last": ({**TTT_GITHUB["last"], "move": "Xc3"}, "not a mark the board has")}
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                self.assertIn(said, " ".join(TTT.check({**TTT_GITHUB, key: bad})))
        self.assertIn("not the mark of the side that moved last",
                      " ".join(TTT.check({**TTT_GITHUB, "last": {**TTT_GITHUB["last"], "move": "Oa1"}})))

    def test_nothing_that_would_help_a_player_choose_is_taken(self):
        # where a side could win next, what perfect play makes of the game, a call to block, and a move offered with
        # the mark that says it wins: each turned away, with a word on why
        for key, bad, said in (("threats", {"house": ["c2"], "github": []}, "threats is gone: the board never shows"),
                               ("outlook", "draw", "outlook is gone: the board never says what perfect play"),
                               ("alert", "must block", "alert is gone: this game's turn calls nothing out")):
            with self.subTest(key=key):
                self.assertIn(said, " ".join(TTT.check({**TTT_GITHUB, key: bad})))
        won = row("tictactoe", "📏", "Mark the Head of the Board!", "Xb3#", "X takes the head of the board", 10, 6)
        self.assertIn("'Xb3#' says what the move would do", " ".join(TTT.check({**TTT_HOUSE, "moves": [won]})))
        self.assertIn("+ is gone", " ".join(TTT.check({**TTT_GITHUB, "last": {**TTT_GITHUB["last"], "move": "Xa2+"}})))
        self.assertIn("+ is gone", " ".join(TTT.check({**TTT_GITHUB, "history": [[1, "Xb2", "Oa1", "@imvale"],
                                                                                  [2, "Xc1+", "Oa3", "@tokafor"],
                                                                                  [3, "Xa2", "", ""]]})))
        self.assertEqual(TTT.check(TTT_WON), [], "the score sheet still marks the move that won")

    def test_a_won_game_names_its_line_and_only_a_won_game_has_one(self):
        self.assertIn("a won game names its winning line", " ".join(TTT.check({**TTT_WON, "line": []})))
        self.assertIn("only a won game has one", " ".join(TTT.check({**TTT_GITHUB, "line": ["a3", "b2", "c1"]})))
        self.assertIn("the winner's three marks", " ".join(TTT.check({**TTT_WON, "line": ["a1", "a2", "a3"]})))
        self.assertEqual(TTT.check({**TTT_WON, "line": ["c1", "b2", "a3"]}), [], "a line either way along")
        won = TTT.state(TTT_WON)
        self.assertEqual((won["result"]["winner"], won["line"], won["alert"]), ("house", ["a3", "b2", "c1"], ""))

    def test_a_drawn_game_is_drawn(self):
        self.assertEqual(TTT.check(TTT_DRAWN), [])
        self.assertIn("The game was drawn on a full board. Game 7 opens 14 Oct.", E.alt("tictactoe", TTT_DRAWN))
        self.assertIn("a game ended by a full board is drawn",
                      " ".join(TTT.check({**TTT_DRAWN, "result": {"winner": "github", "how": "a full board"}})))


class ConnectFour(unittest.TestCase):
    def test_the_house_drops_white_and_github_black_whichever_side_the_arbiter_opened_for(self):
        # a game opens with a White disc when it was opened for the house and a Black one when for GitHub
        self.assertEqual((C4.game.material_of("house"), C4.game.material_of("github")), ("light", "dark"))
        for d, opens, turn, said in ((C4_GITHUB, "github", "github", "after 8... 5"),
                                     (C4_HOUSE, "house", "house", "after 6... 7"),
                                     (C4_FRESH, "github", "house",
                                      "after 1. 4, the Arbiter's move for GitHub: a Black"),
                                     (C4_FRESH_HOUSE, "house", "github",
                                      "after 1. 3, the Arbiter's move for @tannergolden: a White")):
            st = C4.state(d)
            alt = E.alt("connectfour", d)
            with self.subTest(board=name(d), opens=opens):
                self.assertEqual((st["opens"], st["to_move"]), (opens, turn))
                self.assertIn("@tannergolden drops the White discs and GitHub the Black", alt)
                self.assertIn(said, alt)
                self.assertIn(f"turn as {'White' if turn == 'house' else 'Black'}", alt)
                self.assertEqual(st["left"]["house"] + st["left"]["github"], 42 - len(st["board"]))
        self.assertIn("light is gone", " ".join(C4.check({**C4_GITHUB, "light": "house"})))
        unopened = {k: v for k, v in C4_FRESH.items() if k != "opens"}
        self.assertIn("opens None is the side the Arbiter opened for", " ".join(C4.check(unopened)))
        # the opener's colour leads: Black may have one more only in a game opened for GitHub
        self.assertIn("White dropped first, the Arbiter having opened for house",
                      " ".join(C4.check({**C4_FRESH, "opens": "house"})))
        self.assertIn("Black dropped first, the Arbiter having opened for github",
                      " ".join(C4.check({**C4_FRESH_HOUSE, "opens": "github"})))

    def test_every_word_says_white_and_black_the_houses_white_first(self):
        for d in (C4_GITHUB, C4_HOUSE, C4_FRESH, C4_FRESH_HOUSE, C4_WON):
            for variant in ("still", "narrow-still"):
                runs = lettered(d, STANDARD, variant)
                racks = [r for r in runs if r.startswith(("WHITE ·", "BLACK ·"))]
                with self.subTest(board=name(d), opens=d["opens"], variant=variant):
                    self.assertEqual(racks, ["WHITE · HOUSE", "BLACK · GITHUB"], "the house's White on top")
                    self.assertIn("WHITE  ·  THE HOUSE", runs)
                    self.assertTrue([r for r in runs if r.startswith("BLACK  ·  ")], "GitHub as Black")
                    self.assertFalse([r for r in runs if re.search(r"\b(LIGHT|DARK)\b", r)])
            with self.subTest(board=name(d)):
                self.assertNotRegex(E.alt("connectfour", d), r"\b([Ll]ight|[Dd]ark)\b")
                self.assertNotRegex(said(ED.block("connectfour", d, "assets/elements")), r"\b([Ll]ight|[Dd]ark)\b")

    def test_discs_fall_and_take_turns(self):
        empty = "......./" * 5
        self.assertIn("discs fall", " ".join(C4.check({**C4_FRESH, "board": "...L.../" + empty[8:] + "......."})))
        self.assertIn("so it has as many as White or one more",
                      " ".join(C4.check({**C4_FRESH, "board": empty + "DD....."})))

    def test_the_last_disc_lands_where_gravity_puts_it_and_a_win_joins_four(self):
        st = C4.state(C4_GITHUB)
        self.assertEqual((st["last"]["column"], st["last"]["row"], st["alert"]), (5, 2, ""))
        self.assertEqual(st["left"], {"house": 13, "github": 13})
        self.assertIn("not topped by a disc of the side that moved last",
                      " ".join(C4.check({**C4_GITHUB, "last": {**C4_GITHUB["last"], "move": "3"}})))
        won = C4.state(C4_WON)
        self.assertEqual((won["result"]["winner"], len(won["line"])), ("github", 4))
        for line, said in (([[2, 4], [3, 3], [4, 2], [6, 1]], "one after another"),
                           ([[1, 1], [2, 1], [3, 1], [4, 1]], "the winner's four discs"),
                           ([[2, 4], [3, 3], [4, 2]], "one after another")):
            with self.subTest(line=line):
                self.assertIn(said, " ".join(C4.check({**C4_WON, "line": line})))
        self.assertEqual(C4.check({**C4_WON, "line": [[5, 1], [4, 2], [3, 3], [2, 4]]}), [])

    def test_nothing_that_would_help_a_player_choose_is_taken(self):
        # the columns a side could connect four down next, a call to block, and a move offered with the mark that
        # says it wins: each turned away, with a word on why
        self.assertIn("threats is gone: the frame never shows a column",
                      " ".join(C4.check({**C4_GITHUB, "threats": {"house": [7], "github": []}})))
        self.assertIn("alert is gone", " ".join(C4.check({**C4_GITHUB, "alert": "must block"})))
        won = row("connectfour", "⬇️", "Drop Down Column 5!", "5#", "A White disc down column 5, to row 2", 5, 13)
        self.assertIn("'5#' says what the move would do", " ".join(C4.check({**C4_HOUSE, "moves": [won]})))
        self.assertIn("+ is gone", " ".join(C4.check({**C4_GITHUB, "last": {**C4_GITHUB["last"], "move": "5+"}})))
        self.assertEqual(C4.check(C4_WON), [], "the score sheet still marks the drop that won")


class Checkers(unittest.TestCase):
    def test_the_board_is_drawn_from_the_houses_side_as_american_checkers_prints_it(self):
        # White, the house's, at the foot as chess draws White: Black's squares 1 to 4 at the head, square 1 second
        # along, and White's 29 to 32 along the foot, square 32 seventh along
        self.assertEqual([CK.game.rc(n) for n in (1, 4, 5, 29, 32)], [(0, 1), (0, 7), (1, 0), (7, 0), (7, 6)])
        st = CK.state(CK_OPENING)
        x0, y0, s = 38, 62, 46
        corners = {n: CK.layout.xy(st, n, x0, y0, s) for n in (1, 4, 29, 32)}
        self.assertEqual(corners, {1: (x0 + s, y0), 4: (x0 + 7 * s, y0), 29: (x0, y0 + 7 * s),
                                   32: (x0 + 6 * s, y0 + 7 * s)})
        rows = {side: {CK.layout.xy(st, n, x0, y0, s)[1] for n, p in st["pieces"].items() if p == letter}
                for side, letter in (("house", "l"), ("github", "d"))}
        self.assertEqual(rows["house"], {y0 + 5 * s, y0 + 6 * s, y0 + 7 * s}, "the house's White men at the foot")
        self.assertEqual(rows["github"], {y0, y0 + s, y0 + 2 * s}, "GitHub's Black men at the head")
        # the numbers read as the diagram prints them: 1 at the head, 32 at the foot
        sheet = E.draw("checkers", CK_OPENING, STANDARD, "day", "still")
        self.assertEqual(sheet, E.draw("checkers", CK_OPENING, STANDARD, "day", "still"))

    def test_github_plays_black_and_opens_on_a_clock_and_the_house_plays_white(self):
        st = CK.state(CK_OPENING)
        self.assertEqual((st["to_move"], st["opens"], st["due"]), ("github", "github", "21 Oct"),
                         "Black moves first, as American checkers has it, and its first move is due")
        for variant in ("still", "narrow-still"):
            runs = lettered(CK_OPENING, STANDARD, variant)
            with self.subTest(variant=variant):
                self.assertIn("GITHUB'S TURN", runs)
                self.assertTrue({"DUE BY 21 OCT", "BY 21 OCT"} & set(runs), "a clock from the first move")
                self.assertFalse([r for r in runs if "NO CLOCK" in r])
                self.assertIn("WHITE  ·  THE HOUSE", runs)
                self.assertIn("BLACK  ·  EVERYONE ELSE", runs)
                self.assertIn("BLACK MOVES FIRST", runs)
                self.assertEqual([r for r in runs if r.endswith(" TOOK")], ["WHITE TOOK", "BLACK TOOK"])
        for d in (CK_OPENING, CK_GITHUB, CK_CROWNED, CK_WON, CK_DRAWN):
            runs = lettered(d, STANDARD)
            with self.subTest(board=name(d)):
                self.assertFalse([r for r in runs if re.search(r"\b(LIGHT|DARK)\b", r)])
                self.assertNotRegex(E.alt("checkers", d), r"\b([Ll]ight|[Dd]ark)\b")
                self.assertNotRegex(said(ED.block("checkers", d, "assets/elements")), r"\b([Ll]ight|[Dd]ark)\b")
        self.assertIn("It is GitHub's turn as Black, due by 21 Oct. @tannergolden, White: men on 21, 22",
                      E.alt("checkers", CK_OPENING))
        self.assertIn("due: a game under way says the day its move is due by",
                      " ".join(CK.check({k: v for k, v in CK_OPENING.items() if k != "due"})))

    def test_a_jump_names_the_men_it_takes_and_a_crowned_man_is_a_king(self):
        st = CK.state(CK_CROWNED)
        self.assertEqual((st["last"]["path"], st["last"]["jumped"], st["last"]["crowned"]),
                         ([19, 10, 1], [15, 6], True))
        self.assertEqual(st["pieces"][1], "L")
        st = CK.state(CK_GITHUB)
        self.assertEqual((st["alert"], st["jumpers"], st["to_move"]), ("must jump", [8], "github"))
        self.assertEqual(st["last"]["number"], 10, "White's reply in the tenth move, Black having opened it")

    def test_what_the_board_is_drawn_from_is_checked(self):
        cases = {"fen": ("B:W1:B5", "a man on its far row"), "dark": ("house", "dark is gone"),
                 "last": ({**CK_CROWNED["last"], "move": "19x10x2"}, "does not end on a piece"),
                 "kings": ({"house": -1}, "kings gives")}
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                self.assertIn(said, " ".join(CK.check({**CK_CROWNED, key: bad})))
        self.assertIn("names a square twice", " ".join(CK.check({**CK_OPENING, "fen": "B:W21,21:B1"})))
        self.assertIn("more than 12 Black pieces", " ".join(CK.check({**CK_OPENING, "fen": "B:W21:B" + ",".join(
            map(str, range(1, 14)))})))
        self.assertIn("ends on a piece of the side to move",
                      " ".join(CK.check({**CK_GITHUB, "last": {**CK_GITHUB["last"], "move": "14-18"}})))
        self.assertIn("crowned its man, which stands as a king",
                      " ".join(CK.check({**CK_GITHUB, "last": {**CK_GITHUB["last"], "crowned": True}})))
        self.assertIn("crowned is true or false",
                      " ".join(CK.check({**CK_CROWNED, "last": {**CK_CROWNED["last"], "crowned": "yes"}})))
        self.assertIn("alert 'must block' is not what this game's turn can say",
                      " ".join(CK.check({**CK_GITHUB, "alert": "must block"})))
        long_jump = "1x10x19x28x19x10x1x10x19x28x19x10x1"
        self.assertTrue(CK.game.MOVE.fullmatch(long_jump), "twelve jumps, as many as a side has men to take")
        self.assertFalse(CK.game.MOVE.fullmatch(long_jump + "x10"))


class Finished(unittest.TestCase):
    """A finished game keeps its final board up for two days: the result on the turn's plate, the winning line
    where the game has one, the day the fresh board comes, and nothing left to play."""

    BOARDS = (TTT_WON, TTT_DRAWN, C4_WON, CK_WON, CK_DRAWN)

    def test_a_finished_board_offers_no_move_and_only_it_has_a_next_day(self):
        moves = {"tictactoe": TTT_GITHUB, "connectfour": C4_GITHUB, "checkers": CK_GITHUB}
        for d in self.BOARDS:
            pkg = GAMES[d["kind"]][0]
            with self.subTest(board=name(d)):
                self.assertIn("a finished board offers no move", " ".join(pkg.check({**d, "moves":
                                                                                    moves[d["kind"]]["moves"]})))
                self.assertIn("next '32 Oct' is not a day", " ".join(pkg.check({**d, "next": "32 Oct"})))
        for d in (TTT_GITHUB, C4_GITHUB, CK_GITHUB):
            with self.subTest(board=name(d)):
                self.assertIn("a game under way has none", " ".join(GAMES[d["kind"]][0].check({**d, "next": "14 Oct"})))

    def test_only_the_side_that_moved_last_can_have_won_and_each_end_is_won_or_drawn(self):
        self.assertIn("the winner is the side that made the last move, house",
                      " ".join(TTT.check({**TTT_WON, "result": {"winner": "github", "how": "three in a row"}})))
        self.assertIn("a game ended by four in a row has a winner",
                      " ".join(C4.check({**C4_WON, "result": {"winner": None, "how": "four in a row"}})))
        self.assertIn("result is how the game ended", " ".join(CK.check({**CK_WON, "result": {"winner": "house"}})))
        self.assertIn("no move left, repetition, forty moves",
                      " ".join(CK.check({**CK_WON, "result": {"winner": "house", "how": "checkmate"}})))
        self.assertIn("a finished board has nothing left to block", " ".join(CK.check({**CK_WON,
                                                                                        "alert": "must jump"})))

    def test_its_plate_says_who_won_and_how_and_when_the_fresh_board_comes(self):
        for d, label in ((TTT_WON, "@tannergolden wins"), (TTT_DRAWN, "drawn"), (C4_WON, "GitHub wins"),
                         (CK_WON, "@tannergolden wins"), (CK_DRAWN, "drawn")):
            st = GAMES[d["kind"]][0].state(d)
            self.assertEqual((st["result"]["how"], st["next"], st["alert"]), (d["result"]["how"], "14 Oct", ""))
            for tone in (STANDARD, "blackprint"):
                for variant in ("still", "narrow-still"):
                    runs = lettered(d, tone, variant)
                    with self.subTest(board=name(d), tone=tone, variant=variant):
                        self.assertIn(label.upper(), runs, "the plate's label")
                        self.assertIn(d["result"]["how"].upper(), runs, "and how, in its second panel")
                        self.assertIn("NEXT GAME 14 OCT", runs, "the day the fresh board comes, said in full")
                        self.assertFalse([r for r in runs if r.endswith("'S TURN")], "nobody's turn")
        self.assertIn("@tannergolden won with three in a row, from a3 to c1. Game 9 opens 14 Oct.",
                      E.alt("tictactoe", TTT_WON))
        self.assertIn("GitHub won with four in a row. Game 4 opens 14 Oct.", E.alt("connectfour", C4_WON))
        self.assertIn("@tannergolden won: GitHub had no move left. Game 5 opens 14 Oct.", E.alt("checkers", CK_WON))
        self.assertIn("The game was drawn by the forty-move rule.", E.alt("checkers", CK_DRAWN))


class Readme(unittest.TestCase):
    def test_each_board_has_its_turns_banner_above_its_fold_and_every_move_folded_under(self):
        text = ED.block("tictactoe", TTT_GITHUB, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:tictactoe:start -->\n> [!TIP]\n> 🟢 **GitHub's turn!**"
                                        " @tannergolden played 3. Xa2."))
        self.assertIn("\n\n<details>\n<summary><b>❌ Tic-Tac-Toe</b></summary>\n\n<picture>", text)
        self.assertIn("</picture>\n\n<details>\n<summary>⭕ <b>GitHub's Turn</b> · 2 open cells · open to choose one"
                      "</summary>\n\n|  | Move | In words | Play |\n| :-: | :--- | :--- | :-: |\n", text)
        self.assertIn("| 📏 | **Mark the Head of the Board!** `Ob3` | O takes the head of the board |", text)
        self.assertTrue(text.endswith(f"</details>\n\n{NOTE}\n\n</details>\n<!-- markdown:element:tictactoe:end -->"))
        text = ED.block("checkers", CK_OPENING, "assets/elements")
        self.assertIn("> [!TIP]\n> 🟢 **GitHub's turn as Black!**", text)
        self.assertIn("<summary>⛂ <b>GitHub's Turn</b> · 2 legal moves · open to choose one</summary>", text)

    def test_the_side_to_move_is_signed_with_what_it_plays_both_ways_round(self):
        # the house's sign is ❌, ⚪ or ⛀ and GitHub's ⭕, ⚫ or ⛂, whichever side opened
        for d, said in ((TTT_GITHUB, "⭕ <b>GitHub's Turn</b> · 2 open cells"),
                        (TTT_HOUSE, "❌ <b>@tannergolden's Turn</b> · 2 open cells"),
                        (TTT_FRESH, "❌ <b>@tannergolden's Turn</b> · 2 open cells"),
                        (TTT_FRESH_HOUSE, "⭕ <b>GitHub's Turn</b> · 1 open cell ·"),
                        (C4_GITHUB, "⚫ <b>GitHub's Turn</b> · 2 open columns"),
                        (C4_HOUSE, "⚪ <b>@tannergolden's Turn</b> · 1 open column ·"),
                        (C4_FRESH, "⚪ <b>@tannergolden's Turn</b> · 2 open columns"),
                        (C4_FRESH_HOUSE, "⚫ <b>GitHub's Turn</b> · 2 open columns"),
                        (CK_GITHUB, "⛂ <b>GitHub's Turn</b> · 1 legal move ·"),
                        (CK_OPENING, "⛂ <b>GitHub's Turn</b> · 2 legal moves ·")):
            with self.subTest(board=name(d)):
                self.assertIn(f"<summary>{said}", ED.block(d["kind"], d, "assets/elements"))
        white_turn = dict(CK_CROWNED, fen="W:WK1,20,21,24,28,30:B5,9,12,17,18", move=19, history=[
            [18, "10x17", "19x10x1", "@tokafor"], [19, "5-9", "", "@imvale"]],
            last={"move": "5-9", "words": "Man from 5 to 9", "by": "@imvale", "when": "10 Oct"},
            moves=[row("checkers", "⚔️", "Jump the Man on 17!", "21x14", "Man from 21 jumps 17, landing on 14", 5, 38)],
            alert="must jump", prompt="🛑 **@tannergolden's turn!** GitHub played 19. 5-9. Must jump! Reply due by"
                                      " 17 Oct.")
        self.assertEqual(CK.check(white_turn), [])
        self.assertIn("<summary>⛀ <b>@tannergolden's Turn</b> · 1 legal move · only @tannergolden can play these"
                      "</summary>", ED.block("checkers", white_turn, "assets/elements"))

    def test_a_fresh_board_names_the_arbiters_opening_move_and_who_it_opened_for(self):
        for d in (TTT_FRESH, C4_FRESH):
            alt = E.alt(d["kind"], d)
            with self.subTest(kind=d["kind"]):
                self.assertIn("the Arbiter's move for GitHub", alt)
                self.assertIn("It is @tannergolden's turn", alt)
                self.assertIn("The Arbiter opens every game for a side drawn at random",
                              ED.block(d["kind"], d, "assets/elements"))
        self.assertIn("@tannergolden plays X and GitHub O, after 1. Ob2, the Arbiter's move for GitHub: O takes the"
                      " centre. It is @tannergolden's turn as X, due by 21 Oct.", E.alt("tictactoe", TTT_FRESH))
        self.assertIn("@tannergolden drops the White discs and GitHub the Black, after 1. 3, the Arbiter's move for"
                      " @tannergolden: a White disc down column 3, to row 1. It is GitHub's turn as Black",
                      E.alt("connectfour", C4_FRESH_HOUSE))

    def test_the_sides_are_named_the_houses_first_both_ways_round(self):
        # X, White and White first, whichever side the Arbiter opened for: the house's colour never changes
        for d, said in ((TTT_FRESH, "@tannergolden plays X and GitHub O"),
                        (TTT_FRESH_HOUSE, "@tannergolden plays X and GitHub O"),
                        (C4_FRESH, "@tannergolden drops the White discs and GitHub the Black"),
                        (C4_FRESH_HOUSE, "@tannergolden drops the White discs and GitHub the Black"),
                        (CK_OPENING, "@tannergolden, White: men on 21"),
                        (CK_GITHUB, "@tannergolden, White: men on 11")):
            with self.subTest(board=name(d)):
                self.assertIn(said, E.alt(d["kind"], d))

    def test_a_finished_game_is_its_banner_its_board_and_its_note_with_nothing_to_play(self):
        # what the picture cannot say, as the engine writes it on a finished board: a link in it is a link
        over = ("Game 1 is over, and its final board stays up for two days: game 2 opens 15 Oct, 16:00 EST, and "
                "nothing can be played until then. Every finished game is kept as a "
                "[PDN](https://github.com/tannergolden/tannergolden/tree/HEAD/.github/checkers/games).")
        for d in (*Finished.BOARDS, *(dict(b, note=over) for b in Finished.BOARDS)):
            text = ED.block(d["kind"], d, "assets/elements")
            with self.subTest(board=name(d), note=d["note"][:20]):
                self.assertEqual(E.game_of(d["kind"]).check(d), [])
                self.assertIn(f"> [!IMPORTANT]\n> {d['prompt']}\n\n<details>\n<summary><b>"
                              f"{ED.FOLDS[d['kind']][0]}</b></summary>\n\n<picture>", text)
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
        self.assertIn("<details open>\n<summary>⛂ Men · 11 moves</summary>", text)
        self.assertIn("<details open>\n<summary>⛂ King · 1 move</summary>", text)


if __name__ == "__main__":
    unittest.main()
