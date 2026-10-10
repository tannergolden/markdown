# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The repository the kit runs in, through the `git` on the machine.

Everything here is a question the working tree can answer without the API:
where it came from, what changed, when a file last changed and who changed it.
Committing and pushing the files a run drew are here too, so the run and its
tests share one path to the remote.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_SLUG = re.compile(r"github\.com[:/]+([A-Za-z0-9-]+)/([A-Za-z0-9._-]+?)(?:\.git)?/?$")
_FIELD = "\x1f"


class GitError(RuntimeError):
    pass


@dataclass(frozen=True)
class Commit:
    sha: str
    when: dt.datetime          # the commit's time, in UTC
    subject: str
    committer_name: str
    committer_email: str


@dataclass(frozen=True)
class Person:
    name: str
    email: str

    def env(self, role: str) -> dict:
        return {f"GIT_{role}_NAME": self.name, f"GIT_{role}_EMAIL": self.email}


# The bot GitHub Actions commits as, the committer on every commit a run makes.
ACTIONS_BOT = Person("github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com")


class Git:
    def __init__(self, root: Path):
        self.root = Path(root)

    def run(self, *args: str, env: dict | None = None, check: bool = True) -> str:
        try:
            done = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True,
                                  env={**os.environ, **(env or {})})
        except FileNotFoundError as exc:
            raise GitError("git is not on PATH") from exc
        if check and done.returncode != 0:
            detail = (done.stderr or done.stdout).strip().splitlines()
            raise GitError(f"`git {' '.join(args)}` failed: {detail[-1] if detail else f'exit {done.returncode}'}")
        return done.stdout

    def is_repo(self) -> bool:
        try:
            return self.run("rev-parse", "--is-inside-work-tree").strip() == "true"
        except GitError:
            return False

    def head(self) -> str | None:
        try:
            return self.run("rev-parse", "HEAD").strip()
        except GitError:
            return None

    def branch(self) -> str | None:
        """The branch checked out, or None when HEAD is detached."""
        try:
            return self.run("symbolic-ref", "--short", "-q", "HEAD").strip() or None
        except GitError:
            return None

    def is_shallow(self) -> bool:
        return self.run("rev-parse", "--is-shallow-repository").strip() == "true"

    def origin(self) -> str | None:
        try:
            return self.run("remote", "get-url", "origin").strip() or None
        except GitError:
            return None

    def slug(self) -> tuple[str, str] | None:
        """The (owner, name) of the GitHub repository `origin` points at, or None."""
        url = self.origin()
        m = _SLUG.search(url or "")
        return (m.group(1), m.group(2)) if m else None

    def commits(self, path: str | None = None, limit: int = 500) -> list[Commit]:
        """The newest `limit` commits on HEAD, or those that touched `path`, newest first."""
        fmt = _FIELD.join(("%H", "%ct", "%s", "%cn", "%ce"))
        args = ["log", f"--max-count={limit}", f"--format={fmt}"]
        if path:
            args += ["--", path]
        try:
            out = self.run(*args)
        except GitError:
            return []   # no commits yet
        found = []
        for line in out.splitlines():
            parts = line.split(_FIELD)
            if len(parts) != 5:
                continue
            sha, stamp, subject, name, email = parts
            when = dt.datetime.fromtimestamp(int(stamp), tz=dt.timezone.utc)
            found.append(Commit(sha, when, subject, name, email))
        return found

    def changed(self, paths: list[str] | None = None) -> list[str]:
        """The paths under `paths` (or anywhere) that differ from HEAD, untracked ones included."""
        out = self.run("status", "--porcelain", "-z", "--untracked-files=all", "--", *(paths or ["."]))
        entries, items = out.split("\0"), []
        i = 0
        while i < len(entries):
            entry = entries[i]
            if not entry:
                i += 1
                continue
            status, path = entry[:2], entry[3:]
            items.append(path)
            i += 2 if status[0] in "RC" else 1   # a rename names its source next
        return items

    def add(self, paths: list[str]) -> None:
        if paths:
            self.run("add", "--all", "--", *paths)

    def commit(self, message: str, *, author: Person, committer: Person = ACTIONS_BOT) -> str | None:
        """Commit what is staged. Returns the new commit, or None when nothing was staged."""
        if not self.run("diff", "--cached", "--name-only").strip():
            return None
        env = {**os.environ, **author.env("AUTHOR"), **committer.env("COMMITTER")}
        done = subprocess.run(["git", "commit", "--quiet", "--no-verify", "-F", "-"], cwd=self.root, input=message,
                              capture_output=True, text=True, env=env)
        if done.returncode != 0:
            raise GitError(f"`git commit` failed: {(done.stderr or done.stdout).strip()}")
        return self.head()

    def push(self, branch: str, remote: str = "origin", attempts: int = 3) -> None:
        """Push `branch`, rebasing onto what the remote gained meanwhile and trying again if it moved."""
        for attempt in range(attempts):
            try:
                self.run("push", "--quiet", remote, f"HEAD:refs/heads/{branch}")
                return
            except GitError:
                if attempt == attempts - 1:
                    raise
                self.run("pull", "--quiet", "--rebase", remote, branch)
