# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The look a case is drawn in: the standard theme's, a print's, or a pixel set's.

Every part of a page is drawn in the page's theme, and the trophy case is one
of them. A look draws every file of a case from the same measurement, at the
same sizes and in the same words, so when a page changes its theme the case
changes its material and nothing else:

  Standard  the case's own five styles, struck in metal and enamel: the
            standard theme's look (`art`, `styles`)
  Drafted   a print's: every card a drawing on the print's drafting paper, in
            its line and its ink (`prints`)
  Pixels    a pixel set's, a holiday's around its day, a pixel theme's or
            a collection's design's: every card in the set's pixels,
            palette and frame (`holidays.designs.trophies`)

`looks` picks them from the page's theme, the set the page is drawn in and the
section's `look`: a page a set draws is drawn in the set, a page in a print in
the print, and any other page in the standard look, as a section with
`look: standard` always is. After the look it names the ones a case falls back
on, the page's own look and then the standard one, for a case a set cannot
letter.
"""
from __future__ import annotations

from .. import pixelsets
from ..canvas import colours
from ..prints import PRINTS, STANDARD
from . import art, prints, styles  # noqa: F401  (styles registers itself)


class CannotDraw(ValueError):
    """A look cannot draw a case, as a set cannot letter a character its pixels lack."""


class Standard:
    """The standard theme's look: the case's own styles, as the trophies kit drew them."""

    def __init__(self, style: str):
        self.style, self.name = style, STANDARD
        self.draw = art.STYLES[style]

    def card(self, case: str, core, value: int, o: dict) -> str:
        return self.draw(art.CASES[case], core, value, o)

    def pin(self, case: str, a, cur) -> str:
        return art.pin(art.CASES[case], a, cur)

    def level(self, case: str, cores, values, ach, curs, subject, foot) -> str:
        return art.level_card(art.CASES[case], cores, values, ach, curs, subject, foot)

    def next_up(self, case: str, cores, values, ach, curs) -> str:
        return art.next_up_card(art.CASES[case], cores, values, ach, curs)

    def lint(self, svg: str) -> list[str]:
        """Its metals and enamels are shades of their own, as they always were."""
        return []


class Drafted:
    """A print's look: every card a drawing on the print's drafting paper (see `prints`)."""

    def __init__(self, style: str, tone: str):
        self.style, self.tone, self.name = style, tone, tone

    def card(self, case: str, core, value: int, o: dict) -> str:
        return prints.STYLES[self.style](self.tone, case, core, value, o)

    def pin(self, case: str, a, cur) -> str:
        return prints.pin(self.tone, case, a, cur)

    def level(self, case: str, cores, values, ach, curs, subject, foot) -> str:
        return prints.level_card(self.tone, case, cores, values, ach, curs, subject, foot)

    def next_up(self, case: str, cores, values, ach, curs) -> str:
        return prints.next_up_card(self.tone, case, cores, values, ach, curs)

    def lint(self, svg: str) -> list[str]:
        """A print's drawing is held to the palette, as its banners are: every colour a token, or one of the
        colours a repository's own print declares."""
        return colours(svg)


class Pixels:
    """A pixel set's look: the case in the set's pixels, palette and frame (see `holidays.designs.trophies`)."""

    def __init__(self, style: str, held):
        self.style, self.held = style, held
        self.name = pixelsets.name(held.key)

    def _drawn(self, svg: str | None) -> str:
        if svg is None:
            raise CannotDraw(f"{self.name} cannot letter every word of the case")
        return svg

    def card(self, case: str, core, value: int, o: dict) -> str:
        return self._drawn(self.held.trophy_card(self.style, core, value, o, case == "night"))

    def pin(self, case: str, a, cur) -> str:
        return self._drawn(self.held.trophy_pin(a, cur, case == "night"))

    def level(self, case: str, cores, values, ach, curs, subject, foot) -> str:
        return self._drawn(self.held.trophy_level(cores, values, ach, curs, subject, foot, case == "night"))

    def next_up(self, case: str, cores, values, ach, curs) -> str:
        return self._drawn(self.held.trophy_next_up(cores, values, ach, curs, case == "night"))

    def lint(self, svg: str) -> list[str]:
        """A set's files keep to its closed palette, and the case's metals with it."""
        return colours(svg, self.held.trophy_tokens)


def own(style: str, theme: str):
    """The page's own look when no set draws it: its print's, or the standard one."""
    return Drafted(style, theme) if theme in PRINTS else Standard(style)


def looks(section: dict, theme: str = STANDARD, holiday: str = "") -> list:
    """The looks a case is drawn in, the first that can draw it: the set the page is drawn in (`holiday`, a
    holiday's key, a pixel theme's or a collection's design's, as `pixelsets` reads it), then the page's own
    look, then the standard one. `theme` is the page's own theme, rainbowprint already resolved to its print."""
    style = section["style"]
    if section.get("look", "theme") == STANDARD:
        return [Standard(style)]
    out = []
    held = pixelsets.drawn_by(holiday) if holiday else None
    if held is not None and hasattr(held, "trophy_card"):
        out.append(Pixels(style, held))
    out.append(own(style, theme))
    if not isinstance(out[-1], Standard):
        out.append(Standard(style))
    return out
