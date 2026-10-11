# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What every test shares: `src/` on the import path, git without its background maintenance, and the kit's data
handed to the domain once.

The tests stand where the composition root stands: they may import `infra`
to build what the application is handed, and `install()` reads the outlines
and prints the way a run does.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
LAUNCHER = SRC / "markdown-kit.py"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Since git 2.47 a commit, a fetch or a push leaves `git maintenance run --auto` working on in the background, and
# a test that ends at once can find that process writing into its repository's .git while the temporary directory
# is being removed. No test needs maintenance, so every git a test starts, itself or through the kit, runs without
# it: one more entry in git's environment config, after any the environment already holds.
_entry = int(os.environ.get("GIT_CONFIG_COUNT") or 0)
os.environ.update({"GIT_CONFIG_COUNT": str(_entry + 1), f"GIT_CONFIG_KEY_{_entry}": "maintenance.auto",
                   f"GIT_CONFIG_VALUE_{_entry}": "false"})

_catalogue: dict | None = None


def install() -> dict:
    """Read the kit's outlines and prints into the domain, as a run does first. Returns the prints catalogue."""
    global _catalogue
    from infra import resources

    _catalogue = resources.install()
    return _catalogue


def ports(files: dict | None = None, today=None):
    """A `Ports` over an in-memory repository: `files` maps a path to its text."""
    import datetime as dt

    from app.ports import Ports
    from infra import yaml_reader

    files = {str(Path(k)): v for k, v in (files or {}).items()}
    return Ports(catalogue=install(), read_text=lambda p: files.get(str(Path(p))), parse_yaml=yaml_reader.loads,
                 today=lambda zone: today or dt.date(2026, 9, 28), out=io.StringIO(), err=io.StringIO())
