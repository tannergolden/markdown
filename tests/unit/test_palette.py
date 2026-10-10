# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support  # noqa: F401  (puts src/ on the path)

from domain import palette as P


class PaletteTest(unittest.TestCase):
    def test_holds_64_tokens_and_64_icons(self):
        self.assertEqual(len(P.PALETTE), 64)
        self.assertEqual(len(P.ICONS), 64)

    def test_every_token_is_a_distinct_hex(self):
        for name, value in P.PALETTE.items():
            self.assertRegex(value, r"^#[0-9A-F]{6}$", name)
        self.assertEqual(len(set(P.PALETTE.values())), 64)

    def test_hexof_reads_a_token_or_passes_a_hex_through(self):
        self.assertEqual(P.hexof("cobalt"), "#2F66C6")
        self.assertEqual(P.hexof("#abcdef"), "#ABCDEF")
        with self.assertRaises(KeyError):
            P.hexof("chartreuse")

    def test_contrast_matches_wcag(self):
        self.assertAlmostEqual(P.contrast("white", "black"), 21.0, places=2)
        self.assertAlmostEqual(P.contrast("black", "black"), 1.0, places=2)
        self.assertAlmostEqual(P.contrast("white", "magenta"), 4.66, places=2)

    def test_letters_on_keep_four_and_a_half_to_one(self):
        for name in P.PALETTE:
            letters = P.letters_on(name)
            if letters == "white":
                self.assertGreaterEqual(P.contrast("white", name), P.AA, name)
            else:
                self.assertLess(P.contrast("white", name), P.AA, name)

    def test_gold_and_green_take_black_letters(self):
        self.assertEqual(P.letters_on("gold"), "black")
        self.assertEqual(P.letters_on("green"), "black")
        self.assertEqual(P.letters_on("cobalt"), "white")

    def test_is_colour_accepts_tokens_and_hex_only(self):
        self.assertTrue(P.is_colour("navy"))
        self.assertTrue(P.is_colour("#123456"))
        self.assertFalse(P.is_colour("#12345"))
        self.assertFalse(P.is_colour("navyblue"))
        self.assertFalse(P.is_colour(3))


if __name__ == "__main__":
    unittest.main()
