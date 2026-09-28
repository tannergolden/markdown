# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""From one measurement to every file of the case, the README's block, and what the commit says.

`plan(result, section, ...)` decides every file and its content. Nothing here
talks to GitHub, so a measurement kept in the lock can be drawn again forever,
which is how `check`, `render` and the tests work.
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import replace

from .. import KIT, KIT_VERSION
from ..canvas import BUDGET, hazards
from . import art, styles  # noqa: F401  (styles registers itself)
from .block import block
from .catalogue import MODES, PAL, TIER_NAMES, ach_state, measure

STAMP = f"<!--{KIT} v{KIT_VERSION} trophy "


class TrophiesError(ValueError):
    pass


def lint(svg: str) -> list[str]:
    """Everything wrong with a trophy file as a README image, or an empty list.

    A trophy is held to what every file the kit draws is held to, and to its
    own budget, but not to the banners' palette: its metals and enamels are
    shades of their own.
    """
    problems = hazards(svg)
    if 'role="img"' not in svg:
        problems.append('no role="img"')
    if not re.search(r"<title>[^<]+</title>", svg):
        problems.append("no title")
    if STAMP not in svg:
        problems.append("no stamp")
    size = len(svg.encode("utf-8"))
    if size > BUDGET["trophy"]:
        problems.append(f"{size:,} bytes, over the {BUDGET['trophy']:,} budget")
    return problems


def cores_of(section: dict, mode: str) -> list:
    """The core trophies a case shows, in its order, each in its enamel."""
    cores = list(MODES[mode]["core"])
    if section["core"]:
        order = {k: i for i, k in enumerate(section["core"])}
        cores = sorted([c for c in cores if c.key in order], key=lambda c: order[c.key])
    for i, c in enumerate(cores):
        tok = section["enamel"].get(c.key)
        if tok:
            if tok not in PAL:
                raise TrophiesError(f"trophies: enamel: {tok!r} is not a palette token")
            cores[i] = replace(c, tok=tok)
    return cores


def shown(section: dict, mode: str, subject: str, owners: dict) -> list:
    """The achievements a case shows: the section's choice, and an owner-only one only for its owner."""
    login = subject.split("/")[0]
    out = []
    for a in MODES[mode]["ach"]:
        if a.only and (not owners.get(a.only) or owners[a.only].lower() != login.lower()):
            continue
        out.append(a)
    if section["achievements"] == "none":
        return []
    if section["achievements"] != "all":
        chosen = set(section["achievements"])
        out = [a for a in out if a.slug in chosen]
    return out


def _sort_key(a, st):
    rank = 0 if st["earned"] else 2 if st["secret"] else 1
    return (rank, -st["rarity"] if st["earned"] else -st["pct"], a.name)


def plan(result: dict, section: dict, *, folder: str, base: str) -> dict:
    """Every file of the case by path, the README's block, and the facts a commit names.

    `folder` is where the files go, from the repository's root, and `base`
    the same folder as the README reaches it.
    """
    mode = result["mode"]
    if mode not in MODES:
        raise TrophiesError(f"trophies: a {mode} case is not drawn yet")
    cores = cores_of(section, mode)
    subject = result["subject"]
    ach = shown(section, mode, subject, result.get("owners") or {})
    groups = MODES[mode]["groups"]
    curs = result["curs"]
    values = result["values"]
    delta = result.get("delta", {}) if "weekly" in section["card"] else {}
    new = result.get("new", {}) if "new" in section["card"] else {}
    rank = "rank" in section["card"]
    cases = ["night", "day"] if section["case"] == "both" else [section["case"]]
    draw = art.STYLES[section["style"]]
    files: dict[str, str] = {}
    alts: dict[str, str] = {}

    def put(name: str, render):
        for case in cases:
            svg = render(art.CASES[case])
            rel = f"{folder}/{name}{'-day' if case == 'day' else ''}.svg"
            problems = lint(svg)
            if problems:
                raise TrophiesError(f"trophies: {rel} fails the lint: {'; '.join(problems)}")
            files[rel] = svg.rstrip("\n") + "\n"
            if name not in alts:
                a = svg.split('aria-label="', 1)[1].split('"', 1)[0]
                alts[name] = a.replace("&quot;", '"').replace("&amp;", "&")

    for c in cores:
        o = {"rank": rank, "delta": delta.get(c.key, 0), "new": bool(new.get(c.key))}
        put(c.key, lambda th, c=c, o=o: draw(th, c, values[c.key], o))
    if section["banner"]:
        extra = result.get("extra", {})
        if mode == "profile":
            streak = extra.get("currentStreak", 0) if section["streak"] == "current" else extra.get("streak", 0)
            head = f"{streak}-DAY STREAK" if section["streak"] == "current" else f"LONGEST STREAK {streak} DAYS"
            tail = f"  ·  LONGEST {extra.get('streak', 0)} DAYS" if section["streak"] == "current" else ""
            foot = ("flame", PAL["tangerine"], head, tail)
        else:
            lr = extra.get("lastRelease")
            head = f"RELEASED {lr} DAYS AGO" if lr is not None else "NO RELEASE YET"
            foot = ("tag", PAL["teal"], head, f"  ·  {extra.get('commits30', 0):,} COMMITS THIS MONTH")
        put("level", lambda th: art.level_card(th, cores, values, ach, curs, subject, foot))
        put("next-up", lambda th: art.next_up_card(th, cores, values, ach, curs))
    pins = []
    earned = 0
    for a in ach:
        st = ach_state(a, curs.get(a.slug))
        earned += st["earned"]
        put(f"achievements/{a.slug}", lambda th, a=a: art.pin(th, a, curs.get(a.slug)))
        pins.append((a.g, a.slug, alts[f"achievements/{a.slug}"], st))
    pins.sort(key=lambda p: (p[0], _sort_key(next(x for x in ach if x.slug == p[1]), p[3])))
    nxt = art.next_up_items(cores, values, list(ach), curs, 1)
    unmeasured = [a.name for a in ach if curs.get(a.slug) is None]
    summary = f"{earned} of {len(ach)} earned"
    if nxt:
        summary += f" · next: {nxt[0]['name']}, {int(nxt[0]['pct'] * 100)}%"
    text = (block(base, mode, cores, alts, [(g, b, a) for g, b, a, _ in pins], groups, summary, section["embed"],
                  section["banner"]) if section["block"] else None)
    tiers = {c.key: TIER_NAMES[measure(c, values[c.key])["t"]] for c in cores}
    return {"files": files, "block": text, "summary": summary, "tiers": tiers, "earned": earned, "total": len(ach),
            "unmeasured": unmeasured, "subject": subject, "mode": mode, "cores": cores, "ach": ach}


def describe(planned: dict) -> str:
    """One line for the run's log: the case, its tiers, and how much of it is earned."""
    counted = f"{planned['earned']} of {planned['total']} achievements, " if planned["total"] else ""
    return "trophies " + counted + ", ".join(f"{k} {v}" for k, v in planned["tiers"].items())


def headline(reached: dict, delta: dict, subject: str) -> str:
    """The most notable thing a run did to the case: a tier, else an achievement, else what moved."""
    tiers, ach_new = reached.get("tiers", []), reached.get("achievements", [])
    delta = {k: v for k, v in (delta or {}).items() if v}
    if tiers:
        return "reach " + ", ".join(f"{t} on {name}" for t, name in tiers[:2]) + (" and more" if len(tiers) > 2 else "")
    if ach_new:
        return "earn " + ", ".join(ach_new[:2]) + (f" and {len(ach_new) - 2} more" if len(ach_new) > 2 else "")
    if delta:
        top = sorted(delta.items(), key=lambda kv: -kv[1])[:3]
        return "refresh the case, " + ", ".join(f"{k} +{v:,}" for k, v in top)
    return f"refresh the case for {subject}"


def news(planned: dict, result: dict, reached: dict, run: str | None = None) -> list[str]:
    """The paragraphs a commit carries about the case: where it stands, what was reached, earned and moved.

    `run` is the run's id, given when nothing else in the commit says when the
    case was measured and by which run, so no two refreshes read alike.
    """
    stamp = (f"Measured {planned['subject']} on {result.get('today', '')}" + (f" in run {run}" if run else "") + ". "
             if run is not None else "")
    standing = (f"The case stands at {planned['earned']} of {planned['total']} achievements, with "
                if planned["total"] else "The case stands with ")
    out = [stamp + standing + ", ".join(f"{k} at {v}" for k, v in planned["tiers"].items()) + "."]
    tiers, ach_new = reached.get("tiers", []), reached.get("achievements", [])
    if tiers:
        out.append("Newly reached: " + ", ".join(f"{t} on {name}" for t, name in tiers) + ".")
    if ach_new:
        out.append("Newly earned: " + ", ".join(ach_new) + ".")
    delta = {k: v for k, v in (result.get("delta") or {}).items() if v}
    if delta:
        out.append("Moved this week: " + ", ".join(f"{k} +{v:,}" for k, v in sorted(delta.items())) + ".")
    return [textwrap.fill(p, 72) for p in out]
