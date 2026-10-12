# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The trophy case every pixel set draws: a page's trophies, in the set's pixels.

A set restyles the case the way it restyles a badge, and never changes what
it is. Each card keeps its style, a cup, a crest, a medallion, a crystal or a
plaque; its size in the README, so a row never moves when a set comes or
goes; its words, its alt text and its files. What changes is its world: it
stands on the set's own paper inside the set's own frame, by night under the
set's own sky, its words are lettered in the set's two faces and its inks, its
plates are the set's tags and its enamels the nearest of the set's colours,
and the trophy itself is struck in pixels, shaded on the engine's ramps and
lit by its one lamp, up and to the left.

  a tier       the metal it is struck in: the case's bronze, silver, gold,
               platinum and diamond, each a seven-tone ramp on the engine's
               light, so gold is gold in every set, and diamond a prism from
               violet in its shadows to ice in its lights. Unranked is a ghost:
               the trophy's place washed faintly, its outline dashed round it.
               Gold glints; platinum gains its ornament and its sparkles,
               diamond its prism and its stars, as the standard look does
  progress     a bar along the card's foot, filled as far as the next tier
  the frame    a file keeps a unit clear of the set's frame, and its words
               two, told how deep the frame reaches (`trophy_frame`); the
               trophy grows to fill the room left inside it
  the hand     a collection's design letters every word in its hand's two
               inks on its own ground, so its trophies keep the hand too

The metals are the case's own colours: a set's trophy files keep to its closed
palette and the five metals beside it (`trophy_tokens`). A set can strike its
trophies in metals of its own (`trophy_metals`), stand them on another ground
(`trophy_ground`) and engrave its tiers on another plate (`trophy_plate`).

A card's motion is its own, in CSS rather than the engine's SMIL, so it holds
still for a reader who asks for reduced motion even though a trophy has no
still file: a glint passes across a gold trophy's metal, in the engine's
discrete steps and never across a word, and a platinum one's sparkles twinkle
on the engine's cadence. A collection's design glints on its hand's period.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ... import KIT, KIT_VERSION
from ...canvas import BUDGET
from ...trophies.art import (alt_text, case_title, fmt, level_label, level_stats, level_xp, next_up_items,
                             next_up_label, pct_label, pin_caption, pin_label, status_text, top_pct)
from ...trophies.catalogue import TIER_NAMES, ach_state, measure
from ..pixel import GLYPHS, LX, LY, LZ, MISSING, Pix, clip, contrast, fold, make_ramp, measure as tw, tube
from .badges import nearest

# The case's metals, one seven-tone ramp for each tier on the engine's light, dark to light: bronze, a red copper
# whose lights stay peach where gold's turn to straw; silver; gold; platinum, a cool steel; and diamond, a prism
# from violet in its shadows to ice in its lights. Diamond catches the light in two more, its prism's own.
METALS = {
    1: ["#3B1308", "#5E2210", "#8A3C1C", "#B5622F", "#D98C55", "#F0B98A", "#FCE2C8"],
    2: make_ramp("#A8B3C0"),
    3: make_ramp("#E3A62A"),
    4: ["#1E2B45", "#33496E", "#557399", "#87A8CC", "#B9D4EE", "#E1EEFB", "#FFFFFF"],
    5: ["#1B1150", "#33228A", "#5A44C8", "#7C78F0", "#7FC8FF", "#BDF0FF", "#FFFFFF"],
}
PRISM = (make_ramp("#B697FF"), make_ramp("#F496D4"))
METAL_TOKENS = frozenset(c.upper() for ramp in (*METALS.values(), *PRISM) for c in ramp)

# The case's own icons in pixels, beside the badges' 64: a pull request, an issue, a question for a secret, and
# its check, a tick in a ring, with the kit's check as its tick.
OWN = {
    "pull": ["##..#..", "##.####", ".#..#.#", ".#....#", ".#....#", "##...##", "##...##"],
    "issue": ["..###..", ".#...#.", "#.....#", "#..#..#", "#.....#", ".#...#.", "..###.."],
    "q": GLYPHS[7]["question"],
    "tick": GLYPHS[7]["check"],
    "check": GLYPHS[7]["check-circle"],
}

DIAMOND = ["..#..", ".###.", "#####", ".###.", "..#.."]
STAR = ["..#..", ".###.", "#####", ".#.#.", "#...#"]
SMALL_STAR = ["..#..", "#####", ".###.", ".#.#."]
FLARE = ["..#..", "..#..", "##.##", "..#..", "..#.."]
UP = [".#.", "###"]
CROWN = ["#...#...#", "##.###.##", "#########", ".#######."]
SHARD = [".#.", "###", "###", "##.", ".#."]

CARD, PIN, LEVEL, NEXT, PLAQUE = (82, 111), (52, 62), (210, 76), (164, 76), (132, 44)
TAG = 9     # a tag's height, as every set draws one, its letters two rows in and four along
# The rows each card's drawing is at its best in, at its smallest: below them a card's foot closes up a row a gap.
WANTED = {"trophy": 53, "crest": 51, "medallion": 50, "crystal": 50}


@dataclass(frozen=True)
class Room:
    """Where a file's drawing goes: inside the set's frame and a unit clear of it, out of the squares its corner
    pieces take, and its words a unit further in still."""

    x0: int
    y0: int
    x1: int          # the first column past the room
    y1: int          # the first row past the room
    corner: int      # the side of the square at each corner the room leaves to the frame
    w: int
    h: int

    @property
    def foot(self) -> int:
        """The last row a word may take."""
        return self.y1 - 2

    def span(self, y: int, rows: int) -> tuple[int, int]:
        """The columns, from and past, that `rows` rows from row `y` may take: the room's, narrower where they
        reach into the corner squares."""
        if y < self.corner or y + rows > self.h - self.corner:
            return max(self.x0, self.corner), min(self.x1, self.w - self.corner)
        return self.x0, self.x1


def glyph(name: str) -> list:
    """A case's icon as seven by seven pixels: the badges' own, or the case's."""
    return OWN.get(name) or GLYPHS[7].get(name) or GLYPHS[7]["star"]


def lit(nx: float, ny: float) -> float:
    """How much of the lamp a surface facing (nx, ny) in the picture's plane catches, from -1 to 1."""
    return nx * LX + ny * LY


def tone(v: float, x: int, y: int, lo: int = 1, hi: int = 6) -> int:
    """A value on a ramp, rounded, with a checkerboard where two tones meet, as the engine shades."""
    b = math.floor(v)
    f = v - b
    if f >= .62 or (f > .38 and (x + y) % 2 == 0):
        b += 1
    return max(lo, min(hi, b))


def outline(p: Pix, cells, ramp: list, cx: float, cy: float, L: str = "base"):
    """A selective outline round `cells`: the ramp's darkest tone on the side the lamp does not reach, and a
    tone lighter where it does, outside the shape, as the engine outlines a sprite."""
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cells or p.get(*q, L) in ramp[:2]:
                continue
            far = (q[0] + .5 - cx) * LX + (q[1] + .5 - cy) * LY < 0
            p.px(q[0], q[1], ramp[0] if far else ramp[1], L)


def ring_of(cells) -> set:
    """The pixels round `cells`, just outside them: where an outline is drawn."""
    out = set()
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in cells:
                out.add((x + dx, y + dy))
    return out


def walk(ring) -> list[list]:
    """The pixels of `ring` in order round it, as a pen would draw them: from its top-left pixel, each step to the
    neighbour that turns least from the way it was going. A ring that branches comes back as several walks."""
    order = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
    left, walks = set(ring), []
    while left:
        cur = min(left, key=lambda q: (q[1], q[0]))
        left.discard(cur)
        path, d = [cur], 0
        while True:
            for turn in (0, 1, -1, 2, -2, 3, -3):
                k = (d + turn) % 8
                q = (cur[0] + order[k][0], cur[1] + order[k][1])
                if q in left:
                    break
            else:
                break
            left.discard(q)
            path.append(q)
            cur, d = q, k
        walks.append(path)
    return walks


def ghost(p: Pix, cells, colour: str, wash: float = .12):
    """An unranked trophy's place: washed faintly in `colour`, its outline dashed round it two pixels on and two
    off, traced along its edge so a curve or a stem is dashed as evenly as a straight."""
    if wash:
        for (x, y) in cells:
            p.apx(x, y, colour, wash, L="base")
    for path in walk(ring_of(cells)):
        if len(path) > 2:
            for i, (x, y) in enumerate(path):
                if i % 4 < 2:
                    p.px(x, y, colour)


def lines_of(name: str, room: int) -> list[tuple[str, int]]:
    """A name set in the small capitals on at most two lines of `room`, as (line, tracking): broken at its spaces
    and hyphens, a word too wide for a line set tighter, a lone word too wide even so broken across both lines
    with a hyphen, and cut only if even that cannot fit it."""
    words, out, cur = fold(name.upper(), "35").replace("-", "- ").split(), [], ""
    if len(words) == 1 and tw(words[0], "35", 1, 0) > room:
        w = words[0]
        cut = max((i for i in range(2, len(w) - 1) if tw(w[:i] + "-", "35") <= room), default=0)
        if cut and tw(w[cut:], "35") <= room:
            return [(w[:cut] + "-", 1), (w[cut:], 1)]
    for w in words:
        joined = (cur + ("" if cur.endswith("-") else " ") + w) if cur else w
        if tw(joined, "35") <= room:
            cur = joined
            continue
        if cur:
            out.append(cur)
        cur = w
    if cur:
        out.append(cur)
    if len(out) > 2:
        out = [out[0], " ".join(out[1:]).replace("- ", "-")]
    done = []
    for line in out:
        if tw(line, "35") <= room:
            done.append((line, 1))
        elif tw(line, "35", 1, 0) <= room:
            done.append((line, 0))
        else:
            done.append((clip(line, room, "35", 1, 0), 0))
    return done


def hex_in(x: float, y: float, cx: float, cy: float, r: float) -> bool:
    """Whether the point lies inside a pointy-topped hexagon of circumradius `r`."""
    dx, dy = abs(x - cx), abs(y - cy)
    return dx <= r * .866 and dy <= r - dx * .57735


def disc(cx: float, cy: float, r: float) -> set:
    """The pixels of a disc."""
    return {(x, y) for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1)
            for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1) if math.hypot(x + .5 - cx, y + .5 - cy) <= r}


def centred(p: Pix, cx: float, y: int, s: str, colour: str, font: str = "35", scale: int = 1) -> int:
    """A line of letters centred on `cx`. Returns its width."""
    w = tw(s, font, scale)
    return p.text(round(cx - w / 2), y, s, colour, font, scale)


def sparkle(cells: dict, x: int, y: int, ramp: list, big: bool = True):
    """A sparkle's pixels, its middle the ramp's lightest tone."""
    art = FLARE if big else [".#.", "#.#", ".#."]
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch == "#":
                cells[(x + i, y + j)] = ramp[5]
    cells[(x + len(art) // 2, y + len(art) // 2)] = ramp[6]


class Motion:
    """A card's own motion, in CSS so a reader's reduced motion holds it still: the glints and the sparkles."""

    def __init__(self, glint: float):
        self.period = glint
        self.used: set = set()

    def css(self) -> str:
        out = ""
        if "tw" in self.used:
            out += ("@keyframes tw{0%{opacity:1}50%{opacity:.28}}"
                    ".tw{animation:tw 1.5s steps(1,end) infinite}")
        if "gl" in self.used:
            out += ("@keyframes gl{0%{transform:translateX(-36px)}20%,100%{transform:translateX(64px)}}"
                    f".gl{{animation:gl {self.period:g}s steps(25,end) infinite}}")
        if out:
            out += "@media (prefers-reduced-motion:reduce){.tw{animation:none}.gl{animation:none;display:none}}"
        return out


class Trophies:
    """The trophy case's layouts. Every drawing hook a set overrides is listed first, with its default."""

    # ------------------------------------------------------------------------------------------ hooks
    # How deep the set's frame reaches into a trophy file, in units: its top, its sides and its foot, and the side
    # of the square its corner pieces take. A holiday's set has a frame four units deep all round; a design with a
    # deeper one says so, and its files keep a unit clear of it and their words two (see `_room`).
    trophy_frame = (4, 4, 4, 4)

    def trophy_metals(self) -> dict:
        """The ramps a trophy is struck in, by tier, 1 for bronze to 5 for diamond."""
        return METALS

    def trophy_ground(self, p: Pix, night: bool):
        """What a card stands on: the set's paper, by night its sky with a few faint stars, inside its frame."""
        self.paper(p, night, uid="tg")
        if night:
            top, side, foot, _ = self.trophy_frame
            self.stars(p, side + 3, top + 3, p.w - side - 3, p.h - foot - 3, max(4, p.w * p.h // 900), seed=7,
                       twinkling=False, faint=True)
        self.frame(p, night)

    def trophy_plate(self, p: Pix, x: int, y: int, w: int, h: int, night: bool):
        """The plate a tier is engraved on: the set's tag."""
        self.tag(p, x, y, w, h, night)

    def trophy_enamel(self, hue: str) -> tuple:
        """The enamel a trophy's colour takes in the set, and the ink its icon is cut in: the nearest of the set's
        badge colours."""
        swatches = self.badge_swatches()
        block, ink, _ = swatches[nearest(hue, swatches)]
        return block, ink

    @property
    def trophy_tokens(self) -> frozenset:
        """Every colour a trophy file of the set may paint: the set's closed palette, and the case's metals."""
        return frozenset(self.tokens) | METAL_TOKENS

    # ------------------------------------------------------------------------------------- the canvas
    def _glint_period(self) -> float:
        hand = getattr(self, "hand", None) if getattr(self, "collection", "") else None
        return hand.glint if hand else 6.5

    def _trophy_file(self, draw, label: str, night: bool) -> str | None:
        """A trophy file from `draw(p, motion)`, its motion in CSS, or None when the set cannot letter it."""
        def once() -> str | None:
            MISSING.clear()
            motion = Motion(self._glint_period())
            p = draw(motion)
            if MISSING:
                MISSING.clear()
                return None
            self._finish(p, night)
            svg = p.svg(label, "", still=True, stamp=f"{KIT} v{KIT_VERSION} trophy {self.key} "
                        f"{'night' if night else 'day'}")
            css = motion.css()
            if css:
                head, sep, tail = svg.partition("</title>")
                svg = head + sep + f"<style>{css}</style>" + tail
            return svg
        svg = once()
        if svg is None or len(svg.encode("utf-8")) <= BUDGET["trophy"]:
            return svg
        self._lite = True
        try:
            return once()
        finally:
            self._lite = False

    def _card_canvas(self, size: tuple, night: bool) -> Pix:
        p = self.canvas(*size)
        self.trophy_ground(p, night)
        p.ground = set(p.layers["base"].values())   # the colours a glow may lie on
        return p

    def _trophy_room(self, p: Pix) -> Room:
        """The room a file's drawing has: a unit clear of the set's frame all round, and of its corner pieces."""
        top, side, foot, corner = self.trophy_frame
        return Room(side + 1, top + 1, p.w - side - 1, p.h - foot - 1, corner + 1, p.w, p.h)

    def _tint(self, t: int, night: bool) -> str:
        """The colour a tier's metal marks a bar, a pip or a ring in: its middle tone by day, a lighter by night."""
        return self.trophy_metals()[t][4 if night else 3]

    def _shine(self, p: Pix, cx: float, cy: float, r: float, ramp: list, t: int, night: bool):
        """The light a trophy throws round itself, as a lamp's halo: stepped, strongest at its middle, by night
        from bronze and by day from gold, laid on the ground inside the frame only, so it never tints the trophy, a
        word or the frame."""
        if not t or (not night and t < 3):
            return
        alphas = (.05, .09, .14) if night else (.04, .07, .1)
        room = self._trophy_room(p)
        ground, base = getattr(p, "ground", None) or set(), p.layers["base"]
        for y in range(max(room.y0, math.floor(cy - r)), min(room.y1, math.ceil(cy + r) + 1)):
            x0, x1 = room.span(y, 1)
            for x in range(max(x0, math.floor(cx - r)), min(x1, math.ceil(cx + r) + 1)):
                d = math.hypot((x + .5 - cx) / r, (y + .5 - cy) / (r * .92))
                if d < 1 and base.get((x, y)) in ground:
                    p.apx(x, y, ramp[5 if night else 4], alphas[min(2, int((1 - d) * 3))], "base")

    def _twinkles(self, p: Pix, motion: Motion, spots, ramp: list):
        """Sparkles that twinkle on the engine's cadence, each on its own beat."""
        for i, (x, y, big) in enumerate(spots):
            cells: dict = {}
            sparkle(cells, x, y, ramp, big)
            delay = round(i * .5 % 1.5, 2)
            markup = f'<g class="tw" style="animation-delay:{delay}s">{p.markup(cells)}</g>'
            p.raw(25, markup, markup)
        motion.used.add("tw")

    def _glint(self, p: Pix, motion: Motion, cells, ramp: list, uid: str):
        """A glint across a trophy's metal: a band of light two pixels wide that steps across it, clipped to the
        metal alone, so it never crosses an enamel or a word."""
        if not cells:
            return
        ys = [y for _, y in cells]
        y0, y1 = min(ys), max(ys)
        x0 = min(x for x, _ in cells)
        band = {}
        for y in range(y0, y1 + 1):
            for k, c in ((0, ramp[6]), (1, ramp[6]), (2, ramp[5])):
                band[(x0 + (y1 - y) // 2 + k, y)] = c
        cid = f"trg{uid}"   # a prefix no set's own ids take
        p.defs.append(f'<clipPath id="{cid}"><path d="{Pix.area(cells)}"/></clipPath>')
        markup = f'<g clip-path="url(#{cid})"><g class="gl">{p.markup(band)}</g></g>'
        p.raw(24, markup, markup)
        motion.used.add("gl")

    # -------------------------------------------------------------------------------- shared pieces
    def _tagged(self, p: Pix, x: int, y: int, word: str, night: bool, plate: bool = False, after: int = 0) -> int:
        """`word` on one of the set's tags, as its sheets letter a tag: two rows in and four along, `after` more
        columns of room after it. Returns the tag's width."""
        w = tw(word, "35") + 8 + after
        (self.trophy_plate if plate else self.tag)(p, x, y, w, TAG, night)
        p.text(x + 4, y + 2, word, self.ink(night)["tag_ink"], "35")
        return w

    def _tag_reach(self, w: int, night: bool) -> tuple[int, int, int, int]:
        """How far past its box the set dresses a tag `w` wide, to its left, its right, above and below: a strap's
        buckle, say."""
        scratch = Pix(w + 24, TAG + 8)
        self.tag(scratch, 12, 4, w, TAG, night)
        cells = list(scratch.layers["base"])
        if not cells:
            return 0, 0, 0, 0
        xs, ys = [x for x, _ in cells], [y for _, y in cells]
        return (max(0, 12 - min(xs)), max(0, max(xs) - (11 + w)), max(0, 4 - min(ys)), max(0, max(ys) - (3 + TAG)))

    def _top_row(self, room: Room, night: bool) -> tuple[int, int]:
        """The row a card's top row of tags sits on, low enough that all the set dresses a tag in keeps inside the
        room, and the first row under it all."""
        _, _, up, down = self._tag_reach(24, night)
        return room.y0 + up, room.y0 + up + TAG + down

    def _tags(self, p: Pix, room: Room, core, m: dict, o: dict, night: bool):
        """A card's top row: NEW on a tag at the right for a tier newly reached, and the rank on one at the left,
        TOP 2.8%, set as 2.8% or left off where the two would meet; both clear of the frame's corner pieces, and
        placed by all the set dresses them in."""
        y, _ = self._top_row(room, night)
        x0, x1 = room.span(room.y0, TAG + y - room.y0 + 1)
        new = bool(o.get("new") and m["t"])
        right = x1
        if new:
            w = tw("NEW", "35") + 8
            lead, trail, _, _ = self._tag_reach(w, night)
            right = x1 - trail - w
            self._tagged(p, right, y, "NEW", night)
            right -= lead + 2
        if o.get("rank") and m["t"]:
            lab = pct_label(top_pct(core, m["v"]))
            for s in (lab, lab.split(" ", 1)[-1]):
                w = tw(s, "35") + 8
                lead, trail, _, _ = self._tag_reach(w, night)
                if x0 + lead + w + trail <= right:
                    self._tagged(p, x0 + lead, y, s, night)
                    break

    def _line(self, p: Pix, room: Room, y: int, s: str, colour: str, cx: float | None = None) -> int:
        """A line of small capitals on row `y`, centred on `cx` (or set from the room's left): two units clear of the
        frame and its corner pieces on its own row, set tighter where it would not fit, and cut only if even that
        cannot fit it. Returns its width."""
        x0, x1 = room.span(y - 1, 7)
        x0, x1 = x0 + 1, x1 - 1
        track = 1 if tw(s, "35") <= x1 - x0 else 0
        if tw(s, "35", 1, track) > x1 - x0:
            s, track = clip(s, x1 - x0, "35"), 1
        w = tw(s, "35", 1, track)
        x = x0 if cx is None else max(x0, min(x1 - w, round(cx - w / 2)))
        return p.text(x, y, s, colour, "35", 1, track=track)

    def _plate(self, p: Pix, cx: float, y: int, word: str, night: bool, stars: int = 0):
        """A tier engraved on the set's plate, its stars after it, centred on `cx`, and the set's own touch along
        the plate's top, as it lies along a badge's: in the two rows over its letters."""
        k = self.ink(night)
        after = stars * 6 + 1 if stars else 0
        x = round(cx - (tw(word, "35") + 8 + after) / 2)
        w = self._tagged(p, x, y, word, night, plate=True, after=after)
        for i in range(stars):
            p.sprite(x + 4 + tw(word, "35") + 2 + i * 6, y + 2, SMALL_STAR, {"#": k["tag_ink"]})
        touch = Pix(w, TAG)
        self.badge_top(touch, w, {"h": TAG, "corner": "notch", "font": "35"}, len(word) * 3, night)
        for (tx, ty), c in touch.layers["base"].items():
            if ty < 2:
                p.px(x + tx, y + ty, c)

    def _bar(self, p: Pix, x: int, y: int, w: int, share: float, night: bool, fill: str | None = None, h: int = 3):
        """A progress bar: its track in the set's dotted guides, filled as far as it has got."""
        k = self.ink(night)
        p.rect(x, y, w, h, k["dim"])
        n = round(w * max(0.0, min(1.0, share)))
        if n:
            p.rect(x, y, n, h, fill or k["accent"])
            if n < w:
                p.vline(x + n - 1, y, y + h, k["body"])

    def _gauge(self, p: Pix, cx: float, cy: float, r: float, share: float, colour: str, night: bool, n: int = 160):
        """A ring round a medal or a pin, filled from its top as far as `share` in `colour`, its head a spark of
        light, and its track the set's quiet ink washed in, so the whole ring reads at any share."""
        k = self.ink(night)
        drawn, head = set(), None
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            q = (round(cx - .5 + r * math.cos(a)), round(cy - .5 + r * math.sin(a)))
            if q in drawn:
                continue
            drawn.add(q)
            if i / n < share:
                p.px(*q, colour)
                head = q
            else:
                p.apx(*q, k["muted"], .35, L="base")
        if head and share < 1:
            p.px(*head, k["body"])

    def _pips(self, p: Pix, cx: float, y: int, m: dict, night: bool):
        """The five tiers as five diamonds: struck in each tier's metal once reached, outlined in the next, and
        dotted for those still to come; diamond's stars after them."""
        k = self.ink(night)
        metals = self.trophy_metals()
        stars = m["stars"]
        n = 5 * 7 + (stars * 6 + 2 if stars else 0) - 2
        x = round(cx - n / 2)
        for i in range(5):
            ramp = metals[i + 1]
            if m["t"] > i:
                p.sprite(x, y, DIAMOND, {"#": ramp[3]})
                p.sprite(x + 1, y + 1, [".#.", "##.", "..."], {"#": ramp[5]})
                p.px(x + 2, y + 3, ramp[1])
            elif m["t"] == i:
                p.sprite(x, y, ["..#..", ".#.#.", "#...#", ".#.#.", "..#.."], {"#": k["accent"]})
            else:
                p.sprite(x, y, ["..#..", ".....", "#...#", ".....", "..#.."], {"#": k["muted"]})
            x += 7
        x += 2
        for _ in range(stars):
            p.sprite(x, y, STAR, {"#": metals[5][4]})
            x += 6

    def _foot_at(self, room: Room, kind: str, gap: int) -> dict:
        """Where a card's foot sits, from the bottom up: its status on the last rows a word may take, then its bar,
        its value and the trophy's name over it, `gap` rows between each."""
        status = room.foot - 4
        bar = status - gap - 3 if kind in ("bar", "seg") else None
        value = (status if bar is None else bar) - gap - 14
        return {"status": status, "bar": bar, "value": value, "title": value - gap - 5}

    def _footer(self, p: Pix, room: Room, core, m: dict, o: dict, night: bool, kind: str, at: dict):
        """A card's foot: the trophy's name, its value and how it moved this week, its progress, and where it
        stands."""
        k = self.ink(night)
        W = p.w
        centred(p, W / 2, at["title"], core.title.upper(), k["muted"], "35")
        vs = fmt(m["v"])
        delta = o.get("delta")
        extra = (tw(fmt(delta), "35") + 6) if delta else 0
        scale = 2 if tw(vs, "57", 2) + extra <= room.x1 - room.x0 - 4 else 1
        vw = tw(vs, "57", scale)
        unit = core.unit.upper() if core.unit else ""
        uw = tw(unit, "35") + 2 if unit else 0
        x = round(W / 2 - (vw + uw + extra) / 2)
        vy = at["value"] + (0 if scale == 2 else 4)
        p.text(x, vy, vs, k["body"], "57", scale)
        if unit:
            p.text(x + vw + 2, vy + 7 * scale - 5, unit, k["muted"], "35")
        if delta:
            dx = x + vw + uw + 3
            p.sprite(dx, vy + 1, UP, {"#": k["accent"]})
            p.text(dx + 4, vy, fmt(delta), k["accent"], "35")
        bx0, bx1 = room.x0 + 3, room.x1 - 3
        if kind == "bar":
            self._bar(p, bx0, at["bar"], bx1 - bx0, m["pct"] if m["next"] else 1.0, night,
                      self._tint(min(5, m["t"] + 1), night))
        elif kind == "seg":
            sw = (bx1 - bx0 - 8) // 5
            x0 = round(W / 2 - (5 * sw + 8) / 2)
            for i in range(5):
                share = 1 if m["t"] > i else (m["pct"] if m["t"] == i else 0)
                self._bar(p, x0 + i * (sw + 2), at["bar"], sw, share, night, self._tint(i + 1, night))
        self._line(p, room, at["status"], status_text(m), k["muted"], W / 2)

    # ------------------------------------------------------------------------------------ the trophies
    def _cup(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int, top: int, bottom: int):
        """The trophy, a cup: a turned bowl on its stem and foot, two handles, the trophy's enamel on its bowl, on
        a plinth whose plate is engraved with its tier, and the five tiers in pips under it; as tall as the rows
        from `top` to `bottom` let it be."""
        t, k = m["t"], self.ink(night)
        R = 17
        H = max(16, min(23, bottom - top + 1 - 33))    # the bowl's height; the rim, stem, foot, plinth and pips take 33
        y = top + 3 + max(0, (bottom - top + 1 - 33 - H) // 2)
        rows = [(y + i, round(max(2.6, R * max(0.0, 1 - (i / H) ** 2.4) ** .55))) for i in range(H + 1)]
        stem = [(y + H + 1 + i, 2 if i != 2 else 3) for i in range(5)]
        foot = [(y + H + 6 + i, 4 + i * 2) for i in range(4)]
        half = dict(rows + stem + foot)
        body = {(x, yy) for yy, n in half.items() for x in range(cx - n, cx + n)}
        s = H / 24

        def handle(side: int) -> list:
            return [(cx + side * (R + dx), y + dy * s) for dx, dy in ((-1, 3), (3, 2.5), (6, 5.5), (6, 10), (3, 14.5),
                                                                       (-3, 17))]

        rim = set()
        for yy in range(y - 3, y + 3):
            for x in range(cx - R - 1, cx + R + 1):
                if ((x + .5 - cx) / (R + .5)) ** 2 + ((yy + .5 - y) / 2.6) ** 2 <= 1:
                    rim.add((x, yy))
        ey = y + round(11 * s)
        if t == 0:
            scratch = Pix(p.w, p.h)
            for side in (-1, 1):
                tube(scratch, handle(side), 1.5, lambda *a: "#000000", outline="#000000")
            handles = set(scratch.layers["base"]) - body - rim
            ghost(p, body | rim | handles, k["muted"], wash=0)
            for (x, yy) in body | rim:
                p.apx(x, yy, k["muted"], .12, L="base")
            p.sprite(cx - 3, ey - 3, glyph(core.icon), {"#": k["muted"]})
        else:
            ramp = self.trophy_metals()[t]
            for side in (-1, 1):   # the handles, as tubes on the same light
                tube(p, handle(side), 1.5, lambda s_, o, lam, x, yy: ramp[max(1, min(6, 1 + round(5 * lam)))],
                     outline=ramp[0])
            for (x, yy) in body:
                n = half[yy]
                nx = (x + .5 - cx) / max(1, n)
                nz = math.sqrt(max(0.0, 1 - nx * nx))
                lam = max(0.0, nx * LX + nz * LZ + .1)
                v = 1.2 + 4.6 * lam ** 1.15
                if abs(nx + .45) < .14 and yy < y + H - 3:
                    v = 6.2     # the glint down the bowl where the lamp lands
                p.px(x, yy, ramp[tone(v, x, yy, 1, 6)])
            for (x, yy) in rim:   # the rim, and the cup's inside in shadow
                inside = ((x + .5 - cx) / (R - 2.5)) ** 2 + ((yy + .5 - y + .3) / 1.5) ** 2 <= 1
                if inside:
                    p.px(x, yy, ramp[1] if yy >= y - 1 else ramp[2])
                else:
                    p.px(x, yy, ramp[6] if x < cx - 3 and yy < y else ramp[5] if x < cx + 6 else ramp[3])
            outline(p, body | rim, ramp, cx, y + 14)
            # The enamel, a disc on the bowl, its icon cut in the enamel's ink.
            block, ink = self.trophy_enamel(core.hue)
            enamel = disc(cx, ey, 6.6)
            for (x, yy) in enamel:
                d = math.hypot(x + .5 - cx, yy + .5 - ey)
                p.px(x, yy, block if d <= 5.4 else ramp[1] if lit(x + .5 - cx, yy + .5 - ey) < 0 else ramp[5])
            p.sprite(cx - 3, ey - 3, glyph(core.icon), {"#": ink})
            self._shine(p, cx, y + 14, 30, ramp, t, night)
            if t >= 3:
                self._glint(p, motion, (body | rim) - enamel, ramp, "c")
            if t >= 5:   # the prism, where the bowl catches the light
                for (x, yy) in ((cx - 12, y + 6), (cx - 9, y + 15), (cx + 10, y + 4), (cx + 6, y + 18),
                                (cx - 14, y + 1)):
                    p.px(x, yy, PRISM[0][5])
                    p.px(x + 1, yy, PRISM[1][5])
        # The plinth, in the set's own card, and the plate its tier is engraved on.
        py = y + H + 10
        light, dark = self.card_bevel(night)
        for (x0, y0, w, h) in ((cx - 15, py, 30, 2), (cx - 22, py + 2, 44, TAG + 2)):
            p.rect(x0, y0, w, h, k["fill"])
            p.bevel(x0, y0, w, h, light, dark)
            p.box(x0 - 1, y0 - 1, w + 2, h + 2, k["rule"], notch=True)
        self._plate(p, cx, py + 3, TIER_NAMES[t].upper(), night, 0)
        self._pips(p, cx, py + 15, m, night)
        if t >= 4:
            ramp = self.trophy_metals()[t]
            self._twinkles(p, motion, [(cx - 32, y + 1, True), (cx + 27, y + 1, False), (cx + 27, y + 21, True),
                                       (cx - 31, y + 24, False)] + ([(cx - 30, y + 12, False)] if t == 5 else []),
                           ramp)

    def _crest(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int, top: int, bottom: int):
        """The crest: a hexagon, its frame bevelled in the tier's metal round the trophy's enamel, on a banner
        engraved with its tier; rivets from silver, a gem from gold, wings from platinum and a crown at diamond;
        as big as the rows from `top` to `bottom` let it be."""
        t, k = m["t"], self.ink(night)
        by = bottom - TAG + 1             # the banner's plate, on the last rows
        R = max(15, min(19, (by - top - 5) // 2))
        cy = by - R - 1
        rim = 4.5 if R >= 18 else 4.0
        shape = {(x, y) for y in range(cy - R - 1, cy + R + 2) for x in range(cx - R, cx + R + 1)
                 if hex_in(x + .5, y + .5, cx, cy, R)}
        if t == 0:
            ghost(p, shape, k["muted"])
            p.sprite(cx - 7, cy - 7, glyph(core.icon), {"#": k["muted"]}, 2)
            self._plate(p, cx, by, "UNRANKED", night)
            return
        metals = self.trophy_metals()
        ramp = metals[t]
        if t >= 4:   # wings, three feathers a side, behind the frame
            for side in (-1, 1):
                for f in range(3):
                    y0 = cy - 7 + f * 7
                    length = 15 - f * 3
                    for i in range(length):
                        x = cx + side * (16 + i)
                        y = y0 - round(i * (.55 - f * .2))
                        thick = max(1, 3 - i * 3 // length)
                        for j in range(thick):
                            v = 4.8 - i * 2.6 / length - j * .9
                            p.px(x, y + j, ramp[tone(v, x, y + j, 1, 6)])
                        p.px(x, y + thick, ramp[0])
        block, ink = self.trophy_enamel(core.hue)
        frame = set()
        for (x, y) in shape:
            px_, py_ = x + .5, y + .5
            if hex_in(px_, py_, cx, cy, R - rim):
                p.px(x, y, block)
                continue
            frame.add((x, y))
            a = math.degrees(math.atan2(py_ - cy, px_ - cx)) % 360
            face = math.radians(round(a / 60) * 60 % 360)
            v = 3.4 + 2.6 * lit(math.cos(face), math.sin(face))
            if not hex_in(px_, py_, cx, cy, R - rim + 1.1):
                p.px(x, y, ramp[tone(v, x, y, 1, 6)])
            else:
                p.px(x, y, ramp[0])
        outline(p, shape, ramp, cx, cy)
        self._shine(p, cx, cy, 31, ramp, t, night)
        p.sprite(cx - 7, cy - 7, glyph(core.icon), {"#": ink}, 2)
        if t >= 2:   # rivets at the corners
            for i in range(6):
                if i == 0 and t >= 3:
                    continue
                a = math.radians(-90 + 60 * i)
                x, y = round(cx - .5 + (R - 2.2) * math.cos(a)), round(cy - .5 + (R - 2.2) * math.sin(a))
                p.px(x, y, ramp[6])
                p.px(x + 1, y + 1, ramp[1])
        if 3 <= t < 5:   # the gem on the top corner
            gem = metals[4] if t == 3 else PRISM[1]
            p.sprite(cx - 3, cy - R - 2, DIAMOND, {"#": gem[3]})
            p.px(cx - 2, cy - R, gem[6])
            p.px(cx - 1, cy - R - 1, gem[5])
            p.px(cx, cy - R + 1, gem[1])
        if t >= 5:   # and at diamond a crown in its place, its jewels the prism's
            cells = {(cx - 4 + i, cy - R - 5 + j) for j, row in enumerate(CROWN) for i, ch in enumerate(row)
                     if ch == "#"}
            for (x, y) in cells:
                p.px(x, y, ramp[tone(5.4 - (y - (cy - R - 5)) * .8 - (x - cx) * .12, x, y, 1, 6)])
            outline(p, cells, ramp, cx, cy - R - 3)
            for x, c in ((cx - 4, PRISM[0][5]), (cx, PRISM[1][5]), (cx + 4, PRISM[0][5])):
                p.px(x, cy - R - 5, c)
        if t >= 3:
            self._glint(p, motion, frame, ramp, "h")
        # The banner: its tails folded behind in the metal, the tier on the set's plate across it.
        for side in (-1, 1):
            for j in range(7):
                for i in range(9):
                    x = cx + side * (17 + i) - (1 if side < 0 else 0)
                    if i >= 7 and abs(j - 3) < (i - 6):
                        continue
                    p.px(x, by + 2 + j, ramp[2] if j else ramp[3])
                p.px(cx + side * 17 - (1 if side < 0 else 0), by + 2 + j, ramp[0])
        self._plate(p, cx, by, TIER_NAMES[t].upper(), night, m["stars"])
        if t >= 4:
            self._twinkles(p, motion, [(cx - 33, cy - 20, True), (cx + 28, cy - 20, False), (cx + 28, cy + 12, True),
                                       (cx - 31, cy + 14, False)], ramp)

    def _ribbon(self, p: Pix, cx: int, top: int, bottom: int, night: bool, block: str, t: int):
        """A medal's ribbon: two straps that cross to its ring, the far one in shadow, each edged in the set's rule
        with the trophy's enamel down its middle; an unranked medal's only a ghost of one."""
        k = self.ink(night)
        straps = []
        for side in (-1, 1):
            cells = {}
            for y in range(top, bottom + 1):
                f = (y - top) / max(1, bottom - top)
                outer = round(cx + side * (17 - 12 * f))
                for i in range(7):
                    cells[(outer - side * i, y)] = i
            straps.append((side, cells))
        if not t:
            ghost(p, set(straps[0][1]) | set(straps[1][1]), k["muted"])
            return
        for side, cells in straps:   # the far strap first, so the near one crosses it
            for (x, y), i in cells.items():
                p.px(x, y, k["rule"] if i in (0, 6) else block if 2 <= i <= 4 else k["accent"])
                if side < 0:
                    p.apx(x, y, METALS[1][0], .3)

    def _medallion(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int, top: int, bottom: int):
        """The medallion: a medal struck in the tier's metal, its rim reeded and its face sunk inside it, a laurel
        up each side of the trophy's enamel, hung on its ribbon by a ring; the ring round it filled as far as the
        next tier, and its tier on a plate below; as big as the rows from `top` to `bottom` let it be."""
        t, k = m["t"], self.ink(night)
        metals = self.trophy_metals()
        block, ink = self.trophy_enamel(core.hue)
        py = bottom - TAG + 1
        G = max(13, min(19, (py - 3 - top - 7) // 2))      # the ring's radius; the medal's is three less
        r = G - 3
        cy = py - 3 - G
        nxt = min(5, t + 1)
        self._gauge(p, cx, cy, G, m["pct"] if m["next"] else 1.0, self._tint(nxt, night), night)
        self._ribbon(p, cx, top, cy - r + 2, night, block, t)
        medal = disc(cx, cy, r + .4)
        if t == 0:
            ghost(p, medal, k["muted"])
            p.sprite(cx - 3, cy - 3, glyph(core.icon), {"#": k["muted"]})
            self._plate(p, cx, py, "UNRANKED", night)
            return
        ramp = metals[t]
        for (x, y) in ((cx - 2, cy - r - 2), (cx - 1, cy - r - 2), (cx, cy - r - 2), (cx + 1, cy - r - 2),
                       (cx - 2, cy - r - 1), (cx + 1, cy - r - 1)):   # the ring it hangs by
            p.px(x, y, ramp[5] if x < cx else ramp[2])
        enamel = disc(cx, cy, 6.6)
        for (x, y) in medal:
            dx, dy = x + .5 - cx, y + .5 - cy
            d = max(.01, math.hypot(dx, dy))
            light = lit(dx / d, dy / d)
            if (x, y) in enamel:
                p.px(x, y, block if d <= 5.4 else ramp[1] if lit(dx, dy) < 0 else ramp[5])
            elif d > r - 1.4:      # the rim, lit along its top and left
                p.px(x, y, ramp[6 if light > .45 else 5 if light > 0 else 3 if light > -.5 else 2])
            elif d > r - 2.6:      # the face's sunk edge, in shadow where the rim is lit
                p.px(x, y, ramp[2] if light > 0 else ramp[5])
            else:                  # the field, a step lighter toward the lamp
                v = lit(dx / r, dy / r)
                p.px(x, y, ramp[5 if v > .3 else 3 if v < -.35 else 4])
        outline(p, medal, ramp, cx, cy)
        self._shine(p, cx, cy, r + 12, ramp, t, night)
        lr = (6.6 + r - 2.6) / 2 - .5
        wreath = {}
        for i in range(260):   # the laurel: a wreath up each side of the enamel from its foot, open at its top
            a = 2 * math.pi * i / 260
            deg = math.degrees(a) % 360
            if not (110 <= deg <= 245 or deg <= 70 or deg >= 295):
                continue
            for k_, rad in enumerate((lr, lr + 1)):
                q = (round(cx - .5 + rad * math.cos(a)), round(cy - .5 + rad * math.sin(a)))
                wreath[q] = (round(deg / 9) + k_) % 3
        for q, beat in wreath.items():   # in herringbone, a leaf's light edge every third pixel
            p.px(*q, ramp[5] if beat == 0 else ramp[2])
        p.sprite(cx - 3, cy - 3, glyph(core.icon), {"#": ink})
        if t >= 3:
            self._glint(p, motion, medal - enamel, ramp, "m")
        if t >= 5:
            for (x, y) in ((cx - r + 3, cy - 4), (cx - 5, cy - r + 3), (cx + r - 5, cy + 5)):
                p.px(x, y, PRISM[0][5])
                p.px(x + 1, y, PRISM[1][5])
        if t >= 4:
            self._twinkles(p, motion, [(cx - G - 13, cy - G + 1, True), (cx + G + 8, cy - G, False),
                                       (cx + G + 7, cy + 5, True), (cx - G - 11, cy + 8, False)], ramp)
        self._plate(p, cx, py, TIER_NAMES[t].upper(), night, m["stars"])

    def _crystal(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int, top: int, bottom: int):
        """The crystal: cut in the tier's metal, lit from within as far as its progress, its facets shaded by the
        lamp, the trophy's icon at its heart, its shards about it, rings round it from platinum, and its tier on a
        plate below; as tall as the rows from `top` to `bottom` let it be."""
        t, k = m["t"], self.ink(night)
        py = bottom - TAG + 1
        Hc = max(30, min(46, py - 2 - top))
        y0 = top + max(0, (py - 2 - top - Hc) // 2)

        def Y(f: float) -> int:
            return y0 + round(f * (Hc - 1))

        V = {"T": (cx, y0), "LS": (cx - 12, Y(.28)), "FL": (cx - 5, Y(.23)), "FR": (cx + 5, Y(.23)),
             "RS": (cx + 12, Y(.28)), "LB": (cx - 10, Y(.74)), "BL": (cx - 4, Y(.81)), "BR": (cx + 4, Y(.81)),
             "RB": (cx + 10, Y(.74)), "B": (cx, Y(1))}
        faces = [(("LS", "FL", "BL", "LB"), 5), (("FL", "FR", "BR", "BL"), 4), (("FR", "RS", "RB", "BR"), 2),
                 (("T", "LS", "FL"), 6), (("T", "FL", "FR"), 5), (("T", "FR", "RS"), 3),
                 (("LB", "BL", "B"), 3), (("BL", "BR", "B"), 2), (("BR", "RB", "B"), 1)]

        def inside(px_, py_, keys):
            pts = [V[n] for n in keys]
            sign = None
            for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
                cr = (bx - ax) * (py_ - ay) - (by - ay) * (px_ - ax)
                if abs(cr) < 1e-9:
                    continue
                if sign is None:
                    sign = cr > 0
                elif (cr > 0) != sign:
                    return False
            return True

        cells = {}
        for y in range(y0 - 1, Y(1) + 2):
            for x in range(cx - 14, cx + 15):
                for keys, v in faces:
                    if inside(x + .5, y + .5, keys):
                        cells[(x, y)] = v
                        break
        mid = Y(.5)
        share = 1.0 if t == 5 else m["pct"]
        level = round(Y(1) - share * (Y(1) - y0))
        g = glyph(core.icon)
        if t == 0:
            ghost(p, set(cells), k["muted"])
            p.sprite(cx - 3, mid - 3, g, {"#": k["muted"]})
            self._plate(p, cx, py, "UNRANKED", night)
            return
        ramp = self.trophy_metals()[t]
        ring_y = Y(.46)
        if t >= 4:   # a ring round it, its far half behind
            for i in range(120):
                a = 2 * math.pi * i / 120
                if math.sin(a) < 0:
                    p.px(round(cx - .5 + 19 * math.cos(a)), round(ring_y + 4.5 * math.sin(a)), ramp[3])
        for (x, y), v in cells.items():
            p.px(x, y, ramp[tone(v + (1 if y >= level else 0), x, y, 1, 6)])
        if 0 < share < 1:
            for x in range(cx - 14, cx + 15):
                if (x, level) in cells:
                    p.px(x, level, ramp[6])
        outline(p, set(cells), ramp, cx, mid)
        self._shine(p, cx, mid, 27, ramp, t, night)
        for a_, b_ in (("T", "FL"), ("FL", "BL"), ("T", "FR")):   # the edges the lamp finds
            (ax, ay), (bx, by) = V[a_], V[b_]
            n = max(abs(bx - ax), abs(by - ay))
            for i in range(n + 1):
                x, y = round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n)
                if (x, y) in cells:
                    p.px(x, y, ramp[6] if a_ == "T" else ramp[5])
        # The trophy's icon at its heart, cut clear: the lightest tone inside an edge of the darkest.
        icon = {(cx - 3 + i, mid - 3 + j) for j, row in enumerate(g) for i, ch in enumerate(row) if ch == "#"}
        for (x, y) in icon:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x + dx, y + dy) not in icon:
                        p.px(x + dx, y + dy, ramp[0])
        for (x, y) in icon:
            p.px(x, y, ramp[6])
        for (sx, sy) in ((cx - 23, Y(.06)), (cx + 20, Y(.12)), (cx + 18, Y(.76)), (cx - 21, Y(.68))):   # shards
            shard = {(sx + i, sy + j) for j, row in enumerate(SHARD) for i, ch in enumerate(row) if ch == "#"}
            for (x, y) in shard:
                p.px(x, y, ramp[5] if x - sx + y - sy < 3 else ramp[3])
            outline(p, shard, ramp, sx + 1, sy + 2)
        if t >= 4:   # and its near half in front
            for i in range(120):
                a = 2 * math.pi * i / 120
                if math.sin(a) >= 0:
                    p.px(round(cx - .5 + 19 * math.cos(a)), round(ring_y + 4.5 * math.sin(a)),
                         ramp[6] if math.cos(a) < 0 else ramp[4])
            self._twinkles(p, motion, [(cx - 31, Y(.22), True), (cx + 26, Y(.3), False), (cx + 23, Y(.88), True),
                                       (cx - 29, Y(.86), False)], ramp)
        if t >= 5:
            for (x, y) in ((cx - 8, Y(.35)), (cx + 6, Y(.6)), (cx - 3, Y(.9))):
                p.px(x, y, PRISM[0][5])
                p.px(x + 1, y, PRISM[1][5])
        if t >= 3:
            self._glint(p, motion, set(cells) - icon, ramp, "x")
        self._plate(p, cx, py, TIER_NAMES[t].upper(), night, m["stars"])

    # ------------------------------------------------------------------------------------ the entry points
    def trophy_card(self, style: str, core, value: int, o: dict, night: bool) -> str | None:
        """One core trophy's card in `style`, as the set draws it; None when the set cannot letter it."""
        m = measure(core, value)
        if style == "plaque":
            return self._trophy_file(lambda motion: self._plaque(motion, core, m, o, night), alt_text(core, m, o),
                                     night)
        kind = {"trophy": "bar", "crest": "seg"}.get(style, "none")
        art = {"trophy": self._cup, "crest": self._crest, "medallion": self._medallion, "crystal": self._crystal}[style]

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(CARD, night)
            room = self._trophy_room(p)
            top = self._top_row(room, night)[1] + 1
            at = self._foot_at(room, kind, 2)
            if at["title"] - 2 - top < WANTED[style]:
                at = self._foot_at(room, kind, 1)
            art(p, motion, core, m, night, p.w // 2, top, at["title"] - 3)
            self._tags(p, room, core, m, o, night)
            self._footer(p, room, core, m, o, night, kind, at)
            return p
        return self._trophy_file(draw, alt_text(core, m, o), night)

    def _plaque(self, motion: Motion, core, m: dict, o: dict, night: bool) -> Pix:
        """The plaque, a plate across the row: its tier's metal at the left with a trophy struck in it, then the
        trophy's name and its tier, its value and how it moved this week, the five tiers, and how far it is to the
        next with its rank."""
        t, k = m["t"], self.ink(night)
        p = self._card_canvas(PLAQUE, night)
        room = self._trophy_room(p)
        y0, y1 = room.y0, room.y1
        x0, _ = room.span(y0, y1 - y0)
        x1 = x0 + 32
        cells = {(x, y) for x in range(x0, x1) for y in range(y0, y1)}
        gx, gy = (x0 + x1) // 2 - 7, (y0 + y1) // 2 - 7
        if t:
            ramp = self.trophy_metals()[t]
            for (x, y) in cells:
                v = 4.2 + (1.2 if (y - y0) % 4 == 0 else 0) - .9 * (x - x0) / (x1 - x0) - .6 * (y - y0) / (y1 - y0)
                p.px(x, y, ramp[tone(v, x, y, 1, 6)])
            trophy = {(gx + 2 * i + a, gy + 2 * j + b) for j, row in enumerate(glyph("trophy")) for i, ch in
                      enumerate(row) if ch == "#" for a in (0, 1) for b in (0, 1)}
            for (x, y) in trophy:
                p.px(x + 1, y + 1, ramp[6])
            for (x, y) in trophy:
                p.px(x, y, ramp[0])
            if t >= 3:
                self._glint(p, motion, cells - trophy, ramp, "p")
            if t >= 4:
                self._twinkles(p, motion, [(x0 + 1, y0 + 1, False), (x1 - 6, y1 - 6, True)], ramp)
        else:
            ghost(p, {(x, y) for (x, y) in cells if x0 < x < x1 - 1 and y0 < y < y1 - 1}, k["muted"])
            p.sprite(gx, gy, glyph("trophy"), {"#": k["muted"]}, 2)
        p.vline(x1, y0, y1, k["rule"])
        rx = x1 + 4
        _, right = room.span(y0, TAG)
        right -= 2          # the last column a word may take
        # The trophy's name after its icon in its enamel's colour, and its tier lettered at the right, after its stars.
        block, ink = self.trophy_enamel(core.hue)
        mark = block if contrast(block, self.bg_at(p, night, y0 + 3)) >= 3 else k["body"]
        p.sprite(rx, y0, glyph(core.icon), {"#": mark})
        word = TIER_NAMES[t].upper()
        ww = tw(word, "35")
        p.text(right - ww + 1, y0 + 1, word, k["accent"] if t else k["muted"], "35")
        for i in range(m["stars"]):
            p.sprite(right - ww - 7 - i * 6, y0 + 1, SMALL_STAR, {"#": self._tint(5, night)})
        title_room = right - ww - 4 - m["stars"] * 6 - (rx + 10)
        p.text(rx + 10, y0 + 1, clip(core.title.upper(), title_room, "35"), k["muted"], "35")
        # The value as big as the room lets it be, the five tiers under it, and the status on the last rows; where
        # the room is too short for all three at full size, the five tiers give way before the value does.
        vs = fmt(m["v"])
        delta = o.get("delta")
        extra = (tw(fmt(delta), "35") + 6) if delta else 0
        status_y = room.foot - 4
        vy = y0 + 8
        wide = tw(vs, "57", 2) + extra <= right - rx
        if wide and vy + 18 <= status_y:
            scale, bar_y = 2, vy + 15 + (1 if vy + 20 <= status_y else 0)
        elif wide and vy + 16 <= status_y:
            scale, bar_y = 2, None
        else:
            scale, bar_y = 1, vy + 9
            vy += 1
        p.text(rx, vy, vs, k["body"], "57", scale)
        if delta:
            dx = rx + tw(vs, "57", scale) + 3
            p.sprite(dx, vy + 1, UP, {"#": k["accent"]})
            p.text(dx + 4, vy, fmt(delta), k["accent"], "35")
        if bar_y is not None:
            sw = (right - rx - 8) // 5
            for i in range(5):
                share = 1 if t > i else (m["pct"] if t == i else 0)
                self._bar(p, rx + i * (sw + 2), bar_y, sw, share, night, self._tint(i + 1, night), 2)
        status = ("NEW · " if o.get("new") and t else "") + status_text(m)
        _, status_right = room.span(status_y, 5)
        status_right = min(right, status_right - 2)     # the last column a word on the status row may take
        status = clip(status, status_right - rx, "35")
        p.text(rx, status_y, status, k["muted"], "35")
        if o.get("rank") and t:
            rank = pct_label(top_pct(core, m["v"]))
            if tw(status, "35") + 6 + tw(rank, "35") <= status_right - rx:
                p.text(status_right - tw(rank, "35") + 1, status_y, rank, k["muted"], "35")
        return p

    def trophy_pin(self, a, cur, night: bool) -> str | None:
        """One achievement's pin, as the set draws it; None when the set cannot letter it."""
        st = ach_state(a, cur)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(PIN, night)
            room = self._trophy_room(p)
            k = self.ink(night)
            metals = self.trophy_metals()
            earned, secret = st["earned"], st["secret"]
            t = st["rarity"] if earned else 0
            share = 1.0 if st["done"] else st["pct"]
            ringed = not secret and not st["done"]
            # The words from the foot up: the caption on the last row a word may take, the name's lines over it.
            wx0, wx1 = room.x0 + 1, room.x1 - 1
            name = "???" if secret else a.name + (f" {st['tier']}" if st["tier"] else "")
            lines = lines_of(name, wx1 - wx0)
            whole = pin_caption(st)
            cap_y = room.foot - 4
            cx0, cx1 = room.span(cap_y - 1, 7)
            room_w = cx1 - cx0 - 2
            cap = next((c for k_ in (1, 0) for c in (whole, whole.split(" · ")[0], "NOT MEASURED", "UNMEASURED")
                        if tw(c, "35", 1, k_) <= room_w), whole)
            name_y = cap_y - 1 - 6 * len(lines)
            # The pin in the room over the words, as big as it fits: its outline a unit round it, its ring two more.
            rows, g = name_y - 1 - room.y0, 2 if ringed else 0
            r = max(8, min(13, (rows - 2 - 2 * g) // 2))
            cx = p.w // 2
            cy = room.y0 + r + 1 + g + max(0, rows - (2 * r + 2 + 2 * g)) // 2
            if ringed:
                self._gauge(p, cx, cy, r + 2.5, share, self._tint(st["next_rarity"] or 1, night), night, 120)
            face = disc(cx, cy, r)
            if secret or not earned:
                ghost(p, disc(cx, cy, r - 1), k["muted"])
                p.sprite(cx - 3, cy - 3, glyph("q" if secret else a.icon), {"#": k["muted"]})
            else:
                ramp = metals[t]
                block, ink = self.trophy_enamel(a.hue)
                inner = r - 4.4
                enamel = disc(cx, cy, inner + 1)
                for (x, y) in face:
                    dx, dy = x + .5 - cx, y + .5 - cy
                    d = max(.01, math.hypot(dx, dy))
                    if d <= inner:
                        p.px(x, y, block)
                    elif d <= inner + 1:
                        p.px(x, y, ramp[1])
                    else:
                        p.px(x, y, ramp[tone(3.4 + 2.6 * lit(dx / d, dy / d), x, y, 1, 6)])
                outline(p, face, ramp, cx, cy)
                if t >= 2:   # a reeded edge from uncommon
                    for i in range(0, 64, 4):
                        ang = 2 * math.pi * i / 64
                        p.px(round(cx - .5 + (r - 1.6) * math.cos(ang)), round(cy - .5 + (r - 1.6) * math.sin(ang)),
                             ramp[6])
                p.sprite(cx - 3, cy - 3, glyph(a.icon), {"#": ink})
                if t >= 3:
                    self._glint(p, motion, face - enamel, ramp, "a")
                if t >= 4:
                    self._twinkles(p, motion, [(cx - r - 8, cy - r + 1, False), (cx + r + 3, cy - r + 2, True)], ramp)
            y = name_y
            for line, track in lines:
                w = tw(line, "35", 1, track)
                p.text(round(p.w / 2 - w / 2), y, line, k["body"] if earned else k["muted"], "35", 1, track=track)
                y += 6
            self._line(p, room, cap_y, cap, k["accent"] if earned else k["muted"], p.w / 2)
            return p
        return self._trophy_file(draw, pin_label(a, cur), night)

    def trophy_level(self, cores, values, ach, curs, subject: str, foot: tuple, night: bool) -> str | None:
        """The level card: the case's level struck in a hexagon with the ring of its progress round it, the
        case's name, its XP and how complete it is, and the streak or the release under them."""
        st = level_stats(cores, values, ach, curs)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(LEVEL, night)
            room = self._trophy_room(p)
            k = self.ink(night)
            metals = self.trophy_metals()
            ramp = metals[st["bt"]]
            cx, cy = room.x0 + 32, (room.y0 + room.y1) // 2
            for i in range(200):   # the ring of the level's progress
                ang = 2 * math.pi * i / 200 - math.pi / 2
                x, y = round(cx - .5 + 29 * math.cos(ang)), round(cy - .5 + 29 * math.sin(ang))
                c = k["accent"] if i / 200 < st["lp"] else k["dim"]
                p.px(x, y, c)
                p.px(x + (1 if math.cos(ang) > 0 else 0), y, c)
            cells, rim = set(), set()
            R = 25
            for y in range(cy - R - 1, cy + R + 2):
                for x in range(cx - R, cx + R + 1):
                    px_, py_ = x + .5, y + .5
                    if not hex_in(px_, py_, cx, cy, R):
                        continue
                    cells.add((x, y))
                    if hex_in(px_, py_, cx, cy, R - 4.5):
                        continue
                    rim.add((x, y))
                    a_ = math.degrees(math.atan2(py_ - cy, px_ - cx)) % 360
                    face = math.radians(round(a_ / 60) * 60 % 360)
                    v = 3.4 + 2.6 * lit(math.cos(face), math.sin(face))
                    p.px(x, y, ramp[tone(v, x, y)] if not hex_in(px_, py_, cx, cy, R - 3.4) else ramp[0])
            field = cells - rim
            xs, ys = [x for x, _ in field], [y for _, y in field]
            plate = Pix(max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
            self.tag(plate, 0, 0, plate.w, plate.h, night)
            for (x, y) in field:
                p.px(x, y, plate.get(x - min(xs), y - min(ys)) or k["tag"])
            outline(p, cells, ramp, cx, cy)
            centred(p, cx, cy - 11, "LEVEL", k["tag_ink"], "35")
            level = str(st["L"])
            scale = 2 if tw(level, "57", 2) <= 30 else 1
            centred(p, cx, cy - 4 + (0 if scale == 2 else 3), level, k["tag_ink"], "57", scale)
            if st["bt"] >= 3:
                self._glint(p, motion, rim, ramp, "l")
            p.vline(cx + 35, room.y0, room.y1, k["rule"])
            x0, right = cx + 41, room.x1 - 2
            room_w = right - x0
            ty = room.y0 + 3
            title = case_title(subject)
            title_w = min(right, room.span(ty - 1, 9)[1] - 2) - x0     # its row may reach a corner piece
            font = "57" if tw(title, "57") <= title_w else "35"
            p.text(x0, ty, clip(title, title_w, font), k["title"], font)
            togo = fmt(level_xp(st['L'] + 1) - st['xp'])
            xp = [f"LEVEL {st['L']} · {fmt(st['xp'])} XP · {togo} TO LEVEL {st['L'] + 1}",
                  f"LEVEL {st['L']} · {fmt(st['xp'])} XP · {togo} TO GO", f"LEVEL {st['L']} · {fmt(st['xp'])} XP"]
            p.text(x0, ty + 11, next((s for s in xp if tw(s, "35") <= room_w), xp[-1]), k["muted"], "35")
            self._bar(p, x0, ty + 18, room_w, st["lp"], night)
            done = round(st["completion"] * 100)
            case = [f"CASE {done}% COMPLETE · {st['earned']} OF {len(ach)} ACHIEVEMENTS",
                    f"CASE {done}% COMPLETE · {st['earned']} OF {len(ach)}", f"CASE {done}% COMPLETE"] if ach else \
                [f"CASE {done}% COMPLETE"]
            p.text(x0, ty + 26, next((s for s in case if tw(s, "35") <= room_w), case[-1]), k["muted"], "35")
            self._bar(p, x0, ty + 33, room_w, st["completion"], night, self._tint(4, night))
            self.tag(p, x0, ty + 42, 11, 11, night)
            p.sprite(x0 + 2, ty + 44, glyph(foot[0]), {"#": k["tag_ink"]})
            head = foot[2]
            p.text(x0 + 15, ty + 45, head, k["body"], "35")
            tail = foot[3].strip()
            if tail and x0 + 15 + tw(head, "35") + 4 + tw(tail, "35") <= right:
                p.text(x0 + 15 + tw(head, "35") + 4, ty + 45, tail, k["muted"], "35")
            if st["bt"] >= 4:
                self._twinkles(p, motion, [(cx - 27, cy - 27, True), (cx + 24, cy + 21, False)], ramp)
            return p
        return self._trophy_file(draw, level_label(st, subject, foot), night)

    def trophy_next_up(self, cores, values, ach, curs, night: bool) -> str | None:
        """The next-up card: the three things nearest their next step, each with its progress and what is left."""
        items = next_up_items(cores, values, ach, curs)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(NEXT, night)
            room = self._trophy_room(p)
            k = self.ink(night)
            y, under = self._top_row(room, night)
            x0, _ = room.span(room.y0, under - room.y0)
            lead = self._tag_reach(tw("NEXT UP", "35") + 8, night)[0]
            self._tagged(p, x0 + 1 + lead, y, "NEXT UP", night)
            left, right = room.x0 + 1, room.x1 - 3
            first = under + 3
            last = room.foot - 13                         # the last row an item may start on, its words clear
            if left + 1 < room.corner:                    # and its icon clear of the corner piece below it
                last = min(last, p.h - room.corner - 11)
            step = min(18, (last - first) // 2)
            for i, it in enumerate(items):
                y = first + i * step
                block, ink = self.trophy_enamel(it["hue"])
                p.rect(left + 1, y, 11, 11, block)
                p.sprite(left + 3, y + 2, glyph(it["icon"]), {"#": ink})
                pct = f"{int(it['pct'] * 100)}%"
                tx = left + 16
                room_w = right - tw(pct, "35") - 4 - tx
                p.text(tx, y, clip(it["name"].upper(), room_w, "35"), k["body"], "35")
                p.text(right - tw(pct, "35"), y, pct, k["muted"], "35")
                self._bar(p, tx, y + 6, right - tx, it["pct"], night, None, 2)
                p.text(tx, y + 9, clip(it["left"].upper(), right - tx, "35"), k["muted"], "35")
            return p
        return self._trophy_file(draw, next_up_label(items), night)
