# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The command line: `markdown-kit <command>`.

  version    the kit and the version of the files it draws
  settings   read a repository's settings and print them in full, every default filled in
  holidays   the holiday calendar: which set is up on a day, and the windows ahead or in a year
  palette    the 64 colour tokens, and the letters each takes
  icons      the 64 icons

A setting that is wrong exits with status 2 and one line naming it. The run,
check and preview commands arrive with the parts they draw.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from domain import KIT, KIT_VERSION, holidays, palette, prints

from . import config
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
    sub.add_parser("version", help="the kit and the version of the files it draws")
    s = sub.add_parser("settings", help="read a repository's settings and print them in full")
    s.add_argument("--root", type=Path, default=Path("."), help="the repository (default: here)")
    s.add_argument("--input", action="append", metavar="KEY=VALUE", help="a value the stub sets, as the workflow "
                   "passes it: mode, theme, holidays, holiday-days")
    h = sub.add_parser("holidays", help="the holiday calendar")
    h.add_argument("--year", type=int, help="every window in this year")
    h.add_argument("--days", type=int, default=holidays.DEFAULT_DAYS, help="holiday-days, 3 to 7 (default 3)")
    h.add_argument("--today", type=_date, help="the day to ask about (default: today)")
    h.add_argument("--timezone", default="UTC", help="the zone the day is taken in (default UTC)")
    sub.add_parser("palette", help="the 64 colour tokens")
    sub.add_parser("icons", help="the 64 icons")
    return p


def cmd_version(args, ports: Ports) -> int:
    print(f"{KIT} {KIT_VERSION}", file=ports.out)
    return 0


def cmd_settings(args, ports: Ports) -> int:
    cfg = config.load(args.root, ports, _pairs(args.input))
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


COMMANDS = {"version": cmd_version, "settings": cmd_settings, "holidays": cmd_holidays, "palette": cmd_palette,
            "icons": cmd_icons}


def main(argv: list[str], ports: Ports) -> int:
    args = parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args, ports)
    except ValueError as exc:
        print(f"{KIT}: {exc}", file=ports.err)
        return 2
