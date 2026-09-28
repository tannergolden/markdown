# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""`.github/markdown.yml`: a page's settings, with a default for every one of them.

A page that writes no settings at all is drawn from what GitHub says about it,
in the `standard` theme, with the holidays on. Everything is optional, and the
one file holds all of it: the page as a whole at the top, then a section for
each part (`banners`, `badges`, `elements`, `trophies`), which each part checks
for itself as it reads it.

The stub can set four of these too (`mode`, `theme`, `holidays` and
`holiday-days`), so the choices a person makes most often sit in the workflow
they already have open. A value the stub sets wins over the file's.

Every key is checked, and an unknown key or value fails the run with the key
named, rather than being ignored. A key may be written with hyphens or with
underscores: `holiday-days` and `holiday_days` are the same key.
"""
from __future__ import annotations

import re
from typing import Callable

from . import holidays
from .prints import DEFAULT_THEME, RAINBOW, PrintError, is_theme, themes, use as use_prints

MODES = ("profile", "repository", "organization")
PARTS = ("banners", "badges", "elements", "trophies")
DEFAULTS = {
    "mode": "auto",            # profile | repository | organization; auto guesses from the repository
    "subject": "",             # a login, an organization, or owner/name; empty: this repository or its owner
    "theme": DEFAULT_THEME,    # standard, a print, rainbowprint, or one of `prints`
    "holidays": True,          # each holiday's set takes over around its day
    "holiday_days": holidays.DEFAULT_DAYS,  # 3 to 7; New Year's Day always runs 3
    "timezone": "UTC",         # the zone the page's day changes in, so a holiday starts at its midnight
    "readme": "",              # empty: README.md, or profile/README.md for an organization
    "out": "",                 # empty: assets/markdown, beside the README for an organization
    "lock": True,              # keep .github/markdown.lock.json, so `check` can redraw without a token
    "prints": {},              # the repository's own prints, each a name and its colours
    "banners": True,           # each part: true or left out for its defaults, false for none, or its settings
    "badges": True,
    "elements": True,
    "trophies": True,
}
TEXT = ("subject", "timezone", "readme", "out")
# The keys the stub can set, as the workflow passes them: every value a string, "" for not set.
INPUTS = ("mode", "theme", "holidays", "holiday_days")
_ZONE = re.compile(r"UTC|[A-Za-z][A-Za-z0-9_+-]*(?:/[A-Za-z0-9_+-]+){0,2}")
_SUBJECT = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})(?:/[A-Za-z0-9._-]{1,100})?")


class SettingsError(ValueError):
    pass


def _key(k: object) -> str:
    return str(k).replace("-", "_")


def _bool(k: str, v: object) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "false"):
        return v.strip().lower() == "true"
    raise SettingsError(f"{k.replace('_', '-')}: expected true or false, not {v!r}")


def from_inputs(inputs: dict) -> dict:
    """The settings the stub set, from the workflow's inputs: strings, with "" for not set."""
    out: dict = {}
    for k, v in (inputs or {}).items():
        k = _key(k)
        if k not in INPUTS:
            raise SettingsError(f"the stub has no input {k.replace('_', '-')!r} (one of "
                                f"{', '.join(i.replace('_', '-') for i in INPUTS)})")
        v = "" if v is None else str(v).strip()
        if not v:
            continue
        if k == "holidays":
            out[k] = _bool(k, v)
        elif k == "holiday_days":
            if not re.fullmatch(r"\d+", v):
                raise SettingsError(f"holiday-days: expected a whole number, not {v!r}")
            out[k] = int(v)
        else:
            out[k] = v
    return out


def validate(given: dict | None, inputs: dict | None = None, *, catalogue: dict | None = None,
             parts: dict[str, Callable[[object], object]] | None = None, where: str = "the settings") -> dict:
    """The full settings: defaults, under what the file gave, under what the stub set, every value checked.

    `catalogue` is the kit's own prints, which the repository's `prints` are
    added to (and checked against) when it is given. `parts` maps a part's
    section to the function that checks it and returns it in full; a part not
    named keeps its section as given, once its shape is checked.
    """
    cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    if given is not None and not isinstance(given, dict):
        raise SettingsError(f"{where}: expected a map of settings")
    for k, v in (given or {}).items():
        k = _key(k)
        if k not in DEFAULTS:
            raise SettingsError(f"unknown key in {where}: {k.replace('_', '-')}")
        if v is not None:
            cfg[k] = v
    cfg.update(from_inputs(inputs or {}))
    for k in TEXT:
        cfg[k] = "" if cfg[k] is None else str(cfg[k]).strip()
    if cfg["mode"] not in ("auto", *MODES):
        raise SettingsError(f"mode: {cfg['mode']!r} is not one of auto, {', '.join(MODES)}")
    if cfg["subject"] and not _SUBJECT.fullmatch(cfg["subject"]):
        raise SettingsError(f"subject: {cfg['subject']!r} is not a login, an organization or owner/name")
    cfg["holidays"] = _bool("holidays", cfg["holidays"])
    try:
        cfg["holiday_days"] = holidays.check_days(cfg["holiday_days"])
    except holidays.HolidayError as exc:
        raise SettingsError(str(exc)) from exc
    if not _ZONE.fullmatch(cfg["timezone"]):
        raise SettingsError(f"timezone: {cfg['timezone']!r} is not a time zone name like UTC or America/New_York")
    cfg["lock"] = _bool("lock", cfg["lock"])
    for k in ("readme", "out"):
        path = cfg[k]
        if path and (path.startswith("/") or ".." in path.split("/") or "\\" in path):
            raise SettingsError(f"{k}: {path!r} must be a path inside the repository, with forward slashes")
    if not isinstance(cfg["prints"], dict):
        raise SettingsError("prints: expected a map of each print's name to its colours")
    if catalogue is not None:
        try:
            use_prints(catalogue, cfg["prints"])
        except PrintError as exc:
            raise SettingsError(str(exc)) from exc
    cfg["theme"] = str(cfg["theme"]).strip()
    if not is_theme(cfg["theme"]):
        raise SettingsError(f"theme: {cfg['theme']!r} is not one of {', '.join(themes())}; "
                            "a repository adds its own under prints")
    if cfg["theme"] == RAINBOW and not cfg["lock"]:
        raise SettingsError("theme: rainbowprint remembers its last colour in the lock; set lock: true")
    for part in PARTS:
        value = cfg[part]
        if not isinstance(value, (bool, dict, list)):
            raise SettingsError(f"{part}: expected true, false, or its settings")
        check = (parts or {}).get(part)
        if check is not None and value is not False:
            cfg[part] = check({} if value is True else value)
    return cfg


def guess_mode(owner: str, name: str, organization: bool) -> str:
    """The mode a repository is drawn in when the settings say `auto`.

    A person's repository named after them is their profile; an organization's
    `.github` or `.github-private` is the organization's; anything else is a
    repository.
    """
    if organization and name.lower() in (".github", ".github-private"):
        return "organization"
    if not organization and name.lower() == owner.lower():
        return "profile"
    return "repository"


def readme_path(cfg: dict, mode: str) -> str:
    """Where the page is: the settings' `readme`, or the mode's own place."""
    return cfg["readme"] or ("profile/README.md" if mode == "organization" else "README.md")


def out_dir(cfg: dict, mode: str) -> str:
    """Where the files are written: the settings' `out`, or beside the page."""
    return cfg["out"] or ("profile/assets/markdown" if mode == "organization" else "assets/markdown")
