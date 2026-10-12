# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games beside chess on @tannergolden's profile: Tic-Tac-Toe, Connect Four and Checkers, drawn as chess is, in
the standard theme and every print, and nowhere but that profile.

The Arbiter opens Tic-Tac-Toe and Connect Four for a side drawn at random, so each is held to its boards both ways
round: the house opened for, playing X or the dark discs, and GitHub opened for. Each game has a board under way, the
fresh board whose only move is the Arbiter's opening move (or, in Checkers, which the house opens, the board before
any move), and a finished board, kept up for two days with the result on its plate and nothing left to play. The
samples are legal games: Tic-Tac-Toe's GitHub's turn faces a threat on c2, and its finished board is the house's
three in a row on the diagonal; Connect Four's GitHub's turn faces the house's threat down column 7, and GitHub won
game 3 on the diagonal; Checkers' GitHub's turn must jump after the house's capture, and its crowned board is
GitHub's double jump that crowns a king on the house's back row."""
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
TTT_GITHUB = {
    "kind": "tictactoe", "board": "O../XX./O.X", "x": "house", "game": 9, "move": 3, "players": 4, "due": "18 Oct",
    "history": [[1, "Xb2", "Oa1", "@imvale"], [2, "Xc1+", "Oa3+", "@tokafor"], [3, "Xa2+", "", ""]],
    "last": {"move": "Xa2+", "words": "X blocks on a2, threatening c2", "by": "@tannergolden", "when": "11 Oct"},
    "threats": {"house": ["c2"], "github": []}, "outlook": "draw",
    "moves": [row("tictactoe", "⚠️", "Drop Your Guard!", "Ob3+", "O takes the head of the board, threatening c3", 9, 6),
              row("tictactoe", "🛡️", "Parry the Thrust!", "Oc2", "O blocks on c2", 9, 6)],
    "prompt": "🟢 **GitHub's turn as O!** X threatens c2: block it, by 18 Oct.", "note": NOTE}
# GitHub opened for, so GitHub plays X and the house O: the house to move, with a win of its own on b3.
TTT_HOUSE = {
    "kind": "tictactoe", "board": "O.O/.X./X.X", "x": "github", "game": 10, "move": 3, "players": 3, "due": "19 Oct",
    "history": [[1, "Xb2", "Oa3", "the Arbiter"], [2, "Xa1+", "Oc3+", "@tokafor"], [3, "Xc1+", "", "@wrencastellan"]],
    "last": {"move": "Xc1+", "words": "X takes the lower right corner, threatening b1", "by": "@wrencastellan",
             "when": "12 Oct"},
    "threats": {"github": ["b1"], "house": ["b3"]}, "outlook": "house",
    "moves": [row("tictactoe", "🏆", "Strike the Final Blow!", "Ob3#", "O takes b3, three in a row from a3 to c3", 10,
                  6),
              row("tictactoe", "🛡️", "Turn Their Point Aside!", "Ob1+", "O blocks on b1, threatening b3", 10, 6)],
    "prompt": "🛑 **@tannergolden's turn as O!** GitHub played 3. Xc1+.", "note": NOTE}
# A fresh board: the Arbiter opened game 11 for GitHub with the centre, and it is the house's turn as O.
TTT_FRESH = {
    "kind": "tictactoe", "board": ".../.X./...", "x": "github", "game": 11, "move": 1, "players": 0, "due": "21 Oct",
    "history": [[1, "Xb2", "", "the Arbiter"]],
    "last": {"move": "Xb2", "words": "X takes the centre", "by": "the Arbiter", "when": "14 Oct"},
    "threats": {"github": [], "house": []}, "outlook": "draw",
    "moves": [row("tictactoe", "🗡️", "Hold the Corner!", "Oa3", "O takes the upper left corner", 11, 2),
              row("tictactoe", "🪶", "Probe the Line!", "Ob3", "O takes the head of the board", 11, 2)],
    "prompt": "🛑 **@tannergolden's turn as O!** The Arbiter opened game 11 for GitHub with 1. Xb2.",
    "note": "The Arbiter opens every game for a side drawn at random: X wins far more often when anyone slips."}
# The same fresh board the other way round: opened for the house, which plays X, and GitHub to reply as O.
TTT_FRESH_HOUSE = dict(TTT_FRESH, board=".../.../X..", x="house",
                       last={"move": "Xa1", "words": "X takes the lower left corner", "by": "the Arbiter",
                             "when": "14 Oct"}, history=[[1, "Xa1", "", ""]],
                       moves=[row("tictactoe", "🎯", "Strike the Heart!", "Ob2", "O takes the centre", 11, 2)],
                       prompt="🟢 **GitHub's turn as O!** The Arbiter opened game 11 for @tannergolden with 1. Xa1.")
TTT_WON = {
    "kind": "tictactoe", "board": "X.O/OX./XOX", "x": "house", "game": 8, "move": 4, "players": 6,
    "history": [[2, "Xa1+", "Oc3", "@tokafor"], [3, "Xc1+", "Ob1", "@jhalloran"], [4, "Xa3#", "", ""]],
    "last": {"move": "Xa3#", "words": "X takes a3, three in a row from a3 to c1", "by": "@tannergolden",
             "when": "10 Oct"},
    "result": {"winner": "house", "how": "three in a row"}, "line": ["a3", "b2", "c1"], "next": "14 Oct",
    "prompt": "🏆 **@tannergolden wins game 8!** X took a3, b2 and c1. Game 9 opens 14 Oct.", "note": NOTE}
TTT_DRAWN = {
    "kind": "tictactoe", "board": "XOX/XOO/OXX", "x": "github", "game": 6, "move": 5, "players": 7,
    "history": [[3, "Xc3", "Oc2", "@imvale"], [4, "Xb1", "Oa1", "@tokafor"], [5, "Xa2", "", "@jhalloran"]],
    "last": {"move": "Xa2", "words": "X takes the left edge", "by": "@jhalloran", "when": "5 Oct"},
    "result": {"winner": None, "how": "a full board"}, "next": "14 Oct",
    "prompt": "🤝 **Game 6 is drawn!** Nine marks and no line. Game 7 opens 14 Oct.", "note": NOTE}

# --------------------------------------------------------------------------- Connect Four
# GitHub opened for, so GitHub drops the dark discs: its turn, with the house threatening column 7.
C4_GITHUB = {
    "kind": "connectfour", "board": "......./..D..../..LD.../..DD.../D.DLLL./L.DLDLL", "opens": "github",
    "light": "house", "game": 4, "move": 9, "players": 7, "due": "18 Oct",
    "history": [[7, "4", "6", "@devonaraki"], [8, "4", "5+", "@hollyfenwick"], [9, "", "", ""]],
    "last": {"move": "5+", "words": "A light disc down column 5, to row 2, threatening column 7",
             "by": "@tannergolden", "when": "12 Oct"},
    "threats": {"house": [7], "github": []},
    "moves": [row("connectfour", "🛡️", "Plug the Gap!", "7", "A dark disc down column 7 blocks on row 2", 4, 17),
              row("connectfour", "⚠️", "Look the Wrong Way!", "2", "A dark disc down column 2, to row 1", 4, 17)],
    "prompt": "🟢 **GitHub's turn as Dark!** The house threatens column 7: block it, by 18 Oct.", "note": NOTE}
# The house opened for, so the house drops the dark discs and GitHub the light: the house to move.
C4_HOUSE = {
    "kind": "connectfour", "board": "......./......./......./..LL.../.DDD.../LLDDLDL", "opens": "house",
    "light": "github", "game": 5, "move": 7, "players": 5, "due": "19 Oct",
    "history": [[5, "3", "3", "@imvale"], [6, "5+", "7", "@octocat"], [7, "", "", ""]],
    "last": {"move": "7", "words": "A light disc down column 7, to row 1", "by": "@octocat", "when": "10 Oct"},
    "threats": {"house": [1, 5], "github": []},
    "moves": [row("connectfour", "🏆", "Link Up, All Four!", "5#", "A dark disc down column 5 connects four across"
                  " row 2", 5, 13)],
    "prompt": "🛑 **@tannergolden's turn as Dark!** GitHub played 6... ⚪7.", "note": NOTE}
# A fresh board: the Arbiter opened game 6 for GitHub down the centre column, and it is the house's turn as Light.
C4_FRESH = {
    "kind": "connectfour", "board": "......./......./......./......./......./...D...", "opens": "github",
    "light": "house", "game": 6, "move": 1, "players": 0, "due": "21 Oct",
    "history": [[1, "4", "", "the Arbiter"]],
    "last": {"move": "4", "words": "A dark disc down column 4, to row 1", "by": "the Arbiter", "when": "14 Oct"},
    "threats": {"house": [], "github": []},
    "moves": [row("connectfour", "🪂", "Stack the Squad!", "4", "A light disc down column 4, to row 2", 6, 2),
              row("connectfour", "🏔️", "Drop on the Flank!", "1", "A light disc down column 1, to row 1", 6, 2)],
    "prompt": "🛑 **@tannergolden's turn as Light!** The Arbiter opened game 6 for GitHub with 1. ⚫4.",
    "note": "The Arbiter opens every game for a side drawn at random: whoever drops the first disc can force a win."}
C4_FRESH_HOUSE = dict(C4_FRESH, board="......./......./......./......./......./..D....", opens="house",
                      light="github", history=[[1, "3", "", ""]],
                      last={"move": "3", "words": "A dark disc down column 3, to row 1", "by": "the Arbiter",
                            "when": "14 Oct"},
                      prompt="🟢 **GitHub's turn as Light!** The Arbiter opened game 6 for @tannergolden with 1. ⚫3.")
C4_WON = {
    "kind": "connectfour", "board": "....D../....D../.D..L../.LDLD../.LDDDL./DLLLDL.", "opens": "github",
    "light": "house", "game": 3, "move": 10, "players": 9,
    "history": [[8, "3+", "6", "@tokafor"], [9, "3", "2+", "@wrencastellan"], [10, "2#", "", "@jhalloran"]],
    "last": {"move": "2#", "words": "A dark disc down column 2 connects four on the diagonal", "by": "@jhalloran",
             "when": "10 Oct"},
    "result": {"winner": "github", "how": "four in a row"}, "line": [[2, 4], [3, 3], [4, 2], [5, 1]],
    "next": "14 Oct", "prompt": "🏆 **GitHub wins game 3!** Four dark discs on the diagonal. Game 4 opens 14 Oct.",
    "note": NOTE}

# --------------------------------------------------------------------------- Checkers
CK_OPENING = {
    "kind": "checkers", "fen": "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12", "dark": "house",
    "game": 6, "move": 1, "players": 0, "history": [[1, "", "", ""]], "kings": {"house": 0, "github": 0},
    "moves": [row("checkers", "⚓", "Drop Anchor!", "9-13", "Man from 9 to 13", 6, 1),
              row("checkers", "⛵", "Into Open Water!", "9-14", "Man from 9 to 14", 6, 1)],
    "prompt": "🛑 **@tannergolden's turn as Dark!** Dark opens game 6.",
    "note": "A jump must be taken when there is one. " + NOTE}
CK_GITHUB = {
    "kind": "checkers", "fen": "W:W20,21,24,25,27,28,29,30,32:B2,4,5,6,8,9,14,16,18", "dark": "house", "game": 6,
    "move": 10, "players": 11, "due": "18 Oct",
    "history": [[8, "3-8", "26-22", "@hollyfenwick"], [9, "1-6", "22x15", "@sunnypatel"], [10, "11x18", "", ""]],
    "kings": {"house": 0, "github": 0},
    "last": {"move": "11x18", "words": "Man from 11 jumps 15, landing on 18", "by": "@tannergolden", "when": "11 Oct"},
    "alert": "must jump",
    "moves": [row("checkers", "⚔️", "Ram Them Amidships!", "20x11", "Man from 20 jumps 16, landing on 11", 6, 20)],
    "prompt": "🟢 **GitHub's turn as Light!** A jump is waiting, and it must be taken, by 18 Oct.",
    "note": "A jump must be taken when there is one."}
CK_CROWNED = {
    "kind": "checkers", "fen": "B:WK1,20,21,24,28,30:B5,8,12,17,18", "dark": "house", "game": 5, "move": 19,
    "players": 14, "due": "17 Oct",
    "history": [[17, "2-6", "17-14", "@imvale"], [18, "10x17", "19x10x1", "@tokafor"], [19, "", "", ""]],
    "kings": {"house": 0, "github": 1},
    "last": {"move": "19x10x1", "words": "Man from 19 jumps 15 and 6, landing on 1, crowned", "by": "@tokafor",
             "when": "9 Oct", "crowned": True},
    "moves": [row("checkers", "🎣", "Send In the Fire Ship!", "5-9", "Man from 5 to 9", 5, 37),
              row("checkers", "⛵", "Full Sail Ahead!", "8-11", "Man from 8 to 11", 5, 37)],
    "prompt": "🛑 **@tannergolden's turn as Dark!** GitHub played 18... 19x10x1 and crowned a king.",
    "note": "A jump must be taken when there is one."}
# The house's man took GitHub's last: GitHub has no move left, and the house wins.
CK_WON = {
    "kind": "checkers", "fen": "W:W:B5,9,23", "dark": "house", "game": 4, "move": 30, "players": 12,
    "history": [[29, "10-14", "22-18", "@imvale"], [30, "14x23", "", ""]], "kings": {"house": 1, "github": 2},
    "last": {"move": "14x23", "words": "Man from 14 jumps 18, landing on 23", "by": "@tannergolden", "when": "9 Oct"},
    "result": {"winner": "house", "how": "no move left"}, "next": "14 Oct",
    "prompt": "🏆 **@tannergolden wins game 4!** GitHub has no move left. Game 5 opens 14 Oct.", "note": NOTE}
CK_DRAWN = {
    "kind": "checkers", "fen": "B:WK30:BK3", "dark": "house", "game": 3, "move": 88, "players": 20,
    "history": [[87, "8-3", "26-30", "@octocat"], [88, "", "", ""]], "kings": {"house": 3, "github": 4},
    "last": {"move": "26-30", "words": "King from 26 to 30", "by": "@octocat", "when": "8 Oct"},
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
        for kind, needs in (("tictactoe", "board, x"), ("connectfour", "board, opens, light"), ("checkers", "fen")):
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

    def test_x_is_whichever_side_the_arbiter_opened_for(self):
        for d, x, turn, mark in ((TTT_GITHUB, "house", "github", "O"), (TTT_HOUSE, "github", "house", "O"),
                                 (TTT_FRESH, "github", "house", "O"), (TTT_FRESH_HOUSE, "house", "github", "O")):
            st = TTT.state(d)
            with self.subTest(board=name(d), x=x):
                self.assertEqual((st["x"], st["to_move"], TTT.game.mark_of(st, turn)), (x, turn, mark))
        self.assertIn("x 'white' is the side that plays X", " ".join(TTT.check({**TTT_GITHUB, "x": "white"})))
        self.assertIn("x None is the side that plays X", " ".join(TTT.check({k: v for k, v in TTT_GITHUB.items()
                                                                              if k != "x"})))

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
                with self.subTest(board=name(d), x=d["x"], tone=tone):
                    self.assertEqual({mark for mark, _ in marks}, {"X", "O"}, "both sides' medallions at least")
                    self.assertEqual(sorted(set(marks)), [("O", "dark"), ("X", "light")])
            house, github = drawn(TTT_GITHUB, tone), drawn(TTT_HOUSE, tone)     # x: house, then x: github
            with self.subTest(tone=tone):
                self.assertEqual({m for mk, m in house if mk == "X"}, {m for mk, m in github if mk == "X"})
        # the same marks on the same cells draw the same board, whichever side plays them
        flipped = dict(TTT_HOUSE, x="house", threats={"house": ["b1"], "github": ["b3"]}, outlook="github",
                       last=dict(TTT_HOUSE["last"], by="@tannergolden"),
                       history=[[1, "Xb2", "Oa3", ""], [2, "Xa1+", "Oc3+", "@tokafor"], [3, "Xc1+", "", ""]],
                       prompt="🟢 **GitHub's turn as O!** @tannergolden played 3. Xc1+.")
        self.assertEqual(TTT.check(flipped), [])
        for skin in (lambda: TTT.Standard("day"), lambda: TTT.Standard("dark"), lambda: TTT.Print("day", "blackprint"),
                     lambda: TTT.Print("dark", "yellowprint")):
            boards = []
            for d in (TTT_HOUSE, flipped):
                sk = skin()
                cv = sk.new(420, 420, "Tic-Tac-Toe", "The board alone", "elements tictactoe wide")
                TTT.layout.board(cv, sk, TTT.state(d), 38, 62, 368)
                boards.append(cv.svg())
            with self.subTest(skin=type(sk).__name__, dark=sk.dark):
                self.assertEqual(boards[0], boards[1])

    def test_what_is_set_on_a_tray_reads_by_night(self):
        # a tray is the board's light square: by night its letters are dark, as the square's own would be, where the
        # card's light letters would vanish into it
        P.PAIRS.clear()
        for d in (TTT_HOUSE, TTT_DRAWN):
            E.draw("tictactoe", d, STANDARD, "dark", "still")
        on_tray = {(fill, ground) for fill, ground, what in P.PAIRS if what == "on a tray"}
        self.assertEqual(on_tray, {("charcoal", "ash")})
        self.assertGreaterEqual(P.contrast("charcoal", "ash"), 4.5)
        P.PAIRS.clear()
        E.draw("tictactoe", TTT_HOUSE, STANDARD, "day", "still")
        self.assertFalse([p for p in P.PAIRS if p[2] == "on a tray"], "by day a tray's letters are the card's")

    def test_a_threat_asks_the_side_to_move_to_block_unless_it_can_win_first(self):
        st = TTT.state(TTT_GITHUB)
        self.assertEqual((st["to_move"], st["alert"], st["last"]["number"]), ("github", "must block", 3))
        self.assertIn('stroke-dasharray="', TTT.draw("tictactoe", TTT_GITHUB, "blackprint", "day", "still"),
                      "the threatening mark in phantom lines")
        st = TTT.state(TTT_HOUSE)
        self.assertEqual((st["to_move"], st["alert"]), ("house", ""), "the house can win on b3 before it blocks b1")

    def test_what_the_board_is_drawn_from_is_checked(self):
        cases = {"board": ("XXX/.../...", "X moves first"), "outlook": ("win", "outlook"),
                 "threats": ({"house": ["d4"]}, "threats gives"),
                 "line": (["a1", "b1", "c2"], "three cells in a row"),
                 "last": ({**TTT_GITHUB["last"], "move": "Xc3"}, "not a mark the board has")}
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                self.assertIn(said, " ".join(TTT.check({**TTT_GITHUB, key: bad})))
        self.assertIn("each once", " ".join(TTT.check({**TTT_GITHUB, "threats": {"house": ["c2", "c2"]}})))
        self.assertIn("threats gives", " ".join(TTT.check({**TTT_GITHUB, "threats": {"house": ["a1"]}})),
                      "a threat is an open cell")
        self.assertIn("not the mark of the side that moved last",
                      " ".join(TTT.check({**TTT_GITHUB, "last": {**TTT_GITHUB["last"], "move": "Oa1"}})))
        self.assertIn("alert 'must jump' is not what this game's turn can say",
                      " ".join(TTT.check({**TTT_GITHUB, "alert": "must jump"})))

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
    def test_the_opener_drops_the_dark_discs_whichever_side_the_arbiter_opened_for(self):
        for d, opens, turn in ((C4_GITHUB, "github", "github"), (C4_HOUSE, "house", "house"),
                               (C4_FRESH, "github", "house"), (C4_FRESH_HOUSE, "house", "github")):
            st = C4.state(d)
            with self.subTest(board=name(d)):
                self.assertEqual((st["opens"], st["light"], st["to_move"]), (opens, "house" if opens == "github"
                                                                              else "github", turn))
                self.assertEqual(C4.game.material_of(st, opens), "dark")
        self.assertIn("light 'github' is the side that did not open, house",
                      " ".join(C4.check({**C4_GITHUB, "light": "github"})))
        unopened = {k: v for k, v in C4_FRESH.items() if k != "opens"}
        self.assertIn("opens None is the side the Arbiter opened for", " ".join(C4.check(unopened)))

    def test_discs_fall_and_take_turns(self):
        empty = "......./" * 5
        self.assertIn("discs fall", " ".join(C4.check({**C4_FRESH, "board": "...L.../" + empty[8:] + "......."})))
        self.assertIn("the sides take turns", " ".join(C4.check({**C4_FRESH, "board": empty + "DD....."})))

    def test_the_last_disc_lands_where_gravity_puts_it_and_a_win_joins_four(self):
        st = C4.state(C4_GITHUB)
        self.assertEqual((st["last"]["column"], st["last"]["row"], st["alert"]), (5, 2, "must block"))
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

    def test_a_threat_is_a_column_that_is_not_full(self):
        self.assertTrue(C4.check({**C4_GITHUB, "threats": {"house": [8]}}))
        self.assertTrue(C4.check({**C4_GITHUB, "threats": {"house": [True]}}))
        self.assertIn("each once", " ".join(C4.check({**C4_GITHUB, "threats": {"house": [7, 7]}})))


class Checkers(unittest.TestCase):
    def test_the_squares_are_checkers_own_and_the_house_is_on_the_near_side(self):
        self.assertEqual([CK.game.rc(n) for n in (1, 4, 5, 29, 32)], [(0, 1), (0, 7), (1, 0), (7, 0), (7, 6)])
        st = CK.state(CK_OPENING)
        self.assertTrue(st["flip"], "the house plays dark, so the board is turned to put its men nearest")
        self.assertEqual(st["to_move"], "house", "dark moves first, and the house opens")

    def test_a_jump_names_the_men_it_takes_and_a_crowned_man_is_a_king(self):
        st = CK.state(CK_CROWNED)
        self.assertEqual((st["last"]["path"], st["last"]["jumped"], st["last"]["crowned"]),
                         ([19, 10, 1], [15, 6], True))
        self.assertEqual(st["pieces"][1], "L")
        st = CK.state(CK_GITHUB)
        self.assertEqual((st["alert"], st["jumpers"]), ("must jump", [20]))

    def test_what_the_board_is_drawn_from_is_checked(self):
        cases = {"fen": ("B:W1:B5", "a man on its far row"), "dark": ("black", "the side that plays the dark men"),
                 "last": ({**CK_CROWNED["last"], "move": "19x10x2"}, "does not end on a piece"),
                 "kings": ({"house": -1}, "kings gives")}
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                self.assertIn(said, " ".join(CK.check({**CK_CROWNED, key: bad})))
        self.assertIn("the dark men and opens every game: the house", " ".join(CK.check({**CK_OPENING,
                                                                                          "dark": "github"})))
        self.assertEqual(CK.check({k: v for k, v in CK_OPENING.items() if k != "dark"}), [], "the house, unsaid")
        self.assertIn("names a square twice", " ".join(CK.check({**CK_OPENING, "fen": "B:W21,21:B1"})))
        self.assertIn("more than 12 dark pieces", " ".join(CK.check({**CK_OPENING, "fen": "B:W21:B" + ",".join(
            map(str, range(1, 14)))})))
        self.assertIn("ends on a piece of the side to move",
                      " ".join(CK.check({**CK_GITHUB, "last": {**CK_GITHUB["last"], "move": "24-20"}})))
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
        self.assertIn("a finished board has nothing left to block", " ".join(TTT.check({**TTT_WON,
                                                                                         "alert": "must block"})))

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
    def test_each_board_has_its_turns_banner_above_and_every_move_folded_under(self):
        text = ED.block("tictactoe", TTT_GITHUB, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:tictactoe:start -->\n> [!TIP]\n> 🟢 **GitHub's turn"
                                        " as O!**"))
        self.assertIn("</picture>\n\n<details>\n<summary>⭕ <b>GitHub's Turn</b> · 2 open cells · open to choose one"
                      "</summary>\n\n|  | Move | What it does | Play |\n| :-: | :--- | :--- | :-: |\n", text)
        self.assertIn("| ⚠️ | **Drop Your Guard!** `Ob3+` | O takes the head of the board, threatening c3 |", text)
        self.assertTrue(text.endswith(f"</details>\n\n{NOTE}\n<!-- markdown:element:tictactoe:end -->"))
        text = ED.block("checkers", CK_OPENING, "assets/elements")
        self.assertIn("> [!CAUTION]\n> 🛑 **@tannergolden's turn as Dark!**", text)
        self.assertIn("<summary>⛂ <b>@tannergolden's Turn</b> · 2 legal moves · only @tannergolden can play these"
                      "</summary>", text)

    def test_the_side_to_move_is_signed_with_what_it_plays_this_game_both_ways_round(self):
        for d, said in ((TTT_GITHUB, "⭕ <b>GitHub's Turn</b> · 2 open cells"),
                        (TTT_HOUSE, "⭕ <b>@tannergolden's Turn</b> · 2 open cells"),
                        (TTT_FRESH, "⭕ <b>@tannergolden's Turn</b> · 2 open cells"),
                        (TTT_FRESH_HOUSE, "⭕ <b>GitHub's Turn</b> · 1 open cell ·"),
                        (C4_GITHUB, "⚫ <b>GitHub's Turn</b> · 2 open columns"),
                        (C4_HOUSE, "⚫ <b>@tannergolden's Turn</b> · 1 open column ·"),
                        (C4_FRESH, "⚪ <b>@tannergolden's Turn</b> · 2 open columns"),
                        (C4_FRESH_HOUSE, "⚪ <b>GitHub's Turn</b> · 2 open columns"),
                        (CK_GITHUB, "⛀ <b>GitHub's Turn</b> · 1 legal move ·")):
            with self.subTest(board=name(d)):
                self.assertIn(f"<summary>{said}", ED.block(d["kind"], d, "assets/elements"))
        x_turn = dict(TTT_FRESH_HOUSE, board=".../.O./X..", history=[[1, "Xa1", "Ob2", "@imvale"], [2, "", "", ""]],
                      last={"move": "Ob2", "words": "O takes the centre", "by": "@imvale", "when": "15 Oct"},
                      moves=[row("tictactoe", "🗡️", "Corner Them!", "Xc3", "X takes the upper right corner", 11, 3)],
                      prompt="🛑 **@tannergolden's turn as X!** GitHub played 1... Ob2.")
        self.assertIn("<summary>❌ <b>@tannergolden's Turn</b> · 1 open cell · only @tannergolden can play these"
                      "</summary>", ED.block("tictactoe", x_turn, "assets/elements"))

    def test_a_fresh_board_names_the_arbiters_opening_move_and_why(self):
        for d in (TTT_FRESH, C4_FRESH):
            alt = E.alt(d["kind"], d)
            with self.subTest(kind=d["kind"]):
                self.assertIn("the Arbiter's move for GitHub", alt)
                self.assertIn("It is @tannergolden's turn", alt)
                self.assertIn("The Arbiter opens every game for a side drawn at random",
                              ED.block(d["kind"], d, "assets/elements"))
        self.assertIn("GitHub plays X and @tannergolden O, after 1. Xb2, the Arbiter's move for GitHub: X takes the"
                      " centre. It is @tannergolden's turn as O, due by 21 Oct.", E.alt("tictactoe", TTT_FRESH))
        self.assertIn("@tannergolden drops the dark discs and GitHub the light, after 1. 3, the Arbiter's move for"
                      " @tannergolden: a dark disc down column 3, to row 1. It is GitHub's turn as Light",
                      E.alt("connectfour", C4_FRESH_HOUSE))

    def test_the_sides_are_named_in_move_order_both_ways_round(self):
        # X and the dark discs first, whichever side the Arbiter opened for: the house's colour changes game to game
        for d, said in ((TTT_FRESH, "GitHub plays X and @tannergolden O"),
                        (TTT_FRESH_HOUSE, "@tannergolden plays X and GitHub O"),
                        (C4_FRESH, "GitHub drops the dark discs and @tannergolden the light"),
                        (C4_FRESH_HOUSE, "@tannergolden drops the dark discs and GitHub the light")):
            with self.subTest(board=name(d)):
                self.assertIn(said, E.alt(d["kind"], d))
        for d, first in ((C4_GITHUB, "DARK · GITHUB"), (C4_HOUSE, "DARK · HOUSE")):
            racks = [r for r in lettered(d, "standard") if r.startswith(("DARK ·", "LIGHT ·"))]
            with self.subTest(board=name(d)):
                self.assertEqual(racks[0], first, "the opener's dark discs on top")
                self.assertEqual(len(racks), 2)

    def test_a_finished_game_is_its_banner_its_board_and_its_note_with_nothing_to_play(self):
        # what the picture cannot say, as the engine writes it on a finished board: a link in it is a link
        over = ("Game 1 is over, and its final board stays up for two days: game 2 opens 15 Oct, 16:00 EST, and "
                "nothing can be played until then. Every finished game is kept as a "
                "[PDN](https://github.com/tannergolden/tannergolden/tree/HEAD/.github/checkers/games).")
        for d in (*Finished.BOARDS, *(dict(b, note=over) for b in Finished.BOARDS)):
            text = ED.block(d["kind"], d, "assets/elements")
            with self.subTest(board=name(d), note=d["note"][:20]):
                self.assertEqual(E.game_of(d["kind"]).check(d), [])
                self.assertIn(f"> [!IMPORTANT]\n> {d['prompt']}\n\n<picture>", text)
                self.assertNotIn("<details>", text)
                self.assertTrue(text.endswith(f"</picture>\n\n{d['note']}\n<!-- markdown:element:{d['kind']}:end -->"))

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
