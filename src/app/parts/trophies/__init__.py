# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The trophy case, measured and planned: what a person or a repository has earned, and the files it makes.

Measuring reads the subject over GitHub's API into one plain dict: the core
values, a value per achievement (None where the run could not measure it),
and a few extras for the level card. `profile` measures a person, and
`repository` one repository; both read commits through `scan` under a budget.

The lock's trophies record is the case's ledger. A run folds the measurement
into it (`fold`), which is what dates a tier's NEW ribbon and gives each card
its weekly change, and keeps the measurement as `last`, so `check` and
`render` draw the committed case again without a token.

The trophies kit kept that record in `.github/trophies.lock.json`; the first
run of this kit takes it over (`adopt`), so a case keeps its history.
"""
from __future__ import annotations

import datetime as dt
import json
import posixpath

from domain.trophies import ledger as L
from domain.trophies import plan as TP
from domain.trophies import settings as TS
from domain.trophies.catalogue import MODES

from . import profile, repository
from .profile import owner_of

LOCK_KEY = "trophies"
LEGACY_LOCK = ".github/trophies.lock.json"


def adopt(text: str | None) -> dict | None:
    """The case's record from the trophies kit's lock file's text, or None when there is none to take over."""
    if not text:
        return None
    try:
        old = json.loads(text)
    except ValueError:
        return None
    return L.adopt(old) if isinstance(old, dict) else None


def measure(gh, section: dict, record: dict, *, mode: str, subject: str, today: dt.date, notes: list) -> dict:
    """The case's measurement. `record` is the lock's trophies record, whose scanner cache this fills in."""
    if mode == "repository":
        owner, _, name = subject.partition("/")
        result = repository.measure(gh, owner, name, record, today=today, scan_pages=section["scan_pages"])
    elif mode == "profile":
        result = profile.measure(gh, subject, record, today=today, private=section["private"],
                                 scan_pages=section["scan_pages"])
    else:
        raise TP.TrophiesError(f"trophies: a {mode} case is not drawn yet")
    owners: dict = {}
    for a in MODES[mode]["ach"]:
        if a.only and a.only not in owners:
            owners[a.only] = owner_of(gh, a.only)
    result["owners"] = owners
    result["today"] = today.isoformat()
    notes += result.get("notes") or []
    return result


def fold(record: dict, result: dict, section: dict, today: dt.date) -> dict:
    """Fold a run into the case's record, and return what it reached today: {"tiers": [...], "achievements": [...]}.

    Gives the measurement its weekly changes and NEW flags, and keeps it as the
    record's `last`, the measurement the committed case is drawn from.
    """
    mode = result["mode"]
    cores = TP.cores_of(section, mode)
    ach = MODES[mode]["ach"]
    before = L.reached_before(record)
    folded = L.update(record, result, cores, ach, today)
    result.setdefault("delta", folded["delta"])
    result.setdefault("new", folded["new"])
    reached = L.reached_on(record, result, cores, ach, today, before)
    L.remember(record, result)
    return reached


def plan(result: dict, section: dict, *, out: str, readme: str) -> dict:
    """Every file of the case by path, the README's block, and the facts a commit names."""
    problems = TS.for_mode(section, result["mode"])
    if problems:
        raise TP.TrophiesError("; ".join(problems))
    folder = posixpath.join(out.strip("/") or ".", "trophies")
    base = posixpath.relpath(folder, posixpath.dirname(readme) or ".")
    return TP.plan(result, section, folder=folder, base=base)
