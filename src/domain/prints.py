# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The themes a page can be drawn in: `standard`, the prints, and `rainbowprint`.

`standard` is the default. It is the original badges' own look, grown to the
size of a header, and every page is drawn in it unless the settings name
another theme.

A print is the colour a drawing is reproduced in: its lines and lettering on
white paper by day, and by night the sheet those lines are printed on. The
family runs the spectrum, red to pink, then the two the trade named first
after the blueprint, the brownprint and the blackprint. Every colour is a
palette token. By day a print's lines take `line` and its lettering `ink`,
dark enough to read on white; by night the sheet is `sheet`, lettered in
`night`: white on the deep sheets, black on the two bright ones.

The prints are data, `data/prints.json`, handed in by `infra.resources`, and a
repository adds its own under `prints:` in its settings, in the same shape: a
name for each set of colours, each a token or #RRGGBB, `label` and `night`
optional.

The holiday sets are not themes a page chooses. They take over from whichever
theme it is drawn in around each holiday, then hand it back: see `holidays`.
"""
from __future__ import annotations

import re

from .palette import DECLARED, HEX, is_colour

STANDARD = "standard"
DEFAULT_THEME = STANDARD
RAINBOW = "rainbowprint"
# The rainbow, in order. A page in `rainbowprint` is drawn in one of these and
# moves to the next each time a change redraws it.
SPECTRUM = ("redprint", "orangeprint", "yellowprint", "greenprint", "tealprint", "blueprint", "indigoprint",
            "purpleprint", "pinkprint")
FIELDS = ("label", "line", "ink", "sheet", "night")
REQUIRED = ("line", "ink", "sheet")

PRINTS: dict[str, dict] = {}
BUILTIN: tuple[str, ...] = ()
ADDED: tuple[str, ...] = ()


class PrintError(ValueError):
    pass


def _print(name: str, spec: dict) -> dict:
    return {"label": spec.get("label") or name.capitalize(), **{k: spec[k] for k in FIELDS[1:] if k in spec}}


def errors(name: object, spec: object) -> list[str]:
    """What is wrong with one print a repository defines, each said precisely."""
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        return [f"{name!r}: a print's name is lowercase letters, digits and hyphens"]
    if name in BUILTIN or name in (RAINBOW, STANDARD):
        return [f"{name}: the kit already draws a theme by that name; give yours another"]
    if not isinstance(spec, dict):
        return [f"{name}: expected a map of its colours"]
    out = [f"{name}: {k!r} is not a field (one of {', '.join(FIELDS)})" for k in spec if k not in FIELDS]
    out += [f"{name}: no {k!r}" for k in REQUIRED if k not in spec]
    out += [f"{name}: {k} {spec[k]!r} is neither a palette token nor #RRGGBB"
            for k in FIELDS[1:] if k in spec and not is_colour(spec[k])]
    if "label" in spec and not isinstance(spec["label"], str):
        out.append(f"{name}: label is text")
    return out


def use(catalogue: dict, added: dict | None = None) -> tuple[str, ...]:
    """Make `catalogue` the kit's prints and `added` the repository's, replacing any a previous call made.

    Returns the repository's names. Raises PrintError naming everything wrong
    with `added`; the kit's own catalogue is trusted.
    """
    global BUILTIN, ADDED
    PRINTS.clear()
    DECLARED.clear()
    for name, spec in catalogue.items():
        PRINTS[name] = _print(name, spec)
    BUILTIN = tuple(catalogue)
    ADDED = ()
    added = added or {}
    if not isinstance(added, dict):
        raise PrintError("prints: expected a map of each print's name to its colours")
    problems = [p for name, spec in added.items() for p in errors(name, spec)]
    if problems:
        raise PrintError("prints: " + "; ".join(problems))
    for name, spec in added.items():
        PRINTS[name] = _print(name, spec)
        DECLARED.update(v.upper() for v in spec.values() if isinstance(v, str) and HEX.fullmatch(v))
    ADDED = tuple(added)
    return ADDED


def themes() -> tuple[str, ...]:
    """Every theme a page may name: `standard`, each print, and `rainbowprint`."""
    return (STANDARD, *PRINTS, RAINBOW)


def is_theme(name: str) -> bool:
    return name in themes()


def rainbow_after(previous: str | None) -> str:
    """The print `rainbowprint` draws in next: the one after `previous` in the spectrum, or its first."""
    if previous in SPECTRUM:
        return SPECTRUM[(SPECTRUM.index(previous) + 1) % len(SPECTRUM)]
    return SPECTRUM[0]


def colours(tone: str, th: dict) -> dict:
    """A print in a theme: `line` for linework, `ink` for lettering, `paper`, and `edge`, the day sheet's outline."""
    p = PRINTS.get(tone) or PRINTS[SPECTRUM[0] if tone == RAINBOW else "blueprint"]
    dark = th["dark"]
    night = p.get("night", "white")
    return {"line": night if dark else p["line"], "ink": night if dark else p["ink"],
            "paper": p["sheet"] if dark else "white", "edge": p["line"], "dark": dark}
