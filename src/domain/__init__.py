# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The domain: what a README page is drawn from and how, with no I/O at all.

Everything in here is pure. It reads no file, calls no network and runs no
process: the glyph outlines and the print catalogue it draws with are loaded
by `infra.resources` and handed in (`lettering.use`, `prints.use`), so a test
can hand in its own and a drawing is the same bytes wherever it is made.

Nothing here imports anything outside this package and the standard library.
`tests/unit/test_layering.py` holds every module to that.
"""

# Bumped whenever the files a run draws change for the same input. Every SVG
# is stamped with it, so a check can tell a file this version drew from one an
# older version left behind.
KIT_VERSION = "1"
KIT = "markdown-kit"
