# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What day it is where the page is read.

A holiday's set goes up at the page's midnight, so "today" is taken in the time
zone the settings name, UTC unless they name another. A run can also be told
the day outright, which is how a test, a preview and a check pin it.

Some systems ship only the zone database's canonical names: Ubuntu 26.04, the
runner `ubuntu-latest` names, leaves the old aliases (`EST`, `EST5EDT`,
`US/Eastern` and the rest of tz's `backward` file) to the optional
`tzdata-legacy` package. A setting that names one of the North American aliases
still works there: the three with no daylight saving are drawn as their fixed
offsets, under their own names, and the rest as the canonical zone each one
links to. Any other name this machine does not know is a setting to fix.
"""
from __future__ import annotations

import datetime as dt

# The legacy names that never change their clocks: UTC-5, UTC-7 and UTC-10 all
# year, whatever the season, so a fixed offset is the zone itself.
FIXED = {"EST": -5, "MST": -7, "HST": -10}

# The legacy names that keep daylight saving, each with the canonical zone it
# is a link to in the zone database.
CANONICAL = {
    "EST5EDT": "America/New_York",
    "CST6CDT": "America/Chicago",
    "MST7MDT": "America/Denver",
    "PST8PDT": "America/Los_Angeles",
    "US/Eastern": "America/New_York",
    "US/Central": "America/Chicago",
    "US/Mountain": "America/Denver",
    "US/Pacific": "America/Los_Angeles",
    "US/Alaska": "America/Anchorage",
    "US/Aleutian": "America/Adak",
    "US/Arizona": "America/Phoenix",
    "US/East-Indiana": "America/Indiana/Indianapolis",
    "US/Indiana-Starke": "America/Indiana/Knox",
    "US/Michigan": "America/Detroit",
    "US/Hawaii": "Pacific/Honolulu",
    "US/Samoa": "Pacific/Pago_Pago",
}


class ClockError(ValueError):
    pass


def zone(name: str) -> dt.tzinfo:
    """The time zone called `name`: UTC, one from the system's zone database, or a legacy alias it left out."""
    if name in ("UTC", "utc", ""):
        return dt.timezone.utc
    try:
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    except ImportError as exc:  # pragma: no cover - every Python the kit runs on has zoneinfo
        raise ClockError("this Python has no zoneinfo; set timezone: UTC") from exc
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        missing = exc
    if name in FIXED:
        return dt.timezone(dt.timedelta(hours=FIXED[name]), name)
    if name in CANONICAL:
        try:
            return ZoneInfo(CANONICAL[name])
        except (ZoneInfoNotFoundError, ValueError):
            pass
    hint = f"; use its canonical name, {CANONICAL[name]}" if name in CANONICAL else ""
    raise ClockError(f"timezone: {name!r} is not a zone this machine knows, like UTC or America/New_York. An old "
                     f"alias may be missing from this machine's zone database (Ubuntu 26.04 leaves them to "
                     f"tzdata-legacy){hint}") from missing


def today(name: str = "UTC", now: dt.datetime | None = None) -> dt.date:
    """The date in zone `name` at `now` (this moment, unless given)."""
    moment = now or dt.datetime.now(dt.timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.timezone.utc)
    return moment.astimezone(zone(name)).date()
