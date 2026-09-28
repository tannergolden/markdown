# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Measuring the live badges: what each asks GitHub, and what it makes of the answer."""
from __future__ import annotations

import datetime as dt
import unittest

from tests import support
from tests.fakes.github import BOT, FakeGitHub, commit, history_answer

from app.parts import badges as B
from app.parts import banners as measure
from domain.badges import live

support.install()
TODAY = dt.date(2026, 9, 28)


def runs(conclusion):
    return lambda **params: {"workflow_runs": [{"conclusion": conclusion, "head_branch": params.get("branch")}]}


def search(*items):
    return {"items": [{"commit": {"message": message, "committer": {"name": name, "email": email,
                                                                   "date": f"{day}T12:00:00Z"}}}
                      for day, message, name, email in items]}


PERSON = ("Octo Dev", "octo@users.noreply.github.com")


def badge(name, measure_):
    return {"name": name, "label": name.title(), "measure": live.parse(measure_)}


class Workflow(unittest.TestCase):
    def test_the_newest_finished_run_on_the_default_branch(self):
        gh = FakeGitHub({}, paths={"/repos/octo/site": {"default_branch": "trunk"},
                                   "/repos/octo/site/actions/workflows/checks.yml/runs": runs("success")})
        self.assertEqual(B.workflow(gh, "octo/site", "checks.yml", "", []), ("Passing", "green"))
        self.assertEqual(gh.asked[-1], ("/repos/octo/site/actions/workflows/checks.yml/runs",
                                        {"status": "completed", "per_page": 1, "branch": "trunk"}))

    def test_a_named_branch_is_asked_for_directly(self):
        gh = FakeGitHub({}, paths={"/repos/octo/site/actions/workflows/checks.yml/runs": runs("failure")})
        self.assertEqual(B.workflow(gh, "octo/site", "checks.yml", "Development", []), ("Failing", "red"))
        self.assertEqual(len(gh.asked), 1)

    def test_no_run_or_no_access_is_no_data_with_a_note(self):
        gh = FakeGitHub({}, paths={"/repos/octo/site/actions/workflows/checks.yml/runs": {"workflow_runs": []}})
        self.assertEqual(B.workflow(gh, "octo/site", "checks.yml", "main", []), live.NO_DATA)
        notes = []
        self.assertEqual(B.workflow(FakeGitHub({}), "octo/gone", "checks.yml", "", notes), live.NO_DATA)
        self.assertIn("cannot read octo/gone", notes[0])


class LastCommit(unittest.TestCase):
    def test_a_persons_newest_commit_sets_the_kits_and_bots_aside(self):
        gh = FakeGitHub({}, paths={"/search/commits": search(
            ("2026-09-28", "chore(markdown): \U0001FAA7 redraw", *BOT),
            ("2026-09-27", "chore(badges): \U0001F3F7️ re-render badges", *PERSON),
            ("2026-09-10", "feat: a thing\n\nwith a body", *PERSON))})
        self.assertEqual(B.person_commit(gh, "octo", TODAY, []), ("This Month", "yellow"))
        self.assertEqual(gh.asked[0][1]["q"], "author:octo")

    def test_nobody_found_is_no_data(self):
        notes = []
        gh = FakeGitHub({}, paths={"/search/commits": search(("2026-09-28", "chore(trophies): x", *PERSON))})
        self.assertEqual(B.person_commit(gh, "octo", TODAY, notes), live.NO_DATA)
        self.assertIn("none of octo's newest", notes[0])

    def test_a_repositorys_is_read_the_way_the_footer_reads_it(self):
        gh = FakeGitHub({measure.HISTORY: history_answer([[commit("2026-09-27", "chore(markdown): x", *BOT),
                                                            commit("2026-09-26", "fix: y")]])})
        self.assertEqual(B.repository_commit(gh, "octo/site", TODAY, []), ("This Week", "green"))


class Release(unittest.TestCase):
    def test_the_latest_release_and_its_age(self):
        gh = FakeGitHub({}, paths={"/repos/octo/site/releases/latest": {"tag_name": "v2.4.0",
                                                                        "published_at": "2026-01-02T10:00:00Z"}})
        self.assertEqual(B.release(gh, "octo/site", TODAY, []), ("v2.4.0", "yellow"))

    def test_none_yet_and_no_access_are_told_apart(self):
        gh = FakeGitHub({}, paths={"/repos/octo/site": {"default_branch": "main"}})
        self.assertEqual(B.release(gh, "octo/site", TODAY, []), ("No Release", "slate"))
        notes = []
        self.assertEqual(B.release(FakeGitHub({}), "octo/gone", TODAY, notes), live.NO_DATA)
        self.assertTrue(notes)


class Measure(unittest.TestCase):
    def client(self):
        return FakeGitHub({measure.HISTORY: history_answer([[commit("2026-08-01", "docs: z")]])}, paths={
            "/repos/octo/octo": {"default_branch": "main"},
            "/repos/octo/octo/actions/workflows/checks.yml/runs": runs("success"),
            "/repos/octo/tools/actions/workflows/checks.yml/runs": runs("timed_out"),
            "/repos/octo/octo/releases/latest": {"tag_name": "v1", "published_at": "2026-09-01T00:00:00Z"},
            "/search/commits": search(("2026-09-27", "feat: a", *PERSON))})

    def test_what_a_badge_leaves_to_the_page_is_the_pages(self):
        listed = [badge("ci", {"workflow": "checks.yml"}),
                  badge("tools", {"workflow": "checks.yml", "repository": "octo/tools", "branch": "main"}),
                  badge("last", "last-commit"), badge("repo-last", {"last-commit": "octo/octo"}),
                  badge("release", "release"), {"name": "status", "label": "Status", "message": "Active"}]
        got = B.measure(listed, gh=self.client(), mode="profile", subject="octo", here="octo/octo", today=TODAY,
                        notes=[])
        self.assertEqual(got, {"ci": live.value("Passing", "green"), "tools": live.value("Failing", "red"),
                               "last": live.value("This Week", "green"),
                               "repo-last": live.value("Over a Month", "red"),
                               "release": live.value("v1", "green")})

    def test_in_repository_mode_the_last_commit_is_the_repositorys(self):
        gh = self.client()
        got = B.measure([badge("last", "last-commit")], gh=gh, mode="repository", subject="octo/octo",
                        here="octo/octo", today=TODAY, notes=[])
        self.assertEqual(got["last"], live.value("Over a Month", "red"))
        self.assertNotIn("/search/commits", [q for q, _ in gh.asked])

    def test_a_sample_shows_the_best_each_can_say(self):
        self.assertEqual(B.sample([badge("ci", {"workflow": "a.yml"}), badge("release", "release"),
                                   {"name": "s", "label": "S"}]),
                         {"ci": live.value("Passing", "green"), "release": live.value("v1.0.0", "green")})


if __name__ == "__main__":
    unittest.main()
