#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""markdown-kit: the composition root.

The one place that knows both the application and the infrastructure. It reads
the kit's data into the domain, builds the adapters the application is handed,
and runs the command line. Standard library only: run it with any `python3`
from 3.10 on, with nothing installed.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import cli  # noqa: E402
from app.ports import Ports  # noqa: E402
from infra import clock, files, resources, yaml_reader  # noqa: E402


def ports() -> Ports:
    return Ports(catalogue=resources.install(), read_text=files.read_text, parse_yaml=yaml_reader.loads,
                 today=clock.today)


def main(argv: list[str] | None = None) -> int:
    return cli.main(sys.argv[1:] if argv is None else argv, ports())


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Whatever read the output stopped early, like `| head`: not a failure of the kit's.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
