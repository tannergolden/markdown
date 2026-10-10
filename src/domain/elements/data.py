# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The `elements:` section of a page's settings: which elements it draws, and what each is drawn from.

The section maps each element's id to what it is: its `kind`, the fields it
is drawn from, and, when the repository should fill some of them, a
`measure:` request. What the settings write wins over what was measured, so
any element can carry a title, a caption or a description of its own. A page
draws no elements unless its settings name some, because each one goes where
the README's author puts its markers.

An element's files are named for its id: `ID-day.svg` and `ID-dark.svg`, with
`-narrow` or `-still` before the theme for a phone's file and a still one.
"""
from __future__ import annotations

import re
from html import escape

from .. import pixelsets, readme
from ..canvas import BUDGET, lint
from ..holidays.pixel import MISSING
from ..palette import ICONS
from ..prints import STANDARD
from ..standard import elements as SE
from . import draw as E
from .draw import THEMES

# The fields each kind cannot be drawn without, from the settings or from what was measured.
REQUIRED = {
    "schematic": ("boxes", "wires"), "instruments": ("histogram", "dial", "materials", "counters"),
    "milestones": ("events",), "roster": ("people",), "certificate": ("checks", "ring_top", "ring_bottom", "name"),
    "placard": ("owner", "name", "desc", "cells"),
}
# Kinds the elements kit once drew, and the release that retired each, so settings that still name one
# are told what happened rather than that the kind is unknown.
RETIRED = {"plan": "1.3.0", "seal": "1.4.0"}
_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class ElementsError(ValueError):
    pass


def check(section) -> dict:
    """The `elements:` section, its shape checked: a map of each element's id to a map with its kind."""
    if section in (None, True):
        return {}
    if not isinstance(section, dict):
        raise ElementsError("elements: expected false, or a map of each element's id to what it draws")
    for eid, spec in section.items():
        if not isinstance(eid, str) or not _ID.fullmatch(eid):
            raise ElementsError(f"elements: {eid!r}: an element's id is kebab-case, like how-it-fits")
        if not isinstance(spec, dict) or "kind" not in spec:
            raise ElementsError(f"elements: {eid}: expected a map with its kind")
    return {eid: dict(spec) for eid, spec in section.items()}


def merged(section: dict, measured: dict, *, subject: str = "", today: str = "") -> dict:
    """Each element's data: what was measured for it, with what the settings say over it."""
    out = {}
    for eid, spec in section.items():
        d = dict(measured.get(eid, {}))
        d.update({k: v for k, v in spec.items() if k != "measure"})
        d.setdefault("subject", subject)
        if today:
            d.setdefault("today", today)
        out[eid] = d
    return out


def validate(section: dict, measured: dict) -> list[str]:
    """What the section gets wrong, said precisely: an unknown kind, a field an element cannot draw without,
    a wire to a box that is not there, an icon that is not one of the 64."""
    errors = []
    for eid, d in merged(section, measured).items():
        kind = d.get("kind")
        if kind in RETIRED:
            errors.append(f"{eid}: the {kind} element was retired in banners v{RETIRED[kind]}; take it out of the settings")
            continue
        if kind not in E.KINDS:
            errors.append(f"{eid}: unknown kind {kind!r} (one of {', '.join(E.KINDS)})")
            continue
        missing = [f for f in REQUIRED[kind] if f not in d]
        if missing:
            hint = " (a run measures them)" if "measure" in section[eid] else ""
            errors.append(f"{eid}: a {kind} needs {', '.join(missing)}{hint}")
            continue
        if kind == "schematic":
            for w in d["wires"]:
                for k in w[:2]:
                    if k not in d["boxes"]:
                        errors.append(f"{eid}: wire {w[0]} -> {w[1]} names a box that is not there: {k}")
            for k, box in d["boxes"].items():
                if box.get("icon") and box["icon"] not in ICONS:
                    errors.append(f"{eid}: box {k} names an icon that is not in the set: {box['icon']}")
        if kind == "placard" and d.get("icon") and d["icon"] not in ICONS:
            errors.append(f"{eid}: icon {d['icon']!r} is not in the set")
        if kind == "roster" and any(p.get("icon") and p["icon"] not in ICONS for p in d["people"]):
            errors.append(f"{eid}: a person names an icon that is not in the set")
    return errors


def file_name(eid: str, variant: str, theme: str) -> str:
    v = "" if variant in ("wide", "half") else f"-{variant}"
    return f"{eid}{v}-{theme}.svg"


def render(elements: dict, tone: str, holiday: str = "") -> dict[str, str]:
    """{name: svg} for every element, every variant, both themes, in the theme `tone`.

    `standard` is drawn by `standard.elements`, a print by `draw`, from the
    same data into the same files. While `holiday` names a pixel set (a
    holiday's while it is up, or a collection's design for the month; see
    `pixelsets`) it draws them instead, at its own shared half height, and a file it cannot draw within
    the lint is drawn as it always is.
    """
    std = tone == STANDARD
    half = (SE.half_height if std else E.half_height)(elements)
    held = pixelsets.drawn_by(holiday)
    if held:
        halves = [held.element_height(d["kind"], d) for d in elements.values()
                  if E.variants(d["kind"], d) == ("half",)]
        held_half = max(halves) if halves else None
    files = {}
    for eid, d in elements.items():
        kind = d["kind"]
        for variant in E.variants(kind, d):
            for theme in ("day", "dark"):
                svg = None
                if held:
                    MISSING.clear()
                    svg = held.element(kind, E.describe(kind, d), THEMES[theme], variant, held_half)
                    if MISSING or lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=held.tokens):
                        svg = None
                    MISSING.clear()
                files[file_name(eid, variant, theme)] = svg or (
                    SE.draw(kind, d, theme, variant, height=half) if std else
                    E.draw(kind, d, tone, theme, variant, height=half))
    return files


def names(elements: dict) -> list[str]:
    """The files `render` would draw, by name, without drawing them."""
    return [file_name(eid, v, t) for eid, d in elements.items() for v in E.variants(d["kind"], d) for t in ("day", "dark")]


def picture(eid: str, d: dict, rel: str) -> str:
    """The <picture> a README embeds: the phone's file, the still one for no motion, the dark one, then the day one."""
    kind = d["kind"]
    vs = E.variants(kind, d)

    def src(v: str, t: str) -> str:
        return f"{rel}/{file_name(eid, v, t)}"

    lines = ["<picture>"]
    if "narrow" in vs:
        lines.append(f'  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="{src("narrow", "dark")}">')
        lines.append(f'  <source media="(max-width: 585px)" srcset="{src("narrow", "day")}">')
    if "still" in vs:
        lines.append(f'  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{src("still", "dark")}">')
        lines.append(f'  <source media="(prefers-reduced-motion: reduce)" srcset="{src("still", "day")}">')
    main = "half" if "half" in vs else "wide"
    lines.append(f'  <source media="(prefers-color-scheme: dark)" srcset="{src(main, "dark")}">')
    lines.append(f'  <img alt="{escape(E.alt(kind, d))}" src="{src(main, "day")}">')
    lines.append("</picture>")
    pic = "\n".join(lines)
    if d.get("link"):
        pic = f'<a href="{escape(str(d["link"]))}">\n{pic}\n</a>'
    return pic


def block(eid: str, d: dict, rel: str) -> str:
    return readme.block(f"element:{eid}", picture(eid, d, rel))
