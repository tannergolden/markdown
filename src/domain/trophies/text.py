# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-FileCopyrightText: 2020 The Cinzel Project Authors (Cinzel outlines)
# SPDX-FileCopyrightText: 2017 The Barlow Project Authors (Barlow Condensed outlines)
# SPDX-License-Identifier: MIT
"""Outlined lettering, so a trophy looks the same on every device.

A README image cannot load a web font, and the viewer's system font differs
by platform, so every letter on a trophy is drawn as a path: Cinzel Bold for
titles and tier names, Barlow Condensed for numbers and captions. The outlines
are the kit's shared ones (`domain.lettering`), the same a banner is drawn in.
Each SVG embeds only the glyphs it uses, once, and places them with `<use>`.

The case keeps its own id scheme, one id per glyph and no suffix, because a
case's cards are never inlined into one document together.
"""
from __future__ import annotations

from ..lettering import fonts

_KEY = {"serif": "s", "num": "n", "meta": "m"}


def _glyph(font: dict, ch: str):
    """The glyph for a character, or its uppercase, or None."""
    g = font["g"]
    if ch in g:
        return ch
    up = ch.upper()
    return up if up in g else None


def width(text: str, face: str = "meta", size: float = 9, ls: float = 0) -> float:
    """Advance width of `text` at `size`, with letter-spacing `ls` between glyphs."""
    font = fonts()[face]
    s = size / font["upem"]
    adv = 0.0
    n = 0
    for ch in text:
        key = _glyph(font, ch)
        adv += font["g"][key][1] if key else font["upem"] * 0.3
        n += 1
    return adv * s + ls * max(0, n - 1)


def f1(n: float) -> str:
    """One decimal, no trailing zero: the number format every coordinate uses."""
    r = round(n * 10) / 10
    return str(int(r)) if r == int(r) else str(r)


class Lettering:
    """Collects the glyphs one SVG uses, so `defs()` can embed each once."""

    def __init__(self) -> None:
        self.used: set[tuple[str, str]] = set()

    def text(self, s: str, *, face: str = "meta", size: float = 9, x: float = 0, y: float = 0,
             anchor: str = "start", ls: float = 0, fill: str = "#000000", opacity: float | None = None) -> str:
        font = fonts()[face]
        sc = size / font["upem"]
        w = width(s, face, size, ls)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        adv = 0.0
        uses = []
        for ch in s:
            key = _glyph(font, ch)
            if key and key != " ":
                self.used.add((face, key))
                uses.append(f'<use href="#{_KEY[face]}{ord(key)}" x="{round(adv)}"/>')
            adv += (font["g"][key][1] if key else font["upem"] * 0.3) + ls / sc
        op = f' fill-opacity="{opacity}"' if opacity is not None else ""
        return (f'<g transform="translate({f1(x0)} {f1(y)}) scale({sc:.5f} {-sc:.5f})" fill="{fill}"{op}>'
                + "".join(uses) + "</g>")

    def defs(self) -> str:
        out = []
        for face, ch in sorted(self.used, key=lambda k: (k[0], ord(k[1]))):
            out.append(f'<path id="{_KEY[face]}{ord(ch)}" d="{fonts()[face]["g"][ch][0]}"/>')
        return "".join(out)
