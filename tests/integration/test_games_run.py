# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games on @tannergolden's profile, redrawn through the command line run after run as its clock redraws them,
leave exactly the files the README shows, so nothing an old board drew is ever left behind. A board's files are named
for the board, never for its position, so a move, a finished game and a fresh board each redraw the same files in
place. The Hall of Fame draws a badge for each winner it shows, so a Hall that shows fewer winners takes their badges
away. A game taken off the page takes its files and its block with it, and a file someone put there by hand is never
touched."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.integration import test_elements_run as R
from tests.unit import test_elements_chess as CH
from tests.unit import test_elements_games as G
from tests.unit import test_elements_hall as H

from infra import files

IDS = ("chess", "checkers", "connectfour", "tictactoe", "hall-of-fame")


def written(elements: dict[str, dict]) -> str:
    """The settings as the profile's engines write them: each element's keys one to a line, each value in JSON."""
    lines = ["subject: tannergolden", "theme: blueprint", "banners: false", "trophies: false", "elements:"]
    for eid, d in elements.items():
        lines.append(f"  {eid}:")
        lines += [f"    {key}: {json.dumps(value, ensure_ascii=False)}" for key, value in d.items()]
    return "\n".join(lines) + "\n"


class Clock(unittest.TestCase):
    """The profile's page, redrawn as its games go on."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "tannergolden"
        (self.root / ".github").mkdir(parents=True)
        self.out = self.root / "assets" / "elements"
        self.readme = self.root / "README.md"
        self.readme.write_text("# tannergolden\n\n" + "\n\n".join(
            f"<!-- markdown:element:{eid}:start -->\n<!-- markdown:element:{eid}:end -->" for eid in IDS) + "\n",
            encoding="utf-8")
        self.games = {"chess": CH.GAME, "checkers": G.CK_GITHUB, "connectfour": G.C4_GITHUB,
                      "tictactoe": G.TTT_GITHUB, "hall-of-fame": H.HALL}

    def tearDown(self):
        self.tmp.cleanup()

    def draw(self, **boards: dict) -> dict[str, bytes]:
        """Redraw the page with `boards` in place of the games they name, as the clock does, and return every file
        the kit drew, by name, once the page is shown to be clean."""
        self.games.update({eid.replace("_", "-"): d for eid, d in boards.items()})
        (self.root / ".github" / "markdown.yaml").write_text(written(self.games), encoding="utf-8")
        code, out = R.kit("run", "--root", str(self.root), "--today", "2026-10-12")
        self.assertEqual(code, 0, out)
        drawn = {name: (self.out / name).read_bytes() for name in files.drawn(self.out)}
        shown = set(re.findall(r"assets/elements/([\w.-]+\.svg)", self.readme.read_text(encoding="utf-8")))
        self.assertEqual(set(drawn), shown, "the folder holds exactly the files the README shows")
        self.assertEqual(R.kit("check", "--root", str(self.root))[0], 0)
        return drawn

    def test_a_move_a_finished_game_and_a_fresh_board_redraw_the_same_files_in_place(self):
        before = self.draw()
        boards = sorted(name for name in before if not name.startswith("hall-of-fame"))
        self.assertEqual(len(boards), 4 * 8, "four games, each wide and a phone's, moving and still, day and dark")
        for step in ({"chess": CH.HOUSE, "checkers": G.CK_CROWNED, "connectfour": G.C4_HOUSE,
                      "tictactoe": G.TTT_HOUSE},
                     {"chess": CH.SCHOLAR, "checkers": G.CK_WON, "connectfour": G.C4_WON, "tictactoe": G.TTT_WON},
                     {"chess": CH.OPENING, "checkers": G.CK_OPENING, "connectfour": G.C4_FRESH,
                      "tictactoe": G.TTT_FRESH}):
            after = self.draw(**step)
            self.assertEqual(sorted(name for name in after if not name.startswith("hall-of-fame")), boards)
            for name in boards:
                self.assertNotEqual(after[name], before[name], f"{name} is redrawn in place")
            before = after

    def test_each_game_is_folded_under_its_banner_chess_open_and_the_other_three_shut(self):
        # the banner stands over the fold, at the README's top level, where GitHub draws it as an alert
        self.draw()
        text = self.readme.read_text(encoding="utf-8")
        for eid, fold in (("chess", "<details open>\n<summary><b>♟️ Chess</b></summary>"),
                          ("checkers", "<details>\n<summary><b>🏁 Checkers</b></summary>"),
                          ("connectfour", "<details>\n<summary><b>⚫ Connect Four</b></summary>"),
                          ("tictactoe", "<details>\n<summary><b>❌ Tic-Tac-Toe</b></summary>")):
            with self.subTest(game=eid):
                block = re.search(rf"element:{eid}:start -->\n(.*?)\n<!-- markdown:element:{eid}:end", text,
                                  re.S).group(1)
                self.assertRegex(block, r"^> \[!(TIP|CAUTION)\]\n> [^\n]+\n\n<details")
                self.assertIn(f"\n\n{fold}\n\n<picture>", block)
                self.assertTrue(block.endswith("\n\n</details>"), "the note is the fold's last word")

    def test_a_banner_in_a_folded_section_is_a_plain_quote_and_the_page_checks_clean(self):
        # a README that folds a game itself puts the banner in its fold, where GitHub would show an alert's marker
        # as words
        folds = {"chess": "<details open>\n<summary>Chess</summary>\n\n{}\n\n</details>",
                 "checkers": "<details>\n<summary>Checkers</summary>\n\n{}\n\n</details>"}
        self.readme.write_text("# tannergolden\n\n" + "\n\n".join(folds.get(eid, "{}").format(
            f"<!-- markdown:element:{eid}:start -->\n<!-- markdown:element:{eid}:end -->") for eid in IDS) + "\n",
            encoding="utf-8")
        self.draw()
        text = self.readme.read_text(encoding="utf-8")
        blocks = {eid: re.search(rf"element:{eid}:start -->(.*?)<!-- markdown:element:{eid}:end", text, re.S).group(1)
                  for eid in IDS}
        for eid in ("chess", "checkers"):
            with self.subTest(folded=eid):
                self.assertNotIn("[!", blocks[eid])
                self.assertIn("\n> " + self.games[eid]["prompt"] + "\n", blocks[eid], "the banner, a plain quote")
        for eid in ("connectfour", "tictactoe"):
            with self.subTest(top_level=eid):
                self.assertRegex(blocks[eid], r"\n> \[!(TIP|CAUTION)\]\n> ")
        self.draw()
        self.assertEqual(self.readme.read_text(encoding="utf-8"), text, "and a second run changes nothing")

    def test_a_hall_that_shows_fewer_winners_takes_their_badges_away(self):
        def badges(drawn: dict[str, bytes]) -> list[str]:
            return sorted(name for name in drawn if name.startswith("hall-of-fame-badge-"))

        five = badges(self.draw())
        self.assertEqual(len(five), 2 * 6, "five winners' badges and the leader's still twin, day and dark")
        two = badges(self.draw(hall_of_fame=dict(H.HALL, people=H.HALL["people"][:2])))
        self.assertEqual(two, [name for name in five if re.match(r"hall-of-fame-badge-(1|1-still|2)-", name)])
        self.assertEqual(badges(self.draw(hall_of_fame=H.EMPTY)), [])
        self.assertEqual(badges(self.draw(hall_of_fame=H.HALL)), five, "and they come back with their winners")

    def test_a_game_taken_off_the_page_takes_its_files_and_its_block_away(self):
        self.draw()
        del self.games["checkers"]
        drawn = self.draw()
        self.assertFalse([name for name in drawn if name.startswith("checkers")])
        self.assertFalse(list(self.out.glob("checkers*")))
        self.assertNotIn("markdown:element:checkers", self.readme.read_text(encoding="utf-8"))

    def test_an_old_drawing_goes_and_a_file_put_there_by_hand_stays(self):
        self.draw()
        old = self.out / "chess-hall-day.svg"
        old.write_text("<svg><!--markdown-kit v1 chess-hall day--></svg>", encoding="utf-8")
        (self.out / "badges").mkdir()
        shutil.copy(self.out / "hall-of-fame-badge-5-day.svg", self.out / "badges" / "imvale-day.svg")
        mine = self.out / "my-board.svg"
        mine.write_text("<svg><title>Mine</title></svg>", encoding="utf-8")
        self.draw()
        self.assertFalse(old.exists(), "a file an old board drew is taken away")
        self.assertFalse((self.out / "badges").exists(), "with the folder it leaves empty")
        self.assertTrue(mine.exists(), "a file without the kit's stamp is never touched")


if __name__ == "__main__":
    unittest.main()
