# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A badge's value set from outside a run: `markdown-kit set NAME=MESSAGE[:COLOR]`.

A workflow that measures what the kit does not, like a test count, a coverage
figure or a deploy, writes the value into the badge's entry in the settings
file, and the next run draws it. The file is edited in place, a line per value,
so its comments and its layout stay as they were: an entry's `message:` line is
rewritten, and its `message_color:` line too when a colour is given, added under
the message when the entry has none.
"""
from __future__ import annotations

import re

from ..palette import PALETTE

# Words YAML reads as something other than text in one version or another, so a message that is one is quoted.
_LEXICON = {"yes", "no", "on", "off", "true", "false", "null", "~"}
_HEX = re.compile(r"#[0-9a-fA-F]{6}")
_TOP = re.compile(r"[A-Za-z_][\w-]*\s*:")
_ENTRY = re.compile(r"\s*-\s+name:\s*['\"]?([A-Za-z0-9-]+)['\"]?\s*(?:#.*)?$")
_MESSAGE = re.compile(r"(\s*)message:\s*\S.*$")
_COLOUR = re.compile(r"(\s*)message[_-]color:\s*\S.*$")


def scalar(value: str) -> str:
    """`value` as a YAML scalar that reads back as the same text: quoted wherever YAML would read anything else."""
    if (re.search(r"[:#'\"\[\]{},&*!|>%@`]|^\s|\s$|^[\d\-?]", value) or value == ""
            or value.lower() in _LEXICON):
        return "'" + value.replace("'", "''") + "'"
    return value


def update(spec: str) -> tuple[str, str, str | None]:
    """NAME=MESSAGE[:COLOR] as (name, message, colour or None).

    What follows the last colon is the colour only when it is one, a palette
    token or #RRGGBB, so a message with a colon in it passes through whole.
    """
    name, sep, value = spec.partition("=")
    if not sep or not name.strip():
        raise ValueError(f"set: expected NAME=MESSAGE[:COLOR], not {spec!r}")
    message, colour = value, None
    head, colon, tail = value.rpartition(":")
    if colon and (tail in PALETTE or _HEX.fullmatch(tail)):
        message, colour = head, tail
    return name.strip(), message, colour


def _section(lines: list[str]) -> tuple[int, int]:
    """The lines of the `badges:` section: from its key to the next top-level key."""
    start = next((i for i, line in enumerate(lines) if re.match(r"badges\s*:", line)), None)
    if start is None:
        return 0, 0
    end = next((i for i in range(start + 1, len(lines)) if _TOP.match(lines[i])), len(lines))
    return start, end


def set_values(text: str, updates: dict[str, tuple[str, str | None]]) -> tuple[str, list[str]]:
    """`text` with each named badge's message, and colour where one is given, rewritten in place.

    An entry with no message line yet, like a live badge no workflow has set,
    gets one under its name. Returns the new text and the names it found no
    entry for, written `- name: NAME`. When any is missing the text comes back
    unchanged: all of them are set, or none.
    """
    lines = text.split("\n")
    start, end = _section(lines)
    current = None
    entries: dict[str, tuple[int, str]] = {}
    found: dict[str, tuple[int, str]] = {}
    coloured: set[str] = set()
    for i in range(start, end):
        line = lines[i]
        if line.lstrip().startswith("#"):
            continue
        m = _ENTRY.match(line)
        if m:
            current = m.group(1)
            entries[current] = (i, " " * line.index("name:"))
            continue
        if current not in updates:
            continue
        message, colour = updates[current]
        m = _MESSAGE.match(line)
        if m:
            lines[i] = f"{m.group(1)}message: {scalar(message)}"
            found[current] = (i, m.group(1))
        m = _COLOUR.match(line)
        if m and colour:
            lines[i] = f"{m.group(1)}message_color: {colour}"
            coloured.add(current)
    missing = sorted(set(updates) - set(entries))
    if missing:
        return text, missing
    # What an entry lacks goes in from the bottom up, so each index holds: a colour under its message, and a
    # message, with its colour, under the name of an entry that had none.
    inserts = []
    for name, (message, colour) in updates.items():
        colour_line = [] if not colour or name in coloured else [f"message_color: {colour}"]
        i, indent = found.get(name) or entries[name]
        added = colour_line if name in found else [f"message: {scalar(message)}", *colour_line]
        if added:
            inserts.append((i, [indent + line for line in added]))
    for i, added in sorted(inserts, reverse=True):
        lines[i + 1:i + 1] = added
    return "\n".join(lines), []
