# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Forge set: the smithy and the armoury, beaten out of iron.

Every sheet is a hammered iron plate framed in riveted bands, with a strip of
mail hung across the top. Titles are polished steel by day and, by night,
iron fresh from the fire, white at the heart and cooling to ember red at the
edges. Headers stand in the smithy: the hearth with its bellows breathing on
one side, and on the other the smith at his anvil, his hammer swinging and
the sparks flying off the blade, a quench bucket steaming beside him and
shields and an axe on the wall. A strip's hero is the armoury's trophy: a
shield bearing the smith's arms, a helm over it and two swords crossed behind
it, as tall as the strip. On a phone each scene stands under the words. By
day the plate is a cool slate lit from above; by night the forge lights it
from below, the fire flickers in the hearth and embers drift up across the
sheet. Rivets stud every rule and every badge; the footers lie on a floor of
the hearth's stone with coal heaped on it and are struck with the smith's
mark; the links are steel tags on rivets.

It is the medieval collection's November, drawn in the collection's hand (see
`collections.hand`): its words are set in the hand's two inks; its plate
falls within the hand's bands, a slate lifted to the hand's day and a night
held between its dark and its warmth; the forge's fire, its coals, its embers,
its sparks and the hot blade burn on the hand's flame, the fire's heart
flickering on the engine's cadence; the smith is drawn to the hand's canon,
twenty-eight rows tall, on the hand's skin; the smith's swing and the
bellows' breath loop in figures' time, the title's glint passes on the hand's
period and the embers rise in a slow sweep; and drawn as the month's design,
it carries the month's sign at the top centre, the mail parting either side
of it.
"""
from __future__ import annotations

import math

from ...holidays.designs import NARROW, WIDE
from ...holidays.designs.badges import inside
from ...holidays.pixel import Pix, measure, tube
from ..hand import CollectionSet
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TOKENS, step

IRON, STEEL, COAL, EMBER, FLAME = RAMP["iron"], RAMP["steel"], RAMP["coal"], RAMP["ember"], RAMP["flame"]
BRASS, LEATHER, OAK = RAMP["brass"], RAMP["leather"], RAMP["oak"]
LINK_SPRITES = ("hammer", "anvil", "horseshoe", "blade")
# The colours the knights' crests and plumes are dyed, by turns.
CRESTS = (EMBER[4], RAMP["blue"][4], RAMP["green"][4], RAMP["purple"][4], BRASS[4])
SHEET_RULE = 20   # the row an element's sheet rules off its tag and title at
# The rows a phone's H2 and H3 ask for under their words for their heroes, which stand at least two clear of the
# words: the smithy, its chimney rising forty-six rows, and the armoury's trophy, fifty-five.
UNDER = {"H2": 44, "H3": 54}


class Forge(CollectionSet):
    """The Forge design: the smithy and the armoury, beaten out of iron, the medieval collection's November."""

    key = "medieval-forge"
    name = "Forge"
    collection = "medieval"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "Iron, fire and the hammer's beat.")
    about = (
        "Every sheet is a hammered iron plate, a cool slate by day with its dents beaten into the surface, framed in "
        "riveted bands with brass-studded corner plates and a strip of mail hung across the top. Titles are polished "
        "steel by day, with a hard white bevel and a dark edge, and by night iron fresh from the fire, white at the "
        "heart and cooling to ember red toward the ends of the line, a glint passing along them now and again. The "
        "headers stand in the smithy itself: the hearth with its chimney and bellows, its fire roaring up whenever "
        "the bellows are squeezed, and the smith at his anvil, his hammer coming down on the blade in a burst of "
        "sparks, a quench bucket steaming beside him and shields and an axe hung on the wall. The strip's hero is "
        "the armoury's trophy, a shield of red enamel bearing the smith's arms in brass, a hammer raised over an "
        "anvil, with a knight's helm over it and two swords crossed behind. On a phone every scene stands under "
        "the words: the whole smithy across the first header, the smith at his anvil before the hearth on the "
        "second and the trophy over the anvil on the third. By night the forge lights the plate from below, the "
        "fire flickers in the hearth and embers drift slowly up across the sheet. Every footer lies on a floor of "
        "the hearth's stone with coal heaped on it, the smith's anvil standing at its right end where there is "
        "room, and his touchmark is struck in its corner and beside its scale. Rivets stud every rule and every "
        "badge, the links are riveted steel tags, the counters are stamped steel plates, the commits are ingots "
        "glowing hotter the taller they stand, the dial has a hot needle, the releases hang from a chain as steel "
        "tags, the contributors wear knights' helms, and the certificate is struck with a steel seal.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The set's inks: the words in the hand's two inks, the titles in steel by day and in red-hot iron by night,
        every text colour at 4.5:1 on the plate."""
        return dict(
            title=FLAME[4] if night else IRON[2], shadow=EMBER[2] if night else IRON[1],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=C["rule_night"] if night else C["rule_day"], accent=EMBER[5] if night else C["accent_day"],
            tag=LEATHER[3], tag_ink=FLAME[6],
            fill=C["fill_night"] if night else C["fill_day"], dim=C["dim_night"] if night else C["dim_day"],
        )

    def lit(self, night):
        """Polished steel by day, with a hard bevel: white down the letters' left edges and dark iron along
        their feet. By night red-hot iron, painted hottest toward the middle of the line, with a glow."""
        if night:
            return dict(paint=A.HOT_PAINT, glow=(EMBER[5], (0.08, 0.16, 0.26)), night=True)
        return dict(paint=A.STEEL_PAINT, bevel=(C["white"], IRON[0]), night=False)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["plate"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """An iron plate has no stars in it."""

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The plate, and by night embers rising across a wide header at two depths, fewer on a short strip.
        A drawing made lighter to fit its budget keeps half as many embers, still rising at both depths. The
        file holds them still when the header does (see `art.embers`); a phone's header has none."""
        super().sky(p, night, y1, seed=seed, motion=motion, avoid=avoid)
        if night and p.w == WIDE:
            n = (36 if y1 < 80 else 44) // (2 if p.lite else 1)
            A.embers(p, 4, 4, p.w - 4, y1, n, seed=seed + 30, avoid=avoid)

    def frame(self, p, night, webs=False):
        """The riveted iron frame; a sheet with no mail hung over its top edge (a footer, an element) gets
        the heavier band there, with its rivets reading."""
        A.iron_frame(p, night)
        if not webs:
            A.top_band(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """A strip of mail hung from rivet hooks across the top. Where the header carries the hand's mark at the
        top centre, the month's or a sign the page chose, it hangs in two strips, each ending on its hook two units
        clear of the box the mark takes, so the mark cuts no ring of it."""
        if not self.marked:
            A.mail(p, x0, x1, y, night, sag=min(sag, 3), span=span)
            return
        m0 = p.w // 2 - self.mark_size // 2 - 2
        A.mail(p, x0, m0, y, night, sag=min(sag, 3), span=span)
        A.mail(p, m0 + self.mark_size + 4, x1, y, night, sag=min(sag, 3), span=span)

    def tag(self, p, x, y, w, h, night):
        """A leather strap a tag's letters are stamped on: lit along its top, dark along its foot, a stitch at
        each end, and buckled in brass at its start where the plate beside it is bare."""
        p.rect(x, y, w, h, LEATHER[3])
        p.hline(x, x + w, y, LEATHER[4])
        p.hline(x, x + w, y + h - 1, LEATHER[1])
        p.px(x, y + h // 2, LEATHER[5])
        p.px(x + w - 1, y + h // 2, LEATHER[5])
        if w >= 16 and h >= 9 and x >= 9 and all(p.get(x - 1 - i, y + h // 2) is None for i in range(4)):
            A.buckle(p, x - 4, y - 1, h + 2, night)       # a strap long enough for a name is buckled in brass

    def title_text(self, p, x, y, s, night, scale):
        """Letters of polished steel by day, each on a dark shadow inside an edge of the iron's darkest; by night
        letters of iron fresh from the fire inside the same dark edge, glowing. Either catches the light here and
        there, a glint passing along the line on the hand's period (see `art.title_glints`). The line is set in
        symbols (see `art.title`), so the longest title stays light."""
        k = self.ink(night)
        kw = self.lit(night)
        if night and scale < 4:
            kw["glow"] = (EMBER[5], (0.2,))           # one ring but on the biggest titles: a long one costs dearly
        w = A.title(p, x, y, s, scale, k["title"], IRON[0], shadow=None if night else k["shadow"], **kw)
        if scale >= 2:
            A.title_glints(p, x, y, s, scale, night)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.mini_anvil(p, x, y - 1, night)

    def strip_mark(self, p, x, y, night):
        A.mini_hammer(p, x, y - 6, night)

    def scene(self, design, p, rule, night, motion):
        """H1: the hearth, its chimney and its bellows on the left with tools on the wall above, the smith at his anvil
        on the right with the quench bucket beside him and the rack of shields and an axe on the wall behind, or, where
        a long title reaches toward it, the rack's short form at the right end, the red shield and the axe; H2: the
        whole smithy on the right, the hearth at the far end lighting the smith's back; H3: the armoury's trophy, the
        shield with the smith's arms, the helm over it and the swords crossed behind it, as tall as the strip, and the
        smith at his anvil before it where the words leave the floor clear, or where they leave less room a sword over a
        shield. By night the fire and the hot blade light what stands near them (see `finish`)."""
        clear = p.clear_of_words
        if design == "H1":
            A.hearth(p, 6, rule, night, motion, top=14)
            A.bellows(p, 40, rule - 12, night, motion)
            if clear(39, rule - 50, 61, rule - 26):
                A.tools(p, 41, rule - 48, night)
            A.anvil_scene(p, 354, rule, night, motion, clear)
            A.bucket(p, 400, rule, night, motion, w=10, h=10)
            if clear(352, rule - 70, 411, rule - 42):
                A.rack(p, 354, 411, rule - 68, night, clear)
            elif clear(411 - A.RACK_SHORT_W - 12, rule - 70, 411, rule - 42):    # where a long title reaches
                A.rack(p, 411 - A.RACK_SHORT_W, 411, rule - 68, night, clear, short=True)
            return [(5, 64), (352, 410)]
        if design == "H2":
            A.hearth(p, 376, rule, night, motion, top=14)
            A.bellows(p, 352, rule - 12, night, motion, flip=True)
            if clear(351, rule - 50, 373, rule - 26):
                A.tools(p, 353, rule - 48, night)
            A.anvil_scene(p, 297, rule, night, motion, clear)
            if clear(283, rule - 14, 297, rule):
                A.bucket(p, 285, rule, night, motion, w=10, h=10)
            if clear(296, rule - 70, 352, rule - 42):
                A.rack(p, 298, 352, rule - 68, night, clear)
            return [(284, 410)]
        top = A.TROPHY_TOP + max(0, (rule - 3 - A.TROPHY_TOP - A.TROPHY_H) // 2)
        if clear(A.TROPHY_X - 26, top - 2, A.TROPHY_X + 26, top + A.TROPHY_H + 2):
            A.trophy(p, A.TROPHY_X, top, night)
            if clear(282, rule - 32, 358, rule):           # where the words leave the floor, the smith before it
                A.bucket(p, 286, rule, night, motion, w=10, h=10)
                A.anvil_scene(p, 300, rule, night, motion, clear)
                return [(284, 410)]
            return []
        if clear(370, rule - 37, 399, rule - 9):
            A.sword_over_shield(p, 384, rule - 23, night)
        return []

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene: the whole smithy across the phone, standing on the rule at `y` in the rows asked for
        under its words (see `h1_narrow`). A phone's H2 and H3 stand their scenes under their words instead (see
        `scene_under`)."""
        if design == "H1":
            self._phone_forge(p, y, night)

    # ---- a phone's scenes, in rows asked for under its words
    SMITHY = 50       # the rows a phone's H1 smithy stands in, its chimney the tallest of it
    _under = False    # set while a phone's H2 or H3 is drawn with rows under its words for its scene
    _h1_rows = 0      # the rows a phone's H1 is drawn with, while it is

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 asks for between its words and its rule (see `h1_narrow`)."""
        return self._h1_rows

    def h1_narrow(self, h, night):
        """A phone's H1, its whole smithy standing across it under the words, in the rows its chimney rises
        through, the notes set under the words, however many there are: the hand's composition asks a phone's H1
        for a full-width scene under its words, not corner pieces beside them."""
        self._h1_rows = self.SMITHY + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._h1_rows = 0

    def h2_narrow(self, h, night):
        return self._phone(super().h2_narrow, h, night)

    def h3_narrow(self, h, night):
        return self._phone(super().h3_narrow, h, night)

    def _phone(self, draw, h, night):
        """A phone's H2 or H3, drawn with rows under its words for its hero, forty rows tall or more, which beside
        the words would have no room (see `phone_rows`)."""
        self._under = True
        try:
            return draw(h, night)
        finally:
            self._under = False

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 asks for under its words: those its hero takes, two clear of the last words
        at least."""
        return UNDER[design] if self._under else 0

    def scene_under(self, design, p, y0, y1, night):
        """The scene in the rows a phone's H2 or H3 asked for under its words, standing on the rule at `y1`: the
        smithy on an H2, the armoury on an H3."""
        (self._phone_smithy if design == "H2" else self._phone_armoury)(p, y1, night)

    @staticmethod
    def _room(p):
        """Whether a box on a phone lies inside the frame and at least two units clear of every word."""
        def room(x0, y0, x1, y1):
            return x0 >= 5 and x1 <= NARROW - 4 and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2)
        return room

    def _phone_forge(self, p, base, night):
        """The H1's smithy across a phone, standing on the rule at `base`, as the wide H1 has it: the hearth at the
        left, its chimney rising SMITHY rows, the bellows breathing into it and the tools on the wall over them; the
        smith at his anvil, sparks flying off the blade; the quench bucket, and the rack of shields and an axe on
        the wall at the right."""
        room = self._room(p)
        A.hearth(p, 6, base, night, False, top=base - self.SMITHY, w=32, strong=True)
        A.bellows(p, 39, base - 12, night, False)
        if room(41, base - 40, 61, base - 20):
            A.tools(p, 42, base - 40, night)
        A.anvil_scene(p, 66, base, night, False, room, strong=True)
        A.bucket(p, 112, base, night, False, w=10, h=10)
        if room(119, base - 40, 176, base - 14):
            A.rack(p, 120, 176, base - 40, night, room)

    def _phone_smithy(self, p, base, night):
        """The H2's smithy under a phone's words, standing on the rule at `base`, as the wide H2 has it: shields
        hung on the wall, the quench bucket, the smith at his anvil with sparks flying off the blade, the tools on
        the wall over the bellows, and at the far end the hearth, its chimney rising, its fire lighting his back by
        night."""
        room = self._room(p)
        if room(6, base - 34, 51, base - 7):
            A.rack(p, 6, 50, base - 34, night, lambda x0, y0, x1, y1: x1 <= 51 and room(x0, y0, x1, y1))
        if room(51, base - 16, 63, base):
            A.bucket(p, 52, base, night, False, w=10, h=10)
        if room(63, base - 36, 110, base):
            A.anvil_scene(p, 64, base, night, False, room, strong=True)
        if room(121, base - 34, 140, base - 15):
            A.tools(p, 122, base - 34, night)
        if room(119, base - 12, 143, base):
            A.bellows(p, 119, base - 12, night, False, flip=True)
        if room(142, base - UNDER["H2"] - 2, 176, base):
            A.hearth(p, 143, base, night, False, top=base - UNDER["H2"] - 2, w=32, strong=True)

    def _phone_armoury(self, p, base, night):
        """The H3's scene under a phone's words, standing on the rule at `base`: the armoury's trophy on the wall,
        the shield with the smith's arms, the helm over it and the swords crossed behind it; and on the floor before
        the wall the anvil with a blade on it and the hammer laid by, sparks flying, and the quench bucket; by night
        the hot blade lights what stands near it."""
        room = self._room(p)
        top = base - A.TROPHY_H - 1
        if room(A.PHONE_TROPHY_X - 25, top, A.PHONE_TROPHY_X + 25, base - 1):
            A.trophy(p, A.PHONE_TROPHY_X, top, night)
        if room(28, base - 24, 54, base):
            a = A.anvil(p, 29, base, night, small=True)
            A.blade(p, 32, a["face"] - 2, night, length=16, strong=True)
            A.mini_hammer(p, 46, a["face"] - 8, night)
            A.sparks(p, 43, a["face"] - 2, night, False, room)
        if room(60, base - 14, 70, base):
            A.bucket(p, 61, base, night, False, w=8, h=8)
        if room(26, base - 44, 46, base - 26):
            A.tools(p, 27, base - 44, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Rivets along the rule, the seam of the plate the figures stand on; sparser on a sheet's own rule."""
        A.rivet_run(p, x0, x1, y, night, spacing=14 if y <= SHEET_RULE else 11, seed=seed)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: what it lays is the forge's own light."""
        self.finish(p, night)

    def finish(self, p, night):
        """The last pass: the heat of the hot things on what stands near, and by night a glowing needle on
        the dial."""
        A.heat(p, night)
        if night and getattr(p, "dial", None):
            self._hot_needle(p)

    def _hot_needle(self, p):
        """The dial's hand as a needle of iron drawn from the fire by night: red at the hub, yellow along its
        length and white at its point, with its light on the plate round it."""
        cx, cy, r = p.dial
        reach = r - 11
        hand = [(x, y) for (x, y), c in p.layers["base"].items() if c == EMBER[5]
                and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2]
        if not hand:
            return
        for (x, y) in hand:
            t = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / max(1, reach)
            p.px(x, y, FLAME[6] if t > 0.8 else FLAME[5] if t > 0.55 else FLAME[4] if t > 0.3 else EMBER[5])
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                if (x + dx, y + dy) not in p.layers["base"]:
                    p.apx(x + dx, y + dy, EMBER[5], 0.28, "haze")
        tip = max(hand, key=lambda q: (q[0] + 0.5 - cx) ** 2 + (q[1] + 0.5 - cy) ** 2)
        p.halo(tip[0] + 0.5, tip[1] + 0.5, 5.5, 5.5, EMBER[5], (0.1, 0.2), L="haze", shape=False)

    # ---- the footers' own last pass, which their layouts give no hook for
    def _footed(self, p, night):
        """A footer as the smith's: its floor along its foot, the hearth's stone with the smith's anvil standing on
        it where the cells leave it room and coal heaped on it wherever else they do (see `art.footer_floor`), domed
        rivets where its rules join its cells and its band, and by night the forge's glow along its foot."""
        rule = self.ink(night)["rule"]
        A.footer_floor(p, night, rule)
        A.rivet_joins(p, night, rule)
        if night:
            A.foot_glow(p)
        return p

    def _struck(self, p, x0, x1, night):
        """The smith's touchmark struck where the words leave it room between columns x0 and x1 of a scale bar's
        cell, as far right and as low over the floor as it goes, two units clear of every word."""
        n = len(A.MARK)
        for x in range(x1 - n - 2, x0 + 1, -1):
            for y in range(A.floor_top(p) - n - 1, 6, -1):
                if p.clear_of_words(x - 2, y - 2, x + n + 2, y + n + 2) and not any(
                        (x + i, y + j) in p.layers["base"] for i in range(n) for j in range(n)):
                    A.maker_mark(p, x, y, night)
                    return

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night)

    def f2(self, ft, night):
        """F2, the smith's touchmark struck beside its scale bar."""
        p = super().f2(ft, night)
        self._struck(p, 72, 95, night)
        return self._footed(p, night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night)

    def f2_narrow(self, ft, night):
        """A phone's F2, the smith's touchmark struck beside its scale bar."""
        p = super().f2_narrow(ft, night)
        self._struck(p, 66, NARROW - 70, night)
        return self._footed(p, night)

    def link_button(self, label, index, night):
        """The kit's link as a stamped steel tag: by day its letters are cut into the steel, with a lip of
        light below and to the right of each where the cut's far wall catches the light."""
        p = super().link_button(label, index, night)
        if not night:
            ink = self.link_colours(night)[2]
            letters = [u for u in p.uses["base"] if u[0] == ink]        # the glyphs, set as uses of their symbols
            p.uses["base"] = [(C["white"], sid, x + 1, y + 1, s) for (_, sid, x, y, s) in letters] + p.uses["base"]
        return p

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The smith's touchmark struck into the plate in the closing cell's corner."""
        A.maker_mark(p, x + (3 if p.w == NARROW else 2), y - (3 if p.w == NARROW else 4), night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar of alternating steel and blackened iron, `period` pixels a block, lit along the top and
        shaded along the foot."""
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                bright = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (STEEL[6], STEEL[4], STEEL[2])[band] if bright else (COAL[5], COAL[3], COAL[1])[band])

    def link_colours(self, night):
        """A tag of steel with its letters cut dark into it by day, with a dark edge; by night a tag of dark
        iron with bright letters."""
        if night:
            return IRON[2], COAL[0], STEEL[6], COAL[1]
        return STEEL[4], IRON[0], IRON[0], STEEL[2]

    def link_top(self, p, x0, x1, y, seed, night):
        """The tag's bevel, lit along its top and left and shaded down its right, a rivet at each end, and by
        night its foot and lower edges lit faintly by the embers."""
        lit, dark = (IRON[4], COAL[0]) if night else (STEEL[6], STEEL[2])
        w = p.w
        p.hline(1, w - 1, y + 1, lit)
        p.vline(1, y + 1, 11, lit)
        p.vline(w - 2, y + 2, 11, dark)
        A.rivet(p, 2, 6, night=night)
        A.rivet(p, w - 5, 6, night=night)
        if night:
            p.hline(1, w - 1, 11, EMBER[1])
            p.hline(1, w - 1, 12, EMBER[2])
            for xx in (0, w - 1):
                p.vline(xx, 9, 12, EMBER[2])

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (IRON[4], COAL[0]) if night else (C["white"], STEEL[3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a riveted steel plate: its icon stamped into a darker plate let into its cell, a strap
        down the cell's edge held by two rivets, and a rivet in each corner, the top pair of brass on a card
        with a lid."""
        k = -1 if night else 0
        ink = self.ink(night)
        recess = COAL[2] if night else STEEL[5]
        for yy in range(y + 2, y + h - 2):
            for xx in range(x + 2, x + 10):
                if p.get(xx, yy) == ink["fill"]:
                    p.px(xx, yy, recess)
        if not night:
            icon = [(xx, yy) for xx in range(x + 2, x + 10) for yy in range(y + 2, y + h - 2)
                    if p.get(xx, yy) == ink["body"]]
            A.stamp_lips(p, icon, C["white"], recess)
        for yy in range(y + 1, y + h - 1):
            p.px(x + 10, yy, STEEL[5 + k])
            p.px(x + 11, yy, STEEL[3 + k])
            p.px(x + 12, yy, STEEL[1 + k])
        A.rivet(p, x + 10, y + 3, night=night)
        A.rivet(p, x + 10, y + h - 5, night=night)
        for (rx, ry) in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
            if lid and ry == y + 1:
                p.px(rx, ry, BRASS[5 + k])
                p.px(rx + 1, ry, BRASS[3 + k])
                p.px(rx, ry + 1, BRASS[3 + k])
                p.px(rx + 1, ry + 1, BRASS[1 + k])
            else:
                A.rivet(p, rx, ry, night=night)

    def wire_ink(self, night):
        return STEEL[3] if night else IRON[2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as an iron rod: lit along its upper side where it runs level, and pinned to the plate
        with a rivet where it starts and wherever it turns."""
        lit = STEEL[4] if night else IRON[4]
        for (x, y, d) in cells[1:-4]:
            if d == "h" and p.get(x, y - 1) is None:
                p.px(x, y - 1, lit)
        pins = [cells[0]] + [c for i, c in enumerate(cells) if 0 < i < len(cells) - 4 and cells[i - 1][2] != c[2]]
        for (x, y, d) in pins:
            A.rivet(p, x - 1, y - 1, night=night)

    def dashes(self, night):
        return [BRASS[5] if night else BRASS[4], IRON[4] if night else IRON[3]]

    def ornament(self, kind, p, x, y, night):
        """A small anvil with a hammer laid across it, in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.anvil(p, x, y + 14, night, small=True)
                A.hammer_head(p, x + 13, y, night)
                for j in range(1, 7):
                    p.px(x + 12 - j, y + 2 + j // 2, OAK[2] if night else OAK[4])
            return (26, 14)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as an iron ingot stood on end, hotter the taller it is."""
        A.ingot(p, bx, base, bw, v, min(1.0, v / 45), night)

    def peak_mark(self, p, x, y, night):
        A.spark_glint(p, x + 2, y + 3, night)

    def dial_ring(self, p, arc, night):
        """A gauge's ring of polished steel, riveted at the ticks."""
        k = -1 if night else 0

        def colour(s, o, lam, x, y):
            return STEEL[max(1, min(6, round(1.6 + 4.2 * lam) + k))]
        tube(p, arc, 2.0, colour, outline=IRON[0])
        (x0, y0), (x1, _) = arc[0], arc[-1]
        p.dial = ((x0 + x1) / 2, y0, (x1 - x0) / 2 + 1.5)      # for the needle's glow, see `finish`

    def dial_tick(self, p, x, y, night):
        A.rivet(p, x - 1, y - 1, night=night)

    def dial_hub(self, p, cx, cy, night):
        A.bolt(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The smith's materials by turns: brushed steel, blackened iron set with rivets, brass with a sheen,
        and stitched leather."""
        k = -1 if night else 0
        kind = i % 4
        if kind == 0:
            c = STEEL[5 + k] if yy % 2 else STEEL[4 + k]
        elif kind == 1:
            c = STEEL[4 + k] if (xx % 4 == 1 and yy % 4 == 1) else COAL[3 + k]
        elif kind == 2:
            c = BRASS[5 + k] if (xx + yy) % 7 == 0 else BRASS[4 + k]
        else:
            c = LEATHER[6 + k] if (yy in (y0 + 2, y1 - 3) and xx % 3 == 0) else LEATHER[4 + k]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """A stamped steel plate, 11 by 15, bevelled and held by four rivets."""
        k = -1 if night else 0
        q.rect(ox, oy, 11, 15, STEEL[4 + k] if not night else IRON[3])
        q.bevel(ox, oy, 11, 15, STEEL[6 + k] if not night else IRON[5], IRON[2] if not night else COAL[0])
        q.box(ox - 1, oy - 1, 13, 17, IRON[0] if night else IRON[1])
        for (dx, dy) in ((1, 1), (8, 1), (1, 12), (8, 12)):
            A.rivet(q, ox + dx, oy + dy, night=night)

    def counter_ink(self, night, dim):
        """A plate's stamped digit, in a tone a hair off the text's own ink (a mid steel for a leading nought):
        a drawing sets all the letters of one ink together, where that ink is first used, so an ink of their
        own keeps the digits over the plates they are stamped into."""
        if night:
            return STEEL[5] if dim else STEEL[6]
        return COAL[4] if dim else COAL[1]

    def timeline_line(self, p, x0, x1, y, night):
        """The chain the releases hang from, up to today."""
        A.chain(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A stamped steel tag hung from the chain for a release, a wider one for a big release, a ring for a
        patch, an empty tag for one still to come, and for the repository's creation an anvil. The latest
        release's tag is struck in brass once today's mark is set (see `today_mark`)."""
        k = -1 if night else 0
        if kind == "big":
            A.hanging_tag(p, x, gy + 1, night, big=True)
        elif kind == "major":
            A.hanging_tag(p, x, gy + 1, night)
        elif kind == "minor":
            p.sprite(x - 1, gy + 2, [".#.", "#.#", ".#."], {"#": STEEL[4 + k]})
            p.px(x, gy + 2, STEEL[6 + k])
        elif kind == "made":
            A.mini_anvil(p, x - 4, gy + 4, night)
        else:
            A.hanging_tag(p, x, gy + 1, night, outline_only=True)

    def today_mark(self, p, x, y, night):
        """A spark at the chain's end, and the latest tag before it struck in brass: the one hung nearest to
        the left of today on the same chain."""
        A.spark_glint(p, x + 2, y, night, big=True)
        hung = [t for t in getattr(p, "tags", []) if abs(t[1] - (y + 1)) <= 1 and t[0] < x]
        if hung:
            tx, ty, big = max(hung)
            A.hanging_tag(p, tx, ty, night, big=big, brass=True)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a knight's helm with their initials stamped on the faceplate, a different helm by
        turns with a crest or plume dyed a colour of their own; a bot is a helm with its visor down and a
        brass gear on its crown."""
        if not person.get("initials"):
            A.helm(p, cx, cy, night, kind=3)
            return
        kind = i % 3
        colour = CRESTS[i % len(CRESTS)]
        A.helm(p, cx, cy, night, kind=kind, crest=colour)
        if kind == 1:
            A.plume(p, cx + 3, cy - 10, night, colour=colour)
        ini = str(person["initials"])[:2]
        p.text(cx - measure(ini, "35") // 2, cy + 1, ini, COAL[0], "35")

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a bar of iron heated from its far end: cold steel, then red, then yellow."""
        p.box(x, y, w + 2, 4, IRON[0] if night else IRON[1])
        for xx in range(fill):
            u = (xx + 0.5) / max(1, fill)
            top = STEEL[4] if u < 0.4 else EMBER[3] if u < 0.62 else EMBER[5] if u < 0.85 else FLAME[5]
            p.px(x + 1 + xx, y + 1, top)
            p.px(x + 1 + xx, y + 2, step(top, -1))

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A ring of polished steel round the seal, from r0 to r1, set with rivets."""
        k = -1 if night else 0
        rad = (r0 + r1) / 2 - 0.5
        ring = [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))) for a in range(0, 361, 4)]

        def colour(s, o, lam, x, y):
            return STEEL[max(1, min(6, round(1.6 + 4.2 * lam) + k))]
        tube(p, ring, (r1 - r0) / 2 - 0.3, colour, outline=IRON[0])
        for a in range(0, 360, 30):
            ang = math.radians(a)
            A.rivet(p, cx + round(rad * math.cos(ang)) - 1, cy + round(rad * math.sin(ang)) - 1, night=night)

    def seal_mark(self, p, x, y, night):
        A.mini_hammer(p, x + 3, y, night)

    def placard_board(self, p, night):
        """A riveted iron sign: the hammered plate inside bands of riveted iron."""
        A.paper(p, night, uid="pl")
        A.iron_frame(p, night, uid="plf")
        A.top_band(p, night)

    def placard_mark(self, p, x, y, night):
        A.maker_mark(p, x - 1, y - 7, night)

    def placard(self, d, night):
        """The kit's placard, its touchmark struck beside the owner's strap when the layout found no room for
        one beside the title."""
        p = super().placard(d, night)
        if not p.clear_of_words(156, 6, 172, 25) and p.clear_of_words(150, 6, 172, 21):
            self.placard_mark(p, 158, 15, night)
        return p

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch on a badge, kept inside its shape: a riveted steel band along its top two rows, and
        under it each block as the badge laid it, read off its middle row: a block of blackened iron gets a
        brushed highlight and a shadow along its foot, any other block a bevel (lit along its top where no
        letter sits, shaded along its foot and its far end), and a rivet goes in each lower corner."""
        h = s["h"]
        k = -1 if night else 0
        mid = h // 2
        row = [p.get(x, mid) for x in range(w)]
        first = next((x for x in range(w) if row[x]), 0)
        left = next((x for x in range(first, w) if row[x] != row[first]), w)
        tmp = Pix(w, h)
        tmp.hline(0, w, 0, STEEL[4 + k])
        tmp.hline(0, w, 1, STEEL[2 + k])
        x = 1 + seed % 3
        while x + 1 < w:
            A.rivet(tmp, x, 0, night=night)
            x += 7
        ty = self._text_y(s)
        lo = next((x for x in range(w) if inside(x, h - 2, w, h, s["corner"])), 0)
        hi = next((x for x in range(w - 1, -1, -1) if inside(x, h - 2, w, h, s["corner"])), w - 1)
        for (a, b) in ((first, left), (left, w)):
            if b <= a:
                continue
            c = row[a]
            if c == COAL[2]:
                for xx in range(a, b):
                    if p.get(xx, h - 1) == c:
                        tmp.px(xx, h - 1, COAL[0])
                    if p.get(xx, h - 2) == c and (xx + seed) % 6 < 4:
                        tmp.px(xx, h - 2, COAL[4 + k])
            else:
                try:
                    lit, dark = step(c, 1), step(c, -1)
                except KeyError:
                    lit = dark = None
                for xx in range(a, b):
                    if lit and ty > 2 and p.get(xx, 2) == c:
                        tmp.px(xx, 2, lit)
                    if dark and p.get(xx, h - 1) == c:
                        tmp.px(xx, h - 1, dark)
                if dark:
                    for yy in range(2, h - 1):
                        if p.get(b - 1, yy) == c:
                            tmp.px(b - 1, yy, dark)
            A.rivet(tmp, max(a, lo), h - 2, night=night)
            A.rivet(tmp, min(b - 2, hi - 1), h - 2, night=night)
        for (x, y), c in tmp.layers["base"].items():
            if inside(x, y, w, h, s["corner"]):
                p.px(x, y, c)

    def badge_label(self):
        return (COAL[2], STEEL[6])

    def badge_gold(self):
        return (BRASS[4], COAL[1])

    def badge_states(self):
        # Yellow is drawn in amber, so it stands apart from the brass label, with dark letters.
        return {"green": (RAMP["green"][2], C["white"]), "yellow": (EMBER[5], COAL[1]),
                "red": (EMBER[3], C["white"]), "slate": (IRON[4], C["white"])}

    def badge_swatches(self):
        return {"ember": (EMBER[3], C["white"], None), "amber": (EMBER[5], COAL[1], None),
                "brass": (BRASS[4], COAL[1], None), "enamel": (RAMP["green"][2], C["white"], None),
                "lapis": (C["lapis"], C["white"], None), "plum": (RAMP["purple"][2], C["white"], None),
                "steel": (STEEL[6], COAL[2], "outline"), "iron": (COAL[2], STEEL[6], "studs"),
                "slate": (IRON[4], C["white"], None), "leather": (LEATHER[3], C["white"], None),
                "oak": (OAK[3], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "studs" and (x * 7 + y * 13) % 29 == 0 and y not in text_rows:
            return BRASS[4]
        return c

    def badge_outline(self, pattern):
        return STEEL[3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate's colours. Its paper is plain iron, with no dots: the dot is the paper's own colour."""
        if mode == "day":
            return dict(paper=C["plate"], dot=C["plate"], frame=STEEL[5], block=COAL[2], ink=C["ink"],
                        letters=STEEL[6])
        if mode == "night":
            return dict(paper=COAL[1], dot=COAL[1], frame=BRASS[4], block=BRASS[4], ink=STEEL[6], letters=COAL[0])
        return dict(paper=BRASS[4], dot=BRASS[4], frame=COAL[1], edge=BRASS[2], ink=COAL[1])

    def plate_edge(self, block):
        return step(block, -1)


SET = Forge()
