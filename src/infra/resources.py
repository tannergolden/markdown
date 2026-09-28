# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The kit's own data files, read from `src/domain/data/` and handed to the domain.

The domain does no I/O, so the outlines it letters with and the prints it draws
in are read here and handed in: `install()` is the first thing a run does.
"""
from __future__ import annotations

import json
from pathlib import Path

from domain import lettering, prints

DATA = Path(__file__).resolve().parents[1] / "domain" / "data"
FONTS = DATA / "fonts"
# The glyph tables, earlier first: a later one only adds characters an earlier one lacks.
GLYPHS = ("glyphs.json", "glyphs-extra.json")
# Faces kept in files of their own, each with its font's metadata around the face.
FACES = {"jetbrains-mono.json": "mono"}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def glyph_tables() -> list[dict]:
    tables = [_json(FONTS / name) for name in GLYPHS]
    tables += [{face: _json(FONTS / name)[face]} for name, face in FACES.items()]
    return tables


def catalogue() -> dict:
    """The kit's own prints, as `data/prints.json` lists them."""
    return _json(DATA / "prints.json")


def install() -> dict:
    """Hand the outlines and the kit's prints to the domain. Returns the prints catalogue."""
    lettering.use(*glyph_tables())
    cat = catalogue()
    prints.use(cat)
    return cat
