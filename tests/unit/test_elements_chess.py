# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess elements: the game on @tannergolden's profile and its Hall of Fame, in every theme, and nowhere else.

The game is the Max Lange Attack the design was drawn from, game 13 after 21. Nd6+: GitHub to move and in check,
the knight just landed with check, a few pieces taken each side. The house's turn is the same game after
21... cxd6, and the opening board is game 1 before anyone has moved. The Hall of Fame is that series after twelve
games, five winners ranked; an empty one has had no game finish yet."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom

from tests import support
from tests.fakes.github import FakeGitHub

from app.parts import elements as measure
from domain.canvas import BUDGET, lint
from domain.elements import chess as C
from domain.elements import data as ED
from domain.elements import draw as E
from domain.prints import PRINTS, STANDARD

support.install()
DASHES = ("–", "—", "―")
LINK = ("https://github.com/tannergolden/play/issues/new?template=move.yml&title=chess%3A%20c7d6%20%C2%B7%20game%2013"
        "%20%C2%B7%20move%2042")
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
        "names": {"imvale": "Imogen Vale", "tokafor": "Tomas Okafor"}}
EMPTY = {"kind": "chess-hall", "games": 0, "house": 0, "world": 0, "draws": 0, "people": []}
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
                            self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])
                            for ch in DASHES:
                                self.assertNotIn(ch, svg)

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
                    self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [], (d["kind"], tone, variant))


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

    def test_each_winner_has_a_badge_and_the_leaders_has_a_still_twin(self):
        self.assertEqual(E.variants("chess-hall", HALL), ("wide", "narrow", "still", "narrow-still", "badge-1",
                                                          "badge-1-still", "badge-2", "badge-3", "badge-4", "badge-5"))
        self.assertEqual(E.variants("chess-hall", EMPTY), ("wide", "narrow", "still", "narrow-still"))


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
            "check": ("e9", "is not a square"),
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

    def test_what_the_hall_is_drawn_from_is_checked(self):
        cases = {
            "games": (11, "add up to 12 games, not the 11 played"),
            "people": ([["not a login!", 1, "2 Oct", 1]], "people:"),
            "names": ({"imvale": "<script>"}, "names gives a login its name"),
        }
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                self.assertIn(said, " ".join(ED.validate({"h": {**HALL, key: bad}}, {}, subject="tannergolden")))
        six = HALL["people"] + [["octocat", 1, "1 Oct", 1]]
        self.assertIn("at most 5 winners", " ".join(ED.validate({"h": {**HALL, "people": six}}, {},
                                                                subject="tannergolden")))


class Readme(unittest.TestCase):
    def test_the_board_has_its_turns_banner_above_and_every_move_folded_under(self):
        text = ED.block("chess", GAME, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:chess:start -->\n> [!TIP]\n> 🟢 **GitHub's turn!**"))
        self.assertIn("by 18 Oct.\n\n<picture>", text)
        self.assertIn("</picture>\n\n<details>\n<summary>♚ <b>GitHub's moves</b> · 4 legal moves · open to choose one"
                      "</summary>\n\n|  | Move | What it does | Play |\n| :-: | :--- | :--- | :-: |\n", text)
        self.assertIn(f"| 🏰 | **The Royal Retreat** `Kb8` | King from c8 to b8 | [Play ↗]({LINK}) |", text)
        self.assertTrue(text.endswith("</details>\n\nThe first move to arrive is the one played.\n"
                                      "<!-- markdown:element:chess:end -->"))

    def test_the_houses_turn_is_a_caution_and_its_moves_are_the_houses_alone(self):
        text = ED.block("chess", HOUSE, "assets/elements")
        self.assertIn("> [!CAUTION]\n> 🛑 **@tannergolden's turn!**", text)
        self.assertIn("♔ <b>@tannergolden's moves</b> · 4 legal moves · only @tannergolden can play these", text)

    def test_a_busy_turn_is_grouped_by_piece(self):
        many = [{"piece": "knight", "list": [["🐴", f"Ride {i}", "Nf3", "Knight from g1 to f3", LINK] for i in range(7)]},
                {"piece": "pawn", "list": [["🥾", f"March {i}", "e4", "Pawn from e2 to e4", LINK] for i in range(5)]}]
        text = ED.block("chess", {**GAME, "moves": many}, "assets/elements")
        self.assertIn("· 12 legal moves ·", text)
        self.assertIn("<details open>\n<summary>♞ Knights · 7 moves</summary>\n\n|  | Move |", text)
        self.assertIn("<summary>♟ Pawns · 5 moves</summary>", text)

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


class Measured(unittest.TestCase):
    def test_a_winners_name_is_read_from_their_profile_when_the_sheet_can_letter_it(self):
        gh = FakeGitHub({}, users={"imvale": {"name": "Imogen  Vale"}, "tokafor": {"name": "Tomás <O>"},
                                   "jhalloran": {"name": None}})
        self.assertEqual(measure.winners(gh, HALL["people"]), {"imvale": "Imogen Vale"})
        self.assertNotIn("/users/tannergolden", [path for path, _ in gh.asked], "the house is never looked up")
        section = {"chess-hall": {**HALL, "names": {}, "measure": {}}}
        out = measure.measure(section, {}, git=None, gh=gh, subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"chess-hall": {"names": {"imvale": "Imogen Vale"}}})


if __name__ == "__main__":
    unittest.main()
