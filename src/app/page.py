# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""One run's page: whose it is, which mode, what day, where its files go, and which theme it is drawn in.

Everything a part needs to know that is not its own measurement. It is
settled once per run, from the settings, the repository the run is in, the
clock and the lock, and every part draws from the same one, so a page never
mixes two themes or two days.

A page in a collection is drawn in the collection's design for the month (see
`collections`), and a holiday's set still takes over around its day. The
trophies keep the standard look on such a page: the designs draw the banners,
the badges and the elements. A page that follows the collection's calendar
carries the month's mark in its headers; a page that keeps one design all
year does not. A page that chose a sign, `sign: leo`, carries that one
instead, either way.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from domain import collections, holidays, lock, prints, settings


@dataclass(frozen=True)
class Page:
    root: Path
    cfg: dict
    mode: str               # profile | repository | organization
    subject: str            # a login or an organization, or owner/name in repository mode
    here: str               # owner/name of the repository the README is in
    today: dt.date
    readme: str             # the README's path, relative to the root
    out: str                # the folder the files go in, relative to the root
    theme: str              # what the page is drawn in: standard, or a print (rainbowprint resolved to one);
                            # standard for a collection, which the trophies keep
    rainbow: str | None     # the print rainbowprint is on, or None for any other theme
    holiday: holidays.Window | None  # the holiday whose set draws the page today, or None
    design: str = ""        # the collection's design for the month, or the design the settings name; ""
                            # for any other theme. A holiday's set still draws the page while it is up

    @property
    def held(self) -> str:
        """The key of the holiday set the page is drawn in today, or "" for its own theme."""
        return self.holiday.key if self.holiday else ""

    @property
    def pinned(self) -> bool:
        """Whether the settings name one design of a collection, which the page keeps all year."""
        return bool(self.design) and self.cfg["theme"] == self.design

    @property
    def drawn_in(self) -> str:
        """What the parts are told to draw in: a holiday set's key and the day its holiday falls on; the
        collection's design for the month and the day, which tells the design it is drawn as the month's and
        gives its headers the month's mark; the design the settings name, alone, for a page that keeps it all
        year and carries no mark; or "" for the page's own theme. A design comes with the sign the page chose
        after it, `medieval-forge:leo`, which its headers carry in place of the month's."""
        if self.holiday:
            return f"{self.holiday.key}:{self.holiday.day.isoformat()}"
        if not self.design:
            return ""
        drawn = self.design if self.pinned else f"{self.design}:{self.today.isoformat()}"
        sign = self.cfg.get("sign") or ""
        return f"{drawn}:{sign}" if sign else drawn


def here_of(root: Path, ports) -> str:
    """owner/name of the repository the run is in: what GitHub Actions says, else what `origin` says."""
    given = (ports.env.get("GITHUB_REPOSITORY") or "").strip()
    if given:
        return given
    slug = ports.slug(root)
    return f"{slug[0]}/{slug[1]}" if slug else ""


def mode_and_subject(cfg: dict, here: str, organization: bool = False) -> tuple[str, str]:
    """The mode a page is drawn in and whose page it is, from the settings and the repository it is in."""
    mode, subject = cfg["mode"], cfg["subject"]
    owner, _, name = here.partition("/")
    if mode == "auto":
        if subject:
            mode = "repository" if "/" in subject else "profile"
        elif owner and name:
            mode = settings.guess_mode(owner, name, organization)
        else:
            mode = "repository"
    if mode == "repository":
        subject = subject or here
        if "/" not in subject:
            raise settings.SettingsError("repository mode needs subject: owner/name, or a run inside the repository")
    else:
        subject = subject or owner
        if not subject:
            raise settings.SettingsError(f"{mode} mode needs subject: a login, or a run inside the repository")
    return mode, subject


def shade(cfg: dict, lk: dict) -> str | None:
    """The print rainbowprint is on: the lock's, else the spectrum's first. None for any other theme."""
    if cfg["theme"] != prints.RAINBOW:
        return None
    was = (lock.drawn(lk) or {}).get("rainbow")
    return was if was in prints.SPECTRUM else prints.SPECTRUM[0]


def settle(root: Path, cfg: dict, *, mode: str, subject: str, here: str, today: dt.date, lk: dict,
           rainbow: str | None = None) -> Page:
    """The page, with its theme resolved: a rainbowprint drawn in `rainbow`, or the lock's shade, or the first;
    a collection in its design for the month of `today`."""
    tone = rainbow if rainbow else shade(cfg, lk)
    window = holidays.active(today, cfg["holiday_days"], cfg["holidays"])
    if window and not holidays.drawn_by(window.key):
        window = None   # its set is not drawn yet, so the page keeps its own theme
    design = collections.design_for(cfg["theme"], today)
    return Page(root=Path(root), cfg=cfg, mode=mode, subject=subject, here=here, today=today,
                readme=settings.readme_path(cfg, mode), out=settings.out_dir(cfg, mode),
                theme=tone or (prints.STANDARD if design else cfg["theme"]), rainbow=tone, holiday=window,
                design=design)
