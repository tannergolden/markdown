# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""A finished game's countdown: the moment its fresh board comes, in the page's time, and how long was left as of
the board's drawing.

A README runs nothing, so a countdown can only say what is true whenever it is read: the exact moment the next
game opens, and the time left as of the moment the board was drawn, both lettered on the sheet. The sample is
chess's Fool's Mate, game 3 won by GitHub on 12 Oct, its next game opening at 01:00 UTC on 15 Oct, 20:00 the
evening before in EST, the page's zone; the board drawn at 10:47 UTC on 13 Oct."""
from __future__ import annotations

import datetime as dt
import unittest

from tests import support

from domain.canvas import BUDGET, lint
from domain.elements import draw as E
from domain.elements.chess import game as CG

support.install()
FINISHED = {"kind": "chess", "fen": "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3", "game": 3,
            "move": 3, "players": 2,
            "last": {"san": "Qh4#", "from": "d8", "to": "h4", "piece": "queen", "words": "The Queen Strikes h4",
                     "by": "@octocat", "when": "12 Oct"},
            "history": [[1, "f3", "e5", "@hubot"], [2, "g4", "Qh4#", "@octocat"]],
            "result": {"winner": "github", "how": "checkmate"}, "next": "14 Oct", "next_at": "2026-10-15T01:00:00Z",
            "note": "Game 3 is over."}
EST = dt.timezone(dt.timedelta(hours=-5), "EST")       # the page's zone, as a run hands it over
ASOF = {"asof": "2026-10-13T10:47:00Z", "zone": EST}


class Countdown(unittest.TestCase):

    def test_it_says_when_the_next_game_opens_and_how_long_was_left_in_the_pages_time(self):
        cd = CG.countdown({**FINISHED, **ASOF})
        self.assertEqual(cd["opens"], "14 Oct, 20:00 EST")
        self.assertEqual(cd["asof"], "13 Oct, 05:47 EST")
        self.assertEqual(cd["in"], "1 day 14 hrs")
        self.assertAlmostEqual(cd["left"], 38 + 13 / 60)
        self.assertEqual(cd["of"], 48.0)

    def test_without_either_moment_or_a_result_there_is_no_countdown(self):
        self.assertIsNone(CG.countdown(FINISHED))
        self.assertIsNone(CG.countdown({**FINISHED, **ASOF, "next_at": None}))
        self.assertIsNone(CG.countdown({**FINISHED, **ASOF, "result": None}))
        self.assertIsNone(CG.countdown({**FINISHED, "asof": "yesterday"}))

    def test_a_board_drawn_after_its_moment_says_nothing_is_left(self):
        cd = CG.countdown({**FINISHED, "asof": "2026-10-15T09:00:00Z", "zone": EST})
        self.assertEqual((cd["left"], cd["in"]), (0.0, "under an hour"))

    def test_without_a_zone_handed_over_it_tells_time_in_utc(self):
        for zone in (None, "EST", "Mars/Olympus_Mons"):
            with self.subTest(zone=zone):
                cd = CG.countdown({**FINISHED, **ASOF, "zone": zone})
                self.assertEqual(cd["opens"], "15 Oct, 01:00 UTC")

    def test_the_time_left_is_said_in_days_and_hours(self):
        for hours, said in ((47.9, "1 day 23 hrs"), (48, "2 days"), (25, "1 day 1 hr"), (5, "5 hrs"), (1, "1 hr"),
                            (.4, "under an hour")):
            with self.subTest(hours=hours):
                self.assertEqual(CG.left_words(hours), said)

    def test_only_a_finished_board_has_the_moment_its_next_game_comes(self):
        self.assertEqual(CG.check({**FINISHED}), [])
        self.assertIn("next_at", " ".join(CG.check({**FINISHED, "next_at": "soon"})))
        under_way = {k: v for k, v in FINISHED.items() if k not in ("result", "next")}
        self.assertIn("a game under way has none", " ".join(CG.check({**under_way, "due": "19 Oct"})))

    def test_a_finished_board_draws_its_countdown_in_place_of_the_count_in_every_theme(self):
        with_cd = {**FINISHED, **ASOF}
        for tone in ("blackprint", "standard"):
            for variant in ("wide", "narrow"):
                for theme in ("day", "dark"):
                    with self.subTest(tone=tone, variant=variant, theme=theme):
                        svg = E.draw("chess", with_cd, tone, theme, variant)
                        self.assertEqual(lint(svg, budget=BUDGET["board"]), [])
                        self.assertNotEqual(svg, E.draw("chess", FINISHED, tone, theme, variant))

    def test_the_same_moment_draws_the_same_bytes_and_a_later_one_other_bytes(self):
        a = E.draw("chess", {**FINISHED, **ASOF}, "blackprint", "day", "wide")
        self.assertEqual(a, E.draw("chess", {**FINISHED, **ASOF}, "blackprint", "day", "wide"))
        later = {**FINISHED, **ASOF, "asof": "2026-10-14T10:47:00Z"}
        self.assertNotEqual(a, E.draw("chess", later, "blackprint", "day", "wide"))


if __name__ == "__main__":
    unittest.main()
