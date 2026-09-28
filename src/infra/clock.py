# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What day it is where the page is read.

A holiday's set goes up at the page's midnight, so "today" is taken in the time
zone the settings name, UTC unless they name another. A run can also be told
the day outright, which is how a test, a preview and a check pin it.
"""
from __future__ import annotations

import datetime as dt


class ClockError(ValueError):
    pass


def zone(name: str) -> dt.tzinfo:
    """The time zone called `name`: UTC, or one from the system's zone database."""
    if name in ("UTC", "utc", ""):
        return dt.timezone.utc
    try:
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    except ImportError as exc:  # pragma: no cover - every Python the kit runs on has zoneinfo
        raise ClockError("this Python has no zoneinfo; set timezone: UTC") from exc
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ClockError(f"timezone: {name!r} is not a zone this machine knows, like UTC or America/New_York") from exc


def today(name: str = "UTC", now: dt.datetime | None = None) -> dt.date:
    """The date in zone `name` at `now` (this moment, unless given)."""
    moment = now or dt.datetime.now(dt.timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.timezone.utc)
    return moment.astimezone(zone(name)).date()
