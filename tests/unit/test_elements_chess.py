# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess element: the game on @tannergolden's profile, in every variant, theme and print, and nowhere else.

The position is the one after 1. e4 e5 2. Nf3 Nc6 3. Bc4 Nb4 4. Nxe5 Qg5 5. Bxf7+: Black to move and in check,
with two of Black's pawns taken, so every mark the board can carry is on it at once."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom

from tests import support

from domain.canvas import BUDGET, lint
from domain.elements import chess as C
from domain.elements import data as ED
from domain.elements import draw as E
from domain.prints import PRINTS

support.install()
DASHES = ("–", "—", "―")
LINK = "https://github.com/tannergolden/play/issues/new?template=move.yml&title=chess%3A%20g5g2%20%C2%B7%20game%203%20%C2%B7%20move%2010"
GAME = {
    "kind": "chess", "fen": "r1b1kbnr/pppp1Bpp/8/4N1q1/1n2P3/8/PPPP1PPP/RNBQK2R b KQkq - 0 5",
    "game": 3, "move": 10, "white": "tannergolden", "black": "GitHub",
    "last": "c4f7", "last_san": "5. Bxf7+", "last_by": "tannergolden", "check": "e8",
    "turn_note": "Anyone but tannergolden can play",
    "history": [["1", "e4", "e5"], ["2", "Nf3", "Nc6"], ["3", "Bc4", "Nb4"], ["4", "Nxe5", "Qg5"], ["5", "Bxf7+", ""]],
    "hall": [["1", "0-1", "@octocat", "Qh4#"], ["2", "1-0", "tannergolden", "Qxf7#"]],
    "prompt": "**GitHub's move.** Anyone but @tannergolden can play.",
    "moves": [{"piece": "king", "links": [["Kxf7", LINK]]}, {"piece": "queen", "links": [["Qxg2", LINK], ["Qe7", LINK]]}],
    "note": "The first move to arrive is the one played.",
}


def fills(svg: str) -> dict[str, str]:
    """Each piece's fill as drawn into the defs: {id: colour}."""
    return dict(re.findall(r'<g id="(kpc[^"]*)" transform="scale\([^)]*\)"><path d="[^"]*" fill="(#[0-9A-Fa-f]{6})"', svg))


class EveryFile(unittest.TestCase):
    def test_every_variant_theme_and_print_is_well_formed_within_budget_and_deterministic(self):
        for tone in sorted(PRINTS):
            for variant in E.variants("chess", GAME):
                for theme in ("day", "dark"):
                    svg = E.draw("chess", GAME, tone, theme, variant)
                    with self.subTest(tone=tone, variant=variant, theme=theme):
                        minidom.parseString(svg)
                        self.assertEqual(svg, E.draw("chess", GAME, tone, theme, variant))
                        self.assertNotIn("<text", svg)
                        self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])
                        for ch in DASHES:
                            self.assertNotIn(ch, svg)

    def test_a_board_with_nothing_but_its_position_is_drawn(self):
        bare = {"kind": "chess", "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}
        for variant in ("wide", "narrow"):
            self.assertEqual(lint(E.draw("chess", bare, "blackprint", "day", variant), budget=BUDGET["sheet"]), [])


class Board(unittest.TestCase):
    def test_whites_pieces_are_the_lighter_in_either_theme(self):
        day, dark = (E.draw("chess", GAME, "blackprint", theme, "wide") for theme in ("day", "dark"))
        for svg in (day, dark):
            colours = set(fills(svg).values())
            self.assertEqual(len(colours), 2, "one fill for White's pieces and one for Black's")
        # By day the paper is white, so White's pieces are paper; by night the line is, so they are line.
        self.assertIn("#FFFFFF", {colour.upper() for colour in fills(day).values()})
        self.assertIn("#FFFFFF", {colour.upper() for colour in fills(dark).values()})

    def test_every_piece_on_the_board_is_placed_once(self):
        svg = E.draw("chess", GAME, "blackprint", "day", "narrow")
        uses = re.findall(r'<use href="#(kpc[^"]*)" x=', svg)
        self.assertEqual(len(uses), len(C.placement(GAME["fen"])))

    def test_the_wide_sheet_adds_the_captured_pieces_small(self):
        svg = E.draw("chess", GAME, "blackprint", "day", "wide")
        uses = re.findall(r'<use href="#(kpc[^"]*)" x=', svg)
        self.assertEqual(len(uses), len(C.placement(GAME["fen"])) + 2)

    def test_the_last_move_and_the_check_are_marked(self):
        svg = E.draw("chess", GAME, "blackprint", "day", "wide")
        self.assertEqual(svg.count('stroke-dasharray="2.4 2.2"'), 1, "the square the move left")
        self.assertIn('stroke-dasharray="1.6 2.6"', svg, "the line between its squares")
        rings = re.compile(r'<circle [^>]*fill="none"')  # a knight's eye is a circle too, and filled
        self.assertEqual(len(rings.findall(svg)), 2, "the ring round the king in check, and its echo")
        quiet = {k: v for k, v in GAME.items() if k not in ("last", "check")}
        svg = E.draw("chess", quiet, "blackprint", "day", "wide")
        self.assertNotIn("stroke-dasharray", svg)
        self.assertEqual(rings.findall(svg), [])

    def test_the_pieces_taken_are_counted_from_the_position(self):
        self.assertEqual(C.captured(GAME["fen"]), ("pp", ""))
        self.assertEqual(C.captured("4k3/8/8/8/8/8/8/4K3 w - - 0 1"), ("qrrbbnnpppppppp", "QRRBBNNPPPPPPPP"))

    def test_its_title_and_description_say_who_plays_and_whose_turn_it_is(self):
        alt = E.alt("chess", GAME)
        self.assertIn("Chess: tannergolden vs. GitHub", alt)
        self.assertIn("Game 3, move 10. Black to move: GitHub. The last move was 5. Bxf7+.", alt)


class Settings(unittest.TestCase):
    def test_it_is_drawn_on_tannergoldens_profile_alone(self):
        section = {"chess": dict(GAME)}
        self.assertEqual(ED.validate(section, {}, subject="tannergolden"), [])
        self.assertEqual(ED.validate(section, {}, subject="TannerGolden"), [])
        for elsewhere in ("octocat", "tannergolden/markdown", ""):
            with self.subTest(subject=elsewhere):
                self.assertIn("chess: the chess element is drawn on @tannergolden's profile alone",
                              ED.validate(section, {}, subject=elsewhere))

    def test_what_it_is_drawn_from_is_checked(self):
        cases = {
            "fen": ("8/8/8/8/8/8/8/8 w - - 0 1", "does not have one king a side"),
            "last": ("e2", "is not a move in UCI"),
            "check": ("e9", "is not a square"),
            "prompt": ("<b>move</b>", "one line of text"),
            "note": ("a | b", "one line of text"),
            "moves": ([{"piece": "pawn", "links": [["e4", "https://example.com/x"]]}], "is not a move in SAN and the link"),
        }
        for key, (bad, said) in cases.items():
            with self.subTest(key=key):
                errors = " ".join(ED.validate({"chess": {**GAME, key: bad}}, {}, subject="tannergolden"))
                self.assertIn(said, errors)
        self.assertIn("a chess needs fen", " ".join(ED.validate({"chess": {"kind": "chess"}}, {}, subject="tannergolden")))

    def test_the_readme_carries_every_move_as_a_link_under_the_picture(self):
        text = ED.block("chess", GAME, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:chess:start -->\n<picture>"))
        self.assertIn("</picture>\n\n**GitHub's move.** Anyone but @tannergolden can play.\n\n| Piece | Moves |\n", text)
        self.assertIn(f"| King | [Kxf7]({LINK}) |\n| Queen | [Qxg2]({LINK}) · [Qe7]({LINK}) |", text)
        self.assertTrue(text.endswith("The first move to arrive is the one played.\n<!-- markdown:element:chess:end -->"))
        self.assertNotIn("| Piece", ED.block("placard", {"kind": "placard", "owner": "o", "name": "n", "desc": "d",
                                                         "cells": [["A", "1"]]}, "assets/elements"))


class Sets(unittest.TestCase):
    def test_a_holiday_or_the_standard_theme_leaves_the_board_in_the_pages_print(self):
        elements = ED.merged({"chess": dict(GAME)}, {}, subject="tannergolden")
        printed = ED.render(elements, "blackprint")
        self.assertEqual(ED.render(elements, "blackprint", "halloween"), printed)
        standard = ED.render(elements, "standard")
        self.assertEqual(sorted(standard), sorted(printed))
        for svg in standard.values():
            self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])


if __name__ == "__main__":
    unittest.main()
