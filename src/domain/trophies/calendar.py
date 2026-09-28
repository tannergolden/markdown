# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Date arithmetic over a set of active days: streaks, weeks, months, years.

Pure functions over `dict[date, int]` (day -> contributions), so every
Rhythm and Secret achievement is testable without a network. `today` is
passed in rather than read from the clock, which is what keeps a render
reproducible.
"""
from __future__ import annotations

import calendar as _cal
import datetime as dt
from collections import Counter, defaultdict

Days = dict  # dt.date -> int


def active(days: Days) -> list:
    return sorted(d for d, n in days.items() if n > 0)


def longest_streak(days: Days) -> int:
    best = run = 0
    prev = None
    for d in active(days):
        run = run + 1 if prev is not None and (d - prev).days == 1 else 1
        best = max(best, run)
        prev = d
    return best


def current_streak(days: Days, today: dt.date) -> int:
    """Days in a row ending today or yesterday (today may not be over yet)."""
    act = set(active(days))
    d = today if today in act else today - dt.timedelta(days=1)
    n = 0
    while d in act:
        n += 1
        d -= dt.timedelta(days=1)
    return n


def per_year(days: Days) -> Counter:
    c: Counter = Counter()
    for d in active(days):
        c[d.year] += 1
    return c


def max_days_in_a_year(days: Days) -> int:
    c = per_year(days)
    return max(c.values()) if c else 0


def years_active(days: Days) -> int:
    return len(per_year(days))


def perfect_months(days: Days) -> int:
    by_month: dict = defaultdict(set)
    for d in active(days):
        by_month[(d.year, d.month)].add(d.day)
    return sum(1 for (y, m), s in by_month.items() if len(s) == _cal.monthrange(y, m)[1])


def weekends_in_a_year(days: Days) -> int:
    """Most weekends (Saturday or Sunday with a contribution) in one calendar year."""
    c: Counter = Counter()
    seen = set()
    for d in active(days):
        if d.weekday() >= 5:
            key = (d.year, d.isocalendar()[1])
            if key not in seen:
                seen.add(key)
                c[d.year] += 1
    return max(c.values()) if c else 0


def weekdays_in_a_year(days: Days) -> int:
    c: Counter = Counter()
    for d in active(days):
        if d.weekday() < 5:
            c[d.year] += 1
    return max(c.values()) if c else 0


def max_in_a_day(days: Days) -> int:
    return max(days.values()) if days else 0


def max_in_a_week(days: Days) -> int:
    c: Counter = Counter()
    for d, n in days.items():
        iso = d.isocalendar()
        c[(iso[0], iso[1])] += n
    return max(c.values()) if c else 0


def max_in_a_month(days: Days) -> int:
    c: Counter = Counter()
    for d, n in days.items():
        c[(d.year, d.month)] += n
    return max(c.values()) if c else 0


def all_twelve_months(days: Days) -> bool:
    by_year: dict = defaultdict(set)
    for d in active(days):
        by_year[d.year].add(d.month)
    return any(len(m) == 12 for m in by_year.values())


def every_week_of_a_year(days: Days, today: dt.date) -> bool:
    """A completed calendar year with a contribution in each of its ISO weeks."""
    by_year: dict = defaultdict(set)
    for d in active(days):
        if d.year < today.year:
            by_year[d.year].add(d.isocalendar()[1])
    return any(len(w) >= 52 for w in by_year.values())


def longest_gap(days: Days) -> int:
    act = active(days)
    return max(((b - a).days for a, b in zip(act, act[1:])), default=0)


def came_back_after(days: Days, gap: int) -> bool:
    act = active(days)
    return any((b - a).days >= gap for a, b in zip(act, act[1:]))


def on_date(days: Days, month: int, day: int) -> bool:
    return any(d.month == month and d.day == day for d in active(days))


def on_friday_13th(days: Days) -> bool:
    return any(d.day == 13 and d.weekday() == 4 for d in active(days))


def on_anniversary(days: Days, origin: dt.date) -> bool:
    return any(d.month == origin.month and d.day == origin.day and d.year > origin.year for d in active(days))


def consecutive_weeks(weeks_with_activity: set) -> int:
    """Longest run of consecutive (iso_year, iso_week) keys."""
    ordered = sorted(weeks_with_activity)
    best = run = 0
    prev = None
    for y, w in ordered:
        this = dt.date.fromisocalendar(y, w, 1)
        run = run + 1 if prev is not None and (this - prev).days == 7 else 1
        best = max(best, run)
        prev = this
    return best


def weeks_of(days: Days) -> set:
    return {(d.isocalendar()[0], d.isocalendar()[1]) for d in active(days)}


def consecutive_months(months_with_activity: set) -> int:
    ordered = sorted(months_with_activity)
    best = run = 0
    prev = None
    for y, m in ordered:
        run = run + 1 if prev is not None and (y * 12 + m) - (prev[0] * 12 + prev[1]) == 1 else 1
        best = max(best, run)
        prev = (y, m)
    return best


def parse_day(iso: str) -> dt.date:
    return dt.date.fromisoformat(iso[:10])


def parse_time(iso: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
