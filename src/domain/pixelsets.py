# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The pixel set a page is drawn in: a holiday's set around its day, or a collection's design for its month.

Both are drawn with the same layouts and pixels, so the parts ask here for
the set a page is drawn in by its key: a holiday's with the day it falls on
after a colon (`new-years-day:2027-01-01`), which a set that letters the year
needs, or a collection's design, with the day after a colon when it is drawn
as the collection's design for the month (`medieval-forge:2026-11-01`), which
gives its headers the month's mark, and alone when a page keeps it all year
(`medieval-forge`); with the sign a page chose for its headers last
(`medieval-forge:leo`). See `holidays` and `collections`.
"""
from __future__ import annotations

from . import collections, holidays


def drawn_by(held: str | None):
    """The set that draws `held` (a `holidays.designs.Holiday`), or None when there is none."""
    key = (held or "").partition(":")[0]
    if key in holidays.SETS:
        return holidays.drawn_by(held)
    return collections.drawn_by(held)


def name(held: str | None) -> str:
    """The set's name in words: `the Halloween set`, or `Forge, the medieval collection's November design`."""
    key = (held or "").partition(":")[0]
    if key in holidays.NAMES:
        return f"the {holidays.NAMES[key]} set"
    return collections.described(key)
