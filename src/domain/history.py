# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Which commits a person made, as opposed to the kit or a bot.

A footer carries the day its README last changed, and a person reading it
wants the day someone changed the page, not the day a run redrew its images.
So the kit's own refreshes and anything a bot committed are set aside. The
three kits this one replaced committed under their own scopes, and their
commits are set aside the same way, so a page's history reads right from its
first run.
"""
from __future__ import annotations

import re

REFRESH = re.compile(r"^chore\((markdown|banners|badges|trophies|elements)\):")


def automated(subject: str, committer_name: str = "", committer_email: str = "") -> bool:
    """A commit no person made: a refresh by this kit or one before it, or anything a bot committed."""
    if REFRESH.match(subject or ""):
        return True
    return (committer_name or "").endswith("[bot]") or (committer_email or "").endswith("[bot]@users.noreply.github.com")
