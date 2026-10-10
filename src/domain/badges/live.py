# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What a live badge measures, and the state each value is drawn in.

A badge whose value is measured names how under `measure:`, which makes it
live: drawn into `dynamic/`, and the only kind of badge that may wear the gold
label. The kit measures the first three itself, every run, so their message
and colour are never older than the page:

  measure: last-commit            the newest commit a person made: the page's
                                  person on a profile, its repository otherwise
  measure:
    last-commit: tannergolden     a person's newest commit anywhere, or a
                                  repository's, written owner/name
  measure: release                the latest release of the page's repository
  measure:
    release: owner/name           another repository's
  measure:
    workflow: checks.yml          a workflow's last finished run
    repository: owner/name        (optional) the repository it runs in, else the page's
    branch: main                  (optional) the branch its runs are on, else the default one

and the fourth is measured elsewhere:

  measure: set                    a workflow measures it and writes its value
                                  with `markdown-kit set NAME=MESSAGE[:COLOR]`

Every value has a state, in the colours the standards give a live badge:
green, yellow and red, and slate for no data. The kit's own refreshes, the
old kits', and anything a bot committed never count as a person's commit.
"""
from __future__ import annotations

import re

MEASURED = ("workflow", "last-commit", "release")   # what the kit measures itself
SET = "set"                                          # measured elsewhere, and written with `markdown-kit set`
KINDS = (*MEASURED, SET)
NO_DATA = ("No Data", "slate")
NO_RELEASE = ("No Release", "slate")
# Every message a kind shows besides a release's own tag. A plate keeps room
# for the widest of them, so a badge that changes its value never changes width.
VALUES = {
    "workflow": ("Passing", "Failing", NO_DATA[0]),
    "last-commit": ("This Week", "This Month", "Over a Month", NO_DATA[0]),
    "release": (NO_RELEASE[0], NO_DATA[0]),
    SET: (NO_DATA[0],),
}
# What a sample page shows for each kind, where nothing has been measured.
SAMPLE = {"workflow": ("Passing", "green"), "last-commit": ("This Week", "green"), "release": ("v1.0.0", "green")}
# A workflow's conclusions that mean it failed. Anything else that finished (cancelled, skipped, neutral) says nothing.
FAILED = ("failure", "timed_out", "startup_failure")
# Days, at most: a commit this recent is this week's or this month's, and a release this recent is fresh or recent.
WEEK, MONTH = 7, 31
FRESH, RECENT = 90, 365

_LOGIN = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})"
_REPOSITORY = re.compile(_LOGIN + r"/[A-Za-z0-9._-]{1,100}")
_PERSON = re.compile(_LOGIN)
_WORKFLOW = re.compile(r"[A-Za-z0-9._-]+\.ya?ml|\d+")
_BRANCH = re.compile(r"[A-Za-z0-9._/-]+")


class MeasureError(ValueError):
    pass


def _key(k: object) -> str:
    return str(k).replace("_", "-")


def parse(value: object) -> dict:
    """A `measure:` setting as {"kind", "target", "repository", "branch"}, with "" for what it leaves to the page."""
    if isinstance(value, str):
        kind = value.strip()
        if kind == "workflow":
            raise MeasureError("measure: a workflow is named by its file, as workflow: checks.yml")
        if kind not in KINDS:
            raise MeasureError(f"measure: {kind!r} is not one of {', '.join(KINDS)}")
        return {"kind": kind, "target": "", "repository": "", "branch": ""}
    if not isinstance(value, dict):
        raise MeasureError(f"measure: expected one of {', '.join(KINDS)}, or a map naming one")
    given = {_key(k): v for k, v in value.items()}
    if SET in given:
        raise MeasureError("measure: set takes nothing; write it as measure: set")
    kinds = [k for k in given if k in MEASURED]
    if len(kinds) != 1:
        raise MeasureError(f"measure: name exactly one of {', '.join(MEASURED)}")
    kind = kinds[0]
    for k in given:
        if k not in (kind, "repository", "branch"):
            raise MeasureError(f"measure: unknown key {k!r} (a {kind} takes "
                               + ("repository and branch" if kind == "workflow" else "only its own") + ")")
    if kind != "workflow" and ("repository" in given or "branch" in given):
        raise MeasureError(f"measure: repository and branch are a workflow's; name the repository as {kind}: owner/name")
    text = {k: "" if v is None or v is True else str(v).strip() for k, v in given.items()}
    target = text[kind]
    if kind == "workflow" and not _WORKFLOW.fullmatch(target):
        raise MeasureError(f"measure: workflow: {target!r} is not a workflow's file, like checks.yml")
    if kind == "last-commit" and target and not (_PERSON.fullmatch(target) or _REPOSITORY.fullmatch(target)):
        raise MeasureError(f"measure: last-commit: {target!r} is neither a login nor owner/name")
    if kind == "release" and target and not _REPOSITORY.fullmatch(target):
        raise MeasureError(f"measure: release: {target!r} is not owner/name")
    repository, branch = text.get("repository", ""), text.get("branch", "")
    if repository and not _REPOSITORY.fullmatch(repository):
        raise MeasureError(f"measure: repository: {repository!r} is not owner/name")
    if branch and not _BRANCH.fullmatch(branch):
        raise MeasureError(f"measure: branch: {branch!r} is not a branch's name")
    return {"kind": kind, "target": target, "repository": repository, "branch": branch}


def workflow(conclusion: str | None) -> tuple[str, str]:
    """A workflow's last finished run: passing, failing, or no data when it has none or it says nothing."""
    if conclusion == "success":
        return "Passing", "green"
    if conclusion in FAILED:
        return "Failing", "red"
    return NO_DATA


def last_commit(days: int | None) -> tuple[str, str]:
    """How long ago a person last committed: this week, this month, or longer; no data when nobody has."""
    if days is None:
        return NO_DATA
    if days <= WEEK:
        return "This Week", "green"
    if days <= MONTH:
        return "This Month", "yellow"
    return "Over a Month", "red"


def release(tag: str, days: int | None) -> tuple[str, str]:
    """The latest release's tag, green while it is fresh, yellow within the year, red after it."""
    if not tag:
        return NO_RELEASE
    if days is None or days <= FRESH:
        return tag, "green"
    return (tag, "yellow") if days <= RECENT else (tag, "red")


def value(message: str, state: str) -> dict:
    """One badge's measurement, as the lock keeps it."""
    return {"message": message, "state": state}
