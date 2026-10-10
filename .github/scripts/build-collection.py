#!/usr/bin/env python3
"""Draw a collection's year: its twelve designs, a month to each, and the page that shows them.

WHY THIS EXISTS. A collection changes every month, so it is chosen by looking
at its whole year. The page opens on a calendar of the twelve months, each
with its design's header, and below it one design's full sheet: its headers,
phone files, footers, link buttons, the six elements and every badge, each
drawn the way a run draws it, from the kit's own samples and the driftmark
specimen, on GitHub's light and dark grounds. Each design is drawn as its
month's design, the way a page on the collection's calendar draws it, so its
headers carry the month's mark. The theme-sets page shows the collection as
one entry and sends a reader here for the rest.

Nothing is fetched and nothing depends on the day it runs, except which month
the calendar marks as this one, which the reader's own browser works out.

  make themes                                   each complete collection, in docs/themes/<collection>
  build-collection.py medieval OUT --draft      a collection still being drawn, its months to come marked
  build-collection.py medieval OUT --bundle     one data file per design, for a host that caps files
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("build_theme_sets", HERE / "build-theme-sets.py")
TS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TS)

from domain import KIT, KIT_VERSION, collections  # noqa: E402
from domain.collections.hand import signs  # noqa: E402
from domain.palette import hexof  # noqa: E402
from infra import resources  # noqa: E402

TEMPLATE = HERE / "collection.html"
# The page says it drew this folder, so a rebuild may empty it and a wrong path never loses anything.
MARK = '<meta name="generator" content="markdown-kit collection">'


def swatches(held) -> list:
    """The colours a design is known by: its title, accent and body inks, by day and by night."""
    return [{"role": f"{role}, {when}", "hex": hexof(held.ink(night)[role])}
            for night, when in ((False, "day"), (True, "night")) for role in ("title", "accent", "body")]


def design_entry(d, c, key: str) -> dict:
    """One month: its design's words, inks and every drawing its sheet shows, or a month still to come."""
    n = c.month_of(key)
    month = {"key": key, "name": collections.name_of(key), "n": n, "month": collections.MONTHS[n - 1]}
    held = collections.drawn_by(key)
    if held is None:
        return month | {"drawn": False}
    shown = TS.months_design(key)       # drawn as the month's design, so its headers carry the month's mark
    sections = (TS.banner_sections(d, key, "standard", shown)
                + [TS.element_section(d, key, "standard", shown), TS.badge_section(d, key, "standard", shown)])
    return month | {"drawn": True, "tagline": getattr(held, "tagline", ""), "about": getattr(held, "about", ""),
                    "swatches": swatches(held), "colours": len(held.tokens),
                    "hero": {"day": f"{key}/h1-still-day.svg", "dark": f"{key}/h1-still-dark.svg"},
                    "use": f"theme: {key}", "sign": signs(c.key)[n - 1], "sections": sections}


def clear(out: Path) -> None:
    """Empty `out` for a fresh drawing, but only when it is empty or holds a collection's page."""
    if not out.exists():
        return
    page = out / "index.html"
    if any(out.iterdir()) and not (page.is_file() and MARK in page.read_text(encoding="utf-8", errors="replace")):
        raise SystemExit(f"{out} holds something other than a collection's page; give an empty folder or the page's")
    shutil.rmtree(out)


def build(name: str, out: Path, bundle: bool = False, draft: bool = False) -> dict:
    """Draw collection `name`'s year into `out`; returns the page's manifest. A collection still being drawn
    is drawn only as a `draft`, with its months to come marked."""
    resources.install()
    c = collections.COLLECTIONS.get(name)
    if c is None:
        raise SystemExit(f"no collection {name!r} (one of {', '.join(collections.COLLECTIONS)})")
    if not draft and not collections.complete(name):
        raise SystemExit(f"{collections.unfinished(name)}; draw it with --draft to see it")
    d = TS.Drawings()
    months = [design_entry(d, c, key) for key in c.keys]
    drawn = [m for m in months if m["drawn"]]
    if not drawn:
        raise SystemExit(f"{name}: none of its designs is drawn yet")
    manifest = {"kit": f"{KIT} v{KIT_VERSION}", "payload": "bundles" if bundle else "files", "grounds": TS.GROUNDS,
                "drawings": len(d.files), "collection": {"key": c.key, "name": c.name}, "months": months,
                "drawn": len(drawn), "draft": draft}
    heroes, first = {}, {}
    clear(out)
    out.mkdir(parents=True)
    if bundle:
        (out / "themes").mkdir()
        for m in drawn:
            files = {p: d.files[p] for p in TS.paths(m)}
            (out / "themes" / f"{m['key']}.json").write_text(json.dumps(files, separators=(",", ":")) + "\n",
                                                             encoding="utf-8")
            heroes.update({p: d.files[p] for p in m["hero"].values()})
        first = {"key": drawn[0]["key"], "files": {p: d.files[p] for p in TS.paths(drawn[0])}}
    else:
        for path, svg in d.files.items():
            target = out / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(svg, encoding="utf-8")
    page = TEMPLATE.read_text(encoding="utf-8")
    if not bundle:
        # A host that serves the file as it is needs the document's own head; a bundle's host wraps the page in
        # one. The template carries its own charset, which every host needs for the page's letters.
        page = ('<!doctype html>\n<html lang="en">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page)
    for slot, value in (("__MANIFEST__", TS.script_json(manifest)), ("__HEROES__", TS.script_json(heroes)),
                        ("__FIRST__", TS.script_json(first)), ("__KIT__", f"{KIT} v{KIT_VERSION}"),
                        ("__NAME__", c.name)):
        page = page.replace(slot, value)
    (out / "index.html").write_text(page, encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draw a collection's twelve designs, and the page that shows them.")
    parser.add_argument("collection", help="the collection to draw: " + ", ".join(collections.COLLECTIONS))
    parser.add_argument("out", type=Path, help="the folder to draw into, emptied first")
    parser.add_argument("--bundle", action="store_true", help="one data file per design instead of one SVG per drawing")
    parser.add_argument("--draft", action="store_true",
                        help="draw a collection still being drawn, its months to come marked")
    args = parser.parse_args(argv)
    manifest = build(args.collection, args.out, bundle=args.bundle, draft=args.draft)
    print(f"{manifest['collection']['name']}: {manifest['drawn']} of 12 designs, {manifest['drawings']} drawings, "
          f"in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
