# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The README's blocks: what the kit owns between `<!-- markdown:NAME:start -->` and its end marker.

The kit owns only what sits between its markers. Every run rewrites what is
between them and nothing else, so the README's own sections are never
touched. A block that is no longer wanted is taken out again, markers and all.

On the first run a block goes where a README carries it: the header at the top
(under the front matter, when the file opens with it), the badges under the
header, the trophies over the footer, and the footer at the foot. An element
goes only where its markers already stand, because only the README's author
knows which section it belongs in.

The three kits this one replaced wrote their own markers:
`<!-- banners:header:start -->`, `<!-- banners:footer:start -->`,
`<!-- trophies:start -->` and `<!-- elements:NAME:start -->`, each with its end.
A block still written that way is found and rewritten in the new markers, so a
README moves over on its first run with nothing done by hand.
"""
from __future__ import annotations

import re

PREFIX = "markdown"
# Where each block goes on a first run, top to bottom. An element is placed by hand.
PLACED = ("header", "badges", "trophies", "footer")
LEGACY = {
    "header": ("<!-- banners:header:start -->", "<!-- banners:header:end -->"),
    "footer": ("<!-- banners:footer:start -->", "<!-- banners:footer:end -->"),
    "trophies": ("<!-- trophies:start -->", "<!-- trophies:end -->"),
}
_NAME = re.compile(r"[a-z][a-z0-9-]*(?::[a-z0-9][a-z0-9-]*)?")
# A comment that opens the file: front matter, which stays first.
_FRONT = re.compile(r"\A\s*<!--.*?-->[ \t]*\n", re.S)


class ReadmeError(ValueError):
    pass


def markers(name: str) -> tuple[str, str]:
    if not _NAME.fullmatch(name):
        raise ReadmeError(f"{name!r} is not a block name (lowercase words, and `element:NAME` for an element)")
    return f"<!-- {PREFIX}:{name}:start -->", f"<!-- {PREFIX}:{name}:end -->"


def legacy(name: str) -> tuple[str, str] | None:
    """The markers the kit before this one wrote for a block, or None."""
    if name in LEGACY:
        return LEGACY[name]
    if name.startswith("element:"):
        key = name.split(":", 1)[1]
        return f"<!-- elements:{key}:start -->", f"<!-- elements:{key}:end -->"
    return None


def block(name: str, snippet: str) -> str:
    """`snippet` between the block's markers, one line each."""
    start, end = markers(name)
    return f"{start}\n{snippet.strip(chr(10))}\n{end}"


def find(text: str, name: str) -> tuple[int, int] | None:
    """Where the block stands in `text`, markers included, in either marking, or None."""
    for pair in (markers(name), legacy(name)):
        if not pair:
            continue
        start, end = pair
        a = text.find(start)
        if a < 0:
            continue
        b = text.find(end, a + len(start))
        if b < 0:
            raise ReadmeError(f"{start} has no {end} after it")
        return a, b + len(end)
    return None


def current(text: str, name: str) -> str | None:
    """The block as it stands in `text`, markers included, or None."""
    at = find(text, name)
    return text[at[0]:at[1]] if at else None


def _remove(text: str, a: int, b: int) -> str:
    """`text` without text[a:b], and without the blank lines it would leave behind."""
    before, after = text[:a], text[b:]
    after = after[1:] if after.startswith("\n") else after
    if not after.strip():
        return before.rstrip("\n") + "\n" if before.strip() else ""
    if before.endswith("\n\n") and after.startswith("\n"):
        after = after.lstrip("\n")
    return before + after


def _insert(text: str, name: str, wanted: str) -> str | None:
    """`text` with a new block placed where a README carries it, or None for a block placed by hand.

    The header goes at the top and the badges under it; the footer goes at the
    foot and the trophies over it.
    """
    if name not in PLACED:
        return None
    if name == "badges" and (at := find(text, "header")):
        return text[:at[1]] + "\n\n" + wanted + text[at[1]:]
    if name == "trophies" and (at := find(text, "footer")):
        return text[:at[0]] + wanted + "\n\n" + text[at[0]:]
    if name in ("header", "badges"):
        front = _FRONT.match(text)
        head, rest = (text[:front.end()], text[front.end():]) if front else ("", text)
        rest = rest.lstrip("\n")
        return head + ("\n" if head else "") + wanted + ("\n\n" + rest if rest.strip() else "\n")
    body = text.rstrip("\n")
    return body + ("\n\n" if body.strip() else "") + wanted + "\n"


def place(text: str, blocks: dict[str, str | None]) -> tuple[str, list[str]]:
    """`text` with each block written in place, placed on a first run, or taken out when it is None.

    `blocks` maps a block's name to the whole block, markers included (see
    `block`), or to None to take it out; a block not named is left alone.
    Returns the new text and the names of the blocks that were wanted but have
    no place: an element whose markers the README does not have yet.
    """
    unplaced = []
    for name in sorted(blocks, key=lambda n: PLACED.index(n) if n in PLACED else len(PLACED)):
        wanted = blocks[name]
        at = find(text, name)
        if at and wanted is not None:
            text = text[:at[0]] + wanted + text[at[1]:]
        elif at:
            text = _remove(text, *at)
        elif wanted is not None:
            placed = _insert(text, name, wanted)
            if placed is None:
                unplaced.append(name)
            else:
                text = placed
    return text, unplaced
