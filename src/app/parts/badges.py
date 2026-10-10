# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The badges, measured and planned: what each live badge reads now, and the files and block the rows make.

Measuring asks GitHub, through the client the run is handed, for what each
badge names under `measure:`: a workflow's last finished run, the newest commit
a person made, or the latest release. Each comes back as a message and a state,
and the lock keeps them, so a committed badge can be redrawn and checked later
without a token, and the badges can never say what the page no longer does.

  workflow      GET /repos/{owner}/{name}/actions/workflows/{file}/runs, the
                newest finished run on the branch
  last-commit   a person's: GitHub's commit search, newest first; a
                repository's: its default branch's history, as the footer
                reads it
  release       GET /repos/{owner}/{name}/releases/latest

Localizing reads the repository's tracked Markdown, which `run` hands in, and
plans the badges to draw and the documents to rewrite, from the settings and
the lock's record of what it drew before.
"""
from __future__ import annotations

import datetime as dt
import posixpath

from domain.badges import data as BD
from domain.badges import live
from domain.badges import localize as BL
from domain.history import automated

from .banners import last_change

LOCK_KEY = "badges"
# How many of a person's newest commits the search reads before it gives up finding one they made themselves.
SEARCHED = 50


def _days(stamp: str | None, today: dt.date) -> int | None:
    """Whole days from an ISO timestamp's date, in UTC as GitHub keeps it, to `today`; None for no timestamp."""
    if not stamp:
        return None
    return max(0, (today - dt.date.fromisoformat(stamp[:10])).days)


def workflow(gh, repository: str, file: str, branch: str, notes: list) -> tuple[str, str]:
    """The state of `file`'s newest finished run in `repository`, on `branch` or the default one."""
    if not branch:
        repo = gh.rest(f"/repos/{repository}")
        if repo is None:
            notes.append(f"cannot read {repository}; the badge for its workflow {file} shows no data")
            return live.NO_DATA
        branch = repo.get("default_branch") or ""
    params = {"status": "completed", "per_page": 1, **({"branch": branch} if branch else {})}
    runs = gh.rest(f"/repos/{repository}/actions/workflows/{file}/runs", **params)
    if runs is None:
        notes.append(f"cannot read the runs of {file} in {repository}; its badge shows no data")
        return live.NO_DATA
    found = runs.get("workflow_runs") or []
    return live.workflow((found[0] or {}).get("conclusion") if found else None)


def person_commit(gh, login: str, today: dt.date, notes: list) -> tuple[str, str]:
    """How long ago `login` last committed anywhere GitHub's search reaches, setting the kits' and bots' aside."""
    found = gh.rest("/search/commits", q=f"author:{login}", sort="committer-date", order="desc", per_page=SEARCHED)
    if found is None:
        notes.append(f"cannot search {login}'s commits; the badge shows no data")
        return live.NO_DATA
    for item in found.get("items") or []:
        commit = (item or {}).get("commit") or {}
        who = commit.get("committer") or {}
        subject = (commit.get("message") or "").split("\n", 1)[0]
        if not automated(subject, who.get("name") or "", who.get("email") or ""):
            return live.last_commit(_days(who.get("date"), today))
    notes.append(f"none of {login}'s newest {SEARCHED} commits is one a person made; the badge shows no data")
    return live.NO_DATA


def repository_commit(gh, full: str, today: dt.date, notes: list) -> tuple[str, str]:
    """How long ago a person last committed to `full`'s default branch, read the way the footer reads it."""
    owner, _, name = full.partition("/")
    return live.last_commit(_days(last_change(gh, owner, name, notes) or None, today))


def release(gh, full: str, today: dt.date, notes: list) -> tuple[str, str]:
    """`full`'s latest release and how fresh it is; no release when it has none."""
    got = gh.rest(f"/repos/{full}/releases/latest")
    if got is None:
        if gh.rest(f"/repos/{full}") is None:
            notes.append(f"cannot read {full}; the badge for its release shows no data")
            return live.NO_DATA
        return live.release("", None)
    return live.release(str(got.get("tag_name") or ""), _days(got.get("published_at"), today))


def measure(badges: list[dict], *, gh, mode: str, subject: str, here: str, today: dt.date, notes: list) -> dict:
    """What every badge the kit measures reads now, by name: {"message", "state"}.

    What a badge leaves to the page is the page's own: its repository, and on a
    profile its person, whose newest commit is looked for everywhere. A badge a
    workflow sets says what its settings say, so it is not measured here.
    """
    own = subject if mode == "repository" else (here or f"{subject}/{subject}")
    out = {}
    for b in badges:
        m = b.get("measure")
        if not m or m["kind"] == live.SET:
            continue
        if m["kind"] == "workflow":
            said = workflow(gh, m["repository"] or own, m["target"], m["branch"], notes)
        elif m["kind"] == "last-commit":
            target = m["target"] or (subject if mode == "profile" else own)
            said = (repository_commit(gh, target, today, notes) if "/" in target
                    else person_commit(gh, target, today, notes))
        else:
            said = release(gh, m["target"] or own, today, notes)
        out[b["name"]] = live.value(*said)
    return out


def sample(badges: list[dict]) -> dict:
    """What a sample page shows for each badge the kit measures: the best each can say."""
    return {b["name"]: live.value(*live.SAMPLE[b["measure"]["kind"]]) for b in badges
            if b.get("measure") and b["measure"]["kind"] != live.SET}


def plan(section: dict, measured: dict, *, theme: str, shade: str | None, today: dt.date, out: str, readme: str,
         draw: bool = True, holiday: str = "") -> dict:
    """Every badge's files by path, the README's block, and what each says, on a page in `theme` (and in
    the pixel set `holiday` names, a holiday's while it is up or a collection's design)."""
    folder = posixpath.join(out.strip("/") or ".", "badges")
    base = posixpath.relpath(folder, posixpath.dirname(readme) or ".")
    return BD.plan(section["list"], measured, theme=theme, shade=shade, today=today, folder=folder, base=base,
                   draw_files=draw, holiday=holiday)


# --- localizing -----------------------------------------------------------------------------------

def localized(out: str) -> str:
    """The folder localized badges are drawn in, from the repository's root: inside the static badges' folder,
    since a shields.io badge says what its link says, in a folder of their own."""
    return posixpath.join(out.strip("/") or ".", "badges", "static", BL.FOLDER)


def localized_before(out: str) -> list[str]:
    """The folders localized badges were drawn in before, from the repository's root: beside the static and live
    badges' folders, and under `markdown` while every part was drawn into that one folder."""
    root = out.strip("/") or "."
    return [posixpath.join(root, "badges", BL.FOLDER), posixpath.join(root, "markdown", "badges", BL.FOLDER)]


def localize(docs: dict[str, str], record: dict, *, on: bool, here: str, branch: str, out: str,
             readme: str) -> dict:
    """What localizing makes of the repository's Markdown, `docs` by path.

    With `on`, every static shields.io badge is drawn and its links rewritten;
    either way, a badge localized before is drawn again from the lock's `record`
    for as long as a document refers to it, and dropped once none does. A link
    to a badge in a folder localizing has left is moved to the badge's new file,
    on or off: absolute when the repository is known, else relative.

    Returns {"files": {path: svg}, "texts": {path: rewritten text}, "drew":
    [the paths among them whose shields.io links it drew], "moved": [those
    whose links moved to the new folder], "keep": [paths kept as they are],
    "record": {file name: its badge}, "notes": [...]}.
    """
    folder = localized(out)
    pattern, before = BL.references(folder), BL.references(*localized_before(out))
    urls: dict[str, dict] = {}
    notes = []
    if on and not here:
        notes.append("localize: cannot tell which repository this is, so no shields.io link is rewritten")
    elif on:
        for path, text in docs.items():
            for url in BL.SHIELDS.findall(text):
                spec = BL.parse(url)
                if spec is None:
                    notes.append(f"{path}: left {url} as it is; only a static shields.io badge is drawn")
                else:
                    urls.setdefault(url, spec)
    names = BL.names(list(urls.values()), taken=record)
    links = {url: names[BL.signature(spec)] for url, spec in urls.items()}
    found = {(m["folder"], m["name"]) for text in docs.values() for p in (pattern, before) for m in p.finditer(text)}
    kept = {name: record[name] for name in sorted({name for _, name in found}) if name in record}
    kept.update({links[url]: spec for url, spec in urls.items()})
    unknown = sorted((where, name) for where, name in found if name not in kept)
    notes += [f"{where}/{name} is referenced, but the lock has no record of drawing it; it is kept as it is"
              for where, name in unknown]
    texts, drew, moved = {}, [], []
    absolute = f"https://raw.githubusercontent.com/{here}/{branch}/{folder}/" if here else ""
    for path, text in docs.items():
        base = absolute or posixpath.relpath(folder, posixpath.dirname(path) or ".") + "/"
        keep = path == readme or not (on and here)
        shown = BL.rewrite(text, links, base, pattern, keep)
        new = BL.rewrite(text, links, base, pattern, keep, moved=before, drawn=kept)
        if new != text:
            texts[path] = new
            drew += [path] if shown != text else []
            moved += [path] if new != shown else []
    return {"files": {f"{folder}/{name}": BL.draw(spec) for name, spec in sorted(kept.items())},
            "texts": texts, "drew": drew, "moved": moved, "keep": [f"{where}/{name}" for where, name in unknown],
            "record": dict(sorted(kept.items())), "notes": notes}
