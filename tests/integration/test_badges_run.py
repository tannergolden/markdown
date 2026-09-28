# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The badges through the command line, on a real git repository: measured, drawn, checked, rethemed,
localized, set from outside, and taken away again."""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import support
from tests.fakes.github import FakeGitHub, commit, history_answer

from app import cli
from app.parts import banners as measure
from app.ports import Ports
from domain.badges import data as BD
from infra import files, git, yaml_reader

SHIELDS = "https://img.shields.io/badge/Status-Active-2EA043?style=for-the-badge"
RAW = "https://raw.githubusercontent.com/octo/site/main/assets/markdown/badges/localized/"
SETTINGS = """\
mode: repository
subject: octo/site
banners: false
trophies: false
badges:
  localize: true
  list:
    # the static row
    - name: status
      label: Status
      message: Active
      icon: pulse
      message_color: green
      link: ./
    - name: posture
      label: Posture
      message: Hardened
      label_color: gold
      message_color: green
    - name: ci
      label: CI
      icon: check
      measure:
        workflow: checks.yml
    - name: last-commit
      label: Last Commit
      icon: commit
      measure: last-commit
"""
ENV = {**os.environ, "GIT_AUTHOR_NAME": "Octo Dev", "GIT_AUTHOR_EMAIL": "octo@example.com",
       "GIT_COMMITTER_NAME": "Octo Dev", "GIT_COMMITTER_EMAIL": "octo@example.com"}


def client(conclusion: str = "success") -> FakeGitHub:
    return FakeGitHub({measure.HISTORY: history_answer([[commit("2026-09-20", "docs: a change")]])}, paths={
        "/repos/octo/site": {"default_branch": "main"},
        "/repos/octo/site/actions/workflows/checks.yml/runs":
            lambda **p: {"workflow_runs": [{"conclusion": conclusion}]}})


def kit(*argv, gh=None) -> tuple[int, str]:
    out = io.StringIO()
    ports = Ports(catalogue=support.install(), read_text=files.read_text, parse_yaml=yaml_reader.loads,
                  today=lambda zone: dt.date(2026, 9, 25), write_text=files.write_text, append_text=files.append_text,
                  drawn=files.drawn, prune=files.prune, github=lambda: gh or client(), git=git.Git,
                  slug=lambda root: git.Git(root).slug(), env={"GITHUB_REPOSITORY": "octo/site"}, out=out, err=out)
    code = cli.main(list(argv), ports)
    return code, out.getvalue()


class Badges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "site"
        (self.root / ".github").mkdir(parents=True)
        (self.root / "docs").mkdir()
        self.settings = self.root / ".github" / "markdown.yaml"
        self.settings.write_text(SETTINGS, encoding="utf-8")
        (self.root / "README.md").write_text("# Site\n\nWords.\n", encoding="utf-8")
        (self.root / "docs" / "guide.md").write_text(f"# Guide\n\n![Status: Active]({SHIELDS})\n", encoding="utf-8")
        self.git("init", "-q", "-b", "main")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "docs: start")
        self.out = self.root / "assets" / "markdown" / "badges"

    def tearDown(self):
        self.tmp.cleanup()
        support.install()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, env=ENV, check=True, capture_output=True)

    def run_kit(self, *extra, gh=None) -> tuple[int, str]:
        return kit("run", "--root", str(self.root), "--commit-file", str(self.root / ".." / "message"), *extra, gh=gh)

    def check(self, *extra) -> tuple[int, str]:
        return kit("check", "--root", str(self.root), *extra)

    def lock(self) -> dict:
        return json.loads((self.root / ".github" / "markdown.lock.json").read_text(encoding="utf-8"))

    def message(self) -> str:
        return (self.root / ".." / "message").read_text(encoding="utf-8")

    def test_a_run_measures_draws_places_localizes_and_checks(self):
        code, out = self.run_kit()
        self.assertEqual(code, 0, out)
        drawn = sorted(p.relative_to(self.out).as_posix() for p in self.out.rglob("*.svg"))
        self.assertEqual(drawn, ["dynamic/ci.svg", "dynamic/last-commit.svg", "dynamic/posture.svg",
                                 "localized/status-active.svg", "static/status.svg"])
        for path in self.out.rglob("*.svg"):
            self.assertEqual(BD.lint(path.read_text(encoding="utf-8")), [], path.name)
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith("<!-- markdown:badges:start -->\n<div align=\"center\">"), readme[:80])
        self.assertIn('alt="CI: Passing"', readme)
        self.assertIn('alt="Last Commit: This Week"', readme)
        self.assertIn("# Site\n\nWords.\n", readme, "the README's own words are kept")
        guide = (self.root / "docs" / "guide.md").read_text(encoding="utf-8")
        self.assertEqual(guide, f"# Guide\n\n![Status: Active]({RAW}status-active.svg)\n")
        record = self.lock()["parts"]["badges"]
        self.assertEqual(record["measured"], {"ci": {"message": "Passing", "state": "green"},
                                              "last-commit": {"message": "This Week", "state": "green"}})
        self.assertEqual((list(record["localized"]), record["branch"]), (["status-active.svg"], "main"))
        self.assertTrue(self.message().startswith("chore(markdown): \U0001F3F7️ redraw the badges\n"),
                        self.message())
        self.assertIn("docs/guide.md", self.message())
        self.assertEqual(self.check(), (0, self.check()[1]))
        self.assertIn("are current", self.check()[1])

    def test_a_badge_that_moved_is_redrawn_and_named_in_the_commit(self):
        self.run_kit()
        before = (self.out / "dynamic" / "ci.svg").read_text(encoding="utf-8")
        code, out = self.run_kit(gh=client("failure"))
        self.assertEqual(code, 0, out)
        self.assertNotEqual(before, (self.out / "dynamic" / "ci.svg").read_text(encoding="utf-8"))
        self.assertIn('alt="CI: Failing"', (self.root / "README.md").read_text(encoding="utf-8"))
        self.assertIn("The live badges moved: CI from Passing to Failing.", self.message())
        self.assertEqual(self.check()[0], 0, "the lock keeps what was measured, so check draws the same")

    def test_a_quiet_day_writes_nothing(self):
        self.run_kit()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore(markdown): draw")
        code, out = self.run_kit()
        self.assertIn("nothing changed", out)

    def test_a_print_theme_draws_every_badge_as_its_plate(self):
        code, out = self.run_kit("--input", "theme=blackprint")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.out / "static" / "status-dark.svg").is_file())
        self.assertNotIn("<text", (self.out / "static" / "status.svg").read_text(encoding="utf-8"))
        self.assertIn("<picture>", (self.root / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(self.check("--input", "theme=blackprint")[0], 0)
        code, out = self.check()
        self.assertEqual(code, 1, "the settings say standard, and the files are plates")
        self.run_kit()
        self.assertFalse((self.out / "static" / "status-dark.svg").exists(), "back in standard, the night file goes")

    def test_check_names_a_badge_drawn_by_hand_and_a_link_left_to_localize(self):
        self.run_kit()
        (self.out / "static" / "status.svg").write_text("<svg/>", encoding="utf-8")
        (self.root / "docs" / "more.md").write_text(f"![again]({SHIELDS.replace('Active', 'Paused')})\n",
                                                    encoding="utf-8")
        self.git("add", "docs/more.md")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("static/status.svg (differs)", out)
        self.assertIn("docs/more.md (shields.io links to localize)", out)

    def test_a_localized_badge_no_document_shows_is_removed(self):
        self.run_kit()
        (self.root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        self.run_kit()
        self.assertFalse((self.out / "localized" / "status-active.svg").exists())
        self.assertNotIn("localized", self.lock()["parts"]["badges"])

    def test_localizing_off_keeps_what_it_drew_and_touches_nothing_new(self):
        self.run_kit()
        self.settings.write_text(SETTINGS.replace("  localize: true\n", ""), encoding="utf-8")
        (self.root / "docs" / "more.md").write_text(f"![again]({SHIELDS.replace('Active', 'Paused')})\n",
                                                    encoding="utf-8")
        self.git("add", "docs/more.md")
        self.run_kit()
        self.assertTrue((self.out / "localized" / "status-active.svg").is_file(), "the guide still shows it")
        self.assertIn("img.shields.io", (self.root / "docs" / "more.md").read_text(encoding="utf-8"))

    def test_set_writes_a_value_into_the_settings_and_the_next_run_draws_it(self):
        code, out = kit("set", "--root", str(self.root), "posture=Degraded:yellow", "status=Paused")
        self.assertEqual(code, 0, out)
        text = self.settings.read_text(encoding="utf-8")
        self.assertIn("    # the static row\n", text)
        self.assertIn("      message: Degraded\n      label_color: gold\n      message_color: yellow\n", text)
        self.run_kit()
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn('alt="Posture: Degraded"', readme)
        self.assertIn('alt="Status: Paused"', readme)

    def test_set_refuses_what_the_settings_would_not_hold(self):
        for spec, why in (("posture=Odd:teal", "in a state"), ("ci=Passing", "measures its own value"),
                          ("nope=x", "no badge named nope")):
            code, out = kit("set", "--root", str(self.root), spec)
            self.assertEqual(code, 2, spec)
            self.assertIn(why, out, spec)
        self.assertEqual(self.settings.read_text(encoding="utf-8"), SETTINGS, "nothing is written")

    def test_badges_turned_off_take_their_block_and_files_away(self):
        self.run_kit()
        self.settings.write_text("mode: repository\nsubject: octo/site\nbanners: false\ntrophies: false\nbadges: false\n",
                                 encoding="utf-8")
        code, out = self.run_kit()
        self.assertEqual(code, 0, out)
        self.assertNotIn("markdown:badges", (self.root / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(sorted(p.name for p in self.out.rglob("*.svg")), ["status-active.svg"],
                         "a localized badge a document still shows is kept")


if __name__ == "__main__":
    unittest.main()
