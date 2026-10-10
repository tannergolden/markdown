#!/usr/bin/env python3
"""Draw every theme the kit draws a page in, and the page that shows them.

WHY THIS EXISTS. A theme is easier to choose by looking than by reading. The
page shows every theme's headers, phone files, footers, elements and badges,
each drawn the way a run draws it, from the kit's own samples and the
driftmark specimen, on GitHub's light and dark grounds.

Nothing is fetched and nothing depends on the day it runs, so drawing it twice
writes the same bytes, and a change to a theme shows up as a change here.

  make themes                     the page and one SVG per drawing, in docs/themes
  build-theme-sets.py --bundle D  the page and one data file per theme, in D, for
                                  a host that caps how many files a page may have
  ... --only standard,halloween   just these themes

A collection is one entry here, its year of twelve headers, and its own page
beside this one shows every design in full (see build-collection.py). Only a
collection with all twelve designs drawn is shown. Both show the year, so each
design is drawn as its month's design, with the month's mark in its headers.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from domain import KIT, KIT_VERSION, collections, holidays, prints  # noqa: E402
from domain.badges import data as badges_data  # noqa: E402
from domain.banners import sample  # noqa: E402
from domain.banners.compose import compose  # noqa: E402
from domain.banners.designs import DESIGNS, render, slug  # noqa: E402
from domain.banners.settings import check as banners_check  # noqa: E402
from domain.canvas import BUDGET  # noqa: E402
from domain.collections.hand import signs  # noqa: E402
from domain.elements import data as elements_data, draw as elements_draw  # noqa: E402
from domain.palette import hexof  # noqa: E402
from domain.standard import pieces  # noqa: E402
from infra import resources  # noqa: E402
from infra.yaml_reader import loads  # noqa: E402

TEMPLATE = Path(__file__).with_name("theme-sets.html")
SPECIMEN = ROOT / "tests" / "fixtures" / "driftmark" / ".github" / "markdown.yaml"
# The page says it drew this folder, so a rebuild may empty it and a wrong path never loses anything.
MARK = '<meta name="generator" content="markdown-kit theme-sets">'

# The specimen's elements, measured on a fixed day, and the six the page shows.
TODAY = "2026-09-25"
SHOWN = ("how-it-runs", "vitals", "history", "contributors", "conformance", "action")
STYLES = ("for-the-badge", "flat", "flat-square", "plastic", "pill", "compact")
STATES = (("green", "Passing"), ("yellow", "Degraded"), ("red", "Failing"), ("slate", "No Data"))
SEED = "2026W40"
# GitHub's two grounds, which every day and dark file is shown on.
GROUNDS = {"day": "#ffffff", "dark": "#0d1117"}

HEADERS = (("H1", "h1", "H1 Sheet", False), ("H2", "h2", "H2 Section", False), ("H3", "h3", "H3 Strip", False),
           ("H2", "h2-profile", "H2 Section, on a profile", True))
FOOTERS = (("F1", "f1", "F1 Title block"), ("F2", "f2", "F2 Scale bar"))
NOTES = {
    "headers": "Wide, as a README shows them on a desktop. Each one moves; a reader who asks for reduced motion "
               "gets its still pair, which Motion: Still shows here.",
    "phones": "The 360-pixel files a README shows on a small screen. They hold still.",
    "footers": "A footer holds still. The buttons under it carry its links.",
    "elements": "The driftmark specimen, drawn from the same data in every theme.",
    "spectrum": "Red to pink, then round again: the H2 Section in each of the nine prints it moves through.",
    "year": "January to December: the H2 Section in each month's design, which is up from the first of its month "
            "to the last.",
}


class Drawings:
    """Every drawing the page shows, by the path the page finds it at."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def add(self, path: str, svg: str) -> str:
        svg = svg if svg.endswith("\n") else svg + "\n"
        if self.files.setdefault(path, svg) != svg:
            raise ValueError(f"two different drawings for {path}")
        return path


def dims(svg: str) -> tuple[int, int]:
    tag = re.search(r"<svg\b[^>]*>", svg)
    w, h = (re.search(rf'\s{name}="([\d.]+)"', tag[0]) if tag else None for name in ("width", "height"))
    if not (w and h):
        raise ValueError("a drawing without its size")
    return round(float(w[1])), round(float(h[1]))


def weight(*svgs: str) -> int:
    return max(len(s.encode("utf-8")) for s in svgs)


def item(d: Drawings, key: str, name: str, label: str, day: str, dark: str, cap: int, still=None) -> dict:
    """One drawing's day and dark files; a moving one also keeps the still pair a README shows for reduced motion."""
    w, h = dims(day)
    out = {"label": label, "w": w, "h": h, "cap": cap, "size": weight(day, dark),
           "day": d.add(f"{key}/{name}-day.svg", day), "dark": d.add(f"{key}/{name}-dark.svg", dark)}
    if still:
        out["sday"] = d.add(f"{key}/{name}-still-day.svg", still[0])
        out["sdark"] = d.add(f"{key}/{name}-still-dark.svg", still[1])
    return out


@lru_cache(maxsize=None)
def contents(theme: str, holiday: str = ""):
    extra = {"theme": theme, "holiday": holiday}
    header, footer, _ = compose(sample.SAMPLES["repository"], banners_check({}) | extra)
    profile, _, _ = compose(sample.SAMPLES["profile"], banners_check({}) | extra)
    return header, footer, profile


@lru_cache(maxsize=None)
def drawn(code: str, theme: str, holiday: str = "", profile: bool = False) -> dict:
    header, footer, on_profile = contents(theme, holiday)
    content = on_profile if profile else footer if code.startswith("F") else header
    return render(DESIGNS[code], content)


def header(d: Drawings, key: str, theme: str, holiday: str, code: str, name: str, label: str, profile: bool) -> dict:
    files = drawn(code, theme, holiday, profile)
    return item(d, key, name, label, files["header-day.svg"], files["header-dark.svg"], BUDGET["header"],
                still=(files["header-still-day.svg"], files["header-still-dark.svg"]))


def banner_sections(d: Drawings, key: str, theme: str, holiday: str = "") -> list:
    heads = [header(d, key, theme, holiday, *row) for row in HEADERS]
    phones = []
    for code, name, label, profile in HEADERS:
        if not profile:
            files = drawn(code, theme, holiday)
            phones.append(item(d, key, f"{name}-phone", f"{label} on a phone", files["header-narrow-day.svg"],
                               files["header-narrow-dark.svg"], BUDGET["header"]))
    feet, links = [], []
    for code, name, label in FOOTERS:
        files = drawn(code, theme, holiday)
        feet.append(item(d, key, name, label, files["footer-day.svg"], files["footer-dark.svg"], BUDGET["footer"]))
        phones.append(item(d, key, f"{name}-phone", f"{label} on a phone", files["footer-narrow-day.svg"],
                           files["footer-narrow-dark.svg"], BUDGET["footer"]))
        if code == "F1":
            _, footer, _ = contents(theme, holiday)
            for text, _ in footer.links:
                name = f"link-{slug(text)}"
                links.append(chip(d, key, name, text, files[f"{name}-day.svg"], files[f"{name}-dark.svg"]))
    return [
        {"key": "headers", "title": "Headers", "note": NOTES["headers"], "items": heads},
        {"key": "phones", "title": "On a phone", "note": NOTES["phones"], "items": phones},
        {"key": "footers", "title": "Footers", "note": NOTES["footers"], "items": feet,
         "rows": [{"label": "Link buttons", "chips": links}]},
    ]


def chip(d: Drawings, key: str, name: str, label: str, day: str, dark: str | None = None) -> dict:
    """A small drawing shown in a row: one file on both grounds, or a day file and a dark one."""
    w, h = dims(day)
    if dark is None or dark == day:
        path = d.add(f"{key}/{name}.svg", day)
        return {"label": label, "w": w, "h": h, "day": path, "dark": path}
    return {"label": label, "w": w, "h": h, "day": d.add(f"{key}/{name}-day.svg", day),
            "dark": d.add(f"{key}/{name}-dark.svg", dark)}


@lru_cache(maxsize=None)
def specimen() -> dict:
    spec = loads(SPECIMEN.read_text(encoding="utf-8"))
    return elements_data.merged(elements_data.check(spec["elements"]), {}, subject="driftmark/driftmark", today=TODAY)


def element_section(d: Drawings, key: str, theme: str, holiday: str = "") -> dict:
    elements = specimen()
    files = elements_data.render(elements, theme, holiday) if holiday else elements_data.render(elements, theme)
    items = []
    for eid in SHOWN:
        kind = elements[eid]["kind"]
        variant = elements_draw.variants(kind, elements[eid])[0]
        label = kind.capitalize() + (", half page" if variant == "half" else "")
        items.append(item(d, key, eid, label, files[elements_data.file_name(eid, variant, "day")],
                          files[elements_data.file_name(eid, variant, "dark")], BUDGET["card" if kind == "placard"
                                                                                       else "sheet"]))
    return {"key": "elements", "title": "Elements", "note": NOTES["elements"], "items": items}


def badge_chips(d: Drawings, key: str, theme: str, holiday: str = "", prefix: str = "badge") -> list:
    """Each style once, then a live badge in each state. A classic badge is one file on both grounds; a plate has a
    day file and a dark one; a live badge is one file."""
    chips = []
    for style in STYLES:
        b = {"name": "license", "label": "License", "message": "MIT", "icon": "scale", "style": style}
        if theme not in prints.PRINTS:
            b["message_color"] = "yellow"
        svgs = list(badges_data.draw(b, {}, theme=theme, shade=None, seed=SEED, holiday=holiday).values())
        chips.append(chip(d, key, f"{prefix}-{style}", style, svgs[0], svgs[-1]))
    for state, message in STATES:
        b = {"name": "ci", "label": "CI", "icon": "check", "style": "flat",
             "measure": {"kind": "workflow", "workflow": "checks.yml"}}
        files = badges_data.draw(b, {"ci": {"message": message, "state": state}}, theme=theme, shade=None, seed=SEED,
                                 holiday=holiday)
        chips.append(chip(d, key, f"{prefix}-live-{state}", f"live, {message.lower()}", list(files.values())[0]))
    return chips


def badge_section(d: Drawings, key: str, theme: str, holiday: str = "") -> dict:
    if holiday:
        return {"key": "badges", "title": "Badges",
                "note": "On a standard page a badge keeps its classic style; on a print's page it is a plate, with a "
                        "day file and a dark one. A live badge shows its state.",
                "rows": [{"label": "On a standard page", "chips": badge_chips(d, key, "standard", holiday)},
                         {"label": "On a print's page", "chips": badge_chips(d, key, "blueprint", holiday,
                                                                              "plate")}]}
    note = ("Classic badges in all six styles, one file each, and a live badge in each of its states."
            if theme == prints.STANDARD else
            "In a print every badge is a plate, with a day file and a dark one. A live plate takes its state's print.")
    return {"key": "badges", "title": "Badges", "note": note, "rows": [{"label": "", "chips": badge_chips(d, key,
                                                                                                       theme)}]}


def swatches(key: str) -> list:
    """The colours a theme is known by, each with what it colours."""
    if key in holidays.SETS:
        held = holidays.drawn_by(key)
        return [{"role": f"{role}, {when}", "hex": hexof(held.ink(night)[role])}
                for night, when in ((False, "day"), (True, "night")) for role in ("title", "accent", "body")]
    if key == prints.STANDARD:
        return [{"role": role, "hex": hexof(token)} for role, token in
                (("label", pieces.DAY["label"]), ("ink", pieces.DAY["ink"]), ("accent", pieces.ACCENT),
                 ("rule", pieces.DAY["rule"]), ("night paper", pieces.DARK["paper"]))]
    if key == prints.RAINBOW:
        return [{"role": tone.removesuffix("print"), "hex": hexof(prints.PRINTS[tone]["line"])}
                for tone in prints.SPECTRUM]
    p = prints.PRINTS[key]
    roles = [("line", p["line"]), ("ink", p["ink"]), ("sheet", p["sheet"])]
    if p.get("night"):
        roles.append(("night line", p["night"]))
    return [{"role": role, "hex": hexof(token)} for role, token in roles]


def thumb(key: str) -> dict:
    return {"day": f"{key}/h2-still-day.svg", "dark": f"{key}/h2-still-dark.svg"}


def months_design(key: str) -> str:
    """A collection's design as a page on the collection's calendar draws it, on the first of its month:
    `medieval-forge:2026-11-01`. The year the pages show draws every design as its month's, so its headers carry
    the month's mark."""
    return f"{key}:{TODAY[:4]}-{collections.owner(key).month_of(key):02d}-01"


def collection_entry(d: Drawings, key: str) -> dict:
    """A collection as one entry: its year, each month's design as its H2 header, and where the rest is."""
    c = collections.COLLECTIONS[key]
    year = [header(d, k, prints.STANDARD, months_design(k), "H2", "h2",
                   f"{collections.MONTHS[i]}: {collections.name_of(k)}", False) for i, k in enumerate(c.keys)]
    return {"key": key, "name": c.name, "group": "collection", "tag": "a design a month",
            "kicker": "Collection, a design for each month",
            "note": "Twelve pixel designs on one subject, one for each month of the year: the page is drawn in the "
                    "month's design, and the next takes over on the first of every month. A holiday's set still "
                    "takes over around its day.",
            "use": f"theme: {key}",
            "use_note": f"Or name one design to keep it all year, like theme: {c.keys[0]}. Add sign: {signs(key)[0]}, or "
                        "any of the twelve, and every header carries that sign all year. Every design is drawn in "
                        "full on the collection's own page.",
            "link": f"{key}/index.html",
            "swatches": [{"role": collections.MONTHS[i][:3].lower(),
                          "hex": hexof(collections.drawn_by(k).ink(False)["title"])} for i, k in enumerate(c.keys)],
            "slices": [thumb(k) for k in c.keys],
            "sections": [{"key": "year", "title": "The year", "note": NOTES["year"], "items": year}]}


def theme_entry(d: Drawings, key: str) -> dict:
    if key in collections.COLLECTIONS:
        return collection_entry(d, key)
    if key in holidays.SETS:
        held = holidays.drawn_by(key)
        w = holidays.window(key, 2027 if key == holidays.NEW_YEAR else 2026)
        span = f"{w.start:%B} {w.start.day} to {w.end:%B} {w.end.day}"
        kept = ", which New Year's Day always keeps" if key == holidays.NEW_YEAR else ""
        return {"key": key, "name": held.name, "group": "holiday", "tag": f"{w.start:%b} {w.start.day} to "
                f"{w.end:%b} {w.end.day}", "kicker": f"Holiday set, up {span}",
                "note": f"Up {span}, around {holidays.NAMES[key]} ({w.day:%B} {w.day.day}), at the default three "
                        f"days{kept}. It takes over whatever theme the page is in, then hands it back.",
                "use": "holidays: true",
                "use_note": "On by default. A set is never picked as a theme: it comes up around its day whatever the "
                            "theme, and holidays: false keeps every set away.",
                "swatches": swatches(key), "thumb": thumb(key),
                "sections": banner_sections(d, key, "standard", key)
                + [element_section(d, key, "standard", key), badge_section(d, key, "standard", key)]}
    if key == prints.RAINBOW:
        spectrum = [header(d, tone, tone, "", "H2", "h2", tone, False) for tone in prints.SPECTRUM]
        return {"key": key, "name": key, "group": "print", "tag": "all nine",
                "kicker": "Print, the spectrum in turn",
                "note": "Moves to the next colour of the spectrum each time something the page shows changes, and "
                        "keeps its colour on a quiet day.",
                "use": f"theme: {key}", "use_note": "", "swatches": swatches(key),
                "slices": [thumb(tone) for tone in prints.SPECTRUM],
                "sections": [{"key": "spectrum", "title": "The spectrum", "note": NOTES["spectrum"],
                              "items": spectrum}]}
    if key == prints.STANDARD:
        entry = {"group": "standard", "tag": "default", "kicker": "The default theme",
                 "note": "The original badges' own look at the size of a header: it opens with one badge the width of "
                         "the page, and every letter holds 4.5:1 against its ground.",
                 "use_note": "Or leave theme out: standard is the default."}
    else:
        order = list(prints.PRINTS).index(key) + 1
        colour = key.removesuffix("print")
        entry = {"group": "print", "tag": colour, "kicker": f"Print {order:02d} of {len(prints.PRINTS):02d}",
                 "note": f"A drafting sheet in {colour}: its lines on white by day and its sheet by night.",
                 "use_note": ""}
    sections = banner_sections(d, key, key) + [element_section(d, key, key), badge_section(d, key, key)]
    return {"key": key, "name": key, "use": f"theme: {key}", "swatches": swatches(key), "thumb": thumb(key),
            "sections": sections} | entry


def paths(entry: dict) -> list[str]:
    """Every drawing a theme's sheet shows, its own and any it borrows."""
    found = []
    for section in entry["sections"]:
        for it in section.get("items", []):
            found += [it[k] for k in ("day", "dark", "sday", "sdark") if k in it]
        for row in section.get("rows", []):
            for c in row["chips"]:
                found += [c["day"], c["dark"]]
    return list(dict.fromkeys(found))


def script_json(value) -> str:
    """JSON that is safe inside a <script> element."""
    return (json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            .replace("</", "<\\/").replace("<!--", "<\\u0021--"))


def clear(out: Path) -> None:
    """Empty `out` for a fresh drawing, but only when it is empty or holds this page."""
    if not out.exists():
        return
    page = out / "index.html"
    if any(out.iterdir()) and not (page.is_file() and MARK in page.read_text(encoding="utf-8", errors="replace")):
        raise SystemExit(f"{out} holds something other than the theme-sets page; give an empty folder or the page's")
    shutil.rmtree(out)


def build(out: Path, bundle: bool = False, only: list[str] | None = None) -> dict:
    """Draw the themes into `out`; returns the page's manifest."""
    resources.install()
    keys = ([prints.STANDARD, *prints.PRINTS, prints.RAINBOW] + [k for k in holidays.KEYS if k in holidays.SETS]
            + collections.themes())
    if only:
        unknown = sorted(set(only) - set(keys))
        if unknown:
            raise SystemExit(f"no such theme: {', '.join(unknown)}")
        keys = [k for k in keys if k in only]
    d = Drawings()
    entries = [theme_entry(d, key) for key in keys]
    manifest = {"kit": f"{KIT} v{KIT_VERSION}", "payload": "bundles" if bundle else "files", "grounds": GROUNDS,
                "drawings": len(d.files), "themes": entries}
    thumbs, first = {}, {}
    clear(out)
    out.mkdir(parents=True)
    if bundle:
        (out / "themes").mkdir()
        for entry in entries:
            files = {p: d.files[p] for p in paths(entry)}
            (out / "themes" / f"{entry['key']}.json").write_text(json.dumps(files, separators=(",", ":")) + "\n",
                                                                 encoding="utf-8")
        for entry in entries:
            for pair in [entry["thumb"]] if "thumb" in entry else entry["slices"]:
                thumbs.update({p: d.files[p] for p in pair.values()})
        first = {"key": entries[0]["key"], "files": {p: d.files[p] for p in paths(entries[0])}}
    else:
        for path, svg in d.files.items():
            target = out / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(svg, encoding="utf-8")
    page = TEMPLATE.read_text(encoding="utf-8")
    if not bundle:
        # A host that serves the file as it is needs the document's own head; a bundle's host wraps the page in one.
        page = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page)
    for slot, value in (("__MANIFEST__", script_json(manifest)), ("__THUMBS__", script_json(thumbs)),
                        ("__FIRST__", script_json(first)), ("__KIT__", f"{KIT} v{KIT_VERSION}")):
        page = page.replace(slot, value)
    (out / "index.html").write_text(page, encoding="utf-8")
    for entry in entries:
        if entry["group"] == "collection":
            collection_page(entry["key"], out / entry["key"], bundle)
    return manifest


def collection_page(key: str, out: Path, bundle: bool) -> None:
    """A collection's own page, beside this one, by build-collection.py."""
    spec = importlib.util.spec_from_file_location("build_collection", Path(__file__).with_name("build-collection.py"))
    page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(page)
    page.build(key, out, bundle=bundle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draw every theme the kit draws, and the page that shows them.")
    parser.add_argument("out", type=Path, help="the folder to draw into, emptied first (docs/themes)")
    parser.add_argument("--bundle", action="store_true", help="one data file per theme instead of one SVG per drawing")
    parser.add_argument("--only", default="", help="a comma-separated list of themes to draw; every theme if empty")
    args = parser.parse_args(argv)
    manifest = build(args.out, bundle=args.bundle, only=[k for k in args.only.split(",") if k])
    print(f"{len(manifest['themes'])} themes, {manifest['drawings']} drawings, in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
