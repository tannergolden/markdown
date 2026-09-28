# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support

from domain import settings as S


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.catalogue = support.install()

    def tearDown(self):
        support.install()

    def check(self, given=None, inputs=None, **kw):
        return S.validate(given, inputs, catalogue=self.catalogue, **kw)

    def refuses(self, words, given=None, inputs=None):
        with self.assertRaises(S.SettingsError) as caught:
            self.check(given, inputs)
        self.assertIn(words, str(caught.exception))

    def test_nothing_given_is_the_defaults(self):
        cfg = self.check()
        self.assertEqual((cfg["mode"], cfg["theme"], cfg["holidays"], cfg["holiday_days"]), ("auto", "standard", True, 3))
        self.assertTrue(all(cfg[p] is True for p in S.PARTS))

    def test_hyphens_and_underscores_name_the_same_key(self):
        self.assertEqual(self.check({"holiday-days": 5})["holiday_days"], 5)
        self.assertEqual(self.check({"holiday_days": 6})["holiday_days"], 6)

    def test_an_unknown_key_is_named(self):
        self.refuses("unknown key in the settings: colour", {"colour": "red"})

    def test_what_the_stub_sets_wins_over_the_file(self):
        cfg = self.check({"theme": "blueprint", "holiday-days": 4}, {"theme": "blackprint", "holiday-days": "",
                                                                       "holidays": "false"})
        self.assertEqual((cfg["theme"], cfg["holiday_days"], cfg["holidays"]), ("blackprint", 4, False))

    def test_the_stub_can_only_set_its_four_inputs(self):
        self.refuses("the stub has no input 'timezone'", None, {"timezone": "UTC"})

    def test_holiday_days_are_checked(self):
        self.refuses("holiday-days: 8 is outside 3 to 7", {"holiday-days": 8})
        self.refuses("holiday-days: expected a whole number", None, {"holiday-days": "five"})

    def test_the_theme_must_be_one_the_kit_draws(self):
        self.refuses("theme: 'plaid' is not one of standard", {"theme": "plaid"})

    def test_a_repositorys_own_print_can_be_the_theme(self):
        cfg = self.check({"theme": "sunprint", "prints": {"sunprint": {"line": "honey", "ink": "brown", "sheet": "brown"}}})
        self.assertEqual(cfg["theme"], "sunprint")

    def test_a_bad_print_fails_the_settings(self):
        self.refuses("prints: mine: no 'sheet'", {"prints": {"mine": {"line": "navy", "ink": "navy"}}})

    def test_rainbowprint_needs_the_lock(self):
        self.refuses("rainbowprint remembers", {"theme": "rainbowprint", "lock": False})

    def test_mode_subject_timezone_and_paths_are_checked(self):
        self.refuses("mode: 'team'", {"mode": "team"})
        self.refuses("subject: 'not a login!'", {"subject": "not a login!"})
        self.refuses("timezone: 'New York'", {"timezone": "New York"})
        self.refuses("readme: '../README.md'", {"readme": "../README.md"})
        self.assertEqual(self.check({"timezone": "America/New_York"})["timezone"], "America/New_York")

    def test_booleans_must_be_booleans(self):
        self.refuses("holidays: expected true or false", {"holidays": "sometimes"})
        self.refuses("lock: expected true or false", {"lock": 1})

    def test_a_part_is_on_off_or_its_settings(self):
        cfg = self.check({"trophies": False, "badges": [{"name": "x"}]})
        self.assertIs(cfg["trophies"], False)
        self.assertEqual(cfg["badges"], [{"name": "x"}])
        self.refuses("elements: expected true, false, or its settings", {"elements": "yes please"})

    def test_a_part_checks_its_own_section(self):
        seen = []
        cfg = self.check({"banners": {"title": "Hi"}}, parts={"banners": lambda v: seen.append(v) or {**v, "checked": 1}})
        self.assertEqual(seen, [{"title": "Hi"}])
        self.assertEqual(cfg["banners"], {"title": "Hi", "checked": 1})

    def test_mode_is_guessed_from_the_repository(self):
        self.assertEqual(S.guess_mode("tannergolden", "tannergolden", False), "profile")
        self.assertEqual(S.guess_mode("tannergolden", "TannerGolden", False), "profile")
        self.assertEqual(S.guess_mode("acme", ".github", True), "organization")
        self.assertEqual(S.guess_mode("acme", ".github-private", True), "organization")
        self.assertEqual(S.guess_mode("acme", "acme", True), "repository")
        self.assertEqual(S.guess_mode("tannergolden", "markdown", False), "repository")

    def test_an_organizations_page_lives_under_profile(self):
        cfg = self.check()
        self.assertEqual(S.readme_path(cfg, "organization"), "profile/README.md")
        self.assertEqual(S.out_dir(cfg, "organization"), "profile/assets/markdown")
        self.assertEqual(S.readme_path(cfg, "profile"), "README.md")
        self.assertEqual(S.out_dir(self.check({"out": "img"}), "repository"), "img")


if __name__ == "__main__":
    unittest.main()
