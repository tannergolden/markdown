# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support  # noqa: F401

from domain import readme as R

FRONT = "<!--\ntitle: 'A page'\n-->\n\n# A page\n\nSome words.\n"


def blocks(*names, text="{}"):
    return {n: R.block(n, text.format(n)) for n in names}


class ReadmeTest(unittest.TestCase):
    def test_first_run_places_each_block_where_a_readme_carries_it(self):
        text, unplaced = R.place(FRONT, blocks("footer", "trophies", "badges", "header"))
        self.assertEqual(unplaced, [])
        order = [text.index(R.markers(n)[0]) for n in ("header", "badges", "trophies", "footer")]
        self.assertEqual(order, sorted(order))
        self.assertTrue(text.startswith("<!--\ntitle: 'A page'\n-->\n\n<!-- markdown:header:start -->"))
        self.assertLess(text.index("<!-- markdown:badges:end -->"), text.index("# A page"))
        self.assertGreater(text.index("<!-- markdown:trophies:start -->"), text.index("Some words."))

    def test_a_second_run_changes_nothing(self):
        once, _ = R.place(FRONT, blocks("header", "footer"))
        twice, _ = R.place(once, blocks("header", "footer"))
        self.assertEqual(once, twice)

    def test_only_what_is_between_the_markers_is_rewritten(self):
        once, _ = R.place(FRONT, blocks("header"))
        again, _ = R.place(once, blocks("header", text="new {}"))
        self.assertIn("new header", again)
        self.assertEqual(again.replace("new header", "header"), once)

    def test_a_block_no_longer_wanted_is_taken_out_cleanly(self):
        full, _ = R.place(FRONT, blocks("header", "badges", "footer"))
        text, _ = R.place(full, {"badges": None, "footer": None})
        self.assertNotIn("markdown:badges", text)
        self.assertNotIn("markdown:footer", text)
        self.assertNotIn("\n\n\n", text)
        self.assertTrue(text.endswith("Some words.\n"))

    def test_a_new_block_goes_beside_its_neighbour(self):
        with_ends, _ = R.place(FRONT, blocks("header", "footer"))
        text, _ = R.place(with_ends, blocks("badges", "trophies"))
        self.assertLess(text.index("markdown:header:end"), text.index("markdown:badges:start"))
        self.assertLess(text.index("markdown:trophies:end"), text.index("markdown:footer:start"))

    def test_an_element_goes_only_where_its_markers_stand(self):
        text, unplaced = R.place(FRONT, blocks("element:how-it-fits"))
        self.assertEqual((text, unplaced), (FRONT, ["element:how-it-fits"]))
        marked = FRONT + "\n" + R.block("element:how-it-fits", "") + "\n"
        text, unplaced = R.place(marked, blocks("element:how-it-fits"))
        self.assertEqual(unplaced, [])
        self.assertIn("element:how-it-fits\n<!--", text.replace("<!-- markdown:element:how-it-fits:start -->\n", ""))

    def test_the_old_kits_markers_move_over(self):
        old = ("<!-- banners:header:start -->\nold header\n<!-- banners:header:end -->\n\nText\n\n"
               "<!-- elements:how-it-fits:start -->\nold\n<!-- elements:how-it-fits:end -->\n\n"
               "<!-- trophies:start -->\nold trophies\n<!-- trophies:end -->\n\n"
               "<!-- banners:footer:start -->\nold footer\n<!-- banners:footer:end -->\n")
        text, unplaced = R.place(old, blocks("header", "trophies", "footer", "element:how-it-fits"))
        self.assertEqual(unplaced, [])
        self.assertNotIn("banners:", text)
        self.assertNotIn("trophies:start", text.replace("markdown:trophies:start", ""))
        self.assertNotIn("elements:", text)
        self.assertNotIn("old", text)
        self.assertIn("\n\nText\n\n", text)

    def test_a_start_marker_without_its_end_is_an_error(self):
        with self.assertRaises(R.ReadmeError):
            R.place("<!-- markdown:header:start -->\nno end\n", blocks("header"))

    def test_a_block_name_must_be_plain(self):
        with self.assertRaises(R.ReadmeError):
            R.markers("Header!")

    def test_an_empty_readme_gets_just_its_blocks(self):
        text, _ = R.place("", blocks("header", "footer"))
        self.assertEqual(text, R.block("header", "header") + "\n\n" + R.block("footer", "footer") + "\n")


if __name__ == "__main__":
    unittest.main()
