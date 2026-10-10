# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Where every threshold sits against real GitHub data.

The kit says "Silver" and "top 17%" and "Rare". Those words are promises
about how many people or projects reach a number, and this module is where
the promises are pinned to measurements rather than to taste.

TWO REFERENCE POPULATIONS

  profile     Located GitHub accounts: every account with a location set,
              as collected by gayanvoice/top-github-users across 138
              countries. 122,914 accounts, refreshed 2026-09-24, with each
              account's followers and its public and private contributions
              over the last year. A located account is a person who filled
              in a profile, which is the population that puts a trophy case
              on one. The median has 36 followers and 18 public
              contributions a year; 26% made none.

  repository  Public, non-fork repositories with at least one star,
              measured through GitHub's API by `markdown-kit calibrate`
              into data/calibration/repositories.json, which
              `infra.resources` hands in through `use`. Stars
              and forks are counted exactly by the search API; the other
              cores come from a sample stratified by star band and
              weighted by each band's population. The estimates written
              below are what the table holds until that file exists, and
              for active days, which the API cannot count: about 38
              million starred repositories, a near-Zipf star tail anchored
              by the published tallies over 100 and over 1,000 stars and
              the 2016 thousand-stars census, and one fork per seven stars.

WHAT EACH NUMBER IS

  Every core tier carries the share of its population at or above the
  threshold, and every achievement carries the share expected to earn it.
  Each figure has a basis:

    m  measured   read off the dataset directly (followers, yearly activity)
    d  derived    the dataset scaled by a stated factor (all-time commits
                  from yearly contributions; GitHub's own totals per
                  developer from the Innovation Graph)
    e  estimated  the population's shape applied to a count the dataset
                  does not hold, with the anchors named above and the
                  medians github-readme-stats uses for its ranks (commits
                  250 a year, pull requests 50, issues 25, reviews 2, stars
                  50, followers 10, all-time)

  Rarity follows the share, never the other way round:

    Common     40% or more      Uncommon   15% to 40%
    Rare        4% to 15%       Epic        1% to 4%
    Legendary   under 1%

  The tier ladder aims at the same cuts everywhere: Bronze about the top
  half, Silver the top quarter to third, Gold the top tenth, Platinum the
  top 3%, Diamond the top 1%. Stars past Diamond keep doubling the number.

The "top N%" chip interpolates between a trophy's anchors on log-log axes
and extends the last slope beyond Diamond, so a value between two tiers
reads a share between their two shares rather than a number invented for
the gap.
"""
from __future__ import annotations

import math

DATASETS = {
    "located-accounts": "gayanvoice/top-github-users cache, 138 countries, 122,914 accounts, 2026-09-24",
    "innovation-graph": "github/innovationgraph, 2026 Q1: 427,792,765 repositories, 192,326,991 developers, 2.22 repositories and 1.66 pushes a quarter per developer",
    "star-tallies": "anthonygarvan/thousandstars (2016 census) and the published counts of repositories over 100 and 1,000 stars; EvanLi/Github-Ranking 2026-09-24 for the top of the tail",
    "readme-stats": "anuraghazra/github-readme-stats rank medians, the widest-used profile card",
}

BANDS = ((40, 1), (15, 2), (4, 3), (1, 4), (0, 5))  # share at or above -> rarity


def rarity_of(share: float) -> int:
    for floor, r in BANDS:
        if share >= floor:
            return r
    return 5


# -- core trophies: (threshold, top-percent) per tier, and the basis ------------------------
CORE_PCT = {
    ("profile", "commits"): (((100, 43.0), (500, 21.8), (2000, 7.8), (5000, 2.8), (10000, 1.1)), "d",
                             "all-time commits taken as three times one year's public contributions; yearly shares measured"),
    ("profile", "pulls"): (((5, 45.0), (25, 25.0), (100, 9.0), (250, 4.0), (1000, 1.0)), "e", "readme-stats median 50, Zipf tail"),
    ("profile", "reviews"): (((5, 30.0), (25, 14.0), (100, 5.0), (250, 2.2), (1000, 0.6)), "e", "readme-stats median 2, Zipf tail"),
    ("profile", "issues"): (((5, 45.0), (25, 22.0), (100, 8.0), (250, 3.5), (1000, 1.0)), "e", "readme-stats median 25, Zipf tail"),
    ("profile", "stars"): (((10, 30.0), (50, 15.0), (250, 5.0), (1000, 1.6), (5000, 0.4)), "e", "readme-stats median 50 for card users, discounted for located accounts"),
    ("profile", "followers"): (((25, 57.96), (100, 29.03), (350, 10.5), (1000, 3.35), (2500, 1.01)), "m", "located accounts"),
    ("profile", "streak"): (((7, 50.0), (30, 18.0), (100, 5.0), (200, 1.8), (365, 0.5)), "e", "yearly activity shares; a 365-day streak needs 365 active days"),
    ("profile", "repos"): (((5, 50.0), (15, 22.0), (30, 9.0), (60, 3.0), (100, 1.2)), "d", "2.22 repositories per developer on average, Zipf tail"),
    ("repository", "stars"): (((10, 10.0), (100, 1.0), (500, 0.2), (2000, 0.05), (10000, 0.01)), "e", "star tallies, Zipf tail from 1 star"),
    ("repository", "forks"): (((5, 8.0), (25, 1.5), (100, 0.35), (500, 0.07), (2000, 0.015)), "e", "one fork per seven stars"),
    ("repository", "contributors"): (((2, 25.0), (5, 8.0), (15, 2.5), (50, 0.6), (200, 0.12)), "e", "most starred repositories have one author"),
    ("repository", "commits"): (((100, 15.0), (500, 4.0), (2000, 1.0), (5000, 0.4), (20000, 0.08)), "e", "popular-project quartiles 102 / 393 / 1,230 commits, general median near 10"),
    ("repository", "releases"): (((1, 12.0), (5, 4.0), (20, 1.0), (50, 0.35), (200, 0.06)), "e", "most repositories never publish a release"),
    ("repository", "merged"): (((10, 10.0), (50, 3.0), (250, 0.6), (1000, 0.15), (5000, 0.03)), "e", "43 million merges a month across 630 million repositories"),
    ("repository", "resolved"): (((10, 8.0), (50, 2.5), (250, 0.5), (1000, 0.12), (5000, 0.025)), "e", "issues close less often than pull requests merge"),
    ("repository", "active"): (((30, 15.0), (100, 5.0), (365, 1.0), (1000, 0.2), (2500, 0.04)), "e", "1.66 pushes a quarter per developer on average"),
}

# -- achievements: share of the population expected to earn each tier, and the basis ---------
SHARE = {
    "profile": {
        "hello-world": (74, "m"), "first-light": (60, "e"), "opening-move": (45, "e"), "landed": (38, "e"), "ticket": (45, "e"),
        "second-opinion": (25, "e"), "shipped": (20, "e"), "shipwright": ((8, 2, 0.5), "e"), "merge-master": ((20, 8, 1.5), "e"),
        "polyglot": ((35, 15, 4), "e"), "veteran": ((80, 45, 8), "d"), "century": (35, "d"), "monolith": (7, "d"), "long-haul": (10, "e"),
        "stargazer": ((30, 8, 1.2), "e"), "forked": ((15, 7, 1.5), "e"), "watched": (3, "e"), "bug-hunter": (8, "e"), "closer": (6, "e"),
        "fan-club": (5, "e"), "branching-out": (12, "e"),
        "by-the-book": ((8, 3, 0.8), "e"), "gitmoji": ((4, 1), "e"), "signed": ((10, 2), "e"), "duet": (12, "e"), "undo": (25, "e"),
        "surgeon": (20, "e"), "fixer": (15, "e"), "tested": (6, "e"), "scribe": (8, "e"), "green-machine": ((12, 4, 0.7), "e"),
        "well-maintained": (6, "e"), "toolsmith": (4, "e"), "heavy-lifter": (40, "e"), "sweeping-change": (30, "e"),
        "perfect-month": (6, "d"), "weekender": (12, "d"), "night-owl": ((15, 2), "e"), "early-bird": ((10, 1.5), "e"),
        "marathon-day": ((20, 7, 2), "d"), "big-week": (20, "d"), "sprint": (6, "d"), "weekday-warrior": (4, "d"), "year-of-code": (0.6, "d"),
        "four-seasons": (15, "d"), "long-game": ((40, 20, 5), "d"), "comeback": (45, "e"), "friday-deploy": (12, "e"), "lunch-break": (20, "e"),
        "upstream": ((35, 10, 2.5), "e"), "open-door": ((25, 8, 2), "e"), "second-pair-of-eyes": (6, "e"), "reporter": (12, "e"), "voice": (8, "e"),
        "answer-key": (1.5, "e"), "conversation-starter": (3, "e"), "team-player": (10, "e"), "founder": (12, "e"), "crew": (15, "e"),
        "generous": (25, "e"), "curious": (20, "e"), "patron": (1.5, "e"), "backed": (0.6, "e"), "gist-keeper": (8, "e"), "planner": (6, "e"),
        "registry": (4, "e"), "introduced": (30, "e"), "green-light": (8, "e"), "red-pen": (4, "e"), "roundtable": (2, "e"),
        "licensed": ((45, 20, 4), "e"), "documented": ((55, 25, 5), "e"), "curator": ((20, 8, 1.5), "e"), "front-door": (12, "e"),
        "welcome-mat": (8, "e"), "house-rules": (5, "e"), "locksmith": (3, "e"), "gatekeeper": (2, "e"), "auto-pilot": (10, "e"),
        "blueprint": (8, "e"), "open-hand": (4, "e"), "town-hall": (6, "e"), "tidy": (12, "e"), "packager": (12, "e"), "semver": (12, "e"),
        "form-filler": (8, "e"), "roadmap": (4, "e"), "label-maker": (6, "e"),
        "new-year": (15, "d"), "leap-day": (5, "d"), "green-wall": (2, "d"), "homecoming": (10, "d"), "friday-the-13th": (12, "d"),
        "midnight-oil": (3, "e"), "the-answer": (4, "e"), "full-house": (0.5, "e"), "constellation": (0.1, "e"), "inbox-zero": (5, "e"),
        "ghost": (20, "e"), "round-number": (3, "e"),
        "trophy-maker": (0.001, "m"), "badge-maker": (0.001, "m"), "standard-bearer": (0.001, "m"), "pathfinder": (0.001, "m"),
    },
    "repository": {
        "first-star": (100, "m"), "first-fork": (40, "e"), "first-watcher": (60, "e"), "first-release": (12, "e"), "first-merge": (30, "e"),
        "outside-help": (8, "e"), "stranger-report": (15, "e"), "first-tag": (20, "e"), "named": (70, "e"), "front-door": (20, "e"),
        "filed": (15, "e"), "poster": (3, "e"),
        "licensed": (55, "e"), "documented": (75, "e"), "welcome-mat": (6, "e"), "house-rules": (4, "e"), "locksmith": (1.5, "e"),
        "gatekeeper": (2, "e"), "form-filler": (4, "e"), "paperwork": (3, "e"), "auto-pilot": (6, "e"), "changelog": (10, "e"),
        "well-formed": (15, "e"), "town-hall": (3, "e"), "protected": (8, "e"), "clean-bill": (40, "e"), "open-hand": (3, "e"),
        "support-line": (1.5, "e"), "label-maker": (5, "e"), "roadmap": (3, "e"),
        "by-the-book": ((5, 1.5, 0.3), "e"), "signed": ((6, 1), "e"), "gitmoji": ((3, 0.8), "e"), "semver": (6, "e"),
        "green-machine": ((8, 2.5, 0.4), "e"), "test-suite": (35, "e"), "wired": (30, "e"), "release-notes": (5, "e"), "packager": (8, "e"),
        "prerelease": (5, "e"), "squeaky": (45, "e"), "small-steps": (30, "e"), "follows-the-standards": (0.01, "m"), "golden-path": (0.01, "m"),
        "containerized": (15, "e"), "ready-room": (3, "e"),
        "ten-strong": ((4, 0.6, 0.25), "e"), "reviewed": (3, "e"), "fast-reply": (6, "e"), "good-first-issues": (3, "e"), "help-wanted": (3, "e"),
        "outside-merges": ((4, 1, 0.2), "e"), "answered": (1, "e"), "triage": (5, "e"), "well-maintained": (5, "e"), "talkative": (1, "e"),
        "popular-opinion": (1.5, "e"), "long-thread": (1.5, "e"), "mentor": (6, "e"), "regulars": (1.5, "e"), "org-backed": (15, "e"), "crew": (8, "e"),
        "watched": ((1.5, 0.4, 0.03), "e"), "used-by": ((4, 0.8, 0.1), "e"), "star-of-the-week": (1.5, "e"), "trending": (0.6, "e"),
        "forked-far": (0.5, "e"), "living-forks": (3, "e"), "registry": (5, "e"), "downloaded": ((4, 1.2, 0.25), "e"), "visited": (3, "e"),
        "cloned": (5, "e"), "referred": (4, "e"), "big-name": (3, "e"), "stargazer-streak": (1.5, "e"), "fork-magnet": (1.5, "e"),
        "weekly-beat": (2, "e"), "monthly-release": (0.8, "e"), "streak": ((3, 0.5, 0.05), "e"), "comeback": (40, "e"), "night-shift": (8, "e"),
        "weekend-project": (8, "e"), "marathon-day": (10, "e"), "big-week": (6, "e"), "long-game": ((25, 10, 1.5), "e"), "alive": (20, "e"),
        "friday-deploy": (8, "e"), "same-day-fix": (6, "e"),
        "round-number": (2, "e"), "the-answer": (3, "e"), "palindrome": (8, "e"), "leap-day": (0.3, "e"), "friday-the-13th": (1.5, "e"),
        "new-year": (5, "e"), "birthday": (6, "e"), "midnight-oil": (2, "e"), "green-wall": (1.5, "e"), "ghost": (15, "e"),
        "full-house": (0.3, "e"), "constellation": (0.05, "e"),
    },
}

BASIS_NAMES = {"m": "measured", "d": "derived", "e": "estimated"}


def apply_repository_sample(data: dict | None, table: dict) -> dict:
    """Replace the repository-mode estimates in `table` with what the sample measured.

    The sample carries, per core key, the share at or above each of that
    trophy's steps. A key it does not carry (active days cannot be counted
    from the API) keeps its estimate, and so does a key whose steps no
    longer match the catalogue's: the sample predates a threshold change,
    and the estimate stands until the next run."""
    if not data:
        return table
    for key, spec in data.get("cores", {}).items():
        current = table.get(("repository", key))
        if not current:
            continue
        steps = tuple(t for t, _ in current[0])
        anchors = tuple((int(t), float(p)) for t, p in spec["anchors"])
        if tuple(t for t, _ in anchors) != steps:
            continue
        note = (f"{data['n']} repositories in {len(data['bands'])} star bands, weighted by band, {data['date']}"
                if key not in ("stars", "forks") else f"every starred public repository counted by the search API, {data['date']}")
        table[("repository", key)] = (anchors, "m", note)
    return table


ESTIMATED = dict(CORE_PCT)  # the table as written above, before the sample is applied
REPOSITORY_SAMPLE: dict | None = None


def use(sample: dict | None) -> None:
    """Make `sample` the measured repository population, replacing any a previous call made.

    The table is changed in place, so every reader sees the one table. None
    leaves the estimates as written.
    """
    global REPOSITORY_SAMPLE
    CORE_PCT.clear()
    CORE_PCT.update(ESTIMATED)
    REPOSITORY_SAMPLE = sample
    apply_repository_sample(sample, CORE_PCT)


def shares(mode: str, slug: str) -> tuple:
    """The per-tier shares of an achievement, always as a tuple."""
    s, _ = SHARE[mode][slug]
    return tuple(s) if isinstance(s, (list, tuple)) else (s,)


def basis(mode: str, slug: str) -> str:
    return SHARE[mode][slug][1]


def anchors(mode: str, key: str) -> tuple:
    return CORE_PCT[(mode, key)][0]


def top_pct(mode: str, key: str, v: float) -> float:
    """Share of the reference population at or above `v`, in percent.

    Log-log interpolation between (0, 100%) and the tier anchors; past the
    last anchor the last segment's slope continues, floored at 0.001%."""
    pts = [(0, 100.0)] + list(anchors(mode, key))
    lg = lambda x: math.log(x + 1)  # noqa: E731
    if v <= 0:
        return 100.0
    for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
        if v < x1:
            f = (lg(v) - lg(x0)) / (lg(x1) - lg(x0))
            return min(100.0, math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * f))
    (x0, p0), (x1, p1) = pts[-2], pts[-1]
    slope = (math.log(p1) - math.log(p0)) / (lg(x1) - lg(x0))
    return max(0.001, math.exp(math.log(p1) + slope * (lg(v) - lg(x1))))
