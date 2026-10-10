# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The README's trophies block: the level and next-up cards, the core trophies, then the achievements.

Each image exists twice, a Night file and a Day file, and by default they are
embedded in one `<picture>` element whose `prefers-color-scheme` source picks
the Night file on a dark system, the way GitHub documents. `embed: fragment`
writes the older `#gh-dark-mode-only` and `#gh-light-mode-only` pair instead;
GitHub's own CSS no longer hides the other one on a repository page, so both
cards show, and it is kept only for a README rendered somewhere that still
honours the fragments.

Every card links to its entry in the catalogue, so a viewer can find what a
trophy or achievement is for and how it is earned in one click. The link goes
through `blob/HEAD`, the default branch, so it never waits on a tag.
"""
from __future__ import annotations

from html import escape

from .. import readme

NAME = "trophies"
KIT_URL = "https://github.com/tannergolden/markdown"
CATALOGUE = f"{KIT_URL}/blob/HEAD/docs/Catalogue.md"


def _img(base: str, alt: str, embed: str, width: int | None = None) -> str:
    w = f' width="{width}"' if width else ""
    alt = escape(alt, quote=True)
    if embed == "picture":
        return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}.svg">'
                f'<img src="{base}-day.svg" alt="{alt}"{w}></picture>')
    return (f'<img src="{base}.svg#gh-dark-mode-only" alt="{alt}"{w}>'
            f'<img src="{base}-day.svg#gh-light-mode-only" alt="{alt}"{w}>')


def content(out: str, mode: str, cores: list, alts: dict, pins: list, groups: list, summary: str,
            embed: str = "picture", banner: bool = True) -> str:
    """What sits between the markers.

    `out` is the case's folder as the README reaches it; `alts` maps each
    file's base name to its alt text; `pins` is a list of (group index, base,
    alt) for the achievements, in the order they are shown.
    """
    lines = []
    if banner:
        lines += ['<p align="center">', "  " + _img(f"{out}/level", alts.get("level", "Level"), embed),
                  "  " + _img(f"{out}/next-up", alts.get("next-up", "Next up"), embed), "</p>", ""]
    lines.append('<p align="center">')
    for c in cores:
        lines.append(f'  <a href="{CATALOGUE}#{mode}-{c.key}">' + _img(f"{out}/{c.key}", alts.get(c.key, c.title), embed)
                     + "</a>")
    lines += ["</p>", ""]
    if pins:
        # A case that shows no achievements has no drawer for them.
        lines += ["<details>", f"<summary><b>Achievements</b> · {summary}</summary>", ""]
        for gi, g in enumerate(groups):
            mine = [(b, a) for (gg, b, a) in pins if gg == gi]
            if not mine:
                continue
            lines += [f'<p align="center"><b>{g}</b></p>', '<p align="center">']
            for base, alt in mine:
                lines.append(f'  <a href="{CATALOGUE}#{mode}-{base}">' + _img(f"{out}/achievements/{base}", alt, embed)
                             + "</a>")
            lines += ["</p>", ""]
        lines += ["</details>", ""]
    lines += [f'<p align="center"><sub>Refreshed daily by <a href="{KIT_URL}">tannergolden/markdown</a>'
              f' · Every trophy and achievement, what it is for and how to earn it: <a href="{CATALOGUE}#{mode}">the '
              'catalogue</a>. Click any card for its entry.</sub></p>']
    return "\n".join(lines)


def block(*args, **kwargs) -> str:
    """The block, markers and all."""
    return readme.block(NAME, content(*args, **kwargs))
