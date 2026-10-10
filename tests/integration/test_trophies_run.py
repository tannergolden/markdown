# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The trophy case through the command line, on real files: drawn, folded into the lock, checked, taken over
from the trophies kit's lock, and taken away again. A made-up measurement stands in for GitHub."""
from __future__ import annotations

import copy
import datetime as dt
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import support
from tests.fakes.github import FakeGitHub

from app import cli
from app.parts import banners as banners_part
from app.parts import trophies as trophies_part
from app.ports import Ports
from domain.banners import sample as banners_sample
from domain.trophies import plan as P
from domain.trophies import sample
from infra import files, yaml_reader

LOCK = Path(".github") / "markdown.lock.json"


def measurement(**values) -> dict:
    """The profile sample as a run measures it: no weekly change or NEW flags of its own, and `values` moved."""
    m = copy.deepcopy(sample.PROFILE)
    del m["delta"], m["new"]
    m["values"].update(values)
    return m


def run(root: Path, argv: list[str], case: dict | None = None, today: str = "2026-09-25") -> tuple[int, str]:
    out = io.StringIO()

    def measured(gh, section, record, *, mode, subject, today, notes):
        return copy.deepcopy(case or measurement()) | {"owners": {}, "today": today.isoformat()}

    def header(gh, mode, subject, where, *, today):
        return copy.deepcopy(banners_sample.PROFILE) | {"today": today}

    ports = Ports(catalogue=support.install(), read_text=files.read_text, parse_yaml=yaml_reader.loads,
                  today=lambda zone: dt.date.fromisoformat(today), write_text=files.write_text,
                  append_text=files.append_text, drawn=files.drawn, prune=files.prune, remove=files.remove,
                  github=lambda: FakeGitHub({}),
                  env={"GITHUB_REPOSITORY": "octo-dev/octo-dev"}, out=out, err=out)
    with mock.patch.object(trophies_part, "measure", measured), mock.patch.object(banners_part, "measure", header):
        code = cli.main([argv[0], "--root", str(root), *argv[1:]], ports)
    return code, out.getvalue()


class Case(unittest.TestCase):
    settings = "mode: profile\nsubject: octo-dev\nbanners: false\n"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".github").mkdir()
        self.set(self.settings)
        (self.root / "README.md").write_text("# Octo\n\nHello.\n", encoding="utf-8")
        self.msg = self.root / ".." / f"{self.root.name}-message"
        self.out = self.root / "assets" / "trophies"

    def tearDown(self):
        self.tmp.cleanup()
        Path(self.msg).unlink(missing_ok=True)
        support.install()

    def set(self, text: str) -> None:
        (self.root / ".github" / "markdown.yaml").write_text(text, encoding="utf-8")

    def run_kit(self, case: dict | None = None, today: str = "2026-09-25", *extra) -> tuple[int, str]:
        Path(self.msg).unlink(missing_ok=True)
        return run(self.root, ["run", "--commit-file", str(self.msg), *extra], case, today)

    def message(self) -> str:
        return Path(self.msg).read_text(encoding="utf-8") if Path(self.msg).exists() else ""

    def lock(self) -> dict:
        return json.loads((self.root / LOCK).read_text(encoding="utf-8"))

    def readme(self) -> str:
        return (self.root / "README.md").read_text(encoding="utf-8")

    def test_a_first_run_draws_the_case_folds_it_into_the_lock_and_names_what_it_reached(self):
        code, out = self.run_kit()
        self.assertEqual(code, 0, out)
        self.assertIn("trophies 56 of 100 achievements, commits Platinum", out)
        files_ = {p.relative_to(self.out).as_posix() for p in self.out.rglob("*.svg")}
        self.assertEqual(len(files_), 2 * (8 + 2 + 100))
        for p in self.out.rglob("*.svg"):
            self.assertEqual(P.lint(p.read_text(encoding="utf-8")), [], p.name)
        readme = self.readme()
        self.assertIn("# Octo\n\nHello.\n", readme)
        self.assertTrue(readme.rstrip().endswith("<!-- markdown:trophies:end -->"), "a case goes at the foot")
        record = self.lock()["parts"]["trophies"]
        self.assertEqual(set(record), {"reached", "history", "scan", "last"})
        self.assertEqual(record["reached"]["commits"], {"4.0": "2026-09-25"})
        self.assertEqual(record["last"]["values"]["commits"], 5730)
        message = self.message()
        self.assertTrue(message.startswith("chore(markdown): \U0001F3C6 reach "), message)
        self.assertIn("Newly reached: ", message)
        self.assertIn("Newly earned: ", message)
        self.assertIn("Measured octo-dev on 2026-09-25.", message)
        self.assertEqual(run(self.root, ["check"])[0], 0, "the lock keeps what the case is drawn from")

    def test_the_same_measurement_again_changes_nothing(self):
        self.run_kit()
        code, out = self.run_kit()
        self.assertIn("nothing changed", out)
        self.assertEqual(self.message(), "")

    def test_a_week_later_the_cards_show_what_moved_and_the_commit_says_so(self):
        self.run_kit()
        code, out = self.run_kit(measurement(commits=5850), "2026-10-03")
        self.assertEqual(code, 0, out)
        message = self.message()
        self.assertTrue(message.startswith("chore(markdown): \U0001F3C6 refresh the case, commits +120"), message)
        self.assertNotIn("Newly reached", message)
        self.assertIn("up 120 this week", (self.out / "commits.svg").read_text(encoding="utf-8"))

    def test_check_names_a_card_drawn_by_hand_and_a_drifted_block(self):
        self.run_kit()
        (self.out / "commits.svg").write_text("<svg/>", encoding="utf-8")
        code, out = run(self.root, ["check"])
        self.assertEqual(code, 1)
        self.assertIn("trophies/commits.svg (differs)", out)
        self.run_kit()
        text = self.readme()
        (self.root / "README.md").write_text(text.replace("<summary><b>Achievements</b>", "<summary>Mine"),
                                             encoding="utf-8")
        code, out = run(self.root, ["check"])
        self.assertIn("trophies block differs", out)

    def test_the_trophies_kits_lock_is_taken_over(self):
        old = {"version": 1, "reached": {"commits": {"4.0": "2026-03-01"}},
               "history": {"commits": {"2026-09-10": 5600}}, "scan": {"octo-dev/x": {"head": "abc"}}}
        (self.root / ".github" / "trophies.lock.json").write_text(json.dumps(old), encoding="utf-8")
        code, out = self.run_kit()
        self.assertIn("keeps its history from .github/trophies.lock.json, which this run takes away", out)
        self.assertFalse((self.root / ".github" / "trophies.lock.json").exists(), "nothing reads the old lock now")
        record = self.lock()["parts"]["trophies"]
        self.assertEqual(record["reached"]["commits"]["4.0"], "2026-03-01", "the day it was first reached stands")
        self.assertEqual(record["history"]["commits"]["2026-09-10"], 5600)
        self.assertIn("up 130 this week", (self.out / "commits.svg").read_text(encoding="utf-8"))
        self.assertNotIn("Platinum on Commits", self.message(), "nothing it reached before is new")

    def test_an_old_lock_left_behind_after_the_case_moved_over_is_taken_away(self):
        self.run_kit()
        old = self.root / ".github" / "trophies.lock.json"
        old.write_text("{}", encoding="utf-8")
        code, out = self.run_kit()
        self.assertEqual(code, 0, out)
        self.assertFalse(old.exists())
        said = " ".join(self.message().split())
        self.assertIn("took away .github/trophies.lock.json, which the page no longer uses.", said)
        self.assertNotIn("rewrote .github/trophies.lock.json", said)

    def test_block_false_draws_the_files_and_leaves_the_readme_alone(self):
        self.set(self.settings + "trophies:\n  block: false\n")
        self.run_kit()
        self.assertTrue((self.out / "commits.svg").is_file())
        self.assertNotIn("markdown:trophies", self.readme())

    def test_turned_off_the_case_takes_its_files_and_its_block_away(self):
        self.run_kit()
        self.set(self.settings + "trophies: false\n")
        code, out = self.run_kit()
        self.assertEqual(code, 0, out)
        self.assertEqual(list(self.out.rglob("*.svg")), [])
        self.assertNotIn("markdown:trophies", self.readme())

    def test_without_a_measurement_render_keeps_the_case_as_it_is(self):
        self.run_kit()
        lk = self.lock()
        del lk["parts"]["trophies"]
        (self.root / LOCK).write_text(json.dumps(lk), encoding="utf-8")
        before = (self.out / "commits.svg").read_text(encoding="utf-8")
        code, out = run(self.root, ["render"])
        self.assertEqual(code, 0, out)
        self.assertEqual((self.out / "commits.svg").read_text(encoding="utf-8"), before)
        self.assertIn("markdown:trophies:start", self.readme())
        code, out = run(self.root, ["check"])
        self.assertEqual(code, 2)
        self.assertIn("check needs a measurement of the trophies", out)


class WithBanners(Case):
    settings = "mode: profile\nsubject: octo-dev\n"

    def test_the_case_sits_over_the_footer_and_the_commit_leads_with_what_moved(self):
        code, out = self.run_kit()
        self.assertEqual(code, 0, out)
        text = self.readme()
        self.assertLess(text.index("markdown:header:start"), text.index("markdown:trophies:start"))
        self.assertLess(text.index("markdown:trophies:end"), text.index("markdown:footer:start"))
        self.run_kit()
        code, out = self.run_kit(measurement(stars=320), "2026-10-03")
        message = self.message()
        self.assertIn("\U0001F3C6", message.splitlines()[0], "the banners said nothing new; the case did")
        self.assertEqual(message.count("Measured "), 1, "the banners already say when it was measured")

    test_a_first_run_draws_the_case_folds_it_into_the_lock_and_names_what_it_reached = None
    test_a_week_later_the_cards_show_what_moved_and_the_commit_says_so = None
    test_without_a_measurement_render_keeps_the_case_as_it_is = None


if __name__ == "__main__":
    unittest.main()
