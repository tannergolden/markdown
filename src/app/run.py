# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A run, start to finish: measure the page, draw every part, write what changed, and say what moved.

  run      measure through GitHub and git, draw, write the files, the README's blocks and the lock
  render   redraw from what the lock kept (or a saved measurement), write, and measure nothing
  check    redraw from what the lock kept and compare, byte for byte, writing nothing
  preview  draw a sample page into a folder the way a run would, and keep its lock, so the folder checks

The files a part draws are written only when their bytes change, and a file the
kit drew that no part draws any more is removed, so the folder always holds
exactly the page. The lock is written when anything changed, and once a week
besides, which keeps GitHub from switching off a quiet repository's schedule.

With `localize` on under `badges`, a run also draws the shields.io badges the
repository's other Markdown links to and points those links at the files; a
badge it drew that way is kept, and redrawn, for as long as a document shows it.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import posixpath
import textwrap
from pathlib import Path

from domain import lock, prints, readme, settings
from domain.banners import plan as banners_plan
from domain.banners import sample as banners_sample

from .page import Page, here_of, mode_and_subject, settle
from .parts import badges, banners, elements

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
    parts = lk["parts"]
    if (parts.get("banners") or {}).get("last"):
        out["banners"] = parts["banners"]["last"]
    if "elements" in parts:
        out["elements"] = parts["elements"].get("measured") or {}
    if "badges" in parts:
        out["badges"] = parts["badges"].get("measured") or {}
        if parts["badges"].get("branch"):
            out["localize"] = {"branch": parts["badges"]["branch"]}
    return out


def _drawn_elements(lk: dict) -> list[str]:
    """The elements the committed page carries: the ones this kit drew last, and so the ones it may take out."""
    return list((lk["parts"].get("elements") or {}).get("drawn") or [])


# --- planning ----------------------------------------------------------------------------------

def plan_page(page: Page, measured: dict, *, draw: bool = True, was: list[str] = ()) -> dict:
    """Everything a run writes for this page: every part's files by path, the README's blocks, and the notes.

    `was` names the elements the committed page carries, so one no longer in
    the settings has its block taken out; a block the kit never drew is never
    touched.
    """
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
    listed = cfg["badges"]["list"] if isinstance(cfg["badges"], dict) else []
    result["blocks"]["badges"] = None
    if listed:
        p = badges.plan(cfg["badges"], measured.get("badges") or {}, theme=page.theme, shade=page.rainbow,
                        today=page.today, out=page.out, readme=page.readme, draw=draw)
        result["parts"]["badges"] = p
        result["files"].update(p["files"])
        result["blocks"]["badges"] = p["block"]
        result["notes"] += p["notes"]
    section = cfg["elements"] if isinstance(cfg["elements"], dict) else {}
    result["blocks"].update({f"element:{eid}": None for eid in was if eid not in section})
    if section:
        p = elements.plan(section, measured.get("elements") or {}, subject=page.subject,
                          today=page.today.isoformat(), tone=page.theme, out=page.out, readme=page.readme, draw=draw)
        result["parts"]["elements"] = p
        result["files"].update(p["files"])
        result["blocks"].update(p["blocks"])
        result["notes"] += p["notes"]
    return result


def _docs(page: Page, ports) -> dict[str, str]:
    """The repository's tracked Markdown, by path from the root: what localizing reads. Empty outside git."""
    try:
        repo = ports.git(page.root)
        if not repo.is_repo():
            return {}
        listed = repo.run("ls-files", "-z", "--", "*.md", "*.markdown")
    except (RuntimeError, OSError):
        return {}
    out = {}
    for rel in listed.split("\0"):
        text = ports.read_text(page.root / rel) if rel else None
        if text is not None:
            out[rel] = text
    return out


def _origin_head(page: Page, ports) -> str:
    """The default branch as the clone knows it, from origin's HEAD, or empty."""
    try:
        ref = ports.git(page.root).run("symbolic-ref", "-q", "refs/remotes/origin/HEAD", check=False).strip()
    except (RuntimeError, OSError):
        return ""
    return ref.removeprefix("refs/remotes/origin/") if ref.startswith("refs/remotes/origin/") else ""


def localize(page: Page, ports, lk: dict, measured: dict) -> dict | None:
    """What localizing plans for this page, or None when it is off and has drawn nothing before."""
    record = (lk["parts"].get("badges") or {}).get("localized") or {}
    on = isinstance(page.cfg["badges"], dict) and page.cfg["badges"]["localize"]
    if not on and not record:
        return None
    branch = ((measured.get("localize") or {}).get("branch") or (lk["parts"].get("badges") or {}).get("branch")
              or _origin_head(page, ports) or "main")
    planned = badges.localize(_docs(page, ports), record, on=on, here=page.here, branch=branch, out=page.out,
                              readme=page.readme)
    planned["branch"] = branch
    return planned


def _merge(planned: dict, extra: dict | None) -> dict:
    """The page's plan with localizing's badges, documents and notes in it."""
    if extra:
        planned["files"].update(extra["files"])
        planned["texts"] = extra["texts"]
        planned["keep"] = extra["keep"]
        planned["notes"] += extra["notes"]
        planned["localized"] = extra
    return planned


def _kept(page: Page, planned: dict) -> set[str]:
    prefix = page.out.strip("/") + "/"
    return {posixpath.relpath(rel, page.out.strip("/")) for rel in [*planned["files"], *planned.get("keep", ())]
            if rel.startswith(prefix)}


def write(page: Page, ports, planned: dict) -> tuple[list[str], list[str]]:
    """Write what differs and remove what is no longer drawn. Returns (the paths that changed, blocks with no place)."""
    root = page.root
    changed = [rel for rel, svg in planned["files"].items() if ports.write_text(root / rel, svg)]
    changed += [f"{page.out}/{gone}" for gone in ports.prune(root / page.out, _kept(page, planned))]
    texts = planned.get("texts") or {}
    changed += [rel for rel, doc in texts.items() if rel != page.readme and ports.write_text(root / rel, doc)]
    text = ports.read_text(root / page.readme) or ""
    new, unplaced = readme.place(texts.get(page.readme, text), planned["blocks"])
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
    out += [f"{rel} (shields.io links to localize)" for rel in planned.get("texts") or {}]
    text = ports.read_text(root / page.readme) or ""
    for name, wanted in planned["blocks"].items():
        found = readme.current(text, name)
        if wanted is not None and found is None:
            if not name.startswith("element:"):
                out.append(f"{page.readme} ({name} markers missing)")
        elif wanted is not None and found != wanted:
            out.append(f"{page.readme} ({name} block differs)")
        elif wanted is None and found is not None:
            out.append(f"{page.readme} ({name} block no longer drawn)")
    return out


# --- saying what happened --------------------------------------------------------------------------

def _series(items: list[str]) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1] if items else ""


def describe(page: Page, planned: dict) -> str:
    parts = planned["parts"]
    head = (banners_plan.describe(parts["banners"]) if "banners" in parts
            else f"the page for {page.subject} ({page.mode}) in {page.theme}")
    if "badges" in parts:
        head += f"; badges {', '.join(parts['badges']['names'])}"
    if "elements" in parts:
        head += f"; elements {', '.join(parts['elements']['names'])}"
    if planned.get("localized"):
        n = len(planned["localized"]["record"])
        head += f"; {n} localized badge{'s' if n != 1 else ''}"
    return head


def _before(page: Page, lk: dict) -> dict | None:
    """What the committed page showed, for the commit message to compare with; None on a first run."""
    last = remembered(lk)
    if "banners" not in last or page.cfg["banners"] is False:
        return None
    try:
        return banners_plan.facts(plan_page(page, {"banners": last["banners"]}, draw=False)["parts"]["banners"])
    except (ValueError, KeyError, TypeError):
        return None


def _badge_news(page: Page, planned: dict, was: dict, changed: list[str]) -> tuple[list[str], list[str]]:
    """What the badges' part of a commit says: (the badges redrawn, by name; a sentence for each kind of change)."""
    parts, news = planned["parts"], []
    folder = posixpath.join(page.out.strip("/") or ".", "badges") + "/"
    redrawn = sorted({rel[len(folder):].split("/", 1)[-1].removesuffix(".svg").removesuffix("-dark")
                      for rel in changed if rel.startswith(folder) and not rel.startswith(folder + "localized/")})
    if "badges" in parts:
        says = parts["badges"]["says"]
        labels = {b["name"]: b.get("label") or b["name"] for b in page.cfg["badges"]["list"]}
        moved = [n for n in says if (was.get(n) or {}).get("message") not in (None, says[n])]
        if moved:
            news.append("The live badges moved: " + _series([f"{labels[n]} from {was[n]['message']} to {says[n]}"
                                                             for n in moved]) + ".")
        rest = [n for n in redrawn if n not in moved and n in says]
        if rest:
            news.append(f"Redrawn: the badge{'s' if len(rest) > 1 else ''} {_series(rest)}.")
    texts = (planned.get("localized") or {}).get("texts") or {}
    docs = [rel for rel in changed if rel in texts]
    if docs:
        news.append(f"Drew the shields.io badges that {_series(docs)} linked to as committed files, and pointed "
                    "the links at them, so no document fetches a badge from a service any more.")
    return redrawn, news


def commit_message(page: Page, planned: dict, before: dict | None, changed: list[str], run_id: str = "",
                   was: dict | None = None) -> str:
    """A Conventional Commit for this run: what the page now shows, what moved, and why it is committed.

    `was` is what the live badges said before this run, so the message can say
    which of them moved.
    """
    parts = planned["parts"]
    folder = posixpath.join(page.out.strip("/") or ".", "elements") + "/"
    redrawn = sorted({rel[len(folder):].rsplit("-", 1)[0].removesuffix("-narrow").removesuffix("-still")
                      for rel in changed if rel.startswith(folder)})
    news = [f"Redrawn from the settings and the repository: the elements {_series(redrawn)}."] if redrawn else []
    badged, told = _badge_news(page, planned, was or {}, changed)
    news += told
    if "banners" in parts:
        message = banners_plan.commit_message(parts["banners"], before, changed, run_id,
                                              rainbow=page.rainbow is not None)
        if news:
            head, _, rest = message.partition("\n\n")
            paras = rest.split("\n\n")
            for para in news:
                paras.insert(len(paras) - 1, textwrap.fill(para, 72))
            message = head + "\n\n" + "\n\n".join(paras)
        return message
    emoji = "\U0001F3F7\ufe0f" if (badged or told) and not redrawn else "\U0001F4D0"
    what = redrawn + (["the badges"] if badged else [])
    subject = (f"chore(markdown): {emoji} redraw {_series(what)}" if what else
               f"chore(markdown): {emoji} localize the shields.io badges" if told else
               f"chore(markdown): {emoji} redraw the page for {page.subject}")
    if len(subject) > 72:
        subject = f"chore(markdown): {emoji} redraw the page for {page.subject}"
    paras = [textwrap.fill(para, 72) for para in news]
    paras.append(textwrap.fill(f"This run rewrote {len(changed)} files. Nothing is fetched when the README is "
                               "viewed, so every value the page shows has to be committed. The kit recognises this "
                               "commit by its scope and never counts it as the repository's last change.", 72))
    return subject + "\n\n" + "\n\n".join(paras) + "\n"


# --- the commands ------------------------------------------------------------------------------

def finish(page: Page, ports, measured: dict, lk: dict, *, use_lock: bool, advance: bool = False,
           commit_file: str = "") -> list[str]:
    """Plan, write and remember one page. Returns the paths that changed."""
    before = _before(page, lk) if use_lock else None
    said = remembered(lk).get("badges") or {}
    was = _drawn_elements(lk)
    extra = localize(page, ports, lk, measured)
    planned = _merge(plan_page(page, measured, was=was), extra)
    shade_was = (lock.drawn(lk) or {}).get("rainbow")
    if page.rainbow and advance and shade_was in prints.SPECTRUM and stale(page, ports, planned):
        # An update: a rainbowprint draws each one in the next colour of the spectrum.
        nxt = prints.rainbow_after(page.rainbow)
        page = dataclasses.replace(page, theme=nxt, rainbow=nxt)
        planned = _merge(plan_page(page, measured, was=was), extra)
    print(describe(page, planned), file=ports.out)
    changed, unplaced = write(page, ports, planned)
    notes = planned["notes"] + [f"{name}: the README has no markers for it yet, so it is not shown; add "
                                f"<!-- markdown:{name}:start --> and its end where it belongs" for name in unplaced]
    for note in notes:
        print(f"note: {note}", file=ports.out)
    if use_lock:
        due = lock.snapshot_due(lk, page.today)
        if changed or due or ports.read_text(page.root / LOCK) is None:
            if "banners" in measured:
                lock.part(lk, "banners")["last"] = {k: measured["banners"][k] for k in BANNERS_KEEP
                                                    if k in measured["banners"]}
            if "elements" in planned["parts"] or "elements" in lk["parts"]:
                record = lock.part(lk, "elements")
                record["measured"] = measured.get("elements") or {}
                record["drawn"] = planned["parts"]["elements"]["names"] if "elements" in planned["parts"] else []
            if "badges" in planned["parts"] or "badges" in lk["parts"] or extra:
                record = lock.part(lk, "badges")
                record["measured"] = measured.get("badges") or {}
                for key in ("localized", "branch"):
                    record.pop(key, None)
                if extra and extra["record"]:
                    record.update(localized=extra["record"], branch=extra["branch"])
            lock.remember_drawn(lk, theme=page.cfg["theme"], today=page.today, rainbow=page.rainbow)
            if due:
                lock.mark_snapshot(lk, page.today)
            if write_lock(page.root, ports, lk):
                changed.append(LOCK)
    print(f"{len(changed)} files changed" if changed else "nothing changed", file=ports.out)
    if commit_file and changed:
        message = commit_message(page, planned, before, changed, ports.env.get("GITHUB_RUN_ID", ""), was=said)
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
    """The page and every part's measurement, read from GitHub and git now."""
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
    listed = cfg["badges"]["list"] if isinstance(cfg["badges"], dict) else []
    if any(b.get("measure") for b in listed):
        notes = []
        measured["badges"] = badges.measure(listed, gh=gh, mode=mode, subject=subject, here=here, today=day,
                                            notes=notes)
        for note in notes:
            print(f"note: {note}", file=ports.out)
    if here and ((isinstance(cfg["badges"], dict) and cfg["badges"]["localize"])
                 or (lk["parts"].get("badges") or {}).get("localized")):
        # The branch a localized badge's link names: the default one, which a checkout may not know.
        known = ((measured.get("banners") or {}).get("repository") or {}).get("branch")
        measured["localize"] = {"branch": known or (gh.rest(f"/repos/{here}") or {}).get("default_branch") or ""}
    section = cfg["elements"] if isinstance(cfg["elements"], dict) else {}
    if section:
        repo = ports.git(root)
        notes: list = []
        measured["elements"] = elements.measure(section, remembered(lk).get("elements") or {}, git=repo.run, gh=gh,
                                                subject=subject if mode == "repository" else here, today=day,
                                                notes=notes)
        for note in notes:
            print(f"note: {note}", file=ports.out)
    return page, measured, lk


def run(root: Path, cfg: dict, ports, *, today: dt.date | None = None, commit_file: str = "", save: str = "") -> int:
    page, measured, lk = measure_page(root, cfg, ports, today)
    if save:
        ports.write_text(Path(save), json.dumps(measured, indent=1, ensure_ascii=False) + "\n")
    finish(page, ports, measured, lk, use_lock=cfg["lock"], advance=True, commit_file=commit_file)
    return 0


def _offline_page(root: Path, cfg: dict, measured: dict, lk: dict, here: str = "") -> Page:
    """The page a saved measurement was taken of, settled without asking GitHub anything."""
    m = measured.get("banners") or {}
    drawn = lock.drawn(lk) or {}
    mode = cfg["mode"] if cfg["mode"] != "auto" else m.get("mode") or "repository"
    subject = cfg["subject"] or m.get("subject") or ""
    stamp = m.get("today") or drawn.get("day")
    day = dt.date.fromisoformat(stamp) if stamp else dt.date(2026, 1, 1)
    return settle(root, cfg, mode=mode, subject=subject, here=here, today=day, lk=lk)


def render(root: Path, cfg: dict, ports, measured: dict | None = None) -> int:
    lk = read_lock(root, ports)
    if measured is None:
        measured = remembered(lk) or sample(cfg)
    finish(_offline_page(root, cfg, measured, lk, here_of(root, ports)), ports, measured, lk, use_lock=False)
    return 0


def check(root: Path, cfg: dict, ports, measured: dict | None = None) -> int:
    """Are the committed files what the kit draws from the measurement they were drawn from?

    No token and no network, and the numbers cannot move underneath it: a stale
    result means a hand-edited file, a missing one, a block that drifted, or
    settings changed without a run.
    """
    lk = read_lock(root, ports)
    measured = remembered(lk) if measured is None else measured
    if cfg["banners"] is not False and "banners" not in measured:
        print("check needs a measurement: run the kit once with the lock on, or pass --from", file=ports.out)
        return 2
    page = _offline_page(root, cfg, measured, lk, here_of(root, ports))
    planned = _merge(plan_page(page, measured, was=_drawn_elements(lk)), localize(page, ports, lk, measured))
    found = stale(page, ports, planned)
    if found:
        print("stale: " + ", ".join(found), file=ports.out)
        return 1
    print(f"{len(planned['files'])} files and the README's blocks are current", file=ports.out)
    return 0


def sample(cfg: dict) -> dict:
    """A sample measurement for the page's mode: the kit's author, or its own repository."""
    mode = "profile" if cfg["mode"] == "profile" else "repository"
    out = {"banners": json.loads(json.dumps(banners_sample.SAMPLES[mode]))}
    if isinstance(cfg["badges"], dict):
        out["badges"] = badges.sample(cfg["badges"]["list"])
    return out


def preview(root: Path, cfg: dict, ports, today: dt.date | None = None) -> int:
    """The sample, drawn into `root` the way a run would, with a lock beside it, so the folder checks."""
    measured = sample(cfg)
    if today:
        measured["banners"]["today"] = today.isoformat()
    lk = lock.new()
    page = _offline_page(root, cfg, measured, lk)
    finish(page, ports, measured, lk, use_lock=True)
    return 0
