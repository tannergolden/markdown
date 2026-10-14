# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""Replays: a finished game on @tannergolden's profile played again move by move on its own board, looping.

The four samples are real games the profile's engine played to their end and wrote out as a replay's facts, one of
each game: Chess, a trap down the e-file, won for GitHub by @hubot's knight; Checkers, 36 moves won by the
house; Pentago, its two ghosts and a turn of the upper right quarter that makes five for GitHub; Tic-Tac, its two
ghosts and 42 marks, won by the house with three boards in a row. Each is drawn by day and by dark in a print, and
held to what a README image is held to: every letter a path, every colour a token, nothing fetched, and its own
budget. Every motion runs on the one loop, so the file plays the game, holds the finale and plays it again."""
from __future__ import annotations

import datetime as dt
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from tests import support

from app import cli
from app.ports import Ports
from domain.canvas import BUDGET, lint
from domain.elements import replay as R
from domain.elements.replay import portrait as P
from domain.elements.replay.sheet import CURTAIN, HOLD, INTRO, TARGET, plan
from infra import files, yaml_reader

support.install()
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "replays"
SAMPLES = {kind: json.loads((FIXTURES / f"{kind}.json").read_text(encoding="utf-8"))
           for kind in ("chess", "checkers", "pentago", "tictac")}
DASHES = ("–", "—", "―")


def grey(w: int = 6, h: int = 4, top: int = 255) -> bytes:
    """A small grey bitmap, as a PGM: a ramp from black at the left to white at the right."""
    head = f"P5\n# a ramp\n{w} {h}\n{top}\n".encode()
    return head + bytes(round(x * top / (w - 1)) for _ in range(h) for x in range(w))


def drawn(kind: str, theme: str = "day", **kw) -> str:
    return R.draw(SAMPLES[kind], kw.pop("tone", "blackprint"), theme, **kw)


class Facts(unittest.TestCase):
    """What a replay is drawn from: the facts the profile's engine writes, checked before anything is drawn."""

    def test_each_sample_game_is_a_replay_the_kit_can_draw(self):
        for kind, f in SAMPLES.items():
            with self.subTest(kind=kind):
                self.assertEqual(R.check(f), [])

    def broken(self, sample: str, **changes) -> list[str]:
        f = json.loads(json.dumps(SAMPLES[sample]))
        f.update(changes)
        return R.check(f)

    def test_facts_of_another_shape_or_game_are_turned_away(self):
        self.assertIn("version", " ".join(self.broken("chess", replay=2)))
        self.assertIn("one of chess, checkers, pentago, tictac", " ".join(self.broken("chess", kind="go")))
        self.assertEqual(R.check(["not", "a", "map"]), ["the facts are a map of the finished game"])

    def test_only_a_won_game_has_a_replay(self):
        self.assertIn("a replay is a game a side won", " ".join(self.broken("pentago", winner=None)))
        self.assertIn("is won by five in a row", " ".join(self.broken("pentago", reason="five for both")))
        self.assertIn("is won by checkmate", " ".join(self.broken("chess", reason="stalemate")))

    def test_the_winning_move_is_the_winners_own(self):
        f = json.loads(json.dumps(SAMPLES["chess"]))
        f["plies"][-1].update(by=None, by_id=None)
        self.assertIn("the last turn is the winning move, the winner's own", " ".join(R.check(f)))
        self.assertIn("the last turn is the winning move", " ".join(self.broken("chess", winner="house")))

    def test_a_ghost_game_opens_with_its_two_ghosts_and_has_no_other(self):
        for kind in ("pentago", "tictac"):
            f = json.loads(json.dumps(SAMPLES[kind]))
            f["plies"] = f["plies"][1:]
            with self.subTest(kind=kind):
                self.assertIn("the first two turns are the ghosts", " ".join(R.check(f)))
        self.assertIn("places", " ".join(self.broken("tictac", places="nobody")))

    def test_each_turn_is_held_to_its_games_own_terms(self):
        cases = (("tictac", {"cell": "j9"}, "a1 to i9"), ("tictac", {"mark": "Z"}, "X, O or G"),
                 ("pentago", {"quarter": "up"}, "quarter turned"), ("checkers", {"path": [5]}, "every square"),
                 ("chess", {"to": "i9"}, "squares the piece moved"), ("chess", {"promotion": "k"}, "promotion"))
        for kind, change, said in cases:
            f = json.loads(json.dumps(SAMPLES[kind]))
            f["plies"][-1].update(change)
            with self.subTest(kind=kind, change=change):
                self.assertIn(said, " ".join(R.check(f)))

    def test_words_and_names_are_plain_text_a_file_can_hold(self):
        f = json.loads(json.dumps(SAMPLES["pentago"]))
        f["plies"][3]["words"] = "<script>"
        self.assertIn("words", " ".join(R.check(f)))
        f = json.loads(json.dumps(SAMPLES["pentago"]))
        f["players"][0]["player"] = "not a login"
        self.assertIn("players", " ".join(R.check(f)))

    def test_a_replay_is_drawn_in_the_pages_print_else_in_blackprint(self):
        self.assertEqual(R.tone_of("blueprint"), "blueprint")
        self.assertEqual(R.tone_of("blackprint"), "blackprint")
        for theme in ("standard", "halloween", "medieval-longship", "rainbowprint", ""):
            with self.subTest(theme=theme):
                self.assertEqual(R.tone_of(theme), R.FALLBACK)


class Drawn(unittest.TestCase):
    """Every game's replay, by day and by dark: a README image held to its own budget, on one loop."""

    @classmethod
    def setUpClass(cls):
        cls.files = {(kind, theme): drawn(kind, theme) for kind in SAMPLES for theme in ("day", "dark")}

    def test_every_replay_is_a_well_formed_image_within_its_budget(self):
        for (kind, theme), svg in self.files.items():
            with self.subTest(kind=kind, theme=theme):
                self.assertEqual(lint(svg, budget=BUDGET["replay"]), [])
                self.assertNotIn("<text", svg)
                self.assertNotIn("<image", svg)
                self.assertFalse(any(d in svg for d in DASHES))

    def test_nothing_is_fetched_every_reference_is_the_files_own(self):
        for (kind, theme), svg in self.files.items():
            with self.subTest(kind=kind, theme=theme):
                self.assertEqual([h for h in re.findall(r'href="([^"]*)"', svg) if not h.startswith("#")], [])

    def test_every_motion_runs_the_whole_loop_and_repeats_forever(self):
        for (kind, theme), svg in self.files.items():
            anims = re.findall(r"<animate(?:Transform)?\b[^>]*>", svg)
            durs = {re.search(r'dur="([^"]+)"', a).group(1) for a in anims}
            with self.subTest(kind=kind, theme=theme):
                self.assertGreater(len(anims), 20)
                self.assertEqual(len(durs), 1, "one loop, one length")
                self.assertTrue(all('repeatCount="indefinite"' in a for a in anims))
                self.assertFalse(any("begin=" in a for a in anims), "nothing waits on a begin of its own")

    def test_every_key_time_runs_from_the_loops_start_to_its_end(self):
        for (kind, theme), svg in self.files.items():
            for times in re.findall(r'keyTimes="([^"]+)"', svg):
                ks = [float(k) for k in times.split(";")]
                with self.subTest(kind=kind, theme=theme):
                    self.assertEqual((ks[0], ks[-1]), (0.0, 1.0))
                    self.assertEqual(ks, sorted(ks))

    def test_the_same_facts_draw_the_same_bytes(self):
        for kind in SAMPLES:
            with self.subTest(kind=kind):
                self.assertEqual(drawn(kind), self.files[(kind, "day")])

    def test_day_and_dark_are_two_looks_of_one_replay(self):
        for kind in SAMPLES:
            day, dark = self.files[(kind, "day")], self.files[(kind, "dark")]
            with self.subTest(kind=kind):
                self.assertNotEqual(day, dark)
                self.assertEqual(re.search(r'dur="([^"]+)"', day).group(1), re.search(r'dur="([^"]+)"', dark).group(1))

    def test_the_title_names_the_game_its_winner_and_the_winning_move(self):
        self.assertIn("Replay of Chess game 1: @hubot wins with 8... Nf3#", self.files[("chess", "day")])
        self.assertIn("Replay of Tic-Tac game 1: @tannergolden wins with 21... Xc3#", self.files[("tictac", "day")])
        self.assertIn("@octocat wins by five in a row", self.files[("pentago", "day")])

    def test_a_print_tone_is_kept_and_any_other_theme_drawn_in_blackprint(self):
        self.assertNotEqual(drawn("pentago", tone="blueprint"), self.files[("pentago", "day")])
        self.assertEqual(drawn("pentago", tone="halloween"), self.files[("pentago", "day")])

    def test_a_long_game_plays_its_moves_quicker_and_its_last_two_at_the_readmes_tempo(self):
        for kind, f in SAMPLES.items():
            game = R.GAMES[kind][0]
            durations = game.durations(f["plies"])
            pl = plan(durations)
            raw = sum(m + r for m, r in durations)
            with self.subTest(kind=kind):
                self.assertEqual([b.k for b in pl.beats[-2:]], [1.0, 1.0])
                self.assertLessEqual(pl.finale - INTRO, max(TARGET, 0) + sum(m + r for m, r in durations[-2:]) + 1e-6)
                self.assertAlmostEqual(pl.total, pl.finale + HOLD + CURTAIN)
                if raw <= TARGET:
                    self.assertTrue(all(b.k == 1.0 for b in pl.beats))


class Faces(unittest.TestCase):
    """Each player as a halftone of their avatar, from a small grey bitmap; their initials without one; the Arbiter's
    scales; and an account that is gone, an empty dial with no name."""

    def test_a_pgm_reads_as_its_grey_levels_and_anything_else_as_none(self):
        grid = P.read(grey())
        self.assertEqual((len(grid), len(grid[0])), (4, 6))
        self.assertEqual((grid[0][0], grid[0][-1]), (0, 255))
        self.assertEqual(P.read(b"P2\n2 1\n15\n0 15\n"), [[0, 255]])
        self.assertIsNone(P.read(b"P5\n2 2\n1023\n" + b"\x00" * 7), "two bytes a level, one short")
        self.assertEqual(P.read(b"P5\n1 1\n1023\n\x03\xff"), [[255]])
        for junk in (b"", b"PNG", b"P5\n0 0\n255\n", b"P5\n9999 2\n255\n" + b"\0" * 64, b"\x89PNG\r\n"):
            with self.subTest(junk=junk[:8]):
                self.assertIsNone(P.read(junk))

    def test_a_player_with_a_bitmap_is_drawn_in_dots_and_without_one_by_their_initials(self):
        f = SAMPLES["pentago"]
        bare = R.draw(f, "blackprint", "day")
        faces = {p["player_id"]: P.read(grey(12, 12)) for p in f["players"]}
        with_faces = R.draw(f, "blackprint", "day", faces)
        self.assertNotIn("h0", bare.split("<defs>")[1].split("</defs>")[0])
        self.assertIn('stroke-linecap="round"><path d="M', with_faces)
        self.assertLess(len(bare), len(with_faces))

    def test_an_account_that_is_gone_leaves_no_name_and_no_face_in_the_file(self):
        f = SAMPLES["pentago"]
        gone = next(p for p in f["players"] if p["player_id"] != f["by_id"])
        faces = {p["player_id"]: P.read(grey(12, 12)) for p in f["players"]}
        kept = R.draw(f, "blackprint", "day", faces)
        lost = R.draw(f, "blackprint", "day", faces, frozenset({gone["player_id"]}))
        self.assertNotEqual(kept, lost)
        self.assertEqual(lint(lost, budget=BUDGET["replay"]), [])
        self.assertIn('stroke-dasharray="3 2.2"', lost)

    def test_the_initials_of_a_login_are_its_first_two_letters_or_digits(self):
        self.assertEqual(P.initials("octocat"), "OC")
        self.assertEqual(P.initials("-x"), "X")
        self.assertEqual(P.initials("9-lives"), "9L")


class Command(unittest.TestCase):
    """The kit's `replay` command, as tannergolden/play's Replay workflow runs it."""

    def run_kit(self, *argv) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        ports = Ports(catalogue=support.install(), read_text=files.read_text, parse_yaml=yaml_reader.loads,
                      today=lambda zone: dt.date(2026, 10, 13), write_text=files.write_text, out=out, err=err)
        return cli.main(list(argv), ports), out.getvalue(), err.getvalue()

    def test_it_writes_a_day_and_a_dark_file_named_for_the_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            faces = Path(tmp) / "faces"
            faces.mkdir()
            (faces / f"{SAMPLES['chess']['by_id']}.pgm").write_bytes(grey(12, 12))
            (faces / "not-an-id.pgm").write_bytes(grey())
            code, out, _ = self.run_kit("replay", str(FIXTURES / "chess.json"), "--out", tmp, "--faces", str(faces))
            self.assertEqual(code, 0)
            self.assertEqual(sorted(p.name for p in Path(tmp).glob("*.svg")), ["game-1-dark.svg", "game-1-day.svg"])
            self.assertIn("game-1-day.svg", out)

    def test_bad_facts_are_turned_away_with_the_reason_and_draw_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({**SAMPLES["chess"], "reason": "stalemate"}), encoding="utf-8")
            code, _, err = self.run_kit("replay", str(bad), "--out", tmp)
            self.assertEqual(code, 2)
            self.assertIn("is won by checkmate", err)
            self.assertEqual(list(Path(tmp).glob("*.svg")), [])
            code, _, err = self.run_kit("replay", str(Path(tmp) / "missing.json"), "--out", tmp)
            self.assertEqual(code, 2)
            self.assertIn("no such file", err)

    def test_a_gone_list_that_is_not_account_ids_is_turned_away(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = self.run_kit("replay", str(FIXTURES / "chess.json"), "--out", tmp, "--gone", "octocat")
            self.assertEqual(code, 2)
            self.assertIn("account IDs", err)


if __name__ == "__main__":
    unittest.main()
