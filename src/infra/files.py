# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Reading and writing the files a run leaves in the repository.

A file is written only when its bytes change, so a run that draws what is
already there leaves the working tree clean and makes no commit. Writes go to
a temporary file beside the target and are moved into place, so a run that
dies halfway never leaves half a file behind.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from domain import KIT


def read_text(path: Path) -> str | None:
    """The file's text, or None when there is no file."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def write_text(path: Path, text: str) -> bool:
    """Write `text` to `path` if it differs from what is there. Returns True when the file changed."""
    path = Path(path)
    if read_text(path) == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return True


def read_json(path: Path):
    """The JSON value in `path`, or None when there is no file."""
    text = read_text(path)
    return None if text is None else json.loads(text)


def dump_json(value) -> str:
    """JSON the way the kit writes it: sorted, one space of indent, UTF-8 left as it is, a newline at the end."""
    return json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, value) -> bool:
    return write_text(path, dump_json(value))


def remove(path: Path) -> bool:
    """Delete `path` if it is there. Returns True when something was deleted."""
    try:
        Path(path).unlink()
        return True
    except FileNotFoundError:
        return False


# The stamps a drawn file opens with: the kit's own, and those of the three kits it replaced, the banners, the
# badges and the trophies kits. A page that moved to this kit may still hold their files, in the very folders it
# draws into now, and a run takes them away with its own once nothing draws them.
STAMPS = (f"<!--{KIT} v", "<!--banner-kit v", "<!--badge-kit v", "<!--trophy-kit v")


def stamped(path: Path) -> bool:
    """Whether the kit, or a kit it replaced, drew this file: a stamp is in the first few hundred bytes."""
    try:
        with Path(path).open("rb") as fh:
            head = fh.read(1024).decode("utf-8", "replace")
    except OSError:
        return False
    return any(stamp in head for stamp in STAMPS)


def drawn(folder: Path, pattern: str = "*.svg") -> list[str]:
    """Every file under `folder` the kit drew, relative to it, in order."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    return [f.relative_to(folder).as_posix() for f in sorted(folder.rglob(pattern)) if stamped(f)]


def append_text(path: Path, text: str) -> None:
    """Add `text` to the end of `path`, which is made if it is missing: the run's summary, a line at a time."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text)


def prune(folder: Path, keep: set[str], pattern: str = "*.svg") -> list[str]:
    """Delete the files under `folder` the kit drew and this run did not, and return their paths. A folder the
    deletions leave empty goes with them, so one the kit drew into before, like `assets/markdown` before each part
    had a folder of its own, is gone once nothing is left in it.

    Only a file with the kit's stamp is ever deleted, so a file someone put
    there by hand is safe whatever it is called, and so is the folder it is in.
    """
    folder = Path(folder)
    gone = []
    if not folder.is_dir():
        return gone
    for f in sorted(folder.rglob(pattern)):
        rel = f.relative_to(folder).as_posix()
        if rel not in keep and stamped(f):
            f.unlink()
            gone.append(rel)
            parent = f.parent
            while parent != folder and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
    return gone
