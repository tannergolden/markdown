# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""docs/Catalogue.md, written from the catalogue and the calibration so it cannot drift from them."""
from __future__ import annotations

from . import calibration
from .catalogue import MODES, RARITY_NAMES, TIER_NAMES

HEAD = """<!--
title: '🏆 CATALOGUE'
description: 'Every trophy and achievement the kit can award, in both modes, with the threshold and the GitHub data behind each one.'
tags: [trophies, achievements, catalogue, reference]
category: docs
-->

<!-- markdownlint-disable MD041 -->

<div align="center">

# 🏆 CATALOGUE

<a name="top"></a>

**Every trophy and achievement, and what earns it.**

_Written from the data by `make catalogue`. Do not edit by hand._

</div>

---

## 🎯 How Tiers Work

A **core trophy** counts something that only grows. It is cut into five tiers,
Bronze to Diamond, and the card shows progress from the tier you hold to the
next one. Past Diamond it earns a **star** each time the Diamond number
doubles, up to five.

An **achievement** is earned or not. A **tiered** one is earned several times,
at each threshold listed, and the pin shows the numeral you hold. Its
**rarity** decides the metal it is drawn in. **Secret** ones show a question
mark until earned. Anything marked **heavy** reads individual commits rather
than a single count, so it runs under a budget and catches up over a week.

"""

FOOT = """
---

## 🔗 See also

> [!TIP]
> The [README](../README.md) shows a case in use. Every trophy and achievement
> here is read from `src/domain/trophies/catalogue.py` and every number from
> `src/domain/trophies/calibration.py`; edit those and run `make catalogue`,
> never this file.

---

<div align="center">

**Every threshold named. Every share stated.**

[↑ Back to Top](#top)

</div>
"""


def _fmt(n) -> str:
    return f"{n:,}"


def _pct(p: float) -> str:
    if p >= 10:
        return f"{p:.0f}%"
    if p >= 1:
        return f"{p:.1f}".rstrip("0").rstrip(".") + "%"
    return f"{p:.2g}%"


def _core_table(mode: str, cores) -> str:
    rows = ["| Trophy | Counts | Enamel | Bronze | Silver | Gold | Platinum | Diamond | Source |", "| :-- | :-- | :-- | --: | --: | --: | --: | --: | :-- |"]
    for c in cores:
        unit = f" {c.unit}" if c.unit else ""
        rows.append(f'| <a name="{mode}-{c.key}"></a>**{c.title}** | {c.counts} | `{c.tok}` | '
                    + " | ".join(_fmt(s) + unit for s in c.steps) + f" | `{c.src}` |")
    rows += ["", f"Where each tier sits, as the share of {'located accounts' if mode == 'profile' else 'starred public repositories'} at or above it:", "",
             "| Trophy | Bronze | Silver | Gold | Platinum | Diamond | Basis |", "| :-- | --: | --: | --: | --: | --: | :-- |"]
    for c in cores:
        pts, b, note = calibration.CORE_PCT[(mode, c.key)]
        rows.append(f"| **{c.title}** | " + " | ".join("top " + _pct(p) for _, p in pts) + f" | {calibration.BASIS_NAMES[b]}: {note} |")
    return "\n".join(rows)


def _ach_table(mode: str, ach, groups) -> str:
    out = []
    for gi, g in enumerate(groups):
        mine = [a for a in ach if a.g == gi]
        if not mine:
            continue
        out.append(f"### {g}\n")
        out.append("| Achievement | Earned by | Rarity | Who earns it | Source |")
        out.append("| :-- | :-- | :-- | :-- | :-- |")
        for a in mine:
            flags = []
            if a.goals:
                flags.append("tiers " + " / ".join(_fmt(x) for x in a.goals))
            if a.secret:
                flags.append("secret")
            if a.heavy:
                flags.append("heavy")
            if a.only:
                flags.append(f"owner of `{a.only}` only")
            name = f'<a name="{mode}-{a.slug}"></a>**{a.name}**' + (f" <sub>{', '.join(flags)}</sub>" if flags else "")
            rarity = " → ".join(RARITY_NAMES[r] for r in a.rarities)
            share = " → ".join(_pct(x) for x in calibration.shares(mode, a.slug)) + f" <sub>{calibration.BASIS_NAMES[calibration.basis(mode, a.slug)]}</sub>"
            out.append(f"| {name} | {a.how} | {rarity} | {share} | `{a.src}` |")
        out.append("")
    return "\n".join(out)


CALIBRATION = """A tier name and a rarity are claims about how many reach a number. Every
threshold and every rarity in this catalogue is pinned to a share of a
reference population, and each share says how it was got.

**Two reference populations.**

- **Profile mode: located GitHub accounts.** Every account with a location set,
  as collected by [`gayanvoice/top-github-users`](https://github.com/gayanvoice/top-github-users)
  across 138 countries: 122,914 accounts refreshed on 2026-09-24, each with its
  followers and its public and private contributions over the last year. A
  located account is a person who filled in a profile, which is the population
  that puts a trophy case on one. The median has 36 followers and 18 public
  contributions a year; 26% made none.
{REPOSITORY_POPULATION}

**Three kinds of number.** *Measured* is read off a dataset directly (followers,
yearly activity, and every repository-mode core the sample carries). *Derived* is a dataset scaled by a stated factor (all-time
commits as three times one year's contributions; 2.22 repositories per developer
from the Innovation Graph). *Estimated* applies the population's shape to a count
no dataset holds, using the anchors above and the medians
[`github-readme-stats`](https://github.com/anuraghazra/github-readme-stats) uses
for its ranks (250 commits a year, 50 pull requests, 25 issues, 2 reviews, 50
stars, 10 followers).

**Rarity follows the share.** Common is 40% or more of the population, Uncommon
15% to 40%, Rare 4% to 15%, Epic 1% to 4%, Legendary under 1%. The tier ladder
aims at the same cuts for every trophy: Bronze about the top half, Silver the
top quarter to third, Gold the top tenth, Platinum the top 3%, Diamond the top
1%. The **Top N%** chip on a card interpolates between a trophy's anchors, so a
value between two tiers reads a share between their two shares.

The measured column is the honest one; the estimated column is a model, stated
so it can be argued with. When a better dataset turns up, the numbers move and
the words follow, in `src/domain/trophies/calibration.py`.
"""

REPOSITORY_ESTIMATED = """- **Repository mode: public repositories someone else has starred.** About 9% of
  GitHub's 428 million public repositories (the
  [Innovation Graph](https://github.com/github/innovationgraph), 2026 Q1), around
  38 million. Star counts follow a near-Zipf tail, anchored by the published
  tallies of repositories over 100 and over 1,000 stars and by the 2016
  thousand-stars census (7,699 repositories over 1,000 stars, 44% of them over
  2,000, 12% over 5,000, 4% over 10,000). Forks run about one per seven stars.
  The **📐 Calibrate** workflow replaces this model with a measured sample once
  it has run."""

REPOSITORY_MEASURED = """- **Repository mode: public, non-fork repositories with at least one star,**
  measured through GitHub's API on {date} by `markdown-kit calibrate` (the
  **📐 Calibrate** workflow, quarterly). Stars and forks are counted exactly:
  the search API answers how many of the {base:,} such repositories sit at or
  above each threshold. The other cores come from {n} repositories sampled
  across five star bands ({bands}), each measured the way a case measures
  it (contributors, commits, releases, merged pull requests, resolved
  issues) and weighted by its band's share of the population. Active days
  cannot be read from the API and stay estimated."""


def repository_population() -> str:
    """The repository bullet: the measured sample when it exists, the model until then."""
    sample = calibration.REPOSITORY_SAMPLE
    if not sample:
        return REPOSITORY_ESTIMATED
    counts = {b["sampled"] for b in sample["bands"]}
    labels = ", ".join(_band_label(b["band"]) for b in sample["bands"])
    bands = (f"{counts.pop()} in each of {labels} stars" if len(counts) == 1
             else ", ".join(f"{b['sampled']} at {_band_label(b['band'])} stars" for b in sample["bands"]))
    return REPOSITORY_MEASURED.format(date=sample["date"], base=sample["base"] or 0, n=sample["n"], bands=bands)


def _band_label(band: str) -> str:
    lo, hi = band.split("-")
    return f"{int(lo):,}+" if not hi else f"{int(lo):,} to {int(hi):,}"


def page() -> str:
    parts = [HEAD]
    for mode, label, intro in (
        ("profile", "Profile Mode", "The subject is a person. Counts run across every repository the account owns, with the profile repository, bot commits, the kit's own refresh commits, forks and self-stars left out."),
        ("repository", "Repository Mode", "The subject is one repository: the one the stub runs in. Health is binary here, Reach draws on the ledger and the traffic API, and stars exclude the owner and, for an organization, its members."),
    ):
        m = MODES[mode]
        public = [a for a in m["ach"] if not a.only]
        parts.append(f'<a name="{mode}"></a>\n\n## {"👤" if mode == "profile" else "📦"} {label}\n\n{intro}\n')
        parts.append(f"### The {len(m['core'])} core trophies\n")
        parts.append(_core_table(mode, m["core"]) + "\n")
        parts.append(f"### The {len(public)} achievements\n")
        parts.append(_ach_table(mode, m["ach"], m["groups"]))
        parts.append("---\n")
    parts.append("## 📐 How The Numbers Were Set\n")
    parts.append(CALIBRATION.replace("{REPOSITORY_POPULATION}", repository_population()))
    parts.append("## 🏅 Tiers and Rarities\n")
    parts.append("| Tier | " + " | ".join(TIER_NAMES) + " |\n| :-- | " + " | ".join(":--" for _ in TIER_NAMES) + " |\n"
                 "| Metal | ghost | bronze | silver | gold | platinum | diamond |\n")
    parts.append("| Rarity | " + " | ".join(RARITY_NAMES[1:]) + " |\n| :-- | " + " | ".join(":--" for _ in RARITY_NAMES[1:]) + " |\n"
                 "| Metal | bronze | silver | gold | platinum | diamond |")
    parts.append(FOOT)
    return "\n".join(parts)
