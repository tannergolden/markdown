#!/usr/bin/env python3
"""The slot picker in .github/workflows/markdown.yml, run as bash under every event it sees.

The logic lives in the workflow because a reusable workflow runs against the
caller's checkout, where nothing of this repository is on disk. So the test
lifts the script out of the YAML and runs it, rather than copying it here.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "markdown.yml"


def pick(event: str, schedule: str = "", banners: str = "", badges: str = "", trophies: str = "") -> tuple[int, dict, str]:
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    step = next(s for s in doc["jobs"]["slot"]["steps"] if s.get("id") == "pick")
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "out"
        out.write_text("")
        env = dict(os.environ, EVENT=event, SCHEDULE=schedule, BANNERS_AT=banners, BADGES_AT=badges,
                   TROPHIES_AT=trophies, GITHUB_OUTPUT=str(out))
        run = subprocess.run(["bash", "-c", step["run"]], env=env, capture_output=True, text=True)
        got = dict(line.split("=", 1) for line in out.read_text().splitlines() if "=" in line)
        return run.returncode, got, run.stdout + run.stderr


class Slots(unittest.TestCase):
    crons = dict(banners="0 0 * * *", badges="0 8 * * *", trophies="0 16 * * *")

    def test_a_schedule_runs_only_the_kit_whose_cron_fired(self):
        for kit, cron in self.crons.items():
            code, got, _ = pick("schedule", cron, **self.crons)
            self.assertEqual(code, 0)
            self.assertEqual(got, {k: ("true" if k == kit else "false") for k in self.crons}, kit)

    def test_a_manual_run_and_a_pull_request_run_every_kit_the_stub_names(self):
        for event in ("workflow_dispatch", "pull_request", "push"):
            code, got, _ = pick(event, "", **self.crons)
            self.assertEqual(code, 0)
            self.assertEqual(got, {"banners": "true", "badges": "true", "trophies": "true"}, event)

    def test_a_kit_with_no_cron_never_runs(self):
        code, got, _ = pick("workflow_dispatch", "", banners="0 0 * * *")
        self.assertEqual(code, 0)
        self.assertEqual(got, {"banners": "true", "badges": "false", "trophies": "false"})
        code, got, _ = pick("schedule", "0 0 * * *", banners="0 0 * * *")
        self.assertEqual(got["banners"], "true")

    def test_a_cron_that_names_no_kit_fails_loudly(self):
        code, got, log = pick("schedule", "0 12 * * *", **self.crons)
        self.assertEqual(code, 1)
        self.assertIn("::error::", log)
        self.assertIn("0 12 * * *", log)
        self.assertEqual(got, {}, "nothing is written when the run fails")

    def test_the_crons_in_this_repositorys_own_stub_match_its_schedule(self):
        for name in ("own-readme.yml", "own-readme-check.yml"):
            doc = yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"))
            job = next(iter(doc["jobs"].values()))
            named = {job["with"][k] for k in ("banners", "badges", "trophies")}
            self.assertEqual(named, set(self.crons.values()), name)
        own = yaml.safe_load((ROOT / ".github" / "workflows" / "own-readme.yml").read_text(encoding="utf-8"))
        fired = {entry["cron"] for entry in own[True]["schedule"]}
        self.assertEqual(fired, set(self.crons.values()), "on.schedule and with: name the same crons")

    def test_the_slots_are_eight_hours_apart(self):
        hours = sorted(int(c.split()[1]) for c in self.crons.values())
        self.assertEqual([b - a for a, b in zip(hours, hours[1:])], [8, 8])
        self.assertEqual(len({c.split()[0] for c in self.crons.values()}), 1, "the same minute, so the gaps are exact")
        self.assertEqual({c.split()[0] for c in self.crons.values()}, {"0"}, "every slot fires on the hour")


if __name__ == "__main__":
    unittest.main()
