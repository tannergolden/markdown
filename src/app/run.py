# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A run, start to finish: measure the page, draw every part, write what changed, and say what moved.

  run      measure through GitHub, draw, write the files, the README's blocks and the lock
  render   redraw from what the lock kept (or a saved measurement), write, and measure nothing
  check    redraw from what the lock kept and compare, byte for byte, writing nothing
  preview  draw a sample page into a folder the way a run would, and keep its lock, so the folder checks

The files a part draws are written only when their bytes change, and a file the
kit drew that no part draws any more is removed, so the folder always holds
exactly the page. The lock is written when anything changed, and once a week
besides, which keeps GitHub from switching off a quiet repository's schedule.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import posixpath
from pathlib import Path

from domain import lock, prints, readme, settings
from domain.banners import plan as banners_plan
from domain.banners import sample as banners_sample

from .page import Page, here_of, mode_and_subject, settle
from .parts import banners

LOCK = ".github/markdown.lock.json"
# What the lock keeps of the banners' measurement: what `plan` needs to draw them again, nothing that moves by itself.
BANNERS_KEEP = ("mode", "subject", "today", "repository", "profile")


def read_lock(root: Path, ports) -> dict:
    return lock.loads(ports.read_text(Path(root) / LOCK))


def write_lock(root: Path, ports, lk: dict) -> bool:
    return ports.write_text(Path(root) / LOCK, lock.dumps(lk))


def remembered(lk: dict) -> dict:
    """Each part's last measurement, as the lock kept it: what a check and a render redraw from."""
    out = {}
    last = lock.part(lk, "banners").get("last") if "banners" in lk["parts"] else None
    if last:
        out["banners"] = last
    return out


# --- planning ----------------------------------------------------------------------------------

def plan_page(page: Page, measured: dict, *, draw: bool = True) -> dict:
    """Everything a run writes for this page: every part's files by path, the README's blocks, and the notes."""
    cfg = page.cfg
    result: dict = {"parts": {}, "files": {}, "blocks": {}, "notes": []}
    if cfg["banners"] is False:
        result["blocks"].update({"header": None, "footer": None})
    elif "banners" in measured:
        p = banners.plan(measured["banners"], cfg["banners"], theme=page.theme, out=page.out, readme=page.readme,
                         draw=draw)
        result["parts"]["banners"] = p
        result["files"].update(p["files"])
        # A design set to none takes its block away, so both are named whether drawn or not.
        result["blocks"].update({"header": None, "footer": None, **p["blocks"]})
        result["notes"] += p["notes"]
    return result


def _kept(page: Page, planned: dict) -> set[str]:
    prefix = page.out.strip("/") + "/"
    return {posixpath.relpath(rel, page.out.strip("/")) for rel in planned["files"] if rel.startswith(prefix)}


def write(page: Page, ports, planned: dict) -> tuple[list[str], list[str]]:
    """Write what differs and remove what is no longer drawn. Returns (the paths that changed, blocks with no place)."""
    root = page.root
    changed = [rel for rel, svg in planned["files"].items() if ports.write_text(root / rel, svg)]
    changed += [f"{page.out}/{gone}" for gone in ports.prune(root / page.out, _kept(page, planned))]
    text = ports.read_text(root / page.readme) or ""
    new, unplaced = readme.place(text, planned["blocks"])
    if new != text:
        ports.write_text(root / page.readme, new)
        changed.append(page.readme)
    return changed, unplaced


def stale(page: Page, ports, planned: dict) -> list[str]:
    """Every way the committed page differs from a fresh drawing of the same measurement."""
    root, out = page.root, []
    for rel, svg in planned["files"].items():
        now = ports.read_text(root / rel)
        if now is None:
            out.append(f"{rel} (missing)")
        elif now != svg:
            out.append(f"{rel} (differs)")
    keep = _kept(page, planned)
    out += [f"{page.out}/{name} (no longer drawn)" for name in ports.drawn(root / page.out) if name not in keep]
    text = ports.read_text(root / page.readme) or ""
    for name, wanted in planned["blocks"].items():
        found = readme.current(text, name)
        if wanted is not None and found is None:
            out.append(f"{page.readme} ({name} markers missing)")
        elif wanted is not None and found != wanted:
            out.append(f"{page.readme} ({name} block differs)")
        elif wanted is None and found is not None:
            out.append(f"{page.readme} ({name} block no longer drawn)")
    return out


# --- saying what happened --------------------------------------------------------------------------

def describe(page: Page, planned: dict) -> str:
    parts = planned["parts"]
    if "banners" in parts:
        return banners_plan.describe(parts["banners"])
    return f"the page for {page.subject} ({page.mode}): no banners"


def _before(page: Page, lk: dict) -> dict | None:
    """What the committed page showed, for the commit message to compare with; None on a first run."""
    last = remembered(lk)
    if "banners" not in last or "banners" not in (page.cfg or {}) or page.cfg["banners"] is False:
        return None
    try:
        return banners_plan.facts(plan_page(page, last, draw=False)["parts"]["banners"])
    except (ValueError, KeyError, TypeError):
        return None


def commit_message(page: Page, planned: dict, before: dict | None, changed: list[str], run_id: str = "") -> str:
    if "banners" in planned["parts"]:
        return banners_plan.commit_message(planned["parts"]["banners"], before, changed, run_id,
                                           rainbow=page.rainbow is not None)
    return (f"chore(markdown): \U0001FAA7 redraw the page for {page.subject}\n\n"
            f"This run rewrote {len(changed)} files. Nothing is fetched when the README is viewed, so every value\n"
            "the page shows has to be committed.\n")


# --- the commands ------------------------------------------------------------------------------

def finish(page: Page, ports, measured: dict, lk: dict, *, use_lock: bool, advance: bool = False,
           commit_file: str = "") -> list[str]:
    """Plan, write and remember one page. Returns the paths that changed."""
    before = _before(page, lk) if use_lock else None
    planned = plan_page(page, measured)
    was = (lock.drawn(lk) or {}).get("rainbow")
    if page.rainbow and advance and was in prints.SPECTRUM and stale(page, ports, planned):
        # An update: a rainbowprint draws each one in the next colour of the spectrum.
        nxt = prints.rainbow_after(page.rainbow)
        page = dataclasses.replace(page, theme=nxt, rainbow=nxt)
        planned = plan_page(page, measured)
    print(describe(page, planned), file=ports.out)
    changed, unplaced = write(page, ports, planned)
    notes = planned["notes"] + [f"{name}: the README has no markers for it yet, so it is not shown"
                                for name in unplaced]
    for note in notes:
        print(f"note: {note}", file=ports.out)
    if use_lock:
        due = lock.snapshot_due(lk, page.today)
        if changed or due or ports.read_text(page.root / LOCK) is None:
            for name, m in measured.items():
                keep = BANNERS_KEEP if name == "banners" else tuple(m)
                lock.part(lk, name)["last"] = {k: m[k] for k in keep if k in m}
            lock.remember_drawn(lk, theme=page.cfg["theme"], today=page.today, rainbow=page.rainbow)
            if due:
                lock.mark_snapshot(lk, page.today)
            if write_lock(page.root, ports, lk):
                changed.append(LOCK)
    print(f"{len(changed)} files changed" if changed else "nothing changed", file=ports.out)
    if commit_file and changed:
        message = commit_message(page, planned, before, changed, ports.env.get("GITHUB_RUN_ID", ""))
        ports.write_text(Path(commit_file), message)
        print(message.splitlines()[0], file=ports.out)
    summary = ports.env.get("GITHUB_STEP_SUMMARY")
    if summary:
        ports.append_text(Path(summary), f"### Markdown\n\n{describe(page, planned)}\n\n"
                          f"{len(changed)} files changed\n" + "".join(f"\n- {n}" for n in notes) + "\n")
    return changed


def _is_organization(gh, owner: str) -> bool:
    who = gh.rest(f"/users/{owner}") or {}
    return who.get("type") == "Organization"


def measure_page(root: Path, cfg: dict, ports, today: dt.date | None = None) -> tuple[Page, dict, dict]:
    """The page and every part's measurement, read from GitHub now."""
    lk = read_lock(root, ports)
    here = here_of(root, ports)
    gh = ports.github()
    owner, _, name = here.partition("/")
    organization = (cfg["mode"] == "auto" and not cfg["subject"] and name.lower() in (".github", ".github-private")
                    and _is_organization(gh, owner))
    mode, subject = mode_and_subject(cfg, here, organization)
    if mode == "organization":
        raise settings.SettingsError("organization pages are not drawn yet; set mode: repository for now")
    day = today or ports.today(cfg["timezone"])
    page = settle(root, cfg, mode=mode, subject=subject, here=here, today=day, lk=lk)
    measured = {}
    if cfg["banners"] is not False:
        measured["banners"] = banners.measure(gh, mode, subject, here or f"{subject}/{subject}",
                                              today=day.isoformat())
    return page, measured, lk


def run(root: Path, cfg: dict, ports, *, today: dt.date | None = None, commit_file: str = "", save: str = "") -> int:
    page, measured, lk = measure_page(root, cfg, ports, today)
    if save:
        ports.write_text(Path(save), json.dumps(measured, indent=1, ensure_ascii=False) + "\n")
    finish(page, ports, measured, lk, use_lock=cfg["lock"], advance=True, commit_file=commit_file)
    return 0


def _offline_page(root: Path, cfg: dict, measured: dict, lk: dict) -> Page:
    """The page a saved measurement was taken of, settled without asking GitHub anything."""
    m = measured.get("banners") or {}
    mode = m.get("mode") or ("repository" if cfg["mode"] == "auto" else cfg["mode"])
    subject = m.get("subject") or cfg["subject"] or ""
    day = dt.date.fromisoformat(m["today"]) if m.get("today") else dt.date(2026, 1, 1)
    return settle(root, cfg, mode=mode, subject=subject, here="", today=day, lk=lk)


def render(root: Path, cfg: dict, ports, measured: dict | None = None) -> int:
    lk = read_lock(root, ports)
    measured = measured or remembered(lk) or sample(cfg)
    finish(_offline_page(root, cfg, measured, lk), ports, measured, lk, use_lock=False)
    return 0


def check(root: Path, cfg: dict, ports, measured: dict | None = None) -> int:
    """Are the committed files what the kit draws from the measurement they were drawn from?

    No token and no network, and the numbers cannot move underneath it: a stale
    result means a hand-edited file, a missing one, a block that drifted, or
    settings changed without a run.
    """
    lk = read_lock(root, ports)
    measured = measured or remembered(lk)
    if not measured:
        print("check needs a measurement: run the kit once with the lock on, or pass --from", file=ports.out)
        return 2
    page = _offline_page(root, cfg, measured, lk)
    planned = plan_page(page, measured)
    found = stale(page, ports, planned)
    if found:
        print("stale: " + ", ".join(found), file=ports.out)
        return 1
    print(f"{len(planned['files'])} files and the README's blocks are current", file=ports.out)
    return 0


def sample(cfg: dict) -> dict:
    """A sample measurement for the page's mode: the kit's author, or its own repository."""
    mode = "profile" if cfg["mode"] == "profile" else "repository"
    return {"banners": json.loads(json.dumps(banners_sample.SAMPLES[mode]))}


def preview(root: Path, cfg: dict, ports, today: dt.date | None = None) -> int:
    """The sample, drawn into `root` the way a run would, with a lock beside it, so the folder checks."""
    measured = sample(cfg)
    if today:
        measured["banners"]["today"] = today.isoformat()
    lk = lock.new()
    page = _offline_page(root, cfg, measured, lk)
    finish(page, ports, measured, lk, use_lock=True)
    return 0
