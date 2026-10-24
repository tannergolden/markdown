# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The code the Matrix hand writes in: the rain's glyphs, the code falling down a sheet, and the night's glyph stars.

The code falls in mirrored half-width katakana and mirrored numerals, five
units by seven, as the old terminals' character generators drew them, so a
glyph reads as one of the code's at the size a reader meets it, two pixels a
unit. Every design of the Matrix collection writes in the same glyphs, on its
screens, in its rain and in its night sky, so the twelve read as written in one
hand (see `collections.hand`).

The code falls in streams, each a column of glyphs led down the sheet by a
white-hot head with its trail fading behind it, on the hand's flame ramp by
night, which is the phosphor every light in the collection burns on, and in
the hand's dark inks by day, as a printer would set it. A stream steps down a
glyph at a time, so a glyph is lit or not; streams that fall at one pace share
one motion, the column of them drawn once and laid twice, so the loop never
shows its seam. The still twin holds the rain where its loop begins.

A glyph is drawn once in `<defs>` as a single path and placed with `<use>`,
stroked in its tone, so a column of rain costs a few bytes a glyph.
"""
from __future__ import annotations

import random

from ..holidays.pixel import FONTS, Pix, fold, num

W, H = 5, 7          # a glyph's cell, in units
PITCH = 8            # the rows a stream steps down by: a glyph and the unit between it and the next
COLUMN = 6           # the columns a glyph and its gap take across the rain

# The code's glyphs as the character generators drew them, before the code mirrors them: half-width katakana and
# numerals, `#` for a lit unit. `glyph(name)` is the mirrored one the code falls in.
SHAPES = {
    "a": ["#####", "....#", "..#.#", "..##.", "..#..", "..#..", ".#..."],
    "i": ["....#", "...#.", "..##.", ".#.#.", "...#.", "...#.", "...#."],
    "u": ["..#..", "#####", "#...#", "#...#", "....#", "...#.", "..#.."],
    "o": ["...#.", "#####", "...#.", "..##.", ".#.#.", "#..#.", "...#."],
    "ka": [".#...", "#####", ".#..#", ".#..#", ".#..#", "#...#", "#..#."],
    "ki": ["..#..", "#####", "..#..", "#####", "..#..", "..#..", "..#.."],
    "ku": [".#...", ".####", "#...#", "....#", "...#.", "..#..", ".#..."],
    "ke": [".#...", ".####", "#..#.", "...#.", "...#.", "..#..", ".#..."],
    "sa": [".#.#.", "#####", ".#.#.", "...#.", "...#.", "..#..", ".#..."],
    "shi": [".....", "##...", "....#", "##..#", "....#", "...#.", "###.."],
    "tsu": [".....", "#.#.#", "#.#.#", "....#", "...#.", "..#..", ".#..."],
    "te": [".###.", ".....", "#####", "..#..", "..#..", "..#..", ".#..."],
    "na": ["..#..", "..#..", "#####", "..#..", "..#..", ".#...", "#...."],
    "nu": [".....", "#####", "....#", ".#.#.", "..#..", ".#.#.", "#...."],
    "ne": ["..#..", "#####", "...#.", "..#..", ".###.", "#.#.#", "..#.."],
    "ha": [".....", "..#..", "#..#.", "#..#.", "#...#", "#...#", "#...#"],
    "hi": ["#....", "#....", "####.", "#....", "#....", "#....", ".####"],
    "ho": ["..#..", "#####", "..#..", "#.#.#", "#.#.#", "..#..", "..#.."],
    "ma": [".....", "#####", "....#", "...#.", "#.#..", ".#...", "..#.."],
    "mi": [".###.", ".....", ".###.", ".....", ".###.", "....#", "....."],
    "mu": ["..#..", "..#..", ".#...", ".#...", ".#..#", "#####", "....#"],
    "me": ["....#", "....#", ".#.#.", "..#..", ".#.#.", "#....", "....."],
    "mo": [".....", "#####", "..#..", "#####", "..#..", "..#..", "..###"],
    "ya": [".#...", ".#...", "#####", ".#..#", ".#.#.", ".#...", ".#..."],
    "yu": [".....", ".....", ".###.", "...#.", "...#.", "#####", "....."],
    "ra": [".###.", ".....", "#####", "....#", "....#", "...#.", ".##.."],
    "ri": ["#...#", "#...#", "#...#", "#...#", "....#", "...#.", "..#.."],
    "wa": [".....", "#####", "#...#", "....#", "...#.", "..#..", ".#..."],
    "n": [".....", "#....", ".#..#", "....#", "...#.", "..#..", "##..."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    "z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
}
NAMES = tuple(SHAPES)


def glyph(name: str) -> list[str]:
    """A glyph as the code falls in it: its shape mirrored, rows of `#` for lit units."""
    return [row[::-1] for row in SHAPES[name]]


def cells(name: str) -> set:
    """The lit units of a glyph, as (x, y) from its top-left."""
    return {(x, y) for y, row in enumerate(glyph(name)) for x, ch in enumerate(row) if ch == "#"}


def symbol(p: Pix, name: str) -> tuple:
    """The key of a glyph drawn once in `p`'s <defs> as one path with no colour of its own, which takes the stroke
    of the group it is placed in."""
    key = ("code", name)
    if key not in p.syms:
        p.symbol(key, {xy: 1 for xy in cells(name)}, mono=True)
    return key


def write(p: Pix, x, y, name: str, c: str, L: str = "base"):
    """One glyph with its top-left at (x, y), in colour `c`."""
    p.use(symbol(p, name), x, y, L, stroke=c)


def tones(ramp: list, night: bool, length: int, dim: bool = False) -> list:
    """A stream's tones, head first: by night white-hot at its head and fading down the phosphor behind it; by
    day the darkest at its head, paling toward the paper behind it, as a printer's ribbon runs dry. A `dim` stream,
    one that falls behind a title, has no white head and fades from the middle of the ramp: by night down into the
    dark, by day up into the paper."""
    if dim and night:
        lead, fade = [ramp[3], ramp[2], ramp[2]], [ramp[1]] * 3 + [ramp[0]] * 6
    elif dim:
        lead, fade = [ramp[5], ramp[5]], [ramp[6]] * 9
    elif night:
        lead = [ramp[6], ramp[5], ramp[4], ramp[3], ramp[3]]
        fade = [ramp[2]] * 3 + [ramp[1]] * 3 + [ramp[0]] * 4
    else:
        lead = [ramp[0], ramp[0], ramp[1], ramp[1]]
        fade = [ramp[2]] * 4 + [ramp[3]] * 6
    out = (lead + fade)[:length]
    return out + [out[-1]] * (length - len(out))


def strands(p: Pix, ramp: list, night: bool, n: int = 8, lengths=(4, 13), seed: int = 11, dim: bool = False) -> list:
    """The streams the code falls in, drawn once a file in <defs>: `n` columns of glyphs from the shortest of
    `lengths` to the longest, each with its head at its origin and its trail going up, in its tones (`dim` for the
    streams that fall behind a title, see `tones`). Every stream down a sheet is one of these placed, so a sheet of
    rain costs a few bytes a stream. Returns [(id, length)]."""
    key = ("strands", ramp[0], night, n, lengths, dim)
    if key in p.syms:
        return p.syms[key]
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        length = lengths[0] + (lengths[1] - lengths[0]) * i // max(1, n - 1)
        by: dict = {}
        for j, c in enumerate(tones(ramp, night, length, dim)):
            by.setdefault(c, []).append((-j * PITCH, p.syms[symbol(p, rnd.choice(NAMES))]))
        inner = "".join(f'<g stroke="{c}">' + "".join(f'<use href="#{sid}"' + (f' y="{y}"' if y else "") + "/>"
                                                     for y, sid in items) + "</g>" for c, items in by.items())
        sid = f"st{sum(1 for d in p.defs if d.startswith('<g id=\"st'))}"
        p.defs.append(f'<g id="{sid}">{inner}</g>')
        out.append((sid, length))
    p.syms[key] = out
    return out


class Rain:
    """The code falling down a box of a sheet, built stream by stream and written once as raw markup with its
    still twin (see `fall`)."""

    def __init__(self, p: Pix, box: tuple, ramp: list, night: bool, seed: int = 1, kinds: int = 8, lengths=(4, 13),
                 dim: bool = False):
        self.p, self.box, self.ramp, self.night = p, box, ramp, night
        self.rnd = random.Random(seed)
        self.kinds = strands(p, ramp, night, kinds, lengths, dim=dim)
        self.groups: dict = {}     # pace: [(x, head row, strand id, length)]
        self.n = sum(1 for d in p.defs if d.startswith('<clipPath id="rc'))

    def stream(self, x, head_y, pace=0.12, kind=None):
        """A stream down column `x` with its head at row `head_y`, stepping down a glyph every `pace` seconds: one
        of the file's strands, at random unless `kind` names its index."""
        sid, length = self.kinds[self.rnd.randrange(len(self.kinds)) if kind is None else kind]
        self.groups.setdefault(pace, []).append((x, head_y, sid, length))

    def field(self, density=0.7, paces=(0.09, 0.13, 0.18), skip=()):
        """Streams across the whole box, a column every `COLUMN` units, each column taken at the rate `density`, its
        strand and pace at random. A column whose x falls inside a span of `skip` is left dry."""
        x0, y0, x1, y1 = self.box
        for x in range(x0, x1 - W + 1, COLUMN):
            if self.rnd.random() > density or any(a <= x < b for a, b in skip):
                continue
            self.stream(x, y0 + self.rnd.randrange((y1 - y0) // PITCH + 13) * PITCH, pace=self.rnd.choice(paces))

    def fall(self, z: float = -8):
        """Write the rain into the drawing: by pace, each group of streams drawn once in <defs> and placed twice, one
        loop's height apart, stepping down a glyph at a time and round again; held where it begins in the still
        twin. Everything is clipped to the box."""
        p = self.p
        if not self.groups:
            return
        x0, y0, x1, y1 = self.box
        cid = f"rc{self.n}"
        p.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>')
        moving, still = [], []
        for k, (pace, streams) in enumerate(sorted(self.groups.items())):
            longest = max(length for *_, length in streams)
            loop = -(-(y1 - y0 + longest * PITCH) // PITCH) * PITCH     # one loop's height, whole glyphs
            inner = "".join(f'<use href="#{sid}" x="{x}" y="{y0 + (head - y0) % loop}"/>'
                            for x, head, sid, _ in streams)
            gid = f"{cid}s{k}"
            p.defs.append(f'<g id="{gid}">{inner}</g>')
            steps = loop // PITCH
            values = ";".join(f"0 {i * PITCH}" for i in range(steps))
            moving.append(f'<g><use href="#{gid}"/><use href="#{gid}" y="-{loop}"/><animateTransform '
                          f'attributeName="transform" type="translate" values="{values}" dur="{num(steps * pace)}s" '
                          f'repeatCount="indefinite" calcMode="discrete"/></g>')
            still.append(f'<use href="#{gid}"/><use href="#{gid}" y="-{loop}"/>')
        p.raw(z, f'<g clip-path="url(#{cid})">{"".join(moving)}</g>',
              f'<g clip-path="url(#{cid})">{"".join(still)}</g>')


def stars(p: Pix, x0, y0, x1, y1, n, ramp: list, seed=3, twinkling=True, faint=False, avoid=(), dim=None):
    """The night's stars as the code shows through the sky: most a single unit of dim phosphor, some brighter
    and twinkling, and now and then a whole glyph, faint. None inside a box in `avoid`."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a - 1 <= x < c + 1 and b - 1 <= y < d + 1 for a, b, c, d in avoid):
            continue
        if k < 0.55 or faint:
            p.px(x, y, dim or ramp[1], "haze")
        elif k < 0.92:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.6) else "haze"
            p.px(x, y, ramp[4] if rnd.random() < 0.6 else ramp[5], L)
        elif not any(a - 2 <= x + W and x - 2 <= c and b - 2 <= y + H and y - 2 <= d for a, b, c, d in avoid) \
                and x + W < x1 and y + H < y1:
            write(p, x, y, rnd.choice(NAMES), ramp[1], "haze")


def scan(p: Pix, x, y, s, scale, w, n, period: float, white: str):
    """The hand's glint on a title: a scan line a letter's unit tall that steps down the title's letters from their
    top to their foot in the first tenth of every `period` seconds, as a terminal's beam refreshes it, and rests out
    of sight below them the rest of the time, laid on the letters alone through a mask of their glyphs. The still
    twin has none."""
    glyphs, _, space = FONTS["57"]
    uses, cx = [], 0
    for ch in fold(s, "57"):
        if ch == " ":
            cx += space + 1
            continue
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        uses.append(f'<use href="#{p.syms[key]}"' + (f' x="{cx}"' if cx else "") + "/>")
        cx += glyphs[ch][0] + 1
    tall = 7 * scale
    mid = f"sc{n}"
    p.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x - 1}" y="{y - 1}" width="{w + 2}" '
                  f'height="{tall + 2}"><g stroke="{white}" transform="translate({x} {y}) scale({scale})">'
                  f'{"".join(uses)}</g></mask>')
    k = 8
    values = ";".join(f"0 {round(i * (tall + scale) / k)}" for i in range(k + 1))
    times = ";".join(num(i * 0.1 / k) for i in range(k)) + ";.1"
    p.raw(0.5, f'<g mask="url(#{mid})"><rect x="{x}" y="{y - scale}" width="{w}" height="{scale}" fill="{white}" '
               f'fill-opacity=".5"><animateTransform attributeName="transform" type="translate" values="{values}" '
               f'keyTimes="{times}" dur="{num(period)}s" repeatCount="indefinite" calcMode="discrete"/></rect></g>', "")
