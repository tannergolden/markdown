# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The collections: one subject drawn twelve ways, a design for each month of the year.

A collection is a theme a page picks, `theme: medieval`, and the page is drawn
in the collection's design for the month it is in: January's design from the
first of January, February's from the first of February, and so round the
year, so the page changes on the first of every month. The day is the
caller's, in the page's time zone, so the change comes at the page's midnight,
as a holiday's does. Nothing is remembered between runs to make it happen: a
run that is late or missed is put right by the next one, and a page that
picks a collection halfway through a month is drawn in that month's design at
once.

A page can also keep one design of a collection all year by naming it, as in
`theme: medieval-forge`.

A design is told when it is drawn as its collection's design for the month,
the way a holiday's set is told the day its holiday falls on: its key carries
the day after a colon, `medieval-forge:2026-11-01`, and `drawn_by` hands the
design that day. Only a design drawn that way carries the month's mark (see
`hand`); a page that keeps one design all year names it alone. A page may
also choose the sign its headers carry, `sign: leo`, all year and whichever
way it is drawn, and its key then carries the sign after a colon too, last:
`medieval-forge:leo`, or `medieval-forge:2026-11-01:leo`. Every function here
that takes a design's key takes it with a day and a sign as well.

With holidays on, a holiday's set still takes over around its day and hands
the page back to the month's design after. A collection draws the banners,
the badges and the elements; the trophies keep the `standard` look.

Every collection has exactly twelve designs, January's first, and a page can
pick a collection, or one of its designs, only once all twelve are drawn.
Each design is a package beside this one named for its key (`medieval-forge`
is `medieval_forge`), drawn with the holiday sets' layouts and pixels
(`holidays.designs` and `holidays.pixel`), and a design is drawn once its
package is here.
"""
from __future__ import annotations

import datetime as dt
import importlib
import importlib.util
from dataclasses import dataclass

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")


def bare(design: str | None) -> str:
    """A design's key without the day and the sign it may carry after a colon: `medieval-forge:2026-11-01` and
    `medieval-forge:leo` are `medieval-forge`."""
    return (design or "").partition(":")[0]


@dataclass(frozen=True)
class Collection:
    """A collection: its key, its name, and its twelve designs as (key, name), January's first."""

    key: str
    name: str
    designs: tuple

    @property
    def keys(self) -> tuple:
        return tuple(k for k, _ in self.designs)

    def month_of(self, design: str) -> int:
        """The month a design is up in, 1 for January."""
        return self.keys.index(bare(design)) + 1


COLLECTIONS = {
    "medieval": Collection("medieval", "Medieval", (
        ("medieval-longship", "Longship"),        # the northern lights over a winter fjord
        ("medieval-chessmen", "Chessmen"),        # a long winter's game in walrus ivory
        ("medieval-illuminated", "Illuminated"),  # the scriptorium through Lent
        ("medieval-cathedral", "Cathedral"),      # stained glass at Easter
        ("medieval-tournament", "Tournament"),    # the jousts of May
        ("medieval-mappamundi", "Mappa Mundi"),   # the sailing season
        ("medieval-stronghold", "Stronghold"),    # banners on the walls in high summer
        ("medieval-mosaic", "Mosaic"),            # Byzantine gold in the August sun
        ("medieval-alchemist", "Alchemist"),      # the laboratory at the equinox
        ("medieval-tapestry", "Tapestry"),        # Hastings, October 1066
        ("medieval-forge", "Forge"),              # the smithy's fire as the cold comes in
        ("medieval-hoard", "Hoard"),              # a dragon asleep on its gold through midwinter
    )),
}


def package(design: str) -> str:
    """The package a design is drawn by: its key, with underscores."""
    return bare(design).replace("-", "_")


def owner(design: str) -> Collection | None:
    """The collection a design belongs to, or None."""
    key = bare(design)
    return next((c for c in COLLECTIONS.values() if key in c.keys), None)


def is_drawn(design: str) -> bool:
    """Whether a design of a collection is drawn: its package is here."""
    key = bare(design)
    return owner(key) is not None and importlib.util.find_spec(f"{__name__}.{package(key)}") is not None


def drawn_by(design: str | None):
    """The set that draws a design (a `holidays.designs.Holiday`), or None when it is not drawn yet. A key with a
    day after a colon, `medieval-forge:2026-11-01`, is the design drawn as its collection's design for the month,
    and the set is handed that day (see `Holiday.on`); a key alone is the design kept all year. A sign after a
    colon, last, `medieval-forge:leo` or `medieval-forge:2026-11-01:leo`, is the one the page chose for its
    headers to carry, and the set is handed it (see `hand.CollectionSet.signed`)."""
    key, *after = (design or "").split(":")
    if not is_drawn(key):
        return None
    drawn = importlib.import_module(f"{__name__}.{package(key)}").SET
    for part in after:
        drawn = drawn.on(dt.date.fromisoformat(part)) if part[:1].isdigit() else drawn.signed(part)
    return drawn


def drawn(collection: str) -> int:
    """How many of a collection's twelve designs are drawn."""
    return sum(is_drawn(k) for k in COLLECTIONS[collection].keys)


def complete(collection: str) -> bool:
    """Whether every one of a collection's twelve designs is drawn, so a page can pick it."""
    c = COLLECTIONS.get(collection)
    return c is not None and len(c.designs) == len(MONTHS) and drawn(collection) == len(MONTHS)


def is_theme(theme: str) -> bool:
    """Whether a page can pick `theme`: a collection, or one design of one, once all twelve are drawn."""
    c = COLLECTIONS.get(theme) or owner(theme)
    return c is not None and complete(c.key)


def themes() -> list[str]:
    """The collections a page can pick, in the order they are listed."""
    return [k for k in COLLECTIONS if complete(k)]


def unfinished(theme: str) -> str:
    """Why a page cannot pick `theme` yet, when it names a collection or a design still being drawn, else ""."""
    c = COLLECTIONS.get(theme) or owner(theme)
    if c is None or complete(c.key):
        return ""
    return f"{c.key} is a collection still being drawn, with {drawn(c.key)} of its {len(MONTHS)} designs done"


def design_for(theme: str, today: dt.date) -> str:
    """The design a page in `theme` is drawn in on `today`: its collection's design for the month, or the
    design it names; "" for any other theme."""
    if not is_theme(theme):
        return ""
    c = COLLECTIONS.get(theme)
    return c.keys[today.month - 1] if c else theme


def name_of(design: str) -> str:
    """A design's name, `Forge`, or "" when it is not a design of a collection."""
    c = owner(design)
    return dict(c.designs)[bare(design)] if c else ""


def described(design: str, month: bool = False) -> str:
    """A design in words: `Forge, from the medieval collection`, or with `month` the month it is up in,
    `Forge, the medieval collection's November design`."""
    c = owner(design)
    if c is None:
        return design
    if month:
        return f"{name_of(design)}, the {c.key} collection's {MONTHS[c.month_of(design) - 1]} design"
    return f"{name_of(design)}, from the {c.key} collection"
