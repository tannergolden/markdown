# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Everything the application is handed to reach outside itself.

Each field is a plain function or value, so a test can build a `Ports` from
lambdas and a dictionary. The adapters behind the real ones are `infra`'s. An
adapter that fails says so with a `ValueError` (a YAML error, an unknown time
zone), which the command line reports as a setting to fix, or with a
`RuntimeError` for a fault outside the settings (git, the network).
"""
from __future__ import annotations

import datetime as dt
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TextIO


@dataclass
class Ports:
    catalogue: dict                                    # the kit's own prints, already handed to the domain
    read_text: Callable[[Path], str | None]            # a file's text, or None when it is missing
    parse_yaml: Callable[[str], object]                # a YAML document's value
    today: Callable[[str], dt.date]                    # the date in a time zone, by name
    out: TextIO = field(default_factory=lambda: sys.stdout)
    err: TextIO = field(default_factory=lambda: sys.stderr)
