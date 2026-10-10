# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The holiday calendar: which holiday's set, if any, draws a page on a given day.

The holiday sets are not themes a page picks. With holidays on, as they are
unless the settings turn them off, each holiday's set takes over from the
page's own theme for a few days around the holiday and then hands it back.
All seven run; none is skipped on its own.

How long a set stays up is `holiday-days`, from 3 to 7, and the window is
centred on the holiday. An even count cannot centre, so the odd day goes
before it: 4 days is two before, the day, and one after. New Year's Day is
the exception and always runs 3 days, December 31 to January 2, whatever
`holiday-days` says.

No two windows may overlap. At 7 days none of the seven can (the nearest
pair, Christmas and New Year's Day, stay three days apart), and `windows`
still trims any pair that would, at the day between them, so the rule holds
for any calendar this module is given.

The day is the caller's: this module does no I/O and knows no clock. The kit
passes the date in the page's time zone, so the switch happens at the page's
midnight.

Each set is a package beside this one (`halloween`, ...), drawn with the
layouts in `designs` and the pixels in `pixel`; `drawn_by` names the set a
window is drawn in. A window whose set is not drawn yet leaves the page in
its own theme.
"""
from __future__ import annotations

import datetime as dt
import importlib
from dataclasses import dataclass

MIN_DAYS, MAX_DAYS, DEFAULT_DAYS = 3, 7, 3
NEW_YEAR = "new-years-day"


def _fixed(month: int, day: int):
    return lambda year: dt.date(year, month, day)


def _thanksgiving(year: int) -> dt.date:
    """The fourth Thursday of November."""
    first = dt.date(year, 11, 1)
    return first + dt.timedelta(days=(3 - first.weekday()) % 7 + 21)


# In calendar order. Each is (its key, its name, the day in a given year).
HOLIDAYS = (
    (NEW_YEAR, "New Year's Day", _fixed(1, 1)),
    ("valentines-day", "Valentine's Day", _fixed(2, 14)),
    ("juneteenth", "Juneteenth", _fixed(6, 19)),
    ("independence-day", "Independence Day", _fixed(7, 4)),
    ("halloween", "Halloween", _fixed(10, 31)),
    ("thanksgiving", "Thanksgiving", _thanksgiving),
    ("christmas", "Christmas", _fixed(12, 25)),
)
KEYS = tuple(k for k, _, _ in HOLIDAYS)
NAMES = {k: name for k, name, _ in HOLIDAYS}
# The package each set is drawn by, for every holiday that has its set.
SETS = {
    "new-years-day": "new_years_day",
    "valentines-day": "valentines_day",
    "juneteenth": "juneteenth",
    "independence-day": "independence_day",
    "halloween": "halloween",
    "thanksgiving": "thanksgiving",
    "christmas": "christmas",
}


def drawn_by(held: str | None):
    """The set that draws a window (a `designs.Holiday`), or None when it has none yet. `held` is the
    holiday's key, and after a colon the day it falls on, `new-years-day:2027-01-01`, which a set that
    says the year it celebrates needs; with no day a set draws its sample."""
    key, _, day = (held or "").partition(":")
    package = SETS.get(key)
    if not package:
        return None
    drawn = importlib.import_module(f"{__name__}.{package}").SET
    return drawn.on(dt.date.fromisoformat(day)) if day else drawn


@dataclass(frozen=True)
class Window:
    """One holiday's set, up from `start` to `end`, both days included."""

    key: str
    name: str
    day: dt.date
    start: dt.date
    end: dt.date

    def __contains__(self, today: dt.date) -> bool:
        return self.start <= today <= self.end

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


class HolidayError(ValueError):
    pass


def check_days(days: object) -> int:
    """`holiday-days` as a whole number from 3 to 7, or a HolidayError saying what is wrong."""
    if isinstance(days, bool) or not isinstance(days, int):
        raise HolidayError(f"holiday-days: expected a whole number from {MIN_DAYS} to {MAX_DAYS}, not {days!r}")
    if not MIN_DAYS <= days <= MAX_DAYS:
        raise HolidayError(f"holiday-days: {days} is outside {MIN_DAYS} to {MAX_DAYS}")
    return days


def span(days: int, key: str = "") -> tuple[int, int]:
    """How many days a window runs before the holiday and after it."""
    days = MIN_DAYS if key == NEW_YEAR else check_days(days)
    return days // 2, (days - 1) // 2


def window(key: str, year: int, days: int = DEFAULT_DAYS) -> Window:
    """One holiday's window in `year`, before any trimming against its neighbours."""
    for k, name, when in HOLIDAYS:
        if k == key:
            day = when(year)
            before, after = span(days, k)
            return Window(k, name, day, day - dt.timedelta(days=before), day + dt.timedelta(days=after))
    raise HolidayError(f"no holiday {key!r} (one of {', '.join(KEYS)})")


def windows(year: int, days: int = DEFAULT_DAYS) -> list[Window]:
    """Every window in `year`, in order, with the next year's first, trimmed so that none overlaps.

    The next year's first holiday, New Year's Day, comes along because its
    window opens on December 31 of this one.
    """
    ws = [window(k, year, days) for k in KEYS] + [window(KEYS[0], year + 1, days)]
    out: list[Window] = []
    for w in ws:
        if out and w.start <= out[-1].end:
            prev = out[-1]
            gap = (w.day - prev.day).days
            # The last day the earlier set keeps: halfway between the two holidays, the rest to the later one.
            cut = prev.day + dt.timedelta(days=max(0, (gap - 1) // 2))
            out[-1] = Window(prev.key, prev.name, prev.day, prev.start, min(prev.end, cut))
            w = Window(w.key, w.name, w.day, max(w.start, cut + dt.timedelta(days=1)), w.end)
        out.append(w)
    return out


def active(today: dt.date, days: int = DEFAULT_DAYS, enabled: bool = True) -> Window | None:
    """The holiday whose set draws the page on `today`, or None for the page's own theme."""
    if not enabled:
        return None
    for w in windows(today.year - 1, days) + windows(today.year, days):
        if today in w:
            return w
    return None


def upcoming(today: dt.date, days: int = DEFAULT_DAYS, count: int = 7) -> list[Window]:
    """The next `count` windows that have not ended by `today`, the one up now first."""
    seen, out = set(), []
    for year in (today.year - 1, today.year, today.year + 1):
        for w in windows(year, days):
            if w.end >= today and (w.key, w.day) not in seen:
                seen.add((w.key, w.day))
                out.append(w)
    return sorted(out, key=lambda w: w.start)[:count]
