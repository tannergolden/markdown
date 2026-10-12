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
               light, so gold is gold in every set. Unranked is a ghost, its
               outline dotted where it will stand. Gold glints; platinum
               gains its ornament and its sparkles, diamond its prism and its
               stars, as the standard look does
  progress     a bar along the card's foot, filled as far as the next tier
  the hand     a collection's design letters every word in its hand's two
               inks on its own ground, so its trophies keep the hand too

The metals are the case's own colours: a set's trophy files keep to its closed
palette and the five metals beside it (`trophy_tokens`). A set can strike its
trophies in metals of its own (`trophy_metals`), stand them on another ground
(`trophy_ground`) and engrave its tiers on another plate (`trophy_plate`).

A card's motion is its own, in CSS rather than the engine's SMIL, so it holds
still for a reader who asks for reduced motion even though a trophy has no
still file: a glint passes across a gold trophy, in the engine's discrete
steps, and a platinum one's sparkles twinkle on the engine's cadence. A
collection's design glints on its hand's period.
"""
from __future__ import annotations

import math

from ... import KIT, KIT_VERSION
from ...canvas import BUDGET
from ...trophies.art import (alt_text, case_title, fmt, level_label, level_stats, level_xp, next_up_items,
                             next_up_label, pct_label, pin_caption, pin_label, status_text, top_pct)
from ...trophies.catalogue import TIER_NAMES, ach_state, measure
from ..pixel import GLYPHS, LX, LY, LZ, MISSING, Pix, clip, fold, make_ramp, measure as tw, tube, wrap
from .badges import nearest

# The case's metals, one seven-tone ramp for each tier on the engine's light, dark to light: bronze, silver,
# gold, platinum and diamond. Diamond catches the light in two more, its prism.
METALS = {
    1: make_ramp("#B4703A"),
    2: make_ramp("#A8B3C0"),
    3: make_ramp("#E3A62A"),
    4: make_ramp("#93C6E4"),
    5: make_ramp("#6FC2F0"),
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

CARD, PIN, LEVEL, NEXT, PLAQUE = (82, 111), (52, 62), (210, 76), (164, 76), (132, 44)
EDGE = 5    # how far inside the canvas a card's content keeps, clear of the set's frame
TAG = 9     # a tag's height, as every set draws one, its letters two rows in and four along
ART = EDGE + TAG + 1    # the row a card's trophy starts at: the rows above it are its tags', the rank's and NEW's


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


def ghost(p: Pix, cells, colour: str, cx: float, cy: float):
    """An unranked trophy's outline, dashed where it will stand: every other short arc of the pixels round
    `cells`, by their angle about (cx, cy), so a slanted edge is dashed as a straight one is."""
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cells:
                continue
            a = math.degrees(math.atan2(q[1] + .5 - cy, q[0] + .5 - cx)) % 360
            if int(a / 10) % 2 == 0:
                p.px(q[0], q[1], colour)


def lines_of(name: str, room: int) -> list[tuple[str, int]]:
    """A name set in the small capitals on at most two lines of `room`, as (line, tracking): broken at its spaces
    and hyphens, a word too wide for a line set tighter, and cut only if even that cannot fit it."""
    words, out, cur = fold(name.upper(), "35").replace("-", "- ").split(), [], ""
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
    def trophy_metals(self) -> dict:
        """The ramps a trophy is struck in, by tier, 1 for bronze to 5 for diamond."""
        return METALS

    def trophy_ground(self, p: Pix, night: bool):
        """What a card stands on: the set's paper, by night its sky with a few faint stars, inside its frame."""
        self.paper(p, night, uid="tg")
        if night:
            self.stars(p, EDGE + 2, EDGE + 2, p.w - EDGE - 2, p.h - EDGE - 2, max(4, p.w * p.h // 900), seed=7,
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

    def _shine(self, p: Pix, cx: float, cy: float, r: float, ramp: list, t: int, night: bool):
        """The light a trophy throws round itself, as a lamp's halo: stepped, strongest at its middle, by night
        from bronze and by day from gold, laid on the ground only, so it never tints the trophy or a word."""
        if not t or (not night and t < 3):
            return
        alphas = (.05, .09, .14) if night else (.04, .07, .1)
        p.halo(cx, cy, r, r * .92, ramp[5 if night else 4], alphas=alphas, L="base",
               only=getattr(p, "ground", None) or set(), shape=False)

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
        """A glint across a trophy: a band of light two pixels wide that steps across it, clipped to its shape."""
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

    def _rank(self, p: Pix, core, m: dict, o: dict, night: bool):
        """The card's rank, TOP 2.8%, on a tag at the top left."""
        if o.get("rank") and m["t"]:
            self._tagged(p, EDGE, EDGE, pct_label(top_pct(core, m["v"])), night)

    def _new(self, p: Pix, m: dict, o: dict, night: bool, right: int):
        """A tier newly reached: NEW on a tag at the top right."""
        if o.get("new") and m["t"]:
            self._tagged(p, right - tw("NEW", "35") - 8, EDGE, "NEW", night)

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
                p.sprite(x, y, DIAMOND, {"#": ramp[4]})
                p.px(x + 2, y + 1, ramp[6])
                p.px(x + 2, y + 3, ramp[2])
            elif m["t"] == i:
                p.sprite(x, y, ["..#..", ".#.#.", "#...#", ".#.#.", "..#.."], {"#": k["accent"]})
            else:
                p.sprite(x, y, ["..#..", ".....", "#...#", ".....", "..#.."], {"#": k["muted"]})
            x += 7
        x += 2
        for _ in range(stars):
            p.sprite(x, y, STAR, {"#": metals[5][5]})
            x += 6

    def _footer(self, p: Pix, core, m: dict, o: dict, night: bool, kind: str, top: int):
        """A card's foot: the trophy's name, its value and how it moved this week, its progress, and where it
        stands."""
        k = self.ink(night)
        W = p.w
        centred(p, W / 2, top, core.title.upper(), k["muted"], "35")
        vs = fmt(m["v"])
        delta = o.get("delta")
        extra = (tw(fmt(delta), "35") + 6) if delta else 0
        scale = 2 if tw(vs, "57", 2) + extra <= W - 2 * EDGE - 6 else 1
        vw = tw(vs, "57", scale)
        unit = core.unit.upper() if core.unit else ""
        uw = tw(unit, "35") + 2 if unit else 0
        x = round(W / 2 - (vw + uw + extra) / 2)
        vy = top + 8 + (0 if scale == 2 else 4)
        p.text(x, vy, vs, k["body"], "57", scale)
        if unit:
            p.text(x + vw + 2, vy + 7 * scale - 5, unit, k["muted"], "35")
        if delta:
            dx = x + vw + uw + 3
            p.sprite(dx, vy + 1, UP, {"#": k["accent"]})
            p.text(dx + 4, vy, fmt(delta), k["accent"], "35")
        bar_y = top + 24
        metals = self.trophy_metals()
        nxt = metals[min(5, m["t"] + 1)]
        if kind == "bar":
            self._bar(p, EDGE + 4, bar_y, W - 2 * EDGE - 8, m["pct"] if m["next"] else 1.0, night, nxt[4])
        elif kind == "seg":
            room = W - 2 * EDGE - 8
            sw = (room - 4 * 2) // 5
            x0 = round(W / 2 - (5 * sw + 8) / 2)
            for i in range(5):
                share = 1 if m["t"] > i else (m["pct"] if m["t"] == i else 0)
                self._bar(p, x0 + i * (sw + 2), bar_y, sw, share, night, metals[i + 1][4])
        status = status_text(m)
        if tw(status, "35") > W - 2 * EDGE - 2:
            status = clip(status, W - 2 * EDGE - 2, "35")
        centred(p, W / 2, top + (29 if kind != "none" else 27), status, k["muted"], "35")

    # ------------------------------------------------------------------------------------ the trophies
    def _cup(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int = 41, top: int = ART + 3):
        """The trophy, a cup: a turned bowl on its stem and foot, two handles, the trophy's enamel on its bowl, on
        a plinth whose plate is engraved with its tier."""
        t, k = m["t"], self.ink(night)
        R, H = 17, 24
        rows = []
        for i in range(H + 1):
            hw = max(2.6, R * max(0.0, 1 - (i / H) ** 2.4) ** .55)
            rows.append((top + i, round(hw)))
        stem = [(top + H + 1 + i, 2 if i != 2 else 3) for i in range(5)]
        foot = [(top + H + 6 + i, 4 + i * 2) for i in range(4)]
        shape = {(x, y) for y, n in rows + stem + foot for x in range(cx - n, cx + n)}
        if t == 0:
            ghost(p, shape, k["muted"], cx, top + 14)
            for side in (-1, 1):
                for i in range(12):
                    a = math.radians(-90 + i * 15)
                    hx, hy = cx + side * (R + 1 + 4.5 * math.cos(a)), top + 9 + 6.5 * math.sin(a)
                    if i % 2 == 0:
                        p.px(round(hx) - (1 if side < 0 else 0), round(hy), k["muted"])
            p.sprite(cx - 4, top + 8, glyph(core.icon), {"#": k["muted"]})
        else:
            ramp = self.trophy_metals()[t]
            for side in (-1, 1):   # the handles, as tubes on the same light
                path = [(cx + side * (R - 1), top + 3), (cx + side * (R + 3), top + 2.5), (cx + side * (R + 6), top + 5.5),
                        (cx + side * (R + 6), top + 10), (cx + side * (R + 3), top + 14.5), (cx + side * (R - 3), top + 17)]
                tube(p, path, 1.5, lambda s, o, lam, x, y: ramp[max(1, min(6, 1 + round(5 * lam)))], outline=ramp[0])
            for (x, y) in shape:
                n = dict(rows + stem + foot)[y]
                nx = (x + .5 - cx) / max(1, n)
                nz = math.sqrt(max(0.0, 1 - nx * nx))
                lam = max(0.0, nx * LX + nz * LZ + .1)
                v = 1.2 + 4.6 * lam ** 1.15
                if abs(nx + .45) < .14 and y < top + H - 3:
                    v = 6.2     # the glint down the bowl where the lamp lands
                p.px(x, y, ramp[tone(v, x, y, 1, 6)])
            # The rim, and the cup's inside in shadow.
            rim = set()
            for y in range(top - 3, top + 3):
                for x in range(cx - R - 1, cx + R + 1):
                    d = ((x + .5 - cx) / (R + .5)) ** 2 + ((y + .5 - top) / 2.6) ** 2
                    if d > 1:
                        continue
                    rim.add((x, y))
                    inside = ((x + .5 - cx) / (R - 2.5)) ** 2 + ((y + .5 - top + .3) / 1.5) ** 2 <= 1
                    if inside:
                        p.px(x, y, ramp[1] if y >= top - 1 else ramp[2])
                    else:
                        p.px(x, y, ramp[6] if x < cx - 3 and y < top else ramp[5] if x < cx + 6 else ramp[3])
            outline(p, shape | rim, ramp, cx, top + 14)
            # The enamel, a disc on the bowl, its icon cut in the enamel's ink.
            block, ink = self.trophy_enamel(core.hue)
            ey = top + 11
            for y in range(ey - 7, ey + 7):
                for x in range(cx - 7, cx + 7):
                    d = math.hypot(x + .5 - cx, y + .5 - ey)
                    if d <= 5.4:
                        p.px(x, y, block)
                    elif d <= 6.6:
                        p.px(x, y, ramp[1] if lit(x + .5 - cx, y + .5 - ey) < 0 else ramp[5])
            p.sprite(cx - 4, ey - 4, glyph(core.icon), {"#": ink})
            self._shine(p, cx, top + 14, 30, ramp, t, night)
            if t >= 3:
                self._glint(p, motion, shape, ramp, "c")
            if t >= 5:
                for (x, y) in ((cx - 12, top + 6), (cx - 9, top + 15), (cx + 10, top + 4)):
                    p.px(x, y, PRISM[0][5])
                    p.px(x + 1, y, PRISM[1][5])
        # The plinth, in the set's own card, and the plate its tier is engraved on.
        py = top + H + 10
        light, dark = self.card_bevel(night)
        for (x0, y0, w, h) in ((cx - 15, py, 30, 2), (cx - 22, py + 2, 44, TAG + 2)):
            p.rect(x0, y0, w, h, k["fill"])
            p.bevel(x0, y0, w, h, light, dark)
            p.box(x0 - 1, y0 - 1, w + 2, h + 2, k["rule"], notch=True)
        self._plate(p, cx, py + 3, TIER_NAMES[t].upper(), night, 0)
        if t >= 4:
            ramp = self.trophy_metals()[t]
            self._twinkles(p, motion, [(cx - 32, top + 1, True), (cx + 27, top + 1, False), (cx + 27, top + 21, True),
                                       (cx - 31, top + 24, False)] + ([(cx - 30, top + 12, False)] if t == 5 else []),
                           ramp)
        return py + 11

    def _crest(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int = 41, cy: int = ART + 23):
        """The crest: a hexagon, its frame bevelled in the tier's metal round the trophy's enamel, on a banner
        engraved with its tier; rivets from silver, a gem from gold, wings from platinum and a crown at diamond."""
        t, k = m["t"], self.ink(night)
        R, rim = 19, 4.5
        if t == 0:
            ghost(p, {(x, y) for y in range(cy - R - 1, cy + R + 2) for x in range(cx - R, cx + R + 1)
                      if hex_in(x + .5, y + .5, cx, cy, R)}, k["muted"], cx, cy)
            p.sprite(cx - 7, cy - 7, glyph(core.icon), {"#": k["muted"]}, 2)
            self._plate(p, cx, cy + R + 1, "UNRANKED", night)
            return cy + R + 1 + TAG
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
        cells = set()
        block, ink = self.trophy_enamel(core.hue)
        for y in range(cy - R - 1, cy + R + 2):
            for x in range(cx - R, cx + R + 1):
                px_, py_ = x + .5, y + .5
                if not hex_in(px_, py_, cx, cy, R):
                    continue
                cells.add((x, y))
                if hex_in(px_, py_, cx, cy, R - rim):
                    p.px(x, y, block)
                    continue
                a = math.degrees(math.atan2(py_ - cy, px_ - cx)) % 360
                face = math.radians(round(a / 60) * 60 % 360)
                v = 3.4 + 2.6 * lit(math.cos(face), math.sin(face))
                if not hex_in(px_, py_, cx, cy, R - rim + 1.1):
                    p.px(x, y, ramp[tone(v, x, y, 1, 6)])
                else:
                    p.px(x, y, ramp[0])
        outline(p, cells, ramp, cx, cy)
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
            crown = ["#..#..#", "#.###.#", "#######", ".#####."]
            cells_ = {(cx - 4 + i, cy - R - 4 + j) for j, row in enumerate(crown) for i, ch in enumerate(row) if ch == "#"}
            for (x, y) in cells_:
                p.px(x, y, ramp[tone(5.2 - (y - (cy - R - 4)) * .7 - (x - cx) * .12, x, y, 1, 6)])
            outline(p, cells_, ramp, cx, cy - R - 2)
            for x, c in ((cx - 4, PRISM[0][5]), (cx - 1, PRISM[1][5]), (cx + 2, PRISM[0][5])):
                p.px(x, cy - R - 4, c)
        if t >= 3:
            self._glint(p, motion, cells, ramp, "h")
        # The banner: its tails folded behind in the metal, the tier on the set's plate across it.
        by = cy + R + 1
        for side in (-1, 1):
            for j in range(7):
                for i in range(9):
                    x = cx + side * (17 + i) - (1 if side < 0 else 0)
                    if i >= 7 and abs(j - 3) < (i - 6):
                        continue
                    p.px(x, by + 3 + j, ramp[2] if j else ramp[3])
                p.px(cx + side * 17 - (1 if side < 0 else 0), by + 3 + j, ramp[0])
        self._plate(p, cx, by, TIER_NAMES[t].upper(), night, m["stars"])
        if t >= 4:
            self._twinkles(p, motion, [(cx - 33, cy - 20, True), (cx + 28, cy - 20, False), (cx + 28, cy + 12, True),
                                       (cx - 31, cy + 14, False)], ramp)
        return by + TAG

    def _medallion(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int = 41, cy: int = ART + 23):
        """The medallion: a struck medal on its ribbon, its laurel round the trophy's icon, the ring round it
        filled as far as the next tier, and its tier on a plate below."""
        t, k = m["t"], self.ink(night)
        metals = self.trophy_metals()
        block, ink = self.trophy_enamel(core.hue)
        # The ribbon: two straps from the top, the far one in shadow, each with its stripe.
        for side, shade in ((-1, True), (1, False)):
            for y in range(ART, cy - 8):
                f = (y - ART) / max(1, cy - 8 - ART)
                xa = cx + side * round(16 - 13 * f) - (0 if side > 0 else 1)
                for i in range(8):
                    x = xa - side * i
                    p.px(x, y, (block if 2 <= i <= 5 else k["accent"]) if t else k["dim"])
                    if shade:
                        p.apx(x, y, metals[1][0], .35)
        R = 18
        p_ = m["pct"] if m["next"] else 1.0
        nxt = metals[min(5, t + 1)]
        for i in range(160):   # the ring round the medal, filled as far as it has got
            a = 2 * math.pi * i / 160 - math.pi / 2
            x, y = round(cx - .5 + R * math.cos(a)), round(cy - .5 + R * math.sin(a))
            p.px(x, y, nxt[4] if i / 160 < p_ else k["dim"])
        if t == 0:
            ghost(p, {(x, y) for y in range(cy - 16, cy + 16) for x in range(cx - 16, cx + 16)
                      if math.hypot(x + .5 - cx, y + .5 - cy) <= 14.5}, k["muted"], cx, cy)
            p.sprite(cx - 4, cy - 4, glyph(core.icon), {"#": k["muted"]})
            self._plate(p, cx, cy + R + 2, "UNRANKED", night)
            return cy + R + 2 + TAG
        ramp = metals[t]
        cells = set()
        for y in range(cy - 16, cy + 16):
            for x in range(cx - 16, cx + 16):
                dx, dy = x + .5 - cx, y + .5 - cy
                d = math.hypot(dx, dy)
                if d > 15:
                    continue
                cells.add((x, y))
                if d > 12.6:
                    v = 3.4 + 2.6 * lit(dx / d, dy / d)
                elif d > 11.6:
                    v = 3.4 - 2.2 * lit(dx / d, dy / d)
                else:
                    v = 4.2 + 1.5 * lit(dx / 12, dy / 12)
                p.px(x, y, ramp[tone(v, x, y, 1, 6)])
        outline(p, cells, ramp, cx, cy)
        self._shine(p, cx, cy, 28, ramp, t, night)
        for side in (-1, 1):   # the laurel: a sprig of leaves up each side of the face
            for i in range(6):
                a = math.radians(110 + i * 24) if side < 0 else math.radians(70 - i * 24)
                x, y = round(cx - .5 + 9.6 * math.cos(a)), round(cy - .5 + 9.6 * math.sin(a))
                p.px(x, y, ramp[2])
                p.px(x + side, y - 1, ramp[2])
                p.px(x - side, y + 1, ramp[5])
        g = glyph(core.icon)
        p.sprite(cx - 3, cy - 3, g, {"#": ramp[6]})
        p.sprite(cx - 4, cy - 4, g, {"#": ramp[0]})
        if t >= 3:
            self._glint(p, motion, cells, ramp, "m")
        if t >= 4:
            self._twinkles(p, motion, [(cx - 33, cy - 21, True), (cx + 28, cy - 21, False), (cx + 27, cy + 8, True),
                                       (cx - 31, cy + 10, False)], ramp)
        self._plate(p, cx, cy + R + 2, TIER_NAMES[t].upper(), night, m["stars"])
        return cy + R + 2 + TAG

    def _crystal(self, p: Pix, motion: Motion, core, m: dict, night: bool, cx: int = 41):
        """The crystal: cut in the tier's metal, lit from within as far as its progress, its facets shaded by the
        lamp, its shards about it, rings round it from platinum, and its tier on a plate below."""
        t, k = m["t"], self.ink(night)
        V = {"T": (41, ART), "LS": (29, 27), "FL": (36, 25), "FR": (46, 25), "RS": (53, 27), "LB": (31, 47),
             "BL": (37, 50), "BR": (45, 50), "RB": (51, 47), "B": (41, 58)}
        faces = [(("LS", "FL", "BL", "LB"), 4.6), (("FL", "FR", "BR", "BL"), 3.6), (("FR", "RS", "RB", "BR"), 2.2),
                 (("T", "LS", "FL"), 5.6), (("T", "FL", "FR"), 4.8), (("T", "FR", "RS"), 3.0),
                 (("LB", "BL", "B"), 2.6), (("BL", "BR", "B"), 2.0), (("BR", "RB", "B"), 1.4)]

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
        for y in range(ART - 1, 61):
            for x in range(27, 56):
                for keys, v in faces:
                    if inside(x + .5, y + .5, keys):
                        cells[(x, y)] = v
                        break
        share = 1.0 if t == 5 else m["pct"]
        level = round(58 - share * (58 - ART))
        if t == 0:
            ghost(p, set(cells), k["muted"], cx, 36)
            p.sprite(cx - 4, 33, glyph(core.icon), {"#": k["muted"]})
            self._plate(p, cx, 61, "UNRANKED", night)
            return 61 + TAG
        ramp = self.trophy_metals()[t]
        if t >= 4:   # a ring round it, its far half behind
            for i in range(120):
                a = 2 * math.pi * i / 120
                x, y = round(cx - .5 + 19 * math.cos(a)), round(36 + 4.5 * math.sin(a))
                if math.sin(a) < 0:
                    p.px(x, y, ramp[3])
        for (x, y), v in cells.items():
            lift = 1.6 if y >= level else 0
            p.px(x, y, ramp[tone(v + lift, x, y, 1, 6)])
        if 0 < share < 1:
            for x in range(27, 56):
                if (x, level) in cells:
                    p.px(x, level, ramp[6])
        outline(p, set(cells), ramp, cx, 36)
        self._shine(p, cx, 37, 27, ramp, t, night)
        for a_, b_ in (("T", "FL"), ("FL", "BL"), ("T", "FR")):
            (ax, ay), (bx, by) = V[a_], V[b_]
            n = max(abs(bx - ax), abs(by - ay))
            for i in range(n + 1):
                x, y = round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n)
                if (x, y) in cells:
                    p.px(x, y, ramp[6] if a_ == "T" else ramp[5])
        g = glyph(core.icon)
        p.sprite(cx - 3, 34, g, {"#": ramp[1]})
        p.sprite(cx - 4, 33, g, {"#": ramp[6]})
        for (sx, sy) in ((18, 18), (62, 21), (60, 49), (20, 45)):   # shards
            p.sprite(sx, sy, [".#", "##", "#."], {"#": ramp[4]})
            p.px(sx, sy + 1, ramp[6])
        if t >= 4:   # and its near half in front
            for i in range(120):
                a = 2 * math.pi * i / 120
                x, y = round(cx - .5 + 19 * math.cos(a)), round(36 + 4.5 * math.sin(a))
                if math.sin(a) >= 0:
                    p.px(x, y, ramp[6] if math.cos(a) < 0 else ramp[4])
            self._twinkles(p, motion, [(10, 24, True), (67, 28, False), (64, 53, True), (12, 53, False)], ramp)
        if t >= 3:
            self._glint(p, motion, set(cells), ramp, "x")
        self._plate(p, cx, 61, TIER_NAMES[t].upper(), night, m["stars"])
        return 61 + TAG

    # ------------------------------------------------------------------------------------ the entry points
    def trophy_card(self, style: str, core, value: int, o: dict, night: bool) -> str | None:
        """One core trophy's card in `style`, as the set draws it; None when the set cannot letter it."""
        m = measure(core, value)
        if style == "plaque":
            return self._trophy_file(lambda motion: self._plaque(motion, core, m, o, night), alt_text(core, m, o),
                                     night)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(CARD, night)
            art = {"trophy": self._cup, "crest": self._crest, "medallion": self._medallion,
                   "crystal": self._crystal}[style]
            art(p, motion, core, m, night)
            if style == "trophy":
                self._pips(p, p.w / 2, 65, m, night)
            self._rank(p, core, m, o, night)
            self._new(p, m, o, night, p.w - EDGE - 1)
            kind = {"trophy": "bar", "crest": "seg"}.get(style, "none")
            self._footer(p, core, m, o, night, kind, 72)
            return p
        return self._trophy_file(draw, alt_text(core, m, o), night)

    def _plaque(self, motion: Motion, core, m: dict, o: dict, night: bool) -> Pix:
        """The plaque, a plate across the row: its tier's metal at the left with a trophy struck in it, then the
        trophy's name, its tier, its value and its progress."""
        t, k = m["t"], self.ink(night)
        p = self._card_canvas(PLAQUE, night)
        W, H = p.w, p.h
        x0, y0, x1, y1 = EDGE, EDGE, 37, H - EDGE
        cells = {(x, y) for x in range(x0, x1) for y in range(y0, y1)}
        if t:
            ramp = self.trophy_metals()[t]
            for (x, y) in cells:
                v = 4.2 + (1.2 if (y - y0) % 4 == 0 else 0) - .9 * (x - x0) / (x1 - x0) - .6 * (y - y0) / (y1 - y0)
                p.px(x, y, ramp[tone(v, x, y, 1, 6)])
            g = glyph("trophy")
            gx, gy = (x0 + x1) // 2 - 7, (y0 + y1) // 2 - 7
            p.sprite(gx + 1, gy + 1, g, {"#": ramp[6]}, 2)
            p.sprite(gx, gy, g, {"#": ramp[0]}, 2)
            if t >= 3:
                self._glint(p, motion, cells, ramp, "p")
            if t >= 4:
                self._twinkles(p, motion, [(x0 + 1, y0 + 1, False), (x1 - 6, y1 - 6, True)], ramp)
        else:
            for x in range(x0, x1):
                for y in range(y0, y1):
                    if (x in (x0, x1 - 1) or y in (y0, y1 - 1)) and (x + y) % 2 == 0:
                        p.px(x, y, k["muted"])
            p.sprite((x0 + x1) // 2 - 7, (y0 + y1) // 2 - 7, glyph("trophy"), {"#": k["muted"]}, 2)
        p.vline(x1, y0, y1, k["rule"])
        block, ink = self.trophy_enamel(core.hue)
        p.rect(x1 + 4, y0, 9, 9, block)
        p.sprite(x1 + 5, y0 + 1, glyph(core.icon), {"#": ink})
        p.text(x1 + 16, y0 + 2, core.title.upper(), k["muted"], "35")
        right = W - EDGE - 2
        word = TIER_NAMES[t].upper()
        ww = tw(word, "35") + 6
        self._tagged(p, right - ww - 2, y0, word, night, plate=True)
        # The value on a row of its own, as big as it fits, how it moved this week and NEW beside it; under it how
        # far it is to the next tier, and the rank where there is room; and the five tiers along the foot.
        vs = fmt(m["v"])
        room = right - (x1 + 4)
        scale = 2 if tw(vs, "57", 2) <= room - 20 else 1
        vy = y0 + 10 + (0 if scale == 2 else 4)
        p.text(x1 + 4, vy, vs, k["body"], "57", scale)
        delta = o.get("delta")
        if delta:
            dx = x1 + 4 + tw(vs, "57", scale) + 3
            p.sprite(dx, vy + 1, UP, {"#": k["accent"]})
            p.text(dx + 4, vy, fmt(delta), k["accent"], "35")
        if o.get("new") and t:
            self._tagged(p, right - tw("NEW", "35") - 8, vy + 7 * scale - TAG, "NEW", night)
        status = clip(status_text(m), room, "35")
        sy = y0 + 25
        p.text(x1 + 4, sy, status, k["muted"], "35")
        if o.get("rank") and t:
            rank = pct_label(top_pct(core, m["v"]))
            if tw(status, "35") + 6 + tw(rank, "35") <= room:
                p.text(right - tw(rank, "35"), sy, rank, k["muted"], "35")
        sw = (room - 8) // 5
        metals = self.trophy_metals()
        for i in range(5):
            share = 1 if t > i else (m["pct"] if t == i else 0)
            self._bar(p, x1 + 4 + i * (sw + 2), H - EDGE - 3, sw, share, night, metals[i + 1][4], 2)
        for i in range(m["stars"]):
            p.sprite(right - ww - 9 - i * 6, y0 + 2, SMALL_STAR, {"#": metals[5][5]})
        return p

    def trophy_pin(self, a, cur, night: bool) -> str | None:
        """One achievement's pin, as the set draws it; None when the set cannot letter it."""
        st = ach_state(a, cur)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(PIN, night)
            k = self.ink(night)
            metals = self.trophy_metals()
            cx, cy = 26, 20
            earned, secret = st["earned"], st["secret"]
            t = st["rarity"] if earned else 0
            share = 1.0 if st["done"] else st["pct"]
            if not secret and not st["done"]:   # how far along, as a ring round the pin
                nxt = metals[st["next_rarity"] or 1]
                for i in range(120):
                    ang = 2 * math.pi * i / 120 - math.pi / 2
                    x, y = round(cx - .5 + 15.5 * math.cos(ang)), round(cy - .5 + 15.5 * math.sin(ang))
                    p.px(x, y, nxt[4] if i / 120 < share else k["dim"])
            if secret or not earned:
                ghost(p, {(x, y) for y in range(cy - 14, cy + 14) for x in range(cx - 14, cx + 14)
                          if math.hypot(x + .5 - cx, y + .5 - cy) <= 12}, k["muted"], cx, cy)
                p.sprite(cx - 4, cy - 4, glyph("q" if secret else a.icon), {"#": k["muted"]})
            else:
                ramp = metals[t]
                block, ink = self.trophy_enamel(a.hue)
                cells = set()
                for y in range(cy - 14, cy + 14):
                    for x in range(cx - 14, cx + 14):
                        dx, dy = x + .5 - cx, y + .5 - cy
                        d = math.hypot(dx, dy)
                        if d > 13:
                            continue
                        cells.add((x, y))
                        if d <= 8.6:
                            p.px(x, y, block)
                        elif d <= 9.6:
                            p.px(x, y, ramp[1])
                        else:
                            p.px(x, y, ramp[tone(3.4 + 2.6 * lit(dx / d, dy / d), x, y, 1, 6)])
                outline(p, cells, ramp, cx, cy)
                if t >= 2:   # a reeded edge from uncommon
                    for i in range(0, 64, 4):
                        ang = 2 * math.pi * i / 64
                        p.px(round(cx - .5 + 11.4 * math.cos(ang)), round(cy - .5 + 11.4 * math.sin(ang)), ramp[6])
                p.sprite(cx - 4, cy - 4, glyph(a.icon), {"#": ink})
                if t >= 3:
                    self._glint(p, motion, cells, ramp, "a")
                if t >= 4:
                    self._twinkles(p, motion, [(EDGE + 1, EDGE + 1, False), (p.w - EDGE - 6, EDGE + 2, True)], ramp)
            name = "???" if secret else a.name + (f" {st['tier']}" if st["tier"] else "")
            room = p.w - 2 * EDGE + 2
            lines = lines_of(name, room)
            y = 38 + (0 if len(lines) > 1 else 3)
            for line, track in lines:
                w = tw(line, "35", 1, track)
                p.text(round(p.w / 2 - w / 2), y, line, k["body"] if earned else k["muted"], "35", 1, track=track)
                y += 6
            whole = pin_caption(st)
            cap = next((c for c in (whole, whole.split(" · ")[0], "NOT MEASURED", "UNMEASURED")
                        if tw(c, "35") <= room), clip(whole, room, "35"))
            centred(p, p.w / 2, y + 1, cap, k["accent"] if earned else k["muted"])
            return p
        return self._trophy_file(draw, pin_label(a, cur), night)

    def trophy_level(self, cores, values, ach, curs, subject: str, foot: tuple, night: bool) -> str | None:
        """The level card: the case's level struck in a hexagon with the ring of its progress round it, the
        case's name, its XP and how complete it is, and the streak or the release under them."""
        st = level_stats(cores, values, ach, curs)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(LEVEL, night)
            k = self.ink(night)
            metals = self.trophy_metals()
            ramp = metals[st["bt"]]
            cx, cy = 37, 38
            for i in range(200):   # the ring of the level's progress
                ang = 2 * math.pi * i / 200 - math.pi / 2
                x, y = round(cx - .5 + 29 * math.cos(ang)), round(cy - .5 + 29 * math.sin(ang))
                p.px(x, y, k["accent"] if i / 200 < st["lp"] else k["dim"])
                p.px(x + (1 if math.cos(ang) > 0 else 0), y, k["accent"] if i / 200 < st["lp"] else k["dim"])
            cells = set()
            R = 25
            for y in range(cy - R - 1, cy + R + 2):
                for x in range(cx - R, cx + R + 1):
                    px_, py_ = x + .5, y + .5
                    if not hex_in(px_, py_, cx, cy, R):
                        continue
                    cells.add((x, y))
                    if hex_in(px_, py_, cx, cy, R - 4.5):
                        continue
                    a_ = math.degrees(math.atan2(py_ - cy, px_ - cx)) % 360
                    face = math.radians(round(a_ / 60) * 60 % 360)
                    v = 3.4 + 2.6 * lit(math.cos(face), math.sin(face))
                    p.px(x, y, ramp[tone(v, x, y, 1, 6)] if not hex_in(px_, py_, cx, cy, R - 3.4) else ramp[0])
            field = [(x, y) for (x, y) in cells if hex_in(x + .5, y + .5, cx, cy, R - 4.5)]
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
                self._glint(p, motion, cells, ramp, "l")
            p.vline(72, EDGE + 1, p.h - EDGE - 1, k["rule"])
            x0, right = 78, p.w - EDGE - 2
            room = right - x0
            title = case_title(subject)
            font = "57" if tw(title, "57") <= room else "35"
            p.text(x0, 8, clip(title, room, font), k["title"], font)
            xp = [f"LEVEL {st['L']} · {fmt(st['xp'])} XP · {fmt(level_xp(st['L'] + 1) - st['xp'])} TO LEVEL {st['L'] + 1}",
                  f"LEVEL {st['L']} · {fmt(st['xp'])} XP · {fmt(level_xp(st['L'] + 1) - st['xp'])} TO GO",
                  f"LEVEL {st['L']} · {fmt(st['xp'])} XP"]
            p.text(x0, 19, next((s for s in xp if tw(s, "35") <= room), xp[-1]), k["muted"], "35")
            self._bar(p, x0, 26, room, st["lp"], night)
            done = round(st["completion"] * 100)
            case = [f"CASE {done}% COMPLETE · {st['earned']} OF {len(ach)} ACHIEVEMENTS",
                    f"CASE {done}% COMPLETE · {st['earned']} OF {len(ach)}", f"CASE {done}% COMPLETE"] if ach else \
                [f"CASE {done}% COMPLETE"]
            p.text(x0, 34, next((s for s in case if tw(s, "35") <= room), case[-1]), k["muted"], "35")
            self._bar(p, x0, 41, room, st["completion"], night, metals[4][4])
            self.tag(p, x0, 50, 11, 11, night)
            p.sprite(x0 + 2, 52, glyph(foot[0]), {"#": k["tag_ink"]})
            head = foot[2]
            p.text(x0 + 15, 53, head, k["body"], "35")
            tail = foot[3].strip()
            if tail and x0 + 15 + tw(head, "35") + 4 + tw(tail, "35") <= right:
                p.text(x0 + 15 + tw(head, "35") + 4, 53, tail, k["muted"], "35")
            if st["bt"] >= 4:
                self._twinkles(p, motion, [(EDGE + 2, EDGE + 2, True), (64, 60, False)], ramp)
            return p
        return self._trophy_file(draw, level_label(st, subject, foot), night)

    def trophy_next_up(self, cores, values, ach, curs, night: bool) -> str | None:
        """The next-up card: the three things nearest their next step, each with its progress and what is left."""
        items = next_up_items(cores, values, ach, curs)

        def draw(motion: Motion) -> Pix:
            p = self._card_canvas(NEXT, night)
            k = self.ink(night)
            self._tagged(p, EDGE + 1, EDGE, "NEXT UP", night)
            right = p.w - EDGE - 3
            for i, it in enumerate(items):
                y = 18 + i * 18
                block, ink = self.trophy_enamel(it["hue"])
                p.rect(EDGE + 2, y, 11, 11, block)
                p.sprite(EDGE + 4, y + 2, glyph(it["icon"]), {"#": ink})
                pct = f"{int(it['pct'] * 100)}%"
                room = right - tw(pct, "35") - 4 - (EDGE + 17)
                p.text(EDGE + 17, y, clip(it["name"].upper(), room, "35"), k["body"], "35")
                p.text(right - tw(pct, "35"), y, pct, k["muted"], "35")
                self._bar(p, EDGE + 17, y + 6, right - EDGE - 17, it["pct"], night, None, 2)
                p.text(EDGE + 17, y + 10, clip(it["left"].upper(), right - EDGE - 17, "35"), k["muted"], "35")
            return p
        return self._trophy_file(draw, next_up_label(items), night)
