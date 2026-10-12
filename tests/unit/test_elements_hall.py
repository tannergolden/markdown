# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hall of Fame of all four games on @tannergolden's profile, in every theme, and nowhere else.

The Hall is the series after 29 games: twelve of Chess, five of Checkers, three of Connect Four and nine of
Tic-Tac-Toe, five winners ranked across all four, and six players on the leaderboard. An empty one has had no game
finish yet, and a known one is the same Hall with each row's account ID, by which a run reads the login every player
has now. The element the profile's engines write, word for word as the build's contract gives it, is read by the
kit's own YAML reader and checked as a run checks it. Its data lists each player's wins in tier order, Tic-Tac-Toe
first; everything a reader sees lists the games Chess first."""
from __future__ import annotations

import unittest
import xml.dom.minidom as minidom

from tests import support
from tests.fakes.github import FakeGitHub

from app.parts import elements as measure
from infra import yaml_reader
from infra.github import ApiError
from domain.canvas import BUDGET, lint
from domain.elements import chess as C
from domain.elements import data as ED
from domain.elements import draw as E
from domain.elements import hall as H
from domain.elements.hall import readme as RM
from domain.prints import PRINTS, STANDARD

support.install()
DASHES = ("–", "—", "―")
SERIES = {"tictactoe": [9, 4, 2, 3], "connectfour": [3, 1, 2, 0], "checkers": [5, 2, 2, 1], "chess": [12, 5, 6, 1]}
HALL = {"kind": "hall-of-fame", "series": SERIES,
        "people": [["tannergolden", [4, 1, 2, 5], "2 Oct", 29], ["imvale", [1, 1, 0, 2], "19 Sep", 7],
                   ["tokafor", [0, 1, 1, 1], "27 Sep", 9], ["wrencastellan", [1, 0, 1, 0], "4 Sep", 6],
                   ["jhalloran", [0, 0, 0, 1], "8 Oct", 3]],
        "names": {"imvale": "Imogen Vale", "tokafor": "Tomas Okafor"},
        "leaders": [["tannergolden", 1240, 29, [4, 1, 2, 5]], ["imvale", 40, 7, [1, 1, 0, 2]],
                    ["tokafor", 31, 9, [0, 1, 1, 1]], ["wrencastellan", 52, 6, [1, 0, 1, 0]],
                    ["jhalloran", 12, 3, [0, 0, 0, 1]], ["octocat", 9, 2, [0, 0, 0, 0]]]}
NONE = {g: [0, 0, 0, 0] for g in H.GAMES}
EMPTY = {"kind": "hall-of-fame", "series": NONE, "people": [], "leaders": [["tannergolden", 0, 0, [0, 0, 0, 0]]]}
# The same series as HALL, every row carrying its account's ID, the house's included.
IDS = {"tannergolden": 24684994, "imvale": 1001, "tokafor": 1002, "wrencastellan": 1003, "jhalloran": 1004,
       "octocat": 583231}
KNOWN = dict(HALL, people=[[*row, IDS[row[0]]] for row in HALL["people"]],
             leaders=[[*row, IDS[row[0]]] for row in HALL["leaders"]])
# The element as the build's contract writes it, word for word, as the profile's engines write it into the settings.
WRITTEN = """elements:
  hall-of-fame:
    kind: "hall-of-fame"
    series: {"tictactoe": [9, 4, 2, 3], "connectfour": [3, 1, 2, 0], "checkers": [5, 2, 2, 1], "chess": [12, 5, 6, 1]}
    people:
      - ["tannergolden", [4, 1, 2, 5], "2 Oct", 29, 24684994]
      - ["imvale", [0, 1, 0, 2], "19 Sep", 7, 1001]
    leaders:
      - ["tannergolden", 1240, 29, [4, 1, 2, 5], 24684994]
      - ["imvale", 40, 7, [0, 1, 0, 2], 1001]
    measure: {}
"""
# The densest Hall the checks accept: ten winners and twenty of GitHub's players, sent for five places and ten,
# every login of 39 letters and every name of 40, every count at its ceiling of 999,999 and every move count at
# 999,999,999.
W39 = ["W" * 39] + ["W" * (39 - len(str(i))) + str(i) for i in range(1, 20)]
DENSE = {"kind": "hall-of-fame", "series": {g: [999_999, 333_333, 333_333, 333_333] for g in H.GAMES},
         "people": [[w, [999_999 - i] * 4, "28 May", 999_999, 10_000 + i] for i, w in enumerate(W39[:10])],
         "names": {w: "W" * 40 for w in W39[:10]},
         "leaders": [["tannergolden", 999_999_999, 999_999, [249_999] * 4, 24684994]]
         + [[w, 999_999_999 - i, 999_999, [249_999 - i] * 4, 20_000 + i] for i, w in enumerate(W39)]}
TONES = (STANDARD, *sorted(PRINTS))


class EveryFile(unittest.TestCase):
    def test_every_file_in_every_theme_is_well_formed_within_budget_and_deterministic(self):
        for d in (HALL, KNOWN):
            for tone in TONES:
                for variant in E.variants("hall-of-fame", d):
                    for theme in ("day", "dark"):
                        svg = E.draw("hall-of-fame", d, tone, theme, variant)  # the kit's lint and budget, or it raises
                        with self.subTest(tone=tone, variant=variant, theme=theme):
                            minidom.parseString(svg)
                            self.assertEqual(svg, E.draw("hall-of-fame", d, tone, theme, variant))
                            self.assertNotIn("<text", svg)
                            self.assertEqual(lint(svg, budget=BUDGET[E.KINDS["hall-of-fame"][2]]), [])
                            for ch in DASHES:
                                self.assertNotIn(ch, svg)

    def test_it_is_drawn_to_the_boards_budget(self):
        self.assertEqual(E.KINDS["hall-of-fame"][1:], (("wide", "narrow", "still", "narrow-still"), "board"))

    def test_the_densest_hall_the_contract_accepts_is_drawn_with_room_to_spare(self):
        # A file over budget fails the whole run, and every game's page stays a move behind, so the densest Hall the
        # data allows keeps clear of its budget in every tone and every file.
        self.assertEqual(H.check(DENSE), [])
        for tone in TONES:
            for variant in E.variants("hall-of-fame", DENSE):
                for theme in ("day", "dark"):
                    with self.subTest(tone=tone, variant=variant, theme=theme):
                        svg = E.draw("hall-of-fame", DENSE, tone, theme, variant)
                        self.assertLess(len(svg.encode()), BUDGET["board"] * 0.97)

    def test_the_still_files_stand_still_and_the_rest_move(self):
        for variant in E.variants("hall-of-fame", HALL):
            svg = E.draw("hall-of-fame", HALL, "blackprint", "day", variant)
            with self.subTest(variant=variant):
                if variant.endswith("still") or variant.startswith("badge-") and variant != "badge-1":
                    self.assertNotIn("<animate", svg)
                else:
                    self.assertIn("<animate", svg)

    def test_a_hall_before_its_first_winner_and_with_its_first_are_drawn(self):
        first = dict(EMPTY, series=dict(NONE, tictactoe=[1, 1, 0, 0]),
                     people=[["tannergolden", [1, 0, 0, 0], "12 Oct", 1]],
                     leaders=[["tannergolden", 3, 1, [1, 0, 0, 0]], ["octocat", 2, 1, [0, 0, 0, 0]]])
        for d in (EMPTY, first, {"kind": "hall-of-fame"}):
            self.assertEqual(H.check(d), [])
            for tone in (STANDARD, "blackprint"):
                for variant in E.variants("hall-of-fame", d):
                    for theme in ("day", "dark"):
                        svg = E.draw("hall-of-fame", d, tone, theme, variant)
                        self.assertEqual(lint(svg, budget=BUDGET["board"]), [], (tone, variant, theme))


class Hall(unittest.TestCase):
    def test_it_says_the_series_of_every_game_and_ranks_the_winners_with_their_wins_in_each_chess_first(self):
        alt = E.alt("hall-of-fame", HALL)
        self.assertTrue(alt.startswith("Hall of Fame: four games. 29 games of @tannergolden against GitHub, across "
                                       "Chess, Checkers, Connect Four and Tic-Tac-Toe: @tannergolden won 12, GitHub "
                                       "12, and 5 were drawn."), alt)
        self.assertIn(" Chess: 12 games, @tannergolden 5, GitHub 6, 1 drawn. Checkers: 5 games, @tannergolden 2,"
                      " GitHub 2, 1 drawn. Connect Four: 3 games, @tannergolden 1, GitHub 2, 0 drawn. Tic-Tac-Toe: 9"
                      " games, @tannergolden 4, GitHub 2, 3 drawn.", alt)
        self.assertIn("Ranked by wins: @tannergolden with 12 wins (5 in Chess, 2 in Checkers, 1 in Connect Four and 4"
                      " in Tic-Tac-Toe), @imvale with 4 wins (2 in Chess, 1 in Connect Four and 1 in Tic-Tac-Toe),",
                      alt)
        self.assertTrue(alt.endswith("@jhalloran with 1 win (1 in Chess)."), alt)
        self.assertEqual(E.alt("hall-of-fame", EMPTY), "Hall of Fame: four games. No game of @tannergolden against"
                         " GitHub has finished yet, in Chess, Checkers, Connect Four or Tic-Tac-Toe, so the podium"
                         " waits for its first winner.")
        one = E.alt("hall-of-fame", dict(EMPTY, series=dict(NONE, tictactoe=[1, 0, 1, 0])))
        self.assertIn("1 game of @tannergolden against GitHub", one)
        self.assertIn("none were drawn. Chess: none finished yet. Checkers: none finished yet. Connect Four: none"
                      " finished yet. Tic-Tac-Toe: 1 game, @tannergolden 0, GitHub 1, 0 drawn.", one)
        self.assertEqual(H.ORDER, ("chess", "checkers", "connectfour", "tictactoe"))
        self.assertEqual(H.GAMES, ("tictactoe", "connectfour", "checkers", "chess"), "the data keeps tier order")

    def test_the_series_counts_each_game_and_all_four_together(self):
        h = H.state(HALL)
        self.assertEqual(h["series"]["checkers"], {"games": 5, "house": 2, "github": 2, "draws": 1})
        self.assertEqual(h["totals"], {"games": 29, "house": 12, "github": 12, "draws": 5})
        self.assertEqual(H.state({"kind": "hall-of-fame"})["totals"], {"games": 0, "house": 0, "github": 0, "draws": 0},
                         "without a series, no game has finished yet")

    def test_a_winner_is_named_by_their_profile_else_by_their_login_and_the_owner_is_the_house(self):
        people = H.state(HALL)["people"]
        self.assertEqual([(p["name"], p["initials"], p["house"], p["wins"]) for p in people[:4]],
                         [("@TANNERGOLDEN", "TA", True, 12), ("IMOGEN VALE", "IV", False, 4),
                          ("TOMAS OKAFOR", "TO", False, 3), ("@WRENCASTELLAN", "WR", False, 2)])
        self.assertEqual([p["handle"] for p in people[:4]],
                         ["the house", "@imvale", "@tokafor", "github  ·  challenger"])
        self.assertEqual(people[1]["by_game"], {"tictactoe": 1, "connectfour": 1, "checkers": 0, "chess": 2},
                         "the wins in each game, read from the data's tier order")
        leaders = H.state(HALL)["leaders"]
        self.assertEqual([(r["login"], r["moves"], r["games"], r["wins"], r["house"]) for r in leaders[:2]],
                         [("tannergolden", 1240, 29, 12, True), ("imvale", 40, 7, 4, False)])
        self.assertEqual(leaders[0]["by_game"], {"tictactoe": 4, "connectfour": 1, "checkers": 2, "chess": 5})

    def test_a_player_is_shown_by_the_login_their_account_has_now_and_one_whose_account_is_gone_not_at_all(self):
        # @imvale renamed to @imogen-vale; @tokafor deleted their account, and a stranger may hold that login now;
        # @wrencastellan's ID has not been read yet; @jhalloran's row carries no ID.
        logins = {"1001": "imogen-vale", "1002": "", "583231": "octocat"}
        names = {"imogen-vale": "Imogen Vale", "tokafor": "Mallory Mallet", "imvale": "Someone Else"}
        d = dict(KNOWN, people=[*KNOWN["people"][:4], HALL["people"][4]], logins=logins, names=names)
        self.assertEqual(H.check(d), [])
        h = H.state(d)
        self.assertEqual([(p["login"], p["name"], p["handle"], p["badge"], p["id"]) for p in h["people"]],
                         [("tannergolden", "@TANNERGOLDEN", "the house", "@tannergolden", 24684994),
                          ("imogen-vale", "IMOGEN VALE", "@imogen-vale", "@imogen-vale", 1001),
                          ("wrencastellan", "@WRENCASTELLAN", "github  ·  challenger", "@wrencastellan", 1003),
                          ("jhalloran", "@JHALLORAN", "github  ·  challenger", "@jhalloran", None)])
        self.assertEqual([(r["login"], r["id"], r["house"]) for r in h["leaders"]],
                         [("tannergolden", 24684994, True), ("imogen-vale", 1001, False),
                          ("wrencastellan", 1003, False), ("jhalloran", 1004, False), ("octocat", 583231, False)])
        self.assertIn("Ranked by wins: @tannergolden with 12 wins", E.alt("hall-of-fame", d))
        self.assertIn("@imogen-vale with 4 wins", E.alt("hall-of-fame", d))
        self.assertNotIn("tokafor", E.alt("hall-of-fame", d))
        house = dict(d, logins={**logins, "24684994": "someone"})
        self.assertEqual(H.state(house)["people"][0]["login"], "tannergolden", "the house is always the house")
        self.assertEqual(H.state(house)["leaders"][0]["login"], "tannergolden")

    def test_each_winner_has_a_badge_and_the_leaders_has_a_still_twin(self):
        self.assertEqual(E.variants("hall-of-fame", HALL), ("wide", "narrow", "still", "narrow-still", "badge-1",
                                                            "badge-1-still", "badge-2", "badge-3", "badge-4",
                                                            "badge-5"))
        self.assertEqual(E.variants("hall-of-fame", EMPTY), ("wide", "narrow", "still", "narrow-still"))
        gone = dict(KNOWN, logins={"1002": "", "1003": ""})
        self.assertEqual(E.variants("hall-of-fame", gone), ("wide", "narrow", "still", "narrow-still", "badge-1",
                                                            "badge-1-still", "badge-2", "badge-3"),
                         "a badge for each winner shown, and none for a winner whose account is gone")
        self.assertEqual(E.variants("hall-of-fame", dict(HALL, series={"chess": [1, 1, 0, 0]})),
                         ("wide", "narrow", "still", "narrow-still"), "data the checks turn away draws no badge")
        for tone in (STANDARD, "blackprint"):
            badge = E.draw("hall-of-fame", HALL, tone, "day", "badge-2")
            self.assertIn("<title id=\"t\">Hall of Fame: @imvale</title>", badge)
            self.assertIn("Number 2, @imvale, 4 wins", badge)
            self.assertIn("hall-of-fame badge", badge)

    def test_a_place_an_account_that_is_gone_leaves_is_filled_from_the_rows_under_it(self):
        # The engines hand over twice the places: ten winners and twenty of GitHub's players, for five and ten.
        players = [f"player-{i:02}" for i in range(1, 21)]
        uids = {login: 2000 + i for i, login in enumerate(players, 1)}
        people = [["tannergolden", [10, 5, 10, 5], "2 Oct", 40, 24684994]]
        people += [[login, [20 - i, 0, 0, 0], "1 Oct", 25, uids[login]] for i, login in enumerate(players[:9])]
        leaders = [["tannergolden", 900, 40, [10, 5, 10, 5], 24684994]]
        leaders += [[login, 500 - i, 25, [20 - i if i < 9 else 0, 0, 0, 0], uids[login]]
                    for i, login in enumerate(players)]
        gone = {"player-02", "player-03", "player-07"}
        d = dict(KNOWN, series={g: [60, 30, 29, 1] for g in H.GAMES}, people=people, leaders=leaders, names={},
                 logins={str(uids[login]): "" if login in gone else login for login in players})
        self.assertEqual(H.check(d), [])
        h = H.state(d)
        self.assertEqual([p["login"] for p in h["people"]],
                         ["tannergolden", "player-01", "player-04", "player-05", "player-06"])
        self.assertEqual([r["login"] for r in h["leaders"]],
                         ["tannergolden", "player-01", "player-04", "player-05", "player-06", "player-08", "player-09",
                          "player-10", "player-11", "player-12", "player-13"])
        text = ED.block("hall-of-fame", d, "assets/elements")
        self.assertIn("@tannergolden and GitHub's top 10 · ranked by wins in all four games", text)
        self.assertIn("| 🥉 | [@player-05](https://github.com/player-05) | 0 | 0 | 0 | 16 | 496 | 25 |\n", text)
        self.assertTrue(text.split("\n\nA win is")[0].endswith("| 10 | [@player-13](https://github.com/player-13) |"
                                                              " 0 | 0 | 0 | 0 | 488 | 25 |"))
        for login in gone:
            self.assertNotIn(login, text + E.alt("hall-of-fame", d))
        self.assertEqual(text.count('<a href="https://github.com/'), 5, "five badges, each linked")
        for tone in (STANDARD, "blackprint"):
            for variant in E.variants("hall-of-fame", d):
                E.draw("hall-of-fame", d, tone, "dark", variant)  # the kit's lint and budget, or it raises


class Settings(unittest.TestCase):
    def assertTurnedAway(self, d: dict, said: str):
        errors = H.check(d)
        self.assertTrue(any(said in e for e in errors), f"{said!r} not in {errors}")

    def test_the_element_the_engines_write_is_read_and_checked_as_a_run_reads_it(self):
        section = yaml_reader.loads(WRITTEN)["elements"]
        self.assertEqual(ED.validate(section, {}, subject="tannergolden"), [])
        d = ED.merged(section, {}, subject="tannergolden")["hall-of-fame"]
        self.assertEqual([(p["login"], p["wins"], p["by_game"]["chess"]) for p in H.state(d)["people"]],
                         [("tannergolden", 12, 5), ("imvale", 3, 2)])
        self.assertIn("hall-of-fame", ED.OWN_THEMES, "it keeps the page's own theme whatever set is up")

    def test_it_is_drawn_on_tannergoldens_profile_alone_beside_chess_hall(self):
        section = {"hall-of-fame": dict(HALL), "chess-hall": {"kind": "chess-hall", "games": 0, "house": 0,
                                                              "world": 0, "draws": 0}}
        self.assertEqual(ED.validate(section, {}, subject="tannergolden"), [])
        self.assertEqual(ED.validate(section, {}, subject="TannerGolden"), [])
        for elsewhere in ("octocat", "tannergolden/markdown", ""):
            with self.subTest(subject=elsewhere):
                errors = ED.validate(section, {}, subject=elsewhere)
                self.assertIn("hall-of-fame: the hall-of-fame element is drawn on @tannergolden's profile alone",
                              errors)
                self.assertIn("chess-hall: the chess-hall element is drawn on @tannergolden's profile alone", errors)
        self.assertEqual(ED.validate({"h": {"kind": "hall-of-fame"}}, {}, subject="tannergolden"), [],
                         "every field may wait for the engines")

    def test_the_series_is_every_game_its_wins_and_draws_adding_up(self):
        for series in ({"chess": [12, 5, 6, 1]}, {**SERIES, "go": [1, 1, 0, 0]}, [9, 4, 2, 3], "tictactoe", {}, 5,
                       {**{g: v for g, v in SERIES.items() if g != "checkers"}, "Checkers": [5, 2, 2, 1]}):
            with self.subTest(series=series):
                self.assertTurnedAway({**HALL, "series": series}, "series gives each of the four games, tictactoe,"
                                                                  " connectfour, checkers and chess, its games")
        for row in ([9, 4, 2], [9, 4, 2, 3, 0], [9, 4, "2", 3], [9, 4, True, 2], [9, 4, -1, 6], [9.0, 4, 2, 3],
                    [1_000_000, 1_000_000, 0, 0], None, "9 4 2 3", {"games": 9}):
            with self.subTest(row=row):
                self.assertTurnedAway({**HALL, "series": {**SERIES, "connectfour": row}},
                                      f"series: connectfour {row!r} is not the games finished")
        self.assertTurnedAway({**HALL, "series": {**SERIES, "tictactoe": [9, 4, 2, 2]}},
                              "series: tictactoe's wins and draws add up to 8 games, not the 9 finished")
        self.assertEqual(H.check({**HALL, "series": {g: [999_999, 999_999, 0, 0] for g in H.GAMES}}), [],
                         "each game's counts up to 999,999")
        self.assertEqual(H.check({**HALL, "series": None}), [])

    def test_a_winner_is_a_login_with_wins_in_every_game_the_sheet_can_letter_ranked_by_all_of_them(self):
        one = {**HALL, "names": {}}
        rows = ([12345, [1, 0, 0, 0], "2 Oct", 1], ["imvale", 1, "2 Oct", 1], ["imvale", [1, 0, 0], "2 Oct", 1],
                ["imvale", [1, 0, 0, 0, 0], "2 Oct", 1], ["imvale", [0, 0, 0, 0], "2 Oct", 1],
                ["imvale", [1, 0, 0, True], "2 Oct", 1], ["imvale", [1, 0, -1, 1], "2 Oct", 1],
                ["imvale", [1_000_000, 0, 0, 0], "2 Oct", 1], ["imvale", [1, 0, 0, "1"], "2 Oct", 1],
                ["imvale", [1, 0, 0, 0], "2 Oct", 1_000_000], ["imvale", [1, 0, 0, 0], "2 Oct", False],
                ["imvale", [1, 0, 0, 0], 1984, 1], ["imvale", [1, 0, 0, 0], "31 Sep", 1],
                ["imvale", [1, 0, 0, 0], "2 Oct"], ["imvale", [1, 0, 0, 0], "2 Oct", 1, 1001, 1],
                ["imvale", (1, 0, 0, 0), "2 Oct", 1], ["octo|cat", [1, 0, 0, 0], "2 Oct", 1])
        for row in rows:
            with self.subTest(row=row):
                self.assertTurnedAway({**one, "people": [row]}, f"people: {row!r} is not a winner's login, their"
                                                                " wins in each of the four games")
        self.assertEqual(H.check({**one, "people": [["12345", [0, 0, 0, 1], "", 1]]}), [],
                         "an all-digit login, as text, and no day yet")
        self.assertEqual(H.check({**one, "people": [["imvale", [999_999] * 4, "29 Feb", 999_999]]}), [])
        unranked = [["imvale", [1, 0, 0, 0], "2 Oct", 3], ["tokafor", [0, 9, 0, 0], "3 Oct", 12]]
        self.assertTurnedAway({**HALL, "people": unranked},
                              "people: the winners are ranked by their wins in all four games, the most first")
        tied = [HALL["people"][0], ["jhalloran", [0, 0, 0, 3], "8 Oct", 3], HALL["people"][2]]
        self.assertEqual(H.check({**HALL, "people": tied}), [], "winners on the same wins stand in any order")
        ten = HALL["people"] + [[f"spare-{i}", [0, 0, 1, 0], "1 Oct", 1] for i in range(5)]
        self.assertEqual(H.check({**HALL, "people": ten}), [])
        self.assertTurnedAway({**HALL, "people": ten + [ten[-1]]}, "people is a list of at most 10 winners")
        self.assertTurnedAway({**HALL, "people": "tannergolden"}, "people is a list of at most 10 winners")

    def test_a_name_is_plain_text_without_an_at_that_fits_in_capitals(self):
        for name in ("@tannergolden", "Tanner @ Home", "ß" * 21, " ", "​", 1984, True, ["Imogen Vale"], "",
                     "x" * 41):
            with self.subTest(name=name):
                errors = H.check({**HALL, "names": {"imvale": name}})
                self.assertTrue(any(e.startswith("names gives a login its name") for e in errors), errors)
        for name in ("ß" * 20, "Imogen Vale", "Tomás Ørsted", "O'Brien-Smith", "x" * 40):
            with self.subTest(name=name):
                self.assertEqual(H.check({**HALL, "names": {"imvale": name}}), [])

    def test_a_row_of_the_hall_may_carry_its_accounts_id(self):
        self.assertEqual(H.check(KNOWN), [])
        self.assertEqual(H.check({**KNOWN, "people": HALL["people"][:2] + KNOWN["people"][2:]}), [],
                         "rows with an ID and rows without one stand side by side")
        ceiling = [[*HALL["people"][0], 9_999_999_999_999_999]]
        self.assertEqual(H.check({**HALL, "people": ceiling, "leaders": [[*HALL["leaders"][0], 1]]}), [])
        for uid in (0, -1, True, "1001", 10_000_000_000_000_000, 1001.0, None):
            with self.subTest(uid=uid):
                people = [[*HALL["people"][0], uid]]
                self.assertTrue(any(e.startswith("people:") for e in H.check({**HALL, "people": people})))
                leaders = [[*HALL["leaders"][0], uid]]
                self.assertTrue(any(e.startswith("leaders:") for e in H.check({**HALL, "leaders": leaders})))
        for logins in ({"1001": "imogen-vale"}, {"1001": ""}, {"9999999999999999": "octocat"}, {}):
            with self.subTest(logins=logins):
                self.assertEqual(H.check({**KNOWN, "logins": logins}), [])
        for logins in ({1001: "imogen-vale"}, {"01001": "imogen-vale"}, {"1001": "not a login!"}, {"1001": None},
                       {"1001": 1001}, {"10000000000000000": "octocat"}, {"imvale": "imogen-vale"}, ["1001"], "1001"):
            with self.subTest(logins=logins):
                errors = H.check({**KNOWN, "logins": logins})
                self.assertTrue(any(e.startswith("logins gives an account's ID its login") for e in errors), errors)

    def test_what_the_leaderboard_lists_is_checked(self):
        house = ["tannergolden", 9, 2, [1, 0, 0, 0]]
        cases = {
            "a row that is not a login, two counts and four games' wins": [house, ["octocat", "9", 2, [0, 0, 0, 0]]],
            "more wins than games": [["tannergolden", 9, 2, [1, 1, 1, 0]]],
            "more games than moves": [house, ["octocat", 1, 2, [0, 0, 0, 0]]],
            "a login that could break the table": [house, ["octo|cat", 9, 2, [0, 0, 0, 0]]],
            "the house not on top": [["octocat", 9, 2, [0, 0, 0, 0]], house],
            "the house twice": [house, ["TannerGolden", 9, 2, [0, 0, 0, 0]]],
            "a player without a move": [house, ["octocat", 0, 0, [0, 0, 0, 0]]],
            "players out of order": [house, ["octocat", 9, 2, [0, 0, 0, 0]], ["hubot", 3, 1, [0, 0, 1, 0]]],
            "players on the same wins out of order by moves": [house, ["octocat", 3, 2, [0, 0, 0, 1]],
                                                               ["hubot", 9, 2, [1, 0, 0, 0]]],
            "twenty-one players": [house] + [[f"p{i}", 30 - i, 1, [0, 0, 0, 0]] for i in range(21)],
            "not a list": "tannergolden",
            "moves past their ceiling": [["tannergolden", 1_000_000_000, 5, [0, 0, 0, 0]]],
            "games past their ceiling": [["tannergolden", 999_999_999, 1_000_000, [0, 0, 0, 0]]],
            "wins in three games": [house, ["octocat", 9, 2, [0, 0, 0]]],
            "wins as one count": [house, ["octocat", 9, 2, 0]],
            "a count that is a bool": [house, ["octocat", 9, False, [0, 0, 0, 0]]],
            "a login that is a number": [house, [12345, 9, 2, [0, 0, 0, 0]]],
            "an ID that is text": [house, ["octocat", 9, 2, [0, 0, 0, 0], "583231"]],
            "an ID past sixteen digits": [house, ["octocat", 9, 2, [0, 0, 0, 0], 10 ** 16]],
            "a sixth field": [house, ["octocat", 9, 2, [0, 0, 0, 0], 583231, 1]],
        }
        for case, leaders in cases.items():
            with self.subTest(case=case):
                errors = ED.validate({"h": {**HALL, "leaders": leaders}}, {}, subject="tannergolden")
                self.assertTrue(errors and all(e.startswith("h: leaders") for e in errors), errors)
        unordered = {"h": {**HALL, "leaders": cases["players out of order"]}}
        self.assertIn("h: leaders: GitHub's players are ranked by their wins in all four games, then their moves",
                      ED.validate(unordered, {}, subject="tannergolden"))
        for fine in ([], [house], [["tannergolden", 0, 0, [0, 0, 0, 0]], ["octocat", 1, 1, [0, 0, 0, 0]]],
                     HALL["leaders"], KNOWN["leaders"],
                     [["tannergolden", 999_999_999, 999_999, [249_999, 250_000, 250_000, 250_000], 24684994]],
                     [house] + [[f"p{i}", 30 - i, 1, [0, 0, 0, 0]] for i in range(20)]):
            with self.subTest(leaders=fine):
                self.assertEqual(ED.validate({"h": {**HALL, "leaders": fine}}, {}, subject="tannergolden"), [])

    def test_nothing_the_settings_can_hold_makes_the_check_raise(self):
        hostile = (None, True, False, 0, -1, 1984, 10 ** 30, 1.5, "", "x", "```", [], [1], [[]], {}, {"a": 1},
                   ["x", "y", "z", "w", "v"], [[1, 2, 3, 4]])
        rows = ("people", "leaders")
        for key in sorted(set(KNOWN) | {"logins", "names", "series"}):
            for bad in hostile:
                for value in (bad, [bad], [[bad] * 5], [["x", bad, "1 Oct", 1]], [["x", 1, 1, bad]]) if key in rows \
                        else (bad,):
                    with self.subTest(key=key, value=value):
                        self.assertIsInstance(H.check({**KNOWN, key: value}), list)
            with self.subTest(key=key, series="hostile rows"):
                for bad in hostile:
                    self.assertIsInstance(H.check({**KNOWN, "series": {g: bad for g in H.GAMES}}), list)
        for bad in hostile:
            key = bad if isinstance(bad, (str, int)) else "x"
            self.assertIsInstance(H.check({**KNOWN, "names": {key: bad}, "logins": {key: bad}}), list)


class Readme(unittest.TestCase):
    def test_the_hall_links_every_winner_by_their_badge(self):
        text = ED.block("hall-of-fame", HALL, "assets/elements")
        self.assertTrue(text.startswith("<!-- markdown:element:hall-of-fame:start -->\n<picture>"))
        self.assertIn('<div align="center">\n\n<a href="https://github.com/tannergolden"><picture><source media='
                      '"(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" '
                      'srcset="assets/elements/hall-of-fame-badge-1-still-dark.svg">', text)
        self.assertIn('<a href="https://github.com/jhalloran"><picture><source media="(prefers-color-scheme: dark)" '
                      'srcset="assets/elements/hall-of-fame-badge-5-dark.svg"><img alt="#5 @jhalloran, 1 win" '
                      'src="assets/elements/hall-of-fame-badge-5-day.svg"></picture></a>', text)
        self.assertEqual(text.count("(prefers-reduced-motion: reduce)"), 6,
                         "the hall's wide and phone still files, and the leader's badge, by day and night")
        self.assertNotIn("badge", ED.block("hall-of-fame", EMPTY, "assets/elements"))

    def test_the_leaderboard_has_a_column_of_wins_for_every_game_chess_first_then_moves_and_games(self):
        text = ED.block("hall-of-fame", HALL, "assets/elements")
        self.assertIn("</picture></a>\n\n</div>\n\n<details>\n<summary>🏆 <b>Leaderboard</b> · @tannergolden and"
                      " GitHub's top 5 · ranked by wins in all four games, then moves</summary>\n\n"
                      "|  | Player | ♔♚ | ⛀⛂ | ⚪⚫ | ❌⭕ | Moves | Games |\n"
                      "| :-: | :--- | --: | --: | --: | --: | --: | --: |\n"
                      "| 🏠 | **[@tannergolden](https://github.com/tannergolden)** | **5** | **2** | **1** | **4** | "
                      "**1,240** | **29** |\n"
                      "| 🥇 | [@imvale](https://github.com/imvale) | 2 | 0 | 1 | 1 | 40 | 7 |\n"
                      "| 🥈 | [@tokafor](https://github.com/tokafor) | 1 | 1 | 1 | 0 | 31 | 9 |\n"
                      "| 🥉 | [@wrencastellan](https://github.com/wrencastellan) | 0 | 1 | 0 | 1 | 52 | 6 |\n"
                      "| 4 | [@jhalloran](https://github.com/jhalloran) | 1 | 0 | 0 | 0 | 12 | 3 |\n", text)
        self.assertTrue(text.endswith("| 5 | [@octocat](https://github.com/octocat) | 0 | 0 | 0 | 0 | 9 | 2 |\n\n"
                                      "A win is a winning move of one's own, in any of the four games; a move the"
                                      " Arbiter plays, for either side, counts for nobody.\n\n</details>\n"
                                      "<!-- markdown:element:hall-of-fame:end -->"))
        self.assertEqual(RM.SIGNS, {"chess": "\u2654\u265a", "checkers": "\u26c0\u26c2", "connectfour": "\u26aa\u26ab",
                                    "tictactoe": "\u274c\u2b55"},
                         "each game's column headed by its two side signs, the house's first: the white king, the"
                         " white man, the white disc and X")
        self.assertEqual(list(RM.SIGNS), list(H.ORDER), "Chess first")
        alone = ED.block("hall-of-fame", EMPTY, "assets/elements")
        self.assertIn("</picture>\n\n<details>\n<summary>🏆 <b>Leaderboard</b> · @tannergolden · GitHub's players join"
                      " with their first move</summary>", alone)
        self.assertIn("| 🏠 | **[@tannergolden](https://github.com/tannergolden)** | **0** | **0** | **0** | **0** | "
                      "**0** | **0** |", alone)
        one = H.leaderboard({**EMPTY, "leaders": [["tannergolden", 1, 1, [0, 0, 0, 0]], ["octocat", 1, 1, [0] * 4]]})
        self.assertIn("· @tannergolden and GitHub's top player · ranked by wins in all four games, then moves", one)
        self.assertNotIn("Leaderboard", ED.block("hall-of-fame", {"kind": "hall-of-fame"}, "assets/elements"))
        big = H.leaderboard({**EMPTY, "leaders": [["tannergolden", 999_999_999, 999_999, [249_999] * 4]]})
        self.assertIn("| **249,999** | **249,999** | **249,999** | **249,999** | **999,999,999** | **999,999** |", big)

    def test_the_leaderboard_reads_each_players_wins_by_their_game_from_the_tier_order_of_the_data(self):
        # The data lists the wins Tic-Tac-Toe, Connect Four, Checkers, Chess; the leaderboard Chess first.
        d = {**EMPTY, "leaders": [["tannergolden", 9_000, 5_000, [1, 20, 300, 4_000]],
                                  ["imvale", 80, 8, [0, 0, 0, 6]], ["octocat", 90, 9, [5, 0, 0, 0]]]}
        self.assertEqual(H.check(d), [])
        rows = H.leaderboard(d).split("\n")
        self.assertIn("| 🏠 | **[@tannergolden](https://github.com/tannergolden)** | **4,000** | **300** | **20** |"
                      " **1** | **9,000** | **5,000** |", rows)
        self.assertIn("| 🥇 | [@imvale](https://github.com/imvale) | 6 | 0 | 0 | 0 | 80 | 8 |", rows)
        self.assertIn("| 🥈 | [@octocat](https://github.com/octocat) | 0 | 0 | 0 | 5 | 90 | 9 |", rows)

    def test_the_hall_links_each_player_by_the_login_their_account_has_now_and_leaves_a_gone_one_out(self):
        # @imvale is @imogen-vale now; @tokafor deleted their account, so they leave the badges and the leaderboard,
        # and the players under them move up; @jhalloran's ID has not been read, so their row's own login stands.
        d = dict(KNOWN, logins={"1001": "imogen-vale", "1002": "", "1003": "wrencastellan", "583231": "octocat"})
        text = ED.block("hall-of-fame", d, "assets/elements")
        self.assertIn('<a href="https://github.com/imogen-vale"><picture><source media="(prefers-color-scheme: dark)" '
                      'srcset="assets/elements/hall-of-fame-badge-2-dark.svg"><img alt="#2 @imogen-vale, 4 wins" ',
                      text)
        self.assertIn('<a href="https://github.com/wrencastellan"><picture><source media="(prefers-color-scheme: '
                      'dark)" srcset="assets/elements/hall-of-fame-badge-3-dark.svg"><img alt="#3 @wrencastellan, 2 '
                      'wins" ', text)
        self.assertNotIn("badge-5", text)
        self.assertIn("@tannergolden and GitHub's top 4 · ranked by wins in all four games", text)
        self.assertIn("| 🥇 | [@imogen-vale](https://github.com/imogen-vale) | 2 | 0 | 1 | 1 | 40 | 7 |\n"
                      "| 🥈 | [@wrencastellan](https://github.com/wrencastellan) | 0 | 1 | 0 | 1 | 52 | 6 |\n", text)
        self.assertNotIn("tokafor", text)
        self.assertNotIn("imvale", text)
        self.assertEqual(text.count("<a href="), 4, "every badge shown is a link")
        self.assertEqual(text.count("(https://github.com/"), 5, "and every leader shown")

    def test_every_line_of_the_block_is_one_a_readme_reads_as_it_is_meant(self):
        text = ED.block("hall-of-fame", KNOWN, "assets/elements")
        for ch in DASHES:
            self.assertNotIn(ch, text)
        rows = [line for line in text.splitlines() if line.startswith("| ")]
        self.assertEqual(len(rows), 2 + 6, "the head, its alignment, and the house over five of GitHub's players")
        self.assertTrue(all(line.count(" | ") == 7 and line.endswith(" |") for line in rows),
                        "eight cells to every row: the place, the player, a game's wins four times, moves, games")


class Sets(unittest.TestCase):
    def test_a_holiday_or_collection_leaves_it_in_the_pages_own_theme(self):
        elements = ED.merged({"hall-of-fame": dict(HALL)}, {}, subject="tannergolden")
        printed = ED.render(elements, "blackprint")
        self.assertEqual(ED.render(elements, "blackprint", "halloween"), printed)
        standard = ED.render(elements, STANDARD)
        self.assertEqual(sorted(standard), sorted(printed))
        self.assertIn("hall-of-fame-narrow-still-dark.svg", standard)
        self.assertNotEqual(standard["hall-of-fame-day.svg"], printed["hall-of-fame-day.svg"],
                            "the standard theme has its own skin")
        for svg in standard.values():
            self.assertEqual(lint(svg, budget=BUDGET["board"]), [])


def account(uid: int, login: str, name=None) -> dict:
    """GitHub's answer to /user/{id}: the account as it is now."""
    return {"login": login, "id": uid, "type": "User", "name": name}


class Measured(unittest.TestCase):
    def test_a_winners_name_is_read_from_their_profile_when_the_sheet_can_letter_it(self):
        gh = FakeGitHub({}, users={"imvale": {"name": "Imogen  Vale"}, "tokafor": {"name": "Tomás <O>"},
                                   "jhalloran": {"name": None}})
        self.assertEqual(measure.winners(gh, HALL["people"]), {"names": {"imvale": "Imogen Vale"}})
        self.assertNotIn("/users/tannergolden", [path for path, _ in gh.asked], "the house is never looked up")
        section = {"hall-of-fame": {**HALL, "names": {}, "measure": {}}}
        out = measure.measure(section, {}, git=None, gh=gh, subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"hall-of-fame": {"names": {"imvale": "Imogen Vale"}}})
        self.assertFalse([path for path, _ in gh.asked if path.startswith("/user/")], "a row without an ID")

    def test_a_row_with_its_accounts_id_is_read_by_the_id_so_a_login_that_changed_hands_is_never_credited(self):
        # The Hall's rows carry their ID fifth, as chess-hall's do, so the run reads them as it reads chess-hall's:
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
        self.assertEqual([C.game.account(row) for row in people], [24684994, 1001, 1002, 1003, None])
        self.assertEqual([C.game.account(row) for row in KNOWN["leaders"]], list(IDS.values()))
        measured = measure.winners(gh, people, KNOWN["leaders"])
        self.assertEqual(measured, {"names": {"imogen-vale": "Imogen Vale", "jhalloran": "Jo Halloran"},
                                    "logins": {"1001": "imogen-vale", "1002": "", "1003": "wrencastellan",
                                               "1004": "jhalloran", "583231": "octocat"}})
        asked = [path for path, _ in gh.asked]
        self.assertEqual(sorted(asked), ["/user/1001", "/user/1002", "/user/1003", "/user/1004", "/user/583231",
                                         "/users/jhalloran"], "each ID read once, the house never, a login only "
                                                              "for the row without an ID")
        d = dict(KNOWN, people=people, **measured)
        self.assertEqual(H.check(d), [])
        drawn = [(p["name"], p["badge"]) for p in H.state(d)["people"]]
        self.assertEqual(drawn, [("@TANNERGOLDEN", "@tannergolden"), ("IMOGEN VALE", "@imogen-vale"),
                                 ("@WRENCASTELLAN", "@wrencastellan"), ("JO HALLORAN", "@jhalloran")])
        text = ED.block("hall-of-fame", d, "assets/elements")
        for gone in ("github.com/imvale", "github.com/tokafor"):
            self.assertNotIn(gone, text)
        section = {"hall-of-fame": {**{k: v for k, v in d.items() if k not in measured}, "measure": {}}}
        out = measure.measure(section, {}, git=None, gh=gh, subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"hall-of-fame": measured}, "the run keeps the logins beside the names")
        self.assertEqual(ED.validate(section, out, subject="tannergolden"), [])
        merged = ED.merged(section, out, subject="tannergolden")["hall-of-fame"]
        self.assertEqual(merged["logins"]["1001"], "imogen-vale")

    def test_only_github_s_404_takes_a_player_off_and_a_bad_minute_keeps_the_last_reading(self):
        # GitHub refuses /user/1001 (a 403) and fails on /user/1002 past every retry; /user/1003 is a 404, a deleted
        # account; /user/1004 answers.
        def fault(**params):
            raise ApiError("GitHub answered 502 for /user/1002: ")

        paths = {"/user/1001": None, "/user/1002": fault, "/user/1004": account(1004, "jhalloran", "Jo Halloran"),
                 "/user/583231": account(583231, "octocat")}
        before = {"names": {"imogen-vale": "Imogen Vale", "tokafor": "Tomas Okafor"},
                  "logins": {"1001": "imogen-vale", "1002": "", "1003": "wrencastellan"}}
        measured = measure.winners(FakeGitHub({}, paths=paths), KNOWN["people"], KNOWN["leaders"], before)
        self.assertEqual(measured, {"names": {"imogen-vale": "Imogen Vale", "jhalloran": "Jo Halloran"},
                                    "logins": {"1001": "imogen-vale", "1002": "", "1003": "", "1004": "jhalloran",
                                               "583231": "octocat"}},
                         "a refusal and a fault keep the last reading, a gone account staying gone; a 404 is gone")
        h = H.state(dict(KNOWN, **measured))
        self.assertEqual([p["login"] for p in h["people"]], ["tannergolden", "imogen-vale", "jhalloran"])
        self.assertEqual([r["login"] for r in h["leaders"]], ["tannergolden", "imogen-vale", "jhalloran", "octocat"],
                         "and the leaderboard drops them too, the players under them moving up")
        first = measure.winners(FakeGitHub({}, paths=paths), KNOWN["people"], KNOWN["leaders"])
        self.assertEqual(first["logins"], {"1003": "", "1004": "jhalloran", "583231": "octocat"},
                         "with no reading before, an account GitHub didn't answer for is shown as its row has it")
        self.assertEqual([p["login"] for p in H.state(dict(KNOWN, **first))["people"]],
                         ["tannergolden", "imvale", "tokafor", "jhalloran"])
        section = {"hall-of-fame": {**KNOWN, "measure": {}}}
        out = measure.measure(section, {"hall-of-fame": before}, git=None, gh=FakeGitHub({}, paths=paths),
                              subject="tannergolden", today=None, notes=[])
        self.assertEqual(out, {"hall-of-fame": measured}, "the run hands the last reading on")
        idle = measure.measure(section, {"hall-of-fame": before}, git=None, gh=None, subject="tannergolden",
                               today=None, notes=[])
        self.assertEqual(idle, {"hall-of-fame": before}, "a run without GitHub keeps what the last one read")

    def test_a_name_that_poses_as_a_handle_or_that_no_tone_can_letter_is_left_for_the_login(self):
        names = {"imvale": "@tannergolden", "tokafor": "Иван Петров", "wrencastellan": "山田太郎",
                 "jhalloran": "Ελένη Παππά"}
        gh = FakeGitHub({}, users={login: {"name": name} for login, name in names.items()})
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
                    E.draw("hall-of-fame", d, tone, "day", variant)
                self.assertEqual(E.WARNINGS, [], "every name the run keeps is lettered as it is, in every tone")
        E.WARNINGS.clear()


class ChessHall(unittest.TestCase):
    def test_chess_hall_keeps_its_own_data_and_files(self):
        hall = {"kind": "chess-hall", "games": 2, "house": 1, "world": 1, "draws": 0,
                "people": [["tannergolden", 1, "2 Oct", 2], ["imvale", 1, "1 Oct", 1]],
                "leaders": [["tannergolden", 30, 1, 2], ["imvale", 12, 1, 1]]}
        self.assertEqual(ED.validate({"chess-hall": hall}, {}, subject="tannergolden"), [])
        self.assertTrue(H.check({**hall, "kind": "hall-of-fame"}), "a chess-hall's rows are not the Hall's")
        self.assertEqual(E.KINDS["chess-hall"][1:], (("wide", "narrow", "still", "narrow-still"), "sheet"))
        self.assertIn("ranked by wins, then moves", ED.block("chess-hall", hall, "assets/elements"))
        self.assertIn("chess hall", E.draw("chess-hall", hall, STANDARD, "day", "wide").split("-->")[0])


if __name__ == "__main__":
    unittest.main()
