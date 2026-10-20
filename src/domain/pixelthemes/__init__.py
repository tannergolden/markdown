# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The pixel themes: one world drawn as pixel art, a theme a page keeps all year.

A pixel theme is a theme a page picks by its key, `theme: heaven-and-hell`, and
the page is drawn in its set every day of the year: the banners, the badges,
the elements, the trophy case and the games, as a collection's design draws
them. It has no calendar: it never changes with the month, and its headers
carry no month's mark and no sign. Like every set it draws each file twice,
once for a reader in GitHub's light mode and once for one in its dark mode,
and a pixel theme may make the two a pair of twins, as Heaven & Hell is heaven
by day and hell by night.

With holidays on, a holiday's set still takes over around its day and hands
the page back to the pixel theme after, and on the page's birthday the
Birthday set takes it for the day. A file the set cannot draw, like a title in
letters its pixels lack, is drawn in the standard theme.

Each pixel theme is a package beside this one named for its key
(`heaven-and-hell` is `heaven_and_hell`), drawn with the holiday sets' layouts
and pixels (`holidays.designs` and `holidays.pixel`), and a page can pick it
once its package is here. docs/technical/Themes.md defines every kind of theme
the kit draws and says how to add or remove each.
"""
from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """A pixel theme: the key a page names it by, its name, and what it draws, in a sentence, as the theme-sets
    page and `markdown-kit themes` say it."""

    key: str
    name: str
    summary: str


# Every pixel theme, by its key, in the order they are listed.
THEMES = {theme.key: theme for theme in (
    Theme("heaven-and-hell", "Heaven & Hell",
          "Angels by day and demons by night: in GitHub's light mode the page is heaven, and in its dark mode the "
          "same page is hell, each thing of heaven with its fallen twin standing where it stood."),
)}


def bare(key: str | None) -> str:
    """A pixel theme's key without anything after a colon: a pixel theme has no calendar, so a key that comes
    with a day or a sign, `heaven-and-hell:2026-11-01`, names the theme alone."""
    return (key or "").partition(":")[0]


def package(key: str) -> str:
    """The package a pixel theme is drawn by: its key, with underscores."""
    return bare(key).replace("-", "_")


def is_drawn(key: str | None) -> bool:
    """Whether a pixel theme is drawn: it is listed, and its package is here."""
    key = bare(key)
    return key in THEMES and importlib.util.find_spec(f"{__name__}.{package(key)}") is not None


def is_theme(theme: str) -> bool:
    """Whether a page can pick `theme`, as a pixel theme: one that is drawn."""
    return is_drawn(theme) and theme == bare(theme)


def themes() -> list[str]:
    """The pixel themes a page can pick, in the order they are listed."""
    return [k for k in THEMES if is_drawn(k)]


def drawn_by(held: str | None):
    """The set that draws a pixel theme (a `holidays.designs.Holiday`), or None when `held` names none that is
    drawn. Its set is the same every day, so nothing after a colon changes it."""
    if not is_drawn(held):
        return None
    return importlib.import_module(f"{__name__}.{package(held)}").SET


def name_of(key: str | None) -> str:
    """A pixel theme's name, `Heaven & Hell`, or "" when `key` names no pixel theme."""
    theme = THEMES.get(bare(key))
    return theme.name if theme else ""


def described(key: str | None) -> str:
    """A pixel theme in words, as a commit says it: `the Heaven & Hell theme`."""
    return f"the {name_of(key)} theme" if name_of(key) else bare(key)
