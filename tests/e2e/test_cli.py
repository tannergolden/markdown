# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The kit as a person runs it: `python3 src/markdown-kit.py <command>`, in a fresh process."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support


def kit(*args, cwd=None):
    env = {k: v for k, v in os.environ.items() if k not in ("MARKDOWN_TOKEN", "GITHUB_TOKEN")}
    return subprocess.run([sys.executable, str(support.LAUNCHER), *args], cwd=cwd, capture_output=True, text=True,
                          env=env, timeout=120)


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_version(self):
        done = kit("version")
        self.assertEqual((done.returncode, done.stdout), (0, "markdown-kit 1\n"))

    def test_settings_with_no_file_are_the_defaults(self):
        done = kit("settings", "--root", str(self.root))
        self.assertEqual(done.returncode, 0, done.stderr)
        cfg = json.loads(done.stdout)
        self.assertEqual((cfg["theme"], cfg["holidays"], cfg["holiday-days"]), ("standard", True, 3))

    def test_settings_read_the_file_and_the_stub_wins(self):
        (self.root / ".github").mkdir()
        (self.root / ".github" / "markdown.yaml").write_text(
            "mode: profile\ntheme: blueprint\nholiday-days: 5\ntimezone: America/New_York\n"
            "banners:\n  motto: Built to be rebuilt.\ntrophies: false\n", encoding="utf-8")
        done = kit("settings", "--root", str(self.root), "--input", "theme=blackprint", "--input", "holidays=")
        self.assertEqual(done.returncode, 0, done.stderr)
        cfg = json.loads(done.stdout)
        self.assertEqual((cfg["mode"], cfg["theme"], cfg["holiday-days"], cfg["trophies"]), ("profile", "blackprint", 5, False))
        # The banners check their own section and fill in its defaults.
        self.assertEqual((cfg["banners"]["motto"], cfg["banners"]["header"]), ("Built to be rebuilt.", "section"))

    def test_a_bad_setting_exits_2_naming_it(self):
        (self.root / ".github").mkdir()
        (self.root / ".github" / "markdown.yml").write_text("holiday-days: 9\n", encoding="utf-8")
        done = kit("settings", "--root", str(self.root))
        self.assertEqual(done.returncode, 2)
        self.assertEqual(done.stderr.strip(), "markdown-kit: holiday-days: 9 is outside 3 to 7")

    def test_bad_yaml_names_the_file_and_the_line(self):
        (self.root / ".github").mkdir()
        (self.root / ".github" / "markdown.yaml").write_text("theme: a\ntheme: b\n", encoding="utf-8")
        done = kit("settings", "--root", str(self.root))
        self.assertEqual(done.returncode, 2)
        self.assertIn(".github/markdown.yaml: line 2: 'theme' is given twice", done.stderr)

    def test_two_settings_files_are_one_too_many(self):
        (self.root / ".github").mkdir()
        for name in ("markdown.yaml", "markdown.yml"):
            (self.root / ".github" / name).write_text("theme: standard\n", encoding="utf-8")
        done = kit("settings", "--root", str(self.root))
        self.assertEqual(done.returncode, 2)
        self.assertIn("keep one", done.stderr)

    def test_holidays_on_a_given_day(self):
        done = kit("holidays", "--today", "2026-10-30")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(done.stdout.startswith("Fri Oct 30, 2026: Halloween's set is up\n"))

    def test_holidays_in_a_year(self):
        done = kit("holidays", "--year", "2026", "--days", "7")
        lines = done.stdout.splitlines()
        self.assertEqual(len(lines), 7)
        self.assertIn("Wed Oct 28 to Tue Nov 03, 2026  (7 days)", lines[4])
        self.assertIn("(3 days)", lines[0])

    def test_holiday_days_out_of_range_exits_2(self):
        done = kit("holidays", "--days", "2")
        self.assertEqual(done.returncode, 2)

    def test_palette_and_icons_list_64_each(self):
        self.assertEqual(len(kit("palette").stdout.splitlines()), 64)
        self.assertEqual(len(kit("icons").stdout.splitlines()), 64)

    def test_an_unknown_command_is_a_usage_error(self):
        self.assertEqual(kit("draw-everything").returncode, 2)


if __name__ == "__main__":
    unittest.main()
