# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Every design, and every file it draws.

A design is drawn as up to six files, named the way the siblings name theirs:
`-day` for GitHub's light theme and `-dark` for its dark one.

  header-day.svg          header-dark.svg          the ordinary case
  header-still-day.svg    header-still-dark.svg    reduced motion, only for a design that moves
  header-narrow-day.svg   header-narrow-dark.svg   a phone; always still

A footer draws the same six as `footer-*.svg`, plus one pair per link in its
links row, `link-<label>-day.svg` and `link-<label>-dark.svg`, because an
image in a README can carry only the one link that wraps it.

A design drawn in `standard` is drawn by `standard.banners`, the masthead,
and in any print by its own function here: the codes, the files and the
README blocks are the same whichever draws them. While a holiday's set is up
it draws every file instead, and a file it cannot draw within the lint (a
character its letters lack, or a budget it cannot keep) is drawn as it
always is.
"""
from __future__ import annotations

import re

from .. import holidays
from ..canvas import BUDGET, DARK, DAY, lint
from ..holidays.pixel import MISSING
from ..prints import STANDARD
from ..standard import banners as standard
from . import footers, headers
from .content import Footer, Header
from .layout import Design

HEADERS: dict[str, Design] = {
    d.code: d for d in (
        Design("H1", "sheet", "Sheet", "A cover sheet: the title centred and dimensioned with its own width, the motto and any further notes as its general notes, and the figures GitHub gives ruled along its foot.",
               True, ("F1",), headers.sheet_design),
        Design("H2", "section", "Section", "The default. The title drawn as a cut solid: outlined, hatched at 45 degrees, dimensioned both ways, and plotted in as the page opens, with the figures GitHub gives ruled along its foot.",
               True, ("F1",), headers.section),
        Design("H3", "strip", "Strip", "The sheet at a smaller scale: the title dimensioned, a line or two under it, and a slimmer row of figures.",
               True, ("F2",), headers.strip),
    )
}
FOOTERS: dict[str, Design] = {
    d.code: d for d in (
        Design("F1", "title-block", "Title block", "The foot of the sheet, one ruled row: the closing notes, built by, licence, the last change, and the way back up.",
               False, ("H1", "H2"), footers.title_block, kind="footer", chip=footers.chip),
        Design("F2", "scale-bar", "Scale bar", "A slim foot for the strip: a graphic scale, the closing phrase over the attribution, and the way back up.",
               False, ("H3",), footers.scale_bar, kind="footer", chip=footers.chip),
    )
}

DESIGNS: dict[str, Design] = {**HEADERS, **FOOTERS}

# (suffix, wide, motion, theme)
VARIANTS = (
    ("day", True, True, DAY),
    ("dark", True, True, DARK),
    ("still-day", True, False, DAY),
    ("still-dark", True, False, DARK),
    ("narrow-day", False, False, DAY),
    ("narrow-dark", False, False, DARK),
)


def variants(design: Design) -> list[tuple]:
    """The variants a design actually has: a design that never moves has no separate still file."""
    return [v for v in VARIANTS if design.animates or not v[0].startswith("still")]


def budget(kind: str) -> int:
    """What one of a design's files may weigh: a header's or a footer's budget, whatever its variant."""
    return BUDGET[kind]


def slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "link"


def _held(draw, cap: int, tokens: frozenset) -> str | None:
    """A holiday set's file from `draw()`, or None when it fails the lint or its letters lack a character."""
    MISSING.clear()
    svg = draw()
    lacks = bool(MISSING)
    MISSING.clear()
    return None if lacks or lint(svg, budget=cap, tokens=tokens) else svg


def render(design: Design, content: Header | Footer, only: set | None = None) -> dict[str, str]:
    """Every file the design draws for this content, by filename; `only` names the variants wanted."""
    draw, chip = design.draw, design.chip
    if content.tone == STANDARD:
        draw, chip = standard.DRAW[design.code], standard.link
    held = holidays.drawn_by(content.holiday)
    out = {}
    for suffix, wide, motion, theme in variants(design):
        if not only or suffix in only:
            svg = None
            if held:
                drawer = held.header if design.kind == "header" else held.footer
                svg = _held(lambda: drawer(design.code, content, theme, wide, motion), budget(design.kind),
                            held.tokens)
            out[f"{design.kind}-{suffix}.svg"] = svg or draw(content, theme, wide, motion)
    if (design.kind == "footer" and chip and isinstance(content, Footer) and content.on("links")
            and (not only or "links" in only)):
        for i, (label, _) in enumerate(content.links):
            for theme in (DAY, DARK):
                svg = _held(lambda: held.link(label, theme, i), BUDGET["link"], held.tokens) if held else None
                out[f"link-{slug(label)}-{theme['name']}.svg"] = svg or chip(label, theme, content.tone)
    return out


def names(design: Design, content: Header | Footer) -> list[str]:
    """The files `render` would draw for this content, by name, without drawing them."""
    out = [f"{design.kind}-{suffix}.svg" for suffix, *_ in variants(design)]
    if design.kind == "footer" and design.chip and isinstance(content, Footer) and content.on("links"):
        out += [f"link-{slug(label)}-{theme['name']}.svg" for label, _ in content.links for theme in (DAY, DARK)]
    return out


def check(design: Design, files: dict[str, str], tokens: frozenset = frozenset()) -> dict[str, list[str]]:
    """Lint every file; only the ones with problems appear in the result. `tokens` are a holiday set's
    colours, for files it drew."""
    problems = {}
    for name, svg in files.items():
        cap = BUDGET["link"] if name.startswith("link-") else budget(design.kind)
        found = lint(svg, budget=cap, text_ok=design.text_ok, tokens=tokens)
        if found:
            problems[name] = found
    return problems
