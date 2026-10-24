# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Run test modules side by side, one interpreter to a module, as `unittest discover` would run each folder's in one.

WHY THIS EXISTS. The unit suite draws every design in every header for every
content, by day and by night, and on one core it takes longer than the shared
CI job allows, whose fifteen minutes hold the linter, every suite and the build
together. Its modules share nothing while they run, so they run side by side,
as many at a time as the machine has cores (`TEST_JOBS` sets another number),
the largest first. Every folder named joins the one pool, so no suite waits for
another while cores stand idle. Each module runs exactly as discovery runs it:
from the repository's root, as `tests.unit.test_name`, or, in a folder no import
can name, as the repository's scripts' tests in `.github/scripts` are, by
discovery from that folder alone.

Every module's result is printed as it finishes, and a module that fails or
errs prints its whole report. The total comes last, and the exit status is
unittest's: 0 only when every module passed.

    python3 tests/parallel.py tests/unit 'test_*.py' [.github/scripts 'test_*.py' ...]
"""
from __future__ import annotations

import concurrent.futures
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAN = re.compile(r"^Ran (\d+) tests? in", re.M)


def modules(start: str, pattern: str) -> list[tuple[int, str, list[str]]]:
    """The test modules under `start` matching `pattern`, as (size, name, the command that runs it): in a package, by
    its dotted name from the root; in a folder no import can name, by discovery from that folder, as `make
    test-scripts` runs it. A module's size is the best guess of how long it runs."""
    named = all(part.isidentifier() for part in Path(start).parts)
    out = []
    for p in (ROOT / start).glob(pattern):
        if named:
            name = ".".join(p.relative_to(ROOT).with_suffix("").parts)
            out.append((p.stat().st_size, name, [sys.executable, "-m", "unittest", name]))
        else:
            out.append((p.stat().st_size, f"{start}/{p.name}",
                        [sys.executable, "-m", "unittest", "discover", "-s", start, "-p", p.name]))
    return out


def run(module: str, command: list[str]) -> tuple[str, int, int, float, str]:
    """One module run by unittest in its own interpreter: (module, exit status, tests run, seconds, report)."""
    began = time.monotonic()
    done = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    report = done.stdout + done.stderr
    ran = RAN.search(report)
    return module, done.returncode, int(ran.group(1)) if ran else 0, time.monotonic() - began, report


def main(argv: list[str]) -> int:
    pairs = argv[1:]
    if not pairs or len(pairs) % 2:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    found = []
    for start, pattern in zip(pairs[::2], pairs[1::2]):
        these = modules(start, pattern)
        if not these:
            print(f"no test modules match {pattern} under {start}", file=sys.stderr)
            return 1
        found += these
    # The longest first packs the cores best.
    found.sort(key=lambda m: (-m[0], m[1]))
    jobs = max(1, int(os.environ.get("TEST_JOBS") or os.cpu_count() or 1))
    began, failed, total = time.monotonic(), [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        for done in concurrent.futures.as_completed([pool.submit(run, name, command) for _, name, command in found]):
            module, status, ran, seconds, report = done.result()
            total += ran
            # A module with no tests passes, as it does under discovery; unittest from 3.12 says so with status 5.
            if status == 0 or (status == 5 and not ran):
                print(f"ok      {module}: {ran} tests in {seconds:.1f}s", flush=True)
            else:
                failed.append(module)
                print(f"FAILED  {module}: exit {status}, {ran} tests in {seconds:.1f}s\n{report}", flush=True)
    print(f"\nRan {total} tests in {len(found)} modules in {time.monotonic() - began:.1f}s, {jobs} at a time")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
