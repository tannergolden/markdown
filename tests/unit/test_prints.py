# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support

from domain import prints
from domain.canvas import BUDGET, Canvas, lint


class PrintsTest(unittest.TestCase):
    def setUp(self):
        self.catalogue = support.install()

    def tearDown(self):
        support.install()

    def test_standard_is_the_default_and_comes_first(self):
        self.assertEqual(prints.DEFAULT_THEME, "standard")
        self.assertEqual(prints.themes()[0], "standard")
        self.assertEqual(prints.themes()[-1], "rainbowprint")

    def test_the_kit_draws_eleven_prints(self):
        self.assertEqual(len(prints.BUILTIN), 11)
        self.assertIn("blueprint", prints.themes())
        self.assertIn("blackprint", prints.themes())

    def test_a_repository_adds_its_own_print(self):
        added = prints.use(self.catalogue, {"sunprint": {"line": "honey", "ink": "brown", "sheet": "#123456"}})
        self.assertEqual(added, ("sunprint",))
        self.assertTrue(prints.is_theme("sunprint"))
        self.assertEqual(prints.PRINTS["sunprint"]["label"], "Sunprint")
        # A colour the repository declared passes the lint like a token.
        cv = Canvas(10, 10, title="t", desc="d", stamp="s")
        cv.add('<rect fill="#123456"/>')
        self.assertEqual(lint(cv.svg(), budget=BUDGET["link"]), [])

    def test_a_second_use_forgets_the_prints_of_the_first_repository(self):
        prints.use(self.catalogue, {"sunprint": {"line": "honey", "ink": "brown", "sheet": "#123456"}})
        prints.use(self.catalogue)
        self.assertFalse(prints.is_theme("sunprint"))

    def test_a_bad_print_is_refused_with_every_problem_named(self):
        with self.assertRaises(prints.PrintError) as caught:
            prints.use(self.catalogue, {"blueprint": {}, "Bad Name": {}, "mine": {"line": "nope", "size": 3}})
        message = str(caught.exception)
        self.assertIn("blueprint: the kit already draws a theme by that name", message)
        self.assertIn("a print's name is lowercase", message)
        self.assertIn("mine: 'size' is not a field", message)
        self.assertIn("mine: no 'ink'", message)
        self.assertIn("mine: line 'nope' is neither a palette token nor #RRGGBB", message)

    def test_standard_cannot_be_redefined(self):
        self.assertTrue(prints.errors("standard", {"line": "navy", "ink": "navy", "sheet": "navy"}))

    def test_rainbowprint_walks_the_spectrum_and_wraps(self):
        self.assertEqual(prints.rainbow_after(None), "redprint")
        self.assertEqual(prints.rainbow_after("redprint"), "orangeprint")
        self.assertEqual(prints.rainbow_after("pinkprint"), "redprint")

    def test_colours_by_day_and_by_night(self):
        day = prints.colours("blueprint", {"dark": False})
        night = prints.colours("blueprint", {"dark": True})
        self.assertEqual((day["line"], day["ink"], day["paper"]), ("cobalt", "navy", "white"))
        self.assertEqual((night["line"], night["paper"]), ("white", "navy"))
        self.assertEqual(prints.colours("yellowprint", {"dark": True})["ink"], "black")


if __name__ == "__main__":
    unittest.main()
