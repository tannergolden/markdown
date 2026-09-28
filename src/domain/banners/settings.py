# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The `banners:` section of a page's settings, with a default for everything in it.

An empty text field means "read it from GitHub": the title is the
repository's name or the person's, the tagline its description or their
bio. Setting one keeps it; listing a field under `hide` leaves it out of the
drawing. So a page that says nothing gets banners that read its repository
or profile, and keep reading it as it changes.

The theme, the mode, the subject, where the files go and the README they
go in are the page's, not the banners': they sit at the top of the settings
file, and naming one here says so rather than guessing.
"""
from __future__ import annotations

from .compose import FIGURES, MAX_LINKS, MAX_NOTES
from .content import FOOTER_FIELDS, HEADER_FIELDS

DEFAULTS = {
    "header": "section",       # sheet | section | strip | none; section is what a page that says nothing gets
    "footer": "",              # title-block | scale-bar | none; empty means the one made for the header
    "title": "",               # empty: the repository's name, or the person's name
    "tagline": "",             # empty: the repository's description, or the bio
    "motto": "",               # the sheet's first general note; empty: none, or on a profile the status message
    "notes": [],               # up to two more general notes, numbered after the motto
    "description": "",         # a longer line under the notes; empty: none
    "figures": [],             # which figures, in order; empty means the mode's defaults
    "closing": "",             # the footer's closing phrase; empty: none
    "top": "Back to Top",      # the footer's way back up
    "links": [],               # up to four buttons under the footer; empty: the first four pages GitHub has for it
    "hide": [],                # fields that are not drawn
}
CHOICES = {
    "header": {"sheet", "section", "strip", "none"},
    "footer": {"", "title-block", "scale-bar", "none"},
}
TEXT = ("title", "tagline", "motto", "description", "closing", "top")
# What the banners kit's own config held and now belongs to the page as a whole.
PAGE = {"mode", "subject", "theme", "readme", "readme_path", "out", "lock"}
# What that kit read and set aside for configs written for its 1.0: a key, and names under `hide`.
RETIRED = frozenset({"emoji"})
RETIRED_FIELDS = frozenset({"emoji", "divider"})


class BannersError(ValueError):
    pass


def _links(value) -> list:
    """`links` as [[label, url], ...], from a map of label to URL or a list of "Label | URL" lines."""
    if isinstance(value, dict):
        pairs = list(value.items())
    elif isinstance(value, list):
        pairs = []
        for item in value:
            if isinstance(item, dict) and len(item) == 1:
                pairs += list(item.items())
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                pairs.append(tuple(item))
            elif isinstance(item, str) and "|" in item:
                label, _, url = item.partition("|")
                pairs.append((label, url))
            else:
                raise BannersError(f"banners: links: cannot read {item!r}; write Label | URL, or a map of label: URL")
    else:
        raise BannersError("banners: links: expected a map of label: URL, or a list of Label | URL")
    out = [[str(label).strip(), str(url).strip()] for label, url in pairs]
    bad = [label for label, url in out if not label or not url]
    if bad:
        raise BannersError(f"banners: links: every link needs a label and a URL ({bad!r})")
    if len(out) > MAX_LINKS:
        raise BannersError(f"banners: links: at most {MAX_LINKS}, the buttons the row under the footer holds "
                           f"({len(out)} given)")
    return out


def _notes(value) -> list:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise BannersError("banners: notes: expected a list of notes, each a line of text")
    out = [str(n).strip() for n in value if n is not None and str(n).strip()]
    if len(out) > MAX_NOTES:
        raise BannersError(f"banners: notes: at most {MAX_NOTES} after the motto ({len(out)} given)")
    return out


def check(given: dict | None) -> dict:
    """The full `banners:` section: defaults under what was given, every key and value checked."""
    if given is not None and not isinstance(given, dict):
        raise BannersError("banners: expected true, false, or a map of its settings")
    cfg = {k: (list(v) if isinstance(v, list) else v) for k, v in DEFAULTS.items()}
    for k, v in (given or {}).items():
        k = str(k).replace("-", "_")
        if k in RETIRED:
            continue
        if k in PAGE:
            raise BannersError(f"banners: {k.replace('_', '-')} is the page's, not the banners': "
                               "set it at the top of the settings")
        if k not in DEFAULTS:
            raise BannersError(f"banners: unknown key {k.replace('_', '-')}")
        if v is not None:
            cfg[k] = v
    for k in TEXT:
        cfg[k] = "" if cfg[k] is None else str(cfg[k])
    for k, allowed in CHOICES.items():
        if cfg[k] not in allowed:
            raise BannersError(f"banners: {k}: {cfg[k]!r} is not one of {sorted(a for a in allowed if a)}")
    for k in ("figures", "hide"):
        if isinstance(cfg[k], str):
            cfg[k] = [cfg[k]]
        if not isinstance(cfg[k], list):
            raise BannersError(f"banners: {k}: expected a list")
        cfg[k] = [str(x) for x in cfg[k] if k != "hide" or str(x) not in RETIRED_FIELDS]
    known = {key for keys in FIGURES.values() for key in keys}
    for k in cfg["figures"]:
        if k not in known:
            raise BannersError(f"banners: figures: {k!r} is not a figure ({', '.join(sorted(known))})")
    fields = set(HEADER_FIELDS) | set(FOOTER_FIELDS)
    for k in cfg["hide"]:
        if k not in fields:
            raise BannersError(f"banners: hide: {k!r} is not a field ({', '.join(sorted(fields))})")
    cfg["notes"] = _notes(cfg["notes"])
    cfg["links"] = _links(cfg["links"]) if cfg["links"] else []
    return cfg
