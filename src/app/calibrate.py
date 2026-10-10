# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Measure the repository population the repository-mode tiers are set against: `markdown-kit calibrate`.

The catalogue says a Bronze in stars is the top 10% of starred public
repositories, and until this runs that figure is a model. This asks GitHub:
it counts the population directly where the search API can count it (stars,
forks: `stars:>=N` answers with a total), and where it cannot (contributors,
commits, releases, merged pull requests, resolved issues) it samples
repositories from each star band, measures each one the way a case measures
it, and weights the bands by their population.

Stratified by star band on purpose. A uniform sample of starred repositories
is almost entirely one-star repositories, so it could never see the tail
where Diamond lives; forty repositories from the 10,000-star band, weighted
by how few such repositories there are, can.

The client is handed in (`infra.github.Paced`), which sleeps through the
rate limits rather than failing on them. The result is one JSON file, which
`infra.resources` hands to `domain.trophies.calibration` on every run, so
the words on the cards follow the numbers without anyone editing code.
"""
from __future__ import annotations

import datetime as dt
import random

from domain.trophies.catalogue import RCORE

BANDS = ((1, 9), (10, 99), (100, 999), (1000, 9999), (10000, None))
MEASURED = ("stars", "forks", "contributors", "commits", "releases", "merged", "resolved")


def band_query(lo: int, hi: int | None) -> str:
    return f"stars:>={lo}" if hi is None else f"stars:{lo}..{hi}"


def population(client, thresholds: dict) -> dict:
    """Population counts the search API can answer directly."""
    out = {"base": client.count("repositories", "stars:>=1 fork:false"), "bands": {}, "stars": {}, "forks": {}}
    for lo, hi in BANDS:
        out["bands"][f"{lo}-{hi or ''}"] = client.count("repositories", band_query(lo, hi) + " fork:false")
    for n in thresholds["stars"]:
        out["stars"][str(n)] = client.count("repositories", f"stars:>={n} fork:false")
    for n in thresholds["forks"]:
        out["forks"][str(n)] = client.count("repositories", f"forks:>={n} stars:>=1 fork:false")
    return out


def sample_band(client, lo: int, hi: int | None, n: int, rng: random.Random, today: dt.date) -> list:
    """Up to `n` repository names from one star band, spread over creation months."""
    names: list = []
    seen: set = set()
    months = [(y, m) for y in range(2009, today.year + 1) for m in range(1, 13) if (y, m) <= (today.year, today.month)]
    rng.shuffle(months)
    for y, m in months:
        if len(names) >= n:
            break
        end = (dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1)).isoformat()
        q = f"{band_query(lo, hi)} fork:false created:{y}-{m:02d}-01..{end}"
        data, _ = client.get("/search/repositories", {"q": q, "per_page": 30, "page": rng.randint(1, 3)})
        items = [r["full_name"] for r in (data or {}).get("items", []) if not r.get("archived")]
        rng.shuffle(items)
        for full in items[:8]:
            if full not in seen:
                seen.add(full)
                names.append(full)
    return names[:n]


def measure_repository(client, full: str) -> dict | None:
    """The repository the way a case counts it: the seven measurable cores."""
    r, _ = client.get(f"/repos/{full}")
    if not r or r.get("fork"):
        return None
    return {
        "full_name": full,
        "stars": r.get("stargazers_count", 0),
        "forks": r.get("forks_count", 0),
        "contributors": client.last_page(f"/repos/{full}/contributors", {"anon": "true"}),
        "commits": client.last_page(f"/repos/{full}/commits", {}),
        "releases": client.last_page(f"/repos/{full}/releases", {}),
        "merged": client.count("issues", f"repo:{full} is:pr is:merged"),
        "resolved": client.count("issues", f"repo:{full} is:issue is:closed reason:completed"),
    }


def estimate(bands: list, thresholds: dict) -> dict:
    """Stratified shares: Σ over bands of weight × the band's fraction at or above each threshold.

    `bands` is a list of {"weight": share of the population, "repos": [measured dicts]}.
    A band with no measured repositories contributes nothing and is reported."""
    out = {}
    total_weight = sum(b["weight"] for b in bands if b["repos"])
    for key, steps in thresholds.items():
        anchors = []
        for t in steps:
            share = 0.0
            for b in bands:
                if not b["repos"]:
                    continue
                vals = [x[key] for x in b["repos"] if x.get(key) is not None]
                if not vals:
                    continue
                frac = sum(1 for v in vals if v >= t) / len(vals)
                share += (b["weight"] / total_weight) * frac
            anchors.append([t, round(100 * share, 4)])
        # a share can never rise with the threshold; smooth any sampling noise downward
        for i in range(1, len(anchors)):
            anchors[i][1] = min(anchors[i][1], anchors[i - 1][1])
        out[key] = anchors
    return out


def exact_shares(pop: dict, key: str, steps: tuple) -> list:
    base = pop["base"] or 1
    anchors = [[t, round(100 * (pop[key].get(str(t)) or 0) / base, 4)] for t in steps]
    for i in range(1, len(anchors)):
        anchors[i][1] = min(anchors[i][1], anchors[i - 1][1])
    return anchors


def run(client, per_band: int, seed: int, today: dt.date, log=print) -> dict:
    thresholds = {c.key: tuple(c.steps) for c in RCORE if c.key in MEASURED}
    log("counting the population")
    pop = population(client, thresholds)
    base = pop["base"] or 1
    rng = random.Random(seed)
    bands = []
    for lo, hi in BANDS:
        label = f"{lo}-{hi or ''}"
        weight = (pop["bands"][label] or 0) / base
        log(f"sampling band {label}: weight {weight:.5f}")
        repos = []
        for full in sample_band(client, lo, hi, per_band, rng, today):
            m = measure_repository(client, full)
            if m:
                repos.append(m)
        log(f"  measured {len(repos)} repositories")
        bands.append({"band": label, "weight": weight, "population": pop["bands"][label], "sampled": len(repos), "repos": repos})
    sampled = {k: v for k, v in thresholds.items() if k not in ("stars", "forks")}
    cores = {k: {"anchors": a} for k, a in estimate(bands, sampled).items()}
    cores["stars"] = {"anchors": exact_shares(pop, "stars", thresholds["stars"])}
    cores["forks"] = {"anchors": exact_shares(pop, "forks", thresholds["forks"])}
    return {
        "date": today.isoformat(),
        "population": "public, non-fork repositories with at least one star",
        "base": pop["base"],
        "n": sum(b["sampled"] for b in bands),
        "bands": [{k: b[k] for k in ("band", "weight", "population", "sampled")} for b in bands],
        "cores": cores,
        "calls": client.calls,
    }
