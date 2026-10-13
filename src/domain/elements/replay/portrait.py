# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A player as a replay draws them: their GitHub avatar as a print draws a portrait, a halftone of dots in its ink.

No image goes into the file, only dots, so a replay keeps the kit's rule that a file fetches and embeds nothing.
The avatar comes as a small grey bitmap, a PGM (`read`), which whoever runs the replay makes from the avatar
GitHub serves: its levels are stretched to fill the range and evened out, then laid on a grid of dots, each dot a
zero-length stroke with a round cap whose width is the tone there, and the dots of one width gathered in one path.
A player with no bitmap is drawn as the Hall of Fame draws a winner with no name to letter: their initials in the
print's dial. The Arbiter is drawn as its own mark, the scales, and a player whose account is gone as an empty
dial in a dashed ring, with no name. Every portrait is defined once in the file and set wherever it stands.
"""
from __future__ import annotations

from ...canvas import c
from ...lettering import f1

REF = 40.0                      # every portrait is defined at this radius and scaled to where it stands
FINE, COARSE = 2.3, 4.2         # the halftone's pitch: the winner's large portrait, and every small one


def read(data: bytes) -> list[list[int]] | None:
    """A PGM's grey levels, row by row, each 0 (black) to 255 (white); None when it is not one."""
    try:
        magic = data[:2]
        if magic not in (b"P5", b"P2"):
            return None
        fields, i = [], 2
        while len(fields) < 3:
            while i < len(data) and data[i:i + 1].isspace():
                i += 1
            if data[i:i + 1] == b"#":
                while i < len(data) and data[i:i + 1] not in (b"\n", b"\r"):
                    i += 1
                continue
            j = i
            while j < len(data) and not data[j:j + 1].isspace():
                j += 1
            fields.append(int(data[i:j]))
            i = j
        w, h, top = fields
        if not (0 < w <= 512 and 0 < h <= 512 and 0 < top < 65536):
            return None
        if magic == b"P5":
            i += 1
            size = 2 if top > 255 else 1
            raw = data[i:i + w * h * size]
            if len(raw) < w * h * size:
                return None
            values = ([int.from_bytes(raw[k:k + 2], "big") for k in range(0, len(raw), 2)] if size == 2
                      else list(raw))
        else:
            values = [int(v) for v in data[i:].split()][:w * h]
            if len(values) < w * h:
                return None
        scale = 255 / top
        return [[round(values[y * w + x] * scale) for x in range(w)] for y in range(h)]
    except (ValueError, IndexError):
        return None


def sample(grid: list[list[int]], n: int) -> list[list[float]]:
    """The grid resampled to n by n, each cell the mean of what it covers, stretched to the full range with the
    darkest and lightest 2% let go, and its levels evened out: a halftone's own preparation."""
    h, w = len(grid), len(grid[0])
    out = []
    for j in range(n):
        y0, y1 = j * h / n, (j + 1) * h / n
        row = []
        for i in range(n):
            x0, x1 = i * w / n, (i + 1) * w / n
            total = area = 0.0
            for y in range(int(y0), min(h, int(y1) + 1)):
                wy = min(y + 1, y1) - max(y, y0)
                if wy <= 0:
                    continue
                for x in range(int(x0), min(w, int(x1) + 1)):
                    wx = min(x + 1, x1) - max(x, x0)
                    if wx > 0:
                        total += grid[y][x] * wx * wy
                        area += wx * wy
            row.append(total / area if area else 255.0)
        out.append(row)
    flat = sorted(v for row in out for v in row)
    lo, hi = flat[int(len(flat) * .02)], flat[min(len(flat) - 1, int(len(flat) * .98))]
    span = max(1.0, hi - lo)
    out = [[min(1.0, max(0.0, (v - lo) / span)) for v in row] for row in out]
    ranks = sorted(v for row in out for v in row)
    index = {}
    for k, v in enumerate(ranks):
        index.setdefault(v, k)
    last = max(1, len(ranks) - 1)
    return [[index[v] / last for v in row] for row in out]


def portrait_def(cv, sk, grid: list[list[int]], key, pitch: float) -> str:
    """The id of a portrait, a disc REF in radius centred on the origin, defined once in the file."""
    cache = cv.__dict__.setdefault("_portraits", {})
    if (key, pitch) in cache:
        return cache[(key, pitch)]
    n = int(2 * REF / pitch)
    tones = sample(grid, n)
    levels: dict[float, list[tuple[float, float]]] = {}
    for j in range(n):
        for i in range(n):
            x, y = -REF + (i + .5) * pitch, -REF + (j + .5) * pitch
            if x * x + y * y > (REF - pitch * .55) ** 2:
                continue
            lum = tones[j][i] ** .9
            tone = lum if sk.dark else 1 - lum
            d = pitch * 1.04 * tone ** .5
            if d < .4:
                continue
            levels.setdefault(round(d / .3) * .3, []).append((x, y))
    pid = cv.uid("v")
    paths = "".join(f'<path d="{"".join(f"M{x:.1f} {y:.1f}h0" for x, y in pts)}" stroke-width="{q:.1f}"/>'
                    for q, pts in sorted(levels.items()))
    cv.defs.append(f'<g id="{pid}"><circle r="{REF:g}" fill="{c(sk.col["paper"])}"/>'
                   f'<g fill="none" stroke="{c(sk.col["ink"])}" stroke-linecap="round">{paths}</g></g>')
    cache[(key, pitch)] = pid
    return pid


def initials(login: str) -> str:
    """Two letters for a player with no portrait: their login's, as the Hall of Fame letters a winner with no name."""
    letters = [ch for ch in login if ch.isalnum()]
    return "".join(letters[:2]).upper() or "?"


def arbiter_def(cv, sk) -> str:
    """The Arbiter's mark where a player's portrait would be: its scales in a dial, defined once."""
    cache = cv.__dict__.setdefault("_arbiter", [])
    if cache:
        return cache[0]
    aid = cv.uid("arb")
    ink = c(sk.col["ink"])
    cv.defs.append(f'<g id="{aid}"><circle r="40" fill="{c(sk.col["paper"])}"/><g transform="scale(3.6)" fill="none" '
                   f'stroke="{ink}" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round">'
                   f'<path d="M0 -6.5V5.5M-4 5.5H4M-6.5 -4.2H6.5M-6.5 -4.2L-9 1.4H-4ZM6.5 -4.2L4 1.4H9Z"/>'
                   f'<circle cy="-7.4" r="1.1" fill="{ink}" stroke="none"/></g></g>')
    cache.append(aid)
    return aid


class Faces:
    """Every player's face in one replay: a portrait from their bitmap, else their initials; the Arbiter's scales;
    and an empty dashed dial for an account that is gone. `grids` are the bitmaps by account ID, and `gone` the IDs
    whose accounts are gone."""

    def __init__(self, cv, sk, grids: dict[int, list[list[int]]], gone: frozenset[int] = frozenset()):
        self.cv, self.sk, self.grids, self.gone = cv, sk, grids, gone

    def label(self, login: str | None, pid: int | None) -> str:
        """How a player is named under their face: the Arbiter, a deleted account, or their login."""
        if login is None:
            return "arbiter"
        return "deleted account" if pid in self.gone else login

    def named(self, login: str | None, pid: int | None) -> str:
        """How a player is named in the panel's lines: THE ARBITER, A DELETED ACCOUNT, or @LOGIN."""
        if login is None:
            return "THE ARBITER"
        return "A DELETED ACCOUNT" if pid in self.gone else f"@{login.upper()}"

    def face(self, login: str | None, pid: int | None, cx: float, cy: float, r: float, *, ring: float = 1.4,
             extra: str = "") -> str:
        cv, sk = self.cv, self.sk
        line = c(sk.col["line"])
        rim = f'<circle r="{f1(r)}" fill="none" stroke="{line}" stroke-width="{ring:g}"/>'
        if login is None:
            return (f'<g transform="translate({f1(cx)} {f1(cy)})">{extra}<use href="#{arbiter_def(cv, sk)}" '
                    f'transform="scale({r / 40:.4f})"/>{rim}</g>')
        if pid in self.gone:
            return (f'<g transform="translate({f1(cx)} {f1(cy)})">{extra}<circle r="{f1(r)}" '
                    f'fill="{c(sk.col["paper"])}" stroke="{line}" stroke-width="{ring:g}" '
                    f'stroke-dasharray="3 2.2"/></g>')
        grid = self.grids.get(pid) if pid is not None else None
        if grid:
            pitch = FINE if r >= 24 else COARSE
            vid = portrait_def(cv, sk, grid, pid, pitch)
            return (f'<g transform="translate({f1(cx)} {f1(cy)})">{extra}<use href="#{vid}" '
                    f'transform="scale({r / REF:.4f})"/>{rim}</g>')
        size = r * .72
        return (f"<g>{extra}" + sk.dial(cx, cy, r)
                + sk.say(cv, initials(login), cx, cy + sk.cap(size) / 2, size, ls=.8, anchor="middle") + "</g>")
