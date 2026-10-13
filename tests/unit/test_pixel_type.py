# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Both bitmap faces the pixel sets letter in hold every printable ASCII character, or fold it to one they hold.

A character neither face can draw hands the whole file back to the page's own theme. The small capitals once lacked the
semicolon, so a schematic note with one was drawn in the standard look.
"""
from __future__ import annotations

import unittest

from tests import support

from domain.holidays.pixel import type as T

support.install()


class Faces(unittest.TestCase):
    def test_both_faces_letter_every_printable_ascii_character(self):
        for font in T.FONTS:
            for ch in map(chr, range(32, 127)):
                with self.subTest(font=font, ch=ch):
                    T.MISSING.clear()
                    T.fold(ch, font)
                    self.assertFalse(T.MISSING, f"{font} cannot letter {ch!r}")
        T.MISSING.clear()

    def test_the_small_capitals_semicolon_is_the_colons_dot_over_the_commas_tail(self):
        colon, comma, semi = (T.G35[c][1] for c in ":,;")
        self.assertEqual(semi[:2], colon[:2])
        self.assertEqual(semi[3:], comma[3:])

    def test_a_label_with_a_semicolon_and_quotes_is_lettered_whole(self):
        T.MISSING.clear()
        self.assertEqual(T.fold('one theme; "drawn"', "35"), 'ONE THEME; "DRAWN"')
        self.assertFalse(T.MISSING)


if __name__ == "__main__":
    unittest.main()
