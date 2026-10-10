# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support  # noqa: F401

from domain.history import automated


class HistoryTest(unittest.TestCase):
    def test_a_person_s_commit_counts(self):
        self.assertFalse(automated("docs(readme): 📝 say hello", "Tanner Golden", "tanner@example.com"))

    def test_this_kit_s_refresh_and_the_old_kits_are_set_aside(self):
        for scope in ("markdown", "banners", "badges", "trophies", "elements"):
            self.assertTrue(automated(f"chore({scope}): 🎨 redraw", "Tanner Golden", "tanner@example.com"), scope)

    def test_another_chore_counts(self):
        self.assertFalse(automated("chore(deps): bump", "Tanner Golden", "tanner@example.com"))

    def test_anything_a_bot_committed_is_set_aside(self):
        self.assertTrue(automated("docs: x", "github-actions[bot]", "x@example.com"))
        self.assertTrue(automated("docs: x", "Someone", "49699333+dependabot[bot]@users.noreply.github.com"))


if __name__ == "__main__":
    unittest.main()
