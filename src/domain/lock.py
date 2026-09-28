# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The lock, `.github/markdown.lock.json`: what the committed files were drawn from.

Every value on a page is measured again on every run. The lock keeps only what
GitHub cannot say again afterwards, and what `check` needs to redraw the
committed files offline and compare them byte for byte, without a token and
without the numbers moving underneath it:

  drawn     the theme the page was drawn in: its name, the print rainbowprint
            was on, the holiday whose set had taken over, and the day
  parts     each part's own record, which that part owns: the banners' last
            measurement, the trophies' history, and so on
  snapshot  the day the lock was last written for its own sake

It is written when a drawing changed, and once a week besides: a real commit,
which keeps GitHub from switching off the schedule after sixty quiet days in a
repository nobody is pushing to. Deleting it loses history, never correctness.

This module is the lock's shape only; reading and writing the file is
`infra.files`.
"""
from __future__ import annotations

import datetime as dt

VERSION = 1
SNAPSHOT_DAYS = 7


class LockError(ValueError):
    pass


def new() -> dict:
    return {"version": VERSION, "drawn": None, "parts": {}, "snapshot": None}


def normalise(data: object) -> dict:
    """A lock read from disk, checked and filled in; a version this kit does not know is refused."""
    if data is None:
        return new()
    if not isinstance(data, dict):
        raise LockError("the lock is not a JSON object")
    version = data.get("version", VERSION)
    if version != VERSION:
        raise LockError(f"the lock is version {version!r}; this kit reads version {VERSION}")
    out = new()
    out.update({k: data[k] for k in ("drawn", "parts", "snapshot") if k in data})
    if not isinstance(out["parts"], dict):
        raise LockError("the lock's parts are not a JSON object")
    return out


def drawn(lock: dict) -> dict | None:
    """The theme the committed files were drawn in, or None before the first run."""
    return lock.get("drawn")


def remember_drawn(lock: dict, *, theme: str, today: dt.date, holiday: str | None = None,
                   rainbow: str | None = None) -> None:
    lock["drawn"] = {"theme": theme, "holiday": holiday, "rainbow": rainbow, "day": today.isoformat()}


def part(lock: dict, name: str) -> dict:
    """A part's own record, made empty the first time it is asked for."""
    return lock["parts"].setdefault(name, {})


def snapshot_due(lock: dict, today: dt.date) -> bool:
    stamp = lock.get("snapshot")
    return stamp is None or (today - dt.date.fromisoformat(stamp)).days >= SNAPSHOT_DAYS


def mark_snapshot(lock: dict, today: dt.date) -> None:
    lock["snapshot"] = today.isoformat()
