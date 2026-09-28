# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The application: the command line and what each command does, start to finish.

It orchestrates the domain and reaches outside only through the `Ports` it is
handed (see `ports.py`); it never imports `infra`. The composition root,
`src/markdown-kit.py`, builds the real ports, and a test builds its own.
"""
