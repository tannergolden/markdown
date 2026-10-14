# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""A finished game's countdown never makes a commit of its own: run after run, the page is drawn as of the moment the
lock kept, so a run with nothing else to change changes nothing; and when the page changes for something else, it
is drawn as of that run's moment, its countdown brought up to date with it. `check` draws it as of the same moment,
so a committed page with a countdown on it is never stale for the time passing."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests import support
from tests.integration import test_elements_run as R
from tests.unit.test_elements_countdown import FINISHED

from infra import files

support.install()


def written(element: dict) -> str:
    """The settings as the profile's engines write them, the page's time EST, and the one finished board."""
    lines = ["subject: tannergolden", "theme: blueprint", "timezone: EST", "banners: false", "trophies: false",
             "elements:", "  chess:"]
    lines += [f"    {key}: {json.dumps(value, ensure_ascii=False)}" for key, value in element.items()]
    return "\n".join(lines) + "\n"


class NoCommitOfItsOwn(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "tannergolden"
        (self.root / ".github").mkdir(parents=True)
        self.readme = self.root / "README.md"
        self.readme.write_text("# tannergolden\n\n<!-- markdown:element:chess:start -->\n"
                               "<!-- markdown:element:chess:end -->\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_on(self, day: str, element: dict = FINISHED) -> tuple[str, dict[str, bytes]]:
        (self.root / ".github" / "markdown.yaml").write_text(written(element), encoding="utf-8")
        code, out = R.kit("run", "--root", str(self.root), "--today", day)
        self.assertEqual(code, 0, out)
        self.assertEqual(R.kit("check", "--root", str(self.root))[0], 0, "the committed page is current")
        out_dir = self.root / "assets" / "elements"
        return out, {name: (out_dir / name).read_bytes() for name in files.drawn(out_dir)}

    def asof(self) -> str:
        lock = json.loads((self.root / ".github" / "markdown.lock.json").read_text(encoding="utf-8"))
        return lock["parts"]["elements"]["asof"]

    def test_the_first_drawing_is_as_of_its_run(self):
        self.run_on("2026-10-13")
        self.assertEqual(self.asof(), "2026-10-13T12:00:00Z")

    def test_a_later_run_with_nothing_else_to_change_changes_nothing(self):
        _, first = self.run_on("2026-10-13")
        out, again = self.run_on("2026-10-14")
        self.assertIn("nothing changed", out)
        self.assertEqual(again, first)
        self.assertEqual(self.asof(), "2026-10-13T12:00:00Z", "the countdown stays as of the first drawing")

    def test_a_page_that_changes_for_something_else_is_drawn_as_of_that_run(self):
        _, first = self.run_on("2026-10-13")
        out, changed = self.run_on("2026-10-14", {**FINISHED, "note": "Game 3 is over: the next one comes soon."})
        self.assertNotIn("nothing changed", out)
        self.assertEqual(self.asof(), "2026-10-14T12:00:00Z")
        self.assertEqual(sorted(changed), sorted(first), "the same files, redrawn in place")
        self.assertTrue(any(changed[name] != first[name] for name in first), "the countdown is brought up to date")

    def test_a_board_under_way_keeps_no_moment_that_changes_anything(self):
        under_way = {k: v for k, v in FINISHED.items() if k not in ("result", "next", "next_at")}
        under_way["due"] = "19 Oct"
        _, first = self.run_on("2026-10-13", under_way)
        out, again = self.run_on("2026-10-15", under_way)     # inside the week, before the lock's weekly snapshot
        self.assertIn("nothing changed", out)
        self.assertEqual(again, first)


if __name__ == "__main__":
    unittest.main()
