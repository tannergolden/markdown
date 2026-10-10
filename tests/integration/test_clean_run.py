# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A run keeps a repository clean. Each part draws into a folder of its own under the page's `out`, `assets` by
default: `banners`, `badges`, `trophies` and `elements`, and never a folder named for the kit. Every file the kit
drew before, or one of the three kits it replaced drew, that nothing draws now is taken away, with the folders that
leaves empty, as a page drawn into `assets/markdown` moves into the parts' folders on its first run. What anyone
made by hand stays, whatever it is called and wherever it is."""
from __future__ import annotations

import re
import unittest

from tests.integration import test_banners_run as B

from domain import KIT
from domain.banners import plan
from infra import files

DRAWN = f"<svg><!--{KIT} v1 drawn--></svg>"
# What the kit drew when every part lived in `assets/markdown`: the banners at its root, the other parts under it.
BEFORE = ("assets/markdown/header-day.svg", "assets/markdown/footer-dark.svg", "assets/markdown/link-issues-day.svg",
          "assets/markdown/badges/static/status.svg", "assets/markdown/trophies/achievements/answer-key.svg",
          "assets/markdown/elements/vitals-day.svg")
# What the banners, badges and trophies kits drew, each with its own stamp, before this kit replaced them.
OLDER = {"assets/banners/link-old-day.svg": "<!--banner-kit v1 F1 dark-->",
         "assets/issues/issue-1-dark.svg": "<!--banner-kit v1 elements v1 placard wide dark-->",
         "assets/releases/release-1-day.svg": "<!--banner-kit v1 elements v1 placard wide day-->",
         "assets/badges/dynamic/last-commit.svg": "<!--badge-kit v2-->",
         "assets/trophies/achievements/answer-key-day.svg": "<!--trophy-kit v2 day-->"}


class Clean(B.Folder):
    def put(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_page_drawn_into_the_old_folder_moves_into_the_parts_folders_and_leaves_nothing_behind(self):
        for rel in BEFORE:
            self.put(rel, DRAWN)
        for rel, stamp in OLDER.items():
            self.put(rel, f"<svg>{stamp}</svg>")
        mine = [self.put("assets/images/logo.svg", "<svg><!-- mine --></svg>"),
                self.put("assets/branding/mark.png", "png"), self.put("assets/banners/hand.svg", "<svg/>")]
        code, out = self.first()
        self.assertEqual(code, 0, out)
        assets = self.root / "assets"
        self.assertTrue((assets / "banners" / "header-day.svg").is_file(), "the banners in their own folder")
        self.assertIn('src="assets/banners/header-day.svg"', (self.root / "README.md").read_text(encoding="utf-8"))
        for rel in (*BEFORE, *OLDER):
            self.assertFalse((self.root / rel).exists(), rel)
        for folder in ("markdown", "issues", "releases"):
            self.assertFalse((assets / folder).exists(), f"assets/{folder} goes with the last of its files")
        self.assertTrue(all(path.exists() for path in mine), "what anyone made by hand stays")
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)
        said = re.search(r"This run rewrote (\d+) images, README\.md and \.github/markdown\.lock\.json\. It took away "
                         r"(\d+) images, which the page no longer uses\.", " ".join(self.msg.read_text(encoding="utf-8").split()))
        self.assertIsNotNone(said, "the commit names what it took away apart from what it drew")
        drawn = files.drawn(assets)
        self.assertEqual((int(said[1]), int(said[2])), (len(drawn), len(BEFORE) + len(OLDER)))

    def test_an_old_folder_that_holds_something_made_by_hand_stays_with_it(self):
        self.put(BEFORE[0], DRAWN)
        hand = self.put("assets/markdown/notes/mine.svg", "<svg><!-- mine --></svg>")
        code, out = self.first()
        self.assertEqual(code, 0, out)
        self.assertFalse((self.root / BEFORE[0]).exists())
        self.assertTrue(hand.exists())

    def test_the_commit_says_what_was_rewritten_and_what_was_taken_away(self):
        self.assertEqual(plan.files_said(["assets/banners/a.svg"]), "This run rewrote 1 image.")
        both = ["assets/banners/a.svg", "assets/banners/b.svg", "README.md", ".github/x.json"]
        self.assertEqual(plan.files_said(both), "This run rewrote 2 images, README.md and .github/x.json.")
        self.assertEqual(plan.files_said(["assets/banners/a.svg", "README.md"], ["assets/banners/a.svg"]),
                         "This run rewrote README.md. It took away 1 image, which the page no longer uses.")
        self.assertEqual(plan.files_said([".github/trophies.lock.json"], [".github/trophies.lock.json"]),
                         "This run took away .github/trophies.lock.json, which the page no longer uses.")

    def test_a_part_turned_off_is_named_as_taken_away(self):
        self.first()
        self.set("theme: blueprint\nbanners: false\n")
        B.run(["run", "--root", str(self.root), "--today", "2026-09-26", "--commit-file", str(self.msg)])
        said = " ".join(self.msg.read_text(encoding="utf-8").split())
        self.assertRegex(said, r"This run rewrote README\.md and \.github/markdown\.lock\.json\. "
                               r"It took away \d+ images, which the page no longer uses\.")

    def test_check_names_what_a_run_would_take_away(self):
        self.first()
        self.put(BEFORE[1], DRAWN)
        self.put("assets/issues/issue-1-dark.svg", "<svg><!--banner-kit v1 elements v1 placard wide dark--></svg>")
        code, out = B.run(["check", "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("assets/markdown/footer-dark.svg (no longer drawn)", out)
        self.assertIn("assets/issues/issue-1-dark.svg (no longer drawn)", out)


if __name__ == "__main__":
    unittest.main()
