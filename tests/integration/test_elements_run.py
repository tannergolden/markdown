# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The elements through the command line, on a copy of the driftmark specimen, and measured from a real git
history: render, check drift, prune, fill blocks, and take the old kit's markers over."""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import support
from tests.fakes.github import FakeGitHub

from app import cli
from app.parts import elements as M
from app.ports import Ports
from domain.canvas import BUDGET, lint
from infra import files, git, yaml_reader

SPECIMEN = support.ROOT / "tests" / "fixtures" / "driftmark"


def ports(out: io.StringIO, gh=None) -> Ports:
    return Ports(catalogue=support.install(), read_text=files.read_text, parse_yaml=yaml_reader.loads,
                 today=lambda zone: dt.date(2026, 9, 25), write_text=files.write_text, append_text=files.append_text,
                 drawn=files.drawn, prune=files.prune, github=lambda: gh or FakeGitHub({}), git=git.Git,
                 env={"GITHUB_REPOSITORY": "driftmark/driftmark"}, out=out, err=out)


def kit(*argv, gh=None) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main(list(argv), ports(out, gh))
    return code, out.getvalue()


class Specimen(unittest.TestCase):
    """render, check and the README's blocks, on a copy of the specimen."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(SPECIMEN, self.root)
        self.out = self.root / "assets" / "markdown" / "elements"
        self.readme = self.root / "README.md"
        self.settings = self.root / ".github" / "markdown.yaml"

    def tearDown(self):
        self.tmp.cleanup()
        support.install()

    def render(self, *extra):
        return kit("render", "--root", str(self.root), *extra)

    def check(self, *extra):
        return kit("check", "--root", str(self.root), *extra)

    def test_render_then_check_passes_and_the_old_markers_move_over(self):
        code, out = self.render()
        self.assertEqual(code, 0, out)
        self.assertEqual(len(list(self.out.glob("*.svg"))), 24)
        text = self.readme.read_text(encoding="utf-8")
        self.assertNotIn("<!-- elements:", text)
        self.assertEqual(text.count("<!-- markdown:element:"), 18)
        # render keeps no lock, so check is given the measurement: the specimen has none, and draws from its settings.
        (self.root / "empty.json").write_text("{}", encoding="utf-8")
        self.assertEqual(self.check("--from", str(self.root / "empty.json"))[0], 0)

    def test_render_without_a_lock_names_the_page_from_the_repository_it_runs_in(self):
        self.settings.write_text(self.settings.read_text(encoding="utf-8").replace(
            "subject: driftmark/driftmark\n", "mode: repository\n"), encoding="utf-8")
        code, out = self.render()
        self.assertEqual(code, 0, out)
        self.assertIn("the page for driftmark/driftmark (repository)", out)

    def test_render_is_idempotent(self):
        self.render()
        before = {p.name: p.read_bytes() for p in self.out.glob("*.svg")}
        text = self.readme.read_text(encoding="utf-8")
        self.render()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.out.glob("*.svg")})
        self.assertEqual(text, self.readme.read_text(encoding="utf-8"))

    def test_the_page_theme_draws_every_element(self):
        self.render("--input", "theme=blackprint")
        themed = {p.name: p.read_bytes() for p in self.out.glob("*.svg")}
        self.settings.write_text(self.settings.read_text(encoding="utf-8").replace("theme: blueprint", "theme: blackprint"),
                                 encoding="utf-8")
        self.render()
        self.assertEqual(themed, {p.name: p.read_bytes() for p in self.out.glob("*.svg")})
        for p in self.out.glob("*-day.svg"):
            self.assertNotIn("#2F66C6", p.read_text(encoding="utf-8"), p.name)

    def test_a_repository_print_draws_the_elements_and_passes_the_lint(self):
        self.settings.write_text(self.settings.read_text(encoding="utf-8").replace(
            "theme: blueprint", "theme: goldprint\nprints:\n  goldprint: {line: '#B8860B', ink: '#5C4400', sheet: '#7A5B00'}"),
            encoding="utf-8")
        code, out = self.render()
        self.assertEqual(code, 0, out)
        self.assertIn("#B8860B", (self.out / "how-it-runs-day.svg").read_text(encoding="utf-8"))

    def test_check_names_a_stale_file_an_orphan_and_a_stale_block(self):
        self.render()
        empty = self.root / "empty.json"
        empty.write_text("{}", encoding="utf-8")
        (self.out / "how-it-runs-day.svg").write_text("<svg/>", encoding="utf-8")
        code, out = self.check("--from", str(empty))
        self.assertEqual(code, 1)
        self.assertIn("how-it-runs-day.svg (differs)", out)
        self.render()
        orphan = self.out / "gone.svg"
        orphan.write_text("<svg><!--markdown-kit v1 elements gone--></svg>", encoding="utf-8")
        code, out = self.check("--from", str(empty))
        self.assertEqual(code, 1)
        self.assertIn("gone.svg (no longer drawn)", out)
        self.render()
        self.assertFalse(orphan.exists(), "render removes what no element draws")
        text = self.readme.read_text(encoding="utf-8")
        a = text.index("<!-- markdown:element:vitals:start -->") + len("<!-- markdown:element:vitals:start -->")
        self.readme.write_text(text[:a] + "\nstale\n" + text[text.index("<!-- markdown:element:vitals:end -->"):],
                               encoding="utf-8")
        code, out = self.check("--from", str(empty))
        self.assertEqual(code, 1)
        self.assertIn("element:vitals block differs", out)

    def test_blocks_carry_every_variant_in_githubs_order(self):
        self.render()
        text = self.readme.read_text(encoding="utf-8")
        block = text[text.index("<!-- markdown:element:how-it-runs:start -->"):
                     text.index("<!-- markdown:element:how-it-runs:end -->")]
        order = [m.group(1) for m in re.finditer(r'(?:srcset|src)="assets/markdown/elements/([^"]+)"', block)]
        self.assertEqual(order, ["how-it-runs-narrow-dark.svg", "how-it-runs-narrow-day.svg",
                                 "how-it-runs-dark.svg", "how-it-runs-day.svg"])
        half = text[text.index("<!-- markdown:element:contributors:start -->"):
                    text.index("<!-- markdown:element:contributors:end -->")]
        self.assertNotIn("narrow", half, "a half-page element is one size")
        card = text[text.index("<!-- markdown:element:action:start -->"):
                    text.index("<!-- markdown:element:action:end -->")]
        self.assertIn('<a href="https://github.com/driftmark/action">', card)

    def test_a_missing_marker_is_reported_not_silently_skipped(self):
        text = self.readme.read_text(encoding="utf-8")
        a = text.index("<!-- elements:vitals:start -->")
        b = text.index("<!-- elements:vitals:end -->") + len("<!-- elements:vitals:end -->")
        self.readme.write_text(text[:a] + text[b:], encoding="utf-8")
        code, out = self.render()
        self.assertEqual(code, 0)
        self.assertIn("element:vitals: the README has no markers for it yet", out)
        self.assertTrue((self.out / "vitals-day.svg").exists(), "the file is still drawn")

    def test_bad_data_fails_with_a_precise_message(self):
        self.settings.write_text(self.settings.read_text(encoding="utf-8").replace(
            "      - [collector, alerts, PAST THE THRESHOLD]", "      - [collector, alarms, PAST THE THRESHOLD]"),
            encoding="utf-8")
        code, out = self.render()
        self.assertEqual(code, 2)
        self.assertIn("names a box that is not there: alarms", out)


def sh(root: Path, *args: str, when: str = "2026-09-01T12:00:00+00:00") -> str:
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_NAME": "Octo Dev",
           "GIT_AUTHOR_EMAIL": "1+octo-dev@users.noreply.github.com", "GIT_COMMITTER_NAME": "Octo Dev",
           "GIT_COMMITTER_EMAIL": "1+octo-dev@users.noreply.github.com"}
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True, env=env).stdout


class Measured(unittest.TestCase):
    """The measuring path, end to end, on a real repository with a history and tags."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        sh(self.root, "init", "-q", "--initial-branch=main")
        sh(self.root, "config", "commit.gpgsign", "false")
        sh(self.root, "config", "tag.gpgsign", "false")
        for i, (name, text, subject, when) in enumerate((
                ("LICENSE", "MIT\n", "feat(core): \U0001F389 begin", "2026-07-01T12:00:00+00:00"),
                ("src/tool.py", "print('hi')\n" * 40, "feat(tool): \u2728 say hello", "2026-08-10T12:00:00+00:00"),
                (".github/workflows/checks.yml", "jobs:\n  a:\n    steps:\n      - uses: actions/checkout@v4\n",
                 "ci(checks): \U0001F477 check", "2026-09-01T12:00:00+00:00"),
                ("tests/test_tool.py", "pass\n", "test(tool): \u2705 test it", "2026-09-20T12:00:00+00:00"))):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            sh(self.root, "add", name, when=when)
            sh(self.root, "commit", "-q", "-m", subject, when=when)
            if i in (1, 3):
                sh(self.root, "tag", f"v1.{i}.0", when=when)
        self.git = git.Git(self.root).run
        (self.root / "README.md").write_text("# tool\n\n" + "\n\n".join(
            f"<!-- markdown:element:{eid}:start -->\n<!-- markdown:element:{eid}:end -->"
            for eid in ("vitals", "people", "history", "conformance")) + "\n", encoding="utf-8")
        (self.root / ".github" / "markdown.yaml").write_text(
            "mode: repository\nsubject: octo-dev/tool\ntheme: greenprint\nbanners: false\ntrophies: false\nelements:\n"
            "  vitals: {kind: instruments, measure: {count: {tests: 'tests/test_*.py', workflows: '.github/workflows/*'}}}\n"
            "  people: {kind: roster, measure: {}}\n"
            "  history: {kind: milestones, measure: {notable: {v1.1.0: [FIRST RELEASE]}}}\n"
            "  conformance: {kind: certificate, measure: {}, ring_top: CONFORMS, ring_bottom: V1, name: TOOL}\n",
            encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_run_measures_draws_and_then_checks_offline(self):
        gh = FakeGitHub({}, users={})
        code, out = kit("run", "--root", str(self.root), "--today", "2026-09-25", gh=gh)
        self.assertEqual(code, 0, out)
        lk = json.loads((self.root / ".github" / "markdown.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(lk["parts"]["elements"]["measured"]), ["conformance", "history", "people", "vitals"])
        self.assertEqual(lk["parts"]["elements"]["drawn"], ["vitals", "people", "history", "conformance"])
        svg = (self.root / "assets" / "markdown" / "elements" / "vitals-day.svg").read_text(encoding="utf-8")
        self.assertIn("#22773E", svg, "drawn in the greenprint")
        self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])
        self.assertEqual(kit("check", "--root", str(self.root))[0], 0)
        # The lock is enough: a second machine with no git history checks the same bytes.
        shutil.rmtree(self.root / ".git")
        self.assertEqual(kit("check", "--root", str(self.root))[0], 0)

    def test_an_element_taken_out_of_the_settings_takes_its_block_and_files_away(self):
        kit("run", "--root", str(self.root), "--today", "2026-09-25")
        settings = self.root / ".github" / "markdown.yaml"
        settings.write_text("\n".join(line for line in settings.read_text(encoding="utf-8").splitlines()
                                      if not line.startswith("  people")) + "\n", encoding="utf-8")
        code, out = kit("run", "--root", str(self.root), "--today", "2026-09-26")
        self.assertEqual(code, 0, out)
        self.assertNotIn("markdown:element:people", (self.root / "README.md").read_text(encoding="utf-8"))
        self.assertFalse(list((self.root / "assets" / "markdown" / "elements").glob("people-*")))
        self.assertEqual(kit("check", "--root", str(self.root))[0], 0)

    def test_measurements_have_the_shapes_the_elements_want(self):
        h = M.histogram(self.git, weeks=6, today=dt.date(2026, 9, 25))
        self.assertEqual(len(h["bars"]), 6)
        self.assertEqual(sum(n for _, n in h["bars"]), 2, "two commits in the last six weeks")
        m = M.materials(self.git)
        self.assertEqual(m["parts"][0][0], "PYTHON")
        self.assertEqual(m["parts"][-1][0], "OTHER")
        r = M.roster(self.git)
        self.assertEqual([(p["name"], p["handle"], p["n"]) for p in r["people"]], [("OCTO DEV", "@OCTO-DEV", 4)])
        dial = M.days_since_release(self.git, dt.date(2026, 9, 25))
        self.assertEqual((dial["value"], dial["span"]), (5, 30))
        events = M.milestones(self.git, notable={"v1.1.0": ["FIRST RELEASE"]})["events"]
        self.assertEqual([(e["tag"], e["major"], e.get("above")) for e in events],
                         [("V1.1.0", True, ["FIRST RELEASE"]), ("V1.3.0", True, None)])
        rows = {row[0]: row for row in M.checks(self.git)["checks"]}
        self.assertEqual(rows["Licensed"][1:], ["LICENSE", True])
        self.assertEqual(rows["Actions pinned to a tag or a commit"][1:], ["1 of 1 uses:", True])
        self.assertEqual(rows["Conventional commits"][1:], ["4 of 4 subjects", True])

    def test_a_counter_glob_stays_in_its_folder_unless_told_to_cross(self):
        self.assertEqual(M.count(self.git, "HEAD", "*.py"), 0, "no Python at the root: * does not reach into src/")
        self.assertEqual(M.count(self.git, "HEAD", "**.py"), 2)
        self.assertEqual(M.count(self.git, "HEAD", "src/*.py"), 1)

    def test_a_policy_the_owner_serves_for_every_repository_meets_the_check(self):
        rows = {r[0]: r for r in M.checks(self.git)["checks"]}
        self.assertEqual(rows["Security policy"][1:], ["none", False])
        gh = FakeGitHub({})
        gh.rest = lambda path, **params: {"path": "SECURITY.md"} if path.endswith("/.github/contents/SECURITY.md") else None
        self.assertEqual(M.inherited_policy(gh, "octo-dev"), "octo-dev/.github/SECURITY.md")
        rows = {r[0]: r for r in M.checks(self.git, inherited_policy="octo-dev/.github/SECURITY.md")["checks"]}
        self.assertEqual(rows["Security policy"][1:], ["octo-dev/.github/SECURITY.md", True])

    def test_ci_verdict_falls_back_to_the_branch_when_the_commit_is_still_running(self):
        asked = []

        def rest(path, **params):
            asked.append(params)
            if "head_sha" in params:
                return {"workflow_runs": [{"status": "in_progress", "name": "Checks"}]}
            return {"workflow_runs": [
                {"status": "completed", "conclusion": "success", "name": "\U0001F6A6 Checks",
                 "created_at": "2026-09-25T01:00:00Z", "head_sha": "abcdef1234567"},
                {"status": "completed", "conclusion": "failure", "name": "\U0001F6A6 Checks",
                 "created_at": "2026-09-24T01:00:00Z", "head_sha": "0000000000000"},
                {"status": "completed", "conclusion": "failure", "name": "\U0001F3AF Standards Lifecycle",
                 "created_at": "2026-09-25T02:00:00Z", "head_sha": "1111111111111"}]}
        gh = FakeGitHub({})
        gh.rest = rest
        self.assertEqual(M.ci_status(gh, "x/y", "deadbeef", branch="Development"), ("passing", "abcdef1"))
        self.assertEqual(len(asked), 2)
        self.assertEqual(M.ci_status(gh, "x/y", "deadbeef"), (None, None), "no branch to fall back to")

    def test_a_placard_reads_the_repository_it_names(self):
        answers = {"/repos/octo-dev/tool": {"description": "A tool.", "html_url": "https://github.com/octo-dev/tool",
                                           "language": "Python", "stargazers_count": 1284},
                   "/repos/octo-dev/tool/releases/latest": {"tag_name": "v1.3.0"}}
        gh = FakeGitHub({})
        gh.rest = lambda path, **params: answers.get(path)
        self.assertEqual(M.placard(gh, "octo-dev/tool")["cells"],
                         [["Language", "PYTHON"], ["Release", "V1.3.0"], ["Stars", "1,284"]])
        self.assertIsNone(M.placard(gh, "octo-dev/missing"))


if __name__ == "__main__":
    unittest.main()
