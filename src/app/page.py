# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""One run's page: whose it is, which mode, what day, where its files go, and which theme it is drawn in.

Everything a part needs to know that is not its own measurement. It is
settled once per run, from the settings, the repository the run is in, the
clock and the lock, and every part draws from the same one, so a page never
mixes two themes or two days.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from domain import holidays, lock, prints, settings


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
    theme: str              # what the page is drawn in: standard, or a print (rainbowprint resolved to one)
    rainbow: str | None     # the print rainbowprint is on, or None for any other theme
    holiday: holidays.Window | None  # the holiday whose set draws the page today, or None

    @property
    def held(self) -> str:
        """The key of the holiday set the page is drawn in today, or "" for its own theme."""
        return self.holiday.key if self.holiday else ""

    @property
    def drawn_in(self) -> str:
        """What the parts are told to draw in: the set's key and the day its holiday falls on, or ""."""
        return f"{self.holiday.key}:{self.holiday.day.isoformat()}" if self.holiday else ""


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
    """The page, with its theme resolved: a rainbowprint drawn in `rainbow`, or the lock's shade, or the first."""
    tone = rainbow if rainbow else shade(cfg, lk)
    window = holidays.active(today, cfg["holiday_days"], cfg["holidays"])
    if window and not holidays.drawn_by(window.key):
        window = None   # its set is not drawn yet, so the page keeps its own theme
    return Page(root=Path(root), cfg=cfg, mode=mode, subject=subject, here=here, today=today,
                readme=settings.readme_path(cfg, mode), out=settings.out_dir(cfg, mode),
                theme=tone or cfg["theme"], rainbow=tone, holiday=window)
