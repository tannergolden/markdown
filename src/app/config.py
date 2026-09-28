# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Reading a repository's settings: the file, the stub's inputs, and the defaults under both."""
from __future__ import annotations

from pathlib import Path

from domain import settings

# The settings file, by the name the standards give a new YAML file, and by the
# name the workflow beside it would suggest. One of them, not both.
NAMES = (".github/markdown.yaml", ".github/markdown.yml")


def find(root: Path, ports) -> tuple[str | None, str | None]:
    """The settings file's path relative to `root` and its text, or (None, None) when there is none."""
    found = [(name, text) for name in NAMES if (text := ports.read_text(Path(root) / name)) is not None]
    if len(found) > 1:
        raise settings.SettingsError(f"both {NAMES[0]} and {NAMES[1]} are here; keep one")
    return found[0] if found else (None, None)


def load(root: Path, ports, inputs: dict | None = None, parts: dict | None = None) -> dict:
    """The repository's full settings, every value checked."""
    where, text = find(root, ports)
    given = None
    if text is not None:
        try:
            given = ports.parse_yaml(text)
        except ValueError as exc:
            raise settings.SettingsError(f"{where}: {exc}") from exc
    return settings.validate(given, inputs, catalogue=ports.catalogue, parts=parts, where=where or "the settings")
