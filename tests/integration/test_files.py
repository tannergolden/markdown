# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import tempfile
import unittest
from pathlib import Path

from tests import support  # noqa: F401

from domain import KIT
from infra import files


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_file_is_written_only_when_it_changes(self):
        path = self.root / "a" / "b.txt"
        self.assertTrue(files.write_text(path, "one\n"))
        stamp = path.stat().st_mtime_ns
        self.assertFalse(files.write_text(path, "one\n"))
        self.assertEqual(path.stat().st_mtime_ns, stamp)
        self.assertTrue(files.write_text(path, "two\n"))
        self.assertEqual(files.read_text(path), "two\n")

    def test_no_temporary_file_is_left_behind(self):
        files.write_text(self.root / "x.svg", "<svg/>")
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["x.svg"])

    def test_line_endings_are_kept_as_given(self):
        files.write_text(self.root / "x.txt", "a\nb\n")
        self.assertEqual((self.root / "x.txt").read_bytes(), b"a\nb\n")

    def test_json_is_written_sorted_with_a_final_newline(self):
        files.write_json(self.root / "l.json", {"b": 1, "a": "é"})
        self.assertEqual(files.read_text(self.root / "l.json"), '{\n "a": "é",\n "b": 1\n}\n')
        self.assertEqual(files.read_json(self.root / "l.json"), {"a": "é", "b": 1})
        self.assertIsNone(files.read_json(self.root / "missing.json"))

    def test_prune_deletes_only_what_the_kit_drew(self):
        out = self.root / "assets"
        files.write_text(out / "keep.svg", f"<svg><!--{KIT} v1 x--></svg>")
        files.write_text(out / "old.svg", f"<svg><!--{KIT} v1 x--></svg>")
        files.write_text(out / "deep" / "old.svg", f"<svg><!--{KIT} v1 x--></svg>")
        files.write_text(out / "hand.svg", "<svg><!-- drawn by hand --></svg>")
        gone = files.prune(out, {"keep.svg"})
        self.assertEqual(gone, ["deep/old.svg", "old.svg"])
        self.assertEqual(sorted(p.name for p in out.rglob("*.svg")), ["hand.svg", "keep.svg"])

    def test_remove_says_whether_anything_went(self):
        files.write_text(self.root / "x", "")
        self.assertTrue(files.remove(self.root / "x"))
        self.assertFalse(files.remove(self.root / "x"))


if __name__ == "__main__":
    unittest.main()
