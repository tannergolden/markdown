# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The infrastructure: every way the kit touches the world outside its own memory.

Files, git, GitHub's API, the clock and the kit's own data files. Each module
is an adapter the application is handed, never one it reaches for: only the
composition root, `src/markdown-kit.py`, imports anything from here, and a test
can hand the application a fake in its place.
"""
