# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The kit's own data files, read from `src/domain/data/` and handed to the domain.

The domain does no I/O, so the outlines it letters with, the prints it draws
in and the repository population the trophies are calibrated against are read
here and handed in: `install()` is the first thing a run does.
"""
from __future__ import annotations

import json
from pathlib import Path

from domain import lettering, prints
from domain.trophies import calibration

DATA = Path(__file__).resolve().parents[1] / "domain" / "data"
FONTS = DATA / "fonts"
# The glyph tables, earlier first: a later one only adds characters an earlier one lacks.
GLYPHS = ("glyphs.json", "glyphs-extra.json")
# Faces kept in files of their own, each with its font's metadata around its faces.
FACES = {"jetbrains-mono.json": ("mono",), "dejavu-sans.json": ("sans", "sans-bold")}
# What `markdown-kit calibrate` measured of the repository population, when it has been run.
CALIBRATION = DATA / "calibration" / "repositories.json"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def glyph_tables() -> list[dict]:
    tables = [_json(FONTS / name) for name in GLYPHS]
    for name, faces in FACES.items():
        data = _json(FONTS / name)
        tables.append({face: data[face] for face in faces})
    return tables


def catalogue() -> dict:
    """The kit's own prints, as `data/prints.json` lists them."""
    return _json(DATA / "prints.json")


def repository_sample() -> dict | None:
    """The measured repository population, or None before `calibrate` has been run."""
    return _json(CALIBRATION) if CALIBRATION.is_file() else None


def install() -> dict:
    """Hand the outlines, the kit's prints and the calibration to the domain. Returns the prints catalogue."""
    lettering.use(*glyph_tables())
    cat = catalogue()
    prints.use(cat)
    calibration.use(repository_sample())
    return cat
