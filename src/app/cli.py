# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The command line: `markdown-kit <command>`.

  run        measure the page through GitHub, draw it, and write what changed
  render     redraw from what the lock kept, or from a saved measurement, and write
  check      redraw from what the lock kept and compare, writing nothing; exit 1 when stale
  preview    draw a sample page into a folder, the way a run would
  measure    measure the page and print the measurement
  set        set badges' values in the settings file, NAME=MESSAGE[:COLOR], keeping its comments
  lint       draw every design for every sample in every print, and lint every file
  catalogue  docs/Catalogue.md: every trophy and achievement, and what earns it
  calibrate  measure the repository population the repository-mode trophies are set against
  settings   read a repository's settings and print them in full, every default filled in
  holidays   the holiday calendar: which set is up on a day, and the windows ahead or in a year
  palette    the 64 colour tokens, and the letters each takes
  icons      the 64 icons
  version    the kit and the version of the files it draws

A setting that is wrong exits with status 2 and one line naming it; a fault
outside the settings, like a refused token or no network, exits 1 the same way.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from domain import KIT, KIT_VERSION, holidays, palette, prints, settings
from domain.badges import classic as badges_classic
from domain.badges import data as badges_data
from domain.badges import plates as badges_plates
from domain.badges import settings as badges_settings
from domain.banners import sample as banners_sample
from domain.banners.compose import compose
from domain.banners.content import Footer, Header
from domain.banners.designs import DESIGNS, check as lint_files, render as render_design
from domain.banners.settings import check as banners_check
from domain.elements import data as elements_data
from domain.trophies import art as trophies_art
from domain.trophies import catalogue as trophies_catalogue
from domain.trophies import catalogue_md
from domain.trophies import plan as trophies_plan
from domain.trophies import sample as trophies_sample

from . import calibrate, config, run
from .ports import Ports


class Usage(ValueError):
    pass


def _date(text: str) -> dt.date:
    try:
        return dt.date.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{text!r} is not a date like 2026-10-31") from exc


def _pairs(items: list[str]) -> dict:
    out = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep:
            raise Usage(f"--input {item!r}: write it as key=value")
        out[key.strip()] = value
    return out


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=KIT, description="Draws a README's header, footer, badges, elements and "
                                "trophies as committed SVG files.")
    sub = p.add_subparsers(dest="command", required=True, metavar="command")

    def page(sp, today: bool = True):
        sp.add_argument("--root", type=Path, default=Path("."), help="the repository (default: here)")
        sp.add_argument("--input", action="append", metavar="KEY=VALUE", help="a value the stub sets, as the "
                        "workflow passes it: mode, theme, holidays, holiday-days")
        if today:
            sp.add_argument("--today", type=_date, help="the day to draw, YYYY-MM-DD (default: today in the page's zone)")
        return sp

    r = page(sub.add_parser("run", help="measure the page through GitHub, draw it, and write what changed"))
    r.add_argument("--commit-file", default="", help="write a Conventional Commit message here when something changed")
    r.add_argument("--save", default="", help="also save the measurement here, as JSON")
    page(sub.add_parser("render", help="redraw from what the lock kept, and write"), today=False).add_argument(
        "--from", dest="source", type=Path, help="a saved measurement to redraw instead")
    page(sub.add_parser("check", help="compare the committed page with a fresh drawing; exit 1 when stale"),
         today=False).add_argument("--from", dest="source", type=Path, help="a saved measurement to compare with")
    page(sub.add_parser("preview", help="draw a sample page into a folder, the way a run would"))
    page(sub.add_parser("measure", help="measure the page and print the measurement"))
    page(sub.add_parser("set", help="set badges' values in the settings file, keeping its comments"),
         today=False).add_argument("values", nargs="+", metavar="NAME=MESSAGE[:COLOR]",
                                   help="a badge's name, its new message, and a colour after a colon if it changes")
    sub.add_parser("lint", help="draw every design for every sample in every print, and lint every file").add_argument(
        "--specimen", type=Path, help="a repository whose elements are drawn in every print too")
    sub.add_parser("catalogue", help="print docs/Catalogue.md, written from the catalogue")
    c = sub.add_parser("calibrate", help="measure the repository population the trophies are set against")
    c.add_argument("--out", type=Path, default=Path("src/domain/data/calibration/repositories.json"),
                   help="where the measurement goes (default: the kit's own data file)")
    c.add_argument("--per-band", type=int, default=40, help="repositories to measure in each star band (default 40)")
    c.add_argument("--seed", type=int, help="the sample's seed (default: today's ordinal, so a re-run repeats it)")
    c.add_argument("--today", type=_date, help="the day to date it (default: today)")
    s = page(sub.add_parser("settings", help="read a repository's settings and print them in full"), today=False)
    s.set_defaults(command="settings")
    h = sub.add_parser("holidays", help="the holiday calendar")
    h.add_argument("--year", type=int, help="every window in this year")
    h.add_argument("--days", type=int, default=holidays.DEFAULT_DAYS, help="holiday-days, 3 to 7 (default 3)")
    h.add_argument("--today", type=_date, help="the day to ask about (default: today)")
    h.add_argument("--timezone", default="UTC", help="the zone the day is taken in (default UTC)")
    sub.add_parser("palette", help="the 64 colour tokens")
    sub.add_parser("icons", help="the 64 icons")
    sub.add_parser("version", help="the kit and the version of the files it draws")
    return p


def _cfg(args, ports: Ports) -> dict:
    return config.load(args.root, ports, _pairs(args.input))


def _saved(args, ports: Ports) -> dict | None:
    """A measurement saved by `run --save`, or by the banners kit's own `--save`."""
    if not getattr(args, "source", None):
        return None
    text = ports.read_text(args.source)
    if text is None:
        raise Usage(f"--from {args.source}: no such file")
    data = json.loads(text)
    return {"banners": data} if "mode" in data else data


def cmd_run(args, ports: Ports) -> int:
    return run.run(args.root, _cfg(args, ports), ports, today=args.today, commit_file=args.commit_file,
                   save=args.save)


def cmd_render(args, ports: Ports) -> int:
    return run.render(args.root, _cfg(args, ports), ports, _saved(args, ports))


def cmd_check(args, ports: Ports) -> int:
    return run.check(args.root, _cfg(args, ports), ports, _saved(args, ports))


def cmd_preview(args, ports: Ports) -> int:
    return run.preview(args.root, _cfg(args, ports), ports, args.today)


def cmd_measure(args, ports: Ports) -> int:
    _, measured, _ = run.measure_page(args.root, _cfg(args, ports), ports, args.today)
    print(json.dumps(measured, indent=1, ensure_ascii=False), file=ports.out)
    return 0


def cmd_set(args, ports: Ports) -> int:
    """Rewrite each named badge's message, and colour, in the settings file, and check the result still holds."""
    cfg = _cfg(args, ports)
    where, text = config.find(args.root, ports)
    if text is None:
        raise Usage(f"set: there is no settings file to set values in; badges are listed in {config.NAMES[0]}")
    listed = {b["name"]: b for b in (cfg["badges"]["list"] if isinstance(cfg["badges"], dict) else [])}
    updates = {}
    for spec in args.values:
        name, message, colour = badges_settings.update(spec)
        if name not in listed:
            raise Usage(f"set: {where} lists no badge named {name}")
        if listed[name].get("measure"):
            raise Usage(f"set: {name} measures its own value; take out its measure to set one")
        updates[name] = (message, colour)
    new, missing = badges_settings.set_values(text, updates)
    if missing:
        raise Usage(f"set: {', '.join(missing)} has no message line in {where} to rewrite")
    settings.validate(ports.parse_yaml(new), _pairs(args.input), catalogue=ports.catalogue, parts=config.PARTS,
                      where=where)
    ports.write_text(args.root / where, new)
    print(f"set {len(updates)} value{'s' if len(updates) != 1 else ''} in {where}", file=ports.out)
    return 0


def badge_specimens() -> list[tuple[str, dict, str]]:
    """A badge of every style and every plate, in every print and state: what `lint` draws them from."""
    out = []
    for style in badges_classic.STYLES:
        for label, message in (("Status", "Active"), ("Only a label", ""), ("", "Only a message")):
            out.append((f"{style} {label or message}", {"name": "specimen", "label": label, "message": message,
                                                       "icon": "pulse", "style": style}, "standard"))
    for tone in prints.PRINTS:
        for style in badges_classic.STYLES:
            out.append((f"{badges_plates.BLUEPRINT}{style} {tone}", {"name": "specimen", "label": "License",
                                                                     "message": "MIT", "icon": "scale",
                                                                     "style": style}, tone))
    for state in ("green", "yellow", "red", "slate"):
        out.append((f"live {state}", {"name": "specimen", "label": "Build", "message": "Passing", "icon": "check",
                                      "label_color": "gold", "message_color": state}, "blueprint"))
    return out


def trophy_specimens():
    """Every trophy style at every tier in both cases, every pin in every state, and both banner cards."""
    for style, draw in trophies_art.STYLES.items():
        for case, theme in trophies_art.CASES.items():
            for cores in (trophies_catalogue.CORE, trophies_catalogue.RCORE):
                for core in cores:
                    for v in (0, 310, 3610, 23500, 640000):
                        yield f"{style} {core.key} {v} {case}", draw(theme, core, v, {"rank": True, "delta": 9, "new": True})
    for mode, s in trophies_sample.SAMPLES.items():
        m = trophies_catalogue.MODES[mode]
        for case, theme in trophies_art.CASES.items():
            for a in m["ach"]:
                for cur in (None, 0, a.tiers[-1]):
                    yield f"pin {a.slug} {cur} {case}", trophies_art.pin(theme, a, cur)
            yield f"level {mode} {case}", trophies_art.level_card(theme, m["core"], s["values"], m["ach"], s["curs"],
                                                                   s["subject"], ("flame", "#000000", "X", "Y"))
            yield f"next-up {mode} {case}", trophies_art.next_up_card(theme, m["core"], s["values"], m["ach"], s["curs"])


def contents() -> dict:
    """Every content the kit is linted with: each sample, composed, and the kit's own lines."""
    out = {"kit": (Header(), Footer())}
    for key, m in banners_sample.SAMPLES.items():
        h, f, _ = compose(m, banners_check({}))
        out[key] = (h, f)
    return out


def cmd_lint(args, ports: Ports) -> int:
    failed = 0
    themes = (prints.STANDARD, *prints.PRINTS)
    for name, (h, f) in contents().items():
        for code, design in DESIGNS.items():
            largest, problems = 0, {}
            for tone in themes:
                files = render_design(design, (h if design.kind == "header" else f).with_(tone=tone))
                problems.update({f"{tone} {k}": v for k, v in lint_files(design, files).items()})
                largest = max(largest, *(len(svg.encode("utf-8")) for svg in files.values()))
            print(f"{name:<10} {code} {design.name:<12} {len(themes)} themes, largest {largest / 1000:.1f} KB"
                  + ("" if not problems else f"  PROBLEMS: {problems}"), file=ports.out)
            failed += bool(problems)
    largest, problems = 0, []
    for what, b, theme in badge_specimens():
        try:
            files = badges_data.draw(b, {}, theme=theme, shade=None, seed="2026W01")
        except ValueError as exc:
            problems.append(f"{what}: {exc}")
            continue
        largest = max(largest, *(len(svg.encode("utf-8")) for svg in files.values()))
    print(f"badges     {len(badge_specimens())} specimens, largest {largest / 1000:.1f} KB"
          + ("" if not problems else f"  PROBLEMS: {problems}"), file=ports.out)
    failed += bool(problems)
    largest, problems, n = 0, [], 0
    for what, svg in trophy_specimens():
        n += 1
        largest = max(largest, len(svg.encode("utf-8")))
        problems += [f"{what}: {p}" for p in trophies_plan.lint(svg)]
    print(f"trophies   {n:,} specimens, largest {largest / 1000:.1f} KB"
          + ("" if not problems else f"  PROBLEMS: {problems[:5]}"), file=ports.out)
    failed += bool(problems)
    if args.specimen:
        cfg = config.load(args.specimen, ports)
        section = cfg["elements"] if isinstance(cfg["elements"], dict) else {}
        elements = elements_data.merged(section, {}, subject=cfg["subject"])
        largest, problems = 0, []
        for tone in themes:
            try:
                files = elements_data.render(elements, tone)
            except ValueError as exc:  # a drawing that fails the lint says which, and how
                problems.append(f"{tone}: {exc}")
                continue
            largest = max(largest, *(len(svg.encode("utf-8")) for svg in files.values()))
        print(f"elements   {len(elements)} of them, {len(themes)} themes, largest {largest / 1000:.1f} KB"
              + ("" if not problems else f"  PROBLEMS: {problems}"), file=ports.out)
        failed += bool(problems)
    return 1 if failed else 0


def cmd_catalogue(args, ports: Ports) -> int:
    ports.out.write(catalogue_md.page())
    return 0


def cmd_calibrate(args, ports: Ports) -> int:
    today = args.today or dt.date.today()
    client = ports.paced()
    result = calibrate.run(client, args.per_band, args.seed if args.seed is not None else today.toordinal(), today,
                           log=lambda line: print(line, file=ports.err))
    ports.write_text(args.out, json.dumps(result, indent=1) + "\n")
    print(f"wrote {args.out}: {result['n']} repositories in {len(result['bands'])} bands, {result['calls']} API calls",
          file=ports.out)
    for key, spec in result["cores"].items():
        print(f"  {key:13} " + "  ".join(f"{t}: {p:g}%" for t, p in spec["anchors"]), file=ports.out)
    return 0


def cmd_settings(args, ports: Ports) -> int:
    cfg = _cfg(args, ports)
    print(json.dumps({k.replace("_", "-"): v for k, v in cfg.items()}, indent=1, ensure_ascii=False), file=ports.out)
    return 0


def _span(w: holidays.Window) -> str:
    return f"{w.start:%a %b %d} to {w.end:%a %b %d, %Y}  ({w.days} days)"


def cmd_holidays(args, ports: Ports) -> int:
    try:
        holidays.check_days(args.days)
    except holidays.HolidayError as exc:
        raise Usage(str(exc)) from exc
    if args.year:
        for w in holidays.windows(args.year, args.days):
            if w.day.year == args.year:
                print(f"{w.name:<18} {_span(w)}", file=ports.out)
        return 0
    today = args.today or ports.today(args.timezone)
    now = holidays.active(today, args.days)
    print(f"{today:%a %b %d, %Y}: " + (f"{now.name}'s set is up" if now else "no holiday set is up"), file=ports.out)
    for w in holidays.upcoming(today, args.days):
        print(f"{w.name:<18} {_span(w)}", file=ports.out)
    return 0


def cmd_palette(args, ports: Ports) -> int:
    for name, hexv in palette.PALETTE.items():
        letters = palette.letters_on(name)
        print(f"{name:<12} {hexv}  {letters} letters, {palette.contrast(letters, name):.2f}:1", file=ports.out)
    return 0


def cmd_icons(args, ports: Ports) -> int:
    print("\n".join(palette.ICONS), file=ports.out)
    return 0


def cmd_version(args, ports: Ports) -> int:
    print(f"{KIT} {KIT_VERSION}", file=ports.out)
    return 0


COMMANDS = {"run": cmd_run, "render": cmd_render, "check": cmd_check, "preview": cmd_preview, "measure": cmd_measure,
            "set": cmd_set, "lint": cmd_lint, "catalogue": cmd_catalogue, "calibrate": cmd_calibrate, "settings": cmd_settings, "holidays": cmd_holidays, "palette": cmd_palette,
            "icons": cmd_icons, "version": cmd_version}


def main(argv: list[str], ports: Ports) -> int:
    args = parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args, ports)
    except ValueError as exc:
        print(f"{KIT}: {exc}", file=ports.err)
        return 2
    except RuntimeError as exc:  # git, the network, or GitHub refusing: not the settings' fault, but said as plainly
        print(f"{KIT}: {exc}", file=ports.err)
        return 1
