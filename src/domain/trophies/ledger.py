# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The case's record in the lock: what GitHub cannot say afterwards.

Every number on a trophy is measured again on every run. The case's part of
the lock (`parts.trophies`) only adds what GitHub cannot say later: the day
each tier was first reached (for the NEW ribbon), a sparse daily history of
the core values (for the weekly change and the repository Reach
achievements), and the commit scanner's cache. Deleting it loses history,
never correctness.

It also keeps `last`: the measurement the committed case was drawn from, with
the weekly deltas and NEW flags that went into the cards. That is what lets
`check` redraw the case offline and compare, byte for byte, without a token
and without the numbers moving underneath it.

The trophies kit kept this record in `.github/trophies.lock.json`; `adopt`
takes one over, so a case keeps its history when it moves to this kit.
"""
from __future__ import annotations

import datetime as dt

from .catalogue import ROMAN, TIER_NAMES, ach_state, measure

HISTORY_DAYS = 400
NEW_FOR_DAYS = 7


def new() -> dict:
    return {"reached": {}, "history": {}, "scan": {}}


def adopt(old: dict) -> dict:
    """The case's record from the trophies kit's `.github/trophies.lock.json`: its history and dates, kept.

    The scanner's cache is left behind: that kit counted only its own
    refreshes as refreshes, and this one sets aside every kit's, so each
    repository is read again once.
    """
    out = new()
    for key in ("reached", "history"):
        if isinstance(old.get(key), dict):
            out[key] = old[key]
    return out


def reached_on(ledger: dict, result: dict, cores: list, ach: list, today: dt.date, before: dict | None = None) -> dict:
    """What was first reached on `today` and is still held.

    A tier's date stays in the ledger after a threshold moves up and the tier
    is lost, so the date alone would report a Bronze the card no longer
    shows. Only a tier or achievement the run holds right now is named.

    `before` is the ledger's `reached` map as the run read it (see
    `reached_before`). Given, it narrows the answer to what this run reached
    itself: the ledger dates by the day, so a second run on the same day
    would otherwise name again everything the first one reached."""
    key = today.isoformat()
    out = {"tiers": [], "achievements": []}
    reached = ledger.get("reached", {})
    prior = before or {}
    for c in cores:
        m = measure(c, result["values"][c.key])
        for stamp, day in reached.get(c.key, {}).items():
            t, stars = (int(x) for x in stamp.split("."))
            if day == key and stamp not in prior.get(c.key, {}) and (m["t"] > t or (m["t"] == t and m["stars"] >= stars)):
                out["tiers"].append((TIER_NAMES[t] + (f" star {stars}" if stars else ""), c.title))
    for a in ach:
        st = ach_state(a, result["curs"].get(a.slug))
        for k, day in reached.get("ach:" + a.slug, {}).items():
            if day == key and k not in prior.get("ach:" + a.slug, {}) and st["earned"] and st["k"] >= int(k):
                out["achievements"].append(a.name + (f" {ROMAN[int(k)]}" if a.goals else ""))
    return out


def reached_before(ledger: dict) -> dict:
    """A copy of the ledger's `reached` map, taken before a run folds itself in with `update`."""
    return {k: dict(v) for k, v in ledger.get("reached", {}).items()}


def update(ledger: dict, result: dict, cores: list, ach: list, today: dt.date) -> dict:
    """Fold a run into the ledger and return what the cards need from it.

    Returns {"new": {core key: bool}, "delta": {core key: int}, "reached": {...}}.
    """
    key = today.isoformat()
    reached = ledger.setdefault("reached", {})
    history = ledger.setdefault("history", {})
    new, delta = {}, {}
    for c in cores:
        m = measure(c, result["values"][c.key])
        stamp = f"{m['t']}.{m['stars']}"
        rec = reached.setdefault(c.key, {})
        if m["t"] and stamp not in rec:
            rec[stamp] = key
        since = rec.get(stamp)
        new[c.key] = bool(since) and (today - dt.date.fromisoformat(since)).days < NEW_FOR_DAYS and m["t"] > 0
        h = history.setdefault(c.key, {})
        # Sparse: a point is written only when the value moved, so a quiet
        # day leaves the ledger untouched and produces no commit.
        latest = max(h) if h else None
        if latest is None or h[latest] != result["values"][c.key]:
            h[key] = result["values"][c.key]
        for old in [d for d in h if (today - dt.date.fromisoformat(d)).days > HISTORY_DAYS]:
            del h[old]
        week_ago = (today - dt.timedelta(days=7)).isoformat()
        at_or_before = sorted(d for d in h if d <= week_ago)
        base = h[at_or_before[-1]] if at_or_before else None
        delta[c.key] = max(0, result["values"][c.key] - base) if base is not None else 0
    for a in ach:
        st = ach_state(a, result["curs"].get(a.slug))
        if st["earned"]:
            rec = reached.setdefault("ach:" + a.slug, {})
            rec.setdefault(str(st["k"]), key)
    return {"new": new, "delta": delta, "reached": reached}


LAST_KEYS = ("mode", "subject", "today", "values", "curs", "extra", "owners", "delta", "new", "unmeasured")


def remember(ledger: dict, result: dict) -> None:
    """Keep what `render.plan` needs to draw this case again, and nothing else."""
    ledger["last"] = {k: result[k] for k in LAST_KEYS if k in result}


def last(ledger: dict):
    """The measurement the committed case was drawn from, or None."""
    return ledger.get("last")


def value_at(ledger: dict, key: str, day: dt.date):
    """The recorded value of a core key on `day`, from the sparse history."""
    h = ledger.get("history", {}).get(key, {})
    at_or_before = sorted(d for d in h if d <= day.isoformat())
    return h[at_or_before[-1]] if at_or_before else None
