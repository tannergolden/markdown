# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Example measurements, for previews and the tests.

The numbers are made up. They are chosen so every state is exercised: a
Platinum trophy with a NEW ribbon, tiered achievements at each stage, a
secret earned and secrets hidden, and one unmeasured value.
"""
from __future__ import annotations

from .catalogue import ACH, RACH

PROFILE = {
    "mode": "profile", "subject": "octo-dev",
    "values": {"commits": 5730, "pulls": 186, "reviews": 64, "issues": 18, "stars": 312, "followers": 88, "streak": 43, "repos": 34},
    "extra": {"currentStreak": 12, "streak": 43, "years": 7},
    "notes": [], "api": {"calls": 0, "points": 0},
}
_PROFILE_CURS = {
    "hello-world": 5730, "first-light": 34, "opening-move": 186, "landed": 64, "ticket": 18, "second-opinion": 64, "shipped": 14,
    "shipwright": 14, "merge-master": 64, "polyglot": 12, "veteran": 7, "century": 340, "monolith": 340, "long-haul": 0,
    "stargazer": 62, "forked": 12, "watched": 21, "bug-hunter": 11, "closer": 47, "fan-club": 64, "branching-out": 10,
    "by-the-book": 1450, "gitmoji": 620, "signed": 2100, "duet": 3, "undo": 2, "surgeon": 210, "fixer": 88, "tested": 9, "scribe": 31,
    "green-machine": 3200, "well-maintained": 41, "toolsmith": 2, "heavy-lifter": 1, "sweeping-change": 0,
    "perfect-month": 1, "weekender": 31, "night-owl": 44, "early-bird": 6, "marathon-day": 38, "big-week": 130, "sprint": 320,
    "weekday-warrior": 141, "year-of-code": 123, "four-seasons": 1, "long-game": 7, "comeback": 1, "friday-deploy": 0, "lunch-break": 27,
    "upstream": 7, "open-door": 12, "second-pair-of-eyes": 22, "reporter": 9, "voice": 58, "answer-key": 3, "conversation-starter": 4,
    "team-player": 3, "founder": 1, "crew": 2, "generous": 214, "curious": 61, "patron": 0, "backed": 0, "gist-keeper": 14, "planner": 3,
    "registry": 1, "introduced": 1, "green-light": 38, "red-pen": 6, "roundtable": 12,
    "licensed": 31, "documented": 34, "curator": 20, "front-door": 6, "welcome-mat": 1, "house-rules": 1, "locksmith": 1, "gatekeeper": 3,
    "auto-pilot": 1, "blueprint": 1, "open-hand": 0, "town-hall": 1, "tidy": 2, "packager": 1, "semver": 14, "form-filler": 1,
    "roadmap": 2, "label-maker": 31,
    "new-year": 1, "leap-day": 0, "green-wall": 0, "homecoming": 0, "friday-the-13th": 0, "midnight-oil": 0, "the-answer": 0,
    "full-house": 0, "constellation": 0, "round-number": 0, "ghost": 0, "inbox-zero": 0,
    "trophy-maker": 1, "badge-maker": 1, "standard-bearer": 1, "pathfinder": 1,
}
PROFILE["curs"] = {a.slug: _PROFILE_CURS.get(a.slug, 0) for a in ACH}
PROFILE["delta"] = {"commits": 124, "pulls": 3, "reviews": 5, "stars": 9, "followers": 2, "repos": 1}
PROFILE["new"] = {"pulls": True}

REPOSITORY = {
    "mode": "repository", "subject": "octo-dev/toolkit",
    "values": {"stars": 1240, "forks": 86, "contributors": 23, "commits": 3410, "releases": 41, "merged": 612, "resolved": 388, "active": 720},
    "extra": {"lastRelease": 12, "commits30": 43},
    "notes": [], "api": {"calls": 0, "points": 0},
}
_REPO_CURS = {
    "first-star": 1240, "first-fork": 86, "first-watcher": 40, "first-release": 41, "first-merge": 612, "outside-help": 1, "stranger-report": 1,
    "first-tag": 1, "named": 1, "front-door": 1, "filed": 6, "poster": 0,
    "licensed": 1, "documented": 1, "welcome-mat": 1, "house-rules": 1, "locksmith": 1, "gatekeeper": 1, "form-filler": 1, "paperwork": 0,
    "auto-pilot": 1, "changelog": 1, "well-formed": 1, "town-hall": 1, "protected": 1, "clean-bill": 1, "open-hand": 0, "support-line": 0,
    "label-maker": 31, "roadmap": 7,
    "by-the-book": 2900, "signed": 1400, "gitmoji": 220, "semver": 41, "green-machine": 4100, "test-suite": 1, "wired": 1, "release-notes": 41,
    "packager": 1, "prerelease": 0, "squeaky": 1, "small-steps": 1, "follows-the-standards": 1, "golden-path": 1, "containerized": 0, "ready-room": 1,
    "ten-strong": 23, "reviewed": 0, "fast-reply": 1, "good-first-issues": 8, "help-wanted": 3, "outside-merges": 64, "answered": 4, "triage": 1,
    "well-maintained": 61, "talkative": 530, "popular-opinion": 18, "long-thread": 34, "mentor": 1, "regulars": 4, "org-backed": 0, "crew": 3,
    "watched": 40, "used-by": None, "star-of-the-week": 22, "trending": 22, "forked-far": 12, "living-forks": 7, "registry": 1, "downloaded": 14800,
    "visited": 640, "cloned": 110, "referred": 6, "big-name": 0, "stargazer-streak": 9, "fork-magnet": 2,
    "weekly-beat": 52, "monthly-release": 9, "streak": 61, "comeback": 0, "night-shift": 44, "weekend-project": 30, "marathon-day": 38,
    "big-week": 130, "long-game": 4, "alive": 1, "friday-deploy": 1, "same-day-fix": 6,
    "round-number": 0, "the-answer": 0, "palindrome": 0, "leap-day": 0, "friday-the-13th": 0, "new-year": 1, "birthday": 0, "midnight-oil": 0,
    "green-wall": 0, "ghost": 0, "full-house": 0, "constellation": 0,
}
REPOSITORY["curs"] = {a.slug: _REPO_CURS.get(a.slug, 0) for a in RACH}
REPOSITORY["delta"] = {"stars": 22, "forks": 2, "commits": 43, "merged": 9, "resolved": 6, "active": 14}
REPOSITORY["new"] = {"stars": True}

SAMPLES = {"profile": PROFILE, "repository": REPOSITORY}
