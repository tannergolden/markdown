# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import datetime as dt
import unittest

from tests import support  # noqa: F401

from domain import lock as K


class LockTest(unittest.TestCase):
    def test_a_missing_lock_starts_empty(self):
        self.assertEqual(K.normalise(None), K.new())

    def test_another_version_is_refused(self):
        with self.assertRaises(K.LockError):
            K.normalise({"version": 2})

    def test_unknown_fields_are_dropped_and_known_ones_kept(self):
        lock = K.normalise({"version": 1, "snapshot": "2026-09-21", "stray": 1, "parts": {"banners": {"last": {}}}})
        self.assertEqual(lock["snapshot"], "2026-09-21")
        self.assertNotIn("stray", lock)
        self.assertEqual(K.part(lock, "banners"), {"last": {}})

    def test_a_part_gets_an_empty_record_the_first_time(self):
        lock = K.new()
        K.part(lock, "trophies")["history"] = {}
        self.assertEqual(lock["parts"], {"trophies": {"history": {}}})

    def test_the_theme_drawn_is_remembered(self):
        lock = K.new()
        K.remember_drawn(lock, theme="rainbowprint", today=dt.date(2026, 10, 30), holiday="halloween", rainbow="tealprint")
        self.assertEqual(K.drawn(lock), {"theme": "rainbowprint", "holiday": "halloween", "rainbow": "tealprint",
                                         "day": "2026-10-30"})

    def test_a_snapshot_is_due_weekly(self):
        lock = K.new()
        self.assertTrue(K.snapshot_due(lock, dt.date(2026, 9, 28)))
        K.mark_snapshot(lock, dt.date(2026, 9, 28))
        self.assertFalse(K.snapshot_due(lock, dt.date(2026, 10, 4)))
        self.assertTrue(K.snapshot_due(lock, dt.date(2026, 10, 5)))


if __name__ == "__main__":
    unittest.main()
