# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The `trophies:` section of a page's settings: how the case is drawn, with a default for everything.

Whose case it is, where its files go and whether the lock keeps its history
are the page's (`mode`, `subject`, `out`, `lock`); everything else is here:

  style         trophy (a cup), crest, medallion, crystal or plaque
  case          both, or only night or only day
  embed         picture (a <picture> that follows the reader's theme), or fragment
                (the #gh-dark-mode-only links GitHub no longer honours)
  banner        the level and next-up cards above the trophies
  streak        current or longest: which streak the level card leads with (a profile's)
  core          a subset of the mode's core trophies, in order; empty for all of them
  enamel        a core trophy's colour, as a palette token
  achievements  all, none, or a list of their slugs
  card          what a trophy card shows besides its tier: rank, weekly, new
  private       count private contributions too (needs MARKDOWN_TOKEN)
  scan_pages    how many pages of commits (a hundred each) a run reads at most
  block         false draws the files but leaves the README to its author
"""
from __future__ import annotations

from .catalogue import MODES

DEFAULTS = {
    "style": "trophy",
    "case": "both",
    "embed": "picture",
    "banner": True,
    "streak": "current",
    "core": [],
    "enamel": {},
    "achievements": "all",
    "card": ["rank", "weekly", "new"],
    "private": False,
    "scan_pages": 30,
    "block": True,
}
CHOICES = {"style": ("trophy", "crest", "medallion", "crystal", "plaque"), "case": ("both", "night", "day"),
           "embed": ("picture", "fragment"), "streak": ("current", "longest")}
CARD = ("rank", "weekly", "new")
BOOLS = ("banner", "private", "block")
# Settings the trophies kit read that are now the page's, and two it named otherwise.
PAGE = {"mode": "mode", "subject": "subject", "out": "out", "ledger": "lock", "readme_path": "readme"}
RENAMED = {"theme": "embed (picture or fragment)", "readme": "block (false leaves the README to its author)"}


class TrophiesSettingsError(ValueError):
    pass


def _bool(k: str, v: object) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "false"):
        return v.strip().lower() == "true"
    raise TrophiesSettingsError(f"trophies: {k.replace('_', '-')}: expected true or false, not {v!r}")


def check(section) -> dict:
    """The section in full, every value checked, every default filled in."""
    if section in (None, True):
        section = {}
    if not isinstance(section, dict):
        raise TrophiesSettingsError("trophies: expected false, or a map of how the case is drawn")
    cfg = {k: (list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    for k, v in section.items():
        key = str(k).replace("-", "_")
        if key in PAGE:
            raise TrophiesSettingsError(f"trophies: {k} is the page's now; set {PAGE[key]} at the top of the settings")
        if key in RENAMED:
            raise TrophiesSettingsError(f"trophies: {k} is called {RENAMED[key]} now")
        if key not in DEFAULTS:
            raise TrophiesSettingsError(f"trophies: unknown key {k!r} (one of {', '.join(DEFAULTS)})")
        if v is not None:
            cfg[key] = v
    for k, allowed in CHOICES.items():
        if cfg[k] not in allowed:
            raise TrophiesSettingsError(f"trophies: {k}: {cfg[k]!r} is not one of {', '.join(allowed)}")
    for k in BOOLS:
        cfg[k] = _bool(k, cfg[k])
    for k in ("core", "card"):
        if isinstance(cfg[k], str):
            cfg[k] = [cfg[k]]
        if not isinstance(cfg[k], list):
            raise TrophiesSettingsError(f"trophies: {k}: expected a list")
    keys = {c.key for m in MODES.values() for c in m["core"]}
    for k in cfg["core"]:
        if k not in keys:
            raise TrophiesSettingsError(f"trophies: core: {k!r} is not a core trophy ({', '.join(sorted(keys))})")
    if not isinstance(cfg["enamel"], dict):
        raise TrophiesSettingsError("trophies: enamel: expected a map of each core trophy to a palette token")
    for k in cfg["enamel"]:
        if k not in keys:
            raise TrophiesSettingsError(f"trophies: enamel: {k!r} is not a core trophy")
    for k in cfg["card"]:
        if k not in CARD:
            raise TrophiesSettingsError(f"trophies: card: {k!r} is not one of {', '.join(CARD)}")
    if cfg["achievements"] not in ("all", "none") and not isinstance(cfg["achievements"], list):
        raise TrophiesSettingsError("trophies: achievements: expected all, none or a list of slugs")
    if isinstance(cfg["scan_pages"], bool) or not isinstance(cfg["scan_pages"], int) or cfg["scan_pages"] < 0:
        raise TrophiesSettingsError(f"trophies: scan-pages: expected a whole number, not {cfg['scan_pages']!r}")
    return cfg


def for_mode(cfg: dict, mode: str) -> list[str]:
    """What in the section a case in `mode` cannot honour: a core trophy or an enamel of the other mode's."""
    keys = {c.key for c in MODES[mode]["core"]} if mode in MODES else set()
    out = [f"trophies: core: {k!r} is not a {mode} trophy ({', '.join(sorted(keys))})" for k in cfg["core"]
           if k not in keys]
    out += [f"trophies: enamel: {k!r} is not a {mode} trophy" for k in cfg["enamel"] if k not in keys]
    return out
