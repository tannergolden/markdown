# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A collection's hand: what its twelve designs share, so that the year reads as one artist's work.

Each design of a collection keeps its own subject, scene, materials, frame,
title lettering and palette. What it shares with the other eleven is the
collection's hand, and these are a hand's rules, the reference every design
of a collection is drawn to:

- The light. Every design is lit by the engine's one lamp, up and to the left
  and toward the viewer, and shaded on the engine's seven-tone ramps
  (`holidays.pixel.shade`), whose shadows lean purple and whose lights lean
  gold. An outline is the darkest tone of its own material's ramp, never pure
  black.
- The words. Every design sets its words in the hand's two inks, `body` for
  what it says and `muted` for what it says more quietly: the same two in all
  twelve designs, by day and by night. Titles, labels and accents keep the
  design's own materials.
- The ground. The sheet behind the words falls within the hand's band of
  lightness and colour, `day_ground` by day and `night_ground` by night, so
  no month glares or sinks beside the others: a month's mood is in its hue.
  A band is measured in CIELAB, its lightness L* from and to and its colour
  C* at most. By day a ground with almost no colour, C* under 6, leans
  warm, its hue from 40 to 110 degrees: never a cold white or a cold grey.
  A night may be cool, as night skies are. Both inks clear 4.5:1 against
  both ends of both bands.
- The lights. Every flame burns on the hand's flame ramp, and every moon is
  the hand's moon, drawn on its moon ramp.
- The people. Faces and hands are drawn to one canon, the same proportions in
  every design whatever its art form, and their skin is on the hand's three
  skin ramps. By night a face keeps its tone and takes the light of its
  scene, a lamp's warmth or the moon's cold; drawn a tone darker, it would
  read as another person.
- The month's mark. On a page that follows the collection's calendar, the
  hand draws the month's mark at the top centre of every header, in the same
  place in every design (see `Holiday.month_mark`). The medieval hand's mark
  is the month's sign of the zodiac in gold on a lapis roundel (`zodiac`).
  The mark belongs to the calendar, so a page that keeps one design all
  year, as `theme: medieval-forge` does, is drawn without it. A page may
  choose one of the twelve itself, `sign: leo`, and then carries that one on
  every header all year, whether it follows the calendar or keeps one
  design. Every design keeps the top centre of its headers clear for it
  either way.
- The motion. Titles glint on the hand's period, `glint` seconds. Flames
  flicker and stars twinkle on the engine's cadences (`BLINKS` in
  `holidays.pixel.canvas`). Figures idle in loops of 4 to 8 seconds, and
  slow ambient sweeps, a cloud's drift or a turning light, take 24 to 48
  seconds.

`Hand` is a collection's hand and `HANDS` holds every collection's. Every
design of a collection subclasses `CollectionSet`, which carries the hand,
puts its colours in the design's closed palette and draws the month's mark.
`check` says, in words, how a design breaks its hand, and `lab` is what it
measures a colour with.
"""
from __future__ import annotations

import copy
import datetime as dt
import math
from dataclasses import dataclass
from typing import Callable

from .. import collections
from ..banners import sample
from ..banners.compose import compose
from ..banners.content import Header
from ..banners.settings import check as banners_check
from ..holidays.designs import Holiday
from ..holidays.designs.banners import MARK_Y, mark_box as _box
from ..holidays.pixel import Pix, make_ramp
from . import zodiac


@dataclass(frozen=True)
class Hand:
    """A collection's hand. Colours are #RRGGBB; a pair is (by day, by night)."""

    body: tuple            # the words' ink
    muted: tuple           # the quieter words' ink
    day_ground: tuple      # the band the ground behind the words falls in by day: (L* from, L* to, most C*)
    night_ground: tuple    # and by night
    flame: str             # the base of the ramp every flame burns on
    moon: str              # the base of the moon's ramp
    skin: tuple            # the bases of the three skin ramps, light to dark
    glint: float           # how often a title's glint passes, in seconds
    mark: Callable         # draws the month's mark: (p, cx, cy, month, night, motion), naming its colours in `tokens`
    mark_size: int         # the width and height of the box the mark is drawn in, in units
    signs: tuple           # the twelve marks' names, January's first, which a page names to choose one: `sign: leo`

    @property
    def ramps(self) -> dict:
        """The hand's ramps by name, seven tones each, dark to light: `flame`, `moon` and `skin0` to `skin2`."""
        out = {"flame": make_ramp(self.flame), "moon": make_ramp(self.moon)}
        out.update({f"skin{i}": make_ramp(base) for i, base in enumerate(self.skin)})
        return out

    def month_of(self, sign: str) -> int:
        """The month whose mark a page names with `sign`, 1 for January, whatever its case; 0 for a name that is
        none of the hand's."""
        names = [s.lower() for s in self.signs]
        return names.index(sign.lower()) + 1 if sign.lower() in names else 0

    def ramp(self, name: str) -> list[str]:
        """One of the hand's ramps, for a design to draw with: `flame`, `moon`, or `skin0`, `skin1` and `skin2`,
        the light skin to the dark."""
        return self.ramps[name]

    @property
    def tokens(self) -> frozenset:
        """Every colour the hand may paint: its inks, its ramps and its mark's colours."""
        colours = {*self.body, *self.muted, *getattr(self.mark, "tokens", ())}
        colours.update(c for ramp in self.ramps.values() for c in ramp)
        return frozenset(c.upper() for c in colours)


MEDIEVAL = Hand(
    body=("#22180F", "#F2E8D4"),                # iron-gall brown by day, warm cream by night
    muted=("#4E3D2A", "#C9B99C"),
    day_ground=(72, 90, 40),
    night_ground=(4, 16, 24),
    flame="#E07A1F",                            # one amber flame
    moon="#D8E4F0",                             # one pale moon
    skin=("#E9B78F", "#C98E62", "#8E5B3B"),
    glint=12.0,
    mark=zodiac.ROUNDEL,                        # the month's sign of the zodiac, gold on a lapis roundel
    mark_size=zodiac.SIZE,
    signs=zodiac.SIGNS,
)

HANDS = {"medieval": MEDIEVAL}


def signs(theme: str = "") -> list[str]:
    """The signs a page in `theme` may choose for its headers to carry, `sign: leo`, in lower case: its
    collection's hand's, or every hand's for a theme that is no collection's."""
    c = collections.COLLECTIONS.get(theme) or collections.owner(theme)
    hands = [HANDS[c.key]] if c is not None and c.key in HANDS else list(HANDS.values())
    return list(dict.fromkeys(s.lower() for hand in hands for s in hand.signs))


def lab(colour: str) -> tuple[float, float, float]:
    """A #RRGGBB colour's CIELAB lightness L* (0 to 100), its chroma C* and its hue angle h in degrees (0 to 360),
    from sRGB under D65."""
    r, g, b = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    r, g, b = (v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in (r, g, b))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29

    a_, b_ = 500 * (f(x) - f(y)), 200 * (f(y) - f(z))
    return 116 * f(y) - 16, math.hypot(a_, b_), math.degrees(math.atan2(b_, a_)) % 360


class CollectionSet(Holiday):
    """A design of a collection: the class every design of a collection subclasses, naming its `collection`.

    As the subclass is made, its hand's colours join its closed palette, so
    every colour the hand paints is one its files may use. It draws the
    month's mark when it is drawn as its collection's design for the month,
    which the kit says by handing it the day (see `Holiday.on`), and the sign
    a page chose in its place, which the kit hands it too (see `signed`)."""

    collection = ""        # the collection the design belongs to, as `medieval`
    sign = ""              # the sign a page chose for its headers to carry, as `leo`, or "" for the month's

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.collection:
            cls.tokens = frozenset(cls.tokens) | HANDS[cls.collection].tokens

    @property
    def hand(self) -> Hand:
        """The hand the design is drawn in: its collection's."""
        return HANDS[self.collection]

    @property
    def month(self) -> int:
        """The month the design is up in, 1 for January, or 0 for a design no collection lists."""
        c = collections.owner(self.key)
        return c.month_of(self.key) if c else 0

    @property
    def mark_size(self) -> int:
        """The width and height of the box the hand's mark takes, in units."""
        return self.hand.mark_size if self.collection else 0

    def signed(self, sign: str) -> "CollectionSet":
        """This design carrying the sign a page chose, `leo`, at the top centre of every header, in place of the
        month's: the same whether the page follows the calendar or keeps the design all year."""
        held = copy.copy(self)
        held.sign = sign
        return held

    @property
    def mark_month(self) -> int:
        """The month whose mark the design's headers carry, 1 for January: the sign the page chose, else the
        design's own month when it is drawn as its collection's design for the month, which it knows by being
        handed a day; 0 for none, as on a page that keeps one design all year and chose no sign."""
        if self.sign:
            return self.hand.month_of(self.sign)
        return self.month if self.day is not None else 0

    def mark_box(self, p: Pix, margin: int = 2) -> tuple:
        """The box the hand's mark takes at the top centre of a header, `margin` units more all round, as (x0, y0,
        x1, y1), ends excluded: what every scene, star and band motif keeps clear of, whether the mark is drawn
        or not."""
        return _box(p, self.hand.mark_size, margin)

    @property
    def marked(self) -> bool:
        """Whether the design's headers carry the hand's mark. A design that draws round the mark, parting a
        band either side of it, asks this; every design keeps the box clear either way."""
        return bool(self.mark_size and self.mark_month)

    def month_mark(self, p: Pix, cx, cy, night, motion):
        """The hand's mark, centred on (cx, cy): the month's when the design is drawn as its collection's design
        for the month, or the sign the page chose. With neither, as on a page that keeps one design all year, it
        draws nothing, for the month's mark belongs to the calendar."""
        if self.marked:
            self.hand.mark(p, cx, cy, self.mark_month, night, motion)


def contents(key: str) -> list:
    """The headers a design is checked with, as (what, header): the kit's own lines and each of its samples,
    composed as a run composes them, from the kit's data a run installs first (`infra.resources.install`)."""
    out = [("the kit's own lines", Header(tone="standard", holiday=key))]
    for name, m in sample.SAMPLES.items():
        h, _, _ = compose(m, banners_check({}) | {"theme": "standard", "holiday": key})
        out.append((f"the {name} sample", h))
    return out


def _ground(hand: Hand, colour: str, night: bool) -> str:
    """How a ground breaks the hand's band, in words, or ""."""
    lo, hi, most = hand.night_ground if night else hand.day_ground
    light, chroma, hue = lab(colour)
    wrong = []
    if not lo <= light <= hi:
        wrong.append(f"L* {light:.1f}, outside {lo} to {hi}")
    if chroma > most:
        wrong.append(f"C* {chroma:.1f}, over {most}")
    if not night and chroma < 6 and not 40 <= hue <= 110:
        wrong.append(f"almost no colour (C* {chroma:.1f}) at a hue of {hue:.0f} degrees, not warm")
    if not wrong:
        return ""
    return f"the ground behind its words by {'night' if night else 'day'}, {colour}, is " + " and ".join(wrong)


def _draw(held, code: str, wide: bool, h, night: bool) -> Pix:
    if wide:
        return {"H1": held.h1, "H2": held.h2, "H3": held.h3}[code](h, night, False)
    return {"H1": held.h1_narrow, "H2": held.h2_narrow, "H3": held.h3_narrow}[code](h, night)


def _mark_at(p: Pix, mark, month: int, night: bool) -> str:
    """Whether a header holds the month's mark at the top centre: "here", "elsewhere" or "none"."""
    want = Pix(p.w, p.h)
    mark(want, p.w // 2, MARK_Y, month, night, False)
    cells = [(name, xy, c) for name, layer in want.layers.items() for xy, c in layer.items()]
    if all(p.layers.get(name, {}).get(xy) == c for name, xy, c in cells):
        return "here"
    colours = {c for _, _, c in cells}
    return "elsewhere" if any(c in colours for name in want.layers for c in p.layers.get(name, {}).values()) \
        else "none"


def check(design, headers: list | None = None) -> list[str]:
    """How `design`, a design of a collection, breaks its collection's hand, in words: [] when it keeps to it.

    The design is drawn as its collection's design for its month, wide and on
    a phone, by day and by night, with each of `headers`, (what, header) pairs
    that default to the kit's own lines and its samples (see `contents`).
    It names an ink for its words that is not the hand's; a ground behind its
    words, read with `bg_at` over every row its H1 and H2 set words on, that
    falls outside the hand's band; the hand's colours missing from its
    palette; and a header whose month's mark, or the sign the design was
    handed (see `CollectionSet.signed`), is missing or away from the top
    centre."""
    c = collections.owner(design.key)
    if c is None or c.key not in HANDS:
        return [f"{design.key} is not a design of a collection with a hand"]
    hand = HANDS[c.key]
    held = design.on(dt.date(2026, c.month_of(design.key), 1))   # any year: the day says it is the month's design
    month = held.mark_month                       # the month's mark, or the sign the design was handed
    out = []
    for night, when in ((False, "day"), (True, "night")):
        inks = held.ink(night)
        for role in ("body", "muted"):
            want = getattr(hand, role)[night]
            if inks[role].upper() != want.upper():
                out.append(f"its {role} ink by {when} is {inks[role]}, not the hand's {want}")
    missing = sorted(hand.tokens - {t.upper() for t in design.tokens})
    if missing:
        out.append(f"{len(missing)} of the hand's colours are not in its palette, among them {', '.join(missing[:4])}")
    grounds, marks = {}, {}
    for what, h in headers if headers is not None else contents(design.key):
        for code in ("H1", "H2", "H3"):
            for wide in (True, False):
                for night in (False, True):
                    p = _draw(held, code, wide, h, night)
                    if wide and code in ("H1", "H2"):
                        for box in p.words:
                            for y in range(box[1] + 1, box[3] - 1):
                                grounds.setdefault((night, held.bg_at(p, night, y).upper()), None)
                    found = _mark_at(p, hand.mark, month, night)
                    if found != "here":
                        place = f"{code} {'wide' if wide else 'on a phone'} by {'night' if night else 'day'}"
                        marks.setdefault(found, []).append(f"{place} with {what}")
    for night, colour in grounds:
        wrong = _ground(hand, colour, night)
        if wrong:
            out.append(wrong)
    if marks.get("none"):
        out.append(f"no month's mark at the top centre of {len(marks['none'])} headers, among them "
                   f"{marks['none'][0]}")
    if marks.get("elsewhere"):
        out.append(f"the month's mark is away from the top centre of {len(marks['elsewhere'])} headers, among them "
                   f"{marks['elsewhere'][0]}")
    return out
