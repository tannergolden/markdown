# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import datetime as dt
import unittest
from unittest import mock

from tests import support  # noqa: F401

from domain import holidays as H

D = dt.date


class HolidaysTest(unittest.TestCase):
    def test_seven_holidays_in_calendar_order(self):
        self.assertEqual(H.KEYS, ("new-years-day", "valentines-day", "juneteenth", "independence-day", "halloween",
                                  "thanksgiving", "christmas"))

    def test_thanksgiving_is_the_fourth_thursday_of_november(self):
        for year, day in ((2024, 28), (2025, 27), (2026, 26), (2027, 25), (2028, 23), (2029, 22)):
            self.assertEqual(H.window("thanksgiving", year).day, D(year, 11, day))

    def test_windows_centre_with_the_odd_day_before(self):
        for days, before, after in ((3, 1, 1), (4, 2, 1), (5, 2, 2), (6, 3, 2), (7, 3, 3)):
            w = H.window("halloween", 2026, days)
            self.assertEqual((w.day - w.start).days, before, days)
            self.assertEqual((w.end - w.day).days, after, days)
            self.assertEqual(w.days, days)

    def test_new_years_day_always_runs_three_days(self):
        for days in range(3, 8):
            w = H.window("new-years-day", 2027, days)
            self.assertEqual((w.start, w.end), (D(2026, 12, 31), D(2027, 1, 2)), days)

    def test_holiday_days_must_be_three_to_seven(self):
        for bad in (2, 8, 0, "5", 5.0, True):
            with self.assertRaises(H.HolidayError):
                H.check_days(bad)

    def test_no_two_windows_ever_overlap(self):
        for days in range(3, 8):
            for year in range(1950, 2151):
                ws = H.windows(year, days)
                for a, b in zip(ws, ws[1:]):
                    self.assertLess(a.end, b.start, (year, days, a.key, b.key))
                    self.assertIn(a.day, a)

    def test_trimming_keeps_each_holiday_inside_its_window(self):
        # Two made-up holidays four days apart, at seven days each, meet between them.
        made_up = (("a", "A", lambda y: D(y, 3, 1)), ("b", "B", lambda y: D(y, 3, 5)))
        with mock.patch.object(H, "HOLIDAYS", made_up), mock.patch.object(H, "KEYS", ("a", "b")):
            a, b = [w for w in H.windows(2026, 7) if w.day.year == 2026]
        self.assertLess(a.end, b.start)
        self.assertIn(a.day, a)
        self.assertIn(b.day, b)
        self.assertEqual((a.end, b.start), (D(2026, 3, 2), D(2026, 3, 3)))

    def test_active_finds_the_set_on_its_edges_and_not_outside(self):
        self.assertIsNone(H.active(D(2026, 10, 29), 3))
        self.assertEqual(H.active(D(2026, 10, 30), 3).key, "halloween")
        self.assertEqual(H.active(D(2026, 11, 1), 3).key, "halloween")
        self.assertIsNone(H.active(D(2026, 11, 2), 3))
        self.assertEqual(H.active(D(2026, 10, 28), 7).key, "halloween")

    def test_new_years_window_spans_the_year_boundary(self):
        self.assertEqual(H.active(D(2026, 12, 31)).day, D(2027, 1, 1))
        self.assertEqual(H.active(D(2027, 1, 2)).day, D(2027, 1, 1))
        self.assertIsNone(H.active(D(2027, 1, 3)))

    def test_turned_off_means_no_set_ever(self):
        self.assertIsNone(H.active(D(2026, 12, 25), 7, enabled=False))

    def test_upcoming_lists_the_set_up_now_first(self):
        ahead = H.upcoming(D(2026, 10, 31), 3, count=3)
        self.assertEqual([w.key for w in ahead], ["halloween", "thanksgiving", "christmas"])
        self.assertEqual(H.upcoming(D(2026, 12, 30), 3, count=2)[0].key, "new-years-day")


if __name__ == "__main__":
    unittest.main()
