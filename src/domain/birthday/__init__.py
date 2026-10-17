# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The page's birthday: whether the Birthday set draws the page on a given day, and how old the page turns.

The Birthday set is no holiday and no theme a page picks. A page has one
birthday a year, and on it the set takes the page from whatever else would
draw it, a holiday's set, a collection's design or the theme, for that one
day, midnight to midnight in the page's time zone, and hands it back the day
after. It is on unless the settings say `birthday: false`, and it has a
switch of its own: `holidays: false` leaves it on.

Whose birthday it is follows the page's mode:

  profile     the person's, as the settings give it: a month and a day,
              `birthday: 03-14`, or the whole date, `birthday: 1990-03-14`.
              With the year the set says how old they turn, as it does a
              repository; without it the page shows no age. GitHub keeps no
              birthday for a person, so a profile that gives none has none.
  repository  the repository's: the day GitHub created it, in the page's
              time zone, from its first anniversary on, and its set says how
              old it turns. It is GitHub's date and no other: the settings
              may turn it off, never name another day.

A February 29 birthday is kept on February 28 in a common year.

The day is the caller's: this module does no I/O and knows no clock. The set
is drawn by `party`, beside this module, with the holiday sets' layouts and
pixels; `drawn_by` hands it out by its key: `birthday`, then the day, then the
age when one is known, `birthday:2026-03-14:7`. With no day the set draws its
sample.
"""
from __future__ import annotations

import datetime as dt
import importlib
import re
from dataclasses import dataclass

KEY, NAME = "birthday", "Birthday"
OLDEST = 999            # the oldest age a cake holds: three number candles
_GIVEN = re.compile(r"(?:(\d{4})-)?(\d{1,2})-(\d{1,2})")


class BirthdayError(ValueError):
    pass


def check(value: object) -> bool | str:
    """`birthday` as the settings may give it: true, false, a month and a day as `MM-DD`, or the whole date as
    `YYYY-MM-DD`. No message repeats what was written, since it may be a date of birth."""
    if isinstance(value, bool):
        return value
    text = str(value).strip() if isinstance(value, str) else ""
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    found = _GIVEN.fullmatch(text)
    if not found:
        if re.fullmatch(r"\d{1,2}[-/.]\d{1,2}[-/.]\d{4}", text):
            raise BirthdayError("birthday: write a whole date year first, as 1990-03-14, or the month and the day "
                                "alone, as 03-14")
        raise BirthdayError("birthday: expected true, false, a month and a day as MM-DD, like 03-14, or a whole date "
                            "as YYYY-MM-DD")
    year, month, day = (int(found[1]) if found[1] else None), int(found[2]), int(found[3])
    try:
        dt.date(year or 2024, month, day)            # 2024 is a leap year, so February 29 is a day without a year
    except ValueError:
        raise BirthdayError("birthday: that is not a day of the calendar") from None
    return (f"{year:04d}-" if year is not None else "") + f"{month:02d}-{day:02d}"


def falls(month: int, day: int, year: int) -> dt.date:
    """The day a birthday on `month` and `day` falls on in `year`: February 29 is kept on February 28 in a common
    year."""
    try:
        return dt.date(year, month, day)
    except ValueError:
        return dt.date(year, 2, 28)


@dataclass(frozen=True)
class Party:
    """A birthday the page celebrates: the day, and how old the page turns on it, when that is known: a repository's
    always, a person's when the settings give the year (None otherwise)."""

    day: dt.date
    age: int | None = None

    @property
    def held(self) -> str:
        """The set's key, as the parts are told it: `birthday:2026-03-14`, and the age after it when it is known."""
        return f"{KEY}:{self.day.isoformat()}" + (f":{self.age}" if self.age else "")


def on(today: dt.date, *, given: str = "", born: dt.date | None = None) -> Party | None:
    """The birthday the page celebrates on `today`, or None: a person's, on the day `given`, a month and a day or the
    whole date; a repository's, on the day it was `born`. A birthday whose year is known is celebrated from its first
    anniversary on, and turns a year older each time, up to the oldest age a cake holds: a year that would make it
    older is a BirthdayError, whichever day it is asked on."""
    if given:
        *year, month, day = (int(n) for n in given.split("-"))
        if not year:
            return Party(today) if falls(month, day, today.year) == today else None
        born = dt.date(year[0], month, day)
    if born and today.year - born.year > OLDEST:
        raise BirthdayError(f"birthday: a cake holds an age up to {OLDEST}, so a whole date's year is "
                            f"{today.year - OLDEST} or later")
    if born and today.year > born.year and falls(born.month, born.day, today.year) == today:
        return Party(today, today.year - born.year)
    return None


def ordinal(n: int) -> str:
    """A number as an ordinal, the way a birthday is counted: 1st, 2nd, 3rd, 11th, 22nd."""
    tail = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{tail}"


def drawn_by(held: str | None):
    """The set that draws `held` (a `holidays.designs.Holiday`): told the day and a repository's age when `held`
    carries them, its sample when it is the key alone."""
    key, _, rest = (held or "").partition(":")
    if key != KEY:
        return None
    drawn = importlib.import_module(f"{__name__}.party").SET
    if not rest:
        return drawn
    day, _, age = rest.partition(":")
    return drawn.on(dt.date.fromisoformat(day), int(age) if age else None)
