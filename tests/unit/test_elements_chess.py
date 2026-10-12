# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess elements: the game on @tannergolden's profile and its Hall of Fame, in every theme, and nowhere else.

The game is the Max Lange Attack the design was drawn from, game 13 after 21. Nd6+: GitHub to move and in check,
the knight just landed with check, a few pieces taken each side. The house's turn is the same game after
21... cxd6, and the opening board is game 1 before anyone has moved. The Hall of Fame is that series after twelve
games, five winners ranked; an empty one has had no game finish yet, and a known one is the same Hall with each row's
account ID, by which a run reads the login every player has now."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support
from tests.fakes.github import FakeGitHub

from app.parts import elements as measure
from infra.github import ApiError
from domain.canvas import BUDGET, lint
from domain.elements import chess as C
from domain.elements import data as ED
from domain.elements import draw as E
from domain.elements.chess import readme as RM
from domain.lettering import Lettering
from domain.prints import PRINTS, STANDARD

support.install()
DASHES = ("–", "—", "―")


def link(uci: str, game: int = 13, move: int = 42) -> str:
    """A move's link to its ready-made issue, its title naming the move in UCI."""
    return (f"https://github.com/tannergolden/play/issues/new?template=move.yml&title=chess%3A%20{uci}%20%C2%B7%20game"
            f"%20{game}%20%C2%B7%20move%20{move}")


LINK = link("c7d6")
GAME = {
    "kind": "chess", "fen": "2kr4/ppp4p/2nNp3/2b1q3/2p3P1/2PrR3/PP1B1P1P/R4QK1 b - - 3 21",
    "game": 13, "move": 21, "players": 9, "due": "18 Oct", "check": "c8",
    "last": {"san": "Nd6+", "from": "e4", "to": "d6", "piece": "knight", "captured": "",
             "words": "Knight from e4 to d6, check", "by": "@tannergolden", "when": "11 Oct"},
    "taken": {"white": "bpp", "black": "nbp"},
    "history": [[19, "Bxd2", "Qxg7", "@imvale"], [20, "Re3", "Qe5", "@jhalloran"], [21, "Nd6+", "", ""]],
    "prompt": "🟢 **GitHub's turn!** You're in check. Pick a move below, by 18 Oct.",
    "note": "The first move to arrive is the one played.",
    "moves": [{"piece": "king", "list": [["🏰", "The Royal Retreat", "Kb8", "King from c8 to b8", LINK],
                                         ["👑", "Long Live the King", "Kd7", "King from c8 to d7", LINK]]},
              {"piece": "queen", "list": [["🩸", "First Blood", "Qxd6", "Queen from e5 takes the knight on d6", LINK]]},
              {"piece": "pawn", "list": [["🗡️", "Cut Them Down", "cxd6", "Pawn from c7 takes the knight on d6", LINK]]}],
}
HOUSE = dict(GAME, fen="2kr4/pp5p/2npp3/2b1q3/2p3P1/2PrR3/PP1B1P1P/R4QK1 w - - 0 22", move=22, players=10,
             due="19 Oct", check="", taken={"white": "bpp", "black": "nbpn"},
             last={"san": "cxd6", "from": "c7", "to": "d6", "piece": "pawn", "captured": "knight",
                   "words": "Pawn from c7 takes the knight on d6", "by": "@wrencastellan", "when": "12 Oct"},
             history=[[20, "Re3", "Qe5", "@jhalloran"], [21, "Nd6+", "cxd6", "@wrencastellan"], [22, "", "", ""]],
             prompt="🛑 **@tannergolden's turn!** GitHub played 21... cxd6.")
OPENING = {"kind": "chess", "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "game": 1, "move": 1}
HALL = {"kind": "chess-hall", "games": 12, "house": 5, "world": 6, "draws": 1,
        "people": [["tannergolden", 5, "2 Oct", 12], ["imvale", 2, "19 Sep", 7], ["tokafor", 2, "27 Sep", 5],
                   ["wrencastellan", 1, "4 Sep", 6], ["jhalloran", 1, "8 Oct", 3]],
        "names": {"imvale": "Imogen Vale", "tokafor": "Tomas Okafor"},
        "leaders": [["tannergolden", 1204, 5, 12], ["imvale", 40, 2, 7], ["tokafor", 31, 2, 5],
                    ["wrencastellan", 52, 1, 6], ["jhalloran", 12, 1, 3], ["octocat", 9, 0, 2]]}
EMPTY = {"kind": "chess-hall", "games": 0, "house": 0, "world": 0, "draws": 0, "people": []}
# The densest board the contract accepts: queens wherever a pawn could have been crowned, every letter and digit in
# the panel's words and logins, and every number at its longest: a game, a move and its players at nine digits, and
# the move the position is on and the score sheet's rows at five.
LETTERS = "abcdefghijklmnopqrstuvwxyz0123456789"
DENSE = dict(GAME, fen="rqqqkqqr/qqqqqqqq/8/8/8/8/QQQQQQQQ/RQQQKQQR b - - 0 99999", game=123456789,
             move=987654321, players=102345678, check="e8", taken={"white": "qrbnp" * 3, "black": "qrbnp" * 3},
             last={"san": "Qa1xb2+", "from": "a1", "to": "b2", "piece": "queen", "captured": "knight",
                   "words": "The quick brown fox jumps over a lazy dog 0123456789 THE QUICK BROWN FOX JUMPS V",
                   "by": "@" + LETTERS[:39], "when": "27 Oct"},
             history=[[99997, "Qa1xb2+", "exd8=Q#", "@" + LETTERS[3:] + "-xy"],
                      [99998, "O-O-O+", "Nb1xc3+", "@" + LETTERS[::-1][:39]], [99999, "Rh8xg7#", "", ""]])
# The same series as HALL, every row carrying its account's ID, the house's included.
IDS = {"tannergolden": 24684994, "imvale": 1001, "tokafor": 1002, "wrencastellan": 1003, "jhalloran": 1004,
       "octocat": 583231}
KNOWN = dict(HALL, people=[[*row, IDS[row[0]]] for row in HALL["people"]],
             leaders=[[*row, IDS[row[0]]] for row in HALL["leaders"]])
TONES = (STANDARD, *sorted(PRINTS))


class EveryFile(unittest.TestCase):
    def test_every_file_in_every_theme_is_well_formed_within_budget_and_deterministic(self):
        for d in (GAME, HALL):
            for tone in TONES:
                for variant in E.variants(d["kind"], d):
                    for theme in ("day", "dark"):
                        svg = E.draw(d["kind"], d, tone, theme, variant)  # the kit's lint and budget, or it raises
                        with self.subTest(kind=d["kind"], tone=tone, variant=variant, theme=theme):
                            minidom.parseString(svg)
                            self.assertEqual(svg, E.draw(d["kind"], d, tone, theme, variant))
                            self.assertNotIn("<text", svg)
                            self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[d["kind"]][2]]), [])
                            for ch in DASHES:
                                self.assertNotIn(ch, svg)

    def test_the_densest_board_the_contract_accepts_is_drawn_with_room_to_spare(self):
        # A board over budget fails the whole run, and the page's moves stay a turn behind, so the densest board
        # the data allows keeps clear of the board's budget in every tone and every file.
        self.assertEqual(C.check(DENSE), [])
        for tone in TONES:
            for variant in E.variants("chess", DENSE):
                with self.subTest(tone=tone, variant=variant):
                    svg = E.draw("chess", DENSE, tone, "dark", variant)
                    self.assertLess(len(svg.encode()), BUDGET["board"] * 0.97)

    def test_the_still_files_stand_still_and_the_rest_move(self):
        for d in (GAME, HALL):
            for variant in E.variants(d["kind"], d):
                svg = E.draw(d["kind"], d, "blackprint", "day", variant)
                with self.subTest(kind=d["kind"], variant=variant):
                    if variant.endswith("still") or variant.startswith("badge-") and variant != "badge-1":
                        self.assertNotIn("<animate", svg)
                    else:
                        self.assertIn("<animate", svg)

    def test_a_board_before_its_first_move_and_a_hall_before_its_first_winner_are_drawn(self):
        for d in (OPENING, EMPTY, dict(HALL, games=1, house=1, world=0, draws=0, people=HALL["people"][:1])):
            for tone in (STANDARD, "blackprint"):
                for variant in E.variants(d["kind"], d):
                    svg = E.draw(d["kind"], d, tone, "dark", variant)
                    self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[d["kind"]][2]]), [], (d["kind"], tone, variant))


class Board(unittest.TestCase):
    PHANTOM = 'stroke-dasharray="4 1.4 1 1.4"'  # a piece in phantom lines: where the last move's piece stood
    CLOUD = re.compile(r'<path d="M[^"]*a[^"]*Z" fill="none" stroke="#[0-9A-Fa-f]{6}" stroke-width="1.5"')

    def test_the_last_move_and_the_check_are_marked(self):
        svg = E.draw("chess", GAME, "blackprint", "day", "still")
        self.assertIn(self.PHANTOM, svg)
        self.assertRegex(svg, self.CLOUD, "the revision cloud round the king in check")
        quiet = E.draw("chess", OPENING, "blackprint", "day", "still")
        self.assertNotIn(self.PHANTOM, quiet)
        self.assertNotRegex(quiet, self.CLOUD)

    def test_its_title_and_description_say_who_plays_whose_turn_it_is_and_where_everything_stands(self):
        alt = E.alt("chess", GAME)
        self.assertTrue(alt.startswith("Chess: game 13, move 21. Game 13 of @tannergolden against GitHub, after "
                                       "21. Nd6+: knight from e4 to d6, check. It is GitHub's turn, in check, due by "
                                       "18 Oct."), alt)
        self.assertIn("White: king g1; queen f1; rooks a1 and e3", alt)
        self.assertIn("It is @tannergolden's turn, due by 19 Oct.", E.alt("chess", HOUSE))
        self.assertIn("before its first move. It is @tannergolden's turn.", E.alt("chess", OPENING))

    def test_what_each_side_took_comes_from_the_engine_else_from_the_position(self):
        self.assertEqual(C.board_state(GAME)["taken"], {"white": ["bishop", "pawn", "pawn"],
                                                         "black": ["bishop", "knight", "pawn"]})
        self.assertEqual(C.captured("4k3/8/8/8/8/8/8/4K3 w - - 0 1"), ("qrrbbnnpppppppp", "QRRBBNNPPPPPPPP"))
        bare = {k: v for k, v in GAME.items() if k != "taken"}
        self.assertEqual(len(C.board_state(bare)["taken"]["white"]), len(C.captured(GAME["fen"])[0]))

    def test_the_last_move_is_numbered_from_the_position(self):
        self.assertEqual((C.board_state(GAME)["last"]["number"], C.board_state(GAME)["last"]["side"]), (21, "white"))
        self.assertEqual((C.board_state(HOUSE)["last"]["number"], C.board_state(HOUSE)["last"]["side"]), (21, "black"))

    def test_without_a_move_of_its_own_the_board_is_on_the_move_its_position_says(self):
        bare = {k: v for k, v in GAME.items() if k != "move"}
        self.assertEqual(C.check(bare), [])
        self.assertEqual(C.board_state(bare)["move"], 21)
        self.assertTrue(E.alt("chess", bare).startswith("Chess: game 13, move 21."))
        self.assertEqual(C.board_state({**GAME, "move": 20})["move"], 20, "a move of its own is the one drawn")
        plain = {"kind": "chess", "fen": OPENING["fen"]}
        self.assertEqual((C.board_state(plain)["game"], C.board_state(plain)["move"], C.board_state(plain)["players"]),
                         (1, 1, 0))


class Hall(unittest.TestCase):
    def test_it_ranks_the_winners_and_says_the_series(self):
        desc = E.alt("chess-hall", HALL)
        self.assertIn("12 games of @tannergolden against GitHub: @tannergolden won 5, GitHub 6, and 1 was drawn.", desc)
        self.assertIn("Ranked by wins: @tannergolden with 5 wins, @imvale with 2 wins", desc)
        self.assertIn("waits for its first winner", E.alt("chess-hall", EMPTY))

    def test_a_winner_is_named_by_their_profile_else_by_their_login_and_the_owner_is_the_house(self):
        people = C.hall_state(HALL)["people"]
        self.assertEqual([(p["name"], p["initials"], p["house"]) for p in people[:4]],
                         [("@TANNERGOLDEN", "TA", True), ("IMOGEN VALE", "IV", False), ("TOMAS OKAFOR", "TO", False),
                          ("@WRENCASTELLAN", "WR", False)])
        self.assertEqual([p["handle"] for p in people[:4]],
                         ["the house  ·  white", "@imvale", "@tokafor", "github  ·  black"])

    def test_a_player_is_shown_by_the_login_their_account_has_now_and_one_whose_account_is_gone_not_at_all(self):
        # @imvale renamed to @imogen-vale; @tokafor deleted their account, and a stranger may hold that login now;
        # @wrencastellan's ID has not been read yet; @jhalloran's row carries no ID.
        logins = {"1001": "imogen-vale", "1002": "", "583231": "octocat"}
        names = {"imogen-vale": "Imogen Vale", "tokafor": "Mallory Mallet", "imvale": "Someone Else"}
        d = dict(KNOWN, people=[*KNOWN["people"][:4], HALL["people"][4]], logins=logins, names=names)
        self.assertEqual(C.check_hall(d), [])
        h = C.hall_state(d)
        self.assertEqual([(p["login"], p["name"], p["handle"], p["badge"], p["id"]) for p in h["people"]],
                         [("tannergolden", "@TANNERGOLDEN", "the house  ·  white", "@tannergolden", 24684994),
                          ("imogen-vale", "IMOGEN VALE", "@imogen-vale", "@imogen-vale", 1001),
                          ("wrencastellan", "@WRENCASTELLAN", "github  ·  black", "@wrencastellan", 1003),
                          ("jhalloran", "@JHALLORAN", "github  ·  black", "@jhalloran", None)])
        self.assertEqual([(r["login"], r["id"], r["house"]) for r in h["leaders"]],
                         [("tannergolden", 24684994, True), ("imogen-vale", 1001, False),
                          ("wrencastellan", 1003, False), ("jhalloran", 1004, False), ("octocat", 583231, False)])
        self.assertIn("Ranked by wins: @tannergolden with 5 wins, @imogen-vale with 2 wins, @wrencastellan with 1 win,"
                      " @jhalloran with 1 win.", E.alt("chess-hall", d))
        self.assertNotIn("tokafor", E.alt("chess-hall", d))
        house = dict(d, logins={**logins, "24684994": "someone"})
        self.assertEqual(C.hall_state(house)["people"][0]["login"], "tannergolden", "the house is always the house")

    def test_a_name_s_initials_are_its_first_letters_in_any_script(self):
        self.assertEqual(C.game.initials("Élodie Durand", "edurand"), "ÉD")
        self.assertEqual(C.game.initials("Ana-María Núñez", "anm"), "AM")
        self.assertEqual(C.game.initials("", "octocat"), "OC")

    def test_each_winner_has_a_badge_and_the_leaders_has_a_still_twin(self):
        self.assertEqual(E.variants("chess-hall", HALL), ("wide", "narrow", "still", "narrow-still", "badge-1",
                                                          "badge-1-still", "badge-2", "badge-3", "badge-4", "badge-5"))
        self.assertEqual(E.variants("chess-hall", EMPTY), ("wide", "narrow", "still", "narrow-still"))
        gone = dict(KNOWN, logins={"1002": "", "1003": ""})
        self.assertEqual(E.variants("chess-hall", gone), ("wide", "narrow", "still", "narrow-still", "badge-1",
                                                          "badge-1-still", "badge-2", "badge-3"),
                         "a badge for each winner shown, and none for a winner whose account is gone")

    def test_a_place_an_account_that_is_gone_leaves_is_filled_from_the_rows_under_it(self):
        # The engine hands over twice the places: ten winners and twenty of GitHub's players, for five and ten.
        players = [f"player-{i:02}" for i in range(1, 21)]
        uids = {login: 2000 + i for i, login in enumerate(players, 1)}
        people = [["tannergolden", 30, "2 Oct", 40, 24684994]]
        people += [[login, 20 - i, "1 Oct", 25, uids[login]] for i, login in enumerate(players[:9])]
        leaders = [["tannergolden", 900, 30, 40, 24684994]]
        leaders += [[login, 500 - i, 20 - i if i < 9 else 0, 25, uids[login]] for i, login in enumerate(players)]
        gone = {"player-02", "player-03", "player-07"}
        d = dict(KNOWN, games=60, house=30, world=29, draws=1, people=people, leaders=leaders, names={},
                 logins={str(uids[login]): "" if login in gone else login for login in players})
        self.assertEqual(C.check_hall(d), [])
        h = C.hall_state(d)
        self.assertEqual([p["login"] for p in h["people"]],
                         ["tannergolden", "player-01", "player-04", "player-05", "player-06"])
        self.assertEqual([r["login"] for r in h["leaders"]],
                         ["tannergolden", "player-01", "player-04", "player-05", "player-06", "player-08", "player-09",
                          "player-10", "player-11", "player-12", "player-13"])
        text = ED.block("chess-hall", d, "assets/elements")
        self.assertIn("@tannergolden and GitHub's top 10 · ranked by wins", text)
        self.assertIn("| 🥉 | [@player-05](https://github.com/player-05) | 496 | 16 | 25 |\n", text)
        self.assertTrue(text.split("\n\nA win is")[0].endswith("| 10 | [@player-13](https://github.com/player-13) |"
                                                              " 488 | 0 | 25 |"))
        for login in gone:
            self.assertNotIn(login, text + E.alt("chess-hall", d))
        self.assertEqual(text.count('<a href="https://github.com/'), 5, "five badges, each linked")
        for tone in (STANDARD, "blackprint"):
            for variant in E.variants("chess-hall", d):
                E.draw("chess-hall", d, tone, "dark", variant)  # the kit's lint and budget, or it raises


class Settings(unittest.TestCase):
    def test_both_are_drawn_on_tannergoldens_profile_alone(self):
        section = {"chess": dict(GAME), "chess-hall": dict(HALL)}
        self.assertEqual(ED.validate(section, {}, subject="tannergolden"), [])
        self.assertEqual(ED.validate(section, {}, subject="TannerGolden"), [])
        for elsewhere in ("octocat", "tannergolden/markdown", ""):
            with self.subTest(subject=elsewhere):
                errors = ED.validate(section, {}, subject=elsewhere)
                self.assertIn("chess: the chess element is drawn on @tannergolden's profile alone", errors)
                self.assertIn("chess-hall: the chess-hall element is drawn on @tannergolden's profile alone", errors)

    def test_what_the_board_is_drawn_from_is_checked(self):
        cases = {
            "fen": ("8/8/8/8/8/8/8/8 w - - 0 1", "does not have one king a side"),
            "check": ("e9", "is not the square of the king to move"),
            "due": ("tomorrow", "is not a day"),
            "last": ({**GAME["last"], "from": "e9"}, "last: from"),
            "taken": ({"white": "kk"}, "taken gives white and black"),
            "history": ([[19, "Bxd2", "<b>", "@imvale"]], "history:"),
            "prompt": ("<b>move</b>", "one line of text"),
            "note": ("a | b", "one line of text"),
            "moves": ([{"piece": "pawn", "list": [["🥾", "Forward | March", "e4", "Pawn from e2 to e4", LINK]]}],
                      "is not an emoji, a title"),
        }
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                errors = " ".join(ED.validate({"chess": {**GAME, key: bad}}, {}, subject="tannergolden"))
                self.assertIn(said, errors)
        wrong_link = [{"piece": "pawn", "list": [["🥾", "March", "e4", "Pawn from e2 to e4", "https://example.com/x"]]}]
        self.assertTrue(ED.validate({"chess": {**GAME, "moves": wrong_link}}, {}, subject="tannergolden"))
        self.assertIn("a chess needs fen", " ".join(ED.validate({"chess": {"kind": "chess"}}, {}, subject="tannergolden")))

    def assertTurnedAway(self, d: dict, said: str, check=C.check):
        errors = check(d)
        self.assertTrue(any(said in e for e in errors), f"{said!r} not in {errors}")

    def test_text_is_text_and_a_number_a_number_within_its_ceiling(self):
        # YAML reads `note: 1984` as a number, `true` as a bool and an all-digit login as an int: each is turned
        # away here rather than reaching the README, which would fail on it.
        move = ["🏰", "The Royal Retreat", "Kb8", "King from c8 to b8", LINK]
        texts = {"note": (1984, True, ["a note"]), "prompt": (1984, {"a": 1}), "check": (8, True), "due": (18,),
                 "fen": (1984, None), "last": ({**GAME["last"], "words": 1984}, {**GAME["last"], "by": None},
                                              {**GAME["last"], "when": 11}),
                 "taken": ({"white": 5}, {"white": ["p"]}),
                 "history": ([[21, 1984, "", ""]], [[21, "Nd6+", "", 7]], [[21, ["Nd6+"], "", ""]]),
                 "moves": ([{"piece": "king", "list": [[*move[:1], 1984, *move[2:]]]}],
                           [{"piece": "king", "list": [[*move[:4], 5]]}],
                           [{"piece": "king", "list": [[1, *move[1:]]]}])}
        for key, values in texts.items():
            for bad in values:
                with self.subTest(key=key, bad=bad):
                    self.assertTrue(C.check({**GAME, key: bad}))
        numbers = {"game": ("13", True, 0, -1, 1_000_000_000, 13.0, None), "move": ("21", False, 0, 1_000_000_000),
                   "players": ("9", True, -1, 1_000_000_000, 9.5)}
        for key, values in numbers.items():
            for bad in values:
                with self.subTest(key=key, bad=bad):
                    self.assertTurnedAway({**GAME, key: bad}, f"{key} {bad!r} is not a number from")
        for key, fine in (("game", 999_999_999), ("move", 999_999_999), ("players", 999_999_999), ("players", 0)):
            with self.subTest(key=key, fine=fine):
                self.assertEqual(C.check({**GAME, key: fine}), [])
        for row in ([True, "Bxd2", "Qxg7", "@imvale"], [-19, "Bxd2", "Qxg7", "@imvale"], [0, "Bxd2", "", ""],
                    [100_000, "Bxd2", "", ""], ["19", "Bxd2", "", ""]):
            with self.subTest(row=row):
                self.assertTurnedAway({**GAME, "history": [row]}, "is not a row of a move's number up to 99,999")
        self.assertEqual(C.check({**GAME, "history": [[99_999, "Bxd2", "Qxg7", "@imvale"]]}), [])
        for fen in ("2kr4/ppp4p/2nNp3/2b1q3/2p3P1/2PrR3/PP1B1P1P/R4QK1 b - - 3 0",
                    "2kr4/ppp4p/2nNp3/2b1q3/2p3P1/2PrR3/PP1B1P1P/R4QK1 b - - 3 100000"):
            with self.subTest(fen=fen):
                self.assertTurnedAway({**GAME, "fen": fen}, "is not a position in FEN, on a move from 1 to 99,999")

    def test_a_position_is_eight_ranks_of_eight_squares_in_ascii_digits_and_never_crashes_the_check(self):
        cases = {"7pp/8/8/8/8/8/8/K6k w - - 0 1": "does not have eight squares on every rank",
                 "88/8/8/8/8/8/8/K6k w - - 0 1": "does not have eight squares on every rank",
                 "4k2/8/8/8/8/8/8/4K3 w - - 0 1": "does not have eight squares on every rank",
                 "08/8/8/8/8/8/8/K6k w - - 0 1": "is not a position in FEN",
                 "٨/8/8/8/8/8/8/K6k w - - 0 1": "is not a position in FEN",
                 "８/8/8/8/8/8/8/K6k w - - 0 1": "is not a position in FEN",
                 "4k3/8/8/8/8/8/8/4K3 w - - ٠ ١": "is not a position in FEN",
                 "4k3/8/8/8/8/8/8/4K3 w - - 0 ２": "is not a position in FEN",
                 "4k3/8/8/8/8/8/8/4K3 w - - ٣ 1": "is not a position in FEN",
                 "4k3/8/8/8/8/8/8/4K3 w - - 0 2١": "is not a position in FEN",
                 "4k3/8/8/8/8/8/8/4K3 w - - ３ 21": "is not a position in FEN"}
        for fen, said in cases.items():
            with self.subTest(fen=fen):
                self.assertTurnedAway({**OPENING, "fen": fen}, said)
        for history in (5, True, "Nd6+", {"21": "Nd6+"}):
            with self.subTest(history=history):
                self.assertTurnedAway({**GAME, "history": history}, "history is a list of the score sheet's rows")
        self.assertEqual(C.check({**GAME, "history": None}), [])
        self.assertEqual(C.check({**GAME, "history": []}), [])

    def test_a_line_of_the_readme_never_opens_a_block_or_shows_an_image(self):
        # The note follows the moves after a blank line and the prompt is the banner's second line, so anything that
        # opens a block there swallows the README's end marker or turns the alert into a heading.
        blocks = ("```", "```python", "~~~", "# Heading", "### Heading", "- an item", "* an item", "+ an item",
                  "1. an item", "21) an item", "    code", "\tcode", " a space first", "---", "===", "=", "-", "***",
                  "- - -", "_ _ _", "[a]: https://example.com", "[^1]: a footnote")
        for key in ("note", "prompt"):
            for bad in blocks:
                with self.subTest(key=key, bad=bad):
                    self.assertTurnedAway({**GAME, key: bad}, f"{key} {bad!r} would open a block of its own")
            for bad in ("![a pawn](https://example.com/pawn.png)", "See ![it](https://example.com/x.png) here"):
                with self.subTest(key=key, bad=bad):
                    self.assertTurnedAway({**GAME, key: bad}, f"{key} shows an image")
        fine = ("🟢 **GitHub's turn!** @tannergolden played 1. e4. Pick a move below by 18 Oct.",
                "🛑 **@tannergolden's turn!** GitHub played 21... cxd6. Check! Reply due by 19 Oct.",
                "🛑 **@tannergolden's turn!** @tannergolden opens game 1 as White, and GitHub plays Black.",
                ("Anyone but @tannergolden can play on this turn, and the first pick in is played. Every finished game"
                 " is kept as a [PGN](https://github.com/tannergolden/tannergolden/tree/HEAD/.github/chess/games)."),
                "Game 2 was drawn by stalemate. Only @tannergolden can play on this turn.",
                "21... cxd6 was the reply.", "**Bold** first.", "#1 on the board.", "+1 for the knight.",
                "-5 is a lot.")
        for text in fine:
            with self.subTest(text=text):
                self.assertEqual(C.check({**GAME, "note": text, "prompt": text}), [])

    def test_a_move_title_has_no_space_at_either_end(self):
        for title in ("The Royal Retreat ", " The Royal Retreat", "Retreat  "):
            with self.subTest(title=title):
                moves = [{"piece": "king", "list": [["🏰", title, "Kb8", "King from c8 to b8", LINK]]}]
                self.assertTurnedAway({**GAME, "moves": moves}, "is not an emoji, a title")
        for title in ("A", "Go!", "The Royal Retreat", "x" * 100):
            with self.subTest(title=title):
                moves = [{"piece": "king", "list": [["🏰", title, "Kb8", "King from c8 to b8", LINK]]}]
                self.assertEqual(C.check({**GAME, "moves": moves}), [])
        moves = [{"piece": "king", "list": [["🏰", "x" * 101, "Kb8", "King from c8 to b8", LINK]]}]
        self.assertTurnedAway({**GAME, "moves": moves}, "is not an emoji, a title")

    def test_the_marks_on_the_board_and_the_score_sheet_are_ones_the_game_can_have(self):
        self.assertTurnedAway({**GAME, "history": [[21, "", "cxd6", "@wrencastellan"]]},
                              "has Black's move without White's")
        for square in ("e4", "d8", "g1"):  # an empty square, a rook, and White's king on Black's turn
            with self.subTest(check=square):
                self.assertTurnedAway({**GAME, "check": square}, "is not the square of the king to move")
        self.assertTurnedAway({**HOUSE, "check": "c8"}, "is not the square of the king to move")
        self.assertEqual(C.check({**HOUSE, "fen": "2kr4/pp5p/2npp3/2b5/2p3P1/2PrR3/PP1B1P1P/R4qK1 w - - 0 22",
                                  "check": "g1"}), [])
        for day in ("99 Zzz", "32 Oct", "31 Sep", "30 Feb", "0 Oct", "18 Octo", "18  Oct"):
            with self.subTest(due=day):
                self.assertTurnedAway({**GAME, "due": day}, "is not a day")
                self.assertTurnedAway({**GAME, "last": {**GAME["last"], "when": day}}, "last: when")
        for day in ("1 Jan", "29 Feb", "30 Sep", "31 Dec", "18 OCT"):
            with self.subTest(due=day):
                self.assertEqual(C.check({**GAME, "due": day}), [])
        before = {**OPENING, "last": {**GAME["last"]}}
        self.assertTurnedAway(before, "a board before White's first move has no last move")

    def test_nothing_the_settings_can_hold_makes_the_checks_raise(self):
        hostile = (None, True, False, 0, -1, 1984, 10 ** 30, 1.5, "", "x", "```", [], [1], [[]], {}, {"a": 1},
                   ["x", "y", "z", "w", "v"])
        rows = ("history", "moves", "people", "leaders")
        for d, check in ((GAME, C.check), (HOUSE, C.check), (KNOWN, C.check_hall)):
            for key in sorted(set(d) | {"logins", "names", "history", "last", "taken", "result", "next"}):
                for bad in hostile:
                    for value in (bad, [bad], [[bad] * 5]) if key in rows else (bad,):
                        with self.subTest(key=key, value=value):
                            self.assertIsInstance(check({**d, key: value}), list)
        for bad in hostile:
            with self.subTest(last=bad):
                self.assertIsInstance(C.check({**GAME, "last": {k: bad for k in GAME["last"]}}), list)
                key = bad if isinstance(bad, (str, int)) else "x"
                self.assertIsInstance(C.check_hall({**KNOWN, "names": {key: bad}, "logins": {key: bad}}), list)

    def test_what_the_hall_is_drawn_from_is_checked(self):
        cases = {
            "games": (11, "add up to 12 games, not the 11 played"),
            "people": ([["not a login!", 1, "2 Oct", 1]], "people:"),
            "names": ({"imvale": "<script>"}, "names gives a login its name"),
        }
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                self.assertIn(said, " ".join(ED.validate({"h": {**HALL, key: bad}}, {}, subject="tannergolden")))
        ten = HALL["people"] + [[f"spare-{i}", 1, "1 Oct", 1] for i in range(5)]
        self.assertEqual(ED.validate({"h": {**HALL, "people": ten}}, {}, subject="tannergolden"), [])
        self.assertIn("at most 10 winners", " ".join(ED.validate({"h": {**HALL, "people": ten + [ten[-1]]}}, {},
                                                                 subject="tannergolden")))

    def test_a_winner_is_a_login_with_counts_the_sheet_can_letter_ranked_by_their_wins(self):
        def turned_away(d: dict, said: str):
            errors = C.check_hall(d)
            self.assertTrue(any(said in e for e in errors), f"{said!r} not in {errors}")

        one = {**HALL, "games": 1, "house": 0, "world": 1, "draws": 0, "names": {}}
        rows = ([12345, 1, "2 Oct", 1], ["imvale", True, "2 Oct", 1], ["imvale", 1, "2 Oct", False],
                ["imvale", 0, "2 Oct", 1], ["imvale", -1, "2 Oct", 1], ["imvale", 1_000_000, "2 Oct", 1],
                ["imvale", 1, "2 Oct", 1_000_000], ["imvale", "1", "2 Oct", 1], ["imvale", 1, 1984, 1],
                ["imvale", 1, "31 Sep", 1], ["imvale", 1, "2 Oct"], ["imvale", 1, "2 Oct", 1, 1001, 1])
        for row in rows:
            with self.subTest(row=row):
                turned_away({**one, "people": [row]}, f"people: {row!r} is not a winner's login")
        self.assertEqual(C.check_hall({**one, "people": [["12345", 1, "2 Oct", 1]]}), [], "an all-digit login, as text")
        for counts in ({"games": True}, {"games": 1_000_000, "house": 1_000_000, "world": 0, "draws": 0},
                       {"draws": -1}, {"world": "6"}):
            with self.subTest(counts=counts):
                turned_away({**HALL, **counts}, "are counts of games, up to 999,999")
        self.assertEqual(C.check_hall({**EMPTY, "games": 999_999, "house": 999_999}), [])
        unranked = [["imvale", 1, "2 Oct", 3], ["tokafor", 9, "3 Oct", 12], ["jhalloran", 40, "4 Oct", 50]]
        turned_away({**HALL, "people": unranked, "games": 60, "house": 10, "world": 50, "draws": 0},
                    "people: the winners are ranked by their wins, the most first")
        tied = [HALL["people"][0], HALL["people"][2], HALL["people"][1], HALL["people"][4], HALL["people"][3]]
        self.assertEqual(C.check_hall({**HALL, "people": tied}), [], "winners on the same wins stand in any order")

    def test_a_name_is_plain_text_without_an_at_that_fits_in_capitals(self):
        for name in ("@tannergolden", "Tanner @ Home", "ß" * 21, "ﬃ" * 14, " ", "\u200b", "\u200d\u200d", 1984, True,
                     ["Imogen Vale"], {"first": "Imogen"}, "", "x" * 41):
            with self.subTest(name=name):
                errors = C.check_hall({**HALL, "names": {"imvale": name}})
                self.assertTrue(any(e.startswith("names gives a login its name") for e in errors), errors)
        for names in ({12345: "Imogen Vale"}, {"not a login!": "Imogen Vale"}, ["imvale"]):
            with self.subTest(names=names):
                self.assertTrue(C.check_hall({**HALL, "names": names}))
        for name in ("ß" * 20, "Imogen Vale", "Tomás Ørsted", "O'Brien-Smith", "J. R. R. T.", "x" * 40, "李"):
            with self.subTest(name=name):
                self.assertEqual(C.check_hall({**HALL, "names": {"imvale": name}}), [])

    def test_a_row_of_the_hall_may_carry_its_accounts_id(self):
        self.assertEqual(C.check_hall(KNOWN), [])
        self.assertEqual(C.check_hall({**KNOWN, "people": HALL["people"][:2] + KNOWN["people"][2:]}), [],
                         "rows with an ID and rows without one stand side by side")
        ceiling = [[*HALL["people"][0], 9_999_999_999_999_999]]
        self.assertEqual(C.check_hall({**HALL, "people": ceiling, "leaders": [[*HALL["leaders"][0], 1]]}), [])
        for uid in (0, -1, True, "1001", 10_000_000_000_000_000, 1001.0, None):
            with self.subTest(uid=uid):
                people = [[*HALL["people"][0], uid]]
                self.assertTrue(any(e.startswith("people:") for e in C.check_hall({**HALL, "people": people})))
                leaders = [[*HALL["leaders"][0], uid]]
                self.assertTrue(any(e.startswith("leaders:") for e in C.check_hall({**HALL, "leaders": leaders})))
        for logins in ({"1001": "imogen-vale"}, {"1001": ""}, {"9999999999999999": "octocat"}, {}):
            with self.subTest(logins=logins):
                self.assertEqual(C.check_hall({**KNOWN, "logins": logins}), [])
        for logins in ({1001: "imogen-vale"}, {"01001": "imogen-vale"}, {"1001": "not a login!"}, {"1001": None},
                       {"1001": 1001}, {"10000000000000000": "octocat"}, {"imvale": "imogen-vale"}, ["1001"], "1001"):
            with self.subTest(logins=logins):
                errors = C.check_hall({**KNOWN, "logins": logins})
                self.assertTrue(any(e.startswith("logins gives an account's ID its login") for e in errors), errors)

    def test_what_the_leaderboard_lists_is_checked(self):
        house = ["tannergolden", 9, 1, 2]
        cases = {
            "a row that is not a login and three counts": [house, ["octocat", "9", 0, 2]],
            "more wins than games": [["tannergolden", 9, 3, 2]],
            "more games than moves": [house, ["octocat", 1, 0, 2]],
            "a login that could break the table": [house, ["octo|cat", 9, 0, 2]],
            "the house not on top": [["octocat", 9, 0, 2], house],
            "the house twice": [house, ["TannerGolden", 9, 0, 2]],
            "a player without a move": [house, ["octocat", 0, 0, 0]],
            "players out of order": [house, ["octocat", 9, 0, 2], ["hubot", 3, 1, 1]],
            "twenty-one players": [house] + [[f"p{i}", 30 - i, 0, 1] for i in range(21)],
            "not a list": "tannergolden",
            "a count past its ceiling": [["tannergolden", 1_000_000_000, 5, 12]],
            "a count that is a bool": [house, ["octocat", 9, False, 2]],
            "a login that is a number": [house, [12345, 9, 0, 2]],
            "an ID that is text": [house, ["octocat", 9, 0, 2, "583231"]],
            "an ID past sixteen digits": [house, ["octocat", 9, 0, 2, 10 ** 16]],
            "a sixth field": [house, ["octocat", 9, 0, 2, 583231, 1]],
        }
        for case, leaders in cases.items():
            with self.subTest(case=case):
                errors = ED.validate({"h": {**HALL, "leaders": leaders}}, {}, subject="tannergolden")
                self.assertTrue(errors and all(e.startswith("h: leaders") for e in errors), errors)
        for fine in ([], [house], [["tannergolden", 0, 0, 0], ["octocat", 1, 0, 1]], HALL["leaders"], KNOWN["leaders"],
                     [["tannergolden", 999_999_999, 999_999_999, 999_999_999, 24684994]],
                     [house] + [[f"p{i}", 30 - i, 0, 1] for i in range(20)]):
            with self.subTest(leaders=fine):
                self.assertEqual(ED.validate({"h": {**HALL, "leaders": fine}}, {}, subject="tannergolden"), [])


class Readme(unittest.TestCase):
    def test_the_board_has_its_turns_banner_above_its_fold_open_and_every_move_folded_under(self):
        # the banner stands at the README's top level, where GitHub draws it as an alert, over the game folded open
        text = ED.block("chess", GAME, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:chess:start -->\n> [!TIP]\n> 🟢 **GitHub's turn!**"))
        self.assertIn("by 18 Oct.\n\n<details open>\n<summary><b>♟️ Chess</b></summary>\n\n<picture>", text)
        self.assertIn("</picture>\n\n<details>\n<summary>♚ <b>GitHub's Turn</b> · 4 legal moves · open to choose one"
                      "</summary>\n\n|  | Move | In words | Play |\n| :-: | :--- | :--- | :-: |\n", text)
        self.assertIn(f"| 🏰 | **The Royal Retreat** `Kb8` | King from c8 to b8 | [Play ↗]({LINK}) |", text)
        self.assertTrue(text.endswith("</details>\n\nThe first move to arrive is the one played.\n\n</details>\n"
                                      "<!-- markdown:element:chess:end -->"))

    def test_the_houses_turn_is_a_caution_and_its_moves_are_the_houses_alone(self):
        text = ED.block("chess", HOUSE, "assets/elements")
        self.assertIn("> [!CAUTION]\n> 🛑 **@tannergolden's turn!**", text)
        self.assertIn("♔ <b>@tannergolden's Turn</b> · 4 legal moves · only @tannergolden can play these", text)

    def test_a_busy_turn_is_grouped_by_piece(self):
        rides = [f"{a}{b}" for a, b in (("b8", "a6"), ("b8", "c6"), ("b8", "d7"), ("g8", "f6"), ("g8", "h6"),
                                         ("g8", "e7"), ("g8", "g6"))]
        many = [{"piece": "knight", "list": [["🐴", f"Ride {i}", "Nf6", "Knight from g8 to f6", link(uci)]
                                             for i, uci in enumerate(rides)]},
                {"piece": "pawn", "list": [["🥾", f"March {i}", "e5", "Pawn from e7 to e5", link(f"{f}7{f}5")]
                                           for i, f in enumerate("abcde")]}]
        text = ED.block("chess", {**GAME, "moves": many}, "assets/elements")
        self.assertIn("· 12 legal moves ·", text)
        self.assertIn("<details open>\n<summary>♞ Knights · 7 moves</summary>\n\n|  | Move |", text)
        self.assertIn("<summary>♟ Pawns · 5 moves</summary>", text)

    def test_a_group_is_named_for_one_piece_or_several_by_the_squares_its_moves_leave(self):
        def row(uci: str) -> list:
            return ["👑", "Long Live the Queen", "Qd2", "Queen from d1 to d2", link(uci)]

        queens = [row(uci) for uci in ("d1d2", "d1d3", "d1e2", "h8h1", "h8g7", "h8h4")]  # a second queen, crowned
        knight = [row(uci) for uci in ("g1f3", "g1h3", "g1e2")]
        king = [row(uci) for uci in ("e1e2", "e1f1")]
        crowning = [row(uci) for uci in ("a7a8q", "a7a8r", "a7a8b", "a7a8n", "a7b8q", "a7b8n")]  # one pawn, six ways
        groups = [{"piece": "queen", "list": queens}, {"piece": "knight", "list": knight},
                  {"piece": "king", "list": king}, {"piece": "pawn", "list": crowning}]
        text = ED.block("chess", {**HOUSE, "moves": groups}, "assets/elements")
        for said in ("♕ Queens · 6 moves", "♘ Knight · 3 moves", "♔ King · 2 moves", "♙ Pawn · 6 moves"):
            self.assertIn(f"<summary>{said}</summary>", text)
        named = {("rook", ("a1a2", "h1h2")): "Rooks", ("rook", ("a1a2", "a1a3")): "Rook",
                 ("bishop", ("c1d2", "f1e2", "c1b2")): "Bishops", ("king", ("e1e2",)): "King"}
        for (piece, ucis), name in named.items():
            self.assertEqual(RM.group_name(piece, [row(uci) for uci in ucis]), name)

    def test_a_phone_asking_for_reduced_motion_gets_its_still_file_first(self):
        pic = ED.picture("chess", GAME, "assets/elements")
        order = [pic.index(f'srcset="assets/elements/chess-{v}-dark.svg"') for v in ("narrow-still", "narrow", "still")]
        self.assertEqual(order, sorted(order))
        self.assertIn('<source media="(max-width: 585px) and (prefers-reduced-motion: reduce)" '
                      'srcset="assets/elements/chess-narrow-still-day.svg">', pic)

    def test_the_hall_links_every_winner_by_their_badge(self):
        text = ED.block("chess-hall", HALL, "assets/elements")
        self.assertIn('<div align="center">\n\n<a href="https://github.com/tannergolden"><picture><source media='
                      '"(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" '
                      'srcset="assets/elements/chess-hall-badge-1-still-dark.svg">', text)
        self.assertIn('<a href="https://github.com/jhalloran"><picture><source media="(prefers-color-scheme: dark)" '
                      'srcset="assets/elements/chess-hall-badge-5-dark.svg"><img alt="#5 @jhalloran, 1 win" '
                      'src="assets/elements/chess-hall-badge-5-day.svg"></picture></a>', text)
        self.assertEqual(text.count("(prefers-reduced-motion: reduce)"), 6,
                         "the hall's wide and phone still files, and the leader's badge, by day and night")
        self.assertNotIn("badge", ED.block("chess-hall", EMPTY, "assets/elements"))

    def test_the_hall_links_each_player_by_the_login_their_account_has_now_and_leaves_a_gone_one_out(self):
        # @imvale is @imogen-vale now; @tokafor deleted their account, so they leave the badges and the leaderboard,
        # and the players under them move up; @jhalloran's ID has not been read, so their row's own login stands.
        d = dict(KNOWN, logins={"1001": "imogen-vale", "1002": "", "1003": "wrencastellan", "583231": "octocat"})
        text = ED.block("chess-hall", d, "assets/elements")
        self.assertIn('<a href="https://github.com/imogen-vale"><picture><source media="(prefers-color-scheme: dark)" '
                      'srcset="assets/elements/chess-hall-badge-2-dark.svg"><img alt="#2 @imogen-vale, 2 wins" ', text)
        self.assertIn('<a href="https://github.com/wrencastellan"><picture><source media="(prefers-color-scheme: '
                      'dark)" srcset="assets/elements/chess-hall-badge-3-dark.svg"><img alt="#3 @wrencastellan, 1 '
                      'win" ', text)
        self.assertIn('<a href="https://github.com/jhalloran"><picture><source media="(prefers-color-scheme: dark)" '
                      'srcset="assets/elements/chess-hall-badge-4-dark.svg">', text)
        self.assertNotIn("badge-5", text)
        self.assertIn("@tannergolden and GitHub's top 4 · ranked by wins", text)
        self.assertIn("| 🥇 | [@imogen-vale](https://github.com/imogen-vale) | 40 | 2 | 7 |\n"
                      "| 🥈 | [@wrencastellan](https://github.com/wrencastellan) | 52 | 1 | 6 |\n", text)
        self.assertNotIn("tokafor", text)
        self.assertNotIn("imvale", text)
        self.assertEqual(text.count("<a href="), 4, "every badge shown is a link")
        self.assertEqual(text.count("(https://github.com/"), 5, "and every leader shown")

    def test_the_leaderboard_is_folded_under_the_badges_with_the_house_on_top(self):
        text = ED.block("chess-hall", HALL, "assets/elements")
        self.assertIn("</picture></a>\n\n</div>\n\n<details>\n<summary>🏆 <b>Leaderboard</b> · @tannergolden and GitHub's"
                      " top 5 · ranked by wins, then moves</summary>\n\n|  | Player | Moves | Wins | Games |\n"
                      "| :-: | :--- | --: | --: | --: |\n| ♔ | **[@tannergolden](https://github.com/tannergolden)** | "
                      "**1,204** | **5** | **12** |\n| 🥇 | [@imvale](https://github.com/imvale) | 40 | 2 | 7 |\n", text)
        self.assertIn("| 🥉 | [@wrencastellan](https://github.com/wrencastellan) | 52 | 1 | 6 |\n"
                      "| 4 | [@jhalloran](https://github.com/jhalloran) | 12 | 1 | 3 |\n", text)
        self.assertTrue(text.endswith("| 5 | [@octocat](https://github.com/octocat) | 9 | 0 | 2 |\n\nA win is a mating"
                                      " move of one's own; a move or a mate the Arbiter plays, for either side, counts"
                                      " for nobody.\n\n</details>\n<!-- markdown:element:chess-hall:end -->"))
        alone = ED.block("chess-hall", {**EMPTY, "leaders": [["tannergolden", 1, 0, 1]]}, "assets/elements")
        self.assertIn("</picture>\n\n<details>\n<summary>🏆 <b>Leaderboard</b> · @tannergolden · GitHub's players join"
                      " with their first move</summary>", alone)
        one = C.leaderboard({**EMPTY, "leaders": [["tannergolden", 1, 0, 1], ["octocat", 1, 0, 1]]})
        self.assertIn("· @tannergolden and GitHub's top player · ranked by wins, then moves</summary>", one)
        self.assertNotIn("Leaderboard", ED.block("chess-hall", EMPTY, "assets/elements"))


# Finished games, each board kept up for two days with its result: the house mates in four (the Scholar's Mate), GitHub
# mates in two (the Fool's Mate), and a stalemate after a long ending.
SCHOLAR = {"kind": "chess", "fen": "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4", "game": 13,
           "move": 4, "players": 3, "check": "e8",
           "last": {"san": "Qxf7#", "from": "h5", "to": "f7", "piece": "queen", "captured": "pawn",
                    "words": "Queen from h5 takes the pawn on f7, checkmate", "by": "@tannergolden", "when": "12 Oct"},
           "taken": {"white": "p", "black": ""},
           "history": [[2, "Bc4", "Nc6", "@imvale"], [3, "Qh5", "Nf6", "@tokafor"], [4, "Qxf7#", "", ""]],
           "result": {"winner": "house", "how": "checkmate"}, "next": "14 Oct",
           "prompt": "🏆 **Checkmate!** @tannergolden wins game 13. Game 14 opens 14 Oct.",
           "note": "Every finished game's board stays up for two days, then a fresh one comes."}
FOOL = {"kind": "chess", "fen": "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3", "game": 12, "move": 3,
        "players": 2, "check": "e1",
        "last": {"san": "Qh4#", "from": "d8", "to": "h4", "piece": "queen", "captured": "",
                 "words": "Queen from d8 to h4, checkmate", "by": "@wrencastellan", "when": "11 Oct"},
        "history": [[1, "f3", "e5", "@imvale"], [2, "g4", "Qh4#", "@wrencastellan"]],
        "result": {"winner": "github", "how": "checkmate"}, "next": "13 Oct",
        "prompt": "🏆 **Checkmate!** GitHub wins game 12, and @wrencastellan takes a place in the Hall of Fame."}
STALEMATE = {"kind": "chess", "fen": "k7/2Q5/1K6/8/8/8/8/8 b - - 0 60", "game": 11, "move": 60, "players": 14,
             "last": {"san": "Qc7", "from": "c5", "to": "c7", "piece": "queen", "captured": "",
                      "words": "Queen from c5 to c7, stalemate", "by": "@tannergolden", "when": "10 Oct"},
             "history": [[58, "Kb6", "Ka8", "@jhalloran"], [59, "Qc5", "Kb8", "@octocat"], [60, "Qc7", "", ""]],
             "result": {"winner": None, "how": "stalemate"}, "next": "12 Oct",
             "prompt": "🤝 **Stalemate!** Game 11 is drawn. Game 12 opens 12 Oct."}
FINISHED = (SCHOLAR, FOOL, STALEMATE)


def lettered(d: dict, tone: str, variant: str = "still") -> list[str]:
    """Every run of lettering a file sets, in capitals: what a sheet says, since its letters are drawn as paths."""
    runs, text = [], Lettering.text

    def record(self, s, **k):
        runs.append(str(s).upper())
        return text(self, s, **k)
    with mock.patch.object(Lettering, "text", record):
        E.draw(d["kind"], d, tone, "day", variant)
    return runs


class Finished(unittest.TestCase):
    """A finished game keeps its final board up for two days, as every game on the profile does: the final position,
    the winner and how on the turn's plate, the day the fresh board comes across the row, and nothing to play. A board
    under way is drawn exactly as it was before a board could finish."""

    def test_every_file_of_a_finished_board_is_drawn_in_every_theme(self):
        for d in FINISHED:
            self.assertEqual(C.check(d), [], d["fen"])
            for tone in TONES:
                for variant in E.variants("chess", d):
                    for theme in ("day", "dark"):
                        svg = E.draw("chess", d, tone, theme, variant)    # the kit's lint and budget, or it raises
                        with self.subTest(game=d["game"], tone=tone, variant=variant, theme=theme):
                            self.assertEqual(svg, E.draw("chess", d, tone, theme, variant))
                            self.assertNotIn("<text", svg)
                            (self.assertNotIn if variant.endswith("still") else self.assertIn)("<animate", svg)

    def test_its_plate_says_who_won_and_how_and_when_the_fresh_board_comes(self):
        for d, label, how, day in ((SCHOLAR, "@TANNERGOLDEN WINS", "CHECKMATE", "14 OCT"),
                                   (FOOL, "GITHUB WINS", "CHECKMATE", "13 OCT"),
                                   (STALEMATE, "DRAWN", "STALEMATE", "12 OCT")):
            for tone in (STANDARD, "blackprint", "yellowprint"):
                for variant in ("still", "narrow-still"):
                    runs = lettered(d, tone, variant)
                    with self.subTest(game=d["game"], tone=tone, variant=variant):
                        self.assertIn(label, runs)
                        self.assertIn(how, runs)
                        self.assertIn(f"NEXT GAME {day}", runs)
                        self.assertFalse([r for r in runs if r.endswith("'S TURN")], "it is nobody's turn")
        self.assertIn("@TANNERGOLDEN WINS", lettered(SCHOLAR, STANDARD)[-6:], "where the next move would stand")

    def test_its_description_and_readme_say_how_it_ended_and_offer_nothing_to_play(self):
        self.assertIn("after 4. Qxf7#: queen from h5 takes the pawn on f7, checkmate. @tannergolden won: checkmate."
                      " Game 14 opens 14 Oct.", E.alt("chess", SCHOLAR))
        self.assertIn("GitHub won: checkmate. Game 13 opens 13 Oct.", E.alt("chess", FOOL))
        self.assertIn("The game was drawn: stalemate. Game 12 opens 12 Oct.", E.alt("chess", STALEMATE))
        # the note says what the picture cannot, as the engine writes it on a finished board: a link in it is a link
        over = ("Game 12 is over, and its final board stays up for two days: game 13 opens 14 Oct, 16:00 EST, and "
                "nothing can be played until then. Every finished game is kept as a "
                "[PGN](https://github.com/tannergolden/tannergolden/tree/HEAD/.github/chess/games).")
        for d in (*FINISHED, {**FOOL, "note": over}):
            text = ED.block("chess", d, "assets/elements")
            with self.subTest(game=d["game"], note=bool(d.get("note"))):
                self.assertEqual(C.check(d), [])
                self.assertTrue(text.startswith(f"<!-- markdown:element:chess:start -->\n> [!IMPORTANT]\n> "
                                                f"{d['prompt']}\n\n<details open>\n<summary><b>♟️ Chess</b>"
                                                "</summary>\n\n<picture>"))
                self.assertEqual(text.count("<details"), 1, "the game's own fold, and no move in it")
                under = f"\n\n{d['note']}" if d.get("note") else ""
                self.assertTrue(text.endswith(f"</picture>{under}\n\n</details>\n<!-- markdown:element:chess:end -->"),
                                "its banner, its board and its note, with no move to play")

    def test_how_it_ended_is_checked_as_strictly_as_the_rest_of_the_board(self):
        def turned_away(d: dict, said: str):
            errors = C.check(d)
            self.assertTrue(any(said in e for e in errors), f"{said!r} not in {errors}")

        for how in ("checkmate", "stalemate", "insufficient material", "fivefold repetition", "seventy-five moves",
                    "dead position"):
            winner = "house" if how == "checkmate" else None
            with self.subTest(how=how):
                self.assertEqual(C.check({**(SCHOLAR if winner else STALEMATE), "result": {"winner": winner,
                                                                                          "how": how}}), [])
        for bad in ({"winner": "house"}, {"winner": "white", "how": "checkmate"}, {"winner": None, "how": "resigned"},
                    {"winner": None, "how": "threefold repetition"}, "checkmate", ["house", "checkmate"], True,
                    {"winner": "house", "how": "checkmate", "by": "mate"}, {"winner": None, "how": 7}):
            with self.subTest(result=bad):
                turned_away({**SCHOLAR, "result": bad}, "result is how the game ended")
        turned_away({**SCHOLAR, "result": {"winner": None, "how": "checkmate"}},
                    "a game ended by checkmate has a winner")
        turned_away({**STALEMATE, "result": {"winner": "house", "how": "stalemate"}}, "is drawn, its winner null")
        turned_away({**SCHOLAR, "result": {"winner": "github", "how": "checkmate"}},
                    "the winner is the side that made the last move, house")
        turned_away({**FOOL, "result": {"winner": "house", "how": "checkmate"}},
                    "the winner is the side that made the last move, github")
        turned_away({**SCHOLAR, "moves": GAME["moves"]}, "a finished board offers no move")
        self.assertEqual(C.check({**SCHOLAR, "moves": []}), [])
        for day in ("32 Oct", "14 Octo", 14, True):
            with self.subTest(next=day):
                turned_away({**SCHOLAR, "next": day}, f"next {day!r} is not a day")
        turned_away({**GAME, "next": "14 Oct"}, "a game under way has none")

    def test_a_board_under_way_is_drawn_exactly_as_before_whatever_says_it_is_not_finished(self):
        for d in (GAME, HOUSE, OPENING):
            for tone in (STANDARD, "blackprint"):
                for variant in ("wide", "narrow-still"):
                    plain = E.draw("chess", d, tone, "dark", variant)
                    with self.subTest(fen=d["fen"], tone=tone, variant=variant):
                        self.assertEqual(E.draw("chess", {**d, "result": None, "next": ""}, tone, "dark", variant),
                                         plain)


class Sets(unittest.TestCase):
    def test_a_holiday_or_collection_leaves_both_in_the_pages_own_theme(self):
        elements = ED.merged({"chess": dict(GAME), "chess-hall": dict(HALL)}, {}, subject="tannergolden")
        printed = ED.render(elements, "blackprint")
        self.assertEqual(ED.render(elements, "blackprint", "halloween"), printed)
        standard = ED.render(elements, STANDARD)
        self.assertEqual(sorted(standard), sorted(printed))
        self.assertNotEqual(standard["chess-day.svg"], printed["chess-day.svg"], "the standard theme has its own skin")
        for svg in standard.values():
            self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])


def account(uid: int, login: str, name=None) -> dict:
    """GitHub's answer to /user/{id}: the account as it is now."""
    return {"login": login, "id": uid, "type": "User", "name": name}


class Measured(unittest.TestCase):
    def test_a_winners_name_is_read_from_their_profile_when_the_sheet_can_letter_it(self):
        gh = FakeGitHub({}, users={"imvale": {"name": "Imogen  Vale"}, "tokafor": {"name": "Tomás <O>"},
                                   "jhalloran": {"name": None}})
        self.assertEqual(measure.winners(gh, HALL["people"]), {"names": {"imvale": "Imogen Vale"}})
        self.assertNotIn("/users/tannergolden", [path for path, _ in gh.asked], "the house is never looked up")
        section = {"chess-hall": {**HALL, "names": {}, "measure": {}}}
        out = measure.measure(section, {}, git=None, gh=gh, subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"chess-hall": {"names": {"imvale": "Imogen Vale"}}})
        self.assertFalse([path for path, _ in gh.asked if path.startswith("/user/")], "a row without an ID")

    def test_a_row_with_its_accounts_id_is_read_by_the_id_so_a_login_that_changed_hands_is_never_credited(self):
        # @imvale renamed to @imogen-vale, and someone else took the login @imvale; @tokafor deleted their account;
        # @wrencastellan kept theirs; @jhalloran's row carries no ID; @octocat is on the leaderboard alone.
        paths = {"/user/1001": account(1001, "imogen-vale", "Imogen Vale"),
                 "/user/1003": account(1003, "wrencastellan"), "/user/1004": account(1004, "jhalloran", "Jo Halloran"),
                 "/user/583231": account(583231, "octocat", "The Octocat")}
        users = {"imvale": {"login": "imvale", "name": "Mallory Mallet"},
                 "tokafor": {"login": "tokafor", "name": "Eve"},
                 "jhalloran": {"login": "jhalloran", "name": "Jo Halloran"}}
        gh = FakeGitHub({}, users=users, paths=paths)
        people = [*KNOWN["people"][:4], HALL["people"][4]]
        measured = measure.winners(gh, people, KNOWN["leaders"])
        self.assertEqual(measured, {"names": {"imogen-vale": "Imogen Vale", "jhalloran": "Jo Halloran"},
                                    "logins": {"1001": "imogen-vale", "1002": "", "1003": "wrencastellan",
                                               "1004": "jhalloran", "583231": "octocat"}})
        asked = [path for path, _ in gh.asked]
        self.assertEqual(sorted(asked), ["/user/1001", "/user/1002", "/user/1003", "/user/1004", "/user/583231",
                                         "/users/jhalloran"], "each ID read once, the house never, a login only "
                                                              "for the row without an ID")
        d = dict(KNOWN, people=people, **measured)
        self.assertEqual(C.check_hall(d), [])
        drawn = [(p["name"], p["badge"]) for p in C.hall_state(d)["people"]]
        self.assertEqual(drawn, [("@TANNERGOLDEN", "@tannergolden"), ("IMOGEN VALE", "@imogen-vale"),
                                 ("@WRENCASTELLAN", "@wrencastellan"), ("JO HALLORAN", "@jhalloran")])
        text = ED.block("chess-hall", d, "assets/elements")
        self.assertNotIn("MALLORY", " ".join(p["name"] for p in C.hall_state(d)["people"]))
        for gone in ("github.com/imvale", "github.com/tokafor"):
            self.assertNotIn(gone, text)
        section = {"chess-hall": {**{k: v for k, v in d.items() if k not in measured}, "measure": {}}}
        out = measure.measure(section, {}, git=None, gh=gh, subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"chess-hall": measured}, "the run keeps the logins beside the names")
        self.assertEqual(ED.validate(section, out, subject="tannergolden"), [])
        merged = ED.merged(section, out, subject="tannergolden")["chess-hall"]
        self.assertEqual(merged["logins"]["1001"], "imogen-vale")

    def test_only_github_s_404_takes_a_player_off_and_a_bad_minute_keeps_the_last_reading(self):
        # GitHub refuses /user/1001 (a 403) and fails on /user/1002 past every retry; /user/1003 is a 404, a deleted
        # account; /user/1004 answers.
        def fault(**params):
            raise ApiError("GitHub answered 502 for /user/1002: ")

        paths = {"/user/1001": None, "/user/1002": fault, "/user/1004": account(1004, "jhalloran", "Jo Halloran"),
                 "/user/583231": account(583231, "octocat")}
        gh = FakeGitHub({}, paths=paths)
        before = {"names": {"imogen-vale": "Imogen Vale", "tokafor": "Tomas Okafor"},
                  "logins": {"1001": "imogen-vale", "1002": "", "1003": "wrencastellan"}}
        measured = measure.winners(gh, KNOWN["people"], KNOWN["leaders"], before)
        self.assertEqual(measured, {"names": {"imogen-vale": "Imogen Vale", "jhalloran": "Jo Halloran"},
                                    "logins": {"1001": "imogen-vale", "1002": "", "1003": "", "1004": "jhalloran",
                                               "583231": "octocat"}},
                         "a refusal and a fault keep the last reading, a gone account staying gone; a 404 is gone")
        self.assertEqual([p["login"] for p in C.hall_state(dict(KNOWN, **measured))["people"]],
                         ["tannergolden", "imogen-vale", "jhalloran"])
        first = measure.winners(FakeGitHub({}, paths=paths), KNOWN["people"], KNOWN["leaders"])
        self.assertEqual(first["logins"], {"1003": "", "1004": "jhalloran", "583231": "octocat"},
                         "with no reading before, an account GitHub didn't answer for is shown as its row has it")
        self.assertEqual([p["login"] for p in C.hall_state(dict(KNOWN, **first))["people"]],
                         ["tannergolden", "imvale", "tokafor", "jhalloran"])
        section = {"chess-hall": {**KNOWN, "measure": {}}}
        out = measure.measure(section, {"chess-hall": before}, git=None, gh=FakeGitHub({}, paths=paths),
                              subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"chess-hall": measured}, "the run hands the last reading on")

    def test_a_name_that_poses_as_a_handle_or_that_no_tone_can_letter_is_left_for_the_login(self):
        names = {"imvale": "@tannergolden", "tokafor": "Иван Петров", "wrencastellan": "山田太郎",
                 "jhalloran": "Ελένη Παππά"}
        gh = FakeGitHub({}, users={login: {"name": name} for login, name in names.items()})
        self.assertEqual(measure.winners(gh, HALL["people"]), {"names": {}})
        for name in ("مريم", "김민준", "Tanner 🚀", "ß" * 21, "\u200b"):
            with self.subTest(name=name):
                gh = FakeGitHub({}, users={"imvale": {"name": name}})
                self.assertEqual(measure.winners(gh, HALL["people"]), {"names": {}})
        kept = {"imvale": "Tomás Ørsted", "tokafor": "Łukasz Żółć", "wrencastellan": "Zoë O'Brien-Ångström",
                "jhalloran": "Đorđe Šćekić"}
        gh = FakeGitHub({}, users={login: {"name": name} for login, name in kept.items()})
        self.assertEqual(measure.winners(gh, HALL["people"]), {"names": kept})
        d = dict(HALL, names=kept)
        for tone in TONES:
            with self.subTest(tone=tone):
                E.WARNINGS.clear()
                for variant in ("wide", "narrow"):
                    E.draw("chess-hall", d, tone, "day", variant)
                self.assertEqual(E.WARNINGS, [], "every name the run keeps is lettered as it is, in every tone")
        E.WARNINGS.clear()
        E.draw("chess-hall", dict(HALL, names={"imvale": "Иван Петров"}), STANDARD, "day", "wide")
        self.assertTrue(E.WARNINGS, "a name the run leaves out would be drawn as question marks")
        E.WARNINGS.clear()


if __name__ == "__main__":
    unittest.main()
