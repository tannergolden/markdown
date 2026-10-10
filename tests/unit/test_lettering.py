# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support

from domain import lettering as L


class LetteringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.install()

    def test_every_face_is_loaded(self):
        self.assertEqual(set(L.fonts()), {"serif", "meta", "num", "mono", "sans", "sans-bold"})

    def test_the_sans_faces_letter_whatever_another_face_can(self):
        drawn = set().union(*(set(L.fonts()[f]["g"]) for f in ("serif", "meta", "num", "mono")))
        for face in ("sans", "sans-bold"):
            self.assertEqual(L.missing("".join(sorted(drawn)), face), "", face)

    def test_prefixes_are_not_hex_digits(self):
        for face, prefix in L.PREFIX.items():
            self.assertNotIn(prefix, "abcdefABCDEF0123456789", face)

    def test_width_grows_with_size_and_spacing(self):
        base = L.width("README", "meta", 12)
        self.assertGreater(base, 0)
        self.assertAlmostEqual(L.width("README", "meta", 24), base * 2, places=6)
        self.assertAlmostEqual(L.width("README", "meta", 12, ls=1), base + 5, places=6)

    def test_an_unknown_character_is_reported_not_drawn(self):
        self.assertEqual(L.missing("a☃b☃", "meta"), "☃")

    def test_wrap_splits_evenly_rather_than_greedily(self):
        lines = L.wrap("one two three four five six", "meta", 12, L.width("one two three four", "meta", 12))
        self.assertEqual(len(lines), 2)
        widths = [L.width(line, "meta", 12) for line in lines]
        self.assertLess(max(widths) - min(widths), L.width("three", "meta", 12))

    def test_wrap_gives_none_when_rows_are_not_enough(self):
        self.assertIsNone(L.wrap("a b c d", "meta", 12, L.width("a", "meta", 12), rows=2))

    def test_flow_shrinks_before_it_gives_up(self):
        size, lines = L.flow("a long title that will not fit", "meta", 20, 10, L.width("a long title", "meta", 14), rows=3)
        self.assertLessEqual(size, 20)
        self.assertLessEqual(len(lines), 3)

    def test_fx_rounds_the_same_way_every_time(self):
        self.assertEqual(L.fx(1.2346, 3), "1.235")
        self.assertEqual(L.fx(2.0, 3), "2")
        self.assertEqual(L.fx(0.5, 3), "0.5")
        self.assertEqual(L.fx(-0.06, 1), "-0.1")
        self.assertEqual(L.fx(-0.04, 1), "0")
        self.assertEqual(L.f1(10.04), "10")

    def test_each_glyph_is_embedded_once(self):
        lt = L.Lettering()
        lt.text("AAA", face="meta", size=12, fill="#000000")
        lt.text("A", face="meta", size=20, fill="#000000")
        self.assertEqual(lt.defs().count('id="m65"'), 1)

    def test_anchor_middle_centres_the_run(self):
        lt = L.Lettering()
        run = lt.text("AB", face="meta", size=10, x=100, anchor="middle", fill=None)
        x0 = 100 - L.width("AB", "meta", 10) / 2
        self.assertIn(f"translate({L.f1(x0)} 0)", run)

    def test_a_later_table_never_overrides_a_glyph(self):
        first = {"meta": {"upem": 1000, "cap": 700, "g": {"A": ["M0 0", 500]}}}
        second = {"meta": {"upem": 1000, "cap": 700, "g": {"A": ["M1 1", 900], "B": ["M2 2", 600]}}}
        try:
            merged = L.use(first, second)
            self.assertEqual(merged["meta"]["g"]["A"], ["M0 0", 500])
            self.assertEqual(merged["meta"]["g"]["B"], ["M2 2", 600])
        finally:
            support.install()


if __name__ == "__main__":
    unittest.main()
